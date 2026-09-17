#!/usr/bin/env python3
"""R2: what is inside "other departures", and is the verdict carried by one of them?

`other_departures` is a shipping verdict (ALL POSITIVE on both aging bases, clearing every
view's floor). It is also a bundle of seven players, and a bundle can ship on the back of
one member. This names the seven and splits them.

PART 1, DESCRIPTIVE. For each departing player: 2025-26 Minnesota minutes (observed), the
impact the model carries for him in each view on both bases and where that impact comes
from, the minutes the pooled allocator gives him if he had stayed and everything else
happened, and who absorbs those minutes when he goes.

PART 2, THE SPLIT. The pooled Shapley decomposition re-run with the bundle broken into its
seven members (14 moves, 16,384 coalitions, exact), on both aging bases, and every member
re-tested against the same per-view noise floor the shipping list uses.

GATES, fatal:
  G1  with the ORIGINAL eight moves this script reproduces `shapley_min_POOLED.csv` on
      both bases (so the split is the published machinery, not a re-implementation of it)
  G2  the per-view floors reproduce the published floor tables' clearing counts on both
      bases

    python kuminga/scripts/r2_departures.py
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
sys.path.insert(0, os.path.join(REPO, "postmortem"))
sys.path.insert(0, HERE)
sys.argv = [sys.argv[0], "--pooled"] + [a for a in sys.argv[1:] if a != "--pooled"]

import shapley as SH                       # noqa: E402  (module constants, pooled mode)
import build_team_ratings as A             # noqa: E402
import bracket_sim as E                    # noqa: E402
from build_strengths import build_impacts  # noqa: E402
from kuminga.lib import kfreeze, runlog    # noqa: E402
from lib import db                         # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
OUT_P = os.path.join(OUT_DIR, "r2_departures_players.csv")
OUT_S = os.path.join(OUT_DIR, "r2_departures_split_shapley.csv")
OUT_A = os.path.join(OUT_DIR, "r2_departures_absorbers.csv")
FORKS = SH.FORKS
DEPARTURES = SH.REMOVE_WHEN_APPLIED["other_departures"]
BASES = {
    "unaged": dict(strengths=os.path.join(OUT_DIR, "team_strengths_2026_27.csv"),
                   fcurve=os.path.join(OUT_DIR, "fcurve_min.csv"),
                   shapley=os.path.join(OUT_DIR, "shapley_min_POOLED.csv"),
                   floor=os.path.join(OUT_DIR, "noise_floor.csv"), aging="0"),
    "aged": dict(strengths=os.path.join(OUT_DIR, "aged", "team_strengths_2026_27.csv"),
                 fcurve=os.path.join(OUT_DIR, "aged", "fcurve_min.csv"),
                 shapley=os.path.join(OUT_DIR, "aged", "shapley_min_POOLED.csv"),
                 floor=os.path.join(OUT_DIR, "aged", "noise_floor_AGED.csv"), aging="1"),
}


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
        interp = (h ** 2) / 8.0 * f2 * 100
        out[f] = 2.0 * float(np.hypot(mc, interp)) * np.sqrt(2)
    return out


def main():
    with runlog.run("r2_departures", inputs={"departures": DEPARTURES,
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

        def roster_for(coal, remove, add):
            names = list(SH.ALWAYS)
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
            k = SH.nkey("Donte DiVincenzo")
            a = attrs.loc[k]
            rows.append(dict(player_id=a.player_id, player_name="Donte DiVincenzo",
                             consensus_net=a.consensus_net, prior_mpg=a.prior_mpg,
                             rank_score=a.rank_score, pool=a.get("pool", "guard"),
                             rs_avail=0.0 if "ddv_injury" in coal else 1.0))
            return pd.DataFrame(rows)

        def shapley(moves, remove, add, imps, st, fc):
            coals = [frozenset(c) for k in range(len(moves) + 1)
                     for c in itertools.combinations(moves, k)]
            exp = {f: float(st[(st.fork == f) & (st.team_abbr == "MIN")].exp_2026_27.iloc[0])
                   for f in FORKS}
            hb = {f: float(st[(st.fork == f) & (st.team_abbr == "MIN")].hot_baseline.iloc[0])
                  for f in FORKS}
            curves = {f: fc[fc.fork == f] for f in FORKS}
            vals = {f: {} for f in FORKS}
            mins = {}
            for c in coals:
                mp = SH.allocate(roster_for(c, remove, add), curve)
                mins[c] = mp
                for f in FORKS:
                    net = exp[f] + beta * (A.rollup(mp, imps[f], "rs")["net"] - hb[f])
                    vals[f][c] = float(np.interp(net, curves[f].min_net, curves[f].title))
            n = len(moves)
            w = [factorial(k) * factorial(n - k - 1) / factorial(n) for k in range(n)]
            out = []
            for f in FORKS:
                v = vals[f]
                for mv in moves:
                    others = [m for m in moves if m != mv]
                    phi = 0.0
                    for k in range(n):
                        for sub in itertools.combinations(others, k):
                            S = frozenset(sub)
                            phi += w[k] * (v[S | {mv}] - v[S])
                    out.append(dict(fork=f, move=mv, shapley_pp=100 * phi))
            return pd.DataFrame(out), mins

        split_remove = {m: p for m, p in SH.REMOVE_WHEN_APPLIED.items()
                        if m != "other_departures"}
        split_remove.update({"dep:%s" % n: [n] for n in DEPARTURES})
        split_moves = [m for m in SH.MOVES if m != "other_departures"] + \
            ["dep:%s" % n for n in DEPARTURES]

        res, floors_all, desc = [], {}, []
        imps_by = {}
        for basis, cfg in BASES.items():
            os.environ["KUMINGA_AGING"] = cfg["aging"]
            imps, _ = build_impacts(value, darko, bio)
            imps_by[basis] = imps
            st = pd.read_csv(cfg["strengths"])
            fc = pd.read_csv(cfg["fcurve"])

            # G1: the original eight moves reproduce the published table
            orig, mins8 = shapley(SH.MOVES, SH.REMOVE_WHEN_APPLIED, SH.ADD_WHEN_APPLIED,
                                  imps, st, fc)
            pub = pd.read_csv(cfg["shapley"], index_col=0)
            gap = max(abs(float(pub.loc[x.move, x.fork]) - x.shapley_pp)
                      for _, x in orig.iterrows())
            r.note("G1 %s: reproduces shapley_min_POOLED to %.2e pp" % (basis, gap))
            if gap > 1e-6:
                raise RuntimeError("G1 failed on %s" % basis)

            # G2: floors reproduce the published clearing counts
            fl = floors_for(fc, st)
            floors_all[basis] = fl
            pubf = pd.read_csv(cfg["floor"]).set_index("move")
            bad = []
            for mv in SH.MOVES:
                n_clear = sum(abs(float(pub.loc[mv, f])) >= fl[f] for f in FORKS)
                if n_clear != int(pubf.loc[mv, "n_forks_clearing"]):
                    bad.append(mv)
            r.note("G2 %s: floors %s | clearing counts match the published table: %s"
                   % (basis, ", ".join("%s %.3f" % (f, fl[f]) for f in FORKS),
                      "yes" if not bad else "NO %s" % bad))
            if bad:
                raise RuntimeError("G2 failed on %s" % basis)

            # the split
            sp, _ = shapley(split_moves, split_remove, SH.ADD_WHEN_APPLIED, imps, st, fc)
            sp["basis"] = basis
            res.append(sp)
            bundle = orig[orig.move == "other_departures"].set_index("fork").shapley_pp
            r.note("%s bundle: %s | members summed: %s"
                   % (basis, ", ".join("%s %+.3f" % (f, bundle[f]) for f in FORKS),
                      ", ".join("%s %+.3f" % (f, sp[(sp.fork == f) & sp.move.str.startswith(
                          "dep:")].shapley_pp.sum()) for f in FORKS)))

            # descriptive: minutes if they had stayed, and who absorbs them
            full = frozenset(SH.MOVES)
            stay = full - {"other_departures"}
            m_full, m_stay = mins8[full], mins8[stay]
            names = dict(zip(attrs.player_id.dropna().astype(int).astype(str),
                             attrs.player_name))
            if basis == "unaged":
                for pid in set(m_full) | set(m_stay):
                    d = m_full.get(pid, 0.0) - m_stay.get(pid, 0.0)
                    if abs(d) > 1e-6:
                        desc.append(dict(player=names.get(pid, pid), player_id=pid,
                                         mpg_if_departures_stayed=m_stay.get(pid, 0.0),
                                         mpg_actual_moves=m_full.get(pid, 0.0), change=d))

        S = pd.concat(res, ignore_index=True)
        piv = S.pivot_table(index=["basis", "move"], columns="fork",
                            values="shapley_pp").reset_index()
        piv["mean_pp"] = piv[FORKS].mean(axis=1)
        piv["sign"] = piv[FORKS].apply(lambda x: "ALL POSITIVE" if (x > 0).all() else
                                       "ALL NEGATIVE" if (x < 0).all() else "MIXED", axis=1)
        piv["n_clear"] = piv.apply(lambda x: sum(abs(x[f]) >= floors_all[x.basis][f]
                                                 for f in FORKS), axis=1)
        piv["clears_all"] = (piv.sign != "MIXED") & (piv.n_clear == 4)
        wide = piv.pivot(index="move", columns="basis",
                         values=["mean_pp", "sign", "n_clear", "clears_all"])
        wide.columns = ["%s_%s" % (a, b) for a, b in wide.columns]
        wide["ships"] = wide.clears_all_unaged.astype(bool) & wide.clears_all_aged.astype(bool) \
            & (wide.sign_unaged == wide.sign_aged)
        wide = wide.reset_index()
        piv.to_csv(OUT_S, index=False)
        r.note("")
        r.note("SPLIT SHAPLEY, mean pp un-aged / aged, sign, views clearing, ships:")
        for _, x in wide.sort_values("mean_pp_unaged", ascending=False).iterrows():
            r.note("  %-26s %+.3f / %+.3f  %-12s / %-12s  %d/4, %d/4  %s"
                   % (x.move, x.mean_pp_unaged, x.mean_pp_aged, x.sign_unaged, x.sign_aged,
                      x.n_clear_unaged, x.n_clear_aged, "SHIPS" if x.ships else "no"))
        wide.to_csv(OUT_S.replace(".csv", "_verdicts.csv"), index=False)

        # ---- per-player descriptive table ---------------------------------------------
        obs = db.query("""
            select person_id::bigint pid, count(distinct game_id) g, sum(minutes_float) mins
            from nba.nba_player_advanced_stats
            where game_id like '00225%%' and team_tricode = 'MIN' and minutes_float > 0
            group by 1
        """)
        obs = obs.set_index("pid")
        src = pool[pool.team_abbr == "MIN"].drop_duplicates("player_name").set_index(
            "player_name")
        rows = []
        for n in DEPARTURES:
            a = attrs.loc[SH.nkey(n)]
            pid = str(int(a.player_id))
            row = dict(player=n, player_id=pid, pool=a.get("pool"),
                       impact_source=src.loc[n, "impact_source"] if n in src.index else None,
                       mpg_source=src.loc[n, "mpg_source"] if n in src.index else None,
                       prior_mpg=float(a.prior_mpg),
                       games_min_2025_26=int(obs.g.get(int(pid), 0)),
                       mpg_min_2025_26=float(obs.mins.get(int(pid), 0.0) /
                                             max(obs.g.get(int(pid), 1), 1)))
            for basis in BASES:
                for f in FORKS:
                    d = imps_by[basis][f].get(pid)
                    row["impact_%s_%s" % (f, basis)] = (d["off"] - d["def"]) if d else np.nan
            rows.append(row)
        P = pd.DataFrame(rows)
        P.to_csv(OUT_P, index=False)
        D = pd.DataFrame(desc).sort_values("change")
        D.to_csv(OUT_A, index=False)
        r.note("")
        r.note("DEPARTING PLAYERS (impact un-aged: consensus/rapm/box/darko):")
        for _, x in P.iterrows():
            r.note("  %-16s %-8s source %-14s prior %.1f | MIN 2025-26 %d g, %.1f mpg | "
                   "%s" % (x.player, x.pool, x.impact_source, x.prior_mpg, x.games_min_2025_26,
                           x.mpg_min_2025_26, " / ".join(
                               "%+.2f" % x["impact_%s_unaged" % f] for f in FORKS)))
        r.note("MINUTES if the seven had stayed vs the actual moves (un-aged, pooled):")
        for _, x in D.iterrows():
            r.note("  %-22s %5.1f -> %5.1f  (%+.1f)" % (x.player, x.mpg_if_departures_stayed,
                                                      x.mpg_actual_moves, x.change))
        r.output(OUT_P, rows=len(P))
        r.output(OUT_S, rows=len(piv))
        r.output(OUT_A, rows=len(D))


if __name__ == "__main__":
    main()
