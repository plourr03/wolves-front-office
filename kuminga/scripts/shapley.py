#!/usr/bin/env python3
"""Item 11: Shapley decomposition of Minnesota's title-odds change.

EXACT enumeration. With 8 moves that is 2^8 = 256 coalitions, and every coalition is
priced by interpolating the pre-built f-curve (item 11 stage 1) rather than simulated,
so the whole decomposition runs in seconds and no permutation sampling is needed. There
is therefore NO sampling error to report: the only Monte Carlo noise is the f-curve's,
which is carried through as the curve's own seed-to-seed spread.

THE MOVE SET. Seven come from the brief. The eighth is added so the decomposition is
COMPLETE, i.e. the marginal contributions sum exactly to v(all) - v(none) with no
unexplained residual:

  1 randle_out          Julius Randle to Brooklyn
  2 reid_out            Naz Reid to Charlotte
  3 ball_in             LaMelo Ball in
  4 dosunmu_retained    Ayo Dosunmu re-signed (counterfactual: he walks)
  5 depth               Hyland + Clark retained, Evans + Lyles added, as one bundle
  6 ddv_injury          DiVincenzo's Achilles (R7: out for the regular season)
  7 kuminga_in          Jonathan Kuminga in
  8 other_departures    Conley, Anderson, Ingles, Phillips, Zikarsky, Pullin, Freeman

Josh Green appears in no coalition: per R3 both branches have him off the roster, so he
is not a lever, he is a precondition.

ORDER DEPENDENCE. Shapley averages a move's marginal contribution over all 8! = 40,320
orderings, which is exactly the point: these moves interact (Kuminga's value depends on
whether Randle and Reid are gone), so no single ordering is honest. The spread of a
move's marginal contribution ACROSS orderings is reported alongside its Shapley value,
because a move whose contribution swings widely by order is one whose headline number
should be read as a range.

Per R1 the publishable claim is SIGN AGREEMENT ACROSS FORKS, not the point estimate.

    python kuminga/scripts/shapley.py
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from math import factorial

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import kfreeze, runlog  # noqa: E402
import build_team_ratings as A           # noqa: E402
import bracket_sim as E                  # noqa: E402
from build_strengths import build_impacts, nkey  # noqa: E402

POOL = os.path.join(REPO, "kuminga", "outputs", "player_pool_2026_27.csv")
CURVE = os.path.join(REPO, "kuminga", "outputs", "minutes_rank_curve.csv")
FCURVE = os.path.join(REPO, "kuminga", "outputs", "fcurve_min.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
STR = os.path.join(REPO, "kuminga", "outputs", "team_strengths_2026_27.csv")
OUT = os.path.join(REPO, "kuminga", "outputs", "shapley_min.csv")
OUT_ORD = os.path.join(REPO, "kuminga", "outputs", "shapley_order_spread.csv")

ROTATION_SIZE = 10
CURVE_WEIGHT = 0.5
MPG_WEIGHT = 0.5
TEAM_MINUTES = 240.0
FORKS = ["consensus", "rapm", "box", "darko"]

ALWAYS = ["Anthony Edwards", "Rudy Gobert", "Jaden McDaniels", "Joan Beringer",
          "Terrence Shannon Jr.", "[14th man placeholder]"]

MOVES = [
    "randle_out", "reid_out", "ball_in", "dosunmu_retained",
    "depth", "ddv_injury", "kuminga_in", "other_departures",
]

REMOVE_WHEN_APPLIED = {
    "randle_out": ["Julius Randle"],
    "reid_out": ["Naz Reid"],
    "other_departures": ["Mike Conley", "Kyle Anderson", "Joe Ingles",
                         "Julian Phillips", "Rocco Zikarsky", "Zyon Pullin",
                         "Enrique Freeman"],
}
ADD_WHEN_APPLIED = {
    "ball_in": ["LaMelo Ball"],
    "dosunmu_retained": ["Ayo Dosunmu"],
    "depth": ["Bones Hyland", "Jaylen Clark", "Isaiah Evans", "Trey Lyles"],
    "kuminga_in": ["Jonathan Kuminga"],
}
# Players present in the 2025-26 baseline that a move REMOVES if applied, but which
# must be present when the move is not applied.
PRESENT_UNLESS_APPLIED = set(sum(REMOVE_WHEN_APPLIED.values(), []))
# Players who exist in the baseline AND are re-added by a move; if the move is not
# applied they are gone (they were free agents).
BASELINE_AND_MOVE = {"Ayo Dosunmu", "Bones Hyland", "Jaylen Clark"}


def allocate(players: pd.DataFrame, curve: pd.Series) -> dict:
    """The item-8 minutes heuristic, applied to one coalition's roster."""
    g = players[players.rs_avail > 0].copy()
    if g.empty:
        return {}
    g["pct_mpg"] = g.prior_mpg.rank(pct=True)
    g["pct_net"] = g.consensus_net.rank(pct=True)
    g["rank_score"] = MPG_WEIGHT * g.pct_mpg + (1 - MPG_WEIGHT) * g.pct_net
    g = g.sort_values("rank_score", ascending=False).head(ROTATION_SIZE).reset_index(drop=True)
    g["rot_rank"] = g.index + 1
    cm = g.rot_rank.map(lambda i: curve.get(float(i), curve.iloc[-1]))
    base = CURVE_WEIGHT * cm + (1 - CURVE_WEIGHT) * g.prior_mpg
    mpg = base * g.rs_avail
    mpg = mpg / mpg.sum() * TEAM_MINUTES
    return {str(int(p)): float(m) for p, m in zip(g.player_id, mpg) if pd.notna(p)}


def main():
    with runlog.run("shapley", inputs={"pool": POOL, "fcurve": FCURVE,
                                       "moves": MOVES, "coalitions": 2 ** len(MOVES)}) as r:
        pool = pd.read_csv(POOL)
        curve = pd.read_csv(CURVE, index_col=0).iloc[:, 0]
        fc = pd.read_csv(FCURVE)
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        st = pd.read_csv(STR)
        imps, _ = build_impacts(value, darko, bio)

        # One attribute row per player, drawn from whichever scenario has him.
        mn = pool[pool.team_abbr == "MIN"].copy()
        mn["k"] = mn.player_name.map(nkey)
        attrs = mn.sort_values("scenario").drop_duplicates("k", keep="last").set_index("k")
        r.note(f"MIN player attributes available for {len(attrs)} players")

        needed = set(ALWAYS) | PRESENT_UNLESS_APPLIED | set(sum(ADD_WHEN_APPLIED.values(), [])) | {"Donte DiVincenzo"}
        missing = [n for n in needed if nkey(n) not in attrs.index]
        if missing:
            r.note(f"WARNING: no attributes for {missing}")

        def roster_for(coalition: frozenset) -> pd.DataFrame:
            names = list(ALWAYS)
            for mv, players in REMOVE_WHEN_APPLIED.items():
                if mv not in coalition:
                    names += players
            for mv, players in ADD_WHEN_APPLIED.items():
                if mv in coalition:
                    names += players
            rows = []
            for n in names:
                k = nkey(n)
                if k not in attrs.index:
                    continue
                a = attrs.loc[k]
                rows.append(dict(player_id=a.player_id, player_name=n,
                                 consensus_net=a.consensus_net, prior_mpg=a.prior_mpg,
                                 rs_avail=1.0))
            # DiVincenzo: present either way; the move flips his availability.
            k = nkey("Donte DiVincenzo")
            if k in attrs.index:
                a = attrs.loc[k]
                rows.append(dict(player_id=a.player_id, player_name="Donte DiVincenzo",
                                 consensus_net=a.consensus_net, prior_mpg=a.prior_mpg,
                                 rs_avail=0.0 if "ddv_injury" in coalition else 1.0))
            return pd.DataFrame(rows)

        # ---- value function: coalition -> P(title) per fork ---------------------
        p = E.load_e_params()
        beta = float(p["beta"])
        measured_exp = {f: float(st[(st.fork == f) & (st.team_abbr == "MIN")].exp_2026_27.iloc[0])
                        for f in FORKS}
        hot_base = {f: float(st[(st.fork == f) & (st.team_abbr == "MIN")].hot_baseline.iloc[0])
                    for f in FORKS}

        all_coalitions = []
        for k in range(len(MOVES) + 1):
            all_coalitions += [frozenset(c) for c in itertools.combinations(MOVES, k)]
        r.note(f"enumerating {len(all_coalitions)} coalitions")

        vals = {f: {} for f in FORKS}
        nets = {f: {} for f in FORKS}
        for coal in all_coalitions:
            ros = roster_for(coal)
            mpg = allocate(ros, curve)
            for fork in FORKS:
                roll = A.rollup(mpg, imps[fork], "rs")
                net = measured_exp[fork] + beta * (roll["net"] - hot_base[fork])
                nets[fork][coal] = net
                g = fc[fc.fork == fork]
                vals[fork][coal] = float(np.interp(net, g.min_net, g.title))

        for fork in FORKS:
            r.note(f"{fork}: v(none)={vals[fork][frozenset()]*100:.3f}% "
                   f"v(all)={vals[fork][frozenset(MOVES)]*100:.3f}% "
                   f"total={((vals[fork][frozenset(MOVES)]-vals[fork][frozenset()])*100):+.3f}pp")

        # ---- exact Shapley -------------------------------------------------------
        n = len(MOVES)
        rows = []
        for fork in FORKS:
            v = vals[fork]
            for mv in MOVES:
                phi = 0.0
                others = [m for m in MOVES if m != mv]
                for k in range(len(others) + 1):
                    w = factorial(k) * factorial(n - k - 1) / factorial(n)
                    for sub in itertools.combinations(others, k):
                        S = frozenset(sub)
                        phi += w * (v[S | {mv}] - v[S])
                rows.append(dict(fork=fork, move=mv, shapley_pp=phi * 100))
        sh = pd.DataFrame(rows)

        # ---- order dependence: marginal contribution across random orderings -----
        rng = np.random.default_rng(20260827)
        ord_rows = []
        for fork in FORKS:
            v = vals[fork]
            marg = {m: [] for m in MOVES}
            for _ in range(2000):
                perm = list(rng.permutation(MOVES))
                S = frozenset()
                for mv in perm:
                    marg[mv].append(v[S | {mv}] - v[S])
                    S = S | {mv}
            for mv in MOVES:
                a = np.array(marg[mv]) * 100
                ord_rows.append(dict(fork=fork, move=mv, mean_pp=a.mean(),
                                     min_pp=a.min(), max_pp=a.max(),
                                     sd_pp=a.std(), spread_pp=a.max() - a.min()))
        ordf = pd.DataFrame(ord_rows)

        piv = sh.pivot(index="move", columns="fork", values="shapley_pp")
        piv["sign_agreement"] = piv[FORKS].apply(
            lambda x: "ALL POSITIVE" if (x > 0).all() else
                      ("ALL NEGATIVE" if (x < 0).all() else "MIXED"), axis=1)
        piv["mean_pp"] = piv[FORKS].mean(axis=1)
        piv = piv.sort_values("mean_pp", ascending=False)
        piv.to_csv(OUT)
        ordf.to_csv(OUT_ORD, index=False)

        r.note("SHAPLEY (pp of title probability):")
        for mv, x in piv.iterrows():
            r.note(f"  {mv:18s} " + " ".join(f"{f}={x[f]:+.3f}" for f in FORKS) +
                   f"  mean={x.mean_pp:+.3f}  {x.sign_agreement}")
        r.output(OUT, rows=len(piv))
        r.output(OUT_ORD, rows=len(ordf))

    print()
    print(piv.round(3).to_string())
    print()
    print("Order dependence (consensus fork), marginal contribution across 2000 random orderings:")
    print(ordf[ordf.fork == "consensus"][["move", "mean_pp", "min_pp", "max_pp", "spread_pp"]]
          .round(3).to_string(index=False))


if __name__ == "__main__":
    main()
