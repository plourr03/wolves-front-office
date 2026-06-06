# Eye-test: action_poverty

_Higher percentile = more pickup-like. Each percentile is pooled across the full team-season sample._

## Priors before running


- Wolves 2025-26 prediction: **80th to 95th percentile**, updated after
  Component 3 landed at 89. If Action Poverty lands below 70, that warrants
  investigation: either the v1 proxy isn't catching what feels obvious from the
  eye test, or the Q4 diagnosis needs refining.
- The action_diversity_count annotation should show Wolves using fewer distinct
  Synergy play types at >=3% than the championship-archetype teams (Pacers,
  Celtics, Warriors usually run 7-8 distinct actions at meaningful frequency).
- Expected high pickup-side: ball-dominant single-star offenses (PHI, OKC, NOP,
  LAC, MIL, MIN).
- Expected low pickup-side: motion offenses (GSW, IND, BOS, ATL post-Trae).

**v1 vs v2 transparency.** This component uses Synergy-derived proxies because
the action classifier from PBP doesn't exist yet. If v1 confirms the eye-test,
the finding is suggestive. v2 with the full classifier will sharpen it.

## League leaderboard

**League leaders (top 8, 2025-26 RS):**
| Team | Pct | Raw z |
|---|---|---|
| LAC | 92 | +0.95 |
| CHI | 88 | +0.80 |
| LAL | 82 | +0.68 |
| PHX | 79 | +0.57 |
| WAS | 74 | +0.45 |
| DAL | 74 | +0.45 |
| MEM | 73 | +0.44 |
| NOP | 70 | +0.40 |

**League tail (bottom 8, same season):**

| Team | Pct | Raw z |
|---|---|---|
| GSW | 3 | -1.39 |
| BKN | 3 | -1.29 |
| UTA | 5 | -1.14 |
| SAS | 15 | -0.73 |
| ATL | 16 | -0.71 |
| TOR | 21 | -0.54 |
| DEN | 23 | -0.51 |
| DET | 28 | -0.41 |

## Wolves trajectory

| Season | Type | Raw z | Pct rank | Top handler |
|---|---|---|---|--- |
| 2014-15 | Re | -0.35 | 32 | Zach LaVine |
| 2015-16 | Re | -0.47 | 24 | Ricky Rubio |
| 2016-17 | Re | +0.29 | 63 | Ricky Rubio |
| 2017-18 | Re | +1.21 | 96 | Jeff Teague |
| 2018-19 | Re | +0.59 | 80 | Tyus Jones |
| 2019-20 | Re | -0.70 | 17 | D'Angelo Russell |
| 2020-21 | Re | -0.82 | 14 | nan |
| 2021-22 | Re | -0.41 | 28 | D'Angelo Russell |
| 2022-23 | Re | -0.38 | 31 | Mike Conley |
| 2023-24 | Re | -0.42 | 27 | Anthony Edwards |
| 2024-25 | Re | -0.27 | 36 | Anthony Edwards |
| 2025-26 | Re | -0.09 | 45 | Anthony Edwards |

## Investigation notes


**Wolves 2025-26 landed at 45th percentile. The user's prior was 80-95.**

This is below the user's "investigate if below 70" threshold. The first move is
to check whether the v1 proxy is the issue or whether the diagnosis needs
refining.

**Drill-in: Wolves 2025-26 Synergy play-type distribution vs the league.**

| Team | Cut | OffScr | Cut+OffScr | Handoff | Spotup | Iso | PRBH | Post | Trans |
|---|---|---|---|---|---|---|---|---|---|
| **MIN** | 0.052 | 0.050 | **0.102** | 0.057 | 0.229 | **0.096** | **0.131** | 0.041 | 0.190 |
| LAC  | 0.067 | 0.022 | 0.089 | 0.034 | 0.219 | 0.116 | 0.151 | 0.056 | 0.162 |
| LAL  | 0.078 | 0.052 | 0.130 | 0.022 | 0.199 | 0.085 | 0.170 | 0.055 | 0.177 |
| PHI  | 0.062 | 0.033 | 0.095 | 0.040 | 0.230 | 0.099 | 0.141 | 0.039 | 0.185 |
| BOS  | 0.054 | 0.049 | 0.103 | 0.053 | 0.231 | 0.096 | 0.183 | 0.020 | 0.150 |
| GSW  | 0.096 | 0.065 | 0.161 | 0.041 | 0.267 | 0.055 | 0.128 | 0.028 | 0.160 |
| IND  | 0.059 | 0.045 | 0.104 | 0.041 | 0.258 | 0.050 | 0.163 | 0.040 | 0.193 |
| ATL  | 0.076 | 0.056 | 0.132 | 0.060 | 0.223 | 0.042 | 0.147 | 0.028 | 0.216 |

**Wolves on Cut + OffScreen (pure off-ball motion architecture): 10.2%. That is
within 1 percentage point of BOS, IND, and PHI. Not low.** Even excluding Handoff
(which is on-ball) and Spotup (which is mixed), the Wolves are league-average
on designed off-ball motion.

**Where the Wolves ARE distinctive:**

- **Low PR-Ball-Handler share: 13.1%.** League high-iso teams run 14-18% PR-BH.
  The Wolves run less pick-and-roll than most contenders.
- **High Iso share: 9.6%.** Top quartile (matches what Component 3 found).
- **Low Spotup share: 22.9%.** Below league average. Surprising given the iso-
  ends-in-kickout intuition.

**Wolves year-over-year Synergy detail:**

| Season | Cut+OffScr | Handoff | Spotup | Iso | PRBH | Post |
|---|---|---|---|---|---|---|
| 2021-22 | 0.109 | 0.043 | 0.250 | 0.078 | 0.140 | 0.038 |
| 2022-23 | 0.110 | 0.044 | 0.252 | 0.070 | 0.153 | 0.031 |
| 2023-24 | 0.109 | 0.038 | 0.272 | 0.074 | 0.144 | 0.054 |
| 2024-25 | 0.108 | 0.045 | 0.256 | 0.078 | 0.163 | 0.033 |
| **2025-26** | **0.102** | **0.057** | **0.229** | **0.096** | **0.131** | **0.041** |

Off-ball motion (Cut + OffScreen) has been flat across all five seasons at 10-11%.
Iso rose from 7-8% to 9.6%. PR-Ball-Handler fell from 14-16% to 13.1%. **The
Wolves substituted iso for pick-and-roll, while leaving off-ball motion unchanged.**

**What this means: the v1 result is honest, but the diagnosis needs refining.**

The Q4 framing was: low stickiness, high motion death, very high iso, low action
diversity. The data says the first three hold, but the fourth does NOT. The
Wolves are not action-poor. They have a playbook of normal breadth. They are
**iso-overweighted within a normal-breadth playbook.**

That is a more specific diagnosis. Action-poor offenses (only 4 distinct
actions) are easy to recognize. The Wolves' issue is harder to see because they
DO run all the actions, just disproportionately iso.

**Where the v1 proxy is genuinely limited.**

The spec's Action Poverty includes "multi-action possession rate" (chained
actions like PnR -> flare -> cut). Synergy gives us frequencies, not chains. A
team that runs PR -> flare -> cut chains has more actions per possession than a
team that runs PR -> shot, but Synergy reports both as "1 PR possession." v2
with the full action classifier would let us check this directly. It's possible
the Wolves have a chaining problem v1 cannot see.

**Recommended interpretation.** Treat Component 4 as a refinement of the Q4
diagnosis, not a contradiction. The synthesis becomes:

Wolves' Q4 pathology = high motion death (C2) + very high iso reliance with
decentralized load (C3) + normal-breadth playbook but with iso substituting
for PR-Ball-Handler. NOT "they only run a couple of things." More precisely:
"they run plenty of things, but they choose iso when other choices would be
better."

**No metric change warranted in v1.** v2 with the action classifier should
add multi-action density. If that comes back low for the Wolves, the
"action poverty" framing reattaches; if it doesn't, the refined diagnosis
holds permanently.
