# Statistical Methods Reference

Detailed methodology notes for the statistical techniques commonly used in serious basketball analytics. Read this when a project requires depth beyond the SKILL.md overview.

## Bootstrap confidence intervals

The default tool for almost any basketball uncertainty quantification. Works without parametric assumptions and handles the small samples typical of playoff and lineup work.

### Basic procedure

For a statistic computed on a sample of size n:

1. Resample n observations from the original sample with replacement
2. Compute the statistic on the resampled data
3. Repeat 1000+ times
4. Take 2.5th and 97.5th percentiles of the bootstrap distribution as the 95% CI

### Applications in basketball

**Team metrics across game samples.** Resample games with replacement, recompute the team-level metric, report CI. Standard for playoff splits, regular season vs playoff comparisons, and any aggregate based on a game-level sample.

**Lineup metrics across possessions.** Resample possessions with replacement. Important for lineup net ratings, two-man combination performance, etc.

**Differences between groups.** When comparing two groups (e.g. Wolves with Gobert on vs off), bootstrap each separately and report the CI on the difference. The difference's CI should usually exclude zero before claiming a real effect.

### Watch-outs

**Bootstrap CIs assume the sample is representative of the population.** If the sample is biased (e.g. only playoff games against good teams), the bootstrap inherits the bias.

**Bootstrap can underestimate uncertainty for very small samples.** With n < 20, consider parametric methods or wider intervals.

**Dependent observations break standard bootstrap.** Possessions within a game are not independent. Block bootstrap (resample game-blocks of possessions rather than individual possessions) is more honest for possession-level analysis.

## Hierarchical models for lineup analysis

Raw lineup net rating is notoriously noisy. Hierarchical models address this by partial pooling: small-sample lineups get pulled toward the team mean, large-sample lineups stand on their own.

### Basic structure

For lineup i with observed net rating $y_i$ and n_i possessions:

$$y_i \sim \text{Normal}(\theta_i, \sigma^2 / n_i)$$
$$\theta_i \sim \text{Normal}(\mu, \tau^2)$$

Where $\theta_i$ is the lineup's "true" net rating, $\mu$ is the team's overall mean, and $\tau^2$ captures lineup-to-lineup variance.

The posterior mean for $\theta_i$ is a weighted average of the observed $y_i$ and the team mean $\mu$, with weight proportional to the lineup's possession count. Small samples get pulled hard toward the mean. Large samples stay close to their observed value.

### When to use

When you have many lineups with varying sample sizes and want defensible per-lineup estimates. The standard alternative (just reporting raw net rating with a minimum-possession threshold) discards small-sample lineups entirely, which is wasteful.

### Implementation

In Python, use `pymc` or `numpyro`. For quick approximations, the empirical Bayes shrinkage formula works:

$$\hat{\theta}_i = w_i y_i + (1 - w_i) \mu$$
$$w_i = \frac{\tau^2}{\tau^2 + \sigma^2 / n_i}$$

Where $\sigma^2$ is the within-lineup variance (estimated from large-sample lineups) and $\tau^2$ is the between-lineup variance (estimated from the spread of large-sample lineup means).

## Regularized adjusted plus-minus (RAPM)

The workhorse for player impact estimation. Regresses point margin on a sparse player-presence matrix.

### Basic structure

For each possession, build a vector indicating which 10 players are on the floor (5 offensive, 5 defensive). The dependent variable is points scored on that possession. Regress with ridge regularization.

Coefficients are estimated player impact, controlling for the players on the floor with and against them.

### Why ridge

Without regularization, RAPM is extremely noisy because of collinearity (players who always play together cannot be separated). Ridge shrinks coefficients toward zero, which is reasonable because most players have small marginal impact.

### Pooled multi-year RAPM

A single season produces noisy estimates. Pooling 2-3 seasons gives much more stable values. Be careful with players who changed roles or teams substantially: the pooled estimate may not reflect their current state.

### Variants

**EPM (Estimated Plus-Minus).** Blends RAPM with box-score priors, producing more stable estimates with better in-sample fit.

**LEBRON.** Similar concept, slightly different priors and weighting.

**RAPTOR.** FiveThirtyEight's variant, retired now but historically useful.

In practice: use multiple impact metrics and look at the consensus. When they disagree on a player, that disagreement is informative.

## K-means and hierarchical clustering for archetypes

Used to identify offensive and defensive archetypes across teams.

### Procedure

1. Define feature set (pace, three-point rate, defensive scheme, etc.)
2. Z-score features within season to control for league drift
3. Run k-means at multiple k values
4. Evaluate cluster quality via silhouette score, inertia elbow, and interpretability
5. Choose k based on the balance of statistical fit and basketball sense

### Watch-outs

**Feature selection matters.** Different features produce different clusters. Document your feature choices and justify them.

**K-means assumes roughly spherical clusters.** If clusters are elongated or non-convex, consider Gaussian mixture models or DBSCAN.

**Hard assignment loses information for borderline teams.** Soft clustering (probability of membership in each cluster) is more honest for teams near cluster boundaries.

**Era effects matter.** Z-score within season. A "high three-point rate" team in 2015 is different from one in 2024.

## Logistic regression for binary outcomes

Standard tool for predicting binary playoff outcomes (advanced past a round vs not, upset vs no upset).

### Specification

$$\text{logit}(P(\text{outcome})) = \beta_0 + \sum_i \beta_i X_i$$

Where $X_i$ are predictors and $\beta_i$ are coefficients to estimate.

### Watch-outs

**Sample size for binary outcomes is harsh.** A "playoff team that won a championship" is a rare event. Estimates are noisy. Wide CIs.

**Bracket effects.** Playoff outcomes depend on bracket position, not just team quality. Always control for opponent strength.

**Selection bias.** Teams that made the playoffs are not random; they are the top half of the league. Watch for restriction-of-range issues.

## Expected eFG models for shot quality

Built to decompose offensive performance into shot generation vs shot making.

### Features

- Shot location (zone on the court, or distance and angle)
- Defender distance to shooter
- Shot clock remaining at attempt
- Dribbles before the shot
- Catch-and-shoot vs pull-up
- Open vs contested status

### Model choice

Gradient boosted trees (XGBoost, LightGBM) typically outperform linear models for this task because of non-linear interactions between location, defender distance, and shot clock. Use cross-validation to tune.

### Application

For each shot in your target sample, predict expected eFG%. Compare to actual eFG%. The difference is "shot making" effect. The expected eFG% itself is "shot quality."

A team that generates 51% expected eFG% but produces 47% actual eFG% has a shot making problem, not a shot quality problem.

## Time series for trajectory analysis

For age curves and individual player trajectories.

### Age curves

Pull historical comp populations (e.g. "all defensive-anchor centers who played 5+ seasons since 2000"). Compute mean and standard deviation of impact metric at each age. Smooth with LOESS or splines.

Output: expected production by age for the archetype.

### Individual trajectory

Plot player's actual values against the archetype curve. Categorize as ahead/on/behind the curve.

For projection, blend the player's recent trajectory with the archetype expectation, with weight toward the archetype as projection horizon grows.

### Watch-outs

**Survivorship bias.** Players who play 5+ seasons are not random. They are the players who stuck. The curve overstates expected production at advanced ages compared to a typical drafted player.

**Archetype boundaries are fuzzy.** A player's archetype may shift as they age (a wing becomes a more limited spot-up shooter). Be flexible about archetype assignment.

## Counterfactual modeling

For "what if" analyses (Q6 KAT counterfactual is the canonical example).

### Translation models

For projecting a player's stats in a different context:

$$\text{projected} = w \cdot \text{observed}_{\text{current}} + (1 - w) \cdot \text{baseline}_{\text{target context}}$$

Where $w$ captures how much weight to put on the current observed stats vs the target-context baseline. Set by analytical judgment.

### Lineup substitution

To project team-level performance with a different player:

1. Compute counterfactual lineup composition (player X swapped for player Y)
2. Use RAPM-style framework to estimate counterfactual lineup net rating
3. Aggregate to team level using realistic minute distribution

### Watch-outs

**Counterfactuals are model outputs, not measurements.** Always report ranges. Run sensitivity analyses on key assumptions.

**Interaction effects are hard.** A player's impact depends on teammates. Translation models that assume player effects are additive miss this.

## A word on causality

Most basketball "findings" are correlational. Even careful lineup analysis tells you association, not causation. Be honest about this.

**Things that look causal but are not:**
- Player on/off (confounded by teammates)
- "Teams that did X went on to win" (selection effects)
- "Players who were drafted high outperform" (they got more opportunities)

**Things that approach causal:**
- Within-game variation when a player enters or exits (cleaner than season-level on/off)
- Random injury timing as a natural experiment
- Randomized rotations (rare in NBA but possible in summer league or G League)

For most front office work, "associated with" is honest and sufficient. "Caused" requires stronger evidence than basketball data typically supports.

## Multiple testing

When running many tests, false positives accumulate. With α=0.05 and 20 tests, you expect 1 false positive by chance.

Apply correction:
- Bonferroni: divide α by number of tests
- Benjamini-Hochberg: control false discovery rate

When in doubt, be conservative. A finding that survives multiple-testing correction is much more credible than one that does not.
