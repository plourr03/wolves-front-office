"""
Interaction-scenario layer (alebron / LeBron-to-MIN): the fit-clicks / neutral / fit-fails table.

The registered fit hypothesis for LeBron is the THREE-INITIATOR problem, not a two-man unlock:
  - UPSIDE (fit_clicks): LeBron as the connective orchestrator/closer. He runs the half-court
    offense, lets Edwards play off-ball and attack, feeds Gobert lobs, and stabilizes the
    non-Edwards minutes with elite playoff IQ. A point-forward LeBron organizing for Ant + LaMelo.
  - DOWNSIDE (fit_fails): three ball-dominant creators (Edwards, Ball, James) colliding for on-ball
    reps, with NO floor spacing added (LeBron a ~31% shooter last year; Reid/Randle already gone),
    LeBron hunted defensively at 41-42, and a thinner-than-ever bench because he cost a rotation
    minimum body. The collision has MORE bodies than the LaMelo two-man case, so if anything the
    downside tail is wider; we keep the symmetric +/-0.75 bound for comparability and sweep it.

The fit term is a symmetric documented net adjustment on MIN's +LeBron net: fit_clicks = +0.75,
fit_fails = -0.75, neutral = 0. CRN-paired vs the completed post-LaMelo baseline (no LeBron).

Output: alebron/data/sim/scenario_table.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "alebron" / "sim"))
import run_sim as RS  # noqa: E402

E = RS.E
FIT = {"fit_clicks": +0.75, "neutral": 0.0, "fit_fails": -0.75}
SEEDS = [1, 2, 3]
N = 20000
OUT = REPO / "alebron" / "data" / "sim" / "scenario_table.json"


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
    runitback = float(strengths["MIN"]["net"])
    lamelo_delta = float(RS.ts_lamelo["forks"][fork]["trade_delta_raw"])
    lebron_delta = float(RS.ts_lebron["forks"][fork]["lebron_add_delta_raw"])
    min_baseline = runitback + RS.BETA * lamelo_delta            # post-LaMelo, no LeBron
    min_lebron_neutral = min_baseline + RS.BETA * lebron_delta   # +LeBron, neutral fit
    base = sim_min(strengths, min_baseline)
    out = {"min_baseline_postlamelo_net": round(min_baseline, 3),
           "min_with_lebron_neutral_net": round(min_lebron_neutral, 3),
           "baseline_postlamelo": {"title": base[0], "cf": base[1], "finals": base[2]}, "scenarios": {}}
    for sc, bonus in FIT.items():
        post = sim_min(strengths, min_lebron_neutral + bonus)
        out["scenarios"][sc] = {
            "min_net": round(min_lebron_neutral + bonus, 3),
            "title": post[0], "cf": post[1], "finals": post[2],
            "title_delta_pp": (post[0] - base[0]) * 100, "cf_delta_pp": (post[1] - base[1]) * 100,
            "finals_delta_pp": (post[2] - base[2]) * 100,
        }
    return out


def main():
    res = {"fit_bound": 0.75, "n_sims": N, "seeds": SEEDS, "field": "calibrated_primary",
           "note": "Three-initiator fit term (+/-0.75 net), CRN-paired vs the completed post-LaMelo "
                   "baseline. Title % remains GATED on identifiability.", "forks": {}}
    for fork in ["rapm", "box"]:
        res["forks"][fork] = run_fork(fork)
        b = res["forks"][fork]["baseline_postlamelo"]["title"]
        print(f"\n=== {fork} fork (post-LaMelo baseline title {b*100:.2f}%) ===")
        for sc in ["fit_fails", "neutral", "fit_clicks"]:
            s = res["forks"][fork]["scenarios"][sc]
            print(f"  {sc:10} title {s['title']*100:5.2f}% (d {s['title_delta_pp']:+5.2f}pp)  "
                  f"CF {s['cf']*100:5.2f}% (d {s['cf_delta_pp']:+5.2f}pp)  "
                  f"Finals {s['finals']*100:5.2f}% (d {s['finals_delta_pp']:+5.2f}pp)")
    OUT.write_text(json.dumps(res, indent=2))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
