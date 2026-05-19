"""LAFI data layer.

One pull function per logical input the analysis needs. Each returns a
DataFrame at the natural grain (team-season, team-game, possession, or shot).

All functions take a list of season start years (e.g. [2014, 2015, ..., 2025]
for the 2014-15 through 2025-26 window). Season type defaults to both Regular
Season and Playoffs unless the analysis needs to restrict.

No caching at this layer. Pulls happen once per pipeline run, which is fine
given the warehouse is local. Downstream analytical stages cache their own
expensive computed outputs.

Reproducibility contract: same SQL + same warehouse state = same DataFrame.
No hidden state, no random sampling, no timestamps in the output.
"""
from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from lib import db
from analyses.q0a_lafi import config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _season_label_list(years: Iterable[int]) -> list[str]:
    return [config.season_label(y) for y in years]


def _season_type_filter(season_types: Optional[Iterable[str]]) -> tuple[str, list]:
    """Build a SQL IN clause and parameter list for season_type."""
    if season_types is None:
        season_types = config.SEASON_TYPES
    season_types = list(season_types)
    placeholders = ",".join(["%s"] * len(season_types))
    return f"({placeholders})", season_types


# ---------------------------------------------------------------------------
# Team-game and team-season game-level data
# ---------------------------------------------------------------------------


def load_team_games(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Team-game box scores with opponent paired and Oliver possessions computed.

    Returns one row per (game_id, team_id). Mirrors the pattern from
    analyses/q1/data.py so downstream code stays consistent.
    """
    yr_lo, yr_hi = min(years), max(years)
    st_in, st_params = _season_type_filter(season_types)
    sql = f"""
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
            b.team_id           AS opp_team_id,
            b.team_abbreviation AS opp_abbr,
            b.pts  AS opp_pts,
            b.fgm  AS opp_fgm,  b.fga  AS opp_fga,
            b.fg3m AS opp_fg3m, b.fg3a AS opp_fg3a,
            b.ftm  AS opp_ftm,  b.fta  AS opp_fta,
            b.oreb AS opp_oreb, b.dreb AS opp_dreb,
            b.tov  AS opp_tov
        FROM nba_games a
        JOIN nba_games b ON a.game_id = b.game_id AND a.team_id <> b.team_id
        WHERE a.season_type IN {st_in}
          AND (a.season_id %% 10000) BETWEEN %s AND %s
        ORDER BY a.game_date, a.game_id, a.team_abbreviation
    """
    df = db.query(sql, tuple(st_params + [yr_lo, yr_hi]))
    df["game_date"] = pd.to_datetime(df["game_date"])

    numeric_cols = [c for c in df.columns if c not in (
        "game_id", "team_abbreviation", "season_type", "wl", "matchup", "opp_abbr",
    )]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["season_label"] = df["season_start_year"].apply(config.season_label)
    own_poss = df["fga"] + 0.44 * df["fta"] - df["oreb"] + df["tov"]
    opp_poss = df["opp_fga"] + 0.44 * df["opp_fta"] - df["opp_oreb"] + df["opp_tov"]
    df["possessions"] = 0.5 * (own_poss + opp_poss)
    return df


def load_team_season_summary(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """One row per (team, season, season_type) with aggregate offensive and
    defensive ratings, pace, net rating, and games played.

    Uses nba_team_advanced_stats which has per-game ORtg, DRtg, possessions,
    aggregated up. Falls back to Oliver-formula from box scores for any
    game-team rows missing in advanced stats (typically 0 in recent seasons).
    """
    yr_lo, yr_hi = min(years), max(years)
    st_in, st_params = _season_type_filter(season_types)
    sql = f"""
        SELECT
            g.team_id,
            g.team_abbreviation,
            g.season_type,
            (g.season_id %% 10000)::int AS season_start_year,
            COUNT(DISTINCT g.game_id) AS gp,
            SUM(tas.possessions) AS poss_total,
            SUM(tas.offensive_rating * tas.possessions) / NULLIF(SUM(tas.possessions),0)
                AS off_rating,
            SUM(tas.defensive_rating * tas.possessions) / NULLIF(SUM(tas.possessions),0)
                AS def_rating,
            SUM(tas.net_rating * tas.possessions) / NULLIF(SUM(tas.possessions),0)
                AS net_rating,
            AVG(tas.pace)  AS pace,
            SUM(g.pts) AS pts_for,
            SUM(g.fgm) AS fgm,  SUM(g.fga) AS fga,
            SUM(g.fg3a) AS fg3a, SUM(g.fta) AS fta,
            SUM(g.oreb) AS oreb, SUM(g.dreb) AS dreb,
            SUM(g.tov) AS tov,  SUM(g.ast) AS ast
        FROM nba_games g
        LEFT JOIN nba_team_advanced_stats tas
            ON tas.game_id = g.game_id AND tas.team_id = g.team_id
        WHERE g.season_type IN {st_in}
          AND (g.season_id %% 10000) BETWEEN %s AND %s
        GROUP BY g.team_id, g.team_abbreviation, g.season_type, season_start_year
        ORDER BY season_start_year, g.team_abbreviation, g.season_type
    """
    df = db.query(sql, tuple(st_params + [yr_lo, yr_hi]))
    for c in df.columns:
        if c not in ("team_abbreviation", "season_type"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["season_label"] = df["season_start_year"].apply(config.season_label)
    return df


# ---------------------------------------------------------------------------
# Tracking
# ---------------------------------------------------------------------------


# Map measure_type to the set of columns it populates.
# This is what determines which fields are non-null per row.
TRACKING_MEASURE_TYPES = (
    "Possessions", "Drives", "Passing", "CatchShoot", "PullUpShot",
    "SpeedDistance", "ElbowTouch", "PostTouch", "PaintTouch", "Defense", "Rebounding",
)


def load_team_tracking_season(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
    measure_types: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Per-(team, season, season_type, measure_type) tracking aggregates.

    Returns the wide table. Filter by measure_type after loading or pass a
    short list of measures to restrict the pull.
    """
    season_labels = _season_label_list(years)
    st_in, st_params = _season_type_filter(season_types)
    sl_in = ",".join(["%s"] * len(season_labels))
    measure_clause = ""
    measure_params: list = []
    if measure_types:
        mt_list = list(measure_types)
        measure_clause = f"AND measure_type IN ({','.join(['%s']*len(mt_list))})"
        measure_params = mt_list
    sql = f"""
        SELECT *
        FROM nba_team_tracking_season
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
          {measure_clause}
    """
    params = tuple(season_labels + st_params + measure_params)
    df = db.query(sql, params)
    df["season_start_year"] = df["season_year"].apply(config.season_start_year_from_label)
    return df


def load_player_tracking_season(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
    measure_types: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Per-(player, season, season_type, measure_type) tracking aggregates.

    Wide table. Filter by measure_type when only one slice is needed.
    """
    season_labels = _season_label_list(years)
    st_in, st_params = _season_type_filter(season_types)
    sl_in = ",".join(["%s"] * len(season_labels))
    measure_clause = ""
    measure_params: list = []
    if measure_types:
        mt_list = list(measure_types)
        measure_clause = f"AND measure_type IN ({','.join(['%s']*len(mt_list))})"
        measure_params = mt_list
    sql = f"""
        SELECT *
        FROM nba_player_tracking_season
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
          {measure_clause}
    """
    df = db.query(sql, tuple(season_labels + st_params + measure_params))
    df["season_start_year"] = df["season_year"].apply(config.season_start_year_from_label)
    return df


def load_team_tracking_game(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Per-game team tracking. Joined to nba_games for date and season context.

    Tracking-per-game has touches, passes, contested vs uncontested FGA splits,
    rebound chances, secondary assists. Useful for any analysis that needs
    these features at the game level.
    """
    yr_lo, yr_hi = min(years), max(years)
    st_in, st_params = _season_type_filter(season_types)
    sql = f"""
        SELECT
            t.*,
            g.game_date,
            g.season_type,
            (g.season_id %% 10000)::int AS season_start_year,
            g.team_abbreviation
        FROM nba_team_tracking_game t
        JOIN nba_games g
            ON g.game_id = t.game_id AND g.team_id = t.team_id
        WHERE g.season_type IN {st_in}
          AND (g.season_id %% 10000) BETWEEN %s AND %s
    """
    df = db.query(sql, tuple(st_params + [yr_lo, yr_hi]))
    df["game_date"] = pd.to_datetime(df["game_date"])
    return df


# ---------------------------------------------------------------------------
# Synergy
# ---------------------------------------------------------------------------


SYNERGY_PLAY_TYPES = (
    "Cut", "Handoff", "Isolation", "Misc", "OffRebound",
    "OffScreen", "Postup", "PRBallHandler", "PRRollMan",
    "Spotup", "Transition",
)


def load_synergy_team(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
    type_grouping: str = "Offensive",
) -> pd.DataFrame:
    """Synergy team play-type table.

    One row per (team, season, season_type, play_type). poss is total
    possessions for that play type, poss_pct is the percentage of team
    possessions, ppp is points per possession.

    type_grouping defaults to 'Offensive'. Pass 'Defensive' for opponent-side.
    """
    season_labels = _season_label_list(years)
    st_in, st_params = _season_type_filter(season_types)
    sl_in = ",".join(["%s"] * len(season_labels))
    sql = f"""
        SELECT
            season_year, season_type,
            team_id, team_abbreviation, team_name,
            play_type, type_grouping,
            gp, poss, poss_pct, ppp, fg_pct, efg_pct,
            tov_poss_pct, sf_poss_pct, score_poss_pct,
            pts, fgm, fga
        FROM nba_synergy_team_play_types
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
          AND type_grouping = %s
    """
    params = tuple(season_labels + st_params + [type_grouping])
    df = db.query(sql, params)
    df["season_start_year"] = df["season_year"].apply(config.season_start_year_from_label)
    for c in ("gp", "poss", "poss_pct", "ppp", "fg_pct", "efg_pct",
              "tov_poss_pct", "sf_poss_pct", "score_poss_pct",
              "pts", "fgm", "fga"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Shot tables
# ---------------------------------------------------------------------------


def load_team_pt_shot_season(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Team pull-up / catch-and-shoot / 2 vs 3 frequency aggregates per season."""
    season_labels = _season_label_list(years)
    st_in, st_params = _season_type_filter(season_types)
    sl_in = ",".join(["%s"] * len(season_labels))
    sql = f"""
        SELECT *
        FROM nba_team_pt_shot_season
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
    """
    df = db.query(sql, tuple(season_labels + st_params))
    df["season_start_year"] = df["season_year"].apply(config.season_start_year_from_label)
    return df


def load_team_shot_locations_season(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Team shot-zone frequencies and FG% by zone, season aggregates."""
    season_labels = _season_label_list(years)
    st_in, st_params = _season_type_filter(season_types)
    sl_in = ",".join(["%s"] * len(season_labels))
    sql = f"""
        SELECT *
        FROM nba_team_shot_locations_season
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
    """
    df = db.query(sql, tuple(season_labels + st_params))
    df["season_start_year"] = df["season_year"].apply(config.season_start_year_from_label)
    return df


def load_shot_chart(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
    team_id: Optional[int] = None,
) -> pd.DataFrame:
    """Per-shot detail. Filter by team_id to keep result size manageable,
    otherwise this can be 2M+ rows.

    Use this for shot-quality model building. For team-season aggregates,
    prefer load_team_shot_locations_season.
    """
    season_labels = _season_label_list(years)
    st_in, st_params = _season_type_filter(season_types)
    sl_in = ",".join(["%s"] * len(season_labels))
    team_clause = "AND team_id = %s" if team_id is not None else ""
    team_params = [team_id] if team_id is not None else []
    sql = f"""
        SELECT
            game_id, game_event_id, player_id, team_id,
            period, minutes_remaining, seconds_remaining,
            action_type, shot_type, shot_zone_basic, shot_zone_area, shot_zone_range,
            shot_distance, loc_x, loc_y,
            shot_attempted_flag, shot_made_flag,
            game_date, season_year, season_type
        FROM nba_shot_chart_detail
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
          {team_clause}
    """
    df = db.query(sql, tuple(season_labels + st_params + team_params))
    df["season_start_year"] = df["season_year"].apply(config.season_start_year_from_label)
    return df


# ---------------------------------------------------------------------------
# Season universe diagnostic
# ---------------------------------------------------------------------------


def season_universe(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Report what data is available for each season in the window.

    Returns one row per (season_start_year, season_type) with counts of teams
    present in each input table. The component computations later will filter
    to seasons where all required inputs are present.
    """
    season_labels = _season_label_list(years)
    st_in, st_params = _season_type_filter(season_types)
    sl_in = ",".join(["%s"] * len(season_labels))

    # Game-level coverage from nba_games.
    sql_games = f"""
        SELECT (season_id %% 10000)::int AS season_start_year, season_type,
               COUNT(DISTINCT team_id) AS teams,
               COUNT(DISTINCT game_id) AS games
        FROM nba_games
        WHERE season_type IN {st_in}
          AND (season_id %% 10000) BETWEEN %s AND %s
        GROUP BY 1, 2
    """
    games = db.query(sql_games, tuple(st_params + [min(years), max(years)]))

    # Tracking season aggregates: count distinct teams with at least one row
    # at any measure_type per season.
    sql_track_season = f"""
        SELECT season_year, season_type,
               COUNT(DISTINCT team_id) AS tracking_season_teams
        FROM nba_team_tracking_season
        WHERE season_year IN ({sl_in}) AND season_type IN {st_in}
        GROUP BY 1, 2
    """
    track_season = db.query(sql_track_season, tuple(season_labels + st_params))
    track_season["season_start_year"] = track_season["season_year"].apply(config.season_start_year_from_label)

    # Tracking per-game.
    sql_track_game = f"""
        SELECT (g.season_id %% 10000)::int AS season_start_year, g.season_type,
               COUNT(DISTINCT t.team_id) AS tracking_game_teams,
               COUNT(DISTINCT t.game_id) AS tracking_games
        FROM nba_team_tracking_game t
        JOIN nba_games g ON g.game_id = t.game_id AND g.team_id = t.team_id
        WHERE g.season_type IN {st_in}
          AND (g.season_id %% 10000) BETWEEN %s AND %s
        GROUP BY 1, 2
    """
    track_game = db.query(sql_track_game, tuple(st_params + [min(years), max(years)]))

    # Synergy.
    sql_synergy = f"""
        SELECT season_year, season_type,
               COUNT(DISTINCT team_id) AS synergy_teams,
               COUNT(DISTINCT play_type) AS synergy_play_types
        FROM nba_synergy_team_play_types
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
          AND type_grouping = 'Offensive'
        GROUP BY 1, 2
    """
    synergy = db.query(sql_synergy, tuple(season_labels + st_params))
    synergy["season_start_year"] = synergy["season_year"].apply(config.season_start_year_from_label)

    # Shot chart.
    sql_shot = f"""
        SELECT season_year, season_type,
               COUNT(DISTINCT team_id) AS shot_chart_teams,
               COUNT(DISTINCT game_id) AS shot_chart_games
        FROM nba_shot_chart_detail
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
        GROUP BY 1, 2
    """
    shot = db.query(sql_shot, tuple(season_labels + st_params))
    shot["season_start_year"] = shot["season_year"].apply(config.season_start_year_from_label)

    # Pt shot season.
    sql_ptshot = f"""
        SELECT season_year, season_type, COUNT(DISTINCT team_id) AS pt_shot_teams
        FROM nba_team_pt_shot_season
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
        GROUP BY 1, 2
    """
    ptshot = db.query(sql_ptshot, tuple(season_labels + st_params))
    ptshot["season_start_year"] = ptshot["season_year"].apply(config.season_start_year_from_label)

    # Shot locations season.
    sql_shotloc = f"""
        SELECT season_year, season_type, COUNT(DISTINCT team_id) AS shotloc_teams
        FROM nba_team_shot_locations_season
        WHERE season_year IN ({sl_in})
          AND season_type IN {st_in}
        GROUP BY 1, 2
    """
    shotloc = db.query(sql_shotloc, tuple(season_labels + st_params))
    shotloc["season_start_year"] = shotloc["season_year"].apply(config.season_start_year_from_label)

    # Merge everything on (season_start_year, season_type).
    out = games[["season_start_year", "season_type", "teams", "games"]]
    for df, cols in [
        (track_season, ["tracking_season_teams"]),
        (track_game,   ["tracking_game_teams", "tracking_games"]),
        (synergy,      ["synergy_teams", "synergy_play_types"]),
        (shot,         ["shot_chart_teams", "shot_chart_games"]),
        (ptshot,       ["pt_shot_teams"]),
        (shotloc,      ["shotloc_teams"]),
    ]:
        keep = ["season_start_year", "season_type"] + cols
        out = out.merge(df[keep], on=["season_start_year", "season_type"], how="left")
    out = out.sort_values(["season_start_year", "season_type"]).reset_index(drop=True)
    out["season_label"] = out["season_start_year"].apply(config.season_label)
    return out
