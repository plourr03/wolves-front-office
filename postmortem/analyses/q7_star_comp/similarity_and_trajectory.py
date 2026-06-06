"""Q7: Similarity scoring + trajectory analysis.

Computes weighted Euclidean similarity to Edwards' age-24 profile.
Then for each top comp, queries their career to determine peak
production years (post age-24 trajectory).

Feature weights (per Q7 spec Approach A, adapted):
- Playstyle features (50%): pts_per_36, fg3a_per_36, usage_proxy, ast_per_36, 3pa_rate, ft_rate
- Efficiency features (30%): ts_pct, efg_pct
- Volume features (20%): fga_per_36

Era control: z-score within the candidate pool. Acknowledges that era
norms differ (Wade era took fewer threes than the 2020s) but the
similarity comparison uses the same z-score basis.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import db
from analyses.q7_star_comp.edwards_comp_profiles import pull_player_career


OUT_DIR = Path("outputs/tables/q7_star_comp")
OUT_DIR.mkdir(parents=True, exist_ok=True)


PLAYSTYLE_FEATURES = ["pts_per_36", "fg3a_per_36", "usage_proxy", "ast_per_36", "3pa_rate", "ft_rate"]
EFFICIENCY_FEATURES = ["ts_pct", "efg_pct"]
VOLUME_FEATURES = ["fga_per_36"]
ALL_FEATURES = PLAYSTYLE_FEATURES + EFFICIENCY_FEATURES + VOLUME_FEATURES


def compute_similarity(profiles: pd.DataFrame, target_name: str = "Anthony Edwards") -> pd.DataFrame:
    """Compute weighted Euclidean similarity to the target player's profile."""
    # Z-score within pool
    feat_df = profiles[ALL_FEATURES].copy()
    for c in ALL_FEATURES:
        feat_df[c] = pd.to_numeric(feat_df[c], errors="coerce")
    z = (feat_df - feat_df.mean()) / feat_df.std(ddof=0)

    target_idx = profiles[profiles["player"] == target_name].index[0]
    target_z = z.iloc[target_idx]

    # Weights
    weights = {}
    for f in PLAYSTYLE_FEATURES:
        weights[f] = 0.50 / len(PLAYSTYLE_FEATURES)
    for f in EFFICIENCY_FEATURES:
        weights[f] = 0.30 / len(EFFICIENCY_FEATURES)
    for f in VOLUME_FEATURES:
        weights[f] = 0.20 / len(VOLUME_FEATURES)

    distances = []
    for idx in z.index:
        if idx == target_idx:
            distances.append(0.0)
            continue
        d_sq = 0
        for f in ALL_FEATURES:
            diff = z.loc[idx, f] - target_z[f]
            if pd.isna(diff):
                continue
            d_sq += weights[f] * (diff ** 2)
        distances.append(np.sqrt(d_sq))

    result = profiles[["player", "player_id", "season_year"]].copy()
    result["weighted_distance"] = distances
    result["similarity_score"] = 1 / (1 + result["weighted_distance"])
    result = result.sort_values("weighted_distance")
    return result


def get_peak_years_summary(player_id: int, age24_season: str) -> dict:
    """For a player, summarize their career peak metrics (post age-24)."""
    career = pull_player_career(player_id)
    if career.empty:
        return {}

    rs = career[career["season_type"] == "Regular Season"].copy()
    if rs.empty:
        return {}
    # Compute per-36 for every season
    rs["pts_per_36"] = 36 * rs["pts"] / rs["mins"].replace(0, np.nan)
    rs["fga_per_36"] = 36 * rs["fga"] / rs["mins"].replace(0, np.nan)
    rs["ts_pct"] = rs["pts"] / (2 * (rs["fga"] + 0.44 * rs["fta"])).replace(0, np.nan)
    rs["usage_proxy"] = (rs["fga"] + 0.44 * rs["fta"] + rs["tov"]) / rs["mins"].replace(0, np.nan)

    # Post age-24 seasons
    age24 = age24_season
    post = rs[rs["season_year"] >= age24].copy()
    if len(post) == 0:
        return {}

    peak_row = post.loc[post["pts_per_36"].idxmax()] if post["pts_per_36"].notna().any() else None
    return {
        "career_seasons": len(rs),
        "age24_season": age24,
        "peak_pts_per_36": float(post["pts_per_36"].max()) if not post.empty else np.nan,
        "peak_ts_pct": float(post["ts_pct"].max()) if not post.empty else np.nan,
        "peak_pts_season": peak_row["season_year"] if peak_row is not None else None,
        "post24_seasons_logged": len(post),
        "max_games_season": int(post["games"].max()) if not post.empty else 0,
    }


def run():
    print("Loading age-24 profiles...")
    profiles = pd.read_csv(OUT_DIR / "age24_profiles.csv")
    print(f"  {len(profiles)} profiles loaded")

    print("\nComputing weighted similarity to Edwards...")
    sim = compute_similarity(profiles)
    print(sim.to_string(index=False))
    sim.to_csv(OUT_DIR / "similarity_ranking.csv", index=False)

    # For top comps, query their post-age-24 career trajectory
    print("\nQuerying peak-year summaries for top comps...")
    rows = []
    for _, r in sim.iterrows():
        peak = get_peak_years_summary(r["player_id"], r["season_year"])
        if peak:
            rows.append({
                "player": r["player"],
                "weighted_distance": r["weighted_distance"],
                "similarity": r["similarity_score"],
                **peak,
            })

    trajectory = pd.DataFrame(rows)
    cols = ["player", "weighted_distance", "similarity", "age24_season",
             "career_seasons", "post24_seasons_logged",
             "peak_pts_per_36", "peak_ts_pct", "peak_pts_season"]
    print("\n=== Edwards comparable set + peak trajectory ===")
    print(trajectory[cols].round(3).to_string(index=False))
    trajectory.to_csv(OUT_DIR / "comp_trajectory_summary.csv", index=False)


if __name__ == "__main__":
    run()
