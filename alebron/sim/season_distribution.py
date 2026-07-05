"""
Per-season outcome DISTRIBUTION for MIN (+LeBron), straight out of the same 20,000-season
engine the title number uses. Reproduces the engine's single-season playoff-strength draw
(base_net + N(0, sigma_t)) for the +LeBron roster and bins it, so any slide draws TRUE bars.

Both metric forks are run and averaged; the single-season noise (sigma_t ~ 5.5) dwarfs the
fork gap in MIN's net, so the shape is fork-invariant. Writes season_hist.json.

    python alebron/sim/season_distribution.py
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

OUT = REPO / "alebron" / "data" / "sim"
imp_df = pd.read_csv(REPO / "alebron" / "data" / "impact" / "player_impact.csv")
ts_lebron = json.loads((REPO / "alebron" / "data" / "impact" / "team_strength.json").read_text())
ts_lamelo = json.loads((REPO / "lamelo" / "data" / "impact" / "team_strength.json").read_text())
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
    imp = make_imp(fork)
    strengths = E.build_2026_27_league(imp)
    runitback = float(strengths["MIN"]["net"])
    min_baseline = runitback + BETA * float(ts_lamelo["forks"][fork]["trade_delta_raw"])
    post = min_baseline + BETA * float(ts_lebron["forks"][fork]["lebron_add_delta_raw"])
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
    sigma_t = float(np.sqrt(EP["sigma_unobs"] ** 2 + (EP.get("munc_w", 0.35) * avg["munc"]) ** 2
                            + (0.15 * avg["net_sd"]) ** 2))
    mean = avg["post_net"]
    rng = np.random.default_rng(1)
    draws = mean + rng.normal(0.0, sigma_t, N)
    lo, hi = mean - 3.5 * sigma_t, mean + 3.5 * sigma_t
    counts, edges = np.histogram(draws, bins=NBINS, range=(lo, hi))
    P_WORSE = 0.30
    worse_x = float(np.quantile(draws, P_WORSE))
    dream_x = float(np.quantile(draws, 1.0 - avg["cf"]))
    out = {"n_sims": N, "nbins": NBINS, "seed": 1, "source": "bracket_sim 20,000-season engine (+LeBron)",
           "mean_net": round(mean, 3), "sigma_t": round(sigma_t, 3),
           "bin_edges": [round(float(e), 4) for e in edges], "counts": counts.astype(int).tolist(),
           "worse_x": round(worse_x, 4), "dream_x": round(dream_x, 4),
           "p_worse": round(P_WORSE, 4), "p_wash": round(1.0 - P_WORSE - avg["cf"], 4), "p_dream": round(avg["cf"], 4),
           "rates_avg": {k: round(avg[k], 5) for k in ("title", "finals", "cf", "r2")},
           "forks": {f: {k: round(v[k], 5) for k in ("post_net", "title", "cf", "r2")} for f, v in forks.items()}}
    (OUT / "season_hist.json").write_text(json.dumps(out, indent=2))
    print(f"\nsigma_t {sigma_t:.2f}  mean {mean:+.2f}  zones WORSE {out['p_worse']*100:.0f}%  "
          f"WASH {out['p_wash']*100:.0f}%  DREAM {out['p_dream']*100:.0f}%")
    print(f"wrote {OUT/'season_hist.json'}")


if __name__ == "__main__":
    main()
