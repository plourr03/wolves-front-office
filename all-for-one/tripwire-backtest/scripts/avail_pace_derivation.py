"""AVAIL-PACE derivation memo computation (required before TRIPWIRES.md).

Answers the epistemic question: is the trip an ABSOLUTE count breakpoint or
LaMelo's BASELINE-CONDITIONED instantiation of a RELATIVE mapping? The
redefined wire measures pace vs the player's own prior-3 median, so the
mapping is relative; the LaMelo count falls out of his baseline.

Produces, for R1 (N=20) and R2 (N=37, mid of the 36-39 window):
  - relative mapping: early_rel = (avail_N / N) / (prior3_med / sched)
    vs P(below own plan). early_rel = 1.0 is pacing exactly at plan.
  - the early_rel where P(below plan) crosses 0.5 -> trip.
  - LaMelo's trip COUNT = threshold_rel * (plan/sched) * N, for plan = 47
    (baseline) and plan = 63 (analyst-prior sensitivity).
  - scorecard above vs below the line: median season games, share under the
    55-game contention bar, playoff availability (YB2).
  - full Scenario B (388) beside the injury-history subset (LaMelo-like:
    a prior season missing >= 50% of games).
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
SEASON_GAMES = {2008: 82, 2009: 82, 2010: 82, 2011: 66, 2012: 82, 2013: 82,
                2014: 82, 2015: 82, 2016: 82, 2017: 82, 2018: 82, 2019: 72,
                2020: 72, 2021: 82, 2022: 82, 2023: 82, 2024: 82, 2025: 82}
LAMELO_PLAN = 47
LAMELO_PLAN_HI = 63
CONTENTION_BAR = 55  # absolute availability floor Bobby named


def team_game_order():
    g = query("""SELECT team_id, RIGHT(season_id::text,4)::int ss, game_id, game_date,
                        LEFT(season_id::text,1) sp
                 FROM nba.nba_games""")
    rs = g[g.sp == "2"].sort_values(["team_id", "ss", "game_date", "game_id"]).copy()
    rs["game_no"] = rs.groupby(["team_id", "ss"]).cumcount() + 1
    po = g[g.sp == "4"]
    return rs, po


def player_avail():
    return query("SELECT player_id, game_id, (minutes_played>0)::int avail FROM nba.nba_player_stats")


def main() -> None:
    B = pd.read_parquet(DATA / "refclass_B.parquet")
    rs, po = team_game_order()
    pa = player_avail()
    av_by_pid = {pid: set(g.game_id[g.avail == 1]) for pid, g in pa.groupby("player_id")}
    gp = query("""SELECT player_id, LEFT(season_year,4)::int ss, gp
                  FROM nba.nba_player_season_bio WHERE season_type='Regular Season'""")
    gp_map = {(r.player_id, r.ss): r.gp for r in gp.itertuples()}
    a2i = query("SELECT DISTINCT team_abbreviation, team_id FROM nba.nba_games")
    abbr2id = dict(zip(a2i.team_abbreviation, a2i.team_id))

    NS = {"R1": 20, "R2": 37}
    rows = []
    for r in B.itertuples():
        tid = abbr2id.get(r.new_team)
        if tid is None:
            continue
        tg = rs[(rs.team_id == tid) & (rs.ss == r.arr_ss)].sort_values("game_no").copy()
        if not len(tg):
            continue
        avset = av_by_pid.get(r.player_id, set())
        tg["avail"] = tg.game_id.isin(avset).astype(int)
        if r.kind == "midseason":
            tg = tg[tg.game_date >= r.arr_date]
            tg["game_no"] = range(1, len(tg) + 1)
        prior3 = [gp_map.get((r.player_id, r.arr_ss - k)) for k in (1, 2, 3)]
        prior3 = [x for x in prior3 if x is not None]
        if not prior3:
            continue
        plan = float(np.median(prior3))
        sched = SEASON_GAMES.get(r.arr_ss, 82)
        full_gp = gp_map.get((r.player_id, r.arr_ss))
        if full_gp is None:
            continue
        # injury-history subset flag: any prior-4 season missing >= 50%
        severe = any((gp_map.get((r.player_id, r.arr_ss - k)) or sched) / SEASON_GAMES.get(r.arr_ss - k, 82) <= 0.5
                     for k in range(1, 5))
        # playoff availability YB2
        pog = po[(po.team_id == tid) & (po.ss == r.arr_ss)]
        yb2 = (pog.game_id.isin(avset).mean() if len(pog) else np.nan)
        rec = {"arriving": r.arriving, "arr_ss": r.arr_ss, "plan": plan, "sched": sched,
               "full_gp": full_gp, "below_plan": int(full_gp < plan),
               "under_55": int(full_gp < CONTENTION_BAR), "yb2_playoff_avail": yb2,
               "severe_injhx": severe}
        for lab, N in NS.items():
            first = tg[tg.game_no <= N]
            if len(first) >= N:
                ef = first.avail.sum() / N
                rec[f"avail_{lab}"] = int(first.avail.sum())
                rec[f"early_frac_{lab}"] = ef
                rec[f"early_rel_{lab}"] = ef / (plan / sched) if plan > 0 else np.nan
        rows.append(rec)

    df = pd.DataFrame(rows)
    df.to_parquet(DATA / "avail_pace_derivation.parquet", index=False)
    print(f"cases: {len(df)} full Scenario B; {int(df.severe_injhx.sum())} injury-history subset\n")

    def crossing(sub, relcol, N):
        """early_rel where P(below plan) crosses 0.5; return rel and count."""
        s = sub.dropna(subset=[relcol]).sort_values(relcol)
        # bucketed below-plan rate
        s["b"] = pd.cut(s[relcol], [0, 0.6, 0.85, 1.05, 1.3, 5])
        tab = s.groupby("b", observed=True).agg(n=(relcol, "size"),
                                                below=("below_plan", "mean"),
                                                med_gp=("full_gp", "median"),
                                                under55=("under_55", "mean"),
                                                po=("yb2_playoff_avail", "mean"))
        return tab

    for lab, N in NS.items():
        print("=" * 78)
        print(f"{lab} (N={N}) RELATIVE mapping: early pace as multiple of plan pace")
        print("=" * 78)
        relcol = f"early_rel_{lab}"
        fracol = f"early_frac_{lab}"
        sub = df.dropna(subset=[relcol])
        rho, _ = spearmanr(sub[relcol], sub.full_gp)
        print(f"Spearman(early_rel, full_gp) = {rho:.3f}  (n={len(sub)})")
        print("\nbelow-plan / outcome by early_rel bucket (1.0 = pacing at plan):")
        print(crossing(sub, relcol, N).to_string())
        # find crossing: lowest bucket where below<0.5
        print(f"\nLaMelo trip COUNT at {lab} (baseline-conditioned):")
        for plan, tag in [(LAMELO_PLAN, "baseline plan=47"), (LAMELO_PLAN_HI, "sensitivity plan=63")]:
            # trip where early_rel ~ 1.0 (pacing below own plan); express as count
            # use the empirical 0.5 crossing on early_rel
            s = sub.sort_values(relcol)
            # rolling: find rel where cumulative below-plan share drops through 0.5
            # simpler: threshold_rel = the rel at which bucketed below crosses 0.5
            thr_rel = _cross_rel(sub, relcol)
            trip_count = thr_rel * (plan / 82) * N
            print(f"  {tag}: threshold_rel={thr_rel:.2f} -> trip if avail < "
                  f"{trip_count:.1f} of first {N} games")

    # absolute-count view for comparison (class breakpoint on early_frac)
    print("\n" + "=" * 78)
    print("ABSOLUTE-count view (class breakpoint on raw early fraction, R1 N=20)")
    print("=" * 78)
    sub = df.dropna(subset=["early_frac_R1"])
    sub2 = sub.copy(); sub2["bucket"] = pd.cut(sub2.early_frac_R1, [0, 0.5, 0.7, 0.85, 1.0])
    print(sub2.groupby("bucket", observed=True).agg(
        n=("early_frac_R1", "size"), below_plan=("below_plan", "mean"),
        med_gp=("full_gp", "median"), under55=("under_55", "mean"),
        po_avail=("yb2_playoff_avail", "mean")).to_string())

    # injury-history subset beside full
    print("\n" + "=" * 78)
    print("INJURY-HISTORY SUBSET (LaMelo-like) vs FULL, R1 relative mapping")
    print("=" * 78)
    for name, d in [("FULL (388)", df), ("INJ-HX SUBSET", df[df.severe_injhx])]:
        s = d.dropna(subset=["early_rel_R1"])
        if len(s) >= 8:
            rho, _ = spearmanr(s.early_rel_R1, s.full_gp)
            thr = _cross_rel(s, "early_rel_R1")
            print(f"  {name}: n={len(s)}, Spearman={rho:.3f}, threshold_rel={thr:.2f}, "
                  f"LaMelo trip(47) = avail<{thr*(47/82)*20:.1f} of 20")


def _cross_rel(sub, relcol):
    """empirical early_rel where P(below plan) crosses 0.5, via fine buckets."""
    s = sub.dropna(subset=[relcol]).sort_values(relcol).reset_index(drop=True)
    edges = np.arange(0.2, 1.6, 0.1)
    prev = None
    for e in edges:
        window = s[(s[relcol] >= e - 0.15) & (s[relcol] < e + 0.15)]
        if len(window) >= 15:
            rate = window.below_plan.mean()
            if rate <= 0.5:
                return round(float(e), 2)
    return 1.0  # fallback: pacing at plan


if __name__ == "__main__":
    main()
