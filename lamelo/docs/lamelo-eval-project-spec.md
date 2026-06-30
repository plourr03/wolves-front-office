# Project spec: clean-room evaluation of the LaMelo Ball trade

Status: draft for the build agent. Operates under the `analytical-rigor` skill.
That skill is the law. Where this spec and the skill seem to differ, the skill
wins, and the discrepancy gets logged.

---

## 0. Why this project exists, stated honestly

The trade already happened. It cannot be undone. So this project does NOT serve a
go or no-go decision. It serves two real things, and the whole design follows
from them:

1. The credibility of Wolves to a T. A published evaluation that survives a
   sharp reader's scrutiny builds the brand. A confident, fragile number burns
   it. We would rather publish a smaller, true claim than a big, breakable one.
2. The decision system being built toward a front-office career. The asset is a
   calibrated, falsifiable, reusable engine and a track record, not any single
   verdict.

Given that, the headline deliverable is NOT a precise change in title odds. It is
an honest decomposition of what moved, a clear account of what is and is not
knowable, and a set of pre-registered forward predictions reality will grade. The
title number, if it appears at all, appears last, with its full error band, after
we have proven we are allowed to show it.

## 1. Clean-room principle

This is a new project with no inheritance from the prior Joan Bet codebase or its
stored outputs. Priors leak through shared code, shared constants, and remembered
results, and the point of this build is to be uncontaminated.

- No numeric result from the old project is imported as an input or an anchor.
- A component from the old project (a sim routine, an impact mapping) may be
  reused ONLY after it is re-validated from scratch inside this project under the
  skill's calibration requirement, and only the method is reused, not its fitted
  outputs.
- The old project's conclusions (the 2.5 to 3.2 percent band, Package A at 2.92)
  are treated as external claims to be independently reproduced or rejected, not
  as ground truth.

## 2. Two questions, never merged

These are different estimands with different baselines. They get separate
pipelines and separate outputs. Conflating them in one number is forbidden.

- Q1, the decision grade: was acquiring Ball and Green for Reid plus that pick
  package the best available use of those assets, judged against the realistic
  alternatives that existed at decision time. Baselines are counterfactual
  rosters (hold and run it back, and the model's own best alternative such as a
  Jrue-type fit deal). This question is about opportunity cost.
- Q2, the state estimate: given the roster we now actually have, how good are we,
  and what are next-year title odds. The only baseline is the rest of the current
  league. This question does not care about the alternatives in Q1.

## 3. Estimands and the identifiability pre-check

Before building, write each estimand in units, then estimate the noise floor and
decide what is distinguishable. Expect, and design for, the possibility that the
precise title-odds delta is below the floor.

- Primary reportable quantities (expected to be identifiable): the value
  decomposition (where impact moved across creation, spacing, defense, depth,
  variance), tier and seed shifts, P(reach conference finals), P(reach Finals),
  the seeding distribution, and which specific current contenders we pass or fall
  behind.
- Secondary quantity (treat as possibly NOT identifiable): the point change in
  P(title). Gate it behind the noise-floor test. If the plausible delta is inside
  the combined Monte Carlo plus parametric plus structural band, the headline
  becomes "indistinguishable at this resolution," and the ordinal and structural
  findings carry the piece.

## 4. Architecture: layers and their calibration duty

Build as explicit layers so credibility can be inherited and audited. Each layer
states its calibration status before the layer above it is trusted.

1. Data layer. Player game and lineup data, contracts and cap state, the current
   league rosters post-offseason. Every imported estimate carries its origin
   context for the transport step.
2. Player-impact layer. Per-player impact as a distribution, not a point.
   Calibrate the impact metric's predictive validity out of sample (does last
   season's impact predict next season's contribution). This is where the LaMelo
   transport adjustment lives (see section 6).
3. Lineup and interaction layer. The non-additive terms: Ant-LaMelo usage
   collision, Ant off-ball efficiency shift, spacing change from Reid out, defense
   net with Reid out and Ball in and Green in, and the Gobert-dependency
   conditional. These are the noisiest terms and the verdict pivots on them, so
   they are modeled as scenarios, not point estimates.
4. Team-strength layer. Aggregate to a team rating distribution. Calibrate the
   impact-to-rating-to-wins mapping against historical win totals out of sample.
5. Season and playoff sim layer. Simulate the full league season and the bracket
   with home court and series format. Calibrate series outcomes against
   historical analogs (do modeled series win probabilities match observed
   frequencies for comparable rating gaps).
6. Objective layer. Convert simulated outcomes into the objective of section 7.

Every layer above the lowest validated layer carries an inherited-uncertainty
flag into the budget.

## 5. Baselines, recomputed jointly

All baseline arms are recomputed inside this project, against the same current
league, the same model version, in the same run. No baseline is carried over from
prior work or from a stale field. The offseason moved the league violently, so a
baseline computed against last month's field is invalid.

- Q1 arms: actual LaMelo roster, hold-and-run-it-back roster, and at least one
  best-alternative roster representing the strongest realistic different use of
  the assets.
- Q2 arms: actual LaMelo roster versus the live field of current contenders.

## 6. Transport adjustment for imported impact (LaMelo especially)

LaMelo's raw impact comes from non-competitive Charlotte teams, low-leverage
minutes, a high personal usage, and defenses that did not gameplan him as a
playoff threat. Porting that raw into a contender role next to Edwards is
covariate shift and must be adjusted explicitly along: role and usage change,
leverage change, teammate-quality change, opponent-quality and playoff-defense
change, and availability. Each adjustment carries its own uncertainty, and the
adjusted estimate's band is wider than the raw. Do the same, in the other
direction, for Reid's departing impact and for Green.

## 7. The objective function, written out

State it as an equation with every term named. It is not single-season
risk-neutral title maximization, because this trade spent the future and carries
asymmetric downside.

- Maximize the discounted integral of title equity over the contention window,
- net of the option value surrendered (the picks sent out and lost flexibility),
- minus a penalty on the catastrophic-regret tail (Ball busts or breaks down and
  the team is capped out and pick-poor with no pivot),
- with the window modeled as a non-stationary process: aging-curve drift on
  Edwards, Gobert, and Ball, and year-to-year correlation, not independent
  seasons.

The risk attitude this encodes is stated in plain language alongside the
equation, so a reader can argue with the values rather than be misled by hidden
ones.

## 8. Uncertainty budget

Propagate and report every source: Monte Carlo sampling, parametric input
uncertainty, structural model-form uncertainty, field uncertainty, and the
irreducible single-season aleatoric noise. Separate reducible from irreducible.
The deliverable includes the budget itself, and an explicit statement of whether
more compute or data would narrow the answer. If structural and field uncertainty
dominate, that finding is published, not hidden.

## 9. Reference-class anchor

Pre-register the reference class before modeling: historically, how often did a
non-contender-tier team that added a second star onto a young core actually reach
or win a Finals inside a comparable window. Pull the base rate. Shrink the
bottom-up sim toward it with precision weighting. A bottom-up result far above the
reference class is a flag to investigate, not a result to ship.

## 10. Dependence structure

Sample inputs with a calibrated correlation structure, not independently. Use a
shared-factor approach where latent factors (team health, fit-clicks, Gobert
availability) drive multiple inputs at once, so the good tail requires several
things to break right together and the bad tail clusters. Report how much the
tails move between independent and correlated sampling. Because the objective
lives in the tail, this is load-bearing, not cosmetic.

## 11. Bias controls and pre-registration

The analyst is a fan of this team. That is the highest-risk prior contamination
there is, so these are mandatory.

- Pre-register inputs, comp criteria, the objective, and forward predictions
  using the skill's template before running anything.
- Grade the trade from Charlotte's side and from a neutral, name-blinded stance.
  If our model says we crushed it but the neutral version says coin flip, the
  priors are leaking and we stop.
- Identify the load-bearing terms (expected: LaMelo availability, the
  usage-collision penalty, Joan's development, the playoff defense haircut) and
  report results across plausible values of each.
- Commit falsifiable forward predictions (win total, seed, the Ant-LaMelo on or
  off split, Ball games played) to an immutable log with grade dates. This log is
  the long-run credibility asset.

## 12. Deliverables, in order of defensibility

1. The value decomposition: where impact moved and why, with bands.
2. Ordinal and structural findings: tier and seed shifts, contenders passed,
   P(reach CF), P(reach Finals), the weaknesses plugged and the new weaknesses
   created, each tied to a specific term.
3. Scenario table: the title-relevant outputs under fit-clicks, neutral, and
   fit-fails values of the load-bearing terms.
4. The point title-odds delta, ONLY if it clears the noise floor, and only with
   its full band and a statement of what calibrates it. Otherwise, the explicit
   "indistinguishable at this resolution" headline.
5. The pre-registered prediction log.
6. A short "what we cannot resolve" section, written plainly.

## 13. Acceptance gates (must pass before anything is published)

- Estimands written, identifiability verdict recorded.
- Every layer's calibration status recorded; unvalidated layers flagged.
- Uncertainty budget complete; reducible versus irreducible separated.
- All baselines recomputed jointly against the current field.
- Transport adjustments applied to all imported impacts.
- Reference-class shrinkage applied.
- Correlation structure in place; tail sensitivity reported.
- Adversarial and name-blinded passes done.
- Output is decomposition-first; no point probability without a band; the
  "indistinguishable" result is available and used when honest.
- Forward predictions logged.

## 14. Suggested build phases for the agent

1. Data and contracts ingestion, current league rosters, cap and apron state.
2. Impact layer with transport adjustments and out-of-sample validation.
3. Interaction and lineup layer as scenario-parameterized terms.
4. Team-strength and win mapping, calibrated.
5. Season and playoff sim, calibrated against historical series.
6. Objective layer and uncertainty budget.
7. Baselines and reference-class anchor, joint run.
8. Adversarial, sensitivity, and output assembly.
9. Pre-registration finalized and predictions committed.

## 15. Open questions to resolve early

- The exact post-trade cap and apron tier, since it changes the Q2 framing and
  any future-flexibility term.
- The best single "best alternative" roster to stand in for Q1's opportunity-cost
  baseline.
- The cleanest available historical reference class and its sample size.
- Which impact metric has the best out-of-sample calibration in our data, since
  the whole tower inherits from it.

---

## 16. Specification multiverse (researcher degrees of freedom)

Pre-registering inputs stops input-tuning, but the pipeline still has many
defensible analytic choices: impact metric, aging-curve form, shrinkage strength,
dependence calibration, transport-adjustment magnitudes, sim assumptions. Each is
a fork, and walking the fork that flatters the team is how bias re-enters even
with honest inputs.

- Enumerate the reasonable settings for each choice. Run the headline outputs
  across the full grid (a specification-curve or multiverse analysis).
- Report the distribution of results across the multiverse, not a single path.
- If the verdict is stable across defensible choices, that stability is a strong
  result. If it flips, the instability is the honest headline, and no single
  path may be cherry-picked as "the answer."

## 17. Reproducibility and provenance

A result that cannot be reproduced exactly is not publishable.

- Deterministic runs: pinned environment, fixed random seeds, versioned input
  data, and a run manifest mapping every output to the exact inputs, code commit,
  and seed that produced it.
- A field-freeze date for the league state, since the field is still moving. Keep
  the ability to re-run as the field updates, with a changelog of how the answer
  moved and why.

## 18. Leakage and temporal validation

- All out-of-sample validation uses temporal splits: train on the past, test on
  strictly later data, no peeking.
- Audit explicitly for leakage (no future information in any feature),
  survivorship bias in the comp sets, and the handling of missingness.
- State the validation protocol before fitting, not after seeing results.

## 19. Retrodiction sanity backtests (acceptance test)

Before the engine is trusted on this trade, it must retrodict a handful of
historical cases with known outcomes: past star-acquisition trades and past title
races. If it cannot reproduce known results within its stated bands, it is not
trusted here and the architecture is revisited. This is a gate, not a
nice-to-have.

## 20. Kill criteria (when no number is published)

Written in advance so the choice is principled, not convenient. Publish the
qualitative decomposition only, and explicitly decline to publish a probability,
if any of the following hold:

- The impact layer or the playoff sim fails its calibration check.
- The specification multiverse shows the verdict is unstable across defensible
  choices.
- The identifiability pre-check puts the title delta inside the noise floor.

## 21. Public translation layer (required deliverable)

The failure mode for a publication is doing rigorous work and then overselling it
in the caption for engagement. Prevent it by making the honest-to-audience
version a project deliverable.

- A specification for communicating "indistinguishable at this resolution," a
  wide band, or a decomposition, in a way that is still a compelling Wolves to a
  T post and never collapses back into false precision for clicks.
- The rule: the public claim may not be stronger than the gated result. The
  caption inherits the error bars.
