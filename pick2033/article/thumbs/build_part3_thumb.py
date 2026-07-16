"""Part 3 thumbnail: the bill in title equity, both perspectives, straight
from total_asset_cost.json (top1_true, picks_swaps_total).

Same pattern as the Part 1/2 generators: 1280x720 LAFI-style static SVG, two
80% interval strips (Charlotte in brand green, Minnesota in quiet white),
median tick + mean dot, and the asymmetry as the money annotation.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]

W, H = 1280, 720
X0, X1 = 300.0, 1180.0  # strip area (labels live left of X0)
LO, HI = -2.0, 25.0     # equity axis, percentage points

GREEN = "#00843D"
GREEN_HI = "#00C457"
MONO = "JetBrains Mono, Consolas, monospace"
SANS = "Segoe UI, Inter, sans-serif"


def main():
    data = json.loads((PROJECT / "outputs/json/total_asset_cost.json").read_text())
    tot = data["runs"]["top1_true"]
    cha = tot["delivered_to_CHA"]["picks_swaps_total"]
    mn = tot["forgone_by_MIN"]["picks_swaps_total"]
    ratio = cha["mean"] / mn["mean"]
    ratio_label = f"{ratio:.1f}x"  # 1.8x, as printed in the article

    def x(v):
        return X0 + (v - LO) / (HI - LO) * (X1 - X0)

    rows = [
        ("DELIVERED TO CHARLOTTE", cha, GREEN, "rgba(0,132,61,0.35)", GREEN_HI),
        ("FORGONE BY MINNESOTA", mn, "#FFFFFF", "rgba(255,255,255,0.16)", "#FFFFFF"),
    ]
    row_y = [330, 470]

    parts = []
    parts.append(
        f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;'
        f'background:#050505;width:{W}px;height:{H}px;overflow:hidden}}</style></head><body>\n'
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n'
        '<defs><radialGradient id="amb-green" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{GREEN}" stop-opacity="0.14"/>'
        f'<stop offset="60%" stop-color="{GREEN}" stop-opacity="0.05"/>'
        f'<stop offset="100%" stop-color="{GREEN}" stop-opacity="0"/></radialGradient></defs>\n'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#050505"/>\n'
        '<circle cx="900" cy="300" r="480" fill="url(#amb-green)"/>\n'
    )

    # Zero line + axis ticks.
    parts.append(
        f'<line x1="{x(0):.1f}" y1="250" x2="{x(0):.1f}" y2="560" stroke="rgba(255,255,255,0.16)" '
        'stroke-width="1.5" stroke-dasharray="3,5"/>\n'
        f'<text x="{x(0):.1f}" y="240" text-anchor="middle" fill="rgba(255,255,255,0.34)" '
        f'font-family="{MONO}" font-size="12">0</text>\n'
    )
    for v in (10, 20):
        parts.append(
            f'<text x="{x(v):.1f}" y="240" text-anchor="middle" fill="rgba(255,255,255,0.34)" '
            f'font-family="{MONO}" font-size="12">+{v}</text>\n'
        )

    for (label, d, dot_fill, strip_fill, num_fill), y in zip(rows, row_y):
        parts.append(
            f'<text x="{X0 - 24}" y="{y - 12}" text-anchor="end" fill="rgba(255,255,255,0.85)" '
            f'font-family="{MONO}" font-size="15" font-weight="700" letter-spacing="1.5">{label.split(" ", 2)[0]} {label.split(" ", 2)[1]}</text>\n'
            f'<text x="{X0 - 24}" y="{y + 10}" text-anchor="end" fill="rgba(255,255,255,0.85)" '
            f'font-family="{MONO}" font-size="15" font-weight="700" letter-spacing="1.5">{label.split(" ", 2)[2]}</text>\n'
        )
        x0s, x1s = x(d["q10"]), x(d["q90"])
        parts.append(
            f'<rect x="{x0s:.1f}" y="{y - 12}" width="{x1s - x0s:.1f}" height="24" rx="12" fill="{strip_fill}"/>\n'
            f'<line x1="{x(d["q50"]):.1f}" y1="{y - 17}" x2="{x(d["q50"]):.1f}" y2="{y + 17}" '
            'stroke="rgba(255,255,255,0.75)" stroke-width="2"/>\n'
            f'<circle cx="{x(d["mean"]):.1f}" cy="{y}" r="9" fill="{dot_fill}"/>\n'
            f'<text x="{x1s + 16:.1f}" y="{y + 6}" fill="{num_fill}" font-family="{MONO}" '
            f'font-size="24" font-weight="700">{d["mean"]:.1f}</text>\n'
        )

    # The money annotation: the asymmetry.
    parts.append(
        f'<text x="640" y="130" text-anchor="middle" fill="{GREEN_HI}" font-family="{MONO}" '
        f'font-size="96" font-weight="700">{ratio_label}</text>\n'
        '<text x="640" y="164" text-anchor="middle" fill="rgba(255,255,255,0.78)" '
        f'font-family="{SANS}" font-size="16" font-weight="600">same picks, nearly twice the title weight</text>\n'
        '<text x="640" y="186" text-anchor="middle" fill="rgba(255,255,255,0.42)" '
        f'font-family="{SANS}" font-size="13">cumulative title equity, percentage points &#183; 50,000 futures</text>\n'
    )

    # Caption + watermark.
    parts.append(
        '<text x="640" y="640" text-anchor="middle" fill="rgba(255,255,255,0.30)" '
        f'font-family="{SANS}" font-size="13">the picks-and-swaps bill, priced from both sides of the same futures &#183; strip: 80% of futures, tick: median, dot: mean</text>\n'
        '<text x="40" y="700" fill="rgba(255,255,255,0.30)" font-family="Segoe UI, Inter, sans-serif" '
        'font-size="12">@WolvesToaT &#183; Jul 2026</text>\n'
        "</svg></body></html>\n"
    )

    out = HERE / "part3_the_bill_thumb.html"
    out.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {out}")
    print(f"CHA mean {cha['mean']:.2f} [{cha['q10']:.2f}, {cha['q90']:.2f}] / MIN {mn['mean']:.2f} [{mn['q10']:.2f}, {mn['q90']:.2f}] / ratio {ratio_label}")


if __name__ == "__main__":
    main()
