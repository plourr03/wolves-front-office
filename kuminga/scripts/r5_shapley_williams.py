#!/usr/bin/env python3
"""R5: the Shapley grand coalition is missing Cody Williams. How much does it matter?

Found in the consistency pass. `reconcile_figures.py` compares Shapley's "what actually
happened" coalition with the direct simulation of the current roster and has always
called the difference interpolation error. It was 0.06 to 0.07 points when written
(2026-08-27) and above 1.1 in every committed version since 2026-09-03 (1.24 at the start
of this pass), because on 2026-08-29 Minnesota traded Josh Green for Cody Williams and Konchar
(D56), the simulated roster gained Williams at 16.1 minutes, and `shapley.py` never did:
its ALWAYS list still carries a "[14th man placeholder]" that has no attributes and is
silently skipped. Every coalition, the grand coalition included, is priced without him.

Williams is not a lever in the decomposition. Like Green's departure he is a
precondition of both branches, so he belongs in every coalition. This script prices the
eight-move game both ways on both aging bases and applies the shipping rule to each.

A second gap of the same kind surfaced while checking the first: coalition rows were
built without the `curve_weight` column, so the W1 team-changer rule (0.8 for movers,
D59) never reached the attribution allocator. `williams_only` isolates the first fix;
`after_d85` carries both.

Now that `shapley.py` carries the fix, this script is the before/after record. The
pre-D85 tables are frozen in outputs/pre_d85 (SHA256SUMS alongside).

  G1  the post-D85 list reproduces the tables `shapley.py` now writes, on both bases and
      both allocators. That is the enforced gate. The pre-D85 list is priced too, and its
      difference from the frozen pre-D85 tables is REPORTED, not enforced: those tables were
      priced on the impact spine of that day and D89 refit RAPM, so they cannot reproduce.
  G2  the floors reproduce the published clearing counts for the current tables.
  G3  post-D85, the grand coalition's roster is exactly the simulated current roster
      (same 14 player ids).
  G4  reported, not enforced: post-D85, the team-rank grand coalition against the direct
      simulation. What is left is interpolation.

It also re-runs the R2 split of the departures bundle with Williams present, and, as a
sensitivity only, prices the fixed game under the team-rank allocator the headline
simulation uses (the shipping rule stays on the pooled attribution allocator, S1/W1b).


    python kuminga/scripts/r5_shapley_williams.py
"""
from __future__ import annotations

import itertools
import os
import sys
from math import factorial

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
sys.path.insert(0, HERE)
sys.argv = [sys.argv[0], "--pooled"] + [a for a in sys.argv[1:] if a != "--pooled"]

import shapley as SH                       # noqa: E402  (module constants, pooled mode)
import build_team_ratings as A             # noqa: E402
import bracket_sim as E                    # noqa: E402
from build_strengths import build_impacts  # noqa: E402
from kuminga.lib import kfreeze, rotation, runlog  # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
OUT = os.path.join(OUT_DIR, "r5_shapley_williams.csv")
OUT_V = os.path.join(OUT_DIR, "r5_shapley_williams_verdicts.csv")
OUT_ALL = os.path.join(OUT_DIR, "r5_shapley_williams_vall.csv")
FORKS = SH.FORKS
DEPARTURES = SH.REMOVE_WHEN_APPLIED["other_departures"]
BASES = {
    "unaged": dict(strengths=os.path.join(OUT_DIR, "team_strengths_2026_27.csv"),
                   fcurve=os.path.join(OUT_DIR, "fcurve_min.csv"),
                   shapley=os.path.join(OUT_DIR, "shapley_min_POOLED.csv"),
                   floor=os.path.join(OUT_DIR, "noise_floor.csv"),
                   sim=os.path.join(OUT_DIR, "preaging", "sim_all30_2026_27.csv"), aging="0"),
    "aged": dict(strengths=os.path.join(OUT_DIR, "aged", "team_strengths_2026_27.csv"),
                 fcurve=os.path.join(OUT_DIR, "aged", "fcurve_min.csv"),
                 shapley=os.path.join(OUT_DIR, "aged", "shapley_min_POOLED.csv"),
                 floor=os.path.join(OUT_DIR, "aged", "noise_floor_AGED.csv"),
                 sim=os.path.join(OUT_DIR, "aged", "sim_all30_2026_27.csv"), aging="1"),
}
# the ALWAYS list as it stood before D85, and as it stands now
BEFORE = ["Anthony Edwards", "Rudy Gobert", "Jaden McDaniels", "Joan Beringer",
          "Terrence Shannon Jr.", "[14th man placeholder]"]
AFTER = list(SH.ALWAYS)


def floors_for(fc, st):
    """noise_floor.py, line for line: 2 x sqrt(2) x hypot(MC, interpolation), per view."""
    out = {}
    for f in FORKS:
        g = fc[fc.fork == f].sort_values("min_net").reset_index(drop=True)
        net = float(st[(st.fork == f) & (st.team_abbr == "MIN")].net_current.iloc[0])
        mc = float(np.interp(net, g.min_net, g.title_sd)) * 100
        h = float(g.min_net.diff().median())
        d2 = np.abs(np.diff(g.title.to_numpy(), 2)) / (h ** 2)
        idx = int(np.clip(np.searchsorted(g.min_net.to_numpy(), net) - 1, 0, len(d2) - 1))
        lo, hi = max(0, idx - 2), min(len(d2), idx + 3)
        f2 = float(np.max(d2[lo:hi])) if hi > lo else float(np.max(d2))
        out[f] = 2.0 * float(np.hypot(mc, (h ** 2) / 8.0 * f2 * 100)) * np.sqrt(2)
    return out


def sign_of(x):
    return "ALL POSITIVE" if (x > 0).all() else "ALL NEGATIVE" if (x < 0).all() else "MIXED"


def main():
    with runlog.run("r5_shapley_williams", inputs={"always_before": BEFORE,
                                                   "always_after": AFTER,
                                                   "bases": list(BASES)}) as r:
        pool = pd.read_csv(SH.POOL)
        curve = pd.read_csv(SH.CURVE, index_col=0).iloc[:, 0]
        value = pd.read_csv(SH.VALUE)
        darko = pd.read_csv(SH.DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        mn = pool[pool.team_abbr == "MIN"].copy()
        mn["k"] = mn.player_name.map(SH.nkey)
        attrs = mn.sort_values("scenario").drop_duplicates("k", keep="last").set_index("k")
        beta = float(E.load_e_params()["beta"])

        def roster_for(coal, always, remove, add, weights=True):
            names = list(always)
            for mv, players in remove.items():
                if mv not in coal:
                    names += players
            for mv, players in add.items():
                if mv in coal:
                    names += players
            rows = []
            for n in names:
                k = SH.nkey(n)
                if k not in attrs.index:
                    continue
                a = attrs.loc[k]
                rows.append(dict(player_id=a.player_id, player_name=n,
                                 consensus_net=a.consensus_net, prior_mpg=a.prior_mpg,
                                 rank_score=a.rank_score, pool=a.get("pool", "forward"),
                                 rs_avail=1.0))
                if weights:
                    rows[-1]["curve_weight"] = a.curve_weight
            a = attrs.loc[SH.nkey("Donte DiVincenzo")]
            rows.append(dict(player_id=a.player_id, player_name="Donte DiVincenzo",
                             consensus_net=a.consensus_net, prior_mpg=a.prior_mpg,
                             rank_score=a.rank_score, pool=a.get("pool", "guard"),
                             rs_avail=0.0 if "ddv_injury" in coal else 1.0))
            if weights:
                rows[-1]["curve_weight"] = a.curve_weight
            return pd.DataFrame(rows)

        def teamrank(players, curve_):
            return rotation.allocate(players, curve_, use_ceiling=True)

        def game(moves, always, remove, add, imps, st, fc, alloc=None, weights=True):
            alloc = alloc or SH.allocate
            coals = [frozenset(c) for k in range(len(moves) + 1)
                     for c in itertools.combinations(moves, k)]
            exp = {f: float(st[(st.fork == f) & (st.team_abbr == "MIN")].exp_2026_27.iloc[0])
                   for f in FORKS}
            hb = {f: float(st[(st.fork == f) & (st.team_abbr == "MIN")].hot_baseline.iloc[0])
                  for f in FORKS}
            vals = {f: {} for f in FORKS}
            for c in coals:
                mp = alloc(roster_for(c, always, remove, add, weights), curve)
                for f in FORKS:
                    g = fc[fc.fork == f]
                    net = exp[f] + beta * (A.rollup(mp, imps[f], "rs")["net"] - hb[f])
                    vals[f][c] = float(np.interp(net, g.min_net, g.title))
            n = len(moves)
            w = [factorial(k) * factorial(n - k - 1) / factorial(n) for k in range(n)]
            out = []
            for f in FORKS:
                v = vals[f]
                for mv in moves:
                    others = [m for m in moves if m != mv]
                    phi = sum(w[k] * (v[frozenset(s) | {mv}] - v[frozenset(s)])
                              for k in range(n) for s in itertools.combinations(others, k))
                    out.append(dict(fork=f, move=mv, shapley_pp=100 * phi))
            vall = {f: 100 * vals[f][frozenset(moves)] for f in FORKS}
            vnone = {f: 100 * vals[f][frozenset()] for f in FORKS}
            return pd.DataFrame(out), vall, vnone

        # G3: the fixed grand coalition is the simulated current roster
        cur_ids = set(pool[(pool.scenario == "current") & (pool.team_abbr == "MIN")]
                      .player_id.astype(int))
        grand = roster_for(frozenset(SH.MOVES), AFTER, SH.REMOVE_WHEN_APPLIED,
                           SH.ADD_WHEN_APPLIED)
        g_ids = set(grand.player_id.astype(int))
        pub_ids = set(roster_for(frozenset(SH.MOVES), BEFORE, SH.REMOVE_WHEN_APPLIED,
                                 SH.ADD_WHEN_APPLIED, False).player_id.astype(int))
        r.note("G3: simulated current roster %d players; pre-D85 grand coalition %d "
               "(missing %s); post-D85 grand coalition %d, identical: %s"
               % (len(cur_ids), len(pub_ids), sorted(cur_ids - pub_ids), len(g_ids),
                  g_ids == cur_ids))
        if g_ids != cur_ids:
            raise RuntimeError("G3 failed: post-D85 grand coalition is not the current roster")

        split_remove = {m: p for m, p in SH.REMOVE_WHEN_APPLIED.items() if m != "other_departures"}
        split_remove.update({"dep:%s" % n: [n] for n in DEPARTURES})
        split_moves = [m for m in SH.MOVES if m != "other_departures"] + \
            ["dep:%s" % n for n in DEPARTURES]

        rows, vrows = [], []
        floors = {}
        PRE = os.path.join(OUT_DIR, "pre_d85")
        for basis, cfg in BASES.items():
            os.environ["KUMINGA_AGING"] = cfg["aging"]
            imps, _ = build_impacts(value, darko, bio)
            st = pd.read_csv(cfg["strengths"])
            fc = pd.read_csv(cfg["fcurve"])
            sim = pd.read_csv(cfg["sim"])
            direct = sim[sim.team_abbr == "MIN"].set_index("fork").title_current * 100
            fl = floors_for(fc, st)
            floors[basis] = fl
            sub = "aged" if basis == "aged" else ""
            # `strict` marks a reference that MUST reproduce. The pre-D85 tables were priced
            # on the impact spine of that day; D89 refit RAPM, so they are a historical record
            # and their difference is reported rather than enforced. The current tables still
            # have to reproduce exactly, which is what checks this script against the pipeline.
            versions = [
                # name, ALWAYS list, mover weights, allocator, published table, floor table, strict
                ("before_d85", BEFORE, False, None,
                 os.path.join(PRE, sub, "shapley_min_POOLED.csv"),
                 os.path.join(PRE, sub, "noise_floor_AGED.csv" if sub else "noise_floor.csv"), False),
                ("williams_only", AFTER, False, None, None, None, False),
                ("after_d85", AFTER, True, None, cfg["shapley"], cfg["floor"], True),
                ("before_d85_teamrank", BEFORE, False, teamrank,
                 None if sub else os.path.join(PRE, "shapley_min.csv"), None, False),
                ("after_d85_teamrank", AFTER, True, teamrank,
                 os.path.join(OUT_DIR, sub, "shapley_min.csv"), None, True),
            ]
            for version, always, wts, alloc, ref, ref_floor, strict in versions:
                sh, vall, vnone = game(SH.MOVES, always, SH.REMOVE_WHEN_APPLIED,
                                       SH.ADD_WHEN_APPLIED, imps, st, fc, alloc=alloc,
                                       weights=wts)
                if version == "after_d85_teamrank":
                    worst = max(abs(vall[f] - float(direct[f])) for f in FORKS)
                    r.note("G4 %s: post-D85 team-rank grand coalition against the direct "
                           "simulation, worst view %.3f pp (interpolation only)" % (basis, worst))
                if ref:
                    pubtab = pd.read_csv(ref, index_col=0)
                    gap = max(abs(float(pubtab.loc[x.move, x.fork]) - x.shapley_pp)
                              for _, x in sh.iterrows())
                    msg = "G1 %s %s: %s %s to %.2e pp" % (
                        basis, version, "reproduces" if strict else "differs from",
                        os.path.relpath(ref, OUT_DIR), gap)
                    if gap > 1e-6:
                        if strict:
                            raise RuntimeError("G1 failed: " + msg)
                        msg += " (expected: that table was priced before the D89 impact refit; "\
                               "the D85 before/after record stands in decisions.md)"
                    if strict and ref_floor:
                        pubf = pd.read_csv(ref_floor).set_index("move")
                        bad = [mv for mv in SH.MOVES
                               if sum(abs(float(pubtab.loc[mv, f])) >= fl[f] for f in FORKS)
                               != int(pubf.loc[mv, "n_forks_clearing"])]
                        msg += "; G2 clearing counts match %s: %s" % (
                            os.path.relpath(ref_floor, OUT_DIR), "yes" if not bad else "NO %s" % bad)
                        if bad:
                            raise RuntimeError("G2 failed: " + msg)
                    r.note(msg)
                sh["basis"], sh["version"], sh["game"] = basis, version, "eight moves"
                rows.append(sh)
                for f in FORKS:
                    vrows.append(dict(basis=basis, version=version, fork=f, v_all=vall[f],
                                      v_none=vnone[f], direct_sim=float(direct[f]),
                                      v_all_minus_direct=vall[f] - float(direct[f])))
                r.note("%s %-20s v(all) %s | direct sim %s"
                       % (basis, version, " ".join("%.2f" % vall[f] for f in FORKS),
                          " ".join("%.2f" % direct[f] for f in FORKS)))
            sp, _, _ = game(split_moves, AFTER, split_remove, SH.ADD_WHEN_APPLIED,
                            imps, st, fc)
            sp["basis"], sp["version"], sp["game"] = basis, "after_d85", "split departures"
            rows.append(sp)

        S = pd.concat(rows, ignore_index=True)
        S.to_csv(OUT, index=False)
        pd.DataFrame(vrows).to_csv(OUT_ALL, index=False)

        piv = S.pivot_table(index=["game", "version", "basis", "move"], columns="fork",
                            values="shapley_pp").reset_index()
        piv["mean_pp"] = piv[FORKS].mean(axis=1)
        piv["sign"] = piv[FORKS].apply(sign_of, axis=1)
        piv["n_clear"] = piv.apply(lambda x: sum(abs(x[f]) >= floors[x.basis][f] for f in FORKS), axis=1)
        piv["min_margin"] = piv.apply(lambda x: min(abs(x[f]) - floors[x.basis][f] for f in FORKS), axis=1)
        piv["clears_all"] = (piv.sign != "MIXED") & (piv.n_clear == 4)
        wide = piv.pivot_table(index=["game", "version", "move"], columns="basis",
                               values=["mean_pp", "sign", "n_clear", "clears_all", "min_margin"],
                               aggfunc="first")
        wide.columns = ["%s_%s" % (a, b) for a, b in wide.columns]
        wide = wide.reset_index()
        wide["ships"] = (wide.clears_all_unaged.astype(bool) & wide.clears_all_aged.astype(bool)
                         & (wide.sign_unaged == wide.sign_aged))
        wide.to_csv(OUT_V, index=False)

        for gm in ("eight moves", "split departures"):
            for version in ("before_d85", "williams_only", "after_d85",
                            "before_d85_teamrank", "after_d85_teamrank"):
                sub = wide[(wide.game == gm) & (wide.version == version)]
                if sub.empty:
                    continue
                r.note("")
                r.note("%s, %s: mean pp un-aged / aged, sign, views clearing, thinnest margin, ships"
                       % (gm.upper(), version))
                for _, x in sub.sort_values("mean_pp_unaged", ascending=False).iterrows():
                    r.note("  %-26s %+.3f / %+.3f  %-12s / %-12s  %d/4, %d/4  %+.3f / %+.3f  %s"
                           % (x.move, x.mean_pp_unaged, x.mean_pp_aged, x.sign_unaged, x.sign_aged,
                              x.n_clear_unaged, x.n_clear_aged, x.min_margin_unaged,
                              x.min_margin_aged, "SHIPS" if x.ships else "no"))
        r.output(OUT, rows=len(S))
        r.output(OUT_V, rows=len(wide))
        r.output(OUT_ALL)


if __name__ == "__main__":
    main()
