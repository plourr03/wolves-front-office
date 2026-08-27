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
