# Gaps remaining: Kuminga project

Items that failed or could not be completed, with the reason and what would unblock them.

## Item 7: 2026-27 futures and win totals. NOT COLLECTED. Blocked on terms of use.

**What happened.** Six candidate sources were checked before any odds table was fetched: VegasInsider, Covers, Action Network, DraftKings Sportsbook, CBS Sports and NBA.com. Every one of them explicitly forbids automated retrieval in its terms of use. VegasInsider's is representative: users "may not engage in unauthorized spidering, scraping, data mining or harvesting." No odds were retrieved, per the assignment's own stop condition.

**Worth recording:** robots.txt on VegasInsider, Covers, Action Network and DraftKings all permit crawling the relevant odds paths, while the human-readable terms forbid it. Where the two disagree the terms govern, so the machine-readable permission is not a licence.

**Consequence.** Item 10's market-comparison column cannot be produced tonight. The all-30 before/after table ships without it. The three historical seasons of preseason odds already on disk (2023-24, 2024-25, 2025-26) are unaffected and remain usable for model-vs-market backtesting.

**The manual path, for Bobby.** https://www.vegasinsider.com/nba/odds/futures/ carries both championship futures and season win totals for all 30 teams on one page. Opening it in a browser and pasting the table into `offseason/data/2026-27-preseason-odd.csv`, in the same three-column shape as the existing files, unblocks the comparison in about five minutes.

## Item 6: the league-wide future-pick ledger was NOT fully refreshed.

The Minnesota assets are enumerated and verified (10 rows, `kuminga/data/traded_picks_2026_offseason.csv`). A full refresh of all 609 rows was not possible: Spotrac and RealGM both return HTTP 403 to automated retrieval, as does Basketball-Reference's injury endpoint.

What exists instead: `kuminga/data/nba_draft_picks_future_2026_08_26.csv`, which is the June 6 ledger with the verified Minnesota delta appended and **37 MIN-involved rows flagged `stale_post_2026_trade`**. Any pick-value work that touches another team's 2028-2033 obligations should treat the unflagged rows as June vintage.

---

## Standing limitations of the run (not failures, but read them before quoting a number)

**The matchup overlay is off.** `simulate_league` can adjust series outcomes for archetype matchups, but the profiles it needs exist for 12 of 30 teams. Running it for 12 would break R2's identical-pipeline requirement, so every series resolves on net rating alone. The cost is specific and worth naming: archetype matchup effects are exactly where the postmortem's Q4 work found this roster most exposed, and San Antonio, the team that eliminated them and then reached the Finals, is the archetype it handles worst. This model cannot see that.

**The counterfactual fives cannot see position.** Per R5 they are talent rollups. The machinery minutes-weights impact estimates and would field five centres without complaint. "Beringer at the 4" means "Beringer's minutes-weighted impact instead of Kuminga's", not a claim about a two-centre frontcourt. Anything about actual fit is in the descriptive lineup evidence, which is on/off splits and not causal either.

**DARKO is integer-rounded.** The leaderboard on disk carries 13 distinct DPM values across 582 players. Kuminga's "-1" could be anywhere from -1.5 to -0.5. It is kept as the fourth view because an external check that disagrees is worth more than one that agrees, and because Dunks & Threes EPM and BBall Index LEBRON are both gated. It is not a peer of the other three.

**The out-year cap thresholds are a forward scale.** 2026-27 is league-set and verified. 2027-28 and 2028-29 are the constants file's 7%-per-year projection. Distances to the tax and apron lines in those seasons are directional.

**The out-year salary totals are not rosters.** Minnesota's 2027-28 and 2028-29 books count only players already under contract (nine and seven). They sit below the tax line because the roster is not filled, not because Minnesota escapes the tax. The stretch charge, by contrast, is fully known in both years.

**The baseline is healthy and the current field is not.** R6 applies no injuries to the baseline; R7 applies them to the current field. So the league-wide mean net delta is negative (-0.33 under consensus) by construction, and part of every injured team's decline is the injury rather than any transaction. Eight teams carry a long-term-out player and Minnesota is one of them. `outputs/coherence_checks.csv` quantifies it: injured teams average -0.85, healthy teams -0.14.

**The impact spine was not refit.** `player_value.csv` is the June three-season RAPM fit. Refitting it to include 2025-26 playoffs would have meant rebuilding the league-wide possession cache, which is a multi-hour job that would have consumed the night. Kuminga, LaMelo and every rotation player are already in it, so the run is not blocked, but the values are a June vintage on a 2023-26 window.

**The fit engine's synergy layer was not built,** per R5. It remains scaffolding. The Edwards-times-Kuminga interaction does not exist as a number in this project and nothing here should be read as one.

---

## Phase 3.5 status of the remaining gaps

**Item 7 / A3 forward half: STILL BLOCKED, but now one command from done.** `kuminga/scripts/market_vs_model_2026_27.py` is written, tested to its blocked path, and exits with instructions. The moment `offseason/data/2026-27-preseason-odd.csv` exists in the same three-column shape as the three historical files, running that script produces the all-30 model-vs-market table with flagged disagreements. Thresholds are stated rather than tuned: 4.0 wins and 2.5pp on title odds, each roughly calibrated to the model's own measured out-of-sample error, and a disagreement only counts when the market sits OUTSIDE the whole four-fork band.

**A3 backtest half: DONE.** Three seasons run. What could not be done, and why, is worth keeping visible: a full historical replay of this pipeline is impossible because the warehouse holds only one season of rosters (`nba_team_rosters` is 2025-26 only) and the impact spine is a pooled 2023-26 fit, so using it for 2023-24 would leak three years of future information. What was testable is the calibration spine, and it was.

**New gap, from C2.** The Shapley move set has no "replacement guard" for the Dosunmu counterfactual, so letting him walk credits Minnesota with minutes nobody actually plays. That is why he grades ALL NEGATIVE. C3 fixes exactly this problem for the power-forward slot; the same slot treatment has not been applied to the guard rotation. Doing so would need a slot pool per position and is a half-day of work, not a rerun.

**New gap, from C3.** The slot finding is conditional on Terrence Shannon Jr. being the man who fills the 4. Minnesota still has to reach the 14-man minimum, and if the body they add is a forward, the alternative improves and Kuminga's margin narrows. Re-run `slot_analysis.py` after any signing.

**Standing, unchanged.** The matchup overlay is off and its measured cost (0.11pp) is computed on profiles that exist for 12 of 30 teams, so it is a floor rather than an estimate. DARKO remains integer-rounded. The 2027-28 and 2028-29 thresholds remain a forward scale. The impact spine was not refit.

## 12. Early Bird rights and an exercised player option (CONFIRM, U4)

If Kuminga picks up his 2027-28 player option, Minnesota reaches the 2028 offseason with two consecutive seasons of his service and, on the plain reading, **Early Bird rights** (greater of 175% of prior salary, $11,142,600, or 105% of the league-average salary; up to four years; the new deal must run at least two years and its second season cannot be an option).

**What is not confirmed:** the sources consulted state Early Bird requires "two consecutive seasons with one team without changing teams via free agency" but do **not explicitly address whether a season played on an exercised player option counts** toward that total. It plainly should, because exercising an option continues the same contract and involves no free agency, but that inference is not sourced.

**To close:** find the CBA definition of "Early Qualifying Veteran Free Agent" (Article I definitions) and confirm the service-counting language. Section 5 currently states the Early Bird branch with this caveat attached; if it turns out an option year does NOT count, the whole opt-in branch collapses back to Non-Bird and section 5 must be rewritten.

Status as of 2026-08-27: open. Two sources consulted (Hoops Rumors Early Bird glossary, CBA Guide).

## 13. CLOSED 2026-09-03: the league-wide cap quarantine is lifted

**Status: both gates pass, 30 of 30. The quarantine raised on 2026-08-27 is lifted.** `outputs/roster_v3_gates.json`, run `roster_v3_gates`.

**FIRST, THE CORRECTION, because the diagnosis recorded here was wrong.** This item previously said "players are sitting on different teams in the two books" and cited James Harden on Cleveland and Giannis Antetokounmpo on Miami as proof. **That was wrong.** Spotrac's own pages put Harden on Cleveland and Giannis on Miami, exactly where our book had them. The team assignments were right the whole time.

**The real causes were two membership rules we had never modelled.**

- **Pending transactions.** Spotrac lists reported-but-unofficial moves separately and excludes them from team totals. Our book folded them in at full value. Cleveland's $42,317,307 gap was not Harden being on the wrong team, it was Harden being counted at his full salary in our book while Spotrac carried him as a $29,938,272 pending row and excluded him from the total.
- **Dead money.** Waived players still count against the team that waived them, and our book largely did not carry them. Phoenix's entire $19,383,010 gap was Bradley Beal's waived salary.

Both cut in opposite directions, which is exactly why the league aggregate was within 0.63% while individual teams were tens of millions apart. **The 4.9x absolute-to-net ratio told me the errors cancelled; I read that as misassignment when it was a systematic rule omission in both directions.** The roster-count anomaly was the same story: rows for waived and pending players were being counted as standard contracts.

**What actually closed it.** A full re-scrape of all 30 Spotrac team cap pages (2026-09-03), parsed into `roster_snapshot_2026_27_v3.csv` with dead money, pending transactions and per-player unlikely bonuses carried as distinct statuses for the first time.

| gate | result |
|---|---|
| A, parse faithful vs Spotrac's own header count | **30 of 30** |
| A, standard contracts within the offseason limit of 20 | **30 of 30** |
| B1, active roster dollars | **30 of 30** to the dollar |
| B2, dead money dollars | **30 of 30** to the dollar |
| B, apron per team | **30 of 30** |

Sum of absolute per-team differences: **$183,047,636 to $0.**

**Gate A had to be re-specified, and that is a finding in itself.** The original 13-to-15 range failed seven teams, six of them on Spotrac's own published counts, because **13-to-15 is a regular-season rule**. In the offseason a team may carry up to 20 and must cut down before opening night. A gate that rejects the reference source's own data is mis-specified. See D56.

**WHAT REPLACES THE QUARANTINE, because two real limitations remain.**

- **Single-source risk, OPEN.** The roster book is now sourced only to Spotrac, and B1 and B2 compare our parse against Spotrac's own totals, so they are **parse-fidelity tests, not independent-truth tests**. v1 came from Basketball-Reference. A cross-publisher check has not been run and should be before any league-wide claim carries real weight.
- **Unlikely bonuses on four teams.** Spotrac renders some unlikely bonuses as "-" per player while including them in its own total. WAS is short $5,458,310, DEN $1,091,658, DAL and TOR $264,305 each. Active roster and dead money match to the dollar on all four, so membership is right and only the bonus column is incomplete; the team total is used as the authority. **DAL and TOR being short by the identical figure is unexplained.** **Denver's apron TIER depends on those bonuses** (first apron on the per-player column, second apron on the total), so any claim about Denver's tier is still not quotable.

**Minnesota is unaffected by both.** Its per-player bonus column is complete ($1,750,000 against $1,750,000 implied) and its apron reconciles to all three of Spotrac's separately-computed figures at zero difference.


## 14. Overnight run of 2026-09-09/10: what did not finish, and why

Recorded per the autonomy rule: failures go here and the run moves on.

**BLOCKED ON AN EXTERNAL SOURCE**

- ~~**H1 champion feature columns.**~~ **CLOSED 2026-09-17 (R6, D83)** for the three clean seasons, via Basketball-Reference snapshots frozen in `data/bref/`; the pre-playoff odds and odds-history columns stay open for a pasted source. Original entry: Net-rating ranks, post-All-Star ranks, seeds, playoff net rating versus regular season, best-player metric, top-8 age, continuity (returning minutes share), top-8 playoff health, ORtg and DRtg ranks. Basketball-Reference returns **403 to direct requests**, and the `r.jina.ai` proxy is **rate-limited on that entire domain until 2026-09-10 04:14 GMT** ("Anonymous access blocked ... DDoS attack suspected"). The warehouse cannot substitute: `nba_team_advanced_stats` is GAME level and has no season key, so every one of those columns needs a season aggregation that does not exist yet. **Not guessed.** Retry the B-Ref preseason-odds and team-summary pages after the block lifts.
- **Champions table before 2023-24.** The project holds clean 30-team preseason odds for exactly three seasons. Extending back needs `basketball-reference.com/leagues/NBA_{year}_preseason_odds.html` (published, citable, courtesy sportsoddshistory.com) or a paste. **sportsbettingdime.com was found and rejected**: its past-seasons table names San Antonio as the 2026 champion when New York won 4-1. A source that misstates a champion is not usable for its odds either.

**BLOCKED ON MISSING WAREHOUSE COLUMNS**

- ~~**Minutes-weighted size** as an M1 style feature.~~ **CLOSED 2026-09-10, and the gap was my error, not the warehouse's.** I queried for `height_inches`; the column is **`player_height_inches`**, and it is fully populated (572, 569 and 582 non-null rows across the three seasons). Size is now in the feature set, weighted by games played because the table carries `gp` and no minutes column. **Re-tested: the held-out gain does NOT change sign.** With size and the two originally-planned interactions restored (rim against size, offensive rebounding against size), held-out MAE gains are **-0.0151 on 2025-26 games and -0.0265 on the postseasons**, against -0.0085 and -0.0395 without it. The overlay stays off. **The lesson is about the gap, not the feature: a null result from a query I wrote is evidence about my query first and the data second.**
- ~~**N2 opponent distribution by seed.**~~ **CLOSED** (N2 path: modal seed, first-round opponent mix, title equity conditional on reaching the second round, all on the sheet). Original entry: `run_sim` does not persist the simulator's `matchups` block, so the expected first-round and second-round opponent distribution cannot be read off the existing run. The seed distribution itself IS available and is in the skeleton. Fix is one line in `run_sim` plus a re-run.

**NOT REACHED at the time, ALL NOW DONE (status 2026-09-17)**

- ~~**M3** opponent cards~~ done. ~~**M4** lineup study~~ done, post-fix numbers (D84). ~~**M5** usage accounting~~ done, in sections 3 and 5.
- ~~**N3** playoff translation~~ done. ~~**N4** versatility index~~ done. ~~**N5** fragility~~ done. ~~**N7** clutch~~ done; **the late-clock split is WITHHELD** (reconstruction 79.9% against an 80% bar set in advance).
- ~~**H3** separation, **H4** case files, **H5** Minnesota on the champion sheet~~ done (D83, and the Knicks file in section 2).
- ~~**N8** full watch list~~ done, with a December game-30 checkpoint for Boston added in R4.

**RUN BUT NOT YET FOLDED IN**

- ~~**The 200k-sim run.**~~ **DONE**: every f-curve view is at 200,000 simulations and the floors are computed from it. Original entry: Not launched. `build_fcurve` costs roughly 28 minutes at 20,000 sims per fork per seed, so 200,000 is a four-to-five hour job that would have consumed the whole night and blocked everything above it. **Judgement call: the aged pipeline was run first because it is a quotability gate, and the 200k is a precision improvement to a floor that is already not the binding constraint on most verdicts.** Logged in decisions.md.

**A STANDING RISK, not a gap**

- The roster book remains **single-sourced to Spotrac**. The dollar gates are parse-fidelity tests, not independent-truth tests. Unchanged from D56.


## 15. After the restructure and consistency pass of 2026-09-17: what is still open

**WITHHELD, by rule**

- **Late-clock split.** Play-by-play has no shot clock; the reconstruction read within two seconds of zero at recorded violations 79.9% of the time against a bar of 80% fixed in advance. One methods sentence in section 6. Clutch ships.

**OPEN, awaiting a source**

- **Pre-playoff odds and every odds-history column before the clean seasons** (H1). Left blank in `h1_champion_sheet.csv` for a pasted source; B-Ref's preseason-odds pages are the citable route.

**FLAGGED, and what is now fixed**

- ~~**The shared stint pipeline's point columns.**~~ **FIXED AT THE SOURCE 2026-09-18 (D88).** `postmortem/lib/lineup_aggregation.py` now rebuilds points from made shots, stint points reconcile to the box score exactly (48 of 48 team-games), and the 41 postmortem figures that rode on the old basis are recomputed with before and after logged. Five playoff figures change sign. **What remains** is the possession-grain version of the same defect: possession points are credited to the possession's offensive team, which is wrong for about 3.9% of points and reaches postmortem's RAPM, Q1's halfcourt/transition/clutch splits, and the fit engine's possession builder. Two RAPM claims in a published article draft are therefore unverified. Re-fitting RAPM is a separate job.
- ~~**The attribution allocator is a choice the shipping list depends on.**~~ **CLOSED 2026-09-18 (D87).** The shipping rule is now four cells, two aging bases by two allocators, and all seven verdicts hold in every cell. `depth` ships under team-rank alone and therefore does not ship, which is the case that justified the test.
- ~~**Duplicate run ID.**~~ **CLOSED 2026-09-18 (D86).** Run ids are now reserved with an atomic marker file before a run starts, so a collision bumps the timestamp instead of sharing an id. The six ids that already collided (two `noise_floor`, five `build_fcurve` fork groups) are marked, the `noise_floor` pair records which run supersedes it per basis, and `reconcile_figures.py` gate C3 fails on any unmarked duplicate or any figure citing one.

**A STANDING RISK, unchanged**

- The roster book is single-sourced to Spotrac (D56).

**NEW, opened 2026-09-18 by D88**

- ~~**The possession grain.**~~ **CLOSED 2026-09-19 (D89).** The defect was in `lib/lineups.derive_possessions`, not in `lib/pbp.reconstruct_possessions` (that one retro-credits and-ones correctly and was never exposed, so Q1's halfcourt, transition and clutch splits were not affected). Points now go to the team that scored them; per-team possession points reconcile to `nba_games.pts` on 96 of 96 sampled team-games against 14 before. Both possession caches were rebuilt, RAPM was refit on both bases with the legacy-points fit reproducing the published numbers as a gate, consensus was re-derived from frozen Basketball-Reference values, and the two RAPM claims in the article draft were re-tested and both hold. A second correction rode along: an and-one free throw no longer ends a possession, so the grid lost 2.05% of its possessions, all `made_ft`.
- **The fit engine's pinned fork.** `counterfactual-fit-engine/src/stints/stint_builder.py` is a deliberate hash-pinned copy of the fixed library and still carries the defect. Fixing it breaks the pin by design, so it is Bobby's call. Downstream: the tripwire PAIR-DRTG markers and the jaden_calibration JD-COVER report, both bannered, both on a 15,669-game panel that needs a scheduled rebuild.

## 16. The Bet additions (C1 to C5, 2026-09-22): what is open

- **C1 preseason odds.** The two columns (`preseason_title_odds`, `preseason_odds_source`) are empty in `outputs/c1_champions.csv` and print as "open"; they fill from a pasted source with a URL per row, and the paragraphs do not use them.
- **C1 seed tie-breaks.** Seeds are the Basketball-Reference conference finish; the warehouse standings rank breaks ties on point differential and the script notes any disagreement in the run log (none fatal). Net ratings are NBA.com per-game figures weighted by possessions; the Basketball-Reference season figure rides in the CSV as a cross-check, not as the printed number.
- **C2 extension length.** The clause that limits Edwards's standard extension to two new seasons (the reported "two years, about $122 million") was not located in the 2023 CBA text by search; that figure rests on two reports. Everything else in the clock is quoted from the CBA by page.
- **C3 base rate is thin.** The strict cohort is 20 player-seasons (16 players) and 6 with the healthy-prior-season condition; two looser variants (85 and 41) are printed as sensitivity. Any sentence built on the strict cohort must carry its n.
- **C3 availability is a fraction of every game.** The pipeline's rs_avail convention scales minutes in every game rather than removing whole games; identical in expectation for the linear rollup, not for the allocator's ceilings. The doc says so.
- **C4 dollars with one source.** Lyles's exact salary (the book's $2,449,421 minimum; reports say minimum with a $1.5M partial guarantee), the cash in the Green trade ($4M in the Hoops Rumors check-in only), the two-way holdovers' terms and Ingles's NBL deal are not on two fetched pages. The Athletic's trade grade (D+) is carried secondhand and marked. Three player pages in the ledger were reached by the slug rule (flagged `slug_guessed` in the CSV) rather than a known id; each page's title was checked against the name.
- **C5 gate scope.** `gate_prose.py` matches digits exactly, so a rounded figure passes only when a rounded key is on the sheet (salaries carry both); the five league constants it allows (82, 48, 30, 100, 7) are listed in the script and should stay short. The reconcile allowlist gained `Parts? \d` for series labels.
- **Basketball-Reference access.** Direct fetches with a browser User-Agent at one request per four seconds work and are cached with hashes (`kuminga/lib/bref.py`, `data/bref/manifest.json`); the r.jina.ai proxy was blocked for the domain on 2026-09-22 and is not used. prosportstransactions, Spotrac injuries, RotoWire and RealGM refuse scripted fetches; injury causes and signing terms were sourced from ESPN, NBA.com, CBS, Hoops Rumors and the official scorer's reports instead.
