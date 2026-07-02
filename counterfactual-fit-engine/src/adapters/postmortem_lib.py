"""AM-1 fence: hash-verified frozen imports from postmortem/lib.

postmortem/lib serves the live LAFI/offseason consumers. fitengine's G1
possession-parity gate references reconstruct_possessions as THE canonical
parser, so these files must not drift under us. Every import through this
adapter first verifies the git blob hash of each pinned file against
config/pinned_lib.yaml and REFUSES on mismatch (fixtures catch drift after
it bites; the hash refuses it). Vendoring at the pinned hash is the memo'd
fallback if postmortem needs to move mid-build.

Frozen re-exports (never modified by fitengine):
  db.query                        Postgres access
  pbp.normalize_pbp               both-format normalizer
  pbp.reconstruct_possessions     canonical possession parser (G1 reference)
  pbp.tag_garbage_time/tag_clutch/tag_transition   A3 leverage basis

The floor-state/stint code (lineups.py, lineup_aggregation.py) is pinned
here for provenance but is FORKED into src/stints/ at F1 for hardening;
the pinned originals remain the comparison baseline.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = FITENGINE_ROOT.parent
PIN_FILE = FITENGINE_ROOT / "config" / "pinned_lib.yaml"


class PinnedLibDriftError(ImportError):
    pass


def _git_blob_hash(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def verify_pins() -> dict:
    pins = yaml.safe_load(PIN_FILE.read_text())["pinned_files"]
    drifted = {}
    for rel, expected in pins.items():
        actual = _git_blob_hash(REPO_ROOT / rel)
        if actual != expected:
            drifted[rel] = {"expected": expected, "actual": actual}
    if drifted:
        raise PinnedLibDriftError(
            "postmortem/lib has drifted from the AM-1 pin. Do NOT absorb "
            "silently: either re-pin with a decision memo (if the change is "
            "benign and fitengine adopts it) or vendor a snapshot at the "
            f"pinned hashes. Drifted: {drifted}")
    return pins


# verification runs at import time, before anything else touches the lib
verify_pins()

sys.path.insert(0, str(REPO_ROOT / "postmortem"))

from lib.db import query  # noqa: E402, F401
from lib.pbp import (  # noqa: E402, F401
    normalize_pbp,
    reconstruct_possessions,
    tag_clutch,
    tag_garbage_time,
    tag_transition,
)
