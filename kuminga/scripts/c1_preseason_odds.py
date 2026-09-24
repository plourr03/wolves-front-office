#!/usr/bin/env python3
"""C1 odds: the preseason title odds for every champion season, 2015-16 to 2025-26.

WHAT THIS FILLS. The champions table (`champions_table.py`) and the C1 champion rows
(`c1_champions.py`) read one file per season from `offseason/data/{season}-preseason-odd.csv`.
Three of those files (2023-24 to 2025-26) were hand-transcribed. This script builds the
eight older ones from Basketball-Reference's preseason odds page for each season
(`/leagues/NBA_{year}_preseason_odds.html`, published courtesy of sportsoddshistory.com),
fetched once through `kuminga.lib.bref` so the page is cached with its sha256 in
`data/bref/manifest.json`.

GATES, each fatal.
  1. every page parses to exactly 30 teams, no duplicate, no missing odds;
  2. the season's champion (hard-coded below, the same list `c1_champions.py` cross-checks
     against the Basketball-Reference season page) is on the page;
  3. for the three hand-transcribed seasons the page is compared with the existing file,
     team by team, and must match on odds and win total; those files are NOT rewritten.

OUTPUT. The eight new odds files, in the existing files' format (Team, Odds with sign,
blank, W-L O/U, Result), and `kuminga/data/preseason_odds_sources.csv`: one row per season
with the URL, the sha256 of the cached page, the fetch time, the team count, the champion,
its odds and its raw rank. As-of is the fetch time in the manifest.

    python kuminga/scripts/c1_preseason_odds.py
"""
from __future__ import annotations

import io
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import bref, runlog  # noqa: E402

ODDS_DIR = os.path.join(REPO, "offseason", "data")
OUT = os.path.join(REPO, "kuminga", "data", "preseason_odds_sources.csv")

CHAMPIONS = {
    2016: "Cleveland Cavaliers", 2017: "Golden State Warriors", 2018: "Golden State Warriors",
    2019: "Toronto Raptors", 2020: "Los Angeles Lakers", 2021: "Milwaukee Bucks",
    2022: "Golden State Warriors", 2023: "Denver Nuggets", 2024: "Boston Celtics",
    2025: "Oklahoma City Thunder", 2026: "New York Knicks",
}
HAND_TRANSCRIBED = {"2023-24", "2024-25", "2025-26"}


def season_of(year):
    return "%d-%s" % (year - 1, str(year)[2:])


def fmt_odds(v):
    v = int(v)
    return "%+d" % v


def main():
    with runlog.run("c1_preseason_odds", inputs={"years": sorted(CHAMPIONS)}) as r:
        man = bref.manifest()
        rows = []
        for year, champ in sorted(CHAMPIONS.items()):
            season = season_of(year)
            path = "/leagues/NBA_%d_preseason_odds.html" % year
            html = bref.fetch(path)
            key = bref.key_of(path)
            d = pd.read_html(io.StringIO(html))[0]
            d = d[["Team", "Odds", "W-L O/U", "Result"]].copy()
            if len(d) != 30 or d.Team.duplicated().any() or d.Odds.isna().any():
                raise RuntimeError("%s: page parsed %d teams, %d duplicates, %d missing odds"
                                   % (season, len(d), int(d.Team.duplicated().sum()), int(d.Odds.isna().sum())))
            if champ not in set(d.Team):
                raise RuntimeError("%s: champion %s not on the page" % (season, champ))
            d["Odds"] = d.Odds.astype(int)
            d = d.sort_values(["Odds"], key=lambda s: s.map(lambda o: 100.0 / (o + 100.0) if o > 0 else (-o) / (-o + 100.0)),
                              ascending=False).reset_index(drop=True)
            c = d[d.Team == champ].iloc[0]
            rank_raw = int(d.index[d.Team == champ][0]) + 1
            out = pd.DataFrame({"Team": d.Team, "Odds": d.Odds.map(fmt_odds), "": "",
                                "W-L O/U": d["W-L O/U"], "Result": d.Result})
            f = os.path.join(ODDS_DIR, "%s-preseason-odd.csv" % season)
            if season in HAND_TRANSCRIBED:
                e = pd.read_csv(f)
                m = e.merge(d, on="Team", how="outer", suffixes=("_file", "_bref"))
                if len(m) != 30 or m.Odds_file.isna().any() or m.Odds_bref.isna().any():
                    raise RuntimeError("%s: team names differ between the file and the page" % season)
                bad = m[(m.Odds_file.astype(str).str.replace("+", "", regex=False).astype(float) != m.Odds_bref.astype(float))
                        | (m["W-L O/U_file"].astype(float) != m["W-L O/U_bref"].astype(float))]
                if len(bad):
                    raise RuntimeError("%s: hand-transcribed file disagrees with the page on %d teams: %s"
                                       % (season, len(bad), ", ".join(bad.Team)))
                status = "hand-transcribed file kept; matches the page on all 30 teams"
            else:
                out.to_csv(f, index=False)
                status = "written from the page"
            r.note("%s  %-22s %+6d  raw rank %2d  | favourite %-22s %+6d | %s"
                   % (season, champ, int(c.Odds), rank_raw, d.iloc[0].Team, int(d.iloc[0].Odds), status))
            rows.append(dict(season=season, url=bref.BASE + path, cache_key=key, sha256=man[key]["sha256"],
                             fetched_at=man[key].get("fetched_at", ""), n_teams=len(d), champion=champ,
                             champion_odds=int(c.Odds), champion_rank_raw=rank_raw,
                             favorite=d.iloc[0].Team, favorite_odds=int(d.iloc[0].Odds), file=os.path.relpath(f, REPO),
                             status=status, credit="Basketball-Reference, courtesy sportsoddshistory.com"))
            man = bref.manifest()
        src = pd.DataFrame(rows)
        src.to_csv(OUT, index=False)
        r.output(OUT, rows=len(src))
        for f in sorted(os.listdir(ODDS_DIR)):
            if f.endswith("-preseason-odd.csv"):
                r.output(os.path.join(ODDS_DIR, f), rows=30)
    print(src[["season", "champion", "champion_odds", "champion_rank_raw", "favorite", "favorite_odds", "status"]].to_string(index=False))


if __name__ == "__main__":
    main()
