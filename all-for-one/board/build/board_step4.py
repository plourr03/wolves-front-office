"""Board build, step FOUR (board_spec v2.1 + ONE FOR ALL salvage rider).

Un-stops the one stopped sub-item from step three: perf/run and leaf title-equity
now come from a REAL Joan Bet (bracket_sim) run on the RECONCILED post-trade roster
(roster_recon/joanbet_reconciled.json), carried BOTH forks (rapm, box) end to end
as first-class scenarios. Every downstream number is reported as a RANGE across the
two forks with the driving fork named.

What changed from step three (board_step3.py):
  UN-STOPPED, now REAL (per fork, from the reconciled bracket_sim run):
    - run transition at node 7: the fork's real run-band distribution (season-1),
      fit-shifted one round deeper/shallower per fit notch. No longer a placeholder.
    - perf re-draw at the node-9 season boundary: the fork's real perf-band
      distribution. No longer a hardcoded T1 .3 / T2 .4 / T3 .3.
    - leaf title-equity ANCHOR: the fork's real bracket_sim title equity
      (rapm ~0.019, box ~0.038) replaces the lamelo interim ~0.027 anchor. The
      file's absolute raw nets are NOT read (only the trade DELTA was, upstream in
      the sim); this consumes the sim's title equity, per Bobby's directive.
  RESEEDED from the Jaden calibration class (jaden_markers_v02.md, ratified):
    - jaden transition priors seeded from the defense-screened class (n=19) tier
      frequencies, so the machine's leap expectation is the historical base rate
      (LEAP 2/19 = 0.105), not hope.
  CARRIED FORWARD unchanged: the hazard-reads-value keystone, the salvage /
    ARM-CONVERT rider with SALVAGE_CAP (now under an anti-tuning clause in the
    spec), the dual-curve harness, the real melo_avail prior, the acceptance-model
    arm costs.

The salvage cap (0.03) is Bobby's values dial and, per the spec anti-tuning clause,
is NOT adjusted in response to these outputs. Where real equity lands near the cap
(the convert-mass finding), that tension is REPORTED, not tuned away.

Run:  python board_step4.py
"""
from __future__ import annotations

import json
import math
from collections import deque, Counter, defaultdict
from pathlib import Path

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


# ============================================================ REAL fork inputs
# The reconciled Joan Bet run (roster_recon/joanbet_reconciled.py -> .json): both
# forks, on the reconciled post-trade roster (phantom Gueye removed). Title equity,
# run bands, perf bands per fork.
RECON = json.loads((Path(__file__).parent / "roster_recon" / "joanbet_reconciled.json").read_text())

# The lamelo INTERIM anchor step three used for the leaf scale (~0.027). Step four
# replaces it, per fork, with the fork's real bracket_sim title equity. Keeping the
# reference makes the swap explicit: LEAF_SCALE == 1.0 reproduces step three.
ANCHOR_REF = 0.027

# fork-parameterized globals, set by set_fork()
FORK = None
LEAF_TITLE = None       # fork bracket_sim title equity -> anchors the leaf scale
LEAF_SCALE = None       # LEAF_TITLE / ANCHOR_REF
RUN7_BASE = None        # fork season-1 run-band dist (neutral fit), renormalized
PERF9 = None            # fork perf-band dist for the node-9 season-boundary re-draw


def _renorm(d):
    tot = sum(d.values())
    return {k: v / tot for k, v in d.items()} if tot > 0 else dict(d)


def set_fork(fork):
    global FORK, LEAF_TITLE, LEAF_SCALE, RUN7_BASE, PERF9
    FORK = fork
    f = RECON["forks"][fork]
    LEAF_TITLE = float(f["title"])
    LEAF_SCALE = LEAF_TITLE / ANCHOR_REF
    RUN7_BASE = _renorm({r: float(f["run_bands"][r]) for r in RUN})
    PERF9 = _renorm({p: float(f["perf_bands"][p]) for p in PERF})


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
# SALVAGE_CAP is Bobby's values dial. Per the board_spec ANTI-TUNING CLAUSE it is
# NOT adjusted in response to solver outputs; equity landing near it is a reported
# finding, not a parameter to move. It changes only by Bobby's logged values ruling.
# RULED 2026-07-17 to 0.012 (was a 0.03 placeholder). Verbatim justification: "I want
# to try to win this with Ant." Values-anchored (Utah 2022 ~1, rebuild median 2-3,
# OKC best 5-6, in title-equity points); solver outputs used ONCE as a disclosed
# consistency check only, no cap adjusted to alter any output. See board_spec v2.3.
SALVAGE_CAP = 0.012          # Bobby's dial (RULED): a stocked rebuild is worth at most this in title odds
SALVAGE_WEIGHT = 0.012       # proactive convert at best leverage (node 6, return_quality 1.0) == SALVAGE_CAP
INVOLUNTARY_DISCOUNT = 0.6   # REQUESTED salvages worse than proactive: the price of hesitation
LEVERAGE = {6: 1.00, 9: 0.85, 12: 0.70, 14: 0.55}          # decays toward the 2029 walk (TUNE)


def return_quality(node, p_req=0.0):
    return LEVERAGE.get(node, 0.55) * (1.0 - 0.30 * p_req)   # decays with node AND hazard


def proactive_salvage(node, p_req=0.0):
    return min(SALVAGE_CAP, SALVAGE_WEIGHT * return_quality(node, p_req))


def involuntary_salvage(node, p_req=0.0):
    return min(SALVAGE_CAP, SALVAGE_WEIGHT * return_quality(node, p_req) * INVOLUNTARY_DISCOUNT)


# ------------------------------------------------- leaf title-equity (fork-anchored)
# Same additive health structure as step three, but the whole additive sum is scaled
# by LEAF_SCALE = (fork bracket_sim title equity) / (lamelo interim anchor 0.027), so
# the leaf lives on the fork's REAL title-equity scale. RING (=1.0) and REQUESTED
# salvage stay ABSOLUTE (a title is a title; salvage is Bobby's dial), so the fork
# scale moves the live-branch leaves relative to the fixed hazard midpoint and cap.
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
    return max(0.0, min(1.0, LEAF_SCALE * v))


# ------------------------------------------------- arm costs
# ARM-G / ARM-B are REAL-ish (acceptance model's required sweeteners: ARM-G needs a
# ~4-pt sweetener, ARM-B clears at ~0). ARM-D is a PLACEHOLDER, not acceptance-model
# derived. Step three carried it as a benefit-only -0.008 (a tax/repeater-reset
# credit), but the three-lens verification showed that on the marginal fork it made
# ARM-D a reflexive deadline dump chosen unanimously: its modeled state effect (cap
# relief) has NO valued channel here (cap washes out at the node-9 reset and the
# only cap-sensitive leaf is past that reset), and its real cost side (dump
# sweetener, loss of Green+DDV matching, DDV's healthy-branch return) is unmodeled.
# So a free negative cost was buying an unsubstantiated dump. Set NET-ZERO until
# ARM-D earns a real valued cap channel and a cost side. See board_step4_report.md.
PT = 0.003                    # 1 acceptance-model asset-pt ~ this much title equity (TUNE)
ARM_COST = {"WAIT": 0.0, "ARM-S": 0.0, "ARM-G": round(4 * PT, 4), "ARM-B": round(1 * PT, 4),
            "ARM-D": 0.0}     # PLACEHOLDER net-zero (was -0.008 benefit-only; see note above)


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


# ------------------------------------------------- jaden priors (class-seeded)
# Seeded from the DEFENSE-SCREENED Jaden calibration class (jaden_markers_v02.md,
# n=19, ratified 2026-07-17). Class tier frequencies: LEAP 2/19 = 0.105 (Barnes,
# Crowder, at one growth signal), CONVERTED ~1/19 (Huerter: gate-fail + offensive
# leap), STALLED ~6/19 (the JO-FLOOR trippers), STEADY the remainder (~10/19, the
# Anunoby/Bridges gate-pass-and-hold that the doc calls the realistic prior). The
# T2 band is PINNED to the class base rate (leap 0.11); perf tilts it modestly. The
# unconditional class base rate is 0.105; once conditioned on the reconciled team's
# real perf re-draw (mostly T3/T4), the fork-AVERAGED leap is 0.079 (rapm) to 0.096
# (box) -- at or BELOW the base rate, i.e. conditioning on a middling team lowers
# the leap expectation further. That is the "not hope" direction (conservative), not
# a violation of it. T4 added for the real re-draw, which now carries lottery mass.
def jaden_dist(perf_label):
    return {"T1": [("leap", .14), ("steady", .56), ("converted", .05), ("stalled", .25)],
            "T2": [("leap", .11), ("steady", .53), ("converted", .05), ("stalled", .31)],
            "T3": [("leap", .07), ("steady", .45), ("converted", .06), ("stalled", .42)],
            "T4": [("leap", .03), ("steady", .32), ("converted", .05), ("stalled", .60)]}[perf_label]


CONVERT = "__CONVERT__"

# ------------------------------------------------- loyalty premium (step five)
# The keep-Jaden vs cold comparison (loyalty premium, publishable three). Default
# OFF so steps 1-4 are unchanged. When ON, the gate (node 14, Jaden's walk year:
# "extend or expose") offers an expose-Jaden arm. Its economics use ONLY existing
# channels -- the leaf loses Jaden's tier bonus and gains one band of cap relief
# (node 14 -> leaf t=15 is direct, so the cap change is valued, unlike ARM-D). A
# real Jaden-trade asset return is NOT modeled (per the do-not-improvise rule), so
# the expose value here is a LOWER bound and the loyalty premium a conservative one.
EXPOSE_JADEN_ARM = False

# step-five diagnostic (default OFF): remove ARM-CONVERT from every menu, forcing a
# pure-hold (never-reset) solve. Used only to price how much the reset OPTION adds
# over running it back to the end -- the root hold-vs-reset reconciliation.
DISABLE_CONVERT = False


def exposed_leaf(s):
    """Leaf continuation if Jaden is exposed (traded/walked) at the gate: his tier
    bonus removed (jaden -> stalled, bonus 0) plus one band of cap relief. Existing
    channels only; asset return unmodeled -> conservative."""
    s2 = _set(s, jaden=JADEN.index("stalled"), cap=max(0, gi(s, "cap") - 1))
    return soft_horizon(_set(s2, t=15))


# ------------------------------------------------- run-band fit shift
RUN_FIT_SHIFT = 0.15   # fraction of run mass moved one round deeper/shallower per fit notch (TUNE)


def shift_run(bands, k):
    """Move |k| fraction of mass one round deeper (k>0, toward RING) or shallower
    (k<0, toward none) along RUN. Endpoints absorb. Used to fit-adjust the fork's
    real season-1 run bands at node 7 (green fit deepens the run, red flattens it)."""
    order = list(RUN)
    b = {r: float(bands.get(r, 0.0)) for r in order}
    if abs(k) < 1e-12:
        return b
    out = {r: 0.0 for r in order}
    for i, r in enumerate(order):
        m = b[r]
        if k > 0 and i < len(order) - 1:
            out[order[i + 1]] += m * k
            out[r] += m * (1 - k)
        elif k < 0 and i > 0:
            out[order[i - 1]] += m * (-k)
            out[r] += m * (1 + k)
        else:
            out[r] += m
    return out


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
        if not DISABLE_CONVERT:
            acts.append(("ARM-CONVERT", 0.0, [(CONVERT, 6)]))
        return acts

    if typ == "chance" and t == 7:   # REAL run dist: fork season-1 run bands, fit-shifted
        # perf is fixed at T2 for season 1 (root), so only fit shifts the base bands.
        fit_adj = {"prior": 0, "green": -1, "yellow": 0, "red": +1}[FIT[gi(s, "fit")]]
        dist = shift_run(RUN7_BASE, -fit_adj * RUN_FIT_SHIFT)   # green (-1) -> deeper; red (+1) -> shallower
        return [("_", 0.0, [(p, _set(s, t=nt, run=RUN.index(r))) for r, p in dist.items() if p > 1e-12])]

    if typ == "ant_decision":
        acts.append(("proceed", 0.0, [("HAZARD9", 9)]))
        if not DISABLE_CONVERT:
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
        if not DISABLE_CONVERT:
            acts.append(("ARM-CONVERT", 0.0, [(CONVERT, 12)]))
        return acts

    if t == 11:
        return [("_", 0.0, [(1 / 3, _set(s, t=nt, fit=FIT.index(f))) for f in ("green", "yellow", "red")])]

    if typ == "chance" and t == 13:
        return [("_", 0.0, [(.5, _set(s, t=nt, pick2028=PICK2028.index("resolved_kept"))),
                            (.5, _set(s, t=nt, pick2028=PICK2028.index("resolved_swapped")))])]

    if typ == "gate":
        acts = [("proceed", 0.0, [("GATE14", 14)])]
        if not DISABLE_CONVERT:
            acts.append(("ARM-CONVERT", 0.0, [(CONVERT, 14)]))
        if EXPOSE_JADEN_ARM:
            acts.append(("expose-Jaden", 0.0, [("GATE14_EXPOSE", 14)]))
        return acts

    return [("_", 0.0, [(1.0, _set(s, t=nt))])]


def _hazard9_next_states(s, extended=False):
    """All (perf,jaden,ant) states a node-9 hazard can reach. perf now uses the
    fork's REAL perf-band re-draw (PERF9); jaden from the class-seeded priors."""
    base0 = _set(s, melo_deal=MELO_DEAL.index("extended")) if extended else s
    nt = gi(s, "t") + 1
    # July 2027: Green + DDV (~27.6M) clear and the hard cap expires, so the payroll
    # eases toward the tax band. Model that as cap -> min(current, tax_band): an
    # apron team drops to tax_band, but a team that dumped BELOW the tax (ARM-D)
    # STAYS below it. (Was an unconditional tax_band, which silently erased ARM-D's
    # cap relief -- caught by the step-four three-lens verification.)
    cap9 = min(gi(base0, "cap"), CAP.index("tax_band"))
    out = []
    for pl in PERF:
        pp = PERF9.get(pl, 0.0)
        if pp <= 0:
            continue
        for jl, jp in jaden_dist(pl):
            b = _set(base0, t=nt, perf=PERF.index(pl), jaden=JADEN.index(jl), cap=cap9)
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
            if p0 in ("HAZARD9", "HAZARD9_EXT", "GATE14", "GATE14_EXPOSE"):
                if p0 in ("GATE14", "GATE14_EXPOSE"):
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


def gate14_value(s, val, curve, expose=False):
    cont = exposed_leaf(s) if expose else soft_horizon(_set(s, t=15))
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
    elif p0 == "GATE14_EXPOSE":
        ev = gate14_value(s, val, curve, expose=True)
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
        elif p0 in ("GATE14", "GATE14_EXPOSE"):
            cont = exposed_leaf(s) if p0 == "GATE14_EXPOSE" else soft_horizon(_set(s, t=15))
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


def run_fork_board(fork):
    """Solve + diagnose the whole board for one metric fork under both curves."""
    set_fork(fork)
    states = reachable()
    out = {"fork": fork, "leaf_title": LEAF_TITLE, "leaf_scale": round(LEAF_SCALE, 4),
           "n_states": len(states)}
    res = {}
    for cv in ("cliff", "ramp"):
        val, choice = solve(states, cv)
        res[cv] = (val, choice, forward(states, val, choice, cv))
    val_c, ch_c, dg_c = res["cliff"]; val_r, ch_r, dg_r = res["ramp"]

    node6 = [s for s in states if gi(s, "t") == 6]
    flips = [s for s in node6 if ch_c.get(s) != ch_r.get(s)]

    # preliminary reads (per fork): UNLOCK price sweep + LaMelo extension timing
    global UNLOCK_COST
    save = UNLOCK_COST
    v_with, _ = solve(states, "cliff")
    UNLOCK_COST = 999.0
    v_wo, _ = solve(states, "cliff")
    UNLOCK_COST = save

    rows = sorted(dg_c["convert_rows"], key=lambda r: -r[2])
    # Guardrail, made non-tautological: among convert-ELIGIBLE states (the nodes
    # where ARM-CONVERT is on the menu), the max continuation value of those that
    # DECLINED to convert. If this sits well above SALVAGE_CAP, live branches are
    # being actively held rather than trivially below the cap -- the guardrail is
    # doing real work, not just passing by construction. (The converter-side check
    # in forward() stays as the clamp-regression guard.)
    conv_nodes = {6, 9, 12, 14}
    held = [val_c[s] for s in states if gi(s, "t") in conv_nodes and ch_c.get(s) not in (None, "ARM-CONVERT")]
    out.update({
        "root_cliff": val_c[ROOT], "root_ramp": val_r[ROOT],
        "root_action_cliff": ch_c.get(ROOT), "root_action_ramp": ch_r.get(ROOT),
        "node6_hold": len(node6) - len(flips), "node6_total": len(node6), "node6_flip": len(flips),
        "node6_action_mode": Counter(ch_c.get(s) for s in node6).most_common(1)[0],
        "p_ring_cliff": dg_c["p_ring"], "p_ring_ramp": dg_r["p_ring"],
        "retained_s1": dg_c["retained_s1"], "retained_s2": dg_c["retained_s2"],
        "convert_mass_cliff": dg_c["p_convert"], "convert_mass_ramp": dg_r["p_convert"],
        "convert_states": len(rows),
        "convert_max_stay": rows[0][2] if rows else 0.0,
        "held_live_max": max(held) if held else 0.0,   # live branch that declined convert
        "violations": dg_c["violations"] + dg_r["violations"],
        "unlock_spread": v_with[ROOT] - v_wo[ROOT],
        "flips": flips,
    })
    return out, res, states


def _rng(a, b, ah, bh):
    """(low, high, driving-high fork) for a pair of fork values a (rapm), b (box)."""
    return (min(a, b), max(a, b), bh if b >= a else ah)


def main():
    print("=" * 78)
    print("BOARD BUILD, STEP FOUR  (board_spec v2.1 + ONE FOR ALL salvage rider)")
    print("  perf/run/title UN-STOPPED: real reconciled Joan Bet, BOTH forks first-class")
    print("=" * 78)
    print("provenance: run/perf/title REAL per fork (reconciled bracket_sim) | melo_avail")
    print("prior REAL (backtest) | ARM-G/ARM-B costs REAL-ish (acceptance model), ARM-D")
    print("PLACEHOLDER net-zero | jaden priors class-seeded (screened n=19) |")
    print("hazard/salvage PLACEHOLDER/TUNE (cap under the board_spec anti-tuning clause)")

    forks = {}
    for fk in ("rapm", "box"):
        o, res, states = run_fork_board(fk)
        forks[fk] = o
        print("\n" + "-" * 78)
        print(f"FORK = {fk.upper()}   leaf title equity {o['leaf_title']:.4f}  "
              f"(leaf scale x{o['leaf_scale']} vs the 0.027 lamelo anchor)")
        print("-" * 78)
        print(f"  states {o['n_states']:,} | root value cliff {o['root_cliff']:.4f} "
              f"ramp {o['root_ramp']:.4f}")
        print(f"  root action: {o['root_action_cliff']!r} (cliff) / {o['root_action_ramp']!r} (ramp)")
        print(f"  node-6 actions: {o['node6_hold']}/{o['node6_total']} HOLD under both curves, "
              f"{o['node6_flip']} FLIP")
        for s in o["flips"][:4]:
            print(f"    flip fit={FIT[gi(s,'fit')]:6s} melo={MELO_AVAIL[gi(s,'melo_avail')]}")
        print("  diagnostics (cliff), P(ring) and P(retained) reported SEPARATELY:")
        print(f"    P(ring while Ant a Wolf):                  {o['p_ring_cliff']:.4f}")
        print(f"    P(Ant retained through season 1):          {o['retained_s1']:.4f}")
        print(f"    P(Ant retained through season 2 / commit): {o['retained_s2']:.4f}")
        print(f"    P(mass reaching a proactive ARM-CONVERT):  {o['convert_mass_cliff']:.4f}")
        print(f"  node-6 modal action: {o['node6_action_mode'][0]} "
              f"({o['node6_action_mode'][1]}/{o['node6_total']})")
        print(f"  convert audit: {o['convert_states']} states choose ARM-CONVERT, "
              f"max stay among converters {o['convert_max_stay']:.4f} (cap {SALVAGE_CAP})")
        print(f"    guardrail real work: max continuation among convert-eligible states that")
        print(f"    HELD (declined convert) = {o['held_live_max']:.4f}  "
              f"({'>' if o['held_live_max'] > SALVAGE_CAP else '<='} cap {SALVAGE_CAP}: "
              f"{'live branches actively protected' if o['held_live_max'] > SALVAGE_CAP else 'no live branch above cap'})")
        print(f"    NEVER-TRADES-A-LIVE-BRANCH: {'PASS' if not o['violations'] else 'FAIL'}")
        assert not o["violations"], f"[{fk}] live-branch convert: {o['violations'][:3]}"
        assert all(proactive_salvage(n) <= SALVAGE_CAP + 1e-12 for n in (6, 9, 12, 14)), "salvage clamp broke"
        print("  preliminary reads (per fork, labelled):")
        print(f"    UNLOCK spread (real leaf scale, PLACEHOLDER unlock cost): {o['unlock_spread']:+.4f}")
        print(f"    LaMelo extension timing (node 0): {o['root_action_cliff']} (cliff) / "
              f"{o['root_action_ramp']} (ramp)")

    print("\n" + "=" * 78)
    print("FORK RANGES (low, high, driving-high fork) -- every headline is a range")
    print("=" * 78)
    r, b = forks["rapm"], forks["box"]
    range_keys = [
        ("leaf title equity", "leaf_title"),
        ("root value (cliff)", "root_cliff"),
        ("P(ring) (cliff)", "p_ring_cliff"),
        ("P(Ant retained S2)", "retained_s2"),
        ("convert mass (cliff)", "convert_mass_cliff"),
        ("UNLOCK spread", "unlock_spread"),
    ]
    for name, key in range_keys:
        lo, hi, drv = _rng(r[key], b[key], "rapm", "box")
        print(f"  {name:22s}: [{lo:+.4f}, {hi:+.4f}]  driven high by {drv}")
    print(f"  {'root action (cliff)':22s}: rapm {r['root_action_cliff']!r} / box {b['root_action_cliff']!r}")
    print(f"  {'node-6 holds':22s}: rapm {r['node6_hold']}/{r['node6_total']} / "
          f"box {b['node6_hold']}/{b['node6_total']}")

    print("\n  CONVERT-MASS FINDING (reported, not tuned -- anti-tuning clause):")
    print(f"    rapm convert mass {r['convert_mass_cliff']:.3f} (leaf scale x{r['leaf_scale']}) vs "
          f"box {b['convert_mass_cliff']:.3f} (x{b['leaf_scale']}).")
    print("    The fork disagreement IS the finding: on the rapm read the reconciled")
    print("    team is marginal enough that many live branches sit at the salvage cap")
    print("    (rebuild competitive); on the box read leaves clear the cap and holding")
    print("    dominates. SALVAGE_CAP is unchanged; the tension is surfaced, per spec.")

    # write machine-readable
    dump = {"anchor_ref": ANCHOR_REF, "salvage_cap": SALVAGE_CAP, "run_fit_shift": RUN_FIT_SHIFT,
            "forks": {fk: {k: v for k, v in o.items() if k not in ("flips",)} for fk, o in forks.items()}}
    outp = Path(__file__).parent / "board_step4_out.json"
    outp.write_text(json.dumps(dump, indent=1, default=lambda x: list(x) if isinstance(x, tuple) else str(x)))
    print(f"\nwrote {outp}")
    print("\nSTATUS: step four runs end to end on the reconciled roster, both forks")
    print("first-class; perf/run/title un-stopped and real; stop for review.")


if __name__ == "__main__":
    main()
