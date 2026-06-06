"""Build the LAFI fingerprint visualization for Chasing the First Banner.

Conforms to the viz-builder skill contract: the deliverable is a self-contained
HTML *fragment* (container div + scoped style + IIFE script), pure D3 v7 against
the `d3` global, site design tokens via .style(), responsive, accessible.

Outputs two files in outputs/charts/q0a_lafi/:
  fingerprint_fragment.html  -- THE DELIVERABLE. Paste into /admin/visualizations/new.
  fingerprint_preview.html   -- a local dev harness (full doc: D3 CDN + design
                                tokens + the fragment + a scroll spacer so the
                                scroll-triggered entrance can be reviewed).

viz id: lafi-fingerprint-2025-26   (container id: viz-lafi-fingerprint-2025-26)

Values load from the canonical Q0A composite output, never hardcoded.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
VIZ_ID = "lafi-fingerprint-2025-26"

# key -> (display name, short descriptor)
COMPONENT_META = {
    "C1": ("Ball Stickiness", "How much one player dominates the ball"),
    "C2": ("Motion Death", "How much the off-ball players move"),
    "C3": ("Isolation Reliance", "How often possessions end one-on-one"),
    "C4": ("Action Poverty", "How narrow the playbook is"),
    "C5": ("Shot Quality Decay", "Whether the resulting shots are good"),
}

# Comparison teams. Each teaches something different.
COMPARISON_SPECS = [
    ("SAS", 2025, "SAS2025", "vs Spurs '25-26",
     "San Antonio Spurs, 2025-26. The team that bounced the Wolves from the second round, and near the opposite end of every component that matters."),
    ("PHI", 2021, "PHI2021", "vs 76ers '21-22",
     "Philadelphia 76ers, 2021-22. A cohort team. Joel Embiid finished second in MVP voting that year, and they still lost in the second round."),
    ("DEN", 2022, "DEN2022", "vs Nuggets '22-23",
     "Denver Nuggets, 2022-23. The 2023 champions, one of the most designed offenses of the tracking era."),
    ("MIN", 2023, "MIN2023", "vs Wolves '23-24",
     "Minnesota Timberwolves, 2023-24. The Wolves' own conference finals team two seasons earlier, with a very different fingerprint."),
]

SHARP_RANK = "3rd in the NBA. The three components that decide playoff offense."
FULL_RANK = "13th in the NBA. All five components together."

ALT_TEXT = (
    "Horizontal bar chart of the 2025-26 Minnesota Timberwolves' five LAFI "
    "components. Three ridges are extreme: Isolation Reliance at the 90th "
    "percentile, Shot Quality Decay at 83, and Motion Death at 72. Two are "
    "moderate: Action Poverty at 45 and Ball Stickiness at 31. The composite "
    "scores are Sharp LAFI 90 and Full LAFI 65."
)


def fingerprint(comp: pd.DataFrame, team: str, year: int) -> dict:
    r = comp[(comp.team_abbreviation == team)
             & (comp.season_start_year == year)
             & (comp.season_type == "Regular Season")].iloc[0]
    return {
        "C1": round(r.C1_ball_stickiness_pct),
        "C2": round(r.C2_movement_death_pct),
        "C3": round(r.C3_isolation_reliance_pct),
        "C4": round(r.C4_action_poverty_pct),
        "C5": round(r.C5_shot_quality_decay_pct),
        "sharp": round(r.sharp_lafi_pct),
        "full": round(r.lafi_pct),
    }


def load_data():
    comp = pd.read_csv(ROOT / "outputs/tables/q0a_lafi/lafi_composite_5component.csv")
    wolves = fingerprint(comp, "MIN", 2025)

    order = sorted(("C1", "C2", "C3", "C4", "C5"), key=lambda k: wolves[k], reverse=True)
    components = [{
        "key": k, "name": COMPONENT_META[k][0], "desc": COMPONENT_META[k][1],
        "value": wolves[k],
    } for k in order]

    comparisons = {}
    for team, year, cid, pill, context in COMPARISON_SPECS:
        fp = fingerprint(comp, team, year)
        comparisons[cid] = {
            "pill": pill, "context": context,
            "vals": {k: fp[k] for k in ("C1", "C2", "C3", "C4", "C5")},
            "sharp": fp["sharp"], "full": fp["full"],
        }
    return wolves, components, comparisons


# ---------------------------------------------------------------------------
# Fragment
# ---------------------------------------------------------------------------

FRAGMENT = r"""<div id="viz-__VIZID__">
  <div class="fp-pills" role="group" aria-label="Compare another team">
__PILLS__
  </div>
  <p class="fp-context" aria-live="polite"></p>
  <div class="fp-host"></div>
  <div class="fp-tiles">
    <div class="fp-tile">
      <span class="fp-tile-num" data-bucket="__SHARP_BUCKET__">__SHARP__</span>
      <span class="fp-tile-text">
        <span class="fp-tile-name">Sharp LAFI</span>
        <span class="fp-tile-sub">__SHARP_RANK__</span>
        <span class="fp-tile-cmp" data-k="sharp"></span>
      </span>
    </div>
    <div class="fp-tile">
      <span class="fp-tile-num" data-bucket="__FULL_BUCKET__">__FULL__</span>
      <span class="fp-tile-text">
        <span class="fp-tile-name">Full LAFI</span>
        <span class="fp-tile-sub">__FULL_RANK__</span>
        <span class="fp-tile-cmp" data-k="full"></span>
      </span>
    </div>
  </div>
</div>
<style>
  #viz-__VIZID__ { font-family: var(--family-sans); color: var(--text-primary); }
  #viz-__VIZID__ .fp-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
  #viz-__VIZID__ .fp-pill {
    background: var(--bg-surface); color: var(--text-secondary);
    border: 1px solid var(--border-subtle); border-radius: 999px;
    padding: 6px 14px; font: 600 12px var(--family-sans); cursor: pointer;
    transition: color 150ms ease, border-color 150ms ease, background 150ms ease;
  }
  #viz-__VIZID__ .fp-pill:hover { color: var(--text-primary); border-color: var(--border-default); }
  #viz-__VIZID__ .fp-pill.is-on { background: var(--status-info); color: var(--bg-inset); border-color: var(--status-info); }
  #viz-__VIZID__ .fp-pill[data-cmp=""].is-on { background: var(--accent-default); color: var(--bg-inset); border-color: var(--accent-default); }
  #viz-__VIZID__ .fp-context {
    margin: 0 0 14px 0; padding-left: 12px; min-height: 18px;
    border-left: 2px solid var(--status-info);
    font: 13px/1.5 var(--family-sans); color: var(--text-secondary);
    opacity: 0; transition: opacity 200ms ease;
  }
  #viz-__VIZID__ .fp-context.is-shown { opacity: 1; }
  #viz-__VIZID__ .fp-tiles { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; }
  #viz-__VIZID__ .fp-tile {
    flex: 1; min-width: 240px; display: flex; align-items: baseline; gap: 12px;
    background: var(--bg-surface); border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md); padding: 14px 16px;
  }
  #viz-__VIZID__ .fp-tile-num { font: 800 32px var(--family-mono); line-height: 1; }
  #viz-__VIZID__ .fp-tile-num[data-bucket="error"] { color: var(--status-error); }
  #viz-__VIZID__ .fp-tile-num[data-bucket="warning"] { color: var(--status-warning); }
  #viz-__VIZID__ .fp-tile-num[data-bucket="accent"] { color: var(--accent-default); }
  #viz-__VIZID__ .fp-tile-text { display: flex; flex-direction: column; gap: 2px; }
  #viz-__VIZID__ .fp-tile-name { font: 700 13px var(--family-sans); }
  #viz-__VIZID__ .fp-tile-sub { font: 11.5px/1.4 var(--family-sans); color: var(--text-tertiary); }
  #viz-__VIZID__ .fp-tile-cmp {
    font: 700 11.5px var(--family-mono); color: var(--status-info); margin-top: 3px;
    opacity: 0; transition: opacity 200ms ease;
  }
  #viz-__VIZID__ .fp-tile-cmp.is-shown { opacity: 1; }
</style>
<script>
(function () {
  var ID = "viz-__VIZID__";
  var WOLVES = __WOLVES_JSON__;
  var COMPARISONS = __COMPARISONS_JSON__;

  var container = document.getElementById(ID);
  if (!container || typeof d3 === "undefined") return;
  var host = container.querySelector(".fp-host");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var currentCmp = null;
  var hasEntered = false;     // becomes true once the entrance animation has run
  var lastWidth = 0;          // guards the ResizeObserver against its spurious first fire

  function bucketColor(v) {
    if (v >= 66) return "var(--status-error)";
    if (v >= 34) return "var(--status-warning)";
    return "var(--accent-default)";
  }

  // animate=true plays the entrance (bars grow, values count up). Otherwise the
  // chart is drawn in its resting state: empty before the entrance, full after.
  function render(animate) {
    var playIn = animate && !reduceMotion;
    if (playIn) hasEntered = true;
    var settled = reduceMotion || hasEntered;

    var root = d3.select(host);
    root.selectAll("*").remove();
    var width = host.clientWidth || 640;
    lastWidth = width;
    // Three layout modes. Phone stacks the component label above the bar
    // because no left margin small enough to leave bar space is wide enough
    // to fit "Isolation Reliance" or "Shot Quality Decay" beside it.
    var phone = width < 480;
    var narrow = width < 640;
    var marginL = phone ? 12 : (narrow ? 146 : 206);
    var marginR = phone ? 36 : 44;
    var rowH = phone ? 72 : (narrow ? 48 : 58);
    var top = 38, bottom = 10;
    var height = top + bottom + WOLVES.length * rowH;

    var svg = root.append("svg")
      .attr("width", "100%")
      .attr("viewBox", "0 0 " + width + " " + height)
      .attr("role", "img");

    var x = d3.scaleLinear().domain([0, 100]).range([marginL, width - marginR]);
    var trackH = 20;
    var startEmpty = playIn || !settled;

    // Pickup zone: the extreme third of the scale.
    svg.append("rect")
      .attr("x", x(66)).attr("y", top)
      .attr("width", x(100) - x(66)).attr("height", height - top - bottom)
      .style("fill", "var(--status-error)").style("fill-opacity", 0.07);

    var rows = svg.append("g").selectAll("g").data(WOLVES).join("g")
      .attr("transform", function (d, i) { return "translate(0," + (top + i * rowH) + ")"; });
    var cy = phone ? 40 : rowH / 2;

    if (phone) {
      // Phone: label above the bar, anchored to the left edge.
      rows.append("text")
        .attr("x", marginL).attr("y", 16)
        .style("fill", "var(--text-primary)").style("font", "600 13px var(--family-sans)")
        .text(function (d) { return d.name; });
    } else {
      rows.append("text")
        .attr("x", marginL - 12).attr("y", cy - (narrow ? 0 : 7)).attr("dy", "0.32em")
        .attr("text-anchor", "end")
        .style("fill", "var(--text-primary)").style("font", "600 13px var(--family-sans)")
        .text(function (d) { return d.name; });
      if (!narrow) {
        rows.append("text")
          .attr("x", marginL - 12).attr("y", cy + 9).attr("dy", "0.32em")
          .attr("text-anchor", "end")
          .style("fill", "var(--text-tertiary)").style("font", "11px var(--family-sans)")
          .text(function (d) { return d.desc; });
      }
    }

    // Track background.
    rows.append("rect")
      .attr("x", x(0)).attr("y", cy - trackH / 2)
      .attr("width", x(100) - x(0)).attr("height", trackH).attr("rx", 4)
      .style("fill", "var(--bg-inset)").style("stroke", "var(--border-subtle)");

    // The Wolves' bar.
    var bar = rows.append("rect")
      .attr("x", x(0)).attr("y", cy - trackH / 2)
      .attr("height", trackH).attr("rx", 4)
      .style("fill", function (d) { return bucketColor(d.value); })
      .style("cursor", "pointer")
      .attr("width", startEmpty ? 0 : function (d) { return x(d.value) - x(0); });
    bar.append("title").text(function (d) {
      return d.name + ": " + d.value + "th percentile. " + d.desc + ".";
    });
    bar.on("mouseenter", function () { d3.select(this).style("filter", "brightness(1.18)"); })
       .on("mouseleave", function () { d3.select(this).style("filter", null); });

    // Wolves value label, monospace.
    var val = rows.append("text")
      .attr("x", width - marginR + 8).attr("y", cy).attr("dy", "0.32em")
      .style("fill", function (d) { return bucketColor(d.value); })
      .style("font", "700 14px var(--family-mono)")
      .text(function (d) { return startEmpty ? 0 : d.value; });

    // Entrance: bars grow, values count up in sync. Staggered, once.
    if (playIn) {
      bar.transition().duration(660).delay(function (_, i) { return i * 95; })
        .ease(d3.easeCubicOut)
        .attr("width", function (d) { return x(d.value) - x(0); });
      val.transition().duration(660).delay(function (_, i) { return i * 95; })
        .ease(d3.easeCubicOut)
        .tween("text", function (d) {
          var node = this, interp = d3.interpolateNumber(0, d.value);
          return function (t) { node.textContent = Math.round(interp(t)); };
        });
    }

    // Comparison markers.
    if (currentCmp) {
      var cmp = COMPARISONS[currentCmp];
      var mk = rows.append("g").style("opacity", reduceMotion ? 1 : 0);
      mk.append("line")
        .attr("x1", function (d) { return x(cmp.vals[d.key]); })
        .attr("x2", function (d) { return x(cmp.vals[d.key]); })
        .attr("y1", cy - trackH / 2 - 4).attr("y2", cy + trackH / 2 + 4)
        .style("stroke", "var(--status-info)").style("stroke-width", 2);
      var dot = mk.append("circle")
        .attr("cx", function (d) { return x(cmp.vals[d.key]); }).attr("cy", cy)
        .attr("r", 5)
        .style("fill", "var(--status-info)")
        .style("stroke", "var(--bg-inset)").style("stroke-width", 2);
      dot.append("title").text(function (d) {
        return cmp.pill.replace("vs ", "") + " " + d.name + ": " + cmp.vals[d.key] + "th percentile.";
      });
      mk.append("text")
        .attr("x", function (d) { return x(cmp.vals[d.key]); })
        .attr("y", phone ? cy + trackH / 2 + 12 : cy - trackH / 2 - 9)
        .attr("text-anchor", "middle")
        .style("fill", "var(--status-info)").style("font", "700 10px var(--family-mono)")
        .text(function (d) { return cmp.vals[d.key]; });
      if (!reduceMotion) mk.transition().duration(300).style("opacity", 1);
    }

    // League-average reference line. Drawn last so it stays visible over the bars.
    svg.append("line")
      .attr("x1", x(50)).attr("x2", x(50)).attr("y1", top - 18).attr("y2", height - bottom)
      .style("stroke", "var(--text-secondary)").style("stroke-width", 1.5)
      .style("stroke-dasharray", "5 4");
    svg.append("text")
      .attr("x", x(50)).attr("y", top - 23).attr("text-anchor", "middle")
      .style("fill", "var(--text-secondary)")
      .style("font", "600 10.5px var(--family-sans)")
      .style("letter-spacing", "0.05em")
      .text("LEAGUE AVERAGE");
  }

  function updateChrome() {
    container.querySelectorAll(".fp-pill").forEach(function (p) {
      p.classList.toggle("is-on", (p.dataset.cmp || "") === (currentCmp || ""));
    });
    var ctx = container.querySelector(".fp-context");
    if (currentCmp) {
      ctx.textContent = COMPARISONS[currentCmp].context;
      ctx.classList.add("is-shown");
    } else {
      ctx.classList.remove("is-shown");
    }
    container.querySelectorAll(".fp-tile-cmp").forEach(function (el) {
      if (currentCmp) {
        var c = COMPARISONS[currentCmp];
        el.textContent = c.pill.replace("vs ", "") + ":  " + c[el.dataset.k];
        el.classList.add("is-shown");
      } else {
        el.classList.remove("is-shown");
      }
    });
  }

  container.querySelectorAll(".fp-pill").forEach(function (p) {
    p.addEventListener("click", function () {
      currentCmp = p.dataset.cmp || null;
      updateChrome();
      render(false);
    });
  });

  // Initial draw: resting state. The entrance fires when the chart scrolls
  // into view (IntersectionObserver), so the animation greets the reader
  // rather than finishing before they arrive.
  render(false);
  if (reduceMotion) {
    /* already at final state */
  } else if (window.IntersectionObserver) {
    var io = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting && !hasEntered) {
        render(true);
        io.disconnect();
      }
    }, { threshold: 0.25 });
    io.observe(container);
  } else {
    render(true);
  }

  // Redraw on real width changes only (skip the ResizeObserver's first fire).
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
<title>LAFI fingerprint, preview harness</title>
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
<div class="harness-note">Local preview harness. The publishable artifact is fingerprint_fragment.html.</div>
<div class="harness-stage">
__FRAGMENT__
</div>
</body>
</html>
"""


def build_pills(comparisons: dict) -> str:
    pills = ['    <button class="fp-pill is-on" data-cmp="" type="button">Just the Wolves</button>']
    for cid, c in comparisons.items():
        pills.append(f'    <button class="fp-pill" data-cmp="{cid}" type="button">{c["pill"]}</button>')
    return "\n".join(pills)


def value_bucket(v: int) -> str:
    if v >= 66:
        return "error"
    if v >= 34:
        return "warning"
    return "accent"


def main():
    wolves, components, comparisons = load_data()
    print("Wolves 2025-26 LAFI fingerprint:")
    for c in components:
        print(f"  {c['name']:<22}{c['value']:>4}   {value_bucket(c['value'])}")
    print(f"  Sharp LAFI            {wolves['sharp']:>4}")
    print(f"  Full LAFI             {wolves['full']:>4}")

    wolves_json = json.dumps(components, separators=(",", ":"))
    comparisons_json = json.dumps(comparisons, separators=(",", ":"))

    fragment = (FRAGMENT
                .replace("__VIZID__", VIZ_ID)
                .replace("__PILLS__", build_pills(comparisons))
                .replace("__WOLVES_JSON__", wolves_json)
                .replace("__COMPARISONS_JSON__", comparisons_json)
                .replace("__SHARP__", str(wolves["sharp"]))
                .replace("__FULL__", str(wolves["full"]))
                .replace("__SHARP_BUCKET__", value_bucket(wolves["sharp"]))
                .replace("__FULL_BUCKET__", value_bucket(wolves["full"]))
                .replace("__SHARP_RANK__", SHARP_RANK)
                .replace("__FULL_RANK__", FULL_RANK))

    out_dir = ROOT / "outputs/charts/q0a_lafi"
    frag_path = out_dir / "fingerprint_fragment.html"
    frag_path.write_text(fragment, encoding="utf-8")

    preview = PREVIEW_HARNESS.replace("__FRAGMENT__", fragment)
    prev_path = out_dir / "fingerprint_preview.html"
    prev_path.write_text(preview, encoding="utf-8")

    print(f"\nFragment : {frag_path} ({len(fragment)/1024:.1f} KB)  <- publish this")
    print(f"Preview  : {prev_path}  <- open this locally")
    print(f"\nviz id   : {VIZ_ID}")
    print(f"altText  : {ALT_TEXT}")


if __name__ == "__main__":
    main()
