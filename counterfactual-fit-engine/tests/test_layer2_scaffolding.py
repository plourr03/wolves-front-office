"""F4 smoke tests, synthetic data only (no real Layer 2 fits until F3
vectors exist): GBM floor beats additive on planted pairwise synergy, the
set-attention net is permutation invariant before AND after training, and
it also beats the additive baseline on the synthetic set."""

import numpy as np
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models import gbm_floor  # noqa: E402

K = 4
N_PLAYERS = 60


def synth_world(seed=9, n_rows=2500):
    """Planted structure: outcome = additive sum + pairwise synergy on
    dims (0,1) within the offense + small context effects + noise."""
    rng = np.random.default_rng(seed)
    vectors = {pid: rng.normal(0, 1, K) for pid in range(1, N_PLAYERS + 1)}
    rows = []
    for i in range(n_rows):
        off = rng.choice(N_PLAYERS, 5, replace=False) + 1
        dfn = rng.choice(N_PLAYERS, 5, replace=False) + 1
        ov = np.stack([vectors[p] for p in off])
        dv = np.stack([vectors[p] for p in dfn])
        additive = ov[:, 0].sum() - dv[:, 1].sum()
        synergy = sum(gbm_floor._cosine(ov[i_, :2], ov[j_, :2])
                      for i_ in range(5) for j_ in range(i_ + 1, 5))
        home = rng.random()
        rest = rng.normal(0, 1.5)
        y = 112 + 2.0 * additive + 3.0 * synergy + 0.8 * home + 0.2 * rest \
            + rng.normal(0, 2.0)
        rows.append({
            "off_lineup": ",".join(map(str, sorted(off))),
            "def_lineup": ",".join(map(str, sorted(dfn))),
            "pts_per100": y, "poss": float(rng.integers(5, 60)),
            "home_share": home, "rest_delta": rest,
            "end_year": 2015 + (i * 4) // n_rows,  # 4 synthetic seasons
        })
    return pd.DataFrame(rows), vectors


def test_gbm_floor_beats_additive_on_planted_synergy():
    rows, vectors = synth_world()
    report = gbm_floor.temporal_fit_eval(rows, vectors, test_year=2018)
    assert report["n_train"] > 0 and report["n_test"] > 0
    assert report["beats_additive"], report


def test_engineered_features_shape_and_determinism():
    rows, vectors = synth_world(n_rows=50)
    X1 = gbm_floor.engineer_matrix(rows, vectors)
    X2 = gbm_floor.engineer_matrix(rows, vectors)
    assert X1.shape == (50, 9 * K + 5)
    np.testing.assert_array_equal(X1, X2)


@pytest.fixture(scope="module")
def torch_bits():
    torch = pytest.importorskip("torch")
    from src.models.set_attention import SetSynergyNet, train
    return torch, SetSynergyNet, train


def _tensors(rows, vectors, torch):
    off = np.stack([np.stack([vectors[int(p)] for p in r.split(",")])
                    for r in rows.off_lineup])
    dfn = np.stack([np.stack([vectors[int(p)] for p in r.split(",")])
                    for r in rows.def_lineup])
    ctx = rows[["home_share", "rest_delta"]].to_numpy()
    ctx = np.column_stack([ctx, rows.end_year.to_numpy() - 2015])
    return off, dfn, ctx


def test_set_attention_permutation_invariance(torch_bits):
    torch, SetSynergyNet, _ = torch_bits
    rows, vectors = synth_world(n_rows=8)
    off, dfn, ctx = _tensors(rows, vectors, torch)
    model = SetSynergyNet(k_dim=K)
    model.eval()
    t = lambda a: torch.as_tensor(a, dtype=torch.float32)
    with torch.no_grad():
        base = model(t(off), t(dfn), t(ctx))
        rng = np.random.default_rng(0)
        po = off[:, rng.permutation(5), :]
        pd_ = dfn[:, rng.permutation(5), :]
        perm = model(t(po), t(pd_), t(ctx))
    torch.testing.assert_close(base, perm, atol=1e-5, rtol=1e-5)


def test_set_attention_trains_and_beats_additive(torch_bits):
    torch, SetSynergyNet, train = torch_bits
    rows, vectors = synth_world(seed=13, n_rows=1500)
    off, dfn, ctx = _tensors(rows, vectors, torch)
    y = rows.pts_per100.to_numpy()
    w = rows.poss.to_numpy()
    tr = rows.end_year < 2018
    te = ~tr

    model = SetSynergyNet(k_dim=K)
    train(model, off[tr.values], dfn[tr.values], ctx[tr.values],
          y[tr.values], w[tr.values], epochs=60, patience=10)
    model.eval()
    t = lambda a: torch.as_tensor(a, dtype=torch.float32)
    with torch.no_grad():
        pred = model(t(off[te.values]), t(dfn[te.values]),
                     t(ctx[te.values])).numpy()
    rmse = float(np.sqrt(np.average((y[te.values] - pred) ** 2,
                                    weights=w[te.values])))

    from sklearn.linear_model import Ridge
    Xtr = gbm_floor.engineer_matrix(rows[tr], vectors)
    Xte = gbm_floor.engineer_matrix(rows[te], vectors)
    contrast = slice(8 * K, 9 * K)
    base = Ridge(alpha=1.0).fit(Xtr[:, contrast], y[tr.values],
                                sample_weight=w[tr.values])
    rmse_base = float(np.sqrt(np.average(
        (y[te.values] - base.predict(Xte[:, contrast])) ** 2,
        weights=w[te.values])))
    assert rmse < rmse_base, (rmse, rmse_base)

    # invariance must survive training
    with torch.no_grad():
        b0 = model(t(off[:8]), t(dfn[:8]), t(ctx[:8]))
        rng = np.random.default_rng(1)
        b1 = model(t(off[:8][:, rng.permutation(5), :]),
                   t(dfn[:8][:, rng.permutation(5), :]), t(ctx[:8]))
    torch.testing.assert_close(b0, b1, atol=1e-4, rtol=1e-4)
