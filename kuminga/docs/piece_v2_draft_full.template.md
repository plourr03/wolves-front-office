# Minnesota's title odds, what Kuminga changes, and what the market can't see

*Draft, rendered from `piece_v2_draft_full.template.md`. Every number comes from `outputs/final_numbers.csv` by key and carries a run ID in the claims table at the end. The reconcile gate fails if a digit reaches this page any other way.*

**The short version, in five bullets.**

- **What the market says.** The betting market has Minnesota at {{mkt_min}} to win the title, {{mkt_min_rank}}th in the league, once you strip out the bookmakers' margin.
- **What the model says.** {{title}} on the primary basis, with the four ways of measuring players spanning {{title_lo}} to {{title_hi}}, and {{title_aged}} once you correct for how players age. Every one of the four views ranks Minnesota below where the market has them, on both bases.
- **What ships about Kuminga.** He beats the player who would otherwise have played his minutes, and the gap clears the model's own noise under every way I can test it. The one alternative that flips it is Joan Beringer taking those minutes instead.
- **What the offseason verdict depends on.** "The offseason made Minnesota worse" is the sentence this piece can't write. It holds only while Cody Williams plays {{williams_threshold}} minutes a night or more, and only on one of the two aging bases.
- **What to watch.** Five claims with thresholds set now, checked at game {{w_game}}, and one bigger one about Boston checked at game {{bos_dec_game}}.

## 1. The number

Here's the number everything else hangs off. The model gives Minnesota a **{{title}}** chance of winning the title, and the market gives it **{{mkt_min}}**.

Where each comes from, because the gap between them is the whole story. The market number is six sportsbooks' odds with the bookmakers' margin removed (their prices add up to {{overround}} over a hundred, and every team gets shaved back proportionally). The model number is a season simulated {{sims}} times per view, where a "view" is one of four ways of scoring how much each player helps his team, and {{title}} is the average of the four. The views themselves put Minnesota anywhere from {{title_lo}} to {{title_hi}}.

That's the primary basis, every player at last season's measured level. A second basis adjusts each player for a year of aging, and it's kinder to Minnesota because Minnesota is young: **{{title_aged}}**, spanning {{title_lo_aged}} to {{title_hi_aged}}. The piece quotes both, and I'd rather you saw the pair than a blend.

### Why the gap is real, and where it isn't

The honest way to compare a model to a market is to ask whether they agree on the shape of the league. They mostly do: ranking all thirty teams, they line up with a rank correlation of {{rankcorr_lo}} to {{rankcorr_hi}} across the four views ({{rankcorr_lo_aged}} to {{rankcorr_hi_aged}} aged). They disagree about {{n_disagree}} specific teams by more than half a point of title odds, and on {{n_allviews}} of those every view sits on the same side of the market. Minnesota is one of them.

On the primary basis all four views price Minnesota below the market, and they rank it {{min_view_ranks}} against the market's {{mkt_min_rank}}th. That's not two estimates overlapping inside their error bars. The market's number sits outside the model's whole range.

On the aged basis the picture softens. Every view still ranks Minnesota below the market ({{min_view_ranks_aged}}), but one of the four prices it above the market's {{mkt_min}} (the DARKO view, at {{min_darko_aged}}, with the box view at {{min_box_aged}} just under). So the careful statement is this: the model ranks Minnesota lower than the market on both bases, and it prices Minnesota lower than the market in every view only on the primary one.

One caution before you lean on "all four views agree." The views aren't independent. Consensus is built partly out of RAPM and tracks it at a correlation of {{cons_rapm_corr}} across players, so when those two agree it's largely the same measurement twice. Four-way agreement means a finding doesn't hinge on one modeling choice. It isn't a confidence interval.

### The model's biggest claim, and its expiry date

If you want to know whether to trust any of this, don't watch Minnesota. Watch Boston. The model makes the Celtics a **{{model_bos}}** title team against a market price of **{{mkt_bos}}**, in every view ({{model_bos_aged}} aged, still all four on the same side). That's the biggest disagreement the model has with anyone, and it comes with a date. If Boston's net rating through its {{bos_dec_game}}th game, around the end of December, is below {{bos_dec_threshold}} per hundred possessions, the market's read on Boston beats the model's. The model's range for Boston is {{bos_range_lo}} to {{bos_range_hi}}, and a {{bos_dec_game}}-game net rating carries about {{dec_noise}} points of pure chance, so the threshold sits where chance alone would rarely put a team the model has right.

The same machinery prices Minnesota, so a Boston miss is a Minnesota caveat too.

Charlotte is on the list as well, and it comes with a confession. The model first priced Charlotte at {{cha_model_pre}}, {{cha_gap_pre}} points over a market price of {{mkt_cha}}. About half of that gap was a bug in my own possession data, which I found and fixed; the model now has Charlotte at {{model_cha}}, a gap of {{cha_gap_now}}. What's left is the real disagreement, and it still runs in the same direction.

### What actually ships

The model prices every offseason move Minnesota made, plus a few things that happened to it, and each gets a yes or no on whether it's solid enough to print. The rule is strict on purpose: a verdict ships only if it points the same way on both aging bases and under both ways of handing out minutes, and only if all four views clear the model's own noise in every one of those four combinations. A noise floor, since it comes up a lot, is the size of change the simulation could produce by luck alone, doubled.

{{n_ship}} of {{n_candidates}} candidates clear that bar.

{{TABLE:ship_pooled}}

Every row is on the same minutes rule the Kuminga section uses, and every row clears all four views in all four cells, both aging bases by both minutes rules; the full four-cell table is in the appendix. Two of the seven are Minnesota's own decisions, Ball in and Reid out. One is an injury, DiVincenzo's Achilles, which ships as a cost and not as anyone's fault. Four are the same Kuminga comparison run under different rules for who else would have played his minutes: positive against three of them, negative if the answer is Beringer. The Kuminga section is about that.

It was {{n_ship_pre}} before this pass. Three that used to ship don't anymore, the other departures as a bundle, Randle out and the Dosunmu re-signing, all retired after I found the attribution model had been pricing every combination of moves on a roster without Cody Williams on it. Randle out is the one fans will ask about. Its sign now depends on which minutes rule you use, which is exactly the verdict the rule exists to keep off the page.

**The number, and the condition:** {{title}} modeled ({{title_aged}} aged) against {{mkt_min}} priced. The model ranks Minnesota below the market on both bases, the probability gap is all-views only on the primary basis, and all of it is only as trustworthy as a model that also makes Boston a {{model_bos}} team, which December will test.

## 2. What the odds get right

Most of what gets argued about in September is unmeasurable, and this section is the evidence for that sentence. Every test here came back empty, and the empties are the point, not an apology for them.

### Style doesn't predict

The first thing everyone wants is a style overlay: this team plays fast, that team packs the paint, surely that matters in a series. I built one. Style interactions fixed in advance, fitted on two seasons and tested on games those seasons never saw. Adding style made predictions slightly worse: the average error in predicted margin rose by {{m1_rs_worse}} points per game on {{m1_rs_n}} held-out regular season games and by {{m1_po_worse}} points per game on {{m1_po_n}} held-out playoff games. The San Antonio matchup thesis couldn't be estimated from this data, and the series model runs without any style term at all.

### Nothing "translates" to the playoffs

Then the translation question: is there some regular season trait that predicts playoff success beyond plain net rating? I fixed {{n3_n_features}} candidate features before looking, and tested them on {{n3_series}} playoff series going back to the {{n3_start}} postseason. **{{n3_n_translating}} of {{n3_n_features}}** added out-of-sample signal once you account for having tried eight things at once. That sample could have detected an effect of about {{n3_mde_lo}} to {{n3_mde_hi}} points per game, so this isn't a small-sample shrug.

"Defense travels" deserves its own line because it's the one everybody believes. It is not supported, and the estimate points the other way. At equal net rating, a team whose rating leans on defense did **{{ds_coef}} points per game** in its series per standard deviation of that lean, with a standard error of {{ds_se}}. That's a p-value of {{ds_p}} against a bar of {{ds_bar}}, the bar being what you need after testing eight things. Its interval tops out at {{ds_ci_hi}}. Earlier seasons and recent seasons agree ({{ds_early}} and {{ds_late}}), and three-point luck doesn't explain it ({{ds_luck}} once you add luck). It misses the bar, so it changes nothing in the model. But if you were going to bet on defense traveling, you should know the sign.

### Versatility and matchups are mostly noise

Versatility, the idea that some teams match up well against more of the field, turns out to be net rating restated: the better team is the better team against everybody. Under the series model, a team's swing in series odds across the contender field tracks its own net rating with a rank correlation of {{n4_rankcorr}} outside the field. In the games themselves, a repeatable matchup effect is worth about {{n4_sd13}} points per game since the {{n4_start13}} season and {{n4_sd97}} over {{n4_games97}} games since {{n4_start97}}. The ceiling on it is {{n4_sd97_up}}, which is worth at most {{n4_series_up}} points of series probability in an even series. Individual matchups, the "who guards Ant" question, are the same story in miniature. A pairing of thirty possessions carries a standard error of {{m3_se30}} points per matchup possession, and a team's main defender on a star normally holds him {{m3_norm_lo}} to {{m3_norm_hi}} below his own average, because stoppers get the hard possessions. Judged against that norm, {{m3_edges}} of {{m3_rows}} observed West-field matchups beat it by two standard errors, where chance alone would give about {{m3_chance}}.

### What champions actually looked like

Base rates, as counts, on the {{h2_n}} clean seasons of odds I have. The preseason favorite won {{h2_fav}} of {{h2_n}}. The champion came from the market's top five {{h2_top5}} of {{h2_n}} times, priced between {{h2_lo}} and {{h2_hi}}. Set against the {{h3_n_non}} top-five teams that didn't win in the three most recent seasons (the feature comparison still runs on 2023-24 to 2025-26), only {{h3_n_sep}} of {{h3_n_feat}} features separate the champions: offensive rank, defensive rank and continuity. No style feature does.

The Knicks are the file that shows why. The market had them at {{nyk_mkt}}, {{nyk_rank}}th, with a win total of {{nyk_wt}}. They won {{nyk_wins}}, right on it. This project's model had them at {{nyk_model}}, below the market, on the same side of the market where it now sits on Minnesota. The regular season was steady: {{nyk_rs}} per game, {{nyk_pre}} before the break and {{nyk_post}} after. Then the playoffs were a different team, **{{nyk_po_rec}} at {{nyk_po}}**, and they were the only one of {{nyk_po_teams}} playoff teams whose margin improved ({{nyk_lift}}, against an average of {{nyk_lift_mean}}; Minnesota's was {{nyk_cmp_lift}}). What moved wasn't visible in September. Their top five players missed {{nyk_top5_rs_games_missed}} regular season games and {{nyk_top5_po_games_missed}} in the playoffs, the top five's share of the minutes went from {{nyk_top5_share_rs}} to {{nyk_top5_share_po}}, and the bracket broke their way.

**The number, and the condition:** {{n3_n_translating}} of {{n3_n_features}} translation features survive, and the conclusion rests on the belief that what decided last year's title (health, a shortened rotation, a bracket) wasn't knowable until April.

## 3. What the odds can't see, and what it means for Minnesota

The optimist's version, said the way a fan would say it: this roster finally has a second creator next to Ant, the bench can shoot, the West is wide open behind the top two, and nobody's model prices chemistry or a young team's growth. The pessimist's version: they traded two proven bigs for a point guard who hasn't stayed healthy, a wing on a one-year deal and a rookie center, and the depth chart is one injury from Cody Williams playing real minutes.

Both are about things the market prices badly. Here's what the data says about each.

### Health

Take one of Minnesota's top three players away for the playoffs and the model says its title odds fall by **{{n5_min_drop}} points on average, {{n5_min_share}} of what it has** ({{n5_min_share_aged}} on the aged basis). Oklahoma City loses {{n5_okc_drop}} ({{n5_okc_share}}) and San Antonio {{n5_sas_drop}} ({{n5_sas_share}}). In raw strength the three teams lose about the same per player: {{n5_min_net}}, {{n5_okc_net}} and {{n5_sas_net}} points of net rating. The difference is shape. The contenders' loss sits in one star ({{n5_okc_bigname}} at {{n5_okc_big}}, {{n5_sas_bigname}} at {{n5_sas_big}}); Minnesota's is spread across the three. With a tightened playoff rotation Minnesota loses the least of the three: {{n5_min_po}} against {{n5_okc_po}} and {{n5_sas_po}}. On the aged basis Minnesota loses {{n5_min_net_aged}} per player against {{n5_okc_net_aged}} and {{n5_sas_net_aged}}, so the spread-not-concentrated reading holds on both bases. Which Minnesota player is costliest to lose doesn't hold on both bases, so this piece doesn't name one.

### The rotation, and the coin flip in it

The model gives Cody Williams **{{williams_mpg}} minutes a night**. That's an assumption, not a projection, and here's why it matters more than a tenth man's minutes should. Williams is the lowest-ranked of the ten men who play, {{rs_gap}} behind Jaylen Clark on the rank score that orders the rotation (Williams {{rs_williams}}, Clark {{rs_clark}}). With DiVincenzo out, both play. With DiVincenzo healthy, one of them gets cut, and that gap is the difference between Williams at {{williams_mpg}} and Williams at zero. It's a coaching decision the model is guessing at.

And it carries a verdict. Below {{williams_threshold}} minutes a night for Williams, the four views stop agreeing that the offseason made Minnesota worse. The model's negative read on the summer is, in part, a read on a rotation call nobody has made.

Double-big lineups can be evaluated now that the roster is set: {{m4_double}} of {{m4_fives}} legal fives use two bigs, and {{m4_nogobert}} play without Gobert. {{m4_top10_beringer}} of the ten best-graded fives include Joan Beringer, whose rating rests on a rookie season of {{beringer_prior}} minutes a game. Those fives are composed from individual ratings, not observed, and they rest on a rookie sample, so I'm not going to tell you what the closing five looks like. Only {{m4_observed}} of the {{m4_fives}} fives have ever played a possession together.

One thing from last season's data that people get wrong: the two Gobert frontcourts were level. Reid next to Gobert was {{reid_gobert}} per hundred possessions, Randle next to Gobert was {{randle_gobert}}. The case for the offseason was never "Reid was carrying the frontcourt."

### Usage

Last season's usage doesn't fit on one floor. The projected top five adds up to the **{{m5_top_pct}}th percentile** of {{m5_league_fives}} league starting fives; with Kuminga in for Dosunmu it's the **{{m5_kin_pct}}th**, and the **{{m5_kin3_pct}}th** at three-season rates. Last season's actual five was the {{m5_obs_pct}}th. Somebody's shots go away.

The base rate says how much, not whose. When a high-usage player gains a new high-usage teammate (the study follows that player, so here it is Edwards gaining Ball and Ball gaining Edwards), his usage drops and his efficiency doesn't: adjusted for who the players were, {{m5_adj_usg}} points of usage and {{m5_adj_ts}} of true shooting across {{m5_treated}} player-seasons, and at the level where Edwards and Ball sit, {{m5_star_usg}} of usage (standard error {{m5_star_usg_se}}) and {{m5_star_ts}} of true shooting, on only {{m5_star_n}} cases. Pairings cost shots, not points per shot.

### The path

Minnesota's most likely seed is **{{n2_modal}} ({{n2_modal_p}})**, and its chance of a top-six seed is **{{n2_top6}}**. Its first-round opponent is San Antonio or Oklahoma City **{{n2_sas_okc}}** of the time, which are the two teams it beats least. It reaches the second round {{n2_r2}} of the time, and once there it wins the title {{n2_cond}} of the time. Title equity is a first-round problem.

**The number, and the condition:** losing any one of its top three costs Minnesota about {{n5_min_share}} of its title odds on average ({{n5_min_share_aged}} aged), and every rotation figure above depends on Williams's {{williams_mpg}} minutes surviving a coaching staff.

## 4. Kuminga, better and worse

The optimist: he's the athletic four they've been missing since Randle stopped being one, he's cheap, he's young, and he's an upgrade on whoever else was going to soak up those minutes. The pessimist: he couldn't stick in Golden State, his units cratered next to a non-shooting center, which is exactly what Gobert is, and his playoff numbers are ugly enough that you don't need a model.


### Better

He beats the most likely internal fill for his minutes. Against the default answer to "who plays the four if not him," the model gives {{v_A_c3_default_shannon_pooled_u}} points of title odds on the primary basis and {{v_A_c3_default_shannon_pooled_a}} aged, or {{v_A_c3_default_shannon_tr_u}} and {{v_A_c3_default_shannon_tr_a}} under the headline's own minutes rule. It clears on size, not just sign, and it clears every view under both bases and both minutes rules, which is the strictest test this piece applies to anything. The two sizes differ mostly because the allocators give him different minutes: {{k_min_teamrank}} a night under the headline's rule, {{k_min_pooled}} under the pooled one.

As a defender assigned to a top scorer, in last season's data pooled with the two before it, he held scorers slightly below the norm: percentile {{k_defender_pct}} of {{k_defender_ref}} defenders, where low is good ({{k_defender_z}} standard errors, inside the noise; {{k_defender_n}} pairings, {{k_defender_poss}} possessions).

He's not a primary creator competing with Edwards and Ball for the ball: usage {{k_usg}} last season, below the high-usage line, with {{k_unast}} of his makes unassisted (percentile {{k_unast_pct}}, on {{k_makes}} makes).

### Worse, or uncertain

The slot verdict depends on who the alternative is. If Beringer took those minutes instead, the comparison runs the other way, {{v_D_beringer_fills_pooled_u}} on the primary basis and {{v_D_beringer_fills_pooled_a}} aged ({{v_D_beringer_fills_tr_u}} and {{v_D_beringer_fills_tr_a}} under the headline's minutes rule), and that clears too. The model likes Beringer a lot on a rookie sample. Whether it should is a different question, and it's the biggest single uncertainty in the Kuminga verdict.

As a scorer against the defender a team assigns him, he's about at the norm: percentile {{k_scorer_pct}} of {{k_scorer_ref}} ({{k_scorer_z}} standard errors, {{k_scorer_n}} pairings, {{k_scorer_poss}} possessions over three seasons; last season alone gives {{k_scorer_n26}} pairings, too few to say anything).

Next to a non-shooting center at Golden State, his units were {{gsw_with}} per hundred possessions against {{gsw_without}} without one, on {{gsw_with_poss}} and {{gsw_without_poss}} possessions, with a three-point attempt rate of {{gsw_with_3par}} against {{gsw_without_3par}}. The gap sits inside the noise (standard error {{gsw_se}}), so it's not evidence on its own. It is the Gobert question in miniature.

In the playoffs, all of it pooled: {{po_games}} games and {{po_poss}} possessions, **on-court net {{po_net}}**. In the {{po_onoff_games}} games with lineup data, with garbage time removed, his team was {{po_onoff}} per hundred possessions worse with him on than off (standard error {{po_onoff_se}}). Small, and confounded by who else was on the floor, but blowouts don't explain it.

He adds to the crunch. The projected five with him in is the {{m5_kin_pct}}th-percentile usage five.

### The contract

Two years from the taxpayer mid-level exception: **{{k_y1}}** this season and **{{k_y2}}** next, a player option on the second year, {{k_total}} in all. The team's release disclosed no terms, so these are reported figures, corroborated by the exception amount to the dollar. If he opts out after one season, he'll have one season of service and Minnesota holds only Non-Bird rights, which cap a re-signing at **{{k_nonbird}}**. If he opts in and plays both years, Minnesota holds Early Bird rights. The option model has him opting out with a probability between {{k_optout_lo}} and {{k_optout_hi}} across the views.

**The number, and the condition:** {{v_A_c3_default_shannon_pooled_u}} points of title odds against the default fill, conditional on the alternative not being Beringer and on one season that the option may make the only one.

## 5. Edwards, and why Ball is here

The optimist: Ball is the second creator Ant has never had, defenses can't send everything at one guy anymore, and Ant's off-ball game is about to get room it's never had. The pessimist: two ball-dominant guards, one ball, neither one defends, and the usage crunch is going to land on somebody's efficiency.


### The most guardable star

Across the league last season, the defender a team assigned to Edwards held him further under his own level than that assignment holds almost any other scorer: **percentile {{e_pct_shipped}} of {{e_n_off}} top scorers**, {{e_z_shipped}} standard errors over {{e_pairings}} pairings. That's a single-season finding, so it got the confound checks. Build the baseline only from rotation defenders and it's percentile {{e_pct_A}}. Drop the playoffs and it's {{e_pct_B}}. Do both and it's {{e_pct_C}}. Over three seasons he is the lowest of {{k_scorer_ref}} scorers (percentile {{e_scorer_pct3}}, {{e_scorer_z3}} standard errors, {{e_scorer_n3}} pairings).

Read that carefully, because it's not "Edwards is bad." It's that one good defender, assigned to him, takes more off him than one good defender takes off anyone else. That's what a team with one creator looks like from the outside.

### The creators

Edwards made {{cr_edw}} of his baskets unassisted last season (percentile {{cr_edw_pct}}), Ball {{cr_ball}} (percentile {{cr_ball_pct}}), against a league median of {{cr_median}}. Two of them on the floor is the point.

### What the pairing should cost

New high-usage pairings cost usage, not efficiency. Adjusted for who the players were, {{m5_adj_usg}} points of usage and {{m5_adj_ts}} of true shooting across {{m5_treated}} player-seasons, and {{m5_star_usg}} and {{m5_star_ts}} at the star level where Edwards ({{usg_edw}}) and Ball ({{usg_ball}}) sit.

So the argument is simple, and it's the one opinionated sentence in this piece. If a team's assigned defender can hold Edwards this reliably, the fix isn't a better Edwards. It's a second creator the assignment can't also cover. That's why Ball is here, and the base rate says the pairing should cost shots, not efficiency.

**The number, and the condition:** percentile {{e_pct_shipped}} as a scorer against his assigned defender, and the argument holds only if Ball draws that assignment often enough to loosen it.

## 6. Clutch

The optimist: Ant is a closer, and close games are where stars earn the money. The pessimist: Ant's late-game shot selection is why they lose close games, and now there are two guys who want the last shot.

In the last five minutes of a close game, everyone gets worse and more baskets come unassisted. Across the league since the {{cl_start}} season, effective field goal percentage falls from **{{cl_efg_all}} to {{cl_efg_clutch}}** in the clutch, and the unassisted share of makes rises from **{{cl_un_all}} to {{cl_un_clutch}}**. That's the baseline every "closer" has to be judged against, and almost nobody clears it. Of {{cl_n_ok}} creators with enough clutch shots, **{{cl_n_big}}** beat that league-wide drop by two standard errors ({{cl_big1}} at {{cl_big1_z}}, {{cl_big2}} at {{cl_big2_z}}), where chance alone would give about {{cl_chance}}.

Edwards shot {{cl_edw_efg}} on {{cl_edw_fga}} clutch attempts, {{cl_edw_z}} standard errors better than the drop. Ball shot {{cl_ball_efg}} on {{cl_ball_fga}}, {{cl_ball_z}}. Both inside the noise. Neither the closer story nor the choker story survives contact with the sample size.

One split you won't find here. The late-clock split, how each creator does when the shot clock is nearly out, was withheld. Play-by-play doesn't record the shot clock, so it has to be reconstructed, and my reconstruction read within two seconds of zero at recorded violations {{lc_g1}} of the time against a bar of {{lc_bar}} that was set in advance. It missed the bar, so it doesn't get printed.

**The number, and the condition:** {{cl_n_big}} of {{cl_n_ok}} creators beat the clutch drop, which is about what chance gives, and that holds until somebody's sample gets big enough to say otherwise.

## 7. The bill

The cap chain closes to the dollar, so here it is. {{chain_start}}, minus Green's {{chain_green}}, plus Williams at {{chain_williams}} and Konchar at {{chain_konchar}}, minus {{chain_stretch}} for stretching Konchar, minus {{chain_dollar}} for a rounding difference on McDaniels, equals **{{chain_post}}**. Add Kuminga's {{chain_kuminga}} and it's **{{chain_final}}**: **{{room_hard_cap}} under the hard cap**, {{over_first}} over the first apron and {{over_tax}} over the tax line.

What the Green dump cost: no pick and no swap, in either direction. Cash, and {{dead_year}} a year of Konchar dead money for three seasons, {{dead_future}} of it landing in the two seasons after this one. Minnesota holds Cody Williams in return, with a club option of {{williams_option}}.

And the Dosunmu arithmetic, which is only arithmetic. With Dosunmu, Green and Kuminga all on the books Minnesota was **{{dos_stuck_over}} over the hard cap**, so something had to go. The contract forced the dump, not the acquisition. But the cheapest legal version of that move, a minimum player instead of Williams and Konchar, would have left Minnesota at {{dos_cheapest_apron}} and about {{dos_cheapest_tax}} of tax; what happened left it at {{dos_happened_apron}} and about {{dos_happened_tax}}. Taking Williams and Konchar back cost {{dos_dump_payroll}} of payroll and about {{dos_dump_tax}} more tax. Not re-signing Dosunmu at all would have kept Green, added a minimum guard, and let Minnesota pay Kuminga up to {{dos_nodos_kuminga}} from the non-taxpayer mid-level, landing exactly on the first apron with about {{dos_nodos_tax}} of tax.

The option, once more, because it's the one that decides next summer: {{k_y1}} now, {{k_y2}} next season at his choice, and a Non-Bird ceiling of {{k_nonbird}} if he leaves after one.

**The number, and the condition:** {{room_hard_cap}} of hard-cap room for the whole league year, enough for one minimum addition if nothing goes wrong.

## 8. What to watch

Every conclusion above is conditional on something, so here are the conditions, written as tests with thresholds set now, before the season starts. Each is checked at a team's {{w_game}}th game, late November. The thresholds are set outside the noise a {{w_game}}-game sample carries, so an ordinary early-season wobble doesn't trip them.

**{{w1_claim}}.** Now: {{w1_now}}. Flips if: **{{w1_flip}}**. This is the rotation coin flip from section 3, and it's the first thing to look at.

**{{w2_claim}}.** Now: {{w2_now}}. Flips if: **{{w2_flip}}**.

**{{w3_claim}}.** Now: {{w3_now}}. Flips if: **{{w3_flip}}**. And the bigger Boston test, at game {{bos_dec_game}}: net rating below {{bos_dec_threshold}} per hundred and the market's read of Boston beats the model's.

**{{w4_claim}}.** Now: {{w4_now}}. Flips if: **{{w4_flip}}**.

**{{w5_claim}}.** Now: {{w5_now}}. Flips if: **{{w5_flip}}**.

If Williams is under {{williams_threshold}} minutes at game {{w_game}}, the offseason verdict is officially unwritable and this piece said so in advance. If Boston is under {{bos_dec_threshold}} at game {{bos_dec_game}}, come back to section 1 and discount everything in it.

## Methods

The four views, the two aging bases, the quotability rule, the four cells, the allocators, the noise floor, the simulation, the market, the labels on every figure and the corrections made during the work are in one place for the whole series: the methods document (`methods.md`), rendered from the same sheet as this draft.

## Pull-quotes

1. "The model has Minnesota at {{title}} to win the title. The market has {{mkt_min}}. Every one of the four ways the model scores players ranks Minnesota below where the market does." (`title`, `mkt_min`, `min_view_ranks`)

2. "If you want to know whether to trust the model, don't watch Minnesota. Watch Boston: {{model_bos}} against a market price of {{mkt_bos}}, and a net rating below {{bos_dec_threshold}} through game {{bos_dec_game}} means the market was right." (`model_bos`, `mkt_bos`, `bos_dec_threshold`, `bos_dec_game`)

3. "Kuminga beats whoever else would have played his minutes, and it clears the model's own noise under every rule I can throw at it. The one thing that flips it is Joan Beringer taking those minutes instead." (`v_A_c3_default_shannon_pooled_u`, `v_A_c3_default_shannon_cells`, `v_D_beringer_fills_pooled_u`)

4. "'The offseason made Minnesota worse' is the sentence this piece can't write. It holds only while Cody Williams plays {{williams_threshold}} minutes a night or more, and only on one of the two aging bases." (`williams_threshold`, `off_delta_u`, `off_delta_a`)

5. "One good defender, assigned to Edwards, takes more off him than one good defender takes off anyone else: percentile {{e_pct_shipped}} of {{e_n_off}} top scorers. That's what a team with one creator looks like from the outside." (`e_pct_shipped`, `e_n_off`, `e_z_shipped`)

6. "'Defense travels' is not supported, and the estimate points the other way: {{ds_coef}} points per game per standard deviation of defensive lean, short of the bar." (`ds_coef`, `ds_se`, `ds_bar`)

## Numbers wanted

None. The six figures the first draft wrote around are on the sheet with their run IDs and in the prose (D92).

## Claims table

Every paragraph that carries a figure, with the sheet keys it uses and the run IDs behind them. The edit can be done against the sheet from this table alone.

{{CLAIMS_TABLE}}
