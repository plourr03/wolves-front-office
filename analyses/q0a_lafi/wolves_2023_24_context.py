"""How good was the 2023-24 Wolves offense, really?

Article 2's opening calls it "some of the most organized offense in the
league." The article's own baseline section calls it "a normal one." This
script settles which is accurate, on two axes:

  1. Output: where did the 2023-24 Wolves rank among the 30 teams in
     offensive rating, defensive rating, net rating (Regular Season).
  2. Architecture: where did they rank on Full LAFI and Sharp LAFI within
     the 2023-24 season (lower = more designed / less pickup).

Re-runnable: python -m analyses.q0a_lafi.wolves_2023_24_context
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from lib import db

WOLVES = 1610612750
COMPOSITE_CSV = Path("outputs/tables/q0a_lafi/lafi_composite_5component.csv")

pd.set_option("display.width", 170)
pd.set_option("display.max_rows", 40)


def team_ratings_2023_24() -> pd.DataFrame:
    """Possession-weighted ORtg / DRtg / NetRtg per team, 2023-24 RS."""
    sql = """
        SELECT
            g.team_id,
            g.team_abbreviation,
            COUNT(DISTINCT g.game_id) AS gp,
            SUM(tas.offensive_rating * tas.possessions)
                / NULLIF(SUM(tas.possessions), 0) AS off_rating,
            SUM(tas.defensive_rating * tas.possessions)
                / NULLIF(SUM(tas.possessions), 0) AS def_rating,
            SUM(tas.net_rating * tas.possessions)
                / NULLIF(SUM(tas.possessions), 0) AS net_rating
        FROM nba_games g
        JOIN nba_team_advanced_stats tas
            ON tas.game_id = g.game_id AND tas.team_id = g.team_id
        WHERE g.season_type = 'Regular Season'
          AND (g.season_id %% 10000) = %s
        GROUP BY g.team_id, g.team_abbreviation
    """
    df = db.query(sql, (2023,))
    for c in ("gp", "off_rating", "def_rating", "net_rating"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["off_rank"] = df["off_rating"].rank(ascending=False).astype(int)
    df["def_rank"] = df["def_rating"].rank(ascending=True).astype(int)
    df["net_rank"] = df["net_rating"].rank(ascending=False).astype(int)
    return df


def lafi_ranks_2023_24() -> pd.DataFrame:
    """Within-2023-24 ranking on Full and Sharp LAFI. Lower = more designed."""
    comp = pd.read_csv(COMPOSITE_CSV)
    s = comp[(comp["season_start_year"] == 2023)
             & (comp["season_type"] == "Regular Season")].copy()
    s["full_designed_rank"] = s["lafi_weighted_pct_sum"].rank(ascending=True).astype(int)
    s["sharp_designed_rank"] = s["sharp_lafi_weighted_pct_sum"].rank(ascending=True).astype(int)
    return s


def run() -> None:
    print("=== The 2023-24 Wolves offense in context ===\n")

    ratings = team_ratings_2023_24()
    n = len(ratings)
    print(f"Teams in 2023-24 RS: {n}\n")

    print("Offensive rating, all teams (best to worst):")
    show = ratings.sort_values("off_rating", ascending=False)
    print(show[["team_abbreviation", "off_rating", "off_rank",
                "def_rating", "def_rank", "net_rating", "net_rank"]]
          .to_string(index=False, float_format=lambda x: f"{x:.1f}"))

    wolves = ratings[ratings["team_id"] == WOLVES].iloc[0]
    print(f"\n--- Minnesota 2023-24 RS ---")
    print(f"  Offensive rating: {wolves['off_rating']:.1f}  -> rank {wolves['off_rank']} of {n}")
    print(f"  Defensive rating: {wolves['def_rating']:.1f}  -> rank {wolves['def_rank']} of {n}")
    print(f"  Net rating:       {wolves['net_rating']:+.1f}  -> rank {wolves['net_rank']} of {n}")

    lafi = lafi_ranks_2023_24()
    nl = len(lafi)
    win = lafi[lafi["team_id"] == WOLVES]
    if win.empty:
        print("\n[LAFI] Minnesota row not found in composite CSV for 2023-24 RS.")
        return
    w = win.iloc[0]
    print(f"\n--- Minnesota 2023-24 architecture (LAFI), within {nl}-team season ---")
    print(f"  Full LAFI percentile (vs all team-seasons): {w['lafi_pct']:.0f}")
    print(f"  Sharp LAFI percentile (vs all team-seasons): {w['sharp_lafi_pct']:.0f}")
    print(f"  Most-designed rank this season, Full LAFI:  {w['full_designed_rank']} of {nl}")
    print(f"  Most-designed rank this season, Sharp LAFI: {w['sharp_designed_rank']} of {nl}")
    print("\n  Most-designed teams in 2023-24 (Full LAFI, lowest = most designed):")
    top = lafi.sort_values("lafi_weighted_pct_sum").head(8)
    print(top[["team_abbreviation", "lafi_pct", "sharp_lafi_pct",
               "full_designed_rank"]]
          .to_string(index=False, float_format=lambda x: f"{x:.0f}"))


if __name__ == "__main__":
    run()
