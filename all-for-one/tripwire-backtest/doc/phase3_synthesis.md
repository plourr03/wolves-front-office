# Phase 3: Predictive Validity Synthesis

Tripwire backtest, Phase 3. Produced 2026-07-17. Scripts: `avail_pace_mapping.py`, `avail_pace_derivation.py`, `compute_scenarioA_labels.py`, `compute_scenarioC_labels.py`. This synthesizes predictive validity across all candidate metrics and reports wire-eligibility against the pre-registered gates. **Phase 4 selection is not performed here; it stops for Bobby's review, per the ruling.**

No p-values, per the spec: at these sample sizes they would be theater. Exact case counts are reported everywhere.

## The gates (pre-registered, from the spec config)

A metric is wire-eligible only if it clears all three: reliability r(25) >= 0.50 (exact-count metrics exempt), at least N_GATE = 8 labeled cases, and sign consistency >= SIGN_GATE = 0.70. SIGN_GATE is marked TUNE in the config.

## Results by metric

| Metric | Reliability r(25) | Class (n labeled) | Predictive Spearman | Sign consistency | Verdict |
|---|---|---|---|---|---|
| **AVAIL-PACE** | exempt (exact count) | Scenario B (388) | **0.77** | **0.77** | **WIRE-ELIGIBLE**, gates ARM-G |
| **FC-DRB** | 0.502 (pass) | Scenario C (82) | 0.617 | 0.659 | reliability + strong Spearman, **misses sign gate (0.659 < 0.70)** |
| PAIR-DRTG | 0.512 (pass) | Scenario A YA1 (6) | -0.09 | 0.67 | **underpowered** (n=6 < 8); hypothesis not confirmed |
| TOV-BLEED | 0.665 (pass) | Scenario A (6) | — | — | **underpowered** (same co-star class) |
| SPACE-ANT | no curve (G4) | — | — | — | dashboard-only |

## AVAIL-PACE: the one metric that clears every gate

Detailed in `phase3_avail_pace.md` and `phase3_avail_pace_derivation.md`. Across 388 Scenario B cases, early availability pace predicts full-season availability with Spearman 0.77 at N=20 and sign consistency 0.77, both above gate, on the largest class in the study. Its threshold is derived and baseline-conditioned (LaMelo trips toward ARM-G at 12 or fewer of 20 games at R1, 23 or fewer of 37 at R2). It is exempt from the reliability gate as an exact count. This is the strongest-supported wire and the only one that clears the pre-registered gates unambiguously.

## FC-DRB: strong rank signal, misses the sign gate

FC-DRB clears reliability (0.502, marginal) and shows a solid predictive signal on a well-powered class: across 82 Scenario C succession cases, early anchor-off defensive rebounding predicts rest-of-season anchor-off rebounding with Spearman 0.617. The early hole persists, which is exactly the predictive claim that would justify ARM-B (acquire a rebounding big): a team rebounding poorly in anchor-off minutes early is likely to keep doing so.

**But its sign consistency is 0.659, just below the 0.70 gate.** Per the rigor discipline (falsifiable gates, never retune a threshold to make a metric pass), FC-DRB is reported as **failing the pre-registered sign gate**, notwithstanding the strong Spearman. Whether a 0.70 binary-sign bar is the right screen for a metric with a well-powered Spearman of 0.617 is a SIGN_GATE-is-TUNE question, and it is Bobby's Phase 4 call, not one to resolve by lowering the bar here. Flagged, not decided.

## PAIR-DRTG and TOV-BLEED: the co-star class is too small

Both pass reliability. Both are separators in the spec's central Scenario A hypothesis ("early offense is the false signal; the separators were availability pace, shared-floor defense, and the turnover/spacing interaction"). But that hypothesis lives on the co-star class, and the co-star class cannot power the test:

- The strict Scenario A class is 17 cases, but **only 6 have a computable YA1 label** (pair shared-floor net rating over games 41-82, 800-possession floor). The 8 midseason arrivals mostly cannot be labeled: "games 41-82" postdates their arrival, or the pair never logged 800 shared possessions (Harden-Durant in an injury-hit 2020-21, Irving-Doncic arriving in February, and so on). YA1 as defined is an offseason-arrival label.
- At n=6, the defense-separates test is underpowered (below N_GATE = 8) and its point estimate actually runs the wrong way (early offense Spearman +0.60, early defense -0.09), which at this sample size is noise, not a refutation.

**The spec anticipated exactly this**: "This is a hypothesis with a class size around twelve. Treat it as a prior, not a verdict." The data confirms the class is too small to promote PAIR-DRTG or TOV-BLEED from prior to verdict.

Per the pre-staged PAIR-DRTG decision rule: the YA1 hypothesis did not confirm, so PAIR-DRTG demotes to dashboard and G6 shrinkage is not built. TOV-BLEED rests on the same underpowered class and demotes on the same grounds.

## What Phase 3 hands to Phase 4 (the stop)

The honest state of the wire library after three phases:

1. **AVAIL-PACE** clears every pre-registered gate on a 388-case class. It is a binding wire gating ARM-G, with a derived, baseline-conditioned threshold and a full derivation memo.
2. **FC-DRB** clears reliability and shows a well-powered predictive Spearman (0.617, n=82) but misses the sign gate (0.659 vs 0.70, TUNE). It gates a different arm (ARM-B). Its promotion hinges on a SIGN_GATE decision that is Phase 4's to make.
3. **PAIR-DRTG and TOV-BLEED** clear reliability but their predictive validity rests on the ~6-case co-star class and cannot be confirmed. They remain dashboard diagnostics unless the class grows.
4. **SPACE-ANT** was never a candidate (no data, G4).

This points toward shipping **one to two binding wires** (AVAIL-PACE certainly; FC-DRB if the sign gate is judged too strict for a strong-Spearman metric), covering two different arms (ARM-G, ARM-B), rather than four. MAX_WIRES is a cap, not a quota, and the honest reading of the data is that only the two large classes (Scenario B availability, Scenario C succession) can currently support wires; the co-star class cannot. That is a real finding, not a shortfall: it says the February decision is best instrumented on availability and frontcourt rebounding, and that the co-star-fit question needs either more history or a different (non-backtest) instrument.

Phase 4 selection, the TRIPWIRES.md draft, and the SIGN_GATE decision stop here for Bobby's review.
