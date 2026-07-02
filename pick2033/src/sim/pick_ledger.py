"""pick_ledger: MIN's first-round obligation stack + generalized ordered
swap resolution (Bobby's confirmed semantics, 2026-07-01; trade_terms.yaml).

Given per-path slot arrays for all 30 teams (Engine D output), resolves for
each swap year what pick MIN actually holds AFTER prior encumbrances, then
applies the CHA swap. Slots are 1-30 (1 = best).

Resolution rules (all confirmed except the 2029 TBD branch, v1 = CHA-own):
  2027  MIN's first joins the UTA/CLE/PHX pool; MIN holds NOTHING.
  2028  MIN own, unencumbered -> CHA swap: CHA takes the more favorable of
        (MIN, CHA); MIN left with the other.
  2029  MIN keeps own first ONLY if top-5, else it conveys to the UTA-side
        pool and the CHA swap is DEAD that year. When MIN retains (top-5),
        CHA may swap its own first against it.
  2030  SAS stack first: MIN keeps own if #1 overall; else MIN holds the
        LEAST favorable of {MIN, best of (SAS, DAL)}. Then the CHA swap
        applies to MIN's resolved holding. `top1_carries_to_CHA` config
        flag: if False, a #1-overall MIN pick is NOT swappable (MIN keeps
        outright); if True the swap still applies. RUN BOTH.
  2033  MIN's first conveys to CHA outright (unprotected).

HARD GATE: any PRICED run (values, not slots) requires
trade_terms.yaml: verified_post_july6 == true. Slot resolution itself is
mechanical and testable now.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_trade_terms() -> dict:
    return yaml.safe_load((PROJECT_ROOT / "config" / "trade_terms.yaml").read_text())


@dataclass
class SwapYearOutcome:
    """Per-path outcomes for one swap year. Slots are int (1-30);
    0 encodes 'holds nothing this year'."""
    year: int
    min_slot_resolved: np.ndarray      # what MIN holds after PRIOR obligations, before CHA swap
    swap_live: np.ndarray              # bool: is the CHA swap operative this year
    cha_slot_final: np.ndarray         # CHA's first after the swap
    min_slot_final: np.ndarray         # MIN's first after the swap (0 = none)
    swap_exercised: np.ndarray = field(default=None)  # CHA ended up with a better pick than its own


def resolve_year(year: int, slots: dict[str, np.ndarray],
                 top1_carries_to_CHA: bool = True) -> SwapYearOutcome:
    """slots: {'MIN': (n,), 'CHA': (n,), 'SAS': (n,), 'DAL': (n,)} pick slots
    for the given year."""
    MIN, CHA = slots["MIN"], slots["CHA"]
    n = len(MIN)
    zeros = np.zeros(n, dtype=MIN.dtype)

    if year == 2027:
        return SwapYearOutcome(year, zeros, np.zeros(n, bool), CHA.copy(), zeros,
                               np.zeros(n, bool))
    if year == 2028:
        resolved = MIN.copy()
        live = np.ones(n, bool)
    elif year == 2029:
        retained = MIN <= 5
        resolved = np.where(retained, MIN, 0)
        live = retained
    elif year == 2030:
        best_sas_dal = np.minimum(slots["SAS"], slots["DAL"])
        is_no1 = MIN == 1
        stacked = np.maximum(MIN, best_sas_dal)     # LEAST favorable = larger slot
        resolved = np.where(is_no1, MIN, stacked)
        live = np.ones(n, bool)
        if not top1_carries_to_CHA:
            live = ~is_no1
    elif year == 2033:
        # outright conveyance: CHA holds both its own pick and MIN's first
        return SwapYearOutcome(year, MIN.copy(), np.zeros(n, bool), CHA.copy(),
                               zeros, np.zeros(n, bool))
    else:
        raise ValueError(f"{year} is not a swap/conveyance year")

    # CHA swap: takes the more favorable (smaller slot) of (resolved MIN, CHA own)
    better = (resolved < CHA) & live & (resolved > 0)
    cha_final = np.where(better, resolved, CHA)
    min_final = np.where(live & (resolved > 0),
                         np.where(better, CHA, resolved),
                         resolved)
    return SwapYearOutcome(year, resolved, live, cha_final, min_final, better)


def resolve_all(slot_arrays: np.ndarray, fr_ids: list[str], seasons: list[int],
                top1_carries_to_CHA: bool = True) -> dict[int, SwapYearOutcome]:
    """slot_arrays: (n_paths, n_seasons, n_teams) from Engine D."""
    fi = {f: i for i, f in enumerate(fr_ids)}
    si = {s: i for i, s in enumerate(seasons)}
    out = {}
    for year in (2027, 2028, 2029, 2030, 2033):
        if year not in si:
            continue
        ys = {t: slot_arrays[:, si[year], fi[t]].astype(np.int16)
              for t in ("MIN", "CHA", "SAS", "DAL")}
        out[year] = resolve_year(year, ys, top1_carries_to_CHA)
    return out


def require_verified_terms():
    """Call before ANY priced run. Hard-fails while terms are unverified."""
    terms = load_trade_terms()
    if not terms.get("verified_post_july6", False):
        raise RuntimeError(
            "trade_terms.yaml: verified_post_july6 is false -- swap PRICING is "
            "hard-gated until the post-July-6 verification (slot resolution and "
            "payoff-machinery tests are allowed; priced outputs are not).")
