"""F2 unit contracts (no DB, no DuckDB store): the aging-basis
reimplementation matches pick2033's exactly, ridge_solve recovers known
coefficients, and the design builder pools sub-threshold players."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

FITENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FITENGINE_ROOT))


def _rapm():
    """Import src.models.rapm lazily so config parsing happens per test."""
    from src.models import rapm
    return rapm


def test_natural_cubic_basis_matches_pick2033():
    rapm = _rapm()
    aging_path = (FITENGINE_ROOT.parent / "pick2033" / "src" / "models"
                  / "aging.py")
    if not aging_path.exists():
        pytest.skip("pick2033 not present on this machine")
    spec = importlib.util.spec_from_file_location("p2033_aging", aging_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ages = np.array([19.0, 21.5, 24.0, 27.3, 30.0, 33.1, 36.0, 40.0])
    ours = rapm.natural_cubic_basis(ages)
    theirs = mod.natural_cubic_basis(ages)
    assert ours.shape == theirs.shape == (8, 5)
    np.testing.assert_allclose(ours, theirs, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(rapm.KNOTS, mod.KNOTS)


def test_ridge_solve_recovers_offsets_and_signal():
    rapm = _rapm()
    rng = np.random.default_rng(7)
    from scipy.sparse import csr_matrix
    n, k = 4000, 12
    X = csr_matrix((rng.random((n, k)) < 0.3).astype(float))
    true = rng.normal(0, 2, k)
    y = 110.0 + X @ true + rng.normal(0, 0.5, n)
    w = np.full(n, 3.0)
    coef, intercept = rapm.ridge_solve(X, y, w, alpha=1e-6)
    np.testing.assert_allclose(coef, true, atol=0.15)
    assert abs(intercept - 110.0) < 1.0
    # offset trick: fitting y - X@prior must return coef ~ true - prior
    prior = true * 0.5
    coef2, _ = rapm.ridge_solve(X, y, w, alpha=1e-6, offset=X @ prior)
    np.testing.assert_allclose(prior + coef2, true, atol=0.15)


def test_build_design_pools_subthreshold_players():
    rapm = _rapm()
    five_a = "1,2,3,4,5"
    five_b = "6,7,8,9,10"
    # player 99 appears in one low-possession row only -> replacement pool
    five_c = "1,2,3,4,99"
    df = pd.DataFrame({
        "off_lineup": [five_a, five_c, five_b],
        "def_lineup": [five_b, five_b, five_a],
        "poss": [rapm.MIN_POSS_OWN, 10, rapm.MIN_POSS_OWN],
        "pts": [500, 8, 480],
        "game_id": ["g1", "g1", "g2"],
    })
    X, y, w, games, players, R, poss_by_player = rapm.build_design(df)
    assert 99 not in players
    assert set(players) == set(range(1, 11))
    assert X.shape == (3, 2 * (R + 1))
    # every row must place exactly 5 offense and 5 defense entries
    row_sums = np.asarray(X.sum(axis=1)).ravel()
    np.testing.assert_array_equal(row_sums, [10.0, 10.0, 10.0])
    # the replacement column carries player 99's appearance
    assert X[1, R] == 1.0


def test_gram_system_matches_dense_weighted_centered():
    rapm = _rapm()
    rng = np.random.default_rng(3)
    from scipy.sparse import csr_matrix
    n, k = 500, 8
    X = csr_matrix((rng.random((n, k)) < 0.4).astype(float))
    y = rng.normal(0, 3, n)
    w = rng.uniform(0.5, 4, n)
    G0, b0, SYY, x_mean, y_mean, sw = rapm.gram_system(X, y, w)
    Xd = X.toarray()
    xm = (w[:, None] * Xd).sum(0) / w.sum()
    ym = (w * y).sum() / w.sum()
    Xc, yc = Xd - xm, y - ym
    np.testing.assert_allclose(G0, (Xc * w[:, None]).T @ Xc, atol=1e-8)
    np.testing.assert_allclose(b0, (Xc * w[:, None]).T @ yc, atol=1e-8)
    np.testing.assert_allclose(SYY, (w * yc * yc).sum(), atol=1e-6)
    np.testing.assert_allclose(x_mean, xm, atol=1e-10)


def test_gcv_prefers_more_shrinkage_when_noisier():
    rapm = _rapm()
    rng = np.random.default_rng(5)
    from scipy.sparse import csr_matrix
    n, k = 3000, 20
    X = csr_matrix((rng.random((n, k)) < 0.3).astype(float))
    beta = rng.normal(0, 1, k)
    w = np.ones(n)
    y_clean = X @ beta + rng.normal(0, 0.3, n)
    y_noisy = X @ beta + rng.normal(0, 6.0, n)
    a_clean = rapm.ALPHA_GRID[int(np.argmin(rapm._gcv_curve(X, y_clean, w)))]
    a_noisy = rapm.ALPHA_GRID[int(np.argmin(rapm._gcv_curve(X, y_noisy, w)))]
    assert a_noisy >= a_clean
    # GCV curve must be finite everywhere
    assert np.all(np.isfinite(rapm._gcv_curve(X, y_clean, w)))


def test_archetype_mapping():
    rapm = _rapm()
    assert rapm.archetype("Guard") == "guard"
    assert rapm.archetype("Center") == "big"
    assert rapm.archetype("Forward-Center") == "big"
    assert rapm.archetype("Forward") == "wing"
    assert rapm.archetype("Guard-Forward") == "wing"
    assert rapm.archetype(None) == "wing"
