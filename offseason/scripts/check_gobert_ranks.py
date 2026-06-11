#!/usr/bin/env python3
"""Verify the outline's two publishable claims: (a) league-leading screen assists in Utah,
(b) elite roll-man efficiency. Rank Gobert league-wide per season."""
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
from lib import db  # noqa: E402
GOBERT = 203497
pd.set_option("display.width", 200)


def q(sql, params=None):
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = 30000")
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


print("=== (a) Screen-assist league rank per season (total screen assists, RS, g>=40) ===")
sa = q("""SELECT season_year, player_id, player_name, g, screen_assists,
                 RANK() OVER (PARTITION BY season_year ORDER BY screen_assists DESC) rk
          FROM nba_player_hustle_stats_season
          WHERE season_type='Regular Season' AND g>=40""")
gob = sa[sa.player_id == GOBERT].sort_values("season_year")
for _, r in gob.iterrows():
    leader = sa[(sa.season_year == r.season_year) & (sa.rk == 1)].iloc[0]
    print(f"  {r.season_year}: Gobert {int(r.screen_assists)} screen ast, league rank #{int(r.rk)} "
          f"| leader: {leader.player_name} {int(leader.screen_assists)}")

print("\n=== (b) Roll-man (offensive) PPP percentile per season (min 50 poss) ===")
rm = q("""SELECT season_year, ppp, percentile, poss
          FROM nba_synergy_player_play_types
          WHERE player_id=%s AND play_type='PRRollMan' AND season_type='Regular Season'
            AND type_grouping='Offensive' AND poss>=50 ORDER BY season_year""", (GOBERT,))
print(rm.to_string(index=False))
print(f"\n  mean roll-man percentile (Utah 16-22 vs MIN): "
      f"Utah {rm[(rm.season_year>='2016-17')&(rm.season_year<='2021-22')].percentile.mean():.2f}, "
      f"MIN {rm[rm.season_year>='2022-23'].percentile.mean():.2f}")
