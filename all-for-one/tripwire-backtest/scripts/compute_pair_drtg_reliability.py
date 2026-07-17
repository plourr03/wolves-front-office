"""Raw PAIR-DRTG reliability: shared-floor defensive rating for qualifying
pairs, early vs rest, across the panel. This is the ACTUAL metric (not the
team-DRTG ceiling), computed at the shared-possession floor, to apply the
pre-staged PAIR-DRTG decision rule honestly.

For each team-season, enumerate pairs among the top-10 minute players; for
each pair compute shared-floor def poss and points against in the first 25
games and the rest; keep pairs clearing the possession floor in BOTH halves;
correlate early vs rest DRTG across all qualifying pairs.

The spec's note: raw pair DRTG is slow to stabilize, only the fitengine-shrunk
version is usable at R1. This measures the RAW reliability so the decision
rule (r(25) >= 0.50 -> wire candidate) reads off a real number.
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
DATA = REPO / "all-for-one" / "tripwire-backtest" / "data"
PANEL = DATA / "stints_panel"
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

FLOORS = [200, 350, 500]  # shared def poss floor per half; 350 is the R1 spec floor


def main() -> None:
    files = sorted(PANEL.glob("*.parquet"))
    print(f"loading {len(files)} panel games...", flush=True)
    df = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)
    df = df[~df.in_garbage_time]
    g = query("""SELECT game_id, team_id, RIGHT(season_id::text,4)::int ss, game_date
                 FROM nba.nba_games WHERE LEFT(season_id::text,1)='2'""")
    df = df.merge(g, on=["game_id", "team_id"], how="inner")
    df = df[(df.ss >= 2014) & (df.ss <= 2024)]
    gn = (df[["team_id", "ss", "game_id", "game_date"]].drop_duplicates()
          .sort_values(["team_id", "ss", "game_date", "game_id"]))
    gn["game_no"] = gn.groupby(["team_id", "ss"]).cumcount() + 1
    df = df.merge(gn[["team_id", "ss", "game_id", "game_no"]], on=["team_id", "ss", "game_id"])
    print(f"panel rows: {len(df)}", flush=True)

    # explode each stint into its lineup's players, keep def poss + pts against
    def top_players(sub):
        # minutes proxy: sum stint durations per player (player appears in lineup_id)
        secs = {}
        for L, d in zip(sub.lineup_id, sub.duration_sec):
            for p in L.split(","):
                secs[p] = secs.get(p, 0) + d
        return set(sorted(secs, key=secs.get, reverse=True)[:10])

    rows = []  # (floor, early_drtg, rest_drtg) per qualifying pair
    for (tid, ss), sub in df.groupby(["team_id", "ss"]):
        tp = top_players(sub)
        early = sub[sub.game_no <= 25]; rest = sub[sub.game_no > 25]
        # per-pair aggregates
        def pair_agg(half):
            agg = {}
            for L, dp, pa in zip(half.lineup_id, half.possessions_def, half.points_against):
                ps = [p for p in L.split(",") if p in tp]
                for a, b in combinations(sorted(ps), 2):
                    k = (a, b)
                    if k not in agg:
                        agg[k] = [0, 0]
                    agg[k][0] += dp; agg[k][1] += pa
            return agg
        ea, ra = pair_agg(early), pair_agg(rest)
        for k in set(ea) & set(ra):
            edp, epa = ea[k]; rdp, rpa = ra[k]
            for fl in FLOORS:
                if edp >= fl and rdp >= fl:
                    rows.append((fl, 100 * epa / edp, 100 * rpa / rdp))

    res = pd.DataFrame(rows, columns=["floor", "early", "rest"])
    print("\nRAW PAIR-DRTG reliability, early(first 25g) vs rest, by shared-poss floor:")
    print(f"{'floor':>6} {'n_pairs':>8} {'r(25)':>8}")
    for fl in FLOORS:
        s = res[res.floor == fl]
        if len(s) >= 8:
            r, _ = pearsonr(s.early, s.rest)
            print(f"{fl:>6} {len(s):>8} {r:>8.3f}")
    res.to_parquet(DATA / "phase1_pair_drtg.parquet", index=False)


if __name__ == "__main__":
    main()
