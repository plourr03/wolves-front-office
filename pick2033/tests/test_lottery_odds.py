"""M0 gate: lottery tables match official values; draw mechanics reproduce
exact probabilities within Monte Carlo error; reform constraints hold."""

import itertools
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.sim.lottery import (
    BALLS_78_LOSER,
    BALLS_LOTTERY,
    BALLS_NINE_TEN,
    BALLS_RELEGATED,
    FLOOR_WORST3_MAX_PICK,
    POST_2019_WEIGHTS,
    PRE_2019_WEIGHTS,
    legacy_lottery,
    reformed_lottery,
)

N_MC = 200_000


def test_tables_sum_to_1000():
    assert PRE_2019_WEIGHTS.sum() == 1000
    assert POST_2019_WEIGHTS.sum() == 1000


def test_published_pick1_anchors():
    # Official pick-1 odds: pre-2019 worst team 25.0%; post-2019 bottom three 14.0% each.
    assert PRE_2019_WEIGHTS[0] / 1000 == pytest.approx(0.250)
    for i in range(3):
        assert POST_2019_WEIGHTS[i] / 1000 == pytest.approx(0.140)
    # Reform ball shares: relegated 2/37 = 5.4%, standard lottery 3/37 = 8.1% (published).
    total = 7 * BALLS_LOTTERY + 3 * BALLS_RELEGATED + 4 * BALLS_NINE_TEN + 2 * BALLS_78_LOSER
    assert total == 37
    assert BALLS_RELEGATED / total == pytest.approx(0.054, abs=0.001)
    assert BALLS_LOTTERY / total == pytest.approx(0.081, abs=0.001)


def _exact_topk_slot_probs(weights: np.ndarray, k: int) -> np.ndarray:
    """Exact Plackett-Luce slot probabilities for the drawn picks + the
    deterministic inverse-record remainder, by enumeration of ordered draws."""
    n = len(weights)
    probs = np.zeros((n, n))
    total = weights.sum()
    for perm in itertools.permutations(range(n), k):
        p, rem = 1.0, total
        for idx in perm:
            p *= weights[idx] / rem
            rem -= weights[idx]
        for slot, idx in enumerate(perm):
            probs[idx, slot] += p
        undrawn = [i for i in range(n) if i not in perm]
        for slot, idx in enumerate(undrawn, start=k):
            probs[idx, slot] += p
    return probs


@pytest.mark.parametrize("era,weights,k", [
    ("pre_2019_weighted", PRE_2019_WEIGHTS, 3),
    ("post_2019", POST_2019_WEIGHTS, 4),
])
def test_legacy_mc_matches_exact_enumeration(era, weights, k):
    exact = _exact_topk_slot_probs(weights, k)
    rng = np.random.default_rng(20330701)
    order = np.broadcast_to(np.arange(14), (N_MC, 14)).copy()
    picks = legacy_lottery(order, era, rng)
    for team in range(14):
        for slot in [0, 1, k - 1, k, 7, 13]:
            mc = float((picks[:, slot] == team).mean())
            se = max(np.sqrt(exact[team, slot] * (1 - exact[team, slot]) / N_MC), 1e-6)
            assert abs(mc - exact[team, slot]) < max(5 * se, 0.002), (
                f"{era} team {team} slot {slot}: mc={mc:.4f} exact={exact[team, slot]:.4f}")


def _reformed_fixture(n_paths, barred1=None, barred5=None):
    """Canonical reform setup: teams 0-15 worst-first. Roles: 0-2 relegated,
    3-9 standard lottery (3 balls), 10-13 nine/ten seeds, 14-15 7v8 losers."""
    teams = np.broadcast_to(np.arange(16), (n_paths, 16)).copy()
    balls = np.array([BALLS_RELEGATED] * 3 + [BALLS_LOTTERY] * 7
                     + [BALLS_NINE_TEN] * 4 + [BALLS_78_LOSER] * 2, dtype=float)
    balls = np.broadcast_to(balls, (n_paths, 16)).copy()
    relegated = np.zeros((n_paths, 16), dtype=bool)
    relegated[:, :3] = True
    b1 = np.zeros((n_paths, 16), dtype=bool)
    b5 = np.zeros((n_paths, 16), dtype=bool)
    if barred1 is not None:
        b1[:, barred1] = True
    if barred5 is not None:
        b5[:, barred5] = True
    return teams, balls, relegated, b1, b5


def test_reformed_pick1_marginals_and_permutation():
    rng = np.random.default_rng(20330702)
    n = 100_000
    teams, balls, relegated, b1, b5 = _reformed_fixture(n)
    picks = reformed_lottery(teams, balls, relegated, b1, b5, rng)
    # every path is a permutation of the 16 teams
    assert (np.sort(picks, axis=1) == np.arange(16)).all()
    # pick-1 marginals match ball shares (published 5.4% / 8.1%)
    p1 = picks[:, 0]
    assert float((p1 == 0).mean()) == pytest.approx(2 / 37, abs=0.004)
    assert float((p1 == 3).mean()) == pytest.approx(3 / 37, abs=0.004)
    assert float((p1 == 14).mean()) == pytest.approx(1 / 37, abs=0.003)


def test_reformed_floor_worst3_never_below_12():
    rng = np.random.default_rng(20330703)
    n = 200_000
    teams, balls, relegated, b1, b5 = _reformed_fixture(n)
    picks = reformed_lottery(teams, balls, relegated, b1, b5, rng)
    slots = np.argsort(picks, axis=1)  # slots[p, team] = 0-based slot of team
    worst3_slots = slots[:, :3]
    assert worst3_slots.max() <= FLOOR_WORST3_MAX_PICK - 1, (
        f"floored team fell to pick {worst3_slots.max() + 1}")


def test_reformed_cross_year_bars():
    rng = np.random.default_rng(20330704)
    n = 50_000
    teams, balls, relegated, b1, b5 = _reformed_fixture(n, barred1=0, barred5=4)
    picks = reformed_lottery(teams, balls, relegated, b1, b5, rng)
    assert not (picks[:, 0] == 0).any(), "no-repeat-#1 violated"
    assert not (picks[:, :5] == 4).any(), "no-top-5-three-straight violated"
