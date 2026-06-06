---
name: viz-builder
description: Use this skill whenever building, editing, restyling, or debugging a data visualization for the Chasing the First Banner site. Trigger it for any D3 chart, any work on the `visualizations` collection, anything referenced by a `{{viz:id}}` shortcode, or requests like "make a chart for this article", "build a viz", "the chart colors look off", "add a tooltip to the chart". It encodes the design tokens, the HTML-fragment contract, and the interactivity and accessibility defaults so every chart matches the site without relitigating them each time.
---

# Viz Builder

Builds interactive D3 visualizations for Chasing the First Banner that match
the site's design system exactly. A visualization is authored once as a
self-contained HTML fragment, saved into the `visualizations` collection,
and referenced from an article with `{{viz:<id>}}`.

`CLAUDE.md` and `docs/chasing-the-first-banner-plan.md` override this skill
on any conflict. Read them first.

## The contract

A visualization is an **HTML fragment**, not a full document: a container
`<div>`, an optional `<style>`, and a `<script>`. It renders in two places
and must look identical in both:

1. **Static article page** (production SEO page). The publish pipeline
   inlines the fragment into `<figure class="viz" id="viz-<id>">`. The page
   already provides `/tokens.css`, `data-theme` on `<body>`, and D3 v7.
2. **Flutter app** (composer preview + in-app article page). The fragment
   runs in a sandboxed iframe (`lib/shared/widgets/viz_embed_web.dart`)
   that provides the same design tokens and D3 v7, and auto-sizes to the
   chart's height.

Rules that follow from this:

- **D3 v7 is a global.** Use `d3`. Do not add your own `<script src>` for
  D3. Other libraries are not available; keep it pure D3.
- **It is a fragment.** No `<!DOCTYPE>`, no `<head>`, no `<body>`.
- **One unique id.** The container is `<div id="viz-<kebab-id>">`. Two
  charts can share a page; nothing may collide.
- **The `<script>` runs inline on parse.** Wrap it in an IIFE
  (`(function(){ ... })();`) so its variables never leak.
- **Sandboxed.** No `localStorage`, no parent-window access, no network
  calls except D3 from the CDN. Embed the chart's data directly in the
  script as a JS literal.
- **It auto-sizes.** The iframe measures content height; do not assume a
  fixed viewport. Make the chart responsive to its container width.

## Design tokens

Use the CSS custom properties below. They resolve in both render
environments. Never hardcode a hex value that duplicates a token.

**Critical:** CSS variables are only valid in CSS *properties*, not in SVG
*presentation attributes*. Set every token-based color with D3's
`.style(...)`, never `.attr(...)`:

```js
bar.style("fill", "var(--accent-default)");   // correct
bar.attr("fill", "var(--accent-default)");    // WRONG: var() ignored
```

### Color

| Token | Value (dark) | Use for |
|---|---|---|
| `--accent-default` | `#00843D` | The primary series. The Wolves. The "one thing the chart is about." |
| `--accent-hover` | `#00A04A` | Hover/active state of the primary series. |
| `--accent-subtle` | `rgba(0,132,61,.18)` | Fills behind the primary series, zone shading. |
| `--dataviz-1..8` | see below | Categorical series when you need several distinct colors. |
| `--text-primary` | `#FFFFFF` | Value labels, axis emphasis. |
| `--text-secondary` | `rgba(255,255,255,.72)` | Category labels, axis text. |
| `--text-tertiary` | `rgba(255,255,255,.48)` | Gridlines text, captions, de-emphasized marks. |
| `--border-subtle` | `rgba(255,255,255,.08)` | Gridlines, axis baselines. |
| `--border-default` | `rgba(255,255,255,.16)` | Stronger axis lines. |
| `--status-error` | `#FF5C5C` | "Bad" values, negative deltas, the pickup zone. |
| `--status-warning` | `#F5A623` | Caution thresholds. |
| `--status-info` | `#4A9EFF` | Neutral callouts. |
| `--status-success` | `#00A04A` | "Good" values, positive deltas. |
| `--bg-surface` | `#0E0E0E` | Tooltip background, inset panels. |
| `--bg-inset` | `#050505` | Deepest insets. |

Categorical palette, in order: `--dataviz-1` `#00C457`, `--dataviz-2`
`#FFFFFF`, `--dataviz-3` `#4A9EFF`, `--dataviz-4` `#F5A623`, `--dataviz-5`
`#FF5C8A`, `--dataviz-6` `#B388FF`, `--dataviz-7` `#7CE7B8`, `--dataviz-8`
`#FFD166`.

Color discipline:

- One chart, one idea. The subject of the chart (usually the Wolves) is
  `--accent-default`. Everything else is quieter: `--text-tertiary`,
  `--border-default`, or a single muted gray.
- Reach for the `--dataviz-*` palette only for genuinely categorical data
  with no natural primary series. Use them in order.
- "Higher is worse" metrics (e.g. LAFI) trend `--accent-default` (good) to
  `--status-error` (bad). Do not invert.
- Never encode meaning by color alone. Pair it with position, a label, or
  a shape so it survives color-blindness and the PNG fallback.

### Type and spacing

- Font: `var(--family-sans)` (Inter) for everything; `var(--family-mono)`
  (JetBrains Mono) for numeric value labels so digits align.
- Sizes: 12px for axis/caption text, 13px for labels, 13 to 14px for value
  labels. The chart is not the place for large type; the article carries
  the headline.
- Spacing: multiples of 4. Use the `--space-*` tokens for any HTML chrome.
- Corner radius on bars/rects: `4` (matches `--radius-sm`).

## Responsiveness

A chart must look deliberate at any width, from a 360px phone to a wide
monitor. Pure SVG scaling is not enough: scaling a fixed drawing shrinks
text and marks until they are unreadable. Redraw instead. Four rules, all
implemented in the worked template below:

- **Clamp the drawing width.** `width = clamp(clientWidth, 320, 960)`.
  Below 320 nothing is usable; above 960 a chart reads as sparse. Set the
  `<svg>` to that pixel width with `max-width: 100%` and `margin: 0 auto`.
  Text then stays a true pixel size (13px is always 13px) and on a wide
  screen the chart centers rather than stretching.
- **Redraw on resize, never scale a stale drawing.** Re-run `render()`
  from a `ResizeObserver` on the container. Each render re-measures and
  re-lays-out.
- **Breakpoint at 480px.** Below it, simplify on purpose: move category
  labels above the marks instead of beside them, thin out axis ticks,
  shrink margins. Width-only reflow is not enough; the layout itself has
  to change or the chart is cramped on a phone. The specific traps are
  in "Phone-width pitfalls" below.
- **Height comes from the data.** Bar charts: `rowCount * rowHeight`.
  Scatter or line: an aspect ratio of the width. Always with a sensible
  minimum, never a hardcoded pixel height. The iframe auto-sizes to
  whatever height you compute.

Reuse the template's `render()` shape; it wires up all four.

### Phone-width pitfalls

The wide chart that looks great at 700px is the one most likely to break
at 360px. Three traps come up over and over:

- **Shrinking the left margin is not the fix.** A multi-word 13px label
  ("Isolation Reliance", "Shot Quality Decay") is 130 to 170px wide. Any
  left margin small enough to leave usable bar space cannot fit the
  label, so the label gets clipped off the left edge. The fix is to move
  the label above the bar at the breakpoint, not to compress the margin
  it lives in.
- **Anything that lived above the bar must relocate below in phone
  mode.** Comparison markers, callout values, secondary stats. They
  occupied the space the category label now claims, and they will
  collide unless you move them. Send them below the bar.
- **Bar-end labels can cross visual boundaries at narrow widths.** A
  label sitting just past the bar's right edge can extend through a
  wall, target line, or threshold zone and undercut the visual story.
  Provide a short variant for compact mode ("Lost in Round 2" becomes
  "Lost R2", "Missed the playoffs" becomes "Missed").

Resize the preview HTML to about 360px before saving. Every label should
render fully, no label should cross a wall or target line, and the
layout should look reflowed rather than scaled.

## Interactivity

Every chart should reward a cursor. Defaults:

- **Hover.** Lift the hovered mark: shift to `--accent-hover`, or raise
  opacity of the focused series and dim the rest.
- **Tooltip.** Simplest accessible tooltip is a `<title>` child on each
  mark (native, free, screen-reader friendly). For richer tooltips, build
  a positioned `<div>` styled with `--bg-surface`, `--border-subtle`,
  `--radius-md`, and `--text-primary`.
- **Transitions.** Animate on first render (bars grow, points fade in),
  ~600ms, `d3.easeCubicOut`, with a small per-element stagger.
- **Respect reduced motion.** Branch on it and render the final state
  immediately when set:
  ```js
  var reduceMotion =
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  ```

## Scroll passthrough

A chart trapped between the article and the footer is broken. By default,
interactive marks inside an SVG capture wheel events on desktop and touch
gestures on mobile, so the reader's vertical scroll dies the moment the
cursor or thumb crosses the chart. Every fragment must explicitly let the
page scroll through it.

Three things together. None of them alone is enough.

**1. CSS rule on the container and every descendant.** `touch-action`
does not inherit, so setting it on the container alone leaves the SVG and
its interactive marks with their defaults. Put a CSS rule at the top of
the fragment that covers all descendants:

```html
<style>
  /* Force vertical scroll/swipe to pass through every descendant. */
  #viz-<id>, #viz-<id> * { touch-action: manipulation; }
</style>
```

This is the single biggest fix for mobile. Without it, phone swipes die
inside the chart even if the JS is perfect. `manipulation` keeps pinch
zoom and single-finger pan and only suppresses double-tap-to-zoom.

**2. JS wheel forwarder for iframe embeds.** When the fragment runs
inside an iframe (the Flutter app and the composer preview), wheel events
don't bubble to the outer article. Forward them to the parent:

```js
if (window.parent !== window) {
  root.node().addEventListener("wheel", function (e) {
    if (e.ctrlKey || e.metaKey) return; // pinch-zoom intent on trackpads
    try {
      window.parent.scrollBy(e.deltaX, e.deltaY);
    } catch (err) {
      window.parent.postMessage({
        type: "viz-scroll",
        deltaX: e.deltaX,
        deltaY: e.deltaY
      }, "*");
    }
  }, { passive: true });
}
```

**3. JS touchmove forwarder for iframe embeds.** Same logic for mobile,
in case the iframe still consumes touch events despite the CSS rule:

```js
if (window.parent !== window) {
  var lastTouchY = null;
  root.node().addEventListener("touchstart", function (e) {
    if (e.touches.length === 1) lastTouchY = e.touches[0].clientY;
  }, { passive: true });
  root.node().addEventListener("touchmove", function (e) {
    if (e.touches.length !== 1 || lastTouchY === null) return;
    var y = e.touches[0].clientY;
    var dy = lastTouchY - y;
    lastTouchY = y;
    try {
      window.parent.scrollBy(0, dy);
    } catch (err) {
      window.parent.postMessage({
        type: "viz-scroll",
        deltaX: 0,
        deltaY: dy
      }, "*");
    }
  }, { passive: true });
}
```

All three blocks go right after the `var root = d3.select(...)` line, so
they run once when the fragment loads. When the fragment uses a
`var container = document.getElementById(ID)` pattern (cohort ladder,
fingerprint), swap `root.node()` for `container`.

### Why all three

`touch-action` alone is the right idea on paper, but in practice the
SVG inside `.fp-host` or `.cl-host` does not inherit container styles,
so the rule must explicitly target descendants. The wheel and touchmove
forwarders cover the iframe case where the gesture has nowhere natural
to bubble to.

### Host-side responsibility

`scrollBy` on `window.parent` works when the iframe is same-origin. When
it is cross-origin (the Flutter web app may load fragments from a CDN),
`scrollBy` throws and the fragment falls through to `postMessage`. For
that path to actually scroll the article, the iframe wrapper
(`lib/shared/widgets/viz_embed_web.dart`) must add a `message` listener
that calls `window.scrollBy` on `{ type: 'viz-scroll' }` events. If you
change the wrapper, keep it in sync with this contract.

Pure-HTML fragments (no D3, no script) only need the CSS rule. Touch and
wheel forwarders depend on the script being there.

## Watermark and date stamp

Every chart carries a small credit line that ships with it, so a
screenshot lifted from the site still names where it came from and when
it was made. The line sits in the bottom-right of the SVG (or the
bottom-right of the container, for pure-HTML fragments) in
`--text-tertiary` at low opacity. Visible to a deliberate eye, ignorable
during normal reading.

Format: `@WolvesToaT · MMM YYYY` (handle, middle dot, month-year). Use the
publication month of the article that hosts the chart, not the current
runtime date, so the stamp is a true provenance marker rather than a
moving target. Month-year granularity is enough; day-level precision
reads as fussy and dates the work artificially.

Snippet, appended at the end of `render()` after all chart elements so
it draws on top:

```js
// Watermark + date stamp. Travels with the chart in screenshots.
svg.append("text")
  .attr("x", width - 6)
  .attr("y", height - 6)
  .attr("text-anchor", "end")
  .style("fill", "var(--text-tertiary)")
  .style("font", "9px var(--family-sans)")
  .style("opacity", 0.55)
  .style("pointer-events", "none")
  .text("@WolvesToaT · May 2026");
```

For pure-HTML fragments (no SVG), add a small div instead:

```html
<div class="<viz-id>-watermark">@WolvesToaT · May 2026</div>
```

```css
#<viz-id> .<viz-id>-watermark {
  font: 9px var(--family-sans);
  color: var(--text-tertiary);
  opacity: 0.55;
  text-align: right;
  margin-top: 12px;
}
```

Do not use the @ as a literal email or social handle hyperlink. It is a
credit mark, not a navigational element. Pointer-events on the SVG text
are disabled so it never steals a hover from the chart.

## Accessibility

- The `<svg>` gets `role="img"`. The article-level alt text lives on the
  `visualizations/<id>.altText` field (a required, complete sentence);
  the chart itself does not need to repeat it, but every mark should have
  a `<title>` so hover/AT users get the values.
- Text must clear WCAG AA against `#000`. The token text colors already
  do; if you tint text, re-check.
- Never rely on color alone (see color discipline above).

## Scoping

- The container id is unique: `viz-<kebab-id>` matching the `vizId`.
- Prefer setting styles through D3 (`.style(...)`, `.attr(...)`) over a
  `<style>` block. D3-set styles cannot leak.
- If you must use a `<style>` block, scope **every** selector under the
  container id: `#viz-<id> .bar { ... }`. An unscoped `.bar` rule would
  bleed into other charts on the same static page.

## Hard constraints

From `CLAUDE.md`, non-negotiable:

- No em dashes or en dashes anywhere, including chart labels, comments,
  and tooltip text. Use commas, periods, colons, parentheses.
- Do not reproduce the Timberwolves wordmark, logos, or the trademarked
  jersey tree pattern.
- Do not republish figures or data from paid sources (Cleaning the Glass,
  Synergy). Cite findings; do not copy charts.

## Worked template

A responsive, interactive, token-driven horizontal bar chart. It clamps
its width, reflows its layout below 480px, derives height from the data,
and keeps text at a true pixel size. Copy it, rename `viz-CHANGEME` to the
real `vizId`, and replace the `data` literal.

```html
<div id="viz-CHANGEME"></div>
<style>
  /* Force vertical scroll/swipe to pass through every descendant. */
  #viz-CHANGEME, #viz-CHANGEME * { touch-action: manipulation; }
</style>
<script>
(function () {
  // Data: embed it here as a JS literal. label drives the row, value the bar.
  var data = [
    { label: "Example A", value: 72 },
    { label: "Example B", value: 58 },
    { label: "Example C", value: 41 }
  ];

  var root = d3.select("#viz-CHANGEME");
  var reduceMotion =
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Scroll passthrough. The CSS rule above handles touch on every
  // descendant; these forwarders handle the iframe-embedded cases for
  // both wheel (desktop) and touchmove (mobile fallback).
  if (window.parent !== window) {
    root.node().addEventListener("wheel", function (e) {
      if (e.ctrlKey || e.metaKey) return;
      try {
        window.parent.scrollBy(e.deltaX, e.deltaY);
      } catch (err) {
        window.parent.postMessage({
          type: "viz-scroll",
          deltaX: e.deltaX,
          deltaY: e.deltaY
        }, "*");
      }
    }, { passive: true });
    var lastTouchY = null;
    root.node().addEventListener("touchstart", function (e) {
      if (e.touches.length === 1) lastTouchY = e.touches[0].clientY;
    }, { passive: true });
    root.node().addEventListener("touchmove", function (e) {
      if (e.touches.length !== 1 || lastTouchY === null) return;
      var y = e.touches[0].clientY;
      var dy = lastTouchY - y;
      lastTouchY = y;
      try {
        window.parent.scrollBy(0, dy);
      } catch (err) {
        window.parent.postMessage({
          type: "viz-scroll",
          deltaX: 0,
          deltaY: dy
        }, "*");
      }
    }, { passive: true });
  }

  function render() {
    root.selectAll("*").remove();

    // Clamp: unusable below 320, sparse above 960.
    var raw = root.node().clientWidth || 640;
    var width = Math.max(320, Math.min(960, raw));
    var compact = width < 480;

    // Layout reflows at the breakpoint, not just the width.
    var rowH = compact ? 58 : 46;
    var barH = compact ? 16 : 22;
    var margin = {
      top: 8,
      right: 48,
      bottom: 8,
      left: compact ? 4 : 132
    };
    // Height comes from the data, never hardcoded.
    var height = margin.top + margin.bottom + data.length * rowH;

    // Pixel width + max-width keeps text true-size and centers on wide
    // screens instead of stretching.
    var svg = root.append("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", "0 0 " + width + " " + height)
      .attr("role", "img")
      .style("display", "block")
      .style("max-width", "100%")
      .style("margin", "0 auto");

    var x = d3.scaleLinear()
      .domain([0, d3.max(data, function (d) { return d.value; })])
      .nice()
      .range([margin.left, width - margin.right]);

    function rowTop(i) { return margin.top + i * rowH; }
    var barOffset = compact ? 24 : (rowH - barH) / 2;

    // Category label: beside the bar when wide, above it when compact.
    svg.append("g").selectAll("text").data(data).join("text")
      .attr("x", compact ? margin.left : margin.left - 12)
      .attr("y", function (d, i) {
        return rowTop(i) + (compact ? 13 : rowH / 2);
      })
      .attr("dy", compact ? "0" : "0.35em")
      .attr("text-anchor", compact ? "start" : "end")
      .style("fill", "var(--text-secondary)")
      .style("font", "13px var(--family-sans)")
      .text(function (d) { return d.label; });

    // Bars.
    var bars = svg.append("g").selectAll("rect").data(data).join("rect")
      .attr("x", margin.left)
      .attr("y", function (d, i) { return rowTop(i) + barOffset; })
      .attr("height", barH)
      .attr("rx", 4)
      .style("fill", "var(--accent-default)")
      .style("cursor", "pointer")
      .attr("width", reduceMotion
        ? function (d) { return x(d.value) - margin.left; }
        : 0);

    bars.append("title")
      .text(function (d) { return d.label + ": " + d.value; });

    bars
      .on("mouseenter", function () {
        d3.select(this).style("fill", "var(--accent-hover)");
      })
      .on("mouseleave", function () {
        d3.select(this).style("fill", "var(--accent-default)");
      });

    if (!reduceMotion) {
      bars.transition()
        .duration(600)
        .delay(function (_, i) { return i * 80; })
        .ease(d3.easeCubicOut)
        .attr("width", function (d) { return x(d.value) - margin.left; });
    }

    // Value labels, monospace so digits align.
    svg.append("g").selectAll("text").data(data).join("text")
      .attr("x", function (d) { return x(d.value) + 8; })
      .attr("y", function (d, i) {
        return rowTop(i) + barOffset + barH / 2;
      })
      .attr("dy", "0.35em")
      .style("fill", "var(--text-primary)")
      .style("font", "600 13px var(--family-mono)")
      .text(function (d) { return d.value; });

    // Watermark + date stamp. Travels with the chart in screenshots.
    svg.append("text")
      .attr("x", width - 6)
      .attr("y", height - 6)
      .attr("text-anchor", "end")
      .style("fill", "var(--text-tertiary)")
      .style("font", "9px var(--family-sans)")
      .style("opacity", 0.55)
      .style("pointer-events", "none")
      .text("@WolvesToaT · May 2026");
  }

  render();
  if (window.ResizeObserver) {
    new ResizeObserver(render).observe(root.node());
  }
})();
</script>
```

## Publishing workflow

1. Build the fragment per the contract above.
2. Open `/admin/visualizations/new`. Set the title, the viz id
   (kebab-case; this is the `{{viz:id}}` key and the `viz-<id>` container
   id, so keep them consistent), and a complete-sentence alt text.
3. Paste the fragment into the HTML field. Save.
4. In the article composer, place the cursor and use "Insert
   visualization", or type `{{viz:<id>}}` on its own line.
5. Publish or republish the article. The pipeline inlines the fragment;
   the in-app article reads it live from Firestore.

## Pre-save checklist

- [ ] Fragment only: container `<div>`, optional scoped `<style>`, IIFE
      `<script>`. No `<head>`/`<body>`/doctype.
- [ ] Container id is `viz-<vizId>`, unique.
- [ ] No `<script src>` for D3; uses the `d3` global.
- [ ] All token colors set via `.style(...)`, never `.attr("fill", ...)`.
- [ ] Width clamped to 320..960; `<svg>` uses a pixel width plus
      `max-width: 100%` and `margin: 0 auto` (true-size text, centered).
- [ ] Layout reflows at the 480px breakpoint, not just the width.
- [ ] Height derived from the data; no hardcoded pixel height.
- [ ] Redraws from a `ResizeObserver`.
- [ ] Hover state and `<title>` tooltips on every mark.
- [ ] Enter transition with a `prefers-reduced-motion` branch.
- [ ] Scroll passthrough: a CSS rule
      `#viz-<id>, #viz-<id> * { touch-action: manipulation; }` plus, for
      iframe embeds, JS forwarders for both `wheel` (desktop) and
      `touchmove` (mobile fallback). The page must scroll vertically
      through the chart on phone (swipe) and desktop (wheel) while
      hover/tap interactions still work.
- [ ] Watermark + date stamp in the bottom-right of the SVG (or the
      container for pure-HTML fragments). Format: `@WolvesToaT · MMM YYYY`,
      using the article's publication month.
- [ ] No meaning encoded by color alone.
- [ ] No em or en dashes anywhere in the fragment.
- [ ] `altText` written on the visualization doc.
