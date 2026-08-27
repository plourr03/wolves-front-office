#!/usr/bin/env python3
"""C2 side-by-side: every sign-agreement verdict, with and without the minutes ceiling.

The decision rule Bobby set: if any Wolves verdict changes, the ceiling version becomes
primary and the un-ceilinged one is reported as a sensitivity. If none change, the
ceiling version is STILL primary, because it is the more defensible rule, and the
result is reported as robust.

Diagnostic to watch, also his: "Dosunmu retained" scoring ALL NEGATIVE on pure on-court
terms is a smell. A rotation guard on a real contract should not be unambiguously bad
for a team in every view; if he still is under the ceiling, that is a signal about the
minutes model rather than about Dosunmu.

    python kuminga/scripts/compare_ceiling.py
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
OUT_MOVES = os.path.join(OUTDIR, "C2_moves_ceiling_vs_not.csv")
OUT_TEAMS = os.path.join(OUTDIR, "C2_teams_ceiling_vs_not.csv")


def verdict(row, cols):
    v = row[cols].to_numpy(dtype=float)
    if (v > 0).all():
        return "ALL POSITIVE"
    if (v < 0).all():
        return "ALL NEGATIVE"
    return "MIXED"


def main():
    with runlog.run("compare_ceiling", inputs={"outdir": OUTDIR}) as r:
        # ---- the Wolves' eight moves -----------------------------------------
        new = pd.read_csv(os.path.join(OUTDIR, "shapley_min.csv"), index_col=0)
        old = pd.read_csv(os.path.join(OUTDIR, "shapley_min_NOCEILING.csv"), index_col=0)
        rows = []
        for mv in sorted(set(new.index) | set(old.index)):
            o = old.loc[mv] if mv in old.index else None
            n = new.loc[mv] if mv in new.index else None
            rows.append(dict(
                move=mv,
                verdict_noceiling=o.sign_agreement if o is not None else "n/a",
                verdict_ceiling=n.sign_agreement if n is not None else "n/a",
                changed=(o is not None and n is not None
                         and o.sign_agreement != n.sign_agreement),
                mean_noceiling=float(o.mean_pp) if o is not None else np.nan,
                mean_ceiling=float(n.mean_pp) if n is not None else np.nan,
                **{f"{f}_noceiling": float(o[f]) if o is not None else np.nan for f in FORKS},
                **{f"{f}_ceiling": float(n[f]) if n is not None else np.nan for f in FORKS},
            ))
        mv = pd.DataFrame(rows).sort_values("mean_ceiling", ascending=False)
        mv.to_csv(OUT_MOVES, index=False)

        n_changed = int(mv.changed.sum())
        r.note(f"WOLVES MOVES: {n_changed} of {len(mv)} sign-agreement verdicts changed")
        for _, x in mv.iterrows():
            flag = "  <-- CHANGED" if x.changed else ""
            r.note(f"  {x.move:18s} {x.verdict_noceiling:13s} -> {x.verdict_ceiling:13s} "
                   f"| mean {x.mean_noceiling:+.3f} -> {x.mean_ceiling:+.3f}{flag}")

        dos = mv[mv.move == "dosunmu_retained"]
        if len(dos):
            d = dos.iloc[0]
            r.note(f"DIAGNOSTIC (dosunmu_retained): {d.verdict_noceiling} -> "
                   f"{d.verdict_ceiling}, mean {d.mean_noceiling:+.3f} -> "
                   f"{d.mean_ceiling:+.3f}")

        # ---- all 30 teams' offseason signs ------------------------------------
        tn = pd.read_csv(os.path.join(OUTDIR, "sim_all30_2026_27.csv"))
        to = pd.read_csv(os.path.join(OUTDIR, "sim_all30_2026_27_NOCEILING.csv"))
        def team_verdicts(sim):
            p = sim.pivot_table(index="team_abbr", columns="fork", values="title_delta")
            p = p[FORKS] * 100
            return p.apply(lambda row: verdict(row, FORKS), axis=1), p.mean(axis=1)
        vo, mo = team_verdicts(to)
        vn, mn_ = team_verdicts(tn)
        t = pd.DataFrame({"verdict_noceiling": vo, "verdict_ceiling": vn,
                          "mean_pp_noceiling": mo, "mean_pp_ceiling": mn_})
        t["changed"] = t.verdict_noceiling != t.verdict_ceiling
        t = t.sort_values("mean_pp_ceiling", ascending=False)
        t.to_csv(OUT_TEAMS)

        nt = int(t.changed.sum())
        r.note(f"ALL 30 TEAMS: {nt} of {len(t)} offseason sign verdicts changed")
        for tm, x in t[t.changed].iterrows():
            r.note(f"  {tm}: {x.verdict_noceiling} -> {x.verdict_ceiling} "
                   f"(mean {x.mean_pp_noceiling:+.2f} -> {x.mean_pp_ceiling:+.2f}pp)")
        r.note("verdict counts, no-ceiling:  " +
               str(t.verdict_noceiling.value_counts().to_dict()))
        r.note("verdict counts, with ceiling:" +
               str(t.verdict_ceiling.value_counts().to_dict()))

        if n_changed:
            r.note("RULING: a Wolves verdict changed, so the CEILING version is primary "
                   "and the un-ceilinged run is reported as a sensitivity.")
        else:
            r.note("RULING: no Wolves verdict changed. The ceiling version is still "
                   "primary because it is the more defensible rule, and the result is "
                   "reported as ROBUST to the minutes model.")
        r.output(OUT_MOVES, rows=len(mv))
        r.output(OUT_TEAMS, rows=len(t))

    print()
    print(mv[["move", "verdict_noceiling", "verdict_ceiling", "changed",
              "mean_noceiling", "mean_ceiling"]].round(3).to_string(index=False))
    print()
    print(t.round(2).to_string())


if __name__ == "__main__":
    main()
