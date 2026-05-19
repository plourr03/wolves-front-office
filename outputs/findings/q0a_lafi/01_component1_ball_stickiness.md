# Component 1 finding: Ball Stickiness

**Date:** 2026-05-16
**Component:** Ball Stickiness (25% LAFI weight)
**Output:** outputs/tables/q0a_lafi/components/ball_stickiness.csv and ball_stickiness_eye_test.md

## Headline

**The prior was wrong. The Wolves are not especially sticky in 2025-26.**

The 2025-26 Wolves rank at the 30th percentile of all team-seasons in the 2014-15 through 2025-26 sample. The stated prior was top 5 (90th+ percentile). The metric's top/bottom rankings are internally consistent and roster-accurate, so the prior is the thing that needs updating, not the metric.

## What the data showed

**League extremes 2025-26 RS, top 8:** OKC (92), LAL (89), DAL (88), LAC (84), NYK (83), NOP (82), HOU (80), BOS (77).

**Bottom 8:** GSW (0), CHI (5), IND (5), MIA (7), MEM (10), BKN (18), TOR (24), ATL (26).

**Wolves trajectory across seasons:**

| Season | Pct | Top handler |
|---|---|---|
| 2017-18 | 82 | Jeff Teague (Butler/Thibs era) |
| 2019-20 | 14 | D'Angelo Russell |
| 2022-23 | 14 | Mike Conley |
| 2023-24 | 34 | Anthony Edwards (WCF year) |
| **2024-25** | **68** | **Anthony Edwards (Randle year 1)** |
| **2025-26** | **30** | **Anthony Edwards (Randle year 2)** |

The 2024-25 to 2025-26 drop from 68 to 30 is the headline. The thesis predicted the opposite trajectory.

## Three rankings that defied priors, all roster-correct

The eye-test surfaced three rankings that surprised the prior. Drilling in turned each into a roster fact, not a metric error.

1. **ATL at 26th percentile (predicted high).** ATL's top time-of-possession players are Jalen Johnson, CJ McCollum, Dyson Daniels, Nickeil Alexander-Walker. Trae Young is no longer on the roster. The Hawks-should-be-sticky prior was based on a Trae-centric offense that no longer exists.

2. **OKC at 92nd percentile (predicted moderate).** SGA owns 25.5% of team time-of-possession with 5.51 dribbles per touch. Team avg dribbles/touch is 2.61 (elevated). Compared to 2024-25 when Jalen Williams handled more, 2025-26 OKC has concentrated around SGA.

3. **BOS at 77th percentile (predicted lower).** No Jayson Tatum at the top of the time-of-possession leaderboard (Finals injury). Brown, Pritchard, and White have absorbed iso load.

All three were prior failures, not metric failures.

## Why the Wolves' 2025-26 ranking dropped

We do not know yet. Three live hypotheses to test once more components are built:

1. The "feels like pickup" perception lives in the other four components rather than ball stickiness. We will know once Movement Death, Isolation Reliance, Action Poverty, and Shot Quality Decay are computed.
2. The 2024-25 stickiness was driven by Randle integration year 1 when he dominated the ball as the new hub. In 2025-26 the iso load may have decentralized across Edwards, Randle, and others. A team can be more pickup while being less sticky if iso load is spread across three or four guys instead of dominated by one.
3. The metric is right and our perception is partly wrong. Two long-time fans can be wrong about the same team.

## Calibration scorecard

| Prior | Outcome |
|---|---|
| Wolves rank top 5 on Ball Stickiness | Wrong. Wolves at 30th percentile. |
| Wolves trajectory: low in 23-24, rising in 24-25 and 25-26 | Half right. 23-24 was 34 (low). 24-25 was 68 (high). 25-26 was 30 (back down). |
| Hawks should be high (Trae) | Wrong, because Trae was traded. |
| Warriors should be low | Right. GSW at 0th percentile. |

Two priors held, two failed. One of the failures was a stale-roster issue, not a thesis problem.

## Implication for the project

This is a real finding. If the LA-Fitness perception is correct (and the user and Scott both believe it is), it lives somewhere else in the LAFI composite. The remaining four components carry 75% of the weight. The thesis is not dead. It is sharpened: we are now looking specifically at whether Movement Death, Action Poverty, and the others pick up what Ball Stickiness did not.

## Open hypothesis for Phase 5

Compute the variance of time-of-possession share across the top 5 rotation players for each Wolves season. If 2025-26 has lower lead-handler share but more uniform distribution among the top 5 (versus 2024-25 where Randle dominated), that is a different kind of pickup ball: distributed isolation rather than star isolation. This belongs in the Wolves writeup, not the metric.

## What we decided

Proceed to Component 2 without modifying Component 1. The component is mechanically sound. Re-spec moves are off the table until the full composite has run.
