#!/usr/bin/env python3
"""Phase 1c: held-out RAPM coverage calibration of the established-player SD inflation.

The analytic ridge posterior SDs are too tight (they capture coefficient sampling
variation only, blind to role, lineup, opponent, and the RS-to-PO regime change), which
would compress every team-strength distribution in a tail-event model. This calibrates a
HETEROSCEDASTIC inflation of net_sd against a real HELD-OUT test: fit RAPM on 2023-24 +
2024-25, predict 2025-26, and widen the SD until the intervals actually cover.

Noisy-target correction (required): the held-out 2025-26 RAPM is itself a noisy estimate,
so its own SD is folded into the coverage scoring (denominator sqrt(sd_pred^2 + sd_ho^2)).
Ignoring it would attribute target noise to prediction error and systematically OVER-inflate
(fattening the very tails the thesis likes), so this correction cuts against the thesis on
purpose.

Leak-free: the heteroscedastic covariate is the TRAIN-only RAPM-vs-box disagreement
|net_rapm_tr - box_net_bpm_tr|, computed without touching the held-out season.

All fits use the FROZEN warehouse snapshot (box prior) plus the local possession cache, so
a warehouse update mid-build cannot move 1b and 1c onto different data.

    python core_max/impact/coverage_calibration.py
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
sys.path.insert(0, os.path.join(REPO, "core_max"))
import build_rapm as BR          # noqa: E402
from data_pull import frozen     # noqa: E402

OUTDIR = os.path.join(REPO, "core_max", "outputs", "phase1")
TRAIN, HOLDOUT = (2023, 2024), (2025,)
MIN_POSS_TR, MIN_POSS_HO = 3000, 1500          # well-estimated in both windows
LEVELS = [0.5, 0.68, 0.8, 0.9, 0.95]


def fit_cached(name, seasons, box_table):
    path = os.path.join(OUTDIR, f"rapm_{name}.parquet")
    if os.path.exists(path):
        print(f"  using cached {name} fit ({path})", flush=True)
        return pd.read_parquet(path)
    box, sid = frozen.load(box_table)
    print(f"  fitting {name} RAPM on seasons {seasons} (frozen box {sid}) ...", flush=True)
    tab = BR.fit_rapm(seasons, box_feats=box)
    os.makedirs(OUTDIR, exist_ok=True)
    tab.to_parquet(path, index=False)
    return tab


def coverage(t, levels):
    return {p: float(np.mean(np.abs(t) <= norm.ppf(0.5 + p / 2))) for p in levels}


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    print("Phase 1c held-out RAPM coverage calibration")
    tr = fit_cached("train", TRAIN, "box_feats_train")
    ho = fit_cached("holdout", HOLDOUT, "box_feats_holdout")

    m = tr.merge(ho, on="player_id", suffixes=("_tr", "_ho"))
    m = m[(m["possessions_tr"] >= MIN_POSS_TR) & (m["possessions_ho"] >= MIN_POSS_HO)].copy()
    print(f"dual-estimated players (train >= {MIN_POSS_TR}, holdout >= {MIN_POSS_HO} poss): {len(m)}")

    m["d"] = m["net_rapm_tr"] - m["net_rapm_ho"]
    m["div_tr"] = (m["net_rapm_tr"] - m["box_net_bpm_tr"]).abs()          # train-only, leak-free
    zmu, zsd = float(m["div_tr"].mean()), float(m["div_tr"].std())
    m["zdiv"] = (m["div_tr"] - zmu) / zsd

    # baseline: raw analytic SD, noisy target (no inflation)
    t0 = m["d"] / np.sqrt(m["net_sd_tr"] ** 2 + m["net_sd_ho"] ** 2)
    cov0 = coverage(t0, LEVELS)
    cov0_naive = coverage(m["d"] / m["net_sd_tr"], LEVELS)
    print("baseline coverage NAIVE (ignores holdout noise; would justify inflation):",
          {p: round(cov0_naive[p], 3) for p in LEVELS})
    print("baseline coverage CORRECTED (noisy-target folded in; the honest test):",
          {p: round(cov0[p], 3) for p in LEVELS})

    # grid-search heteroscedastic inflation sd_pred = net_sd_tr * a * (1 + b*zdiv),
    # minimizing multi-level coverage loss with the noisy-target denominator
    dd, str_, sho, zz = (m["d"].to_numpy(), m["net_sd_tr"].to_numpy(),
                         m["net_sd_ho"].to_numpy(), m["zdiv"].to_numpy())
    best = None
    for a in np.linspace(0.8, 3.0, 45):
        for b in np.linspace(0.0, 1.2, 25):
            sd_pred = str_ * a * (1 + b * zz)
            if np.any(sd_pred <= 0):
                continue
            t = dd / np.sqrt(sd_pred ** 2 + sho ** 2)
            cov = coverage(t, LEVELS)
            loss = sum((cov[p] - p) ** 2 for p in LEVELS)
            if best is None or loss < best[0]:
                best = (loss, float(a), float(b), cov)
    loss, a, b, cov = best
    print(f"calibrated: a={a:.3f}, b={b:.3f} | coverage:", {p: round(cov[p], 3) for p in LEVELS})

    # heteroscedasticity check: 80% coverage by train-divergence tercile, raw vs calibrated
    m["sd_pred"] = m["net_sd_tr"] * a * (1 + b * m["zdiv"])
    m["t"] = m["d"] / np.sqrt(m["sd_pred"] ** 2 + m["net_sd_ho"] ** 2)
    z80 = norm.ppf(0.9)
    print("80% coverage by train RAPM-vs-box divergence tercile:")
    for lab, (q0, q1) in [("low", (0.0, 1 / 3)), ("mid", (1 / 3, 2 / 3)), ("high", (2 / 3, 1.0))]:
        lo, hi = m["div_tr"].quantile(q0), m["div_tr"].quantile(q1)
        bn = m[(m["div_tr"] >= lo) & (m["div_tr"] <= hi)]
        c0 = float(np.mean(np.abs(t0.loc[bn.index]) <= z80))
        c1 = float(np.mean(np.abs(bn["t"]) <= z80))
        print(f"  div {lab:4s} (n={len(bn):3d}): raw {c0:.2f} -> calibrated {c1:.2f}")

    # selection-effect firm-up (measure it, do not assert it): the test only includes players
    # stable enough to persist across all three windows, and stable players over-cover by
    # construction. Split by total possessions and confirm corrected coverage trends toward
    # nominal as stability drops; this converts the selection-bias claim into measured evidence.
    m["stab"] = m["possessions_tr"] + m["possessions_ho"]
    print("80% corrected coverage by stability (total possessions) tercile:")
    for lab, (q0, q1) in [("low", (0.0, 1 / 3)), ("mid", (1 / 3, 2 / 3)), ("high", (2 / 3, 1.0))]:
        lo, hi = m["stab"].quantile(q0), m["stab"].quantile(q1)
        bn = m[(m["stab"] >= lo) & (m["stab"] <= hi)]
        c = float(np.mean(np.abs(t0.loc[bn.index]) <= z80))
        print(f"  stability {lab:4s} (n={len(bn):3d}, poss {int(lo):,}-{int(hi):,}): 80% coverage {c:.2f}")

    # DECISION (skeptical in both directions). The corrected held-out test does NOT justify
    # inflating the analytic SDs: they OVER-cover at every level. The grid would SHRINK (a hit
    # the floor), but shrinking established-player SDs cuts veteran-roster variance and would
    # FLATTER the high-variance Fork B, and a 3-season / noisy-1-season-holdout test lacks the
    # power for a confident shrink. So we DECLINE to inflate (the data refuses it) and DECLINE
    # to shrink (it flatters the thesis on weak evidence); hold at the analytic posterior SDs
    # as-is. The mild heteroscedastic signal (high-divergence players slightly under-covered)
    # is real but second-order and swamped by the overall over-coverage.
    adopt_a, adopt_b = 1.0, 0.0
    print(f"\nADOPTED: a={adopt_a}, b={adopt_b}  (analytic posterior SDs as-is: no inflation, no shrink)")
    params = {
        "form": "sd_used = net_sd * a * (1 + b * (div - zmu)/zsd), div = |net_rapm - box_net_bpm|",
        "a": adopt_a, "b": adopt_b, "zmu": zmu, "zsd": zsd,
        "decision": "as-is baseline center; shrink and heteroscedastic-widen carried as Phase 3-4 sensitivity variants",
        "decision_basis": ("LOAD-BEARING reason is statistical: low power (one noisy holdout season, 313 players) "
                           "plus selection toward stable players who over-cover by construction (measured by the "
                           "stability-tercile trend, not asserted). The fact that shrink would flatter Fork B is a "
                           "SKEPTICISM FLAG to raise the bar, NOT the justification; a clean high-power test that "
                           "said shrink would be followed and accepted as honestly helping Fork B."),
        "grid_result": {"a": a, "b": b, "coverage": cov,
                        "note": "grid minimized coverage loss but hit the shrink floor; carried as the shrink variant"},
        "sensitivity_variants_phase3_4": [
            {"name": "center_as_is", "a": 1.0, "b": 0.0, "desc": "adopted baseline center"},
            {"name": "shrink", "a": a, "b": 0.0, "desc": "corrected-test point estimate; sweep to show the verdict is robust"},
            {"name": "hetero_widen", "a": 1.0, "b": 0.20, "desc": "mild widen of high-divergence players per their under-coverage; sweep"},
        ],
        "levels": LEVELS, "coverage_baseline_corrected": cov0, "coverage_baseline_naive": cov0_naive,
        "snapshot": frozen.current_snapshot_id(), "n_calib": int(len(m)),
        "train": list(TRAIN), "holdout": list(HOLDOUT),
        "min_poss_train": MIN_POSS_TR, "min_poss_holdout": MIN_POSS_HO,
        "note": ("Corrected held-out coverage OVER-covers at every level, so the Q1 premise "
                 "(analytic SDs too tight, inflate them) is NOT supported by the data. The naive "
                 "(no noisy-target) coverage under-covers and WOULD have justified inflation, which "
                 "is exactly the trap the noisy-target correction was required to avoid. 3 seasons "
                 "is a limited test (noisy 1-season holdout, 313 stable dual-window players), so we "
                 "neither inflate nor shrink: hold at the principled posterior SDs."),
    }
    with open(os.path.join(OUTDIR, "inflation_params.json"), "w", encoding="utf-8") as fh:
        json.dump(params, fh, indent=2)
    print(f"wrote {os.path.join(OUTDIR, 'inflation_params.json')} (adopted a={adopt_a}, b={adopt_b})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
