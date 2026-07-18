"""Stage 0 of the ONE FOR ALL board visualization: the data export.

Countdown-compatible: consumes the solver as a READ-ONLY library (imports board_step4,
solves, forward-samples), makes ZERO solver edits, and emits board_viz_export.json for
the composition spikes and the eventual interactive build.

Export schema (per the directive):
  meta      : fork weights (the fork-adjudication prior), salvage cap, p_east, source
              tag (SOLVER here; SYNTHETIC if ever hand-faked), curve, generated stamp.
  nodes     : the decision calendar (id, t, type, name).
  forks[f]  : traces  -> 400 weight-tagged forward samples, each with an event-CODE
                         stream, per-node health + equity, and a terminal class.
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


def _node_rec(s, val):
    return {"t": int(B.gi(s, "t")), "type": B.NODE_TYPE.get(B.gi(s, "t"), ""),
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
            path.append({"t": 15, "type": "leaf", "health": health(s), "band": health_band(health(s)),
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
        if B.NODE_TYPE.get(t) == "read_R1":
            codes.append("AVAIL_" + B.MELO_AVAIL[B.gi(s2, "melo_avail")])
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
        if lbl in ("ARM-CONVERT", "expose-Jaden"):
            terminals[("EXPOSE" if lbl == "expose-Jaden" else f"CONVERT@{t}")] += m
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
            terminals["leaf-committed"] += m * (1 - pd)
            terminals["REQUESTED"] += m * pd
        else:
            for p, ns in outs:
                mass[ns] += m * p
    nh = {int(k): {b: round(v, 5) for b, v in bands.items()} for k, bands in node_health.items()}
    tm = {k: round(v, 5) for k, v in sorted(terminals.items(), key=lambda kv: -kv[1])}
    return nh, tm


def build_fork(fork):
    B.set_fork(fork); B.EXPOSE_JADEN_ARM = False; B.DISABLE_CONVERT = False; B.DISABLE_ACQ_ARMS = False
    states = B.reachable()
    val, choice = B.solve(states, CURVE)
    rng = np.random.default_rng(SEED + (0 if fork == "rapm" else 1))
    traces = [sample_trace(fork, val, choice, rng, i) for i in range(N_TRACES)]
    node_health, terminals = exact_aggregates(states, val, choice)   # EXACT, not sampled
    # sampled terminals kept for transparency (shows the 400-trace visual field's spread)
    sampled = defaultdict(float)
    for tr in traces:
        sampled[tr["terminal"]] += tr["weight"]
    return {"traces": traces, "node_health": node_health, "terminals": terminals,
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
            "schema": "one-for-all/board-viz/1",
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
