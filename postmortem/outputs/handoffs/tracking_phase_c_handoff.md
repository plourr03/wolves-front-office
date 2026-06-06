# Phase C tracking ingestion: spec amendment + server agent prompt

Self-contained document. Paste the spec amendment portion into `nba-warehouse/specs/data_pipeline_spec.md` as Section 17 (or append it after Section 16). Then paste the agent prompt at the bottom into the same Claude Code session that built Phase A/B.

The Phase C ingestion adds a small set of endpoints that were originally deferred but turn out to be cheap, work cleanly, and directly unblock Q3 (mechanism analysis), Q2 (defensive on/off, rim protection), and the expected-eFG model that everything downstream depends on. Nothing here conflicts with Phase A/B; new tables only.

---

## Section 17: Tracking data ingestion, Phase C

### 17.1 Why this exists

Phase A and Phase B (Section 16) ingest the bulk-volume tracking endpoints: SynergyPlayTypes, LeagueDashPtStats (11 measure types × Player+Team), BoxScorePlayerTrackV3, and LeagueHustleStats. That covers LAFI v1 and most of Q2 / Q3 / Q0D macro analysis.

Five additional endpoints round out the coverage. They were originally documented as deferred either because (a) one endpoint had a misremembered module name in the original spec, or (b) the work was tied to a specific later analysis (Q3c) that we marked as not-yet-time. Live probing after Phase A/B work began confirmed all of them function and return useful data with low ingestion cost. Phase C ingests them.

### 17.2 Endpoints in priority order

| Priority | Endpoint | Granularity | Per-call cost | Why it matters |
|---|---|---|---|---|
| P0 | `LeagueDashPtDefend` and `LeagueDashPtTeamDefend` | Season per player and per team | ~1-15s | Defender-impact metric: `D_FG_PCT` (opponent FG% allowed when this player is the closest defender) and `NORMAL_FG_PCT` (what those opponents normally shoot), with `PCT_PLUSMINUS` as the delta. Gobert lands at -5.1 pp in 2025-26 (he depresses opponent shooting 5 points below expected). This is the single cleanest defender-quality metric the NBA exposes. Feeds Q2 (is Gobert declining year-over-year), Q3c (Gobert vs Naz comparison), Q5 (archetype thresholds for defensive bigs). |
| P1 | `LeagueDashPlayerShotLocations` and `LeagueDashTeamShotLocations` | Season per player and per team | 4-5s | Full zone breakdowns directly from NBA: `Restricted Area`, `In The Paint (Non-RA)`, `Mid-Range`, `Left Corner 3`, `Right Corner 3`, `Above the Break 3`, `Backcourt`, plus an aggregate `Corner 3`. FGM, FGA, FG_PCT per zone. Replaces the crude zone classifier currently used in Q1 v2 with NBA's own zoning (league-comparable). Feeds Q1, Q3a (shot quality model), Q4 (archetype features). |
| P2 | `ShotChartDetail` | Season per team (returns every shot for that team) | 1-5s | Per-shot data with `LOC_X`, `LOC_Y`, `SHOT_DISTANCE`, `SHOT_ZONE_*` tags, `EVENT_TYPE`, `ACTION_TYPE`, made/missed flag, period, clock. Returns ~7,000-8,500 shots per team-season in one call. Also returns a second dataset of league averages by zone (FGM, FGA, FG_PCT). This is the engine for Q3a's expected-eFG model. Without it, the model can't be fit without re-deriving shot location from PBP (doable but messy). |
| P3 | `BoxScoreMatchupsV3` | Per-game | ~0.5-1s | Per-game defender-attacker pairs with `matchupMinutes`, `partialPossessions`, `matchupFieldGoalsMade/Attempted`, `matchupThreePointersMade/Attempted`, plus help-defense fields. ~200 matchup rows per game. Critical for Q3c (who is the actual screen defender on opponent PnRs, what happens when Gobert is the matchup vs Naz). |
| P4 (lower priority, optional) | `LeagueDashPlayerPtShot`, `LeagueDashTeamPtShot`, `LeagueDashOppPtShot` | Season per player and team | 1-15s | 2PT-vs-3PT shooting and frequency splits per player/team and what opponents shoot against each team. Useful for archetype work in Q4 but partially redundant with `LeagueDashPtStats` (`CatchShoot`, `PullUpShot`) and `LeagueDashPlayerShotLocations` (P1 above). Ingest if cheap, skip if you want to keep Phase C tight. |

`PlayerDashPtShotDefend` was tested and returns empty data sets for primary defenders (probably needs a `defense_category` parameter that the nba_api default doesn't supply). The same information is available via `LeagueDashPtDefend` (P0), so we do not ingest `PlayerDashPtShotDefend`. Document this in 17.5 so future readers don't try to wire it up.

### 17.3 Tables to add

All in the `nba` schema. All upsert on the documented primary key. Use the same wide-table schema decision the agent made for `nba_player_tracking_season` in Phase A (single wide table per granularity). For `ShotChartDetail` and `BoxScoreMatchupsV3` the row-level structure is dictated by the endpoint payload; the schemas below mirror what comes back.

As in Phase A/B: **live-probe the column names and types before locking the DDL**. Earlier iterations of the Phase A/B spec had column-name drift from the actual API responses; the agent caught and corrected several in the live build. Same protocol here.

#### `nba_player_pt_defend_season`

From `LeagueDashPtDefend`. One row per `(player_id, season_year, season_type)`.

Primary key: `(player_id, season_year, season_type)`.

Columns (verified from live probe on 2025-26 RS):
`close_def_person_id (-> player_id), player_name, player_last_team_id, player_last_team_abbreviation, player_position, age, gp, g, freq, d_fgm, d_fga, d_fg_pct, normal_fg_pct, pct_plusminus, source, updated_at`.

#### `nba_team_pt_defend_season`

From `LeagueDashPtTeamDefend`. Primary key: `(team_id, season_year, season_type)`.

Columns: `team_id, team_name, team_abbreviation, gp, g, freq, d_fgm, d_fga, d_fg_pct, normal_fg_pct, pct_plusminus, source, updated_at`.

#### `nba_player_shot_locations_season`

From `LeagueDashPlayerShotLocations`. The endpoint returns multi-level column headers; flatten them at ingestion time using the pattern `<zone_lowercased_underscored>_<metric>` for each of the 8 zone groups. Primary key: `(player_id, season_year, season_type)`.

Zone groups (verified from live probe):
- `Restricted Area` -> `restricted_area_fgm`, `restricted_area_fga`, `restricted_area_fg_pct`
- `In The Paint (Non-RA)` -> `paint_non_ra_fgm`, `paint_non_ra_fga`, `paint_non_ra_fg_pct`
- `Mid-Range` -> `midrange_fgm`, `midrange_fga`, `midrange_fg_pct`
- `Left Corner 3` -> `left_corner_3_fgm`, `left_corner_3_fga`, `left_corner_3_fg_pct`
- `Right Corner 3` -> `right_corner_3_fgm`, `right_corner_3_fga`, `right_corner_3_fg_pct`
- `Above the Break 3` -> `above_break_3_fgm`, `above_break_3_fga`, `above_break_3_fg_pct`
- `Backcourt` -> `backcourt_fgm`, `backcourt_fga`, `backcourt_fg_pct`
- `Corner 3` (aggregate) -> `corner_3_fgm`, `corner_3_fga`, `corner_3_fg_pct`

Plus header columns: `player_id, player_name, team_id, team_abbreviation, age, nickname, source, updated_at`.

#### `nba_team_shot_locations_season`

From `LeagueDashTeamShotLocations`. Same shape as the player table minus the player fields, plus the team header. Primary key: `(team_id, season_year, season_type)`.

#### `nba_shot_chart_detail`

From `ShotChartDetail` dataset[0]. One row per shot. Primary key: `(game_id, game_event_id)`.

Columns (verified from live probe):
`grid_type, game_id, game_event_id, player_id, player_name, team_id, team_name, period, minutes_remaining, seconds_remaining, event_type (Made Shot / Missed Shot), action_type, shot_type (2PT/3PT Field Goal), shot_zone_basic, shot_zone_area, shot_zone_range, shot_distance, loc_x, loc_y, shot_attempted_flag, shot_made_flag, game_date, htm, vtm, source, updated_at`.

Note: this duplicates some information already in `nba_play_by_play` (shot location, made/missed). Keep both. PBP has shot details for every shot in the game including FTs. `nba_shot_chart_detail` has the NBA's authoritative zone classification (`SHOT_ZONE_BASIC/AREA/RANGE`), which differs from PBP and is what the rest of the league reports against. Q3a's expected-eFG model uses this table; ad-hoc PBP queries continue to use `nba_play_by_play`.

#### `nba_shot_chart_league_avg`

From `ShotChartDetail` dataset[1]. League averages by zone. Primary key: `(season_year, season_type, shot_zone_basic, shot_zone_area, shot_zone_range)`.

Columns: `season_year, season_type, grid_type, shot_zone_basic, shot_zone_area, shot_zone_range, fga, fgm, fg_pct, source, updated_at`.

Note: this dataset is returned alongside the team's shots in the same API call. Capture it once per `(season, team)` call but upsert keyed on `(season_year, season_type, zone fields)` so duplicate writes are no-ops.

#### `nba_boxscore_matchups`

From `BoxScoreMatchupsV3`. One row per `(game_id, team_id, person_id_off, person_id_def)`. Primary key on those four columns.

Columns (verified from live probe; snake_case the camelCase API field names):
`game_id, team_id, team_city, team_name, team_tricode, team_slug, person_id_off, first_name_off, family_name_off, name_i_off, player_slug_off, position_off, comment_off, jersey_num_off, person_id_def, first_name_def, family_name_def, name_i_def, player_slug_def, jersey_num_def, matchup_minutes (text like '0:10'), matchup_minutes_sort (numeric seconds), partial_possessions, percentage_defender_total_time, percentage_offensive_total_time, percentage_total_time_both_on, switches_on, player_points, team_points, matchup_assists, matchup_potential_assists, matchup_turnovers, matchup_blocks, matchup_field_goals_made, matchup_field_goals_attempted, matchup_field_goals_percentage, matchup_three_pointers_made, matchup_three_pointers_attempted, matchup_three_pointers_percentage, help_blocks, help_field_goals_made, help_field_goals_attempted, help_field_goals_percentage, matchup_free_throws_made, matchup_free_throws_attempted, shooting_fouls, source, updated_at`.

#### (Optional) `nba_player_pt_shot_season`, `nba_team_pt_shot_season`, `nba_opp_pt_shot_season`

From `LeagueDashPlayerPtShot`, `LeagueDashTeamPtShot`, `LeagueDashOppPtShot`. Only ingest if P4 is greenlit. Same wide-table style. Primary keys: `(player_id, season_year, season_type)` and `(team_id, ...)`.

Columns shared across all three (verified from live probe): `gp, g, fga_frequency, fgm, fga, fg_pct, efg_pct, fg2a_frequency, fg2m, fg2a, fg2_pct, fg3a_frequency, fg3m, fg3a, fg3_pct`, plus appropriate headers.

### 17.4 Operational ordering

Same pattern as Phase A/B: current season first, historical backfill second.

**Phase C-A: 2025-26 current season (run first).**

Execute, in order:

1. `python -X utf8 pipeline/tracking_refresh.py --season 2025-26 --phase pt-defend`
   - `LeagueDashPtDefend` and `LeagueDashPtTeamDefend` for Regular Season and Playoffs. 4 calls per season type, ~1 minute total.
2. `python -X utf8 pipeline/tracking_refresh.py --season 2025-26 --phase shot-locations`
   - `LeagueDashPlayerShotLocations` and `LeagueDashTeamShotLocations` for Regular Season and Playoffs. 4 calls per season type, ~30 seconds.
3. `python -X utf8 pipeline/tracking_refresh.py --season 2025-26 --phase shot-chart`
   - `ShotChartDetail` for every team (30 teams) for Regular Season and Playoffs. 60 calls per season type, 5-10 minutes total. Writes both `nba_shot_chart_detail` and `nba_shot_chart_league_avg`.
4. `python -X utf8 pipeline/tracking_refresh.py --season 2025-26 --phase matchups-wolves`
   - `BoxScoreMatchupsV3` for every 2025-26 Wolves game in `nba_games` only (RS + playoffs). ~95 calls, 1-2 minutes. The Wolves-first subset lets Q3c begin work without waiting on the full league backfill.
5. *(optional)* `python -X utf8 pipeline/tracking_refresh.py --season 2025-26 --phase pt-shot`
   - `LeagueDashPlayerPtShot`, `LeagueDashTeamPtShot`, `LeagueDashOppPtShot` for Regular Season and Playoffs. 6 calls per season type, ~1 minute.

Run verification queries after each step. If any return zero rows for an expected season type, stop and surface the failure.

Expected Phase C-A duration end to end: 10-15 minutes (20 if pt-shot included).

**Phase C-B: historical backfill.**

`python -X utf8 pipeline/tracking_refresh.py --season all --phase all-c`

Internally iterate seasons in reverse-chronological order: 2024-25 back to 2013-14. For each season, run pt-defend, shot-locations, shot-chart, and pt-shot if enabled. **Skip `BoxScoreMatchupsV3` for the full league backfill** for now; per-game over 12 seasons is ~15K calls and adds several hours of runtime that we don't need yet. Instead, run `--phase matchups-wolves --season all` separately to backfill Wolves matchups across all seasons (~1100 games, ~20 minutes).

Expected Phase C-B duration: 1-2 hours for the season-aggregate endpoints. Additional ~20 minutes for the Wolves-only matchups backfill.

### 17.5 Implementation notes

**Reuse Phase A/B infrastructure.** The script `pipeline/tracking_refresh.py` already exists with `--season` / `--phase` argument parsing, circuit breaker, jittered rate limiting, run-log writes, and per-call progress prints. Add the new phase handlers (`pt-defend`, `shot-locations`, `shot-chart`, `matchups-wolves`, optionally `pt-shot`, plus an `all-c` aggregate) without restructuring the existing script.

**Live-probe before locking DDL.** Phase A's spec had several column-name drifts that the agent caught by probing live. Do the same for Phase C: hit each endpoint once before writing `CREATE TABLE`, dump the columns, confirm the snake-cased names match what's documented here, and adjust where they don't. The schema lists in 17.3 are derived from probes on 2025-26 RS but historical seasons can have minor differences (most often: a column was added or dropped in some year).

**`LeagueDashPlayerShotLocations` returns multi-level columns.** The DataFrame from `obj.get_data_frames()[0]` has a 2-level column index where the top level is the zone name and the bottom level is the metric. Flatten with `df.columns = [_flatten(c) for c in df.columns]` where `_flatten` maps the tuple to the snake-case name documented in 17.3. Test the flattening on a 2024-25 sample to confirm zones haven't been renamed.

**`ShotChartDetail` returns two datasets.** Dataset[0] is the per-shot data. Dataset[1] is league averages by zone. Persist both. The league-averages dataset is keyed on zone fields and the season being queried, so write it with the season metadata attached.

**`BoxScoreMatchupsV3` field naming is camelCase.** Same as `BoxScorePlayerTrackV3` from Phase A. Snake-case at ingest. Use the existing helper if one was built; otherwise write a small `_camel_to_snake` function once.

**Pre-2013-14 tracking returns empty for the season-aggregate endpoints.** `BoxScoreMatchupsV3` may return data for older games but the matchup-level fields will be sparse. Log empty datasets without erroring, same as Phase A/B.

**Idempotency.** Every write path uses `INSERT ... ON CONFLICT DO UPDATE`. Reruns produce zero new rows.

**Observability.** Write per-phase row counts to `tracking_refresh_run_log`. Extend the existing schema if needed to accommodate the new phase names (`pt-defend`, `shot-locations`, `shot-chart`, `matchups-wolves`, `pt-shot`, `all-c`).

### 17.6 Verification queries (Section 16.4 analog)

After Phase C-A:

```sql
SELECT COUNT(*) FROM nba_player_pt_defend_season WHERE season_year = '2025-26';
SELECT COUNT(*) FROM nba_team_pt_defend_season   WHERE season_year = '2025-26';
SELECT COUNT(*) FROM nba_player_shot_locations_season WHERE season_year = '2025-26';
SELECT COUNT(*) FROM nba_team_shot_locations_season   WHERE season_year = '2025-26';
SELECT COUNT(DISTINCT game_id), COUNT(*) FROM nba_shot_chart_detail
  WHERE game_id IN (SELECT game_id FROM nba_games WHERE season_id IN (22025, 42025));
SELECT season_year, season_type, COUNT(*)
  FROM nba_shot_chart_league_avg
  WHERE season_year = '2025-26' GROUP BY season_year, season_type;
SELECT COUNT(DISTINCT game_id), COUNT(*) FROM nba_boxscore_matchups
  WHERE game_id IN (SELECT game_id FROM nba_games WHERE season_id IN (22025, 42025) AND team_abbreviation = 'MIN');

-- Spot check: Gobert should have a row in pt_defend with PCT_PLUSMINUS noticeably negative
SELECT player_name, player_last_team_abbreviation, gp, d_fga, d_fg_pct, normal_fg_pct, pct_plusminus
FROM nba_player_pt_defend_season
WHERE season_year = '2025-26' AND season_type = 'Regular Season' AND player_name = 'Rudy Gobert';

-- Spot check: 2025-26 Wolves' restricted-area FG% (should be ~70%)
SELECT team_abbreviation, gp, restricted_area_fgm, restricted_area_fga, restricted_area_fg_pct
FROM nba_team_shot_locations_season
WHERE season_year = '2025-26' AND season_type = 'Regular Season' AND team_abbreviation = 'MIN';
```

Expected: every count returns a non-zero row count. Gobert's PCT_PLUSMINUS for 2025-26 RS should be around -0.05 (verified by the wolves-front-office side; deviation of more than 0.02 would suggest an ingestion issue).

After Phase C-B: every season from 2013-14 to 2025-26 should have non-zero counts for the season-aggregate tables.

### 17.7 Known gaps and risks

- **`PlayerDashPtShotDefend` not ingested.** Returns empty even for primary defenders unless `defense_category` is supplied. `LeagueDashPtDefend` (in this Phase) and `BoxScoreMatchupsV3` (also in this Phase) cover the same information. Skip.
- **Multi-level column flattening for shot locations.** Test on a couple of older seasons; if zone names changed pre-2017, add aliasing.
- **Tracking data starts 2013-14 universally for the season-aggregate endpoints, but `BoxScoreMatchupsV3` may return data for older games with partial fields.** Default-skip pre-2013-14 unless we explicitly want historical matchup data.
- **`ShotChartDetail` per-team calls** for older seasons (pre-2014ish) may not return tracking-derived zone tags. Don't error; log and continue.

---

## Agent prompt to paste

Once Section 17 above is applied to `specs/data_pipeline_spec.md`, hand the agent the following prompt in the same Claude Code session that built Phase A/B.

> Phase C of tracking ingestion. Section 17 of `specs/data_pipeline_spec.md` is the spec; read it end-to-end first.
>
> Add the new phase handlers to `pipeline/tracking_refresh.py`. Do not restructure the existing script; extend it. The new phases are: `pt-defend`, `shot-locations`, `shot-chart`, `matchups-wolves`, `pt-shot` (optional), plus an `all-c` aggregate that runs the four required ones in order.
>
> Add the eight new tables (six required + two from the optional pt-shot phase if you ingest it) per the schemas in Section 17.3. Use the same wide-table convention you chose in Phase A. Update `docs/database_inventory.md` once the tables exist and have rows.
>
> Before writing the `CREATE TABLE` statements, **live-probe each endpoint once** on 2025-26 RS, dump the column list, and confirm the snake-cased names match Section 17.3. If anything drifts (camelCase fields, new columns, renamed columns), correct the DDL and document the correction. You caught several such drifts in Phase A; expect a few here too.
>
> Run Phase C-A in foreground (2025-26 current season). After each sub-phase, run the verification queries in Section 17.6 and report row counts. Wolves' Gobert should show `pct_plusminus` around -0.05 after the `pt-defend` step; Wolves' restricted-area FG_PCT should be around 0.70 after the `shot-locations` step. If those spot checks fail, stop and surface what you see.
>
> After Phase C-A passes verification, kick off Phase C-B (historical backfill 2024-25 back to 2013-14) in the background with `nohup` to `logs/phase-c-backfill-YYYY-MM-DD.log`. The Wolves-only matchups backfill (`--phase matchups-wolves --season all`) can run in the same background block; sequence it after the season-aggregate work so each runs in isolation.
>
> Constraints (same as Phase A/B):
> - Do not modify any existing table.
> - Do not modify `daily_refresh_complete.py`.
> - Idempotent upserts on documented primary keys.
> - No new third-party dependencies.
> - Pre-2013-14 empties are logged, not errored.
> - `PlayerDashPtShotDefend` is explicitly skipped (see 17.7).
>
> When Phase C-B finishes, append to `outputs/tracking_ingestion_status.md` (the same status doc you wrote for Phase A/B). Report total runtime, row counts per table per season, any deviations from Section 17 you had to make, and a one-line answer to "did Gobert's `pct_plusminus` historical trend show monotonic decline or flat?" (a curiosity check that confirms the data is sensible).
