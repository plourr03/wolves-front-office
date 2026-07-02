"""E2: swap option pricing machinery (spec 7.7 + confirmed encumbrance
semantics). MACHINERY ONLY until trade_terms.yaml: verified_post_july6 is
true -- require_verified_terms() hard-gates every priced entry point; the
resolution layer (pick_ledger) and payoff shapes are testable now.

Per swap year Y and simulation path:
    exercised[path] = CHA ended up holding a better pick than its own
    payoff[path]    = value(cha_slot_final) - value(CHA own slot)   >= 0
in both currencies (VORP primary, WS robustness), using E1 REALIZED-value
draws (curve draw + empirical band residual) so payoff intervals carry
outcome risk, with curve-only reported as a variant.

The 2033 outright first is priced as value(min_slot_resolved).
Seconds: flat E1 slot-31-45 value (config-listed).
The resolved 2026 No.28/No.33 line item: deterministic slot-EV off E1.
Totals: per-path sums, never sums of marginal means.
Scenario decomposition: baseline / Edwards-departs / CHA-ascends / joint.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.models.slot_value import band_residuals, curve_draws, load_data  # noqa: E402
from src.sim.pick_ledger import require_verified_terms, resolve_all  # noqa: E402

SWAP_YEARS = (2028, 2029, 2030)


def payoff_draws(outcome, post, residuals, rng, realized=True):
    """Swap payoff for one year: value(CHA final) - value(CHA own), same
    curve/residual draw pairing across the pair so slot-value uncertainty
    is common-random-numbered within the path."""
    res = residuals if realized else None
    n = len(outcome.cha_slot_final)
    v_final = np.zeros(n)
    v_own = np.zeros(n)
    live = outcome.cha_slot_final > 0
    # CHA own slot: reconstruct (cha_final == own unless exercised)
    own = np.where(outcome.swap_exercised, outcome.min_slot_final, outcome.cha_slot_final)
    v_final[live] = curve_draws(post, outcome.cha_slot_final[live], rng, res)
    same = outcome.cha_slot_final == own
    v_own[same] = v_final[same]           # identical slot -> identical draw (CRN)
    diff = live & ~same
    v_own[diff] = curve_draws(post, own[diff], rng, res)
    return np.maximum(v_final - v_own, 0.0), outcome.swap_exercised.copy()


def scenario_masks(departures: dict, cha_win_2033: np.ndarray) -> dict:
    edwards_out = departures["Anthony Edwards"]
    cha_good = cha_win_2033 >= 0.55
    return {
        "baseline": ~edwards_out & ~cha_good,
        "edwards_departs": edwards_out & ~cha_good,
        "cha_ascends": ~edwards_out & cha_good,
        "joint_tail": edwards_out & cha_good,
    }


def price_all(slots, fr_ids, seasons, departures, cha_win_2033, seed,
              top1_carries_to_CHA=True, currency="vorp"):
    """FULL priced run -- HARD-GATED until terms verification."""
    require_verified_terms()
    return _price_impl(slots, fr_ids, seasons, departures, cha_win_2033, seed,
                       top1_carries_to_CHA, currency)


def _price_impl(slots, fr_ids, seasons, departures, cha_win_2033, seed,
                top1_carries_to_CHA, currency):
    from src.models.slot_value import fit as fit_e1
    import yaml
    params = yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())
    df = load_data()
    col = "value_4yr" if currency == "vorp" else "value_alt"
    post, _ = fit_e1(df[col].values.astype(float), df.slot.values.astype(int),
                     currency, params["seed"] + 6)
    residuals = band_residuals(df, post, col)
    rng = np.random.default_rng(seed)
    outcomes = resolve_all(slots, fr_ids, seasons, top1_carries_to_CHA)
    masks = scenario_masks(departures, cha_win_2033)

    report = {"currency": currency, "top1_carries_to_CHA": top1_carries_to_CHA,
              "swaps": {}, "outright_2033": None}
    total = np.zeros(slots.shape[0])
    for y in SWAP_YEARS:
        pay, exercised = payoff_draws(outcomes[y], post, residuals, rng)
        total += pay
        report["swaps"][y] = _summarize(pay, exercised, masks)
    v2033 = curve_draws(post, outcomes[2033].min_slot_resolved, rng, residuals)
    total += v2033
    report["outright_2033"] = _summarize(v2033, np.ones_like(v2033, bool), masks)
    report["total_per_path"] = _summarize(total, None, masks)
    return report


def _summarize(vals, exercised, masks):
    out = {"mean": float(vals.mean()), "q10": float(np.percentile(vals, 10)),
           "q50": float(np.percentile(vals, 50)), "q80_lo": float(np.percentile(vals, 10)),
           "q90": float(np.percentile(vals, 90))}
    if exercised is not None:
        out["p_exercise"] = float(np.asarray(exercised).mean())
    out["scenarios"] = {k: {"p": float(m.mean()),
                            "conditional_mean": float(vals[m].mean()) if m.any() else None}
                        for k, m in masks.items()}
    return out
