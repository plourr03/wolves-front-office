#!/usr/bin/env python3
"""M5: usage accounting. Is there enough ball for Edwards, Ball and Kuminga?

THREE MEASUREMENTS, all read straight from the warehouse (no model input, so nothing here
moves when the simulation chain re-runs). Regular season only throughout.

A. UNIT USAGE SUMS. Each projected Minnesota five, scored as the sum of its players'
   2025-26 usage rates, against the same sum for EVERY starting five that actually
   started a game in 2023-24, 2024-25 and 2025-26. A starter's usage there is his usage
   for that team that season, so league fives have already negotiated their shares with
   each other. Minnesota's projected fives have not: each player's rate was earned in a
   different situation. The gap between the two is the usage that has to be given up.
   Starters are read from the box score: a player with a listed position started, and
   every team-game has exactly five.

B. BASE RATES FOR NEW HIGH-USAGE PAIRINGS. Three seasons (t = 2023-24, 2024-25, 2025-26).
   A player is HIGH USAGE if his season t-1 usage was at least USG_HIGH over at least
   MIN_PREV minutes. He is TREATED in season t if he played at least MIN_CUR minutes for
   his main team and shared at least SHARED_MIN games there with another high-usage player
   he did NOT share a floor with in t-1. He is a CONTROL if he meets the same thresholds
   with no such new partner. Outcomes are the change in usage and in true shooting from
   t-1 to t. The control group is the point: high-usage players lose usage and efficiency
   on average anyway (regression to the mean, age), so the pairing effect is the
   difference between the groups, adjusted for prior usage, age and whether the player
   changed teams, with standard errors clustered by player.

C. CREATION SHARES. From play-by-play, the share of each player's made field goals that
   were assisted or unassisted, overall and split into twos and threes, for Ball,
   Edwards, Kuminga, Dosunmu and Hyland, with a league percentile among players with at
   least FGM_REF made field goals. Play-by-play made shots are reconciled to box-score FGM
   before any share is reported, and the script fails closed if they disagree.

WHAT THIS CANNOT SEE. There is no lineup table, so usage is season-level on a team, not
possession-level with a given partner on the floor. The base rates describe what happened
to players who found themselves in a new high-usage pairing, not what a coach chose to do
with them, and selection into those pairings is not random.

    python kuminga/scripts/m5_usage_accounting.py
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
ROT = os.path.join(OUT_DIR, "rotations_2026_27.csv")
OUT_A = os.path.join(OUT_DIR, "m5_unit_usage.csv")
OUT_B = os.path.join(OUT_DIR, "m5_pairing_base_rates.csv")
OUT_BP = os.path.join(OUT_DIR, "m5_pairing_panel.csv")
OUT_C = os.path.join(OUT_DIR, "m5_creation_shares.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "m5_usage_accounting.md")

SEASONS = {"22": "2022-23", "23": "2023-24", "24": "2024-25", "25": "2025-26"}
USG_HIGH = 0.25
MIN_PREV = 1000.0
MIN_CUR = 800.0
SHARED_MIN = 25
USG_SENS = (0.22, 0.28)
FGM_REF = 200
LEAGUE_SEASONS = ("2023-24", "2024-25", "2025-26")   # starting-five distribution
TEAM = "MIN"
CREATORS = {1630163: "LaMelo Ball", 1630162: "Anthony Edwards", 1630228: "Jonathan Kuminga",
            1630245: "Ayo Dosunmu", 1630538: "Nah'Shon Hyland"}
GUARDS_BIGS = {"big": {203497, 1642866}}   # Gobert, Beringer: the roster's listed centres


def pct_rank(series, value):
    s = series.dropna()
    return float((s < value).mean() * 100 + (s == value).mean() * 50)


def ts(pts, fga, fta):
    d = 2.0 * (fga + 0.44 * fta)
    return pts / d if d else np.nan


def cluster_ols(y, X, groups):
    """OLS with cluster-robust (CR1) standard errors."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    xtx_inv = np.linalg.inv(X.T @ X)
    meat = np.zeros((X.shape[1], X.shape[1]))
    g = pd.Series(groups).reset_index(drop=True)
    for _, idx in g.groupby(g).groups.items():
        s = X[list(idx)].T @ resid[list(idx)]
        meat += np.outer(s, s)
    n, k, G = len(y), X.shape[1], g.nunique()
    adj = (G / (G - 1)) * ((n - 1) / (n - k))
    cov = adj * xtx_inv @ meat @ xtx_inv
    return beta, np.sqrt(np.diag(cov))


def main():
    with runlog.run("m5_usage_accounting",
                    inputs={"usg_high": USG_HIGH, "min_prev": MIN_PREV, "min_cur": MIN_CUR,
                            "shared_min": SHARED_MIN, "fgm_ref": FGM_REF,
                            "seasons": list(SEASONS.values())}) as r:
        like = " or ".join("a.game_id like '002%s%%%%'" % k for k in SEASONS)
        g = db.query("""
            select a.game_id, a.person_id::bigint pid, a.team_tricode team,
                   a.minutes_float mins, a.usage_percentage usg, a.possessions poss,
                   coalesce(a.position, '') pos, s.pts, s.fga, s.fta
            from nba.nba_player_advanced_stats a
            left join nba.nba_player_stats s
              on s.game_id::text = a.game_id::text and s.player_id::text = a.person_id::text
            where (""" + like + """)""")
        for c in ("mins", "usg", "poss", "pts", "fga", "fta"):
            g[c] = pd.to_numeric(g[c], errors="coerce")
        g["season"] = g.game_id.str[3:5].map(SEASONS)
        n_unmatched = int(g[g.mins > 0].pts.isna().sum())
        g = g[g.mins > 0].copy()
        r.note("player-game rows with minutes: %d; box-score join misses: %d"
               % (len(g), n_unmatched))
        if n_unmatched > 0.01 * len(g):
            raise RuntimeError("box-score join lost more than 1%% of rows")
        g["usg_poss"] = g.usg * g.poss

        def agg(frame, keys):
            a = frame.groupby(keys).agg(mins=("mins", "sum"), poss=("poss", "sum"),
                                        usg_poss=("usg_poss", "sum"), pts=("pts", "sum"),
                                        fga=("fga", "sum"), fta=("fta", "sum"),
                                        games=("game_id", "nunique")).reset_index()
            a["usg"] = a.usg_poss / a.poss
            a["ts"] = a.pts / (2.0 * (a.fga + 0.44 * a.fta))
            return a

        ps = agg(g, ["pid", "season"])            # player-season, all teams
        pts_ = agg(g, ["pid", "season", "team"])  # player-team-season

        # ============ A. UNIT USAGE SUMS ==========================================
        st = g.loc[g.pos != "", ["game_id", "team", "season", "pid"]].merge(
            pts_[["pid", "season", "team", "usg"]],
                                  on=["pid", "season", "team"])
        five = st.groupby(["game_id", "team", "season"]).agg(n=("pid", "size"),
                                                             usg_sum=("usg", "sum"))
        bad = int((five.n != 5).sum())
        five = five[five.n == 5].reset_index()
        five = five[five.season.isin(LEAGUE_SEASONS)].reset_index(drop=True)
        r.note("A. league starting fives: %d team-games (%d dropped, not exactly five)"
               % (len(five), bad))
        q = five.usg_sum.quantile([0.1, 0.5, 0.9, 0.99])
        r.note("   starting-five usage sum: p10 %.3f, median %.3f, p90 %.3f, p99 %.3f, "
               "max %.3f" % (q[0.1], q[0.5], q[0.9], q[0.99], five.usg_sum.max()))

        rot = pd.read_csv(ROT)
        mn = rot[(rot.scenario == "current") & (rot.team_abbr == TEAM)
                 & rot.player_id.notna()].copy()
        mn["pid"] = mn.player_id.astype(int)
        mn = mn.sort_values("mpg", ascending=False)
        last = ps[ps.season == "2025-26"].set_index("pid")
        mn["usg"] = mn.pid.map(last.usg)
        mn["mins_2526"] = mn.pid.map(last.mins)
        name = dict(zip(mn.pid, mn.player_name))
        r.note("   Minnesota 2025-26 usage: " + "; ".join(
            "%s %s" % (x.player_name, "%.3f" % x.usg if pd.notna(x.usg) else "none")
            for _, x in mn.head(10).iterrows()))

        top5 = list(mn.pid.head(5))
        kum = [p for p in top5 if p != 1630245][:4] + [1630228]
        legal = mn[mn.usg.notna() & (mn.mpg >= 10)]
        best, best_sum = None, -1
        import itertools
        for combo in itertools.combinations(legal.pid, 5):
            if not set(combo) & GUARDS_BIGS["big"]:
                continue
            s_ = float(legal.set_index("pid").loc[list(combo), "usg"].sum())
            if s_ > best_sum:
                best, best_sum = list(combo), s_
        # last season's most-used Minnesota starting five, as the observed reference
        mst = st[(st.team == TEAM) & (st.season == "2025-26")]
        lab = mst.groupby("game_id").pid.apply(lambda s: tuple(sorted(s)))
        mode_five = list(lab.value_counts().index[0])
        mode_games = int(lab.value_counts().iloc[0])
        names_q = db.query("""select distinct person_id::bigint pid, first_name || ' ' || family_name nm
                              from nba.nba_player_advanced_stats
                              where game_id like '00225%%' and team_tricode = 'MIN'""")
        name_all = dict(zip(names_q.pid, names_q.nm))
        name_all.update(name)

        units = [
            ("Projected top five by minutes", top5, "projected"),
            ("Kuminga in for Dosunmu", kum, "projected"),
            ("Highest-usage five with a centre", best, "projected"),
            ("2025-26 most-used Minnesota starting five (%d starts)" % mode_games,
             mode_five, "observed"),
        ]
        # sensitivity: three-season possession-weighted rates, so one short or injured
        # season (Kuminga: 36 games in 2025-26) does not set a player's share alone
        pooled = agg(g[g.season.isin(["2023-24", "2024-25", "2025-26"])], ["pid"])
        pooled = pooled.set_index("pid")
        ts_med = (five.groupby(["team", "season"]).usg_sum.median())
        rows_a = []
        for label, ids, kind in units:
            if kind == "observed":
                u = mst[mst.pid.isin(ids)].drop_duplicates("pid").set_index("pid").usg
                vals = [float(u.get(p, np.nan)) for p in ids]
            else:
                vals = [float(last.usg.get(p, np.nan)) for p in ids]
            vals3 = [float(pooled.usg.get(p, np.nan)) for p in ids]
            s_ = float(np.nansum(vals))
            s3 = float(np.nansum(vals3))
            rows_a.append(dict(
                unit=label, kind=kind, players="; ".join(name_all.get(p, str(p)) for p in ids),
                usg_each="; ".join("%.3f" % v for v in vals), usg_sum=s_,
                missing=int(np.isnan(vals).sum()),
                league_pct=pct_rank(five.usg_sum, s_),
                share_league_at_or_above=float((five.usg_sum >= s_).mean()),
                excess_over_median=s_ - float(q[0.5]),
                team_seasons_with_higher_median=int((ts_med > s_).sum()),
                usg_each_2023_26="; ".join("%.3f" % v for v in vals3), usg_sum_2023_26=s3,
                league_pct_2023_26=pct_rank(five.usg_sum, s3)))
            r.note("   %-58s sum %.3f  percentile %.1f  (%.2f%% of league starts at or above)"
                   "  | 2023-26 rates %.3f pct %.1f"
                   % (label, s_, rows_a[-1]["league_pct"],
                      100 * rows_a[-1]["share_league_at_or_above"], s3,
                      rows_a[-1]["league_pct_2023_26"]))
        A = pd.DataFrame(rows_a)
        A["league_team_games"] = len(five)
        A["league_p10"], A["league_median"], A["league_p90"], A["league_p99"] = (
            q[0.1], q[0.5], q[0.9], q[0.99])
        A.to_csv(OUT_A, index=False)

        # which real team-seasons ran the highest usage fives, for context
        top_ts = (five.groupby(["team", "season"]).usg_sum.median()
                  .sort_values(ascending=False).head(5))
        r.note("   highest median starting-five usage sums by team-season: " + "; ".join(
            "%s %s %.3f" % (t_, s_, v) for (t_, s_), v in top_ts.items()))

        # ============ B. NEW HIGH-USAGE PAIRINGS =================================
        tm = g[["game_id", "team", "season", "pid"]]
        pair = tm.merge(tm, on=["game_id", "team", "season"])
        pair = pair[pair.pid_x != pair.pid_y]
        shared = pair.groupby(["season", "team", "pid_x", "pid_y"]).size().rename("shared")
        shared = shared.reset_index()
        ever = set(zip(shared.season, shared.pid_x, shared.pid_y))

        order = list(SEASONS.values())
        prev_of = {order[i]: order[i - 1] for i in range(1, len(order))}
        main_team = (pts_.sort_values("mins", ascending=False)
                     .drop_duplicates(["pid", "season"]).set_index(["pid", "season"]))
        psx = ps.set_index(["pid", "season"])
        bio = db.query("""select player_id::bigint pid, season_year season, age
                          from nba.nba_player_season_bio where season_type = 'Regular Season'""")
        age = bio.drop_duplicates(["pid", "season"]).set_index(["pid", "season"]).age

        sh_idx = shared[shared.shared >= SHARED_MIN].groupby(
            ["season", "team", "pid_x"]).pid_y.apply(list)

        def build_panel(thr):
            panel = []
            for t in order[1:]:
                tp = prev_of[t]
                prev = psx.xs(tp, level="season")
                high_prev = set(prev[(prev.usg >= thr) & (prev.mins >= MIN_PREV)].index)
                for p in high_prev:
                    if (p, t) not in main_team.index:
                        continue
                    mt = main_team.loc[(p, t)]
                    if mt.mins < MIN_CUR:
                        continue
                    partners = [q_ for q_ in sh_idx.get((t, mt.team, p), [])
                                if q_ in high_prev]
                    new = [q_ for q_ in partners if (tp, p, q_) not in ever]
                    cont = [q_ for q_ in partners if (tp, p, q_) in ever]
                    prev_team = (main_team.loc[(p, tp)].team
                                 if (p, tp) in main_team.index else None)
                    panel.append(dict(
                        pid=p, season=t, team=mt.team, prev_team=prev_team,
                        moved=int(prev_team != mt.team), treated=int(len(new) > 0),
                        n_new_partners=len(new), n_continuing_partners=len(cont),
                        new_partners="; ".join(str(x) for x in new),
                        usg_prev=float(prev.loc[p].usg), usg_cur=float(mt.usg),
                        ts_prev=float(prev.loc[p].ts), ts_cur=float(mt.ts),
                        mins_prev=float(prev.loc[p].mins), mins_cur=float(mt.mins),
                        age=float(age.get((p, t), np.nan))))
            out = pd.DataFrame(panel)
            out["d_usg"] = out.usg_cur - out.usg_prev
            out["d_ts"] = out.ts_cur - out.ts_prev
            return out

        def adjusted(frame, thr):
            fm = frame.dropna(subset=["age"]).reset_index(drop=True)
            X = np.column_stack([np.ones(len(fm)), fm.treated, fm.usg_prev - thr,
                                 fm.age - fm.age.mean(), fm.moved])
            res = {}
            for yv in ("d_usg", "d_ts"):
                b, se = cluster_ols(fm[yv], X, fm.pid)
                res[yv] = (float(b[1]), float(se[1]))
            return res, len(fm), int(fm.treated.sum()), fm.pid.nunique()

        P = build_panel(USG_HIGH)
        P.to_csv(OUT_BP, index=False)
        r.note("B. panel: %d high-usage player-seasons, %d treated (new high-usage partner), "
               "%d controls, %d distinct players"
               % (len(P), P.treated.sum(), (1 - P.treated).sum(), P.pid.nunique()))

        rows_b = []
        for moved in (None, 1, 0):
            sub = P if moved is None else P[P.moved == moved]
            for tr in (1, 0):
                s_ = sub[sub.treated == tr]
                rows_b.append(dict(
                    group="%s, %s" % ("all" if moved is None else
                                      ("changed teams" if moved else "stayed"),
                                      "new high-usage partner" if tr else "no new partner"),
                    moved=moved, treated=tr, n=len(s_),
                    usg_prev=s_.usg_prev.mean(), d_usg=s_.d_usg.mean(),
                    d_usg_se=s_.d_usg.std() / np.sqrt(len(s_)) if len(s_) > 1 else np.nan,
                    d_ts=s_.d_ts.mean(),
                    d_ts_se=s_.d_ts.std() / np.sqrt(len(s_)) if len(s_) > 1 else np.nan))
        adj, n_adj, n_tr, n_pl = adjusted(P, USG_HIGH)
        rows_b.append(dict(group="ADJUSTED pairing effect (prior usage, age, moved)",
                           threshold=USG_HIGH, n=n_adj, n_treated=n_tr, players=n_pl,
                           d_usg=adj["d_usg"][0], d_usg_se=adj["d_usg"][1],
                           d_ts=adj["d_ts"][0], d_ts_se=adj["d_ts"][1]))
        for thr in USG_SENS:
            res, n_s, tr_s, pl_s = adjusted(build_panel(thr), thr)
            rows_b.append(dict(group="SENSITIVITY adjusted effect, high usage >= %.2f" % thr,
                               threshold=thr, n=n_s, n_treated=tr_s, players=pl_s,
                               d_usg=res["d_usg"][0], d_usg_se=res["d_usg"][1],
                               d_ts=res["d_ts"][0], d_ts_se=res["d_ts"][1]))
        B = pd.DataFrame(rows_b)
        B.to_csv(OUT_B, index=False)
        for _, x in B.iterrows():
            r.note("   %-52s n %3d  d_usg %+.4f (%.4f)  d_ts %+.4f (%.4f)"
                   % (x.group, x.n, x.d_usg, x.d_usg_se, x.d_ts, x.d_ts_se))

        # who on Minnesota qualifies as high usage going into 2026-27
        hi_mn = [(CREATORS.get(p, name_all.get(p, p)), float(last.usg.get(p, np.nan)),
                  float(last.mins.get(p, np.nan)))
                 for p in list(mn.pid.head(8))]
        r.note("   Minnesota against the high-usage definition (usage >= %.2f over %d+ "
               "minutes, 2025-26): %s" % (USG_HIGH, MIN_PREV, "; ".join(
                   "%s %.3f/%.0f%s" % (n_, u_, m_, " HIGH" if u_ >= USG_HIGH and
                                         m_ >= MIN_PREV else "")
                   for n_, u_, m_ in hi_mn if pd.notna(u_))))

        # ============ C. CREATION SHARES =========================================
        likep = " or ".join("game_id like '002%s%%%%'" % k for k in ("23", "24", "25"))
        c = db.query(r"""
            select substr(game_id, 4, 2) yy, person_id::bigint pid, shot_value,
                   count(*) fgm,
                   count(*) filter (where description ~ '\([^()]* [0-9]+ AST\)') ast
            from (select distinct game_id, action_number, person_id, shot_value, description
                  from nba.nba_play_by_play
                  where (""" + likep + """) and is_field_goal = 1
                    and shot_result = 'Made') x
            group by 1, 2, 3""")
        for col in ("fgm", "ast", "shot_value"):
            c[col] = pd.to_numeric(c[col], errors="coerce")
        c["season"] = c.yy.map(SEASONS)
        fgm_box = db.query("""select player_id::bigint pid, season_year season, sum(fgm) fgm
                              from nba.nba_player_stats
                              where game_id like '002%%' and season_year in
                                    ('2023-24','2024-25','2025-26')
                              group by 1, 2""")
        fgm_box["fgm"] = pd.to_numeric(fgm_box.fgm)
        tot = c.groupby(["pid", "season"]).agg(fgm=("fgm", "sum"), ast=("ast", "sum"))
        chk = tot.join(fgm_box.set_index(["pid", "season"]).fgm.rename("box"), how="inner")
        gap = (chk.fgm - chk.box).abs().sum() / chk.box.sum()
        r.note("C. play-by-play made FG vs box-score FGM, all players 2023-26: "
               "absolute gap %.3f%% of %d makes" % (100 * gap, int(chk.box.sum())))
        if gap > 0.02:
            raise RuntimeError("play-by-play makes do not reconcile to the box score")

        def shares(frame):
            f2 = frame[frame.shot_value == 2]
            f3 = frame[frame.shot_value == 3]
            fg, a = frame.fgm.sum(), frame.ast.sum()
            return dict(fgm=int(fg), unast_share=1 - a / fg if fg else np.nan,
                        fgm2=int(f2.fgm.sum()),
                        unast2=1 - f2.ast.sum() / f2.fgm.sum() if f2.fgm.sum() else np.nan,
                        fgm3=int(f3.fgm.sum()),
                        unast3=1 - f3.ast.sum() / f3.fgm.sum() if f3.fgm.sum() else np.nan)

        lg26 = c[c.season == "2025-26"].groupby("pid").apply(
            lambda f: pd.Series(shares(f)), include_groups=False)
        ref = lg26[lg26.fgm >= FGM_REF]
        r.note("   league reference: %d players with %d+ makes in 2025-26, median "
               "unassisted share %.3f" % (len(ref), FGM_REF, ref.unast_share.median()))
        rows_c = []
        for pid, nm in CREATORS.items():
            for lab, frame in (("2025-26", c[(c.pid == pid) & (c.season == "2025-26")]),
                               ("2023-26 pooled", c[c.pid == pid])):
                s_ = shares(frame)
                s_.update(player=nm, pid=pid, window=lab,
                          box_fgm=int(chk.box[chk.index.get_level_values(0) == pid].sum())
                          if lab != "2025-26" else int(chk.box.get((pid, "2025-26"), 0)),
                          league_pct=pct_rank(ref.unast_share, s_["unast_share"])
                          if lab == "2025-26" and s_["fgm"] else np.nan,
                          league_median=float(ref.unast_share.median()),
                          usg_2025_26=float(last.usg.get(pid, np.nan)),
                          mins_2025_26=float(last.mins.get(pid, np.nan)),
                          games_2025_26=float(last.games.get(pid, np.nan)),
                          ts_2025_26=float(last.ts.get(pid, np.nan)))
                rows_c.append(s_)
                r.note("   %-18s %-15s makes %4d (box %4d)  unassisted %.3f  2s %.3f  3s %.3f"
                       "%s" % (nm, lab, s_["fgm"], s_["box_fgm"], s_["unast_share"],
                               s_["unast2"], s_["unast3"],
                               "  league pct %.0f" % s_["league_pct"]
                               if pd.notna(s_["league_pct"]) else ""))
        C = pd.DataFrame(rows_c)
        C.to_csv(OUT_C, index=False)

        # ============ THE DOC ====================================================
        r.output(OUT_A, rows=len(A))
        r.output(OUT_B, rows=len(B))
        r.output(OUT_BP, rows=len(P))
        r.output(OUT_C, rows=len(C))
        write_doc(r, A, B, P, C, q, five, ref, adj, top_ts)
        r.output(OUT_MD)


def write_doc(r, A, B, P, C, q, five, ref, adj, top_ts):
    def pts(v):
        return "%+.1f" % (100 * v)

    au = A.set_index("unit")
    top_label = [u for u in au.index if u.startswith("Projected top five")][0]
    kum_label = [u for u in au.index if u.startswith("Kuminga in")][0]
    best_label = [u for u in au.index if u.startswith("Highest-usage")][0]
    obs_label = [u for u in au.index if au.loc[u, "kind"] == "observed"][0]
    bg = B.set_index("group")
    main = bg.loc["ADJUSTED pairing effect (prior usage, age, moved)"]
    s28 = bg.loc[[g_ for g_ in bg.index if "0.28" in g_][0]]
    s22 = bg.loc[[g_ for g_ in bg.index if "0.22" in g_][0]]
    raw_t = bg.loc["all, new high-usage partner"]
    raw_c = bg.loc["all, no new partner"]
    mov_t = bg.loc["changed teams, new high-usage partner"]
    sty_t = bg.loc["stayed, new high-usage partner"]
    c26 = C[C.window == "2025-26"].set_index("player")
    c3 = C[C.window != "2025-26"].set_index("player")
    (t1, s1), v1 = list(top_ts.items())[0]

    L = []
    L.append("# M5: usage accounting\n")
    L.append("*As of 2026-09-16. Regular seasons 2022-23 to 2025-26 from the warehouse "
             "(`nba_player_advanced_stats`, `nba_player_stats`, `nba_play_by_play`). "
             "Run `%s`. OBSERVED = happened. PROJECTED = a five built from 2026-27 "
             "projected minutes and each player's 2025-26 rate. No model input: nothing "
             "here moves when the simulation chain re-runs.*\n" % r.run_id)
    L.append("| block | row | value | reference | where it sits | sample |")
    L.append("|---|---|---:|---|---|---|")
    for unit, x in au.iterrows():
        L.append("| A. Unit usage | **%s** (%s): %s | **%.3f** | league starting fives: "
                 "median %.3f, 90th pct %.3f, 99th %.3f | **percentile %.1f**; at "
                 "2023-26 rates %.3f, percentile %.1f | %s team-games, 2023-26 |"
                 % (unit, x.kind.upper(), x.players.replace("; ", ", "), x.usg_sum,
                    x.league_median, x.league_p90, x.league_p99, x.league_pct,
                    x.usg_sum_2023_26, x.league_pct_2023_26,
                    "{:,}".format(int(x.league_team_games))))
    labels = [
        ("all, new high-usage partner", "OBSERVED. Gained a new high-usage partner"),
        ("all, no new partner", "OBSERVED. No new high-usage partner (control)"),
        ("changed teams, new high-usage partner",
         "OBSERVED. Changed teams INTO a new pairing (Ball's case)"),
        ("changed teams, no new partner", "OBSERVED. Changed teams, no new partner"),
        ("stayed, new high-usage partner",
         "OBSERVED. Stayed while a high-usage player arrived (Edwards's case)"),
        ("stayed, no new partner", "OBSERVED. Stayed, no new partner"),
    ]
    for key, lab in labels:
        x = bg.loc[key]
        L.append("| B. Pairing base rates | %s: change on the season before | %s usage "
                 "pts (SE %.1f) | true shooting %s pts (SE %.1f) | prior usage %.3f | "
                 "%d player-seasons |"
                 % (lab, pts(x.d_usg), 100 * x.d_usg_se, pts(x.d_ts), 100 * x.d_ts_se,
                    x.usg_prev, x.n))
    for key in [g_ for g_ in bg.index if g_.startswith(("ADJUSTED", "SENSITIVITY"))]:
        x = bg.loc[key]
        L.append("| B. Pairing base rates | **Pairing effect, adjusted** for prior usage, "
                 "age and team change; high usage = %.2f or more%s | **%s usage pts** "
                 "(SE %.1f) | **true shooting %s pts** (SE %.1f) | SEs clustered by player "
                 "| %d player-seasons, %d treated, %d players |"
                 % (x.threshold, " (primary)" if key.startswith("ADJUSTED") else "",
                    pts(x.d_usg), 100 * x.d_usg_se, pts(x.d_ts), 100 * x.d_ts_se, x.n,
                    x.n_treated, x.players))
    for nm in c26.index:
        x = c26.loc[nm]
        L.append("| C. Creation | **%s**: unassisted share of made FGs, 2025-26 "
                 "(twos / threes) | **%.2f** (%.2f / %.2f) | league median %.2f; his "
                 "2023-26 pooled %.2f | **percentile %.0f** of %d | %d makes (box score "
                 "%d); usage %.3f, TS %.3f |"
                 % (nm, x.unast_share, x.unast2, x.unast3, x.league_median,
                    c3.loc[nm, "unast_share"], x.league_pct, len(ref), x.fgm, x.box_fgm,
                    x.usg_2025_26, x.ts_2025_26))
    L.append("")

    k = au.loc[kum_label]
    n_ts = five.groupby(["team", "season"]).ngroups
    higher_txt = ("higher than the median starting five of every one of the %d "
                  "team-seasons in that span" % n_ts
                  if k.team_seasons_with_higher_median == 0 else
                  "below the median starting five of %d of the %d team-seasons in "
                  "that span" % (k.team_seasons_with_higher_median, n_ts))
    zs = [abs(bg.loc[g_, c_] / bg.loc[g_, c_ + "_se"])
          for g_ in bg.index if g_.startswith(("ADJUSTED", "SENSITIVITY"))
          for c_ in ("d_usg", "d_ts")]
    clears_txt = ("None of the adjusted effects clears two standard errors at any "
                  "threshold (largest %.1f)." % max(zs) if max(zs) < 2 else
                  "At least one adjusted effect clears two standard errors (%.1f)."
                  % max(zs))
    for who in ("Anthony Edwards", "LaMelo Ball"):
        assert c26.loc[who, "usg_2025_26"] >= 0.28, who
    para = (
        "**What it shows.** Last season's usage rates do not fit on one floor. Minnesota's "
        "projected top five by minutes adds up to %.3f, above %.0f%% of the %s starting "
        "fives used in the last three regular seasons. Put Kuminga in for Dosunmu and it "
        "is %.3f (percentile %.1f), %s; the highest team-season median was %s %s at %.3f. "
        "At three-season rates, which do not let Kuminga's %d-game season set his share, "
        "that five is "
        "%.3f, percentile %.1f. So usage will be given up, and the question is what that "
        "has cost before. In %d player-seasons where a high-usage player gained a new "
        "high-usage partner, he lost %.1f points of usage against %.1f for high-usage "
        "players who did not. Most of that gap is who those players were (higher prior "
        "usage, more team changes). Adjusted for it, the pairing itself cost %.1f points "
        "of usage (SE %.1f) and %.1f points of true shooting (SE %.1f). Among stars only "
        "(high usage at 0.28 or more, where Edwards at %.3f and Ball at %.3f both sit), "
        "the usage cost is larger, %.1f points (SE %.1f), and efficiency still does not "
        "fall (%s, SE %.1f), though that rests on %d treated player-seasons. The players "
        "who changed teams into a pairing, Ball's case, "
        "lost the most usage (%.1f) and true shooting (%.1f), but players who changed "
        "teams without a new partner lost %.1f and %.1f, so most of that is the move. On "
        "creation, Edwards and Ball are the two self-creators: %.0f%% and %.0f%% of their "
        "baskets unassisted, percentiles %.0f and %.0f. "
        "Both create far more of their twos than their threes (Edwards %.0f%% and %.0f%%, "
        "Ball %.0f%% and %.0f%%). Kuminga (%.0f%%, percentile %.0f, on only %d makes) and "
        "Hyland (%.0f%%, percentile %.0f) are above the league median of %.0f%% but well "
        "short of the two stars; Dosunmu (%.0f%%) is at it. "
        "**What it does not show.** Whose usage gives, because there is no lineup table "
        "and every rate here is season-level on a team, not possessions with a given "
        "partner on the floor. Whether these %d player-seasons resemble this one: they are "
        "mostly deliberate star acquisitions, not random, and %d treated player-seasons "
        "is a small base. The changed-teams rows rest on %d and %d player-seasons. %s "
        "And nothing "
        "about defence, fit or winning: a pairing that costs no efficiency can still cost "
        "games. Kuminga does not meet the high-usage definition (%.3f over %.0f minutes), "
        "so the base rates speak to Edwards and Ball, not to him."
        % (au.loc[top_label, "usg_sum"],
           100 * (1 - au.loc[top_label, "share_league_at_or_above"]),
           "{:,}".format(int(k.league_team_games)), k.usg_sum, k.league_pct, higher_txt,
           t1, s1, v1, int(c26.loc["Jonathan Kuminga", "games_2025_26"]),
           k.usg_sum_2023_26, k.league_pct_2023_26,
           raw_t.n, -100 * raw_t.d_usg, -100 * raw_c.d_usg,
           -100 * main.d_usg, 100 * main.d_usg_se, -100 * main.d_ts, 100 * main.d_ts_se,
           c26.loc["Anthony Edwards", "usg_2025_26"], c26.loc["LaMelo Ball", "usg_2025_26"],
           -100 * s28.d_usg, 100 * s28.d_usg_se, pts(s28.d_ts), 100 * s28.d_ts_se,
           s28.n_treated,
           -100 * mov_t.d_usg, -100 * mov_t.d_ts,
           -100 * bg.loc["changed teams, no new partner", "d_usg"],
           -100 * bg.loc["changed teams, no new partner", "d_ts"],
           100 * c26.loc["Anthony Edwards", "unast_share"],
           100 * c26.loc["LaMelo Ball", "unast_share"],
           c26.loc["Anthony Edwards", "league_pct"], c26.loc["LaMelo Ball", "league_pct"],
           100 * c26.loc["Anthony Edwards", "unast2"],
           100 * c26.loc["Anthony Edwards", "unast3"],
           100 * c26.loc["LaMelo Ball", "unast2"], 100 * c26.loc["LaMelo Ball", "unast3"],
           100 * c26.loc["Jonathan Kuminga", "unast_share"],
           c26.loc["Jonathan Kuminga", "league_pct"], c26.loc["Jonathan Kuminga", "fgm"],
           100 * c26.loc["Nah'Shon Hyland", "unast_share"],
           c26.loc["Nah'Shon Hyland", "league_pct"],
           100 * c26.loc["Anthony Edwards", "league_median"],
           100 * c26.loc["Ayo Dosunmu", "unast_share"],
           raw_t.n, raw_t.n, mov_t.n, bg.loc["changed teams, no new partner", "n"], clears_txt,
           c26.loc["Jonathan Kuminga", "usg_2025_26"],
           c26.loc["Jonathan Kuminga", "mins_2025_26"]))
    L.append(para + "\n")
    L.append("*Definitions.* Usage is possession-weighted from game logs; a five's sum "
             "is the sum of its players' season rates, and a league starter's rate is his "
             "rate for that team that season. Starters carry more usage than the bench, "
             "so a starting five's sum normally runs above 1.00. Starters are read from "
             "the box score "
             "(exactly five per team-game, %s team-games, 2023-24 to 2025-26). High usage: %.2f or more over "
             "%d+ minutes the season before. Treated: %d+ minutes for the main team and "
             "%d+ shared games with a high-usage player he did not share a game with the "
             "season before. Adjusted effect: OLS of the change on treatment, prior usage, "
             "age and team change, standard errors clustered by player. Assisted: the "
             "play-by-play description names an assister; play-by-play makes reconcile "
             "to box-score FGM. Creation percentile among the %d players with %d+ makes. "
             "Detail: `outputs/m5_unit_usage.csv`, `m5_pairing_base_rates.csv`, "
             "`m5_pairing_panel.csv`, `m5_creation_shares.csv`.\n"
             % ("{:,}".format(len(five)), USG_HIGH, MIN_PREV, MIN_CUR, SHARED_MIN,
                len(ref), FGM_REF))
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
