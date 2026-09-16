#!/usr/bin/env python3
"""N3: playoff translation. Does anything beyond regular-season net rating predict how a
team plays in a playoff series, out of sample?

THE QUESTION. The playoff sim steps series on regular-season net rating. The folk claim is
that some teams "translate" better than their net rating says: defence travels, size
travels, a short rotation of stars travels. N3 tests that claim as main effects, at the
level of the playoff series, which is the unit the sim actually steps.

THE UNIT: ONE PLAYOFF SERIES. Oriented to the team with home court (home in game 1).
  y      mean per-game margin for that team across the series
  hc     1 for home court, 0 in the 2019-20 bubble (neutral site)
  dnet   regular-season net rating difference (per-game plus-minus, as M1 and F4d)
  dX     the candidate feature's difference, each feature z-scored within its season
Baseline: y = a*hc + b*dnet. Candidate: y = a*hc + b*dnet + c*dX, one feature at a time.

EIGHT CANDIDATES, FIXED BEFORE ANY FIT. The six M1 style features (rim rate, three-point
rate, pace, opponent turnover rate, offensive rebound rate, games-weighted size), the F4d
top-heaviness proxy (top-three share of team minutes), and one addition, DEFENCE SHARE:
the defensive component of a team's net rating minus its offensive component, so that at
equal net a positive value is a team built on defence. That is the "defence travels" claim
stated as a number, and it is added because it is the most-repeated translation claim and
the H1 sheet already carries ORtg and DRtg ranks.

TWO SAMPLES, AND WHICH ONE DECIDES.
  PRIMARY (as specified): the three postseasons of this project, 2024 to 2026, 45 series.
  LONGER HORIZON: 2014 to 2026, 13 postseasons, 195 series, the earliest season in which
  all eight features exist (shot locations and player tracking start in 2013-14). This is
  the longer-horizon check the H3 brief asks N3 to carry, and it is run because 45 series
  cannot detect an effect of plausible size; the minimum detectable effect is reported
  for both, so the reader can see that rather than take it on trust.

OUT OF SAMPLE, THREE WAYS. Leave-one-series-out (closed form), leave-one-postseason-out,
and a permutation test: the feature is shuffled across series within each postseason
(keeping net rating and home court fixed) PERMS times, and p is the share of shuffles
whose leave-one-out gain is at least the real one. With eight candidates, a feature must
clear p < 0.05 / 8 to count.

THE RULE, stated before the run. A feature TRANSLATES only if, on the longer horizon, its
leave-one-series-out AND leave-one-postseason-out gains are both positive and its
permutation p clears the Bonferroni line, AND its coefficient has the same sign on the
primary three-season sample. Anything that translates is scored for all 30 current
rosters and proposed as a series-step sensitivity, applied identically to all 30. If
nothing translates, nothing is scored, and the sim's net-rating series step stands.

A TEAM-LEVEL CHECK, the literal form of the brief: each playoff team-season's playoff
margin on its regular-season net, its opponents' games-weighted net, and the feature.

    python kuminga/scripts/n3_playoff_translation.py
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
M1_FEAT = os.path.join(OUT_DIR, "m1_style_features.csv")
OUT_FEAT = os.path.join(OUT_DIR, "n3_team_features.csv")
OUT_SER = os.path.join(OUT_DIR, "n3_series_frame.csv")
OUT_RES = os.path.join(OUT_DIR, "n3_translation_tests.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "n3_playoff_translation.md")

FIRST, LAST = 2013, 2025                     # season start years, 2013-14 .. 2025-26
PRIMARY = ["2023-24", "2024-25", "2025-26"]
BUBBLE = "2019-20"
FEATS = ["rim_rate", "fg3a_rate", "pace", "opp_tov_rate", "oreb_rate", "size", "top3",
         "def_share"]
WORDS = {"rim_rate": "rim rate", "fg3a_rate": "three-point rate", "pace": "pace",
         "opp_tov_rate": "turnovers forced", "oreb_rate": "offensive rebound rate",
         "size": "size", "top3": "top-three minutes share",
         "def_share": "defence share of net rating"}
PERMS = 2000
SEED = 20260916
ALPHA = 0.05 / len(FEATS)


def season_label(y):
    return "%d-%02d" % (y, (y + 1) % 100)


def zs(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 1e-9 else s * 0.0


def loo_mse(X, y):
    """Leave-one-out MSE for OLS, closed form via the hat matrix."""
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    h = np.einsum("ij,jk,ik->i", X, XtX_inv, X)
    return float(np.mean((e / (1.0 - h)) ** 2)), b


def group_cv_mse(X, y, groups):
    se = []
    for gval in np.unique(groups):
        tr, te = groups != gval, groups == gval
        b = np.linalg.pinv(X[tr].T @ X[tr]) @ X[tr].T @ y[tr]
        se.append((y[te] - X[te] @ b) ** 2)
    return float(np.mean(np.concatenate(se)))


def ols_se(X, y):
    b = np.linalg.pinv(X.T @ X) @ X.T @ y
    e = y - X @ b
    s2 = float(e @ e) / (len(y) - X.shape[1])
    return b, np.sqrt(np.diag(s2 * np.linalg.pinv(X.T @ X))), np.sqrt(s2)


def main():
    seasons = [season_label(y) for y in range(FIRST, LAST + 1)]
    rs_ids = {season_label(y): 20000 + y for y in range(FIRST, LAST + 1)}
    po_ids = {season_label(y): 40000 + y for y in range(FIRST, LAST + 1)}
    with runlog.run("n3_playoff_translation",
                    inputs={"seasons": [seasons[0], seasons[-1]], "primary": PRIMARY,
                            "features": FEATS, "perms": PERMS, "seed": SEED,
                            "alpha_bonferroni": ALPHA}) as r:
        g = db.query("""
            select game_id, season_id, team_id, team_abbreviation as team, matchup,
                   plus_minus, pts, fga, fg3a, fg3m, fta, oreb, dreb, tov
            from nba.nba_games where season_id in %(i)s
        """, {"i": tuple(list(rs_ids.values()) + list(po_ids.values()))})
        for c in ("plus_minus", "pts", "fga", "fg3a", "fg3m", "fta", "oreb", "dreb", "tov"):
            g[c] = pd.to_numeric(g[c], errors="coerce")
        g["season_id"] = pd.to_numeric(g.season_id)
        inv = {v: k for k, v in rs_ids.items()}
        inv.update({v: k for k, v in po_ids.items()})
        g["season"] = g.season_id.map(inv)
        g["is_po"] = g.season_id >= 40000
        g["home"] = (~g.matchup.str.contains("@")).astype(int)
        g = g.drop_duplicates(["game_id", "team"])
        opp = g[["game_id", "team", "pts", "fga", "fg3a", "fg3m", "fta", "oreb", "dreb",
                 "tov"]].copy()
        opp.columns = ["game_id"] + ["o_" + c for c in opp.columns[1:]]
        m = g.merge(opp, on="game_id")
        m = m[m.team != m.o_team].copy()
        r.note("team-game rows: %d regular season, %d playoff"
               % (int((~m.is_po).sum()), int(m.is_po.sum())))

        # ---- team-season features, regular season only ---------------------------
        rs = m[~m.is_po].copy()
        rs["poss"] = rs.fga - rs.oreb + rs.tov + 0.44 * rs.fta
        rs["o_poss"] = rs.o_fga - rs.o_oreb + rs.o_tov + 0.44 * rs.o_fta
        a = rs.groupby(["season", "team"]).agg(
            n=("game_id", "size"), net=("plus_minus", "mean"), fga=("fga", "sum"),
            fg3a=("fg3a", "sum"), fg3m=("fg3m", "sum"), o_fg3a=("o_fg3a", "sum"),
            o_fg3m=("o_fg3m", "sum"), oreb=("oreb", "sum"), o_dreb=("o_dreb", "sum"),
            o_tov=("o_tov", "sum"), o_fga=("o_fga", "sum"), pts=("pts", "sum"),
            o_pts=("o_pts", "sum"), poss=("poss", "sum"), o_poss=("o_poss", "sum"),
            team_id=("team_id", "first")).reset_index()
        a["fg3a_rate"] = a.fg3a / a.fga
        a["oreb_rate"] = a.oreb / (a.oreb + a.o_dreb)
        a["pace"] = (a.fga + a.o_fga) / (2.0 * a.n)          # M1's proxy, kept identical
        a["opp_tov_rate"] = a.o_tov / a.o_fga
        a["ortg"] = 100 * a.pts / a.poss
        a["drtg"] = 100 * a.o_pts / a.o_poss
        lg = a.groupby("season")[["ortg", "drtg"]].transform("mean")
        a["def_share"] = (lg.drtg - a.drtg) - (a.ortg - lg.ortg)
        # POST HOC ONLY (see the section below): three-point shooting luck on each side
        a["fg3_pct"] = a.fg3m / a.fg3a
        a["o_fg3_pct"] = a.o_fg3m / a.o_fg3a
        lg3 = a.groupby("season")[["fg3_pct", "o_fg3_pct"]].transform("mean")
        a["own3_luck"] = a.fg3_pct - lg3.fg3_pct
        a["opp3_luck"] = lg3.o_fg3_pct - a.o_fg3_pct     # positive = opponents missed

        sl = db.query("""
            select season_year as season, team_id, restricted_area_fga, paint_non_ra_fga,
                   midrange_fga, left_corner_3_fga, right_corner_3_fga, above_break_3_fga
            from nba.nba_team_shot_locations_season
            where season_type = 'Regular Season' and season_year in %(s)s
        """, {"s": tuple(seasons)})
        zc = ["restricted_area_fga", "paint_non_ra_fga", "midrange_fga",
              "left_corner_3_fga", "right_corner_3_fga", "above_break_3_fga"]
        for c in zc + ["team_id"]:
            sl[c] = pd.to_numeric(sl[c], errors="coerce")
        sl["rim_rate"] = sl.restricted_area_fga / sl[zc].sum(axis=1)
        a["team_id"] = pd.to_numeric(a.team_id)
        a = a.merge(sl[["season", "team_id", "rim_rate"]], on=["season", "team_id"],
                    how="left")

        bio = db.query("""
            select season_year as season, team_abbreviation as team,
                   sum(player_height_inches * gp) / nullif(sum(gp), 0) as size
            from nba.nba_player_season_bio
            where season_type = 'Regular Season' and season_year in %(s)s
              and player_height_inches is not null and gp > 0
            group by 1, 2
        """, {"s": tuple(seasons)})
        bio["size"] = pd.to_numeric(bio["size"], errors="coerce")
        a = a.merge(bio, on=["season", "team"], how="left")

        tr = db.query("""
            select season_year as season, team_abbreviation as team, player_id, min
            from nba.nba_player_tracking_season
            where season_type = 'Regular Season' and season_year in %(s)s
        """, {"s": tuple(seasons)})
        tr["min"] = pd.to_numeric(tr["min"], errors="coerce")
        # F4d's two traps: one row per tracking category, and `min` is already a total
        tr = tr.drop_duplicates(["season", "team", "player_id"]).dropna(subset=["min"])
        top = tr.groupby(["season", "team"])["min"].apply(
            lambda v: float(v.sort_values(ascending=False).head(3).sum() / v.sum()))
        a = a.merge(top.rename("top3").reset_index(), on=["season", "team"], how="left")

        missing = {f: int(a[f].isna().sum()) for f in FEATS}
        r.note("team-seasons %d; missing per feature: %s" % (len(a), missing))
        if any(v > 0 for v in missing.values()):
            bad = a[a[FEATS].isna().any(axis=1)][["season", "team"] + FEATS]
            r.note("  unresolved rows:\n%s" % bad.to_string(index=False))
            raise RuntimeError("feature coverage incomplete; fix the joins before testing")
        raw = a[["season", "team", "net", "ortg", "drtg"] + FEATS].copy()
        for f in FEATS + ["own3_luck", "opp3_luck"]:
            a[f] = a.groupby("season")[f].transform(zs)
        a[["season", "team", "net"] + FEATS].to_csv(OUT_FEAT, index=False)

        # reproducibility gate: the six style features must match M1's file exactly
        if os.path.exists(M1_FEAT):
            m1 = pd.read_csv(M1_FEAT)
            chk = m1.merge(a, on=["season", "team"], suffixes=("_m1", ""))
            diffs = {f: float((chk[f + "_m1"] - chk[f]).abs().max())
                     for f in ["rim_rate", "fg3a_rate", "pace", "opp_tov_rate",
                               "oreb_rate", "size"]}
            r.note("gate: max abs difference from M1's style features over %d "
                   "team-seasons: %s" % (len(chk), {k: round(v, 9) for k, v in
                                                     diffs.items()}))
            if max(diffs.values()) > 1e-6:
                raise RuntimeError("N3 features do not reproduce M1's")

        # ---- the series frame ------------------------------------------------------
        po = m[m.is_po].copy()
        po["series"] = po.game_id.str[:9]
        po["game_no"] = po.game_id.str[9].astype(int)
        s_teams = po.groupby("series").team.nunique()
        if not (s_teams == 2).all():
            raise RuntimeError("a series key does not resolve to exactly two teams")
        g1 = po[(po.game_no == 1) & (po.home == 1)][["series", "team", "o_team"]]
        ser = po.merge(g1.rename(columns={"team": "A", "o_team": "B"}), on="series")
        ser = ser[ser.team == ser.A]
        S = ser.groupby(["season", "series", "A", "B"]).agg(
            y=("plus_minus", "mean"), games=("game_id", "nunique"),
            wins=("plus_minus", lambda v: int((v > 0).sum()))).reset_index()
        S["a_won"] = (S.wins * 2 > S.games).astype(int)
        S["round"] = S.series.str[7].astype(int)
        S["hc"] = (S.season != BUBBLE).astype(float)
        F = a.set_index(["season", "team"])
        for side in ("A", "B"):
            idx = list(zip(S.season, S[side]))
            S["net_" + side] = F.net.reindex(idx).to_numpy()
            for f in FEATS + ["own3_luck", "opp3_luck"]:
                S[f + "_" + side] = F[f].reindex(idx).to_numpy()
        S = S.dropna()
        S["dnet"] = S.net_A - S.net_B
        for f in FEATS + ["own3_luck", "opp3_luck"]:
            S["d_" + f] = S[f + "_A"] - S[f + "_B"]
        S.to_csv(OUT_SER, index=False)
        per = S.groupby("season").size()
        r.note("series: %d across %d postseasons (%s per postseason); games per series "
               "%d to %d; bubble %s kept with home court set to zero"
               % (len(S), S.season.nunique(), "/".join(str(v) for v in per.unique()),
                  S.games.min(), S.games.max(), BUBBLE))
        if not (per == 15).all():
            raise RuntimeError("a postseason does not have exactly 15 series")

        # ---- the tests -----------------------------------------------------------
        rng = np.random.default_rng(SEED)
        rows = []
        samples = [("primary 2024-26", S[S.season.isin(PRIMARY)].reset_index(drop=True)),
                   ("longer 2014-26", S.reset_index(drop=True))]
        for lab, d in samples:
            y = d.y.to_numpy(float)
            X0 = np.column_stack([d.hc, d.dnet])
            base_loo, b0 = loo_mse(X0, y)
            base_lopo = group_cv_mse(X0, y, d.season.to_numpy())
            _, se0, sig0 = ols_se(X0, y)
            r.note("")
            r.note("%s: %d series | baseline home court %+.2f, per net point %+.3f | "
                   "residual SD %.2f pts/game | LOO MSE %.2f, LOPO MSE %.2f"
                   % (lab, len(d), b0[0], b0[1], sig0, base_loo, base_lopo))
            seasons_arr = d.season.to_numpy()
            for f in FEATS:
                x = d["d_" + f].to_numpy(float)
                X1 = np.column_stack([d.hc, d.dnet, x])
                loo1, b1 = loo_mse(X1, y)
                lopo1 = group_cv_mse(X1, y, seasons_arr)
                bb, se, _ = ols_se(X1, y)
                gain = base_loo - loo1
                cnt = 0
                for _ in range(PERMS):
                    xp = x.copy()
                    for sv in np.unique(seasons_arr):
                        ix = np.where(seasons_arr == sv)[0]
                        xp[ix] = x[rng.permutation(ix)]
                    lp, _ = loo_mse(np.column_stack([d.hc, d.dnet, xp]), y)
                    cnt += (base_loo - lp) >= gain
                p = (cnt + 1) / (PERMS + 1)
                rows.append(dict(
                    sample=lab, feature=f, n_series=len(d), coef=float(bb[2]),
                    coef_se=float(se[2]), mde80=2.8 * float(se[2]),
                    sd_dfeature=float(x.std(ddof=0)),
                    loo_gain=gain, loo_gain_pct=100 * gain / base_loo,
                    lopo_gain=base_lopo - lopo1,
                    lopo_gain_pct=100 * (base_lopo - lopo1) / base_lopo,
                    perm_p=p, clears_bonferroni=bool(p < ALPHA)))
                x_ = rows[-1]
                r.note("  %-13s coef %+.2f (SE %.2f, MDE80 %.2f) per z | LOO gain %+.3f "
                       "(%+.1f%%) | LOPO gain %+.3f (%+.1f%%) | perm p %.4f%s"
                       % (f, x_["coef"], x_["coef_se"], x_["mde80"], x_["loo_gain"],
                          x_["loo_gain_pct"], x_["lopo_gain"], x_["lopo_gain_pct"], p,
                          "  CLEARS" if p < ALPHA else ""))
        T = pd.DataFrame(rows)

        # ---- the decision -------------------------------------------------------------
        lo = T[T["sample"] == "longer 2014-26"].set_index("feature")
        pr = T[T["sample"] == "primary 2024-26"].set_index("feature")
        verdict = {}
        for f in FEATS:
            ok = (lo.loc[f, "loo_gain"] > 0 and lo.loc[f, "lopo_gain"] > 0
                  and lo.loc[f, "perm_p"] < ALPHA
                  and np.sign(lo.loc[f, "coef"]) == np.sign(pr.loc[f, "coef"]))
            verdict[f] = bool(ok)
        T["translates"] = T.feature.map(verdict)
        T.to_csv(OUT_RES, index=False)
        passed = [f for f, v in verdict.items() if v]
        r.note("")
        r.note("TRANSLATES under the pre-stated rule: %s"
               % (", ".join(passed) if passed else "NONE"))

        # ---- team-level check, the literal form of the brief ----------------------------
        tl = []
        for side, o in (("A", "B"), ("B", "A")):
            t_ = S[["season", "games", side, o]].copy()
            t_.columns = ["season", "games", "team", "opp"]
            t_["margin_sum"] = S.y * S.games * (1 if side == "A" else -1)
            tl.append(t_)
        tl = pd.concat(tl)
        tl = tl.merge(a[["season", "team", "net"]], on=["season", "team"])
        tl = tl.merge(a[["season", "team", "net"]].rename(
            columns={"team": "opp", "net": "opp_net"}), on=["season", "opp"])
        tl["opp_net_w"] = tl.opp_net * tl.games
        TT = tl.groupby(["season", "team"]).agg(
            games=("games", "sum"), margin=("margin_sum", "sum"),
            opp_net=("opp_net_w", "sum"), net=("net", "first")).reset_index()
        TT["po_margin"] = TT.margin / TT.games
        TT["opp_net"] = TT.opp_net / TT.games
        TT = TT.merge(a[["season", "team"] + FEATS], on=["season", "team"])
        team_rows = []
        for lab, d in (("primary 2024-26", TT[TT.season.isin(PRIMARY)]),
                       ("longer 2014-26", TT)):
            d = d.reset_index(drop=True)
            y = d.po_margin.to_numpy(float)
            X0 = np.column_stack([np.ones(len(d)), d.net, d.opp_net])
            b0l, _ = loo_mse(X0, y)
            for f in FEATS:
                X1 = np.column_stack([X0, d[f]])
                l1, _ = loo_mse(X1, y)
                bb, se, _ = ols_se(X1, y)
                team_rows.append(dict(sample=lab, feature=f, n_team_seasons=len(d),
                                      coef=float(bb[3]), coef_se=float(se[3]),
                                      loo_gain_pct=100 * (b0l - l1) / b0l))
        TL = pd.DataFrame(team_rows)
        TL.to_csv(OUT_RES.replace(".csv", "_team_level.csv"), index=False)
        r.note("team-level check (playoff margin on RS net, opponents' net, feature):")
        for _, x in TL.iterrows():
            r.note("  %-16s %-13s n %3d coef %+.2f (SE %.2f) LOO gain %+.1f%%"
                   % (x["sample"], x.feature, x.n_team_seasons, x.coef, x.coef_se,
                      x.loo_gain_pct))

        # ---- POST HOC, labelled as such: the one near-miss, stress-tested -----------
        # Chosen AFTER seeing the results, so nothing here can promote a feature past
        # the pre-stated rule. Two questions. (1) The rule's sign check used the primary
        # seasons, which sit INSIDE the longer sample, so it was not an independent
        # replication; the non-overlapping 2014-23 window is. (2) A defensive rating
        # carries more shooting luck than an offensive one (opponents' three-point
        # percentage is mostly outside a defence's control), so a defence-built net
        # rating may simply regress. Adding each side's three-point luck tests that.
        ph = []
        early = S[~S.season.isin(PRIMARY)].reset_index(drop=True)
        for lab, d, extra in (
                ("2014-23 only (non-overlapping)", early, []),
                ("2024-26 only", S[S.season.isin(PRIMARY)].reset_index(drop=True), []),
                ("2014-26, + both teams' three-point luck", S.reset_index(drop=True),
                 ["d_own3_luck", "d_opp3_luck"]),
                ("2014-26, + opponents' three-point luck only", S.reset_index(drop=True),
                 ["d_opp3_luck"])):
            y = d.y.to_numpy(float)
            X = np.column_stack([d.hc, d.dnet, d.d_def_share] + [d[c] for c in extra])
            bb, se, _ = ols_se(X, y)
            X0 = np.column_stack([d.hc, d.dnet] + [d[c] for c in extra])
            l0, _ = loo_mse(X0, y)
            l1, _ = loo_mse(X, y)
            row = dict(check=lab, n_series=len(d), def_share_coef=float(bb[2]),
                       def_share_se=float(se[2]),
                       loo_gain_pct=100 * (l0 - l1) / l0)
            for j, c in enumerate(extra):
                row[c + "_coef"] = float(bb[3 + j])
                row[c + "_se"] = float(se[3 + j])
            ph.append(row)
        PH = pd.DataFrame(ph)
        PH.to_csv(OUT_RES.replace(".csv", "_posthoc.csv"), index=False)
        r.note("")
        r.note("POST HOC, defence share (cannot change the verdict):")
        for _, x in PH.iterrows():
            r.note("  %-44s n %3d | def_share %+.2f (SE %.2f) | LOO gain %+.1f%%%s"
                   % (x.check, x.n_series, x.def_share_coef, x.def_share_se,
                      x.loo_gain_pct, "".join(
                          " | %s %+.2f (SE %.2f)" % (c, x[c + "_coef"], x[c + "_se"])
                          for c in ("d_own3_luck", "d_opp3_luck")
                          if c + "_coef" in x and pd.notna(x[c + "_coef"]))))
        r.output(OUT_RES.replace(".csv", "_posthoc.csv"), rows=len(PH))

        r.output(OUT_FEAT, rows=len(a))
        r.output(OUT_SER, rows=len(S))
        r.output(OUT_RES, rows=len(T))
        r.output(OUT_RES.replace(".csv", "_team_level.csv"), rows=len(TL))
        write_doc(r, T, TL, PH, S, a, passed)
        r.output(OUT_MD)


def write_doc(r, T, TL, PH, S, a, passed):
    lo = T[T["sample"] == "longer 2014-26"].set_index("feature")
    pr = T[T["sample"] == "primary 2024-26"].set_index("feature")
    tl = TL.set_index(["sample", "feature"])
    ph = PH.set_index("check")
    n_pr, n_lo = int(pr.n_series.iloc[0]), int(lo.n_series.iloc[0])
    ds = lo.loc["def_share"]
    ds_early = ph.loc["2014-23 only (non-overlapping)"]
    ds_late = ph.loc["2024-26 only"]
    ds_luck = ph.loc["2014-26, + both teams' three-point luck"]
    y = S.y.to_numpy(float)
    X0 = np.column_stack([S.hc, S.dnet])
    b0, _, sig_lo = ols_se(X0, y)
    Sp = S[S.season.isin(PRIMARY)]
    _, _, sig_pr = ols_se(np.column_stack([Sp.hc, Sp.dnet]), Sp.y.to_numpy(float))
    ci_hi = ds.coef + 1.96 * ds.coef_se
    mn = a[(a.team == "MIN")].set_index("season").def_share
    rim_pr = tl.loc[("primary 2024-26", "rim_rate")]
    rim_lo = tl.loc[("longer 2014-26", "rim_rate")]

    L = []
    L.append("# N3: playoff translation\n")
    L.append("*As of 2026-09-16. Warehouse `nba_games`, `nba_team_shot_locations_season`, "
             "`nba_player_season_bio`, `nba_player_tracking_season`; regular seasons and "
             "playoffs 2013-14 to 2025-26. Run `%s`. Every number here is OBSERVED "
             "history or a fit to it; nothing is modelled for 2026-27.*\n" % r.run_id)
    L.append("**In plain terms.** The playoff sim moves each series on regular-season net "
             "rating. The question is whether anything else about a team (how it plays, "
             "how big it is, how few players carry it, whether its rating comes from "
             "defence) predicts how it does in a series once net rating is known. "
             "**Nothing does, by the rule set before the test was run.** %s. So the sim's "
             "series step stands as it is, the same for all 30 teams, and no roster is "
             "scored on a translation feature, because there is no translation feature "
             "to score. One result is worth knowing anyway: **the old line that defence "
             "travels is not supported. The estimate points the other way**, in two "
             "separate windows of history, and three-point shooting luck does not explain it. It "
             "still falls short of the bar, so it changes nothing in the model.\n"
             % ("Eight candidates were tested on the %d series of this project's three "
                "postseasons and on %d series going back to 2014; none adds out-of-sample "
                "signal that survives the correction for testing eight things at once"
                % (n_pr, n_lo)))

    L.append("| feature | %d series, 2024-26: coef (SE) | out-of-sample gain, series / "
             "postseason | %d series, 2014-26: coef (SE) | smallest effect it could "
             "detect | out-of-sample gain, series / postseason | permutation p | "
             "translates |" % (n_pr, n_lo))
    L.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for f in FEATS:
        x, z = pr.loc[f], lo.loc[f]
        L.append("| %s | %+.2f (%.2f) | %+.1f%% / %+.1f%% | **%+.2f** (%.2f) | %.2f | "
                 "%+.1f%% / %+.1f%% | %.3f | %s |"
                 % (WORDS[f], x.coef, x.coef_se, x.loo_gain_pct, x.lopo_gain_pct,
                    z.coef, z.coef_se, z.mde80, z.loo_gain_pct, z.lopo_gain_pct,
                    z.perm_p, "**yes**" if f in passed else "no"))
    L.append("")
    L.append("*Coefficients are points of series margin per game per one standard "
             "deviation of the feature difference (features z-scored within season), "
             "on top of home court and the net-rating difference. Out-of-sample gain is "
             "the drop in held-out squared error against net rating alone; negative "
             "means the feature made predictions worse. The bar is permutation p below "
             "%.4f (0.05 across eight tests), positive gain both ways on the longer "
             "sample, and the same sign on the three seasons.*\n" % ALPHA)

    L.append("**How small the sample is, as numbers.** %d series in the three "
             "postseasons, with a residual spread of %.1f points per game after net "
             "rating. At that size the test could only detect an effect of about %.1f to "
             "%.1f points per game per standard deviation, larger than the whole "
             "home-court edge over 13 postseasons (%+.2f). The %d-series sample brings "
             "that to %.2f to %.2f. So the three-season null means little on its own; "
             "the 13-season null means translation effects larger than about one point "
             "per game per standard deviation are unlikely for these eight features.\n"
             % (n_pr, sig_pr, pr.mde80.min(), pr.mde80.max(), b0[0], n_lo,
                lo.mde80.min(), lo.mde80.max()))

    L.append("**Top-heaviness (the F4d question).** Top-three minutes share: %+.2f "
             "(SE %.2f) over %d series, out-of-sample gain %+.1f%%, p %.2f. F4d's "
             "one-postseason null holds on thirteen. No series-step adjustment is "
             "proposed.\n" % (lo.loc["top3", "coef"], lo.loc["top3", "coef_se"], n_lo,
                              lo.loc["top3", "loo_gain_pct"], lo.loc["top3", "perm_p"]))

    L.append("**Defence share, the near miss (post hoc, cannot change the verdict).** "
             "At equal net rating, a team whose rating leans on defence did **%.2f "
             "points per game worse per standard deviation** in its series (SE %.2f, "
             "p %.3f against a bar of %.4f), worth about %.1f points of regular-season "
             "net rating. Its single-test 95%% interval tops out at %+.2f, so the data are not "
             "consistent with defence-built teams translating better. Two checks were "
             "chosen after seeing this, and are labelled that way. The rule's sign check "
             "used the three recent postseasons, which sit inside the longer sample, so "
             "it was not an independent replication; the non-overlapping 2014-23 window "
             "gives **%+.2f (SE %.2f)** on %d series against **%+.2f (SE %.2f)** on %d "
             "for 2024-26, nearly identical. And because a defensive rating carries more "
             "shooting luck than an offensive one, both teams' three-point luck was "
             "added: the estimate barely moves (%+.2f, SE %.2f), and the luck terms "
             "themselves are near zero. Minnesota's regular-season rating leaned on "
             "defence in each of the last three seasons (z %s), most in 2023-24. That is "
             "context, not a score: the feature did not pass, and a 2026-27 value would "
             "come from the model's offence and defence split, which is not computed "
             "here.\n"
             % (-ds.coef, ds.coef_se, ds.perm_p, ALPHA, -ds.coef / b0[1], ci_hi,
                ds_early.def_share_coef, ds_early.def_share_se, int(ds_early.n_series),
                ds_late.def_share_coef, ds_late.def_share_se, int(ds_late.n_series),
                ds_luck.def_share_coef, ds_luck.def_share_se,
                ", ".join("%+.2f in %s" % (mn[s_], s_) for s_ in PRIMARY)))

    L.append("**The team-level check, and a mirage it catches.** In the literal form of "
             "the brief (each playoff team's margin on its own net, its opponents' net "
             "and the feature), rim rate looks like it translates on the three recent "
             "postseasons: %+.2f (SE %.2f), out-of-sample gain %+.1f%% on %d "
             "team-seasons. Over 13 postseasons it is %+.2f (SE %.2f) with a gain of "
             "%+.1f%%. That is what a three-season sample does, and it is why the longer "
             "sample decides.\n"
             % (rim_pr.coef, rim_pr.coef_se, rim_pr.loo_gain_pct,
                int(rim_pr.n_team_seasons), rim_lo.coef, rim_lo.coef_se,
                rim_lo.loo_gain_pct))

    L.append("**What it does not show.** Matchup effects: these are main effects, and "
             "M1 already found the style interactions carry nothing out of sample. "
             "Anything about players: a team's style is last season's team, not this "
             "season's roster. Injuries during the playoffs, which move series and are "
             "not in any feature. And translation effects smaller than about one point "
             "per game per standard deviation, which 195 series cannot rule out.\n")

    L.append("*Definitions.* Series oriented to the team at home in game 1; margin is "
             "the mean per-game plus-minus across the series. Net rating is regular-season "
             "per-game plus-minus. Features, regular season, z-scored within season: rim "
             "rate (restricted-area share of shots), three-point rate, pace (M1's "
             "shot-based proxy), turnovers forced per opponent shot, offensive rebound "
             "rate, games-weighted height, top-three share of team minutes (F4d's "
             "proxy), and defence share, (league DRtg minus DRtg) minus (ORtg minus "
             "league ORtg), from estimated possessions. The six style features reproduce "
             "M1's exactly on 2023-26. Home court is zero for the 2019-20 bubble. "
             "Out of sample: leave one series out, leave one postseason out, and %d "
             "within-postseason permutations. Detail: `outputs/n3_translation_tests.csv`, "
             "`n3_translation_tests_team_level.csv`, `n3_translation_tests_posthoc.csv`, "
             "`n3_series_frame.csv`, `n3_team_features.csv`.\n" % PERMS)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
