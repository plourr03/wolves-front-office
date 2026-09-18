# Piece 2 skeleton: the season preview

**Status: restructured into eight sections. Rendered from `piece_v2_skeleton.template.md` by `render_piece.py`; every number comes from `outputs/final_numbers.csv` by key, and `reconcile_figures.py` fails if a digit reaches this page any other way.**

**Labelling rule.** `[observed]` happened and is in the data. `[composed]` is a real measurement recombined by us. `[modeled]` comes out of the simulation or an impact view. `[assumed]` is our choice and the piece says so. Run IDs for every figure are on the sheet.

**Framing rule for every market comparison: never "the odds were wrong."** The market is a prior. The piece shows how good a prior it is and what information moved the winners inside it.

**Structural rule: no section ends in a verdict.** Each ends with its number and the condition that number depends on.

---

## 1. The number

Minnesota's modelled title probability for the season is **1.69% `[modeled, run_sim]`**, four-view band **0.82% to 2.62%**, on the un-aged basis. On the survivorship-corrected aged basis it is **2.55% `[modeled, run_sim]`**, band 1.29% to 3.73%: aging helps Minnesota because Minnesota is young, so the piece quotes both. The market says **3.16% `[observed, market_devig]`, 6th**, after removing a 21.8% overround proportionally.

**The disagreement is all-views on the primary basis, and holds in rank on both.** On the un-aged basis every one of the four views prices Minnesota below the market and ranks it in the range 13 to 16 against the market's 6th `[modeled, f4_per_view_disagreement]`; the market's number sits outside the model's whole band. On the aged basis every view still ranks Minnesota below the market (9 to 15), but 2 of the four views price it above the market's 3.16% (box 3.33%, DARKO 3.73%), so in probability the aged disagreement is **mixed** `[modeled, r5_honesty_rail_bases]`. The piece can say the model ranks Minnesota lower than the market does on both bases; it cannot say every view prices Minnesota below the market on both.

**The honesty rail.** The model and the market order the league at a rank correlation of **0.78 to 0.82** across the four views, 0.77 to 0.80 on the aged basis `[composed, market_devig, r5_honesty_rail_bases]`. They agree about the shape of the league and disagree about 20 specific teams, and **16 of those 20 are all-views**, where every view sits on the same side of the market; on the aged basis it is 15 of 17. The disagreements do not trace to a single fixable defect (F1). The four views are not independent instruments either: consensus and RAPM move together, so "all four agree" is a check that a finding does not hinge on one modelling choice, never a confidence interval.

**The model's biggest falsifiable claim is Boston.** The model makes Boston a **17.00% `[modeled, market_devig]`** title team against a market price of **5.47%**, and it does so in every view; on the aged basis it is 13.49%, still all-views. Named, with a date: **if Boston's net rating through its 30th game, around the end of December, is below -1.5 per 100 possessions, the market's read of Boston beats the model's** `[composed, n8_watch_list]`. The model's own range for Boston is +3.5 to +9.0, and a 30-game net rating carries about 3.1 points of pure chance, so the threshold sits where chance alone would rarely put a team the model has right. The same field prices every Minnesota number, so a Boston miss is a Minnesota caveat too.

**The 7 verdicts that ship** hold their sign in all four cells of the rule, two aging bases by two minutes allocators, and clear every view's noise floor in each, at 200,000 simulations per view `[modeled, w2_aging_gate, noise_floor, r7_allocator_agreement]`. It was 9 before the corrections below, out of 13 candidates.

| verdict | un-aged, mean points of title odds | aged | sign, un-aged / aged | views clearing, un-aged, aged |
|---|---:|---:|---|---|
| LaMelo Ball in | +0.68 | +0.78 | all positive / all positive | 4/4, 4/4 |
| Naz Reid out | -0.42 | -0.51 | all negative / all negative | 4/4, 4/4 |
| DiVincenzo's Achilles (not a transaction) | -0.42 | -0.33 | all negative / all negative | 4/4, 4/4 |
| Kuminga slot, default allocation | +0.52 | +0.58 | all positive / all positive | 4/4, 4/4 |
| Kuminga slot, McDaniels slides | +0.50 | +0.56 | all positive / all positive | 4/4, 4/4 |
| Kuminga slot, Beringer fills | -1.13 | -1.94 | all negative / all negative | 4/4, 4/4 |
| Kuminga slot, tight eligibility rule | +0.50 | +0.56 | all positive / all positive | 4/4, 4/4 |

*Notes.* Two of the 7 are Minnesota's own transactions (Ball in, Reid out). One is an injury, which ships as a cost and is not a verdict on the front office. Four compare Kuminga against different internal alternatives for his minutes: positive against three of them, negative against Beringer. A view "clears" when its value is larger than its noise floor in either direction, so a verdict can clear every view and still fail on sign. **The allocator test is the newest of the four cells and it changed nothing:** the same seven survive whether minutes are allocated team-wide, as the headline simulation does, or inside position groups, as the attribution layer does, and the count on the looser two-cell rule is the same 7 `[modeled, r7_allocator_agreement]`. The sizes do move with the allocator, which is why the table gives the pooled figures and the appendix gives both.

**What no longer ships, and why.** Until this pass the decomposition priced every combination of moves on a roster without Cody Williams, the player the Green trade brought back, and without the rule that gives new arrivals their minutes. Priced with the headline simulation's own minutes rule, its version of the actual roster sat 1.24 points of title odds from that simulation on the un-aged basis; it now sits within 0.08 on either basis, which is interpolation. The pooled rule the verdicts use spreads minutes across more of the bench by design and sits up to 0.83 below. With both corrected, 3 verdicts that shipped no longer do `[modeled, r5_shapley_williams]`:

| verdict | un-aged, mean points of title odds | aged | sign, un-aged / aged | views clearing, un-aged, aged |
|---|---:|---:|---|---|
| Other departures (a bundle of seven) | +0.36 | +0.71 | mixed / all positive | 4/4, 4/4 |
| Julius Randle out | +0.07 | +0.34 | all positive / all positive | 2/4, 4/4 |
| Ayo Dosunmu re-signed | -0.16 | -0.22 | mixed / mixed | 3/4, 3/4 |

None of the three survives the allocator cell either: under the headline's own minutes rule other departures is -0.51 un-aged against +0.36 pooled, Randle out turns negative (-0.22), and Dosunmu re-signed stays mixed `[modeled, r7_allocator_agreement]`. The departures bundle is seven players; split into them, 0 ships on its own, and Kyle Anderson comes closest (+0.08 un-aged, +0.37 aged, views clearing 3/4, 4/4) `[modeled, r2_departures]`. Randle out's history of flips is in the appendix.

**The number, and the condition:** 1.69% modelled (2.55% aged) against 3.16% priced; the model ranks Minnesota lower than the market on both bases, the gap in probability is all-views only un-aged, and it is only as trustworthy as a model that also makes Boston a 17.00% team, which December will test.

---

## 2. What the odds get right

**The things argued about in September are mostly unmeasurable, and the tests say so.**

**Style matchups.** Style interactions fixed in advance, fitted on two seasons and held out, made predictions **worse**: held-out mean absolute error rose by 0.0151 on 1,225 regular-season games and by 0.0265 on 251 postseason games `[modeled, m1_style_model]`. The San Antonio thesis could not be estimated from this data, and the series model runs without a style overlay.

**Playoff translation, and "defense travels."** Nothing tested translates. Eight candidate features, fixed before the fit, on 195 playoff series going back to the 2014 postseason: **0 of 8** add out-of-sample signal once the test allows for trying eight things at once, and that sample could detect an effect of about 0.95 to 1.15 points per game `[modeled, n3_playoff_translation]`. **"Defense travels" is not supported, and the estimate points the other way:** at equal net rating, a team whose rating leans on defense did **-0.85 points per game** in its series per standard deviation (standard error 0.34, p 0.011 against a bar of 0.0063). Its single-test interval tops out at -0.18. Earlier and recent history agree (-0.87 and -0.86), and three-point luck does not explain it (-0.77 with luck added). It misses the bar, so it changes nothing in the model.

**Versatility.** Under the series model the piece uses, a team's swing in series odds across the contender field is net rating restated (rank correlation 1.00 outside the field) `[modeled, n4_versatility_index]`. In the games themselves, a repeatable matchup effect is worth about 0.65 points per game since the 2013-14 season and 0.00 over 34,357 games since 1997-98, with a ceiling of 1.25, worth at most 9 points of series probability in an even series `[observed]`.

**Individual matchups.** A pairing of thirty possessions carries a standard error of 0.14 points per matchup possession, and a team's main defender on a star normally holds him 0.05 to 0.10 below his average. Judged against that norm, 2 of 79 observed West-field matchups beat it by two standard errors, where chance alone gives about 2.3 `[observed, m3_opponent_cards]`.

**Champions, as honest counts.** Across the 3 clean seasons the preseason favourite won **1 of 3**, and the champion came from the market's top five **3 of 3**, priced between 8.27% and 14.69% `[observed, champions_table]`. Set against the 14 top-five teams that did not win, only 3 of 20 features separate the champions: offensive rank, defensive rank and continuity. No style feature does `[observed, h1_h3_h5_profile]`.

**The Knicks, the last champion.** The market had them at **8.27%, 4th, 53.5 wins**; they won 53. This project's model had them at 4.63% `[observed, h4_knicks_case_file]`. The regular season was steady: +6.33 per game, +6.16 before the break and +6.67 after. Then the playoffs were a different team: **16-3 at +14.89**, and they were the only one of 16 playoff teams whose margin improved (+8.57, against an average of -7.39; Minnesota's was -9.19). What moved was not visible in September. Their top five players missed 46 regular-season games and 2 in the playoffs; the top five's share of minutes went from 0.579 to 0.673; and the bracket broke their way.

**The number, and the condition:** 0 of 8 translation features survive, and the conclusion rests on the belief that what decided last year's title (health, a shortened rotation, a bracket) was not knowable until April.

---

## 3. What the odds can't see, and what it means for Minnesota

**Health and fragility.** Take one of Minnesota's top three players away for the playoffs and its title odds fall by **0.82 points on average, 49% of what it has** (38% aged); Oklahoma City loses 6.20 (37%) and San Antonio 5.11 (37%) `[modeled, n5_fragility]`. In strength the three lose about the same per player: **2.30, 2.32 and 2.25 points of net rating**. The contenders' loss sits in one star (Shai Gilgeous-Alexander 4.01, Victor Wembanyama 4.77); Minnesota's is spread across the three. With a tightened playoff rotation Minnesota loses the least of the three: 1.95 against 2.52 and 2.36. On the aged basis Minnesota loses 1.77 per player against 2.25 and 2.06, so the spread-not-concentrated reading holds on both bases. **Which Minnesota player is costliest to lose does not hold on both bases, and the piece does not name one.**

**The rotation.** The model gives Cody Williams **16.1 minutes a night** `[assumed, build_rotations]`. He is the lowest-ranked of the ten men who play, **0.0101** behind Jaylen Clark on the rank score that orders the rotation (Williams 0.3041, Clark 0.3142) `[composed, build_rotations]`. With DiVincenzo out, both play; with DiVincenzo healthy, the man cut is Williams, and he plays none. That gap is the whole difference between 16.1 minutes and zero. **Below 12.0 minutes a night, the four views stop agreeing that the offseason made Minnesota worse** `[modeled, williams_minutes_sensitivity]`. Double-big lineups can now be evaluated: 161 of 749 legal fives use two bigs, and 294 play without Gobert `[composed, m4_lineup_study]`. Every one of the 10 best-graded fives includes Joan Beringer, whose rating rests on a rookie season of 7.9 minutes a game: **those fives are composed, not observed, and rest on a rookie sample.** Only 5 of the 749 fives have ever played together. Last season's two Gobert frontcourts were level on correct points: +3.2 with Reid and +3.3 with Randle per 100 possessions `[observed, lineup_evidence]`.

**Usage.** Last season's usage does not fit on one floor. The projected top five adds up to the **87th percentile** of 7,380 league starting fives; with Kuminga in for Dosunmu it is the **96th**, and the **98th** at three-season rates. Last season's actual five was the 56th `[composed, m5_usage_accounting]`. New star pairings have cost usage, not efficiency: at the level where Edwards and Ball sit, **-1.5 points of usage (standard error 0.9) and +0.8 of true shooting**, on only 9 cases `[observed]`.

**The path.** Minnesota's most likely seed is **7th (27%)**, and its chance of a top-six seed is **44%** `[modeled, seed_distribution]`. Its first-round opponent is San Antonio or Oklahoma City **51%** of the time, the two teams it beats least. It reaches the second round 28% of the time, and once there wins the title 6.0% of the time: **title equity is a first-round problem** `[modeled, n2_path]`.

**The number, and the condition:** losing any one of its top three costs Minnesota about 49% of its title odds on average (38% aged), and every rotation figure above depends on Williams' 16.1 minutes surviving a coaching staff.

---

## 4. Kuminga, better and worse

**Better.**

- **He beats the most likely internal fill for his minutes** `[modeled, slot_robustness]`: +0.52 points of title odds un-aged and +0.58 aged, positive in every view and clearing every view's floor on both bases (4/4, 4/4) at 200,000 simulations. It clears on size, not just sign.
- **As a defender assigned to a top scorer**, he held scorers slightly below the norm: percentile 23 of 309 defenders, where low is good (-1.3 standard errors, inside the noise; 13 pairings, 711 possessions) `[observed, n6_kuminga_ledger]`.
- **He is not a primary creator competing for Edwards' and Ball's shots:** usage 0.226 last season, below the high-usage line, with 44% of his makes unassisted (percentile 69, on 157 makes) `[observed]`.

**Worse, or uncertain.**

- **The slot verdict depends on who the alternative was.** If Beringer took those minutes instead, the comparison runs the other way: -1.13 un-aged and -1.94 aged, and that also clears `[modeled]`.
- **As a scorer against the defender a team assigns him**, he sits about at the norm: percentile 36 of 245 (-0.2 standard errors, 29 pairings, 1,415 possessions over three seasons; last season alone gives 3 pairings, too few) `[observed]`.
- **Next to a non-shooting centre at Golden State**, his units were -2.1 per 100 possessions against +0.6 without one, on 5,340 and 5,672 possessions, with a three-point attempt rate of 0.430 against 0.448. The gap is inside the noise (standard error 3.5), but it is the Gobert question in miniature `[observed]`.
- **In the playoffs, all of it pooled:** 40 games and 1,139 possessions, **on-court net -16.2**. In the 23 games with lineup data, with garbage time removed, his team was -16.0 per 100 possessions worse with him on than off (standard error 8.4). Small, and confounded by who else was on the floor, but not explained by blowouts `[observed]`.
- **He adds to the crunch:** the projected five with him in is the 96th-percentile usage five `[composed]`.

**The contract, in one paragraph.** Two years from the taxpayer mid-level exception: **$6,064,000** this season and **$6,367,200** next, a player option on the second year, $12,431,200 in all; the team release disclosed no terms, so these are reported figures `[observed]`. If he opts out after one season, he has one season of service and Minnesota holds only Non-Bird rights, which cap a re-signing at **$7,276,800**. If he opts in and plays both, Minnesota holds Early Bird rights. The option model has him opting out with probability **0.50 to 0.80** across the views `[modeled, player_option]`.

**The number, and the condition:** +0.52 points of title odds against the default fill, conditional on the alternative not being Beringer and on one season that the option may make the only one.

---

## 5. Edwards, and why Ball is here

**Edwards is the most guardable star one-on-one.** Across the league last season, the defender a team assigned to Edwards held him further under his own level than that assignment holds almost any other scorer: **percentile 1 of 150 top scorers**, -5.6 standard errors over 21 pairings `[observed, m3_primary_defender_check]`. It survives both confound checks: a baseline built only from rotation defenders (percentile 1) and dropping the playoffs (percentile 5; both together, 5). Over three seasons he is the **lowest of 245 scorers** (percentile 0, -8.6 standard errors, 72 pairings) `[observed, n6_kuminga_ledger]`.

**The creators.** Edwards made **61%** of his baskets unassisted (percentile 95), Ball **55%** (percentile 84), and Dosunmu 35%, at the league median of 35% `[observed, m5_usage_accounting]`.

**The pairing base rate.** New high-usage pairings cost usage, not efficiency: adjusted for who the players were, -0.4 points of usage and -0.1 of true shooting across 34 player-seasons, and -1.5 and +0.8 at the star level where Edwards (0.309) and Ball (0.306) sit `[observed]`.

**The argument.** If a team's assigned defender can hold Edwards this reliably, the fix is not a better Edwards but a second creator the assignment cannot also cover. That is why Ball is here, and the base rate says the pairing should cost shots, not efficiency.

**The number, and the condition:** percentile 1 as a scorer against his assigned defender, and the argument holds only if Ball draws that assignment often enough to loosen it.

---

## 6. Clutch

**In the last five minutes of a close game, everyone gets worse and more baskets come unassisted.** Across the league since the 2023-24 season, effective shooting falls from **0.544 to 0.502** and the unassisted share of makes rises from **37% to 45%** `[observed, n7_late_clock]`. Of 22 creators with enough clutch shots, **2** beat that drop by two standard errors (Derrick White +2.3, Jamal Murray +2.0), where chance alone gives about 1.0. Edwards shot 0.546 on 306 clutch attempts (+1.3 standard errors beyond the drop) and Ball 0.460 on 100 (-0.1): **both inside the noise.**

*Late clock, withheld.* Play-by-play does not record the shot clock, and the reconstruction read within two seconds of zero at recorded violations only 79.9% of the time against a bar of 80% set in advance, so no late-clock split is published.

**The number, and the condition:** 2 of 22 creators beat the clutch drop, about what chance gives.

---

## 7. What to watch

Five claims, each checked at a team's 20th game, late November `[composed, n8_watch_list]`.

| claim | now | flips if |
|---|---|---|
| Cody Williams' minutes decide whether the offseason verdict holds | 16.1 a night (model default) | **below 12.0 a night** |
| Minnesota's level is inside the model's range | model range -1.7 to +1.8 (four views, both aging bases) | **above +7.5 or below -7.5** |
| The model's two largest disagreements with the market | BOS: model 17.0% title odds vs market 5.5%, model net range +3.5 to +9.0. SAS: model 13.9% vs market 23.0%, range +4.1 to +8.1 | **BOS below -2.2; SAS above +13.8** |
| The Edwards-Ball pairing costs usage, not efficiency | 2025-26 true shooting: Edwards 0.617, Ball 0.546. Unadjusted base rate for a new high-usage pairing: -0.3 points of true shooting (34 player-seasons) | **Edwards below 0.547, or Ball below 0.476** |
| Minnesota is not on a champion's path | projected rank 15 (un-aged) / 14 (aged); the 29 champions since 1997-98 ranked 11 at worst after 20 games (2005-06 MIA and 2022-23 DEN), median 2 | **3 or better (test); 11 or better (checkpoint)** |

**The number, and the condition:** 12.0 minutes of Cody Williams is the threshold that moves the headline verdict, and it depends on a rotation decision no one has made yet.

---

## 8. The bill

**The cap chain closes to the dollar** `[observed, green_resolution]`: $217,621,829, minus Green's $14,679,012, plus Williams at $6,015,600 and Konchar at $6,165,000, minus $4,110,000 for stretching Konchar, minus $1 for the McDaniels rounding, equals **$211,013,416**. Add Kuminga's $6,064,000 and it is **$217,077,416**: **$4,608,584 under the hard cap** and **$8,062,416 over the first apron**.

**What the Green dump cost: no pick and no swap, either direction.** Cash, and $2,055,000 a year of Konchar dead money for three seasons, $4,110,000 of it landing in the two seasons after this one `[observed, green_asset_cost]`. Minnesota holds Cody Williams in return, with a club option of $7,669,890.

**Dosunmu forced the dump, not the acquisition.** With Dosunmu, Green and Kuminga all on the books Minnesota was **$1,999,829 over the hard cap**, so something had to go. But the cheapest legal version of that move, a minimum player instead of Williams and Konchar, left Minnesota at $210,364,580 and about $8.7M of tax; what happened left it at $217,077,416 and about $23.3M. **Taking Williams and Konchar back cost $6,712,836 of payroll and about $14.6M more tax** `[observed, dosunmu_final_states]`. Not re-signing Dosunmu at all would have kept Green, added a minimum guard, and let Minnesota pay Kuminga up to $8,254,095 from the non-taxpayer mid-level, landing exactly on the first apron with about $7.0M of tax.

**The option.** $6,064,000 now, $6,367,200 next season at his choice, and a Non-Bird ceiling of $7,276,800 if he leaves after one.

**The number, and the condition:** $4,608,584 of hard-cap room for the whole league year, enough for one minimum addition if nothing goes wrong.

---

## Appendix

**What could not be estimated.** The late-clock split (withheld, section 6). A style overlay for series (section 2). Pre-playoff odds and every odds-history column before the clean seasons, left open for a pasted source. Earlier lineup findings built on the shared stint pipeline's point columns, which credited part of each team's points to the other team. The library is fixed and the postmortem figures are recomputed (D88); what remains is the possession-grain version of the same defect, which reaches RAPM and is not re-fitted.

**Tail players behind the model's biggest disagreements** (impact per view, no caps, no edits) `[modeled, f4_per_view_disagreement]`:

| player | possessions | consensus | RAPM | box | DARKO |
|---|---:|---:|---:|---:|---:|
| Derrick White (BOS) | 34,187 | +4.50 | +4.52 | +1.59 | +2.00 |
| Jayson Tatum (BOS) | 27,912 | +4.32 | +4.06 | +1.81 | +4.00 |
| Neemias Queta (BOS) | 12,078 | +4.52 | +4.97 | +1.61 | +2.00 |
| Payton Pritchard (BOS) | 28,044 | +2.75 | +3.08 | +0.86 | +1.00 |
| Paul George (BOS) | 22,107 | +2.69 | +2.54 | +0.91 | +1.00 |
| Mitchell Robinson (BOS) | 11,805 | +2.88 | +2.50 | +1.55 | +3.00 |
| Moussa Diabate (CHA) | 10,786 | +6.29 | +6.29 | +0.51 | +1.00 |
| Kon Knueppel (CHA) | 10,074 | +3.70 | +4.10 | +0.90 | +0.00 |
| Naz Reid (CHA) | 29,463 | +3.15 | +3.27 | +0.87 | +1.00 |
| Cade Cunningham (DET) | 30,366 | +3.63 | +3.34 | +0.99 | +4.00 |
| Ausar Thompson (DET) | 21,715 | +3.39 | +3.57 | +1.13 | +1.00 |
| Paul Reed (DET) | 11,888 | +3.82 | +3.67 | +2.57 | +2.00 |
| Javonte Green (DET) | 12,133 | +2.41 | +2.56 | +0.95 | +1.00 |
| Amen Thompson (HOU) | 28,927 | +3.48 | +3.11 | +1.09 | +1.00 |
| Alperen Sengun (HOU) | 29,974 | +2.37 | +2.37 | +1.45 | +2.00 |
| Tari Eason (HOU) | 15,866 | +3.08 | +3.68 | +1.38 | +2.00 |
| Steven Adams (HOU) | 7,157 | +3.22 | +4.20 | +0.20 | +2.00 |
| Marcus Smart (HOU) | 13,546 | +2.27 | +3.27 | -0.17 | +1.00 |
| Kevin Durant (HOU) | 32,027 | +1.78 | +1.02 | +1.06 | +3.00 |
| Pascal Siakam (IND) | 34,405 | +3.22 | +3.75 | +1.23 | +1.00 |
| Ivica Zubac (IND) | 24,588 | +2.74 | +2.61 | +0.67 | +2.00 |
| Karl-Anthony Towns (NYK) | 33,296 | +3.85 | +3.86 | +1.20 | +3.00 |
| Jalen Brunson (NYK) | 36,515 | +2.70 | +2.75 | +1.15 | +3.00 |
| OG Anunoby (NYK) | 32,031 | +2.65 | +2.80 | +0.58 | +4.00 |
| Miles McBride (NYK) | 18,664 | +3.03 | +3.84 | +0.13 | +1.00 |
| Josh Hart (NYK) | 35,827 | +2.13 | +1.64 | -0.04 | +0.00 |
| Shai Gilgeous-Alexander (OKC) | 37,420 | +7.54 | +6.82 | +4.22 | +6.00 |
| Chet Holmgren (OKC) | 30,933 | +4.82 | +4.78 | +2.50 | +5.00 |
| Isaiah Hartenstein (OKC) | 24,440 | +4.74 | +4.69 | +1.36 | +3.00 |
| Jalen Williams (OKC) | 24,660 | +2.78 | +1.92 | +1.65 | +2.00 |
| Alex Caruso (OKC) | 21,281 | +4.26 | +4.22 | +1.90 | +2.00 |
| Ajay Mitchell (OKC) | 9,940 | +2.81 | +2.94 | +0.83 | +1.00 |
| Jaylin Williams (OKC) | 9,600 | +2.63 | +1.72 | +1.76 | +1.00 |
| Joel Embiid (PHI) | 14,567 | +4.70 | +3.56 | +2.58 | +4.00 |
| Tyrese Maxey (PHI) | 31,485 | +2.69 | +2.31 | +1.69 | +3.00 |
| Dean Wade (PHI) | 16,627 | +3.73 | +4.72 | +0.24 | +1.00 |
| LeBron James (PHI) | 28,286 | +2.77 | +1.27 | +1.52 | +2.00 |
| Victor Wembanyama (SAS) | 24,823 | +9.05 | +8.88 | +4.85 | +6.00 |
| Dylan Harper (SAS) | 8,520 | +3.58 | +4.15 | +0.91 | +1.00 |
| Tobias Harris (SAS) | 29,161 | +2.68 | +3.02 | +0.24 | +1.00 |
| Luke Kornet (SAS) | 17,657 | +3.84 | +3.52 | +1.74 | +1.00 |
| De'Aaron Fox (SAS) | 31,481 | +2.34 | +2.39 | +1.42 | +2.00 |
| Julian Champagnie (SAS) | 24,840 | +1.96 | +2.54 | +0.65 | +2.00 |
| Kawhi Leonard (TOR) | 23,329 | +5.95 | +5.94 | +2.48 | +6.00 |
| Scottie Barnes (TOR) | 28,956 | +2.82 | +1.82 | +1.71 | +2.00 |
| Immanuel Quickley (TOR) | 20,531 | +1.59 | +1.14 | +1.31 | +1.00 |

**The market against each view, for the largest disagreements and Minnesota** (title odds) `[modeled]`:

| team | market | consensus | RAPM | box | DARKO | views |
|---|---:|---:|---:|---:|---:|---|
| MIN | 3.16% | 0.82% | 1.20% | 2.11% | 2.62% | ALL-VIEWS |
| BOS | 5.47% | 19.28% | 20.49% | 13.27% | 14.94% | ALL-VIEWS |
| HOU | 1.61% | 5.03% | 5.09% | 5.27% | 6.41% | ALL-VIEWS |
| SAS | 22.96% | 16.15% | 17.52% | 9.77% | 12.12% | ALL-VIEWS |
| PHI | 8.42% | 3.62% | 2.78% | 0.53% | 3.01% | ALL-VIEWS |
| NYK | 8.21% | 3.71% | 3.86% | 6.08% | 3.59% | ALL-VIEWS |
| OKC | 22.49% | 16.31% | 15.05% | 17.58% | 17.92% | ALL-VIEWS |
| DET | 3.16% | 5.02% | 5.17% | 10.48% | 11.76% | ALL-VIEWS |
| CHA | 0.81% | 8.21% | 9.44% | 5.20% | 0.58% | MIXED |

**Why "the offseason made Minnesota worse" does not ship.** The published offseason delta is -1.25 points un-aged and all-negative, but -0.39 and mixed on the aged basis, so it fails the rule that a verdict holds on both. It also carries two things the front office did not choose. The decomposition prices every state on the interpolation curve, where the same delta is -0.965: take out the DiVincenzo injury (+1.728) and the Williams minutes (+1.029), which overlap completely (-1.029, because a healthy DiVincenzo is what takes Williams' minutes), and the remainder is **+0.762**, mixed across views `[modeled, w1c_decompose]`.

**The seven shipping verdicts under both allocators** (mean points of title odds, pooled un-aged / pooled aged / team-rank un-aged / team-rank aged, then views clearing in each cell) `[modeled, r7_allocator_agreement]`:

| verdict | pooled, un-aged | pooled, aged | team-rank, un-aged | team-rank, aged | views clearing in each cell |
|---|---:|---:|---:|---:|---|
| LaMelo Ball in | +0.68 | +0.78 | +1.36 | +1.33 | 4/4, 4/4, 4/4, 4/4 |
| Naz Reid out | -0.42 | -0.51 | -1.08 | -1.11 | 4/4, 4/4, 4/4, 4/4 |
| DiVincenzo's Achilles (not a transaction) | -0.42 | -0.33 | -0.91 | -0.73 | 4/4, 4/4, 4/4, 4/4 |
| Kuminga slot, default allocation | +0.44 | +0.57 | +0.52 | +0.58 | 4/4, 4/4, 4/4, 4/4 |
| Kuminga slot, McDaniels slides | +0.41 | +0.55 | +0.50 | +0.56 | 4/4, 4/4, 4/4, 4/4 |
| Kuminga slot, Beringer fills | -0.81 | -1.42 | -1.13 | -1.94 | 4/4, 4/4, 4/4, 4/4 |
| Kuminga slot, tight eligibility rule | +0.44 | +0.57 | +0.50 | +0.56 | 4/4, 4/4, 4/4, 4/4 |

Kuminga's minutes are 25.2 under the headline's rule and 22.0 under the pooled one, which is most of why the slot sizes differ between the two.

**Randle out's flip history.** All-positive under the first minutes rules (D29). Mixed once the slot-aware allocator arrived, and it lost its quotable label (D31). All-positive again on the aged basis, when it was still held back as unstable (D52). All-positive on team-rank curve indexing, which became primary (D60). It has held its sign on both aging bases since the aging gate (D65), cleared every floor at full simulation count (D69), survived the D70 fixes (D77) and the departures split (D81). **It stopped shipping at D85**, when Cody Williams entered every coalition and new arrivals got their minutes by the headline's rule: +0.07 un-aged, +0.34 aged, views clearing 2/4, 4/4. Under the headline's team-rank allocator it turns negative un-aged, so its sign is not stable either.
