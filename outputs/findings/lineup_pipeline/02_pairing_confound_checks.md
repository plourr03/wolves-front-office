# Confound checks: Gobert+Naz and Gobert+Randle pairings
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

- **Stints:** 76  
- **Minutes:** 203.8  
- **Possessions (off/def):** 412 / 406  
- **Net rating:** **-13.26** (95% CI [-27.94, +1.50])  
- **Off rating:** 97.6  /  **Def rating:** 110.8  
- **Off 3PA rate:** 0.325  
- **fg3a per 100:** 29.6

**By series:**

```
series_label  stints_n  minutes  poss_off  poss_def  pts_for  pts_against    net
   R1_vs_DEN        40   115.03       230       230      233          240  -3.04
   R2_vs_SAS        36    88.73       182       176      169          210 -26.46
```

**By Edwards game-status (the game the stint was played in):**

```
edwards_status  stints_n  minutes  poss_off  poss_def  pts_for  pts_against    net
           DNP        13    29.73        55        56       52           65 -21.53
       Limited        27    76.32       157       155      153          166  -9.64
        Normal        36    97.70       200       195      197          219 -13.81
```

**By Edwards on the floor (was Ant in this lineup_id):**

```
 edwards_on_floor  stints_n  minutes  poss_off  poss_def  pts_for  pts_against    net
            False        30    77.70       158       156      154          175 -14.71
             True        46   126.05       254       250      248          275 -12.36
```

**Score margin at stint start (Wolves perspective):**

```
margin_at_start
Close (-2..+2)    28
Leading 10+        6
Leading 3-10      11
Trailing 10+      15
Trailing 3-10     16
```

## Cohort C: All three bigs on floor (triple-big)
### Gobert+Naz+Randle

- **Stints:** 19  
- **Minutes:** 33.2  
- **Possessions (off/def):** 67 / 65  
- **Net rating:** **+22.53** (95% CI [-28.26, +63.14])  
- **Off rating:** 117.9  /  **Def rating:** 95.4  
- **Off 3PA rate:** 0.238  
- **fg3a per 100:** 22.4

**By series:**

```
series_label  stints_n  minutes  poss_off  poss_def  pts_for  pts_against   net
   R1_vs_DEN        10    18.28        37        34       46           36 18.44
   R2_vs_SAS         9    14.96        30        31       33           26 26.13
```

**By Edwards game-status (the game the stint was played in):**

```
edwards_status  stints_n  minutes  poss_off  poss_def  pts_for  pts_against   net
           DNP         8    17.87        36        32       44           34 15.97
       Limited         4     5.68        13        10       17            4 90.77
        Normal         7     9.69        18        23       18           24 -4.35
```

**By Edwards on the floor (was Ant in this lineup_id):**

```
 edwards_on_floor  stints_n  minutes  poss_off  poss_def  pts_for  pts_against   net
            False        12    25.29        51        46       66           46 29.41
             True         7     7.95        16        19       13           16 -2.96
```

**Score margin at stint start (Wolves perspective):**

```
margin_at_start
Close (-2..+2)    4
Leading 10+       1
Leading 3-10      3
Trailing 10+      8
Trailing 3-10     3
```

