# The Williams ordering check

*Run `williams_ordering_check_20260929T061318Z`. Item 1 is the projected ten under both allocators; item 2 re-orders the same roster three ways; item 3 sets his minutes from the mover base rate (`mover_minutes_base_rate.py`). Every verdict is priced the way the sensitivity script prices it: title odds at the roster's net minus at the baseline's, per view, off the f-curve, the field fixed.*

## 1. Minnesota's pool by rank score

| # | player | rank score | minutes pct | impact pct | prior mpg | mover | consensus | RAPM | box | DARKO | team-rank mpg | pooled mpg |
|---:|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Rudy Gobert | 0.919 | 0.88 | 0.96 | 31.3 |  | +4.88 | +5.01 | +0.78 | +2.00 | 34.3 | 34.3 |
| 2 | Anthony Edwards | 0.896 | 0.98 | 0.81 | 35.0 |  | +2.66 | +2.13 | +1.58 | +4.00 | 36.0 | 30.5 |
| 3 | LaMelo Ball | 0.876 | 0.74 | 0.91 | 28.0 | yes | +3.78 | +3.86 | +1.98 | +3.00 | 31.0 | 26.9 |
| 4 | Jaden McDaniels | 0.734 | 0.89 | 0.58 | 31.7 |  | +0.98 | +0.99 | -0.32 | +0.00 | 32.0 | 26.7 |
| 5 | Jonathan Kuminga | 0.661 | 0.55 | 0.69 | 23.1 | yes | +1.65 | +1.82 | +0.21 | -1.00 | 26.1 | 22.1 |
| 6 | Ayo Dosunmu | 0.486 | 0.71 | 0.26 | 27.3 |  | -0.78 | -1.59 | +0.51 | -1.00 | 26.8 | 22.3 |
| 7 | Joan Beringer | 0.450 | 0.06 | 0.84 | 7.9 |  | +2.84 | +3.55 | +3.56 | +1.00 | 10.9 | 10.9 |
| 8 | Nah'Shon Hyland | 0.415 | 0.29 | 0.54 | 16.6 |  | +0.78 | +0.13 | +1.07 | +nan | 18.4 | 15.3 |
| 9 | Jaylen Clark | 0.333 | 0.18 | 0.49 | 13.1 |  | +0.46 | +0.93 | +0.06 | +0.00 | 15.6 | 13.0 |
| 10 | Trey Lyles | 0.229 | 0.03 | 0.43 | 6.0 |  | +0.24 | +0.25 | -0.02 | +nan | 9.0 | 8.8 |
| 11 | Isaiah Evans | 0.177 | 0.11 | 0.25 | 10.6 |  | -0.82 | -0.82 | -0.82 | -0.82 | 0.0 | 9.8 |
| 12 | Cody Williams | 0.128 | 0.60 | 0.01 | 24.3 | yes | -4.39 | -4.42 | -2.18 | -3.00 | 0.0 | 10.8 |
| 13 | Terrence Shannon Jr. | 0.110 | 0.16 | 0.06 | 12.5 |  | -2.40 | -2.44 | -0.89 | -2.00 | 0.0 | 8.6 |

Shannon in the team-rank ten: **no**. In the pooled top ten by minutes: **no**.

## 2. Three orderings, and 3. the calibrated default

| ordering or level | Williams rank | Williams mpg | offseason delta, mean | sign | consensus | RAPM | box | DARKO |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| primary: mover-discounted order (movers 0.2 / 0.8) | 12 | 0.0 | +0.30 | MIXED | -0.39 | +0.34 | +0.31 | +0.93 |
| sensitivity: flat 0.5 / 0.5 order for all | 10 | 16.1 | -0.78 | ALL NEGATIVE | -1.35 | -0.86 | -0.53 | -0.36 |
| impact only (pct impact, all) | 13 | 0.0 | +0.35 | MIXED | -0.33 | +0.44 | +0.31 | +0.99 |
| calibrated: median retention, all movers | 12 | 18.0 | -1.13 | ALL NEGATIVE | -1.65 | -1.23 | -0.84 | -0.79 |
| calibrated: lower quartile, all movers | 12 | 10.6 | -0.62 | ALL NEGATIVE | -1.23 | -0.70 | -0.40 | -0.17 |
| calibrated: upper quartile, all movers | 12 | 22.0 | -1.36 | ALL NEGATIVE | -1.83 | -1.46 | -1.05 | -1.09 |
| calibrated: median, new team top ten by wins (n=8) | 12 | 11.7 | -0.71 | ALL NEGATIVE | -1.30 | -0.80 | -0.47 | -0.27 |
| calibrated: median, new team at or above .600 (n=6) | 12 | 11.7 | -0.71 | ALL NEGATIVE | -1.30 | -0.80 | -0.47 | -0.27 |
| calibrated: median, new team under .500 (n=16) | 12 | 20.7 | -1.29 | ALL NEGATIVE | -1.77 | -1.39 | -0.99 | -1.00 |

Mover base rate: n = 34, retention median 0.74, quartiles 0.43 and 0.90; Williams's prior load 24.3 a night.
