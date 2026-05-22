"""Verify factual claims in 01_lafi_article_first_draft.md against the warehouse."""
import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

if os.environ.get("POSTGRES_PASSWORD", "replace-me") == "replace-me":
    raise RuntimeError(".env password missing or placeholder")

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
cur = conn.cursor()
cur.execute("SET search_path TO nba")


def section(title):
    print(f"\n{'='*70}\n{title}\n{'='*70}")


section("Identify season_id values present for 2025-26")
cur.execute(
    """
    SELECT DISTINCT season_id, season_type, MIN(game_date), MAX(game_date), COUNT(*)
    FROM nba_games
    WHERE game_date >= '2025-09-01'
    GROUP BY season_id, season_type
    ORDER BY season_id, season_type
    """
)
for r in cur.fetchall():
    print(r)

section("CLAIM: 2025-26 Wolves regular season record = 49-33")
cur.execute(
    """
    SELECT
      SUM(CASE WHEN wl = 'W' THEN 1 ELSE 0 END) AS wins,
      SUM(CASE WHEN wl = 'L' THEN 1 ELSE 0 END) AS losses,
      COUNT(*) AS games
    FROM nba_games
    WHERE team_abbreviation = 'MIN'
      AND season_type = 'Regular Season'
      AND game_date BETWEEN '2025-09-01' AND '2026-06-30'
    """
)
print("Wolves RS record:", cur.fetchone())

section("CLAIM: Beat Nuggets in R1 of 2025-26 playoffs")
cur.execute(
    """
    SELECT game_date, matchup, wl, pts
    FROM nba_games
    WHERE team_abbreviation = 'MIN'
      AND season_type = 'Playoffs'
      AND game_date BETWEEN '2025-09-01' AND '2026-08-31'
    ORDER BY game_date
    """
)
for r in cur.fetchall():
    print(r)

section("CLAIM: Wolves 2025-26 ORtg = middle of the pack (RS, league rank)")
cur.execute(
    """
    WITH team_season AS (
      SELECT g.team_abbreviation,
             SUM(g.pts) AS pts,
             SUM(a.possessions) AS poss,
             AVG(a.offensive_rating) AS avg_ortg,
             COUNT(*) AS games
      FROM nba_games g
      JOIN nba_team_advanced_stats a USING (game_id, team_id)
      WHERE g.season_type = 'Regular Season'
        AND g.game_date BETWEEN '2025-09-01' AND '2026-06-30'
      GROUP BY g.team_abbreviation
    )
    SELECT team_abbreviation,
           ROUND(avg_ortg::numeric, 2) AS avg_ortg,
           RANK() OVER (ORDER BY avg_ortg DESC) AS ortg_rank,
           games
    FROM team_season
    ORDER BY avg_ortg DESC
    """
)
rows = cur.fetchall()
for r in rows:
    print(r)

section("CLAIM: Wolves 2025-26 DRtg = top-five defense (RS, league rank)")
cur.execute(
    """
    WITH team_season AS (
      SELECT g.team_abbreviation,
             AVG(a.defensive_rating) AS avg_drtg,
             COUNT(*) AS games
      FROM nba_games g
      JOIN nba_team_advanced_stats a USING (game_id, team_id)
      WHERE g.season_type = 'Regular Season'
        AND g.game_date BETWEEN '2025-09-01' AND '2026-06-30'
      GROUP BY g.team_abbreviation
    )
    SELECT team_abbreviation,
           ROUND(avg_drtg::numeric, 2) AS avg_drtg,
           RANK() OVER (ORDER BY avg_drtg ASC) AS drtg_rank,
           games
    FROM team_season
    ORDER BY avg_drtg ASC
    """
)
for r in cur.fetchall():
    print(r)
