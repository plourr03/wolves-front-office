# Post-LAFI replan proposal

**Date:** 2026-05-17
**Status:** Proposal only. No spec edits made in this session. The next session executes whatever is agreed.
**Inputs read:** the canonical LAFI deliverable (`11_wolves_lafi_deliverable.md`), the v2 master plan, and the ten unbuilt specs (Q0B, Q0C, Q0D, Q1, Q2, Q3, Q4, Q5, Q6, Q7).

---

## Executive summary of the replan

LAFI v1 changed three things about the project that propagate into every downstream spec.

1. **The Wolves are not in a known failure mode.** Their Q4 pathology is rare and not well-precedented. The standard prescription template (find a comp team that fixed itself, copy the moves) does not apply because there are few clean comps.
2. **C1 single-star pickup is the historically documented playoff-failure pattern, and the Wolves are not C1-extreme.** The cohort and prescription analyses now need to engage with this asymmetry. The Wolves are failing in a different direction than the league's other recent failures.
3. **LAFI has partially answered questions previously assigned to Q1 and Q3.** Shot quality decay is now diagnosed at the v1 level by C5. Action allocation is now diagnosed at the v1 level by C4. The remaining original tactical work has narrowed.

The four spec revisions the user named (Q5, Q7, Q0C, Q3) are correct. I am also flagging meaningful revisions needed in Q0B, Q0D, Q4, and Q6, plus minor cross-reference updates in Q1 and Q2. I am proposing two new candidate specs (action-classifier infrastructure, Edwards trajectory deep dive) that surface gaps the current set does not cover.

The revised build sequence promotes Q7 to immediately before Q5, narrows Q3 to PnR coverage only, and orders downstream analyses so each consumes LAFI findings explicitly rather than working around them.

---

## Part 1: The four user-named spec revisions

### Q5 Prescription (significant rewriting)

**Affected sections:** 1.3 (principles), 2 (gap analysis), 4 (acquisition paths), 6 (integration), 9 (worries).

**Why this needs to change.** The current Q5 spec implicitly assumes that the prescription will identify gap archetypes against a known failure mode, then prescribe archetypes that have historically closed those gaps in comp teams. LAFI v1 broke that assumption. The Wolves are not in a known failure mode; the cohort and historical-comp evidence will be thinner than the spec assumes; and the prescription must derive from first principles anchored on the three independent fixable paths surfaced in the diagnosis.

**Proposed concrete edits:**

- **Section 1.3 (principles), add a fifth principle:** "First principles, not pattern matching. The Wolves' pathology is rare in the historical record. Prescription leans on the diagnosed mechanism (Q1-Q4, LAFI), not on copying what worked for similar teams, because few similar teams exist. Where historical evidence exists (Q0C, Q7), use it; where it does not, derive from mechanism."

- **Section 2.1 (compiling the gaps), restructure around the three paths from the LAFI diagnosis instead of the current illustrative bullet list:**
  - Path 1 gaps: Edwards developmental ceiling (does the team reach Category A protection)
  - Path 2 gaps: catch-and-shoot personnel (Category B protection)
  - Path 3 gaps: designed off-ball motion (the allocation problem)
  - Plus the existing defensive and structural gaps from Q1-Q4 (preserve as is)

  The three paths become the spine of the prescription. The original four illustrative bullets are reabsorbed into one of the three paths or kept as supplementary diagnostic items.

- **Section 2.3 (the archetype need), add for each path:**
  - Path 1: production thresholds for "Category A creator" (e.g., usage > 28%, TS% > 60% on iso, foul-drawing rate, etc.). The archetype the Wolves need Edwards to grow into.
  - Path 2: production thresholds for elite catch-and-shoot wings (e.g., 38%+ on 5+ catch-and-shoot 3PA per game, defensive minimum). The archetype to acquire.
  - Path 3: production thresholds for "system change" (system metrics that would have to shift: PR-Ball-Handler frequency restored to 14-16%, off-ball motion lifted from 10% to ~14%, etc.). This is a coaching path, not an acquisition.

- **Section 4 (acquisition paths), add a fifth path category called "system change":** Restoring designed off-ball motion through coaching. The first non-acquisition path in the analysis. Required because the LAFI allocation finding showed this is the only fixable path that does not require new personnel.

- **Section 4.4 (the recommended portfolio), revise the three example portfolios:**
  - **Portfolio A (system-first):** Coaching emphasis on restoring 2023-24 allocation. Minor catch-and-shoot acquisition (MLE level). Hold Gobert, Randle. Bet on Path 3 with light Path 2 support.
  - **Portfolio B (Category B acquisition):** Trade for a high-volume catch-and-shoot wing using draft capital. Pair with system changes. The targeted Path 2 plus Path 3 combination.
  - **Portfolio C (preserve flexibility for Path 1):** Minimize moves while Edwards' trajectory plays out. Use system changes to close part of the gap. Keep cap flexibility for 2026-27 when Edwards' tier becomes clearer.

  The original example portfolios A, B, C (internal-plus-targeted, reset-and-rebuild, all-in) can be preserved as additional alternatives but the LAFI-derived portfolios above should be primary.

- **Section 6 (integration), add explicit LAFI consumption:** "Q5 consumes the LAFI v1 diagnosis (the four-act trajectory, the C1 contrast, the allocation problem, the Spurs case study) as the primary structural framing. Q1-Q4 sharpen the diagnosis but LAFI provides the architectural categorization that determines which prescription path applies."

- **Section 9 (what I'm worried about), add a new worry:** "Forcing historical analogies. The Wolves' pathology is rare. The temptation will be to find a comp team and overweight it. Resist. If the cohort and Q7 evidence is thin, present it as thin rather than dressing it up."

**Estimated rewriting effort:** roughly 30% of the spec. Sections 3 (cap reality) and 5 (math) need only light updates; the structural skeleton in Section 4 and the framing in Sections 1, 2, 6, 9 are the heavy lifts.

---

### Q7 Star Comparable Analysis (re-prioritized, content largely unchanged)

**Affected sections:** content unchanged, position in master plan moved up.

**Why this needs to change.** The Q7 spec itself is well-written and the methodology holds up post-LAFI. What changes is its priority. Originally Q7 ran in parallel with Q4 and before Q5. Given LAFI's finding that team-level historical comps are thin for the Wolves, the star-level historical evidence becomes the primary external benchmark for Q5. Q7 should land before Q5 with no waiting.

**Proposed concrete edits to Q7 spec content:**

- **Section 1.3 (relationship to other analyses), add a sentence:** "Following the LAFI v1 finding that the Wolves' team-level pathology is rare and not well-precedented, Q7's star-level evidence becomes the primary external benchmark for Q5. Where Q0C provides weak team-level analogies, Q7 must provide stronger star-level ones."

- **Section 5.1 (candidate principles), add an explicit Wolves-specific addendum to Principle 4 (off-ball gravity threat):** Reference the LAFI finding that the Wolves lack Category B protection. The principle is already there; the LAFI-specific application would say "the Wolves' catch-and-shoot personnel is good not great and the Path 2 prescription depends on this principle being correct in modern terms."

- **Section 5.1, Principle 1 (secondary creator):** add a Wolves-specific sub-principle: "for Q4 architectures specifically, the secondary creator may need different traits than for Q3 architectures. Q3 (single-star) teams need a release valve; Q4 (distributed iso) teams need someone who can convert distributed touches into actual designed actions rather than more iso. Whether this is one of the seven principles or a distinct one to be added depends on what the comp analysis finds."

**Proposed master-plan position:** Q7 runs after Q3 completes (Q7 needs Q1-Q3 outputs as inputs per the existing spec) and immediately before Q5. Not in parallel with Q4.

**Estimated additional effort:** minor. A handful of sentence-level edits to integrate the LAFI framing. The bulk of the spec is unaffected.

---

### Q0C Historical Cohort (significant cohort-definition revision)

**Affected sections:** 2.1 (base cohort), 2.2 (similarity-adjusted cohort), 3.2 (secondary labels), 5 (the prescriptive analysis), 5.3 (deep case studies).

**Why this needs to change.** The current Q0C cohort is defined by record + playoff exit (top-10 SRS team that lost in R2 or close). LAFI v1 added a finding the current cohort cannot encode: the historical playoff-failure pattern is C1-extreme, and the Wolves are not. The cohort analysis needs to incorporate LAFI components (especially C1 and the Sharp LAFI subset) as features so we can distinguish "comp by record" from "comp by architecture." The Wolves comp matching should privilege architecture-similar teams (Q4-leaning, unusual component relationships) over record-similar teams.

**Proposed concrete edits:**

- **Section 2.1 (base cohort), add a paragraph at the end:** "Each cohort team-season should also be annotated with its LAFI components and quadrant placement (Q1/Q2/Q3/Q4). This allows downstream analysis to filter or stratify by architectural pattern, not just record. The base cohort definition remains record-and-result based; the LAFI annotations are a layered feature."

- **Section 2.2 (similarity-adjusted cohort), add LAFI features to the similarity dimensions:**
  - Add to roster construction: "LAFI components (C1 through C5) and quadrant placement"
  - Add to similarity weighting: "LAFI similarity: 15% (added to the existing dimensions; reduce roster construction weight from 25% to 20% to make room, or rebalance overall weights)"
  - The Wolves' specific Sharp LAFI 90 / Full LAFI 65 / Q4 placement becomes the matching target for architecture-similar comps.

- **Section 2.4 (expected similar comps), revise the prior list to flag which are Q3 vs Q4 leaning:** Several of the listed expected comps (Memphis, Utah, Chicago, Indiana, Detroit) are Q1 or Q2 leaning, not Q4. This is fine descriptively but should be noted. Add to the prior list: "We expect the architecture-similar Wolves comps to be sparse precisely because Q4 is rare. The cohort analysis should not be surprised if architecture-similar comps are 2-4 teams rather than 10-15."

- **Section 3.2 (secondary labels), add three LAFI-relevant labels:**
  - "Was the team C1-extreme (Q3 single-star pickup) or non-C1-extreme?"
  - "Did the team shift its LAFI profile away from C1-extreme within 3 years (specifically away from single-star pickup)?"
  - "What quadrant did the team move to over the 3-year window (if any)?"

- **Section 5.1 (the comparison), the breakthrough vs stuck split should be augmented with C1 stratification:**
  - Among C1-extreme breakthrough comps, what specifically did they shift?
  - Among non-C1-extreme breakthrough comps (small sample, but relevant for the Wolves), what did they do? This is the most directly relevant subset for the Wolves prescription, even if sparse.

- **Section 5.2 (candidate differentiators), add three new candidates to test:**
  - "Acquired a high-volume catch-and-shoot specialist (Category B protection)"
  - "Restored designed off-ball motion through coaching (system change with stable roster)"
  - "Stars who reached top-10 league tier within the 3-year window enabled different prescription paths"

- **Section 5.3 (deep case studies), revise the case selection:**
  - **Breakthrough case:** Currently proposed as 2019-20 Nuggets. Confirm post-LAFI. The Nuggets' LAFI profile pre-bubble might be illustrative if they were C1-leaning before becoming Q1.
  - **Stuck case:** Currently 2017-19 Jazz. Worth checking their LAFI profile. The Jazz had Mitchell as a primary creator; were they C1-extreme?
  - **Decline case:** 2014-16 Grizzlies. The Memphis grit-and-grind was structurally Q1 leaning (designed) with weak offense overall. Different from Wolves.
  - **Add a fourth case (if any comp surfaces):** A historical Q4-leaning team that broke through. If none exist, that itself is the finding and should be reported.

**Estimated rewriting effort:** roughly 25% of the spec. The cohort definition (2.1) and similarity computation (2.2) are the most affected. The math (Section 4) does not need to change.

---

### Q3 Mechanism Analysis (significant scope reduction)

**Affected sections:** 2 (the three sub-analyses), 3 (Q3a in full), 8 (sequencing).

**Why this needs to change.** Q3 originally had three sub-analyses: Q3a (shot quality vs shot making), Q3b (PnR coverage decoder offense), Q3c (PnR coverage decoder defense). LAFI Component 5 (Shot Quality Decay) has now done Q3a's headline work at the v1 level. LAFI Component 4 (Action Poverty) has done the action classification piece. Q3 should narrow to the PnR coverage decoder, which is the highest-leverage tactical original work and is not duplicated by LAFI. This narrows the scope and accelerates the timeline because the action classifier infrastructure is now solely justified by PnR coverage classification.

**Proposed concrete edits:**

- **Section 2 (the three sub-analyses), restructure:**
  - Remove Q3a as a primary sub-analysis. Replace with a short "Q3a-integration" section that summarizes LAFI C5 findings and adds the player-level shot quality decomposition LAFI didn't do (per-player expected eFG gap analysis is still original work).
  - Q3b (PnR coverage decoder offense) becomes the main analysis.
  - Q3c (PnR coverage decoder defense) is preserved as is.

- **Section 3 (Q3a), shrink from a full sub-analysis to an integration section:**
  - **Section 3.1-3.2:** delete the framework and model-building paragraphs. Reference LAFI C5 instead.
  - **Section 3.3:** preserve the gap analysis but narrow to player-level (LAFI did team-level). Add: "The team-level shot quality gap is established by LAFI C5 (Wolves at 83rd percentile shot quality decay, league avg ~50). Q3a's contribution is player-level decomposition: which Wolves players are individually under-converting (shot-making) vs which are being put in bad-shot situations (shot quality)."
  - **Section 3.4:** preserve as is. Player-level breakdown is still original.

- **Section 4 (Q3b PnR coverage decoder offense):** unchanged. This is the central original work.

- **Section 5 (Q3c PnR coverage decoder defense):** unchanged.

- **Section 8 (sequencing), revise the time estimate:**
  - Was: "3-4 weeks, of which 2-3 weeks is the action classifier work"
  - Becomes: "2-3 weeks. The action classifier work is the heaviest piece. Since Q3a is now an integration with LAFI rather than a build, the classifier is the rate-limiting step but is solely justified by Q3b/c. If the classifier is built as a separate infrastructure spec (recommended), Q3 itself becomes 1-2 weeks of work consuming that infrastructure."

- **Section 9 (worries), update:** the "shot quality model is non-trivial" worry was about Q3a. With Q3a reduced, this worry shrinks. Replace with: "The action classifier is the rate-limiting work. If it is separated into its own spec, Q3's timeline becomes more predictable."

- **Section 10 (success criteria), revise:** strike the "expected eFG model is built and the shot quality vs shot making decomposition is informative" minimum-viable criterion. Replace with reference to LAFI C5's existing decomposition.

**Estimated scope reduction:** roughly 25% of original spec content removed; 5% added for integration. Net Q3 spec gets 20% smaller. Timeline reduces from 3-4 weeks to 1-2 weeks if the action classifier is built separately.

---

## Part 2: Other specs that need adjustment

### Q0B Trajectory and Windows (moderate revision)

**Why this needs to change.** Q0B already touches on Edwards' trajectory (Section 4.1) but treats it as one of several diagnostic questions. LAFI elevated Edwards' developmental ceiling to **the** consequential variable for the prescription. The "Wolves get Category A protection automatically if Edwards reaches Luka/SGA tier" framing means Q0B's Edwards analysis is no longer one of six questions; it is the central question.

**Proposed concrete edits:**

- **Section 1.3 (the working hypothesis), add a paragraph:** "Per LAFI v1, Edwards' developmental trajectory determines whether the Wolves receive Category A protection (his solo creation manufacturing shot quality despite motion death) over the contention window. Q0B's Edwards analysis is the highest-priority diagnostic, not one of six equal questions."

- **Section 4.1 (Is Edwards still ascending?), expand from a single sub-question to a full sub-analysis:**
  - Add: comparison of Edwards' age-24 production to historical comparables at the same age (drawing on Q7 outputs once available)
  - Add: explicit assessment of whether his trajectory suggests Luka/SGA tier is reachable, with appropriate uncertainty
  - Add: connection to LAFI Path 1 framing (Plan A only if his trajectory continues)

- **Section 4.6 (the window verdict), revise:** the window verdict now depends on Edwards' trajectory more than on Gobert's decline. The synthesis should reflect this asymmetry.

- **Section 7 (worries), add:** "Edwards' ceiling is the project's single most consequential prediction. Be extra careful about projecting a leap that the data does not support, and equally careful about projecting a plateau that the data does not support."

**Estimated rewriting effort:** roughly 15% of the spec. Mostly expansion of Section 4.1 and 4.6.

### Q0D Coaching System (minor revision)

**Why this needs to change.** Q0D's working hypothesis already aligns with LAFI findings. The "allocation problem" finding (LAFI Section 6 of the deliverable) sharpens Q0D's central question. The 2023-24 baseline is now empirically validated as the most-designed version of the offense.

**Proposed concrete edits:**

- **Section 1.4 (working hypothesis), update:** the hypothesis can now be grounded in specific LAFI evidence. "The 2024-25 and 2025-26 offense has progressively become less systematic" becomes "LAFI v1 confirmed: Off-ball motion (Cut + OffScreen) has held flat at 10-11% across all five Edwards-era seasons. What has shifted is iso displacing pick-and-roll (iso 7.8% to 9.6%, PR-Ball-Handler 14-16% to 13.1%). The system has not lost actions; it has reallocated them."

- **Section 4.2 (is the change personnel-driven or coach-driven?), sharpen:** add that LAFI's allocation finding is the most coaching-actionable diagnosis in the project. The Q0D analysis should specifically test whether the iso/PR shift correlates with personnel (Randle vs KAT) or with same-personnel within-season choices.

- **Section 4.5 (the stale verdict), revise the four options:** add a fifth option suggested by LAFI: "Allocation-shifted: the playbook is preserved but the calling has changed toward iso. Same actions, different choices."

**Estimated rewriting effort:** roughly 10% of the spec. Mostly Sections 1.4 and 4.

### Q1 Diagnose the Break (minor revision, cross-reference)

**Why this needs to change.** Q1's four-factors decomposition is still original and necessary. But LAFI has partially answered the offensive shot-quality question. Q1 should cross-reference LAFI rather than duplicating work.

**Proposed concrete edits:**

- **Section 1.3 (expected output), add:** "Shot-quality-side findings should cross-reference LAFI C5 rather than re-derive. Q1 focuses on the four-factors decomposition and the halfcourt vs transition split, which are LAFI-orthogonal."

- **Section 2.2 (metric set), no change.** The four-factors and dropoff comparisons are not redundant with LAFI.

- **Section 4.2 (where in the four factors is the decline concentrated?), add:** "For eFG% specifically, LAFI C5 has documented shot-quality decay at the team-season grain. Q1's contribution here is the playoff-specific dropoff (Wolves playoff eFG% vs Wolves regular-season eFG% vs league-average playoff dropoff). This is a different question than C5 answered."

- **Section 7 (sequencing), update:** Q1 sequencing is unchanged but its findings should be presented alongside LAFI v1 in the deliverable.

**Estimated rewriting effort:** roughly 5% of the spec. Cross-reference adds only.

### Q2 Localize the Damage (minor revision)

**Why this needs to change.** Q2 is lineup-level on/off and WOWY. LAFI does not overlap, but the "distributed iso" finding implies Q2 should track action allocation by lineup, not just net rating. The Naz vs Gobert at 5 question is sharpened by LAFI's catch-and-shoot personnel finding (Naz is a 38.1% catch-and-shoot shooter; Gobert is not a shooter at all).

**Proposed concrete edits:**

- **Section 2.1 (lineup-level data), add a metric:** "Iso possessions per 100 possessions, per lineup. Tracks where the LAFI-identified iso allocation problem is concentrated by lineup."

- **Section 5.2 (does the Gobert vs Naz at the 5 question have a clean answer?), expand the framing:**
  - The LAFI finding that the Wolves lack Category B protection makes Naz's catch-and-shoot ability a structural asset, not just a tactical advantage in specific lineups. Q2's Gobert-vs-Naz analysis should explicitly engage with this.
  - Add: "Naz at the 5 provides one form of Category B protection (a stretch big who can catch-and-shoot at 38%). Gobert at the 5 provides rim protection but no shot-quality manufacturing for the off-ball players. The trade-off is more LAFI-relevant than the spec originally framed."

- **Section 6 (integration), add:** "Q2 feeds Q5 with explicit lineup-level evidence of the LAFI allocation problem. Lineups where iso is heaviest become the units to focus on for the system-change Path 3."

**Estimated rewriting effort:** roughly 10% of the spec. Mostly Section 5.2 expansion.

### Q4 Archetype Stress Test (moderate revision)

**Why this needs to change.** Q4's clustering approach can now incorporate LAFI's empirically-validated quadrant framework. PCA's PC2 axis independently surfaced the Q1/Q2/Q3/Q4 framework. Q4 should either use LAFI components directly as clustering features or use the quadrant placement as a candidate clustering approach. Q4's "archetype prevalence over time" analysis should specifically track Q4 prevalence as it relates to the Wolves' novel-pathology claim.

**Proposed concrete edits:**

- **Section 2.1 (the features), add LAFI components to the clustering feature set:**
  - Add: "LAFI components C1-C5 (when computable, 2014-15 onward)"
  - Add: "Sharp LAFI score (when computable)"
  - These are already z-scored within season, so they integrate cleanly with the existing z-scored features.

- **Section 2.3 (the clustering method), add a second clustering approach:**
  - Original: K-means on the feature set.
  - Add: "Quadrant-based: classify teams by LAFI quadrant (Q1/Q2/Q3/Q4) and treat each quadrant as a cluster. Cross-validate against k-means results. If the two approaches produce similar partitions, the quadrant framework is the more interpretable cluster definition."

- **Section 4.1 (archetype prevalence analysis question), add a specific question:** "Has Q4 (distributed pickup) prevalence risen, fallen, or stayed stable across the last decade? If Q4 prevalence has been rising, the Wolves are an early example of an emerging archetype. If stable, the Wolves are an outlier."

- **Section 4.4 (championship correlation), add:** "Cross-reference with the C1 univariate finding. Have any Q4-leaning teams won championships? Reached finals? If not, the Wolves' Q4 placement is a structural disadvantage. If a Q4 team has won, identify what they did differently."

**Estimated rewriting effort:** roughly 20% of the spec. Mostly Sections 2.1, 2.3, 4.1, 4.4.

### Q6 KAT Counterfactual (significant additions)

**Why this needs to change.** LAFI has confirmed that the KAT-era 2023-24 offense was the most-designed version. Q6's counterfactual currently substitutes KAT for Randle at the lineup-level RAPM grain. With LAFI in hand, Q6 can also ask the structural question: "what would the Wolves' LAFI profile likely have been with KAT?" This becomes the structural complement to the lineup-level work.

**Proposed concrete edits:**

- **Section 4.2 (KAT-in-Wolves projection), add a sub-step "Step 5: LAFI projection":**
  - For 2024-25 and 2025-26, project the Wolves' LAFI components under the counterfactual where KAT stays.
  - Methodology: substitute KAT's role characteristics (catch-and-shoot share, off-ball gravity, pick-and-pop frequency) into the Wolves' lineup composition and recompute the LAFI sub-metrics.
  - The 2023-24 KAT-era LAFI profile (Full LAFI 35, Sharp LAFI 45) is the baseline.

- **Section 4.4 (further counterfactuals), add an explicit LAFI-trajectory counterfactual:**
  - "Would the Wolves have remained in Q1 with KAT? Or would they have drifted toward Q3 anyway because Randle was not the sole driver of the Q4 collapse (Gobert's decline, DiVincenzo's loss, system contraction also contributed)?"
  - This question is empirical given the trajectory data and matters for the prescription.

- **Section 7.2 (what Q6 feeds), update:**
  - Was: "Q6 establishes upper-bound benchmark for what one major acquisition can do"
  - Becomes: "Q6 establishes both the upper-bound benchmark and the structural counterfactual. The structural piece (would the Wolves have been Q1 with KAT) informs whether the current Q4 placement is fixable by personnel or whether it would have emerged regardless of the trade."

- **Section 8.3 (charts), add:** "The Counterfactual LAFI Trajectory: a small-multiples chart showing the actual 2023-24 through 2025-26 LAFI components alongside the counterfactual KAT trajectory for the same years. Visualizes whether KAT would have prevented the Q1 to Q4 migration."

**Estimated additions:** roughly 15% of the spec. Mostly Sections 4.2-4.4 and 8.

---

## Part 3: Revised build sequence

**Current v2 master plan sequence (Phase 3, post-data-engineering):**

```
11. Q1
12. LAFI v1                  ← complete
13. Q2
14. Q3 (original scope)
15. Q6
16. Q0C
17. Q4
18. Q7 (parallel with Q4)
19. Q0B + Q0D
20. LAFI v2
21. Q5
```

**Proposed revised sequence:**

```
LAFI v1                       ← complete (already done)

12. Q1 (with LAFI cross-references; minor revision)
13. Q2 (with iso-by-lineup tracking; minor revision)
14. Q6 (with LAFI counterfactual addition; significant additions)
15. ACTION-CLASSIFIER (new infra spec, see Part 4) [optional, can defer]
16. Q3 (narrowed scope: PnR coverage only; Q3a reduced to LAFI integration)
17. Q0D (with allocation problem integration; minor revision)
18. Q0C (with LAFI features in cohort definition; significant revision)
19. Q4 (with LAFI quadrant framework; moderate revision)
20. Q0B (with elevated Edwards trajectory analysis; moderate revision)
21. Q7 (largely unchanged, re-prioritized; runs after Q3, before Q5)
22. Q5 (significantly rewritten; first-principles prescription anchored on three paths)

LAFI v2 (deferred; depends on action classifier; can run after Q5 or in parallel)

23. Integration writeup
```

**Rationale for the reordering:**

- **Q1 and Q2 remain near the front** because they are tactical foundation. Q1 establishes what broke; Q2 establishes who broke it. Both feed everything else.
- **Q6 moves up to position 14** so the LAFI counterfactual question is answered before Q3 starts. Q6 also confirms whether the 2023-24 designed offense was reachable with KAT-era personnel, which informs Q3's expected findings.
- **Action classifier is now a candidate standalone spec** because its only remaining downstream consumer (with Q3 narrowed) is Q3's PnR coverage decoder. Building it as a separate spec makes its scope and timeline visible and lets Q3 start without waiting if v1 of Q3 uses manual coding for the playoff sample.
- **Q3 moves down to position 16** because its scope is narrower and its main piece (PnR coverage) is downstream of action classifier infrastructure.
- **Q0D moves up to position 17** (before Q0C) because the allocation problem finding from LAFI is fresh and Q0D directly tests the hypothesis.
- **Q0C stays in the middle** but with revised cohort definition. It feeds Q5.
- **Q4 stays after Q0C** because its archetype clustering benefits from the cohort-level historical framing.
- **Q0B moves later (position 20)** because Q0B now elevates Edwards' trajectory as a primary diagnostic, which is also the dominant Q7 input. Building Q0B and Q7 closer together is efficient.
- **Q7 moves to position 21** (immediately before Q5) per user direction. Q7 needs Q1-Q3 findings as inputs and feeds Q5 directly.
- **Q5 stays last** but with the substantial rewrite. Q5 consumes Q7 (star comp principles) and Q0C (cohort base rates) plus the LAFI-derived three paths.

**The single biggest sequencing change:** Q7 moves up (good, per user), Q3 moves down (good, narrower scope), Q0D moves up (good, allocation problem is immediate). The Q5 rewrite happens before the build, not after.

---

## Part 4: Gaps and new candidate specs

LAFI surfaced two gaps the current spec set does not cover. Each is a candidate for a new spec or a sub-section of an existing one.

### Candidate new spec: Action Classifier Infrastructure

**Why a new spec.** The action classifier is currently treated as shared infrastructure across LAFI v2 and Q3. With Q3 narrowed and LAFI v2 deferred, the classifier is solely justified by Q3's PnR coverage decoder. It is still a multi-week build with its own design choices (manual vs automated, coverage taxonomy, validation methodology, accuracy targets). Treating it as a standalone spec makes its scope visible, lets it be planned and built independently of the analyses that consume it, and makes deferral or simplification decisions explicit.

**Proposed scope:**
- Action taxonomy (PnR, ICE, blitz, switch, drop, etc.) with explicit definitions
- Automated classifier from PBP and tracking
- Manual coding fallback for validation
- Accuracy targets (precision, recall for each coverage type)
- Validation sample (small set of manually coded games)
- Output schema (per-PnR row with coverage label and confidence)
- Sequencing: probably 2-3 weeks if built; can be deferred if Q3 uses manual-only for the playoff sample

**Decision point for the user:** is the classifier worth building, or should Q3 use manual coding for the 2025-26 playoff sample only and skip the league-wide automation? The latter is faster but limits Q3's generalizability.

### Candidate new spec or sub-section: Edwards Developmental Trajectory Deep Dive

**Why a new spec or sub-section.** LAFI's Path 1 says "Edwards develops into Category A solo creator," and the Front Office Takeaways made this the single most consequential variable for the contention window. Q0B touches on Edwards' trajectory (Section 4.1) but treats it as one of six diagnostic questions. Q7 will identify Edwards comp stars but at the "what built around them" level, not at the "did they make the next leap" level. The specific question "what is the probability Edwards reaches Luka/SGA tier in the next two seasons" is not formally owned by any current spec.

**Two options:**

Option A: **Expand Q0B Section 4.1 into a full primary sub-analysis.** Q0B already covers age curves and player trajectories. Pulling Edwards out as the primary sub-analysis (with the other rotation players as supporting) is a reasonable scope adjustment.

Option B: **New spec Q8: Edwards Tier-Leap Analysis.** Standalone analysis. Uses Q7 comp set plus historical guard development data. Output is a probabilistic forecast of Edwards' trajectory across the next 3 seasons.

**Recommendation:** Option A (expand Q0B Section 4.1) is the lighter-weight approach and avoids spec proliferation. Option B is appropriate if the analysis grows substantially or if the user wants the Edwards question to be a standalone deliverable independent of Q0B.

**Decision point for the user:** which option?

### Sub-section candidate: Allocation Restoration Impact Analysis

**Why.** LAFI's "allocation problem" finding is coaching-actionable (the only one). Quantifying the impact of restoring the 2023-24 allocation (iso back to 7-8%, PR-Ball-Handler back to 14-16%) is a forward-looking analysis with direct Q5 implications. Currently no spec owns this.

**Recommendation:** Add as a sub-section to Q0D (Coaching System Analysis). Q0D already engages with system-vs-personnel questions. The allocation restoration sub-section asks: "if we hold personnel constant and shift allocation back to 2023-24 ratios, what net rating change would we expect?" The math is straightforward given the LAFI data and the per-action PPP data from Synergy.

No new spec needed; this is a Q0D enhancement.

### Gap that does NOT need a new spec: LAFI v2

LAFI v2 with the action classifier is mentioned in the LAFI deliverable. It can be deferred indefinitely without blocking other analyses because Q3's narrowed scope no longer depends on it, and Q5 can use LAFI v1 findings. LAFI v2 stays as a "later" item in the master plan, run only if the action classifier gets built and validated for other purposes.

---

## Part 5: What does NOT need to change

Several things are worth naming to confirm they stay as they are.

- **The project principles (Section 2 of the master plan).** "Let the data lead," "archetypes before names," "rigor over hot takes," "honest uncertainty," "be willing to land anywhere." All vindicated by the LAFI process. No changes.
- **The success criteria (Section 8).** Minimum viable / strong / stretch tiers are still the right framing. No changes.
- **The project's out-of-scope items (Section 9).** No changes.
- **Q1's four-factors framework.** Still original and necessary. Minor cross-references added, structure unchanged.
- **Q2's lineup heatmap approach.** Still original and necessary. Minor additions for iso tracking, structure unchanged.
- **The Q7 spec's content.** Position changes, but the methodology, candidate pool, principle library, and translation framework are all sound. Only minor sentence-level edits to integrate LAFI framing.
- **The master plan principles, success criteria, and out-of-scope sections.** No edits proposed.

---

## Part 6: Decision points the user needs to resolve before the next session executes

To convert this proposal into edits, the user needs to decide on the following:

1. **Q5 portfolio framing.** The proposal restructures the recommended portfolios around the three LAFI paths (system-first, Category B acquisition, preserve flexibility for Path 1). The original portfolios (internal-plus-targeted, reset-and-rebuild, all-in) are preserved as alternatives. Confirm this is the right balance, or specify a different framing.

2. **Q0C cohort weighting.** The proposal adds LAFI similarity at 15% weight and reduces roster construction from 25% to 20%. Confirm this rebalancing, or specify different weights.

3. **Action classifier as standalone spec or in-line in Q3.** The proposal recommends standalone (it makes scope visible). The alternative is keeping it inside Q3 with explicit timeline allocation. Confirm.

4. **Edwards trajectory: expand Q0B or create new Q8.** The proposal recommends expanding Q0B. Confirm or choose the alternative.

5. **LAFI v2.** Defer indefinitely, or schedule for after Q5? The proposal recommends defer indefinitely.

6. **Build sequence ordering of Q0D and Q0C.** The proposal moves Q0D before Q0C. The original v2 had them as a synthesis pair at the end. Confirm or specify a different placement.

7. **Q6 LAFI counterfactual addition.** Adding the structural counterfactual is methodologically heavier than the current lineup-level RAPM substitution. Confirm this addition is worth the additional complexity.

---

## Summary of proposed changes by spec, at a glance

| Spec | Proposed change magnitude | Primary motivation |
|---|---|---|
| Q5 Prescription | **Significant** (30%) | First-principles framing required; three-paths structure replaces archetype-comp template |
| Q7 Star Comp | **Position only** | Moves up to immediately before Q5; content largely preserved |
| Q0C Cohort | **Significant** (25%) | LAFI components added as cohort features; comp matching prioritizes architecture similarity |
| Q3 Mechanism | **Significant scope reduction** (-20% net) | Q3a reduced to LAFI integration; Q3b PnR coverage becomes the main analysis |
| Q0B Trajectory | **Moderate** (15%) | Edwards trajectory elevated to central diagnostic |
| Q0D Coaching | **Minor** (10%) | Allocation problem integration; 2023-24 baseline empirically validated |
| Q4 Archetype Stress | **Moderate** (20%) | LAFI quadrant framework added as clustering approach; Q4 prevalence question added |
| Q6 KAT Counterfactual | **Significant addition** (15% added) | Structural LAFI counterfactual added alongside lineup-level RAPM |
| Q1 Diagnose the Break | **Minor** (5%) | Cross-references to LAFI added; structure unchanged |
| Q2 Localize the Damage | **Minor** (10%) | Iso-by-lineup tracking added; Gobert-vs-Naz reframed via Category B |
| Master plan v2 | **Moderate** | Build sequence reordered; Q7 promoted; Q3 narrowed; action classifier flagged for own spec |
| **New: Action Classifier** | **New spec** | Currently embedded in Q3; recommend extracting |
| **New: Q0B Edwards expansion** (or Q8) | **New sub-section or spec** | Edwards trajectory is now Plan A's pivotal variable |

The replan is substantial but contained. No spec gets thrown out. The project's overall shape is preserved; what changes is which question each spec answers, in what order, and against what evidence base.
</thinking>

The proposal document is written. Saved at `outputs/findings/q0a_lafi/12_post_lafi_replan_proposal.md`.

## What the proposal covers

The document is structured in six parts that walk through everything you asked for, plus the gaps and decision points needed before the next session executes.

**Part 1: The four user-named spec revisions.** Concrete edits with section references for each of Q5, Q7, Q0C, Q3. Estimated rewriting magnitudes (Q5 ~30%, Q0C ~25%, Q3 ~20% net reduction, Q7 position-only with minor sentence edits).

**Part 2: Other specs needing adjustment** (the ones you asked me to check):
- **Q0B (moderate revision):** elevate Edwards trajectory from one of six diagnostic questions to **the** central question, because Path 1 in the LAFI deliverable depends on his developmental ceiling.
- **Q0D (minor revision):** integrate the allocation problem finding; the 2023-24 baseline is now empirically validated as the most-designed version.
- **Q1 (minor):** cross-reference LAFI C5 for shot quality side rather than re-derive. Four-factors and halfcourt vs transition splits are LAFI-orthogonal and stay.
- **Q2 (minor):** add iso-by-lineup tracking; reframe Gobert vs Naz at the 5 through the Category B finding (Naz at 38.1% catch-and-shoot is a structural Category B asset).
- **Q4 (moderate):** add LAFI components as clustering features; add quadrant-based clustering as a second approach; add Q4-prevalence-over-time as a specific question.
- **Q6 (significant addition):** add a structural LAFI counterfactual ("would the Wolves have stayed Q1 with KAT?") alongside the existing lineup-level RAPM substitution.

**Part 3: Revised build sequence.** Q7 promoted to immediately before Q5 (per your direction). Q3 narrowed and pushed down. Q0D moves up to where the allocation problem finding is still fresh. Q5 stays last but with the substantial rewrite happening before the build, not after.

**Part 4: Gaps the current spec set doesn't cover.** Two candidate new artifacts:
1. **Action Classifier as its own spec.** Currently embedded in Q3. With Q3 narrowed, the classifier's only remaining justification is PnR coverage. Treating it as its own spec makes scope visible and lets Q3 start with manual-coding fallback if the classifier slips. **Decision needed: own spec or in-line.**
2. **Edwards Trajectory Deep Dive.** Plan A in the front-office takeaways hinges on Edwards reaching Luka/SGA tier. No spec owns this question formally. **Decision needed: expand Q0B Section 4.1 or create a new Q8.**

Plus one in-place addition: an Allocation Restoration Impact sub-section in Q0D (no new spec, just an extension of an existing one).

**Part 5: What does NOT need to change.** The project principles, success criteria, out-of-scope items, Q1's four-factors framework, Q2's lineup heatmap approach, and Q7's methodology. All vindicated by the LAFI process.

**Part 6: Seven decision points** you need to resolve before the next session executes:
1. Q5 portfolio framing (three-LAFI-paths replacing or complementing the original three portfolios)
2. Q0C cohort weighting (LAFI similarity at 15%, roster construction at 20%)
3. Action classifier as standalone spec or in-line in Q3
4. Edwards trajectory: expand Q0B or create new Q8
5. LAFI v2: defer indefinitely or schedule after Q5
6. Q0D before or after Q0C in the build sequence
7. Q6 LAFI counterfactual addition: worth the additional complexity

## Summary table at the end

| Spec | Change magnitude | Primary motivation |
|---|---|---|
| Q5 | Significant (30%) | First-principles framing replaces archetype-comp template |
| Q7 | Position only | Promoted to immediately before Q5 |
| Q0C | Significant (25%) | LAFI components as cohort features |
| Q3 | Significant scope reduction (-20% net) | Q3a reduced to LAFI integration |
| Q0B | Moderate (15%) | Edwards trajectory elevated |
| Q0D | Minor (10%) | Allocation problem integration |
| Q4 | Moderate (20%) | LAFI quadrant framework added |
| Q6 | Significant addition (+15%) | Structural LAFI counterfactual |
| Q1 | Minor (5%) | Cross-references to LAFI |
| Q2 | Minor (10%) | Iso-by-lineup tracking |
| Master plan | Moderate | Build sequence reordered |
| New: Action Classifier spec | New | Extract from Q3 |
| New: Edwards trajectory expansion or Q8 | New (sub-section or spec) | Plan A's pivotal variable |

No spec gets thrown out. The project's overall shape is preserved; what changes is which question each spec answers, in what order, and against what evidence base.

## What I deliberately did not do

- I did not make any spec edits. The proposal is proposal-only per your instruction.
- I did not start a new analytical build. The next session executes the agreed changes.
- I did not mark any new tasks as in_progress, since this was a re-planning session and the post-replan work belongs to the next session.

When you've reviewed the proposal and resolved the seven decision points, the next session can execute the edits across the master plan and the affected specs cleanly. Take your time with it; the replan matters more than any single build.