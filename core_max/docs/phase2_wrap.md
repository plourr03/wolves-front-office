# Phase 2 wrap: Joan's development distribution (FROZEN v1.3 spec)

Joan's impact is priced as an empirical comp-class distribution (the maturity bridge:
membership from his structural profile, impact only from comps' reliable mature seasons,
washouts floored to a composition-set replacement, map residual uncertainty propagated).
Reported for the full N=28 class and the binding Joan-like sub-class (rookie minutes <= 600,
N=14). Method merits decided every number; sobering is a coincidence here, not a policy.

## Joan's per-year impact (net), replacement center -1.70

| view | year | washout | median | p75 | p90 |
|---|---|---|---|---|---|
| full class | Yr1 (2026-27) | 43% | -0.6 | +1.6 | +3.0 |
| full class | Yr2 (2027-28) | 43% | -0.5 | +2.0 | +3.6 |
| **sub-class (faithful)** | Yr1 | **64%** | **-1.4** | +0.1 | +2.2 |
| **sub-class (faithful)** | Yr2 | **64%** | **-1.4** | +0.5 | +2.7 |
| full, mature (cy4-6) | out-year | ~44% | ~-0.3 | +2.4 | ~+4.0 |
| sub, mature (cy4-6) | out-year | ~55% | ~-1.1 | +1.7 | +3.2-3.6 |

His rookie RAPM is near-uninformative for the future (unvalidatable development gap): the
nudge is +0.34 at the widest gap (baseline), and it touches NOTHING in the out-year term.
With the nudge, Yr1 mean is +0.38 (full) / -0.36 (sub).

## The verdict, stated honestly

The faithful (sub-class) base rate: **Joan is more likely than not (64%) to be a
replacement-level player, with a median outcome below replacement, a real but minority
develop tail (p75 around break-even, p90 +2.2 early to +3.3 mature), and a Bynum-shaped
ceiling that rests on six or seven survivors.** The full class is gentler (43% washout,
median -0.6) but it is the diluted view (the median comp played roughly twice Joan's rookie
minutes). The bet survives only in the sense that the upside tail is real, NOT as "Joan is
likely good." This is the honest base rate for his exact profile.

## What this means for Fork B (the part to stake openly)

Fork B trades Gobert (a stable, established ~+4.5 mature impact) for Joan (a mostly-bust
gamble with a long-shot ~+3.3 ceiling) plus salary flexibility and two fit returns. For
Fork B to be the P(title)-maximizing move, the Phase 3 title engine has to show that Joan's
upside tail, the flexibility, and the fit gains together outweigh giving up Gobert's high floor
(high, but NOT certain: a 34-year-old center's floor carries real collapse risk, which the
Phase 3 veteran-collapse left-tail prices, so the comparison has honest tails on both sides),
under the convexity of P(title) at the Wolves' operating point. The model has
refused to bake the Joan belief in; it is now an open wager the GM stakes, not an assumption
the model granted. That is the spirit clause cashing out: the bet is real, it is steep, and
it is honestly framed.

## Fragility (carry loudly into Phase 3)

- N = 28 (14 in the faithful sub-class); the out-year upside rests on 6-7 survivors. Wide humility.
- Replacement bracket is wide and matters: sub-class Yr1 median runs -0.72 (generous -0.97)
  to -1.40 (center) to -2.50 (harsh -2.83). Carry the bracket as a Phase 3-4 sensitivity.
- Basic-box->impact map R2 ~0.37 (residual sd 1.70), propagated so the distribution is not
  artificially tight.

## For Phase 3 (the title engine), per-iteration sampling

- Sample Joan's per-year impact from the comp-class empirical distribution
  (`outputs/phase2/dev_distribution_percomp.csv`), NOT a collapsed mean.
- Sweep, do not pick: full vs faithful sub-class; the replacement bracket [-0.97, -2.83];
  and the established-SD variants from Phase 1c. The verdict must hold across the grid.
- Joan's rookie nudge <= +0.34 (near-uninformative); the out-year real-option term gets none.
- Veteran collapse left-tail (Phase 3 carry-forward) still owed for Gobert/Conley.
