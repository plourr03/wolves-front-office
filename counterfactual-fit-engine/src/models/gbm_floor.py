"""F4 scaffolding: the GBM floor (spec 8.4 architecture 1, mandatory
first). Gradient-boosted trees on engineered lineup features; the baseline
the set-attention primary must beat at G3, and if the floor wins, the
floor ships.

Feature engineering from ten K-dim player vectors per row (five offense,
five defense):
  per side, per skill dim: sum, mean, max, min          -> 4*K each side
  offense-minus-defense contrasts of the per-dim sums   -> K
  pairwise redundancy: mean and min pairwise cosine similarity within the
  offense five over the creation subspace (config: which dims), the
  pre-registered descriptive redundancy illustration     -> 2
  context: home_share, rest_delta, end_year (season env) -> 3

Estimator: lightgbm if importable (config layer2.gbm), else sklearn
HistGradientBoostingRegressor -- same API either way, chosen at runtime,
recorded in the returned meta.

NO real Layer 2 fit runs until F3 vectors exist (directive 2026-07-03
item 4); tests exercise the harness on synthetic vectors only. The
temporal-holdout API (train <= s-1, test s) is the G3 protocol shape.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

CREATION_DIMS_DEFAULT: tuple[int, ...] = (0, 1)  # placeholder until F3 labels


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(a @ b / (na * nb))


def engineer_row(off_vecs: np.ndarray, def_vecs: np.ndarray,
                 home_share: float, rest_delta: float, end_year: int,
                 creation_dims: tuple[int, ...] = CREATION_DIMS_DEFAULT
                 ) -> np.ndarray:
    """off_vecs/def_vecs: (5, K). Returns the engineered feature vector."""
    feats = []
    for side in (off_vecs, def_vecs):
        feats.extend(side.sum(axis=0))
        feats.extend(side.mean(axis=0))
        feats.extend(side.max(axis=0))
        feats.extend(side.min(axis=0))
    feats.extend(off_vecs.sum(axis=0) - def_vecs.sum(axis=0))
    sub = off_vecs[:, list(creation_dims)]
    cos = [_cosine(sub[i], sub[j]) for i in range(5) for j in range(i + 1, 5)]
    feats.extend([float(np.mean(cos)), float(np.min(cos))])
    feats.extend([home_share, rest_delta, float(end_year)])
    return np.asarray(feats, dtype=np.float64)


def engineer_matrix(rows: pd.DataFrame, vectors: dict[int, np.ndarray],
                    creation_dims: tuple[int, ...] = CREATION_DIMS_DEFAULT
                    ) -> np.ndarray:
    """rows: lineup_obs-shaped frame with off_lineup/def_lineup id strings.
    vectors: player_id -> (K,) skill vector (already leakage-safe and aged
    by the caller via FeatureService; this module never touches seasons)."""
    out = []
    for r in rows.itertuples():
        off = np.stack([vectors[int(p)] for p in r.off_lineup.split(",")])
        dfv = np.stack([vectors[int(p)] for p in r.def_lineup.split(",")])
        out.append(engineer_row(off, dfv, r.home_share, r.rest_delta,
                                r.end_year, creation_dims))
    return np.stack(out)


def make_estimator(params: dict | None = None):
    params = params or {}
    try:
        from lightgbm import LGBMRegressor
        est = LGBMRegressor(
            n_estimators=params.get("n_estimators", 500),
            learning_rate=params.get("learning_rate", 0.05),
            num_leaves=params.get("num_leaves", 63),
            random_state=params.get("seed", 20260702), verbose=-1)
        backend = "lightgbm"
    except ImportError:
        from sklearn.ensemble import HistGradientBoostingRegressor
        est = HistGradientBoostingRegressor(
            max_iter=params.get("n_estimators", 500),
            learning_rate=params.get("learning_rate", 0.05),
            random_state=params.get("seed", 20260702))
        backend = "sklearn_hgb"
    return est, backend


def temporal_fit_eval(rows: pd.DataFrame, vectors: dict[int, np.ndarray],
                      test_year: int, params: dict | None = None) -> dict:
    """G3-shaped protocol: train on end_year <= test_year-1, evaluate on
    test_year, possession-weighted RMSE vs the additive baseline (linear
    fit on the off-minus-def sum contrasts only)."""
    train = rows[rows.end_year < test_year]
    test = rows[rows.end_year == test_year]
    if train.empty or test.empty:
        raise ValueError("temporal split produced an empty side")
    Xtr = engineer_matrix(train, vectors)
    Xte = engineer_matrix(test, vectors)
    ytr, yte = train.pts_per100.to_numpy(), test.pts_per100.to_numpy()
    wtr, wte = train.poss.to_numpy(), test.poss.to_numpy()

    est, backend = make_estimator(params)
    est.fit(Xtr, ytr, sample_weight=wtr)
    pred = est.predict(Xte)
    rmse = float(np.sqrt(np.average((yte - pred) ** 2, weights=wte)))

    # additive baseline: weighted linear model on the K contrast features
    from sklearn.linear_model import Ridge
    K = (Xtr.shape[1] - 5) // 9
    contrast = slice(8 * K, 9 * K)
    base = Ridge(alpha=1.0).fit(Xtr[:, contrast], ytr, sample_weight=wtr)
    bpred = base.predict(Xte[:, contrast])
    rmse_base = float(np.sqrt(np.average((yte - bpred) ** 2, weights=wte)))

    return {"backend": backend, "test_year": test_year,
            "n_train": len(train), "n_test": len(test),
            "rmse_gbm": rmse, "rmse_additive": rmse_base,
            "beats_additive": rmse < rmse_base}
