# Decision Memo: SIGN_GATE Amendment (FC-DRB admission)

Filed 2026-07-17, per Bobby's ruling of the same date. This memo documents the amendment that admits FC-DRB as the second wire, the symmetry re-check it forces, the confidence intervals, and one caveat the analysis surfaced that Bobby's ruling did not address and that belongs at the Phase 4 review.

## The amendment is a translation, not a retune

The pre-registered gate was sign consistency >= 0.70 (a binarized concordance: the fraction of cases where the early metric's direction relative to the class median matches the outcome's). FC-DRB's sign consistency is 0.659, which fails that gate. The amendment does not lower the gate; it translates it to the continuous scale the sign gate is a coarse proxy for.

Under the standard orthant relationship for a bivariate-normal pair, the probability of concordance is

    C = 1/2 + arcsin(rho) / pi

so a concordance gate of 0.70 corresponds to a correlation of

    rho = sin((0.70 - 0.5) * pi) = sin(0.2 pi) = 0.588 ~ 0.59.

Verified numerically: the 0.70 sign gate maps to Spearman 0.588. **The amendment: for classes with n >= 30, the continuous criterion governs at Spearman >= 0.59 (the arcsine image of the pre-registered 0.70); for n < 30 the original 0.70 sign gate stands unchanged.**

The rationale is outcome-independent, decided on the statistic not the answer: the sign gate exists to protect tiny classes from overfit correlations, where a high rho can ride on two or three influential points and the binary concordance is the more robust screen. At n = 82 that protection is not needed and the binarization is the blunter instrument, discarding the magnitude information the Spearman keeps. The cutover at n = 30 is the usual large-sample threshold. This rule would have been the better pre-registration; it is adopted now, in the open, with the disclosure below.

## Symmetry check (every metric, both rules)

N_GATE (8) is Fixed and untouched. The translated rule is applied to every candidate, not just FC-DRB:

| Metric | n | Spearman | sign | n>=30? | Binarized gate (0.70) | Continuous gate (0.59) | Verdict |
|---|---|---|---|---|---|---|---|
| AVAIL-PACE | 388 | 0.769 | 0.772 | yes | PASS | PASS | **wire** (unchanged either way) |
| FC-DRB | 82 | 0.617 | 0.659 | yes | fail | **PASS** | **admitted via continuous** |
| PAIR-DRTG | 6 | -0.09 | 0.67 | no | (n < N_GATE=8) | (n < 30, orig gate) | **demoted** (fails N_GATE) |
| TOV-BLEED | 6 | — | — | no | (n < N_GATE=8) | (n < 30, orig gate) | **demoted** (fails N_GATE) |

AVAIL-PACE is unchanged: it clears both the binarized and the continuous gate, so the amendment does not touch it. PAIR-DRTG and TOV-BLEED stay demoted: at n = 6 they fail the Fixed N_GATE outright, the amendment's n >= 30 branch never applies to them, and the original sign gate would govern if it did. Only FC-DRB's verdict moves, and only from fail-to-pass on the continuous criterion its own binarized proxy was approximating.

## Confidence intervals (reported, not gates)

Per the ruling, CIs are reported for both statistics on both surviving metrics. Fisher z-interval for the correlations, Wilson interval for the sign proportions, 95%:

| Metric | Spearman [95% CI] | sign [95% CI] |
|---|---|---|
| FC-DRB | 0.617 [0.461, 0.735] | 0.659 [0.551, 0.752] |
| AVAIL-PACE | 0.769 [0.724, 0.807] | 0.772 [0.727, 0.811] |

These are not gates and do not change any verdict. Note honestly: FC-DRB's Spearman CI lower bound (0.461) sits below the 0.59 continuous gate, so the point estimate clears the gate but the interval includes values that would not. AVAIL-PACE's entire interval sits well above. This is the quantitative statement of what "marginal wire" means for FC-DRB.

## Caveat surfaced for the Phase 4 review: which FC-DRB number is the wire built on

This is not in Bobby's ruling and I am flagging it rather than deciding it. The 0.617 the amendment admits FC-DRB on is the **Scenario C succession-class persistence, measured on whole-team defensive rebounding for teams whose primary anchor departed entirely** (n = 82). But the wire's own metric is **Gobert-off (anchor-off) defensive rebounding**, because the Wolves keep Gobert and lose the *second* anchor, Naz Reid. Those are different quantities:

- The wire's actual metric, anchor-off DRB persistence across all team-seasons: early-to-rest Spearman ~0.50 (drb37->rest 0.495, matching its reliability r(25) = 0.502). This is **below** the 0.59 continuous gate.
- The succession-class whole-team DRB persistence (what the ruling used): 0.617, **above** the gate.

The class membership is defensible: the spec explicitly frames the Wolves as a Scenario C case ("the 2026-27 Wolves instance is the Naz Reid departure behind Gobert"), and Reid is a frontcourt anchor departing. But the *metric* the wire computes (Gobert-off DRB) persists more weakly (~0.50) than the class-level signal (0.617) the admission rests on, because Gobert stays and stabilizes the primary rebounding while the bench-frontcourt hole is noisier. **The two-read persistence requirement (fire only if bottom-tier at both R1 and R2) is what makes the marginal metric usable**: it lifts P(the hole persists) but only to ~0.49, so the wire is genuinely marginal.

Recommendation for the review: keep FC-DRB as the marginal ARM-B wire (the succession-class validity and the two-read requirement justify it as a plausibility trigger, not a precise predictor), but state its metric-definition caveat in TRIPWIRES.md alongside the gate disclosure, so the February decision knows the second wire is the weaker of the two and rests on a class-level analog rather than the exact metric it reads. If the review judges that gap disqualifying, FC-DRB demotes to dashboard and TRIPWIRES.md ships one binding wire (AVAIL-PACE) plus the free ARM-S advisory, which is a clean and honest fallback.

## Disclosure (for TRIPWIRES.md change control)

FC-DRB failed the original binarized sign gate (0.659 vs 0.70). The gate was amended to a continuous Spearman >= 0.59 criterion for n >= 30 (the arcsine translation of 0.70), **after seeing the data**, on 2026-07-17. Under the original rule FC-DRB is out; under the amended rule it is in. Both verdicts are recorded here and in TRIPWIRES.md. The amendment is outcome-independent in its justification (it protects the same thing the sign gate protects, more precisely) but was adopted post hoc, and that is disclosed rather than hidden.
