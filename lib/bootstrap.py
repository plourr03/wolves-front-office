"""
Bootstrap utilities for confidence intervals.

Project convention (per CLAUDE.md): every team or player metric reported with a
CI, default 1000+ resamples, percentile method unless otherwise noted.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def bootstrap_ci(
    values: np.ndarray | pd.Series,
    statistic=np.mean,
    n_resamples: int = 1000,
    ci: float = 0.95,
    seed: int | None = 42,
) -> tuple[float, float, float]:
    """
    Bootstrap a statistic and return (point_estimate, lower, upper) at the
    requested CI level. Resamples with replacement, percentile method.
    """
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return (np.nan, np.nan, np.nan)
    point = float(statistic(arr))
    idx = rng.integers(0, len(arr), size=(n_resamples, len(arr)))
    samples = arr[idx]
    stats = np.array([statistic(s) for s in samples])
    alpha = (1.0 - ci) / 2.0
    lower = float(np.quantile(stats, alpha))
    upper = float(np.quantile(stats, 1.0 - alpha))
    return point, lower, upper


def bootstrap_weighted_mean(
    values: np.ndarray | pd.Series,
    weights: np.ndarray | pd.Series,
    n_resamples: int = 1000,
    ci: float = 0.95,
    seed: int | None = 42,
) -> tuple[float, float, float]:
    """
    Bootstrap a weighted mean. Resamples rows together (values and weights
    paired). Useful when each row represents a game and weights are possessions.
    """
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    mask = ~(np.isnan(v) | np.isnan(w))
    v, w = v[mask], w[mask]
    if len(v) == 0:
        return (np.nan, np.nan, np.nan)
    point = float(np.sum(v * w) / np.sum(w))
    idx = rng.integers(0, len(v), size=(n_resamples, len(v)))
    stats = np.array(
        [np.sum(v[i] * w[i]) / np.sum(w[i]) if np.sum(w[i]) > 0 else np.nan for i in idx]
    )
    alpha = (1.0 - ci) / 2.0
    lower = float(np.nanquantile(stats, alpha))
    upper = float(np.nanquantile(stats, 1.0 - alpha))
    return point, lower, upper
