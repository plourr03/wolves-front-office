# Eye-test: ball_stickiness

_Higher percentile = more pickup-like. Each percentile is pooled across the full team-season sample._

## Priors before running


- The thesis predicts the 2025-26 Wolves should rank high (top 5) on stickiness.
- Expected high: heavy ball-dominant stars. Hawks (Trae), Mavs (Luka), Knicks (Brunson).
- Expected low: pass-heavy systems. Pacers, prior-Warriors (Steph/Draymond), Thunder pre-2024-25.
- Wolves trajectory prior: should dip in 2023-24 (WCF year, KAT gravity), rise in 2024-25 and 2025-26 post-Randle.

## League leaderboard

**League leaders (top 8, 2025-26 RS):**
| Team | Pct | Raw z |
|---|---|---|
| OKC | 92 | +1.17 |
| LAL | 89 | +0.98 |
| DAL | 88 | +0.95 |
| LAC | 85 | +0.86 |
| NYK | 83 | +0.80 |
| NOP | 82 | +0.75 |
| HOU | 80 | +0.66 |
| BOS | 78 | +0.59 |

**League tail (bottom 8, same season):**

| Team | Pct | Raw z |
|---|---|---|
| GSW | 1 | -1.87 |
| CHI | 5 | -1.28 |
| IND | 6 | -1.27 |
| MIA | 8 | -1.12 |
| MEM | 11 | -0.96 |
| BKN | 19 | -0.71 |
| TOR | 25 | -0.53 |
| ATL | 27 | -0.49 |

## Wolves trajectory

| Season | Type | Raw z | Pct rank | Top handler |
|---|---|---|---|--- |
| 2014-15 | Re | +0.39 | 71 | Zach LaVine |
| 2015-16 | Re | +0.74 | 81 | Ricky Rubio |
| 2016-17 | Re | +0.55 | 76 | Ricky Rubio |
| 2017-18 | Re | +0.79 | 83 | Jeff Teague |
| 2018-19 | Re | -0.16 | 42 | Tyus Jones |
| 2019-20 | Re | -0.82 | 15 | D'Angelo Russell |
| 2021-22 | Re | -0.42 | 29 | D'Angelo Russell |
| 2022-23 | Re | -0.84 | 14 | Mike Conley |
| 2023-24 | Re | -0.32 | 35 | Anthony Edwards |
| 2024-25 | Re | +0.32 | 69 | Anthony Edwards |
| 2025-26 | Re | -0.38 | 31 | Anthony Edwards |

## Investigation notes


The eye-test surfaced three rankings that defied the priors. All three turned out
to be data-correct and prior-incorrect.

**ATL at 26th percentile (predicted high).** ATL's top time-of-possession players
in 2025-26 are Jalen Johnson, CJ McCollum, Dyson Daniels, Nickeil Alexander-Walker.
Trae Young is no longer on the roster. The "Hawks should be sticky" prior was
based on a Trae-centric offense that no longer exists.

**OKC at 92nd percentile (predicted moderate).** SGA owns 25.5% of team time-of-
possession with 5.51 dribbles per touch. The team avg is 2.61 drib/touch (elevated).
Compared to 2024-25 when Jalen Williams handled more, 2025-26 OKC has concentrated
around SGA. The "OKC is a movement team" mental model is from prior seasons.

**BOS at 77th percentile (predicted lower).** Top time-of-possession players are
Pritchard, White, Brown. Jayson Tatum is absent from the top of the list (recovering
from Finals injury). Without Tatum's gravity, the Celtics have leaned on Brown/
Pritchard iso, raising stickiness.

In all three cases the metric was right and the prior was based on outdated rosters.

**Wolves trajectory finding (the headline of this component).**

The 2024-25 -> 2025-26 drop from 68th to 30th percentile contradicts the LAFI thesis
on this component. The thesis predicted 2025-26 should be high on stickiness.

Possible explanations for Phase 5 to investigate:

1. The "feels like pickup" perception lives in the other four components
   (no off-ball motion, no actions, predictable shots) rather than ball stickiness.
2. The 2024-25 stickiness was driven by Randle integration year 1, when he dominated
   the ball as the new offensive hub. In 2025-26 the iso load may have decentralized
   across Ant + Randle + others, which would lower the lead-handler concentration
   metric without actually making the team more designed.
3. A team can be more "pickup" while being less "sticky" if the iso load is spread
   across three or four players instead of dominated by one.

**Open hypothesis for Phase 5 (do not change Component 1 over this):**

Compute the variance of time-of-possession share across the top 5 rotation players
for each Wolves season. If 2025-26 has lower lead-handler share but more uniform
distribution among the top 5 (versus 2024-25 where Randle dominated), that is a
different kind of pickup ball. This belongs in the Wolves writeup, not in the
metric construction.

**Conclusion for the build.** Component 1 measures what it claims to measure. Its
top/bottom rankings are internally consistent and roster-accurate. The Wolves'
2025-26 stickiness ranking is an honest finding even if it complicates the thesis.
Proceed to Component 2 and let the composite tell the full story.
