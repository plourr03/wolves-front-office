"""Static gallery for the radial stills (delivery only; no interactivity).

Base64-embeds the PNG stills into one content-only HTML page so Bobby can review the
composition in one place. House tokens, mono type, midnight ground. This is a viewer,
not the viz: the deliverable is the PNG stills; this just shows them.

Run:  python build_gallery.py
"""
from __future__ import annotations
import base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
STILLS = HERE / "stills"

SHOTS = [
    ("corridor_box_full.png", "Full field · straight · box fork",
     "THE CORRIDOR: left is NOW, right is the 2028 GATE, calendar columns are the verticals. Futures "
     "route as circuit traces on a lane grid, bending only at columns. The center lane is the road to "
     "the next ring; ring '27 sits in-line with a thin gold entry (only the 4.5% that win enter); the "
     "alive weave routes around it; the Ant-departs drain off the bottom as a rose fall; resets freeze "
     "as red rings in the failure shelf."),
    ("corridor_box_sheared.png", "Full field · sheared ~12° · box fork",
     "The same render with a ~12-degree isometric shear, for the straight-vs-sheared pick. The board "
     "reads as a circuit seen at an angle."),
    ("corridor_box_zoom50.png", "50% zoom · the crossover and both rings",
     "Magnified from ring '27 to the gate: the re-sort where '28-bound futures jog back into the "
     "center road, the rose fall of departures, and ring '28 crowded at the gate."),
    ("corridor_box_scrubber_r2.png", "Season scrubber · frozen at R2 (node 5)",
     "The collapse tool positioned at the January-2027 read: the weave up to R2, before the "
     "node-9 resets fire. Early season, the field still intact."),
]

TOKENS = """
:root{--midnight:#0A1120;--panel:#0E1626;--ink:#C9D4E3;--ink-dim:#6B7BA0;--gold:#F2C14E;--line:#1b2740;
  --mono:ui-monospace,'Cascadia Code','SF Mono',Menlo,Consolas,monospace}
*{box-sizing:border-box;margin:0}body{background:var(--midnight);color:var(--ink);font-family:var(--mono);
  padding:40px 20px 80px;line-height:1.5}
.wrap{max-width:1040px;margin:0 auto}
h1{font-size:15px;letter-spacing:.24em;text-transform:uppercase;font-weight:600;color:var(--ink)}
h1 b{color:var(--gold)}
.lede{color:var(--ink-dim);font-size:12.5px;margin:10px 0 4px;letter-spacing:.02em}
.recipe{color:var(--ink-dim);font-size:11.5px;margin:2px 0 34px;letter-spacing:.02em}
figure{margin:0 0 42px;border:1px solid var(--line);border-radius:5px;overflow:hidden;background:#060b16}
figure img{display:block;width:100%;height:auto}
figcaption{padding:14px 16px;border-top:1px solid var(--line)}
figcaption .t{font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink)}
figcaption .d{font-size:12px;color:var(--ink-dim);margin-top:6px;max-width:74ch}
.foot{color:var(--ink-dim);font-size:11px;margin-top:20px;letter-spacing:.02em}
"""


def data_uri(p):
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def main():
    figs = []
    for fn, title, desc in SHOTS:
        p = STILLS / fn
        if not p.exists():
            continue
        figs.append(f'<figure><img alt="{title}" src="{data_uri(p)}">'
                    f'<figcaption><div class="t">{title}</div><div class="d">{desc}</div></figcaption></figure>')
    html = f"""<title>Corridor stills — ONE FOR ALL board</title>
<style>{TOKENS}</style>
<div class="wrap">
<h1>ONE FOR ALL &nbsp;/&nbsp; <b>THE CORRIDOR</b> &nbsp;·&nbsp; composition stills</h1>
<p class="lede">Every future the board holds for 2026-27, drawn as one circuit trace on the real solver export.
Left to right is time; the center lane is the road to the next ring; the eye follows the corridor to the gate.</p>
<p class="recipe">GRAMMAR PREVIEW (v3) · additive light · circuit routing, bends only at columns · rings in-line ·
awaiting afo_frame.jpg for the weave-density and channel-glow match · static, no interactivity yet</p>
{''.join(figs)}
<p class="foot">Delivery: PNG stills at board/viz/stills/. Rendered from board_viz_export.json
(SOLVER, forks 0.5/0.5, cap 0.012, P(east) 0.60, 400 traces/fork). Nothing published beyond this
private review page.</p>
</div>"""
    out = HERE / "radial_gallery.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
