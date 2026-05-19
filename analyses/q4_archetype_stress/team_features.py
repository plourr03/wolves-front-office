"""Q4 archetype stress test: build per-team feature vectors for clustering.

For each (team, season) in 2023-24, 2024-25, 2025-26, pull:
- Offensive features: pace, 3PA rate, rim share, midrange share
- Synergy play type frequencies (PR-Ball-Handler, Iso, Post-up, Cut, OffScreen, Spotup)
- Defensive features: defensive rating, opponent 3PA rate, opponent rim FG%

Output: a 90-row (30 teams * 3 seasons) feature DataFrame.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import db


OUT_DIR = Path("outputs/tables/q4_archetype_stress")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def pull_team_advanced(seasons=(2023, 2024, 2025)) -> pd.DataFrame:
    """Per-team season-aggregated advanced stats."""
    placeholders = ",".join(["%s"] * len(seasons))
    sql = f"""
        SELECT tas.team_id, tas.team_tricode,
               (g.season_id %% 10000)::int AS season_start_year,
               AVG(tas.offensive_rating) AS avg_ortg,
               AVG(tas.defensive_rating) AS avg_drtg,
               AVG(tas.net_rating) AS avg_net_rtg,
               AVG(tas.pace) AS avg_pace,
               AVG(tas.true_shooting_percentage) AS avg_ts,
               AVG(tas.effective_field_goal_percentage) AS avg_efg
        FROM nba_team_advanced_stats tas
        JOIN nba_games g ON tas.game_id = g.game_id AND tas.team_id = g.team_id
        WHERE (g.season_id %% 10000) IN ({placeholders})
          AND g.season_type = 'Regular Season'
        GROUP BY tas.team_id, tas.team_tricode, g.season_id
    """
    df = db.query(sql, tuple(seasons))
    for c in ("avg_ortg", "avg_drtg", "avg_net_rtg", "avg_pace", "avg_ts", "avg_efg"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def pull_team_shot_diet(season_year: str = "2025-26") -> pd.DataFrame:
    """Aggregate shot chart detail per team for the season: 3PA rate, rim share."""
    sql = """
        SELECT team_id, season_year,
               COUNT(*) AS fga,
               SUM(CASE WHEN shot_type LIKE '%%3PT%%' THEN 1 ELSE 0 END) AS fg3a,
               SUM(CASE WHEN shot_zone_basic = 'Restricted Area' THEN 1 ELSE 0 END) AS rim_attempts,
               SUM(CASE WHEN shot_zone_basic IN ('Mid-Range') THEN 1 ELSE 0 END) AS mid_attempts,
               SUM(CASE WHEN shot_made_flag = 1 THEN 1 ELSE 0 END) AS fgm
        FROM nba_shot_chart_detail
        WHERE season_year = %s
          AND season_type = 'Regular Season'
        GROUP BY team_id, season_year
    """
    df = db.query(sql, (season_year,))
    for c in ("fga", "fg3a", "rim_attempts", "mid_attempts", "fgm"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["3pa_rate"] = df["fg3a"] / df["fga"]
    df["rim_rate"] = df["rim_attempts"] / df["fga"]
    df["mid_rate"] = df["mid_attempts"] / df["fga"]
    df["fg_pct"] = df["fgm"] / df["fga"]
    df["season_start_year"] = int(season_year[:4])
    return df


def pull_team_play_types(seasons=("2023-24", "2024-25", "2025-26")) -> pd.DataFrame:
    """Synergy team play types by season."""
    placeholders = ",".join(["%s"] * len(seasons))
    sql = f"""
        SELECT team_id, season_year, play_type, type_grouping,
               poss_pct, ppp, poss
        FROM nba_synergy_team_play_types
        WHERE season_year IN ({placeholders})
          AND season_type = 'Regular Season'
    """
    df = db.query(sql, tuple(seasons))
    for c in ("poss_pct", "ppp", "poss"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["season_start_year"] = df["season_year"].apply(lambda s: int(s[:4]))
    return df


def pull_opponent_shot_diet_against(seasons=("2023-24", "2024-25", "2025-26")) -> pd.DataFrame:
    """Per defending team, opponent shot diet aggregated."""
    rows = []
    for season in seasons:
        sql = """
            SELECT g.team_id AS def_team_id,
                   COUNT(*) AS opp_fga,
                   SUM(CASE WHEN scd.shot_type LIKE '%%3PT%%' THEN 1 ELSE 0 END) AS opp_fg3a,
                   SUM(CASE WHEN scd.shot_zone_basic = 'Restricted Area' THEN 1 ELSE 0 END) AS opp_rim_attempts,
                   SUM(CASE WHEN scd.shot_made_flag = 1 THEN 1 ELSE 0 END) AS opp_fgm,
                   SUM(CASE WHEN scd.shot_zone_basic = 'Restricted Area' AND scd.shot_made_flag = 1 THEN 1 ELSE 0 END) AS opp_rim_makes
            FROM nba_shot_chart_detail scd
            JOIN nba_games g ON g.game_id = scd.game_id AND g.team_id <> scd.team_id
            WHERE scd.season_year = %s
              AND scd.season_type = 'Regular Season'
            GROUP BY g.team_id
        """
        df = db.query(sql, (season,))
        df["season_start_year"] = int(season[:4])
        for c in ("opp_fga", "opp_fg3a", "opp_rim_attempts", "opp_fgm", "opp_rim_makes"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["opp_3pa_rate"] = df["opp_fg3a"] / df["opp_fga"]
        df["opp_rim_share"] = df["opp_rim_attempts"] / df["opp_fga"]
        df["opp_rim_fg_pct"] = df["opp_rim_makes"] / df["opp_rim_attempts"]
        rows.append(df)
    return pd.concat(rows, ignore_index=True)


def build_team_feature_matrix() -> pd.DataFrame:
    """Build the full feature matrix for all 30 teams x 3 seasons."""
    adv = pull_team_advanced()
    print(f"  Advanced stats: {len(adv)} rows")

    # Per-season shot diets and play types
    diets = []
    for sy in ("2023-24", "2024-25", "2025-26"):
        diets.append(pull_team_shot_diet(sy))
    diet = pd.concat(diets, ignore_index=True)
    print(f"  Shot diet: {len(diet)} rows")

    plays = pull_team_play_types()
    # Wide-pivot: one row per (team, season), one column per play type for offensive
    off_plays = plays[plays["type_grouping"] == "Offensive"]
    play_pivot = off_plays.pivot_table(
        index=["team_id", "season_start_year"],
        columns="play_type", values="poss_pct", aggfunc="mean"
    ).reset_index()
    play_pivot.columns = ["team_id", "season_start_year"] + [
        f"off_{c}_pct" for c in play_pivot.columns[2:]
    ]
    print(f"  Play type pivot: {len(play_pivot)} rows")

    opp_diet = pull_opponent_shot_diet_against()
    print(f"  Opponent shot diet: {len(opp_diet)} rows")

    # Merge all
    merged = adv.merge(diet[["team_id", "season_start_year", "3pa_rate", "rim_rate",
                                "mid_rate"]],
                         on=["team_id", "season_start_year"], how="left")
    merged = merged.merge(play_pivot, on=["team_id", "season_start_year"], how="left")
    merged = merged.merge(opp_diet[["def_team_id", "season_start_year",
                                       "opp_3pa_rate", "opp_rim_share", "opp_rim_fg_pct"]],
                            left_on=["team_id", "season_start_year"],
                            right_on=["def_team_id", "season_start_year"],
                            how="left").drop(columns=["def_team_id"])
    return merged


def run():
    print("Q4: Building team feature matrix across 2023-24, 2024-25, 2025-26\n")
    df = build_team_feature_matrix()
    df.to_csv(OUT_DIR / "team_features_3season.csv", index=False)
    print(f"\nFeature matrix: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample (first 5 rows):")
    print(df.head().round(3).to_string())


if __name__ == "__main__":
    run()
