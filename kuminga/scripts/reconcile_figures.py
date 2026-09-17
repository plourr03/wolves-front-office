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
purely interpolation plus Monte Carlo noise. D85: that stopped being true when Cody
Williams joined the simulated roster and not the Shapley one; the check is now a gate. The DIRECT SIM is canonical because it is
simulated at higher precision (5 seeds x 20,000 vs 3 x 10,000) and on a continuous net
rather than a 0.5-wide grid.

    python kuminga/scripts/reconcile_figures.py
"""
from __future__ import annotations

import os
import re
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
            "CANONICAL. Band %.2f to %.2f." % (
                min(mn.loc[f, "title_current"] * 100 for f in FORKS),
                max(mn.loc[f, "title_current"] * 100 for f in FORKS)))

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
        # D85: this gap was 1.24pp for weeks and was read as interpolation. It was the
        # attribution roster missing a player. Interpolation alone is under 0.1pp, so a
        # gap above the limit means the two rosters differ, and that is fatal.
        C1_LIMIT = 0.15
        if np.abs(err).max() > C1_LIMIT:
            raise RuntimeError("C1 failed: f-curve pricing of the actual roster is %.3fpp from the "
                               "direct simulation (limit %.2f). The Shapley grand coalition is not "
                               "the simulated roster." % (np.abs(err).max(), C1_LIMIT))

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

        # ---- C2: the skeleton gate ---------------------------------------------------
        # Every figure the piece quotes must be on the final numbers sheet with a run ID.
        # The skeleton and the morning report are rendered from templates by sheet key, so
        # the test is: (1) every key used exists and carries a run ID, (2) the MASKED
        # render (values replaced by a sentinel) contains no digit outside a short
        # allowlist, and (3) no retracted or superseded figure survives in the text.
        sheet = pd.read_csv(os.path.join(OUTDIR, "final_numbers.csv"), dtype=str).set_index("key")
        used = pd.read_csv(os.path.join(OUTDIR, "render_keys_used.csv")).key
        no_run = [k for k in used if not str(sheet.loc[k, "run_id"]).strip() or
                  str(sheet.loc[k, "run_id"]) in ("nan", "n/a")]
        allow = [r"^#+\s*\d+\.", r"\b\d{4}-\d{2}\b", r"\b[DFHMNRWSCGUVLPTAX]\d+[a-e]?\b",
                 r"`[^`]*`", r"\u27e6\u27e7", r"\b[Pp]iece 2\b", r"\bsections? \d\b"]
        retracted = ["6.53", "+2.90", "+6.83", "twice as good", "below 8 a night",
                     "Shannon fills", "0.3029", "0.3131", "+1.253", "+1.714", "1.68%",
                     "+0.488", "Not estimated this run", "not reached", "2.54%", "0.78 to 0.80",
                     # D85
                     "ships because of one player", "clears on his own", "a bundle of 7",
                     "fails it when the bundle is split", "ships on one player",
                     "The disagreement is all-views, so it is real"]
        report = []
        for doc in ("piece_v2_skeleton.md", "morning_report_v2.md"):
            masked = open(os.path.join(OUTDIR, doc.replace(".md", ".masked.md")),
                          encoding="utf-8").read()
            strays = []
            for i, line in enumerate(masked.splitlines(), 1):
                clean = line
                for pat in allow:
                    clean = re.sub(pat, " ", clean)
                for m in re.finditer(r"\d", clean):
                    strays.append("%s:%d: %s" % (doc, i, line.strip()[:120]))
                    break
            rendered = open(os.path.join(REPO, "kuminga", "docs", doc), encoding="utf-8").read()
            stale = [s for s in retracted if s in rendered]
            report.append(dict(document=doc, stray_digit_lines=len(strays),
                               stale_figures=len(stale), stale="; ".join(stale)))
            for s in strays:
                r.note("STRAY DIGIT %s" % s)
            for s in stale:
                r.note("STALE FIGURE in %s: %s" % (doc, s))
        skel = open(os.path.join(REPO, "kuminga", "docs", "piece_v2_skeleton.md"), encoding="utf-8").read()
        must = {"headline title odds": sheet.loc["title", "value"],
                "Williams threshold": sheet.loc["williams_threshold", "value"]}
        missing = [k for k, v in must.items() if v not in skel]
        rep = pd.DataFrame(report)
        rep.to_csv(os.path.join(OUTDIR, "reconcile_skeleton.csv"), index=False)
        r.note("C2: %d sheet keys used, %d without a run ID; stray digits %s; stale figures %s; "
               "required figures missing %s" % (len(used), len(no_run),
                                                dict(zip(rep.document, rep.stray_digit_lines)),
                                                dict(zip(rep.document, rep.stale_figures)), missing))
        if no_run or rep.stray_digit_lines.sum() or rep.stale_figures.sum() or missing:
            raise RuntimeError("C2 failed: the skeleton quotes a figure that is not on the sheet, "
                               "or carries a retracted one")
        r.output(os.path.join(OUTDIR, "reconcile_skeleton.csv"), rows=len(rep))

    print()
    print(df[["label", "canonical"] + FORKS + ["mean", "lo", "hi"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
