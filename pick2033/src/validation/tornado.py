"""S7 tornado runner (spec Section 9 + accumulated ruling arms).
BUILT 2026-07-02, EXECUTES POST-JULY-6 (priced runs are hard-gated; every
arm's headline outputs are the 2033 pick EV and the total asset cost, which
require pricing).

Each arm = one Engine D run (20k paths for arms, full 50k for the base) +
one priced pass, reported as deltas on the headline outputs vs base.
Per-arm definitions below are pre-declared; no arm is tuned after seeing
its result.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.sim.pick_ledger import require_verified_terms  # noqa: E402

ARMS = [
    # (name, kind, spec) -- kinds consumed by run_arm()
    ("hazard_scale_0.5x", "hazard_scale", 0.5),
    ("hazard_scale_1.5x", "hazard_scale", 1.5),
    ("blend_faster", "blend_shift", -1),          # roster trust decays one season faster
    ("blend_slower", "blend_shift", +1),
    ("trajectory_phi_p10", "posterior_pctile", ("phi", 10)),
    ("trajectory_phi_p90", "posterior_pctile", ("phi", 90)),
    ("shock_scale_p10", "posterior_pctile", ("sigma_shock", 10)),
    ("shock_scale_p90", "posterior_pctile", ("sigma_shock", 90)),
    ("slot_value_ws", "currency", "ws"),
    ("playin_crude_randomization", "playin", "crude"),
    ("top1_carries_false", "config", {"top1_carries_to_CHA": False}),
    ("pooled_dynamics", "posterior_swap", "trajectory_c0a9750162a046d3"),  # Ruling A cond. 1, fit-once
    ("cha_lineage_bobcats_fresh", "refit_lineage", "bobcats_fresh"),       # Bobby amendment 5 (plan)
    ("s_contract_midpoint_split", "hazard_refit_perturbed", "midpoint_split"),  # directive 3, ungated
    ("lamelo_extended", "config", {"lamelo_contract": "extended"}),
]


def run_arm(name, kind, spec):
    raise NotImplementedError(
        "arm execution lands post-July-6: each arm re-runs Engine D with the "
        "declared perturbation and re-prices; deltas vs base go to tornado.json")


def main():
    require_verified_terms()   # hard gate: no tornado before pricing unlocks
    for arm in ARMS:
        run_arm(*arm)


if __name__ == "__main__":
    main()
