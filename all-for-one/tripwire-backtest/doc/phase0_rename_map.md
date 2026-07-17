# Phase 0 Rename Map and Parse Acceptance

Tripwire backtest, Phase 0 Step 5. Produced 2026-07-17.

Maps every placeholder name in the spec to the real warehouse, with a status per entry, then reports the parse status of each section 7 query. The spec's stated acceptance ("every query in section 7 parses against the mapped schema") cannot be met as written; this document says why and proposes a revised bar.

## Status legend

- **MAPPED**: clean one-to-one rename, query runs unchanged but for the name.
- **DERIVED**: no single table/column exists; the placeholder is a computation over real tables. Query needs rewriting, not just renaming.
- **BLOCKED**: no source exists; blocked on a gap-register item.
- **RETIRED**: the placeholder is deleted by a Phase 0 redefinition and has no successor query.

## Table rename map

| Spec placeholder | Real object | Status | Note |
|---|---|---|---|
| `team_game` | `nba.nba_games` | MAPPED | Team-game grain. `season_id` prefix: 1 pre, 2 RS, 4 playoff. |
| `player_game` | `nba.nba_player_stats` | MAPPED | `minutes_played` is INTEGER (per-game floor). |
| `player_season` | `nba.nba_player_season_bio` | **DERIVED** | No `minutes` column; derive from `SUM(minutes_float)`. No `position`; join `nba_player_bio`. `usg_pct` is a fraction (see below). |
| `stint` | reconstructed from `nba_play_by_play` | **DERIVED** | No lineup table. Built by fitengine's stint builder into parquet, not Postgres. Feasibility proven to 2010-11 by the Step 2 spike. |
| `stint_player` | reconstructed (stint `lineup_id`) | **DERIVED** | Same. The per-stint parquet carries a `lineup_id` of sorted player ids, not a `stint_player` join table. |
| `honors` | none | **BLOCKED (G1)** | No award data in the warehouse. Blocks Scenario A. |
| `transactions` | `nba.nba_transactions` | MAPPED (partial) | Starts 2015-07-01. Pre-2015 midseason arrivals derived/curated (G2). |
| tracking shot data | `nba.nba_player_tracking_season` (season), `nba_player_tracking_game` (game) | MAPPED (partial) | CatchShoot at season grain only; no wide-open/defender data anywhere (G4). |
| `availability_posterior` | none | **RETIRED (4b)** | pick2033 models draft slots, not availability. AVAIL-PACE redefined onto the warehouse. |
| `availability_posterior_draws` | none | **RETIRED (4b)** | Same. |
| trade model `P_yes` | `partner_acceptance.decide()` | **DERIVED (G5)** | Returns boolean, not a probability. 0.25 floor replaced by boolean verdict + sweetener price. |
| `first_n_games(team, season, n)` | helper view, to build | DERIVED | Buildable from `nba_games` ordered by `game_date`; not yet created. |

## Column rename map (the load-bearing ones)

| Spec placeholder | Real | Status | Note |
|---|---|---|---|
| `player_season.usg_pct >= 28.0` | `nba_player_season_bio.usg_pct >= 0.28` | **DERIVED** | **Scale bug.** Column is a fraction in [0, 0.571]. `>= 28.0` matches zero rows. See coverage report section 1. |
| `player_season.minutes >= 1200` | `SUM(nba_player_advanced_stats.minutes_float)` | **DERIVED** | No minutes column on the season table. |
| `player_season.pos_group = 'G'` | `nba_player_bio.position IN ('Guard','Guard-Forward','Forward-Guard')` | **DERIVED** | Career-static label. `advanced_stats.position` is a starters flag (61% null), not a position. |
| `team_game.drb`, `team_game.opp_orb` | `nba_games.dreb`, and opponent `oreb` via self-join on `game_id` | **DERIVED** | `nba_games` carries only the team's own rebounds per row; opponent ORB requires joining the other team's row for the same game. There is no `opp_orb` column. |
| `player_season.season - 1` join | string arithmetic on `season_year` ('2023-24' to '2022-23') | DERIVED | `season_year` is a text label, not an integer; the prior-season self-join is string manipulation, not `season - 1`. |

## Parse acceptance: results

`EXPLAIN` run against the live schema. The spec's four section 7 query sketches:

| Query | Parse status | Reason |
|---|---|---|
| Reliability curve (team DRB), **as written** | **FAIL** | `opp_orb` column does not exist. |
| Reliability curve (team DRB), **mapped with self-join** | **OK** | Runs once opponent ORB comes from a `game_id` self-join. |
| Shared-floor pair aggregate | **N/A in Postgres** | Reads `stint` / `stint_player`, which live in fitengine's parquet cache, not the warehouse. Parses in DuckDB against the stint load, not here. This is a store mismatch the spec's "PostgreSQL warehouse" framing hides. |
| Scenario A extraction, **without honors** | DERIVED, parses once season-join and usg scale are fixed | The class query can enumerate team-changing high-usage guards, but cannot apply the incumbent filter. |
| Scenario A extraction, **with honors** | **FAIL** | `relation "nba.honors" does not exist`. Blocked on G1. |
| AVAIL-PACE, **original** | **FAIL** | `relation "nba.availability_posterior" does not exist`. Retired by 4b. |
| AVAIL-PACE, **redefined** | **OK** | Games-through-N from `nba_player_stats` joined to `nba_games` parses and runs. |

**So the spec's acceptance bar cannot be met as written.** Two section 7 queries reference tables that do not exist (`honors`, `availability_posterior`), one reads a store this executor does not target (`stint`), and two more fail on column-level mismatches (`opp_orb`, the `usg_pct` scale) that are silent-wrong rather than loud-fail. Editing the queries to parse and then declaring the bar met would hide exactly the gaps this phase exists to surface.

## Proposed revised acceptance bar (for Bobby's ruling)

Replace "every query in section 7 parses" with a three-tier bar that is honest about the gaps:

1. **RUNS NOW**: the query parses and executes against the current warehouse after the documented mapping. (Reliability curve with self-join; AVAIL-PACE redefined.)
2. **RUNS AFTER named ingest**: the query parses and runs once a specific gap-register item lands. (Scenario A extraction after G1 honors ingest; the stint aggregates after the fitengine stint panel is built, feasibility already proven.)
3. **RETIRED**: the query is deleted by a Phase 0 redefinition and has no successor. (AVAIL-PACE original.)

Acceptance is met when every section 7 query is in tier 1, or in tier 2 with its blocking gap-register item costed, or in tier 3 with its redefinition recorded. By that bar, Phase 0 acceptance **is** met: nothing is left unaccounted for. That is the honest version of "every query parses."

## Lookup-level seed resolution (Phase 0 guardrail)

Per the plan, Phase 0 checks only that each seed case resolves to rows through the mapped schema. Full extraction with labels is Phase 2 and does not run here.

**Scenario A core class (12 cases): all resolve.** Each arriving player is found changing teams into the named team in the named season, with a plausible prior-season usage:

| Arriving | Season | Team | GP | prior usg | |
|---|---|---|---|---|---|
| Lillard | 2023-24 | MIL | 73 | 0.274 | resolved |
| Irving | 2022-23 | DAL | 60 | 0.286 | resolved |
| Harden | 2020-21 | BKN | 44 | 0.283 | resolved |
| Harden | 2021-22 | PHI | 65 | 0.266 | resolved |
| Harden | 2023-24 | LAC | 72 | 0.202 | resolved (note: prior usg 0.20, below the 0.28 bar; a genuine class-membership question for Phase 2, not a resolution failure) |
| Westbrook | 2021-22 | LAL | 78 | 0.264 | resolved |
| Paul | 2020-21 | PHX | 70 | 0.221 | resolved (prior usg 0.22, same note) |
| Mitchell | 2022-23 | CLE | 68 | 0.310 | resolved |
| Beal | 2023-24 | PHX | 53 | 0.224 | resolved (same note) |
| Fox | 2024-25 | SAS | 62 | 0.274 | resolved |
| Doncic | 2024-25 | LAL | 50 | 0.328 | resolved **only via player_id** (see below) |
| Murray | 2024-25 | NOP | 31 | 0.263 | resolved |

**Two cases exposed a real join hazard.** Luka Dončić and Kristaps Porziņģis returned zero rows on an exact **name** match, because the warehouse stores them with diacritics (`Luka Dončić`, `Kristaps Porziņģis`) and the seed list spells them ASCII. They resolve immediately on `player_id` (Dončić 1629029, LAL, 50 GP, usg 0.328; Porziņģis 204001, 14 seasons). This confirms the house convention with a concrete failure: **the extraction and all seed reconciliation must join on `nba_player_id`, never on player name.** A name join would silently drop two of the twelve core Scenario A cases, and would do it without erroring, which is the same silent-empty failure mode as the usg_pct scale bug.

**Scenario B availability class: all resolve** (on player_id; the same diacritic caveat applies to Porziņģis, who is a Scenario B seed too). Ben Simmons, John Wall, Irving, LaVine, Porziņģis, Lonzo Ball, Leonard, George, Middleton all have the expected multi-season histories.

**Note surfaced for Phase 2, not resolved here:** several core Scenario A arrivals (Harden-to-Clippers 0.20, Paul-to-Suns 0.22, Beal-to-Suns 0.22) have prior-season usage **below** the spec's 0.28 bar. The spec anticipates this ("filter sensitivity must be reported, since cases like CP3 to Phoenix hinge on it"). It is a class-definition question for Phase 2, not a Phase 0 resolution failure: these players resolve fine; whether they clear the usage filter is exactly the sensitivity the spec wants reported.

## What Phase 0 hands to Phase 1/2

- A mapping that is complete: every placeholder is MAPPED, DERIVED (with the derivation), BLOCKED (with the gap item), or RETIRED (with the redefinition).
- Two hard join rules: join on `nba_player_id`, never name (diacritics); and treat `usg_pct` as a fraction.
- One helper view still to build: `first_n_games`, trivial from `nba_games` ordered by `game_date`.
- The blocking dependency for Phase 2 is G1 (honors). Everything else either runs now or is costed.
