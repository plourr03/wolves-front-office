# Master Project Plan: Timberwolves 2025-26 Postmortem and Roster Construction Analysis

**Project owner:** Bobby
**Analytical partner:** Claude
**Started:** May 2026, mid-second-round series vs San Antonio
**Status:** Specification phase

---

## 1. Project purpose

To produce a rigorous, data-driven analysis of why the 2025-26 Minnesota Timberwolves underperformed expectations in the playoffs, and to identify the specific archetypes of player acquisition, roster construction, and tactical adjustments most likely to meaningfully improve their championship odds going forward.

The intended audience is the Timberwolves front office. The intended outcome is a contribution to the team's roster and strategic decision-making. The personal motivation is a lifelong fan wanting his team to win a championship.

## 2. Project principles

These are non-negotiable principles that govern the entire project. They exist to keep the analysis honest and credible.

**Let the data lead.** No pre-baked conclusions. If the data says Gobert should be traded, we say so. If it says Gobert should stay and the changes should be around him, we say so. The same applies to every player, including Anthony Edwards (though we're not seriously considering trading him absent a request).

**Archetypes before names.** When prescribing roster changes, identify the production thresholds and archetypal needs first. List specific player names only in appendices after the archetype case is made. This is how front offices think.

**Rigor over hot takes.** Every claim needs to hold up across the full playoff sample at minimum, ideally the full season, and where possible across historical comparisons. No anchoring on the eye test of a single game.

**Honest uncertainty.** Where confidence intervals are wide, say so. Where samples are small, say so. Don't oversell findings. Don't undersell them either.

**Be willing to land anywhere.** Each analysis must be willing to produce a "the conventional wisdom is correct" finding as readily as a "the conventional wisdom is wrong" finding. Pre-committing to a conclusion is the fastest way to lose credibility with serious decision-makers.

## 3. Analysis inventory

The full set of analyses, organized by structural role.

### 3.1 Meta-layer analyses (Question 0)

These sit above the tactical analyses and provide the framing.

| ID | Name | Purpose | Spec Status |
|----|------|---------|-------------|
| Q0A | LA Fitness Index (LAFI) | Quantify offensive "pickup ball" tendency and validate it as a playoff predictor | Complete |
| Q0B | Trajectory and Windows | Roster age curves, contention window analysis, year-over-year player development | Complete |
| Q0C | Historical Cohort Analysis | What happens to teams that look like the 2025-26 Wolves | Complete |
| Q0D | Coaching System Analysis | How Finch's offense changed pre vs post KAT and whether the system is stale | Complete |

### 3.2 Tactical analyses (Questions 1 through 5)

The core diagnostic and prescriptive work.

| ID | Name | Purpose | Spec Status |
|----|------|---------|-------------|
| Q1 | Diagnose the Break | Regular season vs playoff splits, four factors, lineup baselines | Complete |
| Q2 | Localize the Damage | Lineup matrices, two-man combinations, individual on/off | Complete |
| Q3 | Mechanism Analysis | Shot quality, PnR coverage decoder (offense and defense) | Complete |
| Q4 | Archetype Stress Test | Opponent archetype clustering and Wolves performance by cluster | Complete |
| Q5 | Prescription | Cap reality, archetype gap analysis, acquisition paths | Complete |

### 3.3 Special analyses

| ID | Name | Purpose | Spec Status |
|----|------|---------|-------------|
| Q6 | KAT Retroactive and Counterfactual | Evaluate the KAT-Randle trade with one season of full data, and project the counterfactual Wolves with KAT | Complete |
| Q7 | Star Comparable Analysis | Identify historical stars similar to Ant, extract roster construction principles from their supporting casts, translate to modern league | Complete |

## 4. Build sequence

The order in which to specify and build the analyses. This sequence respects analytical dependencies and prioritizes the highest-leverage pieces first.

**Phase 1: Specification (current phase)**

1. Master project plan (this document)
2. LAFI specification (complete)
3. Historical Cohort Analysis specification
4. KAT Retroactive specification
5. Q1 through Q5 specifications, in order
6. Q0B (Trajectory) and Q0D (Coaching) specifications

**Phase 2: Data engineering**

7. Pull remainder of 2025-26 PBP data
8. Build tracking data pipeline from NBA API
9. Build the action classifier (rate-limiting step; required for LAFI v2 and Q3)
10. Build lineup-level metric computation pipeline

**Phase 3: Build, in execution priority order**

11. Q1 (diagnose the break): cheapest and fastest, sets the table
12. LAFI v1: highest-leverage original work, no action classifier needed
13. Q2 (localize the damage): lineup matrices and on/off
14. Q3 (mechanism analysis): the PnR coverage decoder, requires action classifier
15. Q6 (KAT retroactive): requires lineup data from Q2
16. Q0C (historical cohort): standalone, can run in parallel
17. Q4 (archetype stress test): requires league-wide data
18. Q7 (star comparable analysis): can run in parallel with Q4
19. Q0B and Q0D (trajectory and coaching): synthesis pieces
20. LAFI v2: with action classifier
21. Q5 (prescription): requires output from all prior analyses, especially Q0C and Q7

**Phase 4: Integration and writeup**

21. Synthesize findings across all analyses
22. Build the deliverable (form TBD: memo, deck, or full report)
23. Identify path to front office

## 5. Dependency graph

Understanding which analyses depend on which is critical for not getting stuck.

```
Q1 (baseline diagnostic)
  +-> Q2 (lineup-level deep dive)
       +-> Q6 (KAT counterfactual)
       +-> Q3 (mechanism analysis)
            +-> LAFI v2 (uses action classifier from Q3)
            +-> Q5 (prescription)

Q0C (historical cohort) -> standalone, feeds Q5 framing

Q4 (archetype clustering) -> standalone, feeds Q5

Q7 (star comparable analysis) -> depends on Q0C and Q1-Q3 findings, feeds Q5 directly

Q0B (trajectory) -> synthesis, requires Q1 and Q2 outputs

Q0D (coaching) -> synthesis, requires Q1, Q2, Q3

LAFI v1 -> standalone, no dependencies beyond league-wide tracking data
```

The single biggest dependency is the action classifier. It is needed for:
- LAFI Component 4 (Action Poverty) at full fidelity
- Q3 (the PnR coverage decoder and action-type classification)

This is why building LAFI v1 first (without the action classifier) is so important: it lets us validate the core thesis without waiting on the most expensive piece of infrastructure.

## 6. Shared infrastructure

Things that need to be built once and reused across analyses.

**6.1 Data pipelines**
- PBP archive (1997-2026, partially in hand)
- NBA tracking API ingestion (per-game, per-possession)
- Lineup-level possession data (derived from PBP)
- Cap and contract data (Spotrac or similar)
- Historical roster and result data (Basketball Reference)

**6.2 Computed datasets**
- Team-season four-factors table, 2014-15 to 2025-26
- Lineup net rating table (Wolves-specific, plus league-wide for context)
- Possession-level shot quality model (expected eFG given location, defender, clock)
- Action classifier output, once built

**6.3 Reusable functions**
- Z-scoring within season
- Percentile rank conversion
- Bootstrap confidence interval computation
- Lineup similarity metric (for cohort analyses)
- Team similarity metric (for cohort analyses)

## 7. Living document principle

This master plan is meant to be updated as the project progresses. Specifically:

- When an analysis spec is complete, update the Spec Status column in Section 3
- When new analyses are added or removed, update the inventory
- When findings from one analysis change the priority or design of another, update the build sequence
- When data engineering reveals constraints not anticipated in specs, update affected specs

The project is large enough that holding it in memory is no longer realistic. This document is the single source of truth for project state.

## 8. Success criteria for the overall project

What does "this project worked" look like.

**Minimum viable:** A coherent set of analyses that the analyst (Bobby) can defend to any informed reader. Findings are honest, methodology is sound, and the work is presentable in some form (memo, deck, or report).

**Strong:** The analyses surface at least two non-obvious insights about the Wolves roster or strategy that the front office should consider. The work is good enough that an analytics-friendly front office contact would pass it up the chain.

**Stretch:** The analysis materially contributes to a Wolves decision-making process. This is mostly outside the analyst's control but it's the north-star outcome.

## 9. What is explicitly out of scope

To prevent scope creep:

- This is not a draft analysis. We're not evaluating the 2026 draft class. (Could be a future project.)
- This is not a coaching evaluation per se. We will analyze the system, not Finch as a coach.
- This is not a player development analysis except inasmuch as it surfaces from the trajectory work in Q0B.
- This is not a financial deep-dive. We will incorporate cap realities into Q5 but we will not build a multi-year salary cap model.
- This is not predicting the 2026-27 standings.

---

End of master project plan.
