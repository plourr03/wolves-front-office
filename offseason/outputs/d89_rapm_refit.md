# D89. RAPM refit on corrected possession points

*Before: the frozen pre-D89 possession cache. After: the rebuilt cache. Box and DARKO views are untouched; consensus is re-derived downstream.*

## Shifts

| view | mean | mean absolute | largest |
|---|---:|---:|---:|
| off_rapm | -0.014 | 0.334 | 1.45 |
| def_rapm | -0.021 | 0.311 | 1.46 |
| net_rapm | +0.007 | 0.582 | 2.49 |

## The direction of the bias, by and-one rate

| quartile   |   players |   and_one_rate |   d_off |   d_def |   d_net |
|:-----------|----------:|---------------:|--------:|--------:|--------:|
| Q1 lowest  |       124 |          0.023 |  -0.05  |  -0.029 |  -0.02  |
| Q2         |       123 |          0.044 |  -0.046 |  -0.01  |  -0.036 |
| Q3         |       123 |          0.06  |   0.096 |  -0.123 |   0.219 |
| Q4 highest |       124 |          0.084 |   0.105 |  -0.023 |   0.128 |

Correlation between a player's and-one rate and his offensive RAPM shift: **0.176**.

## Named players

| player | off before | off after | def before | def after | net before | net after | possessions | and-one rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Jonathan Kuminga | -1.16 | -0.98 | -2.53 | -2.80 | +1.37 | +1.82 | 17628 | 0.075 |
| Anthony Edwards | +3.39 | +4.15 | +2.21 | +2.02 | +1.18 | +2.14 | 36276 | 0.079 |
| Rudy Gobert | -0.76 | -1.46 | -6.52 | -6.47 | +5.76 | +5.01 | 33083 | 0.091 |
| LaMelo Ball | +4.18 | +5.10 | +2.23 | +1.24 | +1.95 | +3.86 | 17038 | 0.042 |
| Naz Reid | +0.55 | +0.62 | -2.72 | -2.11 | +3.27 | +2.72 | 28945 | 0.044 |
| Moussa Diabaté | +3.31 | +2.76 | -2.98 | -2.29 | +6.30 | +5.05 | 10571 | 0.074 |
| Kon Knueppel | +3.19 | +2.99 | -0.91 | -1.12 | +4.10 | +4.11 | 9854 | 0.045 |
| Neemias Queta | +1.20 | +1.17 | -3.77 | -4.01 | +4.97 | +5.18 | 11730 | 0.052 |
