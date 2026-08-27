#!/usr/bin/env python3
"""F4: one coalition. What does KEEPING Josh Green do on the floor?

Everywhere else in this project Green is off the roster: R3 has him gone in both cap
branches, because both branches exist precisely to move him. That is a cap assumption,
and it has never been priced as a basketball question. If keeping him is positive under
all four views, then "Dosunmu's contract is why Green has to be shed" has an on-court
cost attached to it and belongs in claim (a). If the views disagree, it stays in the
appendix.

METHOD. Take Minnesota's current roster, add Green as a guard, re-allocate minutes under
the same pooled slot rule the primary Shapley run uses (Minnesota's own 2025-26 position
budgets), and price the difference under each of the four impact views.

His league-wide rank score is recomputed against the CURRENT scenario's distribution
rather than reused from the baseline scenario, because the percentile map moves between
scenarios and a stale rank would silently mis-slot him.

    python kuminga/scripts/green_kept.py
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

from kuminga.lib import kfreeze, rotation, runlog          # noqa: E402
import build_team_ratings as A                              # noqa: E402
import bracket_sim as E                                     # noqa: E402
from build_strengths import build_impacts, add_rookie_impacts  # noqa: E402

OUTDIR = os.path.join(REPO, "kuminga", "outputs")
POOL = os.path.join(OUTDIR, "player_pool_2026_27.csv")
FCURVE = os.path.join(OUTDIR, "fcurve_min.csv")
STR = os.path.join(OUTDIR, "team_strengths_2026_27.csv")
SHARE = os.path.join(OUTDIR, "team_pool_shares.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT = os.path.join(OUTDIR, "green_kept.csv")

FORKS = ["consensus", "rapm", "box", "darko"]
GREEN_ID = 1630182


def main():
    with runlog.run("green_kept", inputs={"player_id": GREEN_ID,
                                          "minutes_rule": "pooled, MIN budget"}) as r:
        pool = pd.read_csv(POOL)
        fc = pd.read_csv(FCURVE)
        st = pd.read_csv(STR)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, pool)
        budget = pd.read_csv(SHARE, index_col=0).loc["MIN"].to_dict()

        cur = pool[pool.scenario == "current"].copy()
        mn = cur[cur.team_abbr == "MIN"].copy()

        g = pool[(pool.player_id == GREEN_ID)].iloc[0]
        # league-wide percentiles, recomputed against the CURRENT distribution
        pct_mpg = float((cur.prior_mpg < g.prior_mpg).mean())
        pct_net = float((cur.consensus_net < g.consensus_net).mean())
        rank = 0.5 * pct_mpg + 0.5 * pct_net
        r.note(f"Josh Green: prior {g.prior_mpg:.2f} mpg, consensus net "
               f"{g.consensus_net:+.2f}, listed {g.position} -> pool "
               f"'{rotation.pool_of(g.position)}'")
        r.note(f"  league-wide rank score recomputed on the CURRENT pool: "
               f"{rank:.4f} (was {g.rank_score:.4f} in the baseline scenario)")
        assert str(GREEN_ID) in imps["consensus"], "Green missing from the impact table"
        for f in FORKS:
            iv = imps[f][str(GREEN_ID)]
            r.note(f"  impact, {f}: off {iv['off']:+.2f} def {iv['def']:+.2f} "
                   f"net {iv['off'] + iv['def']:+.2f}")

        green_row = dict(player_id=float(GREEN_ID), player_name="Josh Green",
                         consensus_net=g.consensus_net, prior_mpg=g.prior_mpg,
                         rank_score=rank, pool=rotation.pool_of(g.position),
                         rs_avail=1.0)
        without = mn[["player_id", "player_name", "consensus_net", "prior_mpg",
                      "rank_score", "pool", "rs_avail"]].reset_index(drop=True)
        with_g = pd.concat([without, pd.DataFrame([green_row])], ignore_index=True)

        curve = pd.read_csv(os.path.join(OUTDIR, "minutes_rank_curve.csv"),
                            index_col=0).iloc[:, 0]
        beta = float(E.load_e_params()["beta"])

        def price(players):
            mins = rotation.allocate_pooled(players, curve, budget_share=budget)
            out = {}
            for fork in FORKS:
                row = st[(st.fork == fork) & (st.team_abbr == "MIN")]
                exp, hb = float(row.exp_2026_27.iloc[0]), float(row.hot_baseline.iloc[0])
                net = exp + beta * (A.rollup(mins, imps[fork], "rs")["net"] - hb)
                out[fork] = float(np.interp(net, fc[fc.fork == fork].min_net,
                                            fc[fc.fork == fork].title)) * 100
            return out, mins

        p_wo, m_wo = price(without)
        p_w, m_w = price(with_g)

        gmin = m_w.get(str(GREEN_ID), 0.0)
        assert gmin > 0, "Green got no minutes; the key convention broke"
        r.note(f"Green is allocated {gmin:.2f} mpg in the pooled rotation; the guard "
               f"budget is fixed, so those minutes come out of the other guards.")
        moved = {k: m_w.get(k, 0.0) - m_wo.get(k, 0.0) for k in m_wo}
        for pid, dm in sorted(moved.items(), key=lambda x: x[1])[:4]:
            nm = without[without.player_id.astype(float) == float(pid)].player_name
            if len(nm) and abs(dm) > 0.05:
                r.note(f"    {nm.iloc[0]:20s} {dm:+.2f} mpg")

        marg = {f: p_w[f] - p_wo[f] for f in FORKS}
        vals = list(marg.values())
        sign = ("ALL POSITIVE" if all(v > 0 for v in vals) else
                "ALL NEGATIVE" if all(v < 0 for v in vals) else "MIXED")
        for f in FORKS:
            r.note(f"  {f:10s} without {p_wo[f]:.3f}%  with {p_w[f]:.3f}%  "
                   f"marginal {marg[f]:+.3f}pp")
        r.note(f"VERDICT, keeping Green: {sign} [{min(vals):+.3f}, {max(vals):+.3f}]pp, "
               f"mean {np.mean(vals):+.3f}pp")
        if sign == "ALL POSITIVE":
            r.note("RULING: positive under all four, so the on-court cost of shedding "
                   "Green belongs in claim (a) as one sentence.")
        else:
            r.note("RULING: not positive under all four, so it stays in the appendix and "
                   "the piece does not attach an on-court cost to losing Green.")

        pd.DataFrame([dict(move="green_kept", green_mpg=gmin,
                           **{f: marg[f] for f in FORKS},
                           mean_pp=float(np.mean(vals)), lo_pp=min(vals),
                           hi_pp=max(vals), sign_agreement=sign)]).to_csv(OUT, index=False)
        r.output(OUT, rows=1)


if __name__ == "__main__":
    main()
