# pick2033 validation report (auto-generated)
generated 2026-07-02T18:29:24.233341+00:00 @ 3284daf3

**Standing caveats:** Model B and all Engine D outputs are PROVISIONAL (borderline spells kept pending Bobby's final call; contract covariate omitted pending M2 backfill; July-6 exit updates pending). Swap PRICING is hard-gated on trade-terms verification (verified_post_july6: false). The 8.4 operationalization was chosen after a correlated preview, justified a priori; weaker than true pre-registration and disclosed.

**Gate ruling log:** docs/decisions.md (8.1 accepted-with-red-gate; 8.4 operationalization ratified with amendments; Model B calibration parked).

**Counting convention:** season counts are INCLUSIVE (the panel is 1980-2026 = 47 season-years, 1,314 franchise-season rows). Older memos saying '46 years' used span counting and stand under this note (declared 2026-07-02).


---
## M0 cross-checks

# M0 cross-check: B-Ref SRS vs warehouse point differential
- overlap rows matched: 863 of 863 B-Ref franchise-seasons (1998+)
- corr(SRS, avg point diff), all seasons: **0.9969** (gate: > 0.98)
- by half-decade: 1995: 0.995, 2000: 0.994, 2005: 0.998, 2010: 0.996, 2015: 0.998, 2020: 0.998, 2025: 0.999
- largest gaps (SRS vs diff, SOS effects expected): UTA 1999 0.98; LAL 2014 0.96; BOS 2008 0.96; SAS 1999 0.94; GSW 2001 0.94

**GATE PASS**

---
## Gates 8.1 — Model A (trajectory)

# Model A rolling-origin backtests (gates 8.1)
origins 1995-2019, horizons 1-7, 5153 scored cells, 4000 paths/forecast

|   horizon |   crps_model |   crps_persistence |   crps_pooled |   coverage_80 |   n |
|----------:|-------------:|-------------------:|--------------:|--------------:|----:|
|         1 |        1.896 |              2.911 |         1.888 |         0.777 | 737 |
|         2 |        2.31  |              3.802 |         2.299 |         0.78  | 736 |
|         3 |        2.522 |              4.5   |         2.5   |         0.769 | 736 |
|         4 |        2.54  |              4.783 |         2.519 |         0.781 | 736 |
|         5 |        2.583 |              5.041 |         2.562 |         0.774 | 736 |
|         6 |        2.594 |              5.041 |         2.58  |         0.777 | 736 |
|         7 |        2.621 |              5.128 |         2.614 |         0.772 | 736 |

- coverage gate (80% PI in [72,88] all horizons): **PASS**
- skill gate at h=7 (model 2.621 < persistence 5.128 and pooled 2.614): **FAIL**
- dispersion gate (sim wins SD 12.78 vs hist 12.86, within 15%): **PASS**
# Model A rolling-origin backtests (gates 8.1)
origins 1995-2019, horizons 1-7, 5153 scored cells, 4000 paths/forecast

|   horizon |   crps_model |   crps_persistence |   crps_pooled |   coverage_80 |   n |
|----------:|-------------:|-------------------:|--------------:|--------------:|----:|
|         1 |        1.897 |              2.911 |         1.888 |         0.775 | 737 |
|         2 |        2.31  |              3.802 |         2.299 |         0.774 | 736 |
|         3 |        2.522 |              4.5   |         2.5   |         0.764 | 736 |
|         4 |        2.542 |              4.783 |         2.519 |         0.776 | 736 |
|         5 |        2.584 |              5.041 |         2.562 |         0.77  | 736 |
|         6 |        2.594 |              5.041 |         2.58  |         0.776 | 736 |
|         7 |        2.623 |              5.128 |         2.614 |         0.772 | 736 |

- coverage gate (80% PI in [72,88] all horizons): **PASS**
- skill gate at h=7 (model 2.623 < persistence 5.128 and pooled 2.614): **FAIL**
- dispersion gate (sim wins SD 12.79 vs hist 12.86, within 15%): **PASS**
# Model A skill gate: FAIL as pre-registered, statistical tie in substance — decision needed

2026-07-01. Gates 8.1 status after the full v1/v2 investigation.

## What passed
| Gate | v1 (Student-t) | v2 (mixture) |
|---|---|---|
| MCMC health (R-hat < 1.01, ESS > 400, no div.) | PASS (1.005 / 1143 / 0) | PASS (1.004 / 1074 / 0) |
| Coverage (80% PI in [72,88], h=1-7) | PASS (77.2-78.1%) | PASS (76.4-77.6%) |
| Dispersion (sim wins SD w/in 15% of hist.) | PASS (12.78 vs 12.86) | PASS (12.79 vs 12.86) |
| Skill (CRPS < both baselines at h=7) | **FAIL** vs pooled | **FAIL** vs pooled |

Both variants beat persistence by ~2x everywhere. The miss is only against the
pooled mean-reversion baseline.

## The miss, quantified
- v1 h=7: model 2.621 vs pooled 2.614 (+0.007, origin-clustered t = 0.57)
- v2 h=7: model 2.623 vs pooled 2.614 (+0.009, t = 0.72)
- h=1-5: deficit +0.008 to +0.022 (0.4-0.9% relative), t = 2-3 (real but tiny)

## Diagnosis (why, not just what)
The spec's pre-registered v2 (two-component mixture innovation) was built and
swept: CRPS is IDENTICAL to v1 within 0.002 at every horizon. The deficit is
therefore NOT innovation shape. What both variants have and pooled lacks is
the hierarchical franchise-mean layer: posterior tau = 0.78 (franchise means
span only ±0.85 SRS), so the mu_i are mostly estimation noise that adds
forecast variance without exploitable signal. Pooled is nested in our model
(tau -> 0); the deficit is the bounded, honestly-priced cost of estimating 30
means that barely differ.

Iteration STOPPED here deliberately: further prior-tuning (e.g. tightening
tau) against the same backtest set would be fitting the gate, not the model
(rigor standard: sealed evaluation, no threshold revision).

## What the mixture bought anyway
v2 posterior: routine years sigma = 2.9; **19% of franchise-seasons are shock
years with sigma = 5.3** (w_routine 0.81 [0.67, 0.93], sigma_shock 5.3
[4.5, 6.4]). This is the explicit structural-shock regime the 2033 pricing
question feeds on, and it is interpretable (a shock probability) where the
t's nu = 11 is not. The 8.4 tail-realism gate at M4 tests it directly.

## Decision needed (blocks Stage 2 publication, not Stage 1)
The gate fails by the letter; by substance the model is tied with pooled at
the gate horizon (t = 0.7) while providing what pooled cannot: per-franchise
long-run means (mu_CHA is load-bearing -- the CHA-lineage tornado arm
interrogates exactly this), calibrated intervals, and a fat-tail regime.

Options:
1. **Accept Model A v2 with the documented miss (recommended).** The gate
   stays red in the report with this analysis attached; the honest reading is
   "7-year point skill beyond pooled reversion is not extractable at this
   resolution; the model's value is calibrated uncertainty + tails +
   franchise structure, each separately gated."
2. Re-specify the skill gate (e.g. "not significantly worse than pooled,
   clustered t < 2, plus coverage pass"). This is a threshold revision and is
   listed only for completeness; your call, not mine.
3. Drop the franchise-mean layer (pooled dynamics for all 30). Erases the
   mu_CHA structure the swap-pricing question needs; not recommended.

Artifacts: backtest_scores_v{1,2}_*.parquet, model_a_backtests_v{1,2}_*.md,
posteriors trajectory_d3799719cc9d10f0 (v1) / trajectory_57cc91bf42fd771d (v2).

---

## RULING (Bobby, 2026-07-01): Option 1 — accepted with conditions

Model A v2 (mixture) accepted; red gate stands documented, memo unedited.
Full ruling text and rationale: docs/decisions.md. Conditions: (1) S7
tornado arm runs a pooled-dynamics variant (tau -> 0, fit once, untuned)
through Engine D; (2) Stage 2 methodology notes disclose the red gate in one
plain sentence with the tie statistics; (3) if gate 8.4 fails at M4 the
fallback is v1, never a re-tuned v2 (8.1's test set stays sealed); (4)
gate-design lesson logged below.

### Gate-design lesson (for future spec versions)
Long-horizon point-skill gates against near-climatological baselines are
close to unwinnable by construction: at h=7, pooled mean-reversion is near
the information limit for NBA team strength. Future specs gate long horizons
on calibration and tails only, and reserve point-skill gates for horizons
where information exists to extract.

### Finding promoted to the Stage 2 piece
tau = 0.78, franchise long-run means spanning under ±1 SRS across 46 years:
long-run franchise identity ("franchise DNA") is worth less than one point
per 100 possessions. The red gate is the same fact seen from the other side.


---
## Gates 8.2 — Model B (hazard) [PROVISIONAL]

# Model B hazard (gates 8.2) -- PROVISIONAL
- freeze 49f2135d534f3ce7; 1290 rows, 238 departures; contract covariate OMITTED (0% coverage); July-6 updates not applied
- train MCMC r_hat 1.0034 ess 1269; full r_hat 1.0024
- C-index (held-out rows): 0.675 (gate >= 0.63) -> **PASS**
- calibration slope: 0.664 (gate [0.8, 1.2]) -> **FAIL**
- Cox sign agreement: PASS {'age_z': (0.3662638866457283, 0.940141499042511), 'yrs_z': (-1.962254648101481e-16, -0.11008197069168091), 'win2_z': (-0.1769523744216352, -0.32242700457572937), 'deep': (-0.3427215956875313, -0.4964357614517212), 'mkt_c': (0.013642719056742001, 0.07910475134849548), 'supermax': (0.2423147651642942, 0.41805529594421387), 'an_z': (-0.09122637450069201, -0.35096755623817444)}
- Edwards cumulative P(departed by 2033), central scenario: 0.846; excluding 21 borderlines: 0.851 (delta +0.005)
# Model B calibration gate: FAIL (parked) — decision memo for Bobby

2026-07-02 overnight run. PROVISIONAL fit (freeze 49f2135d534f3ce7); parked
per the overnight directive, work continued on independent tracks.

## Status of gates 8.2 (provisional fit)
| Gate | Result |
|---|---|
| MCMC health | PASS (r_hat 1.003, ess 1269) |
| C-index >= 0.63 (held-out) | PASS (0.675) |
| Cox sign agreement (all covariates) | PASS (7/7, face-valid directions) |
| Calibration slope in [0.8, 1.2] | **FAIL (0.664)** |

## The miss, quantified
Held-out sample: 235 player-seasons, 46 departure events (spell-level 20%
holdout, sealed seed). Point slope 0.664 (< 1 = predictions too spread /
overconfident). Spell-level cluster bootstrap: mean 0.703, 90% CI
[0.38, 1.04], P(slope >= 0.8) = 0.30. The holdout is underpowered to
establish calibration tightly either way; the lean is real but the gate
verdict rests on 46 events.

## Candidate causes (not adjudicated overnight)
1. **The documented contract-covariate omission.** contract_years_remaining
   has 0% historical coverage at M0 and is omitted. The model cannot separate
   walk-year stars from locked-in stars, so covariate-driven spread that
   should be explained by contract state gets loaded onto other covariates.
   The M2 backfill + refit is already required before Stage 1.
2. Mild overfit: 8 covariates + era effects on 192 training events with
   Normal(0,1) coefficient priors. A single pre-declared shrinkage revision
   (e.g. Normal(0, 0.5)) would pull the slope toward 1.
3. Holdout power (46 events) -- irreducible without changing the split,
   which would unseal it.

## Options for ruling
1. **Park until the M2 contract backfill + final fit, re-gate then
   (recommended).** The provisional fit is non-publishable by directive
   anyway; M2's refit is the natural sealed re-test, and cause 1 is already
   scheduled to be addressed there.
2. One pre-declared shrinkage revision now (mirror of the 8.1 mixture
   precedent): tighter coefficient priors, refit once, re-gate once.
   Costs a second look at the same holdout; only worth it if Engine D
   integration cannot tolerate the current spread.
3. Both (shrinkage priors declared now, applied at the M2 refit).

## Downstream note (Engine D, overnight)
Engine D runs with the provisional-B hazard as directed. Slope < 1 means
simulated departure draws are somewhat too extreme in both directions at the
covariate level; the Edwards-departs scenario mass is the quantity to treat
with widest error bars in provisional outputs. Everything downstream is
tagged PROVISIONAL.

## Edwards provisional read (NOT publishable; contract leverage absent)
Central scenario (team win pct 2yr = .60): cumulative P(departed by 2033)
= 0.846 -- inflated by the missing contract covariate (a signed rookie-max
year suppresses hazard in ways this fit cannot see). Borderline-spell
sensitivity: +0.005 (negligible). Real interpretation waits on the M2 fit.


---
## Gates 8.3 — Model C (aging)

# Model C aging curves (gates 8.3)
- delta rows 14496 (2861 imputed dropout rows), players 2432
- train MCMC: r_hat 1.0050, ess 687; with-imp r_hat 1.0054; no-imp r_hat 1.0055
- held-out RMSE: model 1.799 vs no-aging 1.849 vs league-mean 1.849 -> **PASS**
- survivor-bias audit (max |with - without| past age 30, BPM):
    - big: 0.14 (imputed version authoritative past 30 per spec)
    - guard: 0.08 (imputed version authoritative past 30 per spec)
    - wing: 0.11 (imputed version authoritative past 30 per spec)

---
## Gates 8.4 — Engine D [PROVISIONAL]

# 8.4 preview RE-JUDGED under ratified operationalization (ON-1)
- historical base rates (win-pct thresholds .732/.244): top 0.0594, bottom 0.0632
- disclosure: Operationalization chosen after a correlated preview (2026-07-01), justified a priori (phi^7 ~ 0.07 makes the terminal horizon effectively stationary); weaker than true pre-registration and disclosed as such.

## v2_mixture (accepted)
- terminal (2033): top 0.0679 vs 0.0594, bottom 0.0508 vs 0.0632 -> **PASS**
- transient (non-increasing excess w/in 2x MC SE): **PASS**
- yearly top rates 2027-33: [0.0883, 0.0796, 0.0732, 0.0706, 0.0699, 0.0689, 0.0679]
- pooled (reported, un-gated): top 0.0741, bottom 0.0585

## v1_student_t
- terminal (2033): top 0.0681 vs 0.0594, bottom 0.0505 vs 0.0632 -> **PASS**
- transient (non-increasing excess w/in 2x MC SE): **PASS**
- yearly top rates 2027-33: [0.0887, 0.079, 0.0741, 0.0711, 0.0689, 0.0685, 0.0681]
- pooled (reported, un-gated): top 0.0740, bottom 0.0581

# Engine D run (PROVISIONAL), 2000 paths
- **two_tier** (10.5s): conservation True, slots-perm True, tail terminal PASS, transient PASS, autocorr PASS {1: 0.665458698472196, 2: 0.4713672207811223, 3: 0.3367348887767409}
  departures: {'Anthony Edwards': 0.889, 'LaMelo Ball': 0.886}  exit_shift -1.81  roster_cal r=0.979
- **pure_a** (8.1s): conservation True, slots-perm True, tail terminal PASS, transient PASS, autocorr PASS {1: 0.6607580700242676, 2: 0.4664970966101926, 3: 0.335507201149005}
# Engine D transient check: FAIL (parked) — decision memo for Bobby

2026-07-02 overnight. Two-tier variant, corrected 50k run (after fixing the
prior-chain leak, roster-calibration construction mismatch, reliability
shrinkage, and roster dedupe — all documented in the session log).

## Status of gates 8.4 (ratified operationalization)
| Gate | two_tier | pure_a |
|---|---|---|
| Conservation (1230 exact) | PASS | PASS |
| Slot permutation validity | PASS | PASS |
| Tail terminal (2033, ±25% band) | PASS (top +15.2%, bottom -19.1%) | PASS |
| Autocorrelation envelope | PASS | PASS |
| Transient (excess non-increasing, 2x MC SE) | **FAIL** | PASS |

## The miss, quantified
Yearly top-tail rates 2027-2033: .0827, .0691, .0660, .0661, .0667, .0676,
.0684 (hist .0594). The excess DECAYS from +.023 to +.007 by 2029, then
rises ~+.0024 through 2033 — many times the ~.0002 MC SE, so not noise.

## Diagnosis
Amendment 2 encoded "excess non-increasing," which assumes the conditional
transient approaches stationarity FROM ABOVE (true for pure Model A: .0886
monotone down to .0685). The two-tier variant's detail-team dynamics (MIN
declining through departure worlds, CHA cresting mid-horizon, renormalization
coupling) pull the league top-tail BELOW its stationary level mid-horizon;
the subsequent rise is CONVERGENCE to the same ~.068 stationary rate the
pure-A run reaches from above. The a-priori rationale in the ratified ruling
("the transient must fade; 2033 is effectively stationary") is satisfied in
substance: |excess| shrinks monotonically-ish from .023 to ~.008 and
stabilizes; the letter fails on direction of approach.

## Options for ruling (not applied; no threshold revision overnight)
1. Re-express the transient check on |excess| (or "no divergence after the
   first year": excess never exceeds its prior-year value by more than
   tolerance UNLESS still below the terminal level"). Rationale stands a
   priori: the check's purpose is fade-not-diverge, symmetric in approach
   direction. This is an operationalization amendment — yours to make, and
   it should be made blind to which variant it rescues (it does not change
   pure_a's verdict).
2. Accept the red cell documented (terminal + all other gates pass; the
   deliverable prices 2033, which is the gated horizon).
3. Treat the mid-horizon dip as a model artifact demanding investigation
   (e.g., is the CHA crest too strong? is renormalization coupling
   overstated?) before Stage 2.

## Interim handling (per overnight constraints)
Engine D outputs remain PROVISIONAL with 4/5 gates green and this memo
attached; downstream machinery (E2 resolution, exports) proceeds on
provisional artifacts; nothing publishes.

---

## Ruling B executed (2026-07-02) — escalation triggered, investigation complete

Re-judged BOTH variants under the symmetric check (|rate_t - rate_2033|
non-increasing, 2x MC SE): pure_a PASS, two_tier **still FAIL**.

### Why it still fails: overshoot-crossing, not divergence
Two-tier yearly top rates: .0825, .0692, .0661, .0661, .0667, .0672, .0683
(terminal .0683). The trajectory CROSSES its terminal value at ~2028
(distance .0009), dips below (renormalization suppression peaks 2029-30),
and recovers. Any monotone-distance check fails at a crossing by
construction: distance ~0 at the cross, then must rise before re-converging.
Max post-2027 violation: ~.002 absolute (~3% relative).

### Required decomposition: mechanism CONFIRMED, but not via flatness
The 28 prior-chain teams' top-tail rate also dips (.0877 -> .0673 -> .0697)
-- which triggered this escalation. Investigation: the dip is the arithmetic
complement of the MIN+CHA crest under 1230-win renormalization. MIN+CHA
combined mean win_pct runs hot mid-horizon (.601 at 2028 vs .551 pure_a);
the 28 teams' mean win_pct is suppressed by up to -.39pp exactly
mid-horizon; correlation between that suppression and the 28-team top-tail
gap across years: **0.996**. The field's own dynamics are clean (pure_a's
28 decay monotonically). "Flat at stationary" was unattainable in a closed
league once the detail teams move: renormalization transmits their crest to
everyone. Nothing is wrong in the field.

### Spec-compliance fix applied during investigation (honest miss noted)
Aging deltas were applied as posterior MEANS (deterministic crest in every
path); fixed to per-path posterior draws per the spec's uncertainty
propagation. Expected it to soften the crest; it did not (it widens per-path
spread; the crest is the mean path). Reported as predicted-wrong.

### Residual question for Bobby (option 3 scope)
Is the CHA crest right-sized? A -0.67-aggregate young roster cresting at a
~51-win median by 2029 via aging curves with no churn/injury drag, at
w(2029) = 0.65 roster weight, is directionally plausible (young cores do
ascend) but untested against historical young-core base rates. That
comparison (e.g., trajectory of sub-.500 teams with 3+ under-23 rotation
players, 1985-2019) is a well-posed Stage-2-prep analysis if you want the
crest validated rather than assumed. Alternatively: accept the red transient
cell documented (terminal — the deliverable horizon — passes everywhere,
and the violation is ~.002 at a confirmed-mechanism crossing).
No third check-rewording proposed: the pattern lesson says stop.

## RULING C (2026-07-02): cell accepted RED, documented, FINAL.
Crossing mechanism confirmed; no further rewording. Same posture as 8.1.


---
## Model E1 — slot value

```json
{
 "vorp": {
  "health": {
   "worst_r_hat": 1.0026153604198018,
   "min_ess_bulk": 1855.931544665648
  },
  "curve_mean": [
   5.664999961853027,
   5.244999885559082,
   4.925000190734863,
   4.415999889373779,
   3.984999895095825,
   3.4830000400543213,
   3.128999948501587,
   2.8429999351501465,
   2.6700000762939453,
   2.4670000076293945,
   2.2260000705718994,
   2.010999917984009,
   1.8769999742507935,
   1.7380000352859497,
   1.628999948501587,
   1.5360000133514404,
   1.4559999704360962,
   1.3849999904632568,
   1.319000005722046,
   1.2619999647140503,
   1.2109999656677246,
   1.1510000228881836,
   1.0959999561309814,
   1.0379999876022339,
   0.9789999723434448,
   0.9269999861717224,
   0.875,
   0.8190000057220459,
   0.7680000066757202,
   0.718999981880188,
   0.6700000166893005,
   0.621999979019165,
   0.5740000009536743,
   0.5329999923706055,
   0.492000013589859,
   0.44999998807907104,
   0.41100001335144043,
   0.3720000088214874,
   0.33000001311302185,
   0.289000004529953,
   0.24899999797344208,
   0.20800000429153442,
   0.1679999977350235,
   0.12600000202655792,
   0.08399999886751175,
   0.04100000113248825,
   -0.006000000052154064,
   -0.054
```

### Sim manifest: pure_a (PROVISIONAL)
gates: {'conservation': True, 'slot_permutation': True, 'tail_terminal_pass': True, 'tail_transient_pass': True, 'autocorr_pass': True, 'transient_check': 'ruling_B_symmetric_2026-07-02'}  paths: 50000  seed: 20330706

### Sim manifest: two_tier (PROVISIONAL)
gates: {'conservation': True, 'slot_permutation': True, 'tail_terminal_pass': True, 'tail_transient_pass': False, 'autocorr_pass': True, 'transient_check': 'ruling_B_symmetric_2026-07-02'}  paths: 50000  seed: 20330706