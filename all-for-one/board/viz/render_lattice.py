"""ONE RIVER v6: THE LATTICE, NOT THE TREE.

A prefix tree renders divergence and DISCARDS convergence. The board's state space is a
merging lattice: two futures that arrive at the same state ARE the same state, and the render
has to say so. So a drawn channel here is a STATE (the solver's own reachable-state encoding),
weight-summed -- one channel may split into many, and many channels merge into one wherever
their mass lands on a shared state. Merges are physics, not styling.

Geometry, all of it data-caused:
  * LANES BY RANK. Per column the live states are ordered by equity (the solver's value
    function), best at the top. A trace's lane IS its state's rank. A crossing happens exactly
    when two states swap rank between columns -- every braid, every out-and-back, is that.
  * WIDTH = distinct live states. One state at Now; 4,312 at the gate.
  * BRIGHTNESS = MASS, additively and in linear light. In the BUFFER that makes conservation
    of light arithmetic. In the FRAME it does not, and the difference is not academic: any
    display transfer that keeps a 180:1 per-pixel range legible gives back more light to a
    thousand dim pixels than to one bright one, so dispersing a column's mass can brighten the
    picture even as the probability drains. An earlier cut of this render did exactly that --
    the frame got ~9x brighter left to right while the docstring claimed the opposite. So the
    profile is now MEASURED off the rendered frame (light_profile) and tuned until the live
    field really does end dimmer than it starts: gate/Now = 0.73. The residual bulge at the
    reads is the trunk clipping, and is reported rather than hidden.
  * NOTHING ENDS MID-FIELD. Exiting mass (converted, requested, dead end) merges into one
    weighted channel per column per kind and runs off the page at a shallow angle. Futures
    that leave the story leave the page.

Why the field is the exact lattice and not the 400 traces: a channel is a state, and in a
400-trace sample two histories almost never land on the same state out in the wide part of the
field. Measured: the sample has 12 merge-nodes of 586 channels; the same object computed
exactly has 1,376 of 12,565. Rendering the sample would have drawn a tree again and called it
a lattice. The traces remain, doing the job they are actually good at: the audit overlay.

Run:  python render_lattice.py              # still + zoom + audit overlay + reconciliation
      python render_lattice.py --fork rapm  # the perturbation render (a different solver input)
"""
from __future__ import annotations
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
S_W, S_H = 2100, 1180
XL, XR = 150, S_W - 150
CY, BAND = S_H / 2 + 14, S_H * 0.72
# Column height exponent and the display transfer. These two together decide whether the
# PICTURE conserves light, not just the buffer -- see light_profile() and the note there.
HEXP, GAIN, GAMMA = 0.5, 0.22, 1.0
YB = S_H - 84
TMAX = 14
RING27_T = 7
RING_R = 30

BG = np.array([9, 15, 28], float)
TEAL = np.array([53, 201, 192], float)
GOLD = np.array([242, 193, 78], float)
ROSE = np.array([196, 120, 140], float)
INK = (110, 123, 160)
FONT_PATH = "C:/Windows/Fonts/consola.ttf"
HUMAN = {0: "Now", 3: "Nov read", 5: "Jan read", 6: "deadline", 7: "playoffs", 8: "draft",
         9: "July 27", 12: "deadline", 13: "playoffs", 14: "the gate"}


def col_x(t):
    return XL + (XR - XL) * (min(t, TMAX) / TMAX)


def _font(sz):
    try:
        return ImageFont.truetype(FONT_PATH, sz)
    except Exception:
        return ImageFont.load_default()


class Lattice:
    """The drawable lattice: lane geometry over the exported states, edges and exits."""

    def __init__(self, L):
        self.states = {int(c): v for c, v in L["states"].items()}
        self.edges = {int(c): v for c, v in L.get("edges", {}).items()}
        self.exits = {int(c): v for c, v in L.get("exits", {}).items()}
        self.n = {c: len(v) for c, v in self.states.items()}
        self.n_max = max(self.n.values())
        self.where = {}                       # sid -> (col, rank)
        for c, ss in self.states.items():
            for k, s in enumerate(ss):
                self.where[s[0]] = (c, k)
        self.merge_nodes = L["n_merge_nodes"]
        self.n_states, self.n_edges = L["n_states"], L["n_edges"]

    def height(self, c):
        """Vertical extent of a column = sqrt(live states), scaled so the widest column (the
        gate, 4,312 states) fills the band. Disclosed compression, and the only one: a linear
        scale would render nine states at Now-plus-one-read as two pixels next to a field four
        thousand lanes wide. Rank ORDER inside the column is exact and uncompressed."""
        return BAND * (self.n[c] ** HEXP) / (self.n_max ** HEXP)

    def y(self, c, rank):
        """Lane y: rank 0 (best equity) at the top of that column's band, centered."""
        n = self.n[c]
        f = 0.0 if n == 1 else rank / (n - 1.0) - 0.5
        return CY + f * self.height(c)

    def mass(self, c, rank):
        return self.states[c][rank][1]

    def indeg(self):
        d = defaultdict(set)
        for c, es in self.edges.items():
            for i, j, m in es:
                d[(c, j)].add(i)
        return d


def _splat(buf, p0, p1, total, dim=1.0):
    """Lay `total` units of light along a segment, spread so that each pixel-column of x
    receives the segment's mass. Additive: overlapping channels sum, which is the whole point."""
    x0, y0 = p0; x1, y1 = p1
    d = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(d / 0.9))
    xs = np.linspace(x0, x1, n); ys = np.linspace(y0, y1, n)
    amt = total * (abs(x1 - x0) + 1.0) / n
    if dim != 1.0:
        amt = amt * np.linspace(1.0, dim, n)
    m = (xs >= 0) & (xs < S_W) & (ys >= 0) & (ys < S_H)
    np.add.at(buf, (ys[m].astype(int), xs[m].astype(int)), amt if np.isscalar(amt) else amt[m])


def render(L, highlight=None, subtitle="", dim_field=1.0, fork="box"):
    lat = Lattice(L)
    live = np.zeros((S_H, S_W), float)
    gold = np.zeros((S_H, S_W), float)
    rose = np.zeros((S_H, S_W), float)
    hi = np.zeros((S_H, S_W), float)

    base = np.empty((S_H, S_W, 3), float); base[:] = BG
    img0 = Image.fromarray(base.astype(np.uint8)); dc = ImageDraw.Draw(img0, "RGBA")
    for t in HUMAN:
        x = col_x(t); dc.line([x, 70, x, YB + 4], fill=(120, 140, 180, 8), width=1)
    base = np.asarray(img0, float)

    # --- the lattice itself: every edge is a real transition carrying real mass -------------
    for c, es in sorted(lat.edges.items()):
        x0, x1 = col_x(c - 1), col_x(c)
        for i, j, m in es:
            _splat(live, (x0, lat.y(c - 1, i)), (x1, lat.y(c, j)), m)

    # --- exits: merged per (column, kind), off the page, never ending mid-field -------------
    exit_log, rings = [], []
    for c, rows in sorted(lat.exits.items()):
        byk = defaultdict(list)
        for kind, rank, m in rows:
            byk[kind].append((rank, m))
        for kind, parts in byk.items():
            tot = sum(m for _, m in parts)
            if tot <= 1e-9:
                continue
            y0 = sum(lat.y(c, r) * m for r, m in parts) / tot      # mass-weighted departure lane
            x0 = col_x(c)
            exit_log.append((c, kind, tot, len(parts)))
            if kind == "RING":                                      # a ring is arrival, not exit
                # The title is decided in the c -> c+1 transition, so the ring sits half a
                # column downstream of the lane the mass leaves from, and the gold thread has
                # real horizontal extent. (Drawing it at col_x(c) made dx = 0, which _splat's
                # per-x normalisation then collapsed to ~1/130th of an equal-mass edge.)
                rings.append((col_x(c) + (col_x(1) - col_x(0)) * 0.5, y0, x0, tot))
                continue
            if kind.startswith("COMMITTED"):
                # not an exit -- this is the plan working. It keeps its shape and runs off the
                # RIGHT edge, one run per surviving state, so the gate shows a distribution.
                # (COMMITTED_EXPOSED is the same outcome reached via the expose-Jaden arm.)
                for r, m in parts:
                    _splat(live, (x0, lat.y(c, r)), (S_W + 40, lat.y(c, r)), m, dim=0.7)
                continue
            up = y0 < CY                                            # shallow run to the NEAR edge
            span = (XR - XL) / TMAX * 6.2
            y1 = -80 if up else S_H + 80
            _splat(live, (x0, y0), (x0 + span * 0.5, y0 + (y1 - y0) * 0.34), tot * 0.62, dim=0.55)
            _splat(rose, (x0 + span * 0.5, y0 + (y1 - y0) * 0.34), (x0 + span, y1), tot * 0.7, dim=0.22)

    for rx, y0, x0, tot in rings:
        _splat(gold, (x0, y0), (rx, CY), tot)

    # --- audit overlay ---------------------------------------------------------------------
    if highlight:
        for tr in highlight:
            prev = None
            for c, rank in tr["lanes"]:
                p = (col_x(c), lat.y(c, rank))
                if prev:
                    _splat(hi, prev, p, 0.85)
                prev = p
            if prev and tr.get("off"):
                up = prev[1] < CY
                _splat(hi, prev, (prev[0] + (XR - XL) / TMAX * 1.5, -70 if up else S_H + 70), 0.55)

    # --- linear light -> three-pass bloom -> display transfer ------------------------------
    def three(b, a, m, c_):
        return a * gaussian_filter(b, 7.0) + m * gaussian_filter(b, 2.4) + c_ * gaussian_filter(b, 0.7)

    Ll = np.zeros((S_H, S_W, 3), float)
    Ll += TEAL[None, None, :] * three(live, 0.05, 0.18, 0.62)[..., None] * dim_field
    Ll += GOLD[None, None, :] * three(gold, 0.06, 0.26, 0.95)[..., None] * dim_field
    Ll += ROSE[None, None, :] * three(rose, 0.05, 0.14, 0.45)[..., None] * dim_field
    if highlight:
        Ll += np.array([255, 255, 255])[None, None, :] * three(hi, 0.008, 0.035, 0.85)[..., None] * 0.85
    # brightness stays LINEAR in mass all the way to here (conservation of light is arithmetic);
    # this last curve is display encoding, applied once, to the whole frame equally.
    lin = np.clip(Ll * GAIN, 0, None)
    out = base + 255.0 * (1.0 - np.exp(-lin ** GAMMA))
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")

    d = ImageDraw.Draw(img, "RGBA")
    for rx, _y, _x, tot in rings:                # radius carries the mass that reaches it
        rr = 14 + 260 * math.sqrt(tot)
        d.ellipse([rx - rr, CY - rr, rx + rr, CY + rr], outline=(*GOLD.astype(int), 210), width=2)
    _chrome(d, lat, subtitle, fork)
    return img, lat, exit_log


def _chrome(d, lat, subtitle, fork):
    d.text((30, 26), "ONE RIVER", font=_font(21), fill=(*INK, 240))
    d.text((30, 56), "every future the board holds. a channel is a STATE, so futures that reach the same state merge into one channel;",
           font=_font(13), fill=(*INK, 168))
    d.text((30, 72), "lanes are ordered by equity, so every crossing is a change of rank. a channel's brightness is its probability mass." + subtitle,
           font=_font(13), fill=(*INK, 168))
    for t, lab in HUMAN.items():
        x = col_x(t); d.text((x - len(lab) * 3.1, YB + 22), lab, font=_font(12), fill=(*INK, 175))
    d.text((30, S_H - 26), "futures that leave the story leave the page", font=_font(12), fill=(196, 120, 140, 165))
    d.text((S_W - 660, S_H - 26),
           f"SOLVER · {fork} · {lat.n_states} states · {lat.n_edges} transitions · {lat.merge_nodes} merge points"
           f" · width {lat.n[0]} at Now to {lat.n[TMAX]} at the gate",
           font=_font(11), fill=(*INK, 150))


# ------------------------------------------------------------------ audit (proof A) --------
ADVERSE = {"FIT_R", "FIT_Y", "AVAIL_C", "PERF_T3", "PERF_T4", "JAD_STAL"}
# Every one of these is emitted only from the t=6 or t=12 decision menus, so "arms at the
# deadline" is true by construction. EXT is deliberately NOT here: an extension can fire at
# t=0, t=9 or t=12, so counting it would have made the caption true only by luck.
ARMS = {"ARMG", "ARMB", "ARMD", "ARMS", "UNLOCK", "ADV28"}


def lanes_of(tr, lat):
    out = []
    for n in tr["path"]:
        w = lat.where.get(n["sid"])
        if w:
            out.append(w)
    return out


def rank_frac(lat, c, rank):
    return rank / max(1, lat.n[c] - 1)


def adverse_col(s):
    """The column at which this future's state first went bad -- the trip, not the repair.
    Read off the state itself (a red/yellow fit, LaMelo unavailable, a bottom perf tier or a
    stalled Jaden), so it does not depend on the code stream being complete."""
    for n in s["tr"]["path"]:
        if (n["fit"] in ("red", "yellow") or n["melo"] == "C"
                or n["run"] == "none" and n["t"] > 8 or n["jaden"] == "stalled"):
            return int(n["t"])
    return None


def audit(traces, lat):
    """Five roles, every one a REAL trace:

      title / exit / gate   the three v5 roles, kept.
      repaired              a future that trips a wire, takes a deadline arm, and MERGES back
                            into a healthier corridor. Not asserted -- checked: it must pass
                            through a genuine merge point (a state other histories also reach)
                            AND climb the equity ranking between the read that hurt it and the
                            gate. This is the plan working.
      converges-with        the future it merges WITH: a different history that lands on the
                            same state. From that column the two white lines are ONE line,
                            because they are one state. That is the physics v5 threw away."""
    indeg = lat.indeg()
    scored = []
    for tr in traces:
        lanes = lanes_of(tr, lat)
        if not lanes:
            continue
        scored.append({"tr": tr, "lanes": lanes, "codes": set(tr["codes"]),
                       "alive": tr["terminal"] == "RING" or tr["terminal"].startswith("leaf-committed"),
                       "at": {c: r for c, r in lanes}})

    def partner_of(s):
        """Another sampled trace that ARRIVES at a state s also occupies, from a different
        state one column earlier. Among the candidates, take the one that then stays merged
        longest, so the shared channel is actually legible on the frame."""
        best = None
        for c, r in s["lanes"]:
            if c == 0 or len(indeg.get((c, r), ())) < 2:
                continue
            for o in scored:
                if o is s or o["at"].get(c) != r:
                    continue
                if o["at"].get(c - 1) is None or o["at"].get(c - 1) == s["at"].get(c - 1):
                    continue
                k = c
                while o["at"].get(k + 1) is not None and o["at"].get(k + 1) == s["at"].get(k + 1):
                    k += 1
                if best is None or (k - c) > best[3]:
                    best = (o, c, r, k - c, k)
        return best

    pick, note = {}, {}
    for s in scored:
        t = s["tr"]["terminal"]
        if t == "RING" and "title" not in pick:
            pick["title"] = s
        elif t == "REQUESTED" and s["lanes"][-1][0] == 9 and "exit" not in pick:
            pick["exit"] = s
        elif t.startswith("leaf-committed") and "gate" not in pick:
            pick["gate"] = s

    best = None
    for s in scored:
        if not (s["alive"] and s["codes"] & ADVERSE and s["codes"] & ARMS):
            continue
        # Measure the climb from where the WIRE TRIPPED, not from the merge. Anchoring at the
        # deadline made the gain a property of the shared downstream state, so the repaired
        # trace and its untouched partner posted an identical number and the caption credited
        # the repair for something the repair had nothing to do with.
        t0 = adverse_col(s)
        if t0 is None:
            continue
        after = [(c, r) for c, r in s["lanes"] if c >= t0]
        if len(after) < 3:
            continue
        gain = rank_frac(lat, *after[0]) - rank_frac(lat, *after[-1])      # + = climbed the board
        pr = partner_of(s)
        if pr is None or gain <= 0:
            continue
        if best is None or (pr[3], gain) > (best[5], best[0]):
            best = (gain, s, pr[0], pr[1], pr[2], pr[3], pr[4])
    if best:
        gain, s, p, mc, mr, span, until = best
        pick["repaired"], pick["converges-with"] = s, p
        where = HUMAN.get(mc, f"column {mc}")
        t0 = adverse_col(s)
        pgain = None
        if adverse_col(p) is not None:
            pa = [(c, r) for c, r in p["lanes"] if c >= adverse_col(p)]
            pgain = rank_frac(lat, *pa[0]) - rank_frac(lat, *pa[-1]) if len(pa) >= 3 else None
        note["repaired"] = (
            f"its state has gone bad by the {HUMAN.get(t0, 'column ' + str(t0))}, it takes a deadline arm, "
            f"and from the column where it went bad it climbs {gain * 100:.0f}% of the equity ranking by the gate"
            + ("" if pgain is not None else
               " — the partner below never went bad at all, so there was nothing to repair"))
        note["converges-with"] = (
            f"a different history that lands on the SAME state at the {where} — {len(indeg[(mc, mr)])} "
            f"histories reach it. From there the two white lines are ONE line, because they are one "
            f"channel, and they stay one until "
            + (f"the {HUMAN.get(until + 1, 'next node')} splits them again" if until < TMAX else "the gate"))

    hl, rows, pair = [], [], []
    for label, s in pick.items():
        tr = s["tr"]
        h = {"lanes": s["lanes"], "off": tr["terminal"] == "REQUESTED"}
        hl.append(h)
        if label in ("repaired", "converges-with"):
            pair.append(h)
        rows.append([label, tr["id"], tr["terminal"], tr["codes"], note.get(label, "")])
    return hl, rows, pair, (best[3] if best else None)


def light_profile(img, lat):
    """Emitted light per calendar column, MEASURED off the rendered frame.

    The linear buffer conserves light by construction (amplitude = mass), but the buffer is
    not what anyone looks at. A concave display transfer gives back more light to many dim
    pixels than to one bright one, so dispersing a column's mass across thousands of sub-pixel
    lanes can make the FRAME brighter even as the probability drains. That is measurable, so
    it gets measured rather than asserted: this returns the column integral in the picture
    next to the probability mass it is supposed to track."""
    a = np.asarray(img, float).sum(axis=2)
    bg = float(BG.sum())
    rows = []
    for t in sorted(lat.n):
        x = int(col_x(t))
        band = a[:, max(0, x - 18):x + 18] - bg
        rows.append((t, float(np.clip(band, 0, None).sum()) / 1e3,
                     sum(s[1] for s in lat.states[t])))
    return rows


def reconcile(traces, lat):
    seen = defaultdict(float)
    for tr in traces:
        for n in tr["path"]:
            if n["sid"] in lat.where:          # drawn lanes only (skips absorbed / t=15 leaf rows)
                seen[n["sid"]] += tr["weight"]
    gate = lat.n[TMAX]
    peak_c = max(lat.n, key=lambda c: lat.n[c])
    return {"n_traces": len(traces), "occupied": len(seen), "n_states": lat.n_states,
            "n_edges": lat.n_edges, "merges": lat.merge_nodes,
            "peak": (peak_c, lat.n[peak_c]), "gate": gate, "widths": dict(sorted(lat.n.items()))}


def main():
    export = json.loads((HERE / "board_viz_export.json").read_text())
    fork = "box"
    if "--fork" in sys.argv:
        fork = sys.argv[sys.argv.index("--fork") + 1]
    F = export["forks"][fork]
    out = HERE / "stills"; out.mkdir(exist_ok=True)
    if fork != "box":
        img, lat, _ = render(F["lattice"], subtitle=f"   [{fork} fork]", fork=fork)
        img.save(out / f"lattice_{fork}.png"); print(f"wrote lattice_{fork}.png ({lat.n_states} states)")
        return

    img, lat, exit_log = render(F["lattice"])
    img.save(out / "lattice_full.png")
    x0, x1 = int(col_x(6)), S_W
    y0, y1 = int(CY - S_H * 0.36), int(CY + S_H * 0.36)
    img.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * 1.5), int((y1 - y0) * 1.5)), Image.LANCZOS).save(out / "lattice_zoom50.png")

    hl, rows, pair, mcol = audit(F["traces"], lat)
    aimg, *_ = render(F["lattice"], highlight=hl, dim_field=0.55)
    aimg.save(out / "lattice_audit.png")
    if mcol is not None:                       # the merge, close up: two white lines becoming one
        pimg, *_ = render(F["lattice"], highlight=pair, dim_field=0.35)
        mx0, mx1 = int(col_x(mcol - 2.6)), int(col_x(mcol + 2.2))
        my0, my1 = int(CY - 130), int(CY + 130)
        pimg.crop((mx0, my0, mx1, my1)).resize((int((mx1 - mx0) * 2.4), int((my1 - my0) * 2.4)),
                                               Image.LANCZOS).save(out / "lattice_merge_zoom.png")
    rec = reconcile(F["traces"], lat)
    prof = light_profile(img, lat)
    lat_nx = Lattice({**F["lattice"], "exits": {}})
    prof_live = light_profile(render({**F["lattice"], "exits": {}})[0], lat_nx)
    (out / "lattice_audit_table.json").write_text(json.dumps(rows, indent=1))
    (out / "lattice_recon.json").write_text(json.dumps(
        {"recon": rec, "exits": exit_log, "light": prof, "light_live": prof_live}, indent=1))
    print("light per column (measured off the frame): "
          + " ".join(f"{t}:{v:.0f}" for t, v, _m in prof_live)
          + f"  [live field only; gate/Now = {prof_live[-1][1] / prof_live[0][1]:.2f}]")
    print(f"states {rec['n_states']} · edges {rec['n_edges']} · merge points {rec['merges']}")
    print(f"widths {rec['widths']}")
    print("exits:", [(c, k, round(m, 4), n) for c, k, m, n in exit_log])
    for label, tid, term, codes, note in rows:
        print(f"  AUDIT {label:9s} id={tid} {term}: {' > '.join(codes)} {note}")


if __name__ == "__main__":
    main()
