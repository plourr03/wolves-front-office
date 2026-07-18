"""Radial composition stills for the ONE FOR ALL board (art-direction v2, binding).

Renders board_viz_export.json to PNG stills with a numpy ADDITIVE-light software
renderer (a float buffer IS globalCompositeOperation 'lighter'), so the binding
rendering recipe is honored exactly:

  - additive light for the living field; density = luminance = probability
  - monochrome teal journeys, colored ONLY at endings (gold center + ring dive,
    red dead-end glyph, rose exit segment)
  - three-pass strokes (halo / mid / core) via multi-scale blur; weight modulates
    alpha, never width
  - dead futures drawn first, source-over, dark #1A2540, beneath the light
  - radial overdraw guard: alpha falls toward center so the middle never whites out
    (title dives excepted)
  - prefix-braid angles: traces sharing a code prefix share an angle at that radius
    and only diverge after their codes diverge, so the root is one braid unwinding
  - mono type only, labels on one spoke + margins, provenance footer

Semantics:
  - one gold ring at dead center is a TERMINAL, never a waypoint; no non-ring path
    enters its exclusion radius
  - radius is time: NOW at the rim, hairline calendar circles inward, GATE innermost
  - RING futures leave their circle and dive to center at their win year
  - ALIVE-at-gate futures terminate ON the gate circle, crowding it
  - CONVERT futures freeze at their death radius as small red rings (dead-end)
  - REQUESTED futures curve outward and leave past the rim (rose)

Deliver: full, 50%-zoom, and a mid-season scrubber still (contracting now-circle,
diverged futures greyed). No interactivity.

Run:  python render_radial.py
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

S = 1600
CX = CY = S / 2
R_OUT = S * 0.430          # NOW (t=0) at the rim
R_GATE = S * 0.150         # GATE (t=14) innermost calendar circle
R_GOLD = S * 0.066         # the gold terminal ring
EXCL = R_GOLD + S * 0.018  # exclusion radius: no non-ring path enters
TMAX = 14

# palette (linear-ish for additive accumulation)
BG = np.array([10, 17, 32], float)
DEAD = np.array([26, 37, 64], float)
TEAL = np.array([53, 201, 192], float)
GOLD = np.array([242, 193, 78], float)
RED = np.array([226, 75, 74], float)
ROSE = np.array([196, 120, 140], float)
INK = (107, 123, 160)

FONT_PATH = "C:/Windows/Fonts/consola.ttf"


def r_of(t):
    return R_GATE + (R_OUT - R_GATE) * ((TMAX - min(t, TMAX)) / TMAX)


def classify(term):
    if term == "RING":
        return "ring"
    if term.startswith("CONVERT"):
        return "convert"
    if term == "REQUESTED":
        return "requested"
    if term == "EXPOSE":
        return "requested"
    return "committed"       # leaf-committed / leaf-<run>: alive at gate


def normalize(traces):
    """The full export carries path/codes/terminal; reduce to what the renderer uses."""
    out = []
    for tr in traces:
        out.append({"cls": classify(tr["terminal"]), "codes": tr.get("codes", []),
                    "pts": [[nd["t"], nd["health"], nd["equity"]] for nd in tr["path"]],
                    "term": tr["terminal"], "w": tr["weight"]})
    return out


# ------------------------------------------------- corridor-spiral angle model
# Corridors ARE identity: each trace is bundled by LaMelo's availability read (A/B/C),
# the earliest fork in its story. Three corridors of naturally UNEQUAL width (the
# reference-class prior A .336 / B .267 / C .397), so the field is organic, not a
# symmetric pinwheel, and the angle encodes something true.
COR_SEED = {"A": -math.pi / 2, "B": math.pi / 6, "C": math.pi * 0.92}   # uneven seeds
COR_WEDGE = {"A": 1.5, "B": 1.25, "C": 1.7}                             # arc each corridor fans into
SPIRAL = 1.15       # inward rotation so corridors spiral rather than radiate


def _smoothstep(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def _corridor(tr):
    for c in tr["codes"]:
        if c.startswith("AVAIL_"):
            return c[-1] if c[-1] in "ABC" else "B"
    return "B"


def braid_angles(traces):
    """Per-trace angle(t): bundled at the corridor seed at the rim, fanning smoothly into
    the corridor's wedge inward, the whole field spiralling. Corridor = LaMelo availability
    (A/B/C), so bundles mean something and widths are unequal."""
    groups = {"A": [], "B": [], "C": []}
    for i, tr in enumerate(traces):
        groups[_corridor(tr)].append(i)
    seed_a, home_a = {}, {}
    for cor, members in groups.items():
        cnt = max(1, len(members))
        seed = COR_SEED[cor]; wedge = COR_WEDGE[cor]
        for local, i in enumerate(sorted(members, key=lambda j: tuple(traces[j]["codes"]))):
            seed_a[i] = seed
            home_a[i] = seed + wedge * ((local + 0.5) / cnt - 0.5)
            home_a[i] += (((i * 2654435761) % 1000) / 1000 - 0.5) * (wedge / cnt) * 0.7

    def angle_of(i, t):
        d = _smoothstep(t / TMAX)
        return seed_a[i] * (1 - d) + home_a[i] * d + SPIRAL * (t / TMAX)
    return angle_of


# ------------------------------------------------- polyline builders
def journey_points(tr, angle_of, i, upto_t=TMAX):
    """The inward journey as smooth (x,y,r,a) points. Angle is sampled at fine time
    steps (not only at nodes) so the curve is a smooth polar spiral, no sharp corners."""
    ts = [p[0] for p in tr["pts"] if p[0] <= upto_t]
    if len(ts) < 2:
        return []
    t0, t1 = ts[0], ts[-1]
    pts = []
    steps = max(24, int((t1 - t0) * 6))
    for s in range(steps + 1):
        t = t0 + (t1 - t0) * s / steps
        r = r_of(t); a = angle_of(i, t)
        pts.append((CX + math.cos(a) * r, CY + math.sin(a) * r, r, a))
    return pts


def densify(xy, step=3.0):
    out = []
    for (x0, y0), (x1, y1) in zip(xy, xy[1:]):
        d = math.hypot(x1 - x0, y1 - y0)
        m = max(2, int(d / step))
        for s in range(m):
            f = s / m
            out.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    if xy:
        out.append(xy[-1])
    return out


def splat(buf, pts, amt, guard=True):
    if not pts:
        return
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    m = (xs >= 0) & (xs < S) & (ys >= 0) & (ys < S)
    xs, ys = xs[m].astype(int), ys[m].astype(int)
    a = np.full(xs.shape, amt, float)
    if guard:
        rr = np.hypot(xs - CX, ys - CY)
        # overdraw guard: fade toward the center so it cannot white out
        a *= np.clip((rr - EXCL) / (R_OUT - EXCL), 0.10, 1.0) ** 0.6
    np.add.at(buf, (ys, xs), a)


# ------------------------------------------------- main render
def render(fork, scrub_t=None):
    traces = normalize(EXPORT["forks"][fork]["traces"])
    angle_of = braid_angles(traces)
    living = np.zeros((S, S), float)
    gold = np.zeros((S, S), float)
    rose = np.zeros((S, S), float)
    gate_hits = []

    base = np.empty((S, S, 3), float); base[:] = BG
    img0 = Image.fromarray(base.astype(np.uint8)); dctx = ImageDraw.Draw(img0, "RGBA")
    # hairline calendar circles (4-6% alpha), gate emphasized
    for nd in EXPORT["nodes"]:
        r = r_of(nd["t"]); al = 20 if nd["t"] == 14 else 11
        dctx.ellipse([CX - r, CY - r, CX + r, CY + r], outline=(120, 140, 180, al), width=1)
    base = np.asarray(img0, float)

    red_glyphs = []
    for i, tr in enumerate(traces):
        cls = tr["cls"]
        t_term = _terminal_node(tr)
        resolved = scrub_t is None or t_term <= scrub_t   # has this future happened yet?
        jt = TMAX if scrub_t is None else min(scrub_t, t_term)
        jp = journey_points(tr, angle_of, i, upto_t=jt)
        if len(jp) < 2:
            continue
        dp = densify([(p[0], p[1]) for p in jp])
        if scrub_t is not None and not resolved:
            # still alive at the scrub moment: draw the inward journey to the now-circle, no ending
            splat(living, dp, 0.16)
            continue
        greyed = scrub_t is not None and cls in ("convert", "requested")  # already collapsed
        g = 0.22 if greyed else 1.0
        if cls == "convert":
            _draw_dead(base, dp)                        # dead journey, dark, beneath the light
            red_glyphs.append((jp[-1][0], jp[-1][1], greyed))
        elif cls == "requested":
            splat(living, dp, 0.16 * g)
            splat(rose, densify(_outward(jp[-1])), 0.10 * g, guard=False)
        elif cls == "ring":
            splat(living, dp, 0.20)
            splat(gold, densify(_dive(jp[-1]), step=2.0), 0.14, guard=False)
        else:  # committed / leaf: alive, terminate ON the gate circle (crowd it)
            splat(living, dp, 0.16)
            gate_hits.append(_on_gate(jp[-1]))
    for (gx, gy) in gate_hits:
        splat(living, [(gx, gy)] * 9, 0.75, guard=False)

    # ---- compose: three-pass additive light + guard, gold, rose ----
    def three(buf, a_halo, a_mid, a_core):
        return (a_halo * gaussian_filter(buf, 7.0) + a_mid * gaussian_filter(buf, 2.5)
                + a_core * gaussian_filter(buf, 0.9))
    L = np.zeros((S, S, 3), float)
    lt = three(living, 0.040, 0.085, 0.22)
    L += TEAL[None, None, :] * lt[..., None]
    gg = three(gold, 0.05, 0.12, 0.42)
    L += GOLD[None, None, :] * gg[..., None]
    rr = three(rose, 0.035, 0.07, 0.14)
    L += ROSE[None, None, :] * rr[..., None]

    out = base + L * 255.0
    # soft filmic tone-map so dense corridors glow without blowing to white
    out = 255.0 * (1.0 - np.exp(-out / 300.0))
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")

    # red dead-end glyphs (small rings frozen at death radius; greyed if collapsed in a scrub)
    for (x, y, gy) in red_glyphs:
        d.ellipse([x - 3.2, y - 3.2, x + 3.2, y + 3.2], outline=(*RED.astype(int), 90 if gy else 185), width=1)

    # the gate circle: the hallway the alive-at-gate futures crowd onto, none entering
    d.ellipse([CX - R_GATE, CY - R_GATE, CX + R_GATE, CY + R_GATE], outline=(*TEAL.astype(int), 95), width=1)

    # the one gold terminal ring at dead center (crisp, on top)
    d.ellipse([CX - R_GOLD, CY - R_GOLD, CX + R_GOLD, CY + R_GOLD], outline=(*GOLD.astype(int), 255), width=3)
    d.ellipse([CX - R_GOLD - 4, CY - R_GOLD - 4, CX + R_GOLD + 4, CY + R_GOLD + 4], outline=(*GOLD.astype(int), 70), width=1)

    if scrub_t is not None:                            # the contracting now-circle
        rs = r_of(scrub_t)
        d.ellipse([CX - rs, CY - rs, CX + rs, CY + rs], outline=(*TEAL.astype(int), 150), width=2)
    _labels(d, fork, scrub_t)
    _footer(d)
    return img


def _terminal_node(tr):
    """The node index where this future resolves (used by the scrubber)."""
    term = tr["term"]
    if term.startswith("CONVERT@"):
        return int(term.split("@")[1])
    if term == "RING":
        return tr["pts"][-1][0]
    return min(tr["pts"][-1][0], 14)      # requested / committed / leaf: last real node, gate-capped


def _draw_dead(base, dp):
    for (x, y) in dp[::2]:
        xi, yi = int(x), int(y)
        if 0 <= xi < S and 0 <= yi < S:
            base[yi, xi] = base[yi, xi] * 0.85 + DEAD * 0.15


def _outward(last):
    # short dim exit flick: a brief curl outward toward the rim, not a sweeping arc
    x, y, r, a = last
    out = [(x, y)]
    for s in range(1, 7):
        rr = r + s * (S * 0.010); aa = a + s * 0.035
        out.append((CX + math.cos(aa) * rr, CY + math.sin(aa) * rr))
    return out


def _dive(last):
    # delicate spiral in to the gold ring's edge (the title terminal), gentle curl
    x, y, r, a = last
    out = [(x, y)]
    for s in range(1, 22):
        f = s / 21
        rr = r * (1 - f) + (R_GOLD + 2) * f; aa = a + f * 0.28
        out.append((CX + math.cos(aa) * rr, CY + math.sin(aa) * rr))
    return out


def _on_gate(last):
    x, y, r, a = last
    return CX + math.cos(a) * R_GATE, CY + math.sin(a) * R_GATE


def _font(sz):
    try:
        return ImageFont.truetype(FONT_PATH, sz)
    except Exception:
        return ImageFont.load_default()


def _labels(d, fork, scrub_t):
    fs = _font(13)
    # all calendar text lives in the MARGINS, never over the field
    d.text((34, 28), "RADIAL", font=_font(22), fill=(*INK, 240))
    d.text((34, 60), f"fork {fork}  ·  radius = time", font=fs, fill=(*INK, 195))
    d.text((34, 78), "NOW at the rim  →  the 2028 GATE at the center", font=fs, fill=(*INK, 150))
    d.text((34, 94), "gold ring = the title (a terminal, nothing else enters)", font=fs, fill=(*INK, 150))
    # a compact time axis down the right margin (out of the field)
    xa = S - 150
    d.text((xa, 30), "time inward", font=fs, fill=(*INK, 150))
    for k, (t, txt) in enumerate([(0, "NOW  Jul26"), (5, "read R2  Jan27"), (6, "deadline  Feb27"),
                                  (9, "gate  Jul27"), (13, "lottery  May28"), (14, "GATE  2028")]):
        yy = 54 + k * 18
        d.text((xa, yy), txt, font=fs, fill=(*INK, 175))
    d.text((CX - 22, CY + R_GOLD + 9), "TITLE", font=_font(12), fill=(*GOLD.astype(int), 220))
    if scrub_t is not None:
        d.text((34, 116), f"season scrubber @ node {scrub_t}: now-circle contracted, diverged futures greyed",
               font=fs, fill=(*INK, 200))


def _footer(d):
    m = EXPORT["meta"]
    f = _font(12)
    txt = (f"{m['source']} · cliff · forks rapm {m['fork_weights']['rapm']} / box {m['fork_weights']['box']}"
           f" · cap {m['salvage_cap']} · P(east) {m['p_east']} · {m['n_traces_per_fork']} traces/fork"
           f" · export {m['generated'].replace('T', ' ').replace('+00:00', 'Z')}")
    d.text((30, S - 34), txt, font=f, fill=(*INK, 200))
    leg = "endings:  gold = title   teal = alive at gate   red = reset (dead)   rose = Ant departs"
    d.text((30, S - 54), leg, font=f, fill=(*INK, 180))


def main():
    outdir = HERE / "stills"; outdir.mkdir(exist_ok=True)
    full = render("box")
    full.save(outdir / "radial_box_full.png")
    # 50% zoom: crop the central half and upscale (shows the gate crowd + gold dive)
    half = int(S * 0.25)
    full.crop((half, half, S - half, S - half)).resize((S, S), Image.LANCZOS).save(outdir / "radial_box_zoom50.png")
    # mid-season scrubber: freeze just after the Jul-2027 boundary (node 10), where the
    # node-9 collapse has fired -- resets greyed, survivors still streaming toward the gate
    render("box", scrub_t=10).save(outdir / "radial_box_scrubber_mid.png")
    # the grim fork for contrast
    render("rapm").save(outdir / "radial_rapm_full.png")
    for p in ("radial_box_full.png", "radial_box_zoom50.png", "radial_box_scrubber_mid.png", "radial_rapm_full.png"):
        print(f"wrote {outdir/p} ({(outdir/p).stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
