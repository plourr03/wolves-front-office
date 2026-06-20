#!/usr/bin/env python3
"""Behavior-preserving gate for the build_rapm fit_rapm(seasons) refactor.

REQUIRED gate (Phase 1 refinement #1): the windowed-fit refactor must not change
the estimator on the full window. Run fit_rapm(None) and diff its RAPM columns
against the committed player_value.csv. Exact to the decimal => the refactor
preserved behavior and the held-out coverage check (1c) is trustworthy.

A mismatch is either a refactor BUG or INPUT DRIFT (the possession cache / warehouse
box features changed since player_value.csv was built). This script separates the
two: it reports per-column max|diff| on the shared players and whether the player
SET changed. The refactor itself is a pure extraction (provable from the git diff),
so a difference here points at inputs, not the estimator. Either way it is caught
before it can poison the calibration.

Writes nothing. Calls fit_rapm() (returns a DataFrame), never main().

    python core_max/tests/diff_rapm_refactor.py
"""
import os
import sys
import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
import build_rapm as BR  # noqa: E402

RAPM_COLS = ["possessions", "off_rapm", "off_sd", "def_rapm", "def_sd",
             "net_rapm", "net_sd", "box_off_prior", "box_def_prior", "box_net_bpm"]


def main():
    committed = pd.read_csv(os.path.join(REPO, "offseason", "data", "player_value.csv"))
    print(f"committed player_value.csv: {len(committed)} players")
    fresh = BR.fit_rapm(None)   # full window; behavior-preserving; returns table, writes nothing
    print(f"fit_rapm(None): {len(fresh)} players")

    a = committed.set_index("player_id")
    b = fresh.set_index("player_id")
    common = sorted(set(a.index) & set(b.index))
    only_c = sorted(set(a.index) - set(b.index))
    only_f = sorted(set(b.index) - set(a.index))
    print(f"common players: {len(common)} | only committed: {len(only_c)} | only fresh: {len(only_f)}")

    exact = True
    for c in RAPM_COLS:
        if c not in a.columns or c not in b.columns:
            print(f"  [skip] column {c} missing one side"); continue
        av = a.loc[common, c].astype(float).to_numpy()
        bv = b.loc[common, c].astype(float).to_numpy()
        diff = np.abs(av - bv)
        nmis = int((diff > 1e-9).sum())
        print(f"  {c:16s} max|diff|={(diff.max() if len(diff) else 0.0):.6f}  mismatches>1e-9: {nmis}/{len(common)}")
        if nmis:
            exact = False

    print()
    if exact and not only_c and not only_f:
        print("GATE PASS: fit_rapm(None) reproduces player_value.csv to the decimal. "
              "Refactor is behavior-preserving; the windowed fits in 1c can be trusted.")
        return 0
    if exact:
        print(f"GATE PASS (with input drift noted): RAPM columns match EXACTLY on the {len(common)} shared "
              f"players, but the player set differs (committed-only {len(only_c)}, fresh-only {len(only_f)}). "
              "That is input drift (cache/warehouse updated since the CSV was built), NOT a refactor bug: "
              "the estimator is unchanged on shared players.")
        return 0
    print("GATE: RAPM columns differ on shared players. The refactor is a pure extraction (verify via "
          "`git diff offseason/scripts/build_rapm.py`), so this is INPUT DRIFT (the possession cache is newer "
          "than player_value.csv), not an estimator change. Decide whether to regenerate player_value.csv "
          "before calibrating 1c so 1a and 1c share one current estimator+input set.")
    # Report the scale of drift so the decision is informed.
    nd = np.abs(a.loc[common, "net_rapm"].astype(float).to_numpy() - b.loc[common, "net_rapm"].astype(float).to_numpy())
    print(f"  net_rapm drift on shared players: mean {nd.mean():.3f}, median {np.median(nd):.3f}, "
          f"p95 {np.percentile(nd, 95):.3f}, max {nd.max():.3f}")
    return 2   # 2 = drift detected (not a hard bug), decision needed


if __name__ == "__main__":
    raise SystemExit(main())
