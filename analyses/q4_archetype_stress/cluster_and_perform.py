"""Q4: Cluster teams into archetypes, analyze Wolves performance vs each.

Uses K-means clustering on the 2025-26 team feature matrix to identify
4-5 archetype clusters. Then computes the Wolves' regular season + playoff
performance against each cluster.

Output: archetype labels, team-archetype assignments, Wolves' performance
by archetype.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from lib import db


IN_FILE = Path("outputs/tables/q4_archetype_stress/team_features_3season.csv")
OUT_DIR = Path("outputs/tables/q4_archetype_stress")
WOLVES_TEAM_ID = 1610612750

# Features for clustering: capture the offensive/defensive archetype, not
# the team's quality. Skip avg_ortg / avg_drtg / avg_net_rtg.
CLUSTER_FEATURES_OFFENSIVE = [
    "3pa_rate", "rim_rate",
    "off_Isolation_pct", "off_PRBallHandler_pct", "off_Postup_pct",
    "off_Transition_pct", "off_Spotup_pct", "off_Cut_pct",
    "off_OffScreen_pct",
    "avg_pace",
]

CLUSTER_FEATURES_DEFENSIVE = [
    "opp_3pa_rate", "opp_rim_share", "opp_rim_fg_pct",
]


def cluster_teams(features_df: pd.DataFrame, season: int = 2025,
                   n_clusters: int = 5, seed: int = 42) -> pd.DataFrame:
    """K-means cluster teams in the given season."""
    df = features_df[features_df["season_start_year"] == season].copy().reset_index(drop=True)
    feature_cols = CLUSTER_FEATURES_OFFENSIVE + CLUSTER_FEATURES_DEFENSIVE
    X = df[feature_cols].copy()
    # Fill NaN with column means (rare)
    X = X.fillna(X.mean())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    df["cluster"] = km.fit_predict(X_scaled)
    return df


def label_clusters(clustered: pd.DataFrame) -> dict:
    """Generate descriptive labels for each cluster based on feature means."""
    cluster_summary = clustered.groupby("cluster").agg({
        "3pa_rate": "mean",
        "rim_rate": "mean",
        "off_Isolation_pct": "mean",
        "off_PRBallHandler_pct": "mean",
        "off_Postup_pct": "mean",
        "off_Transition_pct": "mean",
        "off_Spotup_pct": "mean",
        "avg_pace": "mean",
        "opp_3pa_rate": "mean",
        "opp_rim_fg_pct": "mean",
        "avg_drtg": "mean",
    }).round(3)
    # Print for inspection; manual labels below
    print("Cluster characteristics:")
    print(cluster_summary)
    return cluster_summary.to_dict("index")


def pull_wolves_games(season_year: int) -> pd.DataFrame:
    """Pull all Wolves games + opponent + result for the season."""
    sql = """
        SELECT a.game_id, a.game_date, a.team_id,
               a.matchup, a.wl, a.pts AS wolves_pts, a.plus_minus,
               b.team_id AS opp_team_id, b.team_abbreviation AS opp_abbr,
               b.pts AS opp_pts, a.season_type
        FROM nba_games a
        JOIN nba_games b ON a.game_id = b.game_id AND a.team_id <> b.team_id
        WHERE a.team_id = %s
          AND (a.season_id %% 10000) = %s
        ORDER BY a.game_date
    """
    df = db.query(sql, (WOLVES_TEAM_ID, season_year))
    df["game_date"] = pd.to_datetime(df["game_date"])
    for c in ("wolves_pts", "opp_pts", "plus_minus"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["margin"] = df["wolves_pts"] - df["opp_pts"]
    return df


def wolves_perf_by_cluster(games: pd.DataFrame, clustered: pd.DataFrame) -> pd.DataFrame:
    """For each cluster, compute the Wolves' performance against teams in that cluster."""
    # Build a map: opp_team_id -> cluster
    opp_cluster_map = dict(zip(clustered["team_id"], clustered["cluster"]))
    games = games.copy()
    games["opp_cluster"] = games["opp_team_id"].map(opp_cluster_map)

    summary = games.groupby(["opp_cluster", "season_type"]).agg(
        games=("game_id", "nunique"),
        wins=("wl", lambda x: (x == "W").sum()),
        losses=("wl", lambda x: (x == "L").sum()),
        avg_margin=("margin", "mean"),
        avg_wolves_pts=("wolves_pts", "mean"),
        avg_opp_pts=("opp_pts", "mean"),
    ).reset_index()
    summary["win_pct"] = summary["wins"] / summary["games"]
    summary["avg_margin"] = summary["avg_margin"].round(2)
    summary["win_pct"] = summary["win_pct"].round(3)
    return summary


def run():
    print("Loading team feature matrix...")
    features = pd.read_csv(IN_FILE)
    print(f"  {len(features)} team-season rows")

    print("\n=== Clustering 2025-26 teams (k=5) ===")
    clustered = cluster_teams(features, season=2025, n_clusters=5)

    cluster_summary = label_clusters(clustered)

    print("\n=== Cluster assignments ===")
    for cid in sorted(clustered["cluster"].unique()):
        teams = clustered[clustered["cluster"] == cid].sort_values("avg_net_rtg", ascending=False)
        print(f"\nCluster {cid}:")
        for _, r in teams.iterrows():
            print(f"  {r['team_tricode']}: ortg={r['avg_ortg']:.1f}, drtg={r['avg_drtg']:.1f}, "
                  f"3pa={r['3pa_rate']:.3f}, opp_3pa={r['opp_3pa_rate']:.3f}, "
                  f"opp_rim={r['opp_rim_fg_pct']:.3f}")

    clustered.to_csv(OUT_DIR / "cluster_assignments_2025_26.csv", index=False)

    print("\n=== Wolves performance by opponent cluster ===")
    games = pull_wolves_games(2025)
    print(f"  Wolves 2025-26 games pulled: {len(games)}")

    perf = wolves_perf_by_cluster(games, clustered)
    print(perf.to_string(index=False))
    perf.to_csv(OUT_DIR / "wolves_perf_by_cluster_2025_26.csv", index=False)

    # Also Wolves' 2024-25 + 2023-24 performance for context
    print("\n=== Wolves performance by opponent cluster (3-year combined) ===")
    all_games = []
    for sy in [2023, 2024, 2025]:
        all_games.append(pull_wolves_games(sy))
    all_g = pd.concat(all_games, ignore_index=True)
    # Use 2025-26 cluster assignments for all years (assume team archetypes are roughly stable)
    perf_all = wolves_perf_by_cluster(all_g, clustered)
    print(perf_all.to_string(index=False))
    perf_all.to_csv(OUT_DIR / "wolves_perf_by_cluster_3year.csv", index=False)


if __name__ == "__main__":
    run()
