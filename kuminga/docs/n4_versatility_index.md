# N4: versatility index

*As of 2026-09-16. Part 1 is MODELLED: 2026-27 strengths from the un-aged primary after the D70 fixes, series model with the style overlay off (M2). Part 2 is OBSERVED: regular seasons from `nba_games`. Run `n4_versatility_index_20260929T181847Z`.*

**In plain terms.** The index asks how much a team's chance of winning a series swings across the eight contenders. Under the series model this project uses, that swing is set entirely by the team's own net rating: for the 22 teams outside the field, ranking by swing is ranking by net rating (rank correlation 1.00 in every view). The model prices a series on the rating gap and home court and nothing else, so the index ranks where a team sits on the curve, not how versatile it is. SAS tops it because its rating sits among the contenders, where series are closest to coin flips; Minnesota ranks 14 of 30. **Minnesota's best matchup in the field is HOU (33%) and its worst BOS (14%); within each view that order is the order of the opponents' net ratings.**

The real question is whether versatility exists in the games themselves, which the model would then be missing. Across 15,669 regular-season games since 2013-14, the best estimate of a true, repeatable matchup effect (one team playing a particular opponent better than the ratings say) is **0.6 points per game**, and on 34,357 games since 1997-98 it is 0.0. On an even series those two estimates are worth about 5 and 0 points of series probability. The data cannot rule out an effect as large as 1.2 points per game (95% upper bound), which would be worth 9 points in an even series, so this is a small effect with a loose ceiling, not a proven zero. A team's spread of results across opponents does repeat from one season to the next (+0.26), but that is volatility, not versatility: how swingy a team's games are repeats more strongly (+0.30), and once it is removed the spread's repeat falls to -0.01.

## Part 1. The index as specified (MODELLED)

Field, top 8 by modelled title odds: BOS (18.1%), OKC (14.7%), SAS (13.8%), DET (7.8%), DEN (6.1%), TOR (5.8%), HOU (5.4%), MIA (5.1%). A contender is scored against the other seven.

| rank | team | net, 2026-27 | gap to field | spread (SD) [four views] | range | mean P(series) |
|---:|---|---:|---:|---|---:|---:|
| 1 | SAS (field) | +7.19 | +1.39 | 0.142 [0.134, 0.147] | 0.396 | 0.620 |
| 2 | TOR (field) | +4.70 | -1.10 | 0.138 [0.083, 0.173] | 0.363 | 0.411 |
| 3 | DET (field) | +5.37 | -0.43 | 0.136 [0.128, 0.150] | 0.383 | 0.468 |
| 4 | MIA (field) | +4.36 | -1.44 | 0.132 [0.106, 0.159] | 0.378 | 0.377 |
| 5 | HOU (field) | +4.33 | -1.47 | 0.124 [0.107, 0.139] | 0.350 | 0.367 |
| 6 | DEN (field) | +4.65 | -1.15 | 0.121 [0.082, 0.146] | 0.323 | 0.391 |
| 7 | OKC (field) | +7.43 | +1.64 | 0.121 [0.072, 0.175] | 0.324 | 0.651 |
| 8 | CHA | +3.37 | -2.43 | 0.110 [0.058, 0.132] | 0.333 | 0.321 |
| 9 | NYK | +3.72 | -2.08 | 0.107 [0.080, 0.135] | 0.298 | 0.336 |
| 10 | BOS (field) | +8.36 | +2.56 | 0.094 [0.071, 0.117] | 0.279 | 0.716 |
| 11 | PHI | +3.08 | -2.72 | 0.093 [0.070, 0.114] | 0.264 | 0.292 |
| 12 | ATL | +2.47 | -3.32 | 0.086 [0.075, 0.103] | 0.242 | 0.255 |
| 13 | LAL | +2.07 | -3.73 | 0.085 [0.068, 0.125] | 0.241 | 0.245 |
| 14 | **MIN** | +2.41 | -3.39 | 0.084 [0.076, 0.094] | 0.236 | 0.254 |
| 15 | CLE | +1.71 | -4.09 | 0.082 [0.063, 0.123] | 0.230 | 0.226 |
| 16 | POR | +1.39 | -4.41 | 0.074 [0.040, 0.092] | 0.209 | 0.207 |
| 17 | PHX | +0.75 | -5.05 | 0.064 [0.060, 0.069] | 0.179 | 0.174 |
| 18 | ORL | +0.33 | -5.46 | 0.060 [0.054, 0.068] | 0.167 | 0.156 |
| 19 | CHI | -2.03 | -7.83 | 0.035 [0.028, 0.039] | 0.098 | 0.080 |
| 20 | LAC | -2.80 | -8.60 | 0.029 [0.024, 0.041] | 0.081 | 0.064 |
| 21 | GSW | -2.95 | -8.75 | 0.028 [0.018, 0.045] | 0.079 | 0.065 |
| 22 | DAL | -3.04 | -8.84 | 0.027 [0.024, 0.029] | 0.074 | 0.057 |
| 23 | BKN | -3.98 | -9.78 | 0.024 [0.010, 0.044] | 0.066 | 0.049 |
| 24 | NOP | -3.72 | -9.52 | 0.022 [0.018, 0.031] | 0.062 | 0.047 |
| 25 | MIL | -4.54 | -10.33 | 0.018 [0.011, 0.028] | 0.050 | 0.036 |
| 26 | IND | -6.01 | -11.81 | 0.011 [0.009, 0.014] | 0.029 | 0.020 |
| 27 | SAC | -6.85 | -12.64 | 0.008 [0.005, 0.013] | 0.022 | 0.016 |
| 28 | MEM | -6.88 | -12.68 | 0.008 [0.005, 0.012] | 0.022 | 0.015 |
| 29 | UTA | -9.46 | -15.26 | 0.004 [0.001, 0.010] | 0.011 | 0.008 |
| 30 | WAS | -9.48 | -15.28 | 0.004 [0.001, 0.007] | 0.010 | 0.007 |

**Minnesota against the field** (P wins the series, four-view band):

| opponent | P(Minnesota wins) | four-view band | opponent net |
|---|---:|---|---:|
| HOU | **0.330** | 0.282 to 0.372 | +4.33 |
| MIA | **0.330** | 0.246 to 0.391 | +4.36 |
| DEN | **0.311** | 0.247 to 0.398 | +4.65 |
| TOR | **0.310** | 0.209 to 0.401 | +4.70 |
| DET | **0.266** | 0.239 to 0.312 | +5.37 |
| SAS | **0.180** | 0.110 to 0.249 | +7.19 |
| OKC | **0.162** | 0.134 to 0.181 | +7.43 |
| BOS | **0.138** | 0.063 to 0.213 | +8.36 |

Best matchup HOU, worst BOS. Within each view the order is exactly the order of the opponents' net ratings, and cannot be anything else under this model. Averaged across the four views the order can cross where a team's rating differs a lot between views: TOR's band runs from 0.21 to 0.40, the widest here, so 'best matchup' is a statement about the average of four views that disagree. The four-view bands on Minnesota's eight series are 0.05 to 0.19 wide.

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
