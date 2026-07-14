"""Part 2 thumbnail: where the 2033 pick lands, straight from
slot_distribution_2033_FINAL.json.

Same pattern as build_part1_thumb.py (the LAFI-style 1280x720 static SVG):
the full 30-slot distribution as true bars, the 16-team lottery zone in brand
green with the playoff range in quiet white, and the money number annotated.
Render to PNG at 2x with headless Chrome (see the command in the repo log).
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]

W, H = 1280, 720
X0, X1 = 96.0, 1184.0
YBASE, YTOP = 596.0, 300.0

GREEN = "#00843D"
GREEN_HI = "#00C457"
MONO = "JetBrains Mono, Consolas, monospace"
SANS = "Segoe UI, Inter, sans-serif"


def main():
    data = json.loads((PROJECT / "outputs/json/slot_distribution_2033_FINAL.json").read_text())
    slots = data["slots"]
    p_lottery = data["p_lottery"]
    lot_label = f"{p_lottery * 100:.1f}"          # 61.9
    playoff_label = f"{100 - p_lottery * 100:.1f}"  # 38.1
    pmax = max(s["p"] for s in slots)

    slot_w = (X1 - X0) / 30
    bar_w = slot_w - 6

    def bx(i):  # left edge for slot index i (0-based)
        return X0 + i * slot_w + 3

    def bh(p):
        return p / pmax * (YBASE - YTOP)

    boundary_x = X0 + 16 * slot_w  # between slot 16 and 17

    parts = []
    parts.append(
        f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;'
        f'background:#050505;width:{W}px;height:{H}px;overflow:hidden}}</style></head><body>\n'
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n'
        '<defs>\n'
        '  <radialGradient id="amb-green" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{GREEN}" stop-opacity="0.14"/>'
        f'<stop offset="60%" stop-color="{GREEN}" stop-opacity="0.05"/>'
        f'<stop offset="100%" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>\n'
        '</defs>\n'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#050505"/>\n'
        '<circle cx="420" cy="330" r="460" fill="url(#amb-green)"/>\n'
    )

    # Bars: lottery slots green, playoff slots quiet white.
    for i, s in enumerate(slots):
        h = bh(s["p"])
        fill = GREEN if s["slot"] <= 16 else "#FFFFFF"
        op = "0.95" if s["slot"] <= 16 else "0.30"
        parts.append(
            f'<rect x="{bx(i):.1f}" y="{YBASE - h:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="2" '
            f'fill="{fill}" fill-opacity="{op}"/>\n'
        )

    # Zone divider + labels.
    parts.append(
        f'<line x1="{boundary_x:.1f}" y1="250" x2="{boundary_x:.1f}" y2="{YBASE}" '
        'stroke="rgba(255,255,255,0.16)" stroke-width="1.5" stroke-dasharray="3,5"/>\n'
        f'<text x="{X0 + 8 * slot_w:.0f}" y="242" text-anchor="middle" fill="{GREEN_HI}" '
        f'font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="1.5">'
        f'THE LOTTERY &#183; {lot_label}%</text>\n'
        f'<text x="{X0 + 23 * slot_w:.0f}" y="242" text-anchor="middle" fill="rgba(255,255,255,0.55)" '
        f'font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="1.5">'
        f'PLAYOFF RANGE &#183; {playoff_label}%</text>\n'
    )

    # Big number, top right, elbow down to the lottery zone.
    parts.append(
        f'<text x="1000" y="150" text-anchor="middle" fill="{GREEN_HI}" font-family="{MONO}" '
        f'font-size="96" font-weight="700">{lot_label}%</text>\n'
        '<text x="1000" y="182" text-anchor="middle" fill="rgba(255,255,255,0.78)" '
        f'font-family="{SANS}" font-size="16" font-weight="600">chance the pick is a lottery pick</text>\n'
        '<text x="1000" y="204" text-anchor="middle" fill="rgba(255,255,255,0.42)" '
        f'font-family="{SANS}" font-size="13">the 2033 first &#183; 16-team definition &#183; 50,000 futures</text>\n'
        f'<path d="M 1000 216 L 1000 330 L {boundary_x - 24:.0f} 330" fill="none" '
        'stroke="rgba(0,196,87,0.5)" stroke-width="1.5"/>\n'
        f'<path d="M {boundary_x - 22:.0f} 324 L {boundary_x - 32:.0f} 330 L {boundary_x - 22:.0f} 336 Z" '
        'fill="rgba(0,196,87,0.7)"/>\n'
    )

    # Axis ticks (slot numbers) + baseline + caption + watermark.
    parts.append(f'<line x1="{X0}" y1="{YBASE}" x2="{X1}" y2="{YBASE}" stroke="rgba(255,255,255,0.14)" stroke-width="1"/>\n')
    for slot in (1, 5, 10, 16, 20, 25, 30):
        cxx = bx(slot - 1) + bar_w / 2
        parts.append(
            f'<text x="{cxx:.0f}" y="622" text-anchor="middle" fill="rgba(255,255,255,0.34)" '
            f'font-family="{MONO}" font-size="12">{slot}</text>\n'
        )
    parts.append(
        f'<text x="{(X0 + X1) / 2:.0f}" y="648" text-anchor="middle" fill="rgba(255,255,255,0.30)" '
        f'font-family="{SANS}" font-size="13">where the 2033 first lands, across 50,000 simulated futures</text>\n'
        '<text x="40" y="700" fill="rgba(255,255,255,0.30)" font-family="Segoe UI, Inter, sans-serif" '
        'font-size="12">@WolvesToaT &#183; Jul 2026</text>\n'
        "</svg></body></html>\n"
    )

    out = HERE / "part2_fifty_thousand_thumb.html"
    out.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {out}")
    print(f"labels: lottery {lot_label}% / playoff {playoff_label}% / pmax {pmax:.4f}")


if __name__ == "__main__":
    main()
