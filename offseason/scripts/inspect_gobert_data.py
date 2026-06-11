#!/usr/bin/env python3
"""
inspect_gobert_data.py -- BOUNDED data-availability probe for the Gobert usage audit.

Deliberately small and timeout-guarded (15s statement timeout) so it cannot hang:
checks what tracking / synergy seasons exist for Gobert (id 203497) in the warehouse,
across his Utah (2013-14..2021-22) and Minnesota (2022-23..2025-26) years.

    python inspect_gobert_data.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
from lib import db  # noqa: E402

GOBERT = 203497


def q(sql, params=None):
    # statement_timeout guard so a stalled query fails loudly instead of hanging
    import psycopg2
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = 15000")
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    import pandas as pd
    return pd.DataFrame(rows, columns=cols)


print("=== nba_player_tracking_season: season x measure_type coverage (all players) ===")
cov = q("""SELECT season_year, season_type, measure_type, COUNT(*) n
           FROM nba_player_tracking_season
           GROUP BY 1,2,3 ORDER BY 1,2,3""")
import pandas as pd
pd.set_option("display.max_rows", 300)
pd.set_option("display.width", 200)
# compact: just season x measure_type matrix for Regular Season
rs = cov[cov["season_type"] == "Regular Season"]
print("Regular Season measure_types by season:")
print(rs.pivot_table(index="season_year", columns="measure_type", values="n", aggfunc="sum").fillna(0).astype(int))

print("\n=== Gobert (203497) rows in nba_player_tracking_season ===")
g = q("""SELECT season_year, season_type, measure_type
         FROM nba_player_tracking_season WHERE player_id=%s
         ORDER BY season_year, season_type, measure_type""", (GOBERT,))
print(f"rows: {len(g)}")
print("seasons present:", sorted(g["season_year"].unique().tolist()))
print("measure_types present:", sorted(g["measure_type"].unique().tolist()))

print("\n=== columns available in nba_player_tracking_season ===")
colz = q("""SELECT column_name FROM information_schema.columns
            WHERE table_schema='nba' AND table_name='nba_player_tracking_season'
            ORDER BY ordinal_position""")
print(colz["column_name"].tolist())

print("\n=== nba_synergy_player_play_types: season coverage + play_types ===")
syn = q("""SELECT season_year, season_type, COUNT(DISTINCT play_type) ptypes, COUNT(*) n
           FROM nba_synergy_player_play_types GROUP BY 1,2 ORDER BY 1,2""")
print(syn.to_string(index=False))
pt = q("SELECT DISTINCT play_type FROM nba_synergy_player_play_types ORDER BY 1")
print("play_types:", pt["play_type"].tolist())

print("\n=== Gobert synergy rows (warehouse only) ===")
gs = q("""SELECT season_year, season_type, play_type
          FROM nba_synergy_player_play_types WHERE player_id=%s
          ORDER BY 1,2,3""", (GOBERT,))
print(f"rows: {len(gs)}")
if len(gs):
    print(gs.to_string(index=False))
