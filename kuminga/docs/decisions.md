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

