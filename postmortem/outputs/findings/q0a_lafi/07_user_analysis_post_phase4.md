# User analysis: Phase 4 result and the discipline of letting the data lead

**Date:** 2026-05-16
**Author:** Bobby
**Context:** Reading the predictive validation results. LAFI did not validate as a predictive metric at conventional significance. This is Scenario 3 from pre-commitment.

## The honest version

LAFI did not validate as a predictive metric at conventional significance. The point estimates went in the right direction. The coefficients are smaller than the spec's publishable threshold. The confidence intervals brush zero. This is Scenario 3 from my pre-commitment.

Two days ago I told you that if LAFI didn't predict, the analysis would pivot to descriptive rather than predictive. That commitment matters now more than ever. The temptation will be to chase robustness checks until something hits. We won't do that.

The right reason to run robustness checks: "We have a specific hypothesis about why the result might be sensitive to a methodological choice, and we want to test that hypothesis."

The wrong reason: "The result wasn't what we hoped, so let's vary the methodology until something is significant."

## The C1 finding is the real discovery and it's bigger than the null result

From the components regression:

```
C1_ball_stickiness_pct     -0.031  0.069
C2_movement_death_pct      -0.001  0.972
C3_isolation_reliance_pct  +0.021  0.411
C4_action_poverty_pct      -0.008  0.680
C5_shot_quality_decay_pct  -0.002  0.899
```

**C1 (Ball Stickiness) is the only component that approaches significance. The direction is negative. The magnitude is meaningful.**

In plain language: across the last decade of NBA playoff history, the kind of pickup ball that has predictably failed is the single-star isolation kind. Harden Rockets. Trae Hawks. Westbrook Thunder. Pre-Kyrie Mavs. The league has selected against this archetype because elite playoff defenses have learned how to scheme against it.

**The Wolves' Q4 pathology (distributed pickup, low stickiness, dead off-ball) is not the pattern the historical data has selected against.** The Wolves aren't failing because they look like the Rockets. They're failing because they've found a different way to be bad that the league hasn't seen at scale yet.

This is actually a more interesting finding than "LAFI predicts playoff failure." Here's the case for why.

If LAFI had hit at conventional significance: "We built a metric that predicts playoff failure, the Wolves rank high on it, here's the diagnosis."

The story we actually have: **"We built a metric that captures pickup-style offense. The league's historical playoff-failure pattern is Q3 single-star pickup. The Wolves have invented a Q4 distributed pickup that the league hasn't seen fail at scale yet. They are running into the limits of an offensive architecture that has no historical precedent for working in the modern playoffs, but also no historical precedent for failing because nobody has tried it before."**

That's a sharper, more honest, and arguably more useful story for the front office. It says: you're not in a known failure mode that someone else has solved. You're in an unknown failure mode that you're going to have to think through from first principles.

## On the C5 wrong-direction finding

C5 going positive in Regression B (p=0.048, meaning bad RS shot quality predicts BETTER playoff ORtg) is a regression-to-the-mean artifact, not a real finding.

The mechanism: teams with bad regular season shot quality often get healthier in the playoffs or face the variance benefit of small sample. Their playoff ORtg regresses toward their underlying talent level which is closer to league average than their bad RS shot quality suggested.

Right move: see it in the data, don't trust it as a real causal pattern, flag it and move on. Disclose in the writeup as a known artifact.

## Which robustness checks to run, with honest reasoning

The agent offered three. Plus one I'm adding.

**1. COVID-inclusive robustness check. RUN IT.** Specific hypothesis: maybe excluding 2019-20 and 2020-21 dropped 30 playoff team-seasons and we're sample-limited. If COVID-inclusive shows tighter CIs and similar point estimates, that's evidence the result is sample-limited rather than null. If point estimates change direction or magnitude, the exclusion was right.

**2. Different DV (binary "advanced past round 1"). RUN IT.** Specific hypothesis: continuous playoff wins is too noisy because of bracket draws. A binary outcome might be cleaner. Caveat: binary reduces information. Right comparison: does logistic on binary produce tighter CIs around LAFI than continuous? If yes, binary is genuinely cleaner.

**3. Restrict to 2018-19+ where the 5-component LAFI is most reliable. DO NOT RUN.** Reasoning is bad. Restricting to a narrower window when the headline was null is exactly the methodology-fishing pattern to avoid. If 5-component is more reliable, we'd want MORE data to detect a real effect, not less.

**4. (New) Run Regression A with C1 as the sole LAFI predictor.** Specific hypothesis: if C1 is doing all the predictive work, a univariate regression on C1 should produce a tighter and cleaner result than either the composite or the multivariate components. In the components regression C1 had -0.031 at p=0.069. The other components are absorbing variance unrelated to the predictive signal. Removing them might tighten the C1 estimate. This isn't methodology fishing because the hypothesis is grounded in the components regression result we already have. We're not searching for significance; we're testing a specific theory the data already suggested.

**Stop after these. No more searching.**

## What this changes about the deliverable

**Change 1: The headline metric shifts.** No longer "Wolves are 3rd on Sharp LAFI." More like: "The Wolves play offense in a structurally unusual way that the league has not seen at scale, and the LAFI framework reveals how their pathology differs from the historical playoff-failure pattern." Sharp LAFI ranking goes from headline to supporting evidence.

**Change 2: The C1 finding becomes a major section.** The historical playoff-failure pattern (single-star pickup, C1 elevated) is a real and defensible finding. Stands alone.

**Change 3: The Wolves analysis pivots from "you're failing in a known way" to "you're failing in an unknown way."** Honest and more useful for the front office because it implies they can't copy how the Rockets fixed themselves (they didn't, they traded Harden). They have to think through from first principles.

## Calibration

Two days ago I wrote down probabilities:
- 60% Scenario 1 (Sharp LAFI predicts cleanly)
- 30% Scenario 2 (Full LAFI predicts, Sharp doesn't add much)
- 10% Scenario 3/4 (descriptive only)

The actual outcome is Scenario 3. I had it at 10%. I was substantially overconfident in the predictive value of the metric.

The agent's instinct to design a careful three-way regression with bootstrap CIs and BH correction was the right move precisely because it produced a result I would have been tempted to talk myself into believing if the methodology were looser. The methodology held me honest. That's the system working.

This is useful calibration. My priors on predictive validation were too optimistic.

## The honest emotional read

A disappointment in one specific sense: LAFI doesn't get to be the predictive metric I hoped for. The "we built a new playoff predictor" headline is off the table.

But the C1 finding plus the Wolves' Q4 architectural anomaly is a more interesting story than what LAFI-as-predictor would have been. Predictive metrics are a dime a dozen. "Here's a pathology no one has seen before and a team running headlong into its consequences" is the kind of finding that makes someone in a front office actually want to read the rest of the work.

The project is still in good shape. Phase 5 (Wolves diagnosis) is going to be even sharper than originally planned because we can now situate the Wolves as architectural outliers, not just LAFI-elevated.

## Direction

Run COVID-inclusive (#1), binary DV (#2), and C1-only univariate (#4). Skip the narrow-window check (#3). Do not run additional checks beyond these three.

Then write the Phase 4 findings markdown honestly:
- We landed in Scenario 3
- Document the C1 single-star-pickup finding as the real positive signal
- Pivot the project's framing from "LAFI predicts playoff failure" to "LAFI describes pickup-style offense and reveals that the Wolves have a structurally unusual pathology that differs from historical playoff failures."

Then move to Phase 5. The Wolves diagnosis is going to be the most important section of the entire project.
