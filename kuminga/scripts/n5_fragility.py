#!/usr/bin/env python3
"""N5: fragility. What happens to Minnesota, Oklahoma City and San Antonio if one of their
top three players is out for the playoffs?

THE REMOVAL. For each team, each of its top three players is removed for the PLAYOFFS
ONLY. The regular season is untouched, so seeding comes from the full-strength roster,
and the playoff series are played at the reduced strength. That is the injury the
question describes: a player who helped earn the seed and is not there in April.

  1. MINUTES. The player's availability is set to zero and the team's 240 minutes are
     re-allocated by the SAME allocator the pipeline uses (`rotation.allocate`, ceiling
     rule on), so the minutes cascade to the next men up to their own ceilings.
  2. STRENGTH. The team's net moves by the pipeline's own formula: beta times the change
     in the minutes-weighted impact rollup, in each of the four views.
  3. TITLE ODDS. The league simulation, run with seeding from full-strength nets and the
     playoff series from the reduced net for that one team. Every removal is paired with
     a baseline run on the SAME random seeds (common random numbers), so the drop is the
     removal, not simulation noise.
  4. WEST RANK. The team's rank among the fifteen West teams by title probability.
  5. NEXT MAN UP. Who absorbs the minutes, and the minutes-weighted impact of the
     absorbed minutes against the impact of the player removed.

WHO IS "TOP THREE". By projected 2026-27 minutes, because that choice does not depend on
any one impact view and is what a rotation actually leans on. Where the top three by
consensus impact contribution (minutes times impact) differs, the extra player is run
too, as a sensitivity: Isaiah Hartenstein for Oklahoma City, Dylan Harper for San
Antonio. Minnesota's top three are the same by both definitions.

GATES, each fatal if it fails:
  G1  the un-aged snapshot strengths equal `outputs/preaging/`
  G2  the allocator reproduces the published rotation minutes for all three teams
  G3  the pricing formula reproduces the published net for every team and view
  G4  the playoff-only simulator, with no removal, reproduces `simulate_league` draw for
      draw

LIMITS stated up front. The team's playoff variance terms (method uncertainty, net sd)
are held at full-roster values. Minutes are the regular-season allocation with the player
removed; a playoff rotation shortens, which this does not model. Un-aged basis; `--aged`
repeats it on the survivorship-corrected aged basis once the chain has refreshed
`outputs/aged/`.

    python kuminga/scripts/n5_fragility.py [--aged]
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

TEAMS = ["MIN", "OKC", "SAS"]
FORKS = ["consensus", "rapm", "box", "darko"]
TOP_N = 3
SEEDS = [11, 12, 13]
NSIMS = 20000


def sim_playoff_only(strengths, po_net, n_sims, seed):
    """`bracket_sim.simulate_league`, line for line, with ONE change: seeding (simulated
    wins) uses the full-strength net, and the playoff draw uses `po_net` where given.
    The random draws are consumed in the same order, so runs on the same seed are paired.
    G4 checks that with po_net empty this reproduces the original exactly."""
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
    return {t: dict(title=title[t] / n_sims, conf=confwin[t] / n_sims,
                    r2=reach[t][2] / n_sims, cf=reach[t][3] / n_sims,
                    finals=reach[t][4] / n_sims) for t in teams}


def run_state(args):
    fork, label, strengths, po_net = args
    acc = None
    for s in SEEDS:
        res = sim_playoff_only(strengths, po_net, NSIMS, s)
        if acc is None:
            acc = {t: {k: [v] for k, v in d.items()} for t, d in res.items()}
        else:
            for t, d in res.items():
                for k, v in d.items():
                    acc[t][k].append(v)
    return fork, label, {t: dict({k: float(np.mean(v)) for k, v in d.items()},
                                 title_seeds=list(d["title"]))
                         for t, d in acc.items()}


def main():
    from kuminga.lib import kfreeze, rotation, runlog
    import build_team_ratings as A
    import bracket_sim as E
    from build_strengths import build_impacts, add_rookie_impacts

    ap = argparse.ArgumentParser()
    ap.add_argument("--aged", action="store_true")
    ap.add_argument("--doc-only", action="store_true",
                    help="rewrite the doc from the CSVs of the last completed run")
    args = ap.parse_args()
    basis = "aged" if args.aged else "unaged"
    src = os.path.join(OUT_DIR, "aged") if args.aged else SNAP
    sfx = "_AGED" if args.aged else ""
    OUT = os.path.join(OUT_DIR, "n5_fragility%s.csv" % sfx)
    OUT_NM = os.path.join(OUT_DIR, "n5_next_man_up%s.csv" % sfx)
    OUT_MD = os.path.join(REPO, "kuminga", "docs", "n5_fragility.md")

    if args.doc_only:
        with runlog.run("n5_fragility_doc", inputs={"from": [OUT, OUT_NM]}) as r:
            R = pd.read_csv(OUT)
            NM = pd.read_csv(OUT_NM)
            src_run = [x for x in open(os.path.join(REPO, "kuminga", "logs", "runs.jsonl"),
                                       encoding="utf-8")
                       if '"n5_fragility_2' in x and '"ok"' in x]
            r.note("doc rewritten from the CSVs of the last ok n5_fragility run")
            runs = [x.split('"run_id": "')[1].split('"')[0] for x in src_run]
            aged_f = os.path.join(OUT_DIR, "n5_fragility_AGED.csv")
            aged_nm = os.path.join(OUT_DIR, "n5_next_man_up_AGED.csv")
            aged = ((pd.read_csv(aged_f), pd.read_csv(aged_nm))
                    if os.path.exists(aged_f) and os.path.exists(aged_nm) else None)
            write_doc(r, R, NM, OUT_MD, sim_run=", ".join(runs[-2:]) if runs else "unknown",
                      aged=aged)
            r.output(OUT_MD)
        return

    with runlog.run("n5_fragility", inputs={"basis": basis, "source": src, "teams": TEAMS,
                                            "seeds": SEEDS, "nsims": NSIMS,
                                            "top_n": TOP_N}) as r:
        if "KUMINGA_AGING" in os.environ and not args.aged:
            raise RuntimeError("KUMINGA_AGING is set in this shell; the un-aged run "
                               "must not see it")
        st = pd.read_csv(os.path.join(src, "team_strengths_2026_27.csv"))
        pool = pd.read_csv(os.path.join(SNAP, "player_pool_2026_27.csv"))
        rot = pd.read_csv(os.path.join(SNAP, "rotations_2026_27.csv"))
        curve = pd.read_csv(os.path.join(SNAP, "minutes_rank_curve.csv"),
                            index_col=0).iloc[:, 0]

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
        # build_impacts applies aging ITSELF when KUMINGA_AGING=1, exactly as the aged
        # leg of the chain runs it. A first --aged run called apply_aging separately
        # without the variable set, aged nothing, and G3 caught it.
        if args.aged:
            os.environ["KUMINGA_AGING"] = "1"
        imps, _ = build_impacts(value, darko, bio)
        add_rookie_impacts(imps, rot)
        beta = float(E.load_e_params()["beta"])

        # G2 and G3
        cur_min = {}
        for t in TEAMS:
            g = pool[(pool.scenario == "current") & (pool.team_abbr == t)].copy()
            mp = rotation.allocate(g, curve, use_ceiling=True)
            pub = rot[(rot.scenario == "current") & (rot.team_abbr == t)]
            pub = {str(int(x.player_id)): float(x.mpg) for _, x in pub.iterrows()
                   if pd.notna(x.player_id) and x.mpg > 0}
            keys = set(mp) | set(pub)
            d2 = max(abs(mp.get(k, 0.0) - pub.get(k, 0.0)) for k in keys)
            r.note("G2 %s allocator vs published rotation: max abs minutes diff %.2e"
                   % (t, d2))
            if d2 > 1e-6:
                raise RuntimeError("G2 failed for %s" % t)
            cur_min[t] = pub
        g3 = 0.0
        for f in FORKS:
            for t in TEAMS:
                row = st[(st.fork == f) & (st.team_abbr == t)].iloc[0]
                net = row.exp_2026_27 + beta * (A.rollup(cur_min[t], imps[f], "rs")["net"]
                                                - row.hot_baseline)
                g3 = max(g3, abs(net - row.net_current))
        r.note("G3 pricing formula vs published net, 3 teams x 4 views: max abs diff %.2e"
               % g3)
        if g3 > 1e-6:
            raise RuntimeError("G3 failed")

        def strengths_for(f):
            s = st[st.fork == f]
            return {x.team_abbr: {"net": float(x.net_current), "net_sd": float(x.net_sd),
                                  "munc": float(x.munc), "conf": x.conf, "profile": None}
                    for _, x in s.iterrows()}

        # G4
        s0 = strengths_for("consensus")
        a_ = E.simulate_league(copy.deepcopy(s0), n_sims=3000, seed=99, use_overlay=False)
        b_ = sim_playoff_only(copy.deepcopy(s0), {}, 3000, 99)
        g4 = max(abs(a_["teams"][t]["title"] - b_[t]["title"]) for t in s0)
        r.note("G4 playoff-only simulator vs simulate_league, 3,000 sims, no removal: max "
               "abs title diff %.2e" % g4)
        if g4 > 0:
            raise RuntimeError("G4 failed")

        # ---- who is removed ---------------------------------------------------------
        removals = []
        for t in TEAMS:
            g = rot[(rot.scenario == "current") & (rot.team_abbr == t)].copy()
            g = g[g.player_id.notna() & (g.mpg > 0)]
            g["contrib"] = g.mpg / 48.0 * g.consensus_net
            by_min = list(g.sort_values("mpg", ascending=False).player_id.head(TOP_N))
            by_con = list(g.sort_values("contrib", ascending=False).player_id.head(TOP_N))
            names = dict(zip(g.player_id, g.player_name))
            for pid in by_min:
                removals.append((t, int(pid), names[pid], "top three by minutes"))
            for pid in by_con:
                if pid not in by_min:
                    removals.append((t, int(pid), names[pid],
                                     "sensitivity: top three by impact contribution"))
            r.note("%s top three by minutes: %s | by consensus contribution: %s"
                   % (t, ", ".join(names[p] for p in by_min),
                      ", ".join(names[p] for p in by_con)))

        # ---- minutes and strength for each removal --------------------------------------
        states, nm_rows = [], []
        for t, pid, pname, why in removals:
            g = pool[(pool.scenario == "current") & (pool.team_abbr == t)].copy()
            g.loc[g.player_id == pid, "rs_avail"] = 0.0
            mp = rotation.allocate(g, curve, use_ceiling=True)
            gained = {k: mp.get(k, 0.0) - cur_min[t].get(k, 0.0) for k in set(mp) |
                      set(cur_min[t])}
            gained = {k: v for k, v in gained.items() if v > 1e-6}
            lost_min = cur_min[t].get(str(pid), 0.0)
            # names must be built from the SAME filtered rows as the ids; zipping a
            # dropna'd id column against the unfiltered name column shifts every name
            # after the first missing id (caught on the first full run: Hartenstein was
            # listed as absorbing his own minutes)
            named = pool[pool.player_id.notna()]
            pnames = dict(zip(named.player_id.astype(int).astype(str), named.player_name))
            assert str(pid) not in gained, "a removed player cannot gain minutes"
            nets = {}
            for f in FORKS:
                row = st[(st.fork == f) & (st.team_abbr == t)].iloc[0]
                d_hot = (A.rollup(mp, imps[f], "rs")["net"]
                         - A.rollup(cur_min[t], imps[f], "rs")["net"])
                nets[f] = float(row.net_current + beta * d_hot)
                # sensitivity only: the pipeline's own playoff rollup (top nine by minutes,
                # rescaled to 240), so the removed player's minutes land on the players
                # already in the rotation instead of the eleventh and twelfth men
                d_po = (A.rollup(mp, imps[f], "playoff")["net"]
                        - A.rollup(cur_min[t], imps[f], "playoff")["net"])
                imp_p = imps[f].get(str(pid))
                p_net = (imp_p["off"] - imp_p["def"]) if imp_p else np.nan
                repl = [(k, v, imps[f][k]["off"] - imps[f][k]["def"])
                        for k, v in gained.items() if k in imps[f]]
                w = sum(v for _, v, _ in repl)
                repl_net = sum(v * n for _, v, n in repl) / w if w else np.nan
                top_abs = sorted(gained.items(), key=lambda kv: -kv[1])[:3]
                nm_rows.append(dict(
                    basis=basis, team=t, removed=pname, why=why, fork=f,
                    removed_mpg=lost_min, removed_net=p_net,
                    replacement_net=repl_net, replacement_gap=repl_net - p_net,
                    minutes_redistributed=sum(gained.values()),
                    team_net_full=float(row.net_current), team_net_removed=nets[f],
                    team_net_drop=float(row.net_current) - nets[f],
                    team_net_drop_playoff_rollup=float(-beta * d_po),
                    new_to_rotation="; ".join(
                        "%s +%.1f" % (pnames.get(k, k), v) for k, v in
                        sorted(gained.items(), key=lambda kv: -kv[1])
                        if cur_min[t].get(k, 0.0) <= 1e-9),
                    absorbers="; ".join("%s +%.1f" % (pnames.get(k, k), v)
                                        for k, v in top_abs)))
            states.append((t, pid, pname, why, nets))

        # ---- the simulations, paired on seeds -----------------------------------------------
        jobs = []
        for f in FORKS:
            s = strengths_for(f)
            jobs.append((f, "BASELINE", s, {}))
            for t, pid, pname, why, nets in states:
                jobs.append((f, "%s|%s" % (t, pname), s, {t: nets[f]}))
        r.note("simulating %d states x %d seeds x %s sims (common random numbers)"
               % (len(jobs), len(SEEDS), "{:,}".format(NSIMS)))
        with ProcessPoolExecutor(max_workers=6) as ex:
            res = {(f, lab): out for f, lab, out in ex.map(run_state, jobs)}

        def west_rank(out, team):
            w = sorted([x for x in out if st[st.team_abbr == x].conf.iloc[0] == "W"],
                       key=lambda x: -out[x]["title"])
            return w.index(team) + 1

        rows = []
        for t, pid, pname, why, nets in states:
            for f in FORKS:
                b = res[(f, "BASELINE")]
                x = res[(f, "%s|%s" % (t, pname))]
                rows.append(dict(
                    basis=basis, team=t, removed=pname, why=why, fork=f,
                    title_full=100 * b[t]["title"], title_removed=100 * x[t]["title"],
                    drop_pp=100 * (b[t]["title"] - x[t]["title"]),
                    drop_seed_se=100 * float(np.std(np.subtract(
                        b[t]["title_seeds"], x[t]["title_seeds"]), ddof=1)
                        / np.sqrt(len(SEEDS))),
                    drop_rel=(b[t]["title"] - x[t]["title"]) / b[t]["title"]
                    if b[t]["title"] else np.nan,
                    finals_full=100 * b[t]["finals"], finals_removed=100 * x[t]["finals"],
                    west_rank_full=west_rank(b, t), west_rank_removed=west_rank(x, t),
                    net_full=float(st[(st.fork == f) & (st.team_abbr == t)].net_current
                                   .iloc[0]),
                    net_removed=nets[f]))
        R = pd.DataFrame(rows)
        R.to_csv(OUT, index=False)
        NM = pd.DataFrame(nm_rows)
        NM.to_csv(OUT_NM, index=False)

        r.note("")
        r.note("FRAGILITY (%s basis): title odds with each player out for the playoffs, "
               "mean of four views [band]" % basis)
        for (t, pname, why), d in R.groupby(["team", "removed", "why"], sort=False):
            nm = NM[(NM.team == t) & (NM.removed == pname)]
            r.note("  %-3s %-24s full %5.2f%% -> %5.2f%% | drop %.2fpp [%.2f, %.2f] (%.0f%%) "
                   "| West rank %s -> %s | net -%.2f | removed %+.2f, next men %+.2f%s"
                   % (t, pname, d.title_full.mean(), d.title_removed.mean(),
                      d.drop_pp.mean(), d.drop_pp.min(), d.drop_pp.max(),
                      100 * d.drop_rel.mean(),
                      "/".join(str(v) for v in d.west_rank_full),
                      "/".join(str(v) for v in d.west_rank_removed),
                      nm.team_net_drop.mean(), nm[nm.fork == "consensus"].removed_net.iloc[0],
                      nm[nm.fork == "consensus"].replacement_net.iloc[0],
                      "" if why.startswith("top") else "  (sensitivity)"))
        r.output(OUT, rows=len(R))
        r.output(OUT_NM, rows=len(NM))
        if not args.aged:
            write_doc(r, R, NM, OUT_MD, sim_run=r.run_id)
            r.output(OUT_MD)
        else:
            r.note("aged basis written; run --doc-only to fold it into the doc")


def write_doc(r, R, NM, path, sim_run, aged=None):
    L = []
    L.append("# N5: fragility\n")
    L.append("*As of 2026-09-16. MODELLED: un-aged primary after the D70 fixes, series "
             "overlay off. Each player removed for the playoffs only; seeding from the "
             "full roster. Title odds from %d seeds x %s simulations per state, paired on "
             "seeds with the full-strength run. Simulation run `%s`; doc run `%s`.*\n"
             % (len(SEEDS), "{:,}".format(NSIMS), sim_run, r.run_id))
    main_ = R[R.why.str.startswith("top")]
    team = main_.groupby(["team", "fork"]).agg(drop_pp=("drop_pp", "mean"),
                                               full=("title_full", "first"))
    team = team.groupby("team").agg(drop_mean=("drop_pp", "mean"),
                                    drop_lo=("drop_pp", "min"), drop_hi=("drop_pp", "max"),
                                    full=("full", "mean"))
    # one source for the full-roster odds, so prose and tables round the same number
    team["full"] = main_.groupby("team").title_full.mean()
    team["rel"] = team.drop_mean / team.full
    per = (R.groupby(["team", "removed", "why"], sort=False)
           .agg(full=("title_full", "mean"), rem=("title_removed", "mean"),
                drop=("drop_pp", "mean"), lo=("drop_pp", "min"), hi=("drop_pp", "max"),
                rel=("drop_rel", "mean"),
                wr_full=("west_rank_full", lambda v: "/".join(str(i) for i in v)),
                wr_rem=("west_rank_removed", lambda v: "/".join(str(i) for i in v)))
           .reset_index())
    con = NM[NM.fork == "consensus"].set_index(["team", "removed"])
    netdrop = NM.groupby(["team", "removed"]).team_net_drop.agg(["mean", "min", "max"])

    worst = per[per.why.str.startswith("top")].sort_values("drop", ascending=False)
    L.append("**In plain terms.** %s\n" % plain(team, per, NM))
    L.append("| team | out for the playoffs | title odds, full roster | without him | drop, "
             "points [four views] | share of the team's odds lost | West rank by title "
             "odds, full / without (per view) | team net lost | his impact / the next "
             "men's (consensus) | who absorbs his minutes (consensus) |")
    L.append("|---|---|---:|---:|---|---:|---|---:|---|---|")
    for _, x in per.iterrows():
        c = con.loc[(x.team, x.removed)]
        nd = netdrop.loc[(x.team, x.removed)]
        L.append("| %s | %s%s | %.2f%% | %.2f%% | **%.2f** [%.2f, %.2f] | %.0f%% | %s / %s "
                 "| %.2f [%.2f, %.2f] | %+.2f / %+.2f | %s |"
                 % (x.team, x.removed, " *(sensitivity)*" if not x.why.startswith("top")
                    else "", x.full, x.rem, x["drop"], x.lo, x.hi, 100 * x.rel, x.wr_full,
                    x.wr_rem, nd["mean"], nd["min"], nd["max"], c.removed_net,
                    c.replacement_net, c.absorbers))
    L.append("")
    L.append("*West rank is listed per view, in the order consensus / RAPM / box / DARKO. "
             "Seed-to-seed noise on a drop, with the paired seeds, is at most %.2f points "
             "(standard error across %d seeds).*\n"
             % (R.drop_seed_se.max(), len(SEEDS)))
    nl = (NM[NM.why.str.startswith("top")].groupby(["team", "removed"]).team_net_drop
          .mean().reset_index())
    L.append("| team | title odds, full | mean drop across its top three, points [views] | "
             "share of its odds | mean net lost per removal | largest single net loss |")
    L.append("|---|---:|---|---:|---:|---|")
    for t_, x in team.iterrows():
        z = nl[nl.team == t_].sort_values("team_net_drop", ascending=False)
        L.append("| %s | %.2f%% | %.2f [%.2f, %.2f] | %.0f%% | %.2f | %s, %.2f |"
                 % (t_, x.full, x.drop_mean, x.drop_lo, x.drop_hi, 100 * x.rel,
                    z.team_net_drop.mean(), z.removed.iloc[0], z.team_net_drop.iloc[0]))
    L.append("")
    po = (NM[NM.why.str.startswith("top")].groupby("team")
          [["team_net_drop", "team_net_drop_playoff_rollup"]].mean())
    L.append("**Where the minutes go, and why it matters.** Each rotation is ten men, most "
             "of them close to their minute ceilings, so the allocator sends a removed "
             "player's minutes mostly to the eleventh and twelfth men rather than to the "
             "players already in the rotation. For Minnesota with %s out, the men who enter "
             "the rotation are %s. That is the "
             "pipeline's regular-season rule working as written, and a playoff rotation "
             "would not do it: it tightens, and the minutes go to the starters. Re-priced "
             "with the pipeline's own playoff rollup (top nine by minutes, rescaled to a "
             "full game), the mean net lost per removal is %s, against %s on the "
             "regular-season rule.%s\n"
             % (NM[(NM.team == "MIN") & (NM.fork == "consensus")].removed.iloc[0],
                NM[(NM.team == "MIN") & (NM.fork == "consensus")].new_to_rotation
                .replace("", "none").iloc[0],
                ", ".join("%s %.2f" % (t_, po.loc[t_, "team_net_drop_playoff_rollup"])
                          for t_ in po.index),
                ", ".join("%s %.2f" % (t_, po.loc[t_, "team_net_drop"]) for t_ in po.index),
                ""))
    if aged is not None:
        L.extend(both_bases(R, NM, aged[0], aged[1]))
    L.append("**What it does not show.** The team's playoff variance is held at "
             "full-roster values. "
             "Injuries to more than one player, or to anyone outside the top three.\n")
    L.append("*Method.* Minutes: `rotation.allocate` with the player's availability at "
             "zero, ceiling rule on, reproducing the published rotation exactly before any "
             "removal (gate G2). Strength: net plus beta times the change in the "
             "minutes-weighted impact rollup, reproducing the published net exactly (G3). "
             "Simulation: `simulate_league` with seeding from full-strength nets and the "
             "playoff draw from the reduced net, reproducing the original draw for draw "
             "when nothing is removed (G4). Next men: minutes-weighted impact of the "
             "minutes each other player gains. Detail: `outputs/n5_fragility.csv`, "
             "`n5_next_man_up.csv`.\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def both_bases(R, NM, RA, NA):
    """The W2 discipline: which N5 statements hold on BOTH aging bases."""
    def summary(Rx, Nx):
        m = Rx[Rx.why.str.startswith("top")]
        n = Nx[Nx.why.str.startswith("top")]
        full = m.groupby("team").title_full.mean()
        drop = m.groupby(["team", "removed"]).drop_pp.mean()
        net = n.groupby(["team", "removed"]).team_net_drop.mean()
        out = {}
        for t in full.index:
            d, nt = drop.loc[t], net.loc[t]
            out[t] = dict(full=full[t], drop=d.mean(), share=d.mean() / full[t],
                          net=nt.mean(), big_name=nt.idxmax(), big=nt.max(),
                          top_title_loss=d.idxmax())
        return out
    u, g = summary(R, NM), summary(RA, NA)
    teams = list(u)
    L = ["## Both aging bases\n",
         "The same removals on the survivorship-corrected aged basis (outputs/aged/, "
         "gated the same way). A statement belongs in the piece only if it holds on "
         "both.\n",
         "| team | title odds, un-aged / aged | mean drop, points | share of its odds | "
         "mean net lost per removal | largest single net loss | biggest title-odds loss |",
         "|---|---|---|---|---|---|---|"]
    for t in teams:
        L.append("| %s | %.2f%% / %.2f%% | %.2f / %.2f | %.0f%% / %.0f%% | %.2f / %.2f | "
                 "%s %.2f / %s %.2f | %s / %s |"
                 % (t, u[t]["full"], g[t]["full"], u[t]["drop"], g[t]["drop"],
                    100 * u[t]["share"], 100 * g[t]["share"], u[t]["net"], g[t]["net"],
                    u[t]["big_name"], u[t]["big"], g[t]["big_name"], g[t]["big"],
                    u[t]["top_title_loss"], g[t]["top_title_loss"]))
    L.append("")
    others = [t for t in teams if t != "MIN"]
    checks = [
        ("Minnesota loses a larger share of its title odds than both contenders",
         all(b["MIN"]["share"] > max(b[o]["share"] for o in others) for b in (u, g))),
        ("Minnesota's largest single net loss is smaller than each contender's",
         all(b["MIN"]["big"] < min(b[o]["big"] for o in others) for b in (u, g))),
        ("Minnesota loses no more strength per removal on average than the contenders "
         "(within 0.10 or less)",
         all(b["MIN"]["net"] <= max(b[o]["net"] for o in others) + 0.10 for b in (u, g))),
        ("The same Minnesota player is the biggest title-odds loss on both bases",
         u["MIN"]["top_title_loss"] == g["MIN"]["top_title_loss"]),
    ]
    L.append("| statement | holds on both bases |")
    L.append("|---|---|")
    for s, ok in checks:
        L.append("| %s | **%s** |" % (s, "yes" if ok else "no"))
    L.append("")
    if not checks[3][1]:
        L.append("So the piece can say Minnesota's strength is spread and the contenders' "
                 "is concentrated, and it cannot name which Minnesota player is the "
                 "costliest to lose: %s on the un-aged basis, %s on the aged one.\n"
                 % (u["MIN"]["top_title_loss"], g["MIN"]["top_title_loss"]))
    return L


def po_sentence(po):
    """What the playoff-rollup sensitivity says, written from the numbers."""
    shrink = [x for x in po.index
              if po.loc[x, "team_net_drop_playoff_rollup"] < po.loc[x, "team_net_drop"]]
    grow = [x for x in po.index if x not in shrink]
    least = po.team_net_drop_playoff_rollup.idxmin()
    parts = []
    def poss(xs):
        return " and ".join("%s's" % x for x in xs)
    if shrink:
        parts.append("%s %s (%s)" % (poss(shrink), "loss shrinks" if len(shrink) == 1
                                     else "losses shrink", "; ".join(
            "%.2f to %.2f" % (po.loc[x, "team_net_drop"],
                              po.loc[x, "team_net_drop_playoff_rollup"]) for x in shrink)))
    if grow:
        parts.append("%s %s (%s)" % (poss(grow), "grows" if len(grow) == 1 else "grow",
                                     "; ".join(
            "%.2f to %.2f" % (po.loc[x, "team_net_drop"],
                              po.loc[x, "team_net_drop_playoff_rollup"]) for x in grow)))
    return ("With a tightened playoff rotation, %s, because tightening takes weak "
            "eleventh and twelfth men out of the replacement and takes a strong bench out "
            "with it. On that reading %s loses the least strength per removal of the "
            "three. It is a sensitivity on net rating, not re-simulated title odds."
            % (", while ".join(parts), least))


def plain(team, per, NM):
    mn = team.loc["MIN"]
    m = per[(per.team == "MIN") & per.why.str.startswith("top")].sort_values(
        "drop", ascending=False)
    top = m.iloc[0]
    others = [t for t in team.index if t != "MIN"]
    top3 = NM[NM.why.str.startswith("top")]
    nl = top3.groupby(["team", "removed"]).team_net_drop.mean().reset_index()
    avg = nl.groupby("team").team_net_drop.mean()
    big = nl.sort_values("team_net_drop", ascending=False).groupby("team").head(1) \
        .set_index("team")
    imp = top3[top3.team == "MIN"].groupby("removed").removed_net.agg(["min", "max"])
    return (
        "Take one of Minnesota's top three away for the playoffs and its title odds fall "
        "from %.2f%% by %.2f points on average, %.0f%% of what it had. %s. "
        "In strength, the three teams lose almost the same amount per removal on average "
        "(%s net points), but the contenders' loss sits in one player (%s) while "
        "Minnesota's is spread across three (its largest is %s, %.2f). Minnesota loses a "
        "bigger share of its odds mostly because it starts from %.2f%%, where each point of "
        "net rating is a larger fraction of what it has. One caution on the order inside "
        "Minnesota: how much each loss costs is only as good as each view's rating of the "
        "player, and the views disagree most on %s (impact %+.2f to %+.2f across the four), "
        "and his drop runs from %.2f to %.2f points across them. %s"
        % (mn.full, mn.drop_mean, 100 * mn.rel,
           "; ".join("%s falls from %.2f%% by %.2f points on average (%.0f%%)"
                     % (t, team.loc[t, "full"], team.loc[t, "drop_mean"],
                        100 * team.loc[t, "rel"]) for t in others),
           ", ".join("%s %.2f" % (t, avg[t]) for t in team.index),
           ", ".join("%s %.2f" % (big.loc[t, "removed"], big.loc[t, "team_net_drop"])
                     for t in others),
           big.loc["MIN", "removed"], big.loc["MIN", "team_net_drop"], mn.full,
           (imp["max"] - imp["min"]).idxmax(),
           imp.loc[(imp["max"] - imp["min"]).idxmax(), "min"],
           imp.loc[(imp["max"] - imp["min"]).idxmax(), "max"],
           float(m.set_index("removed").loc[(imp["max"] - imp["min"]).idxmax(), "lo"]),
           float(m.set_index("removed").loc[(imp["max"] - imp["min"]).idxmax(), "hi"]),
           po_sentence(top3.groupby("team")[["team_net_drop",
                                             "team_net_drop_playoff_rollup"]].mean())))


if __name__ == "__main__":
    main()
