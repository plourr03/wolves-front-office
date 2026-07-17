"""Joan Bet (bracket_sim) run on the RECONCILED post-trade roster, BOTH forks.

Recomputes the trade delta from the reconciled rotation (roster_reconciliation.md:
Gueye 18 removed as phantom, Shannon Jr. + Trey Lyles added, Jaylen Clark named),
reusing the offseason engine (build_team_strength.team_raw_net, bracket_sim). Does
NOT feed the file's absolute raw nets into anything (only the delta is robust, per
the file note). Carries rapm AND box forks end to end.

Output per fork: MIN post-trade net, title equity, and the perf-band and run-band
distributions the board's step-four transitions consume, reported as a range
across forks with the driving fork named. Title numbers stay GATED per lamelo.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
sys.path.insert(0, str(REPO / "offseason" / "scripts"))
sys.path.insert(0, str(REPO / "lamelo" / "impact"))
import build_team_ratings as A       # noqa: E402
import bracket_sim as E              # noqa: E402
import build_team_strength as BTS    # noqa: E402  (player_net, team_raw_net, PRE)

OUT = REPO / "all-for-one" / "board" / "build" / "roster_recon"

# RECONCILED post-trade rotation (240 mpg) -- roster_reconciliation.md. Gueye REMOVED.
RECONCILED_POST = {
    "Anthony Edwards": 35, "LaMelo Ball": 33, "Jaden McDaniels": 33, "Rudy Gobert": 30,
    "Ayo Dosunmu": 28, "Josh Green": 27, "Terrence Shannon Jr.": 16, "Jaylen Clark": 14,
    "Joan Beringer": 14, "Trey Lyles": 10,
}
BETA = float(E.load_e_params()["beta"])
SEEDS = [1, 2, 3, 4, 5]
N = 20000


def make_imp(fork):
    import pandas as pd
    d = pd.read_csv(REPO / "lamelo" / "data" / "impact" / "player_impact.csv")
    imp = {}
    for _, r in d.iterrows():
        pid = str(int(r.player_id))
        off, dff = (float(r.off_rapm), float(r.def_rapm)) if fork == "rapm" else \
                   (float(r.box_off_prior), float(r.box_def_prior))
        imp[pid] = {"off": off, "def": dff, "off_sd": float(r.off_sd), "def_sd": float(r.def_sd),
                    "def_div": abs(float(r.def_rapm) - float(r.box_def_prior)), "read": ""}
    return imp


def run_fork(fork):
    imp = make_imp(fork)
    strengths = E.build_2026_27_league(imp)
    min_pre = float(strengths["MIN"]["net"])                       # field run-it-back (DiVincenzo out)
    post_raw = BTS.team_raw_net(RECONCILED_POST, fork)            # RECONCILED rotation raw net
    pre_raw = BTS.team_raw_net(BTS.PRE, fork)                     # run-it-back rotation raw net
    delta_raw = post_raw - pre_raw
    min_post = min_pre + BETA * delta_raw
    # simulate the field with MIN at the reconciled post-trade net
    title, cf, finals, r2, conf, seedbands = [], [], [], [], [], []
    keys_seen = None
    for s in SEEDS:
        strengths["MIN"]["net"] = min_post
        out = E.simulate_league(strengths, n_sims=N, seed=s, use_overlay=True)
        mn = out["teams"]["MIN"]
        keys_seen = list(mn.keys())
        title.append(mn.get("title", 0.0)); cf.append(mn.get("cf", 0.0))
        finals.append(mn.get("finals", 0.0)); r2.append(mn.get("r2", 0.0))
        conf.append(mn.get("conf", 0.0))
        # perf band proxy from playoff/seed signal: use expected wins if present
        seedbands.append({k: mn.get(k) for k in ("exp_wins", "playoff", "top4", "playin") if k in mn})
    m = lambda x: float(np.mean(x))
    return {
        "fork": fork, "min_pre_net": round(min_pre, 3), "min_post_net": round(min_post, 3),
        "reconciled_trade_delta_raw": round(delta_raw, 4), "deflated_delta": round(BETA * delta_raw, 3),
        "title": m(title), "conf": m(conf), "finals": m(finals), "cf": m(cf), "reach_r2": m(r2),
        "mn_keys": keys_seen, "seedband_sample": seedbands[0],
    }


import math
WINS_A, WINS_B, WIN_SD = 41.0, 2.239, 5.5   # e_params wins model + unobserved sigma


def _cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def perf_bands(net):
    """MIN perf-band distribution from projected wins (net -> wins, normal noise).
    Bands (seed-proxy, TUNE): T1 top-4 >=53, T2 playoff 46-52, T3 play-in 40-45, T4 <40."""
    wins = WINS_A + WINS_B * net
    ge = lambda t: 1 - _cdf((t - wins) / WIN_SD)
    t1 = ge(53); t2 = ge(46) - t1; t3 = ge(40) - ge(46); t4 = 1 - ge(40)
    return {"T1": round(t1, 3), "T2": round(t2, 3), "T3": round(t3, 3), "T4": round(t4, 3)}, round(wins, 1)


def run_bands(f, net):
    """Board run-band distribution (deepest result, monotone) from the sim reach
    probs, with P(playoffs) from the win model. reach_r2=won R1; cf=reached conf
    finals; finals=reached Finals; title=RING."""
    wins = WINS_A + WINS_B * net
    p_po = 1 - _cdf((46 - wins) / WIN_SD)                # P(playoffs) ~ P(wins>=46)
    p_po = max(p_po, f["reach_r2"])                       # can't be below P(won R1)
    return {"none": round(max(0, 1 - p_po), 3), "R1": round(max(0, p_po - f["reach_r2"]), 3),
            "R2": round(max(0, f["reach_r2"] - f["cf"]), 3), "WCF": round(max(0, f["cf"] - f["finals"]), 3),
            "F": round(max(0, f["finals"] - f["title"]), 3), "RING": round(f["title"], 4)}


def main():
    print("Joan Bet on the RECONCILED post-trade roster (Gueye phantom removed), both forks.")
    print("Title numbers GATED (lamelo identifiability); reported as a fork RANGE.\n")
    res = {"n_sims": N, "seeds": SEEDS, "beta": BETA, "rotation": RECONCILED_POST,
           "note": "reconciled roster; only the trade DELTA is used, not the file's absolute nets; "
                   "title GATED; forks carried as first-class scenarios.", "forks": {}}
    for fork in ("rapm", "box"):
        f = run_fork(fork)
        res["forks"][fork] = f
        pb, wins = perf_bands(f["min_post_net"])
        f["exp_wins"] = wins
        f["perf_bands"] = pb
        f["run_bands"] = run_bands(f, f["min_post_net"])
        print(f"[{fork:4}] MIN net pre {f['min_pre_net']:+.2f} -> post {f['min_post_net']:+.2f} "
              f"(recon delta raw {f['reconciled_trade_delta_raw']:+.3f}, deflated {f['deflated_delta']:+.3f})")
        print(f"       ~{wins} wins | title {f['title']*100:.2f}%  CF {f['cf']*100:.1f}%  reachR2 {f['reach_r2']*100:.1f}%")
        print(f"       perf bands {pb}")
        print(f"       run bands  {f['run_bands']}")
    # fork ranges (range across forks, driving fork named)
    def rng(key):
        a, b = res["forks"]["rapm"][key], res["forks"]["box"][key]
        drv = "box" if b >= a else "rapm"
        return (min(a, b), max(a, b), drv)
    print("\nFORK RANGES (low, high, driving-high fork):")
    for k in ("min_post_net", "title", "cf", "finals"):
        lo, hi, drv = rng(k)
        print(f"  {k:14}: [{lo:.4f}, {hi:.4f}]  driven high by {drv}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "joanbet_reconciled.json").write_text(json.dumps(res, indent=1))
    print(f"\nwrote {OUT/'joanbet_reconciled.json'}")


if __name__ == "__main__":
    main()
