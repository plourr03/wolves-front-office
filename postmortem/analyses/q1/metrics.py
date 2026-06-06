"""
Q1 metrics: aggregate team-game rows into team-season-type four-factors and
ratings. Computed from raw counts (so the season-level numbers are exactly
totals-divided-by-totals, not means-of-game-means).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# A possession ≈ FGA + 0.44 * FTA − OREB + TOV (standard Oliver formula).
# We have actual possessions in nba_team_advanced_stats already, so we prefer
# that and fall back to the formula only when computing on subsamples without
# the advanced join.


def aggregate_team_season(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """
    Aggregate a DataFrame of team-games into one row per group.

    Computes:
      games, wins, possessions, opp_possessions,
      ortg, drtg, net_rtg, pace,
      efg_pct, tov_pct, oreb_pct, ft_per_fga,
      opp_efg_pct, opp_tov_pct, dreb_pct, opp_ft_per_fga,
      three_pt_rate, opp_three_pt_rate
    """
    g = df.groupby(group_cols, dropna=False)

    out = pd.DataFrame({
        "games":           g.size(),
        "wins":            g["wl"].apply(lambda s: (s == "W").sum()),
        "possessions":     g["possessions"].sum(),
        "pts":             g["pts"].sum(),
        "opp_pts":         g["opp_pts"].sum(),
        "fgm":             g["fgm"].sum(),
        "fga":             g["fga"].sum(),
        "fg3m":            g["fg3m"].sum(),
        "fg3a":            g["fg3a"].sum(),
        "fta":             g["fta"].sum(),
        "oreb":            g["oreb"].sum(),
        "dreb":            g["dreb"].sum(),
        "tov":             g["tov"].sum(),
        "opp_fgm":         g["opp_fgm"].sum(),
        "opp_fga":         g["opp_fga"].sum(),
        "opp_fg3m":        g["opp_fg3m"].sum(),
        "opp_fg3a":        g["opp_fg3a"].sum(),
        "opp_fta":         g["opp_fta"].sum(),
        "opp_oreb":        g["opp_oreb"].sum(),
        "opp_dreb":        g["opp_dreb"].sum(),
        "opp_tov":         g["opp_tov"].sum(),
    }).reset_index()

    # ORtg / DRtg via raw totals. Possessions are symmetric per-game in our
    # pull (Oliver formula averaged across both teams), so the same total is
    # used as denominator on both sides.
    out["ortg"]    = 100.0 * out["pts"]     / out["possessions"]
    out["drtg"]    = 100.0 * out["opp_pts"] / out["possessions"]
    out["net_rtg"] = out["ortg"] - out["drtg"]
    out["pace"]    = out["possessions"] / out["games"]

    # Four factors (offense)
    out["efg_pct"]    = (out["fgm"] + 0.5 * out["fg3m"]) / out["fga"]
    # TOV% via Oliver definition: tov / (fga + 0.44*fta + tov). Possessions denominator.
    out["tov_pct"]    = out["tov"] / (out["fga"] + 0.44 * out["fta"] + out["tov"])
    out["oreb_pct"]   = out["oreb"] / (out["oreb"] + out["opp_dreb"])
    out["ft_per_fga"] = out["fta"] / out["fga"]

    # Four factors (defense)
    out["opp_efg_pct"]    = (out["opp_fgm"] + 0.5 * out["opp_fg3m"]) / out["opp_fga"]
    out["opp_tov_pct"]    = out["opp_tov"] / (out["opp_fga"] + 0.44 * out["opp_fta"] + out["opp_tov"])
    out["dreb_pct"]       = out["dreb"] / (out["dreb"] + out["opp_oreb"])
    out["opp_ft_per_fga"] = out["opp_fta"] / out["opp_fga"]

    # Three-point environment
    out["three_pt_rate"]     = out["fg3a"]     / out["fga"]
    out["opp_three_pt_rate"] = out["opp_fg3a"] / out["opp_fga"]
    out["three_pt_pct"]      = out["fg3m"]     / out["fg3a"]
    out["opp_three_pt_pct"]  = out["opp_fg3m"] / out["opp_fg3a"]

    return out


METRIC_COLS_OFFENSE = [
    "ortg", "efg_pct", "tov_pct", "oreb_pct", "ft_per_fga",
    "three_pt_rate", "three_pt_pct", "pace",
]
METRIC_COLS_DEFENSE = [
    "drtg", "opp_efg_pct", "opp_tov_pct", "dreb_pct", "opp_ft_per_fga",
    "opp_three_pt_rate", "opp_three_pt_pct",
]
METRIC_COLS_ALL = ["net_rtg"] + METRIC_COLS_OFFENSE + METRIC_COLS_DEFENSE


def bootstrap_team_metrics(
    df: pd.DataFrame,
    metric_cols: list[str] = METRIC_COLS_ALL,
    n_resamples: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Resample games (rows) of the given team-games DataFrame with replacement,
    recompute aggregate metrics, return a long DataFrame of (metric, lower, upper).

    The DataFrame should already be filtered to one team-season-type slice.
    """
    rng = np.random.default_rng(seed)
    n = len(df)
    if n == 0:
        return pd.DataFrame(columns=["metric", "lower", "upper"])

    samples = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        sub = df.iloc[idx]
        agg = aggregate_team_season(sub, group_cols=["team_abbreviation"])
        # one row
        samples.append(agg.iloc[0][metric_cols].values)

    arr = np.array(samples, dtype=float)  # shape (n_resamples, n_metrics)
    lower = np.nanpercentile(arr, 2.5, axis=0)
    upper = np.nanpercentile(arr, 97.5, axis=0)
    return pd.DataFrame({"metric": metric_cols, "lower": lower, "upper": upper})
