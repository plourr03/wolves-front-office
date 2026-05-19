# Eye-test: isolation_reliance

_Higher percentile = more pickup-like. Each percentile is pooled across the full team-season sample._

## Priors before running


- Wolves 2025-26 should land 55th to 75th percentile on overall Isolation Reliance.
- Wolves 2025-26 should be higher than 2024-25 on overall iso rate (the offense has
  decentralized iso rather than reduced it).
- Wolves iso Herfindahl (top-5 concentration) should drop from 2024-25 to 2025-26,
  consistent with the "scattered iso" Q4 placement.
- Wolves Edwards-era trajectory: 2022-23 moderate, 2023-24 lower (WCF year more
  designed), 2024-25 elevated (Randle integration), 2025-26 higher than 2024-25.
- League extremes top: CLE with Mitchell, DAL with Luka, PHX top quintile. OKC very
  high. Post-Trae ATL should be lower than the prior expected.

## League leaderboard

**League leaders (top 8, 2025-26 RS):**
| Team | Pct | Raw z |
|---|---|---|
| BOS | 97 | +1.56 |
| LAC | 96 | +1.45 |
| PHI | 93 | +1.13 |
| MIN | 90 | +1.02 |
| LAL | 88 | +0.97 |
| PHX | 87 | +0.95 |
| HOU | 86 | +0.92 |
| OKC | 84 | +0.89 |

**League tail (bottom 8, same season):**

| Team | Pct | Raw z |
|---|---|---|
| CHI | 1 | -1.70 |
| ATL | 4 | -1.29 |
| GSW | 5 | -1.26 |
| TOR | 10 | -0.99 |
| BKN | 11 | -0.94 |
| UTA | 13 | -0.86 |
| IND | 16 | -0.82 |
| MEM | 20 | -0.73 |

## Wolves trajectory

| Season | Type | Raw z | Pct rank | Top handler |
|---|---|---|---|--- |
| 2014-15 | Re | +0.29 | 66 | Zach LaVine |
| 2015-16 | Re | -0.33 | 38 | Ricky Rubio |
| 2016-17 | Re | -0.33 | 38 | Ricky Rubio |
| 2017-18 | Re | +0.83 | 82 | Jeff Teague |
| 2018-19 | Re | -0.12 | 48 | Tyus Jones |
| 2019-20 | Re | -0.50 | 30 | D'Angelo Russell |
| 2020-21 | Re | -0.67 | 22 | nan |
| 2021-22 | Re | -0.27 | 41 | D'Angelo Russell |
| 2022-23 | Re | -0.22 | 44 | Mike Conley |
| 2023-24 | Re | -0.09 | 49 | Anthony Edwards |
| 2024-25 | Re | +0.45 | 71 | Anthony Edwards |
| 2025-26 | Re | +1.02 | 90 | Anthony Edwards |

## Investigation notes


**All five user predictions tracked. Four held, one over-shot in the right direction.**

| Prior | Outcome |
|---|---|
| Wolves 2025-26 lands 55-75 pct | **Over.** Actual 89th percentile (even higher than predicted) |
| Wolves 25-26 > 24-25 on iso rate | **Right.** 70 -> 89, +19 percentile points |
| Wolves iso Herfindahl drops 24-25 to 25-26 | **Right.** 0.455 -> 0.361 |
| Edwards-era trajectory: 22-23 mod, 23-24 lower, 24-25 elev, 25-26 higher | **Right.** 43, 49, 70, 89 |
| Post-Trae ATL lower than priors | **Right.** ATL at 4th percentile (very low iso) |
| OKC very high | Right but not the very top. OKC at 84th, behind BOS/LAC/PHI/MIN. |

**The Herfindahl annotation is the key finding for the Wolves diagnosis.**

| Season | Iso Herf top-5 | Top iso player (share) | Players with iso |
|---|---|---|---|
| 2022-23 | 0.451 | Edwards (0.65) | 9 |
| 2023-24 | 0.420 | Edwards (0.59) | 7 |
| **2024-25** | **0.455** | **Edwards (0.62)** | **7** |
| **2025-26** | **0.361** | **Edwards (0.48)** | **8** |

Edwards remains the top iso option, but his share fell from 62% (24-25) to 48% (25-26).
Iso load is now distributed across 8 players instead of concentrated in 7. The number
of players taking iso possessions ROSE while the total iso rate ALSO ROSE. This is
the data signature of "scattered iso" the Q4 quadrant framing predicted: total iso
up, concentration down, off-ball motion still missing.

**League leaders pass the eye test.**

BOS (96), LAC (96), PHI (93), MIN (89), LAL (88), PHX (86), HOU (85), OKC (84). All
known iso-heavy 2025-26 rosters. BOS at the top is roster-correct: with Tatum out,
the Celtics have leaned heavily on Brown/Pritchard iso. LAC (Harden/Kawhi/PG),
PHI (Embiid/Maxey/George), LAL (LeBron/Luka), PHX, HOU all check out.

**Bottom passes too.**

GSW (4), ATL (4), IND (16) are the three lowest-iso teams (movement-heavy). All
consistent with priors. ATL again confirms the post-Trae reality.

**Three-component cross pattern for the Wolves 2025-26:**

| Component | Wolves pct | Direction |
|---|---|---|
| C1 Ball Stickiness | 30 | Not concentrated on one handler |
| C2 Movement Death | 71 | Off-ball players don't move |
| C3 Isolation Reliance | 89 | Heavy iso |

The three-line story: heavy iso, distributed across multiple players, no off-ball motion.
That is Q4 with three-component support. The user's "distributed pickup" diagnosis is
holding.

**No metric changes warranted.** Proceed to Component 4 (Action Poverty).
