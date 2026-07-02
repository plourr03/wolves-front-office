"""ON-1: re-judge the 8.4 preview under the RATIFIED operationalization
(docs/decisions.md): exact win-pct thresholds (.732 / .244, amendment 3),
terminal-horizon band, transient non-increase within 2x MC SE, pooled rates
reported un-gated. Both Model A variants. PROVISIONAL preview -- the real
gate runs at M4 with the full Engine D."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.models.trajectory import fit, forecast_paths, load_panel, load_params
from src.sim.strength_blend import load_srs_to_wins
from src.validation.gates_84 import DISCLOSURE, evaluate_tail_gate, historical_tail_rates

N_PATHS = 10_000


def main():
    params = load_params()
    panel = load_panel()
    start = panel[panel.season == 2026].set_index("franchise_id").srs.to_dict()
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    hist_wpct = con.execute("SELECT win_pct FROM franchise_seasons").fetchdf().win_pct.values
    con.close()
    hist_top, hist_bottom = historical_tail_rates(hist_wpct)
    p = load_srs_to_wins()

    lines = ["# 8.4 preview RE-JUDGED under ratified operationalization (ON-1)",
             f"- historical base rates (win-pct thresholds .732/.244): "
             f"top {hist_top:.4f}, bottom {hist_bottom:.4f}",
             f"- disclosure: {DISCLOSURE}", ""]
    for label, overrides in [("v2_mixture (accepted)", None),
                             ("v1_student_t", {"innovation": "student_t"})]:
        post, fr_ids, _ = fit(quiet=True, variant_overrides=overrides)
        rng = np.random.default_rng(params["seed"] + 84)
        srs = forecast_paths(post, fr_ids, start, 7, N_PATHS, params["seed"] + 84)
        wpct = np.clip(0.5 + p["c"] * srs
                       + rng.normal(0, p["resid_sd_win_pct"], srs.shape), 0.02, 0.98)
        # renormalize league win share per season (equivalent to 1230 wins)
        wpct *= 0.5 / wpct.mean(axis=2, keepdims=True)
        res = evaluate_tail_gate(wpct, hist_wpct)
        lines += [
            f"## {label}",
            f"- terminal (2033): top {res.terminal_top:.4f} vs {res.hist_top:.4f}, "
            f"bottom {res.terminal_bottom:.4f} vs {res.hist_bottom:.4f} -> "
            f"**{'PASS' if res.terminal_pass else 'FAIL'}**",
            f"- transient (non-increasing excess w/in 2x MC SE): "
            f"**{'PASS' if res.transient_pass else 'FAIL'}**",
            f"- yearly top rates 2027-33: {[round(x, 4) for x in res.yearly_top]}",
            f"- pooled (reported, un-gated): top {res.pooled_top:.4f}, "
            f"bottom {res.pooled_bottom:.4f}",
            "",
        ]
    report = "\n".join(lines)
    (PROJECT_ROOT / "outputs" / "validation" / "early_84_rejudged.md").write_text(
        report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
