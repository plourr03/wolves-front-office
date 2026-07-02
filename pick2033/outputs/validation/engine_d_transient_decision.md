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
