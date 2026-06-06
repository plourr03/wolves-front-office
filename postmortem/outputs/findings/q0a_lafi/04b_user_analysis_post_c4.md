# User analysis: Component 4 is the most important finding so far

**Date:** 2026-05-16
**Author:** Bobby
**Context:** Reading the Component 4 result and the refined Q4 diagnosis.

## The miss produced a better finding than the prediction would have

Prior: Wolves 80-95th percentile on Action Poverty. Actual: 45th. That's a real miss. But the reason for the miss is what makes this valuable.

The standard pickup-ball story would have been: "Wolves run only a couple of plays, that's why it feels like LA Fitness." The data says no. They run 11 Synergy play types at >=3% usage. The playbook breadth is normal. League-average normal.

The actual pathology is more specific and more diagnostic: the Wolves have a normal-breadth playbook but allocate possessions badly within it. They run iso 9.6% of the time when they should be running PR-Ball-Handler 16% of the time. They have all the tools. They keep reaching for the wrong one.

This is so much more useful as a diagnosis than "they only run a few things" would have been. Here's why.

- If the problem were narrow playbook, the fix would be coaching install: teach the team more actions. That's relatively cheap.
- If the problem is allocation within a normal playbook, the fix is harder and points to specific things:
  - **Personnel**: the players the team has push the offense toward iso rather than away from it.
  - **Decision-making**: whoever is calling actions or reading defenses is choosing iso when better options exist.
  - **System design**: the offense's default mode is iso when something breaks down, rather than flowing into another action.

Each has different implications:
- Personnel implications point to Q5 (do we need different players who don't gravitate toward iso).
- Decision-making implications point to Q0D (the coaching system question).
- System design implications point to both.

The Q4 quadrant diagnosis is sharper. We're not "a team that runs only iso." We're **"a team that has every option available and keeps choosing iso anyway."** That second framing is much more damning because it removes the easy excuse.

## The LAC comparison is gold and should be preserved in the final writeup

LAC and MIN both reach 89-96th percentile on iso, but through opposite routes. LAC is "sticky hands, narrow playbook" (Harden/Kawhi/PG-style 1-on-1). MIN is "distributed touches, broad playbook, dead off-ball, iso anyway." Same destination, opposite roads.

This matters for the prescription:
- LAC's iso problem is fixable by roster construction (more shooters, more movement guys around the iso stars).
- MIN's iso problem is harder because the playbook is already there but isn't being used. Adding more designed actions to MIN's playbook would not help; the actions already exist. The team isn't running them.

This points to two distinct possibilities for Q5: either the personnel doesn't have the cohesion to execute the actions that exist, or the offensive philosophy defaults to iso when designed actions don't immediately produce. Both are testable later but worth flagging now.

**Specific instruction for the final deliverable:** the refined diagnosis (normal-breadth playbook with bad allocation) and the LAC vs MIN contrast must be preserved as named findings.

## Calibration check: 50% prior accuracy through 4 components

After four components, prior accuracy is 9 of 18, exactly 50%. That's basically random.

The wins were mostly structural (LAC will be sticky, GSW will be designed, the Wolves' motion death will rise). The losses were mostly on Wolves-specific magnitudes (overpredicted stickiness, overpredicted action poverty).

The pattern is informative: better at predicting what category a team falls into, worse at predicting how extreme the Wolves specifically will be on a given component. Useful self-knowledge: trust qualitative predictions about the team, discount magnitude predictions.

## Component 5 prediction (low confidence)

Wolves: 55-75th percentile on Shot Quality Decay. Late-clock contested shots are inevitable given Q4 offense, but the Wolves do have Ant who can manufacture decent shots even from bad situations, and they shoot threes at reasonable volume. So elevated but not extreme. Lower confidence than earlier component predictions given the track record.

## Composite math preview

With weights 25/20/20/20/15, the Wolves through four components:

```
(0.25 * 30) + (0.20 * 71) + (0.20 * 89) + (0.20 * 45)
  =  7.5      +  14.2      +  17.8      +   9.0
  = 48.5  of  85 possible points across first four
```

That's roughly 57% of the available weight pushing the composite up to roughly the 57th percentile if C5 lands at league median. If C5 lands at 75th, composite around 60-65. If C5 lands at 90th, composite around 65-70.

In any scenario the Wolves are not where the original thesis predicted (top 5 league-wide on LAFI). They'll be elevated but not extreme. **That's actually fine for the analysis and arguably better.** The story shifts from "Wolves are pickup ball" to "Wolves are pickup ball on specific dimensions, and those dimensions explain their playoff struggles." Sharper, more defensible, more useful.

## Project shape heads-up: Q7 (Star Comparable Analysis)

No action needed during LAFI. Awareness only.

A new analysis was specced today: Q7 Star Comparable Analysis. It identifies historical stars similar to Anthony Edwards, catalogs the roster constructions that worked and failed around them, extracts the underlying principles, and translates those principles to the modern league. Q7 is a bridge analysis between Q0C (historical cohort, team-level) and Q5 (prescription). Q7 takes Q0C's team-level historical context and adds star-level evidence about what worked around stars like Ant specifically.

The Q7 spec lives at `specs/q7_star_comparable_analysis_spec.md`. The master plan inventory and dependency graph have been updated.

Q7 runs after Q0C and Q1-Q3 are complete, can run in parallel with Q4, and feeds Q5 directly. When LAFI is complete, the agent can pick up Q7 by reading the spec file.

## Direction

Proceed to Component 5 (Shot Quality Decay). After it lands, discuss what the composite tells us before moving to Phase 3 (correlation matrix and PCA diagnostics).
