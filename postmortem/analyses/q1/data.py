"""
Q1 data layer.

Primary pull comes from nba_games (raw box scores) plus a self-join on the
opposing team in the same game. Possessions and ratings are computed via the
Dean Oliver formula so the analysis is self-contained and does not depend on
nba_team_advanced_stats being backfilled (which, as of 2026-05-14, is missing
for the 2025-26 playoffs).

Returns one row per (game_id, team_id) with both the team's box and the
opponent's box on the same row.
"""

from __future__ import annotations

import pandas as pd

from lib import db


SEASONS_RS_PO = list(range(2014, 2026))  # start years inclusive, 2014-15 .. 2025-26


_SQL = """
SELECT
    a.game_id,
    a.team_id,
    a.team_abbreviation,
    a.season_id,
    (a.season_id %% 10000)::int AS season_start_year,
    a.season_type,
    a.game_date,
    a.matchup,
    a.wl, a.plus_minus,
    a.pts, a.fgm, a.fga, a.fg3m, a.fg3a, a.ftm, a.fta,
    a.oreb, a.dreb, a.tov, a.ast, a.stl, a.blk,
    b.team_abbreviation AS opp_abbr,
    b.team_id           AS opp_team_id,
    b.pts  AS opp_pts,
    b.fgm  AS opp_fgm,
    b.fga  AS opp_fga,
    b.fg3m AS opp_fg3m,
    b.fg3a AS opp_fg3a,
    b.ftm  AS opp_ftm,
    b.fta  AS opp_fta,
    b.oreb AS opp_oreb,
    b.dreb AS opp_dreb,
    b.tov  AS opp_tov
FROM nba_games a
JOIN nba_games b
  ON a.game_id = b.game_id AND a.team_id <> b.team_id
WHERE a.season_type IN ('Regular Season','Playoffs')
  AND (a.season_id %% 10000) BETWEEN %(yr_lo)s AND %(yr_hi)s
ORDER BY a.game_date, a.game_id, a.team_abbreviation
"""


def pull_team_games(years: list[int] = SEASONS_RS_PO) -> pd.DataFrame:
    """Pull team-game rows (with opponent paired) for the given start-year range."""
    yr_lo, yr_hi = min(years), max(years)
    df = db.query(_SQL, {"yr_lo": yr_lo, "yr_hi": yr_hi})

    df["game_date"] = pd.to_datetime(df["game_date"])

    numeric_cols = [c for c in df.columns if c not in (
        "game_id", "team_abbreviation", "season_type", "wl",
        "matchup", "opp_abbr",
    )]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["season_label"] = df["season_start_year"].apply(
        lambda y: f"{int(y)}-{str(int(y) + 1)[-2:]}" if pd.notna(y) else None
    )

    # Possessions per Oliver formula. Use the symmetric average of own and opp
    # possessions to get a single agreed-upon number per team-game, matching
    # how NBA.com computes pace and ratings.
    own = df["fga"] + 0.44 * df["fta"] - df["oreb"] + df["tov"]
    opp = df["opp_fga"] + 0.44 * df["opp_fta"] - df["opp_oreb"] + df["opp_tov"]
    df["possessions"] = 0.5 * (own + opp)
    df["opp_possessions"] = df["possessions"]  # by construction, same number

    # Pace: possessions per 48 minutes. Box scores are full games, so this is
    # possessions / (minutes/48). For non-OT games, minutes = 240 = 48 min * 5.
    # We approximate by treating each game as 48 min (good for RS averaging);
    # OT games will pull pace down slightly, which is the conventional behavior.
    df["pace"] = df["possessions"]  # one-team-per-48 already; pace is just poss

    return df
