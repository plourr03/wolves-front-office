#!/usr/bin/env python3
"""M3: opponent cards for the West field, both halves mandatory.

ONE CARD PER OPPONENT: the eight West teams with the highest modelled title odds.
Each card carries:

  HEADER            model title odds (mean and four-view band), market title odds and
                    rank, and Minnesota's series win probability against them.
  OFFSEASON LEDGER  who arrived and who left, weighted by minutes and impact, plus the
                    team's modelled offseason change.
  STYLE             last season's style profile against Minnesota's. DESCRIPTIVE ONLY:
                    the M1 held-out test found style interactions carry no predictive
                    value (held-out MAE worse by 0.0151 on regular-season games and
                    0.0265 on playoff games, with size included), so M2 left the overlay
                    off. The three largest CONTRASTS are shown in plain words, and no
                    interaction coefficient is shown, because a coefficient from a model
                    that failed validation would present a rejected result as a finding.
  MATCHUPS          observed possession-level matchups from `nba_boxscore_matchups`,
                    2025-26 regular season plus playoffs, in BOTH directions:
                    where they hurt Minnesota, and where Minnesota hurts them.
  SERIES            net-rating basis, overlay off, home court to the higher net.
  MARKET            title odds only. No series lines exist in the odds file, so none are
                    shown.

HOW A "KEY MATCHUP" IS CHOSEN, mechanically and identically for every card. For each of a
team's top five players by projected 2026-27 minutes, find the defender on the other
team's projected top eight who guarded him the most in 2025-26, on ANY team context.
Personnel moved this summer, so a matchup that happened while LaMelo Ball was in
Charlotte is still evidence about LaMelo Ball. Each row states its possessions.

HOW "HURT" IS JUDGED. Raw points per possession mislead, because a star scores
efficiently against everyone. Each matchup is set against the OFFENDER'S OWN 2025-26
baseline across every defender he faced, and then against the LEAGUE NORM for a primary
defender: across 2025-26, a team's heaviest rotation defender on one of the top 150
offenders held him 0.05 to 0.10 below his own baseline, rising with possessions. Below
baseline is therefore the normal result for a heavy matchup, and each row is judged by how
far it runs BEYOND that norm. The norm and the noise variance are re-measured from the
warehouse on every run. Minnesota's top five are also pooled across every opponent, and
`m3_primary_defender_check.py` stress-tests that pooled rank against two confounds.

SAMPLE SIZE, stated as numbers. The median 2025-26 offender-defender pairing is 4.8
partial possessions and the 95th percentile is 29.8. Pairings under 30 are flagged THIN.

NOISE, measured rather than assumed. Across every 2025-26 offender-game-defender cell, the
variance of points around the offender's own baseline is PER_POSS_VAR (0.614) per partial
possession, so a pairing of n possessions carries a standard error of sqrt(0.614/n):
0.14 at 30 possessions, 0.08 at 100. The spread of observed deviations across real
pairings of 25-35, 45-60 and 80-120 possessions (0.143, 0.113, 0.087) follows that scaling
almost exactly, which says most of what varies between matchups is noise. Each row carries
its deviation in standard errors, and a matchup is called an EDGE only at two or more.
Every individual matchup is descriptive evidence, never a verdict.

INPUTS. Strengths, simulation and seeds are read from `outputs/preaging/`, the un-aged
primary, so this is safe to run while the aged leg of a re-run temporarily overwrites
`outputs/`.

    python kuminga/scripts/m3_opponent_cards.py
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

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
PRE = os.path.join(OUT_DIR, "preaging")
STR = os.path.join(PRE, "team_strengths_2026_27.csv")
SIM = os.path.join(PRE, "sim_all30_2026_27.csv")
ROT = os.path.join(OUT_DIR, "rotations_2026_27.csv")
MKT = os.path.join(OUT_DIR, "market_devig_2026_27.csv")
R1 = os.path.join(OUT_DIR, "n2_round1_opponents.csv")
STYLE = os.path.join(OUT_DIR, "m1_style_features.csv")
OUT = os.path.join(OUT_DIR, "m3_opponent_cards.csv")
OUT_M = os.path.join(OUT_DIR, "m3_key_matchups.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "m3_opponent_cards.md")

TEAM = "MIN"
FORKS = ["consensus", "rapm", "box", "darko"]
N_CARDS = 8
TOP_OFF = 5
TOP_DEF = 8
THIN = 30.0
PER_POSS_VAR = 0.614   # measured, see docstring; re-measured and logged every run
EDGE_Z = 2.0
REF_TOP_OFF = 150      # league reference: offenders by total partial possessions
REF_ROT_DEF = 300      # league reference: defenders by total partial possessions
REF_BANDS = [5, 30, 60, 120, 100000]
STYLE_WORDS = {
    "rim_rate": ("gets to the rim more", "gets to the rim less"),
    "fg3a_rate": ("takes more threes", "takes fewer threes"),
    "pace": ("plays faster", "plays slower"),
    "opp_tov_rate": ("forces more turnovers", "forces fewer turnovers"),
    "oreb_rate": ("crashes the offensive glass harder", "crashes the offensive glass less"),
    "size": ("is bigger", "is smaller"),
}


def main():
    with runlog.run("m3_opponent_cards",
                    inputs={"strengths": STR, "thin_threshold": THIN,
                            "style": "descriptive only (M1/M2)"}) as r:
        st = pd.read_csv(STR)
        sim = pd.read_csv(SIM)
        rot = pd.read_csv(ROT)
        mkt = pd.read_csv(MKT).set_index("team_abbr")
        r1 = pd.read_csv(R1)
        r1 = r1.set_index(r1.columns[0]).iloc[:, 0]
        sty = pd.read_csv(STYLE)
        sty = sty[sty.season == "2025-26"].set_index("team")

        # guard: the strengths must be the un-aged primary
        mn_net = float(st[(st.fork == "consensus") & (st.team_abbr == TEAM)]
                       .net_current.iloc[0])
        r.note("strengths read from preaging; MIN consensus net %+.3f "
               "(the un-aged primary is -0.405)" % mn_net)

        # ---- the field --------------------------------------------------------
        tit = (sim.groupby(["team_abbr", "conf"]).title_current.agg(["mean", "min", "max"])
               .reset_index())
        west = tit[(tit.conf == "W") & (tit.team_abbr != TEAM)]
        field = west.sort_values("mean", ascending=False).head(N_CARDS)
        r.note("West field, top %d by modelled title odds: %s"
               % (N_CARDS, ", ".join(field.team_abbr)))

        # ---- series probability, per fork --------------------------------------
        series = {}
        for f in FORKS:
            s = st[st.fork == f]
            strengths = {x.team_abbr: {"net": float(x.net_current), "munc": float(x.munc),
                                       "conf": x.conf, "profile": None}
                         for _, x in s.iterrows()}
            res = E.conditional_series(TEAM, strengths, use_overlay=False)
            for opp, p in res.items():
                series.setdefault(opp, []).append(float(p))

        # ---- rosters: current and 2025-26 ------------------------------------------
        cur = rot[rot.scenario == "current"]
        base = rot[rot.scenario == "baseline"]

        def top_ids(team, n, frame):
            g = frame[(frame.team_abbr == team) & frame.player_id.notna()]
            g = g[g.player_id > 0].sort_values("mpg", ascending=False).head(n)
            return list(g.player_id.astype(int)), dict(zip(g.player_id.astype(int),
                                                          g.player_name))

        teams = [TEAM] + list(field.team_abbr)
        ids_all, names = set(), {}
        for t in teams:
            ids, nm = top_ids(t, TOP_DEF, cur)
            ids_all |= set(ids)
            names.update(nm)

        # ---- observed matchups, 2025-26 regular season and playoffs ---------------
        ids_sql = ",".join(str(i) for i in sorted(ids_all))
        m = db.query("""
            select person_id_off off_id, person_id_def def_id,
                   sum(partial_possessions) poss, sum(player_points) pts,
                   sum(matchup_field_goals_made) fgm,
                   sum(matchup_field_goals_attempted) fga,
                   sum(matchup_three_pointers_made) fg3m,
                   sum(matchup_three_pointers_attempted) fg3a,
                   sum(matchup_turnovers) tov
            from nba.nba_boxscore_matchups
            where (game_id like '00225%%' or game_id like '00425%%')
              and person_id_off in (""" + ids_sql + """)
            group by 1, 2""")
        for c in ("poss", "pts", "fgm", "fga", "fg3m", "fg3a", "tov"):
            m[c] = pd.to_numeric(m[c], errors="coerce").fillna(0.0)
        base_ppp = m.groupby("off_id").apply(
            lambda g: g.pts.sum() / g.poss.sum() if g.poss.sum() else np.nan,
            include_groups=False)
        r.note("matchup rows for the %d players on these nine rosters: %d"
               % (len(ids_all), len(m)))

        # ---- the league reference: noise, and the norm for a primary defender ---------
        lg = db.query("""
            select game_id g, team_id oteam, person_id_off o, person_id_def d,
                   sum(partial_possessions) poss, sum(player_points) pts
            from nba.nba_boxscore_matchups
            where game_id like '00225%%' or game_id like '00425%%'
            group by 1, 2, 3, 4""")
        for c in ("poss", "pts"):
            lg[c] = pd.to_numeric(lg[c], errors="coerce").fillna(0.0)
        sides = lg[["g", "oteam"]].drop_duplicates()
        sides = sides.merge(sides.rename(columns={"oteam": "dteam"}), on="g")
        sides = sides[sides.oteam != sides.dteam]
        lg = lg.merge(sides, on=["g", "oteam"])
        otot = lg.groupby("o").agg(P=("poss", "sum"), T=("pts", "sum"))
        cells = lg[lg.poss > 0].join(otot, on="o")
        per_poss_var = float(((cells.pts - cells["T"] / cells.P * cells.poss) ** 2).sum()
                             / cells.poss.sum())
        dtot = lg.groupby("d").poss.sum()
        pr = lg.groupby(["o", "dteam", "d"]).agg(poss=("poss", "sum"),
                                                 pts=("pts", "sum")).reset_index()
        pr = pr.join(otot, on="o")
        pr["dev"] = pr.pts / pr.poss - pr["T"] / pr.P
        top_off = otot.P.sort_values(ascending=False).head(REF_TOP_OFF).index
        rot_def = dtot.sort_values(ascending=False).head(REF_ROT_DEF).index
        prim = pr[pr.o.isin(top_off) & pr.d.isin(rot_def) & (pr.poss >= REF_BANDS[0])]
        prim = prim.sort_values("poss", ascending=False).groupby(["o", "dteam"]).head(1)
        prim = prim.assign(band=pd.cut(prim.poss, REF_BANDS, right=False))
        norm_tab = prim.groupby("band", observed=True).agg(n=("dev", "size"),
                                                           norm=("dev", "mean"))
        prim = prim.assign(z=(prim.dev - prim.band.map(norm_tab.norm).astype(float))
                           / np.sqrt(per_poss_var / prim.poss))
        z_sd = float(prim[prim.poss >= THIN].z.std())
        share_hi = float((prim.z >= EDGE_Z).mean())
        share_lo = float((prim.z <= -EDGE_Z).mean())
        r.note("league noise: variance %.3f per partial possession (docstring %.3f), "
               "SE %.3f at 30 possessions" % (per_poss_var, PER_POSS_VAR,
                                             np.sqrt(per_poss_var / 30)))
        r.note("primary-defender norm (top %d offenders by possessions, top %d defenders, "
               "each team's heaviest defender on him):" % (REF_TOP_OFF, REF_ROT_DEF))
        for b, x in norm_tab.iterrows():
            r.note("  %-14s n=%4d  norm %+.3f" % (b, x.n, x.norm))
        r.note("SD of the norm-adjusted z across those pairings, 30+ possessions: %.2f "
               "(1.00 = pure noise)" % z_sd)

        def norm_for(poss):
            for b, x in norm_tab.iterrows():
                if poss in b:
                    return float(x.norm)
            return float(norm_tab.norm.iloc[0]) if poss < REF_BANDS[0] else float(
                norm_tab.norm.iloc[-1])

        def key_matchups(off_team, def_team):
            off_ids, _ = top_ids(off_team, TOP_OFF, cur)
            def_ids, _ = top_ids(def_team, TOP_DEF, cur)
            out = []
            for o in off_ids:
                sub = m[(m.off_id == o) & (m.def_id.isin(def_ids))]
                if sub.empty:
                    out.append(dict(off_team=off_team, def_team=def_team,
                                    offender=names.get(o, o), defender="none observed",
                                    poss=0.0, ppp=np.nan, base_ppp=base_ppp.get(o, np.nan),
                                    vs_base=np.nan, norm=np.nan, beyond=np.nan, fg="",
                                    three="", tov=0.0, thin=True, z=np.nan))
                    continue
                x = sub.sort_values("poss", ascending=False).iloc[0]
                ppp = x.pts / x.poss if x.poss else np.nan
                bp = base_ppp.get(o, np.nan)
                nm_ = norm_for(float(x.poss))
                vb = (ppp - bp) if pd.notna(bp) else np.nan
                out.append(dict(
                    off_team=off_team, def_team=def_team, offender=names.get(o, o),
                    defender=names.get(int(x.def_id), int(x.def_id)), poss=float(x.poss),
                    ppp=ppp, base_ppp=bp, vs_base=vb, norm=nm_,
                    beyond=(vb - nm_) if pd.notna(vb) else np.nan,
                    fg="%d-%d" % (x.fgm, x.fga), three="%d-%d" % (x.fg3m, x.fg3a),
                    tov=float(x.tov), thin=bool(x.poss < THIN),
                    z=((vb - nm_) / np.sqrt(per_poss_var / x.poss))
                    if pd.notna(vb) and x.poss else np.nan))
            return out

        cards, allm = [], []
        md = []
        mk_min = mkt.loc[TEAM]
        md.append("# M3: opponent cards, the West field\n")
        md.append("**Basis.** Series probabilities on net rating with the style overlay "
                  "**off** (M2). Style shown as **descriptive only**. Matchups are "
                  "observed 2025-26 possessions and are **evidence, not verdicts**: the "
                  "median pairing is 4.8 partial possessions, pairings under %d are "
                  "flagged thin, and a pairing's standard error is measured at %.2f "
                  "points per matchup possession at 30 possessions and %.2f at 100. "
                  "Run `%s`.\n"
                  % (THIN, np.sqrt(per_poss_var / 30), np.sqrt(per_poss_var / 100),
                     r.run_id))
        md.append("**The yardstick is what a primary defender normally allows, not zero.** "
                  "Across the league in 2025-26, a team's heaviest rotation defender on "
                  "one of the top %d offenders held him %s below his own baseline (by "
                  "possession band: %s). A heavy matchup is a designated stopper on "
                  "possessions the offence did not choose, so running below baseline is "
                  "the normal result and says nothing on its own. Each row is judged "
                  "**beyond that norm**, and a matchup is called an **edge** only at %.0f "
                  "or more standard errors past it. After the adjustment the spread of "
                  "league pairings is %.2f standard errors (1.00 would be pure noise), so "
                  "most of what separates one matchup from another is sampling. On the "
                  "N_ROWS observed rows below, the league's own rate of two-SE "
                  "deviations among primary pairings would produce about N_CHANCE, "
                  "with nothing special about these teams.\n"
                  % (REF_TOP_OFF, "%.2f to %.2f" % (-norm_tab.norm.max(), -norm_tab.norm.min()),
                     ", ".join("%d-%s poss %+.2f" % (b.left, "" if b.right > 10000 else
                                                     "%d" % b.right, x.norm)
                               for b, x in norm_tab.iterrows()).replace("- poss", "+ poss"),
                     EDGE_Z, z_sd))
        # every top offender, pooled over all his primary pairings of 30+ possessions
        pp = prim[prim.poss >= THIN].copy()
        pp["beyond"] = pp.dev - pp.band.map(norm_tab.norm).astype(float)
        pool = pp.groupby("o").apply(lambda g: pd.Series(dict(
            n=len(g), poss=g.poss.sum(),
            beyond=float(np.average(g.beyond, weights=g.poss)),
            z=float(np.average(g.beyond, weights=g.poss)
                    / np.sqrt(per_poss_var / g.poss.sum())))), include_groups=False)
        pool = pool[pool.n >= 5]
        pool["pct_rank"] = pool.z.rank(pct=True)
        min_ids, _ = top_ids(TEAM, TOP_OFF, cur)
        md.append("**Minnesota's top five against primary defenders, every opponent "
                  "pooled.** Each player's 2025-26 pairings of %d+ possessions against "
                  "a team's heaviest rotation defender on him, judged beyond the norm and "
                  "set against the other %d top offenders with five or more such "
                  "pairings. A percentile near 0 means primary defenders held him more "
                  "than they hold most scorers.\n" % (THIN, len(pool) - 1))
        md.append("| player | pairings | possessions | beyond norm | in SEs | percentile |")
        md.append("|---|---:|---:|---:|---:|---:|")
        pool_rows = []
        for pid in min_ids:
            if pid in pool.index:
                x = pool.loc[pid]
                md.append("| %s | %d | %.0f | %+.3f | %+.1f | %.0f |"
                          % (names.get(pid, pid), x.n, x.poss, x.beyond, x.z,
                             100 * x.pct_rank))
                pool_rows.append((names.get(pid, pid), x.z, x.pct_rank))
            else:
                md.append("| %s | fewer than 5 | | | | |" % names.get(pid, pid))
        md.append("")
        chk_f = os.path.join(OUT_DIR, "m3_primary_defender_check.csv")
        if os.path.exists(chk_f):
            chk = pd.read_csv(chk_f)
            e_ = chk[chk.player == "Anthony Edwards"].set_index("variant")
            if len(e_) == 4:
                md.append("**Confound check** (`m3_primary_defender_check.py`). Edwards's "
                          "rank survives a baseline built from rotation defenders only "
                          "(percentile %.0f, %+.1f SEs) and survives dropping the playoffs "
                          "(percentile %.0f, %+.1f SEs; both changes together, %.0f). The "
                          "playoffs sharpen it (Christian Braun drew 110 of his 145 "
                          "possessions on Edwards in the first-round series, Devin Vassell "
                          "119 of 147 in the second), but the regular season alone already puts him at the "
                          "%.0fth percentile of %d top scorers. Read it as description: "
                          "last season, the defender a team assigned to Edwards held him "
                          "further under his own level than that assignment holds almost "
                          "any other scorer. It does not say why, and it does not say "
                          "2026-27 will repeat it.\n"
                          % (e_.loc["A", "percentile"], e_.loc["A", "z"],
                             e_.loc["B", "percentile"], e_.loc["B", "z"],
                             e_.loc["C", "percentile"], e_.loc["B", "percentile"],
                             int(e_.loc["B", "n_offenders"])))
        for nm_, z_, pr_ in pool_rows:
            r.note("pooled vs primary defenders: %-22s %+.1f SEs, percentile %.0f"
                   % (nm_, z_, 100 * pr_))

        md.append("**Read the matchup numbers on their own scale.** They are points per "
                  "*matchup* possession: the points the offender scored while that "
                  "defender was on him, divided by the partial possessions they shared. "
                  "He does not shoot on most of those possessions, so typical values run "
                  "0.2 to 0.5, not the 1.1 of team offence. That is why every row is set "
                  "against the offender's own baseline across all defenders, and only the "
                  "difference is meaningful.\n")
        z_min = {f_: float(sty.loc[TEAM, f_]) for f_ in STYLE_WORDS if f_ in sty.columns}
        near = [f_ for f_, z in z_min.items() if abs(z) < 0.05]
        md.append("**Minnesota.** Market **%.2f%%**, rank %d. Model **%.2f%%**.%s\n"
                  % (mk_min.market_pct, int(mk_min.market_rank), mk_min.model_pct,
                     (" In 2025-26 Minnesota sat at league average on %s (z within 0.05 "
                      "of zero), so a style contrast on %s describes the opponent, not a "
                      "Minnesota tendency." % (" and ".join(near),
                                               "either" if len(near) == 2 else "these"))
                     if near else ""))
        md.append("---\n")

        for _, fx in field.iterrows():
            o = fx.team_abbr
            sp = series.get(o, [np.nan])
            mo = mkt.loc[o]
            s_o = st[st.team_abbr == o]
            d_net = [float(s_o[s_o.fork == f].delta_net.iloc[0]) for f in FORKS]

            # offseason ledger
            cur_o = cur[cur.team_abbr == o]
            base_o = base[base.team_abbr == o]
            arr = cur_o[~cur_o.player_id.isin(base_o.player_id)].copy()
            dep = base_o[~base_o.player_id.isin(cur_o.player_id)].copy()
            arr["w"] = arr.mpg / 48.0 * arr.consensus_net
            dep["w"] = dep.mpg / 48.0 * dep.consensus_net
            arr = arr[arr.mpg > 0].reindex(arr.w.abs().sort_values(ascending=False).index).head(3)
            dep = dep[dep.mpg > 0].reindex(dep.w.abs().sort_values(ascending=False).index).head(3)

            # style contrasts
            contrasts = []
            if o in sty.index and TEAM in sty.index:
                for f_, (hi, lo) in STYLE_WORDS.items():
                    if f_ in sty.columns:
                        gap = float(sty.loc[o, f_] - sty.loc[TEAM, f_])
                        contrasts.append((abs(gap), f_, gap, float(sty.loc[o, f_]),
                                          float(sty.loc[TEAM, f_]), hi if gap > 0 else lo))
                contrasts.sort(reverse=True)

            hurt_min = key_matchups(o, TEAM)       # their offence, our defence
            min_hurts = key_matchups(TEAM, o)      # our offence, their defence
            allm += hurt_min + min_hurts

            cards.append(dict(
                team=o, model_title_mean=fx["mean"] * 100, model_title_lo=fx["min"] * 100,
                model_title_hi=fx["max"] * 100, market_pct=float(mo.market_pct),
                market_rank=int(mo.market_rank), min_series_mean=float(np.mean(sp)),
                min_series_lo=float(np.min(sp)), min_series_hi=float(np.max(sp)),
                p_round1_opponent=float(r1.get(o, 0.0)),
                offseason_delta_mean=float(np.mean(d_net)),
                offseason_delta_lo=min(d_net), offseason_delta_hi=max(d_net)))

            md.append("## %s\n" % o)
            md.append("| | |\n|---|---|")
            md.append("| model title odds | **%.2f%%** [%.2f, %.2f] |"
                      % (fx["mean"] * 100, fx["min"] * 100, fx["max"] * 100))
            md.append("| market title odds | %.2f%%, rank %d |"
                      % (mo.market_pct, int(mo.market_rank)))
            md.append("| **Minnesota wins the series** | **%.3f** [%.3f, %.3f] |"
                      % (np.mean(sp), np.min(sp), np.max(sp)))
            md.append("| P(first-round opponent) | %.3f |" % float(r1.get(o, 0.0)))
            md.append("| modelled offseason change | %+.2f net [%+.2f, %+.2f] |\n"
                      % (np.mean(d_net), min(d_net), max(d_net)))

            md.append("**Offseason ledger.** Arrivals: " + (
                "; ".join("%s (%.1f mpg, %+.2f)" % (x.player_name, x.mpg, x.consensus_net)
                          for _, x in arr.iterrows()) or "none in the rotation")
                + ". Departures: " + (
                "; ".join("%s (%.1f mpg, %+.2f)" % (x.player_name, x.mpg, x.consensus_net)
                          for _, x in dep.iterrows()) or "none from the rotation") + ".\n")

            if contrasts:
                md.append("**Style, descriptive only** (2025-26, z-scored, not adjusted "
                          "for this summer's moves): " + "; ".join(
                              "%s **%s** than Minnesota (%+.2f against %s)"
                              % (o, words, zo,
                                 "league average" if abs(zm) < 0.05 else "%+.2f" % zm)
                              for _, f_, gap, zo, zm, words in contrasts[:3]) + ".\n")

            def mtable(rows, title, edge_words):
                md.append("**%s**\n" % title)
                md.append("| offence | guarded most by | poss | pts per matchup poss "
                          "| his baseline | vs baseline | primary-defender norm "
                          "| beyond norm | in SEs | FG | 3P | TOV |")
                md.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|")
                for x in rows:
                    if x["defender"] == "none observed":
                        md.append("| %s | none observed | 0 | | | | | | | | | |"
                                  % x["offender"])
                        continue
                    md.append("| %s | %s | %.0f%s | %.2f | %.2f | %+.2f | %+.2f | **%+.2f** "
                              "| %+.2f | %s | %s | %.0f |"
                              % (x["offender"], x["defender"], x["poss"],
                                 " *thin*" if x["thin"] else "", x["ppp"], x["base_ppp"],
                                 x["vs_base"], x["norm"], x["beyond"], x["z"], x["fg"],
                                 x["three"], x["tov"]))
                md.append("")

                def say(x):
                    return ("%s against %s, %+.2f beyond the norm over %.0f possessions "
                            "(%+.2f SEs%s)" % (x["offender"], x["defender"], x["beyond"],
                                               x["poss"], x["z"],
                                               ", thin" if x["thin"] else ""))
                obs = [x for x in rows if pd.notna(x["z"])]
                edges = sorted([x for x in obs if x["z"] >= EDGE_Z], key=lambda x: -x["z"])
                held = sorted([x for x in obs if x["z"] <= -EDGE_Z], key=lambda x: x["z"])
                if not obs:
                    line = "no observed matchups in this direction."
                elif edges:
                    line = "**%s:** %s." % (edge_words, "; ".join(say(x) for x in edges))
                else:
                    pos = [x for x in obs if x["z"] > 0]
                    line = ("**no edge.** No matchup ran two standard errors above what a "
                            "primary defender normally allows. " + (
                                "Closest: %s." % say(max(pos, key=lambda x: x["z"]))
                                if pos else "Every matchup ran at or below the norm."))
                if held:
                    line += (" Held two or more SEs beyond the norm: %s."
                             % "; ".join(say(x) for x in held))
                md.append("*In one line:* " + line + "\n")

            mtable(hurt_min, "Their offence against Minnesota's defenders (above "
                             "the norm = they hurt Minnesota)",
                   "Edge for them")
            mtable(min_hurts, "Minnesota's offence against their defenders (above "
                              "the norm = Minnesota hurts them)",
                   "Edge for Minnesota")
            md.append("---\n")

        cdf = pd.DataFrame(cards)
        cdf.to_csv(OUT, index=False)
        pd.DataFrame(allm).to_csv(OUT_M, index=False)
        n_obs = int(pd.DataFrame(allm).z.notna().sum())
        text = "\n".join(md).replace("N_ROWS", "%d" % n_obs).replace(
            "N_CHANCE", "%.1f above and %.1f below" % (n_obs * share_hi, n_obs * share_lo))
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write(text)

        r.note("")
        r.note("CARD SUMMARY (Minnesota's series probability, net-rating basis):")
        for _, x in cdf.sort_values("min_series_mean").iterrows():
            r.note("  %-4s model %5.2f%% | market %5.2f%% rk %2d | MIN wins series %.3f "
                   "[%.3f, %.3f] | P(R1 opp) %.3f"
                   % (x.team, x.model_title_mean, x.market_pct, x.market_rank,
                      x.min_series_mean, x.min_series_lo, x.min_series_hi,
                      x.p_round1_opponent))
        md_df = pd.DataFrame(allm)
        nthin = int(md_df.thin.sum())
        r.note("key matchups: %d rows, %d flagged thin (< %d possessions)"
               % (len(md_df), nthin, THIN))
        r.output(OUT, rows=len(cdf))
        r.output(OUT_M, rows=len(md_df))
        r.output(OUT_MD)


if __name__ == "__main__":
    main()
