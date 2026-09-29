#!/usr/bin/env python3
"""The Bet, Part 2: six interactive visuals, one per finding, built from the outputs and the sheet.

Same pattern and chrome as Part 1 (`charts_part1.py`): self-contained fragments the host wraps
with D3 v7 and the design tokens, a preview harness each, a launcher. Placed in the article
with `{{viz:<id>}}`.

  the-fork            the offseason verdict as a function of Cody Williams's minutes: the four
                      views' deltas on a minutes slider, the 12.6 threshold where the four stop
                      agreeing; hero is the threshold.
  the-verdicts        every move on the ledger with its four cells (two aging bases by two
                      minutes allocators), the ones that ship in green; hero is LaMelo in.
  the-second-creator  three tabs: what a primary defender takes off each Wolf (Edwards at the
                      1st percentile of 150), who creates his own shot (unassisted shares against
                      the league median), and how much ball there is to go around (the projected
                      five's usage sum against the league); hero is Edwards's percentile.
  the-eight-tests     the eight regular-season traits on 195 playoff series as a forest plot,
                      every interval crossing zero, defence share pointing the wrong way; hero is
                      zero of eight.
  model-vs-market     thirty teams, model against market on a log-log scatter with the agreement
                      line, Minnesota, Boston and Charlotte named, Charlotte's pre-fix point
                      falling to the corrected one; hero is the Boston gap.
  the-path            three tabs: the seed distribution with the play-in zone, the first-round
                      opponent, and what losing each of the three costs; hero is the modal seed.

GATE. Every hero figure and every figure the captions state is checked against
`outputs/final_numbers.csv` before a file is written. The run ID and the keys checked are the
first line of each fragment.

    python kuminga/scripts/charts_part2.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

from kuminga.lib import runlog  # noqa: E402
import charts_part1 as C1       # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs", "charts", "part2")
OUTS = os.path.join(REPO, "kuminga", "outputs")
VIEW_LABEL = {"consensus": "consensus", "rapm": "RAPM", "box": "box score", "darko": "DARKO"}


def pct2(v):
    return "%.2f%%" % v


# ================================================================== 1. the fork
def viz_the_fork(S):
    w = pd.read_csv(os.path.join(OUTS, "williams_minutes_sensitivity.csv")).sort_values("williams_mpg")
    grid = [dict(mpg=float(x.williams_mpg), consensus=float(x.delta_consensus), rapm=float(x.delta_rapm),
                 box=float(x.delta_box), darko=float(x.delta_darko), sign=str(x.delta_sign), title=float(x.title_mean))
            for _, x in w.iterrows()]
    default = float(w[w.level == "model default"].williams_mpg.iloc[0])
    assert "%.1f" % default == S["williams_mpg"], (default, S["williams_mpg"])
    # the threshold: the highest minutes at which some view is no longer negative, by linear interpolation
    thr = None
    for v in ("consensus", "rapm", "box", "darko"):
        pts = [(g["mpg"], g[v]) for g in grid]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if y0 >= 0 > y1:
                xx = x0 + (0 - y0) * (x1 - x0) / (y1 - y0)
                thr = xx if thr is None else max(thr, xx)
    assert thr is not None and "%.1f" % thr == S["williams_threshold"], (thr, S["williams_threshold"])
    W = pd.read_csv(os.path.join(OUTS, "williams_ordering_check.csv"))
    cal = float(W[W.ordering.str.startswith("calibrated: median, new team top ten")].iloc[0].williams_mpg)
    assert "%.1f" % cal == S["w_cal_top10_mpg"]
    data = dict(grid=grid, default=default, default_txt=S["williams_mpg"], threshold=thr, threshold_txt=S["williams_threshold"],
                cal=cal, cal_txt=S["w_cal_top10_mpg"], ret_txt=S["w_ret_top10_median"], rank_primary=S["w_rank_primary"], rank_impact=S["w_rank_impact_only"],
                flat_mpg=S["w_mpg_flat"], flat_rank=S["w_rank_flat"], xmax=float(w.williams_mpg.max()))
    # D111: the model's default benches Williams (0.0), so the slider starts at zero and walks UP to the base rate
    pid = "the-fork"
    p = "#viz-%s" % pid
    stage = ('<svg class="th-svg" role="img" aria-label="The offseason verdict against Cody Williams minutes"></svg>'
             '<div class="th-slider"><label class="th-slider-lab">Cody Williams, minutes a night: <span class="th-slider-val"></span></label>'
             + ('<input class="th-range" type="range" min="0" max="%.1f" step="0.1" value="%.1f" aria-label="Cody Williams minutes a night"></div>' % (data["xmax"], default))
             + '<div class="th-readout"></div>')
    html = C1.chrome_html(pid, "The fork", "the verdict against one player's minutes", "minutes a night", "above this, every way of scoring players says the summer hurt",
                          "Each line is one way of scoring players: the change in Minnesota's title odds, in points, from the roster that finished last season to the one that starts this one, with Cody Williams at the minutes on the axis and those minutes taken from the players the model trusts more. "
                          "Un-aged basis, the field held fixed. The default of " + S["williams_mpg"] + " is where the model's ordering puts him: " + S["w_rank_primary"] + "th man under the rule it applies to every player who changed teams, " + S["w_rank_impact_only"] + "th on impact alone. The flat half-and-half order that handed him " + S["w_mpg_flat"] + " a night is kept as the sensitivity. The blue line is the base rate: movers like him who landed on a top-ten team kept a median " + S["w_ret_top10_median"] + " of their prior minutes. Drag the slider; the verdict is ALL NEGATIVE only while every line is below zero.",
                          extra_stage=stage, hero_num=S["williams_mpg"])
    css = C1.chrome_css(pid, "var(--status-warning)") + """
  %(p)s .th-svg { width: 100%%; height: 300px; display: block; }
  %(p)s.is-compact .th-svg { height: 280px; }
  %(p)s .th-axis text { font: 500 10px var(--family-mono); fill: var(--text-tertiary); }
  %(p)s .th-axis line, %(p)s .th-axis path { stroke: rgba(255,255,255,.12); }
  %(p)s .th-zero { stroke: rgba(255,255,255,.45); stroke-width: 1.2; }
  %(p)s .th-line { fill: none; stroke-width: 2; opacity: 0; transition: opacity 400ms ease; }
  %(p)s .th-line.is-on { opacity: 1; }
  %(p)s .th-line-lab { font: 700 10px var(--family-mono); opacity: 0; transition: opacity 400ms ease; }
  %(p)s .th-line-lab.is-on { opacity: 1; }
  %(p)s .th-thr { stroke: var(--status-warning); stroke-width: 1.5; stroke-dasharray: 5 4; opacity: 0; transition: opacity 400ms ease; }
  %(p)s .th-thr.is-on { opacity: 1; }
  %(p)s .th-thr-lab { font: 700 10px var(--family-mono); fill: var(--status-warning); letter-spacing: .04em; text-transform: uppercase; opacity: 0; transition: opacity 400ms ease; }
  %(p)s .th-thr-lab.is-on { opacity: 1; }
  %(p)s .th-cal { stroke: var(--status-info); }
  %(p)s .th-cal-lab { fill: var(--status-info); }
  %(p)s .th-cursor { stroke: #fff; stroke-width: 1; opacity: .7; }
  %(p)s .th-dot { stroke: #050505; stroke-width: 1.5; }
  %(p)s .th-neg-band { fill: rgba(255,92,92,.06); }
  %(p)s .th-slider { display: flex; flex-direction: column; gap: 6px; padding: 8px 6px 2px; }
  %(p)s .th-slider-lab { font: 600 12px var(--family-sans); color: var(--text-secondary); }
  %(p)s .th-slider-val { font: 700 12px var(--family-mono); color: var(--text-primary); }
  %(p)s .th-range { width: 100%%; accent-color: var(--status-warning); cursor: pointer; }
  %(p)s .th-readout { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; padding: 8px 6px 4px; }
  %(p)s.is-compact .th-readout { grid-template-columns: repeat(2, 1fr); }
  %(p)s .th-cell { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 6px 8px; }
  %(p)s .th-cell-lab { font: 600 9.5px var(--family-mono); color: var(--text-tertiary); letter-spacing: .04em; text-transform: uppercase; }
  %(p)s .th-cell-val { font: 700 15px var(--family-mono); color: var(--text-primary); }
  %(p)s .th-cell.is-neg .th-cell-val { color: var(--status-error); }
  %(p)s .th-cell.is-pos .th-cell-val { color: var(--accent-hover); }
  %(p)s .th-verdict { grid-column: 1 / -1; text-align: center; font: 700 12px var(--family-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--text-secondary); padding-top: 4px; }
  %(p)s .th-verdict.is-neg { color: var(--status-error); }
  %(p)s .th-verdict.is-mixed { color: var(--status-warning); }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var VIEWS = [["consensus", "consensus", "var(--dataviz-2)"], ["rapm", "RAPM", "var(--dataviz-3)"], ["box", "box score", "var(--dataviz-6)"], ["darko", "DARKO", "var(--dataviz-4)"]];
  var CAPS = [
    "The model's default benches Cody Williams: " + D.rank_primary + "th man on the rule it applies to every player who changed teams, " + D.rank_impact + "th on impact alone. The flat order that handed him " + D.flat_mpg + " a night is the sensitivity now, not the answer.",
    "At zero, three of the four ways of scoring players say the summer helped a little and one says it hurt. Mixed.",
    "Give him minutes and they come from the players the model trusts more. The lines fall.",
    "Above " + D.threshold_txt + " a night the last of the four crosses zero and every way of scoring players says the summer hurt. Movers like him who landed on a top-ten team kept " + D.ret_txt + " of their minutes, " + D.cal_txt + " for him. That's the fork, and the base rate sits on the wrong side of it."
  ];
  function interp(v, mpg) {
    var pts = D.grid;
    if (mpg <= pts[0].mpg) return pts[0][v];
    for (var i = 0; i < pts.length - 1; i++) {
      var a = pts[i], b = pts[i + 1];
      if (mpg >= a.mpg && mpg <= b.mpg) { var t = (b.mpg === a.mpg) ? 0 : (mpg - a.mpg) / (b.mpg - a.mpg); return a[v] + t * (b[v] - a[v]); }
    }
    return pts[pts.length - 1][v];
  }
  var cur = D.default;
  function build() {
    var compact = compactNow();
    var svg = root.select(".th-svg"); svg.selectAll("*").remove();
    var W = Math.max(320, Math.min(720, rootNode.clientWidth || 640)) - 26, H = compact ? 280 : 300;
    var m = { t: 18, r: compact ? 60 : 84, b: 34, l: compact ? 38 : 44 };
    svg.attr("viewBox", "0 0 " + W + " " + H);
    var x = d3.scaleLinear().domain([0, D.xmax]).range([m.l, W - m.r]);
    var allv = []; D.grid.forEach(function (g) { VIEWS.forEach(function (v) { allv.push(g[v[0]]); }); });
    var y = d3.scaleLinear().domain([Math.min(-1.5, d3.min(allv) - 0.1), Math.max(1, d3.max(allv) + 0.1)]).range([H - m.b, m.t]);
    svg.append("rect").attr("class", "th-neg-band").attr("x", m.l).attr("width", W - m.l - m.r).attr("y", y(0)).attr("height", H - m.b - y(0));
    var ax = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m.b) + ")").call(d3.axisBottom(x).ticks(compact ? 4 : 8).tickFormat(function (v) { return v; }));
    ax.select(".domain").remove();
    svg.append("text").attr("class", "th-axis").append("tspan").attr("x", (m.l + W - m.r) / 2).attr("y", H - 4).attr("text-anchor", "middle").style("font", "500 10px var(--family-mono)").style("fill", "var(--text-tertiary)").text("Williams minutes a night");
    var ay = svg.append("g").attr("class", "th-axis").attr("transform", "translate(" + m.l + ",0)").call(d3.axisLeft(y).ticks(5).tickFormat(function (v) { return (v > 0 ? "+" : "") + v.toFixed(1); }).tickSize(-(W - m.l - m.r)));
    ay.select(".domain").remove();
    svg.append("line").attr("class", "th-zero").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(0)).attr("y2", y(0));
    var lines = {};
    VIEWS.forEach(function (v) {
      var pts = D.grid.map(function (g) { return [x(g.mpg), y(g[v[0]])]; });
      var path = svg.append("path").attr("class", "th-line").attr("d", d3.line()(pts)).attr("stroke", v[2]);
      var last = D.grid[D.grid.length - 1];
      var lab = svg.append("text").attr("class", "th-line-lab").attr("x", x(last.mpg) + 6).attr("y", y(last[v[0]]) + 3.5).attr("fill", v[2]).text(v[1]);
      lines[v[0]] = { path: path, lab: lab };
    });
    var thr = svg.append("line").attr("class", "th-thr").attr("x1", x(D.threshold)).attr("x2", x(D.threshold)).attr("y1", m.t).attr("y2", H - m.b);
    var thrLab = svg.append("text").attr("class", "th-thr-lab").attr("x", x(D.threshold) - 6).attr("y", m.t + 10).attr("text-anchor", "end").text(D.threshold_txt + " a night");   // D111: left of its line, away from the base-rate label
    var calLine = svg.append("line").attr("class", "th-thr th-cal").attr("x1", x(D.cal)).attr("x2", x(D.cal)).attr("y1", m.t).attr("y2", H - m.b);
    var calLab = svg.append("text").attr("class", "th-thr-lab th-cal-lab").attr("x", x(D.cal) + 6).attr("y", m.t + 10).attr("text-anchor", "start").text("base rate " + D.cal_txt);   // D111: short at every width; the note explains the contender destination
    var cursor = svg.append("line").attr("class", "th-cursor").attr("y1", m.t).attr("y2", H - m.b);
    var dots = {};
    VIEWS.forEach(function (v) { dots[v[0]] = svg.append("circle").attr("class", "th-dot").attr("r", 4.5).attr("fill", v[2]); });
    // readout
    var ro = root.select(".th-readout"); ro.selectAll("*").remove();
    var cells = {};
    VIEWS.forEach(function (v) {
      var c = ro.append("div").attr("class", "th-cell");
      c.append("div").attr("class", "th-cell-lab").text(v[1]);
      cells[v[0]] = c.append("div").attr("class", "th-cell-val");
      cells[v[0] + "_el"] = c;
    });
    var verdict = ro.append("div").attr("class", "th-verdict");
    var range = root.select(".th-range").attr("max", D.xmax.toFixed(1)).attr("value", cur.toFixed(1));
    range.on("input", function () { cur = parseFloat(this.value); clearPlayTimers(); setAt(cur); showReplay(); });
    function setAt(mpg) {
      cursor.attr("x1", x(mpg)).attr("x2", x(mpg));
      var neg = 0;
      VIEWS.forEach(function (v) {
        var val = interp(v[0], mpg);
        dots[v[0]].attr("cx", x(mpg)).attr("cy", y(val));
        cells[v[0]].text((val > 0 ? "+" : "") + val.toFixed(2));
        cells[v[0] + "_el"].classed("is-neg", val < 0).classed("is-pos", val > 0);
        if (val < 0) neg++;
      });
      var all = neg === VIEWS.length;
      verdict.text(all ? "all four negative: the summer hurt" : "mixed: the four ways don't agree").classed("is-neg", all).classed("is-mixed", !all);
      root.select(".th-slider-val").text(mpg.toFixed(1));
      root.select(".th-range").property("value", mpg.toFixed(1));
    }
    lastBuilt = { lines: lines, thr: thr, thrLab: thrLab, calLine: calLine, calLab: calLab, setAt: setAt, compact: compact };
    return lastBuilt;
  }
  function linesOn(b, on) { Object.keys(b.lines).forEach(function (k) { b.lines[k].path.classed("is-on", on); b.lines[k].lab.classed("is-on", on); }); }
  function finalState(b) {
    clearPlayTimers(); linesOn(b, true); b.thr.classed("is-on", true); b.thrLab.classed("is-on", true); b.calLine.classed("is-on", true); b.calLab.classed("is-on", true);
    b.setAt(cur); root.select(".th-hero-num").text(D.threshold_txt); root.classed("is-landed", true); setCaption(CAPS[3], true); showReplay();
  }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false);
    linesOn(b, false); b.thr.classed("is-on", false); b.thrLab.classed("is-on", false); b.calLine.classed("is-on", false); b.calLab.classed("is-on", false);
    cur = D.default; b.setAt(cur); root.select(".th-hero-num").text(D.default_txt); setCaption(CAPS[0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    at(700, function () { linesOn(b, true); setCaption(CAPS[1]); });
    at(2600, function () { setCaption(CAPS[2]); });
    // the slider walks up from the default (zero) to the base rate, through the threshold
    var steps = 40, from = D.default, to = D.cal;
    for (var i = 1; i <= steps; i++) {
      (function (i) { at(2800 + i * 45, function () { cur = from + (to - from) * i / steps; b.setAt(cur); root.select(".th-hero-num").text(cur.toFixed(1)); }); })(i);
    }
    at(2800 + steps * 45 + 200, function () { b.thr.classed("is-on", true); b.thrLab.classed("is-on", true); b.calLine.classed("is-on", true); b.calLab.classed("is-on", true); root.select(".th-hero-num").text(D.threshold_txt); root.classed("is-landed", true); setCaption(CAPS[3]); });
    at(2800 + steps * 45 + 1400, showReplay);
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + C1.script(pid, js), ["williams_mpg", "williams_threshold"]


# ================================================================== 2. the verdicts
def viz_the_verdicts(S):
    r7 = pd.read_csv(os.path.join(OUTS, "r7_allocator_verdicts.csv")).set_index("item")
    items = [("ball_in", "LaMelo Ball in"), ("reid_out", "Naz Reid out"), ("A_c3_default_shannon", "Kuminga, against the fill at the four (Cody Williams)"),
             ("D_beringer_fills", "Kuminga, if Beringer fills the four instead"), ("ddv_injury", "DiVincenzo's Achilles, not a transaction"),
             ("randle_out", "Julius Randle out"), ("dosunmu_retained", "Ayo Dosunmu re-signed"),
             ("other_departures", "The other departures, a bundle of seven"), ("depth", "Depth signings and re-signings")]
    rows = []
    # D111: the slot file keeps the historical variant id; the sheet key names the fill
    SHEET_KEY = {"A_c3_default_shannon": "A_c3_default_williams"}
    for key, lab in items:
        x = r7.loc[key]
        sk = SHEET_KEY.get(key, key)
        cells = dict(pooled_u=float(x.pooled_unaged_mean), pooled_a=float(x.pooled_aged_mean),
                     tr_u=float(x.teamrank_unaged_mean), tr_a=float(x.teamrank_aged_mean))
        assert "%+.2f" % cells["pooled_u"] == S["v_%s_pooled_u" % sk], (key, cells["pooled_u"], S["v_%s_pooled_u" % sk])
        assert "%+.2f" % cells["pooled_a"] == S["v_%s_pooled_a" % sk], (key, cells["pooled_a"], S["v_%s_pooled_a" % sk])
        rows.append(dict(key=key, label=lab, ships=bool(x.ships_all_four), signs=str(x.signs), family=str(x.family),
                         pooled_u_sign=str(x.pooled_unaged_sign), pooled_a_sign=str(x.pooled_aged_sign),
                         pooled_u_clear=int(x.pooled_unaged_clear), pooled_a_clear=int(x.pooled_aged_clear), **cells))
    data = dict(rows=rows, ball_txt=S["v_ball_in_pooled_u"], reid_txt=S["v_reid_out_pooled_u"], kum_txt=S["v_A_c3_default_williams_pooled_u"], ddv_txt=S["v_ddv_injury_pooled_u"])
    pid = "the-verdicts"
    p = "#viz-%s" % pid
    stage = '<svg class="th-svg" role="img" aria-label="Every move with its four cells"></svg>'
    html = C1.chrome_html(pid, "The verdicts", "every move, four cells each", "points of title odds", "LaMelo in, the one clearly positive move; green rows ship under every cell",
                          "Each row is a move; each mark is the change in Minnesota's title odds, in points, under one cell: a circle for the pooled allocator, a square for the team-rank allocator, filled for the un-aged basis and hollow for the aged one. "
                          "A verdict ships only if all four cells agree on the sign and clear the simulation's own noise under every way of scoring players. Randle, Dosunmu and the bundles don't. Hover a row for the cells.",
                          extra_stage=stage, hero_num="0.00")
    css = C1.chrome_css(pid, "var(--accent-default)") + """
  %(p)s .th-svg { width: 100%%; height: 380px; display: block; }
  %(p)s.is-compact .th-svg { height: 430px; }
  %(p)s .th-axis text { font: 500 10px var(--family-mono); fill: var(--text-tertiary); }
  %(p)s .th-axis line, %(p)s .th-axis path { stroke: rgba(255,255,255,.12); }
  %(p)s .th-zero { stroke: rgba(255,255,255,.45); stroke-width: 1.2; }
  %(p)s .th-row { cursor: pointer; opacity: 0; transition: opacity 320ms ease; }
  %(p)s .th-row.is-on { opacity: 1; }
  %(p)s .th-rlab { font: 600 11px var(--family-sans); fill: var(--text-secondary); }
  %(p)s .th-row.is-ship .th-rlab { fill: var(--text-primary); font-weight: 700; }
  %(p)s.is-compact .th-rlab { font-size: 9.5px; }
  %(p)s .th-range { stroke: rgba(255,255,255,.22); stroke-width: 2; }
  %(p)s .th-row.is-ship .th-range { stroke: var(--accent-subtle); stroke-width: 6; }
  %(p)s .th-mark { stroke-width: 1.5; }
  %(p)s .th-ship-tag { font: 700 8.5px var(--family-mono); letter-spacing: .05em; text-transform: uppercase; fill: var(--accent-hover); }
  %(p)s .th-legend { font: 500 10px var(--family-sans); fill: var(--text-tertiary); }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var CAPS = [
    "Every move on the ledger, priced four ways: two aging bases, two rules for handing out minutes.",
    "LaMelo in is the one clearly positive move, " + D.ball_txt + " points of title odds. Naz out is clearly negative, " + D.reid_txt + ".",
    "Kuminga against whoever else would play the four: " + D.kum_txt + ", and it holds in every cell. The one thing that flips it is Beringer taking the minutes.",
    "Randle out and the Dosunmu re-sign don't get a sign. The four ways can't agree, so neither do I."
  ];
  function fmt(v) { return (v > 0 ? "+" : "") + v.toFixed(2); }
  function build() {
    var compact = compactNow();
    var svg = root.select(".th-svg"); svg.selectAll("*").remove();
    var W = Math.max(320, Math.min(720, rootNode.clientWidth || 640)) - 26, H = compact ? 430 : 380;
    var m = { t: compact ? 44 : 30, r: 14, b: 30, l: compact ? 150 : 250 };
    svg.attr("viewBox", "0 0 " + W + " " + H);
    var vals = []; D.rows.forEach(function (r) { vals.push(r.pooled_u, r.pooled_a, r.tr_u, r.tr_a); });
    var x = d3.scaleLinear().domain([Math.min(-1.5, d3.min(vals) - 0.15), Math.max(1.8, d3.max(vals) + 0.15)]).range([m.l, W - m.r]);
    var y = d3.scaleBand().domain(D.rows.map(function (r) { return r.key; })).range([m.t, H - m.b]).paddingInner(0.35);
    var ax = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m.b) + ")").call(d3.axisBottom(x).ticks(compact ? 5 : 7).tickFormat(fmt).tickSize(-(H - m.b - m.t)));
    ax.select(".domain").remove();
    svg.append("line").attr("class", "th-zero").attr("x1", x(0)).attr("x2", x(0)).attr("y1", m.t - 6).attr("y2", H - m.b);
    // legend
    var lg = svg.append("g").attr("class", "th-legend").attr("transform", "translate(" + m.l + "," + (m.t - (compact ? 30 : 16)) + ")");
    var lx = 0, ly = 0;
    [["circle", true, "pooled, un-aged"], ["circle", false, "pooled, aged"], ["rect", true, "team-rank, un-aged"], ["rect", false, "team-rank, aged"]].forEach(function (l, i) {
      if (compact && i === 2) { lx = 0; ly = 14; }
      if (l[0] === "circle") lg.append("circle").attr("cx", lx + 5).attr("cy", ly).attr("r", 4).attr("fill", l[1] ? "rgba(255,255,255,.8)" : "none").attr("stroke", "rgba(255,255,255,.8)").attr("stroke-width", 1.5);
      else lg.append("rect").attr("x", lx + 1).attr("y", ly - 4).attr("width", 8).attr("height", 8).attr("fill", l[1] ? "rgba(255,255,255,.8)" : "none").attr("stroke", "rgba(255,255,255,.8)").attr("stroke-width", 1.5);
      lg.append("text").attr("x", lx + 13).attr("y", ly + 3.5).text(compact ? l[2].replace("team-rank", "rank").replace("un-aged", "raw") : l[2]);
      lx += (compact ? 92 : 124);
    });
    var rows = [];
    D.rows.forEach(function (r) {
      var g = svg.append("g").attr("class", "th-row" + (r.ships ? " is-ship" : "")).attr("data-key", r.key);
      var cy = y(r.key) + y.bandwidth() / 2;
      var lab = g.append("text").attr("class", "th-rlab").attr("x", m.l - 10).attr("y", cy + 3.5).attr("text-anchor", "end")
        .text(compact ? r.label.replace("Kuminga, against the fill at the four (Cody Williams)", "Kuminga vs Williams").replace("Kuminga, if Beringer fills the four instead", "Kuminga vs Beringer").replace("DiVincenzo's Achilles, not a transaction", "DiVincenzo's Achilles").replace("The other departures, a bundle of seven", "Other departures (7)").replace("Depth signings and re-signings", "Depth deals") : r.label);
      var lo = Math.min(r.pooled_u, r.pooled_a, r.tr_u, r.tr_a), hi = Math.max(r.pooled_u, r.pooled_a, r.tr_u, r.tr_a);
      g.append("line").attr("class", "th-range").attr("x1", x(lo)).attr("x2", x(hi)).attr("y1", cy).attr("y2", cy);
      var col = r.ships ? (r.pooled_u < 0 ? "var(--status-error)" : "var(--accent-hover)") : "rgba(255,255,255,.7)";
      g.append("circle").attr("class", "th-mark").attr("cx", x(r.pooled_u)).attr("cy", cy).attr("r", 5.5).attr("fill", col).attr("stroke", col);
      g.append("circle").attr("class", "th-mark").attr("cx", x(r.pooled_a)).attr("cy", cy).attr("r", 5.5).attr("fill", "#050505").attr("stroke", col);
      g.append("rect").attr("class", "th-mark").attr("x", x(r.tr_u) - 4.5).attr("y", cy - 4.5).attr("width", 9).attr("height", 9).attr("fill", col).attr("stroke", col);
      g.append("rect").attr("class", "th-mark").attr("x", x(r.tr_a) - 4.5).attr("y", cy - 4.5).attr("width", 9).attr("height", 9).attr("fill", "#050505").attr("stroke", col);
      if (r.ships && !compact) g.append("text").attr("class", "th-ship-tag").attr("x", x(hi) + 10).attr("y", cy + 3).text("ships");
      var desc = "Pooled allocator: " + fmt(r.pooled_u) + " un-aged (" + r.pooled_u_sign.toLowerCase() + ", " + r.pooled_u_clear + " of 4 views clear the noise), " + fmt(r.pooled_a) + " aged (" + r.pooled_a_sign.toLowerCase() + ", " + r.pooled_a_clear + " of 4). Team-rank allocator: " + fmt(r.tr_u) + " un-aged, " + fmt(r.tr_a) + " aged. " + (r.ships ? "Ships: every cell agrees on the sign and clears the noise." : "Does not ship.");
      g.on("mouseenter", function () { tipAt(this, r.label, desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, r.label, desc); });
      rows.push({ g: g, r: r });
    });
    lastBuilt = { rows: rows, compact: compact };
    return lastBuilt;
  }
  function finalState(b) { clearPlayTimers(); b.rows.forEach(function (o) { o.g.classed("is-on", true); }); root.select(".th-hero-num").text(D.ball_txt); root.classed("is-landed", true); setCaption(CAPS[3], true); showReplay(); }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false);
    b.rows.forEach(function (o) { o.g.classed("is-on", false); });
    root.select(".th-hero-num").text("0.00"); setCaption(CAPS[0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    b.rows.forEach(function (o, i) { at(600 + i * 380, function () { o.g.classed("is-on", true); }); });
    at(600 + 2 * 380, function () { setCaption(CAPS[1]); tickText(root.select(".th-hero-num"), 0, parseFloat(D.ball_txt), 700, function (t) { return "+" + t.toFixed(2); }); root.classed("is-landed", true); });
    at(600 + 4 * 380 + 400, function () { setCaption(CAPS[2]); });
    at(600 + 9 * 380 + 400, function () { setCaption(CAPS[3]); showReplay(); });
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + C1.script(pid, js), ["v_ball_in_pooled_u", "v_reid_out_pooled_u", "v_A_c3_default_williams_pooled_u", "v_ddv_injury_pooled_u", "v_D_beringer_fills_pooled_u", "v_randle_out_pooled_u", "v_dosunmu_retained_pooled_u"]


# ================================================================== 3. the second creator
def viz_the_second_creator(S):
    chk = pd.read_csv(os.path.join(OUTS, "m3_primary_defender_check.csv"))
    chk = chk[chk.variant == "shipped"]
    n6 = pd.read_csv(os.path.join(OUTS, "n6_primary_defender.csv"))
    e3 = n6[(n6.window == "2023-26 pooled") & (n6.player == "Anthony Edwards") & (n6.role == "scorer")].iloc[0]
    ed = chk[chk.player == "Anthony Edwards"].iloc[0]
    assert "%.0f" % ed.percentile == S["e_pct_shipped"] and int(ed.pairings) == int(S["e_pairings"]) and int(ed.n_offenders) == int(S["e_n_off"])
    assert "%.0f" % e3.percentile == S["e_scorer_pct3"] and int(e3.n_reference) == int(S["k_scorer_ref"])
    wolves = [dict(player=str(x.player), pct=float(x.percentile), pairings=int(x.pairings), poss=float(x.poss), beyond=float(x.beyond_norm), z=float(x.z)) for _, x in chk.iterrows()]
    cs = pd.read_csv(os.path.join(OUTS, "m5_creation_shares.csv"))
    c26 = cs[cs.window == "2025-26"].set_index("player")
    assert "%.0f%%" % (100 * c26.loc["Anthony Edwards", "unast_share"]) == S["cr_edw"]
    assert "%.0f%%" % (100 * c26.loc["LaMelo Ball", "unast_share"]) == S["cr_ball"]
    assert "%.0f%%" % (100 * c26.loc["Anthony Edwards", "league_median"]) == S["cr_median"]
    creators = [dict(player=pl, share=float(c26.loc[pl, "unast_share"]), fgm=int(c26.loc[pl, "fgm"]), two=float(c26.loc[pl, "unast2"]), three=float(c26.loc[pl, "unast3"]), pct=float(c26.loc[pl, "league_pct"]))
                for pl in ("Anthony Edwards", "LaMelo Ball", "Jonathan Kuminga")]
    median = float(c26.loc["Anthony Edwards", "league_median"])
    uu = pd.read_csv(os.path.join(OUTS, "m5_unit_usage.csv"))
    kin = uu[uu.unit == "Kuminga in for Dosunmu"].iloc[0]
    assert "%.0f" % kin.league_pct == S["m5_kin_pct"] and "{:,}".format(int(kin.league_team_games)) == S["m5_league_fives"]
    units = [dict(unit=str(x.unit), players=str(x.players), usg=float(x.usg_sum), pct=float(x.league_pct), kind=str(x.kind)) for _, x in uu.iterrows()]
    league = dict(p10=float(kin.league_p10), median=float(kin.league_median), p90=float(kin.league_p90), p99=float(kin.league_p99), n=int(kin.league_team_games))
    data = dict(wolves=wolves, n_off=int(ed.n_offenders), ed_pct_txt=S["e_pct_shipped"], ed3_pct_txt=S["e_scorer_pct3"], ref3=int(e3.n_reference), pairings=int(ed.pairings),
                creators=creators, median=median, edw_txt=S["cr_edw"], ball_txt=S["cr_ball"], median_txt=S["cr_median"],
                units=units, league=league, kin_pct_txt=S["m5_kin_pct"], fives_txt=S["m5_league_fives"])
    pid = "the-second-creator"
    p = "#viz-%s" % pid
    toolbar = ('<div class="th-toggle" role="group" aria-label="Which panel"><button type="button" data-tab="suppress" class="is-on">What a defense takes</button>'
               '<button type="button" data-tab="create">Who creates his own shot</button><button type="button" data-tab="usage">Ball to go around</button></div>')
    stage = '<svg class="th-svg" role="img" aria-label="The case for a second creator"></svg>'
    html = C1.chrome_html(pid, "The second creator", "why LaMelo is here", "percentile", "of the 150 top scorers, what his primary defender takes off him: almost nobody loses more",
                          "Panel one: each Wolf's percentile among the league's 150 highest-volume scorers for points per possession beyond the norm against his primary defender, last season, regular season and playoffs; lower is more suppressed. "
                          "Panel two: the share of a player's makes that were unassisted, against the league median. Panel three: a starting five's combined usage against every starting five in the league's last three seasons. Hover a mark.",
                          extra_stage=stage, toolbar=toolbar, hero_num="")
    css = C1.chrome_css(pid, "var(--accent-default)") + """
  %(p)s .th-svg { width: 100%%; height: 250px; display: block; }
  %(p)s.is-compact .th-svg { height: 270px; }
  %(p)s .th-hero-num { font-size: 44px; }
  %(p)s .th-axis text { font: 500 10px var(--family-mono); fill: var(--text-tertiary); }
  %(p)s .th-axis line, %(p)s .th-axis path { stroke: rgba(255,255,255,.12); }
  %(p)s .th-mark { cursor: pointer; opacity: 0; transition: opacity 320ms ease; }
  %(p)s .th-mark.is-on { opacity: 1; }
  %(p)s .th-mlab { font: 600 10.5px var(--family-sans); fill: var(--text-secondary); pointer-events: none; }
  %(p)s .th-mlab.is-ant { fill: var(--text-primary); font-weight: 700; }
  %(p)s .th-bar { cursor: pointer; }
  %(p)s .th-ref { stroke: rgba(255,255,255,.5); stroke-width: 1.5; stroke-dasharray: 4 3; }
  %(p)s .th-ref-lab { font: 700 9.5px var(--family-mono); fill: var(--text-tertiary); letter-spacing: .04em; text-transform: uppercase; }
  %(p)s .th-note { font: 600 10.5px var(--family-sans); fill: var(--text-secondary); }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var CAPS = {
    suppress: ["Take the league's " + D.n_off + " highest-volume scorers and ask what a primary defender takes off each of them.", "Ant sits at the " + D.ed_pct_txt + "st percentile: almost nobody in the league loses more to his primary defender. Over three seasons and " + D.ref3 + " scorers, he is the lowest of all of them."],
    create: ["Last season " + D.edw_txt + " of Ant's makes were unassisted. LaMelo, in Charlotte, was at " + D.ball_txt + ". The league median is " + D.median_txt + ".", "Two of the most self-created scorers in basketball, in one backcourt. The base rate says the one already there gives up shots, not efficiency."],
    usage: ["A starting five with Kuminga in it sits at the " + D.kin_pct_txt + "th percentile of " + D.fives_txt + " starting fives for combined usage.", "Somebody is going to give up shots. Somebody always does."]
  };
  var tab = "suppress";
  function build() {
    var compact = compactNow();
    var svg = root.select(".th-svg"); svg.selectAll("*").remove();
    var W = Math.max(320, Math.min(720, rootNode.clientWidth || 640)) - 26, H = compact ? 270 : 250;
    svg.attr("viewBox", "0 0 " + W + " " + H);
    var marks = [];
    if (tab === "suppress") {
      var m = { t: 56, r: 20, b: 40, l: 20 };
      var x = d3.scaleLinear().domain([0, 100]).range([m.l, W - m.r]);
      var ax = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m.b) + ")").call(d3.axisBottom(x).tickValues([0, 25, 50, 75, 100]).tickFormat(function (v) { return v + "th"; }));
      ax.select(".domain").remove();
      svg.append("text").attr("class", "th-ref-lab").attr("x", x(0)).attr("y", m.t - 10).attr("text-anchor", "start").text("most suppressed");
      svg.append("text").attr("class", "th-ref-lab").attr("x", x(100)).attr("y", m.t - 10).attr("text-anchor", "end").text("least");
      svg.append("line").attr("class", "th-ref").attr("x1", m.l).attr("x2", W - m.r).attr("y1", (H - m.b + m.t) / 2).attr("y2", (H - m.b + m.t) / 2);
      svg.append("text").attr("class", "th-ref-lab").attr("x", x(50)).attr("y", m.t - 30).attr("text-anchor", "middle").text("percentile among " + D.n_off + " top scorers, last season");
      var cy = (H - m.b + m.t) / 2;
      var sorted = D.wolves.slice().sort(function (a, b) { return a.pct - b.pct; });
      sorted.forEach(function (w, i) {
        var isAnt = w.player === "Anthony Edwards";
        var g = svg.append("g").attr("class", "th-mark");
        g.append("circle").attr("cx", x(w.pct)).attr("cy", cy).attr("r", isAnt ? 10 : 7).attr("fill", isAnt ? "var(--accent-default)" : "rgba(255,255,255,.14)").attr("stroke", isAnt ? "var(--accent-hover)" : "rgba(255,255,255,.45)").attr("stroke-width", isAnt ? 2 : 1);
        var up = i % 2 === 0;
        var anchor = w.pct < 15 ? "start" : (w.pct > 85 ? "end" : "middle");
        g.append("text").attr("class", "th-mlab" + (isAnt ? " is-ant" : "")).attr("x", x(w.pct) + (anchor === "start" ? -8 : (anchor === "end" ? 8 : 0))).attr("y", up ? cy - 16 : cy + 24).attr("text-anchor", anchor).text((compact ? w.player.replace(/^(\w)\w+ /, "$1. ") : w.player) + (isAnt ? ", " + D.ed_pct_txt + "st" : ""));
        var desc = w.pairings + " primary defenders, " + Math.round(w.poss) + " possessions. " + (w.beyond > 0 ? "+" : "") + w.beyond.toFixed(3) + " points per possession beyond the norm, z " + w.z.toFixed(2) + ". Percentile " + w.pct.toFixed(1) + " of " + D.n_off + ".";
        g.on("mouseenter", function () { tipAt(this, w.player, desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, w.player, desc); });
        marks.push(g);
      });
      // the three-season note
      var g3 = svg.append("g").attr("class", "th-mark");
      g3.append("text").attr("class", "th-note").attr("x", x(50)).attr("y", H - 6).attr("text-anchor", "middle").text(compact ? "Three seasons, " + D.ref3 + " scorers: Ant is the lowest." : "Widen it to three seasons and " + D.ref3 + " scorers and Ant is the lowest of all of them (" + D.ed3_pct_txt + "th percentile).");
      marks.push(g3);
    } else if (tab === "create") {
      var m2 = { t: 20, r: 70, b: 30, l: compact ? 96 : 130 };
      var names = D.creators.map(function (c) { return c.player; }).concat(["League median"]);
      var y = d3.scaleBand().domain(names).range([m2.t, H - m2.b]).paddingInner(0.35);
      var x2 = d3.scaleLinear().domain([0, 0.75]).range([m2.l, W - m2.r]);
      var ax2 = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m2.b) + ")").call(d3.axisBottom(x2).ticks(5).tickFormat(function (v) { return Math.round(v * 100) + "%"; }).tickSize(-(H - m2.b - m2.t)));
      ax2.select(".domain").remove();
      D.creators.concat([{ player: "League median", share: D.median, median: true }]).forEach(function (c) {
        var g = svg.append("g").attr("class", "th-mark th-bar");
        var col = c.median ? "rgba(255,255,255,.3)" : (c.player === "Anthony Edwards" ? "var(--accent-default)" : (c.player === "LaMelo Ball" ? "var(--accent-hover)" : "rgba(255,255,255,.55)"));
        g.append("rect").attr("x", x2(0)).attr("y", y(c.player)).attr("width", x2(c.share) - x2(0)).attr("height", y.bandwidth()).attr("rx", 3).attr("fill", col);
        g.append("text").attr("class", "th-mlab").attr("x", m2.l - 8).attr("y", y(c.player) + y.bandwidth() / 2 + 3.5).attr("text-anchor", "end").text(compact ? c.player.replace(/^(\w)\w+ /, "$1. ") : c.player);
        g.append("text").attr("class", "th-mlab is-ant").attr("x", x2(c.share) + 6).attr("y", y(c.player) + y.bandwidth() / 2 + 3.5).text(Math.round(c.share * 100) + "%");
        if (!c.median) {
          var desc = c.fgm + " makes last season, " + Math.round(c.share * 100) + "% unassisted: " + Math.round(c.two * 100) + "% of his twos and " + Math.round(c.three * 100) + "% of his threes. League percentile " + c.pct.toFixed(0) + ".";
          g.on("mouseenter", function () { tipAt(this, c.player, desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, c.player, desc); });
        }
        marks.push(g);
      });
    } else {
      var m3 = { t: 60, r: 20, b: 40, l: 20 };
      var x3 = d3.scaleLinear().domain([0.85, 1.25]).range([m3.l, W - m3.r]);
      var cy3 = (H - m3.b + m3.t) / 2;
      var ax3 = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m3.b) + ")").call(d3.axisBottom(x3).ticks(5).tickFormat(function (v) { return v.toFixed(2); }));
      ax3.select(".domain").remove();
      svg.append("text").attr("class", "th-ref-lab").attr("x", x3(1.05)).attr("y", m3.t - 34).attr("text-anchor", "middle").text("combined usage of a starting five, " + D.fives_txt + " fives, 2023-26");
      [["p10", "10th"], ["median", "median"], ["p90", "90th"], ["p99", "99th"]].forEach(function (r) {
        svg.append("line").attr("class", "th-ref").attr("x1", x3(D.league[r[0]])).attr("x2", x3(D.league[r[0]])).attr("y1", m3.t - 8).attr("y2", H - m3.b);
        svg.append("text").attr("class", "th-ref-lab").attr("x", x3(D.league[r[0]])).attr("y", m3.t - 12).attr("text-anchor", "middle").text(r[1]);
      });
      D.units.forEach(function (u, i) {
        var g = svg.append("g").attr("class", "th-mark");
        var isKin = u.unit.indexOf("Kuminga in") === 0;
        var isObs = u.kind === "observed";
        var yy = cy3 + (i - 1.5) * (compact ? 22 : 26);
        g.append("circle").attr("cx", x3(u.usg)).attr("cy", yy).attr("r", isKin ? 9 : 6).attr("fill", isKin ? "var(--accent-default)" : (isObs ? "rgba(255,255,255,.35)" : "rgba(255,255,255,.14)")).attr("stroke", isKin ? "var(--accent-hover)" : "rgba(255,255,255,.45)").attr("stroke-width", isKin ? 2 : 1);
        var lab = isKin ? "With Kuminga, " + D.kin_pct_txt + "th" : (isObs ? "Last season's five" : u.unit.replace("Projected top five by minutes", "Projected five").replace("Highest-usage five with a centre", "Highest-usage five"));
        g.append("text").attr("class", "th-mlab" + (isKin ? " is-ant" : "")).attr("x", x3(u.usg) + (isKin ? 14 : 10)).attr("y", yy + 3.5).text(compact ? lab.replace("Last season's five", "Last season") : lab);
        var desc = u.players + ". Usage sum " + u.usg.toFixed(3) + ", the " + u.pct.toFixed(0) + "th percentile of " + D.fives_txt + " starting fives.";
        g.on("mouseenter", function () { tipAt(this, u.unit, desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, u.unit, desc); });
        marks.push(g);
      });
    }
    root.selectAll(".th-toggle button").on("click", function () {
      tab = this.getAttribute("data-tab");
      root.selectAll(".th-toggle button").classed("is-on", function () { return this.getAttribute("data-tab") === tab; });
      clearPlayTimers(); lastBuilt = build(); finalState(lastBuilt);
    });
    lastBuilt = { marks: marks, compact: compact };
    return lastBuilt;
  }
  function heroFor() {
    if (tab === "suppress") { root.select(".th-hero-num").text(D.ed_pct_txt + "st"); root.select(".th-hero-unit").text("percentile"); root.select(".th-hero-label").text("of the " + D.n_off + " top scorers, what his primary defender takes off him: almost nobody loses more"); }
    else if (tab === "create") { root.select(".th-hero-num").text(D.edw_txt); root.select(".th-hero-unit").text("of Ant's makes unassisted"); root.select(".th-hero-label").text("LaMelo " + D.ball_txt + ", the league median " + D.median_txt); }
    else { root.select(".th-hero-num").text(D.kin_pct_txt + "th"); root.select(".th-hero-unit").text("percentile"); root.select(".th-hero-label").text("the five with Kuminga, for combined usage, of " + D.fives_txt + " starting fives"); }
  }
  function finalState(b) { clearPlayTimers(); b.marks.forEach(function (g) { g.classed("is-on", true); }); heroFor(); root.classed("is-landed", true); setCaption(CAPS[tab][1], true); showReplay(); }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false);
    b.marks.forEach(function (g) { g.classed("is-on", false); });
    root.select(".th-hero-num").text(""); setCaption(CAPS[tab][0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    b.marks.forEach(function (g, i) { at(600 + i * 260, function () { g.classed("is-on", true); }); });
    at(600 + b.marks.length * 260 + 300, function () { heroFor(); root.classed("is-landed", true); setCaption(CAPS[tab][1]); });
    at(600 + b.marks.length * 260 + 1500, showReplay);
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + C1.script(pid, js), ["e_pct_shipped", "e_pairings", "e_n_off", "e_scorer_pct3", "k_scorer_ref", "cr_edw", "cr_ball", "cr_median", "m5_kin_pct", "m5_league_fives"]


# ================================================================== 4. the eight tests
def viz_the_eight_tests(S):
    n3 = pd.read_csv(os.path.join(OUTS, "n3_translation_tests.csv"))
    lo = n3[n3["sample"] == "longer 2014-26"]
    LAB = {"rim_rate": "rim rate", "fg3a_rate": "three-point rate", "pace": "pace", "opp_tov_rate": "turnovers forced", "oreb_rate": "offensive rebounding", "size": "size", "top3": "top-three minutes share", "def_share": "defence share (\"defense travels\")"}
    rows = [dict(feature=str(x.feature), label=LAB[str(x.feature)], coef=float(x.coef), se=float(x.coef_se), mde=float(x.mde80), p=float(x.perm_p), translates=bool(x.translates)) for _, x in lo.iterrows()]
    n_series = int(lo.n_series.iloc[0])
    assert str(n_series) == S["n3_series"] and int(S["n3_n_translating"]) == sum(r["translates"] for r in rows) and int(S["n3_n_features"]) == len(rows)
    ds = [r for r in rows if r["feature"] == "def_share"][0]
    assert "%+.2f" % ds["coef"] == S["ds_coef"], (ds["coef"], S["ds_coef"])
    data = dict(rows=rows, n_series=n_series, n_feat=len(rows), n_trans=sum(r["translates"] for r in rows), ds_txt=S["ds_coef"].replace("+", ""))
    pid = "the-eight-tests"
    p = "#viz-%s" % pid
    stage = '<svg class="th-svg" role="img" aria-label="Eight regular-season traits tested on playoff series"></svg>'
    html = C1.chrome_html(pid, "The eight tests", "what translates to the playoffs", "of " + str(len(rows)) + " traits predicted a series", "once you knew how good the two teams were, none of the things we argue about did",
                          "Each row is one regular-season trait, tested on " + str(n_series) + " playoff series since 2014 for whether the team with more of it beat the series margin the two teams' quality already predicted. "
                          "The mark is the estimated points per game per standard deviation of the trait; the bar is two standard errors either side; the faint dashed span is the smallest effect the sample could detect, the bar we set in advance for calling a trait real. Seven of the eight cross zero; defence share doesn't, and it points the wrong way for the cliché, but it sits inside that span, so it doesn't clear the bar either. Hover for the permutation p-value.",
                          extra_stage=stage, hero_num="")
    css = C1.chrome_css(pid, "var(--status-info)") + """
  %(p)s .th-svg { width: 100%%; height: 330px; display: block; }
  %(p)s .th-hero-num { font-size: 48px; }
  %(p)s .th-axis text { font: 500 10px var(--family-mono); fill: var(--text-tertiary); }
  %(p)s .th-axis line, %(p)s .th-axis path { stroke: rgba(255,255,255,.12); }
  %(p)s .th-zero { stroke: rgba(255,255,255,.5); stroke-width: 1.2; }
  %(p)s .th-row { cursor: pointer; opacity: 0; transition: opacity 320ms ease; }
  %(p)s .th-row.is-on { opacity: 1; }
  %(p)s .th-rlab { font: 600 11px var(--family-sans); fill: var(--text-secondary); }
  %(p)s.is-compact .th-rlab { font-size: 9.5px; }
  %(p)s .th-row.is-ds .th-rlab { fill: var(--text-primary); font-weight: 700; }
  %(p)s .th-ci { stroke: rgba(255,255,255,.55); stroke-width: 2; }
  %(p)s .th-row.is-ds .th-ci { stroke: var(--status-info); }
  %(p)s .th-pt { fill: rgba(255,255,255,.85); }
  %(p)s .th-row.is-ds .th-pt { fill: var(--status-info); }
  %(p)s .th-mde { stroke: rgba(255,255,255,.18); stroke-width: 1; stroke-dasharray: 3 3; }
  %(p)s .th-note { font: 600 10.5px var(--family-sans); fill: var(--text-secondary); }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var CAPS = [
    "Eight regular-season traits that are supposed to translate to the playoffs, the ones you hear every May.",
    "Tested on " + D.n_series + " playoff series since 2014, holding how good the two teams were fixed.",
    "Zero of the eight predicted who won by the bar we set in advance. Not the three-point rate. Not the size. Not the pace.",
    "\"Defense travels\" isn't supported, and the estimate points the other way: " + D.ds_txt + " points a game per standard deviation of defensive lean, inside the smallest effect the sample could detect, so we don't call it real."
  ];
  function fmt(v) { return (v > 0 ? "+" : "") + v.toFixed(2); }
  function build() {
    var compact = compactNow();
    var svg = root.select(".th-svg"); svg.selectAll("*").remove();
    var W = Math.max(320, Math.min(720, rootNode.clientWidth || 640)) - 26, H = 330;
    var m = { t: 16, r: 16, b: 44, l: compact ? 120 : 210 };
    svg.attr("viewBox", "0 0 " + W + " " + H);
    var ext = d3.max(D.rows, function (r) { return Math.max(Math.abs(r.coef) + 1.96 * r.se, r.mde); }) + 0.2;
    var x = d3.scaleLinear().domain([-ext, ext]).range([m.l, W - m.r]);
    var y = d3.scaleBand().domain(D.rows.map(function (r) { return r.feature; })).range([m.t, H - m.b]).paddingInner(0.4);
    var ax = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m.b) + ")").call(d3.axisBottom(x).ticks(compact ? 3 : 7).tickFormat(fmt).tickSize(-(H - m.b - m.t)));
    ax.select(".domain").remove();
    svg.append("text").attr("class", "th-note").attr("x", (m.l + W - m.r) / 2).attr("y", H - 6).attr("text-anchor", "middle").text(compact ? "points per game per SD of the trait" : "playoff points per game per standard deviation of the trait, beyond what team quality predicts");
    svg.append("line").attr("class", "th-zero").attr("x1", x(0)).attr("x2", x(0)).attr("y1", m.t).attr("y2", H - m.b);
    var rows = [];
    D.rows.forEach(function (r) {
      var g = svg.append("g").attr("class", "th-row" + (r.feature === "def_share" ? " is-ds" : ""));
      var cy = y(r.feature) + y.bandwidth() / 2;
      g.append("text").attr("class", "th-rlab").attr("x", m.l - 10).attr("y", cy + 3.5).attr("text-anchor", "end").text(compact ? r.label.replace(" (\"defense travels\")", "").replace("top-three minutes share", "top-three share") : r.label);
      g.append("line").attr("class", "th-mde").attr("x1", x(-r.mde)).attr("x2", x(r.mde)).attr("y1", cy).attr("y2", cy);
      g.append("line").attr("class", "th-ci").attr("x1", x(r.coef - 1.96 * r.se)).attr("x2", x(r.coef + 1.96 * r.se)).attr("y1", cy).attr("y2", cy);
      g.append("circle").attr("class", "th-pt").attr("cx", x(r.coef)).attr("cy", cy).attr("r", 5);
      var desc = "Estimate " + fmt(r.coef) + " points a game per standard deviation, standard error " + r.se.toFixed(2) + ", permutation p " + r.p.toFixed(3) + ". Smallest effect this sample could detect: " + r.mde.toFixed(2) + " (the faint dashed span). " + (r.translates ? "Translates." : "Does not translate.");
      g.on("mouseenter", function () { tipAt(this, r.label, desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, r.label, desc); });
      rows.push(g);
    });
    lastBuilt = { rows: rows, compact: compact };
    return lastBuilt;
  }
  function finalState(b) { clearPlayTimers(); b.rows.forEach(function (g) { g.classed("is-on", true); }); root.select(".th-hero-num").text(D.n_trans); root.classed("is-landed", true); setCaption(CAPS[3], true); showReplay(); }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false);
    b.rows.forEach(function (g) { g.classed("is-on", false); }); root.select(".th-hero-num").text(""); setCaption(CAPS[0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    at(1200, function () { setCaption(CAPS[1]); });
    b.rows.forEach(function (g, i) { at(1800 + i * 300, function () { g.classed("is-on", true); }); });
    at(1800 + b.rows.length * 300 + 200, function () { setCaption(CAPS[2]); root.select(".th-hero-num").text(D.n_trans); root.classed("is-landed", true); });
    at(1800 + b.rows.length * 300 + 2600, function () { setCaption(CAPS[3]); showReplay(); });
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + C1.script(pid, js), ["n3_series", "n3_n_translating", "n3_n_features", "ds_coef"]


# ================================================================== 5. model vs market
def viz_model_vs_market(S):
    M = pd.read_csv(os.path.join(OUTS, "market_devig_2026_27.csv"))
    pre = pd.read_csv(os.path.join(OUTS, ".pre_refit_snapshot", "market_devig_2026_27.csv")).set_index("team_abbr")
    rows = []
    for _, x in M.iterrows():
        rows.append(dict(abbr=x.team_abbr, team=x.team, market=float(x.market_pct), model=float(x.model_pct), mrank=int(x.market_rank), rank=int(x.model_rank),
                         views=dict(consensus=100 * float(x.consensus), rapm=100 * float(x.rapm), box=100 * float(x.box), darko=100 * float(x.darko))))
    by = {r["abbr"]: r for r in rows}
    assert pct2(by["MIN"]["model"]) == S["title"] and pct2(by["MIN"]["market"]) == S["mkt_min"]
    assert pct2(by["BOS"]["model"]) == S["model_bos"] and pct2(by["BOS"]["market"]) == S["mkt_bos"]
    assert pct2(by["CHA"]["model"]) == S["model_cha"] and pct2(by["CHA"]["market"]) == S["mkt_cha"]
    cha_pre = float(pre.loc["CHA", "model_pct"])
    assert pct2(cha_pre) == S["cha_model_pre"]
    data = dict(rows=rows, cha_pre=cha_pre, cha_pre_txt=S["cha_model_pre"], cha_txt=S["model_cha"], mkt_cha_txt=S["mkt_cha"], title_txt=S["title"], mkt_min_txt=S["mkt_min"],
                bos_txt=S["model_bos"], mkt_bos_txt=S["mkt_bos"], ranks_txt=S["min_view_ranks"], bos_thr=S["bos_dec_threshold"], bos_game=S["bos_dec_game"], mkt_rank=S["mkt_min_rank"])
    pid = "model-vs-market"
    p = "#viz-%s" % pid
    stage = '<svg class="mo-svg" role="img" aria-label="Model against market, thirty teams"></svg>'
    html = C1.chrome_html(pid, "Model against market", "thirty teams, title odds", "", "Boston: the model against the market, the biggest disagreement on the board",
                          "Each dot is a team: the market's de-vigged title odds across, our model's across four ways of scoring players up. The diagonal is agreement. Log scales, because the favorites and the field are two orders apart. "
                          "The hollow Charlotte mark is where the model had the Hornets before a bug crediting baskets to the wrong team was fixed at the source and every player refit. Hover a team for the four views.",
                          extra_stage=stage, hero_num="")
    css = C1.chrome_css(pid, "var(--status-info)") + """
  %(p)s .mo-svg { width: 100%%; height: 360px; display: block; }
  %(p)s.is-compact .mo-svg { height: 340px; }
  %(p)s .mo-hero-num { font-size: 34px; }
  %(p)s.is-compact .mo-hero-num { font-size: 24px; }
  %(p)s .mo-axis text { font: 500 10px var(--family-mono); fill: var(--text-tertiary); }
  %(p)s .mo-axis line, %(p)s .mo-axis path { stroke: rgba(255,255,255,.12); }
  %(p)s .mo-diag { stroke: rgba(255,255,255,.4); stroke-width: 1.2; stroke-dasharray: 5 4; }
  %(p)s .mo-dot { cursor: pointer; opacity: 0; transition: opacity 300ms ease; }
  %(p)s .mo-dot.is-on { opacity: 1; }
  %(p)s .mo-lab { font: 700 10px var(--family-mono); pointer-events: none; opacity: 0; transition: opacity 300ms ease; }
  %(p)s .mo-lab.is-on { opacity: 1; }
  %(p)s .mo-axlab { font: 600 10px var(--family-sans); fill: var(--text-tertiary); }
  %(p)s .mo-ghost { fill: none; stroke: var(--status-error); stroke-width: 1.5; stroke-dasharray: 3 2; opacity: 0; transition: opacity 300ms ease; }
  %(p)s .mo-ghost.is-on { opacity: 1; }
  %(p)s .mo-drop { stroke: var(--status-error); stroke-width: 1.2; opacity: 0; transition: opacity 300ms ease; }
  %(p)s .mo-drop.is-on { opacity: 1; }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var CAPS = [
    "Thirty teams. The market's price across, the model's price up. On the diagonal, they agree.",
    "Charlotte first, because it's where the model was wrong in public: " + D.cha_pre_txt + " against a market of " + D.mkt_cha_txt + ", until the bug was found.",
    "Fixed at the source and refit, Charlotte comes down to " + D.cha_txt + ". Still above the market. An honest disagreement now.",
    "Minnesota: " + D.title_txt + " against the market's " + D.mkt_min_txt + ", sixth in the league by the market, " + D.ranks_txt + "th by the model.",
    "The biggest disagreement is Boston, " + D.bos_txt + " against " + D.mkt_bos_txt + ". If the Celtics are below " + D.bos_thr + " through game " + D.bos_game + ", the market was right and the model owes you an explanation."
  ];
  var NAMED = { MIN: "var(--accent-default)", BOS: "var(--status-info)", CHA: "var(--status-error)" };
  function build() {
    var compact = compactNow();
    var svg = root.select(".mo-svg"); svg.selectAll("*").remove();
    var W = Math.max(320, Math.min(720, rootNode.clientWidth || 640)) - 26, H = compact ? 340 : 360;
    var m = { t: 16, r: 18, b: 40, l: 46 };
    svg.attr("viewBox", "0 0 " + W + " " + H);
    var FLOOR = 0.03;
    var x = d3.scaleLog().domain([FLOOR, 40]).range([m.l, W - m.r]);
    var y = d3.scaleLog().domain([FLOOR, 40]).range([H - m.b, m.t]);
    var tv = [0.1, 0.3, 1, 3, 10, 30];
    function cx(r) { return x(Math.max(FLOOR, r.market)); }
    function cyv(v) { return y(Math.max(FLOOR, v)); }
    var ax = svg.append("g").attr("class", "mo-axis").attr("transform", "translate(0," + (H - m.b) + ")").call(d3.axisBottom(x).tickValues(tv).tickFormat(function (v) { return v + "%"; }).tickSize(-(H - m.b - m.t)));
    ax.select(".domain").remove();
    var ay = svg.append("g").attr("class", "mo-axis").attr("transform", "translate(" + m.l + ",0)").call(d3.axisLeft(y).tickValues(tv).tickFormat(function (v) { return v + "%"; }).tickSize(-(W - m.l - m.r)));
    ay.select(".domain").remove();
    svg.append("text").attr("class", "mo-axlab").attr("x", (m.l + W - m.r) / 2).attr("y", H - 6).attr("text-anchor", "middle").text("market, de-vigged title odds");
    svg.append("text").attr("class", "mo-axlab").attr("transform", "rotate(-90)").attr("x", -(m.t + H - m.b) / 2).attr("y", 12).attr("text-anchor", "middle").text("model, mean of four views");
    svg.append("line").attr("class", "mo-diag").attr("x1", x(FLOOR)).attr("y1", y(FLOOR)).attr("x2", x(40)).attr("y2", y(40));
    svg.append("text").attr("class", "mo-axlab").attr("x", m.l + 8).attr("y", m.t + 12).attr("text-anchor", "start").text("dots on the bottom edge: under " + FLOOR + "% in the model");
    var dots = {};
    D.rows.forEach(function (r) {
      var named = NAMED[r.abbr];
      var g = svg.append("g").attr("class", "mo-dot").attr("data-abbr", r.abbr);
      g.append("circle").attr("cx", cx(r)).attr("cy", cyv(r.model)).attr("r", named ? 8 : 5).attr("fill", named || "rgba(255,255,255,.14)").attr("stroke", named || "rgba(255,255,255,.4)").attr("stroke-width", named ? 2 : 1);
      var lab = svg.append("text").attr("class", "mo-lab").attr("x", cx(r) + (named ? 11 : 7)).attr("y", cyv(r.model) + 3.5).attr("fill", named || "var(--text-tertiary)").text(r.abbr).style("font-size", named ? "11px" : (compact ? "0" : "9px"));
      if (!named && !compact) lab.style("opacity", 0);
      var desc = "Market " + r.market.toFixed(2) + "% (rank " + r.mrank + "), model " + r.model.toFixed(2) + "% (rank " + r.rank + ")" + (r.model < FLOOR ? ", drawn at the floor" : "") + ". By view: consensus " + r.views.consensus.toFixed(2) + "%, RAPM " + r.views.rapm.toFixed(2) + "%, box score " + r.views.box.toFixed(2) + "%, DARKO " + r.views.darko.toFixed(2) + "%.";
      g.on("mouseenter", function () { tipAt(this, r.team, desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, r.team, desc); });
      dots[r.abbr] = { g: g, lab: lab, r: r, named: !!named };
    });
    var cha = dots["CHA"].r;
    var ghost = svg.append("circle").attr("class", "mo-ghost").attr("cx", cx(cha)).attr("cy", cyv(D.cha_pre)).attr("r", 8);
    var ghostLab = svg.append("text").attr("class", "mo-lab").attr("x", cx(cha) - 11).attr("y", cyv(D.cha_pre) + 3.5).attr("text-anchor", "end").attr("fill", "var(--status-error)").text("CHA before the fix");
    var drop = svg.append("line").attr("class", "mo-drop").attr("x1", cx(cha)).attr("x2", cx(cha)).attr("y1", cyv(D.cha_pre) + 8).attr("y2", cyv(cha.model) - 8);
    lastBuilt = { dots: dots, ghost: ghost, ghostLab: ghostLab, drop: drop, compact: compact };
    return lastBuilt;
  }
  function allOn(b, on) { Object.keys(b.dots).forEach(function (k) { b.dots[k].g.classed("is-on", on); if (b.dots[k].named || !b.compact) b.dots[k].lab.classed("is-on", on); }); }
  function heroBos() { root.select(".mo-hero-num").text(D.bos_txt + " vs " + D.mkt_bos_txt); }
  function finalState(b) { clearPlayTimers(); allOn(b, true); b.ghost.classed("is-on", true); b.ghostLab.classed("is-on", true); b.drop.classed("is-on", true); heroBos(); root.classed("is-landed", true); setCaption(CAPS[4], true); showReplay(); }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false); allOn(b, false); b.ghost.classed("is-on", false); b.ghostLab.classed("is-on", false); b.drop.classed("is-on", false);
    root.select(".mo-hero-num").text(""); setCaption(CAPS[0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    var order = D.rows.slice().sort(function (a, c) { return a.market - c.market; });
    order.forEach(function (r, i) { if (r.abbr === "CHA") return; at(500 + i * 60, function () { b.dots[r.abbr].g.classed("is-on", true); if (b.dots[r.abbr].named || !b.compact) b.dots[r.abbr].lab.classed("is-on", true); }); });
    at(2600, function () { setCaption(CAPS[1]); b.ghost.classed("is-on", true); b.ghostLab.classed("is-on", true); });
    at(4600, function () { setCaption(CAPS[2]); b.drop.classed("is-on", true); b.dots["CHA"].g.classed("is-on", true); b.dots["CHA"].lab.classed("is-on", true); });
    at(6800, function () { setCaption(CAPS[3]); });
    at(9000, function () { setCaption(CAPS[4]); heroBos(); root.classed("is-landed", true); });
    at(10200, showReplay);
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + C1.script(pid, js), ["title", "mkt_min", "model_bos", "mkt_bos", "model_cha", "mkt_cha", "cha_model_pre", "min_view_ranks", "bos_dec_threshold", "bos_dec_game"]


# ================================================================== 6. the path
def viz_the_path(S):
    sd = pd.read_csv(os.path.join(OUTS, "seed_distribution.csv"))
    ms = sd[(sd.team_abbr == "MIN") & (sd.field == "current")]
    seeds = [dict(seed=k, p=float(ms["p_seed%d" % k].mean())) for k in range(1, 11)]
    miss = float(ms.p_miss_11plus.mean())
    modal = max(seeds, key=lambda s: s["p"])
    assert "%dth" % modal["seed"] == S["n2_modal"] and "%.0f%%" % (100 * modal["p"]) == S["n2_modal_p"]
    top6 = float(ms.p_playoff_top6.mean())
    assert "%.0f%%" % (100 * top6) == S["n2_top6"]
    r1 = pd.read_csv(os.path.join(OUTS, "n2_round1_opponents.csv"))
    r1.columns = ["team", "p"]
    assert "%.0f%%" % (100 * (float(r1.set_index("team").p["SAS"]) + float(r1.set_index("team").p["OKC"]))) == S["n2_sas_okc"]
    opp = [dict(team=str(x.team), p=float(x.p)) for _, x in r1.iterrows() if float(x.p) >= 0.005]
    path = pd.read_csv(os.path.join(OUTS, "n2_path.csv"))
    r2 = float(path.r2.mean()); cond = float(path.title.mean() / path.r2.mean())
    assert "%.0f%%" % (100 * r2) == S["n2_r2"] and "%.1f%%" % (100 * cond) == S["n2_cond"]
    f = pd.read_csv(os.path.join(OUTS, "n5_fragility.csv"))
    f = f[(f.team == "MIN") & (f.basis == "unaged")]
    # D113: the three by impact contribution. Since D111 LaMelo is fourth by minutes and sits in
    # N5's sensitivity rows, so the rows are taken by player, not by the minutes set
    three = []
    for pl, slug in (("Anthony Edwards", "edwards"), ("Rudy Gobert", "gobert"), ("LaMelo Ball", "ball")):
        g = f[f.removed == pl]
        assert len(g) == 4, (pl, len(g))
        dr, sh = float(g.drop_pp.mean()), float(g.drop_pp.mean() / g.title_full.mean())
        assert "%.2f" % dr == S["n5_min_%s_drop" % slug] and "%.0f%%" % (100 * sh) == S["n5_min_%s_share" % slug], (pl, dr, sh)
        three.append(dict(player=pl, drops={str(x.fork): float(x.drop_pp) for _, x in g.iterrows()}, mean=dr, rel=sh,
                          share_txt=S["n5_min_%s_share" % slug], drop_txt=S["n5_min_%s_drop" % slug]))
    playin = modal["seed"] >= 7
    seed_label = ("the most likely seed: a play-in game, one night, everything on it" if playin
                  else "the most likely seed, and it skips the play-in")
    seed_line = ("The most likely version of April is a play-in game." if playin
                 else "The most likely version of April skips the play-in.")
    data = dict(seeds=seeds, miss=miss, modal=modal["seed"], modal_txt=S["n2_modal"], modal_p_txt=S["n2_modal_p"], top6_txt=S["n2_top6"], opp=opp, sas_okc_txt=S["n2_sas_okc"],
                r2_txt=S["n2_r2"], cond_txt=S["n2_cond"], three=three, seed_label=seed_label, seed_line=seed_line,
                sga_share_txt=S["n5_okc_gilgeousalexander_share"], sga_drop_txt=S["n5_okc_gilgeousalexander_drop"],
                wemby_share_txt=S["n5_sas_wembanyama_share"])
    pid = "the-path"
    p = "#viz-%s" % pid
    toolbar = ('<div class="th-toggle" role="group" aria-label="Which panel"><button type="button" data-tab="seeds" class="is-on">The seed</button>'
               '<button type="button" data-tab="r1">The first round</button><button type="button" data-tab="three">The three</button></div>')
    stage = '<svg class="th-svg" role="img" aria-label="Where the season is most likely to go"></svg>'
    html = C1.chrome_html(pid, "The path", "where April most likely starts", "", seed_label,
                          "Seeds: the share of simulated seasons ending at each seed, averaged over the four ways of scoring players, un-aged. First round: who Minnesota draws when it makes the field. The three: the points of title odds lost when Ant, Rudy or LaMelo misses the playoffs (seeding from the full roster), one mark per way of scoring players, with the share of the team's odds beside each name. Hover a bar.",
                          extra_stage=stage, toolbar=toolbar, hero_num="")
    css = C1.chrome_css(pid, "var(--accent-default)") + """
  %(p)s .th-svg { width: 100%%; height: 280px; display: block; }
  %(p)s .th-hero-num { font-size: 44px; }
  %(p)s .th-axis text { font: 500 10px var(--family-mono); fill: var(--text-tertiary); }
  %(p)s .th-axis line, %(p)s .th-axis path { stroke: rgba(255,255,255,.12); }
  %(p)s .th-bar { cursor: pointer; opacity: 0; transition: opacity 300ms ease; }
  %(p)s .th-bar.is-on { opacity: 1; }
  %(p)s .th-blab { font: 700 10px var(--family-mono); fill: var(--text-secondary); text-anchor: middle; pointer-events: none; }
  %(p)s .th-zone { fill: rgba(245,166,35,.08); }
  %(p)s .th-zone-lab { font: 700 9.5px var(--family-mono); fill: var(--status-warning); letter-spacing: .05em; text-transform: uppercase; }
  %(p)s .th-note { font: 600 10.5px var(--family-sans); fill: var(--text-secondary); }
  %(p)s .th-rlab { font: 600 11px var(--family-sans); fill: var(--text-secondary); }
  %(p)s .th-mean { stroke: rgba(255,255,255,.5); stroke-width: 1.5; stroke-dasharray: 4 3; }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var CAPS = {
    seeds: ["Run the season and ask where it ends. Each bar is the share of simulated seasons ending at that seed.", "The most likely seed is " + D.modal_txt + ", at " + D.modal_p_txt + ". A top-six seed, " + D.top6_txt + ". " + D.seed_line],
    r1: ["If they make the field, who's standing there?", "San Antonio or Oklahoma City is the first-round opponent " + D.sas_okc_txt + " of the time. They reach the second round " + D.r2_txt + " of the time, and from there win it all " + D.cond_txt + " of the time. The mountain is the first round."],
    three: ["Take Ant, Rudy or LaMelo out for the playoffs.", "About two thirds of the title odds go with each of them: " + D.three[0].share_txt + ", " + D.three[1].share_txt + ", " + D.three[2].share_txt + ". Oklahoma City and San Antonio each have one player like that, Shai at " + D.sga_share_txt + " and Wembanyama at " + D.wemby_share_txt + ". Three single points of failure where the contenders have one, on a smaller stake: Ant is worth " + D.three[0].drop_txt + " points, Shai " + D.sga_drop_txt + "."]
  };
  var tab = "seeds";
  var VIEWS = [["consensus", "var(--dataviz-2)"], ["rapm", "var(--dataviz-3)"], ["box", "var(--dataviz-6)"], ["darko", "var(--dataviz-4)"]];
  function build() {
    var compact = compactNow();
    var svg = root.select(".th-svg"); svg.selectAll("*").remove();
    var W = Math.max(320, Math.min(720, rootNode.clientWidth || 640)) - 26, H = 280;
    svg.attr("viewBox", "0 0 " + W + " " + H);
    var bars = [];
    if (tab === "seeds") {
      var m = { t: 30, r: 14, b: 34, l: 40 };
      var cats = D.seeds.map(function (s) { return String(s.seed); }).concat(["miss"]);
      var x = d3.scaleBand().domain(cats).range([m.l, W - m.r]).paddingInner(0.25);
      var y = d3.scaleLinear().domain([0, Math.max(0.4, d3.max(D.seeds, function (s) { return s.p; }) + 0.05)]).range([H - m.b, m.t]);
      var ay = svg.append("g").attr("class", "th-axis").attr("transform", "translate(" + m.l + ",0)").call(d3.axisLeft(y).ticks(4).tickFormat(function (v) { return Math.round(v * 100) + "%"; }).tickSize(-(W - m.l - m.r)));
      ay.select(".domain").remove();
      var ax = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m.b) + ")").call(d3.axisBottom(x).tickFormat(function (v) { return v === "miss" ? (compact ? "out" : "miss") : v; }));
      ax.select(".domain").remove();
      svg.append("text").attr("class", "th-note").attr("x", (m.l + W - m.r) / 2).attr("y", H - 4).attr("text-anchor", "middle").style("font-size", "9.5px").text("seed in the West");
      svg.append("rect").attr("class", "th-zone").attr("x", x("7") - x.step() * 0.125).attr("width", x.step() * 4).attr("y", m.t - 4).attr("height", H - m.b - m.t + 4);
      svg.append("text").attr("class", "th-zone-lab").attr("x", x("7") + x.step() * 1.875).attr("y", m.t - 8).attr("text-anchor", "middle").text("the play-in");
      D.seeds.concat([{ seed: "miss", p: D.miss }]).forEach(function (s) {
        var g = svg.append("g").attr("class", "th-bar");
        var isModal = s.seed === D.modal;
        g.append("rect").attr("x", x(String(s.seed))).attr("y", y(s.p)).attr("width", x.bandwidth()).attr("height", H - m.b - y(s.p)).attr("rx", 3).attr("fill", isModal ? "var(--accent-default)" : (String(s.seed) === "miss" ? "rgba(255,92,92,.5)" : "rgba(255,255,255,.22)"));
        if (s.p >= 0.02) g.append("text").attr("class", "th-blab").attr("x", x(String(s.seed)) + x.bandwidth() / 2).attr("y", y(s.p) - 4).text(Math.round(s.p * 100) + "%");
        var lab = s.seed === "miss" ? "Miss the play-in" : "Seed " + s.seed;
        var desc = (100 * s.p).toFixed(1) + "% of simulated seasons, averaged over the four ways of scoring players." + (isModal ? " The modal seed." : "");
        g.on("mouseenter", function () { tipAt(this, lab, desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, lab, desc); });
        bars.push(g);
      });
    } else if (tab === "r1") {
      var m2 = { t: 16, r: 60, b: 30, l: 60 };
      var y2 = d3.scaleBand().domain(D.opp.map(function (o) { return o.team; })).range([m2.t, H - m2.b]).paddingInner(0.3);
      var x2 = d3.scaleLinear().domain([0, Math.max(0.35, d3.max(D.opp, function (o) { return o.p; }) + 0.03)]).range([m2.l, W - m2.r]);
      var ax2 = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m2.b) + ")").call(d3.axisBottom(x2).ticks(5).tickFormat(function (v) { return Math.round(v * 100) + "%"; }).tickSize(-(H - m2.b - m2.t)));
      ax2.select(".domain").remove();
      D.opp.forEach(function (o) {
        var g = svg.append("g").attr("class", "th-bar");
        var top = o.team === "SAS" || o.team === "OKC";
        g.append("rect").attr("x", x2(0)).attr("y", y2(o.team)).attr("width", x2(o.p) - x2(0)).attr("height", y2.bandwidth()).attr("rx", 3).attr("fill", top ? "var(--status-error)" : "rgba(255,255,255,.22)");
        g.append("text").attr("class", "th-rlab").attr("x", m2.l - 8).attr("y", y2(o.team) + y2.bandwidth() / 2 + 3.5).attr("text-anchor", "end").text(o.team);
        g.append("text").attr("class", "th-blab").attr("x", x2(o.p) + 16).attr("y", y2(o.team) + y2.bandwidth() / 2 + 3.5).text(Math.round(o.p * 100) + "%");
        var desc = "First-round opponent in " + (100 * o.p).toFixed(1) + "% of the simulated seasons in which Minnesota makes the field.";
        g.on("mouseenter", function () { tipAt(this, o.team, desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, o.team, desc); });
        bars.push(g);
      });
      var gn = svg.append("g").attr("class", "th-bar");
      gn.append("text").attr("class", "th-note").attr("x", W - m2.r).attr("y", m2.t + 12).attr("text-anchor", "end").text("SAS or OKC: " + D.sas_okc_txt);
      bars.push(gn);
    } else {
      var m3 = { t: 24, r: 20, b: 34, l: compact ? 90 : 130 };
      var y3 = d3.scaleBand().domain(D.three.map(function (t) { return t.player; })).range([m3.t, H - m3.b]).paddingInner(0.4);
      var allv = []; D.three.forEach(function (t) { VIEWS.forEach(function (v) { allv.push(t.drops[v[0]]); }); });
      var x3 = d3.scaleLinear().domain([0, d3.max(allv) + 0.2]).range([m3.l, W - m3.r]);
      var ax3 = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m3.b) + ")").call(d3.axisBottom(x3).ticks(5).tickFormat(function (v) { return v.toFixed(1); }).tickSize(-(H - m3.b - m3.t)));
      ax3.select(".domain").remove();
      svg.append("text").attr("class", "th-note").attr("x", (m3.l + W - m3.r) / 2).attr("y", H - 4).attr("text-anchor", "middle").style("font-size", "9.5px").text("points of title odds lost when he misses the playoffs");
      D.three.forEach(function (t) {
        var g = svg.append("g").attr("class", "th-bar");
        var cy = y3(t.player) + y3.bandwidth() / 2;
        g.append("text").attr("class", "th-rlab").attr("x", m3.l - 10).attr("y", cy + 3.5).attr("text-anchor", "end").text((compact ? t.player.replace(/^(\w)\w+ /, "$1. ") : t.player) + ", " + t.share_txt);
        var lo = d3.min(VIEWS, function (v) { return t.drops[v[0]]; }), hi = d3.max(VIEWS, function (v) { return t.drops[v[0]]; });
        g.append("line").attr("x1", x3(lo)).attr("x2", x3(hi)).attr("y1", cy).attr("y2", cy).attr("stroke", "rgba(255,255,255,.25)").attr("stroke-width", 2);
        VIEWS.forEach(function (v) { g.append("circle").attr("cx", x3(t.drops[v[0]])).attr("cy", cy).attr("r", 5).attr("fill", v[1]).attr("stroke", "#050505").attr("stroke-width", 1.2); });
        var desc = "By view: consensus " + t.drops.consensus.toFixed(2) + ", RAPM " + t.drops.rapm.toFixed(2) + ", box score " + t.drops.box.toFixed(2) + ", DARKO " + t.drops.darko.toFixed(2) + " points of title odds; " + Math.round(100 * t.rel) + "% of the team's odds on average.";
        g.on("mouseenter", function () { tipAt(this, t.player + " out for the playoffs", desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, t.player + " out for the playoffs", desc); });
        bars.push(g);
      });
    }
    root.selectAll(".th-toggle button").on("click", function () {
      tab = this.getAttribute("data-tab");
      root.selectAll(".th-toggle button").classed("is-on", function () { return this.getAttribute("data-tab") === tab; });
      clearPlayTimers(); lastBuilt = build(); finalState(lastBuilt);
    });
    lastBuilt = { bars: bars, compact: compact };
    return lastBuilt;
  }
  function heroFor() {
    if (tab === "seeds") { root.select(".th-hero-num").text(D.modal_txt + ", " + D.modal_p_txt); root.select(".th-hero-unit").text(""); root.select(".th-hero-label").text(D.seed_label); }
    else if (tab === "r1") { root.select(".th-hero-num").text(D.sas_okc_txt); root.select(".th-hero-unit").text("of the time"); root.select(".th-hero-label").text("San Antonio or Oklahoma City in the first round"); }
    else { root.select(".th-hero-num").text(D.three[0].share_txt); root.select(".th-hero-unit").text("of the title odds"); root.select(".th-hero-label").text("lost if Ant misses the playoffs, and Rudy and LaMelo cost about the same: three single points of failure where the contenders have one"); }
  }
  function finalState(b) { clearPlayTimers(); b.bars.forEach(function (g) { g.classed("is-on", true); }); heroFor(); root.classed("is-landed", true); setCaption(CAPS[tab][1], true); showReplay(); }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false);
    b.bars.forEach(function (g) { g.classed("is-on", false); }); root.select(".th-hero-num").text(""); setCaption(CAPS[tab][0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    b.bars.forEach(function (g, i) { at(600 + i * 160, function () { g.classed("is-on", true); }); });
    at(600 + b.bars.length * 160 + 300, function () { heroFor(); root.classed("is-landed", true); setCaption(CAPS[tab][1]); });
    at(600 + b.bars.length * 160 + 1500, showReplay);
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + C1.script(pid, js), ["n2_modal", "n2_modal_p", "n2_top6", "n2_sas_okc", "n2_r2", "n2_cond", "n5_min_edwards_share", "n5_min_gobert_share", "n5_min_ball_share", "n5_min_edwards_drop", "n5_min_gobert_drop", "n5_min_ball_drop", "n5_okc_gilgeousalexander_share", "n5_okc_gilgeousalexander_drop", "n5_sas_wembanyama_share"]


# ================================================================== main
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    S = pd.read_csv(os.path.join(OUTS, "final_numbers.csv"), dtype=str).set_index("key").value
    with runlog.run("charts_part2", inputs={"sheet": "final_numbers.csv"}) as r:
        built = [viz_the_fork(S), viz_the_verdicts(S), viz_the_second_creator(S), viz_the_eight_tests(S), viz_model_vs_market(S), viz_the_path(S)]
        titles = {"the-fork": ("The fork", "The verdict against Cody Williams's minutes, on a slider."),
                  "the-verdicts": ("The verdicts", "Every move with its four cells; the ones that ship in green."),
                  "the-second-creator": ("The second creator", "What a defense takes off Ant, who creates his own shot, how much ball there is."),
                  "the-eight-tests": ("The eight tests", "Eight regular-season traits on 195 playoff series, all crossing zero."),
                  "model-vs-market": ("Model against market", "Thirty teams on a log-log scatter; Charlotte's fix, Minnesota, Boston."),
                  "the-path": ("The path", "The seed, the first-round opponent, and what losing each of the three costs.")}
        cards = []
        for pid, frag, keys in built:
            stem = pid.replace("-", "_")
            frag = "<!-- %s; sheet keys checked: %s -->\n" % (r.run_id, ", ".join(keys)) + frag
            fp = os.path.join(OUT_DIR, stem + "_fragment.html")
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(frag)
            with open(os.path.join(OUT_DIR, stem + "_preview.html"), "w", encoding="utf-8") as fh:
                fh.write(C1.preview(titles[pid][0], frag, stem + "_fragment.html"))
            r.output(fp)
            r.note("%s: %d bytes, keys %s" % (stem + "_fragment.html", len(frag.encode("utf-8")), ", ".join(keys)))
            cards.append('<a class="card" href="%s_preview.html"><div class="sec">Part 2</div><div class="title">%s</div><div class="sub">%s</div><div class="files">%s_fragment.html · place with {{viz:%s}}</div></a>'
                         % (stem, titles[pid][0], titles[pid][1], stem, pid))
        index = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>The Bet, Part 2: visuals</title>
<style>
  :root { --accent:#00843D; --bg-surface:#0E0E0E; --text:#fff; --text-2:rgba(255,255,255,.72); --text-3:rgba(255,255,255,.48); --border:rgba(255,255,255,.08); --sans:'Inter',system-ui,-apple-system,sans-serif; --mono:'JetBrains Mono',ui-monospace,Menlo,monospace; }
  body { margin:0; padding:48px 16px 80px; background:#000; color:var(--text); font-family:var(--sans); }
  .wrap { max-width:720px; margin:0 auto; }
  h1 { font-size:24px; margin:0 0 6px; }
  p.lead { color:var(--text-2); font-size:14px; line-height:1.6; margin:0 0 4px; }
  p.note { color:var(--text-3); font-size:12.5px; line-height:1.55; margin:0 0 28px; }
  a.card { display:block; text-decoration:none; background:var(--bg-surface); border:1px solid var(--border); border-radius:10px; padding:16px 18px; margin-bottom:12px; transition:border-color .15s ease, transform .15s ease; }
  a.card:hover { border-color:var(--accent); transform:translateY(-1px); }
  .sec { font:700 11px var(--mono); letter-spacing:.06em; text-transform:uppercase; color:var(--text-3); }
  .title { color:var(--text); font-size:17px; font-weight:600; margin:4px 0 2px; }
  .sub { color:var(--text-2); font-size:13px; line-height:1.45; }
  .files { color:var(--text-3); font:11px var(--mono); margin-top:6px; }
</style></head>
<body><div class="wrap">
  <h1>The Bet, Part 2: the visuals</h1>
  <p class="lead">Six fragments, built by <code>scripts/charts_part2.py</code> from the outputs and the sheet. Click a card to open its preview harness.</p>
  <p class="note">Each fragment is the publishable artifact (the host supplies D3 v7 and the design tokens). Every figure the visual states was checked against final_numbers.csv when the file was written; the run ID is the first line of each fragment.</p>
  %s
</div></body></html>
""" % "\n  ".join(cards)
        with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(index)
        r.output(os.path.join(OUT_DIR, "index.html"))


if __name__ == "__main__":
    main()
