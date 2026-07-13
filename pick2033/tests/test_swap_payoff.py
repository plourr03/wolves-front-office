"""Hand-constructed standings through the full encumbrance stack
(spec test_swap_payoff; Bobby's confirmed semantics 2026-07-01)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.sim.pick_ledger import require_verified_terms, resolve_year


def arr(*vals):
    return np.array(vals, dtype=np.int16)


def slots(MIN, CHA, SAS=None, DAL=None):
    n = len(MIN)
    return {"MIN": MIN, "CHA": CHA,
            "SAS": SAS if SAS is not None else arr(*[15] * n),
            "DAL": DAL if DAL is not None else arr(*[16] * n)}


def test_2027_min_holds_nothing():
    out = resolve_year(2027, slots(arr(3, 20), arr(7, 7)))
    assert (out.min_slot_resolved == 0).all()
    assert not out.swap_live.any()
    assert (out.cha_slot_final == arr(7, 7)).all()


def test_2028_straight_swap():
    # path 0: MIN 8 vs CHA 3 -> not exercised; path 1: MIN 2 vs CHA 9 -> exercised
    out = resolve_year(2028, slots(arr(8, 2), arr(3, 9)))
    assert out.swap_live.all()
    assert (out.swap_exercised == np.array([False, True])).all()
    assert (out.cha_slot_final == arr(3, 2)).all()
    assert (out.min_slot_final == arr(8, 9)).all()


def test_2029_top5_only():
    # path 0: MIN 4 (retained, swap live, CHA 10 takes it)
    # path 1: MIN 6 (conveys to UTA pool; swap dead; MIN holds nothing)
    # path 2: MIN 5, CHA 2 (retained, live, CHA keeps its better own pick)
    out = resolve_year(2029, slots(arr(4, 6, 5), arr(10, 10, 2)))
    assert (out.swap_live == np.array([True, False, True])).all()
    assert (out.min_slot_resolved == arr(4, 0, 5)).all()
    assert (out.cha_slot_final == arr(4, 10, 2)).all()
    assert (out.min_slot_final == arr(10, 0, 5)).all()
    assert (out.swap_exercised == np.array([True, False, False])).all()


def test_2030_sas_stack_then_swap():
    # path 0: MIN #1 overall -> keeps own (flag True: still swappable vs CHA 4)
    # path 1: MIN 5, best(SAS,DAL)=3 -> least favorable = 5; CHA 2 keeps own
    # path 2: MIN 2, best(SAS,DAL)=20 -> MIN holds 20; CHA 25 swaps up to 20
    s = slots(arr(1, 5, 2), arr(4, 2, 25), SAS=arr(9, 3, 20), DAL=arr(10, 12, 25))
    out = resolve_year(2030, s, top1_carries_to_CHA=True)
    assert (out.min_slot_resolved == arr(1, 5, 20)).all()
    assert (out.cha_slot_final == arr(1, 2, 20)).all()
    assert (out.min_slot_final == arr(4, 5, 25)).all()

    out2 = resolve_year(2030, s, top1_carries_to_CHA=False)
    assert not out2.swap_live[0]                # MIN keeps #1 outright
    assert (out2.cha_slot_final == arr(4, 2, 20)).all()
    assert out2.min_slot_final[0] == 1


def test_2033_outright_conveyance():
    out = resolve_year(2033, slots(arr(12, 1), arr(5, 30)))
    assert (out.min_slot_resolved == arr(12, 1)).all()   # the conveyed asset
    assert (out.min_slot_final == 0).all()
    assert (out.cha_slot_final == arr(5, 30)).all()      # CHA's own, held alongside


def test_pricing_hard_gate(monkeypatch):
    # Tests the gate MECHANISM under both flag states, independent of the live
    # config (verified_post_july6 flipped true 2026-07-12 when terms verified).
    from src.sim import pick_ledger
    monkeypatch.setattr(pick_ledger, "load_trade_terms",
                        lambda: {"verified_post_july6": False})
    with pytest.raises(RuntimeError, match="verified_post_july6"):
        require_verified_terms()
    monkeypatch.setattr(pick_ledger, "load_trade_terms",
                        lambda: {"verified_post_july6": True})
    require_verified_terms()


def test_e2_machinery_on_synthetic_slots():
    """End-to-end payoff machinery on FABRICATED slots (not a priced run of
    the real trade: inputs are synthetic, gate on real pricing stays up)."""
    from src.sim.swap_pricing import _price_impl
    rng = np.random.default_rng(0)
    n = 400
    fr_ids = ["MIN", "CHA", "SAS", "DAL"]
    seasons = [2027, 2028, 2029, 2030, 2031, 2032, 2033]
    slots_arr = rng.integers(1, 31, size=(n, len(seasons), len(fr_ids))).astype(np.int8)
    departures = {"Anthony Edwards": rng.random(n) < 0.5}
    cha_win = rng.uniform(0.3, 0.7, n)
    rep = _price_impl(slots_arr, fr_ids, seasons, departures, cha_win,
                      seed=1, top1_carries_to_CHA=True, currency="vorp")
    assert set(rep["swaps"]) == {2028, 2029, 2030}
    for y, s in rep["swaps"].items():
        assert 0.0 <= s["p_exercise"] <= 1.0
        assert s["mean"] >= 0.0                      # option payoffs are non-negative
    assert rep["outright_2033"]["mean"] > 0.0        # a first-round pick has value
    assert rep["total_per_path"]["mean"] >= rep["outright_2033"]["mean"]
    probs = [v["p"] for v in rep["total_per_path"]["scenarios"].values()]
    assert abs(sum(probs) - 1.0) < 1e-9


def test_priced_run_hard_gate(monkeypatch):
    from src.sim import pick_ledger
    from src.sim.swap_pricing import price_all
    monkeypatch.setattr(pick_ledger, "load_trade_terms",
                        lambda: {"verified_post_july6": False})
    with pytest.raises(RuntimeError, match="verified_post_july6"):
        price_all(None, None, None, None, None, 0)
