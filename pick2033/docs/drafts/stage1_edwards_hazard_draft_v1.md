# Pricing the LaMelo Trade, Part 1: The Tenure Bet

DRAFT v1 (2026-07-02) from PROVISIONAL fit. Publication waits on the
July-6 freeze and one-shot refit. All bracketed slots fill from the FINAL
model. Per carry-forward ruling, no provisional hazard magnitudes appear.

---

The trade call came on June 25, and the headline wrote itself: LaMelo Ball
is a Timberwolf. Randle and Reid go out, the second apron slams shut behind
them, and the roster Minnesota takes into next season is faster, younger,
and stranger than the one that just won 49 games.

But the headline is not the price. The price is a promise with a date on
it: Minnesota's 2033 first-round pick, unprotected, plus the right to swap
first-rounders in 2028, 2029, and 2030. Charlotte did not trade LaMelo for
players. Charlotte traded LaMelo for futures contracts on the Minnesota
Timberwolves, and the single biggest variable in what those contracts pay
out is a question that sounds like talk radio and prices like an insurance
policy.

How long does Anthony Edwards stay?

Ask it the talk-radio way and you get vibes: he loves it here, he just
bought a house, did you see the interview. Ask it the way an actuary would
and you get something more useful. An insurer selling you a life policy is
not claiming to know your soul. It is claiming to know what happened to
forty years of people who looked like you on paper. That is exactly the
claim this piece makes about Edwards, and it is the only claim it makes.
Nothing here is a report on his intentions. It is a report on the history
of players in his situation, applied to his situation.

This is the first of three parts. Part 1 prices the tenure bet. Part 2
simulates both franchises to 2033, fifty thousand times, and turns the
simulation into a probability for every slot that 2033 pick can land on.
Part 3 prices the swaps the way a quant prices options and hands you the
full bill in championship currency. The house rule for all three parts is
the same: every number arrives with error bars, and where the honest answer
is wide, we print it wide.

## Every star tenure since 1990

Here is the dataset the tenure bet rests on. Take every player since 1990
who reached a star season, defined mechanically: an All-NBA selection, or a
top-20 league finish in Box Plus-Minus with at least 1,500 minutes. From
the first qualifying season with a franchise, follow him until he leaves,
retires, or the data runs out. Each of those runs is a spell. There are 304
of them, covering 1,290 player-seasons, and they ended in departure 238
times.

Sit with that ratio for a second. Of the star tenures that have finished,
the overwhelming majority finished with the star in another uniform. The
forever-star, the Duncan, the Dirk, the Curry, is not the norm. He is the
tail of the distribution. The typical spell runs about four seasons. Kevin
Garnett's twelve years in Minnesota, the longest anyone around here needs
reminding of, was already an outlier before it ended the way most spells
end.

The 238 endings are the training data. What separates the tenures that
lasted from the tenures that didn't turns out to be boringly consistent,
and two entirely different statistical machines agree on every direction
(a hierarchical Bayesian model and an old-fashioned Cox survival model,
fit separately as a check on each other).

Stars stay where the team wins. The strongest retention force in the data
is the simplest: trailing two-year win percentage. Deep playoff runs push
the same way; a conference finals trip in the last three seasons measurably
slows the exits. Small markets bleed stars faster than big ones, which
Minnesota fans did not need a regression to believe. The decorated dig in:
the more All-NBA selections a player has accumulated with a franchise, the
less likely he is to leave it in any given year. And seasons where a player
holds supermax leverage are exactly the seasons the relationship gets
renegotiated, one way or the other.

Then there is the covariate that does the most work, and it is the one
everyone forgets when the conversation stays on vibes: the contract clock.

## The walk-year cliff

A star in the middle of a long deal almost never changes teams by choice.
A star entering the final year of one is a different species. The history
is blunt about this. LeBron James left Cleveland in a walk year and left
Miami in a walk year; the same ledger that says so also shows Garnett's
2004 walk year passing quietly, buying Minnesota three more seasons before
the 2007 ending. The cliff does not say a star leaves. It says the walk
year is when the leaving happens, if it happens.

[POST-REFIT SLOT: walk-year hazard vs mid-contract hazard, final model,
with 80% intervals. Print the multiple, e.g. "a star's departure odds in a
walk year run Nx his mid-contract odds", plus the caveat sentence on the
inference: contract years reconstructed from salary histories with the
labeling audit described in the methodology notes.]

Building that clock honestly was its own small war, and the methodology
notes carry the details. The short version: we reconstructed
contract-years-remaining for every spell season from thirty-five years of
salary records, checked the reconstruction against contracts whose
structure is public record (Garnett's famous $126 million counts down
5-4-3-2-1-0 in our data, LeBron's two walk-year exits land on exactly the
right summers), and ran a simulation proving that the one systematic
labeling error we could not fully eliminate would have EXAGGERATED the
walk-year effect if left unfixed. We fixed it before fitting, and we wrote
the correction down before we knew what it would do to the answer.

## Edwards, through the machine

Now run Anthony Edwards through it, season by season, 2027 to 2033.

His age arc covers 25 to 31, entering the exact years where the historical
exits concentrate. His tenure clock passes seven seasons in 2027, deep
enough that the data treats him as a franchise fixture rather than a
flight risk on those grounds alone. Minnesota is a middle market, which
costs a little. He carries two All-NBA selections and counting, which
helps. The team-success term is whatever the Wolves make it, and Part 2
will let it breathe across fifty thousand simulated futures rather than
pinning it to one assumption.

And his contract is public record: signed through 2028-29, no options,
verified against two independent sources. The summer of 2029 is the walk
year. It sits three seasons before the pick conveys and one season after
the last swap. Charlotte's asset package is not spread evenly across the
future. It is clustered around the exact years the tenure math says are
the dangerous ones.

[POST-REFIT SLOT: the annual hazard curve 2027-2033, central scenario,
with 80% bands. Chart reference: edwards_hazard.json final export.]

[POST-REFIT SLOT: the cumulative departure probability through 2033 with
80% interval, stated in one plain sentence, followed immediately by the
interval-first framing sentence: the width IS the finding where it is
wide.]

[POST-REFIT SLOT: the scenario split. Cumulative curve under the
winning-team scenario vs the decline scenario, to make the one
controllable lever concrete.]

Two things about these numbers before anyone screenshots them. First, they
are conditional on scenarios, not prophecy; the full simulation in Part 2
replaces the scenarios with distributions. Second, the intervals are wide
because 304 spells is what history actually offers, and we would rather
hand you a wide honest number than a narrow fake one. The model passed its
discrimination gate on held-out data (it ranks who-leaves-when better than
chance by a solid margin), and its calibration is disclosed, warts
included, in the validation report.

## What this has to do with a draft pick

Everything. The swaps live in 2028, 2029, and 2030. The unprotected first
conveys in 2033. In the simulated futures where Edwards spends the whole
window in Minnesota, those picks mostly land in the twenties, and
Charlotte's package ages into a curiosity. In the futures where the tenure
bet goes bad, the frontier of bad Wolves seasons lines up with the exact
years Charlotte owns the right to profit from them. The value of what
Minnesota sent out is not a number. It is a distribution with two humps,
and the valley between them is the question this piece just priced.

Part 2 builds the futures: both rosters, aging curves, the new sixteen-team
lottery, all of it, run fifty thousand times. Part 3 opens the options
ledger and sends Charlotte the bill.

One more thing, because it is the piece's most practical sentence and it
belongs to the front office as much as the fans. Of every retention force
in forty years of star tenures, the strongest one is the only one a team
fully controls: winning. The cheapest way to keep the 2033 pick worthless
is the same as the best reason to have made this trade at all.

---

*Methodology notes: The model is a league-wide discrete-time hazard fit on
304 star spells (1990-2026), applied to Edwards' observable covariates. It
contains no information about any player's intentions and makes no claims
about them. Star definition, contract reconstruction and its audit,
validation gates (passed and failed alike), and every ruling made along
the way are documented in the project's public validation report. All
numbers in this piece come from the final post-July-6 model; the draft was
written before that model ran, with the numbers slotted, so the prose
could not be tuned to the result.*
