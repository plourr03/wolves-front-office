# Pre-committed predictions log (graded later; never edited after the fact)

## P1 — 2026-07-02, logged BEFORE the M2 contract-backfill refit runs
**Prediction (Bobby, morning rulings):** the final 2033 posterior comes out
LIGHTER-TAILED than the provisional one, because the missing contract
covariate currently inflates departure worlds (the provisional hazard cannot
see that a signed rookie-max year suppresses departure, so simulated
Edwards/LaMelo exits are too frequent, MIN collapse worlds are
over-produced, and the provisional pick posterior is too heavy at the top).
**Grading:** compare slot_distribution_2033 P(top4)/P(top10) provisional
(.167/.422, run seed 20330706) vs post-M2-refit run. Direction called in
advance; a post-refit lightening is read as predicted, not tuned.

### P1 GRADED (2026-07-12, post-M2-refit FINAL run): CONFIRMED in both cells
Final slot_distribution_2033 (FINAL freeze 50f9b7bc5b19835b, M2 posterior,
seed 20330706): P(top4) .157 vs provisional .167; P(top10) .391 vs
provisional .422. Lighter-tailed in both pre-declared cells — direction
called in advance, read as predicted, not tuned. Mechanism matches the
stated reasoning: the backfilled contract covariate is strongly protective
(b_contract_z -2.940), so signed years suppress simulated departures and
fewer MIN-collapse worlds reach the top of the 2033 draft. Magnitude:
-1.0 point top-4 (6% relative), -3.1 points top-10 (7% relative).
Caveat carried with the grade: the M2 calibration slope re-gate stayed red
(1.413, boot 90% CI [1.127, 1.872] vs [0.8, 1.2]) — final look, stands
documented per Ruling A; see outputs/validation/model_b_hazard_M2_FINAL.md.

### P1 BASELINE PIN-NOTE (2026-07-13 addendum; the logged prediction above is untouched)
Two committed pre-M2 provisional runs existed for the P1 baseline: the
04:02 UTC 2026-07-02 run (commit 8931e70c, .167/.422, the run P1's grading
clause quotes) and the 18:16 UTC run (commit dbb3657b, post-pick_ledger,
.170/.421). Bobby's ruling (2026-07-13, verbatim "A"): grade as-logged.
The baseline is PINNED to the 04:02 artifact, commit 8931e70c. The 18:16
run stands on the record as a later, ledger-resolved provisional, not the
grading baseline. Shift between them: +0.003 p_top4 (~1.8 SE), within
noise; the grade's direction is identical under either. Memo:
outputs/validation/p1_baseline_decision.md.

## P2 — 2026-07-02, logged BEFORE the young-core cohort analysis runs
**Prediction (Bobby, Ruling D):** the matched cohort's median trajectory
crests BELOW the model's CHA median crest (~51 wins at 2029). Reasoning:
the roster tier for a young core can only add (everyone rides the aging
curve up; nobody busts, gets traded, or loses minutes to teammates'
improvement); historical young cores that hit 51 wins are the memorable
survivors, and the cohort includes the plateaus.
**Direction:** if confirmed, correcting it REDUCES swap values — against
the editorial thesis.
**Grading:** compare the model CHA median trajectory (45.0/49.8/50.8/49.2/
46.9 wins, 2027-2031, run seed 20330706) against the matched-band cohort
median when the cohort analysis lands.

### P2 GRADED (2026-07-02, same day): CONFIRMED on direction, near-push on magnitude
Matched cohort median crest 49.4 wins < model CHA crest 50.8 — Bobby's
direction was right, by 1.4 wins. The model's crest sits at ~p60 of the
matched cohort (p50 49.4, p70 52.8), i.e. mildly generous, not
survivor-biased fantasy. Decision rule NOT triggered (model peak 50.8 <
matched p70 peak 52.8): per the pre-committed rule the crest STANDS,
documented, no adjustment, no re-run. Note the shape agreement: the cohort
median also crests then fades (peak year +4, decline by +5), matching the
model's crest-then-fade. The no-churn/no-bust concern and the real-ascent
upside roughly offset in this band. Full fans:
outputs/validation/young_core_cohort.json.
