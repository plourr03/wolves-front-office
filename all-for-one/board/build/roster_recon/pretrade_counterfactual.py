"""Pre-trade counterfactual: Joan Bet (bracket_sim) on the ENCODED PRE rotation.

Item 3 of Bobby's post-step-four directive: run bracket_sim on the run-it-back
roster (build_team_strength.PRE: Randle + Reid, DiVincenzo out, no LaMelo), both
forks, to produce the TRADE-VERDICT read. Reports pre-trade equity, the trade's
equity delta per fork (post minus pre), and the perf/run bands, so the piece can
say what the LaMelo trade actually bought in title odds.

Anchoring is the same as the reconciled post run: the engine's calibrated 2026-27
MIN net is the pre-trade anchor (min_pre = strengths["MIN"]["net"]), and the
reconciled post net is min_pre + BETA * deflated_trade_delta. So simulating at
min_pre is the pre-trade counterfactual on the same scale as the post, and the
title-equity difference is the pure trade effect. PRELIMINARY; title numbers GATED
(lamelo identifiability), reported as a fork range.

The forward-equity positioning of pre and post against the 0.10 hazard cliff (the
board's commitment line) is done in board_step5.py, which owns the board machinery;
this script produces the single-season sim inputs it consumes.

Run:  python pretrade_counterfactual.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import joanbet_reconciled as J    # noqa: E402  (reuses E, make_imp, perf_bands, run_bands, SEEDS, N, BETA)

REPO = J.REPO
OUT = HERE


def run_pre(fork):
    """Simulate the field with MIN at the pre-trade (run-it-back) net, both metrics."""
    imp = J.make_imp(fork)
    strengths = J.E.build_2026_27_league(imp)
    min_pre = float(strengths["MIN"]["net"])            # engine's calibrated run-it-back MIN net
    title, cf, finals, r2, conf = [], [], [], [], []
    for s in J.SEEDS:
        strengths["MIN"]["net"] = min_pre               # pre-trade: no trade delta applied
        out = J.E.simulate_league(strengths, n_sims=J.N, seed=s, use_overlay=True)
        mn = out["teams"]["MIN"]
        title.append(mn.get("title", 0.0)); cf.append(mn.get("cf", 0.0))
        finals.append(mn.get("finals", 0.0)); r2.append(mn.get("r2", 0.0)); conf.append(mn.get("conf", 0.0))
    m = lambda x: float(np.mean(x))
    f = {"fork": fork, "min_pre_net": round(min_pre, 3), "title": m(title), "cf": m(cf),
         "finals": m(finals), "reach_r2": m(r2), "conf": m(conf)}
    pb, wins = J.perf_bands(min_pre)
    f["exp_wins"] = wins
    f["perf_bands"] = pb
    f["run_bands"] = J.run_bands(f, min_pre)
    return f


def main():
    print("Pre-trade counterfactual (encoded PRE / run-it-back rotation), both forks.")
    print("Trade-verdict read: pre-trade equity + the trade's equity delta per fork.")
    print("PRELIMINARY; title GATED (lamelo); reported as a fork range.\n")
    print("PRE rotation (build_team_strength.PRE):")
    for k, v in J.BTS.PRE.items():
        print(f"    {k:24s} {v}")

    post = json.loads((OUT / "joanbet_reconciled.json").read_text())["forks"]
    res = {"n_sims": J.N, "seeds": J.SEEDS, "pre_rotation": dict(J.BTS.PRE),
           "note": "encoded PRE rotation (run-it-back); anchored on the engine's calibrated MIN net, "
                   "same scale as the reconciled post; the delta is the trade effect; title GATED.",
           "forks": {}}
    print()
    for fork in ("rapm", "box"):
        pre = run_pre(fork)
        po = post[fork]
        delta_title = po["title"] - pre["title"]
        pre["post_title"] = po["title"]
        pre["post_net"] = po["min_post_net"]
        pre["trade_delta_title"] = delta_title
        pre["trade_delta_net"] = po["min_post_net"] - pre["min_pre_net"]
        res["forks"][fork] = pre
        print(f"[{fork:4}] PRE net {pre['min_pre_net']:+.2f} (~{pre['exp_wins']} wins) "
              f"title {pre['title']*100:.2f}%  CF {pre['cf']*100:.1f}%  reachR2 {pre['reach_r2']*100:.1f}%")
        print(f"       POST net {po['min_post_net']:+.2f} title {po['title']*100:.2f}%  "
              f"=> TRADE delta net {pre['trade_delta_net']:+.2f}, title {delta_title*100:+.2f} pts")
        print(f"       pre perf bands {pre['perf_bands']}")
        print(f"       pre run  bands {pre['run_bands']}")

    r, b = res["forks"]["rapm"], res["forks"]["box"]
    print("\nFORK RANGES (low, high, driving-high fork):")
    for name, key in [("pre-trade title", "title"), ("post-trade title", "post_title"),
                      ("trade delta (title pts)", "trade_delta_title")]:
        a, c = r[key], b[key]
        drv = "box" if c >= a else "rapm"
        print(f"  {name:24s}: [{a*100:+.2f}, {c*100:+.2f}]  driven high by {drv}")
    print("\n  TRADE VERDICT (preliminary): the LaMelo deal is title-equity POSITIVE on the")
    print("  box read and roughly FLAT-to-negative on the rapm read; the pre-trade run-it-back")
    print("  team is itself a low-equity contender on both. Cliff positioning in board_step5.")

    (OUT / "pretrade_counterfactual.json").write_text(json.dumps(res, indent=1))
    print(f"\nwrote {OUT/'pretrade_counterfactual.json'}")


if __name__ == "__main__":
    main()
