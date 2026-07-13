"""Adapter F (joan_bet_adapter) unit contract.

The heavy CRN-reproduction check (per-path VORP arrays must reproduce
swap_pricing_FINAL.json before any equity number is written) runs inside
joan_bet_adapter.main() itself and hard-fails the pass; these tests pin
the conversion math and the export's gate language, and they run fast.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from src.integrate.joan_bet_adapter import (
    DELIVERY_SEASONS, _load_curve, equity_from_value_draws, instrument_equity,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def curve():
    return _load_curve()["curve"]


def test_zero_value_is_zero_equity(curve):
    v = np.zeros(5)
    net = np.full(5, 3.0)
    assert np.allclose(equity_from_value_draws(v, {"curve": curve, "net": net}), 0.0)


def test_monotone_in_tier(curve):
    """The same positive delta buys weakly more title equity on a stronger
    team (the curve's whole point)."""
    v = np.full(4, 4.0)  # d = 1.0 net per season
    nets = np.array([-7.0, 1.15, 3.74, 7.21])
    pp = equity_from_value_draws(v, {"curve": curve, "net": nets})
    assert (np.diff(pp) >= -1e-9).all()
    assert pp[0] == pytest.approx(0.0, abs=1e-6)   # rebuild tier buys nothing
    assert pp[-1] > 1.0                             # contender tier is steep


def test_odd_symmetry_negative_draws(curve):
    v = np.array([2.0, -2.0])
    net = np.full(2, 3.74)
    pp = equity_from_value_draws(v, {"curve": curve, "net": net})
    assert pp[0] == pytest.approx(-pp[1], rel=1e-9)


def test_tier_clamp_outside_reference_range(curve):
    """Nets beyond the reference teams clamp to the end tiers rather than
    extrapolating the tier axis."""
    v = np.full(2, 4.0)
    inside = equity_from_value_draws(v, {"curve": curve, "net": np.array([7.21, -7.0])})
    outside = equity_from_value_draws(v, {"curve": curve, "net": np.array([12.0, -12.0])})
    assert outside[0] == pytest.approx(inside[0], rel=1e-9)
    assert outside[1] == pytest.approx(inside[1], abs=1e-9)


def test_delta_extrapolation_beyond_grid(curve):
    """Past the 4.0 grid edge the curve continues on the 3.0-4.0 slope."""
    net = np.full(3, 7.21)
    pp = equity_from_value_draws(np.array([12.0, 16.0, 20.0]),
                                 {"curve": curve, "net": net})  # d = 3, 4, 5
    slope_grid = pp[1] - pp[0]
    slope_extrap = pp[2] - pp[1]
    assert slope_extrap == pytest.approx(slope_grid, rel=1e-9)


def test_instrument_equity_horizon_clamp(curve):
    """A 2033 pick delivers entirely past the sim horizon, so all four
    seasons read the 2033 tier: 4x the single-season equity, exactly."""
    seasons = [2027, 2028, 2029, 2030, 2031, 2032, 2033]
    n = 6
    rng = np.random.default_rng(0)
    winpct = rng.uniform(0.2, 0.7, size=(n, len(seasons), 2))
    fr_ids = ["MIN", "CHA"]
    c = 0.032568684193784385
    V = np.full(n, 4.0)
    cum = instrument_equity(V, 2033, "CHA", winpct, fr_ids, seasons, curve, c)
    net_2033 = (winpct[:, -1, 1] - 0.5) / c
    single = equity_from_value_draws(V, {"curve": curve, "net": net_2033})
    assert np.allclose(cum, DELIVERY_SEASONS * single)


def test_export_gate_language():
    out = PROJECT_ROOT / "outputs" / "json" / "total_asset_cost.json"
    if not out.exists():
        pytest.skip("equity pass has not run")
    payload = json.loads(out.read_text())
    assert "deltas only" in payload["meta"]["gate_note"]
    assert payload["meta"]["per_path_sum_note"] == "totals are per-path sums, not sums of means"
    for run in payload["runs"].values():
        for persp in ("delivered_to_CHA", "forgone_by_MIN"):
            tot = run[persp]["picks_swaps_total"]
            assert set(tot) >= {"mean", "q10", "q50", "q90", "per_season", "scenarios"}
            assert set(run[persp]["decomposition"]) >= {
                "swap_2028", "swap_2029", "swap_2030", "outright_2033",
                "second_2029", "second_2032", "second_2033", "resolved_2026"}
