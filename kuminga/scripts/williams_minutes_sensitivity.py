#!/usr/bin/env python3
"""W1: every headline verdict as a function of one assumption about Cody Williams.

WHY THIS EXISTS. The Green trade put Cody Williams on Minnesota, and the rotation model
allocates from PRIOR MINUTES PER APPEARANCE. He played 24.3 a night for a 27-win Utah
team and his impact is -3.86, the worst on the roster, so the model handed him roughly
19 minutes on a contender and that became the single largest driver of Minnesota's
projected decline. Minutes per appearance is a ROLE signal, and a role earned on a
rebuilding team does not transfer. Nothing sourced says Williams plays 19 minutes here.

THE W1 RULE addresses this league-wide: team-changers are blended 80/20 toward the rank
curve instead of 50/50, so a mover is priced on the rank he earns with his new team
rather than the role he left. That is a structural fix applied identically to all 30.
This script is the SENSITIVITY that sits beside it, and it answers the question the rule
cannot: how much of each published verdict is still riding on this one number.

FOUR VERDICTS, all priced at each minutes level, none of them requiring a new season sim:

  TITLE PROBABILITY   from the f-curve, which is P(title | MIN net) with the field held
                      fixed. That is exactly what the f-curve was built for.
  OFFSEASON DELTA     title at MIN's current net minus title at MIN's baseline net, both
                      read off the same curve, so the comparison is like for like.
  PLAY-IN             from the same seeding draw `seed_distribution.py` uses: simulated
                      wins from net, ranked within conference. MIN's net is substituted
                      and every other team is left alone. Same RNG seed, so the figures
                      are directly comparable to that script's.
  KUMINGA SLOT        remove Kuminga, hand his minutes down the rank order under each
                      player's own ceiling, and re-price. This is the number section 5
                      of the piece actually claims.

WHAT MOVING THE MINUTES DOES AND DOES NOT DO. Reducing Williams' minutes hands them to
the rest of Minnesota's rotation under each player's ceiling. It does NOT change any
other team, so the field is fixed throughout and every figure here is a MIN-only
perturbation. That is the honest scope: it measures the sensitivity of our own
projection to our own assumption, not a forecast of what Finch will do.

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
LEVELS = [None, 16.0, 12.0, 8.0, 0.0]   # None = whatever the rotation rule allocates
SEED = 4242
NSIMS = 100_000


def sign_of(vals):
    return ("ALL POSITIVE" if min(vals) > 0 else
            "ALL NEGATIVE" if max(vals) < 0 else "MIXED")


def main():
    with runlog.run("williams_minutes_sensitivity",
                    inputs={"levels": [str(x) for x in LEVELS], "nsims": NSIMS,
                            "mover_curve_weight": rotation.MOVER_CURVE_WEIGHT}) as r:
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
        p = E.load_e_params()
        wa, wb, sig = float(p["wins_a"]), float(p["wins_b"]), float(p["sigma_record"])

        # D111: under the mover-discounted order he may be outside the ten, in which case
        # the model default is zero and the levels above it take minutes FROM the rotation
        actual = rot_min.get(WILLIAMS_ID, 0.0)
        wrow = mn[mn.player_id == float(WILLIAMS_ID)].iloc[0]
        r.note("Cody Williams: allocated %.2f mpg on a prior of %.2f, impact %.2f "
               "(consensus), ceiling %.2f"
               % (actual, wrow.prior_mpg, wrow.consensus_net, ceil[WILLIAMS_ID]))

        def net_for(minutes, fork):
            row = st[(st.fork == fork) & (st.team_abbr == "MIN")]
            exp = float(row.exp_2026_27.iloc[0])
            hb = float(row.hot_baseline.iloc[0])
            roll = A.rollup(minutes, imps[fork], "rs")
            return exp + beta * (roll["net"] - hb)

        def title_at(net, fork):
            g = fc[fc.fork == fork]
            return float(np.interp(net, g.min_net, g.title)) * 100

        # ---- play-in, using seed_distribution's own machinery -----------------
        west = st[(st.conf == "W")]

        def top6_for(net_by_fork):
            """P(MIN finishes top 6 in the West) with MIN's net replaced and every other
            team untouched. Same draw as seed_distribution.py."""
            out = {}
            rng = np.random.default_rng(SEED)
            for fork in FORKS:
                c = west[west.fork == fork]
                nets = c.net_current.to_numpy(dtype=float).copy()
                teams = c.team_abbr.tolist()
                nets[teams.index("MIN")] = net_by_fork[fork]
                wins = wa + wb * nets[None, :] + rng.normal(0, sig, (NSIMS, len(teams)))
                order = np.argsort(-wins, axis=1)
                seeds = np.empty_like(order)
                np.put_along_axis(seeds, order,
                                  np.arange(1, len(teams) + 1)[None, :]
                                  .repeat(NSIMS, 0), axis=1)
                s = seeds[:, teams.index("MIN")]
                out[fork] = float((s <= 6).mean())
            return out

        def hand_down(minutes, drop_id):
            """Remove a player and cascade his minutes down the rank order, each taker
            capped at his own ceiling. Minutes that cannot be placed are returned."""
            m = dict(minutes)
            freed = m.pop(drop_id, 0.0)
            for pid in sorted(m, key=lambda x: -rank.get(x, 0)):
                if freed <= 1e-9:
                    break
                take = min(max(ceil.get(pid, 0.0) - m.get(pid, 0.0), 0.0), freed)
                m[pid] = m.get(pid, 0.0) + take
                freed -= take
            return m, freed

        def set_williams(minutes, target):
            m = dict(minutes)
            freed = m.get(WILLIAMS_ID, 0.0) - target
            m[WILLIAMS_ID] = target
            if freed < -1e-9:
                # the minutes come FROM the others, in proportion to what each carries
                need = -freed
                others = {p: v for p, v in m.items() if p != WILLIAMS_ID}
                tot = sum(others.values())
                for pid, v in others.items():
                    m[pid] = v - need * v / tot
                return m, 0.0
            for pid in sorted([x for x in m if x != WILLIAMS_ID],
                              key=lambda x: -rank.get(x, 0)):
                if freed <= 1e-9:
                    break
                take = min(max(ceil.get(pid, 0.0) - m.get(pid, 0.0), 0.0), freed)
                m[pid] = m.get(pid, 0.0) + take
                freed -= take
            return m, freed

        rows = []
        for lv in LEVELS:
            m, unplaced = (dict(rot_min), 0.0) if lv is None else set_williams(rot_min, lv)
            net_k = {f: net_for(m, f) for f in FORKS}
            title_k = {f: title_at(net_k[f], f) for f in FORKS}
            base_t = {f: title_at(float(st[(st.fork == f)
                                          & (st.team_abbr == "MIN")].net_baseline.iloc[0]), f)
                      for f in FORKS}
            delta = {f: title_k[f] - base_t[f] for f in FORKS}
            top6 = top6_for(net_k)

            m2, kunp = hand_down(m, KUMINGA_ID)
            kpp = {f: title_k[f] - title_at(net_for(m2, f), f) for f in FORKS}

            rec = dict(williams_mpg=(actual if lv is None else lv),
                       level=("model default" if lv is None else "%.0f" % lv),
                       unplaced_minutes=unplaced, kuminga_unplaced=kunp)
            for f in FORKS:
                rec["net_" + f] = net_k[f]
                rec["title_" + f] = title_k[f]
                rec["delta_" + f] = delta[f]
                rec["top6_" + f] = top6[f]
                rec["kuminga_pp_" + f] = kpp[f]
            rec["title_mean"] = float(np.mean([title_k[f] for f in FORKS]))
            rec["title_lo"] = float(min(title_k.values()))
            rec["title_hi"] = float(max(title_k.values()))
            rec["delta_mean"] = float(np.mean([delta[f] for f in FORKS]))
            rec["delta_sign"] = sign_of([delta[f] for f in FORKS])
            rec["top6_mean"] = float(np.mean([top6[f] for f in FORKS]))
            rec["top6_lo"] = float(min(top6.values()))
            rec["top6_hi"] = float(max(top6.values()))
            rec["kuminga_mean_pp"] = float(np.mean([kpp[f] for f in FORKS]))
            rec["kuminga_sign"] = sign_of([kpp[f] for f in FORKS])
            rows.append(rec)

        d = pd.DataFrame(rows)
        d.to_csv(OUT, index=False)

        r.note("")
        r.note("EVERY HEADLINE VERDICT, as a function of Cody Williams' minutes:")
        for _, x in d.iterrows():
            r.note("  %-14s %5.1f mpg | title %.2f%% (%.2f-%.2f) | offseason delta "
                   "%+.2fpp %-13s | top-6 %.2f (%.2f-%.2f) | Kuminga %+.3fpp %s%s"
                   % (x.level, x.williams_mpg, x.title_mean, x.title_lo, x.title_hi,
                      x.delta_mean, x.delta_sign, x.top6_mean, x.top6_lo, x.top6_hi,
                      x.kuminga_mean_pp, x.kuminga_sign,
                      "" if x.unplaced_minutes < 0.01
                      else "  [%.1f UNPLACED]" % x.unplaced_minutes))

        r.note("")
        dsigns, ksigns = set(d.delta_sign), set(d.kuminga_sign)
        r.note("UNCONDITIONAL ACROSS THE RANGE?")
        r.note("  offseason delta sign : %s -> %s"
               % (", ".join(sorted(dsigns)),
                  "UNCONDITIONAL" if len(dsigns) == 1 else "CONDITIONAL"))
        r.note("  Kuminga slot sign    : %s -> %s"
               % (", ".join(sorted(ksigns)),
                  "UNCONDITIONAL" if len(ksigns) == 1 else "CONDITIONAL"))
        r.note("  title probability    : %.2f%% to %.2f%%, a factor of %.2fx"
               % (d.title_mean.min(), d.title_mean.max(),
                  d.title_mean.max() / d.title_mean.min() if d.title_mean.min() else 0))
        r.note("  P(top 6, avoids play-in): %.2f to %.2f"
               % (d.top6_mean.min(), d.top6_mean.max()))
        r.output(OUT, rows=len(d))

    print()
    cols = ["level", "williams_mpg", "title_mean", "delta_mean", "delta_sign",
            "top6_mean", "kuminga_mean_pp", "kuminga_sign"]
    print(d[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
