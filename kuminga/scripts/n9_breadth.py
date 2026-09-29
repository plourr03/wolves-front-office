#!/usr/bin/env python3
"""N9: the breadth of the odds. How wide is the model's range for a team's title odds once
every modelling fork is allowed to vary, and how does Minnesota's range compare with the
teams the market prices beside it?

No written specification of N9 exists in the project; this is built from the components
Bobby listed (D112): four uncertainty sources, draws priced on the f-curve, conditional
title-odds percentiles, expected-wins and seed ranges, upside share, Minnesota against the
teams priced beside it, and an eleven-season proxy validation with a tendency test.

THE FOUR SOURCES. The model's forks, the things it is unsure about before a ball is
bounced, are the sources; the simulator's own season noise is NOT drawn here because the
f-curve already integrates it (the f-curve is P(title | expected net) with the simulator's
playoff-strength noise inside). The four:
  1. the impact view (consensus, RAPM, box, DARKO)
  2. the aging basis (un-aged, survivorship-corrected aged)
  3. the rotation ordering (primary mover-discounted, flat half-and-half sensitivity, D111)
  4. the minutes allocator (team-rank, pooled)
Every combination is a cell: 32 per team, equal weight. Each cell's expected net is the
pipeline's own formula, exp + beta * (rollup(minutes, impacts) - hot_baseline), with the
minutes from the named allocator on the named ordering and the impacts on the named basis.
G1: the primary cell reproduces `team_strengths_2026_27.csv` on both bases for all 30 teams.

PRICING. Minnesota's cells are priced on its own f-curve for the cell's view and basis.
Every other team is priced on an ANCHORED PROXY of that f-curve: the curve is shifted so
that it passes through the team's own simulated title odds at the team's primary cell
(log-odds shift, so probabilities stay in range) and carries Minnesota's slope from there.
It is a proxy, stated as one; the team's own f-curve would need its own 200k run.

BREADTH. Per team: the percentiles of title odds across the 32 cells, the expected-wins
range (wins = wins_a + wins_b * net, the simulator's own), the seed range across the eight
view-by-basis cells from `seed_distribution.csv` (seeding does not depend on the ordering
or the allocator in the simulator), the upside share (the share of the team's mean title
odds that the upper half of its cells contributes), the share of cells above the market
price, and the variance of expected net decomposed into the four sources' main effects.

THE ELEVEN-SEASON PROXIES. The model cannot be run on past seasons, so breadth is
bridged by observable correlates that exist for the eleven champions and the 48 top-five
non-champions: top-eight mean age (youth as upside), returning share of playoff minutes by
contract (continuity as narrowness), and the count of in-season acquisitions. Validation:
across the 30 current teams, the Spearman correlation between the model's breadth and the
same proxies computed from the projected rotations. Tendency: Mann-Whitney, champions
against the 48, two-sided, with the Bonferroni note for three tests.

    python kuminga/scripts/n9_breadth.py
"""
from __future__ import annotations

import io
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

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
ROT = os.path.join(OUT_DIR, "rotations_2026_27.csv")
MARKET = os.path.join(OUT_DIR, "market_devig_2026_27.csv")
VALUE = os.path.join(REPO, "offseason", "data", "player_value.csv")
DARKO = os.path.join(REPO, "offseason", "data", "darko-dpm-leaderboard.csv")
ROSTER = os.path.join(REPO, "kuminga", "data", "roster_snapshot_2026_27_SIM.csv")
CHAMPS = os.path.join(OUT_DIR, "c1_champions.csv")
CONTS = os.path.join(OUT_DIR, "c1_contenders.csv")
DOC = os.path.join(REPO, "kuminga", "docs", "n9_breadth.md")

FORKS = ["consensus", "rapm", "box", "darko"]
BASES = ["unaged", "aged"]
ORDERS = ["primary", "flat"]
ALLOCS = ["team-rank", "pooled"]
NEIGHBOURS = ["MIN", "DEN", "DET", "CLE", "TOR", "BOS", "MIA"]   # the 3.16% tie, plus the price above and below
LEAN_P = 0.05
P_FLOOR = 1e-5


def logit(p):
    p = np.clip(p, P_FLOOR, 1 - P_FLOOR)
    return np.log(p / (1 - p))


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def read_basis(basis):
    d = OUT_DIR if basis == "unaged" else AGED
    return (pd.read_csv(os.path.join(d, "team_strengths_2026_27.csv")),
            pd.read_csv(os.path.join(d, "sim_all30_2026_27.csv")),
            pd.read_csv(os.path.join(d, "fcurve_min.csv")),
            pd.read_csv(os.path.join(d, "seed_distribution.csv")))


def impacts_for(basis, value, darko, bio, pool):
    prev = os.environ.get(BS.AGING_ENV)
    os.environ[BS.AGING_ENV] = "1" if basis == "aged" else "0"
    try:
        imps, _ = BS.build_impacts(value, darko, bio)
        BS.add_rookie_impacts(imps, pool)
    finally:
        if prev is None:
            os.environ.pop(BS.AGING_ENV, None)
        else:
            os.environ[BS.AGING_ENV] = prev
    return imps


def main():
    with runlog.run("n9_breadth", inputs={"cells": 32, "sources": "view, basis, ordering, allocator"}) as r:
        pool = pd.read_csv(POOL)
        pool = pool[pool.scenario == "current"].copy()
        curve = pd.read_csv(CURVE, index_col=0).iloc[:, 0]
        value = pd.read_csv(VALUE)
        darko = pd.read_csv(DARKO)
        darko.columns = [c.strip().lstrip("﻿") for c in darko.columns]
        bio, _ = kfreeze.load("player_bio")
        params = E.load_e_params()
        beta, wa, wb = float(params["beta"]), float(params["wins_a"]), float(params["wins_b"])
        market = pd.read_csv(MARKET).set_index("team_abbr")
        teams = sorted(pool.team_abbr.unique())
        assert len(teams) == 30, len(teams)

        data = {b: read_basis(b) for b in BASES}
        imps = {b: impacts_for(b, value, darko, bio, pool) for b in BASES}

        # ---- minutes per team, ordering, allocator (shared by both bases) ------------
        minutes = {}
        for t in teams:
            g0 = pool[pool.team_abbr == t].copy()
            for o in ORDERS:
                g = g0.copy()
                if o == "flat":
                    g["rank_score"] = g["rank_score_flat"]
                minutes[(t, o, "team-rank")] = rotation.allocate(g, curve, use_ceiling=True)
                minutes[(t, o, "pooled")] = rotation.allocate_pooled(g, curve)

        # ---- the cells ------------------------------------------------------------------
        rows = []
        g1_worst = 0.0
        for b in BASES:
            st, sim, fc, seeds = data[b]
            for t in teams:
                for f in FORKS:
                    row = st[(st.fork == f) & (st.team_abbr == t)].iloc[0]
                    exp_, hb = float(row.exp_2026_27), float(row.hot_baseline)
                    for o in ORDERS:
                        for a in ALLOCS:
                            net = exp_ + beta * (A.rollup(minutes[(t, o, a)], imps[b][f], "rs")["net"] - hb)
                            if o == "primary" and a == "team-rank":
                                g1_worst = max(g1_worst, abs(net - float(row.net_current)))
                            rows.append(dict(team=t, basis=b, view=f, ordering=o, allocator=a, net=net))
        cells = pd.DataFrame(rows)
        r.note("G1: the primary cell reproduces team_strengths net_current, worst gap %.2e (both bases, 30 teams)" % g1_worst)
        if g1_worst > 1e-6:
            raise RuntimeError("G1 failed: primary cell does not reproduce the published net (%.2e)" % g1_worst)

        # ---- pricing --------------------------------------------------------------------
        def fcurve(b, f):
            g = data[b][2]
            g = g[g.fork == f].sort_values("min_net")
            return g.min_net.to_numpy(float), g.title.to_numpy(float)

        def price_min(b, f, net):
            x, y = fcurve(b, f)
            return float(np.interp(net, x, y))

        anchors = {}
        for b in BASES:
            st, sim, _, _ = data[b]
            for t in teams:
                for f in FORKS:
                    sr = sim[(sim.fork == f) & (sim.team_abbr == t)].iloc[0]
                    anchors[(b, t, f)] = (float(sr.net_current), float(sr.title_current))

        def price(t, b, f, net):
            if t == "MIN":
                return price_min(b, f, net)
            net_t, title_t = anchors[(b, t, f)]
            net_m, _ = anchors[(b, "MIN", f)]
            shift = net_m - net_t
            c = logit(title_t) - logit(price_min(b, f, net_t + shift))
            return float(expit(logit(price_min(b, f, net + shift)) + c))

        cells["title"] = [100 * price(x.team, x.basis, x.view, x.net) for x in cells.itertuples()]
        cells["wins"] = wa + wb * cells.net
        # the anchor check: the primary cell of every team prices to its own simulated odds
        chk = cells[(cells.ordering == "primary") & (cells.allocator == "team-rank")].copy()
        chk["sim_title"] = [100 * anchors[(x.basis, x.team, x.view)][1] for x in chk.itertuples()]
        gap = float((chk.title - chk.sim_title).abs().max())
        r.note("G2: at the anchor the proxy returns the simulated odds, worst gap %.2e pp; Minnesota's own f-curve "
               "against its direct simulation, worst gap %.3f pp (interpolation only)"
               % (float((chk[chk.team != "MIN"].title - chk[chk.team != "MIN"].sim_title).abs().max()),
                  float((chk[chk.team == "MIN"].title - chk[chk.team == "MIN"].sim_title).abs().max())))
        if gap > 0.2:
            raise RuntimeError("G2 failed: proxy gap %.3f pp at an anchor" % gap)
        cells.to_csv(os.path.join(OUT_DIR, "n9_breadth_cells.csv"), index=False)

        # ---- per-team breadth --------------------------------------------------------------
        def seed_range(t):
            out = []
            for b in BASES:
                sd = data[b][3]
                sd = sd[(sd.field == "current") & (sd.team_abbr == t)]
                for f in FORKS:
                    x = sd[sd.fork == f]
                    if len(x):
                        out.append((float(x.mean_seed.iloc[0]), float(x.p_playoff_top6.iloc[0])))
            return out

        summ, srcs = [], []
        for t in teams:
            c = cells[cells.team == t]
            tt = c.title.to_numpy(float)
            q = np.percentile(tt, [10, 25, 50, 75, 90])
            med = np.median(tt)
            upper = tt[tt > med] if (tt > med).any() else tt[tt >= med]
            upside = float(upper.sum() / tt.sum()) if tt.sum() > 0 else np.nan
            mkt = float(market.loc[t, "market_pct"]) if t in market.index else np.nan
            sr = seed_range(t)
            w = c.wins.to_numpy(float)
            best = c.loc[c.title.idxmax()]
            worst = c.loc[c.title.idxmin()]
            summ.append(dict(
                team=t, market_pct=mkt, market_rank=int(market.loc[t, "market_rank"]) if t in market.index else np.nan,
                title_mean=float(tt.mean()), title_p10=q[0], title_p25=q[1], title_p50=q[2], title_p75=q[3], title_p90=q[4],
                title_min=float(tt.min()), title_max=float(tt.max()),
                breadth_ratio=float(q[4] / q[0]) if q[0] > 0 else np.nan,
                breadth_net=float(np.percentile(c.net, 90) - np.percentile(c.net, 10)),
                upside_share=upside, cells_above_market=float((tt > mkt).mean()) if not np.isnan(mkt) else np.nan,
                wins_mean=float(w.mean()), wins_p10=float(np.percentile(w, 10)), wins_p90=float(np.percentile(w, 90)),
                seed_mean_lo=min(s for s, _ in sr) if sr else np.nan, seed_mean_hi=max(s for s, _ in sr) if sr else np.nan,
                p_top6_lo=min(p for _, p in sr) if sr else np.nan, p_top6_hi=max(p for _, p in sr) if sr else np.nan,
                best_cell="%s / %s / %s / %s" % (best.view, best.basis, best.ordering, best.allocator),
                worst_cell="%s / %s / %s / %s" % (worst.view, worst.basis, worst.ordering, worst.allocator)))
            # variance of expected net by source: main effects, equal-weight cells
            tot = float(c.net.var(ddof=0))
            shares = {}
            for src in ("view", "basis", "ordering", "allocator"):
                shares[src] = float(c.groupby(src).net.mean().var(ddof=0) / tot) if tot > 0 else np.nan
            srcs.append(dict(team=t, var_net=tot, **{"share_" + k: v for k, v in shares.items()},
                             share_interaction=(1 - sum(shares.values())) if tot > 0 else np.nan))
        S = pd.DataFrame(summ).set_index("team")
        V = pd.DataFrame(srcs).set_index("team")
        S.to_csv(os.path.join(OUT_DIR, "n9_breadth_summary.csv"))
        V.to_csv(os.path.join(OUT_DIR, "n9_breadth_sources.csv"))

        r.note("")
        r.note("BREADTH, Minnesota against the teams priced beside it (title odds in pp, 32 cells each):")
        r.note("  %-4s %7s %7s | %6s %6s %6s %6s %6s | %6s %6s | %5s %5s | %s"
               % ("team", "market", "mean", "p10", "p25", "p50", "p75", "p90", "upside", ">mkt", "w_p10", "w_p90", "seed mean range"))
        for t in NEIGHBOURS:
            x = S.loc[t]
            r.note("  %-4s %6.2f%% %6.2f%% | %6.2f %6.2f %6.2f %6.2f %6.2f | %5.0f%% %5.0f%% | %5.1f %5.1f | %.1f to %.1f (top six %.0f%% to %.0f%%)"
                   % (t, x.market_pct, x.title_mean, x.title_p10, x.title_p25, x.title_p50, x.title_p75, x.title_p90,
                      100 * x.upside_share, 100 * x.cells_above_market, x.wins_p10, x.wins_p90, x.seed_mean_lo, x.seed_mean_hi,
                      100 * x.p_top6_lo, 100 * x.p_top6_hi))
        r.note("  variance of expected net by source (share of the 32-cell variance):")
        for t in NEIGHBOURS:
            v = V.loc[t]
            r.note("  %-4s view %.0f%%  basis %.0f%%  ordering %.0f%%  allocator %.0f%%  interaction %.0f%%  (sd of net %.2f)"
                   % (t, 100 * v.share_view, 100 * v.share_basis, 100 * v.share_ordering, 100 * v.share_allocator,
                      100 * v.share_interaction, np.sqrt(v.var_net)))

        # ---- the proxies, current season ------------------------------------------------
        rot = pd.read_csv(ROT)
        rot = rot[rot.scenario == "current"]
        roster = pd.read_csv(ROSTER)
        age = roster.dropna(subset=["nba_player_id"]).assign(pid=lambda d: d.nba_player_id.astype(int)).set_index("pid").age
        pool_pid = pool.dropna(subset=["player_id"]).assign(pid=lambda d: d.player_id.astype(int)).set_index("pid")
        prox = []
        for t in teams:
            g = rot[rot.team_abbr == t].sort_values("mpg", ascending=False)
            top8 = g.head(8)
            ages = [age.get(int(p), np.nan) for p in top8.player_id]
            mv = [bool(pool_pid.moved_teams.get(int(p), False)) for p in g.player_id]
            ret_share = float(g.mpg[~np.array(mv)].sum() / g.mpg.sum()) if len(g) else np.nan
            prox.append(dict(team=t, top8_mean_age=float(np.nanmean(ages)), returning_minutes_share=ret_share,
                             n_movers_in_rotation=int(sum(mv))))
        PX = pd.DataFrame(prox).set_index("team")
        S2 = S.join(PX).join(V[["var_net"]])
        S2.to_csv(os.path.join(OUT_DIR, "n9_breadth_summary.csv"))

        val = []
        live = S2[S2.title_mean >= 0.5]
        for measure, col in (("breadth of net (p90 - p10)", "breadth_net"), ("upside share", "upside_share"),
                             ("breadth of title odds (p90 / p10, teams at 0.5% or more)", "breadth_ratio")):
            frame = S2 if col != "breadth_ratio" else live
            for pname, pcol in (("top-eight mean age", "top8_mean_age"), ("returning minutes share", "returning_minutes_share"),
                                ("movers in the rotation", "n_movers_in_rotation")):
                x = frame[[col, pcol]].dropna()
                rho, p = spearmanr(x[col], x[pcol])
                val.append(dict(measure=measure, proxy=pname, n=len(x), spearman=float(rho), p_value=float(p)))
        VAL = pd.DataFrame(val)
        VAL.to_csv(os.path.join(OUT_DIR, "n9_proxy_validation.csv"), index=False)
        r.note("")
        r.note("VALIDATION, 2026-27: does the model's breadth track the proxies across the 30 teams? (Spearman)")
        for x in VAL.itertuples():
            r.note("  %-58s vs %-24s n=%2d rho=%+.2f p=%.3f" % (x.measure, x.proxy, x.n, x.spearman, x.p_value))

        # ---- the proxies, eleven seasons: tendency ----------------------------------------
        ch = pd.read_csv(CHAMPS)
        co = pd.read_csv(CONTS)
        for d in (ch, co):
            d["n_in_season_moves"] = d.in_season_moves.map(lambda s: 0 if str(s).strip() == "none" else str(s).count(";") + 1)
        tests = []
        for pname, pcol in (("top-eight mean age", "top8_mean_age"), ("returning playoff-minutes share, by contract", "returning_po_minutes_share_contract"),
                            ("in-season acquisitions among the eight", "n_in_season_moves")):
            a, b_ = ch[pcol].dropna().astype(float), co[pcol].dropna().astype(float)
            u, p = mannwhitneyu(a, b_, alternative="two-sided")
            tests.append(dict(proxy=pname, n_champions=len(a), n_contenders=len(b_), champion_median=float(a.median()),
                              contender_median=float(b_.median()), u=float(u), p_value=float(p), leans=bool(p < LEAN_P),
                              leans_bonferroni=bool(p < LEAN_P / 3)))
        T = pd.DataFrame(tests)
        T.to_csv(os.path.join(OUT_DIR, "n9_proxy_tendency.csv"), index=False)
        hist = pd.concat([ch.assign(group="champion"), co.assign(group="contender")])[
            ["season", "team", "group", "top8_mean_age", "returning_po_minutes_share_contract", "n_in_season_moves", "preseason_title_odds"]]
        hist.to_csv(os.path.join(OUT_DIR, "n9_proxies_history.csv"), index=False)
        r.note("")
        r.note("TENDENCY, eleven seasons: champions (n=%d) against the top-five non-champions (n=%d), Mann-Whitney two-sided, lean at p < %.2f (Bonferroni for three tests: %.3f)"
               % (len(ch), len(co), LEAN_P, LEAN_P / 3))
        for x in T.itertuples():
            r.note("  %-46s champions %.2f  contenders %.2f  p=%.3f  %s" % (x.proxy, x.champion_median, x.contender_median, x.p_value,
                                                                              "LEANS" if x.leans else "no lean"))
        # Minnesota on the proxies
        mn = S2.loc["MIN"]
        r.note("")
        r.note("MINNESOTA on the proxies: top-eight mean age %.1f, returning minutes share %.0f%%, movers in the rotation %d; "
               "against the eleven champions' medians %.1f and %.0f%%"
               % (mn.top8_mean_age, 100 * mn.returning_minutes_share, mn.n_movers_in_rotation,
                  T.champion_median.iloc[0], 100 * T.champion_median.iloc[1]))

        # ---- the doc -------------------------------------------------------------------------
        L = ["# N9: the breadth of the odds", "",
             "Run `%s`. No written N9 specification exists in the project; the design is D112 in decisions.md, built from the listed components. Every figure here is in `n9_breadth_summary.csv`, `n9_breadth_cells.csv`, `n9_breadth_sources.csv`, `n9_proxy_validation.csv`, `n9_proxy_tendency.csv` and `n9_proxies_history.csv`." % r.run_id, "",
             "## The four sources and the cells", "",
             "Each team has 32 cells: four impact views, two aging bases, two rotation orderings (the primary mover-discounted order and the flat half-and-half sensitivity), two minutes allocators (team-rank and pooled). A cell's expected net is the pipeline's own formula; the primary cell reproduces the published strengths on both bases (G1). Minnesota's cells are priced on its own f-curve. Every other team is priced on an anchored proxy: Minnesota's f-curve shifted in log-odds to pass through that team's own simulated title odds at its primary cell (G2). The simulator's season noise is not drawn again, because the f-curve already integrates it.", "",
             "## Minnesota against the teams priced beside it", "",
             "| team | market | mean | p10 | p25 | p50 | p75 | p90 | upside share | cells above market | wins p10 to p90 | mean seed range | P(top six) range |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for t in NEIGHBOURS:
            x = S2.loc[t]
            L.append("| %s | %.2f%% | %.2f%% | %.2f | %.2f | %.2f | %.2f | %.2f | %.0f%% | %.0f%% | %.1f to %.1f | %.1f to %.1f | %.0f%% to %.0f%% |"
                     % (t, x.market_pct, x.title_mean, x.title_p10, x.title_p25, x.title_p50, x.title_p75, x.title_p90, 100 * x.upside_share,
                        100 * x.cells_above_market, x.wins_p10, x.wins_p90, x.seed_mean_lo, x.seed_mean_hi, 100 * x.p_top6_lo, 100 * x.p_top6_hi))
        L += ["", "Upside share is the share of a team's mean title odds contributed by the upper half of its 32 cells; 50% would mean no upside skew at all.", "",
              "## Where the breadth comes from", "", "| team | view | basis | ordering | allocator | interaction | sd of expected net |", "|---|---|---|---|---|---|---|"]
        for t in NEIGHBOURS:
            v = V.loc[t]
            L.append("| %s | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.2f |" % (t, 100 * v.share_view, 100 * v.share_basis, 100 * v.share_ordering,
                                                                                   100 * v.share_allocator, 100 * v.share_interaction, np.sqrt(v.var_net)))
        L += ["", "## The proxies", "",
              "The model cannot be run on past seasons, so breadth is bridged by correlates that exist for the eleven champions and the 48 top-five non-champions: top-eight mean age, returning share of playoff minutes by contract, and in-season acquisitions among the eight.", "",
              "**Validation on 2026-27** (Spearman across the 30 teams; the odds ratio only for teams the model has at 0.5% or more):", "",
              "| measure | proxy | n | rho | p |", "|---|---|---|---|---|"]
        for x in VAL.itertuples():
            L.append("| %s | %s | %d | %+.2f | %.3f |" % (x.measure, x.proxy, x.n, x.spearman, x.p_value))
        L += ["", "**Tendency on the eleven seasons** (Mann-Whitney, two-sided; lean at p below %.2f, Bonferroni for three tests %.3f):" % (LEAN_P, LEAN_P / 3), "",
              "| proxy | champions' median | contenders' median | p | leans |", "|---|---|---|---|---|"]
        for x in T.itertuples():
            L.append("| %s | %.2f | %.2f | %.3f | %s |" % (x.proxy, x.champion_median, x.contender_median, x.p_value, "yes" if x.leans else "no"))
        L += ["", "Minnesota on the proxies: top-eight mean age %.1f, returning minutes share %.0f%%, %d movers in the ten." % (mn.top8_mean_age, 100 * mn.returning_minutes_share, mn.n_movers_in_rotation), "",
              "## Limits", "",
              "The other teams' pricing is a proxy anchored on one simulated point per view and basis; Minnesota's own f-curve slope is assumed to carry. The four sources are the model's forks, equally weighted; nothing here says one view or basis is more likely than another. The historical proxies are correlates of breadth, not breadth: a team can be young and narrow, or old and wide."]
        io.open(DOC, "w", encoding="utf-8").write("\n".join(L) + "\n")
        for p in ("n9_breadth_cells.csv", "n9_breadth_summary.csv", "n9_breadth_sources.csv", "n9_proxy_validation.csv",
                  "n9_proxy_tendency.csv", "n9_proxies_history.csv"):
            r.output(os.path.join(OUT_DIR, p))
        r.output(DOC)


if __name__ == "__main__":
    main()
