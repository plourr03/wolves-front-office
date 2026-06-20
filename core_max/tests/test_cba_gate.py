#!/usr/bin/env python3
"""test_cba_gate.py — Phase 0 validation for the CBA-feasibility gate.

Three layers:
  A. Gate validation: the three spec scenarios PASS; one hand-built FAIL per gate
     predicate (CBA-illegal leg, lands at/above 2nd apron, required player dropped,
     roster too thin).
  B. KAT-trade structural regression: replay the documented salary shape of the
     Karl-Anthony Towns trade through the reused engine and confirm the matching /
     take-back logic reproduces the expected verdict.
  C. Engine known-answer regression: a handful of hand-checked evaluate_move cases
     ported directly, so a change in the reused CBA math is caught here.

    python core_max/tests/test_cba_gate.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # `cba` importable

from cba import gate                       # noqa: E402
from cba import engine_bridge as bridge    # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = ROOT / "config" / "gate_config.json"
SCENARIOS = ROOT / "config" / "scenarios"

_PASSED: list[bool] = []


def check(name: str, cond: bool, detail: str = "") -> bool:
    ok = bool(cond)
    _PASSED.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -> {detail}" if detail else ""))
    return ok


# --------------------------------------------------------------------------- #
# helpers to build inline plans
# --------------------------------------------------------------------------- #
def leg(label, outgoing=(), incoming=(), exception_used="none") -> gate.Leg:
    return gate.Leg(label=label, outgoing=tuple(outgoing), incoming=tuple(incoming),
                    exception_used=exception_used)


AYO = {"label": "Ayo Dosunmu (Bird re-sign)", "salary": 16_500_000, "pid": "1630245"}


# --------------------------------------------------------------------------- #
# A. Gate validation
# --------------------------------------------------------------------------- #
def test_gate(config: gate.GateConfig) -> None:
    print("\nA. Gate validation")

    # the three spec scenarios should all be FEASIBLE (they differ on title equity, not legality)
    for name in ("status_quo", "fork_b", "splash"):
        plan = gate.Plan.from_file(SCENARIOS / f"{name}.json")
        res = gate.evaluate_plan(plan, config)
        check(f"scenario '{name}' PASSES the gate", res.passed,
              f"apron ${res.final_apron:,} ({res.final_tier}), "
              f"${res.second_apron_line - res.final_apron:,} under 2nd apron")

    # FAIL 1: CBA-illegal leg. Re-sign Ayo (-> first-apron tier), then a full-MLE
    # signing, which is unavailable above the first apron -> illegal leg.
    p = gate.Plan("fail_illegal", "Ayo then an unavailable full-MLE signing", (
        leg("Re-sign Ayo via Bird", incoming=(AYO,), exception_used="bird"),
        leg("Full-MLE signing ($15.048M)",
            incoming=({"label": "MLE wing", "salary": 15_048_000, "pid": "MLE"},),
            exception_used="full_mle"),
    ))
    r = gate.evaluate_plan(p, config)
    check("FAIL (CBA-illegal leg) is rejected", (not r.passed) and (not r.chain_legal),
          "; ".join(r.reasons))

    # FAIL 2: required player dropped. Fork B's two trades but NO Ayo re-sign.
    p = gate.Plan("fail_no_ayo", "Fork B trades without re-signing Ayo", (
        leg("Randle -> creator", outgoing=({"label": "Randle", "salary": 33_333_334, "pid": "203944"},),
            incoming=({"label": "creator", "salary": 30_000_000, "pid": "C1"},)),
        leg("Gobert -> wing", outgoing=({"label": "Gobert", "salary": 36_500_000, "pid": "203497",
                                         "trade_kicker_pct": 0.075},),
            incoming=({"label": "wing", "salary": 24_000_000, "pid": "W1"},)),
    ))
    r = gate.evaluate_plan(p, config)
    check("FAIL (Ayo not retained) is rejected", (not r.passed) and (not r.required_retained_ok)
          and r.chain_legal and r.below_second_apron, "; ".join(r.reasons))

    # FAIL 3: lands at/above the second apron. Bird re-signs do NOT trip the apron
    # hard cap, so over-spending on OWN free agents is the one legal way MIN can
    # breach the second apron. The $15M own-FA here is hypothetical (MIN has no such
    # free agent); the mechanism it exercises is real.
    p = gate.Plan("fail_over_2nd_apron", "Ayo + a hypothetical $15M own-FA Bird re-sign push over the 2nd apron", (
        leg("Re-sign Ayo via Bird", incoming=(AYO,), exception_used="bird"),
        leg("Re-sign hypothetical own-FA ($15M) via Bird",
            incoming=({"label": "own FA", "salary": 15_000_000, "pid": "OWNFA"},),
            exception_used="bird"),
    ))
    r = gate.evaluate_plan(p, config)
    check("FAIL (above 2nd apron) is rejected", (not r.passed) and (not r.below_second_apron)
          and r.chain_legal and r.required_retained_ok,
          f"lands ${r.final_apron:,} >= ${r.second_apron_line:,}")

    # FAIL 4: roster too thin. Aggregate four bodies for one, plus Ayo -> 7 counted
    # contracts, below the floor.
    p = gate.Plan("fail_thin_roster", "Aggregate 4-for-1 over-shed leaves the roster too thin", (
        leg("Aggregate Gobert + Randle + Conley + DiVincenzo -> one star",
            outgoing=(
                {"label": "Gobert", "salary": 36_500_000, "pid": "203497", "trade_kicker_pct": 0.075},
                {"label": "Randle", "salary": 33_333_334, "pid": "203944"},
                {"label": "Conley", "salary": 10_800_000, "pid": "201144"},
                {"label": "DiVincenzo", "salary": 12_000_000, "pid": "1628978"},
            ),
            incoming=({"label": "star ($50M)", "salary": 50_000_000, "pid": "STAR"},)),
        leg("Re-sign Ayo via Bird", incoming=(AYO,), exception_used="bird"),
    ))
    r = gate.evaluate_plan(p, config)
    check("FAIL (roster too thin) is rejected", (not r.passed) and (not r.roster_ok)
          and r.chain_legal and r.below_second_apron and r.required_retained_ok,
          f"counted contracts {r.roster_count} < floor {config.roster_floor}")


# --------------------------------------------------------------------------- #
# B. KAT-trade structural regression
# --------------------------------------------------------------------------- #
def test_kat_structural() -> None:
    print("\nB. KAT-trade structural regression")
    print("   NOTE: structural (salary-shape) replay using current MIN state + 2026-27 brackets.")
    print("   A period-accurate replay needs 2024-25 cap lines + 2024-25 team-state (a documented gap).")
    const = bridge.load_constants("2026-27")
    min_base = bridge.load_team_state("MIN", "2026-27", "base")
    # Documented (approximate) 2024-25 salaries from the KAT trade:
    KAT = 49_205_800
    RANDLE_IN, DDV_IN = 28_939_680, 11_445_759
    r = bridge.evaluate_move(
        min_base, const,
        [{"label": "Karl-Anthony Towns", "salary": KAT}],
        [{"label": "Julius Randle", "salary": RANDLE_IN},
         {"label": "Donte DiVincenzo", "salary": DDV_IN}],
    )
    in_total = RANDLE_IN + DDV_IN
    check("KAT trade is a legal salary match", r["legal"], r.get("failing_constraint", ""))
    check("KAT trade takes back LESS than it sends (no take-back-more cap)",
          (not r["take_back_more"]) and in_total < KAT,
          f"${in_total:,} in vs ${KAT:,} out")
    check("KAT trade sets no first-apron take-back-more hard cap",
          r.get("hard_cap_set", "none") == "none")


# --------------------------------------------------------------------------- #
# C. Engine known-answer regression (ported, no trade_search dependency)
# --------------------------------------------------------------------------- #
def test_engine_known_answers() -> None:
    print("\nC. Engine known-answer regression (ported evaluate_move cases)")
    c = bridge.load_constants("2026-27")
    minb = bridge.load_team_state("MIN", "2026-27", "base")
    okc = bridge.load_team_state("OKC", "2026-27", "base")

    r = bridge.evaluate_move(minb, c, [{"label": "Randle", "salary": 33_333_334}],
                             [{"label": "wing", "salary": 35_000_000}])
    check("legal take-back within the 125% band", r["legal"])

    r = bridge.evaluate_move(minb, c, [{"label": "filler", "salary": 10_000_000}],
                             [{"label": "star", "salary": 30_000_000}])
    check("illegal over-band match rejected", not r["legal"])

    r = bridge.evaluate_move(minb, c, [{"label": "Randle", "salary": 33_333_334}],
                             [{"label": "Kyrie", "salary": 39_491_282}])
    check("take-back-more SETS the first-apron hard cap",
          r["legal"] and r["take_back_more"] and r["hard_cap_set"] == "first_apron")

    r = bridge.evaluate_move(okc, c, [{"label": "p1", "salary": 15_000_000},
                                      {"label": "p2", "salary": 12_000_000}],
                             [{"label": "big", "salary": 26_000_000}])
    check("second-apron aggregation forbidden", not r["legal"])

    r = bridge.evaluate_move(okc, c, [{"label": "p1", "salary": 20_000_000}],
                             [{"label": "in", "salary": 19_500_000}])
    check("second-apron 1-for-1 dollar-for-dollar legal", r["legal"])


def main() -> int:
    print("=" * 78)
    print("PHASE 0 CBA-GATE VALIDATION")
    print("=" * 78)
    config = gate.GateConfig.from_file(CONFIG)
    print(f"config v{config.version} | season {config.season} | "
          f"second apron ${config.second_apron_line:,} | roster_floor {config.roster_floor}")

    test_gate(config)
    test_kat_structural()
    test_engine_known_answers()

    n_ok, n = sum(_PASSED), len(_PASSED)
    print(f"\n{n_ok}/{n} checks passed")
    return 0 if n_ok == n else 1


if __name__ == "__main__":
    raise SystemExit(main())
