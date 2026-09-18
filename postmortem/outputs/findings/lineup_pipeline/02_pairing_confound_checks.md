# Confound checks: Gobert+Naz and Gobert+Randle pairings
> **CORRECTED 2026-09-18 (D88).** The lineup net ratings, on/off figures and pairing figures below were computed on stint points that credited about 3.4% of points to the wrong team. Regular-season figures move by under 2 points per 100. Playoff figures move by up to 17 and five change sign. Before and after for every figure: `postmortem/outputs/findings/lineup_pipeline/03_d88_points_fix_and_recompute.md`. Do not quote a playoff figure from this document without checking it there.

**Date:** 2026-05-17
**Cohorts:** 2025-26 playoffs, gt-filtered Wolves stints.
**Context variables:** series (R1 vs DEN / R2 vs SAS), Edwards game-availability status (DNP / Limited / Normal), Edwards on-floor flag (whether Ant was actually in this specific lineup_id), score margin at stint start.
**Bootstrap:** 1000 resamples of stints with replacement, seed=42.

## Cohort A: Gobert+Naz on floor, Randle OFF
### Gobert+Naz, no Randle

- **Stints:** 75  
- **Minutes:** 127.3  
- **Possessions (off/def):** 262 / 260  
- **Net rating:** **+9.82** (95% CI [-9.87, +28.86])  
- **Off rating:** 123.3  /  **Def rating:** 113.5  
- **Off 3PA rate:** 0.290  
- **fg3a per 100:** 27.9

**By series:**

```
series_label  stints_n  minutes  poss_off  poss_def  pts_for  pts_against   net
   R1_vs_DEN        42    67.55       136       131      164          152  4.56
   R2_vs_SAS        33    59.73       126       129      159          143 15.34
```

**By Edwards game-status (the game the stint was played in):**

```
edwards_status  stints_n  minutes  poss_off  poss_def  pts_for  pts_against   net
           DNP        14    19.67        37        36       52           46 12.76
       Limited        24    45.79        95        97      103          105  0.17
        Normal        37    61.82       130       127      168          144 15.84
```

**By Edwards on the floor (was Ant in this lineup_id):**

```
 edwards_on_floor  stints_n  minutes  poss_off  poss_def  pts_for  pts_against   net
            False        33    52.43       104       108      136          126 14.10
             True        42    74.85       158       152      187          169  7.17
```

**Score margin at stint start (Wolves perspective):**

```
margin_at_start
Close (-2..+2)    15
Leading 10+        8
Leading 3-10      12
Trailing 10+      12
Trailing 3-10     28
```

## Cohort B: Gobert+Randle on floor, Naz OFF
### Gobert+Randle, no Naz

- **Stints:** 74  
- **Minutes:** 197.4  
- **Possessions (off/def):** 397 / 392  
- **Net rating:** **-12.22** (95% CI [-26.17, +1.81])  
- **Off rating:** 97.7  /  **Def rating:** 109.9  
- **Off 3PA rate:** 0.317  
- **fg3a per 100:** 29.2

**By series:**

```
series_label  stints_n  minutes  poss_off  poss_def  pts_for  pts_against    net
   R1_vs_DEN        38   108.64       215       216      219          221  -0.45
   R2_vs_SAS        36    88.73       182       176      169          210 -26.46
```

**By Edwards game-status (the game the stint was played in):**

```
edwards_status  stints_n  minutes  poss_off  poss_def  pts_for  pts_against    net
           DNP        11    23.35        40        42       38           46 -14.52
       Limited        27    76.32       157       155      153          166  -9.64
        Normal        36    97.70       200       195      197          219 -13.81
```

**By Edwards on the floor (was Ant in this lineup_id):**

```
 edwards_on_floor  stints_n  minutes  poss_off  poss_def  pts_for  pts_against    net
            False        28    71.32       143       142      140          156 -11.96
             True        46   126.05       254       250      248          275 -12.36
```

**Score margin at stint start (Wolves perspective):**

```
margin_at_start
Close (-2..+2)    26
Leading 10+        6
Leading 3-10      11
Trailing 10+      15
Trailing 3-10     16
```

## Cohort C: All three bigs on floor (triple-big)
### Gobert+Naz+Randle

- **Stints:** 20  
- **Minutes:** 39.6  
- **Possessions (off/def):** 82 / 79  
- **Net rating:** **+10.88** (95% CI [-28.52, +55.42])  
- **Off rating:** 113.4  /  **Def rating:** 102.5  
- **Off 3PA rate:** 0.292  
- **fg3a per 100:** 25.6

**By series:**

```
series_label  stints_n  minutes  poss_off  poss_def  pts_for  pts_against   net
   R1_vs_DEN        11    24.66        52        48       60           55  0.80
   R2_vs_SAS         9    14.96        30        31       33           26 26.13
```

**By Edwards game-status (the game the stint was played in):**

```
edwards_status  stints_n  minutes  poss_off  poss_def  pts_for  pts_against   net
           DNP         9    24.25        51        46       58           53 -1.49
       Limited         4     5.68        13        10       17            4 90.77
        Normal         7     9.69        18        23       18           24 -4.35
```

**By Edwards on the floor (was Ant in this lineup_id):**

```
 edwards_on_floor  stints_n  minutes  poss_off  poss_def  pts_for  pts_against   net
            False        13    31.68        66        60       80           65 12.88
             True         7     7.95        16        19       13           16 -2.96
```

**Score margin at stint start (Wolves perspective):**

```
margin_at_start
Close (-2..+2)    5
Leading 10+       1
Leading 3-10      3
Trailing 10+      8
Trailing 3-10     3
```

