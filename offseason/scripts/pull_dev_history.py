#!/usr/bin/env python3
"""
pull_dev_history.py  -- pull season-level MINUTES + BLOCKS (and basic counting stats) from
nba_api leaguedashplayerstats across ~25 years, cached to data/cache/. The bio table has age /
height / draft but no minutes or blocks; blocks are the most diagnostic rim signal, so the
rim-anchor comp set is rebuilt on blocks + rebounding + size with real minutes for the role tiers.

    python pull_dev_history.py
"""

import os
import sys
import time
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "data", "cache")
os.makedirs(CACHE, exist_ok=True)
OUT = os.path.join(CACHE, "season_min_blk_2001_2026.csv")

from nba_api.stats.endpoints import leaguedashplayerstats  # noqa: E402

SEASONS = [f"{y}-{str(y+1)[2:]}" for y in range(2001, 2026)]   # 2001-02 .. 2025-26
COLS = ["PLAYER_ID", "PLAYER_NAME", "AGE", "GP", "MIN", "REB", "AST", "BLK", "STL", "PTS"]


def main():
    rows = []
    for s in SEASONS:
        for attempt in range(4):
            try:
                df = leaguedashplayerstats.LeagueDashPlayerStats(
                    season=s, season_type_all_star="Regular Season", per_mode_detailed="Totals",
                    timeout=60).get_data_frames()[0]
                for _, r in df.iterrows():
                    rows.append({"season": s, **{c: r[c] for c in COLS}})
                print(f"  {s}: {len(df)} players")
                break
            except Exception as e:
                print(f"  {s}: attempt {attempt+1} failed ({str(e)[:50]}); retrying")
                time.sleep(2.0)
        time.sleep(0.7)   # be polite to the endpoint
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["season"] + COLS)
        w.writeheader(); w.writerows(rows)
    print(f"wrote {len(rows)} player-seasons -> {OUT}")


if __name__ == "__main__":
    main()
