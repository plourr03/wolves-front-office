"""
Per-season outcome DISTRIBUTION for MIN (post-trade), straight out of the same
20,000-season engine the title number uses. The slide draws TRUE BARS from this,
not an illustrated curve.

What it is: each simulated season the engine draws MIN's playoff strength once as
  playoff_net = base_net + N(0, sigma_t)            (bracket_sim.simulate_league, line ~183)
and the whole bracket turns on that draw. We reproduce that exact draw (same params:
sigma_unobs, MIN's method-uncertainty, posterior sd) for 20,000 seasons and bin it.
The shape is the genuine, lumpy model output.

The green DREAM tail is tied to MIN's ACTUAL simulated reach-CF rate from a full bracket run,
so the green AREA equals how often the model has them reaching the conference finals:
  THE DREAM  = the top reach-CF share of seasons     (green; the real deep-run rate, ~17%)
  A WASH     = the central band, the most likely outcome (a normal playoff team; the trade ~a wash)
  IT GETS WORSE = the lower tail of the outcome range  (a clearly below-par season)
The worse/wash divider marks the lower third of the outcome distribution (the genuinely
disappointing seasons) vs the central band; only the green cut is pinned to an exact model rate.

Both metric forks are run and averaged; the single-season noise (sigma_t ~ 5.5) dwarfs the
fork gap in MIN's net (2.18 vs 3.01), so the shape is fork-invariant. Writes season_hist.json.

    python season_distribution.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "offseason" / "scripts"))
import build_team_ratings as A   # noqa: E402
import bracket_sim as E          # noqa: E402

OUT = REPO / "lamelo" / "data" / "sim"
imp_df = pd.read_csv(REPO / "lamelo" / "data" / "impact" / "player_impact.csv")
ts = json.loads((REPO / "lamelo" / "data" / "impact" / "team_strength.json").read_text())
EP = E.load_e_params()
BETA = float(EP["beta"])
N = 20000
NBINS = 30


def make_imp(fork):
    imp = {}
    for _, r in imp_df.iterrows():
        pid = str(int(r.player_id))
        if fork == "rapm":
            off, dff = float(r.off_rapm), float(r.def_rapm)
        else:
            off, dff = float(r.box_off_prior), float(r.box_def_prior)
        imp[pid] = {"off": off, "def": dff, "off_sd": float(r.off_sd), "def_sd": float(r.def_sd),
                    "def_div": abs(float(r.def_rapm) - float(r.box_def_prior)), "read": ""}
    return imp


def run_fork(fork):
    """Full bracket run for MIN post-trade. Returns (post_net, munc, net_sd, outcome rates)."""
    imp = make_imp(fork)
    strengths = E.build_2026_27_league(imp)
    min_pre = float(strengths["MIN"]["net"])
    raw_delta = float(ts["forks"][fork]["trade_delta_raw"])
    post = min_pre + BETA * raw_delta
    strengths["MIN"]["net"] = post
    munc = float(strengths["MIN"].get("munc", 0.0))
    net_sd = float(strengths["MIN"].get("net_sd", 0.0))
    r = E.simulate_league(strengths, n_sims=N, seed=1, use_overlay=True)["teams"]["MIN"]
    return {"post_net": post, "munc": munc, "net_sd": net_sd,
            "title": r["title"], "finals": r["finals"], "cf": r["cf"], "r2": r["r2"]}


def main():
    forks = {f: run_fork(f) for f in ("rapm", "box")}
    for f, v in forks.items():
        print(f"[{f:4}] net {v['post_net']:+.2f}  title {v['title']*100:.2f}%  "
              f"reach-CF {v['cf']*100:.1f}%  reach-R2 {v['r2']*100:.1f}%")

    avg = {k: float(np.mean([forks[f][k] for f in forks]))
           for k in ("post_net", "munc", "net_sd", "title", "finals", "cf", "r2")}
    # per-season playoff-strength sigma, exactly as the engine forms it (bracket_sim line ~157)
    sigma_t = float(np.sqrt(EP["sigma_unobs"] ** 2 + (EP["munc_w"] * avg["munc"]) ** 2
                            + (0.15 * avg["net_sd"]) ** 2))
    mean = avg["post_net"]

    rng = np.random.default_rng(1)
    draws = mean + rng.normal(0.0, sigma_t, N)        # the genuine per-season draw, reproduced
    lo, hi = mean - 3.5 * sigma_t, mean + 3.5 * sigma_t
    counts, edges = np.histogram(draws, bins=NBINS, range=(lo, hi))  # ~0.05% beyond +-3.5sd, dropped
    counts = counts.astype(int)

    # green DREAM cut pinned to the model reach-CF rate (green area == reach-CF); worse/wash
    # cut at the lower third of the outcome range (the clearly below-par seasons)
    P_WORSE = 0.30
    worse_x = float(np.quantile(draws, P_WORSE))
    dream_x = float(np.quantile(draws, 1.0 - avg["cf"]))

    out = {
        "n_sims": N, "nbins": NBINS, "seed": 1, "source": "bracket_sim 20,000-season engine",
        "note": "MIN post-trade single-season playoff-strength draw, reproduced from the engine "
                "(base_net + N(0, sigma_t)); green DREAM cut pinned to the model reach-CF rate, "
                "worse/wash cut at the lower third of the outcome range.",
        "mean_net": round(mean, 3), "sigma_t": round(sigma_t, 3),
        "bin_edges": [round(float(e), 4) for e in edges],
        "counts": counts.tolist(),
        "worse_x": round(worse_x, 4), "dream_x": round(dream_x, 4),
        "p_worse": round(P_WORSE, 4), "p_wash": round(1.0 - P_WORSE - avg["cf"], 4),
        "p_dream": round(avg["cf"], 4),
        "rates_avg": {k: round(avg[k], 5) for k in ("title", "finals", "cf", "r2")},
        "forks": {f: {k: round(v[k], 5) for k in ("post_net", "title", "cf", "r2")}
                  for f, v in forks.items()},
    }
    (OUT / "season_hist.json").write_text(json.dumps(out, indent=2))
    g = sum(c for c, e in zip(counts, edges[:-1]) if e >= dream_x)
    print(f"\nsigma_t {sigma_t:.2f}  mean {mean:+.2f}")
    print(f"zones  WORSE {out['p_worse']*100:.0f}%  WASH {out['p_wash']*100:.0f}%  "
          f"DREAM {out['p_dream']*100:.0f}%   (green bars hold {g} of {N} = {g/N*100:.0f}%)")
    print(f"peak bin {counts.max()}   green tail bins: "
          f"{[int(c) for c, e in zip(counts, edges[:-1]) if e >= dream_x]}")
    print(f"wrote {OUT/'season_hist.json'}")


if __name__ == "__main__":
    main()
