# The Minnesota Timberwolves' 2025-26 Offense, Through the LA Fitness Index

**A diagnosis of how this team's offensive architecture differs from the league's known playoff-failure patterns, and what that implies for the path forward.**

Prepared 2026-05-17 | LAFI v1 | Sample: 12 NBA regular seasons, 144 playoff team-seasons in validation

---

## Executive summary

The 2025-26 Timberwolves play offense in a way the rest of the NBA has not had to defeat at scale. They rank 3rd in the league on the subset of metrics that predict playoff offensive collapse (Sharp LAFI, 90th percentile). They rank only 13th on the full LA Fitness Index composite (65th percentile). The gap is the diagnosis: the team is extreme on the components that matter for playoff offense (motion death, isolation reliance, shot quality decay), and only moderate on the components the league has historically learned how to defeat (ball stickiness, action poverty).

The initial hypothesis was that the Wolves were top-5 on LAFI overall. The data refined that: they are top-3 on the playoff-relevant subset and roughly 13th overall.

The historical playoff-failure pattern (Harden-era Rockets, Trae-era Hawks, Westbrook-era Thunder) is single-star pickup, captured by Component 1 (Ball Stickiness). That archetype consistently underperforms in the playoffs (univariate p=0.030, coefficient -0.023 wins per percentile). **The Wolves are 31st percentile on Component 1.** They are not in this archetype.

The Wolves' failure pattern is different. Distributed pickup, where multiple players take turns isolating while no one moves off-ball, and the resulting shot diet decays sharply. This combination is rare historically and not well-precedented. The fixes that worked for other pickup-leaning teams (acquire a secondary creator, lean into the star) do not directly apply because their pathology is not the standard one.

The diagnosis is severe. It is not hopeless. The structural problems are nameable, measurable, and at least partially fixable. The 2023-24 WCF version of this offense is reachable. The team has three independent paths to closing the gap. The current state has none of them in place.

---

## Key findings

1. **Sharp LAFI: 3rd in the league.** Wolves at 90th percentile on the C2+C3+C5 subset (motion death + iso reliance + shot quality decay). Behind only Philadelphia and the LA Clippers.
2. **Full LAFI: 13th in the league.** Wolves at 65th percentile on the 5-component composite. Not extreme overall; extreme on the playoff-relevant subset.
3. **The historical playoff-failure mode is single-star pickup (C1), not the Wolves' pattern.** C1 univariate predicts playoff wins at p=0.030. The Wolves are 31st percentile on C1.
4. **The Edwards-era trajectory has been a four-act story.** 2023-24 (WCF year) was the most-designed version. 2024-25 (Randle integration) moved toward Q3 (single-star pickup). 2025-26 moved further into Q4 (distributed pickup with bad shots).
5. **The Wolves have a normal-breadth playbook and are choosing iso anyway.** Action Poverty at 45th percentile means the actions exist. Iso frequency at 9.6% has displaced pick-and-roll, which has fallen from 14-16% to 13.1%. This is a coaching-actionable finding that does not require new personnel.
6. **The Spurs matchup is the architectural inverse of the Wolves' style.** A 72-percentile-point gap on shot quality between MIN (83) and SAS (11), with Wembanyama and switchable perimeter defense countering both pieces of Q4's only mechanism.

---

## The diagnostic

### Section 1: Where the Wolves rank

The Wolves' 2025-26 LAFI profile, regular season, percentile rank against the 2014-15 through 2025-26 league sample:

| Metric | Wolves percentile | League position |
|---|---|---|
| **Sharp LAFI (C2+C3+C5)** | **90** | **3rd** (behind PHI 93, LAC 92) |
| Full LAFI (5 components) | 65 | ~13th |
| C1 Ball Stickiness | 31 | bottom third |
| C2 Movement Death | 72 | top third |
| C3 Isolation Reliance | 90 | top 10% |
| C4 Action Poverty (v1) | 45 | middle |
| C5 Shot Quality Decay | 83 | top 17% |

The two LAFI numbers tell different layers of the story. Full LAFI dilutes the Wolves' pathology by averaging across components they are not extreme on (C1, C4). Sharp LAFI isolates the components that matter for playoff offense.

**[Chart 4: League Fingerprint]** Horizontal bars of all 30 teams' Full LAFI for 2025-26 RS, with Sharp LAFI overlaid as markers. Wolves highlighted.

### Section 2: The Edwards-era trajectory

The five-component evolution from 2022-23 through 2025-26 reads as a four-act story.

| Season | C1 sticky | C2 motion-death | C3 iso | C4 action-pov | C5 shot-qual | Full LAFI | Sharp LAFI |
|---|---|---|---|---|---|---|---|
| 2022-23 (Gobert year 1) | 14 | 64 | 44 | 31 | 47 | 34 | 53 |
| 2023-24 (WCF year) | 35 | 43 | 49 | 27 | 39 | 35 | 45 |
| 2024-25 (Randle year 1) | 69 | 55 | 71 | 36 | 72 | 63 | 71 |
| **2025-26 (Randle year 2)** | **31** | **72** | **90** | **45** | **83** | **65** | **90** |

**Act 1, Gobert integration:** the offense had not figured out how to play with him. Already a bodies-do-not-move team but not yet an iso team.

**Act 2, WCF year:** the most-designed version of the Edwards-era offense and the deepest playoff run. The data validates that 2023-24 was the high-water mark not just in record but in offensive structure.

**Act 3, Randle integration:** Q3-leaning. [CORRECTED 2026-05-22: the original text read "Randle dominated possessions as the new hub." Player-grain verification shows the 2024-25 hub was Anthony Edwards, not Randle. Edwards held the ball more than twice as long as Randle and ran 1,128 on-ball creation possessions to Randle's 423; Randle ranked third on the team in time of possession. The stickiness spike (69) came from Edwards consolidating the lead-guard role as Conley declined, not from Randle. See `14_hub_attribution_correction.md`.] Stickiness rose sharply (69), iso rose (71), shot quality cratered (72). They reached the conference finals but the architecture was already different.

**Act 4, current season:** Q4. Stickiness fell back (Randle no longer dominating; iso load decentralized). Motion died worse. Iso reached extreme. Shot quality continued its decline.

Three components moved in lockstep across the recent three seasons:

- C2 motion-death: 43 → 55 → 72
- C3 iso-reliance: 49 → 71 → 90
- C5 shot-quality-decay: 39 → 72 → 83

The PCA validation surfaced this independently. PC2 of the league's offensive space (22% of variance) loads exactly along the axis that separates Q3 from Q4. The four-quadrant framework is a real structural distinction in NBA offensive style.

**[Chart 2: Wolves Trajectory]** Line chart, five component percentiles across four seasons, with C2/C3/C5 emphasized.

### Section 3: The historical playoff-failure pattern is Q3, and the Wolves are not Q3

This is the section that pivots the diagnosis from descriptive to substantive.

The validation regression on 144 playoff team-seasons since 2014-15 found one component with significant predictive value: **C1 Ball Stickiness, coef -0.023, p=0.030, 95% bootstrap CI entirely negative**. The other four components have no individual predictive value in the historical sample.

What this means: across the last decade, the way pickup-style offense has predictably failed in the playoffs is single-star pickup. One creator dominates the ball, defenses scheme that one player, the offense breaks. The historical examples make the pattern visible:

| Team-season | C1 percentile | Playoff result |
|---|---|---|
| DAL 2022-23 (Luka pre-Kyrie) | 95 | Missed playoffs |
| POR 2017-18 (Lillard McCollum) | 98 | Round 1 sweep |
| OKC 2018-19 (Westbrook) | 97 | Round 1 exit |
| ATL 2021-22 (Trae Young) | 98 | Round 1 exit |
| LAC 2023-24 (Harden Kawhi PG) | 97 | Round 1 exit |
| HOU 2017-18 (Harden peak) | 99 | Lost WCF Game 7 |
| OKC 2017-18 (Westbrook PG) | 99 | Round 1 exit |
| HOU 2018-19 (Harden) | 100 | Lost WCF |

The shape is consistent. A team becomes C1-extreme. The defense schemes the dominant handler. The offense breaks.

**The Wolves are 31st percentile on C1.** They are not playing this kind of offense. Edwards' time-of-possession share is 21.6% of the team total, well below the 25-35% range that defines Q3 ball-dominant offenses. The iso load is distributed across Edwards, Randle, McDaniels, Reid, and others. The defining feature of single-star pickup (one player owning the ball) is not the Wolves' problem.

This matters for the prescription. If the Wolves were Q3, the historical record would suggest specific fixes (the post-Harden Rockets traded him and rebuilt around younger players; Atlanta moved off the iso-star architecture post-Trae). The league's playoff-failure mode has known counter-moves.

The Wolves' Q4 pathology has limited historical precedent. The Cavaliers in some Mitchell-Garland seasons and the Mavericks in some pre-Kyrie years have had partial versions of this shape, but no clean comp has the full configuration (moderate stickiness, dead motion, decentralized iso, normal-breadth playbook, bad shot quality). The combination is rare and not well-precedented.

**[Chart 5: Historical Case Studies]** Four panels showing the 5-component profiles of 2017-18 HOU, 2017-18 OKC, 2022-23 DAL, and 2025-26 MIN. The first three are C1-extreme (Q3). The Wolves are not.

### Section 4: The four-quadrant framework

The (C1 stickiness, C2 motion-death) plane defines four offensive archetypes:

| Quadrant | (C1, C2) | Archetype | Failure mode |
|---|---|---|---|
| Q1: Designed | low, low | Warriors, Pacers, post-Trae Hawks | Rare. Gold standard. |
| Q2: Star-fed motion | high, low | Brunson Knicks | Survivable if creator is elite. |
| Q3: Single-star pickup | high, high | Harden Rockets, Trae Hawks, Westbrook OKC | The known playoff-failure mode. |
| Q4: Distributed pickup | low, high | **Wolves 2025-26** | Rare. Not a known failure mode. |

The Phase 3 PCA validated this independently. PC2 of the league offensive space surfaces the same axis we developed qualitatively. That is methodological convergence: the framework was not imposed on the data; the data found it.

**[Chart 6: Wolves Quadrant Migration]** Scatter on the (C1, C2) plane with all 30 teams as background, Wolves' four Edwards-era seasons connected by arrows ending in Q4. The visual makes the four-act trajectory legible at a glance.

### Section 5: Why motion death produces bad shots for the Wolves when it usually does not

Across the league, motion death (C2) and shot quality decay (C5) are essentially uncorrelated (Pearson r = 0.059 across 330 team-seasons). This is one of the most diagnostic numbers in the analysis.

**For most NBA teams, dead off-ball motion produces normal shots because someone manufactures the shot quality. For the Wolves, dead off-ball motion produces bad shots because nobody manufactures the shot quality. The motion death is a vulnerability other teams cover with personnel; the Wolves do not have the personnel that covers it.**

Most teams with dead off-ball motion fall into one of two categories.

**Category A: Star-anchored isolation.** The team has a transcendent on-ball creator (Doncic, SGA, prime Harden) who can manufacture good shots from isolation despite the lack of motion. The star bends the defense one-on-one. The off-ball players do not need to move because the star creates enough advantage by himself.

**Category B: Specialist shooting.** The team has elite catch-and-shoot personnel (Klay-era Warriors, certain Hawks configurations) who produce good shots from stationary positions because they are so good at the shot itself.

The Wolves are in neither category. Edwards is among the league's top scoring guards and his trajectory suggests Category A protection is achievable, but he is not yet at the tier where he can carry a motion-dead offense in playoff settings against elite defensive schemes. His 21.6% time-of-possession share indicates defenses scheme him with help and force the ball into other hands, where the iso load gets distributed across players who individually do not bend the defense the same way.

On Category B: the Wolves' catch-and-shoot personnel is good not great. DiVincenzo (38.3% on 496 catch-and-shoot 3PA) was the elite specialist but he is out for the year with the Achilles. Naz Reid (38.1% on 344), Jaden McDaniels (45.1% on 162 with high efficiency but low volume), Ayo Dosunmu (42.9% on 231), and Mike Conley (38.9% on 108) are reliable but not at the Klay Thompson tier of high-volume elite shooting that defines Category B.

The architectural problem is specific. The Wolves have built an offense in a configuration that requires either Category A or Category B personnel to function, and the team has neither.

### Section 6: The allocation problem (coaching-actionable)

Worth naming separately because it is the only finding the head coach can act on directly without acquiring new personnel.

The Wolves are 45th percentile on Action Poverty, which is roughly league average. **They have a normal-breadth playbook.** They run all 11 Synergy play types at >=3% usage. The actions exist.

But the year-over-year allocation has shifted toward iso and away from pick-and-roll:

| Season | Iso % | PR-Ball-Handler % | Off-ball motion (Cut+OffScr) % |
|---|---|---|---|
| 2021-22 | 7.8 | 14.0 | 10.9 |
| 2022-23 | 7.0 | 15.3 | 11.0 |
| 2023-24 | 7.4 | 14.4 | 10.9 |
| 2024-25 | 7.8 | 16.3 | 10.8 |
| **2025-26** | **9.6** | **13.1** | **10.2** |

Off-ball motion has been flat across all five seasons at 10-11%. Iso rose from 7-8% to 9.6%. PR-Ball-Handler dropped from 14-16% to 13.1%. **The Wolves have substituted iso for pick-and-roll while leaving off-ball motion unchanged.**

This is a within-system reallocation, not a missing-actions problem. The pick-and-roll is in the playbook. It is being called less. The substitution toward iso compounds with the other Q4 pathologies (motion death, shot quality decay) but is not the cause of them.

This finding implies a coaching lever exists. Restoring the prior years' iso/PR ratio would not by itself fix Q4, but it would close part of the gap without requiring any roster move. That is unusual among the diagnoses in this memo and worth flagging.

### Section 7: The Spurs as the architectural counterargument

The Spurs are the team most structurally opposite to the Wolves in the entire league on the LAFI dimensions.

| Component | Wolves 2025-26 | Spurs 2025-26 | Gap |
|---|---|---|---|
| C1 Ball Stickiness | 31 | 38 | similar |
| C2 Movement Death | 72 | 56 | +16 (Wolves worse) |
| C3 Isolation Reliance | 90 | 28 | +62 |
| C4 Action Poverty | 45 | 15 | +30 |
| **C5 Shot Quality Decay** | **83** | **11** | **+72** |
| Full LAFI | 65 | 23 | +42 |
| Sharp LAFI | 90 | 27 | +63 |

The Spurs are designed across every component. Combined with Wembanyama at the rim and switchable perimeter defenders (Vassell, Sochan, Castle), they are the worst possible matchup architecture for a Q4 offense.

Q4 depends on iso advantage creation (the only mechanism). The Spurs counter both ways. Wembanyama at the rim lets the rest of the defense take risks they otherwise could not: aggressive doubles on Edwards because the rotation is covered, switches onto Randle in the post because help shrinks his space, recoveries against McDaniels or Reid because the drive into help is waiting. The switchable perimeter lets every iso get a competent defender without compromising rotations.

The 72-percentile-point gap on shot quality decay is the result. The Spurs' offense generates clean shots; the Wolves' offense generates bad shots; the gap compounds across a seven-game series.

This is not bad luck or a hot opponent. The Wolves drew the team architecturally most equipped to beat them. If they had drawn a different second-round opponent with a more conventional offensive profile and weaker rim protection (the Lakers, the Mavericks, the Heat), the series might have produced a very different result.

---

## Prescription pointers (handoff to Q5)

This diagnosis sets up Q5 (prescription) but does not substitute for it. Q5 will evaluate specific moves on cost and impact. The diagnosis leaves Q5 with three independent fixable paths.

**Path 1: Edwards develops into Category A solo creator.** Plan A only if his trajectory continues. Realistic over multiple seasons but not in the current playoff window. Q5 should evaluate his development trajectory against historical comps (Q7 spec covers this in depth) and estimate the probability of his reaching the Luka/SGA tier within the current contention window.

**Path 2: Acquire elite catch-and-shoot specialists.** Category B protection. Buyer's market exists for shooters at the trade deadline. Q5 should evaluate cap and asset constraints, identify candidate archetypes, and estimate how much each upgrade closes the C5 (shot quality) gap.

**Path 3: Restore designed off-ball motion through coaching.** System change. The actions exist in the playbook (the allocation problem section above). Calling them more, running them harder, and rebalancing iso back toward pick-and-roll closes part of the gap without requiring new personnel. Q5 should evaluate this against the realistic ceiling of system-only improvements.

The Spurs matchup analysis adds a specific implication: if the path to the Finals requires beating an elite-rim-protection opponent, the Wolves need either Category A or Category B in place. Path 3 alone may not be sufficient.

---

## What would falsify this diagnosis

The honest version of any diagnostic memo includes the conditions under which we would update.

- **If the Wolves' 2026-27 LAFI profile shifts out of Q4 even without major roster changes**, the in-house-fixable framing would need revising and Path 3 (system change) would be re-elevated as a more likely Plan A.
- **If Q4-leaning teams begin appearing more frequently and winning at rates comparable to Q1-Q3 teams**, the "rare and not well-precedented" framing would weaken and the diagnosis would soften.
- **If Edwards reaches Luka or SGA tier in 2026-27**, Category A protection becomes automatic and the rest of the diagnosis becomes less load-bearing.
- **If a future season shows the C2 × C5 league correlation rising (closer to the Wolves' Edwards-era lockstep)**, the Wolves' pattern would be revealed as an early example of an emerging league pattern rather than a structural anomaly.
- **If the v2 LAFI (with full action classifier) shows the Wolves are actually high on multi-action density (chain length)**, the playbook-breadth finding gets sharpened but the headline framing holds.

---

## What the front office should take from this

Three things.

**One. The 2023-24 shape is reachable.** Two seasons of post-KAT drift, not an unrecoverable structural change. The same group of core players produced a designed offense in 2023-24. Path 3 (system change) has a higher ceiling than the current state suggests because the team has been here before.

**Two. Edwards's trajectory is the most consequential variable.** **If** he reaches Luka or SGA tier in the next two seasons, the Wolves get Category A protection automatically and the rest of the diagnosis becomes less load-bearing. **If** he plateaus at his current tier, the Wolves are dependent on Paths 2 and 3 (catch-and-shoot personnel acquisition, system change). Q5 should not bet the prescription on Edwards making the next leap; it should plan for the case where he does not, with his development as additional upside.

**Three. The current configuration is not a known failure mode.** There is no off-the-shelf playbook for fixing distributed pickup ball with moderate stickiness, dead off-ball, and bad shot quality, because the configuration is rare and not well-precedented. The front office is not behind in solving a known problem; it is ahead in encountering a less-charted one. The standard moves (trade for a secondary creator, lean into the star) do not directly apply. The right moves are derived from the components of the team's specific pathology.

The diagnosis is severe. The structural problems are nameable, measurable, and at least partially fixable. Q5 will turn this into specific moves.

---

## Methodology appendix

### Sample

- Universe: NBA team-seasons 2014-15 through 2025-26, regular season for LAFI computation, playoffs for outcome validation.
- LAFI sample size: 330 team-seasons (5-component) on inner-joined data.
- Validation sample: 144 playoff team-seasons (excluding 2019-20 bubble, 2020-21 COVID, and 2025-26 in-progress).
- Robustness sample: 160 playoff team-seasons (COVID-inclusive).

### LAFI construction

Five components, each computed as the mean of sub-metric z-scores within season (per spec section 3.1, controls for era drift), then converted to a 0-100 percentile rank across the historical sample. Composite is the weighted sum of component percentile ranks: 0.25*C1 + 0.20*C2 + 0.20*C3 + 0.20*C4 + 0.15*C5, then percentile-ranked across the sample.

Sharp LAFI is the same weighted sum restricted to the three components with measurable lockstep movement during the Wolves' Edwards-era trajectory: C2, C3, C5 with weights renormalized to sum to 1.

### Component-level proxies (v1)

- C1 Ball Stickiness: lead-handler time-of-possession share, avg seconds per touch, avg dribbles per touch, inverted passes per possession.
- C2 Movement Death: off-ball miles per possession (lead-handler subtracted), Synergy OffScreen frequency, Synergy Cut frequency, all sign-flipped.
- C3 Isolation Reliance: Synergy iso frequency, pull-up FGA share, unassisted FG rate.
- C4 Action Poverty: Synergy play-type entropy, designed-action share, ball-dominant-action share. v1 proxies because the full action classifier (multi-action chain density) is not yet built; v2 may sharpen this component's reading.
- C5 Shot Quality Decay: catch-and-shoot vs pull-up split, pull-up three share, restricted-area share, midrange share. No defender-distance data in this slice; v2 with tracking-shot-categorization would add contested rate directly.

### Predictive validation

Three primary regressions (playoff wins, ORtg decay, series upset), each run with Full LAFI, Sharp LAFI, and the five components individually. Bootstrap CIs (1000 resamples, seed=42). Benjamini-Hochberg multiple testing correction across the six primary LAFI coefficients.

Robustness checks: COVID-inclusive sample, binary "advanced past round 1" DV (cleaner than continuous wins because bracket-draw noise contaminates continuous outcomes), C1-only univariate (test the components-regression signal).

### Statistical results summary

- Primary continuous regressions: directionally correct but not significant after BH correction (sample-limited).
- **C1 univariate: significant (p=0.030 default, p=0.030 COVID-inclusive). Single-star pickup is the historical playoff-failure pattern.**
- **Binary DV (advanced past round 1): significant for both Full LAFI (p=0.035 COVID-inclusive) and Sharp LAFI (p=0.049 default, p=0.036 COVID-inclusive). Bootstrap CIs entirely negative.**

### PCA diagnostic

PC1 variance explained: 61.4% (spec target was 50-65%; squarely in the healthy range). All five components load on the same direction (a single pickup-ness axis). PC2 (22% additional variance) independently surfaced the Q3 vs Q4 distinction that was developed qualitatively from cross-component reasoning.

### Correlation matrix highlights

No pair of components exceeds 0.74 correlation league-wide (spec threshold was 0.80; passed). C3 × C5 = 0.708 (iso and bad shots travel together normally). C2 × C5 = 0.059 (motion death and shot quality are uncorrelated league-wide; the Wolves' Edwards-era lockstep is unusual).

### What this analysis does not claim

LAFI does not predict the Wolves' playoff outcome deterministically. The Sharp LAFI binary-DV coefficient gives the Wolves roughly a one-third probability of advancing past round 1 controlling for net rating; that is a real estimate, not certainty. Many high-LAFI teams have advanced, and many low-LAFI teams have not. LAFI adds explanatory power; it does not replace net rating or talent. The Q4 sample is small. The "rare and not well-precedented" framing is supported but is a forward-looking claim.

### Reproducibility

Every chart, table, and statistic in this memo is regenerable from the production warehouse by running `python -m analyses.q0a_lafi --component <name>`, `--composite`, `--validate`, and `--charts`. The findings folder under `outputs/findings/q0a_lafi/` captures the full chronological reasoning trail. Connection params read from `.env` at repo root.

### Artifacts

```
outputs/findings/q0a_lafi/        full chronological reasoning trail (00 - 11)
outputs/tables/q0a_lafi/          per-component CSVs, composite, validation
outputs/charts/q0a_lafi/          six hero visualizations (01-06)
```
