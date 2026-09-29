# Minnesota's title odds, what Kuminga changes, and what the market can't see (the short version)

*Draft, rendered from `piece_v2_draft_short.template.md`. Same claims and the same numbers as the full piece, fewer of them. Every number comes from `outputs/final_numbers.csv` by key.*

**The short version, in five bullets.**

- **What the market says.** Minnesota is 3.16% to win the title, 6th in the league, once the bookmakers' margin is stripped out.
- **What the model says.** 2.76% on the primary basis, and 3.72% once you correct for aging. Every one of the four ways of measuring players ranks Minnesota below where the market has them, on both bases.
- **What ships about Kuminga.** He beats the player who would otherwise have played his minutes, and the gap clears the model's own noise under every way I can test it. The one alternative that flips it is Joan Beringer taking those minutes instead.
- **What the offseason verdict depends on.** "The offseason made Minnesota worse" is the sentence this piece can't write. It holds only while Cody Williams plays 8.9 minutes a night or more, and only on one of the two aging bases.
- **What to watch.** Five claims with thresholds set now, checked at game 20, and one bigger one about Boston checked at game 30.

## 1. The number

The model gives Minnesota **2.76%** to win the title. The market gives it **3.16%**, 6th in the league.

The model number averages four ways of scoring players (the "views") over 200,000 simulated seasons each. Correct every player for a year of aging and it's **3.72%**, because Minnesota is young; the piece quotes both.

The model and the market agree on the shape of the league and disagree about 19 specific teams, Minnesota among them. On the primary basis all four views price it below the market and rank it 9 to 14 against the market's 6th. On the aged basis every view still ranks it below the market, but one view prices it above, so the probability gap is all-views only on the primary basis.

The model's biggest disagreement with the market isn't Minnesota, it's Boston: **18.12%** against a market price of 5.47%, in every view, and it has a date. If Boston's net rating through game 30 is below -1.7 per hundred possessions, the market's read beats the model's. Charlotte is on the list too, with a confession: the model first priced it at 5.86%, about half of that gap over the market was a bug in my own data, found and fixed, and it's 3.60% now against a market price of 0.81%.

7 of 13 offseason verdicts are solid enough to print: they point the same way under both aging bases and both minutes rules, and every view clears the model's own noise. Two are Ball in and Reid out, one is DiVincenzo's Achilles, and four are the same Kuminga comparison under different rules for who else plays his minutes.

**The number, and the condition:** 2.76% against 3.16%, only as trustworthy as a model that also makes Boston a 18.12% team.

## 2. What the odds get right

Most of what gets argued about in September is unmeasurable, and the tests say so. A style overlay made predictions worse, not better. Of 8 regular season traits tested as predictors of playoff success on 195 series, **0** survive. "Defense travels" is not supported, and the estimate points the other way (-0.85 points per game per standard deviation of defensive lean, short of the bar).

Base rates, as counts on 11 clean seasons of odds: the favorite won 4 of 11, and the champion came from the market's top five 10 of 11 times. 0 of 19 team-level features separate the champions from the 48 top-five teams that didn't win; of the style features, 0 of 8 do, on the three seasons that have them.

The Knicks are the illustration. Market 8.27%, 4th, steady all season, then **16-3 at +14.89** in the playoffs, the only one of 16 playoff teams whose margin improved. What decided the title wasn't knowable until April.

**The number, and the condition:** 0 of 8 translation features survive, and that rests on believing health, a shortened rotation and a bracket can't be priced in September.

## 3. What the odds can't see

The optimist says this roster finally has a second creator next to Ant and nobody's model prices chemistry. The pessimist says they traded two proven bigs for a point guard who hasn't stayed healthy and a wing on a one-year deal.

Health: lose any one of the top three and the model says Minnesota loses **55%** of its title odds (45% aged). The contenders' loss sits in one star; Minnesota's is spread across three, on both bases, so this piece names no costliest player.

The rotation: the model gives Cody Williams **0.0 minutes a night**, and that's an assumption. He's the lowest-ranked of the ten who play, 0.2050 behind Jaylen Clark on the score that orders the rotation, and when DiVincenzo is healthy one of them gets cut. Below **8.9** minutes a night for Williams, the four views stop agreeing that the offseason made Minnesota worse, so that verdict is partly a read on a rotation call nobody has made. Beringer-led lineups top the composed fives on a rookie sample, so there's no closing-five sentence here. And from last season's data, Reid next to Gobert (+3.2) and Randle next to Gobert (+3.3) were level.

Usage: the projected five with Kuminga in is the **96th percentile** of 7,380 league starting fives.

The path: modal seed **6th**, and San Antonio or Oklahoma City in the first round 34% of the time. Title equity is a first-round problem.

**The number, and the condition:** 55% of the odds ride on each of the top three, and every rotation figure depends on Williams's 0.0 minutes surviving a coaching staff.

## 4. Kuminga, better and worse

The optimist: an athletic four, cheap, young, an upgrade on whoever else soaks up those minutes. The pessimist: he couldn't stick in Golden State and the playoff numbers are ugly.

Better: he beats the most likely fill for his minutes by +0.51 points of title odds on the primary basis (+0.67 aged), clearing every floor under both aging bases and both minutes rules.

Worse, or uncertain: if Beringer took the minutes instead, it flips to -0.78 and clears the other way, on a rookie sample. In the playoffs, all of it pooled, 40 games and 1,139 possessions, on-court net **-16.2**; with garbage time removed, -16.0 worse on than off (standard error 8.4). Small, and confounded by who else was on the floor, but blowouts don't explain it.

The contract: $6,064,000 now, $6,367,200 at his option. Opt out after one season and Minnesota's Non-Bird ceiling is $7,276,800.

**The number, and the condition:** +0.51 against the default fill, conditional on the alternative not being Beringer.

## 5. Edwards, and why Ball is here

The optimist: Ball is the second creator Ant has never had. The pessimist: two ball-dominant guards, one ball, neither defends.

The defender a team assigns to Edwards holds him further under his own level than that assignment holds almost any other scorer: **percentile 1 of 150 top scorers** last season, -5.6 standard errors over 21 pairings, and it survives the checks for confounds. That isn't "Edwards is bad." It's what a team with one creator looks like from the outside.

Edwards made 61% of his baskets unassisted, Ball 55%, against a league median of 35%. New star pairings cost usage, not efficiency.

So: if one assigned defender can hold Edwards this reliably, the fix isn't a better Edwards, it's a second creator the assignment can't also cover.

**The number, and the condition:** percentile 1 against his assigned defender, holding only if Ball draws that assignment often enough to loosen it.

## 6. Clutch

The optimist: Ant is a closer. The pessimist: Ant's late shot selection loses close games.

In the last five minutes of a close game everyone gets worse: league-wide, effective field goal percentage drops from 0.544 to 0.502 and more baskets come unassisted. Only 2 of 22 creators beat that drop by two standard errors. Edwards and Ball are both inside the noise.

**The number, and the condition:** 2 of 22 beat the clutch drop, about what chance gives.

## 7. The bill

The cap chain closes to the dollar: $217,621,829 before the summer, **$217,077,416** after Green out, Williams and Konchar in, Konchar stretched, and Kuminga signed. And the Dosunmu arithmetic: with Dosunmu, Green and Kuminga all on the books Minnesota was $1,999,829 over the hard cap, so the contract forced the dump, not the acquisition. Taking Williams and Konchar back instead of a minimum player cost $6,712,836 of payroll and about $14.6M more tax.

**The number, and the condition:** $4,608,584 of hard-cap room for the whole league year, enough for one minimum addition if nothing goes wrong.

## 8. What to watch

Five claims, thresholds set now, checked at game 20. Williams: above 8.9 a night. Minnesota's level: above +8.7 or below -5.5. The two biggest market disagreements: BOS below -2.4; SAS above +14.4, with the bigger Boston test at game 30 below -1.7. The Edwards and Ball pairing: Edwards below 0.547, or Ball below 0.476. The champion's path: 5 or better at season's end (test); 11 or better after 20 games (checkpoint).
