"""Verify Game 7 Wolves @ Nuggets 2024 playoffs narrative.

Article claim: "Going into Denver and winning Game 7 after trailing by 20"
We need to confirm:
  1. The game was in Denver (away game)
  2. Wolves won
  3. They trailed by ~20 at some point
"""
from lib.db import query

GAME_ID = '0042300237'

# Pull score progression
pbp = query("""
    SELECT period, clock, team_tricode, score_home, score_away,
           description, action_type
    FROM nba_play_by_play
    WHERE game_id = %s
    ORDER BY action_number
""", (GAME_ID,))

print(f"Total PBP events: {len(pbp)}")
print(f"Final score: home(DEN)={pbp.iloc[-1]['score_home']}, away(MIN)={pbp.iloc[-1]['score_away']}")
print()

# Compute MIN's running margin (away - home)
import pandas as pd
pbp['score_home'] = pd.to_numeric(pbp['score_home'], errors='coerce').ffill().fillna(0).astype(int)
pbp['score_away'] = pd.to_numeric(pbp['score_away'], errors='coerce').ffill().fillna(0).astype(int)
pbp['period'] = pbp['period'].astype(int)
pbp['min_margin'] = pbp['score_away'] - pbp['score_home']

# Per-quarter min/max margin
print("Per-period MIN margin range (away - home, negative = trailing):")
for period in sorted(pbp['period'].unique()):
    p = pbp[pbp['period'] == period]
    print(f"  Q{period}: min={p['min_margin'].min()}, max={p['min_margin'].max()}, "
          f"end-of-period={p.iloc[-1]['score_away']}-{p.iloc[-1]['score_home']}")

# Find the largest deficit
max_deficit_idx = pbp['min_margin'].idxmin()
mx = pbp.loc[max_deficit_idx]
print(f"\nMax deficit: MIN trailed by {-mx['min_margin']} (DEN {mx['score_home']} - MIN {mx['score_away']})")
print(f"  At Q{mx['period']}, clock {mx['clock']}")
print(f"  Event: {mx['description']}")

# Score at end of each period
print("\nScore by end of period:")
for period in sorted(pbp['period'].unique()):
    p = pbp[pbp['period'] == period]
    last = p.iloc[-1]
    print(f"  End Q{period}: DEN {last['score_home']} - MIN {last['score_away']} (margin {last['min_margin']})")

# Halftime score
half = pbp[pbp['period'] <= 2].iloc[-1]
print(f"\nHalftime: DEN {half['score_home']} - MIN {half['score_away']} (MIN trails by {-half['min_margin']})")

end_q3 = pbp[pbp['period'] <= 3].iloc[-1]
print(f"End Q3: DEN {end_q3['score_home']} - MIN {end_q3['score_away']} (margin {end_q3['min_margin']})")
