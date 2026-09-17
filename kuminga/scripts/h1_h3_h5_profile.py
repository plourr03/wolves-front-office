#!/usr/bin/env python3
"""H1 remaining columns, H3 separation, H5 Minnesota on the champion sheet.

THE THREE CLEAN SEASONS ONLY: 2023-24, 2024-25, 2025-26, the seasons with a hand-
transcribed preseason board. Odds-history columns for other seasons, and pre-playoff
odds for these, are left OPEN for a pasted source rather than filled from anything
unverified.

SOURCES, per column, frozen as snapshots in `kuminga/data/bref/` (sha256 in the run log):
  B-REF league page (`leagues_NBA_YYYY`)         team Age, ORtg, DRtg, NRtg, Pace, 3PAr,
                                                 offensive and defensive four factors,
                                                 conference standings (seed)
  B-REF player advanced (`leagues_NBA_YYYY_advanced`)  best player (highest VORP on the
                                                 team), top-8 minutes-weighted age
  WAREHOUSE `nba_games`                          regular-season net rating (a second source
                                                 for NRtg), post-All-Star net rating, playoff
                                                 net rating
  WAREHOUSE `nba_player_advanced_stats`          continuity (share of minutes from players
                                                 on the team the season before), top-8
                                                 playoff games missed
  N3 `n3_team_features.csv`                      rim rate, size, top-three minutes share (not
                                                 on B-Ref's league page)
  odds files `offseason/data/*-preseason-odd.csv`  preseason price and rank

H1  one row per champion, every column.
H3  champions (n = 3) against the preseason top-5 non-champions (ties at fifth included),
    feature by feature: ranges with n, no model. A feature SEPARATES if no more than a
    quarter of non-champions fall inside the champions' range (stated before the run). The
    separating features are then set against N3's thirteen-season test where the two
    overlap.
H5  Minnesota on the sheet: 2025-26 actuals, plus 2026-27 values where the feature is
    known before the season. Each feature: inside or outside the champions' range, and
    whether a season can close the gap or only the roster can. Closable gaps are routed to
    the N8 watch list with thresholds from the champions' ranges.

    python kuminga/scripts/h1_h3_h5_profile.py
"""
from __future__ import annotations

import hashlib
import os
import re
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

BREF = os.path.join(REPO, "kuminga", "data", "bref")
ODDS = os.path.join(REPO, "offseason", "data")
OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
OUT_H1 = os.path.join(OUT_DIR, "h1_champion_sheet.csv")
OUT_H3 = os.path.join(OUT_DIR, "h3_separation.csv")
OUT_H5 = os.path.join(OUT_DIR, "h5_minnesota_sheet.csv")
OUT_R = os.path.join(OUT_DIR, "h5_watch_routes.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "h1_h3_h5_champion_profile.md")

SEASONS = {"2023-24": (2024, "BOS"), "2024-25": (2025, "OKC"), "2025-26": (2026, "NYK")}
BREF_ABBR = {"BRK": "BKN", "CHO": "CHA", "PHO": "PHX"}
SEP_SHARE = 0.25
N3_FEATURES = {"rim_rate", "size", "top3", "pace_z", "fg3a_z", "oreb_z", "opp_tov_z",
               "def_share_z"}


def clean(c):
    c = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", str(c)).strip()
    return c.replace("*", "").strip()


def table(path, first_cols):
    """Parse a B-Ref table out of a proxy snapshot, tab or pipe format."""
    lines = open(path, encoding="utf-8").read().splitlines()
    rows, header = [], None
    for ln in lines:
        if "|" in ln and ln.strip().startswith("|"):
            cells = [clean(c) for c in ln.strip().strip("|").split("|")]
        elif "\t" in ln:
            cells = [clean(c) for c in ln.split("\t")]
        else:
            if header is not None and rows:
                break
            continue
        if cells[:len(first_cols)] == first_cols:
            if header is None:
                header = cells
            continue
        if header is None or set("".join(cells)) <= set("-: "):
            continue
        if len(cells) >= len(header) - 2:
            rows.append(cells[:len(header)] + [""] * (len(header) - len(cells)))
        elif rows:
            break
    return header, rows


def team_table(year):
    h, rows = table(os.path.join(BREF, "leagues_NBA_%d.html.md" % year),
                    ["Rk", "Team", "Age", "W", "L", "PW"])
    # the four factors appear twice (offence, then defence); name them apart
    seen, names = {}, []
    for c in h:
        seen[c] = seen.get(c, 0) + 1
        names.append(c if seen[c] == 1 else "d_" + c)
    df = pd.DataFrame(rows, columns=names)
    df = df[df.Team.map(lambda t: t in E.NAME_TO_ABBR)]
    df["team"] = df.Team.map(E.NAME_TO_ABBR)
    for c in ("Age", "W", "L", "ORtg", "DRtg", "NRtg", "Pace", "3PAr", "ORB%", "d_TOV%"):
        df[c] = pd.to_numeric(df[c].str.replace("+", "", regex=False), errors="coerce")
    return df.reset_index(drop=True)


def standings(year):
    path = os.path.join(BREF, "leagues_NBA_%d.html.md" % year)
    out = {}
    for conf in ("Eastern Conference", "Western Conference"):
        h, rows = table(path, [conf, "W", "L"])
        seed = 0
        for r_ in rows:
            name = clean(r_[0])
            name = re.sub(r"\s*\(\d+\)$", "", name)
            if name in E.NAME_TO_ABBR:
                seed += 1
                out[E.NAME_TO_ABBR[name]] = seed
            if seed == 15:
                break
    return out


def players(year):
    h, rows = table(os.path.join(BREF, "leagues_NBA_%d_advanced.html.md" % year),
                    ["Rk", "Player", "Age", "Team"])
    df = pd.DataFrame(rows, columns=h)
    # multi-team totals (TOT, 2TM, 3TM) are not a team
    df = df[df.Player.ne("League Average") & df.Team.str.len().eq(3)
            & ~df.Team.eq("TOT") & ~df.Team.str.match(r"^\dTM$")]
    df["team"] = df.Team.map(lambda t: BREF_ABBR.get(t, t))
    for c in ("Age", "G", "MP", "BPM", "VORP"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def games(season_ids):
    g = db.query("""
        select game_id, season_id, game_date, team_abbreviation team, plus_minus, fga, fta,
               oreb, tov
        from nba.nba_games where season_id in %(i)s
    """, {"i": tuple(season_ids)})
    for c in ("plus_minus", "fga", "fta", "oreb", "tov"):
        g[c] = pd.to_numeric(g[c], errors="coerce")
    g = g.drop_duplicates(["game_id", "team"])
    opp = g[["game_id", "team", "fga", "fta", "oreb", "tov"]].rename(
        columns={"team": "opp", "fga": "o_fga", "fta": "o_fta", "oreb": "o_oreb", "tov": "o_tov"})
    g = g.merge(opp, on="game_id")
    g = g[g.team != g.opp].copy()
    g["poss"] = 0.5 * ((g.fga - g.oreb + g.tov + 0.44 * g.fta)
                       + (g.o_fga - g.o_oreb + g.o_tov + 0.44 * g.o_fta))
    g["game_date"] = pd.to_datetime(g.game_date)
    return g


def net100(d):
    return 100.0 * d.plus_minus.sum() / d.poss.sum()


def main():
    with runlog.run("h1_h3_h5_profile", inputs={
            "bref": {f: sha(os.path.join(BREF, f)) for f in sorted(os.listdir(BREF))},
            "sep_share": SEP_SHARE}) as r:
        # ---- the sample: champions and preseason top-5 non-champions --------------------
        sample = []
        for season, (year, champ) in SEASONS.items():
            o = pd.read_csv(os.path.join(ODDS, "%s-preseason-odd.csv" % season))
            o["p_raw"] = o.Odds.map(lambda v: 100 / (float(v) + 100) if float(v) > 0
                                    else -float(v) / (-float(v) + 100))
            o["p"] = o.p_raw / o.p_raw.sum()
            o["rank"] = o.p.rank(ascending=False, method="min").astype(int)
            o["team"] = o.Team.map(E.NAME_TO_ABBR)
            top = o[o["rank"] <= 5]
            for _, x in top.iterrows():
                sample.append(dict(season=season, year=year, team=x.team,
                                   group="champion" if x.team == champ else "top-5 non-champion",
                                   pre_implied=100 * x.p, pre_rank=int(x["rank"])))
            if champ not in set(top.team):
                c = o[o.team == champ].iloc[0]
                sample.append(dict(season=season, year=year, team=champ, group="champion",
                                   pre_implied=100 * c.p, pre_rank=int(c["rank"])))
            m = o[o.team == "MIN"].iloc[0]
            if "MIN" not in set(top.team) and season == "2025-26":
                sample.append(dict(season=season, year=year, team="MIN",
                                   group="Minnesota (not top 5)", pre_implied=100 * m.p,
                                   pre_rank=int(m["rank"])))
        SAM = pd.DataFrame(sample)
        r.note("sample: %s" % "; ".join("%s %s %s (#%d)" % (x.season, x.team, x.group,
                                                             x.pre_rank)
                                         for _, x in SAM.iterrows()))

        feats = []
        gate_rows = []
        for season, (year, champ) in SEASONS.items():
            tt = team_table(year)
            if len(tt) != 30:
                raise RuntimeError("B-Ref team table for %d parsed %d teams" % (year, len(tt)))
            seeds = standings(year)
            if len(seeds) != 30:
                raise RuntimeError("standings for %d parsed %d teams" % (year, len(seeds)))
            pl = players(year)
            if pl.team.nunique() != 30:
                raise RuntimeError("player table for %d covers %d teams" % (year,
                                                                            pl.team.nunique()))
            y0 = year - 1
            rs = games([20000 + y0])
            po = games([40000 + y0])
            # G1: warehouse regular-season net against B-Ref NRtg
            wn = rs.groupby("team").apply(net100, include_groups=False)
            chk = tt.set_index("team").NRtg.to_frame().join(wn.rename("wh"))
            corr = float(chk.NRtg.corr(chk.wh))
            mad = float((chk.NRtg - chk.wh).abs().mean())
            rank_agree = float((chk.NRtg.rank(ascending=False) ==
                                chk.wh.rank(ascending=False)).mean())
            gate_rows.append(dict(season=season, corr=corr, mad=mad, rank_agree=rank_agree))
            r.note("G1 %s: B-Ref NRtg vs warehouse net, corr %.4f, mean abs diff %.2f, "
                   "identical rank for %.0f%% of teams" % (season, corr, mad, 100 * rank_agree))
            if corr < 0.99:
                raise RuntimeError("G1 failed: B-Ref and warehouse net ratings disagree")

            # All-Star break: the longest gap between league game dates in February
            dates = pd.Series(sorted(rs.game_date.unique()))
            feb = dates[dates.dt.month.isin([2, 3])].reset_index(drop=True)
            gaps = feb.diff()
            i = int(gaps.idxmax())
            asb_end = feb[i]
            post = rs[rs.game_date >= asb_end]
            post_net = post.groupby("team").apply(net100, include_groups=False)
            po_net = po.groupby("team").apply(net100, include_groups=False)
            r.note("   All-Star break ends %s (gap %d days)" % (asb_end.date(),
                                                              gaps.max().days))

            # continuity and playoff health, from game logs
            adv = db.query("""
                select substr(game_id,1,5) p, person_id::bigint pid, team_tricode team,
                       sum(minutes_float) mins, count(distinct game_id) g
                from nba.nba_player_advanced_stats
                where substr(game_id,1,5) in %(p)s and minutes_float > 0 group by 1, 2, 3
            """, {"p": ("002%02d" % (y0 % 100), "002%02d" % ((y0 - 1) % 100),
                        "004%02d" % (y0 % 100))})
            adv["mins"] = pd.to_numeric(adv.mins)
            cur = adv[adv.p == "002%02d" % (y0 % 100)]
            prev = adv[adv.p == "002%02d" % ((y0 - 1) % 100)]
            pog = adv[adv.p == "004%02d" % (y0 % 100)]
            prev_set = set(zip(prev.team, prev.pid))
            po_games = po.groupby("team").game_id.nunique()

            z = lambda s: (s - s.mean()) / s.std(ddof=0)  # noqa: E731
            tt["def_share"] = (tt.DRtg.mean() - tt.DRtg) - (tt.ORtg - tt.ORtg.mean())
            for c_, src in (("Pace", "pace_z"), ("3PAr", "fg3a_z"), ("ORB%", "oreb_z"),
                            ("d_TOV%", "opp_tov_z"), ("def_share", "def_share_z")):
                tt[src] = z(tt[c_])
            tt["nrtg_rank"] = tt.NRtg.rank(ascending=False, method="min")
            tt["ortg_rank"] = tt.ORtg.rank(ascending=False, method="min")
            tt["drtg_rank"] = tt.DRtg.rank(ascending=True, method="min")
            post_rank = post_net.rank(ascending=False, method="min")
            n3 = pd.read_csv(os.path.join(OUT_DIR, "n3_team_features.csv"))
            n3 = n3[n3.season == season].set_index("team")

            for team in set(SAM[SAM.season == season].team) | {"MIN"}:
                t = tt.set_index("team").loc[team]
                ct = cur[cur.team == team]
                cont = float(ct[[(team, p) in prev_set for p in ct.pid]].mins.sum()
                             / ct.mins.sum())
                top8 = ct.sort_values("mins", ascending=False).head(8)
                if team in po_games.index:
                    gp = pog[pog.team == team].set_index("pid").g
                    missed = int(sum(po_games[team] - gp.get(p, 0) for p in top8.pid))
                    po_n = float(po_net[team])
                else:
                    missed, po_n = np.nan, np.nan
                pt = pl[pl.team == team].sort_values("MP", ascending=False)
                best = pt.sort_values("VORP", ascending=False).iloc[0]
                t8 = pt.head(8)
                feats.append(dict(
                    season=season, team=team,
                    nrtg=float(t.NRtg), nrtg_rank=int(t.nrtg_rank), ortg_rank=int(t.ortg_rank),
                    drtg_rank=int(t.drtg_rank), post_asb_net=float(post_net[team]),
                    post_asb_rank=int(post_rank[team]), seed=int(seeds[team]),
                    po_net=po_n, po_minus_rs=po_n - float(wn[team]) if pd.notna(po_n) else np.nan,
                    best_player=best.Player, best_vorp=float(best.VORP), best_bpm=float(best.BPM),
                    top8_age=float(np.average(t8.Age, weights=t8.MP)),
                    team_age_bref=float(t.Age), continuity=cont,
                    top8_po_games_missed=missed,
                    pace_z=float(t.pace_z), fg3a_z=float(t.fg3a_z), oreb_z=float(t.oreb_z),
                    opp_tov_z=float(t.opp_tov_z), def_share_z=float(t.def_share_z),
                    rim_rate=float(n3.loc[team, "rim_rate"]), size=float(n3.loc[team, "size"]),
                    top3=float(n3.loc[team, "top3"])))
        F = pd.DataFrame(feats)
        S = SAM.merge(F, on=["season", "team"], how="left")
        H1 = S[S.group == "champion"].copy()
        H1["pre_playoff_odds"] = "OPEN: awaiting a pasted source"
        H1.to_csv(OUT_H1, index=False)
        r.note("")
        r.note("H1, champions:")
        for _, x in H1.iterrows():
            r.note("  %s %s pre %.2f%% #%d | NRtg %+.1f #%d (O #%d, D #%d) | post-ASB #%d | seed %d "
                   "| playoff %+.1f (vs RS %+.1f) | best %s VORP %.1f | top-8 age %.1f | "
                   "continuity %.2f | top-8 playoff games missed %s"
                   % (x.season, x.team, x.pre_implied, x.pre_rank, x.nrtg, x.nrtg_rank,
                      x.ortg_rank, x.drtg_rank, x.post_asb_rank, x.seed, x.po_net,
                      x.po_minus_rs, x.best_player, x.best_vorp, x.top8_age, x.continuity,
                      x.top8_po_games_missed))

        # ---- H3 --------------------------------------------------------------------
        NUM = [("pre_implied", "preseason implied %", "high"), ("pre_rank", "preseason rank", "low"),
               ("nrtg_rank", "net rating rank", "low"), ("ortg_rank", "offence rank", "low"),
               ("drtg_rank", "defence rank", "low"), ("post_asb_rank", "post-All-Star net rank", "low"),
               ("seed", "seed", "low"), ("po_minus_rs", "playoff minus regular-season net", "high"),
               ("best_vorp", "best player VORP", "high"), ("top8_age", "top-8 age", None),
               ("continuity", "continuity", "high"),
               ("top8_po_games_missed", "top-8 playoff games missed", "low"),
               ("pace_z", "pace (z)", None), ("fg3a_z", "three-point rate (z)", None),
               ("oreb_z", "offensive rebound rate (z)", None),
               ("opp_tov_z", "turnovers forced (z)", None),
               ("def_share_z", "defence share (z)", None), ("rim_rate", "rim rate (z)", None),
               ("size", "size (z)", None), ("top3", "top-three minutes share (z)", None)]
        ch = S[S.group == "champion"]
        nc = S[S.group == "top-5 non-champion"]
        h3 = []
        for col, lab, _ in NUM:
            c_, n_ = ch[col].dropna(), nc[col].dropna()
            lo, hi = float(c_.min()), float(c_.max())
            inside = int(((n_ >= lo) & (n_ <= hi)).sum())
            h3.append(dict(feature=col, label=lab, champions=", ".join("%.2f" % v for v in c_),
                           champ_lo=lo, champ_hi=hi, n_champ=len(c_), n_non=len(n_),
                           non_lo=float(n_.min()), non_median=float(n_.median()),
                           non_hi=float(n_.max()), non_inside=inside,
                           share_inside=inside / len(n_) if len(n_) else np.nan,
                           separates=bool(len(n_) and inside / len(n_) <= SEP_SHARE)))
        H3 = pd.DataFrame(h3)
        n3res = pd.read_csv(os.path.join(OUT_DIR, "n3_translation_tests.csv"))
        n3res = n3res[n3res["sample"] == "longer 2014-26"].set_index("feature")
        n3map = {"pace_z": "pace", "fg3a_z": "fg3a_rate", "oreb_z": "oreb_rate",
                 "opp_tov_z": "opp_tov_rate", "def_share_z": "def_share", "rim_rate": "rim_rate",
                 "size": "size", "top3": "top3"}
        H3["n3_feature"] = H3.feature.map(n3map)
        H3["n3_translates"] = H3.n3_feature.map(lambda f: bool(n3res.loc[f, "translates"])
                                                if isinstance(f, str) else np.nan)
        H3["n3_coef"] = H3.n3_feature.map(lambda f: float(n3res.loc[f, "coef"])
                                          if isinstance(f, str) else np.nan)
        H3.to_csv(OUT_H3, index=False)
        r.note("")
        r.note("H3, champions (n=%d) vs top-5 non-champions (n=%d); separates if <= %.0f%% of "
               "non-champions inside the champions' range:" % (len(ch), len(nc), 100 * SEP_SHARE))
        for _, x in H3.iterrows():
            r.note("  %-34s champs %-24s non %.2f..%.2f (median %.2f), %2d of %2d inside %s%s"
                   % (x.label, x.champions, x.non_lo, x.non_hi, x.non_median, x.non_inside,
                      x.n_non, "SEPARATES" if x.separates else "",
                      "" if not isinstance(x.n3_feature, str) else
                      " | N3: %s (coef %+.2f)" % ("translates" if x.n3_translates else
                                                  "no signal", x.n3_coef)))

        # ---- H5 --------------------------------------------------------------------
        mn = S[(S.team == "MIN") & (S.season == "2025-26")].iloc[0] if len(
            S[(S.team == "MIN") & (S.season == "2025-26")]) else F[(F.team == "MIN") & (
                F.season == "2025-26")].iloc[0]
        mkt = pd.read_csv(os.path.join(OUT_DIR, "market_devig_2026_27.csv")).set_index("team_abbr")
        rot = pd.read_csv(os.path.join(OUT_DIR, "rotations_2026_27.csv"))
        cur27 = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN") & (rot.mpg > 0)]
        base26 = rot[(rot.scenario == "baseline") & (rot.team_abbr == "MIN")]
        cont27 = float(cur27[cur27.player_id.isin(base26.player_id)].mpg.sum() / cur27.mpg.sum())
        CLOSABLE = {"nrtg_rank", "ortg_rank", "drtg_rank", "post_asb_rank", "seed",
                    "po_minus_rs", "top8_po_games_missed"}
        PRE = {"pre_implied": 100 * float(mkt.loc["MIN", "market_prop"]),
               "pre_rank": int(mkt.loc["MIN", "market_rank"]), "continuity": cont27}
        h5, routes = [], []
        for col, lab, good in NUM:
            row = H3[H3.feature == col].iloc[0]
            val26 = float(mn[col]) if pd.notna(mn[col]) else np.nan
            val = PRE.get(col, val26)
            when = "2026-27 (known now)" if col in PRE else "2025-26 actual"
            inside = bool(row.champ_lo <= val <= row.champ_hi) if pd.notna(val) else None
            if inside is None:
                status = "n/a"
            elif inside:
                status = "inside the champions' range"
            elif good is None:
                # a style or age feature has no better direction (N3 found none translates)
                status = "outside, above" if val > row.champ_hi else "outside, below"
            else:
                better = (val > row.champ_hi) if good == "high" else (val < row.champ_lo)
                status = "outside, on the good side" if better else "outside, short of it"
            kind = "a season can close it" if col in CLOSABLE else "set by the roster or the market"
            h5.append(dict(feature=col, label=lab, minnesota=val, basis=when,
                           champ_lo=row.champ_lo, champ_hi=row.champ_hi, status=status,
                           closable=kind, separates=row.separates))
            if status == "outside, short of it" and col in CLOSABLE:
                thr = row.champ_hi if good == "low" else row.champ_lo
                routes.append(dict(feature=col, label=lab, minnesota_2025_26=val,
                                   champions_range="%.2f to %.2f" % (row.champ_lo, row.champ_hi),
                                   threshold=("%s %.0f or better" % (lab, thr)) if good == "low"
                                   else ("%s %.2f or better" % (lab, thr)),
                                   checkable="season end" if col in ("nrtg_rank", "ortg_rank",
                                                                     "drtg_rank", "seed")
                                   else ("after the All-Star break" if col == "post_asb_rank"
                                         else "the playoffs"),
                                   separates=row.separates))
        H5 = pd.DataFrame(h5)
        H5.to_csv(OUT_H5, index=False)
        R = pd.DataFrame(routes)
        R.to_csv(OUT_R, index=False)
        r.note("")
        r.note("H5, Minnesota:")
        for _, x in H5.iterrows():
            r.note("  %-34s %8.2f (%s) champions %.2f..%.2f -> %s; %s"
                   % (x.label, x.minnesota, x.basis, x.champ_lo, x.champ_hi, x.status,
                      x.closable))
        r.note("routed to N8: %s" % ("; ".join(R.threshold) if len(R) else "none"))
        for f in (OUT_H1, OUT_H3, OUT_H5, OUT_R):
            r.output(f)
        write_doc(r, H1, H3, H5, R, pd.DataFrame(gate_rows), len(ch), len(nc))
        r.output(OUT_MD)


def write_doc(r, H1, H3, H5, R, G, n_ch, n_nc):
    L = ["# H1, H3, H5: the champion profile, and Minnesota on it\n",
         "*As of 2026-09-17. Three clean seasons (2023-24 to 2025-26). OBSERVED throughout, "
         "except Minnesota's 2026-27 preseason price, continuity and projected rank. Run `%s`. "
         "B-Ref pages frozen in `kuminga/data/bref/` with hashes in the run log.*\n" % r.run_id,
         "**Two sources for the net ratings.** B-Ref's NRtg against this warehouse's game-log "
         "net rating: correlation %s, mean absolute difference %s points, identical league "
         "rank for %s of teams.\n" % (", ".join("%.4f" % v for v in G["corr"]),
                                       ", ".join("%.2f" % v for v in G.mad),
                                       ", ".join("%.0f%%" % (100 * v) for v in G.rank_agree)),
         "## H1. The champions\n",
         "| season | champion | preseason | net rating (rank) | offence / defence rank | "
         "post-All-Star rank | seed | playoff net (vs regular season) | best player (VORP) | "
         "top-8 age | continuity | top-8 playoff games missed | pre-playoff odds |",
         "|---|---|---|---|---|---:|---:|---|---|---:|---:|---:|---|"]
    for _, x in H1.iterrows():
        L.append("| %s | %s | %.2f%%, #%d | %+.1f (#%d) | #%d / #%d | %d | %d | %+.1f (%+.1f) | "
                 "%s (%.1f) | %.1f | %.2f | %d | %s |"
                 % (x.season, x.team, x.pre_implied, x.pre_rank, x.nrtg, x.nrtg_rank,
                    x.ortg_rank, x.drtg_rank, x.post_asb_rank, x.seed, x.po_net, x.po_minus_rs,
                    x.best_player, x.best_vorp, x.top8_age, x.continuity,
                    x.top8_po_games_missed, x.pre_playoff_odds))
    L.append("")
    L.append("## H3. Champions against the preseason top-5 teams that did not win\n")
    L.append("n = %d champions against %d non-champions (every team priced in the top five, "
             "ties at fifth included). A feature **separates** if no more than a quarter of the "
             "non-champions fall inside the champions' range. With three champions a range is "
             "wide by chance and narrow by chance; nothing here is a rate.\n" % (n_ch, n_nc))
    L.append("| feature | champions | non-champions: low / median / high | non-champions inside "
             "the champions' range | separates | N3, 13 seasons |")
    L.append("|---|---|---|---|---|---|")
    for _, x in H3.iterrows():
        L.append("| %s | %s | %.2f / %.2f / %.2f | %d of %d | %s | %s |"
                 % (x.label, x.champions, x.non_lo, x.non_median, x.non_hi, x.non_inside,
                    x.n_non, "**yes**" if x.separates else "no",
                    "" if not isinstance(x.n3_feature, str) else
                    ("translates" if x.n3_translates else "no signal (coef %+.2f)" % x.n3_coef)))
    L.append("")
    sep = H3[H3.separates]
    both = sep[sep.n3_feature.map(lambda f: isinstance(f, str))]
    L.append("**Where H3 and N3 meet.** %s\n" % (
        ("Of the separating features, %s %s also tested in N3's thirteen seasons, and N3 found "
         "no out-of-sample signal for %s. Three champions separating on a feature is a "
         "description of three teams; thirteen seasons of series is the test, and the test "
         "says no." % (", ".join(both.label), "is" if len(both) == 1 else "are",
                       "it" if len(both) == 1 else "any of them"))
        if len(both) else
        ("None of the separating features is a style or translation feature, so H3 and N3 do "
         "not overlap: what separates these champions (%s) is level and health, which N3 "
         "holds fixed through net rating rather than tests." % ", ".join(sep.label))
        if len(sep) else "No feature separates, and N3 found none that translates: they agree."))
    L.append("## H5. Minnesota on the sheet\n")
    L.append("| feature | Minnesota | basis | champions' range | status | closable? |")
    L.append("|---|---:|---|---|---|---|")
    for _, x in H5.iterrows():
        L.append("| %s | %.2f | %s | %.2f to %.2f | %s | %s |"
                 % (x.label, x.minnesota, x.basis, x.champ_lo, x.champ_hi, x.status, x.closable))
    L.append("")
    L.append("**Routed to the N8 watch list** (closable gaps, thresholds from the champions' "
             "ranges): %s\n" % ("; ".join("%s, checkable %s" % (x.threshold, x.checkable)
                                          for _, x in R.iterrows()) if len(R) else "none"))
    L.append("*Open columns.* Pre-playoff odds for these seasons, and every odds-history column "
             "for seasons before 2023-24, are left open for a pasted source. Nothing here was "
             "filled from an unverified odds table.\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
