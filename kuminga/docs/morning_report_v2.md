# Morning report: the overnight run of 2026-09-09 into 2026-09-10

**Run window:** roughly 21:00 to 04:15 UTC. **Nine commits**, `8daf5f52` through `aa89afd8`. Decision entries **D59 through D65**. Everything below is reproducible from those runs; nothing here is remembered.

---

## 1. What is unconditional now, and what depends on what

**Two verdicts are unconditional. The headline is not one of them.**

**UNCONDITIONAL: Kuminga is positive in his slot.** Against the player most likely to take his minutes he grades positive under **all four views**, and that holds under **every** stress applied this run: across the whole Cody Williams minutes range from 0 to 16 (D59), under both the pool-rank and team-rank curve indexing (D60), and under **both aging bases**, +0.488 un-aged and +0.615 aged (D65). It is the only claim in this project that got sturdier every time it was pushed.

The caveat that travels with it is about **size, not sign**. The weakest of the four views sits below its own noise floor under both bases (0.174 against 0.479 un-aged, 0.209 aged, 3 of 4 clearing either way). The publishable form is therefore fixed: **positive under every view and under both aging bases, and too small for one view of four to resolve.** Not "worth half a point."

**UNCONDITIONAL: the Beringer alternative is negative.** If Joan Beringer takes those minutes instead, all four views go negative, -1.10 un-aged and -1.96 aged, and that result clears the floor on all four. Both the positive and the negative case are real, and which one you get is a rotation decision rather than a fact about Kuminga.

**NOT UNCONDITIONAL, and this is the important one: "the offseason made Minnesota worse" does not ship.** It fails the project's own quotability rule in three separate ways.

1. **The aging gate.** ALL NEGATIVE un-aged at -1.261pp, **MIXED aged at -0.398pp**. A verdict ships only if the sign holds under both bases. This one does not.
2. **The Williams range.** ALL NEGATIVE while he plays 12 minutes or more, **MIXED at 8 and below**. DARKO is the view that flips. Checked on both the f-curve and the season-sim basis, with the same breakpoint, so it is not an artifact of the estimator.
3. **The decomposition.** Take the DiVincenzo injury and the Williams minutes out and the remainder, which is the part the front office actually chose, is **+0.762pp MIXED**. Three of four views think the moves helped.

**And the injury and the Williams assumption are the same wound, not two.** Healing DiVincenzo removes Williams from the rotation by itself: with DiVincenzo out Williams is the tenth man at 16.1 minutes, with him healthy Williams is eleventh at zero. The interaction is **exactly minus the Williams figure**. Anyone adding the two repairs overstates the combined fix by a full percentage point.

**The whole thing turns on 0.0101.** Williams' rank score is 0.3029 against Jaylen Clark's 0.3131. That gap decides sixteen minutes a night or none, and about a point of title probability. Write his minutes as a coin-flip rotation call, never as a projection.

**Two more that do not ship:** the DiVincenzo injury verdict and the depth bundle both go ALL NEGATIVE un-aged to MIXED aged.

---

## 2. The style model, and the West matchups

**The style model found nothing, and that is the finding.**

Five interactions fixed in advance, fitted on 2023-25, held out on 2025-26 and separately on three postseasons:

| sample | n | base MAE | with style | gain |
|---|---:|---:|---:|---:|
| train, 2023-25 | 2,455 | 10.626 | 10.629 | -0.0034 |
| **held out, 2025-26** | 1,225 | 11.086 | 11.095 | **-0.0085** |
| **held out, postseasons** | 251 | 12.478 | 12.517 | **-0.0395** |

Negative on both held-out samples, and **worst on the postseasons**, which is exactly where the San Antonio thesis lives. **The overlay stays off. The piece says the San Antonio thesis could not be estimated from this data.**

The cleanest evidence is the training line: five interactions fitted on 2,455 games barely improved **the sample they were fitted on**. There was nothing to overfit, so there was nothing to transfer. The postseason sample is **251 games, roughly 43 series**, and that number travels with any playoff claim built on it.

**West matchups, therefore on the net-rating basis, series win probability for Minnesota:**

| worst | | best among plausible playoff teams | |
|---|---:|---|---:|
| Oklahoma City | **0.101** | Golden State | 0.735 |
| San Antonio | **0.133** | LA Clippers | 0.699 |
| Houston | 0.255 | Phoenix | 0.516 |
| Denver | 0.288 | Portland | 0.540 |
| LA Lakers | 0.347 | | |

Minnesota's title equity is almost entirely in the **27.8% of seasons where it escapes the first round**. Conditional on reaching round two, the path to a title is about **6%**. The modal seed is **7th at 0.269**, barely ahead of 6th at 0.252.

---

## 3. The champions base rates, and where Minnesota sits

**n = 3. Every figure is a count out of three, not a rate.**

| season | champion | preseason | implied | rank |
|---|---|---|---:|---:|
| 2023-24 | Boston | +450 | 14.69% | 1 |
| 2024-25 | Oklahoma City | +675 | 10.80% | 2 |
| 2025-26 | New York | +900 | 8.27% | 4 |

The favourite won **1 of 3**. The champion came from the top five **3 of 3** and the top four **3 of 3**. Champions were priced between **8.27% and 14.69%**, median 10.80%.

**Minnesota is at 3.16% and rank 6 on the market, 1.68% and rank 14 on the model. No champion in this sample started below 8.27% or worse than rank 4.** Minnesota is outside the band by a factor of two and a half on the market and five on the model.

**The closest analog is the team that just did it.** The 2025-26 Knicks were the cheapest champion here, started fourth, **finished under their own win total at 53-29, and won four rounds anyway.**

**And the market study exposed a problem in our own model that belongs on the honesty rail.** Twenty of thirty teams differ from the model by more than its materiality floor, and the pattern indicts us: the model makes **Boston the title favourite at 16.99% against a market rank of fifth**, and **Charlotte a top-five team against a market rank of nineteenth**. Neither is defensible. When a model disagrees with the market about Minnesota by 1.5 points and about Boston by 11.5, the Minnesota disagreement has to be read in that light. **Minnesota's market number also sits outside our four-view band**, so this is not two estimates overlapping within uncertainty.

---

## 4. The three most important judgment calls

**One. I adopted W1b as primary against the letter of your decision rule, and said so.** The rule said team-rank indexing becomes primary only if the offseason verdict changes. It cannot: `build_rotations` already used team-rank, so the defect only ever touched the attribution layer, verified by flipping the mode and getting 600 identical rotation rows to nine decimals. I adopted it anyway, because indexing a curve by a rank it was not fitted on is a misuse rather than a modelling choice with a defensible alternative, and adopting it costs nothing in headline consistency precisely because it cannot move the headlines. Pool-rank is kept as the recorded sensitivity. **Alternative rejected: leave a known-incorrect indexing as the published basis for the attribution table section 4 quotes.**

**Two. I did not run the 200k sim.** It is a four-to-five hour job. Running it would have consumed the night and blocked W1b, W1c, the aging gate, the market work, the champions study and M1, every one of which changed a verdict, in exchange for a precision improvement to a floor that binds no verdict currently shipping. **Alternative rejected: run the 200k first and defer the aging gate.** The aging gate is a rule about what may be printed; the 200k is a decimal place. The rule outranks the decimal. The magnitude caveat in section 4 of the skeleton is therefore written against the current floor and may relax later.

**Three. I rejected an entire source before using any of it.** sportsbettingdime.com's past-seasons table was the fastest route to ten seasons of champion history. It names **San Antonio** as the 2026 champion. New York won 4-1. A source that misstates a champion cannot be trusted for its odds columns either, so none of it was taken and the champions table is three seasons built on your own files instead. **It would have poisoned the base rates silently.**

---

## Technical detail

**W1b.** Curve indexing moved from within-pool to within-team rank in the attribution allocator, with positional minimums (60% of each team's own observed pool share) replacing hard pool budgets. **One sign flip**, `randle_out` MIXED to ALL POSITIVE. Magnitudes on the big player moves roughly doubled (Reid out -0.246 to -0.520), which is the evidence the old indexing was compressing every attribution toward zero. One verdict lost the floor: `ddv_injury` from 4 of 4 to 3 of 4.

A design error caught mid-item: my first implementation copied `allocate()`'s ten-man truncation into the attribution allocator, which crashed `green_kept` because Josh Green sits tenth on one rank score and eleventh on another, so a hard cut moved his coalition value between 13 minutes and zero on a 0.016 percentile difference. Attribution must not be that brittle. Truncation removed, curve extrapolated past rank 10. Three sign flips became one.

**W1c.** Injury +1.714pp, Williams +1.006pp, interaction -1.006pp, remainder +0.762pp MIXED. Full re-allocation at each state rather than holding other players fixed; the simpler alternative would have made the components additive by construction and hidden the interaction that is the finding.

**W2.** Nine verdicts ship under both aging bases, five do not. Aging helps Minnesota because Minnesota is young: title 1.68% un-aged against 2.54% aged, P(top 6) 0.438 against 0.643.

**P0.** Eleven rows promoted to official. The team release discloses no terms, so every promoted row carries `terms_status = terms_not_released_by_team` on the row itself.

**Market.** Overround 21.8%. Proportional de-vig quoted; power method (k = 1.0871) reported beside it, moving Minnesota 0.26pp. The 76ers book_4 at +2500 against a 750-900 range is flagged; the median is robust to it (875 in, 850 out).

**Three bugs found and fixed.** The aged chain's restore list did not cover every file it writes, so the first gate run compared an aged file against itself and reported five slot variants as identical under both bases; caught because identical values to three decimals across two bases is a symptom, not a result. And the method-versus-column trap fired **twice more** (`x.sample`, then `x.item`), the second time hours after I wrote a comment warning about the first. Every site now indexes by name.

---

## What did not finish, and why

Full detail in `gaps_remaining.md` item 14.

**Blocked on an external source.** Most of the H1 champion feature columns (net-rating ranks, seeds, playoff net rating, continuity, health) and every season before 2023-24. **Basketball-Reference returns 403 directly, and its proxy is rate-limited on that whole domain until 04:14 UTC** with a DDoS-suspicion message. The warehouse cannot substitute: its team advanced table is game level with no season key. Retry the B-Ref pages after the block lifts, or paste them.

**Blocked on missing warehouse columns.** Minutes-weighted size as a style feature: `nba_player_season_bio` has neither a height nor a minutes column. Dropped rather than proxied, and two of the five planned interactions were redefined without it. **This could plausibly change the M1 answer and the held-out test does not rule it out.** Also N2's opponent-distribution-by-seed, because `run_sim` does not persist the simulator's matchup block; one line plus a re-run fixes it.

**Not reached:** M3 opponent cards, M4 lineup study, M5 usage accounting, N3 playoff translation, N4 versatility, N5 fragility, N7 late-clock splits, H3 separation, H4 case files, H5 Minnesota scored on the champion sheet, and the full N8 watch list. Four of the five watch-list claims are drafted in the skeleton from work that did complete. **The highest-value next item is H4's Knicks case file**, because the 2025-26 Knicks are the cheapest champion in the sample and the only real template for the argument Minnesota needs.

**Standing risk, unchanged:** the roster book is single-sourced to Spotrac, so the dollar gates are parse-fidelity tests rather than independent-truth tests.

**The deliverable:** `kuminga/docs/piece_v2_skeleton.md`, eleven sections, every number labelled observed / composed / modeled / assumed with a run ID, sections 4 through 9 opening with the strongest optimistic and pessimistic case, and no section ending in a verdict.
