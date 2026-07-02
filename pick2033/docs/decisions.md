# Decision record — pick2033

## 2026-07-01 — Gate ruling: 8.1 skill (h=7)

**GATE RULING (8.1 skill, h=7): Option 1.** Accept Model A v2 (mixture) with
the red gate documented; memo attached to validation_report.md unedited.
Conditions (Bobby, verbatim):

1. Add S7 tornado arm: pooled-dynamics variant (tau -> 0, fit once, not
   tuned) through Engine D, to quantify whether the hierarchical-mean
   choice moves the 2033 posterior and swap prices at all. This converts
   the model-selection question into a measured downstream sensitivity.
2. Stage 2 methodology notes disclose the red gate in one plain sentence
   with the tie statistics. Not buried.
3. If gate 8.4 (tail realism) fails at M4, fallback is v1, not a re-tuned
   v2 -- 8.1's test set stays sealed.
4. Log the gate-design lesson: long-horizon point-skill gates vs
   near-climatological baselines are close to unwinnable by construction;
   future spec versions gate long horizons on calibration and tails only.

**Rationale (Bobby):** the skill gate exists to catch a model worse than
trivial alternatives. This one beats persistence 2x everywhere and ties
pooled reversion at the gate horizon while delivering calibrated
per-franchise intervals (gated, passing), a fat-tail shock regime (gated at
8.4), and the per-franchise means the pre-registered CHA-lineage tornado arm
exists to interrogate. No post-hoc threshold revision (option 2 off the
table); deleting the franchise-mean layer (option 3) would delete a committed
sensitivity analysis to fix a deficit measured in thousandths. The gate was
slightly misdesigned (Bobby's own design): at h=7 pooled reversion is near
climatology, which is near the information limit for NBA team strength --
demanding strictly better point skill there was near-unwinnable by
construction, at a horizon where the deliverable needs calibration, tails,
and structure, not point skill.

**Finding pulled forward to Stage 2 (a discovery, not an appendix defect):**
tau = 0.78 with franchise long-run means spanning less than ±1 SRS point
across 46 seasons: long-run "franchise DNA" is worth under one point per 100
possessions. The red gate is part of that story: we looked for persistent
franchise quality and found barely any, which is exactly why the model
cannot beat pooled reversion on points.

**Model C:** signed off clean. The imputed-scale fix is proper
heteroskedastic treatment (imputations are a different measurement process),
not a workaround.

## 2026-07-01 — Gate ruling: 8.4 tail-realism operationalization (RATIFIED with amendments)

**GATE RULING (8.4 tail-realism operationalization): RATIFIED with amendments.**
(Bobby, verbatim:)
1. Gate BOTH tails at terminal horizon (2033) within the spec's original
   +/-25% band vs the historical unconditional rate. Band unchanged.
2. Transient check: per-year tail-rate excess non-increasing across
   2027-2033, with tolerance = 2x Monte Carlo SE per year (strict
   monotonicity not required; inversions within noise pass).
3. Historical base rates MUST be computed on win-percentage thresholds
   (>= .732 top tail, <= .244 bottom), so the four shortened seasons
   (1999/2012/2020/2021) enter at pace. If the preview used raw win
   counts, recompute before judging anything.
4. Pooled-over-horizons rates: reported, un-gated, with the conditioning
   explanation attached.
5. Pre-committed lag-3 fallback: if autocorrelation fails the envelope at
   M4, the designated response is the spec's covariate-effects variant
   (core age, continuity, star loss on the innovation mean), fit ONCE:
   must pass 8.1 health/coverage/dispersion, not degrade CRPS beyond v2's
   documented margin, and clear 8.4. One shot, no sweep; 8.1's test set
   stays sealed. v1 fallback is closed (shown identical on tails).
6. Disclosure: preview-informed timing of this operationalization noted
   in the validation report.

**A priori justification (the record):** with phi = 0.684, the 2033 marginal
retains ~7% of the initial condition (0.684^7) -- effectively stationary, the
only place an unconditional base rate is a valid reference. Gating the pooled
rate conflated a correct conditional transient with a stationarity claim.
Mirror image of the 8.1 lesson: that gate demanded conditional skill where
only climatology exists; this one demanded climatology where conditional
structure exists. Same design error, opposite direction.

**Honesty note (goes in the validation report):** this operationalization was
chosen after a correlated preview, not before any data. Disclosed; acceptable
because the justification stands on first principles regardless of what the
preview showed, but weaker than true pre-registration.

**Amendment 3 verification (same day):** the preview already computed base
rates on win_pct * 82 (pace-normalized, thresholds .7317/.2439); shortened
seasons entered at pace. The pooled excess does not dissolve -- it is the
conditioning transient.

**Lag-3 direction note (for Stage 2 notes at M4):** over-persistence is
conveniently conservative for the deliverable -- it holds Minnesota's current
strength too long, producing fewer bad-Wolves worlds in the swap years and a
thinner 2033 tail, biasing asset cost DOWNWARD against the editorial thesis.
If the priced trade still comes out expensive under a model slightly too kind
to Minnesota's future, the finding is robust.

## 2026-07-02 — Morning rulings (verbatim)

RULING A (Model B calibration, 8.2 slope): Option 3.
1. Declared now, blind to backfilled data: M2 refit uses
   contract_years_remaining backfill (missingness flag per spec 6.2)
   PLUS coefficient priors Normal(0, 0.5) on standardized covariates.
   One final pre-declared spec.
2. M2 refit re-gates ALL of 8.2 on the same sealed holdout. Second and
   FINAL look: pass, or the red cell stands documented with the
   bootstrap CI. No third fit.
3. Bundled-change attribution ambiguity accepted; deliverable is a
   calibrated model, not cause isolation.
4. Slope reported with bootstrap CI either way; 46 events is thin and
   the report says so.

RULING B (Engine D transient, 8.4): Option 1, amended symmetrically.
1. New check: |tail_rate_t - tail_rate_2033| non-increasing 2027-2033,
   tolerance 2x MC SE per year. Variant-blind; re-judge BOTH variants
   and report both.
2. Required before Stage 2: decompose the mid-horizon dip by computing
   the top-tail rate among the 28 prior-chain teams only. Flat at
   stationary = mechanism confirmed; dips too = escalate to option 3
   investigation.
3. Disclosure in validation report: check re-expressed after a failing
   run exposed a directional assumption; fade-not-diverge rationale
   predates the run; weaker than pre-registration, stated as such.
4. House-standards entry (third gate-wording defect, same author):
   convergence checks reference the model's own terminal/stationary
   state, symmetric in approach direction; unconditional historical
   references belong in terminal gates only.

CARRY-FORWARD:
- 0.846 stays quarantined to provisional-tagged artifacts. It appears
  in no draft, export, or note.
- Logged prediction, before the M2 refit runs: the final 2033 posterior
  should come out lighter-tailed than provisional, because the missing
  contract covariate currently inflates departure worlds. Post-refit
  shift is then read as predicted, not tuned.

Context notes from the ruling: all three Engine D fixes assessed correct
(prior-chain separation = correct spec 7.4 reading; shared
rotation_aggregate = train/serve alignment; shrink-to-replacement = right
prior for fringe players). Two earlier flags resolved against Bobby's
recall and are so recorded: Bosh 2016 was 53 games / 1,778 minutes
(legitimate spell), and Robertson was a covariate bug, not a name-join miss.

## 2026-07-02 (afternoon) — Rulings C and D + backfill directive (verbatim)

RULING C (Engine D transient cell): Accept RED, documented, final.
Crossing mechanism confirmed (0.996 suppression correlation, clean
pure_a field). No further check rewording; agent's stop was correct.

RULING D (CHA crest validation): Run the young-core cohort analysis
as Stage-2 prep, framed as validating a swap-pricing input.
1. Cohort: 1985-2019 team-seasons, win_pct < .500, 3+ players under 23
   with 1000+ minutes. Report the 5-year win-trajectory fan,
   unconditional AND matched on starting band (.400-.500).
2. Pre-committed decision rule, declared before results: if the model's
   CHA median crest exceeds the matched cohort's 70th-percentile
   trajectory, apply a cohort-calibrated young-roster blend adjustment
   (fit to the cohort median, chosen blind to its effect on swap
   prices), then re-run Engine D and all 8.4 gates once. Otherwise the
   crest stands, documented.
3. Log prediction P2 in predictions.md now: the matched cohort median
   crests BELOW the model's CHA crest (no-churn/no-bust reasoning).
   Direction reduces swap values, i.e. against the editorial thesis.
   Grade it when the cohort lands.

CONTRACT BACKFILL DIRECTIVE (before the one-shot M2 refit):
1. Re-derive the Duncan-pattern bias direction with a synthetic test:
   simulate spells with a known contract coefficient, inject the
   smooth-re-sign mislabeling, refit, observe the bias. Bobby's
   hypothesis: the memo has it backwards -- the error deletes true
   walk-year person-time from NON-events (stayers), inflating observed
   hazard at years=0 and EXAGGERATING the coefficient. Settle
   empirically; the answer goes in the record either way.
2. Add a salary-discontinuity re-sign detector (new-deal signatures:
   level jumps, raise-structure breaks) plus a targeted manual pass on
   residual smooth cases among long-tenure stars. Those rows ARE the
   Edwards reference class. Covariate construction, upstream of the
   sealed holdout, blind to fit outcomes: allowed under Ruling A and
   required by it in spirit.
3. If ambiguous cases remain, one pre-declared sensitivity arm
   (perturb affected rows' years_remaining), not a second fit.

Framing note (Bobby): the crest investigation is NOT gate rescue -- it
validates a load-bearing pricing input whose error direction FAVORS the
editorial thesis (crest years 2028-2030 are the swap years). The lag-3
finding biased against the thesis; this one biases toward it, which is
exactly when the house standard says validate rather than accept.

## 2026-07-02 — Rulings C and D executed
C: transient cell accepted RED, final; memo closed with mechanism attached.
D: cohort ran (77 entries / 18 matched). Decision rule NOT triggered:
model CHA crest 50.8 < matched p70 peak 52.8 (model sits ~p60 of history).
Crest STANDS, documented. P2 graded CONFIRMED on direction (cohort median
49.4 < model 50.8) with a 1.4-win magnitude — the honest read is that the
model is mildly, not materially, generous to Charlotte.
Backfill directive executed: synthetic test SETTLED the bias direction
(EXAGGERATES, ~2.6x on the slope; Bobby right, memo wrong — corrected on
the record); re-sign detector added (rookie-exempt + tight pass; all five
ground-truth careers read correctly); 21 residual segments routed to the
pre-declared S-CONTRACT sensitivity arm, no hand edits.

## 2026-07-02 — Sequencing amendment (verbatim) + borderline resolution

SEQUENCING AMENDMENT (Ruling A timing, declared before the refit runs):
The one-shot M2 refit executes on the complete post-July-6 freeze, not
before. Rationale: the July 6 pass adds three known departure events
(Giannis/Kawhi/LaMelo) currently coded censored; refitting first means
either a final model with knowingly wrong labels or a forbidden third
fit against the sealed holdout. One fit, complete data.

July 6 run order (one mechanical day):
1. Trade-terms verification -> trade_terms.yaml, verified_post_july6=true
2. Spells import: borderline calls + SET verdicts + three exit updates;
   FINAL freeze. Disclose whether any of the three touched the sealed
   holdout (label correction, not peeking).
3. One-shot M2 refit + full 8.2 re-gate; grade P1.
4. Final Engine D re-run on the final hazard; re-judge 8.4.
5. Priced E2 runs unlock; Stage 1 finalizes same day.
6. Stage 2 notes additions: the young-core emergent validation (model
   crest at ~cohort 60th percentile; matched historical cores also
   crest at year +4 then fade; n=18 band caveat) and the corrected
   Duncan-bias record with the synthetic numbers.

Stage 1 DRAFTING from provisional continues now; publication waits.

BORDERLINE RESOLUTION: Bobby's leans on all 21, agent reviewed and
accepted without exception (internally consistent under
recognition-or-primacy-during-spell; aggregate stakes pre-measured at
~0.5% on the Edwards curve).
PRUNE (13): Michael Adams, Batum, Calderon, Darrell Armstrong, Brent
Barry x2, Ryan Anderson, Nene, Gallinari x2, Lou Williams, Lowry-HOU,
Robert Williams. KEEP (8): Dana Barros, Tyreke Evans, Kevin Martin,
Kenny Anderson x2, Derek Harper, Kukoc, Whiteside.

P2 self-grade nuance (Bobby, on record): the no-churn optimism was real
but ALREADY PRICED -- at the 2029 crest, 35% of CHA's simulated strength
is franchise-prior reversion pulling the roster arc down. The genuinely
valuable finding is emergent: the engine reproduced the historical
crest-at-year-4-then-fade arc without being fit to it.

## 2026-07-02 (evening) — verification closures + LaMelo contract directive

DATE CLOSED: June 25 confirmed against public reporting (Charania broke the
agreement in principle the morning of Thursday June 25; ESPN corroborates).
"The trade call came on June 25" stands as written.

LAMELO CONTRACT (bonus catch from verification): three years left
(2/1/0, walk year 2029 -- the SAME summer as Edwards), extension-eligible
July 6 for 2yr/$119.2M. Directives:
1. Model: MIN-side star stability in the swap window depends on BOTH
   clocks. LaMelo's contract path enters the sim config.
2. July 6: check the news BEFORE the final Engine D run; set LaMelo's
   path per what is signed/unsigned that morning; if unresolved, run the
   pre-declared both-ways sensitivity (3-remaining walk-2029 vs extended
   through 2031), never pick silently.
3. Editorial: the shared-2029-walk-year line is PARKED out of Part 1
   (belongs to Parts 2/3; may dissolve by publication morning).
   Verified: Part 1 v2 contains no LaMelo contract content.

DISCLOSURE ADDITION: re-gate event count reported alongside spell count.
Verified: all three pruned holdout members are departure exits; events
46 -> 43 (rows 235 -> 231). Wired into the --final freeze output.

RELEASE GATE (spec Section 12, survives "markup-free"): when slots fill on
July 6, one full read with real numbers in place before shipping,
especially the cumulative-probability sentence.

DRAFTING DIRECTIVE received: Part 2 drafted now slot-based (beat sheet in
directive), Part 3 skeleton only (encumbrance reveal in conditional
language), viz/tornado/replay code built provisional-safe now. Cadence:
Part 1 July 6, Part 2 ~July 8-9, Part 3 mid-July. Companion carousel:
NOT directed (question open with Bobby).

## 2026-07-02 — Part 2 markup + p70 re-arm + Part 3 approval

STAGE 2 MARKUP applied (v1 -> v2), all four items. The validation-logic
item is wired, not just written: the cohort script now live-reads the CHA
crest from the NEWEST Engine D artifact (FINAL preferred over PROVISIONAL),
so the pre-committed p70 rule re-arms automatically against the run that
ships; if the final crest crosses p70 the cohort-calibrated adjustment
fires as originally declared. Engine D runner and JSON exports now carry
FINAL/PROVISIONAL tags end to end. Quarantine boundary clarified on the
record: the provisional P(top-4)/P(top-10) may be quoted inside the P1
grading section ONLY, labeled as the known-flawed pre-contract-fix
artifact being graded; the provisional hazard figure appears nowhere.

PART 3 SKELETON: approved as structure. Replay realized outcomes
independently verified by Bobby (2014: 17th, 2016: 3rd, 2017 swap: No. 1,
2018: 8th). Beat 5 amended: the three second-rounders join the bill
decomposition so every asset appears in the total exactly once.

CAROUSEL: recommended YES (Part 1 companion, built after July-6 numbers
land; hazard curve is the most carousel-able chart of the project).
Final editorial call remains open; nothing blocks on it.
