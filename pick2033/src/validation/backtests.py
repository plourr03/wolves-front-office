"""Gates 8.1: rolling-origin backtests for Model A.

For each origin T in 1995..2019: fit on seasons <= T (cached per key),
simulate 7 seasons forward from the observed T states, score against realized
SRS at every horizon:

  - CRPS (empirical, from 4,000 posterior-predictive paths)
  - 80% predictive-interval coverage  (gate: within [72%, 88%] at every horizon)
  - skill at horizon 7 (gate: CRPS beats BOTH baselines)
      baseline 1  persistence: point forecast srs_T (CRPS of a point = MAE)
      baseline 2  pooled mean-reversion: OLS srs_{t+1} = a + b srs_t on the
                  training panel, iterated analytically, Gaussian CRPS
  - dispersion sanity (gate: simulated cross-sectional SD of season wins
    within 15% of historical SD), via the fresh SRS->wins fit

Scoring only covers (franchise, T, h) cells where both srs_T and realized
srs_{T+h} exist (expansion entries and the CHA 2003-04 gap drop out).

Writes outputs/validation/model_a_backtests.md + backtest_scores.parquet.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from src.models.trajectory import fit, forecast_paths, load_panel, load_params
from src.sim.strength_blend import fit_srs_to_wins, wins_from_srs

OUT = PROJECT_ROOT / "outputs" / "validation"
ORIGINS = range(1995, 2020)
HORIZONS = 7
N_PATHS = 4000


def empirical_crps(samples: np.ndarray, y: float) -> float:
    """CRPS via the sorted-sample estimator: E|X-y| - 0.5 E|X-X'|."""
    x = np.sort(samples)
    n = len(x)
    term1 = np.abs(x - y).mean()
    # E|X-X'| = 2/n^2 * sum_i (2i - n + 1... use pairwise via sorted identity
    i = np.arange(1, n + 1)
    term2 = 2.0 / (n * n) * np.sum((2 * i - n - 1) * x)
    return float(term1 - 0.5 * term2)


def gaussian_crps(mean: float, sd: float, y: float) -> float:
    from scipy.stats import norm
    z = (y - mean) / sd
    return float(sd * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi)))


def pooled_ar1(panel: pd.DataFrame) -> tuple[float, float, float]:
    """OLS srs_{t+1} = a + b srs_t on contiguous pairs of the training panel."""
    prev, curr = [], []
    for _, g in panel.groupby("franchise_id"):
        g = g.sort_values("season")
        s, v = g.season.values, g.srs.values
        m = s[1:] == s[:-1] + 1
        prev.extend(v[:-1][m])
        curr.extend(v[1:][m])
    prev, curr = np.array(prev), np.array(curr)
    b, a = np.polyfit(prev, curr, 1)
    resid_sd = float((curr - (a + b * prev)).std(ddof=2))
    return float(a), float(b), resid_sd


def pooled_forecast(a: float, b: float, resid_sd: float, srs_T: float, h: int):
    mu_inf = a / (1 - b)
    mean = mu_inf + (b ** h) * (srs_T - mu_inf)
    var = resid_sd ** 2 * (1 - b ** (2 * h)) / (1 - b ** 2)
    return mean, float(np.sqrt(var))


def run_origin(T: int, full_panel: pd.DataFrame, seed: int) -> list[dict]:
    post, fr_ids, _ = fit(through=T, quiet=True)
    train = full_panel[full_panel.season <= T]
    a, b, rsd = pooled_ar1(train)
    start = train[train.season == T].set_index("franchise_id").srs.to_dict()
    present = [f for f in fr_ids if f in start]
    paths = forecast_paths(post, fr_ids, start, HORIZONS, N_PATHS, seed + T)
    realized = full_panel.set_index(["franchise_id", "season"]).srs
    rows = []
    for h in range(1, HORIZONS + 1):
        for j, f in enumerate(present):
            key = (f, T + h)
            if key not in realized.index:
                continue
            y = float(realized.loc[key])
            s = paths[:, h - 1, j]
            lo, hi = np.percentile(s, [10, 90])
            pm, psd = pooled_forecast(a, b, rsd, start[f], h)
            rows.append({
                "origin": T, "franchise_id": f, "horizon": h, "realized": y,
                "crps_model": empirical_crps(s, y),
                "crps_persistence": abs(y - start[f]),
                "crps_pooled": gaussian_crps(pm, psd, y),
                "covered_80": bool(lo <= y <= hi),
            })
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    params = load_params()
    full_panel = load_panel()
    all_rows = []
    for T in ORIGINS:
        rows = run_origin(T, full_panel, params["seed"])
        all_rows.extend(rows)
        print(f"origin {T}: {len(rows)} cells", flush=True)
    df = pd.DataFrame(all_rows)
    df.to_parquet(OUT / "backtest_scores.parquet", index=False)

    by_h = df.groupby("horizon").agg(
        crps_model=("crps_model", "mean"),
        crps_persistence=("crps_persistence", "mean"),
        crps_pooled=("crps_pooled", "mean"),
        coverage_80=("covered_80", "mean"),
        n=("covered_80", "size"))
    cov_ok = by_h.coverage_80.between(0.72, 0.88).all()
    h7 = by_h.loc[7]
    skill_ok = (h7.crps_model < h7.crps_persistence) and (h7.crps_model < h7.crps_pooled)

    # dispersion sanity: simulate one league-season step from every historical
    # season's states, compare cross-sectional SD of wins to history
    post, fr_ids, _ = fit(quiet=True)
    rng = np.random.default_rng(params["seed"] + 999)
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    wins_panel = con.execute(
        "SELECT franchise_id, season, win_pct FROM franchise_seasons").fetchdf()
    con.close()
    sim_sds, hist_sds = [], []
    for T in range(1985, 2026):
        start = full_panel[full_panel.season == T].set_index("franchise_id").srs.to_dict()
        nxt = wins_panel[wins_panel.season == T + 1]
        if len(nxt) < 20 or len(start) < 20:
            continue
        paths = forecast_paths(post, fr_ids, start, 1, 400, params["seed"] + 7000 + T)
        wins = wins_from_srs(paths[:, 0, :], rng=rng, season_noise=True)
        sim_sds.append(wins.std(axis=1, ddof=1).mean())
        hist_sds.append((nxt.win_pct * 82).std(ddof=1))
    sim_sd, hist_sd = float(np.mean(sim_sds)), float(np.mean(hist_sds))
    disp_ok = abs(sim_sd - hist_sd) / hist_sd <= 0.15

    lines = [
        "# Model A rolling-origin backtests (gates 8.1)",
        f"origins {ORIGINS.start}-{ORIGINS.stop - 1}, horizons 1-7, "
        f"{len(df)} scored cells, {N_PATHS} paths/forecast\n",
        by_h.round(3).to_markdown(),
        "",
        f"- coverage gate (80% PI in [72,88] all horizons): **{'PASS' if cov_ok else 'FAIL'}**",
        f"- skill gate at h=7 (model {h7.crps_model:.3f} < persistence "
        f"{h7.crps_persistence:.3f} and pooled {h7.crps_pooled:.3f}): "
        f"**{'PASS' if skill_ok else 'FAIL'}**",
        f"- dispersion gate (sim wins SD {sim_sd:.2f} vs hist {hist_sd:.2f}, "
        f"within 15%): **{'PASS' if disp_ok else 'FAIL'}**",
    ]
    report = "\n".join(lines)
    (OUT / "model_a_backtests.md").write_text(report, encoding="utf-8")
    print("\n" + report)
    sys.exit(0 if (cov_ok and skill_ok and disp_ok) else 1)


if __name__ == "__main__":
    main()
