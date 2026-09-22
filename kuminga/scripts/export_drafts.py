#!/usr/bin/env python3
"""Export the rendered drafts and the methods document as plain markdown for the editor:
the same text with the provenance line (the italic "rendered from" line under the title)
removed. Nothing else changes, so the prose gate can be run on the exports and pass.

    python kuminga/scripts/export_drafts.py
"""
from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.abspath(os.path.join(HERE, "..", "docs"))
EXPORT = os.path.join(DOCS, "export")
FILES = [("piece_v2_draft_full.md", "draft_full.md"), ("piece_v2_draft_short.md", "draft_short.md"),
         ("methods.md", "methods.md")]


def main():
    os.makedirs(EXPORT, exist_ok=True)
    for src, dst in FILES:
        text = open(os.path.join(DOCS, src), encoding="utf-8").read()
        text = re.sub(r"^\*(Draft, rendered from|Rendered from) [^\n]*\*\n", "", text, count=1, flags=re.M)
        with open(os.path.join(EXPORT, dst), "w", encoding="utf-8") as fh:
            fh.write(text)
        print("exported %s -> export/%s (%d words)" % (src, dst, len(text.split())))


if __name__ == "__main__":
    main()
