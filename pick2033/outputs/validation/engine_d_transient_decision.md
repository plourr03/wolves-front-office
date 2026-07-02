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
