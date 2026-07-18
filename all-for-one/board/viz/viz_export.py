"""Stage 0 of the ONE FOR ALL board visualization: the data export.

Countdown-compatible: consumes the solver as a READ-ONLY library (imports board_step4,
solves, forward-samples), makes ZERO solver edits, and emits board_viz_export.json for
the composition spikes and the eventual interactive build.

Export schema (per the directive):
  meta      : fork weights (the fork-adjudication prior), salvage cap, p_east, source
              tag (SOLVER here; SYNTHETIC if ever hand-faked), curve, generated stamp.
  nodes     : the decision calendar (id, t, type, name).
  forks[f]  : traces  -> 400 weight-tagged forward samples, each with an event-CODE
                         stream, per-node health + equity, a per-column `sid` (the
                         solver's reachable-state encoding -- the LATTICE KEY, v6),
                         and a terminal class.
              node_health -> per-node mass distribution over health bands.
              terminals   -> mass by terminal class (RING / REQUESTED / CONVERT@n /
                             EXPOSE / leaf-<run>).
  realized  : [] -- empty until the R1/R2 reads land in-season; the shape is fixed so
              the renderer can light up the realized path without a schema change.

Sampling is a seeded forward Monte Carlo that mirrors board_step4.forward() exactly
(same chance/hazard/gate transition math), so 400 equal-weight samples reproduce the
policy's mass distribution. Deterministic given the seed.

Run:  python viz_export.py
"""
from __future__ import annotations
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent / "build"
sys.path.insert(0, str(BUILD))
sys.path.insert(0, str(BUILD / "roster_recon"))
import board_step4 as B          # noqa: E402  READ-ONLY solver library
import board_step6 as X6         # noqa: E402  for p_east

N_TRACES = 400
CURVE = "cliff"
SEED = 20260717
FORK_WEIGHTS = {"rapm": 0.5, "box": 0.5}   # fork-adjudication freeze prior (agnostic)

HAZ = ("smax_signed", "smax_declined", "default")


def health(s):
    """Composite 0..1 state health for the radial/folded renders: fit, perf, LaMelo
    availability, and run depth, blended. 1 = healthiest (center/short path)."""
    fit = {"green": 1.0, "prior": 0.6, "yellow": 0.4, "red": 0.0}[B.FIT[B.gi(s, "fit")]]
    perf = {"T1": 1.0, "T2": 0.66, "T3": 0.33, "T4": 0.0}[B.PERF[B.gi(s, "perf")]]
    avail = {"A": 1.0, "B": 0.5, "C": 0.0}[B.MELO_AVAIL[B.gi(s, "melo_avail")]]
    run = {"none": 0.3, "R1": 0.45, "R2": 0.6, "WCF": 0.8, "F": 0.9, "RING": 1.0}[B.RUN[B.gi(s, "run")]]
    return round(0.30 * fit + 0.25 * perf + 0.20 * avail + 0.25 * run, 3)


def health_band(h):
    return "green" if h >= 0.66 else ("yellow" if h >= 0.4 else "red")


def sid(s):
    """The LATTICE KEY: the solver's own reachable-state encoding, verbatim.

    A state is the 12-tuple indexed by B.IDX; this is its lossless string form. Two traces
    carrying the same sid at the same column ARE in the same state -- the renderer must draw
    them as one channel, which is what makes convergence (merging) visible rather than
    discarded. Nothing here is derived or bucketed; it is the solver's key."""
    return "-".join(str(int(v)) for v in s)


def _node_rec(s, val):
    return {"t": int(B.gi(s, "t")), "type": B.NODE_TYPE.get(B.gi(s, "t"), ""),
            "sid": sid(s),
            "health": health(s), "band": health_band(health(s)),
            "equity": round(float(val.get(s, B.terminal_value(s, CURVE))), 4),
            "run": B.RUN[B.gi(s, "run")], "fit": B.FIT[B.gi(s, "fit")],
            "melo": B.MELO_AVAIL[B.gi(s, "melo_avail")], "jaden": B.JADEN[B.gi(s, "jaden")],
            "ant": B.ANT[B.gi(s, "ant")]}


def _code(lbl, s_next=None):
    m = {"ext-LaMelo-now": "EXT", "ext-LaMelo-9": "EXT", "ext-LaMelo-late": "EXT",
         "ARM-G": "ARMG", "ARM-B": "ARMB", "ARM-B2": "ARMB", "ARM-D": "ARMD", "ARM-S": "ARMS",
         "UNLOCK": "UNLOCK", "WAIT": "WAIT", "ext-wait": "WAIT", "proceed": "PROCEED",
         "advance-trade-2028": "ADV28"}
    return m.get(lbl, lbl.upper())


def sample_trace(fork, val, choice, rng, tid):
    s = B.ROOT
    path, codes = [], []
    terminal = "leaf"
    guard = 0
    while True:
        guard += 1
        if guard > 40:
            terminal = "GUARD"; break
        path.append(_node_rec(s, val))
        t = B.gi(s, "t")
        if B.is_absorbing(s):
            terminal = "RING" if B.RUN[B.gi(s, "run")] == "RING" else "REQUESTED"
            break
        # no `t >= 14` short-circuit: node 14 (the gate) is a DECISION state; read its
        # choice so the gate commit-vs-depart split (GATE14) actually runs.
        lbl = choice[s]
        cost, outs = next((c, o) for l, c, o in B.successors(s) if l == lbl)
        p0, tgt0 = outs[0]

        if p0 == B.CONVERT:
            codes.append("CONVERT"); terminal = f"CONVERT@{t}"; break
        if p0 in ("HAZARD9", "HAZARD9_EXT"):
            if lbl == "ext-LaMelo-9":
                codes.append("EXT")
            # sample perf/jaden re-draw
            hs = B._hazard9_next_states(s, extended=(p0 == "HAZARD9_EXT"))
            ws = np.array([pw for pw, _ in hs], float); ws /= ws.sum()
            _, b = hs[rng.choice(len(hs), p=ws)]
            # sample Ant stay-split vs REQUESTED
            vs = {al: val.get(B._set(b, ant=B.ANT.index(al)), B.terminal_value(B._set(b, ant=B.ANT.index(al)), CURVE)) for al in HAZ}
            w = B.stay_split(max(vs.values()), CURVE)
            p_stay = B.sigmoid_commit(sum(w[al] * vs[al] for al in vs), CURVE)
            codes.append("PERF_" + B.PERF[B.gi(b, "perf")])
            codes.append("JAD_" + B.JADEN[B.gi(b, "jaden")].upper()[:4])
            if rng.random() < (1 - p_stay):
                s = B._set(b, ant=B.ANT.index("REQUESTED")); codes.append("REQ")
            else:
                wp = np.array([w[a] for a in HAZ], float); wp = wp / wp.sum()
                al = HAZ[rng.choice(len(HAZ), p=wp)]
                s = B._set(b, ant=B.ANT.index(al))
                codes.append({"smax_signed": "SMAX", "smax_declined": "DECLINE", "default": "STAY"}[al])
            continue
        if p0 in ("GATE14", "GATE14_EXPOSE"):
            expose = (p0 == "GATE14_EXPOSE")
            if expose:
                codes.append("EXPOSE")
            cont = B.exposed_leaf(s) if expose else B.soft_horizon(B._set(s, t=15))
            pd = 1 - B.sigmoid_commit(cont, CURVE)
            if B.ANT[B.gi(s, "ant")] == "smax_signed":
                pd *= B.SMAX_MULT
            pd = min(1.0, pd)
            path.append({"t": 15, "type": "leaf", "sid": sid(B._set(s, t=15)),
                         "health": health(s), "band": health_band(health(s)),
                         "equity": round(float(cont), 4), "run": B.RUN[B.gi(s, "run")], "fit": B.FIT[B.gi(s, "fit")],
                         "melo": B.MELO_AVAIL[B.gi(s, "melo_avail")], "jaden": B.JADEN[B.gi(s, "jaden")], "ant": B.ANT[B.gi(s, "ant")]})
            if rng.random() < pd:
                terminal = "REQUESTED"; codes.append("REQ_GATE")
            else:
                terminal = "leaf-committed" + ("-exposed" if expose else "")
            break

        # ordinary chance / deterministic transition: sample by probability
        probs = np.array([p for p, _ in outs], float); probs = probs / probs.sum()
        idx = rng.choice(len(outs), p=probs)
        s2 = outs[idx][1]
        # emit codes for the informative dimensions that changed
        if lbl not in ("_",):
            codes.append(_code(lbl, s2))
        if t == 7:                                   # run resolved
            codes.append("RUN_" + B.RUN[B.gi(s2, "run")])
        # EVERY read node, not just the advisory one. R2 (t=5) is the BINDING read and t=11 is
        # the season-2 cycle; emitting only read_R1 left a degradation at the binding read
        # invisible to anything reading the code stream (the audit's ADVERSE test, notably).
        # Change-guarded after t=3 so the stream stays an event log, not a state dump.
        if B.NODE_TYPE.get(t) in ("read_R1", "read_R2", "read"):
            if t == 3 or B.gi(s2, "melo_avail") != B.gi(s, "melo_avail"):
                codes.append("AVAIL_" + B.MELO_AVAIL[B.gi(s2, "melo_avail")])
            if t == 3 or B.gi(s2, "fit") != B.gi(s, "fit"):
                codes.append("FIT_" + B.FIT[B.gi(s2, "fit")][0].upper())
        s = s2
    return {"id": f"{fork[:1]}{tid}", "fork": fork, "weight": round(1.0 / N_TRACES, 6),
            "path": path, "codes": codes, "terminal": terminal}


def exact_aggregates(states, val, choice):
    """Node-health mass and terminal masses computed EXACTLY from the solver's forward
    mass (not the 400-trace sample), so the viz's aggregate numbers are accurate while
    the traces stay a visual sample. Mirrors board_step4.forward() transition math."""
    mass = defaultdict(float); mass[B.ROOT] = 1.0
    node_health = defaultdict(lambda: defaultdict(float))
    terminals = defaultdict(float)
    for s in sorted(states, key=lambda x: B.gi(x, "t")):
        m = mass.get(s, 0.0)
        if m <= 0:
            continue
        node_health[B.gi(s, "t")][health_band(health(s))] += m
        if B.is_absorbing(s):
            terminals["RING" if B.RUN[B.gi(s, "run")] == "RING" else "REQUESTED"] += m
            continue
        t = B.gi(s, "t")
        # NOTE: no `t >= 14` short-circuit -- node 14 (the gate) is a DECISION state; its
        # choice (proceed->GATE14 / ARM-CONVERT / expose) must be read so the commit-vs-
        # depart split runs, exactly as board_step4.forward() does. (An earlier guard here
        # dead-coded the gate handler and dumped all gate mass into leaf-<run>.)
        lbl = choice[s]
        # ARM-CONVERT is the only terminal choice. expose-Jaden is NOT: the solver prices it
        # through gate14_value(expose=True), a commit-vs-depart split, and forward() has no
        # expose special-case at all. Short-circuiting it here would book 100% of expose mass
        # as an exit and dead-code the GATE14_EXPOSE half of the branch below.
        if lbl == "ARM-CONVERT":
            terminals[f"CONVERT@{t}"] += m
            continue
        cost, outs = next((c, o) for l, c, o in B.successors(s) if l == lbl)
        p0, tgt0 = outs[0]
        if p0 in ("HAZARD9", "HAZARD9_EXT"):
            for pw, b in B._hazard9_next_states(s, extended=(p0 == "HAZARD9_EXT")):
                vs = {al: val.get(B._set(b, ant=B.ANT.index(al)), B.terminal_value(B._set(b, ant=B.ANT.index(al)), CURVE)) for al in HAZ}
                w = B.stay_split(max(vs.values()), CURVE); ps = B.sigmoid_commit(sum(w[al] * vs[al] for al in vs), CURVE)
                for al in HAZ:
                    mass[B._set(b, ant=B.ANT.index(al))] += m * pw * ps * w[al]
                mass[B._set(b, ant=B.ANT.index("REQUESTED"))] += m * pw * (1 - ps)
        elif p0 in ("GATE14", "GATE14_EXPOSE"):
            cont = B.exposed_leaf(s) if p0 == "GATE14_EXPOSE" else B.soft_horizon(B._set(s, t=15))
            pd = 1 - B.sigmoid_commit(cont, CURVE)
            if B.ANT[B.gi(s, "ant")] == "smax_signed":
                pd *= B.SMAX_MULT
            pd = min(1.0, pd)
            terminals["leaf-committed" + ("-exposed" if p0 == "GATE14_EXPOSE" else "")] += m * (1 - pd)
            terminals["REQUESTED"] += m * pd
        else:
            for p, ns in outs:
                mass[ns] += m * p
    nh = {int(k): {b: round(v, 5) for b, v in bands.items()} for k, bands in node_health.items()}
    tm = {k: round(v, 5) for k, v in sorted(terminals.items(), key=lambda kv: -kv[1])}
    return nh, tm


def build_lattice(states, val, choice):
    """THE LATTICE (v6). The solver's exact forward mass over its reachable states, with the
    edges between them -- so convergence is carried in the data instead of being thrown away.

    Why exact rather than sampled: a channel is a STATE, and two histories merge when they
    reach the same state. In a 400-trace sample that almost never happens in the wide part of
    the field (measured: 12 merge-nodes of 586 channels; the 400 traces
    touch 774 distinct sids, but 188 of those are absorbing terminals or t=15 leaves, which
    are not lattice channels), so a sample-built render is a tree wearing a
    lattice's name. The same object computed exactly has 1,376 merge-nodes of 12,565. Same
    definition, no estimator noise. The traces stay -- they are the audit overlay.

    Emitted per column: live states (mass, equity, health), the edges arriving into them, and
    the mass that EXITS at that column (converted, requested, ring), each tagged to the live
    lane it left from so the render can route it off the page instead of ending it mid-field.
    """
    mass = defaultdict(float); mass[B.ROOT] = 1.0
    edges = defaultdict(float)           # (col, src_state, dst_state) -> mass
    exits = defaultdict(float)           # (col, kind, src_state) -> mass
    for s in sorted(states, key=lambda x: B.gi(x, "t")):
        m = mass.get(s, 0.0)
        if m <= 1e-15:
            continue
        t = int(B.gi(s, "t"))
        if B.is_absorbing(s):
            continue                     # already booked as an exit by its predecessor
        lbl = choice[s]
        if lbl == "ARM-CONVERT":            # the ONLY terminal choice -- see exact_aggregates
            exits[(t, "CONVERT", s)] += m
            continue
        cost, outs = next((c, o) for l, c, o in B.successors(s) if l == lbl)
        p0, tgt0 = outs[0]

        def land(ns, w):
            if w <= 1e-15:
                return
            if B.is_absorbing(ns):       # RING / REQUESTED: leaves from THIS lane, at this column
                exits[(t, "RING" if B.RUN[B.gi(ns, "run")] == "RING" else "REQUESTED", s)] += w
            else:
                mass[ns] += w; edges[(int(B.gi(ns, "t")), s, ns)] += w

        if p0 in ("HAZARD9", "HAZARD9_EXT"):
            for pw, b in B._hazard9_next_states(s, extended=(p0 == "HAZARD9_EXT")):
                vs = {al: val.get(B._set(b, ant=B.ANT.index(al)), B.terminal_value(B._set(b, ant=B.ANT.index(al)), CURVE)) for al in HAZ}
                w = B.stay_split(max(vs.values()), CURVE); ps = B.sigmoid_commit(sum(w[al] * vs[al] for al in vs), CURVE)
                for al in HAZ:
                    land(B._set(b, ant=B.ANT.index(al)), m * pw * ps * w[al])
                land(B._set(b, ant=B.ANT.index("REQUESTED")), m * pw * (1 - ps))
        elif p0 in ("GATE14", "GATE14_EXPOSE"):
            cont = B.exposed_leaf(s) if p0 == "GATE14_EXPOSE" else B.soft_horizon(B._set(s, t=15))
            pd = 1 - B.sigmoid_commit(cont, CURVE)
            if B.ANT[B.gi(s, "ant")] == "smax_signed":
                pd *= B.SMAX_MULT
            pd = min(1.0, pd)
            exits[(t, "REQUESTED", s)] += m * pd
            exits[(t, "COMMITTED_EXPOSED" if p0 == "GATE14_EXPOSE" else "COMMITTED", s)] += m * (1 - pd)
        else:
            for p, ns in outs:
                land(ns, m * p)

    # per-column live lanes, ordered by equity rank (descending; stable tiebreak on the key)
    bycol = defaultdict(list)
    for s, m in mass.items():
        if m > 1e-12 and not B.is_absorbing(s):
            bycol[int(B.gi(s, "t"))].append(s)
    st_out, idx = {}, {}
    for c, ss in bycol.items():
        ss.sort(key=lambda s: (-float(val.get(s, B.terminal_value(s, CURVE))), sid(s)))
        idx[c] = {s: k for k, s in enumerate(ss)}
        st_out[str(c)] = [[sid(s), round(mass[s], 12), round(float(val.get(s, B.terminal_value(s, CURVE))), 5),
                           health(s)] for s in ss]
    ed_out = defaultdict(list)
    for (c, a, b), m in edges.items():
        if c in idx and (c - 1) in idx and a in idx[c - 1] and b in idx[c]:
            ed_out[str(c)].append([idx[c - 1][a], idx[c][b], round(m, 12)])
    ex_out = defaultdict(list)
    for (c, kind, s), m in exits.items():
        if c in idx and s in idx[c]:
            ex_out[str(c)].append([kind, idx[c][s], round(m, 12)])
    indeg = defaultdict(set)
    for (c, a, b) in edges:
        indeg[(c, b)].add(a)
    return {"states": st_out, "edges": dict(ed_out), "exits": dict(ex_out),
            "widths": {str(c): len(v) for c, v in sorted(st_out.items(), key=lambda kv: int(kv[0]))},
            "n_states": sum(len(v) for v in st_out.values()), "n_edges": len(edges),
            "n_merge_nodes": sum(1 for v in indeg.values() if len(v) > 1)}


def build_fork(fork):
    B.set_fork(fork); B.EXPOSE_JADEN_ARM = False; B.DISABLE_CONVERT = False; B.DISABLE_ACQ_ARMS = False
    states = B.reachable()
    val, choice = B.solve(states, CURVE)
    rng = np.random.default_rng(SEED + (0 if fork == "rapm" else 1))
    traces = [sample_trace(fork, val, choice, rng, i) for i in range(N_TRACES)]
    node_health, terminals = exact_aggregates(states, val, choice)   # EXACT, not sampled
    lattice = build_lattice(states, val, choice)
    # sampled terminals kept for transparency (shows the 400-trace visual field's spread)
    sampled = defaultdict(float)
    for tr in traces:
        sampled[tr["terminal"]] += tr["weight"]
    return {"traces": traces, "lattice": lattice, "node_health": node_health, "terminals": terminals,
            "terminals_sampled": {k: round(v, 4) for k, v in sorted(sampled.items(), key=lambda kv: -kv[1])},
            "root_value": round(float(val[B.ROOT]), 4)}


def main():
    nodes = [{"id": n, "t": n, "type": ty, "name": name} for n, ty, name in B.CALENDAR]
    export = {
        "meta": {
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": "SOLVER",                    # SYNTHETIC only if ever hand-faked
            "curve": CURVE,
            "fork_weights": FORK_WEIGHTS,
            "salvage_cap": B.SALVAGE_CAP,
            "p_east": X6.P_EAST,
            "n_traces_per_fork": N_TRACES,
            "schema": "one-for-all/board-viz/2",   # v2 adds per-column `sid` (lattice key)
        },
        "nodes": nodes,
        "forks": {fk: build_fork(fk) for fk in ("rapm", "box")},
        "realized": [],                            # empty until the R1/R2 reads land
    }
    out = HERE / "board_viz_export.json"
    out.write_text(json.dumps(export, separators=(",", ":")), encoding="utf-8")
    kb = out.stat().st_size / 1024
    print(f"wrote {out} ({kb:.0f} KB)")
    for fk in ("rapm", "box"):
        f = export["forks"][fk]
        print(f"  {fk}: {len(f['traces'])} traces | terminals {dict(list(f['terminals'].items())[:5])}")


if __name__ == "__main__":
    main()
