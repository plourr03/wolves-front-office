"""Q7: Build age-24 feature profiles for Edwards and historical comp candidates.

Approach: pull career stats from the warehouse for Edwards (age 19-24) and
a candidate pool of historical guards who reached star tier by age 24
(Wade, Kobe, Mitchell, Booker, LaVine, Brown, Carter, Beal, McGrady,
Iverson, plus borderline candidates).

For each player, compute an "age-24 season profile" feature vector:
- Box-score rate stats (per 36)
- Shooting efficiency and shot mix
- Usage proxy (FGA + 0.44*FTA + TOV per minute)
- Career arc to that point (career year, prior all-star count)

Then compute similarity using normalized Euclidean distance.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import db


OUT_DIR = Path("outputs/tables/q7_star_comp")
OUT_DIR.mkdir(parents=True, exist_ok=True)


# Candidate pool: (player_id, name, age-24 season label)
# Player IDs come from the warehouse / NBA Stats. Some borderline candidates
# have data only from 1997+ (warehouse coverage).
CANDIDATES = {
    1630162: ("Anthony Edwards", "2025-26", 1),  # current
    # Combo / scoring guards in the comp pool
    2548: ("Dwyane Wade", "2005-06", 0),
    977: ("Kobe Bryant", "2002-03", 0),
    1495: ("Vince Carter", "2000-01", 0),
    947: ("Allen Iverson", "1999-00", 0),
    1503: ("Tracy McGrady", "2003-04", 0),
    202710: ("Jimmy Butler", "2013-14", 0),
    1626156: ("Bradley Beal", "2017-18", 0),
    1628378: ("Donovan Mitchell", "2020-21", 0),
    1626164: ("Devin Booker", "2020-21", 0),
    203897: ("Zach LaVine", "2019-20", 0),
    1627759: ("Jaylen Brown", "2020-21", 0),
    201942: ("DeMar DeRozan", "2013-14", 0),
    1717: ("Brandon Roy", "2008-09", 0),
    101108: ("Russell Westbrook", "2012-13", 0),
    202326: ("John Wall", "2014-15", 0),
}


def pull_player_career(player_id: int) -> pd.DataFrame:
    """Pull all per-game stats for a player across their career from the warehouse."""
    sql = """
        SELECT ps.season_year, g.season_type,
               COUNT(*) AS games,
               SUM(ps.minutes_played) AS mins,
               SUM(ps.pts) AS pts,
               SUM(ps.fgm) AS fgm,
               SUM(ps.fga) AS fga,
               SUM(ps.fg3m) AS fg3m,
               SUM(ps.fg3a) AS fg3a,
               SUM(ps.ftm) AS ftm,
               SUM(ps.fta) AS fta,
               SUM(ps.oreb) AS oreb,
               SUM(ps.dreb) AS dreb,
               SUM(ps.ast) AS ast,
               SUM(ps.tov) AS tov,
               SUM(ps.stl) AS stl,
               SUM(ps.blk) AS blk
        FROM nba_player_stats ps
        JOIN nba_games g ON g.game_id = ps.game_id AND g.team_id = ps.team_id
        WHERE ps.player_id = %s
          AND g.season_type IN ('Regular Season', 'Playoffs')
        GROUP BY ps.season_year, g.season_type
        ORDER BY ps.season_year, g.season_type
    """
    df = db.query(sql, (player_id,))
    if df.empty:
        return df
    # Coerce
    for c in ("games", "mins", "pts", "fgm", "fga", "fg3m", "fg3a",
              "ftm", "fta", "oreb", "dreb", "ast", "tov", "stl", "blk"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def aggregate_season_profile(career_df: pd.DataFrame, season_year: str) -> dict:
    """Aggregate one season into a single feature row (regular season only)."""
    sub = career_df[(career_df["season_year"] == season_year) &
                      (career_df["season_type"] == "Regular Season")]
    if sub.empty:
        return {}
    row = sub.iloc[0]
    mp = row["mins"]
    fga = row["fga"]
    fta = row["fta"]
    if mp == 0:
        return {}
    out = {
        "season_year": season_year,
        "games": row["games"],
        "mins": mp,
        "pts_per_36": 36 * row["pts"] / mp,
        "fga_per_36": 36 * fga / mp,
        "fg3a_per_36": 36 * row["fg3a"] / mp,
        "fta_per_36": 36 * fta / mp,
        "ast_per_36": 36 * row["ast"] / mp,
        "tov_per_36": 36 * row["tov"] / mp,
        "stl_per_36": 36 * row["stl"] / mp,
        "fg_pct": row["fgm"] / fga if fga else np.nan,
        "fg3_pct": row["fg3m"] / row["fg3a"] if row["fg3a"] else np.nan,
        "ft_pct": row["ftm"] / fta if fta else np.nan,
        "ts_pct": row["pts"] / (2 * (fga + 0.44 * fta)) if (fga + 0.44 * fta) else np.nan,
        "efg_pct": (row["fgm"] + 0.5 * row["fg3m"]) / fga if fga else np.nan,
        "3pa_rate": row["fg3a"] / fga if fga else np.nan,
        "ft_rate": fta / fga if fga else np.nan,
        "usage_proxy": (fga + 0.44 * fta + row["tov"]) / mp,
    }
    return out


def run():
    print("Q7: Building age-24 comp profiles for Edwards and candidates\n")
    rows = []
    for pid, (name, age24_season, _) in CANDIDATES.items():
        career = pull_player_career(pid)
        if career.empty:
            print(f"  {name}: NO DATA in warehouse")
            continue
        profile = aggregate_season_profile(career, age24_season)
        if not profile:
            print(f"  {name}: NO age-24 season ({age24_season}) data")
            continue
        profile["player"] = name
        profile["player_id"] = pid
        rows.append(profile)
        print(f"  {name} ({age24_season}): pts/36={profile['pts_per_36']:.1f}, "
              f"fg3a/36={profile['fg3a_per_36']:.1f}, ts={profile['ts_pct']:.3f}, "
              f"usage_proxy={profile['usage_proxy']:.3f}")

    profiles = pd.DataFrame(rows)
    profiles.to_csv(OUT_DIR / "age24_profiles.csv", index=False)
    print(f"\nSaved {len(profiles)} profiles to {OUT_DIR / 'age24_profiles.csv'}")
    return profiles


if __name__ == "__main__":
    run()
