"""Verify stats claimed in section one of articles/02_how_they_got_here_first_draft.md.

Claims (2023-24 MIN Regular Season):
  1. Best defense in the league
  2. Third-best net rating
  3. Offense ranked 17th of 30 in PPP
  4. Full LAFI of 35
  5. Sharp LAFI of 45
  6. Around 13th of 30 in how designed their offense was
  7. Motion death 43
  8. Isolation reliance 49
  9. Shot quality decay 39
  10. Designed actions on 61.9 percent of possessions
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
from lib.db import query
from analyses.q0a_lafi import composite

TEAM = 'MIN'
SEASON_RANGE = ('2023-10-01', '2024-04-30')

# ---- Claims 1-3: team rating ranks ----
# Aggregate per-game advanced ratings into season averages, weighted by possessions
team_adv = query("""
    SELECT t.team_tricode,
           SUM(t.offensive_rating * t.possessions) / NULLIF(SUM(t.possessions), 0) AS ortg,
           SUM(t.defensive_rating * t.possessions) / NULLIF(SUM(t.possessions), 0) AS drtg,
           SUM(t.net_rating * t.possessions) / NULLIF(SUM(t.possessions), 0) AS net_rtg,
           SUM(t.possessions) AS poss,
           COUNT(*) AS gp
    FROM nba_team_advanced_stats t
    JOIN nba_games g
      ON g.game_id = t.game_id AND g.team_id = t.team_id
    WHERE g.season_type = 'Regular Season'
      AND g.game_date BETWEEN %s AND %s
    GROUP BY t.team_tricode
""", SEASON_RANGE)
for c in ('ortg', 'drtg', 'net_rtg'):
    team_adv[c] = team_adv[c].astype(float)
team_adv['drtg_rank']    = team_adv['drtg'].rank(ascending=True,  method='min').astype(int)
team_adv['net_rtg_rank'] = team_adv['net_rtg'].rank(ascending=False, method='min').astype(int)
team_adv['ortg_rank']    = team_adv['ortg'].rank(ascending=False, method='min').astype(int)

print("=" * 72)
print("2023-24 MIN team ratings  (claims 1-3)")
print("=" * 72)
mr = team_adv[team_adv['team_tricode'] == TEAM]
if len(mr) == 0:
    print("  MIN row not found")
else:
    r = mr.iloc[0]
    n = len(team_adv)
    print(f"  DRtg:   {r['drtg']:.2f}   rank {r['drtg_rank']} of {n}     claim: 1st (best defense)")
    print(f"  Net:    {r['net_rtg']:+.2f}   rank {r['net_rtg_rank']} of {n}     claim: 3rd")
    print(f"  ORtg:   {r['ortg']:.2f}   rank {r['ortg_rank']} of {n}    claim: 17th")
    print(f"  Median ORtg: {team_adv['ortg'].median():.2f}   MIN diff vs median: {r['ortg']-team_adv['ortg'].median():+.2f}")
    print(f"  Games:  {int(r['gp'])}")

# ---- Claims 4-9: LAFI ----
print()
print("=" * 72)
print("2023-24 MIN LAFI  (claims 4-9)")
print("=" * 72)
five, _ = composite.assemble_composite(years=[2023], season_types=("Regular Season",))
ml = five[(five['team_abbreviation'] == TEAM) & (five['season_start_year'] == 2023)]
if len(ml) == 0:
    print("  MIN LAFI row not found for 2023-24 RS")
else:
    r = ml.iloc[0]
    n = len(five[five['season_start_year'] == 2023])
    five_2324 = five[five['season_start_year'] == 2023].copy().sort_values('lafi_pct', ascending=True).reset_index(drop=True)
    design_rank = int(five_2324.index[five_2324['team_abbreviation'] == TEAM][0]) + 1
    print(f"  Full LAFI:    {r['lafi_pct']:.1f}   claim: 35")
    print(f"  Sharp LAFI:   {r['sharp_lafi_pct']:.1f}   claim: 45")
    print(f"  Design rank:  {design_rank} of {n}   claim: ~13")
    print(f"  Motion death (C2):       {r['C2_movement_death_pct']:.1f}    claim: 43")
    print(f"  Isolation reliance (C3): {r['C3_isolation_reliance_pct']:.1f}    claim: 49")
    print(f"  Shot quality decay (C5): {r['C5_shot_quality_decay_pct']:.1f}    claim: 39")
    print(f"  Ball stickiness (C1):    {r['C1_ball_stickiness_pct']:.1f}    (article elsewhere claims 35)")
    print(f"  Action poverty (C4):     {r['C4_action_poverty_pct']:.1f}    (article elsewhere claims 27)")

# ---- Claim 10: designed-actions share ----
print()
print("=" * 72)
print("2023-24 MIN designed-actions share  (claim 10)")
print("=" * 72)
syn = query("""
    SELECT play_type, type_grouping, SUM(poss) AS poss
    FROM nba_synergy_team_play_types
    WHERE team_abbreviation = %s
      AND season_year = '2023-24'
      AND season_type = 'Regular Season'
    GROUP BY play_type, type_grouping
    ORDER BY type_grouping, poss DESC
""", (TEAM,))
print("Per-play-type possessions (by type_grouping):")
print(syn.to_string(index=False))
# offensive only
off = syn[syn['type_grouping'].str.lower() == 'offensive'].copy()
total_off = off['poss'].sum()
print(f"\nTotal offensive possessions tracked: {total_off:.0f}")
# Two candidate definitions of "designed actions"
iso_poss = off[off['play_type'].str.lower().str.contains('isolation')]['poss'].sum()
nonpass = ['Isolation', 'Transition']  # transition is often excluded
nonscripted = off[~off['play_type'].isin(nonpass)]['poss'].sum() if not off.empty else 0
print(f"\nCandidate definitions of 'designed':")
print(f"  1 - iso_share:                  {100*(total_off-iso_poss)/total_off:.1f}%   (claim: 61.9%)")
print(f"  excluding iso + transition:     {100*nonscripted/total_off:.1f}%")
# Per play-type shares so we can think about other groupings
print("\nPer play-type share of offensive possessions:")
off_sorted = off.assign(share_pct=100 * off['poss'] / total_off).sort_values('share_pct', ascending=False)
print(off_sorted[['play_type', 'poss', 'share_pct']].to_string(index=False))
