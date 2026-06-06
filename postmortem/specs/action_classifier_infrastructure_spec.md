# Action Classifier Infrastructure Specification

**Project:** Timberwolves 2025-26 Postmortem
**Spec ID:** Action Classifier (infrastructure)
**Status:** Standalone spec, pre-build. Extracted from Q3 and LAFI v2 during the post-LAFI replan.
**Position in stack:** Shared infrastructure. Consumed by Q3 (PnR coverage decoder) and optionally by LAFI v2 (Component 4 high-fidelity).

---

## 1. Why a standalone spec

In the original master plan, the action classifier was implicitly bundled inside Q3 and LAFI v2. The post-LAFI replan extracted it for three reasons:

1. **Scope visibility.** The action classifier is a multi-week build with its own design choices, validation methodology, and accuracy tradeoffs. Embedding it inside an analytical spec obscures these decisions and makes deferral or simplification harder to reason about.
2. **Deferral discipline.** With Q3 narrowed (Q3a now just integrates LAFI C5) and LAFI v2 deferred indefinitely, the action classifier's only mandatory downstream consumer is Q3's PnR coverage decoder. Treating it as a standalone spec lets the project defer the classifier without blocking Q3, because Q3 has a documented manual-coding fallback.
3. **Reusability.** The classifier output (per-PnR coverage labels) is reusable across multiple analyses. Documenting it as a standalone infrastructure piece makes that reusability explicit.

## 2. What the classifier does

For every pick-and-roll possession in the warehouse, output a labeled record:

- `game_id`, `play_id`, `period`, `clock_remaining`
- `ball_handler_id`, `screener_id`, `defender_on_handler_id`, `defender_on_screener_id`
- `screen_location` (left, right, middle; above the break, in the paint; angle)
- `coverage_label`: one of the seven coverage types in Section 3
- `confidence_score`: 0 to 1, how confident the classifier is in the label
- `possession_outcome`: PPP for the possession that contained this action
- `coverage_resolution`: did the action resolve before any subsequent action (single-action possession) or did the offense run another action after (multi-action)

## 3. The coverage taxonomy

Seven coverage types, each with an explicit definition. These match the Q3 spec Section 4.1 taxonomy.

1. **Drop:** Screener defender drops below the screen, staying in or near the paint. Ball-handler defender stays attached. The ball-handler can see the floor; the screener defender protects the rim. Concedes mid-range and three; protects rim.
2. **Soft hedge / show:** Screener defender briefly steps up to slow the ball-handler, then recovers to the screener. Less aggressive than blitz.
3. **Hard hedge:** Screener defender aggressively steps out to wall off the ball-handler, often higher and longer than a soft hedge.
4. **Blitz / trap:** Two defenders converge on the ball-handler within roughly 1 second of the screen, forcing a pass.
5. **Switch:** The defender on the screener picks up the ball-handler post-screen; the defender on the handler picks up the screener.
6. **Ice / weak (against side PnR):** Defender on handler forces the ball-handler away from the screen, typically toward the sideline or baseline.
7. **Top-lock / under:** Defender on handler goes under the screen, daring the ball-handler to shoot, or top-locks the screener to deny the screen.

Edge cases:

- Late switch: the screen is defended initially as drop or hedge, then the defenders switch later in the possession. Should be classified by primary coverage at the screen action, with a sub-flag for "late switch."
- Failed coverage: the intended coverage broke down. Classify by intent (what the defenders were trying to do) and flag separately as a failed execution.
- Empty side / weakside considerations: tagging recommended but not blocking.

## 4. Classification methodology

Two complementary approaches. The standalone spec accommodates both.

### 4.1 Automated classifier (the primary build target)

Heuristics derived from PBP plus tracking data:

- **Drop:** screener defender's position remains within roughly 8 feet of the rim throughout the screen, and ball-handler defender remains within 4 feet of the ball-handler.
- **Switch:** screener defender's position trajectory post-screen tracks the ball-handler's position; ball-handler defender's position tracks the screener.
- **Blitz/trap:** two defenders within 6 feet of the ball-handler within 1 second of the screen.
- **Hedge:** screener defender steps above the screen briefly (less than 2 seconds, distance from rim greater than 12 feet) then recovers to the screener.
- **Ice:** ball-handler's path deviates away from the screener by more than ~10 degrees from the expected path under a normal coverage.
- **Top-lock / under:** ball-handler defender's position is between the ball-handler and the screen at the moment of the screen attempt.

These heuristics produce a confidence score per coverage type. Output the highest-confidence label with a confidence value.

### 4.2 Manual coding (the fallback)

For validation and for the Q3 fallback path:

- Pull video for the 2025-26 Wolves playoff possessions (estimated ~600 PnR possessions across 11 games).
- Manual code each PnR with one of the seven labels.
- Cost: roughly 20-30 hours of careful coding. Doable for Q3's headline analysis (the Spurs series specifically).
- Manual codes also serve as the validation set for the automated classifier (Section 5).

### 4.3 Hybrid approach (recommended for Q3 v1)

If the automated classifier is built but its accuracy on the validation set is borderline (e.g., 75-85% on the most diagnostic coverages), use a hybrid:

- Automated labels with confidence > 0.7 are accepted.
- Automated labels with confidence < 0.7 are manually reviewed.
- Automated labels with confidence between 0.7 and the threshold get spot-checked.

This balances scale (automated handles the bulk) with accuracy (manual catches the edge cases).

## 5. Validation methodology

The classifier's accuracy must be measured against ground truth. The validation set is the manually coded Wolves playoff sample (Section 4.2).

For each coverage type, compute:

- **Precision:** of the possessions the classifier labeled as this coverage, what fraction actually were this coverage?
- **Recall:** of the possessions that actually were this coverage, what fraction did the classifier catch?
- **F1 score:** harmonic mean of precision and recall.

Report all three per coverage type. Confusion matrix (predicted x actual) for the full classifier.

Accuracy targets (these are targets, not gates; below the target means the finding is presented with explicit accuracy caveats):

- Drop: F1 >= 0.85 (most common coverage, should be cleanest)
- Switch: F1 >= 0.80 (clear positional signature)
- Blitz/trap: F1 >= 0.80 (clear two-defender signature)
- Hedge: F1 >= 0.70 (soft vs hard distinction is hard)
- Ice: F1 >= 0.70
- Top-lock/under: F1 >= 0.65 (rare and ambiguous)
- Overall macro-F1 >= 0.78

## 6. Output schema

```sql
CREATE TABLE nba.action_classifier_output (
    game_id              VARCHAR(20),
    play_id              INTEGER,
    period               SMALLINT,
    clock_remaining_sec  NUMERIC(5,2),
    ball_handler_id      INTEGER,
    screener_id          INTEGER,
    defender_on_handler  INTEGER,
    defender_on_screener INTEGER,
    screen_location      VARCHAR(20),
    coverage_label       VARCHAR(20),
    confidence_score     NUMERIC(4,3),
    possession_ppp       NUMERIC(5,3),
    is_multi_action      BOOLEAN,
    classifier_version   VARCHAR(20),
    classified_at        TIMESTAMP,
    PRIMARY KEY (game_id, play_id)
);
```

Tables are loaded into the production warehouse so any downstream analysis can join on `game_id` and `play_id`.

## 7. Sequencing and consumers

**Build sequence:** The classifier can run any time after the lineup-level possession pipeline is built (because the PnR identification needs possession boundaries). It is not on the critical path for Q1, Q2, Q4, Q5, Q6, Q7, Q0B, Q0C, Q0D.

**Critical consumer:** Q3 PnR coverage decoder (Q3b for offense, Q3c for defense). Without the classifier, Q3 falls back to manual coding for the 2025-26 playoff sample only.

**Optional consumer:** LAFI v2 Action Poverty Component 4 high-fidelity rebuild. Currently deferred (per master plan v3 Section 6.4).

**Estimated build time:** 2-3 weeks for v1. Validation pass adds another 3-5 days. Total roughly 3 weeks.

## 8. Deferral logic

The classifier can be deferred without blocking the project. Specifically:

- Q3 runs with manual coding for the 2025-26 playoff sample (Wolves only, ~600 possessions).
- The findings hold for the playoff series specifically; league-wide generalizations are weakened.
- The Q3 deliverable explicitly notes which findings are playoff-sample-only and which are league-wide.

The classifier becomes mandatory if:

- Q3 produces a finding that requires league-wide validation (e.g., "Wolves see more blitzes than typical playoff teams" needs a league-wide blitz frequency baseline).
- LAFI v2 is re-triggered per the master plan.
- A future analysis needs PnR-level data at scale.

## 9. What I'm worried about

**Classifier accuracy on the most diagnostic coverages.** "Soft hedge vs show vs drop with high pickup" can blur. The taxonomy itself may need refinement during the build.

**Tracking data completeness.** Some games or quarters have incomplete tracking data. The classifier should handle this gracefully (return null + reason rather than guessing).

**Coverage taxonomy may be too rigid.** Real-world coverage choices are often hybrid (drop on the ball, switch on the off-ball action). The taxonomy may need a "primary + secondary" structure rather than a single label.

**Sample biases.** Most NBA PnRs are drops. Less common coverages (top-lock, ice) have small training samples and harder classification. The accuracy targets reflect this.

## 10. Success criteria

**Minimum viable:** A documented classifier that handles drop, switch, and blitz/trap with F1 >= 0.75 each, validated against the manually coded Wolves playoff sample.

**Strong:** All seven coverage types meet their per-target F1 thresholds. The classifier scales to the full league for 2025-26 RS and PO.

**Stretch:** The classifier is validated on multiple seasons (2023-24 through 2025-26) and unlocks LAFI v2 Component 4 high-fidelity rebuild.

---

End of specification.
