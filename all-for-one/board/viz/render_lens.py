"""ONE RIVER v5: THE DATA MUST BE VISIBLE. A lens grown from the real state prefixes.

No bend, crossing, or split exists unless the data caused it. All 400 futures begin as ONE
thread at Now (the root) and split only at the columns where their event sequences first
diverge -- the reads, the deadline, the playoffs, the July-27 boundary. Traces that share a
prefix share ONE drawn channel; their weights sum additively into that channel's brightness.
The whole is a lens: it blooms as futures differentiate and thins as light leaves. Width at a
column = the number of distinct live states; luminance of a channel = its probability mass;
total luminance only decreases left to right.

The v2 rendering recipe (additive light, three-pass strokes, squint test) is binding. Rings
live in the river, death leaves the page, conservation of light, human labels -- all stand.

Delivered with the still (data-fidelity proofs):
  A. trace audit: three real trace ids (a title, a July-27 exit, an alive-at-gate), their event
     sequences printed, highlighted on an overlay -- every bend maps to a listed event.
  B. reconciliation: 400 traces -> M drawn channels via shared prefixes, reported.
  C. perturbation: re-render from a second export (different seed); the composition must change.

Run:  python render_lens.py            # lens still + zoom + audit overlay + reconciliation
      python render_lens.py --alt EXPORT.json   # a perturbation render from another export
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
XL, XR = 155, S_W - 95
CY = S_H / 2
YT, YB = 96, S_H - 84
TMAX = 14
RING_R = 44
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


def _font(sz):
    try:
        return ImageFont.truetype(FONT_PATH, sz)
    except Exception:
        return ImageFont.load_default()


def trace_states(path):
    """State at each column 0..TMAX -- the data that can bend a trace's ROAD: fit, LaMelo
    availability, the season-1 run outcome, and the Ant commitment. (jaden is read only
    informationally and never re-sorts the policy, so it does not split the road.)"""
    nodes = sorted(path, key=lambda n: n["t"]); cur = None; j = 0; out = []
    for c in range(TMAX + 1):
        while j < len(nodes) and nodes[j]["t"] <= c:
            n = nodes[j]; cur = (n["fit"], n["melo"], n["run"], n["ant"]); j += 1
        out.append(cur)
    return out


def death_of(tr):
    t = tr["terminal"]
    if t == "RING":
        return (RING27_T, "ring27")
    if t.startswith("CONVERT@"):
        return (int(t.split("@")[1]), "exit")
    if t in ("REQUESTED", "EXPOSE"):
        return (min(tr["path"][-1]["t"], TMAX), "exit")
    return (TMAX, "gate")


def build(traces):
    """Returns per-trace states + death, and the channel graph: for each column the distinct
    live prefixes (channels), each with mass, a y, and a parent channel."""
    T = []
    for tr in traces:
        dcol, kind = death_of(tr)
        T.append({"st": trace_states(tr["path"]), "w": tr["weight"], "dcol": dcol, "kind": kind,
                  "codes": tr["codes"], "id": tr["id"], "term": tr["terminal"]})
    # base order for a planar (non-crossing) layout: sort by the full state sequence
    order = sorted(range(len(T)), key=lambda i: tuple(map(str, T[i]["st"])))
    base_rank = {i: k for k, i in enumerate(order)}

    def sig(i, c):
        return tuple(T[i]["st"][0:c + 1])

    # channels per column (only traces still live at that column)
    chan_y, chan_mass, chan_parent = {}, {}, {}
    n_by_col = {}
    for c in range(TMAX + 1):
        groups = defaultdict(list)
        for i in range(len(T)):
            if T[i]["dcol"] >= c:
                groups[sig(i, c)].append(i)
        gord = sorted(groups, key=lambda s: sum(base_rank[i] for i in groups[s]) / len(groups[s]))
        n = len(groups); n_by_col[c] = n
        for gi, s in enumerate(gord):
            chan_mass[(c, s)] = sum(T[i]["w"] for i in groups[s])
            chan_parent[(c, s)] = s[:-1] if c > 0 else None
            chan_y[(c, s)] = gi  # ordinal for now; y computed after SLOT is known
    n_max = max(n_by_col.values())
    slot = min(26.0, (S_H * 0.66) / max(1, n_max))
    for (c, s), gi in list(chan_y.items()):
        chan_y[(c, s)] = CY + (gi - (n_by_col[c] - 1) / 2) * slot
    return T, sig, chan_y, chan_mass, n_by_col, n_max


def _splat(buf, p0, p1, amt):
    x0, y0 = p0; x1, y1 = p1
    d = math.hypot(x1 - x0, y1 - y0); m = max(2, int(d / 2.2))
    xs = np.linspace(x0, x1, m); ys = np.linspace(y0, y1, m)
    mm = (xs >= 0) & (xs < S_W) & (ys >= 0) & (ys < S_H)
    np.add.at(buf, (ys[mm].astype(int), xs[mm].astype(int)), amt)


def render(traces, highlight=None):
    T, sig, chan_y, chan_mass, n_by_col, n_max = build(traces)
    living = np.zeros((S_H, S_W), float); gold = np.zeros((S_H, S_W), float); rose = np.zeros((S_H, S_W), float)
    hi = np.zeros((S_H, S_W), float)
    base = np.empty((S_H, S_W, 3), float); base[:] = BG
    img0 = Image.fromarray(base.astype(np.uint8)); dc = ImageDraw.Draw(img0, "RGBA")
    for t in HUMAN:
        x = col_x(t); dc.line([x, YT - 6, x, YB + 6], fill=(120, 140, 180, 7), width=1)
    base = np.asarray(img0, float)

    MB = max(chan_mass.values())
    # channel segments: each channel connects to its parent; brightness = mass (accumulation)
    for (c, s), y in chan_y.items():
        if c == 0:
            continue
        ps = s[:-1]
        py = chan_y.get((c - 1, ps))
        if py is None:
            continue
        if chan_mass[(c, s)] < 0.0012:                        # the faintest tail: below one thread, skip
            continue
        x0, x1 = col_x(c - 1), col_x(c)
        amt = 1.1 * (chan_mass[(c, s)] / MB) ** 0.88          # luminance from mass ONLY (no base -> not uniform)
        jog = abs(y - py)
        _splat(living, (x0, py), (x1 - jog, py), amt)         # run, then a caused bend at the column
        _splat(living, (x1 - jog, py), (x1, y), amt)
    # endings: rings entered (gold), exits leave the page and fade (rose whisper)
    for i in range(len(T)):
        d, kind = T[i]["dcol"], T[i]["kind"]
        y = chan_y.get((d, sig(i, d)))
        if y is None:
            continue
        x = col_x(d); w = T[i]["w"] / MB
        if kind == "ring27":
            _splat(gold, (x, y), (col_x(RING27_T) - RING_R + 2, CY), 0.05 + w)
        elif kind == "exit":
            span = col_x(min(TMAX, d + 1.5)) - x; dy = span * (-1 if y < CY else 1)
            _splat(living, (x, y), (x + span * 0.4, y + dy * 0.4), 0.12)
            _splat(rose, (x + span * 0.4, y + dy * 0.4), (x + span, y + dy), 0.05)
    if highlight:
        for i in highlight:
            prev = None
            for c in range(0, T[i]["dcol"] + 1):
                y = chan_y.get((c, sig(i, c)))
                if y is None:
                    break
                p = (col_x(c), y)
                if prev:
                    jog = abs(p[1] - prev[1])
                    _splat(hi, prev, (p[0] - jog, prev[1]), 1.0); _splat(hi, (p[0] - jog, prev[1]), p, 1.0)
                prev = p

    def three(b, a, m, c):
        return a * gaussian_filter(b, 6.0) + m * gaussian_filter(b, 2.2) + c * gaussian_filter(b, 0.8)
    L = np.zeros((S_H, S_W, 3), float)
    L += TEAL[None, None, :] * three(living, 0.04, 0.085, 0.24)[..., None]
    L += GOLD[None, None, :] * three(gold, 0.05, 0.12, 0.42)[..., None]
    L += ROSE[None, None, :] * three(rose, 0.03, 0.05, 0.10)[..., None]
    if highlight:
        L += np.array([255, 255, 255])[None, None, :] * three(hi, 0.02, 0.05, 0.5)[..., None] * 0.6
    out = 255.0 * (1 - np.exp(-(base + L * 255.0) / 300.0))
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for t in (RING27_T, RING28_T):
        cx = col_x(t)
        d.ellipse([cx - RING_R, CY - RING_R, cx + RING_R, CY + RING_R], outline=(*GOLD.astype(int), 255), width=3)
    _chrome(d, n_max, len(chan_y), len(T))
    return img, T, sig, chan_y, n_max


def _chrome(d, n_max, n_chan, n_tr):
    d.text((30, 28), "ONE RIVER", font=_font(21), fill=(*INK, 240))
    d.text((30, 58), "every future the board holds, grown from Now as one thread. it splits only where the data diverges,",
           font=_font(13), fill=(*INK, 165))
    d.text((30, 74), "and only narrows as futures leave. width = distinct live states · brightness = probability mass.",
           font=_font(13), fill=(*INK, 165))
    for t, lab in HUMAN.items():
        x = col_x(t); d.text((x - len(lab) * 3.1, YB + 20), lab, font=_font(12), fill=(*INK, 170))
    d.text((S_W - 560, S_H - 26), f"SOLVER · box · {n_tr} traces -> {n_chan} channels (peak width {n_max} states)",
           font=_font(11), fill=(*INK, 150))


def audit(T, sig, chan_y):
    """Pick a title, a July-27 exit, and an alive-at-gate trace; return ids + event tables."""
    pick = {}
    for i in range(len(T)):
        k = T[i]["kind"]; term = T[i]["term"]
        if term == "RING" and "title" not in pick:
            pick["title"] = i
        elif k == "exit" and T[i]["dcol"] == 9 and "exit" not in pick:
            pick["exit"] = i
        elif k == "gate" and "gate" not in pick:
            pick["gate"] = i
    rows = []
    for label, i in pick.items():
        rows.append((label, T[i]["id"], T[i]["term"], T[i]["codes"]))
    return list(pick.values()), rows


def main():
    if "--alt" in sys.argv:
        exp = json.loads(Path(sys.argv[sys.argv.index("--alt") + 1]).read_text())
        img, *_ = render(exp["forks"]["box"]["traces"])
        img.save(HERE / "stills" / "lens_box_alt.png"); print("wrote lens_box_alt.png"); return
    export = json.loads((HERE / "board_viz_export.json").read_text())
    traces = export["forks"]["box"]["traces"]
    out = HERE / "stills"; out.mkdir(exist_ok=True)
    img, T, sig, chan_y, n_max = render(traces)
    img.save(out / "lens_box_full.png")
    x0, x1 = int(col_x(4)), S_W; y0, y1 = int(CY - S_H * 0.34), int(CY + S_H * 0.34)
    img.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * 1.55), int((y1 - y0) * 1.55)), Image.LANCZOS).save(out / "lens_box_zoom50.png")
    hi_ids, rows = audit(T, sig, chan_y)
    aimg, *_ = render(traces, highlight=hi_ids)
    aimg.save(out / "lens_box_audit.png")
    (out / "lens_audit_table.json").write_text(json.dumps(rows, indent=1))
    print(f"wrote lens_box_full.png, lens_box_zoom50.png, lens_box_audit.png | {len(chan_y)} channels")
    for label, tid, term, codes in rows:
        print(f"  AUDIT {label:6s} id={tid} term={term}: {' > '.join(codes)}")


if __name__ == "__main__":
    main()
