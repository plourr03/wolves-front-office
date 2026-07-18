"""v7.2 delivery page: the poster, its 50% zoom, per-class coverage, and the perturbation pair.

Nothing else, per the directive. Content-only HTML for the Artifact host.
"""
from __future__ import annotations
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STILLS = HERE / "stills"
C = json.loads((STILLS / "poster_cover.json").read_text())
COVER, N, CAP, BUD = C["cover"], C["n_drawn"], C["cap"], C["budgets"]
TV = C["title_verdict"]
SP = C["spacing"]
LABEL = {"TITLE": "a title", "ALIVE": "still alive at the gate",
         "EXITS": "Ant asks out", "DEAD": "converted &mdash; the reset"}
ORDER = ("TITLE", "ALIVE", "EXITS", "DEAD")

TOK = """
:root{--midnight:#0A1120;--ink:#C9D4E3;--ink-dim:#6B7BA0;--gold:#F2C14E;--teal:#35C9C0;--rose:#C4788C;
  --red:#E24B4A;--line:#1b2740;--mono:ui-monospace,'Cascadia Code','SF Mono',Menlo,Consolas,monospace}
*{box-sizing:border-box;margin:0}body{background:var(--midnight);color:var(--ink);font-family:var(--mono);padding:38px 20px 80px;line-height:1.55}
.wrap{max-width:1180px;margin:0 auto}
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
.gold{color:var(--gold)}.teal{color:var(--teal)}.rose{color:var(--rose)}.dim{color:var(--ink-dim)}
.pass{color:var(--teal)}.fail{color:var(--red);font-weight:600}
.flag{border-left:2px solid var(--gold);padding:12px 16px;background:#0d1524;margin:16px 0;font-size:12.5px;color:var(--ink-dim)}
.flag b{color:var(--gold)}
.foot{color:var(--ink-dim);font-size:11px;margin-top:28px}
"""


def uri(p):
    return "data:image/png;base64," + base64.b64encode((STILLS / p).read_bytes()).decode()


def cover_table():
    r = ['<table><tr><th>where the future ends up</th><th>share of the board</th><th>routes drawn</th>'
         '<th>routes that exist</th><th>those routes are</th><th>with shared segments</th></tr>']
    for K in ORDER:
        c = COVER[K]
        cl = "gold" if K == "TITLE" else ("rose" if K in ("EXITS", "DEAD") else "teal")
        r.append(f'<tr><td class="{cl}">{LABEL[K]}</td><td>{c["total"] * 100:.2f}%</td>'
                 f'<td>{c["drawn"]} (budget {c["budget"]})</td><td>{c["routes"]:,}</td>'
                 f'<td>{c["shown"] / c["total"] * 100:.1f}% of the outcome</td>'
                 f'<td>{c["shown_sub"] / c["total"] * 100:.1f}%</td></tr>')
    return "".join(r) + "</table>"


def spacing_block():
    rows = "".join(f'<tr><td>{k}</td><td>{v[0] * 100:.0f}% to {v[1] * 100:.0f}%</td></tr>'
                   for k, v in SP["occupancy"].items())
    return (f'<h2>Spacing <span>&mdash; measured off the frame, same as everything else</span></h2>'
            f'<table><tr><th>act</th><th>field occupancy (target 35&ndash;70%)</th></tr>{rows}</table>'
            f'<p class="lede">Largest empty region <b>{SP["largest_empty_region"] * 100:.0f}%</b> of the '
            f'field against a ~15% ceiling, and <b>{SP["label_collisions"]}</b> label collisions. The cost '
            f'is stated rather than buried: the log pitch bought the early braid by compressing the width '
            f'signal, so the ratio between the narrowest and widest drawn column fell from 12x to about 2x. '
            f'Width still rises monotonically with the state count, so the pinches remain true &mdash; the '
            f'poster just says &ldquo;wide&rdquo; more quietly than v7.1 did.</p>')


def test_table():
    r = ['<table><tr><th>in two seconds you should see</th><th>measured off the frame</th><th></th></tr>']
    for a, b, ok in C["two_second"]:
        cls = "pass" if ok else "fail"
        r.append(f'<tr><td>{a}</td><td class="dim">{b}</td><td class="{cls}">{"PASS" if ok else "FAIL"}</td></tr>')
    return "".join(r) + "</table>"


def main():
    t, al = COVER["TITLE"], COVER["ALIVE"]
    html = f"""<title>One River — the poster (v7.2)</title>
<style>{TOK}</style>
<div class="wrap">
<h1>ONE FOR ALL &nbsp;/&nbsp; <b>ONE RIVER</b> &nbsp;·&nbsp; v7.2, the poster</h1>
<p class="lede">Same lattice, same physics: a channel is a state, so futures that reach the same state
merge; lanes are ordered by equity, so every bend is a change of rank; futures that leave the story
leave the page. What is new is <b>selection</b>. The board holds 12,565 states, and drawing all of them
makes a texture rather than a picture &mdash; so the poster draws {N} routes, budgeted <b>by where the
future ends up</b>, and prints on its own face how much of each outcome those routes actually carry.</p>
<p class="lede"><b>v7.2 is spacing only.</b> Layout is editorial, data is sacred: lane pitch now follows the
log of the live-state count and column spacing follows structural activity rather than days, so the early
river reads as a braid instead of a string and the quiet stretches stop eating the page. Selection, the
physics, the proofs and every number below are unchanged from v7.1 &mdash; the coverage table is
identical. What moved is where things sit.</p>

<h2>The poster</h2>
<figure><img alt="poster" src="{uri('poster_full.png')}"><figcaption>One state at Now, because the
present is one state. It spreads through the two tripwire reads, the thin gold enters the ring at the
2027 playoffs, and July 27 splits the board: teal carries the futures still alive at the gate, and two
rose bundles leave the page &mdash; Ant asking out downward, the reset upward. The haze is everything
not drawn.</figcaption></figure>

<h2>The poster <span>&mdash; 50%</span></h2>
<figure><img alt="poster zoom" src="{uri('poster_zoom50.png')}"><figcaption>Closer: each drawn channel
is one route through the state space, and its brightness is the probability it carries within its own
outcome.</figcaption></figure>

<h2>Per-class coverage <span>&mdash; the honesty footer, restated</span></h2>
{cover_table()}
<p class="lede">Two columns, because there are two honest answers. "Those routes are" is the exact
probability the future follows one of the drawn state sequences. "With shared segments" is the
probability it stays inside the drawn corridors the whole way, which is larger because routes overlap.
{N} routes drawn against budgets {'+'.join(str(BUD[k]) for k in ORDER)}={sum(BUD.values())} and a hard
cap of {CAP}; <b>every budget is saturated</b>, so in every class there are more routes than are
drawn.</p>
<p class="lede">The shape of that table is the finding. Six routes carry <b>{t['shown'] / t['total'] * 100:.0f}%</b>
of every title future, because titles run through a narrow neck. Eighteen carry
<b>{al['shown'] / al['total'] * 100:.1f}%</b> of the futures still alive at the gate, because survival fans into
{al['routes']:,} distinguishable routes. Winning is a corridor; surviving is a delta.</p>

<div class="flag"><b>A correction, because the first cut of this poster overstated itself.</b>
Verification caught that the coverage numbers were computed in the wrong currency &mdash; widest-path
bottleneck weights rather than route probability. In a lattice with 1,376 merge points those are very
different: the published figure for the survivors was 7.2% when the truth is
{al['shown'] / al['total'] * 100:.1f}%. Selection now picks the most probable routes by an exact K-best
search, and every number above is the probability of an event. A page whose whole premise is honest
selection does not get to be sloppy about its own arithmetic.</div>

<div class="flag"><b>There is no 2028 title on this board, and that is measured, not assumed.</b>
{TV['text'].capitalize()}. Its budget of 10 routes went unspent, which is why {N} rather than
{sum(BUD.values()) + 10} channels are drawn.</div>

{spacing_block()}

<h2>The two-second test</h2>
{test_table()}
<p class="lede">Measured off the rendered frame rather than asserted &mdash; pixel counts, not opinions.
Still the weakest kind of scoring, because it tests what I chose to measure. The real test is you
showing it cold to someone and hearing what they say first.</p>

<h2>Perturbation <span>&mdash; structure holds, fine branching changes</span></h2>
<div class="pair">
<figure><img alt="seed A" src="{uri('poster_pert_A.png')}"><figcaption>routes re-derived from a
400-future sample, seed A</figcaption></figure>
<figure><img alt="seed B" src="{uri('poster_pert_B.png')}"><figcaption>the same, seed B</figcaption></figure>
</div>
<p class="lede">Both frames run the identical selection over flows <i>estimated from a finite sample of
futures</i> rather than the exact flow. The skeleton is stable &mdash; one origin, the ring in the same
place, the July-27 split, the same bundles leaving &mdash; while the thin routes reshuffle and the
coverage percentages move. That difference is sampling noise, and it is why the delivered poster above
is built from the exact flow instead: it has none.</p>

<p class="foot">Rendered from board_viz_export.json (SOLVER, schema one-for-all/board-viz/2, box fork,
cap 0.012, P(east) 0.60). Zero solver edits. One label corrected from v6: node 13 is the May 2028
lottery, not a second postseason. Static, no controls: if this is approved it is frozen editorial
output and joins the freeze bundle and its hash.</p>
</div>"""
    (HERE / "poster_review.html").write_text(html, encoding="utf-8")
    print(f"wrote poster review ({(HERE / 'poster_review.html').stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
