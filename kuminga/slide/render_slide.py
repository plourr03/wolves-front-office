#!/usr/bin/env python3
"""
Render a single Wolves to a T "snapshot" slide (1080x1350 portrait PNG).

Usage:
    python render_slide.py config.json out.png

The config is JSON. See references/design-system.md for the full field guide
and examples/ for worked configs. Every number in the config must trace to a
verified source; label projections with "est" or "~" and credit sources in
footer_right. This script only draws what it is given, it does not invent data.
"""
import json
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

W, H = 1080, 1350
MX = 80
CW = W - 2 * MX

# ---- default palette: one aurora accent + neutral on midnight ----
DEFAULTS = {
    "bg_top":   [8, 19, 36],
    "bg_bot":   [13, 33, 58],
    "accent":   [132, 214, 104],   # aurora green
    "accent_d": [96, 178, 92],
    "white":    [238, 244, 250],
    "slate":    [140, 159, 180],
    "mute":     [95, 116, 138],
    "tile":     [15, 32, 53],
    "hair":     [35, 58, 84],
    "brand":      "WOLVES TO A T",
    "brand_tag":  "TIMBERWOLVES ANALYTICS",
    "dateline":   "",
    "headline":   ["HEADLINE"],
    "accent_line": -1,             # which headline line gets the accent (-1 = last)
    "subhead":    [],
    "tiles":      [],              # exactly 4: {num, label, detail:[..]}
    "catch":      None,            # {label, text} or null
    "context":    None,           # {label, text} or null
    "footer_right": [],
}

# Font mapping for this machine. The skill bundle ships a Linux DejaVu path, which
# on Windows silently falls through to ImageFont.load_default() and renders a tiny
# bitmap font, i.e. a broken slide that still exits 0. These are the same faces the
# approved lamelo carousel uses, so the two renders share a voice.
FONT_DIR = "C:/Windows/Fonts/"
_MISSING = []


def _f(name, size, var=None):
    try:
        f = ImageFont.truetype(FONT_DIR + name, size)
        if var:
            try:
                f.set_variation_by_name(var)
            except Exception:
                pass
        return f
    except OSError:
        _MISSING.append(name)
        return ImageFont.load_default()


COND_B = lambda s: _f("bahnschrift.ttf", s, "Bold")   # condensed display
SANS_B = lambda s: _f("seguisb.ttf", s)               # Segoe UI Semibold
SANS   = lambda s: _f("segoeui.ttf", s)               # Segoe UI
MONO_B = lambda s: _f("consolab.ttf", s)              # Consolas Bold, the numerals


def _assert_fonts():
    for fn in ("bahnschrift.ttf", "seguisb.ttf", "segoeui.ttf", "consolab.ttf"):
        _f(fn, 20)
    if _MISSING:
        raise SystemExit(f"missing fonts, refusing to render a fallback-bitmap slide: "
                         f"{sorted(set(_MISSING))}")


def render(cfg, out_path):
    _assert_fonts()
    c = dict(DEFAULTS)
    c.update(cfg)
    col = lambda k: tuple(c[k])

    # ---- background: vertical gradient + faint aurora glow + grain ----
    grad = np.zeros((H, W, 3), dtype=np.float64)
    top, bot = c["bg_top"], c["bg_bot"]
    for y in range(H):
        t = y / (H - 1)
        for ch in range(3):
            grad[y, :, ch] = top[ch] + (bot[ch] - top[ch]) * t
    yy, xx = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((xx - 880) ** 2) / (520 ** 2) + ((yy - 210) ** 2) / (430 ** 2)))
    for ch, gc in enumerate((30, 70, 48)):
        grad[:, :, ch] += glow * gc
    grad += np.random.default_rng(7).normal(0, 5.0, (H, W, 1))
    img = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)

    def text_ls(x, y, s, fnt, fill, ls=0, anchor="la"):
        if ls == 0:
            d.text((x, y), s, font=fnt, fill=fill, anchor=anchor); return
        total = d.textlength(s, font=fnt) + ls * (len(s) - 1)
        if anchor[0] == "m": x -= total / 2
        elif anchor[0] == "r": x -= total
        cx = x
        for chx in s:
            d.text((cx, y), chx, font=fnt, fill=fill, anchor="l" + anchor[1])
            cx += d.textlength(chx, font=fnt) + ls

    # ---- masthead accent bar ----
    ad, ac = col("accent_d"), col("accent")
    for x in range(W):
        t = x / (W - 1)
        d.line([(x, 0), (x, 7)],
               fill=tuple(int(ad[k] + (ac[k] - ad[k]) * t) for k in range(3)))

    # ---- kicker row ----
    text_ls(MX, 60, c["brand"], SANS_B(25), col("white"), ls=7)
    if c["dateline"]:
        text_ls(W - MX, 62, c["dateline"], MONO_B(25), col("accent"), ls=1, anchor="ra")

    # ---- headline (condensed bold, accent on chosen line) ----
    hl = c["headline"]
    acc_idx = c["accent_line"] if c["accent_line"] >= 0 else len(hl) - 1
    hy = 150
    for i, line in enumerate(hl):
        d.text((MX - 4, hy), line, font=COND_B(140),
               fill=col("accent") if i == acc_idx else col("white"))
        hy += 136

    # ---- subhead ----
    sy = 452
    for line in c["subhead"]:
        d.text((MX, sy), line, font=SANS(31), fill=col("slate"))
        sy += 42

    # ---- 2x2 stat grid ----
    gx, gy, gap, th_ = MX, 558, 30, 218
    tw_ = (CW - gap) // 2
    for i, t in enumerate(c["tiles"][:4]):
        cx, ry = i % 2, i // 2
        x0 = gx + cx * (tw_ + gap)
        y0 = gy + ry * (th_ + gap)
        d.rectangle([x0, y0, x0 + tw_, y0 + th_], fill=col("tile"), outline=col("hair"), width=2)
        d.rectangle([x0, y0, x0 + 6, y0 + 52], fill=col("accent"))
        d.text((x0 + 30, y0 + 26), t["num"], font=MONO_B(74), fill=col("accent"))
        text_ls(x0 + 32, y0 + 124, t["label"], SANS_B(24), col("white"), ls=2)
        ly = y0 + 158
        for ln in t.get("detail", [])[:2]:
            d.text((x0 + 32, ly), ln, font=SANS(22), fill=col("slate"))
            ly += 29

    # ---- "the catch" editorial strip ----
    cy = gy + 2 * th_ + gap + 28
    if c["catch"]:
        d.rectangle([MX, cy, W - MX, cy + 84], fill=(14, 28, 47), outline=col("hair"), width=2)
        d.rectangle([MX, cy, MX + 6, cy + 84], fill=col("accent"))
        text_ls(MX + 30, cy + 17, c["catch"]["label"], SANS_B(21), col("accent"), ls=3)
        d.text((MX + 30, cy + 45), c["catch"]["text"], font=SANS(23), fill=col("white"))

    # ---- context line ----
    if c["context"]:
        ty = cy + 120
        text_ls(MX, ty, c["context"]["label"], SANS_B(21), col("slate"), ls=3)
        d.text((MX, ty + 30), c["context"]["text"], font=MONO_B(24), fill=col("white"))

    # ---- footer ----
    fline = H - 92
    d.line([(MX, fline), (W - MX, fline)], fill=col("hair"), width=2)
    text_ls(MX, fline + 22, c["brand"], SANS_B(23), col("white"), ls=4)
    if c["brand_tag"]:
        text_ls(MX, fline + 52, c["brand_tag"], SANS(18), col("accent"), ls=3)
    fr = c["footer_right"]
    for i, line in enumerate(fr[:2]):
        text_ls(W - MX, fline + 24 + i * 26, line, SANS(19), col("mute"), anchor="ra")

    img.save(out_path)
    return out_path


if __name__ == "__main__":
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "slide.png"
    with open(cfg_path) as fh:
        cfg = json.load(fh)
    print("saved", render(cfg, out_path))
