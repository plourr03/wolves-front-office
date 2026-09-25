#!/usr/bin/env python3
"""The base rate for a mover's minutes: what share of his prior per-appearance load does a
low-impact, well-used player on a bad team keep when he changes teams?

WHY. The rotation model orders players by a 50/50 blend of last season's minutes per
appearance and impact, so Cody Williams, who played 24.3 a night for a bottom-ten Utah
team at the lowest impact on Minnesota's roster, is handed a real role on a contender.
The W1 rule discounts a mover's own prior load in the MINUTES blend, but the question
underneath it is empirical: what do players like him actually keep?

THE COHORT, stated before the run. Every player who, in season t-1:
  - had a bottom-quartile impact rating (Basketball-Reference BPM at or below the 25th
    percentile of players with at least MIN_PRIOR_MP minutes that season),
  - averaged at least 18 minutes per appearance for his main team (the team he played the
    most minutes for), and
  - whose main team finished in the bottom ten of the league by wins,
and who, in season t, played his most minutes for a DIFFERENT team. Destination seasons
t are 2023-24, 2024-25 and 2025-26, so prior seasons are 2022-23 to 2024-25.

THE OUTCOME. Retention = minutes per appearance on the new main team in t, divided by
minutes per appearance on the prior main team in t-1. A qualifying player with no NBA
minutes in t is reported separately (he kept nothing, but he is not a "mover").

SOURCES. Basketball-Reference league advanced pages (per player-team row: games, minutes,
BPM, with the player slug as the key) and the league page team table (wins and losses),
all from the html cache with hashes in the manifest.

OUTPUT. `outputs/mover_minutes_cohort.csv` (one row per qualifying mover) and
`outputs/mover_minutes_base_rate.csv` (the summary: n, median and quartiles of retention,
and the same conditioned on the new team's win percentage).

    python kuminga/scripts/mover_minutes_base_rate.py
"""
from __future__ import annotations

import io
import os
import sys

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import bref, runlog  # noqa: E402

OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
OUT_COHORT = os.path.join(OUT_DIR, "mover_minutes_cohort.csv")
OUT_BASE = os.path.join(OUT_DIR, "mover_minutes_base_rate.csv")

DEST_YEARS = [2024, 2025, 2026]     # season t, B-Ref year (2024 = 2023-24)
MIN_PRIOR_MP = 500                  # minutes in t-1 to be in the impact-percentile pool
MIN_PRIOR_MPG = 18.0
BOTTOM_TEN_RANK = 21                # wins rank 21 to 30 of 30
IMPACT_QUANTILE = 0.25


def players(year):
    """Per player-team rows for a season: slug, player, team, games, minutes, BPM."""
    html = bref.strip_comments(bref.fetch("/leagues/NBA_%d_advanced.html" % year))
    soup = BeautifulSoup(html, "lxml")
    tab = soup.find("table", id="advanced")
    rows = []
    for tr in tab.tbody.find_all("tr"):
        if tr.get("class") and "thead" in tr.get("class"):
            continue
        td = {c.get("data-stat"): c for c in tr.find_all(["td", "th"])}
        nm = td.get("name_display") or td.get("player")
        if nm is None:
            continue
        a = nm.find("a")
        team = (td.get("team_name_abbr") or td.get("team_id"))
        rows.append(dict(slug=a["href"] if a else nm.get_text(strip=True), player=nm.get_text(strip=True),
                         team=team.get_text(strip=True) if team else "", g=td["games"].get_text(strip=True),
                         mp=td["mp"].get_text(strip=True), bpm=td["bpm"].get_text(strip=True)))
    d = pd.DataFrame(rows)
    for c in ("g", "mp", "bpm"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[d.player != "League Average"].copy()
    d["multi"] = d.team.str.match(r"^\dTM$|^TOT$")
    return d


def team_wins(year):
    html = bref.strip_comments(bref.fetch("/leagues/NBA_%d.html" % year))
    t = pd.read_html(io.StringIO(html), attrs={"id": "advanced-team"})[0]
    t.columns = [c[1] if not str(c[1]).startswith("Unnamed") else c[0] for c in t.columns]
    t = t[t.Team.notna()].copy()
    t["Team"] = t.Team.astype(str).str.replace("*", "", regex=False).str.strip()
    t = t[t.Team != "League Average"]
    t["W"] = pd.to_numeric(t.W, errors="coerce")
    t["L"] = pd.to_numeric(t.L, errors="coerce")
    t["win_pct"] = t.W / (t.W + t.L)
    t["wins_rank"] = t.W.rank(ascending=False, method="min").astype(int)
    # abbreviations: from the season's advanced player table team codes matched by name is
    # not available here, so map full names to B-Ref codes through the roster links
    soup = BeautifulSoup(html, "lxml")
    codes = {}
    for a in soup.select("table#advanced-team a[href^='/teams/']"):
        codes[a.get_text(strip=True)] = a["href"].split("/")[2]
    t["code"] = t.Team.map(codes)
    if t.code.isna().any() or len(t) != 30:
        raise RuntimeError("team table for %d: %d teams, %d without a code" % (year, len(t), int(t.code.isna().sum())))
    return t.set_index("code")[["Team", "W", "L", "win_pct", "wins_rank"]]


def season_frame(year):
    """One row per player: season BPM (the totals row where he had several teams), his
    main team (most minutes), minutes per appearance on that team, and the team's record."""
    d = players(year)
    tw = team_wins(year)
    per_team = d[~d.multi].copy()
    tot = d[d.multi].set_index("slug")
    out = []
    for slug, g in per_team.groupby("slug"):
        main = g.sort_values("mp", ascending=False).iloc[0]
        season_bpm = float(tot.loc[slug, "bpm"]) if slug in tot.index else float(main.bpm)
        season_mp = float(tot.loc[slug, "mp"]) if slug in tot.index else float(g.mp.sum())
        out.append(dict(slug=slug, player=main.player, team=main.team, g=int(main.g), mp=float(main.mp),
                        mpg=float(main.mp) / max(1, int(main.g)), season_mp=season_mp, season_bpm=season_bpm,
                        n_teams=len(g), team_win_pct=float(tw.loc[main.team, "win_pct"]) if main.team in tw.index else np.nan,
                        team_wins_rank=int(tw.loc[main.team, "wins_rank"]) if main.team in tw.index else -1))
    return pd.DataFrame(out)


def main():
    with runlog.run("mover_minutes_base_rate", inputs={"dest_years": DEST_YEARS, "min_prior_mp": MIN_PRIOR_MP,
                                                        "min_prior_mpg": MIN_PRIOR_MPG, "bottom_ten_rank": BOTTOM_TEN_RANK,
                                                        "impact_quantile": IMPACT_QUANTILE}) as r:
        frames = {y: season_frame(y) for y in range(min(DEST_YEARS) - 1, max(DEST_YEARS) + 1)}
        cohort = []
        for y in DEST_YEARS:
            prev, cur = frames[y - 1], frames[y]
            pool = prev[prev.season_mp >= MIN_PRIOR_MP]
            cut = float(pool.season_bpm.quantile(IMPACT_QUANTILE))
            q = prev[(prev.season_mp >= MIN_PRIOR_MP) & (prev.season_bpm <= cut) & (prev.mpg >= MIN_PRIOR_MPG)
                     & (prev.team_wins_rank >= BOTTOM_TEN_RANK)]
            r.note("%d-%s: impact pool %d players (>= %d minutes), bottom-quartile cut BPM %.2f; %d qualify on impact, "
                   "load and a bottom-ten team" % (y - 2, str(y - 1)[2:], len(pool), MIN_PRIOR_MP, cut, len(q)))
            cur_i = cur.set_index("slug")
            for _, x in q.iterrows():
                if x.slug in cur_i.index:
                    c = cur_i.loc[x.slug]
                    moved = c.team != x.team
                    if not moved:
                        continue
                    cohort.append(dict(dest_season="%d-%s" % (y - 1, str(y)[2:]), slug=x.slug, player=x.player,
                                       prior_team=x.team, prior_mpg=x.mpg, prior_g=x.g, prior_bpm=x.season_bpm,
                                       prior_team_win_pct=x.team_win_pct, prior_team_wins_rank=x.team_wins_rank,
                                       new_team=c.team, new_mpg=float(c.mpg), new_g=int(c.g), new_team_win_pct=float(c.team_win_pct),
                                       new_team_wins_rank=int(c.team_wins_rank), retention=float(c.mpg) / float(x.mpg), played=True))
                else:
                    cohort.append(dict(dest_season="%d-%s" % (y - 1, str(y)[2:]), slug=x.slug, player=x.player,
                                       prior_team=x.team, prior_mpg=x.mpg, prior_g=x.g, prior_bpm=x.season_bpm,
                                       prior_team_win_pct=x.team_win_pct, prior_team_wins_rank=x.team_wins_rank,
                                       new_team="", new_mpg=0.0, new_g=0, new_team_win_pct=np.nan, new_team_wins_rank=-1,
                                       retention=0.0, played=False))
        C = pd.DataFrame(cohort).sort_values(["dest_season", "retention"], ascending=[True, False])
        C.to_csv(OUT_COHORT, index=False)
        M = C[C.played]
        rows = []

        def summarise(label, d):
            rows.append(dict(group=label, n=len(d), median=float(d.retention.median()) if len(d) else np.nan,
                             q25=float(d.retention.quantile(0.25)) if len(d) else np.nan,
                             q75=float(d.retention.quantile(0.75)) if len(d) else np.nan,
                             share_kept_all=float((d.retention >= 1).mean()) if len(d) else np.nan,
                             median_prior_mpg=float(d.prior_mpg.median()) if len(d) else np.nan,
                             median_new_mpg=float(d.new_mpg.median()) if len(d) else np.nan))
            r.note("  %-46s n=%3d  retention median %.2f (IQR %.2f to %.2f), kept it all %.0f%%, prior %.1f -> new %.1f a night"
                   % (label, len(d), rows[-1]["median"], rows[-1]["q25"], rows[-1]["q75"], 100 * rows[-1]["share_kept_all"],
                      rows[-1]["median_prior_mpg"], rows[-1]["median_new_mpg"]))

        r.note("THE BASE RATE, movers who played in season t:")
        summarise("all movers", M)
        for s, d in M.groupby("dest_season"):
            summarise("  " + s, d)
        summarise("new team top ten by wins", M[M.new_team_wins_rank <= 10])
        summarise("new team middle ten", M[(M.new_team_wins_rank > 10) & (M.new_team_wins_rank <= 20)])
        summarise("new team bottom ten", M[M.new_team_wins_rank > 20])
        summarise("new team at or above .600", M[M.new_team_win_pct >= 0.6])
        summarise("new team under .500", M[M.new_team_win_pct < 0.5])
        r.note("qualifying players with no NBA minutes in season t (not movers): %d of %d" % (int((~C.played).sum()), len(C)))
        B = pd.DataFrame(rows)
        B.to_csv(OUT_BASE, index=False)
        r.output(OUT_COHORT, rows=len(C))
        r.output(OUT_BASE, rows=len(B))
    print(B.to_string(index=False))


if __name__ == "__main__":
    main()
