# User decisions on the replan proposal, plus Q8 addition

**Date:** 2026-05-17
**Author:** Bobby (with data scientist Claude on Q8)
**Context:** Read of the replan proposal. Decisions on the seven decision points, two additions the proposal missed, and a new spec (Q8) added based on what front-office readers will actually want.

## Decisions on the seven decision points

**Decision 1: Q5 portfolio framing.** Three-LAFI-paths become primary. Original portfolios become explicit alternatives, labeled "if the diagnosis is wrong and we are in a more conventional failure mode, here is the template prescription." This preserves the original work but anchors the prescription on the actual diagnosis.

**Decision 2: Q0C cohort weighting.** Accept the proposed rebalancing (LAFI 15%, roster construction 20%) as primary. Add a sensitivity analysis at 5% and 25% LAFI weighting. If the comp set is stable across weightings, the cohort findings are robust. If it shifts dramatically, that tells us how reliant we are on LAFI's architectural framing for similarity matching.

**Decision 3: Action classifier.** Standalone spec, with manual-coding fallback for Q3 as a contingency. If the classifier slips, Q3 should be able to proceed with manual coding for the 2025-26 playoff sample specifically.

**Decision 4: Edwards trajectory.** Expand Q0B (Option A). Avoids spec proliferation. The Edwards trajectory question is genuinely a trajectory question. Q0B Section 4.1 becomes the primary sub-analysis with other rotation players as supporting context. Q0B should run after Q7 (which provides the Edwards comp evidence).

**Decision 5: LAFI v2.** Defer indefinitely with a documented re-trigger condition. Re-trigger if (a) the action classifier gets built and validated, AND (b) someone wants higher-fidelity C4. Keeps the door open without scheduling it.

**Decision 6: Q0D before Q0C.** Yes. The allocation problem finding is fresh and Q0D directly tests it. Q0C can then reference Q0D findings.

**Decision 7: Q6 LAFI counterfactual.** Yes, with a scope cap. Only build the LAFI counterfactual for the headline metric (Sharp LAFI and four-quadrant placement) at 2024-25 and 2025-26 seasons. Don't try to project every component or every season. This keeps the work bounded while preserving the most important finding.

## Two additions the proposal didn't surface

**Issue 1: Q5 archetype framework should be preserved and remapped onto the three paths, not deleted.**

The original Q5 spec had concrete archetypes (secondary creator, stretch big, three-and-D wing). The revised Q5 has three paths. These should reconcile, not replace each other.

- Path 2 (Category B catch-and-shoot) maps to a specific archetype: high-volume catch-and-shoot wings, ideally with defensive switchability.
- The "secondary creator" archetype from the original spec maps to Path 1's interim support (someone who can punish doubles while Edwards develops into not needing that).
- Path 3 (system change) doesn't have an acquisition archetype; it's a coaching question.

When Q5 is revised, the archetypes section should be restructured to map archetypes to paths, not deleted. The original archetype work is still useful; only its framing changes.

**Issue 2: The Wolves-specific anomaly finding (C2 x C5 correlation) should propagate into downstream specs.**

LAFI surfaced that the Wolves have unusual cross-component correlations not seen league-wide (C1 x C5 tight, C2 x C5 lockstep for Wolves but uncorrelated league-wide). This finding lives in the LAFI deliverable but doesn't propagate to any other spec. It should.

- Q0C should test whether historically breakthrough comp teams had Wolves-like anomalous correlations or normal ones. If anomalous correlation predicts failure, that's another differentiator candidate.
- Q4 should incorporate the anomalous correlation as a feature in the archetype stress test. Teams with unusual cross-component relationships may face structural disadvantages even if their component levels look fine.
- Q7 should ask whether any historical comp stars played on teams with anomalous correlation patterns. Were they protected by other factors?

This is methodologically delicate (anomalous correlation is a derived feature, not a raw component) but it surfaced as a meaningful finding and shouldn't be lost.

## Q8 added as a new spec

Based on a conversation with Claude (separate data scientist session) about Gobert and Randle specifically. Three reasons for the addition:

1. The Gobert and Randle contracts are the dominant items on the Wolves' cap sheet outside Edwards. Every front office decision this summer will involve these two.
2. Public discourse this summer will center on these two players. An analytical project that doesn't engage with them specifically risks being seen as theoretical.
3. The Q4 pathology diagnosis from LAFI v1 has direct implications for both players. The project has the infrastructure to test specific player-level hypotheses; no public work does.

**Q8 specific hypotheses (Bobby's theories, to be tested honestly):**

- **Gobert:** Positional constraints (must stay near the rim, cannot shoot) suppress off-ball motion when he is on the floor. This is the LAFI-relevant version of the "he clogs the lane" intuition.
- **Randle:** Possession usage exceeds his marginal value at the team level. His iso possessions are negative-EV.

Both theories are testable. Neither is pre-validated. The data scientist disclosed his own priors (sympathetic to Gobert-as-problem framing) and committed to running the tests honestly even if they don't support the hypothesis.

**Q8 structure (per the spec):**

- 12 pre-committed hypotheses (5 Gobert, 5 Randle, 2 combined)
- Four direct tests for Gobert (motion when on/off, basic on/off, spacing, defensive treatment by opponents)
- Four direct tests for Randle (usage vs efficiency, playoff vs regular season, possession value at margin, fit with Edwards)
- Combined analysis with four scenarios (keep both, trade Gobert keep Randle, keep Gobert move Randle, move both)
- Strong methodological discipline against confirmation bias (Section 9.1)

**Q8 position in build sequence:** between Q6 (which provides KAT counterfactual context) and Q7 (which feeds Q5). Q8 needs Q2's lineup foundation and Q6's counterfactual framing.

## What this means for execution

The replan now has more pieces than the original proposal. The execution session needs to:

1. Update the master plan to a v3 incorporating all decisions and the Q8 addition
2. Revise the four user-named specs (Q5, Q7, Q0C, Q3) per the proposal's edits plus the two additions
3. Revise the other affected specs (Q0B, Q0D, Q1, Q2, Q4, Q6) per the proposal's edits
4. Add anomaly propagation to Q0C, Q4, Q7 per Issue 2
5. Add archetype-to-path mapping to Q5 per Issue 1
6. Create the new Action Classifier spec
7. Add the LAFI v2 deferral with documented re-trigger condition
8. Verify Q8 spec is consistent with the rest of the replan (it was drafted before this replan was finalized)

After execution, pause for review before any new analytical work. The new build cadence picks up after the v3 master plan and specs are confirmed to be coherent with what LAFI actually showed.

## Direction for the agent

"Proposal is approved with the listed decisions. Two additions to incorporate when executing the revisions: (a) Q5 archetype framework should be preserved and remapped onto the three paths, not deleted; (b) the Wolves-specific anomaly finding should propagate into Q0C, Q4, and Q7 as a feature or hypothesis to test. Q8 has been added; the next session should integrate it into the master plan. Execute the spec edits across the master plan and affected specs. Preserve all changes in the findings folder. Pause for review before starting any new build."
