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
    ("radial_box_full.png", "Full field · box fork",
     "Every 2026-27 future as a trace. Time is radius: NOW at the rim, the 2028 GATE innermost, "
     "the title a gold terminal at dead center. Three corridors, bundled by LaMelo's availability "
     "read, spiral inward and unwind; the alive-at-gate futures crowd the gate circle (the hallway "
     "made literal, none entering); a few gold threads dive to the title."),
    ("radial_box_zoom50.png", "50% zoom · the gate and the title",
     "The center half, magnified: the crowded gate ring of committed futures, the delicate gold "
     "dives entering the title, and the exclusion around the gold that no other path crosses."),
    ("radial_box_scrubber_mid.png", "Season scrubber · frozen just past Jul 2027 (node 10)",
     "The collapse read radially: the now-circle has contracted inward to the present moment, the "
     "node-9 resets are greyed where they died, and the surviving futures stream on toward the gate. "
     "Proof that time reads as a contracting circle."),
    ("radial_rapm_full.png", "Full field · rapm fork (the grim read)",
     "The same board on the pessimistic metric fork: almost every future resets at the Jul-2027 "
     "boundary, so the field barely reaches the gate. The corridors thin to almost nothing."),
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
    html = f"""<title>Radial stills — ONE FOR ALL board</title>
<style>{TOKENS}</style>
<div class="wrap">
<h1>ONE FOR ALL &nbsp;/&nbsp; <b>Radial board</b> &nbsp;·&nbsp; composition stills</h1>
<p class="lede">Every future the board holds for 2026-27, drawn as one trace, on the real solver export.
Time is radius, the title is the gold center, and the eye follows the surviving corridor in.</p>
<p class="recipe">additive light · monochrome teal journeys, colored endings · dead drawn beneath ·
the gate hallway made literal · static stills, no interactivity yet</p>
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
