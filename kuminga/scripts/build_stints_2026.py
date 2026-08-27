#!/usr/bin/env python3
"""Item 15, stage 1: rebuild the 2025-26 stint layer for the three teams the fit
section needs evidence from.

Compute budget is the binding constraint, so this is scoped to MIN (Randle+Gobert vs
Reid+Gobert), GSW and ATL (Kuminga on/off in both of his 2025-26 homes) rather than
the whole league. The derived possession/stint cache under counterfactual-fit-engine
covers only 2019-21 on this machine, so there is nothing to reuse for 2025-26.

Reuses postmortem/lib/lineup_aggregation, which runs the possession state machine and
derives per-lineup stints with garbage-time flags. Nothing new is modelled here.

    python kuminga/scripts/build_stints_2026.py
"""
from __future__ import annotations

import os
import sys
import time

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from lib import db                                    # noqa: E402
from lib.lineup_aggregation import process_games_to_stints  # noqa: E402
from kuminga.lib import runlog                        # noqa: E402

TEAMS = ("MIN", "GSW", "ATL")
OUT = os.path.join(REPO, "kuminga", "data", "stints_2025_26.parquet")
OUT_GAMES = os.path.join(REPO, "kuminga", "data", "stints_2025_26_games.csv")


def main():
    with runlog.run("build_stints_2026", inputs={"teams": list(TEAMS), "season": "2025-26"}) as r:
        games = db.query("""
            SELECT DISTINCT g.game_id, g.game_date, g.season_type
            FROM nba_games g
            WHERE g.game_date >= '2025-10-01'
              AND g.season_type IN ('Regular Season','Playoffs')
              AND g.game_id IN (SELECT game_id FROM nba_games
                                WHERE team_abbreviation = ANY(%s))
            ORDER BY g.game_date""", (list(TEAMS),))
        gids = games.game_id.tolist()
        r.note(f"{len(gids)} games involving {TEAMS} in 2025-26 "
               f"({(games.season_type=='Playoffs').sum()} playoff)")
        games.to_csv(OUT_GAMES, index=False)

        t0 = time.time()
        stints = process_games_to_stints(gids)
        el = time.time() - t0
        r.note(f"built {len(stints):,} stints in {el/60:.1f} min "
               f"({el/max(len(gids),1):.2f}s/game)")

        stints.to_parquet(OUT, index=False)
        r.note(f"teams present: {stints.team_id.nunique()}")
        r.note(f"garbage-time stints: {int(stints.in_garbage_time.sum()):,} "
               f"of {len(stints):,}")
        r.output(OUT, rows=len(stints))
        r.output(OUT_GAMES, rows=len(games))


if __name__ == "__main__":
    main()
