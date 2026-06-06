# User followup: DiVincenzo addition + next-session direction

**Date:** 2026-05-17
**Authors:** Bobby and data scientist Claude
**Context:** Post-replan-execution review. Two new items: a player the original Q8 scope did not include, and a recommendation on what to build first.

## User raised: DiVincenzo

Bobby's note (from text): the original Q8 scope is Gobert and Randle, but DiVincenzo tore his Achilles in round 1. With him out for the year (likely most of 2026-27 too), the team's Category B catch-and-shoot anchor is gone. The summer's roster conversation will include him implicitly even if not explicitly. Worth surfacing in the analysis.

## Data scientist analysis

DiVincenzo has four distinct things going on that belong in different places:

1. **The injury fact.** Achilles tear for a guard typically means a year minimum out, often with diminished athleticism on return. He'll likely miss most or all of 2026-27. Roster construction fact that propagates into every prescription.
2. **The contract fact.** Multi-year deal with significant money remaining. Can't cut him without taking a cap hit. Effectively a dead salary slot for 2026-27 unless a trade partner takes on injured-player risk (rare).
3. **The role fact.** He was the team's primary catch-and-shoot specialist (38.3% on 496 attempts before the injury). In LAFI terms, the closest thing the Wolves had to Category B protection. With him out, the team's Category B personnel drops to Naz Reid (a big), Conley (a smaller volume), and McDaniels (high accuracy but low volume).
4. **The 2024-25 fit fact.** When the Wolves reached the conference finals, DiVincenzo was a meaningful piece. The team architecture that worked had him in it. The team architecture without him has not been tested in a full healthy playoff run.

### Where each piece belongs

- **Injury and contract facts:** Q5 (Prescription) cap reality section. A salary slot that produces zero value in 2026-27 changes what the team can do.
- **Role and 2024-25 fit facts:** Q8 (Player-Specific Roster Decisions), but only secondarily. The decision is whether to plan around his return in 2027-28 or treat him as effectively gone.
- **Category B replacement question:** Q5. "DiVincenzo was the Category B anchor; if he doesn't return to form, the team needs Category B personnel from elsewhere" is a specific Q5 sub-question.
- **2024-25 counterfactual:** note in the Q0A deliverable that the 2024-25 healthy version had a Category B anchor the 2025-26 team didn't.

### Recommendation: extend Q8, don't create Q9

The work to do on DiVincenzo:

1. Quantify his 2024-25 contribution (lineup-level impact, Category B role, defensive value)
2. Project the realistic recovery profile (Achilles return rates for guards in their late 20s)
3. Identify the Category B gap his absence creates in 2026-27 specifically
4. Frame the financial and roster implications for 2026-27 and 2027-28

That's small enough to fit as a Q8 extension. Three players (Gobert, Randle, DiVincenzo) instead of two. The methodology overlaps. The DiVincenzo work is mostly recovery projection and Category B gap analysis, both of which use Q8's analytical infrastructure. Estimated +25-30% to Q8 scope.

The argument for extending Q8 over creating Q9: all three are "what do we do about this specific player" questions. The unified player-focused framing matches how a front office reader would consume it.

The argument against: Gobert and Randle are decisions the front office is actively making. DiVincenzo is largely a non-decision (he's recovering, the contract is what it is, the team adapts). Mixing might dilute the Gobert/Randle work.

On balance: extend Q8. DiVincenzo material is short enough not to overwhelm Gobert/Randle.

## Data scientist's next-session recommendation

The data scientist's recommended sequence:

1. **Build the lineup-level possession data pipeline.** Infrastructure, probably 3-5 days. Prerequisite for Q2 and Q6.
2. **Q1 (Diagnose the Break).** 3-5 days.
3. **Q2 (Localize the Damage).** 5-7 days.
4. **Q6 (KAT Retroactive and Counterfactual).** 1-2 weeks.
5. **Q8 (Gobert, Randle, and now DiVincenzo).** 2-3 weeks.

Roughly six weeks total to get from current state to Q8 done. After Q8 the project has produced the analyses that answer the questions the front office actually faces this summer.

The reasoning for putting the lineup pipeline first: it removes the infrastructure pause between Q1 and Q2 and unblocks Q6 cleanly. Adds a few days but smooths the build.

## Two watch-items the data scientist flagged

1. **Matchup-level data is Wolves-only for 2025-26.** League-wide backfill is candidate ingest for Q3 or Q4. Worth a heads-up to the agent when those analyses start so it's not a mid-build surprise.
2. **Action classifier backwards-compatibility section.** Eventually. If the classifier is built and used for Q3, and then years later someone wants to re-run with an improved version, the output schema needs versioning. The `classifier_version` column is already there; the spec should explicitly say which versions are usable for which analyses. Minor; flag for when the classifier actually gets built.

## Decision

Execute the recommendation:

1. Extend Q8 with DiVincenzo section (spec edit)
2. Flag matchup watch-item in master plan v3
3. Start building the lineup pipeline this session
4. After lineup pipeline is sufficiently built, next session starts Q1

The DiVincenzo addition is a contained spec change. The lineup pipeline is a real infrastructure build but the foundational pieces (substitution parsing, floor-state derivation, validation, possession boundaries) are bounded enough to start this session. The per-lineup aggregation layer that uses these foundations is the next layer and may extend to a follow-up session.

## Quote worth preserving

From the data scientist: "Six weeks ago you had a gut feeling and a screenshot of texts with Scott. Now you have a canonical front-office deliverable on the Wolves' LA Fitness Index pathology, a 13-position revised master plan with explicit dependencies and rationale, 13 spec documents covering every analytical question in the project, a new infrastructure spec for the action classifier, a complete findings folder that preserves the reasoning trail chronologically, a defensible methodology for everything from data extraction through prescription, a clear next-build target. Most analytical projects don't ever reach this state. They either rush to conclusions without the foundation, or they get stuck in spec phase and never build."

That's where the project stands going into the next build wave.
