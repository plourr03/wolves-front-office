# Component 4 finding: Action Poverty (v1)

**Date:** 2026-05-16
**Component:** Action Poverty (20% LAFI weight)
**Status:** v1 with Synergy proxies. Full action classifier (v2) deferred.
**Output:** outputs/tables/q0a_lafi/components/action_poverty.csv and action_poverty_eye_test.md

## Headline

**Wolves 2025-26 landed at 45th percentile. The user's prior was 80-95.**

Below the "investigate if below 70" threshold. The investigation produced a substantive finding, not a v1 proxy fix. The Q4 diagnosis needs refining, not the metric.

## What we found by drilling into the play-type breakdown

The Wolves 2025-26 Synergy distribution against the league:

| Team | Cut+OffScr | Handoff | Spotup | Iso | PRBH | Post |
|---|---|---|---|---|---|---|
| **MIN** | **0.102** | 0.057 | **0.229** | **0.096** | **0.131** | 0.041 |
| LAC | 0.089 | 0.034 | 0.219 | 0.116 | 0.151 | 0.056 |
| LAL | 0.130 | 0.022 | 0.199 | 0.085 | 0.170 | 0.055 |
| PHI | 0.095 | 0.040 | 0.230 | 0.099 | 0.141 | 0.039 |
| BOS | 0.103 | 0.053 | 0.231 | 0.096 | 0.183 | 0.020 |
| GSW | 0.161 | 0.041 | 0.267 | 0.055 | 0.128 | 0.028 |
| IND | 0.104 | 0.041 | 0.258 | 0.050 | 0.163 | 0.040 |
| ATL | 0.132 | 0.060 | 0.223 | 0.042 | 0.147 | 0.028 |

**The Wolves' off-ball motion (Cut + OffScreen) is 10.2%. That's roughly league-average.** It's within a percentage point of BOS, IND, and PHI. GSW and ATL are higher, but the Wolves are not abnormally low.

What IS distinctive about the Wolves:

- **Low PR-Ball-Handler share (13.1%).** League high-iso teams run 14-18%.
- **High Iso share (9.6%).** Top quartile, matching what Component 3 already showed.
- **Low Spotup share (22.9%).** Below league average. Surprising given the "kick out off iso" intuition.

## Wolves year-over-year Synergy detail

| Season | Cut+OffScr | Handoff | Spotup | Iso | PRBH | Post |
|---|---|---|---|---|---|---|
| 2021-22 | 0.109 | 0.043 | 0.250 | 0.078 | 0.140 | 0.038 |
| 2022-23 | 0.110 | 0.044 | 0.252 | 0.070 | 0.153 | 0.031 |
| 2023-24 | 0.109 | 0.038 | 0.272 | 0.074 | 0.144 | 0.054 |
| 2024-25 | 0.108 | 0.045 | 0.256 | 0.078 | 0.163 | 0.033 |
| **2025-26** | **0.102** | **0.057** | **0.229** | **0.096** | **0.131** | **0.041** |

**Off-ball motion has been flat across all five seasons at 10-11%.** Iso rose from 7-8% to 9.6%. PR-Ball-Handler dropped from 14-16% to 13.1%.

The Wolves substituted iso for pick-and-roll while leaving off-ball motion unchanged.

## The refined diagnosis

The Q4 framing was: low stickiness, high motion death, very high iso, low action diversity.

The data says the first three hold, but the fourth does NOT. The Wolves are not action-poor. They have a playbook of normal breadth. **They are iso-overweighted within a normal-breadth playbook.**

That is a more specific diagnosis. Action-poor offenses (only 4 distinct actions, e.g., 2017-18 Cavs late-stage LeBron) are easy to recognize. The Wolves' problem is harder to see because they DO run all the actions, they just choose iso when other choices would be better.

The refined working synthesis:

> Wolves' Q4 pathology = high motion death (C2) + very high iso reliance with decentralized load (C3) + normal-breadth playbook but with iso substituting for PR-Ball-Handler. NOT "they only run a couple of things." More precisely: "they run plenty of things, but they choose iso when other choices would be better."

## Where the v1 proxy is genuinely limited

The spec's Action Poverty includes "multi-action possession rate" (chained actions like PnR -> flare -> cut). Synergy gives us frequencies, not chains.

A team that runs PR -> flare -> cut chains has more actions per possession than a team that runs PR -> shot. Synergy reports both as one PR possession. v2 with the full action classifier would let us check this directly. **It's possible the Wolves have a chaining problem that v1 cannot see.** If they run PR -> shot when other teams run PR -> flare -> shot, v2 will catch it.

For now, treat the 45th percentile as v1's honest answer at the play-type-frequency level.

## Calibration scorecard

| Prior | Outcome |
|---|---|
| Wolves 2025-26 Action Poverty 80-95 pct | **Wrong.** 45 pct. |
| If below 70, investigate v1 proxy vs Q4 refinement | Investigated. Q4 refinement needed, not v1 fix. |
| Low pickup-side: GSW, IND, BOS, ATL post-Trae | Mostly right. GSW (2), IND (also low), ATL (16). BOS at 32 was a bit higher than expected. |
| High pickup-side: PHI, OKC, NOP, LAC, MIL | LAC (92) and LAL (82) hit. PHI (45), OKC (29), MIL (39) lower than expected. |

Note: the high-iso teams (PHI, OKC) don't all rank high on Action Poverty by v1 metrics. That's the same proxy issue affecting the Wolves: high iso alone doesn't mean a narrow playbook.

## League leaders 2025-26 RS

**Top 8:** LAC (92), CHI (87), LAL (82), PHX (78), WAS (74), DAL (73), MEM (73), NOP (70).

**Bottom 8:** GSW (2), BKN (3), UTA (5), SAS (14), ATL (16), TOR (21), DEN (23), DET (28).

CHI at 87 is interesting (rebuilding team, narrow playbook). DEN at 23 reflects the Jokic system's breadth. SAS at 14 is consistent with Wembanyama-anchored designed motion.

## What it means for the rest of the build

The Wolves' four-component profile so far:

- C1 Ball Stickiness: 30 (moderate-low)
- C2 Movement Death: 71 (high pickup)
- C3 Isolation Reliance: 89 (very high pickup)
- C4 Action Poverty (v1): 45 (moderate, not pickup)

The composite weighting (25/20/20/20/15) implies the Wolves' LAFI will be driven primarily by C2 + C3 (40% combined). C1 and C4 will pull DOWN their composite. C5 (Shot Quality Decay) is the last piece and could push them up if it's elevated.

The story is sharper than the original thesis but less extreme. The Wolves are not LAFI-extreme on every component; they are extreme specifically on motion death and iso reliance. The composite will rank them high overall but probably not as the league's most pickup team.

## What we decided

Proceed to Component 5 (Shot Quality Decay). No metric change in C4 v1. v2 with action classifier should add multi-action density as a future check.

Add a note to the v2 roadmap: chained-action analysis is the test that will tell us whether the v1 "normal breadth" reading is actually right at the chain level. Synergy can't answer this; the action classifier can.
