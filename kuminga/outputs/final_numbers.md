# Final numbers

Every figure the piece may quote, with the run that produced it. Anything not on this sheet does not go in.

Frozen warehouse snapshot: `wh_cf31d54027f4e098`.

**Verdict labels.** QUOTABLE: survives all four views. QUOTABLE AS BAND: quote the range, never the midpoint. DIRECTIONAL: sign agreed, magnitude not. NOT QUOTABLE: views disagree on sign, or too uncertain. FACT: sourced or arithmetic, not a model output.

## The deal that cannot happen yet

| figure                                | value                         | band                            | verdict   | run_id                              | note                                                                  |
|:--------------------------------------|:------------------------------|:--------------------------------|:----------|:------------------------------------|:----------------------------------------------------------------------|
| MIN 2026-27 apron salary, pre-Kuminga | $215,871,829                  | 13 contracted players           | FACT      | cap_reconciliation_20260827T123553Z | contracted salary only; excludes cap holds and the roster placeholder |
| with Kuminga at the taxpayer MLE      | $221,935,829                  | 14 contracted players           | FACT      | cap_reconciliation_20260827T123553Z |                                                                       |
| amount over the second apron          | $249,829                      | second apron $221,686,000       | FACT      | eval_signing_20260827T123804Z       | less than a rookie-minimum contract                                   |
| trade branch at a legal 14-man roster | $208,614,817                  | $400,183 under the first apron  | FACT      | cap_reconciliation_20260827T123553Z |                                                                       |
| stretch branch at 14                  | $213,507,821                  | $4,492,821 OVER the first apron | FACT      | cap_reconciliation_20260827T123553Z |                                                                       |
| a 15th man in the trade branch        | $957,817 over the first apron |                                 | FACT      | cap_reconciliation_20260827T123553Z | so any salary returning in a Green trade crosses it                   |

## The price and the market

| figure                                      | value                  | band                                          | verdict          | run_id                        | note                                                                |
|:--------------------------------------------|:-----------------------|:----------------------------------------------|:-----------------|:------------------------------|:--------------------------------------------------------------------|
| Kuminga market value, four views            | $2.7M to $11.7M        | all-ages percentile map                       | QUOTABLE AS BAND | eval_signing_20260827T123804Z |                                                                     |
| best real bid (Lakers, rejected)            | $12.0M/yr over 3 years | ~$36M total, sign-and-trade                   | FACT             | eval_signing_20260827T123804Z | Anthony Slater, ESPN                                                |
| views agreeing with the real bid within 25% | 2 of 4                 | consensus $11.5M, RAPM $11.7M vs a $12.0M bid | QUOTABLE         | eval_signing_20260827T123804Z | the two possession-based views land within 4%; box and DARKO do not |
| age-restricted market value (22-25)         | $2.3M to $3.6M         | n=38, bimodal                                 | NOT QUOTABLE     | eval_signing_20260827T123804Z | measures the age structure of NBA pay, not his value                |
| surplus in impact units at the MLE          | -0.47 to +0.91         | 2 of 4 positive                               | NOT QUOTABLE     | eval_signing_20260827T123804Z | views disagree on sign                                              |
| surplus at Atlanta's declined $24.3M option | -1.76 to -0.03         | all four negative                             | QUOTABLE         | eval_signing_20260827T123804Z | all four views agree Atlanta was right to decline                   |

## The slot he inherits

| figure                                          | value              | band              | verdict          | run_id                           | note                                                       |
|:------------------------------------------------|:-------------------|:------------------|:-----------------|:---------------------------------|:-----------------------------------------------------------|
| Kuminga marginal contribution, slot-constrained | +0.140 to +1.226pp | ALL POSITIVE      | QUOTABLE AS BAND | slot_analysis_20260827T131606Z   | his minutes can only go to Terrence Shannon Jr.            |
| Randle+Gobert net rating                        | +3.10              | 3,443 possessions | FACT             | lineup_evidence_20260827T024925Z | descriptive on/off, not an effect                          |
| Reid+Gobert net rating                          | +6.83              | 2,253 possessions | FACT             | lineup_evidence_20260827T024925Z | descriptive on/off, not an effect                          |
| Kuminga on/off at GSW                           | -6.53              | 971 possessions   | FACT             | lineup_evidence_20260827T024925Z | small sample; the sign reversal between teams is the point |
| Kuminga on/off at ATL                           | +2.90              | 1,077 possessions | FACT             | lineup_evidence_20260827T024925Z | small sample; the sign reversal between teams is the point |

## What moved the offseason

| figure                    | value        | band             | verdict          | run_id                   | note         |
|:--------------------------|:-------------|:-----------------|:-----------------|:-------------------------|:-------------|
| Shapley: ball_in          | +1.30pp mean | +0.81 to +2.39pp | QUOTABLE AS BAND | shapley_20260827T131301Z | ALL POSITIVE |
| Shapley: randle_out       | +0.19pp mean | +0.05 to +0.28pp | QUOTABLE AS BAND | shapley_20260827T131301Z | ALL POSITIVE |
| Shapley: other_departures | +0.15pp mean | -0.50 to +1.33pp | NOT QUOTABLE     | shapley_20260827T131301Z | MIXED        |
| Shapley: depth            | +0.10pp mean | -0.16 to +0.39pp | NOT QUOTABLE     | shapley_20260827T131301Z | MIXED        |
| Shapley: kuminga_in       | -0.04pp mean | -0.73 to +0.40pp | NOT QUOTABLE     | shapley_20260827T131301Z | MIXED        |
| Shapley: dosunmu_retained | -0.52pp mean | -0.86 to -0.02pp | QUOTABLE AS BAND | shapley_20260827T131301Z | ALL NEGATIVE |
| Shapley: ddv_injury       | -0.72pp mean | -1.64 to -0.24pp | QUOTABLE AS BAND | shapley_20260827T131301Z | ALL NEGATIVE |
| Shapley: reid_out         | -0.98pp mean | -1.60 to -0.37pp | QUOTABLE AS BAND | shapley_20260827T131301Z | ALL NEGATIVE |

## The structural risk

| figure                             | value        | band                        | verdict          | run_id                         | note                                                             |
|:-----------------------------------|:-------------|:----------------------------|:-----------------|:-------------------------------|:-----------------------------------------------------------------|
| P(Kuminga opts out after year one) | 0.50 to 0.80 | flat aging                  | QUOTABLE AS BAND | player_option_20260827T024131Z | first-pass model, not calibrated                                 |
| P(Minnesota can retain him)        | 0.28 to 0.54 | flat aging                  | QUOTABLE AS BAND | player_option_20260827T024131Z | Non-Bird caps a re-sign start at $7,640,640                      |
| Non-Bird re-sign ceiling in 2027   | $7,640,640   | 120% of the year-two salary | FACT             | league_year_constants          | confirmed from CBA text: a declined option year is never covered |

## The West

| figure                                         | value    | band               | verdict          | run_id                             | note                               |
|:-----------------------------------------------|:---------|:-------------------|:-----------------|:-----------------------------------|:-----------------------------------|
| P(MIN avoids the play-in), baseline            | 0.73     | 0.73 to 0.73       | QUOTABLE AS BAND | seed_distribution_20260827T025830Z |                                    |
| P(MIN avoids the play-in), after the offseason | 0.62     | 0.39 to 0.84       | QUOTABLE AS BAND | seed_distribution_20260827T025830Z | the widest and most legible result |
| MIN West rank, before and after                | #5 to #6 | mean of four views | DIRECTIONAL      | build_outputs_20260827T131629Z     |                                    |
| MIN title probability, after                   | 2.62%    | 1.57% to 3.81%     | QUOTABLE AS BAND | run_sim_20260827T124337Z           | never quote the midpoint alone     |
| MIN offseason title-odds change                | -0.32pp  | -1.38 to +0.86pp   | NOT QUOTABLE     | run_sim_20260827T124337Z           | the four views disagree on sign    |

## Calibration

| figure                                            | value          | band                | verdict   | run_id                                | note                                            |
|:--------------------------------------------------|:---------------|:--------------------|:----------|:--------------------------------------|:------------------------------------------------|
| title-odds error vs the market, 3-season backtest | 1.44 to 2.35pp | mean absolute error | FACT      | backtest_calibration_20260827T124932Z | the same size as Minnesota's entire fork spread |
| win-total error vs the market                     | 8.80 vs 7.47   | model vs market MAE | FACT      | backtest_calibration_20260827T124932Z | model bias +0.27 wins                           |

