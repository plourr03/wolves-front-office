"""A2 smoke tests on synthetic data (the only kind of A2 fit permitted
until skill vectors exist): curve recovery on a known aging shape, the
validation harness beating its baselines, and the real-data guard."""

import numpy as np
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models import aging_fit  # noqa: E402


def synth_panel(seed=11, n_players=150):
    """Two skill dims with known aging shapes: dim_a peaks at 27 and
    declines, dim_b declines linearly with age."""
    rng = np.random.default_rng(seed)
    rows = []
    for pid in range(n_players):
        start_age = rng.uniform(19, 30)
        arch = rng.choice(["guard", "wing", "big"])
        a = rng.normal(0, 1)
        b = rng.normal(0, 1)
        for k in range(6):
            age = start_age + k
            a += -0.12 * (age - 27.0) / 3.0 + rng.normal(0, 0.05)
            b += -0.08 + rng.normal(0, 0.05)
            rows.append({"player_id": pid, "end_year": 2015 + k,
                         "age": age, "arch": arch, "dim_a": a, "dim_b": b,
                         "weight": rng.uniform(0.5, 2.0)})
    return pd.DataFrame(rows)


def test_build_deltas_pairs_consecutive_seasons_only():
    panel = synth_panel(n_players=5)
    panel = panel[~((panel.player_id == 0) & (panel.end_year == 2017))]
    d = aging_fit.build_deltas(panel, ["dim_a", "dim_b"])
    p0 = d[(d.player_id == 0)]
    assert 2017 not in set(p0.end_year)      # missing season
    assert 2018 not in set(p0.end_year)      # gap breaks the pair too
    assert set(d.dim) == {"dim_a", "dim_b"}


def test_curves_recover_known_shapes():
    panel = synth_panel()
    deltas = aging_fit.build_deltas(panel, ["dim_a", "dim_b"])
    curves = aging_fit.fit_curves(deltas)
    # dim_a: young players improve, old players decline
    young = aging_fit.expected_delta(curves, "dim_a", "wing", 21.0)
    old = aging_fit.expected_delta(curves, "dim_a", "wing", 34.0)
    assert young > 0 > old
    # dim_b: decline at every age
    for age in (21.0, 27.0, 33.0):
        assert aging_fit.expected_delta(curves, "dim_b", "guard", age) < 0


def test_validation_beats_baselines_on_structured_data():
    panel = synth_panel(seed=5)
    deltas = aging_fit.build_deltas(panel, ["dim_a"])
    report = aging_fit.validate(deltas, None)
    row = report[report.dim == "dim_a"].iloc[0]
    assert row.rmse_curve < row.rmse_zero
    assert row.beats_both or row.rmse_curve < row.rmse_league_mean * 1.02


def test_real_fit_refuses_without_skill_vectors():
    if aging_fit.SKILL_VECTORS.exists():
        pytest.skip("skill vectors exist; guard no longer applies")
    with pytest.raises(RuntimeError, match="requires outputs/skill_vectors"):
        aging_fit.fit_from_skill_vectors()
