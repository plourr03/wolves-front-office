# Pricing the LaMelo Trade, Part 3: The Bill

DRAFT v1 (2026-07-12). Beats and characterizations pre-registered in the 7/2 skeleton; swap prices filled from swap_pricing_FINAL.json (FINAL Engine D artifacts, both top1 branches, both currencies). Still slotted, pending their runs: the 2013 replay (Beat 4), the 15-arm tornado, the title-equity conversion and total_asset_cost decomposition (Beat 5), the resolved 2026 line item and the seconds (Beat 3). Prose around those slots written before they run. Two skeleton characterizations amended by the numbers, both flagged inline. RELEASE GATE: Bobby's numbers-in-place read after the remaining slots fill.

---

Charlotte's press release says Minnesota granted "swap rights in 2028, 2029, and 2030," and the phrasing does what press releases do: it makes three different financial instruments sound like triplets. They are not. Read the actual fine print, the pile of conditional language Minnesota's earlier trades left stapled to its own draft picks, and the three swaps come apart in your hands.

The 2028 swap is the clean one. Two picks, Charlotte takes the better, no strings.

The 2029 swap is an option so deep out of the money it barely exists. Minnesota's own 2029 first already belongs to Utah's pick pool unless it lands in the top five, leftover fine print from the Gobert trade, so Charlotte's swap right only wakes up in the narrow futures where the Wolves have gotten bad enough, fast enough, to keep their own pick. Rarely alive. Enormous when it is.

The 2030 swap is subordinated debt. Before Charlotte touches anything, Minnesota's pick passes through a San Antonio and Dallas stack that can strip its upside, and Charlotte swaps against whatever crawls out.

Those were the characterizations we wrote down before pricing anything. Now the machine has priced them, fifty thousand futures at a time, and two of the three survive contact. The third needed an amendment that tells you something about Charlotte.

## How you price an option on a basketball team

One paragraph of theory, no Greek letters. A swap right is worthless in most futures: if Charlotte's own pick is better, the right expires quietly and costs Minnesota nothing. Its entire value lives in the minority of futures where Minnesota's pick is the better one, which is why an average taken over all futures looks small while the thing itself is dangerous. And the three swaps are not independent bets, because they all ride the same underlying asset: if Edwards leaves in 2029, the 2029 swap, the 2030 swap, and the 2033 pick all get more valuable together. So the only honest total is computed path by path, summing what the package pays in each future and then looking at the distribution of that sum. Never add the averages of things that happen together.

Here is what each instrument pays, in the currency of a pick's first four seasons of value above a replacement player (4-year VORP), the same currency we use to grade drafts:

The 2028 swap exercises in 41.6 percent of futures. Its typical payoff is nothing, the median is zero, and its 90th-percentile payoff is 2.2 wins, with a mean of 0.7. Clean, modest, real.

The 2029 swap exercises in 12.3 percent of futures, and here is the fine-print stat of the piece: its 90th-percentile payoff is still zero. You can sit at the 90th percentile of futures and this option has paid Charlotte nothing. But its mean is 0.7, the same as the 2028 swap's, and both facts are true at once because when the 2029 swap finally wakes up, it pays about 5.3 wins on average, more than the 2033 pick's whole expected value. This is not a draft asset. It is a catastrophe insurance policy that Charlotte bought against exactly one event: the Wolves collapsing so hard by 2029 that a top-five pick stays home. It pays in the worlds Part 1 warned about, and almost nowhere else.

The 2030 swap is where the skeleton needed its first amendment. We characterized it as subordinated debt, upside pre-stripped by the San Antonio and Dallas stack, and structurally that is still true. But it prices as the most valuable swap of the three, not the least: exercised in 66.3 percent of futures, mean payoff 1.3 wins, 90th percentile 4.6. The reason is not Minnesota's side of the trade at all. It is Charlotte's. By 2030 the simulated Hornets are cresting, a median 49-win team picking in the twenties, and a swap right held by a good team is cheap to exercise against almost anybody. Charlotte did not buy 2030 upside from Minnesota. They bought the right to throw away their own late pick in the exact season they expect to stop needing it.

[SLOT: the resolved 2026 No. 28/No. 33 line item, one sentence, footnoted as slot-EV by design.]

[SLOT: the three second-rounders (2029, 2032, 2033), flat-valued at the E1 slot-31-45 average with the one-line sensitivity, so every asset in the package appears in the total exactly once.]

## Where the cost lives

Cut the fifty thousand futures into four world-states and ask each one what the full package pays Charlotte. Baseline, Edwards stays and the Hornets stay ordinary, is 24.7 percent of futures and pays 4.0 wins on average. Edwards leaves while the Hornets stay ordinary: 33.3 percent, paying 5.3. The Hornets ascend to a 45-win-or-better 2033 while Edwards stays: 18.0 percent, paying 4.2. And the quadrant where both things happen, Edwards gone and Charlotte good, is 24.0 percent of futures and pays 5.6.

The skeleton expected that last quadrant to be rare and brutal, a thin tail carrying an outsized share of the bill. That is the second amendment, and it is worse news than the expectation: the joint tail is not rare. A quarter of simulated futures put a departed Edwards and an ascendant Charlotte in the same timeline, partly because the same 2029 summer that decides Edwards' address also sits mid-crest on Charlotte's arc. The bill is not a lightning strike Minnesota is hoping to dodge. Every quadrant pays at least four wins on average; the bad quadrants just pay more. What Minnesota is actually hoping is that its own future comes from the left side of each quadrant's distribution, and to be fair, the path-level spread is wide: the total package pays less than nothing in about one future in ten (a late pick's first four years can be worth less than a replacement player) and more than 13 wins in another one in ten.

Add it up the honest way, path by path: the full package, the 2033 first plus all three swaps, pays Charlotte a mean of 4.9 wins of four-year value, median 3.1, with an 80 percent interval from minus 0.8 to 13.0. For scale, the unprotected 2033 first alone accounts for 2.2 of that mean, and its own interval runs from minus 1.4 to 8.1. The fine print about whether a No. 1 overall Minnesota pick in 2030 would still be swappable, a genuinely unresolved contract question, moves the total by about 0.2 wins, so we ran it both ways and it changes nothing that matters. Priced in win shares instead of VORP as a robustness check, the picture holds.

## We ran the machine on 2013

Numbers this far into the future have to earn trust somewhere, so we sent the machine back in time. Same pipeline, same models, fed only what was knowable in the summer of 2013, and pointed at the most infamous pick package in league history: the firsts Brooklyn sent Boston for Kevin Garnett and Paul Pierce. The picks that became the third selection in 2016 and the first selection in 2017, the ones that became Jaylen Brown and Jayson Tatum, plus a 17th and an 8th along the way. The question is not whether the machine predicts Brown and Tatum. Nothing predicts Brown and Tatum. The question is whether reality landed inside the intervals the machine would have printed at signing, or whether the truth of 2014 through 2018 lives in a tail the machine did not know it had.

[POST-REPLAY SLOT: the 2013 replay fan charts vs realized outcomes (2014: 17, 2016: 3, 2017 swap: 1, 2018: 8). Gate 8.5 verdict either way. If a realized outcome sits in the far tail, say so and explain what that means about tails rather than hiding it. Secondary: the 2019 PG package; the negative control.]

## The bill, both perspectives

[POST-PRICING SLOT: total asset cost in title equity, per-path sums, CRN-paired deltas only, no absolute title odds per the house gate. TWO co-equal numbers side by side: value delivered to Charlotte at their marginal title curve, and value forgone by Minnesota at ours. Headline unit is Bobby's call at fill time; both cumulative 4-year and per-season are computed.]

[SLOT: tornado. Which assumptions move the answer: hazard scale, blend schedule, phi/shock tails, slot-value currency, play-in handling, 2030 top1 flag, pooled-dynamics arm, CHA-lineage arm, S-CONTRACT arm, LaMelo extension scenario. Lead with whichever dominates; if one assumption rules, that finding leads the methodology notes.]

## The verdict, next to the basketball

[SLOT: one paragraph placing the asset bill beside the clean-room on-court evaluation, quoted in its own terms per its own gate. What Minnesota bought, in that evaluation's language.]

So here is the trade, stated in full and without a press release in the room. Minnesota bought the best passer the franchise has ever put next to Anthony Edwards, and it agreed to owe Charlotte a debt that pays out of Minnesota's own worst futures: a mean of about five wins of draft value, a quarter of it riding on a single unprotected pick seven years away, the rest spread across three options that all get expensive in the same timelines. The debt is survivable in the futures where the basketball works and heavy in the futures where it does not, which is the defining property of every bet worth arguing about.

And the collection date is already circled. Two max contracts in one building, two walk years, one summer: 2029. Part 1 priced one of those clocks. The other one ticks at the same rate, and as of today, nobody has stopped either of them.

---

*Methodology notes: swap payoffs computed per path on the FINAL 50,000-future simulation of Part 2, valued with the draft-slot value model (posterior curve draws with realized-outcome residuals, common random numbers within each path so payoff intervals carry real outcome risk); both top1-carries branches and both currencies reported in the public export; the 2029 swap priced on Charlotte-own-pick semantics, confirmed by the finalized trade language. Totals are per-path sums, never sums of marginal means. The replay, tornado, and title-equity conversion fill their slots when their pre-declared runs complete; this draft was written before they ran.*
