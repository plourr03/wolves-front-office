# Piece 2 skeleton: the season preview

**Status: restructured into eight sections. Rendered from `piece_v2_skeleton.template.md` by `render_piece.py`; every number comes from `outputs/final_numbers.csv` by key, and `reconcile_figures.py` fails if a digit reaches this page any other way.**

**Labelling rule.** `[observed]` happened and is in the data. `[composed]` is a real measurement recombined by us. `[modeled]` comes out of the simulation or an impact view. `[assumed]` is our choice and the piece says so. Run IDs for every figure are on the sheet.

**Framing rule for every market comparison: never "the odds were wrong."** The market is a prior. The piece shows how good a prior it is and what information moved the winners inside it.

**Structural rule: no section ends in a verdict.** Each ends with its number and the condition that number depends on.

---

## 1. The number

Minnesota's modelled title probability for the season is **{{title|t}}**, four-view band **{{title_lo}} to {{title_hi}}**, on the un-aged basis. On the survivorship-corrected aged basis it is **{{title_aged|t}}**, band {{title_lo_aged}} to {{title_hi_aged}}: aging helps Minnesota because Minnesota is young, so the piece quotes both. The market says **{{mkt_min|t}}, {{mkt_min_rank}}th**, after removing a {{overround}} overround proportionally.

**The disagreement is all-views on the primary basis, and holds in rank on both.** On the un-aged basis every one of the four views prices Minnesota below the market and ranks it in the range {{min_view_ranks}} against the market's {{mkt_min_rank}}th `[modeled, f4_per_view_disagreement]`; the market's number sits outside the model's whole band. On the aged basis every view still ranks Minnesota below the market ({{min_view_ranks_aged}}), but DARKO prices it above the market's {{mkt_min}}, at {{min_darko_aged}} against a box view of {{min_box_aged}} just under it, so in probability the aged disagreement is **{{min_label_aged}}** on {{min_above_aged}} view of four `[modeled, r5_honesty_rail_bases]`. The piece can say the model ranks Minnesota lower than the market does on both bases; it cannot say every view prices Minnesota below the market on both.

**The honesty rail.** The model and the market order the league at a rank correlation of **{{rankcorr_lo}} to {{rankcorr_hi}}** across the four views, {{rankcorr_lo_aged}} to {{rankcorr_hi_aged}} on the aged basis `[composed, market_devig, r5_honesty_rail_bases]`. They agree about the shape of the league and disagree about {{n_disagree}} specific teams, and **{{n_allviews}} of those {{n_disagree}} are all-views**, where every view sits on the same side of the market; on the aged basis it is {{n_allviews_aged}} of {{n_disagree_aged}}. The disagreements do not trace to a single fixable defect (F1). The four views are not independent instruments either: consensus and RAPM move together, so "all four agree" is a check that a finding does not hinge on one modelling choice, never a confidence interval.

**The model's biggest falsifiable claim is Boston.** The model makes Boston a **{{model_bos|t}}** title team against a market price of **{{mkt_bos}}**, and it does so in every view; on the aged basis it is {{model_bos_aged}}, still {{bos_label_aged}}. Named, with a date: **if Boston's net rating through its {{bos_dec_game}}th game, around the end of December, is below {{bos_dec_threshold}} per {{per100}} possessions, the market's read of Boston beats the model's** `[composed, n8_watch_list]`. The model's own range for Boston is {{bos_range_lo}} to {{bos_range_hi}}, and a {{bos_dec_game}}-game net rating carries about {{dec_noise}} points of pure chance, so the threshold sits where chance alone would rarely put a team the model has right. The same field prices every Minnesota number, so a Boston miss is a Minnesota caveat too.

**The {{n_ship}} verdicts that ship** hold their sign in all four cells of the rule, two aging bases by two minutes allocators, and clear every view's noise floor in each, at {{sims}} simulations per view `[modeled, w2_aging_gate, noise_floor, r7_allocator_agreement]`. It was {{n_ship_pre}} before the corrections below, out of {{n_candidates}} candidates.

{{TABLE:ship}}

*Notes.* Two of the {{n_ship}} are Minnesota's own transactions (Ball in, Reid out). One is an injury, which ships as a cost and is not a verdict on the front office. Four compare Kuminga against different internal alternatives for his minutes: positive against three of them, negative against Beringer. A view "clears" when its value is larger than its noise floor in either direction, so a verdict can clear every view and still fail on sign. **The allocator test is the newest of the four cells and it changed nothing:** the same seven survive whether minutes are allocated team-wide, as the headline simulation does, or inside position groups, as the attribution layer does, and the count on the looser two-cell rule is the same {{n_ship_two_cell}} `[modeled, r7_allocator_agreement]`. The sizes do move with the allocator, which is why the table gives the pooled figures and the appendix gives both.

**What no longer ships, and why.** Until this pass the decomposition priced every combination of moves on a roster without Cody Williams, the player the Green trade brought back, and without the rule that gives new arrivals their minutes. Priced with the headline simulation's own minutes rule, its version of the actual roster sat {{d85_gap_before}} points of title odds from that simulation on the un-aged basis; it now sits within {{d85_residual}} on either basis, which is interpolation. The pooled rule the verdicts use spreads minutes across more of the bench by design and sits up to {{d85_pooled_gap}} below. With both corrected, {{n_retired}} verdicts that shipped no longer do `[modeled, r5_shapley_williams]`:

{{TABLE:retired}}

None of the three survives the allocator cell either: under the headline's own minutes rule other departures is {{v_other_departures_tr_u}} un-aged against {{v_other_departures_pooled_u}} pooled, Randle out turns negative ({{v_randle_out_tr_u}}), and Dosunmu re-signed stays mixed `[modeled, r7_allocator_agreement]`. The departures bundle is seven players; split into them, {{n_dep_ship}} ships on its own, and Kyle Anderson comes closest ({{anderson_u}} un-aged, {{anderson_a}} aged, views clearing {{anderson_clear}}) `[modeled, r2_departures]`. Randle out's history of flips is in the appendix.

**The number, and the condition:** {{title}} modelled ({{title_aged}} aged) against {{mkt_min}} priced; the model ranks Minnesota lower than the market on both bases, the gap in probability is all-views only un-aged, and it is only as trustworthy as a model that also makes Boston a {{model_bos}} team, which December will test.

---

## 2. What the odds get right

**The things argued about in September are mostly unmeasurable, and the tests say so.**

**Style matchups.** Style interactions fixed in advance, fitted on two seasons and held out, made predictions **worse**: held-out mean absolute error rose by {{m1_rs_worse}} on {{m1_rs_n}} regular-season games and by {{m1_po_worse}} on {{m1_po_n}} postseason games `[modeled, m1_style_model]`. The San Antonio thesis could not be estimated from this data, and the series model runs without a style overlay.

**Playoff translation, and "defense travels."** Nothing tested translates. Eight candidate features, fixed before the fit, on {{n3_series}} playoff series going back to the {{n3_start}} postseason: **{{n3_n_translating}} of {{n3_n_features}}** add out-of-sample signal once the test allows for trying eight things at once, and that sample could detect an effect of about {{n3_mde_lo}} to {{n3_mde_hi}} points per game `[modeled, n3_playoff_translation]`. **"Defense travels" is not supported, and the estimate points the other way:** at equal net rating, a team whose rating leans on defense did **{{ds_coef}} points per game** in its series per standard deviation (standard error {{ds_se}}, p {{ds_p}} against a bar of {{ds_bar}}). Its single-test interval tops out at {{ds_ci_hi}}. Earlier and recent history agree ({{ds_early}} and {{ds_late}}), and three-point luck does not explain it ({{ds_luck}} with luck added). It misses the bar, so it changes nothing in the model.

**Versatility.** Under the series model the piece uses, a team's swing in series odds across the contender field is net rating restated (rank correlation {{n4_rankcorr}} outside the field) `[modeled, n4_versatility_index]`. In the games themselves, a repeatable matchup effect is worth about {{n4_sd13}} points per game since the {{n4_start13}} season and {{n4_sd97}} over {{n4_games97}} games since {{n4_start97}}, with a ceiling of {{n4_sd97_up}}, worth at most {{n4_series_up}} points of series probability in an even series `[observed]`.

**Individual matchups.** A pairing of thirty possessions carries a standard error of {{m3_se30}} points per matchup possession, and a team's main defender on a star normally holds him {{m3_norm_lo}} to {{m3_norm_hi}} below his average. Judged against that norm, {{m3_edges}} of {{m3_rows}} observed West-field matchups beat it by two standard errors, where chance alone gives about {{m3_chance}} `[observed, m3_opponent_cards]`.

**Champions, as honest counts.** Across the {{h2_n}} clean seasons the preseason favourite won **{{h2_fav}} of {{h2_n}}**, and the champion came from the market's top five **{{h2_top5}} of {{h2_n}}**, priced between {{h2_lo}} and {{h2_hi}} `[observed, champions_table]`. Set against the {{h3_n_non}} top-five teams that did not win, only {{h3_n_sep}} of {{h3_n_feat}} features separate the champions: offensive rank, defensive rank and continuity. No style feature does `[observed, h1_h3_h5_profile]`.

**The Knicks, the last champion.** The market had them at **{{nyk_mkt}}, {{nyk_rank}}th, {{nyk_wt}} wins**; they won {{nyk_wins}}. This project's model had them at {{nyk_model}} `[observed, h4_knicks_case_file]`. The regular season was steady: {{nyk_rs}} per game, {{nyk_pre}} before the break and {{nyk_post}} after. Then the playoffs were a different team: **{{nyk_po_rec}} at {{nyk_po}}**, and they were the only one of {{nyk_po_teams}} playoff teams whose margin improved ({{nyk_lift}}, against an average of {{nyk_lift_mean}}; Minnesota's was {{nyk_cmp_lift}}). What moved was not visible in September. Their top five players missed {{nyk_top5_rs_games_missed}} regular-season games and {{nyk_top5_po_games_missed}} in the playoffs; the top five's share of minutes went from {{nyk_top5_share_rs}} to {{nyk_top5_share_po}}; and the bracket broke their way.

**The number, and the condition:** {{n3_n_translating}} of {{n3_n_features}} translation features survive, and the conclusion rests on the belief that what decided last year's title (health, a shortened rotation, a bracket) was not knowable until April.

---

## 3. What the odds can't see, and what it means for Minnesota

**Health and fragility.** Take one of Minnesota's top three players away for the playoffs and its title odds fall by **{{n5_min_drop}} points on average, {{n5_min_share}} of what it has** ({{n5_min_share_aged}} aged); Oklahoma City loses {{n5_okc_drop}} ({{n5_okc_share}}) and San Antonio {{n5_sas_drop}} ({{n5_sas_share}}) `[modeled, n5_fragility]`. In strength the three lose about the same per player: **{{n5_min_net}}, {{n5_okc_net}} and {{n5_sas_net}} points of net rating**. The contenders' loss sits in one star ({{n5_okc_bigname}} {{n5_okc_big}}, {{n5_sas_bigname}} {{n5_sas_big}}); Minnesota's is spread across the three. With a tightened playoff rotation Minnesota loses the least of the three: {{n5_min_po}} against {{n5_okc_po}} and {{n5_sas_po}}. On the aged basis Minnesota loses {{n5_min_net_aged}} per player against {{n5_okc_net_aged}} and {{n5_sas_net_aged}}, so the spread-not-concentrated reading holds on both bases. **Which Minnesota player is costliest to lose does not hold on both bases, and the piece does not name one.**

**The rotation.** The model gives Cody Williams **{{williams_mpg}} minutes a night** `[assumed, build_rotations]`. He is the lowest-ranked of the ten men who play, **{{rs_gap}}** behind Jaylen Clark on the rank score that orders the rotation (Williams {{rs_williams}}, Clark {{rs_clark}}) `[composed, build_rotations]`. With DiVincenzo out, both play; with DiVincenzo healthy, the man cut is Williams, and he plays none. That gap is the whole difference between {{williams_mpg}} minutes and zero. **Below {{williams_threshold}} minutes a night, the four views stop agreeing that the offseason made Minnesota worse** `[modeled, williams_minutes_sensitivity]`. Double-big lineups can now be evaluated: {{m4_double}} of {{m4_fives}} legal fives use two bigs, and {{m4_nogobert}} play without Gobert `[composed, m4_lineup_study]`. Every one of the {{m4_top10_beringer}} best-graded fives includes Joan Beringer, whose rating rests on a rookie season of {{beringer_prior}} minutes a game: **those fives are composed, not observed, and rest on a rookie sample.** Only {{m4_observed}} of the {{m4_fives}} fives have ever played together. Last season's two Gobert frontcourts were level on correct points: {{reid_gobert}} with Reid and {{randle_gobert}} with Randle per {{per100}} possessions `[observed, lineup_evidence]`.

**Usage.** Last season's usage does not fit on one floor. The projected top five adds up to the **{{m5_top_pct}}th percentile** of {{m5_league_fives}} league starting fives; with Kuminga in for Dosunmu it is the **{{m5_kin_pct}}th**, and the **{{m5_kin3_pct}}th** at three-season rates. Last season's actual five was the {{m5_obs_pct}}th `[composed, m5_usage_accounting]`. New star pairings have cost usage, not efficiency: at the level where Edwards and Ball sit, **{{m5_star_usg}} points of usage (standard error {{m5_star_usg_se}}) and {{m5_star_ts}} of true shooting**, on only {{m5_star_n}} cases `[observed]`.

**The path.** Minnesota's most likely seed is **{{n2_modal}} ({{n2_modal_p}})**, and its chance of a top-six seed is **{{n2_top6}}** `[modeled, seed_distribution]`. Its first-round opponent is San Antonio or Oklahoma City **{{n2_sas_okc}}** of the time, the two teams it beats least. It reaches the second round {{n2_r2}} of the time, and once there wins the title {{n2_cond}} of the time: **title equity is a first-round problem** `[modeled, n2_path]`.

**The number, and the condition:** losing any one of its top three costs Minnesota about {{n5_min_share}} of its title odds on average ({{n5_min_share_aged}} aged), and every rotation figure above depends on Williams' {{williams_mpg}} minutes surviving a coaching staff.

---

## 4. Kuminga, better and worse

**Better.**

- **He beats the most likely internal fill for his minutes** `[modeled, slot_robustness]`: {{v_A_c3_default_shannon_u}} points of title odds un-aged and {{v_A_c3_default_shannon_a}} aged, positive in every view and clearing every view's floor on both bases ({{v_A_c3_default_shannon_clear}}) at {{sims}} simulations. It clears on size, not just sign.
- **As a defender assigned to a top scorer**, he held scorers slightly below the norm: percentile {{k_defender_pct}} of {{k_defender_ref}} defenders, where low is good ({{k_defender_z}} standard errors, inside the noise; {{k_defender_n}} pairings, {{k_defender_poss}} possessions) `[observed, n6_kuminga_ledger]`.
- **He is not a primary creator competing for Edwards' and Ball's shots:** usage {{k_usg}} last season, below the high-usage line, with {{k_unast}} of his makes unassisted (percentile {{k_unast_pct}}, on {{k_makes}} makes) `[observed]`.

**Worse, or uncertain.**

- **The slot verdict depends on who the alternative was.** If Beringer took those minutes instead, the comparison runs the other way: {{v_D_beringer_fills_u}} un-aged and {{v_D_beringer_fills_a}} aged, and that also clears `[modeled]`.
- **As a scorer against the defender a team assigns him**, he sits about at the norm: percentile {{k_scorer_pct}} of {{k_scorer_ref}} ({{k_scorer_z}} standard errors, {{k_scorer_n}} pairings, {{k_scorer_poss}} possessions over three seasons; last season alone gives {{k_scorer_n26}} pairings, too few) `[observed]`.
- **Next to a non-shooting centre at Golden State**, his units were {{gsw_with}} per {{per100}} possessions against {{gsw_without}} without one, on {{gsw_with_poss}} and {{gsw_without_poss}} possessions, with a three-point attempt rate of {{gsw_with_3par}} against {{gsw_without_3par}}. The gap is inside the noise (standard error {{gsw_se}}), but it is the Gobert question in miniature `[observed]`.
- **In the playoffs, all of it pooled:** {{po_games}} games and {{po_poss}} possessions, **on-court net {{po_net}}**. In the {{po_onoff_games}} games with lineup data, with garbage time removed, his team was {{po_onoff}} per {{per100}} possessions worse with him on than off (standard error {{po_onoff_se}}). Small, and confounded by who else was on the floor, but not explained by blowouts `[observed]`.
- **He adds to the crunch:** the projected five with him in is the {{m5_kin_pct}}th-percentile usage five `[composed]`.

**The contract, in one paragraph.** Two years from the taxpayer mid-level exception: **{{k_y1}}** this season and **{{k_y2}}** next, a player option on the second year, {{k_total}} in all; the team release disclosed no terms, so these are reported figures `[observed]`. If he opts out after one season, he has one season of service and Minnesota holds only Non-Bird rights, which cap a re-signing at **{{k_nonbird}}**. If he opts in and plays both, Minnesota holds Early Bird rights. The option model has him opting out with probability **{{k_optout_lo}} to {{k_optout_hi}}** across the views `[modeled, player_option]`.

**The number, and the condition:** {{v_A_c3_default_shannon_u}} points of title odds against the default fill, conditional on the alternative not being Beringer and on one season that the option may make the only one.

---

## 5. Edwards, and why Ball is here

**Edwards is the most guardable star one-on-one.** Across the league last season, the defender a team assigned to Edwards held him further under his own level than that assignment holds almost any other scorer: **percentile {{e_pct_shipped}} of {{e_n_off}} top scorers**, {{e_z_shipped}} standard errors over {{e_pairings}} pairings `[observed, m3_primary_defender_check]`. It survives both confound checks: a baseline built only from rotation defenders (percentile {{e_pct_A}}) and dropping the playoffs (percentile {{e_pct_B}}; both together, {{e_pct_C}}). Over three seasons he is the **lowest of {{k_scorer_ref}} scorers** (percentile {{e_scorer_pct3}}, {{e_scorer_z3}} standard errors, {{e_scorer_n3}} pairings) `[observed, n6_kuminga_ledger]`.

**The creators.** Edwards made **{{cr_edw}}** of his baskets unassisted (percentile {{cr_edw_pct}}), Ball **{{cr_ball}}** (percentile {{cr_ball_pct}}), and Dosunmu {{cr_dos}}, at the league median of {{cr_median}} `[observed, m5_usage_accounting]`.

**The pairing base rate.** New high-usage pairings cost usage, not efficiency: adjusted for who the players were, {{m5_adj_usg}} points of usage and {{m5_adj_ts}} of true shooting across {{m5_treated}} player-seasons, and {{m5_star_usg}} and {{m5_star_ts}} at the star level where Edwards ({{usg_edw}}) and Ball ({{usg_ball}}) sit `[observed]`.

**The argument.** If a team's assigned defender can hold Edwards this reliably, the fix is not a better Edwards but a second creator the assignment cannot also cover. That is why Ball is here, and the base rate says the pairing should cost shots, not efficiency.

**The number, and the condition:** percentile {{e_pct_shipped}} as a scorer against his assigned defender, and the argument holds only if Ball draws that assignment often enough to loosen it.

---

## 6. Clutch

**In the last five minutes of a close game, everyone gets worse and more baskets come unassisted.** Across the league since the {{cl_start}} season, effective shooting falls from **{{cl_efg_all}} to {{cl_efg_clutch}}** and the unassisted share of makes rises from **{{cl_un_all}} to {{cl_un_clutch}}** `[observed, n7_late_clock]`. Of {{cl_n_ok}} creators with enough clutch shots, **{{cl_n_big}}** beat that drop by two standard errors ({{cl_big1}} {{cl_big1_z}}, {{cl_big2}} {{cl_big2_z}}), where chance alone gives about {{cl_chance}}. Edwards shot {{cl_edw_efg}} on {{cl_edw_fga}} clutch attempts ({{cl_edw_z}} standard errors beyond the drop) and Ball {{cl_ball_efg}} on {{cl_ball_fga}} ({{cl_ball_z}}): **both inside the noise.**

*Late clock, withheld.* Play-by-play does not record the shot clock, and the reconstruction read within two seconds of zero at recorded violations only {{lc_g1}} of the time against a bar of {{lc_bar}} set in advance, so no late-clock split is published.

**The number, and the condition:** {{cl_n_big}} of {{cl_n_ok}} creators beat the clutch drop, about what chance gives.

---

## 7. What to watch

Five claims, each checked at a team's {{w_game}}th game, late November `[composed, n8_watch_list]`.

| claim | now | flips if |
|---|---|---|
| {{w1_claim}} | {{w1_now}} | **{{w1_flip}}** |
| {{w2_claim}} | {{w2_now}} | **{{w2_flip}}** |
| {{w3_claim}} | {{w3_now}} | **{{w3_flip}}** |
| {{w4_claim}} | {{w4_now}} | **{{w4_flip}}** |
| {{w5_claim}} | {{w5_now}} | **{{w5_flip}}** |

**The number, and the condition:** {{williams_threshold}} minutes of Cody Williams is the threshold that moves the headline verdict, and it depends on a rotation decision no one has made yet.

---

## 8. The bill

**The cap chain closes to the dollar** `[observed, green_resolution]`: {{chain_start}}, minus Green's {{chain_green}}, plus Williams at {{chain_williams}} and Konchar at {{chain_konchar}}, minus {{chain_stretch}} for stretching Konchar, minus {{chain_dollar}} for the McDaniels rounding, equals **{{chain_post}}**. Add Kuminga's {{chain_kuminga}} and it is **{{chain_final}}**: **{{room_hard_cap}} under the hard cap** and **{{over_first}} over the first apron**.

**What the Green dump cost: no pick and no swap, either direction.** Cash, and {{dead_year}} a year of Konchar dead money for three seasons, {{dead_future}} of it landing in the two seasons after this one `[observed, green_asset_cost]`. Minnesota holds Cody Williams in return, with a club option of {{williams_option}}.

**Dosunmu forced the dump, not the acquisition.** With Dosunmu, Green and Kuminga all on the books Minnesota was **{{dos_stuck_over}} over the hard cap**, so something had to go. But the cheapest legal version of that move, a minimum player instead of Williams and Konchar, left Minnesota at {{dos_cheapest_apron}} and about {{dos_cheapest_tax}} of tax; what happened left it at {{dos_happened_apron}} and about {{dos_happened_tax}}. **Taking Williams and Konchar back cost {{dos_dump_payroll}} of payroll and about {{dos_dump_tax}} more tax** `[observed, dosunmu_final_states]`. Not re-signing Dosunmu at all would have kept Green, added a minimum guard, and let Minnesota pay Kuminga up to {{dos_nodos_kuminga}} from the non-taxpayer mid-level, landing exactly on the first apron with about {{dos_nodos_tax}} of tax.

**The option.** {{k_y1}} now, {{k_y2}} next season at his choice, and a Non-Bird ceiling of {{k_nonbird}} if he leaves after one.

**The number, and the condition:** {{room_hard_cap}} of hard-cap room for the whole league year, enough for one minimum addition if nothing goes wrong.

---

## Appendix

**What could not be estimated.** The late-clock split (withheld, section 6). A style overlay for series (section 2). Pre-playoff odds and every odds-history column before the clean seasons, left open for a pasted source. Earlier lineup findings built on the shared stint pipeline's point columns, which credited part of each team's points to the other team. Both grains are fixed now, the lineup one and the possession one under it, and everything built on them is recomputed: the postmortem lineup figures (D88) and the RAPM the impact views ride on (D89). The impact spine behind this piece is the refit one.

**Tail players behind the model's biggest disagreements** (impact per view, no caps, no edits) `[modeled, f4_per_view_disagreement]`:

{{TABLE:tail}}

**The market against each view, for the largest disagreements and Minnesota** (title odds) `[modeled]`:

{{TABLE:perview}}

**Why "the offseason made Minnesota worse" does not ship.** The published offseason delta is {{off_delta_u}} points un-aged and all-negative, but {{off_delta_a}} and mixed on the aged basis, so it fails the rule that a verdict holds on both. It also carries two things the front office did not choose. The decomposition prices every state on the interpolation curve, where the same delta is {{w1c_offseason_delta}}: take out the DiVincenzo injury ({{w1c_injury_cost}}) and the Williams minutes ({{w1c_williams_cost}}), which overlap completely ({{w1c_interaction}}, because a healthy DiVincenzo is what takes Williams' minutes), and the remainder is **{{w1c_remainder}}**, mixed across views `[modeled, w1c_decompose]`.

**The seven shipping verdicts under both allocators** (mean points of title odds, pooled un-aged / pooled aged / team-rank un-aged / team-rank aged, then views clearing in each cell) `[modeled, r7_allocator_agreement]`:

{{TABLE:allocators}}

Kuminga's minutes are {{k_min_teamrank}} under the headline's rule and {{k_min_pooled}} under the pooled one, which is most of why the slot sizes differ between the two.

**Randle out's flip history.** All-positive under the first minutes rules (D29). Mixed once the slot-aware allocator arrived, and it lost its quotable label (D31). All-positive again on the aged basis, when it was still held back as unstable (D52). All-positive on team-rank curve indexing, which became primary (D60). It has held its sign on both aging bases since the aging gate (D65), cleared every floor at full simulation count (D69), survived the D70 fixes (D77) and the departures split (D81). **It stopped shipping at D85**, when Cody Williams entered every coalition and new arrivals got their minutes by the headline's rule: {{v_randle_out_u}} un-aged, {{v_randle_out_a}} aged, views clearing {{v_randle_out_clear}}. Under the headline's team-rank allocator it turns negative un-aged, so its sign is not stable either.
