"""engine_bridge.py — the single, isolated coupling point between core_max and
the verified offseason CBA engine.

Per the kickoff decision (hybrid CBA gate): reuse the validated deterministic
engine as the compute core, but keep ALL knowledge of where it lives and how it
is called in this one adapter, so the rest of core_max depends on a clean typed
surface rather than on the offseason code's schema or style. If the offseason
engine ever moves or changes signature, this is the only file that edits.

Reused unchanged:
  offseason/scripts/evaluate_move.py   load_constants, load_team_state, evaluate_move
  offseason/scripts/chain_engine.py    run_chain (state carry, hard-cap latch, TPE consumption)
  offseason/scripts/build_team_state.py derive_tier, toolbox (via chain_engine)

Note: we deliberately import only chain_engine.run_chain and evaluate_move. The
heavier trade_search / partner_acceptance / simulation stack is NOT pulled in
(those are imported lazily inside other chain_engine functions we do not call).
"""
from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENGINE_DIR = os.path.join(_REPO_ROOT, "offseason", "scripts")
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

import evaluate_move as _EM   # noqa: E402
import chain_engine as _CE    # noqa: E402


def load_constants(season: str) -> dict:
    """League_year_constants row for a season (cap, tax, both aprons, matching brackets)."""
    return _EM.load_constants(season)


def load_team_state(team: str, season: str, scenario: str = "base") -> dict:
    """The derived team_state row (apron basis, tier, TPEs, distances, permissions)."""
    return _EM.load_team_state(team, season, scenario)


def run_chain(initial_ts_row: dict, const: dict, legs: list[dict], label: str = "MIN"):
    """Thread `legs` through a fresh carried state. Returns (ChainState, [leg_result, ...]).
    Each leg_result carries `legal`, `failing_constraint`, the corrected apron, hard-cap
    fields, etc. The returned state exposes `.ts`, `.count`, `.roster_in`, `.roster_out`."""
    return _CE.run_chain(initial_ts_row, const, legs, label=label)


def evaluate_move(team_state: dict, const: dict, outgoing: list[dict], incoming: list[dict],
                  pick_and_cash: dict | None = None, exception_used: str = "none") -> dict:
    """Single-transaction CBA evaluation (used for the structural regression test)."""
    return _EM.evaluate_move(team_state, const, outgoing, incoming, pick_and_cash, exception_used)
