# N5: fragility

*As of 2026-09-16. MODELLED: un-aged primary after the D70 fixes, series overlay off. Each player removed for the playoffs only; seeding from the full roster. Title odds from 3 seeds x 20,000 simulations per state, paired on seeds with the full-strength run. Simulation run `n5_fragility_20260916T220325Z`; doc run `n5_fragility_doc_20260916T221110Z`.*

**In plain terms.** Take one of Minnesota's top three away for the playoffs and its title odds fall from 1.66% by 0.82 points on average, 49% of what it had. The biggest single loss is Rudy Gobert (0.90 points). OKC falls from 16.73% by 6.20 points on average (37%); SAS falls from 13.76% by 5.11 points on average (37%). In strength, the three teams lose almost the same amount per removal on average (MIN 2.30, OKC 2.32, SAS 2.25 net points), but the contenders' loss sits in one player (Shai Gilgeous-Alexander 4.01, Victor Wembanyama 4.77) while Minnesota's is spread across three (its largest is Rudy Gobert, 3.25). Minnesota loses a bigger share of its odds mostly because it starts from 1.66%, where each point of net rating is a larger fraction of what it has. One caution on the order inside Minnesota: how much each loss costs is only as good as each view's rating of the player, and the views disagree most on Rudy Gobert (impact +0.77 to +5.76 across the four), and his drop runs from 0.61 to 1.32 points across them. With a tightened playoff rotation, MIN's loss shrinks (2.30 to 1.95), while OKC's and SAS's grow (2.32 to 2.52; 2.25 to 2.36), because tightening takes weak eleventh and twelfth men out of the replacement and takes a strong bench out with it. On that reading MIN loses the least strength per removal of the three. It is a sensitivity on net rating, not re-simulated title odds.

| team | out for the playoffs | title odds, full roster | without him | drop, points [four views] | share of the team's odds lost | West rank by title odds, full / without (per view) | team net lost | his impact / the next men's (consensus) | who absorbs his minutes (consensus) |
|---|---|---:|---:|---|---:|---|---:|---|---|
| MIN | Anthony Edwards | 1.66% | 0.93% | **0.74** [0.32, 1.71] | 41% | 8/7/6/6 / 8/8/7/7 | 1.70 [0.90, 3.32] | +1.88 / -0.18 | Isaiah Evans +13.0; Trey Lyles +9.0; Jaden McDaniels +2.9 |
| MIN | Rudy Gobert | 1.66% | 0.77% | **0.90** [0.61, 1.32] | 63% | 8/7/6/6 / 9/9/7/7 | 3.25 [0.94, 5.15] | +5.28 / -0.87 | Cody Williams +10.3; Trey Lyles +9.0; Ayo Dosunmu +4.8 |
| MIN | LaMelo Ball | 1.66% | 0.85% | **0.82** [0.39, 1.44] | 49% | 8/7/6/6 / 8/8/7/7 | 1.95 [1.51, 2.53] | +2.28 / -0.59 | Trey Lyles +9.0; Cody Williams +7.1; Ayo Dosunmu +4.8 |
| OKC | Shai Gilgeous-Alexander | 16.73% | 6.81% | **9.92** [8.03, 10.99] | 60% | 1/2/1/1 / 3/3/2/3 | 4.01 [2.80, 4.81] | +7.54 / +2.41 | Aday Mara +16.0; Ajay Mitchell +3.0; Cason Wallace +3.0 |
| OKC | Chet Holmgren | 16.73% | 10.35% | **6.37** [4.02, 8.56] | 38% | 1/2/1/1 / 2/2/1/2 | 2.26 [1.28, 2.89] | +4.82 / +2.77 | Aday Mara +15.6; Cason Wallace +2.2; Ajay Mitchell +2.2 |
| OKC | Jalen Williams | 16.73% | 14.43% | **2.30** [1.33, 2.84] | 14% | 1/2/1/1 / 2/2/1/1 | 0.71 [0.45, 0.93] | +2.78 / +2.89 | Aday Mara +15.5; Cason Wallace +2.1; Ajay Mitchell +2.1 |
| OKC | Isaiah Hartenstein *(sensitivity)* | 16.73% | 12.19% | **4.54** [1.70, 6.06] | 28% | 1/2/1/1 / 2/2/1/1 | 1.56 [0.50, 2.19] | +4.74 / +2.52 | Aday Mara +15.3; Cason Wallace +1.8; Ajay Mitchell +1.7 |
| SAS | Victor Wembanyama | 13.76% | 4.12% | **9.64** [5.23, 13.48] | 68% | 2/1/2/2 / 5/4/5/4 | 4.77 [3.00, 6.18] | +9.05 / +0.31 | Keldon Johnson +18.2; De'Aaron Fox +2.0; Julian Champagnie +1.8 |
| SAS | De'Aaron Fox | 13.76% | 10.69% | **3.07** [1.23, 4.79] | 21% | 2/1/2/2 / 2/2/2/2 | 1.10 [0.57, 1.56] | +2.34 / +0.37 | Keldon Johnson +18.3; Julian Champagnie +2.0; Stephon Castle +1.9 |
| SAS | Tobias Harris | 13.76% | 11.16% | **2.61** [-0.57, 5.85] | 15% | 2/1/2/2 / 2/2/2/2 | 0.88 [-0.25, 1.97] | +2.68 / +0.24 | Keldon Johnson +18.2; Julian Champagnie +1.8; Stephon Castle +1.8 |
| SAS | Dylan Harper *(sensitivity)* | 13.76% | 10.16% | **3.60** [0.47, 7.31] | 23% | 2/1/2/2 / 2/2/2/2 | 1.28 [0.20, 2.55] | +3.58 / -0.39 | Keldon Johnson +18.0; Stephon Castle +1.4; Luke Kornet +1.3 |

*West rank is listed per view, in the order consensus / RAPM / box / DARKO. Seed-to-seed noise on a drop, with the paired seeds, is at most 0.24 points (standard error across 3 seeds).*

| team | title odds, full | mean drop across its top three, points [views] | share of its odds | mean net lost per removal | largest single net loss |
|---|---:|---|---:|---:|---|
| MIN | 1.66% | 0.82 [0.45, 1.49] | 49% | 2.30 | Rudy Gobert, 3.25 |
| OKC | 16.73% | 6.20 [4.77, 7.42] | 37% | 2.32 | Shai Gilgeous-Alexander, 4.01 |
| SAS | 13.76% | 5.11 [1.96, 8.04] | 37% | 2.25 | Victor Wembanyama, 4.77 |

**Where the minutes go, and why it matters.** Each rotation is ten men, most of them close to their minute ceilings, so the allocator sends a removed player's minutes mostly to the eleventh and twelfth men rather than to the players already in the rotation. For Minnesota with Anthony Edwards out, the men who enter the rotation are Isaiah Evans +13.0; Trey Lyles +9.0. That is the pipeline's regular-season rule working as written, and a playoff rotation would not do it: it tightens, and the minutes go to the starters. Re-priced with the pipeline's own playoff rollup (top nine by minutes, rescaled to a full game), the mean net lost per removal is MIN 1.95, OKC 2.52, SAS 2.36, against MIN 2.30, OKC 2.32, SAS 2.25 on the regular-season rule.

**What it does not show.** The team's playoff variance is held at full-roster values. Injuries to more than one player, or to anyone outside the top three. And the aged basis, which is run separately once the chain refreshes `outputs/aged/`; until then these numbers carry the un-aged label.

*Method.* Minutes: `rotation.allocate` with the player's availability at zero, ceiling rule on, reproducing the published rotation exactly before any removal (gate G2). Strength: net plus beta times the change in the minutes-weighted impact rollup, reproducing the published net exactly (G3). Simulation: `simulate_league` with seeding from full-strength nets and the playoff draw from the reduced net, reproducing the original draw for draw when nothing is removed (G4). Next men: minutes-weighted impact of the minutes each other player gains. Detail: `outputs/n5_fragility.csv`, `n5_next_man_up.csv`.
