#!/usr/bin/env python3
"""H1 champion sheet, H3 separation, H5 Minnesota on the sheet: eleven seasons.

SAMPLE. Every champion 2015-16 to 2025-26 (`outputs/c1_champions.csv`) against every
preseason top-five team that did not win (`outputs/c1_contenders.csv`, tied prices sharing a
rank, ties at fifth included), plus Minnesota 2025-26 for H5. The team-level features come
from the same machinery for every team, `c1_champions.build` (warehouse box scores and
Basketball-Reference transaction logs), so a champion and a non-champion are measured the
same way.

FEATURES (H3, eleven seasons). Preseason implied price and rank; regular-season net-rating
rank (warehouse), offence and defence rank (B-Ref league page); post-All-Star rank; seed;
playoff minus regular-season net; the best player's VORP (B-Ref player advanced); top-8 age;
continuity BY APPEARANCE and BY CONTRACT, each as a count of the top eight and as the share
of playoff minutes; top-8 games missed in the regular season and in the playoffs; the top
five's minute share in the regular season and in the playoffs, and the tightening between
them.

STYLE FEATURES (three seasons, labeled). Pace, three-point rate, offensive rebounding,
turnovers forced and defence share (B-Ref league page, z-scored within the season) and N3's
rim rate, size and top-three share. Reported on 2023-24 to 2025-26 as before and labeled as
such; the same comparison on all eleven seasons is written to a second table for the record.

RULE. A feature separates if no more than a quarter of the non-champions fall inside the
champions' range (minimum to maximum), stated before the run. n is stated for every feature.
Nothing here is a model.

GATES, each fatal. G1: B-Ref NRtg against the warehouse net rating, every season,
correlation at least 0.99. G2: for 2023-24 to 2025-26 the B-Ref-derived columns (NRtg and
its rank, offence and defence rank, seed, best player and his VORP) must equal what the
previous three-season run produced from the proxy snapshots (git HEAD's
`h1_champion_sheet.csv`), so the change of parser changes no number.

H5. Minnesota on the sheet: 2025-26 actuals built the same way (`c1_contenders.csv`, group
"minnesota"), plus 2026-27 values known now (market price and rank; continuity by contract
and by appearance from the current roster against last season's). Each feature: inside or
outside the eleven champions' range, and whether a season can close the gap. Closable gaps
are routed to the N8 watch list with thresholds from the champions' ranges.

    python kuminga/scripts/h1_h3_h5_profile.py
"""
from __future__ import annotations

import io
import os
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "postmortem"))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import bref, runlog  # noqa: E402
from lib import db                    # noqa: E402
import bracket_sim as E               # noqa: E402
import c1_champions as C1             # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
OUT_H1 = os.path.join(OUT_DIR, "h1_champion_sheet.csv")
OUT_H3 = os.path.join(OUT_DIR, "h3_separation.csv")
OUT_H3S = os.path.join(OUT_DIR, "h3_separation_style_eleven.csv")
OUT_H5 = os.path.join(OUT_DIR, "h5_minnesota_sheet.csv")
OUT_R = os.path.join(OUT_DIR, "h5_watch_routes.csv")
OUT_SAMPLE = os.path.join(OUT_DIR, "h3_sample.csv")
OUT_MD = os.path.join(REPO, "kuminga", "docs", "h1_h3_h5_champion_profile.md")
AS_OF = "2026-09-24"

BREF_ABBR = {"BRK": "BKN", "CHO": "CHA", "PHO": "PHX"}
SEP_SHARE = 0.25
STYLE_SEASONS = ["2023-24", "2024-25", "2025-26"]
STYLE = ["pace_z", "fg3a_z", "oreb_z", "opp_tov_z", "def_share_z", "rim_rate", "size", "top3"]

# (column, label, better direction or None, scope)
NUM = [
    ("pre_implied", "preseason implied %", "high", "eleven"),
    ("pre_rank", "preseason rank", "low", "eleven"),
    ("nrtg_rank", "net rating rank", "low", "eleven"),
    ("ortg_rank", "offence rank", "low", "eleven"),
    ("drtg_rank", "defence rank", "low", "eleven"),
    ("post_asb_rank", "post-All-Star net rank", "low", "eleven"),
    ("seed", "seed", "low", "eleven"),
    ("po_minus_rs", "playoff minus regular-season net", "high", "eleven"),
    ("best_vorp", "best player VORP", "high", "eleven"),
    ("top8_age", "top-8 age", None, "eleven"),
    ("top8_returning_appear", "top-8 returning, by appearance", "high", "eleven"),
    ("top8_returning_contract", "top-8 returning, by contract", "high", "eleven"),
    ("returning_share_appear", "returning share of playoff minutes, by appearance", "high", "eleven"),
    ("returning_share_contract", "returning share of playoff minutes, by contract", "high", "eleven"),
    ("top8_rs_games_missed", "top-8 regular-season games missed", None, "eleven"),
    ("top8_po_games_missed", "top-8 playoff games missed", "low", "eleven"),
    ("top5_share_rs", "top-five minute share, regular season", None, "eleven"),
    ("top5_share_po", "top-five minute share, playoffs", "high", "eleven"),
    ("tighten", "top-five share, playoffs minus regular season", "high", "eleven"),
    ("pace_z", "pace (z)", None, "three"),
    ("fg3a_z", "three-point rate (z)", None, "three"),
    ("oreb_z", "offensive rebound rate (z)", None, "three"),
    ("opp_tov_z", "turnovers forced (z)", None, "three"),
    ("def_share_z", "defence share (z)", None, "three"),
    ("rim_rate", "rim rate (z)", None, "three"),
    ("size", "size (z)", None, "three"),
    ("top3", "top-three minutes share (z)", None, "three"),
]
CLOSABLE = {"nrtg_rank", "ortg_rank", "drtg_rank", "post_asb_rank", "seed", "po_minus_rs",
            "top8_po_games_missed", "top5_share_po", "tighten"}
N3MAP = {"pace_z": "pace", "fg3a_z": "fg3a_rate", "oreb_z": "oreb_rate", "opp_tov_z": "opp_tov_rate",
         "def_share_z": "def_share", "rim_rate": "rim_rate", "size": "size", "top3": "top3"}


# ---------------------------------------------------------------- Basketball-Reference, html cache
def league_html(year):
    return bref.strip_comments(bref.fetch("/leagues/NBA_%d.html" % year))


def team_table(year):
    t = pd.read_html(io.StringIO(league_html(year)), attrs={"id": "advanced-team"})[0]
    cols = [c[1] if not str(c[1]).startswith("Unnamed") else c[0] for c in t.columns]
    seen, names = {}, []
    for c in cols:                              # the four factors appear twice: offence, then defence
        seen[c] = seen.get(c, 0) + 1
        names.append(c if seen[c] == 1 else "d_" + c)
    t.columns = names
    t = t[t.Team.notna()].copy()
    t["Team"] = t.Team.astype(str).str.replace("*", "", regex=False).str.strip()
    t = t[t.Team.isin(E.NAME_TO_ABBR)].copy()
    t["team"] = t.Team.map(E.NAME_TO_ABBR)
    for c in ("Age", "W", "L", "ORtg", "DRtg", "NRtg", "Pace", "3PAr", "ORB%", "d_TOV%"):
        t[c] = pd.to_numeric(t[c], errors="coerce")
    if len(t) != 30:
        raise RuntimeError("B-Ref team table for %d parsed %d teams" % (year, len(t)))
    return t.reset_index(drop=True)


def standings(year):
    html = league_html(year)
    out = {}
    for conf in ("E", "W"):
        d = pd.read_html(io.StringIO(html), attrs={"id": "confs_standings_%s" % conf})[0]
        names = (d[d.columns[0]].astype(str).str.replace("*", "", regex=False)
                 .str.replace(r"\s*\(\d+\)$", "", regex=True).str.strip())
        seed = 0
        for nm in names:
            if nm in E.NAME_TO_ABBR:
                seed += 1
                out[E.NAME_TO_ABBR[nm]] = seed
    if len(out) != 30:
        raise RuntimeError("standings for %d parsed %d teams" % (year, len(out)))
    return out


def players(year):
    html = bref.strip_comments(bref.fetch("/leagues/NBA_%d_advanced.html" % year))
    d = pd.read_html(io.StringIO(html), attrs={"id": "advanced"})[0]
    d = d[d.Player.notna() & (d.Player != "Player") & (d.Player != "League Average")].copy()
    d["Team"] = d.Team.astype(str)
    d = d[d.Team.str.len().eq(3) & ~d.Team.eq("TOT") & ~d.Team.str.match(r"^\dTM$")].copy()
    d["team"] = d.Team.map(lambda t: BREF_ABBR.get(t, t))
    for c in ("Age", "G", "MP", "BPM", "VORP"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    if d.team.nunique() != 30:
        raise RuntimeError("player table for %d covers %d teams" % (year, d.team.nunique()))
    return d


def head_csv(relpath):
    """A file as it is at git HEAD, or None."""
    try:
        out = subprocess.run(["git", "show", "HEAD:" + relpath], capture_output=True, text=True,
                             encoding="utf-8", cwd=REPO, check=True).stdout
        return pd.read_csv(io.StringIO(out))
    except Exception:
        return None


def separation(ch, nc, col, lab, scope):
    c_, n_ = ch[col].dropna(), nc[col].dropna()
    lo, hi = float(c_.min()), float(c_.max())
    inside = int(((n_ >= lo) & (n_ <= hi)).sum())
    return dict(feature=col, label=lab, seasons=scope,
                champions=", ".join("%.2f" % v for v in c_), champ_lo=lo, champ_hi=hi,
                champ_median=float(c_.median()), n_champ=len(c_), n_non=len(n_),
                non_lo=float(n_.min()), non_median=float(n_.median()), non_hi=float(n_.max()),
                non_inside=inside, share_inside=inside / len(n_) if len(n_) else np.nan,
                separates=bool(len(n_) and inside / len(n_) <= SEP_SHARE))


def main():
    C = pd.read_csv(os.path.join(OUT_DIR, "c1_champions.csv"))
    C["group"] = "champion"
    N = pd.read_csv(os.path.join(OUT_DIR, "c1_contenders.csv"))
    S = pd.concat([C, N], ignore_index=True)
    seasons = sorted(S.season.unique())
    man = bref.manifest()
    keys = ["leagues_NBA_%d" % (int(s[:4]) + 1) for s in seasons] + ["leagues_NBA_%d_advanced" % (int(s[:4]) + 1) for s in seasons]
    with runlog.run("h1_h3_h5_profile", inputs={
            "bref": {k: man[k]["sha256"][:16] for k in keys if k in man},
            "sep_share": SEP_SHARE, "style_seasons": STYLE_SEASONS,
            "sample": {"champions": len(C), "non_champions": int((N.group == "top-5 non-champion").sum())}}) as r:
        n3 = pd.read_csv(os.path.join(OUT_DIR, "n3_team_features.csv"))
        feats, gate_rows = [], []
        for season in seasons:
            year = int(season[:4]) + 1
            tt = team_table(year)
            seeds = standings(year)
            pl = players(year)
            tt["def_share"] = (tt.DRtg.mean() - tt.DRtg) - (tt.ORtg - tt.ORtg.mean())
            z = lambda s: (s - s.mean()) / s.std(ddof=0)  # noqa: E731
            for c_, src in (("Pace", "pace_z"), ("3PAr", "fg3a_z"), ("ORB%", "oreb_z"),
                            ("d_TOV%", "opp_tov_z"), ("def_share", "def_share_z")):
                tt[src] = z(tt[c_])
            tt["nrtg_rank_bref"] = tt.NRtg.rank(ascending=False, method="min").astype(int)
            tt["ortg_rank"] = tt.ORtg.rank(ascending=False, method="min").astype(int)
            tt["drtg_rank"] = tt.DRtg.rank(ascending=True, method="min").astype(int)
            T = tt.set_index("team")
            # G1: B-Ref NRtg against the warehouse net rating, all thirty teams
            wn = C1.net_ratings(20000 + year - 1)
            chk = T.NRtg.to_frame().join(wn.net.astype(float).rename("wh"))
            corr = float(chk.NRtg.corr(chk.wh))
            mad = float((chk.NRtg - chk.wh).abs().mean())
            rank_agree = float((chk.NRtg.rank(ascending=False) == chk.wh.rank(ascending=False)).mean())
            gate_rows.append(dict(season=season, corr=corr, mad=mad, rank_agree=rank_agree))
            r.note("G1 %s: B-Ref NRtg vs warehouse net, corr %.4f, mean abs diff %.2f, identical rank for %.0f%% of teams"
                   % (season, corr, mad, 100 * rank_agree))
            if corr < 0.99:
                raise RuntimeError("G1 failed for %s: B-Ref and warehouse net ratings disagree" % season)
            n3s = n3[n3.season == season].set_index("team")
            for _, x in S[S.season == season].iterrows():
                team = x.team
                t = T.loc[team]
                pt = pl[pl.team == team]
                best = pt.sort_values("VORP", ascending=False).iloc[0]
                t8 = pt.sort_values("MP", ascending=False).head(8)
                feats.append(dict(
                    season=season, team=team,
                    nrtg_bref=float(t.NRtg), nrtg_rank_bref=int(t.nrtg_rank_bref),
                    ortg_rank=int(t.ortg_rank), drtg_rank=int(t.drtg_rank), seed_page=int(seeds[team]),
                    best_player=best.Player, best_vorp=float(best.VORP), best_bpm=float(best.BPM),
                    top8_age_mp=float(np.average(t8.Age, weights=t8.MP)), team_age_bref=float(t.Age),
                    pace_z=float(t.pace_z), fg3a_z=float(t.fg3a_z), oreb_z=float(t.oreb_z),
                    opp_tov_z=float(t.opp_tov_z), def_share_z=float(t.def_share_z),
                    rim_rate=float(n3s.loc[team, "rim_rate"]), size=float(n3s.loc[team, "size"]),
                    top3=float(n3s.loc[team, "top3"])))
        F = pd.DataFrame(feats)
        S = S.merge(F, on=["season", "team"], how="left")
        # the H3 columns, named for the table
        S["pre_implied"] = S.preseason_implied_pct
        S["pre_rank"] = S.preseason_rank
        S["nrtg"] = S.net_rs
        S["nrtg_rank"] = S.net_rs_rank
        S["post_asb_rank"] = S.net_post_asb_rank
        S["seed"] = S.seed_bref.fillna(S.seed_warehouse).astype(int)
        S["po_minus_rs"] = S.net_po_minus_rs
        S["top8_age"] = S.top8_mean_age
        S["top8_returning_appear"] = S.top8_returning
        S["returning_share_appear"] = S.returning_po_minutes_share
        S["returning_share_contract"] = S.returning_po_minutes_share_contract
        S["tighten"] = S.top5_share_po - S.top5_share_rs
        S.to_csv(OUT_SAMPLE, index=False)
        seed_diff = S[S.seed != S.seed_page]
        if len(seed_diff):
            r.note("seed: the B-Ref standings order differs from the team page finish for %s (team page used)"
                   % "; ".join("%s %s (%d vs %d)" % (x.season, x.team, x.seed, x.seed_page) for _, x in seed_diff.iterrows()))

        # G2: the parser change must reproduce the three-season run's B-Ref columns
        old = head_csv("kuminga/outputs/h1_champion_sheet.csv")
        if old is not None and "nrtg" in old.columns:
            bad = []
            for _, o in old[old.season.isin(STYLE_SEASONS)].iterrows():
                nw = S[(S.season == o.season) & (S.team == o.team)]
                if not len(nw):
                    continue
                nw = nw.iloc[0]
                for a, b in (("nrtg", "nrtg_bref"), ("nrtg_rank", "nrtg_rank_bref"), ("ortg_rank", "ortg_rank"),
                             ("drtg_rank", "drtg_rank"), ("seed", "seed"), ("best_player", "best_player"),
                             ("best_vorp", "best_vorp")):
                    if str(o[a]) != str(nw[b]) and not (isinstance(o[a], float) and abs(float(o[a]) - float(nw[b])) < 1e-9):
                        bad.append("%s %s %s: was %r, now %r" % (o.season, o.team, a, o[a], nw[b]))
            r.note("G2: %d B-Ref-derived values compared with the three-season run, %d differ%s"
                   % (7 * len(old[old.season.isin(STYLE_SEASONS)]), len(bad), (": " + "; ".join(bad)) if bad else ""))
            if bad:
                raise RuntimeError("G2 failed: the html parser does not reproduce the snapshot run")
        else:
            r.note("G2: no previous h1_champion_sheet.csv at HEAD to compare with")

        H1 = S[S.group == "champion"].copy()
        H1.to_csv(OUT_H1, index=False)
        r.note("")
        r.note("H1, champions (n=%d):" % len(H1))
        for _, x in H1.iterrows():
            r.note("  %s %s pre %.2f%% #%d | net %+.1f #%d (O #%d, D #%d) | post-ASB #%d | seed %d | playoff %+.1f (vs RS %+.1f) "
                   "| best %s VORP %.1f | age %.1f | returning %d/%d (appearance/contract), share %.2f/%.2f | missed %d RS, %d PO "
                   "| top-5 %.2f -> %.2f"
                   % (x.season, x.team, x.pre_implied, x.pre_rank, x.nrtg, x.nrtg_rank, x.ortg_rank, x.drtg_rank, x.post_asb_rank,
                      x.seed, x.net_po, x.po_minus_rs, x.best_player, x.best_vorp, x.top8_age, x.top8_returning_appear,
                      x.top8_returning_contract, x.returning_share_appear, x.returning_share_contract,
                      x.top8_rs_games_missed, x.top8_po_games_missed, x.top5_share_rs, x.top5_share_po))

        # ---- H3 ---------------------------------------------------------------------------
        ch = S[S.group == "champion"]
        nc = S[S.group == "top-5 non-champion"]
        ch3, nc3 = ch[ch.season.isin(STYLE_SEASONS)], nc[nc.season.isin(STYLE_SEASONS)]
        h3, h3s = [], []
        for col, lab, _, scope in NUM:
            if scope == "eleven":
                h3.append(separation(ch, nc, col, lab, "eleven (2015-16 to 2025-26)"))
            else:
                h3.append(separation(ch3, nc3, col, lab, "three (2023-24 to 2025-26)"))
                h3s.append(separation(ch, nc, col, lab, "eleven (2015-16 to 2025-26)"))
        H3, H3S = pd.DataFrame(h3), pd.DataFrame(h3s)
        n3res = pd.read_csv(os.path.join(OUT_DIR, "n3_translation_tests.csv"))
        n3res = n3res[n3res["sample"] == "longer 2014-26"].set_index("feature")
        for H in (H3, H3S):
            H["n3_feature"] = H.feature.map(N3MAP)
            H["n3_translates"] = H.n3_feature.map(lambda f: bool(n3res.loc[f, "translates"]) if isinstance(f, str) else np.nan)
            H["n3_coef"] = H.n3_feature.map(lambda f: float(n3res.loc[f, "coef"]) if isinstance(f, str) else np.nan)
        H3.to_csv(OUT_H3, index=False)
        H3S.to_csv(OUT_H3S, index=False)
        r.note("")
        r.note("H3, team-level features on eleven seasons: champions n=%d vs top-5 non-champions n=%d; separates if <= %.0f%% of "
               "non-champions fall inside the champions' range" % (len(ch), len(nc), 100 * SEP_SHARE))
        for _, x in H3.iterrows():
            r.note("  %-52s [%s] champs %.2f..%.2f (median %.2f) non %.2f..%.2f (median %.2f), %2d of %2d inside %s"
                   % (x.label, "11" if x.seasons.startswith("eleven") else " 3", x.champ_lo, x.champ_hi, x.champ_median,
                      x.non_lo, x.non_hi, x.non_median, x.non_inside, x.n_non, "SEPARATES" if x.separates else ""))
        r.note("H3, style features on eleven seasons, for the record:")
        for _, x in H3S.iterrows():
            r.note("  %-52s champs %.2f..%.2f non %.2f..%.2f, %2d of %2d inside %s"
                   % (x.label, x.champ_lo, x.champ_hi, x.non_lo, x.non_hi, x.non_inside, x.n_non, "SEPARATES" if x.separates else ""))

        # ---- H5 ---------------------------------------------------------------------------
        mn = S[(S.team == "MIN") & (S.season == "2025-26")]
        if not len(mn):
            raise RuntimeError("Minnesota 2025-26 is not in the sample; run c1_contenders.py")
        mn = mn.iloc[0]
        mkt = pd.read_csv(os.path.join(OUT_DIR, "market_devig_2026_27.csv")).set_index("team_abbr")
        rot = pd.read_csv(os.path.join(OUT_DIR, "rotations_2026_27.csv"))
        cur27 = rot[(rot.scenario == "current") & (rot.team_abbr == "MIN") & (rot.mpg > 0)].copy()
        base26 = set(rot[(rot.scenario == "baseline") & (rot.team_abbr == "MIN")].player_id.dropna().astype(int))
        appeared26 = set(db.query("""select distinct s.player_id from nba.nba_player_stats s
                                     join nba.nba_games g on g.game_id = s.game_id and g.team_id = s.team_id
                                     where g.season_id = 22025 and g.team_abbreviation = 'MIN' and s.minutes_played > 0""").player_id.astype(int))
        cur27["pid"] = cur27.player_id.fillna(-1).astype(int)
        # by contract for 2026-27: with Minnesota at any point of 2025-26, so everyone who
        # appeared plus anyone carried on last season's roster without appearing
        base26 = base26 | appeared26
        cont27_contract = float(cur27[cur27.pid.isin(base26)].mpg.sum() / cur27.mpg.sum())
        cont27_appear = float(cur27[cur27.pid.isin(appeared26)].mpg.sum() / cur27.mpg.sum())
        top8_27 = cur27.sort_values("mpg", ascending=False).head(8)
        n8_contract = int(top8_27.pid.isin(base26).sum())
        n8_appear = int(top8_27.pid.isin(appeared26).sum())
        PRE = {"pre_implied": 100 * float(mkt.loc["MIN", "market_prop"]), "pre_rank": int(mkt.loc["MIN", "market_rank"]),
               "returning_share_contract": cont27_contract, "returning_share_appear": cont27_appear,
               "top8_returning_contract": n8_contract, "top8_returning_appear": n8_appear}
        r.note("")
        r.note("H5 2026-27 known now: market %.2f%% rank %d; continuity of the projected rotation by contract %.2f (top-8 %d of 8), "
               "by appearance %.2f (top-8 %d of 8)" % (PRE["pre_implied"], PRE["pre_rank"], cont27_contract, n8_contract,
                                                        cont27_appear, n8_appear))
        h5, routes = [], []
        for col, lab, good, scope in NUM:
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
                status = "outside, above" if val > row.champ_hi else "outside, below"
            else:
                better = (val > row.champ_hi) if good == "high" else (val < row.champ_lo)
                status = "outside, on the good side" if better else "outside, short of it"
            kind = "a season can close it" if col in CLOSABLE else "set by the roster or the market"
            h5.append(dict(feature=col, label=lab, seasons=row.seasons, minnesota=val, basis=when,
                           champ_lo=row.champ_lo, champ_hi=row.champ_hi, status=status, closable=kind,
                           separates=row.separates))
            if status == "outside, short of it" and col in CLOSABLE:
                thr = row.champ_hi if good == "low" else row.champ_lo
                routes.append(dict(feature=col, label=lab, minnesota_2025_26=val,
                                   champions_range="%.2f to %.2f" % (row.champ_lo, row.champ_hi),
                                   threshold=("%s %.0f or better" % (lab, thr)) if good == "low" else ("%s %.2f or better" % (lab, thr)),
                                   checkable="season end" if col in ("nrtg_rank", "ortg_rank", "drtg_rank", "seed")
                                   else ("after the All-Star break" if col == "post_asb_rank" else "the playoffs"),
                                   separates=row.separates))
        H5 = pd.DataFrame(h5)
        H5.to_csv(OUT_H5, index=False)
        R = pd.DataFrame(routes)
        R.to_csv(OUT_R, index=False)
        r.note("H5, Minnesota:")
        for _, x in H5.iterrows():
            r.note("  %-52s %8.2f (%s) champions %.2f..%.2f -> %s; %s"
                   % (x.label, x.minnesota, x.basis, x.champ_lo, x.champ_hi, x.status, x.closable))
        r.note("routed to N8: %s" % ("; ".join(R.threshold) if len(R) else "none"))
        for f in (OUT_SAMPLE, OUT_H1, OUT_H3, OUT_H3S, OUT_H5, OUT_R):
            r.output(f)
        write_doc(r, H1, H3, H3S, H5, R, pd.DataFrame(gate_rows), len(ch), len(nc), len(ch3), len(nc3), PRE)
        r.output(OUT_MD)


def write_doc(r, H1, H3, H3S, H5, R, G, n_ch, n_nc, n_ch3, n_nc3, PRE):
    L = ["# H1, H3, H5: the champion profile, and Minnesota on it\n",
         "*As of %s. Eleven seasons (2015-16 to 2025-26): %d champions against %d preseason top-five teams that did not win, "
         "every team built with the champions' own machinery (`c1_champions.build`). OBSERVED throughout, except Minnesota's "
         "2026-27 market price and rank and the continuity of its projected rotation. Run `%s`. Basketball-Reference pages "
         "cached in `kuminga/data/bref/` with their hashes in the manifest.*\n" % (AS_OF, n_ch, n_nc, r.run_id),
         "**Two sources for the net ratings.** B-Ref's NRtg against this warehouse's game-log net rating, season by season: "
         "correlation %s; mean absolute difference %s points; identical league rank for %s of teams.\n"
         % (", ".join("%.3f" % v for v in G["corr"]), ", ".join("%.2f" % v for v in G.mad),
            ", ".join("%.0f%%" % (100 * v) for v in G.rank_agree)),
         "**Continuity, two definitions.** By appearance: a player who appeared for the franchise in the previous regular season. "
         "By contract: a player whose stint with the franchise opened before the previous regular season ended, whether or not "
         "he played in it (Jamal Murray, Denver 2022-23, counts by contract only). Both are carried as a count of the top eight "
         "and as the share of playoff minutes.\n",
         "## H1. The champions\n",
         "| season | champion | preseason | net rating (rank) | offence / defence rank | post-All-Star rank | seed | "
         "playoff net (vs regular season) | best player (VORP) | top-8 age | returning of 8: appearance / contract | "
         "returning share: appearance / contract | top-8 games missed RS / playoffs | top-five share RS -> playoffs |",
         "|---|---|---|---|---|---:|---:|---|---|---:|---|---|---|---|"]
    for _, x in H1.iterrows():
        L.append("| %s | %s | %.2f%%, #%d | %+.1f (#%d) | #%d / #%d | %d | %d | %+.1f (%+.1f) | %s (%.1f) | %.1f | %d / %d | "
                 "%.0f%% / %.0f%% | %d / %d | %.0f%% -> %.0f%% |"
                 % (x.season, x.team, x.pre_implied, x.pre_rank, x.nrtg, x.nrtg_rank, x.ortg_rank, x.drtg_rank, x.post_asb_rank,
                    x.seed, x.net_po, x.po_minus_rs, x.best_player, x.best_vorp, x.top8_age, x.top8_returning_appear,
                    x.top8_returning_contract, 100 * x.returning_share_appear, 100 * x.returning_share_contract,
                    x.top8_rs_games_missed, x.top8_po_games_missed, 100 * x.top5_share_rs, 100 * x.top5_share_po))
    L.append("")
    L.append("## H3. Champions against the preseason top-five teams that did not win\n")
    L.append("Team-level features on all eleven seasons: n = %d champions against %d non-champions (every team priced in the top "
             "five, ties at fifth included). Style features on the three most recent seasons, labeled: n = %d against %d. A feature "
             "**separates** if no more than a quarter of the non-champions fall inside the champions' range (minimum to maximum). "
             "Ranges are descriptions, not rates.\n" % (n_ch, n_nc, n_ch3, n_nc3))
    L.append("| feature | seasons | champions: low / median / high | non-champions: low / median / high | non-champions inside "
             "the champions' range | separates | N3, 13 seasons |")
    L.append("|---|---|---|---|---|---|---|")
    for _, x in H3.iterrows():
        L.append("| %s | %s | %.2f / %.2f / %.2f | %.2f / %.2f / %.2f | %d of %d | %s | %s |"
                 % (x.label, x.seasons, x.champ_lo, x.champ_median, x.champ_hi, x.non_lo, x.non_median, x.non_hi,
                    x.non_inside, x.n_non, "**yes**" if x.separates else "no",
                    "" if not isinstance(x.n3_feature, str) else
                    ("translates" if x.n3_translates else "no signal (coef %+.2f)" % x.n3_coef)))
    L.append("")
    sep = H3[H3.separates]
    L.append("**What separates.** %s\n" % (
        ("On the team-level features, %s. On the style features (three seasons), %s." % (
            ", ".join(sep[sep.seasons.str.startswith("eleven")].label) or "nothing",
            ", ".join(sep[sep.seasons.str.startswith("three")].label) or "nothing"))))
    L.append("**The style features on all eleven seasons, for the record.**\n")
    L.append("| feature | champions: low / high | non-champions: low / high | inside | separates |")
    L.append("|---|---|---|---|---|")
    for _, x in H3S.iterrows():
        L.append("| %s | %.2f / %.2f | %.2f / %.2f | %d of %d | %s |"
                 % (x.label, x.champ_lo, x.champ_hi, x.non_lo, x.non_hi, x.non_inside, x.n_non, "**yes**" if x.separates else "no"))
    L.append("")
    L.append("## H5. Minnesota on the sheet\n")
    L.append("2026-27 values known now: market %.2f%%, rank %d; the projected rotation's continuity by contract %.2f "
             "(%d of the top eight) and by appearance %.2f (%d of the top eight).\n"
             % (PRE["pre_implied"], PRE["pre_rank"], PRE["returning_share_contract"], PRE["top8_returning_contract"],
                PRE["returning_share_appear"], PRE["top8_returning_appear"]))
    L.append("| feature | seasons | Minnesota | basis | champions' range | status | closable? |")
    L.append("|---|---|---:|---|---|---|---|")
    for _, x in H5.iterrows():
        L.append("| %s | %s | %.2f | %s | %.2f to %.2f | %s | %s |"
                 % (x.label, x.seasons, x.minnesota, x.basis, x.champ_lo, x.champ_hi, x.status, x.closable))
    L.append("")
    L.append("**Routed to the N8 watch list** (closable gaps, thresholds from the champions' ranges): %s\n"
             % ("; ".join("%s, checkable %s" % (x.threshold, x.checkable) for _, x in R.iterrows()) if len(R) else "none"))
    L.append("*Open columns.* Pre-playoff odds for these seasons are not fetched; nothing here was filled from an unverified "
             "odds table.\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
