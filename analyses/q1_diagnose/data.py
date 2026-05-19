"""Q1 data layer.

Pulls team-game and team-season aggregates from the warehouse for Wolves
and league comparisons. Uses Oliver-formula possessions when advanced-stats
possessions are missing.
"""
from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from lib import db
from analyses.q1_diagnose import config


# ---------------------------------------------------------------------------
# Per-game team data with opponent paired
# ---------------------------------------------------------------------------


_TEAM_GAME_SQL = """
SELECT
    a.game_id,
    a.team_id,
    a.team_abbreviation,
    (a.season_id %% 10000)::int AS season_start_year,
    a.season_type,
    a.game_date,
    a.matchup,
    a.wl,
    a.plus_minus,
    a.pts, a.fgm, a.fga, a.fg3m, a.fg3a, a.ftm, a.fta,
    a.oreb, a.dreb, a.tov, a.ast,
    b.team_id           AS opp_team_id,
    b.team_abbreviation AS opp_abbr,
    b.pts  AS opp_pts,
    b.fgm  AS opp_fgm,  b.fga  AS opp_fga,
    b.fg3m AS opp_fg3m, b.fg3a AS opp_fg3a,
    b.ftm  AS opp_ftm,  b.fta  AS opp_fta,
    b.oreb AS opp_oreb, b.dreb AS opp_dreb,
    b.tov  AS opp_tov,
    tas.offensive_rating, tas.defensive_rating, tas.net_rating,
    tas.pace, tas.possessions
FROM nba_games a
JOIN nba_games b ON a.game_id = b.game_id AND a.team_id <> b.team_id
LEFT JOIN nba_team_advanced_stats tas
    ON tas.game_id = a.game_id AND tas.team_id = a.team_id
WHERE a.season_type IN ('Regular Season','Playoffs')
  AND (a.season_id %% 10000) BETWEEN %s AND %s
ORDER BY a.game_date, a.game_id, a.team_abbreviation
"""


def load_team_games(year_lo: int = 2014, year_hi: int = 2025) -> pd.DataFrame:
    """Pull team-game rows for the year range with opponent paired and per-game
    advanced ratings attached where available.
    """
    df = db.query(_TEAM_GAME_SQL, (year_lo, year_hi))
    df["game_date"] = pd.to_datetime(df["game_date"])
    numeric_cols = [c for c in df.columns if c not in (
        "game_id", "team_abbreviation", "season_type", "wl", "matchup", "opp_abbr",
    )]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["season_label"] = df["season_start_year"].apply(config.season_label)

    # Oliver formula possessions (use as fallback when advanced-stats is missing).
    own_poss = df["fga"] + 0.44 * df["fta"] - df["oreb"] + df["tov"]
    opp_poss = df["opp_fga"] + 0.44 * df["opp_fta"] - df["opp_oreb"] + df["opp_tov"]
    df["oliver_possessions"] = 0.5 * (own_poss + opp_poss)
    df["possessions_eff"] = df["possessions"].where(df["possessions"].notna(),
                                                     df["oliver_possessions"])
    return df


def filter_to_team_and_seasons(
    games: pd.DataFrame,
    team_id: int,
    years: Iterable[int],
    season_type: Optional[str] = None,
) -> pd.DataFrame:
    out = games[(games["team_id"] == team_id) & (games["season_start_year"].isin(years))]
    if season_type:
        out = out[out["season_type"] == season_type]
    return out


def playoff_team_seasons(games: pd.DataFrame, year: int) -> list[int]:
    """List team_ids that made the playoffs in a given season_start_year."""
    return sorted(games[(games["season_start_year"] == year)
                        & (games["season_type"] == "Playoffs")]["team_id"].unique().tolist())
