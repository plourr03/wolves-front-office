# Spec amendment: tracking data ingestion

**For paste into:** `nba-warehouse/specs/data_pipeline_spec.md`

**Replace existing Section 13 "Tracking data" subsection with:**

### Tracking data

Touches, defensive deflections, contested shots, distance traveled. All `stats.nba.com` only and behind separate endpoints. The patch in `nba_session.py` already works for these endpoints in principle. The full ingestion plan including endpoints, table schemas, and operational ordering is documented in Section 16 below. Tracking data is required for LAFI v2 and significantly improves Q2, Q3, and Q0D.

---

**Append the following as Section 16:**

## 16. Tracking data ingestion

The 2025-26 Wolves postmortem (LAFI, Q3 mechanism analysis, Q2 lineup work) depends on tracking data that lives on `stats.nba.com` but is not yet in the warehouse. This section specifies what to ingest, the tables it lands in, and the operational ordering.

### 16.1 Endpoints in priority order

Priority is set by value-per-minute: cheap, high-leverage endpoints come first so LAFI v1 and Q3 v1 are unblocked before the heavier ingestion finishes.

| Priority | Endpoint | Granularity | Per-call cost | Why it matters |
|---|---|---|---|---|
| P0 | `SynergyPlayTypes` | Season per team and per player, per play type, per offensive/defensive grouping | ~0.1s | Iso, PR-ballhandler, PR-rollman, post-up, spot-up, handoff, off-screen, cut, transition, putbacks, misc. Directly feeds LAFI Components 3 and 4 without the action classifier. Highest value per second of ingestion time. |
| P1 | `LeagueDashPtStats` (11 measure types, Player and Team granularity) | Season per player and season per team | 2-15s per call | `Possessions` → LAFI Component 1 (time-of-possession, dribbles/touch, sec/touch). `SpeedDistance` → LAFI Component 2 (season-level avg speed and total distance, the cleanest source for Movement Death). `CatchShoot`, `PullUpShot` → LAFI Component 5. `Drives`, `Defense`, `Passing`, `ElbowTouch`, `PostTouch`, `PaintTouch`, `Rebounding` → Q2 / Q3 / Q0D inputs. Run each measure type twice per season: once with `player_or_team='Player'`, once with `'Team'`. Do not pass `Efficiency` (overlaps with `nba_player_advanced_stats` already in the warehouse). |
| P2 | `BoxScorePlayerTrackV3` | Per-game player and team | ~0.7s per game | Per-game `distance`, `touches`, `passes`, `contested`/`uncontested` FG splits, `defendedAtRim`. Per-game granularity is what Q2 on/off and Q3 game-by-game decoder need. Heaviest backfill (~15K calls for full historical sweep). |
| P2 | `LeagueHustleStatsPlayer` and `LeagueHustleStatsTeam` | Season per player and team | ~0.5s per call | Deflections, contested 2s, contested 3s, loose balls recovered, charges drawn, screen assists. Feeds Q2 defensive intensity work and Q3 defensive scheme analysis. Cheap to ingest (under one minute for the full historical sweep). |
| P3 (deferred) | `LeagueDashPtShots` | Season per player per defender-distance bucket | TBD | Feeds the expected-eFG model in Q3a. nba_api has a version-dependent module-name issue (verified 2026-05-14). Wire up after the action classifier is in flight. |
| P4 (deferred) | `BoxScoreMatchupsV3` | Per-game matchup pairs | TBD | Defensive matchup data: who guarded whom and for how long. Needed for the Q3c Gobert vs Naz comparison. Reserved for Q3 build time; not needed for LAFI v1. |

Tracking data on `stats.nba.com` starts in 2013-14 (the SportVU rollout). Calls for older seasons return empty data sets. Do not waste backfill cycles on pre-2013-14 seasons.

### 16.2 Tables to add

All in the `nba` schema. All use `INSERT ... ON CONFLICT DO UPDATE` for idempotency.

#### `nba_synergy_team_play_types`

One row per `(season_year, season_type, team_id, play_type, type_grouping)`.

Primary key: `(season_year, season_type, team_id, play_type, type_grouping)`.

Columns (from `SynergyPlayTypes` with `player_or_team_abbreviation='T'`):

- `season_year` (varchar 7), e.g. `'2025-26'`.
- `season_type` (varchar 20): `'Regular Season'` or `'Playoffs'`.
- `team_id` (int), `team_abbreviation` (varchar 3), `team_name` (varchar).
- `play_type` (varchar 30): `Isolation`, `PRBallHandler`, `PRRollman`, `PostUp`, `Spotup`, `Handoff`, `OffScreen`, `Cut`, `Transition`, `Putbacks`, `Misc`.
- `type_grouping` (varchar 10): `offensive` or `defensive`.
- `percentile` (numeric), `gp` (int), `poss_pct` (numeric), `ppp` (numeric), `fg_pct` (numeric).
- `ft_poss_pct`, `tov_poss_pct`, `sf_poss_pct`, `plus_one_poss_pct`, `score_poss_pct` (all numeric).
- `efg_pct` (numeric), `poss` (int), `pts` (int), `fgm` (int), `fga` (int), `fgmx` (int).
- `source` (varchar 20): `'stats_api'`.
- `updated_at` (timestamp).

#### `nba_synergy_player_play_types`

Same as above but at player granularity. Primary key: `(season_year, season_type, player_id, play_type, type_grouping)`. Adds `player_id`, `player_name`, plus `team_id` for the player's team of record in that play-type slice.

#### `nba_player_tracking_season`

One row per `(player_id, season_year, season_type, measure_type)`. Most measure types share a common header (player, team, gp, w, l, min) but have measure-specific columns. Storing as a single wide table with the union of all measure-specific columns (NULL where not applicable) is simplest for queries.

Primary key: `(player_id, season_year, season_type, measure_type)`.

Common columns: `season_year`, `season_type`, `measure_type` (varchar 30), `player_id`, `player_name`, `team_id`, `team_abbreviation`, `gp`, `w`, `l`, `min`, `source`, `updated_at`.

Measure-specific columns (union, NULL where the measure type does not produce them):

- From `Possessions`: `points`, `touches`, `front_ct_touches`, `time_of_poss`, `avg_sec_per_touch`, `avg_drib_per_touch`, `pts_per_touch`, `elbow_touches`, `post_touches`, `paint_touches`, `pts_per_elbow_touch`, `pts_per_post_touch`, `pts_per_paint_touch`.
- From `SpeedDistance`: `dist_feet`, `dist_miles`, `dist_miles_off`, `dist_miles_def`, `avg_speed`, `avg_speed_off`, `avg_speed_def`.
- From `CatchShoot`: `catch_shoot_fgm`, `catch_shoot_fga`, `catch_shoot_fg_pct`, `catch_shoot_pts`, `catch_shoot_fg3m`, `catch_shoot_fg3a`, `catch_shoot_fg3_pct`, `catch_shoot_efg_pct`.
- From `PullUpShot`: `pull_up_fgm`, `pull_up_fga`, `pull_up_fg_pct`, `pull_up_pts`, `pull_up_fg3m`, `pull_up_fg3a`, `pull_up_fg3_pct`, `pull_up_efg_pct`.
- From `Drives`: `drives`, `drive_fgm`, `drive_fga`, `drive_fg_pct`, `drive_ftm`, `drive_fta`, `drive_ft_pct`, `drive_pts`, `drive_pts_pct`, `drive_passes`, `drive_passes_pct`, `drive_ast`, `drive_ast_pct`, `drive_tov`, `drive_tov_pct`, `drive_pf`, `drive_pf_pct`.
- From `Defense`: `def_rim_fgm`, `def_rim_fga`, `def_rim_fg_pct`, plus `stl`, `blk`, `dreb`, `dfgm`, `dfga`, `dfg_pct`.
- From `Passing`: `passes_made`, `passes_received`, `assists`, `secondary_assists`, `potential_ast`, `ast_pts_created`, `ast_adj`, `ast_to_pass_pct`, `ast_to_pass_pct_adj`.
- From `ElbowTouch`, `PostTouch`, `PaintTouch`: `touches`, `fgm`, `fga`, `fg_pct`, `ftm`, `fta`, `ft_pct`, `pts`, `passes`, `ast`, `tov`, `pf`, `pts_pct`, `pass_pct`, `ast_pct`, `tov_pct`, `fouled_pct`. Prefixed by `elbow_`, `post_`, `paint_` respectively.
- From `Rebounding`: `oreb`, `oreb_contested`, `oreb_uncontested`, `oreb_chances`, `oreb_chance_pct`, `oreb_chance_defer_pct`, plus `dreb` versions, plus `reb_chance_pct_adj`.

If the wide table is unwieldy, an alternative schema is one table per measure type, all with the same `(player_id, season_year, season_type)` key. Either works. The wide table is simpler operationally; ten narrow tables are easier to evolve. Implementer's choice; document the choice in this section once made.

#### `nba_team_tracking_season`

Team-level analog of `nba_player_tracking_season`. Populated by calling `LeagueDashPtStats` with `player_or_team='Team'` for each of the 11 measure types.

Primary key: `(team_id, season_year, season_type, measure_type)`.

Columns: drop the player fields (`player_id`, `player_name`) from `nba_player_tracking_season`'s schema; keep everything else. Use the same wide-vs-narrow choice as for the player table.

LAFI's team-level metrics read from this table directly. Q4 archetype clustering pulls features from here.

#### `nba_player_hustle_stats_season` and `nba_team_hustle_stats_season`

From `LeagueHustleStatsPlayer` and `LeagueHustleStatsTeam`. One row per `(player_id|team_id, season_year, season_type)`.

Primary keys: `(player_id, season_year, season_type)` and `(team_id, season_year, season_type)`.

Columns include `contested_shots`, `contested_shots_2pt`, `contested_shots_3pt`, `deflections`, `charges_drawn`, `screen_assists`, `screen_ast_pts`, `off_loose_balls_recovered`, `def_loose_balls_recovered`, `loose_balls_recovered`, `pct_loose_balls_recovered_off`, `pct_loose_balls_recovered_def`, `pct_loose_balls_recovered`, `off_boxouts`, `def_boxouts`, `box_outs`, `box_out_player_team_rebs`, `box_out_player_rebs`. Plus the common header (`gp`, `w`, `l`, `min`, etc.).

#### `nba_player_tracking_game`

One row per `(game_id, player_id)` from `BoxScorePlayerTrackV3`.

Primary key: `(game_id, player_id)`.

Columns mirror the endpoint payload:

- `game_id`, `team_id`, `team_abbreviation`, `player_id`, `player_name`, `position`, `comment` (varchar, usually empty), `jersey_num`, `minutes` (varchar like `"29:37"`), `minutes_float` (numeric, derived).
- `speed` (numeric, avg mph), `distance` (numeric, miles).
- `rebound_chances_offensive`, `rebound_chances_defensive`, `rebound_chances_total` (all int).
- `touches`, `secondary_assists`, `free_throw_assists`, `passes`, `assists` (all int).
- `contested_fgm`, `contested_fga`, `contested_fg_pct` (int/int/numeric).
- `uncontested_fgm`, `uncontested_fga`, `uncontested_fg_pct`.
- `fg_pct` (numeric).
- `defended_at_rim_fgm`, `defended_at_rim_fga`, `defended_at_rim_fg_pct`.
- `source` (varchar 20): `'stats_api'`.
- `updated_at` (timestamp).

#### `nba_team_tracking_game`

Same shape as `nba_player_tracking_game` minus player fields. Primary key: `(game_id, team_id)`. Mirrors the `team_stats` data set returned by `BoxScorePlayerTrackV3`.

### 16.3 Operational ordering

The current-season analysis blocks first. The historical backfill is for later. So:

**Phase A: Current season ingestion (2025-26).**

In strict order, finishing each before starting the next:

1. `SynergyPlayTypes` for 2025-26 Regular Season and 2025-26 Playoffs. All 11 play types times both type groupings (offensive, defensive) times both granularities (team, player) = 44 calls per season type, ~10 seconds total.
2. `LeagueDashPtStats` for 2025-26 Regular Season and 2025-26 Playoffs, all 11 measure types (`Possessions, SpeedDistance, CatchShoot, PullUpShot, Drives, Defense, Passing, ElbowTouch, PostTouch, PaintTouch, Rebounding`), each run twice (`Player` and `Team`). 44 calls per season type, 5-15 minutes per season type.
3. `BoxScorePlayerTrackV3` for every 2025-26 game in `nba_games` that does not already have a row in `nba_player_tracking_game`. ~1300 calls for RS plus current playoffs, 15-25 minutes at 0.7-1.5s per call with light rate-limit pacing.
4. (Optional) `LeagueHustleStatsPlayer` and `LeagueHustleStatsTeam` for both season types. 4 calls per season type, under a minute total.

After Phase A, the 2025-26 tracking universe is complete. LAFI v1 and the team-level Q3 work can begin.

**Phase B: Historical backfill (2024-25 back to 2013-14).**

Process seasons in reverse-chronological order so the most recently relevant data lands first:

1. For each season in `[2024-25, 2023-24, 2022-23, 2021-22, 2020-21, 2019-20, 2018-19, 2017-18, 2016-17, 2015-16, 2014-15, 2013-14]`:
   - `SynergyPlayTypes` for Regular Season and Playoffs.
   - `LeagueDashPtStats` for Regular Season and Playoffs, all 11 measure types, both Player and Team granularity.
   - `BoxScorePlayerTrackV3` for every game in `nba_games` for that season, regular season and playoffs.
   - (Optional) `LeagueHustleStatsPlayer` and `LeagueHustleStatsTeam` for both season types.

Expected total time: ~4-6 hours for `BoxScorePlayerTrackV3` across 12 seasons of historical games, plus 1-2 hours for the other endpoints combined. Run in background; the daily refresh continues unaffected.

If a season returns empty data sets (pre-tracking eras for endpoints we did not realize were time-limited), log the empty count and continue. Do not error out.

### 16.4 Implementation notes

**Script layout.** Add `scr/data_collection/tracking_refresh.py` modeled after `daily_refresh_complete.py`. It is invoked standalone for the backfill and called as a final phase by `daily_refresh_complete.py` for the current-season incremental.

**Akamai bypass.** Import `nba_session` and apply `patch_nba_api()` at the top exactly like the existing scripts. No additional infrastructure is required.

**Empty-param trap.** `LeagueDashPtStats` accepts many nullable parameters. Do not pass them with empty string defaults. The `_ParamFilteringSession` wrapper in `nba_session.py` filters them automatically once the patch is applied.

**Rate limiting.** Match the existing pace pattern (8-15 second jitter between heavy calls; less for cheap ones). For `SynergyPlayTypes` and `LeagueDashPtStats` season-aggregate calls, 0.5-1 second jitter is fine. For `BoxScorePlayerTrackV3` per-game calls, use the existing per-game pace (similar to `boxscoreadvancedv3`).

**Idempotency.** Every write path uses upsert on the documented primary key. Reruns are safe and produce zero new rows.

**Observability.** Each phase writes a counts summary to `daily_refresh_run_log` (extend the existing schema or add a parallel `tracking_refresh_run_log` table; implementer's choice, document the choice here).

**Verification.** After Phase A, the following queries should return non-zero rows:

```sql
SELECT COUNT(*) FROM nba_synergy_team_play_types WHERE season_year = '2025-26';
SELECT COUNT(*) FROM nba_synergy_player_play_types WHERE season_year = '2025-26';
SELECT measure_type, COUNT(*) FROM nba_player_tracking_season WHERE season_year = '2025-26' GROUP BY measure_type;
SELECT measure_type, COUNT(*) FROM nba_team_tracking_season WHERE season_year = '2025-26' GROUP BY measure_type;
SELECT COUNT(DISTINCT game_id) FROM nba_player_tracking_game
WHERE game_id IN (SELECT game_id FROM nba_games WHERE season_id IN (22025, 42025));
SELECT COUNT(DISTINCT game_id) FROM nba_team_tracking_game
WHERE game_id IN (SELECT game_id FROM nba_games WHERE season_id IN (22025, 42025));
-- (optional) hustle
SELECT COUNT(*) FROM nba_player_hustle_stats_season WHERE season_year = '2025-26';
SELECT COUNT(*) FROM nba_team_hustle_stats_season WHERE season_year = '2025-26';
```

The `measure_type` rollups must show 11 distinct rows per season type (one per measure type) and the row counts per measure type should be approximately equal (each measure type is one row per player or team).

After Phase B, the same queries should return rows for every season_year from 2013-14 forward.

### 16.5 Known gaps and risks

- **Pre-2013-14 tracking.** Empty. Do not attempt.
- **`LeagueDashPtShots` module name in `nba_api`.** As of 2026-05-14 the expected module name fails to import. The endpoint exists in the API; the Python binding is the issue. Verify the correct module name before adding it to ingestion.
- **Tracking accuracy in bubble (2019-20) and shortened (2020-21) seasons.** Tracking may be partial or anomalous. Ingest anyway. The downstream analyses already plan to flag these seasons.
- **Synergy classification drift.** The play-type taxonomy can change subtly between seasons. Pull the raw counts every time rather than caching derived percentages.

### 16.6 What this unblocks

| Analysis | Before tracking | After tracking |
|---|---|---|
| LAFI Component 1 (Ball Stickiness) | Proxy via `assists / fga` only | Direct: `TIME_OF_POSS`, `AVG_DRIB_PER_TOUCH`, `PASSES` per player |
| LAFI Component 2 (Movement Death) | Not computable | Season-level: `SpeedDistance` measure type gives `avg_speed_off`, `dist_miles_off`. Per-game `distance` per player from `BoxScorePlayerTrackV3` for finer slices. Off-ball share derivable by subtracting the lead handler's contribution. |
| LAFI Component 3 (Isolation Reliance) | Not computable from PBP alone | Direct: Synergy `Isolation` POSS_PCT |
| LAFI Component 4 (Action Poverty) | Blocked on action classifier | Approximated via Synergy frequencies (off-screen, cut, handoff) without classifier |
| LAFI Component 5 (Shot Quality Decay) | Blocked | Direct: `CATCH_SHOOT_EFG_PCT`, `PULL_UP_EFG_PCT` |
| Q2 rim protection (Gobert) | None | `defended_at_rim_fg_pct` per game |
| Q3 PnR coverage (offense) | Blocked on action classifier | Synergy `PRBallHandler` PPP gives macro view |
| Q3 PnR coverage (defense) | Blocked on classifier | Synergy `PRBallHandler` and `PRRollman` defensive grouping; matchup-level data blocked on `BoxScoreMatchupsV3` |
| Q0D Coaching System | Limited | Per-season play-type distribution year over year |
