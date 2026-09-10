#!/usr/bin/env python3
"""Merge per-fork f-curve parts into one fcurve_min.csv.

The four forks are independent sweeps over the same grid, so a high-precision run is
split across four concurrent processes and stitched here. Fails closed if a fork is
missing rather than writing a curve with a hole in it.
"""
from __future__ import annotations
import glob, os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
from kuminga.lib import runlog  # noqa: E402

OUT = os.path.join(REPO, "kuminga", "outputs", "fcurve_min.csv")
FORKS = ["consensus", "rapm", "box", "darko"]

def main():
    with runlog.run("merge_fcurve_parts", inputs={"forks": FORKS}) as r:
        parts = []
        for f in FORKS:
            p = OUT.replace(".csv", ".part_%s.csv" % f)
            assert os.path.exists(p), "missing part for fork %s: %s" % (f, p)
            d = pd.read_csv(p)
            assert len(d), "empty part for %s" % f
            r.note("  %-10s %d grid rows" % (f, len(d)))
            parts.append(d)
        df = pd.concat(parts, ignore_index=True)
        assert set(df.fork) == set(FORKS), "fork set mismatch after merge"
        df.to_csv(OUT, index=False)
        r.note("merged %d rows into %s" % (len(df), os.path.relpath(OUT, REPO)))
        r.output(OUT, rows=len(df))

if __name__ == "__main__":
    main()
