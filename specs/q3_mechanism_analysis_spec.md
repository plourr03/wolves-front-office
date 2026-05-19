# Q3: Mechanism Analysis Specification

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q3
**Status:** Specification, revised post-LAFI v1 (2026-05-17)
**Position in stack:** Tactical analysis, narrowed scope. PnR coverage decoder is the central original work.

**Revision note:** Q3 scope has been narrowed following LAFI v1. The original Q3a (shot quality vs shot making) is now an integration with LAFI Component 5 plus player-level decomposition only; LAFI has done the team-season-level work. Q3b (PnR coverage decoder, offense) becomes the main analysis. Q3c (PnR coverage decoder, defense) is preserved as is. The Action Classifier has been extracted to its own standalone infrastructure spec (`specs/action_classifier_infrastructure_spec.md`); Q3 consumes its output when available, with manual-coding fallback for the 2025-26 playoff sample when not.

---

## 1. The thesis

### 1.1 The question

Why, mechanistically, is the Wolves offense breaking down in the playoffs, and what specifically is failing on defense?

Q1 told us what broke. Q2 told us who broke it. Q3 tells us why and how. This is the deepest tactical layer of the analysis and arguably the most original. The pick-and-roll coverage decoder, in particular, is the kind of analysis that, done well, separates serious analysts from fans with opinions.

### 1.2 Why this matters

Front offices and coaching staffs make scheme decisions. The right scheme depends on personnel and on what opponents do. The wrong scheme can render even good players ineffective. The PnR coverage decoder reveals what teams are doing to the Wolves on offense (the patterns of coverage they're seeing) and what the Wolves are doing on defense (the coverages they're choosing and how they're performing).

The single most important offensive question in the modern NBA: how does the league's best defenses guard your star, and how does your team respond? For the Wolves, this is the Anthony Edwards question. He gets blitzed, hedged, trapped, switched. The team's offensive ceiling depends on how it responds in each of those coverages.

The single most important defensive question for any team with a non-switching center: how do opponents attack you when you can't switch, and how badly are you bleeding? For the Wolves with Gobert in drop, this is the central defensive question. We can quantify exactly how much the drop is leaking.

### 1.3 The working hypotheses

To document before running data:

- **Edwards is blitzed and trapped more often in the playoffs than the regular season.** Defenses do this because they know secondary creation is weak.
- **The Wolves offense generates worse outcomes against blitzes than against drops.** Specifically, the pass-out from the blitz doesn't result in good shots.
- **Defensive PPP against the Wolves is highest in pick-and-roll where Gobert is the screener defender.** Gobert in drop allows uncontested threes and floaters. Switching with Gobert is worse, but not by much, because of mismatch attacks.
- **The Wolves halfcourt offense has a "no-answer" problem.** When the first action breaks down, there's no second or third action. Possessions that don't score in the first 6 seconds of the shot clock convert at a much worse rate than league average.

These are testable. Some will be confirmed, some won't. The honest analysis reports both.

---

## 2. The three sub-analyses (post-replan)

Q3 contains three distinct sub-analyses. The scope of Q3a is narrowed following LAFI v1.

**Q3a: Shot quality vs shot making (now an integration + player-level decomposition only)**
LAFI Component 5 has documented team-season-level shot quality decay (Wolves at 83rd percentile vs league average 50). Q3a is no longer a full sub-analysis. It is reduced to: (a) cite LAFI C5 for the team-level finding, and (b) add player-level decomposition (which Wolves players are individually under-converting vs which are being put in bad-shot situations). The player-level piece is genuinely original work; LAFI did not do it.

**Q3b: PnR coverage decoder (offense) — MAIN ANALYSIS**
For every Wolves PnR, classify the defensive coverage and measure the outcome. The central original work of Q3 post-replan.

**Q3c: PnR coverage decoder (defense)**
For every opponent PnR, classify the Wolves coverage and measure the outcome. Unchanged from the original spec.

---

## 3. Q3a: Player-level shot quality decomposition (integration with LAFI C5)

### 3.1 What LAFI C5 already established

LAFI Component 5 (Shot Quality Decay) documented at the team-season level that the Wolves' 2025-26 shot diet is at the 83rd percentile of league pickup-like, vs SAS at the 11th percentile (a 72-percentile-point gap). The four sub-metrics that drove the C5 finding (catch-and-shoot vs pull-up split, pull-up three share, restricted-area share, midrange share) collectively diagnosed the team-level shot quality problem.

Q3a is no longer a from-scratch shot quality build. It is an integration with LAFI C5 plus the player-level work LAFI did not do.

### 3.2 The original Q3a expected eFG% model is deferred

The full expected eFG% model with defender distance, shot clock remaining, dribbles, etc. is a real research project. With LAFI C5 already showing the team-level finding, the question is whether the expected eFG% model adds enough marginal value to justify building it. The post-replan answer: not on the Q3 critical path. Defer the expected eFG% model. Revisit if Q5's portfolio analysis demands player-level expected eFG numbers.

If the expected eFG% model is built later (separately), it would feed Q5 directly. It is not blocking Q3's central PnR coverage work.

### 3.3 The player-level decomposition (the original Q3a piece that remains)

For each rotation Wolves player, compute:

- Their playoff eFG% (actual)
- League-average eFG% on the shot types they took (a simple expected-eFG benchmark using zone averages, no defender-distance model needed)
- Gap = Actual - Expected

A player whose gap is sharply negative is under-converting. A player whose expected eFG% is low but actual is at expected is being put in bad-shot situations.

This is a v1 player-level decomposition. It does not require the full expected eFG% model. It uses zone-level league averages as the benchmark, which is good enough to identify which Wolves players are over- vs under-performing on the shot diet they are getting.

The output is a per-player table:

```
Player        | Actual eFG | Zone-Expected eFG | Gap   | Notes
Edwards       | 0.490      | 0.520             | -0.030| Underconverting
McDaniels     | 0.560      | 0.540             | +0.020| Slightly overconverting
Randle        | 0.470      | 0.510             | -0.040| Underconverting
Naz           | 0.530      | 0.540             | -0.010| Roughly as expected
Conley        | 0.500      | 0.500             |  0.000| At expected
```

(Illustrative numbers.)

This decomposition is the integration point with Q8 (Gobert and Randle analysis). Randle's gap specifically feeds Q8's hypothesis H2a (Randle's possession usage exceeds his marginal value).

### 3.4 The breakdown

Same breakdowns as the original spec, but applied to the player-level decomposition above:

- By shot type (rim, midrange, three)
- By time on shot clock (early, middle, late)
- By assisted vs unassisted

Per-player. The team-level decomposition is in LAFI C5; do not duplicate.

---

## 4. Q3b: PnR coverage decoder (offense)

This is the heart of Q3 and the most original piece of work in the project.

### 4.1 The coverage taxonomy

Defensive coverages against pick-and-roll:

- **Drop:** Big drops below the screen, ball-handler can see the floor but the big protects the rim. Concedes mid-range and three; protects rim.
- **Soft hedge / show:** Big briefly steps up to slow the ball-handler, then recovers. Less aggressive than blitz.
- **Hard hedge:** Big aggressively steps up to wall off the ball-handler.
- **Blitz / trap:** Two defenders on the ball-handler, forcing a pass.
- **Switch:** Big switches onto the ball-handler.
- **Ice / weak (against side PnR):** Forcing the ball-handler away from the screen, toward the sideline or baseline.
- **Top-lock / under (rare):** Defender goes under the screen, daring the ball-handler to shoot.

For each Wolves PnR, classify the defensive coverage.

### 4.2 Classification methodology

This is the hardest piece of work. Two approaches:

**Approach A: Manual coding.** A trained eye watches video and tags each PnR. High accuracy but extremely time-consuming. Doable for a single playoff series but not for league-wide application.

**Approach B: Automated classification from PBP and tracking.** Build heuristics that identify each coverage:
- "Drop" = big stays in the paint area while the ball-handler moves above the break
- "Switch" = the defender on the screener picks up the ball-handler post-screen
- "Blitz" = two defenders are within 6 feet of the ball-handler within 1 second of the screen

The automated approach is messier but scales. For Q3, the recommendation is to do both: build automated classification, then manually audit a sample to validate accuracy.

This is the same action classifier required by LAFI Component 4. Build it once, use it for both.

### 4.3 The output

For each coverage type, compute Wolves performance:

```
Coverage        | Frequency | Wolves PPP | League avg PPP for coverage
Drop            |   45%     |   1.02     |   0.98
Hedge           |   12%     |   0.95     |   1.05
Switch          |   15%     |   0.88     |   1.10
Blitz/Trap      |   18%     |   0.76     |   0.92
Ice             |    8%     |   0.92     |   1.00
Other           |    2%     |   0.84     |   0.95
```

(Illustrative numbers.)

The story is in the comparison. If the Wolves are below league average against blitz specifically, that's a structural weakness defenses can exploit.

### 4.4 The Edwards-specific decoder

The headline analysis is Edwards as ball-handler. Same table but filtered to Edwards-as-ballhandler PnRs only. This isolates how teams are guarding the star and how the offense responds.

### 4.5 The pass-out tracking

When the Wolves get blitzed and Ant kicks out, what happens to the possession? Compute:

- Pass-out destination (typically the screener short-rolling)
- The decision the recipient makes (shoot, drive, pass)
- The outcome of the possession

The Wolves' weakness, in the working hypothesis, is the pass-out from the blitz. Gobert as the short-roll recipient is not a creator. He can't make the next play. So the blitz effectively ends the possession because the second action doesn't materialize.

Quantify this: of pass-outs from blitzes, what's the PPP? Compare to league average. If it's well below, that's the structural offensive problem.

---

## 5. Q3c: PnR coverage decoder (defense)

Same methodology, applied to opponent offense.

### 5.1 The setup

For every opponent PnR in 2025-26 playoffs (and key regular season samples), classify the Wolves' defensive coverage and measure the outcome.

### 5.2 The Gobert-specific table

The headline analysis is Gobert as screener defender. What coverages is he running and how are opponents performing in each?

```
Wolves Coverage with Gobert as screener defender:

Coverage              | Frequency | Opponent PPP | League avg opp PPP
Drop                  |   72%     |   1.08       |    1.02
Hedge                 |   12%     |   1.15       |    1.00
Switch                |    8%     |   1.22       |    1.05
Other                 |    8%     |   1.05       |    0.95
```

(Illustrative numbers.)

The expected finding: Gobert in drop concedes a lot of points. Gobert in switch concedes even more. The Wolves' overall PnR defense is leaky in modern playoff contexts.

### 5.3 The Naz comparison

Same table but with Naz as the screener defender:

```
Wolves Coverage with Naz as screener defender:

Coverage              | Frequency | Opponent PPP | League avg opp PPP
Drop                  |   40%     |   1.10       |    1.02
Switch                |   35%     |   1.08       |    1.05
Hedge                 |   20%     |   1.05       |    1.00
Other                 |    5%     |   1.02       |    0.95
```

The hypothesis: Naz is roughly comparable to Gobert in drop (a little worse because he's not as good a rim protector) but significantly better in switch (because he can actually guard wings on the perimeter). This means the team has more scheme flexibility with Naz.

### 5.4 Series-specific deep dive

For the 2025-26 second-round series specifically, drill into how the Spurs are attacking the Wolves' coverages. Wembanyama as a screener is a particular problem because his shooting and ball-handling break drop coverage. Quantify:

- Spurs PnRs involving Wemby as screener
- Wolves coverage on those
- Outcomes

This series-specific analysis becomes a vivid case study within the broader Q3 framework.

---

## 6. The math

### 6.1 PPP computation

Points per possession on possessions that include a given action. A PnR possession is defined as any possession that includes at least one ball-screen action. PPP = points scored on PnR possessions / count of PnR possessions.

### 6.2 League-wide baselines

To know whether Wolves' PPP in a given coverage is good or bad, we need league baselines. Compute, across all league PnR possessions in 2025-26:
- Average PPP in each coverage type
- Variance and IQR

Wolves' performance is then contextualized as "they're at the Xth percentile of league teams in PPP against blitz."

### 6.3 Sample size

PnR possessions are common (50-60 per game). So sample sizes for the headline metrics are reasonable. But specific coverage types within specific game situations may have small samples. Apply CI methodology consistently.

### 6.4 Comparing to baselines

For each Wolves coverage outcome:
- Wolves PPP
- League average PPP for that coverage
- Difference
- Bootstrap CI on the difference

This is the same pattern as Q1: identify where the Wolves deviate from norm.

---

## 7. Charts and visualizations

### 7.1 The Coverage Performance Chart (offense)

A grouped bar chart. X-axis: each coverage type. Y-axis: PPP. Two bars per coverage: Wolves and league average. Highlights where Wolves over- and underperform.

### 7.2 The Coverage Performance Chart (defense)

Same structure, defensive version.

### 7.3 The Coverage Frequency Pie

Pie or donut chart showing how often opponents use each coverage against the Wolves. Quickly reveals what teams are doing schematically.

### 7.4 The Pass-Out Decision Tree

For blitz-and-trap possessions specifically, a tree showing what happens after the trap. Pass to who, then what. The tree's terminal nodes are scoring outcomes. Visually striking and informative.

### 7.5 The Shot Quality Scatterplot

X-axis: expected eFG% (shot quality). Y-axis: actual eFG% (shot making). Each point is a player or a lineup. The diagonal line is "performing as expected." Below the line is underperformance. Above is overperformance.

---

## 8. Sequencing (post-replan)

1. **Action Classifier (separate spec).** The Action Classifier has been extracted to its own standalone infrastructure spec (`specs/action_classifier_infrastructure_spec.md`). Q3 consumes its output when available.
2. **Manual-coding fallback if needed.** If the Action Classifier slips or is not built in time, Q3 falls back to manual coding for the 2025-26 Wolves playoff sample (estimated ~600 PnR possessions across 11 games; roughly 20-30 hours of careful coding). This preserves the most important Q3 finding (PnR coverage in the Spurs series) even if the full league-wide automation is not ready.
3. Classify all Wolves PnRs in 2025-26 playoffs (and key regular season samples) for Q3b.
4. Classify all opponent PnRs against Wolves in same samples for Q3c.
5. Compute league-wide baselines for each coverage (requires Action Classifier; otherwise use league baselines from prior research as proxy).
6. Compute Wolves outcomes for each coverage (Q3b for offense, Q3c for defense).
7. Build the pass-out tracking (Q3b).
8. Build the player-level shot quality decomposition (Q3a integration; light work).
9. Build charts.
10. Write up.

Estimated time post-replan: 1-2 weeks if the Action Classifier is available, 2-3 weeks if manual coding the playoff sample (most of the marginal time is the manual coding).

The Action Classifier is no longer the rate-limiting step for Q3 specifically (because of the manual fallback), but it is on the critical path for the league-wide generalization of Q3 findings.

---

## 9. What I'm worried about

**The action classifier accuracy on diagnostic coverages.** Now extracted to its own spec. Q3 worries reduce to "did the classifier hit its F1 targets for drop, switch, blitz." If yes, Q3 proceeds with classifier output. If no, Q3 uses manual codes for the Wolves playoff sample and league-wide claims are appropriately caveated.

**Coverage types blur in practice.** Real-world PnR defense doesn't cleanly fall into discrete buckets. A "soft hedge" can look like a "show" can look like a "soft drop." The classifier (or manual coder) will have some ambiguity. Be honest about classifier accuracy when reporting findings.

**The pass-out analysis requires multi-event PBP tracing.** A blitz creates a sequence: trap, pass, drive or shot. Following the sequence requires careful PBP parsing. This is doable but adds complexity.

**Selection effects in coverage choice.** Teams choose coverages based on what they think will work against a specific opponent. So observed coverage frequencies aren't random. The Wolves see a lot of blitzes because teams have learned blitzes work against them. The analysis should not over-interpret "Wolves see more blitzes" as a fact about Wolves; it's a fact about how the league has adapted to them.

**The narrowed scope tempts duplication of LAFI C5.** Resist. Q3a's player-level decomposition is the only original shot-quality work; the team-level analysis lives in LAFI C5. The Q3 deliverable should reference LAFI C5 rather than recomputing.

---

## 10. Success criteria (post-replan)

**Minimum viable:** Coverage classification (Action Classifier or manual fallback) for the 2025-26 Wolves playoff sample, with clean findings on the highest-traffic coverages (drop, switch, blitz). Player-level shot quality decomposition (Q3a integration) for the Wolves rotation.

**Strong:** Detailed analysis of each coverage with statistical confidence. Pass-out decision tree built and informative. Edwards-specific and Gobert-specific tables that the team's coaching staff would find usable. Q3a player-level decomposition surfaces specific players who are under-converting vs being put in bad-shot situations, feeding Q8.

**Stretch:** The Action Classifier is built and meets its accuracy targets per its standalone spec; Q3's coverage tables generalize to league-wide PnR comparisons. The analysis identifies a specific scheme change or personnel change that would meaningfully improve the team's PnR performance, supported by counterfactual quantification.

---

End of specification.
