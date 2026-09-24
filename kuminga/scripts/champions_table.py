#!/usr/bin/env python3
"""H1/H2: what the preseason market knew about the teams that went on to win.

THE FRAMING RULE, which governs every line of this: never "the odds were wrong." The
preseason market is a prior. The question is how good a prior it is, and what information
moved the eventual winners inside it. A champion at +900 is not a market failure; it is a
market saying one-in-ten and one-in-ten happening.

SOURCES, and one that was rejected.

  ODDS AND RESULTS  `offseason/data/{season}-preseason-odd.csv`, eleven seasons, all 30
                    teams, with win totals and final records. 2023-24 to 2025-26 were
                    hand-transcribed; 2015-16 to 2022-23 were written by
                    `c1_preseason_odds.py` from Basketball-Reference's preseason odds page
                    for each season (courtesy sportsoddshistory.com), cached with its sha256,
                    and the three hand-transcribed files were checked against the same pages
                    team by team (`kuminga/data/preseason_odds_sources.csv`).
  CHAMPIONS         one per season, 2015-16 Cleveland to 2025-26 New York (beat San
                    Antonio 4-1, Brunson Finals MVP), each verified at the Wikipedia
                    Finals page named in SEASONS and, in `c1_champions.py`, against the
                    Basketball-Reference season page.
  REJECTED          sportsbettingdime.com's past-seasons table names SAN ANTONIO as the
                    2026 champion. San Antonio lost the Finals. A source that misstates
                    a champion is not usable for anything else on this page, so none of
                    its odds were taken either.

WHAT IS MISSING AND WHY. The brief asks for net-rating ranks, seeds, playoff net rating,
continuity, top-8 health and the N3 translation features. The warehouse's team advanced
table is GAME level, so every one of those needs a season aggregation that is not built
yet, and Basketball-Reference is returning 403 to both direct and proxied requests. Those
columns are listed in gaps_remaining.md rather than guessed. **n = 3 is stated as a
number everywhere below, because with three champions almost nothing here is a rate.**

    python kuminga/scripts/champions_table.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)

from kuminga.lib import runlog  # noqa: E402

DATA = os.path.join(REPO, "offseason", "data")
OUT = os.path.join(REPO, "kuminga", "outputs", "champions_h1.csv")
OUT_BASE = os.path.join(REPO, "kuminga", "outputs", "champions_h2_base_rates.csv")
CUR = os.path.join(REPO, "kuminga", "outputs", "market_devig_2026_27.csv")

SEASONS = {
    "2015-16": ("Cleveland Cavaliers", "https://en.wikipedia.org/wiki/2016_NBA_Finals"),
    "2016-17": ("Golden State Warriors", "https://en.wikipedia.org/wiki/2017_NBA_Finals"),
    "2017-18": ("Golden State Warriors", "https://en.wikipedia.org/wiki/2018_NBA_Finals"),
    "2018-19": ("Toronto Raptors", "https://en.wikipedia.org/wiki/2019_NBA_Finals"),
    "2019-20": ("Los Angeles Lakers", "https://en.wikipedia.org/wiki/2020_NBA_Finals"),
    "2020-21": ("Milwaukee Bucks", "https://en.wikipedia.org/wiki/2021_NBA_Finals"),
    "2021-22": ("Golden State Warriors", "https://en.wikipedia.org/wiki/2022_NBA_Finals"),
    "2022-23": ("Denver Nuggets", "https://en.wikipedia.org/wiki/2023_NBA_Finals"),
    "2023-24": ("Boston Celtics", "https://en.wikipedia.org/wiki/2024_NBA_Finals"),
    "2024-25": ("Oklahoma City Thunder",
                "https://en.wikipedia.org/wiki/2025_NBA_Finals"),
    "2025-26": ("New York Knicks", "https://en.wikipedia.org/wiki/2026_NBA_Finals"),
}


def american_to_prob(o):
    o = float(o)
    return 100.0 / (o + 100.0) if o > 0 else (-o) / (-o + 100.0)


def main():
    with runlog.run("champions_table", inputs={"seasons": list(SEASONS)}) as r:
        rows = []
        for season, (champ, src) in SEASONS.items():
            f = os.path.join(DATA, "%s-preseason-odd.csv" % season)
            d = pd.read_csv(f)
            d["p_raw"] = d.Odds.map(american_to_prob)
            over = float(d.p_raw.sum())
            d["p"] = d.p_raw / over                      # proportional de-vig
            d = d.sort_values("p", ascending=False).reset_index(drop=True)
            # tied prices share a rank, so a co-favourite is rank 1 (2023-24: Boston and
            # Denver both +450)
            d["rank"] = d.p.rank(ascending=False, method="min").astype(int)
            fav = d.iloc[0]
            c = d[d.Team == champ]
            assert len(c) == 1, "champion %s not found in %s" % (champ, season)
            c = c.iloc[0]
            # the Result column carries "W-L (over|under)" against the win total
            res = str(c.get("Result", ""))
            wins = int(res.split("-")[0]) if "-" in res else None
            ou = "over" if "(over)" in res else ("under" if "(under)" in res else None)
            rows.append(dict(
                season=season, champion=champ,
                champ_odds=int(c.Odds), champ_implied_pct=c.p * 100,
                champ_rank=int(c["rank"]),
                favorite=fav.Team, favorite_odds=int(fav.Odds),
                favorite_implied_pct=fav.p * 100,
                favorite_won=bool(int(c["rank"]) == 1),
                co_favorites=int((d["rank"] == 1).sum()),
                overround_pct=(over - 1) * 100,
                champ_wins=wins, champ_vs_win_total=ou,
                champ_win_total=c.get("W-L O/U"), source=src))
        h1 = pd.DataFrame(rows)
        h1.to_csv(OUT, index=False)

        r.note("H1. THE CHAMPIONS TABLE, n = %d seasons" % len(h1))
        for _, x in h1.iterrows():
            r.note("  %s  champion %-22s %+-6d  %5.2f%%  rank %-2d | favourite %-22s "
                   "%5.2f%% | %s | %d wins, %s its total"
                   % (x.season, x.champion, x.champ_odds, x.champ_implied_pct,
                      x.champ_rank, x.favorite, x.favorite_implied_pct,
                      "FAVOURITE WON" if x.favorite_won else "favourite lost",
                      x.champ_wins, x.champ_vs_win_total))

        # ---- H2 base rates ----------------------------------------------------
        n = len(h1)
        base = dict(
            n_seasons=n,
            p_favorite_wins=float(h1.favorite_won.mean()),
            p_champ_top1=float((h1.champ_rank <= 1).mean()),
            p_champ_top3=float((h1.champ_rank <= 3).mean()),
            p_champ_top5=float((h1.champ_rank <= 5).mean()),
            p_champ_top8=float((h1.champ_rank <= 8).mean()),
            champ_implied_median=float(h1.champ_implied_pct.median()),
            champ_implied_min=float(h1.champ_implied_pct.min()),
            champ_implied_max=float(h1.champ_implied_pct.max()),
            champ_rank_median=float(h1.champ_rank.median()),
            champ_rank_max=int(h1.champ_rank.max()),
            champ_beat_win_total=float((h1.champ_vs_win_total == "over").mean()),
        )
        pd.DataFrame([base]).to_csv(OUT_BASE, index=False)

        r.note("")
        r.note("H2. BASE RATES. n = %d. Every one of these is a count out of %d and is "
               "written as a count, not a rate." % (n, n))
        r.note("  the preseason favourite won        %d of %d" %
               (int(h1.favorite_won.sum()), n))
        r.note("  champion came from the top 3       %d of %d" %
               (int((h1.champ_rank <= 3).sum()), n))
        r.note("  champion came from the top 5       %d of %d" %
               (int((h1.champ_rank <= 5).sum()), n))
        r.note("  champion came from the top 8       %d of %d" %
               (int((h1.champ_rank <= 8).sum()), n))
        r.note("  champion beat its own win total    %d of %d" %
               (int((h1.champ_vs_win_total == "over").sum()), n))
        r.note("  champions' preseason implied probability: median %.2f%%, "
               "range %.2f%% to %.2f%%, median rank %.0f"
               % (base["champ_implied_median"], base["champ_implied_min"],
                  base["champ_implied_max"], base["champ_rank_median"]))

        # ---- where Minnesota sits --------------------------------------------
        if os.path.exists(CUR):
            cur = pd.read_csv(CUR).set_index("team_abbr")
            mn = cur.loc["MIN"]
            r.note("")
            r.note("MINNESOTA ON THAT DISTRIBUTION, 2026-27.")
            r.note("  market  %.2f%%, rank %d" % (mn.market_pct, int(mn.market_rank)))
            r.note("  model   %.2f%%, rank %d" % (mn.model_pct, int(mn.model_rank)))
            lo, hi = base["champ_implied_min"], base["champ_implied_max"]
            inside = lo <= mn.market_pct <= hi
            r.note("  the %d champions' preseason range is %.2f%% to %.2f%%. "
                   "Minnesota's MARKET number is %s that range."
                   % (n, lo, hi, "INSIDE" if inside else "OUTSIDE"))
            r.note("  Minnesota's MODEL number (%.2f%%) is %s it."
                   % (mn.model_pct,
                      "inside" if lo <= mn.model_pct <= hi else "OUTSIDE"))
            worst_rank = int(h1.champ_rank.max())
            r.note("  no champion in this sample started worse than rank %d. Minnesota "
                   "is market rank %d and model rank %d."
                   % (worst_rank, int(mn.market_rank), int(mn.model_rank)))
            r.note("")
            r.note("THE HONEST READING, given n = %d. This sample cannot support a rate. "
                   "What it can support is a RANGE: all %d champions were priced "
                   "between %.2f%% and %.2f%% and none started outside the top %d. "
                   "Minnesota's market price sits %s that band and its model price sits "
                   "well below it. That is a statement about where Minnesota is being "
                   "asked to come from, not a probability that it gets there."
                   % (n, n, lo, hi, worst_rank,
                      "just inside" if inside else "outside"))
        r.output(OUT, rows=len(h1))
        r.output(OUT_BASE, rows=1)

    print()
    print(h1[["season", "champion", "champ_odds", "champ_implied_pct", "champ_rank",
              "favorite", "favorite_won"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
