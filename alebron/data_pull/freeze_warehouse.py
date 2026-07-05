"""
Phase 2, step 1: freeze the warehouse to a versioned parquet snapshot.

Clean-room project. This script reuses ONLY the database connection helper from
postmortem/lib/db.py (pure infrastructure, not a fitted output or constant), and
exports the warehouse tables the engine needs into a dated, content-hashed snapshot
so the analysis is reproducible while the live field keeps moving through free agency.

Excluded here on purpose: nba_play_by_play (17M rows, and pre-2025-26 uses a legacy
format that needs a possession-normalization shim). PBP/possession extraction is its
own step in the impact-layer build, not this generic field freeze.

Run:  python lamelo/data_pull/freeze_warehouse.py
Output: lamelo/data/snapshot_<date>/<table>.parquet  +  manifest.json
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "postmortem" / "lib"))
import db  # noqa: E402  (infrastructure-only reuse: the psycopg2 connection helper)

FREEZE_DATE = "2026-06-25"  # field-freeze date, locked in freeze_manifest.md
OUT = REPO / "lamelo" / "data" / f"snapshot_{FREEZE_DATE}"

# Tables to freeze (moderate size; PBP excluded as noted above).
TABLES = [
    "nba_player_stats",
    "nba_player_advanced_stats",
    "nba_games",
    "nba_team_advanced_stats",
    "nba_synergy_player_play_types",
    "nba_team_rosters",
    "nba_player_bio",
    "nba_transactions",
    "nba_player_contracts",
]


def content_fingerprint(dfr: pd.DataFrame) -> str:
    """Deterministic content fingerprint independent of row order and file format."""
    h = pd.util.hash_pandas_object(dfr.fillna("\x00NULL\x00"), index=False)
    # sort the per-row hashes so row order does not change the fingerprint
    return hashlib.sha256(h.sort_values().to_numpy().tobytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest: dict = {"freeze_date": FREEZE_DATE, "tables": {}}
    use_parquet = True
    try:
        import pyarrow  # noqa: F401
    except Exception:
        use_parquet = False
        print("pyarrow not available; falling back to csv.gz")

    for t in TABLES:
        print(f"exporting {t} ...", flush=True)
        dfr = db.query(f"SELECT * FROM {t}")
        fp = content_fingerprint(dfr)
        if use_parquet:
            path = OUT / f"{t}.parquet"
            dfr.to_parquet(path, index=False)
        else:
            path = OUT / f"{t}.csv.gz"
            dfr.to_csv(path, index=False, compression="gzip")
        manifest["tables"][t] = {
            "rows": int(len(dfr)),
            "cols": list(map(str, dfr.columns)),
            "content_sha256": fp,
            "file": path.name,
            "bytes": int(path.stat().st_size),
        }
        print(f"  {len(dfr):>9,} rows -> {path.name}  ({path.stat().st_size/1e6:.1f} MB)")

    # overall snapshot hash = sha256 of the canonical manifest (sans the hash itself)
    canon = json.dumps(manifest["tables"], sort_keys=True).encode()
    manifest["snapshot_sha256"] = "wh_" + hashlib.sha256(canon).hexdigest()[:16]
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\nsnapshot id: {manifest['snapshot_sha256']}")
    print(f"manifest: {OUT / 'manifest.json'}")


if __name__ == "__main__":
    main()
