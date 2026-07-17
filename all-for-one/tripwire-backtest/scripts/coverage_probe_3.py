"""Phase 0 probe 3: confirm two load-bearing assumptions before writing the report.

A) minutes_float nulls are DNPs, not data loss. Load-bearing because the spike's
   PRIMARY criterion (recon_rate_TRUE_0p5) is scored against minutes_float.
B) nba_player_bio.position covers the Scenario A arriving-guard population.
C) CatchShoot season-grain columns, for the G4 write-up.
"""
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


hdr("A. Are minutes_float nulls just DNPs? (2013-14 RS)")
print(query("""
    SELECT (a.minutes_float IS NULL) AS mf_null,
           COUNT(*) AS n,
           SUM((ps.player_id IS NULL)::int) AS no_box_row,
           SUM((a.comment IS NOT NULL AND TRIM(a.comment) <> '')::int) AS has_dnp_comment,
           SUM((a.minutes IS NULL OR TRIM(a.minutes) = '')::int) AS adv_minutes_blank
    FROM nba.nba_player_advanced_stats a
    JOIN nba.nba_games g ON g.game_id = a.game_id
    LEFT JOIN nba.nba_player_stats ps
           ON ps.game_id = a.game_id AND ps.player_id = a.person_id
    WHERE g.season_id::text = '22013'
    GROUP BY 1
""").to_string(index=False))

hdr("A2. nba_player_stats column list (find the minutes column name)")
print(query("""
    SELECT ordinal_position AS ord, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema='nba' AND table_name='nba_player_stats'
    ORDER BY ordinal_position
""").to_string(index=False))

hdr("B. nba_player_bio coverage vs the Scenario A candidate population")
print("-- players with a RS season >= 2009-10 who have usg>=28 & a bio position")
print(query("""
    WITH cand AS (
        SELECT DISTINCT b.player_id
        FROM nba.nba_player_season_bio b
        WHERE b.season_type='Regular Season'
          AND b.season_year >= '2009-10'
          AND b.usg_pct >= 28.0
    )
    SELECT COUNT(*) AS candidates,
           SUM((pb.player_id IS NULL)::int) AS no_bio_row,
           SUM((pb.position IS NULL OR TRIM(pb.position) = '')::int) AS bio_pos_blank
    FROM cand c
    LEFT JOIN nba.nba_player_bio pb ON pb.player_id = c.player_id
""").to_string(index=False))

print("\n-- position distribution of that candidate pool")
print(query("""
    WITH cand AS (
        SELECT DISTINCT b.player_id
        FROM nba.nba_player_season_bio b
        WHERE b.season_type='Regular Season'
          AND b.season_year >= '2009-10'
          AND b.usg_pct >= 28.0
    )
    SELECT COALESCE(NULLIF(TRIM(pb.position), ''), '(blank)') AS position,
           COUNT(*) AS n
    FROM cand c
    LEFT JOIN nba.nba_player_bio pb ON pb.player_id = c.player_id
    GROUP BY 1 ORDER BY n DESC
""").to_string(index=False))

hdr("B2. Do the Scenario A core seed arrivals resolve to a Guard position? (lookup-level)")
print(query("""
    SELECT pb.player_id, pb.player_name, pb.position
    FROM nba.nba_player_bio pb
    WHERE pb.player_name IN (
        'Damian Lillard','Kyrie Irving','James Harden','Russell Westbrook',
        'Chris Paul','Donovan Mitchell','Bradley Beal','De''Aaron Fox',
        'Luka Doncic','Dejounte Murray','LaMelo Ball','Anthony Edwards'
    )
    ORDER BY pb.player_name
""").to_string(index=False))

hdr("C. CatchShoot season-grain columns (G4 write-up)")
print(query("""
    SELECT ordinal_position AS ord, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema='nba' AND table_name='nba_player_tracking_season'
      AND (column_name ILIKE '%%fg3%%' OR column_name ILIKE '%%catch%%'
           OR column_name ILIKE '%%fga%%' OR column_name = 'measure_type')
    ORDER BY ordinal_position
""").to_string(index=False))

print("\n-- confirm: is there ANY column anywhere in the DB with wide-open / defender-distance semantics?")
print(query("""
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema='nba'
      AND (column_name ILIKE '%%wide%%' OR column_name ILIKE '%%open%%'
           OR column_name ILIKE '%%defender%%' OR column_name ILIKE '%%closest%%'
           OR column_name ILIKE '%%touch_time%%' OR column_name ILIKE '%%dribble%%')
    ORDER BY 1, 2
""").to_string(index=False))
