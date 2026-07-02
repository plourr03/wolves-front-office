"""star_spells_builder: generate candidate star spells (spec 6.2) and the
review CSV for Bobby's human-in-the-loop pass.

Definition (config/star_definition.yaml, accepted 2026-07-01): a player ENTERS
a spell in his first season with a franchise earning All-NBA OR a top-20
league BPM finish with 1500+ minutes. The spell persists until departure,
retirement, or censoring, even if star-level play lapses.

Event coding per spell-season row:
  event_departure  the player's season t+1 FINAL-STINT franchise differs from
                   the spell franchise. This covers offseason moves (t+1 spent
                   elsewhere) and mid-season-t+1 trades away (final stint of
                   t+1 elsewhere). Any cause counts (spec non-goal).
                   NOTE (bugfix 2026-07-01): a multi-team season where the
                   FINAL stint is the spell franchise is an ARRIVAL, not a
                   departure -- the spell simply begins/continues. Direction
                   comes only from cross-season final-stint comparison; a
                   same-season stint count carries no direction and must not
                   close spells. Spells persist without re-qualification and
                   data-boundary exits are censored by definition.
  event_retire     no NBA season after t (career ends with franchise).
                   Near the data edge this is indistinguishable from a gap
                   year -> flagged for review instead of auto-coded.
  censored         spell alive at data end (2026).

Covariates: age, years_with_franchise (consecutive tenure incl. pre-star
years), team_win_pct_2yr (trailing t-1/t average), deep_run_recent (franchise
CF+ in t..t-2), all_nba_count_career, market_tier (config), supermax_eligible
(HEURISTIC: 2018+ era, 7+ years of service, All-NBA in t..t-2; review),
contract_years_remaining (NOT populated at M0 -- historical contract data is
the known-messiest field; column ships empty with contract_known=False and
the model learns a missingness effect; best-effort backfill lands in M2).

Outputs:
  data/staged/star_spell_seasons_candidate.parquet   per-season rows (model B input, pre-review)
  outputs/star_spells_review.csv                     spell-level review sheet for Bobby
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.etl.bref_client import fetch, strip_comment_tables
from src.etl.bref_parsers import parse_playoff_deep_runs
from src.etl.franchise_map import to_franchise

DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"
STAGED = PROJECT_ROOT / "data" / "staged"
OUTPUTS = PROJECT_ROOT / "outputs"

CFG = yaml.safe_load((PROJECT_ROOT / "config" / "star_definition.yaml").read_text())
START_YEAR = int(CFG["spell"]["start_year"])
BPM_TOP_K = int(CFG["entry"]["bpm_top_k"])
BPM_FLOOR = int(CFG["entry"]["bpm_minutes_floor"])
DATA_END = 2026


def load_tables():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    ps = con.execute("SELECT * FROM player_impact_seasons").fetchdf()
    fs = con.execute("SELECT franchise_id, season, win_pct FROM franchise_seasons").fetchdf()
    all_nba = con.execute("SELECT * FROM all_nba").fetchdf()
    con.close()
    return ps, fs, all_nba


def deep_runs() -> pd.DataFrame:
    rows = []
    for season in range(START_YEAR - 3, DATA_END + 1):
        html = strip_comment_tables(
            fetch(f"/leagues/NBA_{season}.html", f"leagues_NBA_{season}"))
        rows.extend(parse_playoff_deep_runs(html, season))
    df = pd.DataFrame(rows).drop_duplicates(["season", "bref_abbr"])
    df["franchise_id"] = [to_franchise(a, s) for a, s in zip(df.bref_abbr, df.season)]
    return df[["season", "franchise_id"]].drop_duplicates()


def final_team_by_season(ps: pd.DataFrame) -> pd.DataFrame:
    """One row per (player, season): the FINAL franchise (last stint) plus
    season-level combined stats, career metadata."""
    attributed = ps[~ps.is_combined & ps.franchise_id.notna()].copy()
    attributed["stint_order"] = attributed.stint_order.fillna(0)
    finals = (attributed.sort_values("stint_order")
              .groupby(["player_id", "season"]).last().reset_index()
              [["player_id", "season", "franchise_id"]]
              .rename(columns={"franchise_id": "final_franchise"}))
    multi = (attributed.groupby(["player_id", "season"]).franchise_id.nunique()
             .rename("n_franchises").reset_index())
    combined = (ps.sort_values("is_combined", ascending=False)
                .drop_duplicates(["player_id", "season"])
                [["player_id", "season", "player_name", "age", "mp", "bpm", "vorp"]])
    out = combined.merge(finals, on=["player_id", "season"], how="inner") \
                  .merge(multi, on=["player_id", "season"], how="left")
    return out


def star_entry_flags(seasons: pd.DataFrame, all_nba: pd.DataFrame) -> pd.DataFrame:
    elig = seasons[(seasons.mp >= BPM_FLOOR) & seasons.bpm.notna()].copy()
    elig["bpm_rank"] = elig.groupby("season").bpm.rank(ascending=False, method="min")
    bpm_star = set(map(tuple, elig[elig.bpm_rank <= BPM_TOP_K][["player_id", "season"]].values))
    an_star = set(map(tuple, all_nba[["player_id", "season"]].values))
    seasons = seasons.copy()
    keys = list(zip(seasons.player_id, seasons.season))
    seasons["is_star_season"] = [k in bpm_star or k in an_star for k in keys]
    seasons["all_nba_this"] = [k in an_star for k in keys]
    return seasons


def build_spells(seasons: pd.DataFrame) -> pd.DataFrame:
    """Walk each player's timeline; emit spell-season rows."""
    rows = []
    for pid, g in seasons.sort_values("season").groupby("player_id"):
        g = g.reset_index(drop=True)
        career_last = int(g.season.max())
        active = None  # (spell_id, franchise, entry_season)
        spell_n = 0
        for i, r in g.iterrows():
            season, fr = int(r.season), r.final_franchise
            nxt = g[g.season == season + 1]
            next_fr = nxt.final_franchise.iloc[0] if len(nxt) else None
            gap = (len(nxt) == 0) and (season < career_last)

            if active and active[1] != fr:
                # departed mid-window: event was recorded on the prior row
                active = None
            if active is None and r.is_star_season and season >= START_YEAR:
                spell_n += 1
                active = (f"{pid}_{spell_n}", fr, season)
            if active is None:
                continue

            departed = next_fr is not None and next_fr != fr
            retired = next_fr is None and season >= career_last and season < DATA_END
            censored = season == DATA_END and not departed
            rows.append({
                "spell_id": active[0], "player_id": pid, "player_name": r.player_name,
                "franchise_id": fr, "season": season, "entry_season": active[2],
                "age": r.age, "all_nba_this": r.all_nba_this,
                "event_departure": bool(departed),
                "event_retire": bool(retired and not departed),
                "censored": bool(censored),
                "gap_year_after": bool(gap),
            })
            if departed or retired:
                active = None
    return pd.DataFrame(rows)


def add_covariates(sp: pd.DataFrame, seasons: pd.DataFrame, fs: pd.DataFrame,
                   all_nba: pd.DataFrame, deep: pd.DataFrame) -> pd.DataFrame:
    # years_with_franchise: consecutive tenure incl. pre-star seasons
    tenure = {}
    ten_rows = []
    for pid, g in seasons.sort_values("season").groupby("player_id"):
        run_fr, run_start = None, None
        for _, r in g.iterrows():
            # reset tenure only on a franchise change; same-franchise gap
            # years (injury, overseas) do not restart the clock
            if r.final_franchise != run_fr:
                run_fr, run_start = r.final_franchise, r.season
            ten_rows.append((pid, r.season, int(r.season - run_start + 1)))
    ten = pd.DataFrame(ten_rows, columns=["player_id", "season", "years_with_franchise"])
    sp = sp.merge(ten, on=["player_id", "season"], how="left")

    # trailing 2-year team win pct
    fs2 = fs.rename(columns={"win_pct": "win_pct_t"})
    fs_prev = fs.rename(columns={"win_pct": "win_pct_prev", "season": "season_"})
    fs_prev["season"] = fs_prev.season_ + 1
    sp = (sp.merge(fs2, on=["franchise_id", "season"], how="left")
            .merge(fs_prev[["franchise_id", "season", "win_pct_prev"]],
                   on=["franchise_id", "season"], how="left"))
    sp["team_win_pct_2yr"] = sp[["win_pct_t", "win_pct_prev"]].mean(axis=1)

    # deep run in t..t-2
    deep_set = set(map(tuple, deep.values))
    sp["deep_run_recent"] = [
        any((f, s - k) in deep_set for k in (0, 1, 2))
        for f, s in zip(sp.franchise_id, sp.season)]

    # career All-NBA count through t: direct count of award seasons <= t.
    # (bugfix 2026-07-01: the previous exact-season merge + ffill lost honors
    # that never coincided with a spell row, e.g. Alvin Robertson's 1986
    # 2nd team vs his 1991-92 MIL spell)
    from bisect import bisect_right
    award_seasons = all_nba.groupby("player_id").season.apply(sorted).to_dict()
    sp["all_nba_count_career"] = [
        bisect_right(award_seasons.get(p, []), s)
        for p, s in zip(sp.player_id, sp.season)]
    sp = sp.drop(columns=["win_pct_t", "win_pct_prev"])

    # years of service (since first NBA season) for the supermax heuristic
    first = seasons.groupby("player_id").season.min().rename("first_season")
    sp = sp.merge(first, on="player_id", how="left")
    yos = sp.season - sp.first_season
    recent_an = [
        any((p, s - k) in set(map(tuple, all_nba[["player_id", "season"]].values))
            for k in (0, 1, 2)) for p, s in zip(sp.player_id, sp.season)]
    sp["supermax_eligible"] = (sp.season >= 2018) & (yos >= 7) & pd.Series(recent_an)

    tiers = pd.read_csv(PROJECT_ROOT / "config" / "market_tiers.csv")
    sp = sp.merge(tiers[["franchise_id", "market_tier"]], on="franchise_id", how="left")

    sp["contract_years_remaining"] = np.nan
    sp["contract_known"] = False
    return sp


def boundary_exit_type(roster_team: str | None, contract_teams: set[str],
                       spell_franchise: str, age: float) -> str:
    """Bobby's boundary rule (2026-07-01), one branch wider than proposed:
    at the data edge a missing next season is disambiguated by where the
    player currently BELONGS, not by the absence of stats.

      roster/contract with SAME franchise      -> censored  (Haliburton, Kyrie)
      roster/contract with DIFFERENT franchise -> departure (Lillard: MIL
          waived-and-stretched him; the MIL cap charge is dead money, his
          roster row is POR -> the franchise lost the star)
      no evidence: age >= 33 -> retire, else  -> review (NEEDS_REVIEW)

    Roster membership is primary evidence (dead money has a cap charge but no
    roster row); contract rows are the fallback when no roster row exists.
    A cap charge on the spell franchise PLUS elsewhere with no roster row is
    genuinely ambiguous -> review.
    """
    if roster_team == spell_franchise:
        return "censored"
    if roster_team is not None:
        return "departure"
    if not contract_teams:
        return "retire" if age is not None and age >= 33 else "review"
    if contract_teams == {spell_franchise}:
        return "censored"
    if spell_franchise not in contract_teams:
        return "departure"
    return "review"


def _norm_name(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().replace(".", "").replace("'", "").strip()


def apply_boundary_rule(sp: pd.DataFrame) -> pd.DataFrame:
    """Recode exits for spells whose last observed season is DATA_END - 1
    (next season missing at the data edge). Historical retire detection for
    earlier career ends is unchanged."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        roster = con.execute(
            "SELECT team, player FROM league_rosters_snapshot").fetchdf()
    except duckdb.CatalogException:
        print("WARNING: league_rosters_snapshot missing; boundary rule using contracts only")
        roster = pd.DataFrame(columns=["team", "player"])
    con.close()
    contracts = pd.read_csv(
        PROJECT_ROOT.parent / "offseason" / "data" / "nba_contracts_2026_27.csv")
    roster_team = {_norm_name(p): t for t, p in zip(roster.team, roster.player)}
    contract_teams: dict[str, set] = {}
    for t, p in zip(contracts.team_abbr, contracts.player):
        contract_teams.setdefault(_norm_name(p), set()).add(t)

    sp = sp.copy()
    sp["boundary_note"] = ""
    for spell_id, g in sp.groupby("spell_id"):
        last = g.sort_values("season").iloc[-1]
        if last.season != DATA_END - 1 or last.event_departure or last.censored:
            continue
        idx = g.sort_values("season").index[-1]
        key = _norm_name(last.player_name)
        rt, ct = roster_team.get(key), contract_teams.get(key, set())
        verdict = boundary_exit_type(rt, ct, last.franchise_id, last.age)
        note = f"boundary rule: roster={rt or 'none'} contracts={sorted(ct) or 'none'} -> {verdict}"
        sp.at[idx, "event_retire"] = verdict == "retire"
        sp.at[idx, "event_departure"] = verdict == "departure"
        sp.at[idx, "censored"] = verdict == "censored"
        sp.at[idx, "boundary_note"] = note
    return sp


def review_sheet(sp: pd.DataFrame) -> pd.DataFrame:
    def summarize(g):
        g = g.sort_values("season")
        last = g.iloc[-1]
        if last.event_departure:
            exit_type = "departure"
        elif last.event_retire:
            exit_type = "retire"
        elif last.censored:
            exit_type = "censored"
        else:
            exit_type = "NEEDS_REVIEW"
        flags = []
        if isinstance(last.get("boundary_note"), str) and last.boundary_note:
            flags.append(last.boundary_note)
        if last.gap_year_after:
            flags.append("gap_year_after_exit")
        if len(g) == 1:
            flags.append("single_season_spell")
        if exit_type == "retire" and last.season >= DATA_END - 1:
            flags.append("retire_vs_censor_edge")
        return pd.Series({
            "player_name": last.player_name, "franchise_id": last.franchise_id,
            "entry_season": int(g.entry_season.iloc[0]), "exit_season": int(last.season),
            "n_seasons": len(g), "exit_type": exit_type,
            "age_at_exit": last.age, "all_nba_count": int(last.all_nba_count_career),
            "review_flags": ";".join(flags), "bobby_correction": "", "bobby_notes": "",
        })
    return sp.groupby("spell_id").apply(summarize, include_groups=False).reset_index()


def main():
    ps, fs, all_nba = load_tables()
    seasons = star_entry_flags(final_team_by_season(ps), all_nba)
    sp = build_spells(seasons)
    sp = add_covariates(sp, seasons, fs, all_nba, deep_runs())
    sp = apply_boundary_rule(sp)
    STAGED.mkdir(exist_ok=True, parents=True)
    sp.to_parquet(STAGED / "star_spell_seasons_candidate.parquet", index=False)
    rev = review_sheet(sp)
    OUTPUTS.mkdir(exist_ok=True, parents=True)
    rev.to_csv(OUTPUTS / "star_spells_review.csv", index=False)
    print(f"spell-season rows: {len(sp)}  spells: {sp.spell_id.nunique()}  "
          f"players: {sp.player_id.nunique()}")
    print(rev.exit_type.value_counts().to_string())
    print(f"review sheet -> {OUTPUTS / 'star_spells_review.csv'}")


if __name__ == "__main__":
    main()
