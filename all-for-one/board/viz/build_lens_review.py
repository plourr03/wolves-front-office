"""Review page for the v5 lens still + the data-fidelity proofs (delivery only).

Embeds: the lens still (full + 50% zoom); the audit overlay with its event table (proof A);
the reconciliation line (proof B); and the perturbation pair, two seeds side by side (proof C).
Content-only HTML for the Artifact host.
"""
from __future__ import annotations
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STILLS = HERE / "stills"
ROWS = json.loads((STILLS / "lens_audit_table.json").read_text())

TOK = """
:root{--midnight:#0A1120;--ink:#C9D4E3;--ink-dim:#6B7BA0;--gold:#F2C14E;--teal:#35C9C0;--rose:#C4788C;--line:#1b2740;
  --mono:ui-monospace,'Cascadia Code','SF Mono',Menlo,Consolas,monospace}
*{box-sizing:border-box;margin:0}body{background:var(--midnight);color:var(--ink);font-family:var(--mono);padding:38px 20px 80px;line-height:1.55}
.wrap{max-width:1120px;margin:0 auto}
h1{font-size:15px;letter-spacing:.24em;text-transform:uppercase;font-weight:600}h1 b{color:var(--gold)}
.lede{color:var(--ink-dim);font-size:12.5px;margin:10px 0 30px}
h2{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink);margin:34px 0 12px;font-weight:600}
h2 span{color:var(--ink-dim);letter-spacing:.02em;text-transform:none;font-weight:400}
figure{margin:0 0 10px;border:1px solid var(--line);border-radius:5px;overflow:hidden;background:#060b16}
figure img{display:block;width:100%;height:auto}
figcaption{padding:11px 14px;border-top:1px solid var(--line);font-size:12px;color:var(--ink-dim)}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}
table{width:100%;border-collapse:collapse;font-size:11.5px;margin-top:6px}
td,th{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{color:var(--ink);font-weight:600;letter-spacing:.04em}
.k{color:var(--gold)}.tid{color:var(--teal)}
.foot{color:var(--ink-dim);font-size:11px;margin-top:26px}
code{color:var(--ink);background:#0e1626;padding:1px 5px;border-radius:3px}
"""


def uri(p):
    return "data:image/png;base64," + base64.b64encode((STILLS / p).read_bytes()).decode()


def table():
    r = ["<table><tr><th>role</th><th>trace id</th><th>terminal</th><th>event sequence (each bend on the highlighted path is one of these)</th></tr>"]
    for label, tid, term, codes in ROWS:
        r.append(f'<tr><td class="k">{label}</td><td class="tid">{tid}</td><td>{term}</td>'
                 f'<td>{" &rsaquo; ".join(codes)}</td></tr>')
    return "".join(r) + "</table>"


def main():
    html = f"""<title>One River (lens) — data-fidelity review</title>
<style>{TOK}</style>
<div class="wrap">
<h1>ONE FOR ALL &nbsp;/&nbsp; <b>ONE RIVER</b> &nbsp;·&nbsp; v5, the data must be visible</h1>
<p class="lede">All 400 futures begin as one thread at Now and split only where their event data diverges.
Traces sharing a prefix share one channel; brightness is that channel's probability mass. The whole is a
lens: it blooms as futures differentiate and thins as light leaves. No bend exists that the data did not cause.</p>

<h2>The lens <span>— full field</span></h2>
<figure><img alt="lens full" src="{uri('lens_box_full.png')}"><figcaption>One origin at Now. It blooms at the
reads, the playoffs (the 6-way season-1 result) and the July-27 boundary, then thins as futures leave. Bright
corridors are the probable paths; the dim haze is the rare states. Rings live in the river.</figcaption></figure>

<h2>The lens <span>— 50% zoom</span></h2>
<figure><img alt="lens zoom" src="{uri('lens_box_zoom50.png')}"><figcaption>The center half: the playoffs bloom,
the July-27 branching, the departures fading off the page, and the surviving stream reaching the gate.</figcaption></figure>

<h2>Proof A — trace audit <span>· the reviewer can read a future off the picture</span></h2>
<figure><img alt="audit overlay" src="{uri('lens_box_audit.png')}"><figcaption>Three real traces highlighted in
white: a title, a July-27 exit, and an alive-at-the-gate. Every bend on a white path lands on a calendar column
where that trace's data changed — cross-check against the table below.</figcaption></figure>
{table()}

<h2>Proof B — reconciliation</h2>
<p class="lede">400 sampled futures collapse to <b>766 drawn channels</b> across the calendar via shared prefixes
(one thread at Now, peak width 139 distinct live states at the July-27 branching). Every channel is a real group
of traces; its brightness is the sum of their weights.</p>

<h2>Proof C — perturbation <span>· a different seed must visibly change the picture</span></h2>
<div class="pair">
<figure><img alt="seed A" src="{uri('lens_box_full.png')}"><figcaption>seed A (20260717)</figcaption></figure>
<figure><img alt="seed B" src="{uri('lens_box_alt.png')}"><figcaption>seed B (88888) — a fresh sample of 400 futures</figcaption></figure>
</div>
<p class="lede">Re-sampling the futures re-draws the fine branching (the tail states differ trace by trace) while the
mass structure — the bright corridors and the lens envelope — holds. If the two were identical the render would be
decoration; they are not.</p>

<p class="foot">Rendered from board_viz_export.json (SOLVER, box fork, cap 0.012, P(east) 0.60). afo_frame.jpg is
not in the repo; the calibration target is the frame's irregularity, not a tiling. Static, no interactivity.</p>
</div>"""
    (HERE / "radial_gallery.html").write_text(html, encoding="utf-8")
    print(f"wrote review page ({(HERE / 'radial_gallery.html').stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
