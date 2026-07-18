"""Review page for the v6 lattice still + its proofs (delivery only).

Embeds: the still (full + 50% zoom); the upgraded audit overlay with its event table including
the repaired path and the future it merges with, plus the merge close-up; the extended
reconciliation (merge count, trace-to-channel collapse, peak and gate widths); and the
perturbation pair. Content-only HTML for the Artifact host.
"""
from __future__ import annotations
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STILLS = HERE / "stills"
ROWS = json.loads((STILLS / "lattice_audit_table.json").read_text())
REC = json.loads((STILLS / "lattice_recon.json").read_text())
EXPORT = json.loads((HERE / "board_viz_export.json").read_text())
LB, LR = EXPORT["forks"]["box"]["lattice"], EXPORT["forks"]["rapm"]["lattice"]
RAPM_CONVERT = sum(v for k, v in EXPORT["forks"]["rapm"]["terminals"].items() if k.startswith("CONVERT"))

HUMAN = {0: "Now", 3: "Nov read", 5: "Jan read", 6: "deadline", 7: "playoffs", 8: "draft",
         9: "July 27", 10: "post-July 27", 11: "season-2 read", 12: "deadline 2",
         13: "playoffs 2", 14: "the gate"}
KIND = {"REQUESTED": "Ant requests out", "CONVERT": "converted (the reset)",
        "RING": "a title", "COMMITTED": "commits past the gate"}

TOK = """
:root{--midnight:#0A1120;--ink:#C9D4E3;--ink-dim:#6B7BA0;--gold:#F2C14E;--teal:#35C9C0;--rose:#C4788C;--line:#1b2740;
  --mono:ui-monospace,'Cascadia Code','SF Mono',Menlo,Consolas,monospace}
*{box-sizing:border-box;margin:0}body{background:var(--midnight);color:var(--ink);font-family:var(--mono);padding:38px 20px 80px;line-height:1.55}
.wrap{max-width:1140px;margin:0 auto}
h1{font-size:15px;letter-spacing:.24em;text-transform:uppercase;font-weight:600}h1 b{color:var(--gold)}
.lede{color:var(--ink-dim);font-size:12.5px;margin:10px 0 30px}
h2{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink);margin:36px 0 12px;font-weight:600}
h2 span{color:var(--ink-dim);letter-spacing:.02em;text-transform:none;font-weight:400}
figure{margin:0 0 10px;border:1px solid var(--line);border-radius:5px;overflow:hidden;background:#060b16}
figure img{display:block;width:100%;height:auto}
figcaption{padding:11px 14px;border-top:1px solid var(--line);font-size:12px;color:var(--ink-dim)}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}
table{width:100%;border-collapse:collapse;font-size:11.5px;margin-top:6px}
td,th{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{color:var(--ink);font-weight:600;letter-spacing:.04em}
.k{color:var(--gold)}.tid{color:var(--teal)}.note{color:var(--ink-dim)}
.rose{color:var(--rose)}
.flag{border-left:2px solid var(--gold);padding:12px 16px;background:#0d1524;margin:16px 0;font-size:12.5px;color:var(--ink-dim)}
.flag b{color:var(--gold)}
.foot{color:var(--ink-dim);font-size:11px;margin-top:28px}
"""


def uri(p):
    return "data:image/png;base64," + base64.b64encode((STILLS / p).read_bytes()).decode()


def audit_table():
    r = ['<table><tr><th>role</th><th>trace</th><th>ends</th><th>event sequence</th>'
         '<th>what it proves</th></tr>']
    for label, tid, term, codes, note in ROWS:
        r.append(f'<tr><td class="k">{label}</td><td class="tid">{tid}</td><td>{term}</td>'
                 f'<td>{" &rsaquo; ".join(codes)}</td><td class="note">{note or "&mdash;"}</td></tr>')
    return "".join(r) + "</table>"


def width_table():
    w = LB["widths"]
    head = "".join(f"<th>{HUMAN.get(int(c), c)}</th>" for c in sorted(w, key=int))
    body = "".join(f"<td>{w[c]}</td>" for c in sorted(w, key=int))
    return f"<table><tr>{head}</tr><tr>{body}</tr></table>"


def exit_table():
    r = ['<table><tr><th>leaves at</th><th>what happens</th><th>probability mass</th>'
         '<th>lanes merged into that one channel</th></tr>']
    for c, kind, m, n in REC["exits"]:
        r.append(f'<tr><td class="k">{HUMAN.get(c, c)}</td><td>{KIND.get(kind, kind)}</td>'
                 f'<td>{m * 100:.2f}%</td><td>{n}</td></tr>')
    tot = sum(m for _, _, m, _ in REC["exits"])
    r.append(f'<tr><td colspan="2"><b>total</b></td><td><b>{tot * 100:.2f}%</b></td>'
             f'<td class="note">nothing is lost and nothing ends in frame</td></tr>')
    return "".join(r) + "</table>"


def main():
    rec = REC["recon"]
    html = f"""<title>One River (lattice) — v6 data-fidelity review</title>
<style>{TOK}</style>
<div class="wrap">
<h1>ONE FOR ALL &nbsp;/&nbsp; <b>ONE RIVER</b> &nbsp;·&nbsp; v6, the lattice not the tree</h1>
<p class="lede">A channel here is a <b>state</b>, not a history. So futures that reach the same state
stop being two lines and become one, which is what a prefix tree throws away. Lanes are ordered by
equity, so every crossing on the page is a change of rank. Brightness is probability mass, added in
linear light, which makes conservation of light arithmetic rather than a styling rule: the light in a
column is the probability still in play. Futures that leave the story leave the page.</p>

<h2>The lattice <span>&mdash; full field</span></h2>
<figure><img alt="lattice full" src="{uri('lattice_full.png')}"><figcaption>One state at Now. It opens
at the November read, <b>closes back to six states at the playoffs</b> (a merge: the January read washes
out part of what November said), opens again at the draft, and explodes at July 27 into
{LB['widths']['10']:,} states. From there the field both splits and pinches &mdash;
{LB['widths']['12']:,} states at the second deadline down to {LB['widths']['13']:,} at the playoffs
&mdash; and dims all the way, because two thirds of the probability has already left the page.</figcaption></figure>

<h2>The lattice <span>&mdash; 50% zoom on the second season</span></h2>
<figure><img alt="lattice zoom" src="{uri('lattice_zoom50.png')}"><figcaption>The braid is state rank
changing hands. Every crossing is two states swapping equity order between columns; nothing here is a
lane exchange chosen for looks. The pinch at the second playoffs is {LB['widths']['12']:,} states
merging into {LB['widths']['13']:,}.</figcaption></figure>

<h2>Proof A &mdash; trace audit <span>· five real futures, one of them repaired</span></h2>
<figure><img alt="audit overlay" src="{uri('lattice_audit.png')}"><figcaption>Five real traces in white
over a dimmed field. Every bend on a white path is a change in that future's equity rank, and the table
below lists the events that caused it.</figcaption></figure>
{audit_table()}

<h2>The merge, close up <span>· the physics v5 discarded</span></h2>
<figure><img alt="merge close-up" src="{uri('lattice_merge_zoom.png')}"><figcaption>Only the repaired
future and the future it merges with. They part at the November read &mdash; one gets LaMelo available,
one does not &mdash; run as two separate lines through the January read, and then <b>land on the same
state at the deadline and become one line</b>. They stay one line to the gate, because from there they
are not two similar futures, they are the same future. A prefix tree would have drawn them as two lines
forever.</figcaption></figure>

<h2>Proof B &mdash; reconciliation</h2>
<p class="lede">{rec['n_states']:,} states, {rec['n_edges']:,} transitions,
<b>{rec['merges']:,} merge points</b> (states reached from more than one prior state). The
{rec['n_traces']} sampled futures occupy {rec['occupied']:,} of those states. Peak width
{rec['peak'][1]:,} distinct live states at {HUMAN.get(rec['peak'][0], rec['peak'][0])};
{rec['gate']:,} at the gate.</p>
{width_table()}
<p class="lede" style="margin-top:16px">And the exits &mdash; every one a merged weighted channel that
runs off the canvas:</p>
{exit_table()}

<div class="flag"><b>One deviation, flagged.</b> The directive defines a channel as the group of
<i>traces</i> on the same state. Measured: in the 400-trace sample that produces only <b>12 merge
points across 774 channels</b> &mdash; out in the wide part of the field two sampled histories almost
never land on the same state, so a sample-built render would have been a tree wearing a lattice's name.
The same object computed exactly over the solver's forward mass gives <b>{rec['merges']:,} merge points
across {rec['n_states']:,} states</b>. Same definition, no estimator noise. So the field is the exact
lattice and the traces do the audit. Second disclosure: column height is
<b>&radic;(live states)</b>, not live states &mdash; on a linear scale the nine states at the November
read are two pixels beside a gate {LB['widths']['14']:,} lanes wide. Rank order inside a column is exact
and uncompressed.</div>

<h2>Proof C &mdash; perturbation <span>· a different input must visibly change the picture</span></h2>
<div class="pair">
<figure><img alt="box fork" src="{uri('lattice_full.png')}"><figcaption>box fork &mdash;
{LB['n_states']:,} states, {LB['n_merge_nodes']:,} merges</figcaption></figure>
<figure><img alt="rapm fork" src="{uri('lattice_rapm.png')}"><figcaption>rapm fork &mdash;
{LR['n_states']:,} states, {LR['n_merge_nodes']:,} merges</figcaption></figure>
</div>
<p class="lede">Same renderer, same code path, one different solver input. Under the rapm fork
<b>{RAPM_CONVERT * 100:.1f}%</b> of the probability
converts at July 27, so nearly all the light leaves in a single beam and what remains at the gate is a
ghost. If the render were decoration the two frames would look alike. Note the change from v5: the field
is now exact, so re-seeding no longer moves it &mdash; a seed only reshuffles which futures the audit
picks. Perturbing the picture now requires perturbing the model, which is the stronger test.</p>

<p class="foot">Rendered from board_viz_export.json (SOLVER, schema one-for-all/board-viz/2,
cap 0.012, P(east) 0.60). Zero solver edits; the viz lane reads the export only. afo_frame.jpg is
still not in the repo, so density and glow stay calibrated to the v4-approved braid. Static, no
interactivity.</p>
</div>"""
    (HERE / "lattice_review.html").write_text(html, encoding="utf-8")
    print(f"wrote review page ({(HERE / 'lattice_review.html').stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
