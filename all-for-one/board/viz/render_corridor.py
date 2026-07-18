"""THE CORRIDOR (viz geometry v3): a circuit-board timeline of the board.

Left to right is time (NOW at the left, the 2028 GATE at the right); calendar columns
are faint verticals; futures are traced as circuit routes on a lane grid with orthogonal
runs and 45-degree jogs, bending ONLY at calendar columns (a bend is an event). The
center lane is always the road to the NEXT ring. The v2 rendering recipe is binding:
additive light, monochrome teal journeys with colored endings, three-pass strokes,
dead drawn first, the squint test.

Semantics:
  - ring '27 sits in-line on the center lane at the spring-2027 column (node 7); ring
    '28 at the gate column (node 14). Rings are terminals with an exclusion zone: only
    that year's RING futures enter and terminate on the circumference; everyone else
    routes AROUND, so the weave visibly parts at each ring.
  - center lane = the road to the next ring. NOW -> ring '27: the '27-title futures hold
    the center, everyone else rides the bands. After ring '27 the board RE-SORTS: the
    '28-bound futures jog back into the center (the crossover merge), the rest stay outer.
  - upper band = alive futures not on the current ring road. lower band = the failure
    shelf: resets freeze as small red rings at their column; exits (request/convert) bend
    down and leave through the bottom edge; alive-at-gate futures crowd ring '28 without
    entering.
  - honest thinness: no minimum corridor width. Four futures reaching ring '27 is four
    threads; the '27-vs-'28 density contrast is the story.

Deliver: PNG stills, full and 50% zoom, straight and ~12-degree sheared, plus a mid-season
collapse still (scrubber at R2, node 5). No interactivity.

Run:  python render_corridor.py
"""
from __future__ import annotations
import json
import math
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EXPORT = json.loads((HERE / "board_viz_export.json").read_text(encoding="utf-8"))

S_W, S_H = 2100, 1180
XL, XR = 165, S_W - 95
YT, YB = 120, S_H - 96
TMAX = 14
N_LANES = 44
LANE_H = (YB - YT) / N_LANES
RING27_COL, RING28_COL = 7, 14

# bands (lane index ranges)
CEN = (20, 24)          # center road
UP = (3, 19)            # upper band: alive, off-road
LO = (25, 42)           # lower band: the failure shelf
RING_R = 3.0 * LANE_H

BG = np.array([9, 15, 28], float)
DEAD = np.array([24, 34, 60], float)
TEAL = np.array([53, 201, 192], float)
GOLD = np.array([242, 193, 78], float)
RED = np.array([226, 75, 74], float)
ROSE = np.array([196, 120, 140], float)
INK = (107, 123, 160)
FONT_PATH = "C:/Windows/Fonts/consola.ttf"


def col_x(t):
    return XL + (XR - XL) * (min(t, TMAX) / TMAX)


def lane_y(L):
    return YT + L * LANE_H + LANE_H / 2


def classify(term):
    if term == "RING":
        return "ring"
    if term.startswith("CONVERT"):
        return "convert"
    if term in ("REQUESTED", "EXPOSE"):
        return "requested"
    return "committed"


def term_node(tr):
    t = tr["terminal"]
    if t.startswith("CONVERT@"):
        return int(t.split("@")[1])
    if t == "RING":
        return next((p["t"] for p in tr["path"] if p.get("run") == "RING"), tr["path"][-1]["t"])
    return min(tr["path"][-1]["t"], 14)


def normalize(traces):
    out = []
    order = sorted(range(len(traces)), key=lambda i: tuple(traces[i]["codes"]))
    spread = {i: (k + 0.5) / len(traces) for k, i in enumerate(order)}   # global braid position
    for i, tr in enumerate(traces):
        out.append({"cls": classify(tr["terminal"]), "codes": tr["codes"], "term": tr["terminal"],
                    "tnode": term_node(tr), "spread": spread[i], "run_by": _run_by(tr)})
    return out


def _run_by(tr):
    return {p["t"]: p.get("run", "none") for p in tr["path"]}


def _band_at(tr, t):
    """(lane_lo, lane_hi) band for this trace at column t; None once it has ended.
    Convert/requested ride the UP band (alive) until their event column, then the route
    ends and the tail drops them into the failure shelf (a red ring) or off the bottom."""
    cls, tn = tr["cls"], tr["tnode"]
    if cls == "ring":
        return CEN if t <= RING27_COL else None
    if cls in ("convert", "requested"):
        return UP if t <= tn else None
    # committed / alive to the gate
    return UP if t <= RING27_COL else CEN


def _lane(tr, band, t):
    lo, hi = band
    # bundles share lanes so corridors glow by accumulation; the braid unwinds over time --
    # few corridor lanes at NOW, more as events diverge. Traces snap to a corridor lane, so
    # many share one (accumulation), and the count grows toward the gate (the unwind).
    span = hi - lo
    d = _smooth(t / TMAX)
    n_cor = max(1, min(span, 1 + int(round(span * d))))
    bucket = min(n_cor - 1, int(tr["spread"] * n_cor))
    return lo + int(round(span * (bucket + 0.5) / n_cor))


def _smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def route(tr, upto_t=TMAX):
    """Circuit polyline: for each column the trace's lane; horizontal runs between columns,
    45-degree jogs centered at columns (bends only at columns). Returns points + a tail spec."""
    cols = []
    last_t = min(upto_t, tr["tnode"])
    for t in range(0, last_t + 1):
        b = _band_at(tr, t)
        if b is None:
            break
        cols.append((t, _lane(tr, b, t)))
    if len(cols) < 1:
        return [], None
    pts = []
    for k, (t, L) in enumerate(cols):
        x = col_x(t); y = lane_y(L)
        if k == 0:
            pts.append((x, y)); continue
        pt, pL = cols[k - 1]
        px = col_x(pt); py = lane_y(pL)
        dL = L - pL
        jog = abs(dL) * LANE_H                                  # 45-degree jog width
        # horizontal run in the previous lane, then a 45-degree jog centered on this column
        pts.append((x - jog, py))
        pts.append((x, y))
    tail = None
    tn = tr["tnode"]
    if last_t >= tn:                                            # the future has resolved
        tail = (tr["cls"], cols[-1])
    return pts, tail


def splat(buf, pts, amt):
    if len(pts) < 2:
        return
    dp = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0); m = max(2, int(d / 2.4))
        for s in range(m):
            f = s / m; dp.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    dp.append(pts[-1])
    xs = np.array([p[0] for p in dp]); ys = np.array([p[1] for p in dp])
    mm = (xs >= 0) & (xs < S_W) & (ys >= 0) & (ys < S_H)
    np.add.at(buf, (ys[mm].astype(int), xs[mm].astype(int)), amt)


def render(fork, scrub_t=None, shear=0.0):
    traces = normalize(EXPORT["forks"][fork]["traces"])
    living = np.zeros((S_H, S_W), float)
    gold = np.zeros((S_H, S_W), float)
    rose = np.zeros((S_H, S_W), float)

    base = np.empty((S_H, S_W, 3), float); base[:] = BG
    img0 = Image.fromarray(base.astype(np.uint8)); dc = ImageDraw.Draw(img0, "RGBA")
    for nd in EXPORT["nodes"]:                                  # faint calendar columns
        x = col_x(nd["t"]); dc.line([x, YT - 8, x, YB + 8], fill=(120, 140, 180, 15), width=1)
    base = np.asarray(img0, float)

    red_glyphs = []; gate_crowd = []
    for tr in traces:
        pts, tail = route(tr, upto_t=TMAX if scrub_t is None else scrub_t)
        if len(pts) < 2:
            continue
        greyed = scrub_t is not None and tr["cls"] in ("convert", "requested") and tr["tnode"] <= scrub_t
        ex, ey = pts[-1]                                        # the trace's live end (UP band, at its event)
        if tr["cls"] == "convert":
            _draw_dead(base, pts)                              # dead journey, dark, beneath the light
            if tail:                                            # drop into the failure shelf, freeze as a red ring
                ry = lane_y(LO[0] + (LO[1] - LO[0]) * (0.3 + 0.5 * tr["spread"]))
                _draw_dead(base, [(ex, ey), (ex + (ry - ey), ry)])
                red_glyphs.append((ex + (ry - ey), ry, greyed))
        elif tr["cls"] == "requested":
            splat(living, pts, 0.14 * (0.3 if greyed else 1))
            if tail:                                            # bend down 45deg and leave through the bottom edge
                span = (YB + 40) - ey
                splat(rose, [(ex, ey), (ex + span, YB + 40)], 0.11 * (0.3 if greyed else 1))
        elif tr["cls"] == "ring":
            splat(living, pts, 0.18)
            if tail:                                            # enter ring '27, terminate on the circumference
                cx, cy = col_x(RING27_COL), lane_y((CEN[0] + CEN[1]) / 2)
                splat(gold, [(ex, ey), (cx - RING_R + 2, cy)], 0.16)
        else:                                                  # committed: crowd ring '28 at the gate, no entry
            splat(living, pts, 0.16)

    def three(b, a, m, c):
        return a * gaussian_filter(b, 6.0) + m * gaussian_filter(b, 2.2) + c * gaussian_filter(b, 0.8)
    L = np.zeros((S_H, S_W, 3), float)
    L += TEAL[None, None, :] * three(living, 0.04, 0.085, 0.24)[..., None]
    L += GOLD[None, None, :] * three(gold, 0.05, 0.12, 0.42)[..., None]
    L += ROSE[None, None, :] * three(rose, 0.035, 0.07, 0.16)[..., None]
    out = base + L * 255.0
    out = 255.0 * (1 - np.exp(-out / 300.0))
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    if abs(shear) > 1e-6:
        img = img.transform((S_W, S_H), Image.AFFINE, (1, math.tan(math.radians(shear)), -math.tan(math.radians(shear)) * S_H / 2, 0, 1, 0), resample=Image.BICUBIC, fillcolor=tuple(BG.astype(int)))
    d = ImageDraw.Draw(img, "RGBA")
    _rings(d)
    for (x, y, gy) in red_glyphs:
        d.ellipse([x - 3, y - 3, x + 3, y + 3], outline=(*RED.astype(int), 80 if gy else 180), width=1)
    _labels(d, fork, scrub_t, shear)
    _footer(d)
    return img


def _deadbuf(base):
    return base


def _draw_dead(base, pts):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0); m = max(2, int(d / 3))
        for s in range(m):
            f = s / m; x = int(x0 + (x1 - x0) * f); y = int(y0 + (y1 - y0) * f)
            if 0 <= x < S_W and 0 <= y < S_H:
                base[y, x] = base[y, x] * 0.86 + DEAD * 0.14


def _rings(d):
    cy = lane_y((CEN[0] + CEN[1]) / 2)
    for col, lab in [(RING27_COL, "'27"), (RING28_COL, "'28")]:
        cx = col_x(col)
        d.ellipse([cx - RING_R, cy - RING_R, cx + RING_R, cy + RING_R], outline=(*GOLD.astype(int), 255), width=3)
        d.ellipse([cx - RING_R - 4, cy - RING_R - 4, cx + RING_R + 4, cy + RING_R + 4], outline=(*GOLD.astype(int), 60), width=1)
        d.text((cx - 9, cy - 6), lab, font=_font(12), fill=(*GOLD.astype(int), 230))


def _font(sz):
    try:
        return ImageFont.truetype(FONT_PATH, sz)
    except Exception:
        return ImageFont.load_default()


def _labels(d, fork, scrub_t, shear):
    fs = _font(13)
    d.text((30, 26), "THE CORRIDOR", font=_font(20), fill=(*INK, 240))
    d.text((30, 56), f"fork {fork}  ·  left = NOW (Jul 2026)   right = the 2028 GATE"
                     + (f"   ·  shear {shear:.0f}°" if shear else "   ·  straight"), font=fs, fill=(*INK, 175))
    d.text((30, 74), "center lane = the road to the next ring · upper = alive off-road · lower = the failure shelf",
           font=fs, fill=(*INK, 140))
    for t, txt in [(0, "NOW"), (3, "R1"), (5, "R2"), (6, "deadline"), (7, "ring '27"), (9, "Jul27 gate"),
                   (12, "deadline 2"), (14, "GATE '28")]:
        x = col_x(t); d.text((x - 14, YB + 14), txt, font=_font(11), fill=(*INK, 160))
    if scrub_t is not None:
        d.text((30, 92), f"scrubber @ R2 (node {scrub_t}): season frozen mid-collapse, diverged futures greyed",
               font=fs, fill=(*INK, 200))


def _footer(d):
    m = EXPORT["meta"]
    d.text((30, S_H - 30), f"{m['source']} · forks rapm {m['fork_weights']['rapm']} / box {m['fork_weights']['box']}"
           f" · cap {m['salvage_cap']} · P(east) {m['p_east']} · {m['n_traces_per_fork']} traces/fork"
           f" · export {m['generated'].replace('T', ' ').replace('+00:00', 'Z')}", font=_font(12), fill=(*INK, 190))
    d.text((30, S_H - 48), "endings:  gold = title   teal = alive   red = reset   rose = Ant departs",
           font=_font(12), fill=(*INK, 170))


def main():
    out = HERE / "stills"; out.mkdir(exist_ok=True)
    full = render("box"); full.save(out / "corridor_box_full.png")
    render("box", shear=12).save(out / "corridor_box_sheared.png")
    # 50% zoom into the ring '27 -> gate span (the crossover re-sort + both rings)
    x0, x1 = int(col_x(5)), S_W; y0, y1 = int(YT + (YB - YT) * 0.28), int(YB + 40)
    full.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * 1.6), int((y1 - y0) * 1.6)), Image.LANCZOS).save(out / "corridor_box_zoom50.png")
    render("box", scrub_t=5).save(out / "corridor_box_scrubber_r2.png")
    for p in ("corridor_box_full.png", "corridor_box_sheared.png", "corridor_box_zoom50.png", "corridor_box_scrubber_r2.png"):
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
