# N4: versatility index

*As of 2026-09-16. Part 1 is MODELLED: 2026-27 strengths from the un-aged primary after the D70 fixes, series model with the style overlay off (M2). Part 2 is OBSERVED: regular seasons from `nba_games`. Run `n4_versatility_index_20260916T213612Z`.*

**In plain terms.** The index asks how much a team's chance of winning a series swings across the eight contenders. Under the series model this project uses, that swing is set entirely by the team's own net rating: for the 22 teams outside the field, ranking by swing is ranking by net rating (rank correlation 1.00 in every view). The model prices a series on the rating gap and home court and nothing else, so the index ranks where a team sits on the curve, not how versatile it is. DET tops it because its rating sits among the contenders, where series are closest to coin flips; Minnesota ranks 15 of 30. **Minnesota's best matchup in the field is CHA (29%) and its worst OKC (10%); within each view that order is the order of the opponents' net ratings.**

The real question is whether versatility exists in the games themselves, which the model would then be missing. Across 15,669 regular-season games since 2013-14, the best estimate of a true, repeatable matchup effect (one team playing a particular opponent better than the ratings say) is **0.6 points per game**, and on 34,357 games since 1997-98 it is 0.0. On an even series those two estimates are worth about 5 and 0 points of series probability. The data cannot rule out an effect as large as 1.2 points per game (95% upper bound), which would be worth 9 points in an even series, so this is a small effect with a loose ceiling, not a proven zero. A team's spread of results across opponents does repeat from one season to the next (+0.26), but that is volatility, not versatility: how swingy a team's games are repeats more strongly (+0.30), and once it is removed the spread's repeat falls to -0.01.

## Part 1. The index as specified (MODELLED)

Field, top 8 by modelled title odds: BOS (17.0%), OKC (16.7%), SAS (13.9%), DET (8.1%), CHA (5.9%), HOU (5.4%), TOR (4.9%), DEN (4.7%). A contender is scored against the other seven.

| rank | team | net, 2026-27 | gap to field | spread (SD) [four views] | range | mean P(series) |
|---:|---|---:|---:|---|---:|---:|
| 1 | DET (field) | +5.29 | -0.15 | 0.160 [0.138, 0.180] | 0.451 | 0.492 |
| 2 | SAS (field) | +6.93 | +1.49 | 0.155 [0.144, 0.175] | 0.445 | 0.622 |
| 3 | TOR (field) | +4.05 | -1.39 | 0.149 [0.076, 0.187] | 0.413 | 0.381 |
| 4 | HOU (field) | +4.07 | -1.37 | 0.149 [0.120, 0.183] | 0.452 | 0.373 |
| 5 | NYK | +3.67 | -1.77 | 0.143 [0.130, 0.160] | 0.447 | 0.363 |
| 6 | CHA (field) | +4.14 | -1.30 | 0.141 [0.068, 0.189] | 0.381 | 0.401 |
| 7 | MIA | +3.66 | -1.78 | 0.140 [0.110, 0.172] | 0.444 | 0.359 |
| 8 | LAL | +2.90 | -2.54 | 0.132 [0.107, 0.148] | 0.406 | 0.316 |
| 9 | DEN (field) | +3.50 | -1.94 | 0.127 [0.097, 0.166] | 0.359 | 0.334 |
| 10 | PHI | +2.52 | -2.91 | 0.124 [0.069, 0.158] | 0.396 | 0.289 |
| 11 | OKC (field) | +7.65 | +2.21 | 0.123 [0.072, 0.171] | 0.363 | 0.690 |
| 12 | BOS (field) | +7.89 | +2.45 | 0.113 [0.094, 0.140] | 0.347 | 0.708 |
| 13 | ATL | +2.11 | -3.33 | 0.112 [0.075, 0.169] | 0.339 | 0.263 |
| 14 | CLE | +1.72 | -3.72 | 0.109 [0.084, 0.143] | 0.344 | 0.246 |
| 15 | **MIN** | +0.88 | -4.56 | 0.094 [0.062, 0.150] | 0.295 | 0.203 |
| 16 | PHX | +0.64 | -4.80 | 0.092 [0.067, 0.151] | 0.286 | 0.191 |
| 17 | ORL | +0.62 | -4.82 | 0.087 [0.070, 0.109] | 0.267 | 0.185 |
| 18 | POR | +0.25 | -5.19 | 0.080 [0.070, 0.089] | 0.248 | 0.172 |
| 19 | LAC | -1.88 | -7.32 | 0.054 [0.043, 0.068] | 0.166 | 0.096 |
| 20 | GSW | -2.19 | -7.63 | 0.050 [0.033, 0.074] | 0.158 | 0.092 |
| 21 | CHI | -2.36 | -7.80 | 0.050 [0.028, 0.086] | 0.156 | 0.085 |
| 22 | DAL | -3.78 | -9.22 | 0.034 [0.025, 0.054] | 0.107 | 0.054 |
| 23 | NOP | -4.71 | -10.15 | 0.029 [0.014, 0.061] | 0.092 | 0.044 |
| 24 | MEM | -5.17 | -10.61 | 0.025 [0.013, 0.048] | 0.078 | 0.035 |
| 25 | MIL | -5.18 | -10.61 | 0.023 [0.015, 0.032] | 0.071 | 0.035 |
| 26 | BKN | -5.31 | -10.75 | 0.023 [0.011, 0.033] | 0.070 | 0.033 |
| 27 | SAC | -6.42 | -11.86 | 0.017 [0.008, 0.034] | 0.054 | 0.023 |
| 28 | IND | -6.36 | -11.80 | 0.017 [0.010, 0.034] | 0.053 | 0.023 |
| 29 | UTA | -10.03 | -15.47 | 0.009 [0.001, 0.030] | 0.028 | 0.010 |
| 30 | WAS | -9.49 | -14.93 | 0.008 [0.002, 0.024] | 0.026 | 0.010 |

**Minnesota against the field** (P wins the series, four-view band):

| opponent | P(Minnesota wins) | four-view band | opponent net |
|---|---:|---|---:|
| CHA | **0.294** | 0.119 to 0.616 | +4.14 |
| DEN | **0.288** | 0.225 to 0.363 | +3.50 |
| TOR | **0.260** | 0.161 to 0.378 | +4.05 |
| HOU | **0.255** | 0.191 to 0.312 | +4.07 |
| DET | **0.189** | 0.172 to 0.204 | +5.29 |
| SAS | **0.133** | 0.066 to 0.209 | +6.93 |
| BOS | **0.102** | 0.047 to 0.163 | +7.89 |
| OKC | **0.101** | 0.064 to 0.129 | +7.65 |

Best matchup CHA, worst OKC. Within each view the order is exactly the order of the opponents' net ratings, and cannot be anything else under this model. Averaged across the four views the order can cross where a team's rating differs a lot between views: CHA's band runs from 0.12 to 0.62, the widest here, so 'best matchup' is a statement about the average of four views that disagree. The four-view bands on Minnesota's eight series are 0.03 to 0.50 wide.

## Part 2. Is there any versatility to measure? (OBSERVED)

| measure | 2013-14 to 2025-26 | 1997-98 to 2025-26 |
|---|---:|---:|
| regular-season games | 15,669 | 34,357 |
| team-pair-seasons with two or more meetings | 5,594 | 11,961 |
| variance of the true pair effect [95% interval] | +0.42 [-2.26, +3.15] | -0.05 [-1.63, +1.55] |
| **SD of the true matchup effect, points per game** | **0.65** (upper 1.77) | **0.00** (upper 1.25) |

| further checks, 2013-14 to 2025-26 | value |
|---|---|
| residual SD of a single game after home court and ratings | 13.06 points |
| pair residual, one half of meetings against the other | correlation +0.002 over 5,594 pair-seasons |
| even series with home court: point estimate (2013-26 / 1997-2026) / upper bound | 0.540 becomes 0.585 / 0.540 / 0.627 |
| team spread across opponents, season to next | +0.262 over 360 team pairs |
| team game-to-game volatility, season to next | +0.297 |
| team spread with volatility removed, season to next | -0.015 |
| team's own true-matchup-variance estimate, season to next | +0.021 |

**What it shows.** Under the model the piece uses, the versatility index is a restatement of net rating, and Minnesota's best and worst matchups are its weakest and strongest opponents in each view. In the games themselves, the best estimate of a repeatable matchup effect is small, and it comes from a test that assumes no style mechanism at all, so it agrees with M1 (style interactions carry nothing out of sample) and N3 (no style trait translates) from a different direction. **What it does not show.** That matchup effects are zero: the upper bound is loose enough that a real effect of up to 1.2 points per game, worth up to 9 points on an even series, is not ruled out. Playoff matchups, where a coach has a week to game-plan one opponent; the test uses regular-season meetings, two to four a season, and the playoffs have too few repeated pairs to estimate the same way. Effects specific to one pair, such as San Antonio's scheme against Edwards, which can be real and still leave the league-wide average near zero. And mid-season roster changes, which blur a pair's meetings.

*Definitions.* Field: top 8 by mean modelled title odds across the four views. Series probability: `bracket_sim.conditional_series`, overlay off, home court to the higher net. Spread: population standard deviation and range across the field. Residual: game margin minus home court and the rating gap, fitted per season, with each team's net computed without the games between that pair. True pair-effect variance: the mean cross-product of two different games' residuals within the same pair-season (independent game noise contributes zero), bootstrapped over pair-seasons (2000 resamples). Volatility: a team-season's residual SD across all its games. Per-game points are put on the series scale with the sim's resolver as if they were net-rating points. Detail: `outputs/n4_versatility_index.csv`, `n4_min_matchups.csv`, `n4_matchup_repeatability.csv`.
