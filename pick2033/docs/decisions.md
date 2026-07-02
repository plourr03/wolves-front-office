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
