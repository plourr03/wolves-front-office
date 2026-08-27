"""Content-addressed warehouse snapshots for the Kuminga project.

Same discipline as core_max/data_pull/frozen.py, generalized to freeze an arbitrary
set of warehouse tables. The production warehouse is READ-ONLY for this project and it
is a moving target (the daily refresh runs every morning at 03:33), so every model
input is pinned to a snapshot whose id is a hash of its own contents. An identical
warehouse state reproduces the same id; a mutated snapshot fails loudly on read.

    from kuminga.lib import kfreeze
    kfreeze.freeze({"nba_player_contracts": df, ...}, label="phase1")
    df, sid = kfreeze.load("nba_player_contracts")
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FROZEN_ROOT = os.path.join(REPO, "kuminga", "data", "frozen")


def _hash_df(df: pd.DataFrame) -> str:
    """Deterministic content hash: sorted-CSV bytes, column order stable."""
    csv = df.sort_values(list(df.columns)).to_csv(index=False).encode("utf-8")
    return hashlib.sha256(csv).hexdigest()


def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce Postgres NUMERIC (decimal.Decimal) columns to float.

    Decimal objects survive a parquet round-trip with a different repr than the
    in-memory frame, so hashing before the write and re-hashing after the read
    disagree even though nothing changed. Normalising once, up front, means the
    stored bytes and the verified bytes are the same object.
    """
    out = df.copy()
    for c in out.columns:
        if out[c].dtype == object:
            nonnull = out[c].dropna()
            if len(nonnull) and isinstance(nonnull.iloc[0], Decimal):
                out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def freeze(tables: dict[str, pd.DataFrame], label: str = "unlabeled",
           note: str = "", set_current: bool = True) -> str:
    """Write a content-addressed snapshot. Returns the snapshot id.

    The hash is taken on the ROUND-TRIPPED frame (write, read back, hash) so that
    freeze-time and load-time hashes are computed over identical bytes. Hashing the
    in-memory frame instead makes the integrity assert fire on any dtype the parquet
    writer normalises, which is a false alarm that looks exactly like corruption.
    """
    os.makedirs(FROZEN_ROOT, exist_ok=True)
    tables = {k: _normalise(v) for k, v in tables.items()}

    tmpdir = os.path.join(FROZEN_ROOT, "_staging")
    os.makedirs(tmpdir, exist_ok=True)
    hashes = {}
    for name, df in sorted(tables.items()):
        path = os.path.join(tmpdir, name + ".parquet")
        df.to_parquet(path, index=False)
        hashes[name] = _hash_df(pd.read_parquet(path))

    combined = hashlib.sha256(
        "".join(f"{k}:{hashes[k]}" for k in sorted(hashes)).encode("utf-8")
    ).hexdigest()[:16]
    sid = f"wh_{combined}"

    outdir = os.path.join(FROZEN_ROOT, sid)
    os.makedirs(outdir, exist_ok=True)
    for name in tables:
        os.replace(os.path.join(tmpdir, name + ".parquet"),
                   os.path.join(outdir, name + ".parquet"))
    try:
        os.rmdir(tmpdir)
    except OSError:
        pass

    manifest = {
        "snapshot_id": sid,
        "label": label,
        "note": note,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "nba_warehouse schema nba (read-only)",
        "tables": {
            name: {"rows": int(len(df)), "cols": list(df.columns), "sha256": hashes[name]}
            for name, df in tables.items()
        },
    }
    with open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    if set_current:
        with open(os.path.join(FROZEN_ROOT, "CURRENT"), "w", encoding="utf-8") as fh:
            fh.write(sid)
    return sid


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
    """Load a frozen table, re-hashing and asserting it matches the manifest."""
    sid = snapshot_id or current_snapshot_id()
    man = manifest(sid)
    assert table in man["tables"], f"table '{table}' not in snapshot {sid} (have: {list(man['tables'])})"
    df = pd.read_parquet(os.path.join(FROZEN_ROOT, sid, table + ".parquet"))
    h = _hash_df(df)
    assert h == man["tables"][table]["sha256"], f"'{table}' content hash mismatch (snapshot mutated)"
    return df, sid
