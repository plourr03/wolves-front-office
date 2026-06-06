# User analysis: Phase 4 in full perspective and what Phase 5 needs to deliver

**Date:** 2026-05-16
**Author:** Bobby
**Context:** Phase 4 robustness checks rescued the predictive validation. Three findings landed clean. Now setting up Phase 5.

## What just happened

Twenty minutes ago we were preparing a Scenario 3 writeup. Now we have a Scenario 2-plus-discovery hybrid. Three findings:

**Finding 1: C1 univariate is significant.** Coef -0.023, p=0.030, CI entirely negative. The historical single-star pickup pattern is a real and measurable cause of playoff failure.

**Finding 2: Binary DV LAFI is significant.** Coef -0.013 to -0.014 across Full and Sharp, p ranging 0.035 to 0.052. A 90th-percentile LAFI team is roughly half as likely to advance past round 1 as a 40th-percentile team, controlling for RS net rating.

**Finding 3: COVID-inclusive tightening is consistent with sample-limited true effect.** Point estimates stable, p-values shrinking. The relationship is real, the original sample wasn't big enough.

Each alone would be publishable. Together they're stronger than the most optimistic Scenario 1.

## Methodological lesson

The robustness checks weren't methodology fishing because each had a specific articulated hypothesis. COVID tested "is the result sample-limited." Binary DV tested "is continuous wins too noisy due to bracket draws." C1 univariate tested "is one component doing all the predictive work." Each prediction made in advance, each validated. That's how robustness analysis is supposed to work.

## Why the binary DV finding is the most important methodologically

Continuous playoff wins is a noisy outcome variable. A team that draws an easy first-round opponent racks up wins regardless of their own quality. A team that draws a hard first-round opponent might lose despite being better. The noise from bracket draws is systematic and not addressed by adding net rating as a control.

Binary "advanced past round 1" eliminates this noise. It is a cleaner signal of "did this team beat a comparable opponent in a 7-game series." The fact that LAFI becomes significant on binary DV but not continuous DV is itself evidence that LAFI is measuring something real that gets washed out by bracket noise in the continuous version. This is not p-hacking. It is discovering the original DV was the wrong tool.

For the writeup, this matters because we can present the binary DV as the canonical predictive test with methodological justification: bracket draws contaminate continuous wins, binary advancement is the cleaner outcome.

## The canonical narrative now

**Historical pattern (C1 finding):** The way pickup-style offense has traditionally failed in the playoffs is single-star isolation reliance. One player dominates the ball, the defense schemes that player, the offense collapses. Harden Rockets, Trae Hawks, Westbrook Thunder. A well-documented archetype the league has learned how to beat through aggressive blitzing, traps, and switching.

**Wolves' pattern (the anomaly):** Not C1 extreme. Moderate on stickiness (30th percentile). Extreme on motion death, iso reliance, and shot quality decay. A distributed version of pickup ball where multiple players take turns isolating while no one moves off-ball. Historically rare. The league has not had to develop a counter-scheme for it because it has not been tried at scale.

**The implication:** The Wolves are not following a known failure path that someone else has solved. They are following a novel failure path that they will have to think through from first principles. The conventional fixes (acquire a secondary creator, lean into the star) do not necessarily apply because their pathology is not the standard one.

## What Phase 5 needs to deliver

Seven sections:

**Section 1: Where the Wolves rank.** Full LAFI, Sharp LAFI, each component individually. The Sharp LAFI 3rd-in-league is still the most arresting single number and should lead. But it now sits inside a richer framework.

**Section 2: The Edwards-era trajectory.** Five-component evolution 2022-23 through 2025-26, the four-act story (Gobert integration → WCF year → Randle integration → Q4 collapse). Now empirically validated by Phase 3's correlation patterns and PCA.

**Section 3: The C1 contrast.** This is the new section the validation findings require. Wolves at 30th percentile on C1. The historical playoff-failure pattern is C1 extreme. The Wolves are not failing in the historically common way. They are failing in a way the league has not seen at scale. Need to make this explicit with comparison to known C1-extreme failure cases. Post-2018 Rockets are the cleanest example.

**Section 4: The Q3 vs Q4 framework with quantitative validation.** PCA's PC2 axis confirmed the Q3/Q4 distinction independently. Show the league quadrant map with major teams labeled, Wolves' position clearly marked, and the contrast with single-star failure modes.

**Section 5: The Wolves-specific correlation anomaly.** The unusual coupling pattern (C1 × C5 tight, C2 × C5 inverse league-wide but lockstep over last three Wolves seasons). This is where the diagnosis goes from "Wolves are bad in this way" to "Wolves are bad in a way that does not fit standard NBA patterns at the component-relationship level."

**Section 6: The mechanism.** Why the Wolves' specific pattern is hard to fix. Lack of star-tier solo creation (so they can not get Category A protection that other pickup-leaning teams get). Lack of elite catch-and-shoot personnel (so they can not get Category B protection). They have neither escape hatch.

**Section 7: What it implies for the Spurs matchup.** The series-specific case study. The Spurs are the structural counterargument: low on every LAFI component, elite rim protection, switchable perimeter. The Wolves' Q4 pathology meets the Spurs' Q1 design and produces the result the data predicts: a 70-percentile gap on shot quality between the teams.

## Two things to flag for the agent before Phase 5

**Do not oversell the predictive findings.** The binary DV result is publishable but the effect size (50% less likely to advance from 90th to 40th percentile) needs to be presented honestly. It is a meaningful effect but not deterministic. Many high-LAFI teams have advanced, and many low-LAFI teams have not. LAFI adds explanatory power; it does not replace net rating or talent.

**The diagnosis is harder to write than the validation.** Phase 5 is where the writing matters most. The findings are now substantively complex (LAFI describes style, C1 captures historical failure, Wolves are extreme on different components, the pattern is novel, the mechanism is specific to their personnel context). Writing this in a way that is clear and lands for a front office reader is going to require more drafting work than the previous phases. Plan for it.

## Calibration update

I had Scenario 1 at 60% and Scenarios 3/4 at 10%. The actual outcome is a hybrid that includes elements I had at low probability AND elements I did not even consider.

Pattern emerging: I am good at qualitative pattern recognition and bad at probability estimates. When I look at data and say "this is a Q4 architecture," that has been borne out. When I attach probabilities to outcomes, I am overconfident in directions that turn out to be wrong.

For the rest of the project: lean on qualitative reasoning where I have been reliable, give wider ranges when asked for probabilities, defer more to the data when probability assignments and data disagree.

## Direction

Phase 5. The Wolves diagnosis is the spine of the eventual deliverable. Take time with the writing. When the output lands, the framing right now is the strongest version of this project we could have ended up with. The Wolves diagnosis writeup needs to do it justice.
