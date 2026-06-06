"""Build the narrative of Wolves @ Nuggets Game 7, 2024 playoffs from PBP."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
from lib.db import query

GAME_ID = '0042300237'

pbp = query("""
    SELECT action_number, period, clock, team_tricode, score_home, score_away,
           description, action_type, sub_type, player_name, is_field_goal, shot_value
    FROM nba_play_by_play
    WHERE game_id = %s
    ORDER BY action_number
""", (GAME_ID,))

pbp['score_home'] = pd.to_numeric(pbp['score_home'], errors='coerce').ffill().fillna(0).astype(int)
pbp['score_away'] = pd.to_numeric(pbp['score_away'], errors='coerce').ffill().fillna(0).astype(int)
pbp['min_margin'] = pbp['score_away'] - pbp['score_home']

# Player scoring totals
print("=" * 70)
print("WOLVES @ NUGGETS, Game 7, May 19 2024 — Final: MIN 98, DEN 90")
print("=" * 70)

# Pull box-score-style per-player from nba_player_stats
ps = query("""
    SELECT team_abbreviation, player_name, pts, reb, ast, stl, blk, tov,
           fgm, fga, fg3m, fg3a, ftm, fta, plus_minus, minutes_played
    FROM nba_player_stats
    WHERE game_id = %s
    ORDER BY team_abbreviation, pts DESC
""", (GAME_ID,))
print("\nMIN scorers (sorted by pts):")
print(ps[ps['team_abbreviation']=='MIN'][['player_name','pts','reb','ast','fgm','fga','fg3m','fg3a','plus_minus','minutes_played']].to_string(index=False))
print("\nDEN scorers (sorted by pts):")
print(ps[ps['team_abbreviation']=='DEN'][['player_name','pts','reb','ast','fgm','fga','fg3m','fg3a','plus_minus','minutes_played']].to_string(index=False))

# Quarter scores
print("\n" + "=" * 70)
print("QUARTER SCORES")
print("=" * 70)
for p in [1,2,3,4]:
    quarter = pbp[pbp['period'].astype(int) == p]
    prev = pbp[pbp['period'].astype(int) == p-1]
    if len(prev) > 0:
        prev_home, prev_away = prev.iloc[-1]['score_home'], prev.iloc[-1]['score_away']
    else:
        prev_home, prev_away = 0, 0
    last = quarter.iloc[-1]
    q_den = last['score_home'] - prev_home
    q_min = last['score_away'] - prev_away
    print(f"  Q{p}: MIN {q_min} - DEN {q_den}  (cumulative: MIN {last['score_away']} - DEN {last['score_home']}, margin {last['min_margin']:+d})")

# Find max deficit moment
mx = pbp.loc[pbp['min_margin'].idxmin()]
print(f"\nLargest deficit: MIN trailed by {-mx['min_margin']} (DEN {mx['score_home']} - MIN {mx['score_away']})")
print(f"  Period: Q{mx['period']}, clock {mx['clock']}")
print(f"  Triggering event: {mx['description']}")

# Find when MIN first tied / took lead
zero_or_lead = pbp[pbp['min_margin'] >= 0]
first_tie = zero_or_lead[zero_or_lead['period'].astype(int) >= 3].iloc[0] if len(zero_or_lead[zero_or_lead['period'].astype(int) >= 3]) else None
print(f"\nFirst tie/lead from Q3 onward: Q{first_tie['period']} clock {first_tie['clock']}  ({first_tie['score_away']}-{first_tie['score_home']})  -> {first_tie['description']}")

# Find first MIN lead in Q4
q4_leads = pbp[(pbp['period'].astype(int) == 4) & (pbp['min_margin'] > 0)]
if len(q4_leads) > 0:
    first_q4_lead = q4_leads.iloc[0]
    print(f"\nFirst MIN lead in Q4: clock {first_q4_lead['clock']}  ({first_q4_lead['score_away']}-{first_q4_lead['score_home']})  -> {first_q4_lead['description']}")

# Q4 scoring breakdown by player (MIN)
print("\n" + "=" * 70)
print("Q4 SCORING — who carried the comeback")
print("=" * 70)
q4 = pbp[(pbp['period'].astype(int) == 4) & (pbp['is_field_goal'] == True) & (pbp['shot_result'] == 'Made' if 'shot_result' in pbp.columns else True)]
# Refetch with shot_result + made/missed
q4_pbp = query("""
    SELECT period, clock, team_tricode, score_home, score_away,
           description, action_type, sub_type, player_name, shot_result, shot_value
    FROM nba_play_by_play
    WHERE game_id = %s AND period = 4
    ORDER BY action_number
""", (GAME_ID,))
q4_made = q4_pbp[q4_pbp['shot_result'] == 'Made']
print("\nQ4 made FGs by player (MIN):")
min_q4 = q4_made[q4_made['team_tricode'] == 'MIN'].copy()
min_q4['pts'] = min_q4['shot_value'].fillna(2).astype(int)
agg = min_q4.groupby('player_name')['pts'].agg(['sum','count']).sort_values('sum', ascending=False)
agg.columns = ['Q4_pts', 'Q4_FGM']
print(agg.to_string())

# Free throws Q4
ft = q4_pbp[q4_pbp['action_type'].str.contains('Free Throw', na=False, case=False) & (q4_pbp['shot_result'] == 'Made')]
ft_min = ft[ft['team_tricode'] == 'MIN']
print("\nQ4 made FTs by player (MIN):")
print(ft_min.groupby('player_name').size().to_string())
