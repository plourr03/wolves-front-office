# N5: fragility

*As of 2026-09-16. MODELLED: un-aged primary after the D70 fixes, series overlay off. Each player removed for the playoffs only; seeding from the full roster. Title odds from 3 seeds x 20,000 simulations per state, paired on seeds with the full-strength run. Simulation run `n5_fragility_20260919T233508Z`; doc run `n5_fragility_20260919T233508Z`.*

**In plain terms.** Take one of Minnesota's top three away for the playoffs and its title odds fall from 1.60% by 0.87 points on average, 54% of what it had. OKC falls from 14.71% by 6.04 points on average (41%); SAS falls from 13.73% by 6.04 points on average (44%). In strength, the three teams lose almost the same amount per removal on average (MIN 2.60, OKC 2.73, SAS 2.70 net points), but the contenders' loss sits in one player (Shai Gilgeous-Alexander 4.89, Victor Wembanyama 5.26) while Minnesota's is spread across three (its largest is Rudy Gobert, 3.09). Minnesota loses a bigger share of its odds mostly because it starts from 1.60%, where each point of net rating is a larger fraction of what it has. One caution on the order inside Minnesota: how much each loss costs is only as good as each view's rating of the player, and the views disagree most on Rudy Gobert (impact +0.78 to +5.01 across the four), and his drop runs from 0.55 to 1.32 points across them. With a tightened playoff rotation, MIN's loss shrinks (2.60 to 2.22), while OKC's and SAS's grow (2.73 to 3.01; 2.70 to 2.83), because tightening takes weak eleventh and twelfth men out of the replacement and takes a strong bench out with it. On that reading MIN loses the least strength per removal of the three. It is a sensitivity on net rating, not re-simulated title odds.

| team | out for the playoffs | title odds, full roster | without him | drop, points [four views] | share of the team's odds lost | West rank by title odds, full / without (per view) | team net lost | his impact / the next men's (consensus) | who absorbs his minutes (consensus) |
|---|---|---:|---:|---|---:|---|---:|---|---|
| MIN | Anthony Edwards | 1.60% | 0.76% | **0.85** [0.42, 1.72] | 52% | 8/6/7/6 / 8/8/7/7 | 2.13 [1.28, 3.32] | +2.66 / -0.18 | Isaiah Evans +13.0; Trey Lyles +9.0; Jaden McDaniels +2.9 |
| MIN | Rudy Gobert | 1.60% | 0.74% | **0.87** [0.55, 1.32] | 61% | 8/6/7/6 / 8/8/7/7 | 3.09 [0.96, 4.71] | +4.88 / -1.00 | Cody Williams +10.3; Trey Lyles +9.0; Ayo Dosunmu +4.8 |
| MIN | LaMelo Ball | 1.60% | 0.71% | **0.90** [0.53, 1.44] | 59% | 8/6/7/6 / 8/8/8/7 | 2.59 [1.57, 3.22] | +3.78 / -0.70 | Trey Lyles +9.0; Cody Williams +7.1; Ayo Dosunmu +4.8 |
| OKC | Shai Gilgeous-Alexander | 14.71% | 4.93% | **9.77** [8.84, 10.59] | 68% | 2/2/1/1 / 4/5/3/3 | 4.89 [3.36, 6.17] | +9.50 / +2.64 | Bennett Stirtz +15.4; Ajay Mitchell +3.0; Cason Wallace +3.0 |
| OKC | Chet Holmgren | 14.71% | 8.17% | **6.54** [4.61, 8.20] | 46% | 2/2/1/1 / 4/4/1/2 | 2.71 [1.51, 3.41] | +6.05 / +3.08 | Bennett Stirtz +15.0; Cason Wallace +2.2; Ajay Mitchell +2.2 |
| OKC | Jalen Williams | 14.71% | 12.89% | **1.81** [0.08, 2.90] | 12% | 2/2/1/1 / 2/2/1/1 | 0.59 [0.03, 0.92] | +2.65 / +3.31 | Bennett Stirtz +15.0; Cason Wallace +2.2; Ajay Mitchell +2.1 |
| OKC | Isaiah Hartenstein *(sensitivity)* | 14.71% | 11.18% | **3.52** [1.31, 4.49] | 25% | 2/2/1/1 / 2/3/1/1 | 1.34 [0.39, 1.88] | +4.53 / +2.94 | Bennett Stirtz +14.8; Cason Wallace +1.8; Ajay Mitchell +1.8 |
| SAS | Victor Wembanyama | 13.73% | 3.56% | **10.17** [5.76, 14.76] | 72% | 1/1/2/2 / 4/4/5/4 | 5.26 [3.40, 7.02] | +9.99 / +0.21 | Keldon Johnson +18.2; De'Aaron Fox +2.0; Devin Vassell +1.9 |
| SAS | De'Aaron Fox | 13.73% | 9.26% | **4.47** [1.55, 8.03] | 30% | 1/1/2/2 / 2/2/3/2 | 1.65 [0.74, 2.74] | +3.41 / +0.21 | Keldon Johnson +18.3; Devin Vassell +2.0; Julian Champagnie +1.9 |
| SAS | Tobias Harris | 13.73% | 10.26% | **3.47** [-0.33, 7.86] | 21% | 1/1/2/2 / 2/2/2/2 | 1.20 [-0.14, 2.67] | +3.24 / +0.06 | Keldon Johnson +18.2; Devin Vassell +1.9; Julian Champagnie +1.7 |
| SAS | Dylan Harper *(sensitivity)* | 13.73% | 9.38% | **4.35** [0.58, 9.11] | 27% | 1/1/2/2 / 2/3/2/2 | 1.59 [0.27, 3.25] | +4.27 / -0.66 | Keldon Johnson +18.0; Julian Champagnie +1.4; Luke Kornet +1.3 |

*West rank is listed per view, in the order consensus / RAPM / box / DARKO. Seed-to-seed noise on a drop, with the paired seeds, is at most 0.18 points (standard error across 3 seeds).*

| team | title odds, full | mean drop across its top three, points [views] | share of its odds | mean net lost per removal | largest single net loss |
|---|---:|---|---:|---:|---|
| MIN | 1.60% | 0.87 [0.53, 1.50] | 54% | 2.60 | Rudy Gobert, 3.09 |
| OKC | 14.71% | 6.04 [5.38, 7.09] | 41% | 2.73 | Shai Gilgeous-Alexander, 4.89 |
| SAS | 13.73% | 6.04 [2.33, 10.21] | 44% | 2.70 | Victor Wembanyama, 5.26 |

**Where the minutes go, and why it matters.** Each rotation is ten men, most of them close to their minute ceilings, so the allocator sends a removed player's minutes mostly to the eleventh and twelfth men rather than to the players already in the rotation. For Minnesota with Anthony Edwards out, the men who enter the rotation are Isaiah Evans +13.0; Trey Lyles +9.0. That is the pipeline's regular-season rule working as written, and a playoff rotation would not do it: it tightens, and the minutes go to the starters. Re-priced with the pipeline's own playoff rollup (top nine by minutes, rescaled to a full game), the mean net lost per removal is MIN 2.22, OKC 3.01, SAS 2.83, against MIN 2.60, OKC 2.73, SAS 2.70 on the regular-season rule.

**What it does not show.** The team's playoff variance is held at full-roster values. Injuries to more than one player, or to anyone outside the top three.

*Method.* Minutes: `rotation.allocate` with the player's availability at zero, ceiling rule on, reproducing the published rotation exactly before any removal (gate G2). Strength: net plus beta times the change in the minutes-weighted impact rollup, reproducing the published net exactly (G3). Simulation: `simulate_league` with seeding from full-strength nets and the playoff draw from the reduced net, reproducing the original draw for draw when nothing is removed (G4). Next men: minutes-weighted impact of the minutes each other player gains. Detail: `outputs/n5_fragility.csv`, `n5_next_man_up.csv`.
