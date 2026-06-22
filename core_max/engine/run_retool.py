#!/usr/bin/env python3
"""The question the Phase-3 verdict OPENS: keep Gobert, what is the best move?

The verdict said Gobert is too good to give up for capital-realistic returns. So this tests the
RANDLE-ONLY RETOOL: keep Gobert (keep the elite defense), keep Joan as a developmental BACKUP
(bust risk contained to ~10 min, not the starting 5), re-sign Ayo, and swap ONLY Randle's
bad-shooting minutes for a real secondary creator / shooter (the actual LAFI fix). With common
random numbers, every shared piece cancels, so the delta vs status quo is a near-pure read on
the Randle->creator upgrade. Same honest engine, same vetted return band, same guardrails.

    python core_max/engine/run_retool.py
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_scenarios as RS

# Retool rotation = status quo with Randle's 31 min reassigned to the creator; ALL else identical
# (Gobert kept, Joan still a 10-min backup), so the comparison isolates the Randle->creator swap.
ROT_RETOOL = {k: v for k, v in RS.ROT_SQ.items() if k != "Randle"}
ROT_RETOOL["CREATOR"] = RS.ROT_SQ["Randle"]      # 31 min
SHARED_RT = ("Edwards", "McDaniels", "Naz", "Ayo", "TSJ", "Conley", "Gobert", "Joan")


def run_retool_cell(val, dims, avail, dev, sub_ids, creator, fit_bound=0.75, fcurve=None):
    grid, P = fcurve
    f = lambda x: np.interp(x, grid, P)
    rng = np.random.default_rng(RS.SEED)
    jp = RS.joan_pool(dev, sub_ids, False, RS.REPL0)

    sq_pids = {RS.PID[k]: v for k, v in RS.ROT_SQ.items()}
    rt_pids = {RS.PID[k]: v for k, v in ROT_RETOOL.items() if k in RS.PID}
    rt_pids[creator[3]] = ROT_RETOOL["CREATOR"]
    rt_fit = RS.fit_delta(sq_pids, rt_pids, dims, fit_bound)

    sq_net = np.empty(RS.NDRAW); rt_net = np.empty(RS.NDRAW)
    for i in range(RS.NDRAW):
        shared = {nm: RS.draw_contrib(rng.normal(*RS.point_sd(nm, val)), RS.AGE[nm],
                                      avail.get(RS.PID[nm], 0.85), rng, 1.0, RS.REPL0) for nm in SHARED_RT}
        ran = RS.draw_contrib(rng.normal(*RS.point_sd("Randle", val)), RS.AGE["Randle"],
                              avail.get(RS.PID["Randle"], 0.85), rng, 1.0, RS.REPL0)
        cre = RS.draw_contrib(rng.normal(creator[0], creator[1]), creator[2], creator[4], rng, 1.0, RS.REPL0)
        c_sq = {**shared, "Randle": ran}
        c_rt = {**shared, "CREATOR": cre}
        sq_net[i] = sum(RS.ROT_SQ[k] / 48.0 * c_sq[k] for k in RS.ROT_SQ)
        rt_net[i] = sum(ROT_RETOOL[k] / 48.0 * c_rt[k] for k in ROT_RETOOL)
    anchor = RS.BASE_NET - sq_net.mean()
    sq_P = f(sq_net + anchor)
    rt_P = f(rt_net + anchor + rt_fit)
    delta = (rt_P - sq_P) * 100
    return {"sq": sq_P.mean() * 100, "rt": rt_P.mean() * 100, "delta": delta.mean(),
            "lo": np.percentile(delta, 5), "hi": np.percentile(delta, 95),
            "p_pos": float((delta > 0).mean()) * 100, "fit": rt_fit, "net": (rt_net + anchor).mean()}


def main():
    val, dims, avail, dev, sub_ids = RS.load_inputs()
    print("building f-curve ...", flush=True)
    fcurve = RS.build_fcurve()
    grid, P = fcurve
    print(f"  sanity f(+1.36)={np.interp(1.36, grid, P)*100:.2f}%\n")
    creators = {"MPJ (BKN, available, flat+stacks)": RS.ret_spec("MPJ", val, avail),
                "Jrue (POR seller, age 36)": RS.ret_spec("Jrue", val, avail),
                "Cam Johnson (DEN, shooter, shaky seller)": RS.ret_spec("Cam", val, avail)}
    print("=== RANDLE-ONLY RETOOL (keep Gobert + Joan-as-backup; swap only Randle's slot) ===")
    print("  vs status quo. CRN isolates the Randle->creator upgrade.\n")
    for lab, cre in creators.items():
        r = run_retool_cell(val, dims, avail, dev, sub_ids, cre, fcurve=fcurve)
        sign = "UPGRADE" if r["delta"] > 0 else "downgrade"
        print(f"  {lab:42s} SQ {r['sq']:.2f}% RT {r['rt']:.2f}% (net {r['net']:+.2f}) "
              f"dP {r['delta']:+.2f}pp [{r['lo']:+.2f},{r['hi']:+.2f}] P(RT>SQ) {r['p_pos']:>3.0f}% [{sign}]")
    print("\n  (contrast: Fork B central was dP -1.14pp. The retool keeps Gobert's +4.57 and only")
    print("   upgrades the Randle slot, so it should not carry the Gobert-sized hole Fork B did.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
