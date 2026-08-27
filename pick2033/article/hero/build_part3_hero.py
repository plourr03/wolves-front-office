"""Part 3 hero: the trade as an invoice, every instrument a line item.

Companion to the Part 1/2/3 thumbnail generators, but drawn with PIL rather
than SVG (the lamelo/slide renderer's path: supersample, real display fonts,
LANCZOS downscale) so it renders with one command and no headless browser.

2560x1440 final, drawn on a 1280x720 logical grid at 4x. Flat #050505 ground,
hairline rules, mono ledger, brand green reserved for the total only. No people
depicted, so the silhouette rule is moot. No glow or bloom by design.

Every number is read from the FINAL exports at run time:
  outputs/json/swap_pricing_FINAL.json   (top1_true_vorp: swaps, outright_2033)
  outputs/json/total_asset_cost.json     (line_items_vorp: resolved_2026, seconds)

    .venv/Scripts/python article/hero/build_part3_hero.py
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]

W, H = 1280, 720          # logical
S = 4                     # supersample
OUT_W, OUT_H = 2560, 1440 # final

BG = (5, 5, 5)
WHITE = (255, 255, 255)
DIM = (255, 255, 255, 108)
MUTE = (255, 255, 255, 78)
HAIR = (255, 255, 255, 40)
HAIR_HI = (255, 255, 255, 92)
GREEN = (0, 132, 61)
GREEN_HI = (0, 196, 87)

FD = "C:/Windows/Fonts/"


def _f(fn, size, var=None):
    f = ImageFont.truetype(FD + fn, int(size * S))
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


COND = lambda s: _f("bahnschrift.ttf", s, "Bold")   # condensed display
HEAVY = lambda s: _f("FRAHV.TTF", s)                # Franklin Gothic Heavy
SB = lambda s: _f("seguisb.ttf", s)                 # Segoe UI Semibold
SR = lambda s: _f("segoeui.ttf", s)                 # Segoe UI
MONO = lambda s: _f("consola.ttf", s)               # Consolas
MONOB = lambda s: _f("consolab.ttf", s)             # Consolas Bold


class SDraw:
    """Logical coordinates onto the supersampled surface. Fonts are already scaled."""

    def __init__(self, d):
        self.d = d

    def line(self, xy, fill, width=1):
        self.d.line([(p[0] * S, p[1] * S) for p in xy], fill=fill, width=max(1, round(width * S)))

    def text(self, xy, text, font, fill, anchor=None, spacing=0.0):
        if spacing:
            # Letterspacing is drawn glyph by glyph, so a right anchor has to be
            # resolved against the spaced width first, then drawn left to right.
            x, y = xy
            if anchor and anchor[0] == "r":
                x -= self.spaced_length(text, font, spacing)
            for ch in text:
                self.d.text((x * S, y * S), ch, font=font, fill=fill)
                x += self.textlength(ch, font) + spacing
            return
        self.d.text((xy[0] * S, xy[1] * S), text, font=font, fill=fill, anchor=anchor)

    def textlength(self, text, font):
        return self.d.textlength(text, font=font) / S

    def spaced_length(self, text, font, spacing):
        return sum(self.textlength(ch, font) for ch in text) + spacing * max(0, len(text) - 1)


def load_rows():
    sp = json.loads((PROJECT / "outputs/json/swap_pricing_FINAL.json").read_text())
    ta = json.loads((PROJECT / "outputs/json/total_asset_cost.json").read_text())
    run = sp["runs"]["top1_true_vorp"]
    li = ta["line_items_vorp"]

    rows = [
        ("2033 FIRST (UNPROTECTED)", run["outright_2033"]["mean"]),
        ("2028 SWAP", run["swaps"]["2028"]["mean"]),
        ("2029 SWAP", run["swaps"]["2029"]["mean"]),
        ("2030 SWAP", run["swaps"]["2030"]["mean"]),
        ("2026 DRAFT NIGHT (28 OUT, 33 IN)", li["resolved_2026"]["net_out_vorp"]),
        ("2029 / 2032 / 2033 SECONDS", li["seconds"]["total_vorp"]),
    ]
    total = run["total_per_path"]["mean"] + li["resolved_2026"]["net_out_vorp"] + li["seconds"]["total_vorp"]

    # The per-path total of the four simulated instruments must equal the sum of
    # their means (expectation is linear); the intervals are what never add.
    sim_sum = run["outright_2033"]["mean"] + sum(run["swaps"][y]["mean"] for y in ("2028", "2029", "2030"))
    assert abs(sim_sum - run["total_per_path"]["mean"]) < 1e-6, "simulated means do not reconcile"
    assert abs(round(sum(v for _, v in rows), 4) - round(total, 4)) < 1e-6, "line items do not reconcile"
    return rows, total, sp["meta"]["n_paths"]


def main():
    rows, total, n_paths = load_rows()

    rng = np.random.default_rng(20330708)
    grain = rng.normal(0, 2.6, (H * S, W * S, 1))
    base = np.clip(np.zeros((H * S, W * S, 3)) + np.array(BG) + grain, 0, 255).astype(np.uint8)
    img = Image.fromarray(base, "RGB").convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = SDraw(ImageDraw.Draw(layer))

    X0, X1 = 110, 1170

    # Masthead.
    g.text((X0, 86), "PRICING THE LAMELO TRADE   /   PART 3", MONO(14), DIM, spacing=1.6)
    g.text((X0, 112), "THE BILL", HEAVY(84), WHITE)
    g.text((X0, 214), "what Minnesota actually owes Charlotte, itemized", SR(20), (255, 255, 255, 132))

    # Ledger head.
    g.line([(X0, 258), (X1, 258)], HAIR_HI, 1)
    g.text((X0, 266), "INSTRUMENT", MONO(12), MUTE, spacing=1.4)
    g.text((X1, 266), "MEAN, 4-YR VORP", MONO(12), MUTE, anchor="ra", spacing=1.4)

    # Line items, with dot leaders.
    y = 306
    for label, value in rows:
        lab_f, num_f = MONO(19), MONOB(22)
        num = f"{value:.1f}"
        g.text((X0, y), label, lab_f, (255, 255, 255, 214))
        g.text((X1, y - 2), num, num_f, (255, 255, 255, 232), anchor="ra")
        lead_lo = X0 + g.textlength(label, lab_f) + 12
        lead_hi = X1 - g.textlength(num, num_f) - 14
        x = lead_lo
        while x < lead_hi:
            g.line([(x, y + 14), (x + 1.2, y + 14)], HAIR, 1)
            x += 7
        y += 40

    # Double rule, then the total.
    g.line([(X0, 556), (X1, 556)], HAIR_HI, 1)
    g.line([(X0, 561), (X1, 561)], HAIR_HI, 1)
    g.text((X0, 578), "TOTAL", COND(34), WHITE)
    wins_f, tot_f = COND(24), HEAVY(46)
    g.text((X1, 592), "WINS", wins_f, GREEN_HI, anchor="ra")
    g.text((X1 - g.textlength("WINS", wins_f) - 16, 572), f"{total:.1f}", tot_f, GREEN_HI, anchor="ra")

    # Footer.
    g.text(
        (X0, 646),
        f"mean four-year value above replacement delivered to Charlotte, across {n_paths:,} simulated futures",
        SR(15),
        (255, 255, 255, 96),
    )
    g.text((X0, 668), "means add; the intervals do not, and they are the whole story inside", SR(15), (255, 255, 255, 66))
    g.text((X1, 668), "@WolvesToaT  \u00b7  Jul 2026", SB(14), (255, 255, 255, 84), anchor="ra")

    out_img = Image.alpha_composite(img, layer).convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)
    out = HERE / "part3_the_bill_hero.png"
    out_img.save(out)
    print(f"wrote {out}  {out_img.size[0]}x{out_img.size[1]}")
    for label, value in rows:
        print(f"  {label:<34} {value:.4f} -> {value:.1f}")
    print(f"  {'TOTAL':<34} {total:.4f} -> {total:.1f}")


if __name__ == "__main__":
    main()
