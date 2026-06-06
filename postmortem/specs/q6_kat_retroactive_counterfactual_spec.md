# Q6: KAT Retroactive and Counterfactual Analysis Specification

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q6
**Status:** Specification, revised post-LAFI v1 (2026-05-17)
**Position in stack:** Special analysis. Now adds a scope-capped LAFI counterfactual ("would the Wolves have stayed Q1 with KAT?") alongside the existing lineup-level RAPM substitution.

**Revision note:** Q6's structural piece has been added: a LAFI counterfactual that asks whether the Wolves would have remained in Q1 (the 2023-24 designed-offense quadrant) had KAT stayed. The scope is capped per Decision 7 of the post-LAFI replan: only Sharp LAFI and four-quadrant placement, only for 2024-25 and 2025-26 seasons. The full component-by-component counterfactual is not built; the structural finding (would they have stayed Q1) is the one that matters for Q5.

---

## 1. The thesis

### 1.1 What happened

In late September 2024, the Minnesota Timberwolves traded Karl-Anthony Towns to the New York Knicks for Julius Randle, Donte DiVincenzo, and a 2025 first-round pick (via Detroit). KAT had been with the franchise for 9 seasons. The trade was made in part for fit reasons (the perceived KAT-Gobert offensive incompatibility) and in part for financial reasons (avoiding the second apron with KAT's extension).

The 2024-25 Wolves with Randle reached the conference finals. The 2025-26 Wolves with Randle are about to lose in the second round. The Knicks with KAT reached the Eastern Conference finals in 2024-25 and lost in the second round of 2025-26.

### 1.2 The question this analysis answers

Was the KAT-for-Randle trade a good decision in retrospect, and what would the Wolves look like right now if the trade had not been made?

This is a hard question to answer well because it requires both retrospective evaluation (what happened) and counterfactual reasoning (what would have happened). Both pieces have their own methodology and pitfalls. Done honestly, this analysis is one of the most valuable parts of the larger project because it evaluates the single largest lever the front office has pulled in the Edwards era.

### 1.3 The why

Three reasons this analysis matters more than the surface "was it a good trade" question suggests.

**It evaluates the front office's decision-making process, not just the outcome.** The Wolves traded KAT for specific reasons (fit, finance, defense). One year and one playoff run later, we can evaluate whether those reasons held up. This is institutional learning that has implications beyond just this one trade.

**It calibrates expectations for the current roster.** If the counterfactual analysis suggests the Wolves-with-KAT would be a meaningfully better team than the Wolves-with-Randle, that's an indictment of the current roster construction. If it suggests the team is roughly the same, the focus needs to shift elsewhere (Gobert, depth, system).

**It establishes a baseline for the prescription analysis.** When Q5 (prescription) starts asking "what acquisitions would move this team forward," the KAT counterfactual provides an upper bound on what kind of improvement is plausible from a single roster move. If "having KAT back" only adds 3 wins, then no single acquisition the Wolves can realistically make is going to fix the team. The diagnosis becomes structural rather than personnel.

### 1.4 The honesty requirement

This analysis is politically sensitive in a way that most of the project isn't. The Wolves front office made this trade. The trade is now public history. Saying "the trade was a mistake" implicitly criticizes the people who made it. Saying "the trade was fine" risks understating real concerns about the current roster.

The right framing is neither indictment nor defense. The right framing is: here's the evidence on both sides, here's the most likely truth, here's what it implies going forward. Reasonable people can disagree on the interpretation. Unreasonable people pre-commit to a conclusion.

---

## 2. The two pieces

The analysis has two distinct components that share methodology but answer different questions.

**Part A: The retroactive evaluation.** Compare what actually happened in the year and a half post-trade. KAT in New York vs Randle in Minnesota. Both teams' performance, fit, and trajectory.

**Part B: The counterfactual projection.** Project what the 2024-25 and 2025-26 Wolves would have looked like with KAT instead of Randle. This requires modeling KAT's likely production in a Wolves uniform and propagating that through lineup-level effects.

Part A is descriptive and relatively straightforward. Part B is modeling-heavy and requires careful methodology.

---

## 3. Part A: The retroactive evaluation

### 3.1 The individual production comparison

For both KAT (in New York) and Randle (in Minnesota), pull production stats across:

**Box score and basic efficiency:**
- Points, rebounds, assists, stocks, turnovers per game and per 36
- TS%, eFG%, usage rate
- Three-point volume and percentage
- Free throw rate

**Advanced metrics:**
- BPM, EPM, RAPM, RAPTOR (or whatever modern impact metrics are available)
- VORP, win shares per 48
- Defensive estimated plus-minus specifically

**Lineup-level impact:**
- On/off team net rating
- On-court team offensive rating
- On-court team defensive rating

**Playoff specific:**
- All of the above in playoff samples (2024-25 and 2025-26)
- Particularly: how did each player's production change from regular season to playoffs?

**Time period:** Compare across both 2024-25 and 2025-26 regular seasons and playoffs.

### 3.2 The team-level comparison

This is more important than the individual comparison.

**Wolves offense 2023-24 (with KAT) vs Wolves offense 2024-25 and 2025-26 (with Randle):**

- Offensive rating (regular season and playoffs)
- Four factors
- Shot distribution (rim, midrange, three)
- Halfcourt vs transition splits
- Play type frequencies (PnR, post-up, isolation, off-ball action)
- LAFI scores year-over-year (this is where Q6 integrates with the LAFI analysis)

**Knicks offense pre-KAT vs post-KAT:**
- Same set of metrics
- Did adding KAT change the Knicks' offensive design? In what ways?
- This is the validation that KAT's offensive impact is real and travels with him, not a Minnesota system artifact.

### 3.3 The full trade ledger

The trade wasn't just KAT for Randle. It was:

**Wolves received:** Julius Randle, Donte DiVincenzo, 2025 first-round pick (via Detroit)
**Wolves sent:** Karl-Anthony Towns, plus salary matching

So the full retrospective evaluation needs to account for:

- Randle's production (covered above)
- DiVincenzo's production. He's now out with a torn Achilles. So the 2025-26 contribution is approximately zero, and the 2026-27 contribution will be limited if he plays at all. This is a significant negative on the trade ledger.
- The 2025 first-round pick. What was selected with it? How is that player performing? What's the expected long-term value?
- The financial implications. How much cap relief did the Wolves get? What did they do or could they have done with that flexibility?

### 3.4 What the retroactive evaluation produces

The output of Part A is a multi-dimensional report card on the trade. Specifically:

**Pure production:** Who has been more productive, KAT or Randle?

**Team-level offensive impact:** Has the Wolves offense gotten better or worse since the trade? Has the Knicks offense gotten better since the trade? This is the cleanest measure of whether the player swap moved the needle for both teams.

**Playoff durability:** Both players are now in their 30s and have varied playoff track records. How have they performed in playoff settings specifically?

**Health:** Both players have injury risk. Who's been on the floor more reliably?

**The ancillary pieces:** Does the value of DiVincenzo (when healthy) plus the draft pick offset any production gap between Randle and KAT?

**The financial dimension:** Were the Wolves' financial goals served by the trade? Did the cap relief enable other moves, or has it sat unused?

The expectation is that this section will produce a nuanced verdict, not a simple thumbs up or thumbs down. The most likely shape: "KAT has produced more individual offense, Randle has been a comparable but different player, the Wolves' offensive system suffered more than expected, but DiVincenzo's loss and other factors complicate the picture."

---

## 4. Part B: The counterfactual projection

This is the harder and more interesting half of the analysis. Done well, it's powerful. Done poorly, it's just speculation dressed up as analytics.

### 4.1 What we're modeling

The counterfactual question: if the trade had not happened, what would the 2024-25 and 2025-26 Wolves have looked like?

This requires:
- Projecting KAT's likely production in a Wolves uniform across these two seasons
- Substituting that production into the Wolves' actual lineup data
- Recomputing team-level metrics (offensive rating, net rating, etc.)
- Projecting downstream effects (playoff outcomes given the new team strength)

### 4.2 The KAT-in-Wolves projection

KAT's production might have differed in Minnesota vs New York for two reasons:

1. **Role/usage differences.** In Minnesota with Ant as the alpha, KAT was the second option. In New York with Brunson, he's also (largely) the second option but in a different system.

2. **Fit/teammates.** KAT's lineup-level impact depends on who he plays with. The Knicks have OG Anunoby, Mikal Bridges, Brunson, Hart. The Wolves have Edwards, McDaniels, Gobert, Conley. Different shooting, different defense, different ball-handling.

**Methodology for the projection:**

**Step 1: Establish KAT's baseline production.** Use his actual 2024-25 and 2025-26 numbers as the starting point.

**Step 2: Adjust for context.** Two adjustments are needed:
- Usage adjustment: would his usage be the same in Minnesota? (Probably similar to his historical Minnesota usage, which is well-documented.)
- Fit adjustment: would his efficiency be different given different teammates? (This is the hard part.)

**Step 3: Use a "translation" model.** For the fit adjustment, the cleanest approach is:
- Look at KAT's full Minnesota tenure (2015-2024) and identify the role he played
- Compare to the Knicks' system and identify how his role has shifted
- Adjust his New York stats back toward his Minnesota production patterns to estimate what he'd have produced in a 2024-25 / 2025-26 Wolves context

This is a soft adjustment, not a precise model. The honest framing: "If KAT had stayed in Minnesota, his production would likely have been in the range of X to Y, with our point estimate at Z."

**Step 4: Account for age.** KAT was 29 entering 2024-25, 30 entering 2025-26. Apply standard aging curves for skilled bigs. Modest decline expected.

**Step 5: LAFI projection (scope-capped, post-replan addition).** Project the Wolves' LAFI profile under the KAT counterfactual for 2024-25 and 2025-26. Scope is intentionally narrow:

- **Headline metrics only:** Sharp LAFI percentile and four-quadrant placement. Not all five components individually, not full LAFI. The headline question is "would the Wolves have stayed in Q1?" and Sharp LAFI plus quadrant answers it.
- **Two seasons only:** 2024-25 and 2025-26. Not the full Edwards era.
- **Baseline anchor:** the 2023-24 KAT-era profile (Full LAFI 35, Sharp LAFI 45, Q1-leaning) is the empirical baseline. The counterfactual projects forward from there with KAT remaining.

Methodology for the LAFI projection:
- Identify how KAT's role characteristics (catch-and-shoot share, off-ball gravity from his three-point threat, pick-and-pop frequency) would have populated the LAFI sub-metrics under the actual 2024-25 and 2025-26 Wolves lineup compositions.
- Substitute the KAT role characteristics into the Wolves' actual lineup data for those two seasons.
- Recompute the C2, C3, and C5 sub-metrics (the three components Sharp LAFI uses) and roll up to Sharp LAFI and quadrant placement.
- C1 and C4 are not projected (out of scope per the scope cap).

The counterfactual answer is a probabilistic statement: "Under the conservative translation weight, the Wolves' counterfactual 2025-26 Sharp LAFI is in the range of X to Y, and their quadrant placement is Q1/Q2/Q3/Q4 with probability P1/P2/P3/P4." The honest framing: "If KAT had stayed, the Wolves would likely have remained Q1-leaning or moved to Q2 (star-fed motion) rather than Q4 (distributed pickup). The Q4 collapse is roughly attributable to the trade plus the system contraction it enabled."

If the counterfactual answer is "they would have stayed Q1," that is the cleanest indictment of the trade's structural impact. If "they would have drifted to Q3 or Q4 anyway because Gobert's decline and the broader system contraction were the dominant drivers," that is the cleanest defense of the trade. Either answer is informative.

### 4.3 The lineup-level substitution

Once we have a projected KAT stat line, the harder work begins. We need to compute counterfactual lineup performance.

**The basic substitution:**

For each Wolves lineup that featured Randle, substitute KAT and project the new lineup's performance. This requires a lineup-level performance model.

**Approach A: Multi-year RAPM-style decomposition.**

Use a multi-year regularized adjusted plus-minus framework to estimate each player's marginal contribution. Plug KAT's contribution into the Wolves' lineup composition and aggregate up to team-level.

This is sophisticated but it's the cleanest approach. It also handles fit issues organically because RAPM captures interaction effects between players.

**Approach B: Component substitution.**

Decompose lineup performance into offensive and defensive components, then substitute KAT's offensive and defensive components for Randle's. Less sophisticated but more interpretable.

The output of this step: a counterfactual Wolves team-level offensive rating, defensive rating, and net rating for 2024-25 and 2025-26.

### 4.4 The further counterfactuals

If KAT had stayed, other things would have been different too. Specifically:

**DiVincenzo wouldn't have been on the team.** The Wolves' actual 2024-25 wing rotation included DiVincenzo as a starter. Without that trade, the Wolves would have had to find another wing. Probably a less skilled option. So the counterfactual isn't just "Wolves with KAT instead of Randle." It's "Wolves with KAT, no DiVincenzo, no draft pick acquired in that trade, and presumably a different wing rotation."

**The cap situation would have been different.** With KAT and his extension on the books, the Wolves would have been deeper into luxury tax territory. They may have made different ancillary moves.

**The 2025 free agency moves would have been different.** Did the Wolves use any of the cap flexibility freed by the trade?

Honest framing: the cleanest counterfactual is "swap Randle for KAT, hold everything else constant." A more complete counterfactual adjusts for the ancillary moves but introduces more speculation. Do both versions and report both.

**The LAFI-trajectory counterfactual question (post-replan addition).** Would the Wolves have remained in Q1 (the 2023-24 designed-offense quadrant) with KAT, or would they have drifted toward Q3 or Q4 anyway because other factors (Gobert's decline, DiVincenzo's loss, general system contraction) were the dominant drivers?

This is the most important question Q6 can answer for Q5's prescription framing. If the LAFI trajectory is mostly KAT-driven, then the Q4 collapse is attributable to the trade and Path 2 (Category B catch-and-shoot acquisition) is the most direct reversal path. If the LAFI trajectory would have happened regardless of KAT, then the current Q4 placement is a more structural problem that personnel changes alone cannot fix, and Path 3 (system change) becomes the higher-leverage path.

Methodology: project the LAFI counterfactual under two ancillary assumptions:
- **Assumption A (KAT stays, everything else as actual).** Wolves' counterfactual LAFI in 2024-25 and 2025-26 under the as-actual non-KAT roster.
- **Assumption B (KAT stays, DiVincenzo never on roster, ancillary moves adjusted).** Wolves' counterfactual LAFI with the full alternative roster (no DiVincenzo, different wing rotation, etc.).

If A and B both project Q1, the LAFI trajectory is robustly KAT-driven. If A projects Q1 but B projects Q3, the trade was specifically what enabled the Q4 collapse via the DiVincenzo and ancillary effects. If both project Q3 or Q4, the trade alone was not the cause; structural factors dominate.

### 4.5 The playoff projection

Once we have a counterfactual regular season net rating, we can project counterfactual playoff outcomes.

**Methodology:**
- Use historical relationships between regular season net rating and playoff performance
- Account for seeding and bracket
- Output a counterfactual probability distribution over playoff outcomes

Example output:
- Counterfactual 2024-25 Wolves: 56% chance to reach conference finals (vs actual 100%, since they did)
- Counterfactual 2025-26 Wolves: 38% chance to reach conference finals (vs actual playoff path so far)

The probabilities should be reported with appropriate uncertainty.

---

## 5. The math

### 5.1 The translation model for KAT

To convert KAT's New York stats to projected Minnesota stats:

```
KAT_MIN_projected = KAT_NY_actual + (KAT_MIN_historical_avg - KAT_NY_actual) * weight
```

Where `weight` is between 0 and 1, capturing how much we believe context matters. A weight of 0.5 says we expect KAT's projected Minnesota stats to land halfway between his actual New York stats and his historical Minnesota averages.

Determining the right weight is a judgment call but it can be informed by:
- How different are the two systems statistically? (More different = higher weight)
- How much of KAT's career has been in Minnesota vs other places? (Mostly Minnesota = higher weight on Minnesota history)

Recommended starting weight: 0.4. KAT's stats in MIN projected = 0.6 * NY stats + 0.4 * (KAT MIN average adjusted to his 2024-26 skill level).

### 5.2 The lineup-level substitution

Using RAPM (or similar):

```
Counterfactual lineup net rating = Sum of player contributions, with KAT swapped for Randle
                                  + Lineup-specific interaction terms (estimated)
```

The interaction terms are the hard part. Use league-wide priors about how player archetypes interact (e.g. two-skilled-big lineups have specific properties).

### 5.3 The playoff projection

A team's playoff overperformance can be modeled as a function of:
- Net rating (the dominant predictor)
- LAFI or similar style metrics
- Seeding
- Injury context

Use a logistic regression trained on historical playoff outcomes to convert counterfactual net rating into a probability of reaching each playoff round.

### 5.4 Uncertainty quantification

This is critical. The counterfactual is full of judgment calls and modeling assumptions. The output should look like:

```
Counterfactual Wolves with KAT, 2025-26:
- Projected net rating: +5.8 [range: +4.2 to +7.4]
- Projected wins: 53 [range: 49 to 57]
- Probability of reaching conference finals: 47% [range: 32% to 62%]
```

The ranges are essential. A single point estimate is overconfident given the methodology.

### 5.5 Sensitivity analysis

Run the counterfactual at three different translation weights (0.2, 0.4, 0.6) and report all three. If results are stable across weights, the counterfactual is robust. If they swing wildly, that's important to disclose.

---

## 6. The harder honesty

Three things this analysis must address honestly even if they're uncomfortable.

### 6.1 The Gobert-KAT fit problem was real

The original concern that drove the trade was that KAT and Gobert didn't fit well together offensively. This concern wasn't fabricated. The data showed it.

The counterfactual analysis has to engage with this honestly. The "Wolves with KAT" projection has to include the Gobert-KAT lineup data, which was structurally challenged. If the counterfactual just projects KAT into a Naz-at-the-five lineup, it's cheating.

**Approach:** Compute counterfactual lineup performance for both possible primary lineups:
- KAT + Gobert frontcourt (which is what the Wolves were running for years)
- KAT + Naz frontcourt (with Gobert moved to the bench or out)

Then ask: which configuration would the team most likely have run? In honest projection, probably KAT + Gobert (consistent with what they actually did), at least to start.

### 6.2 KAT's playoff history is not unblemished

KAT's playoff track record has its own warts. He's been criticized for playoff disappearances in past years. The trade was partly motivated by playoff concerns about his game, not just regular season fit. The counterfactual analysis should incorporate his realistic playoff production (with appropriate variance), not just his regular season averages.

### 6.3 Randle has been pretty good

In Minnesota, Randle has been a real contributor. He scored 17 points and grabbed 10 rebounds in Game 5 of the current series. The Wolves reached the conference finals last year with him on the roster. Saying "the trade was a mistake" requires overcoming the actual evidence that Randle has been a positive contributor. The counterfactual has to show that KAT would have been meaningfully more positive, not just plausibly more positive.

---

## 7. The integration with the larger project

### 7.1 Where Q6 sits in the deliverable

The KAT analysis is most naturally placed:
- Late in the diagnostic section, after the team-level findings have been established
- As its own standalone section, given the political weight of the analysis
- Before the prescription section, because the verdict on the trade affects the prescription's framing

### 7.2 What it feeds

Q6 feeds Q5 two distinct things:

**The upper-bound benchmark.** If "having KAT back" produces +3 wins and a 47% conference finals probability, that is the absolute ceiling for what one big move can do. Q5's prescriptions should be calibrated against this benchmark.

**The structural counterfactual (post-replan addition).** The LAFI counterfactual answers whether the current Q4 placement is fixable by personnel (KAT-equivalent acquisition) or whether it would have emerged regardless of the trade. This determines the relative weight Q5 puts on Path 2 (Category B personnel acquisition) vs Path 3 (system change). If the LAFI counterfactual says the trade caused the Q4 placement, Path 2 becomes more credible. If the trade was incidental, Path 3 carries more weight.

Q6's structural finding also feeds Q8 (Gobert and Randle decisions). If KAT was the primary driver of the 2023-24 Q1 placement, the framing for Randle changes: he is being asked to do a job (manufacture Category B shot quality via off-ball gravity) that he is not built for. Q8 incorporates that finding.

### 7.3 What it consumes

The KAT analysis requires:
- Lineup data from Q2
- LAFI scores from Q0A (to compare Wolves offensive design before and after the trade)
- Team-level offensive analysis from Q1

So Q6 is downstream of those three pieces. Build Q1, Q2, and the LAFI v1 first, then build Q6.

---

## 8. Charts and visualizations

### 8.1 The Production Comparison Chart

A side-by-side comparison of KAT and Randle across the past two seasons. Key metrics in bar chart form, with KAT and Randle bars side by side for each metric. Includes both regular season and playoff splits.

### 8.2 The Team Trajectory Chart

A line chart showing the Wolves' offensive rating year over year, with vertical markers for the KAT trade and major roster moves. Includes the Knicks' offensive rating on the same chart (or a paired chart) for comparison.

### 8.3 The Counterfactual Distribution Chart

A density plot showing the projected distribution of 2025-26 Wolves win totals under three scenarios:
- Actual (no counterfactual)
- KAT counterfactual, conservative translation weight
- KAT counterfactual, aggressive translation weight

This visualizes the uncertainty in the counterfactual estimate.

### 8.3a The Counterfactual LAFI Trajectory (post-replan addition)

A small-multiples chart with two panels:
- 2024-25 actual vs counterfactual: Sharp LAFI value and four-quadrant placement under actual (Randle) vs counterfactual (KAT) personnel.
- 2025-26 actual vs counterfactual: same.

The visual makes the structural KAT counterfactual legible at a glance. If the counterfactual lines stay in Q1 while the actual lines drift to Q4, the trade's structural impact is visually undeniable. If the counterfactual also drifts, the trade was not the structural cause.

### 8.4 The Decision Tree

A visual showing the actual sequence of decisions (KAT trade, downstream effects) vs the counterfactual sequence. Helps readers grasp what's being compared.

### 8.5 The Ledger Summary

A simple table summarizing the full trade ledger:
- KAT vs Randle production differential
- DiVincenzo contribution (and lost contribution due to injury)
- Draft pick value
- Financial implications
- Estimated team-level impact

This is the executive summary table for the section.

---

## 9. Sequencing

1. Pull all relevant data: KAT and Randle stats in both teams, lineup data, advanced metrics
2. Build Part A: retroactive evaluation
3. Build the KAT translation model (the projection of his Wolves production)
4. Build lineup-level substitution
5. Project counterfactual team-level metrics
6. Project counterfactual playoff outcomes
7. Sensitivity analyses
8. Write up findings honestly

Estimated time: 2 weeks, mostly because the modeling work is involved.

---

## 10. What I'm worried about

### 10.1 The counterfactual is inherently speculative

No matter how careful the methodology, the counterfactual is a model output, not a measurement. Smart readers will be skeptical of it. The defensive posture: lean heavily on uncertainty intervals, document assumptions transparently, run sensitivity analyses.

### 10.2 Political reception

If this analysis lands in front of someone who advocated for the trade, they will read it with a critical eye. The work has to be airtight in methodology to survive that scrutiny. This is one of the reasons to be especially careful in this section.

### 10.3 KAT performing well in New York is partly a system artifact

The Knicks built a specific system around KAT (high screen-and-roll with Brunson, KAT at the pick-and-pop spot). If we project KAT to Minnesota's actual system, his production might not translate. The translation model needs to handle this carefully.

### 10.4 The "Randle was good when it mattered" argument

Randle had a strong 2024-25 playoff run. He was a major reason the Wolves reached the conference finals. A counterfactual that says "we'd have been better with KAT" has to overcome the fact that the actual Randle version of the team got further than the Wolves had been in 20 years.

Honest framing: the counterfactual evaluates 2024-25 AND 2025-26 together. The 2024-25 result was good. The 2025-26 result has not been good. A two-year window is the fairest evaluation period.

---

## 11. Success criteria

**Minimum viable:** A clean retroactive comparison (Part A) with honest assessment of both players' production and team impact. Counterfactual (Part B) with appropriate uncertainty, even if conclusions are tentative.

**Strong:** Both parts produce defensible findings with quantified uncertainty. The analysis surfaces specific dimensions on which the trade has helped or hurt that go beyond the obvious surface-level production comparisons.

**Stretch:** The counterfactual produces a result robust enough across sensitivity analyses to provide a confident probabilistic answer to "did the trade help or hurt." This is the version that meaningfully informs front office thinking going forward.

---

## 12. Open questions to revisit

1. The exact translation weight for the KAT projection
2. Whether to include the 2025 draft pick value in the ledger (player is too young to evaluate fully)
3. How to handle DiVincenzo's Achilles injury (treat as bad luck or as part of the trade's downside)
4. Whether to incorporate KAT's pre-2024 Minnesota production or use only recent seasons as the baseline
5. Whether to compute the counterfactual for both 2024-25 and 2025-26 separately or jointly

---

End of specification.
