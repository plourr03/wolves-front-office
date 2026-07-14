# Pricing the LaMelo Trade, Part 1: The Tenure Bet

DRAFT v4 (2026-07-13), narrative pass on v3 per Bobby's read ("good but kinda boring, more narrative, for someone without a math degree"). Every number, interval, source, and caveat is byte-identical to v3; changes are prose-only, concentrated in seven paragraphs (dataset intro, two-models paragraph, retention-forces paragraph, contract-clock lead-in, clock-audit paragraph, Edwards profile, validation-gates paragraph). All other paragraphs untouched from v3. Sources unchanged: star_spells_final.meta.json, edwards_hazard_FINAL.json, model_b_hazard_M2_FINAL.md, hazard_m2_full posterior. LaMelo status at fill time: unsigned (verified 2026-07-12, news check). RELEASE GATE: Bobby's numbers-in-place read.

---

The trade call came on June 25, and the headline wrote itself: LaMelo Ball is a Timberwolf. Randle and Reid go out, the second apron slams shut behind them, and the roster Minnesota takes into next season is faster, younger, and stranger than the one that just won 49 games.

But the headline is not the price. The price is a promise with a date on it: Minnesota's 2033 first-round pick, unprotected, plus the right to swap first-rounders in 2028, 2029, and 2030. Charlotte did not trade LaMelo for players. Charlotte traded LaMelo for futures contracts on the Minnesota Timberwolves, and the single biggest variable in what those contracts pay out is a question that sounds like talk radio and prices like an insurance policy.

How long does Anthony Edwards stay?

Ask it the talk-radio way and you get vibes: he loves it here, he just bought a house, did you see the interview. Ask it the way an actuary would and you get something more useful. An insurer selling you a life policy is not claiming to know your soul. It is claiming to know what happened to forty years of people who looked like you on paper. That is exactly the claim this piece makes about Edwards, and it is the only claim it makes. Nothing here is a report on his intentions. It is a report on the history of players in his situation, applied to his situation.

This is the first of three parts. Part 1 prices the tenure bet. Part 2 simulates both franchises to 2033, fifty thousand times, and turns the simulation into a probability for every slot that 2033 pick can land on. Part 3 prices the swaps the way a quant prices options and hands you the full bill in championship currency. The house rule for all three parts is the same: every number arrives with error bars, and where the honest answer is wide, we print it wide.

## Every star tenure since 1990

The bet rests on a pile of stories every fan base has lived some version of. Take every player since 1990 who reached a genuine star season (All-NBA, or a top-20 league finish in Box Plus-Minus with at least 1,500 minutes; the definition is mechanical so nobody's favorite gets argued in or out). Start the clock his first qualifying season with a franchise and follow him until he leaves, retires, or the data runs out. Each of those runs is a spell. There are 291 of them, covering 1,264 player-seasons, and they ended in departure 228 times.

Sit with that ratio for a second. Of the star tenures that have finished, the overwhelming majority finished with the star in another uniform. The forever-star, the Duncan, the Dirk, the Curry, is not the norm. He is the tail of the distribution. The typical spell runs about four seasons. Kevin Garnett's twelve years in Minnesota, the longest anyone around here needs reminding of, was already an outlier before it ended the way most spells end.

{{viz:spell-lengths}}

So what separates the tenures that lasted from the ones that didn't? We asked the question twice, with two statistical machines built on entirely different philosophies (a hierarchical Bayesian model, and an old-fashioned Cox survival model, the same tool hospitals use to study patient survival, fit separately as a check on each other), because a finding that only shows up under one lens is usually a mirage. The two machines agree on every direction. And before either one got a look, a fifth of the spells were sealed away in a holdout the model never trains on, kept aside so the finished product could be graded on stories it had never read.

The answers are almost embarrassingly familiar. Stars stay where the team wins: the last two years of win percentage push retention, deep playoff runs push the same way, and a conference finals trip in the last three seasons measurably slows the exits. Small markets bleed stars faster than big ones, which nobody in Minnesota needed a regression to believe. The decorated dig in: every All-NBA selection a player stacks with a franchise makes him a little harder to pry loose. And the seasons where a player holds supermax leverage are exactly the seasons the relationship gets renegotiated, one way or the other.

Then there is the force everyone forgets while the conversation stays on vibes: the contract clock. In the final model it does the most work, and it is not close.

{{viz:tenure-forces}}

## The walk-year cliff

A star in the middle of a long deal almost never changes teams by choice. A star entering the final year of one is a different species. The history is blunt about this. LeBron James left Cleveland in a walk year and left Miami in a walk year; the same ledger that says so also shows Garnett's 2004 walk year passing quietly, buying Minnesota three more seasons before the 2007 ending. The cliff does not say a star leaves. It says the walk year is when the leaving happens, if it happens.

In the final model, a star's departure odds in a walk year run roughly seventy times his mid-contract odds (80% interval: 43x to 104x; mid-contract here means two years left on the deal). If a 70x multiple sounds outrageous, translate it to probabilities: run Edwards' own 2029 profile through the machine with two years remaining on his deal and the departure hazard is about 1 percent; run the identical profile with zero years remaining and it is 44 percent. The cliff is not a metaphor. One caveat rides with the number wherever it goes: contract years were reconstructed from thirty-five years of salary histories, with the labeling audit described in the methodology notes.

Building that clock honestly was its own small war, and the methodology notes carry the scars. We rebuilt contract-years-remaining for every spell season from thirty-five years of salary records, then tested the rebuild against contracts whose structure is public record: Garnett's famous $126 million counts down 5-4-3-2-1-0 in our data, and LeBron's two walk-year exits land on exactly the right summers. One kind of labeling error survived every scrub, so we simulated it, and learned that left alone it would have made the cliff look even bigger than it is. We fixed it before fitting, and we wrote the correction down before we knew what it would do to the answer.

## Edwards, through the machine

Now run Anthony Edwards through it, season by season, 2027 to 2033.

The machine does not know about the house he bought or what he said at the podium. It knows his profile. His age runs 25 to 31 across the window, entering the exact years where history's exits concentrate. His tenure clock passes seven seasons in 2027, deep enough that the data reads him as a franchise fixture rather than a flight risk on those grounds alone. Minnesota is a middle market, which costs a little. He carries two All-NBA selections and counting, which helps. And the team-success term is whatever the Wolves make it, so Part 2 will let it breathe across fifty thousand simulated futures rather than pinning it to one assumption.

And his contract is public record: signed through 2028-29, no options, verified against two independent sources. The summer of 2029 is the walk year. It sits one season before the final swap and four drafts before the unprotected pick conveys.

Here is the curve the machine draws. With the Wolves winning at a .600 clip, Edwards' annual departure hazard is under 1 percent in 2027 and about 7 percent in 2028. At the 2029 walk year it spikes to 44 percent (80% interval: 35 to 53). Past the cliff, the curve is conditional on him having crossed it: the model assumes a star who survives his walk year re-signs on a fresh four-year deal (an assumption written down in advance and stress-tested in Part 3's tornado), so 2030 and 2031 fall to near zero, and the hazard climbs back to about 14 percent by 2033 as that hypothetical second deal ages toward its own cliff.

{{viz:edwards-hazard}}

Add it up and the machine's answer to the talk-radio question is this: a 56 percent chance Anthony Edwards has departed by the summer of 2033, with an 80 percent interval running from 45 to 68. Read the interval before the point estimate. History genuinely does not know, and the width is itself the finding: the pick Charlotte now owns is priced off something close to a coin flip, not a certainty in either direction.

{{viz:edwards-cumulative}}

The split between scenarios is the one controllable lever, and it is worth stating plainly. Keep the team winning at .600 and the cumulative departure number is 56 percent. Let the team sag to .450 and it is 71 percent (80% interval: 60 to 81). Fifteen points of Edwards-retention probability is what "just keep winning" is actually worth, before anyone says a word about vibes.

Two things about these numbers before anyone screenshots them. First, they are conditional on scenarios, not prophecy; the full simulation in Part 2 replaces the scenarios with distributions. Second, the intervals are wide because 291 spells is what history actually offers, and we would rather hand you a wide honest number than a narrow fake one. On the sealed holdout the model earned one green grade and one red one, and the public scorecard prints both. The green: it ranks who leaves, and when, well better than chance. The red: its exact probability levels drift outside the tolerance set in advance (calibration slope 1.413 against a 0.8-to-1.2 window, bootstrap 90% CI 1.13 to 1.87), and the validation report prints that red cell with its confidence interval rather than hiding it.

## What this has to do with a draft pick

Everything. The swaps live in 2028, 2029, and 2030, and the unprotected first conveys in 2033. The swaps have fine print (Minnesota's earlier obligations to other franchises complicate what Charlotte can actually capture in two of the three years, and Part 3 reads that fine print closely). The asset without fine print is the big one: the 2033 first, unprotected, sitting squarely on the far side of the walk year. In the futures where Edwards spends the whole window in Minnesota, that pick mostly lands in the twenties and Charlotte's package ages into a curiosity. In the futures where the tenure bet goes bad, it does not. Its value is a distribution, and its dangerous mass lives in the exact futures this piece just priced.

Part 2 builds the futures: both rosters, aging curves, the new sixteen-team lottery, all of it, run fifty thousand times. Part 3 opens the options ledger, reads the fine print, and sends Minnesota the honest bill.

One more thing, because it is the piece's most practical sentence and it belongs to the front office as much as the fans. Across forty years of star tenures, the strongest retention force a team actually controls is the simplest one: winning. The cheapest way to keep the 2033 pick worthless is the same as the best reason to have made this trade at all.

---

*Methodology notes: The model is a league-wide discrete-time hazard fit on 291 star spells (1990-2026), applied to Edwards' observable covariates. It contains no information about any player's intentions and makes no claims about them. Star definition, contract reconstruction and its audit, validation gates (passed and failed alike), and every ruling made along the way are documented in the project's public validation report. All numbers in this piece come from the final post-July-6 model; the draft was written before that model ran, with every model-dependent and dataset-dependent number slotted, so the prose could not be tuned to the result.*
