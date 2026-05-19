# The LA Fitness Index: Analytical Specification

**Project:** Timberwolves 2025-26 Postmortem
**Author:** Bobby (with analytical partner)
**Status:** Specification, pre-build
**Coined term:** LA Fitness Index (LAFI)

---

## 1. The thesis

### 1.1 The phenomenon being measured

Pickup basketball at LA Fitness has a distinct, recognizable fingerprint that has nothing to do with talent and everything to do with structure. The fingerprint:

- One player dominates the ball
- The other four stand and watch
- There are no plays, only "actions" that emerge ad hoc
- When the ball-handler gets stuck, he isolates
- Shots happen late in the clock, contested, off the dribble
- There is no flow, no rhythm, no off-ball motion of consequence

This style exists in the NBA on a spectrum. Some teams sit close to the "pickup" end: prime Harden Rockets, Westbrook OKC, early-Luka Mavericks, Trae Young Hawks. Some teams sit close to the "designed" end: 2014 Spurs, late-2010s Warriors, 2024 Celtics, 2024-25 Pacers, 2024-25 Thunder. Most teams sit somewhere in between.

The LA Fitness Index (LAFI) is a single number from 0 to 100 that places every NBA team on this spectrum, where 0 is fully designed and 100 is fully pickup.

### 1.2 Why this matters (the why)

This is the most important part of the spec because if the "why" isn't compelling, the metric is just descriptive trivia. The thesis is **predictive**: where a team sits on this spectrum predicts playoff success in a way that talent and regular season net rating alone do not.

The mechanism is straightforward and rooted in basic basketball epistemology:

**Regular season basketball is a talent game.** 82 games, three nights a week, limited prep time, opponents you'll see twice. Teams with one transcendent ball-handler can win consistently because mismatches always exist somewhere and the best player on the floor can exploit them. Pickup-style offenses can be very effective in this environment because the offense's structural weaknesses are masked by talent and by defensive fatigue.

**Playoff basketball is a system game.** Seven games against the same opponent. Days of film prep. Defenses scout exactly what you do, load up on it, and force you into your second and third options. This is the precise environment that exposes pickup-style offenses. They have no second and third options. They have one option (the star) and four players whose job is to space, watch, and occasionally finish open shots that the star generates.

The hypothesis: when you control for regular season talent (SRS, net rating), the **structure of the offense** explains a meaningful portion of variance in playoff outcomes. Pickup-style offenses underperform their regular season indicators in the playoffs. Designed offenses meet or exceed them.

If this is true, the LAFI is doing something genuinely useful: separating teams that look equally good in March from teams that will behave differently in May.

### 1.3 The Wolves-specific argument

The secondary thesis: the 2025-26 Wolves are far up the pickup end of this spectrum, more so than their regular season record suggests they should be, and this explains the disconnect between their record, their playoff struggles, and the fan eye test (Bobby and Scott both independently describing the offense as boring, sticky, "watching pickup at LA Fitness"). If LAFI predicts what the thesis says it predicts, the Wolves' current trajectory is exactly what the model would forecast.

---

## 2. The metric: structure and components

### 2.1 Overall structure

LAFI is a composite of five components. Each component is computed as a raw value, converted to a 0-100 percentile rank against all team-seasons in the historical sample, and then weighted into the final Index.

```
LAFI = 0.25 * BallStickiness + 0.20 * MovementDeath + 0.20 * IsolationReliance
     + 0.20 * ActionPoverty + 0.15 * ShotQualityDecay
```

Higher is more pickup-like. Lower is more designed.

The weights are first-pass priors. They reflect my judgment that ball stickiness is the most defining feature of pickup ball (hence 0.25), and that shot quality is the most downstream and result-oriented component (hence the lowest weight at 0.15 since it's partly a consequence of the other four). The weights should be validated and potentially re-tuned during the predictive validation phase. See Section 5.4.

### 2.2 Component 1: Ball Stickiness (25%)

**What it measures:** How much one player dominates each possession. The single most defining trait of pickup ball.

**The why:** In a designed offense, the ball moves. In a pickup offense, the ball stops. When the ball stops, the defense doesn't have to rotate, doesn't have to make decisions, and can load up on the one player who has it. Stopping the ball is the easiest way to make an offense easy to guard.

**Sub-metrics:**

1. **Lead-handler time-of-possession share.** Total seconds the team's top time-of-possession player holds the ball, divided by total halfcourt possessions. Higher = stickier.

2. **Long-touch possession rate.** Percentage of halfcourt possessions where any single player holds the ball for more than 4 consecutive seconds at some point during the possession. Higher = stickier.

3. **Dribbles per touch (team average).** Higher = more pickup-like.

4. **Inverse passes per possession.** A team that averages 2.1 passes per possession is stickier than a team averaging 3.5. Computed as (league_max_passes_per_possession - team_passes_per_possession).

**Composite:** Each sub-metric is z-scored within season (to control for era drift in league averages), the four z-scores are averaged, and the resulting composite z-score is converted to a 0-100 percentile rank.

**Why each sub-metric matters individually:**
- Time of possession captures aggregate dominance by the lead handler
- Long-touch rate captures the "stuck" phenomenon, which is more pickup than just having a high-usage star
- Dribbles per touch captures one-on-one play even within possessions that move
- Passes per possession is the cleanest single proxy for ball movement

The four sub-metrics correlate with each other but capture distinct enough variance to be worth including. Confirm with correlation matrix during build.

### 2.3 Component 2: Movement Death (20%)

**What it measures:** Whether the four players without the ball are actively contributing to the offense or standing and watching.

**The why:** Pickup offenses have an obvious tell that's separate from ball stickiness. Even if the ball is moving a bit, if the four off-ball players are flat-footed, the defense doesn't have to rotate. The single biggest difference between, say, a Steve Kerr offense and a James Harden Rockets offense isn't who has the ball, it's what the other four guys are doing while someone has it.

**Sub-metrics:**

1. **Off-ball player distance traveled per offensive possession.** Tracking data gives total distance. Subtract the lead handler's distance, divide by 4 (the four off-ball players), normalize per possession. Lower = more pickup.

2. **Off-ball screens per 100 possessions.** Pickup ball has no off-ball screens. Designed offenses run flares, pin-downs, staggers, hammers, wide pins. Count of off-ball screen events from PBP (or Synergy if available).

3. **Cuts per 100 possessions.** Tracking data classifies cuts. Designed offenses have lots of cuts. Pickup offenses have very few.

4. **Average inter-player spacing during halfcourt offense.** This is more advanced and requires court-coordinate tracking. The hypothesis: pickup offenses have static spacing (players plant themselves), designed offenses have dynamic spacing (players relocate, fill behind drives, swap positions). Measured as the standard deviation of pairwise distances over the course of a possession. Lower SD = more static = more pickup.

**Composite:** Same procedure as Component 1. Z-score within season, average, convert to percentile.

**Note on sub-metric 4:** This is the most technically demanding and may need to be dropped in v1. If so, the other three sub-metrics carry the component on their own.

### 2.4 Component 3: Isolation Reliance (20%)

**What it measures:** How much the offense leans on one-on-one play, particularly as a fallback when designed actions fail.

**The why:** Isolation isn't inherently bad. Some of the most effective offenses in history have used iso liberally (the 2018 Rockets had a top-3 offense). The question is whether iso is the **first option** (which can be efficient if the personnel is right) or whether it's the **last option** (which is the pickup tell). A possession that starts with a designed action, breaks down, and ends in late-clock iso is structurally different from a possession that starts in iso by design.

**Sub-metrics:**

1. **Overall isolation play-type frequency.** Synergy gives this directly. Without Synergy, approximate from PBP: tag possessions where the ball-handler dribbles 4+ times with no screen set in the possession and the possession ends in their shot, foul drawn, or turnover.

2. **Late-clock isolation rate.** Of all shots taken with under 7 seconds on the shot clock, what percentage are isolation attempts? This is the cleanest measure of "iso as fallback." High = pickup.

3. **Contested pull-up jumper rate.** Possessions ending in a pull-up jumper with a defender within 4 feet. This is the visual signature of pickup ball: someone got stuck, jacked one up.

4. **Self-created shot percentage.** Of all team field goal attempts, what percentage are unassisted? Designed offenses have high assist rates because actions create open shots. Pickup offenses have lower assist rates because shots are self-generated.

**Composite:** Same procedure.

**The key insight:** Sub-metrics 2 and 3 are the most diagnostic. A team can have high overall iso frequency by design (high sub-metric 1) without being a pickup offense, but if your late-clock iso rate is high and your contested pull-up rate is high, you're pickup whether you'd admit it or not.

### 2.5 Component 4: Action Poverty (20%)

**What it measures:** Whether the offense runs a diverse and frequent set of recognizable basketball actions, or whether it runs the same two or three things every time down.

**The why:** Designed offenses have a playbook. Pickup offenses don't. A team that runs 25-30 distinct recognizable actions in a game (horns, Spain PnR, flare, hammer, Chicago, ice screen, ghost, slip, etc.) is structurally different from a team that runs Ant pick-and-roll, Randle post-up, and Ant iso for 75% of possessions. This is the truest structural measure of "designed" vs "pickup" because it gets directly at offensive architecture.

**Sub-metrics:**

1. **Unique action types per game.** Requires action-classification from PBP. Count distinct recognized action types per game.

2. **Multi-action possession rate.** Percentage of halfcourt possessions that flow from one action into another (e.g., horns into a flare, or PnR into an off-ball screen). Designed offenses chain actions. Pickup offenses don't.

3. **Non-ISO action density.** Total identifiable non-isolation actions per 100 possessions. Captures how much actual basketball architecture the offense uses.

4. **Off-ball action share.** Percentage of all actions that involve off-ball screens or off-ball cuts (as opposed to on-ball screens). Off-ball architecture is the most demanding and design-heavy. Pickup offenses run very little of it.

**Composite:** Same procedure.

**Implementation note:** This component requires the action classifier, which is the rate-limiting step of the entire project. v1 of the LAFI may need to use simplified proxies (e.g., on-ball screen count from PBP, off-ball screen count from PBP, isolation count) without full action-type taxonomy. v2 with the full classifier will be richer but is several weeks of additional work.

### 2.6 Component 5: Shot Quality Decay (15%)

**What it measures:** The downstream output of the previous four components. What kind of shots does this offense actually produce?

**The why:** The first four components measure process. This component measures result. The reason it gets only 15% weight is that it's partially a consequence of the other four. If an offense is sticky, has no movement, relies on iso, and runs no actions, it will inevitably produce bad shots. So shot quality is somewhat downstream and including it at full weight would double-count. But it's worth including at moderate weight because it captures a few things the process components don't, particularly:
- Shot selection discipline (some pickup-style offenses still self-correct into okay shots)
- Personnel effects (a great iso scorer can produce decent shot quality even from a pickup process)

**Sub-metrics:**

1. **Average shot clock remaining at shot attempt.** Lower = worse = more pickup-like. Designed offenses get into shots earlier. Pickup offenses run the clock down trying to manufacture something.

2. **Wide-open shot rate.** Percentage of shots taken with the nearest defender 6+ feet away. Higher = more designed. Lower = more pickup. (NBA.com tracking gives this.)

3. **Tightly contested shot rate.** Percentage of shots taken with the nearest defender within 2 feet. Higher = more pickup.

4. **Expected eFG% based on shot location, defender distance, and clock remaining.** This is a model output. Fit an expected-eFG model from tracking data, score every team's shot diet, take the team average. Lower expected eFG% = worse shot quality = more pickup.

5. **Catch-and-shoot vs pull-up three rate ratio.** Designed offenses generate catch-and-shoot threes. Pickup offenses generate pull-up threes. Ratio of (C&S 3PA) / (pull-up 3PA). Higher = more designed.

**Composite:** Same procedure.

---

## 3. The math

### 3.1 Z-scoring within season

Every raw sub-metric is z-scored within its season:

```
z_i,t = (x_i,t - mean(x_t)) / std(x_t)
```

Where `i` is the team and `t` is the season. This controls for league-wide era drift (the league has gotten more iso-heavy and three-point-heavy over the last decade; we want to measure how a team compares to its contemporaries, not to historical averages).

### 3.2 Aggregating sub-metrics into components

For each component, sub-metric z-scores are averaged with equal weight:

```
component_z = mean(z_submetric_1, z_submetric_2, ..., z_submetric_n)
```

Then converted to a 0-100 percentile rank across the full historical sample for interpretability.

We use equal weighting of sub-metrics within a component because we don't have strong theoretical priors about which sub-metric matters more, and adding more weights creates more places for the analyst to put their thumb on the scale. Equal weighting is the more defensible default.

### 3.3 Aggregating components into LAFI

Weighted sum of percentile-ranked components:

```
LAFI = 0.25*BS + 0.20*MD + 0.20*IR + 0.20*AP + 0.15*SQD
```

Result is on a 0-100 scale. Conceptually, a LAFI of 80 means "this team is more pickup-style than 80% of NBA team-seasons in the sample."

### 3.4 Validating the component structure

After building v1, run two diagnostic checks:

**Correlation matrix.** All five components should correlate positively with each other (they should all be measuring "pickup-ness" in different ways), but no two should correlate above ~0.80. If two components correlate at 0.90, they're measuring the same thing and one should be dropped or merged.

**Principal Component Analysis.** Run PCA on the five components. The hypothesis is that the first principal component (PC1) captures the "pickup-vs-designed" axis and explains 50-65% of variance. If PC1 explains 80%+, the components are too redundant. If PC1 explains under 40%, the components aren't measuring a coherent underlying construct and the metric needs rethinking.

Both checks happen after v1 is built. If they fail, we re-spec.

### 3.5 Weight tuning (the harder math)

The 25/20/20/20/15 weights are priors. They can be empirically tuned if we want LAFI to be optimally predictive of playoff outcomes. Two approaches:

**Approach A: Keep priors fixed.** Defensible because it means the weights weren't reverse-engineered to fit the answer we wanted. Stronger external credibility.

**Approach B: Tune via cross-validated regression.** Fit a regression where the dependent variable is playoff overperformance (actual playoff wins minus expected playoff wins given regular season SRS), and the predictors are the five components. The fitted coefficients become the optimal weights. Cross-validate to avoid overfitting (5-fold by season, hold out one season at a time, refit, average coefficients).

My strong recommendation: **build with Approach A first**, document the predictive validation results, then run Approach B as a robustness check. Report both. If Approach B's tuned weights are radically different from the priors, that's interesting information. If they're similar, the priors stand and the analysis has external credibility.

---

## 4. The predictive validation

This is what makes LAFI a real metric instead of an aesthetic descriptor. Three nested questions, in order.

### 4.1 Question A: Does LAFI predict playoff overperformance, controlling for regular season strength?

**Setup:** For every playoff team-season in the historical sample (2014-15 to 2025-26, roughly 160 team-seasons), compute:
- Regular season SRS
- LAFI
- Actual playoff wins
- Expected playoff wins given SRS and bracket position (modeled separately)
- Playoff overperformance = actual wins - expected wins

**Regression:**
```
PlayoffOverperformance ~ SRS + LAFI + (bracket controls) + season fixed effects
```

**Hypothesis:** LAFI has a significant negative coefficient. Higher LAFI = worse playoff overperformance, controlling for regular season strength.

**Interpretation thresholds:**
- LAFI coefficient of -0.05 wins per LAFI point: weakly suggestive
- LAFI coefficient of -0.10 wins per LAFI point: meaningful, publishable
- LAFI coefficient of -0.15+ wins per LAFI point: a genuine finding worth front office attention

A team with LAFI 80 vs a team with LAFI 30 has a 50-point gap. At a coefficient of -0.10, that's 5 fewer playoff wins, holding regular season talent constant. That would be a powerful result.

### 4.2 Question B: Does LAFI predict offensive rating decay from regular season to playoffs?

This is the mechanistic version of Question A and arguably more important because it tells us **why** LAFI matters.

**Setup:** For every team-season that made the playoffs:
- Regular season offensive rating
- Playoff offensive rating
- ORtg decay = playoff ORtg - regular season ORtg (typically negative)
- LAFI

**Regression:**
```
ORtgDecay ~ LAFI + (opponent defensive strength) + season fixed effects
```

**Hypothesis:** LAFI has a significant negative coefficient. Higher LAFI = larger drop in offensive rating from regular season to playoffs.

If this comes back significant, we've identified the mechanism: pickup offenses get scouted and schemed harder in playoff conditions, and the system doesn't have answers when the first option is taken away.

This is the regression I'm most excited about, because if it works, it explains the **why** of LAFI in a way that the headline outcomes regression doesn't. Outcomes are noisy. Mechanism is causal.

### 4.3 Question C: Does LAFI predict upsets?

**Setup:** For every playoff series, compute:
- Higher-seeded team's LAFI minus lower-seeded team's LAFI (LAFI differential)
- Outcome: did the higher seed win the series?

**Logistic regression:**
```
HigherSeedWon ~ LAFI_differential + SRS_differential + home_court_advantage
```

**Hypothesis:** Higher LAFI for the favorite increases upset probability. A favorite with high LAFI is more upset-prone because their offensive style is more brittle under playoff pressure.

This is the most fan-friendly result if it works, because it lets us say "the LA Fitness Index identifies which favorites are most likely to get upset." That's a sticky soundbite.

### 4.4 Statistical care

Three traps to avoid in the validation:

**Multiple testing.** We're running three regressions. With three tests at α=0.05, false positive risk is elevated. Apply a Bonferroni or Benjamini-Hochberg correction, or use α=0.02 per test.

**Sample size.** 160 playoff team-seasons sounds like a lot but it's split across 12 seasons with structural variation between them. Bootstrap your confidence intervals. Report 95% CIs, not just point estimates and p-values.

**Endogeneity.** LAFI and SRS aren't independent. Pickup-style teams may systematically have higher or lower SRS for reasons related to their style. Include SRS as a control but also examine the bivariate relationship to make sure the multivariate coefficient is recovering the right effect. Run a robustness check using net rating instead of SRS.

---

## 5. The Wolves diagnosis

After the Index is built and validated, three analyses on the Wolves specifically.

### 5.1 Year-over-year Wolves LAFI

Compute Wolves LAFI for:
- 2021-22 (pre-Gobert)
- 2022-23 (first Gobert year, with KAT)
- 2023-24 (the WCF breakthrough, KAT and Ant in peak chemistry)
- 2024-25 (first Randle year)
- 2025-26 (current)

**Hypothesis:** LAFI dropped meaningfully in 2023-24 (good year, designed offense around KAT's gravity), then climbed substantially in 2024-25 and 2025-26 after the KAT-Randle swap. The Wolves became more pickup-like specifically because Randle's offensive game is more iso-and-post-oriented than KAT's gravitational catch-and-shoot game, and the system around him collapsed.

Sub-component analysis: which of the five components rose most? My prior is Ball Stickiness and Action Poverty rose most. Movement Death may also have risen.

### 5.2 League rank

Where do the 2025-26 Wolves sit on LAFI among all 30 teams? My prior is top 5, plausibly top 3. If they sit at the 90th+ percentile, that's a powerful single-stat indictment.

Cross-reference against playoff teams specifically. The most useful framing isn't "Wolves are 3rd-highest LAFI in the league," it's "of the 16 playoff teams, the Wolves have the X-highest LAFI." Among playoff teams, where you sit on LAFI is what matters for the championship-ceiling question.

### 5.3 Cohort comparison

Identify the 10-15 most similar team-seasons in the historical sample to the 2025-26 Wolves. Similarity defined as: similar LAFI (within 5 points), similar SRS (within 1.5), similar core star age (within 2 years).

What happened to those teams in the playoffs? This is a probabilistic argument: "Teams that have looked like the 2025-26 Wolves on these dimensions have, on average, [X outcome]."

This feeds directly into the historical cohort analysis (the next major piece of the larger project), but the LAFI-specific version of it lives in this section.

### 5.4 If the hypothesis fails

Be honest about this in the spec. If the Wolves don't rank as high on LAFI as I'm predicting, the headline of the analysis changes. Possible alternative findings:

- Wolves rank middle of the pack on LAFI. Then the playoff problem isn't an LA Fitness problem and we need to look elsewhere (probably to defense or to specific personnel matchups).
- Wolves rank high on LAFI but LAFI itself doesn't predict playoff outcomes in the validation. Then LAFI is descriptively interesting but not a real diagnostic, and we should present it as color rather than as the main argument.
- Wolves rank high on LAFI AND LAFI predicts playoff outcomes. The full thesis holds. This is the strong outcome.

The analysis should be willing to land at any of these conclusions. Pre-committing to the strong outcome is exactly the kind of thumb-on-scale that erodes credibility.

---

## 6. Charts and visualizations

The five hero visualizations.

### 6.1 The Index Map (master chart)

Scatterplot. X-axis: regular season net rating. Y-axis: LAFI. Each point is a team-season. Color encodes playoff outcome (missed playoffs / first round out / second round out / conf finals / finals / champion).

What we should see if the thesis holds: at any given net rating, higher LAFI teams cluster toward worse playoff outcomes. The "upper right" quadrant (good record + high LAFI) should be sparsely populated with deep playoff teams. The "upper left" quadrant (good record + low LAFI) should be where champions live.

Label notable teams: 2014 Spurs (low LAFI, champion), 2017 Warriors, 2018 Rockets (high LAFI, lost WCF), 2017 Thunder, 2024 Pacers, 2025-26 Wolves. The labels carry the story.

### 6.2 The Wolves Trajectory

Line chart, 2021-22 through 2025-26. Wolves LAFI on the y-axis. Optionally overlay the five component lines so readers can see which components drove the change.

If the hypothesis holds, the line dips in 2023-24 (good year) and rises sharply in 2024-25 and 2025-26.

### 6.3 The Predictive Validation Chart

Bar chart. X-axis: LAFI decile (1-10). Y-axis: probability of advancing past round 2.

If LAFI predicts playoff outcomes, this should slope sharply downward. The 10th-decile bar (highest LAFI) should be much shorter than the 1st-decile bar.

Include error bars (bootstrapped 95% CIs).

### 6.4 The League Fingerprint

Horizontal bar chart of all 30 current teams, ranked by LAFI. Wolves bar highlighted. Annotation showing the league median and the threshold for "high LAFI" (top quartile).

This is the chart that goes viral if this gets published. It's the league-wide LA Fitness scoreboard.

### 6.5 The Historical Case Studies

Small multiples (2x2 grid) of four case study teams, each one a season trajectory or shot chart that illustrates what high-LAFI playoff death looks like. Candidates: 2018 Rockets, 2017 Thunder, 2022 Mavs (Luka pre-Kyrie), and the 2025-26 Wolves as the fourth panel.

This is the visceral "see what I mean" supporting evidence.

---

## 7. Sequencing and dependencies

For the build (in order):

1. v1 of the Index using the tracking-data sub-metrics only. No action classifier yet. Skip Component 4 or use simplified proxies. Two weeks of work.
2. Predictive validation on v1. If it works at v1, the project is greenlit. If not, decide whether to invest in the action classifier or pivot.
3. Wolves diagnosis on v1. Year-over-year and league rank.
4. Build the action classifier. Several weeks. The rate-limiting step.
5. v2 of the Index with Component 4 fully implemented.
6. Re-run predictive validation and Wolves diagnosis on v2.
7. Writeup and charts.

Critical principle: **v1 is sufficient to test the hypothesis.** Don't let the action classifier delay validation of the core idea. If v1 shows the relationship is real, v2 sharpens it. If v1 doesn't, v2 probably won't either.

---

## 8. What I'm worried about

Honest pre-mortem. Three risks worth flagging now so we can think about them as we build.

### 8.1 The Index correlates too tightly with usage rate of the star

If LAFI ends up basically being "how much does your best player dominate the ball," it's not a new metric, it's just inverted ball-movement stats. Differentiation comes from Components 3, 4, and 5 capturing things beyond pure handler dominance. Watch this in the correlation diagnostics.

### 8.2 The action classifier is too hard

If building a robust action classifier from PBP turns out to take months rather than weeks, the v2 version of the Index never gets built and Component 4 stays as a proxy forever. Fine for the Wolves analysis but limits the metric's long-term value. Worth having a backup plan: a manual-coded sample of 50-100 games from which to derive league-wide action-frequency estimates if the automated classifier doesn't work.

### 8.3 The predictive relationship is real but small

LAFI might be statistically significant but explain only 3-5% of variance in playoff overperformance. That's still real but it's not as compelling a story. Be prepared for this outcome and present it honestly. "LAFI explains a real but modest portion of playoff variance" is a fine finding. Overselling it as "LAFI predicts playoff outcomes" when it explains 4% of variance is the kind of overreach that gets analysts dismissed by serious decision-makers.

---

## 9. Open questions to revisit

Things I deliberately haven't resolved in this spec because they need real data to inform:

1. Final weights on the five components (priors set, empirical tuning deferred to validation phase)
2. Whether to include Component 4 sub-metric 4 (the spacing standard deviation) in v1 or push to v2
3. Whether to use SRS or net rating as the control variable in the predictive validation
4. Whether to z-score within season or pool across seasons (current spec says within-season; revisit if results look weird)
5. How to handle the 2019-20 and 2020-21 seasons (COVID, bubble, no fans, weird scheduling)

---

## 10. Success criteria

What does "this worked" look like.

**Minimum viable success:** LAFI v1 differentiates the 30 current NBA teams in a way that matches expert eye-test rankings on at least the extremes (the top 3 and bottom 3 teams pass the smell test). Wolves rank in the top 5. The predictive validation regression is at least directionally negative even if not statistically significant.

**Full success:** LAFI's predictive coefficient is statistically significant in at least 2 of the 3 validation questions (4.1, 4.2, 4.3). The Wolves rank in the top 3 league-wide. The metric becomes a coherent, publishable piece of work.

**Stretch success:** LAFI's predictive relationship is strong enough that the Index becomes useful for forecasting (not just describing). A front office could plausibly use it to evaluate whether a team is a championship-ceiling team or a paper tiger. This is the version that gets read by people who decide things.

---

End of specification.
