# D90. The chain re-run on refit impacts, before and after

*Before is `outputs/.chain_snapshot`, taken by `chain.py` before the run; the aged simulation's before state comes from git. After is the chain's output.*

## 1. Minnesota's title number and rank per view

| basis | view | before | rank | after | rank |
|---|---|---:|---:|---:|---:|
| un-aged | consensus | 0.82% | 16 | **0.86%** | **16** |
| un-aged | rapm | 1.20% | 15 | **1.25%** | **14** |
| un-aged | box | 2.11% | 13 | **2.03%** | **14** |
| un-aged | darko | 2.62% | 13 | **2.59%** | **13** |
| un-aged | **mean of four** | 1.69% | | **1.68%** | |
| aged | consensus | 1.29% | 15 | **1.18%** | **15** |
| aged | rapm | 1.85% | 13 | **1.75%** | **14** |
| aged | box | 3.33% | 12 | **3.03%** | **13** |
| aged | darko | 3.73% | 9 | **3.59%** | **9** |
| aged | **mean of four** | 2.55% | | **2.39%** | |

## 2. The shipping verdicts, all four cells

| verdict | pooled un-aged | pooled aged | team-rank un-aged | team-rank aged | ships |
|---|---|---|---|---|---|
| ball_in | +0.68 to **+0.79** | +0.78 to **+0.91** | +1.36 to **+1.56** | +1.33 to **+1.58** | yes to **yes** |
| reid_out | -0.42 to **-0.33** | -0.51 to **-0.40** | -1.08 to **-1.03** | -1.11 to **-1.05** | yes to **yes** |
| other_departures | +0.36 to **+0.29** | +0.71 to **+0.61** | -0.51 to **-0.87** | +0.13 to **-0.22** | no to **no** |
| randle_out | +0.07 to **-0.04** | +0.34 to **+0.19** | -0.22 to **-0.53** | +0.20 to **-0.11** | no to **no** |
| dosunmu_retained | -0.16 to **-0.21** | -0.22 to **-0.29** | -0.03 to **-0.29** | -0.13 to **-0.36** | no to **no** |
| depth | +0.06 to **+0.06** | +0.13 to **+0.13** | +0.75 to **+0.50** | +0.71 to **+0.55** | no to **no** |
| kuminga_in | +0.02 to **+0.04** | +0.10 to **+0.11** | +0.30 to **+0.22** | +0.35 to **+0.32** | no to **no** |
| ddv_injury | -0.42 to **-0.39** | -0.33 to **-0.33** | -0.91 to **-1.00** | -0.73 to **-0.83** | yes to **yes** |
| A_c3_default_shannon | +0.44 to **+0.44** | +0.57 to **+0.56** | +0.52 to **+0.55** | +0.58 to **+0.66** | yes to **yes** |
| B_lyles_fills | +0.01 to **+0.04** | -0.06 to **-0.01** | +0.03 to **+0.07** | -0.08 to **-0.01** | no to **no** |
| C_mcdaniels_slides | +0.41 to **+0.42** | +0.55 to **+0.54** | +0.50 to **+0.53** | +0.56 to **+0.64** | yes to **yes** |
| D_beringer_fills | -0.81 to **-0.72** | -1.42 to **-1.31** | -1.13 to **-1.03** | -1.94 to **-1.84** | yes to **yes** |
| E_tight_rule_F_or_FC | +0.44 to **+0.44** | +0.57 to **+0.56** | +0.50 to **+0.54** | +0.56 to **+0.64** | yes to **yes** |

Shipping before: 7. After: 7.
Dropped: none
Added: none
The seven that shipped before, still shipping: ['A_c3_default_shannon', 'C_mcdaniels_slides', 'D_beringer_fills', 'E_tight_rule_F_or_FC', 'ball_in', 'ddv_injury', 'reid_out']

## 3. Charlotte and Boston against the market

| team | basis | market | model before | model after | label before | label after | views above market, before to after |
|---|---|---:|---:|---:|---|---|---|
| CHA | unaged | 0.81% | 5.86% | **3.44%** | MIXED | **MIXED** | 3 to 3 |
| CHA | aged | 0.81% | 7.82% | **4.84%** | ALL-VIEWS | **ALL-VIEWS** | 4 to 4 |
| BOS | unaged | 5.47% | 17.00% | **18.33%** | ALL-VIEWS | **ALL-VIEWS** | 4 to 4 |
| BOS | aged | 5.47% | 13.49% | **14.23%** | ALL-VIEWS | **ALL-VIEWS** | 4 to 4 |
| MIN | unaged | 3.16% | 1.69% | **1.68%** | ALL-VIEWS | **ALL-VIEWS** | 0 to 0 |
| MIN | aged | 3.16% | 2.55% | **2.39%** | MIXED | **MIXED** | 2 to 1 |

**CHA**: label unchanged on both bases
**BOS**: label unchanged on both bases

## 4. The honesty rail

| basis | rank correlation before | after | disagreements before | after | all-views before | after |
|---|---|---|---:|---:|---:|---:|
| unaged | 0.78 to 0.82 | **0.78 to 0.83** | 20 | **20** | 16 | **16** |
| aged | 0.77 to 0.80 | **0.73 to 0.82** | 17 | **19** | 15 | **15** |
