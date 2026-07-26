#!/usr/bin/env python3
"""Freeze ONE warehouse snapshot for the entire Phase 1 build.

The warehouse is a live, moving target (it shifted between 2026-06-13 and now, which
the RAPM refactor gate caught). Phase 1 is multi-step with a slow RAPM refit in the
middle, so a second update landing between 1b and 1c would silently put them on
different data, hitting the residuals and the calibration (not the invariant SDs).
This pulls everything Phase 1 needs from the warehouse ONCE into a content-addressed
local snapshot; 1b and 1c then both assert they read the same snapshot id. Same
reproducibility discipline as fixed seeds and versioned constants, extended to the
one input that just demonstrated it can shift under us.

    python core_max/data_pull/freeze_warehouse.py [--label 2026-06-20]

Writes core_max/data_frozen/<snapshot_id>/ (frozen tables + manifest.json) and points
core_max/data_frozen/CURRENT at it. snapshot_id is a content hash, so an identical
warehouse state reproduces the same id.
"""
import os
import sys
import json
import hashlib
import argparse
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
sys.path.insert(0, os.path.join(REPO, "postmortem"))
import build_rapm as BR   # noqa: E402  (its box_features hits the warehouse)
from lib import db        # noqa: E402

FROZEN_ROOT = os.path.join(REPO, "core_max", "data_frozen")
RIM_SEASONS = ("2023-24", "2024-25", "2025-26")


def pull_rim_defense():
    """Per-player-season rim-protection signals (box/tracking-computable, small-sample
    stable). The signal the rim correction conditions on, never def_rapm."""
    return db.query("""
        SELECT player_id, season_year, gp, def_rim_fgm, def_rim_fga, def_rim_fg_pct, blk
        FROM nba_player_tracking_season
        WHERE measure_type = 'Defense' AND season_type = 'Regular Season'
          AND season_year IN %s
        ORDER BY player_id, season_year""", (RIM_SEASONS,))


def _hash_df(df: pd.DataFrame) -> str:
    """Deterministic content hash: sorted-CSV bytes (column-order stable)."""
    csv = df.sort_values(list(df.columns)).to_csv(index=False).encode("utf-8")
    return hashlib.sha256(csv).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="unlabeled", help="human metadata only; the id is content-based")
    args = ap.parse_args()

    tables = {}
    print("pulling rim defense (3 seasons) ...", flush=True)
    tables["rim_defense"] = pull_rim_defense()
    print(f"  {len(tables['rim_defense'])} rows", flush=True)
    print("pulling box features: full window ...", flush=True)
    tables["box_feats_full"] = BR.box_features(None)
    print("pulling box features: train window (2023, 2024) ...", flush=True)
    tables["box_feats_train"] = BR.box_features((2023, 2024))
    print("pulling box features: holdout window (2025) ...", flush=True)
    tables["box_feats_holdout"] = BR.box_features((2025,))

    hashes = {k: _hash_df(v) for k, v in tables.items()}
    combined = hashlib.sha256("".join(hashes[k] for k in sorted(hashes)).encode()).hexdigest()
    snapshot_id = "wh_" + combined[:16]

    out = os.path.join(FROZEN_ROOT, snapshot_id)
    os.makedirs(out, exist_ok=True)
    for k, v in tables.items():
        v.to_parquet(os.path.join(out, k + ".parquet"), index=False)
    manifest = {
        "snapshot_id": snapshot_id,
        "label": args.label,
        "source": "nba_warehouse (POSTGRES_HOST <SERVER_TAILSCALE_IP>, schema nba)",
        "rim_seasons": list(RIM_SEASONS),
        "box_windows": {"full": None, "train": [2023, 2024], "holdout": [2025]},
        "tables": {k: {"rows": int(len(v)), "cols": list(v.columns), "sha256": hashes[k]}
                   for k, v in tables.items()},
        "purpose": "Phase 1 frozen warehouse read; 1b (rim) and 1c (RAPM box prior) both pin this id.",
        "note": "fit_rapm names query (player_name labels only) is cosmetic and not frozen; the numeric path (box prior) is.",
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    with open(os.path.join(FROZEN_ROOT, "CURRENT"), "w", encoding="utf-8") as fh:
        fh.write(snapshot_id + "\n")

    print(f"\nFROZEN snapshot {snapshot_id} -> {out}")
    for k in tables:
        print(f"  {k}: {len(tables[k])} rows, sha {hashes[k][:12]}")


if __name__ == "__main__":
    main()
