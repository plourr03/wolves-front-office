"""Build a Wolves-rotation comparison table: RAPM vs raw on/off vs
lineup-grain net rating. Also check benchmark placement of Jokic, Brunson,
SGA, Wembanyama, etc.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from analyses.q2_localize import config


def run():
    # Load RAPM
    rapm = pd.read_csv(config.TABLE_DIR / "rapm_player_impacts.csv")
    # Load Edwards on/off (from yoy_edwards_lineups.csv has Edwards specifically)
    # For other Wolves players, use individual_on_off_2025.csv
    onoff = pd.read_csv(config.TABLE_DIR / "individual_on_off_2025.csv")

    # For 2025-26 RS specifically, build the comparison
    onoff_rs = onoff[onoff["season_type"] == "Regular Season"].copy()
    onoff_po = onoff[onoff["season_type"] == "Playoffs"].copy()

    # Merge RAPM with on/off (2025-26 only)
    merged = onoff_rs.merge(rapm[["player_id", "off_rapm", "def_rapm", "net_rapm"]],
                              on="player_id", how="left")
    merged = merged.sort_values("net_rapm", ascending=False, na_position="last")

    # Format
    cols = ["player_name", "on_minutes", "on_net_rating", "off_net_rating",
            "on_off_diff", "off_rapm", "def_rapm", "net_rapm"]
    print("\n=== Wolves rotation: RAPM vs Raw on/off (2025-26 RS) ===")
    print(merged[cols].round(2).to_string(index=False))
    merged.to_csv(config.TABLE_DIR / "rapm_vs_onoff_2025rs.csv", index=False)

    # Same for 2025-26 PO
    merged_po = onoff_po.merge(rapm[["player_id", "off_rapm", "def_rapm", "net_rapm"]],
                                 on="player_id", how="left")
    merged_po = merged_po.sort_values("net_rapm", ascending=False, na_position="last")
    print("\n=== Wolves rotation: RAPM vs Raw on/off (2025-26 PO) ===")
    print(merged_po[cols].round(2).to_string(index=False))
    merged_po.to_csv(config.TABLE_DIR / "rapm_vs_onoff_2025po.csv", index=False)

    # Benchmark check: Jokic, Brunson, SGA, Wembanyama, Murray, etc.
    benchmark_pids = {
        203999: "Jokic",
        1628973: "Brunson",
        1628983: "Shai Gilgeous-Alexander",
        1641705: "Wembanyama",
        1627750: "Murray",
        1629029: "Doncic",
        1628378: "Mitchell",
        1629027: "Maxey",
        203954: "Embiid",
        203935: "Butler",
        1627732: "Brown",
        1628369: "Tatum",
        1627759: "Brown (Jaylen)",
        201142: "Durant",
        202331: "Paul George",
    }
    bench_df = rapm[rapm["player_id"].isin(benchmark_pids.keys())].copy()
    bench_df["bench_name"] = bench_df["player_id"].map(benchmark_pids)
    bench_df = bench_df.sort_values("net_rapm", ascending=False)
    print("\n=== Benchmark league players (Wolves opponents in 3-season sample) ===")
    print(bench_df[["bench_name", "player_name", "off_rapm", "def_rapm", "net_rapm"]].round(2).to_string(index=False))

    # Print league rank percentile of each Wolves rotation player and benchmark
    rapm_sorted = rapm.sort_values("net_rapm", ascending=False).reset_index(drop=True)
    rapm_sorted["league_rank"] = rapm_sorted.index + 1
    n = len(rapm_sorted)

    wolves_pids = [config.ANT_ID, config.GOBERT_ID, config.NAZ_ID, config.RANDLE_ID,
                    config.MCDANIELS_ID, config.CONLEY_ID, config.DIVINCENZO_ID,
                    config.DOSUNMU_ID]
    wolves_ranks = rapm_sorted[rapm_sorted["player_id"].isin(wolves_pids)][
        ["player_name", "net_rapm", "league_rank"]]
    print(f"\nLeague ranks (out of {n} qualifying players) for key Wolves:")
    print(wolves_ranks.to_string(index=False))

    bench_ranks = rapm_sorted[rapm_sorted["player_id"].isin(benchmark_pids.keys())].copy()
    bench_ranks["bench_name"] = bench_ranks["player_id"].map(benchmark_pids)
    print(f"\nLeague ranks for benchmark players:")
    print(bench_ranks[["bench_name", "player_name", "net_rapm", "league_rank"]].to_string(index=False))


if __name__ == "__main__":
    run()
