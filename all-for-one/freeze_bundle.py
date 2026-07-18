"""Freeze bundler for the ONE FOR ALL October 20, 2026 freeze.

Rehearses the freeze mechanics NOW (a dry run), so October 20 is the SECOND time
this pipeline runs, not the first. It bundles the freeze-set artifacts exactly as
the real freeze will, computes a deterministic SHA-256 bundle hash, and writes a
manifest. It publishes NOTHING; the rehearsal hash is recorded locally only.

Determinism (the whole point -- the hash is the article's proof, so the procedure
must be reproducible byte for byte):
  - files are read as raw BYTES (no line-ending normalization),
  - the freeze set is sorted by repo-relative path,
  - the bundle hash is sha256 of the canonical body (one "sha256  path" line per
    present file, sorted, newline-terminated) and nothing else,
  - NO timestamps, machine names, or run-order enter the output.
Run it twice; the manifest bytes and the bundle hash must be identical.

Usage:
  python freeze_bundle.py            # write manifest + print bundle hash
  python freeze_bundle.py --verify   # run the bundling twice in-process, assert identical
"""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent          # wolves-front-office/
HERE = Path(__file__).resolve().parent                 # all-for-one/

# The freeze SET: the content artifacts that lock on 2026-10-20 (repo-relative paths).
# board_spec.md carries the SALVAGE_CAP ruling and the P(east) ruling record (manifest
# items 5 and 6); roster_reconciliation.md is the roster snapshot (item 7).
FREEZE_SET = [
    "all-for-one/tripwire-backtest/TRIPWIRES.md",
    "all-for-one/board/jaden_calibration/jaden_markers_v02.md",
    "all-for-one/board/docs/fork_adjudication.md",
    "all-for-one/board/docs/league_event_resolve_rule.md",
    "all-for-one/board/docs/board_spec.md",
    "all-for-one/board/build/roster_recon/roster_reconciliation.md",
]

# Members named in the freeze but not yet materialized as files. They do NOT enter the
# bundle hash (absent = not hashed); they are recorded so the October bundle adds them.
PENDING = [
    "R1/R2 schedule mapping (manifest item 8) -- awaiting the 2026-27 NBA schedule release",
]

MANIFEST_OUT = HERE / "freeze_bundle_manifest.txt"


def file_sha256(relpath: str) -> str:
    return hashlib.sha256((REPO / relpath).read_bytes()).hexdigest()


def canonical_body() -> str:
    """The exact bytes the bundle hash is taken over: sorted 'sha256  path' lines."""
    lines = []
    for rel in sorted(FREEZE_SET):
        lines.append(f"{file_sha256(rel)}  {rel}\n")
    return "".join(lines)


def bundle_hash() -> str:
    return hashlib.sha256(canonical_body().encode("utf-8")).hexdigest()


def render_manifest() -> str:
    """The human-readable manifest. Deterministic: no timestamps or run metadata.
    The bundle hash is a function ONLY of the canonical body (present files)."""
    body = canonical_body()
    bh = hashlib.sha256(body.encode("utf-8")).hexdigest()
    out = []
    out.append("ONE FOR ALL -- freeze bundle manifest (REHEARSAL)")
    out.append("Freeze target: 2026-10-20. This file is a dry run; nothing is published.")
    out.append("")
    out.append(f"present freeze-set members: {len(FREEZE_SET)}")
    out.append("per-file SHA-256 (sorted by path; the bundle hash is taken over exactly these lines):")
    out.append("")
    out.append(body.rstrip("\n"))
    out.append("")
    out.append(f"pending members (named, absent -- NOT in the bundle hash): {len(PENDING)}")
    for p in PENDING:
        out.append(f"  - {p}")
    out.append("")
    out.append(f"BUNDLE SHA-256 (rehearsal): {bh}")
    out.append("")
    out.append("Reproduce: python all-for-one/freeze_bundle.py --verify")
    return "\n".join(out) + "\n"


def verify() -> bool:
    """Run the bundling twice in-process; assert byte-identical manifest and hash."""
    m1, h1 = render_manifest(), bundle_hash()
    m2, h2 = render_manifest(), bundle_hash()
    ok = (m1 == m2) and (h1 == h2)
    print(f"[verify] run1 hash {h1}")
    print(f"[verify] run2 hash {h2}")
    print(f"[verify] manifest bytes identical: {m1 == m2} | hash identical: {h1 == h2}")
    print(f"[verify] RESULT: {'PASS (deterministic)' if ok else 'FAIL (non-deterministic!)'}")
    return ok


def main():
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    manifest = render_manifest()
    MANIFEST_OUT.write_text(manifest, encoding="utf-8", newline="\n")
    print(manifest)
    print(f"wrote {MANIFEST_OUT}")


if __name__ == "__main__":
    main()
