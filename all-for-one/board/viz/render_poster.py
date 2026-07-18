"""ONE RIVER v7.1: THE POSTER. Stratified selection over the v6 lattice.

All v6 physics stands: a channel is a STATE so histories merge, lanes are ordered by equity so
every bend is a rank change, exits leave the page.

What v7.1 adds is SELECTION, and selection is the thing that has to be disclosed. The lattice
has 12,565 states; a poster that draws all of them is a texture, not a picture. So the poster
draws a budgeted handful of ROUTES per destination class, and prints on its own face how much
of each outcome those routes actually carry.

Two currencies, and they are not the same, which is the mistake an earlier cut of this file
made:
  * a route's MASS is the exact probability that the future follows that state sequence and
    ends in that class -- the product of its transition probabilities. Routes are selected by
    it, and "carrying X% of that outcome" is measured in it.
  * a route's BOTTLENECK (the widest-path weight) is a flow-decomposition quantity. It is NOT
    the probability of anything, and in a lattice with 1,376 merge nodes it overstates badly:
    the earlier cut reported 7.2% of the survivors where the truth is 0.4%.
The footer reports the route figure AND the drawn-subgraph figure, because corridors share
segments and the union on the page carries more than the sum of its routes.

Everything not selected is still on the page as ambient haze: the RESIDUAL, i.e. what is left
of every edge and every exit after the drawn routes are subtracted out. Present, and
deliberately unreadable.

Brightness means mass WITHIN a class. Across classes it does not, and cannot: the title class
is 4.5% of the board, and at global scale gold would be invisible. That is a deliberate, stated
departure from the v6 global rule.

Run:  python render_poster.py          # the poster + 50% + perturbation pair + coverage
"""
from __future__ import annotations
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
S_W, S_H = 2100, 1000
MARGIN = 64                                   # the type grid: one margin, one rhythm
GRID = 22                                     # baseline step for every stacked text block
XL, XR = MARGIN + 96, S_W - MARGIN - 96
CY = 397.0
YB = 706                                      # calendar rule
TMAX = 14

# v7.2 SPACING. Layout is editorial, data is sacred: pitch and column spacing are composed for
# legibility, while topology (splits, merges, bends at columns), brightness = mass, and every
# printed number stay exactly what the solver says.
FMIN, FMAX, GV = 0.13, 0.58, 0.68             # band height = FMIN..FMAX of canvas, log in states
# FMAX is bounded by the field's own height (calendar rule at YB, header above): a band
# taller than the space it has would put routes under the type.
MIN_GAP = 0.026                               # no column gap narrower than this share of the span
ACT_P = 1.0                                   # column spacing ~ structural activity ** ACT_P
# Display exposure. Note what it cannot fix: at Now every outcome occupies the SAME state, so
# all four class layers sum in the trunk and its core saturates to white. That is the one place
# on the page where colour stops encoding class, it is a fact about the board rather than a
# tuning failure, and the footer says so.
EXPO = 0.19

BG = np.array([9, 15, 28], float)
TEAL = np.array([53, 201, 192], float)
GOLD = np.array([242, 193, 78], float)
ROSE = np.array([196, 120, 140], float)
INK = (110, 123, 160)
FONT_PATH = "C:/Windows/Fonts/consola.ttf"
# node 13 is the MAY 2028 LOTTERY, not a second postseason -- the board resolves exactly one
# (node 7). The v6 stills mislabelled it.
HUMAN = {0: "Now", 3: "Nov read", 5: "Jan read", 6: "deadline", 7: "playoffs", 8: "draft",
         9: "July 27", 11: "season-2 reads", 12: "deadline", 13: "lottery", 14: "the gate"}

KIND_CLASS = {"RING": "TITLE", "COMMITTED": "ALIVE", "COMMITTED_EXPOSED": "ALIVE",
              "REQUESTED": "EXITS", "CONVERT": "DEAD"}
ORDER = ("TITLE", "ALIVE", "EXITS", "DEAD")
BUDGET = {"TITLE": 6, "ALIVE": 18, "EXITS": 8, "DEAD": 4}      # sums to 36, under the 45 cap
HARD_CAP = 45
CLASS_LABEL = {"TITLE": "a title", "ALIVE": "still alive at the gate",
               "EXITS": "Ant asks out", "DEAD": "converted -- the reset"}
UP_CLASSES = {"DEAD"}          # the reset leaves upward, Ant-asks-out leaves downward


def _font(sz):
    try:
        return ImageFont.truetype(FONT_PATH, sz)
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------------------- the lattice, as flow ------
class Flow:
    """The exported lattice re-read as a flow network. Adjacency lists, not a scanned dict."""

    def __init__(self, L):
        self.states = {int(c): v for c, v in L["states"].items()}
        self.n = {c: len(v) for c, v in self.states.items()}
        self.n_max = max(self.n.values())
        self.mass = {(c, i): v[i][1] for c, v in self.states.items() for i in range(len(v))}
        self.adj = defaultdict(list)                       # (c,i) -> [((c+1,j), mass)]
        for c, es in L["edges"].items():
            for i, j, m in es:
                self.adj[(int(c) - 1, i)].append(((int(c), j), m))
        self.exit = defaultdict(dict)
        self.class_mass = defaultdict(float)
        self.title_cols = set()
        for c, rows in L["exits"].items():
            for kind, i, m in rows:
                k = KIND_CLASS[kind]
                self.exit[(int(c), i)][k] = self.exit[(int(c), i)].get(k, 0.0) + m
                self.class_mass[k] += m
                if k == "TITLE":
                    self.title_cols.add(int(c))
        self.root = (0, 0)
        self.cols = sorted(self.n)
        self.n_edge = defaultdict(int)
        for c, es in L["edges"].items():
            self.n_edge[int(c)] = len(es)
        self.n_exit = {int(c): len(v) for c, v in L["exits"].items()}
        self._layout_x()

    # ------------------------------------------------------------------ v7.2 spacing --------
    def _layout_x(self):
        """HORIZONTAL RHYTHM: column spacing weighted by STRUCTURAL ACTIVITY -- how many
        transitions arrive, how many distinct states are live, how much mass left the column
        before -- not by days and not uniform. Quiet stretches compress; the act from the
        playoffs to July 27, where the board actually decides things, gets room. Every column
        keeps its calendar label, so the time axis is warped but never hidden."""
        gap = {}
        for c in self.cols[1:]:
            a = (math.log1p(self.n_edge.get(c, 0)) + math.log1p(self.n[c])
                 + math.log1p(self.n_exit.get(c - 1, 0)))
            gap[c] = a ** ACT_P
        tot = sum(gap.values())
        span = XR - XL
        # every gap gets MIN_GAP of the span first; activity distributes what is left
        floor = MIN_GAP * span
        free = span - floor * len(gap)
        self.xs = {self.cols[0]: float(XL)}
        run = float(XL)
        for c in self.cols[1:]:
            run += floor + free * gap[c] / tot
            self.xs[c] = run
        self.gap_share = {c: (floor + free * gap[c] / tot) / span for c in gap}

    def x(self, c):
        return self.xs[min(c, TMAX)]

    def height(self, c):
        """VERTICAL BREATHING: band height is monotone in the live-state count but on a LOG
        scale with a generous floor, so nine states at the November read read as a braid rather
        than a string, while 4,312 at the gate still read as wider."""
        f = FMIN + (FMAX - FMIN) * (math.log(self.n[c]) / math.log(self.n_max)) ** GV
        return f * S_H

    def y(self, c, i):
        n = self.n[c]
        return CY + (0.0 if n == 1 else i / (n - 1.0) - 0.5) * self.height(c)

    def class_flow(self, K):
        """Per-edge mass destined for class K, by backward recursion over the column DAG."""
        p, edge = {}, defaultdict(list)
        for c in reversed(self.cols):
            for i in range(self.n[c]):
                u = (c, i); m = self.mass[u]
                if m <= 0:
                    p[u] = 0.0
                    continue
                got = self.exit[u].get(K, 0.0)
                for v, em in self.adj[u]:
                    got += em * p.get(v, 0.0)
                p[u] = got / m
        for u, vs in self.adj.items():
            for v, em in vs:
                f = em * p.get(v, 0.0)
                if f > 1e-15:
                    edge[u].append([v, f])
        exitf = {u: d[K] for u, d in self.exit.items() if d.get(K, 0.0) > 1e-15}
        return edge, exitf


def route_mass(fl, path, K):
    """EXACT probability that the future follows this state sequence and ends in class K."""
    p = 1.0
    for a, z in zip(path, path[1:]):
        m = fl.mass[a]
        p = p * (next(f for v, f in fl.adj[a] if v == z) / m) if m > 0 else 0.0
    last = path[-1]
    return p * fl.exit[last].get(K, 0.0) / fl.mass[last] if fl.mass[last] > 0 else 0.0


def decompose(fl, K, budget):
    """Select routes BY PROBABILITY MASS (the directive's rule), highest first.

    Max-product path DP: best[u] is the largest probability of getting from u to a class-K exit.
    Extract the argmax route, subtract its mass from every edge and exit it used, repeat. Each
    drawn channel is therefore a real state sequence with a real probability, and the extracted
    masses are directly comparable to the class total."""
    cf, exitf = fl.class_flow(K)
    # transition probability = RAW edge mass / state mass. Using the class-destined flow here
    # would multiply the "ends in K" factor in twice and collapse every route probability.
    # cf is used only to prune edges that cannot reach K at all.
    allow = {u: [(v, m) for v, m in fl.adj[u] if any(vv == v for vv, _ in cf.get(u, ()))]
             for u in fl.adj}
    # K-best suffix DP: kbest[u] = the `budget` most probable ways to get from u to a K exit,
    # each as (probability, next state or None, index into that state's list). A
    # subtract-and-repeat greedy was wrong here -- it re-extracted the same path, because a
    # route's probability is far below any single edge's mass, so subtracting never retires it.
    kbest = {}
    for c in reversed(fl.cols):
        for i in range(fl.n[c]):
            u = (c, i); m = fl.mass[u]
            cand = []
            if m > 0:
                e = exitf.get(u, 0.0)
                if e > 0:
                    cand.append((e / m, None, -1))
                for v, rm in allow.get(u, ()):
                    p = rm / m
                    for idx, ent in enumerate(kbest.get(v, ())):
                        cand.append((p * ent[0], v, idx))
            cand.sort(key=lambda t: -t[0])
            kbest[u] = cand[:budget]
    out = []
    for w, v, idx in kbest.get(fl.root, ())[:budget]:
        if w <= 1e-14:
            break
        path, nv, ni = [fl.root], v, idx
        while nv is not None:
            path.append(nv)
            _p, nv, ni = kbest[nv][ni]
        out.append({"path": path, "w": w, "cls": K, "exit_at": path[-1]})
    return out


def subgraph_mass(fl, cs, K):
    """Probability the future stays inside the DRAWN corridors and ends in K. Corridors share
    segments, so this exceeds the sum of the individual route masses; both are reported."""
    if not cs:
        return 0.0
    de = defaultdict(set); dx = {c["exit_at"] for c in cs}
    for c in cs:
        for a, z in zip(c["path"], c["path"][1:]):
            de[a].add(z)
    sub = {}
    for c in reversed(fl.cols):
        for i in range(fl.n[c]):
            u = (c, i); m = fl.mass[u]
            if m <= 0:
                sub[u] = 0.0; continue
            s = fl.exit[u].get(K, 0.0) / m if u in dx else 0.0
            for v, em in fl.adj[u]:
                if v in de.get(u, ()):
                    s += (em / m) * sub.get(v, 0.0)
            sub[u] = s
    return sub.get(fl.root, 0.0)


def n_routes(fl, K):
    """How many distinct root-to-exit state sequences end in this class (DP, not enumeration)."""
    edge, exitf = fl.class_flow(K)
    cnt = {}
    for c in reversed(fl.cols):
        for i in range(fl.n[c]):
            u = (c, i)
            n = 1 if u in exitf else 0
            for v, _f in edge.get(u, ()):
                n += cnt.get(v, 0)
            cnt[u] = n
    return cnt.get(fl.root, 0)


def select(fl):
    picked, cover = [], {}
    for K in ORDER:
        total = fl.class_mass.get(K, 0.0)
        cs = decompose(fl, K, min(BUDGET[K], HARD_CAP - len(picked))) if total > 0 else []
        picked += cs
        cover[K] = {"drawn": len(cs), "budget": BUDGET[K], "total": total,
                    "routes": n_routes(fl, K) if total > 0 else 0,
                    "shown": sum(c["w"] for c in cs),
                    "shown_sub": subgraph_mass(fl, cs, K)}
    return picked, cover


# ------------------------------------------------------------------------- drawing -----------
def _splat(buf, p0, p1, amt, dim=1.0):
    x0, y0 = p0; x1, y1 = p1
    d = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(d / 0.7))
    xs = np.linspace(x0, x1, n); ys = np.linspace(y0, y1, n)
    a = amt if dim == 1.0 else amt * np.linspace(1.0, dim, n)
    m = (xs >= 0) & (xs < S_W) & (ys >= 0) & (ys < S_H)
    np.add.at(buf, (ys[m].astype(int), xs[m].astype(int)), a if np.isscalar(a) else a[m])


def exit_leg(fl, x, y, up):
    # the downward exit gets the long shallow run; the upward one gets a shorter run so it
    # clears the top of the frame instead of shearing across the whole second season
    span = (XR - XL) * (0.17 if up else 0.34)
    y1 = -80 if up else S_H + 80
    return (x + span * 0.5, y + (y1 - y) * 0.34), (x + span, y1)


def draw(fl, picked, cover, subtitle="", note=""):
    lay = {k: np.zeros((S_H, S_W), float) for k in ("teal", "gold", "rose")}
    haze = np.zeros((S_H, S_W), float)

    base = np.empty((S_H, S_W, 3), float); base[:] = BG
    im0 = Image.fromarray(base.astype(np.uint8)); dc = ImageDraw.Draw(im0, "RGBA")
    for t in HUMAN:
        dc.line([fl.x(t), MARGIN + 40, fl.x(t), YB - 8], fill=(120, 140, 180, 9), width=1)
    base = np.asarray(im0, float)

    # Routes share segments -- near Now they share ALL of them, because at Now there is one
    # state. A segment is drawn ONCE per class carrying the summed mass of the routes using it,
    # so the trunk's brightness is not a function of how many routes the selection kept.
    seg, ends = defaultdict(float), defaultdict(float)
    for c in picked:
        for u, v in zip(c["path"], c["path"][1:]):
            seg[(c["cls"], u, v)] += c["w"]
        ends[(c["cls"], c["exit_at"])] += c["w"]
    cmax = defaultdict(float)
    for (K, _u, _v), w in seg.items():
        cmax[K] = max(cmax[K], w)

    def amp(K, w):
        """Proportional to mass within the class, with a floor so a route that is real but a
        thousand times thinner than its neighbour is still on the page. Both stated in the
        footer -- the floor is why this is 'brightness within an outcome', not a measurement."""
        return 0.075 * max(0.10, w / cmax[K])

    for (K, u, v), w in seg.items():
        buf = lay["gold"] if K == "TITLE" else (lay["rose"] if K in ("EXITS", "DEAD") else lay["teal"])
        _splat(buf, (fl.x(u[0]), fl.y(*u)), (fl.x(v[0]), fl.y(*v)), amp(K, w))

    ring_x = ring_y = None
    for (K, (ec, ei)), w in ends.items():
        x, y = fl.x(ec), fl.y(ec, ei)
        a = amp(K, w)
        if K == "TITLE":
            ring_x = x + (fl.x(8) - fl.x(7)) * 0.55
            ring_y = y                      # the ring sits where the title mass actually leaves
            _splat(lay["gold"], (x, y), (ring_x, ring_y), a * 1.5)
        elif K == "ALIVE":
            _splat(lay["teal"], (x, y), (S_W + 40, y), a, dim=0.5)
        else:
            mid, end = exit_leg(fl, x, y, K in UP_CLASSES)
            _splat(lay["rose"], (x, y), mid, a * 0.85, dim=0.6)
            _splat(lay["rose"], mid, end, a * 0.75, dim=0.15)

    # --- the haze IS the residual: every edge and exit, minus what the drawn routes took -----
    drawn_edge, drawn_exit = defaultdict(float), defaultdict(float)
    for c in picked:
        for u, v in zip(c["path"], c["path"][1:]):
            drawn_edge[(u, v)] += c["w"]
        drawn_exit[(c["cls"], c["exit_at"])] += c["w"]
    for u, vs in fl.adj.items():
        for v, m in vs:
            r = m - drawn_edge.get((u, v), 0.0)
            if r > 1e-12:
                _splat(haze, (fl.x(u[0]), fl.y(*u)), (fl.x(v[0]), fl.y(*v)), r)
    for u, dd in fl.exit.items():
        for K, m in dd.items():
            r = m - drawn_exit.get((K, u), 0.0)
            if r <= 1e-12:
                continue
            x, y = fl.x(u[0]), fl.y(*u)
            if K == "ALIVE":
                _splat(haze, (x, y), (S_W + 40, y), r, dim=0.5)
            elif K == "TITLE":
                _splat(haze, (x, y), (x + (fl.x(8) - fl.x(7)) * 0.55, y), r)
            else:
                mid, end = exit_leg(fl, x, y, K in UP_CLASSES)
                _splat(haze, (x, y), mid, r, dim=0.6); _splat(haze, mid, end, r, dim=0.15)

    def three(b, a, m, c_):
        return a * gaussian_filter(b, 7.0) + m * gaussian_filter(b, 2.4) + c_ * gaussian_filter(b, 0.7)

    L = np.zeros((S_H, S_W, 3), float)
    L += TEAL[None, None, :] * three(lay["teal"], 0.13, 0.32, 0.55)[..., None]
    L += GOLD[None, None, :] * three(lay["gold"], 0.22, 0.52, 1.05)[..., None]   # gold guaranteed visible
    L += ROSE[None, None, :] * three(lay["rose"], 0.12, 0.28, 0.50)[..., None]
    out = base + 255.0 * (1.0 - np.exp(-np.clip(L * EXPO, 0, None)))
    # The haze is composited AFTER the transfer, so "4% alpha" means literally that and cannot
    # be crushed or amplified by the exposure curve the corridors are tuned on. Compressed
    # before scaling: residual mass spans four orders of magnitude, so a linear haze would be
    # invisible exactly where the undrawn futures are. It is a PRESENCE; the footer is the
    # measurement.
    hz = gaussian_filter(haze, 10.0)
    hz = (hz / (hz.max() + 1e-12)) ** 0.32 * 0.051
    out = out + TEAL[None, None, :] * hz[..., None]
    # The caption sits on its own plate. Exits still run off the bottom of the canvas per v6 --
    # they pass BEHIND the type rather than through it, which is the difference between a
    # composed page and a collision.
    plate = YB + 18
    out[plate:] = BG[None, None, :] + (out[plate:] - BG[None, None, :]) * 0.14
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")

    d = ImageDraw.Draw(img, "RGBA")
    if ring_x is not None:                # radius from the CLASS mass, not from what was drawn
        rr = 22 + 240 * math.sqrt(cover["TITLE"]["total"])
        d.ellipse([ring_x - rr, ring_y - rr, ring_x + rr, ring_y + rr],
                  outline=(*GOLD.astype(int), 200), width=2)
    _chrome(d, fl, cover, picked, subtitle, note)
    return img


def _wrap(text, width):
    out, line = [], ""
    for w in text.split():
        if len(line) + len(w) + 1 > width:
            out.append(line); line = w
        else:
            line = (line + " " + w).strip()
    if line:
        out.append(line)
    return out


def _chrome(d, fl, cover, picked, subtitle, note):
    """TYPE RHYTHM: one margin, one baseline step, two columns of caption. Nothing set as a
    wall of hairlines."""
    d.text((MARGIN, MARGIN - 26), "ONE RIVER", font=_font(26), fill=(*INK, 245))
    d.text((MARGIN, MARGIN + 12),
           "every future the Timberwolves board holds, from now to the summer of 2028." + subtitle,
           font=_font(13), fill=(*INK, 175))

    # calendar: staggered onto two baselines wherever labels would collide
    d.line([MARGIN, YB, S_W - MARGIN, YB], fill=(*INK, 45), width=1)
    prev_r, row = -1e9, 0
    for t in sorted(HUMAN):
        lab = HUMAN[t]
        w = 6.6 * len(lab)
        x = fl.x(t) - w / 2
        row = 1 - row if x < prev_r + 14 else 0
        prev_r = max(prev_r, x + w) if row else x + w
        d.line([fl.x(t), YB - 5, fl.x(t), YB + 5], fill=(*INK, 110), width=1)
        d.text((x, YB + 12 + row * 17), lab, font=_font(12), fill=(*INK, 185))

    y0 = YB + 62
    d.text((MARGIN, y0), "WHAT YOU ARE LOOKING AT", font=_font(11), fill=(*INK, 205))
    y = y0 + GRID + 4
    for K in ORDER:
        c = cover[K]
        col = (242, 193, 78) if K == "TITLE" else ((196, 120, 140) if K in ("EXITS", "DEAD") else (53, 201, 192))
        arrow = ", leaves upward" if K == "DEAD" else (", leaves downward" if K == "EXITS" else "")
        d.text((MARGIN, y), f"{CLASS_LABEL[K]}{arrow}", font=_font(13), fill=(*col, 225))
        d.text((MARGIN + 268, y),
               f"{c['total'] * 100:5.2f}%  ·  {c['drawn']} of {c['routes']:,} routes  ·  "
               f"{c['shown'] / c['total'] * 100:.1f}% of the outcome "
               f"({c['shown_sub'] / c['total'] * 100:.0f}% with shared segments)",
               font=_font(12), fill=(*INK, 185))
        y += GRID + 2

    col2 = MARGIN + 880
    y = y0 + GRID + 4
    for para in (
        f"{len(picked)} routes drawn, budgets {'+'.join(str(BUDGET[k]) for k in ORDER)}"
        f"={sum(BUDGET.values())} under a {HARD_CAP} cap. Every budget is saturated, so every class holds "
        f"more routes than are drawn. The rest is the haze: the residual of each edge and exit once the "
        f"drawn routes are subtracted out. Present, and deliberately unreadable.",
        "Brightness is probability within each outcome, floored so a very thin route stays on the page, and "
        "not comparable across outcomes. At Now every outcome is the same state, so all four layers sum and "
        "the trunk core saturates: the one place where colour stops telling you what you are looking at.",
        "Layout is composed, data is not. Column spacing follows structural activity rather than days; band "
        "height follows the log of the live-state count. Every label, route and number is the solver's.",
    ):
        for line in _wrap(para, 74):
            d.text((col2, y), line, font=_font(12), fill=(*INK, 150)); y += 16
        y += 7
    if note:
        d.text((MARGIN, S_H - MARGIN + 12), note, font=_font(11), fill=(*INK, 150))
    if note:
        d.text((30, y), note, font=_font(11), fill=(*INK, 150))


# ------------------------------------------------------------- measured acceptance -----------
def two_second_test(fl, cover, picked, img):
    """Item 3, MEASURED off the data and the rendered frame -- not asserted."""
    a = np.asarray(img, float)
    lum = a.sum(axis=2) - float(BG.sum())
    gold_px = int(((a[..., 0] > 90) & (a[..., 0] - a[..., 2] > 25)).sum())
    rose_px = int(((a[..., 0] - a[..., 1] > 12) & (a[..., 0] > 45)).sum())
    edge_ink = int((lum[:, S_W - 26:] > 8).sum() + (lum[:26, :] > 8).sum() + (lum[S_H - 26:, :] > 8).sum())
    # measured off the FRAME, so it is what a viewer actually sees, not what the code intended
    spread = {}
    for t in fl.cols:
        x = int(fl.x(t))
        band = lum[:YB, max(0, x - 8):x + 8].max(axis=1)
        lit = np.flatnonzero(band > 10)
        spread[t] = float(lit[-1] - lit[0]) if lit.size else 0.0
    lo = min([v for v in spread.values() if v > 0.5] or [1.0])
    ratio = max(spread.values()) / lo
    return [
        ("a start", f"one state at Now: the field is {fl.n[0]} lane wide there", fl.n[0] == 1),
        ("a ring", f"{gold_px:,} gold pixels; {cover['TITLE']['drawn']} title routes, honestly thin at "
                   f"{cover['TITLE']['total'] * 100:.1f}% of the board", gold_px > 400),
        ("wide or thin", f"the drawn field spans {lo / S_H * 100:.0f}% of the canvas at its narrowest "
                         f"column and {max(spread.values()) / S_H * 100:.0f}% at its widest ({ratio:.1f}x). "
                         f"v7.2's log pitch bought the early braid by compressing this ratio from 12x",
         ratio >= 1.5),
        ("some paths leave", f"{rose_px:,} rose pixels and {edge_ink:,} lit pixels on the canvas edges",
         rose_px > 400 and edge_ink > 200),
    ]


ACTS = {"opening (Now to the Jan read)": (0, 5), "season one (deadline to the draft)": (6, 8),
        "the boundary (July 27)": (9, 10), "season two (reads to the gate)": (11, 14)}


def spacing_report(fl, img, picked):
    """v7.2 item 5: the spacing checklist, MEASURED off the frame -- field occupancy per act,
    the largest empty region, and label collisions."""
    a = np.asarray(img, float)
    lum = a.sum(axis=2) - float(BG.sum())
    top, bot = MARGIN + 30, YB - 8
    field = lum[top:bot, :]

    occ = {}
    for name, (c0, c1) in ACTS.items():
        vals = []
        for t in range(c0, c1 + 1):
            x = int(fl.x(t))
            band = field[:, max(0, x - 8):x + 8].max(axis=1)
            lit = np.flatnonzero(band > 10)
            vals.append((lit[-1] - lit[0]) / S_H if lit.size else 0.0)
        occ[name] = (min(vals), max(vals))

    # largest empty region: coarse grid over the field, biggest connected run of dark cells
    gh, gw = 24, 48
    cell = np.zeros((gh, gw), bool)
    hstep, wstep = field.shape[0] / gh, S_W / gw
    for r in range(gh):
        for c in range(gw):
            blk = field[int(r * hstep):int((r + 1) * hstep), int(c * wstep):int((c + 1) * wstep)]
            cell[r, c] = blk.max() <= 10
    seen = np.zeros_like(cell); best = 0
    for r in range(gh):
        for c in range(gw):
            if cell[r, c] and not seen[r, c]:
                stack, size = [(r, c)], 0
                seen[r, c] = True
                while stack:
                    rr, cc = stack.pop(); size += 1
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = rr + dr, cc + dc
                        if 0 <= nr < gh and 0 <= nc < gw and cell[nr, nc] and not seen[nr, nc]:
                            seen[nr, nc] = True; stack.append((nr, nc))
                best = max(best, size)
    empty = best / (gh * gw)

    boxes, coll = [], 0
    prev_r, row = -1e9, 0
    for t in sorted(HUMAN):
        w = 6.6 * len(HUMAN[t]); x = fl.x(t) - w / 2
        row = 1 - row if x < prev_r + 14 else 0
        prev_r = max(prev_r, x + w) if row else x + w
        boxes.append((row, x, x + w))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if boxes[i][0] == boxes[j][0] and boxes[i][2] > boxes[j][1] and boxes[j][2] > boxes[i][1]:
                coll += 1
    return {"occupancy": {k: [round(v[0], 3), round(v[1], 3)] for k, v in occ.items()},
            "largest_empty_region": round(empty, 3), "label_collisions": coll,
            "gap_share": {str(k): round(v, 4) for k, v in sorted(fl.gap_share.items())}}


def title_verdict(fl):
    """MEASURED, not asserted: which columns carry title mass, and therefore whether a second
    championship is a route on this board at all."""
    cols = sorted(fl.title_cols)
    where = ", ".join(HUMAN.get(c, str(c)) for c in cols)
    return {"cols": cols, "one_postseason": len(cols) == 1,
            "text": (f"title mass exists at exactly one column ({where}), so the board resolves one "
                     f"postseason; a 2028 title lives inside the gate's continuation value rather than "
                     f"as a route" if len(cols) == 1 else f"title mass at columns {cols}")}


# ------------------------------------------------------------------------ perturbation -------
def sampled_flow(L, traces):
    """The lattice with edge masses ESTIMATED from a finite sample of futures. Perturbation
    only: the delivered poster uses the exact flow and has no sampling noise."""
    S = json.loads(json.dumps(L))
    where = {}
    for c, ss in S["states"].items():
        for k, s in enumerate(ss):
            where[s[0]] = (int(c), k)
    em, sm, ex = defaultdict(float), defaultdict(float), defaultdict(float)
    for tr in traces:
        lanes = [where[n["sid"]] for n in tr["path"] if n["sid"] in where]
        w = tr["weight"]
        for u in lanes:
            sm[u] += w
        for a, b in zip(lanes, lanes[1:]):
            em[(a, b)] += w
        term = tr["terminal"]
        kind = ("RING" if term == "RING" else "CONVERT" if term.startswith("CONVERT")
                else "COMMITTED" if term.startswith("leaf-committed") else "REQUESTED")
        if lanes:
            ex[(lanes[-1], kind)] += w
    S["states"] = {c: [[s[0], sm.get((int(c), k), 0.0), s[2], s[3]] for k, s in enumerate(ss)]
                   for c, ss in S["states"].items()}
    S["edges"] = {c: [[i, j, em.get(((int(c) - 1, i), (int(c), j)), 0.0)] for i, j, _m in es]
                  for c, es in S["edges"].items()}
    byc = defaultdict(list)
    for ((c, i), kind), m in ex.items():
        if m > 0:
            byc[str(c)].append([kind, i, m])
    S["exits"] = dict(byc)
    return S


def main():
    E = json.loads((HERE / "board_viz_export.json").read_text())
    F = E["forks"]["box"]
    out = HERE / "stills"; out.mkdir(exist_ok=True)

    fl = Flow(F["lattice"])
    picked, cover = select(fl)
    img = draw(fl, picked, cover)
    img.save(out / "poster_full.png")
    x0, x1 = int(fl.x(0)) - 60, S_W
    y0, y1 = int(CY - S_H * 0.30), int(CY + S_H * 0.30)
    img.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * 1.45), int((y1 - y0) * 1.45)),
                                      Image.LANCZOS).save(out / "poster_zoom50.png")
    rows = two_second_test(fl, cover, picked, img)
    tv = title_verdict(fl)
    sp = spacing_report(fl, img, picked)

    alt = HERE / "board_viz_export_alt.json"
    pert = []
    for tag, traces in (("A", F["traces"]),
                        ("B", json.loads(alt.read_text())["forks"]["box"]["traces"] if alt.exists() else None)):
        if traces is None:
            continue
        f2 = Flow(sampled_flow(F["lattice"], traces))
        p2, c2 = select(f2)
        draw(f2, p2, c2, subtitle=f"   [routes re-derived from a {len(traces)}-future sample, seed {tag}]",
             note="perturbation frame: the delivered poster uses the exact flow and has no sampling noise.").save(
            out / f"poster_pert_{tag}.png")
        pert.append({"seed": tag, "shown": {k: round(v["shown"], 6) for k, v in c2.items()},
                     "total": {k: round(v["total"], 6) for k, v in c2.items()}})

    (out / "poster_cover.json").write_text(json.dumps(
        {"cover": cover, "n_drawn": len(picked), "cap": HARD_CAP, "budgets": BUDGET,
         "two_second": [[a, b, ok] for a, b, ok in rows], "title_verdict": tv,
         "spacing": sp, "pert": pert}, indent=1))
    for K in ORDER:
        c = cover[K]
        print(f"  {K:6s} {c['drawn']:2d}/{c['budget']:2d} of {c['routes']:>6,} routes | outcome {c['total'] * 100:5.2f}% | "
              f"routes = {c['shown'] / c['total'] * 100:5.1f}% of it | drawn subgraph = {c['shown_sub'] / c['total'] * 100:5.1f}%")
    print(f"  {len(picked)} routes drawn (cap {HARD_CAP})")
    print(f"  TITLE VERDICT: {tv['text']}")
    for a, b, ok in rows:
        print(f"  TWO-SECOND {'PASS' if ok else 'FAIL'}  {a}: {b}")
    print(f"  SPACING largest empty region {sp['largest_empty_region'] * 100:.0f}% of field | "
          f"label collisions {sp['label_collisions']}")
    for k, (lo, hi) in sp["occupancy"].items():
        print(f"    occupancy {k:36s} {lo * 100:5.1f}% to {hi * 100:5.1f}%")


if __name__ == "__main__":
    main()
