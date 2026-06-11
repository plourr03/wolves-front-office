# The Gobert Depreciation Curve and the Timed Reservation Price (feeds Piece 8, "The Price of Rudy")

_The closer's second act. Piece 2 argues the world is too low on Gobert. This prices the car-lot
question: does the trade-in value survive a year of waiting? Built on the existing machinery (the
both-out reservation price, the age curve, the availability model, the DARKO leaderboard, the
trade-comp database) plus the public transaction record for aging elite-defense centers._

Script: `gobert_depreciation.py`. Contract verified against HoopsHype (2026-06-06):
**$36.5M in 2026-27, a $38.0M player option in 2027-28 (his age-35 season), no trade kicker,
no no-trade clause.** The option is the cliff.

## The curve in one table

Net DPM projected forward from his current DARKO read (+2.0) by the standard age curve. Dollar
value uses his actual current DARKO value ($39.7M) and the empirically fit marginal slope (about
$9.1M of value per lost DPM point, R-squared 0.92 across high-minute players). "Window weight" is
P(healthy AND productive through that season): the recency-weighted suit-up rate (91%, he is
durable) aged forward, times the probability his net impact stays clearly positive.

| season | age | net DPM | DARKO $ value | salary | contract surplus | P(healthy) | P(productive) | window weight |
|---|---|---|---|---|---|---|---|---|
| 2025-26 (today) | 33 | +2.0 | $39.7M | $35.0M | **+$4.7M** | ~91% | high | -- |
| 2026-27 | 34 | +1.50 | $35.2M | $36.5M | **-$1.3M** | 91% | 87% | 79% |
| 2027-28 (the $38M option) | 35 | +0.95 | $30.2M | $38.0M | **-$7.8M** | 87% | 69% | 60% |
| 2028-29 (would be a new deal) | 36 | +0.07 | $22.2M | (free agent) | n/a | 82% | 32% | 26% |

**The surplus crosses negative this coming season, not in some distant future.** He is +$4.7M of
surplus today on a $35.0M salary. In 2026-27 two things happen at once: his salary steps up to
$36.5M and the age-34 decline knocks his value to about $35.2M, so the surplus flips to roughly
**-$1.3M**. On the $38M option year it is about **-$8M**. The asset that looks like a bargain in
June 2026 is a break-even-to-negative contract by opening night and a clear negative by the option
year. This is the single most important number in the piece: **his trade-value clock is already
past noon.**

(Caveats, both stated in the article: the projection holds his minutes roughly constant, so a
minutes decline would steepen the drop; and a rim-anchor's DEFENSE ages more gracefully than the
50/50 off/def split assumes, so the on-court decline could be a touch slower than modeled, though
the contract math is unchanged because the salary step-up is contractual.)

## What the market actually pays for an aging elite-defense center

The trade-comp database and the public record agree, and the pattern is steep. There is no comp in
which a defense-first center on a $30M-plus salary fetched a first-round haul after age 33. The
returns collapse from "a useful player plus a second" to "you attach an asset to move him":

| comp | age at trade | what the elite/good big returned |
|---|---|---|
| Rudy Gobert (2022) | 30 | four firsts plus a swap (the CEILING; not repeatable, and it is his own deal) |
| Marc Gasol, MEM to TOR (2019) | 34 | a younger starting center (Valanciunas) plus two role players plus a 2nd; a deadline contender buying defense for a title run |
| Kristaps Porzingis (2026 deadline) | 30 | role players and salary, ZERO picks in the deal |
| Gordon Hayward (2024 deadline) | 34 | moved as a big expiring for filler plus minor seconds |
| Al Horford, OKC to BOS (2021) | 35 | a NEGATIVE-value contract: a 2nd and a young body were ATTACHED to move him |
| Dwight Howard (early 30s) | 31-33 | a former three-time DPOY passed around for salary filler, then waived |

The lesson the comps teach is the lesson the surplus curve predicts: **a $35-38M defense-only
center in his mid-30s is priced by the league as a salary-matching piece, not as an asset, and the
moment the salary outruns the production you pay to move him (Horford at 35), you do not get paid.**

## The three windows, priced

**Window 1, now (June 2026, age 34, two years of control).** The realistic return is a useful
rotation player plus a second, with a protected first conceivable only if a defense-needy contender
bites. This is exactly the both-out finding: the best harvest package (a Charlotte-type deal for a
young rim-runner plus picks) prices NEGATIVE in present title equity under all four views
(consensus -0.50, box -0.72, RAPM -1.20, DARKO -0.43), and only CLEARS the bar to trade under the
single most Gobert-skeptical view (box), and even then only if you are optimizing 2027 over 2026-27.

**Window 2, the February 2027 deadline (half a season of age 34, plus the age-35 option year).**
This is the peak-return window, for three independent reasons. (1) Deadline urgency: a title
contender short a rim anchor in February pays a premium it would never pay in July, and Gasol-34 is
the proof that a deadline buyer is the one team that pays real value for an aging defensive center.
(2) He is still a controllable 1.5-year asset, not a pure rental, because the $38M option year is
still ahead of the buyer. (3) Information: you have banked half a season of Beringer's groomed
backup branch and half a season more evidence on which Gobert view is true (see below). His value
has only slipped a half-step (DARKO about +1.4), so the EV you sacrifice by trading has barely
moved. **This is the best risk-adjusted moment to trade him if you trade him at all.**

**Window 3, summer 2027 (age-35 $38M expiring, opt-in modeled as near-certain).** He opts in: $38M
at age 35 for a defense-only center is far above any market he could reach in free agency, so the
opt-in is as close to certain as these things get, and the asset becomes a one-year expiring at a
**-$8M contract surplus**. The realistic return is **negative**: this is the Horford-35 case, where
you attach a second (the target) or a lightly-protected first (the ceiling concession) to move him
for cap relief. The war-chest rationale that was the entire case for trading him has evaporated,
because there is no war chest in a negative return.

## The time-dependent reservation price (by view)

The both-out reservation price was a single snapshot. Depreciation makes it a curve. The price of
KEEPING him (the present title equity you sacrifice by trading him) scales with his on-court impact,
which the age curve erodes, so the reservation bar DROPS over time:

| view of Gobert | EV sacrificed, now | EV sacrificed, deadline | EV sacrificed, summer 2027 |
|---|---|---|---|
| box (+1.48) | +0.97pp | +0.81pp | +0.28pp |
| DARKO (+2.00) | +2.18pp | +1.91pp | +1.04pp |
| consensus (+5.28) | +3.87pp | +3.69pp | +3.10pp |
| rapm (+5.76) | +5.40pp | +5.17pp | +4.42pp |

Read it against the return curve and the crux appears. The reservation bar falls slowly (his
impact erodes gradually). The realistic return falls FAST and turns negative by summer 2027. So:

- **The gap between what you would need and what you would get is NARROWEST at the deadline**, where
  the offered return is at its peak (contender urgency) and the bar has only dipped a half-step.
- **By summer 2027 the gap is unbridgeable under every view**, not because the bar is high (it is at
  its lowest, +0.28 to +4.42pp) but because the OFFERED return is negative. You cannot clear even a
  +0.28pp bar with a package that costs you assets to execute.

## The explicit finding: does holding past this summer destroy value?

Yes, and the answer is sharp. **Holding past the February 2027 deadline destroys more value than
any realistic summer-2027 return adds.** The realized trade value swings from positive at the
deadline (a contender pays a real package for a 1.5-year DPOY-level anchor) to negative twelve
months later (a $38M age-35 expiring you attach a sweetener to move). That swing, from a positive
package to paying-to-move, dwarfs anything a summer-2027 deal could add. The summer-2027 window is
not a smaller version of the deadline window; it is the value-destruction cliff the option year
creates.

So the branch ranking, against "sell now" and "hold to 2027":

1. **Hold now, re-price at the deadline (BEST).** Preserves 2026-27 title equity (every both-out
   portfolio prices negative now), banks half a season of Beringer development and half a season of
   evidence on which Gobert view is real, and hits the one moment his defensive value commands a
   premium while his contract is still an asset. If a contender overpays at the deadline, you sell
   into strength. If no one does, you have lost nothing and you keep a still-useful +1.4 anchor for
   your own playoff run.
2. **Sell now (SECOND, and only conditionally).** Justified only if you believe the box or DARKO
   read AND you are committed to the 2027 reset, because it banks the war chest before further
   depreciation. It costs present title equity (-0.4 to -1.2pp) under every view.
3. **Hold to summer 2027 (WORST, avoid).** You spend the contention year holding him, then arrive at
   the negative-surplus cliff with no trade value and a $38M expiring. This is the one path the
   analysis affirmatively rejects.

## Does the depreciation soften the hold verdict? Plainly: under two views, yes

Per the instruction to say so if it does. **Under the box (+1.48) and DARKO (+2.00) views, the
depreciation curve softens the hold and converts it into a hold-to-the-deadline-then-sell lean.**
If Gobert is a good-not-irreplaceable center whose contract surplus goes negative this very season,
the disciplined move is to sell a melting asset at the deadline (its peak-return, maximum-information
moment) while a defensive-anchor market still exists, rather than ride it into the age-35 cliff. The
both-out work already showed the box view is the one where a trade clears; the depreciation curve
adds urgency to it and names the deadline as the window.

**The hold-and-contend verdict survives intact only under the consensus (+5.28) and RAPM (+5.76)
views.** There, even a depreciated Gobert is +4 to +5 next season, an elite anchor whose loss
craters the title number by more than any package returns, so you keep him through the contention
window regardless of the contract surplus. The keep-or-trade question is, as it was for the AD
trade, a referendum on which measurement of Gobert you believe. Depreciation does not resolve the
referendum. It sets a clock on it, and the clock says the deadline is when you must answer.

## The Beringer-information synergy

The deadline is the point of maximum information with trade value still alive, and that is the whole
argument for Window 2 over Window 1. By February 2027 you have roughly half a season of Beringer in
the groomed-backup branch (the cones put a young first-round big given real backup minutes behind a
starter at 46% rotation-rim-protector-or-better by 2027-28, so half a season of evidence materially
narrows that cone) and half a season more of the four-view question (does Gobert grade like a +1.5
or a +5 player on THIS roster). You learn whether you even need to replace his rim protection
internally before you decide whether to sell it externally, and you learn it while he is still a
controllable asset a contender will pay for. Waiting to summer 2027 buys a little more Beringer
information at the cost of all of Gobert's trade value. The deadline is where the two curves, rising
information and falling trade value, cross to MIN's advantage.

## One-line summary for the piece

He is +$4.7M of surplus today and a negative contract by opening night. The realistic return falls
from a real package now, to a contender's premium at the February deadline, to paying-to-move by the
summer-2027 option cliff. Hold him this summer, run the plan, re-price at the deadline with half a
season of Beringer on tape, and never let it reach the cliff. Under the two skeptical views, lean
toward selling AT that deadline rather than holding; under the two believing views, keep him for the
window. The clock, not the verdict, is what the depreciation curve settles.
