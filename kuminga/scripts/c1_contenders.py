#!/usr/bin/env python3
"""C1 contenders: the champions-table row for every preseason top-five team that did not win.

For each of the eleven seasons 2015-16 to 2025-26, every team the preseason title odds had
in the top five (proportional de-vig, tied prices sharing a rank, ties at fifth included)
that did not win the title, built with exactly the champions' machinery, `c1_champions.build`:
the top eight by playoff minutes (by regular-season minutes for a team that did not make the
playoffs), how each was acquired from his Basketball-Reference transaction log, age,
continuity by appearance and by contract, net-rating ranks, the All-Star split, seed, games
missed, the top five's minute shares. Minnesota 2025-26 is built the same way for H5.

SOURCES. The odds files `offseason/data/{season}-preseason-odd.csv` for the sample; the
warehouse and the Basketball-Reference cache for the rows (see `c1_champions.py`).

OUTPUT. `outputs/c1_contenders.csv` (one row per team-season, `group` = "top-5 non-champion"
or "minnesota") and `outputs/c1_contender_top8.csv` (the eight players per team).

    python kuminga/scripts/c1_contenders.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "postmortem"))
sys.path.insert(0, os.path.join(REPO, "offseason", "scripts"))

from kuminga.lib import runlog  # noqa: E402
from lib import db              # noqa: E402
import bracket_sim as E         # noqa: E402
import c1_champions as C1       # noqa: E402

ODDS_DIR = os.path.join(REPO, "offseason", "data")
OUT_DIR = os.path.join(REPO, "kuminga", "outputs")
YEARS = list(range(2016, 2027))
EXTRA = {2026: ["MIN"]}          # built for H5, flagged "minnesota"


def top_five(year):
    season = "%d-%s" % (year - 1, str(year)[2:])
    d = pd.read_csv(os.path.join(ODDS_DIR, "%s-preseason-odd.csv" % season))
    d["p_raw"] = d.Odds.map(lambda o: 100.0 / (float(o) + 100.0) if float(o) > 0 else -float(o) / (-float(o) + 100.0))
    d["p"] = d.p_raw / d.p_raw.sum()
    d["rank"] = d.p.rank(ascending=False, method="min").astype(int)
    d["abbr"] = d.Team.map(E.NAME_TO_ABBR)
    if d.abbr.isna().any() or len(d) != 30:
        raise RuntimeError("%s: odds file has %d teams, %d unmapped names" % (season, len(d), int(d.abbr.isna().sum())))
    return d[d["rank"] <= 5].sort_values("p", ascending=False)


def team_ids(year):
    sid = 20000 + year - 1
    d = db.query("select distinct team_id, team_abbreviation from nba.nba_games where season_id = %(s)s", {"s": sid})
    return {str(x.team_abbreviation): int(x.team_id) for _, x in d.iterrows()}


def main():
    champs = pd.read_csv(os.path.join(OUT_DIR, "c1_champions.csv")).set_index("season").team
    with runlog.run("c1_contenders", inputs={"years": YEARS, "extra": EXTRA}) as r:
        rows, tops = [], []
        for y in YEARS:
            season = "%d-%s" % (y - 1, str(y)[2:])
            ids = team_ids(y)
            t5 = top_five(y)
            teams = [(a, "top-5 non-champion") for a in t5.abbr if a != champs[season]]
            teams += [(a, "minnesota") for a in EXTRA.get(y, []) if a not in [t for t, _ in teams] and a != champs[season]]
            for abbr, group in teams:
                row, P = C1.build(y, r, team=(ids[abbr], abbr))
                row["group"] = group
                row.update(C1.preseason_odds(y, abbr))
                rows.append(row)
                P["group"] = group
                tops.append(P)
                r.note("%s %s (%s): seed %s, RS net %+.2f (%d), post-ASB %+.2f (%d), PO %s; returning %d/%d (appearance/contract), "
                       "missed %d/%d, top-5 %.0f%%->%s; pre %s" % (
                           season, abbr, group, row["seed_bref"], row["net_rs"], row["net_rs_rank"], row["net_post_asb"],
                           row["net_post_asb_rank"], ("%+.2f" % row["net_po"]) if row["made_playoffs"] else "no playoffs",
                           row["top8_returning"], row["top8_returning_contract"], row["top8_rs_games_missed"],
                           row["top8_po_games_missed"], 100 * row["top5_share_rs"],
                           ("%.0f%%" % (100 * row["top5_share_po"])) if row["made_playoffs"] else "n/a",
                           row["preseason_title_odds"]))
        R = pd.DataFrame(rows)
        P = pd.concat(tops, ignore_index=True)
        p_r = os.path.join(OUT_DIR, "c1_contenders.csv")
        p_p = os.path.join(OUT_DIR, "c1_contender_top8.csv")
        R.to_csv(p_r, index=False)
        P.to_csv(p_p, index=False)
        unk = P[P.acq_type == "unknown"]
        r.note("acquisition unresolved for %d of %d top-eight players%s" % (
            len(unk), len(P), (": " + "; ".join("%s %s %s" % (x.season, x.team, x.player) for _, x in unk.iterrows())) if len(unk) else ""))
        r.note("%d team-seasons: %d top-5 non-champions, %d extra" % (len(R), int((R.group == "top-5 non-champion").sum()),
                                                                       int((R.group != "top-5 non-champion").sum())))
        r.output(p_r, rows=len(R))
        r.output(p_p, rows=len(P))


if __name__ == "__main__":
    main()
