"""One-shot inventory of 2025-26 vs historical coverage in the warehouse.

Reads connection params from `wolves-front-office/.env` (POSTGRES_*).
Fails loudly if the file is missing or still contains the REPLACE_ME placeholder
so we never silently fall back to a stale local DB.
"""
import os
import sys
from pathlib import Path

import psycopg2

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = REPO_ROOT / ".env"

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit("python-dotenv is required. Install with: pip install python-dotenv")

if not ENV_PATH.exists():
    sys.exit(f"Missing {ENV_PATH}. Copy .env.example to .env and fill in the password.")
load_dotenv(ENV_PATH)

required = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
missing = [k for k in required if not os.getenv(k)]
if missing:
    sys.exit(f"Missing env vars: {missing}")
if os.getenv("POSTGRES_PASSWORD") == "REPLACE_ME":
    sys.exit(f"POSTGRES_PASSWORD is still REPLACE_ME in {ENV_PATH}. Set the real password.")

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=int(os.environ["POSTGRES_PORT"]),
    database=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
cur = conn.cursor()

def q(sql, *params):
    cur.execute(sql, params)
    return cur.fetchall()

def hdr(t):
    print(f"\n{'='*72}\n{t}\n{'='*72}")

hdr("Server / schema")
print(q("SELECT current_database(), current_user, inet_server_addr(), inet_server_port(), version()")[0])
print("tables in nba:", [r[0] for r in q(
    "SELECT table_name FROM information_schema.tables WHERE table_schema='nba' ORDER BY 1"
)])

hdr("nba_games: distinct games per season, last 5 seasons")
for row in q("""
    SELECT season_id, season_type,
           COUNT(DISTINCT game_id) AS games,
           MIN(game_date) AS first_dt,
           MAX(game_date) AS last_dt
    FROM nba.nba_games
    WHERE season_id IN ('22025','22024','22023','22022','22021',
                        '42025','42024','42023','42022','42021')
    GROUP BY season_id, season_type
    ORDER BY season_id DESC, season_type
"""):
    print(f"  {row[0]} {row[1]:<14} games={row[2]:>5}  {row[3]} .. {row[4]}")

hdr("nba_player_stats: 2025-26 player-game rows by month")
for row in q("""
    SELECT date_trunc('month', game_date)::date AS mo, COUNT(*)
    FROM nba.nba_player_stats
    WHERE game_date >= '2025-10-01'
    GROUP BY mo ORDER BY mo
"""):
    print(f"  {row[0]}  {row[1]:>6,} rows")

hdr("nba_play_by_play: 2025-26 game coverage (joined via nba_games)")
for row in q("""
    WITH g AS (
        SELECT DISTINCT game_id, game_date FROM nba.nba_games
        WHERE game_date >= '2025-10-01'
    ),
    p AS (
        SELECT DISTINCT pbp.game_id, g.game_date
        FROM nba.nba_play_by_play pbp
        JOIN g USING (game_id)
    )
    SELECT
        (SELECT COUNT(*) FROM g)  AS games_in_2025_26,
        (SELECT COUNT(*) FROM p)  AS games_with_pbp,
        (SELECT COUNT(*) FROM g) - (SELECT COUNT(*) FROM p) AS missing,
        (SELECT MAX(game_date) FROM p) AS last_pbp_game_date
"""):
    print(f"  games_in_2025_26={row[0]}  with_pbp={row[1]}  missing={row[2]}  last_pbp_date={row[3]}")

hdr("nba_play_by_play: 2025-26 row count")
for row in q("""
    SELECT COUNT(*)
    FROM nba.nba_play_by_play pbp
    WHERE pbp.game_id IN (
        SELECT game_id FROM nba.nba_games WHERE game_date >= '2025-10-01'
    )
"""):
    print(f"  rows={row[0]:,}")

hdr("nba_player_advanced_stats: 2025-26 rows (game_id joined)")
for row in q("""
    SELECT COUNT(*), COUNT(DISTINCT pas.game_id)
    FROM nba.nba_player_advanced_stats pas
    WHERE pas.game_id IN (
        SELECT game_id FROM nba.nba_games WHERE game_date >= '2025-10-01'
    )
"""):
    print(f"  rows={row[0]:,}  games={row[1]:,}")

hdr("nba_team_advanced_stats: 2025-26 rows (game_id joined)")
for row in q("""
    SELECT COUNT(*), COUNT(DISTINCT tas.game_id)
    FROM nba.nba_team_advanced_stats tas
    WHERE tas.game_id IN (
        SELECT game_id FROM nba.nba_games WHERE game_date >= '2025-10-01'
    )
"""):
    print(f"  rows={row[0]:,}  games={row[1]:,}")

hdr("nba_team_rosters: seasons present")
for row in q("SELECT season, COUNT(*) FROM nba.nba_team_rosters GROUP BY season ORDER BY season DESC"):
    print(f"  {row[0]:<12} rows={row[1]:,}")

hdr("daily_refresh_run_log: schema")
for row in q("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema='nba' AND table_name='daily_refresh_run_log'
    ORDER BY ordinal_position
"""):
    print(f"  {row[0]:<30} {row[1]}")

hdr("daily_refresh_run_log: last 10 runs (all cols)")
for row in q("""
    SELECT *
    FROM nba.daily_refresh_run_log
    ORDER BY 1 DESC
    LIMIT 10
"""):
    print(f"  {row}")

hdr("Timberwolves 2025-26 game count sanity check")
print(q("""
    SELECT season_type, COUNT(DISTINCT game_id)
    FROM nba.nba_games
    WHERE season_id IN ('22025','42025')
      AND team_abbreviation = 'MIN'
    GROUP BY season_type
""")[0:5])

conn.close()
