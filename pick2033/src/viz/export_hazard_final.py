"""edwards_hazard FINAL export (July-6 step-4 wiring gap, closed 2026-07-12).

The provisional edwards_hazard JSON is written by hazard.main(); run_m2()
writes the gate report and Engine D stats but no curves export. This script
produces edwards_hazard_FINAL.json from the CACHED m2_full posterior --
never refits, and never re-calls run_m2() (a cache-hit rerun would clobber
the recorded r_hats in model_b_hazard_M2_FINAL.md with NaNs).

Covariate construction mirrors Engine D exactly: provisional Edwards path
(edwards_path) plus contract_z/contract_known from the verified STARS
contract path (2/1/0, 2029 walk year, post-walk reset 4), standardized with
the cyr stats the M2 fit wrote to hazard_m2_stats.json.

No borderline_sensitivity block: the 13 borderline prunes are already
baked into the FINAL freeze the m2_full posterior was fit on.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.models.hazard import M2_FINAL_SPEC, edwards_path  # noqa: E402
from src.sim.league_sim import STARS, contract_years_for  # noqa: E402

POSTERIORS = PROJECT_ROOT / "outputs" / "posteriors"
STAGED = PROJECT_ROOT / "data" / "staged"
OUT_JSON = PROJECT_ROOT / "outputs" / "json"


def load_m2_posterior() -> pd.DataFrame:
    files = sorted(POSTERIORS.glob("hazard_m2_full_*.parquet"))
    if not files:
        raise RuntimeError("no cached m2_full posterior; run the M2 refit "
                           "(python -m src.models.hazard --m2) first")
    return pd.read_parquet(files[-1])


def m2_edwards_curves(post: pd.DataFrame, stats: dict, scenario_win: float) -> dict:
    path = edwards_path(stats, scenario_win)
    edwards = next(s for s in STARS["MIN"] if s["player"] == "Anthony Edwards")
    cyr = np.array([contract_years_for(edwards, int(s)) for s in path.season],
                   dtype=float)
    path["contract_z"] = (cyr - stats["cyr_mean"]) / stats["cyr_sd"]
    path["contract_known"] = 1.0
    covars = M2_FINAL_SPEC["covariates"]
    b = post[[f"b_{c}" for c in covars]].values
    logits = (post.b0.values[:, None] + b @ path[covars].values.T
              + post["u_era_3"].values[:, None])
    h_draws = 1 / (1 + np.exp(-logits))
    surv = np.cumprod(1 - h_draws, axis=1)
    cum = 1 - surv
    q = lambda a, lo, hi: (np.percentile(a, lo, axis=0), np.percentile(a, hi, axis=0))
    ann_lo, ann_hi = q(h_draws, 10, 90)
    cum_lo, cum_hi = q(cum, 10, 90)
    return {
        "scenario_team_win_pct_2yr": scenario_win,
        "contract_years_remaining_path": {int(s): int(c)
                                          for s, c in zip(path.season, cyr)},
        "annual": [{"season": int(s), "hazard_mean": float(h_draws[:, i].mean()),
                    "lo80": float(ann_lo[i]), "hi80": float(ann_hi[i])}
                   for i, s in enumerate(path.season)],
        "cumulative": [{"season": int(s), "p_departed_by_mean": float(cum[:, i].mean()),
                        "lo80": float(cum_lo[i]), "hi80": float(cum_hi[i])}
                       for i, s in enumerate(path.season)],
    }


if __name__ == "__main__":
    post = load_m2_posterior()
    stats = json.loads((POSTERIORS / "hazard_m2_stats.json").read_text())
    freeze = json.loads((STAGED / "star_spells_final.meta.json").read_text())
    curves = {
        "tag": "FINAL",
        "freeze_hash": freeze["freeze_hash"],
        "contract_covariate": ("INCLUDED (M2_FINAL_SPEC: contract_z + "
                               "contract_known, 99.5%-coverage backfill)"),
        "scenarios": {
            "central_win60": m2_edwards_curves(post, stats, 0.60),
            "decline_win45": m2_edwards_curves(post, stats, 0.45),
        },
    }
    OUT_JSON.mkdir(parents=True, exist_ok=True)
    (OUT_JSON / "edwards_hazard_FINAL.json").write_text(json.dumps(curves, indent=1))
    c = curves["scenarios"]["central_win60"]["cumulative"]
    print(f"edwards_hazard_FINAL: P(departed by 2033) central "
          f"{c[-1]['p_departed_by_mean']:.3f} [{c[-1]['lo80']:.3f}, {c[-1]['hi80']:.3f}]")
