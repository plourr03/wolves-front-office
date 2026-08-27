# Provenance appendix

Assembled 2026-08-27T02:46:20.932361+00:00

## Frozen warehouse snapshot

- **Snapshot id:** `wh_cf31d54027f4e098`
- **Frozen at:** 2026-08-27T02:31:21.257819+00:00
- **Source:** nba_warehouse schema nba (read-only)

| Table | Rows | sha256 (first 16) |
|---|---|---|
| `contracts` | 1,070 | `13f4bbda102234a7` |
| `transactions` | 9,849 | `0a41feff88c20533` |
| `rosters_2025_26` | 530 | `61e88ea5587b3dc8` |
| `player_games` | 28,572 | `34adbe7efd37c08c` |
| `player_games_adv` | 34,587 | `0e242b0cf363e9ff` |
| `team_games` | 2,772 | `47bbd20da894f0ad` |
| `team_net` | 283 | `d16b6060e21b1740` |
| `player_bio` | 2,860 | `9c7d1f0b550d4d0e` |

## Artifacts and the runs that produced them

| artifact                                           | rows   | script                       | run_id                                        | status   |
|:---------------------------------------------------|:-------|:-----------------------------|:----------------------------------------------|:---------|
| kuminga\data\transaction_supplement.csv            | 5      | build_transaction_supplement | build_transaction_supplement_20260827T015411Z | ok       |
| kuminga/data/frozen/wh_a806ee0164f04a3f            |        | freeze_inputs                | freeze_inputs_20260827T015615Z                | ok       |
| kuminga\outputs\team_state_diff_2026_27.csv        | 30     | diff_team_state              | diff_team_state_20260827T020817Z              | ok       |
| offseason\data\nba_contracts_2026_27_verified.csv  | 459    | patch_contracts              | patch_contracts_20260827T021228Z              | ok       |
| kuminga\data\roster_snapshot_2026_27.csv           | 516    | build_roster_snapshot        | build_roster_snapshot_20260827T021240Z        | ok       |
| kuminga\data\roster_snapshot_discrepancies.csv     | 12     | build_roster_snapshot        | build_roster_snapshot_20260827T021240Z        | ok       |
| kuminga\data\injuries_2026_27.csv                  | 10     | build_injuries               | build_injuries_20260827T021428Z               | ok       |
| kuminga\data\traded_picks_2026_offseason.csv       | 10     | build_pick_ledger            | build_pick_ledger_20260827T021502Z            | ok       |
| kuminga\data\nba_draft_picks_future_2026_08_26.csv | 617    | build_pick_ledger            | build_pick_ledger_20260827T021502Z            | ok       |
| kuminga/data/frozen/wh_bfebdf122fef9959            |        | freeze_inputs                | freeze_inputs_20260827T022316Z                | ok       |
| kuminga/data/frozen/wh_cffa3359210c1181            |        | freeze_inputs                | freeze_inputs_20260827T022633Z                | ok       |
| kuminga/data/frozen/wh_cf31d54027f4e098            |        | freeze_inputs                | freeze_inputs_20260827T023006Z                | ok       |
| kuminga\outputs\team_strengths_2026_27.csv         | 120    | build_strengths              | build_strengths_20260827T023202Z              | ok       |
| kuminga\outputs\rotations_2026_27.csv              | 600    | build_rotations              | build_rotations_20260827T023548Z              | ok       |
| kuminga\outputs\minutes_rank_curve.csv             | 10     | build_rotations              | build_rotations_20260827T023548Z              | ok       |
| kuminga\outputs\rookie_priors.csv                  | 60     | build_rotations              | build_rotations_20260827T023548Z              | ok       |
| kuminga\outputs\player_pool_2026_27.csv            | 988    | build_rotations              | build_rotations_20260827T023548Z              | ok       |
| kuminga\outputs\cap_branches.csv                   | 6      | cap_branches                 | cap_branches_20260827T023847Z                 | ok       |
| kuminga\outputs\cap_branches.md                    |        | cap_branches                 | cap_branches_20260827T023847Z                 | ok       |
| kuminga\outputs\sim_all30_2026_27.csv              | 120    | run_sim                      | run_sim_20260827T023247Z                      | ok       |
| kuminga\outputs\par_curves_by_fork.csv             | 4      | eval_signing                 | eval_signing_20260827T024047Z                 | ok       |
| kuminga\outputs\kuminga_surplus_by_fork.csv        | 8      | eval_signing                 | eval_signing_20260827T024047Z                 | ok       |
| kuminga\outputs\kuminga_cap_gate.json              |        | eval_signing                 | eval_signing_20260827T024047Z                 | ok       |
| kuminga\outputs\player_option.csv                  | 9      | player_option                | player_option_20260827T024131Z                | ok       |
| kuminga\outputs\T1_all30_before_after.csv          | 30     | build_outputs                | build_outputs_20260827T024552Z                | ok       |
| kuminga\outputs\T2_west_ranking.csv                | 15     | build_outputs                | build_outputs_20260827T024552Z                | ok       |
| kuminga\outputs\PROVENANCE.csv                     | 24     | build_outputs                | build_outputs_20260827T024552Z                | ok       |

## External sources

Every externally sourced fact carries its URL in the file that uses it:

- Cap thresholds: `offseason/data/league_year_constants.json`, `source` field per season.
- Kuminga terms and the Hawks option: `kuminga/data/transaction_supplement.csv`, `source_url_1` / `source_url_2`.
- Dead-money resolution: `kuminga/data/dup_resolution_verified.json`, `sources` per player.
- Injuries: `kuminga/data/injuries_2026_27.csv`, `source_url`.
- Traded picks: `kuminga/data/traded_picks_2026_offseason.csv`, `source_url`.
