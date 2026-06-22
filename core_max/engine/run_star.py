#!/usr/bin/env python3
"""The star branch the frontier omitted (the public's #1 question: Giannis for the core).

Two questions, answered honestly:
  (A) MAGNITUDE: a star acquired CHEAPLY (keep the core) would help a lot. A star at the
      REALISTIC price (Milwaukee's reported ask: McDaniels + Naz + TSJ + 2 firsts) guts the
      depth/defense, so the net gain is much smaller, the fit-over-splash logic at MVP level.
  (B) ATTAINABILITY: the Wolves have McDaniels AND Beringer off-limits (reporting) and only
      ~No. 28 + a 2033 first to trade; Miami is the frontrunner. So the cheap-price star is not
      available, and the realistic-price star barely beats the retool.

    python core_max/engine/run_star.py
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_scenarios as RS

GIANNIS = ("1629027_giannis", 7.29, 1.57, 31)   # consensus_net, sd, age
# Realistic-price rotation: out McDaniels+Naz+TSJ (Bucks' ask) for Giannis + 2 min fillers.
ROT_STAR_REAL = {"Edwards": 36, "GIANNIS": 36, "Gobert": 30, "Randle": 26, "Ayo": 26,
                 "Conley": 18, "Joan": 10, "FILL1": 30, "FILL2": 28}
# Cheap-price (NOT available) rotation: out Randle + DiVincenzo + picks, KEEP the core.
ROT_STAR_CHEAP = {"Edwards": 36, "GIANNIS": 36, "McDaniels": 33, "Gobert": 28, "Naz": 26,
                  "Ayo": 24, "Conley": 11, "Joan": 10}


def main():
    import age_curve as AC
    RS._val, RS._dims, RS._avail, RS._dev, RS._sub_ids = RS.load_inputs()
    print("building f-curve ...", flush=True)
    grid, P = RS.build_fcurve()
    f = lambda x: np.interp(x, grid, P)
    g_pt = GIANNIS[1] + AC.age_delta(GIANNIS[3])

    def net_dist(rotation, rng):
        jp = RS.joan_pool(RS._dev, RS._sub_ids, False, RS.REPL0)
        out = np.empty(RS.NDRAW)
        for i in range(RS.NDRAW):
            c = {}
            for k in rotation:
                if k == "Joan":
                    c[k] = float(rng.choice(jp))
                elif k == "GIANNIS":
                    c[k] = RS.draw_contrib(rng.normal(g_pt, GIANNIS[2]), GIANNIS[3], 0.80, rng, 1.0, RS.REPL0)
                elif k.startswith("FILL"):
                    c[k] = RS.REPL0
                else:
                    c[k] = RS.draw_contrib(rng.normal(*RS.point_sd(k, RS._val)), RS.AGE[k],
                                           RS._avail.get(RS.PID[k], 0.85), rng, 1.0, RS.REPL0)
            out[i] = sum(rotation[k] / 48.0 * c[k] for k in rotation)
        return out

    sp = net_dist(RS.ROT_SQ, np.random.default_rng(RS.SEED))
    anchor = RS.BASE_NET - sp.mean()
    sp_T = f(sp + anchor).mean() * 100

    # fit term: Giannis next to Gobert (+Randle) is a spacing logjam -> the symmetric fit term penalizes it
    def fit_for(rot):
        sq_pids = {RS.PID[k]: v for k, v in RS.ROT_SQ.items()}
        rp = {RS.PID[k]: v for k, v in rot.items() if k in RS.PID}
        rp["1629027"] = rot["GIANNIS"]   # giannis pid for dims (may be absent -> neutral)
        return RS.fit_delta(sq_pids, rp, RS._dims, 0.75)

    print(f"\nstatus quo: {sp_T:.2f}% (net +1.36)\n")
    for lab, rot in [("Giannis at REALISTIC price (out McDaniels+Naz+TSJ+2 firsts)", ROT_STAR_REAL),
                     ("Giannis at CHEAP price (keep core; NOT available)", ROT_STAR_CHEAP)]:
        nd = net_dist(rot, np.random.default_rng(RS.SEED))
        net = (nd + anchor)
        fit = fit_for(rot)
        T = f(net + fit).mean() * 100
        print(f"  {lab:54s} net {net.mean()+fit:+.2f} -> {T:.2f}%  (dP {T-sp_T:+.2f}pp vs stand-pat)")

    print("\n  Contrast: retool (keep Gobert, fix Randle slot) ~3.0-3.7%; Fork B 1.3%.")
    print("  Read: a star at the price the Bucks actually want (the young core) barely beats the")
    print("  retool, because surrendering McDaniels' defense + Naz's +3.15 + depth for ONE body")
    print("  (with min-filler holes + a Giannis/Gobert spacing logjam) offsets most of the star.")
    print("  A star acquired CHEAPLY would help a lot, but that price is not on the table")
    print("  (McDaniels + Beringer off-limits; only ~No. 28 + 2033 tradeable; Miami the frontrunner).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
