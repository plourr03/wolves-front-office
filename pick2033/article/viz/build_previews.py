"""Regenerates the preview_part*.html harness files from the canonical
*_fragment.html files, in article order. The fragments are the publishable
artifacts; the previews are throwaway local test pages (720/480/360 width
toolbar, site design tokens, D3 v7 from the CDN).

Run from anywhere: python article/viz/build_previews.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent

PARTS = {
    1: ("Part 1, The Tenure Bet", [
        "spell_lengths_fragment.html",
        "tenure_forces_fragment.html",
        "edwards_hazard_fragment.html",
        "edwards_cumulative_fragment.html",
    ]),
    2: ("Part 2, Fifty Thousand Futures", [
        "cohort_crest_fragment.html",
        "win_fancharts_fragment.html",
        "slot_distribution_fragment.html",
        "edwards_split_fragment.html",
    ]),
    3: ("Part 3, The Bill", [
        "swap_ledger_fragment.html",
        "cost_quadrants_fragment.html",
        "replay_2013_fragment.html",
        "equity_bill_fragment.html",
        "tornado_fragment.html",
    ]),
}

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}, viz preview harness</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  :root {{
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
  }}
  body {{ margin:0; padding:32px; background:#000; }}
  .harness-note {{ max-width:720px; margin:0 auto 16px; color:rgba(255,255,255,.4); font:12px var(--family-sans); }}
  .harness-toolbar {{ max-width:720px; margin:0 auto 12px; display:flex; gap:8px; align-items:center; color:rgba(255,255,255,.6); font:11px var(--family-sans); }}
  .harness-toolbar button {{ background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.16); color:rgba(255,255,255,.85); padding:4px 10px; border-radius:6px; font:11px var(--family-sans); cursor:pointer; }}
  .harness-toolbar button:hover {{ background:rgba(255,255,255,.12); }}
  .harness-stage {{ max-width:720px; margin:0 auto; }}
  .harness-sep {{ max-width:720px; margin:36px auto; border:0; border-top:1px solid rgba(255,255,255,.1); }}
</style>
</head>
<body>
<div class="harness-note">Local preview harness for {title}. The publishable artifacts are the *_fragment.html files; this file is generated, do not edit by hand.</div>
<div class="harness-toolbar">
  <span>Test widths:</span>
  <button onclick="document.querySelectorAll('.harness-stage').forEach(function(s){{s.style.maxWidth='720px'}})">720</button>
  <button onclick="document.querySelectorAll('.harness-stage').forEach(function(s){{s.style.maxWidth='480px'}})">480</button>
  <button onclick="document.querySelectorAll('.harness-stage').forEach(function(s){{s.style.maxWidth='360px'}})">360 (phone)</button>
  <button onclick="window.location.reload()">Hard reload</button>
</div>
"""


def main():
    for n, (title, fragments) in PARTS.items():
        stages = []
        for f in fragments:
            body = (HERE / f).read_text(encoding="utf-8").strip()
            stages.append('<div class="harness-stage">\n' + body + "\n</div>")
        html = (HEAD.format(title=title)
                + '\n<hr class="harness-sep">\n'.join(stages)
                + "\n</body>\n</html>\n")
        out = HERE / f"preview_part{n}.html"
        out.write_text(html, encoding="utf-8")
        print(f"{out.name}: {len(fragments)} fragments")


if __name__ == "__main__":
    main()
