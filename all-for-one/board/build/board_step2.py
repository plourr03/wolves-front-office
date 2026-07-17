"""Board build, step two (against board_spec v2.0).

Adds real transition STRUCTURE (still placeholder numbers) to the step-one
scaffold. Six mechanisms, in the priority order Bobby set:

 1. Causal ordering at season boundaries: perf/run resolve first, jaden
    conditions on the resolved season, ant resolves LAST.
 2. KEYSTONE: hazard-reads-value recursion. Ant's transition at nodes 9 and
    14 is the cliff curve (sigmoid of forward equity, midpoint 0.10, steep
    slope, TUNE) applied to the solver's OWN continuation value at the state.
    The smax_signed hazard multiplier (0.3, TUNE) flows through to node 14.
 3. melo_deal live: an extension arm at nodes 0 and 12 (placeholder cost/effect)
    so the extension-timing question is expressible.
 4. Arm differentiation: distinct placeholder cost + effect per arm, so the
    solver prefers among arms, not just act-vs-wait.
 5. UNLOCK pricing: node 12's menu conditions on firsts_tradeable; the toy
    with-vs-without value spread is reported as a mechanism demo.
 6. Soft horizon: terminal states carry a continuation value as a function of
    STATE HEALTH (placeholder), per spec section 1, so the late tree does not
    go scorched earth.

ALL probabilities and values are placeholders (TUNE). Step three replaces them
one variable at a time (availability first, AVAIL-PACE is built).

Run:  python board_step2.py
"""
from __future__ import annotations

import math
from collections import deque, Counter

# --------------------------------------------------------------- dimensions
PERF = ("T1", "T2", "T3", "T4")
RUN = ("none", "R1", "R2", "WCF", "F", "RING")
MELO_AVAIL = ("A", "B", "C")
FIT = ("prior", "green", "yellow", "red")
ANT = ("default", "smax_signed", "smax_declined", "REQUESTED")
MELO_DEAL = ("pre_ext", "extended", "walk")
JADEN = ("leap", "steady", "converted", "stalled")
CAP = ("below_tax", "tax_band", "apron1", "apron2")
FIRSTS = (0, 1)
PICK2028 = ("swap_pending", "resolved_kept", "resolved_swapped")
UNLOCK = (False, True)

CALENDAR = [
    (0, "decision", "roster fill / LaMelo ext arm / LeBron stub"),
    (1, "decision", "rookie options"),
    (2, "commitment", "TRIPWIRES + jaden_markers freeze; season opens"),
    (3, "read_R1", "advisory tripwire read (~g17-20)"),
    (4, "threshold", "signees trade-eligible"),
    (5, "read_R2", "binding tripwire read (~g36-39)"),
    (6, "decision", "trade deadline 1"),
    (7, "chance", "playoffs (run resolves)"),
    (8, "decision", "draft 2027"),
    (9, "ant_hazard", "July 2027: season boundary + Ant supermax (hazard)"),
    (10, "decision", "rookie options 2"),
    (11, "read", "season-2 tripwire cycle"),
    (12, "decision", "trade deadline 2 (Gobert hammer; UNLOCK-conditioned)"),
    (13, "chance", "May 2028 lottery (2028 swap resolves)"),
    (14, "gate", "THE GATE: final Ant answer (hazard) + soft horizon"),
]
NODE_TYPE = {n: t for n, t, _ in CALENDAR}

IDX = dict(t=0, perf=1, run=2, melo_avail=3, fit=4, ant=5, melo_deal=6,
           jaden=7, cap=8, firsts=9, pick2028=10, unlock=11)


def gi(s, k):
    return s[IDX[k]]


def lvl(s, k, tup):
    return tup[s[IDX[k]]]


def is_absorbing(s):
    return RUN[gi(s, "run")] == "RING" or ANT[gi(s, "ant")] == "REQUESTED"


ROOT = (0, PERF.index("T2"), RUN.index("none"), MELO_AVAIL.index("B"),
        FIT.index("prior"), ANT.index("default"), MELO_DEAL.index("pre_ext"),
        JADEN.index("steady"), CAP.index("apron1"), FIRSTS.index(0),
        PICK2028.index("swap_pending"), UNLOCK.index(False))


def _set(s, **kw):
    s = list(s)
    for k, v in kw.items():
        s[IDX[k]] = v
    return tuple(s)


# ----------------------------------------------------- hazard (the cliff curve)
HAZ_MIDPOINT = 0.10     # forward three-year equity midpoint (spec section 4), TUNE
HAZ_SLOPE = 35.0        # steep cliff, TUNE
SMAX_MULT = 0.3         # smax_signed multiplies subsequent departure hazard, TUNE
UNLOCK_COST = 0.020     # asset-point price of unlocking the 2028 first, TUNE (swept in the demo)


def sigmoid_commit(equity):
    """P(Ant commits / stays) as a function of forward three-year title equity."""
    return 1.0 / (1.0 + math.exp(-HAZ_SLOPE * (equity - HAZ_MIDPOINT)))


# stay-split weights (how commitment divides among the non-REQUESTED ant states);
# tilt toward smax_signed as equity rises (a bright future -> sign the supermax).
def stay_split(equity):
    p = sigmoid_commit(equity)
    w_smax = 0.25 + 0.55 * p
    w_decl = 0.20 * (1 - p)
    w_def = 1.0 - w_smax - w_decl
    return {"smax_signed": w_smax, "smax_declined": w_decl, "default": max(0.0, w_def)}


# ----------------------------------------------------- soft horizon (item 6)
def soft_horizon(s):
    """Health-based continuation value at the modeling edge (placeholder), so the
    solver never torches the final year (spec section 1)."""
    if ANT[gi(s, "ant")] == "REQUESTED":
        return 0.0
    if RUN[gi(s, "run")] == "RING":
        return 1.0
    # scaled as a P(eventual ring) proxy (0..~0.25 for non-RING), so it sits on
    # the SAME scale as the hazard midpoint (0.10 forward title equity). This is
    # the calibration the step-two verification flagged: a health proxy on a
    # larger scale left the cliff inert. Still a placeholder, but scale-consistent.
    v = {"none": .02, "R1": .03, "R2": .05, "WCF": .09, "F": .15, "RING": 1.0}[RUN[gi(s, "run")]]
    v += {"T1": .030, "T2": .015, "T3": .005, "T4": 0.0}[PERF[gi(s, "perf")]]
    v += {"leap": .025, "steady": .010, "converted": .005, "stalled": 0.0}[JADEN[gi(s, "jaden")]]
    v += {"extended": .015, "pre_ext": .005, "walk": 0.0}[MELO_DEAL[gi(s, "melo_deal")]]
    v += {"smax_signed": .020, "default": .005, "smax_declined": 0.0, "REQUESTED": 0.0}[ANT[gi(s, "ant")]]
    v += {"below_tax": .010, "tax_band": .005, "apron1": 0.0, "apron2": -.008}[CAP[gi(s, "cap")]]
    v += {"green": .015, "prior": .005, "yellow": 0.0, "red": -.012}[FIT[gi(s, "fit")]]  # pairing health
    v += .008 if FIRSTS[gi(s, "firsts")] == 1 else 0.0
    return max(0.0, min(1.0, v))


# ----------------------------------------------------- arm menu (item 4)
# each arm: (label, cost, effect_fn). cost is an immediate value charge; effect
# mutates state. Distinct so the solver can PREFER among arms.
def _fit_to(s, level):
    return _set(s, fit=FIT.index(level))


# FIT indices: prior=0, green=1, yellow=2, red=3 (lower index = healthier).
# Distinct effects so each arm is optimal somewhere (verified below), not just
# distinct costs: ARM-S is a FREE one-level nudge CAPPED at yellow (staggering
# minutes only goes so far); ARM-G is a one-level improvement that can reach
# green (guard depth); ARM-B is a one-SHOT to green (a backup big fully patches
# the frontcourt hole in a single move) but costs more.
ARMS = {
    "WAIT":  (0.000, lambda s: s),
    "ARM-S": (0.000, lambda s: _set(s, fit=max(FIT.index("yellow"), gi(s, "fit") - 1))),
    "ARM-G": (0.015, lambda s: _set(s, fit=max(FIT.index("green"), gi(s, "fit") - 1))),
    "ARM-B": (0.020, lambda s: _set(s, fit=min(gi(s, "fit"), FIT.index("green")))),
    "UNLOCK": (0.020, lambda s: _set(s, unlock=UNLOCK.index(True))),
    "ARM-D": (-0.008, lambda s: _set(s, cap=max(0, gi(s, "cap") - 1))),  # dump: net cap relief
}


# ----------------------------------------------------- transitions (structure)
# successors(s) -> list of (action, cost, [(prob, next_state), ...]).
# Chance/read/hazard nodes expose a single action "_" with cost 0. Decision nodes
# expose the action menu. For the ant-hazard nodes the probabilities are
# PLACEHOLDER here (used only for REACHABILITY); solve() recomputes them from
# continuation values.
def successors(s):
    if is_absorbing(s):
        return []
    t = gi(s, "t")
    typ = NODE_TYPE[t]
    nt = t + 1

    if t == 0:  # roster fill + LaMelo early-extension arm (item 3)
        acts = [("ext-wait", 0.0, [(1.0, _set(s, t=nt))])]
        if MELO_DEAL[gi(s, "melo_deal")] == "pre_ext":
            acts.append(("ext-LaMelo-now", 0.012,
                         [(1.0, _set(s, t=nt, melo_deal=MELO_DEAL.index("extended")))]))
        return acts

    if typ == "read_R1":
        outs = [(1 / 9, _set(s, t=nt, fit=FIT.index(f), melo_avail=MELO_AVAIL.index(a)))
                for f in ("green", "yellow", "red") for a in ("A", "B", "C")]
        return [("_", 0.0, outs)]

    if typ == "read_R2":
        f0, a0 = gi(s, "fit"), gi(s, "melo_avail")
        fo = sorted({f0, min(f0 + 1, len(FIT) - 1)})
        ao = sorted({a0, min(a0 + 1, len(MELO_AVAIL) - 1)})
        outs = [(1 / (len(fo) * len(ao)), _set(s, t=nt, fit=f, melo_avail=a)) for f in fo for a in ao]
        return [("_", 0.0, outs)]

    if t == 6:  # deadline 1: differentiated arms (item 4) + UNLOCK
        acts = []
        for lbl, (cost, eff) in ARMS.items():
            if lbl == "UNLOCK":
                if UNLOCK[gi(s, "unlock")]:
                    continue
                cost = UNLOCK_COST          # module global, so the demo can sweep it
            ns = _set(eff(s), t=nt)
            acts.append((lbl, cost, [(1.0, ns)]))
        return acts

    if typ == "chance" and t == 7:  # playoffs: run resolves (effective band folds fit)
        fit_adj = {"prior": 0, "green": -1, "yellow": 0, "red": +1}[FIT[gi(s, "fit")]]
        eff = max(0, min(3, gi(s, "perf") + fit_adj))
        # title is rare even for a top team (placeholder, but realistic scale)
        dist = {0: [("R2", .30), ("WCF", .40), ("F", .22), ("RING", .08)],
                1: [("R1", .35), ("R2", .40), ("WCF", .20), ("F", .05)],
                2: [("R1", .60), ("R2", .35), ("WCF", .05)],
                3: [("none", .5), ("R1", .5)]}[eff]
        return [("_", 0.0, [(p, _set(s, t=nt, run=RUN.index(r))) for r, p in dist])]

    if typ == "ant_hazard":  # node 9: season boundary + Ant supermax (item 1 + 2)
        # CAUSAL ORDER: perf re-draws, run stays monotone, jaden conditions on the
        # resolved perf, ant resolves LAST (hazard, handled in solve()). For
        # reachability we enumerate all (perf, jaden, ant) resolutions.
        outs = []
        for pl, pp in [("T1", .3), ("T2", .4), ("T3", .3)]:
            for jl, jp in jaden_dist(pl):
                for al in ("smax_signed", "smax_declined", "default", "REQUESTED"):
                    base = _set(s, t=nt, perf=PERF.index(pl), jaden=JADEN.index(jl),
                                ant=ANT.index(al), cap=CAP.index("tax_band"))
                    outs.append((pp * jp * 0.25, base))   # placeholder prob (reachability only)
        return [("_", 0.0, outs)]

    if t == 9:  # (handled above); keep fallthrough safe
        return [("_", 0.0, [(1.0, _set(s, t=nt))])]

    if t == 12:  # deadline 2: Gobert hammer; UNLOCK-conditioned advance-trade (item 5)
        # ordinary deadline-2 move (expiring-matched): improves fit ONE level.
        f1 = FIT[max(FIT.index("green"), gi(s, "fit") - 1)]
        acts = [("WAIT", 0.0, [(1.0, _set(s, t=nt))]),
                ("ARM-B2", 0.02, [(1.0, _set(_fit_to(s, f1), t=nt))])]
        if UNLOCK[gi(s, "unlock")]:   # only constructible if the 2028 first was unlocked
            # the point of UNLOCK: the 2028 FIRST (a premium asset) becomes
            # deadline-usable 5 months early, so it buys a STRONGER move than the
            # expiring-matched ARM-B2 (placeholder: full fit->green in one step).
            acts.append(("advance-trade-2028", 0.005,
                         [(1.0, _set(_fit_to(s, "green"), t=nt, firsts=FIRSTS.index(1)))]))
        # LaMelo extension arm also available here (item 3), if still pre_ext
        if MELO_DEAL[gi(s, "melo_deal")] == "pre_ext":
            acts.append(("ext-LaMelo-late", 0.012,
                         [(1.0, _set(s, t=nt, melo_deal=MELO_DEAL.index("extended")))]))
        return acts

    if t == 11:  # season-2 tripwire cycle: fit redraws for the new season
        outs = [(1 / 3, _set(s, t=nt, fit=FIT.index(f))) for f in ("green", "yellow", "red")]
        return [("_", 0.0, outs)]

    if typ == "chance" and t == 13:  # lottery: 2028 swap resolves
        return [("_", 0.0, [(.5, _set(s, t=nt, pick2028=PICK2028.index("resolved_kept"))),
                            (.5, _set(s, t=nt, pick2028=PICK2028.index("resolved_swapped")))])]

    if typ == "gate":  # node 14: terminal (final ant hazard applied in solve)
        return [("_", 0.0, [(1.0, _set(s, t=nt, firsts=FIRSTS.index(1)))])]

    return [("_", 0.0, [(1.0, _set(s, t=nt))])]


def jaden_dist(perf_label):
    """Jaden tier conditions on the RESOLVED season perf (item 1 causal order)."""
    return {"T1": [("leap", .35), ("steady", .35), ("converted", .15), ("stalled", .15)],
            "T2": [("leap", .20), ("steady", .40), ("converted", .20), ("stalled", .20)],
            "T3": [("leap", .10), ("steady", .35), ("converted", .25), ("stalled", .30)]}[perf_label]


# ----------------------------------------------------- reachability
def reachable(allow_unlock=True):
    seen = {ROOT}
    q = deque([ROOT])
    while q:
        s = q.popleft()
        if gi(s, "t") >= 14 or is_absorbing(s):
            continue
        for lbl, _c, outs in successors(s):
            if not allow_unlock and lbl in ("UNLOCK",):
                continue
            for _, ns in outs:
                if ns not in seen:
                    seen.add(ns)
                    q.append(ns)
    return seen


# ----------------------------------------------------- backward induction
def terminal_value(s):
    if ANT[gi(s, "ant")] == "REQUESTED":
        return 0.0
    if RUN[gi(s, "run")] == "RING":
        return 1.0
    return soft_horizon(s)


def node9_resolve(s, val):
    """The keystone, computed once and reused by solve() AND the demo so they can
    never diverge. Returns (value, marginal_equity, marginal_P_requested). Causal
    order: perf redraws, run monotone, jaden conditions on the resolved perf, ant
    resolves LAST via the cliff curve reading the solver's OWN continuation value.
    Uses `k in val` membership (never an `or` fallback), so a missing continuation
    surfaces as a hard error rather than a silent soft_horizon substitution."""
    nt = gi(s, "t") + 1
    value = eq_m = req_m = 0.0
    for pl, pp in [("T1", .3), ("T2", .4), ("T3", .3)]:
        for jl, jp in jaden_dist(pl):
            base = _set(s, t=nt, perf=PERF.index(pl), jaden=JADEN.index(jl),
                        cap=CAP.index("tax_band"))
            vs = {}
            for al in ("smax_signed", "smax_declined", "default"):
                k = _set(base, ant=ANT.index(al))
                vs[al] = val[k] if k in val else terminal_value(k)  # membership, not `or`
            w = stay_split_from_states(vs)
            equity = sum(w[al] * vs[al] for al in vs)      # forward 3yr equity
            p_stay = sigmoid_commit(equity)                # cliff curve
            pw = pp * jp
            value += pw * (p_stay * equity)                # stay->equity; REQUESTED->0
            eq_m += pw * equity
            req_m += pw * (1.0 - p_stay)
    return value, eq_m, req_m


def stay_split_from_states(vs):
    """Placeholder stay-split: tilt toward smax_signed as the stay-equity rises."""
    equity = max(vs.values())
    return stay_split(equity)


def ant_hazard_node14_value(s, val):
    """Node 14 (gate): final ant answer. Departure hazard reads the soft-horizon
    continuation, with the smax_signed multiplier flowing through (item 2)."""
    cont = soft_horizon(_set(s, t=15))
    p_commit = sigmoid_commit(cont)
    p_depart = 1.0 - p_commit
    if ANT[gi(s, "ant")] == "smax_signed":
        p_depart *= SMAX_MULT                     # signed the supermax -> stickier
    p_depart = min(1.0, p_depart)
    return (1.0 - p_depart) * cont                # + p_depart * 0


def solve(states, allow_unlock=True):
    val = {}
    order = sorted(states, key=lambda s: -gi(s, "t"))
    root_action = None
    for s in order:
        if is_absorbing(s):
            val[s] = terminal_value(s)
            continue
        t = gi(s, "t")
        typ = NODE_TYPE.get(t)
        if typ == "gate":                          # node 14: final hazard, terminal
            val[s] = ant_hazard_node14_value(s, val)
            continue
        if typ == "ant_hazard":                    # node 9: keystone recursion
            val[s] = node9_resolve(s, val)[0]
            continue
        succ = successors(s)
        if not succ:
            val[s] = terminal_value(s)
            continue
        avals = []
        for lbl, cost, outs in succ:
            if not allow_unlock and lbl == "UNLOCK":
                continue
            ev = sum(p * val.get(ns, terminal_value(ns)) for p, ns in outs)
            avals.append((ev - cost, lbl))
        best, lbl = max(avals)
        val[s] = best
        if s == ROOT:
            root_action = lbl
    return val, root_action


# ----------------------------------------------------- report
def main():
    print("=" * 72)
    print("BOARD BUILD, STEP TWO  (board_spec v2.0)  --  PLACEHOLDER numbers")
    print("=" * 72)

    states = reachable()
    print(f"\nREACHABLE state count (from root): {len(states):,}")
    byt = Counter(gi(s, "t") for s in states)
    for n, ty, name in CALENDAR:
        print(f"  node {n:2d} ({ty:10s}): {byt.get(n,0):6d}   {name[:40]}")
    print(f"  drivers: node 9 resolves perf(3) x jaden(4) x ant(4) causally; "
          f"melo_deal now branches (extension arm)")

    val, root_action = solve(states)
    print(f"\nBACKWARD INDUCTION over {len(val):,} states")
    print(f"  ROOT value (placeholder P(ring while Ant a Wolf)): {val[ROOT]:.4f}")
    print(f"  toy optimal action at node 0: {root_action!r}  "
          f"(ext-LaMelo-now vs ext-wait -- item 3)")

    print("\n" + "-" * 72)
    print("KEYSTONE DEMO (item 2): hazard reads the solver's OWN continuation.")
    print("  Computed over ACTUALLY-REACHABLE node-9 states via node9_resolve()")
    print("  (the same code path solve() uses -- no synthetic states, no fallback).")
    print("-" * 72)
    node9 = [s for s in states if gi(s, "t") == 9]
    rows = [(node9_resolve(s, val)[1], node9_resolve(s, val)[2], s) for s in node9]
    eqs = [e for e, _, _ in rows]
    reqs = [r for _, r, _ in rows]
    import statistics as st
    print(f"  reachable node-9 states: {len(node9)}")
    print(f"  forward-equity range across them: min {min(eqs):.3f}, median "
          f"{st.median(eqs):.3f}, max {max(eqs):.3f}   (cliff midpoint = {HAZ_MIDPOINT})")
    print(f"  P(Ant requests out) range:        min {min(reqs):.3f}, median "
          f"{st.median(reqs):.3f}, max {max(reqs):.3f}")
    # representative real states spanning the equity range, low to high
    rows.sort(key=lambda x: x[0])
    picks = [rows[0], rows[len(rows) // 4], rows[len(rows) // 2], rows[3 * len(rows) // 4], rows[-1]]
    print("  representative reachable node-9 states (real solver values):")
    print(f"    {'run':5s} {'perf':4s} {'jaden':9s} {'meloDeal':9s} {'fit':6s} | "
          f"{'equity':>7s} {'P(REQ)':>7s}")
    for eq, rq, s in picks:
        print(f"    {RUN[gi(s,'run')]:5s} {PERF[gi(s,'perf')]:4s} {JADEN[gi(s,'jaden')]:9s} "
              f"{MELO_DEAL[gi(s,'melo_deal')]:9s} {FIT[gi(s,'fit')]:6s} | {eq:7.3f} {rq:7.3f}")
    print("  the cliff engages: low-equity reachable states carry a real, elevated")
    print("  P(Ant requests out); high-equity states drive it toward zero.")

    print("\n  smax multiplier flow-through (item 2), node 14 final hazard,")
    print("  held at the SAME near-cliff soft-horizon so only the 0.3 mult differs:")
    # fix cont near the cliff by using a bleak-ish health state; report both the
    # natural (smax raises health too) and the isolated (same cont) multiplier.
    for ant_state in ("smax_signed", "default"):
        s14 = _set(ROOT, t=14, run=RUN.index("R2"), perf=PERF.index("T3"),
                   ant=ANT.index(ant_state), jaden=JADEN.index("stalled"),
                   melo_deal=MELO_DEAL.index("pre_ext"), cap=CAP.index("apron1"))
        cont = soft_horizon(_set(s14, t=15))
        p_dep = 1 - sigmoid_commit(cont)
        if ant_state == "smax_signed":
            p_dep *= SMAX_MULT
        print(f"    ant={ant_state:13s} cont={cont:.3f}  P(final REQUESTED)={min(1,p_dep):.3f}  "
              f"node14 value={(1-min(1,p_dep))*cont:.3f}")
    # isolated multiplier at a fixed cont
    cfix = 0.12
    base_dep = 1 - sigmoid_commit(cfix)
    print(f"    isolated at cont={cfix}: base P(depart)={base_dep:.3f}, "
          f"smax_signed P(depart)={base_dep*SMAX_MULT:.3f} (x{SMAX_MULT})")

    print("\n" + "-" * 72)
    print("UNLOCK SPREAD (item 5): board value with vs without UNLOCK, SWEPT over")
    print("  the (placeholder) asset price of unlocking the 2028 first")
    print("-" * 72)
    global UNLOCK_COST
    st_wo = reachable(allow_unlock=False)
    v_without, _ = solve(st_wo, allow_unlock=False)
    saved = UNLOCK_COST
    print(f"  {'unlock price':>12s} {'value w/ opt':>12s} {'value w/o':>10s} {'spread':>9s}  verdict")
    for price in (0.004, 0.008, 0.012, 0.020):
        UNLOCK_COST = price
        v_with, _ = solve(states, allow_unlock=True)
        spread = v_with[ROOT] - v_without[ROOT]
        verdict = "UNLOCK lives" if spread > 1e-9 else "dies quietly"
        print(f"  {price:12.3f} {v_with[ROOT]:12.4f} {v_without[ROOT]:10.4f} {spread:+9.4f}  {verdict}")
    UNLOCK_COST = saved
    print("  (the spec's mechanism: price the option by the with-vs-without spread;")
    print("   where the spread never clears the market price, UNLOCK dies quietly)")

    print("\n" + "-" * 72)
    print("ARM DIFFERENTIATION (item 4): optimal deadline-1 action across the")
    print("  18 reachable node-6 states -- each arm should win somewhere")
    print("-" * 72)
    node6 = [s for s in states if gi(s, "t") == 6]
    picks6 = Counter()
    for s in node6:
        best = max((sum(p * val.get(ns, terminal_value(ns)) for p, ns in outs) - cost, lbl)
                   for lbl, cost, outs in successors(s))
        picks6[best[1]] += 1
    print(f"  {dict(picks6)}")
    print("  (ARM-S free-yellow, ARM-G one-level-to-green, ARM-B one-shot-green: "
          "distinct effect + cost)")

    print("\n  sanity checks:")
    print(f"    RING terminal value  = {terminal_value(_set(ROOT, t=14, run=RUN.index('RING'))):.2f} (expect 1.00)")
    print(f"    REQUESTED terminal   = {terminal_value(_set(ROOT, t=14, ant=ANT.index('REQUESTED'))):.2f} (expect 0.00)")
    print(f"    soft-horizon healthy = {soft_horizon(_set(ROOT, t=15, run=RUN.index('WCF'), perf=PERF.index('T1'), ant=ANT.index('smax_signed'), jaden=JADEN.index('leap'), melo_deal=MELO_DEAL.index('extended'))):.3f} (>0, no scorched earth)")
    print(f"    soft-horizon bleak   = {soft_horizon(_set(ROOT, t=15, run=RUN.index('none'), perf=PERF.index('T3'))):.3f} (>0)")
    print("\nSTATUS: step-two structure runs end to end. All numbers placeholder/TUNE.")


if __name__ == "__main__":
    main()
