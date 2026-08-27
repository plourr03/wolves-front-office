#!/usr/bin/env python3
"""Item 10, the seed distribution the main sim does not return.

`simulate_league` computes conference seeds internally but returns only title /
conference / round-advance probabilities. Rather than edit a shared engine file that
four other subsystems import, this reproduces the engine's OWN seeding step exactly
and nothing else:

    sim_wins = wins_a + wins_b * net + Normal(0, sigma_record)
    seed     = rank within conference by sim_wins, descending

Those are the same parameters, from the same calibration file, that the bracket uses.
So this is the engine's seeding distribution, isolated, not a second model of it.

    python kuminga/scripts/seed_distribution.py
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
OUT = os.path.join(REPO, "kuminga", "outputs", "seed_distribution.csv")
NSIMS = 100_000
SEED = 20260827
FORKS = ["consensus", "rapm", "box", "darko"]


def main():
    with runlog.run("seed_distribution", inputs={"nsims": NSIMS, "seed": SEED}) as r:
        st = pd.read_csv(STR)
        p = E.load_e_params()
        wa, wb, sig = float(p["wins_a"]), float(p["wins_b"]), float(p["sigma_record"])
        r.note(f"seeding model: wins = {wa} + {wb}*net + N(0, {sig}); "
               f"{NSIMS:,} draws per fork per field")

        rng = np.random.default_rng(SEED)
        rows = []
        for fork in FORKS:
            f = st[st.fork == fork]
            for field, col in (("baseline", "net_baseline"), ("current", "net_current")):
                for conf in ("E", "W"):
                    c = f[f.conf == conf]
                    nets = c[col].to_numpy(dtype=float)
                    teams = c.team_abbr.tolist()
                    wins = wa + wb * nets[None, :] + rng.normal(0, sig, (NSIMS, len(teams)))
                    # rank 1 = most wins
                    order = np.argsort(-wins, axis=1)
                    seeds = np.empty_like(order)
                    np.put_along_axis(seeds, order,
                                      np.arange(1, len(teams) + 1)[None, :].repeat(NSIMS, 0), axis=1)
                    for j, t in enumerate(teams):
                        s = seeds[:, j]
                        row = dict(fork=fork, field=field, conf=conf, team_abbr=t,
                                   mean_seed=float(s.mean()),
                                   p_top4=float((s <= 4).mean()),
                                   p_playoff_top6=float((s <= 6).mean()),
                                   p_playin_7_10=float(((s >= 7) & (s <= 10)).mean()),
                                   p_miss_11plus=float((s >= 11).mean()))
                        for k in range(1, 11):
                            row[f"p_seed{k}"] = float((s == k).mean())
                        rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)
        r.note(f"wrote {len(df)} rows")
        mn = df[(df.team_abbr == "MIN")]
        for _, x in mn.iterrows():
            r.note(f"  MIN [{x.fork:9s}/{x.field:8s}] mean seed {x.mean_seed:.2f} | "
                   f"top-4 {x.p_top4:.3f} | top-6 {x.p_playoff_top6:.3f} | "
                   f"play-in {x.p_playin_7_10:.3f} | miss {x.p_miss_11plus:.3f}")
        r.output(OUT, rows=len(df))

    print()
    m = df[df.team_abbr == "MIN"].pivot_table(
        index="field", columns="fork",
        values=["mean_seed", "p_top4", "p_playoff_top6", "p_playin_7_10"])
    print(m.round(3).to_string())


if __name__ == "__main__":
    main()
