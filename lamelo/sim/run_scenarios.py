"""
Interaction-scenario layer: the fit-clicks / neutral / fit-fails table, the most direct
test of the registered secondary-creator-unlock hypothesis (LaMelo lifts Edwards off-ball
and Gobert via lob/rim gravity) and its symmetric hedge (Ant-LaMelo usage collision,
LaMelo's defense hunted with Gobert in drop). Both metric forks, CRN-paired, consistent.

The fit term is a symmetric, documented net adjustment applied to MIN's post-trade net:
fit_clicks = +0.75 (the unlock realized), fit_fails = -0.75 (the hedge realized), neutral
= 0. The +/-0.75 bound is the additivity-tested scenario scale (a scenario PARAMETER, not
a fitted output); sensitivity at +/-0.5 and +/-1.0 is a multiverse refinement.

Output: lamelo/data/sim/scenario_table.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "lamelo" / "sim"))
import run_sim as RS  # noqa: E402  (sets up offseason path, brings make_imp/BETA/E/ts)

E = RS.E
FIT = {"fit_clicks": +0.75, "neutral": 0.0, "fit_fails": -0.75}
SEEDS = [1, 2, 3]
N = 20000
OUT = REPO / "lamelo" / "data" / "sim" / "scenario_table.json"


def sim_min(strengths, net):
    t, c, f = [], [], []
    for s in SEEDS:
        strengths["MIN"]["net"] = net
        m = E.simulate_league(strengths, n_sims=N, seed=s, use_overlay=True)["teams"]["MIN"]
        t.append(m["title"]); c.append(m["cf"]); f.append(m["finals"])
    return np.mean(t), np.mean(c), np.mean(f)


def run_fork(fork):
    imp = RS.make_imp(fork)
    strengths = E.build_2026_27_league(imp)
    min_pre = float(strengths["MIN"]["net"])
    raw_delta = float(RS.ts["forks"][fork]["trade_delta_raw"])
    min_post_neutral = min_pre + RS.BETA * raw_delta
    pre = sim_min(strengths, min_pre)
    out = {"min_pre_net": round(min_pre, 3), "min_post_neutral_net": round(min_post_neutral, 3),
           "pre_runitback": {"title": pre[0], "cf": pre[1], "finals": pre[2]}, "scenarios": {}}
    for sc, bonus in FIT.items():
        post = sim_min(strengths, min_post_neutral + bonus)
        out["scenarios"][sc] = {
            "min_net": round(min_post_neutral + bonus, 3),
            "title": post[0], "cf": post[1], "finals": post[2],
            "title_delta_pp": (post[0] - pre[0]) * 100,
            "cf_delta_pp": (post[1] - pre[1]) * 100,
            "finals_delta_pp": (post[2] - pre[2]) * 100,
        }
    return out


def main():
    res = {"fit_bound": 0.75, "n_sims": N, "seeds": SEEDS,
           "note": "fit term is a scenario parameter (+/-0.75 net), CRN-paired vs run-it-back; "
                   "title percentages remain GATED pending calibration re-validation + retrodiction.",
           "forks": {}}
    for fork in ["rapm", "box"]:
        res["forks"][fork] = run_fork(fork)
        print(f"\n=== {fork} fork (run-it-back title "
              f"{res['forks'][fork]['pre_runitback']['title']*100:.2f}%) ===")
        for sc in ["fit_fails", "neutral", "fit_clicks"]:
            s = res["forks"][fork]["scenarios"][sc]
            print(f"  {sc:10} title {s['title']*100:5.2f}% (d {s['title_delta_pp']:+5.2f}pp)  "
                  f"CF {s['cf']*100:5.2f}% (d {s['cf_delta_pp']:+5.2f}pp)  "
                  f"Finals {s['finals']*100:5.2f}% (d {s['finals_delta_pp']:+5.2f}pp)")
    OUT.write_text(json.dumps(res, indent=2))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
