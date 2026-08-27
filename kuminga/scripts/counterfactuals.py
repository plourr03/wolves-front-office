#!/usr/bin/env python3
"""Items 12 and 17: the Kuminga scenario fan, and the counterfactual fives.

BOTH ARE TALENT ROLLUPS, NOT FIT MODELS (R5). This machinery values a rotation by
minutes-weighting each player's impact estimate. It cannot see position, spacing,
handle, or who guards whom. Two players with the same net rating are interchangeable
to it, which is exactly the thing the fit engine was supposed to fix and cannot yet
(its synergy layer is scaffolding). So "Beringer at the 4" here means "Beringer's
minutes-weighted impact instead of Kuminga's", not a claim about a frontcourt that
plays two centres. Read these as talent accounting, and read the descriptive lineup
evidence (item 15) for anything about fit.

ITEM 12, the scenario fan: Kuminga's own impact is swept low / median / high from each
fork's posterior, plus a playoff-translation variant, and pushed through the f-curve.

ITEM 17, the counterfactual fives:
  actual          Ball / Edwards / McDaniels / Kuminga / Gobert
  beringer_4      Kuminga's slot goes to Joan Beringer
  mcdaniels_4     Kuminga's slot goes to the next wing on the roster
  alt_pf_*        Kuminga's slot goes to a power forward who actually signed
                  elsewhere this summer for money Minnesota could have paid
                  (at or under the $6,064,000 taxpayer MLE)

    python kuminga/scripts/counterfactuals.py
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
sys.path.insert(0, HERE)   # sibling scripts (build_strengths) regardless of how this is invoked

from kuminga.lib import kfreeze, runlog  # noqa: E402
import build_team_ratings as A           # noqa: E402
import bracket_sim as E                  # noqa: E402
from build_strengths import build_impacts, nkey  # noqa: E402
from shapley import allocate             # noqa: E402

POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
CURVE = os.path.join(REPO, "kuminga", "outputs", "minutes_rank_curve.csv")
FCURVE = os.path.join(REPO, "kuminga", "outputs", "fcurve_min.csv")
STR = os.path.join(REPO, "kuminga", "outputs", "team_strengths_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
OUT_FAN = os.path.join(REPO, "kuminga", "outputs", "scenario_fan.csv")
OUT_CF = os.path.join(REPO, "kuminga", "outputs", "counterfactual_fives.csv")

FORKS = ["consensus", "rapm", "box", "darko"]
KUMINGA = "Jonathan Kuminga"
TPMLE = 6_064_000

# Alternatives: real 2026 summer signings at or under the taxpayer MLE whom Minnesota
# could have paid with the same tool. Selected from the transaction log crossed with
# the contract book, then ranked by consensus impact.
ALTERNATIVES = [
    ("Josh Minott", 4_500_000, "BKN"),      # best affordable by consensus (+2.58), but
                                            # only 4,535 possessions, net_sd 2.10
    ("Jaxson Hayes", 6_000_000, "UTA"),     # +1.72 on 13,826 possessions, steadier
    ("Kenrich Williams", 5_000_000, "OKC"),  # +0.70, the median outcome for this money
]
# Above the taxpayer MLE, so NOT gettable with the tool Minnesota had. Carried purely
# as context for how much better the money would have had to be.
OUT_OF_REACH = [("Al Horford", 6_822_000, "GSW"), ("Dean Wade", 9_000_000, "PHI")]


def main():
    with runlog.run("counterfactuals", inputs={"pool": POOL, "fcurve": FCURVE}) as r:
        pool = pd.read_csv(POOL)
        curve = pd.read_csv(CURVE, index_col=0).iloc[:, 0]
        fc = pd.read_csv(FCURVE)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        st = pd.read_csv(STR)
        imps, _ = build_impacts(value, darko, bio)

        p = E.load_e_params()
        beta = float(p["beta"])
        exp_by_fork = {f: float(st[(st.fork == f) & (st.team_abbr == "MIN")].exp_2026_27.iloc[0])
                       for f in FORKS}
        hotbase_by_fork = {f: float(st[(st.fork == f) & (st.team_abbr == "MIN")].hot_baseline.iloc[0])
                           for f in FORKS}

        mn = pool[(pool.team_abbr == "MIN") & (pool.scenario == "current")].copy()
        r.note(f"MIN current pool: {len(mn)} players")

        vmap = value.set_index("player_id")

        def price(roster: pd.DataFrame, fork: str, kum_override: float | None = None,
                  kum_playoff_mult: bool = False):
            """roster -> (net, title).

            kum_override replaces Kuminga's total impact. kum_playoff_mult instead
            applies the ENGINE'S OWN playoff multiplier for his translation read to
            his offensive term, rather than an invented haircut: his record carries
            translation_read = 'slips', and build_team_ratings.PLAYOFF_OFF_MULT maps
            'slips' to 0.92. Using the engine's constant keeps this consistent with
            how every other playoff rollup in the project is computed.
            """
            mpg = allocate(roster, curve)
            imp = imps[fork]
            if kum_playoff_mult:
                kid = str(int(roster[roster.player_name == KUMINGA].player_id.iloc[0]))
                imp = dict(imp)
                base = dict(imp[kid])
                mult = A.PLAYOFF_OFF_MULT.get(base.get("read", ""), 1.0)
                base["off"] = base["off"] * mult
                imp[kid] = base
            if kum_override is not None:
                kid = str(int(roster[roster.player_name == KUMINGA].player_id.iloc[0]))
                imp = dict(imp)
                base = dict(imp.get(kid, {"off": 0.0, "def": 0.0, "off_sd": 1.5,
                                          "def_sd": 1.5, "def_div": 0.0, "read": ""}))
                # Move the override entirely through the offensive term, holding
                # defense fixed: the sweep is over his TOTAL impact and the split is
                # not separately identified at this resolution.
                shift = kum_override - (base["off"] - base["def"])
                base["off"] = base["off"] + shift
                imp[kid] = base
            roll = A.rollup(mpg, imp, "rs")
            net = exp_by_fork[fork] + beta * (roll["net"] - hotbase_by_fork[fork])
            g = fc[fc.fork == fork]
            return net, float(np.interp(net, g.min_net, g.title))

        # ---------------- item 12: scenario fan --------------------------------
        west = st[(st.fork == "consensus") & (st.conf == "W")]
        fan_rows = []
        for fork in FORKS:
            kv = value[value.player_id == 1630228].iloc[0]
            fork_net = {"consensus": float(kv.consensus_net),
                        "rapm": float(kv.off_rapm - kv.def_rapm),
                        "box": float(kv.box_off_prior - kv.box_def_prior),
                        "darko": None}[fork]
            if fork_net is None:
                dk = darko.copy()
                dk["k"] = dk["Player"].map(nkey)
                fork_net = float(dk[dk.k == nkey(KUMINGA)]["DPM"].iloc[0])
            sd = float(np.sqrt(kv.off_sd ** 2 + kv.def_sd ** 2))

            for label, val in (("low_p10", fork_net - 1.2816 * sd),
                               ("median", fork_net),
                               ("high_p90", fork_net + 1.2816 * sd),
                               ("playoff_slips", None)):
                if label == "playoff_slips":
                    net, title = price(mn, fork, kum_playoff_mult=True)
                    val = float("nan")
                else:
                    net, title = price(mn, fork, kum_override=val)
                w = st[(st.fork == fork) & (st.conf == "W")].copy()
                w.loc[w.team_abbr == "MIN", "net_current"] = net
                rank = int((w.net_current > net).sum()) + 1
                fan_rows.append(dict(fork=fork, scenario=label, kuminga_net=val,
                                     min_net=net, title=title, west_rank=rank))
                r.note(f"FAN [{fork:9s}/{label:13s}] Kuminga {val:+.2f} -> MIN net "
                       f"{net:+.2f}, title {title*100:.2f}%, West #{rank}")

        fan = pd.DataFrame(fan_rows)
        fan.to_csv(OUT_FAN, index=False)

        # ---------------- item 17: counterfactual fives ------------------------
        cf_rows = []
        wings = mn[(mn.player_name != KUMINGA)
                   & (~mn.player_name.isin(["Anthony Edwards", "LaMelo Ball",
                                            "Rudy Gobert", "Jaden McDaniels",
                                            "Joan Beringer", "[14th man placeholder]"]))]
        next_wing = wings.sort_values("consensus_net", ascending=False).iloc[0]
        r.note(f"'next wing up' resolves to {next_wing.player_name} "
               f"(consensus {next_wing.consensus_net:+.2f})")

        variants = {"actual": None, "beringer_4": "Joan Beringer",
                    "mcdaniels_4_next_wing": next_wing.player_name}
        for name, sal, team in ALTERNATIVES + OUT_OF_REACH:
            variants[f"alt_{nkey(name)}"] = name

        for vname, replacement in variants.items():
            for fork in FORKS:
                ros = mn.copy()
                note = ""
                if vname == "actual":
                    pass
                elif replacement in set(mn.player_name):
                    # Already on the roster: drop Kuminga, the slot reallocates
                    # internally to players already there.
                    ros = ros[ros.player_name != KUMINGA]
                    note = f"Kuminga removed; minutes reallocate, {replacement} promoted"
                else:
                    # An outside signing: swap Kuminga's row for his.
                    row = value[value.player_name == replacement]
                    if row.empty:
                        continue
                    rw = row.iloc[0]
                    ros = ros[ros.player_name != KUMINGA].copy()
                    prior = mn[mn.player_name == KUMINGA].prior_mpg.iloc[0]
                    ros = pd.concat([ros, pd.DataFrame([dict(
                        player_id=rw.player_id, player_name=replacement,
                        consensus_net=rw.consensus_net, prior_mpg=prior,
                        rs_avail=1.0)])], ignore_index=True)
                    note = f"{replacement} signed instead of Kuminga"
                net, title = price(ros, fork)
                cf_rows.append(dict(variant=vname, fork=fork, replacement=replacement or KUMINGA,
                                    min_net=net, title=title, note=note))

        # ---------------- minutes sensitivity ----------------------------------
        # The heuristic gives Kuminga about 25 minutes. The brief calls him a starter.
        # This is the robustness check on that gap, and the answer is mildly against
        # intuition: giving him MORE minutes makes Minnesota slightly worse under every
        # view, because his impact estimate sits below the minutes-weighted average of
        # the players whose minutes he would take (Gobert +5.28, Ball +2.29,
        # Beringer +2.29). The headline does not hinge on his role.
        ms_rows = []
        kum_heur = float(mn[mn.player_name == KUMINGA].prior_mpg.iloc[0])
        for target in (None, 28.0, 32.0, 36.0):
            for fork in FORKS:
                m = mn.copy()
                if target is not None:
                    mpg0 = allocate(m, curve)
                    kid = str(int(m[m.player_name == KUMINGA].player_id.iloc[0]))
                    rest = {k: v for k, v in mpg0.items() if k != kid}
                    scale = (240.0 - target) / sum(rest.values())
                    mpg = {k: v * scale for k, v in rest.items()}
                    mpg[kid] = target
                else:
                    mpg = allocate(m, curve)
                roll = A.rollup(mpg, imps[fork], "rs")
                net = exp_by_fork[fork] + beta * (roll["net"] - hotbase_by_fork[fork])
                g = fc[fc.fork == fork]
                ms_rows.append(dict(
                    kuminga_mpg=(target if target is not None
                                 else round(mpg[str(int(m[m.player_name == KUMINGA].player_id.iloc[0]))], 2)),
                    label="heuristic" if target is None else f"forced_{int(target)}",
                    fork=fork, min_net=net,
                    title=float(np.interp(net, g.min_net, g.title))))
        ms = pd.DataFrame(ms_rows)
        ms.to_csv(os.path.join(REPO, "kuminga", "outputs", "kuminga_minutes_sensitivity.csv"),
                  index=False)
        base_ms = ms[ms.label == "heuristic"].set_index("fork")
        r.note("MINUTES SENSITIVITY (title pp vs the heuristic's own allocation):")
        for lbl in ("forced_28", "forced_32", "forced_36"):
            d = ms[ms.label == lbl].set_index("fork")
            deltas = {f: (d.loc[f, "title"] - base_ms.loc[f, "title"]) * 100 for f in FORKS}
            r.note(f"  {lbl:11s} " + " ".join(f"{f}={deltas[f]:+.3f}" for f in FORKS))

        cf = pd.DataFrame(cf_rows)
        base = cf[cf.variant == "actual"].set_index("fork")
        cf["title_vs_actual_pp"] = cf.apply(
            lambda x: (x.title - base.loc[x.fork, "title"]) * 100, axis=1)
        cf.to_csv(OUT_CF, index=False)

        piv = cf.pivot_table(index="variant", columns="fork", values="title_vs_actual_pp")
        piv["mean"] = piv.mean(axis=1)
        r.note("COUNTERFACTUAL FIVES, title pp vs the actual five:")
        for v, x in piv.sort_values("mean", ascending=False).iterrows():
            r.note(f"  {v:26s} " + " ".join(f"{f}={x[f]:+.2f}" for f in FORKS) +
                   f"  mean={x['mean']:+.2f}")
        r.output(OUT_FAN, rows=len(fan))
        r.output(OUT_CF, rows=len(cf))

    print()
    print("SCENARIO FAN (item 12):")
    print(fan.pivot_table(index="scenario", columns="fork", values="title").mul(100).round(2).to_string())
    print()
    print("COUNTERFACTUAL FIVES (item 17), title pp vs actual:")
    print(piv.round(2).sort_values("mean", ascending=False).to_string())


if __name__ == "__main__":
    main()
