#!/usr/bin/env python3
"""C4: why Minnesota's baseline moved from the 1.7% on record in June to ~2.95% now.

The June figure (offseason/outputs/e_baseline.md, 2026-06-13) put Minnesota's 2026-27
title probability at 1.7% central, band 1.4 to 2.0. This pipeline's R6 baseline puts it
at 2.95% (consensus fork). That is a large move for something both runs call "the
baseline", so it is decomposed rather than asserted.

Three things changed, and they are separated by walking the path one step at a time
with common random numbers so each step's effect is isolated from Monte Carlo noise:

  1. THE INJURY ASSUMPTION. June modelled Minnesota with DiVincenzo OUT, giving MIN a
     net of +1.36 (expectation +2.16 plus a -0.80 move delta). R6 specifies a HEALTHY
     baseline, so MIN sits at +2.16. This is a definitional difference between the two
     baselines, not a disagreement about the team.
  2. THE MATCHUP OVERLAY. June resolved series with the archetype overlay ON, using
     hand-authored dimension profiles that exist for 12 of 30 teams. R2 forbids a
     pipeline that treats teams differently, so the overlay is OFF here.
  3. EVERYTHING ELSE: the all-30 mechanical field rebuild, the refit rotations, and
     any harness differences. Reported as a residual rather than claimed.

    python kuminga/scripts/baseline_decomp.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import runlog  # noqa: E402
import bracket_sim as E         # noqa: E402

STR = os.path.join(REPO, "kuminga", "outputs", "team_strengths_2026_27.csv")
PROFILES = os.path.join(REPO, "offseason", "data", "opponent_profiles.json")
OUT = os.path.join(REPO, "kuminga", "outputs", "baseline_decomposition.csv")

SEEDS = [1, 2, 3]
NSIMS = 10_000
JUNE_REPORTED = 1.7          # e_baseline.md, 2026-06-13, central of a 1.4-2.0 band
JUNE_MIN_NET = 1.36          # act25 +2.88 -> exp +2.16, move delta -0.80 (DDV out)
FORK = "consensus"


def run(strengths, overlay):
    acc = []
    for seed in SEEDS:
        acc.append(E.simulate_league(strengths, n_sims=NSIMS, seed=seed,
                                     use_overlay=overlay)["teams"]["MIN"]["title"])
    return float(np.mean(acc)) * 100


def main():
    with runlog.run("baseline_decomp", inputs={"seeds": SEEDS, "nsims": NSIMS,
                                               "fork": FORK}) as r:
        st = pd.read_csv(STR)
        f = st[st.fork == FORK]
        base = {x.team_abbr: {"net": float(x.net_baseline), "net_sd": float(x.net_sd),
                              "munc": float(x.munc), "conf": x.conf, "profile": None}
                for _, x in f.iterrows()}
        min_net_r6 = base["MIN"]["net"]
        r.note(f"R6 baseline MIN net: {min_net_r6:+.2f} | June's MIN net: {JUNE_MIN_NET:+.2f}")

        prof = {p["team"]: p["dimensions"] for p in
                json.load(open(PROFILES, encoding="utf-8"))}
        r.note(f"overlay profiles available for {len(prof)} of 30 teams: "
               f"{sorted(prof)}")

        # Step 0: the pipeline as it ships.
        s0 = {k: dict(v) for k, v in base.items()}
        p0 = run(s0, overlay=False)

        # Step 1: same, but Minnesota at June's net (DiVincenzo out).
        s1 = {k: dict(v) for k, v in base.items()}
        s1["MIN"]["net"] = JUNE_MIN_NET
        p1 = run(s1, overlay=False)

        # Step 2: same again, but with the archetype overlay switched on.
        s2 = {k: dict(v) for k, v in s1.items()}
        for t in s2:
            s2[t]["profile"] = prof.get(t)
        p2 = run(s2, overlay=True)

        rows = [
            dict(step="0. this pipeline, R6 healthy baseline, overlay off",
                 min_net=min_net_r6, overlay=False, title_pct=p0, delta_from_previous=np.nan),
            dict(step="1. Minnesota moved to June's net (DiVincenzo out)",
                 min_net=JUNE_MIN_NET, overlay=False, title_pct=p1,
                 delta_from_previous=p1 - p0),
            dict(step="2. archetype matchup overlay switched ON",
                 min_net=JUNE_MIN_NET, overlay=True, title_pct=p2,
                 delta_from_previous=p2 - p1),
            dict(step="3. June's reported figure (e_baseline.md, 2026-06-13)",
                 min_net=JUNE_MIN_NET, overlay=True, title_pct=JUNE_REPORTED,
                 delta_from_previous=JUNE_REPORTED - p2),
        ]
        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)

        for _, x in df.iterrows():
            d = "" if pd.isna(x.delta_from_previous) else f"  ({x.delta_from_previous:+.2f}pp)"
            r.note(f"  {x.step:58s} {x.title_pct:5.2f}%{d}")

        parts = {
            "injury assumption (healthy vs DiVincenzo out)": p0 - p1,
            "matchup overlay (off vs on)": p1 - p2,
            "residual: all-30 field rebuild, rotations, harness": p2 - JUNE_REPORTED,
        }
        total = p0 - JUNE_REPORTED
        r.note(f"TOTAL SHIFT: {JUNE_REPORTED:.2f}% -> {p0:.2f}% = {total:+.2f}pp")
        for k, v in sorted(parts.items(), key=lambda kv: -abs(kv[1])):
            r.note(f"  {k:52s} {v:+.2f}pp  ({100*v/total:4.0f}% of the move)")
        biggest = max(parts, key=lambda k: abs(parts[k]))
        r.note(f"LARGEST COMPONENT: {biggest}")
        r.output(OUT, rows=len(df))

    print()
    print(df.round(3).to_string(index=False))
    print()
    for k, v in parts.items():
        print(f"  {k:52s} {v:+.2f}pp")


if __name__ == "__main__":
    main()
