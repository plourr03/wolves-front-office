# Eye-test: movement_death

_Higher percentile = more pickup-like. Each percentile is pooled across the full team-season sample._

## Priors before running


- The thesis predicts the 2025-26 Wolves should rise meaningfully on Movement Death
  versus the 2023-24 WCF year. "No off-ball motion" is one of the strongest pieces
  of the LA-Fitness perception.
- Expected high (low movement): heavy-iso teams, ball-dominant offenses.
- Expected low (lots of movement): Warriors with Steph, Celtics motion, Pacers,
  Nuggets system around Jokic.
- Stated prior for the Wolves: rise from 2023-24 (KAT era, motion) to 2025-26
  (Randle era, less motion).

## League leaderboard

**League leaders (top 8, 2025-26 RS):**
| Team | Pct | Raw z |
|---|---|---|
| MIL | 89 | +0.73 |
| POR | 87 | +0.65 |
| PHI | 86 | +0.63 |
| NOP | 85 | +0.63 |
| CHI | 85 | +0.63 |
| MEM | 84 | +0.60 |
| MIA | 83 | +0.59 |
| HOU | 78 | +0.44 |

**League tail (bottom 8, same season):**

| Team | Pct | Raw z |
|---|---|---|
| GSW | 3 | -1.58 |
| UTA | 5 | -1.15 |
| BKN | 10 | -0.75 |
| DET | 14 | -0.62 |
| ATL | 16 | -0.57 |
| TOR | 18 | -0.53 |
| BOS | 23 | -0.44 |
| IND | 25 | -0.41 |

## Wolves trajectory

| Season | Type | Raw z | Pct rank | Top handler |
|---|---|---|---|--- |
| 2014-15 | Re | -0.50 | 19 | Zach LaVine |
| 2015-16 | Re | +0.09 | 52 | Ricky Rubio |
| 2016-17 | Re | +0.46 | 78 | Ricky Rubio |
| 2017-18 | Re | +0.66 | 87 | Jeff Teague |
| 2018-19 | Re | +0.38 | 73 | Tyus Jones |
| 2019-20 | Re | +0.41 | 76 | D'Angelo Russell |
| 2021-22 | Re | +0.33 | 69 | D'Angelo Russell |
| 2022-23 | Re | +0.23 | 64 | Mike Conley |
| 2023-24 | Re | -0.01 | 43 | Anthony Edwards |
| 2024-25 | Re | +0.13 | 55 | Anthony Edwards |
| 2025-26 | Re | +0.36 | 72 | Anthony Edwards |

## Investigation notes


**The Wolves trajectory matches the stated prior cleanly.**

| Season | Pct | Top handler | Note |
|---|---|---|---|
| 2017-18 | 87 | Jeff Teague | Butler/Thibs peak iso era. |
| 2019-20 | 76 | D'Angelo Russell | KAT/Russell pre-Gobert. |
| 2022-23 | 63 | Mike Conley | First Gobert year. |
| 2023-24 | **43** | Anthony Edwards | WCF year, KAT gravity. Most movement of the Edwards era. |
| 2024-25 | **55** | Anthony Edwards | Randle year 1. Slight rise. |
| 2025-26 | **71** | Anthony Edwards | Randle year 2. Clear movement drop. |

The 28-percentile-point jump from 2023-24 (43) to 2025-26 (71) is a real signal. The
"no off-ball motion this year" perception is data-supported on this component.

**Cross-component pattern emerging.**

The Wolves' two-component profile so far:

- Component 1 (Ball Stickiness): 2025-26 RS = 30th percentile (moderate-low)
- Component 2 (Movement Death):  2025-26 RS = 71st percentile (high pickup)

The team is NOT especially sticky around a single handler, but the four off-ball
players are not moving. That is a specific kind of pickup ball: scattered iso
attempts by multiple players while the rest stand and watch. Different from
Brunson-NYK (sticky with motion) or Trae-era Hawks (sticky and no motion).

If Components 3 through 5 also show the Wolves elevated, the working synthesis
becomes: "The Wolves' LA Fitness problem is not ball stickiness; it's action
poverty and movement death." That is a sharper finding than the original thesis
and points to specific fixes (designed off-ball architecture) rather than the
vaguer "less iso."

**Other findings worth flagging.**

- **GSW at 2nd percentile.** Steph/Draymond motion. Sanity-passes the spec.
- **IND at 24th, BOS at 23rd, ATL at 15th.** The three lowest LAFI-pickup teams on
  movement. ATL's low rank confirms the post-Trae roster: not only did stickiness
  drop (Component 1, 26th pct), they actually move now.
- **MIA at 83rd percentile (predicted lower).** Heat were a movement team under
  prior rosters. The current iteration is more iso-driven than the brand suggests.
  Worth a roster check.
- **MIL at 88th, NOP at 85th, PHI at 86th.** Giannis, Zion, and Embiid-driven
  offenses respectively. All plausibly low on off-ball motion.

**No metric changes warranted.** The component is internally consistent, the
rankings are roster-plausible, and the Wolves trajectory directly supports a
working hypothesis. Proceed to Component 3 (Isolation Reliance).
