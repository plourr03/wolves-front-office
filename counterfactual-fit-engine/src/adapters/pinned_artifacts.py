"""R2 amendment 4: cross-repo artifact fence, same posture as AM-1.
pick2033's aging posterior (A2 priors) and warehouse (rookie archetype
priors) are pinned by content hash in config/model_params.yaml and verified
at load. A drifted artifact refuses to load; re-pinning requires a memo."""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

FITENGINE_ROOT = Path(__file__).resolve().parents[2]


class PinnedArtifactDriftError(RuntimeError):
    pass


def _sha256_16(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_pinned_path(name: str) -> Path:
    cfg = yaml.safe_load((FITENGINE_ROOT / "config" / "model_params.yaml").read_text())
    entry = cfg["pinned_artifacts"][name]
    path = (FITENGINE_ROOT / entry["path"]).resolve()
    actual = _sha256_16(path)
    if actual != entry["sha256_16"]:
        raise PinnedArtifactDriftError(
            f"{name} at {path} has drifted from its pin "
            f"(expected {entry['sha256_16']}, got {actual}). Re-pin with a "
            "decision memo or restore the pinned artifact; never absorb "
            "silently.")
    return path
