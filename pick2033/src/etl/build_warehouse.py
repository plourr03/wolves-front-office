"""Build data/warehouse.duckdb from staged parquet (spec Section 6 schemas).

Tables:
  franchise_seasons       one row per franchise-season 1980-2026 with derived
                          core_age_min_weighted, continuity_pct, had_star
  player_impact_seasons   B-Ref advanced rows (combined + stints), 1979-2026
  draft_outcomes          1990-2019 picks with value_4yr (VORP) / value_alt (WS)
                          summed over the CALENDAR window draft_year+1..+4
                          (stash/never-played years count 0: prices delay cost)
  all_nba                 All-League selections (star-definition trigger)
  lottery_odds            legacy era tables, audit copy of lottery.py constants

had_star NOTE: at M0 this is the same-season approximation (All-NBA that season
OR top-20 BPM with 1500+ mp). The spell-based version (spec 6.2: any active
star-spell player) replaces it when the M2 spell freeze lands.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.sim.lottery import POST_2019_WEIGHTS, PRE_2019_WEIGHTS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGED = PROJECT_ROOT / "data" / "staged"
DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"

BPM_TOP_K, BPM_MIN_FLOOR = 20, 1500


def team_attributed_rows(ps: pd.DataFrame) -> pd.DataFrame:
    """Rows that attribute minutes to a franchise: single-team rows + stint
    rows. (Combined rows carry no franchise.)"""
    return ps[~ps.is_combined & ps.franchise_id.notna()].copy()


def star_flags(ps: pd.DataFrame, all_nba: pd.DataFrame) -> pd.DataFrame:
    """Same-season star flag per (player_id, season): All-NBA that season or
    top-20 league BPM with 1500+ minutes (combined-row basis)."""
    season_rows = ps[ps.is_combined | ps.stint_order.isna()]
    season_rows = (season_rows.sort_values("is_combined", ascending=False)
                   .drop_duplicates(["player_id", "season"]))
    elig = season_rows[(season_rows.mp >= BPM_MIN_FLOOR) & season_rows.bpm.notna()].copy()
    elig["bpm_rank"] = elig.groupby("season").bpm.rank(ascending=False, method="min")
    bpm_stars = elig[elig.bpm_rank <= BPM_TOP_K][["player_id", "season"]]
    an_stars = all_nba[["player_id", "season"]]
    stars = pd.concat([bpm_stars, an_stars]).drop_duplicates()
    stars["is_star_season"] = True
    return stars


def build_franchise_seasons(fs_raw, ps, all_nba) -> pd.DataFrame:
    attributed = team_attributed_rows(ps)
    attributed = attributed[attributed.mp.notna() & (attributed.mp > 0)]

    # core age: minutes-weighted age of top-6 minutes players per franchise-season
    def core_age(g):
        top6 = g.nlargest(6, "mp")
        return float(np.average(top6.age, weights=top6.mp))

    core = (attributed.dropna(subset=["age"])
            .groupby(["franchise_id", "season"])
            .apply(core_age, include_groups=False)
            .rename("core_age_min_weighted").reset_index())

    # continuity: share of minutes from players on the same franchise in t-1
    prior = attributed[["franchise_id", "season", "player_id"]].copy()
    prior["season"] += 1
    prior["returning"] = True
    cont_base = attributed.merge(
        prior.drop_duplicates(), on=["franchise_id", "season", "player_id"], how="left")
    cont = (cont_base.assign(ret_mp=lambda d: d.mp.where(d.returning.notna(), 0.0))
            .groupby(["franchise_id", "season"])
            .agg(total_mp=("mp", "sum"), ret_mp=("ret_mp", "sum")).reset_index())
    cont["continuity_pct"] = cont.ret_mp / cont.total_mp

    # had_star (same-season approximation, see module docstring)
    stars = star_flags(ps, all_nba)
    star_team = attributed.merge(stars, on=["player_id", "season"], how="inner")
    had_star = (star_team.groupby(["franchise_id", "season"]).size() > 0)
    had_star = had_star.rename("had_star").reset_index()

    out = (fs_raw.merge(core, on=["franchise_id", "season"], how="left")
           .merge(cont[["franchise_id", "season", "continuity_pct"]],
                  on=["franchise_id", "season"], how="left")
           .merge(had_star, on=["franchise_id", "season"], how="left"))
    out["had_star"] = out.had_star.eq(True)
    out["win_pct"] = out.win_loss_pct
    return out[["franchise_id", "season", "bref_abbr", "team_name", "conference",
                "wins", "losses", "win_pct", "srs", "core_age_min_weighted",
                "continuity_pct", "had_star"]]


def build_draft_outcomes(draft, ps) -> pd.DataFrame:
    season_vals = (ps[ps.is_combined | ps.stint_order.isna()]
                   .sort_values("is_combined", ascending=False)
                   .drop_duplicates(["player_id", "season"])
                   [["player_id", "season", "vorp", "ws"]])
    d = draft.copy()
    windows = []
    for offset in (1, 2, 3, 4):
        w = d[["draft_year", "slot", "player_id"]].copy()
        w["season"] = w.draft_year + offset
        windows.append(w)
    wdf = (pd.concat(windows)
           .merge(season_vals, on=["player_id", "season"], how="left"))
    agg = (wdf.groupby(["draft_year", "slot"])
           .agg(value_4yr=("vorp", "sum"), value_alt=("ws", "sum"),
                seasons_observed=("vorp", "count")).reset_index())
    out = d.merge(agg, on=["draft_year", "slot"], how="left")
    out[["value_4yr", "value_alt"]] = out[["value_4yr", "value_alt"]].fillna(0.0)
    out["seasons_observed"] = out.seasons_observed.fillna(0).astype(int)
    return out


def main():
    fs_raw = pd.read_parquet(STAGED / "franchise_seasons_raw.parquet")
    ps = pd.read_parquet(STAGED / "player_impact_seasons.parquet")
    draft = pd.read_parquet(STAGED / "draft_picks.parquet")
    all_nba = pd.read_parquet(STAGED / "all_nba.parquet")

    franchise_seasons = build_franchise_seasons(fs_raw, ps, all_nba)
    draft_outcomes = build_draft_outcomes(draft, ps)

    lot_rows = (
        [{"era": "pre_2019_weighted", "position": i + 1, "weight": int(w), "drawn_picks": 3}
         for i, w in enumerate(PRE_2019_WEIGHTS)]
        + [{"era": "post_2019", "position": i + 1, "weight": int(w), "drawn_picks": 4}
           for i, w in enumerate(POST_2019_WEIGHTS)]
    )
    lottery_odds = pd.DataFrame(lot_rows)

    if DB_PATH.exists():
        DB_PATH.unlink()
    con = duckdb.connect(str(DB_PATH))
    for name, df in [("franchise_seasons", franchise_seasons),
                     ("player_impact_seasons", ps),
                     ("draft_outcomes", draft_outcomes),
                     ("all_nba", all_nba),
                     ("lottery_odds", lottery_odds)]:
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM df")
        n = con.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
        print(f"{name}: {n} rows")
    con.close()
    print(f"warehouse -> {DB_PATH}")


if __name__ == "__main__":
    main()
