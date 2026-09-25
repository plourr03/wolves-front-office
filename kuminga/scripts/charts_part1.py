#!/usr/bin/env python3
"""The Bet, Part 1: the four interactive visuals, built from the ledger and the sheet.

Each visual is a self-contained fragment in the Wolves to a T pattern (the host supplies D3 v7
and the design tokens): a chip, a narrated caption, a stage, a hero figure that lands, a replay
button, a method footnote and the watermark. A preview harness wraps each fragment for local
review, and index.html launches them. The article places one with `{{viz:<id>}}`.

  ins-and-outs   the ledger as a timeline: what went out and what came in, June to September,
                 salary bars for this season (toggle to the whole contract), the picks as rows,
                 a scrubber over the dates; hero is the two seven-player totals.
  the-wall       the Saturday arithmetic as a waterfall: the book against the second-apron hard
                 cap, Green out, Williams and Konchar in, Konchar stretched, Kuminga signed;
                 hero is the room left under the wall.
  the-market     the thirty teams' de-vigged title odds on a log strip, Minnesota inside the
                 five-way tie at sixth; hero is Minnesota's price.
  the-grades     every national letter grade on a timeline, whole-offseason grades against
                 trade-only grades, with the quote on hover; hero is the range.

DATA. `outputs/c4_ledger.csv`, `outputs/green_resolution.csv`, `outputs/market_devig_2026_27.csv`,
`data/c4_offseason_grades.csv`, `data/c4_transaction_sources.csv`. GATE: every hero figure is
checked against `outputs/final_numbers.csv` before a file is written, so the visuals cannot
disagree with the prose. Run ID and the sheet keys used are written into each fragment as a
comment.

    python kuminga/scripts/charts_part1.py
"""
from __future__ import annotations

import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import runlog  # noqa: E402
import bracket_sim as E         # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs", "charts", "part1")
DATA = os.path.join(REPO, "kuminga", "data")
OUTS = os.path.join(REPO, "kuminga", "outputs")
WATERMARK = "@WolvesToaT · Sep 2026"

TOKENS = """
  :root {
    --accent-default:#00843D; --accent-hover:#00A04A; --accent-subtle:rgba(0,132,61,.18);
    --dataviz-1:#00C457; --dataviz-2:#FFFFFF; --dataviz-3:#4A9EFF; --dataviz-4:#F5A623;
    --dataviz-5:#FF5C8A; --dataviz-6:#B388FF; --dataviz-7:#7CE7B8; --dataviz-8:#FFD166;
    --text-primary:#FFFFFF; --text-secondary:rgba(255,255,255,.72); --text-tertiary:rgba(255,255,255,.48);
    --border-subtle:rgba(255,255,255,.08); --border-default:rgba(255,255,255,.16);
    --status-error:#FF5C5C; --status-warning:#F5A623; --status-info:#4A9EFF; --status-success:#00A04A;
    --bg-surface:#0E0E0E; --bg-inset:#050505;
    --family-sans:'Inter',system-ui,-apple-system,sans-serif;
    --family-mono:'JetBrains Mono',ui-monospace,Menlo,monospace;
    --radius-sm:4px; --radius-md:10px;
  }
"""


def money(v):
    return "${:,.0f}".format(v)


def mil(v, d=1):
    return "$%.*fM" % (d, v / 1e6)


# ------------------------------------------------------------------ shared chrome
def chrome_css(pid, chip_color="var(--accent-default)"):
    p = "#viz-%s" % pid
    c = "." + pid[:2]
    return """
  %(p)s, %(p)s * { touch-action: manipulation; }
  %(p)s { font-family: var(--family-sans); color: var(--text-primary); position: relative; }
  %(p)s %(c)s-chip { display: inline-flex; align-items: center; gap: 8px; background: var(--bg-surface); border: 1px solid %(chip)s; border-radius: 999px; padding: 6px 14px; margin-bottom: 14px; font: 700 12px var(--family-sans); letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-primary); }
  %(p)s.is-compact %(c)s-chip { font-size: 10px; padding: 5px 10px; letter-spacing: .05em; gap: 6px; }
  %(p)s %(c)s-chip-dot { width: 8px; height: 8px; border-radius: 50%%; background: %(chip)s; }
  %(p)s %(c)s-chip-sep { color: var(--text-tertiary); font-weight: 400; }
  %(p)s %(c)s-chip-sub { font-weight: 500; color: var(--text-secondary); text-transform: none; letter-spacing: 0.02em; }
  %(p)s %(c)s-caption { font: 600 17px var(--family-sans); color: var(--text-primary); margin: 0 0 14px 0; min-height: 48px; line-height: 1.4; transition: opacity 260ms ease; }
  %(p)s.is-compact %(c)s-caption { font-size: 15px; }
  %(p)s %(c)s-stage { position: relative; background: var(--bg-inset); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 12px; }
  %(p)s %(c)s-tooltip { position: absolute; top: 0; left: 0; background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: 10px; padding: 9px 12px 10px; pointer-events: none; opacity: 0; transition: opacity 140ms ease; z-index: 10; min-width: 170px; max-width: 290px; box-shadow: 0 6px 20px rgba(0,0,0,0.45); }
  %(p)s %(c)s-tooltip.is-on { opacity: 1; }
  %(p)s %(c)s-tip-head { font: 700 12px var(--family-sans); color: var(--text-primary); margin-bottom: 4px; }
  %(p)s %(c)s-tip-desc { font: 500 12px var(--family-sans); color: var(--text-secondary); line-height: 1.35; }
  %(p)s %(c)s-hero { display: flex; flex-direction: column; align-items: center; margin: 18px 0 4px 0; position: relative; }
  %(p)s %(c)s-hero-line { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; justify-content: center; }
  %(p)s %(c)s-hero-num { font: 800 52px var(--family-mono); color: var(--text-primary); line-height: 1; letter-spacing: -0.03em; transition: color 320ms ease; }
  %(p)s.is-landed %(c)s-hero-num { color: %(chip)s; }
  %(p)s.is-compact %(c)s-hero-num { font-size: 38px; }
  %(p)s %(c)s-hero-unit { font: 600 14px var(--family-sans); color: var(--text-secondary); }
  %(p)s %(c)s-hero-label { font: 500 12px var(--family-sans); color: var(--text-tertiary); margin-top: 6px; text-align: center; }
  %(p)s %(c)s-replay { position: absolute; right: 0; top: 4px; background: rgba(255,255,255,.06); border: 1px solid var(--border-default); color: var(--text-secondary); font: 600 11px var(--family-sans); padding: 4px 9px; border-radius: 999px; cursor: pointer; opacity: 0; transition: opacity 200ms ease; }
  %(p)s %(c)s-replay.is-shown { opacity: 1; }
  %(p)s %(c)s-replay:hover { color: var(--text-primary); border-color: var(--text-secondary); }
  %(p)s %(c)s-foot { font: 400 12px var(--family-sans); color: var(--text-tertiary); line-height: 1.5; margin: 14px 0 0 0; }
  %(p)s %(c)s-watermark { font: 600 10px var(--family-mono); color: var(--text-tertiary); letter-spacing: .06em; margin-top: 6px; text-align: right; }
  %(p)s %(c)s-toggle { display: inline-flex; gap: 4px; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 999px; padding: 3px; margin: 0 0 10px 0; }
  %(p)s %(c)s-toggle button { background: transparent; border: 0; color: var(--text-tertiary); font: 600 11px var(--family-sans); padding: 4px 10px; border-radius: 999px; cursor: pointer; }
  %(p)s %(c)s-toggle button.is-on { background: rgba(255,255,255,.10); color: var(--text-primary); }
""" % dict(p=p, c=c, chip=chip_color)


def chrome_html(pid, chip_label, chip_sub, hero_unit, hero_label, foot, extra_stage="", toolbar="", hero_num="0"):
    c = pid[:2]
    return """<div id="viz-%(pid)s">
  <div class="%(c)s-chip" role="status">
    <span class="%(c)s-chip-dot"></span>
    <span class="%(c)s-chip-label">%(chip)s</span>
    <span class="%(c)s-chip-sep">·</span>
    <span class="%(c)s-chip-sub">%(sub)s</span>
  </div>
  <p class="%(c)s-caption" aria-live="polite"></p>
  %(toolbar)s
  <div class="%(c)s-stage">
    %(extra)s
    <div class="%(c)s-tooltip" role="tooltip">
      <div class="%(c)s-tip-head"></div>
      <div class="%(c)s-tip-desc"></div>
    </div>
  </div>
  <div class="%(c)s-hero">
    <div class="%(c)s-hero-line">
      <span class="%(c)s-hero-num">%(hero_num)s</span>
      <span class="%(c)s-hero-unit">%(unit)s</span>
    </div>
    <div class="%(c)s-hero-label">%(label)s</div>
    <button class="%(c)s-replay" type="button" aria-label="Replay">↺ Replay</button>
  </div>
  <p class="%(c)s-foot">%(foot)s</p>
  <div class="%(c)s-watermark">%(wm)s</div>
</div>""" % dict(pid=pid, c=c, chip=chip_label, sub=chip_sub, unit=hero_unit, label=hero_label, foot=foot,
                 extra=extra_stage, toolbar=toolbar, wm=WATERMARK, hero_num=hero_num)


# the shared runtime: scroll passthrough, timers, caption, tooltip, autoplay, resize
JS_COMMON = r"""
  var root = d3.select("#viz-__PID__");
  if (root.empty() || typeof d3 === "undefined") return;
  var rootNode = root.node();
  var C = "__C__";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (window.parent !== window) {
    rootNode.addEventListener("wheel", function (e) { if (e.ctrlKey || e.metaKey) return; try { window.parent.scrollBy(e.deltaX, e.deltaY); } catch (err) { window.parent.postMessage({type:"viz-scroll", deltaX:e.deltaX, deltaY:e.deltaY}, "*"); } }, { passive: true });
    var lastTouchY = null;
    rootNode.addEventListener("touchstart", function (e) { if (e.touches.length === 1) lastTouchY = e.touches[0].clientY; }, { passive: true });
    rootNode.addEventListener("touchmove", function (e) { if (e.touches.length !== 1 || lastTouchY === null) return; var yy = e.touches[0].clientY, dy = lastTouchY - yy; lastTouchY = yy; try { window.parent.scrollBy(0, dy); } catch (err) { window.parent.postMessage({type:"viz-scroll", deltaX:0, deltaY:dy}, "*"); } }, { passive: true });
  }
  var playTimers = [];
  function clearPlayTimers() { playTimers.forEach(function (t) { clearTimeout(t); }); playTimers = []; }
  function at(ms, fn) { playTimers.push(setTimeout(fn, ms)); }
  var capTimer = null;
  function setCaption(txt, instant) {
    var c = root.select("." + C + "-caption");
    if (capTimer) { clearTimeout(capTimer); capTimer = null; }
    if (instant) { c.style("opacity", 1).text(txt); return; }
    c.style("opacity", 0);
    capTimer = setTimeout(function () { capTimer = null; c.text(txt).style("opacity", 1); }, 220);
  }
  function showTooltip(head, desc, x, y) {
    var tip = root.select("." + C + "-tooltip");
    tip.select("." + C + "-tip-head").text(head);
    tip.select("." + C + "-tip-desc").html(desc);
    tip.classed("is-on", true);
    var stageEl = root.select("." + C + "-stage").node();
    var sRect = stageEl.getBoundingClientRect();
    var tipEl = tip.node();
    var tw = tipEl.offsetWidth, th = tipEl.offsetHeight;
    var px = x - tw / 2, py = y - th - 10;
    if (px < 4) px = 4;
    if (px + tw > sRect.width - 4) px = sRect.width - tw - 4;
    if (py < 4) py = y + 16;
    tipEl.style.left = px + "px"; tipEl.style.top = py + "px";
  }
  function tipAt(el, head, desc) {
    var stageEl = root.select("." + C + "-stage").node();
    var sRect = stageEl.getBoundingClientRect();
    var r = el.getBoundingClientRect();
    showTooltip(head, desc, r.left - sRect.left + r.width / 2, r.top - sRect.top);
  }
  function hideTooltip() { root.select("." + C + "-tooltip").classed("is-on", false); }
  function tickText(sel, from, to, duration, fmt) {
    var node = sel.node();
    if (reduceMotion || duration <= 0) { node.textContent = fmt(to); return; }
    d3.select(node).transition("hero").duration(duration).ease(d3.easeCubicOut)
      .tween("text", function () { var i = d3.interpolateNumber(from, to); return function (t) { node.textContent = fmt(i(t)); }; });
  }
  function showReplay() { root.select("." + C + "-replay").classed("is-shown", true); }
  function hideReplay() { root.select("." + C + "-replay").classed("is-shown", false); }
  var __resetOnly = false, __played = false, __lastW = rootNode.clientWidth || 0, lastBuilt = null;
  function compactNow() { var w = rootNode.clientWidth || 640; root.classed("is-compact", w < 480); return w < 480; }
  function __idle() { lastBuilt = build(); __resetOnly = true; play(lastBuilt); __resetOnly = false; }
  function __startOnce() { if (__played) return; __played = true; play(lastBuilt || build()); }
  root.select("." + C + "-replay").on("click", function () { if (lastBuilt) play(lastBuilt); });
  function boot() {
    if (reduceMotion) { lastBuilt = build(); finalState(lastBuilt); __played = true; }
    else {
      __idle();
      if ("IntersectionObserver" in window) {
        var io = new IntersectionObserver(function (entries) { entries.forEach(function (e) { if (e.isIntersecting && e.intersectionRatio >= 0.5) __startOnce(); }); }, { threshold: [0, 0.5, 1] });
        io.observe(rootNode);
      } else { __startOnce(); }
    }
    if (window.ResizeObserver) {
      var rt = null;
      new ResizeObserver(function () {
        if (rt) clearTimeout(rt);
        rt = setTimeout(function () {
          var w = rootNode.clientWidth || 0;
          if (Math.abs(w - __lastW) < 2) return;
          __lastW = w;
          lastBuilt = build();
          if (__played) finalState(lastBuilt); else __idle();
        }, 150);
      }).observe(rootNode);
    }
  }
"""


def script(pid, body):
    return "<script>\n(function () {\n" + JS_COMMON.replace("__PID__", pid).replace("__C__", pid[:2]) + body + "\n  boot();\n})();\n</script>"


def preview(title, fragment, fragment_name):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s, preview harness</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
%(tokens)s
  body { margin:0; padding:32px 16px 80px; background:#000; }
  .harness-note { max-width:720px; margin:0 auto 16px; color:rgba(255,255,255,.4); font:12px var(--family-sans); }
  .harness-toolbar { max-width:720px; margin:0 auto 12px; display:flex; gap:8px; align-items:center; color:rgba(255,255,255,.6); font:11px var(--family-sans); flex-wrap:wrap; }
  .harness-toolbar button { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.16); color:rgba(255,255,255,.85); padding:4px 10px; border-radius:6px; font:11px var(--family-sans); cursor:pointer; }
  .harness-toolbar button:hover { background:rgba(255,255,255,.12); }
  .harness-stage { max-width:720px; margin:0 auto; }
</style>
</head>
<body>
<div class="harness-note">Local preview harness. The publishable artifact is %(name)s.</div>
<div class="harness-toolbar">
  <span>Test widths:</span>
  <button onclick="document.querySelector('.harness-stage').style.maxWidth='720px'">720</button>
  <button onclick="document.querySelector('.harness-stage').style.maxWidth='480px'">480</button>
  <button onclick="document.querySelector('.harness-stage').style.maxWidth='360px'">360 (phone)</button>
  <button onclick="window.location.reload()">Hard reload</button>
</div>
<div class="harness-stage">
%(fragment)s
</div>
</body>
</html>
""" % dict(title=title, tokens=TOKENS, name=fragment_name, fragment=fragment)


# ================================================================== 1. ins and outs
def viz_ins_and_outs(S, sources):
    L = pd.read_csv(os.path.join(OUTS, "c4_ledger.csv"))
    src = sources.set_index("player") if "player" in sources.columns else None

    def terms(x):
        parts = []
        if pd.notna(x.contract_years) and pd.notna(x.contract_total):
            yrs = int(x.contract_years)
            parts.append("%d year%s, %s" % (yrs, "" if yrs == 1 else "s", money(x.contract_total)))
        if isinstance(x.options, str) and x.options:
            parts.append(x.options.replace("_", " "))
        return "; ".join(parts)

    def n_sources(name):
        try:
            v = sources[sources.player == name]
            return int(len(v))
        except Exception:
            return 0

    rows = []
    skip_players = {"Jules Bernard", "Stephen Thompson", "Rocco Zikarsky", "Zyon Pullin", "Enrique Freeman"}
    for _, x in L.iterrows():
        name = str(x.player)
        if name in skip_players:
            continue
        is_pick = bool(re.match(r"^\d{4} ", name))
        d = x.direction
        if d == "in then waived":
            continue
        if is_pick:
            if d == "in":            # the No. 33 selection is Isaiah Evans's row
                continue
            label = re.sub(r"\s*\(.*\)$", "", name)
            m = re.match(r"^(\d{4}) (first|second)-round (pick|swap right|draft rights)", name)
            year, rnd, kind = (m.group(1), m.group(2), m.group(3)) if m else (name[:4], "", "pick")
            if kind == "swap right":
                tag, short = "swap", "%s first, swap right" % year
                sub = "protected 6 through 30" if year == "2029" else ("on a pick San Antonio already holds a swap on" if year == "2030" else "unencumbered")
            elif kind == "draft rights":
                tag, short, sub = "rights", "Matteo Spagnolo, draft rights", "a 2022 second-rounder"
            elif rnd == "first":
                if year == "2026":
                    tag, short, sub = "rights", "No. 28 pick, Joshua Jefferson", "drafted June 23, sent with Randle"
                else:
                    tag, short, sub = "first", "%s first-round pick" % year, "unprotected"
            else:
                tag, short, sub = "second", "%s second-round pick" % year, ""
            rows.append(dict(name=short, direction="out", tag=tag, date=str(x.date), sal=None, total=None, sub=sub,
                             tip="To Charlotte in the four-team trade that closed July 10." + (" " + sub + "." if sub else "")))
            continue
        if name == "Joshua Jefferson":
            continue                 # carried as the No. 28 pick row
        if d == "retained" and pd.isna(x.salary_2026_27):
            if name == "Trey Kaufman-Renn":
                rows.append(dict(name="Trey Kaufman-Renn, rights", direction="kept", tag="rights", date=str(x.date), sal=None, total=None,
                                 sub="No. 59, unsigned", tip="The 59th pick chose a sixth college season and a lawsuit against the NCAA; Minnesota kept his rights."))
            continue
        sal = float(x.salary_2026_27) if pd.notna(x.salary_2026_27) else None
        tot = float(x.contract_total) if pd.notna(x.contract_total) else None
        how = str(x.how)
        tag = "player"
        if name == "LaMelo Ball":
            tag = "star"
        elif d == "out" and how == "waived":
            tag = "dead"
        elif d == "out" and "expired" in how:
            tag = "expired"
        tip = how.capitalize() + ", " + pd.to_datetime(x.date).strftime("%B %d").replace(" 0", " ") + "."
        t = terms(x)
        if t:
            tip += " " + t[0].upper() + t[1:] + "."
        if name == "John Konchar" and d == "out":
            tip = "Waived the afternoon he arrived and stretched: $2,055,000 a year against the cap through 2028-29."
        if name == "Josh Green" and d == "out":
            tip = "Traded to Utah with cash on August 29, seven weeks after he arrived, for Cody Williams and John Konchar."
        if name == "Joe Ingles":
            tip = "Contract expired; signed in Australia's NBL."
        ns = n_sources(name)
        if ns:
            tip += " %d source%s on file." % (ns, "" if ns == 1 else "s")
        sub = ""
        if sal is not None:
            sub = mil(sal, 2) if sal < 1e6 else mil(sal, 1)
        rows.append(dict(name=name, direction=("kept" if d == "retained" else d), tag=tag, date=str(x.date), sal=sal, total=tot,
                         sub=sub, tip=tip))
    rows.sort(key=lambda r: (r["date"], 0 if r["direction"] == "out" else 1, 1 if r["sal"] is None else 0))
    ins = [r for r in rows if r["direction"] == "in" and r["sal"] is not None]
    outs = [r for r in rows if r["direction"] == "out" and r["sal"] is not None]
    in_total, out_total = sum(r["sal"] for r in ins), sum(r["sal"] for r in outs)
    # gate: the two seven-player totals must be the sheet's
    assert money(in_total) == S["c4_in_total"], (money(in_total), S["c4_in_total"])
    assert money(out_total) == S["c4_out_total"], (money(out_total), S["c4_out_total"])
    assert len(ins) == int(S["c4_in_n"]) and len(outs) == int(S["c4_out_n"])
    stops = [
        ("2026-06-22", "June 22", "Dosunmu agrees: five years, $112 million, before the draft"),
        ("2026-06-25", "June 25", "The trade breaks: Randle and Reid out, Ball in"),
        ("2026-07-06", "July 6", "Conley to Boston, Anderson to Toronto, both on minimums"),
        ("2026-07-10", "July 10", "The four-team deal closes; the picks go to Charlotte"),
        ("2026-07-24", "July 24", "Phillips's option declined; he lands in Houston"),
        ("2026-08-29", "August 29", "The Saturday: Green out, Williams and Konchar in, Konchar waived and stretched"),
        ("2026-09-03", "September 3", "Kuminga signs for the taxpayer mid-level"),
    ]
    data = dict(rows=rows, stops=stops, in_total=in_total, out_total=out_total,
                in_total_m=mil(in_total), out_total_m=mil(out_total), n_in=len(ins), n_out=len(outs))
    assert S["c4_in_total_m"].replace(" million", "M") == mil(in_total) and S["c4_out_total_m"].replace(" million", "M") == mil(out_total), (S["c4_in_total_m"], S["c4_out_total_m"])
    pid = "ins-and-outs"
    p, c = "#viz-%s" % pid, ".in"
    toolbar = ('<div class="in-toggle" role="group" aria-label="Bar basis"><button type="button" data-basis="season" class="is-on">This season</button>'
               '<button type="button" data-basis="total">Whole contract</button></div>')
    stage = ('<div class="in-timeline"><div class="in-track"><div class="in-progress"></div></div><div class="in-stops"></div></div>'
             '<div class="in-grid"><div class="in-col in-out"><div class="in-head"><span>Out</span><span class="in-count"></span></div><div class="in-rows in-out-rows"></div></div>'
             '<div class="in-col in-in"><div class="in-head"><span>In</span><span class="in-count"></span></div><div class="in-rows in-in-rows"></div></div></div>'
             '<div class="in-kept"><div class="in-head"><span>Kept</span></div><div class="in-rows in-kept-rows"></div></div>')
    html = chrome_html(pid, "In and out", "June 13 to September 10", "", "Salary this season, seven players each way",
                       "Salaries are 2026-27 cap hits from the verified contract book; the picks are the four-team trade's terms as reported by Hoops Rumors and SI. "
                       "Green and Konchar appear on both sides because they came and went inside the same summer. Two-way and camp deals are left off. "
                       "Hover a row for the terms; drag or click the dates to move through the summer.",
                       extra_stage=stage, toolbar=toolbar, hero_num="$0.0M out · $0.0M in")
    css = chrome_css(pid, "var(--accent-default)") + """
  %(p)s .in-hero-num { font-size: 28px; }
  %(p)s.is-compact .in-hero-num { font-size: 20px; }
  %(p)s .in-hero { padding-right: 84px; align-items: flex-start; }
  %(p)s .in-hero-line { justify-content: flex-start; }
  %(p)s .in-timeline { margin: 4px 6px 14px; }
  %(p)s .in-track { position: relative; height: 4px; background: rgba(255,255,255,.10); border-radius: 2px; }
  %(p)s .in-progress { position: absolute; left: 0; top: 0; height: 100%%; width: 0; background: var(--accent-default); border-radius: 2px; transition: width 500ms cubic-bezier(.22,1,.36,1); }
  %(p)s .in-stops { position: relative; height: 46px; }
  %(p)s .in-stop.is-low .in-stop-lab { margin-top: 12px; }
  %(p)s .in-stop { position: absolute; top: -9px; transform: translateX(-50%%); cursor: pointer; text-align: center; width: 64px; }
  %(p)s .in-stop-dot { width: 10px; height: 10px; border-radius: 50%%; background: var(--bg-surface); border: 2px solid rgba(255,255,255,.3); margin: 0 auto 4px; transition: background 200ms ease, border-color 200ms ease; }
  %(p)s .in-stop.is-on .in-stop-dot { background: var(--accent-default); border-color: var(--accent-default); }
  %(p)s .in-stop-lab { font: 600 10px var(--family-mono); color: var(--text-tertiary); letter-spacing: .02em; white-space: nowrap; }
  %(p)s .in-stop.is-on .in-stop-lab { color: var(--text-primary); }
  %(p)s.is-compact .in-stop-lab { font-size: 8.5px; }
  %(p)s .in-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  %(p)s.is-compact .in-grid { grid-template-columns: 1fr; }
  %(p)s .in-col { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 12px; min-height: 120px; }
  %(p)s .in-out { border-top: 2px solid var(--status-error); }
  %(p)s .in-in { border-top: 2px solid var(--accent-default); }
  %(p)s .in-kept { margin-top: 12px; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-top: 2px solid rgba(255,255,255,.28); border-radius: 10px; padding: 10px 12px; }
  %(p)s .in-head { display: flex; align-items: baseline; justify-content: space-between; font: 700 11px var(--family-mono); letter-spacing: .06em; text-transform: uppercase; margin: 0 0 8px; }
  %(p)s .in-out .in-head { color: var(--status-error); }
  %(p)s .in-in .in-head { color: var(--accent-hover); }
  %(p)s .in-kept .in-head { color: var(--text-secondary); }
  %(p)s .in-count { font-size: 10px; color: var(--text-tertiary); text-transform: none; letter-spacing: 0; }
  %(p)s .in-row { display: grid; grid-template-columns: 148px 1fr 58px; gap: 8px; align-items: center; padding: 4px 4px; border-radius: 6px; opacity: 0; transform: translateY(6px); transition: opacity 360ms ease, transform 360ms ease, background 150ms ease; cursor: pointer; }
  %(p)s .in-row.is-on { opacity: 1; transform: none; }
  %(p)s .in-row.is-off { opacity: .28; }
  %(p)s .in-row:hover { background: rgba(255,255,255,.05); }
  %(p)s.is-compact .in-row { grid-template-columns: 128px 1fr 50px; }
  %(p)s .in-name { font: 600 12px var(--family-sans); color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  %(p)s .in-row.is-pick .in-name { font-weight: 500; color: var(--text-secondary); }
  %(p)s .in-tag { display: inline-block; font: 700 8.5px var(--family-mono); text-transform: uppercase; letter-spacing: .05em; border: 1px solid; border-radius: 999px; padding: 1px 5px; margin-left: 5px; vertical-align: 1px; white-space: nowrap; }
  %(p)s .in-tag-star { color: var(--accent-hover); border-color: var(--accent-hover); }
  %(p)s .in-tag-first { color: var(--status-error); border-color: var(--status-error); }
  %(p)s .in-tag-swap { color: var(--status-warning); border-color: var(--status-warning); }
  %(p)s .in-tag-second, %(p)s .in-tag-rights, %(p)s .in-tag-expired, %(p)s .in-tag-dead { color: var(--text-tertiary); border-color: var(--border-default); }
  %(p)s .in-track-bar { position: relative; height: 12px; background: rgba(255,255,255,.05); border: 1px solid var(--border-subtle); border-radius: 3px; overflow: hidden; }
  %(p)s .in-row.is-pick .in-track-bar { display: none; }
  %(p)s .in-row.is-pick { grid-template-columns: 1fr; }
  %(p)s .in-row.is-pick .in-sal { display: none; }
  %(p)s .in-row.is-pick .in-name { white-space: normal; overflow: visible; }
  %(p)s .in-sub { font: 500 10px var(--family-mono); color: var(--text-tertiary); margin-left: 6px; }
  %(p)s .in-fill { height: 100%%; width: 0; border-radius: 3px; transition: width 600ms cubic-bezier(.22,1,.36,1); }
  %(p)s .in-out .in-fill { background: var(--status-error); }
  %(p)s .in-in .in-fill { background: var(--accent-default); }
  %(p)s .in-kept .in-fill { background: rgba(255,255,255,.35); }
  %(p)s .in-row.is-dead .in-fill { background: transparent; border: 1px dashed var(--text-tertiary); }
  %(p)s .in-sal { font: 700 11.5px var(--family-mono); color: var(--text-secondary); text-align: right; white-space: nowrap; }
  %(p)s .in-row.is-pick .in-sal { font: 500 10px var(--family-mono); color: var(--text-tertiary); }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var basis = "season";
  var stopIdx = D.stops.length - 1;
  var MAX_SEASON = d3.max(D.rows, function (r) { return r.sal || 0; });
  var MAX_TOTAL = d3.max(D.rows, function (r) { return r.total || 0; });
  var CAPS = [
    "The summer, in order. Watch the two columns fill.",
    "June: Dosunmu first, then the trade that sent Randle, Reid and the picks out and brought LaMelo back.",
    "July: the veterans leave on minimums, and the four-team deal closes with the 2033 first on it.",
    "August 29: Green goes back out seven weeks after he arrived, so Kuminga fits under the wall.",
    "Seven players each way. The dollars nearly wash. The picks and the bigs don't."
  ];
  function fmtM(v) { return "$" + (v / 1e6).toFixed(1) + "M"; }
  function short(n, compact) {
    if (!compact) return n;
    return n.replace(/^(\w)\w+ (?=[A-Z])/, "$1. ").replace("Trey Kaufman-Renn, rights", "Kaufman-Renn, rights");
  }
  function rowEl(host, r, compact) {
    var row = host.append("div").attr("class", "in-row" + (r.sal === null ? " is-pick" : "") + (r.tag === "dead" ? " is-dead" : ""));
    var nm = row.append("div").attr("class", "in-name");
    nm.append("span").text(short(r.name, compact));
    if (r.tag !== "player") nm.append("span").attr("class", "in-tag in-tag-" + r.tag).text(r.tag === "dead" ? "stretched" : r.tag);
    if (r.sal === null && r.sub) nm.append("span").attr("class", "in-sub").text(r.sub);
    var fill = row.append("div").attr("class", "in-track-bar").append("div").attr("class", "in-fill");
    row.append("div").attr("class", "in-sal").text(r.sal === null ? (r.sub || "") : "");
    row.on("mouseenter", function () { tipAt(this, r.name, r.tip); }).on("mouseleave", hideTooltip)
       .on("click", function () { tipAt(this, r.name, r.tip); });
    return { r: r, el: row, fill: fill, sal: row.select(".in-sal") };
  }
  function build() {
    var compact = compactNow();
    root.select(".in-out-rows").selectAll("*").remove();
    root.select(".in-in-rows").selectAll("*").remove();
    root.select(".in-kept-rows").selectAll("*").remove();
    var rows = [];
    D.rows.forEach(function (r) {
      var host = r.direction === "out" ? root.select(".in-out-rows") : (r.direction === "in" ? root.select(".in-in-rows") : root.select(".in-kept-rows"));
      rows.push(rowEl(host, r, compact));
    });
    root.select(".in-out .in-count").text(D.n_out + " salaried, plus the picks");
    root.select(".in-in .in-count").text(D.n_in + " salaried");
    // the timeline
    var stops = root.select(".in-stops"); stops.selectAll("*").remove();
    var t0 = new Date(D.stops[0][0]), t1 = new Date(D.stops[D.stops.length - 1][0]);
    var x = d3.scaleTime().domain([t0, t1]).range([4, 96]);
    D.stops.forEach(function (s, i) {
      var el = stops.append("div").attr("class", "in-stop" + (i % 2 ? " is-low" : "")).style("left", x(new Date(s[0])) + "%");
      el.append("div").attr("class", "in-stop-dot");
      el.append("div").attr("class", "in-stop-lab").text(compact ? s[1].replace("August", "Aug").replace("September", "Sep").replace("June", "Jun").replace("July", "Jul") : s[1]);
      el.on("click", function () { clearPlayTimers(); hideReplay(); showStop(i, true); showReplay(); })
        .on("mouseenter", function () { tipAt(this, s[1], s[2]); }).on("mouseleave", hideTooltip);
    });
    root.selectAll(".in-toggle button").on("click", function () {
      basis = this.getAttribute("data-basis");
      root.selectAll(".in-toggle button").classed("is-on", function () { return this.getAttribute("data-basis") === basis; });
      root.select(".in-hero-label").text(basis === "season" ? "Salary this season, seven players each way" : "Whole remaining contracts, in dollars committed");
      applyBars(rows);
    });
    lastBuilt = { rows: rows, x: x, compact: compact };
    return lastBuilt;
  }
  function value(r) { return basis === "season" ? r.sal : r.total; }
  function applyBars(rows) {
    var mx = basis === "season" ? MAX_SEASON : MAX_TOTAL;
    rows.forEach(function (o) {
      if (o.r.sal === null) return;
      var v = value(o.r) || 0;
      o.fill.style("width", Math.round(v / mx * 100) + "%");
      o.sal.text(fmtM(v));
    });
  }
  function showStop(i, withHero, withCaption) {
    if (withCaption === undefined) withCaption = true;
    stopIdx = i;
    var b = lastBuilt; if (!b) return;
    var date = D.stops[i][0];
    root.selectAll(".in-stop").classed("is-on", function (d, j) { return j <= i; });
    root.select(".in-progress").style("width", (b.x(new Date(date)) - 4) / 92 * 100 + "%");
    var outSum = 0, inSum = 0;
    b.rows.forEach(function (o) {
      var on = o.r.date <= date;
      o.el.classed("is-on", on).classed("is-off", false);
      if (on && o.r.sal !== null) { if (o.r.direction === "out") outSum += o.r.sal; if (o.r.direction === "in") inSum += o.r.sal; }
    });
    applyBars(b.rows);
    if (withHero) setHero(outSum, inSum, i === D.stops.length - 1);
    if (withCaption) setCaption(D.stops[i][2], false);
  }
  var heroOut = 0, heroIn = 0;
  function setHero(outSum, inSum, landed) {
    var node = root.select(".in-hero-num");
    var fromO = heroOut, fromI = heroIn; heroOut = outSum; heroIn = inSum;
    if (reduceMotion) { node.text(fmtM(outSum) + " out · " + fmtM(inSum) + " in"); }
    else {
      d3.select(node.node()).transition("hero").duration(500).ease(d3.easeCubicOut).tween("text", function () {
        var io = d3.interpolateNumber(fromO, outSum), ii = d3.interpolateNumber(fromI, inSum);
        return function (t) { node.text(fmtM(io(t)) + " out · " + fmtM(ii(t)) + " in"); };
      });
    }
    root.classed("is-landed", landed);
  }
  function finalState(b) {
    clearPlayTimers();
    showStop(D.stops.length - 1, false, false);
    heroOut = D.out_total; heroIn = D.in_total;
    root.select(".in-hero-num").text(D.out_total_m + " out · " + D.in_total_m + " in");
    root.classed("is-landed", true);
    setCaption(CAPS[4], true);
    showReplay();
  }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false);
    b.rows.forEach(function (o) { o.el.classed("is-on", false); o.fill.style("width", "0%"); });
    root.selectAll(".in-stop").classed("is-on", false);
    root.select(".in-progress").style("width", "0%");
    heroOut = 0; heroIn = 0; root.select(".in-hero-num").text("$0.0M out · $0.0M in");
    setCaption(CAPS[0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    var t = 700, step = 1150;
    D.stops.forEach(function (s, i) { at(t + i * step, function () { showStop(i, true); }); });
    at(t + 1 * step + 500, function () { setCaption(CAPS[1]); });
    at(t + 3 * step + 500, function () { setCaption(CAPS[2]); });
    at(t + 5 * step + 500, function () { setCaption(CAPS[3]); });
    at(t + D.stops.length * step + 700, function () {
      root.select(".in-hero-num").text(D.out_total_m + " out · " + D.in_total_m + " in");
      root.classed("is-landed", true); setCaption(CAPS[4], true); showReplay();
    });
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + script(pid, js), ["c4_in_total", "c4_out_total", "c4_in_total_m", "c4_out_total_m", "c4_in_n", "c4_out_n"]


# ================================================================== 2. the wall
def viz_the_wall(S):
    G = pd.read_csv(os.path.join(OUTS, "green_resolution.csv")).set_index("step").amount
    start = float(G["pre-trade Apron Team Salary (2026-08-27)"])
    kum = float(G["sign Kuminga, taxpayer MLE year 1"])
    final = float(G["final Apron Team Salary"])
    room = float(G["room under second apron, with Kuminga"])
    over1 = float(G["over first apron, with Kuminga"])
    over_tax = float(G["over tax line, with Kuminga"])
    wall = final + room
    apron1 = final - over1
    tax = final - over_tax
    stuck = start + kum - wall
    assert money(stuck) == S["dos_stuck_over"], (money(stuck), S["dos_stuck_over"])
    assert money(room) == S["room_hard_cap"] and money(over1) == S["over_first"]
    assert money(final) == S["chain_final"] and money(float(G["post-trade Apron Team Salary (2026-09-04)"])) == S["chain_post"]
    steps = [
        dict(key="start", label="Book, Aug 27", delta=None, level=start, tip="Apron team salary before the Saturday, Dosunmu and Green on it, Kuminga not yet."),
        dict(key="kuminga_try", label="Kuminga first?", delta=kum, level=start + kum, ghost=True,
             tip="His first-year salary, the full taxpayer mid-level to the dollar, would land the book " + money(stuck) + " over the second apron, which the exception turns into a hard cap."),
        dict(key="green", label="Green out", delta=-float(G["out: Josh Green"]) * -1, level=None, tip="Josh Green and cash to Utah, seven weeks after he arrived."),
        dict(key="williams", label="Williams in", delta=float(G["in: Cody Williams"]), level=None, tip="Cody Williams, the No. 10 pick in 2024, with a team option."),
        dict(key="konchar", label="Konchar in", delta=float(G["in: John Konchar"]), level=None, tip="John Konchar, expiring, the other piece Utah sent."),
        dict(key="stretch", label="Stretched", delta=float(G["waive Konchar, stretch over 3 seasons"]) + float(G["McDaniels, our book $26,200,001 vs Spotrac $26,200,000"]), level=None,
             tip="Waived that afternoon and stretched over three seasons: his hit drops to a third, " + S["dead_year"] + " a year through 2028-29 (the extra dollar is a rounding difference between our book and Spotrac on McDaniels)."),
        dict(key="post", label="Book, Sep 4", delta=None, level=float(G["post-trade Apron Team Salary (2026-09-04)"]), tip="After the Utah trade and the stretch."),
        dict(key="kuminga", label="Kuminga in", delta=kum, level=None, tip="The same " + money(kum) + ", now with room to spare."),
        dict(key="final", label="Final", delta=None, level=final, tip=money(room) + " under the hard cap, " + money(over1) + " over the first apron, " + money(over_tax) + " over the tax line."),
    ]
    # running levels
    lvl = start
    for s in steps:
        if s.get("ghost"):
            continue
        if s["level"] is None:
            lvl = lvl + s["delta"]
            s["level"] = lvl
        else:
            lvl = s["level"]
    assert abs(steps[-1]["level"] - final) < 1.5, steps[-1]["level"]
    data = dict(steps=steps, wall=wall, apron1=apron1, tax=tax, room=room, room_txt=money(room), over1_txt=money(over1),
                over_tax_txt=money(over_tax), stuck_txt=money(stuck), kum_txt=money(kum), start=start, final=final)
    pid = "the-wall"
    p = "#viz-%s" % pid
    stage = '<svg class="th-svg" role="img" aria-label="The Saturday arithmetic against the second apron"></svg>'
    html = chrome_html(pid, "The Saturday", "August 29, the arithmetic", "", "under the second-apron hard cap",
                       "Apron team salary from the verified contract book, before and after the Utah trade, with the second apron as the wall the taxpayer mid-level creates. "
                       "Bars are the running book; the dashed bar is what signing Kuminga first would have done. Hover a bar for the step.",
                       extra_stage=stage, hero_num="$0")
    css = chrome_css(pid, "var(--status-warning)") + """
  %(p)s .th-svg { width: 100%%; height: 340px; display: block; }
  %(p)s.is-compact .th-svg { height: 300px; }
  %(p)s .th-axis text { font: 500 10px var(--family-mono); fill: var(--text-tertiary); }
  %(p)s .th-axis line, %(p)s .th-axis path { stroke: rgba(255,255,255,.12); }
  %(p)s .th-bar { opacity: 0; transition: opacity 300ms ease; cursor: pointer; }
  %(p)s .th-bar.is-on { opacity: 1; }
  %(p)s .th-lab { font: 600 10px var(--family-sans); fill: var(--text-secondary); text-anchor: middle; opacity: 0; transition: opacity 300ms ease; }
  %(p)s.is-compact .th-lab { font-size: 8.5px; }
  %(p)s .th-lab.is-on { opacity: 1; }
  %(p)s .th-val { font: 700 10px var(--family-mono); fill: var(--text-primary); text-anchor: middle; opacity: 0; transition: opacity 300ms ease; }
  %(p)s .th-val.is-on { opacity: 1; }
  %(p)s .th-line { stroke-width: 1.5; stroke-dasharray: 5 4; }
  %(p)s .th-line-lab { font: 700 10px var(--family-mono); letter-spacing: .04em; text-transform: uppercase; paint-order: stroke; stroke: #050505; stroke-width: 4px; stroke-linejoin: round; }
  %(p)s .th-wall { stroke: var(--status-warning); }
  %(p)s .th-wall-lab { fill: var(--status-warning); }
  %(p)s .th-soft { stroke: rgba(255,255,255,.25); }
  %(p)s .th-soft-lab { fill: var(--text-tertiary); }
  %(p)s .th-over { font: 700 10.5px var(--family-mono); fill: var(--status-error); text-anchor: middle; opacity: 0; transition: opacity 300ms ease; }
  %(p)s .th-over.is-on { opacity: 1; }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var CAPS = [
    "Kuminga had agreed. The book hadn't.",
    "Add his first-year salary and Minnesota is " + D.stuck_txt + " over the second apron. With that exception in use, the apron is a hard cap. A wall.",
    "So somebody had to go, and Saturday was the last day to waive a player and stretch him. Green out, Williams and Konchar in.",
    "Konchar waived that afternoon and stretched: his hit cut to a third.",
    "Now Kuminga fits. " + D.room_txt + " to spare, and " + D.over1_txt + " over the first apron, which locks the rest of the year."
  ];
  var ORDER = ["start", "kuminga_try", "green", "williams", "konchar", "stretch", "post", "kuminga", "final"];
  function fmtM(v) { return "$" + (v / 1e6).toFixed(1) + "M"; }
  function build() {
    var compact = compactNow();
    var svg = root.select(".th-svg"); svg.selectAll("*").remove();
    var W = Math.max(320, Math.min(720, rootNode.clientWidth || 640)) - 26, H = compact ? 300 : 340;
    var m = { t: 26, r: compact ? 8 : 14, b: compact ? 66 : 50, l: compact ? 40 : 52 };
    svg.attr("viewBox", "0 0 " + W + " " + H);
    var steps = D.steps;
    var x = d3.scaleBand().domain(steps.map(function (s) { return s.key; })).range([m.l, W - m.r]).paddingInner(0.28).paddingOuter(0.1);
    var lo = Math.floor((D.tax - 2e6) / 5e6) * 5e6, hi = Math.ceil((D.start + D.steps[1].delta + 2e6) / 5e6) * 5e6;
    var y = d3.scaleLinear().domain([lo, hi]).range([H - m.b, m.t]);
    var ax = svg.append("g").attr("class", "th-axis").attr("transform", "translate(" + m.l + ",0)")
      .call(d3.axisLeft(y).ticks(5).tickFormat(function (v) { return "$" + (v / 1e6).toFixed(0) + "M"; }).tickSize(-(W - m.l - m.r)));
    ax.select(".domain").remove();
    // the lines: wall, first apron, tax
    var LINES = [[D.wall, "th-wall", "second apron, the wall"], [D.apron1, "th-soft", "first apron"], [D.tax, "th-soft", "tax line"]];
    LINES.forEach(function (l) {
      svg.append("line").attr("class", "th-line " + l[1]).attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(l[0])).attr("y2", y(l[0]));
    });
    var bars = {};
    var prev = null;
    steps.forEach(function (s) {
      var g = svg.append("g").attr("class", "th-bar").attr("data-key", s.key);
      var base, top, color;
      if (s.delta === null) { base = lo; top = s.level; color = "rgba(255,255,255,.22)"; }
      else if (s.ghost) { base = D.start; top = s.level; color = "none"; }
      else { base = Math.min(prev, s.level); top = Math.max(prev, s.level); color = s.delta < 0 ? "var(--status-error)" : "var(--accent-default)"; }
      g.append("rect").attr("x", x(s.key)).attr("width", x.bandwidth()).attr("y", y(top)).attr("height", Math.max(1, y(base) - y(top)))
        .attr("rx", 3).attr("fill", color).attr("stroke", s.ghost ? "var(--status-error)" : "none").attr("stroke-dasharray", s.ghost ? "4 3" : null).attr("stroke-width", s.ghost ? 1.5 : 0);
      if (s.key === "final") g.select("rect").attr("fill", "var(--status-warning)");
      var vtxt = s.delta === null ? fmtM(s.level) : (s.delta < 0 ? "-" : "+") + fmtM(Math.abs(s.delta));
      g.append("text").attr("class", "th-val").attr("x", x(s.key) + x.bandwidth() / 2).attr("y", y(top) - 5).text(vtxt);
      if (s.ghost) g.append("text").attr("class", "th-over").attr("x", x(s.key) + x.bandwidth() / 2).attr("y", y(top) - 18).text(D.stuck_txt + " over");
      var lab;
      if (compact) {
        var cx0 = x(s.key) + x.bandwidth() / 2;
        lab = svg.append("text").attr("class", "th-lab").attr("x", cx0).attr("y", H - m.b + 10)
          .attr("text-anchor", "end").attr("transform", "rotate(-38 " + cx0 + " " + (H - m.b + 10) + ")").text(s.label);
        if (s.delta !== null && !s.ghost) g.select(".th-val").remove();
      } else {
        lab = svg.append("text").attr("class", "th-lab").attr("x", x(s.key) + x.bandwidth() / 2).attr("y", H - m.b + 16);
        var words = s.label.split(" ");
        var line1 = words.slice(0, Math.ceil(words.length / 2)).join(" "), line2 = words.slice(Math.ceil(words.length / 2)).join(" ");
        lab.append("tspan").attr("x", x(s.key) + x.bandwidth() / 2).text(line1);
        if (line2) lab.append("tspan").attr("x", x(s.key) + x.bandwidth() / 2).attr("dy", 12).text(line2);
      }
      g.on("mouseenter", function () { tipAt(this, s.label, s.tip); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, s.label, s.tip); });
      bars[s.key] = { g: g, lab: lab, s: s };
      if (!s.ghost) prev = s.level;
    });
    LINES.forEach(function (l, i) {
      var right = i === 0;
      svg.append("text").attr("class", "th-line-lab " + l[1] + "-lab").attr("x", right ? W - m.r : m.l + 6).attr("y", y(l[0]) - 4).attr("text-anchor", right ? "end" : "start").text(l[2]);
    });
    lastBuilt = { bars: bars, compact: compact };
    return lastBuilt;
  }
  function heroTo(v, dur) { tickText(root.select(".th-hero-num"), 0, v, dur, function (t) { return "$" + Math.round(t).toLocaleString("en-US"); }); }
  function finalState(b) {
    clearPlayTimers();
    ORDER.forEach(function (k) { b.bars[k].g.classed("is-on", true); b.bars[k].lab.classed("is-on", true); b.bars[k].g.selectAll(".th-val, .th-over").classed("is-on", true); });
    root.select(".th-hero-num").text(D.room_txt); root.classed("is-landed", true); setCaption(CAPS[4], true); showReplay();
  }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false);
    ORDER.forEach(function (k) { b.bars[k].g.classed("is-on", false); b.bars[k].lab.classed("is-on", false); b.bars[k].g.selectAll(".th-val, .th-over").classed("is-on", false); });
    root.select(".th-hero-num").text("$0"); setCaption(CAPS[0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    var t = 600, step = 900;
    ORDER.forEach(function (k, i) {
      at(t + i * step, function () { b.bars[k].g.classed("is-on", true); b.bars[k].lab.classed("is-on", true); b.bars[k].g.selectAll(".th-val, .th-over").classed("is-on", true); });
    });
    at(t + 1 * step + 200, function () { setCaption(CAPS[1]); });
    at(t + 2 * step + 200, function () { setCaption(CAPS[2]); });
    at(t + 5 * step + 200, function () { setCaption(CAPS[3]); });
    at(t + 8 * step + 300, function () { setCaption(CAPS[4]); heroTo(D.room, 900); root.classed("is-landed", true); });
    at(t + 9 * step + 600, showReplay);
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + script(pid, js), ["dos_stuck_over", "room_hard_cap", "over_first", "over_tax", "chain_final", "chain_post", "dead_year"]


# ================================================================== 3. the market
def viz_the_market(S):
    M = pd.read_csv(os.path.join(OUTS, "market_devig_2026_27.csv"))
    conf = dict(E.TEAM_CONF)
    rows = []
    for _, x in M.sort_values("market_rank").iterrows():
        rows.append(dict(abbr=x.team_abbr, team=x.team, pct=float(x.market_pct), rank=int(x.market_rank), odds=int(x.median_odds), conf=conf.get(x.team_abbr, "")))
    mn = [r for r in rows if r["abbr"] == "MIN"][0]
    assert "%.2f%%" % mn["pct"] == S["mkt_min"] and str(mn["rank"]) == S["mkt_min_rank"]
    tie = [r["abbr"] for r in rows if abs(r["pct"] - mn["pct"]) < 1e-9]
    data = dict(rows=rows, min_pct=S["mkt_min"], min_rank=mn["rank"], tie=tie)
    pid = "the-market"
    p = "#viz-%s" % pid
    toolbar = ('<div class="th-toggle" role="group" aria-label="Conference"><button type="button" data-conf="all" class="is-on">All 30</button>'
               '<button type="button" data-conf="W">West</button><button type="button" data-conf="E">East</button></div>')
    stage = '<svg class="th-svg" role="img" aria-label="Thirty teams by title odds"></svg>'
    html = chrome_html(pid, "What the market said", "title odds, September", "to win the title", "sixth in the league, in a five-way tie",
                       "Six books' title odds, median, with the bookmakers' margin stripped out proportionally so the thirty teams sum to one. Log scale, because the favorites and the field are two orders apart. Hover a team for its price.",
                       extra_stage=stage, toolbar=toolbar, hero_num="0.00%")
    css = chrome_css(pid, "var(--accent-default)") + """
  %(p)s .th-svg { width: 100%%; height: 250px; display: block; }
  %(p)s.is-compact .th-svg { height: 260px; }
  %(p)s .th-axis text { font: 500 10px var(--family-mono); fill: var(--text-tertiary); }
  %(p)s .th-axis line, %(p)s .th-axis path { stroke: rgba(255,255,255,.12); }
  %(p)s .th-dot { cursor: pointer; opacity: 0; transition: opacity 300ms ease, r 150ms ease; }
  %(p)s .th-dot.is-on { opacity: 1; }
  %(p)s .th-dot.is-dim { opacity: .18; }
  %(p)s .th-dotlab { font: 700 9.5px var(--family-mono); fill: var(--text-secondary); text-anchor: middle; pointer-events: none; opacity: 0; transition: opacity 300ms ease; }
  %(p)s .th-dotlab.is-on { opacity: 1; }
  %(p)s .th-dotlab.is-dim { opacity: .18; }
  %(p)s .th-note { font: 600 10.5px var(--family-sans); fill: var(--text-secondary); }
  %(p)s .th-note-line { stroke: rgba(255,255,255,.4); stroke-width: 1; }
  %(p)s .th-min { fill: var(--accent-default); }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var CAPS = [
    "Thirty teams, one price each. Strip the bookmakers' margin and they sum to one.",
    "Two co-favorites out on their own, then the Sixers, the Knicks and Boston.",
    "Then a five-way tie at " + D.min_pct + ": " + D.tie.join(", ") + ".",
    "That's Minnesota. Sixth in the league, for a team that lost two rotation bigs and an unprotected first. Not a panic price."
  ];
  var conf = "all";
  function build() {
    var compact = compactNow();
    var svg = root.select(".th-svg"); svg.selectAll("*").remove();
    var W = Math.max(320, Math.min(720, rootNode.clientWidth || 640)) - 26, H = compact ? 260 : 250;
    var m = { t: 44, r: 16, b: 34, l: 16 };
    svg.attr("viewBox", "0 0 " + W + " " + H);
    var x = d3.scaleLog().domain([0.07, 30]).range([m.l, W - m.r]);
    var ax = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m.b) + ")")
      .call(d3.axisBottom(x).tickValues([0.1, 0.3, 1, 3, 10, 30]).tickFormat(function (v) { return v + "%"; }).tickSize(-(H - m.b - m.t)));
    ax.select(".domain").remove();
    // beeswarm: pack dots along y within lanes so ties don't overlap
    var r = compact ? 9 : 11;
    var nodes = D.rows.map(function (d) { return { d: d, x: x(d.pct), y: (H - m.b + m.t) / 2 }; });
    var sim = d3.forceSimulation(nodes).force("x", d3.forceX(function (n) { return n.x; }).strength(1)).force("y", d3.forceY((H - m.b + m.t) / 2).strength(0.08)).force("collide", d3.forceCollide(r + 1.5)).stop();
    for (var i = 0; i < 200; i++) sim.tick();
    var dots = {};
    nodes.forEach(function (n) {
      var isMin = n.d.abbr === "MIN";
      var g = svg.append("g").attr("class", "th-dot" + (isMin ? " th-min-g" : "")).attr("data-abbr", n.d.abbr).attr("data-conf", n.d.conf);
      g.append("circle").attr("cx", n.x).attr("cy", n.y).attr("r", r).attr("fill", isMin ? "var(--accent-default)" : "rgba(255,255,255,.14)").attr("stroke", isMin ? "var(--accent-hover)" : "rgba(255,255,255,.35)").attr("stroke-width", isMin ? 2 : 1);
      var lab = svg.append("text").attr("class", "th-dotlab").attr("x", n.x).attr("y", n.y + 3.5).text(n.d.abbr).attr("fill", isMin ? "#fff" : null).style("font-size", compact ? "8px" : null);
      g.on("mouseenter", function () { tipAt(this, n.d.team, n.d.pct.toFixed(2) + "% to win the title, rank " + n.d.rank + " of 30. Median line +" + n.d.odds.toLocaleString("en-US") + "."); })
       .on("mouseleave", hideTooltip).on("click", function () { tipAt(this, n.d.team, n.d.pct.toFixed(2) + "% to win the title, rank " + n.d.rank + " of 30. Median line +" + n.d.odds.toLocaleString("en-US") + "."); });
      dots[n.d.abbr] = { g: g, lab: lab, n: n };
    });
    // the tie callout
    var mn = dots["MIN"].n;
    svg.append("line").attr("class", "th-note-line").attr("x1", mn.x).attr("x2", mn.x).attr("y1", mn.y - r - 3).attr("y2", m.t - 14);
    var noteTxt = compact ? "five teams at " + D.min_pct : "five teams at " + D.min_pct + ", Minnesota among them";
    var noteW = compact ? 120 : 235;
    var nx = Math.max(noteW / 2 + 4, Math.min(W - noteW / 2 - 4, mn.x));
    svg.append("text").attr("class", "th-note").attr("x", nx).attr("y", m.t - 18).attr("text-anchor", "middle").text(noteTxt);
    root.selectAll(".th-toggle button").on("click", function () {
      conf = this.getAttribute("data-conf");
      root.selectAll(".th-toggle button").classed("is-on", function () { return this.getAttribute("data-conf") === conf; });
      applyConf();
    });
    lastBuilt = { dots: dots, compact: compact };
    return lastBuilt;
  }
  function applyConf() {
    var b = lastBuilt; if (!b) return;
    Object.keys(b.dots).forEach(function (k) {
      var dim = conf !== "all" && b.dots[k].n.d.conf !== conf;
      b.dots[k].g.classed("is-dim", dim); b.dots[k].lab.classed("is-dim", dim);
    });
  }
  function onAll(b, on) { Object.keys(b.dots).forEach(function (k) { b.dots[k].g.classed("is-on", on); b.dots[k].lab.classed("is-on", on); }); }
  function finalState(b) { clearPlayTimers(); onAll(b, true); applyConf(); root.select(".th-hero-num").text(D.min_pct); root.classed("is-landed", true); setCaption(CAPS[3], true); showReplay(); }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false); onAll(b, false);
    root.select(".th-hero-num").text("0.00%"); setCaption(CAPS[0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    var order = D.rows.slice().sort(function (a, c) { return c.rank - a.rank; });   // the field first, the favorites last
    order.forEach(function (d, i) { at(500 + i * 70, function () { b.dots[d.abbr].g.classed("is-on", true); b.dots[d.abbr].lab.classed("is-on", true); }); });
    at(2900, function () { setCaption(CAPS[1]); });
    at(4100, function () { setCaption(CAPS[2]); });
    at(5300, function () { setCaption(CAPS[3]); tickText(root.select(".th-hero-num"), 0, parseFloat(D.min_pct), 800, function (t) { return t.toFixed(2) + "%"; }); root.classed("is-landed", true); });
    at(6400, showReplay);
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + script(pid, js), ["mkt_min", "mkt_min_rank"]


# ================================================================== 4. the grades
GRADE_SCALE = {"A+": 12, "A": 11, "A-": 10, "B+": 9, "B": 8, "B-": 7, "C+": 6, "C": 5, "C-": 4, "D+": 3, "D": 2, "D-": 1, "F": 0}


def viz_the_grades(S):
    G = pd.read_csv(os.path.join(DATA, "c4_offseason_grades.csv"))
    rows = []
    for _, x in G.iterrows():
        g = str(x.grade_or_rank).strip()
        m2 = re.search(r"([A-D][+-]?|F)\s*(?:\(subject to change\)\s*)?for MIN", g)
        m = re.match(r"([A-D][+-]?|F)(?=\s|$|\()", g)
        letter = m2.group(1) if m2 else (m.group(1) if m else None)
        if letter is None or letter not in GRADE_SCALE or str(x.date) in ("unknown", "nan"):
            continue
        what = str(x.what_was_graded)
        if "power ranking" in what or g.startswith("per move"):
            continue
        scope = ("kuminga" if "Kuminga signing" in what else "green" if "Josh Green" in what else "trade" if "Ball trade" in what
                 else ("whole" if what.startswith("whole offseason") else "partial"))
        secondhand = "secondhand" in g or "The Athletic" in str(x.outlet)
        rows.append(dict(outlet=str(x.outlet).replace(" (via Yahoo syndication)", "").replace(" (Minute Media)", ""), author=str(x.author), date=str(x.date),
                         letter=letter, score=GRADE_SCALE[letter], scope=scope, what=what, quote=str(x.rationale_quote) if pd.notna(x.rationale_quote) else "",
                         secondhand=secondhand, restated="restates" in g))
    whole = [r for r in rows if r["scope"] == "whole"]
    lo = min(whole, key=lambda r: r["score"]); hi = max(whole, key=lambda r: r["score"])
    # gate: the whole-offseason grade set on the sheet
    sheet_whole = S["c4_grades_whole"]
    for r in whole:
        assert r["letter"] in sheet_whole, (r["outlet"], r["letter"], sheet_whole)
    assert int(S["c4_grades_whole_n"]) == len(whole), (S["c4_grades_whole_n"], len(whole), [(r["outlet"], r["letter"]) for r in whole])
    data = dict(rows=rows, lo=lo["letter"], hi=hi["letter"], lo_outlet=lo["outlet"], hi_outlet=hi["outlet"], n_whole=len(whole), n_trade=len([r for r in rows if r["scope"] == "trade"]))
    pid = "the-grades"
    p = "#viz-%s" % pid
    toolbar = ('<div class="th-toggle" role="group" aria-label="Which grades"><button type="button" data-scope="all" class="is-on">Everything</button>'
               '<button type="button" data-scope="whole">Whole offseason</button><button type="button" data-scope="trade">The trade alone</button></div>')
    stage = '<svg class="th-svg" role="img" aria-label="Offseason grades by date"></svg>'
    html = chrome_html(pid, "What everyone said", "the grades, June 25 to August 29", "", "whole-offseason grades ran from " + lo["letter"] + " to " + hi["letter"] + "; nobody gave an A, nobody gave an F",
                       "Every national letter grade for Minnesota, placed on the day it ran, from the pieces we fetched and read. Filled marks grade the whole offseason; the lighter filled marks are partial (NBC's grade through July 2, ESPN restating its July grade in August); hollow marks grade the LaMelo Ball trade alone on the day it broke; the two squares grade the Kuminga signing and the Green trade. "
                       "The Athletic's trade grade is secondhand, via Heavy. Hover a mark for the line that came with it.",
                       extra_stage=stage, toolbar=toolbar, hero_num="")
    css = chrome_css(pid, "var(--accent-default)") + """
  %(p)s .th-svg { width: 100%%; height: 330px; display: block; }
  %(p)s.is-compact .th-svg { height: 330px; }
  %(p)s .th-hero-num { font-size: 40px; }
  %(p)s .th-axis text { font: 500 10px var(--family-mono); fill: var(--text-tertiary); }
  %(p)s .th-axis line, %(p)s .th-axis path { stroke: rgba(255,255,255,.12); }
  %(p)s .th-mark { cursor: pointer; opacity: 0; transition: opacity 300ms ease; }
  %(p)s .th-mark.is-on { opacity: 1; }
  %(p)s .th-mark.is-dim { opacity: .15; }
  %(p)s .th-mlab { font: 600 9.5px var(--family-sans); fill: var(--text-secondary); pointer-events: none; }
  %(p)s .th-band { fill: var(--accent-subtle); opacity: 0; transition: opacity 500ms ease; }
  %(p)s .th-band.is-on { opacity: 1; }
""" % dict(p=p)
    js = r"""
  var D = __DATA__;
  var LETTERS = ["F", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+"];
  var CAPS = [
    "June 25: the trade breaks, and the grades come in the same day.",
    "The trade alone drew everything from " + "a D+" + " to " + "an A+" + ", which tells you something about the summer on its own.",
    "The whole-offseason grades, once the rest of the league moved: " + D.lo + " to " + D.hi + ". Nobody gave an A, nobody gave an F.",
    "Read them all and the disagreement isn't about the players. It's about one question: is LaMelo Ball a player you bet a franchise's picks on?"
  ];
  var scope = "all";
  function build() {
    var compact = compactNow();
    var svg = root.select(".th-svg"); svg.selectAll("*").remove();
    var W = Math.max(320, Math.min(720, rootNode.clientWidth || 640)) - 26, H = 330;
    var m = { t: 16, r: 14, b: 30, l: 34 };
    svg.attr("viewBox", "0 0 " + W + " " + H);
    var x = d3.scaleTime().domain([new Date("2026-06-22"), new Date("2026-09-02")]).range([m.l, W - m.r]);
    var y = d3.scalePoint().domain(LETTERS).range([H - m.b, m.t]);
    var ay = svg.append("g").attr("class", "th-axis").attr("transform", "translate(" + m.l + ",0)").call(d3.axisLeft(y).tickSize(-(W - m.l - m.r)));
    ay.select(".domain").remove();
    var axx = svg.append("g").attr("class", "th-axis").attr("transform", "translate(0," + (H - m.b) + ")").call(d3.axisBottom(x).ticks(compact ? 3 : 5).tickFormat(d3.timeFormat("%b %d")));
    axx.select(".domain").remove();
    // the whole-offseason band
    var wh = D.rows.filter(function (r) { return r.scope === "whole"; });
    var band = svg.append("rect").attr("class", "th-band").attr("x", m.l).attr("width", W - m.l - m.r)
      .attr("y", y(D.hi) - 8).attr("height", y(D.lo) - y(D.hi) + 16);
    // marks, with same-day jitter
    var byDay = {};
    var marks = [];
    D.rows.slice().sort(function (a, b) { return a.date < b.date ? -1 : 1; }).forEach(function (r) {
      var k = r.date + "|" + r.letter; byDay[k] = (byDay[k] || 0) + 1;
      var jitter = (byDay[k] - 1) * (compact ? 9 : 12);
      var cx = x(new Date(r.date)) + jitter, cy = y(r.letter);
      var g = svg.append("g").attr("class", "th-mark").attr("data-scope", r.scope);
      var isWhole = r.scope === "whole";
      var sq = r.scope === "kuminga" || r.scope === "green";
      var isPartial = r.scope === "partial";
      if (sq) g.append("rect").attr("x", cx - 6).attr("y", cy - 6).attr("width", 12).attr("height", 12).attr("rx", 2).attr("fill", "var(--accent-default)").attr("stroke", "#fff").attr("stroke-width", 1);
      else g.append("circle").attr("cx", cx).attr("cy", cy).attr("r", compact ? 6 : 7).attr("fill", isWhole ? "var(--accent-default)" : (isPartial ? "rgba(0,132,61,.35)" : "rgba(0,0,0,.6)")).attr("stroke", isWhole ? "var(--accent-hover)" : (r.secondhand ? "var(--status-warning)" : "rgba(255,255,255,.55)")).attr("stroke-width", 1.5).attr("stroke-dasharray", r.secondhand ? "3 2" : null);
      var dupKey = r.outlet + "|" + r.letter + "|" + r.scope;
      var laterTwin = D.rows.some(function (o) { return o !== r && o.outlet === r.outlet && o.letter === r.letter && o.scope === r.scope && o.date > r.date && (new Date(o.date) - new Date(r.date)) < 12 * 86400000; });
      var flip = cx > W - 90;
      var skipLab = compact && isPartial && r.restated;
      if ((isWhole || sq || isPartial) && !laterTwin && !skipLab) g.append("text").attr("class", "th-mlab").attr("x", flip ? cx - 10 : cx + 10).attr("y", cy + 3.5).attr("text-anchor", flip ? "end" : "start").text((compact ? r.outlet.replace("Bleacher Report", "B/R").replace("The Big Lead", "Big Lead").replace("Yahoo Sports", "Yahoo").replace("CBS Sports", "CBS").replace("NBC Sports", "NBC") : r.outlet) + (isPartial && !compact ? (r.restated ? " (restated)" : " (to Jul 2)") : ""));
      var desc = "<b>" + r.letter + "</b>, " + r.what + (r.author && r.author !== "nan" ? ", " + r.author : "") + ", " + r.date + (r.secondhand ? " (secondhand, via Heavy)" : "") + (r.quote ? "<br><i>“" + r.quote + "”</i>" : "");
      g.on("mouseenter", function () { tipAt(this, r.outlet, desc); }).on("mouseleave", hideTooltip).on("click", function () { tipAt(this, r.outlet, desc); });
      marks.push({ g: g, r: r });
    });
    root.selectAll(".th-toggle button").on("click", function () {
      scope = this.getAttribute("data-scope");
      root.selectAll(".th-toggle button").classed("is-on", function () { return this.getAttribute("data-scope") === scope; });
      applyScope();
    });
    lastBuilt = { marks: marks, band: band, compact: compact };
    return lastBuilt;
  }
  function applyScope() {
    var b = lastBuilt; if (!b) return;
    b.marks.forEach(function (o) { var dim = scope !== "all" && o.r.scope !== scope && !(scope === "whole" && (o.r.scope === "partial" || o.r.scope === "kuminga" || o.r.scope === "green")); o.g.classed("is-dim", dim); });
  }
  function finalState(b) {
    clearPlayTimers(); b.marks.forEach(function (o) { o.g.classed("is-on", true); }); b.band.classed("is-on", true); applyScope();
    root.select(".th-hero-num").text(D.lo + " to " + D.hi); root.classed("is-landed", true); setCaption(CAPS[3], true); showReplay();
  }
  function play(b) {
    clearPlayTimers(); hideReplay(); root.classed("is-landed", false);
    b.marks.forEach(function (o) { o.g.classed("is-on", false); }); b.band.classed("is-on", false);
    root.select(".th-hero-num").text(""); setCaption(CAPS[0], true);
    if (reduceMotion) { finalState(b); return; }
    if (__resetOnly) return;
    var t = 500;
    b.marks.forEach(function (o, i) { at(t + i * 140, function () { o.g.classed("is-on", true); }); });
    var n = b.marks.length;
    at(t + 9 * 140 + 200, function () { setCaption(CAPS[1]); });
    at(t + n * 140 + 300, function () { setCaption(CAPS[2]); b.band.classed("is-on", true); root.select(".th-hero-num").text(D.lo + " to " + D.hi); root.classed("is-landed", true); });
    at(t + n * 140 + 2600, function () { setCaption(CAPS[3]); showReplay(); });
  }
""".replace("__DATA__", json.dumps(data))
    return pid, html + "\n<style>" + css + "</style>\n" + script(pid, js), ["c4_grades_whole", "c4_grades_whole_n"]


# ================================================================== main
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    S = pd.read_csv(os.path.join(OUTS, "final_numbers.csv"), dtype=str).set_index("key").value
    sources = pd.read_csv(os.path.join(DATA, "c4_transaction_sources.csv"), dtype=str)
    with runlog.run("charts_part1", inputs={"ledger": "c4_ledger.csv", "chain": "green_resolution.csv",
                                            "market": "market_devig_2026_27.csv", "grades": "c4_offseason_grades.csv"}) as r:
        built = [viz_ins_and_outs(S, sources), viz_the_wall(S), viz_the_market(S), viz_the_grades(S)]
        cards = []
        titles = {"ins-and-outs": ("In and out", "The summer as a ledger with a date scrubber; seven players each way."),
                  "the-wall": ("The Saturday", "The arithmetic against the second apron, step by step."),
                  "the-market": ("What the market said", "Thirty teams on a log strip; Minnesota inside the five-way tie."),
                  "the-grades": ("What everyone said", "Every national letter grade on the day it ran.")}
        for pid, frag, keys in built:
            stem = pid.replace("-", "_")
            frag = "<!-- %s; sheet keys checked: %s -->\n" % (r.run_id, ", ".join(keys)) + frag
            fp = os.path.join(OUT_DIR, stem + "_fragment.html")
            with open(fp, "w", encoding="utf-8") as fh:
                fh.write(frag)
            pp = os.path.join(OUT_DIR, stem + "_preview.html")
            with open(pp, "w", encoding="utf-8") as fh:
                fh.write(preview(titles[pid][0], frag, stem + "_fragment.html"))
            r.output(fp)
            r.note("%s: %d bytes, keys %s" % (stem + "_fragment.html", len(frag.encode("utf-8")), ", ".join(keys)))
            cards.append('<a class="card" href="%s_preview.html"><div class="sec">Part 1</div><div class="title">%s</div><div class="sub">%s</div><div class="files">%s_fragment.html · place with {{viz:%s}}</div></a>'
                         % (stem, titles[pid][0], titles[pid][1], stem, pid))
        index = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>The Bet, Part 1: visuals</title>
<style>
  :root { --accent:#00843D; --accent-hover:#00A04A; --bg-surface:#0E0E0E; --text:#fff; --text-2:rgba(255,255,255,.72); --text-3:rgba(255,255,255,.48); --border:rgba(255,255,255,.08); --sans:'Inter',system-ui,-apple-system,sans-serif; --mono:'JetBrains Mono',ui-monospace,Menlo,monospace; }
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
  <h1>The Bet, Part 1: the visuals</h1>
  <p class="lead">Four fragments, built by <code>scripts/charts_part1.py</code> from the ledger and the sheet. Click a card to open its preview harness.</p>
  <p class="note">Each fragment is the publishable artifact (the host supplies D3 v7 and the design tokens). Every hero figure was checked against final_numbers.csv when the file was written; the run ID is the first line of each fragment.</p>
  %s
</div></body></html>
""" % "\n  ".join(cards)
        ip = os.path.join(OUT_DIR, "index.html")
        with open(ip, "w", encoding="utf-8") as fh:
            fh.write(index)
        r.output(ip)


if __name__ == "__main__":
    main()
