#!/usr/bin/env python3
"""Freeze one warehouse snapshot for the whole Kuminga build.

The warehouse refreshes every morning at 03:33. This build spans a night and several
slow steps, so a refresh landing mid-run would silently put early and late steps on
different data. Everything the project needs is pulled ONCE into a content-addressed
snapshot under kuminga/data/frozen/, and every downstream script reads through
kfreeze.load(), which re-hashes and asserts.

The production warehouse is READ-ONLY here. This only SELECTs.

    python kuminga/scripts/freeze_inputs.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "postmortem"))

from lib import db                       # noqa: E402
from kuminga.lib import kfreeze, runlog  # noqa: E402

# The 2025-26 season, which is the last completed one and the basis for both the
# R6 baseline and the minutes heuristic.
SEASON = "2025-26"


def pull():
    t = {}

    # Full contract book, all teams, all seasons. The live cap spine.
    t["contracts"] = db.query("""
        SELECT br_player_id, team_abbr, season, player_name, nba_team_id,
               nba_team_tricode, season_order, salary, option_type,
               remaining_guaranteed_total, source_url, scraped_at
        FROM nba_player_contracts""")

    # Every transaction the league has published. group_sort ties trade legs together.
    t["transactions"] = db.query("""
        SELECT transaction_hash, transaction_type, transaction_date,
               transaction_description, team_id, team_slug, player_id, player_slug,
               additional_sort, group_sort
        FROM nba_transactions""")

    # The latest roster snapshot. NOTE: current-DATED but 2025-26 in CONTENT. It is
    # frozen here as the 2025-26 end-of-season roster (which is what it actually is,
    # and exactly what R6 asks for as the baseline), NOT as a 2026-27 roster.
    t["rosters_2025_26"] = db.query("""
        SELECT team_id, team_abbreviation, season, player, player_id, position,
               height, weight, age, experience, how_acquired, roster_date
        FROM nba_team_rosters
        WHERE roster_date = (SELECT MAX(roster_date) FROM nba_team_rosters)""")

    # Per-game box for the last completed season, RS and PO, with season_type resolved.
    t["player_games"] = db.query("""
        SELECT ps.player_id, ps.player_name, ps.team_id, ps.team_abbreviation,
               ps.game_date, ps.game_id, g.season_type, ps.minutes_played,
               ps.pts, ps.reb, ps.ast, ps.stl, ps.blk, ps.tov,
               ps.fgm, ps.fga, ps.fg3m, ps.fg3a, ps.ftm, ps.fta, ps.plus_minus
        FROM nba_player_stats ps
        JOIN (SELECT DISTINCT game_id, season_type FROM nba_games) g USING (game_id)
        WHERE ps.season_year = %s""", (SEASON,))

    # Advanced per game. minutes_float is the only trustworthy minutes source;
    # rows with NULL/0 minutes_float are DNPs and must be filtered by consumers.
    t["player_games_adv"] = db.query("""
        SELECT a.game_id, a.person_id AS player_id, a.team_id, g.season_type,
               a.minutes_float, a.usage_percentage, a.true_shooting_percentage,
               a.offensive_rating, a.defensive_rating, a.net_rating, a.pie,
               a.possessions, a.comment
        FROM nba_player_advanced_stats a
        JOIN (SELECT DISTINCT game_id, season_type, game_date FROM nba_games) g
             USING (game_id)
        WHERE g.game_date >= '2025-09-01'""")

    # Team-game results, for measured team net rating (the R6 baseline anchor).
    t["team_games"] = db.query("""
        SELECT game_id, team_id, team_abbreviation, game_date, season_type,
               matchup, wl, pts, plus_minus, minutes_played
        FROM nba_games
        WHERE game_date >= '2025-09-01'""")

    # Player bio: age, draft slot, experience. Used by the minutes heuristic and the
    # rookie prior. NOTE: contains no 2026 draft class.
    t["player_bio"] = db.query("""
        SELECT player_id, display_first_last AS player_name, birthdate, position,
               height_inches, weight, season_exp, from_year, to_year,
               draft_year, draft_round, draft_number, team_abbreviation
        FROM nba_player_bio""")

    return t


def main():
    with runlog.run("freeze_inputs", inputs={"season": SEASON, "host": "nba_warehouse (read-only)"}) as r:
        tables = pull()
        for k, v in tables.items():
            r.note(f"{k}: {len(v):,} rows x {len(v.columns)} cols")
        sid = kfreeze.freeze(
            tables, label="kuminga-phase1",
            note="One snapshot for the whole Kuminga build. rosters_2025_26 is the "
                 "2025-26 end-of-season roster (the table is current-dated but 2025-26 "
                 "in content); it is the R6 baseline, not a 2026-27 roster.")
        r.note(f"snapshot {sid}")
        r.output(f"kuminga/data/frozen/{sid}", tables=len(tables))
    print(f"\nSNAPSHOT: {sid}")


if __name__ == "__main__":
    main()
