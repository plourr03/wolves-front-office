# Cross-component pattern matrix

**Live document.** Updated after each component build.

**Last updated:** 2026-05-16 (Phase 2 complete; all five components built)

## The framework (Q1 to Q4 quadrants)

| Quadrant | (C1 sticky, C2 motion-death) | Archetype | What it looks like |
|---|---|---|---|
| **Q1: Designed** | low, low | Warriors (Steph/Dray), Pacers, post-Trae Hawks | Ball moves, bodies move. Gold standard. |
| **Q2: Star-fed motion** | high, low | Brunson Knicks | One creator dominates ball, everyone else moves. |
| **Q3: Single-star pickup** | high, high | Harden Rockets, LAC, PHI, OKC, LAL | Star isolates, everyone watches. Classic pickup. |
| **Q4: Distributed pickup** | low, high | Wolves 2025-26 | Multiple players take iso turns, nobody moves. |

## Wolves Edwards-era five-component trajectory

| Season | C1 sticky | C2 motion-death | C3 iso-rel | C4 action-pov (v1) | C5 shot-qual decay | Iso Herf | Top handler |
|---|---|---|---|---|---|---|---|
| 2022-23 | 14 | 63 | 43 | 30 | 46 | 0.451 | Mike Conley |
| 2023-24 | 34 | **43** | 49 | 27 | 39 | 0.420 | Anthony Edwards |
| 2024-25 | **68** | 55 | 70 | 35 | 71 | **0.455** | Anthony Edwards |
| **2025-26** | **30** | **71** | **89** | **45** | **82** | **0.361** | Anthony Edwards |

**Reading the trajectory:**

- 2023-24 was the lowest year on every "pickup" component. Q1-leaning. The WCF year.
- 2024-25 lifted on C1, C3, C5 simultaneously. Q3-leaning, Randle integration year, iso concentrated (Herf 0.455).
- 2025-26 moved further on C2, C3, C5. C1 dropped (iso decentralized). C4 lifted slightly but stayed moderate. **Q4 (distributed pickup) with degraded shot quality, normal-breadth playbook, dead off-ball motion.**

The Edwards-era progression on each "pickup" component:
- C2 motion-death: 43 -> 55 -> 71
- C3 iso-reliance: 49 -> 70 -> 89
- C5 shot quality decay: 39 -> 71 -> 82

Three components moved in lockstep. C1 and C4 did not. The "feels like pickup" perception lives in those three.

## Composite preview (manual math, full Phase 3 in next step)

Weighted percentile sum:
```
0.25 * 30 + 0.20 * 71 + 0.20 * 89 + 0.20 * 45 + 0.15 * 82
  = 7.50 + 14.20 + 17.80 + 9.00 + 12.30
  = 60.80
```

Wolves' raw weighted percentile: ~61. The actual LAFI composite after re-ranking the weighted z-scores across the sample will be similar but not identical. Phase 3 produces the canonical number.

**The story has shifted:**
- Original thesis: Wolves top 5 on LAFI league-wide.
- Data: Wolves mid-60s percentile on LAFI composite.
- **Refined headline: Wolves play pickup ball on the specific dimensions that break offenses in May (motion death, iso reliance, shot quality decay). Not LAFI-extreme on every component, but extreme on the ones that matter.**

## League extremes 2025-26 RS, five-component placement

| Team | C1 | C2 | C3 | C4 | C5 | Quadrant read |
|---|---|---|---|---|---|---|
| GSW | 0 | 2 | 4 | 2 | 19 | **Q1 extreme.** Designed on every component. |
| SAS | (TBD) | (TBD) | (TBD) | 14 | **11** | **Q1-leaning.** Wembanyama anchored design. |
| IND | 5 | 24 | 16 | (low) | (TBD) | Q1. Pacers motion. |
| ATL | 26 | 15 | 4 | 16 | 17 | **Q1 post-Trae.** Cleanly designed post-trade. |
| BOS | 77 | 23 | 96 | (moderate) | **98** | **Q2 hybrid.** Sticky+iso+bad shots but bodies still move. Tatum-out signature. |
| LAC | 84 | 51 | 96 | **92** | 77 | **Q3+narrow.** Sticky+iso+narrow playbook. The LAC route to high iso. |
| PHI | 86 | 86 | 93 | 45 | (TBD) | **Q3 extreme.** Iso volume with sticky handlers. |
| LAL | 89 | (TBD) | 88 | 82 | 94 | Q3-likely with narrow playbook and bad shots. |
| OKC | 92 | (TBD) | 84 | 29 | (TBD) | Q3-leaning, SGA-concentrated, broad playbook. |
| MIL | (TBD) | 88 | (TBD) | (low) | (TBD) | Q3 or Q4, Giannis-driven. |
| **MIN** | **30** | **71** | **89** | **45** | **82** | **Q4. Distributed iso, no motion, bad shots, normal-breadth playbook.** |

## The LAC vs MIN comparison, expanded

The two iso-heavy teams reached high iso volume by opposite routes:

| Component | LAC | MIN | Read |
|---|---|---|---|
| C1 Ball Stickiness | 84 | 30 | LAC concentrated, MIN distributed |
| C2 Movement Death | 51 | 71 | LAC moves, MIN doesn't |
| C3 Iso Reliance | 96 | 89 | Both extreme |
| C4 Action Poverty (v1) | 92 | 45 | LAC narrow playbook, MIN broad |
| C5 Shot Quality Decay | 77 | 82 | Both have bad shot diet |

**Same destination (high iso, bad shots), opposite roads.** LAC: sticky handlers running a narrow playbook. MIN: distributed touches running a broad playbook but choosing iso anyway.

Implication for prescription:
- LAC's iso problem is fixable by roster construction (more shooters and movement guys around the iso stars).
- MIN's iso problem is harder because the playbook is already there but isn't being used. Adding more designed actions to MIN's playbook would not help; the actions already exist. The team isn't running them.

This is a Q5 (prescription) insight, captured here so it doesn't get lost.

## The Spurs structural counterargument

SAS at 14 (Action Poverty bottom) and 11 (Shot Quality Decay bottom). The Spurs are designed AND generate good shots. Combined with elite rim protection at Wembanyama, they are the structural counterargument to the Wolves at both ends of the floor. This is exactly the matchup architecture the Q4 framing predicts to break the Wolves. The series outcome is consistent.

## Cumulative calibration across all 5 components

| Component | Priors | Right | Wrong |
|---|---|---|---|
| C1 Ball Stickiness | 4 | 1 | 3 |
| C2 Movement Death | 5 | 3 | 2 |
| C3 Isolation Reliance | 5 | 4 | 1 |
| C4 Action Poverty | 4 | 1 | 3 |
| C5 Shot Quality Decay | 4 | 2 | 2 |
| **Totals** | **22** | **11** | **11** |

50% accuracy across 22 priors. Pattern confirmed: directional / structural predictions hold better than magnitude predictions. The wrong priors cluster on "how extreme will the Wolves be on this specific component" and "is this 2025-26 roster of team X still the team I'm picturing."

The 50% number is a feature, not a bug. The findings folder is the artifact that makes this credible: every prior is logged, every miss is documented, every correction is traceable. Most public analysts present conclusions without showing how often they're wrong.

## What's next

Phase 3 (composite, correlation matrix, PCA diagnostics) is queued. Per user instruction, pause for synthesis discussion before kicking off.

The two specific things the user said to preserve in the final writeup:
1. The refined diagnosis ("normal-breadth playbook with bad allocation"), not the original "they only run a couple of things."
2. The LAC vs MIN contrast (same destination, opposite roads).

Both captured here and in the C4 findings markdown for posterity.
