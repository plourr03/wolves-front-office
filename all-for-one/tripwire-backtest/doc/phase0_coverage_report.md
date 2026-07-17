# Phase 0 Coverage Report

Tripwire backtest, Phase 0 Step 1. Produced 2026-07-17 against `nba_warehouse` (PostgreSQL 18.4, schema `nba`), reached via repo-root `.env`.

Every number below is reproducible from the query printed beneath it. Nothing here is inferred from reading code.

Status: **Phases 1 through 4 have not run.** This report plus the stint trust spike, gap register, availability reconciliation, and rename map are the whole of Phase 0.

## 0. Headline

Four findings change the spec.

1. **`usg_pct` is stored as a fraction, not a percentage.** The spec's Scenario A filter `s0.usg_pct >= 28.0` matches **zero rows** against real data. It does not error. It returns an empty class. See section 1; this is the most dangerous finding in the report.
2. **There is no `minutes` column on the player-season table.** The spec's `s0.minutes >= 1200` filter has no source. Minutes must be derived. See section 2.
3. **There is no season-grain position field.** `pos_group = 'G'` has to resolve through a career-static career position on `nba_player_bio`. It works, but it is career-static and that has to be declared. See section 3.
4. **SPACE-ANT cannot produce a reliability curve.** Catch-and-shoot exists only at season grain; game grain has no three-point split and no defender-distance data exists anywhere in the warehouse. See section 5. This is a data verdict, not a modeling choice.

## 1. The usg_pct scale bug (blocking, silent)

The spec, section 7, Scenario A class extraction:

```sql
AND s0.usg_pct >= 28.0
```

Real distribution of `nba.nba_player_season_bio.usg_pct`, Regular Season, 2009-10 forward:

| min | max | avg | p99 |
|---|---|---|---|
| 0.0000 | 0.5710 | 0.1797 | 0.3252 |

```sql
SELECT MIN(usg_pct), MAX(usg_pct), AVG(usg_pct),
       PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY usg_pct)
FROM nba.nba_player_season_bio
WHERE season_type='Regular Season' AND season_year >= '2009-10';
```

The column is a **fraction in [0, 0.571]**. So:

| Filter | Player-seasons matched |
|---|---|
| `usg_pct >= 28.0` (as written in the spec) | **0** |
| `usg_pct >= 0.28` (intended semantics) | **409** |
| total rows in window | 8,783 |

```sql
SELECT SUM((usg_pct >= 28.0)::int)  AS bar_as_written,
       SUM((usg_pct >= 0.28)::int)  AS bar_as_fraction,
       COUNT(*)
FROM nba.nba_player_season_bio
WHERE season_type='Regular Season' AND season_year >= '2009-10';
```

**Why this matters more than a typo.** The query does not fail. It returns an empty result set, which reads as "no historical cases match our situation" rather than "the filter is on the wrong scale." Run unattended, it would have produced a Scenario A class of size zero and an entirely plausible-looking Phase 2 report saying the reference class is too thin to support wires. This is the same shape as the `score_home` / `score_away` silent bug: a code path that is wrong but never errors.

Correct the spec to `>= 0.28`, and add a non-empty assertion to the extraction query so this class can never silently come back empty again.

Scale sanity check, top usage seasons since 2009-10 (`gp >= 40`), which is what the corrected filter is reading:

| Player | Season | usg_pct | gp |
|---|---|---|---|
| Russell Westbrook | 2016-17 | 0.4020 | 81 |
| James Harden | 2018-19 | 0.3960 | 78 |
| Joel Embiid | 2021-22 | 0.3750 | 68 |
| Giannis Antetokounmpo | 2022-23 | 0.3730 | 63 |
| Joel Embiid | 2022-23 | 0.3700 | 66 |
| Luka Doncic | 2022-23 | 0.3680 | 66 |

That is the right list of names in the right order, which is the check that the fraction reading is correct rather than the column being on some other scale entirely.

## 2. `player_season` is a DERIVED view, not a table rename

The spec treats `player_season` as a single table with `usg_pct`, `minutes`, `team_id`, `pos_group`. The closest real table is `nba.nba_player_season_bio` (20,469 rows, 1996-97 to 2025-26, PK `(player_id, season_year, season_type)`). Its full column list:

```
player_id, season_year, season_type, player_name, team_id, team_abbreviation,
age, player_height, player_height_inches, player_weight, college, country,
draft_year, draft_round, draft_number, gp, pts, reb, ast, net_rating,
oreb_pct, dreb_pct, usg_pct, ts_pct, ast_pct, source, updated_at
```

**There is no `minutes` column, and no `position` column.** `pts` / `reb` / `ast` are per-game averages, not totals.

So the spec's `s0.minutes >= 1200` has no direct source. Minutes must be derived per player-season:

- **Preferred:** `SUM(nba_player_advanced_stats.minutes_float)`, seconds-precise, joined to `nba_games` for the season.
- **Acceptable:** `SUM(nba_player_stats.minutes_played)`, but note this column is **INTEGER** (per-game truncation). Summed over a full season it under-counts by roughly 0.5 minutes per game played, so about 41 minutes over 82 games. Against a 1,200-minute threshold that is a ~3% bias, always downward, which will marginally exclude players sitting just above the bar.

Recommendation: derive from `minutes_float`. Record `player_season` in the rename map as **DERIVED**, with the derivation, rather than as a clean rename.

## 3. Position: career-static, adequate, must be declared

No season-grain position field exists. Three candidates were checked.

| Source | Verdict |
|---|---|
| `nba_player_season_bio` | **No position column at all.** |
| `nba_player_advanced_stats.position` | Values are G / F / C but **~61% NULL in every season**. |
| `nba_team_rosters.position` | G / F / C plus hyphenates, but **`season=2025` only**. |
| `nba_player_bio.position` | Guard / Forward / Center plus hyphenates. Static, career-level, all-time. **The only usable source.** |

The `nba_player_advanced_stats.position` null rate is stable at 58-63% across every season 2009-10 to 2025-26, which is not decay. It is structural:

| | rows (2023-24 RS) | avg minutes |
|---|---|---|
| position NOT NULL | 24,600 | 30.89 |
| position NULL | 40,170 | 15.16 |

24,600 = 1,230 games x 2 teams x 10. **That column marks starters, not positions.** It is populated only for the five starters per team, which is exactly what fitengine's `derive_starters` uses it for. It is not a position source and must not be used as one.

`nba_player_bio.position` covers the Scenario A candidate pool completely. Of the 148 distinct players with a Regular Season since 2009-10 at `usg_pct >= 0.28`:

| candidates | missing bio row | blank position |
|---|---|---|
| 148 | **0** | **0** |

Distribution: Guard 73, Forward 36, Center 11, Forward-Center 10, Guard-Forward 7, Center-Forward 6, Forward-Guard 5.

All Scenario A and Scenario B seed arrivals resolve, and resolve correctly:

| Player | position | | Player | position |
|---|---|---|---|---|
| LaMelo Ball | Guard | | Kawhi Leonard | Forward |
| Anthony Edwards | Guard | | Paul George | Forward |
| Damian Lillard | Guard | | Khris Middleton | Forward |
| Kyrie Irving | Guard | | Ben Simmons | **Guard-Forward** |
| James Harden | Guard | | Lonzo Ball | Guard |
| Russell Westbrook | Guard | | John Wall | Guard |
| Chris Paul | Guard | | Zach LaVine | Guard |
| Donovan Mitchell | Guard | | De'Aaron Fox | Guard |
| Bradley Beal | Guard | | Dejounte Murray | Guard |

**Caveat that must reach TRIPWIRES.md:** this is a career-static label. A player who moved between guard and forward across a 15-year career carries one label for all of it. For Scenario A this is tolerable because every core seed arrival is an unambiguous guard, and the spec already routes high-usage non-guards (Anthony, Butler, Towns) to a separate robustness-only class. But the spec's own instruction that "filter sensitivity must be reported" applies here: `pos_group='G'` resolving to `position IN ('Guard','Guard-Forward','Forward-Guard')` is a choice, and Ben Simmons sits on it.

## 4. Era boundaries and coverage, 2009-10 to 2025-26

### Play-by-play format (matters for stint reconstruction)

| Season | source | games | pbp rows |
|---|---|---|---|
| 2009-10 to 2024-25 | **`stats_api` only** | full | ~1.1M to 1.2M per season |
| 2025-26 | `cdn` | 729 | 828,202 |
| 2025-26 | `stats_api` | 501 | 515,574 |

```sql
SELECT RIGHT(g.season_id::text,4) AS season_start, p.source,
       COUNT(DISTINCT p.game_id) AS games, COUNT(*) AS pbp_rows
FROM nba.nba_play_by_play p JOIN nba.nba_games g ON g.game_id = p.game_id
WHERE LEFT(g.season_id::text,1) = '2' GROUP BY 1,2 ORDER BY 1,2;
```

Two consequences.

**The whole backtest window through 2024-25 is 100% legacy (`stats_api`) format.** fitengine's G1 panel reports the legacy stratum at `recon_rate_TRUE_0p5 = 0.998410` over 14,940 games. That 14,940 / 729 legacy / live split reconciles exactly with the 729 `cdn` games above, which confirms the two counts are measuring the same thing.

**Only 2025-26 is mixed**, and it is mixed per game, not per season. Any code branching on season prefix is wrong. This is the season LaMelo's live vectors come from.

### Team-game and player-game coverage

`nba_games` (team-game grain, `season_id` prefix 1 = preseason, 2 = regular season, 4 = playoffs):

| Season | RS team-game rows | RS games |
|---|---|---|
| 2009-10 | 2,460 | 1,230 |
| 2010-11 | 2,460 | 1,230 |
| 2011-12 | 1,980 | **990** (lockout) |
| 2012-13 | 2,458 | **1,229** |
| 2013-14 to 2018-19 | 2,460 | 1,230 |
| 2019-20 | 2,118 | **1,059** (COVID) |
| 2020-21 | 2,160 | **1,080** (short season) |
| 2021-22 to 2025-26 | 2,460 | 1,230 |

The short seasons are real, not gaps. 2012-13 is 1,229 because of the cancelled Celtics-Pacers game (Boston Marathon).

### Transactions era boundary

| Year | rows |
|---|---|
| 2015 | 499 (first date 2015-07-01) |
| 2016 to 2025 | 690 to 1,038 per year |
| 2026 | 547 (partial) |

**Hard floor at 2015-07-01.** See gap register G2; this is smaller than it looks.

### Tracking era boundary

`nba_player_tracking_game` covers **2013-14 through 2025-26**, complete: 1,230 RS games every full season, ~62k to 65k player-game rows per season, plus playoffs.

## 5. SPACE-ANT: the reliability curve is not buildable (feeds G4)

The spec defines SPACE-ANT as "catch-and-shoot three-point attempts per 100 and wide-open three frequency."

**Wide-open / defender-distance data does not exist anywhere in the warehouse.** A search of every column in every table for wide / open / defender / closest / touch_time / dribble semantics returns exactly one hit:

```
nba_boxscore_matchups.percentage_defender_total_time
```

which is a matchup time share, not a defender distance. So "wide-open three frequency" has **no source**. Not thin. Absent.

**Catch-and-shoot exists, but only at season grain.** `nba_player_tracking_season` (`measure_type='CatchShoot'`, 2013-14+) has `catch_shoot_fg3m`, `catch_shoot_fg3a`, `catch_shoot_fg3_pct`. Season grain cannot produce an r(N) curve, because r(N) requires splitting a season at game N into early and rest.

**Game grain has no three-point split.** `nba_player_tracking_game` (2013-14+, complete) carries `contested_fgm/fga/fg_pct`, `uncontested_fgm/fga/fg_pct`, `defended_at_rim_*`. All of these are **all-shots**, with no `fg3` variant anywhere in the table's 38 columns.

So at game grain the best available proxy is `uncontested_fga`, which is (a) not restricted to threes and (b) "uncontested" rather than "wide open," which are different tracking definitions.

**Verdict: SPACE-ANT cannot pass the Phase 1 reliability gate, because the r(N) curve it would be gated on cannot be computed at all.** It survives as a season-grain descriptive only. Since the spec already labels SPACE-ANT "ARM-S, diagnostic," moving it to dashboard-only costs one diagnostic and no wire. Recorded as G4.

## 6. minutes_float nulls are DNPs, confirmed

Load-bearing, because the stint spike's primary criterion (`recon_rate_TRUE_0p5`) is scored against `nba_player_advanced_stats.minutes_float`, and that column is 17-19% NULL in every season. If those nulls were data loss, the spike's denominator would be wrong.

They are not. 2013-14 RS:

| minutes_float NULL | rows | no box row | has DNP comment | adv minutes blank |
|---|---|---|---|---|
| False | 51,236 | 0 | 0 | 0 |
| True | 11,520 | **11,520** | **11,520** | **11,520** |

Every single null row has no box-score row, carries a DNP comment, and has a blank minutes string. The correspondence is exact, not approximate. Nulls are precisely the players who did not play.

51,236 played player-games / 1,230 games = 41.7 per game, or 20.8 per team. That is the right number of players who see the floor in an NBA game.

## 7. Orphan PBP game_ids: none are in scope

12 game_ids have play-by-play but no `nba_games` row. All 12 are 2025-26, and **none are regular-season**:

| prefix | game_ids | meaning |
|---|---|---|
| `003` | 0032500004, ...05, ...06, ...21, ...31, ...41 | All-Star |
| `005` | 0052500101, ...121, ...131, ...201, ...211 | Play-In |
| `006` | 0062500001 | NBA Cup final |

The reference class is built from `002` regular-season games. **Zero orphans fall in the reference-class window.** This is a non-issue for the tripwire backtest, though it is a real warehouse gap worth logging elsewhere.

## 8. What this report does not answer

- Whether stint reconstruction is trustworthy before 2013-14. That is the Step 2 spike.
- Whether the seed cases extract with labels. Phase 0 checks lookup-level resolution only; full extraction is Phase 2.
- Whether any candidate metric stabilizes. That is Phase 1, and it has not run.

## 9. Amendments this report forces on the spec

| Spec location | Change |
|---|---|
| Section 7, Scenario A query | `usg_pct >= 28.0` becomes `>= 0.28`. Add a non-empty assertion. |
| Section 7, Scenario A query | `s0.minutes >= 1200` has no source column; derive from `SUM(minutes_float)`. |
| Section 7, Scenario A query | `s1.pos_group = 'G'` becomes a join to `nba_player_bio.position IN ('Guard','Guard-Forward','Forward-Guard')`, declared career-static. |
| Section 5, wire library | SPACE-ANT moves to dashboard-only. Reason is data availability, not judgement. |
| Section 3, era window | Pending the Step 2 spike. Do not amend yet. |
