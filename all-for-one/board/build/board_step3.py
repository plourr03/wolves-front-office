"""Board build, step three (against board_spec v2.0 + ONE FOR ALL salvage rider).

Wires REAL and INTERIM inputs into the step-two structure, adds the salvage /
ARM-CONVERT objective amendment, and emits the standard diagnostics. Provenance
of every input is labelled, because several are real, several interim, one is
STOPPED, and the rest stay placeholder.

  REAL (from the tripwire backtest):
    - melo_avail prior over {A,B,C} from LaMelo's injury-history reference class
      (A .336 / B .267 / C .397, n=262).
  REAL-ish (from the acceptance model, offseason/partner_acceptance):
    - arm costs: ARM-G needs a ~4-pt sweetener (Tre Jones), ARM-B clears at
      ~0-pt (Robert Williams III / Claxton). So ARM-G costs MORE than ARM-B --
      the inverse of the step-two guess. ARM-D is a salary dump (net relief).
  INTERIM, LABELLED, GATED (from lamelo/ post-trade sim, June 26):
    - leaf title-equity anchor: post-trade Wolves ~0.027 (neutral) .. ~0.037
      (fit-clicks) P(title)/season. GATED (lamelo DELIVERABLE declines to
      publish it), so it anchors the SCALE only, pending a fresh Joan Bet run.
  STOPPED, FLAGGED FOR BOBBY:
    - perf/run transition distributions. These need a FRESH Joan Bet
      (offseason/scripts/bracket_sim.py) run on the POST-TRADE roster. The
      pipeline's default MIN roster is pre-trade (Randle + Reid, no LaMelo); no
      fresh post-trade run exists. Per Bobby's guardrail (do not improvise
      roster inputs), perf/run stays PLACEHOLDER and the requirement is reported.
      Encoded post-trade roster to feed a run: lamelo/data/impact/team_strength.json.
  PLACEHOLDER (TUNE): hazard slope/midpoint/multiplier, arm effects, the salvage
    weight/cap/decay/discount, the interim leaf weights.

ONE FOR ALL salvage rider (Bobby, mid-step-three):
  - departure is no longer worth zero: terminal salvage = SALVAGE_WEIGHT x
    return_quality, CAPPED at SALVAGE_CAP (0.03, Bobby's dial), so no state whose
    stay-continuation exceeds SALVAGE_CAP ever prefers conversion.
  - ARM-CONVERT (proactive Ant trade) at nodes 6, 9, 12, 14, terminal.
  - leverage decay: return_quality falls toward the 2029 walk; REQUESTED
    (involuntary) resolves at a discount vs proactive ARM-CONVERT at the same
    node (the price of hesitation: Utah 2022 vs Minnesota 2007).
  - REQUESTED stays absorbing and involuntary; ARM-CONVERT is the chosen door.

Run:  python board_step3.py
"""
from __future__ import annotations

import math
from collections import deque, Counter, defaultdict

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
    (0, "decision", "roster fill / LaMelo ext arm"),
    (1, "decision", "rookie options"),
    (2, "commitment", "TRIPWIRES + jaden_markers freeze"),
    (3, "read_R1", "advisory tripwire read"),
    (4, "threshold", "signees trade-eligible"),
    (5, "read_R2", "binding tripwire read"),
    (6, "decision", "trade deadline 1 (+ ARM-CONVERT)"),
    (7, "chance", "playoffs (run resolves)"),
    (8, "decision", "draft 2027"),
    (9, "ant_decision", "Jul 2027: season boundary + Ant smax (+ ARM-CONVERT)"),
    (10, "decision", "rookie options 2"),
    (11, "read", "season-2 tripwire cycle"),
    (12, "decision", "trade deadline 2 (+ ARM-CONVERT)"),
    (13, "chance", "May 2028 lottery"),
    (14, "gate", "THE GATE: final Ant answer (+ ARM-CONVERT)"),
]
NODE_TYPE = {n: t for n, t, _ in CALENDAR}
IDX = dict(t=0, perf=1, run=2, melo_avail=3, fit=4, ant=5, melo_deal=6,
           jaden=7, cap=8, firsts=9, pick2028=10, unlock=11)


def gi(s, k):
    return s[IDX[k]]


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


# ------------------------------------------------- REAL: melo_avail prior
MELO_AVAIL_PRIOR = {"A": 0.336, "B": 0.267, "C": 0.397}    # LaMelo injury-history class, backtest

# ------------------------------------------------- hazard (dual curves)
CURVES = {"cliff": dict(midpoint=0.10, slope=35.0),
          "ramp": dict(midpoint=0.08, slope=12.0)}         # ramp = Bobby's robustness curve
SMAX_MULT = 0.3
UNLOCK_COST = 0.020


def sigmoid_commit(equity, curve):
    c = CURVES[curve]
    return 1.0 / (1.0 + math.exp(-c["slope"] * (equity - c["midpoint"])))


def stay_split(equity, curve):
    p = sigmoid_commit(equity, curve)
    w_smax = 0.25 + 0.55 * p
    w_decl = 0.20 * (1 - p)
    return {"smax_signed": w_smax, "smax_declined": w_decl, "default": max(0.0, 1 - w_smax - w_decl)}


# ------------------------------------------------- SALVAGE (ONE FOR ALL rider)
SALVAGE_CAP = 0.03           # Bobby's dial: a stocked rebuild is worth at most this in title odds
SALVAGE_WEIGHT = 0.03        # proactive convert at best leverage == SALVAGE_CAP
INVOLUNTARY_DISCOUNT = 0.6   # REQUESTED salvages worse than proactive: the price of hesitation
LEVERAGE = {6: 1.00, 9: 0.85, 12: 0.70, 14: 0.55}          # decays toward the 2029 walk (TUNE)


def return_quality(node, p_req=0.0):
    return LEVERAGE.get(node, 0.55) * (1.0 - 0.30 * p_req)   # decays with node AND hazard


def proactive_salvage(node, p_req=0.0):
    return min(SALVAGE_CAP, SALVAGE_WEIGHT * return_quality(node, p_req))


def involuntary_salvage(node, p_req=0.0):
    return min(SALVAGE_CAP, SALVAGE_WEIGHT * return_quality(node, p_req) * INVOLUNTARY_DISCOUNT)


# ------------------------------------------------- INTERIM leaf title-equity
# Anchored to lamelo/ post-trade sim (~0.027 neutral), scaled by health. GATED,
# interim, pending a fresh Joan Bet run. Not a published number.
def soft_horizon(s):
    if ANT[gi(s, "ant")] == "REQUESTED":
        return 0.0
    if RUN[gi(s, "run")] == "RING":
        return 1.0
    v = {"none": .015, "R1": .020, "R2": .030, "WCF": .060, "F": .110, "RING": 1.0}[RUN[gi(s, "run")]]
    v += {"T1": .025, "T2": .012, "T3": .004, "T4": 0.0}[PERF[gi(s, "perf")]]
    v += {"leap": .020, "steady": .008, "converted": .004, "stalled": 0.0}[JADEN[gi(s, "jaden")]]
    v += {"extended": .012, "pre_ext": .004, "walk": 0.0}[MELO_DEAL[gi(s, "melo_deal")]]
    v += {"smax_signed": .016, "default": .004, "smax_declined": 0.0, "REQUESTED": 0.0}[ANT[gi(s, "ant")]]
    v += {"below_tax": .008, "tax_band": .004, "apron1": 0.0, "apron2": -.006}[CAP[gi(s, "cap")]]
    v += {"green": .012, "prior": .004, "yellow": 0.0, "red": -.010}[FIT[gi(s, "fit")]]
    v += {"A": .012, "B": .004, "C": -.010}[MELO_AVAIL[gi(s, "melo_avail")]]
    v += .006 if FIRSTS[gi(s, "firsts")] == 1 else 0.0
    return max(0.0, min(1.0, v))


# ------------------------------------------------- REAL-ish arm costs
PT = 0.003                    # 1 acceptance-model asset-pt ~ this much title equity (TUNE)
ARM_COST = {"WAIT": 0.0, "ARM-S": 0.0, "ARM-G": round(4 * PT, 4), "ARM-B": round(1 * PT, 4),
            "ARM-D": -0.008}  # ARM-G (4-pt sweetener) COSTLIER than ARM-B (0-pt): acceptance model


def _fit(s, level):
    return _set(s, fit=FIT.index(level))


def arm_effect(lbl, s):
    if lbl == "ARM-S":
        return _set(s, fit=max(FIT.index("yellow"), gi(s, "fit") - 1))
    if lbl == "ARM-G":
        ns = _set(s, fit=max(FIT.index("green"), gi(s, "fit") - 1))
        if MELO_AVAIL[gi(s, "melo_avail")] == "C":     # guard insurance worth most when LaMelo is out
            ns = _set(ns, melo_avail=MELO_AVAIL.index("B"))
        return ns
    if lbl == "ARM-B":
        return _set(s, fit=min(gi(s, "fit"), FIT.index("green")))
    if lbl == "UNLOCK":
        return _set(s, unlock=UNLOCK.index(True))
    if lbl == "ARM-D":
        return _set(s, cap=max(0, gi(s, "cap") - 1))
    return s


def jaden_dist(perf_label):
    return {"T1": [("leap", .35), ("steady", .35), ("converted", .15), ("stalled", .15)],
            "T2": [("leap", .20), ("steady", .40), ("converted", .20), ("stalled", .20)],
            "T3": [("leap", .10), ("steady", .35), ("converted", .25), ("stalled", .30)]}[perf_label]


CONVERT = "__CONVERT__"


def successors(s):
    if is_absorbing(s):
        return []
    t = gi(s, "t")
    typ = NODE_TYPE[t]
    nt = t + 1
    acts = []

    if t == 0:
        acts.append(("ext-wait", 0.0, [(1.0, _set(s, t=nt))]))
        if MELO_DEAL[gi(s, "melo_deal")] == "pre_ext":
            acts.append(("ext-LaMelo-now", 0.012, [(1.0, _set(s, t=nt, melo_deal=MELO_DEAL.index("extended")))]))
        return acts

    if typ == "read_R1":
        outs = [((1 / 3) * pa, _set(s, t=nt, fit=FIT.index(f), melo_avail=MELO_AVAIL.index(a)))
                for f in ("green", "yellow", "red") for a, pa in MELO_AVAIL_PRIOR.items()]
        return [("_", 0.0, outs)]

    if typ == "read_R2":
        f0, a0 = gi(s, "fit"), gi(s, "melo_avail")
        fo = sorted({f0, min(f0 + 1, len(FIT) - 1)})
        ao = sorted({a0, min(a0 + 1, len(MELO_AVAIL) - 1)})
        outs = [(1 / (len(fo) * len(ao)), _set(s, t=nt, fit=f, melo_avail=a)) for f in fo for a in ao]
        return [("_", 0.0, outs)]

    if t == 6:
        for lbl in ("WAIT", "ARM-S", "ARM-G", "ARM-B", "UNLOCK", "ARM-D"):
            if lbl == "UNLOCK":
                if UNLOCK[gi(s, "unlock")]:
                    continue
                acts.append((lbl, UNLOCK_COST, [(1.0, _set(arm_effect(lbl, s), t=nt))]))
            else:
                acts.append((lbl, ARM_COST[lbl], [(1.0, _set(arm_effect(lbl, s), t=nt))]))
        acts.append(("ARM-CONVERT", 0.0, [(CONVERT, 6)]))
        return acts

    if typ == "chance" and t == 7:   # PLACEHOLDER run dist -- STOPPED pending fresh Joan Bet
        fit_adj = {"prior": 0, "green": -1, "yellow": 0, "red": +1}[FIT[gi(s, "fit")]]
        eff = max(0, min(3, gi(s, "perf") + fit_adj))
        dist = {0: [("R2", .30), ("WCF", .40), ("F", .22), ("RING", .08)],
                1: [("R1", .35), ("R2", .40), ("WCF", .20), ("F", .05)],
                2: [("R1", .60), ("R2", .35), ("WCF", .05)],
                3: [("none", .5), ("R1", .5)]}[eff]
        return [("_", 0.0, [(p, _set(s, t=nt, run=RUN.index(r))) for r, p in dist])]

    if typ == "ant_decision":
        acts.append(("proceed", 0.0, [("HAZARD9", 9)]))
        acts.append(("ARM-CONVERT", 0.0, [(CONVERT, 9)]))
        if MELO_DEAL[gi(s, "melo_deal")] == "pre_ext":
            acts.append(("ext-LaMelo-9", 0.012, [("HAZARD9_EXT", 9)]))
        return acts

    if t == 12:
        acts.append(("WAIT", 0.0, [(1.0, _set(s, t=nt))]))
        f1 = FIT[max(FIT.index("green"), gi(s, "fit") - 1)]
        acts.append(("ARM-B2", 0.02, [(1.0, _set(_fit(s, f1), t=nt))]))
        if UNLOCK[gi(s, "unlock")]:
            acts.append(("advance-trade-2028", 0.005, [(1.0, _set(_fit(s, "green"), t=nt, firsts=FIRSTS.index(1)))]))
        if MELO_DEAL[gi(s, "melo_deal")] == "pre_ext":
            acts.append(("ext-LaMelo-late", 0.012, [(1.0, _set(s, t=nt, melo_deal=MELO_DEAL.index("extended")))]))
        acts.append(("ARM-CONVERT", 0.0, [(CONVERT, 12)]))
        return acts

    if t == 11:
        return [("_", 0.0, [(1 / 3, _set(s, t=nt, fit=FIT.index(f))) for f in ("green", "yellow", "red")])]

    if typ == "chance" and t == 13:
        return [("_", 0.0, [(.5, _set(s, t=nt, pick2028=PICK2028.index("resolved_kept"))),
                            (.5, _set(s, t=nt, pick2028=PICK2028.index("resolved_swapped")))])]

    if typ == "gate":
        return [("proceed", 0.0, [("GATE14", 14)]), ("ARM-CONVERT", 0.0, [(CONVERT, 14)])]

    return [("_", 0.0, [(1.0, _set(s, t=nt))])]


def _hazard9_next_states(s, extended=False):
    """All (perf,jaden,ant) states a node-9 hazard can reach (for reachability +
    forward sim). Shared by reachable() and forward() so they cannot diverge."""
    base0 = _set(s, melo_deal=MELO_DEAL.index("extended")) if extended else s
    nt = gi(s, "t") + 1
    out = []
    for pl, pp in [("T1", .3), ("T2", .4), ("T3", .3)]:
        for jl, jp in jaden_dist(pl):
            b = _set(base0, t=nt, perf=PERF.index(pl), jaden=JADEN.index(jl), cap=CAP.index("tax_band"))
            out.append((pp * jp, b))
    return out


def reachable():
    seen = {ROOT}
    q = deque([ROOT])
    while q:
        s = q.popleft()
        if gi(s, "t") >= 14 or is_absorbing(s):
            continue
        for lbl, _c, outs in successors(s):
            p0, tgt0 = outs[0]              # for special actions p0 is the marker, tgt0 the node
            if p0 == CONVERT:
                continue                     # convert is terminal, not expanded
            if p0 in ("HAZARD9", "HAZARD9_EXT", "GATE14"):
                if p0 == "GATE14":
                    continue                 # gate is terminal (final hazard in solve)
                for _pw, b in _hazard9_next_states(s, extended=(p0 == "HAZARD9_EXT")):
                    for al in ANT:
                        bb = _set(b, ant=ANT.index(al))
                        if bb not in seen:
                            seen.add(bb); q.append(bb)
                continue
            for p, ns in outs:
                if ns not in seen:
                    seen.add(ns); q.append(ns)
    return seen


def node9_resolve(s, val, curve, extended=False):
    inv = involuntary_salvage(9)
    value = eq_m = req_m = 0.0
    for pw, b in _hazard9_next_states(s, extended):
        vs = {}
        for al in ("smax_signed", "smax_declined", "default"):
            k = _set(b, ant=ANT.index(al))
            vs[al] = val[k] if k in val else terminal_value(k, curve)
        w = stay_split(max(vs.values()), curve)
        equity = sum(w[al] * vs[al] for al in vs)
        p_stay = sigmoid_commit(equity, curve)
        value += pw * (p_stay * equity + (1 - p_stay) * inv)   # REQUESTED -> involuntary salvage
        eq_m += pw * equity
        req_m += pw * (1 - p_stay)
    return value, eq_m, req_m


def gate14_value(s, val, curve):
    cont = soft_horizon(_set(s, t=15))
    pd = 1.0 - sigmoid_commit(cont, curve)
    if ANT[gi(s, "ant")] == "smax_signed":
        pd *= SMAX_MULT
    pd = min(1.0, pd)
    return (1 - pd) * cont + pd * involuntary_salvage(14)


def terminal_value(s, curve):
    if ANT[gi(s, "ant")] == "REQUESTED":
        # a REQUESTED absorbing state salvages at the leverage of the node it
        # departed at. All reachable REQUESTED states arise from the node-9 hazard
        # (-> t=10) [node-14 departures are credited inline in gate14_value], so
        # this must match node9_resolve's inline involuntary_salvage(9). Kept
        # t-aware so a future refactor that reads these states stays correct.
        return involuntary_salvage(9 if gi(s, "t") <= 13 else 14)
    if RUN[gi(s, "run")] == "RING":
        return 1.0
    return soft_horizon(s)


def action_value(s, lbl, cost, outs, val, curve):
    p0, tgt0 = outs[0]                       # special actions: p0 is the marker, tgt0 the node
    if p0 == CONVERT:
        ev = proactive_salvage(tgt0)
    elif p0 == "HAZARD9":
        ev = node9_resolve(s, val, curve)[0]
    elif p0 == "HAZARD9_EXT":
        ev = node9_resolve(s, val, curve, extended=True)[0]
    elif p0 == "GATE14":
        ev = gate14_value(s, val, curve)
    else:
        ev = sum(p * val.get(ns, terminal_value(ns, curve)) for p, ns in outs)
    return ev - cost


def solve(states, curve):
    val, choice = {}, {}
    for s in sorted(states, key=lambda x: -gi(x, "t")):
        if is_absorbing(s):
            val[s] = terminal_value(s, curve); continue
        avals = [(action_value(s, lbl, cost, outs, val, curve), lbl)
                 for lbl, cost, outs in successors(s)]
        best, lbl = max(avals)
        val[s], choice[s] = best, lbl
    return val, choice


def forward(states, val, choice, curve):
    """Propagate mass from ROOT under the optimal policy -> P(ring), retention,
    convert audit, live-branch check."""
    mass = defaultdict(float); mass[ROOT] = 1.0
    p_ring = p_convert = retained_s1 = retained_s2 = 0.0
    convert_rows, violations = [], []
    for s in sorted(states, key=lambda x: gi(x, "t")):
        m = mass.get(s, 0.0)
        if m <= 0 or is_absorbing(s):
            if m > 0 and RUN[gi(s, "run")] == "RING":
                p_ring += m
            continue
        t = gi(s, "t")
        lbl = choice[s]
        if lbl == "ARM-CONVERT":
            p_convert += m
            stay = max([action_value(s, l, c, o, val, curve) for l, c, o in successors(s) if l != "ARM-CONVERT"],
                       default=0.0)
            convert_rows.append((t, s, stay, m))
            if stay > SALVAGE_CAP + 1e-9:
                violations.append((t, s, stay))
            continue
        cost, outs = next((c, o) for l, c, o in successors(s) if l == lbl)
        p0, tgt0 = outs[0]
        if p0 in ("HAZARD9", "HAZARD9_EXT"):
            for pw, b in _hazard9_next_states(s, extended=(p0 == "HAZARD9_EXT")):
                vs = {al: val.get(_set(b, ant=ANT.index(al)), terminal_value(_set(b, ant=ANT.index(al)), curve))
                      for al in ("smax_signed", "smax_declined", "default")}
                w = stay_split(max(vs.values()), curve)
                p_stay = sigmoid_commit(sum(w[al] * vs[al] for al in vs), curve)
                for al in ("smax_signed", "smax_declined", "default"):
                    mass[_set(b, ant=ANT.index(al))] += m * pw * p_stay * w[al]
                mass[_set(b, ant=ANT.index("REQUESTED"))] += m * pw * (1 - p_stay)
        elif p0 == "GATE14":
            cont = soft_horizon(_set(s, t=15))
            pd = 1 - sigmoid_commit(cont, curve)
            if ANT[gi(s, "ant")] == "smax_signed":
                pd *= SMAX_MULT
            retained_s2 += m * (1 - min(1, pd))
        else:
            for p, ns in outs:
                mass[ns] += m * p
        if t == 7:
            retained_s1 += m
    return dict(p_ring=p_ring, p_convert=p_convert, retained_s1=retained_s1,
                retained_s2=retained_s2, convert_rows=convert_rows, violations=violations)


def main():
    print("=" * 74)
    print("BOARD BUILD, STEP THREE  (board_spec v2.0 + ONE FOR ALL salvage rider)")
    print("=" * 74)
    print("provenance: melo_avail prior REAL (backtest) | arm costs REAL-ish")
    print("(acceptance model) | leaf equity INTERIM/GATED (lamelo sim) | perf/run")
    print("STOPPED (needs fresh Joan Bet) | hazard+salvage PLACEHOLDER/TUNE")

    states = reachable()
    print(f"\nREACHABLE state count: {len(states):,}")
    byt = Counter(gi(s, "t") for s in states)
    for n, ty, name in CALENDAR:
        print(f"  node {n:2d} ({ty:12s}): {byt.get(n,0):6d}  {name[:34]}")

    print("\n" + "-" * 74)
    print("DUAL-CURVE HARNESS: solve under cliff AND ramp; holds-under-both vs flips")
    print("-" * 74)
    res = {}
    for cv in ("cliff", "ramp"):
        val, choice = solve(states, cv)
        res[cv] = (val, choice, forward(states, val, choice, cv))
        print(f"  [{cv:5s}] root value {val[ROOT]:.4f} | root action {choice[ROOT]!r}")
    val_c, ch_c, dg_c = res["cliff"]; val_r, ch_r, dg_r = res["ramp"]
    node6 = [s for s in states if gi(s, "t") == 6]
    flips = [s for s in node6 if ch_c.get(s) != ch_r.get(s)]
    print(f"  node-6 actions: {len(node6)-len(flips)}/{len(node6)} HOLD under both curves, "
          f"{len(flips)} FLIP")
    for s in flips[:5]:
        print(f"    flip fit={FIT[gi(s,'fit')]:6s} melo={MELO_AVAIL[gi(s,'melo_avail')]}: "
              f"{ch_c.get(s)} (cliff) -> {ch_r.get(s)} (ramp)")

    print("\n" + "-" * 74)
    print("DIAGNOSTICS (cliff policy): P(ring) and P(Ant retained) reported SEPARATELY")
    print("-" * 74)
    print(f"  P(ring while Ant a Wolf):                    {dg_c['p_ring']:.4f}")
    print(f"  P(Ant retained through season 1):            {dg_c['retained_s1']:.4f}")
    print(f"  P(Ant retained through season 2 / commit):   {dg_c['retained_s2']:.4f}")
    print(f"  P(mass reaching a proactive ARM-CONVERT):    {dg_c['p_convert']:.4f}")
    print(f"  (ramp policy: P(ring) {dg_r['p_ring']:.4f}, retained-S1 {dg_r['retained_s1']:.4f})")

    print("\n" + "-" * 74)
    print("CONVERT AUDIT (cliff): states choosing ARM-CONVERT, with stay-continuation")
    print("  CHECKED property: never trades a live branch (stay < SALVAGE_CAP)")
    print("-" * 74)
    rows = sorted(dg_c["convert_rows"], key=lambda r: -r[2])
    print(f"  states choosing ARM-CONVERT: {len(rows)}")
    if rows:
        print(f"  max stay-continuation among converters: {rows[0][2]:.4f}  (SALVAGE_CAP {SALVAGE_CAP})")
        for t_, s, stay, m in rows[:5]:
            print(f"    node {t_:2d} run={RUN[gi(s,'run')]:4s} perf={PERF[gi(s,'perf')]} "
                  f"melo={MELO_AVAIL[gi(s,'melo_avail')]} deal={MELO_DEAL[gi(s,'melo_deal')]}: stay={stay:.4f}")
    viol = dg_c["violations"] + dg_r["violations"]
    print(f"  NEVER-TRADES-A-LIVE-BRANCH: {'PASS' if not viol else 'FAIL '+str(len(viol))}")
    assert not viol, f"live-branch convert: {viol[:5]}"

    print("\n" + "-" * 74)
    print("PRELIMINARY reads (interim/placeholder components named)")
    print("-" * 74)
    global UNLOCK_COST
    save = UNLOCK_COST
    v_with, _ = solve(states, "cliff")
    UNLOCK_COST = 999.0
    v_wo, _ = solve(states, "cliff")
    UNLOCK_COST = save
    print(f"  UNLOCK spread (INTERIM leaf scale, PLACEHOLDER cost): {v_with[ROOT]-v_wo[ROOT]:+.4f}")
    print(f"  LaMelo extension timing (node 0): cliff {ch_c.get(ROOT)!r}, ramp {ch_r.get(ROOT)!r}")
    print(f"    -- PRELIMINARY: melo_avail prior REAL; leaf INTERIM/GATED; ext effect PLACEHOLDER")

    print("\n  sanity checks:")
    print(f"    RING terminal = {terminal_value(_set(ROOT, t=14, run=RUN.index('RING')), 'cliff'):.2f} (1.00)")
    print(f"    REQUESTED salvage = {terminal_value(_set(ROOT, t=14, ant=ANT.index('REQUESTED')), 'cliff'):.4f} "
          f"(>0, capped {SALVAGE_CAP})")
    print(f"    proactive salvage node6 {proactive_salvage(6):.4f} > node14 {proactive_salvage(14):.4f} (leverage decay)")
    print(f"    involuntary {involuntary_salvage(9):.4f} < proactive {proactive_salvage(9):.4f} node9 (hesitation price)")

    print("\n" + "=" * 74)
    print("STOPPED SUB-ITEM (flagged): perf/run needs a FRESH Joan Bet run")
    print("=" * 74)
    print("  offseason/scripts/bracket_sim.py (Component E) exists + runs, but its")
    print("  default MIN roster is PRE-trade (Randle+Reid, no LaMelo). No fresh")
    print("  post-trade run exists (nearest lamelo/ June26 is scalar-delta + GATED).")
    print("  UN-STOP INPUTS: bracket_sim.simulate_league() on MIN's POST-trade lineup")
    print("  (lamelo/data/impact/team_strength.json) reflecting the July final roster")
    print("  (two vet-min spots open) -> per-team title odds + seed bands.")
    print("\nSTATUS: step three runs end to end; provenance labelled; stop for review.")


if __name__ == "__main__":
    main()
