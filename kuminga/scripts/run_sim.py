#!/usr/bin/env python3
"""Item 10: the all-30 before/after simulation, every fork, CRN-paired.

Runs the championship engine twice per fork: once on the R6 baseline field (the
2025-26 end-of-season rosters, no injuries) and once on the current field, using
IDENTICAL random draws so the difference isolates the offseason from Monte Carlo
noise. Persists ALL THIRTY teams, which is the change from every previous run in this
repo: the harness computed the full league and then kept only Minnesota.

Per R1 nothing here is a headline. The point estimates feed the attribution, the
ordinal ranking and the band; the band is what ships.

    python kuminga/scripts/run_sim.py [--nsims 20000]
"""
from __future__ import annotations

import argparse
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
OUT = os.path.join(REPO, "kuminga", "outputs", "sim_all30_2026_27.csv")
OUT_MATCH = os.path.join(REPO, "kuminga", "outputs", "sim_matchups_2026_27.csv")

SEEDS = [1, 2, 3, 4, 5]
FORKS = ["consensus", "rapm", "box", "darko"]

# The overlay applies a matchup-dimension adjustment using hand-authored opponent
# profiles that exist for only 12 teams. R2 retires those, and running an overlay for
# 12 of 30 teams would make the pipeline non-identical across teams, which is the one
# thing the ruling forbids. So the overlay is OFF and every series is resolved on net
# rating alone, uniformly.
USE_OVERLAY = False


def strengths_from(df: pd.DataFrame, col: str) -> dict:
    return {
        r.team_abbr: {"net": float(r[col]), "net_sd": float(r.net_sd),
                      "munc": float(r.munc), "conf": r.conf, "profile": None}
        for _, r in df.iterrows()
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsims", type=int, default=20000)
    args = ap.parse_args()

    with runlog.run("run_sim", inputs={"strengths": STR, "nsims": args.nsims,
                                       "seeds": SEEDS, "overlay": USE_OVERLAY}) as r:
        st = pd.read_csv(STR)
        p = E.load_e_params()
        wa, wb = float(p["wins_a"]), float(p["wins_b"])
        r.note(f"expected wins = {wa} + {wb} * net")

        rows, mrows = [], []
        for fork in FORKS:
            f = st[st.fork == fork]
            s_base = strengths_from(f, "net_baseline")
            s_cur = strengths_from(f, "net_current")

            acc = {t: {k: [] for k in ("title", "conf", "r2", "cf", "finals")}
                   for t in s_base}
            acc_b = {t: {k: [] for k in ("title", "conf", "r2", "cf", "finals")}
                     for t in s_base}

            for seed in SEEDS:
                # CRN: the SAME seed drives both fields, so the paired difference
                # cancels the draw and leaves only the roster change.
                rb = E.simulate_league(s_base, n_sims=args.nsims, seed=seed,
                                       use_overlay=USE_OVERLAY)["teams"]
                _full = E.simulate_league(s_cur, n_sims=args.nsims, seed=seed,
                                          use_overlay=USE_OVERLAY)
                rc = _full["teams"]
                # N2: the simulator computes a matchup block (who meets whom, and who
                # wins given they meet) and it was being thrown away, so the expected
                # first- and second-round opponent distribution could not be read off
                # any existing run. Kept here, one row per pair per fork per seed.
                for k, v in _full.get("matchups", {}).items():
                    mrows.append(dict(fork=fork, seed=seed, pair=k, a=v["a"], b=v["b"],
                                      meet=v["meet"],
                                      a_wins_given_meet=v["a_wins_given_meet"]))
                for t in s_base:
                    for k in ("title", "conf", "r2", "cf", "finals"):
                        acc_b[t][k].append(rb[t][k])
                        acc[t][k].append(rc[t][k])
            r.note(f"fork {fork}: {len(SEEDS)} seeds x {args.nsims:,} sims x 2 fields done")

            for t in s_base:
                base_net, cur_net = s_base[t]["net"], s_cur[t]["net"]
                row = dict(fork=fork, team_abbr=t, conf=s_base[t]["conf"],
                           net_baseline=base_net, net_current=cur_net,
                           net_delta=cur_net - base_net,
                           wins_baseline=wa + wb * base_net,
                           wins_current=wa + wb * cur_net,
                           wins_delta=wb * (cur_net - base_net))
                for k in ("title", "conf", "r2", "cf", "finals"):
                    b = float(np.mean(acc_b[t][k]))
                    c = float(np.mean(acc[t][k]))
                    row[f"{k}_baseline"] = b
                    row[f"{k}_current"] = c
                    row[f"{k}_delta"] = c - b
                    row[f"{k}_mc_sd"] = float(np.std(acc[t][k]))
                rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(OUT, index=False)
        if mrows:
            md = pd.DataFrame(mrows)
            md = (md.groupby(["fork", "pair", "a", "b"])
                  [["meet", "a_wins_given_meet"]].mean().reset_index())
            md.to_csv(OUT_MATCH, index=False)
            r.note("N2: wrote %d matchup rows to %s"
                   % (len(md), os.path.relpath(OUT_MATCH, REPO)))
        r.note(f"wrote {len(df)} rows: {df.fork.nunique()} forks x {df.team_abbr.nunique()} teams")

        mn = df[df.team_abbr == "MIN"]
        for _, x in mn.iterrows():
            r.note(f"  MIN [{x.fork}]: title {x.title_baseline*100:.2f}% -> "
                   f"{x.title_current*100:.2f}% ({x.title_delta*100:+.2f}pp), "
                   f"net {x.net_baseline:+.2f} -> {x.net_current:+.2f}, "
                   f"wins {x.wins_baseline:.1f} -> {x.wins_current:.1f}")
        r.output(OUT, rows=len(df))

    print()
    print("MINNESOTA, all four forks:")
    print(mn[["fork", "net_baseline", "net_current", "net_delta", "wins_current",
              "title_baseline", "title_current", "title_delta"]].round(4).to_string(index=False))
    print()
    piv = df.pivot_table(index="team_abbr", columns="fork", values="title_delta")
    piv = (piv * 100).round(2)
    piv["mean"] = piv.mean(axis=1).round(2)
    print("Title-odds change from the offseason (pp), by fork:")
    print(piv.sort_values("mean", ascending=False).to_string())


if __name__ == "__main__":
    main()
