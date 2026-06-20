# Phase 1d: knob-effect report

The guardrail: report what each Phase 1 calibration knob does to the
Fork-B-minus-splash comparison, so the verdict is never an artifact of a knob set
to taste. Both knobs came out NEUTRAL, which is the fair outcome.

## Knob 1: established-player SD level (1c)

- **Adopted: as-is, a=1.0, b=0.0** (analytic posterior SD unchanged). The corrected
  held-out test refused inflation (it over-covers); the grid wanted to shrink, which
  was declined as thesis-flattering on a low-power, survivor-only test.
- **Effect on the established distributions:** `sd_used = net_sd`. No widening, no
  tightening.
- **Carried as Phase 3-4 sensitivity variants** (in `inflation_params.json`): a
  shrink (a=0.8, the corrected-test point estimate) and a mild heteroscedastic widen
  (b=0.20, for the high-divergence under-coverage). Phase 3-4 sweeps both through the
  title simulation and shows the Fork-B-vs-splash verdict is robust across the knob's
  whole plausible range, which resolves the SD level by demonstrating the answer does
  not depend on it rather than by winning the calibration argument now.

## Knob 2: box-to-RAPM rim correction (1b)

- **Applies to reliable-sample players' BOX priors only; gated OFF for unreliable
  players (Joan).** But the established baseline (1a) uses `consensus_net`, which is
  RAPM-based and already prices rim protection directly. The corrected box estimate is
  NOT used for established players. So the rim correction does **not enter** the
  established team-strength at all.
- **Where it does matter:** Phase 2 young-player box priors, where it is gated off for
  Joan. So its effect on the current Fork-B-vs-splash comparison is **zero**.

## Net

Neither Phase 1 knob enters the Fork-B-vs-splash comparison. The eventual verdict will
rest on point estimates and roster construction, the things that should decide it, not
on a tunable someone could say was set to taste. That is the fairness property the
apparatus existed to protect.

## Directional comfort on any residual error

If the established SDs are nonetheless a touch wide, the extra tail accrues to the
**veteran-heavy** rosters (status_quo, splash), because their variance comes from these
established SDs while Fork B's upside comes from the Phase 2 young-player module. So any
leftover SD error runs **against** Fork B, not for it. That is the direction we want
residual bias to run.

## Deferred to Phase 3-4

The full, quantitative title-gap sensitivity (sweeping the SD variants and the rim
correction through the Monte Carlo) wires in once the scenarios carry real acquired
players instead of salary-matched placeholders.
