# Piece 2 skeleton: the season preview

**Status: restructured into eight sections. Rendered from `piece_v2_skeleton.template.md` by `render_piece.py`; every number comes from `outputs/final_numbers.csv` by key, and `reconcile_figures.py` fails if a digit reaches this page any other way.**

**Labelling rule.** `[observed]` happened and is in the data. `[composed]` is a real measurement recombined by us. `[modeled]` comes out of the simulation or an impact view. `[assumed]` is our choice and the piece says so. Run IDs for every figure are on the sheet.

**Framing rule for every market comparison: never "the odds were wrong."** The market is a prior. The piece shows how good a prior it is and what information moved the winners inside it.

**Structural rule: no section ends in a verdict.** Each ends with its number and the condition that number depends on.

---

## 1. The number

Minnesota's modelled title probability for the season is **⟦⟧ `[tag]`**, four-view band **⟦⟧ to ⟦⟧**, on the un-aged basis. On the survivorship-corrected aged basis it is **⟦⟧ `[tag]`**, band ⟦⟧ to ⟦⟧: aging helps Minnesota because Minnesota is young, so the piece quotes both. The market says **⟦⟧ `[tag]`, ⟦⟧th**, after removing a ⟦⟧ overround proportionally.

**The disagreement is all-views on the primary basis, and holds in rank on both.** On the un-aged basis every one of the four views prices Minnesota below the market and ranks it in the range ⟦⟧ against the market's ⟦⟧th `[modeled, f4_per_view_disagreement]`; the market's number sits outside the model's whole band. On the aged basis every view still ranks Minnesota below the market (⟦⟧), but ⟦⟧ of the four views price it above the market's ⟦⟧ (box ⟦⟧, DARKO ⟦⟧), so in probability the aged disagreement is **⟦⟧** `[modeled, r5_honesty_rail_bases]`. The piece can say the model ranks Minnesota lower than the market does on both bases; it cannot say every view prices Minnesota below the market on both.

**The honesty rail.** The model and the market order the league at a rank correlation of **⟦⟧ to ⟦⟧** across the four views, ⟦⟧ to ⟦⟧ on the aged basis `[composed, market_devig, r5_honesty_rail_bases]`. They agree about the shape of the league and disagree about ⟦⟧ specific teams, and **⟦⟧ of those ⟦⟧ are all-views**, where every view sits on the same side of the market; on the aged basis it is ⟦⟧ of ⟦⟧. The disagreements do not trace to a single fixable defect (F1). The four views are not independent instruments either: consensus and RAPM move together, so "all four agree" is a check that a finding does not hinge on one modelling choice, never a confidence interval.

**The model's biggest falsifiable claim is Boston.** The model makes Boston a **⟦⟧ `[tag]`** title team against a market price of **⟦⟧**, and it does so in every view; on the aged basis it is ⟦⟧, still ⟦⟧. Named, with a date: **if Boston's net rating through its ⟦⟧th game, around the end of December, is below ⟦⟧ per ⟦⟧ possessions, the market's read of Boston beats the model's** `[composed, n8_watch_list]`. The model's own range for Boston is ⟦⟧ to ⟦⟧, and a ⟦⟧-game net rating carries about ⟦⟧ points of pure chance, so the threshold sits where chance alone would rarely put a team the model has right. The same field prices every Minnesota number, so a Boston miss is a Minnesota caveat too.

**The ⟦⟧ verdicts that ship** hold their sign in all four cells of the rule, two aging bases by two minutes allocators, and clear every view's noise floor in each, at ⟦⟧ simulations per view `[modeled, w2_aging_gate, noise_floor, r7_allocator_agreement]`. It was ⟦⟧ before the corrections below, out of ⟦⟧ candidates.

| verdict | un-aged, mean points of title odds | aged | sign, un-aged / aged | views clearing, un-aged, aged |
|---|---:|---:|---|---|
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |

*Notes.* Two of the ⟦⟧ are Minnesota's own transactions (Ball in, Reid out). One is an injury, which ships as a cost and is not a verdict on the front office. Four compare Kuminga against different internal alternatives for his minutes: positive against three of them, negative against Beringer. A view "clears" when its value is larger than its noise floor in either direction, so a verdict can clear every view and still fail on sign. **The allocator test is the newest of the four cells and it changed nothing:** the same seven survive whether minutes are allocated team-wide, as the headline simulation does, or inside position groups, as the attribution layer does, and the count on the looser two-cell rule is the same ⟦⟧ `[modeled, r7_allocator_agreement]`. The sizes do move with the allocator, which is why the table gives the pooled figures and the appendix gives both.

**What no longer ships, and why.** Until this pass the decomposition priced every combination of moves on a roster without Cody Williams, the player the Green trade brought back, and without the rule that gives new arrivals their minutes. Priced with the headline simulation's own minutes rule, its version of the actual roster sat ⟦⟧ points of title odds from that simulation on the un-aged basis; it now sits within ⟦⟧ on either basis, which is interpolation. The pooled rule the verdicts use spreads minutes across more of the bench by design and sits up to ⟦⟧ below. With both corrected, ⟦⟧ verdicts that shipped no longer do `[modeled, r5_shapley_williams]`:

| verdict | un-aged, mean points of title odds | aged | sign, un-aged / aged | views clearing, un-aged, aged |
|---|---:|---:|---|---|
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |

None of the three survives the allocator cell either: under the headline's own minutes rule other departures is ⟦⟧ un-aged against ⟦⟧ pooled, Randle out turns negative (⟦⟧), and Dosunmu re-signed stays mixed `[modeled, r7_allocator_agreement]`. The departures bundle is seven players; split into them, ⟦⟧ ships on its own, and Kyle Anderson comes closest (⟦⟧ un-aged, ⟦⟧ aged, views clearing ⟦⟧) `[modeled, r2_departures]`. Randle out's history of flips is in the appendix.

**The number, and the condition:** ⟦⟧ modelled (⟦⟧ aged) against ⟦⟧ priced; the model ranks Minnesota lower than the market on both bases, the gap in probability is all-views only un-aged, and it is only as trustworthy as a model that also makes Boston a ⟦⟧ team, which December will test.

---

## 2. What the odds get right

**The things argued about in September are mostly unmeasurable, and the tests say so.**

**Style matchups.** Style interactions fixed in advance, fitted on two seasons and held out, made predictions **worse**: held-out mean absolute error rose by ⟦⟧ on ⟦⟧ regular-season games and by ⟦⟧ on ⟦⟧ postseason games `[modeled, m1_style_model]`. The San Antonio thesis could not be estimated from this data, and the series model runs without a style overlay.

**Playoff translation, and "defense travels."** Nothing tested translates. Eight candidate features, fixed before the fit, on ⟦⟧ playoff series going back to the ⟦⟧ postseason: **⟦⟧ of ⟦⟧** add out-of-sample signal once the test allows for trying eight things at once, and that sample could detect an effect of about ⟦⟧ to ⟦⟧ points per game `[modeled, n3_playoff_translation]`. **"Defense travels" is not supported, and the estimate points the other way:** at equal net rating, a team whose rating leans on defense did **⟦⟧ points per game** in its series per standard deviation (standard error ⟦⟧, p ⟦⟧ against a bar of ⟦⟧). Its single-test interval tops out at ⟦⟧. Earlier and recent history agree (⟦⟧ and ⟦⟧), and three-point luck does not explain it (⟦⟧ with luck added). It misses the bar, so it changes nothing in the model.

**Versatility.** Under the series model the piece uses, a team's swing in series odds across the contender field is net rating restated (rank correlation ⟦⟧ outside the field) `[modeled, n4_versatility_index]`. In the games themselves, a repeatable matchup effect is worth about ⟦⟧ points per game since the ⟦⟧ season and ⟦⟧ over ⟦⟧ games since ⟦⟧, with a ceiling of ⟦⟧, worth at most ⟦⟧ points of series probability in an even series `[observed]`.

**Individual matchups.** A pairing of thirty possessions carries a standard error of ⟦⟧ points per matchup possession, and a team's main defender on a star normally holds him ⟦⟧ to ⟦⟧ below his average. Judged against that norm, ⟦⟧ of ⟦⟧ observed West-field matchups beat it by two standard errors, where chance alone gives about ⟦⟧ `[observed, m3_opponent_cards]`.

**Champions, as honest counts.** Across the ⟦⟧ clean seasons the preseason favourite won **⟦⟧ of ⟦⟧**, and the champion came from the market's top five **⟦⟧ of ⟦⟧**, priced between ⟦⟧ and ⟦⟧ `[observed, champions_table]`. Set against the ⟦⟧ top-five teams that did not win, only ⟦⟧ of ⟦⟧ features separate the champions: offensive rank, defensive rank and continuity. No style feature does `[observed, h1_h3_h5_profile]`.

**The Knicks, the last champion.** The market had them at **⟦⟧, ⟦⟧th, ⟦⟧ wins**; they won ⟦⟧. This project's model had them at ⟦⟧ `[observed, h4_knicks_case_file]`. The regular season was steady: ⟦⟧ per game, ⟦⟧ before the break and ⟦⟧ after. Then the playoffs were a different team: **⟦⟧ at ⟦⟧**, and they were the only one of ⟦⟧ playoff teams whose margin improved (⟦⟧, against an average of ⟦⟧; Minnesota's was ⟦⟧). What moved was not visible in September. Their top five players missed ⟦⟧ regular-season games and ⟦⟧ in the playoffs; the top five's share of minutes went from ⟦⟧ to ⟦⟧; and the bracket broke their way.

**The number, and the condition:** ⟦⟧ of ⟦⟧ translation features survive, and the conclusion rests on the belief that what decided last year's title (health, a shortened rotation, a bracket) was not knowable until April.

---

## 3. What the odds can't see, and what it means for Minnesota

**Health and fragility.** Take one of Minnesota's top three players away for the playoffs and its title odds fall by **⟦⟧ points on average, ⟦⟧ of what it has** (⟦⟧ aged); Oklahoma City loses ⟦⟧ (⟦⟧) and San Antonio ⟦⟧ (⟦⟧) `[modeled, n5_fragility]`. In strength the three lose about the same per player: **⟦⟧, ⟦⟧ and ⟦⟧ points of net rating**. The contenders' loss sits in one star (⟦⟧ ⟦⟧, ⟦⟧ ⟦⟧); Minnesota's is spread across the three. With a tightened playoff rotation Minnesota loses the least of the three: ⟦⟧ against ⟦⟧ and ⟦⟧. On the aged basis Minnesota loses ⟦⟧ per player against ⟦⟧ and ⟦⟧, so the spread-not-concentrated reading holds on both bases. **Which Minnesota player is costliest to lose does not hold on both bases, and the piece does not name one.**

**The rotation.** The model gives Cody Williams **⟦⟧ minutes a night** `[assumed, build_rotations]`. He is the lowest-ranked of the ten men who play, **⟦⟧** behind Jaylen Clark on the rank score that orders the rotation (Williams ⟦⟧, Clark ⟦⟧) `[composed, build_rotations]`. With DiVincenzo out, both play; with DiVincenzo healthy, the man cut is Williams, and he plays none. That gap is the whole difference between ⟦⟧ minutes and zero. **Below ⟦⟧ minutes a night, the four views stop agreeing that the offseason made Minnesota worse** `[modeled, williams_minutes_sensitivity]`. Double-big lineups can now be evaluated: ⟦⟧ of ⟦⟧ legal fives use two bigs, and ⟦⟧ play without Gobert `[composed, m4_lineup_study]`. Every one of the ⟦⟧ best-graded fives includes Joan Beringer, whose rating rests on a rookie season of ⟦⟧ minutes a game: **those fives are composed, not observed, and rest on a rookie sample.** Only ⟦⟧ of the ⟦⟧ fives have ever played together. Last season's two Gobert frontcourts were level on correct points: ⟦⟧ with Reid and ⟦⟧ with Randle per ⟦⟧ possessions `[observed, lineup_evidence]`.

**Usage.** Last season's usage does not fit on one floor. The projected top five adds up to the **⟦⟧th percentile** of ⟦⟧ league starting fives; with Kuminga in for Dosunmu it is the **⟦⟧th**, and the **⟦⟧th** at three-season rates. Last season's actual five was the ⟦⟧th `[composed, m5_usage_accounting]`. New star pairings have cost usage, not efficiency: at the level where Edwards and Ball sit, **⟦⟧ points of usage (standard error ⟦⟧) and ⟦⟧ of true shooting**, on only ⟦⟧ cases `[observed]`.

**The path.** Minnesota's most likely seed is **⟦⟧ (⟦⟧)**, and its chance of a top-six seed is **⟦⟧** `[modeled, seed_distribution]`. Its first-round opponent is San Antonio or Oklahoma City **⟦⟧** of the time, the two teams it beats least. It reaches the second round ⟦⟧ of the time, and once there wins the title ⟦⟧ of the time: **title equity is a first-round problem** `[modeled, n2_path]`.

**The number, and the condition:** losing any one of its top three costs Minnesota about ⟦⟧ of its title odds on average (⟦⟧ aged), and every rotation figure above depends on Williams' ⟦⟧ minutes surviving a coaching staff.

---

## 4. Kuminga, better and worse

**Better.**

- **He beats the most likely internal fill for his minutes** `[modeled, slot_robustness]`: ⟦⟧ points of title odds un-aged and ⟦⟧ aged, positive in every view and clearing every view's floor on both bases (⟦⟧) at ⟦⟧ simulations. It clears on size, not just sign.
- **As a defender assigned to a top scorer**, he held scorers slightly below the norm: percentile ⟦⟧ of ⟦⟧ defenders, where low is good (⟦⟧ standard errors, inside the noise; ⟦⟧ pairings, ⟦⟧ possessions) `[observed, n6_kuminga_ledger]`.
- **He is not a primary creator competing for Edwards' and Ball's shots:** usage ⟦⟧ last season, below the high-usage line, with ⟦⟧ of his makes unassisted (percentile ⟦⟧, on ⟦⟧ makes) `[observed]`.

**Worse, or uncertain.**

- **The slot verdict depends on who the alternative was.** If Beringer took those minutes instead, the comparison runs the other way: ⟦⟧ un-aged and ⟦⟧ aged, and that also clears `[modeled]`.
- **As a scorer against the defender a team assigns him**, he sits about at the norm: percentile ⟦⟧ of ⟦⟧ (⟦⟧ standard errors, ⟦⟧ pairings, ⟦⟧ possessions over three seasons; last season alone gives ⟦⟧ pairings, too few) `[observed]`.
- **Next to a non-shooting centre at Golden State**, his units were ⟦⟧ per ⟦⟧ possessions against ⟦⟧ without one, on ⟦⟧ and ⟦⟧ possessions, with a three-point attempt rate of ⟦⟧ against ⟦⟧. The gap is inside the noise (standard error ⟦⟧), but it is the Gobert question in miniature `[observed]`.
- **In the playoffs, all of it pooled:** ⟦⟧ games and ⟦⟧ possessions, **on-court net ⟦⟧**. In the ⟦⟧ games with lineup data, with garbage time removed, his team was ⟦⟧ per ⟦⟧ possessions worse with him on than off (standard error ⟦⟧). Small, and confounded by who else was on the floor, but not explained by blowouts `[observed]`.
- **He adds to the crunch:** the projected five with him in is the ⟦⟧th-percentile usage five `[composed]`.

**The contract, in one paragraph.** Two years from the taxpayer mid-level exception: **⟦⟧** this season and **⟦⟧** next, a player option on the second year, ⟦⟧ in all; the team release disclosed no terms, so these are reported figures `[observed]`. If he opts out after one season, he has one season of service and Minnesota holds only Non-Bird rights, which cap a re-signing at **⟦⟧**. If he opts in and plays both, Minnesota holds Early Bird rights. The option model has him opting out with probability **⟦⟧ to ⟦⟧** across the views `[modeled, player_option]`.

**The number, and the condition:** ⟦⟧ points of title odds against the default fill, conditional on the alternative not being Beringer and on one season that the option may make the only one.

---

## 5. Edwards, and why Ball is here

**Edwards is the most guardable star one-on-one.** Across the league last season, the defender a team assigned to Edwards held him further under his own level than that assignment holds almost any other scorer: **percentile ⟦⟧ of ⟦⟧ top scorers**, ⟦⟧ standard errors over ⟦⟧ pairings `[observed, m3_primary_defender_check]`. It survives both confound checks: a baseline built only from rotation defenders (percentile ⟦⟧) and dropping the playoffs (percentile ⟦⟧; both together, ⟦⟧). Over three seasons he is the **lowest of ⟦⟧ scorers** (percentile ⟦⟧, ⟦⟧ standard errors, ⟦⟧ pairings) `[observed, n6_kuminga_ledger]`.

**The creators.** Edwards made **⟦⟧** of his baskets unassisted (percentile ⟦⟧), Ball **⟦⟧** (percentile ⟦⟧), and Dosunmu ⟦⟧, at the league median of ⟦⟧ `[observed, m5_usage_accounting]`.

**The pairing base rate.** New high-usage pairings cost usage, not efficiency: adjusted for who the players were, ⟦⟧ points of usage and ⟦⟧ of true shooting across ⟦⟧ player-seasons, and ⟦⟧ and ⟦⟧ at the star level where Edwards (⟦⟧) and Ball (⟦⟧) sit `[observed]`.

**The argument.** If a team's assigned defender can hold Edwards this reliably, the fix is not a better Edwards but a second creator the assignment cannot also cover. That is why Ball is here, and the base rate says the pairing should cost shots, not efficiency.

**The number, and the condition:** percentile ⟦⟧ as a scorer against his assigned defender, and the argument holds only if Ball draws that assignment often enough to loosen it.

---

## 6. Clutch

**In the last five minutes of a close game, everyone gets worse and more baskets come unassisted.** Across the league since the ⟦⟧ season, effective shooting falls from **⟦⟧ to ⟦⟧** and the unassisted share of makes rises from **⟦⟧ to ⟦⟧** `[observed, n7_late_clock]`. Of ⟦⟧ creators with enough clutch shots, **⟦⟧** beat that drop by two standard errors (⟦⟧ ⟦⟧, ⟦⟧ ⟦⟧), where chance alone gives about ⟦⟧. Edwards shot ⟦⟧ on ⟦⟧ clutch attempts (⟦⟧ standard errors beyond the drop) and Ball ⟦⟧ on ⟦⟧ (⟦⟧): **both inside the noise.**

*Late clock, withheld.* Play-by-play does not record the shot clock, and the reconstruction read within two seconds of zero at recorded violations only ⟦⟧ of the time against a bar of ⟦⟧ set in advance, so no late-clock split is published.

**The number, and the condition:** ⟦⟧ of ⟦⟧ creators beat the clutch drop, about what chance gives.

---

## 7. What to watch

Five claims, each checked at a team's ⟦⟧th game, late November `[composed, n8_watch_list]`.

| claim | now | flips if |
|---|---|---|
| ⟦⟧ | ⟦⟧ | **⟦⟧** |
| ⟦⟧ | ⟦⟧ | **⟦⟧** |
| ⟦⟧ | ⟦⟧ | **⟦⟧** |
| ⟦⟧ | ⟦⟧ | **⟦⟧** |
| ⟦⟧ | ⟦⟧ | **⟦⟧** |

**The number, and the condition:** ⟦⟧ minutes of Cody Williams is the threshold that moves the headline verdict, and it depends on a rotation decision no one has made yet.

---

## 8. The bill

**The cap chain closes to the dollar** `[observed, green_resolution]`: ⟦⟧, minus Green's ⟦⟧, plus Williams at ⟦⟧ and Konchar at ⟦⟧, minus ⟦⟧ for stretching Konchar, minus ⟦⟧ for the McDaniels rounding, equals **⟦⟧**. Add Kuminga's ⟦⟧ and it is **⟦⟧**: **⟦⟧ under the hard cap** and **⟦⟧ over the first apron**.

**What the Green dump cost: no pick and no swap, either direction.** Cash, and ⟦⟧ a year of Konchar dead money for three seasons, ⟦⟧ of it landing in the two seasons after this one `[observed, green_asset_cost]`. Minnesota holds Cody Williams in return, with a club option of ⟦⟧.

**Dosunmu forced the dump, not the acquisition.** With Dosunmu, Green and Kuminga all on the books Minnesota was **⟦⟧ over the hard cap**, so something had to go. But the cheapest legal version of that move, a minimum player instead of Williams and Konchar, left Minnesota at ⟦⟧ and about ⟦⟧ of tax; what happened left it at ⟦⟧ and about ⟦⟧. **Taking Williams and Konchar back cost ⟦⟧ of payroll and about ⟦⟧ more tax** `[observed, dosunmu_final_states]`. Not re-signing Dosunmu at all would have kept Green, added a minimum guard, and let Minnesota pay Kuminga up to ⟦⟧ from the non-taxpayer mid-level, landing exactly on the first apron with about ⟦⟧ of tax.

**The option.** ⟦⟧ now, ⟦⟧ next season at his choice, and a Non-Bird ceiling of ⟦⟧ if he leaves after one.

**The number, and the condition:** ⟦⟧ of hard-cap room for the whole league year, enough for one minimum addition if nothing goes wrong.

---

## Appendix

**What could not be estimated.** The late-clock split (withheld, section 6). A style overlay for series (section 2). Pre-playoff odds and every odds-history column before the clean seasons, left open for a pasted source. Earlier lineup findings built on the shared stint pipeline's point columns, which credited part of each team's points to the other team. The library is fixed and the postmortem figures are recomputed (D88); what remains is the possession-grain version of the same defect, which reaches RAPM and is not re-fitted.

**Tail players behind the model's biggest disagreements** (impact per view, no caps, no edits) `[modeled, f4_per_view_disagreement]`:

| player | possessions | consensus | RAPM | box | DARKO |
|---|---:|---:|---:|---:|---:|
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |

**The market against each view, for the largest disagreements and Minnesota** (title odds) `[modeled]`:

| team | market | consensus | RAPM | box | DARKO | views |
|---|---:|---:|---:|---:|---:|---|
| MIN | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| BOS | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| HOU | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| SAS | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| PHI | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| NYK | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| OKC | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| DET | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| CHA | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |

**Why "the offseason made Minnesota worse" does not ship.** The published offseason delta is ⟦⟧ points un-aged and all-negative, but ⟦⟧ and mixed on the aged basis, so it fails the rule that a verdict holds on both. It also carries two things the front office did not choose. The decomposition prices every state on the interpolation curve, where the same delta is ⟦⟧: take out the DiVincenzo injury (⟦⟧) and the Williams minutes (⟦⟧), which overlap completely (⟦⟧, because a healthy DiVincenzo is what takes Williams' minutes), and the remainder is **⟦⟧**, mixed across views `[modeled, w1c_decompose]`.

**The seven shipping verdicts under both allocators** (mean points of title odds, pooled un-aged / pooled aged / team-rank un-aged / team-rank aged, then views clearing in each cell) `[modeled, r7_allocator_agreement]`:

| verdict | pooled, un-aged | pooled, aged | team-rank, un-aged | team-rank, aged | views clearing in each cell |
|---|---:|---:|---:|---:|---|
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |

Kuminga's minutes are ⟦⟧ under the headline's rule and ⟦⟧ under the pooled one, which is most of why the slot sizes differ between the two.

**Randle out's flip history.** All-positive under the first minutes rules (D29). Mixed once the slot-aware allocator arrived, and it lost its quotable label (D31). All-positive again on the aged basis, when it was still held back as unstable (D52). All-positive on team-rank curve indexing, which became primary (D60). It has held its sign on both aging bases since the aging gate (D65), cleared every floor at full simulation count (D69), survived the D70 fixes (D77) and the departures split (D81). **It stopped shipping at D85**, when Cody Williams entered every coalition and new arrivals got their minutes by the headline's rule: ⟦⟧ un-aged, ⟦⟧ aged, views clearing ⟦⟧. Under the headline's team-rank allocator it turns negative un-aged, so its sign is not stable either.
