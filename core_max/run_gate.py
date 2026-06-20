#!/usr/bin/env python3
"""run_gate.py — run the CBA-feasibility gate over the configured scenarios.

    python core_max/run_gate.py                 # all scenarios in config/scenarios/
    python core_max/run_gate.py --scenario fork_b
    python core_max/run_gate.py --plan path/to/plan.json

Deterministic and config-driven: scenarios live in config/scenarios/*.json, the
binding cap lines come from the versioned engine constants, nothing is hardcoded.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # make `cba` importable

from cba import gate  # noqa: E402

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config" / "gate_config.json"
SCENARIOS = HERE / "config" / "scenarios"


def main() -> int:
    ap = argparse.ArgumentParser(description="Core Maximization CBA-feasibility gate.")
    ap.add_argument("--scenario", help="name of a scenario in config/scenarios (without .json)")
    ap.add_argument("--plan", help="path to a standalone plan JSON")
    ap.add_argument("--config", default=str(CONFIG), help="path to gate_config.json")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")

    config = gate.GateConfig.from_file(args.config)
    logging.getLogger("core_max").info(
        "config v%s | season %s | second apron $%s | seed %s",
        config.version, config.season, f"{config.second_apron_line:,}", config.seed)

    if args.plan:
        plan_paths = [Path(args.plan)]
    elif args.scenario:
        plan_paths = [SCENARIOS / f"{args.scenario}.json"]
    else:
        plan_paths = sorted(SCENARIOS.glob("*.json"))

    print("=" * 78)
    print("CBA-FEASIBILITY GATE (Phase 0)")
    print("=" * 78)
    all_pass = True
    summaries = []
    for p in plan_paths:
        plan = gate.Plan.from_file(p)
        res = gate.evaluate_plan(plan, config)
        all_pass = all_pass and res.passed
        print()
        print(gate.format_result(res, plan))
        summaries.append(gate.plain_summary(res))

    print()
    print("-" * 78)
    print("PLAIN-LANGUAGE SUMMARY")
    print("-" * 78)
    for s in summaries:
        print("  " + s)
    return 0 if all_pass else 0  # gate is a classifier, not a build step; never errors on a FAIL


if __name__ == "__main__":
    raise SystemExit(main())
