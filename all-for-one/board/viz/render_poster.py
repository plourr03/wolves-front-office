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
S_W, S_H = 2100, 900
XL, XR = 150, S_W - 150
CY, BAND = 392.0, 600.0
YB = 700
TMAX = 14
HEXP = 0.5          # column height = n_states ** HEXP (disclosed in the footer)
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


def col_x(t):
    return XL + (XR - XL) * (min(t, TMAX) / TMAX)


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

    def height(self, c):
        return BAND * (self.n[c] ** HEXP) / (self.n_max ** HEXP)

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


def exit_leg(x, y, up):
    span = (XR - XL) / TMAX * 5.4
    y1 = -80 if up else S_H + 80
    return (x + span * 0.5, y + (y1 - y) * 0.34), (x + span, y1)


def draw(fl, picked, cover, subtitle="", note=""):
    lay = {k: np.zeros((S_H, S_W), float) for k in ("teal", "gold", "rose")}
    haze = np.zeros((S_H, S_W), float)

    base = np.empty((S_H, S_W, 3), float); base[:] = BG
    im0 = Image.fromarray(base.astype(np.uint8)); dc = ImageDraw.Draw(im0, "RGBA")
    for t in HUMAN:
        dc.line([col_x(t), 96, col_x(t), YB - 6], fill=(120, 140, 180, 9), width=1)
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
        _splat(buf, (col_x(u[0]), fl.y(*u)), (col_x(v[0]), fl.y(*v)), amp(K, w))

    ring_x = None
    for (K, (ec, ei)), w in ends.items():
        x, y = col_x(ec), fl.y(ec, ei)
        a = amp(K, w)
        if K == "TITLE":
            ring_x = x + (col_x(1) - col_x(0)) * 0.62
            _splat(lay["gold"], (x, y), (ring_x, CY), a * 1.5)
        elif K == "ALIVE":
            _splat(lay["teal"], (x, y), (S_W + 40, y), a, dim=0.5)
        else:
            mid, end = exit_leg(x, y, K in UP_CLASSES)
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
                _splat(haze, (col_x(u[0]), fl.y(*u)), (col_x(v[0]), fl.y(*v)), r)
    for u, dd in fl.exit.items():
        for K, m in dd.items():
            r = m - drawn_exit.get((K, u), 0.0)
            if r <= 1e-12:
                continue
            x, y = col_x(u[0]), fl.y(*u)
            if K == "ALIVE":
                _splat(haze, (x, y), (S_W + 40, y), r, dim=0.5)
            elif K == "TITLE":
                _splat(haze, (x, y), (x + (col_x(1) - col_x(0)) * 0.62, CY), r)
            else:
                mid, end = exit_leg(x, y, K in UP_CLASSES)
                _splat(haze, (x, y), mid, r, dim=0.6); _splat(haze, mid, end, r, dim=0.15)

    def three(b, a, m, c_):
        return a * gaussian_filter(b, 7.0) + m * gaussian_filter(b, 2.4) + c_ * gaussian_filter(b, 0.7)

    L = np.zeros((S_H, S_W, 3), float)
    L += TEAL[None, None, :] * three(lay["teal"], 0.13, 0.32, 0.55)[..., None]
    L += GOLD[None, None, :] * three(lay["gold"], 0.15, 0.38, 0.80)[..., None]
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
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")

    d = ImageDraw.Draw(img, "RGBA")
    if ring_x is not None:                # radius from the CLASS mass, not from what was drawn
        rr = 22 + 240 * math.sqrt(cover["TITLE"]["total"])
        d.ellipse([ring_x - rr, CY - rr, ring_x + rr, CY + rr], outline=(*GOLD.astype(int), 200), width=2)
    _chrome(d, cover, picked, subtitle, note)
    return img


def _chrome(d, cover, picked, subtitle, note):
    d.text((30, 26), "ONE RIVER", font=_font(22), fill=(*INK, 245))
    d.text((30, 58), "every future the Timberwolves board holds, from now to the summer of 2028." + subtitle,
           font=_font(13), fill=(*INK, 175))
    for t, lab in HUMAN.items():
        d.text((col_x(t) - len(lab) * 3.1, YB + 12), lab, font=_font(12), fill=(*INK, 180))

    y = YB + 44
    d.text((30, y), "WHAT YOU ARE LOOKING AT", font=_font(11), fill=(*INK, 210))
    for K in ORDER:
        c = cover[K]
        col = (242, 193, 78) if K == "TITLE" else ((196, 120, 140) if K in ("EXITS", "DEAD") else (53, 201, 192))
        arrow = " (leaves upward)" if K == "DEAD" else (" (leaves downward)" if K == "EXITS" else "")
        d.text((30, y + 18),
               f"{CLASS_LABEL[K]}{arrow}: {c['total'] * 100:.1f}% of the board. {c['drawn']} of "
               f"{c['routes']:,} routes drawn; those routes are {c['shown'] / c['total'] * 100:.1f}% of the "
               f"outcome, and {c['shown_sub'] / c['total'] * 100:.0f}% once shared segments are counted.",
               font=_font(11), fill=(*col, 205))
        y += 15
    y += 18
    for line in (
        f"{len(picked)} routes drawn (budgets {'+'.join(str(BUDGET[k]) for k in ORDER)}"
        f"={sum(BUDGET.values())}, hard cap {HARD_CAP}); every budget is saturated, so in every class "
        f"there are more routes than are drawn.",
        "brightness is probability WITHIN each outcome, floored so a very thin route is still on the page, "
        "and not comparable across outcomes. column height is the square root of the live state count.",
        "at Now every outcome is the same state, so all four layers sum and the trunk core saturates to "
        "white: the one place on this page where colour stops telling you which outcome you are looking at.",
        "everything not drawn is the haze: the residual of every edge and exit after the drawn routes are "
        "subtracted out. present, and deliberately unreadable.",
    ):
        d.text((30, y), line, font=_font(11), fill=(*INK, 150)); y += 15
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
        x = int(col_x(t))
        band = lum[:YB, max(0, x - 8):x + 8].max(axis=1)
        lit = np.flatnonzero(band > 10)
        spread[t] = float(lit[-1] - lit[0]) if lit.size else 0.0
    lo = min([v for v in spread.values() if v > 0.5] or [1.0])
    ratio = max(spread.values()) / lo
    return [
        ("a start", f"one state at Now: the field is {fl.n[0]} lane wide there", fl.n[0] == 1),
        ("a ring", f"{gold_px:,} gold pixels; {cover['TITLE']['drawn']} title routes, honestly thin at "
                   f"{cover['TITLE']['total'] * 100:.1f}% of the board", gold_px > 400),
        ("wide or thin", f"the drawn field spans {lo:.0f}px at its narrowest column and "
                         f"{max(spread.values()):.0f}px at its widest ({ratio:.0f}x)", ratio >= 3.0),
        ("some paths leave", f"{rose_px:,} rose pixels and {edge_ink:,} lit pixels on the canvas edges",
         rose_px > 400 and edge_ink > 200),
    ]


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
    x0, x1 = int(col_x(0)) - 40, S_W
    y0, y1 = int(CY - S_H * 0.30), int(CY + S_H * 0.30)
    img.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * 1.45), int((y1 - y0) * 1.45)),
                                      Image.LANCZOS).save(out / "poster_zoom50.png")
    rows = two_second_test(fl, cover, picked, img)
    tv = title_verdict(fl)

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
         "two_second": [[a, b, ok] for a, b, ok in rows], "title_verdict": tv, "pert": pert}, indent=1))
    for K in ORDER:
        c = cover[K]
        print(f"  {K:6s} {c['drawn']:2d}/{c['budget']:2d} of {c['routes']:>6,} routes | outcome {c['total'] * 100:5.2f}% | "
              f"routes = {c['shown'] / c['total'] * 100:5.1f}% of it | drawn subgraph = {c['shown_sub'] / c['total'] * 100:5.1f}%")
    print(f"  {len(picked)} routes drawn (cap {HARD_CAP})")
    print(f"  TITLE VERDICT: {tv['text']}")
    for a, b, ok in rows:
        print(f"  TWO-SECOND {'PASS' if ok else 'FAIL'}  {a}: {b}")


if __name__ == "__main__":
    main()
