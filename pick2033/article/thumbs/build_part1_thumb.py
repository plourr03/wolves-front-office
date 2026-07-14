"""Part 1 thumbnail: the walk-year cliff, straight from edwards_hazard_FINAL.json.

Follows the LAFI article thumbnail pattern (lamelo/article/viz/season_distribution_thumb.html):
1280x720 static SVG on #050505, the piece's centerpiece chart, one big annotated
number, watermark. Rendered to PNG at 2x with a headless browser (see README note
in the emitted HTML header). No people depicted, so the silhouette rule is moot.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]

W, H = 1280, 720
X0, X1 = 110.0, 1180.0
YBASE, YTOP = 596.0, 150.0
YMAX = 0.65  # hazard-axis headroom above the .450 peak

GREEN = "#00843D"
GREEN_HI = "#00C457"
GRAY = "rgba(255,255,255,0.45)"
MONO = "JetBrains Mono, Consolas, monospace"
SANS = "Segoe UI, Inter, sans-serif"


def x(season):
    return X0 + (season - 2027) / 6.0 * (X1 - X0)


def y(hazard):
    return YBASE - hazard / YMAX * (YBASE - YTOP)


def main():
    data = json.loads((PROJECT / "outputs/json/edwards_hazard_FINAL.json").read_text())
    win = data["scenarios"]["central_win60"]["annual"]
    dec = data["scenarios"]["decline_win45"]["annual"]
    win_pts = [(a["season"], a["hazard_mean"]) for a in win]
    dec_pts = [(a["season"], a["hazard_mean"]) for a in dec]
    win_2029 = round(next(a["hazard_mean"] for a in win if a["season"] == 2029) * 100)
    dec_2029 = round(next(a["hazard_mean"] for a in dec if a["season"] == 2029) * 100)

    def poly(pts):
        return " ".join(f"{x(s):.1f},{y(h):.1f}" for s, h in pts)

    peak_x, peak_y = x(2029), y(next(h for s, h in win_pts if s == 2029))
    dec_peak_y = y(next(h for s, h in dec_pts if s == 2029))

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
        '  <radialGradient id="amb-white" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.05"/>'
        '<stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>\n'
        '</defs>\n'
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="#050505"/>\n'
        '<circle cx="980" cy="300" r="460" fill="url(#amb-green)"/>\n'
        '<circle cx="300" cy="450" r="380" fill="url(#amb-white)"/>\n'
    )

    # Axis.
    parts.append(f'<line x1="{X0-14}" y1="{YBASE}" x2="{X1+4}" y2="{YBASE}" stroke="rgba(255,255,255,0.14)" stroke-width="1"/>\n')
    for s in range(2027, 2034):
        hot = s == 2029
        fill = "rgba(255,255,255,0.75)" if hot else "rgba(255,255,255,0.34)"
        weight = ' font-weight="700"' if hot else ""
        parts.append(f'<line x1="{x(s):.1f}" y1="{YBASE}" x2="{x(s):.1f}" y2="{YBASE+7}" stroke="rgba(255,255,255,0.18)" stroke-width="1"/>\n')
        parts.append(f'<text x="{x(s):.1f}" y="{YBASE+26}" text-anchor="middle" fill="{fill}" font-family="{MONO}" font-size="12"{weight}>{s}</text>\n')

    # Declining scenario first (dimmer, underneath), then the winning scenario.
    parts.append(f'<polyline points="{poly(dec_pts)}" fill="none" stroke="{GRAY}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>\n')
    for s, h in dec_pts:
        parts.append(f'<circle cx="{x(s):.1f}" cy="{y(h):.1f}" r="3.5" fill="{GRAY}"/>\n')
    parts.append(f'<polyline points="{poly(win_pts)}" fill="none" stroke="{GREEN}" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>\n')
    for s, h in win_pts:
        parts.append(f'<circle cx="{x(s):.1f}" cy="{y(h):.1f}" r="4.5" fill="{GREEN}"/>\n')

    # Gray-peak label, LAFI zone-label grammar.
    parts.append(
        f'<text x="{peak_x:.1f}" y="{dec_peak_y-18:.1f}" text-anchor="middle" fill="rgba(255,255,255,0.55)" '
        f'font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="1.5">SAGS TO .450 &#183; {dec_2029}%</text>\n'
    )

    # Big number block, top right, elbow connector to the green peak.
    bx = 1030
    parts.append(
        f'<text x="{bx}" y="205" text-anchor="middle" fill="{GREEN_HI}" font-family="{MONO}" font-size="108" font-weight="700">{win_2029}%</text>\n'
        f'<text x="{bx}" y="237" text-anchor="middle" fill="rgba(255,255,255,0.78)" font-family="{SANS}" font-size="16" font-weight="600">his departure odds at the 2029 walk year</text>\n'
        f'<text x="{bx}" y="259" text-anchor="middle" fill="rgba(255,255,255,0.42)" font-family="{SANS}" font-size="13">on a Wolves team still winning at .600</text>\n'
        f'<path d="M {bx} 271 L {bx} {peak_y:.0f} L {peak_x+25:.0f} {peak_y:.0f}" fill="none" stroke="rgba(0,196,87,0.5)" stroke-width="1.5"/>\n'
        f'<path d="M {peak_x+27:.0f} {peak_y-6:.0f} L {peak_x+17:.0f} {peak_y:.0f} L {peak_x+27:.0f} {peak_y+6:.0f} Z" fill="rgba(0,196,87,0.7)"/>\n'
    )

    # Caption + watermark.
    parts.append(
        f'<text x="{(X0+X1)/2:.0f}" y="648" text-anchor="middle" fill="rgba(255,255,255,0.30)" font-family="{SANS}" font-size="13">Anthony Edwards, modeled annual departure odds, 2027 to 2033</text>\n'
        f'<text x="40" y="700" fill="rgba(255,255,255,0.30)" font-family="{SANS}" font-size="12">@WolvesToaT &#183; Jul 2026</text>\n'
        "</svg></body></html>\n"
    )

    out = HERE / "part1_tenure_bet_thumb.html"
    out.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {out}")
    print(f"labels: win {win_2029}% / decline {dec_2029}% at 2029")


if __name__ == "__main__":
    main()
