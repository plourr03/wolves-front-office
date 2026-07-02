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
