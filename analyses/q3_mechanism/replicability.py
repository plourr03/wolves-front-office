"""Q3 replicability analysis: which 2025-26 teams could plausibly replicate
the Spurs' scheme against Edwards?

Hypothesis: The Spurs' scheme that suppressed Edwards' 3PA volume (from
~8.4/g in RS to 5.3/g in PO R2) relied on:
  1. Elite rim protection at center (Wembanyama, allowing aggressive
     perimeter closeouts because the rim is protected)
  2. Switchable wings (allowing closeouts on Edwards' off-ball catches)
  3. Coordinated defensive discipline

For each team, pull defensive proxies:
  - Team defensive rating
  - Opponent rim FG% (via shot chart detail)
  - Opponent 3PA rate (do they hold opponents to fewer threes? proxy for
    closeout discipline)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import db


OUT_DIR = Path("outputs/tables/q3_mechanism")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def team_defensive_profile(season_year: str = "2025-26") -> pd.DataFrame:
    """For each team, compute defensive proxies for the 2025-26 season."""
    # Pull from team game-level advanced stats
    sql = """
        SELECT tas.team_id, tas.team_tricode,
               AVG(tas.defensive_rating) AS avg_def_rtg,
               AVG(tas.pace) AS avg_pace
        FROM nba_team_advanced_stats tas
        JOIN nba_games g ON tas.game_id = g.game_id AND tas.team_id = g.team_id
        WHERE (g.season_id % 10000) = 2025
          AND g.season_type = 'Regular Season'
        GROUP BY tas.team_id, tas.team_tricode
        ORDER BY avg_def_rtg
    """
    df = db.query(sql)
    for c in ("avg_def_rtg", "avg_pace"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def opponent_shot_diet_against(season_year: str = "2025-26") -> pd.DataFrame:
    """For each team, what's the opponent shot diet (3PA rate, rim attempts)?
    Uses nba_shot_chart_detail. The team_id column on shot chart is the
    SHOOTING team; we want shots TAKEN AGAINST each team. We join via game_id
    and pick the non-shooting team as the defensive team.

    For each game x defending team, count opponent shots by type.
    """
    sql = """
        SELECT scd.game_id, scd.team_id AS shooting_team_id,
               g.team_id AS def_team_id,
               COUNT(*) AS opp_fga,
               SUM(CASE WHEN scd.shot_type LIKE '%%3PT%%' THEN 1 ELSE 0 END) AS opp_fg3a,
               SUM(CASE WHEN scd.shot_zone_basic = 'Restricted Area' THEN 1 ELSE 0 END) AS opp_rim_attempts,
               SUM(CASE WHEN scd.shot_made_flag = 1 THEN 1 ELSE 0 END) AS opp_fgm,
               SUM(CASE WHEN scd.shot_type LIKE '%%3PT%%' AND scd.shot_made_flag = 1 THEN 1 ELSE 0 END) AS opp_fg3m,
               SUM(CASE WHEN scd.shot_zone_basic = 'Restricted Area' AND scd.shot_made_flag = 1 THEN 1 ELSE 0 END) AS opp_rim_makes
        FROM nba_shot_chart_detail scd
        JOIN nba_games g ON g.game_id = scd.game_id AND g.team_id <> scd.team_id
        WHERE scd.season_year = %s
          AND scd.season_type = 'Regular Season'
        GROUP BY scd.game_id, scd.team_id, g.team_id
    """
    df = db.query(sql, (season_year,))
    for c in ("opp_fga", "opp_fg3a", "opp_rim_attempts", "opp_fgm",
              "opp_fg3m", "opp_rim_makes"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def aggregate_def_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate opponent shot diet to team-season level."""
    grouped = df.groupby("def_team_id").agg(
        games=("game_id", "nunique"),
        opp_fga=("opp_fga", "sum"),
        opp_fg3a=("opp_fg3a", "sum"),
        opp_fgm=("opp_fgm", "sum"),
        opp_fg3m=("opp_fg3m", "sum"),
        opp_rim_attempts=("opp_rim_attempts", "sum"),
        opp_rim_makes=("opp_rim_makes", "sum"),
    ).reset_index()
    grouped["opp_3pa_rate"] = grouped["opp_fg3a"] / grouped["opp_fga"]
    grouped["opp_3p_pct"] = grouped["opp_fg3m"] / grouped["opp_fg3a"].replace(0, np.nan)
    grouped["opp_rim_share"] = grouped["opp_rim_attempts"] / grouped["opp_fga"]
    grouped["opp_rim_fg_pct"] = grouped["opp_rim_makes"] / grouped["opp_rim_attempts"].replace(0, np.nan)
    return grouped


def team_abbreviations() -> dict[int, str]:
    df = db.query("""
        SELECT DISTINCT team_id, team_abbreviation
        FROM nba_games
        WHERE (season_id % 10000) = 2025
    """)
    return dict(zip(df["team_id"], df["team_abbreviation"]))


def run():
    print("Pulling team defensive ratings (2025-26 RS)...")
    def_rtg = team_defensive_profile()
    print(def_rtg.head(15).round(2).to_string(index=False))

    print("\nPulling opponent shot diet by defensive team...")
    opp = opponent_shot_diet_against("2025-26")
    agg = aggregate_def_profile(opp)
    abbrev = team_abbreviations()
    agg["team_abbr"] = agg["def_team_id"].map(abbrev)

    merged = agg.merge(def_rtg[["team_id", "avg_def_rtg"]],
                         left_on="def_team_id", right_on="team_id", how="left")
    merged = merged.sort_values("opp_3pa_rate")

    print("\n=== Teams that hold opponents to fewer 3PA (closeout discipline proxy) ===")
    cols = ["team_abbr", "games", "opp_fga", "opp_3pa_rate", "opp_3p_pct",
             "opp_rim_share", "opp_rim_fg_pct", "avg_def_rtg"]
    print(merged[cols].head(15).round(3).to_string(index=False))
    print("\n=== Teams that allow MORE 3PA (less closeout discipline) ===")
    print(merged[cols].tail(10).round(3).to_string(index=False))

    merged.to_csv(OUT_DIR / "team_defensive_profiles_2025_26.csv", index=False)

    # Composite score: low opp_3pa_rate AND low opp_rim_fg_pct = Spurs-like archetype
    print("\n=== Composite: which teams combine elite closeout (low opp 3PA rate) WITH rim protection (low opp rim FG%) ===")
    league_3pa_rate = merged["opp_3pa_rate"].mean()
    league_rim_fg = merged["opp_rim_fg_pct"].mean()
    merged["closeout_better_than_avg"] = league_3pa_rate - merged["opp_3pa_rate"]
    merged["rim_protection_better_than_avg"] = league_rim_fg - merged["opp_rim_fg_pct"]
    merged["spurs_archetype_score"] = merged["closeout_better_than_avg"] + merged["rim_protection_better_than_avg"]
    merged = merged.sort_values("spurs_archetype_score", ascending=False)
    print(merged[["team_abbr", "opp_3pa_rate", "opp_3p_pct", "opp_rim_fg_pct",
                    "avg_def_rtg", "closeout_better_than_avg",
                    "rim_protection_better_than_avg",
                    "spurs_archetype_score"]].head(10).round(3).to_string(index=False))
    merged.to_csv(OUT_DIR / "team_spurs_archetype_score.csv", index=False)


if __name__ == "__main__":
    run()
