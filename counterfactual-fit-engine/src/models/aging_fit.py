"""A2: aging-curve fits for fitengine's OWN skill dimensions.

Model C (pick2033) supplies the NET-impact aging delta used in the Layer
1a prior. Layer 2's leakage rule ages K-dimensional SKILL VECTORS, and a
single net curve cannot claim per-dimension shape (rim pressure ages
differently from connective passing). A2 is the code that fits
Model-C-STYLE delta curves per skill dimension, same basis, same
archetype hierarchy, once skill vectors exist.

DISCIPLINE (directive 2026-07-03 item 3): this module is WRITTEN and
smoke-tested on synthetic data only. fit_from_skill_vectors refuses to
run until outputs/skill_vectors exists (F3 proper). No real fit happened
overnight.

Method (deliberately lighter than Model C's MCMC; these curves feed
feature aging, not a published posterior):
  delta_z[p, dim, t] = g_arch(age[p, t]) + eps      per dimension
  g = natural cubic spline (pick2033 KNOTS), fit by weighted ridge with
  a small roughness penalty; per-archetype fit with pooled-global
  shrinkage (arch curve = blend of arch fit and global fit weighted by
  arch sample size). Player random effects are approximated by
  one-step demeaning of each player's mean residual (gamma_hat), which
  is enough for curve extraction and keeps the fit in milliseconds.
Validation on held-out deltas: RMSE must beat the delta=0 baseline and
the league-mean-delta baseline (Model C's own gates, reapplied).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.models.rapm import KNOTS, natural_cubic_basis  # noqa: E402

SKILL_VECTORS = FITENGINE_ROOT / "outputs" / "skill_vectors"
MIN_ARCH_N = 80          # below this, an archetype leans on the global curve
RIDGE_ALPHA = 10.0


def build_deltas(panel: pd.DataFrame, dims: list[str]) -> pd.DataFrame:
    """panel: player_id, end_year, age, arch, <dims...>, weight.
    Returns one row per consecutive-season pair per dimension:
    player_id, end_year (of the LATER season), age (later season), arch,
    dim, delta, weight (min of the two seasons' weights)."""
    rows = []
    for pid, g in panel.sort_values("end_year").groupby("player_id"):
        g = g.reset_index(drop=True)
        for i in range(1, len(g)):
            if g.end_year[i] != g.end_year[i - 1] + 1:
                continue
            for d in dims:
                a, b = g[d][i - 1], g[d][i]
                if pd.isna(a) or pd.isna(b):
                    continue
                rows.append({
                    "player_id": pid, "end_year": int(g.end_year[i]),
                    "age": float(g.age[i]), "arch": g.arch[i], "dim": d,
                    "delta": float(b - a),
                    "weight": float(min(g.weight[i], g.weight[i - 1])),
                })
    return pd.DataFrame(rows)


def _ridge_curve(age: np.ndarray, delta: np.ndarray,
                 w: np.ndarray) -> np.ndarray:
    X = natural_cubic_basis(age)
    Xw = np.column_stack([np.ones(len(age)), X])
    G = (Xw * w[:, None]).T @ Xw
    G[np.diag_indices_from(G)] += RIDGE_ALPHA
    return np.linalg.solve(G, (Xw * w[:, None]).T @ delta)


def fit_curves(deltas: pd.DataFrame) -> dict:
    """Per (dim, arch) curve params with global shrinkage and one-pass
    player-effect demeaning. Returns {dim: {arch: params, '_global': params}}
    where params = [intercept, beta_0..beta_4]."""
    out: dict[str, dict[str, np.ndarray]] = {}
    for dim, gd in deltas.groupby("dim"):
        gd = gd.copy()
        glob = _ridge_curve(gd.age.to_numpy(), gd.delta.to_numpy(),
                            gd.weight.to_numpy())
        # one-step player random effect: demean each player's residual
        X = np.column_stack([np.ones(len(gd)),
                             natural_cubic_basis(gd.age.to_numpy())])
        resid = gd.delta.to_numpy() - X @ glob
        gamma = pd.Series(resid).groupby(gd.player_id.to_numpy()).transform("mean")
        adj = gd.delta.to_numpy() - 0.5 * gamma.to_numpy()  # shrink gamma by half
        curves = {"_global": glob}
        for arch, ga in gd.assign(adj=adj).groupby("arch"):
            fit = _ridge_curve(ga.age.to_numpy(), ga.adj.to_numpy(),
                               ga.weight.to_numpy())
            lam = min(1.0, len(ga) / MIN_ARCH_N)
            curves[arch] = lam * fit + (1 - lam) * glob
        out[dim] = curves
    return out


def expected_delta(curves: dict, dim: str, arch: str, age: float) -> float:
    params = curves[dim].get(arch, curves[dim]["_global"])
    X = np.concatenate([[1.0], natural_cubic_basis(np.array([age]))[0]])
    return float(X @ params)


def validate(deltas: pd.DataFrame, curves: dict,
             holdout_frac: float = 0.2, seed: int = 20260703) -> pd.DataFrame:
    """Refit on a train split, score the holdout against delta=0 and
    league-mean baselines. One row per dim with the pass flag."""
    rng = np.random.default_rng(seed)
    mask = rng.random(len(deltas)) < holdout_frac
    train, test = deltas[~mask], deltas[mask]
    fitted = fit_curves(train)
    rows = []
    for dim, gt in test.groupby("dim"):
        pred = np.array([expected_delta(fitted, dim, r.arch, r.age)
                         for r in gt.itertuples()])
        w = gt.weight.to_numpy()
        rmse = float(np.sqrt(np.average((gt.delta - pred) ** 2, weights=w)))
        rmse0 = float(np.sqrt(np.average(gt.delta ** 2, weights=w)))
        mu = float(np.average(train[train.dim == dim].delta,
                              weights=train[train.dim == dim].weight))
        rmse_mu = float(np.sqrt(np.average((gt.delta - mu) ** 2, weights=w)))
        rows.append({"dim": dim, "rmse_curve": rmse, "rmse_zero": rmse0,
                     "rmse_league_mean": rmse_mu,
                     "beats_both": rmse < min(rmse0, rmse_mu)})
    return pd.DataFrame(rows)


def fit_from_skill_vectors() -> None:
    """The real A2 fit. Refuses until F3 produces skill vectors."""
    if not SKILL_VECTORS.exists():
        raise RuntimeError(
            "A2 aging fit requires outputs/skill_vectors (F3). Written and "
            "smoke-tested only, per the 2026-07-03 overnight directive; "
            "run again after the Layer 1b freeze.")
    raise NotImplementedError(
        "wire the skill_vectors schema here at F3 freeze time")


if __name__ == "__main__":
    fit_from_skill_vectors()
