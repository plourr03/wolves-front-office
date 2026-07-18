"""Board step seven: the ARM-D cost side, wired live.

Bobby's post-step-six directive item 1: the ARM-D cost side is now specifiable
without improvisation, so the value channel (step six) gets its cost and is wired
into the solve. Three cost components, all COMPUTED (never asserted):

  (a) dump sweetener: dumping salary is a SELL-side transaction, so its required
      sweetener is priced off the SAME buyers-to-sellers proxy as acquisitions, run
      in MIRROR: a tight market (many buyers) makes a dump CHEAPER to place, a loose
      market dearer. State-dependent (board_step6 market machinery, mirrored).
  (b) matching-optionality loss: dumping DDV shrinks the node-6 acquisition doorway
      (DDV+Green ~27.6M is the only midsize-deal matching). Priced as DDV's salary
      share of the board-value delta between having the acquire arms and not
      (board_step4.DISABLE_ACQ_ARMS). Computed, not asserted.
  (c) return value: DDV's healthy-branch stretch-run value, forfeited by the dump.
      His warehouse impact, at rotation minutes, over the Achilles-conditioned
      stretch/playoff fraction, weighted by P(healthy return).

armd_net(posture) = benefit(posture, step six) - [(a)+(b)+(c)]. Wired as
ARM_COST['ARM-D'] = -armd_net and solved LIVE under both ownership postures
(tax_tolerant base, tax_averse alt), with the convert audit and mass conservation
reported as always. Supersedes step six's deliberately-not-wired ARM-D.

Run:  python board_step7.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "roster_recon"))
import board_step4 as B          # noqa: E402  solver
import board_step6 as X6         # noqa: E402  armd benefit + market multiplier
import joanbet_reconciled as J   # noqa: E402  impacts

# ---- TUNE knobs (labelled) -----------------------------------------------------
DUMP_SWEETENER_BASE = 0.004      # equity cost to place an injured expiring at a normal market (TUNE)
DDV_SALARY = 12.9e6              # DDV expiring
MATCH_DOORWAY = 27.6e6           # DDV + Green, the midsize-deal matching
DDV_SHARE = DDV_SALARY / MATCH_DOORWAY            # ~0.467 of the doorway
DDV_MINUTES_SHARE = 0.083        # ~20 mpg
DDV_STRETCH_FRACTION = 0.35      # stretch run + playoff weight he returns for (Achilles timeline)
DDV_P_HEALTHY = 0.6              # P(meaningful healthy return this season)
TITLE_PER_NET = 0.013            # ~title-equity per net point (from the reconciled delta), TUNE


def ddv_impact(fork):
    import pandas as pd
    d = pd.read_csv(J.REPO / "lamelo" / "data" / "impact" / "player_impact.csv")
    r = d[d.player_id == 1628978].iloc[0]
    return float(r.net_rapm) if fork == "rapm" else float(r.box_net_bpm)


# ---- (a) dump sweetener, mirror of the acquire market --------------------------
def dump_sweetener(market_pct):
    acquire_mult = X6.market_tightness_multiplier(market_pct)     # 0.7 loose .. 1.3 tight
    mirror_mult = (0.7 + 0.6) - (acquire_mult - 0.7)              # reflect around 1.0: tight -> cheap dump
    return DUMP_SWEETENER_BASE * mirror_mult, round(mirror_mult, 3)


# ---- (b) matching-optionality loss ---------------------------------------------
def matching_optionality(fork):
    B.set_fork(fork)
    B.DISABLE_ACQ_ARMS = False
    states = B.reachable()
    v_with, _ = B.solve(states, "cliff")
    B.DISABLE_ACQ_ARMS = True
    v_without, _ = B.solve(states, "cliff")
    B.DISABLE_ACQ_ARMS = False
    acq_option = v_with[B.ROOT] - v_without[B.ROOT]              # value of the acquire doorway
    return DDV_SHARE * max(0.0, acq_option), round(acq_option, 4)


# ---- (c) DDV return value (Achilles-conditioned) -------------------------------
def ddv_return_value(fork):
    net = ddv_impact(fork)
    team_net_contrib = net * DDV_MINUTES_SHARE                    # his share of team net while on floor
    equity = team_net_contrib * DDV_STRETCH_FRACTION * DDV_P_HEALTHY * TITLE_PER_NET
    return equity, round(net, 2)


# ---- assemble + wire live ------------------------------------------------------
def armd_cost(fork, market_pct=0.5):
    a, mirror = dump_sweetener(market_pct)
    b, acq_opt = matching_optionality(fork)
    c, ddv_net = ddv_return_value(fork)
    return dict(sweetener=a, matching=b, return_val=c, total=a + b + c,
                mirror_mult=mirror, acq_option=acq_opt, ddv_net=ddv_net)


def solve_armd_live(fork, posture, market_pct=0.5):
    """Wire ARM-D = -(benefit - EXPLICIT cost) and solve LIVE; report firing + audit + mass.

    EXPLICIT cost = sweetener (a) + return (c) ONLY. The matching-optionality (b) is
    NOT added to the wired cost: the board's node-6 argmax already prices ARM-D
    directly against the acquire arms (ARM-B/ARM-G), so when ARM-D fires instead of
    acquiring, the forgone fit and the resulting convert-mass rise ARE the matching
    loss, realized endogenously. Adding (b) on top would double-count it. (b) is still
    COMPUTED and reported (per the directive), and its endogenous realization is the
    convert-mass delta vs the ARM-D-forced-off solve, below."""
    B.set_fork(fork)
    benefit = X6.armd_value(posture)["arm_d_value_equity"]
    cost = armd_cost(fork, market_pct)
    explicit_cost = cost["sweetener"] + cost["return_val"]          # (a)+(c); (b) is endogenous
    armd_net = benefit - explicit_cost
    base = dict(B.ARM_COST)
    B.ARM_COST = dict(base); B.ARM_COST["ARM-D"] = -armd_net        # negative cost = value gain
    states = B.reachable()
    val, ch = B.solve(states, "cliff")
    dg = B.forward(states, val, ch, "cliff")
    n6 = [s for s in states if B.gi(s, "t") == 6]
    armd_fires = sum(1 for s in n6 if ch[s] == "ARM-D")
    term = _terminal_mass(states, val, ch, "cliff")
    # endogenous matching realization: convert mass with ARM-D removed (forced not to dump)
    B.ARM_COST = dict(base); B.ARM_COST["ARM-D"] = 999.0            # ARM-D off
    val0, ch0 = B.solve(states, "cliff")
    dg0 = B.forward(states, val0, ch0, "cliff")
    B.ARM_COST = base
    return dict(posture=posture, benefit=round(benefit, 4), explicit_cost=round(explicit_cost, 4),
                matching_computed=round(cost["matching"], 4), armd_net=round(armd_net, 4),
                armd_wired_cost=round(-armd_net, 4),
                node6_armd_fires=armd_fires, node6_total=len(n6),
                node6_mode=Counter(ch[s] for s in n6).most_common(1)[0][0],
                convert_mass=round(dg["p_convert"], 4), convert_mass_armd_off=round(dg0["p_convert"], 4),
                matching_endogenous=round(dg["p_convert"] - dg0["p_convert"], 4),
                violations=len(dg["violations"]), terminal_mass=round(term, 6), cost_breakdown=cost)


def _terminal_mass(states, val, ch, curve):
    mass = defaultdict(float); mass[B.ROOT] = 1.0; term = 0.0
    for s in sorted(states, key=lambda x: B.gi(x, "t")):
        m = mass.get(s, 0.0)
        if m <= 0:
            continue
        if B.is_absorbing(s) or B.gi(s, "t") >= 14:
            term += m; continue
        lbl = ch[s]
        if lbl in ("ARM-CONVERT", "expose-Jaden"):
            term += m; continue
        cost, outs = next((c, o) for l, c, o in B.successors(s) if l == lbl)
        p0, t0 = outs[0]
        if p0 in ("HAZARD9", "HAZARD9_EXT"):
            for pw, b in B._hazard9_next_states(s, extended=(p0 == "HAZARD9_EXT")):
                vs = {al: val.get(B._set(b, ant=B.ANT.index(al)), B.terminal_value(B._set(b, ant=B.ANT.index(al)), curve))
                      for al in ("smax_signed", "smax_declined", "default")}
                w = B.stay_split(max(vs.values()), curve); ps = B.sigmoid_commit(sum(w[al] * vs[al] for al in vs), curve)
                for al in ("smax_signed", "smax_declined", "default"):
                    mass[B._set(b, ant=B.ANT.index(al))] += m * pw * ps * w[al]
                mass[B._set(b, ant=B.ANT.index("REQUESTED"))] += m * pw * (1 - ps)
        elif p0 in ("GATE14", "GATE14_EXPOSE"):
            term += m
        else:
            for p, ns in outs:
                mass[ns] += m * p
    return term


def main():
    print("=" * 78)
    print("BOARD BUILD, STEP SEVEN  (ARM-D cost side, wired live)")
    print("=" * 78)
    dump = {"tune": dict(DUMP_SWEETENER_BASE=DUMP_SWEETENER_BASE, DDV_SHARE=round(DDV_SHARE, 3),
                         DDV_STRETCH_FRACTION=DDV_STRETCH_FRACTION, DDV_P_HEALTHY=DDV_P_HEALTHY),
            "forks": {}}
    for fork in ("rapm", "box"):
        print("\n" + "-" * 78)
        print(f"FORK = {fork.upper()}")
        print("-" * 78)
        cost = armd_cost(fork)
        print(f"  ARM-D cost side (normal market): (a) sweetener {cost['sweetener']:.4f} (mirror x{cost['mirror_mult']}) "
              f"| (b) matching {cost['matching']:.4f} (acq option {cost['acq_option']:.4f} x DDV share {DDV_SHARE:.2f}, "
              f"NOT wired -- endogenous) | (c) return {cost['return_val']:.4f} (DDV net {cost['ddv_net']})")
        print(f"     wired explicit cost (a)+(c) = {cost['sweetener']+cost['return_val']:.4f}")
        res = {}
        for posture in ("tax_tolerant", "tax_averse"):
            r = solve_armd_live(fork, posture)
            res[posture] = r
            fires = "FIRES" if r["node6_armd_fires"] > 0 else "does not fire"
            print(f"  [{posture:12s}] benefit {r['benefit']:+.4f} - explicit cost {r['explicit_cost']:.4f} = "
                  f"net {r['armd_net']:+.4f} (wired ARM-D cost {r['armd_wired_cost']:+.4f})")
            print(f"       ARM-D {fires} at node 6 ({r['node6_armd_fires']}/{r['node6_total']}); modal {r['node6_mode']}; "
                  f"convert mass {r['convert_mass']:.4f} (ARM-D off {r['convert_mass_armd_off']:.4f}, "
                  f"endogenous matching cost +{r['matching_endogenous']:.4f}); "
                  f"viol {r['violations']}; term mass {r['terminal_mass']}")
        # market sensitivity of the sweetener (tight vs loose) under averse
        tight_cost = armd_cost(fork, 0.9)["total"]; loose_cost = armd_cost(fork, 0.1)["total"]
        print(f"  market sensitivity (dump sweetener mirror): tight total {tight_cost:.4f} < loose {loose_cost:.4f} "
              f"(tight market = cheaper dump)")
        dump["forks"][fork] = dict(cost=cost, tolerant=res["tax_tolerant"], averse=res["tax_averse"],
                                   tight_cost=tight_cost, loose_cost=loose_cost)

    print("\n" + "=" * 78)
    print("POSTURE SORT (ARM-D live)")
    print("=" * 78)
    for fork in ("rapm", "box"):
        f = dump["forks"][fork]
        print(f"  {fork}: tolerant net {f['tolerant']['armd_net']:+.4f} "
              f"({'fires' if f['tolerant']['node6_armd_fires'] else 'holds'}) | "
              f"averse net {f['averse']['armd_net']:+.4f} "
              f"({'fires' if f['averse']['node6_armd_fires'] else 'holds'})")

    (HERE / "board_step7_out.json").write_text(json.dumps(dump, indent=1, default=float))
    print(f"\nwrote {HERE/'board_step7_out.json'}")
    print("STATUS: step seven runs end to end; ARM-D cost side wired; stop for review.")


if __name__ == "__main__":
    main()
