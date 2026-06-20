"""Read the pinned Phase 1 warehouse snapshot, asserting integrity and a shared id.

Every Phase 1 step that touches warehouse-derived data loads through here, so a
second warehouse update mid-build cannot open a seam: 1b and 1c read the SAME
content-addressed snapshot and assert the same id. See freeze_warehouse.py.
"""
import os
import json
import hashlib
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FROZEN_ROOT = os.path.join(REPO, "core_max", "data_frozen")


def current_snapshot_id() -> str:
    with open(os.path.join(FROZEN_ROOT, "CURRENT"), encoding="utf-8") as fh:
        return fh.read().strip()


def manifest(snapshot_id: str | None = None) -> dict:
    sid = snapshot_id or current_snapshot_id()
    with open(os.path.join(FROZEN_ROOT, sid, "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    assert man["snapshot_id"] == sid, f"snapshot id mismatch: dir {sid} vs manifest {man['snapshot_id']}"
    return man


def load(table: str, snapshot_id: str | None = None) -> tuple[pd.DataFrame, str]:
    """Return (frozen table, snapshot_id). Re-hashes the table and asserts it matches the
    manifest, so a mutated snapshot fails loudly. Pass the same snapshot_id from 1b into 1c
    (or rely on CURRENT) to guarantee both steps read one warehouse state."""
    sid = snapshot_id or current_snapshot_id()
    man = manifest(sid)
    assert table in man["tables"], f"table '{table}' not in snapshot {sid}"
    df = pd.read_parquet(os.path.join(FROZEN_ROOT, sid, table + ".parquet"))
    h = hashlib.sha256(df.sort_values(list(df.columns)).to_csv(index=False).encode("utf-8")).hexdigest()
    assert h == man["tables"][table]["sha256"], f"'{table}' content hash mismatch (snapshot mutated)"
    return df, sid
