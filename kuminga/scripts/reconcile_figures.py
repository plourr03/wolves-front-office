#!/usr/bin/env python3
"""C1: reconcile the near-identical figures that appear in more than one place.

Two collisions in the first morning report, both real and both worth a permanent
check rather than a one-off edit.

COLLISION 1: three different numbers in the 2.9 to 3.2 range, all describing
"Minnesota before the offseason".

  2.95%  the SIM's R6 baseline, CONSENSUS FORK ONLY
  2.94%  the same thing, averaged across the four forks
  3.15%  the SHAPLEY empty coalition, averaged across forks
  2.95%  the SHAPLEY "actual minus Kuminga" coalition, averaged across forks
         (a numerical coincidence with the consensus baseline, which is what made
         the report read as if two different objects were the same one)

The two ROSTERS are genuinely different and answer different questions:

  R6 baseline           run the exact 2025-26 end-of-season roster back, 18 players.
                        It ignores that Dosunmu, Hyland and Clark were free agents.
  Shapley v(none)       do literally nothing: let your own free agents walk and sign
                        nobody. 15 players plus a 14th-man charge.

R6 is what the brief specified and is what T1/T2 use, so it is CANONICAL for any
before/after claim. The Shapley zero is the natural origin for attribution and must
be labelled "let the free agents walk", never "did nothing".

COLLISION 2: the actual-roster band is 1.67-3.83 in one place and 1.71-3.77 in
another. The first is the direct simulation; the second is the f-curve interpolation
used to price coalitions cheaply. The rosters are identical (verified), so the gap is
purely interpolation plus Monte Carlo noise. The DIRECT SIM is canonical because it is
simulated at higher precision (5 seeds x 20,000 vs 3 x 10,000) and on a continuous net
rather than a 0.5-wide grid.

    python kuminga/scripts/reconcile_figures.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

OUTDIR = os.path.join(REPO, "kuminga", "outputs")
FORKS = ["consensus", "rapm", "box", "darko"]
OUT = os.path.join(OUTDIR, "canonical_figures.csv")
OUT_MD = os.path.join(OUTDIR, "canonical_figures.md")


def main():
    with runlog.run("reconcile_figures", inputs={"outdir": OUTDIR}) as r:
        sim = pd.read_csv(os.path.join(OUTDIR, "sim_all30_2026_27.csv"))
        named = pd.read_csv(os.path.join(OUTDIR, "named_scenarios.csv"), index_col=0)
        mn = sim[sim.team_abbr == "MIN"].set_index("fork")

        rows = []

        def add(label, obj, source, canonical, per_fork, note):
            vals = [per_fork[f] for f in FORKS]
            rows.append(dict(label=label, object=obj, source=source,
                             canonical=canonical,
                             **{f: per_fork[f] for f in FORKS},
                             mean=float(np.mean(vals)),
                             lo=float(np.min(vals)), hi=float(np.max(vals)),
                             note=note))

        add("Minnesota before the offseason",
            "R6 baseline: the 2025-26 end-of-season roster, 18 players, no injuries",
            "run_sim.py (direct simulation)", True,
            {f: mn.loc[f, "title_baseline"] * 100 for f in FORKS},
            "CANONICAL for any before/after claim. This is what T1 and T2 use.")

        add("Minnesota if the free agents had walked",
            "Shapley empty coalition: no moves AND no re-signings, 15 players + a "
            "14th-man charge",
            "shapley.py (f-curve interpolation)", False,
            {f: named.loc["did_nothing", f] for f in FORKS},
            "The natural origin for attribution. NOT the same roster as the R6 "
            "baseline and must not be called 'did nothing'.")

        add("Minnesota after the offseason",
            "the current roster, Green removed per R3",
            "run_sim.py (direct simulation)", True,
            {f: mn.loc[f, "title_current"] * 100 for f in FORKS},
            "CANONICAL. Band 1.67 to 3.83.")

        add("Minnesota after the offseason (f-curve)",
            "the same roster, priced by interpolation",
            "shapley.py (f-curve interpolation)", False,
            {f: named.loc["what_actually_happened", f] for f in FORKS},
            "Used only so 256 coalitions are affordable. Differs from the direct sim "
            "by interpolation error alone.")

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)

        # quantify the interpolation error explicitly
        direct = np.array([mn.loc[f, "title_current"] * 100 for f in FORKS])
        interp = np.array([named.loc["what_actually_happened", f] for f in FORKS])
        err = interp - direct
        r.note(f"f-curve interpolation error vs direct sim, per fork: "
               + ", ".join(f"{f}={e:+.3f}pp" for f, e in zip(FORKS, err)))
        r.note(f"  max |error| = {np.abs(err).max():.3f}pp")

        base_r6 = np.array([mn.loc[f, "title_baseline"] * 100 for f in FORKS])
        base_sh = np.array([named.loc["did_nothing", f] for f in FORKS])
        r.note(f"R6 baseline vs Shapley zero, per fork: "
               + ", ".join(f"{f}={d:+.3f}pp" for f, d in zip(FORKS, base_sh - base_r6)))
        r.note("  The gap is the three expiring contracts (Dosunmu, Hyland, Clark) "
               "plus a 14th-man charge, not noise.")

        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write("# Canonical figures\n\n")
            fh.write("Where two numbers in this project describe nearly the same thing, "
                     "this table says which one is canonical and why.\n\n")
            fh.write(df[["label", "object", "source", "canonical"] + FORKS +
                        ["mean", "lo", "hi"]].to_markdown(index=False, floatfmt=".2f"))
            fh.write("\n\n## Notes\n\n")
            for _, x in df.iterrows():
                fh.write(f"**{x.label}** ({'canonical' if x.canonical else 'secondary'}): "
                         f"{x.note}\n\n")
            fh.write(f"\nf-curve interpolation error against the direct simulation is at "
                     f"most {np.abs(err).max():.3f}pp across the four forks. That is the "
                     "price of pricing 256 coalitions by interpolation instead of "
                     "simulating each one, and it is small relative to the fork spread.\n")

        r.output(OUT, rows=len(df))
        r.output(OUT_MD)

    print()
    print(df[["label", "canonical"] + FORKS + ["mean", "lo", "hi"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
