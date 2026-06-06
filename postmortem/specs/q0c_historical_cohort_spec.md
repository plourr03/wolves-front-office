# Q0C: Historical Cohort Analysis Specification

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q0C
**Status:** Specification, revised post-LAFI v1 (2026-05-17)
**Position in stack:** Meta-layer analysis (Question 0)

**Revision note:** The cohort definition has been revised to incorporate LAFI components and quadrant placement as features. The similarity-adjusted cohort now prioritizes architectural similarity to the Wolves (Q4 distributed pickup) over pure record-based similarity. The differentiator analysis explicitly stratifies by C1 status because LAFI's Phase 4 validation showed C1 (single-star pickup) is the historically documented playoff-failure pattern, and the Wolves are not in that pattern. The Wolves-specific anomalous correlation finding (C2 x C5 lockstep while league-wide they are uncorrelated) is added as a candidate differentiator to test. Sensitivity analysis runs at three LAFI weightings.

---

## 1. The thesis

### 1.1 The phenomenon being studied

In every era of NBA history, there have been teams that posted very good regular season records, were widely considered contenders, and then lost in the second round of the playoffs. Some of those teams went on to win championships within a few years. Some made deep playoff runs but never broke through. Some declined into mediocrity. Some traded their stars and rebuilt.

The 2025-26 Wolves are about to become one of those teams (probabilistically; the series is currently 3-2 against). The question is which historical outcome they most resemble.

This is not a literary question. It's a probabilistic one. By identifying historical teams that look like the 2025-26 Wolves across several dimensions, we can build an evidence-based base rate for what happens next.

### 1.2 The why

Front offices systematically overweight their own situation and underweight base rates. They believe "we're different" because they have insider information about their own team that they don't have about historical teams. This is a well-documented bias in decision-making across many fields. The corrective is to anchor decisions to base rates from a relevant reference class.

The historical cohort analysis provides that reference class. It tells the front office: "Teams that look like you have historically gone on to do X, Y, and Z with these probabilities." That's not a prediction. It's a base rate. The front office can then ask: "What about our situation makes us more or less likely than the base rate?" That's a much better question than the one they're currently asking, which is implicitly "what should we do, considering only our specific situation?"

The secondary benefit: the cohort analysis identifies historical comparables in detail, which allows us to study what specific moves the successful comps made vs the failed comps. This generates concrete, evidence-based hypotheses about what kinds of moves are most likely to work for this Wolves roster.

### 1.3 The two big questions

The analysis is structured around two big questions:

**Question A: What is the realistic distribution of outcomes for a team that looks like the 2025-26 Wolves?**

This is the base rate question. The output is a probability distribution: X% chance of winning a title within 3 years, Y% chance of making the finals, Z% chance of declining into the lottery, etc.

**Question B: Among historically similar teams, what differentiated the ones that broke through from the ones that didn't?**

This is the prescriptive question. The output is a list of moves, philosophies, or developments that successful comps had that failed comps did not. This feeds directly into Q5 (prescription).

---

## 2. The cohort definition

This is the most consequential methodological decision in the analysis. Get this wrong and everything downstream is junk.

### 2.1 The base cohort

The base cohort is all team-seasons in the last 30 years (1995-96 through 2024-25, plus 2025-26 itself as the target) that meet these criteria:

- Made the playoffs
- Regular season Simple Rating System (SRS) of +3.0 or higher (this is roughly top-10 in the league in most seasons)
- Eliminated in the conference semifinals (Round 2) in 4-6 games, OR
- Eliminated in the conference finals after being a 2-or-3 seed, OR
- Currently in the position of being a strong regular season team facing second-round elimination

The breadth here is intentional. We want "very good teams that fell short of the conference finals or just barely got there," not just the narrow "round 2 exit" definition. The Wolves' realistic 2025-26 outcome will fall in this band.

Expected sample size: roughly 60-80 team-seasons.

**LAFI annotation (post-replan addition).** Each cohort team-season should also be annotated with its LAFI components and quadrant placement (Q1/Q2/Q3/Q4) for the seasons where LAFI is computable (2014-15 onward, gated by Synergy and tracking availability). For pre-LAFI cohort teams, partial annotations are acceptable (some components may not be computable for older seasons due to tracking-data gaps). The base cohort definition remains record-and-result based; the LAFI annotations are a layered feature that downstream analysis uses for stratification.

When LAFI annotations are unavailable for older cohort teams, the analysis should explicitly flag those teams as "pre-LAFI era" and report results both with and without them included. This matters for the differentiator analysis where C1 stratification is central.

### 2.2 The similarity-adjusted cohort

From the base cohort, identify the most similar teams to the 2025-26 Wolves. Similarity defined across these dimensions:

**Roster age profile:**
- Star age (Anthony Edwards is 24)
- Co-star age range (McDaniels 25, Naz 26, Randle 30, Gobert 33)
- Average age of top-7 rotation, weighted by minutes
- Distance between youngest and oldest core players (a measure of "timeline mismatch")

**Star archetype:**
- Primary creator type (Edwards is a downhill scoring guard with developing playmaking)
- Best historical comparables for the star archetype

**Roster construction:**
- Has a defensive-anchor center (Gobert)
- Has a stretch four or face-up four (Randle)
- Has elite wing defense (McDaniels)
- Has a high-usage scorer plus secondary creators (rare; the Wolves arguably don't have this)
- Three-point rate ranking
- Defensive identity (top-5 defense, mid, or below)

**LAFI architecture (post-replan addition):**
- LAFI Full and Sharp percentile ranks
- LAFI quadrant placement (Q1/Q2/Q3/Q4)
- C1 (Ball Stickiness) percentile specifically (the diagnostic component per validation)
- Anomalous-correlation flag: does the team's C2 x C5 correlation across recent seasons match the Wolves' lockstep pattern, or is it closer to the league-wide near-zero?

For pre-2014-15 cohort teams, the LAFI architecture dimension contributes zero weight (cannot be computed). For 2014-15 onward teams, full LAFI similarity contributes per the weighting below.

**Coaching and continuity:**
- Coach tenure (Finch is in his sixth season)
- Roster continuity year over year

**Cap and asset situation:**
- Cap flexibility (limited)
- Draft pick capital (depleted from the KAT trade)
- Tradeable contracts beyond the star

### 2.3 The similarity metric

For each candidate team-season, compute a similarity score to the 2025-26 Wolves. Two approaches available, run both for robustness.

**Approach A: Weighted Euclidean distance.**

Convert each dimension to a numeric value, z-score across the base cohort, and compute weighted Euclidean distance to the Wolves. Weights set by analytical priors (revised post-LAFI):

- Star age and archetype: 25% (the star is the gravitational center of every NBA team)
- Roster age profile: 15% (reduced from 20% to make room for LAFI architecture)
- Roster construction (offensive style, defensive identity): 20% (reduced from 25%)
- Coaching/continuity: 10%
- Cap/asset situation: 15% (reduced from 20%)
- **LAFI architecture (new): 15%** — includes LAFI quadrant placement, C1 percentile, and anomalous-correlation flag.

**Sensitivity analysis (post-replan).** Run the similarity computation at three LAFI weightings:

- Primary: 15% LAFI (as above)
- High: 25% LAFI (and reduce other weights proportionally)
- Low: 5% LAFI (and increase other weights proportionally)

If the top 15-20 comps are stable across the three weightings, the cohort findings are robust. If the comp set shifts dramatically, that itself is a finding: it tells us how reliant the cohort is on LAFI's architectural framing for similarity matching.

For pre-2014-15 cohort teams (no LAFI), redistribute LAFI weight to roster construction within that subset.

**Approach B: Hierarchical similarity scoring.**

Convert each dimension to a tier (high/medium/low or similar/dissimilar), and require minimum matches in critical dimensions before considering a team similar. For example: any candidate team must have a defensive-identity ranking within 3 places of the Wolves, OR they're excluded regardless of other similarities. This prevents "false positives" where a team is technically close on average but completely different in some structural way.

**Recommendation:** Use Approach A as the primary, Approach B as a sanity-check filter. Take the top 15-20 most similar teams from Approach A, then drop any that fail Approach B's structural filters.

### 2.4 Expected similar comps (priors, revised post-LAFI)

The original prior list is preserved with LAFI quadrant annotations:

- **2014-15 and 2015-16 Memphis Grizzlies.** Grit-and-grind plateau, defensive identity, slow pace. Likely Q1-leaning (low motion death, low iso). **Architecture-similar to Wolves only on the defensive-identity dimension; LAFI quadrant differs.**
- **2017-18 and 2018-19 Utah Jazz.** Gobert-anchored defense, Mitchell as the young star, capped out by lack of secondary creation. **Worth checking LAFI: was the Mitchell-era Jazz C1-extreme (Q3) or distributed?**
- **2019-20 Denver Nuggets (pre-bubble).** The most interesting comp; they were similar to the Wolves and then solved their problem. **Likely Q2 or Q1 even before the breakthrough (Jokic's gravity manufactures shot quality). Studying what changed for Denver is gold, but architectural similarity to the Wolves' Q4 may be weak.**
- **2014-15 Chicago Bulls.** Thibs-era defense, offensive limitations. Probably Q3 (Rose, Butler iso-leaning).
- **2013-14 Indiana Pacers.** Top defense, fell short in the East. Pre-LAFI era; no architecture annotation available.
- **2005-06 Detroit Pistons.** Pre-LAFI era. The pattern of "championship-caliber defense but ceiling-capped offense" is illustrative but architectural framing is unavailable.

**Post-LAFI expectation:** the architecture-similar Wolves comps will be sparse precisely because Q4 (distributed pickup) is rare. The cohort analysis should not be surprised if architecture-similar comps are 2-4 teams rather than 10-15. If the top 15 most-similar comps (by combined Euclidean distance) are nearly all Q1 or Q3, that itself is a finding: the Wolves' pathology is not well-represented in the historical comp set, and the prescription must lean more on Q7 star-level evidence than on team-level cohort evidence.

Some of these comps reached the conference finals. Some didn't. The variety of outcomes is the point: similar profiles produced different endings, and the differences are diagnostic.

---

## 3. Outcome classification

For each cohort team, label what happened in the 3 seasons after the cohort year.

### 3.1 Outcome categories

**Tier 1: Championship Breakthrough**
- Won an NBA championship within 3 seasons of the cohort year

**Tier 2: Near-Miss**
- Reached the conference finals or NBA finals within 3 seasons (without winning a title)

**Tier 3: Sustained Contention**
- Continued making the playoffs and winning at least one playoff series in each of the next 3 seasons, but without making a conference finals

**Tier 4: Plateau**
- Continued making the playoffs but with no progression (typically round 1 or round 2 exits, no deep runs)

**Tier 5: Decline**
- Missed the playoffs in at least 2 of the next 3 seasons, OR
- Traded the star within 2 seasons

**Tier 6: Rebuild**
- Explicitly tore the team down and entered a rebuilding phase

### 3.2 Secondary labels

In addition to the outcome tier, label each cohort team for what happened structurally:

- Did they trade a major rotation player within the next 12 months?
- Did they trade their star within the next 24 months?
- Did they acquire a major player (via trade or free agency) within the next 12 months? If so, what archetype?
- Did they change head coaches?
- Did their best player improve, stagnate, or decline?

**LAFI-relevant secondary labels (post-replan addition):**

- Was the team C1-extreme (Q3 single-star pickup, C1 percentile >= 80) at the cohort year? This is the historically documented playoff-failure pattern.
- Did the team shift its LAFI profile away from C1-extreme within 3 years (specifically away from single-star pickup)?
- What quadrant did the team move to over the 3-year window (if any)?
- Did the team's anomalous-correlation pattern (Wolves-like C2 x C5 lockstep) persist, resolve, or appear?

These labels are what powers the prescriptive question (Question B). The LAFI-relevant labels specifically allow stratification of the breakthrough analysis by architectural pattern.

---

## 4. The math

### 4.1 Base rate computation

The simplest output of the analysis:

```
P(Tier 1 | cohort) = count(cohort teams in Tier 1) / count(cohort teams)
P(Tier 2 | cohort) = count(cohort teams in Tier 2) / count(cohort teams)
...
```

These are the base rates for the entire cohort. They answer the question "what happens to teams like this?"

### 4.2 Similarity-weighted base rates

The more sophisticated version. Instead of treating all cohort teams equally, weight them by similarity to the Wolves:

```
P_weighted(Tier i | Wolves) = sum_over_cohort(similarity_j * I[Tier_j = i]) / sum_over_cohort(similarity_j)
```

Where `similarity_j` is the inverse Euclidean distance (or some other similarity score) of cohort team j to the Wolves, and `I[]` is the indicator function.

This produces base rates that lean more heavily on the most similar comps and less heavily on cohort teams that are technically in the bucket but not particularly Wolves-like.

### 4.3 Conditional base rates by structural action

For Question B, compute conditional probabilities:

```
P(Tier 1 | cohort AND made_archetype_X_acquisition)
P(Tier 1 | cohort AND did_not_make_archetype_X_acquisition)
```

If the difference between these is large, that's evidence that making the X acquisition matters.

For example: "Of cohort teams that acquired a secondary playmaker in the offseason, 25% reached the conference finals within 3 years. Of those that didn't, only 10% did."

These conditional rates are descriptive, not causal (the teams that acquired secondary playmakers may have been better positioned in other ways), but they're directionally informative.

### 4.4 Confidence intervals

With cohort sizes of 60-80 teams, base rate estimates have meaningful uncertainty. Bootstrap confidence intervals:

```
For each bootstrap iteration:
  Resample cohort with replacement
  Recompute base rate
Take 2.5th and 97.5th percentiles as 95% CI
```

Always report the CI alongside the point estimate. A base rate of "20% with 95% CI [12%, 31%]" is more honestly informative than "20%."

### 4.5 The single most useful summary statistic

If we had to reduce the entire analysis to one number, it would be:

**Similarity-weighted probability of reaching the conference finals or better within 3 seasons.**

This is the cleanest answer to "what is the realistic ceiling for this team given its profile?"

---

## 5. The prescriptive analysis (Question B)

After the base rates are established, the analysis pivots to differentiation.

### 5.1 The comparison

Split the cohort into two groups:
- Breakthrough group: Tier 1 or Tier 2 outcomes (won a title or reached conference finals)
- Stuck group: Tiers 3 through 6 (everything else)

For each structural label in Section 3.2, compute the rate of that action in the breakthrough group vs the stuck group.

**C1 stratification (post-replan addition).** Run the breakthrough vs stuck split with two additional stratifications:

- Among C1-extreme cohort teams (C1 >= 80 at cohort year), what specifically did the breakthrough comps shift? This is the literature's "single-star pickup failure mode" cohort. Most differentiators should appear here because the league has had time to develop counter-moves.
- Among non-C1-extreme cohort teams (C1 < 80), what did the breakthrough comps do? This is the small but Wolves-directly-relevant subset. If the breakthrough rate in this subset is meaningfully different from the C1-extreme subset, that informs which differentiators are Wolves-applicable vs Q3-applicable.

The expectation is that the C1-extreme subset will have more comps and clearer differentiators, while the non-C1-extreme subset will be sparse. The Wolves' prescription weight on this analysis should reflect the sparsity honestly.

### 5.2 What we're looking for

Differentiators that meet two criteria:
- Meaningful difference between breakthrough and stuck (say, 20+ percentage points)
- Sample size large enough to be plausibly real (at least 5-7 teams in each group)

Candidate differentiators to test (original list, preserved):
- Acquired a secondary ball-handler/playmaker
- Acquired a stretch big or stretch forward
- Acquired a wing shooter with defensive utility
- Replaced the defensive-anchor center
- Star development (BPM improvement of 2.0+)
- Made a meaningful coaching change
- Did NOT trade their star
- Tightened the rotation (reduced rotation player count)

**New candidate differentiators to test (post-LAFI, anchored on the three paths):**

- **Path 1 evidence.** "Star reached top-10 league tier (by EPM/BPM) within the 3-year window." This is the Path 1 equivalent at the cohort level. If breakthrough comps disproportionately had stars who made this leap, Path 1 has empirical historical support.
- **Path 2 evidence.** "Acquired a high-volume catch-and-shoot specialist (38%+ on 5+ catch-and-shoot 3PA per game)." Specifically tests the Category B protection hypothesis from LAFI.
- **Path 3 evidence.** "Restored or significantly altered offensive system through coaching while keeping roster stable." Tests whether system change with stable personnel has historically produced breakthroughs.

**Anomalous-correlation differentiator (post-replan addition, per Issue 2):**

- "Did the cohort team have Wolves-like anomalous component correlations (C2 x C5 lockstep)?" Among the breakthrough comps, how many had the anomalous pattern? Among the stuck comps, same? If anomalous correlation predicts failure independent of component levels, that is a structural finding that propagates back to Q4 and forward to Q5.

This is methodologically delicate because anomalous correlation requires multiple seasons of data per team to compute, and the cohort year itself is a single season. Operationalize as: "Did the team show the anomalous correlation pattern across the 3 seasons centered on the cohort year (cohort year +/- 1)?"

### 5.3 Deep case studies (revised post-LAFI)

In addition to the statistical analysis, do 2-4 deep case studies of the most informative comps. Each case study should explicitly engage with the case team's LAFI architecture (quadrant, C1 status) and what changed.

**The breakthrough story (priority).** One detailed case study of a comp team that broke through. Original candidate 2019-20 Nuggets confirmed. The Nuggets were likely Q1 or Q2 architecturally (Jokic's gravity manufactures shot quality), not Q4 like the Wolves. The case study should be explicit about this: what they did is informative even if their architectural starting point was different. Murray's development, Bruce Brown signing, Caldwell-Pope trade, Aaron Gordon trade — annotate each by which LAFI path they would map to under the Wolves' framework.

**The stuck story.** Original candidate 2017-19 Jazz. Verify LAFI architecture: were they C1-extreme (Q3 single-star pickup with Mitchell) or distributed? If C1-extreme, they are a Q3 stuck case and only partially applicable to the Wolves. If distributed, they are a more directly Wolves-relevant stuck case.

**The decline story.** Original candidate 2014-16 Grizzlies. Pre-LAFI era so architectural framing is unavailable. The Grizzlies' "championship-caliber defense, ceiling-capped offense" pattern is the structural story; LAFI architecture is auxiliary.

**Fourth case (added post-LAFI): the Q4 case study, if it exists.** Search the historical cohort for any team that was Q4-leaning (high motion death, high iso, low stickiness, bad shot quality, normal-breadth playbook). If one exists and broke through, that is the single most directly applicable comp the Wolves have. If one exists and stuck, that is the directly applicable warning. If none exists, that itself is the finding: report that the Wolves' Q4 architecture has no clean historical comp and the deliverable's prescription must lean on first principles per Q5 Section 1.3.

These case studies make the analysis vivid and memorable in a way pure base rates don't.

---

## 6. Wolves-specific application

After the cohort is built and the base rates and differentiators are computed, apply to the Wolves.

### 6.1 The probability report

Output something like:

```
Probability that the 2025-26 Wolves will reach the conference finals within 3 seasons: 22% [13%, 31%]
Probability of winning a championship within 3 seasons: 6% [2%, 12%]
Probability of declining out of the playoffs within 3 seasons: 18% [10%, 28%]
Probability of trading Anthony Edwards within 2 seasons: 4% [1%, 9%]
```

(Numbers are illustrative; the real ones will come from the data.)

### 6.2 The differentiator report

Output a table of differentiators with the following columns:
- Action / structural change
- Rate among breakthrough comps
- Rate among stuck comps
- Difference
- Comp examples (1-2 specific teams that did this)

This is the punchline of the analysis. It says: "Teams that broke through tended to do X and avoid Y. Here's the evidence."

### 6.3 The narrative integration

The cohort analysis output gets integrated into the larger project in two places:
- The opening framing of the entire deliverable (sets the stakes: this is what's at stake based on historical precedent)
- The prescription section (Q5), where the differentiators inform what archetypes of move to prioritize

---

## 7. Charts and visualizations

### 7.1 The Outcome Distribution Chart

A horizontal stacked bar chart. Two bars:
- "Base cohort outcomes" (all cohort teams, equally weighted)
- "Similarity-weighted outcomes" (Wolves-weighted)

Each bar segmented by outcome tier with appropriate colors. Quickly shows the realistic distribution and how it shifts when we focus on Wolves-like teams specifically.

### 7.2 The Comp Cards

A grid layout, each cell a "card" for one of the top 10 most similar comp teams. Each card shows:
- Team and year
- Similarity score
- What they looked like (3-4 key stats)
- What happened (outcome tier)
- 1-sentence narrative

These are the human anchors. Readers will study these cards more than any other visualization.

### 7.3 The Differentiator Chart

A bar chart with one bar per candidate differentiator, showing the gap between breakthrough rate and stuck rate. Sorted by gap size.

The biggest visible gaps are the most actionable insights.

### 7.4 The Path Chart

For each tier (breakthrough, stuck, decline), show a timeline of what typically happened across the 3 seasons following the cohort year. Made it to the conference finals in year +1? Won the title in year +2? Traded the star in year +3?

This is the "what does the next 3 years look like" visualization.

---

## 8. Sequencing and dependencies

The historical cohort is largely independent of the other analyses. It can run in parallel with most of the project. The one dependency: the differentiator analysis (Section 5) becomes more useful if we can pre-define which archetypes are interesting based on the LAFI and Q3 findings.

Sub-sequencing within the cohort analysis itself:

1. Pull team-season data for 1995-96 through 2025-26 (Basketball Reference)
2. Identify the base cohort using the SRS and playoff result filters
3. Pull additional features (roster age, archetype, etc.) for each cohort team
4. Build the similarity metric and compute similarity scores
5. Label outcomes for each cohort team
6. Compute base rates (Section 4)
7. Compute differentiators (Section 5)
8. Build the Wolves-specific application (Section 6)
9. Build charts (Section 7)
10. Write up

Estimated total time: 2-3 weeks of evenings.

---

## 9. What I'm worried about

### 9.1 Era effects

The NBA in 1995 is structurally different from the NBA in 2025. A "good team that lost in round 2" in 1995 looks different from one in 2025. The cohort spans 30 years to get a reasonable sample size, but this introduces era-mismatch risk.

Mitigations:
- Weight more recent comps more heavily in the similarity metric (an explicit era weight)
- Run a robustness check using only the last 15 years (2010-2024) and compare
- Note era when displaying comp cards so readers can apply their own judgment

### 9.2 Survivorship bias in outcomes

Teams that broke through often had things go right that weren't predictable. A draft pick that hit. A free agent who chose them. Injuries that didn't happen. The cohort analysis is going to surface "winning teams did X" patterns where X may just be "got lucky." Be careful about implying causation.

Specific things to watch:
- "Winning teams developed their young player" may just mean they had a young player whose development trajectory hit. Other teams had young players whose trajectories missed.
- "Winning teams acquired a key role player in free agency" may just mean their cap situation allowed it and they got the player they targeted. Other teams had cap situations that didn't or got rejected by their targets.

The analysis should frame differentiators as "associated with" rather than "caused" breakthrough.

### 9.3 Cohort definition sensitivity

Where you draw the cohort boundaries affects everything downstream. If we set the SRS threshold at +2.0 instead of +3.0, the cohort gets bigger and the base rates change. If we restrict to "lost specifically in round 2 in 5-6 games," the cohort gets smaller and more precise.

Mitigation: explicitly run sensitivity analyses. Build the analysis at three cohort definitions and report all three. If results are stable across definitions, the findings are robust. If they swing wildly, that's worth knowing.

### 9.4 Subjective labeling

Some of the structural labels (Section 3.2) involve judgment. "Did they acquire a major player?" requires defining "major." "Did the star develop?" requires defining "develop." These judgments can be made consistent with documented rules, but they introduce subjectivity.

Mitigation: document the rules explicitly. Have a colleague (or me, in this case) sanity-check a sample of labels. Re-label if necessary.

---

## 10. Success criteria

**Minimum viable:** A coherent cohort of 30+ teams with reasonable similarity to the Wolves, base rates computed with bootstrapped CIs, and at least 2-3 plausible differentiators identified. Even if the analysis is messy, the cohort itself is a useful reference.

**Strong:** A clean cohort, base rates that pass the smell test (e.g. a championship probability that's substantially less than 50% but not zero), 4-5 statistically meaningful differentiators, and 2-3 vivid comp case studies. This is the version that meaningfully informs Q5.

**Stretch:** The analysis surfaces a non-obvious differentiator that no one in the Wolves front office is currently thinking about. (E.g. "successful comps tended to deepen their wing depth more aggressively than failed comps," if true.) This is the version that earns the project a second meeting with anyone you send it to.

---

## 11. Open questions to revisit

1. Exact SRS threshold for the base cohort (+2.5? +3.0? +3.5?)
2. Whether to include the 2019-20 and 2020-21 bubble seasons (probably yes with notes)
3. Whether 3-year outcome window is right, or whether 4 or 5 makes more sense for "did they break through"
4. Specific weighting of dimensions in the similarity metric
5. How to handle teams that traded their star vs teams whose star left in free agency (different mechanisms, similar outcomes)

---

End of specification.
