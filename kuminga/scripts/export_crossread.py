#!/usr/bin/env python3
"""Export the series as plain markdown for the cross-read.

The four parts, the four feeds (each part's short version, pull-quotes and slide copy in one
file), the index and the rendered methods page are written to `outputs/crossread/` with:

  - every `{{viz:<id>}}` tag replaced by a bracketed placeholder naming the visual
  - the N9 documents included with a PENDING banner (N9 is not in the series; D113)
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

PENDING = {}   # D113: the fragility passages were rewritten and are no longer pending

# N9 is not in any part; its documents travel with the package, marked pending (D113)
N9_DOCS = ["n9_breadth.md", "n9_proxies.md"]
N9_BANNER = ("> **PENDING. N9 is not in the series.** The breadth analysis and its proxies are here for the cross-read only; "
             "nothing from them enters the parts until Bobby decides (D112, D113).\n\n")


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
                    "N9 documents marked PENDING -->\n\n" % (os.path.relpath(src, REPO), r.run_id, head, stamp))

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

        for name in N9_DOCS:
            src = os.path.join(DOCS, name)
            if os.path.exists(src):
                dst = os.path.join(OUT, name)
                io.open(dst, "w", encoding="utf-8").write(header(src) + N9_BANNER + io.open(src, encoding="utf-8").read())
                written.append(dst)
                r.note("%s: included, marked PENDING" % name)
        for name, src in (("index.md", os.path.join(SERIES, "index.md")), ("methods.md", os.path.join(DOCS, "methods.md"))):
            text, nv, _ = plain(io.open(src, encoding="utf-8").read(), name, r)
            dst = os.path.join(OUT, name)
            io.open(dst, "w", encoding="utf-8").write(header(src) + text)
            written.append(dst)
            r.note("%s: %d visuals replaced" % (name, nv))

        manifest = os.path.join(OUT, "README.md")
        io.open(manifest, "w", encoding="utf-8").write(
            "# Cross-read package\n\nExported %s from commit %s (run %s). Plain markdown: visuals appear as `[visual: id]`; "
            "the fragility passages were rewritten under D113 and are no longer bracketed; the N9 documents (`n9_breadth.md`, `n9_proxies.md`) are included and marked PENDING, because N9 is not in the series.\n\n"
            % (stamp, head, r.run_id) + "\n".join("- %s" % os.path.basename(p) for p in written) + "\n")
        for p in written + [manifest]:
            r.output(p)
        print("exported %d files to %s" % (len(written), os.path.relpath(OUT, REPO)))


if __name__ == "__main__":
    main()
