"""Q2 analysis: load cached stints, aggregate, build comparison tables.

Consumes parquet stint caches written by `batch.py` and produces:

- Per-lineup season totals (gt-filtered + raw)
- Wolves lineup leaderboards (RS and PO, 2024-25 and 2025-26)
- League-wide playoff lineup baselines (for percentile placement)
- Wolves 2024-25 vs 2025-26 lineup-grain comparison (matched personnel)
- Gobert-at-5 vs Naz-at-5 with Category B framing
- Individual on/off (raw) with bootstrap CIs
- Player-pair WOWY for the core rotation

All comparisons include bootstrap CIs, opponent context where relevant, and
flag confounds explicitly.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

from lib import db, lineup_aggregation as agg
from analyses.q2_localize import config


# ---------------------------------------------------------------------------
# Player + game metadata
# ---------------------------------------------------------------------------


def load_player_names(player_ids: Iterable[int]) -> dict[int, str]:
    """Return id -> short display name for the given player_ids.

    Uses nba_player_stats for the most recent observation per id (which is
    canonical) and falls back to the raw player_name string from PBP when
    not present in the stats table.
    """
    ids = [int(p) for p in player_ids if p]
    if not ids:
        return {}
    placeholders = ",".join(["%s"] * len(ids))
    sql = f"""
        SELECT DISTINCT ON (player_id) player_id, player_name
        FROM nba_player_stats
        WHERE player_id IN ({placeholders})
        ORDER BY player_id, game_date DESC
    """
    df = db.query(sql, tuple(ids))
    return {int(r.player_id): str(r.player_name) for r in df.itertuples()}


def lineup_label(lineup_id: str, name_lookup: dict[int, str]) -> str:
    """Render a canonical lineup_id as a human-readable name string."""
    pids = [int(p) for p in lineup_id.split(",")]
    parts = []
    for pid in pids:
        full = name_lookup.get(pid, f"#{pid}")
        # Use last name only for brevity; if first initial is needed, callers
        # can extend.
        parts.append(_short_name(full))
    return " | ".join(sorted(parts))


def _short_name(full: str) -> str:
    """Last-name short form; keep DiVincenzo, McDaniels, etc. intact."""
    full = full.strip()
    if "," in full:
        last = full.split(",")[0].strip()
    else:
        toks = full.split()
        last = toks[-1] if toks else full
    return last


def load_game_metadata(season_year: int, season_type: str | None = None) -> pd.DataFrame:
    """Return per-game metadata: game_id, game_date, team_id, team_abbreviation,
    opp_team_id, opp_abbr, plus_minus, pts, opp_pts, season_type.
    """
    where = ["(season_id %% 10000) = %s"]
    params = [season_year]
    if season_type:
        where.append("season_type = %s")
        params.append(season_type)
    sql = f"""
        SELECT a.game_id, a.game_date, a.team_id, a.team_abbreviation,
               b.team_id AS opp_team_id, b.team_abbreviation AS opp_abbr,
               a.season_type, a.plus_minus, a.pts, b.pts AS opp_pts
        FROM nba_games a
        JOIN nba_games b ON a.game_id = b.game_id AND a.team_id <> b.team_id
        WHERE {' AND '.join(where)}
        ORDER BY a.game_date, a.game_id
    """
    df = db.query(sql, tuple(params))
    df["game_date"] = pd.to_datetime(df["game_date"])
    return df


def load_team_advanced(season_year: int, season_type: str | None = None,
                        team_ids: Iterable[int] | None = None) -> pd.DataFrame:
    """Per-team RS or PO regular-season summary for opponent strength.

    Returns mean offensive and defensive rating per team_id for the
    requested season slice. For opponent strength annotation, the natural
    pairing is "this team's RS offensive rating vs whoever they faced in
    the PO."
    """
    where = ["(season_id %% 10000) = %s"]
    params = [season_year]
    if season_type:
        where.append("season_type = %s")
        params.append(season_type)
    if team_ids is not None:
        ids = list(team_ids)
        if ids:
            placeholders = ",".join(["%s"] * len(ids))
            where.append(f"team_id IN ({placeholders})")
            params.extend(ids)
    sql = f"""
        SELECT team_id,
               AVG(offensive_rating) AS off_rtg,
               AVG(defensive_rating) AS def_rtg,
               AVG(net_rating) AS net_rtg,
               COUNT(*) AS n_games
        FROM nba_team_advanced_stats
        WHERE {' AND '.join(where)}
        GROUP BY team_id
    """
    return db.query(sql, tuple(params))


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------


def split_stints_by_season_type(stints: pd.DataFrame,
                                  season_year: int) -> dict[str, pd.DataFrame]:
    """Split a stint set by game season_type using nba_games as lookup."""
    if stints.empty:
        return {"Regular Season": stints, "Playoffs": stints}
    game_ids = sorted(stints["game_id"].unique())
    placeholders = ",".join(["%s"] * len(game_ids))
    meta = db.query(
        f"SELECT DISTINCT game_id, season_type FROM nba_games WHERE game_id IN ({placeholders})",
        tuple(game_ids),
    )
    season_map = dict(zip(meta["game_id"], meta["season_type"]))
    stints = stints.copy()
    stints["season_type"] = stints["game_id"].map(season_map)
    return {st: stints[stints["season_type"] == st].copy()
            for st in stints["season_type"].dropna().unique()}


def aggregate_for_team(stints_subset: pd.DataFrame, team_id: int,
                        season_year: int, season_type: str,
                        gt_filter: bool = True) -> pd.DataFrame:
    """Filter stints to one team and run aggregation."""
    sub = stints_subset[stints_subset["team_id"] == team_id]
    if sub.empty:
        return pd.DataFrame()
    return agg.aggregate_lineup_totals(sub, season_year, season_type, gt_filter)


def aggregate_all_teams(stints_subset: pd.DataFrame,
                         season_year: int, season_type: str,
                         gt_filter: bool = True) -> pd.DataFrame:
    """Aggregate per-(team, lineup) without filtering to one team."""
    if stints_subset.empty:
        return pd.DataFrame()
    return agg.aggregate_lineup_totals(stints_subset, season_year, season_type, gt_filter)


# ---------------------------------------------------------------------------
# Bootstrap helpers for stint-grain metrics
# ---------------------------------------------------------------------------


def bootstrap_lineup_metric(lineup_stints: pd.DataFrame, metric_fn,
                              n_resamples: int = None, seed: int = None) -> dict:
    """Bootstrap a metric on a lineup's stint records.

    Resamples stints with replacement; each resample recomputes the metric
    via metric_fn(stints_subset). Returns point + CI.
    """
    n_resamples = n_resamples or config.BOOTSTRAP_N
    seed = seed or config.BOOTSTRAP_SEED
    rng = np.random.default_rng(seed)
    n = len(lineup_stints)
    if n < 3:
        try:
            point = metric_fn(lineup_stints)
        except Exception:
            point = np.nan
        return {"point": point if not (isinstance(point, float) and np.isnan(point)) else np.nan,
                "ci_lo": np.nan, "ci_hi": np.nan, "n": n}
    try:
        point = metric_fn(lineup_stints)
    except Exception:
        point = np.nan
    samples = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        try:
            v = metric_fn(lineup_stints.iloc[idx])
        except Exception:
            continue
        if not np.isnan(v):
            samples.append(v)
    if len(samples) < 5:
        return {"point": float(point) if not np.isnan(point) else np.nan,
                "ci_lo": np.nan, "ci_hi": np.nan, "n": n}
    samples = np.array(samples)
    lo, hi = np.quantile(samples, [(1 - config.CI_LEVEL) / 2, 1 - (1 - config.CI_LEVEL) / 2])
    return {"point": float(point), "ci_lo": float(lo), "ci_hi": float(hi), "n": n}


def m_net_rating(stints: pd.DataFrame) -> float:
    poss_off = stints["possessions_off"].sum()
    poss_def = stints["possessions_def"].sum()
    if poss_off == 0 or poss_def == 0:
        return float("nan")
    return 100 * stints["points_for"].sum() / poss_off - 100 * stints["points_against"].sum() / poss_def


def m_off_rating(stints: pd.DataFrame) -> float:
    poss = stints["possessions_off"].sum()
    return 100 * stints["points_for"].sum() / poss if poss else float("nan")


def m_def_rating(stints: pd.DataFrame) -> float:
    poss = stints["possessions_def"].sum()
    return 100 * stints["points_against"].sum() / poss if poss else float("nan")


def m_off_3pa_rate(stints: pd.DataFrame) -> float:
    fga = stints["fga_off"].sum()
    return stints["fg3a_off"].sum() / fga if fga else float("nan")


def m_off_efg(stints: pd.DataFrame) -> float:
    fga = stints["fga_off"].sum()
    if not fga:
        return float("nan")
    return (stints["fgm_off"].sum() + 0.5 * stints["fg3m_off"].sum()) / fga


def m_fg3a_per_100(stints: pd.DataFrame) -> float:
    poss = stints["possessions_off"].sum()
    return 100 * stints["fg3a_off"].sum() / poss if poss else float("nan")


# ---------------------------------------------------------------------------
# Lineup-pair WOWY ("with or without you")
# ---------------------------------------------------------------------------


def lineup_contains(lineup_id: str, player_ids: Iterable[int]) -> bool:
    s = set(int(p) for p in lineup_id.split(","))
    return all(int(p) in s for p in player_ids)


def player_in_lineup(lineup_id: str, player_id: int) -> bool:
    return str(int(player_id)) in lineup_id.split(",")
