#!/usr/bin/env python3
"""The frontier: across capital-realistic moves, what is the CEILING on the Wolves' title odds,
and does any move materially move it, or are they asset-constrained into the mid-tier?

Each move reports: title odds (same honest engine), delta vs stand-pat, ASSET COST (so a free
signing's +0.5 is distinguished from a pick-burning +0.5), and CBA status via the Phase-0 gate
(so the frontier subsumes the cap check; it also reports which MLE the resulting tier allows).

Plus a separate, heavily-caveated FUTURE-WINDOW probe: with Joan developed, Gobert/Randle money
rolled off, and cap/picks regained, does the ceiling actually rise? Patience is the right answer
only if waiting pays, so this is tested, not assumed.

    python core_max/engine/run_frontier.py
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import run_scenarios as RS
import run_retool as RT
from core_max.cba import gate as G

# ADDITIVITY CORRECTION (2026-06-22): the MLE shooter was modeled here as a flat team-net ADD on
# top of each move. That is fine on STAND-PAT (a clogged offense, no creator) where a shooter
# genuinely helps (~+0.25). It is WRONG stacked on top of a CREATOR retool: the combined-roster
# model (run_package.py, which models the shooter IN the rotation) shows the shooter adds ~0 once a
# creator has already un-clogged the offense (package C 3.19% ~= Cam-alone 3.24%). So the old
# "retool + full MLE = 3.69% (+1.24)" double-counted the shooter; the honest ceiling is ~3.2%
# (+0.77). MLE_ON_CREATOR is set to ~0 accordingly; run_package.py is the CANONICAL combined model.
MLE_TAX = 0.25            # shooter on stand-pat (no creator) genuinely helps
MLE_ON_CREATOR = 0.05     # shooter stacked on a creator adds ~nothing (combined model); was 0.40 (inflated)
CFG = os.path.join(HERE, "..", "config", "gate_config.json")


def net_dist(rotation, creator=None, wing=None, rng=None):
    """Sample MIN team-net for a rotation. Known names drawn from Phase-1a; Joan from his Phase-2
    comp pool; CREATOR/WING slots from their return specs (or replacement for a relief slot)."""
    jp = RS.joan_pool(RS._dev, RS._sub_ids, False, RS.REPL0)
    out = np.empty(RS.NDRAW)
    for i in range(RS.NDRAW):
        c = {}
        for k in rotation:
            if k == "Joan":
                c[k] = float(rng.choice(jp))
            elif k == "CREATOR":
                c[k] = (RS.draw_contrib(rng.normal(creator[0], creator[1]), creator[2], creator[4], rng, 1.0, RS.REPL0)
                        if creator else RS.REPL0)
            elif k == "WING":
                c[k] = (RS.draw_contrib(rng.normal(wing[0], wing[1]), wing[2], wing[4], rng, 1.0, RS.REPL0)
                        if wing else RS.REPL0)
            else:
                c[k] = RS.draw_contrib(rng.normal(*RS.point_sd(k, RS._val)), RS.AGE[k],
                                       RS._avail.get(RS.PID[k], 0.85), rng, 1.0, RS.REPL0)
        out[i] = sum(rotation[k] / 48.0 * c[k] for k in rotation)
    return out


def gate_status(legs):
    try:
        cfg = G.GateConfig.from_file(CFG)
        plan = G.Plan("frontier", "", tuple(G.Leg(**l) for l in legs))
        r = G.evaluate_plan(plan, cfg)
        tier = r.final_tier
        mle = "full" if tier in ("over_cap_under_tax", "taxpayer") else ("taxpayer" if tier == "first_apron" else "none")
        return ("PASS" if r.passed else "FAIL"), tier, mle
    except Exception as e:
        return f"ERR:{str(e)[:30]}", "?", "?"


AYO = {"label": "Ayo (Bird)", "salary": 16_500_000, "pid": "1630245"}


def main():
    RS._val, RS._dims, RS._avail, RS._dev, RS._sub_ids = RS.load_inputs()
    print("building f-curve ...", flush=True)
    grid, P = RS.build_fcurve()
    f = lambda x: np.interp(x, grid, P)

    Jrue, Cam, MPJ = RS.ret_spec("Jrue", RS._val, RS._avail), RS.ret_spec("Cam", RS._val, RS._avail), RS.ret_spec("MPJ", RS._val, RS._avail)
    ONe = RS.ret_spec("ONeale", RS._val, RS._avail)

    rng = np.random.default_rng(RS.SEED)
    sp = net_dist(RS.ROT_SQ, rng=np.random.default_rng(RS.SEED))
    anchor = RS.BASE_NET - sp.mean()

    def title(net_arr, add=0.0, fit=0.0):
        return f(net_arr + anchor + add + fit).mean() * 100

    sp_T = title(sp)
    print(f"  stand-pat anchor: {sp_T:.2f}%\n")

    # legs for the gate (Randle out + Ayo; retool returns; Fork B both out)
    randle_out = lambda inc, sal: [{"label": "Randle->creator", "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": "203944"}],
                                    "incoming": [{"label": inc, "salary": sal, "pid": "RET"}]},
                                   {"label": "Ayo", "incoming": [AYO], "exception_used": "bird"}]
    # pricier creators need DiVincenzo ($12.5M, injured anyway) attached so the deal takes back LESS
    # (opens room) instead of breaching the first-apron hard cap that keeping Gobert pins MIN near.
    randle_plus = lambda inc, sal: [{"label": "Randle+DDV->creator",
                                     "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": "203944"},
                                                  {"label": "DiVincenzo", "salary": 12_500_000, "pid": "1628978"}],
                                     "incoming": [{"label": inc, "salary": sal, "pid": "RET"}]},
                                    {"label": "Ayo", "incoming": [AYO], "exception_used": "bird"}]
    forkb_legs = [{"label": "Randle->cre", "outgoing": [{"label": "Randle", "salary": 33_333_334, "pid": "203944"}],
                   "incoming": [{"label": "cre", "salary": 30_000_000, "pid": "C"}]},
                  {"label": "Gobert->wing", "outgoing": [{"label": "Gobert", "salary": 36_500_000, "pid": "203497", "trade_kicker_pct": 0.075}],
                   "incoming": [{"label": "wing", "salary": 24_000_000, "pid": "W"}]},
                  {"label": "Ayo", "incoming": [AYO], "exception_used": "bird"}]

    def fitval(rot_pids_extra):
        sq_pids = {RS.PID[k]: v for k, v in RS.ROT_SQ.items()}
        return RS.fit_delta(sq_pids, rot_pids_extra, RS._dims, 0.75)

    rt_pids = lambda cre: {**{RS.PID[k]: v for k, v in RT.ROT_RETOOL.items() if k in RS.PID}, cre[3]: RT.ROT_RETOOL["CREATOR"]}

    print(f"{'move':46s}{'title':>7s}{'dVS_sp':>8s}{'asset cost':>22s}{'CBA':>6s}{'MLE':>6s}")
    rows = []
    def add_move(lab, net_arr, add, fit, cost, legs):
        T = title(net_arr, add, fit); st, tier, mle = gate_status(legs) if legs else ("PASS", "n/a", "full")
        rows.append((lab, T, T - sp_T, cost, st, mle))
        print(f"{lab:46s}{T:>6.2f}%{T-sp_T:>+7.2f}{cost:>22s}{st:>6s}{mle:>6s}")

    add_move("0 stand pat + develop (Ayo only)", sp, 0.0, 0.0, "none", [{"label": "Ayo", "incoming": [AYO], "exception_used": "bird"}])
    add_move("1 stand pat + taxpayer-MLE shooter", sp, MLE_TAX, 0.0, "MLE $ only", [{"label": "Ayo", "incoming": [AYO], "exception_used": "bird"}])
    # retools (keep Gobert): need fit + creator slot
    rt_J = net_dist(RT.ROT_RETOOL, creator=Jrue, rng=np.random.default_rng(RS.SEED))
    rt_C = net_dist(RT.ROT_RETOOL, creator=Cam, rng=np.random.default_rng(RS.SEED))
    rt_M = net_dist(RT.ROT_RETOOL, creator=MPJ, rng=np.random.default_rng(RS.SEED))
    add_move("2 retool Randle+DDV->Jrue (attainable)", rt_J, 0.0, fitval(rt_pids(Jrue)), "Randle+DDV+pick", randle_plus("Jrue", 34_800_000))
    add_move("3 retool Randle->Cam (best fit, shaky)", rt_C, 0.0, fitval(rt_pids(Cam)), "Randle + pick", randle_out("Cam", 23_062_500))
    add_move("4 retool Randle->Cam + full MLE (canonical: run_package C)", rt_C, MLE_ON_CREATOR, fitval(rt_pids(Cam)), "Randle + pick + MLE$", randle_out("Cam", 23_062_500))
    add_move("5 retool Randle+DDV->MPJ (available, flat)", rt_M, 0.0, fitval(rt_pids(MPJ)), "Randle+DDV+pick", randle_plus("MPJ", 40_806_150))
    # Fork B contrast
    fb = net_dist(RS.ROT_FB, creator=Jrue, wing=ONe, rng=np.random.default_rng(RS.SEED))
    add_move("6 Fork B (Gobert+Randle out) [contrast]", fb, 0.0, RS.fit_delta({RS.PID[k]: v for k, v in RS.ROT_SQ.items()}, {**{RS.PID[k]: v for k, v in RS.ROT_FB.items() if k in RS.PID}, Jrue[3]: RS.ROT_FB["CREATOR"], ONe[3]: RS.ROT_FB["WING"]}, RS._dims, 0.75), "Gobert+Randle+pick", forkb_legs)

    ceiling = max(rows, key=lambda r: r[1])
    print(f"\n  NEAR-TERM CEILING: {ceiling[0].strip()} at {ceiling[1]:.2f}% "
          f"(+{ceiling[2]:.2f}pp over stand-pat {sp_T:.2f}%). Everything sits in a ~{sp_T:.1f}-{ceiling[1]:.1f}% band.")

    # ---- FUTURE-WINDOW probe (heavily caveated): does waiting pay? ----
    print("\n=== FUTURE-WINDOW probe (does patience pay? tested, not assumed) ===")
    print("  Joan developed + Gobert/Randle (~$70M) rolled off + cap/picks regained, spent on a")
    print("  freed-up acquisition. Mapped through the CURRENT f-curve (CAVEAT: rivals age too;")
    print("  this BOUNDS the future ceiling, it does not predict the future league).")
    dev = RS._dev
    import pandas as pd
    mature = pd.read_csv(RS.DEV); mature = mature[mature["cy"].isin([4, 5, 6])]
    jvals = [mature["imp"].dropna().quantile(q) for q in (0.5, 0.75, 0.9)]   # developed-Joan tiers (measured survivors)
    # future MIN core net (rough): Ant prime + McDaniels grown + Naz + TSJ + Joan(dev) + a freed-cap acquisition
    for jlab, jnet, acq, alab in [("Joan busts (mature median)", jvals[0], 1.0, "avg piece"),
                                  ("Joan solid (mature p75)", jvals[1], 2.5, "good starter"),
                                  ("Joan hits (mature p90) + strong add", jvals[2], 3.5, "near-star")]:
        # crude future net: status-quo-ish core minus the 2 bigs' net, plus developed Joan at the 5 and the acquisition
        future_net = RS.BASE_NET + (jnet - (-0.6)) * (26 / 48) + (acq - 0.49) * (30 / 48)
        T = f(future_net) * 100
        print(f"  {jlab:38s} (+{alab}): MIN net ~{future_net:+.2f} -> ~{T:.1f}% title (vs ~2.4% now)")
    print("  Read: the future ceiling rises materially ONLY in the minority branch where Joan")
    print("  actually develops AND the freed cap lands a real piece. If Joan busts (the base rate),")
    print("  the future window is not better. 'Be patient' is justified only if you believe that")
    print("  conjunction; it is not free.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
