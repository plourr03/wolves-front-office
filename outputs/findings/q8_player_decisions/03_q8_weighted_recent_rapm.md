# Q8 weighted-recent RAPM: the Gobert decline test

**Date:** 2026-05-17
**Status:** The blocking item flagged by Bobby's data scientist before Q8 final ship. Tests whether Gobert's 3-year pooled RAPM (+6.18) overstates his current-year impact.
**Method:** Same sparse ridge regression as the pooled RAPM, but restricted to 2025-26 possessions only (18,740 possessions from 94 games, vs 55,670 / 289 games for the pooled).

## Headline

**Gobert's 2025-26-only net RAPM is +1.98, down from +6.18 pooled. A 4.2-point decline.**

The Q8 framing needs to incorporate this. Gobert is still a positive contributor and still the team's best defensive RAPM (-5.19 def in 2025-26, the lowest in the sample). But the magnitude of his impact has come down meaningfully. The keep-Gobert recommendation still holds for 2026-27 but with revised confidence about his trajectory going forward.

**Secondary findings:**

- **DiVincenzo's 2025-26-only RAPM is +4.84 (the #1 in the 404-player 2025-26 sample).** Up from +1.35 pooled. The pooled estimate was understating his 2025-26 form because earlier seasons (2023-24 NYK, 2024-25 partial) dragged the average down. The DiVincenzo Category B case is even stronger with recent data.

- **Randle's 2025-26-only RAPM is -0.07 (essentially neutral), up from -0.88 pooled.** The case for moving him weakens slightly with the recent estimate. He's not a clearly negative-impact player in 2025-26; he's just approximately neutral. The salary-efficiency gap remains (-2.57 surplus vs the +2.5 threshold for his salary tier).

- **Edwards' net RAPM is more negative in 2025-26-only (-1.97 vs -0.61 pooled), confirming the Wolves-only-sample artifact.** As the sample shrinks, the artifact gets worse (less off-floor variation to estimate impact from). Continue to treat his net RAPM as not interpretable; use his offensive RAPM (+1.37 in 2025-26-only, +3.97 pooled).

- **Naz Reid is stable** (+2.70 in 2025-26-only vs +2.42 pooled). His 2025-26 #3 league rank confirms his value.

## 1. The comparison table

| Player | Off 2025 | Def 2025 | Net 2025 | Off pooled | Def pooled | Net pooled | Δ Off | Δ Def | Δ Net |
|---|---|---|---|---|---|---|---|---|---|
| **Rudy Gobert** | -3.20 | -5.19 | **+1.98** | -0.71 | -6.89 | **+6.18** | -2.49 | +1.70 | **-4.20** |
| Naz Reid | +0.19 | -2.51 | +2.70 | +0.04 | -2.38 | +2.42 | +0.16 | -0.13 | +0.29 |
| Jaylen Clark | +0.70 | -0.35 | +1.06 | +1.55 | +0.10 | +1.45 | -0.85 | -0.45 | -0.40 |
| **Donte DiVincenzo** | +1.98 | -2.87 | **+4.84** | +0.38 | -0.97 | **+1.35** | +1.59 | -1.90 | **+3.49** |
| Mike Conley | -0.10 | +0.28 | -0.38 | -1.06 | -0.66 | -0.40 | +0.96 | +0.94 | +0.01 |
| Jaden McDaniels | -0.34 | +0.28 | -0.62 | -0.20 | +0.29 | -0.48 | -0.14 | -0.01 | -0.14 |
| Joan Beringer | +0.59 | +1.53 | -0.93 | +1.00 | +1.57 | -0.58 | -0.40 | -0.05 | -0.35 |
| Anthony Edwards (use off) | +1.37 | +3.34 | -1.97 | +3.97 | +4.58 | -0.61 | -2.59 | -1.23 | -1.36 |
| **Julius Randle** | +1.38 | +1.45 | **-0.07** | +1.07 | +1.95 | **-0.88** | +0.31 | -0.50 | +0.81 |
| Bones Hyland | -1.22 | +0.49 | -1.71 | -1.06 | +0.38 | -1.44 | -0.16 | +0.10 | -0.27 |
| Ayo Dosunmu | -0.45 | +0.70 | -1.14 | -0.33 | +1.45 | -1.79 | -0.11 | -0.75 | +0.64 |
| Terrence Shannon Jr. | +1.08 | +3.38 | -2.30 | +0.30 | +3.07 | -2.77 | +0.78 | +0.31 | +0.46 |

## 2. The 2025-26 top 10 (sanity check)

| Rank | Player | Off | Def | Net |
|---|---|---|---|---|
| **1** | **Donte DiVincenzo** | +1.98 | -2.87 | **+4.84** |
| 2 | Victor Wembanyama | +1.19 | -1.61 | +2.80 |
| 3 | Naz Reid | +0.19 | -2.51 | +2.70 |
| 4 | Kawhi Leonard | +1.50 | -0.73 | +2.23 |
| **5** | **Rudy Gobert** | -3.20 | -5.19 | **+1.98** |
| 6 | Julian Champagnie | +1.00 | -0.97 | +1.97 |
| 7 | Derrick Jones Jr. | +0.66 | -1.30 | +1.96 |
| 8 | Aaron Gordon | +0.77 | -1.07 | +1.84 |
| 9 | Jarred Vanderbilt | +1.31 | -0.47 | +1.78 |
| 10 | Kristaps Porzingis | +1.32 | -0.37 | +1.69 |

**Three Wolves players in the top 5 of the 2025-26-only RAPM:** DiVincenzo (#1), Naz Reid (#3), Gobert (#5). For a team with only one All-Star caliber player (Edwards, whose RAPM is artifact), this is a striking concentration of positive-impact role/role-plus players. The team's structural positives at the role-player level are real and supported by recent data.

**Caveat about the sanity check:** Wolves players are over-represented in the top because the Wolves-only sample bias favors Wolves players who appear in every Wolves game over opponents who appear in 2-4 games. Wembanyama at #2 is real; the rest of the league benchmarks are noisier. The Wolves-internal ranking (DiVincenzo > Naz > Gobert > everyone else) is informative.

## 3. The Gobert decline picture

Breaking the 4.2-point net decline into offensive and defensive components:

- **Defensive RAPM**: -5.19 in 2025-26 vs -6.89 pooled. Slightly worse but still the lowest (best) in the 2025-26 sample. His defense is essentially intact at age 33. **Hypothesis H1b (Gobert remains a top-tier defensive impact player despite his age) survives the decline test.**

- **Offensive RAPM**: -3.20 in 2025-26 vs -0.71 pooled. **A 2.5-point drop in offensive impact.** This is the dominant driver of the net decline. The team's offense with Gobert on the floor in 2025-26 was meaningfully worse than the team's offense with him in 2023-24 and 2024-25.

**The offensive decline is plausibly explained by team-system changes around him, not by Gobert personally declining.** The team replaced KAT (who created elite offensive gravity) with Randle (who's a more inside-the-arc creator). The team's overall 3PA rate dropped 3.6 percentage points YoY (per the yoy comparison). DiVincenzo went down in the playoffs (less Category B around Gobert when on the floor in R2). All of these changes happen to coincide with what we measure as "Gobert's offensive RAPM declined."

This is a confound, not a confound resolution. We can't cleanly separate "Gobert got worse offensively" from "the team's offense got worse around Gobert in ways that show up in his coefficient." But the directional finding is clear: in 2025-26, the Wolves' offense was meaningfully less productive when Gobert was on the floor than in prior years.

## 4. The 2025-26-only updates to the salary-efficiency picture

Re-running the salary efficiency table with 2025-26-only RAPM:

| Player | 2025-26 salary | 2025-26 net RAPM | Threshold | Surplus |
|---|---|---|---|---|
| Edwards (use off) | $45.6M | +1.37 | +4.0 | -2.63 (artifact) |
| **Gobert** | **$35.0M** | **+1.98** | **+2.5** | **-0.52** |
| Randle | $30.9M | -0.07 | +2.5 | -2.57 |
| McDaniels | $24.4M | -0.62 | +1.0 | -1.62 |
| Naz Reid | $21.6M | +2.70 | +1.0 | +1.70 |
| **DiVincenzo** | **$12.0M** | **+4.84** | **+0.5** | **+4.34** |
| Conley | $0.7M | -0.38 | 0.0 | -0.38 |

**With the 2025-26-only RAPM lens:**
- **DiVincenzo's surplus jumps to +4.34** (massively under-paid for his current-year impact)
- **Gobert's surplus is now -0.52** (slightly below his salary tier threshold)
- **Randle's surplus is similar at -2.57** (still the largest negative)
- **Naz remains positive at +1.70**

**The Gobert framing change:** he's no longer outproducing his $35M tier under 2025-26-only data. He's slightly under-producing it. This doesn't change the keep-Gobert recommendation (he's still a top-5 impact player and still has elite defense), but it changes the confidence and the salary justification.

**The DiVincenzo framing change:** his under-pay relative to current production is now extreme. At $12M for +4.84 RAPM, he's producing impact closer to a $40M tier player. This is normal for a player on a mid-tier contract who's playing at All-Star adjacent levels, but it strongly reinforces the "invest aggressively in his recovery and re-signing" recommendation.

## 5. Implications for Q8 final ship

### What changes in the Q8 framing

**The Gobert keep case:**
- 3-year pooled framing: "He's the #1 RAPM in the sample at +6.18. Outproduces his contract tier by +3.68 surplus. The trade case is clearly weak."
- 2025-26-only framing: "He's still a top-5 impact player and still has elite defense. But his offensive impact has declined meaningfully. He's slightly under-producing his $35M tier threshold in current-year terms. The keep-Gobert case for 2026-27 holds (with elite defense + Category B around him), but the long-term commitment is less obvious. [REVISED 2026-05-18:] The previous note here said the 2027-28 non-guaranteed year gives the team optionality. That framing was wrong. Gobert's 2027-28 ($38M) is a PLAYER OPTION that Gobert will almost certainly exercise. The team does not have free optionality. The team's options to remove him from 2027-28 are trade (cleanest window: summer 2026 or trade deadline 2027) or pay $38M."

The honest framing: **Gobert is declining but is still a positive contributor.** The decision for 2026-27 is keep. [REVISED:] The decision for 2027-28 is NOT a passive evaluation; it is an active trade-or-pay decision because Gobert holds the option year. If the team wants to extract value via trade, the windows are summer 2026 and trade deadline 2027 (before his $38M locks in). Summer 2027 trades become harder as acquiring teams must absorb the option-year salary.

**The DiVincenzo case:**
- 3-year pooled framing: "+1.35 RAPM positive contributor. 12-point on/off swing. Category B mechanism confirmed. Achilles tear creates a gap that requires Q5 Path 2 acquisition."
- 2025-26-only framing: "+4.84 RAPM, **#1 in the 2025-26 sample**. Best impact player on the team by RAPM. Achilles tear means the team is losing its highest-impact non-Edwards player. Q5 Path 2 acquisition is even more urgent. Re-signing him aggressively in summer 2027 if he proves out is the right play."

The honest framing: **DiVincenzo's value is even larger than v1 implied.** This changes how Q5 should weight Path 2 acquisition and DiVincenzo retention.

**The Randle case:**
- 3-year pooled framing: "-0.88 RAPM, rank #468. Approximately neutral. Move only if clear upgrade available."
- 2025-26-only framing: "-0.07 RAPM, essentially neutral. Salary surplus -2.57 (clear underpay vs tier). Move only if clear upgrade available, salary gap makes the upgrade case more pressing."

The honest framing: **Randle's recent RAPM is closer to neutral than negative.** The case for moving him doesn't strengthen with this data; it slightly weakens. The salary-efficiency case for moving him (the v2 addendum framing) remains the strongest part of the trade argument.

### What doesn't change

**The DiVincenzo non-decision framing:** he's locked in by contract and injury through 2026-27. The team's job is to plan around the recovery and protect his summer 2027 free agency value.

**The "Scenarios B and D unsupported" verdict:** Trading Gobert remains weakly supported (he's still top-5 in the league sample in 2025-26 and the team's clearest defensive anchor). Trading both is even weaker.

**The "keep all three, plan for 2027 reset, pursue Category B" recommendation framework.**

## 6. Updated probability assignments

| Question | v1 | Addendum | 2025-26-only update |
|---|---|---|---|
| Gobert is a net negative on the current roster | 15-25% | (same) | **20-30%** (slightly up due to current-year decline) |
| Gobert would be net positive with Category B fully in place | 70-85% | (same) | 65-80% (slightly down, same reason) |
| Realistic trade return for Gobert improves championship odds | 20-30% | (same) | 25-35% (slightly up; current-year impact lower means easier to replace) |
| Randle is a net negative on the current roster | 30-45% | (same) | **20-35%** (down; recent RAPM closer to neutral) |
| Randle is overpaid relative to production | (new in addendum) 70-85% | 70-85% | 75-90% (up; current-year RAPM still under tier threshold) |
| DiVincenzo recovers to meaningful 2026-27 contribution | 25-40% | (same) | (same) |
| DiVincenzo Category B gap requires external acquisition | 75-85% | (same) | **80-90%** (up; recent RAPM shows he was the team's #1 impact player; gap is larger than v1 implied) |

## 7. Implications for Q5 paths

**Path 1 (Edwards development):** Unchanged. His offensive impact is established.

**Path 2 (Category B acquisition):** Even more urgent. DiVincenzo was the team's #1 impact player by 2025-26-only RAPM. His loss is the largest single negative-shock the roster has absorbed. External Category B for 2026-27 should be the #1 priority for the front office.

**Path 3 (system change to restore designed actions):** Even more urgent. Gobert's offensive RAPM decline (-2.5 YoY) is plausibly system-driven (KAT departure, less designed off-ball motion). If Q0D (coaching system analysis) confirms a system shift, restoring the 2024-25 RS offensive shape could partially close Gobert's offensive cost.

**Path 4 (frontcourt restructuring):** Stays weak. Gobert is declining but still top-5; Randle is closer to neutral than negative. The case for major frontcourt changes is not supported by either pooled or recent RAPM.

## 8. The bottom-line update

**Gobert is declining offensively but is still a top-5 impact player in the league by 2025-26-only RAPM (with sample caveats). His defense is essentially intact. The keep-Gobert recommendation for 2026-27 holds, with the understanding that his magnitude of impact has come down and the 2027-28 path forward is genuinely more open than the pooled RAPM suggested.**

**DiVincenzo's 2025-26-only RAPM at #1 in the sample (+4.84) is the most consequential single update.** It reinforces and sharpens the original recommendation: the team's #1 priority is protecting the Achilles recovery and adding Category B redundancy. The 2026-27 absence (or partial absence) of DiVincenzo is the largest negative-shock the roster will absorb.

**Randle's case is slightly weakened by 2025-26-only data.** He's closer to neutral than the pooled estimate suggested. The case for moving him rests primarily on the salary-efficiency gap (his $30M slot deployed elsewhere likely produces more) rather than on him being a clearly negative-impact player.

## 9. What this addendum still doesn't do

- **Full league-wide RAPM** (would resolve the Edwards artifact and improve benchmark calibration for the 2025-26-only estimates)
- **Defensive-anchor center age curve** (to project Gobert's likely 2026-27 and 2027-28 impact based on historical comps)
- **Achilles recovery comp set** (specific historical comps for guards in their late 20s)
- **Realistic trade market research**

All four are valuable for the final Q5 deliverable but none is blocking for moving to Q0D and Q3 next.

## 10. Artifacts

```
analyses/q2_localize/
  rapm_recent.py                  driver

outputs/tables/q2_localize/
  rapm_2025_only.csv              2025-26-only impacts for all qualifying players
  rapm_2025_vs_pooled.csv         Wolves rotation comparison table
```

Re-runnable: `python -m analyses.q2_localize.rapm_recent`.

## 11. Status

The blocking item for Q8 final ship is resolved. Gobert's 2025-26-only RAPM is +1.98, down from +6.18 pooled. The keep-Gobert recommendation survives (he's still top-5 league-wide and elite defensively), but the magnitude of his impact and the long-term commitment confidence both come down. DiVincenzo's 2025-26-only RAPM at #1 in the sample reinforces the urgency of Path 2 acquisition and recovery investment. Randle's case slightly weakens (closer to neutral); the salary-efficiency argument remains the strongest part of the trade case.

Per the data scientist's sequence: Q0D and Q3 are the next analyses, with Q5 spec revision after both surface their findings.
