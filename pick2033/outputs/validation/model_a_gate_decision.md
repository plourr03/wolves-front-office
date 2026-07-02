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
