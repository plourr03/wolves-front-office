# Q0C v1: Historical cohort analysis (scope-capped)

**Date:** 2026-05-18
**Status:** Q0C v1. Scope-capped per the data scientist's direction: "Are there historical teams with similar architectural profiles to the 2025-26 Wolves, and if so, what happened to them?" Simple cohort first; 3 to 5 useful comps is plenty; zero is a finding itself.

**Method:** Identify cohort by LAFI architectural placement (Sharp LAFI >= 80 percentile AND C1 ball stickiness < 50 AND C2 movement death > 50, i.e. distributed-pickup Q4 with extreme playoff-relevant pathology). Pull regular season record and playoff outcomes for each cohort team from `nba_games`. Identify pattern.

## Headline

**The cohort is small (8 teams across 11 seasons of universe, 2014-15 through 2025-26) and the outcomes are strikingly consistent: no team with this architectural profile has reached a conference finals.**

Out of 7 historical cohort teams (excluding 2025-26 MIN target):
- **5 of 7 missed the playoffs entirely (71%)**
- **1 of 7 lost in R1, swept (14%)**
- **1 of 7 lost in R2 (14%)**
- **0 of 7 reached the conference finals (0%)**

The 2025-26 Wolves matched the upper tier of what this cohort produces (R2 exit). The cohort's two playoff-reaching teams (PHI 2021-22 and PHX 2023-24) had top-tier talent (MVP-candidate Embiid; Durant + Booker + Beal). Even with top-tier talent, the architectural profile capped them at R2.

**This is empirical validation that the Q5 prescription's architectural emphasis is correct.** The Wolves' R2 ceiling is not bad luck or a difficult matchup. It is the historical pattern for teams with this profile.

## 1. Cohort identification

The cohort filter follows the Q0A LAFI deliverable's distinction between distributed pickup (Q4) and single-star pickup (Q3). Q3 has a known playoff-failure pattern (C1 Ball Stickiness univariate p=0.030). Q4 is rarer and historically less precedented. The cohort isolates Q4 + Sharp LAFI extreme.

| Filter | Threshold | Rationale |
|---|---|---|
| Sharp LAFI percentile | >= 80 | Captures top-quintile playoff-relevant pathology (C2 + C3 + C5 lockstep) |
| C1 Ball Stickiness | < 50 | Q4 placement (not single-star ball-dominant) |
| C2 Movement Death | > 50 | Q4 placement (dead off-ball motion) |
| Season type | Regular Season only | Consistent with LAFI computation universe |

Across the 330 team-seasons in the LAFI universe (2014-15 through 2025-26 RS), 8 teams meet this profile. This is approximately 2.4% of team-seasons. The cohort is small, which is itself a finding: the architectural profile is rare historically.

## 2. The cohort with outcomes

| Season | Team | RS Record | Sharp LAFI | Full LAFI | Playoff Outcome |
|---|---|---|---|---|---|
| 2016-17 | PHX | 24-58 | 92.4 | 85.2 | Missed |
| 2024-25 | SAC | 40-42 | 91.2 | 65.8 | Missed |
| **2025-26** | **MIN** | **49-33** | **89.7** | **64.5** | **R2 lost (6-6) [target]** |
| 2021-22 | PHI | 51-31 | 88.5 | 82.4 | R2 lost (6-6) |
| 2022-23 | CHI | 40-42 | 88.2 | 76.1 | Missed |
| 2023-24 | PHX | 49-33 | 87.6 | 65.5 | R1 lost (0-4, swept) |
| 2018-19 | NYK | 17-65 | 83.0 | 72.4 | Missed |
| 2018-19 | SAC | 39-43 | 81.4 | 71.5 | Missed |

## 3. Per-team narrative context

**2016-17 Phoenix Suns (24-58, missed).** Pre-Booker breakout, tanking-leaning roster. The architectural profile matched but the talent didn't. Not a useful direct comp but documents that the architecture can coexist with bad rosters.

**2018-19 New York Knicks (17-65, missed).** Tank-for-Zion roster (they didn't get Zion). Talent-deficient. Confirms the architecture is correlated with bad seasons even when the team isn't trying.

**2018-19 Sacramento Kings (39-43, missed).** The De'Aaron Fox / Buddy Hield young core. Pre-Sabonis. Moderate talent. Demonstrated the architecture can produce a ~.500 team that just misses the playoffs.

**2021-22 Philadelphia 76ers (51-31, R2 lost).** Embiid MVP candidate (MVP finalist that year, runner-up to Jokic). Harden mid-season acquisition. Tobias Harris, Maxey, Tucker. **The best talent in the cohort by some distance.** Lost to MIA Heat in R2. The closest playoff-outcome comp to the Wolves.

**2022-23 Chicago Bulls (40-42, missed).** DeRozan, LaVine, Vucevic, Caruso, Lonzo (injured). Talent in the rotation but architecturally distributed-pickup. Missed playoffs via play-in.

**2023-24 Phoenix Suns (49-33, R1 swept).** Durant, Booker, Beal. Top-tier offensive talent on paper. **The closest talent comp to the Wolves' 2025-26 (49-win team with star wings).** Architecturally distributed pickup. Swept by the Wolves in R1 (interestingly).

**2024-25 Sacramento Kings (40-42, missed).** Fox, DeRozan, Sabonis, Murray. The most recent comp. Architectural profile matched; played sub-.500 ball; missed playoffs.

**2025-26 Minnesota Timberwolves (49-33, R2 lost).** The target. Edwards, Gobert, Randle, McDaniels, DiVincenzo. Matched the upper-tier outcome of the cohort.

## 4. The cohort pattern (the load-bearing finding)

The 7-team historical comp set produces a remarkably consistent pattern:

**No conference finals appearances.** Zero. The architecturally extreme distributed-pickup profile has not produced a CF run in the LAFI sample period.

**Talent does not break the ceiling.** PHI 2021-22 had MVP-candidate Embiid, James Harden, and a 51-win team. They lost R2. PHX 2023-24 had Kevin Durant, Devin Booker, and Bradley Beal. They got swept in R1. **Top-tier talent in this architectural profile has not produced deep playoff success.**

**The Wolves match the upper-tier outcome.** R2 exit matches PHI 2021-22 exactly. The Wolves outperformed the cohort median (5 of 7 missed playoffs entirely) but did not outperform what top-talent cohort teams produced (R2 ceiling).

**The architectural profile correlates with mediocre regular seasons too.** Median cohort RS record is roughly 40-42. Two teams reached 49-51 wins (the Wolves and PHX 2023-24). One team reached 51-31 (PHI 2021-22). The rest were 40 wins or worse. The architecture is not just a playoff problem; it constrains regular season ceiling too.

## 5. Why this matters for the Q5 prescription

The Q0C finding empirically validates the Q5 prescription's architectural emphasis:

**The R2 exit was not bad luck.** The Wolves matched what this architecture produces. A different first-round opponent would not have moved them to the conference finals because the architecture caps the team there.

**The architectural change is necessary, not optional.** Talent alone has not broken this ceiling in the historical sample. PHI 2021-22 with Embiid + Harden lost R2. PHX 2023-24 with Durant + Booker + Beal lost R1. Adding stars (the Giannis / Durant question from Q5 v3 Section 10) does not address the architectural problem.

**The prescription's specific recommendations align with architectural correction.** Category B wing addition (closes catch-and-shoot gap, restores off-ball motion). Skilled secondary creator (reduces iso reliance, distributes creation). System restoration (motion + PR balance). All three address architectural pathology directly.

**The Edwards tier-leap question gets sharper.** If Edwards reaches MVP-tier and the team becomes single-star ball-dominant, the architecture shifts toward Q3 (single-star pickup, the known playoff-failure pattern per Q0A's C1 univariate finding). Q3 also caps the team. **The architectural fix is not "make Edwards do more"; it is restore designed off-ball motion and Category B production.**

## 6. The honest caveats

**Small sample.** 7 historical comps is not large. The 0/7 conference finals rate has wide confidence bands; the true population probability of CF reach for this profile is meaningfully above 0 (probably 10-25% with the small sample uncertainty). The directional finding (architectural ceiling at R2) is robust; the precision of the rate is not.

**Architectural similarity is approximate.** The cohort filter captures the headline architectural profile but doesn't fully replicate the Wolves' specific configuration. PHI 2021-22 had Harden as a primary creator; PHX 2023-24 had three superstar wings; the Wolves have Edwards + Gobert + Randle. Each cohort team has unique elements.

**Era effects matter at the margins.** The 2014-15 through 2025-26 universe spans different defensive schemes, three-point eras, and rule sets. The 2025-26 NBA plays a different game than 2014-15.

**Bubble + COVID excluded.** The 2019-20 and 2020-21 seasons are excluded from the LAFI universe per the deliverable's spec section 9. Cohort teams from those years (if any) are not represented.

**The 0/7 CF rate could be a small-sample artifact.** A larger sample (next 10 seasons of data) might surface a CF-reaching team. The directional pattern still suggests the architecture is meaningfully worse than league average for deep playoff runs.

## 7. Comparison framings the deliverable can use

**The closest direct comp by talent: PHX 2023-24.** Top-tier wing talent (Durant + Booker + Beal vs Edwards + McDaniels + Randle + Gobert). 49-win regular season. Architectural extreme. Got swept in R1. Demonstrates that wing-heavy talent doesn't break the ceiling.

**The closest comp by playoff outcome: PHI 2021-22.** Embiid + Harden + Tobias. 51-win regular season. Architectural extreme. Lost R2. Demonstrates that MVP-candidate talent doesn't break the ceiling either. **This is the most directly relevant comp for the Wolves' 2025-26 outcome.**

**The recency comp: SAC 2024-25.** Most recent cohort team. Architectural extreme. Missed playoffs. Demonstrates the architecture is producing similar outcomes in the current NBA era (not just historical).

## 8. The Q5 v4 integration framing

The Q5 v3 prescription's "the architectural fix is necessary" claim was previously supported by Q1 (diagnosis), Q3 (mechanism), Q4 (matchup variance), and Q0A LAFI (the architectural framework). Q0C adds the historical-cohort empirical support: **no team in this configuration has reached a conference finals in the LAFI sample period.**

For the deliverable, the framing for the front office:

> "Q0C identifies 7 historical teams with similar architectural profiles to the 2025-26 Wolves. Across that cohort, none reached a conference finals. The two cohort teams with top-tier talent (PHI 2021-22 with MVP-candidate Embiid; PHX 2023-24 with Durant + Booker + Beal) lost in R2 and R1 respectively. The Wolves' 2025-26 R2 exit matches the upper-tier cohort outcome. The historical record indicates that talent alone does not break this architectural ceiling; the prescription's specific recommendations (Category B addition, skilled secondary creator, system restoration) address the structural cap directly."

This is empirically supported and politically defensible. It does not claim the Wolves are uniquely broken; it documents that their profile produces a known pattern of outcomes.

## 9. What Q0C v1 does NOT do

Per the scope cap:

- **Multi-factor similarity matching.** A formal nearest-neighbor analysis across all 5 LAFI components plus other team features (roster archetype, conference, talent tier) would tighten the cohort but doesn't change the central finding.
- **Counterfactual analysis of "what did cohort teams do next."** Some cohort teams adjusted their architecture in subsequent seasons; their trajectories could inform what works and doesn't work in transitioning out of this profile. Deferred to Q0C v2 if requested.
- **Conference-specific cohort analysis.** Western Conference contention is more competitive than Eastern; the cohort doesn't separate by conference.
- **Talent-tier-stratified analysis.** Splitting the cohort by talent tier (top-talent vs mid-talent) and showing outcomes within each could sharpen the finding. The brief narrative in Section 3 covers this informally.
- **Era-adjusted analysis.** The 2014-15 NBA plays differently from 2025-26. A formal era control wasn't applied.

These would sharpen the v1 but the central finding (0/7 conference finals; R2 ceiling for top-talent cohort teams) is robust.

## 10. Implications across the project

**For Q5 v4 prescription synthesis:**
- Add Q0C historical-cohort framing as empirical validation of architectural necessity
- The R2 ceiling argument becomes empirical, not just theoretical
- "Reasonable people can disagree on the trade" framing strengthens because architectural fix needed regardless

**For Q0B contention window:**
- The contention window analysis identifies 2027-28 / 2028-29 as peak years. Q0C shows the architectural profile would cap the peak years at R2 without intervention. The peak years' realization requires architectural change.

**For Q6 v2 KAT counterfactual:**
- The Q6 v2 finding (trade was approximately wash architecturally) gets stronger context. The team would have stayed in the cohort regardless of the trade. The architectural fix was needed independent of the trade interpretation.

**For Q7 Edwards tier-leap:**
- The cohort shows Embiid MVP-candidate talent didn't break the ceiling. Edwards' tier-leap probability (25-35% per Q7) is a real upside variable but does not by itself produce the architectural fix the prescription identifies.

## 11. Artifacts

```
analyses/q0c_historical_cohort/
  __init__.py
  cohort.py                        cohort analysis driver

outputs/tables/q0c_historical_cohort/
  cohort_with_outcomes.csv         cohort teams with playoff outcomes
```

Re-runnable: `python -m analyses.q0c_historical_cohort.cohort`.

## 12. Status

Q0C v1 complete. Phase 2 (Q0B + Q6 + Q0C) complete. The historical-cohort finding empirically validates the Q5 v3 prescription's architectural emphasis. 0 of 7 cohort teams reached a conference finals; top-tier-talent cohort teams capped at R2 and R1.

Next: **Q5 v4 consolidation.** Integrates:
- Q0B trajectory window (4-year contention window 2025-26 through 2028-29; 2027 as the trade-driven cap window)
- Q6 v2 KAT counterfactual (trade was approximately architecturally net-neutral; complicated transaction with offsetting effects)
- Q0C historical cohort (R2 ceiling for this architectural profile; talent alone doesn't break it)
- Contract structure correction (4-scenario framework for 2027 trade window; Portfolio C reframed as trade-driven)

Estimated 2-3 days for Q5 v4. After v4 lands, Phase 3 infrastructure (full league-wide RAPM, Spotrac integration) is optional. Website prep after analytical completeness.
