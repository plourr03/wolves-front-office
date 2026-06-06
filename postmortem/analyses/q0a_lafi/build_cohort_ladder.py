"""Build the LAFI cohort ladder visualization for Chasing the First Banner.

The second chart in Article 1 ("The LA Fitness Game"). It sits in the
"How rare is this" section. Eight cohort teams as rows; each row's bar runs
as far as that team got in the playoffs. A red wall stands at the Conference
Finals. No bar reaches it.

Conforms to the viz-builder skill contract: a self-contained HTML *fragment*
(container div + scoped style + IIFE script), pure D3 v7 against the `d3`
global, site design tokens via .style(), responsive, accessible.

Outputs two files in outputs/charts/q0a_lafi/:
  cohort_ladder_fragment.html  -- THE DELIVERABLE. Paste into /admin/visualizations/new.
  cohort_ladder_preview.html   -- a local dev harness (full doc: D3 CDN +
                                  design tokens + the fragment).

viz id: lafi-cohort-ladder   (container id: viz-lafi-cohort-ladder)

Rows load from the canonical Q0C cohort output, never hardcoded. Playoff
outcomes were re-verified against the warehouse (scripts/verify_cohort_outcomes.py).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
VIZ_ID = "lafi-cohort-ladder"

# Display order is fixed: the five teams that missed the playoffs first
# (worst record to best), then the two playoff teams, then the Wolves last.
ROW_ORDER = [
    (2018, "NYK"), (2016, "PHX"), (2018, "SAC"), (2022, "CHI"), (2024, "SAC"),
    (2023, "PHX"), (2021, "PHI"), (2025, "MIN"),
]

NICKNAME = {"NYK": "Knicks", "PHX": "Suns", "SAC": "Kings",
            "CHI": "Bulls", "PHI": "76ers", "MIN": "Wolves"}

# tier drives color: muted gray, blue callout, Wolves green.
TIER = {
    (2018, "NYK"): "missed", (2016, "PHX"): "missed", (2018, "SAC"): "missed",
    (2022, "CHI"): "missed", (2024, "SAC"): "missed",
    (2023, "PHX"): "made", (2021, "PHI"): "made",
    (2025, "MIN"): "wolves",
}

# (stage index, bar-end label) keyed off the canonical playoff_outcome string.
# Stage index maps to an x position: 0 Missed, 1 Round 1, 2 Round 2.
STAGE = {
    "missed": (0, "Missed the playoffs"),
    "R1 lost (0-4)": (1, "Swept in Round 1"),
    "R2 lost (6-6)": (2, "Lost in Round 2"),
}

NOTE = {
    (2018, "NYK"): "A tank-for-Zion roster. The architecture next to a 17-win season.",
    (2016, "PHX"): "Pre-Booker-breakout Phoenix. The profile can sit on a bad roster.",
    (2018, "SAC"): "The young Fox and Hield Kings. A near-.500 team that just missed.",
    (2022, "CHI"): "DeRozan, LaVine, and Vucevic. Knocked out in the play-in.",
    (2024, "SAC"): "Fox, DeRozan, and Sabonis. The most recent team to fit the profile.",
    (2023, "PHX"): "Durant, Booker, and Beal. Swept in the first round, by the Wolves.",
    (2021, "PHI"): "Joel Embiid finished second in MVP voting. They still lost in the second round.",
    (2025, "MIN"): "Edwards, Gobert, and Randle. A 49-win team. The team this project is about.",
}

ALT_TEXT = (
    "Horizontal bar chart of the eight LAFI cohort teams from 2014-15 through "
    "2025-26. Each bar runs as far as that team reached in the playoffs. Five "
    "teams missed the playoffs entirely. The 2023-24 Suns were swept in the "
    "first round. The 2021-22 76ers and the 2025-26 Timberwolves lost in the "
    "second round. A red line marks the Conference Finals. No team's bar "
    "reaches it."
)


def load_rows() -> list[dict]:
    df = pd.read_csv(ROOT / "outputs/tables/q0c_historical_cohort/cohort_with_outcomes.csv")
    rows = []
    for syear, team in ROW_ORDER:
        r = df[(df.season_start_year == syear) & (df.team_abbreviation == team)].iloc[0]
        stage_idx, bar_label = STAGE[r.playoff_outcome]
        rows.append({
            "team": team,
            "label": f"{r.season_year} {NICKNAME[team]}",
            "record": r.rs_record,
            "tier": TIER[(syear, team)],
            "stage": stage_idx,
            "outcome": bar_label,
            "sharp": round(r.sharp_lafi_pct),
            "note": NOTE[(syear, team)],
        })
    return rows


# ---------------------------------------------------------------------------
# Fragment
# ---------------------------------------------------------------------------

FRAGMENT = r"""<div id="viz-__VIZID__">
  <div class="cl-legend" aria-hidden="true">
    <span class="cl-key"><span class="cl-sw" data-t="missed"></span>Missed the playoffs</span>
    <span class="cl-key"><span class="cl-sw" data-t="made"></span>Made the playoffs</span>
    <span class="cl-key"><span class="cl-sw" data-t="wolves"></span>The 2025-26 Wolves</span>
  </div>
  <div class="cl-host"></div>
  <p class="cl-foot">Eight team-seasons match this offensive profile across 2014-15 through 2025-26. A small sample. The chart shows a pattern, not a law.</p>
</div>
<style>
  #viz-__VIZID__ { font-family: var(--family-sans); color: var(--text-primary); }
  #viz-__VIZID__ .cl-legend {
    display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 14px;
  }
  #viz-__VIZID__ .cl-key {
    display: flex; align-items: center; gap: 7px;
    font: 600 12px var(--family-sans); color: var(--text-secondary);
  }
  #viz-__VIZID__ .cl-sw { width: 12px; height: 12px; border-radius: 3px; }
  #viz-__VIZID__ .cl-sw[data-t="missed"] { background: var(--text-tertiary); }
  #viz-__VIZID__ .cl-sw[data-t="made"] { background: var(--status-info); }
  #viz-__VIZID__ .cl-sw[data-t="wolves"] { background: var(--accent-default); }
  #viz-__VIZID__ .cl-foot {
    margin: 12px 0 0 0; font: 11.5px/1.5 var(--family-sans);
    color: var(--text-tertiary);
  }
</style>
<script>
(function () {
  var ID = "viz-__VIZID__";
  var ROWS = __ROWS_JSON__;

  var container = document.getElementById(ID);
  if (!container || typeof d3 === "undefined") return;
  var host = container.querySelector(".cl-host");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasEntered = false;
  var lastWidth = 0;

  // Stage x positions on a 0..5 domain. The bar starts at x(0); a missed
  // team reaches the first rung at 0.5, Round 1 at 1.5, Round 2 at 2.5.
  // The wall (Conference Finals) is at 3.5, the Finals rung at 4.5.
  var STAGE_X = [0.5, 1.5, 2.5];
  var WALL_X = 3.5;
  var RUNGS = [
    { x: 0.5, label: "Missed", short: "Miss" },
    { x: 1.5, label: "Round 1", short: "R1" },
    { x: 2.5, label: "Round 2", short: "R2" },
    { x: 4.5, label: "Finals", short: "Fin" }
  ];
  // Compact-mode abbreviations for the bar-end outcome labels. Keeps the
  // label from crashing through the Conference Finals wall on narrow widths.
  var SHORT_OUTCOME = {
    "Missed the playoffs": "Missed",
    "Swept in Round 1": "Swept R1",
    "Lost in Round 2": "Lost R2"
  };

  function tierColor(t) {
    if (t === "wolves") return "var(--accent-default)";
    if (t === "made") return "var(--status-info)";
    return "var(--text-tertiary)";
  }

  function render(animate) {
    var playIn = animate && !reduceMotion;
    if (playIn) hasEntered = true;
    var settled = reduceMotion || hasEntered;
    var startEmpty = playIn || !settled;

    var root = d3.select(host);
    root.selectAll("*").remove();

    var raw = host.clientWidth || 640;
    var width = Math.max(320, Math.min(960, raw));
    var compact = width < 480;

    var marginL = compact ? 6 : 152;
    var marginR = 16;
    var rowH = compact ? 64 : 50;
    var barH = compact ? 16 : 22;
    var top = compact ? 58 : 62;
    var bottom = 14;
    var height = top + bottom + ROWS.length * rowH;

    var svg = root.append("svg")
      .attr("width", width).attr("height", height)
      .attr("viewBox", "0 0 " + width + " " + height)
      .attr("role", "img")
      .style("display", "block")
      .style("max-width", "100%").style("margin", "0 auto");
    lastWidth = raw;

    var x = d3.scaleLinear().domain([0, 5]).range([marginL, width - marginR]);
    var plotTop = top - 6;
    var plotBottom = height - bottom;

    // Unreached zone: everything at or past the Conference Finals.
    svg.append("rect")
      .attr("x", x(WALL_X)).attr("y", plotTop)
      .attr("width", x(5) - x(WALL_X)).attr("height", plotBottom - plotTop)
      .style("fill", "var(--status-error)").style("fill-opacity", 0.06);

    // Faint rungs for the reachable rounds plus the Finals.
    RUNGS.forEach(function (r) {
      svg.append("line")
        .attr("x1", x(r.x)).attr("x2", x(r.x))
        .attr("y1", plotTop).attr("y2", plotBottom)
        .style("stroke", "var(--border-subtle)").style("stroke-width", 1);
      svg.append("text")
        .attr("x", x(r.x)).attr("y", top - 14).attr("text-anchor", "middle")
        .style("fill", "var(--text-tertiary)")
        .style("font", "600 10.5px var(--family-sans)")
        .style("letter-spacing", "0.04em")
        .text(compact ? r.short : r.label.toUpperCase());
    });

    // The wall: the Conference Finals. Drawn bold, in the warning red.
    svg.append("line")
      .attr("x1", x(WALL_X)).attr("x2", x(WALL_X))
      .attr("y1", plotTop).attr("y2", plotBottom)
      .style("stroke", "var(--status-error)").style("stroke-width", 2.5);
    svg.append("text")
      .attr("x", x(WALL_X)).attr("y", top - 14).attr("text-anchor", "middle")
      .style("fill", "var(--status-error)")
      .style("font", "700 10.5px var(--family-sans)")
      .style("letter-spacing", "0.04em")
      .text(compact ? "CONF FINALS" : "CONFERENCE FINALS");

    // The wall's message, two lines, ending at the wall.
    var msg = compact
      ? ["No cohort team", "crosses this."]
      : ["Nobody in the cohort", "crosses this line."];
    var cap = svg.append("text")
      .attr("x", x(WALL_X) - 9).attr("text-anchor", "end")
      .style("fill", "var(--status-error)")
      .style("font", "600 11px var(--family-sans)");
    cap.append("tspan").attr("x", x(WALL_X) - 9).attr("y", 17).text(msg[0]);
    cap.append("tspan").attr("x", x(WALL_X) - 9).attr("y", 32).text(msg[1]);

    var rows = svg.append("g").selectAll("g").data(ROWS).join("g")
      .attr("transform", function (_, i) {
        return "translate(0," + (top + i * rowH) + ")";
      });

    // Wolves row: a faint accent wash so the subject team reads as the subject.
    rows.filter(function (d) { return d.tier === "wolves"; })
      .append("rect")
      .attr("x", 0).attr("y", 0)
      .attr("width", width).attr("height", rowH)
      .style("fill", "var(--accent-default)").style("fill-opacity", 0.07);

    var barCY = compact ? 40 : rowH / 2;

    // Team label. Beside the track when wide, above it when compact.
    if (compact) {
      rows.append("text")
        .attr("x", marginL).attr("y", 15)
        .style("fill", "var(--text-primary)")
        .style("font", "600 13px var(--family-sans)")
        .text(function (d) { return d.label + ",  " + d.record; });
    } else {
      rows.append("text")
        .attr("x", marginL - 14).attr("y", barCY - 7).attr("dy", "0.32em")
        .attr("text-anchor", "end")
        .style("fill", "var(--text-primary)")
        .style("font", "600 13px var(--family-sans)")
        .text(function (d) { return d.label; });
      rows.append("text")
        .attr("x", marginL - 14).attr("y", barCY + 9).attr("dy", "0.32em")
        .attr("text-anchor", "end")
        .style("fill", "var(--text-tertiary)")
        .style("font", "11px var(--family-mono)")
        .text(function (d) { return d.record; });
    }

    // Per-row track baseline: the full journey, faint.
    rows.append("line")
      .attr("x1", x(0)).attr("x2", x(5))
      .attr("y1", barCY).attr("y2", barCY)
      .style("stroke", "var(--border-subtle)").style("stroke-width", 1);

    // The bar: how far the team got.
    var bar = rows.append("rect")
      .attr("x", x(0)).attr("y", barCY - barH / 2)
      .attr("height", barH).attr("rx", 4)
      .style("fill", function (d) { return tierColor(d.tier); })
      .style("cursor", "pointer")
      .attr("width", function (d) {
        return startEmpty ? 0 : x(STAGE_X[d.stage]) - x(0);
      });
    bar.append("title").text(function (d) {
      return d.label + " (" + d.record + "). " + d.outcome
        + ". Sharp LAFI " + d.sharp + ". " + d.note;
    });
    bar.on("mouseenter", function () {
      d3.select(this).style("filter", "brightness(1.2)");
    }).on("mouseleave", function () {
      d3.select(this).style("filter", null);
    });

    // Outcome label, just past the bar end. Shortened on compact widths so
    // the label does not cross the Conference Finals wall.
    var lab = rows.append("text")
      .attr("y", barCY).attr("dy", "0.32em")
      .style("fill", function (d) {
        return d.tier === "missed" ? "var(--text-secondary)" : tierColor(d.tier);
      })
      .style("font", "600 12px var(--family-sans)")
      .style("opacity", startEmpty ? 0 : 1)
      .attr("x", function (d) { return x(STAGE_X[d.stage]) + 10; })
      .text(function (d) {
        return compact ? (SHORT_OUTCOME[d.outcome] || d.outcome) : d.outcome;
      });

    if (playIn) {
      bar.transition().duration(620)
        .delay(function (_, i) { return i * 90; })
        .ease(d3.easeCubicOut)
        .attr("width", function (d) { return x(STAGE_X[d.stage]) - x(0); });
      lab.transition().duration(300)
        .delay(function (_, i) { return i * 90 + 320; })
        .style("opacity", 1);
    }
  }

  render(false);
  if (reduceMotion) {
    /* already at final state */
  } else if (window.IntersectionObserver) {
    var io = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting && !hasEntered) {
        render(true);
        io.disconnect();
      }
    }, { threshold: 0.2 });
    io.observe(container);
  } else {
    render(true);
  }

  if (window.ResizeObserver) {
    new ResizeObserver(function () {
      var w = host.clientWidth || 640;
      if (w !== lastWidth) render(false);
    }).observe(host);
  }
})();
</script>
"""

PREVIEW_HARNESS = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LAFI cohort ladder, preview harness</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  /* Dev harness only. Production supplies these tokens via /tokens.css. */
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
  body { margin:0; padding:32px; background:#000; }
  .harness-note {
    max-width:840px; margin:0 auto 16px; color:rgba(255,255,255,.4);
    font:12px var(--family-sans);
  }
  .harness-stage { max-width:840px; margin:0 auto; }
</style>
</head>
<body>
<div class="harness-note">Local preview harness. The publishable artifact is cohort_ladder_fragment.html.</div>
<div class="harness-stage">
__FRAGMENT__
</div>
</body>
</html>
"""


def main():
    rows = load_rows()
    print("LAFI cohort ladder rows (display order):")
    for r in rows:
        print(f"  {r['label']:<20}{r['record']:<8}{r['outcome']:<22}"
              f"tier={r['tier']:<8}sharp={r['sharp']}")

    rows_json = json.dumps(rows, separators=(",", ":"))
    fragment = (FRAGMENT
                .replace("__VIZID__", VIZ_ID)
                .replace("__ROWS_JSON__", rows_json))

    out_dir = ROOT / "outputs/charts/q0a_lafi"
    frag_path = out_dir / "cohort_ladder_fragment.html"
    frag_path.write_text(fragment, encoding="utf-8")

    preview = PREVIEW_HARNESS.replace("__FRAGMENT__", fragment)
    prev_path = out_dir / "cohort_ladder_preview.html"
    prev_path.write_text(preview, encoding="utf-8")

    print(f"\nFragment : {frag_path} ({len(fragment)/1024:.1f} KB)  <- publish this")
    print(f"Preview  : {prev_path}  <- open this locally")
    print(f"\nviz id   : {VIZ_ID}")
    print(f"altText  : {ALT_TEXT}")


if __name__ == "__main__":
    main()
