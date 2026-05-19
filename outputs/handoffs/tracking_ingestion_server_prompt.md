# Server agent prompt: tracking data ingestion

Paste the body below into the agent session running in `nba-warehouse`. Before pasting, make sure the spec amendment in `tracking_ingestion_spec_amendment.md` has been applied to `specs/data_pipeline_spec.md` so the agent can reference Section 16.

---

You are working in the `nba-warehouse` repo. Your task is to build tracking-data ingestion and run it in two phases: the current season first, then a historical backfill.

## What to read first

1. `specs/data_pipeline_spec.md` end to end, with particular attention to:
   - Section 12 (Adding a new endpoint), especially the three traps and the verification template.
   - Section 16 (Tracking data ingestion). This is the spec for what you are about to build. Endpoints, table schemas, sequencing, and verification queries all live there.
2. `scr/data_collection/nba_session.py` for the Akamai bypass. Every script you write must `import nba_session` and call `nba_session.patch_nba_api()` before any `nba_api` import is used.
3. `scr/data_collection/daily_refresh_complete.py` for the existing patterns: phase structure, idempotent upserts, jittered rate limiting, circuit breakers, run-log writes.
4. `docs/database_inventory.md` to confirm what already exists.

If after reading you find anything in Section 16 ambiguous or in conflict with how the existing pipeline works, stop and surface the conflict before building. Do not improvise schema decisions that diverge from the spec.

## What to build

A new script `scr/data_collection/tracking_refresh.py`. It must:

- Be invokable standalone with `python -X utf8 scr\data_collection\tracking_refresh.py`.
- Support a `--season` argument accepting either a single season label like `2025-26` or the keyword `all` for the full backfill.
- Support a `--phase` argument accepting `synergy`, `pt-stats`, `boxscore-track`, `hustle`, or `all` so phases can be run in isolation for verification.
- Create the new tables described in Section 16 if they do not exist, using `CREATE TABLE IF NOT EXISTS`. The full list is:
  - `nba_synergy_team_play_types`
  - `nba_synergy_player_play_types`
  - `nba_player_tracking_season`
  - `nba_team_tracking_season`  (team-level analog; same shape, primary key `(team_id, season_year, season_type, measure_type)`)
  - `nba_player_tracking_game`
  - `nba_team_tracking_game`
  - `nba_player_hustle_stats_season`  (only if you implement the optional hustle phase)
  - `nba_team_hustle_stats_season`    (same)
  - Pick one schema choice for `nba_player_tracking_season` and `nba_team_tracking_season` (wide table vs narrow per measure type); document the choice with an inline comment in Section 16 of the spec and stick with it. Apply the same choice to both.
- Use `INSERT ... ON CONFLICT DO UPDATE` on the documented primary keys. Reruns must produce zero new rows.
- Write a per-phase row summary to a new `tracking_refresh_run_log` table (or extend `daily_refresh_run_log` with a `script_name` column; pick one and document).
- Apply the same circuit breaker pattern as Phase 4 of `daily_refresh_complete.py`: bail after 5 consecutive endpoint timeouts, log the count, and exit non-zero so the wrapping job can be retried later.
- Print progress every N calls so a watching human (or `tail -f`) can see it is alive.

Do not change the existing daily refresh script's behavior in this task. The current-season incremental hookup into `daily_refresh_complete.py` is a follow-up; build the standalone script first.

## How to run it: the two-phase sequence

### Phase A: 2025-26 current season (run first)

Execute, in order:

1. `python -X utf8 scr\data_collection\tracking_refresh.py --season 2025-26 --phase synergy`
   - For 11 play types (`Isolation, PRBallHandler, PRRollman, PostUp, Spotup, Handoff, OffScreen, Cut, Transition, Putbacks, Misc`), both type groupings (`offensive, defensive`), both granularities (`team, player`). 44 calls per season type, ~10 seconds total.
2. `python -X utf8 scr\data_collection\tracking_refresh.py --season 2025-26 --phase pt-stats`
   - For each of the **11 measure types**, run **twice**: once with `player_or_team='Player'` and once with `'Team'`. The 11 measure types are:
     `Possessions`, `SpeedDistance`, `CatchShoot`, `PullUpShot`, `Drives`, `Defense`, `Passing`, `ElbowTouch`, `PostTouch`, `PaintTouch`, `Rebounding`.
   - Do NOT call `Efficiency` (overlaps with advanced stats already in the warehouse).
   - Total: 22 calls per season type. 5-15 minutes per season type.
3. `python -X utf8 scr\data_collection\tracking_refresh.py --season 2025-26 --phase boxscore-track`
   - `BoxScorePlayerTrackV3` per game for every 2025-26 game in `nba_games`. Returns both player and team data sets in one call. ~1300 calls for RS plus current playoffs, 15-25 minutes.
4. *(optional but recommended)* `python -X utf8 scr\data_collection\tracking_refresh.py --season 2025-26 --phase hustle`
   - `LeagueHustleStatsPlayer` and `LeagueHustleStatsTeam` for Regular Season and Playoffs. Deflections, contested 2s, contested 3s, loose balls recovered, charges drawn, screen assists. 4 calls per season type, under a minute. Feeds Q2 and Q3 defensive intensity work.

After each phase, run the verification queries from Section 16.4 of the spec and report the row counts. If any phase returns zero rows for 2025-26 Regular Season or 2025-26 Playoffs, stop and surface the failure. Do not proceed to Phase B until Phase A's verification passes for both season types.

In particular, after the `pt-stats` phase, confirm that both `nba_player_tracking_season` and `nba_team_tracking_season` have rows for all 11 measure types. A common failure mode is forgetting the Team call; if `nba_team_tracking_season` has zero rows for a measure type the Player call landed in, you skipped half the work.

Expected Phase A duration end to end: 30 to 45 minutes including verification (45 to 60 if you include the hustle phase).

### Phase B: historical backfill (run after Phase A succeeds)

`python -X utf8 scr\data_collection\tracking_refresh.py --season all --phase all`

Internally, iterate seasons in reverse chronological order: 2024-25, 2023-24, ..., 2013-14. For each season, run synergy, then pt-stats (both Player and Team), then boxscore-track, then (if implemented) hustle. Stop at 2013-14; do not attempt earlier seasons (tracking data does not exist before then).

After each season completes, print a one-line summary: rows inserted per table for that season. After the full backfill completes, run the verification queries for every season and report which ones are non-zero and which are zero (zero is expected only for pre-2013-14 tracking, which we are not requesting).

Expected Phase B duration: 4-6 hours. Run with `nohup` or a Windows equivalent so it survives terminal closure. Daily refresh continues unaffected because tracking ingestion writes to its own tables and does not lock any existing tables.

## Constraints

- **Read the bypass guide first.** Section 12 of `specs/data_pipeline_spec.md` documents three traps that catch every new endpoint integrator. Read it before you start writing endpoint calls.
- **Do not modify any existing table.** This task only adds tables. If you find yourself wanting to add a column to `nba_games` or any other existing table, stop and surface what you want and why.
- **Do not modify `daily_refresh_complete.py` in this task.** The hookup is a follow-up.
- **No new third-party dependencies.** Everything you need is already installed (`nba_api`, `curl_cffi`, `psycopg2`, `pandas`).
- **Errors should be observable.** Every failure path writes a row to the run log with the season, phase, and error message.
- **Pre-2013-14 calls return empty data sets.** Detect and log; do not error.
- **`LeagueDashPtShots` is deferred.** Section 16 lists it as P3 with a documented `nba_api` module-name issue. Do not attempt to wire it up in this task. The 11 `LeagueDashPtStats` measure types listed under Phase A step 2 are the only ones you ingest. Do not pass `Efficiency`.

## Success criteria

Phase A success:

- `nba_synergy_team_play_types` has 30 rows per `(2025-26, season_type, play_type, type_grouping)` combination, for both Regular Season and Playoffs. `nba_synergy_player_play_types` similarly populated.
- `nba_player_tracking_season` has at least 400 player rows for 2025-26 Regular Season covering all 11 measure types.
- `nba_team_tracking_season` has 30 team rows for 2025-26 Regular Season covering all 11 measure types.
- `nba_player_tracking_game` and `nba_team_tracking_game` have rows for every 2025-26 game in `nba_games` (RS + playoffs through the most recent refresh).
- (If hustle phase run) `nba_player_hustle_stats_season` and `nba_team_hustle_stats_season` have rows for 2025-26 RS and Playoffs.
- All Section 16.4 verification queries return non-zero.

Phase B success:

- Same coverage for every season 2013-14 through 2024-25.
- No season returns zero rows (an empty result indicates a bug, not absence of data, since tracking exists from 2013-14 on).
- `tracking_refresh_run_log` contains a row per (season, phase) with the row counts and status.

## What to report back

When you are done, write a short status to `outputs/tracking_ingestion_status.md` in `nba-warehouse` containing:

1. Total wall-clock time for Phase A and Phase B.
2. Total rows inserted per table, broken down by season.
3. Any seasons or phases that failed or returned partial data, with the error messages.
4. The schema choice you made for `nba_player_tracking_season` and `nba_team_tracking_season` (wide table vs narrow tables, applied consistently to both) and a one-sentence justification.
5. Any deviations from Section 16 you had to make to get a stable ingest, and why.

That status file is what the analysis side of the project will read to decide when LAFI v1 work can start.
