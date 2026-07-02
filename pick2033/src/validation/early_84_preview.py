"""Early preview of gate 8.4 (tail realism + autocorrelation) under a pure
Model-A league: all 30 franchises simulated 7 seasons from 2026 states,
wins renormalized to 1230. NOT the M4 gate run (no MIN/CHA roster tier, no
lottery consumers) -- an early read on ruling condition 3 (if 8.4 fails at
M4, fallback is v1), so the v1-vs-v2 tail comparison exists before anything
downstream depends on v2.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.models.trajectory import fit, forecast_paths, load_panel, load_params
from src.sim.strength_blend import load_srs_to_wins

N_PATHS = 10_000
HORIZONS = 7


def simulate_wins(post, fr_ids, start, seed):
    p = load_srs_to_wins()
    rng = np.random.default_rng(seed)
    srs = forecast_paths(post, fr_ids, start, HORIZONS, N_PATHS, seed)
    wp = 0.5 + p["c"] * srs + rng.normal(0, p["resid_sd_win_pct"], srs.shape)
    wins = np.clip(wp, 0.02, 0.98) * 82
    wins *= 1230.0 / wins.sum(axis=2, keepdims=True)
    assert np.allclose(wins.sum(axis=2), 1230.0), "conservation violated"
    return wins


def tail_rates(wins):
    return float((wins >= 60).mean()), float((wins <= 20).mean())


def autocorr(wins, lag):
    a = wins[:, :-lag, :].ravel()
    b = wins[:, lag:, :].ravel()
    return float(np.corrcoef(a, b)[0, 1])


def main():
    params = load_params()
    panel = load_panel()
    start = panel[panel.season == 2026].set_index("franchise_id").srs.to_dict()

    hist_wins = None
    import duckdb
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    fs = con.execute("SELECT franchise_id, season, win_pct*82 AS w FROM franchise_seasons").fetchdf()
    con.close()
    hist_hi = float((fs.w >= 60).mean())
    hist_lo = float((fs.w <= 20).mean())
    hist_ac = {}
    for lag in (1, 2, 3):
        pairs = fs.merge(fs.assign(season=fs.season + lag), on=["franchise_id", "season"],
                         suffixes=("_b", "_a"))
        hist_ac[lag] = float(np.corrcoef(pairs.w_a, pairs.w_b)[0, 1])

    lines = ["# Early 8.4 preview (pure Model-A league, 2027-2033, 10k paths)",
             f"historical: P(60+W) {hist_hi:.4f}  P(<=20W) {hist_lo:.4f}  "
             f"autocorr l1/l2/l3 {hist_ac[1]:.3f}/{hist_ac[2]:.3f}/{hist_ac[3]:.3f}", ""]
    for label, overrides in [("v2_mixture (accepted)", None),
                             ("v1_student_t (fallback)", {"innovation": "student_t"})]:
        post, fr_ids, _ = fit(quiet=True, variant_overrides=overrides)
        wins = simulate_wins(post, fr_ids, start, params["seed"] + 84)
        hi, lo = tail_rates(wins)
        acs = {lag: autocorr(wins, lag) for lag in (1, 2, 3)}
        hi_ok = abs(hi - hist_hi) / hist_hi <= 0.25
        lo_ok = abs(lo - hist_lo) / hist_lo <= 0.25
        lines.append(
            f"- **{label}**: P(60+W) {hi:.4f} ({'ok' if hi_ok else 'OUT'}), "
            f"P(<=20W) {lo:.4f} ({'ok' if lo_ok else 'OUT'}), "
            f"autocorr {acs[1]:.3f}/{acs[2]:.3f}/{acs[3]:.3f}")
    report = "\n".join(lines)
    (PROJECT_ROOT / "outputs" / "validation" / "early_84_preview.md").write_text(
        report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
