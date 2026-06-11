#!/usr/bin/env python3
"""Validate the 2021-22 touches anomaly + check hustle (screen-assist) coverage +
pull the honest 'hands / non-creator' counter-evidence (roll-man TOV rate, passing, ast)."""
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
from lib import db  # noqa: E402
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40)
GOBERT = 203497


def q(sql, params=None):
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = 30000")
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


print("=== (1) tracking Possessions gp per season for Gobert (validate 2021-22 touches) ===")
g = q("""SELECT season_year, gp, min, touches, time_of_poss
         FROM nba_player_tracking_season
         WHERE player_id=%s AND season_type='Regular Season' AND measure_type='Possessions'
         ORDER BY season_year""", (GOBERT,))
print(g.to_string(index=False))

print("\n=== (2) hustle stats coverage (screen assists) ===")
h = q("""SELECT season_year, season_type, COUNT(*) n FROM nba_player_hustle_stats_season
         GROUP BY 1,2 ORDER BY 1,2""")
print(h.to_string(index=False) if len(h) else "EMPTY")
hc = q("""SELECT column_name FROM information_schema.columns
          WHERE table_schema='nba' AND table_name='nba_player_hustle_stats_season'
            AND column_name ILIKE '%screen%' ORDER BY 1""")
print("screen-assist columns:", hc["column_name"].tolist())
gh = q("""SELECT * FROM nba_player_hustle_stats_season WHERE player_id=%s""", (GOBERT,))
print(f"Gobert hustle rows: {len(gh)}",
      ("seasons: " + str(sorted(gh['season_year'].unique().tolist()))) if len(gh) else "")

print("\n=== (3) honest other side: roll-man TOV rate + passing/creation (the 'hands' limit) ===")
# roll-man turnover rate (offensive)
tov = q("""SELECT season_year, tov_poss_pct roll_tov_pct, ft_poss_pct roll_ft_pct, score_poss_pct
           FROM nba_synergy_player_play_types
           WHERE player_id=%s AND play_type='PRRollMan' AND season_type='Regular Season'
             AND type_grouping='Offensive' ORDER BY season_year""", (GOBERT,))
print("roll-man TOV/FT/score rates:")
print(tov.to_string(index=False))
# passing / creation from tracking Passing measure
pas = q("""SELECT season_year, gp, passes_made, passes_received, ast, potential_ast,
                  ast_to_pass_pct, ast_adj
           FROM nba_player_tracking_season
           WHERE player_id=%s AND season_type='Regular Season' AND measure_type='Passing'
           ORDER BY season_year""", (GOBERT,))
pas["ast_pg"] = (pd.to_numeric(pas["ast"]) / pas["gp"].clip(lower=1)).round(2)
pas["potast_pg"] = (pd.to_numeric(pas["potential_ast"]) / pas["gp"].clip(lower=1)).round(2)
print("\npassing/creation (low = the non-creator 'hands' limitation):")
print(pas[["season_year", "gp", "passes_made", "ast_pg", "potast_pg", "ast_to_pass_pct"]].to_string(index=False))
