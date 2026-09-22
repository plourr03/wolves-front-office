# Minnesota's title odds, what Kuminga changes, and what the market can't see


**The short version, in five bullets.**

- **What the market says.** The betting market has Minnesota at 3.16% to win the title, 6th in the league, once you strip out the bookmakers' margin.
- **What the model says.** 1.68% on the primary basis, with the four ways of measuring players spanning 0.86% to 2.59%, and 2.39% once you correct for how players age. Every one of the four views ranks Minnesota below where the market has them, on both bases.
- **What ships about Kuminga.** He beats the player who would otherwise have played his minutes, and the gap clears the model's own noise under every way we can test it. The one alternative that flips it is Joan Beringer taking those minutes instead.
- **What the offseason verdict depends on.** "The offseason made Minnesota worse" is the sentence this piece can't write. It holds only while Cody Williams plays 12.6 minutes a night or more, and only on one of the two aging bases.
- **What to watch.** Five claims with thresholds set now, checked at game 20, and one bigger one about Boston checked at game 30.

## 1. The number

Here's the number everything else hangs off. The model gives Minnesota a **1.68%** chance of winning the title, and the market gives it **3.16%**.

Where each comes from, because the gap between them is the whole story. The market number is six sportsbooks' odds with the bookmakers' margin removed (their prices add up to 21.8% over a hundred, and every team gets shaved back proportionally). The model number is a season simulated 200,000 times per view, where a "view" is one of four ways of scoring how much each player helps his team, and 1.68% is the average of the four. The views themselves put Minnesota anywhere from 0.86% to 2.59%.

That's the primary basis, every player at last season's measured level. A second basis adjusts each player for a year of aging, and it's kinder to Minnesota because Minnesota is young: **2.39%**, spanning 1.18% to 3.59%. The piece quotes both, and I'd rather you saw the pair than a blend.

### Why the gap is real, and where it isn't

The honest way to compare a model to a market is to ask whether they agree on the shape of the league. They mostly do: ranking all thirty teams, they line up with a rank correlation of 0.78 to 0.83 across the four views (0.73 to 0.82 aged). They disagree about 20 specific teams by more than half a point of title odds, and on 16 of those every view sits on the same side of the market. Minnesota is one of them.

On the primary basis all four views price Minnesota below the market, and they rank it 13 to 16 against the market's 6th. That's not two estimates overlapping inside their error bars. The market's number sits outside the model's whole range.

On the aged basis the picture softens. Every view still ranks Minnesota below the market (9 to 15), but one of the four prices it above the market's 3.16% (the DARKO view, at 3.59%, with the box view at 3.03% just under). So the careful statement is this: the model ranks Minnesota lower than the market on both bases, and it prices Minnesota lower than the market in every view only on the primary one.

One caution before you lean on "all four views agree." The views aren't independent. Consensus is built partly out of RAPM and tracks it at a correlation of 0.977 across players, so when those two agree it's largely the same measurement twice. Four-way agreement means a finding doesn't hinge on one modeling choice. It isn't a confidence interval.

### The model's biggest claim, and its expiry date

If you want to know whether to trust any of this, don't watch Minnesota. Watch Boston. The model makes the Celtics a **18.33%** title team against a market price of **5.47%**, in every view (14.23% aged, still all four on the same side). That's the biggest disagreement the model has with anyone, and it comes with a date. If Boston's net rating through its 30th game, around the end of December, is below -1.7 per hundred possessions, the market's read on Boston beats the model's. The model's range for Boston is +3.3 to +10.1, and a 30-game net rating carries about 3.1 points of pure chance, so the threshold sits where chance alone would rarely put a team the model has right.

The same machinery prices Minnesota, so a Boston miss is a Minnesota caveat too.

Charlotte is on the list as well, and it comes with a confession. The model first priced Charlotte at 5.86%, +5.04 points over a market price of 0.81%. About half of that gap was a bug in our own possession data, which we found and fixed; the model now has Charlotte at 3.44%, a gap of +2.63. What's left is the real disagreement, and it still runs in the same direction.

### What actually ships

The model prices every offseason move Minnesota made, plus a few things that happened to it, and each gets a yes or no on whether it's solid enough to print. The rule is strict on purpose: a verdict ships only if it points the same way on both aging bases and under both ways of handing out minutes, and only if all four views clear the model's own noise in every one of those four combinations. A noise floor, since it comes up a lot, is the size of change the simulation could produce by luck alone, doubled.

7 of 13 candidates clear that bar.

| verdict | un-aged, mean points of title odds | aged | sign, un-aged / aged | views clearing, un-aged, aged |
|---|---:|---:|---|---|
| LaMelo Ball in | +0.79 | +0.91 | all positive / all positive | 4/4, 4/4 |
| Naz Reid out | -0.33 | -0.40 | all negative / all negative | 4/4, 4/4 |
| DiVincenzo's Achilles (not a transaction) | -0.39 | -0.33 | all negative / all negative | 4/4, 4/4 |
| Kuminga slot, default allocation | +0.55 | +0.66 | all positive / all positive | 4/4, 4/4 |
| Kuminga slot, McDaniels slides | +0.53 | +0.64 | all positive / all positive | 4/4, 4/4 |
| Kuminga slot, Beringer fills | -1.03 | -1.84 | all negative / all negative | 4/4, 4/4 |
| Kuminga slot, tight eligibility rule | +0.54 | +0.64 | all positive / all positive | 4/4, 4/4 |

Two of the seven are Minnesota's own decisions, Ball in and Reid out. One is an injury, DiVincenzo's Achilles, which ships as a cost and not as anyone's fault. Four are the same Kuminga comparison run under different rules for who else would have played his minutes: positive against three of them, negative if the answer is Beringer. The Kuminga section is about that.

It was 9 before this pass. Three that used to ship don't anymore, the other departures as a bundle, Randle out and the Dosunmu re-signing, all retired after we found the attribution model had been pricing every combination of moves on a roster without Cody Williams on it. Randle out is the one fans will ask about. Its sign now depends on which minutes rule you use, which is exactly the verdict the rule exists to keep off the page.

**The number, and the condition:** 1.68% modeled (2.39% aged) against 3.16% priced. The model ranks Minnesota below the market on both bases, the probability gap is all-views only on the primary basis, and all of it is only as trustworthy as a model that also makes Boston a 18.33% team, which December will test.

## 2. What the odds get right

Most of what gets argued about in September is unmeasurable, and this section is the evidence for that sentence. Every test here came back empty, and the empties are the point, not an apology for them.

### Style doesn't predict

The first thing everyone wants is a style overlay: this team plays fast, that team packs the paint, surely that matters in a series. We built one. Style interactions fixed in advance, fitted on two seasons and tested on games those seasons never saw. It made predictions **worse**: the average error rose by 0.0151 on 1,225 held-out regular season games and by 0.0265 on 251 held-out playoff games. The San Antonio matchup thesis couldn't be estimated from this data, and the series model runs without any style term at all.

### Nothing "translates" to the playoffs

Then the translation question: is there some regular season trait that predicts playoff success beyond plain net rating? We fixed 8 candidate features before looking, and tested them on 195 playoff series going back to the 2014 postseason. **0 of 8** added out-of-sample signal once you account for having tried eight things at once. That sample could have detected an effect of about 0.95 to 1.15 points per game, so this isn't a small-sample shrug.

"Defense travels" deserves its own line because it's the one everybody believes. It is not supported, and the estimate points the other way. At equal net rating, a team whose rating leans on defense did **-0.85 points per game** in its series per standard deviation of that lean, with a standard error of 0.34. That's a p-value of 0.011 against a bar of 0.0063, the bar being what you need after testing eight things. Its interval tops out at -0.18. Earlier seasons and recent seasons agree (-0.87 and -0.86), and three-point luck doesn't explain it (-0.77 once you add luck). It misses the bar, so it changes nothing in the model. But if you were going to bet on defense traveling, you should know the sign.

### Versatility and matchups are mostly noise

Versatility, the idea that some teams match up well against more of the field, turns out to be net rating restated. Under the series model, a team's swing in series odds across the contender field tracks its own net rating with a rank correlation of 1.00 outside the field. In the games themselves, a repeatable matchup effect is worth about 0.65 points per game since the 2013-14 season and 0.00 over 34,357 games since 1997-98. The ceiling on it is 1.25, which is worth at most 9 points of series probability in an even series.

Individual matchups, the "who guards Ant" question, are the same story in miniature. A pairing of thirty possessions carries a standard error of 0.14 points per matchup possession, and a team's main defender on a star normally holds him 0.05 to 0.10 below his own average, because stoppers get the hard possessions. Judged against that norm, 2 of 79 observed West-field matchups beat it by two standard errors, where chance alone would give about 2.3.

### What champions actually looked like

Base rates, as counts, on the 3 clean seasons of odds we have. The preseason favorite won 1 of 3. The champion came from the market's top five 3 of 3 times, priced between 8.27% and 14.69%. Set against the 14 top-five teams that didn't win, only 3 of 20 features separate the champions: offensive rank, defensive rank and continuity. No style feature does.

The Knicks are the file that shows why. The market had them at 8.27%, 4th, with a win total of 53.5. They won 53, right on it. This project's model had them at 4.63%. The regular season was steady: +6.33 per game, +6.16 before the break and +6.67 after. Then the playoffs were a different team, **16-3 at +14.89**, and they were the only one of 16 playoff teams whose margin improved (+8.57, against an average of -7.39; Minnesota's was -9.19). What moved wasn't visible in September. Their top five players missed 46 regular season games and 2 in the playoffs, the top five's share of the minutes went from 0.579 to 0.673, and the bracket broke their way.

**The number, and the condition:** 0 of 8 translation features survive, and the conclusion rests on the belief that what decided last year's title (health, a shortened rotation, a bracket) wasn't knowable until April.

## 3. What the odds can't see, and what it means for Minnesota

The optimist's version, said the way a fan would say it: this roster finally has a second creator next to Ant, the bench can shoot, the West is wide open behind the top two, and nobody's model prices chemistry or a young team's growth. The pessimist's version: they traded two proven bigs for a point guard who hasn't stayed healthy, a wing on a one-year deal and a rookie center, and the depth chart is one injury from Cody Williams playing real minutes.

Both are about things the market prices badly. Here's what the data says about each.

### Health

Take one of Minnesota's top three players away for the playoffs and the model says its title odds fall by **0.87 points on average, 54% of what it has** (43% on the aged basis). Oklahoma City loses 6.04 (41%) and San Antonio 6.04 (44%). In raw strength the three teams lose about the same per player: 2.60, 2.73 and 2.70 points of net rating. The difference is shape. The contenders' loss sits in one star (Shai Gilgeous-Alexander at 4.89, Victor Wembanyama at 5.26); Minnesota's is spread across the three. With a tightened playoff rotation Minnesota loses the least of the three: 2.22 against 3.01 and 2.83. On the aged basis Minnesota loses 2.07 per player against 2.63 and 2.52, so the spread-not-concentrated reading holds on both bases. Which Minnesota player is costliest to lose doesn't hold on both bases, so this piece doesn't name one.

### The rotation, and the coin flip in it

The model gives Cody Williams **16.1 minutes a night**. That's an assumption, not a projection, and here's why it matters more than a tenth man's minutes should. Williams is the lowest-ranked of the ten men who play, 0.0293 behind Jaylen Clark on the rank score that orders the rotation (Williams 0.3041, Clark 0.3333). With DiVincenzo out, both play. With DiVincenzo healthy, one of them gets cut, and that gap is the difference between Williams at 16.1 and Williams at zero. It's a coaching decision the model is guessing at.

And it carries a verdict. Below 12.6 minutes a night for Williams, the four views stop agreeing that the offseason made Minnesota worse. The model's negative read on the summer is, in part, a read on a rotation call nobody has made.

Double-big lineups can be evaluated now that the roster is set: 161 of 749 legal fives use two bigs, and 294 play without Gobert. 9 of the ten best-graded fives include Joan Beringer, whose rating rests on a rookie season of 7.9 minutes a game. Those fives are composed from individual ratings, not observed, and they rest on a rookie sample, so I'm not going to tell you what the closing five looks like. Only 5 of the 749 fives have ever played a possession together.

One thing from last season's data that people get wrong: the two Gobert frontcourts were level. Reid next to Gobert was +3.2 per hundred possessions, Randle next to Gobert was +3.3. The case for the offseason was never "Reid was carrying the frontcourt."

### Usage

Last season's usage doesn't fit on one floor. The projected top five adds up to the **87th percentile** of 7,380 league starting fives; with Kuminga in for Dosunmu it's the **96th**, and the **98th** at three-season rates. Last season's actual five was the 56th. Somebody's shots go away.

The base rate says whose. When a new high-usage pairing forms, the treated player's usage drops and his efficiency doesn't: adjusted for who the players were, -0.4 points of usage and -0.1 of true shooting across 34 player-seasons, and at the level where Edwards and Ball sit, -1.5 of usage (standard error 0.9) and +0.8 of true shooting, on only 9 cases. Pairings cost shots, not points per shot.

### The path

Minnesota's most likely seed is **7th (31%)**, and its chance of a top-six seed is **42%**. Its first-round opponent is San Antonio or Oklahoma City **53%** of the time, which are the two teams it beats least. It reaches the second round 28% of the time, and once there it wins the title 6.1% of the time. Title equity is a first-round problem.

**The number, and the condition:** losing any one of its top three costs Minnesota about 54% of its title odds on average (43% aged), and every rotation figure above depends on Williams's 16.1 minutes surviving a coaching staff.

## 4. Kuminga, better and worse

The optimist: he's the athletic four they've been missing since Randle stopped being one, he's cheap, he's young, and he's an upgrade on whoever else was going to soak up those minutes. The pessimist: he couldn't stick in Golden State, his units cratered next to a non-shooting center, which is exactly what Gobert is, and his playoff numbers are ugly enough that you don't need a model.

Here's the data, sorted into better and worse.

### Better

He beats the most likely internal fill for his minutes. Against the default answer to "who plays the four if not him," the model gives +0.44 points of title odds on the primary basis and +0.56 aged, or +0.55 and +0.66 under the headline's own minutes rule. Every view clears its noise floor in all four of those cells (4/4, 4/4, 4/4, 4/4). It clears on size, not just sign, and it clears under both allocators and both aging bases, which is the strictest test this piece applies to anything. The two sizes differ mostly because the allocators give him different minutes: 25.2 a night under the headline's rule, 22.0 under the pooled one.

As a defender assigned to a top scorer, in last season's data pooled with the two before it, he held scorers slightly below the norm: percentile 23 of 309 defenders, where low is good (-1.3 standard errors, inside the noise; 13 pairings, 711 possessions).

He's not a primary creator competing with Edwards and Ball for the ball: usage 0.226 last season, below the high-usage line, with 44% of his makes unassisted (percentile 69, on 157 makes).

### Worse, or uncertain

The slot verdict depends on who the alternative is. If Beringer took those minutes instead, the comparison runs the other way, -0.72 on the primary basis and -1.31 aged (-1.03 and -1.84 under the headline's minutes rule), and that clears too. The model likes Beringer a lot on a rookie sample. Whether it should is a different question, and it's the biggest single uncertainty in the Kuminga verdict.

As a scorer against the defender a team assigns him, he's about at the norm: percentile 36 of 245 (-0.2 standard errors, 29 pairings, 1,415 possessions over three seasons; last season alone gives 3 pairings, too few to say anything).

Next to a non-shooting center at Golden State, his units were -2.1 per hundred possessions against +0.6 without one, on 5,340 and 5,672 possessions, with a three-point attempt rate of 0.430 against 0.448. The gap sits inside the noise (standard error 3.5), so it's not evidence on its own. It is the Gobert question in miniature.

In the playoffs, all of it pooled: 40 games and 1,139 possessions, **on-court net -16.2**. In the 23 games with lineup data, with garbage time removed, his team was -16.0 per hundred possessions worse with him on than off (standard error 8.4). Small, and confounded by who else was on the floor, but blowouts don't explain it.

He adds to the crunch. The projected five with him in is the 96th-percentile usage five.

### The contract

Two years from the taxpayer mid-level exception: **$6,064,000** this season and **$6,367,200** next, a player option on the second year, $12,431,200 in all. The team's release disclosed no terms, so these are reported figures, corroborated by the exception amount to the dollar. If he opts out after one season, he'll have one season of service and Minnesota holds only Non-Bird rights, which cap a re-signing at **$7,276,800**. If he opts in and plays both years, Minnesota holds Early Bird rights. The option model has him opting out with a probability between 0.53 and 0.84 across the views.

**The number, and the condition:** +0.44 points of title odds against the default fill, conditional on the alternative not being Beringer and on one season that the option may make the only one.

## 5. Edwards, and why Ball is here

The optimist: Ball is the second creator Ant has never had, defenses can't send everything at one guy anymore, and Ant's off-ball game is about to get room it's never had. The pessimist: two ball-dominant guards, one ball, neither one defends, and the usage crunch is going to land on somebody's efficiency.

Here's the thing the evidence actually says about Edwards, and it's more specific than either.

### The most guardable star

Across the league last season, the defender a team assigned to Edwards held him further under his own level than that assignment holds almost any other scorer: **percentile 1 of 150 top scorers**, -5.6 standard errors over 21 pairings. That's a single-season finding, so it got the confound checks. Build the baseline only from rotation defenders and it's percentile 1. Drop the playoffs and it's 5. Do both and it's 5. Over three seasons he is the lowest of 245 scorers (percentile 0, -8.6 standard errors, 72 pairings).

Read that carefully, because it's not "Edwards is bad." It's that one good defender, assigned to him, takes more off him than one good defender takes off anyone else. That's what a team with one creator looks like from the outside.

### The creators

Edwards made 61% of his baskets unassisted last season (percentile 95), Ball 55% (percentile 84), against a league median of 35%. Two of them on the floor is the point.

### What the pairing should cost

New high-usage pairings cost usage, not efficiency. Adjusted for who the players were, -0.4 points of usage and -0.1 of true shooting across 34 player-seasons, and -1.5 and +0.8 at the star level where Edwards (0.309) and Ball (0.306) sit.

So the argument is simple, and it's the one genuinely opinionated sentence in this piece. If a team's assigned defender can hold Edwards this reliably, the fix isn't a better Edwards. It's a second creator the assignment can't also cover. That's why Ball is here, and the base rate says the pairing should cost shots, not efficiency.

**The number, and the condition:** percentile 1 as a scorer against his assigned defender, and the argument holds only if Ball draws that assignment often enough to loosen it.

## 6. Clutch

The optimist: Ant is a closer, and close games are where stars earn the money. The pessimist: Ant's late-game shot selection is why they lose close games, and now there are two guys who want the last shot.

In the last five minutes of a close game, everyone gets worse and more baskets come unassisted. Across the league since the 2023-24 season, effective field goal percentage falls from **0.544 to 0.502** in the clutch, and the unassisted share of makes rises from **37% to 45%**. That's the baseline every "closer" has to be judged against, and almost nobody clears it. Of 22 creators with enough clutch shots, **2** beat that league-wide drop by two standard errors (Derrick White at +2.3, Jamal Murray at +2.0), where chance alone would give about 1.0.

Edwards shot 0.546 on 306 clutch attempts, +1.3 standard errors better than the drop. Ball shot 0.460 on 100, -0.1. Both inside the noise. Neither the closer story nor the choker story survives contact with the sample size.

One split you won't find here. The late-clock split, how each creator does when the shot clock is nearly out, was withheld. Play-by-play doesn't record the shot clock, so it has to be reconstructed, and our reconstruction read within two seconds of zero at recorded violations 79.9% of the time against a bar of 80% that was set in advance. It missed the bar, so it doesn't get printed.

**The number, and the condition:** 2 of 22 creators beat the clutch drop, which is about what chance gives, and that holds until somebody's sample gets big enough to say otherwise.

## 7. What to watch

Every conclusion above is conditional on something, so here are the conditions, written as tests with thresholds set now, before the season starts. Each is checked at a team's 20th game, late November. The thresholds are set outside the noise a 20-game sample carries, so an ordinary early-season wobble doesn't trip them.

**Cody Williams' minutes decide whether the offseason verdict holds.** Now: 16.1 a night (model default). Flips if: **below 12.6 a night**. This is the rotation coin flip from section 3, and it's the first thing to look at.

**Minnesota's level is inside the model's range.** Now: model range -1.5 to +1.8 (four views, both aging bases). Flips if: **above +7.5 or below -7.2**.

**The model's two largest disagreements with the market.** Now: BOS: model 18.3% title odds vs market 5.5%, model net range +3.3 to +10.1. SAS: model 13.9% vs market 23.0%, range +4.2 to +8.7. Flips if: **BOS below -2.4; SAS above +14.4**. And the bigger Boston test, at game 30: net rating below -1.7 per hundred and the market's read of Boston beats the model's.

**The Edwards-Ball pairing costs usage, not efficiency.** Now: 2025-26 true shooting: Edwards 0.617, Ball 0.546. Unadjusted base rate for a new high-usage pairing: -0.3 points of true shooting (34 player-seasons). Flips if: **Edwards below 0.547, or Ball below 0.476**.

**Minnesota is not on a champion's path.** Now: projected rank 16 (un-aged) / 13 (aged); the 29 champions since 1997-98 ranked 11 at worst after 20 games (2005-06 MIA and 2022-23 DEN), median 2. Flips if: **3 or better (test); 11 or better (checkpoint)**.

If Williams is under 12.6 minutes at game 20, the offseason verdict is officially unwritable and this piece said so in advance. If Boston is under -1.7 at game 30, come back to section 1 and discount everything in it.

## 8. The bill

The cap chain closes to the dollar, so here it is. $217,621,829, minus Green's $14,679,012, plus Williams at $6,015,600 and Konchar at $6,165,000, minus $4,110,000 for stretching Konchar, minus $1 for a rounding difference on McDaniels, equals **$211,013,416**. Add Kuminga's $6,064,000 and it's **$217,077,416**: **$4,608,584 under the hard cap**, $8,062,416 over the first apron and $16,649,416 over the tax line.

What the Green dump cost: no pick and no swap, in either direction. Cash, and $2,055,000 a year of Konchar dead money for three seasons, $4,110,000 of it landing in the two seasons after this one. Minnesota holds Cody Williams in return, with a club option of $7,669,890.

And the Dosunmu arithmetic, which is only arithmetic. With Dosunmu, Green and Kuminga all on the books Minnesota was **$1,999,829 over the hard cap**, so something had to go. The contract forced the dump, not the acquisition. But the cheapest legal version of that move, a minimum player instead of Williams and Konchar, would have left Minnesota at $210,364,580 and about $8.7M of tax; what happened left it at $217,077,416 and about $23.3M. Taking Williams and Konchar back cost $6,712,836 of payroll and about $14.6M more tax. Not re-signing Dosunmu at all would have kept Green, added a minimum guard, and let Minnesota pay Kuminga up to $8,254,095 from the non-taxpayer mid-level, landing exactly on the first apron with about $7.0M of tax.

The option, once more, because it's the one that decides next summer: $6,064,000 now, $6,367,200 next season at his choice, and a Non-Bird ceiling of $7,276,800 if he leaves after one.

**The number, and the condition:** $4,608,584 of hard-cap room for the whole league year, enough for one minimum addition if nothing goes wrong.

## Methods appendix

**The four views.** Every player gets four impact scores, each in points per hundred possessions. RAPM is a regression that credits each player for how the score moved while he was on the floor, adjusted for everyone else on it. Box is a box-score model. DARKO is a public projection built from box-score trends. Consensus blends RAPM with a public box-score metric. Consensus tracks RAPM at a correlation of 0.977 across players, which means four-way agreement is weaker than it sounds: two of the four are largely the same opinion.

**The two aging bases.** The primary basis takes every player at last season's measured level. The aged basis shifts each player by the expected one-year change for his age, estimated league-wide. Aging helps Minnesota because Minnesota is young, so quoting only one basis would be a choice with a thumb on the scale, and the piece quotes both everywhere.

**The quotability rule.** A verdict ships only if its sign holds under both aging bases and under both minutes allocators (the one the headline simulation uses, which ranks a roster team-wide and plays ten men, and the one the attribution uses, which hands minutes out inside position groups), and only if every one of the four views clears its noise floor in all four of those cells. The noise floor is twice the size of change the simulation and its interpolation could produce on their own.

**The simulation.** 200,000 seasons per view, on both bases. Attribution prices every combination of Minnesota's offseason moves on a curve built from those simulations, and the curve is checked against the direct simulation every run.

**The market.** Six books' title odds, de-vigged proportionally: the raw prices add to 21.8% over a hundred, and each team's price is scaled back so the league sums to one.

**What was withheld.** The late-clock split. The reconstructed shot clock read within two seconds of zero at recorded violations 79.9% of the time against a bar of 80% fixed before the build, so no late-clock figure appears in the piece.

**Corrections made during the work.** Two bugs in our own data changed figures before publication. The lineup pipeline was crediting some baskets to the wrong team, 3.36% of all points on the 578 team-games we checked, which retracted two sentences (that Reid next to Gobert was clearly better than Randle next to Gobert, and that Kuminga's on-off flipped sign between his two teams) and moved several playoff lineup figures in the postmortem project. The same bug lived one level down, in the possession data that RAPM is fitted on, where it misplaced 2.84% of points across 96 team-games, so RAPM was refit on corrected points. Kuminga's net RAPM went from +1.37 to +1.82 (consensus +1.33 to +1.65) and Ball's from +1.95 to +3.86 (consensus +2.29 to +3.78); Edwards rose as well. The headline went from 1.69% to 1.68%, and from 2.55% to 2.39% on the aged basis, because the whole league was refit with them and it's position in the league that the simulation prices. The attribution model had also been pricing every combination of moves on a roster without Cody Williams; fixing that is what retired three of the verdicts that used to ship.

## Pull-quotes

1. "The model has Minnesota at 1.68% to win the title. The market has 3.16%. Every one of the four ways we score players ranks Minnesota below where the market does." (`title`, `mkt_min`, `min_view_ranks`)

2. "If you want to know whether to trust the model, don't watch Minnesota. Watch Boston: 18.33% against a market price of 5.47%, and a net rating below -1.7 through game 30 means the market was right." (`model_bos`, `mkt_bos`, `bos_dec_threshold`, `bos_dec_game`)

3. "Kuminga beats whoever else would have played his minutes, and it clears the model's own noise under every rule we can throw at it. The one thing that flips it is Joan Beringer taking those minutes instead." (`v_A_c3_default_shannon_pooled_u`, `v_A_c3_default_shannon_cells`, `v_D_beringer_fills_pooled_u`)

4. "'The offseason made Minnesota worse' is the sentence this piece can't write. It holds only while Cody Williams plays 12.6 minutes a night or more, and only on one of the two aging bases." (`williams_threshold`, `off_delta_u`, `off_delta_a`)

5. "One good defender, assigned to Edwards, takes more off him than one good defender takes off anyone else: percentile 1 of 150 top scorers. That's what a team with one creator looks like from the outside." (`e_pct_shipped`, `e_n_off`, `e_z_shipped`)

6. "'Defense travels' is not supported, and the estimate points the other way: -0.85 points per game per standard deviation of defensive lean, short of the bar." (`ds_coef`, `ds_se`, `ds_bar`)

## Numbers wanted

None. The six figures the first draft wrote around are on the sheet with their run IDs and in the prose (D92).

## Claims table

Every paragraph that carries a figure, with the sheet keys it uses and the run IDs behind them. The edit can be done against the sheet from this table alone.

| section | paragraph | opens | sheet keys | run IDs | labels |
|---|---|---|---|---|---|
| `summary` | `p3` | `- What the market says. The betting` | `mkt_min`, `mkt_min_rank` | `market_devig_20260919T195044Z` | observed |
| `summary` | `p4` | `- What the model says. {title} on` | `title`, `title_lo`, `title_hi`, `title_aged` | `run_sim_20260919T163222Z`, `run_sim_20260919T195138Z` | modeled |
| `summary` | `p6` | `- What the offseason verdict depends on.` | `williams_threshold` | `n8_watch_list_20260919T233400Z` | modeled |
| `summary` | `p7` | `- What to watch. Five claims with` | `w_game`, `bos_dec_game` | `n8_watch_list_20260919T233400Z` | assumed |
| `1. The number` | `p1` | `Here's the number everything else hangs off.` | `title`, `mkt_min` | `run_sim_20260919T163222Z`, `market_devig_20260919T195044Z` | modeled, observed |
| `1. The number` | `p2` | `Where each comes from, because the gap` | `overround`, `sims`, `title`, `title_lo`, `title_hi` | `market_devig_20260919T195044Z`, `merge_fcurve_parts_20260919T195006Z`, `run_sim_20260919T163222Z` | assumed, modeled, observed |
| `1. The number` | `p3` | `That's the primary basis, every player at` | `title_aged`, `title_lo_aged`, `title_hi_aged` | `run_sim_20260919T195138Z` | modeled |
| `Why the gap is real, and where it isn't` | `p1` | `The honest way to compare a model` | `rankcorr_lo`, `rankcorr_hi`, `rankcorr_lo_aged`, `rankcorr_hi_aged`, `n_disagree`, `n_allviews` | `market_devig_20260919T195044Z`, `r5_honesty_rail_bases_20260919T232922Z`, `f4_per_view_disagreement_20260919T195046Z` | composed |
| `Why the gap is real, and where it isn't` | `p2` | `On the primary basis all four views` | `min_view_ranks`, `mkt_min_rank` | `f4_per_view_disagreement_20260919T195046Z`, `market_devig_20260919T195044Z` | modeled, observed |
| `Why the gap is real, and where it isn't` | `p3` | `On the aged basis the picture softens.` | `min_view_ranks_aged`, `mkt_min`, `min_darko_aged`, `min_box_aged` | `r5_honesty_rail_bases_20260919T232922Z`, `market_devig_20260919T195044Z` | modeled, observed |
| `Why the gap is real, and where it isn't` | `p4` | `One caution before you lean on "all` | `cons_rapm_corr` | `d89_rapm_compare_20260922T010417Z` | composed |
| `The model's biggest claim, and its expiry date` | `p1` | `If you want to know whether to` | `model_bos`, `mkt_bos`, `model_bos_aged`, `bos_dec_game`, `bos_dec_threshold`, `bos_range_lo`, `bos_range_hi`, `dec_noise` | `market_devig_20260919T195044Z`, `r5_honesty_rail_bases_20260919T232922Z`, `n8_watch_list_20260919T233400Z` | assumed, composed, modeled, observed |
| `The model's biggest claim, and its expiry date` | `p3` | `Charlotte is on the list as well,` | `cha_model_pre`, `cha_gap_pre`, `mkt_cha`, `model_cha`, `cha_gap_now` | `market_devig_20260916T195853Z`, `market_devig_20260919T195044Z` | modeled, observed |
| `What actually ships` | `p2` | `{n_ship} of {n_candidates} candidates clear that bar.` | `n_ship`, `n_candidates` | `w2_aging_gate_20260919T232645Z`, `r7_allocator_agreement_20260919T233117Z` | fact, modeled |
| `What actually ships` | `p5` | `{v_ball_in_label} {v_ball_in_u} {v_ball_in_a} {v_ball_in_signs} {v_ball_in_clear}` | `v_ball_in_label`, `v_ball_in_u`, `v_ball_in_a`, `v_ball_in_signs`, `v_ball_in_clear` | `w2_aging_gate_20260919T232645Z` | fact, modeled |
| `What actually ships` | `p6` | `{v_reid_out_label} {v_reid_out_u} {v_reid_out_a} {v_reid_out_signs} {v_reid_out_clear}` | `v_reid_out_label`, `v_reid_out_u`, `v_reid_out_a`, `v_reid_out_signs`, `v_reid_out_clear` | `w2_aging_gate_20260919T232645Z` | fact, modeled |
| `What actually ships` | `p7` | `{v_ddv_injury_label} {v_ddv_injury_u} {v_ddv_injury_a} {v_ddv_injury_signs} {v_ddv_injury_clear}` | `v_ddv_injury_label`, `v_ddv_injury_u`, `v_ddv_injury_a`, `v_ddv_injury_signs`, `v_ddv_injury_clear` | `w2_aging_gate_20260919T232645Z` | fact, modeled |
| `What actually ships` | `p8` | `{v_A_c3_default_shannon_label} {v_A_c3_default_shannon_u} {v_A_c3_default_shannon_a} {v_A_c3_default_shannon_signs} {v_A_c3_default_shannon_clear}` | `v_A_c3_default_shannon_label`, `v_A_c3_default_shannon_u`, `v_A_c3_default_shannon_a`, `v_A_c3_default_shannon_signs`, `v_A_c3_default_shannon_clear` | `w2_aging_gate_20260919T232645Z` | fact, modeled |
| `What actually ships` | `p9` | `{v_C_mcdaniels_slides_label} {v_C_mcdaniels_slides_u} {v_C_mcdaniels_slides_a} {v_C_mcdaniels_slides_signs} {v_C_mcdaniels_slides_clear}` | `v_C_mcdaniels_slides_label`, `v_C_mcdaniels_slides_u`, `v_C_mcdaniels_slides_a`, `v_C_mcdaniels_slides_signs`, `v_C_mcdaniels_slides_clear` | `w2_aging_gate_20260919T232645Z` | fact, modeled |
| `What actually ships` | `p10` | `{v_D_beringer_fills_label} {v_D_beringer_fills_u} {v_D_beringer_fills_a} {v_D_beringer_fills_signs} {v_D_beringer_fills_clear}` | `v_D_beringer_fills_label`, `v_D_beringer_fills_u`, `v_D_beringer_fills_a`, `v_D_beringer_fills_signs`, `v_D_beringer_fills_clear` | `w2_aging_gate_20260919T232645Z` | fact, modeled |
| `What actually ships` | `p11` | `{v_E_tight_rule_F_or_FC_label} {v_E_tight_rule_F_or_FC_u} {v_E_tight_rule_F_or_FC_a} {v_E_tight_rule_F_or_FC_signs} {v_E_tight_rule_F_or_FC_clear}` | `v_E_tight_rule_F_or_FC_label`, `v_E_tight_rule_F_or_FC_u`, `v_E_tight_rule_F_or_FC_a`, `v_E_tight_rule_F_or_FC_signs`, `v_E_tight_rule_F_or_FC_clear` | `w2_aging_gate_20260919T232645Z` | fact, modeled |
| `What actually ships` | `p13` | `It was {n_ship_pre} before this pass. Three` | `n_ship_pre` | `w2_aging_gate_20260919T232645Z` | modeled |
| `What actually ships` | `p14` | `The number, and the condition: {title} modeled` | `title`, `title_aged`, `mkt_min`, `model_bos` | `run_sim_20260919T163222Z`, `run_sim_20260919T195138Z`, `market_devig_20260919T195044Z` | modeled, observed |
| `Style doesn't predict` | `p1` | `The first thing everyone wants is a` | `m1_rs_worse`, `m1_rs_n`, `m1_po_worse`, `m1_po_n` | `m1_style_model_20260910T135427Z` | modeled, observed |
| `Nothing "translates" to the playoffs` | `p1` | `Then the translation question: is there some` | `n3_n_features`, `n3_series`, `n3_start`, `n3_n_translating`, `n3_mde_lo`, `n3_mde_hi` | `n3_playoff_translation_20260916T212714Z` | assumed, composed, fact, modeled, observed |
| `Nothing "translates" to the playoffs` | `p2` | `"Defense travels" deserves its own line because` | `ds_coef`, `ds_se`, `ds_p`, `ds_bar`, `ds_ci_hi`, `ds_early`, `ds_late`, `ds_luck` | `n3_playoff_translation_20260916T212714Z` | assumed, modeled |
| `Versatility and matchups are mostly noise` | `p1` | `Versatility, the idea that some teams match` | `n4_rankcorr`, `n4_sd13`, `n4_start13`, `n4_sd97`, `n4_games97`, `n4_start97`, `n4_sd97_up`, `n4_series_up` | `n4_versatility_index_20260919T234720Z` | fact, modeled, observed |
| `Versatility and matchups are mostly noise` | `p2` | `Individual matchups, the "who guards Ant" question,` | `m3_se30`, `m3_norm_lo`, `m3_norm_hi`, `m3_edges`, `m3_rows`, `m3_chance` | `m3_opponent_cards_20260916T201505Z` | observed |
| `What champions actually looked like` | `p1` | `Base rates, as counts, on the {h2_n}` | `h2_n`, `h2_fav`, `h2_top5`, `h2_lo`, `h2_hi`, `h3_n_non`, `h3_n_sep`, `h3_n_feat` | `champions_table_20260919T195047Z`, `h1_h3_h5_profile_20260917T132715Z` | fact, observed |
| `What champions actually looked like` | `p2` | `The Knicks are the file that shows` | `nyk_mkt`, `nyk_rank`, `nyk_wt`, `nyk_wins`, `nyk_model`, `nyk_rs`, `nyk_pre`, `nyk_post`, `nyk_po_rec`, `nyk_po`, `nyk_po_teams`, `nyk_lift`, `nyk_lift_mean`, `nyk_cmp_lift`, `nyk_top5_rs_games_missed`, `nyk_top5_po_games_missed`, `nyk_top5_share_rs`, `nyk_top5_share_po` | `h4_knicks_case_file_20260916T190540Z` | modeled, observed |
| `What champions actually looked like` | `p3` | `The number, and the condition: {n3_n_translating} of` | `n3_n_translating`, `n3_n_features` | `n3_playoff_translation_20260916T212714Z` | assumed, modeled |
| `Health` | `p1` | `Take one of Minnesota's top three players` | `n5_min_drop`, `n5_min_share`, `n5_min_share_aged`, `n5_okc_drop`, `n5_okc_share`, `n5_sas_drop`, `n5_sas_share`, `n5_min_net`, `n5_okc_net`, `n5_sas_net`, `n5_okc_bigname`, `n5_okc_big`, `n5_sas_bigname`, `n5_sas_big`, `n5_min_po`, `n5_okc_po`, `n5_sas_po`, `n5_min_net_aged`, `n5_okc_net_aged`, `n5_sas_net_aged` | `n5_fragility_20260919T233508Z`, `n5_fragility_20260919T234118Z` | modeled |
| `The rotation, and the coin flip in it` | `p1` | `The model gives Cody Williams {williams_mpg} minutes` | `williams_mpg`, `rs_gap`, `rs_williams`, `rs_clark` | `build_rotations_20260919T163216Z` | assumed, composed |
| `The rotation, and the coin flip in it` | `p2` | `And it carries a verdict. Below {williams_threshold}` | `williams_threshold` | `n8_watch_list_20260919T233400Z` | modeled |
| `The rotation, and the coin flip in it` | `p3` | `Double-big lineups can be evaluated now that` | `m4_double`, `m4_fives`, `m4_nogobert`, `m4_top10_beringer`, `beringer_prior`, `m4_observed` | `m4_lineup_study_20260919T195041Z`, `build_rotations_20260919T163216Z` | composed, observed |
| `The rotation, and the coin flip in it` | `p4` | `One thing from last season's data that` | `reid_gobert`, `randle_gobert` | `lineup_evidence_20260917T133631Z` | observed |
| `Usage` | `p1` | `Last season's usage doesn't fit on one` | `m5_top_pct`, `m5_league_fives`, `m5_kin_pct`, `m5_kin3_pct`, `m5_obs_pct` | `m5_usage_accounting_20260916T203535Z` | composed, observed |
| `Usage` | `p2` | `The base rate says whose. When a` | `m5_adj_usg`, `m5_adj_ts`, `m5_treated`, `m5_star_usg`, `m5_star_usg_se`, `m5_star_ts`, `m5_star_n` | `m5_usage_accounting_20260916T203535Z` | observed |
| `The path` | `p1` | `Minnesota's most likely seed is {n2_modal} ({n2_modal_p}),` | `n2_modal`, `n2_modal_p`, `n2_top6`, `n2_sas_okc`, `n2_r2`, `n2_cond` | `seed_distribution_20260919T195022Z`, `n2_path_20260919T195039Z` | modeled |
| `The path` | `p2` | `The number, and the condition: losing any` | `n5_min_share`, `n5_min_share_aged`, `williams_mpg` | `n5_fragility_20260919T233508Z`, `n5_fragility_20260919T234118Z`, `build_rotations_20260919T163216Z` | assumed, modeled |
| `Better` | `p1` | `He beats the most likely internal fill` | `v_A_c3_default_shannon_pooled_u`, `v_A_c3_default_shannon_pooled_a`, `v_A_c3_default_shannon_tr_u`, `v_A_c3_default_shannon_tr_a`, `v_A_c3_default_shannon_cells`, `k_min_teamrank`, `k_min_pooled` | `r7_allocator_agreement_20260919T233117Z` | modeled |
| `Better` | `p2` | `As a defender assigned to a top` | `k_defender_pct`, `k_defender_ref`, `k_defender_z`, `k_defender_n`, `k_defender_poss` | `n6_kuminga_ledger_20260917T133322Z` | observed |
| `Better` | `p3` | `He's not a primary creator competing with` | `k_usg`, `k_unast`, `k_unast_pct`, `k_makes` | `m5_usage_accounting_20260916T203535Z` | observed |
| `Worse, or uncertain` | `p1` | `The slot verdict depends on who the` | `v_D_beringer_fills_pooled_u`, `v_D_beringer_fills_pooled_a`, `v_D_beringer_fills_tr_u`, `v_D_beringer_fills_tr_a` | `r7_allocator_agreement_20260919T233117Z` | modeled |
| `Worse, or uncertain` | `p2` | `As a scorer against the defender a` | `k_scorer_pct`, `k_scorer_ref`, `k_scorer_z`, `k_scorer_n`, `k_scorer_poss`, `k_scorer_n26` | `n6_kuminga_ledger_20260917T133322Z` | observed |
| `Worse, or uncertain` | `p3` | `Next to a non-shooting center at Golden` | `gsw_with`, `gsw_without`, `gsw_with_poss`, `gsw_without_poss`, `gsw_with_3par`, `gsw_without_3par`, `gsw_se` | `n6_kuminga_ledger_20260917T133322Z` | observed |
| `Worse, or uncertain` | `p4` | `In the playoffs, all of it pooled:` | `po_games`, `po_poss`, `po_net`, `po_onoff_games`, `po_onoff`, `po_onoff_se` | `n6_kuminga_ledger_20260917T133322Z` | observed |
| `Worse, or uncertain` | `p5` | `He adds to the crunch. The projected` | `m5_kin_pct` | `m5_usage_accounting_20260916T203535Z` | composed |
| `The contract` | `p1` | `Two years from the taxpayer mid-level exception:` | `k_y1`, `k_y2`, `k_total`, `k_nonbird`, `k_optout_lo`, `k_optout_hi` | `green_resolution_20260904T014022Z`, `player_option_20260919T195020Z` | fact, modeled |
| `The contract` | `p2` | `The number, and the condition: {v_A_c3_default_shannon_pooled_u} points` | `v_A_c3_default_shannon_pooled_u` | `r7_allocator_agreement_20260919T233117Z` | modeled |
| `The most guardable star` | `p1` | `Across the league last season, the defender` | `e_pct_shipped`, `e_n_off`, `e_z_shipped`, `e_pairings`, `e_pct_A`, `e_pct_B`, `e_pct_C`, `k_scorer_ref`, `e_scorer_pct3`, `e_scorer_z3`, `e_scorer_n3` | `m3_primary_defender_check_20260916T201455Z`, `n6_kuminga_ledger_20260917T133322Z` | observed |
| `The creators` | `p1` | `Edwards made {cr_edw} of his baskets unassisted` | `cr_edw`, `cr_edw_pct`, `cr_ball`, `cr_ball_pct`, `cr_median` | `m5_usage_accounting_20260916T203535Z` | observed |
| `What the pairing should cost` | `p1` | `New high-usage pairings cost usage, not efficiency.` | `m5_adj_usg`, `m5_adj_ts`, `m5_treated`, `m5_star_usg`, `m5_star_ts`, `usg_edw`, `usg_ball` | `m5_usage_accounting_20260916T203535Z` | observed |
| `What the pairing should cost` | `p3` | `The number, and the condition: percentile {e_pct_shipped}` | `e_pct_shipped` | `m3_primary_defender_check_20260916T201455Z` | observed |
| `6. Clutch` | `p2` | `In the last five minutes of a` | `cl_start`, `cl_efg_all`, `cl_efg_clutch`, `cl_un_all`, `cl_un_clutch`, `cl_n_ok`, `cl_n_big`, `cl_big1`, `cl_big1_z`, `cl_big2`, `cl_big2_z`, `cl_chance` | `n7_late_clock_20260916T230449Z` | composed, fact, observed |
| `6. Clutch` | `p3` | `Edwards shot {cl_edw_efg} on {cl_edw_fga} clutch attempts,` | `cl_edw_efg`, `cl_edw_fga`, `cl_edw_z`, `cl_ball_efg`, `cl_ball_fga`, `cl_ball_z` | `n7_late_clock_20260916T230449Z` | observed |
| `6. Clutch` | `p4` | `One split you won't find here. The` | `lc_g1`, `lc_bar` | `n7_late_clock_20260916T230449Z` | assumed, observed |
| `6. Clutch` | `p5` | `The number, and the condition: {cl_n_big} of` | `cl_n_big`, `cl_n_ok` | `n7_late_clock_20260916T230449Z` | observed |
| `7. What to watch` | `p1` | `Every conclusion above is conditional on something,` | `w_game` | `n8_watch_list_20260919T233400Z` | assumed |
| `7. What to watch` | `p2` | `{w1_claim}. Now: {w1_now}. Flips if: {w1_flip}. This` | `w1_claim`, `w1_now`, `w1_flip` | `n8_watch_list_20260919T233400Z` | assumed, composed |
| `7. What to watch` | `p3` | `{w2_claim}. Now: {w2_now}. Flips if: {w2_flip}.` | `w2_claim`, `w2_now`, `w2_flip` | `n8_watch_list_20260919T233400Z` | composed, modelled |
| `7. What to watch` | `p4` | `{w3_claim}. Now: {w3_now}. Flips if: {w3_flip}. And` | `w3_claim`, `w3_now`, `w3_flip`, `bos_dec_game`, `bos_dec_threshold` | `n8_watch_list_20260919T233400Z` | assumed, composed, modelled |
| `7. What to watch` | `p5` | `{w4_claim}. Now: {w4_now}. Flips if: {w4_flip}.` | `w4_claim`, `w4_now`, `w4_flip` | `n8_watch_list_20260919T233400Z` | composed, observed |
| `7. What to watch` | `p6` | `{w5_claim}. Now: {w5_now}. Flips if: {w5_flip}.` | `w5_claim`, `w5_now`, `w5_flip` | `n8_watch_list_20260919T233400Z` | composed, observed |
| `7. What to watch` | `p7` | `If Williams is under {williams_threshold} minutes at` | `williams_threshold`, `w_game`, `bos_dec_threshold`, `bos_dec_game` | `n8_watch_list_20260919T233400Z` | assumed, composed, modeled |
| `8. The bill` | `p1` | `The cap chain closes to the dollar,` | `chain_start`, `chain_green`, `chain_williams`, `chain_konchar`, `chain_stretch`, `chain_dollar`, `chain_post`, `chain_kuminga`, `chain_final`, `room_hard_cap`, `over_first`, `over_tax` | `green_resolution_20260904T014022Z` | fact |
| `8. The bill` | `p2` | `What the Green dump cost: no pick` | `dead_year`, `dead_future`, `williams_option` | `green_resolution_20260904T014022Z` | fact |
| `8. The bill` | `p3` | `And the Dosunmu arithmetic, which is only` | `dos_stuck_over`, `dos_cheapest_apron`, `dos_cheapest_tax`, `dos_happened_apron`, `dos_happened_tax`, `dos_dump_payroll`, `dos_dump_tax`, `dos_nodos_kuminga`, `dos_nodos_tax` | `dosunmu_final_states_20260904T014033Z` | fact |
| `8. The bill` | `p4` | `The option, once more, because it's the` | `k_y1`, `k_y2`, `k_nonbird` | `green_resolution_20260904T014022Z` | fact |
| `8. The bill` | `p5` | `The number, and the condition: {room_hard_cap} of` | `room_hard_cap` | `green_resolution_20260904T014022Z` | fact |
| `Methods appendix` | `p1` | `The four views. Every player gets four` | `cons_rapm_corr` | `d89_rapm_compare_20260922T010417Z` | composed |
| `Methods appendix` | `p4` | `The simulation. {sims} seasons per view, on` | `sims` | `merge_fcurve_parts_20260919T195006Z` | assumed |
| `Methods appendix` | `p5` | `The market. Six books' title odds, de-vigged` | `overround` | `market_devig_20260919T195044Z` | observed |
| `Methods appendix` | `p6` | `What was withheld. The late-clock split. The` | `lc_g1`, `lc_bar` | `n7_late_clock_20260916T230449Z` | assumed, observed |
| `Methods appendix` | `p7` | `Corrections made during the work. Two bugs` | `misplaced_lineup`, `val_lineup_teamgames`, `misplaced_possession`, `val_possession_teamgames`, `k_rapm_pre`, `k_rapm_post`, `k_cons_pre`, `k_cons_post`, `ball_rapm_pre`, `ball_rapm_post`, `ball_cons_pre`, `ball_cons_post`, `title_pre`, `title`, `title_aged_pre`, `title_aged` | `validate_stint_points_20260922T010709Z`, `validate_possession_points_20260922T010307Z`, `d89_rapm_compare_20260922T010417Z`, `run_sim_20260916T173222Z`, `run_sim_20260919T163222Z`, `run_sim_20260916T195902Z`, `run_sim_20260919T195138Z` | fact, modeled, observed |
| `Pull-quotes` | `p1` | `1. "The model has Minnesota at {title}` | `title`, `mkt_min` | `run_sim_20260919T163222Z`, `market_devig_20260919T195044Z` | modeled, observed |
| `Pull-quotes` | `p2` | `2. "If you want to know whether` | `model_bos`, `mkt_bos`, `bos_dec_threshold`, `bos_dec_game` | `market_devig_20260919T195044Z`, `n8_watch_list_20260919T233400Z` | assumed, composed, modeled, observed |
| `Pull-quotes` | `p4` | `4. "'The offseason made Minnesota worse' is` | `williams_threshold` | `n8_watch_list_20260919T233400Z` | modeled |
| `Pull-quotes` | `p5` | `5. "One good defender, assigned to Edwards,` | `e_pct_shipped`, `e_n_off` | `m3_primary_defender_check_20260916T201455Z` | observed |
| `Pull-quotes` | `p6` | `6. "'Defense travels' is not supported, and` | `ds_coef` | `n3_playoff_translation_20260916T212714Z` | modeled |
