"""Fast correctness tests for the Layer 1b factor-model math (no MCMC):
the matrix-determinant-lemma row log-likelihood must equal a direct MVN
logpdf, and the conditional-posterior factor-score mean/cov must equal the
brute-force Gaussian-conditioning formula. These catch a bug in the
marginalized likelihood or the skill-vector derivation without a fit."""

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _woodbury_ll(y, W, d):
    """Mirror of skill_factors._model row_ll, in numpy."""
    p, K = W.shape
    inv_d = 1.0 / d
    a = inv_d * y
    b = W.T @ a
    M = np.eye(K) + (W.T * inv_d) @ W
    L = np.linalg.cholesky(M)
    x = np.linalg.solve(M, b)
    quad = y @ a - b @ x
    logdet = np.sum(np.log(d)) + 2.0 * np.sum(np.log(np.diag(L)))
    return -0.5 * (p * np.log(2 * np.pi) + logdet + quad)


def test_woodbury_ll_matches_direct_mvn():
    rng = np.random.default_rng(0)
    p, K = 21, 8
    for _ in range(5):
        W = rng.normal(0, 0.6, (p, K))
        d = rng.uniform(0.1, 1.5, p)
        y = rng.normal(0, 1, p)
        C = W @ W.T + np.diag(d)
        sign, logdet = np.linalg.slogdet(C)
        direct = -0.5 * (p * np.log(2 * np.pi) + logdet + y @ np.linalg.solve(C, y))
        assert abs(_woodbury_ll(y, W, d) - direct) < 1e-8


def test_factor_score_conditional_matches_bruteforce():
    """E[Z|y] and Cov[Z|y] for y = W z + eps, z~N(0,I), eps~N(0,diag(d))."""
    rng = np.random.default_rng(1)
    p, K = 21, 8
    W = rng.normal(0, 0.6, (p, K))
    d = rng.uniform(0.1, 1.5, p)
    y = rng.normal(0, 1, p)

    # skill_factors uses: A = I + Wᵀ diag(1/d) W ; m = A^-1 Wᵀ diag(1/d) y ; cov = A^-1
    inv_d = 1.0 / d
    A = np.eye(K) + (W.T * inv_d) @ W
    Ainv = np.linalg.inv(A)
    m = Ainv @ (W.T * inv_d) @ y

    # brute force via the joint Gaussian of (z, y): Cov(z,y)=Wᵀ, Cov(y)=WWᵀ+D
    Cyy = W @ W.T + np.diag(d)
    Czy = W.T                       # Cov(z, y) = E[z (Wz+eps)ᵀ] = Wᵀ
    m_bf = Czy @ np.linalg.solve(Cyy, y)
    cov_bf = np.eye(K) - Czy @ np.linalg.solve(Cyy, Czy.T)
    np.testing.assert_allclose(m, m_bf, atol=1e-8)
    np.testing.assert_allclose(Ainv, cov_bf, atol=1e-8)


def test_anchor_structure_is_pure_marker():
    from src.models import skill_factors as sf
    # each anchor feature must be distinct and map to its own factor
    idx = [sf.FEAT_COLS.index(sf.ANCHORS[k]) for k in range(sf.K)]
    assert len(set(idx)) == sf.K            # 8 distinct anchor features
    assert set(sf.ANCHORS) == set(range(sf.K))
