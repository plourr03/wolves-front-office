# Contract backfill coverage (spec 6.2 / Ruling A)
- source: B-Ref all_salaries, 211 spell players, 0 with no salary table: []
- spell-season coverage: **99.5%** of 1290 rows
- by decade: 1990s 98.7%, 2000s 99.7%, 2010s 100.0%, 2020s 99.6%
- walk-year rate among covered rows: 43.1%
- method: salary-break + franchise-change inference; era envelopes keyed on the segment's SIGNING season (25% pre-1999, 15% to 2011, 9% after; 30% in a career's first four seasons for rookie scale); with a raise-structure re-sign detector (rookie-exempt; tight pass on 6+yr residual segments). Duncan-pattern mislabeling EXAGGERATES the contract coefficient (settled by synthetic test, duncan_bias_test.py; the earlier 'attenuates' claim was wrong). Residual ambiguity routes to the pre-declared sensitivity arm, not hand edits. QC'd against Edwards/Garnett/LeBron/Duncan/Kobe ground truth. Data enters the M2 refit blind to fit outcomes.
## Directive-3 sensitivity arm S-CONTRACT — pre-declared 2026-07-02
The 21 residual >=6yr segments among long-tenure stars
(outputs/contract_longsegments_review.csv) mix REAL long deals (Garnett's
1999-2004 $126M, Kobe's 2000-2005, Duncan's 2005-2010 — correctly single
segments) with probable glue the detector cannot separate on salary
evidence alone (Curry's 2022 supermax junction is a +5% raise; LeBron's
LAL chain of short deals; Magic's 1995-2010 post-retirement listing
artifact). No hand edits. Pre-declared arm, to run alongside the S7
tornado: re-derive years_remaining with each residual segment SPLIT AT ITS
MIDPOINT (the maximal-plausible-glue counterfactual), refit the hazard
under the same M2_FINAL_SPEC as an UNGATED sensitivity fit, and report the
Edwards-curve and downstream deltas. The gated one-shot M2 fit uses the
unperturbed labels.
