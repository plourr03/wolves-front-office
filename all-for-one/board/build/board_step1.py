"""Board build, step one (against board_spec v2.0).

Encodes the state space and decision calendar, computes the reachable state
count by forward reachability from the root node, wires transition STUBS with
PLACEHOLDER probabilities, and runs backward induction end to end on FAKE leaf
values to prove the solver scaffold works.

NO real machinery. Every probability and every value here is a placeholder.
The point of step one is: (a) the state space and calendar are encoded exactly
as the spec defines them, (b) reachability pruning (run monotone, RING/REQUESTED
absorbing, chest near-deterministic) lands the reachable set where the spec
predicted ("low thousands"), and (c) backward induction runs over that set.

Run:  python board_step1.py
"""
from __future__ import annotations

from collections import deque
from itertools import product

# ----------------------------------------------------------------- dimensions
# (board_spec v2.0, section 2). Each dimension is a tuple of levels; the state
# stores an index into each.
PERF = ("T1", "T2", "T3", "T4")                       # seed bands
RUN = ("none", "R1", "R2", "WCF", "F", "RING")        # monotone; RING absorbing
MELO_AVAIL = ("A", "B", "C")                          # >=60 / 40-59 / <40 pace
FIT = ("prior", "green", "yellow", "red")
ANT = ("default", "smax_signed", "smax_declined", "REQUESTED")  # REQUESTED absorbing
MELO_DEAL = ("pre_ext", "extended", "walk")
JADEN = ("leap", "steady", "converted", "stalled")
CAP = ("below_tax", "tax_band", "apron1", "apron2")
# chest: only the decision-relevant, reachable sub-fields (the spec's "modest
# set of reachable chest combinations"). Full tuple deferred past step one.
FIRSTS = (0, 1)                                       # firsts_tradeable
PICK2028 = ("swap_pending", "resolved_kept", "resolved_swapped")
UNLOCK = (False, True)                                # unlock_done

# ----------------------------------------------------------------- calendar
# (board_spec v2.0, section 5). node -> (type, short name)
CALENDAR = [
    (0, "decision", "roster fill / LaMelo ext arm / LeBron stub"),
    (1, "decision", "rookie options"),
    (2, "commitment", "TRIPWIRES + jaden_markers freeze; season opens"),
    (3, "read_R1", "advisory tripwire read (~g17-20)"),
    (4, "threshold", "signees trade-eligible"),
    (5, "read_R2", "binding tripwire read (~g36-39)"),
    (6, "decision", "trade deadline 1 (WAIT/ARM-G/ARM-B/ARM-S/UNLOCK/ARM-D)"),
    (7, "chance", "playoffs (run resolves, feeds hazard)"),
    (8, "decision", "draft 2027 (2nd-round only)"),
    (9, "decision", "July 2027: hard cap expires, Ant smax, Jaden tier, cap reset"),
    (10, "decision", "rookie options 2"),
    (11, "read", "season-2 tripwire cycle"),
    (12, "decision", "trade deadline 2 (Gobert expiring hammer)"),
    (13, "chance", "May 2028 lottery (2028 swap resolves)"),
    (14, "gate", "THE GATE: Ant answer, LaMelo/Jaden walk yrs, Gobert, war chest"),
]
NODE_TYPE = {n: t for n, t, _ in CALENDAR}

# state = (t, perf, run, melo_avail, fit, ant, melo_deal, jaden, cap,
#          firsts, pick2028, unlock)
IDX = dict(t=0, perf=1, run=2, melo_avail=3, fit=4, ant=5, melo_deal=6,
           jaden=7, cap=8, firsts=9, pick2028=10, unlock=11)


def is_absorbing(s):
    return RUN[s[IDX["run"]]] == "RING" or ANT[s[IDX["ant"]]] == "REQUESTED"


# --------------------------------------------------------------- root node
# (board_spec v2.0, section 3)
ROOT = (
    0,                       # t
    PERF.index("T2"),        # perf (placeholder projection band)
    RUN.index("none"),       # run
    MELO_AVAIL.index("B"),   # melo_avail (prior from 47-game median)
    FIT.index("prior"),      # fit (no shared-floor data yet)
    ANT.index("default"),    # ant
    MELO_DEAL.index("pre_ext"),
    JADEN.index("steady"),
    CAP.index("apron1"),
    FIRSTS.index(0),
    PICK2028.index("swap_pending"),
    UNLOCK.index(False),
)


def _set(s, **kw):
    s = list(s)
    for k, v in kw.items():
        s[IDX[k]] = v
    return tuple(s)


# --------------------------------------------------- transition stubs (STUB)
# successors(s) -> list of (action_label, [(prob, next_state), ...]).
# Decision nodes expose multiple action_labels; chance/read/etc. expose one
# ("_"). Probabilities are PLACEHOLDERS (uniform-ish); only the STRUCTURE of
# which transitions exist is modeled here.

def successors(s):
    if is_absorbing(s):
        return []                                   # absorbing: terminal
    t = s[IDX["t"]]
    typ = NODE_TYPE[t]
    nt = t + 1

    if typ == "read_R1":
        # fit resolves prior->{green,yellow,red}; melo_avail sets {A,B,C}
        outs = []
        for f in ("green", "yellow", "red"):
            for a in ("A", "B", "C"):
                outs.append((1 / 9, _set(s, t=nt, fit=FIT.index(f),
                                         melo_avail=MELO_AVAIL.index(a))))
        return [("_", outs)]

    if typ == "read_R2":
        # fit may hold or worsen (monotone-ish); melo_avail may hold or drop
        f0 = s[IDX["fit"]]
        fit_opts = sorted({f0, min(f0 + 1, len(FIT) - 1)})
        a0 = s[IDX["melo_avail"]]
        av_opts = sorted({a0, min(a0 + 1, len(MELO_AVAIL) - 1)})
        outs = [(1 / (len(fit_opts) * len(av_opts)), _set(s, t=nt, fit=f, melo_avail=a))
                for f in fit_opts for a in av_opts]
        return [("_", outs)]

    if typ == "chance" and "playoffs" in CALENDAR[t][2]:
        # run advances from 'none' by a placeholder dist over an EFFECTIVE band
        # that folds fit into perf (green fit deepens the run, red shallows it),
        # so a deadline arm that improves fit actually raises title equity.
        fit_adj = {"prior": 0, "green": -1, "yellow": 0, "red": +1}[FIT[s[IDX["fit"]]]]
        eff = max(0, min(len(PERF) - 1, s[IDX["perf"]] + fit_adj))
        dist = {0: [("R2", .2), ("WCF", .35), ("F", .3), ("RING", .15)],   # T1-ish
                1: [("R1", .3), ("R2", .35), ("WCF", .25), ("F", .1)],     # T2-ish
                2: [("R1", .6), ("R2", .3), ("WCF", .1)],                  # T3-ish
                3: [("none", .5), ("R1", .5)]}[eff]                        # T4-ish
        outs = [(p, _set(s, t=nt, run=RUN.index(r))) for r, p in dist]
        return [("_", outs)]

    if typ == "chance":   # lottery (node 13): pick2028 resolves
        outs = [(.5, _set(s, t=nt, pick2028=PICK2028.index("resolved_kept"))),
                (.5, _set(s, t=nt, pick2028=PICK2028.index("resolved_swapped")))]
        return [("_", outs)]

    if t == 6:   # deadline 1: action menu gated by the tripwires
        acts = []
        acts.append(("WAIT", [(1.0, _set(s, t=nt))]))
        # ARM-G (guard depth): placeholder fit improvement, chest unchanged
        acts.append(("ARM-G", [(1.0, _set(s, t=nt, fit=max(1, s[IDX["fit"]] - 1)))]))
        # ARM-B (backup big): placeholder fit improvement
        acts.append(("ARM-B", [(1.0, _set(s, t=nt, fit=max(1, s[IDX["fit"]] - 1)))]))
        # ARM-S (free stagger): small fit nudge, no cost
        acts.append(("ARM-S", [(1.0, _set(s, t=nt, fit=max(1, s[IDX["fit"]] - 1)))]))
        # UNLOCK: flip unlock_done (option purchase)
        if not UNLOCK[s[IDX["unlock"]]]:
            acts.append(("UNLOCK", [(1.0, _set(s, t=nt, unlock=UNLOCK.index(True)))]))
        return acts

    if t == 9:   # July 2027: Ant hazard + Jaden tier + cap reset (season boundary)
        # placeholder: Ant resolves, Jaden tier resolves, perf re-draws for S2
        outs = []
        ant_dist = [("smax_signed", .45), ("smax_declined", .2),
                    ("default", .25), ("REQUESTED", .1)]
        jaden_dist = [("leap", .2), ("steady", .4), ("converted", .2), ("stalled", .2)]
        for al, ap in ant_dist:
            for jl, jp in jaden_dist:
                for pl, pp in [("T1", .3), ("T2", .4), ("T3", .3)]:
                    # run is MONOTONE (deepest result since June 2026), so it is
                    # NOT reset at the season boundary; perf re-draws per season.
                    outs.append((ap * jp * pp,
                                 _set(s, t=nt, ant=ANT.index(al), jaden=JADEN.index(jl),
                                      perf=PERF.index(pl), cap=CAP.index("tax_band"))))
        return [("_", outs)]

    if t == 12:  # deadline 2: Gobert hammer; advance-trade if unlocked
        acts = [("WAIT", [(1.0, _set(s, t=nt))]),
                ("ARM-B2", [(1.0, _set(s, t=nt, fit=max(1, s[IDX["fit"]] - 1)))])]
        if UNLOCK[s[IDX["unlock"]]]:
            acts.append(("advance-trade-2028", [(1.0, _set(s, t=nt, firsts=FIRSTS.index(1)))]))
        return acts

    if typ == "gate":   # node 14: first tradeable first materializes; terminal
        return [("_", [(1.0, _set(s, t=nt, firsts=FIRSTS.index(1)))])] if nt <= 14 else []

    # default decision/threshold/commitment/read nodes: carry forward
    return [("_", [(1.0, _set(s, t=nt))])]


# --------------------------------------------------- forward reachability
def reachable():
    seen = {ROOT}
    q = deque([ROOT])
    edges = 0
    while q:
        s = q.popleft()
        if s[IDX["t"]] >= 14 or is_absorbing(s):
            continue
        for _, outs in successors(s):
            for _, ns in outs:
                edges += 1
                if ns not in seen:
                    seen.add(ns)
                    q.append(ns)
    return seen, edges


# --------------------------------------------------- fake leaf value
def leaf_value(s):
    """PLACEHOLDER title-equity proxy: objective is P(ring while Ant a Wolf).
    Zero if Ant requested out; otherwise a fake monotone function of the deepest
    run and perf band. NOT a real number."""
    if ANT[s[IDX["ant"]]] == "REQUESTED":
        return 0.0
    run_v = {"none": .05, "R1": .08, "R2": .12, "WCF": .25, "F": .45, "RING": 1.0}[RUN[s[IDX["run"]]]]
    perf_v = {"T1": .04, "T2": .02, "T3": .01, "T4": 0.0}[PERF[s[IDX["perf"]]]]
    return min(1.0, run_v + perf_v)


# --------------------------------------------------- backward induction
def solve(states):
    # value by state; process in descending t so successors are done first
    val = {}
    order = sorted(states, key=lambda s: -s[IDX["t"]])
    best_root_action = None
    for s in order:
        if s[IDX["t"]] >= 14 or is_absorbing(s):
            val[s] = leaf_value(s)
            continue
        succ = successors(s)
        if not succ:
            val[s] = leaf_value(s)
            continue
        # decision node: max over actions of expected successor value
        # chance/read node: single "_" action, expected value
        action_vals = []
        for label, outs in succ:
            ev = sum(p * val.get(ns, leaf_value(ns)) for p, ns in outs)
            action_vals.append((ev, label))
        best_ev, best_label = max(action_vals)
        val[s] = best_ev
        if s == ROOT:
            best_root_action = best_label
    return val, best_root_action


def main():
    print("=" * 70)
    print("BOARD BUILD, STEP ONE  (board_spec v2.0)  --  PLACEHOLDER numbers")
    print("=" * 70)
    # naive product (non-t dims) for context
    naive = (len(PERF) * len(RUN) * len(MELO_AVAIL) * len(FIT) * len(ANT) *
             len(MELO_DEAL) * len(JADEN) * len(CAP) * len(FIRSTS) *
             len(PICK2028) * len(UNLOCK))
    print(f"\nstate dimensions: 12 (t + 11 spec dims)")
    print(f"naive per-node product (non-t dims): {naive:,}  x 15 nodes = {naive*15:,}")

    states, edges = reachable()
    print(f"\nREACHABLE state count (from root, with pruning): {len(states):,}")
    print(f"  transition edges traversed: {edges:,}")
    # reachable by node
    from collections import Counter
    byt = Counter(s[IDX['t']] for s in states)
    print("  reachable states per node:")
    for n, _, name in CALENDAR:
        print(f"    node {n:2d} ({NODE_TYPE[n]:11s}): {byt.get(n,0):5d}   {name[:44]}")
    absorb = sum(1 for s in states if is_absorbing(s))
    print(f"  absorbing states in set (RING or REQUESTED): {absorb}")

    val, root_action = solve(states)
    print(f"\nBACKWARD INDUCTION (fake leaf values): ran over {len(val):,} states")
    print(f"  ROOT value (placeholder P(ring while Ant a Wolf)): {val[ROOT]:.4f}")
    print(f"  toy optimal action at node 0: {root_action!r} (node 0 has no action menu in the stub)")
    # demonstrate the max-over-actions logic at a real menu node (deadline 1,
    # node 6) for a red-fit state: acting should beat WAIT under the fake values.
    demo = _set(ROOT, t=6, fit=FIT.index("red"), melo_avail=MELO_AVAIL.index("C"))
    if demo in val:
        acts = successors(demo)
        ranked = sorted(((sum(p * val.get(ns, leaf_value(ns)) for p, ns in outs), lbl)
                         for lbl, outs in acts), reverse=True)
        print(f"  toy optimal action at node 6 (deadline, fit=red, melo=C):")
        for ev, lbl in ranked:
            print(f"      {lbl:20s} EV={ev:.4f}")
    # sanity: a RING leaf should value 1.0, a REQUESTED leaf 0.0
    print("\n  scaffold sanity checks:")
    print(f"    RING leaf value = {leaf_value(_set(ROOT, t=14, run=RUN.index('RING'))):.2f} (expect 1.00)")
    print(f"    REQUESTED leaf value = {leaf_value(_set(ROOT, t=14, ant=ANT.index('REQUESTED'))):.2f} (expect 0.00)")
    print("\nSTATUS: scaffold runs end to end. All probabilities/values are")
    print("placeholders; step two wires real transition stubs, step three")
    print("replaces them one variable at a time (availability first).")


if __name__ == "__main__":
    main()
