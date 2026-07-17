"""Phase 0 probe 4: the usg_pct scale question (spec query returns ZERO rows) +
nba_player_bio schema."""
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


hdr("!! usg_pct SCALE -- spec's `s0.usg_pct >= 28.0` returned ZERO candidates")
print(query("""
    SELECT MIN(usg_pct) AS min, MAX(usg_pct) AS max,
           AVG(usg_pct) AS avg,
           PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY usg_pct) AS p99
    FROM nba.nba_player_season_bio
    WHERE season_type='Regular Season' AND season_year >= '2009-10'
""").to_string(index=False))

print("\n-- top 10 usage seasons since 2009-10 (sanity: should be Westbrook/Harden/Embiid/Jordan-tier)")
print(query("""
    SELECT player_name, season_year, usg_pct, gp
    FROM nba.nba_player_season_bio
    WHERE season_type='Regular Season' AND season_year >= '2009-10' AND gp >= 40
    ORDER BY usg_pct DESC LIMIT 10
""").to_string(index=False))

print("\n-- how many player-seasons clear the spec's intended 28%% bar under each scale reading?")
print(query("""
    SELECT
      SUM((usg_pct >= 28.0)::int)  AS bar_as_written_28_0,
      SUM((usg_pct >= 0.28)::int)  AS bar_as_fraction_0_28,
      COUNT(*)                     AS total_rows
    FROM nba.nba_player_season_bio
    WHERE season_type='Regular Season' AND season_year >= '2009-10'
""").to_string(index=False))

hdr("nba_player_bio full column list")
print(query("""
    SELECT ordinal_position AS ord, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema='nba' AND table_name='nba_player_bio'
    ORDER BY ordinal_position
""").to_string(index=False))

hdr("B2 retry. Scenario A core seed arrivals -> bio position (lookup-level)")
print(query("""
    SELECT pb.player_id, pb.first_name, pb.last_name, pb.position
    FROM nba.nba_player_bio pb
    WHERE (pb.first_name || ' ' || pb.last_name) IN (
        'Damian Lillard','Kyrie Irving','James Harden','Russell Westbrook',
        'Chris Paul','Donovan Mitchell','Bradley Beal','De''Aaron Fox',
        'Luka Doncic','Dejounte Murray','LaMelo Ball','Anthony Edwards',
        'Ben Simmons','John Wall','Zach LaVine','Kristaps Porzingis',
        'Lonzo Ball','Kawhi Leonard','Paul George','Khris Middleton'
    )
    ORDER BY pb.last_name
""").to_string(index=False))

hdr("B3. bio coverage of the (correctly scaled) Scenario A candidate pool")
print(query("""
    WITH cand AS (
        SELECT DISTINCT b.player_id
        FROM nba.nba_player_season_bio b
        WHERE b.season_type='Regular Season'
          AND b.season_year >= '2009-10'
          AND b.usg_pct >= 0.28
    )
    SELECT COUNT(*) AS candidates,
           SUM((pb.player_id IS NULL)::int) AS no_bio_row,
           SUM((pb.position IS NULL OR TRIM(pb.position) = '')::int) AS bio_pos_blank
    FROM cand c
    LEFT JOIN nba.nba_player_bio pb ON pb.player_id = c.player_id
""").to_string(index=False))

print("\n-- position distribution of that pool")
print(query("""
    WITH cand AS (
        SELECT DISTINCT b.player_id
        FROM nba.nba_player_season_bio b
        WHERE b.season_type='Regular Season'
          AND b.season_year >= '2009-10'
          AND b.usg_pct >= 0.28
    )
    SELECT COALESCE(NULLIF(TRIM(pb.position), ''), '(blank)') AS position, COUNT(*) AS n
    FROM cand c
    LEFT JOIN nba.nba_player_bio pb ON pb.player_id = c.player_id
    GROUP BY 1 ORDER BY n DESC
""").to_string(index=False))

hdr("C. wide-open / defender-distance semantics anywhere in the DB?")
r = query("""
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema='nba'
      AND (column_name ILIKE '%%wide%%' OR column_name ILIKE '%%open%%'
           OR column_name ILIKE '%%defender%%' OR column_name ILIKE '%%closest%%'
           OR column_name ILIKE '%%touch_time%%' OR column_name ILIKE '%%dribble%%')
    ORDER BY 1, 2
""")
print(r.to_string(index=False) if len(r) else "   NONE. Confirmed: no defender-distance data exists.")

print("\n-- CatchShoot fg3 columns at SEASON grain")
print(query("""
    SELECT ordinal_position AS ord, column_name
    FROM information_schema.columns
    WHERE table_schema='nba' AND table_name='nba_player_tracking_season'
      AND (column_name ILIKE '%%fg3%%' OR column_name = 'measure_type')
    ORDER BY ordinal_position
""").to_string(index=False))
