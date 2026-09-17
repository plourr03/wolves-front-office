#!/usr/bin/env python3
"""N8: the watch list. Five falsifiable claims for October and November.

EACH CLAIM HAS a metric a reader can look up, the current value this project carries, and
a threshold that would flip it, and every threshold is COMPUTED, never picked. The
checkpoint is a team's twentieth game, which lands in late November.

THE FIVE.
  1  CODY WILLIAMS' MINUTES. The model hands him 16.1 a night and the offseason verdict
     leans on it. Threshold: the minutes at which the four views stop agreeing that the
     offseason made Minnesota worse, interpolated from `williams_minutes_sensitivity`.
  2  MINNESOTA'S NET RATING AFTER 20 GAMES. The model's range for Minnesota is the span of
     its four views on BOTH aging bases. Threshold: the net rating a team whose true level
     sat at the edge of that range would reach less than 5% of the time over 20 games.
  3  THE MODEL'S TWO LARGEST DISAGREEMENTS WITH THE MARKET: Boston (model far above the
     market) and San Antonio (model far below). Same construction, one side each.
  4  EDWARDS AND BALL, THE PAIRING. M5's base rate says new high-usage pairings cost usage
     and not efficiency. Threshold: the 20-game true shooting that would fall below what the
     base rate plus 20-game noise allows, for either player.
  5  THE CHAMPION'S PATH. Every champion since 1997-98, ranked by net rating after its first
     20 games. Threshold: the worst rank any of them held. Minnesota's projected rank is
     set beside it.

NOISE, MEASURED. Twenty-game net rating: from every team-season 2013-14 to 2025-26, the
spread of the first twenty games against the rest of the season, converted to the noise
of a twenty-game mean under a stationary level (which ignores real in-season change and
so errs wide). Twenty-game true shooting: the same construction for every player-season
with usage of 0.25 or more and 60 or more games.

    python kuminga/scripts/n8_watch_list.py
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

from kuminga.lib import runlog  # noqa: E402
from lib import db              # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
WMS = os.path.join(OUT_DIR, "williams_minutes_sensitivity.csv")
STR_U = os.path.join(OUT_DIR, "team_strengths_2026_27.csv")
STR_A = os.path.join(OUT_DIR, "aged", "team_strengths_2026_27.csv")
MKT = os.path.join(OUT_DIR, "market_devig_2026_27.csv")
PANEL = os.path.join(OUT_DIR, "m5_pairing_panel.csv")
CREATION = os.path.join(OUT_DIR, "m5_creation_shares.csv")
OUT = os.path.join(OUT_DIR, "n8_watch_list.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "n8_watch_list.md")

FORKS = ["consensus", "rapm", "box", "darko"]
N_CHECK = 20
N_DEC = 30                # the December checkpoint: a team's thirtieth game, around 31 Dec
Z = 1.645                 # one-sided 5%
NOISE_SEASONS = range(2013, 2026)
CHAMP_SEASONS = range(1997, 2026)


def lab(y):
    return "%d-%02d" % (y, (y + 1) % 100)


def games_frame(first, last, playoffs=False):
    ids = tuple((40000 if playoffs else 20000) + y for y in range(first, last + 1))
    g = db.query("""
        select game_id, season_id, game_date, team_abbreviation team, plus_minus, pts,
               fga, fta, oreb, tov
        from nba.nba_games where season_id in %(i)s
    """, {"i": ids})
    for c in ("plus_minus", "pts", "fga", "fta", "oreb", "tov"):
        g[c] = pd.to_numeric(g[c], errors="coerce")
    g["season"] = pd.to_numeric(g.season_id) % 10000
    g = g.drop_duplicates(["game_id", "team"])
    opp = g[["game_id", "team", "fga", "fta", "oreb", "tov"]].rename(
        columns={"team": "opp", "fga": "o_fga", "fta": "o_fta", "oreb": "o_oreb",
                 "tov": "o_tov"})
    g = g.merge(opp, on="game_id")
    g = g[g.team != g.opp].copy()
    g["poss"] = 0.5 * ((g.fga - g.oreb + g.tov + 0.44 * g.fta)
                       + (g.o_fga - g.o_oreb + g.o_tov + 0.44 * g.o_fta))
    g = g.sort_values(["season", "team", "game_date", "game_id"])
    g["k"] = g.groupby(["season", "team"]).cumcount() + 1
    return g


def net100(d):
    return 100.0 * d.plus_minus.sum() / d.poss.sum()


def main():
    with runlog.run("n8_watch_list", inputs={"n_check": N_CHECK, "z": Z}) as r:
        rows = []

        # ================= 1. Cody Williams' minutes =================================
        w = pd.read_csv(WMS).sort_values("williams_mpg")
        dcols = ["delta_%s" % f for f in FORKS]

        def pattern(row):
            v = [row[c] for c in dcols]
            return "ALL NEGATIVE" if max(v) < 0 else "ALL POSITIVE" if min(v) > 0 else "MIXED"

        w["pattern"] = w.apply(pattern, axis=1)
        default = w[w.level == "model default"].iloc[0]
        # the highest minutes at which the pattern is no longer ALL NEGATIVE, found by
        # interpolating each view's delta between the grid points that bracket its zero
        flips = []
        grid = w.sort_values("williams_mpg")
        for f in FORKS:
            c = "delta_%s" % f
            for i in range(len(grid) - 1):
                lo, hi = grid.iloc[i], grid.iloc[i + 1]
                if lo[c] >= 0 > hi[c]:
                    x = lo.williams_mpg + (0 - lo[c]) * (hi.williams_mpg - lo.williams_mpg) \
                        / (hi[c] - lo[c])
                    flips.append((f, float(x)))
        flip_view, flip_mpg = max(flips, key=lambda t: t[1]) if flips else (None, np.nan)
        VIEW = {"consensus": "consensus", "rapm": "RAPM", "box": "box", "darko": "DARKO"}
        below = grid[grid.williams_mpg < flip_mpg].williams_mpg.max()
        above = grid[grid.williams_mpg >= flip_mpg].williams_mpg.min()
        edge = float(grid[grid.williams_mpg == above]["delta_%s" % flip_view].iloc[0])
        r.note("1. Williams: model default %.1f mpg, pattern %s; first view to turn "
               "positive as his minutes fall: %s at %.1f mpg"
               % (default.williams_mpg, default.pattern, flip_view, flip_mpg))
        rows.append(dict(
            n=1, claim="Cody Williams' minutes decide whether the offseason verdict holds",
            metric="Cody Williams minutes per Minnesota game, through game %d" % N_CHECK,
            label="assumed input, modelled consequence",
            current="%.1f a night (model default)" % default.williams_mpg,
            threshold="below %.1f a night" % flip_mpg,
            flips=("the four views stop agreeing the offseason made Minnesota worse: the "
                   "%s view turns positive, so the verdict goes from ALL NEGATIVE to MIXED "
                   "(at %.0f minutes the %s delta is already only %+.3f points, so this "
                   "flip sits right at the threshold)"
                   % (VIEW[flip_view], above, VIEW[flip_view], edge)),
            source="williams_minutes_sensitivity.csv", value=flip_mpg))

        # ================= noise: twenty-game net rating ================================
        g = games_frame(min(NOISE_SEASONS), max(NOISE_SEASONS))
        per = []
        for (s, t), d in g.groupby(["season", "team"]):
            if len(d) < N_CHECK + 20:
                continue
            a_, b_ = d[d.k <= N_CHECK], d[d.k > N_CHECK]
            per.append(dict(season=s, team=t, first=net100(a_), rest=net100(b_),
                            n_rest=len(b_)))
        per = pd.DataFrame(per)
        var_diff = float((per["first"] - per.rest).var())
        n_rest = float(per.n_rest.mean())
        sig20 = float(np.sqrt(var_diff * n_rest / (N_CHECK + n_rest)))
        # a second read: game-level residual spread about the season level
        g2 = g.merge(g.groupby(["season", "team"]).apply(net100, include_groups=False)
                     .rename("lvl").reset_index(), on=["season", "team"])
        g2["pp100"] = 100.0 * g2.plus_minus / g2.poss
        sd_game = float((g2.pp100 - g2.lvl).std())
        sig20_b = sd_game / np.sqrt(N_CHECK)
        SIG = max(sig20, sig20_b)
        # the December checkpoint, same construction at 30 games
        per30 = []
        for (s, t_), d in g.groupby(["season", "team"]):
            if len(d) < N_DEC + 20:
                continue
            per30.append(dict(first=net100(d[d.k <= N_DEC]), rest=net100(d[d.k > N_DEC]),
                              n_rest=int((d.k > N_DEC).sum())))
        per30 = pd.DataFrame(per30)
        sig30 = float(np.sqrt((per30["first"] - per30.rest).var() * per30.n_rest.mean()
                              / (N_DEC + per30.n_rest.mean())))
        SIG30 = max(sig30, sd_game / np.sqrt(N_DEC))
        r.note("noise, 20-game net rating per 100: split-season %.2f (from %d team-seasons), "
               "game-level %.2f; using %.2f" % (sig20, len(per), sig20_b, SIG))

        # ================= 2 and 3. net rating against the model's range =================
        su, sa = pd.read_csv(STR_U), pd.read_csv(STR_A)
        mkt = pd.read_csv(MKT).set_index("team_abbr")

        def model_range(team):
            v = list(su[su.team_abbr == team].net_current) + list(
                sa[sa.team_abbr == team].net_current)
            return float(min(v)), float(max(v)), float(np.mean(v[:4])), float(np.mean(v[4:]))

        lo, hi, mu_u, mu_a = model_range("MIN")
        r.note("2. MIN model net range across four views x two aging bases: %+.2f to %+.2f "
               "(un-aged mean %+.2f, aged mean %+.2f)" % (lo, hi, mu_u, mu_a))
        rows.append(dict(
            n=2, claim="Minnesota's level is inside the model's range",
            metric="Minnesota net rating per 100 possessions, first %d games" % N_CHECK,
            label="modelled range, measured noise",
            current="model range %+.1f to %+.1f (four views, both aging bases)" % (lo, hi),
            threshold="above %+.1f or below %+.1f" % (hi + Z * SIG, lo - Z * SIG),
            flips=("the model's range for Minnesota is wrong in that direction: a team whose "
                   "true level sat at the edge of the range gets there less than 5%% of the "
                   "time in %d games (noise %.1f per 100)" % (N_CHECK, SIG)),
            source="team_strengths_2026_27.csv (un-aged and aged)",
            value=hi + Z * SIG, value2=lo - Z * SIG))

        m = mkt[["model_mean", "market_prop"]].copy()
        m["gap"] = m.model_mean - m.market_prop
        up, down = m.gap.idxmax(), m.gap.idxmin()
        ulo, uhi, _, _ = model_range(up)
        dlo, dhi, _, _ = model_range(down)
        dec = pd.DataFrame([dict(checkpoint="December (game %d)" % N_DEC, n_games=N_DEC,
                                 noise=SIG30, team=up, direction="model above market",
                                 model_title=100 * m.loc[up, "model_mean"],
                                 market_title=100 * m.loc[up, "market_prop"],
                                 range_lo=ulo, range_hi=uhi, threshold=ulo - Z * SIG30,
                                 flips_if="net rating per 100 below"),
                            dict(checkpoint="December (game %d)" % N_DEC, n_games=N_DEC,
                                 noise=SIG30, team=down, direction="model below market",
                                 model_title=100 * m.loc[down, "model_mean"],
                                 market_title=100 * m.loc[down, "market_prop"],
                                 range_lo=dlo, range_hi=dhi, threshold=dhi + Z * SIG30,
                                 flips_if="net rating per 100 above")])
        dec.to_csv(OUT.replace(".csv", "_december.csv"), index=False)
        r.note("December checkpoint (game %d): noise %.2f per 100; %s flips below %+.1f, %s "
               "above %+.1f" % (N_DEC, SIG30, up, ulo - Z * SIG30, down, dhi + Z * SIG30))
        r.output(OUT.replace(".csv", "_december.csv"), rows=len(dec))
        r.note("3. largest model-market gaps: %s model %.1f%% vs market %.1f%%; %s model %.1f%% "
               "vs market %.1f%%" % (up, 100 * m.loc[up, "model_mean"],
                                    100 * m.loc[up, "market_prop"], down,
                                    100 * m.loc[down, "model_mean"],
                                    100 * m.loc[down, "market_prop"]))
        rows.append(dict(
            n=3, claim="The model's two largest disagreements with the market",
            metric="Net rating per 100, first %d games: %s and %s" % (N_CHECK, up, down),
            label="modelled range, measured noise, market prior",
            current=("%s: model %.1f%% title odds vs market %.1f%%, model net range %+.1f to "
                     "%+.1f. %s: model %.1f%% vs market %.1f%%, range %+.1f to %+.1f"
                     % (up, 100 * m.loc[up, "model_mean"], 100 * m.loc[up, "market_prop"],
                        ulo, uhi, down, 100 * m.loc[down, "model_mean"],
                        100 * m.loc[down, "market_prop"], dlo, dhi)),
            threshold="%s below %+.1f; %s above %+.1f" % (up, ulo - Z * SIG, down,
                                                         dhi + Z * SIG),
            flips=("on that team the market's read beats the model's, and the field that "
                   "prices every Minnesota number is mis-set in the same direction"),
            source="market_devig_2026_27.csv, team_strengths_2026_27.csv",
            value=ulo - Z * SIG, value2=dhi + Z * SIG))

        # ================= 4. Edwards and Ball: efficiency under the pairing ===============
        panel = pd.read_csv(PANEL)
        tr = panel[panel.treated == 1]
        mean_dts, sd_dts = float(tr.d_ts.mean()), float(tr.d_ts.std())
        ids = tuple(range(2013, 2026))
        pg = db.query("""
            select s.player_id::bigint pid, s.season_year season, s.game_date, s.game_id,
                   s.pts, s.fga, s.fta
            from nba.nba_player_stats s
            join (select distinct player_id::bigint pid, season_year
                  from nba.nba_player_season_bio
                  where season_type = 'Regular Season' and usg_pct::numeric >= 0.25
                    and gp::numeric >= 60 and season_year >= '2013-14') b
              on b.pid = s.player_id::bigint and b.season_year = s.season_year
            where s.game_id like '002%%'
        """)
        for c in ("pts", "fga", "fta"):
            pg[c] = pd.to_numeric(pg[c], errors="coerce")
        pg = pg[(pg.fga + pg.fta) > 0].sort_values(["pid", "season", "game_date", "game_id"])
        pg["k"] = pg.groupby(["pid", "season"]).cumcount() + 1

        def ts(d):
            return d.pts.sum() / (2.0 * (d.fga.sum() + 0.44 * d.fta.sum()))

        tsr = []
        for (p_, s_), d in pg.groupby(["pid", "season"]):
            if len(d) < N_CHECK + 20:
                continue
            tsr.append(dict(first=ts(d[d.k <= N_CHECK]), rest=ts(d[d.k > N_CHECK]),
                            n_rest=int((d.k > N_CHECK).sum())))
        tsr = pd.DataFrame(tsr)
        sig_ts = float(np.sqrt((tsr["first"] - tsr.rest).var() * tsr.n_rest.mean()
                               / (N_CHECK + tsr.n_rest.mean())))
        cr = pd.read_csv(CREATION)
        c26 = cr[cr.window == "2025-26"].set_index("player")
        band = float(np.sqrt(sd_dts ** 2 + sig_ts ** 2))
        thr = {n_: float(c26.loc[n_, "ts_2025_26"] + mean_dts - Z * band)
               for n_ in ("Anthony Edwards", "LaMelo Ball")}
        r.note("4. pairing: treated TS change mean %+.3f, SD %.3f (n %d); 20-game TS noise "
               "%.3f (from %d player-seasons); thresholds Edwards %.3f, Ball %.3f"
               % (mean_dts, sd_dts, len(tr), sig_ts, len(tsr), thr["Anthony Edwards"],
                  thr["LaMelo Ball"]))
        rows.append(dict(
            n=4, claim="The Edwards-Ball pairing costs usage, not efficiency",
            metric="True shooting, first %d games, Anthony Edwards and LaMelo Ball" % N_CHECK,
            label="observed base rate, measured noise",
            current=("2025-26 true shooting: Edwards %.3f, Ball %.3f. Unadjusted base rate for a "
                     "new high-usage pairing: %+.1f points of true shooting (%d player-seasons)"
                     % (c26.loc["Anthony Edwards", "ts_2025_26"],
                        c26.loc["LaMelo Ball", "ts_2025_26"], 100 * mean_dts, len(tr))),
            threshold="Edwards below %.3f, or Ball below %.3f" % (thr["Anthony Edwards"],
                                                                  thr["LaMelo Ball"]),
            flips=("the pairing is costing efficiency beyond anything the base rate and 20 "
                   "games of noise allow, and M5's reading does not hold for this pair"),
            source="m5_pairing_panel.csv, m5_creation_shares.csv, nba_player_stats",
            value=thr["Anthony Edwards"], value2=thr["LaMelo Ball"]))

        # ================= 5. the champion's path =======================================
        gc = games_frame(min(CHAMP_SEASONS), max(CHAMP_SEASONS))
        po = db.query("""
            select game_id, season_id, game_date, team_abbreviation team, wl
            from nba.nba_games where season_id in %(i)s
        """, {"i": tuple(40000 + y for y in CHAMP_SEASONS)})
        po["season"] = pd.to_numeric(po.season_id) % 10000
        # the champion won the LAST playoff game of the season. (A first version read the
        # round from the game id, which only encodes it from 2000-01 on, and silently
        # dropped four champions.)
        last = po.sort_values(["season", "game_date", "game_id"]).groupby("season").tail(2)
        champs = last[last.wl == "W"].drop_duplicates("season").set_index("season").team
        if len(champs) != len(CHAMP_SEASONS):
            raise RuntimeError("champion not resolved for every season")
        ranks = []
        for s_, d in gc[gc.k <= N_CHECK].groupby("season"):
            nets = d.groupby("team").apply(net100, include_groups=False)
            rk = nets.rank(ascending=False, method="min")
            full = gc[gc.season == s_].groupby("team").apply(net100, include_groups=False) \
                .rank(ascending=False, method="min")
            if s_ in champs.index and champs[s_] in rk.index:
                ranks.append(dict(season=lab(s_), champion=champs[s_],
                                  rank20=int(rk[champs[s_]]), rank_full=int(full[champs[s_]]),
                                  n_teams=len(rk)))
        CH = pd.DataFrame(ranks)
        worst20 = int(CH.rank20.max())
        share_top = {k: float((CH.rank20 <= k).mean()) for k in (3, 5, 8, 10)}
        allnet = pd.concat([su.assign(b="u"), sa.assign(b="a")]).groupby(
            ["b", "team_abbr"]).net_current.mean().reset_index()
        mrk = []
        for b_, d in allnet.groupby("b"):
            rk = d.set_index("team_abbr").net_current.rank(ascending=False, method="min")
            mrk.append(int(rk["MIN"]))
        r.note("5. champions 1997-98 to 2025-26 (%d): rank after 20 games worst %d, median "
               "%.0f; share in top 3/5/8/10: %s | MIN projected net rank un-aged %d, aged %d"
               % (len(CH), worst20, CH.rank20.median(),
                  ", ".join("%.0f%%" % (100 * v) for v in share_top.values()), mrk[1], mrk[0]))
        worst_rows = CH[CH.rank20 == worst20]
        # under the model: draw one of the eight (view x aging basis) strength sets for the
        # whole league, add 20-game noise to every team, rank, repeat
        sets = [d.set_index("team_abbr").net_current for _, d in
                pd.concat([su.assign(b="u"), sa.assign(b="a")]).groupby(["b", "fork"])]
        rng = np.random.default_rng(20260916)
        NDRAW = 20000
        teams_ = list(sets[0].index)
        mats = np.array([s.reindex(teams_).to_numpy() for s in sets])
        mi = teams_.index("MIN")
        min_rank = np.empty(NDRAW, dtype=int)
        for i in range(NDRAW):
            v = mats[rng.integers(0, len(sets))] + rng.normal(0.0, SIG, len(teams_))
            min_rank[i] = int((v > v[mi]).sum() + 1)
        p_path = float((min_rank <= worst20).mean())
        # the TEST: the best rank noise alone reaches no more than 5% of the time
        k_test = max([k for k in range(1, 31) if (min_rank <= k).mean() <= 0.05] or [0])
        p_k = float((min_rank <= k_test).mean()) if k_test else 0.0
        share_k = float((CH.rank20 <= k_test).mean()) if k_test else 0.0
        r.note("   test threshold: rank %d or better, reached by noise %.3f of the time; "
               "%.0f%% of champions were there" % (k_test, p_k, 100 * share_k))
        r.note("   P(Minnesota ranks %d or better after 20 games | model, 20-game noise) = %.3f"
               % (worst20, p_path))
        rows.append(dict(
            n=5, claim="Minnesota is not on a champion's path",
            metric="Minnesota's league rank in net rating after %d games" % N_CHECK,
            current=("projected rank %d (un-aged) / %d (aged); the %d champions since 1997-98 "
                     "ranked %d at worst after 20 games (%s), median %.0f"
                     % (mrk[1], mrk[0], len(CH), worst20,
                        " and ".join("%s %s" % (x.season, x.champion)
                                     for _, x in worst_rows.iterrows()),
                        CH.rank20.median())),
            threshold="%d or better (test); %d or better (checkpoint)" % (k_test, worst20),
            flips=("TEST: %s or better is somewhere noise alone takes a team projected like "
                   "Minnesota only %.0f%% of the time, so the model has Minnesota's level "
                   "wrong, and %.0f%% of champions since 1997-98 stood there after 20 games. "
                   "CHECKPOINT: %dth or better puts Minnesota back inside every champion's "
                   "range, but noise alone does that %.0f%% of the time, so it proves little"
                   % (k_test, 100 * p_k, 100 * share_k, worst20, 100 * p_path)),
            label="observed history, modelled projection, checkpoint",
            source="nba_games 1997-98 to 2025-26, team_strengths_2026_27.csv",
            value=k_test, value2=worst20))
        CH.to_csv(OUT.replace(".csv", "_champion_ranks.csv"), index=False)

        W = pd.DataFrame(rows)
        W.to_csv(OUT, index=False)
        r.output(OUT, rows=len(W))
        r.output(OUT.replace(".csv", "_champion_ranks.csv"), rows=len(CH))
        write_doc(r, W, CH, SIG, sig_ts, share_top)
        r.output(OUT_MD)


def write_doc(r, W, CH, SIG, sig_ts, share_top):
    L = ["# N8: what to watch in October and November\n",
         "*As of 2026-09-16. Checkpoint: each team's twentieth game, late November. Run "
         "`%s`. Every threshold is computed from the numbers named in its row.*\n" % r.run_id,
         "**In plain terms.** Five things that could prove this preview wrong by the end of "
         "November, and the number at which each one would. Two can be read straight off a "
         "box score: Cody Williams' minutes, and Edwards' and Ball's true shooting. Two are "
         "team levels, and a twenty-game net rating is noisy, about %.1f points per 100 "
         "possessions of pure chance, so those thresholds sit well outside the model's own "
         "range on purpose; a claim that flips on noise is not a claim. The fifth, the "
         "champion's path, carries both a test built the same way and the plain historical "
         "checkpoint, with how often noise alone would trip each.\n" % SIG,
         "| # | claim | metric | now | flips if | what flipping means | label |",
         "|---:|---|---|---|---|---|---|"]
    for _, x in W.iterrows():
        L.append("| %d | **%s** | %s | %s | **%s** | %s | %s |"
                 % (x.n, x.claim, x.metric, x.current, x.threshold, x.flips, x.label))
    L.append("")
    L.append("**The champion's path, in full.** Net-rating rank after 20 games for every "
             "champion since 1997-98: %s. Share of them in the top 3, 5, 8 and 10: %s.\n"
             % ("; ".join("%s %s %d" % (x.season, x.champion, x.rank20)
                          for _, x in CH.iterrows()),
                ", ".join("%.0f%%" % (100 * v) for v in share_top.values())))
    L.append("**What this list does not do.** It does not update the model in November; a "
             "flipped claim is a finding to report, not a re-run. It does not cover injuries, "
             "which N5 prices. And the noise figures assume a team's level holds steady "
             "through a season, which makes every level threshold a little wider than it "
             "needs to be (twenty-game true shooting noise for a high-usage player is %.3f).\n"
             % sig_ts)
    L.append("*Method.* Williams: each view's offseason delta interpolated to zero across "
             "the minutes grid in `williams_minutes_sensitivity.csv`. Net rating: points per "
             "100 estimated possessions; noise is the larger of the split-season estimate "
             "(first 20 games against the rest, 2013-14 to 2025-26, scaled to a 20-game mean) "
             "and the game-level spread divided by the square root of 20; thresholds sit %.3f "
             "noise units beyond the model's range, which spans four views on both aging "
             "bases. Pairing: 2025-26 true shooting plus the mean change for players who "
             "gained a new high-usage partner (M5), minus %.3f times the combined spread of "
             "that change and 20-game noise. Champions: the Finals winner each season from "
             "`nba_games`, ranked on net rating over its first 20 regular-season games. "
             "Detail: `outputs/n8_watch_list.csv`, `n8_watch_list_champion_ranks.csv`.\n"
             % (Z, Z))
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
