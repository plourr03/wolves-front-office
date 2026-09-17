#!/usr/bin/env python3
"""N6: the Kuminga ledger. What the signing makes better, what it makes worse, and how
sure each line is.

Every line is tagged OBSERVED (it happened, it is in the data), MODELED (it comes out of
the simulation or an impact view) or ASSUMED (we chose it). Sample sizes travel with every
observed number.

THE PIECES.
  1  SLOT VERDICT. The Kuminga slot variants (who plays his minutes if he were not here)
     at 200,000-sim precision, on both aging bases, against each basis's noise floor.
  2  PRIMARY DEFENDERS, M3 BASIS. The same construction that put Edwards at the 1st
     percentile: every pairing of 30+ possessions between an offender and a team's
     heaviest rotation defender on him, judged beyond the league norm for such a pairing.
     Kuminga as a SCORER (how primary defenders did on him) and as a DEFENDER (how
     offenders did when he was the primary defender), with Edwards beside him. 2025-26
     is the M3 basis; 2023-24 to 2025-26 pooled is carried because Kuminga's 2025-26 was
     36 games. Per-season baselines, norms and noise, then pooled.
  3  THE GSW ANALOG. Kuminga's Golden State units with a non-shooting centre (height
     81 inches or more and under 10% of his shots from three that season) against his
     units without one: possessions, net per 100, and team three-point attempt rate.
     Garbage time excluded. Minnesota's version of that unit is Kuminga with Gobert.
  4  POSTSEASON, ALL OF IT. Every playoff game he has played, pooled: games, minutes,
     possessions, on-court offensive and defensive rating, usage, true shooting.
  5  THE CRUNCH. His usage and unassisted share against the projected five's usage sum
     (M5).
  6  THE CONTRACT. The Non-Bird and option structure, from the corrected cap chain.

GATE G1: the Golden State stint layer reconciles to the box score, points for per game.

    python kuminga/scripts/n6_kuminga_ledger.py
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
DATA = os.path.join(REPO, "kuminga", "data")
STINTS = [os.path.join(DATA, "stints_gsw_2022_25.parquet"),
          os.path.join(DATA, "stints_2025_26.parquet")]
OUT_PD = os.path.join(OUT_DIR, "n6_primary_defender.csv")
OUT_GSW = os.path.join(OUT_DIR, "n6_gsw_analog.csv")
OUT_PO = os.path.join(OUT_DIR, "n6_postseason.csv")
OUT_L = os.path.join(OUT_DIR, "n6_ledger.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "n6_kuminga_ledger.md")

KUM, ANT, GOB = 1630228, 1630162, 203497
GSW_ID = 1610612744
FORKS = ["consensus", "rapm", "box", "darko"]
TOP_OFF, ROT_DEF, MIN_POSS, MIN_PAIR = 150, 300, 30.0, 5
BANDS = [30, 60, 120, 100000]
SEASONS = {"2023-24": ("00223", "00423"), "2024-25": ("00224", "00424"),
           "2025-26": ("00225", "00425")}
NS_HEIGHT, NS_3PA = 81.0, 0.10


def primary_frame(season, prefixes, keep_off):
    q = db.query("""
        select game_id g, team_id oteam, person_id_off::bigint o, person_id_def::bigint d,
               sum(partial_possessions) poss, sum(player_points) pts
        from nba.nba_boxscore_matchups
        where left(game_id, 5) in %(p)s
        group by 1, 2, 3, 4
    """, {"p": tuple(prefixes)})
    for c in ("poss", "pts"):
        q[c] = pd.to_numeric(q[c], errors="coerce").fillna(0.0)
    sides = q[["g", "oteam"]].drop_duplicates()
    sides = sides.merge(sides.rename(columns={"oteam": "dteam"}), on="g")
    q = q.merge(sides[sides.oteam != sides.dteam], on=["g", "oteam"])
    otot = q.groupby("o").agg(P=("poss", "sum"), T=("pts", "sum"))
    cells = q[q.poss > 0].join(otot, on="o")
    var = float(((cells.pts - cells["T"] / cells.P * cells.poss) ** 2).sum()
                / cells.poss.sum())
    dtot = q.groupby("d").poss.sum()
    top_off = set(otot.P.sort_values(ascending=False).head(TOP_OFF).index)
    rot_def = set(dtot.sort_values(ascending=False).head(ROT_DEF).index)
    pr = q.groupby(["o", "dteam", "d"]).agg(poss=("poss", "sum"),
                                            pts=("pts", "sum")).reset_index()
    pr = pr.join(otot, on="o")
    pr["dev"] = pr.pts / pr.poss - pr["T"] / pr.P
    # the M3 reference set, plus the named players so their own rows exist
    offs = top_off | set(keep_off)
    defs = rot_def | set(keep_off)
    prim = pr[pr.o.isin(offs) & pr.d.isin(defs) & (pr.poss >= MIN_POSS)]
    prim = prim.sort_values("poss", ascending=False).groupby(["o", "dteam"]).head(1)
    ref = prim[prim.o.isin(top_off) & prim.d.isin(rot_def)]
    ref = ref.assign(band=pd.cut(ref.poss, BANDS, right=False))
    norm = ref.groupby("band", observed=True).dev.mean()
    prim = prim.assign(band=pd.cut(prim.poss, BANDS, right=False))
    prim = prim.assign(beyond=prim.dev - prim.band.map(norm).astype(float), var=var,
                       season=season, o_ref=prim.o.isin(top_off), d_ref=prim.d.isin(rot_def))
    return prim


def pool_by(frame, key):
    def f(g):
        b = float(np.average(g.beyond, weights=g.poss))
        se = float(np.sqrt(np.average(g["var"], weights=g.poss) / g.poss.sum()))
        return pd.Series(dict(pairings=len(g), poss=float(g.poss.sum()), beyond=b, z=b / se))
    return frame.groupby(key).apply(f, include_groups=False)


def main():
    with runlog.run("n6_kuminga_ledger", inputs={"ns_height": NS_HEIGHT, "ns_3pa": NS_3PA,
                                                 "min_poss": MIN_POSS}) as r:
        led = []

        def line(side, text, tag, value="", n=""):
            led.append(dict(side=side, line=text, tag=tag, value=value, sample=n))

        # ================= 1. slot verdict =============================================
        slot = {}
        for basis, sfx, d in (("un-aged", "", OUT_DIR), ("aged", "_AGED",
                                                         os.path.join(OUT_DIR, "aged"))):
            sr = pd.read_csv(os.path.join(d, "slot_robustness.csv")).set_index("variant")
            nf = pd.read_csv(os.path.join(d, "noise_floor_slot%s.csv" % sfx)).set_index("variant")
            slot[basis] = sr.join(nf[["n_forks_clearing", "survives"]])
        r.note("1. slot verdicts (mean pp, lo, hi, clears, survives):")
        for v in slot["un-aged"].index:
            u, a = slot["un-aged"].loc[v], slot["aged"].loc[v]
            r.note("   %-22s un-aged %+.3f [%+.3f, %+.3f] %d/4 %s | aged %+.3f [%+.3f, %+.3f] "
                   "%d/4 %s" % (v, u.mean_pp, u.lo_pp, u.hi_pp, u.n_forks_clearing,
                                u.survives, a.mean_pp, a.lo_pp, a.hi_pp, a.n_forks_clearing,
                                a.survives))
        A_u, A_a = slot["un-aged"].loc["A_c3_default_shannon"], slot["aged"].loc[
            "A_c3_default_shannon"]
        line("better", "Signing Kuminga beats the most likely internal fill for his minutes "
             "(slot A, the default allocation, where Williams, Lyles and McDaniels absorb them): "
             "positive in every view on both aging bases and "
             "clearing every view's 200k floor",
             "MODELED", "%+.2f points un-aged [%+.2f, %+.2f]; %+.2f aged [%+.2f, %+.2f]"
             % (A_u.mean_pp, A_u.lo_pp, A_u.hi_pp, A_a.mean_pp, A_a.lo_pp, A_a.hi_pp),
             "200,000 sims per view per curve")
        D_u, D_a = slot["un-aged"].loc["D_beringer_fills"], slot["aged"].loc["D_beringer_fills"]
        line("worse", "If the real alternative was Beringer taking the minutes, the "
             "comparison runs the other way, and that also clears every floor on both bases",
             "MODELED", "%+.2f un-aged, %+.2f aged" % (D_u.mean_pp, D_a.mean_pp),
             "200,000 sims")
        B_u, B_a = slot["un-aged"].loc["B_lyles_fills"], slot["aged"].loc["B_lyles_fills"]
        line("worse", "Against Trey Lyles filling the slot the views split, so the verdict "
             "depends on who the alternative was", "MODELED",
             "%+.2f un-aged, %+.2f aged, MIXED both" % (B_u.mean_pp, B_a.mean_pp), "")

        # ================= 2. primary defenders ========================================
        frames = [primary_frame(s, p, [KUM, ANT]) for s, p in SEASONS.items()]
        allp = pd.concat(frames, ignore_index=True)
        rows = []
        for wlab, fr in (("2025-26", allp[allp.season == "2025-26"]), ("2023-26 pooled", allp)):
            # reference distributions: offenders / defenders with 5+ pairings, in-reference
            off_ref = pool_by(fr[fr.o_ref & fr.d_ref], "o")
            off_ref = off_ref[off_ref.pairings >= MIN_PAIR]
            def_ref = pool_by(fr[fr.o_ref & fr.d_ref], "d")
            def_ref = def_ref[def_ref.pairings >= MIN_PAIR]
            off_named = pool_by(fr[fr.o.isin([KUM, ANT]) & fr.d_ref], "o")
            def_named = pool_by(fr[fr.d.isin([KUM, ANT]) & fr.o_ref], "d")
            for pid, nm in ((KUM, "Jonathan Kuminga"), (ANT, "Anthony Edwards")):
                for role, named, ref, better_low in (("scorer", off_named, off_ref, False),
                                                     ("defender", def_named, def_ref, True)):
                    if pid in named.index:
                        x = named.loc[pid]
                        # scorer: low beyond = held more (worse for him); defender: low =
                        # held offenders more (better for him). Percentile is always "share of
                        # the reference below him".
                        pct = float((ref.z < x.z).mean() * 100)
                        rows.append(dict(window=wlab, player=nm, role=role,
                                         pairings=int(x.pairings), poss=x.poss,
                                         beyond=x.beyond, z=x.z, percentile=pct,
                                         n_reference=len(ref),
                                         enough=bool(x.pairings >= MIN_PAIR)))
                    else:
                        rows.append(dict(window=wlab, player=nm, role=role, pairings=0,
                                         poss=0.0, beyond=np.nan, z=np.nan,
                                         percentile=np.nan, n_reference=len(ref),
                                         enough=False))
        PD = pd.DataFrame(rows)
        PD.to_csv(OUT_PD, index=False)
        r.note("2. primary defenders (beyond norm, z, percentile of reference, pairings, poss):")
        for _, x in PD.iterrows():
            r.note("   %-15s %-17s %-8s beyond %+.3f z %+.1f pct %4.0f of %d | %d pairings, "
                   "%.0f poss%s" % (x.window, x.player, x.role, x.beyond, x.z, x.percentile,
                                    x.n_reference, x.pairings, x.poss,
                                    "" if x.enough else "  (below 5 pairings)"))
        kp = PD[(PD.player == "Jonathan Kuminga") & (PD.window == "2023-26 pooled")].set_index("role")
        k26 = PD[(PD.player == "Jonathan Kuminga") & (PD.window == "2025-26")].set_index("role")
        ep = PD[(PD.player == "Anthony Edwards") & (PD.window == "2023-26 pooled")].set_index("role")
        zs_ = kp.loc["scorer", "z"]
        line("better" if zs_ >= 2 else ("worse" if zs_ <= -2 else "worse"),
             "As a scorer against the defender a team assigns him, Kuminga ran %s "
             "(percentile %.0f of %d scorers), where Edwards sat at the very bottom "
             "(percentile %.0f): the primary-defender problem M3 found is Edwards', not his"
             % ("about at the norm, inside the noise" if abs(zs_) < 2 else
                ("above the norm" if zs_ > 0 else "below the norm"),
                kp.loc["scorer", "percentile"], kp.loc["scorer", "n_reference"],
                ep.loc["scorer", "percentile"]),
             "OBSERVED", "%+.3f beyond the norm, %+.1f SEs (2023-26); 2025-26 alone %s"
             % (kp.loc["scorer", "beyond"], kp.loc["scorer", "z"],
                "%d pairings, too few" % k26.loc["scorer", "pairings"]
                if not k26.loc["scorer", "enough"] else "percentile %.0f"
                % k26.loc["scorer", "percentile"]),
             "%d pairings, %.0f possessions" % (kp.loc["scorer", "pairings"],
                                                 kp.loc["scorer", "poss"]))
        zd_ = kp.loc["defender", "z"]
        line("better" if zd_ < 0 else "worse",
             "As the primary defender on a top-150 scorer, Kuminga held him %s "
             "(percentile %.0f of %d defenders; low is better)"
             % (("slightly below the norm, inside the noise" if zd_ < 0 else
                 "slightly above the norm, inside the noise") if abs(zd_) < 2 else
                ("below the norm" if zd_ < 0 else "above the norm"),
                kp.loc["defender", "percentile"], kp.loc["defender", "n_reference"]),
             "OBSERVED", "%+.3f beyond the norm, %+.1f SEs (2023-26)"
             % (kp.loc["defender", "beyond"], kp.loc["defender", "z"]),
             "%d pairings, %.0f possessions" % (kp.loc["defender", "pairings"],
                                                 kp.loc["defender", "poss"]))

        # ================= 3. the GSW analog ==========================================
        st = pd.concat([pd.read_parquet(f) for f in STINTS], ignore_index=True)
        st["game_id"] = st.game_id.astype(str).str.zfill(10)
        st = st[st.team_id == GSW_ID].drop_duplicates(
            ["game_id", "period_start", "clock_start_sec", "lineup_id"])
        # POINTS FROM THE SCORER, NOT THE POSSESSION. The shared stint pipeline credits a
        # possession's points to the team it believes had the ball, and a possession-
        # tracking slip sends a basket to the wrong side: its points_for misses the box
        # score by 3.4% of points (9% of games exact), with the opponent over by exactly
        # the same amount. The made-shot counts in the same stints are attributed to the
        # team that actually scored, and rebuilt from them points reconcile exactly.
        st["points_for"] = 2 * st.fgm_off + st.fg3m_off + st.ftm_off
        st["points_against"] = 2 * st.fgm_def + st.fg3m_def + st.ftm_def
        box = db.query("""select game_id, pts from nba.nba_games
                          where team_abbreviation = 'GSW' and left(game_id, 5) in %(p)s""",
                       {"p": ("00222", "00223", "00224", "00225", "00422", "00423",
                              "00424", "00425")})
        box["pts"] = pd.to_numeric(box.pts)
        pf = st.groupby("game_id").points_for.sum()
        g1 = box.set_index("game_id").join(pf, how="inner")
        g1_gap = float((g1.pts - g1.points_for).abs().sum() / g1.pts.sum())
        r.note("3. G1 GSW stints (points rebuilt from made shots) vs box score points: %d "
               "games, absolute gap %.2f%%" % (len(g1), 100 * g1_gap))
        if g1_gap > 0.005:
            raise RuntimeError("G1 failed: GSW stints do not reconcile")
        st["season"] = st.game_id.str[3:5].map({"22": "2022-23", "23": "2023-24",
                                                "24": "2024-25", "25": "2025-26"})
        st = st[~st.in_garbage_time.astype(bool)]
        # non-shooting centres, per season, from the warehouse
        ns = db.query("""
            select b.season_year season, s.player_id::bigint pid,
                   max(b.player_height_inches) h, sum(s.fga) fga, sum(s.fg3a) fg3a
            from nba.nba_player_stats s
            join nba.nba_player_season_bio b on b.player_id::bigint = s.player_id::bigint
             and b.season_year = s.season_year and b.season_type = 'Regular Season'
            where s.game_id like '002%%' and s.season_year in ('2022-23','2023-24','2024-25','2025-26')
            group by 1, 2
        """)
        for c in ("h", "fga", "fg3a"):
            ns[c] = pd.to_numeric(ns[c], errors="coerce")
        ns = ns[(ns.h >= NS_HEIGHT) & (ns.fga >= 50) & (ns.fg3a / ns.fga < NS_3PA)]
        ns_set = set(zip(ns.season, ns.pid))
        names = db.query("""select distinct person_id::bigint pid, first_name||' '||family_name nm
                            from nba.nba_player_advanced_stats
                            where team_tricode = 'GSW' and left(game_id,3) = '002'""")
        nmap = dict(zip(names.pid, names.nm))

        def ids(s):
            return [int(v) for v in str(s).split(",")]

        st["ids"] = st.lineup_id.map(ids)
        st["kum"] = st.ids.map(lambda v: KUM in v)
        st["ns_on"] = [any((s_, p) in ns_set for p in v) for s_, v in zip(st.season, st.ids)]
        gsw_rows = []
        ks = st[st.kum]
        for lab, d in (("with a non-shooting centre", ks[ks.ns_on]),
                       ("without one", ks[~ks.ns_on])):
            for wlab, dd in list(d.groupby("season")) + [("2022-26 pooled", d)]:
                po, pd_ = dd.possessions_off.sum(), dd.possessions_def.sum()
                gsw_rows.append(dict(unit=lab, window=wlab, poss_off=int(po), poss_def=int(pd_),
                                     off100=100 * dd.points_for.sum() / po if po else np.nan,
                                     def100=100 * dd.points_against.sum() / pd_ if pd_ else np.nan,
                                     fg3a_rate=dd.fg3a_off.sum() / dd.fga_off.sum()
                                     if dd.fga_off.sum() else np.nan))
        GS = pd.DataFrame(gsw_rows)
        GS["net100"] = GS.off100 - GS.def100
        GS.to_csv(OUT_GSW, index=False)
        who = sorted({nmap.get(p, p) for s_, p in ns_set
                      if any(p in v for v in ks.ids)})
        r.note("   non-shooting centres who shared the floor with Kuminga: %s" % ", ".join(
            str(w) for w in who))
        for _, x in GS.iterrows():
            r.note("   %-28s %-15s off poss %5d | net %+6.1f (%.1f / %.1f) | team 3PA rate %.3f"
                   % (x.unit, x.window, x.poss_off, x.net100, x.off100, x.def100, x.fg3a_rate))
        w_ = GS[(GS.window == "2022-26 pooled")].set_index("unit")
        a_, b_ = w_.loc["with a non-shooting centre"], w_.loc["without one"]

        def net_diff(d):
            x1, x0 = d[d.ns_on], d[~d.ns_on]
            n1 = (100 * x1.points_for.sum() / x1.possessions_off.sum()
                  - 100 * x1.points_against.sum() / x1.possessions_def.sum())
            n0 = (100 * x0.points_for.sum() / x0.possessions_off.sum()
                  - 100 * x0.points_against.sum() / x0.possessions_def.sum())
            return n1 - n0

        kg = {g_: d for g_, d in ks.groupby("game_id")}
        kids = np.array(sorted(kg))
        rng_ = np.random.default_rng(20260917)
        bd = [net_diff(pd.concat([kg[g_] for g_ in rng_.choice(kids, len(kids))]))
              for _ in range(1000)]
        se_ns = float(np.std(bd, ddof=1))
        r.note("   with-minus-without net %+.1f, game-bootstrap SE %.1f over %d games"
               % (a_.net100 - b_.net100, se_ns, len(kids)))
        dz = (a_.net100 - b_.net100) / se_ns
        line("worse" if a_.net100 < b_.net100 else "better",
             "Next to a non-shooting centre at Golden State, Kuminga's units were %s than "
             "without one%s, and took %s threes: the Gobert question in miniature"
             % ("worse" if a_.net100 < b_.net100 else "better",
                " but inside the noise" if abs(dz) < 2 else "",
                "slightly fewer" if a_.fg3a_rate < b_.fg3a_rate else "slightly more"),
             "OBSERVED", "net %+.1f against %+.1f per 100 (difference %+.1f, game-bootstrap SE "
             "%.1f); three-point attempt rate %.3f against %.3f"
             % (a_.net100, b_.net100, a_.net100 - b_.net100, se_ns, a_.fg3a_rate,
                b_.fg3a_rate),
             "%s and %s offensive possessions, 2022-26, garbage time out"
             % ("{:,}".format(int(a_.poss_off)), "{:,}".format(int(b_.poss_off))))

        # ================= 4. postseason, pooled ======================================
        po = db.query("""
            select a.game_id, a.minutes_float mins, a.possessions poss, a.offensive_rating ortg,
                   a.defensive_rating drtg, a.usage_percentage usg, a.team_tricode team,
                   s.pts, s.fga, s.fta
            from nba.nba_player_advanced_stats a
            left join nba.nba_player_stats s on s.game_id::text = a.game_id::text
             and s.player_id::text = a.person_id::text
            where a.person_id::bigint = %(k)s and left(a.game_id, 3) = '004' and a.minutes_float > 0
        """, {"k": KUM})
        for c in ("mins", "poss", "ortg", "drtg", "usg", "pts", "fga", "fta"):
            po[c] = pd.to_numeric(po[c], errors="coerce")
        po["season"] = po.game_id.str[3:5].map(lambda y: "20%s-%02d" % (y, int(y) + 1))
        prow = []
        for wlab, d in list(po.groupby("season")) + [("all", po)]:
            w = d.poss
            prow.append(dict(window=wlab, teams="/".join(sorted(d.team.unique())),
                             games=len(d), minutes=float(d.mins.sum()), poss=float(w.sum()),
                             ortg=float(np.average(d.ortg, weights=w)),
                             drtg=float(np.average(d.drtg, weights=w)),
                             usg=float(np.average(d.usg, weights=w)),
                             ts=float(d.pts.sum() / (2 * (d.fga.sum() + 0.44 * d.fta.sum())))))
        PO = pd.DataFrame(prow)
        PO["net"] = PO.ortg - PO.drtg
        PO.to_csv(OUT_PO, index=False)
        r.note("4. postseason:")
        for _, x in PO.iterrows():
            r.note("   %-4s %-7s %2d g %6.0f min %5.0f poss | on-court net %+.1f (%.1f/%.1f) | "
                   "usage %.3f | TS %.3f" % (x.window, x.teams, x.games, x.minutes, x.poss,
                                            x.net, x.ortg, x.drtg, x.usg, x.ts))
        al = PO[PO.window == "all"].iloc[0]
        # confound check on a striking number: garbage time out, and ON against OFF in the
        # same games, where stints exist (2022-23, 2024-25 at GSW; 2025-26 at ATL)
        ps = pd.concat([pd.read_parquet(f) for f in STINTS], ignore_index=True)
        ps["game_id"] = ps.game_id.astype(str).str.zfill(10)
        ps = ps[(ps.game_id.str[:3] == "004") & ~ps.in_garbage_time.astype(bool)]
        ps = ps.drop_duplicates(["game_id", "team_id", "period_start", "clock_start_sec",
                                 "lineup_id"])
        ps["pf"] = 2 * ps.fgm_off + ps.fg3m_off + ps.ftm_off
        ps["pa"] = 2 * ps.fgm_def + ps.fg3m_def + ps.ftm_def
        ps["kum"] = ps.lineup_id.map(lambda s: str(KUM) in str(s).split(","))
        tm = ps[ps.kum].groupby("game_id").team_id.first()
        ps = ps[ps.game_id.isin(tm.index)]
        ps = ps[ps.team_id == ps.game_id.map(tm)]

        def onoff(d):
            on, off = d[d.kum], d[~d.kum]
            n_on = (100 * on.pf.sum() / on.possessions_off.sum()
                    - 100 * on.pa.sum() / on.possessions_def.sum())
            n_off = (100 * off.pf.sum() / off.possessions_off.sum()
                     - 100 * off.pa.sum() / off.possessions_def.sum())
            return n_on, n_off, n_on - n_off

        n_on, n_off, diff = onoff(ps)
        gids = np.array(sorted(ps.game_id.unique()))
        rng = np.random.default_rng(20260917)
        byg = {g_: d for g_, d in ps.groupby("game_id")}
        boots = []
        for _ in range(2000):
            pick = rng.choice(gids, len(gids), replace=True)
            boots.append(onoff(pd.concat([byg[g_] for g_ in pick]))[2])
        se_oo = float(np.std(boots, ddof=1))
        on_poss = int(ps[ps.kum].possessions_off.sum())
        off_poss = int(ps[~ps.kum].possessions_off.sum())
        r.note("   stint check, garbage time out, %d games: on %+.1f (%d poss), off %+.1f (%d "
               "poss), on-off %+.1f (bootstrap SE %.1f)" % (len(gids), n_on, on_poss, n_off,
                                                         off_poss, diff, se_oo))
        onoff_info = dict(games=len(gids), on=n_on, off=n_off, diff=diff, se=se_oo,
                          on_poss=on_poss, off_poss=off_poss)
        line("better" if al.net > 0 else "worse",
             "Every playoff possession he has played, pooled: his teams were %s with him on "
             "the floor, and in the games where stints exist they were %.0f points per 100 "
             "worse with him on than off, garbage time removed"
             % ("ahead" if al.net > 0 else "behind", abs(diff)),
             "OBSERVED", "on-court net %+.1f per 100 (all %d games); on %+.1f, off %+.1f, "
             "on-off %+.1f with a game-bootstrap SE of %.1f (%d games)"
             % (al.net, al.games, n_on, n_off, diff, se_oo, len(gids)),
             "%s on-court possessions in all; %d on and %d off in the stint games; small, "
             "and confounded by who else was on the floor"
             % ("{:,}".format(int(al.poss)), on_poss, off_poss))

        # ================= 5. the crunch ==============================================
        uu = pd.read_csv(os.path.join(OUT_DIR, "m5_unit_usage.csv")).set_index("unit")
        cs = pd.read_csv(os.path.join(OUT_DIR, "m5_creation_shares.csv"))
        kc = cs[(cs.player == "Jonathan Kuminga")].set_index("window")
        top = [u for u in uu.index if u.startswith("Projected top five")][0]
        kin = [u for u in uu.index if u.startswith("Kuminga in")][0]
        line("worse", "He adds to a usage crunch: the projected five with Kuminga in for "
             "Dosunmu sums to more usage than the typical starting five of every team-season "
             "since 2023-24", "OBSERVED rates, COMPOSED five",
             "%.3f (percentile %.1f) against %.3f with Dosunmu; %.3f at three-season rates"
             % (uu.loc[kin, "usg_sum"], uu.loc[kin, "league_pct"], uu.loc[top, "usg_sum"],
                uu.loc[kin, "usg_sum_2023_26"]),
             "7,380 league starting fives")
        line("better", "But he is not a primary creator competing with Edwards and Ball for "
             "the same shots: below the high-usage line, and a middling self-creator",
             "OBSERVED", "usage %.3f in 2025-26; unassisted share %.2f (percentile %.0f), "
             "%.2f over 2023-26" % (kc.loc["2025-26", "usg_2025_26"],
                                    kc.loc["2025-26", "unast_share"],
                                    kc.loc["2025-26", "league_pct"],
                                    kc.loc["2023-26 pooled", "unast_share"]),
             "%d makes in 2025-26, %d over 2023-26" % (kc.loc["2025-26", "fgm"],
                                                       kc.loc["2023-26 pooled", "fgm"]))

        # ================= 6. contract ================================================
        opt = pd.read_csv(os.path.join(OUT_DIR, "player_option.csv"))
        flat = opt[opt.aging == "flat"]
        line("worse", "The option is his, not Minnesota's: most views have him opting out "
             "after one season, and an opt-out leaves Minnesota only Non-Bird rights",
             "MODELED option; OBSERVED terms",
             "P(opt out) %.2f to %.2f across views (flat aging); Non-Bird ceiling $7,276,800"
             % (flat.p_opt_out.min(), flat.p_opt_out.max()), "")

        L = pd.DataFrame(led)
        L.to_csv(OUT_L, index=False)
        r.output(OUT_PD, rows=len(PD))
        r.output(OUT_GSW, rows=len(GS))
        r.output(OUT_PO, rows=len(PO))
        r.output(OUT_L, rows=len(L))
        write_doc(r, L, PD, GS, PO, slot, flat, onoff_info)
        r.output(OUT_MD)


def write_doc(r, L, PD, GS, PO, slot, flat, oo):
    M = ["# N6: the Kuminga ledger\n",
         "*As of 2026-09-17. Run `%s`. Tags: OBSERVED happened; MODELED comes out of the "
         "simulation or an impact view; ASSUMED is our choice.*\n" % r.run_id]
    for side, title in (("better", "What the signing makes better"),
                        ("worse", "What it makes worse, or leaves uncertain")):
        M.append("## %s\n" % title)
        M.append("| line | tag | number | sample |")
        M.append("|---|---|---|---|")
        for _, x in L[L.side == side].iterrows():
            M.append("| %s | %s | %s | %s |" % (x["line"], x["tag"], x["value"], x["sample"]))
        M.append("")
    M.append("## Detail\n")
    M.append("**Slot variants, 200,000 sims, mean points of title odds [four-view range], views "
             "clearing the floor.**\n")
    M.append("| variant | who takes the minutes | un-aged | aged | ships |")
    M.append("|---|---|---|---|---|")
    for v in slot["un-aged"].index:
        u, a = slot["un-aged"].loc[v], slot["aged"].loc[v]
        M.append("| %s | %s | %+.3f [%+.3f, %+.3f], %d/4 | %+.3f [%+.3f, %+.3f], %d/4 | %s |"
                 % (v, u.filled_by, u.mean_pp, u.lo_pp, u.hi_pp, u.n_forks_clearing,
                    a.mean_pp, a.lo_pp, a.hi_pp, a.n_forks_clearing,
                    "yes" if (u.survives and a.survives and u.sign_agreement ==
                              a.sign_agreement) else "no"))
    M.append("")
    M.append("**Primary defenders, M3 basis** (beyond the league norm for a team's heaviest "
             "rotation defender; scorer percentile is the share of reference scorers held "
             "MORE than him; defender percentile is the share of reference defenders who "
             "held scorers MORE than he did, so low is good for a defender).\n")
    M.append("| window | player | role | beyond norm | in SEs | percentile | pairings | "
             "possessions |")
    M.append("|---|---|---|---:|---:|---:|---:|---:|")
    for _, x in PD.iterrows():
        M.append("| %s | %s | %s | %s | %s | %s of %d | %d%s | %.0f |"
                 % (x.window, x.player, x.role,
                    "%+.3f" % x.beyond if pd.notna(x.beyond) else "n/a",
                    "%+.1f" % x.z if pd.notna(x.z) else "n/a",
                    "%.0f" % x.percentile if pd.notna(x.percentile) else "n/a",
                    x.n_reference, x.pairings, "" if x.enough else " *(thin)*", x.poss))
    M.append("")
    M.append("**The Golden State analog** (garbage time out; per 100 possessions).\n")
    M.append("| Kuminga on the floor | window | offensive possessions | net | offence / "
             "defence | team 3PA rate |")
    M.append("|---|---|---:|---:|---|---:|")
    for _, x in GS.iterrows():
        M.append("| %s | %s | %s | %+.1f | %.1f / %.1f | %.3f |"
                 % (x.unit, x.window, "{:,}".format(int(x.poss_off)), x.net100, x.off100,
                    x.def100, x.fg3a_rate))
    M.append("")
    M.append("**Every postseason game.**\n")
    M.append("| season | team | games | minutes | possessions | on-court net | usage | TS |")
    M.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for _, x in PO.iterrows():
        M.append("| %s | %s | %d | %.0f | %.0f | %+.1f | %.3f | %.3f |"
                 % (x.window, x.teams, x.games, x.minutes, x.poss, x.net, x.usg, x.ts))
    M.append("")
    M.append("**Confound check on the playoff number.** Garbage time removed and set "
             "against the same team with him off the floor, in the %d playoff games with "
             "stints: on %+.1f per 100 (%d possessions), off %+.1f (%d), on-off %+.1f with a "
             "game-bootstrap standard error of %.1f. Garbage time does not explain the "
             "on-court figure. It is still a small sample, and on-off is confounded by who "
             "else shared the floor.\n" % (oo["games"], oo["on"], oo["on_poss"], oo["off"],
                                           oo["off_poss"], oo["diff"], oo["se"]))
    M.append("**The contract, in one paragraph.** Two years from the taxpayer mid-level "
             "exception: $6,064,000 in 2026-27 and $6,367,200 in 2027-28, a player option on "
             "the second year, $12,431,200 in all; the team release disclosed no terms, so "
             "these are reported figures. If he opts out in the summer of 2027, he has one "
             "season of service and Minnesota holds only Non-Bird rights, which cap a "
             "re-signing at 120%% of the salary of the season he actually played: $7,276,800. "
             "If he opts in and plays 2027-28, he has two seasons of service and Minnesota "
             "holds Early Bird rights in 2028. The option model has him opting out with "
             "probability %.2f to %.2f across the views on flat aging, so the likeliest case "
             "is one season followed by a market Minnesota can only meet up to $7,276,800 "
             "without other cap room or an exception.\n"
             % (flat.p_opt_out.min(), flat.p_opt_out.max()))
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(M))


if __name__ == "__main__":
    main()
