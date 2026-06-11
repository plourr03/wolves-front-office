#!/usr/bin/env python3
"""Bounded probe #2: synergy columns + a sample Gobert roll-man row, plus PBP dunk feasibility."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
from lib import db  # noqa: E402
import pandas as pd  # noqa: E402
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 60)

GOBERT = 203497


def q(sql, params=None):
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = 20000")
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


print("=== synergy columns ===")
c = q("""SELECT column_name FROM information_schema.columns
         WHERE table_schema='nba' AND table_name='nba_synergy_player_play_types'
         ORDER BY ordinal_position""")
print(c["column_name"].tolist())

print("\n=== Gobert PRRollMan sample rows (RS), all cols ===")
r = q("""SELECT * FROM nba_synergy_player_play_types
         WHERE player_id=%s AND play_type='PRRollMan' AND season_type='Regular Season'
         ORDER BY season_year""", (GOBERT,))
print(f"rows: {len(r)}  (note: probe1 showed duplicate rows per season -- check for dupes)")
# show a couple seasons, key cols if present
keep = [c for c in ["season_year", "season_type", "play_type", "gp", "poss", "poss_pct",
                    "freq_pct", "pts", "ppp", "fg_pct", "efg_pct", "percentile", "ppp_percentile"]
        if c in r.columns]
print(r[keep].to_string(index=False))

print("\n=== dup check: count rows per (season,type,play_type) for Gobert roll man ===")
d = q("""SELECT season_year, season_type, play_type, COUNT(*) n
         FROM nba_synergy_player_play_types
         WHERE player_id=%s AND play_type='PRRollMan'
         GROUP BY 1,2,3 HAVING COUNT(*)>1 ORDER BY 1""", (GOBERT,))
print(d.to_string(index=False) if len(d) else "no dupes")

print("\n=== PBP: nba_play_by_play columns ===")
pc = q("""SELECT column_name FROM information_schema.columns
          WHERE table_schema='nba' AND table_name='nba_play_by_play'
          ORDER BY ordinal_position""")
print(pc["column_name"].tolist())

print("\n=== PBP dunk feasibility: Gobert dunk-ish descriptions, 2021-22 sample ===")
# find the description column dynamically
desc_col = next((x for x in ["description", "home_description", "visitor_description",
                             "neutral_description", "action_description", "event_description"]
                 if x in pc["column_name"].tolist()), None)
print("description column guess:", desc_col)
