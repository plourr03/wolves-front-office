#!/usr/bin/env python3
"""Export the series as plain markdown for the cross-read.

The four parts, the four feeds (each part's short version, pull-quotes and slide copy in one
file), the index and the rendered methods page are written to `outputs/crossread/` with:

  - every `{{viz:<id>}}` tag replaced by a bracketed placeholder naming the visual
  - the fragility sentences bracketed as PENDING (they are under review after D111, and the
    parts are not edited until that review is read)
  - a header line on each file with the source path, the export run ID and the git commit

Nothing in `docs/series/` is modified.

    python kuminga/scripts/export_crossread.py
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

SERIES = os.path.join(REPO, "kuminga", "docs", "series")
DOCS = os.path.join(REPO, "kuminga", "docs")
OUT = os.path.join(REPO, "kuminga", "outputs", "crossread")

VIZ = re.compile(r"\{\{viz:([a-z0-9-]+)\}\}")

# the sentences under review (D111 changed the fragility figures and the top-three set);
# each is bracketed in place, verbatim, so the reader sees exactly what is pending
PENDING = {
    "part2.md": [
        "Health. If you take any one of Minnesota's three most important players out for the playoffs, the Wolves lose 55% of their title odds, 45% once you correct for age. That sounds fragile and it is. But the loss is spread across three players rather than one: removing Ant, Rudy or Jaden costs 1.47 points of title odds on average, and no single one of them takes the season with him. When you tighten to a playoff rotation, though, the Wolves lose more net rating per missing star than San Antonio or Oklahoma City do. This is not a one-man team, whatever it used to be, and after the last three Aprils I'll take that sentence and frame it. It is a three-man team, and the playoffs are where that shows.",
    ],
    "part4.md": [
        "The title equity is spread across three players now. Losing any one of the top three for the playoffs costs 55% of the odds, which sounds terrible until you look at who: Ant, LaMelo, Rudy, on a roster that a year ago had one creator. Three ways to survive an injury instead of one.",
    ],
    "part4_short.md": [
        "Losing any one of the top three costs 55% of the odds, but it's three players now, not one.",
    ],
}


def git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short=8", "HEAD"], cwd=REPO).decode().strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def plain(text, name, r):
    n_viz = 0

    def sub(m):
        nonlocal n_viz
        n_viz += 1
        return "[visual: %s]" % m.group(1)

    text = VIZ.sub(sub, text)
    n_pending = 0
    for sent in PENDING.get(name, []):
        if sent in text:
            text = text.replace(sent, "[PENDING, fragility under review after D111: " + sent + "]")
            n_pending += 1
        else:
            r.note("  WARNING pending sentence not found verbatim in %s: %s..." % (name, sent[:60]))
    return text, n_viz, n_pending


def slide_to_md(js):
    d = json.loads(js)
    lines = ["**Slide copy**", ""]
    lines.append("- Dateline: %s" % d.get("dateline", ""))
    lines.append("- Headline: %s" % " ".join(d.get("headline", [])))
    for s in d.get("subhead", []):
        lines.append("- Subhead: %s" % s)
    for t in d.get("tiles", []):
        lines.append("- Tile: %s, %s. %s (sheet key `%s`)" % (t.get("num"), t.get("label"), " ".join(t.get("detail", [])), t.get("key")))
    for k in ("catch", "context"):
        if k in d:
            lines.append("- %s: %s" % (d[k].get("label", k), d[k].get("text", "")))
    for f in d.get("footer_right", []):
        lines.append("- Footer: %s" % f)
    return "\n".join(lines)


def main():
    with runlog.run("export_crossread", inputs={"series": os.path.relpath(SERIES, REPO)}) as r:
        os.makedirs(OUT, exist_ok=True)
        head = git_head()
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        written = []

        def header(src):
            return ("<!-- cross-read export of %s | run %s | commit %s | %s | visuals replaced by [visual: id]; "
                    "sentences under review bracketed [PENDING ...] -->\n\n" % (os.path.relpath(src, REPO), r.run_id, head, stamp))

        for i in (1, 2, 3, 4):
            # the part
            src = os.path.join(SERIES, "part%d.md" % i)
            text, nv, npend = plain(io.open(src, encoding="utf-8").read(), "part%d.md" % i, r)
            dst = os.path.join(OUT, "part%d.md" % i)
            io.open(dst, "w", encoding="utf-8").write(header(src) + text)
            written.append(dst)
            r.note("part%d.md: %d visuals replaced, %d sentences bracketed" % (i, nv, npend))
            # the feed: short, quotes, slide
            parts = []
            s = os.path.join(SERIES, "part%d_short.md" % i)
            t, _, np_ = plain(io.open(s, encoding="utf-8").read(), "part%d_short.md" % i, r)
            parts.append("## Short version\n\n" + t.strip())
            q = os.path.join(SERIES, "part%d_quotes.md" % i)
            if os.path.exists(q):
                parts.append("## Pull-quotes\n\n" + io.open(q, encoding="utf-8").read().strip())
            j = os.path.join(SERIES, "part%d_slide.json" % i)
            if os.path.exists(j):
                parts.append("## Slide\n\n" + slide_to_md(io.open(j, encoding="utf-8").read()))
            dst = os.path.join(OUT, "part%d_feed.md" % i)
            io.open(dst, "w", encoding="utf-8").write(header(s) + "# The Bet, Part %d: feed\n\n" % i + "\n\n".join(parts) + "\n")
            written.append(dst)
            r.note("part%d_feed.md: short (%d bracketed), quotes, slide" % (i, np_))

        for name, src in (("index.md", os.path.join(SERIES, "index.md")), ("methods.md", os.path.join(DOCS, "methods.md"))):
            text, nv, _ = plain(io.open(src, encoding="utf-8").read(), name, r)
            dst = os.path.join(OUT, name)
            io.open(dst, "w", encoding="utf-8").write(header(src) + text)
            written.append(dst)
            r.note("%s: %d visuals replaced" % (name, nv))

        manifest = os.path.join(OUT, "README.md")
        io.open(manifest, "w", encoding="utf-8").write(
            "# Cross-read package\n\nExported %s from commit %s (run %s). Plain markdown: visuals appear as `[visual: id]`; "
            "the fragility sentences are bracketed `[PENDING ...]` because their figures changed under D111 and the parts are not edited until that review is read.\n\n"
            % (stamp, head, r.run_id) + "\n".join("- %s" % os.path.basename(p) for p in written) + "\n")
        for p in written + [manifest]:
            r.output(p)
        print("exported %d files to %s" % (len(written), os.path.relpath(OUT, REPO)))


if __name__ == "__main__":
    main()
