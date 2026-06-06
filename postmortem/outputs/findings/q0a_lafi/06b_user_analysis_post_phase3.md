# User analysis: Phase 3 produced two findings, not one

**Date:** 2026-05-16
**Author:** Bobby
**Context:** Reading the composite, correlation matrix, PCA, and Wolves-vs-league comparison.

## The Sharp LAFI is the discovery. The C2 × C5 finding is the diagnosis.

Two things came out of Phase 3 that are easy to conflate. Separating them carefully:

**Discovery 1: Sharp LAFI exists as a distinct construct.** The Wolves are 13th-15th on Full LAFI but 3rd on the C2+C3+C5 subset. That gap (89.7 vs 64.5) is the methodological finding. The pickup-ball pathology that predicts playoff failure lives in a specific subset of LAFI, not the whole thing.

**Discovery 2: The Wolves' C2 × C5 pattern is unique and worse than I thought.** League-wide, motion death and shot quality decay are essentially uncorrelated (0.059). For the Wolves over the full Edwards era, they're inversely correlated (-0.22). But for the last three seasons specifically, they've moved in lockstep. This is the diagnostic finding.

These are different things. The first is about the metric. The second is about the team. The second is much more important.

## I was wrong about "three surfaces of the same disease"

Two days ago I told you C2, C3, C5 were "three surfaces of the same disease." The data says that's wrong league-wide.

Across the league, motion death and shot quality decay are uncorrelated. Most teams that have dead off-ball motion still produce normal-quality shots. They have a star who can manufacture shot quality despite the lack of motion. They have shooting personnel that catches-and-shoots well even from stationary positions. They have a system that generates threes through ball-screen action even without off-ball motion.

So the framing "motion death causes bad shots" is not a general NBA pattern. It's a Wolves-specific pattern for the last three seasons.

This matters for two reasons.

1. **The Wolves' pathology is genuinely unusual.** They're combining problems that most teams don't combine. That makes their offense harder to fix than a typical struggling offense because the fixes don't have established precedent.
2. **The mechanism connecting motion death to bad shots needs to be explained, not assumed.** When I said "three surfaces of the same disease" I was treating the causal link as obvious. The data says it's not obvious. So what IS the mechanism for the Wolves specifically? Why does their motion death produce bad shots when most teams' motion death does not?

## Why the Wolves' motion death produces bad shots when other teams' doesn't

Working hypothesis. Most teams with dead off-ball motion fall into one of two categories.

**Category A: Star-anchored isolation.** The team has a transcendent on-ball creator (Luka, SGA, prime Harden) who can manufacture good shots from isolation despite the lack of motion. The star bends the defense one-on-one. The off-ball players don't need to move because the star creates enough advantage by himself.

**Category B: Specialist shooting.** The team has elite catch-and-shoot personnel (Klay-era Warriors, Buddy Hield types, certain Hawks configurations) who produce good shots from stationary positions because they're so good at the shot itself.

The Wolves are in neither category.

Anthony Edwards is a great scorer but not yet at the Luka/SGA tier of solo defense-breaking. He's in the second tier where defenses can scheme him with help. So the Wolves don't get Category A protection from their motion death.

The Wolves' supporting cast isn't elite catch-and-shoot personnel. Jaden McDaniels is a 36% three-point shooter, good not great. Donte DiVincenzo is the elite shooter and he's out for the year. Naz Reid is good but inconsistent. So they don't get Category B protection either.

**The Wolves are uniquely vulnerable because they have neither the star tier nor the shooting tier that protects most motion-dead offenses. Their motion death produces bad shots specifically because they don't have the personnel to compensate for it.**

This is a much more actionable diagnosis than "three surfaces of the same disease." The previous framing pointed at "fix the motion." This framing points at three different fixable paths: improve Ant's solo creation, upgrade the catch-and-shoot personnel, or restore the off-ball motion. Any one of those would close the gap. The current state has none of them.

## The Wolves-only correlation table tells a deeper story

| Pair | Wolves r | League r |
|---|---|---|
| C1 × C5 | 0.731 | 0.356 |
| C1 × C2 | -0.076 | 0.471 |

For the Wolves, stickiness and shot quality decay are tightly coupled (0.73). For the league, they're loosely coupled (0.36). When the Wolves get sticky (one player dominating), their shots get worse. For most NBA teams, that's not true; stickiness can produce fine shots if the dominant player is good enough.

For the league, stickiness and motion death go together (sticky teams also have dead motion). For the Wolves, they're decoupled (-0.08). When the Wolves are sticky, they sometimes have motion and sometimes don't.

**The pattern that emerges: the Wolves are unusual at the relationships between their offensive components, not just at the levels.** The Edwards-era Wolves have built an offense where the components don't fit together the way they fit together for typical NBA teams. That's a deeper architectural problem than any single component being elevated.

Honestly, this surprises me. I expected the Wolves to be a high-level-but-typical-pattern team. The data says they're a typical-level-but-unusual-pattern team. That's worse, not better, because unusual patterns are harder to fix using conventional playbook moves.

## What this means for Phase 4

The agent already proposed the right design: run each predictive regression three ways (Full LAFI, Sharp LAFI, individual components).

**One stretch addition for the writeup phase, not for Phase 4 itself:** a Wolves-pattern LAFI. Create a metric that captures not just the levels of components but the unusual correlations between them. Specifically, identify teams whose C1 × C5 and C2 × C5 patterns look like the Wolves' (tight C1-C5 coupling, anomalous C2-C5 coupling) and see how they performed in the playoffs. This is harder to build, but it tests whether the pattern, not just the level, predicts playoff failure. Hold for the writeup phase rather than blocking Phase 4.

## On the PCA result

The PCA confirms the architecture of the metric is sound. PC1 explains 61.4% (right in the spec's 50-65% target). All five components load on the same direction with similar magnitude. The metric is measuring one coherent underlying construct (pickup-ness) and the construct is real.

**The PC2 finding is what excites me.** PC2 captures 22% of additional variance and independently surfaces the Q3 vs Q4 distinction we developed manually. One end of PC2 is high motion death + narrow playbook + good shot quality (Q3 single-star pickup). The other end is high iso + bad shots + more motion (Q4 distributed pickup).

This is the data validating our qualitative framework. We didn't impose Q3 vs Q4 on the data. We arrived at the framework through cross-component reasoning. Then PCA, run blind, found the same distinction as the second-most-important axis in the league's offensive space. That's strong methodological evidence that the Q3/Q4 framework is a real structural distinction, not just a useful mental model.

For the writeup, this means we can present the four-quadrant framing with statistical backing rather than as analyst intuition.

## Phase 4 prior expectations

Four scenarios for the predictive validation:

**Scenario 1 (60% likely):** Sharp LAFI is significantly more predictive than Full LAFI. Best outcome. Sharp LAFI becomes the canonical headline metric. Wolves' 3rd-in-league ranking becomes the central finding.

**Scenario 2 (30% likely):** Full LAFI is significantly predictive but Sharp LAFI is not meaningfully better. Acceptable. Full LAFI canonical, Wolves at 13th-15th, framing softens.

**Scenario 3 (10% jointly with 4):** Neither predicts at conventional significance. LAFI becomes descriptive rather than predictive. Wolves analysis remains valuable as explanation but doesn't claim general prediction.

**Scenario 4:** Components individually predict but composite doesn't. Most interesting outcome. Suggests composite is wrong aggregation.

## Two things to flag for the writeup

1. **The C2 × C5 finding deserves its own section.** "Wolves combine problems most NBA teams don't combine" is the single most diagnostic thing we've found.
2. **The PC2 validation of Q3/Q4 needs explicit attention.** Qualitative framework + quantitative confirmation = methodological convergence.

## Where the project is

Phase 3 produced four things:

1. A canonical metric that validates the spec's success criteria.
2. A methodological finding (Sharp vs Full LAFI) that adds value.
3. A diagnostic finding (unusual correlation pattern) that sharpens the Wolves story.
4. Quantitative validation of the qualitative Q3/Q4 framework.

**Proceed to Phase 4.** The C2 × C5 finding is real and important but it doesn't change the regression plan. Run the validation three ways as proposed. Most important thing to look at first: whether Sharp LAFI's coefficient on playoff overperformance is larger than Full LAFI's. If yes, the project has its headline metric.

The agent's analytical instinct surfacing C2 × C5 from the correlation matrix unprompted is the kind of thing that distinguishes a project that produces a metric from a project that produces understanding. We're getting understanding.
