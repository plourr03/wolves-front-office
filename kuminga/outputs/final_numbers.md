# Final numbers, piece 2

*Run `build_final_numbers_20260919T234738Z`. 866 figures, every one with a run ID. Anything not here does not go in the piece.*

## 1. The number

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `title` | MIN title probability, mean of four views | 1.68% | MODELED | QUOTABLE AS BAND | `run_sim_20260919T163222Z` |
| `title_lo` | four-view low | 0.86% | MODELED | QUOTABLE AS BAND | `run_sim_20260919T163222Z` |
| `title_hi` | four-view high | 2.59% | MODELED | QUOTABLE AS BAND | `run_sim_20260919T163222Z` |
| `title_aged` | MIN title probability, mean of four views_aged | 2.39% | MODELED | QUOTABLE AS BAND | `run_sim_20260919T195138Z` |
| `title_lo_aged` | four-view low_aged | 1.18% | MODELED | QUOTABLE AS BAND | `run_sim_20260919T195138Z` |
| `title_hi_aged` | four-view high_aged | 3.59% | MODELED | QUOTABLE AS BAND | `run_sim_20260919T195138Z` |
| `mkt_min` | MIN market title odds, proportional de-vig | 3.16% | OBSERVED | QUOTABLE | `market_devig_20260919T195044Z` |
| `mkt_min_rank` | MIN market rank | 6 | OBSERVED | QUOTABLE | `market_devig_20260919T195044Z` |
| `model_min_rank` | MIN model rank | 15 | MODELED | QUOTABLE | `market_devig_20260919T195044Z` |
| `overround` | six-book overround | 21.8% | OBSERVED | FACT | `market_devig_20260919T195044Z` |
| `rankcorr_lo` | model-market rank correlation, lowest view | 0.78 | COMPOSED | QUOTABLE AS BAND | `market_devig_20260919T195044Z` |
| `rankcorr_hi` | model-market rank correlation, highest view | 0.83 | COMPOSED | QUOTABLE AS BAND | `market_devig_20260919T195044Z` |
| `n_disagree` | teams where model and market differ by more than 0.5 points | 20 | COMPOSED | QUOTABLE | `market_devig_20260919T195044Z` |
| `n_allviews` | of those, disagreements where all four views sit on one side | 16 | COMPOSED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `min_view_ranks` | MIN rank in each view | 13 to 16 | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `rankcorr_lo_aged` | model-market rank correlation, lowest view, aged | 0.73 | COMPOSED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260919T232922Z` |
| `rankcorr_hi_aged` | model-market rank correlation, highest view, aged | 0.82 | COMPOSED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260919T232922Z` |
| `n_disagree_aged` | disagreements over 0.5 points, aged | 19 | COMPOSED | QUOTABLE | `r5_honesty_rail_bases_20260919T232922Z` |
| `n_allviews_aged` | of those, all-views, aged | 15 | COMPOSED | QUOTABLE | `r5_honesty_rail_bases_20260919T232922Z` |
| `min_view_ranks_aged` | MIN rank in each view, aged | 9 to 15 | MODELED | QUOTABLE | `r5_honesty_rail_bases_20260919T232922Z` |
| `min_label_aged` | MIN disagreement label, aged | mixed | MODELED | QUOTABLE | `r5_honesty_rail_bases_20260919T232922Z` |
| `min_above_aged` | MIN views above the market, aged | 1 | MODELED | QUOTABLE | `r5_honesty_rail_bases_20260919T232922Z` |
| `min_box_aged` | MIN box view, aged | 3.03% | MODELED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260919T232922Z` |
| `min_darko_aged` | MIN DARKO view, aged | 3.59% | MODELED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260919T232922Z` |
| `model_bos_aged` | BOS model title odds, mean of four views, aged | 14.23% | MODELED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260919T232922Z` |
| `bos_label_aged` | BOS disagreement label, aged | all-views | MODELED | QUOTABLE | `r5_honesty_rail_bases_20260919T232922Z` |
| `model_bos` | BOS model title odds | 18.33% | MODELED | QUOTABLE AS BAND | `market_devig_20260919T195044Z` |
| `mkt_bos` | BOS market title odds | 5.47% | OBSERVED | QUOTABLE | `market_devig_20260919T195044Z` |
| `model_sas` | SAS model title odds | 13.85% | MODELED | QUOTABLE AS BAND | `market_devig_20260919T195044Z` |
| `mkt_sas` | SAS market title odds | 22.96% | OBSERVED | QUOTABLE | `market_devig_20260919T195044Z` |
| `model_cha` | CHA model title odds | 3.44% | MODELED | QUOTABLE AS BAND | `market_devig_20260919T195044Z` |
| `mkt_cha` | CHA market title odds | 0.81% | OBSERVED | QUOTABLE | `market_devig_20260919T195044Z` |
| `bos_dec_threshold` | Boston December (game 30) threshold, net per 100 | -1.7 | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `bos_dec_game` | December checkpoint game | 30 | ASSUMED | FACT | `n8_watch_list_20260919T233400Z` |
| `bos_range_lo` | Boston model net range low | +3.3 | MODELED | QUOTABLE AS BAND | `n8_watch_list_20260919T233400Z` |
| `bos_range_hi` | Boston model net range high | +10.1 | MODELED | QUOTABLE AS BAND | `n8_watch_list_20260919T233400Z` |
| `dec_noise` | 30-game net rating noise per 100 | 3.1 | OBSERVED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `v_ball_in_pooled_u` | LaMelo Ball in, pooled un-aged mean pp | +0.79 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ball_in_pooled_a` | LaMelo Ball in, pooled aged mean pp | +0.91 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ball_in_tr_u` | LaMelo Ball in, team-rank un-aged mean pp | +1.56 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ball_in_tr_a` | LaMelo Ball in, team-rank aged mean pp | +1.58 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ball_in_cells` | LaMelo Ball in, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ball_in_two_cell` | LaMelo Ball in ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ball_in_label` | verdict label | LaMelo Ball in | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_ball_in_u` | LaMelo Ball in, un-aged mean pp | +0.79 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ball_in_a` | LaMelo Ball in, aged mean pp | +0.91 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ball_in_clear` | LaMelo Ball in, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ball_in_signs` | LaMelo Ball in, sign un-aged / aged | all positive / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ball_in_ships` | LaMelo Ball in ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ball_in_preship` | LaMelo Ball in shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_reid_out_pooled_u` | Naz Reid out, pooled un-aged mean pp | -0.33 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_reid_out_pooled_a` | Naz Reid out, pooled aged mean pp | -0.40 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_reid_out_tr_u` | Naz Reid out, team-rank un-aged mean pp | -1.03 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_reid_out_tr_a` | Naz Reid out, team-rank aged mean pp | -1.05 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_reid_out_cells` | Naz Reid out, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_reid_out_two_cell` | Naz Reid out ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_reid_out_label` | verdict label | Naz Reid out | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_reid_out_u` | Naz Reid out, un-aged mean pp | -0.33 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_reid_out_a` | Naz Reid out, aged mean pp | -0.40 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_reid_out_clear` | Naz Reid out, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_reid_out_signs` | Naz Reid out, sign un-aged / aged | all negative / all negative | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_reid_out_ships` | Naz Reid out ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_reid_out_preship` | Naz Reid out shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_other_departures_pooled_u` | Other departures (a bundle of seven), pooled un-aged mean pp | +0.29 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_other_departures_pooled_a` | Other departures (a bundle of seven), pooled aged mean pp | +0.61 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_other_departures_tr_u` | Other departures (a bundle of seven), team-rank un-aged mean pp | -0.87 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_other_departures_tr_a` | Other departures (a bundle of seven), team-rank aged mean pp | -0.22 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_other_departures_cells` | Other departures (a bundle of seven), views clearing in the four cells | 3/4, 3/4, 3/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_other_departures_two_cell` | Other departures (a bundle of seven) ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_other_departures_label` | verdict label | Other departures (a bundle of seven) | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_other_departures_u` | Other departures (a bundle of seven), un-aged mean pp | +0.29 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_other_departures_a` | Other departures (a bundle of seven), aged mean pp | +0.61 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_other_departures_clear` | Other departures (a bundle of seven), views clearing the floor un-aged / aged | 3/4, 3/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_other_departures_signs` | Other departures (a bundle of seven), sign un-aged / aged | mixed / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_other_departures_ships` | Other departures (a bundle of seven) ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_other_departures_preship` | Other departures (a bundle of seven) shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_randle_out_pooled_u` | Julius Randle out, pooled un-aged mean pp | -0.04 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_randle_out_pooled_a` | Julius Randle out, pooled aged mean pp | +0.19 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_randle_out_tr_u` | Julius Randle out, team-rank un-aged mean pp | -0.53 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_randle_out_tr_a` | Julius Randle out, team-rank aged mean pp | -0.11 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_randle_out_cells` | Julius Randle out, views clearing in the four cells | 4/4, 3/4, 3/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_randle_out_two_cell` | Julius Randle out ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_randle_out_label` | verdict label | Julius Randle out | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_randle_out_u` | Julius Randle out, un-aged mean pp | -0.04 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_randle_out_a` | Julius Randle out, aged mean pp | +0.19 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_randle_out_clear` | Julius Randle out, views clearing the floor un-aged / aged | 4/4, 3/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_randle_out_signs` | Julius Randle out, sign un-aged / aged | mixed / mixed | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_randle_out_ships` | Julius Randle out ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_randle_out_preship` | Julius Randle out shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_dosunmu_retained_pooled_u` | Ayo Dosunmu re-signed, pooled un-aged mean pp | -0.21 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_dosunmu_retained_pooled_a` | Ayo Dosunmu re-signed, pooled aged mean pp | -0.29 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_dosunmu_retained_tr_u` | Ayo Dosunmu re-signed, team-rank un-aged mean pp | -0.29 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_dosunmu_retained_tr_a` | Ayo Dosunmu re-signed, team-rank aged mean pp | -0.36 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_dosunmu_retained_cells` | Ayo Dosunmu re-signed, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_dosunmu_retained_two_cell` | Ayo Dosunmu re-signed ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_dosunmu_retained_label` | verdict label | Ayo Dosunmu re-signed | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_dosunmu_retained_u` | Ayo Dosunmu re-signed, un-aged mean pp | -0.21 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_dosunmu_retained_a` | Ayo Dosunmu re-signed, aged mean pp | -0.29 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_dosunmu_retained_clear` | Ayo Dosunmu re-signed, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_dosunmu_retained_signs` | Ayo Dosunmu re-signed, sign un-aged / aged | mixed / mixed | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_dosunmu_retained_ships` | Ayo Dosunmu re-signed ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_dosunmu_retained_preship` | Ayo Dosunmu re-signed shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_depth_pooled_u` | Depth signings and re-signings, pooled un-aged mean pp | +0.06 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_depth_pooled_a` | Depth signings and re-signings, pooled aged mean pp | +0.13 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_depth_tr_u` | Depth signings and re-signings, team-rank un-aged mean pp | +0.50 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_depth_tr_a` | Depth signings and re-signings, team-rank aged mean pp | +0.55 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_depth_cells` | Depth signings and re-signings, views clearing in the four cells | 1/4, 2/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_depth_two_cell` | Depth signings and re-signings ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_depth_label` | verdict label | Depth signings and re-signings | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_depth_u` | Depth signings and re-signings, un-aged mean pp | +0.06 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_depth_a` | Depth signings and re-signings, aged mean pp | +0.13 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_depth_clear` | Depth signings and re-signings, views clearing the floor un-aged / aged | 1/4, 2/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_depth_signs` | Depth signings and re-signings, sign un-aged / aged | mixed / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_depth_ships` | Depth signings and re-signings ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_depth_preship` | Depth signings and re-signings shipped before D85 | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_kuminga_in_pooled_u` | Kuminga in (pooled), pooled un-aged mean pp | +0.04 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_kuminga_in_pooled_a` | Kuminga in (pooled), pooled aged mean pp | +0.11 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_kuminga_in_tr_u` | Kuminga in (pooled), team-rank un-aged mean pp | +0.22 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_kuminga_in_tr_a` | Kuminga in (pooled), team-rank aged mean pp | +0.32 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_kuminga_in_cells` | Kuminga in (pooled), views clearing in the four cells | 3/4, 4/4, 3/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_kuminga_in_two_cell` | Kuminga in (pooled) ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_kuminga_in_label` | verdict label | Kuminga in (pooled) | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_kuminga_in_u` | Kuminga in (pooled), un-aged mean pp | +0.04 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_kuminga_in_a` | Kuminga in (pooled), aged mean pp | +0.11 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_kuminga_in_clear` | Kuminga in (pooled), views clearing the floor un-aged / aged | 3/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_kuminga_in_signs` | Kuminga in (pooled), sign un-aged / aged | mixed / mixed | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_kuminga_in_ships` | Kuminga in (pooled) ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_kuminga_in_preship` | Kuminga in (pooled) shipped before D85 | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ddv_injury_pooled_u` | DiVincenzo's Achilles (not a transaction), pooled un-aged mean pp | -0.39 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ddv_injury_pooled_a` | DiVincenzo's Achilles (not a transaction), pooled aged mean pp | -0.33 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ddv_injury_tr_u` | DiVincenzo's Achilles (not a transaction), team-rank un-aged mean pp | -1.00 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ddv_injury_tr_a` | DiVincenzo's Achilles (not a transaction), team-rank aged mean pp | -0.83 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ddv_injury_cells` | DiVincenzo's Achilles (not a transaction), views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ddv_injury_two_cell` | DiVincenzo's Achilles (not a transaction) ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_ddv_injury_label` | verdict label | DiVincenzo's Achilles (not a transaction) | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_ddv_injury_u` | DiVincenzo's Achilles (not a transaction), un-aged mean pp | -0.39 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ddv_injury_a` | DiVincenzo's Achilles (not a transaction), aged mean pp | -0.33 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ddv_injury_clear` | DiVincenzo's Achilles (not a transaction), views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ddv_injury_signs` | DiVincenzo's Achilles (not a transaction), sign un-aged / aged | all negative / all negative | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ddv_injury_ships` | DiVincenzo's Achilles (not a transaction) ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_ddv_injury_preship` | DiVincenzo's Achilles (not a transaction) shipped before D85 | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_A_c3_default_shannon_pooled_u` | Kuminga slot, default allocation, pooled un-aged mean pp | +0.44 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_A_c3_default_shannon_pooled_a` | Kuminga slot, default allocation, pooled aged mean pp | +0.56 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_A_c3_default_shannon_tr_u` | Kuminga slot, default allocation, team-rank un-aged mean pp | +0.55 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_A_c3_default_shannon_tr_a` | Kuminga slot, default allocation, team-rank aged mean pp | +0.66 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_A_c3_default_shannon_cells` | Kuminga slot, default allocation, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_A_c3_default_shannon_two_cell` | Kuminga slot, default allocation ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_A_c3_default_shannon_label` | verdict label | Kuminga slot, default allocation | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_A_c3_default_shannon_u` | Kuminga slot, default allocation, un-aged mean pp | +0.55 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_A_c3_default_shannon_a` | Kuminga slot, default allocation, aged mean pp | +0.66 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_A_c3_default_shannon_clear` | Kuminga slot, default allocation, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_A_c3_default_shannon_signs` | Kuminga slot, default allocation, sign un-aged / aged | all positive / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_A_c3_default_shannon_ships` | Kuminga slot, default allocation ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_A_c3_default_shannon_preship` | Kuminga slot, default allocation shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_C_mcdaniels_slides_pooled_u` | Kuminga slot, McDaniels slides, pooled un-aged mean pp | +0.42 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_C_mcdaniels_slides_pooled_a` | Kuminga slot, McDaniels slides, pooled aged mean pp | +0.54 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_C_mcdaniels_slides_tr_u` | Kuminga slot, McDaniels slides, team-rank un-aged mean pp | +0.53 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_C_mcdaniels_slides_tr_a` | Kuminga slot, McDaniels slides, team-rank aged mean pp | +0.64 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_C_mcdaniels_slides_cells` | Kuminga slot, McDaniels slides, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_C_mcdaniels_slides_two_cell` | Kuminga slot, McDaniels slides ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_C_mcdaniels_slides_label` | verdict label | Kuminga slot, McDaniels slides | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_C_mcdaniels_slides_u` | Kuminga slot, McDaniels slides, un-aged mean pp | +0.53 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_C_mcdaniels_slides_a` | Kuminga slot, McDaniels slides, aged mean pp | +0.64 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_C_mcdaniels_slides_clear` | Kuminga slot, McDaniels slides, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_C_mcdaniels_slides_signs` | Kuminga slot, McDaniels slides, sign un-aged / aged | all positive / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_C_mcdaniels_slides_ships` | Kuminga slot, McDaniels slides ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_C_mcdaniels_slides_preship` | Kuminga slot, McDaniels slides shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_D_beringer_fills_pooled_u` | Kuminga slot, Beringer fills, pooled un-aged mean pp | -0.72 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_D_beringer_fills_pooled_a` | Kuminga slot, Beringer fills, pooled aged mean pp | -1.31 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_D_beringer_fills_tr_u` | Kuminga slot, Beringer fills, team-rank un-aged mean pp | -1.03 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_D_beringer_fills_tr_a` | Kuminga slot, Beringer fills, team-rank aged mean pp | -1.84 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_D_beringer_fills_cells` | Kuminga slot, Beringer fills, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_D_beringer_fills_two_cell` | Kuminga slot, Beringer fills ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_D_beringer_fills_label` | verdict label | Kuminga slot, Beringer fills | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_D_beringer_fills_u` | Kuminga slot, Beringer fills, un-aged mean pp | -1.03 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_D_beringer_fills_a` | Kuminga slot, Beringer fills, aged mean pp | -1.84 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_D_beringer_fills_clear` | Kuminga slot, Beringer fills, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_D_beringer_fills_signs` | Kuminga slot, Beringer fills, sign un-aged / aged | all negative / all negative | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_D_beringer_fills_ships` | Kuminga slot, Beringer fills ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_D_beringer_fills_preship` | Kuminga slot, Beringer fills shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_E_tight_rule_F_or_FC_pooled_u` | Kuminga slot, tight eligibility rule, pooled un-aged mean pp | +0.44 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_E_tight_rule_F_or_FC_pooled_a` | Kuminga slot, tight eligibility rule, pooled aged mean pp | +0.56 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_E_tight_rule_F_or_FC_tr_u` | Kuminga slot, tight eligibility rule, team-rank un-aged mean pp | +0.54 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_E_tight_rule_F_or_FC_tr_a` | Kuminga slot, tight eligibility rule, team-rank aged mean pp | +0.64 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_E_tight_rule_F_or_FC_cells` | Kuminga slot, tight eligibility rule, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_E_tight_rule_F_or_FC_two_cell` | Kuminga slot, tight eligibility rule ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_E_tight_rule_F_or_FC_label` | verdict label | Kuminga slot, tight eligibility rule | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_E_tight_rule_F_or_FC_u` | Kuminga slot, tight eligibility rule, un-aged mean pp | +0.54 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_E_tight_rule_F_or_FC_a` | Kuminga slot, tight eligibility rule, aged mean pp | +0.64 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_E_tight_rule_F_or_FC_clear` | Kuminga slot, tight eligibility rule, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_E_tight_rule_F_or_FC_signs` | Kuminga slot, tight eligibility rule, sign un-aged / aged | all positive / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_E_tight_rule_F_or_FC_ships` | Kuminga slot, tight eligibility rule ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_E_tight_rule_F_or_FC_preship` | Kuminga slot, tight eligibility rule shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_B_lyles_fills_pooled_u` | Kuminga slot, Lyles fills, pooled un-aged mean pp | +0.04 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_B_lyles_fills_pooled_a` | Kuminga slot, Lyles fills, pooled aged mean pp | -0.01 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_B_lyles_fills_tr_u` | Kuminga slot, Lyles fills, team-rank un-aged mean pp | +0.07 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_B_lyles_fills_tr_a` | Kuminga slot, Lyles fills, team-rank aged mean pp | -0.01 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_B_lyles_fills_cells` | Kuminga slot, Lyles fills, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_B_lyles_fills_two_cell` | Kuminga slot, Lyles fills ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `v_B_lyles_fills_label` | verdict label | Kuminga slot, Lyles fills | FACT | FACT | `w2_aging_gate_20260919T232645Z` |
| `v_B_lyles_fills_u` | Kuminga slot, Lyles fills, un-aged mean pp | +0.07 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_B_lyles_fills_a` | Kuminga slot, Lyles fills, aged mean pp | -0.01 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_B_lyles_fills_clear` | Kuminga slot, Lyles fills, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_B_lyles_fills_signs` | Kuminga slot, Lyles fills, sign un-aged / aged | mixed / mixed | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_B_lyles_fills_ships` | Kuminga slot, Lyles fills ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `v_B_lyles_fills_preship` | Kuminga slot, Lyles fills shipped before D85 | no | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `n_ship` | verdicts that ship | 7 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `n_ship_pre` | verdicts that shipped before D85 | 9 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `n_retired` | verdicts that shipped before D85 and do not now | 3 | MODELED | QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `n_ship_two_cell` | verdicts that ship on the two-cell rule (pooled only) | 7 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `n_candidates` | candidate verdicts tested | 13 | FACT | FACT | `r7_allocator_agreement_20260919T233117Z` |
| `k_min_pooled` | Kuminga minutes under the pooled allocator | 22.0 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `k_min_teamrank` | Kuminga minutes under the teamrank allocator | 25.2 | MODELED | QUOTABLE | `r7_allocator_agreement_20260919T233117Z` |
| `d85_residual` | post-D85 attribution roster vs direct simulation, worst view pp, both bases | 0.05 | MODELED | QUOTABLE | `r5_shapley_williams_20260919T232647Z` |
| `d85_pooled_gap` | post-D85 pooled attribution rule vs direct simulation, worst view pp, both bases | 0.78 | MODELED | QUOTABLE | `r5_shapley_williams_20260919T232647Z` |
| `d85_gap_before` | pre-D85 attribution roster vs direct simulation, worst view pp, un-aged | 1.25 | MODELED | QUOTABLE | `r5_shapley_williams_20260919T232647Z` |
| `williams_bio` | Cody Williams consensus impact | -4.39 | MODELED | QUOTABLE | `build_rotations_20260919T163216Z` |
| `anderson_u` | Kyle Anderson departure, un-aged pp | +0.09 | MODELED | QUOTABLE | `r2_departures_20260919T232924Z` |
| `anderson_a` | Kyle Anderson departure, aged pp | +0.37 | MODELED | QUOTABLE | `r2_departures_20260919T232924Z` |
| `anderson_clear` | Kyle Anderson departure, views clearing un-aged / aged | 2/4, 4/4 | MODELED | QUOTABLE | `r2_departures_20260919T232924Z` |
| `n_dep_ship` | departures that ship on their own | 0 | MODELED | QUOTABLE | `r2_departures_20260919T232924Z` |
| `n_departures` | players in the other-departures bundle | 7 | FACT | FACT | `r2_departures_20260919T232924Z` |
| `sims` | simulations per f-curve view | 200,000 | ASSUMED | FACT | `merge_fcurve_parts_20260919T195006Z` |
| `per100` | rating basis, possessions | 100 | FACT | FACT | `n8_watch_list_20260919T233400Z` |

## 2. What the odds get right

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `m1_rs_gain` | style overlay held-out MAE gain, 2025-26 regular season | -0.0151 | MODELED | QUOTABLE | `m1_style_model_20260910T135427Z` |
| `m1_rs_worse` | held-out MAE increase, regular season | 0.0151 | MODELED | QUOTABLE | `m1_style_model_20260910T135427Z` |
| `m1_po_worse` | held-out MAE increase, postseasons | 0.0265 | MODELED | QUOTABLE | `m1_style_model_20260910T135427Z` |
| `m1_rs_n` | held-out regular-season games | 1,225 | OBSERVED | FACT | `m1_style_model_20260910T135427Z` |
| `m1_po_gain` | style overlay held-out MAE gain, three postseasons | -0.0265 | MODELED | QUOTABLE | `m1_style_model_20260910T135427Z` |
| `m1_po_n` | held-out postseason games | 251 | OBSERVED | FACT | `m1_style_model_20260910T135427Z` |
| `n3_start` | first postseason in the longer N3 sample | 2014 | FACT | FACT | `n3_playoff_translation_20260916T212714Z` |
| `n3_series` | series, 2014-26 | 195 | OBSERVED | FACT | `n3_playoff_translation_20260916T212714Z` |
| `n3_series_primary` | series, three project postseasons | 45 | OBSERVED | FACT | `n3_playoff_translation_20260916T212714Z` |
| `n3_mde_lo` | smallest detectable effect, 13 seasons, low | 0.95 | COMPOSED | QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `n3_mde_hi` | smallest detectable effect, 13 seasons, high | 1.15 | COMPOSED | QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `n3_n_translating` | features that translate | 0 | MODELED | QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `n3_n_features` | candidate translation features | 8 | ASSUMED | FACT | `n3_playoff_translation_20260916T212714Z` |
| `ds_coef` | defence share, points per game per SD | -0.85 | MODELED | NOT QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `ds_se` | defence share SE | 0.34 | MODELED | NOT QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `ds_p` | defence share permutation p | 0.011 | MODELED | NOT QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `ds_bar` | Bonferroni bar | 0.0063 | ASSUMED | FACT | `n3_playoff_translation_20260916T212714Z` |
| `ds_ci_hi` | defence share single-test 95% interval upper end | -0.18 | MODELED | NOT QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `ds_early` | defence share 2014-23 only | -0.87 | MODELED | NOT QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `ds_late` | defence share 2024-26 only | -0.86 | MODELED | NOT QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `ds_luck` | defence share with three-point luck added | -0.77 | MODELED | NOT QUOTABLE | `n3_playoff_translation_20260916T212714Z` |
| `n4_sd13` | true matchup effect SD, 2013-26, points per game | 0.65 | OBSERVED | QUOTABLE | `n4_versatility_index_20260919T234720Z` |
| `n4_sd13_up` | upper 95%, 2013-26 | 1.77 | OBSERVED | QUOTABLE | `n4_versatility_index_20260919T234720Z` |
| `n4_sd97` | true matchup effect SD, 1997-2026 | 0.00 | OBSERVED | QUOTABLE | `n4_versatility_index_20260919T234720Z` |
| `n4_sd97_up` | upper 95%, 1997-2026 | 1.25 | OBSERVED | QUOTABLE | `n4_versatility_index_20260919T234720Z` |
| `n4_series_up` | series points at the tighter upper bound | 9 | MODELED | QUOTABLE | `n4_versatility_index_20260919T234720Z` |
| `n4_rankcorr` | spread vs own net rank correlation outside the field | 1.00 | MODELED | QUOTABLE | `n4_versatility_index_20260919T234720Z` |
| `n4_start13` | first season, primary window | 2013-14 | FACT | FACT | `n4_versatility_index_20260919T234720Z` |
| `n4_start97` | first season, extended window | 1997-98 | FACT | FACT | `n4_versatility_index_20260919T234720Z` |
| `n4_games97` | regular-season games, 1997-2026 | 34,357 | OBSERVED | FACT | `n4_versatility_index_20260919T234720Z` |
| `m3_se30` | matchup SE at 30 possessions | 0.14 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260916T201505Z` |
| `m3_norm_lo` | primary-defender norm, low | 0.05 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260916T201505Z` |
| `m3_norm_hi` | primary-defender norm, high | 0.10 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260916T201505Z` |
| `m3_edges` | matchups beyond the norm by 2 SEs, above | 2 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260916T201505Z` |
| `m3_rows` | observed West-field primary matchups | 79 | OBSERVED | FACT | `m3_opponent_cards_20260916T201505Z` |
| `m3_chance` | expected by chance, above | 2.3 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260916T201505Z` |
| `h2_n` | clean seasons | 3 | FACT | FACT | `champions_table_20260919T195047Z` |
| `h2_fav` | favourite won | 1 | OBSERVED | QUOTABLE | `champions_table_20260919T195047Z` |
| `h2_top5` | champion from the top five | 3 | OBSERVED | QUOTABLE | `champions_table_20260919T195047Z` |
| `h2_lo` | champions' preseason price, low | 8.27% | OBSERVED | QUOTABLE | `champions_table_20260919T195047Z` |
| `h2_hi` | champions' preseason price, high | 14.69% | OBSERVED | QUOTABLE | `champions_table_20260919T195047Z` |
| `h3_n_non` | preseason top-5 non-champions | 14 | OBSERVED | FACT | `h1_h3_h5_profile_20260917T132715Z` |
| `h3_n_sep` | features that separate | 3 | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260917T132715Z` |
| `h3_n_feat` | features compared | 20 | OBSERVED | FACT | `h1_h3_h5_profile_20260917T132715Z` |
| `nyk_mkt` | Knicks preseason market price | 8.27% | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_rank` | Knicks preseason market rank | 4 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_wt` | Knicks win total | 53.5 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_wins` | Knicks wins | 53 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_model` | our model's Knicks price | 4.63% | MODELED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_rs` | Knicks regular-season margin | +6.33 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_pre` | before the break | +6.16 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_post` | after the break | +6.67 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_po_rec` | Knicks playoff record | 16-3 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_po` | Knicks playoff margin | +14.89 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_lift` | Knicks playoff lift | +8.57 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_po_teams` | playoff teams | 16 | OBSERVED | FACT | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_lift_mean` | Knicks lift_mean | -7.39 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_cmp_lift` | Knicks cmp_lift | -9.19 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_cmp_lift_rank` | Knicks cmp_lift_rank | 11 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_n_positive_lift` | Knicks n_positive_lift | 1 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_top5_rs_games_missed` | Knicks top5_rs_games_missed | 46 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_top5_po_games_missed` | Knicks top5_po_games_missed | 2 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_top5_share_rs` | Knicks top5_share_rs | 0.579 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |
| `nyk_top5_share_po` | Knicks top5_share_po | 0.673 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260916T190540Z` |

## 3. What the odds can't see

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `n5_min_full` | MIN full-roster title odds | 1.60% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T233508Z` |
| `n5_min_drop` | MIN mean drop | 0.87 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T233508Z` |
| `n5_min_share` | MIN share of odds lost | 54% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T233508Z` |
| `n5_min_net` | MIN mean net lost per removal | 2.60 | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_min_big` | MIN largest single net loss | 3.09 | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_min_bigname` | MIN largest single loss, player | Rudy Gobert | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_min_po` | MIN mean net lost, playoff rollup | 2.22 | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_okc_full` | OKC full-roster title odds | 14.71% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T233508Z` |
| `n5_okc_drop` | OKC mean drop | 6.04 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T233508Z` |
| `n5_okc_share` | OKC share of odds lost | 41% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T233508Z` |
| `n5_okc_net` | OKC mean net lost per removal | 2.73 | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_okc_big` | OKC largest single net loss | 4.89 | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_okc_bigname` | OKC largest single loss, player | Shai Gilgeous-Alexander | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_okc_po` | OKC mean net lost, playoff rollup | 3.01 | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_sas_full` | SAS full-roster title odds | 13.73% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T233508Z` |
| `n5_sas_drop` | SAS mean drop | 6.04 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T233508Z` |
| `n5_sas_share` | SAS share of odds lost | 44% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T233508Z` |
| `n5_sas_net` | SAS mean net lost per removal | 2.70 | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_sas_big` | SAS largest single net loss | 5.26 | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_sas_bigname` | SAS largest single loss, player | Victor Wembanyama | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_sas_po` | SAS mean net lost, playoff rollup | 2.83 | MODELED | QUOTABLE | `n5_fragility_20260919T233508Z` |
| `n5_min_full_aged` | MIN full-roster title odds_aged | 2.29% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T234118Z` |
| `n5_min_drop_aged` | MIN mean drop_aged | 0.99 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T234118Z` |
| `n5_min_share_aged` | MIN share of odds lost_aged | 43% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T234118Z` |
| `n5_min_net_aged` | MIN mean net lost per removal_aged | 2.07 | MODELED | QUOTABLE | `n5_fragility_20260919T234118Z` |
| `n5_min_big_aged` | MIN largest single net loss_aged | 2.28 | MODELED | QUOTABLE | `n5_fragility_20260919T234118Z` |
| `n5_min_bigname_aged` | MIN largest single loss, player_aged | LaMelo Ball | MODELED | QUOTABLE | `n5_fragility_20260919T234118Z` |
| `n5_okc_full_aged` | OKC full-roster title odds_aged | 17.10% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T234118Z` |
| `n5_okc_drop_aged` | OKC mean drop_aged | 6.66 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T234118Z` |
| `n5_okc_share_aged` | OKC share of odds lost_aged | 39% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T234118Z` |
| `n5_okc_net_aged` | OKC mean net lost per removal_aged | 2.63 | MODELED | QUOTABLE | `n5_fragility_20260919T234118Z` |
| `n5_okc_big_aged` | OKC largest single net loss_aged | 4.66 | MODELED | QUOTABLE | `n5_fragility_20260919T234118Z` |
| `n5_okc_bigname_aged` | OKC largest single loss, player_aged | Shai Gilgeous-Alexander | MODELED | QUOTABLE | `n5_fragility_20260919T234118Z` |
| `n5_sas_full_aged` | SAS full-roster title odds_aged | 16.39% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T234118Z` |
| `n5_sas_drop_aged` | SAS mean drop_aged | 6.26 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T234118Z` |
| `n5_sas_share_aged` | SAS share of odds lost_aged | 38% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260919T234118Z` |
| `n5_sas_net_aged` | SAS mean net lost per removal_aged | 2.52 | MODELED | QUOTABLE | `n5_fragility_20260919T234118Z` |
| `n5_sas_big_aged` | SAS largest single net loss_aged | 5.52 | MODELED | QUOTABLE | `n5_fragility_20260919T234118Z` |
| `n5_sas_bigname_aged` | SAS largest single loss, player_aged | Victor Wembanyama | MODELED | QUOTABLE | `n5_fragility_20260919T234118Z` |
| `williams_mpg` | Cody Williams projected minutes | 16.1 | ASSUMED | NOT QUOTABLE | `build_rotations_20260919T163216Z` |
| `rs_williams` | Williams rank score | 0.3041 | COMPOSED | DESCRIPTIVE | `build_rotations_20260919T163216Z` |
| `rs_clark` | Jaylen Clark rank score | 0.3333 | COMPOSED | DESCRIPTIVE | `build_rotations_20260919T163216Z` |
| `rs_gap` | rank-score gap | 0.0293 | COMPOSED | DESCRIPTIVE | `build_rotations_20260919T163216Z` |
| `williams_threshold` | Williams minutes below which the offseason verdict turns MIXED | 12.6 | MODELED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w1c_offseason_delta` | published offseason delta, mean pp | -0.753 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260919T195038Z` |
| `w1c_injury_cost` | DiVincenzo injury cost, mean pp | +1.806 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260919T195038Z` |
| `w1c_williams_cost` | Williams minutes cost, mean pp | +1.048 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260919T195038Z` |
| `w1c_interaction` | interaction, mean pp | -1.048 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260919T195038Z` |
| `w1c_remainder` | remainder, mean pp | +1.053 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260919T195038Z` |
| `m4_fives` | legal fives, DiVincenzo excluded | 749 | COMPOSED | FACT | `m4_lineup_study_20260919T195041Z` |
| `m4_double` | double-big fives | 161 | COMPOSED | FACT | `m4_lineup_study_20260919T195041Z` |
| `m4_nogobert` | fives without Gobert | 294 | COMPOSED | FACT | `m4_lineup_study_20260919T195041Z` |
| `m4_observed` | fives that have played together | 5 | OBSERVED | FACT | `m4_lineup_study_20260919T195041Z` |
| `m4_top10_beringer` | of the ten best rankable fives, how many include Beringer | 9 | COMPOSED | DESCRIPTIVE | `m4_lineup_study_20260919T195041Z` |
| `beringer_prior` | Beringer 2025-26 minutes per game | 7.9 | OBSERVED | FACT | `build_rotations_20260919T163216Z` |
| `reid_gobert` | Reid + Gobert net per 100, rebuilt points | +3.2 | OBSERVED | DESCRIPTIVE | `lineup_evidence_20260917T133631Z` |
| `randle_gobert` | Randle + Gobert net per 100, rebuilt points | +3.3 | OBSERVED | DESCRIPTIVE | `lineup_evidence_20260917T133631Z` |
| `m5_top` | projected top five usage sum | 1.121 | COMPOSED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `m5_top_pct` | percentile | 87 | COMPOSED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `m5_kin` | Kuminga-in five usage sum | 1.150 | COMPOSED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `m5_kin_pct` | percentile | 96 | COMPOSED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `m5_kin3_pct` | percentile at three-season rates | 98 | COMPOSED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `m5_obs_pct` | last season's actual five, percentile | 56 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `m5_league_fives` | league starting fives | 7,380 | OBSERVED | FACT | `m5_usage_accounting_20260916T203535Z` |
| `m5_adj_usg` | adjusted pairing effect on usage, points | -0.4 | OBSERVED | DIRECTIONAL | `m5_usage_accounting_20260916T203535Z` |
| `m5_adj_ts` | adjusted pairing effect on true shooting, points | -0.1 | OBSERVED | DIRECTIONAL | `m5_usage_accounting_20260916T203535Z` |
| `m5_star_usg` | star-tier pairing effect on usage | -1.5 | OBSERVED | DIRECTIONAL | `m5_usage_accounting_20260916T203535Z` |
| `m5_star_usg_se` | star-tier usage SE | 0.9 | OBSERVED | DIRECTIONAL | `m5_usage_accounting_20260916T203535Z` |
| `m5_star_ts` | star-tier pairing effect on true shooting | +0.8 | OBSERVED | DIRECTIONAL | `m5_usage_accounting_20260916T203535Z` |
| `m5_star_n` | star-tier treated player-seasons | 9 | OBSERVED | FACT | `m5_usage_accounting_20260916T203535Z` |
| `m5_treated` | player-seasons with a new high-usage partner | 34 | OBSERVED | FACT | `m5_usage_accounting_20260916T203535Z` |
| `n2_modal` | modal seed | 7th | MODELED | QUOTABLE | `seed_distribution_20260919T195022Z` |
| `n2_modal_p` | modal seed probability | 31% | MODELED | QUOTABLE | `seed_distribution_20260919T195022Z` |
| `n2_top6` | P(top six) | 42% | MODELED | QUOTABLE | `seed_distribution_20260919T195022Z` |
| `n2_sas_okc` | P(first-round opponent is SAS or OKC) | 53% | MODELED | QUOTABLE | `n2_path_20260919T195039Z` |
| `n2_r2` | P(reach round two) | 28% | MODELED | QUOTABLE AS BAND | `n2_path_20260919T195039Z` |
| `n2_cond` | P(title | escape round one) | 6.1% | MODELED | QUOTABLE AS BAND | `n2_path_20260919T195039Z` |

## 4. Kuminga, better and worse

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `k_scorer_pct` | Kuminga scorer percentile, 2023-26 | 36 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `k_scorer_z` | Kuminga scorer SEs | -0.2 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `k_scorer_n` | Kuminga scorer pairings | 29 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `k_scorer_poss` | Kuminga scorer possessions | 1,415 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `k_scorer_ref` | reference scorers | 245 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `k_defender_pct` | Kuminga defender percentile, 2023-26 | 23 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `k_defender_z` | Kuminga defender SEs | -1.3 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `k_defender_n` | Kuminga defender pairings | 13 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `k_defender_poss` | Kuminga defender possessions | 711 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `k_defender_ref` | reference defenders | 309 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `k_scorer_n26` | Kuminga scorer pairings 2025-26 | 3 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `e_scorer_pct3` | Edwards scorer percentile, 2023-26 | 0 | OBSERVED | QUOTABLE | `n6_kuminga_ledger_20260917T133322Z` |
| `e_scorer_z3` | Edwards scorer SEs, 2023-26 | -8.6 | OBSERVED | QUOTABLE | `n6_kuminga_ledger_20260917T133322Z` |
| `e_scorer_n3` | Edwards scorer pairings, 2023-26 | 72 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `gsw_with` | GSW units with a non-shooting centre, net | -2.1 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `gsw_without` | without one, net | +0.6 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `gsw_with_poss` | possessions with | 5,340 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `gsw_without_poss` | possessions without | 5,672 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `gsw_with_3par` | 3PA rate with | 0.430 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `gsw_without_3par` | 3PA rate without | 0.448 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `gsw_se` | difference game-bootstrap SE | 3.5 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `po_games` | Kuminga postseason games | 40 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `po_poss` | postseason possessions | 1,139 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `po_net` | postseason on-court net | -16.2 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `po_onoff` | postseason on-off, garbage time out | -16.0 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `po_onoff_se` | on-off SE | 8.4 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260917T133322Z` |
| `po_onoff_games` | stint games | 23 | OBSERVED | FACT | `n6_kuminga_ledger_20260917T133322Z` |
| `k_usg` | Kuminga usage 2025-26 | 0.226 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `k_unast` | Kuminga unassisted share 2025-26 | 44% | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `k_unast_pct` | percentile | 69 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `k_makes` | Kuminga makes 2025-26 | 157 | OBSERVED | FACT | `m5_usage_accounting_20260916T203535Z` |
| `k_y1` | Kuminga year one | $6,064,000 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `k_y2` | Kuminga year two, player option | $6,367,200 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `k_total` | Kuminga total | $12,431,200 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `k_nonbird` | Non-Bird ceiling after an opt-out | $7,276,800 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `k_optout_lo` | P(opt out), low across views, flat aging | 0.53 | MODELED | QUOTABLE AS BAND | `player_option_20260919T195020Z` |
| `k_optout_hi` | P(opt out), high | 0.84 | MODELED | QUOTABLE AS BAND | `player_option_20260919T195020Z` |

## 5. Edwards, and why Ball is here

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `e_pct_shipped` | Edwards percentile, M3 basis | 1 | OBSERVED | QUOTABLE | `m3_primary_defender_check_20260916T201455Z` |
| `e_z_shipped` | Edwards SEs, M3 basis | -5.6 | OBSERVED | QUOTABLE | `m3_primary_defender_check_20260916T201455Z` |
| `e_pct_A` | Edwards percentile, rotation-defender baseline | 1 | OBSERVED | QUOTABLE | `m3_primary_defender_check_20260916T201455Z` |
| `e_z_A` | Edwards SEs, rotation-defender baseline | -5.3 | OBSERVED | QUOTABLE | `m3_primary_defender_check_20260916T201455Z` |
| `e_pct_B` | Edwards percentile, regular season only | 5 | OBSERVED | QUOTABLE | `m3_primary_defender_check_20260916T201455Z` |
| `e_z_B` | Edwards SEs, regular season only | -3.4 | OBSERVED | QUOTABLE | `m3_primary_defender_check_20260916T201455Z` |
| `e_pct_C` | Edwards percentile, both | 5 | OBSERVED | QUOTABLE | `m3_primary_defender_check_20260916T201455Z` |
| `e_z_C` | Edwards SEs, both | -3.1 | OBSERVED | QUOTABLE | `m3_primary_defender_check_20260916T201455Z` |
| `e_n_off` | top scorers in the reference | 150 | OBSERVED | FACT | `m3_primary_defender_check_20260916T201455Z` |
| `e_pairings` | Edwards primary pairings 2025-26 | 21 | OBSERVED | FACT | `m3_primary_defender_check_20260916T201455Z` |
| `cr_edw` | Anthony Edwards unassisted share of makes, 2025-26 | 61% | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `cr_edw_pct` | Anthony Edwards percentile | 95 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `usg_edw` | Anthony Edwards usage 2025-26 | 0.309 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `cr_ball` | LaMelo Ball unassisted share of makes, 2025-26 | 55% | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `cr_ball_pct` | LaMelo Ball percentile | 84 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `usg_ball` | LaMelo Ball usage 2025-26 | 0.306 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `cr_dos` | Ayo Dosunmu unassisted share of makes, 2025-26 | 35% | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `cr_dos_pct` | Ayo Dosunmu percentile | 51 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `usg_dos` | Ayo Dosunmu usage 2025-26 | 0.197 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `cr_median` | league median unassisted share | 35% | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |

## 6. Clutch

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `cl_start` | first season in the pooled clutch window | 2023-24 | FACT | FACT | `n7_late_clock_20260916T230449Z` |
| `cl_efg_all` | league eFG, all shots 2023-26 | 0.544 | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_efg_clutch` | league eFG, clutch | 0.502 | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_un_all` | league unassisted share, all | 37% | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_un_clutch` | league unassisted share, clutch | 45% | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_n_ok` | creators with enough clutch shots | 22 | OBSERVED | FACT | `n7_late_clock_20260916T230449Z` |
| `cl_n_big` | beyond the league drop by 2 SEs | 2 | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_chance` | expected by chance | 1.0 | COMPOSED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_big1` | creator beyond the drop | Derrick White | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_big1_z` | SEs | +2.3 | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_big2` | creator beyond the drop | Jamal Murray | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_big2_z` | SEs | +2.0 | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_edw_efg` | Anthony Edwards clutch eFG | 0.546 | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_edw_fga` | Anthony Edwards clutch attempts | 306 | OBSERVED | FACT | `n7_late_clock_20260916T230449Z` |
| `cl_edw_z` | Anthony Edwards beyond the drop, SEs | +1.3 | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_ball_efg` | LaMelo Ball clutch eFG | 0.460 | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `cl_ball_fga` | LaMelo Ball clutch attempts | 100 | OBSERVED | FACT | `n7_late_clock_20260916T230449Z` |
| `cl_ball_z` | LaMelo Ball beyond the drop, SEs | -0.1 | OBSERVED | QUOTABLE | `n7_late_clock_20260916T230449Z` |
| `lc_g1` | late-clock reconstruction accuracy, within 2 s | 79.9% | OBSERVED | WITHHELD | `n7_late_clock_20260916T230449Z` |
| `lc_bar` | bar set in advance | 80% | ASSUMED | FACT | `n7_late_clock_20260916T230449Z` |

## 7. What to watch

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `w1_claim` | claim 1 | Cody Williams' minutes decide whether the offseason verdict holds | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w1_now` | claim 1 current value | 16.1 a night (model default) | ASSUMED INPUT | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w1_flip` | claim 1 flips if | below 12.6 a night | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w2_claim` | claim 2 | Minnesota's level is inside the model's range | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w2_now` | claim 2 current value | model range -1.5 to +1.8 (four views, both aging bases) | MODELLED RANGE | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w2_flip` | claim 2 flips if | above +7.5 or below -7.2 | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w3_claim` | claim 3 | The model's two largest disagreements with the market | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w3_now` | claim 3 current value | BOS: model 18.3% title odds vs market 5.5%, model net range +3.3 to +10.1. SAS: model 13.9% vs market 23.0%, range +4.2 to +8.7 | MODELLED RANGE | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w3_flip` | claim 3 flips if | BOS below -2.4; SAS above +14.4 | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w4_claim` | claim 4 | The Edwards-Ball pairing costs usage, not efficiency | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w4_now` | claim 4 current value | 2025-26 true shooting: Edwards 0.617, Ball 0.546. Unadjusted base rate for a new high-usage pairing: -0.3 points of true shooting (34 player-seasons) | OBSERVED BASE RATE | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w4_flip` | claim 4 flips if | Edwards below 0.547, or Ball below 0.476 | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w5_claim` | claim 5 | Minnesota is not on a champion's path | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w5_now` | claim 5 current value | projected rank 16 (un-aged) / 13 (aged); the 29 champions since 1997-98 ranked 11 at worst after 20 games (2005-06 MIA and 2022-23 DEN), median 2 | OBSERVED HISTORY | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w5_flip` | claim 5 flips if | 3 or better (test); 11 or better (checkpoint) | COMPOSED | QUOTABLE | `n8_watch_list_20260919T233400Z` |
| `w_game` | checkpoint game | 20 | ASSUMED | FACT | `n8_watch_list_20260919T233400Z` |

## 8. The bill

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `chain_start` | pre-trade Apron Team Salary (2026-08-27) | $217,621,829 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `chain_green` | out: Josh Green | $14,679,012 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `chain_williams` | in: Cody Williams | $6,015,600 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `chain_konchar` | in: John Konchar | $6,165,000 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `chain_stretch` | waive Konchar, stretch over 3 seasons | $4,110,000 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `chain_dollar` | McDaniels, our book $26,200,001 vs Spotrac $26,200,000 | $1 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `chain_post` | post-trade Apron Team Salary (2026-09-04) | $211,013,416 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `chain_kuminga` | sign Kuminga, taxpayer MLE year 1 | $6,064,000 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `chain_final` | final Apron Team Salary | $217,077,416 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `room_hard_cap` | room under second apron, with Kuminga | $4,608,584 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `over_first` | over first apron, with Kuminga | $8,062,416 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `over_tax` | over tax line, with Kuminga | $16,649,416 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `dead_year` | dead money 2026-27 | $2,055,000 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `dead_future` | Konchar dead money in 2027-28 and 2028-29 | $4,110,000 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `williams_option` | Williams 2027-28 club option | $7,669,890 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `dos_nodos_kuminga` | no-Dosunmu branch: most Kuminga could be paid from the non-taxpayer MLE | $8,254,095 | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_stuck_over` | Dosunmu + Green + Kuminga, over the hard cap by | $1,999,829 | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_happened_pay` | dos_happened payroll, tax basis | $215,327,416 | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_happened_apron` | dos_happened payroll, apron basis | $217,077,416 | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_happened_tax` | dos_happened estimated tax | $23.3M | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_cheapest_pay` | dos_cheapest payroll, tax basis | $208,614,580 | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_cheapest_apron` | dos_cheapest payroll, apron basis | $210,364,580 | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_cheapest_tax` | dos_cheapest estimated tax | $8.7M | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_nodos_pay` | dos_nodos payroll, tax basis | $207,265,000 | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_nodos_apron` | dos_nodos payroll, apron basis | $209,015,000 | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_nodos_tax` | dos_nodos estimated tax | $7.0M | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_dump_payroll` | extra payroll from taking Williams and Konchar | $6,712,836 | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |
| `dos_dump_tax` | extra tax | $14.6M | FACT | FACT | `dosunmu_final_states_20260904T014033Z` |

## Appendix

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `off_delta_u` | offseason delta, un-aged | -1.25 | MODELED | NOT QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `off_delta_a` | offseason delta, aged | -0.54 | MODELED | NOT QUOTABLE | `w2_aging_gate_20260919T232645Z` |
| `tail00_player` | tail player | Derrick White (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail00_poss` | possessions | 33,488 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail00_consensus` | consensus | +5.31 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail00_rapm` | rapm | +5.53 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail00_box` | box | +1.96 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail00_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail01_player` | tail player | Jayson Tatum (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail01_poss` | possessions | 27,371 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail01_consensus` | consensus | +5.09 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail01_rapm` | rapm | +4.85 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail01_box` | box | +2.24 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail01_darko` | darko | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail02_player` | tail player | Neemias Queta (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail02_poss` | possessions | 11,730 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail02_consensus` | consensus | +4.75 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail02_rapm` | rapm | +5.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail02_box` | box | +1.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail02_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail03_player` | tail player | Payton Pritchard (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail03_poss` | possessions | 27,327 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail03_consensus` | consensus | +3.28 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail03_rapm` | rapm | +3.62 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail03_box` | box | +1.06 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail03_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail04_player` | tail player | Paul George (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail04_poss` | possessions | 21,781 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail04_consensus` | consensus | +3.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail04_rapm` | rapm | +3.07 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail04_box` | box | +1.21 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail04_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail05_player` | tail player | Mitchell Robinson (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail05_poss` | possessions | 11,720 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail05_consensus` | consensus | +2.61 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail05_rapm` | rapm | +1.87 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail05_box` | box | +1.17 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail05_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail06_player` | tail player | Moussa Diabate (CHA) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail06_poss` | possessions | 10,571 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail06_consensus` | consensus | +5.05 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail06_rapm` | rapm | +5.05 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail06_box` | box | +0.27 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail06_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail07_player` | tail player | Kon Knueppel (CHA) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail07_poss` | possessions | 9,854 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail07_consensus` | consensus | +3.87 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail07_rapm` | rapm | +4.11 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail07_box` | box | +1.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail07_darko` | darko | +0.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail08_player` | tail player | Naz Reid (CHA) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail08_poss` | possessions | 28,945 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail08_consensus` | consensus | +2.79 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail08_rapm` | rapm | +2.73 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail08_box` | box | +0.97 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail08_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail09_player` | tail player | Nikola Jokic (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail09_poss` | possessions | 29,795 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail09_consensus` | consensus | +8.08 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail09_rapm` | rapm | +8.08 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail09_box` | box | +5.43 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail09_darko` | darko | +7.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail10_player` | tail player | Aaron Gordon (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail10_poss` | possessions | 23,054 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail10_consensus` | consensus | +3.47 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail10_rapm` | rapm | +3.88 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail10_box` | box | +0.69 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail10_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail11_player` | tail player | Jamal Murray (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail11_poss` | possessions | 32,124 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail11_consensus` | consensus | +2.74 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail11_rapm` | rapm | +2.89 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail11_box` | box | +1.96 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail11_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail12_player` | tail player | Christian Braun (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail12_poss` | possessions | 25,880 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail12_consensus` | consensus | +2.44 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail12_rapm` | rapm | +3.24 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail12_box` | box | +0.21 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail12_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail13_player` | tail player | Cameron Johnson (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail13_poss` | possessions | 18,473 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail13_consensus` | consensus | +2.38 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail13_rapm` | rapm | +2.77 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail13_box` | box | +0.73 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail13_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail14_player` | tail player | Cade Cunningham (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail14_poss` | possessions | 29,653 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail14_consensus` | consensus | +3.48 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail14_rapm` | rapm | +2.91 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail14_box` | box | +1.31 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail14_darko` | darko | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail15_player` | tail player | Ausar Thompson (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail15_poss` | possessions | 21,191 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail15_consensus` | consensus | +3.95 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail15_rapm` | rapm | +4.35 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail15_box` | box | +1.16 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail15_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail16_player` | tail player | Paul Reed (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail16_poss` | possessions | 11,697 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail16_consensus` | consensus | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail16_rapm` | rapm | +3.79 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail16_box` | box | +2.41 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail16_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail17_player` | tail player | Isaiah Joe (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail17_poss` | possessions | 20,956 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail17_consensus` | consensus | +2.39 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail17_rapm` | rapm | +2.43 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail17_box` | box | +1.48 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail17_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail18_player` | tail player | Duncan Robinson (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail18_poss` | possessions | 22,814 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail18_consensus` | consensus | +1.88 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail18_rapm` | rapm | +2.51 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail18_box` | box | -0.02 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail18_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail19_player` | tail player | Javonte Green (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail19_poss` | possessions | 11,773 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail19_consensus` | consensus | +2.58 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail19_rapm` | rapm | +2.78 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail19_box` | box | +1.11 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail19_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail20_player` | tail player | Amen Thompson (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail20_poss` | possessions | 28,337 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail20_consensus` | consensus | +4.24 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail20_rapm` | rapm | +4.13 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail20_box` | box | +1.31 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail20_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail21_player` | tail player | Kevin Durant (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail21_poss` | possessions | 31,434 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail21_consensus` | consensus | +3.51 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail21_rapm` | rapm | +3.36 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail21_box` | box | +1.72 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail21_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail22_player` | tail player | Tari Eason (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail22_poss` | possessions | 15,553 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail22_consensus` | consensus | +3.13 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail22_rapm` | rapm | +3.69 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail22_box` | box | +1.40 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail22_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail23_player` | tail player | Marcus Smart (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail23_poss` | possessions | 13,273 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail23_consensus` | consensus | +2.73 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail23_rapm` | rapm | +4.08 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail23_box` | box | -0.07 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail23_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail24_player` | tail player | Alperen Sengun (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail24_poss` | possessions | 29,429 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail24_consensus` | consensus | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail24_rapm` | rapm | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail24_box` | box | +1.47 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail24_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail25_player` | tail player | Steven Adams (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail25_poss` | possessions | 6,994 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail25_consensus` | consensus | +2.68 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail25_rapm` | rapm | +3.34 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail25_box` | box | -0.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail25_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail26_player` | tail player | OG Anunoby (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail26_poss` | possessions | 31,666 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail26_consensus` | consensus | +4.38 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail26_rapm` | rapm | +5.22 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail26_box` | box | +0.90 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail26_darko` | darko | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail27_player` | tail player | Karl-Anthony Towns (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail27_poss` | possessions | 32,893 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail27_consensus` | consensus | +3.77 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail27_rapm` | rapm | +3.59 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail27_box` | box | +1.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail27_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail28_player` | tail player | Jalen Brunson (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail28_poss` | possessions | 36,185 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail28_consensus` | consensus | +3.30 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail28_rapm` | rapm | +3.39 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail28_box` | box | +1.55 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail28_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail29_player` | tail player | Miles McBride (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail29_poss` | possessions | 18,187 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail29_consensus` | consensus | +3.22 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail29_rapm` | rapm | +4.07 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail29_box` | box | +0.17 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail29_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail30_player` | tail player | Josh Hart (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail30_poss` | possessions | 35,303 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail30_consensus` | consensus | +2.14 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail30_rapm` | rapm | +1.59 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail30_box` | box | -0.02 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail30_darko` | darko | +0.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail31_player` | tail player | Mikal Bridges (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail31_poss` | possessions | 37,099 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail31_consensus` | consensus | +1.70 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail31_rapm` | rapm | +1.44 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail31_box` | box | +0.37 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail31_darko` | darko | +0.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail32_player` | tail player | Shai Gilgeous-Alexander (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail32_poss` | possessions | 36,663 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail32_consensus` | consensus | +9.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail32_rapm` | rapm | +9.16 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail32_box` | box | +5.05 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail32_darko` | darko | +6.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail33_player` | tail player | Chet Holmgren (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail33_poss` | possessions | 30,400 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail33_consensus` | consensus | +6.05 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail33_rapm` | rapm | +6.39 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail33_box` | box | +2.95 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail33_darko` | darko | +5.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail34_player` | tail player | Isaiah Hartenstein (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail34_poss` | possessions | 24,050 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail34_consensus` | consensus | +4.53 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail34_rapm` | rapm | +4.17 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail34_box` | box | +1.28 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail34_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail35_player` | tail player | Alex Caruso (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail35_poss` | possessions | 20,771 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail35_consensus` | consensus | +5.17 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail35_rapm` | rapm | +5.41 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail35_box` | box | +2.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail35_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail36_player` | tail player | Ajay Mitchell (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail36_poss` | possessions | 9,612 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail36_consensus` | consensus | +3.26 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail36_rapm` | rapm | +3.55 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail36_box` | box | +1.11 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail36_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail37_player` | tail player | Jalen Williams (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail37_poss` | possessions | 24,304 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail37_consensus` | consensus | +2.65 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail37_rapm` | rapm | +1.59 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail37_box` | box | +2.13 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail37_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail38_player` | tail player | Cason Wallace (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail38_poss` | possessions | 26,671 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail38_consensus` | consensus | +2.21 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail38_rapm` | rapm | +1.76 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail38_box` | box | +1.02 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail38_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail39_player` | tail player | Joel Embiid (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail39_poss` | possessions | 14,241 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail39_consensus` | consensus | +5.43 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail39_rapm` | rapm | +4.25 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail39_box` | box | +2.96 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail39_darko` | darko | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail40_player` | tail player | Tyrese Maxey (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail40_poss` | possessions | 30,824 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail40_consensus` | consensus | +3.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail40_rapm` | rapm | +3.26 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail40_box` | box | +2.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail40_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail41_player` | tail player | LeBron James (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail41_poss` | possessions | 27,829 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail41_consensus` | consensus | +3.38 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail41_rapm` | rapm | +1.88 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail41_box` | box | +2.10 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail41_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail42_player` | tail player | Dean Wade (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail42_poss` | possessions | 16,303 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail42_consensus` | consensus | +3.45 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail42_rapm` | rapm | +4.28 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail42_box` | box | +0.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail42_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail43_player` | tail player | VJ Edgecombe (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail43_poss` | possessions | 11,784 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail43_consensus` | consensus | +1.89 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail43_rapm` | rapm | +2.32 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail43_box` | box | +0.27 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail43_darko` | darko | +0.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail44_player` | tail player | Victor Wembanyama (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail44_poss` | possessions | 24,727 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail44_consensus` | consensus | +9.99 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail44_rapm` | rapm | +9.88 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail44_box` | box | +5.55 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail44_darko` | darko | +6.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail45_player` | tail player | De'Aaron Fox (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail45_poss` | possessions | 31,321 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail45_consensus` | consensus | +3.41 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail45_rapm` | rapm | +3.83 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail45_box` | box | +1.80 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail45_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail46_player` | tail player | Dylan Harper (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail46_poss` | possessions | 8,557 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail46_consensus` | consensus | +4.27 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail46_rapm` | rapm | +5.06 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail46_box` | box | +1.12 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail46_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail47_player` | tail player | Tobias Harris (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail47_poss` | possessions | 28,597 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail47_consensus` | consensus | +3.24 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail47_rapm` | rapm | +3.79 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail47_box` | box | +0.54 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail47_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail48_player` | tail player | Luke Kornet (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail48_poss` | possessions | 17,332 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail48_consensus` | consensus | +3.67 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail48_rapm` | rapm | +3.04 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail48_box` | box | +1.73 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail48_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail49_player` | tail player | Kawhi Leonard (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail49_poss` | possessions | 22,880 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail49_consensus` | consensus | +7.61 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail49_rapm` | rapm | +8.02 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail49_box` | box | +3.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail49_darko` | darko | +6.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail50_player` | tail player | Scottie Barnes (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail50_poss` | possessions | 28,446 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail50_consensus` | consensus | +3.65 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail50_rapm` | rapm | +2.83 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail50_box` | box | +2.09 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail50_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail51_player` | tail player | Jakob Poeltl (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail51_poss` | possessions | 16,432 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail51_consensus` | consensus | +2.76 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail51_rapm` | rapm | +2.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail51_box` | box | +1.32 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail51_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail52_player` | tail player | Immanuel Quickley (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail52_poss` | possessions | 20,156 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail52_consensus` | consensus | +2.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail52_rapm` | rapm | +1.79 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail52_box` | box | +1.66 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail52_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail53_player` | tail player | Collin Murray-Boyles (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail53_poss` | possessions | 5,585 | OBSERVED | FACT | `f4_per_view_disagreement_20260919T195046Z` |
| `tail53_consensus` | consensus | +2.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail53_rapm` | rapm | +2.37 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail53_box` | box | +1.13 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `tail53_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_bos_mkt` | BOS market | 5.47% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_bos_consensus` | BOS consensus | 22.94% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_bos_rapm` | BOS rapm | 23.52% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_bos_box` | BOS box | 12.90% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_bos_darko` | BOS darko | 13.95% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_bos_label` | BOS label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_sas_mkt` | SAS market | 22.96% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_sas_consensus` | SAS consensus | 15.88% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_sas_rapm` | SAS rapm | 17.98% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_sas_box` | SAS box | 9.79% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_sas_darko` | SAS darko | 11.76% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_sas_label` | SAS label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_okc_mkt` | OKC market | 22.49% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_okc_consensus` | OKC consensus | 12.89% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_okc_rapm` | OKC rapm | 11.87% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_okc_box` | OKC box | 16.55% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_okc_darko` | OKC darko | 17.44% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_okc_label` | OKC label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_phi_mkt` | PHI market | 8.42% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_phi_consensus` | PHI consensus | 4.02% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_phi_rapm` | PHI rapm | 3.37% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_phi_box` | PHI box | 0.75% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_phi_darko` | PHI darko | 3.59% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_phi_label` | PHI label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_hou_mkt` | HOU market | 1.61% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_hou_consensus` | HOU consensus | 6.73% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_hou_rapm` | HOU rapm | 7.58% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_hou_box` | HOU box | 5.90% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_hou_darko` | HOU darko | 7.16% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_hou_label` | HOU label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_det_mkt` | DET market | 3.16% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_det_consensus` | DET consensus | 4.62% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_det_rapm` | DET rapm | 4.74% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_det_box` | DET box | 10.21% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_det_darko` | DET darko | 11.76% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_det_label` | DET label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_nyk_mkt` | NYK market | 8.21% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_nyk_consensus` | NYK consensus | 3.30% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_nyk_rapm` | NYK rapm | 3.41% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_nyk_box` | NYK box | 5.86% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_nyk_darko` | NYK darko | 3.66% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_nyk_label` | NYK label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_den_mkt` | DEN market | 3.16% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_den_consensus` | DEN consensus | 6.04% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_den_rapm` | DEN rapm | 4.57% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_den_box` | DEN box | 8.72% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_den_darko` | DEN darko | 5.40% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_den_label` | DEN label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_min_mkt` | MIN market | 3.16% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_min_consensus` | MIN consensus | 0.86% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_min_rapm` | MIN rapm | 1.25% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_min_box` | MIN box | 2.03% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_min_darko` | MIN darko | 2.59% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260919T195046Z` |
| `pv_min_label` | MIN label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260919T195046Z` |

