"""The July-6 step-5 priced pass: E2 swap pricing on the FINAL Engine D
artifacts, now that trade_terms.yaml: verified_post_july6 is true.

Runs price_all over BOTH top1_carries_to_CHA branches (per trade_terms.yaml:
run both, report both) x BOTH currencies (VORP primary, WS robustness) on
the shipped two_tier variant, and writes outputs/json/swap_pricing_FINAL.json.
E1 slot-value fits come from the posterior cache; the payoff rng seed is
config seed + 7 (recorded in meta).
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.sim.swap_pricing import price_all  # noqa: E402

SIMS = PROJECT_ROOT / "outputs" / "sims"
OUT = PROJECT_ROOT / "outputs" / "json"
VARIANT = "two_tier"


if __name__ == "__main__":
    params = yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())
    seed = params["seed"] + 7
    z = np.load(SIMS / f"slots_{VARIANT}_FINAL.npz")
    w = np.load(SIMS / f"winpct_{VARIANT}_FINAL.npz")
    slots = z["slots"]
    fr_ids = [str(t) for t in z["fr_ids"]]
    seasons = [int(s) for s in z["seasons"]]
    departures = {"Anthony Edwards": z["dep_Anthony_Edwards"].astype(bool)}
    cha_win_2033 = w["winpct"][:, seasons.index(2033), fr_ids.index("CHA")]

    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True,
                                cwd=PROJECT_ROOT).stdout.strip()
    except OSError:
        commit = "unknown"
    payload = {
        "meta": {"tag": "FINAL", "variant": VARIANT,
                 "n_paths": int(slots.shape[0]), "seed": seed,
                 "generated_utc": datetime.now(timezone.utc).isoformat(),
                 "code_commit": commit},
        "runs": {},
    }
    for top1 in (True, False):
        for currency in ("vorp", "ws"):
            rep = price_all(slots, fr_ids, seasons, departures, cha_win_2033,
                            seed, top1_carries_to_CHA=top1, currency=currency)
            payload["runs"][f"top1_{str(top1).lower()}_{currency}"] = rep

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "swap_pricing_FINAL.json").write_text(json.dumps(payload, indent=1))
    base = payload["runs"]["top1_true_vorp"]
    print(f"swap_pricing_FINAL (top1_true, VORP): "
          f"outright 2033 mean {base['outright_2033']['mean']:.2f}, "
          f"total per-path mean {base['total_per_path']['mean']:.2f}")
    for y, s in base["swaps"].items():
        print(f"  swap {y}: p_exercise {s['p_exercise']:.3f}, mean {s['mean']:.2f}")
