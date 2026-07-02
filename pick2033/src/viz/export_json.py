"""Viz JSON exports (spec Section 11). Every file carries a meta block
(seed, data hashes, code version, timestamp, tag). While any input is
provisional, filenames carry _PROVISIONAL and meta.tag = PROVISIONAL.

Gate-ruling condition (2026-07-01): equity outputs emit ONLY deltas plus a
gate_note; never an absolute P(title) level.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
SIMS = PROJECT_ROOT / "outputs" / "sims"
OUT = PROJECT_ROOT / "outputs" / "json"

GATE_NOTE = ("Absolute title probabilities are gated (LaMelo clean-room "
             "convention); equity figures are CRN-paired deltas only.")


def sim_artifact(prefix: str, variant: str) -> tuple:
    """Prefer FINAL artifacts when they exist; fall back to PROVISIONAL.
    Returns (path, tag)."""
    final = SIMS / f"{prefix}_{variant}_FINAL.npz"
    if final.exists():
        return final, "FINAL"
    return SIMS / f"{prefix}_{variant}_PROVISIONAL.npz", "PROVISIONAL"


def meta(tag="PROVISIONAL", **extra) -> dict:
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True,
                                cwd=PROJECT_ROOT).stdout.strip()
    except OSError:
        commit = "unknown"
    return {"tag": tag, "generated_utc": datetime.now(timezone.utc).isoformat(),
            "code_commit": commit, **extra}


def export_slot_distribution_2033(variant="two_tier"):
    path, tag = sim_artifact("slots", variant)
    z = np.load(path)
    slots, fr_ids = z["slots"], list(z["fr_ids"])
    seasons = list(z["seasons"])
    mi, yi = fr_ids.index("MIN"), seasons.index(2033)
    s2033 = slots[:, yi, mi]
    dist = [{"slot": k, "p": float((s2033 == k).mean())} for k in range(1, 31)]
    payload = {
        "meta": meta(tag=tag, variant=variant, n_paths=int(slots.shape[0]),
                     note="MIN 2033 first (conveys to CHA outright)"),
        "slots": dist,
        "p_top4": float((s2033 <= 4).mean()),
        "p_top10": float((s2033 <= 10).mean()),
        "p_lottery": float((s2033 <= 16).mean()),
        "lottery_definition": "post-2026 reform: 16 drawn picks",
    }
    if "dep_Anthony_Edwards" in z:
        dep = z["dep_Anthony_Edwards"].astype(bool)
        payload["conditional"] = {
            "edwards_stays": {
                "p_top4": float((s2033[~dep] <= 4).mean()),
                "p_top10": float((s2033[~dep] <= 10).mean()),
                "p_lottery": float((s2033[~dep] <= 16).mean()),
                "n_paths": int((~dep).sum()),
            },
            "edwards_departs": {
                "p_top4": float((s2033[dep] <= 4).mean()),
                "p_top10": float((s2033[dep] <= 10).mean()),
                "p_lottery": float((s2033[dep] <= 16).mean()),
                "n_paths": int(dep.sum()),
            },
        }
    (OUT / f"slot_distribution_2033_{tag}.json").write_text(json.dumps(payload, indent=1))
    return payload


def export_win_fancharts(variant="two_tier"):
    path, tag = sim_artifact("winpct", variant)
    z = np.load(path)
    wpct, fr_ids = z["winpct"], list(z["fr_ids"])
    seasons = list(range(2027, 2034))
    payload = {"meta": meta(tag=tag, variant=variant, n_paths=int(wpct.shape[0]))}
    for team in ("MIN", "CHA"):
        ti = fr_ids.index(team)
        rows = []
        for si, season in enumerate(seasons):
            w = wpct[:, si, ti] * 82
            q = np.percentile(w, [5, 20, 50, 80, 95])
            rows.append({"season": season, "q05": round(float(q[0]), 1),
                         "q20": round(float(q[1]), 1), "q50": round(float(q[2]), 1),
                         "q80": round(float(q[3]), 1), "q95": round(float(q[4]), 1)})
        payload[team] = rows
    (OUT / f"win_fancharts_{tag}.json").write_text(json.dumps(payload, indent=1))
    return payload


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    sd = export_slot_distribution_2033()
    fc = export_win_fancharts()
    print(f"slot_distribution_2033: p_top4 {sd['p_top4']:.3f}, p_top10 {sd['p_top10']:.3f}, "
          f"p_lottery {sd['p_lottery']:.3f}")
    print("MIN 2033 fanchart:", fc["MIN"][-1])
    print("CHA 2033 fanchart:", fc["CHA"][-1])
