# Decision log: Kuminga project

Every judgment call made during the autonomous run. Format: the call, the alternative, why.
Rulings R1-R9 came from Bobby and are recorded at the top for reference, not re-litigated.

## Standing rulings (from Bobby, 2026-08-26)

| Ref | Ruling |
|---|---|
| R1 | No single title-odds point estimate. Ship surplus argument, Shapley sign agreement, all-30 ordinal ranking, CRN-paired band, cap mechanics. Compute points internally. |
| R2 | All-30 scope is mechanical: rebuild rosters from contracts + transactions, one documented minutes heuristic applied identically. Retire opponent_rosters.json assumed_moves. |
| R3 | Carry both Green branches. Both have Green off the 2026-27 roster, so strength/attribution runs once; only cap outputs fork. |
| R4 | Kuminga hand-entered: Y1 $6,064,000 TPMLE, Y2 $6,367,200 (5% raise) player option, total $12,431,200. Tag "reported, pending official". Add placeholder 14th-man minimum. |
| R5 | Counterfactual fives on rollup-plus-net-rating, labeled talent rollups. No fitengine synergy build. |
| R6 | Baseline = 2025-26 end-of-season roster for all 30 (as of 2026-06-13, no injuries), through the new pipeline. |
| R7 | DiVincenzo out for 2026-27 RS in primary; sensitivity playoff return at 80%. League-wide long-term-out = sourced report of 20+ games. |
| R8 | Source precedence: official NBA/team release > Spotrac/B-Ref/RealGM > reporters. Log every conflict with both values and URLs. |
| R9 | Fold in the external fact-verification pass; conflicts logged here, resolved by R8. |

---

## Decisions

### D1. Cap thresholds upgraded from projection to final (item 1)

**Call.** Replaced the 2026-27 row in `offseason/data/league_year_constants.json` with the league's actual figures and set `is_projection: false`. Cap $164,961,000, tax $200,428,000, first apron $209,015,000, second apron $221,686,000, minimum team salary $148,465,000, non-taxpayer MLE $15,044,000, taxpayer MLE $6,064,000, room $9,366,000, BAE $5,477,000.

**Alternative.** Adopt the `alebron/data/cap_state.json` "verified" set without an external check, as the fallback in item 1 permitted.

**Why.** A primary source was reachable, so the fallback was not needed. NBA.com confirms the cap/tax/apron/min-team figures; Hoops Rumors confirms the exception values and their term limits. The `alebron` set turned out to be correct on all five figures it carried, so this also retro-validates that file. Regenerated via `build_league_constants.py` rather than hand-edited, so the out-years rescale consistently off the new anchor.

**Why it matters.** The second apron moved $314,000 from the projection ($222,000,000 to $221,686,000). That is the difference between a full-TPMLE signing being legal and illegal for Minnesota while Josh Green is on the books. The engine had been reading the projection.

**Also added** (same file, same run): `exception_terms` (max years and max raise per exception) and `bird_rights` (service-time grades and starting-salary rules). Both previously existed only as prose in `offseason/docs/nba-roster-rules-reference.md`. The `exception_terms` block settles a consistency check on its own: the taxpayer MLE is capped at **two years**, which is exactly the reported length of the Kuminga deal. A three-year deal would have been impossible on this exception.

**Side effect, accepted.** This file is shared with `core_max`, `offseason` and `all-for-one`. Their feasibility gates will now answer on final rather than projected numbers. That is a strict improvement, but it means any previously published figure that depended on the June projection is no longer exactly reproducible from the current constants file. The pre-edit file is preserved at `kuminga/data/league_year_constants.PRE_ITEM1.json`.

### D2. Kuminga terms hand-entered as a supplement child table, not a forked ledger (item 2)

**Call.** Recorded the signing in `kuminga/data/transaction_supplement.csv`, a child table keyed on the league feed's own `group_sort`, with synthetic `SUPP_` keys for events newer than the feed cutoff. Status `reported_pending_official`.

**Alternative.** Build a standalone `transaction_ledger` table as Phase 0 originally proposed.

**Why.** `nba_transactions` is live, league-wide and correctly models multi-team deals through `group_sort`. A parallel ledger would drift from it within a day. What it actually lacks is dollars, enumerated picks and the exception used, which is exactly what the child table adds.

**Finding worth keeping.** The signing was reported 2026-08-26 by Anthony Slater (ESPN), terms via agent Aaron Turner to Shams Charania. The league feed ends 2026-08-23. So Phase 0's "the signing exists in no data source" was not a pipeline failure. The signing was hours old.

**Internal consistency check that passed.** The reported "$12.4M over two years" reconstructs to $12,431,200 from the verified taxpayer MLE ($6,064,000 plus a 5% raise), within $31,200 of the reported figure. Separately, the taxpayer MLE is capped at two years, which is the reported length. A three-year deal on that exception would have been impossible.

### D3. The Hawks' declined option leaves a stale row that must be dropped (item 2)

**Call.** Dropped Kuminga's $24,300,000 Atlanta team-option row from both the roster snapshot and the verified contracts file.

**Why.** Atlanta declined it 2026-06-29 (ESPN, theScore), but `nba_player_contracts`, scraped 2026-08-26, still carries it as live. Left in, Atlanta's apron position is overstated by $24.3M and Kuminga is on two teams at once.

**Logged as an R8 conflict.** Contract source (Spotrac/B-Ref tier) says active; reporter tier says declined. Precedence would normally favour the contract source, but here the contract source is simply stale rather than contradictory, and two independent reporters agree. Resolved in favour of the decline.

### D4. Dead-money duplicates resolved by remaining-guarantee, then deferred to the engine's own handler (item 3)

**Call.** Four players (Beal, Lillard, Caldwell-Pope, Prosper) appear on two teams at the same salary. Identified the active team as the one with the most recent Signing/Trade in the feed, and the other as carrying dead money. Where `verified_contracts.py` already implements this, its numbers win, so there is one source of truth.

**Alternative.** Keep my own stretch math in the roster snapshot.

**Why.** `verified_contracts.py` feeds `build_team_state.py`, which feeds the feasibility gate. Two different answers for the same player would put the roster table and the cap table on different rosters.

**Residual, flagged.** The two methods still disagree for these four on the ACTIVE player's 2026-27 cap hit: the engine assumes a veteran minimum ($3.9M), my snapshot derived remaining-guarantee divided by seasons. Four teams (LAC, MEM, PHI, POR) differ by $0.5M to $2.6M as a result. The other 26 reconcile to the dollar. External figures were requested; if they do not arrive, the engine's number stands and this note is the disclosure.

### D5. The 2026 rookie class had to be restored by hand, and a silent name-matching bug nearly hid it (items 3, 4)

**Call.** Restored 44 players, $203,221,463 of 2026-27 salary, into the verified contracts file with synthetic ids (`R2026_nnn`).

**Why.** `verified_contracts.py` resolves names against `nba_player_bio`, which stops at the 2025 draft class. Every 2026 rookie therefore failed to resolve and was dropped. That silently removed real salary from every team's apron basis: Chicago $15.6M, Oklahoma City $15.4M, Washington $14.7M. Apron positions computed without them would have been wrong league-wide, in the direction of making teams look cheaper than they are.

**A bug found while fixing it, worth recording because it is the kind that does not announce itself.** My first de-duplication pass used a name key that "repaired" latin-1/utf-8 double encoding unconditionally with `errors="ignore"`. That is correct for a mojibaked name and destructive for a correctly-encoded one: "Jokic" with its accent encodes to nothing under latin-1 and was silently truncated, so the same player failed to match himself across two files and was inserted twice. Denver's payroll gained $59.0M and the Lakers' $49.8M before it was caught by a reconciliation check that compared per-team counts and totals between the two files. The fix is that a STRICT latin-1 encode is itself the discriminator: genuine mojibake re-encodes cleanly, a correct name raises. After the fix, 26 of 30 teams reconcile to the dollar and the restored count landed exactly on 44, the size of the draft class.

**Why this is in the decision log and not just the commit.** The failure mode is the project's stated bogey: a plausible number, produced silently, with no error raised. It was caught only because a reconciliation step existed. Every later join in this build uses the same normalizer.

### D6. Rebuilding team_state was not a refresh, it was a different league (item 4)

**Call.** Rebuilt `offseason/data/team_state.csv` on the verified thresholds and the patched contract book. Preserved the June 17 file at `kuminga/data/team_state.PRE_ITEM4.csv` and wrote a full diff to `kuminga/outputs/team_state_diff_2026_27.csv`.

**What changed.** **17 of 30 teams changed apron tier.** Median absolute change in apron salary: $25.8M. Largest moves: the Lakers +$97.7M (over-cap to taxpayer), Chicago +$64.5M (under cap to over cap), Oklahoma City -$30.9M (second apron down to first apron), Sacramento -$14.7M.

**Minnesota specifically:** +$28.8M, from `over_cap_under_tax` to `second_apron`. The June file had the Wolves comfortably below the tax. They are now over the second apron.

**Why it matters beyond bookkeeping.** Any conclusion drawn from the June team_state about who could absorb salary, who had an exception, or who was hard-capped was describing a league that no longer exists. This is the concrete justification for R2.

### D7. Verified dead-money figures replace the engine's vet-minimum guess (items 3, 4)

**Call.** Externally verified all four two-team players and wrote the real figures into `kuminga/data/dup_resolution_verified.json`, which now overrides both the roster snapshot and the verified contracts file.

**What the research found.** All four are genuine two-team situations, not scrape artifacts. The contract table's error is narrower than it looked: it copies the same salary to both rows.

| Player | Active team, 2026-27 cap hit | Dead-money team, 2026-27 | Seasons |
|---|---|---|---|
| Bradley Beal | LAC $6,424,800 | PHX $19,383,010 | 5 (through 2029-30) |
| Damian Lillard | POR $13,398,800 | MIL $21,311,053 | 5 (through 2029-30) |
| Kentavious Caldwell-Pope | PHI $2,449,421 | MEM $17,744,971 | 1 only |
| Olivier-Maxence Prosper | MEM $2,497,812 | DAL $1,002,360 | 3 (through 2027-28) |

`verified_contracts.py` had been assigning all four actives a flat $3,877,000 veteran-minimum guess and recording the dead-money amount as the copied salary. Both were wrong. Lillard's real Portland cap hit is $13.4M, not $3.9M.

**One conflict recorded rather than resolved silently (R8).** SalarySwish puts Milwaukee's Lillard dead money at $21,311,053, applying an annual set-off credit of about $1,205,551 against his Portland salary; HoopsHype says $22,516,603 with no set-off. Chose SalarySwish, because the set-off is a real CBA mechanism and modelling it is the more complete treatment. The $1.2M difference does not move Milwaukee across any threshold.

**Validation.** Against SalarySwish's own team pages, six of eight spot-checked teams land within 2% and the worst is 4.5%. The residual is definitional: SalarySwish's "cap hit" line includes training-camp and Exhibit-10 deals, ours adds incomplete-roster charges to 12.

### D8. R7's binary injury rule is primary, with the fractional derivation carried alongside (item 5)

**Call.** Implemented R7 as written (long-term out means regular-season availability 0) and set the long-term threshold at exactly 20 games missed, i.e. availability at or below 62/82 = 0.756. Also carried the researcher's fractional derivation in `rs_avail_frac` / `po_avail_frac`.

**Why the threshold matters.** My first pass used a looser cut and it swept in Mouhamed Gueye, who is sourced to be reevaluated in October or November, roughly 16 games missed. R7 does not classify him as long-term out, and zeroing a player who will be available for four fifths of the season would have quietly cost Atlanta a rotation piece. Nine of the ten rows qualify; Gueye does not and is carried at 0.80.

**Why both columns exist.** R7's binary rule is deliberately conservative and it costs real accuracy for sourced mid-season returnees: Jimmy Butler is derived at 0.5 and becomes 0.0. Summed across the ten players, R7 removes **2.90 more player-seasons** of regular-season availability than the sourced reading does. Golden State absorbs the largest share. The Wolves are unaffected by the choice, because DiVincenzo is out under either reading, so no headline number in this piece turns on it. The fractional columns exist so the sensitivity is one flag away rather than a rebuild.

**Honesty note carried into the data.** No source publishes an availability fraction. The injury, the date and the return language are sourced; the fractions are a derivation. The file says so, per row.

### D9. Kuminga is "agreed", not "signed", and the model says so (R9)

**Call.** Kept the `reported_pending_official` status after external verification, rather than promoting it.

**Why.** NBA.com's own tracker distinguishes "multiple reports" from "officially announced" and places Kuminga in the former. The official league transaction log has no row. Every outlet traces to one report: agent Aaron Turner to Shams Charania, 2026-08-26. That is strong sourcing for terms, but it is not an executed contract, and the deal cannot legally be executed until the Josh Green move clears the hard cap.

**Consequence carried through:** every Kuminga row in every output keeps the tag, and the morning report leads with it.

### D10. The signing is arithmetically impossible without the Green move, and an outside source reached the same conclusion (R9)

Two things now corroborate the apron finding from Phase 0.

First, SI reported on 2026-08-03 that Minnesota "could offer Kuminga the full $6.06 million taxpayer mid-level exception" but had only "$3.9 million in cap space below that threshold." That is an outside party reaching the same conclusion from the same arithmetic: the Wolves were short, and Green is the precondition.

Second, the CBA verification sharpened why. A team **above** the second apron cannot use any portion of the mid-level exception, taxpayer included, and can add outside free agents only at the minimum. Minnesota was already hard-capped at the second apron by salary aggregation in the LaMelo trade. So this is not a team choosing between tools. Signing Kuminga at $6,064,000 requires being under $221,686,000 at the moment of signing, and the current book is $223,293,829.

**The deadline is also more specific than "compliance".** August 29 is the last day to waive a player and apply the stretch provision to 2026-27 salary; a player must clear waivers by August 31. Verified against the Hoops Rumors 2026 offseason calendar. One outlet (Heavy) rendered it as "Saturday, August 30", which is internally inconsistent because August 30, 2026 is a Sunday. August 29 is correct.

### D11. Bird rights after an opt-out: Non-Bird, confirmed from CBA text (item 13, answered early)

The CBA counts seasons **covered by a player contract** with the team, not contract years signed. An exercised option year counts; a declined one does not, because the contract terminates and that season is never covered. A player who signs two years and opts out after one has one season of service and is a Non-Qualifying Veteran Free Agent.

So if Kuminga opts out in the summer of 2027, Minnesota holds **Non-Bird rights only**, which permit a starting salary of the greater of 120% of his prior salary or 120% of the minimum. On the year-2 figure of $6,367,200 that caps a re-sign start at **$7,640,640**.

Encoded in `league_year_constants.json` under `bird_rights` so it is machine-readable rather than prose.

---

## Phase 2 decisions

### D12. The minutes heuristic, and the two parameters in it (item 8)

**Call.** One rule for all 30 teams. Rank each player by `0.5 * pct_rank(prior minutes) + 0.5 * pct_rank(consensus net)`, take the top 10 available, and give them minutes that are a 50/50 blend of an empirical team-rank curve (fitted on 2025-26) and the player's own prior load, rescaled to 240.

**Two judgment calls inside it, both stated rather than fitted.**

*The rank weight.* Ranking by minutes alone freezes everyone in last season's role and would refuse to promote a player who changed teams into a bigger one, which is precisely Kuminga's situation. Ranking by impact alone hands a high-RAPM, low-minute specialist a starter's load. Half and half.

*The minutes blend.* The rank curve alone gave Rudy Gobert, a 34-year-old centre who played 29 minutes a game, the team's largest load, because his consensus impact (+5.28) is the highest on the roster. That is a real output of the value spine and not obviously wrong as *valuation*, but it is wrong as *minutes*. Blending the curve with each player's own prior load keeps role change possible while bounding it by what the player has actually carried.

**A genuine bug found here, not a preference.** The first version computed prior minutes as total minutes divided by 82, which is minutes per TEAM GAME. That conflates role with availability: Edwards, who played 61 games at about 35 minutes, came out as a 26-minute player and ranked behind Gobert. Since availability is applied separately and explicitly through `rs_avail`, folding it into the role signal as well double-counts it. Fixed to minutes per appearance.

**What is NOT modelled.** Position. The heuristic will happily field five centres. It is a talent-allocation rule, not a lineup constructor, and every downstream counterfactual inherits that limit.

### D13. The delta is the product, not the level (item 8)

Each team's 2026-27 net is `regress_to_expectation(measured 2025-26 net) + beta * (rollup_current - rollup_baseline)`. Both rollups run through the same heuristic, so its level bias cancels and only the roster change survives. This is the shape the engine already used for its three MOVED teams, applied uniformly to all 30.

The baseline (R6) is the 2025-26 end-of-season roster with no injuries, which by construction makes `rollup_current == rollup_baseline` and the baseline net equal to the regressed measured net. Minnesota's measured 2025-26 net of **+2.88** matches the engine's own June figure exactly, which is a useful check that the new pipeline is anchored where the old one was.

### D14. The all-30 rebuild changed the league, not just Minnesota (item 8)

Replacing the 25 stand-pat assumptions moved a lot. Boston rises from 3rd to 1st in projected wins (+4.13) with all four forks agreeing the offseason helped. Miami (+5.19) and Philadelphia (+5.05) are the biggest gainers; Utah (-7.37), Indiana (-5.00) and Toronto (-4.37) the biggest losers. Oklahoma City slips from 1st to 2nd, all four forks agreeing.

**And a finding about the method itself:** only 11 of 30 teams have all four impact views agreeing on the SIGN of their offseason (4 positive, 7 negative). Nineteen are mixed. That is the honest resolution of this machinery, and it is the reason R1's sign-agreement rule is the right publication test rather than a hedge.

### D15. The linear par-dollar curve is unusable out of sample, and it nearly produced a fake headline (items 9, 14)

**What happened.** `build_value_layer` fits `salary = a + b*net` over players earning $8,000,000 or more, which is the right sample for pricing veterans on market-set deals. The fitted intercept is about $19.6M. Applied to Kuminga at the taxpayer MLE it produced a "dollar gap" of **+$17.7M**, and it did so under all four views, which looked like a very clean headline: *every way of measuring him says he is a huge bargain*.

It is an artefact. The curve prices a league-average player at $19.6M because it has never seen a player earning less than $8M. The same curve put Kuminga's 2027 market at $25.5M and therefore said he opts out with probability 1.00 under every fork, which is what made me look at it.

**The fix.** An empirical percentile map (`kuminga/lib/market.py`): a player's impact percentile is read across to the same percentile of the salary distribution among rotation players on non-minimum deals. Monotone, bounded by observed salaries, no functional form. Calibration: net 0.0 maps to about $5.4M, Kuminga's +1.33 to $11.5M, Edwards's +1.88 to $16.0M, Gobert's +5.28 to $57.1M. Those are recognisable prices; the linear curve's were not.

**What it does to the finding, which is the point.** The honest read is no longer unanimous. At the taxpayer MLE, Kuminga's market value comes out at $11.5M (consensus) and $11.7M (RAPM), roughly double what Minnesota is paying; $6.0M on the box view, which is exactly what they are paying; and $2.7M on DARKO, which says they are overpaying slightly even at the minimum-ish price. Two of four views say bargain, one says fair, one says mild overpay.

The project's own value layer had already anticipated this and says the primary surplus should be in NET units because those are bounded. It was right. The impact-unit surplus is now primary and the dollar figure is reported alongside it.

### D16. An eighth move was added to the Shapley set so the decomposition is complete (item 11)

The brief named seven moves. Those seven do not span the difference between the 2025-26 roster and the current one: Conley, Anderson, Ingles, Phillips, Zikarsky, Pullin and Freeman also left and are in none of them. Left as-is, the marginal contributions would sum to something other than the total offseason effect and the gap would sit unexplained.

Added `other_departures` as an eighth move. 2^8 = 256 coalitions, all enumerated exactly, so contributions sum to `v(all) - v(none)` with no residual. Josh Green is deliberately in no coalition: per R3 he is off the roster in both branches, so he is a precondition rather than a lever.

**Exact, not sampled.** Because every coalition is priced by interpolating the f-curve rather than simulated, all 256 are affordable and there is no permutation sampling error to report. The order-dependence table is computed anyway, over 2,000 random orderings, because a move whose marginal contribution swings widely with order is one whose headline should be a range.

### D17. DARKO is carried as a fourth view, but it is integer-rounded (items 9, 10)

The DARKO leaderboard on disk has **13 distinct DPM values across 582 players**: Jokic 7, Kawhi 6, Wembanyama 6, Giannis 5. It is rounded to whole points. Kuminga's "-1.0" could be anything from -1.5 to -0.5.

Kept as a fork, because an external check that disagrees is worth more than one that agrees, and it is the only non-in-house view available (Dunks & Threes EPM and BBall Index LEBRON are both gated). But it is not a peer of the other three and is labelled that way everywhere it appears. The project's own provenance note already calls it "not a calibrated pipeline input; an external sanity check." That is the right reading, and DARKO's coarseness is part of why Minnesota's fork spread is as wide as it is.

### D18. The overlay is off, because it only exists for 12 teams (item 10)

`simulate_league` can apply a matchup-dimension overlay in series resolution, using `opponent_profiles.json`. That file covers 12 teams. Running an overlay for 12 of 30 would make the pipeline non-identical across teams, which is the one thing R2 forbids. The overlay is off and every series resolves on net rating alone, uniformly. The cost is real: the overlay is where archetype matchup effects lived, and the postmortem's Q4 work says those matter for this roster specifically. Recorded as a limitation rather than quietly dropped.

### D19. Two silent-failure bugs in the lineup evidence, both caught by guards rather than by inspection (item 15)

`lineup_id` is COMMA-delimited. The first version split on a hyphen, which returns False for every player and produces a complete, clean-looking table in which nobody was ever on the floor: Randle+Gobert showed 0 possessions, and Kuminga's "OFF" split silently contained all 8,054 Golden State possessions. Nothing raised.

Separately, `type_grouping` in the Synergy table is capitalised `Offensive`; querying for `offensive` returned an empty frame and the transition-share lines simply did not print.

Both are now asserted: every lineup must parse to exactly five ids, every player named in the analysis must appear in at least one stint, and the Transition query must return rows. These are the project's stated bogey (a plausible number produced silently) and the only reason they were caught is that a table of exact zeroes is visibly wrong. A table of slightly-wrong numbers would not have been.

---

## Phase 3.5 decisions

### D20. The cap double-count, and the canonical apron basis (cap reconciliation, items 1 to 3)

**The disagreement.** Phase 0 reported Minnesota's 2026-27 book at $215,871,829 across 13 players. The first morning report said $223,293,829. The gap is exactly $7,422,000 and it decomposes with no remainder:

| | |
|---|---|
| 13 contracted players, `nba_player_contracts` scraped 2026-08-26 | $215,871,829 |
| Jonathan Kuminga at the taxpayer MLE | + $6,064,000 |
| the R4 "14th man" modelling placeholder | + $1,358,000 |
| = the figure the morning report quoted | **$223,293,829** |

**The ruling on what counts.** Apron team salary is contracted salary, plus dead money, plus likely incentives, plus an incomplete-roster charge **only when a team is below TWELVE players** (the rookie minimum per empty slot, offseason only). It does **not** include free-agent cap holds, which sit in the cap basis (Minnesota carries $16,484,548 of those, which is why its cap-basis total of $239,778,377 is larger again and must never be quoted as an apron figure), and it does not include two-way contracts or players a team has not signed.

Minnesota is at 13 contracts, so the incomplete-roster charge is **zero**, and `team_state` independently agrees. **The R4 placeholder is therefore not a CBA charge at all.** It is a projection of a signing that has not happened, and it does not belong in an apron figure.

**CANONICAL: apron team salary = contracted salary only.**

- Pre-Kuminga: **$215,871,829** (13 contracts)
- With Kuminga: **$221,935,829** (14 contracts)

**A second, worse error found while fixing the first.** `eval_signing.py` took `team_state.apron_team_salary`, which already contains Kuminga because `patch_contracts.py` had put him in the contract book, and then added the taxpayer MLE on top of it. The signing was counted twice.

| Figure | Before (reported) | After (correct) |
|---|---|---|
| Apron salary with Green, after signing | $229,357,829 | **$221,935,829** |
| Amount over the second apron | $7,671,829 | **$249,829** |
| Apron salary with Green removed, after signing | $214,678,817 | **$207,256,817** |
| Room under the second apron | $7,007,183 | **$14,429,183** |

The headline changes character entirely. It is not that Minnesota misses by $7.7M. **It is that they miss by $249,829**, which is a quarter of one percent of the apron and less than a rookie minimum contract.

**A third error, same function.** The branch state passed to `evaluate_move` kept the base row's `tier` of `second_apron` even after Green's salary was removed, so the gate refused **both** branches with "taxpayer_mle not available at tier second_apron", including the legal one. The tier is now recomputed from the branch's own salary. On the canonical basis Minnesota's pre-signing tier with Green on the books is **first apron**, not second, which means the taxpayer MLE **is** available to them. The binding constraint was never eligibility. It was the hard cap the exception creates.

### D21. The Green branches restated, with roster fill made explicit

Thresholds: first apron $209,015,000, second apron $221,686,000, rookie minimum $1,358,000. A team must carry 14 or 15 players in the regular season (a grace period allows 12 or 13 for at most two consecutive weeks and 28 total days), so roster size is a real constraint and is shown rather than assumed.

| Branch | Players | Apron salary | vs first apron | vs second apron |
|---|---|---|---|---|
| Trade Green | 13 | $207,256,817 | +$1,758,183 | +$14,429,183 |
| Trade Green | **14** | **$208,614,817** | **+$400,183** | +$13,071,183 |
| Trade Green | 15 | $209,972,817 | **-$957,817** | +$11,713,183 |
| Stretch Green | 13 | $212,149,821 | -$3,134,821 | +$9,536,179 |
| Stretch Green | 14 | $213,507,821 | -$4,492,821 | +$8,178,179 |
| Stretch Green | 15 | $214,865,821 | -$5,850,821 | +$6,820,179 |

**Two findings that only appear once roster fill is explicit.**

First: the trade branch clears the first apron at a legal 14-man roster, but by **$400,183**, and a fifteenth man on a rookie minimum puts them **$957,817 over it**. Staying under the first apron requires carrying exactly fourteen, which is the league minimum and leaves no injury slack.

Second: **any player coming back in a Green trade crosses the first apron.** The room at 14 is $400,183 and the smallest contract that can legally come back is the rookie minimum of $1,358,000. So the "pure salary dump" framing in R3 is not one option among several; it is the only version of the trade that preserves first-apron status.

The stretch branch is over the first apron in every configuration.

### D22. The two-sentence version for the piece (item 3)

> Minnesota could use the taxpayer mid-level exception, worth $6,064,000, but using it hard-caps them at the second apron of $221,686,000 for the rest of the league year, and the test is where the team sits **after** the signing, not before. With Josh Green's $14,679,012 on the books they land at $221,935,829, which is $249,829 over that line, so the exception was legal to use and impossible to fit until Green went.

Sourcing: the exception values and the hard-cap trigger are from Hoops Rumors' 2026-27 exception values and its hard-cap explainer; the incomplete-roster-charge threshold is from the CBA FAQ; the 14-or-15-man regular-season roster requirement and its grace period are from the CBA Guide's roster page. All URLs are in `league_year_constants.json` and `cap_reconciliation.md`.

### D23. The model's market value agrees with the real market, and that adjudicates between the forks (A1)

Kuminga turned down a reported **$12 million-plus annually over three years** from the Lakers via sign-and-trade, roughly $36M total (Anthony Slater, ESPN). Chicago made an offer with no terms reported; Portland pursued him with no terms reported. All three are now in the transaction supplement as `RejectedOffer` rows, with the two undisclosed ones carrying zero dollars so they can never be summed into a total.

Against the best observed bid of $12.0M per year:

| View | Model market value | vs the Lakers bid |
|---|---|---|
| consensus | $11.5M | **agrees, within 4%** |
| RAPM | $11.7M | **agrees, within 3%** |
| box | $6.0M | half the bid |
| DARKO | $2.7M | a quarter of the bid |

This is the first evidence in the project that discriminates between the four views using something outside the model. **The two possession-based views land within four percent of what a real team actually offered. The box and DARKO views are contradicted by the observed market by a factor of two and four.**

That does not make consensus and RAPM right about his on-court impact, and it should not be oversold: a bid is a price, prices embed role and upside and desperation, and one bid is one observation. But it is a real out-of-sample check and it points the same way twice.

**And it sharpens the surplus claim.** Minnesota is paying $6,064,000 for a player whose highest actual bid was about $12,000,000 a year. That is a price argument that no longer rests on the model alone.

### D24. Age-restricted market value, and why it moves so much (A2)

Restricting the reference set to players aged 22 to 25 on non-rookie-scale deals moves Kuminga's estimated market value **down**, sharply:

| View | All ages | Age 22-25 | Direction of the shift |
|---|---|---|---|
| consensus | $11.5M | $2.9M | -$8.5M |
| RAPM | $11.7M | $3.6M | -$8.1M |
| box | $6.0M | $2.6M | -$3.4M |
| DARKO | $2.7M | $2.3M | -$0.4M |

**Why, and what it does and does not mean.** The restricted cohort has a median 2026-27 salary of $2.6M against $9.0M league-wide. Kuminga sits at the 58th percentile of impact all-ages and the 55th within his age band, so his percentile barely moves; almost the entire shift is the cohort's salary distribution, not his standing in it. Young players earn less because of the rookie-scale and second-contract structure, not because they are worse.

So the two numbers answer different questions. **All ages: what does this much impact get paid? Age-restricted: what do players his age get paid?** The first is the better estimate of what he is worth; the second is closer to what a team can usually get him for.

**Two reasons not to lean on the restricted figure.** The cohort is thin, 38 players after the non-minimum filter, and its salary distribution is bimodal, mixing modest second contracts with max rookie extensions up to $36.3M. A percentile map onto a bimodal distribution of that size is fragile.

**The decisive observation is that the real bid, $12.0M, sits above both.** The market did not price Kuminga like a typical 24-year-old. It priced him like his impact, which is what the all-ages consensus and RAPM figures say.

### D25. The three numbers that all looked like "Minnesota before the offseason" (C1)

**What collided.** The plain-language section called 2.95% the "did nothing" baseline while the scenario table showed "did nothing at all" at 3.15%. Both were real; neither was wrong; they describe different rosters, and one was a fork-level figure sitting next to across-fork means.

| Figure | What it actually is |
|---|---|
| 2.95% | the R6 baseline, **consensus fork only** |
| 2.94% | the same thing, averaged across the four forks |
| 3.15% | the **Shapley empty coalition**, averaged across forks |
| 2.95% | the Shapley "actual minus Kuminga" coalition, averaged across forks |

The last one is a numerical coincidence with the first, which is what made the report read as though two different objects were the same one.

**The rosters genuinely differ.** The R6 baseline runs the exact 2025-26 end-of-season roster back, all 18 players, and ignores that Dosunmu, Hyland and Clark were free agents. The Shapley zero does literally nothing: it lets those three walk and signs nobody, leaving 15 players plus a roster charge.

**Ruling.** The R6 baseline is **canonical** for any before/after claim, because it is what the brief specified and what T1 and T2 use. The Shapley zero is the natural origin for attribution and must be labelled "let the free agents walk", never "did nothing". The gap between them is not noise: it runs from -0.36pp (box) to +0.68pp (DARKO) depending on fork.

**Second collision.** The actual-roster band appeared as 1.67-3.83 and as 1.71-3.77. The rosters are identical (verified); the first is the direct simulation and the second is the f-curve interpolation used to price 256 coalitions cheaply. **The direct simulation is canonical**, being run at 5 seeds x 20,000 rather than 3 x 10,000 and on a continuous net rather than a 0.5-wide grid. Maximum interpolation error across the four forks is **0.064pp**, which is small against the fork spread and is now measured rather than assumed.

Both are recorded permanently in `outputs/canonical_figures.md`, which is re-generated by `reconcile_figures.py` so the check survives the next re-run.

### D26. The minutes ceiling (C2), and two bugs it exposed

**The rule.** Every player carries a ceiling of `min(prior per-appearance load + 3, 36)` minutes. Overflow water-fills down the rank order to whoever still has headroom.

**Why it was needed.** Without it the rotation is rescaled to 240 on every add or remove, so removing a forward hands his minutes to the whole rotation in proportion, including to the stars. That makes any player look replaceable, because the implicit counterfactual is "his minutes go to the best players on the roster", which no coach can actually do. Minutes move along the depth chart, not up it.

**Where the rule must yield.** A game is 240 minutes; that is an accounting identity. Ten teams could not reach 240 under a "prior + 3" ceiling even across a 15-man rotation, because their rosters are rookies and low-minute bench players. Rather than let Washington play 221 minutes and silently understate every Washington player, the ceilings are scaled up by exactly the factor needed and the scaling is reported.

**Two bugs found while implementing it.**

*The water-fill dropped its remainder.* The first version capped whoever was over, redistributed `min(share, room)`, then re-tested only for players still over their cap. Once everyone was at or under, the loop exited with the undealt remainder simply discarded, and Minnesota's rotation summed to 239.3 instead of 240. Rewritten as a proper water-fill that carries the remainder across iterations.

*The rookies were being thrown away.* This one predates the ceiling and is worse. The 2026 draft class exists in no id namespace, because `nba_player_bio` stops at the 2025 class. Every consumer filtered on `notna(player_id)`, so rookie minutes were computed and then **discarded**: Washington was valued on 221 of 240 minutes because Dybantsa's 19 simply vanished. That was the 2.2% "coverage" gap I had reported as a rounding detail rather than investigated. Synthetic negative ids plus a slot-prior impact in all four forks take rotation coverage from 97.8% to **100%**.

**The verdict comparison, which was the point.** At the team level the results are **robust**: 2 of 30 sign verdicts changed, and both (Chicago, New Orleans) are teams whose title odds round to zero, so the "change" is floating-point dust rather than a finding. Minnesota's own verdict is unchanged, MIXED under both rules, with the band moving from [-1.28, +0.88]pp to [-1.38, +0.86]pp.

Per Bobby's decision rule the ceiling version is primary either way, because it is the more defensible rule. The un-ceilinged run is preserved as `*_NOCEILING.csv` and reported as a sensitivity.

### D27. Why the baseline moved from 1.7% to 2.95%, and it is not the overlay (C4)

Walking the path one step at a time under common random numbers:

| Step | MIN net | Overlay | Title % | Move |
|---|---|---|---|---|
| This pipeline, R6 healthy baseline, overlay off | +2.16 | off | 2.82 | |
| Minnesota moved to June's net (DiVincenzo out) | +1.36 | off | 2.08 | -0.73pp |
| Archetype matchup overlay switched on | +1.36 | on | 1.97 | -0.11pp |
| June's reported figure | +1.36 | on | 1.70 | -0.27pp |

| Component | Share of the +1.12pp move |
|---|---|
| **injury assumption** (healthy vs DiVincenzo out) | **+0.73pp, 66%** |
| residual (all-30 field rebuild, rotations, harness) | +0.27pp, 24% |
| matchup overlay (off vs on) | +0.11pp, 10% |

**The overlay is the smallest component, not the largest.** Two thirds of the gap is definitional rather than a modelling disagreement: R6 specifies a healthy baseline and June modelled DiVincenzo out. The two runs were answering different questions about the same team.

**But the overlay caveat still stands, for a different reason.** Its measured effect of 0.11pp is computed with dimension profiles that exist for only 12 of 30 teams, so it is an effect measured on a partial overlay and is a floor, not an estimate. The qualitative limitation is unchanged: this pipeline resolves every series on net rating alone and cannot see that San Antonio is the archetype this roster handles worst, which the postmortem's Q4 work established and which is not hypothetical, since San Antonio eliminated them and reached the Finals. Minnesota's number should be read as optimistic on that dimension.

### D28. What the three-season backtest says about the title numbers (A3)

A full historical replay is impossible and the reasons are concrete: there are no historical preseason rosters in the warehouse (the roster table holds one season), and the impact spine is a pooled 2023-26 fit, so using it for 2023-24 would leak three years of future information. Both are in `gaps_remaining.md`.

What is testable without rosters is the **calibration spine**: measured net in one season to projected wins and title odds in the next, which is the "everyone stands pat" model and is exactly the layer C4 left as a residual.

| Season | Model wins MAE | Market wins MAE | Model-actual r | Market-actual r | Title MAE vs market |
|---|---|---|---|---|---|
| 2023-24 | 9.02 | 6.57 | 0.588 | 0.830 | 2.35pp |
| 2024-25 | 8.05 | 8.37 | 0.584 | 0.615 | 1.44pp |
| 2025-26 | 9.32 | 7.47 | 0.526 | 0.717 | 2.02pp |
| **pooled** | **8.80** | **7.47** | | | |

The spine is essentially **unbiased** (+0.27 wins) and its ordering correlates 0.81 to 0.83 with the market's. It is about 1.3 wins worse than the market in absolute error, which is the expected price of holding rosters fixed while the market knows about trades.

**The number that matters for how this piece is written:** the model's title-odds error against the de-vigged market is **1.4 to 2.3 percentage points**. Minnesota's entire four-fork spread this season runs from 1.57% to 3.81%, a range of 2.2pp. **The measurement error is the same size as the thing being measured.** That is the strongest available argument for R1's rule, and it is now a measured quantity rather than a methodological instinct.

### D29. The ceiling result: robust, and primary anyway (C2, completed)

**Wolves moves: 0 of 8 sign-agreement verdicts changed.**

| Move | Without ceiling | With ceiling | Mean, before to after |
|---|---|---|---|
| ball_in | ALL POSITIVE | ALL POSITIVE | +1.17 to +1.30 |
| randle_out | ALL POSITIVE | ALL POSITIVE | +0.35 to +0.19 |
| other_departures | MIXED | MIXED | +0.30 to +0.15 |
| depth | MIXED | MIXED | +0.15 to +0.10 |
| kuminga_in | MIXED | MIXED | -0.20 to -0.04 |
| dosunmu_retained | ALL NEGATIVE | ALL NEGATIVE | -0.71 to -0.52 |
| ddv_injury | ALL NEGATIVE | ALL NEGATIVE | -0.57 to -0.72 |
| reid_out | ALL NEGATIVE | ALL NEGATIVE | -0.88 to -0.98 |

**All 30 teams: 2 of 30 changed**, Chicago (MIXED to ALL POSITIVE) and New Orleans (ALL NEGATIVE to MIXED). Both have mean effects of +0.01pp and -0.00pp respectively, i.e. teams whose title odds round to zero, where the "verdict" is floating-point dust rather than a finding.

**Ruling applied:** no Wolves verdict changed, so per Bobby's rule the ceiling version is **still primary** because it is the more defensible rule, and the result is reported as **robust to the minutes model**. The un-ceilinged run is preserved as `*_NOCEILING.csv`.

**The Dosunmu diagnostic, which was the point of asking.** He stays ALL NEGATIVE under the ceiling, mean -0.71 to -0.52. Bobby's read was that a rotation guard scoring unambiguously negative on pure on-court terms is a smell, and I think that is right, but the smell is not the minutes model: tightening the minutes moved him a fifth of a percentage point and did not touch the sign. Two things it could be instead. His consensus impact is -0.21, genuinely below average, so the model is not inventing anything. And the counterfactual is "Dosunmu walks and nobody replaces him", which credits the roster with minutes that would in reality be bought at some price. The move set has no "replacement guard" to hand them to. That is a limitation of the move set, not of the ceiling, and it is the same limitation C3 fixes for the power forward slot. **If this finding is used in the piece it should carry that caveat explicitly.**

### D30. The slot constraint flips the Kuminga verdict, and it is the most important result of the phase (C3)

**Unconstrained**, removing Kuminga sends his minutes across the whole rotation, so Gobert, Edwards and Ball absorb them. His marginal contribution is MIXED, mean -0.04pp, and the signing looks replaceable.

**Constrained to the slot**, using listed positions from `nba_player_bio` (eligible at the 4 means the listing contains "Forward" and is not centre-first), his minutes can only go to Minnesota's other forwards. McDaniels absorbs 2.7 before hitting his ceiling; Beringer and Lyles are already at theirs. The man who actually fills the slot is **Terrence Shannon Jr.**, whose consensus impact is **-2.18**.

| Fork | With Kuminga | Without | Marginal | Kuminga vs Shannon |
|---|---|---|---|---|
| consensus | 1.63% | 0.57% | **+1.06pp** | +1.33 vs -2.18 |
| RAPM | 2.17% | 0.95% | **+1.23pp** | +1.37 vs -2.21 |
| box | 3.01% | 2.63% | **+0.39pp** | +0.07 vs -0.87 |
| DARKO | 3.74% | 3.60% | **+0.14pp** | -1.00 vs -2.00 |

**ALL POSITIVE, +0.140 to +1.226pp.** His surplus over the actual filler is positive under every view.

**Why this is the right counterfactual and the unconstrained one is not.** "What if Kuminga were not here" is only meaningful if the replacement is someone who could actually take the minutes. The unconstrained version answers "what if his minutes went to the best players on the roster", which is not available to a coach, because the other four positions are occupied by the people occupying them. The constrained version answers the question a general manager actually faces.

**A bug found inside this, and it is the kind that produces a confident wrong answer.** The fill order included the removed player himself. So when Kuminga was taken out, the loop found him as the next eligible body with headroom and handed his own minutes straight back: out at 26.0, back in at 23.3. The "counterfactual" was 97% Kuminga, every marginal contribution came out within 0.08pp of zero, and the table looked perfectly plausible. It was caught because the filler was reported as Jaden McDaniels gaining 2.7 minutes, which does not add up to 26. **The exact failure mode this whole exercise exists to avoid, reproduced inside the fix for it.**

**And it resolves the uncomfortable overnight finding.** Under the slot rule with the posterior-sd bar applied, **no alternative is quotable**: Minott (sd 2.10), Kenrich Williams (1.87) and Dean Wade (1.61) all exceed the 1.5 threshold, and Hayes and Horford are centre-first listings rather than 4s. The "they could have signed someone better" claim does not survive its own uncertainty. That belongs in an appendix with the sd values shown, not in the verdict.

**Scope of the claim, stated so it is not overread.** This is highly sensitive to who is identified as the filler. Shannon Jr. is a Guard-Forward with 12.5 prior minutes a game and a poor rating; if Minnesota signs another forward with the roster spot the 14-man minimum requires, the alternative improves and Kuminga's margin narrows. The finding is "against the forward currently on the roster", not "against any forward they could get".


### D31. The slot constraint applied to every player-specific move, and the one verdict it costs us (S1)

C3 constrained only Kuminga's minutes to his position. That was inconsistent: if the counterfactual for a forward is "another forward plays", the same has to be true for a guard and for a big, or the constraint is being applied wherever it helps. S1 applies it to the whole Shapley set.

**The mechanism.** `rotation.allocate_pooled` splits the 240 team minutes into three position budgets (guard, forward, big) from the primary listing in `nba_player_bio`, and water-fills within each pool against the same per-player ceiling the C2 run uses. Removing a guard means the freed minutes stay in the guard budget.

| Move | Pool | Unconstrained | Slot-aware | Mean, before to after |
|---|---|---|---|---|
| other_departures | bundle | MIXED | **ALL POSITIVE** | +0.15 to +1.12 |
| ball_in | guard | ALL POSITIVE | ALL POSITIVE | +1.30 to +0.67 |
| randle_out | frontcourt | ALL POSITIVE | **MIXED** | +0.19 to +0.07 |
| kuminga_in | forward | MIXED | MIXED | -0.04 to -0.06 |
| reid_out | frontcourt | ALL NEGATIVE | ALL NEGATIVE | -0.98 to -0.26 |
| ddv_injury | availability | ALL NEGATIVE | ALL NEGATIVE | -0.72 to -0.35 |
| depth | bundle | MIXED | **ALL NEGATIVE** | +0.10 to -0.36 |
| dosunmu_retained | guard | ALL NEGATIVE | ALL NEGATIVE | -0.52 to -0.40 |

**One player-specific verdict flipped: `randle_out`.** It goes ALL POSITIVE to MIXED (consensus -0.007, RAPM +0.117, box +0.133, DARKO +0.021). Per Bobby's rule it **loses its QUOTABLE label**. "Letting Randle go helped" is no longer a claim the piece can make. What survives is the weaker and more honest version: the effect is small and the four views do not agree on its sign, which is a different sentence and belongs in the honesty rail rather than the verdict.

Two bundles also flipped (`other_departures`, `depth`). They are not player-specific so the rule does not bite, but they should not be quoted with a sign either, because a verdict that moves this much on a modelling choice is not a finding.

**Dosunmu, which is what Bobby actually held back.** He survives: ALL NEGATIVE both ways, mean -0.52 to -0.40, slot-aware band [-0.758, -0.126]. Constraining his minutes to the guard pool, which was the specific worry (his replacement was being drawn from the whole roster, so the counterfactual roster was implausibly good), moves him a tenth of a percentage point and does not touch the sign. **He is now quotable.** The D29 caveat still attaches: the move set has no "replacement guard" to sign, so this is "retaining Dosunmu at his minutes versus his minutes going to the guards already on the roster", not "versus any guard available".

**Why MIN needs its own pool budget, and the artifact it would otherwise have created.** The first pooled run used league-average shares (guard 49.81%, forward 36.11%, big 14.08% of 240 minutes). Under that budget `reid_out` flipped to MIXED. It is an artifact: **Minnesota played the most big minutes in the league last season, 53.7 a game against a league mean of 33.8, rank 1 of 30.** Gobert at 31.3 and Reid at 26.1 cannot both fit inside a 33.8-minute budget, so the league-average version deleted the double-big shape that is the whole reason Reid's departure matters. `allocate_pooled` now takes a `budget_share` argument and the Shapley run passes Minnesota's own 2025-26 shares from `team_pool_shares.csv`. With the team budget `reid_out` returns to ALL NEGATIVE. **Reported because it was nearly a published flip caused by a default, not by the data.**

**Which run is primary.** The slot-aware run, for the C3 reason: a counterfactual that hands a departing player's minutes to whoever the model rates highest is not available to a coach. The unconstrained table is preserved in `shapley_min.csv`; the slot-aware one is `shapley_min_POOLED.csv` and the comparison is `outputs/S1_shapley_slot_comparison.csv` (run `compare_slot_shapley_20260827T133633Z`).

### D32. The Kuminga finding does not survive every fill, so the claim gets narrowed (S2)

C3's answer depended on identifying Terrence Shannon Jr. as the man who takes the 4 minutes. S2 re-prices the same marginal contribution under five different answers to "who fills the slot".

| Variant | Filled by | Verdict | Band (pp) |
|---|---|---|---|
| A. C3 default | McDaniels +2.7, Shannon +15.5 | ALL POSITIVE | +0.140 to +1.226 |
| B. Lyles forced | Lyles +26.0 | **MIXED** | -0.912 to +0.684 |
| C. McDaniels slides | McDaniels +19.5, then next wing | ALL POSITIVE | +0.140 to +1.204 |
| D. Beringer forced | Beringer +26.0 | **ALL NEGATIVE** | -3.046 to -0.394 |
| E. Forward / Forward-Centre only | McDaniels +2.7 (23.3 unplaced) | **MIXED** | -0.912 to +0.665 |

**Ruling: all-positive does NOT survive every fill.** Per Bobby's decision rule the section claim reads **"against the most likely internal alternative"**, never "against any internal alternative", and the three failing fills are named: Lyles forced into the role, Beringer forced into the role, and the tighter Forward-or-Forward-Centre eligibility rule.

**Why the two "forced" variants are fair tests and not straw men.** Under last season's minutes both Lyles and Beringer have zero headroom: Lyles played 6.0 a game so his ceiling is 9.0 and the rotation already has him at exactly 9.0; Beringer played 7.85 so his ceiling is 10.85 and he is already at 10.85. That is the only reason the C3 fill order skipped past them to Shannon. But "if Lyles were the starter" is a question about a role Finch could assign, not about last season's usage, so B and D lift the ceiling to 36.0 for the named filler. **Reading D correctly: it says a Kuminga-to-Beringer swap is a downgrade under all four views, which is a finding about Beringer, not evidence against Kuminga.** B is the one that genuinely narrows the claim, because Lyles at starter minutes is a real thing a coach might do and the four views split on it.

**Variant E and the rule collision.** C3 calls a player eligible at the 4 if the listing contains "Forward" and is not centre-first, which admits Shannon (Guard-Forward). The S1 pool rule keys on the *primary* listing, which makes Shannon a guard. The two rules disagree about exactly the one player C3's answer turns on. E applies the strictest reading (Forward or Forward-Centre only) and leaves **23.3 of Kuminga's 26.0 minutes unplaceable**, which is itself the honest result: under a strict positional reading Minnesota does not have a backup 4, and that is closer to the argument for the signing than to an argument against it. Say that, rather than picking the rule that gives the nicer number.

`outputs/slot_robustness.csv`, run `slot_robustness_20260827T130634Z`.

### D33. The lede was overstated, and a reader with a calculator would have caught it (S3)

"Could not legally sign him" is false as written. **An exception may be used partially.** Minnesota sits $5,814,171 below the second apron, so a first-year salary of exactly that fits, puts team salary on $221,686,000 to the dollar, and is legal, because the hard cap prohibits *exceeding* the apron rather than reaching it. That is 95.9% of the taxpayer mid-level.

**Change to a previously reported figure:** none. $249,829 is unchanged and correct. What changes is the sentence it supports. **Before:** "could not legally sign him." **After:** "could not sign him for the money they had agreed to pay him", with the loophole stated in the piece rather than left for a reader to find.

Two things close the loophole and both are now in section 1:
- **It costs Kuminga $512,149** over two years at the 5% maximum raise. The player who just declined the Lakers to protect his own optionality is not the obvious person to volunteer it.
- **It freezes the roster at 14 for the season.** Exactly on the apron, Minnesota cannot sign a fifteenth man, absorb a dollar in any trade, or replace an injured player. Carry a fifteenth at the rookie minimum and Kuminga's ceiling falls to $4,456,171, 73.5% of the exception.

**CBA verification, both checked 2026-08-27 per R8.** The roster minimum is **Article XXIX, Section 2(a)**: 14 or 15 players on the Active and Inactive Lists during the regular season. **Section 2(b)(i)** permits 12 or 13 for no more than two consecutive weeks at a time and 28 days in total, so "14-man roster" is a season-long floor with a short grace period, not a daily requirement. Sources: the CBA full text mirror (atlhawksfanatic.github.io/NBA-CBA/miscellaneous.html) and cbaguide.com/eligibility/rosters/. The hard-cap verb is **exceed**, confirmed against Larry Coon's Salary Cap FAQ (cbafaq.com/salarycap17.htm), which is what makes the partial-exception figure land on the dollar rather than a dollar under.

`outputs/lede_loophole.csv`, `outputs/lede_loophole.md`, run `lede_loophole_20260827T134245Z`.

### D34. Skeleton edits, and the one that was not on the list (S4)

Applied as briefed: the win-total backtest into section 6's honesty rail (**this model missed by 8.80 wins on average over three seasons, the betting market by 7.47**, and the market tracked actual wins better in all three); the single-fork play-in sentence removed and replaced with what the band itself says; "adjudicates" softened to "consistent with", since one bid is one observation and not an adjudication; the sign-and-trade caveat moved to sit directly beside the 4% figure rather than living elsewhere; and the age corrected to **23, turning 24 in October** (born 2002-10-06, verified against the frozen `player_bio` snapshot).

**Not on the list, but forced by S1.** Section 4 had to be rebuilt, because its table and its thesis sentence both depended on verdicts that S1 retired. The Randle row is gone. The thesis sentence, "hold the injury out and the transactions were mildly positive", is **ALL POSITIVE under the slot-aware run and MIXED under the unpooled one**, so it flips on a modelling choice and cannot carry a sign. It is replaced by the claim that does survive: the Achilles is the largest single negative under every view, and it is the only item on the board nobody chose. Section 7's verdict was brought in line at the same time, and now names the two load-bearing words in its own central claim.

**A bug in the numbers sheet, caught by an exception rather than by a wrong answer.** `build_final_numbers.py` built a lookup with `{x.item: ...}` over `df.iterrows()`. `Series.item` is a **method**, so the dict was keyed by bound method objects and every lookup missed. It raised a KeyError on a key that was plainly present in the CSV, which is why it was found immediately. Worth recording because the same collision is silent when the shadowed name is used for something other than a lookup: `.name`, `.count`, `.size`, `.min` and `.max` are all columns this project could plausibly create. **Index by string, not by attribute, on any frame whose column names are not controlled here.**

### D35. The Friday slide (S5)

Rendered: `kuminga/slide/kuminga_apron.png`, config `kuminga/slide/kuminga_apron.json`, plus a 319-word companion at `kuminga/slide/kuminga_apron_post.txt`.

Four tiles carry the arithmetic ($215.9M on the books, $6.06M exception, $221.7M apron, $249,829 over), the catch line carries the S3 loophole ("They can pay Kuminga $5,814,171 today. Just not the full exception."), and the footer credits the contract book as of 2026-08-26 and flags the terms as reported rather than official. Every figure on the slide is on `final_numbers.csv`; the config carries a `_provenance` block mapping each number to the run that produced it, since a run ID cannot go on a public post.

**The renderer had to be localised, and it would have failed quietly.** The skill bundle ships `FONT_DIR = "/usr/share/fonts/truetype/dejavu/"`. On Windows every `ImageFont.truetype` call raises OSError, the handler falls through to `ImageFont.load_default()`, and the script **renders a 1080x1350 slide in a tiny bitmap font and exits 0**. A copy now lives at `kuminga/slide/render_slide.py` mapped to the same Windows faces the approved lamelo carousel uses (bahnschrift condensed, Segoe UI, Consolas Bold for numerals), with an `_assert_fonts()` guard that refuses to render rather than emitting a broken slide. The skill bundle itself is untouched.

### D36. Dosunmu is two claims, and together they say less than either does alone (P1)

Split in the skeleton and on the numbers sheet as **Dosunmu (a) on-court** and **Dosunmu (b) cap**, so neither can borrow the other's authority.

**(a) On-court.** His minutes against the guards actually on the roster: **-0.13 to -0.76pp, negative under all four views**, quotable as a band `[shapley_20260827T134406Z]`.

**The counterfactual, now stated explicitly in the piece.** It is **"lose him for nothing"**, not "spend the money elsewhere". Minnesota was over the cap, and an over-the-cap team has exceptions rather than room, so $19,310,345 was never convertible into a better guard at that price. The alternative being priced is his minutes going to Ball, Edwards, Clark and Hyland with nobody arriving. This matters because the natural misreading of a negative Shapley value on a contract is "that money was wasted, spend it better", and that option did not exist.

**(b) Cap** `[dosunmu_cap_20260827T144259Z]`. On the pre-Kuminga book Minnesota is $15,443,829 over the tax line with an estimated **$30.9M** bill. Without his salary they are **$3,866,516 under the line owing nothing**, and still under it after filling to the 14-man floor with two minimums. **His is the contract that makes them a taxpayer.** It also sized the tool they signed Kuminga with: without him they sit **$12,453,516 under the first apron**, where the non-taxpayer mid-level lives, so the exception available to chase a forward would have been **up to $12.45M rather than $6,064,000**.

**Why the split matters and is not pedantry.** (a) says the minutes are worth less than the guards behind him. (b) says the money bought tax liability and a smaller exception. Stacked carelessly they read as "they should have let him walk", which does not follow, because (a)'s counterfactual is losing him for nothing and being worse on the floor. The composite the evidence supports is narrower: Minnesota paid a taxpayer's price for a player their own minutes model grades below his replacements, and the bill arrived as a $6M exception instead of a $12M one.

**Two provenance notes.** The tax rates are flagged CONFIRM in `league_year_constants`, so every tax figure is labelled est. And the contract book carries four years ($86,510,348); the reported five-year $112M total includes a 2030-31 season not in our data, so the $112M is reported terms and not derived here.

### D37. The injury claim fails the per-view check, and so does the fallback (P2)

Asked whether the DiVincenzo Achilles is the largest single negative under **each** of the four views in the slot-aware run rather than on the mean. It is not, and it is not close.

| View | Largest single negative | ddv_injury | Its rank |
|---|---|---|---|
| consensus | depth, -0.332 | -0.218 | 4 of 8 |
| RAPM | dosunmu_retained, -0.443 | -0.189 | 4 of 8 |
| box | **ddv_injury, -0.356** | -0.356 | 1 of 8 |
| DARKO | dosunmu_retained, -0.758 | -0.627 | 3 of 8 |

**It is the largest under one view of four. Under RAPM it is the smallest of the four negatives on the board.**

**The specified fallback also fails, so I did not write it.** The instruction was to fall back to "the largest negative on the mean and the only item nobody chose" if the per-view check failed. It is **not** the largest on the mean either: it ranks **third of eight** at -0.348, behind `dosunmu_retained` at -0.402 and the `depth` bundle at -0.356. Writing the fallback would have replaced one false superlative with another.

**What went in instead**, which needs no superlative: the Achilles is **negative under all four views**, it **survives the slot rule**, and it is **the only item on the list nobody chose**. Every other line is a decision somebody made. The failed superlative is now stated in the skeleton as a do-not-write, with the three ways it is wrong, so it cannot creep back in during drafting.

`compare_slot_shapley_20260827T134414Z`; the check is now a permanent row on `final_numbers.csv` rather than a one-off.

### D38. The methods note names the assumption that is most likely to be wrong (P3)

Added a Methods section to the skeleton. The sentence asked for, in full:

> **Positional minute budgets are each team's own 2025-26 shape, not a league average.** For Minnesota that assumes a **double-big allocation the current roster cannot repeat**: last season's 53.7 centre minutes a game were Gobert plus Reid, and Reid is gone.

With the reason it is still the right choice: holding the shape fixed while the personnel changes is what makes "what did the departures cost" answerable at all. It is simply the wrong tool for forecasting how Finch will play this roster, and every Shapley figure in the piece should be read as "what these moves did to last season's shape" rather than as a rotation projection. This is the same fact that made the league-average budget an artifact in D31, pointed at our own result instead of at the alternative.

### D39. Section 3 gets its setup (P4)

Two facts added ahead of the fill-robustness discussion, both with run IDs:

- **Minnesota is the most big-heavy team in the league**: 53.7 centre minutes a game, **first of thirty**, against a league mean of 33.8 `[build_rotations_20260827T133313Z]`. This is what makes "who can actually take these minutes" a constraint rather than a technicality.
- **Under strict eligibility, 23.3 of Kuminga's 26 minutes have nobody to go to.** Behind Lyles there is no eligible 4 `[slot_robustness_20260827T133141Z]`. The line the section now carries: Minnesota did not sign a power forward into a crowded room, they signed one into an empty one.

The Lyles split then arrives as the honest narrowing rather than as a hedge bolted on at the end: it is the one failing fill a coach could actually choose, and the four views disagree about it.

### D40. The Dosunmu cap claim shrinks by a third once the roster has to be legal (D1)

**Change to a previously reported figure, per the standing rule.**

| Figure | Before (D36) | After (D40) |
|---|---|---|
| Usable exception without him | **$12,453,516** | **$7,555,516 to $8,646,516** |
| Advantage over the taxpayer MLE | $6.39M | **$1.49M to $2.58M** |
| Tax position without him | "$3,866,516 under, owing nothing" | **$59,516 under to $1,031,484 over** |

**What was wrong.** D36 computed the counterfactual by subtracting his salary and stopping, which leaves **twelve** players. That is not a team, it is a violation of Article XXIX Section 2(a). Replacing him and filling to the 14-man floor puts most of the apparent room straight back on the books.

**The replacement charge, verified rather than assumed.** A veteran with three or more years of service signing a **one-year** minimum is charged the **two-year** minimum against team salary, **$2,449,000** for 2026-27, with the league paying the difference against the $3,877,000 such a player actually earns. Multi-year minimums count in full. So the right charge for a replacement guard is neither the rookie minimum nor what the player takes home. Source: Hoops Rumors glossary, minimum salary exception (hoopsrumors.com/2026/03/hoops-rumors-glossary-minimum-salary-exception-5.html), consistent with the CBA minimum-salary exception.

**Both figures are ranges because the last roster spot swings them.** Fill the 14th slot with a rookie minimum and they land $59,516 under the tax line with $8,646,516 under the first apron; fill it with another veteran minimum and they are $1,031,484 over the line with $7,555,516 of room. The piece quotes the range, and the conservative end leads.

**Two claims are retired.** "His is the contract that makes them a taxpayer" overstates it: at a legal roster the no-Dosunmu team **straddles** the tax line. The printable version is that his contract is the difference between roughly level with the line and $15,443,829 past it. And "the tool would have been up to $12.45M" is replaced by **"up to $7.6M to $8.6M at a full roster, against $6,064,000"**, an extra $1.5M to $2.6M of buying power. Still a real finding, and a third of the size of the one that nearly went in.

**Also corrected in the run log itself.** The `dosunmu_cap` notes previously printed the 12-man subtraction as a headline before correcting it further down, which would have left a superseded number sitting in the provenance trail. The note now says the bare subtraction is not a team and points at the legal-roster figure.

`dosunmu_cap_20260827T152542Z`.

### D41. Dosunmu rewritten cap-first, and the two claims labelled by kind (D2)

The paragraph now runs **cap arithmetic first, on-court finding second**, because the cap half needs no model and the on-court half does. The sentence separating them, in full:

> The cap half is arithmetic on contracts and CBA thresholds, and it is true regardless of what anyone thinks of the player; **the on-court half is a model claim about impact metrics**, and it inherits every assumption those metrics carry, including the minutes rule described in the methods note.

The differing counterfactuals are kept explicit: the on-court number prices **losing him for nothing**, the cap number prices **the exception his absence would have unlocked**, and they are about different players at different positions, which is why they do not add. The paragraph closes on the boundary rather than a recommendation: "Reported together, they describe a cost; neither one, nor both, establishes what Minnesota should have done instead." **"Should have let him walk" does not appear**, and the structure is built so a drafting pass cannot arrive there by accident.

### D42. The per-view table is now the worked example for the whole editorial rule (D3)

Moved the P2 ranking table into the methods appendix under the heading "Why this piece reports signs and never rankings", which is what it actually demonstrates. All four views agree the DiVincenzo injury hurt; they place it 4th, 4th, 1st and 3rd of eight. The contrast the section draws:

> "The Achilles was the biggest blow of Minnesota's offseason" is the kind of sentence this data cannot support, while "the Achilles hurt, under every way we know how to measure it" is one it supports easily.

Better placed here than buried in section 4 as a do-not-write, because it generalises: it is the reason the piece carries bands rather than midpoints, signs rather than orderings, and four views rather than one. Section 4 keeps the short version.

### D43. As final states, the Dosunmu re-signing cost roster and not money (F1, F2)

**This is the third revision of the same figure, and the framing changed rather than the arithmetic.** Comparing two finished rosters, both legal, both fourteen men, both with Kuminga on them `[dosunmu_final_states_20260827T154349Z]`:

| | Payroll | vs tax line | Est. tax | Kuminga at | Green |
|---|---|---|---|---|---|
| What happened | $208,614,817 | $8,186,817 over | ~$13.1M | $6,064,000 | traded away |
| Dosunmu not re-signed | $209,015,000 | $8,587,000 over | ~$13.8M | up to $10,004,516 | **kept** |

**The result that retires the tax framing entirely.** The two states are within $400,183 of each other on payroll and within about $700k on tax, and **the counterfactual is the more expensive one**. Both are taxpayers. So "his contract is the difference between roughly level with the tax line and $15.4M past it" (D40) is gone: it was an artifact of comparing a roster with Kuminga against one without him. The claim that replaces it is better and simpler. **Re-signing Dosunmu did not cost money. It cost Josh Green plus about four million dollars of Kuminga's first-year salary, at the same payroll and in the same tax bracket.**

**Why Green must be shed, now stated as arithmetic in the piece.** With both contracts on the book, $215,871,829 + $6,064,000 = $221,935,829, which is $249,829 past the second apron. Dosunmu's $19,310,345 exceeds that overage by $19,060,516, so **without him Green stays and the signing still fits**. The Saturday deadline in section 1 traces to a July contract.

**The ceiling, with its caveat attached.** Without Dosunmu, a replacement guard on a veteran minimum leaves $10,004,516 under the first apron at thirteen players, and that distance *is* the ceiling on Kuminga's first-year salary, because the non-taxpayer mid-level hard-caps there. The exception is worth $15,044,000 and **the whole of it was never spendable**, so the phrasing is fixed as **"up to $10,004,516 at a full roster"**. A rookie-minimum replacement lifts it to $11,095,516; $8M for Kuminga would leave room for a fifteenth man and $9M would not.

**Figure supersession, logged because two of our own numbers now disagree.** The D40 figure of $7,555,516 to $8,646,516 filled to fourteen with minimums first and left the exception signee as a *fifteenth* man. Putting Kuminga inside the fourteen, which is the comparable roster, gives $10,004,516. Both are correct answers to different questions, and only one is the question the piece asks. The superseded row is still on `final_numbers.csv` under **"Dosunmu intermediates (do not quote)"**, labelled SUPERSEDED and marked NOT QUOTABLE, with a pointer to the final-state rows. The intermediate roster figures moved to their own appendix in the skeleton for the same reason: read alone, the 12-man line suggests Minnesota could have ducked the tax, and at a legal roster with Kuminga they land at roughly $209M either way.

### D44. Keeping Josh Green is MIXED, so the salary dump carries no on-court cost (F4)

Both cap branches assume Green leaves. That is a cap assumption that had never been asked as a basketball question, so it was priced as one coalition under the slot rule with Minnesota's own position budgets.

**Verdict: MIXED, -0.48 to +0.01pp, mean -0.18pp** `[green_kept_20260827T154636Z]`. Only RAPM is positive, by 0.014pp. Per the rule set for this item, it **stays in the appendix and the piece attaches no on-court cost to losing Green.** Three of four views think the minutes are better spent elsewhere; they do not agree, so nothing is claimed either way.

Two caveats recorded with it. The pooled rule gives Green 13.3 minutes and takes them proportionally across the whole guard group including Edwards, which is not how a rotation works. And his impacts span -0.22 (box) to -2.00 (DARKO), so the disagreement here is about the player rather than the method.

**A bug that produced a plausible table before it produced an error.** `build_impacts` keys by **string** player id and returns a **dict per player**, not a float. The first version looked up `imps[f].get(float(GREEN_ID))` and reported all four impacts as NaN and Green's minutes as 0.00, while the marginal contributions printed as real numbers. That combination is incoherent, a player with no minutes cannot move the odds, which is what flagged it. The pricing path was in fact correct throughout, because `allocate_pooled` and `A.rollup` both key by `str(int(pid))`; only the diagnostics were wrong. **The lesson is that the diagnostic and the computation must share a key convention, or the diagnostic will vouch for something it never inspected.** An assertion now fails the run if Green draws no minutes.

### D45. Section 4 magnitudes labelled (F3)

The table row is now **"Dosunmu retained (on-court)"**, so a reader cannot take a Shapley number as a verdict on the contract. Added: applying the slot rule cut every magnitude in that table, by between a quarter and three quarters, and moved none of their signs. The looser rule flatters big effects by letting minutes flow to whoever the model rates highest, so the sizes shown are the conservative version and the signs are the finding.

### D46. Dosunmu was agreed three days before the trade that brought Green in

**The warehouse cannot answer this, and the way it fails is worth recording.** Both rows carry `transaction_date = 2026-07-10`:

| Date | Player | Type | Description |
|---|---|---|---|
| 2026-07-10 | ayo-dosunmu | Signing | Minnesota Timberwolves re-signed guard Ayo Dosunmu to a Contract. |
| 2026-07-10 | lamelo-ball | Trade | Minnesota Timberwolves received guard LaMelo Ball from Charlotte Hornets. |
| 2026-07-10 | josh-green | Trade | Minnesota Timberwolves received guard Josh Green from Charlotte Hornets. |

That is the **official** date for both, the day the league processed them after the moratorium. The two sort columns look ordinal and are not: `additional_sort` is **0 for every signing and the counterparty team id for trades** (1610612766, Charlotte), and `group_sort` is a type-prefixed group id (`Signing 1153092`, `Trade 2026008`). `created_at` is our own ingest batch, not league time. **The same hazard as `action_number`: a column that sorts cleanly and means something else.** Do not use any of the three to order same-day transactions.

**The agreement dates, from primary reporting (R8, two sources each).**

- **Dosunmu: agreed the night of Monday 2026-06-22.** ESPN published 2026-06-23 at 12:02 AM ET: "Dosunmu's agents... worked with Timberwolves executives on Monday night to ultimately secure the long-term commitment" (espn.com/nba/story/_/id/49150075). Corroborated by NBA.com's report of the same five-year, $112M deal (nba.com/news/reports-ayo-dosunmu-to-re-sign-with-timberwolves).
- **Ball and Green: agreed Thursday 2026-06-25.** ESPN, Ohm Youngmisuk, published 2026-06-25 09:35 AM ET, "sources told ESPN's Shams Charania on Thursday", and the trade explicitly sends "LaMelo Ball and Josh Green to the Minnesota Timberwolves for Naz Reid and a series of draft picks" (espn.com/nba/story/_/id/49175343). Corroborated by NBA.com (nba.com/news/lamelo-ball-trade-timberwolves-2026) and the club release (timberwolves.com).

**Which came first: Dosunmu, by three days.** Both became official on Friday 2026-07-10.

**Why this matters to claim (a), and the limit on it.** Section 4 says Green has to be shed to fit Kuminga. The sequence supports that ordering: the $19,310,345 commitment to Dosunmu was reported before Minnesota agreed to take Green's $14,679,012 back. **But it does not establish that they were decided in that order.** A four-team trade of that size is negotiated over weeks, so the two were almost certainly live at once, and a reported-first date is not a decided-first date. The piece may say the Dosunmu agreement was reported three days earlier; it may not say Minnesota chose Dosunmu and then took Green anyway.

**And one fact that was not in the model's framing at all: Green did not arrive separately.** He came from Charlotte in the LaMelo Ball trade, as part of the same deal that sent Naz Reid out. Every earlier note treats him as a salary already sitting on the book. He is salary Minnesota **took on**, three days after committing to Dosunmu, in the trade that is the largest positive in the Shapley table.

### D47. "A player cannot come back in a Green trade" was wrong, in two places

**Correction to a previously reported claim.** Section 1 said "any player coming back in a Green trade crosses it, because the smallest contract that **can legally** come back is $1,358,000", and claim (a) said Green "cannot be flipped for a player". Both confused *costly* with *prohibited*.

**What is actually true.** A Green trade can bring salary back. The binding ceiling is the **second-apron hard cap**, which leaves **$13,071,183 of room at a fourteen-man roster** `[cap_branches_20260827T023847Z]`. That is the constraint that binds, not the trade-matching rules: Green goes out at $14,679,012, so matching would allow more than the hard cap does. Crossing the **first** apron is permitted; it is not a hard cap for Minnesota, whose hard cap sits at the second apron from using the taxpayer MLE.

**What crossing the first apron costs, now stated as four things** rather than the three in the old runbook note:
1. No **sign-and-trade** acquisition.
2. No **bi-annual exception**, $5,477,000.
3. No **trade exception generated in a prior year**.
4. **Tighter matching**: cannot aggregate two salaries to match one larger one, cannot take back more than is sent out.

The fifth restriction usually listed, losing the non-taxpayer mid-level, is **moot here** and is flagged as such, because the taxpayer version is what signs Kuminga.

**The reframe that follows.** "The re-signing removes every option except the dump" is replaced by **"it removes keeping him, and makes every other exit cost something"**. There are two exits and both are charged: a pure dump costs whatever pick or swap moves a $14.7M expiring for nothing, and a trade that returns a player costs the first-apron restrictions for the season. Section 1's closing line changed from "the pure salary dump is not one option among several" to "it is **not the only legal option**; it is the only one that keeps them under the first apron".

**Fixed in all four places** so the terms match: section 1, claim (a), `lock_runbook.md` L1 item 4, and two new rows on `final_numbers.csv` ("salary a Green trade can bring back", $13,071,183; "incoming salary that costs the tier", $400,183).

### D48. The independent recomputation broke the lede (V1)

A fresh context with no access to `kuminga/scripts` or `kuminga/lib` recomputed every published cap figure from raw sources. **The arithmetic was clean throughout. The inputs and the CBA rules were not.** Six material errors, two of which are publication-blocking.

**ERROR 1, the lede is wrong by 8x. Apron Team Salary includes UNLIKELY BONUSES.**

Regular Team Salary excludes unlikely bonuses. The apron calculation removes cap holds and **adds them back**. Minnesota carries **$1,750,000** of them: Jaden McDaniels $1,000,000 and Donte DiVincenzo $750,000.

| | Before | After |
|---|---|---|
| Pre-Kuminga apron basis | $215,871,829 | **$217,621,829** |
| With Kuminga | $221,935,829 | **$223,685,829** |
| **Over the second apron** | **$249,829** | **$1,999,829** |
| The "loophole" first-year salary | $5,814,171 | **$4,064,171** |
| Cost of the loophole to Kuminga | $512,149 | **$4,099,649** |

**Independently confirmed twice.** The rule: Hoops Rumors tax-apron glossary and the CBA Guide both state Apron Team Salary = Team Salary − cap holds + unlikely bonuses. The magnitude: **Spotrac's own page computes "2nd Apron Space: $4,064,172"** against our $4,064,171, a one-dollar difference traceable to McDaniels ($26,200,000 there, $26,200,001 in Basketball-Reference, SalarySwish and our book).

Everything in section 1 keyed to $249,829 is gone. So is the slide, whose headline is literally "SHORT BY $249,829".

**ERROR 2, a sign flip. The trade branch is a FIRST-APRON team.** At a legal 14-man roster it is now **$1,349,817 OVER** the first apron, not $400,183 under. The consequence inverts: it is no longer "any incoming salary above $400,183 costs the tier", it is **they are already a first-apron team in the pure-dump branch, before anything comes back.** Section 1's "the only version that keeps them under the first apron" is false. The four restrictions apply either way.

**ERROR 3, the luxury-tax schedule was the pre-2023 CBA table.** `tax_brackets_nonrepeater_approx` used a **$5,000,000** bracket width with rates 1.50/1.75/2.50/4.75/5.75. The 2026-27 schedule is a **$6,064,000** width with non-repeater rates **1.00/1.25/3.50/4.75, +0.50 per bracket after**. The width is checkable arithmetic: $5,000,000 indexed to the cap is 5,000,000 x 164,961,000 / 136,021,000 = $6,063,806, i.e. $6,064,000; the constants had frozen the 2023-24 value. Verified against Hoops Rumors and the CBA Guide, which agree.

Our figures were **22% to 50% too high**: the 13-player book falls from $30,858,188 to **$25,249,402**, and the trade branch from $13,076,930 to **$8,717,521**. Fixed in `league_year_constants.json`, which the offseason project shares, with the repeater schedule added and the source recorded. `tax_brackets_confirm` flipped from True to False.

**ERROR 4, the Non-Bird figure uses the wrong base year.** Published $7,640,640 = 120% of the *declined option year* ($6,367,200). Non-Bird is 120% of the salary in the **last season actually played**, so if he opts out after 2026-27 that is $6,064,000 and the ceiling is **$7,276,800**. The published figure was also internally inconsistent with itself: in any branch where $6,367,200 is the prior salary he has played two seasons in Minnesota and holds **Early Bird** rights, which is exactly the U4 finding, so Non-Bird would not bind there at all.

**ERROR 5, a live deadline the model has no date condition for.** The current season's salary can only be stretched if the player clears waivers by **August 31**, and waivers run 48 hours. Green has no seasons after 2026-27. If Minnesota does not waive him by roughly **August 29**, the stretch branch **ceases to exist** and the full $14,679,012 stays on the book. That is the Saturday lock date, and the runbook models the branch with no date condition on it.

**ERROR 6, `min_salary_by_yos` is rounded to the nearest $1,000 throughout.** Real values: rookie minimum **$1,357,763** (not $1,358,000), 2-YOS **$2,449,421** (not $2,449,000), 10+ YOS **$3,876,529** (not $3,877,000). This puts a small error into every roster-fill figure and makes the claim that a partial exception "lands team salary on the apron to the dollar" unsupportable at that precision.

**Also surfaced, not yet actioned:** Minnesota holds two live prior-year trade exceptions worth **$17,350,158** (Conley $10,774,038 expiring 2/3/2027, Dillingham $6,576,120 expiring 2/5/2027), which the first-apron restriction list mentions without naming; Trey Lyles is only **$1,500,000 guaranteed** of a $2,449,421 cap hit with a 1/10/2027 guarantee date, while our book marks him fully guaranteed; the two-way line names one player when there are three; and Spotrac already displays Minnesota as hard-capped at the second apron for a reason the check could not identify.

**Cross-check of the 13-player total (Part B).** Ours $215,871,829; **Spotrac $215,871,828**, a one-dollar difference on McDaniels, same 13 players, no holds, no dead money; **HoopsHype $218,886,255** across 16 rows, which reconciles exactly once three two-ways ($2,036,646) are removed and three line items are explained: HoopsHype prints Lyles at what he is *paid* ($3,876,529) rather than his cap charge, has McDaniels $450,000 low against three other sources, and Hyland $672 high. **Our cap-basis figure is right; it was the apron basis that was wrong.**

### D49. The aging pass exposed an architecture fact worth more than the aging pass (U1, partial)

Fitted a one-year aging curve from `nba_player_season_bio`, on same-team year-over-year net-rating deltas, shrunk n/(n+40), 2000 onward. Peak at **27**. Applied adjustment runs from **+0.767** impact points at age 20 to **-0.353** at 36. Minnesota is **+0.176**, 18th of 30.

**Two errors caught inside it.**

**First, applying the curve as distance-from-peak double-counts age.** A player's measured impact already reflects how old he was. The projection needs only the expected *one-year change*. The first version applied the cumulative curve and made **20-year-old Joan Beringer the most penalised player on Minnesota at -2.864**, when the same data says he should improve by +1.5 net points. Caught because a rookie centre being the biggest age penalty on a roster containing 35-year-old Rudy Gobert is absurd on its face.

**Second, and this is the finding: aging cancels out of this model by construction.** `exp_2026_27` comes from last season's measured team rating, and the impact model enters only as `beta x (roll[current] − roll[baseline])`. Both rollups were being built from the same aged impacts, so **every returning player's adjustment cancelled exactly** and the aged run reproduced the un-aged team strengths to all 120 rows. The fix is that the baseline rollup must use un-aged impacts, because it represents last season's roster at last season's ages. Now corrected, and the aged strengths do move.

**What this means for reading any Shapley number in this project:** the model has never been able to see a roster simply getting older. It only ever sees the difference between who left and who arrived. That is a real limitation and it belongs in the methods note regardless of what the aged verdicts turn out to be.

### D50. The corrected cap chain, on the apron basis (R1, R2)

**Rule, with both citations.** Apron Team Salary = Team Salary **minus** free-agent cap holds **plus** unlikely bonuses. Hoops Rumors, tax-apron glossary: "the Aprons make adjustments to Team Salary by removing Cap Holds and adding Unlikely Bonuses, which is called Apron Team Salary" (hoopsrumors.com/2025/01/hoops-rumors-glossary-tax-aprons-2.html); The CBA Guide, The Aprons (cbaguide.com/thresholds/apron/). Minnesota's unlikely bonuses: **McDaniels $1,000,000, DiVincenzo $750,000**.

Published once to `outputs/cap_canonical.json` and read from there by `lede_loophole`, `dosunmu_cap`, `dosunmu_final_states`, `eval_signing` and `cap_branches`. **No consumer re-derives the basis any more**, which is the structural fix: the 8x error propagated because five scripts each rebuilt the basis from a component row.

| Figure | Old (contracted basis) | Corrected (apron basis) |
|---|---|---|
| Pre-Kuminga | $215,871,829 | **$217,621,829** |
| With Kuminga | $221,935,829 | **$223,685,829** |
| Over the second apron | $249,829 | **$1,999,829** |
| Loophole first-year salary | $5,814,171 (95.9% of the MLE) | **$4,064,171 (67.0%)** |
| Loophole cost to Kuminga | $512,149 | **$4,099,649** |
| Trade branch, 13 / 14 / 15 | — | **$209,006,817 / $210,364,580 / $211,722,343** |
| Stretch branch, 13 / 14 / 15 | — | **$213,899,821 / $215,257,584 / $216,615,347** |
| Trade branch vs first apron at 14 | $400,183 UNDER | **$1,349,580 OVER** |
| Stretch branch vs first apron at 14 | $4,492,821 over | **$6,242,584 over** |
| Second-apron room, trade / stretch at 14 | $13,071,183 / $8,178,179 | **$11,321,420 / $6,428,416** |
| No-Dosunmu counterfactual, Kuminga ceiling at 13 | up to $10,004,516 | **up to $8,254,095** (vet-min replacement), **$9,345,753** (rookie-min) |
| Non-Bird 2027 ceiling | $7,640,640 | **$7,276,800** |

**The finding that changes section 1's argument: both branches are first-apron teams.** The trade branch is $1,349,580 over, not $400,183 under. Every "the pure dump is the only version that keeps them under the first apron" sentence is deleted, because no version does. The four restrictions apply either way, and the one with a price tag attached is the prior-year trade exceptions: Minnesota holds **$17,350,158** live (Conley $10,774,038 to 2/3/2027, Dillingham $6,576,120 to 2/5/2027) and cannot use them.

**Non-Bird, corrected basis.** 120% of the salary in the last season actually **played**. If he opts out after 2026-27 that is the year-one figure $6,064,000, giving **$7,276,800**. The old $7,640,640 took 120% of the *declined* option year, which is both wrong and self-contradictory, since in any world where $6,367,200 is the prior salary he has two seasons of service and holds Early Bird rights instead (175% = $11,142,600, per D-log U4).

**R2, the tax basis, now stated on every tax row.** Tax is charged on **regular team salary, which excludes unlikely bonuses** unless earned. `cap_branches` and `dosunmu_final_states` now add the bonuses for apron thresholds and subtract them again for the tax calculation. Combined with the corrected 2023-CBA bracket table:

- Trade branch: **$8,717,225 (est)**, was $13,076,930
- Stretch branch: **~$16,974,544 (est)**
- **Trade-vs-stretch difference: about $8.26M**, against the "roughly $10.9M" previously in the piece
- Dosunmu final states: actual **$8,717,225** vs counterfactual **$7,030,250**, so the no-Dosunmu roster now **saves** about $1.69M in tax. Under the old wrong brackets the counterfactual looked $700k *more* expensive. **The direction of that comparison reversed.**

The corrected trade-branch tax reproduces the independent check to the dollar ($8,717,225 both ways), which is the first time the two computations have agreed on a tax figure.

### D51. R3 did not reconcile, and it found something worse than bonuses

Compared our team salary to Spotrac's published apron allocation for all 30 teams. **15 of 30 differ by more than $2,000, and the differences are not one cause.**

**Teams where ours is LOWER** (consistent with missing unlikely bonuses): 18 teams, $110,121,537 in total, median $3,417,722. Largest: MIL -$26,231,053, PHX -$19,383,010, MEM -$12,125,118, SAC -$9,334,251, WAS -$8,458,310, DEN -$8,386,921.

**Teams where ours is HIGHER**, which bonuses cannot explain: **CLE +$42,317,307**, LAC +$8,331,101, HOU +$5,073,420, DAL +$4,739,328, BOS +$2,715,526.

**CLE's gap is exactly James Harden's $42,317,307**, and our contract book has him on Cleveland. One player, one team, and the discrepancy matches to the dollar.

**Roster counts are impossible for eight teams.** MEM 21 standard contracts, LAC 18, MIL 18, NOP 18, and DAL, ATL, PHX, CHA at 17. The maximum is 15.

**Ruling: the all-30 layer is not publishable.** Apron tier flags differ on 8 teams between the two bases, including DEN moving into the second apron and CLE dropping from second apron to under the tax. Anything resting on the league-wide contract book, which is section 6's "seventeen of thirty changed apron tier", the West ranking, and every rival's title odds, is suspect until the book is repaired. Logged in `gaps_remaining.md` and flagged in the lock runbook. **Minnesota's own numbers are unaffected**, since the MIN book was verified player-for-player against the warehouse, Spotrac and Basketball-Reference in V1.

### D52. Aging changes no quotable verdict (U1)

Aged run is primary per the decision rule; un-aged preserved in `outputs/preaging/`.

| Move | Un-aged | Aged | |
|---|---|---|---|
| other_departures | ALL POSITIVE +1.12 | ALL POSITIVE +1.42 | |
| ball_in | ALL POSITIVE +0.67 | ALL POSITIVE +0.73 | survives |
| randle_out | MIXED +0.07 | ALL POSITIVE +0.25 | **FLIPPED** |
| kuminga_in | MIXED -0.06 | MIXED +0.03 | |
| reid_out | ALL NEGATIVE -0.26 | ALL NEGATIVE -0.36 | survives |
| ddv_injury | ALL NEGATIVE -0.35 | ALL NEGATIVE -0.27 | |
| depth | ALL NEGATIVE -0.36 | MIXED -0.32 | **FLIPPED** |
| dosunmu_retained | ALL NEGATIVE -0.40 | ALL NEGATIVE -0.42 | survives |

**No currently-quotable verdict is lost.** `ball_in`, `reid_out` and `dosunmu_retained` survive both the slot rule and the aging adjustment. `randle_out` flips again, in the opposite direction this time, which settles it: a verdict that moves under two independent modelling choices is not a finding, and it stays retired. `depth` was already sign-less.

MIN's title band rises across all four views, **1.57-3.81% to 2.33-4.83%**. That is mostly a level effect: the fitted curve is net-positive league-wide because of survivorship (players who decline leave and stop contributing deltas), so most teams gain. The band is what ships, and it moved.
