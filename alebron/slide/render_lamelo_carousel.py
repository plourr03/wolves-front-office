#!/usr/bin/env python3
"""
Wolves to a T -- LaMelo trade analytical CAROUSEL (4 x 1080x1350).
Rendered at 2x and downscaled (LANCZOS) so every curve, line and edge is
anti-aliased, no jaggies. Restraint, not ornament: variety is structural (each
slide a different layout), not decorative. Green == the upside only, kept to the
small CLICKS tail so it stays the smallest, brightest thing in the set.
  1 THE BET        the distribution as a full-height hero (one graceful bell, small green tail)
  2 THE BULL CASE  the two upside levers, side by side
  3 WHAT DECIDES   a risk ledger, direction shown at a glance
  4 THE VERDICT    the editorial close + what to watch + sources

    python render_lamelo_carousel.py        # writes carousel/slide_1.png ... slide_4.png
"""
import os
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

W, H, MX = 1080, 1350, 80
CW = W - 2 * MX
S = 2                                    # supersample factor
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "carousel")
HIST_PATH = os.path.join(HERE, "..", "data", "sim", "season_hist.json")

P = {
    "bg_top": (5, 18, 35), "bg_bot": (11, 30, 53),
    "accent": (132, 214, 104), "accent_d": (96, 178, 92), "accent_dim": (74, 120, 86),
    "white": (240, 245, 251), "slate": (150, 168, 190), "mute": (101, 121, 145),
    "tile": (16, 33, 54), "tile_d": (12, 26, 44), "hair": (38, 60, 86),
    "wash": (104, 131, 165), "worse": (72, 97, 129), "clicks": (132, 214, 104),  # likelihood bars
    "track": (22, 37, 56), "grid": (33, 52, 75),
}
FD = "C:/Windows/Fonts/"
def _f(fn, s, var=None):
    try:
        f = ImageFont.truetype(FD + fn, int(s * S))
        if var:
            try: f.set_variation_by_name(var)
            except Exception: pass
        return f
    except OSError:
        return ImageFont.load_default()
COND = lambda s: _f("bahnschrift.ttf", s, "Bold")   # condensed display (headlines, bar labels)
HEAVY = lambda s: _f("FRAHV.TTF", s)                # Franklin Gothic Heavy (reserve for big impact)
SB = lambda s: _f("seguisb.ttf", s)                 # Segoe UI Semibold (labels, tags)
SR = lambda s: _f("segoeui.ttf", s)                 # Segoe UI (body)
MONO = lambda s: _f("consolab.ttf", s)              # Consolas Bold (numerals)
MARKER = lambda s: _f("Inkfree.ttf", s)             # Ink Free, the analyst's green marker scrawl


class SDraw:
    """Scales logical coordinates to the 2x surface; fonts are already 2x. self.oy is a
    logical y-offset added to every draw, used to vertically center a slide body between
    the fixed masthead and footer (set after masthead, reset to 0 before footer)."""
    def __init__(self, d): self.d = d; self.oy = 0
    def line(self, xy, fill, width=1):
        self.d.line([(p[0] * S, (p[1] + self.oy) * S) for p in xy], fill=fill, width=max(1, round(width * S)))
    def rectangle(self, box, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        self.d.rectangle([x0 * S, (y0 + self.oy) * S, x1 * S, (y1 + self.oy) * S], fill=fill, outline=outline, width=max(1, round(width * S)))
    def polygon(self, pts, fill=None, outline=None):
        self.d.polygon([(p[0] * S, (p[1] + self.oy) * S) for p in pts], fill=fill, outline=outline)
    def text(self, xy, text, font, fill, anchor=None):
        self.d.text((xy[0] * S, (xy[1] + self.oy) * S), text, font=font, fill=fill, anchor=anchor)
    def textlength(self, text, font):
        return self.d.textlength(text, font=font) / S


def bg_array():
    HS, WS = H * S, W * S
    g = np.zeros((HS, WS, 3))
    for y in range(HS):                                          # base midnight gradient
        g[y, :] = [P["bg_top"][c] + (P["bg_bot"][c] - P["bg_top"][c]) * (y / (HS - 1)) for c in range(3)]
    yy, xx = np.mgrid[0:HS, 0:WS]                                # aurora glow, green-teal, upper-right
    glow = np.exp(-(((xx - WS * 0.74) ** 2) / (WS * 0.36) ** 2 + ((yy - HS * 0.10) ** 2) / (HS * 0.33) ** 2))
    for c, gc in enumerate((28, 68, 46)):
        g[:, :, c] += glow * gc
    g += np.random.default_rng(7).normal(0, 4.0, (HS, WS, 1))    # faint grain
    return g


def bg():
    img = Image.fromarray(np.clip(bg_array(), 0, 255).astype(np.uint8), "RGB")
    return img, SDraw(ImageDraw.Draw(img))


def ls(d, x, y, s, fnt, fill, sp=0, anc="la"):
    if sp == 0:
        d.text((x, y), s, fnt, fill, anchor=anc); return
    tot = d.textlength(s, fnt) + sp * (len(s) - 1)
    if anc[0] == "m": x -= tot / 2
    elif anc[0] == "r": x -= tot
    for ch in s:
        d.text((x, y), ch, fnt, fill, anchor="l" + anc[1]); x += d.textlength(ch, fnt) + sp


def wrap(d, text, fnt, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, fnt) <= maxw: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out


def caret_down(d, cx, cy, s, col):
    d.polygon([(cx - s, cy - s * 0.7), (cx + s, cy - s * 0.7), (cx, cy + s * 0.85)], fill=col)


def hand_arrow(d, pts, col, w=3):                   # a slightly-bent, hand-drawn marker arrow
    for i in range(1, len(pts)):
        d.line([pts[i - 1], pts[i]], fill=col, width=w)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ang = float(np.arctan2(y2 - y1, x2 - x1)); L = 24
    for da in (2.62, -2.62):
        d.line([(x2, y2), (x2 + L * np.cos(ang + da), y2 + L * np.sin(ang + da))], fill=col, width=w)


def hand_ellipse(d, cx, cy, rx, ry, col, w=3):      # a loose, wobbly, over-shot hand circle
    n, a0, span = 76, -2.15, 2 * np.pi * 1.10        # 10% overshoot so the pen crosses its start
    pts = []
    for k in range(n):
        a = a0 + span * k / (n - 1)
        wob = 1 + 0.045 * np.sin(3 * a + 0.7) + 0.022 * np.sin(6 * a + 2.1)
        pts.append((cx + rx * wob * np.cos(a), cy + ry * wob * np.sin(a)))
    for i in range(1, len(pts)):
        d.line([pts[i - 1], pts[i]], fill=col, width=w)


def masthead(d):
    for x in range(W):
        t = x / (W - 1)
        d.line([(x, 0), (x, 7)], fill=tuple(int(P["accent_d"][k] + (P["accent"][k] - P["accent_d"][k]) * t) for k in range(3)))
    ls(d, MX, 50, "WOLVES TO A T", SB(23), P["white"], sp=7)
    ls(d, W - MX, 52, "THE LAMELO TRADE  ·  06.29.26", SB(19), P["accent"], sp=2, anc="ra")


def footer(d, swipe=None, sources=None):
    fl = H - 86
    d.line([(MX, fl), (W - MX, fl)], fill=P["hair"], width=2)
    ls(d, MX, fl + 20, "WOLVES TO A T", SB(20), P["white"], sp=4)
    ls(d, MX, fl + 48, "CHAMPIONSHIP MODEL + FIT DECOMPOSITION", SR(16), P["accent"], sp=2)
    if swipe:
        ls(d, W - MX, fl + 32, swipe, SB(18), P["accent"], sp=2, anc="ra")
    if sources:
        for i, s in enumerate(sources):
            d.text((W - MX, fl + 22 + i * 26), s, SR(16), P["mute"], anchor="ra")


# ---------------- slide 1: the cover ----------------
C_POP = (150, 230, 112)     # the dream-tail green, for text + labels


def slide1():
    """The real 20,000-season histogram, rendered as true bars (lumpy = real), with an
    analyst's hand-circled note on the long-shot green tail. Bars/heights come straight
    from lamelo/data/sim/season_hist.json (the same engine the title number uses)."""
    hist = json.loads(open(HIST_PATH, encoding="utf-8").read())
    counts = np.array(hist["counts"], float)
    edges = np.array(hist["bin_edges"], float)
    nb = len(counts)
    e0, eN = edges[0], edges[-1]
    dream_x, worse_x = hist["dream_x"], hist["worse_x"]
    x0, x1 = MX, W - MX
    yB, HP = 902, 470
    maxc = counts.max()
    netx = lambda v: x0 + (v - e0) / (eN - e0) * (x1 - x0)                # net -> logical x
    centers = (edges[:-1] + edges[1:]) / 2
    is_green = centers >= dream_x                                         # the dream tail (area = reach-CF)

    HS, WS = H * S, W * S
    g = bg_array()
    blue_bot, blue_top = np.array([24, 36, 60]), np.array([58, 82, 120])      # depth gradient
    green_bot, green_top = np.array([46, 104, 60]), np.array([176, 244, 138])
    gap = 2.0
    bars = []                                                            # (xL, xR, top, green) logical
    for i in range(nb):
        fL, fR = x0 + i / nb * (x1 - x0), x0 + (i + 1) / nb * (x1 - x0)
        h = counts[i] / maxc * HP
        bars.append((fL, fR, yB - h, bool(is_green[i])))
        if h < 0.5:
            continue
        bxL, bxR = int(round((fL + gap) * S)), int(round((fR - gap) * S))
        bt, bb = int(round((yB - h) * S)), int(round(yB * S))
        if bxR <= bxL or bb <= bt:
            continue
        rows = np.arange(bt, bb)
        t = ((bb - rows) / (bb - bt))[:, None]                           # 0 at base -> 1 at the lit top
        cb, ct = (green_bot, green_top) if is_green[i] else (blue_bot, blue_top)
        for c in range(3):
            g[bt:bb, bxL:bxR, c] = cb[c] + (ct[c] - cb[c]) * t
    # green glow: the dream tail emits light into the cold picture
    gcx, gcy = netx(9.6) * S, (yB - 0.18 * HP) * S
    glow = np.exp(-(((np.arange(WS) - gcx) ** 2) / (WS * 0.090) ** 2)[None, :]
                  - (((np.arange(HS) - gcy) ** 2) / (HS * 0.060) ** 2)[:, None])
    glow *= (np.arange(HS)[:, None] <= yB * S)
    for c, gc in enumerate((30, 78, 46)):
        g[:, :, c] += glow * gc
    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGB")
    d = SDraw(ImageDraw.Draw(img))

    masthead(d)                                                         # green bar + WOLVES TO A T / date row, like the rest

    d.line([(x0, yB), (x1, yB)], fill=P["hair"], width=2)                # baseline
    for fL, fR, top, grn in bars:                                        # lit top edge per bar
        if yB - top < 0.5:
            continue
        d.line([(fL + gap, top), (fR - gap, top)], fill=((206, 250, 168) if grn else (96, 124, 160)), width=2)
    wx = netx(worse_x)                                                   # worse | wash divider (subtle)
    d.line([(wx, yB - 0.36 * HP), (wx, yB)], fill=(60, 84, 112), width=1)
    dx = netx(dream_x)                                                   # "dream starts here" landmark
    d.line([(dx, yB - 0.30 * HP), (dx, yB)], fill=(96, 150, 110), width=1)

    hf = COND(84); x = MX - 2                                            # title (held)
    for seg, c in [("THE LAMELO ", P["white"]), ("BET", C_POP)]:
        d.text((x, 144), seg, hf, c); x += d.textlength(seg, hf)
    d.text((MX, 252), "Three ways it can go. The good one is the least likely.", SR(26), P["slate"])
    d.text((MX, 288), "Each bar is how often that result came up across 20,000 simulated", SR(19), P["mute"])
    d.text((MX, 316), "seasons, weighing fit, health, and the rest of the West.", SR(19), P["mute"])
    d.text(((x0 + wx) / 2, yB + 16), "IT GETS WORSE", COND(31), P["mute"], anchor="ma")
    d.text(((wx + dx) / 2, yB + 16), "A WASH", COND(31), P["mute"], anchor="ma")
    d.text(((dx + x1) / 2, yB + 16), "THE DREAM", COND(31), C_POP, anchor="ma")
    # analyst margin note, hand-circling the real long-shot green tail
    ell_cx, ell_cy = netx(13.4), 812
    hand_ellipse(d, ell_cx, ell_cy, 152, 96, C_POP, w=3)
    d.text((netx(7.2), 470), "the whole gamble,", MARKER(46), C_POP)
    d.text((netx(7.2), 516), "right here.", MARKER(46), C_POP)
    hand_arrow(d, [(netx(11.4), 568), (netx(12.6), 640), (netx(13.0), 706)], C_POP, w=3)

    d.text((MX, 972),                                                  # footnote: name what the axis measures
           "The full range of simulated season outcomes, worse to no real change to the leap, "
           "by how often the model landed there.", SR(17), P["mute"])
    d.text((MX - 2, 1022), "They bet the whole future", COND(56), P["white"])     # punchline (held)
    x = MX - 2
    for seg, c in [("on the ", P["white"]), ("little green bars", C_POP), (".", P["white"])]:
        d.text((x, 1088), seg, COND(56), c); x += d.textlength(seg, COND(56))
    footer(d, swipe="THE DREAM  →")
    return img


# ---------------- slide 2: the bull case, side by side ----------------
def point(d, y, big, support, tick, sz=44):
    d.rectangle([MX, y + 8, MX + 7, y + sz + 4], fill=tick)
    d.text((MX + 26, y - 4), big, COND(sz), P["white"])
    d.text((MX + 26, y + sz + 10), support, SR(22), P["slate"])


def slide2(d):
    masthead(d)                                          # header pinned at top; body spaced to fill
    hf = COND(54); x = MX - 2
    for seg, c in [("FIRST, THE ", P["white"]), ("DREAM", P["accent"]), (".", P["white"])]:
        d.text((x, 150), seg, hf, c); x += d.textlength(seg, hf)
    d.text((MX, 220), "Ant is one of the deadliest catch-and-shoot shooters alive.", SR(25), P["slate"])

    # BEAT 1 (hero): Ant's shot diet. WIDTH = how often, the % = how well he shoots it
    d.text((MX, 280), "Width = how often he takes it.   The % = how well he shoots it.", SR(21), P["mute"])
    x0, x1 = MX, W - MX
    by, bh = 352, 190
    split = x0 + 0.277 * (x1 - x0)
    GREEN, GHI, GRAY = (150, 230, 112), (198, 250, 156), (70, 92, 122)
    d.rectangle([x0, by, split, by + bh], fill=GREEN)
    d.rectangle([x0, by, split, by + 5], fill=GHI)                  # lit cap = glow
    d.rectangle([split, by, x1, by + bh], fill=GRAY)
    gcx, grx = (x0 + split) / 2, (split + x1) / 2
    ls(d, gcx, by - 34, "WIDE OPEN", SB(20), GREEN, sp=2, anc="ma")
    d.text((gcx, by + bh / 2 - 20), "49.6%", MONO(42), (8, 22, 38), anchor="mm")
    ls(d, gcx, by + bh / 2 + 26, "FROM THREE", SB(16), (12, 36, 22), sp=2, anc="ma")
    d.text((gcx, by + bh + 16), "just 27% of his shots", SR(20), P["slate"], anchor="ma")
    ls(d, grx, by - 34, "CONTESTED  ·  OFF THE DRIBBLE", SB(20), P["slate"], sp=2, anc="ma")
    d.text((grx, by + bh / 2 - 20), "35.3%", MONO(42), P["white"], anchor="mm")
    ls(d, grx, by + bh / 2 + 26, "FROM THREE", SB(16), P["slate"], sp=2, anc="ma")
    d.text((grx, by + bh + 16), "the other 73%", SR(20), P["slate"], anchor="ma")

    bf = COND(52); x = MX - 2                                             # the looks become available (true)
    for seg, c in [("LaMelo ", P["white"]), ("hands him those looks.", P["accent"])]:
        d.text((x, 612), seg, bf, c); x += d.textlength(seg, bf)
    # the honest turn (the slide's real insight): the share does NOT automatically move
    d.text((MX, 684), "But historical comps say it barely moves. Scorers who got a lead", SR(23), P["slate"])
    d.text((MX, 716), "creator mostly kept hunting their own shot. The looks will be there.", SR(23), P["slate"])
    cf = COND(42); x = MX - 2                                             # the payoff: the choice is his
    for seg, c in [("IT'S ON ", P["white"]), ("ANT", P["accent"]), (" TO TAKE THEM!", P["white"])]:
        d.text((x, 766), seg, cf, c); x += d.textlength(seg, cf)

    # secondary beat: it's not just Ant, Gobert's roll VOLUME could climb too (finish already elite + flat)
    d.line([(MX, 858), (W - MX, 858)], fill=P["hair"], width=1)
    ls(d, MX, 882, "IT'S NOT JUST ANT", SB(18), P["mute"], sp=3)
    d.text((MX, 914), "Gobert's pick-and-rolls per game could climb with LaMelo as the primary creator.", SR(22), P["slate"])
    SAGE = (120, 170, 128)
    bx0 = MX + 132
    bmax = (W - MX - 64) - bx0
    rowy = 974
    for label, val, vlab in [("NOW", 1.5, "1.5"), ("HIS PEAK", 3.5, "3.5")]:
        ls(d, MX, rowy - 9, label, SB(16), P["slate"], sp=1)
        wpx = val / 3.5 * bmax
        d.rectangle([bx0, rowy - 13, bx0 + wpx, rowy + 13], fill=SAGE)
        d.text((bx0 + wpx + 12, rowy), vlab, MONO(20), P["white"], anchor="lm")
        rowy += 48
    d.text((MX, rowy + 10), "Same elite finish, just more volume, and that's mostly LaMelo's creation.", SR(21), P["mute"])
    footer(d, swipe="THE NIGHTMARE  →")


# ---------------- slide 3: the risk ledger ----------------
def slide3(d):
    masthead(d)                                          # header pinned at top; sections spaced to fill
    d.text((MX - 2, 150), "BUT CAN YOU TRUST IT?", COND(54), P["white"])
    d.text((MX, 216), "Three reasons the dream probably doesn't happen.", SR(25), P["slate"])

    # 1. health -- the games-played sawtooth (his real availability, the shape tells the story)
    d.text((MX, 320), "He's never healthy.", COND(38), P["white"])
    gp = [51, 75, 36, 22, 47, 72]; yrs = ["'21", "'22", "'23", "'24", "'25", "'26"]
    gw, ggap, gbase = 116, 26, 614
    gx0 = MX + (CW - (6 * gw + 5 * ggap)) / 2
    for i, (v, yr) in enumerate(zip(gp, yrs)):
        bx = gx0 + i * (gw + ggap)
        h = int(v / 82 * 168)
        col = P["worse"] if v < 45 else P["wash"]
        d.rectangle([bx, gbase - h, bx + gw, gbase], fill=col)
        d.text((bx + gw / 2, gbase - h - 30), str(v), MONO(24), P["white"], anchor="ma")
        d.text((bx + gw / 2, gbase + 8), yr, SR(17), P["mute"], anchor="ma")
    d.text((MX, gbase + 46), "Games per year. Two seasons cratered. He's a coin flip to even play.", SR(23), P["slate"])

    # 2. defense -- percentile bar, LaMelo down at the bad end
    dy = 790
    d.text((MX, dy), "He can't guard anybody.", COND(38), P["white"])
    by = dy + 64
    d.rectangle([MX, by, W - MX, by + 18], fill=P["track"])
    d.rectangle([MX, by, MX + 0.30 * CW, by + 18], fill=P["worse"])
    mk = MX + 0.30 * CW
    d.rectangle([mk - 5, by - 12, mk + 5, by + 30], fill=P["white"])
    ls(d, MX, by + 34, "WORST DEFENDERS", SR(16), P["mute"], sp=1)
    ls(d, W - MX, by + 34, "BEST", SR(16), P["mute"], sp=1, anc="ra")
    d.text((MX, by + 66), "Bottom third against the pick-and-roll, and they hunt him more every year.", SR(22), P["slate"])

    # 3. depth -- the quiet development bet (respect the kid; the bet is the risk, not him)
    d.text((MX, 1050), "A big bet on Beringer.", COND(38), P["white"])
    d.text((MX, 1100), "Reid and Randle are gone, so the frontcourt now leans on a 19-year-old taking a leap.", SR(22), P["slate"])
    d.text((MX, 1134), "It's a real bet, and with no picks and a hard cap, the only help left is the mid-level or a minimum.", SR(22), P["slate"])
    footer(d, swipe="TO BE FAIR  →")


# ---------------- slide 4: what the model doesn't capture (steelman + honest landing) ----------------
def slide_concede(d):
    masthead(d)
    d.text((MX - 2, 150), "OKAY, TO BE FAIR.", COND(54), P["white"])
    d.text((MX, 222), "The best of the other side, on the scale.", SR(26), P["slate"])
    for i, (big, support) in enumerate([
        ("They had to do something.", "The West is a gauntlet. Standing pat was its own gamble."),
        ("Ant wanted help.", "Keeping your franchise star happy is worth real money."),
        ("Charlotte gave him up.", "Teams don't sell high on a guy they truly believe in."),
        ("They're not done yet.", "A mid-level or minimum can still add a power forward, but cheap tools patch the hole, not fix it."),
    ]):
        y = 300 + i * 120
        d.rectangle([MX, y + 6, MX + 7, y + 40], fill=P["mute"])
        d.text((MX + 26, y - 2), big, COND(38), P["white"])
        d.text((MX + 26, y + 46), support, SR(21 if i == 3 else 22), P["slate"])
    # the verdict lands heavier than all three: finding -> fan's heart -> honest landing
    ty, bh = 786, 332
    d.rectangle([MX, ty, W - MX, ty + bh], fill=P["tile_d"], outline=P["hair"], width=2)
    d.rectangle([MX, ty, MX + 6, ty + bh], fill=P["accent"])
    ls(d, MX + 30, ty + 28, "AND YET", SB(19), P["accent"], sp=3)
    for i, ln in enumerate([                                  # the finding, credited to the model
        "The simulations say it's most likely a wash,",
        "and they bet the entire future to find out."]):
        d.text((MX + 30, ty + 68 + i * 34), ln, SR(24), P["white"])
    SRI = _f("segoeuii.ttf", 24)                              # the fan's heart, an italic aside
    d.text((MX + 30, ty + 162), "As a fan, you're praying this is the swing that finally gets them over the top.",
           SRI, P["slate"])
    d.text((MX + 30, ty + 252), "The model just can't promise it made them better.", COND(32), P["white"])
    footer(d, swipe="THE VERDICT  →")


# ---------------- slide 5: the verdict ----------------
def slide4(d):
    masthead(d)
    hf = COND(88); x = MX - 2
    for seg, c in [("THE CEILING'S ", P["white"]), ("REAL.", P["accent"])]:
        d.text((x, 196), seg, hf, c); x += d.textlength(seg, hf)
    d.text((MX - 2, 286), "THE ODDS AREN'T.", hf, P["white"])

    d.text((MX, 448), "Not a disaster.", COND(72), P["white"])
    d.text((MX, 536), "Not an upgrade.", COND(72), P["white"])
    bf = COND(72); x = MX - 2
    for seg, c in [("A ", P["white"]), ("bet", P["accent"]), (".", P["white"])]:
        d.text((x, 624), seg, bf, c); x += d.textlength(seg, bf)
    d.text((MX, 762), "They made it fun. They just didn't make it better.", SR(30), P["slate"])
    d.text((MX, 808), "This is what the math says, not what we wanted.", SR(24), P["mute"])
    # the gradeable early tells
    wy = 858
    d.line([(MX, wy), (W - MX, wy)], fill=P["hair"], width=1)
    ls(d, MX, wy + 22, "WHAT TO WATCH EARLY", SB(18), P["accent"], sp=3)
    for i, ln in enumerate([                                 # four sharp one-liners, mechanism-based
        "LaMelo's health. The first ankle absence is the tell, the model leans nearer 50 games than our 63.",
        "Gobert's pick-and-roll volume, watch it climb from ~1.5 toward 3 a game.",
        "Does Ant's open-look share actually climb, or does he keep hunting pull-ups?",
        "The defense when Gobert sits. If it holds, Beringer leaped. If it craters, the depth problem is real."]):
        yy = wy + 52 + i * 31
        d.rectangle([MX, yy + 7, MX + 6, yy + 13], fill=P["slate"])   # neutral bullet, one per line
        d.text((MX + 22, yy), ln, SR(21), P["slate"])
    # the close: honesty first, then the precise long shot worth rooting for (the fan's last word)
    d.text((MX, 1066), "The model says probably not. But if the looks open up and the ankle holds", SR(24), P["white"])
    d.text((MX, 1098), "and the kid leaps, that's the season that proves it wrong.", SR(24), P["white"])
    cf = _f("segoeuib.ttf", 26); x = MX                                  # caps + bold, same size
    for seg, c in [("THAT'S THE BET. AND THAT'S ", P["white"]), ("WORTH ROOTING FOR.", P["accent"])]:
        d.text((x, 1142), seg, cf, c); x += d.textlength(seg, cf)
    footer(d, sources=["Wolves to a T  ·  the analytical read on the LaMelo trade.",
                       "Not a forecast. Trade official July 6."])


def main():
    os.makedirs(OUT, exist_ok=True)
    for n, fn in enumerate([slide1, slide2, slide3, slide_concede, slide4], 1):
        if fn is slide1:
            img = slide1()
        else:
            img, d = bg(); fn(d)
        p = os.path.join(OUT, f"slide_{n}.png")
        img.resize((W, H), Image.LANCZOS).save(p); print("saved", p)


if __name__ == "__main__":
    main()
