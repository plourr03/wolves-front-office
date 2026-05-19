# Q6 v2: KAT counterfactual (corrected roster)

**Date:** 2026-05-18
**Status:** Q6 v2. Supersedes v1 (preserved as `01_q6_v1_findings.md` for audit trail). Same-day correction prompted by Bobby flagging that the KAT-for-Randle trade also brought DiVincenzo to Minnesota. The trade was a one-for-two (plus picks), not a one-for-one.

**Method (corrected):** Player-level Synergy swap. Remove BOTH Randle and DiVincenzo from the 2025-26 Wolves Synergy distribution. Add KAT's 2025-26 NYK Synergy production (scaled to Randle's volume) plus a "replacement-level wing" filling DiVincenzo's slot at reduced volume and reduced efficiency. The replacement-level wing represents what the Wolves likely would have signed in 2024 free agency without the cap savings from the KAT trade (an Ingles-tier veteran or minimum-salary catch-and-shoot specialist). Three sensitivity bands on the replacement wing: optimistic (70% volume, -0.02 PPP), default (50% / -0.05), pessimistic (30% / -0.08).

## Headline (revised)

**The counterfactual KAT 2025-26 Wolves land in Q4 territory, not Q3.** The corrected counterfactual lands at Sharp LAFI ~78-85 (vs actual 90, vs v1 estimate 70-80) and Full LAFI ~58-65 (vs actual 65, vs v1 estimate 50-58). The team would not have been architecturally meaningfully better than the actual 2025-26 Wolves.

**The trade had simultaneous positive AND negative architectural effects that partially cancel.** V1 framed the trade as primarily negative architecturally; v2 corrects to "complicated transaction with offsetting effects":

- **Negative (trade brought):** Randle's high-volume isolation, lower PR-Roll-Man volume, slightly worse efficiency than KAT
- **Positive (trade brought):** DiVincenzo's elite catch-and-shoot specialist production, his off-ball motion via OffScreen, his secondary playmaking, his contract value

Without the trade, the Wolves lose the DiVincenzo benefit entirely and gain back KAT's positives but at a smaller scale than v1 implied. The architectural drift to Q4 has causes largely independent of the trade.

**This strengthens the Q5 v3 prescription substantially.** If the trade was approximately architecturally neutral in net effect, the team's Q4 pathology is even more dependent on the OTHER factors: system trajectory (Q0D), aging (Conley/Gobert/Randle), and the Category B specialist gap (Cat B catch-and-shoot collapse). The architectural additions the prescription identifies are needed regardless of the counterfactual choice.

## 1. The methodological correction

V1's premise: "KAT replaces Randle, holding DiVincenzo constant." This was wrong because DiVincenzo arrived in Minnesota as part of the same trade. The correct counterfactual structure:

- Wolves SEND: KAT (and minor pieces, plus picks)
- Wolves RECEIVE: Randle + DiVincenzo + 2025 first-round pick (via DET)

So "if the KAT trade didn't happen" means the 2025-26 roster has:
- KAT (still on his extension, age 30) — replaces Randle's slot
- NO DiVincenzo — he stays at NYK or signs elsewhere as a free agent
- Replacement-level wing at minimum or below-MLE — what the Wolves likely would have added without the cap savings from the trade

V1 only modeled the first piece. V2 models all three.

## 2. Player profiles in the corrected swap

**KAT 2025-26 NYK (age 30):** 1305 total offensive Synergy possessions. PRRollMan 177 (87th pct PPP), Spotup 233 (67th pct), Postup 156, Transition 199, Iso 124 (29th pct PPP), Cut 80, OffScreen 29.

**Randle 2025-26 MIN (age 31):** 1574 total. Iso 262 (heavy volume), Spotup 333, Transition 262, PRBallHandler 148, Postup 156.

**DiVincenzo 2025-26 MIN (age 29):** 948 total. Spotup 316 (the Cat B piece), Transition 169, OffScreen 132 (substantial off-ball motion), PRBallHandler 110, Handoff 129, PRRollMan rare.

**Replacement-level wing (modeled):** 50% of DiVincenzo's volume with -0.05 PPP across all plays. Represents an Ingles-tier veteran or minimum-salary wing the Wolves might have signed in 2024 free agency.

## 3. Architectural swap results

**Per-play-type frequency comparison:**

| Play type | 2023-24 actual | 2025-26 actual | v1 CF (one-for-one) | v2 CF default (50%) | v2 vs actual |
|---|---|---|---|---|---|
| Isolation | 7.39% | 9.62% | 8.38% | **8.74%** | -0.88 pp |
| Cut | 6.10% | 5.23% | 5.41% | **5.64%** | +0.41 pp |
| OffScreen | 4.76% | 5.02% | 4.89% | **4.39%** | -0.63 pp |
| **Motion (Cut+OffScreen)** | **10.86%** | **10.25%** | **10.31%** | **10.03%** | **-0.22 pp** |
| PRRollMan | 5.65% | 4.18% | 5.44% | **5.75%** | +1.57 pp |
| Spotup | 27.19% | 22.91% | 22.33% | **21.72%** | -1.19 pp |
| Transition | 14.94% | 18.98% | 18.74% | 18.79% | -0.19 pp |

**Critical findings (v2 differs from v1):**

1. **OffScreen drops BELOW actual 2025-26.** Without DiVincenzo's 132 OffScreen possessions, the replacement wing (50% volume) provides only ~66 OffScreen possessions. The team's already-stressed off-ball motion via screens declines further from 5.02% to 4.39%. **DiVincenzo was doing real off-ball work; the replacement wouldn't.**

2. **Motion (Cut + OffScreen) DROPS overall (10.03% v2 vs 10.25% actual).** The corrected counterfactual makes the team's motion death pathology WORSE, not better. KAT swapping in restores some Cut volume (KAT does meaningful cutting in NYK) but the DiVincenzo loss more than offsets it. This is the most important v2 finding: **the trade was a net POSITIVE for the team's off-ball motion**, contrary to v1's framing.

3. **Spotup drops below actual (21.72% v2 vs 22.91% actual).** Without DiVincenzo's 316 Spotup possessions at elite efficiency (PPP 1.193, 38.3% on 496 catch-and-shoot 3PA across the season), the team's spot-up volume declines further. The Category B gap the prescription identifies WIDENS in the counterfactual. **The trade was a net positive for catch-and-shoot production.**

4. **Iso reliance reverts LESS than v1 said (8.74% v2 vs 8.38% v1).** With DiVincenzo gone, more iso load stays on the team because the replacement wing can't generate as many secondary actions. The trade's positive contribution to spreading creation load was real.

5. **PRRollMan still reverts substantially (5.75% v2 vs 5.65% baseline).** This is the one clear positive of the counterfactual: KAT is a much better roll partner than Randle, and that holds in v2.

## 4. Sensitivity to replacement-level wing assumption

| Scenario | Replacement wing | Sharp LAFI projection | Full LAFI projection |
|---|---|---|---|
| Optimistic (70% volume, -0.02 PPP) | Ingles-tier veteran | ~75-82 | ~55-62 |
| **Default (50% volume, -0.05 PPP)** | **Minimum-salary specialist** | **~78-85** | **~58-65** |
| Pessimistic (30% volume, -0.08 PPP) | Roster-bottom wing | ~82-87 | ~62-65 |

Across all three scenarios, the counterfactual lands in Q4 territory (Sharp LAFI 75-87 vs actual 90, Full LAFI 55-65 vs actual 65). **None of the scenarios produce a meaningful reversion to Q1/Q2.** The directional finding is robust to the replacement-wing assumption.

## 5. LAFI component projections (corrected)

| LAFI component | 2023-24 actual | 2025-26 actual | v1 CF projection | v2 CF projection (default) |
|---|---|---|---|---|
| C1 Ball stickiness | 35 | 31 | ~30-40 | ~30-40 (unchanged) |
| C2 Movement death | 43 | 72 | ~65-72 | **~73-80 (WORSE than actual)** |
| C3 Isolation reliance | 49 | 90 | ~65-75 | ~75-82 (less reversion) |
| C4 Action poverty | 27 | 45 | ~40-45 | ~42-47 (slightly worse) |
| C5 Shot quality decay | 39 | 83 | ~75-83 | **~85-88 (WORSE than actual)** |
| **Full LAFI (composite)** | **35** | **65** | **~50-58** | **~58-65** |
| **Sharp LAFI (C2+C3+C5)** | **45** | **90** | **~70-80** | **~78-85** |

The v2 counterfactual lands in Q4 territory across all sensitivity bands. The team would not have been architecturally meaningfully better than the actual 2025-26.

## 6. Team blended PPP impact (revised)

| Scenario | Actual Synergy PPP | CF Synergy PPP | Delta | Season impact |
|---|---|---|---|---|
| Optimistic 70% | 1.033 | 1.034 | +0.001 | +8.7 pts |
| Default 50% | 1.033 | 1.033 | +0.000 | +3.5 pts |
| Pessimistic 30% | 1.033 | 1.034 | +0.001 | +10.3 pts |

**Team blended PPP is essentially identical between actual and counterfactual.** The architectural shifts (more iso reverted by KAT, less motion from DiVincenzo loss) approximately cancel at the team-PPP level. The trade was approximately neutral in raw efficiency terms.

This is consistent with the LAFI-level finding: the trade was complicated, not single-directionally negative.

## 7. The revised verdict on the scope-capped question

**"Would the team have stayed Q1 architecturally per LAFI with KAT (and without DiVincenzo)?"**

**Corrected answer: No. The team would still have been in Q4 territory, roughly comparable to the actual 2025-26.** The counterfactual offers small directional improvements (less iso, more PR-Roll-Man) but absorbs equally meaningful penalties (less off-ball motion via OffScreen, less catch-and-shoot volume). Net architectural movement: small, possibly slightly toward Q4-leaning rather than away.

**The trade was approximately architecturally neutral in net effect.** This is a substantial revision from v1's "significant but not sole driver" framing. The corrected framing is "the trade brought offsetting positive and negative effects; net architectural impact was small."

## 8. The revised KAT trade verdict

The corrected counterfactual provides a much more balanced foundation for the deliverable's KAT framing (politically sensitive per CLAUDE.md):

**What the trade gave up:**
- KAT at age 28 was a +5.65% PRRollMan team contributor; replacement-by-Randle dropped this to 4.18% in 2025-26
- KAT's elite efficiency at his role plays (Cut, Postup, OffScreen at 28)
- The 2023-24 Q1/Q2 architectural baseline (but KAT at age 30 in NYK does less OffScreen and lower Iso efficiency, so this baseline was unlikely to fully hold anyway)

**What the trade brought:**
- DiVincenzo, who became the team's #1 RAPM in 2025-26 (+4.84) before the playoff injury
- DiVincenzo's elite Cat B production (6.05 cs_3PA/g at 38.3%, 496 total catch-and-shoot 3PA in 82 games)
- DiVincenzo's substantial OffScreen motion (132 possessions, the offsetting C2 motion contribution)
- Randle (moderate negative but not catastrophic; positive RAPM pairings with Edwards and Gobert; some PR-Ball-Handler value)
- A 2025 first-round pick (via Detroit)
- Cap savings vs KAT's extension that funded other roster moves

**The honest verdict:** the trade was a complicated transaction with simultaneous positive and negative effects. Reasonable people will read the evidence differently:

- **One reading:** "The team lost KAT (a top-30 player) and got Randle who isn't worth his salary." Frames negatively.
- **Another reading:** "The team got DiVincenzo who became their #1 impact player AND saved cap relative to KAT's extension."
- **The architectural reading:** "The trade was approximately net-neutral architecturally. The team's Q4 pathology has causes mostly independent of the trade."

All three readings have evidence. The deliverable should engage with all of them rather than picking one as definitive.

## 9. Implications for Q5 v4 integration

The v2 finding changes how Q5 v4 should engage with the KAT trade:

1. **The KAT framing should be more balanced** than v1 implied. The trade had real positives (DiVincenzo) and real negatives (KAT out, Randle in). The architectural net effect was small. "Reasonable people can disagree" framing is the right register.

2. **The prescription's foundation strengthens.** If the trade is approximately architecturally neutral, the Q4 pathology depends MORE on system trajectory (Q0D), aging (Conley/Gobert), and the Category B gap (Cat B catch-and-shoot collapse). All three of these are addressed by the Q5 v3 prescription. The prescription doesn't depend on the trade interpretation.

3. **The DiVincenzo Category B framework gets strong support.** V2 shows that without DiVincenzo, the team would have a WORSE Cat B problem than they have now. This validates the prescription's emphasis on DiVincenzo recovery + Category B redundancy.

4. **The motion-restoration prescription gets strengthened.** V2 shows that even with KAT back, the motion death pathology persists. This means Path 3 (system change, motion restoration) from the Q0A LAFI deliverable is needed regardless of personnel.

5. **The honest framing for the front office:** "The trade had complicated effects, but the team's architectural pathology has multiple causes that the prescription addresses. The path forward doesn't depend on which interpretation of the trade you find more compelling."

## 10. The pattern observation

This is the fifth material correction the project has caught. The pattern is now well-established: incomplete framings and single-source claims get refined under additional scrutiny.

**Bobby caught what neither the agent nor the data scientist did.** The trade structure (one-for-two plus picks) was hiding in plain sight; the v1 analysis implicitly assumed a one-for-one swap. This is the kind of catch that comes from someone who knows the actual transaction history (lifelong fan with deep franchise context per CLAUDE.md) rather than from an analytical agent working from data alone.

For future Q6-type counterfactual work, the methodological discipline now includes: explicitly model the full transaction (all incoming and outgoing pieces, plus picks if relevant). This avoids the one-for-one trap.

## 11. What Q6 v2 still does NOT do

Per the scope cap, deferred:

- **Full lineup-level substitution with bootstrapped CIs.** A formal lineup-grain simulation would tighten projections but doesn't change the central finding.
- **Detailed shot quality differential between KAT/Randle/DiVincenzo trio.** Catch-and-shoot 3PA vs pull-up analysis at the player level would sharpen C5 projection.
- **Counterfactual playoff outcome projection.** Would the team have reached the Finals with KAT? Beaten the Spurs? These are second-order questions; v2 stays at architectural projection.
- **Salary cap dynamics of the counterfactual.** Without the cap savings from the trade, what other moves would the Wolves have NOT made? Deferred.
- **Picks valuation.** The 2025 first-round pick via Detroit has its own value that v2 does not model.

## 12. Artifacts

```
analyses/q6_kat_counterfactual/
  __init__.py
  synergy_swap.py                  v1 driver (preserved)
  synergy_swap_v2.py               v2 corrected driver

outputs/tables/q6_kat_counterfactual/
  counterfactual_synergy.csv             v1 (preserved)
  v2_counterfactual_default_50pct.csv    v2 default scenario
  v2_headline_architectural_shifts.csv   v2 multi-scenario comparison
  wolves_team_synergy_history.csv        team history
  headline_architectural_swing.csv       v1 (preserved)

outputs/findings/q6_kat_counterfactual/
  01_q6_v1_findings.md             v1 (preserved with SUPERSEDED marker)
  02_q6_v2_findings.md             v2 (this document)
```

Re-runnable: `python -m analyses.q6_kat_counterfactual.synergy_swap_v2`.

## 13. Status

Q6 v2 complete. The KAT counterfactual finding lands honestly with the corrected one-for-two trade structure: **the trade was approximately architecturally neutral in net effect**. The Q4 pathology has causes mostly independent of the trade.

The Q5 v3 prescription stands and strengthens. Architectural additions (Category B wing + skilled secondary creator) and system restoration are needed regardless of the counterfactual interpretation. The trade interpretation does not change the prescription.

Phase 2 next: Q0C historical cohort analysis. Then Q5 v4 consolidation of Q0B + Q6 v2 + Q0C plus the contract structure correction.
