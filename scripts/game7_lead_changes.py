"""Lead changes in Q4 of Wolves @ Nuggets Game 7, 2024 playoffs."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
from lib.db import query

GAME_ID = '0042300237'

pbp = query("""
    SELECT action_number, period, clock, team_tricode, score_home, score_away,
           description, action_type, sub_type, player_name, shot_result, shot_value
    FROM nba_play_by_play
    WHERE game_id = %s AND period = 4
    ORDER BY action_number
""", (GAME_ID,))

pbp['score_home'] = pd.to_numeric(pbp['score_home'], errors='coerce').ffill().fillna(0).astype(int)
pbp['score_away'] = pd.to_numeric(pbp['score_away'], errors='coerce').ffill().fillna(0).astype(int)
# MIN is away
pbp['margin'] = pbp['score_away'] - pbp['score_home']  # positive = MIN leads

# Identify lead direction: +1 MIN, -1 DEN, 0 tied
def lead_side(m):
    if m > 0: return 'MIN'
    if m < 0: return 'DEN'
    return 'TIE'
pbp['lead'] = pbp['margin'].apply(lead_side)

# A "lead change" is when the leading team flips (DEN <-> MIN). Going through TIE in between counts.
# Iterate to find transitions away from "TIE" that go to the OTHER team than the last non-tie lead.
changes = []
last_real_lead = None  # track who was leading most recently (not tie)
for i, row in pbp.iterrows():
    cur = row['lead']
    if cur == 'TIE':
        continue
    if last_real_lead is None:
        # first non-tie state in Q4 — at the start MIN trailed by 1 (entering Q4 67-66 DEN)
        last_real_lead = cur
        continue
    if cur != last_real_lead:
        changes.append({
            'clock': row['clock'],
            'new_leader': cur,
            'score_min': row['score_away'],
            'score_den': row['score_home'],
            'margin': row['margin'],
            'scorer': row['player_name'],
            'description': row['description'],
        })
        last_real_lead = cur

# Format clock from ISO PT##M##S
def fmt(c):
    if not isinstance(c, str): return c
    s = c.replace('PT','').replace('S','')
    if 'M' in s:
        m, ss = s.split('M')
        return f"{int(m):02d}:{float(ss):05.2f}"
    return c

print("Entering Q4: DEN 67, MIN 66 (DEN leads by 1)")
print()
print(f"Lead changes in Q4 (excluding ties):")
print()
for ch in changes:
    print(f"  {fmt(ch['clock']):>8}  {ch['new_leader']} {ch['score_min']}-{ch['score_den']}  "
          f"({ch['scorer']})  --  {ch['description']}")

# Also show ties for context
print()
print("All score-flip-relevant events in Q4 (TIE moments included):")
last = None
for i, row in pbp.iterrows():
    if row['lead'] != last:
        if row['lead'] == 'TIE' or last == 'TIE' or row['lead'] != last:
            print(f"  {fmt(row['clock']):>8}  {row['lead']:>3}  {row['score_away']:>3}-{row['score_home']:>3}  "
                  f"({row['player_name'] or '-'})  --  {row['description']}")
        last = row['lead']
