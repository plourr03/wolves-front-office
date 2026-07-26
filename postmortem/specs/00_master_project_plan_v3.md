# Master Project Plan v3: Timberwolves 2025-26 Postmortem and Roster Construction Analysis

**Project owner:** Bobby
**Analytical partner:** Claude
**Started:** May 2026, mid-second-round series vs San Antonio
**Status:** Post-LAFI replan complete. Active build phase for downstream analyses.

**Revision notes (v3 vs v2):**

- LAFI v1 (Q0A) is complete. Findings drove a substantial replan documented in `outputs/findings/q0a_lafi/12_post_lafi_replan_proposal.md` and `12b_user_decisions_and_q8_addition.md`.
- Build sequence reordered: Q7 promoted to immediately before Q5, Q3 scope reduced and moved down, Q0D moved before Q0C, Q8 added between Q6 and Q7.
- Q8 (Player-Specific Roster Decisions for Gobert and Randle) added to the inventory.
- Action Classifier promoted to its own standalone infrastructure spec rather than being embedded in Q3 or LAFI v2.
- LAFI v2 deferred indefinitely with documented re-trigger conditions.
- All affected specs (Q5, Q7, Q0C, Q3, Q0B, Q0D, Q4, Q6, Q1, Q2) revised in their respective files.

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

**(New) First principles when historical analogies are weak.** LAFI v1 established that the Wolves' Q4 pathology is rare and not well-precedented. Where Q0C and Q7 produce thin comp evidence, the prescription must derive from mechanism, not from pattern matching.

## 3. Analysis inventory

The full set of analyses, organized by structural role.

### 3.1 Meta-layer analyses (Question 0)

These sit above the tactical analyses and provide the framing.

| ID | Name | Purpose | Spec Status | Build Status |
|----|------|---------|-------------|--------------|
| Q0A | LA Fitness Index (LAFI) | Quantify offensive "pickup ball" tendency and validate it as a playoff predictor | Complete | **v1 complete (2026-05-17)** |
| Q0B | Trajectory and Windows | Roster age curves, contention window analysis. Now elevates Edwards trajectory to central diagnostic per LAFI Path 1. | Revised (post-LAFI) | Pending |
| Q0C | Historical Cohort Analysis | What happens to teams that look like the 2025-26 Wolves. Now includes LAFI components and quadrant as cohort features. | Revised (post-LAFI) | Pending |
| Q0D | Coaching System Analysis | How Finch's offense changed pre vs post KAT and whether the system is stale. Now anchored on LAFI allocation problem finding. | Revised (post-LAFI) | Pending |

### 3.2 Tactical analyses (Questions 1 through 5)

The core diagnostic and prescriptive work.

| ID | Name | Purpose | Spec Status | Build Status |
|----|------|---------|-------------|--------------|
| Q1 | Diagnose the Break | Regular season vs playoff splits, four factors, lineup baselines. Now cross-references LAFI C5 for shot quality. | Revised (post-LAFI, minor) | Pending |
| Q2 | Localize the Damage | Lineup matrices, two-man combinations, individual on/off. Now tracks iso-per-lineup. | Revised (post-LAFI, minor) | Pending |
| Q3 | Mechanism Analysis | PnR coverage decoder (offense and defense). Q3a reduced to LAFI C5 integration. | Revised (post-LAFI, scope reduction) | Pending |
| Q4 | Archetype Stress Test | Opponent archetype clustering with LAFI quadrant framework added. | Revised (post-LAFI) | Pending |
| Q5 | Prescription | Cap reality, archetype gap analysis, acquisition paths. Restructured around three LAFI paths. | Revised (post-LAFI, significant) | Pending |

### 3.3 Special analyses

| ID | Name | Purpose | Spec Status | Build Status |
|----|------|---------|-------------|--------------|
| Q6 | KAT Retroactive and Counterfactual | Evaluate the KAT-Randle trade with one season of full data, plus structural LAFI counterfactual ("would the Wolves have stayed Q1 with KAT"). | Revised (post-LAFI, scope-capped addition) | Pending |
| Q7 | Star Comparable Analysis | Identify historical stars similar to Ant, extract roster construction principles, translate to modern league. Promoted to immediately before Q5. | Revised (post-LAFI, minor) | Pending |
| **Q8** | **Player-Specific Roster Decisions (Gobert, Randle, DiVincenzo)** | **Decision-prescriptive analysis at the player level. v1 + salary addendum + weighted-recent RAPM complete.** | **Revised (added 2026-05-17)** | **v1 Complete (2026-05-17)** |
| **Q9** | **Superstar acquisition analysis (Giannis, Durant, hypotheticals)** | **Counterfactual roster construction. Addresses the "what about adding a third star" question that Q5 will not recommend but readers will ask about. Trade math, post-trade roster outlook, time-horizon analysis (2026 vs 2027 reset).** | **New (added 2026-05-18)** | **Pending (deferred to post-Q5)** |

### 3.4 Shared infrastructure specs

| ID | Name | Purpose | Spec Status |
|----|------|---------|-------------|
| Action Classifier | PnR coverage classifier from PBP and tracking | Standalone spec (extracted from Q3 and LAFI v2; pending) |

## 4. Build sequence

The order in which to specify and build the analyses. This sequence respects analytical dependencies and prioritizes the highest-leverage pieces first.

**Phase 1: Specification (complete).** All specs are documented in `specs/`.

**Phase 2: Data engineering (complete).** Production warehouse is in place. Tracking and Synergy data are loaded. Lineup-level pipeline is the next infrastructure piece.

**Phase 3: Build, in execution priority order (revised post-LAFI):**

1. **Q0A LAFI v1 — complete.**
2. **Q1 (Diagnose the Break)**: cheapest and fastest. Cross-references LAFI but produces original four-factors and halfcourt/transition splits.
3. **Q2 (Localize the Damage)**: lineup matrices and on/off; now tracks iso allocation per lineup.
4. **Q6 (KAT Retroactive and Counterfactual)**: requires lineup data from Q2 plus LAFI v1 outputs. Includes scope-capped LAFI counterfactual.
5. **Q8 (Player-Specific Roster Decisions: Gobert and Randle)**: requires Q2 lineup foundation and Q6 counterfactual context.
6. **Action Classifier (infrastructure spec)**: separate build that unblocks Q3's PnR coverage decoder. Can be deferred; Q3 has manual-coding fallback.
7. **Q3 (Mechanism Analysis, narrowed scope)**: PnR coverage decoder. Consumes Action Classifier output if available; otherwise manual codes the 2025-26 playoff sample.
8. **Q0D (Coaching System Analysis)**: tests allocation problem finding directly. Moved up because the LAFI allocation finding is fresh.
9. **Q0C (Historical Cohort Analysis)**: includes LAFI components and quadrant as cohort features; runs sensitivity at three LAFI weightings.
10. **Q4 (Archetype Stress Test)**: includes LAFI quadrant framework as a clustering approach.
11. **Q7 (Star Comparable Analysis)**: promoted to immediately before Q5. Star-level historical evidence becomes the primary external benchmark when team-level cohort comps are thin.
12. **Q0B (Trajectory and Windows)**: Edwards trajectory elevated to primary sub-analysis. Runs after Q7 (which provides comp evidence for Edwards' tier-leap probability).
13. **Q5 (Prescription)**: v2 spec (post-diagnostic-completion) collapses paths to one primary + two supporting. Original archetype framework preserved.
14. **Q9 (Superstar acquisition analysis)**: built after Q5. Addresses the "Giannis / Durant / hypothetical star addition" question that Q5 will not primarily recommend. The deliverable's response to "but what about a superstar trade?" The analysis frames why diagnostic findings don't point at this lever, engages the honest counter argument, and addresses the 2026 vs 2027-reset trade-math reality. Built last because it depends on Q5's prescription being settled.
15. **LAFI v2**: deferred indefinitely. Re-trigger conditions: (a) Action Classifier built and validated, AND (b) specific analytical need for higher-fidelity C4.

**Phase 4: Integration and writeup**

15. Synthesize findings across all analyses
16. Build the deliverable (form TBD: memo, deck, or full report)
17. Identify path to front office

## 5. Dependency graph

```
Q0A LAFI v1 (COMPLETE) -> feeds every downstream spec

Q1 -> Q2
       Q2 -> Q6
              Q6 -> Q8
                     Q8 -> Q5
              Q2 -> Action Classifier (manual fallback for Q3) -> Q3
                                                                   Q3 -> Q5

Q0D -> Q0C (Q0D produces allocation findings that Q0C can reference)
        Q0C -> Q4
                Q4 -> Q7 -> Q5
        Q0C -> Q5
                Q7 -> Q0B (Q7 provides comp evidence for Edwards' tier-leap)
                       Q0B -> Q5

LAFI v2 (deferred): re-trigger if Action Classifier built AND need higher-fidelity C4
```

**Key sequencing notes (post-replan):**

- The action classifier is no longer the rate-limiting step. Q3 can proceed with manual coding for the 2025-26 playoff sample if the classifier slips. Only the league-wide generalization of Q3's findings depends on the classifier.
- Q7 is the new linchpin between historical comp evidence and prescription. With Q0C's team-level comp evidence likely to be thin (LAFI showed Wolves' pathology is rare), star-level comp evidence becomes primary.
- Q8 is the decision-prescriptive analysis at the player level. It feeds Q5 but answers questions Q5 alone would not address (the specific Gobert and Randle cases).
- Q0B runs late because its Edwards trajectory analysis depends on Q7's comp findings.

## 6. Shared infrastructure

### 6.1 Data pipelines

The data ingestion pipeline lives in a separate repo, `nba-warehouse` (sibling directory `../nba-warehouse/`). Architecture and operations are documented in `../nba-warehouse/specs/data_pipeline_spec.md`. Current contents in `../nba-warehouse/docs/database_inventory.md`.

All analysis code connects to the production Postgres warehouse at `<SERVER_LAN_IP>:5432 / nba_warehouse`, schema `nba`. Credentials live in `wolves-front-office/.env` (gitignored). The legacy `localhost:4101` instance is decommissioned and must not be used.

Capability inventory (as of 2026-05-17):

- **PBP archive (1997 to 2026):** complete except three specific 2025-26 playoff games. Suitable for all downstream analyses.
- **Team and player game-level stats:** caught up for 2025-26 (RS + playoffs to date).
- **Advanced stats per player and per team per game:** complete for RS, complete for playoffs in the LAFI sample.
- **NBA tracking API ingestion:** wired in. Per-game tables cover roughly the last 13 seasons. Per-season tables span multiple seasons across all `measure_type` slices.
- **Synergy play type data:** present for 12 seasons (2014-15 onward, RS+PO). Used extensively in LAFI Components 3 and 4.
- **Shot chart detail:** 2014-15 through 2025-26 with backfill complete.
- **Hustle, defensive impact, point-shot, shot-location season aggregates:** present for 2025-26 with multi-season coverage in some tables.
- **Matchup-level data:** `nba_boxscore_matchups` is Wolves-only for 2025-26. **Watch item:** league-wide backfill is required if Q3 or Q4 needs cross-team matchup comparisons (e.g., defensive-assignment data for non-Wolves teams in the league-wide validation step). Flag at the start of Q3 and Q4 build sessions so this is not a mid-build surprise. If the backfill is not available, scope Q3 and Q4 to Wolves-specific matchup analysis only.
- **Lineup-level possession data:** not yet built. The next infrastructure piece. Required for Q2 and downstream.
- **Player bio and stints:** `nba_player_bio`, `nba_player_season_bio`, `nba_player_stints` are in place. Replace the BBR roster scrape originally planned.
- **Roster snapshots:** `nba_team_rosters` is 2025-26 only. Historical rosters can be derived from `nba_player_stints` for most analyses.
- **Cap and contract data:** manual on demand (Spotrac).

### 6.2 Computed datasets

- LAFI v1 component CSVs and composite (complete, in `outputs/tables/q0a_lafi/`).
- Lineup net rating table (Wolves-specific, plus league-wide for context). Build target for Q2.
- Possession-level shot quality model (expected eFG given location, defender, clock). Build target if Q3 PnR coverage decoder needs it; LAFI C5 already covers team-season level.
- Action Classifier output. Build target if the standalone Action Classifier spec is executed.

### 6.3 Reusable functions

- Z-scoring within season (in LAFI util.py; promote to lib if used elsewhere)
- Percentile rank conversion (in LAFI util.py)
- Bootstrap confidence interval computation (in `lib/bootstrap.py`)
- Lineup similarity metric (for cohort analyses) — build target
- Team similarity metric (for cohort analyses) — partially covered by LAFI similarity

### 6.4 LAFI v2 deferral (documented re-trigger condition)

LAFI v2 was originally planned to use the Action Classifier for higher-fidelity Component 4 (Action Poverty). With v1 complete and Q3 narrowed, LAFI v2 is deferred indefinitely.

**Re-trigger conditions (both must hold):**

1. The Action Classifier has been built, validated against a manual sample, and meets a documented accuracy target.
2. A specific analytical need for higher-fidelity Action Poverty measurement is identified. Likely sources: a Q3 finding that suggests v1's allocation framing missed multi-action chain density; a Q5 prescription that depends on quantifying playbook breadth at finer grain.

If both conditions hold, LAFI v2 is a focused build: refresh Component 4 with classifier output, re-compute the composite, re-run validation, update the deliverable.

## 7. Living document principle

This master plan is meant to be updated as the project progresses. Specifically:

- When an analysis spec is complete, update the Spec Status and Build Status columns in Section 3
- When new analyses are added or removed, update the inventory
- When findings from one analysis change the priority or design of another, update the build sequence (this is what motivated the v2 -> v3 replan after LAFI v1)
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
- This is not a player development analysis except inasmuch as it surfaces from the trajectory work in Q0B and the Edwards-specific analysis there.
- This is not a financial deep-dive. We will incorporate cap realities into Q5 and Q8 but we will not build a multi-year salary cap model.
- This is not predicting the 2026-27 standings.

---

End of master project plan v3.
