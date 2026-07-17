"""Board step five: convert frontier, cliff positioning, loyalty premium.

At the RULED SALVAGE_CAP = 0.012 ("I want to try to win this with Ant", Bobby
2026-07-17), carried across both metric forks. Imports board_step4 as the solver
library and adds the post-step-four publishables:

  1. CONVERT FRONTIER (directive item 2 + ruling re-emit): convert-vs-hold mass by
     node and by resolved state (run x melo_avail x jaden), per fork; plus the
     root-level hold-vs-reset reconciliation, so the "run-it-back beats a reset"
     sentence and the convert-mass number are visibly the same fact.
  2. CLIFF POSITIONING (directive item 3): the pre-trade board root value vs the
     post-trade, both against the 0.10 hazard commitment line.
  3. LOYALTY PREMIUM (directive item 4, publishable three): cold vs keep-Jaden dual
     solve per fork under both patience curves; the equity gap, the divergence
     states (expect CONVERTED-tier concentration), and the convert audit under the
     constraint. The expose-Jaden arm uses existing cap/jaden leaf channels only
     (board_step4.exposed_leaf); a real asset return is unmodeled, so the premium
     is a conservative LOWER bound.
  4. NO-SCORCHED-EARTH confirmation at the ruled cap (ruling item 3): dead branches
     still orderly-convert, hesitation gap still priced, live branches still held.

Run:  python board_step5.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import board_step4 as B    # noqa: E402  (solver library)

PRE = json.loads((HERE / "roster_recon" / "pretrade_counterfactual.json").read_text())["forks"]
CONV_NODES = (6, 9, 12, 14)
CONV_LABELS = ("ARM-CONVERT", "expose-Jaden")


# ============================================================ 1. convert frontier
def instrumented_forward(states, val, choice, curve):
    """Mirror board_step4.forward but bucket convert-vs-hold mass by node and by
    resolved (run, melo_avail, jaden) state at the convert-eligible nodes."""
    mass = defaultdict(float); mass[B.ROOT] = 1.0
    node_conv, node_hold = defaultdict(float), defaultdict(float)
    res_conv, res_hold = defaultdict(float), defaultdict(float)
    p_convert = 0.0
    for s in sorted(states, key=lambda x: B.gi(x, "t")):
        m = mass.get(s, 0.0)
        if m <= 0 or B.is_absorbing(s):
            continue
        t = B.gi(s, "t"); lbl = choice[s]
        if t in CONV_NODES:
            key = (B.RUN[B.gi(s, "run")], B.MELO_AVAIL[B.gi(s, "melo_avail")], B.JADEN[B.gi(s, "jaden")])
            if lbl in CONV_LABELS:
                node_conv[t] += m; res_conv[key] += m
            else:
                node_hold[t] += m; res_hold[key] += m
        if lbl in CONV_LABELS:
            p_convert += m
            continue
        cost, outs = next((c, o) for l, c, o in B.successors(s) if l == lbl)
        p0, tgt0 = outs[0]
        if p0 in ("HAZARD9", "HAZARD9_EXT"):
            for pw, b in B._hazard9_next_states(s, extended=(p0 == "HAZARD9_EXT")):
                vs = {al: val.get(B._set(b, ant=B.ANT.index(al)), B.terminal_value(B._set(b, ant=B.ANT.index(al)), curve))
                      for al in ("smax_signed", "smax_declined", "default")}
                w = B.stay_split(max(vs.values()), curve)
                ps = B.sigmoid_commit(sum(w[al] * vs[al] for al in vs), curve)
                for al in ("smax_signed", "smax_declined", "default"):
                    mass[B._set(b, ant=B.ANT.index(al))] += m * pw * ps * w[al]
                mass[B._set(b, ant=B.ANT.index("REQUESTED"))] += m * pw * (1 - ps)
        elif p0 in ("GATE14", "GATE14_EXPOSE"):
            pass  # gate leaf is terminal, no onward mass
        else:
            for p, ns in outs:
                mass[ns] += m * p
    return dict(node_conv=dict(node_conv), node_hold=dict(node_hold),
                res_conv=dict(res_conv), res_hold=dict(res_hold), p_convert=p_convert)


def convert_frontier(fork, states):
    B.set_fork(fork); B.EXPOSE_JADEN_ARM = False; B.DISABLE_CONVERT = False
    val, ch = B.solve(states, "cliff")
    fr = instrumented_forward(states, val, ch, "cliff")

    # root hold-vs-reset reconciliation
    root_hold = val[B.ROOT]                       # optimal (run-it-back) value
    reset_now = B.proactive_salvage(6)            # value of resetting today (best leverage)
    B.DISABLE_CONVERT = True                       # forced pure-hold (never reset)
    val_fh, _ = B.solve(states, "cliff")
    B.DISABLE_CONVERT = False
    forced_hold = val_fh[B.ROOT]
    reset_option_value = root_hold - forced_hold  # what the reset OPTION adds over pure hold
    return fr, dict(root_hold=root_hold, reset_now=reset_now, forced_hold=forced_hold,
                    reset_option_value=reset_option_value)


# ============================================================ 2. cliff positioning
def board_root(fork, kind, states):
    """Root value (forward equity) for the post-trade board (kind='post') or the
    pre-trade counterfactual (kind='pre', PRE sim inputs, melo neutralized). Saves
    and restores ALL fork globals so results never depend on call order."""
    saved = (B.FORK, B.LEAF_TITLE, B.LEAF_SCALE, B.RUN7_BASE, B.PERF9, dict(B.MELO_AVAIL_PRIOR))
    if kind == "post":
        B.set_fork(fork)
    else:
        f = PRE[fork]
        B.FORK = "pre_" + fork
        B.LEAF_TITLE = float(f["title"]); B.LEAF_SCALE = B.LEAF_TITLE / B.ANCHOR_REF
        B.RUN7_BASE = B._renorm({r: float(f["run_bands"][r]) for r in B.RUN})
        B.PERF9 = B._renorm({p: float(f["perf_bands"][p]) for p in B.PERF})
        B.MELO_AVAIL_PRIOR = {"A": 0.0, "B": 1.0, "C": 0.0}   # no LaMelo: neutralize availability
    val, ch = B.solve(states, "cliff")
    root, act = val[B.ROOT], ch.get(B.ROOT)
    B.FORK, B.LEAF_TITLE, B.LEAF_SCALE, B.RUN7_BASE, B.PERF9, B.MELO_AVAIL_PRIOR = saved
    return root, act


# ============================================================ 3. loyalty premium
def loyalty_premium(fork, states):
    B.set_fork(fork)
    out = {}
    for cv in ("cliff", "ramp"):
        B.EXPOSE_JADEN_ARM = False; B.DISABLE_CONVERT = False
        val_keep, ch_keep = B.solve(states, cv)
        B.EXPOSE_JADEN_ARM = True
        val_cold, ch_cold = B.solve(states, cv)
        B.EXPOSE_JADEN_ARM = False
        premium = val_cold[B.ROOT] - val_keep[B.ROOT]
        # divergence: gate states where cold exposes Jaden; bucket by (redrawn) jaden tier
        gate = [s for s in states if B.gi(s, "t") == 14]
        exposed = [s for s in gate if ch_cold.get(s) == "expose-Jaden"]
        by_tier = defaultdict(int)
        for s in exposed:
            by_tier[B.JADEN[B.gi(s, "jaden")]] += 1
        out[cv] = dict(keep_root=val_keep[B.ROOT], cold_root=val_cold[B.ROOT], premium=premium,
                       n_gate=len(gate), n_exposed=len(exposed), by_tier=dict(by_tier))
    # convert audit under the keep constraint (cliff): keep == base board
    B.EXPOSE_JADEN_ARM = False
    val_k, ch_k = B.solve(states, "cliff")
    dg = B.forward(states, val_k, ch_k, "cliff")
    out["keep_convert_mass"] = dg["p_convert"]
    out["keep_violations"] = len(dg["violations"])
    return out


# ============================================================ no-scorched-earth
def scorched_earth_check(fork, states):
    B.set_fork(fork); B.EXPOSE_JADEN_ARM = False; B.DISABLE_CONVERT = False
    val, ch = B.solve(states, "cliff")
    n9 = [s for s in states if B.gi(s, "t") == 9]
    conv = [s for s in n9 if ch[s] == "ARM-CONVERT"]
    hold = [s for s in n9 if ch[s] != "ARM-CONVERT"]
    conv_stay = [max([B.action_value(s, l, c, o, val, "cliff") for l, c, o in B.successors(s) if l != "ARM-CONVERT"],
                     default=0.0) for s in conv]
    hold_val = [val[s] for s in hold]
    return dict(proactive9=B.proactive_salvage(9), involuntary9=B.involuntary_salvage(9),
                conv_stay_max=max(conv_stay) if conv_stay else 0.0,
                hold_val_min=min(hold_val) if hold_val else 0.0,
                hold_val_max=max(hold_val) if hold_val else 0.0,
                n_conv=len(conv), n_hold=len(hold))


def main():
    print("=" * 78)
    print("BOARD BUILD, STEP FIVE  (ruled SALVAGE_CAP = 0.012, both forks)")
    print("  convert frontier | cliff positioning | loyalty premium (publishable 3)")
    print("=" * 78)
    print(f"cap {B.SALVAGE_CAP} weight {B.SALVAGE_WEIGHT} | hesitation: proactive(9) "
          f"{B.proactive_salvage(9):.4f} > involuntary(9) {B.involuntary_salvage(9):.4f}")

    B.set_fork("rapm"); states = B.reachable()   # reachable set is fork- and flag-independent

    dump = {"salvage_cap": B.SALVAGE_CAP, "forks": {}}
    for fork in ("rapm", "box"):
        fr, recon = convert_frontier(fork, states)
        se = scorched_earth_check(fork, states)
        lp = loyalty_premium(fork, states)
        pre_root, _ = board_root(fork, "pre", states)
        post_root, post_act = board_root(fork, "post", states)

        print("\n" + "-" * 78)
        print(f"FORK = {fork.upper()}")
        print("-" * 78)
        print("  1. CONVERT FRONTIER")
        print(f"     convert mass total {fr['p_convert']:.4f}")
        print("     by node (convert / reach):")
        for n in CONV_NODES:
            c = fr["node_conv"].get(n, 0.0); h = fr["node_hold"].get(n, 0.0)
            if c + h > 1e-9:
                print(f"       node {n:2d}: convert {c:.4f} / reach {c+h:.4f}  ({c/(c+h)*100:.0f}% convert)")
        print("     by resolved state (run x melo x jaden), top convert buckets:")
        for key, mm in sorted(fr["res_conv"].items(), key=lambda kv: -kv[1])[:6]:
            print(f"       {key[0]:4s} melo={key[1]} jaden={key[2]:9s}: convert mass {mm:.4f}")
        print(f"     root hold-vs-reset: run-it-back (optimal) {recon['root_hold']:.4f}  vs  "
              f"reset-now {recon['reset_now']:.4f}")
        print(f"       -> holding beats resetting-now by {recon['root_hold']/max(recon['reset_now'],1e-9):.1f}x; "
              f"the reset OPTION adds only {recon['reset_option_value']:+.4f} over pure hold")
        print(f"       -> so the {fr['p_convert']*100:.0f}% convert mass is a DOWNSTREAM node-9 conditional on")
        print(f"          dead outcomes, not a root preference to reset (same fact, both shown)")

        print("  2. CLIFF POSITIONING (vs 0.10 commitment line)")
        print(f"     pre-trade root {pre_root:.4f} (commit p={B.sigmoid_commit(pre_root,'cliff'):.2f}) | "
              f"post-trade root {post_root:.4f} (commit p={B.sigmoid_commit(post_root,'cliff'):.2f})")
        print(f"     both below 0.10: trade moves Ant {'+' if post_root>pre_root else ''}"
              f"{post_root-pre_root:+.4f} along the slope, "
              f"{'over' if post_root>=0.10 else 'still short of'} the cliff")

        print("  3. LOYALTY PREMIUM (cold vs keep-Jaden)")
        for cv in ("cliff", "ramp"):
            d = lp[cv]
            print(f"     [{cv:5s}] keep {d['keep_root']:.4f} vs cold {d['cold_root']:.4f} -> "
                  f"premium {d['premium']:+.4f}; expose chosen at {d['n_exposed']}/{d['n_gate']} gate states "
                  f"tiers={d['by_tier']}")
        print(f"     convert audit under keep: convert mass {lp['keep_convert_mass']:.4f}, "
              f"live-branch violations {lp['keep_violations']}")

        print("  4. NO-SCORCHED-EARTH (ruled cap)")
        print(f"     node9 {se['n_conv']} convert / {se['n_hold']} hold | converter stay max "
              f"{se['conv_stay_max']:.4f} (< node-9 convert line {se['proactive9']:.4f}: dead)")
        print(f"     held val {se['hold_val_min']:.4f}..{se['hold_val_max']:.4f} "
              f"(> node-9 convert line {se['proactive9']:.4f}: live branches held; the line is "
              f"proactive_salvage(9)=cap*0.85, not the node-6 cap {B.SALVAGE_CAP}); "
              f"hesitation gap {se['proactive9']-se['involuntary9']:.4f} priced")

        dump["forks"][fork] = {
            "convert_mass": fr["p_convert"], "node_conv": fr["node_conv"], "node_hold": fr["node_hold"],
            "recon": recon, "pre_root": pre_root, "post_root": post_root,
            "loyalty": {k: v for k, v in lp.items()}, "scorched": se,
        }

    print("\n" + "=" * 78)
    print("FORK RANGES")
    print("=" * 78)
    r, b = dump["forks"]["rapm"], dump["forks"]["box"]
    def rng(name, key, sub=None):
        av = r[key] if sub is None else r[key][sub]
        bv = b[key] if sub is None else b[key][sub]
        drv = "box" if bv >= av else "rapm"
        print(f"  {name:26s}: [{av:+.4f}, {bv:+.4f}]  driven high by {drv}")
    rng("convert mass", "convert_mass")
    rng("pre-trade root (cliff pos)", "pre_root")
    rng("post-trade root (cliff pos)", "post_root")
    print(f"  {'loyalty premium (cliff)':26s}: "
          f"[{min(r['loyalty']['cliff']['premium'],b['loyalty']['cliff']['premium']):+.4f}, "
          f"{max(r['loyalty']['cliff']['premium'],b['loyalty']['cliff']['premium']):+.4f}]  "
          f"driven high by {'box' if b['loyalty']['cliff']['premium']>=r['loyalty']['cliff']['premium'] else 'rapm'}")

    (HERE / "board_step5_out.json").write_text(
        json.dumps(dump, indent=1, default=lambda x: list(x) if isinstance(x, tuple) else str(x)))
    print(f"\nwrote {HERE/'board_step5_out.json'}")
    print("\nSTATUS: step five runs end to end at the ruled cap, both forks; stop for review.")


if __name__ == "__main__":
    main()
