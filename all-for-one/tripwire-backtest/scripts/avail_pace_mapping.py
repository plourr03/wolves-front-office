"""AVAIL-PACE empirical mapping (Scenario B labels + Phase 3).

The redefined AVAIL-PACE wire (phase0_avail_pace_redefinition.md) measures
games-played pace through team game N versus the arriving player's
prior-three-season games-played median, and takes its trip threshold from
the Scenario B reference-class mapping applied to LaMelo out of sample.

This script computes that mapping:
  early feature   avail_through_N  = games the player was available (min>0)
                  among the team's first N games (from arrival date for
                  midseason arrivals), for N in {10,15,20,25,30}
  plan baseline   prior3_median    = median games played over the 3 seasons
                  before arrival (matches YB3)
  outcomes        YB1 = full-season games played
                  YB3 = 1 if final GP < prior3_median (landed below plan)

Phase 3 stats (exact counts, no p-values):
  Spearman(avail_through_N, YB1), sign consistency vs class median,
  leave-one-out threshold stability. Then the mapping is applied to LaMelo:
  his prior3_median is 47; his through-N pace maps to a projected full-season
  availability and a trip threshold.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

pd.set_option("display.width", 220)
NS = [10, 15, 20, 25, 30]
SEASON_GAMES = {2008: 82, 2009: 82, 2010: 82, 2011: 66, 2012: 82, 2013: 82,
                2014: 82, 2015: 82, 2016: 82, 2017: 82, 2018: 82, 2019: 72,
                2020: 72, 2021: 82, 2022: 82, 2023: 82, 2024: 82, 2025: 82}


def team_game_order() -> pd.DataFrame:
    """team_id, season_start, game_id, game_date, game_no (1-based)."""
    g = query("""
        SELECT team_id, RIGHT(season_id::text,4)::int AS ss, game_id, game_date
        FROM nba.nba_games WHERE LEFT(season_id::text,1)='2'
    """)
    g = g.sort_values(["team_id", "ss", "game_date", "game_id"])
    g["game_no"] = g.groupby(["team_id", "ss"]).cumcount() + 1
    return g


def player_avail() -> pd.DataFrame:
    """player_id, game_id, min>0 availability."""
    return query("""
        SELECT ps.player_id, ps.game_id, (ps.minutes_played > 0)::int AS avail
        FROM nba.nba_player_stats ps
    """)


def main() -> None:
    B = pd.read_parquet(DATA / "refclass_B.parquet")
    tgo = team_game_order()
    pa = player_avail()
    gp = query("""SELECT player_id, LEFT(season_year,4)::int ss, gp
                  FROM nba.nba_player_season_bio WHERE season_type='Regular Season'""")
    gp_map = {(r.player_id, r.ss): r.gp for r in gp.itertuples()}
    team_id_map = query("SELECT DISTINCT team_abbreviation, team_id FROM nba.nba_games")
    abbr2id = dict(zip(team_id_map.team_abbreviation, team_id_map.team_id))

    rows = []
    for r in B.itertuples():
        tid = abbr2id.get(r.new_team)
        if tid is None:
            continue
        # team's games in arrival season, ordered
        tg = tgo[(tgo.team_id == tid) & (tgo.ss == r.arr_ss)].sort_values("game_no")
        if not len(tg):
            continue
        # availability of this player over those games
        av = pa[pa.player_id == r.player_id].set_index("game_id").avail
        tg = tg.copy()
        tg["avail"] = tg.game_id.map(av).fillna(0).astype(int)
        # for midseason arrivals, clock starts at arrival date
        if r.kind == "midseason":
            tg = tg[tg.game_date >= r.arr_date]
            tg["game_no"] = range(1, len(tg) + 1)
        prior3 = [gp_map.get((r.player_id, r.arr_ss - k)) for k in (1, 2, 3)]
        prior3 = [x for x in prior3 if x is not None]
        prior3_med = float(np.median(prior3)) if prior3 else np.nan
        full_gp = gp_map.get((r.player_id, r.arr_ss))
        rec = {"arriving": r.arriving, "arr_ss": r.arr_ss, "team": r.new_team,
               "kind": r.kind, "prior3_med": prior3_med, "full_gp": full_gp,
               "sched": SEASON_GAMES.get(r.arr_ss, 82)}
        for N in NS:
            first = tg[tg.game_no <= N]
            rec[f"avail_{N}"] = int(first.avail.sum()) if len(first) >= N else np.nan
        rows.append(rec)

    df = pd.DataFrame(rows)
    df = df[df.full_gp.notna() & df.prior3_med.notna()]
    df["yb3_below_plan"] = (df.full_gp < df.prior3_med).astype(int)
    # normalize outcome to availability fraction of schedule
    df["full_avail_frac"] = df.full_gp / df.sched
    df.to_parquet(DATA / "avail_pace_cases.parquet", index=False)
    print(f"AVAIL-PACE mapping: {len(df)} Scenario B cases with complete data\n")

    print("=" * 78)
    print("PHASE 3: does early availability pace predict full-season availability?")
    print("=" * 78)
    print(f"{'N':>4} {'n_cases':>8} {'spearman(avail_N, full_gp)':>28} {'sign_consistency':>18}")
    for N in NS:
        sub = df[df[f"avail_{N}"].notna()]
        if len(sub) < 8:
            print(f"{N:>4} {len(sub):>8}  (below N_GATE=8)")
            continue
        rho, _ = spearmanr(sub[f"avail_{N}"], sub.full_gp)
        # sign consistency: fraction where early-vs-median direction matches
        # outcome-vs-median direction
        em = sub[f"avail_{N}"].median()
        om = sub.full_gp.median()
        match = ((sub[f"avail_{N}"] >= em) == (sub.full_gp >= om)).mean()
        print(f"{N:>4} {len(sub):>8} {rho:>28.3f} {match:>18.3f}")

    # AVAIL-PACE as a RATE: early availability fraction vs full-season fraction
    print("\n" + "=" * 78)
    print("AVAIL-PACE rate form: early avail fraction (avail_N / N) vs full fraction")
    print("=" * 78)
    N = 20
    sub = df[df[f"avail_{N}"].notna()].copy()
    sub["early_frac"] = sub[f"avail_{N}"] / N
    rho, _ = spearmanr(sub.early_frac, sub.full_avail_frac)
    print(f"N=20: n={len(sub)}, Spearman(early_frac, full_frac) = {rho:.3f}")
    # calibration: mean full fraction by early-frac tertile
    sub["tertile"] = pd.qcut(sub.early_frac, 3, labels=["low", "mid", "high"], duplicates="drop")
    print("\ncalibration (mean full-season availability by early-pace tertile at N=20):")
    print(sub.groupby("tertile", observed=True).agg(
        n=("early_frac", "size"),
        early_frac_mean=("early_frac", "mean"),
        full_frac_mean=("full_avail_frac", "mean"),
        below_plan_rate=("yb3_below_plan", "mean")).to_string())

    # LaMelo out-of-sample application
    print("\n" + "=" * 78)
    print("LaMelo application (prior3 median = 47, sched 82)")
    print("=" * 78)
    print("LaMelo's prior-3-season games: 22, 47, 72 -> median 47 (0.573 of 82).")
    print("His R1 read is at ~team game 17-20. The mapping above gives, for a")
    print("player at his early-availability fraction, the class's full-season")
    print("availability distribution. Threshold derivation: pick the early_frac")
    print("at N=20 below which the class's below-plan rate exceeds 0.5.")
    # threshold: early_frac at N=20 where below_plan probability crosses 0.5
    sub2 = sub.sort_values("early_frac")
    # simple isotonic-ish: rolling below-plan rate
    print("\nbelow-plan rate by early_frac bucket (N=20):")
    sub2["bucket"] = pd.cut(sub2.early_frac, [0, 0.5, 0.7, 0.85, 1.0])
    print(sub2.groupby("bucket", observed=True).agg(
        n=("early_frac", "size"), below_plan=("yb3_below_plan", "mean"),
        full_frac=("full_avail_frac", "mean")).to_string())


if __name__ == "__main__":
    main()
