# Piece 2 skeleton: the season preview

**Status: drafted 2026-09-10 during the overnight run. Supersedes `piece_skeleton.md`.**

**Labelling rule, applied to every number below.** `[observed]` means it happened and is in the data. `[composed]` means it is a real measurement re-weighted or re-combined by us. `[modeled]` means it comes out of the simulation. `[assumed]` means we chose it and the piece must say so. Every figure carries a run ID. **If a number is not on `final_numbers.csv` it does not go in the piece.**

**Framing rule for every market comparison in this piece: never "the odds were wrong."** The market is a prior. The piece shows how good a prior it is and what information moved the winners inside it.

**Structural rule: no section ends in a verdict.** Each ends with its number and the condition that number depends on.

---

## 1. The number

Minnesota's modelled title probability for 2026-27 is **1.68%**, four-view band **0.82% to 2.57%**, on the un-aged basis `[modeled, run_sim]`. On the survivorship-corrected aged basis it is **2.54%, band 1.28% to 3.71%** `[modeled, w2_aging_gate]`. **Aging helps Minnesota, because Minnesota is young**, and the piece quotes both rather than picking.

The market says **3.16%**, sixth in the league, after de-vigging a 21.8% overround proportionally `[observed, market_devig]`.

**Lead with the gap, not the number.** The market's figure sits **outside** our four-view band. This is not two estimates overlapping inside their uncertainty; it is a disagreement our own spread does not cover, and the piece has to hold both numbers up rather than pick one.

**The honesty rail, and it belongs here rather than in a footnote.**

**The model and the market order the league at a correlation of 0.78 to 0.80** `[modeled, f4c]`. They agree about the shape of the league and disagree about twenty specific teams, and the disagreements are **not traceable to a single defect**. Five candidate explanations were tested and all five failed: thin-sample inflation (+2.16 against +2.07, no effect), return-from-absence pricing (five players league-wide, all marginal), wrong measured 2025-26 nets (correlation 0.9994 with actual margins), missing playoff rotation concentration (wiring it in moves Boston 2nd to 2nd), and shrinkage toward league average (the prior is a box-score prior, not league average) `[f1_disagreement_diagnosis]`.

**The depth-versus-stars story is dead as a number.** Correlation between a team's impact concentration and model-minus-market is **-0.065** across 30 teams `[f4c]`. And concentration does not predict playoff margin either: adding it to a series model gains **+0.039 in sample and -0.034 held out** `[f4d]`, which is what overfitting looks like. **No series adjustment is applied.**

**What can be said is which disagreements are the model's and which are the model arguing with itself.** Sixteen of the twenty are ALL-VIEWS, where all four forks sit on the same side of the market. Four are MIXED. **Boston is ALL-VIEWS**: every fork ranks it first or second, so it is not one instrument's artifact. **Charlotte is MIXED**: consensus and RAPM rank it fourth, box ninth and DARKO sixteenth, so most of Charlotte is a RAPM-family artifact and the piece should not defend it `[f4a]`.

**And the four views are not four independent instruments.** Consensus and RAPM correlate at **0.963** across rotation players, with a mean absolute difference of 0.42; box correlates 0.700 with consensus and has roughly half the spread (sd 1.06 against 1.85) `[f4b]`. "All four agree" is therefore closer to "two-and-a-bit agree", and it is a check that a finding does not hinge on one modelling choice, never a confidence interval.

**For Minnesota, both numbers go in the piece.** Market **3.16%, rank 6**. Model **1.68%, rank 14**, and Minnesota is **ALL-VIEWS below the market**: every fork puts them 13th to 16th. The market's number sits outside our four-view band, so this is not two estimates overlapping within uncertainty.

**The rule this piece follows: it names which number it would bet on only where the four views agree.** On Minnesota they agree with each other and disagree with the market, and the piece says exactly that rather than pretending the gap away or claiming the market is wrong.

**The number, and the condition it depends on:** 1.68% modelled against 3.16% priced, and the gap is only interpretable if you also accept that the same model has Boston first and Charlotte fifth.

---

## 2. What the number hides

The published offseason delta is **-0.951pp, ALL NEGATIVE across four views** `[modeled, w1c_decompose]`. Read alone it says the front office made the team worse. It is carrying three different things.

| component | mean | band | sign |
|---|---:|---|---|
| published offseason delta | -0.951pp | [-1.752, -0.350] | ALL NEGATIVE |
| what the DiVincenzo injury costs | **+1.714pp** | [+1.245, +2.889] | ALL POSITIVE |
| what the Cody Williams minutes cost | +1.006pp | [+0.716, +1.185] | ALL POSITIVE |
| interaction | -1.006pp | [-1.185, -0.716] | ALL NEGATIVE |
| **remainder, the offseason itself** | **+0.762pp** | **[-0.403, +2.535]** | **MIXED** |

**Once the injury and the minutes assumption come out, the offseason stops grading negative.** Three of four views think the moves helped `[modeled]`.

**The interaction is the whole story and it is exactly minus the Williams figure.** That is not rounding. **Healing DiVincenzo removes Williams from the rotation by itself**: with DiVincenzo out Williams ranks tenth and plays 16.1 minutes, with him healthy Williams is eleventh and plays none. The two repairs are one repair. Anyone adding them overstates the fix by a full point.

**And it is a knife edge.** Williams sits at rank score **0.3029** against Jaylen Clark's **0.3131** `[composed, build_rotations]`. A gap of **0.0101 in a percentile blend** decides sixteen minutes a night or zero, and therefore about a point of title probability. Present his minutes as a rotation coin-flip, never as a projection.

**And the headline delta fails the aging gate outright.** ALL NEGATIVE un-aged at -1.261pp, **MIXED aged at -0.398pp** `[modeled, w2_aging_gate]`. Under this project's own quotability rule a verdict ships only if it holds under both bases, so **"the offseason made Minnesota worse" does not ship.** It is conditional three separate ways: on the aging basis, on Cody Williams playing 12 or more minutes, and on counting a season-ending Achilles as an offseason outcome.

**The number, and the condition:** the offseason itself is +0.762pp MIXED, and the negative headline it replaces survives neither the aging gate nor the Williams range.

---

## 3. What champions had

**n = 3. Every figure in this section is a count out of three, not a rate, and must be written that way** `[observed, champions_table]`.

| season | champion | preseason | implied | rank | favourite won? |
|---|---|---|---:|---:|---|
| 2023-24 | Boston | +450 | 14.69% | 1 | yes |
| 2024-25 | Oklahoma City | +675 | 10.80% | 2 | no |
| 2025-26 | New York | +900 | 8.27% | 4 | no |

The favourite won **1 of 3**. The champion came from the top five **3 of 3**, and from the top four **3 of 3**. Champions' preseason implied probability ran **8.27% to 14.69%, median 10.80%**.

**Minnesota is priced at 3.16% and rank 6 on the market, 1.68% and rank 14 on the model.** No champion in this sample started below 8.27% or worse than rank 4.

**The useful comparison is the team that just did it.** The 2025-26 Knicks were the cheapest champion here at 8.27%, started fourth, **finished under their own win total at 53-29, and won four rounds anyway** `[observed]`. That is the shape of the argument available to Minnesota and it is why the Knicks are a case file rather than a curiosity.

**The number, and the condition:** the champions' band is 8.27% to 14.69% at n = 3, and Minnesota sits outside it on both the market and the model.

---

## 4. Kuminga, better and worse

**The optimistic case, at its strongest.** He is 23, he cost the taxpayer mid-level, and against the player most likely to take his minutes he grades positive **under all four views, +0.174 to +0.704pp, mean +0.488** `[modeled, slot_robustness]`. That verdict is **unconditional across the entire Cody Williams minutes range**, strengthening from +0.44pp to +1.39pp as Williams plays less `[modeled, williams_minutes_sensitivity]`. It is the one claim in this project that got sturdier every time it was stress-tested.

**And it survives the aging gate**, the strictest test this project applies: the same ALL POSITIVE sign under both the un-aged basis (+0.488) and the survivorship-corrected aged basis (+0.615) `[modeled, w2_aging_gate]`. Nine verdicts cleared that gate and five did not. This is one of the nine.

**The pessimistic case, at its strongest.** The magnitude does not clear the machinery's own error, under either basis. The weakest of the four views sits below its own noise floor both times: **0.174 against a floor of 0.479 un-aged, 0.209 aged, 3 of 4 views clearing either way** `[modeled, noise_floor_slot]`. So the honest form is fixed by what the floor supports: **positive in sign under every view and under both aging bases, and too small for one view of four to resolve under either.** Not "worth half a point". Positive, and smaller than one of our four instruments can measure.

Promote Joan Beringer into the slot instead and all four views go **negative, -1.10 un-aged and -1.96 aged**, and that result clears the floor on all four. The positive case and the negative case are both real. Which one you get is a rotation decision.

**The evidence.** Kuminga's own on/off flips sign between his two 2025-26 teams: **-6.53 at Golden State over 971 possessions, +2.90 at Atlanta over 1,077** `[observed, lineup_evidence]`. Neither is an effect at that sample. His three-point rate rose from 27.3% to 35.9% between them and his accuracy rose with it, 32.1% to 34.6%; in the playoffs the rate rose again to 40.0% and the accuracy collapsed to 20.8% `[observed]`.

**The number, and the condition:** +0.488pp mean, positive under every view, conditional on the alternative being Shannon or Williams rather than Beringer, and not resolvable on one view of four.

---

## 5. The rotation

**The optimistic case.** The minutes rule now prices a player who changed teams on the rank he earns with his new team rather than the role he left, applied identically to all 30 `[assumed, rotation.MOVER_CURVE_WEIGHT = 0.8]`. Under it Kuminga rises to 25.2 minutes and Ball to 30.6, and the correlation between a mover's impact and his minutes change is **+0.774** league-wide, which is the rule working `[composed, build_rotations]`.

**The pessimistic case.** The rule re-optimises **only movers**. A badly-allocated incumbent stays badly allocated, so a mover-heavy team gets a better rotation for a reason about the method rather than the roster. League-wide the mean team gain is **+0.020 net points and it correlates 0.56 with the number of movers** `[modeled]`. Minnesota gains +0.074, and **69% of that is Cody Williams alone**; the rest sits at the league mean and cancels.

**The evidence.** Projected minutes: Edwards 34.8, Gobert 34.3, McDaniels 30.4, Ball 30.6, Dosunmu 25.4, Kuminga 25.2, Williams 16.1, Hyland 17.5, Clark 14.8, Beringer 10.9 `[composed]`.

**The number, and the condition:** Williams at 16.1 minutes, and everything in section 2 depends on that surviving contact with a coaching staff.

---

## 6. The matchups

**The optimistic case.** The postmortem found San Antonio actively suppressing Edwards' catch-and-shoot looks and pushing him into the floater zone. If style matchups are real and estimable, Minnesota's path can be read rather than guessed.

**The pessimistic case, and it is the one the data supports.** **It could not be estimated.** Five style interactions fixed in advance, fitted on 2023-25 and held out on 2025-26 and on three postseasons, made predictions **worse on both held-out samples**: MAE gain -0.0085 on 1,225 regular-season games and **-0.0395 on 251 postseason games, roughly 43 series** `[modeled, m1_style_model]`.

**So the overlay is off, and the piece says so plainly: the San Antonio thesis could not be estimated from this data.** Style features appear on the opponent cards as **descriptive only**.

The cleanest evidence of no signal is the training line: five interactions fitted on 2,455 games barely improved **the sample they were fitted on**. There was nothing to overfit, so there was nothing to transfer.

**The number, and the condition:** a held-out MAE gain of -0.0395 over 43 series, and the honest caveat that a real effect in one seven-game series and a stable transferable style interaction are different things this test cannot separate.

---

## 7. Versatility

**Not estimated this run.** The versatility index depends on the M2 series model, and M2 came out off. Ranking all 30 by the spread of series win probability across the contender field would inherit exactly the structure the held-out test rejected.

**What can be said instead:** the seed distribution below is the real matchup exposure, and it is wide.

**The number, and the condition:** deferred to `gaps_remaining.md`, conditional on a series model that survives a held-out test.

---

## 8. Fragility

**Not estimated this run.** Removing each team's top three players for the playoffs and re-simulating is specified in N5 and was not reached.

**What is already known and belongs here:** Minnesota is currently playing without the man who led its 2025-26 RAPM sample, and section 2 prices that at **+1.714pp of title probability, ALL POSITIVE across four views** `[modeled]`. The fragility question has already been answered once this year, involuntarily.

**The number, and the condition:** +1.714pp for one player's availability, conditional on the R7 reading that he misses the regular season entirely.

---

## 9. Mouths to feed

**The optimistic case.** Ball, Edwards, Kuminga and Dosunmu is a lot of shot creation for a team that lacked a secondary creator, which this project's own earlier work named as the missing piece.

**The pessimistic case.** Four players who need the ball, one of whom is on a two-year deal with an opt-out and a stated plan to reach free agency, and a centre whose roll volume already fell 41%.

**Not estimated this run.** The usage accounting in M5 (projected-unit usage sums against the league starting-five distribution, three-season base rates for high-usage pairings, assisted and unassisted shares) was not reached.

**The number, and the condition:** deferred, conditional on the play-by-play pull in M5.

---

## 10. What to watch

Five falsifiable claims, each with a metric, a current value and the threshold that flips it. **This list is provisional because N8 was not completed; these are the four that fall out of work that was.**

1. **Cody Williams' minutes.** Current projection 16.1 `[assumed]`. **Below 8 a night and the offseason verdict flips from ALL NEGATIVE to MIXED** `[modeled]`. This is the single highest-leverage number in the preview.
2. **DiVincenzo's availability.** Currently 0 games `[observed, R7]`. Any real return is worth up to +1.714pp, and it removes Williams from the rotation as a side effect.
3. **Minnesota's top-six finish.** Modelled at 0.44, band 0.22 to 0.67 `[modeled]`. The modal seed is 7th at 0.269, barely ahead of 6th at 0.252.
4. **The Boston check on our own model.** If Boston is not a top-two team by January, the model's league-wide ordering is wrong in a way that also touches Minnesota's number.

**The number, and the condition:** eight minutes of Cody Williams is the threshold that moves the headline, and it depends on a rotation decision no one has made yet.

---

## 11. The bill

The signing is **official**; Kuminga wears No. 24; **the team release discloses no terms**, so every dollar here is reported rather than club-confirmed `[observed, p0_lock_official]`.

Two years, **$6,064,000 then $6,367,200**, total **$12,431,200**, player option on year two, taxpayer mid-level exception. Year one is corroborated from outside the reporting: Spotrac carried it at the taxpayer exception to the dollar. Two outlets say roughly $13.0M instead, a $568,800 difference that changes no legality question and is flagged rather than resolved.

**The chain, which closes to the dollar** `[observed, green_resolution]`: $217,621,829, minus Green's $14,679,012, plus Williams and Konchar at $12,180,600, minus $4,110,000 for stretching Konchar, minus $1 for the McDaniels penny, equals **$211,013,416**. Add Kuminga and it is **$217,077,416**, which is **$4,608,584 under the hard cap** and **$8,062,416 over the first apron**.

Spotrac publishes three separately-computed figures for Minnesota and **all three agree with ours at zero difference**.

**What the Green dump cost: no pick and no swap, either direction.** Cash, plus $2,055,000 a year of dead money for three seasons, $4,110,000 of it landing in 2027-28 and 2028-29. Against that they hold Cody Williams, the tenth pick in 2024, with a 2027-28 club option.

**And the part that is expensive is not the part people will blame.** Re-signing Dosunmu did not cost real money: the cheapest legal version of the forced move and the no-Dosunmu counterfactual sit within $1.7M of each other. **Taking Williams and Konchar back instead of a minimum body cost $6,712,836 of payroll and roughly $14.6M more tax**, because it crosses into the 3.50 bracket. Roughly $20M all in, for one season of a 22-year-old who has not been good yet.

**The number, and the condition:** $4,608,584 of hard-cap room for the whole league year, and it is only enough for one minimum addition if nothing goes wrong.

---

## Appendix: what this preview could not estimate

Carried here rather than left implicit. Full detail in `gaps_remaining.md`.

- **The style overlay** (M2), tested and rejected on held-out data.
- **Opponent cards** (M3), **lineup study** (M4), **usage accounting** (M5).
- **Playoff translation** (N3), **versatility index** (N4), **fragility** (N5), **late-clock splits** (N7).
- **Most of the champions column list** (H1): net-rating ranks, seeds, playoff net rating, continuity, health. Basketball-Reference returned 403 directly and its proxy is rate-limited on that domain.
- **Seasons before 2023-24** in the champions table, which need a B-Ref page or a paste.
- **Minutes-weighted size** as a style feature: no height or minutes column on the warehouse bio table.
