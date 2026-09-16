# Provenance appendix

Assembled 2026-09-16T19:58:40.286268+00:00

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
| kuminga\data\roster_snapshot_2026_27.csv               | 516    | build_roster_snapshot        | build_roster_snapshot_20260827T031702Z        | ok       |
| kuminga\data\roster_snapshot_discrepancies.csv         | 12     | build_roster_snapshot        | build_roster_snapshot_20260827T031702Z        | ok       |
| kuminga\data\transaction_supplement.csv                | 9      | build_transaction_supplement | build_transaction_supplement_20260827T123728Z | ok       |
| kuminga\outputs\baseline_decomposition.csv             | 4      | baseline_decomp              | baseline_decomp_20260827T124626Z              | ok       |
| kuminga\outputs\C2_moves_ceiling_vs_not.csv            | 8      | compare_ceiling              | compare_ceiling_20260827T131315Z              | ok       |
| kuminga\outputs\C2_teams_ceiling_vs_not.csv            | 30     | compare_ceiling              | compare_ceiling_20260827T131315Z              | ok       |
| kuminga\outputs\apron_reconcile_all30.csv              | 30     | apron_reconcile_all30        | apron_reconcile_all30_20260827T191607Z        | ok       |
| kuminga\data\roster_snapshot_2026_27_v2.csv            | 622    | build_roster_v2              | build_roster_v2_20260827T201556Z              | ok       |
| kuminga\outputs\roster_v2_gates.csv                    | 30     | roster_v2_gates              | roster_v2_gates_20260827T201557Z              | ok       |
| kuminga\data\roster_snapshot_2026_27_v3.csv            | 622    | build_roster_v3              | build_roster_v3_20260903T230731Z              | ok       |
| kuminga\data\spotrac_anchors_2026_27_v3.csv            | 30     | build_roster_v3              | build_roster_v3_20260903T230731Z              | ok       |
| kuminga\outputs\backtest_calibration.csv               | 90     | backtest_calibration         | backtest_calibration_20260903T235222Z         | ok       |
| kuminga\outputs\backtest_calibration_summary.csv       | 3      | backtest_calibration         | backtest_calibration_20260903T235222Z         | ok       |
| kuminga\outputs\cap_branches.csv                       | 6      | cap_branches                 | cap_branches_20260904T013155Z                 | ok       |
| kuminga\outputs\cap_branches.md                        |        | cap_branches                 | cap_branches_20260904T013155Z                 | ok       |
| kuminga\outputs\dosunmu_cap.csv                        | 6      | dosunmu_cap                  | dosunmu_cap_20260904T013155Z                  | ok       |
| kuminga\outputs\spacing_table.csv                      | 2      | spacing_table                | spacing_table_20260904T013159Z                | ok       |
| kuminga\outputs\spacing_teams.csv                      | 30     | spacing_table                | spacing_table_20260904T013159Z                | ok       |
| kuminga\outputs\figures\fig1_attribution_waterfall.png |        | build_figures                | build_figures_20260904T013215Z                | ok       |
| kuminga\outputs\figures\fig2_west_before_after.png     |        | build_figures                | build_figures_20260904T013215Z                | ok       |
| kuminga\outputs\figures\fig4_seed_distribution.png     |        | build_figures                | build_figures_20260904T013215Z                | ok       |
| kuminga\outputs\figures\fig3_scenario_fan.png          |        | build_figures                | build_figures_20260904T013215Z                | ok       |
| kuminga\outputs\lineup_evidence.csv                    | 10     | lineup_evidence              | lineup_evidence_20260904T013228Z              | ok       |
| kuminga\outputs\kuminga_shot_profile.csv               | 8      | lineup_evidence              | lineup_evidence_20260904T013228Z              | ok       |
| kuminga\outputs\roster_v3_gates.csv                    | 30     | roster_v3_gates              | roster_v3_gates_20260904T013842Z              | ok       |
| kuminga\outputs\cap_reconciliation.csv                 | 8      | cap_reconciliation           | cap_reconciliation_20260904T013922Z           | ok       |
| kuminga\outputs\cap_branches_canonical.csv             | 6      | cap_reconciliation           | cap_reconciliation_20260904T013922Z           | ok       |
| kuminga\outputs\cap_reconciliation.md                  |        | cap_reconciliation           | cap_reconciliation_20260904T013922Z           | ok       |
| kuminga\outputs\green_resolution.csv                   | 16     | green_resolution             | green_resolution_20260904T014022Z             | ok       |
| kuminga\outputs\green_resolution.md                    |        | green_resolution             | green_resolution_20260904T014022Z             | ok       |
| kuminga\outputs\green_asset_cost.csv                   | 1      | green_resolution             | green_resolution_20260904T014022Z             | ok       |
| kuminga\outputs\cap_canonical.json                     |        | green_resolution             | green_resolution_20260904T014022Z             | ok       |
| kuminga\outputs\dosunmu_final_states.csv               | 9      | dosunmu_final_states         | dosunmu_final_states_20260904T014033Z         | ok       |
| kuminga\outputs\coherence_checks.csv                   | 4      | build_outputs                | build_outputs_20260909T214647Z                | ok       |
| kuminga\outputs\T1_all30_before_after.csv              | 30     | build_outputs                | build_outputs_20260909T214647Z                | ok       |
| kuminga\outputs\T2_west_ranking.csv                    | 15     | build_outputs                | build_outputs_20260909T214647Z                | ok       |
| kuminga\outputs\PROVENANCE.csv                         | 85     | build_outputs                | build_outputs_20260909T214647Z                | ok       |
| kuminga\outputs\canonical_figures.csv                  | 4      | reconcile_figures            | reconcile_figures_20260909T214648Z            | ok       |
| kuminga\outputs\canonical_figures.md                   |        | reconcile_figures            | reconcile_figures_20260909T214648Z            | ok       |
| kuminga\outputs\w1_verdict_comparison.csv              | 6      | w1_compare                   | w1_compare_20260909T214729Z                   | ok       |
| kuminga\outputs\w1c_delta_decomposition.csv            | 4      | w1c_decompose                | w1c_decompose_20260910T032423Z                | ok       |
| kuminga\outputs\aging_curve.csv                        | 20     | aging_curve                  | aging_curve_20260910T032614Z                  | ok       |
| kuminga\outputs\aging_applied.csv                      | 974    | aging_curve                  | aging_curve_20260910T032614Z                  | ok       |
| kuminga\outputs\market_devig_2026_27.csv               | 30     | market_devig                 | market_devig_20260910T032751Z                 | ok       |
| kuminga\outputs\champions_h1.csv                       | 3      | champions_table              | champions_table_20260910T033202Z              | ok       |
| kuminga\outputs\champions_h2_base_rates.csv            | 1      | champions_table              | champions_table_20260910T033202Z              | ok       |
| kuminga\outputs\final_numbers.md                       |        | build_final_numbers          | build_final_numbers_20260910T040503Z          | ok       |
| kuminga\outputs\final_numbers.csv                      | 80     | build_final_numbers          | build_final_numbers_20260910T040503Z          | ok       |
| kuminga\outputs\f1_disagreement_ranking.csv            | 20     | f1_disagreement_diagnosis    | f1_disagreement_diagnosis_20260910T132650Z    | ok       |
| kuminga\outputs\f1_rollup_decomposition.csv            | 80     | f1_disagreement_diagnosis    | f1_disagreement_diagnosis_20260910T132650Z    | ok       |
| kuminga\outputs\f4a_per_view_disagreement.csv          | 30     | f4_per_view_disagreement     | f4_per_view_disagreement_20260910T134902Z     | ok       |
| kuminga\outputs\f4b_tail_players.csv                   | 46     | f4_per_view_disagreement     | f4_per_view_disagreement_20260910T134902Z     | ok       |
| kuminga\outputs\f4c_top_heaviness.csv                  | 30     | f4_per_view_disagreement     | f4_per_view_disagreement_20260910T134902Z     | ok       |
| kuminga\outputs\f4d_topheaviness_series.csv            | 2      | f4d_topheaviness_series      | f4d_topheaviness_series_20260910T135054Z      | ok       |
| kuminga\outputs\m1_style_features.csv                  | 90     | m1_style_model               | m1_style_model_20260910T135427Z               | ok       |
| kuminga\outputs\m1_style_model_fit.csv                 | 3      | m1_style_model               | m1_style_model_20260910T135427Z               | ok       |
| kuminga\outputs\n2_path.csv                            | 4      | n2_path                      | n2_path_20260910T140443Z                      | ok       |
| kuminga\outputs\n2_round1_opponents.csv                | 14     | n2_path                      | n2_path_20260910T140443Z                      | ok       |
| kuminga\outputs\m4_lineups.csv                         | 640    | m4_lineup_study              | m4_lineup_study_20260910T140700Z              | ok       |
| kuminga\outputs\williams_minutes_sensitivity.csv       | 5      | williams_minutes_sensitivity | williams_minutes_sensitivity_20260910T170213Z | ok       |
| kuminga\outputs\noise_floor.csv                        | 8      | noise_floor                  | noise_floor_20260910T170216Z                  | ok       |
| kuminga\outputs\noise_floor_AGED.csv                   | 8      | noise_floor                  | noise_floor_20260910T203737Z                  | ok       |
| kuminga\outputs\w2_aging_gate.csv                      | 14     | w2_aging_gate                | w2_aging_gate_20260910T203830Z                | ok       |
| kuminga\data\roster_snapshot_2026_27_SIM.csv           | 444    | adapt_roster_v3              | adapt_roster_v3_20260916T173213Z              | ok       |
| kuminga\outputs\sim_roster_diff_v1_v3.csv              | 115    | adapt_roster_v3              | adapt_roster_v3_20260916T173213Z              | ok       |
| kuminga\outputs\rotations_2026_27.csv                  | 600    | build_rotations              | build_rotations_20260916T173214Z              | ok       |
| kuminga\outputs\minutes_rank_curve.csv                 | 10     | build_rotations              | build_rotations_20260916T173214Z              | ok       |
| kuminga\outputs\rookie_priors.csv                      | 60     | build_rotations              | build_rotations_20260916T173214Z              | ok       |
| kuminga\outputs\player_pool_2026_27.csv                | 974    | build_rotations              | build_rotations_20260916T173214Z              | ok       |
| kuminga\outputs\team_pool_shares.csv                   | 30     | build_rotations              | build_rotations_20260916T173214Z              | ok       |
| kuminga\outputs\team_strengths_2026_27.csv             | 120    | build_strengths              | build_strengths_20260916T173218Z              | ok       |
| kuminga\outputs\sim_all30_2026_27.csv                  | 120    | run_sim                      | run_sim_20260916T173222Z                      | ok       |
| kuminga\outputs\h4_knicks_case_file.csv                | 45     | h4_knicks_case_file          | h4_knicks_case_file_20260916T190540Z          | ok       |
| kuminga\docs\case_file_knicks_2025_26.md               |        | h4_knicks_case_file          | h4_knicks_case_file_20260916T190540Z          | ok       |
| kuminga\outputs\fcurve_min.part_consensus.csv          | 29     | build_fcurve                 | build_fcurve_20260916T173840Z                 | ok       |
| kuminga\outputs\fcurve_min.part_box.csv                | 29     | build_fcurve                 | build_fcurve_20260916T173840Z                 | ok       |
| kuminga\outputs\fcurve_min.part_darko.csv              | 29     | build_fcurve                 | build_fcurve_20260916T173840Z                 | ok       |
| kuminga\outputs\fcurve_min.part_rapm.csv               | 29     | build_fcurve                 | build_fcurve_20260916T173840Z                 | ok       |
| kuminga\outputs\fcurve_min.csv                         | 116    | merge_fcurve_parts           | merge_fcurve_parts_20260916T195816Z           | ok       |
| kuminga\outputs\shapley_min.csv                        | 8      | shapley                      | shapley_20260916T195818Z                      | ok       |
| kuminga\outputs\shapley_order_spread.csv               | 32     | shapley                      | shapley_20260916T195818Z                      | ok       |
| kuminga\outputs\shapley_min_POOLED.csv                 | 8      | shapley                      | shapley_20260916T195822Z                      | ok       |
| kuminga\outputs\shapley_order_spread_POOLED.csv        | 32     | shapley                      | shapley_20260916T195822Z                      | ok       |
| kuminga\outputs\S1_shapley_slot_comparison.csv         | 8      | compare_slot_shapley         | compare_slot_shapley_20260916T195824Z         | ok       |
| kuminga\outputs\slot_robustness.csv                    | 5      | slot_robustness              | slot_robustness_20260916T195826Z              | ok       |
| kuminga\outputs\slot_constrained.csv                   | 4      | slot_analysis                | slot_analysis_20260916T195828Z                | ok       |
| kuminga\outputs\slot_alternatives.csv                  | 5      | slot_analysis                | slot_analysis_20260916T195828Z                | ok       |
| kuminga\outputs\player_option.csv                      | 9      | player_option                | player_option_20260916T195829Z                | ok       |
| kuminga\outputs\seed_distribution.csv                  | 240    | seed_distribution            | seed_distribution_20260916T195831Z            | ok       |
| kuminga\outputs\scenario_fan.csv                       | 16     | counterfactuals              | counterfactuals_20260916T195835Z              | ok       |
| kuminga\outputs\counterfactual_fives.csv               | 32     | counterfactuals              | counterfactuals_20260916T195835Z              | ok       |
| kuminga\outputs\market_comparison.csv                  | 4      | eval_signing                 | eval_signing_20260916T195836Z                 | ok       |
| kuminga\outputs\par_curves_by_fork.csv                 | 4      | eval_signing                 | eval_signing_20260916T195836Z                 | ok       |
| kuminga\outputs\kuminga_surplus_by_fork.csv            | 8      | eval_signing                 | eval_signing_20260916T195836Z                 | ok       |
| kuminga\outputs\kuminga_cap_gate.json                  |        | eval_signing                 | eval_signing_20260916T195836Z                 | ok       |
| kuminga\outputs\green_kept.csv                         | 1      | green_kept                   | green_kept_20260916T195838Z                   | ok       |
| kuminga\outputs\lede_loophole.csv                      | 10     | lede_loophole                | lede_loophole_20260916T195839Z                | ok       |
| kuminga\outputs\lede_loophole.md                       |        | lede_loophole                | lede_loophole_20260916T195839Z                | ok       |

## External sources

Every externally sourced fact carries its URL in the file that uses it:

- Cap thresholds: `offseason/data/league_year_constants.json`, `source` field per season.
- Kuminga terms and the Hawks option: `kuminga/data/transaction_supplement.csv`, `source_url_1` / `source_url_2`.
- Dead-money resolution: `kuminga/data/dup_resolution_verified.json`, `sources` per player.
- Injuries: `kuminga/data/injuries_2026_27.csv`, `source_url`.
- Traded picks: `kuminga/data/traded_picks_2026_offseason.csv`, `source_url`.
