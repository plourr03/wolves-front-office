# Player Bio and Stints Backfill: Engineering Brief

## Why we need this

The wolves-front-office analysis project needs trade-aware roster history, plus player biographical data, for several upcoming analyses (Q0B trajectory and contention windows, Q0C historical cohort, Q4 archetype work, and many supporting queries throughout the project).

We're not scraping Basketball Reference. Two NBA Stats API endpoints, plus a structure derived from data already in the warehouse, give us everything we'd want from BBR and more (jersey number, birthdate, player slug, position).

## What we need: three artifacts

Names, schemas, indexing, and refresh scheduling are at your discretion. Coordinate with the patterns already used in the `nba` schema.

### Artifact 1: A per-player biographical reference

One row per distinct player who has appeared in `nba.nba_player_stats`.

**Source endpoint:** `commonplayerinfo` (one call per player_id).

**Information we depend on from the response:**

- Birthdate. This is the single most important field. With it we can compute age at any historical date, which is what the age-curve and trajectory analyses need.
- Position
- Height and weight
- Draft year, draft round, draft number
- Career start year and career end (or current) year
- School and country
- Jersey number
- A stable display name and a slug-style identifier

The endpoint also returns operational flags (D-League, NBA, Greatest 75, etc.) and a small headline-stats result set. Persist or drop at your discretion; none are load-bearing for our analyses.

Volume: roughly 2,860 calls for the existing warehouse, one-time, then incremental as new players appear (rookies and new signings each season).

### Artifact 2: A per-player-season biographical snapshot

One row per (player, season). Captures season-time facts that legitimately change year over year and aren't best modeled as immutable bio.

**Source endpoint:** `leaguedashplayerbiostats` (one call per season per season-type, returns every active player for that season).

**Information we depend on from the response:**

- Season-time team affiliation
- Season-time age
- Season-time height and weight
- Season aggregate counters (games played at minimum)

The endpoint also returns season-aggregate stats (PTS, REB, AST, NET_RATING, USG_PCT, TS_PCT, etc.) that are redundant with our existing box-score data. Whether to persist them is your call; cheap to keep alongside if it simplifies downstream queries.

Behavior to verify before committing the schema: for a mid-season-traded player, this endpoint returns a single row at the season grain (most likely showing their season-ending team). Run one probe against a known mid-season trade to confirm exactly how it represents that player, then design accordingly. The within-season trade detail is handled by Artifact 3 anyway, so this is a finishing decision rather than a blocker.

Volume: roughly 60 calls for the full historical archive (30 seasons x 2 season types), then two calls per refresh going forward.

### Artifact 3: A trade-aware stint structure

This is the most important deliverable of the three because it unblocks every "who was on what team when" question across the project.

**Source:** purely derived from `nba.nba_player_stats` joined to `nba.nba_games` for dates. No API calls.

**Semantics:**

A "stint" is a contiguous span during which a player appeared in box scores for a specific team within a specific season. The identity is (player_id, team_id, season_id). For each stint we want:

- The first game date the player appeared in box scores for that team that season
- The last game date the player appeared in box scores for that team that season
- Total games played during the stint
- Total minutes played during the stint

A player who plays the entire season for one team has one stint that season. A player traded mid-season has two stints, with a natural boundary on the trade date. A player on multiple 10-day deals or two-way conversions naturally produces multiple stints as well.

This structure enables queries like:

- "Who was on team X on date D" (stints where stint_start_date <= D <= stint_end_date and team_id = X)
- "Who was on team X's playoff roster" (stints active on the team's first playoff game date)
- "Was this player traded mid-season this year" (multiple stints per player per season)
- "When did Player Y join Team X" (stint_start_date for that pairing)

Materialize as a table or view at your discretion. A materialized table is likely worth it given how many downstream queries will lean on it; refresh it as part of the daily run.

## Acceptance criteria

- Every distinct player_id in `nba.nba_player_stats` is represented in the bio artifact
- Every (player, season) pair where the player appeared in at least one game is represented in the season-snapshot artifact
- The stint artifact correctly returns multiple rows for known mid-season-traded players. Pick one recent deadline trade to verify against, e.g., a 2024-25 or 2025-26 deadline move.
- All three artifacts integrate cleanly into the existing daily refresh pipeline

## What not to do

- Don't scrape Basketball Reference for this. The two NBA Stats API endpoints together cover everything we'd want from BBR and add fields BBR doesn't have (jersey, birthdate, slug).
- Don't substitute `playercareerstats` or `playerprofilev2` for this work; those are useful endpoints for other analyses but are the wrong grain for what we need here.
- Don't treat the season-snapshot as a substitute for stints; the season grain masks within-season team changes.

## Open design decisions

These are all yours. The brief intentionally avoids prescribing them.

- Naming conventions for the three artifacts
- Whether to separate regular-season and playoff rows in the season snapshot or merge them
- Indexing strategy (the stint table will see frequent date-range and team filters)
- Whether to deduplicate or keep redundant fields between the bio artifact and the season snapshot
- Refresh cadence: one-time backfill plus daily incremental, or a different pattern
- Whether the stint structure is a materialized table or a view
