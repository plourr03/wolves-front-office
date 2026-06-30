#!/usr/bin/env python3
"""
Wolves to a T -- LaMelo trade analytical companion slide (1080x1350).
Inherits the snapshot-slide visual language (midnight, one aurora accent, mono
numerals, squared tiles, grain, the catch strip) but draws a custom hero: the bet
as a distribution of three outcomes, with the probability weight HONESTLY skewed
toward the wash/fail side. Green == the upside only (so it is the smallest thing on
the slide). Every figure traces to the model; no fabricated probabilities.

    python render_lamelo_slide.py out.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

W, H = 1080, 1350
MX = 80
CW = W - 2 * MX

P = {
    "bg_top": (8, 19, 36), "bg_bot": (13, 33, 58),
    "accent": (132, 214, 104), "accent_d": (96, 178, 92), "accent_dim": (74, 120, 86),
    "white": (238, 244, 250), "slate": (140, 159, 180), "mute": (95, 116, 138),
    "tile": (15, 32, 53), "hair": (35, 58, 84), "fill_dim": (30, 50, 72),
}

FD = "C:/Windows/Fonts/"
def _f(fn, s):
    try: return ImageFont.truetype(FD + fn, s)
    except OSError: return ImageFont.load_default()
COND = lambda s: _f("arialnb.ttf", s)   # Arial Narrow Bold (condensed)
SB   = lambda s: _f("arialbd.ttf", s)   # Arial Bold
SR   = lambda s: _f("arial.ttf", s)     # Arial
MONO = lambda s: _f("consolab.ttf", s)  # Consolas Bold (mono numerals)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main(out="lamelo_slide.png"):
    # ---- background: gradient + aurora glow + grain (matches the feed) ----
    g = np.zeros((H, W, 3))
    for y in range(H):
        t = y / (H - 1)
        g[y, :] = [P["bg_top"][c] + (P["bg_bot"][c] - P["bg_top"][c]) * t for c in range(3)]
    yy, xx = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((xx - 880) ** 2) / 520 ** 2 + ((yy - 210) ** 2) / 430 ** 2))
    for c, gc in enumerate((30, 70, 48)):
        g[:, :, c] += glow * gc
    g += np.random.default_rng(7).normal(0, 5.0, (H, W, 1))
    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)

    def ls(x, y, s, fnt, fill, sp=0, anc="la"):
        if sp == 0:
            d.text((x, y), s, font=fnt, fill=fill, anchor=anc); return
        tot = d.textlength(s, font=fnt) + sp * (len(s) - 1)
        if anc[0] == "m": x -= tot / 2
        elif anc[0] == "r": x -= tot
        for ch in s:
            d.text((x, y), ch, font=fnt, fill=fill, anchor="l" + anc[1])
            x += d.textlength(ch, font=fnt) + sp

    # ---- masthead ----
    for x in range(W):
        d.line([(x, 0), (x, 7)], fill=lerp(P["accent_d"], P["accent"], x / (W - 1)))
    ls(MX, 52, "WOLVES TO A T", SB(24), P["white"], sp=7)
    ls(W - MX, 54, "THE LAMELO TRADE · ANALYSIS", MONO(22), P["accent"], sp=1, anc="ra")

    # ---- headline: "A SWING," / "NOT AN UPGRADE." (accent the bull word) ----
    hf = COND(118)
    x = MX - 2
    for seg, col in [("A ", P["white"]), ("SWING", P["accent"]), (",", P["white"])]:
        d.text((x, 100), seg, font=hf, fill=col); x += d.textlength(seg, font=hf)
    d.text((MX - 2, 200), "NOT AN UPGRADE.", font=hf, fill=P["white"])

    # ---- subhead ----
    d.text((MX, 322), "A real swing, for a ceiling the math", font=SR(30), fill=P["slate"])
    d.text((MX, 360), "does not expect them to hit.", font=SR(30), fill=P["slate"])

    # ---- HERO: distribution of three outcomes, honestly skewed ----
    x0, x1 = MX, W - MX
    yB, HP = 600, 150
    mode_u, sigL, sigR = 0.40, 0.30, 0.235
    d1u, d2u = 0.27, 0.55             # dividers: FAILS | WASH | CLICKS
    us = np.linspace(0, 1, x1 - x0)
    f = np.where(us < mode_u, np.exp(-((us - mode_u) / sigL) ** 2),
                 np.exp(-((us - mode_u) / sigR) ** 2))
    aF, aW, aC = f[us < d1u].sum(), f[(us >= d1u) & (us < d2u)].sum(), f[us >= d2u].sum()
    tot = aF + aW + aC
    print(f"REGION AREA (honesty check): FAILS {aF/tot*100:.0f}%  WASH {aW/tot*100:.0f}%  "
          f"CLICKS {aC/tot*100:.0f}%   |  wash+fail {(aF+aW)/tot*100:.0f}% vs click {aC/tot*100:.0f}%")

    # filled curve: green concentrates only in the right (clicks) tail
    for i, u in enumerate(us):
        gx = x0 + i
        top = yB - f[i] * HP
        gw = np.clip((u - 0.46) / 0.46, 0, 1) ** 1.4
        d.line([(gx, top), (gx, yB)], fill=lerp(P["fill_dim"], P["accent"], gw))
    # curve stroke (brighter, same semantic)
    pts = [(x0 + i, yB - f[i] * HP) for i in range(len(us))]
    for i in range(1, len(pts)):
        u = us[i]; gw = np.clip((u - 0.46) / 0.46, 0, 1) ** 1.4
        d.line([pts[i - 1], pts[i]], fill=lerp((120, 140, 162), P["accent"], gw), width=3)
    # baseline + dividers + axis ends
    d.line([(x0, yB), (x1, yB)], fill=P["hair"], width=2)
    for du in (d1u, d2u):
        dx = int(x0 + du * (x1 - x0))
        top = yB - (np.exp(-((du - mode_u) / sigL) ** 2) if du < mode_u
                    else np.exp(-((du - mode_u) / sigR) ** 2)) * HP
        d.line([(dx, top), (dx, yB)], fill=P["hair"], width=1)
    ls(x0, yB + 8, "WORSE", SR(17), P["mute"], sp=2)
    ls(x1, yB + 8, "THE LEAP", SR(17), P["mute"], sp=2, anc="ra")

    # region labels: FAILS (left-aligned), WASH (centered), CLICKS (right-aligned, accent)
    cF = x0 + d1u / 2 * (x1 - x0)
    cW = x0 + (d1u + d2u) / 2 * (x1 - x0)
    yL = yB + 40
    d.text((x0, yL), "IT FAILS", font=SB(26), fill=P["white"])
    ls(x0, yL + 33, "A REAL TAIL", SB(15), P["mute"], sp=2)
    d.text((x0, yL + 56), "hunted, hurt, no depth", font=SR(20), fill=P["slate"])
    d.text((cW, yL), "A WASH", font=SB(26), fill=P["white"], anchor="ma")
    ls(cW, yL + 33, "THE LIKELY MIDDLE", SB(15), P["mute"], sp=2, anc="ma")
    d.text((cW, yL + 56), "strength ~ unchanged", font=SR(20), fill=P["slate"], anchor="ma")
    d.text((x1, yL), "IT CLICKS", font=SB(26), fill=P["accent"], anchor="ra")
    ls(x1, yL + 33, "THE SMALLER TAIL", SB(15), P["accent_dim"], sp=2, anc="ra")
    mstr = "+3.5 to +7.7pp"
    d.text((x1, yL + 56), mstr, font=MONO(20), fill=P["accent"], anchor="ra")
    mw = d.textlength(mstr, font=MONO(20))
    d.text((x1 - mw - 8, yL + 56), "reach-CF", font=SR(20), fill=P["slate"], anchor="ra")

    # ---- two explanatory groups (the asymmetry, from the fit decomposition) ----
    def group(y, header, hcol, rows, marker):
        ls(MX, y, header, SB(20), hcol, sp=3)
        ry = y + 34
        for fig, fcol, label, detail in rows:
            d.rectangle([MX, ry + 5, MX + 6, ry + 21], fill=marker)
            d.text((MX + 22, ry), label, font=SB(22), fill=P["white"])
            dx = MX + 318
            if fig:
                d.text((dx, ry + 1), fig, font=MONO(21), fill=fcol)
                dx += d.textlength(fig, font=MONO(21)) + 8
            d.text((dx, ry + 1), detail, font=SR(21), fill=P["slate"])
            ry += 37
        return ry

    y = group(742, "WHAT COULD MAKE IT CLICK  ·  REAL, BUT NOT DECISIVE", P["accent"], [
        ("", None, "THE OFFENSE WORKS", "every comp two-guard duo ran a fine offense"),
        ("0.63", P["accent"], "EDWARDS OFF-BALL", "catch-shoot eFG, top-4 of 31 stars"),
    ], P["accent"])
    group(y + 24, "WHAT ACTUALLY DECIDES IT  ·  LEANS NEGATIVE OR UNKNOWN", P["slate"], [
        ("can't-tell", P["white"], "LAMELO'S PLAYOFF D", "a real risk; his playoff D sample is nil"),
        ("~50", P["white"], "AVAILABILITY", "games projected, under the 63 we predicted"),
        ("", None, "FRONTCOURT DEPTH", "a structural D drag even at full Gobert health"),
    ], P["mute"])

    # ---- the verdict (catch strip, two lines) ----
    cy = 1018
    d.rectangle([MX, cy, W - MX, cy + 96], fill=(14, 28, 47), outline=P["hair"], width=2)
    d.rectangle([MX, cy, MX + 6, cy + 96], fill=P["accent"])
    ls(MX + 28, cy + 16, "THE VERDICT", SB(20), P["accent"], sp=3)
    d.text((MX + 28, cy + 44), "The ceiling is real. The math says don't bet on it,", font=SR(22), fill=P["white"])
    d.text((MX + 28, cy + 70), "and they spent the whole future to find out.", font=SR(22), fill=P["white"])

    # ---- the third bet: the internal-development leg of the variance (added risk, NOT optimism) ----
    ny = 1136
    ls(MX, ny, "THE THIRD BET  ·  ADDED VARIANCE, NOT A SAFETY NET", SB(18), P["slate"], sp=2)
    d.text((MX, ny + 29), "Both bigs behind Gobert are gone; only the mid-level and minimums refill the hole.",
           font=SR(19), fill=P["mute"])
    d.text((MX, ny + 52), "So the depth rides on a 19-year-old: Beringer must hold the backup-five (need-to-have D).",
           font=SR(19), fill=P["mute"])
    d.text((MX, ny + 75), "Shannon's the lesser, wing bet. Another coin flip on the pile, not a safety net.",
           font=SR(19), fill=P["mute"])

    # ---- footer ----
    fl = H - 86
    d.line([(MX, fl), (W - MX, fl)], fill=P["hair"], width=2)
    ls(MX, fl + 20, "WOLVES TO A T", SB(22), P["white"], sp=4)
    ls(MX, fl + 48, "TIMBERWOLVES ANALYTICS", SR(17), P["accent"], sp=3)
    d.text((W - MX, fl + 20), "Scenario figures: Wolves to a T model.", font=SR(18), fill=P["mute"], anchor="ra")
    d.text((W - MX, fl + 46), "Analysis, not a forecast. Trade official July 6.", font=SR(18), fill=P["mute"], anchor="ra")

    img.save(out)
    print("saved", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "lamelo_slide.png")
