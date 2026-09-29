# N6: the Kuminga ledger

*As of 2026-09-17. Run `n6_kuminga_ledger_20260929T100505Z`. Tags: OBSERVED happened; MODELED comes out of the simulation or an impact view; ASSUMED is our choice.*

## What the signing makes better

| line | tag | number | sample |
|---|---|---|---|
| Signing Kuminga beats the most likely internal fill for his minutes (slot A, the default allocation, where Williams, Lyles and McDaniels absorb them): positive in every view on both aging bases and clearing every view's 200k floor | MODELED | +1.40 points un-aged [+1.11, +1.87]; +1.73 aged [+1.18, +2.45] | 200,000 sims per view per curve |
| As the primary defender on a top-150 scorer, Kuminga held him slightly below the norm, inside the noise (percentile 23 of 309 defenders; low is better) | OBSERVED | -0.037 beyond the norm, -1.3 SEs (2023-26) | 13 pairings, 711 possessions |
| But he is not a primary creator competing with Edwards and Ball for the same shots: below the high-usage line, and a middling self-creator | OBSERVED | usage 0.226 in 2025-26; unassisted share 0.44 (percentile 69), 0.39 over 2023-26 | 157 makes in 2025-26, 871 over 2023-26 |

## What it makes worse, or leaves uncertain

| line | tag | number | sample |
|---|---|---|---|
| If the real alternative was Beringer taking the minutes, the comparison runs the other way, and that also clears every floor on both bases | MODELED | -1.48 un-aged, -2.48 aged | 200,000 sims |
| Against Trey Lyles filling the slot the views split, so the verdict depends on who the alternative was | MODELED | +0.12 un-aged, +0.04 aged, MIXED both |  |
| As a scorer against the defender a team assigns him, Kuminga ran about at the norm, inside the noise (percentile 36 of 245 scorers), where Edwards sat at the very bottom (percentile 0): the primary-defender problem M3 found is Edwards', not his | OBSERVED | -0.005 beyond the norm, -0.2 SEs (2023-26); 2025-26 alone 3 pairings, too few | 29 pairings, 1415 possessions |
| Next to a non-shooting centre at Golden State, Kuminga's units were worse than without one but inside the noise, and took slightly fewer threes: the Gobert question in miniature | OBSERVED | net -2.1 against +0.6 per 100 (difference -2.7, game-bootstrap SE 3.5); three-point attempt rate 0.430 against 0.448 | 5,340 and 5,672 offensive possessions, 2022-26, garbage time out |
| Every playoff possession he has played, pooled: his teams were behind with him on the floor, and in the games where stints exist they were 16 points per 100 worse with him on than off, garbage time removed | OBSERVED | on-court net -16.2 per 100 (all 40 games); on -18.1, off -2.1, on-off -16.0 with a game-bootstrap SE of 8.4 (23 games) | 1,139 on-court possessions in all; 810 on and 1375 off in the stint games; small, and confounded by who else was on the floor |
| He adds to a usage crunch: the projected five with Kuminga in for Dosunmu sums to more usage than the typical starting five of every team-season since 2023-24 | OBSERVED rates, COMPOSED five | 1.150 (percentile 95.6) against 1.121 with Dosunmu; 1.177 at three-season rates | 7,380 league starting fives |
| The option is his, not Minnesota's: most views have him opting out after one season, and an opt-out leaves Minnesota only Non-Bird rights | MODELED option; OBSERVED terms | P(opt out) 0.53 to 0.84 across views (flat aging); Non-Bird ceiling $7,276,800 |  |

## Detail

**Slot variants, 200,000 sims, mean points of title odds [four-view range], views clearing the floor.**

| variant | who takes the minutes | un-aged | aged | ships |
|---|---|---|---|---|
| A_c3_default_shannon | Jaden McDaniels +2.7; Cody Williams +23.3 | +1.403 [+1.110, +1.868], 4/4 | +1.726 [+1.185, +2.448], 4/4 | yes |
| B_lyles_fills | Trey Lyles +26.1 | +0.120 [-0.839, +0.674], 4/4 | +0.043 [-0.945, +0.724], 4/4 | no |
| C_mcdaniels_slides | Jaden McDaniels +4.0; Cody Williams +22.1 | +1.344 [+1.019, +1.811], 4/4 | +1.659 [+1.086, +2.373], 4/4 | yes |
| D_beringer_fills | Joan Beringer +25.1; Jaden McDaniels +0.9 | -1.477 [-2.646, -0.485], 4/4 | -2.478 [-4.124, -1.061], 4/4 | yes |
| E_tight_rule_F_or_FC | Jaden McDaniels +2.7; Cody Williams +23.3 | +1.403 [+1.110, +1.868], 4/4 | +1.726 [+1.185, +2.448], 4/4 | yes |

**Primary defenders, M3 basis** (beyond the league norm for a team's heaviest rotation defender; scorer percentile is the share of reference scorers held MORE than him; defender percentile is the share of reference defenders who held scorers MORE than he did, so low is good for a defender).

| window | player | role | beyond norm | in SEs | percentile | pairings | possessions |
|---|---|---|---:|---:|---:|---:|---:|
| 2025-26 | Jonathan Kuminga | scorer | +0.034 | +0.5 | 62 of 150 | 3 *(thin)* | 140 |
| 2025-26 | Jonathan Kuminga | defender | -0.046 | -0.4 | 39 of 194 | 1 *(thin)* | 45 |
| 2025-26 | Anthony Edwards | scorer | -0.115 | -5.6 | 1 of 150 | 21 | 1451 |
| 2025-26 | Anthony Edwards | defender | +0.004 | +0.2 | 54 of 194 | 14 | 836 |
| 2023-26 pooled | Jonathan Kuminga | scorer | -0.005 | -0.2 | 36 of 245 | 29 | 1415 |
| 2023-26 pooled | Jonathan Kuminga | defender | -0.037 | -1.3 | 23 of 309 | 13 | 711 |
| 2023-26 pooled | Anthony Edwards | scorer | -0.090 | -8.6 | 0 of 245 | 72 | 5823 |
| 2023-26 pooled | Anthony Edwards | defender | -0.021 | -1.7 | 18 of 309 | 61 | 3817 |

**The Golden State analog** (garbage time out; per 100 possessions).

| Kuminga on the floor | window | offensive possessions | net | offence / defence | team 3PA rate |
|---|---|---:|---:|---|---:|
| with a non-shooting centre | 2022-23 | 1,607 | -8.6 | 115.6 / 124.2 | 0.464 |
| with a non-shooting centre | 2023-24 | 2,116 | +2.5 | 118.0 / 115.5 | 0.410 |
| with a non-shooting centre | 2024-25 | 1,543 | -1.2 | 111.6 / 112.8 | 0.417 |
| with a non-shooting centre | 2025-26 | 74 | -11.7 | 125.7 / 137.3 | 0.590 |
| with a non-shooting centre | 2022-26 pooled | 5,340 | -2.1 | 115.5 / 117.6 | 0.430 |
| without one | 2022-23 | 1,409 | +1.9 | 117.2 / 115.2 | 0.467 |
| without one | 2023-24 | 2,103 | +5.5 | 120.2 / 114.7 | 0.414 |
| without one | 2024-25 | 1,263 | -8.2 | 110.1 / 118.4 | 0.466 |
| without one | 2025-26 | 897 | -0.5 | 113.3 / 113.8 | 0.478 |
| without one | 2022-26 pooled | 5,672 | +0.6 | 116.1 / 115.5 | 0.448 |

**Every postseason game.**

| season | team | games | minutes | possessions | on-court net | usage | TS |
|---|---|---:|---:|---:|---:|---:|---:|
| 2021-22 | GSW | 16 | 138 | 298 | -11.2 | 0.258 | 0.581 |
| 2022-23 | GSW | 10 | 61 | 126 | -21.3 | 0.215 | 0.608 |
| 2024-25 | GSW | 8 | 187 | 392 | -15.7 | 0.267 | 0.572 |
| 2025-26 | ATL | 6 | 156 | 323 | -19.2 | 0.211 | 0.574 |
| all | ATL/GSW | 40 | 542 | 1139 | -16.2 | 0.243 | 0.578 |

**Confound check on the playoff number.** Garbage time removed and set against the same team with him off the floor, in the 23 playoff games with stints: on -18.1 per 100 (810 possessions), off -2.1 (1375), on-off -16.0 with a game-bootstrap standard error of 8.4. Garbage time does not explain the on-court figure. It is still a small sample, and on-off is confounded by who else shared the floor.

**The contract, in one paragraph.** Two years from the taxpayer mid-level exception: $6,064,000 in 2026-27 and $6,367,200 in 2027-28, a player option on the second year, $12,431,200 in all; the team release disclosed no terms, so these are reported figures. If he opts out in the summer of 2027, he has one season of service and Minnesota holds only Non-Bird rights, which cap a re-signing at 120% of the salary of the season he actually played: $7,276,800. If he opts in and plays 2027-28, he has two seasons of service and Minnesota holds Early Bird rights in 2028. The option model has him opting out with probability 0.53 to 0.84 across the views on flat aging, so the likeliest case is one season followed by a market Minnesota can only meet up to $7,276,800 without other cap room or an exception.
