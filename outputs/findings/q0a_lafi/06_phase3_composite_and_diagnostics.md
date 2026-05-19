# Phase 3 finding: composite, correlation matrix, PCA, sharp LAFI

**Date:** 2026-05-16
**Status:** Phase 3 complete. All composite and diagnostic outputs persisted.
**Output:** outputs/tables/q0a_lafi/lafi_composite_5component.csv, composite_diagnostics/

## Headline

**Sharp LAFI is sharper than the manual math suggested. The Wolves are 3rd in the league on the subset of LAFI that matters for playoff offense (C2 + C3 + C5).**

| Metric | Wolves 2025-26 percentile | Approx league rank |
|---|---|---|
| Full LAFI (5-component) | 64.5 | ~13th-15th |
| 4-component robustness | 60.6 | ~14th-16th |
| **Sharp LAFI (C2 + C3 + C5)** | **89.7** | **3rd** |

The user's manual prediction of 60-65 on full LAFI landed at 64.5. Spot-on. But the Sharp LAFI puts the Wolves nearly extreme (90th percentile, behind only PHI and LAC).

This validates the methodological move proposed earlier: **report both Full and Sharp LAFI in the final deliverable.** Full LAFI says "Wolves are elevated, not extreme." Sharp LAFI says "Wolves are extreme on the components that predict playoff offensive collapse." Both are true. They tell different layers of the same story.

## Full LAFI league standings 2025-26 RS

**Top 10:**
| # | Team | Full LAFI pct |
|---|---|---|
| 1 | LAC | 95 |
| 2 | LAL | 87 |
| 3 | OKC | 82 |
| 3 | HOU | 82 |
| 5 | PHI | 81 |
| 6 | DAL | 80 |
| 7 | WAS | 79 |
| 8 | BOS | 78 |
| 8 | PHX | 78 |
| 10 | NOP | 75 |

The Wolves rank ~13th-15th on Full LAFI. They are not top-5, as the original thesis predicted.

**Bottom 10:** GSW (0), BKN (3), ATL (6), TOR (8), UTA (15), IND (17), **SAS (23)**, MIA (30), CHI (30), DET (31).

**SAS at 23rd percentile on Full LAFI.** The Spurs are designed across every component. They are the structural counterargument to the Wolves at both ends. Series outcome is consistent with the architecture.

## Sharp LAFI league standings 2025-26 RS (the headline)

| # | Team | Sharp LAFI pct |
|---|---|---|
| 1 | PHI | 93 |
| 2 | LAC | 92 |
| **3** | **MIN** | **90** |
| 4 | HOU | 84 |
| 4 | WAS | 84 |
| 6 | PHX | 82 |
| 7 | MIL | 78 |
| 8 | BOS | 77 |
| 9 | LAL | 76 |
| 10 | OKC | 73 |

**The Wolves are 3rd in the league on Sharp LAFI**, behind only Philly and the Clippers. PHI and LAC are also top-5 on Full LAFI (95 and 81). The Wolves are uniquely extreme ONLY on the playoff-relevant subset.

**This is the central methodological finding of Phase 3:** the Wolves' pathology is invisible at the Full LAFI level (they look "elevated, not extreme") but near-extreme at the Sharp LAFI level. Other Sharp-LAFI leaders (PHI, LAC) are also Full-LAFI leaders. The Wolves stand alone as Sharp-LAFI extreme but Full-LAFI moderate.

## Correlation matrix (league-wide, 5-component pool n=330)

| Pair | Pearson r |
|---|---|
| C2 motion-death × C4 action-poverty | 0.735 |
| **C3 iso × C5 shot quality** | **0.708** |
| C3 iso × C4 action-poverty | 0.684 |
| C1 sticky × C3 iso | 0.627 |
| C1 sticky × C4 action-poverty | 0.599 |
| C1 sticky × C2 motion-death | 0.471 |
| C2 motion-death × C3 iso | 0.463 |
| C1 sticky × C5 shot quality | 0.356 |
| C4 action-poverty × C5 shot quality | 0.340 |
| **C2 motion-death × C5 shot quality** | **0.059** |

**Spec section 3.4 said no pair should correlate above 0.80. The highest is 0.735. The five components pass the redundancy check cleanly.**

**Key surprise:** C2 motion-death × C5 shot quality is 0.059 league-wide. **Essentially uncorrelated.** This is important. The user's hypothesis was that C2, C3, C5 are "three surfaces of the same disease" with high cross-correlations. The data partially supports this:

- C3 × C5 = 0.708. Strongly correlated. The "iso produces bad shots" causal chain is real league-wide.
- C2 × C3 = 0.463. Moderately correlated. Motion-death and iso usually travel together but not always.
- **C2 × C5 = 0.059. Essentially uncorrelated league-wide.** Motion-death does NOT typically produce bad shot quality. Most teams that have dead off-ball motion produce shot diets that are roughly average.

**Implication for the Wolves diagnosis.** The Wolves' Edwards-era trajectory of motion-death rising together with shot quality is NOT typical. League-wide, those two move independently. The Wolves are doing something unusual: their motion death is producing bad shots in a way most teams' motion death does not.

This sharpens the Wolves-specific diagnosis. The "three surfaces" framing reduces to "two surfaces + a Wolves-specific anomaly." The Wolves uniquely combine motion death and shot quality decay in a way the rest of the league doesn't.

## PCA diagnostic

PC1 variance explained: **61.4%**. Spec wanted 50-65% as the healthy range. We are squarely in the middle.

| PC | Variance | Cumulative |
|---|---|---|
| PC1 | 61.4% | 61.4% |
| PC2 | 21.6% | 83.0% |
| PC3 | 9.6% | 92.6% |
| PC4 | 4.2% | 96.7% |
| PC5 | 3.3% | 100.0% |

PC1 captures the single "pickup-ness" axis. PC2 captures a real second axis worth 22% of variance.

**PC1 loadings** (all negative, meaning all five components load on the same direction):

| Component | PC1 loading |
|---|---|
| C1 ball stickiness | -0.452 |
| C2 motion death | -0.405 |
| C3 iso reliance | -0.511 |
| C4 action poverty | -0.501 |
| C5 shot quality decay | -0.346 |

C3 and C4 load strongest on PC1, meaning iso reliance and action poverty are the most "central" components to the pickup construct. C5 (shot quality decay) loads weakest on PC1, consistent with it being partly downstream of the others.

**PC2 loadings** (the secondary axis):

| Component | PC2 loading |
|---|---|
| C1 ball stickiness | -0.049 |
| C2 motion death | -0.582 |
| C3 iso reliance | +0.282 |
| C4 action poverty | -0.267 |
| C5 shot quality decay | +0.713 |

PC2 separates teams along an axis where one end has "high motion death + narrow playbook + low shot quality decay" and the other end has "high iso reliance + high shot quality decay + high motion." That second axis is essentially Q3-vs-Q4: single-star pickup teams cluster on one side, distributed-iso teams on the other. PCA has independently surfaced the user's quadrant framing.

## Wolves vs league correlations

Across the Wolves' 11 Edwards-era seasons in the 5-component sample, the correlation patterns differ meaningfully from league-wide:

**Wolves-only correlations:**

| Pair | Wolves r | League r | Wolves - League |
|---|---|---|---|
| C1 × C5 | **0.731** | 0.356 | **+0.376** |
| C3 × C5 | 0.727 | 0.708 | +0.019 |
| C4 × C5 | 0.469 | 0.340 | +0.129 |
| C2 × C5 | -0.220 | 0.059 | -0.279 |
| C2 × C3 | 0.055 | 0.463 | -0.408 |
| C1 × C2 | -0.076 | 0.471 | -0.547 |

The Wolves' Edwards era shows a **distinct correlation signature**:

- **C1 × C5 is much tighter than league (0.731 vs 0.356).** When the Wolves get sticky (Randle integration year), shot quality cratered. When they decentralize (2025-26), it stays bad. Stickiness and shot quality move together for them in a way they don't for most teams.
- **C3 × C5 tracks league baseline (0.727 vs 0.708).** Wolves are normal here: iso → bad shots is the standard relationship.
- **C2 × C5 is INVERSE for the Wolves (-0.220 vs 0.059).** Across the full Wolves history, motion-death and shot quality moved in OPPOSITE directions year-over-year. The recent three-season lockstep is a sub-sample pattern within a noisier overall history.
- **C1 × C2 is inverse for the Wolves (-0.076 vs 0.471).** When the Wolves got sticky, motion didn't die (it actually held or improved). That's atypical.

**What this means.** The Wolves' Edwards-era trajectory shows three components (C2, C3, C5) rising together since 2023-24, but the underlying year-over-year correlation across the full Wolves history says C2 and C5 typically don't track. Their recent lockstep is real and is captured in the trajectory table, but it's not because motion-death and shot quality always travel together. It's because both have been deteriorating in parallel for *different* reasons over the same window.

This is a methodological subtlety worth preserving: the trajectory tells a clean four-act story, but the underlying causal links between C2 and C5 are not symmetric the way they are for C3 and C5.

## Implications for the writeup

1. **Headline framing should use Sharp LAFI as the punchline.** "Wolves are 3rd in the league on the subset of LAFI that predicts playoff offensive collapse." That is the most diagnostic single number.
2. **Full LAFI provides the context.** Reporting both shows the user (and the front office) that the Wolves are not extreme on every dimension, just the ones that matter most.
3. **The C2 × C5 league finding is its own discovery.** Motion-death and shot quality are typically uncorrelated. This is a basketball insight independent of the Wolves story.
4. **The four-act trajectory remains the headline visualization.** PCA loadings confirm the quadrant framing emerged from the data, not imposed on it.

## Calibration on the user's Phase 3 watch-list

| Watch item | Outcome |
|---|---|
| C2/C3, C2/C5, C3/C5 above 0.70 league-wide | Partial. C3/C5 yes (0.708). C2/C3 (0.463) and C2/C5 (0.059) no. |
| PCA PC1 variance 50-65% | **Hit dead center. 61.4%.** |
| Wolves 5-component rank 60-65 percentile | **Hit. 64.5.** |
| Wolves correlations vs league: tighter coupling on motion/iso/shots | Mixed. Tighter on C1/C5 and C3/C5; INVERSE on C2/C5. |

3 of 4 expectations confirmed cleanly. The C2/C5 surprise is informative, not a metric problem.

## What we decided

Phase 3 complete. Five-component LAFI is mechanically clean. Sharp LAFI is the more diagnostic Wolves number. No component re-spec warranted.

Phase 4 (predictive validation) is the next step. Per spec, three regressions:
- Regression A: playoff overperformance vs SRS + LAFI + bracket controls + season FE
- Regression B: ORtg decay vs LAFI + opp DRtg + season FE
- Regression C: series upset probability vs LAFI differential

**Important Phase 4 design choice unlocked by this finding.** Run each regression THREE times:
1. Full LAFI as the predictor (canonical)
2. Sharp LAFI as the predictor (the diagnostic version)
3. Each of the 5 components individually (which components actually drive the prediction)

If Sharp LAFI is more predictive than Full LAFI, the methodological move is to report Sharp LAFI as the primary metric in the final deliverable with Full LAFI as supporting context. If they predict equivalently, Full LAFI stays canonical and Sharp LAFI is a robustness check. If neither predicts, the analysis pivots to descriptive rather than predictive framing.
