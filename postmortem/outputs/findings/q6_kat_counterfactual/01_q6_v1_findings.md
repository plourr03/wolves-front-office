# Q6 v1: KAT counterfactual (scope-capped) [SUPERSEDED by v2]

**Date:** 2026-05-18
**Status:** Q6 v1. **SUPERSEDED by Q6 v2 (`02_q6_v2_findings.md`) same day.** Preserved for audit trail.

> **METHODOLOGICAL GAP (2026-05-18):** Bobby caught that the KAT-for-Randle trade also brought DiVincenzo to Minnesota. V1's swap was one-for-one (KAT replaces Randle, holding DiVincenzo constant). The correct counterfactual is one-for-two: remove BOTH Randle AND DiVincenzo, add KAT plus a replacement-level wing. V1's headline finding (counterfactual lands at Q3) was based on the incomplete swap. V2 reruns with the corrected roster and substantially revises the trade verdict framing. See v2 for current state.

**Method:** Player-level Synergy swap counterfactual. Substitute KAT's 2025-26 NYK Synergy production (scaled to Randle's volume to control for usage) for Randle's actual 2025-26 MIN Synergy production. Reconstruct counterfactual team-level play type frequencies. Compare to actual 2025-26 (Q4) and to 2023-24 (Q1/Q2 baseline) at the architectural level.

## Headline

**No, but they would not have been Q4 either.** The counterfactual KAT 2025-26 Wolves would likely have landed at Q3-leaning, similar architecturally to the actual 2024-25 Wolves (LAFI Full 63 / Sharp 71). The trade was a significant architectural factor (it explains roughly half the isolation-reliance increase and most of the PRRollMan decline) but not the sole driver. The motion-death component (C2 of LAFI) is essentially unaffected by the KAT swap, which means the architectural drift toward Q4 has roots beyond the KAT trade.

**The honest framing:** the trade accelerated and amplified an architectural drift that was already in motion. Without the trade, the team would still have drifted (just more slowly), landing in Q3 rather than Q4 by 2025-26. The Q5 v3 prescription's diagnosis stands: the team needs architectural additions (Category B wing, skilled secondary creator) regardless of the counterfactual KAT scenario.

## 1. The 2023-24 baseline (already established by Q0A)

Per `outputs/findings/q0a_lafi/11_wolves_lafi_deliverable.md` Section 2, the Edwards-era trajectory:

| Season | Roster context | C1 | C2 | C3 | C4 | C5 | Full LAFI | Sharp LAFI |
|---|---|---|---|---|---|---|---|---|
| 2022-23 | Gobert year 1 | 14 | 64 | 44 | 31 | 47 | 34 | 53 |
| **2023-24** | **WCF year, last KAT** | **35** | **43** | **49** | **27** | **39** | **35** | **45** |
| 2024-25 | Randle year 1 | 69 | 56 | 71 | 36 | 72 | 63 | 71 |
| 2025-26 | Randle year 2 | 31 | 72 | 90 | 45 | 83 | 65 | 90 |

**The 2023-24 Wolves (last KAT year) were architecturally Q1/Q2.** Full LAFI 35 (35th percentile, league-average territory) and Sharp LAFI 45 (45th percentile, slightly above the median). Both well below the league's playoff-failure threshold. The LAFI deliverable characterized 2023-24 as "the most-designed version of the Edwards-era offense."

Three components moved in lockstep after the KAT trade:
- C2 motion-death: 43 → 56 → 72 (+29 percentile)
- C3 iso-reliance: 49 → 71 → 90 (+41 percentile)
- C5 shot-quality-decay: 39 → 72 → 83 (+44 percentile)

**Step 1 conclusion:** the 2023-24 Wolves WERE Q1/Q2 architecturally. The drift to Q4 happened AFTER the trade.

## 2. KAT's actual age 28-30 production trajectory

Pulling KAT's Synergy profile across his last MIN year (2023-24, age 28) and his first two NYK years (2024-25 age 29; 2025-26 age 30) characterizes how he aged within his archetype.

**Key shifts in KAT's profile (NYK vs his last MIN year):**

| Play type | 2023-24 MIN (age 28) | 2025-26 NYK (age 30) | Change |
|---|---|---|---|
| Cut | 51 poss (84th pct PPP) | 80 poss (73rd pct PPP) | volume up, PPP similar |
| OffScreen | 100 poss (75th pct PPP) | 29 poss (12th pct PPP) | volume crashed |
| Isolation | 156 poss (62nd pct) | 124 poss (29th pct PPP) | volume similar, efficiency crashed |
| PRRollMan | 124 poss (90th pct PPP) | 177 poss (87th pct PPP) | volume up, PPP similar |
| Postup | 170 poss (72nd pct) | 156 poss (31st pct PPP) | volume similar, efficiency dropped |
| Spotup | 322 poss (32nd pct PPP) | 233 poss (67th pct PPP) | volume down, efficiency up |
| Transition | 119 poss (76th pct PPP) | 199 poss (66th pct PPP) | volume up, PPP similar |

**Observations:**

1. **KAT in NYK is doing dramatically less OffScreen** (29 poss vs 100 in MIN 2023-24). His role at age 30 is less off-ball-movement-heavy than at age 28. This matters for the counterfactual because the LAFI C2 motion-death component partially depends on OffScreen volume.

2. **PRRollMan volume increased in NYK** (177 vs 124). KAT is still an elite roll partner, and arguably more so in the Brunson + Bridges system than the Edwards-led MIN system.

3. **Isolation volume similar across teams** (124 vs 156). KAT iso possessions are not the headline of the trade swap.

4. **Spotup volume down** in NYK (233 vs 322). His role has shifted away from pure floor-spacing.

**For the counterfactual: KAT at age 30 is NOT the same archetypal piece as KAT at age 28.** He's still a positive contributor across most play types, but his off-ball movement specifically has reduced. This means the counterfactual swap will not fully restore the 2023-24 architectural profile, even though the trade-driven iso reliance reverses meaningfully.

## 3. Counterfactual 2025-26 team Synergy

**Method:** Subtract Randle's 2025-26 MIN actual Synergy possessions; add KAT's 2025-26 NYK actual Synergy possessions scaled by 1.206 (Randle's total 1574 poss / KAT's NYK total 1305 poss) to match Randle's role volume. The counterfactual approximates "KAT in Randle's slot in the 2025-26 Wolves system at Randle's usage."

| Play type | Actual 2025-26 | Randle out | KAT in (scaled) | Counterfactual | Actual % | CF % | Δ pp |
|---|---|---|---|---|---|---|---|
| Isolation | 867 | -262 | +150 | 755 | 9.62% | 8.38% | **-1.25 pp** |
| PRRollMan | 377 | -100 | +213 | 490 | 4.18% | 5.44% | **+1.26 pp** |
| PRBallHandler | 1180 | -148 | +35 | 1067 | 13.10% | 11.84% | -1.25 pp |
| Cut | 471 | -80 | +96 | 487 | 5.23% | 5.41% | +0.18 pp |
| OffScreen | 452 | -46 | +35 | 441 | 5.02% | 4.89% | -0.12 pp |
| OffRebound | 506 | -82 | +215 | 639 | 5.62% | 7.09% | +1.47 pp |
| Postup | 371 | -156 | +188 | 403 | 4.12% | 4.48% | +0.36 pp |
| Spotup | 2064 | -333 | +281 | 2012 | 22.91% | 22.33% | -0.58 pp |
| Transition | 1710 | -262 | +240 | 1688 | 18.98% | 18.74% | -0.24 pp |

**Team blended PPP impact:** +0.004 per Synergy possession (1.037 CF vs 1.033 actual). Scaled to ~9000 possessions: roughly +36 points per season, or +0.4 PPG. Tiny improvement at the team-PPP level.

## 4. Architectural reversion check

The key question: does the counterfactual swap revert the team to 2023-24 architectural baseline, or only partially?

| Metric | 2023-24 KAT | 2025-26 Randle (actual) | 2025-26 KAT (counterfactual) | % reversion |
|---|---|---|---|---|
| **Isolation %** | 7.39% | 9.62% | 8.38% | **56% reverted** |
| Cut % | 6.10% | 5.23% | 5.41% | 21% reverted |
| OffScreen % | 4.76% | 5.02% | 4.89% | 50% reverted |
| **Motion (Cut+OffScreen) %** | 10.86% | 10.25% | 10.31% | **10% reverted** |
| **PRRollMan %** | 5.65% | 4.18% | 5.44% | **86% reverted** |
| Spotup % | 27.19% | 22.91% | 22.33% | counterfactual continues to decline |

**Three categories of architectural change:**

**Category 1: KAT-driven shifts (the trade was the primary driver).**
- **PRRollMan reverts 86%.** KAT in 2025-26 NYK is still an elite roll partner (177 possessions at 87th percentile PPP). Randle's roll-man volume was lower than KAT's. The KAT swap restores most of the PRRollMan deficit.
- **Isolation reverts 56%.** KAT does less iso volume than Randle (124 vs 262 in their respective 2025-26 seasons). The KAT swap removes ~110 iso possessions from the team-level total. Meaningful but not full reversion.

**Category 2: Mixed (the trade was a partial driver).**
- **OffScreen reverts 50%.** KAT swap modestly improves off-ball motion via his Cut volume, but KAT's NYK 2025-26 OffScreen volume (29 poss) is dramatically lower than his MIN 2023-24 level (100 poss). His age 30 self isn't restoring the off-ball motion of his 2023-24 self.

**Category 3: Trade-independent shifts (the drift would have happened anyway).**
- **Motion (Cut + OffScreen total) reverts only 10%.** The Wolves' off-ball motion decline is essentially unaffected by the KAT swap. This is the key finding for the C2 LAFI component: motion death is broader than the trade.
- **Spotup continues to decline in counterfactual.** KAT's NYK 2025-26 spotup volume is lower than his 2023-24 MIN level. The catch-and-shoot collapse (Cat B gap per Q3) is independent of KAT vs Randle.

## 5. LAFI component projection (heuristic)

Translating the Synergy-level swap into LAFI percentile projections requires applying the swap to the actual LAFI component calculations. The C3 iso reliance and C2 motion death components depend partly on Synergy frequencies. Approximate projection:

| LAFI component | 2023-24 actual | 2025-26 actual | 2025-26 CF (KAT) projection |
|---|---|---|---|
| C1 Ball stickiness | 35 | 31 | ~30-40 (minor change from swap) |
| C2 Movement death | 43 | 72 | ~65-72 (small improvement; OffScreen partial) |
| **C3 Isolation reliance** | **49** | **90** | **~65-75 (substantial improvement; iso volume down)** |
| C4 Action poverty | 27 | 45 | ~40-45 (minor change) |
| C5 Shot quality decay | 39 | 83 | ~75-83 (small improvement; KAT efg slightly better in mix) |
| **Full LAFI (composite)** | **35** | **65** | **~50-58 (mid range)** |
| **Sharp LAFI (C2+C3+C5)** | **45** | **90** | **~70-80 (Q3 range, not Q1)** |

The projection bands are wide because the heuristic translation from Synergy-level swap to LAFI percentile is approximate. But the directional conclusion is robust: the counterfactual KAT 2025-26 Wolves would land between Q3 (similar to actual 2024-25) and the actual 2025-26 Q4. They would NOT revert to the 2023-24 Q1/Q2 baseline.

## 6. The verdict on the scope-capped question

**"Would the team have stayed Q1 architecturally per LAFI with KAT?"**

**The data-driven answer: No. The team would have stayed Q3 (similar to actual 2024-25), not reverted to Q1.**

**Why this answer is honest:**

1. **The 2023-24 baseline (Q1/Q2) was achievable in a specific roster configuration.** That configuration had KAT at age 28 in his pre-extension prime, plus Conley at age 36 (not 38), plus DiVincenzo healthy, plus the system as architected.

2. **KAT at age 30 is not KAT at age 28.** His OffScreen and Spotup volumes are down. His isolation efficiency dropped. He's still a positive player but his archetype role has narrowed.

3. **The Wolves' system trajectory has shifted independent of personnel.** Q0D's coaching system analysis found a real allocation shift (PR-Roll-Man down 41%) regardless of personnel. The LAFI deliverable's "Act 4" framing names this directly.

4. **Other roster factors compound:** Conley aging (RAPM declined), DiVincenzo injury (Cat B specialist out), McDaniels role expansion delayed, Beringer rookie minutes drag.

**The trade was the architectural catalyst that accelerated the drift.** Without it, the team probably becomes 2024-25-leaning in 2025-26 rather than 2024-25-leaning in 2024-25 and Q4 in 2025-26. The Q4 destination might still arrive in 2026-27 or 2027-28 without intervention.

**This validates the Q5 v3 prescription regardless of the counterfactual.** The team needs architectural additions (Category B wing + skilled secondary creator) and system restoration whether or not the KAT trade is reversed. The counterfactual shows the trade was a significant factor; it does not show the team would be championship-architecturally-sound without the trade.

## 7. The KAT-for-Randle trade verdict

The deliverable's KAT framing per CLAUDE.md needs to land honestly. The Q6 v1 finding:

**The trade was a significant architectural factor that accelerated a drift already in motion.** The 2023-24 Wolves were Q1/Q2 architecturally with KAT, age-appropriate Conley, and DiVincenzo healthy. The trade combined with other aging/injury/system factors moved the team to Q4 in two years. Without the trade, the team would likely have moved to Q3 in the same window. The trade explains roughly half the iso reliance increase, most of the PRRollMan decline, and limited motion-death change.

**The Spotrac contract context matters.** KAT's extension and contract value made the trade financially defensible (his deal would have constrained future flexibility). The basketball architectural cost was meaningful but not solely-causative.

**The right framing for the front office reader:** "The trade was a significant architectural cost. Reasonable people could read the evidence differently. The trade was not the sole driver of the team's Q4 drift; other factors contributed. The team's path forward (Q5 v3 prescription) is needed regardless of the counterfactual KAT scenario."

## 8. What Q6 v1 does NOT do

Per the data scientist's scope cap, deferred:

- **Full lineup-level substitution with bootstrapped CIs.** A formal lineup-grain simulation would tighten projections but doesn't change the central finding.
- **Detailed shot quality differential between KAT and Randle.** Catch-and-shoot 3PA vs pull-up analysis at the player level would sharpen C5 projection.
- **Multi-season comp set for KAT 2024-26 trajectory.** Comparison to other star-level age 28-30 transitions would tighten the age-projection band.
- **Salary cap implications of the counterfactual.** What the team gives up to keep KAT (no Randle, no DiVincenzo via the secondary moves, different cap structure). Deferred to Q5 v4 if needed.
- **Counterfactual playoff outcome projection.** Would the team have reached the Finals? Beaten the Spurs? Won the title? These are second-order questions; the scope-capped Q6 stays at architectural reversion.

These would sharpen the v1 but the central finding (trade was significant but not sole driver; counterfactual lands at Q3 not Q1) is robust.

## 9. Artifacts

```
analyses/q6_kat_counterfactual/
  __init__.py
  synergy_swap.py                  player-level Synergy swap driver

outputs/tables/q6_kat_counterfactual/
  counterfactual_synergy.csv       per-play-type CF distribution
  wolves_team_synergy_history.csv  three-season team Synergy
  headline_architectural_swing.csv summary table
```

Re-runnable: `python -m analyses.q6_kat_counterfactual.synergy_swap`.

## 10. Status

Q6 v1 complete. The KAT counterfactual finding lands honestly: the trade was a significant architectural factor that accelerated a drift already in motion, but not the sole driver. The counterfactual KAT 2025-26 Wolves would have been Q3, not Q1. The Q5 v3 prescription stands regardless.

**Implication for Q5 v4 integration:**
- The KAT framing section should reflect the "trade was significant but not sole" finding.
- The deliverable can engage with KAT honestly without overstating "this was the architectural error" or understating "this had no impact."
- Reasonable readers can disagree on whether the basketball cost outweighed the contract/cap savings.

Phase 2 next: Q0C historical cohort analysis. Then Q5 v4 consolidation of Q0B + Q6 + Q0C plus the contract structure correction.
