# Minnesota's title odds, what Kuminga changes, and what the market can't see (the short version)

*Draft, rendered from `piece_v2_draft_short.template.md`. Same claims and the same numbers as the full piece, fewer of them. Every number comes from `outputs/final_numbers.csv` by key.*

**The short version, in five bullets.**

- **What the market says.** Minnesota is ⟦⟧ to win the title, ⟦⟧th in the league, once the bookmakers' margin is stripped out.
- **What the model says.** ⟦⟧ on the primary basis, and ⟦⟧ once you correct for aging. Every one of the four ways of measuring players ranks Minnesota below where the market has them, on both bases.
- **What ships about Kuminga.** He beats the player who would otherwise have played his minutes, and the gap clears the model's own noise under every way I can test it. The one alternative that flips it is Joan Beringer taking those minutes instead.
- **What the offseason verdict depends on.** "The offseason made Minnesota worse" is the sentence this piece can't write. It holds only while Cody Williams plays ⟦⟧ minutes a night or more, and only on one of the two aging bases.
- **What to watch.** Five claims with thresholds set now, checked at game ⟦⟧, and one bigger one about Boston checked at game ⟦⟧.

## 1. The number

The model gives Minnesota **⟦⟧** to win the title. The market gives it **⟦⟧**, ⟦⟧th in the league.

The model number averages four ways of scoring players (the "views") over ⟦⟧ simulated seasons each. Correct every player for a year of aging and it's **⟦⟧**, because Minnesota is young; the piece quotes both.

The model and the market agree on the shape of the league and disagree about ⟦⟧ specific teams, Minnesota among them. On the primary basis all four views price it below the market and rank it ⟦⟧ against the market's ⟦⟧th. On the aged basis every view still ranks it below the market, but one view prices it above, so the probability gap is all-views only on the primary basis.

The model's biggest disagreement with the market isn't Minnesota, it's Boston: **⟦⟧** against a market price of ⟦⟧, in every view, and it has a date. If Boston's net rating through game ⟦⟧ is below ⟦⟧ per hundred possessions, the market's read beats the model's. Charlotte is on the list too, with a confession: the model first priced it at ⟦⟧, about half of that gap over the market was a bug in my own data, found and fixed, and it's ⟦⟧ now against a market price of ⟦⟧.

⟦⟧ of ⟦⟧ offseason verdicts are solid enough to print: they point the same way under both aging bases and both minutes rules, and every view clears the model's own noise. Two are Ball in and Reid out, one is DiVincenzo's Achilles, and four are the same Kuminga comparison under different rules for who else plays his minutes.

**The number, and the condition:** ⟦⟧ against ⟦⟧, only as trustworthy as a model that also makes Boston a ⟦⟧ team.

## 2. What the odds get right

Most of what gets argued about in September is unmeasurable, and the tests say so. A style overlay made predictions worse, not better. Of ⟦⟧ regular season traits tested as predictors of playoff success on ⟦⟧ series, **⟦⟧** survive. "Defense travels" is not supported, and the estimate points the other way (⟦⟧ points per game per standard deviation of defensive lean, short of the bar).

Base rates, as counts on ⟦⟧ clean seasons of odds: the favorite won ⟦⟧ of ⟦⟧, and the champion came from the market's top five ⟦⟧ of ⟦⟧ times. No style feature separates the champions from the top-five teams that didn't win (three most recent seasons).

The Knicks are the illustration. Market ⟦⟧, ⟦⟧th, steady all season, then **⟦⟧ at ⟦⟧** in the playoffs, the only one of ⟦⟧ playoff teams whose margin improved. What decided the title wasn't knowable until April.

**The number, and the condition:** ⟦⟧ of ⟦⟧ translation features survive, and that rests on believing health, a shortened rotation and a bracket can't be priced in September.

## 3. What the odds can't see

The optimist says this roster finally has a second creator next to Ant and nobody's model prices chemistry. The pessimist says they traded two proven bigs for a point guard who hasn't stayed healthy and a wing on a one-year deal.

Health: lose any one of the top three and the model says Minnesota loses **⟦⟧** of its title odds (⟦⟧ aged). The contenders' loss sits in one star; Minnesota's is spread across three, on both bases, so this piece names no costliest player.

The rotation: the model gives Cody Williams **⟦⟧ minutes a night**, and that's an assumption. He's the lowest-ranked of the ten who play, ⟦⟧ behind Jaylen Clark on the score that orders the rotation, and when DiVincenzo is healthy one of them gets cut. Below **⟦⟧** minutes a night for Williams, the four views stop agreeing that the offseason made Minnesota worse, so that verdict is partly a read on a rotation call nobody has made. Beringer-led lineups top the composed fives on a rookie sample, so there's no closing-five sentence here. And from last season's data, Reid next to Gobert (⟦⟧) and Randle next to Gobert (⟦⟧) were level.

Usage: the projected five with Kuminga in is the **⟦⟧th percentile** of ⟦⟧ league starting fives.

The path: modal seed **⟦⟧**, and San Antonio or Oklahoma City in the first round ⟦⟧ of the time. Title equity is a first-round problem.

**The number, and the condition:** ⟦⟧ of the odds ride on each of the top three, and every rotation figure depends on Williams's ⟦⟧ minutes surviving a coaching staff.

## 4. Kuminga, better and worse

The optimist: an athletic four, cheap, young, an upgrade on whoever else soaks up those minutes. The pessimist: he couldn't stick in Golden State and the playoff numbers are ugly.

Better: he beats the most likely fill for his minutes by ⟦⟧ points of title odds on the primary basis (⟦⟧ aged), clearing every floor under both aging bases and both minutes rules.

Worse, or uncertain: if Beringer took the minutes instead, it flips to ⟦⟧ and clears the other way, on a rookie sample. In the playoffs, all of it pooled, ⟦⟧ games and ⟦⟧ possessions, on-court net **⟦⟧**; with garbage time removed, ⟦⟧ worse on than off (standard error ⟦⟧). Small, and confounded by who else was on the floor, but blowouts don't explain it.

The contract: ⟦⟧ now, ⟦⟧ at his option. Opt out after one season and Minnesota's Non-Bird ceiling is ⟦⟧.

**The number, and the condition:** ⟦⟧ against the default fill, conditional on the alternative not being Beringer.

## 5. Edwards, and why Ball is here

The optimist: Ball is the second creator Ant has never had. The pessimist: two ball-dominant guards, one ball, neither defends.

The defender a team assigns to Edwards holds him further under his own level than that assignment holds almost any other scorer: **percentile ⟦⟧ of ⟦⟧ top scorers** last season, ⟦⟧ standard errors over ⟦⟧ pairings, and it survives the checks for confounds. That isn't "Edwards is bad." It's what a team with one creator looks like from the outside.

Edwards made ⟦⟧ of his baskets unassisted, Ball ⟦⟧, against a league median of ⟦⟧. New star pairings cost usage, not efficiency.

So: if one assigned defender can hold Edwards this reliably, the fix isn't a better Edwards, it's a second creator the assignment can't also cover.

**The number, and the condition:** percentile ⟦⟧ against his assigned defender, holding only if Ball draws that assignment often enough to loosen it.

## 6. Clutch

The optimist: Ant is a closer. The pessimist: Ant's late shot selection loses close games.

In the last five minutes of a close game everyone gets worse: league-wide, effective field goal percentage drops from ⟦⟧ to ⟦⟧ and more baskets come unassisted. Only ⟦⟧ of ⟦⟧ creators beat that drop by two standard errors. Edwards and Ball are both inside the noise.

**The number, and the condition:** ⟦⟧ of ⟦⟧ beat the clutch drop, about what chance gives.

## 7. The bill

The cap chain closes to the dollar: ⟦⟧ before the summer, **⟦⟧** after Green out, Williams and Konchar in, Konchar stretched, and Kuminga signed. And the Dosunmu arithmetic: with Dosunmu, Green and Kuminga all on the books Minnesota was ⟦⟧ over the hard cap, so the contract forced the dump, not the acquisition. Taking Williams and Konchar back instead of a minimum player cost ⟦⟧ of payroll and about ⟦⟧ more tax.

**The number, and the condition:** ⟦⟧ of hard-cap room for the whole league year, enough for one minimum addition if nothing goes wrong.

## 8. What to watch

Five claims, thresholds set now, checked at game ⟦⟧. Williams: ⟦⟧. Minnesota's level: ⟦⟧. The two biggest market disagreements: ⟦⟧, with the bigger Boston test at game ⟦⟧ below ⟦⟧. The Edwards and Ball pairing: ⟦⟧. The champion's path: ⟦⟧.
