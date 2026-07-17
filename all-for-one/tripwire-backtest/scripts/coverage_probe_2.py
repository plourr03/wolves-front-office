"""Phase 0 schema probe, part 2. Fixes the `min` column error and drills the
position question, which part 1 showed is not cleanly answerable."""
import sys
from pathlib import Path

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

import pandas as pd  # noqa: E402
pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 300)


def hdr(s):
    print("\n" + "=" * 78)
    print(s)
    print("=" * 78)


hdr("1b. nba_player_season_bio full column list")
print(query("""
    SELECT ordinal_position AS ord, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema='nba' AND table_name='nba_player_season_bio'
    ORDER BY ordinal_position
""").to_string(index=False))

hdr("1c. nba_player_bio.position  (static/career -- the only all-time source)")
print(query("""
    SELECT position AS val, COUNT(*) AS n
    FROM nba.nba_player_bio GROUP BY 1 ORDER BY n DESC NULLS LAST
""").to_string(index=False))

hdr("1d. nba_player_advanced_stats.position null rate PER SEASON (61%% null overall)")
print(query("""
    SELECT RIGHT(g.season_id::text, 4) AS season_start,
           COUNT(*) AS player_games,
           SUM((a.position IS NULL)::int) AS pos_null,
           ROUND(100.0 * SUM((a.position IS NULL)::int) / COUNT(*), 1) AS pct_null
    FROM nba.nba_player_advanced_stats a
    JOIN nba.nba_games g ON g.game_id = a.game_id
    WHERE RIGHT(g.season_id::text, 4)::int >= 2009
      AND LEFT(g.season_id::text, 1) = '2'
    GROUP BY 1 ORDER BY 1
""").to_string(index=False))

hdr("1e. Does advanced_stats.position only populate for STARTERS? (reconciler uses it for starters)")
print(query("""
    SELECT (a.position IS NULL) AS pos_is_null,
           COUNT(*) AS n,
           ROUND(AVG(a.minutes_float)::numeric, 2) AS avg_min
    FROM nba.nba_player_advanced_stats a
    JOIN nba.nba_games g ON g.game_id = a.game_id
    WHERE g.season_id::text = '22023'
    GROUP BY 1
""").to_string(index=False))

hdr("3a. nba_player_season_bio usg_pct / gp nulls per season (RS)")
print(query("""
    SELECT season_year, COUNT(*) AS rows,
           SUM((usg_pct IS NULL)::int) AS usg_null,
           SUM((gp IS NULL)::int) AS gp_null
    FROM nba.nba_player_season_bio
    WHERE season_type = 'Regular Season' AND season_year >= '2009-10'
    GROUP BY 1 ORDER BY 1
""").to_string(index=False))

hdr("3b. nba_games.game_date nulls")
print(query("""
    SELECT SUM((game_date IS NULL)::int) AS date_null, COUNT(*) AS rows
    FROM nba.nba_games
""").to_string(index=False))

hdr("3c. minutes_float nulls per season (reconciler PRIMARY reference)")
print(query("""
    SELECT RIGHT(g.season_id::text, 4) AS season_start,
           LEFT(g.season_id::text, 1) AS stype,
           COUNT(*) AS player_games,
           SUM((a.minutes_float IS NULL)::int) AS mf_null
    FROM nba.nba_player_advanced_stats a
    JOIN nba.nba_games g ON g.game_id = a.game_id
    WHERE RIGHT(g.season_id::text, 4)::int >= 2009
    GROUP BY 1, 2 ORDER BY 1, 2
""").to_string(index=False))

hdr("4a. nba_games team-game rows by season")
print(query("""
    SELECT RIGHT(season_id::text, 4) AS season_start,
           LEFT(season_id::text, 1) AS stype,
           COUNT(*) AS team_game_rows, COUNT(DISTINCT game_id) AS games
    FROM nba.nba_games
    WHERE RIGHT(season_id::text, 4)::int >= 2009
    GROUP BY 1, 2 ORDER BY 1, 2
""").to_string(index=False))

hdr("4b. PBP by season + format mix (RS only)")
print(query("""
    SELECT RIGHT(g.season_id::text, 4) AS season_start,
           p.source, COUNT(DISTINCT p.game_id) AS games, COUNT(*) AS pbp_rows
    FROM nba.nba_play_by_play p
    JOIN nba.nba_games g ON g.game_id = p.game_id
    WHERE RIGHT(g.season_id::text, 4)::int >= 2009
      AND LEFT(g.season_id::text, 1) = '2'
    GROUP BY 1, 2 ORDER BY 1, 2
""").to_string(index=False))

hdr("4c. nba_player_stats by season_year")
print(query("""
    SELECT season_year, COUNT(*) AS rows, COUNT(DISTINCT game_id) AS games
    FROM nba.nba_player_stats
    WHERE season_year >= '2009-10' GROUP BY 1 ORDER BY 1
""").to_string(index=False))

hdr("4d. nba_transactions by year")
print(query("""
    SELECT EXTRACT(YEAR FROM transaction_date)::int AS yr, COUNT(*) AS n
    FROM nba.nba_transactions GROUP BY 1 ORDER BY 1
""").to_string(index=False))

hdr("5. Orphan PBP game_ids")
orph = query("""
    SELECT p.game_id, LEFT(p.game_id, 3) AS prefix, COUNT(*) AS pbp_rows
    FROM nba.nba_play_by_play p
    LEFT JOIN nba.nba_games g ON g.game_id = p.game_id
    WHERE g.game_id IS NULL
    GROUP BY 1, 2 ORDER BY 1
""")
print(orph.to_string(index=False))
print(f"\norphan game count: {len(orph)}")
