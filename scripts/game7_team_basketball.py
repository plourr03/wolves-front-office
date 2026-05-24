"""How much team basketball / unselfish ball did the Wolves play in Game 7
vs. their 2023-24 baseline? Per-game tracking only, no LAFI percentile work."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
from lib.db import query

GAME_ID = '0042300237'

# Game-level team tracking for MIN in this game
g7_team = query("""
    SELECT t.*
    FROM nba_team_tracking_game t
    WHERE t.game_id = %s AND t.team_tricode = 'MIN'
""", (GAME_ID,))
print("Game 7 MIN team-tracking row:")
print(g7_team.T.to_string())

# Same metrics for every MIN regular-season game 2023-24 (baseline)
baseline = query("""
    SELECT t.game_id, g.game_date, t.passes, t.assists, t.secondary_assists,
           t.touches, t.contested_fga, t.uncontested_fga,
           t.contested_fgm, t.uncontested_fgm,
           g.fgm, g.fga, g.ast, g.pts, g.tov
    FROM nba_team_tracking_game t
    JOIN nba_games g
      ON g.game_id = t.game_id AND g.team_id = t.team_id
    WHERE t.team_tricode = 'MIN'
      AND g.season_type = 'Regular Season'
      AND g.game_date BETWEEN '2023-10-01' AND '2024-04-30'
""")
print(f"\nBaseline: {len(baseline)} regular-season games 2023-24")

# Compute indicators
def indicators(row, fgm, ast):
    return {
        'passes': int(row['passes']),
        'assists': int(row['assists']),
        'secondary_assists': int(row['secondary_assists']),
        'touches': int(row['touches']),
        'passes_per_touch': row['passes'] / row['touches'] if row['touches'] else None,
        'ast_per_fgm': ast / fgm if fgm else None,
        'assisted_fgm_share_proxy': ast / fgm if fgm else None,  # same thing
        'contested_fga_share': row['contested_fga'] / (row['contested_fga'] + row['uncontested_fga']) if (row['contested_fga'] + row['uncontested_fga']) else None,
        'uncontested_fg_pct': row['uncontested_fgm'] / row['uncontested_fga'] if row['uncontested_fga'] else None,
    }

g7_row = g7_team.iloc[0]
# Need MIN game stats for that game (fgm, ast)
g7_box = query("""SELECT fgm, fga, ast, pts, tov FROM nba_games WHERE game_id = %s AND team_abbreviation = 'MIN'""", (GAME_ID,)).iloc[0]
g7_ind = indicators(g7_row, g7_box['fgm'], g7_box['ast'])
print("\nGAME 7 indicators (MIN):")
for k,v in g7_ind.items():
    print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")

# Baseline distribution
base_ind = []
for _, r in baseline.iterrows():
    base_ind.append(indicators(r, r['fgm'], r['ast']))
base_df = pd.DataFrame(base_ind)

print("\n2023-24 RS baseline (per game):")
print(base_df.describe().round(3).T[['mean','std','min','25%','50%','75%','max']].to_string())

# Where does Game 7 fall in the baseline distribution? (percentile rank)
print("\nGame 7 percentile within 2023-24 RS distribution:")
for k, v in g7_ind.items():
    if k in base_df.columns and isinstance(v, (int, float)):
        pct = (base_df[k] <= v).mean() * 100
        print(f"  {k}: {v:.3f}  pct={pct:.0f}  (mean {base_df[k].mean():.3f})")

# Top ball-handler share: max player time-of-poss can't be from tracking_game (no ToP col),
# but we have touches per player. Use that.
g7_player = query("""
    SELECT family_name, first_name, touches, passes, assists, secondary_assists,
           contested_fga, uncontested_fga
    FROM nba_player_tracking_game
    WHERE game_id = %s AND team_tricode = 'MIN' AND minutes_float > 0
    ORDER BY touches DESC
""", (GAME_ID,))
print("\nGame 7 MIN player touches:")
print(g7_player.to_string(index=False))

total_touches = g7_player['touches'].sum()
top_share = g7_player.iloc[0]['touches'] / total_touches if total_touches else 0
print(f"\nTop ball-handler touches share: {top_share:.3f} ({g7_player.iloc[0]['first_name']} {g7_player.iloc[0]['family_name']})")

# Compare top-share to baseline
baseline_top_share = query("""
    SELECT p.game_id, MAX(p.touches)::float / NULLIF(SUM(p.touches),0) AS top_share
    FROM nba_player_tracking_game p
    JOIN nba_games g
      ON g.game_id = p.game_id AND g.team_id = p.team_id
    WHERE p.team_tricode = 'MIN'
      AND g.season_type = 'Regular Season'
      AND g.game_date BETWEEN '2023-10-01' AND '2024-04-30'
      AND p.minutes_float > 0
    GROUP BY p.game_id
""")
print(f"\n2023-24 RS top-touches-share distribution:")
print(baseline_top_share['top_share'].describe().round(3).to_string())
pct_top = (baseline_top_share['top_share'] <= top_share).mean() * 100
print(f"Game 7 top-share percentile: {pct_top:.0f}")
