"""Phase 0 schema probe for the tripwire backtest.

Answers the five open unknowns from the approved plan Step 1.
Read-only. Prints a report; writes nothing to the DB.
"""
import sys
from pathlib import Path

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
sys.path.insert(0, str(REPO / "postmortem"))
from lib.db import query  # noqa: E402

import pandas as pd  # noqa: E402

pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 200)
pd.set_option("display.max_columns", 50)


def hdr(s):
    print("\n" + "=" * 78)
    print(s)
    print("=" * 78)


# ---------------------------------------------------------------- 1. position
hdr("1. POSITION FIELD for spec pos_group='G' filter")

for tbl in ("nba_player_season_bio", "nba_player_bio", "nba_team_rosters",
            "nba_player_advanced_stats"):
    cols = query("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema='nba' AND table_name=%s
          AND (column_name ILIKE '%%pos%%' OR column_name ILIKE '%%height%%')
        ORDER BY ordinal_position
    """, (tbl,))
    print(f"\n-- {tbl}")
    print(cols.to_string(index=False) if len(cols) else "   (no position-like column)")

# what values does it actually carry, and is it populated historically?
for tbl, col, seascol in (
    ("nba_player_season_bio", "position", "season_year"),
    ("nba_player_advanced_stats", "position", None),
    ("nba_team_rosters", "position", None),
):
    exists = query("""
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='nba' AND table_name=%s AND column_name=%s
    """, (tbl, col))
    if not len(exists):
        continue
    print(f"\n-- {tbl}.{col} distinct values (top 25)")
    print(query(f"""
        SELECT {col} AS val, COUNT(*) AS n
        FROM nba.{tbl}
        GROUP BY 1 ORDER BY n DESC NULLS LAST LIMIT 25
    """).to_string(index=False))


# -------------------------------------------------- 2. tracking_game coverage
hdr("2. nba_player_tracking_game  (decides G4 / SPACE-ANT)")

print("\n-- full column list")
print(query("""
    SELECT ordinal_position AS ord, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema='nba' AND table_name='nba_player_tracking_game'
    ORDER BY ordinal_position
""").to_string(index=False))

print("\n-- season coverage (via join to nba_games for season) + uncontested nulls")
print(query("""
    SELECT LEFT(g.season_id::text, 1) AS stype,
           RIGHT(g.season_id::text, 4) AS season_start,
           COUNT(DISTINCT t.game_id) AS games,
           COUNT(*) AS rows
    FROM nba.nba_player_tracking_game t
    JOIN nba.nba_games g ON g.game_id = t.game_id
    GROUP BY 1, 2 ORDER BY 2, 1
""").to_string(index=False))


# ------------------------------------------------------------- 3. null audit
hdr("3. NULL AUDIT on load-bearing columns")

print("\n-- nba_player_season_bio: usg_pct / gp nulls per season (RS only)")
print(query("""
    SELECT season_year,
           COUNT(*) AS rows,
           SUM((usg_pct IS NULL)::int) AS usg_null,
           SUM((gp IS NULL)::int) AS gp_null,
           SUM((min IS NULL)::int) AS min_null
    FROM nba.nba_player_season_bio
    WHERE season_type = 'Regular Season'
      AND season_year >= '2009-10'
    GROUP BY 1 ORDER BY 1
""").to_string(index=False))

print("\n-- nba_games.game_date nulls")
print(query("""
    SELECT SUM((game_date IS NULL)::int) AS date_null, COUNT(*) AS rows
    FROM nba.nba_games
""").to_string(index=False))

print("\n-- nba_player_advanced_stats.minutes_float nulls per season (reconciler PRIMARY ref)")
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


# ------------------------------------------------- 4. rows per season, 5 core
hdr("4. ROWS PER SEASON, core tables, 2009-10 .. 2025-26")

print("\n-- nba_games (team-game) by season_id prefix")
print(query("""
    SELECT RIGHT(season_id::text, 4) AS season_start,
           LEFT(season_id::text, 1) AS stype,
           COUNT(*) AS team_game_rows,
           COUNT(DISTINCT game_id) AS games
    FROM nba.nba_games
    WHERE RIGHT(season_id::text, 4)::int >= 2009
    GROUP BY 1, 2 ORDER BY 1, 2
""").to_string(index=False))

print("\n-- nba_play_by_play by season (join games) + format mix")
print(query("""
    SELECT RIGHT(g.season_id::text, 4) AS season_start,
           p.source,
           COUNT(DISTINCT p.game_id) AS games,
           COUNT(*) AS pbp_rows
    FROM nba.nba_play_by_play p
    JOIN nba.nba_games g ON g.game_id = p.game_id
    WHERE RIGHT(g.season_id::text, 4)::int >= 2009
      AND LEFT(g.season_id::text, 1) = '2'
    GROUP BY 1, 2 ORDER BY 1, 2
""").to_string(index=False))

print("\n-- nba_player_stats by season_year")
print(query("""
    SELECT season_year, COUNT(*) AS rows, COUNT(DISTINCT game_id) AS games
    FROM nba.nba_player_stats
    WHERE season_year >= '2009-10'
    GROUP BY 1 ORDER BY 1
""").to_string(index=False))

print("\n-- nba_transactions by year (era boundary)")
print(query("""
    SELECT EXTRACT(YEAR FROM transaction_date)::int AS yr,
           COUNT(*) AS n,
           MIN(transaction_date) AS first_date
    FROM nba.nba_transactions
    GROUP BY 1 ORDER BY 1
""").to_string(index=False))


# ------------------------------------------------------------- 5. orphan pbp
hdr("5. ORPHAN PBP game_ids (no nba_games row)")

orph = query("""
    SELECT DISTINCT p.game_id, LEFT(p.game_id, 3) AS prefix, COUNT(*) AS pbp_rows
    FROM nba.nba_play_by_play p
    LEFT JOIN nba.nba_games g ON g.game_id = p.game_id
    WHERE g.game_id IS NULL
    GROUP BY 1, 2 ORDER BY 1
""")
print(orph.to_string(index=False))
print(f"\norphan count: {len(orph)}")
