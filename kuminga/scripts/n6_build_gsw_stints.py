#!/usr/bin/env python3
"""N6, stage 1: Golden State stint layer for 2022-23 to 2024-25, Kuminga's main GSW years.

The 2025-26 stint file already covers GSW (and ATL, after the February trade). The GSW
analog in the ledger (Kuminga's units next to non-shooting centres) needs the earlier
seasons too, so this runs the same shared pipeline (`postmortem/lib/lineup_aggregation`,
which normalises both play-by-play formats) on every Golden State regular-season and
playoff game of those three seasons. Nothing is modelled here.

    python kuminga/scripts/n6_build_gsw_stints.py
"""
from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from lib import db                                           # noqa: E402
from lib.lineup_aggregation import process_games_to_stints  # noqa: E402
from kuminga.lib import runlog                               # noqa: E402

OUT = os.path.join(REPO, "kuminga", "data", "stints_gsw_2022_25.parquet")
OUT_GAMES = os.path.join(REPO, "kuminga", "data", "stints_gsw_2022_25_games.csv")


def main():
    with runlog.run("n6_build_gsw_stints", inputs={"team": "GSW",
                                                   "seasons": ["2022-23", "2024-25"]}) as r:
        games = db.query("""
            SELECT DISTINCT g.game_id, g.game_date, g.season_type
            FROM nba_games g
            WHERE g.season_id IN (22022, 22023, 22024, 42022, 42023, 42024)
              AND g.team_abbreviation = 'GSW'
            ORDER BY g.game_date""")
        gids = games.game_id.tolist()
        r.note("%d GSW games 2022-23 to 2024-25 (%d playoff)"
               % (len(gids), int((games.season_type == "Playoffs").sum())))
        games.to_csv(OUT_GAMES, index=False)
        t0 = time.time()
        stints = process_games_to_stints(gids)
        r.note("built %s stints in %.1f min" % ("{:,}".format(len(stints)),
                                                (time.time() - t0) / 60))
        stints.to_parquet(OUT, index=False)
        r.output(OUT, rows=len(stints))
        r.output(OUT_GAMES, rows=len(games))


if __name__ == "__main__":
    main()
