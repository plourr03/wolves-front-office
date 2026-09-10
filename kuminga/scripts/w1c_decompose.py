#!/usr/bin/env python3
"""W1c: what is Minnesota's projected decline actually made of?

The offseason delta is one number carrying at least three different things: real roster
moves (Reid and Randle out, Ball and Kuminga in, Green traded), a season-ending injury
that has nothing to do with the offseason at all, and a modelling assumption about a
player nobody has seen in a Minnesota uniform. Reporting them as one figure invites the
reader to attribute all of it to the front office. This separates them.

FOUR STATES, each a full re-allocation of Minnesota's 240 minutes through the SAME
allocator `build_rotations` uses, then priced on the same f-curve:

    CURRENT   as projected: DiVincenzo out for the season, Williams at his allocated load
    NO INJURY DiVincenzo available, minutes re-allocated around him
    NO WILLIAMS  Williams unavailable, his minutes cascading to the next men under their
                 own ceilings
    NEITHER   both

DEFINITIONS, so the arithmetic is checkable:

    D            = title(CURRENT) - title(BASELINE)          the published offseason delta
    injury cost  = title(NO INJURY) - title(CURRENT)         what the Achilles costs
    williams cost= title(NO WILLIAMS) - title(CURRENT)       what the assumption costs
    both         = title(NEITHER) - title(CURRENT)
    interaction  = both - injury cost - williams cost
    remainder    = D + both = title(NEITHER) - title(BASELINE)

The remainder is the honest "what the offseason did" number: the delta with the injury
and the Williams assumption both removed. THE INTERACTION IS THE POINT OF DOING IT THIS
WAY. Losing DiVincenzo and giving those wing minutes to a negative-impact player are not
independent events; the injury is what creates the minutes Williams absorbs. A decomposition
that assumed additivity would double-count or under-count that overlap, so it is measured.

    python kuminga/scripts/w1c_decompose.py
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

from kuminga.lib import kfreeze, rotation, runlog      # noqa: E402
import build_team_ratings as A                         # noqa: E402
import bracket_sim as E                                # noqa: E402
from build_strengths import build_impacts, add_rookie_impacts  # noqa: E402

POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
CURVE = os.path.join(REPO, "kuminga", "outputs", "minutes_rank_curve.csv")
FCURVE = os.path.join(REPO, "kuminga", "outputs", "fcurve_min.csv")
STR = os.path.join(REPO, "kuminga", "outputs", "team_strengths_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "w1c_delta_decomposition.csv")

FORKS = ["consensus", "rapm", "box", "darko"]
DDV = "Donte DiVincenzo"
WIL = "Cody Williams"


def sign_of(v):
    return ("ALL POSITIVE" if min(v) > 0 else
            "ALL NEGATIVE" if max(v) < 0 else "MIXED")


def main():
    with runlog.run("w1c_decompose", inputs={"states": 4}) as r:
        pool = pd.read_csv(POOL)
        cur = pd.read_csv(CURVE, index_col=0).iloc[:, 0]
        fc = pd.read_csv(FCURVE)
        st = pd.read_csv(STR)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, pool)
        beta = float(E.load_e_params()["beta"])

        mn = pool[(pool.scenario == "current") & (pool.team_abbr == "MIN")].copy()
        r.note("MIN pool: %d players, DiVincenzo rs_avail=%.2f, Williams prior %.2f"
               % (len(mn), float(mn[mn.player_name == DDV].rs_avail.iloc[0]),
                  float(mn[mn.player_name == WIL].prior_mpg.iloc[0])))

        def state(no_injury=False, no_williams=False):
            g = mn.copy()
            if no_injury:
                g.loc[g.player_name == DDV, "rs_avail"] = 1.0
            if no_williams:
                g.loc[g.player_name == WIL, "rs_avail"] = 0.0
            return rotation.allocate(g, cur, use_ceiling=True)

        def price(minutes):
            out = {}
            for f in FORKS:
                row = st[(st.fork == f) & (st.team_abbr == "MIN")]
                exp = float(row.exp_2026_27.iloc[0])
                hb = float(row.hot_baseline.iloc[0])
                net = exp + beta * (A.rollup(minutes, imps[f], "rs")["net"] - hb)
                g = fc[fc.fork == f]
                out[f] = (float(np.interp(net, g.min_net, g.title)) * 100, net)
            return out

        states = {
            "CURRENT": state(),
            "NO INJURY": state(no_injury=True),
            "NO WILLIAMS": state(no_williams=True),
            "NEITHER": state(no_injury=True, no_williams=True),
        }
        priced = {k: price(v) for k, v in states.items()}
        base_t = {f: float(np.interp(
            float(st[(st.fork == f) & (st.team_abbr == "MIN")].net_baseline.iloc[0]),
            fc[fc.fork == f].min_net, fc[fc.fork == f].title)) * 100 for f in FORKS}

        r.note("")
        r.note("MINUTES by state (MIN, the players that move):")
        for k, mp in states.items():
            nm = {str(int(x.player_id)): x.player_name for _, x in mn.iterrows()
                  if pd.notna(x.player_id)}
            shown = {nm.get(p, p): round(m, 1) for p, m in mp.items()
                     if nm.get(p) in (DDV, WIL, "Jonathan Kuminga", "Nah'Shon Hyland",
                                      "Jaylen Clark", "Terrence Shannon Jr.")}
            r.note("  %-12s %s" % (k, shown))

        rows = []
        for f in FORKS:
            T = {k: priced[k][f][0] for k in states}
            D = T["CURRENT"] - base_t[f]
            inj = T["NO INJURY"] - T["CURRENT"]
            wil = T["NO WILLIAMS"] - T["CURRENT"]
            both = T["NEITHER"] - T["CURRENT"]
            rows.append(dict(fork=f, title_baseline=base_t[f],
                             title_current=T["CURRENT"],
                             title_no_injury=T["NO INJURY"],
                             title_no_williams=T["NO WILLIAMS"],
                             title_neither=T["NEITHER"],
                             offseason_delta=D, injury_cost=inj, williams_cost=wil,
                             both=both, interaction=both - inj - wil,
                             remainder=D + both))
        d = pd.DataFrame(rows)
        d.to_csv(OUT, index=False)

        def band(col):
            v = d[col].tolist()
            return "%+.3f  [%+.3f, %+.3f]  %s" % (np.mean(v), min(v), max(v), sign_of(v))

        r.note("")
        r.note("DECOMPOSITION of Minnesota's offseason title-odds delta (pp):")
        r.note("  published offseason delta D          %s" % band("offseason_delta"))
        r.note("  what the DiVincenzo injury costs     %s" % band("injury_cost"))
        r.note("     (positive = odds would be HIGHER with him healthy)")
        r.note("  what the Cody Williams load costs    %s" % band("williams_cost"))
        r.note("     (positive = odds would be HIGHER if he did not play)")
        r.note("  both removed                         %s" % band("both"))
        r.note("  INTERACTION (both - injury - williams) %s" % band("interaction"))
        r.note("  REMAINDER, the offseason itself      %s" % band("remainder"))

        r.note("")
        i_m, w_m, x_m = (d.injury_cost.mean(), d.williams_cost.mean(),
                         d.interaction.mean())
        r.note("THE DIVINCENZO-WILLIAMS INTERACTION, stated explicitly.")
        r.note("  Removing the injury alone is worth %+.3fpp and removing the Williams "
               "load alone is worth %+.3fpp, which would sum to %+.3fpp. Removing both "
               "is actually worth %+.3fpp, so the interaction is %+.3fpp."
               % (i_m, w_m, i_m + w_m, d.both.mean(), x_m))
        if x_m < -0.005:
            r.note("  The interaction is NEGATIVE, meaning the two fixes OVERLAP: they "
                   "are partly the same wound. DiVincenzo's absence is what frees the "
                   "wing minutes Williams absorbs, so healing the injury and benching "
                   "Williams are competing for the same minutes and cannot both be "
                   "banked. Adding the two separate figures OVERSTATES the combined "
                   "repair by %.3fpp." % abs(x_m))
        elif x_m > 0.005:
            r.note("  The interaction is POSITIVE: the two fixes REINFORCE, and doing "
                   "both is worth more than the sum of doing each.")
        else:
            r.note("  The interaction is negligible; the two effects are close to "
                   "additive over this range.")

        r.note("")
        rem = d.remainder.tolist()
        r.note("WHAT THE OFFSEASON ITSELF DID, once the injury and the Williams "
               "assumption are both taken out: %s" % band("remainder"))
        r.note("  This is the number that belongs next to 'the front office made the "
               "team worse', because it is the only one of these that the front office "
               "actually chose.")
        r.output(OUT, rows=len(d))

    print()
    print(d[["fork", "offseason_delta", "injury_cost", "williams_cost",
             "interaction", "remainder"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
