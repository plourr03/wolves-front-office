"""Weighted-recent RAPM: 2025-26 only, compared to 3-year pooled.

Per Bobby's data scientist's review of Q8: the Gobert decline test.
Defensive-anchor centers can decline rapidly at 33. The 3-year pooled
RAPM (2023-24, 2024-25, 2025-26) may overstate his current-year impact.
A 2025-26-only RAPM either confirms the pooled estimate is current-relevant
or reveals decline that must be incorporated into Q8 framing.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from analyses.q2_localize import config, rapm
from analyses.q2_localize import batch as q2_batch
from lib import db


def load_possessions_for_season(season_year: int) -> pd.DataFrame:
    """Load per-possession cache for one season's Wolves games."""
    # Use the same possession cache that rapm.py populates.
    season_gids = q2_batch.fetch_game_ids(season_year, "Regular Season",
                                            team_id=config.WOLVES_TEAM_ID)
    po_gids = q2_batch.fetch_game_ids(season_year, "Playoffs",
                                        team_id=config.WOLVES_TEAM_ID)
    all_gids = sorted(set(season_gids + po_gids))
    parts = []
    for gid in all_gids:
        df = rapm.process_game_to_possessions(gid)
        if df is not None:
            parts.append(df)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def fit_season_rapm(season_year: int, alpha: float = 2000.0, min_poss: int = 30) -> pd.DataFrame:
    """Build RAPM from one season's possessions only."""
    print(f"Loading {season_year} possessions...")
    poss = load_possessions_for_season(season_year)
    print(f"  {len(poss)} possessions across {poss['game_id'].nunique()} games")
    X_off, X_def, y, qualifying = rapm.build_rapm_matrices(poss, min_possessions_per_player=min_poss)
    off_c, def_c, intercept = rapm.fit_rapm(X_off, X_def, y, alpha=alpha)
    impacts = rapm.extract_player_impacts(off_c, def_c, intercept, qualifying)
    # Attach names
    pids = impacts["player_id"].astype(int).tolist()
    placeholders = ",".join(["%s"] * len(pids))
    names = db.query(
        f"""SELECT DISTINCT ON (player_id) player_id, player_name
            FROM nba_player_stats
            WHERE player_id IN ({placeholders})
            ORDER BY player_id, game_date DESC""",
        tuple(pids),
    )
    impacts["player_name"] = impacts["player_id"].map(dict(zip(names["player_id"], names["player_name"])))
    return impacts.sort_values("net_rapm", ascending=False).reset_index(drop=True)


def run():
    print("=== Weighted-recent RAPM: 2025-26 only ===\n")

    # 2025-26 only
    rapm_25 = fit_season_rapm(2025)
    rapm_25.to_csv(config.TABLE_DIR / "rapm_2025_only.csv", index=False)

    # Also run 2023-24-only and 2024-25-only for career-arc chart purposes
    print("\n=== 2024-25-only ===")
    rapm_24 = fit_season_rapm(2024)
    rapm_24.to_csv(config.TABLE_DIR / "rapm_2024_only.csv", index=False)
    print("\n=== 2023-24-only ===")
    rapm_23 = fit_season_rapm(2023)
    rapm_23.to_csv(config.TABLE_DIR / "rapm_2023_only.csv", index=False)

    # Print Gobert across the three season-only fits
    print("\n=== Gobert across single-season RAPMs ===")
    for label, df in [("2023-24", rapm_23), ("2024-25", rapm_24), ("2025-26", rapm_25)]:
        gob = df[df["player_id"] == 203497]
        if not gob.empty:
            r = gob.iloc[0]
            print(f"  {label}: net={r['net_rapm']:+.2f}  off={r['off_rapm']:+.2f}  def={r['def_rapm']:+.2f}")

    # Compare to pooled
    pooled = pd.read_csv(config.TABLE_DIR / "rapm_player_impacts.csv")
    pooled = pooled[["player_id", "off_rapm", "def_rapm", "net_rapm"]].rename(
        columns={"off_rapm": "off_pooled", "def_rapm": "def_pooled", "net_rapm": "net_pooled"}
    )
    recent = rapm_25[["player_id", "player_name", "off_rapm", "def_rapm", "net_rapm"]].rename(
        columns={"off_rapm": "off_2025", "def_rapm": "def_2025", "net_rapm": "net_2025"}
    )
    cmp = recent.merge(pooled, on="player_id", how="left")
    cmp["delta_net"] = cmp["net_2025"] - cmp["net_pooled"]
    cmp["delta_def"] = cmp["def_2025"] - cmp["def_pooled"]
    cmp["delta_off"] = cmp["off_2025"] - cmp["off_pooled"]

    # Focus on Wolves rotation
    wolves_pids = [config.ANT_ID, config.GOBERT_ID, config.NAZ_ID, config.RANDLE_ID,
                    config.MCDANIELS_ID, config.CONLEY_ID, config.DIVINCENZO_ID,
                    config.DOSUNMU_ID, config.CLARK_ID, config.HYLAND_ID,
                    config.SHANNON_ID, config.BERINGER_ID]
    wolves_cmp = cmp[cmp["player_id"].isin(wolves_pids)].copy()
    wolves_cmp = wolves_cmp.sort_values("net_pooled", ascending=False)

    print("\n=== Wolves rotation: 2025-26-only vs 3-year pooled RAPM ===")
    print(wolves_cmp[["player_name", "off_2025", "def_2025", "net_2025",
                       "off_pooled", "def_pooled", "net_pooled",
                       "delta_off", "delta_def", "delta_net"]].round(2).to_string(index=False))

    wolves_cmp.to_csv(config.TABLE_DIR / "rapm_2025_vs_pooled.csv", index=False)

    # Print top of league for sanity check
    print("\n=== 2025-26 top 10 by net RAPM (sanity check) ===")
    print(rapm_25.head(10)[["player_name", "off_rapm", "def_rapm", "net_rapm"]].round(2).to_string(index=False))

    print(f"\nTotal qualifying players in 2025-26-only: {len(rapm_25)}")


if __name__ == "__main__":
    run()
