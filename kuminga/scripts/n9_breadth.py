#!/usr/bin/env python3
"""N9 (version 2, D113): the breadth of the odds. How wide is the model's range for a team's
title odds once the model's forks AND the season's player-level uncertainty are allowed to
vary, and how does Minnesota's range compare with the teams the market prices beside it?

No written N9 specification exists in the project; the design is D112 as revised by D113.

CELLS: impact view (4) x aging basis (2) x minutes allocator (2) = 16 per team. The flat
ordering is NOT a cell: it is a recorded sensitivity (D111), and it enters only as role
uncertainty for players who changed teams (below).

DRAWS: N joint draws per team, the same draws feeding all 16 cells (common random numbers),
each sampling three things together:
  1. AVAILABILITY. Every pool player's share of regular-season games is drawn from his own
     predictive distribution: the C3 cohort method generalized. For each player, the
     historical player-seasons (2002-03 to 2025-26) that match him on age (within a year),
     the number of his last three seasons at 60% of games or fewer, last season's games
     share (within 0.10) and last season's role (minutes per appearance, 24 or more, or
     within six), widened in fixed steps until the cohort has at least 40 player-seasons;
     the draw is one of the cohort's outcomes. A whole season missed between two seasons
     played counts as zero games (so the cohort is not survivor-only). Rookies and players
     with no NBA season draw from the rookie cohort (first seasons at 12 or more minutes per
     appearance). A known season-long absence (rs_avail below one in the pool, DiVincenzo)
     multiplies the draw. The draw enters RELATIVE to the league's typical availability for
     rotation minutes (the minutes-weighted mean of the predicted shares across the 30
     projected rotations): the model's net-to-wins and title scales are calibrated on real
     seasons, which already carry ordinary wear, so only a player's deviation from typical
     health moves his team (a player at the typical share is at the published minutes).
     Availability is REGULAR-SEASON availability with the playoffs at
     full strength, the convention Part 4's Ball figures use (C3); whether a player is there
     in April is the fragility question (N5), not drawn here. It is priced through the seed:
     see PRICING.
  2. ROLE, movers. Each player who changed teams is ordered, independently, on the primary
     mover-discounted score or the flat half-and-half score, with equal probability.
  3. ROLE, rookies. Each 2026 rookie's impact is his draft-slot prior plus a normal draw with
     the stated prior sd: the residual sd of the 2025 class around the slot line (computed
     here; 2.05 points of net on n=44). His order score moves with it.

PRICING. For each draw and cell the pipeline's own formula gives two nets: the regular-season
net (minutes with the drawn availability) and the playoff net (full availability, the draw's
roles). Title odds are the playoff net priced on the f-curve, less the seeding share s of the
gap to the regular-season net priced on the same curve:
    title = F(net_po) - s * (F(net_po) - F(net_rs))
s is calibrated per view and basis on C3's direct simulations (Ball at 50, 60 and 70 games,
seeding from the reduced net, playoffs at full strength) and gated against them. Minnesota
is priced on its own f-curve; every other team on an anchored proxy (Minnesota's curve shifted
in log-odds through the team's own simulated odds at its published point), as in version 1.
Expected wins = wins_a + wins_b * net_rs (the simulator's own). The seed is the simulator's
own regular-season rule, vectorized: the team's wins plus record noise against the other
fourteen conference teams at their cell's point nets plus noise.

GATES
  G1  zero noise (every draw at full availability, primary order, rookie at the prior) the
      team-rank cell reproduces the published net for all 30 teams on both bases
  G2  the proxy returns each team's simulated odds at its anchor
  G3  the seeding share reproduces C3's direct-simulation title odds at 50, 60, 70 games
      within the f-curve tolerance (0.15 points), both bases
  G4  the seed rule, at point nets, reproduces seed_distribution.csv's mean seed within 0.05
  G5  THE HEADLINE GATE: in the headline cells (team-rank, un-aged, four views) the mean over
      the joint draws reproduces the sheet's headline within the f-curve tolerance; the same
      for the aged basis against the aged headline. G1 to G4 are fatal. G5 is reported, and
      N9 does not ship while it fails; its failure is decomposed by source for Minnesota.

    python kuminga/scripts/n9_breadth.py [--ndraws N]
"""
from __future__ import annotations

import argparse
import io
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

from kuminga.lib import kfreeze, rotation, runlog      # noqa: E402
import build_team_ratings as A                         # noqa: E402
import bracket_sim as E                                # noqa: E402
import build_strengths as BS                           # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
AGED = os.path.join(OUT_DIR, "aged")
POOL = os.path.join(OUT_DIR, "player_pool_2026_27.csv")
CURVE = os.path.join(OUT_DIR, "minutes_rank_curve.csv")
MARKET = os.path.join(OUT_DIR, "market_devig_2026_27.csv")
PANEL = os.path.join(OUT_DIR, "c3_player_seasons_panel.csv")
SHEET = os.path.join(OUT_DIR, "final_numbers.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
DOC = os.path.join(REPO, "kuminga", "docs", "n9_breadth.md")

FORKS = ["consensus", "rapm", "box", "darko"]
BASES = ["unaged", "aged"]
ALLOCS = ["team-rank", "pooled"]
NEIGHBOURS = ["MIN", "DEN", "DET", "CLE", "TOR", "BOS", "MIA"]
TOL = 0.15                 # the f-curve tolerance (reconcile C1), percentage points
SEED_TOL = 0.05
NDRAWS = 2000
K_SEED = 400
RNG_SEED = 20260929
BAD_SHARE = 0.60
MIN_COHORT = 40
ROOKIE_MPA = 12.0
P_FLOOR = 1e-5

# ---------------------------------------------------------------- availability cohorts


def start_year(season):
    return int(str(season)[:4])


def history_table(panel):
    """One row per (player, outcome season t) with the features the cohort matches on."""
    rows = []
    for pid, g in panel.groupby("player_id"):
        g = g.sort_values("t")
        S = dict(zip(g.t, g.share))
        M = dict(zip(g.t, g.mpa))
        AG = dict(zip(g.t, g.age))
        first, last = min(S), max(S)

        def share_at(k):
            if k in S:
                return S[k]
            return 0.0 if first < k < last else None      # a whole season missed in between

        for t in range(max(first + 1, 2002), last + 1):
            out = share_at(t)
            prev = share_at(t - 1)
            if out is None or prev is None:
                continue
            nbad = 0
            for k in (t - 3, t - 2, t - 1):
                v = share_at(k)
                if v is not None and v <= BAD_SHARE:
                    nbad += 1
            mprev = M.get(t - 1)
            if mprev is None or pd.isna(mprev):
                ks = [k for k in M if k < t and not pd.isna(M[k])]
                mprev = M[max(ks)] if ks else np.nan
            age = AG.get(t)
            if age is None or pd.isna(age):
                ka = [k for k in AG if not pd.isna(AG[k])]
                age = (AG[max(ka)] + (t - max(ka))) if ka else np.nan
            rows.append((pid, t, float(age), float(out), float(prev), nbad, float(mprev) if not pd.isna(mprev) else np.nan))
    return pd.DataFrame(rows, columns=["player_id", "t", "age", "share", "share_prev", "n_bad", "mpa_prev"])


def target_features(panel, pid, t=2026):
    g = panel[panel.player_id == pid].sort_values("t")
    if g.empty:
        return None
    S = dict(zip(g.t, g.share))
    first, last = min(S), max(S)

    def share_at(k):
        if k in S:
            return S[k]
        return 0.0 if first < k <= last else None

    prev = S.get(t - 1, 0.0 if first < t - 1 else None)
    if prev is None:
        prev = S[last]
    nbad = sum(1 for k in (t - 3, t - 2, t - 1) if share_at(k) is not None and share_at(k) <= BAD_SHARE)
    mp = g.dropna(subset=["mpa"])
    mprev = float(mp.mpa.iloc[-1]) if len(mp) else np.nan
    ag = g.dropna(subset=["age"])
    age = float(ag.age.iloc[-1] + (t - ag.t.iloc[-1])) if len(ag) else np.nan
    return dict(age=age, share_prev=float(prev), n_bad=int(nbad), mpa_prev=mprev)


STEPS = [dict(age=1, sp=0.10, role=True, nb=0), dict(age=2, sp=0.10, role=True, nb=0),
         dict(age=2, sp=0.15, role=True, nb=0), dict(age=2, sp=0.15, role=False, nb=0),
         dict(age=2, sp=0.15, role=False, nb=1), dict(age=3, sp=0.20, role=False, nb=1)]


def cohort(H, x):
    for i, s in enumerate(STEPS):
        m = ((H.age - x["age"]).abs() <= s["age"]) & ((H.share_prev - x["share_prev"]).abs() <= s["sp"]) \
            & ((H.n_bad - x["n_bad"]).abs() <= s["nb"])
        if s["role"] and not np.isnan(x["mpa_prev"]):
            if x["mpa_prev"] >= 24:
                m &= H.mpa_prev >= 24
            else:
                m &= (H.mpa_prev - x["mpa_prev"]).abs() <= 6
        out = H.share[m].to_numpy(float)
        if len(out) >= MIN_COHORT:
            return out, i
    return H.share.to_numpy(float), len(STEPS)


# ---------------------------------------------------------------- the worker

_W = {}


def _init():
    pool = pd.read_csv(POOL)
    pool = pool[pool.scenario == "current"].copy()
    curve = pd.read_csv(CURVE, index_col=0).iloc[:, 0]
    value = pd.read_csv(VALUE)
    darko = pd.read_csv(DARKO)
    darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
    bio, _ = kfreeze.load("player_bio")
    imps = {}
    for b in BASES:
        prev = os.environ.get(BS.AGING_ENV)
        os.environ[BS.AGING_ENV] = "1" if b == "aged" else "0"
        try:
            im, _ = BS.build_impacts(value, darko, bio)
            BS.add_rookie_impacts(im, pool)
        finally:
            if prev is None:
                os.environ.pop(BS.AGING_ENV, None)
            else:
                os.environ[BS.AGING_ENV] = prev
        imps[b] = im
    st = {b: pd.read_csv(os.path.join(OUT_DIR if b == "unaged" else AGED, "team_strengths_2026_27.csv")) for b in BASES}
    beta = float(E.load_e_params()["beta"])
    league_nets = np.sort(pool.consensus_net.to_numpy(float))
    _W.update(pool=pool, curve=curve, imps=imps, st=st, beta=beta, league_nets=league_nets)


def _ecdf(x):
    ln = _W["league_nets"]
    return np.searchsorted(ln, x, side="right") / len(ln)


def run_team(args):
    """Nets for one team: arrays [N, basis, view, allocator] for the regular season and the
    playoffs. `flags` switch the sources on and off (the Minnesota decomposition)."""
    team, n, seed, cohorts, rookie_sd, flags, typical = args
    if not _W:
        _init()
    pool, curve, imps, st, beta = _W["pool"], _W["curve"], _W["imps"], _W["st"], _W["beta"]
    base = pool[pool.team_abbr == team].copy().reset_index(drop=True)
    rng = np.random.default_rng(seed)
    npl = len(base)
    keys = [str(int(p)) if not pd.isna(p) else None for p in base.player_id]
    mover = base.moved_teams.fillna(False).astype(bool).to_numpy()
    rookie = base.is_rookie.fillna(False).astype(bool).to_numpy()
    rs0 = base.rs_avail.to_numpy(float)
    rank_p = base.rank_score.to_numpy(float)
    rank_f = base.rank_score_flat.to_numpy(float)
    net0 = base.consensus_net.to_numpy(float)
    ecdf0 = _ecdf(net0)
    # the draws, all at once (common random numbers across the 16 cells)
    avail = np.ones((n, npl))
    if flags.get("avail", True):
        for i in range(npl):
            c = cohorts.get(keys[i]) if keys[i] is not None else None
            if c is None:
                c = cohorts["__rookie__"]
            avail[:, i] = c[rng.integers(0, len(c), n)] / typical
    fork = (rng.random((n, npl)) < 0.5) & mover if flags.get("fork", True) else np.zeros((n, npl), bool)
    z = rng.standard_normal((n, npl)) * rookie if flags.get("rookie", True) else np.zeros((n, npl))
    rows_rs = np.zeros((n, 2, 4, 2))
    rows_po = np.zeros((n, 2, 4, 2))
    exp_hb = {(b, f): (float(st[b][(st[b].fork == f) & (st[b].team_abbr == team)].exp_2026_27.iloc[0]),
                       float(st[b][(st[b].fork == f) & (st[b].team_abbr == team)].hot_baseline.iloc[0]))
              for b in BASES for f in FORKS}
    for d in range(n):
        g = base.copy()
        dnet = rookie_sd * z[d]
        rs = np.where(fork[d], rank_f, rank_p)
        if rookie.any():
            pct = base.pct_net.to_numpy(float) + (_ecdf(net0 + dnet) - ecdf0)
            rs = np.where(rookie, rotation.MPG_WEIGHT * base.pct_mpg.to_numpy(float) + (1 - rotation.MPG_WEIGHT) * pct, rs)
        g["rank_score"] = rs
        g_rs = g.copy()
        g_rs["rs_avail"] = rs0 * avail[d]
        g_po = g
        mins = {}
        for a in ALLOCS:
            alloc = (lambda x: rotation.allocate(x, curve, use_ceiling=True)) if a == "team-rank" else (lambda x: rotation.allocate_pooled(x, curve))
            mins[("rs", a)] = alloc(g_rs)
            mins[("po", a)] = alloc(g_po)
        # rookie impact shifts enter the rollup linearly: (minutes / 48) * shift in net
        shift = {k: 0.0 for k in mins}
        if rookie.any():
            for k, mm in mins.items():
                shift[k] = sum(mm.get(keys[i], 0.0) / 48.0 * dnet[i] for i in np.where(rookie)[0] if keys[i] is not None)
        for bi, b in enumerate(BASES):
            for fi, f in enumerate(FORKS):
                ex, hb = exp_hb[(b, f)]
                for ai, a in enumerate(ALLOCS):
                    rows_rs[d, bi, fi, ai] = ex + beta * (A.rollup(mins[("rs", a)], imps[b][f], "rs")["net"] + shift[("rs", a)] - hb)
                    rows_po[d, bi, fi, ai] = ex + beta * (A.rollup(mins[("po", a)], imps[b][f], "rs")["net"] + shift[("po", a)] - hb)
    return team, rows_rs, rows_po


# ---------------------------------------------------------------- main


def logit(p):
    p = np.clip(p, P_FLOOR, 1 - P_FLOOR)
    return np.log(p / (1 - p))


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ndraws", type=int, default=NDRAWS)
    ap.add_argument("--variant", choices=["spec", "forkoff"], default="spec",
                    help="forkoff: the mover order held at the primary for every team (written with a _FORKOFF suffix)")
    args = ap.parse_args()
    N = args.ndraws
    FORK = args.variant == "spec"
    SFX = "" if FORK else "_FORKOFF"
    with runlog.run("n9_breadth", inputs={"version": 2, "cells": 16, "ndraws": N, "variant": args.variant,
                                          "sources": "view, basis, allocator; availability, mover order, rookie impact"}) as r:
        pool = pd.read_csv(POOL)
        pool = pool[pool.scenario == "current"].copy()
        teams = sorted(pool.team_abbr.unique())
        params = E.load_e_params()
        wa, wb, sig_rec = float(params["wins_a"]), float(params["wins_b"]), float(params["sigma_record"])
        market = pd.read_csv(MARKET).set_index("team_abbr")
        sheet = pd.read_csv(SHEET, dtype=str).set_index("key")
        head = {"unaged": float(sheet.loc["title", "value"].rstrip("%")), "aged": float(sheet.loc["title_aged", "value"].rstrip("%"))}

        # ---- the rookie prior sd, from the 2025 class -----------------------------------------
        bio, _ = kfreeze.load("player_bio")
        v = pd.read_csv(VALUE).set_index("player_id")
        rk = bio[bio.draft_year.astype(str) == "2025"].copy()
        rk["pick"] = pd.to_numeric(rk.draft_number, errors="coerce")
        rk["cn"] = rk.player_id.map(v.consensus_net)
        rk = rk.dropna(subset=["pick", "cn"]).drop_duplicates("player_id")
        bb, aa = np.polyfit(rk.pick, rk.cn, 1)
        res = rk.cn - (aa + bb * rk.pick)
        rookie_sd = float(np.sqrt((res ** 2).sum() / (len(rk) - 2)))
        r.note("rookie prior sd: %.2f points of net (2025 class, n=%d, residual around the slot line)" % (rookie_sd, len(rk)))

        # ---- availability cohorts ----------------------------------------------------------------
        panel = pd.read_csv(PANEL)
        H = history_table(panel)
        firsts = panel.sort_values("t").groupby("player_id").head(1)
        rook = firsts[(firsts.mpa >= ROOKIE_MPA) & (firsts.t >= 2002)].share.to_numpy(float)
        cohorts = {"__rookie__": rook}
        steps = []
        for _, x in pool.dropna(subset=["player_id"]).iterrows():
            pid = int(x.player_id)
            if pid < 0:
                continue
            tf = target_features(panel, pid)
            if tf is None:
                continue
            out, step = cohort(H, tf)
            cohorts[str(pid)] = out
            steps.append(dict(team=x.team_abbr, player=x.player_name, player_id=pid, **tf, cohort_n=len(out), widen_step=step,
                              pred_mean=float(out.mean()), pred_p10=float(np.percentile(out, 10)), pred_p50=float(np.median(out)),
                              pred_p90=float(np.percentile(out, 90))))
        AV = pd.DataFrame(steps)
        AV.to_csv(os.path.join(OUT_DIR, "n9_availability.csv"), index=False)
        r.note("availability: %d history rows; %d players with their own cohort (median n %d; %d widened past step 0); rookie cohort n %d, mean share %.2f"
               % (len(H), len(AV), int(AV.cohort_n.median()), int((AV.widen_step > 0).sum()), len(rook), rook.mean()))
        rot = pd.read_csv(os.path.join(OUT_DIR, "rotations_2026_27.csv"))
        rot = rot[(rot.scenario == "current") & (rot.mpg > 0)].copy()
        rot["pm"] = [float(cohorts.get(str(int(p)), cohorts["__rookie__"]).mean()) if not pd.isna(p) and int(p) > 0 else float(cohorts["__rookie__"].mean())
                     for p in rot.player_id]
        typical = float((rot.pm * rot.mpg).sum() / rot.mpg.sum())
        r.note("typical availability for rotation minutes (minutes-weighted mean predicted share, 30 rotations): %.3f" % typical)
        AV["relative_to_typical"] = AV.pred_mean / typical
        AV.to_csv(os.path.join(OUT_DIR, "n9_availability.csv"), index=False)
        mn = AV[AV.team == "MIN"].sort_values("pred_mean")
        for x in mn.itertuples():
            r.note("   MIN %-22s age %4.1f prev %.2f bad %d mpa %4.1f -> mean %.2f (p10 %.2f, median %.2f) n=%d step %d"
                   % (x.player, x.age, x.share_prev, x.n_bad, x.mpa_prev, x.pred_mean, x.pred_p10, x.pred_p50, x.cohort_n, x.widen_step))

        # ---- G1: zero noise reproduces the published net ----------------------------------------
        zero = dict(avail=False, fork=False, rookie=False)
        with ProcessPoolExecutor(max_workers=6, initializer=_init) as ex:
            Z = {t: (rs_, po_) for t, rs_, po_ in ex.map(run_team, [(t, 1, 0, cohorts, rookie_sd, zero, 1.0) for t in teams])}
        st = {b: pd.read_csv(os.path.join(OUT_DIR if b == "unaged" else AGED, "team_strengths_2026_27.csv")) for b in BASES}
        g1 = 0.0
        point = {}
        for t in teams:
            rs_, po_ = Z[t]
            for bi, b in enumerate(BASES):
                for fi, f in enumerate(FORKS):
                    pub = float(st[b][(st[b].fork == f) & (st[b].team_abbr == t)].net_current.iloc[0])
                    g1 = max(g1, abs(po_[0, bi, fi, 0] - pub), abs(rs_[0, bi, fi, 0] - pub))
                    for ai, a in enumerate(ALLOCS):
                        point[(t, b, f, a)] = float(po_[0, bi, fi, ai])
        r.note("G1: zero noise reproduces the published net, worst gap %.2e (30 teams, both bases, both nets)" % g1)
        if g1 > 1e-6:
            raise RuntimeError("G1 failed: %.2e" % g1)

        # ---- the draws ---------------------------------------------------------------------------
        jobs = [(t, N, RNG_SEED + 1000 * i, cohorts, rookie_sd, dict(avail=True, fork=FORK, rookie=True), typical) for i, t in enumerate(teams)]
        # Minnesota, one source at a time (same seed: the sources' draws are generated in the same order)
        mi = teams.index("MIN")
        dec = {"availability only": dict(avail=True, fork=False, rookie=False), "mover order only": dict(avail=False, fork=True, rookie=False),
               "rookie impact only": dict(avail=False, fork=False, rookie=True), "availability and rookies (mover order at the primary)": dict(avail=True, fork=False, rookie=True)}
        jobs += [("MIN", N, RNG_SEED + 1000 * mi, cohorts, rookie_sd, fl, typical) for fl in dec.values()]
        with ProcessPoolExecutor(max_workers=6, initializer=_init) as ex:
            res_ = list(ex.map(run_team, jobs))
        D = {t: (rs_, po_) for t, rs_, po_ in res_[:len(teams)]}
        DEC = {lab: (rs_, po_) for lab, (_, rs_, po_) in zip(dec, res_[len(teams):])}
        r.note("draws: %d per team, 16 cells each" % N)

        # ---- pricing -------------------------------------------------------------------------------
        fc = {b: pd.read_csv(os.path.join(OUT_DIR if b == "unaged" else AGED, "fcurve_min.csv")) for b in BASES}
        sims = {b: pd.read_csv(os.path.join(OUT_DIR if b == "unaged" else AGED, "sim_all30_2026_27.csv")) for b in BASES}

        def F(b, f, net):
            g = fc[b][fc[b].fork == f].sort_values("min_net")
            return np.interp(net, g.min_net.to_numpy(float), g.title.to_numpy(float))

        anchors = {}
        for b in BASES:
            for t in teams:
                for f in FORKS:
                    x = sims[b][(sims[b].fork == f) & (sims[b].team_abbr == t)].iloc[0]
                    anchors[(b, t, f)] = (float(x.net_current), float(x.title_current))

        def price(t, b, f, net):
            net = np.asarray(net, float)
            if t == "MIN":
                return F(b, f, net)
            nt, tt = anchors[(b, t, f)]
            nm, _ = anchors[(b, "MIN", f)]
            c = logit(tt) - logit(F(b, f, nt + nm - nt))
            return expit(logit(F(b, f, net + nm - nt)) + c)

        g2 = max(abs(float(price(t, b, f, anchors[(b, t, f)][0])) - anchors[(b, t, f)][1]) * 100
                 for b in BASES for t in teams if t != "MIN" for f in FORKS)
        r.note("G2: the proxy returns each team's simulated odds at its anchor, worst gap %.2e pp (the probability floor, %.0e, for teams simulated at zero)" % (g2, 100 * P_FLOOR))
        if g2 > 100 * P_FLOOR * 1.01:   # a team the simulation prices at zero sits on the probability floor
            raise RuntimeError("G2 failed: %.3e" % g2)

        # the seeding share, calibrated on C3's direct simulations
        S_ = {}
        g3 = []
        for b, fn in (("unaged", "c3_ball_availability.csv"), ("aged", "c3_ball_availability_AGED.csv")):
            c3 = pd.read_csv(os.path.join(OUT_DIR, fn))
            for f in FORKS:
                x = c3[(c3.fork == f) & (c3.games < 82)]
                gap = 100 * (F(b, f, x.net_full.to_numpy(float)) - F(b, f, x.net_rs.to_numpy(float)))
                s = float(x.title_drop_pp.sum() / gap.sum())
                S_[(b, f)] = s
                pred = 100 * F(b, f, x.net_full.to_numpy(float)) - s * gap
                for gm, p_, obs, dp, do in zip(x.games, pred, x.title, s * gap, x.title_drop_pp):
                    g3.append(dict(basis=b, view=f, games=int(gm), s=s, title_pred=float(p_), title_direct=float(obs),
                                   drop_pred=float(dp), drop_direct=float(do)))
        G3 = pd.DataFrame(g3)
        G3["gap"] = (G3.title_pred - G3.title_direct).abs()
        G3["drop_gap"] = (G3.drop_pred - G3.drop_direct).abs()
        r.note("G3: seeding share s by view (un-aged / aged): %s; worst title gap %.3f pp, worst drop gap %.3f pp against C3's direct simulations"
               % (", ".join("%s %.2f / %.2f" % (f, S_[("unaged", f)], S_[("aged", f)]) for f in FORKS), G3.gap.max(), G3.drop_gap.max()))
        if G3.gap.max() > TOL:
            raise RuntimeError("G3 failed: %.3f pp" % G3.gap.max())

        def title_of(t, rs_, po_):
            out = np.zeros(po_.shape)
            for bi, b in enumerate(BASES):
                for fi, f in enumerate(FORKS):
                    for ai in range(2):
                        p_po = price(t, b, f, po_[:, bi, fi, ai])
                        p_rs = price(t, b, f, rs_[:, bi, fi, ai])
                        out[:, bi, fi, ai] = 100 * (p_po - S_[(b, f)] * (p_po - p_rs))
            return out

        TT = {t: title_of(t, *D[t]) for t in teams}

        # ---- seeds -----------------------------------------------------------------------------------
        conf = pool.drop_duplicates("team_abbr").set_index("team_abbr")
        confs = st["unaged"].drop_duplicates("team_abbr").set_index("team_abbr").conf
        rng = np.random.default_rng(RNG_SEED + 7)
        e0 = rng.normal(0, sig_rec, K_SEED)
        er = rng.normal(0, sig_rec, (K_SEED, 14))

        def seeds(t, b, f, a, nets):
            rivals = [u for u in teams if u != t and confs[u] == confs[t]]
            wr = np.array([wa + wb * point[(u, b, f, a)] for u in rivals])[None, :] + er[:, :len(rivals)]
            wt = (wa + wb * np.asarray(nets, float))[:, None] + e0[None, :]
            seed = 1 + (wr[None, :, :] > wt[:, :, None]).sum(axis=2)
            return seed.mean(axis=1), (seed <= 6).mean(axis=1)

        sd = pd.read_csv(os.path.join(OUT_DIR, "seed_distribution.csv"))
        sd = sd[sd.field == "current"]
        g4 = 0.0
        rng_g = np.random.default_rng(99)
        big0 = rng_g.normal(0, sig_rec, 40000)
        bigr = rng_g.normal(0, sig_rec, (40000, 14))
        for t in teams:
            for f in FORKS:
                rivals = [u for u in teams if u != t and confs[u] == confs[t]]
                wr = np.array([wa + wb * point[(u, "unaged", f, "team-rank")] for u in rivals])[None, :] + bigr[:, :len(rivals)]
                wt = wa + wb * point[(t, "unaged", f, "team-rank")] + big0
                ms = float((1 + (wr > wt[:, None]).sum(axis=1)).mean())
                pub = float(sd[(sd.fork == f) & (sd.team_abbr == t)].mean_seed.iloc[0])
                g4 = max(g4, abs(ms - pub))
        r.note("G4: the seed rule at point nets reproduces seed_distribution.csv's mean seed, worst gap %.3f" % g4)
        if g4 > SEED_TOL:
            raise RuntimeError("G4 failed: %.3f" % g4)

        # ---- G5: the headline gate -------------------------------------------------------------------
        g5 = []
        for bi, b in enumerate(BASES):
            m_views = [float(TT["MIN"][:, bi, fi, 0].mean()) for fi in range(4)]
            mean = float(np.mean(m_views))
            g5.append(dict(basis=b, headline=head[b], draw_mean=mean, gap=mean - head[b], passes=abs(mean - head[b]) <= TOL,
                           **{"view_" + f: v_ for f, v_ in zip(FORKS, m_views)}))
        G5 = pd.DataFrame(g5)
        for x in G5.itertuples():
            r.note("G5 %s: headline %.2f%%, mean over the joint draws %.2f%% (gap %+.2f pp): %s"
                   % (x.basis, x.headline, x.draw_mean, x.gap, "PASSES" if x.passes else "FAILS (tolerance %.2f)" % TOL))

        # Minnesota's decomposition by source, headline cells
        dec_rows = []
        for lab, (rs_, po_) in [("all three sources", D["MIN"])] + list(DEC.items()):
            T_ = title_of("MIN", rs_, po_)
            for bi, b in enumerate(BASES):
                v_ = T_[:, bi, :, 0].mean(axis=1)
                dec_rows.append(dict(sources=lab, basis=b, mean=float(v_.mean()), gap=float(v_.mean() - head[b]),
                                     p10=float(np.percentile(v_, 10)), p50=float(np.median(v_)), p90=float(np.percentile(v_, 90)),
                                     passes=abs(float(v_.mean()) - head[b]) <= TOL))
        # the sensitivity: availability reaching the playoffs too (games missed at random, April included)
        rs_, po_ = DEC["availability only"]
        T_ = np.zeros(rs_.shape)
        for bi, b in enumerate(BASES):
            for fi, f in enumerate(FORKS):
                T_[:, bi, fi, :] = 100 * F(b, f, rs_[:, bi, fi, :])
        for bi, b in enumerate(BASES):
            v_ = T_[:, bi, :, 0].mean(axis=1)
            dec_rows.append(dict(sources="sensitivity: availability reaching the playoffs too", basis=b, mean=float(v_.mean()),
                                 gap=float(v_.mean() - head[b]), p10=float(np.percentile(v_, 10)), p50=float(np.median(v_)),
                                 p90=float(np.percentile(v_, 90)), passes=abs(float(v_.mean()) - head[b]) <= TOL))
        DECT = pd.DataFrame(dec_rows)
        DECT.to_csv(os.path.join(OUT_DIR, "n9_min_sources.csv"), index=False)
        r.note("Minnesota, headline cells, by source (mean over the four views; un-aged then aged):")
        for x in DECT.itertuples():
            r.note("   %-58s %-6s mean %.2f%% (gap %+.2f) p10 %.2f p50 %.2f p90 %.2f"
                   % (x.sources, x.basis, x.mean, x.gap, x.p10, x.p50, x.p90))

        # ---- per team, per cell, and the summary --------------------------------------------------------
        cells, summ, var = [], [], []
        for t in teams:
            rs_, po_ = D[t]
            T_ = TT[t]
            W_ = wa + wb * rs_
            allv, allw, allseed, alltop6 = [], [], [], []
            for bi, b in enumerate(BASES):
                for fi, f in enumerate(FORKS):
                    for ai, a in enumerate(ALLOCS):
                        tv = T_[:, bi, fi, ai]
                        es, p6 = seeds(t, b, f, a, rs_[:, bi, fi, ai])
                        cells.append(dict(team=t, basis=b, view=f, allocator=a, point_net=point[(t, b, f, a)],
                                          title_point=float(100 * (price(t, b, f, point[(t, b, f, a)]))),
                                          title_mean=float(tv.mean()), title_p10=float(np.percentile(tv, 10)),
                                          title_p50=float(np.median(tv)), title_p90=float(np.percentile(tv, 90)),
                                          wins_mean=float(W_[:, bi, fi, ai].mean()), seed_mean=float(es.mean()), top6_mean=float(p6.mean())))
                        allv.append(tv)
                        allw.append(W_[:, bi, fi, ai])
                        allseed.append(es)
                        alltop6.append(p6)
            tv = np.concatenate(allv)
            med = np.median(tv)
            upper = tv[tv > med]
            mkt = float(market.loc[t, "market_pct"])
            q = np.percentile(tv, [10, 25, 50, 75, 90])
            w_ = np.concatenate(allw)
            s_ = np.concatenate(allseed)
            p6_ = np.concatenate(alltop6)
            summ.append(dict(team=t, market_pct=mkt, market_rank=int(market.loc[t, "market_rank"]),
                             title_mean=float(tv.mean()), title_p10=q[0], title_p25=q[1], title_p50=q[2], title_p75=q[3], title_p90=q[4],
                             breadth_ratio=float(q[4] / q[0]) if q[0] > 0 else np.nan, upside_share=float(upper.sum() / tv.sum()),
                             share_above_market=float((tv > mkt).mean()),
                             wins_mean=float(w_.mean()), wins_p10=float(np.percentile(w_, 10)), wins_p90=float(np.percentile(w_, 90)),
                             seed_p10=float(np.percentile(s_, 10)), seed_p50=float(np.median(s_)), seed_p90=float(np.percentile(s_, 90)),
                             top6_p10=float(np.percentile(p6_, 10)), top6_p90=float(np.percentile(p6_, 90))))
            # variance of title odds: between cells (and its view / basis / allocator main effects) and within cells (the draws)
            M_ = T_.mean(axis=0)
            tot = float(T_.var())
            between = float(M_.var())
            within = tot - between
            me = {"view": float(M_.mean(axis=(0, 2)).var()), "basis": float(M_.mean(axis=(1, 2)).var()),
                  "allocator": float(M_.mean(axis=(0, 1)).var())}
            var.append(dict(team=t, sd_title=np.sqrt(tot), share_within_cells=within / tot, share_between_cells=between / tot,
                            **{"share_" + k: v__ / tot for k, v__ in me.items()}))
        C = pd.DataFrame(cells)
        S2 = pd.DataFrame(summ).set_index("team")
        V = pd.DataFrame(var).set_index("team")
        C.to_csv(os.path.join(OUT_DIR, "n9_breadth_cells%s.csv" % SFX), index=False)
        S2.to_csv(os.path.join(OUT_DIR, "n9_breadth_summary%s.csv" % SFX))
        V.to_csv(os.path.join(OUT_DIR, "n9_breadth_sources%s.csv" % SFX))
        G5.to_csv(os.path.join(OUT_DIR, "n9_headline_gate%s.csv" % SFX), index=False)
        if not FORK:
            r.note("variant written with suffix %s; the doc is written by the spec run" % SFX)
            for p_ in ("n9_breadth_cells", "n9_breadth_summary", "n9_breadth_sources", "n9_headline_gate"):
                r.output(os.path.join(OUT_DIR, p_ + SFX + ".csv"))
            return
        G3.to_csv(os.path.join(OUT_DIR, "n9_seeding_share.csv"), index=False)
        np.savez_compressed(os.path.join(OUT_DIR, "n9_draws_MIN.npz"), title=TT["MIN"], net_rs=D["MIN"][0], net_po=D["MIN"][1])

        r.note("")
        r.note("BREADTH, Minnesota against the teams priced beside it (title odds in pp; 16 cells x %d draws):" % N)
        for t in NEIGHBOURS:
            x = S2.loc[t]
            r.note("  %-4s mkt %5.2f%% | mean %5.2f | p10 %5.2f p50 %5.2f p90 %5.2f | upside %3.0f%% | above mkt %3.0f%% | wins %4.1f to %4.1f | seed %.1f to %.1f | top six %3.0f%% to %3.0f%%"
                   % (t, x.market_pct, x.title_mean, x.title_p10, x.title_p50, x.title_p90, 100 * x.upside_share, 100 * x.share_above_market,
                      x.wins_p10, x.wins_p90, x.seed_p10, x.seed_p90, 100 * x.top6_p10, 100 * x.top6_p90))
        for t in NEIGHBOURS:
            v_ = V.loc[t]
            r.note("  %-4s variance: within cells (the draws) %.0f%%, between cells %.0f%% (view %.0f%%, basis %.0f%%, allocator %.0f%%), sd %.2f pp"
                   % (t, 100 * v_.share_within_cells, 100 * v_.share_between_cells, 100 * v_.share_view, 100 * v_.share_basis,
                      100 * v_.share_allocator, v_.sd_title))

        # ---- the doc ---------------------------------------------------------------------------------------
        L = ["# N9: the breadth of the odds (version 2)", "",
             "Run `%s`. PENDING: N9 does not enter the series while the headline gate (G5) fails or until Bobby decides. Design: D112 as revised by D113 in decisions.md." % r.run_id, "",
             "## Gates", "",
             "- G1 zero noise reproduces the published net: worst gap %.1e." % g1,
             "- G2 the proxy returns each team's simulated odds at its anchor: worst gap %.1e pp." % g2,
             "- G3 the seeding share reproduces C3's direct simulations: worst title gap %.3f pp, worst drop gap %.3f pp. Seeding share by view, un-aged / aged: %s."
             % (G3.gap.max(), G3.drop_gap.max(), ", ".join("%s %.2f / %.2f" % (f, S_[("unaged", f)], S_[("aged", f)]) for f in FORKS)),
             "- G4 the seed rule reproduces the published mean seed: worst gap %.3f." % g4]
        for x in G5.itertuples():
            L.append("- G5 (%s): headline %.2f%%, mean over the joint draws %.2f%%, gap %+.2f pp against a tolerance of %.2f: **%s**."
                     % (x.basis, x.headline, x.draw_mean, x.gap, TOL, "passes" if x.passes else "fails"))
        L += ["", "## Minnesota's headline cells, by source", "", "| sources | basis | mean | gap to headline | p10 | p50 | p90 |", "|---|---|---|---|---|---|---|"]
        for x in DECT.itertuples():
            L.append("| %s | %s | %.2f%% | %+.2f | %.2f | %.2f | %.2f |" % (x.sources, x.basis, x.mean, x.gap, x.p10, x.p50, x.p90))
        L += ["", "## Minnesota against the teams priced beside it", "",
              "| team | market | mean | p10 | p50 | p90 | upside share | draws above market | wins p10 to p90 | seed p10 to p90 | P(top six) p10 to p90 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for t in NEIGHBOURS:
            x = S2.loc[t]
            L.append("| %s | %.2f%% | %.2f%% | %.2f | %.2f | %.2f | %.0f%% | %.0f%% | %.1f to %.1f | %.1f to %.1f | %.0f%% to %.0f%% |"
                     % (t, x.market_pct, x.title_mean, x.title_p10, x.title_p50, x.title_p90, 100 * x.upside_share, 100 * x.share_above_market,
                        x.wins_p10, x.wins_p90, x.seed_p10, x.seed_p90, 100 * x.top6_p10, 100 * x.top6_p90))
        fo = os.path.join(OUT_DIR, "n9_breadth_summary_FORKOFF.csv")
        if os.path.exists(fo):
            SF = pd.read_csv(fo).set_index("team")
            GF = pd.read_csv(os.path.join(OUT_DIR, "n9_headline_gate_FORKOFF.csv"))
            L += ["", "**Variant: the mover order held at the primary for every team** (availability and rookie impact only). Headline gate: %s." % "; ".join(
                      "%s %.2f%% against %.2f%%, gap %+.2f, %s" % (x.basis, x.draw_mean, x.headline, x.gap, "passes" if x.passes else "fails") for x in GF.itertuples()), "",
                  "| team | market | mean | p10 | p50 | p90 | upside share | draws above market | wins p10 to p90 | seed p10 to p90 | P(top six) p10 to p90 |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
            for t in NEIGHBOURS:
                x = SF.loc[t]
                L.append("| %s | %.2f%% | %.2f%% | %.2f | %.2f | %.2f | %.0f%% | %.0f%% | %.1f to %.1f | %.1f to %.1f | %.0f%% to %.0f%% |"
                         % (t, x.market_pct, x.title_mean, x.title_p10, x.title_p50, x.title_p90, 100 * x.upside_share, 100 * x.share_above_market,
                            x.wins_p10, x.wins_p90, x.seed_p10, x.seed_p90, 100 * x.top6_p10, 100 * x.top6_p90))
        L += ["", "Upside share: the share of the mean title odds contributed by the upper half of the draws (50% would be no skew).", "",
              "## Where the breadth comes from", "", "| team | within cells (the draws) | between cells | view | basis | allocator | sd of title odds |",
              "|---|---|---|---|---|---|---|"]
        for t in NEIGHBOURS:
            v_ = V.loc[t]
            L.append("| %s | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.2f |" % (t, 100 * v_.share_within_cells, 100 * v_.share_between_cells,
                                                                               100 * v_.share_view, 100 * v_.share_basis, 100 * v_.share_allocator, v_.sd_title))
        L += ["", "## Availability, Minnesota's rotation", "", "Typical availability for rotation minutes, league-wide: %.2f of games. A player's draw enters relative to it." % typical, "",
              "| player | age | last season's share | seasons at 60% or less (of 3) | cohort n | predicted mean share | p10 | relative to typical |", "|---|---|---|---|---|---|---|---|"]
        for x in mn.sort_values("pred_mean").itertuples():
            L.append("| %s | %.0f | %.2f | %d | %d | %.2f | %.2f | %.2f |" % (x.player, x.age, x.share_prev, x.n_bad, x.cohort_n, x.pred_mean, x.pred_p10, x.relative_to_typical))
        L += ["", "## Limits", "",
              "Games share mixes injury with a coach's decision, and a season out of the NBA (overseas) reads as a season missed; Kuminga's 2025-26 and Lyles's 2025-26 are both examples. Availability is drawn independently player by player, for the regular season only; April is the fragility question (N5), and the sensitivity above shows the cost if games were missed at random through the playoffs too. The mover fork is an equal-probability choice between two orderings, not an estimate of which is right. The other teams are priced on an anchored proxy of Minnesota's f-curve. The rookie prior sd comes from one class."]
        io.open(DOC, "w", encoding="utf-8").write("\n".join(L) + "\n")
        for p in ("n9_breadth_cells.csv", "n9_breadth_summary.csv", "n9_breadth_sources.csv", "n9_availability.csv", "n9_min_sources.csv",
                  "n9_seeding_share.csv", "n9_headline_gate.csv", "n9_draws_MIN.npz"):
            r.output(os.path.join(OUT_DIR, p))
        r.output(DOC)


if __name__ == "__main__":
    main()
