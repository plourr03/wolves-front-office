# Phase 2, Part 1: Reference Class Extraction

Tripwire backtest, Phase 2. Produced 2026-07-17. Data: `data/refclass_{A,B,C}.parquet`, `data/arrivals_foundation.parquet`. Scripts: `build_reference_class.py` (A + foundation), `build_reference_class_bc.py` (B, C).

This part builds the three scenario classes and reconciles them against the seed tables. Labels (outcomes) follow in Part 2; the stint-dependent labels (YA1 pair net rating, YC1 anchor-off rebounding) wait on the stint panel, the box-score labels do not.

## Foundation: arrivals from game-level data

`nba_player_season_bio` carries one row per player-season, so it cannot see midseason trades. Arrivals are therefore built from game-level `nba_player_stats`: per player, teams are ordered by first-game date, and an arrival is either a midseason team change (a new team after the first this season) or an offseason change (this season's first team differs from the most recent prior season with games). Every join keys on `nba_player_id`.

One bug worth recording, because it mattered: an earlier version compared only to season `ss-1`, which missed players who sat out a full season before arriving. **John Wall (zero games 2019-20 before arriving at Houston) and Ben Simmons (zero games 2021-22) were invisible until the detector was fixed to look back to the most recent season with games.** Availability cases are exactly the players most likely to have a gap year, so this bug hit the scenario it could least afford to.

Foundation: 3,481 arrival events, 2010-11 forward.

## Scenario A: co-star integration

An arriving guard, prior-season usage >= 0.28 (corrected from the spec's 28.0 scale bug) and >= 1200 prior-season minutes (derived from `minutes_float`), joining a team with a qualifying incumbent. Guard via career-static `nba_player_bio.position`.

Class sizes under the mandated sensitivities:

| Definition | Cases |
|---|---|
| **Strict** (usg >= 0.28, incumbent All-NBA in prior 2 or All-Star game-starter) | **17** |
| Loosened usage (usg >= 0.25, incumbent strict) | 58 |
| Widened incumbent (usg >= 0.28, incumbent incl. current-season All-Star) | 26 |

17 strict is well above N_GATE (8). The strict class (9 offseason, 8 midseason) is a clean list of real co-star arrivals: the seed cases plus discovered ones (Arenas to ORL 2010, Wade and Thomas to CLE 2017, DeRozan to SAS 2018, Schröder to OKC 2018, D'Angelo Russell twice in 2019, Westbrook to HOU 2019, Cam Thomas and Harden to their 2025-26 teams).

### Seed reconciliation (all 12 core seeds accounted for)

| Seed | Result |
|---|---|
| Lillard-MIL, Irving-DAL, Harden-BKN, Harden-PHI, Westbrook-LAL, Beal-PHX, Doncic-LAL | **IN strict** (7) |
| Harden-LAC | OUT strict (usg 0.247 < 0.28 AND incumbent widened-only); enters under loosened usage + widened incumbent |
| Paul-PHX | OUT strict (usg 0.228 AND incumbent widened-only); the CP3-to-Phoenix case the spec named |
| Mitchell-CLE | OUT strict (incumbent Garland is All-Star-reserve only); enters under widened incumbent |
| Fox-SAS | OUT strict (incumbent Wembanyama, sophomore, no prior-2 honor); enters under widened incumbent |
| Murray-NOP | OUT all (usg 0.259 < 0.28 AND incumbent Zion has no qualifying honor; see honors caveat) |

Every seed either appears or has a logged reason. The out-cases are precisely the two sensitivities the spec demands be reported: the **usage filter** (Harden-LAC 0.247, Paul 0.228, Beal was 0.288 so in, Murray 0.259) and the **incumbent filter** (Garland/Booker/George as All-Star-only, Wembanyama as sophomore, Zion as injured voted-starter). Both are carried into Phase 3 as strict-vs-loosened sensitivity runs (carry-forward #2).

## Scenario B: availability pacing

An arriving player, any position, who missed >= 30% of games in >= 2 of the four prior seasons (denominator = that season's scheduled games, so lockout/COVID years count correctly). Added relevance filter: the player was a genuine rotation regular (>= 24 mpg in >= 1 of the four prior seasons with >= 20 games), which drops journeyman waiver-churn from the availability signal and keeps the stars/starters the scenario is about.

Class size: **388** (700 fell away when the relevance filter replaced an earlier minutes-only filter that let in end-of-bench veterans like Scalabrine and Kwame Brown).

### Seed reconciliation

| Seed | Result |
|---|---|
| Wall-HOU, Irving-DAL, Porzingis-BOS, Lonzo-CHI, Middleton-WAS | **IN** (5) |
| Simmons-BKN | OUT: his availability collapse is post-arrival. At his arrival his prior four seasons were 81/79/57/58 games, only one (barely) near the 30% line. The 2-of-4 rule is backward-looking and cannot see a breakdown that hasn't happened yet. |
| LaVine-SAC | OUT: one catastrophic season (25 games, 2023-24) but only 1 of 4, not 2. |
| Leonard-LAC | OUT: one load-management season (9 games, 2017-18); his 2018-19 was managed to 60 games (0.27 missed, just under the 0.30 line), so 1 of 4. |
| George-LAC | OUT: durable before 2019 (0 of 4). Paired with Leonard in the trade but not himself an availability case. |

5 of 9 seeds fit the strict definition. The 4 misses are all the same shape: the 2-of-4-prior rule is stricter than the eye test and misses players whose history is one catastrophic season (LaVine, Leonard) or a breakdown concentrated at/after arrival (Simmons). This is a real property of the definition and is reported, not patched. Phase 3 notes it when interpreting AVAIL-PACE, whose whole point is that pace-in-season can catch what prior-season history misses.

## Scenario C: frontcourt succession

A team whose leading rim-minutes anchor (max-minute center, >= 1500 minutes) departed, with the hole not filled by an acquired veteran big. Two departure modes: offseason (anchor plays < 500 minutes for the team next season) and midseason (anchor traded away during the season). Class size: **116**.

### Seed reconciliation

| Seed | Result |
|---|---|
| UTA post-Gobert 22-23 | **IN** (offseason; note replacement Kelly Olynyk acquired, flagged) |
| MIL post-Lopez 25-26 | **IN** (offseason; replacement Myles Turner flagged) |
| HOU post-Capela 19-20, BKN post-Allen 20-21, LAL post-Davis 24-25 | **IN, curated**: midseason departures the auto-detector cannot reach, because the departed anchor either did not play for his new team that season (Capela, injured post-trade) or the season-total anchor became the replacement (Allen, then Jordan). Added as curated entries with this logged reason. |

All 5 seeds accounted for. The `replacement_acquired` flag separates clean succession holes (28 offseason cases with no veteran replacement) from patched ones, which matters for YC2 (the deadline-acquisition comparison). The 2026-27 Wolves instance (Naz Reid departing behind Gobert) is the target this scenario is built to inform.

## What is deferred to Part 2

- **Box-score labels** (computable now, no panel): YB1 games played, YB2 playoff availability, YB3 availability vs prior-three-season plan; YA3 breakup flags (hand-curated); YA2 with the SRS proxy (G3).
- **Stint-dependent labels** (wait on the panel): YA1 pair shared-floor net rating over games 41-82; YC1 anchor-off defensive rebounding and rim FG% over games 26-82; YC2 the before/after deltas.
- **Early features**: the first-N-game versions of each candidate metric, which feed Phase 3.

## Definitional choices logged for the record

These are the places where the spec left a definition open and Phase 2 made a documented call, each reversible:
1. Position is career-static (`nba_player_bio`); `pos_group='G'` = {Guard, Guard-Forward, Forward-Guard}.
2. Scenario B added a >= 24 mpg relevance filter the spec did not specify, to keep the class meaningful.
3. Scenario C anchor requires >= 1500 minutes; replacement veteran requires >= 1500 minutes and prior-roster absence.
4. The incumbent All-Star-starter criterion uses game-starter status, with the documented 2018+ format caveats from Phase 0.5.
