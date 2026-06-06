# DiVincenzo lineup finding: confound check

**Date:** 2026-05-17
**Status:** Finding from prior session materially weakened. The headline does not survive scrutiny.
**Context:** The previous session reported that the Wolves' starting lineup with DiVincenzo (Edwards / McDaniels / Randle / Gobert / DiVincenzo) was +3.01 net rating across 44.7 playoff minutes, while the same four players with Dosunmu instead of DiVincenzo were -27.24 across 45.6 minutes. The data scientist asked for four confound checks before this finding carried weight in Q2 or Q8.

## Headline of this check

**The +3 vs -27 comparison is not what it appears to be.** The two lineups played in materially different contexts. The opponent confound is severe; the bootstrap confidence intervals overlap; the +3 vs -27 difference is not statistically distinguishable at 95% from this sample alone.

The finding survives in a much weaker form: the Dosunmu-led starting unit was bad in Round 2 vs San Antonio. We do not have a clean test of DiVincenzo vs Dosunmu in equivalent contexts.

## The four confound checks

### Check 1: Minutes by series

| Lineup | R1 vs DEN minutes | R2 vs SAS minutes |
|---|---|---|
| DiVincenzo | **44.7** | **0** |
| Dosunmu | 8.4 | **37.2** |

**This is the most severe confound by a wide margin.** The DiVincenzo lineup played 100% of its playoff minutes in Round 1 against Denver. The Dosunmu lineup played 82% of its playoff minutes in Round 2 against San Antonio. Round 2 against the Spurs (with Wembanyama defending) is a structurally much harder context, as documented in the LAFI Wolves diagnosis (Sharp LAFI gap MIN 90 vs SAS 27).

The +3 vs -27 comparison is mostly a R1-DEN-vs-R2-SAS comparison wearing DiVincenzo-vs-Dosunmu clothing.

### Check 2: Bootstrap 95% CI on net rating

1000 resamples, seed=42, stint-level resampling.

| Lineup | Point estimate | 95% CI |
|---|---|---|
| DiVincenzo | +3.01 | [-27.58, +34.11] |
| Dosunmu | -27.24 | [-56.84, +13.75] |

**The two confidence intervals overlap from -27.58 to +13.75.** The difference between the two point estimates is not statistically significant at 95% with this sample. The CIs are wide because each lineup has only ~45 minutes (well below the typical 200-300 minute threshold where lineup net rating starts to stabilize).

### Check 3: Score margin distribution at stint start

| Lineup | Mean margin | Median | Range | Close games (\|margin\| <= 5) | Trailing |
|---|---|---|---|---|---|
| DiVincenzo | +0.3 | 0 | [-11, +22] | 10 of 12 | 3 of 12 |
| Dosunmu | -3.6 | -1 | [-19, +5] | 10 of 14 | 7 of 14 |

The Dosunmu lineup was deployed slightly more often in trailing contexts (mean margin -3.6 vs +0.3). Both lineups played mostly close games, so this is a moderate context difference, not extreme. The Dosunmu lineup's R2 SAS stints in particular include several deep-trailing situations (start margins of -12, -13, -19) where the unit was likely playing catch-up.

### Check 4: Period distribution and stint lengths

| Lineup | Q1 stints | Q2 | Q3 | Q4 | Avg stint length |
|---|---|---|---|---|---|
| DiVincenzo | 4 | 2 | 2 | 4 | 3.7 min |
| Dosunmu | 4 | 2 | 4 | 4 | 3.3 min |

Both lineups have similar period distributions and stint lengths. This confound is not material.

## What the finding actually supports

**Honestly statable:**

- The DiVincenzo-anchored starting lineup was competitive against Denver in Round 1 (+3.01 over 44.7 min, but wide CI).
- The Dosunmu-anchored starting lineup was bad against San Antonio in Round 2 (-21.67 over 37.2 min, also wide CI).
- The Wolves never tested the DiVincenzo lineup against SAS (he was injured before R2).
- The Wolves used the Dosunmu lineup minimally against DEN (only 8.4 minutes, very small sample).

**Not statably from this comparison alone:**

- "DiVincenzo's absence caused the collapse." The opponent confound prevents this attribution.
- "Category B catch-and-shoot personnel is the difference between competitive and disastrous." The lineup-level evidence does not survive scrutiny at this sample size.
- Any quoted statistic comparing the two lineups' net ratings as if they played comparable opponents.

## What this means for Q2 and Q8

**Q2 Localize the Damage:** the DiVincenzo vs Dosunmu lineup comparison cannot be presented as a controlled test of Category B protection. Q2 should report both lineups' performance honestly with the opponent confound named explicitly. The comparison still has descriptive value (these were the two starting units across two series) but the causal framing has to be soft.

**Q8 DiVincenzo treatment:** the spec's H3a hypothesis ("DiVincenzo's 2024-25 contribution was a meaningful Category B asset in LAFI terms, and his absence is a primary driver of the 2025-26 Category B gap") cannot be supported from the playoff-lineup data alone. Q8 should look elsewhere for the evidence:

- 2024-25 vs 2025-26 team-level comparison with DiVincenzo on-floor minutes specifically (regular season sample is much larger)
- DiVincenzo's individual catch-and-shoot volume and accuracy across both seasons
- LAFI C5 component changes in MIN lineups with vs without him in 2024-25 (when he was healthy and available)

The playoff confound makes the 2024-25 regular-season comparison much more important than originally anticipated.

**Q5 Prescription Path 2:** the Category B path's evidence base from this specific comparison is weaker than the prior session suggested. Path 2 still has theoretical support from LAFI v1's structural analysis (the league-wide finding that catch-and-shoot personnel protects motion-dead offenses). The playoff lineup evidence is supplementary, not load-bearing.

## What this check did right

This is exactly the kind of "let the data lead" moment the project has been disciplined about. The prior session's headline was striking, and it would have been tempting to let it become a quoted statistic in Q2 and Q8. The confound check caught it before that happened.

The lesson worth preserving: **45 minutes per lineup is below the threshold where net ratings stabilize.** When lineup samples are small and the deployment context differs substantially across the compared units (different opponents, different game states), the headline numbers are descriptive at best, not causal. The bootstrap CI was the clearest signal: a +3 vs -27 gap with overlapping CIs from -56 to +34 is not the same as "the lineup architecture broke when DiVincenzo went down."

## Recommendation for the writeup

When this finding is referenced downstream:

1. State the descriptive comparison (Dosunmu starter unit at -27 vs SAS, DiVincenzo starter unit at +3 vs DEN).
2. State the opponent confound explicitly: "the comparison is largely between opponents, not between personnel."
3. State the sample size and CI: "each lineup played only 45 minutes; CIs are wide and overlap."
4. State the load-bearing finding clearly: "the lineup-level evidence is suggestive of Category B's importance but is not a controlled test. The structural evidence for Category B comes from LAFI v1's league-wide analysis (Section 5 of the LAFI deliverable), not from this lineup comparison."

This honesty is the project's competitive advantage. The DiVincenzo finding becomes weaker but the project's credibility stays intact.

## Artifacts

- Stint-level data: `outputs/tables/lineup_pipeline/stints_wolves_2025_26_playoffs.csv`
- Aggregated lineup totals: `outputs/tables/lineup_pipeline/lineup_totals_wolves_2025_26_playoffs_gt_filtered.csv`
- This findings document.
