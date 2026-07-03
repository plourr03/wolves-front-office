"""Targeted ingest: backfill the 2020-21 player-tracking hole in
nba_player_tracking_season (F3 GATING ruling item 1, 2026-07-03).

The warehouse load skipped 2020-21 for the season-aggregate tracking
endpoints; the endpoint itself HAS the season (verified: LeagueDashPtStats
season=2020-21 returns 540 players). This pulls all 11 measure types the
warehouse carries and inserts them with the same schema/convention as the
existing seasons (columns are the API fields lowercased; the warehouse adds
season_year/season_type/measure_type/source/updated_at). Idempotent:
deletes any existing 2020-21 Regular Season tracking rows first (there are
none) then inserts.

Run: python -m src.etl.ingest_tracking_2021   (any python with nba_api +
     psycopg2; uses the repo-root .env)
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

REPO_ROOT = Path(__file__).resolve().parents[3]
SEASON = "2020-21"
SEASON_TYPE = "Regular Season"
SOURCE = "stats_api"
MEASURES = ["Possessions", "CatchShoot", "PullUpShot", "Drives", "Defense",
            "Passing", "ElbowTouch", "PostTouch", "PaintTouch", "Rebounding",
            "SpeedDistance"]


def _connect():
    for line in open(REPO_ROOT / ".env"):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"], user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        options=f"-c search_path={os.environ.get('POSTGRES_SCHEMA', 'nba')}")


def _pull(measure: str) -> pd.DataFrame:
    from nba_api.stats.endpoints import leaguedashptstats
    ep = leaguedashptstats.LeagueDashPtStats(
        pt_measure_type=measure, player_or_team="Player", season=SEASON,
        season_type_all_star=SEASON_TYPE, timeout=30)
    df = ep.get_data_frames()[0]
    df.columns = [c.lower() for c in df.columns]
    # the only API/warehouse column-name difference across the 11 measures
    # (the warehouse pipeline renamed it on load)
    df = df.rename(columns={"ast_pts_created": "ast_points_created"})
    df["season_year"] = SEASON
    df["season_type"] = SEASON_TYPE
    df["measure_type"] = measure
    df["source"] = SOURCE
    df["updated_at"] = datetime.now()
    return df


def main() -> None:
    con = _connect()
    cur = con.cursor()
    cur.execute("SELECT * FROM nba_player_tracking_season LIMIT 0")
    wh_cols = [d[0] for d in cur.description]

    pre = pd.read_sql("""SELECT measure_type, count(*) n FROM nba_player_tracking_season
                         WHERE season_year=%s AND season_type=%s GROUP BY 1""",
                      con, params=(SEASON, SEASON_TYPE))
    print(f"pre-existing 2020-21 tracking rows: {int(pre.n.sum()) if len(pre) else 0}")
    cur.execute("""DELETE FROM nba_player_tracking_season
                   WHERE season_year=%s AND season_type=%s""",
                (SEASON, SEASON_TYPE))
    print(f"deleted {cur.rowcount} stale rows (idempotency)")

    total = 0
    for measure in MEASURES:
        df = _pull(measure)
        unmapped = [c for c in df.columns if c not in wh_cols]
        if unmapped:
            raise RuntimeError(f"{measure}: API cols not in warehouse: {unmapped}")
        aligned = df.reindex(columns=wh_cols)
        rows = [tuple(None if pd.isna(v) else v for v in r)
                for r in aligned.itertuples(index=False, name=None)]
        execute_values(
            cur,
            f"INSERT INTO nba_player_tracking_season ({', '.join(wh_cols)}) VALUES %s",
            rows, page_size=500)
        total += len(rows)
        print(f"  {measure}: inserted {len(rows)} rows")
    con.commit()

    post = pd.read_sql("""SELECT measure_type, count(*) n FROM nba_player_tracking_season
                          WHERE season_year=%s AND season_type=%s GROUP BY 1 ORDER BY 1""",
                       con, params=(SEASON, SEASON_TYPE))
    print(f"\ninserted {total} rows across {len(MEASURES)} measures")
    print(post.to_string(index=False))
    con.close()


if __name__ == "__main__":
    main()
