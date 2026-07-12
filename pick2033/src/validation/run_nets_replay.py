"""Execute and score the 2013 Celtics-Nets replay (spec 8.5 primary).

Runs the as-of-2013 chain built in historical_replays.run_nets_replay
(fit through 2013, pure-Model-A league sim 2014-2018, pre-2019 weighted
lottery, top-8-per-conference playoffs), then scores the realized BKN pick
slots from config/replay_nets_2013.yaml against the simulated 90%
predictive intervals.

GATE 8.5 STATUS: the pre-declared gate wants 2-of-3 replays (this one, the
2019 PG package, one negative control). Only the 2013 chain is built; this
runner reports the primary replay's verdict and marks the gate PARTIAL.
No silent scope-shrink: the missing replays are named in the output.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.validation.historical_replays import run_nets_replay  # noqa: E402

OUT_JSON = PROJECT_ROOT / "outputs" / "json"
OUT_VAL = PROJECT_ROOT / "outputs" / "validation"

N_PATHS = 20_000


def main():
    t0 = time.time()
    results, present, cfg = run_nets_replay(N_PATHS)
    bi = present.index("BKN")
    realized = {int(k): int(v) for k, v in cfg["realized_outcomes"].items()}

    rows = []
    for season, slot in sorted(realized.items()):
        sims = results[season][:, bi].astype(int)
        lo, hi = int(np.percentile(sims, 5)), int(np.percentile(sims, 95))
        inside = lo <= slot <= hi
        rows.append({
            "season": season,
            "realized_slot": slot,
            "interval_90": [lo, hi],
            "inside": bool(inside),
            "median_slot": float(np.median(sims)),
            "p_slot_leq_realized": float((sims <= slot).mean()),
            "p_top3": float((sims <= 3).mean()),
            "dist_head": {str(k): float((sims == k).mean()) for k in range(1, 11)},
        })
    n_inside = sum(r["inside"] for r in rows)
    replay_pass = n_inside == len(rows)

    payload = {
        "meta": {"tag": "FINAL", "n_paths": N_PATHS, "as_of": str(cfg["as_of"]),
                 "lottery_era": cfg["lottery_era"],
                 "variant": "pure_model_a (declared default; two-tier needs 2013 rosters)",
                 "runtime_s": round(time.time() - t0, 1)},
        "scored": rows,
        "replay_verdict": {"slots_inside_90": f"{n_inside}/{len(rows)}",
                           "pass": bool(replay_pass)},
        "gate_85_status": {
            "status": "PARTIAL",
            "note": ("gate is 2-of-3 replays (2013 primary, 2019 PG secondary, "
                     "negative control); only the 2013 chain is built and run. "
                     "The remaining two replays are open work, not waived."),
            "primary_2013": "PASS" if replay_pass else "FAIL",
        },
    }
    OUT_JSON.mkdir(parents=True, exist_ok=True)
    (OUT_JSON / "replay_nets_2013_FINAL.json").write_text(json.dumps(payload, indent=1))

    lines = ["# 2013 Celtics-Nets replay (spec 8.5 primary) -- FINAL",
             f"- as-of 2013 fit, {N_PATHS} paths, pre-2019 weighted lottery, "
             "pure Model A (declared default)",
             f"- runtime {payload['meta']['runtime_s']}s"]
    for r in rows:
        lines.append(
            f"- {r['season']}: realized {r['realized_slot']}, 90% interval "
            f"{r['interval_90'][0]}-{r['interval_90'][1]}, median {r['median_slot']:.0f} "
            f"-> **{'INSIDE' if r['inside'] else 'OUTSIDE'}** "
            f"(P(slot <= realized) {r['p_slot_leq_realized']:.2f})")
    lines.append(f"- replay verdict: {n_inside}/{len(rows)} inside -> "
                 f"**{'PASS' if replay_pass else 'FAIL'}**")
    lines.append("- gate 8.5: **PARTIAL** (1 of 3 replays built; 2019 PG package "
                 "and the negative control remain open)")
    OUT_VAL.mkdir(parents=True, exist_ok=True)
    (OUT_VAL / "replay_nets_2013_FINAL.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
