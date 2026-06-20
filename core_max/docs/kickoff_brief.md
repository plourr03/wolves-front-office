# Core Maximization ("The Joan Bet") — Kickoff Brief

> **Spirit of this project:** we are hunting for the team nobody believed in, the
> one so well-fit it raises everyone's floor and shocks the league. That outcome
> is the right tail of the model, and the whole engine exists to find it and
> price it honestly. The guardrails are not here to suppress upside. They are
> here to make the upside credible, so that when the model believes, the belief
> means something. Optimize for the real version of the dream, never the
> manufactured one.

## What this is

A standalone analysis. It inherits nothing from prior publications, apps, or
repos. Source of truth: `offseason/docs/wolves-core-maximization-spec.md`.

Goal: build a championship-equity engine that correctly prices young-player
development, then use it to evaluate maximizing the existing Wolves core (Fork B:
bet on Joan Beringer, trade Gobert and Randle for fit) against a status-quo
baseline and a splash counterfactual. The objective is P(title), a tail event,
over a 2-year horizon plus a real-options term for the out-year development
upside. The named anti-goal: do not build "confirmation bias with a Monte Carlo
wrapper."

## Decisions LOCKED (spec Section 11)

- Fit over splash. Run from the Morant archetype.
- Bet on Joan = Fork B. Gobert's replacement is not a center.
- Two-trade default; aggregate only for the perfect single fit.
- Stay below the second apron (binding CBA constraint).
- Model young players as sampled distributions, never collapsed means.
- Objective is P(title), a tail event.

## Decisions RESOLVED at kickoff (1/1/1/1)

- **Comp set:** broad, pre-registered structural pool (position group, draft-slot
  band around #17, entry-age band, minutes floor) with archetype as a covariate
  under hierarchical partial pooling. No hand-picked comps.
- **Risk posture:** pure P(title) max as the model objective. Year-1 defensive
  rating is a reported, toggleable diagnostic (distribution + P(title | floor) +
  P(collapse)) that never auto-penalizes the plan. A **human GM veto** is
  retained on a catastrophic Year-1 floor.
- **CBA gate:** hybrid. Reuse the verified deterministic engine
  (`offseason/scripts/evaluate_move.py`, `chain_engine.py`) as the compute core;
  own a clean, config-driven, typed gate interface; re-validate the constants.
- **Horizon:** 2 years integrated, plus a real-options Gobert term carrying the
  year-3+ development upside the window truncates.

## Three review notes folded in

1. **Archetype-condition the box-to-RAPM translation (locked Phase 2).** Box-BPM
   adds one-directional bias against rim protectors (a shot-alterer who does not
   block gets little box credit). Joan is a rim protector, so a uniform map
   systematically buries him on the exact dimension the bet is about. Condition
   the translation by archetype (or carry a rim-protector residual). Default
   error direction is too-pessimistic-on-Joan; correct it visibly and show the
   sensitivity.
2. **Human veto on the defensive-floor diagnostic.** The model optimizes P(title)
   and never auto-penalizes the floor; the GM may still veto a plan with a
   catastrophic Year-1 floor. Surface the diagnostic prominently, not as
   decoration.
3. **Known-transaction regression test (Phase 0).** Reproducing the current cap
   standing only tests the salary rollup; replaying a real completed transaction
   exercises the matching/apron logic directly.

## Still open (decide at Phase 2, not blocking)

Which Randle return archetype to model first: Garland-type (PnR creator +
shooting) vs MPJ-type (size + shooting + scaling creation). Working default:
MPJ-type first (live, reportedly available, scales next to Ant).

## Working norms

No em dashes or en dashes. Plain-language summary accompanies every technical
output. Config-driven and reproducible: fixed seeds, versioned priors, scenarios
defined in config not hardcoded.

## Where things live

- Spec (source of truth): `offseason/docs/wolves-core-maximization-spec.md`
- This project's code: `core_max/`
- Approved kickoff plan: `~/.claude/plans/project-kickoff-read-this-velvet-peach.md`
- Reused CBA engine: `offseason/scripts/{evaluate_move,chain_engine,build_team_state}.py`
