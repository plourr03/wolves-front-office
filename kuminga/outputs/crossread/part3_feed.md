<!-- cross-read export of kuminga\docs\series\part3_short.md | run export_crossread_20260929T183814Z | commit 749ed93a | 2026-09-29T18:38:14Z | visuals replaced by [visual: id]; N9 documents marked PENDING -->

# The Bet, Part 3: feed

## Short version

# The Bet, Part 3: How champions actually happen (feed version)

I rebuilt the last eleven champions from the box scores and the transaction logs: who played the playoff minutes, how they got there, how many had been there the year before, and what changed between October and June.

Ten of the eleven were top five in regular-season net rating; the one that wasn't, the 2023 Nuggets, was 6th. Six were No. 1 seeds. The second half told you much less: a champion's post-All-Star rank was as bad as 18th. On average the top eight missed 101 regular-season games and 6.2 playoff games, which is the whole list in two numbers: champions get hurt in the winter and are healthy in the spring. And every one of them tightened, the top five's share of the minutes going from 56% to 70%.

The Knicks are the clearest case. The market had them fourth at 8.27% in October; our model had them at 4.63%. They were steady all year, 5th in net rating, the No. 3 seed. Then they went 16-3 at +14.89 a game, the only one of sixteen playoff teams whose margin improved, with a top five that missed 46 games in the regular season and 2 in the playoffs. Same eight guys, healthy, playing more.

Across the eleven, the favorite won four times and the champion came from the market's top five ten times, priced between 4.01% and 57.65%. Against the 48 top-five teams that didn't win, nothing separates in October: no feature is exclusive to champions. By April they lean: a median 4th in net rating against the also-rans' 7th, and a median 1 seed against a 4. Style separated nothing on the three seasons that have it. Denver 2023, ninth at 4.01%, is the closest analog by price and by build; the Knicks are the closest in time.

Minnesota is priced at 3.16%. Whether it has eight guys like that is Part 4.

## Pull-quotes

# The Bet, Part 3: pull-quotes

1. "Champions get hurt in the winter and are healthy in the spring." (`c1_mean_missed_rs`, `c1_mean_missed_po`)

2. "Of the sixteen teams in the field, they were the only one whose margin improved from the regular season." (`nyk_n_positive_lift`, `nyk_po_teams`, `nyk_po`, `nyk_rs`)

3. "The same eight guys, healthy, playing more of the minutes, better than they were in February." (`c1_2025_26_returning`, `c1_2025_26_returning_share`, `nyk_top5_share_rs`, `nyk_top5_share_po`)

4. "Being good on both ends, and having been together, is what separated the champions from the other favorites." (`h3_n_sep`, `h3_n_feat`, `h3_n_non`)

5. "The market is pricing a team that might do that. The model is pricing a team that probably won't. Neither of them can see the thing the list keeps pointing at." (`mkt_min`, `title`, `c1_top5_net_n`)

## Slide

**Slide copy**

- Dateline: THE BET, PART 3 · 09.24.26
- Headline: HOW CHAMPIONS ACTUALLY HAPPEN.
- Subhead: Eleven champions, 2015-16 to last June,
- Subhead: rebuilt from the box scores.
- Tile: 10 of 11, TOP FIVE IN NET RATING. The exception, Denver 2023, was 6th. (sheet key `c1_top5_net_n`)
- Tile: 6 of 11, WERE THE NO. 1 SEED. Three won from the 3 seed. (sheet key `c1_seed_1_n`)
- Tile: 101, TOP-8 GAMES MISSED, REG SEASON. Average champion. In the playoffs: 6.2. (sheet key `c1_mean_missed_rs`)
- Tile: 70%, TOP-5 MINUTES SHARE, PLAYOFFS. Up from 56% in the regular season. (sheet key `c1_mean_top5_po`)
- THE CATCH: Champions get hurt in the winter and are healthy in the spring. Style never separated them.
- THE KNICKS: 8.27% in October  ·  16-3 at +14.89 in the playoffs  ·  top five missed 46, then 2
- Footer: Warehouse box scores, Basketball-Reference.
- Footer: Every champion cross-checked. Part 3 of 4.
