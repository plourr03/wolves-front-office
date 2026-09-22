#!/usr/bin/env python3
"""The prose gate (C5). Scan a FINISHED draft, written prose-first with no template keys, for
figures that are not on the final-numbers sheet.

Every number in the draft is read as a token (with its sign, dollar sign, commas, decimals
and percent), reduced to its digits and compared with the digits of every number on the
sheet (`outputs/final_numbers.csv`, every value split into the numbers it contains). A
token matches only if the sheet carries exactly the same digits, so "1.7%" does not pass on
the strength of a sheet value of 1.68%; the writer quotes the sheet's precision or adds a
rounded key. Tokens that are structure rather than findings are allowed and listed:
seasons (2026-27), four-digit years, dates, list markers and headings, item codes, code
spans, and a short list of league constants named in ALLOWED_CONSTANTS. The retracted
phrase list from `reconcile_figures.py` is applied to the prose too.

Output: a report of every unmatched token with its line, written to
`outputs/gate_prose_<draft>.csv` and printed; the gate fails (non-zero exit) if any token is
unmatched or any retracted phrase survives.

    python kuminga/scripts/gate_prose.py DRAFT.md [DRAFT2.md ...]
"""
from __future__ import annotations

import argparse
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

from kuminga.lib import runlog  # noqa: E402
from reconcile_figures import RETRACTED  # noqa: E402

OUT = os.path.join(REPO, "kuminga", "outputs")
SHEET = os.path.join(OUT, "final_numbers.csv")
# league constants that are structure, not findings: games in a season, minutes in a game,
# teams in the league, the per-100-possessions scale, playoff series length
ALLOWED_CONSTANTS = {"82", "48", "30", "100", "7"}
STRUCTURE = [r"\b\d{4}-\d{2}\b",                       # seasons
             r"\b(19|20)\d{2}-\d{2}-\d{2}\b",            # ISO dates
             r"\b(19|20)\d{2}\b",                        # years
             r"^\s*#+.*$",                               # headings
             r"^\s*\d+\.\s",                             # list markers
             r"\b[DFHMNRWSCGUVLPTAX]\d+[a-e]?\b",         # item codes
             r"`[^`]*`",                                 # code spans
             r"\[\d+\]\([^)]*\)", r"\(https?://[^)]*\)", r"https?://\S+"]   # links
TOKEN = re.compile(r"[-+]?\$?\d[\d,]*(?:\.\d+)?%?")


def digits(tok):
    return re.sub(r"[^\d.]", "", tok).strip(".")


def sheet_numbers(sheet):
    nums = set()
    for v in sheet.value.astype(str):
        for m in TOKEN.finditer(v):
            d = digits(m.group(0))
            if d:
                nums.add(d)
    return nums


def scan(path, nums):
    rows = []
    text = open(path, encoding="utf-8").read()
    for i, line in enumerate(text.splitlines(), 1):
        clean = line
        for pat in STRUCTURE:
            clean = re.sub(pat, " ", clean, flags=re.M)
        for m in TOKEN.finditer(clean):
            tok = m.group(0)
            d = digits(tok)
            if not d:
                continue
            if d in ALLOWED_CONSTANTS and "%" not in tok and "$" not in tok:
                continue
            if d in nums:
                continue
            ctx = line.strip()
            j = max(0, ctx.find(tok) - 50)
            rows.append(dict(document=os.path.basename(path), line=i, token=tok, context=ctx[j:j + 130]))
    stale = [s for s in RETRACTED if s in text]
    return rows, stale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts", nargs="+")
    args = ap.parse_args()
    with runlog.run("gate_prose", inputs={"drafts": args.drafts, "sheet": SHEET}) as r:
        sheet = pd.read_csv(SHEET, dtype=str)
        nums = sheet_numbers(sheet)
        r.note("sheet: %d figures, %d distinct numbers" % (len(sheet), len(nums)))
        failed = False
        for path in args.drafts:
            rows, stale = scan(path, nums)
            rep = pd.DataFrame(rows, columns=["document", "line", "token", "context"])
            out = os.path.join(OUT, "gate_prose_%s.csv" % os.path.splitext(os.path.basename(path))[0])
            rep.to_csv(out, index=False)
            r.note("%s: %d numbers not on the sheet, %d retracted phrases" % (os.path.basename(path), len(rep), len(stale)))
            for _, x in rep.iterrows():
                r.note("  NOT ON SHEET line %d: %s   | %s" % (x.line, x.token, x.context))
            for s in stale:
                r.note("  RETRACTED: %s" % s)
            r.output(out, rows=len(rep))
            if len(rep) or stale:
                failed = True
        if failed:
            raise RuntimeError("prose gate failed: a figure is not on the sheet or a retracted phrase survives")
        r.note("prose gate clean")


if __name__ == "__main__":
    main()
