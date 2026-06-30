"""
Sim layer: title-odds and Q2 quantities for the LaMelo trade, BOTH metric forks,
internally consistent end to end, CRN-paired (run-it-back vs post-trade share the same
random draws so the delta isolates the trade).

Reuses the calibrated sim METHOD (bracket_sim + series_resolver + the SCALE/SHAPE params).
The clean-room status of the SCALE/SHAPE/series calibrations is a REPRODUCTION CHECK +
the retrodiction gate, run separately; those are external-data-anchored (win totals,
de-vigged boards, 1997-2025 series), independent of the impact metric. The TITLE NUMBER
stays gated pending that re-validation + the retrodiction backtest; the CRN-paired delta
and the Q2 ordinal quantities are field-robust and reported with the gate caveat.

Per fork: build the 30-team field with the fork's clean-room impacts (so the same metric
drives MIN, the opponents, and the method-uncertainty term), set MIN run-it-back = the
field's MIN (DiVincenzo-out baseline), MIN post-trade = run-it-back + beta * team-strength
raw delta (deflated to the RS scale). The fork range IS the structural band.

Output: lamelo/data/sim/sim_results.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "offseason" / "scripts"))
import build_team_ratings as A  # noqa: E402
import bracket_sim as E         # noqa: E402

OUT = REPO / "lamelo" / "data" / "sim"
OUT.mkdir(parents=True, exist_ok=True)

imp_df = pd.read_csv(REPO / "lamelo" / "data" / "impact" / "player_impact.csv")
ts = json.loads((REPO / "lamelo" / "data" / "impact" / "team_strength.json").read_text())
BETA = float(E.load_e_params()["beta"])
SEEDS = [1, 2, 3, 4, 5]
N = 20000


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
    min_pre = float(strengths["MIN"]["net"])               # run-it-back (DiVincenzo out)
    raw_delta = float(ts["forks"][fork]["trade_delta_raw"])
    min_post = min_pre + BETA * raw_delta                  # post-trade, deflated trade delta
    rows = {"min_pre_net": round(min_pre, 3), "min_post_net": round(min_post, 3),
            "deflated_trade_delta": round(BETA * raw_delta, 3)}
    dt, dcf, pt, pcf, pf = [], [], [], [], []
    for s in SEEDS:
        strengths["MIN"]["net"] = min_pre
        pre = E.simulate_league(strengths, n_sims=N, seed=s, use_overlay=True)["teams"]["MIN"]
        strengths["MIN"]["net"] = min_post
        post = E.simulate_league(strengths, n_sims=N, seed=s, use_overlay=True)["teams"]["MIN"]
        dt.append(post["title"] - pre["title"]); dcf.append(post["cf"] - pre["cf"])
        pt.append(post["title"]); pcf.append(post["cf"]); pf.append(post["finals"])
    rows.update({
        "pre_title": float(np.mean([p for p in pt]) - np.mean(dt)),  # implied pre
        "post_title": float(np.mean(pt)), "post_cf": float(np.mean(pcf)), "post_finals": float(np.mean(pf)),
        "title_delta_pp": float(np.mean(dt)) * 100, "title_delta_mc_sd_pp": float(np.std(dt)) * 100,
        "cf_delta_pp": float(np.mean(dcf)) * 100,
    })
    return rows


def main():
    res = {"n_sims": N, "seeds": SEEDS, "beta": BETA,
           "gate_note": "TITLE NUMBER GATED pending SCALE/SHAPE/series re-validation diff + retrodiction backtest; "
                        "reported here with that caveat. CRN-paired delta and Q2 ordinals are field-robust.",
           "forks": {}}
    for fork in ["rapm", "box"]:
        res["forks"][fork] = run_fork(fork)
        f = res["forks"][fork]
        print(f"[{fork:4}] MIN net pre {f['min_pre_net']:+.2f} -> post {f['min_post_net']:+.2f} "
              f"(trade {f['deflated_trade_delta']:+.3f})")
        print(f"       post-trade: title {f['post_title']*100:.2f}%  CF {f['post_cf']*100:.1f}%  "
              f"Finals {f['post_finals']*100:.1f}%")
        print(f"       title DELTA {f['title_delta_pp']:+.3f}pp (MC sd {f['title_delta_mc_sd_pp']:.3f}pp)  "
              f"CF delta {f['cf_delta_pp']:+.2f}pp")
    # structural band on the title delta = the fork range
    lo = min(res["forks"]["rapm"]["title_delta_pp"], res["forks"]["box"]["title_delta_pp"])
    hi = max(res["forks"]["rapm"]["title_delta_pp"], res["forks"]["box"]["title_delta_pp"])
    res["title_delta_structural_band_pp"] = [round(lo, 3), round(hi, 3)]
    print(f"\nTITLE DELTA structural band across forks: [{lo:+.3f}, {hi:+.3f}] pp")
    (OUT / "sim_results.json").write_text(json.dumps(res, indent=2))
    print(f"wrote {OUT/'sim_results.json'}")


if __name__ == "__main__":
    main()
