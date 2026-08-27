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

