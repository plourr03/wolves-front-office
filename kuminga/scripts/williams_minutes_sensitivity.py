#!/usr/bin/env python3
"""How much of Minnesota's projected decline is one assumption about Cody Williams?

WHY THIS EXISTS. The Green trade put Cody Williams on Minnesota, and the rotation model
hands him roughly 19 minutes a night because it allocates from PRIOR MINUTES PER
APPEARANCE, and he played 24.3 a night for a rebuilding Utah team. His impact is -3.86,
the worst on the roster by a distance. Those two facts together move Minnesota's
minutes-weighted impact by about 0.4 points and are the single largest driver of the
modelled title probability falling from 3.58% to roughly 1.4%.

THE PROBLEM WITH THAT. Minutes per appearance is a ROLE signal, and a role earned on a
27-win team does not transfer to a team trying to win a title. Minnesota has Terrence
Shannon Jr., Jaylen Clark and Nah'Shon Hyland competing for the same minutes. Nothing in
the sourced record says Williams starts or plays 19 minutes for this team. The number is
an inherited default, not a projection anyone made.

SO THE HONEST THING IS TO MEASURE IT rather than argue about it. This holds everything
else fixed, walks Williams' minutes down, hands them to the rest of the rotation in rank
order up to each player's own ceiling, and re-prices Minnesota off the same f-curve the
rest of the project uses. It reports two things:

  1. Minnesota's title probability at each Williams minutes level.
  2. Kuminga's marginal contribution at each level, which is the number the piece
     actually claims. If that claim is stable across the range, the Williams assumption
     is a caveat. If it moves the sign, the claim is conditional on it and has to say so.

    python kuminga/scripts/williams_minutes_sensitivity.py
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
sys.path.insert(0, HERE)

from kuminga.lib import kfreeze, rotation, runlog     # noqa: E402
import build_team_ratings as A                        # noqa: E402
import bracket_sim as E                               # noqa: E402
from build_strengths import build_impacts, add_rookie_impacts  # noqa: E402

POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
ROT = os.path.join(REPO, "kuminga", "outputs", "rotations_2026_27.csv")
FCURVE = os.path.join(REPO, "kuminga", "outputs", "fcurve_min.csv")
STR = os.path.join(REPO, "kuminga", "outputs", "team_strengths_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "williams_minutes_sensitivity.csv")

FORKS = ["consensus", "rapm", "box", "darko"]
KUMINGA_ID = "1630228"
WILLIAMS_ID = "1642262"
LEVELS = [None, 16.0, 12.0, 8.0, 4.0, 0.0]   # None = leave the model's own allocation


def main():
    with runlog.run("williams_minutes_sensitivity",
                    inputs={"levels": [str(x) for x in LEVELS]}) as r:
        pool = pd.read_csv(POOL)
        rot = pd.read_csv(ROT)
        fc = pd.read_csv(FCURVE)
        st = pd.read_csv(STR)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, pool)

        mn = pool[(pool.scenario == "current") & (pool.team_abbr == "MIN")].copy()
        mr = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN")]
        rot_min = {str(int(x.player_id)): float(x.mpg) for _, x in mr.iterrows()}
        name = {str(int(x.player_id)): x.player_name for _, x in mn.iterrows()
                if pd.notna(x.player_id)}
        ceil = {str(int(x.player_id)): float(rotation.ceiling_for(x.prior_mpg))
                for _, x in mn.iterrows() if pd.notna(x.player_id)}
        rank = {str(int(x.player_id)): float(x.rank_score) for _, x in mn.iterrows()
                if pd.notna(x.player_id)}
        beta = float(E.load_e_params()["beta"])

        assert WILLIAMS_ID in rot_min, "Cody Williams is not in the rotation"
        actual = rot_min[WILLIAMS_ID]
        r.note("Cody Williams is allocated %.2f mpg on a prior of %.2f and an impact of "
               "%.2f (consensus), the worst on the roster."
               % (actual,
                  float(mn[mn.player_id == float(WILLIAMS_ID)].prior_mpg.iloc[0]),
                  float(mn[mn.player_id == float(WILLIAMS_ID)].consensus_net.iloc[0])))

        def price(minutes):
            out = {}
            for fork in FORKS:
                row = st[(st.fork == fork) & (st.team_abbr == "MIN")]
                exp = float(row.exp_2026_27.iloc[0])
                hb = float(row.hot_baseline.iloc[0])
                g = fc[fc.fork == fork]
                roll = A.rollup(minutes, imps[fork], "rs")
                net = exp + beta * (roll["net"] - hb)
                out[fork] = (float(np.interp(net, g.min_net, g.title)) * 100, net)
            return out

        def set_williams(minutes, target):
            """Williams to `target`; the freed minutes go down the rank order to anyone
            with room under his own ceiling. Minutes that cannot be placed are reported
            rather than silently discarded, because discarding them values Minnesota on
            fewer than 240 minutes and flatters the result."""
            out = dict(minutes)
            freed = out.get(WILLIAMS_ID, 0.0) - target
            out[WILLIAMS_ID] = target
            order = sorted([p for p in out if p != WILLIAMS_ID],
                           key=lambda p: -rank.get(p, 0))
            for p in order:
                if freed <= 1e-9:
                    break
                room = max(ceil.get(p, 0.0) - out.get(p, 0.0), 0.0)
                take = min(room, freed)
                out[p] = out.get(p, 0.0) + take
                freed -= take
            return out, freed

        rows = []
        for lv in LEVELS:
            m = dict(rot_min)
            unplaced = 0.0
            if lv is not None:
                m, unplaced = set_williams(rot_min, lv)
            wk = price(m)
            # and the same state with Kuminga removed, his minutes redistributed the
            # same way, so the marginal contribution is measured on a like basis
            m2 = dict(m)
            kfreed = m2.pop(KUMINGA_ID, 0.0)
            order = sorted(m2, key=lambda p: -rank.get(p, 0))
            for p in order:
                if kfreed <= 1e-9:
                    break
                room = max(ceil.get(p, 0.0) - m2.get(p, 0.0), 0.0)
                take = min(room, kfreed)
                m2[p] = m2.get(p, 0.0) + take
                kfreed -= take
            wo = price(m2)
            rec = dict(williams_mpg=(actual if lv is None else lv),
                       level=("model default" if lv is None else "%.0f" % lv),
                       unplaced_minutes=unplaced,
                       kuminga_unplaced=kfreed)
            for f in FORKS:
                rec["title_" + f] = wk[f][0]
                rec["net_" + f] = wk[f][1]
                rec["kuminga_pp_" + f] = wk[f][0] - wo[f][0]
            vals = [rec["kuminga_pp_" + f] for f in FORKS]
            rec["kuminga_mean_pp"] = float(np.mean(vals))
            rec["kuminga_sign"] = ("ALL POSITIVE" if min(vals) > 0 else
                                   "ALL NEGATIVE" if max(vals) < 0 else "MIXED")
            rec["title_mean"] = float(np.mean([rec["title_" + f] for f in FORKS]))
            rows.append(rec)

        d = pd.DataFrame(rows)
        d.to_csv(OUT, index=False)

        r.note("")
        r.note("MINNESOTA TITLE PROBABILITY by Cody Williams' minutes:")
        for _, x in d.iterrows():
            r.note("  %-14s %5.1f mpg -> title %.2f%% (range %.2f to %.2f), "
                   "Kuminga %+.3fpp %s%s"
                   % (x.level, x.williams_mpg, x.title_mean,
                      min(x["title_" + f] for f in FORKS),
                      max(x["title_" + f] for f in FORKS),
                      x.kuminga_mean_pp, x.kuminga_sign,
                      "" if x.unplaced_minutes < 0.01
                      else "  [%.1f min UNPLACED]" % x.unplaced_minutes))

        lo, hi = d.title_mean.min(), d.title_mean.max()
        r.note("")
        r.note("SPREAD attributable to this ONE assumption: %.2f to %.2f%% title "
               "probability, a factor of %.2fx." % (lo, hi, hi / lo if lo else 0))
        signs = set(d.kuminga_sign)
        r.note("Kuminga's verdict across the whole range: %s"
               % (", ".join(sorted(signs))))
        if len(signs) == 1:
            r.note("  STABLE. The section-5 claim does not depend on how many minutes "
                   "Cody Williams plays, so the Williams assumption is a caveat on the "
                   "TEAM number and not on the Kuminga number.")
        else:
            r.note("  NOT STABLE. The claim is conditional on the Williams assumption "
                   "and the piece must say so explicitly.")
        r.output(OUT, rows=len(d))

    print()
    cols = ["level", "williams_mpg", "title_mean", "kuminga_mean_pp", "kuminga_sign",
            "unplaced_minutes"]
    print(d[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
