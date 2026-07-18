"""v7.1 delivery page: the poster, its 50% zoom, per-class coverage, and the perturbation pair.

Nothing else, per the directive. Content-only HTML for the Artifact host.
"""
from __future__ import annotations
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STILLS = HERE / "stills"
C = json.loads((STILLS / "poster_cover.json").read_text())
COVER, N, CAP = C["cover"], C["n_drawn"], C["cap"]
LABEL = {"RING27": "a title in 2027", "RING28": "a title in 2028",
         "ALIVE": "still alive at the gate", "EXITS": "Ant asks out",
         "DEAD": "converted &mdash; the reset"}

TOK = """
:root{--midnight:#0A1120;--ink:#C9D4E3;--ink-dim:#6B7BA0;--gold:#F2C14E;--teal:#35C9C0;--rose:#C4788C;--line:#1b2740;
  --mono:ui-monospace,'Cascadia Code','SF Mono',Menlo,Consolas,monospace}
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
.ok{color:var(--teal)}
.foot{color:var(--ink-dim);font-size:11px;margin-top:28px}
"""


def uri(p):
    return "data:image/png;base64," + base64.b64encode((STILLS / p).read_bytes()).decode()


def cover_table():
    r = ['<table><tr><th>where the future ends up</th><th>routes drawn</th><th>routes that exist</th>'
         '<th>share of that outcome shown</th><th>share of the whole board</th></tr>']
    for K in ("RING27", "ALIVE", "EXITS", "DEAD", "RING28"):
        c = COVER[K]
        cl = "gold" if K == "RING27" else ("rose" if K in ("EXITS", "DEAD") else "teal")
        if c["total"] <= 0:
            r.append(f'<tr><td class="dim">{LABEL[K]}</td><td colspan="4" class="dim">no such path on '
                     f'this board &mdash; the board resolves one postseason (2027); a 2028 title lives '
                     f'inside the gate’s continuation value, not as a route</td></tr>')
            continue
        r.append(f'<tr><td class="{cl}">{LABEL[K]}</td><td>{c["drawn"]} (budget {c["budget"]})</td>'
                 f'<td>{c["corridor_total"]:,}</td><td>{c["shown"] / c["total"] * 100:.0f}%</td>'
                 f'<td>{c["total"] * 100:.2f}%</td></tr>')
    return "".join(r) + "</table>"


def test_table():
    r = ['<table><tr><th>in two seconds you should see</th><th>what carries it</th><th></th></tr>']
    for a, b, ok in C["two_second"]:
        r.append(f'<tr><td>{a}</td><td class="dim">{b}</td><td class="ok">{"PASS" if ok else "FAIL"}</td></tr>')
    return "".join(r) + "</table>"


def main():
    html = f"""<title>One River — the poster (v7.1)</title>
<style>{TOK}</style>
<div class="wrap">
<h1>ONE FOR ALL &nbsp;/&nbsp; <b>ONE RIVER</b> &nbsp;·&nbsp; v7.1, the poster</h1>
<p class="lede">Same lattice, same physics: a channel is a state, so futures that reach the same state
merge; lanes are ordered by equity, so every bend is a change of rank; futures that leave the story
leave the page. What is new is <b>selection</b>. The board holds 12,565 states, and drawing all of them
makes a texture rather than a picture &mdash; so the poster draws {N} channels, budgeted
<b>by where the future ends up</b>, and says so on its own face.</p>

<h2>The poster</h2>
<figure><img alt="poster" src="{uri('poster_full.png')}"><figcaption>One state at Now, because the
present is one state. It spreads through the two tripwire reads, the thin gold enters the ring at the
2027 playoffs, and July 27 splits the board: the teal corridors carry the futures still alive at the
gate, the rose bundle is Ant asking out and the reset, running off the page. The haze is everything
not drawn.</figcaption></figure>

<h2>The poster <span>&mdash; 50%</span></h2>
<figure><img alt="poster zoom" src="{uri('poster_zoom50.png')}"><figcaption>Closer: the corridors are
weighted groups, not single lines, and their brightness is the probability each one carries within its
own outcome.</figcaption></figure>

<h2>Per-class coverage <span>&mdash; the honesty footer, restated</span></h2>
{cover_table()}
<p class="lede">{N} channels drawn against a {CAP} cap. Two things are deliberate and stated on the
poster itself. First, <b>brightness means probability within an outcome, not across outcomes</b>: a
title is 4.5% of the board, and on a global scale the gold would simply not be visible &mdash; so gold
is scaled against gold. Second, the routes not drawn are still there as haze at about 4% alpha, present
and deliberately unreadable; the haze is compressed so it is perceptible where the undrawn futures
actually are, which makes it a presence rather than a measurement. The numbers above are the
measurement.</p>
<p class="lede">Note the shape of the coverage: six routes carry <b>46%</b> of every title future,
because titles run through a narrow neck. Eighteen carry only <b>7%</b> of the futures still alive at
the gate, because survival fans into tens of thousands of distinguishable states. That asymmetry is the
finding, not a rendering artifact.</p>

<h2>The two-second test</h2>
{test_table()}
<p class="lede">Self-scored, which is the weakest kind of scoring. The real test is you showing it cold
to someone and seeing what they say first.</p>

<h2>Perturbation <span>&mdash; structure holds, fine branching changes</span></h2>
<div class="pair">
<figure><img alt="seed A" src="{uri('poster_pert_A.png')}"><figcaption>corridors re-derived from a
400-future sample, seed A</figcaption></figure>
<figure><img alt="seed B" src="{uri('poster_pert_B.png')}"><figcaption>the same, seed B</figcaption></figure>
</div>
<p class="lede">Both frames run the identical selection over flows <i>estimated from a finite sample of
futures</i> rather than the exact flow. The skeleton is stable &mdash; one origin, the ring at the same
place, the July-27 split, the same bundle leaving &mdash; while the thin corridors reshuffle and the
coverage percentages move. That difference is the sampling noise, and it is the reason the delivered
poster above is built from the exact flow instead: it has none.</p>

<p class="foot">Rendered from board_viz_export.json (SOLVER, schema one-for-all/board-viz/2, box fork,
cap 0.012, P(east) 0.60). Zero solver edits. One label corrected from v6: node 13 is the May 2028
lottery, not a second postseason &mdash; the board resolves exactly one. Static, no controls: if this
is approved it is frozen editorial output and joins the freeze bundle and its hash.</p>
</div>"""
    (HERE / "poster_review.html").write_text(html, encoding="utf-8")
    print(f"wrote poster review ({(HERE / 'poster_review.html').stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
