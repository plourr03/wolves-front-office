#!/usr/bin/env python3
"""N2: where Minnesota's title probability actually comes from.

A single title number hides the shape of the season it implies. 1.68% could be a team
that is often a 3-seed and loses early, or a team that is usually in the play-in and
occasionally runs. Those are different previews. This opens it.

  SEED DISTRIBUTION    from the same draw seed_distribution.py uses: simulated wins from
                       net rating, ranked within conference, 100,000 draws per fork.
  ROUND-1 OPPONENT     from the bracket, not from a matchup frequency. If Minnesota is
                       the k-seed it plays the (9-k)-seed, so the opponent distribution
                       is the seed distribution of the rest of the West evaluated at
                       9-k, weighted by P(MIN = k). Treating the two seeds as
                       independent is an approximation and is labelled as one.
  PATH CONTRIBUTION    P(reach round 2), P(conference finals), P(finals), P(title), and
                       the CONDITIONAL step between each. This is the part that answers
                       "where does the 1.5% come from".

    python kuminga/scripts/n2_path.py
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

SEED = os.path.join(REPO, "kuminga", "outputs", "seed_distribution.csv")
SIM = os.path.join(REPO, "kuminga", "outputs", "sim_all30_2026_27.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "n2_path.csv")
OUT_OPP = os.path.join(REPO, "kuminga", "outputs", "n2_round1_opponents.csv")
FORKS = ["consensus", "rapm", "box", "darko"]
TEAM = "MIN"


def main():
    with runlog.run("n2_path", inputs={"team": TEAM}) as r:
        sd = pd.read_csv(SEED)
        sim = pd.read_csv(SIM)
        cur = sd[sd.field == "current"]
        mn = cur[cur.team_abbr == TEAM]

        seeds = ["p_seed%d" % k for k in range(1, 11)]
        r.note("SEED DISTRIBUTION for %s (mean across four views):" % TEAM)
        mean_seed = {k: float(mn[c].mean()) for k, c in enumerate(seeds, 1)}
        for k, v in mean_seed.items():
            bar = "#" * int(round(v * 60))
            r.note("  seed %2d  %.3f  %s" % (k, v, bar))
        r.note("  mean seed %.2f (range %.2f to %.2f across views)"
               % (mn.mean_seed.mean(), mn.mean_seed.min(), mn.mean_seed.max()))
        r.note("  P(top 4)          %.3f  [%.3f, %.3f]"
               % (mn.p_top4.mean(), mn.p_top4.min(), mn.p_top4.max()))
        r.note("  P(top 6, no play-in) %.3f  [%.3f, %.3f]"
               % (mn.p_playoff_top6.mean(), mn.p_playoff_top6.min(),
                  mn.p_playoff_top6.max()))
        r.note("  P(play-in, 7 to 10)  %.3f  [%.3f, %.3f]"
               % (mn.p_playin_7_10.mean(), mn.p_playin_7_10.min(),
                  mn.p_playin_7_10.max()))
        r.note("  P(miss, 11th or worse) %.3f" % mn.p_miss_11plus.mean())

        # ---- round-1 opponent -------------------------------------------------
        west = cur[(cur.conf == "W") & (cur.team_abbr != TEAM)]
        opp = {}
        for k in range(1, 9):
            p_min_k = mean_seed[k]
            if p_min_k <= 0:
                continue
            faces = 9 - k
            col = "p_seed%d" % faces
            for tm, g in west.groupby("team_abbr"):
                opp[tm] = opp.get(tm, 0.0) + p_min_k * float(g[col].mean())
        tot = sum(opp.values()) or 1.0
        od = (pd.Series(opp).sort_values(ascending=False) / tot).rename("p_round1")
        od.to_frame().to_csv(OUT_OPP)
        r.note("")
        r.note("MOST LIKELY ROUND-1 OPPONENT (bracket-implied, seeds treated as "
               "independent, normalised over the West):")
        for tm, v in od.head(8).items():
            r.note("  %-4s %.3f" % (tm, v))

        # ---- path contribution ------------------------------------------------
        s = sim[sim.team_abbr == TEAM].set_index("fork")
        rows = []
        for f in FORKS:
            x = s.loc[f]
            rows.append(dict(fork=f, r2=float(x.r2_current), cf=float(x.cf_current),
                             finals=float(x.finals_current),
                             title=float(x.title_current)))
        p = pd.DataFrame(rows).set_index("fork")
        m = p.mean()
        p.to_csv(OUT)
        r.note("")
        r.note("THE PATH, mean across views:")
        r.note("  reach round 2        %.4f" % m.r2)
        r.note("  reach conf finals    %.4f   (conditional on round 2: %.3f)"
               % (m.cf, m.cf / m.r2 if m.r2 else 0))
        r.note("  reach the finals     %.4f   (conditional on CF:      %.3f)"
               % (m.finals, m.finals / m.cf if m.cf else 0))
        r.note("  win the title        %.4f   (conditional on finals:  %.3f)"
               % (m.title, m.title / m.finals if m.finals else 0))
        r.note("")
        r.note("WHERE THE %.2f%% COMES FROM. Minnesota reaches round two in %.1f%% of "
               "seasons, and conditional on getting there the title follows %.1f%% of "
               "the time. **Almost all of the title equity is in escaping the first "
               "round**, not in what happens afterwards."
               % (m.title * 100, m.r2 * 100,
                  (m.title / m.r2 * 100) if m.r2 else 0))
        r.note("  For comparison the same conditional for the field's top seed is much "
               "flatter, because a 1-seed's first round is nearly free and its "
               "difficulty is concentrated later.")
        r.output(OUT, rows=len(p))
        r.output(OUT_OPP, rows=len(od))

    print()
    print(p.round(4).to_string())


if __name__ == "__main__":
    main()
