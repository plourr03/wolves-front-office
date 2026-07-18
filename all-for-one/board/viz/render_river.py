"""ONE RIVER (viz composition v4): a single teal river of futures that narrows as light exits.

Supersedes the corridor composition. The approved hex-weave braid stays; everything else
simplifies to one central weave spanning the full width, NOW at the left and the 2028 gate at
the right. The v2 rendering recipe is binding (additive light, three-pass strokes, squint test).

  - ONE structure: a single river on the centerline, no bands, no failure shelf.
  - RINGS live in the river: ring '27 (playoffs) and ring '28 (the gate) sit on the centerline
    at their columns; the weave parts around each and re-merges; only that year's title threads
    enter, in gold, terminating on the circumference.
  - DEATH = leaving the page: any future ending before the gate peels from the river at its death
    column, curves to the NEAREST edge (proximity only), and fades within ~1.5 columns. No glyphs,
    no shelf, at most a whisper of rose on the last segment.
  - CONSERVATION OF LIGHT: total river brightness only decreases left to right, because light only
    exits. The gate river is visibly thinner than NOW; the ~51% departures read as narrowing.
  - WEAVE full width: within-river lane exchanges at every calendar column keep the braid alive
    across the whole board (bends only at columns remains law); the right half never goes straight.
  - one color story: teal river, gold rings + title threads, deaths fade to dark.

Deliver: exactly ONE still, straight, full field + the same at 50% zoom, on one review page.

Run:  python render_river.py
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
XL, XR = 155, S_W - 95
CY = S_H / 2
YT, YB = 96, S_H - 84                     # page edges the dying light leaves through
H_MAX = S_H * 0.205                        # river half-height at NOW (full mass)
H_FLOOR = 0.42                             # never compress below this fraction, so the weave survives full width
K = 7                                      # woven strands (bundles); fewer = wider spacing = crossings stay visible
TMAX = 14
RING_R = 46
RING27_T, RING28_T = 7, 14

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


def _death(tr):
    """The column a future leaves the river: rings enter '27 at playoffs; convert/requested die
    at their event; committed run to the gate (never leave -> None)."""
    term = tr["terminal"]
    if term == "RING":
        return ("ring27", RING27_T)
    if term.startswith("CONVERT@"):
        return ("die", int(term.split("@")[1]))
    if term in ("REQUESTED", "EXPOSE"):
        return ("die", min(tr["path"][-1]["t"], TMAX))
    return (None, None)                    # committed: alive to the gate


def normalize(traces):
    order = sorted(range(len(traces)), key=lambda i: tuple(traces[i]["codes"]))
    spread = {i: (k + 0.5) / len(traces) for k, i in enumerate(order)}
    out = []
    for i, tr in enumerate(traces):
        kind, dcol = _death(tr)
        out.append({"strand": min(K - 1, int(spread[i] * K)), "kind": kind, "dcol": dcol,
                    "codes": tr["codes"]})
    return out


def braid_positions():
    """pos[(strand, col)] -> lane index 0..K-1. Adjacent transpositions alternate parity each
    column, so strands weave over-under across the ENTIRE width (never straight parallel)."""
    order = list(range(K)); pos = {}
    for c in range(TMAX + 1):
        for p, s in enumerate(order):
            pos[(s, c)] = p
        i = c % 2
        while i + 1 < K:
            order[i], order[i + 1] = order[i + 1], order[i]; i += 2
    return pos


POS = braid_positions()


def alive_frac(traces, c):
    n = sum(1 for tr in traces if tr["dcol"] is None or tr["dcol"] > c)
    return n / max(1, len(traces))


def strand_y(strand, c, halfh):
    p = POS[(strand, c)]
    y = CY + (p / (K - 1) - 0.5) * 2 * halfh
    # ring parting: push strands out of the ring's exclusion at ring columns
    if c in (RING27_T, RING28_T) and abs(y - CY) < RING_R + 10:
        y = CY + math.copysign(RING_R + 10, y - CY if abs(y - CY) > 1 else (p - (K - 1) / 2))
    return y


def splat(buf, pts, amt):
    if len(pts) < 2:
        return
    dp = []
    for (x0, y0, a0), (x1, y1, a1) in zip(pts, pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0); m = max(2, int(d / 2.4))
        for s in range(m):
            f = s / m; dp.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, a0 + (a1 - a0) * f))
    dp.append(pts[-1])
    xs = np.array([p[0] for p in dp]); ys = np.array([p[1] for p in dp]); al = np.array([p[2] for p in dp])
    mm = (xs >= 0) & (xs < S_W) & (ys >= 0) & (ys < S_H)
    np.add.at(buf, (ys[mm].astype(int), xs[mm].astype(int)), amt * al[mm])


def river_path(tr, halfh_of):
    """Orthogonal runs along the strand lane with 45-degree jogs centered on each column."""
    last = TMAX if tr["dcol"] is None else tr["dcol"]
    pts = []
    for c in range(0, last + 1):
        x = col_x(c); y = strand_y(tr["strand"], c, halfh_of[c])
        if c == 0:
            pts.append((x, y, 1.0)); continue
        py = strand_y(tr["strand"], c - 1, halfh_of[c - 1])
        jog = abs(y - py)
        pts.append((x - jog, py, 1.0)); pts.append((x, y, 1.0))
    return pts


def render(fork):
    traces = normalize(EXPORT["forks"][fork]["traces"])
    # width narrows with the surviving mass (conservation of light) but is FLOORED so the braid
    # keeps crossing to the gate -- the right half never straightens into parallel wires.
    halfh = {c: H_MAX * max(H_FLOOR, alive_frac(traces, c)) for c in range(TMAX + 1)}
    living = np.zeros((S_H, S_W), float); gold = np.zeros((S_H, S_W), float); rose = np.zeros((S_H, S_W), float)

    base = np.empty((S_H, S_W, 3), float); base[:] = BG
    img0 = Image.fromarray(base.astype(np.uint8)); dc = ImageDraw.Draw(img0, "RGBA")
    for t in HUMAN:
        x = col_x(t); dc.line([x, YT - 6, x, YB + 6], fill=(120, 140, 180, 13), width=1)
    base = np.asarray(img0, float)

    for tr in traces:
        pts = river_path(tr, halfh)
        if len(pts) < 2:
            continue
        splat(living, pts, 0.15)
        if tr["kind"] == "ring27":                          # title thread enters ring '27, gold
            ex, ey, _ = pts[-1]
            splat(gold, [(ex, ey, 1.0), (col_x(RING27_T) - RING_R + 2, CY, 1.0)], 0.18)
        elif tr["kind"] == "die":                           # peel toward the nearest edge, fade to nothing
            ex, ey, _ = pts[-1]
            span = col_x(min(TMAX, tr["dcol"] + 1.5)) - ex   # fades within ~1.5 columns
            dy = span * (-1 if ey < CY else 1)               # 45deg toward the nearest edge, no meaning
            q1 = (ex + span * 0.4, ey + dy * 0.4, 0.28)
            q2 = (ex + span * 0.75, ey + dy * 0.75, 0.07)
            end = (ex + span, ey + dy, 0.0)
            splat(living, [(ex, ey, 0.42), q1], 0.12)        # already fading as it leaves the weave
            splat(rose, [q1, q2, end], 0.04)                 # a whisper of rose, gone within 1.5 columns

    def three(b, a, m, c):
        return a * gaussian_filter(b, 6.0) + m * gaussian_filter(b, 2.2) + c * gaussian_filter(b, 0.8)
    L = np.zeros((S_H, S_W, 3), float)
    L += TEAL[None, None, :] * three(living, 0.04, 0.085, 0.24)[..., None]
    L += GOLD[None, None, :] * three(gold, 0.05, 0.12, 0.42)[..., None]
    L += ROSE[None, None, :] * three(rose, 0.03, 0.05, 0.10)[..., None]
    out = 255.0 * (1 - np.exp(-(base + L * 255.0) / 300.0))
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for t, r_ in ((RING27_T, "'27"), (RING28_T, "'28")):
        cx = col_x(t)
        d.ellipse([cx - RING_R, CY - RING_R, cx + RING_R, CY + RING_R], outline=(*GOLD.astype(int), 255), width=3)
        d.ellipse([cx - RING_R - 4, CY - RING_R - 4, cx + RING_R + 4, CY + RING_R + 4], outline=(*GOLD.astype(int), 55), width=1)
    _chrome(d, fork, halfh)
    return img


def _font(sz):
    try:
        return ImageFont.truetype(FONT_PATH, sz)
    except Exception:
        return ImageFont.load_default()


def _chrome(d, fork, halfh):
    d.text((30, 28), "ONE RIVER", font=_font(21), fill=(*INK, 240))
    d.text((30, 58), "every future the board holds, woven into one stream. it only narrows: light leaves when a future ends.",
           font=_font(13), fill=(*INK, 165))
    # legend under the lede (three lines), away from the field and the label row
    lg = _font(12); lx = 30
    for i, (sw, txt) in enumerate([(TEAL, "the river — futures still alive"), (GOLD, "gold — the title"),
                                   (ROSE, "fading — futures ending")]):
        d.line([lx + i * 250, 82, lx + i * 250 + 20, 82], fill=(*np.array(sw).astype(int), 220), width=3)
        d.text((lx + i * 250 + 28, 76), txt, font=lg, fill=(*INK, 175))
    for t, lab in HUMAN.items():
        x = col_x(t); d.text((x - len(lab) * 3.1, YB + 20), lab, font=_font(12), fill=(*INK, 170))
    m = EXPORT["meta"]
    d.text((S_W - 560, S_H - 26), f"{m['source']} · box fork · export {m['generated'].replace('T', ' ').replace('+00:00', 'Z')}",
           font=_font(11), fill=(*INK, 150))


def main():
    out = HERE / "stills"; out.mkdir(exist_ok=True)
    full = render("box"); full.save(out / "river_box_full.png")
    x0, x1 = int(col_x(4)), S_W; y0, y1 = int(CY - H_MAX - 30), int(CY + H_MAX + 30)
    full.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * 1.55), int((y1 - y0) * 1.55)), Image.LANCZOS).save(out / "river_box_zoom50.png")
    print("wrote river_box_full.png, river_box_zoom50.png")


if __name__ == "__main__":
    main()
