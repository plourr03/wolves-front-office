# Provenance appendix

Assembled 2026-09-03T23:51:40.474026+00:00

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

| artifact                                               | rows   | script                       | run_id                                        | status   |
|:-------------------------------------------------------|:-------|:-----------------------------|:----------------------------------------------|:---------|
| kuminga/data/frozen/wh_a806ee0164f04a3f                |        | freeze_inputs                | freeze_inputs_20260827T015615Z                | ok       |
| kuminga\outputs\team_state_diff_2026_27.csv            | 30     | diff_team_state              | diff_team_state_20260827T020817Z              | ok       |
| offseason\data\nba_contracts_2026_27_verified.csv      | 459    | patch_contracts              | patch_contracts_20260827T021228Z              | ok       |
| kuminga\data\injuries_2026_27.csv                      | 10     | build_injuries               | build_injuries_20260827T021428Z               | ok       |
| kuminga\data\traded_picks_2026_offseason.csv           | 10     | build_pick_ledger            | build_pick_ledger_20260827T021502Z            | ok       |
| kuminga\data\nba_draft_picks_future_2026_08_26.csv     | 617    | build_pick_ledger            | build_pick_ledger_20260827T021502Z            | ok       |
| kuminga/data/frozen/wh_bfebdf122fef9959                |        | freeze_inputs                | freeze_inputs_20260827T022316Z                | ok       |
| kuminga/data/frozen/wh_cffa3359210c1181                |        | freeze_inputs                | freeze_inputs_20260827T022633Z                | ok       |
| kuminga/data/frozen/wh_cf31d54027f4e098                |        | freeze_inputs                | freeze_inputs_20260827T023006Z                | ok       |
| kuminga\data\stints_2025_26.parquet                    | 12608  | build_stints_2026            | build_stints_2026_20260827T023401Z            | ok       |
| kuminga\data\stints_2025_26_games.csv                  | 256    | build_stints_2026            | build_stints_2026_20260827T023401Z            | ok       |
| kuminga\outputs\lineup_evidence.csv                    | 10     | lineup_evidence              | lineup_evidence_20260827T024925Z              | ok       |
| kuminga\outputs\kuminga_shot_profile.csv               | 8      | lineup_evidence              | lineup_evidence_20260827T024925Z              | ok       |
| kuminga\outputs\seed_distribution.csv                  | 240    | seed_distribution            | seed_distribution_20260827T025830Z            | ok       |
| kuminga\data\roster_snapshot_2026_27.csv               | 516    | build_roster_snapshot        | build_roster_snapshot_20260827T031702Z        | ok       |
| kuminga\data\roster_snapshot_discrepancies.csv         | 12     | build_roster_snapshot        | build_roster_snapshot_20260827T031702Z        | ok       |
| kuminga\data\transaction_supplement.csv                | 9      | build_transaction_supplement | build_transaction_supplement_20260827T123728Z | ok       |
| kuminga\outputs\baseline_decomposition.csv             | 4      | baseline_decomp              | baseline_decomp_20260827T124626Z              | ok       |
| kuminga\outputs\backtest_calibration.csv               | 90     | backtest_calibration         | backtest_calibration_20260827T124932Z         | ok       |
| kuminga\outputs\backtest_calibration_summary.csv       | 3      | backtest_calibration         | backtest_calibration_20260827T124932Z         | ok       |
| kuminga\outputs\C2_moves_ceiling_vs_not.csv            | 8      | compare_ceiling              | compare_ceiling_20260827T131315Z              | ok       |
| kuminga\outputs\C2_teams_ceiling_vs_not.csv            | 30     | compare_ceiling              | compare_ceiling_20260827T131315Z              | ok       |
| kuminga\outputs\coherence_checks.csv                   | 4      | build_outputs                | build_outputs_20260827T131629Z                | ok       |
| kuminga\outputs\T1_all30_before_after.csv              | 30     | build_outputs                | build_outputs_20260827T131629Z                | ok       |
| kuminga\outputs\T2_west_ranking.csv                    | 15     | build_outputs                | build_outputs_20260827T131629Z                | ok       |
| kuminga\outputs\PROVENANCE.csv                         | 55     | build_outputs                | build_outputs_20260827T131629Z                | ok       |
| kuminga\outputs\figures\fig1_attribution_waterfall.png |        | build_figures                | build_figures_20260827T131630Z                | ok       |
| kuminga\outputs\figures\fig2_west_before_after.png     |        | build_figures                | build_figures_20260827T131630Z                | ok       |
| kuminga\outputs\figures\fig4_seed_distribution.png     |        | build_figures                | build_figures_20260827T131630Z                | ok       |
| kuminga\outputs\figures\fig3_scenario_fan.png          |        | build_figures                | build_figures_20260827T131630Z                | ok       |
| kuminga\outputs\canonical_figures.csv                  | 4      | reconcile_figures            | reconcile_figures_20260827T131633Z            | ok       |
| kuminga\outputs\canonical_figures.md                   |        | reconcile_figures            | reconcile_figures_20260827T131633Z            | ok       |
| kuminga\outputs\green_kept.csv                         | 1      | green_kept                   | green_kept_20260827T154636Z                   | ok       |
| kuminga\outputs\spacing_table.csv                      | 2      | spacing_table                | spacing_table_20260827T170355Z                | ok       |
| kuminga\outputs\spacing_teams.csv                      | 30     | spacing_table                | spacing_table_20260827T170355Z                | ok       |
| kuminga\outputs\player_option.csv                      | 9      | player_option                | player_option_20260827T174547Z                | ok       |
| kuminga\outputs\apron_reconcile_all30.csv              | 30     | apron_reconcile_all30        | apron_reconcile_all30_20260827T191607Z        | ok       |
| kuminga\outputs\dosunmu_cap.csv                        | 6      | dosunmu_cap                  | dosunmu_cap_20260827T191753Z                  | ok       |
| kuminga\outputs\dosunmu_final_states.csv               | 8      | dosunmu_final_states         | dosunmu_final_states_20260827T191823Z         | ok       |
| kuminga\outputs\cap_reconciliation.csv                 | 8      | cap_reconciliation           | cap_reconciliation_20260827T191905Z           | ok       |
| kuminga\outputs\cap_branches_canonical.csv             | 6      | cap_reconciliation           | cap_reconciliation_20260827T191905Z           | ok       |
| kuminga\outputs\cap_reconciliation.md                  |        | cap_reconciliation           | cap_reconciliation_20260827T191905Z           | ok       |
| kuminga\outputs\cap_branches.csv                       | 6      | cap_branches                 | cap_branches_20260827T192046Z                 | ok       |
| kuminga\outputs\cap_branches.md                        |        | cap_branches                 | cap_branches_20260827T192046Z                 | ok       |
| kuminga\outputs\final_numbers.md                       |        | build_final_numbers          | build_final_numbers_20260827T194229Z          | ok       |
| kuminga\outputs\final_numbers.csv                      | 67     | build_final_numbers          | build_final_numbers_20260827T194229Z          | ok       |
| kuminga\outputs\aging_curve.csv                        | 20     | aging_curve                  | aging_curve_20260827T194419Z                  | ok       |
| kuminga\outputs\aging_applied.csv                      | 988    | aging_curve                  | aging_curve_20260827T194419Z                  | ok       |
| kuminga\outputs\noise_floor.csv                        | 8      | noise_floor                  | noise_floor_20260827T194635Z                  | ok       |
| kuminga\data\roster_snapshot_2026_27_v2.csv            | 622    | build_roster_v2              | build_roster_v2_20260827T201556Z              | ok       |
| kuminga\outputs\roster_v2_gates.csv                    | 30     | roster_v2_gates              | roster_v2_gates_20260827T201557Z              | ok       |
| kuminga\outputs\slot_constrained.csv                   | 4      | slot_analysis                | slot_analysis_20260827T201932Z                | ok       |
| kuminga\outputs\slot_alternatives.csv                  | 5      | slot_analysis                | slot_analysis_20260827T201932Z                | ok       |
| kuminga\data\roster_snapshot_2026_27_v3.csv            | 622    | build_roster_v3              | build_roster_v3_20260903T230731Z              | ok       |
| kuminga\data\spotrac_anchors_2026_27_v3.csv            | 30     | build_roster_v3              | build_roster_v3_20260903T230731Z              | ok       |
| kuminga\outputs\roster_v3_gates.csv                    | 30     | roster_v3_gates              | roster_v3_gates_20260903T230838Z              | ok       |
| kuminga\data\roster_snapshot_2026_27_SIM.csv           | 444    | adapt_roster_v3              | adapt_roster_v3_20260903T231232Z              | ok       |
| kuminga\outputs\sim_roster_diff_v1_v3.csv              | 115    | adapt_roster_v3              | adapt_roster_v3_20260903T231232Z              | ok       |
| kuminga\outputs\rotations_2026_27.csv                  | 600    | build_rotations              | build_rotations_20260903T231304Z              | ok       |
| kuminga\outputs\minutes_rank_curve.csv                 | 10     | build_rotations              | build_rotations_20260903T231304Z              | ok       |
| kuminga\outputs\rookie_priors.csv                      | 60     | build_rotations              | build_rotations_20260903T231304Z              | ok       |
| kuminga\outputs\player_pool_2026_27.csv                | 974    | build_rotations              | build_rotations_20260903T231304Z              | ok       |
| kuminga\outputs\team_pool_shares.csv                   | 30     | build_rotations              | build_rotations_20260903T231304Z              | ok       |
| kuminga\outputs\team_strengths_2026_27.csv             | 120    | build_strengths              | build_strengths_20260903T231402Z              | ok       |
| kuminga\outputs\sim_all30_2026_27.csv                  | 120    | run_sim                      | run_sim_20260903T231420Z                      | ok       |
| kuminga\outputs\green_resolution.csv                   | 15     | green_resolution             | green_resolution_20260903T232731Z             | ok       |
| kuminga\outputs\green_resolution.md                    |        | green_resolution             | green_resolution_20260903T232731Z             | ok       |
| kuminga\outputs\green_asset_cost.csv                   | 1      | green_resolution             | green_resolution_20260903T232731Z             | ok       |
| kuminga\outputs\cap_canonical.json                     |        | green_resolution             | green_resolution_20260903T232731Z             | ok       |
| kuminga\outputs\fcurve_min.csv                         | 116    | build_fcurve                 | build_fcurve_20260903T232055Z                 | ok       |
| kuminga\outputs\scenario_fan.csv                       | 16     | counterfactuals              | counterfactuals_20260903T234956Z              | ok       |
| kuminga\outputs\counterfactual_fives.csv               | 32     | counterfactuals              | counterfactuals_20260903T234956Z              | ok       |
| kuminga\outputs\market_comparison.csv                  | 4      | eval_signing                 | eval_signing_20260903T235026Z                 | ok       |
| kuminga\outputs\par_curves_by_fork.csv                 | 4      | eval_signing                 | eval_signing_20260903T235026Z                 | ok       |
| kuminga\outputs\kuminga_surplus_by_fork.csv            | 8      | eval_signing                 | eval_signing_20260903T235026Z                 | ok       |
| kuminga\outputs\kuminga_cap_gate.json                  |        | eval_signing                 | eval_signing_20260903T235026Z                 | ok       |
| kuminga\outputs\shapley_min.csv                        | 8      | shapley                      | shapley_20260903T235033Z                      | ok       |
| kuminga\outputs\shapley_order_spread.csv               | 32     | shapley                      | shapley_20260903T235033Z                      | ok       |
| kuminga\outputs\shapley_min_POOLED.csv                 | 8      | shapley                      | shapley_20260903T235037Z                      | ok       |
| kuminga\outputs\shapley_order_spread_POOLED.csv        | 32     | shapley                      | shapley_20260903T235037Z                      | ok       |
| kuminga\outputs\S1_shapley_slot_comparison.csv         | 8      | compare_slot_shapley         | compare_slot_shapley_20260903T235104Z         | ok       |
| kuminga\outputs\slot_robustness.csv                    | 5      | slot_robustness              | slot_robustness_20260903T235106Z              | ok       |
| kuminga\outputs\lede_loophole.csv                      | 10     | lede_loophole                | lede_loophole_20260903T235139Z                | ok       |
| kuminga\outputs\lede_loophole.md                       |        | lede_loophole                | lede_loophole_20260903T235139Z                | ok       |

## External sources

Every externally sourced fact carries its URL in the file that uses it:

- Cap thresholds: `offseason/data/league_year_constants.json`, `source` field per season.
- Kuminga terms and the Hawks option: `kuminga/data/transaction_supplement.csv`, `source_url_1` / `source_url_2`.
- Dead-money resolution: `kuminga/data/dup_resolution_verified.json`, `sources` per player.
- Injuries: `kuminga/data/injuries_2026_27.csv`, `source_url`.
- Traded picks: `kuminga/data/traded_picks_2026_offseason.csv`, `source_url`.
