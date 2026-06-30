# Freeze manifest and provenance (Phase 1)

Date written: 2026-06-25. This file fixes the reproducibility anchors before any
fitting. It is the run manifest's root: every later output traces to this freeze.

## Field-freeze

- Field-freeze date: 2026-06-25 (resolved with reviewer: freeze now).
- The 30-team rosters and cap state are frozen as of this date. The field is still
  moving through free agency; a changelog records any re-run and how the answer
  moved. The MIN and CHA rows are re-verified post-trade before use.
- Warehouse access: Postgres `nba_warehouse`, schema `nba`, over Tailscale
  (`100.69.186.94`, LAN `192.168.1.236`), via `postmortem/lib/db.py` and the
  `POSTGRES_*` env vars. Connectivity confirmed 2026-06-25.

## Warehouse fingerprint (as of 2026-06-25)

Row estimates (`pg_class.reltuples`) for the tables the engine reads:

| Table | est. rows |
|---|---|
| nba_play_by_play | 17,288,714 |
| nba_player_advanced_stats | 976,431 |
| nba_player_stats | 786,765 |
| nba_synergy_player_play_types | 104,752 |
| nba_games | 77,480 |
| nba_team_advanced_stats | 77,034 |
| nba_team_rosters | 42,709 |
| nba_transactions | 9,470 |
| nba_player_bio | 2,826 |
| nba_player_contracts | 1,226 |

Coverage: `nba_player_stats` and `nba_player_advanced_stats` span 1996-97 (advanced
from 1997-98) through 2025-26. The 2025-26 season is effectively closed as of the
freeze (last game date 2026-06-13). All four sealed-holdout seasons have full
coverage (1309 to 1314 games each, advanced stats present). The live application
seasons (2023-24, 2024-25, 2025-26) are complete.

Full warehouse snapshot export to versioned parquet is DONE (Phase 2, step 1):
`lamelo/data_pull/freeze_warehouse.py` produced
`lamelo/data/snapshot_2026-06-25/` with nine tables and per-table content hashes.
Snapshot id: **wh_65cf5da7f50c7f62** (see `snapshot_2026-06-25/manifest.json`).
`nba_play_by_play` is excluded by design (17M rows, and pre-2025-26 needs a
possession-normalization shim); possession extraction is a dedicated impact-layer
step. The fingerprint above verifies the export against the warehouse state.

## Three-era temporal partition (fixed before any fitting)

Disjoint blocks, so no fitted component ever touches the sealed gate data:

- FIT era: all seasons EXCEPT the sealed block below. Trains the series logit, the
  net-to-wins mapping, SHAPE (sigma_unobs), the box-score prior, the YoY
  metric-selection test, the aging curve, and the transport priors.
- SEALED retrodiction holdout: 2016-17, 2017-18, 2018-19, 2022-23. Four full-82-game
  non-COVID seasons (the bubble 2019-20 and condensed 2020-21 are excluded as
  unrepresentative for an availability and playoff-sim gate). Used ONLY for the
  final retrodiction gate. The series logit and wins mapping are refit on all
  history minus these four seasons.
- LIVE application: 2023-24, 2024-25, 2025-26 impact feeding the actual LaMelo
  question. A forward prediction, not a backtest; not part of the gate.

## Sealed holdout: the seal

The four sealed seasons are recorded here and MUST be excluded from every fit listed
under the FIT era. Any fitting script reads the sealed list from this manifest and
asserts the seasons are absent from its training set. The seal is verified by a
leakage check before the gate runs. Breaking the seal invalidates the
gate; if a fit accidentally touches a sealed season, that fit is rerun.

## Determinism plan (run manifest fields, populated at Phase 2 start)

- Environment: pinned via a lockfile (to be created at Phase 2 start).
- Seeds: fixed master seed, recorded per run; child seeds derived deterministically.
- Snapshot: the Phase 2 parquet export hash, mapped to this fingerprint.
- Manifest: every output maps to its inputs, code commit, seed, and this freeze.

## Status

Phase 1 freeze complete: field-freeze date set, warehouse fingerprinted, three-era
partition fixed, holdout sealed. The pre-registration (`preregistration.md`) is
DRAFT pending four reviewer decisions (games-played band, win-total band, on/off
accept, survival-fraction downside). No modeling code and no title number were
produced in Phase 1.
