#!/usr/bin/env python3
"""Item 11, stage 1: P(outcome | MIN net rating), one curve per fork.

Exact Shapley over the 7-move set needs 2^7 = 128 coalitions per fork. Simulating each
coalition directly would be 128 x 4 forks x 5 seeds x 20,000 sims, roughly eight hours.
Instead, because only Minnesota's roster varies while the other 29 teams are held
fixed, P(title) is a smooth monotone function of MIN's net rating alone. So the curve
is built ONCE per fork over a grid of MIN net values, with common random numbers, and
every coalition is then priced by interpolation. This is the same f-curve device
core_max already uses for its scenario sweep.

The grid is deliberately wider than any coalition can reach, so no coalition is ever
priced by extrapolation.

    python kuminga/scripts/build_fcurve.py
"""
from __future__ import annotations

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
OUT = os.path.join(REPO, "kuminga", "outputs", "fcurve_min.csv")

GRID = np.arange(-4.0, 10.01, 0.5)
SEEDS = [1, 2, 3]
NSIMS = 10000
FORKS = ["consensus", "rapm", "box", "darko"]
OUTCOMES = ("title", "conf", "r2", "cf", "finals")


def main():
    with runlog.run("build_fcurve", inputs={"grid": [float(GRID[0]), float(GRID[-1]),
                                                     float(GRID[1] - GRID[0])],
                                            "seeds": SEEDS, "nsims": NSIMS}) as r:
        st = pd.read_csv(STR)
        rows = []
        for fork in FORKS:
            f = st[st.fork == fork]
            # The field is every team EXCEPT Minnesota, held at its current strength.
            field = {x.team_abbr: {"net": float(x.net_current), "net_sd": float(x.net_sd),
                                   "munc": float(x.munc), "conf": x.conf, "profile": None}
                     for _, x in f.iterrows()}
            r.note(f"fork {fork}: field of {len(field)} teams, sweeping MIN over "
                   f"{len(GRID)} grid points")
            for g in GRID:
                s = {k: dict(v) for k, v in field.items()}
                s["MIN"]["net"] = float(g)
                acc = {k: [] for k in OUTCOMES}
                for seed in SEEDS:
                    res = E.simulate_league(s, n_sims=NSIMS, seed=seed,
                                            use_overlay=False)["teams"]["MIN"]
                    for k in OUTCOMES:
                        acc[k].append(res[k])
                row = dict(fork=fork, min_net=float(g))
                for k in OUTCOMES:
                    row[k] = float(np.mean(acc[k]))
                    row[k + "_sd"] = float(np.std(acc[k]))
                rows.append(row)
            done = [x for x in rows if x["fork"] == fork]
            r.note(f"  {fork}: title ranges {done[0]['title']*100:.2f}% at net "
                   f"{GRID[0]:+.1f} to {done[-1]['title']*100:.2f}% at net {GRID[-1]:+.1f}")

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)
        r.note(f"wrote {len(df)} grid rows")
        r.output(OUT, rows=len(df))

    print(df[df.fork == "consensus"][["min_net", "title", "cf", "finals"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
