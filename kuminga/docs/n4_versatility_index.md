# N4: versatility index

*As of 2026-09-16. Part 1 is MODELLED: 2026-27 strengths from the un-aged primary after the D70 fixes, series model with the style overlay off (M2). Part 2 is OBSERVED: regular seasons from `nba_games`. Run `n4_versatility_index_20260919T234720Z`.*

**In plain terms.** The index asks how much a team's chance of winning a series swings across the eight contenders. Under the series model this project uses, that swing is set entirely by the team's own net rating: for the 22 teams outside the field, ranking by swing is ranking by net rating (rank correlation 1.00 in every view). The model prices a series on the rating gap and home court and nothing else, so the index ranks where a team sits on the curve, not how versatile it is. HOU tops it because its rating sits among the contenders, where series are closest to coin flips; Minnesota ranks 16 of 30. **Minnesota's best matchup in the field is MIA (26%) and its worst BOS (10%); within each view that order is the order of the opponents' net ratings.**

The real question is whether versatility exists in the games themselves, which the model would then be missing. Across 15,669 regular-season games since 2013-14, the best estimate of a true, repeatable matchup effect (one team playing a particular opponent better than the ratings say) is **0.6 points per game**, and on 34,357 games since 1997-98 it is 0.0. On an even series those two estimates are worth about 5 and 0 points of series probability. The data cannot rule out an effect as large as 1.2 points per game (95% upper bound), which would be worth 9 points in an even series, so this is a small effect with a loose ceiling, not a proven zero. A team's spread of results across opponents does repeat from one season to the next (+0.26), but that is volatility, not versatility: how swingy a team's games are repeats more strongly (+0.30), and once it is removed the spread's repeat falls to -0.01.

## Part 1. The index as specified (MODELLED)

Field, top 8 by modelled title odds: BOS (18.3%), OKC (14.7%), SAS (13.9%), DET (7.8%), HOU (6.8%), DEN (6.2%), TOR (5.8%), MIA (4.6%). A contender is scored against the other seven.

| rank | team | net, 2026-27 | gap to field | spread (SD) [four views] | range | mean P(series) |
|---:|---|---:|---:|---|---:|---:|
| 1 | HOU (field) | +5.04 | -0.82 | 0.149 [0.129, 0.176] | 0.390 | 0.434 |
| 2 | SAS (field) | +7.19 | +1.33 | 0.140 [0.131, 0.147] | 0.395 | 0.615 |
| 3 | DET (field) | +5.38 | -0.48 | 0.133 [0.124, 0.151] | 0.380 | 0.464 |
| 4 | TOR (field) | +4.70 | -1.16 | 0.133 [0.082, 0.169] | 0.364 | 0.400 |
| 5 | OKC (field) | +7.43 | +1.57 | 0.120 [0.070, 0.175] | 0.323 | 0.647 |
| 6 | DEN (field) | +4.65 | -1.21 | 0.119 [0.077, 0.143] | 0.326 | 0.386 |
| 7 | MIA (field) | +4.11 | -1.75 | 0.112 [0.104, 0.132] | 0.347 | 0.340 |
| 8 | NYK | +3.72 | -2.14 | 0.104 [0.077, 0.127] | 0.296 | 0.329 |
| 9 | CHA | +3.22 | -2.64 | 0.100 [0.054, 0.125] | 0.287 | 0.304 |
| 10 | BOS (field) | +8.38 | +2.52 | 0.093 [0.070, 0.116] | 0.278 | 0.713 |
| 11 | PHI | +3.04 | -2.82 | 0.091 [0.071, 0.111] | 0.260 | 0.285 |
| 12 | ATL | +2.42 | -3.44 | 0.084 [0.073, 0.103] | 0.239 | 0.249 |
| 13 | LAL | +1.82 | -4.04 | 0.081 [0.063, 0.125] | 0.231 | 0.230 |
| 14 | CLE | +1.71 | -4.15 | 0.081 [0.060, 0.123] | 0.229 | 0.223 |
| 15 | POR | +1.39 | -4.47 | 0.073 [0.038, 0.092] | 0.208 | 0.204 |
| 16 | **MIN** | +1.02 | -4.84 | 0.066 [0.052, 0.077] | 0.187 | 0.184 |
| 17 | PHX | +0.69 | -5.17 | 0.062 [0.056, 0.068] | 0.176 | 0.170 |
| 18 | ORL | +0.22 | -5.64 | 0.057 [0.050, 0.068] | 0.162 | 0.149 |
| 19 | CHI | -2.20 | -8.06 | 0.033 [0.028, 0.038] | 0.093 | 0.075 |
| 20 | LAC | -2.81 | -8.67 | 0.028 [0.023, 0.040] | 0.080 | 0.062 |
| 21 | GSW | -2.95 | -8.81 | 0.028 [0.018, 0.045] | 0.079 | 0.064 |
| 22 | DAL | -3.01 | -8.87 | 0.027 [0.023, 0.029] | 0.074 | 0.057 |
| 23 | BKN | -4.04 | -9.90 | 0.023 [0.009, 0.044] | 0.064 | 0.047 |
| 24 | NOP | -4.02 | -9.87 | 0.020 [0.015, 0.027] | 0.056 | 0.042 |
| 25 | MIL | -4.60 | -10.46 | 0.017 [0.011, 0.026] | 0.048 | 0.034 |
| 26 | IND | -6.43 | -12.29 | 0.009 [0.006, 0.012] | 0.025 | 0.018 |
| 27 | SAC | -6.85 | -12.71 | 0.008 [0.005, 0.012] | 0.022 | 0.015 |
| 28 | MEM | -7.26 | -13.12 | 0.007 [0.004, 0.013] | 0.020 | 0.015 |
| 29 | WAS | -8.97 | -14.83 | 0.004 [0.001, 0.008] | 0.012 | 0.008 |
| 30 | UTA | -9.53 | -15.39 | 0.004 [0.001, 0.009] | 0.010 | 0.007 |

**Minnesota against the field** (P wins the series, four-view band):

| opponent | P(Minnesota wins) | four-view band | opponent net |
|---|---:|---|---:|
| MIA | **0.262** | 0.181 to 0.342 | +4.11 |
| TOR | **0.235** | 0.131 to 0.343 | +4.70 |
| DEN | **0.232** | 0.160 to 0.321 | +4.65 |
| HOU | **0.213** | 0.145 to 0.276 | +5.04 |
| DET | **0.191** | 0.175 to 0.215 | +5.38 |
| SAS | **0.130** | 0.063 to 0.196 | +7.19 |
| OKC | **0.111** | 0.078 to 0.133 | +7.43 |
| BOS | **0.098** | 0.034 to 0.158 | +8.38 |

Best matchup MIA, worst BOS. Within each view the order is exactly the order of the opponents' net ratings, and cannot be anything else under this model. Averaged across the four views the order can cross where a team's rating differs a lot between views: TOR's band runs from 0.13 to 0.34, the widest here, so 'best matchup' is a statement about the average of four views that disagree. The four-view bands on Minnesota's eight series are 0.04 to 0.21 wide.

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
