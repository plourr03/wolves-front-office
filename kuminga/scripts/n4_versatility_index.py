#!/usr/bin/env python3
"""N4: versatility index. How much does a team's series win probability swing across the
contender field, and is any of that swing about matchups?

PART 1, AS SPECIFIED. From the M2 series model, each team's probability of winning a
series against each of the eight contenders (the top eight by modelled title odds, league
wide; a contender is scored against the other seven), per impact view. Spread is the
standard deviation and the range of those probabilities. All 30 ranked. Minnesota's best
and worst matchups, with the four-view band.

WHAT THAT INDEX CAN AND CANNOT MEAN, stated before the numbers. M2 left the style overlay
off because it failed held-out validation, so the series model prices a series from the
net-rating gap and home court alone. Every team faces the same eight opponents. So a
team's spread is fixed by its own net rating: teams near the contenders' level sit on the
steep middle of the curve and swing the most, and very strong or very weak teams sit on
the flat ends and swing the least. Under this model the index measures POSITION ON THE
CURVE, not versatility. The script shows that as a number (for the teams outside the field,
the rank correlation between spread and own net rating) rather than asserting it.

PART 2, THE OBSERVED CHECK. If matchup-specific effects exist (a team that plays one
opponent better than the net ratings say, repeatably), that is the versatility the model
cannot see. Test, regular seasons 2013-14 to 2025-26, model free:
  1. For every game, the residual margin after home court and the two teams' net ratings,
     fitted per season, each net computed EXCLUDING the games between that pair, so a
     pair's own results do not leak into its expectation.
  2. For every team pair with two or more games in a season, the mean cross-product of
     two DIFFERENT games' residuals estimates the variance of the TRUE pair effect,
     because independent game noise contributes nothing to it. Its square root is the
     standard deviation of real matchup effects in points per game, bootstrapped over
     pair-seasons. (A first version split each pair's meetings into two halves; that
     throws information away and left the upper bound too loose to say anything, so the
     halves are kept only as a readable check.)
  3. The same on every regular season from 1997-98, as a precision check.
  4. Team level: does a team's spread of results across opponents repeat from one season
     to the next, and if so, is that versatility or just volatility (teams whose games
     swing more have a wider spread against every opponent alike)?
The point estimate and the upper bound are put on the series scale with the sim's resolver.

INPUTS. `outputs/preaging/` strengths and simulation, the un-aged primary. The chain
refreshed that folder at the end of its un-aged leg, after the D70 fixes; the script
checks it against the un-aged snapshot before using it.

    python kuminga/scripts/n4_versatility_index.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import runlog  # noqa: E402
from lib import db              # noqa: E402
import bracket_sim as E         # noqa: E402
import series_resolver as D     # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
PRE = os.path.join(OUT_DIR, "preaging")
SNAP = os.path.join(OUT_DIR, "_restore_unaged")
STR = os.path.join(PRE, "team_strengths_2026_27.csv")
SIM = os.path.join(PRE, "sim_all30_2026_27.csv")
OUT_IDX = os.path.join(OUT_DIR, "n4_versatility_index.csv")
OUT_MIN = os.path.join(OUT_DIR, "n4_min_matchups.csv")
OUT_REP = os.path.join(OUT_DIR, "n4_matchup_repeatability.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "n4_versatility_index.md")

TEAM = "MIN"
FORKS = ["consensus", "rapm", "box", "darko"]
N_FIELD = 8
FIRST, LAST = 2013, 2025
EXT_FIRST = 1997          # precision check: every regular season in nba_games
BOOT = 2000
SEED = 20260916


def season_label(y):
    return "%d-%02d" % (y, (y + 1) % 100)


def main():
    with runlog.run("n4_versatility_index",
                    inputs={"strengths": STR, "n_field": N_FIELD, "overlay": "off (M2)",
                            "repeatability_seasons": [season_label(FIRST),
                                                      season_label(LAST)],
                            "boot": BOOT, "seed": SEED}) as r:
        st = pd.read_csv(STR)
        if os.path.exists(os.path.join(SNAP, "team_strengths_2026_27.csv")):
            sn = pd.read_csv(os.path.join(SNAP, "team_strengths_2026_27.csv"))
            chk = st.merge(sn, on=["fork", "team_abbr"], suffixes=("", "_snap"))
            gap = float((chk.net_current - chk.net_current_snap).abs().max())
            r.note("gate: preaging strengths vs the chain's un-aged snapshot, max abs net "
                   "difference %.9f over %d rows" % (gap, len(chk)))
            if gap > 1e-9:
                raise RuntimeError("preaging strengths are not the post-D70 un-aged set")
        sim = pd.read_csv(SIM)
        tit = sim.groupby("team_abbr").title_current.mean().sort_values(ascending=False)
        field = list(tit.index[:N_FIELD])
        r.note("contender field, top %d by modelled title odds (mean of four views): %s"
               % (N_FIELD, ", ".join("%s %.1f%%" % (t, 100 * tit[t]) for t in field)))

        # ================= PART 1: the index as specified ===========================
        rows, pmat = [], []
        for f in FORKS:
            s = st[st.fork == f]
            strengths = {x.team_abbr: {"net": float(x.net_current), "munc": float(x.munc),
                                       "conf": x.conf, "profile": None}
                         for _, x in s.iterrows()}
            for t in strengths:
                res = E.conditional_series(t, strengths, use_overlay=False)
                ps = np.array([res[o] for o in field if o != t])
                rows.append(dict(fork=f, team=t, conf=strengths[t]["conf"],
                                 net=strengths[t]["net"], n_opp=len(ps),
                                 sd=float(ps.std(ddof=0)), rng=float(ps.max() - ps.min()),
                                 mean_p=float(ps.mean())))
                for o in field:
                    if o != t:
                        pmat.append(dict(fork=f, team=t, opp=o, p=float(res[o])))
        V = pd.DataFrame(rows)
        P = pd.DataFrame(pmat)

        # how much of the spread is just the team's own net rating. Outside the field
        # every team faces the SAME eight opponents, so within a view its spread must be
        # a fixed function of its own net; all of them sit below the field, where that
        # function rises with net, so the rank correlation should be exactly 1.
        r2 = {}
        for f in FORKS:
            v = V[(V.fork == f) & ~V.team.isin(field)]
            r2[f] = float(v.sd.rank().corr(v.net.rank()))
        r.note("rank correlation of spread with own net rating, the %d teams outside the "
               "field, per view: %s" % (30 - N_FIELD, ", ".join("%s %.3f" % (f, r2[f])
                                                              for f in FORKS)))

        idx = V.groupby(["team", "conf"]).agg(
            net_mean=("net", "mean"), sd_mean=("sd", "mean"), sd_lo=("sd", "min"),
            sd_hi=("sd", "max"), range_mean=("rng", "mean"), range_lo=("rng", "min"),
            range_hi=("rng", "max"), mean_p=("mean_p", "mean"),
            n_opp=("n_opp", "first")).reset_index()
        idx["rank"] = idx.sd_mean.rank(ascending=False, method="min").astype(int)
        idx["in_field"] = idx.team.isin(field)
        field_net = V[V.team.isin(field)].groupby("fork").net.mean()
        idx["net_gap_to_field"] = idx.team.map(
            V.assign(g=V.net - V.fork.map(field_net)).groupby("team").g.mean())
        idx = idx.sort_values("rank")
        idx.to_csv(OUT_IDX, index=False)
        r.note("")
        r.note("VERSATILITY INDEX as specified (sd of series win probability across the "
               "field; four-view band):")
        for _, x in idx.iterrows():
            r.note("  %2d %-4s net %+6.2f (gap to field %+6.2f) | sd %.3f [%.3f, %.3f] | "
                   "range %.3f | mean P %.3f%s"
                   % (x["rank"], x.team, x.net_mean, x.net_gap_to_field, x.sd_mean, x.sd_lo,
                      x.sd_hi, x.range_mean, x.mean_p, "  (field)" if x.in_field else ""))

        mp = P[P.team == TEAM].groupby("opp").p.agg(["mean", "min", "max"]).reset_index()
        mp = mp.sort_values("mean", ascending=False)
        opp_net = V[V.team.isin(field)].groupby("team").net.mean()
        mp["opp_net_mean"] = mp.opp.map(opp_net)
        mp.to_csv(OUT_MIN, index=False)
        r.note("")
        r.note("MINNESOTA against the field (P wins series, four-view band):")
        for _, x in mp.iterrows():
            r.note("  %-4s %.3f [%.3f, %.3f]  opponent net %+.2f"
                   % (x.opp, x["mean"], x["min"], x["max"], x.opp_net_mean))

        # ================= PART 2: is there any repeatable matchup effect? ============
        def matchup_frame(first, last):
            ids = tuple(20000 + y for y in range(first, last + 1))
            g = db.query("""
                select game_id, season_id, game_date, team_abbreviation as team, matchup,
                       plus_minus
                from nba.nba_games where season_id in %(i)s
            """, {"i": ids})
            g["plus_minus"] = pd.to_numeric(g.plus_minus, errors="coerce")
            g["season"] = pd.to_numeric(g.season_id).map(
                {20000 + y: season_label(y) for y in range(first, last + 1)})
            g["home"] = (~g.matchup.str.contains("@")).astype(int)
            g = g.drop_duplicates(["game_id", "team"]).dropna(subset=["plus_minus"])
            opp = g[["game_id", "team"]].rename(columns={"team": "opp"})
            m = g.merge(opp, on="game_id")
            m = m[m.team != m.opp].copy()
            m = m[m.team < m.opp].copy()          # one row per game
            m["y"] = m.plus_minus.astype(float)
            m["h"] = np.where(m.home == 1, 1.0, -1.0)
            both = pd.concat([
                m[["season", "team", "opp", "y"]].rename(columns={"team": "t", "opp": "o"}),
                m[["season", "opp", "team", "y"]].rename(columns={"opp": "t", "team": "o"})
                .assign(y=lambda d: -d.y)])
            tot = both.groupby(["season", "t"]).y.agg(["sum", "count"])
            pr_ = both.groupby(["season", "t", "o"]).y.agg(["sum", "count"])
            keys = m[["season", "team", "opp"]].drop_duplicates()
            k_t = keys.merge(tot.reset_index().rename(columns={"t": "team"}),
                             on=["season", "team"])
            k_t = k_t.merge(pr_.reset_index().rename(
                columns={"t": "team", "o": "opp", "sum": "psum", "count": "pcnt"}),
                on=["season", "team", "opp"])
            k_t["net_t"] = (k_t["sum"] - k_t.psum) / (k_t["count"] - k_t.pcnt)
            k_o = keys.merge(tot.reset_index().rename(columns={"t": "opp"}),
                             on=["season", "opp"])
            k_o = k_o.merge(pr_.reset_index().rename(
                columns={"t": "opp", "o": "team", "sum": "psum", "count": "pcnt"}),
                on=["season", "team", "opp"])
            k_o["net_o"] = (k_o["sum"] - k_o.psum) / (k_o["count"] - k_o.pcnt)
            m = m.merge(k_t[["season", "team", "opp", "net_t"]],
                        on=["season", "team", "opp"])
            m = m.merge(k_o[["season", "team", "opp", "net_o"]],
                        on=["season", "team", "opp"])
            m["dnet"] = m.net_t - m.net_o
            m["resid"] = np.nan
            fits = []
            for s_, d in m.groupby("season"):
                X = np.column_stack([d.h, d.dnet])
                b, *_ = np.linalg.lstsq(X, d.y.to_numpy(float), rcond=None)
                m.loc[d.index, "resid"] = d.y - X @ b
                fits.append((s_, b[0], b[1]))
            return m, fits

        def moment(m, rng, boot):
            """Variance of the true pair effect: mean cross-product of two different
            games' residuals within the same pair-season (independent noise has zero
            expected cross-product). Bootstrap over pair-seasons."""
            pr = m.groupby(["season", "team", "opp"]).resid.agg(
                S="sum", Q=lambda v: float((v ** 2).sum()), n="size")
            pr = pr[pr.n >= 2]
            num = (pr.S ** 2 - pr.Q).to_numpy()
            den = (pr.n * (pr.n - 1)).to_numpy().astype(float)
            est = float(num.sum() / den.sum())
            bs = []
            for _ in range(boot):
                ix = rng.integers(0, len(num), len(num))
                bs.append(num[ix].sum() / den[ix].sum())
            lo_, hi_ = np.percentile(bs, [2.5, 97.5])
            return est, float(lo_), float(hi_), len(pr)

        rng = np.random.default_rng(SEED)
        results = {}
        for lab, (f0, f1) in (("primary", (FIRST, LAST)), ("extended", (EXT_FIRST, LAST))):
            m, fits = matchup_frame(f0, f1)
            var, lo_v, hi_v, npairs = moment(m, rng, BOOT)
            sd_pt, sd_up = float(np.sqrt(max(var, 0))), float(np.sqrt(max(hi_v, 0)))
            results[lab] = dict(window="%s to %s" % (season_label(f0), season_label(f1)),
                                games=len(m), pair_seasons=npairs,
                                resid_sd=float(m.resid.std()), var=var, var_lo=lo_v,
                                var_hi=hi_v, sd_true=sd_pt, sd_upper95=sd_up,
                                home_mean=float(np.mean([x[1] for x in fits])),
                                slope_mean=float(np.mean([x[2] for x in fits])))
            r.note("")
            r.note("PART 2 %s (%s): %d games, %d pair-seasons | per-season fits, home "
                   "%+.2f and %.3f per net point on average | residual SD %.2f"
                   % (lab, results[lab]["window"], len(m), npairs,
                      results[lab]["home_mean"], results[lab]["slope_mean"],
                      results[lab]["resid_sd"]))
            r.note("  variance of TRUE pair effect %.3f [%.3f, %.3f] -> SD %.2f pts/game, "
                   "upper 95%% %.2f" % (var, lo_v, hi_v, sd_pt, sd_up))
            if lab == "primary":
                mp_ = m
        m = mp_

        # the readable version: halves of each pair's meetings
        m = m.sort_values(["season", "team", "opp", "game_date", "game_id"])
        m["k"] = m.groupby(["season", "team", "opp"]).cumcount()
        m["half"] = m.k % 2
        hh = m.groupby(["season", "team", "opp", "half"]).resid.mean().unstack("half")
        hh = hh.dropna()
        half_corr = float(np.corrcoef(hh[0], hh[1])[0, 1])
        r.note("  readable check, pair residual in alternate halves of meetings: corr "
               "%+.3f over %d pair-seasons" % (half_corr, len(hh)))

        # on the series scale, with the sim's own resolver, at an even matchup
        pri, ext = results["primary"], results["extended"]
        tight = min(pri["sd_upper95"], ext["sd_upper95"])
        p_even = D.series_win_prob(0.0, 0.0, True)
        p_pt = D.series_win_prob(ext["sd_true"], 0.0, True)
        p_pt_pri = D.series_win_prob(pri["sd_true"], 0.0, True)
        p_up = D.series_win_prob(tight, 0.0, True)
        r.note("  on the series scale (even teams, home court): point estimate moves P from "
               "%.3f to %.3f; the tighter upper bound (%.2f) moves it to %.3f"
               % (p_even, p_pt, tight, p_up))

        # CONFOUND CHECK on the team-level repeat: volatility versus versatility.
        # A team's spread of results across opponents mixes two things: how swingy its
        # games are (game-to-game volatility, which inflates every opponent's average
        # alike) and genuine opponent-specific effects. Split them per team-season.
        tv = pd.concat([
            m[["season", "team", "opp", "resid"]],
            m[["season", "opp", "team", "resid"]].rename(
                columns={"opp": "team", "team": "opp"}).assign(resid=lambda d: -d.resid)])
        order = [season_label(y) for y in range(FIRST, LAST + 1)]
        nxt = {order[i]: order[i + 1] for i in range(len(order) - 1)}
        per = []
        for (s_, t_), d in tv.groupby(["season", "team"]):
            op = d.groupby("opp").resid.agg(S="sum", Q=lambda v: float((v ** 2).sum()),
                                            n="size", mean="mean")
            op2 = op[op.n >= 2]
            per.append(dict(season=s_, team=t_, spread=float(op["mean"].std()),
                            volatility=float(d.resid.std()),
                            true_var=float((op2.S ** 2 - op2.Q).sum()
                                           / (op2.n * (op2.n - 1)).sum())))
        per = pd.DataFrame(per)
        per["season_next"] = per.season.map(nxt)
        yy = per.merge(per[["season", "team", "spread", "volatility", "true_var"]].rename(
            columns={"season": "season_next", "spread": "spread_n",
                     "volatility": "volatility_n", "true_var": "true_var_n"}),
            on=["season_next", "team"])
        c_spread = float(yy.spread.corr(yy.spread_n))
        c_vol = float(yy.volatility.corr(yy.volatility_n))
        c_true = float(yy.true_var.corr(yy.true_var_n))
        c_sv = float(per.spread.corr(per.volatility))
        # spread with volatility partialled out, season to season
        bsv = np.polyfit(per.volatility, per.spread, 1)
        per["spread_resid"] = per.spread - np.polyval(bsv, per.volatility)
        yy = yy.merge(per[["season", "team", "spread_resid"]], on=["season", "team"])
        yy = yy.merge(per[["season", "team", "spread_resid"]].rename(
            columns={"season": "season_next", "spread_resid": "spread_resid_n"}),
            on=["season_next", "team"])
        c_part = float(yy.spread_resid.corr(yy.spread_resid_n))
        r.note("  team level, season to next over %d pairs: spread %+.3f | volatility "
               "%+.3f | spread with volatility removed %+.3f | team's own true-matchup "
               "variance estimate %+.3f | spread vs volatility same season %+.3f"
               % (len(yy), c_spread, c_vol, c_part, c_true, c_sv))

        rep = pd.DataFrame([dict(
            primary_window=pri["window"], primary_games=pri["games"],
            primary_pair_seasons=pri["pair_seasons"], resid_sd=pri["resid_sd"],
            primary_var=pri["var"], primary_var_lo=pri["var_lo"],
            primary_var_hi=pri["var_hi"], primary_sd_true=pri["sd_true"],
            primary_sd_upper95=pri["sd_upper95"],
            extended_window=ext["window"], extended_games=ext["games"],
            extended_pair_seasons=ext["pair_seasons"], extended_var=ext["var"],
            extended_var_lo=ext["var_lo"], extended_var_hi=ext["var_hi"],
            extended_sd_true=ext["sd_true"], extended_sd_upper95=ext["sd_upper95"],
            half_corr=half_corr, half_pairs=len(hh),
            p_series_even=p_even, p_series_point=p_pt, p_series_point_primary=p_pt_pri,
            p_series_upper=p_up,
            upper_used=tight, team_pairs=len(yy), team_spread_year_corr=c_spread,
            team_volatility_year_corr=c_vol, team_spread_net_of_vol_year_corr=c_part,
            team_true_var_year_corr=c_true, spread_vs_volatility=c_sv,
            spread_net_rankcorr_min=min(r2.values()))])
        rep.to_csv(OUT_REP, index=False)

        r.output(OUT_IDX, rows=len(idx))
        r.output(OUT_MIN, rows=len(mp))
        r.output(OUT_REP, rows=len(rep))
        write_doc(r, idx, mp, rep.iloc[0], field, tit, r2)
        r.output(OUT_MD)


def write_doc(r, idx, mp, rep, field, tit, r2):
    L = []
    mn = idx[idx.team == TEAM].iloc[0]
    best, worst = mp.iloc[0], mp.iloc[-1]
    top = idx.iloc[0]
    wide = mp.assign(w=mp["max"] - mp["min"]).sort_values("w").iloc[-1]
    band_w = (mp["max"] - mp["min"])
    lift_pt = 100 * (rep.p_series_point - rep.p_series_even)
    lift_pt_pri = 100 * (rep.p_series_point_primary - rep.p_series_even)
    lift_up = 100 * (rep.p_series_upper - rep.p_series_even)
    vol_story = (rep.team_volatility_year_corr > rep.team_spread_year_corr
                 and abs(rep.team_spread_net_of_vol_year_corr) < rep.team_spread_year_corr)

    L.append("# N4: versatility index\n")
    L.append("*As of 2026-09-16. Part 1 is MODELLED: 2026-27 strengths from the un-aged "
             "primary after the D70 fixes, series model with the style overlay off (M2). "
             "Part 2 is OBSERVED: regular seasons from `nba_games`. Run `%s`.*\n" % r.run_id)
    L.append("**In plain terms.** The index asks how much a team's chance of winning a "
             "series swings across the eight contenders. Under the series model this "
             "project uses, that swing is set entirely by the team's own net rating: for "
             "the %d teams outside the field, ranking by swing is ranking by net rating "
             "(rank correlation %.2f in every view). The model prices a series on the "
             "rating gap and home court and nothing else, so the index ranks where a team "
             "sits on the curve, not how versatile it is. %s tops it because its rating "
             "sits among the contenders, where series are closest to coin flips; "
             "Minnesota ranks %d of 30. **Minnesota's best matchup in the field is %s (%.0f%%) "
             "and its worst %s (%.0f%%); within each view that order is the order of the "
             "opponents' net ratings.**\n"
             % (30 - N_FIELD, rep.spread_net_rankcorr_min, top.team, mn["rank"], best.opp,
                100 * best["mean"], worst.opp, 100 * worst["mean"]))
    L.append("The real question is whether versatility exists in the games themselves, "
             "which the model would then be missing. Across %s regular-season games since "
             "%s, the best estimate of a true, repeatable matchup effect (one team playing "
             "a particular opponent better than the ratings say) is **%.1f points per "
             "game**, and on %s games since %s it is %.1f. On an even series those two "
             "estimates are worth about %.0f and %.0f points of series probability. The "
             "data cannot "
             "rule out an effect as large as %.1f points per game (95%% upper bound), "
             "which would be worth %.0f points in an even series, so this is a small "
             "effect with a loose ceiling, not a proven zero. %s\n"
             % ("{:,}".format(int(rep.primary_games)), rep.primary_window[:7],
                rep.primary_sd_true, "{:,}".format(int(rep.extended_games)),
                rep.extended_window[:7], rep.extended_sd_true, lift_pt_pri, lift_pt,
                rep.upper_used,
                lift_up,
                ("A team's spread of results across opponents does repeat from one season "
                 "to the next (%+.2f), but that is volatility, not versatility: how swingy "
                 "a team's games are repeats more strongly (%+.2f), and once it is removed "
                 "the spread's repeat falls to %+.2f."
                 % (rep.team_spread_year_corr, rep.team_volatility_year_corr,
                    rep.team_spread_net_of_vol_year_corr)) if vol_story else
                ("A team's spread of results across opponents repeats from one season to "
                 "the next at %+.2f, and %+.2f once game-to-game volatility is removed."
                 % (rep.team_spread_year_corr, rep.team_spread_net_of_vol_year_corr))))

    L.append("## Part 1. The index as specified (MODELLED)\n")
    L.append("Field, top %d by modelled title odds: %s. A contender is scored against the "
             "other seven.\n" % (N_FIELD, ", ".join("%s (%.1f%%)" % (t, 100 * tit[t])
                                                    for t in field)))
    L.append("| rank | team | net, 2026-27 | gap to field | spread (SD) [four views] | "
             "range | mean P(series) |")
    L.append("|---:|---|---:|---:|---|---:|---:|")
    for _, x in idx.iterrows():
        L.append("| %d | %s%s | %+.2f | %+.2f | %.3f [%.3f, %.3f] | %.3f | %.3f |"
                 % (x["rank"], "**%s**" % x.team if x.team == TEAM else x.team,
                    " (field)" if x.in_field else "", x.net_mean, x.net_gap_to_field,
                    x.sd_mean, x.sd_lo, x.sd_hi, x.range_mean, x.mean_p))
    L.append("")
    L.append("**Minnesota against the field** (P wins the series, four-view band):\n")
    L.append("| opponent | P(Minnesota wins) | four-view band | opponent net |")
    L.append("|---|---:|---|---:|")
    for _, x in mp.iterrows():
        L.append("| %s | **%.3f** | %.3f to %.3f | %+.2f |"
                 % (x.opp, x["mean"], x["min"], x["max"], x.opp_net_mean))
    L.append("")
    L.append("Best matchup %s, worst %s. Within each view the order is exactly the order "
             "of the opponents' net ratings, and cannot be anything else under this model. "
             "Averaged across the four views the order can cross where a team's rating "
             "differs a lot between views: %s's band runs from %.2f to %.2f, the widest "
             "here, so 'best matchup' is a statement about the average of four views that "
             "disagree. The four-view bands on Minnesota's eight series are %.2f to %.2f "
             "wide.\n" % (best.opp, worst.opp, wide.opp, wide["min"], wide["max"],
                          band_w.min(), band_w.max()))

    L.append("## Part 2. Is there any versatility to measure? (OBSERVED)\n")
    L.append("| measure | %s | %s |" % (rep.primary_window, rep.extended_window))
    L.append("|---|---:|---:|")
    L.append("| regular-season games | %s | %s |" % ("{:,}".format(int(rep.primary_games)),
                                                  "{:,}".format(int(rep.extended_games))))
    L.append("| team-pair-seasons with two or more meetings | %s | %s |"
             % ("{:,}".format(int(rep.primary_pair_seasons)),
                "{:,}".format(int(rep.extended_pair_seasons))))
    L.append("| variance of the true pair effect [95%% interval] | %+.2f [%+.2f, %+.2f] | "
             "%+.2f [%+.2f, %+.2f] |" % (rep.primary_var, rep.primary_var_lo,
                                         rep.primary_var_hi, rep.extended_var,
                                         rep.extended_var_lo, rep.extended_var_hi))
    L.append("| **SD of the true matchup effect, points per game** | **%.2f** (upper %.2f) "
             "| **%.2f** (upper %.2f) |" % (rep.primary_sd_true, rep.primary_sd_upper95,
                                            rep.extended_sd_true, rep.extended_sd_upper95))
    L.append("")
    L.append("| further checks, %s | value |" % rep.primary_window)
    L.append("|---|---|")
    L.append("| residual SD of a single game after home court and ratings | %.2f points |"
             % rep.resid_sd)
    L.append("| pair residual, one half of meetings against the other | correlation %+.3f "
             "over %s pair-seasons |" % (rep.half_corr, "{:,}".format(int(rep.half_pairs))))
    L.append("| even series with home court: point estimate (2013-26 / 1997-2026) / upper "
             "bound | %.3f becomes %.3f / %.3f / %.3f |"
             % (rep.p_series_even, rep.p_series_point_primary, rep.p_series_point,
                rep.p_series_upper))
    L.append("| team spread across opponents, season to next | %+.3f over %d team pairs |"
             % (rep.team_spread_year_corr, int(rep.team_pairs)))
    L.append("| team game-to-game volatility, season to next | %+.3f |"
             % rep.team_volatility_year_corr)
    L.append("| team spread with volatility removed, season to next | %+.3f |"
             % rep.team_spread_net_of_vol_year_corr)
    L.append("| team's own true-matchup-variance estimate, season to next | %+.3f |"
             % rep.team_true_var_year_corr)
    L.append("")
    L.append("**What it shows.** Under the model the piece uses, the versatility index is a "
             "restatement of net rating, and Minnesota's best and worst matchups are its "
             "weakest and strongest opponents in each view. In the games themselves, the "
             "best estimate of a repeatable matchup effect is small, and it comes from a "
             "test that assumes no style mechanism at all, so it agrees with M1 (style "
             "interactions carry nothing out of sample) and N3 (no style trait translates) "
             "from a different direction. **What it does not show.** That matchup effects "
             "are zero: the upper bound is loose enough that a real effect of up to %.1f "
             "points per game, worth up to %.0f points on an even series, is not ruled out. "
             "Playoff matchups, where a coach has a week to game-plan one opponent; the "
             "test uses regular-season meetings, two to four a season, and the playoffs "
             "have too few repeated pairs to estimate the same way. Effects specific to one "
             "pair, such as San Antonio's scheme against Edwards, which can be real and "
             "still leave the league-wide average near zero. And mid-season roster changes, "
             "which blur a pair's meetings.\n" % (rep.upper_used, lift_up))
    L.append("*Definitions.* Field: top %d by mean modelled title odds across the four "
             "views. Series probability: `bracket_sim.conditional_series`, overlay off, "
             "home court to the higher net. Spread: population standard deviation and "
             "range across the field. Residual: game margin minus home court and the "
             "rating gap, fitted per season, with each team's net computed without the "
             "games between that pair. True pair-effect variance: the mean cross-product "
             "of two different games' residuals within the same pair-season (independent "
             "game noise contributes zero), bootstrapped over pair-seasons (%d resamples). "
             "Volatility: a team-season's residual SD across all its games. Per-game "
             "points are put on the series scale with the sim's resolver as if they were "
             "net-rating points. Detail: `outputs/n4_versatility_index.csv`, "
             "`n4_min_matchups.csv`, `n4_matchup_repeatability.csv`.\n" % (N_FIELD, BOOT))
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
