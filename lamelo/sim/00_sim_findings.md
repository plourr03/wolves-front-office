# Sim findings, 2026-06-25 (GATED, hold for review)

Both metric forks run end to end and internally consistent, CRN-paired (run-it-back vs
post-trade share the same draws). Reuses the calibrated sim method + SCALE/SHAPE/series
params. The TITLE NUMBER IS GATED pending the clean-room re-validation diff + the
retrodiction backtest (see Gates). The CRN-paired delta and the Q2 ordinals are
field-robust and reported with that caveat.

## The gated title-odds picture

| quantity | RAPM (defense-aware) | box (defense-blind) |
|---|---|---|
| post-trade P(title) | 2.66% | 3.92% |
| post-trade P(reach CF) | 15.1% | 19.3% |
| post-trade P(reach Finals) | 6.4% | 8.6% |
| CRN-paired title delta | +0.005pp | +1.113pp |
| Monte Carlo sd on the delta | 0.003pp | 0.059pp |

Inter-fork point spread on the title delta = [+0.005, +1.113] pp. AUDIT FIX 4: this is the
point spread between the two metric forks ONLY (at the modeled-Gueye point). It does NOT
include parametric input uncertainty (impact SDs, transport band) or the role-player
valuation fork, so the TRUE band extends well BELOW zero (the Gueye fork alone drives the
RAPM net delta to -0.56 / -1.12; see `impact/03_team_strength_findings.md`).

## The headline (honest, gated)

The title-odds delta depends entirely on which defensive metric you trust, a choice the
out-of-sample calibration could NOT settle (the YoY test tied). Under the defense-aware
read the trade moves title odds by +0.005pp, indistinguishable from zero. Under the
defense-blind read it is a modest +1.1pp. The structural band [+0.005, +1.11]pp INCLUDES
zero, so the title delta is not distinguishable from zero at the resolution set by the
unresolved metric choice. Best case a modest +1.1pp; on the more defensively complete
read, nothing. We do not cherry-pick: both are reported, and the band includes zero.

## Reducible vs irreducible (the band, decomposed)

- Monte Carlo sampling: tiny (<= 0.06pp), already negligible and CRN-shrunk. Reducible
  but not worth more sims.
- Parametric (input SDs, transport band, AND the role-player valuation fork from audit Fix
  1): moderate-to-large, reducible with better data. The Gueye fork alone pushes the RAPM
  delta below zero, so including it the title-delta band crosses well below zero.
- STRUCTURAL (the defensive-metric fork): DOMINANT, ~1.1pp, dwarfs everything else. It is
  reducible only with a metric-discriminating calibration that more/better data could
  eventually provide; current data cannot separate the metrics (the YoY tie). So today it
  is effectively irreducible.
- Aleatoric (one-season variance): baked into the absolute title odds (sigma_unobs), but
  the CRN-paired delta removes nearly all of it.

So the fuzziness is STRUCTURAL, not Monte Carlo and not one-season noise. More compute
buys nothing; the answer is gated by an unresolved metric choice. Per the spec, that
finding is published, not hidden.

## Q1 connection (the editorial payload)

This title-odds change, indistinguishable from zero on the most complete read and at best
a modest +1.1pp, was bought with a 2033 unprotected first, three first-round swaps
(2028/2029/2030), three seconds, and a second-apron hard cap (with the $33.3M exception
and the full MLE forfeited). The decision-grade story: a mountain of future spent to, at
best, nudge title odds by a point, and on the defense-aware read, to tread water.

## Gates remaining before the title number publishes

1. Re-validate the SCALE, SHAPE, and series-resolver calibrations clean-room and DIFF
   against the old params (alpha -5.4365, beta 1.067, wins_a 41, wins_b 2.239, sigma_unobs
   5.5, series b0 0.5018 / b1 0.1345). Stop-if-fail. This run reused them as a documented
   reproduction; the formal diff is pending.
2. Run the retrodiction backtest on the sealed 2016-19 + 2022-23 holdout with the
   pre-registered pass/fail. Must pass before any title number prints.

Until both pass, the title number above is PROVISIONAL. The structural finding (the
delta is fork-dependent and indistinguishable from zero at this resolution) does not
depend on those gates and is the robust result.
