"""gate.py — the deterministic CBA-feasibility gate (spec Section 5).

Given a Plan (an ordered list of trade/signing legs) and a GateConfig, return a
GateResult. A plan PASSES only if it is:
  1. CBA-legal leg by leg (matching, apron hard caps, aggregation, the latch),
  2. landing BELOW the second apron (the spec's binding constraint),
  3. retaining every required-retained player (Ayo Dosunmu, via Bird re-sign),
  4. leaving a fillable roster.
No plan that FAILS the gate is ever handed to the title-equity engine.

This module owns the Plan / GateResult abstraction. The CBA math itself is reused
unchanged from the verified offseason engine through cba.engine_bridge.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cba import engine_bridge as bridge

log = logging.getLogger("core_max.cba.gate")


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class RequiredPlayer:
    pid: str
    name: str
    reason: str = ""


@dataclass(frozen=True)
class GateConfig:
    """Versioned, file-driven gate configuration. The binding second-apron line is
    read LIVE from the engine constants (not duplicated here) so it cannot drift; the
    config records provenance and the reconciliation notes only."""
    version: str
    season: str
    team: str
    base_scenario: str
    second_apron_line: int
    required_retained: tuple[RequiredPlayer, ...]
    roster_floor: int
    seed: int
    constants_source: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_file(path: str | Path) -> "GateConfig":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        const = bridge.load_constants(d["season"])
        sa_live = int(const["second_apron"])
        # If the config records an expected binding line, assert it against the engine.
        sa_cfg = (d.get("constants_source") or {}).get("second_apron_binding_line")
        if sa_cfg is not None and int(sa_cfg) != sa_live:
            raise ValueError(
                f"second-apron line drift: config says ${int(sa_cfg):,}, engine says ${sa_live:,}. "
                "Re-validate the constants before trusting the gate.")
        return GateConfig(
            version=d["version"],
            season=d["season"],
            team=d["team"],
            base_scenario=d.get("base_scenario", "base"),
            second_apron_line=sa_live,
            required_retained=tuple(RequiredPlayer(**r) for r in d.get("required_retained", [])),
            roster_floor=int(d.get("roster_floor", 8)),
            seed=int(d.get("seed", 0)),
            constants_source=d.get("constants_source", {}),
        )


# --------------------------------------------------------------------------- #
# Plan
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Leg:
    label: str
    outgoing: tuple[dict, ...] = ()
    incoming: tuple[dict, ...] = ()
    exception_used: str = "none"

    def to_engine(self) -> dict:
        return {
            "label": self.label,
            "outgoing": [dict(p) for p in self.outgoing],
            "incoming": [dict(p) for p in self.incoming],
            "exception_used": self.exception_used,
        }


@dataclass(frozen=True)
class Plan:
    name: str
    description: str
    legs: tuple[Leg, ...]

    @staticmethod
    def from_file(path: str | Path) -> "Plan":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        legs = tuple(
            Leg(
                label=leg["label"],
                outgoing=tuple(leg.get("outgoing", [])),
                incoming=tuple(leg.get("incoming", [])),
                exception_used=leg.get("exception_used", "none"),
            )
            for leg in d["legs"]
        )
        return Plan(name=d["name"], description=d.get("description", ""), legs=legs)


# --------------------------------------------------------------------------- #
# Result
# --------------------------------------------------------------------------- #
@dataclass
class GateResult:
    plan_name: str
    passed: bool
    reasons: list[str]                 # human-readable failure reasons (empty if passed)
    chain_legal: bool
    final_apron: int
    final_tier: str
    below_second_apron: bool
    required_retained_ok: bool
    required_status: dict[str, bool]
    roster_count: int
    roster_ok: bool
    second_apron_line: int
    per_leg: list[dict]


# --------------------------------------------------------------------------- #
# The gate
# --------------------------------------------------------------------------- #
def evaluate_plan(plan: Plan, config: GateConfig) -> GateResult:
    """Run the plan's legs through the reused chain engine, then apply the four
    Section-5 predicates. Deterministic: no sampling, no randomness."""
    const = bridge.load_constants(config.season)
    base_ts = bridge.load_team_state(config.team, config.season, config.base_scenario)
    legs = [leg.to_engine() for leg in plan.legs]

    state, results = bridge.run_chain(base_ts, const, legs)

    chain_legal = all(bool(r.get("legal")) for r in results)
    final_apron = int(state.ts["apron_team_salary"])
    final_tier = str(state.ts["tier"])
    sa = int(const["second_apron"])
    below_second = final_apron < sa

    # Required retention models a pending free agent: the player must be ACQUIRED
    # (re-signed, so present in roster_in) and not subsequently traded out.
    required_status: dict[str, bool] = {}
    for rp in config.required_retained:
        retained = (rp.pid in state.roster_in) and (rp.pid not in state.roster_out)
        required_status[rp.name] = retained
    required_ok = all(required_status.values()) if required_status else True

    roster_count = int(state.count)
    roster_ok = roster_count >= config.roster_floor

    reasons: list[str] = []
    if not chain_legal:
        idx, bad = next((i + 1, r) for i, r in enumerate(results) if not r.get("legal"))
        reasons.append(f"CBA-illegal at leg {idx}: {bad.get('failing_constraint', 'unspecified')}")
    if not below_second:
        reasons.append(f"lands at/above the second apron: ${final_apron:,} >= ${sa:,}")
    for name, ok in required_status.items():
        if not ok:
            reasons.append(f"required player not retained: {name}")
    if not roster_ok:
        reasons.append(
            f"roster too thin: {roster_count} counted contracts < floor {config.roster_floor}")

    per_leg = [
        {
            "label": legs[i]["label"],
            "legal": bool(r.get("legal")),
            "apron": r.get("corrected_apron_team_salary") or r.get("new_apron_team_salary"),
            "why": r.get("failing_constraint") or "",
            "hard_capped": bool(r.get("take_back_more") or r.get("hard_cap_tripped")
                                or r.get("hard_cap_set", "none") != "none"),
        }
        for i, r in enumerate(results)
    ]

    passed = not reasons
    return GateResult(
        plan_name=plan.name,
        passed=passed,
        reasons=reasons,
        chain_legal=chain_legal,
        final_apron=final_apron,
        final_tier=final_tier,
        below_second_apron=below_second,
        required_retained_ok=required_ok,
        required_status=required_status,
        roster_count=roster_count,
        roster_ok=roster_ok,
        second_apron_line=sa,
        per_leg=per_leg,
    )


# --------------------------------------------------------------------------- #
# Reporting (technical detail + plain-language summary)
# --------------------------------------------------------------------------- #
def format_result(res: GateResult, plan: Plan | None = None) -> str:
    lines: list[str] = []
    verdict = "PASS" if res.passed else "FAIL"
    lines.append(f"[{verdict}] {res.plan_name}")
    if plan and plan.description:
        lines.append(f"   {plan.description}")
    for leg in res.per_leg:
        tag = "legal" if leg["legal"] else "ILLEGAL"
        apron = f"${leg['apron']:,}" if leg["apron"] is not None else "n/a"
        cap = " [hard-capped]" if leg["hard_capped"] else ""
        lines.append(f"   - [{tag}] {leg['label']} -> apron {apron}{cap}")
        if not leg["legal"] and leg["why"]:
            lines.append(f"       why: {leg['why']}")
    lines.append(
        f"   end state: apron ${res.final_apron:,} ({res.final_tier}), "
        f"${res.second_apron_line - res.final_apron:,} under the second apron")
    lines.append(
        f"   gates: below_2nd_apron={res.below_second_apron} | "
        f"required_retained={res.required_retained_ok} {res.required_status} | "
        f"roster_ok={res.roster_ok} (count {res.roster_count})")
    if not res.passed:
        for r in res.reasons:
            lines.append(f"   FAIL reason: {r}")
    return "\n".join(lines)


def plain_summary(res: GateResult) -> str:
    """One-paragraph, jargon-light readout for non-technical scanning."""
    if res.passed:
        return (f"{res.plan_name}: FEASIBLE. It lands at ${res.final_apron:,}, "
                f"${res.second_apron_line - res.final_apron:,} below the second apron, keeps the "
                f"must-keep players, and leaves a fillable roster, so it is eligible to be scored "
                f"for title equity.")
    return (f"{res.plan_name}: NOT FEASIBLE. " + " ".join(res.reasons) +
            " It would not be scored for title equity until fixed.")
