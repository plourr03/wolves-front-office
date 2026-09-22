#!/usr/bin/env python3
"""C3: Ball's games. Minnesota's title odds and P(top six) with LaMelo Ball available for
50, 60, 70 and 82 regular-season games, the playoffs at full strength, on both aging bases.

THE SCENARIO. Ball's regular-season availability is set to games/82. The playoffs are
untouched: he is there in April at full strength. That is the question the piece asks,
what a Ball season of the kind Charlotte lived through does to the seed, and through
the seed to the title.
  1. MINUTES. The pool row for Ball carries rs_avail = games/82 and Minnesota's 240
     minutes are re-allocated by the SAME allocator the pipeline uses
     (`rotation.allocate`, ceiling rule on), so his lost minutes cascade to the next men
     up to their own ceilings. This is the pipeline's own availability convention (the
     injuries table works the same way): a fraction of every game, not all of some games,
     which is the same thing in expectation for a linear minutes-weighted rollup.
  2. STRENGTH. The regular-season net moves by the pipeline's own formula: beta times the
     change in the minutes-weighted impact rollup, in each of the four views.
  3. TITLE ODDS. The league simulation, run with seeding (simulated wins) from the
     reduced regular-season net and the playoff series from the full-strength net. That
     is n5's playoff-only simulator with the two roles swapped: n5 reduced the playoffs
     and kept the seed; this reduces the seed and keeps the playoffs. Every availability
     is paired with the 82-game state on the SAME random seeds (common random numbers).
  4. P(TOP SIX). The share of simulated seasons in which Minnesota's simulated wins rank
     sixth or better among the fifteen West teams, the engine's own seeding rule, the
     one `seed_distribution.py` isolates.
GATES, each fatal if it fails:
  G1  the un-aged snapshot strengths equal `outputs/preaging/`
  G2  the allocator reproduces the published Minnesota rotation minutes
  G3  the pricing formula reproduces the published Minnesota net in every view
  G4  the simulator here reproduces `n5_fragility.sim_playoff_only` draw for draw, both
      with nothing changed and with the 50-game state (the only change here is the seed
      tally, which consumes no randomness)
  G5  at 82 games the mean-of-views title odds sit within 0.15 points of the sheet's
      headline for the basis (the C1 f-curve tolerance), and P(top six) within one point
      of `seed_distribution.csv` (a different seed and draw count, so MC noise only)
LIMITS stated up front. Minnesota's variance terms (method uncertainty, net sd) are held
at full-roster values. Nothing else on the roster changes with Ball's availability: the
rest of the rotation is as published, DiVincenzo out. Un-aged basis by default; `--aged`
repeats it on the survivorship-corrected aged basis.

    python kuminga/scripts/c3_ball_availability.py [--aged] [--nsims N]
"""
from __future__ import annotations

import argparse
import copy
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))
sys.path.insert(0, HERE)

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
SNAP = os.path.join(OUT_DIR, "_restore_unaged")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
SHEET = os.path.join(OUT_DIR, "final_numbers.csv")

TEAM = "MIN"
BALL = 1630163
GAMES = [50, 60, 70, 82]
FORKS = ["consensus", "rapm", "box", "darko"]
SEEDS = [11, 12, 13]
NSIMS = 50_000
HEADLINE_TOL = 0.15      # points of title odds, the C1 f-curve tolerance
TOP6_TOL = 1.0           # points, seed_distribution.csv used another seed and 100k draws


def sim_rs_scaled(strengths, po_net, n_sims, seed):
    """`n5_fragility.sim_playoff_only` line for line (itself `simulate_league` with the
    playoff draw taken from `po_net` where given), plus a tally of the seed the engine
    hands Minnesota. Seeding uses strengths[t]["net"], the playoff draw po_net where
    given. The random draws are consumed in the same order, so runs on the same seed are
    paired with n5's function and with each other. G4 checks the equality."""
    import bracket_sim as E
    import series_resolver as D
    p = E.load_e_params()
    rng = np.random.default_rng(seed)
    teams = list(strengths)
    base_net = np.array([strengths[t]["net"] for t in teams])
    po_base = np.array([po_net.get(t, strengths[t]["net"]) for t in teams])
    munc = np.array([strengths[t].get("munc", 0.0) for t in teams])
    sd = np.array([strengths[t].get("net_sd", 0.0) for t in teams])
    conf = {t: strengths[t]["conf"] for t in teams}
    sigma_t = np.sqrt(p["sigma_unobs"] ** 2 + (E.MUNC_W * munc) ** 2 + (0.15 * sd) ** 2)
    sig_rec = p["sigma_record"]
    wa, wb = p["wins_a"], p["wins_b"]
    idx = {t: i for i, t in enumerate(teams)}
    title = {t: 0 for t in teams}
    confwin = {t: 0 for t in teams}
    reach = {t: {2: 0, 3: 0, 4: 0} for t in teams}
    seed_hist = np.zeros(16, dtype=np.int64)     # index 1..15, Minnesota's West rank

    def resolve(hi, lo, dnet):
        pr = D.series_win_prob(dnet[hi], dnet[lo], True, None, None)
        win_hi = rng.random() < pr
        return hi if win_hi else lo

    for _ in range(n_sims):
        eps = rng.normal(0.0, sigma_t)
        dnet = {t: po_base[idx[t]] + eps[idx[t]] for t in teams}
        sim_wins = {t: wa + wb * base_net[idx[t]] + rng.normal(0.0, sig_rec) for t in teams}
        seeds_by_conf = {}
        for c in ("E", "W"):
            ct = sorted([t for t in teams if conf[t] == c], key=lambda t: -sim_wins[t])
            if c == "W":
                seed_hist[ct.index(TEAM) + 1] += 1
            seeds_by_conf[c] = ct[:8]
        r1 = E._seed_bracket(seeds_by_conf)
        conf_champs = {}
        for c in ("E", "W"):
            (a1, a8), (a4, a5), (a3, a6), (a2, a7) = r1[c]
            w18 = resolve(a1, a8, dnet); w45 = resolve(a4, a5, dnet)
            w36 = resolve(a3, a6, dnet); w27 = resolve(a2, a7, dnet)
            for t in (w18, w45, w36, w27):
                reach[t][2] += 1

            def host(x, y):
                return (x, y) if sim_wins[x] >= sim_wins[y] else (y, x)
            sf1 = resolve(*host(w18, w45), dnet)
            sf2 = resolve(*host(w27, w36), dnet)
            for t in (sf1, sf2):
                reach[t][3] += 1
            cf = resolve(*host(sf1, sf2), dnet)
            reach[cf][4] += 1
            conf_champs[c] = cf
            confwin[cf] += 1
        ce, cw = conf_champs["E"], conf_champs["W"]
        champ = resolve(*((ce, cw) if sim_wins[ce] >= sim_wins[cw] else (cw, ce)), dnet)
        title[champ] += 1
    out = {t: dict(title=title[t] / n_sims, conf=confwin[t] / n_sims,
                   r2=reach[t][2] / n_sims, cf=reach[t][3] / n_sims,
                   finals=reach[t][4] / n_sims) for t in teams}
    out[TEAM]["top6"] = float(seed_hist[1:7].sum()) / n_sims
    out[TEAM]["top4"] = float(seed_hist[1:5].sum()) / n_sims
    out[TEAM]["playin_7_10"] = float(seed_hist[7:11].sum()) / n_sims
    out[TEAM]["miss_11plus"] = float(seed_hist[11:].sum()) / n_sims
    out[TEAM]["mean_seed"] = float((seed_hist * np.arange(16)).sum()) / n_sims
    return out


def run_state(args):
    fork, games, strengths, po_net, nsims = args
    acc = None
    for s in SEEDS:
        res = sim_rs_scaled(strengths, po_net, nsims, s)[TEAM]
        if acc is None:
            acc = {k: [v] for k, v in res.items()}
        else:
            for k, v in res.items():
                acc[k].append(v)
    out = {k: float(np.mean(v)) for k, v in acc.items()}
    out["title_seeds"] = list(acc["title"])
    out["top6_seeds"] = list(acc["top6"])
    return fork, games, out


def main():
    from kuminga.lib import kfreeze, rotation, runlog
    import build_team_ratings as A
    import bracket_sim as E
    from build_strengths import build_impacts, add_rookie_impacts
    import n5_fragility as N5

    ap = argparse.ArgumentParser()
    ap.add_argument("--aged", action="store_true")
    ap.add_argument("--nsims", type=int, default=NSIMS)
    args = ap.parse_args()
    basis = "aged" if args.aged else "unaged"
    src = os.path.join(OUT_DIR, "aged") if args.aged else SNAP
    sfx = "_AGED" if args.aged else ""
    OUT = os.path.join(OUT_DIR, "c3_ball_availability%s.csv" % sfx)
    OUT_MIN = os.path.join(OUT_DIR, "c3_ball_minutes%s.csv" % sfx)

    with runlog.run("c3_ball_availability", inputs={"basis": basis, "source": src,
                                                     "games": GAMES, "seeds": SEEDS,
                                                     "nsims": args.nsims}) as r:
        if "KUMINGA_AGING" in os.environ and not args.aged:
            raise RuntimeError("KUMINGA_AGING is set in this shell; the un-aged run "
                               "must not see it")
        st = pd.read_csv(os.path.join(src, "team_strengths_2026_27.csv"))
        pool = pd.read_csv(os.path.join(SNAP, "player_pool_2026_27.csv"))
        rot = pd.read_csv(os.path.join(SNAP, "rotations_2026_27.csv"))
        curve = pd.read_csv(os.path.join(SNAP, "minutes_rank_curve.csv"),
                            index_col=0).iloc[:, 0]
        sheet = pd.read_csv(SHEET, dtype=str).set_index("key")

        # G1
        if not args.aged:
            pre = pd.read_csv(os.path.join(OUT_DIR, "preaging", "team_strengths_2026_27.csv"))
            g1 = st.merge(pre, on=["fork", "team_abbr"], suffixes=("", "_p"))
            gap = float((g1.net_current - g1.net_current_p).abs().max())
            r.note("G1 snapshot strengths vs preaging: max abs diff %.2e" % gap)
            if gap > 1e-9:
                raise RuntimeError("G1 failed")

        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        if args.aged:
            os.environ["KUMINGA_AGING"] = "1"      # build_impacts ages itself (see n5)
        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, rot)
        beta = float(E.load_e_params()["beta"])

        # G2
        g = pool[(pool.scenario == "current") & (pool.team_abbr == TEAM)].copy()
        assert (g.player_id == BALL).sum() == 1, "Ball not on the Minnesota pool exactly once"
        assert float(g.loc[g.player_id == BALL, "rs_avail"].iloc[0]) == 1.0, \
            "Ball's published availability is not 1.0; the 82-game state would not be the headline"
        mp_full = rotation.allocate(g, curve, use_ceiling=True)
        pub = rot[(rot.scenario == "current") & (rot.team_abbr == TEAM)]
        pub = {str(int(x.player_id)): float(x.mpg) for _, x in pub.iterrows()
               if pd.notna(x.player_id) and x.mpg > 0}
        d2 = max(abs(mp_full.get(k, 0.0) - pub.get(k, 0.0)) for k in set(mp_full) | set(pub))
        r.note("G2 allocator vs published Minnesota rotation: max abs minutes diff %.2e" % d2)
        if d2 > 1e-6:
            raise RuntimeError("G2 failed")
        named = pool[pool.player_id.notna()]
        pnames = dict(zip(named.player_id.astype(int).astype(str), named.player_name))

        # G3
        g3 = 0.0
        full_net = {}
        for f in FORKS:
            row = st[(st.fork == f) & (st.team_abbr == TEAM)].iloc[0]
            net = row.exp_2026_27 + beta * (A.rollup(pub, imps[f], "rs")["net"] - row.hot_baseline)
            g3 = max(g3, abs(net - row.net_current))
            full_net[f] = float(row.net_current)
        r.note("G3 pricing formula vs published Minnesota net, 4 views: max abs diff %.2e" % g3)
        if g3 > 1e-6:
            raise RuntimeError("G3 failed")

        def strengths_for(f):
            s = st[st.fork == f]
            return {x.team_abbr: {"net": float(x.net_current), "net_sd": float(x.net_sd),
                                  "munc": float(x.munc), "conf": x.conf, "profile": None}
                    for _, x in s.iterrows()}

        # ---- minutes and regular-season strength at each availability ---------------
        rs_net, min_rows = {}, []
        for games in GAMES:
            a = games / 82.0
            gg = g.copy()
            gg.loc[gg.player_id == BALL, "rs_avail"] = a
            mp = rotation.allocate(gg, curve, use_ceiling=True)
            gained = {k: mp.get(k, 0.0) - mp_full.get(k, 0.0) for k in set(mp) | set(mp_full)}
            gained = {k: v for k, v in gained.items() if v > 1e-6}
            for f in FORKS:
                d_hot = A.rollup(mp, imps[f], "rs")["net"] - A.rollup(mp_full, imps[f], "rs")["net"]
                rs_net[(f, games)] = full_net[f] + beta * d_hot
                min_rows.append(dict(
                    basis=basis, games=games, rs_avail=round(a, 4), fork=f,
                    ball_mpg_full=mp_full.get(str(BALL), 0.0), ball_mpg=mp.get(str(BALL), 0.0),
                    minutes_redistributed=sum(gained.values()),
                    net_full=full_net[f], net_rs=rs_net[(f, games)],
                    net_drop=full_net[f] - rs_net[(f, games)],
                    absorbers="; ".join("%s +%.1f" % (pnames.get(k, k), v) for k, v in
                                        sorted(gained.items(), key=lambda kv: -kv[1])[:4])))
            r.note("%d games: Ball %.1f -> %.1f mpg; net drop by view %s" % (
                games, mp_full.get(str(BALL), 0.0), mp.get(str(BALL), 0.0),
                ", ".join("%s %.2f" % (f, full_net[f] - rs_net[(f, games)]) for f in FORKS)))

        # G4: draw-for-draw equality with n5's simulator, nothing changed and 50 games
        s0 = strengths_for("consensus")
        a_ = N5.sim_playoff_only(copy.deepcopy(s0), {}, 2000, 7)
        b_ = sim_rs_scaled(copy.deepcopy(s0), {}, 2000, 7)
        g4 = max(abs(a_[t]["title"] - b_[t]["title"]) + abs(a_[t]["finals"] - b_[t]["finals"])
                 for t in s0)
        s1 = copy.deepcopy(s0)
        s1[TEAM]["net"] = rs_net[("consensus", 50)]
        a_ = N5.sim_playoff_only(copy.deepcopy(s1), {TEAM: full_net["consensus"]}, 2000, 7)
        b_ = sim_rs_scaled(copy.deepcopy(s1), {TEAM: full_net["consensus"]}, 2000, 7)
        g4 = max(g4, max(abs(a_[t]["title"] - b_[t]["title"]) + abs(a_[t]["finals"] - b_[t]["finals"])
                         for t in s0))
        r.note("G4 this simulator vs n5.sim_playoff_only, 2,000 sims x 2 states: max abs diff %.2e" % g4)
        if g4 > 0:
            raise RuntimeError("G4 failed")

        # ---- the simulations, paired on seeds ----------------------------------------
        jobs = []
        for f in FORKS:
            for games in GAMES:
                s = strengths_for(f)
                s[TEAM]["net"] = rs_net[(f, games)]
                jobs.append((f, games, s, {TEAM: full_net[f]}, args.nsims))
        r.note("simulating %d states x %d seeds x %s sims (common random numbers)"
               % (len(jobs), len(SEEDS), "{:,}".format(args.nsims)))
        with ProcessPoolExecutor(max_workers=4) as ex:
            res = {(f, games): out for f, games, out in ex.map(run_state, jobs)}

        rows = []
        for f in FORKS:
            b = res[(f, 82)]
            for games in GAMES:
                x = res[(f, games)]
                rows.append(dict(
                    basis=basis, games=games, fork=f,
                    title=100 * x["title"], title_82=100 * b["title"],
                    title_drop_pp=100 * (b["title"] - x["title"]),
                    title_drop_seed_se=100 * float(np.std(np.subtract(b["title_seeds"], x["title_seeds"]), ddof=1)
                                                   / np.sqrt(len(SEEDS))),
                    finals=100 * x["finals"], conf=100 * x["conf"],
                    top6=100 * x["top6"], top6_82=100 * b["top6"],
                    top6_drop_pp=100 * (b["top6"] - x["top6"]),
                    top6_drop_seed_se=100 * float(np.std(np.subtract(b["top6_seeds"], x["top6_seeds"]), ddof=1)
                                                  / np.sqrt(len(SEEDS))),
                    top4=100 * x["top4"], playin_7_10=100 * x["playin_7_10"],
                    miss_11plus=100 * x["miss_11plus"], mean_seed=x["mean_seed"],
                    net_rs=rs_net[(f, games)], net_full=full_net[f]))
        R = pd.DataFrame(rows)
        R.to_csv(OUT, index=False)
        pd.DataFrame(min_rows).to_csv(OUT_MIN, index=False)

        # G5: the 82-game state against the sheet and the seed distribution
        head_key = "title_aged" if args.aged else "title"
        head = float(sheet.loc[head_key, "value"].rstrip("%"))
        mine = float(R[R.games == 82].title.mean())
        r.note("G5 82-game title odds, mean of views: %.2f%% vs sheet %s %.2f%% (gap %.3fpp, tol %.2f)"
               % (mine, head_key, head, mine - head, HEADLINE_TOL))
        if abs(mine - head) > HEADLINE_TOL:
            raise RuntimeError("G5 failed: 82-game title odds off the headline")
        sd_path = os.path.join(src, "seed_distribution.csv")
        if os.path.exists(sd_path):
            sd = pd.read_csv(sd_path)
            sd = sd[(sd.field == "current") & (sd.team_abbr == TEAM)]
            for f in FORKS:
                ref = 100 * float(sd[sd.fork == f].p_playoff_top6.iloc[0])
                got = float(R[(R.games == 82) & (R.fork == f)].top6.iloc[0])
                r.note("G5 82-game P(top six) %s: %.2f%% vs seed_distribution.csv %.2f%% (gap %.2fpp)"
                       % (f, got, ref, got - ref))
                if abs(got - ref) > TOP6_TOL:
                    raise RuntimeError("G5 failed: P(top six) off the seed distribution for %s" % f)
        else:
            r.note("G5 P(top six) reference: no seed_distribution.csv beside the strengths (%s); skipped" % src)

        r.note("")
        r.note("BALL'S GAMES (%s basis): Minnesota title odds and P(top six) by Ball's regular-season games, "
               "mean of four views [band]" % basis)
        for games, d in R.groupby("games", sort=False):
            r.note("  %2d games | title %5.2f%% [%.2f, %.2f] (drop %.2fpp) | P(top six) %5.1f%% [%.1f, %.1f] "
                   "(drop %.1fpp) | mean seed %.2f | net drop %.2f"
                   % (games, d.title.mean(), d.title.min(), d.title.max(), d.title_drop_pp.mean(),
                      d.top6.mean(), d.top6.min(), d.top6.max(), d.top6_drop_pp.mean(),
                      d.mean_seed.mean(), (d.net_full - d.net_rs).mean()))
        r.output(OUT, rows=len(R))
        r.output(OUT_MIN, rows=len(min_rows))


if __name__ == "__main__":
    main()
