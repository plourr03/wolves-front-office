# Final numbers, piece 2

*Run `build_final_numbers_20260929T183504Z`. 1777 figures, every one with a run ID. Anything not here does not go in the piece.*

## 1. The number

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `title` | MIN title probability, mean of four views | 2.76% | MODELED | QUOTABLE AS BAND | `run_sim_20260929T024343Z` |
| `title_lo` | four-view low | 1.83% | MODELED | QUOTABLE AS BAND | `run_sim_20260929T024343Z` |
| `title_hi` | four-view high | 3.89% | MODELED | QUOTABLE AS BAND | `run_sim_20260929T024343Z` |
| `title_aged` | MIN title probability, mean of four views_aged | 3.72% | MODELED | QUOTABLE AS BAND | `run_sim_20260929T061417Z` |
| `title_lo_aged` | four-view low_aged | 2.48% | MODELED | QUOTABLE AS BAND | `run_sim_20260929T061417Z` |
| `title_hi_aged` | four-view high_aged | 5.13% | MODELED | QUOTABLE AS BAND | `run_sim_20260929T061417Z` |
| `mkt_min` | MIN market title odds, proportional de-vig | 3.16% | OBSERVED | QUOTABLE | `market_devig_20260929T061326Z` |
| `mkt_min_rank` | MIN market rank | 6 | OBSERVED | QUOTABLE | `market_devig_20260929T061326Z` |
| `model_min_rank` | MIN model rank | 12 | MODELED | QUOTABLE | `market_devig_20260929T061326Z` |
| `overround` | six-book overround | 21.8% | OBSERVED | FACT | `market_devig_20260929T061326Z` |
| `rankcorr_lo` | model-market rank correlation, lowest view | 0.78 | COMPOSED | QUOTABLE AS BAND | `market_devig_20260929T061326Z` |
| `rankcorr_hi` | model-market rank correlation, highest view | 0.85 | COMPOSED | QUOTABLE AS BAND | `market_devig_20260929T061326Z` |
| `n_disagree` | teams where model and market differ by more than 0.5 points | 19 | COMPOSED | QUOTABLE | `market_devig_20260929T061326Z` |
| `n_allviews` | of those, disagreements where all four views sit on one side | 15 | COMPOSED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `min_view_ranks` | MIN rank in each view | 9 to 14 | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `rankcorr_lo_aged` | model-market rank correlation, lowest view, aged | 0.74 | COMPOSED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260929T094828Z` |
| `rankcorr_hi_aged` | model-market rank correlation, highest view, aged | 0.82 | COMPOSED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260929T094828Z` |
| `n_disagree_aged` | disagreements over 0.5 points, aged | 18 | COMPOSED | QUOTABLE | `r5_honesty_rail_bases_20260929T094828Z` |
| `n_allviews_aged` | of those, all-views, aged | 14 | COMPOSED | QUOTABLE | `r5_honesty_rail_bases_20260929T094828Z` |
| `min_view_ranks_aged` | MIN rank in each view, aged | 7 to 11 | MODELED | QUOTABLE | `r5_honesty_rail_bases_20260929T094828Z` |
| `min_label_aged` | MIN disagreement label, aged | mixed | MODELED | QUOTABLE | `r5_honesty_rail_bases_20260929T094828Z` |
| `min_above_aged` | MIN views above the market, aged | 3 | MODELED | QUOTABLE | `r5_honesty_rail_bases_20260929T094828Z` |
| `min_box_aged` | MIN box view, aged | 3.94% | MODELED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260929T094828Z` |
| `min_darko_aged` | MIN DARKO view, aged | 5.13% | MODELED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260929T094828Z` |
| `model_bos_aged` | BOS model title odds, mean of four views, aged | 14.06% | MODELED | QUOTABLE AS BAND | `r5_honesty_rail_bases_20260929T094828Z` |
| `bos_label_aged` | BOS disagreement label, aged | all-views | MODELED | QUOTABLE | `r5_honesty_rail_bases_20260929T094828Z` |
| `model_bos` | BOS model title odds | 18.12% | MODELED | QUOTABLE AS BAND | `market_devig_20260929T061326Z` |
| `mkt_bos` | BOS market title odds | 5.47% | OBSERVED | QUOTABLE | `market_devig_20260929T061326Z` |
| `model_sas` | SAS model title odds | 13.80% | MODELED | QUOTABLE AS BAND | `market_devig_20260929T061326Z` |
| `mkt_sas` | SAS market title odds | 22.96% | OBSERVED | QUOTABLE | `market_devig_20260929T061326Z` |
| `model_cha` | CHA model title odds | 3.60% | MODELED | QUOTABLE AS BAND | `market_devig_20260929T061326Z` |
| `mkt_cha` | CHA market title odds | 0.81% | OBSERVED | QUOTABLE | `market_devig_20260929T061326Z` |
| `bos_dec_threshold` | Boston December (game 30) threshold, net per 100 | -1.7 | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `bos_dec_game` | December checkpoint game | 30 | ASSUMED | FACT | `n8_watch_list_20260929T100500Z` |
| `bos_range_lo` | Boston model net range low | +3.4 | MODELED | QUOTABLE AS BAND | `n8_watch_list_20260929T100500Z` |
| `bos_range_hi` | Boston model net range high | +10.0 | MODELED | QUOTABLE AS BAND | `n8_watch_list_20260929T100500Z` |
| `dec_noise` | 30-game net rating noise per 100 | 3.1 | OBSERVED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `v_ball_in_pooled_u` | LaMelo Ball in, pooled un-aged mean pp | +0.88 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ball_in_pooled_a` | LaMelo Ball in, pooled aged mean pp | +1.04 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ball_in_tr_u` | LaMelo Ball in, team-rank un-aged mean pp | +1.71 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ball_in_tr_a` | LaMelo Ball in, team-rank aged mean pp | +1.78 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ball_in_cells` | LaMelo Ball in, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ball_in_two_cell` | LaMelo Ball in ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ball_in_label` | verdict label | LaMelo Ball in | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_ball_in_u` | LaMelo Ball in, un-aged mean pp | +0.88 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ball_in_a` | LaMelo Ball in, aged mean pp | +1.04 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ball_in_clear` | LaMelo Ball in, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ball_in_signs` | LaMelo Ball in, sign un-aged / aged | all positive / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ball_in_ships` | LaMelo Ball in ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ball_in_preship` | LaMelo Ball in shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_reid_out_pooled_u` | Naz Reid out, pooled un-aged mean pp | -0.35 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_reid_out_pooled_a` | Naz Reid out, pooled aged mean pp | -0.44 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_reid_out_tr_u` | Naz Reid out, team-rank un-aged mean pp | -0.81 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_reid_out_tr_a` | Naz Reid out, team-rank aged mean pp | -0.83 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_reid_out_cells` | Naz Reid out, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_reid_out_two_cell` | Naz Reid out ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_reid_out_label` | verdict label | Naz Reid out | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_reid_out_u` | Naz Reid out, un-aged mean pp | -0.35 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_reid_out_a` | Naz Reid out, aged mean pp | -0.44 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_reid_out_clear` | Naz Reid out, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_reid_out_signs` | Naz Reid out, sign un-aged / aged | all negative / all negative | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_reid_out_ships` | Naz Reid out ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_reid_out_preship` | Naz Reid out shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_other_departures_pooled_u` | Other departures (a bundle of seven), pooled un-aged mean pp | +0.18 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_other_departures_pooled_a` | Other departures (a bundle of seven), pooled aged mean pp | +0.54 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_other_departures_tr_u` | Other departures (a bundle of seven), team-rank un-aged mean pp | -0.73 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_other_departures_tr_a` | Other departures (a bundle of seven), team-rank aged mean pp | -0.01 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_other_departures_cells` | Other departures (a bundle of seven), views clearing in the four cells | 4/4, 2/4, 4/4, 3/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_other_departures_two_cell` | Other departures (a bundle of seven) ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_other_departures_label` | verdict label | Other departures (a bundle of seven) | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_other_departures_u` | Other departures (a bundle of seven), un-aged mean pp | +0.18 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_other_departures_a` | Other departures (a bundle of seven), aged mean pp | +0.54 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_other_departures_clear` | Other departures (a bundle of seven), views clearing the floor un-aged / aged | 4/4, 2/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_other_departures_signs` | Other departures (a bundle of seven), sign un-aged / aged | mixed / mixed | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_other_departures_ships` | Other departures (a bundle of seven) ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_other_departures_preship` | Other departures (a bundle of seven) shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_randle_out_pooled_u` | Julius Randle out, pooled un-aged mean pp | -0.06 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_randle_out_pooled_a` | Julius Randle out, pooled aged mean pp | +0.18 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_randle_out_tr_u` | Julius Randle out, team-rank un-aged mean pp | -0.32 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_randle_out_tr_a` | Julius Randle out, team-rank aged mean pp | +0.12 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_randle_out_cells` | Julius Randle out, views clearing in the four cells | 3/4, 3/4, 3/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_randle_out_two_cell` | Julius Randle out ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_randle_out_label` | verdict label | Julius Randle out | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_randle_out_u` | Julius Randle out, un-aged mean pp | -0.06 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_randle_out_a` | Julius Randle out, aged mean pp | +0.18 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_randle_out_clear` | Julius Randle out, views clearing the floor un-aged / aged | 3/4, 3/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_randle_out_signs` | Julius Randle out, sign un-aged / aged | mixed / mixed | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_randle_out_ships` | Julius Randle out ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_randle_out_preship` | Julius Randle out shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_dosunmu_retained_pooled_u` | Ayo Dosunmu re-signed, pooled un-aged mean pp | -0.27 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_dosunmu_retained_pooled_a` | Ayo Dosunmu re-signed, pooled aged mean pp | -0.36 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_dosunmu_retained_tr_u` | Ayo Dosunmu re-signed, team-rank un-aged mean pp | -0.40 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_dosunmu_retained_tr_a` | Ayo Dosunmu re-signed, team-rank aged mean pp | -0.44 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_dosunmu_retained_cells` | Ayo Dosunmu re-signed, views clearing in the four cells | 3/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_dosunmu_retained_two_cell` | Ayo Dosunmu re-signed ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_dosunmu_retained_label` | verdict label | Ayo Dosunmu re-signed | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_dosunmu_retained_u` | Ayo Dosunmu re-signed, un-aged mean pp | -0.27 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_dosunmu_retained_a` | Ayo Dosunmu re-signed, aged mean pp | -0.36 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_dosunmu_retained_clear` | Ayo Dosunmu re-signed, views clearing the floor un-aged / aged | 3/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_dosunmu_retained_signs` | Ayo Dosunmu re-signed, sign un-aged / aged | mixed / mixed | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_dosunmu_retained_ships` | Ayo Dosunmu re-signed ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_dosunmu_retained_preship` | Ayo Dosunmu re-signed shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_depth_pooled_u` | Depth signings and re-signings, pooled un-aged mean pp | +0.10 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_depth_pooled_a` | Depth signings and re-signings, pooled aged mean pp | +0.19 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_depth_tr_u` | Depth signings and re-signings, team-rank un-aged mean pp | +0.72 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_depth_tr_a` | Depth signings and re-signings, team-rank aged mean pp | +0.83 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_depth_cells` | Depth signings and re-signings, views clearing in the four cells | 2/4, 3/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_depth_two_cell` | Depth signings and re-signings ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_depth_label` | verdict label | Depth signings and re-signings | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_depth_u` | Depth signings and re-signings, un-aged mean pp | +0.10 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_depth_a` | Depth signings and re-signings, aged mean pp | +0.19 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_depth_clear` | Depth signings and re-signings, views clearing the floor un-aged / aged | 2/4, 3/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_depth_signs` | Depth signings and re-signings, sign un-aged / aged | mixed / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_depth_ships` | Depth signings and re-signings ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_depth_preship` | Depth signings and re-signings shipped before D85 | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_kuminga_in_pooled_u` | Kuminga in (pooled), pooled un-aged mean pp | +0.02 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_kuminga_in_pooled_a` | Kuminga in (pooled), pooled aged mean pp | +0.11 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_kuminga_in_tr_u` | Kuminga in (pooled), team-rank un-aged mean pp | +0.19 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_kuminga_in_tr_a` | Kuminga in (pooled), team-rank aged mean pp | +0.35 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_kuminga_in_cells` | Kuminga in (pooled), views clearing in the four cells | 3/4, 4/4, 3/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_kuminga_in_two_cell` | Kuminga in (pooled) ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_kuminga_in_label` | verdict label | Kuminga in (pooled) | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_kuminga_in_u` | Kuminga in (pooled), un-aged mean pp | +0.02 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_kuminga_in_a` | Kuminga in (pooled), aged mean pp | +0.11 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_kuminga_in_clear` | Kuminga in (pooled), views clearing the floor un-aged / aged | 3/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_kuminga_in_signs` | Kuminga in (pooled), sign un-aged / aged | mixed / mixed | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_kuminga_in_ships` | Kuminga in (pooled) ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_kuminga_in_preship` | Kuminga in (pooled) shipped before D85 | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ddv_injury_pooled_u` | DiVincenzo's Achilles (not a transaction), pooled un-aged mean pp | -0.42 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ddv_injury_pooled_a` | DiVincenzo's Achilles (not a transaction), pooled aged mean pp | -0.35 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ddv_injury_tr_u` | DiVincenzo's Achilles (not a transaction), team-rank un-aged mean pp | -0.76 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ddv_injury_tr_a` | DiVincenzo's Achilles (not a transaction), team-rank aged mean pp | -0.58 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ddv_injury_cells` | DiVincenzo's Achilles (not a transaction), views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ddv_injury_two_cell` | DiVincenzo's Achilles (not a transaction) ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_ddv_injury_label` | verdict label | DiVincenzo's Achilles (not a transaction) | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_ddv_injury_u` | DiVincenzo's Achilles (not a transaction), un-aged mean pp | -0.42 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ddv_injury_a` | DiVincenzo's Achilles (not a transaction), aged mean pp | -0.35 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ddv_injury_clear` | DiVincenzo's Achilles (not a transaction), views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ddv_injury_signs` | DiVincenzo's Achilles (not a transaction), sign un-aged / aged | all negative / all negative | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ddv_injury_ships` | DiVincenzo's Achilles (not a transaction) ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_ddv_injury_preship` | DiVincenzo's Achilles (not a transaction) shipped before D85 | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_A_c3_default_williams_pooled_u` | Kuminga slot, the default fill (Cody Williams), pooled un-aged mean pp | +0.51 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_A_c3_default_williams_pooled_a` | Kuminga slot, the default fill (Cody Williams), pooled aged mean pp | +0.67 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_A_c3_default_williams_tr_u` | Kuminga slot, the default fill (Cody Williams), team-rank un-aged mean pp | +1.40 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_A_c3_default_williams_tr_a` | Kuminga slot, the default fill (Cody Williams), team-rank aged mean pp | +1.73 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_A_c3_default_williams_cells` | Kuminga slot, the default fill (Cody Williams), views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_A_c3_default_williams_two_cell` | Kuminga slot, the default fill (Cody Williams) ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_A_c3_default_williams_label` | verdict label | Kuminga slot, the default fill (Cody Williams) | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_A_c3_default_williams_u` | Kuminga slot, the default fill (Cody Williams), un-aged mean pp | +1.40 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_A_c3_default_williams_a` | Kuminga slot, the default fill (Cody Williams), aged mean pp | +1.73 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_A_c3_default_williams_clear` | Kuminga slot, the default fill (Cody Williams), views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_A_c3_default_williams_signs` | Kuminga slot, the default fill (Cody Williams), sign un-aged / aged | all positive / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_A_c3_default_williams_ships` | Kuminga slot, the default fill (Cody Williams) ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_A_c3_default_williams_preship` | Kuminga slot, the default fill (Cody Williams) shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_C_mcdaniels_slides_pooled_u` | Kuminga slot, McDaniels slides, pooled un-aged mean pp | +0.47 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_C_mcdaniels_slides_pooled_a` | Kuminga slot, McDaniels slides, pooled aged mean pp | +0.63 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_C_mcdaniels_slides_tr_u` | Kuminga slot, McDaniels slides, team-rank un-aged mean pp | +1.34 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_C_mcdaniels_slides_tr_a` | Kuminga slot, McDaniels slides, team-rank aged mean pp | +1.66 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_C_mcdaniels_slides_cells` | Kuminga slot, McDaniels slides, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_C_mcdaniels_slides_two_cell` | Kuminga slot, McDaniels slides ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_C_mcdaniels_slides_label` | verdict label | Kuminga slot, McDaniels slides | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_C_mcdaniels_slides_u` | Kuminga slot, McDaniels slides, un-aged mean pp | +1.34 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_C_mcdaniels_slides_a` | Kuminga slot, McDaniels slides, aged mean pp | +1.66 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_C_mcdaniels_slides_clear` | Kuminga slot, McDaniels slides, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_C_mcdaniels_slides_signs` | Kuminga slot, McDaniels slides, sign un-aged / aged | all positive / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_C_mcdaniels_slides_ships` | Kuminga slot, McDaniels slides ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_C_mcdaniels_slides_preship` | Kuminga slot, McDaniels slides shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_D_beringer_fills_pooled_u` | Kuminga slot, Beringer fills, pooled un-aged mean pp | -0.78 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_D_beringer_fills_pooled_a` | Kuminga slot, Beringer fills, pooled aged mean pp | -1.42 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_D_beringer_fills_tr_u` | Kuminga slot, Beringer fills, team-rank un-aged mean pp | -1.48 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_D_beringer_fills_tr_a` | Kuminga slot, Beringer fills, team-rank aged mean pp | -2.48 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_D_beringer_fills_cells` | Kuminga slot, Beringer fills, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_D_beringer_fills_two_cell` | Kuminga slot, Beringer fills ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_D_beringer_fills_label` | verdict label | Kuminga slot, Beringer fills | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_D_beringer_fills_u` | Kuminga slot, Beringer fills, un-aged mean pp | -1.48 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_D_beringer_fills_a` | Kuminga slot, Beringer fills, aged mean pp | -2.48 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_D_beringer_fills_clear` | Kuminga slot, Beringer fills, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_D_beringer_fills_signs` | Kuminga slot, Beringer fills, sign un-aged / aged | all negative / all negative | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_D_beringer_fills_ships` | Kuminga slot, Beringer fills ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_D_beringer_fills_preship` | Kuminga slot, Beringer fills shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_E_tight_rule_F_or_FC_pooled_u` | Kuminga slot, tight eligibility rule, pooled un-aged mean pp | +0.51 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_E_tight_rule_F_or_FC_pooled_a` | Kuminga slot, tight eligibility rule, pooled aged mean pp | +0.67 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_E_tight_rule_F_or_FC_tr_u` | Kuminga slot, tight eligibility rule, team-rank un-aged mean pp | +1.40 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_E_tight_rule_F_or_FC_tr_a` | Kuminga slot, tight eligibility rule, team-rank aged mean pp | +1.73 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_E_tight_rule_F_or_FC_cells` | Kuminga slot, tight eligibility rule, views clearing in the four cells | 4/4, 4/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_E_tight_rule_F_or_FC_two_cell` | Kuminga slot, tight eligibility rule ships on the two-cell rule (pooled only) | yes | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_E_tight_rule_F_or_FC_label` | verdict label | Kuminga slot, tight eligibility rule | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_E_tight_rule_F_or_FC_u` | Kuminga slot, tight eligibility rule, un-aged mean pp | +1.40 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_E_tight_rule_F_or_FC_a` | Kuminga slot, tight eligibility rule, aged mean pp | +1.73 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_E_tight_rule_F_or_FC_clear` | Kuminga slot, tight eligibility rule, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_E_tight_rule_F_or_FC_signs` | Kuminga slot, tight eligibility rule, sign un-aged / aged | all positive / all positive | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_E_tight_rule_F_or_FC_ships` | Kuminga slot, tight eligibility rule ships | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_E_tight_rule_F_or_FC_preship` | Kuminga slot, tight eligibility rule shipped before D85 | yes | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_B_lyles_fills_pooled_u` | Kuminga slot, Lyles fills, pooled un-aged mean pp | +0.05 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_B_lyles_fills_pooled_a` | Kuminga slot, Lyles fills, pooled aged mean pp | -0.01 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_B_lyles_fills_tr_u` | Kuminga slot, Lyles fills, team-rank un-aged mean pp | +0.12 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_B_lyles_fills_tr_a` | Kuminga slot, Lyles fills, team-rank aged mean pp | +0.04 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_B_lyles_fills_cells` | Kuminga slot, Lyles fills, views clearing in the four cells | 3/4, 3/4, 4/4, 4/4 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_B_lyles_fills_two_cell` | Kuminga slot, Lyles fills ships on the two-cell rule (pooled only) | no | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `v_B_lyles_fills_label` | verdict label | Kuminga slot, Lyles fills | FACT | FACT | `w2_aging_gate_20260929T094601Z` |
| `v_B_lyles_fills_u` | Kuminga slot, Lyles fills, un-aged mean pp | +0.12 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_B_lyles_fills_a` | Kuminga slot, Lyles fills, aged mean pp | +0.04 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_B_lyles_fills_clear` | Kuminga slot, Lyles fills, views clearing the floor un-aged / aged | 4/4, 4/4 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_B_lyles_fills_signs` | Kuminga slot, Lyles fills, sign un-aged / aged | mixed / mixed | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_B_lyles_fills_ships` | Kuminga slot, Lyles fills ships | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `v_B_lyles_fills_preship` | Kuminga slot, Lyles fills shipped before D85 | no | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `n_ship` | verdicts that ship | 7 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `n_ship_pre` | verdicts that shipped before D85 | 9 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `n_retired` | verdicts that shipped before D85 and do not now | 3 | MODELED | QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `n_ship_two_cell` | verdicts that ship on the two-cell rule (pooled only) | 7 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `n_candidates` | candidate verdicts tested | 13 | FACT | FACT | `r7_allocator_agreement_20260929T095016Z` |
| `k_min_pooled` | Kuminga minutes under the pooled allocator | 22.1 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `k_min_teamrank` | Kuminga minutes under the teamrank allocator | 26.1 | MODELED | QUOTABLE | `r7_allocator_agreement_20260929T095016Z` |
| `d85_residual` | post-D85 attribution roster vs direct simulation, worst view pp, both bases | 0.09 | MODELED | QUOTABLE | `r5_shapley_williams_20260929T094603Z` |
| `d85_pooled_gap` | post-D85 pooled attribution rule vs direct simulation, worst view pp, both bases | 2.01 | MODELED | QUOTABLE | `r5_shapley_williams_20260929T094603Z` |
| `d85_gap_before` | pre-D85 attribution roster vs direct simulation, worst view pp, un-aged | 0.09 | MODELED | QUOTABLE | `r5_shapley_williams_20260929T094603Z` |
| `williams_bio` | Cody Williams consensus impact | -4.39 | MODELED | QUOTABLE | `build_rotations_20260929T024337Z` |
| `anderson_u` | Kyle Anderson departure, un-aged pp | +0.13 | MODELED | QUOTABLE | `r2_departures_20260929T094830Z` |
| `anderson_a` | Kyle Anderson departure, aged pp | +0.44 | MODELED | QUOTABLE | `r2_departures_20260929T094830Z` |
| `anderson_clear` | Kyle Anderson departure, views clearing un-aged / aged | 2/4, 4/4 | MODELED | QUOTABLE | `r2_departures_20260929T094830Z` |
| `n_dep_ship` | departures that ship on their own | 0 | MODELED | QUOTABLE | `r2_departures_20260929T094830Z` |
| `n_departures` | players in the other-departures bundle | 7 | FACT | FACT | `r2_departures_20260929T094830Z` |
| `sims` | simulations per f-curve view | 200,000 | ASSUMED | FACT | `merge_fcurve_parts_20260929T061250Z` |
| `per100` | rating basis, possessions | 100 | FACT | FACT | `n8_watch_list_20260929T100500Z` |

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
| `n4_sd13` | true matchup effect SD, 2013-26, points per game | 0.65 | OBSERVED | QUOTABLE | `n4_versatility_index_20260929T181847Z` |
| `n4_sd13_up` | upper 95%, 2013-26 | 1.77 | OBSERVED | QUOTABLE | `n4_versatility_index_20260929T181847Z` |
| `n4_sd97` | true matchup effect SD, 1997-2026 | 0.00 | OBSERVED | QUOTABLE | `n4_versatility_index_20260929T181847Z` |
| `n4_sd97_up` | upper 95%, 1997-2026 | 1.25 | OBSERVED | QUOTABLE | `n4_versatility_index_20260929T181847Z` |
| `n4_series_up` | series points at the tighter upper bound | 9 | MODELED | QUOTABLE | `n4_versatility_index_20260929T181847Z` |
| `n4_rankcorr` | spread vs own net rank correlation outside the field | 1.00 | MODELED | QUOTABLE | `n4_versatility_index_20260929T181847Z` |
| `n4_start13` | first season, primary window | 2013-14 | FACT | FACT | `n4_versatility_index_20260929T181847Z` |
| `n4_start97` | first season, extended window | 1997-98 | FACT | FACT | `n4_versatility_index_20260929T181847Z` |
| `n4_games97` | regular-season games, 1997-2026 | 34,357 | OBSERVED | FACT | `n4_versatility_index_20260929T181847Z` |
| `m3_se30` | matchup SE at 30 possessions | 0.14 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260929T100601Z` |
| `m3_norm_lo` | primary-defender norm, low | 0.05 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260929T100601Z` |
| `m3_norm_hi` | primary-defender norm, high | 0.10 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260929T100601Z` |
| `m3_edges` | matchups beyond the norm by 2 SEs, above | 2 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260929T100601Z` |
| `m3_rows` | observed West-field primary matchups | 79 | OBSERVED | FACT | `m3_opponent_cards_20260929T100601Z` |
| `m3_chance` | expected by chance, above | 2.3 | OBSERVED | QUOTABLE | `m3_opponent_cards_20260929T100601Z` |
| `h2_n` | clean seasons | 11 | FACT | FACT | `champions_table_20260929T061328Z` |
| `h2_fav` | favourite won | 4 | OBSERVED | QUOTABLE | `champions_table_20260929T061328Z` |
| `h2_top3` | champion from the top three | 8 | OBSERVED | QUOTABLE | `champions_table_20260929T061328Z` |
| `h2_top5` | champion from the top five | 10 | OBSERVED | QUOTABLE | `champions_table_20260929T061328Z` |
| `h2_lo` | champions' preseason price, low | 4.01% | OBSERVED | QUOTABLE | `champions_table_20260929T061328Z` |
| `h2_hi` | champions' preseason price, high | 57.65% | OBSERVED | QUOTABLE | `champions_table_20260929T061328Z` |
| `h2_median` | champions' preseason price, median | 12.75% | OBSERVED | QUOTABLE | `champions_table_20260929T061328Z` |
| `h2_worst_rank` | worst preseason rank of a champion | 9 | OBSERVED | QUOTABLE | `champions_table_20260929T061328Z` |
| `h3_n_champ` | champions in the comparison | 11 | OBSERVED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_n_non` | preseason top-5 non-champions, eleven seasons | 48 | OBSERVED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_n_sep` | team-level features that separate, eleven seasons | 0 | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_n_feat` | team-level features compared, eleven seasons | 19 | OBSERVED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_sep_list` | the separating team-level features | none | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3s_n_non` | preseason top-5 non-champions, three seasons (style) | 14 | OBSERVED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3s_n_sep` | style features that separate, three seasons | 0 | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3s_n_feat` | style features compared, three seasons | 8 | OBSERVED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3s11_n_sep` | style features that separate, eleven seasons (for the record) | 0 | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_pre_implied_lo` | preseason implied %, champions' low | 4.01 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_pre_implied_hi` | preseason implied %, champions' high | 57.65 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_pre_implied_inside` | preseason implied %, non-champions inside the range | 44 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_pre_rank_lo` | preseason rank, champions' low | 1.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_pre_rank_hi` | preseason rank, champions' high | 9.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_pre_rank_inside` | preseason rank, non-champions inside the range | 48 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_nrtg_rank_lo` | net rating rank, champions' low | 1.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_nrtg_rank_hi` | net rating rank, champions' high | 6.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_nrtg_rank_inside` | net rating rank, non-champions inside the range | 21 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_ortg_rank_lo` | offence rank, champions' low | 1.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_ortg_rank_hi` | offence rank, champions' high | 17.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_ortg_rank_inside` | offence rank, non-champions inside the range | 43 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_drtg_rank_lo` | defence rank, champions' low | 1.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_drtg_rank_hi` | defence rank, champions' high | 14.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_drtg_rank_inside` | defence rank, non-champions inside the range | 34 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_post_asb_rank_lo` | post-All-Star net rank, champions' low | 1.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_post_asb_rank_hi` | post-All-Star net rank, champions' high | 18.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_post_asb_rank_inside` | post-All-Star net rank, non-champions inside the range | 42 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_seed_lo` | seed, champions' low | 1.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_seed_hi` | seed, champions' high | 3.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_seed_inside` | seed, non-champions inside the range | 22 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_po_minus_rs_lo` | playoff minus regular-season net, champions' low | -4.13 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_po_minus_rs_hi` | playoff minus regular-season net, champions' high | 9.07 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_po_minus_rs_inside` | playoff minus regular-season net, non-champions inside the range | 17 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_best_vorp_lo` | best player VORP, champions' low | 3.30 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_best_vorp_hi` | best player VORP, champions' high | 8.90 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_best_vorp_inside` | best player VORP, non-champions inside the range | 39 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_age_lo` | top-8 age, champions' low | 25.50 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_age_hi` | top-8 age, champions' high | 29.70 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_age_inside` | top-8 age, non-champions inside the range | 30 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_returning_appear_lo` | top-8 returning, by appearance, champions' low | 4.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_returning_appear_hi` | top-8 returning, by appearance, champions' high | 8.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_returning_appear_inside` | top-8 returning, by appearance, non-champions inside the range | 42 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_returning_contract_lo` | top-8 returning, by contract, champions' low | 4.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_returning_contract_hi` | top-8 returning, by contract, champions' high | 8.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_returning_contract_inside` | top-8 returning, by contract, non-champions inside the range | 43 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_returning_share_appear_lo` | returning share of playoff minutes, by appearance, champions' low | 0.52 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_returning_share_appear_hi` | returning share of playoff minutes, by appearance, champions' high | 0.91 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_returning_share_appear_inside` | returning share of playoff minutes, by appearance, non-champions inside the range | 30 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_returning_share_contract_lo` | returning share of playoff minutes, by contract, champions' low | 0.56 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_returning_share_contract_hi` | returning share of playoff minutes, by contract, champions' high | 0.91 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_returning_share_contract_inside` | returning share of playoff minutes, by contract, non-champions inside the range | 31 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_rs_games_missed_lo` | top-8 regular-season games missed, champions' low | 54.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_rs_games_missed_hi` | top-8 regular-season games missed, champions' high | 154.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_rs_games_missed_inside` | top-8 regular-season games missed, non-champions inside the range | 38 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_po_games_missed_lo` | top-8 playoff games missed, champions' low | 1.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_po_games_missed_hi` | top-8 playoff games missed, champions' high | 15.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top8_po_games_missed_inside` | top-8 playoff games missed, non-champions inside the range | 33 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top5_share_rs_lo` | top-five minute share, regular season, champions' low | 0.51 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top5_share_rs_hi` | top-five minute share, regular season, champions' high | 0.60 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top5_share_rs_inside` | top-five minute share, regular season, non-champions inside the range | 25 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top5_share_po_lo` | top-five minute share, playoffs, champions' low | 0.63 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top5_share_po_hi` | top-five minute share, playoffs, champions' high | 0.76 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_top5_share_po_inside` | top-five minute share, playoffs, non-champions inside the range | 33 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_tighten_lo` | top-five share, playoffs minus regular season, champions' low | 0.07 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_tighten_hi` | top-five share, playoffs minus regular season, champions' high | 0.19 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3_tighten_inside` | top-five share, playoffs minus regular season, non-champions inside the range | 32 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_n_champ` | tendency test: champions | 11 | OBSERVED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_n_non` | tendency test: non-champions | 48 | OBSERVED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_lean_p` | tendency test: a feature leans below this two-sided p | 0.05 | ASSUMED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_n_lean` | features that lean | 3 | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_lean_list` | the features that lean | net rating rank; seed; defence rank | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_n_tests` | tendency test: features tested | 5 | OBSERVED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_bonf_p` | tendency test: Bonferroni threshold, 0.05 over the features tested | 0.01 | ASSUMED | FACT | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_bonf_list` | leans that survive the Bonferroni threshold | seed | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_bonf_fail_list` | leans that do not survive it | net rating rank; defence rank | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_nrtg_rank_champ_median` | net rating rank, champions' median | 4 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_nrtg_rank_non_median` | net rating rank, non-champions' median | 7 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_nrtg_rank_p` | net rating rank, two-sided rank-sum p | 0.010 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_post_asb_rank_champ_median` | post-All-Star net rank, champions' median | 5 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_post_asb_rank_non_median` | post-All-Star net rank, non-champions' median | 10 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_post_asb_rank_p` | post-All-Star net rank, two-sided rank-sum p | 0.212 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_seed_champ_median` | seed, champions' median | 1 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_seed_non_median` | seed, non-champions' median | 4 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_seed_p` | seed, two-sided rank-sum p | 0.002 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_ortg_rank_champ_median` | offence rank, champions' median | 3 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_ortg_rank_non_median` | offence rank, non-champions' median | 7 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_ortg_rank_p` | offence rank, two-sided rank-sum p | 0.114 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_drtg_rank_champ_median` | defence rank, champions' median | 5 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_drtg_rank_non_median` | defence rank, non-champions' median | 12 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h3t_drtg_rank_p` | defence rank, two-sided rank-sum p | 0.033 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2015_16_best` | 2015-16 champion's best player by VORP | LeBron James | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2015_16_best_vorp` | 2015-16 champion's best player, VORP | 7.5 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2015_16_ortg_rank` | 2015-16 champion's offence rank | 3 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2015_16_drtg_rank` | 2015-16 champion's defence rank | 10 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2016_17_best` | 2016-17 champion's best player by VORP | Stephen Curry | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2016_17_best_vorp` | 2016-17 champion's best player, VORP | 5.9 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2016_17_ortg_rank` | 2016-17 champion's offence rank | 1 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2016_17_drtg_rank` | 2016-17 champion's defence rank | 2 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2017_18_best` | 2017-18 champion's best player by VORP | Kevin Durant | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2017_18_best_vorp` | 2017-18 champion's best player, VORP | 5.5 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2017_18_ortg_rank` | 2017-18 champion's offence rank | 3 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2017_18_drtg_rank` | 2017-18 champion's defence rank | 11 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2018_19_best` | 2018-19 champion's best player by VORP | Kawhi Leonard | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2018_19_best_vorp` | 2018-19 champion's best player, VORP | 4.7 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2018_19_ortg_rank` | 2018-19 champion's offence rank | 5 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2018_19_drtg_rank` | 2018-19 champion's defence rank | 5 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2019_20_best` | 2019-20 champion's best player by VORP | LeBron James | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2019_20_best_vorp` | 2019-20 champion's best player, VORP | 6.1 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2019_20_ortg_rank` | 2019-20 champion's offence rank | 11 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2019_20_drtg_rank` | 2019-20 champion's defence rank | 3 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2020_21_best` | 2020-21 champion's best player by VORP | Giannis Antetokounmpo | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2020_21_best_vorp` | 2020-21 champion's best player, VORP | 5.6 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2020_21_ortg_rank` | 2020-21 champion's offence rank | 5 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2020_21_drtg_rank` | 2020-21 champion's defence rank | 10 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2021_22_best` | 2021-22 champion's best player by VORP | Stephen Curry | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2021_22_best_vorp` | 2021-22 champion's best player, VORP | 4.4 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2021_22_ortg_rank` | 2021-22 champion's offence rank | 17 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2021_22_drtg_rank` | 2021-22 champion's defence rank | 1 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2022_23_best` | 2022-23 champion's best player by VORP | Nikola Jokić | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2022_23_best_vorp` | 2022-23 champion's best player, VORP | 8.8 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2022_23_ortg_rank` | 2022-23 champion's offence rank | 5 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2022_23_drtg_rank` | 2022-23 champion's defence rank | 14 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2023_24_best` | 2023-24 champion's best player by VORP | Jayson Tatum | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2023_24_best_vorp` | 2023-24 champion's best player, VORP | 4.7 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2023_24_ortg_rank` | 2023-24 champion's offence rank | 1 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2023_24_drtg_rank` | 2023-24 champion's defence rank | 3 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2024_25_best` | 2024-25 champion's best player by VORP | Shai Gilgeous-Alexander | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2024_25_best_vorp` | 2024-25 champion's best player, VORP | 8.9 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2024_25_ortg_rank` | 2024-25 champion's offence rank | 3 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2024_25_drtg_rank` | 2024-25 champion's defence rank | 1 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2025_26_best` | 2025-26 champion's best player by VORP | Jalen Brunson | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2025_26_best_vorp` | 2025-26 champion's best player, VORP | 3.3 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2025_26_ortg_rank` | 2025-26 champion's offence rank | 3 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h1_2025_26_drtg_rank` | 2025-26 champion's defence rank | 7 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_pre_implied` | Minnesota, preseason implied % (2026-27 (known now)) | 3.16 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_pre_implied_status` | Minnesota, preseason implied %: status | outside, short of it | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_pre_rank` | Minnesota, preseason rank (2026-27 (known now)) | 6.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_pre_rank_status` | Minnesota, preseason rank: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_nrtg_rank` | Minnesota, net rating rank (2025-26 actual) | 10.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_nrtg_rank_status` | Minnesota, net rating rank: status | outside, short of it | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_ortg_rank` | Minnesota, offence rank (2025-26 actual) | 12.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_ortg_rank_status` | Minnesota, offence rank: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_drtg_rank` | Minnesota, defence rank (2025-26 actual) | 8.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_drtg_rank_status` | Minnesota, defence rank: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_post_asb_rank` | Minnesota, post-All-Star net rank (2025-26 actual) | 18.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_post_asb_rank_status` | Minnesota, post-All-Star net rank: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_seed` | Minnesota, seed (2025-26 actual) | 6.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_seed_status` | Minnesota, seed: status | outside, short of it | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_po_minus_rs` | Minnesota, playoff minus regular-season net (2025-26 actual) | -8.96 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_po_minus_rs_status` | Minnesota, playoff minus regular-season net: status | outside, short of it | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_best_vorp` | Minnesota, best player VORP (2025-26 actual) | 3.50 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_best_vorp_status` | Minnesota, best player VORP: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_age` | Minnesota, top-8 age (2025-26 actual) | 28.80 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_age_status` | Minnesota, top-8 age: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_returning_appear` | Minnesota, top-8 returning, by appearance (2026-27 (known now)) | 6.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_returning_appear_status` | Minnesota, top-8 returning, by appearance: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_returning_contract` | Minnesota, top-8 returning, by contract (2026-27 (known now)) | 6.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_returning_contract_status` | Minnesota, top-8 returning, by contract: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_returning_share_appear` | Minnesota, returning share of playoff minutes, by appearance (2026-27 (known now)) | 0.72 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_returning_share_appear_status` | Minnesota, returning share of playoff minutes, by appearance: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_returning_share_contract` | Minnesota, returning share of playoff minutes, by contract (2026-27 (known now)) | 0.72 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_returning_share_contract_status` | Minnesota, returning share of playoff minutes, by contract: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_rs_games_missed` | Minnesota, top-8 regular-season games missed (2025-26 actual) | 117.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_rs_games_missed_status` | Minnesota, top-8 regular-season games missed: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_po_games_missed` | Minnesota, top-8 playoff games missed (2025-26 actual) | 8.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top8_po_games_missed_status` | Minnesota, top-8 playoff games missed: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top5_share_rs` | Minnesota, top-five minute share, regular season (2025-26 actual) | 0.61 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top5_share_rs_status` | Minnesota, top-five minute share, regular season: status | outside, above | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top5_share_po` | Minnesota, top-five minute share, playoffs (2025-26 actual) | 0.64 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top5_share_po_status` | Minnesota, top-five minute share, playoffs: status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_tighten` | Minnesota, top-five share, playoffs minus regular season (2025-26 actual) | 0.03 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_tighten_status` | Minnesota, top-five share, playoffs minus regular season: status | outside, short of it | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_pace_z` | Minnesota, pace (z) (2025-26 actual) | 0.55 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_pace_z_status` | Minnesota, pace (z): status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_fg3a_z` | Minnesota, three-point rate (z) (2025-26 actual) | 0.12 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_fg3a_z_status` | Minnesota, three-point rate (z): status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_oreb_z` | Minnesota, offensive rebound rate (z) (2025-26 actual) | -0.10 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_oreb_z_status` | Minnesota, offensive rebound rate (z): status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_opp_tov_z` | Minnesota, turnovers forced (z) (2025-26 actual) | 0.24 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_opp_tov_z_status` | Minnesota, turnovers forced (z): status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_def_share_z` | Minnesota, defence share (z) (2025-26 actual) | 0.43 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_def_share_z_status` | Minnesota, defence share (z): status | outside, above | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_rim_rate` | Minnesota, rim rate (z) (2025-26 actual) | 0.32 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_rim_rate_status` | Minnesota, rim rate (z): status | outside, above | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_size` | Minnesota, size (z) (2025-26 actual) | 0.00 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_size_status` | Minnesota, size (z): status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top3` | Minnesota, top-three minutes share (z) (2025-26 actual) | 0.41 | OBSERVED | QUOTABLE | `h1_h3_h5_profile_20260929T100612Z` |
| `h5_top3_status` | Minnesota, top-three minutes share (z): status | inside the champions' range | OBSERVED | DESCRIPTIVE | `h1_h3_h5_profile_20260929T100612Z` |
| `nyk_mkt` | Knicks preseason market price | 8.27% | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_rank` | Knicks preseason market rank | 4 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_wt` | Knicks win total | 53.5 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_wins` | Knicks wins | 53 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_model` | our model's Knicks price | 4.63% | MODELED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_rs` | Knicks regular-season margin | +6.33 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_pre` | before the break | +6.16 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_post` | after the break | +6.67 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_po_rec` | Knicks playoff record | 16-3 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_po` | Knicks playoff margin | +14.89 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_lift` | Knicks playoff lift | +8.57 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_po_teams` | playoff teams | 16 | OBSERVED | FACT | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_lift_mean` | Knicks lift_mean | -7.39 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_cmp_lift` | Knicks cmp_lift | -9.19 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_cmp_lift_rank` | Knicks cmp_lift_rank | 11 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_n_positive_lift` | Knicks n_positive_lift | 1 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_top5_rs_games_missed` | Knicks top5_rs_games_missed | 46 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_top5_po_games_missed` | Knicks top5_po_games_missed | 2 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_top5_share_rs` | Knicks top5_share_rs | 0.579 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |
| `nyk_top5_share_po` | Knicks top5_share_po | 0.673 | OBSERVED | QUOTABLE | `h4_knicks_case_file_20260924T192303Z` |

## 3. What the odds can't see

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `n5_min_full` | MIN full-roster title odds | 2.66% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_drop` | MIN mean drop | 1.47 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_share` | MIN share of odds lost | 55% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_net` | MIN mean net lost per removal | 2.91 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_min_big` | MIN largest single net loss | 3.72 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_min_bigname` | MIN largest single loss, player | Rudy Gobert | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_min_po` | MIN mean net lost, playoff rollup | 3.45 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_min_edwards_drop` | MIN without Anthony Edwards for the playoffs, title odds lost, points | 1.81 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_edwards_share` | MIN without Anthony Edwards for the playoffs, share of title odds lost | 68% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_mcdaniels_drop` | MIN without Jaden McDaniels for the playoffs, title odds lost, points | 0.94 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_mcdaniels_share` | MIN without Jaden McDaniels for the playoffs, share of title odds lost | 35% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_ball_drop` | MIN without LaMelo Ball for the playoffs, title odds lost, points | 1.77 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_ball_share` | MIN without LaMelo Ball for the playoffs, share of title odds lost | 66% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_gobert_drop` | MIN without Rudy Gobert for the playoffs, title odds lost, points | 1.68 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_gobert_share` | MIN without Rudy Gobert for the playoffs, share of title odds lost | 63% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_min_n_60` | MIN players whose playoff absence costs at least 60% of the odds | 3 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_min_n_half` | MIN players whose playoff absence costs at least half of the odds | 3 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_okc_full` | OKC full-roster title odds | 14.73% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_drop` | OKC mean drop | 6.07 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_share` | OKC share of odds lost | 41% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_net` | OKC mean net lost per removal | 2.73 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_okc_big` | OKC largest single net loss | 4.89 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_okc_bigname` | OKC largest single loss, player | Shai Gilgeous-Alexander | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_okc_po` | OKC mean net lost, playoff rollup | 3.01 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_okc_holmgren_drop` | OKC without Chet Holmgren for the playoffs, title odds lost, points | 6.56 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_holmgren_share` | OKC without Chet Holmgren for the playoffs, share of title odds lost | 45% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_hartenstein_drop` | OKC without Isaiah Hartenstein for the playoffs, title odds lost, points | 3.56 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_hartenstein_share` | OKC without Isaiah Hartenstein for the playoffs, share of title odds lost | 24% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_williams_drop` | OKC without Jalen Williams for the playoffs, title odds lost, points | 1.81 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_williams_share` | OKC without Jalen Williams for the playoffs, share of title odds lost | 12% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_gilgeousalexander_drop` | OKC without Shai Gilgeous-Alexander for the playoffs, title odds lost, points | 9.83 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_gilgeousalexander_share` | OKC without Shai Gilgeous-Alexander for the playoffs, share of title odds lost | 67% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_okc_n_60` | OKC players whose playoff absence costs at least 60% of the odds | 1 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_okc_n_half` | OKC players whose playoff absence costs at least half of the odds | 1 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_sas_full` | SAS full-roster title odds | 13.68% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_drop` | SAS mean drop | 6.03 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_share` | SAS share of odds lost | 44% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_net` | SAS mean net lost per removal | 2.70 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_sas_big` | SAS largest single net loss | 5.26 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_sas_bigname` | SAS largest single loss, player | Victor Wembanyama | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_sas_po` | SAS mean net lost, playoff rollup | 2.83 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_sas_fox_drop` | SAS without De'Aaron Fox for the playoffs, title odds lost, points | 4.47 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_fox_share` | SAS without De'Aaron Fox for the playoffs, share of title odds lost | 33% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_harper_drop` | SAS without Dylan Harper for the playoffs, title odds lost, points | 4.38 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_harper_share` | SAS without Dylan Harper for the playoffs, share of title odds lost | 32% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_harris_drop` | SAS without Tobias Harris for the playoffs, title odds lost, points | 3.45 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_harris_share` | SAS without Tobias Harris for the playoffs, share of title odds lost | 25% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_wembanyama_drop` | SAS without Victor Wembanyama for the playoffs, title odds lost, points | 10.15 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_wembanyama_share` | SAS without Victor Wembanyama for the playoffs, share of title odds lost | 74% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095141Z` |
| `n5_sas_n_60` | SAS players whose playoff absence costs at least 60% of the odds | 1 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_sas_n_half` | SAS players whose playoff absence costs at least half of the odds | 1 | MODELED | QUOTABLE | `n5_fragility_20260929T095141Z` |
| `n5_min_full_aged` | MIN full-roster title odds_aged | 3.71% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_drop_aged` | MIN mean drop_aged | 1.68 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_share_aged` | MIN share of odds lost_aged | 45% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_net_aged` | MIN mean net lost per removal_aged | 2.36 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_min_big_aged` | MIN largest single net loss_aged | 2.99 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_min_bigname_aged` | MIN largest single loss, player_aged | Anthony Edwards | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_min_edwards_drop_aged` | MIN without Anthony Edwards for the playoffs, title odds lost, points_aged | 2.23 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_edwards_share_aged` | MIN without Anthony Edwards for the playoffs, share of title odds lost_aged | 60% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_mcdaniels_drop_aged` | MIN without Jaden McDaniels for the playoffs, title odds lost, points_aged | 1.09 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_mcdaniels_share_aged` | MIN without Jaden McDaniels for the playoffs, share of title odds lost_aged | 30% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_ball_drop_aged` | MIN without LaMelo Ball for the playoffs, title odds lost, points_aged | 2.21 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_ball_share_aged` | MIN without LaMelo Ball for the playoffs, share of title odds lost_aged | 60% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_gobert_drop_aged` | MIN without Rudy Gobert for the playoffs, title odds lost, points_aged | 1.72 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_gobert_share_aged` | MIN without Rudy Gobert for the playoffs, share of title odds lost_aged | 46% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_min_n_60_aged` | MIN players whose playoff absence costs at least 60% of the odds_aged | 1 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_min_n_half_aged` | MIN players whose playoff absence costs at least half of the odds_aged | 2 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_okc_full_aged` | OKC full-roster title odds_aged | 17.13% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_drop_aged` | OKC mean drop_aged | 6.72 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_share_aged` | OKC share of odds lost_aged | 39% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_net_aged` | OKC mean net lost per removal_aged | 2.63 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_okc_big_aged` | OKC largest single net loss_aged | 4.66 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_okc_bigname_aged` | OKC largest single loss, player_aged | Shai Gilgeous-Alexander | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_okc_holmgren_drop_aged` | OKC without Chet Holmgren for the playoffs, title odds lost, points_aged | 7.13 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_holmgren_share_aged` | OKC without Chet Holmgren for the playoffs, share of title odds lost_aged | 42% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_hartenstein_drop_aged` | OKC without Isaiah Hartenstein for the playoffs, title odds lost, points_aged | 3.27 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_hartenstein_share_aged` | OKC without Isaiah Hartenstein for the playoffs, share of title odds lost_aged | 19% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_williams_drop_aged` | OKC without Jalen Williams for the playoffs, title odds lost, points_aged | 2.19 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_williams_share_aged` | OKC without Jalen Williams for the playoffs, share of title odds lost_aged | 13% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_gilgeousalexander_drop_aged` | OKC without Shai Gilgeous-Alexander for the playoffs, title odds lost, points_aged | 10.83 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_gilgeousalexander_share_aged` | OKC without Shai Gilgeous-Alexander for the playoffs, share of title odds lost_aged | 63% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_okc_n_60_aged` | OKC players whose playoff absence costs at least 60% of the odds_aged | 1 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_okc_n_half_aged` | OKC players whose playoff absence costs at least half of the odds_aged | 1 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_sas_full_aged` | SAS full-roster title odds_aged | 16.46% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_drop_aged` | SAS mean drop_aged | 6.29 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_share_aged` | SAS share of odds lost_aged | 38% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_net_aged` | SAS mean net lost per removal_aged | 2.52 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_sas_big_aged` | SAS largest single net loss_aged | 5.52 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_sas_bigname_aged` | SAS largest single loss, player_aged | Victor Wembanyama | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_sas_fox_drop_aged` | SAS without De'Aaron Fox for the playoffs, title odds lost, points_aged | 4.57 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_fox_share_aged` | SAS without De'Aaron Fox for the playoffs, share of title odds lost_aged | 28% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_harper_drop_aged` | SAS without Dylan Harper for the playoffs, title odds lost, points_aged | 6.09 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_harper_share_aged` | SAS without Dylan Harper for the playoffs, share of title odds lost_aged | 37% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_harris_drop_aged` | SAS without Tobias Harris for the playoffs, title odds lost, points_aged | 2.13 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_harris_share_aged` | SAS without Tobias Harris for the playoffs, share of title odds lost_aged | 13% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_wembanyama_drop_aged` | SAS without Victor Wembanyama for the playoffs, title odds lost, points_aged | 12.17 | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_wembanyama_share_aged` | SAS without Victor Wembanyama for the playoffs, share of title odds lost_aged | 74% | MODELED | QUOTABLE AS BAND | `n5_fragility_20260929T095826Z` |
| `n5_sas_n_60_aged` | SAS players whose playoff absence costs at least 60% of the odds_aged | 1 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `n5_sas_n_half_aged` | SAS players whose playoff absence costs at least half of the odds_aged | 1 | MODELED | QUOTABLE | `n5_fragility_20260929T095826Z` |
| `williams_mpg` | Cody Williams projected minutes (0.0 when outside the ten) | 0.0 | ASSUMED | NOT QUOTABLE | `build_rotations_20260929T024337Z` |
| `rs_williams` | Williams rank score | 0.1284 | COMPOSED | DESCRIPTIVE | `build_rotations_20260929T024337Z` |
| `rs_clark` | Jaylen Clark rank score | 0.3333 | COMPOSED | DESCRIPTIVE | `build_rotations_20260929T024337Z` |
| `rs_gap` | rank-score gap | 0.2050 | COMPOSED | DESCRIPTIVE | `build_rotations_20260929T024337Z` |
| `williams_threshold` | Williams minutes at which the offseason verdict changes pattern (watch-list claim 1) | 8.9 | MODELED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w1c_offseason_delta` | published offseason delta, mean pp | +0.297 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260929T061320Z` |
| `w1c_injury_cost` | DiVincenzo injury cost, mean pp | +0.781 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260929T061320Z` |
| `w1c_williams_cost` | Williams minutes cost, mean pp | +0.000 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260929T061320Z` |
| `w1c_interaction` | interaction, mean pp | +0.000 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260929T061320Z` |
| `w1c_remainder` | remainder, mean pp | +1.079 | MODELED | QUOTABLE AS BAND | `w1c_decompose_20260929T061320Z` |
| `w1c_offseason_sign` | published offseason delta, sign pattern over the four views | MIXED | MODELED | QUOTABLE | `w1c_decompose_20260929T061320Z` |
| `w1c_noinjury_sign` | the summer with the injury counted as weather, sign pattern over the four views | ALL POSITIVE | MODELED | QUOTABLE | `w1c_decompose_20260929T061320Z` |
| `m4_fives` | legal fives, DiVincenzo excluded | 749 | COMPOSED | FACT | `m4_lineup_study_20260929T061323Z` |
| `m4_double` | double-big fives | 161 | COMPOSED | FACT | `m4_lineup_study_20260929T061323Z` |
| `m4_nogobert` | fives without Gobert | 294 | COMPOSED | FACT | `m4_lineup_study_20260929T061323Z` |
| `m4_observed` | fives that have played together | 5 | OBSERVED | FACT | `m4_lineup_study_20260929T061323Z` |
| `m4_top10_beringer` | of the ten best rankable fives, how many include Beringer | 9 | COMPOSED | DESCRIPTIVE | `m4_lineup_study_20260929T061323Z` |
| `beringer_prior` | Beringer 2025-26 minutes per game | 7.9 | OBSERVED | FACT | `build_rotations_20260929T024337Z` |
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
| `n2_modal` | modal seed | 6th | MODELED | QUOTABLE | `seed_distribution_20260929T061304Z` |
| `n2_modal_p` | modal seed probability | 26% | MODELED | QUOTABLE | `seed_distribution_20260929T061304Z` |
| `n2_top6` | P(top six) | 70% | MODELED | QUOTABLE | `seed_distribution_20260929T061304Z` |
| `n2_sas_okc` | P(first-round opponent is SAS or OKC) | 34% | MODELED | QUOTABLE | `n2_path_20260929T061321Z` |
| `n2_r2` | P(reach round two) | 38% | MODELED | QUOTABLE AS BAND | `n2_path_20260929T061321Z` |
| `n2_cond` | P(title | escape round one) | 7.2% | MODELED | QUOTABLE AS BAND | `n2_path_20260929T061321Z` |

## 4. Kuminga, better and worse

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `k_scorer_pct` | Kuminga scorer percentile, 2023-26 | 36 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `k_scorer_z` | Kuminga scorer SEs | -0.2 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `k_scorer_n` | Kuminga scorer pairings | 29 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `k_scorer_poss` | Kuminga scorer possessions | 1,415 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `k_scorer_ref` | reference scorers | 245 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `k_defender_pct` | Kuminga defender percentile, 2023-26 | 23 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `k_defender_z` | Kuminga defender SEs | -1.3 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `k_defender_n` | Kuminga defender pairings | 13 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `k_defender_poss` | Kuminga defender possessions | 711 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `k_defender_ref` | reference defenders | 309 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `k_scorer_n26` | Kuminga scorer pairings 2025-26 | 3 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `e_scorer_pct3` | Edwards scorer percentile, 2023-26 | 0 | OBSERVED | QUOTABLE | `n6_kuminga_ledger_20260929T100505Z` |
| `e_scorer_z3` | Edwards scorer SEs, 2023-26 | -8.6 | OBSERVED | QUOTABLE | `n6_kuminga_ledger_20260929T100505Z` |
| `e_scorer_n3` | Edwards scorer pairings, 2023-26 | 72 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `gsw_with` | GSW units with a non-shooting centre, net | -2.1 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `gsw_without` | without one, net | +0.6 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `gsw_with_poss` | possessions with | 5,340 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `gsw_without_poss` | possessions without | 5,672 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `gsw_with_3par` | 3PA rate with | 0.430 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `gsw_without_3par` | 3PA rate without | 0.448 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `gsw_se` | difference game-bootstrap SE | 3.5 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `po_games` | Kuminga postseason games | 40 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `po_poss` | postseason possessions | 1,139 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `po_net` | postseason on-court net | -16.2 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `po_onoff` | postseason on-off, garbage time out | -16.0 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `po_onoff_se` | on-off SE | 8.4 | OBSERVED | DESCRIPTIVE | `n6_kuminga_ledger_20260929T100505Z` |
| `po_onoff_games` | stint games | 23 | OBSERVED | FACT | `n6_kuminga_ledger_20260929T100505Z` |
| `k_usg` | Kuminga usage 2025-26 | 0.226 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `k_unast` | Kuminga unassisted share 2025-26 | 44% | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `k_unast_pct` | percentile | 69 | OBSERVED | QUOTABLE | `m5_usage_accounting_20260916T203535Z` |
| `k_makes` | Kuminga makes 2025-26 | 157 | OBSERVED | FACT | `m5_usage_accounting_20260916T203535Z` |
| `k_y1` | Kuminga year one | $6,064,000 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `k_y2` | Kuminga year two, player option | $6,367,200 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `k_total` | Kuminga total | $12,431,200 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `k_nonbird` | Non-Bird ceiling after an opt-out | $7,276,800 | FACT | FACT | `green_resolution_20260904T014022Z` |
| `k_optout_lo` | P(opt out), low across views, flat aging | 0.53 | MODELED | QUOTABLE AS BAND | `player_option_20260929T061302Z` |
| `k_optout_hi` | P(opt out), high | 0.84 | MODELED | QUOTABLE AS BAND | `player_option_20260929T061302Z` |

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
| `w1_claim` | claim 1 | Cody Williams' minutes decide whether the offseason verdict holds | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w1_now` | claim 1 current value | 0.0 a night (model default: outside the ten under the primary ordering; 16.1 under the flat 0.5 / 0.5 order kept as the sensitivity) | ASSUMED INPUT | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w1_flip` | claim 1 flips if | above 8.9 a night | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w2_claim` | claim 2 | Minnesota's level is inside the model's range | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w2_now` | claim 2 current value | model range +0.2 to +3.0 (four views, both aging bases) | MODELLED RANGE | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w2_flip` | claim 2 flips if | above +8.7 or below -5.5 | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w3_claim` | claim 3 | The model's two largest disagreements with the market | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w3_now` | claim 3 current value | BOS: model 18.1% title odds vs market 5.5%, model net range +3.4 to +10.0. SAS: model 13.8% vs market 23.0%, range +4.2 to +8.7 | MODELLED RANGE | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w3_flip` | claim 3 flips if | BOS below -2.4; SAS above +14.4 | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w4_claim` | claim 4 | The Edwards-Ball pairing costs usage, not efficiency | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w4_now` | claim 4 current value | 2025-26 true shooting: Edwards 0.617, Ball 0.546. Unadjusted base rate for a new high-usage pairing: -0.3 points of true shooting (34 player-seasons) | OBSERVED BASE RATE | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w4_flip` | claim 4 flips if | Edwards below 0.547, or Ball below 0.476 | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w5_claim` | claim 5 | Minnesota is not on a champion's path | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w5_now` | claim 5 current value | projected rank 13 (primary basis) / 10 (aged); the 11 champions since 2015-16 ranked 11 at worst after 20 games (2022-23 DEN), 6 at worst at season's end (2022-23 DEN) with 10 of 11 in the top 5, and 18 at worst after the All-Star break | OBSERVED HISTORY | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w5_flip` | claim 5 flips if | 5 or better at season's end (test); 11 or better after 20 games (checkpoint) | COMPOSED | QUOTABLE | `n8_watch_list_20260929T100500Z` |
| `w_game` | checkpoint game | 20 | ASSUMED | FACT | `n8_watch_list_20260929T100500Z` |

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
| `cha_model_pre` | CHA model title odds before the refit | 5.86% | MODELED | QUOTABLE | `market_devig_20260916T195853Z` |
| `cha_gap_pre` | CHA model minus market before the refit, points | +5.04 | MODELED | QUOTABLE | `market_devig_20260916T195853Z` |
| `cha_gap_now` | CHA model minus market now, points | +2.79 | MODELED | QUOTABLE | `market_devig_20260929T061326Z` |
| `title_pre` | MIN title probability before the refit, mean of four views | 1.69% | MODELED | QUOTABLE AS BAND | `run_sim_20260916T173222Z` |
| `title_aged_pre` | MIN title probability before the refit, mean of four views, aged | 2.55% | MODELED | QUOTABLE AS BAND | `run_sim_20260916T195902Z` |
| `cons_rapm_corr` | consensus-RAPM correlation across players, net, after the refit | 0.977 | COMPOSED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `cons_rapm_corr_pre` | consensus-RAPM correlation across players, net, before the refit | 0.973 | COMPOSED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `k_rapm_pre` | Jonathan Kuminga net RAPM before the refit | +1.37 | MODELED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `k_rapm_post` | Jonathan Kuminga net RAPM after the refit | +1.82 | MODELED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `k_cons_pre` | Jonathan Kuminga consensus net before the refit | +1.33 | MODELED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `k_cons_post` | Jonathan Kuminga consensus net after the refit | +1.65 | MODELED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `ball_rapm_pre` | LaMelo Ball net RAPM before the refit | +1.95 | MODELED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `ball_rapm_post` | LaMelo Ball net RAPM after the refit | +3.86 | MODELED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `ball_cons_pre` | LaMelo Ball consensus net before the refit | +2.29 | MODELED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `ball_cons_post` | LaMelo Ball consensus net after the refit | +3.78 | MODELED | QUOTABLE | `d89_rapm_compare_20260922T010417Z` |
| `misplaced_lineup` | share of points the old lineup pipeline credited to the wrong team | 3.36% | OBSERVED | QUOTABLE | `validate_stint_points_20260922T010709Z` |
| `misplaced_possession` | share of possession points the old attribution credited to the wrong team | 2.84% | OBSERVED | QUOTABLE | `validate_possession_points_20260922T010307Z` |
| `val_lineup_teamgames` | team-games in the lineup-grain check | 578 | FACT | FACT | `validate_stint_points_20260922T010709Z` |
| `val_possession_teamgames` | team-games in the possession-grain check | 96 | FACT | FACT | `validate_possession_points_20260922T010307Z` |
| `off_delta_u` | offseason delta, un-aged | -0.18 | MODELED | NOT QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `off_delta_a` | offseason delta, aged | +0.79 | MODELED | NOT QUOTABLE | `w2_aging_gate_20260929T094601Z` |
| `tail00_player` | tail player | Derrick White (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail00_poss` | possessions | 33,488 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail00_consensus` | consensus | +5.31 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail00_rapm` | rapm | +5.53 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail00_box` | box | +1.96 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail00_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail01_player` | tail player | Jayson Tatum (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail01_poss` | possessions | 27,371 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail01_consensus` | consensus | +5.09 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail01_rapm` | rapm | +4.85 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail01_box` | box | +2.24 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail01_darko` | darko | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail02_player` | tail player | Neemias Queta (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail02_poss` | possessions | 11,730 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail02_consensus` | consensus | +4.75 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail02_rapm` | rapm | +5.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail02_box` | box | +1.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail02_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail03_player` | tail player | Payton Pritchard (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail03_poss` | possessions | 27,327 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail03_consensus` | consensus | +3.28 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail03_rapm` | rapm | +3.62 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail03_box` | box | +1.06 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail03_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail04_player` | tail player | Paul George (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail04_poss` | possessions | 21,781 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail04_consensus` | consensus | +3.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail04_rapm` | rapm | +3.07 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail04_box` | box | +1.21 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail04_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail05_player` | tail player | Mitchell Robinson (BOS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail05_poss` | possessions | 11,720 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail05_consensus` | consensus | +2.61 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail05_rapm` | rapm | +1.87 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail05_box` | box | +1.17 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail05_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail06_player` | tail player | Moussa Diabate (CHA) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail06_poss` | possessions | 10,571 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail06_consensus` | consensus | +5.05 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail06_rapm` | rapm | +5.05 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail06_box` | box | +0.27 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail06_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail07_player` | tail player | Kon Knueppel (CHA) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail07_poss` | possessions | 9,854 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail07_consensus` | consensus | +3.87 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail07_rapm` | rapm | +4.11 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail07_box` | box | +1.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail07_darko` | darko | +0.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail08_player` | tail player | Naz Reid (CHA) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail08_poss` | possessions | 28,945 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail08_consensus` | consensus | +2.79 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail08_rapm` | rapm | +2.73 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail08_box` | box | +0.97 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail08_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail09_player` | tail player | Nikola Jokic (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail09_poss` | possessions | 29,795 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail09_consensus` | consensus | +8.08 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail09_rapm` | rapm | +8.08 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail09_box` | box | +5.43 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail09_darko` | darko | +7.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail10_player` | tail player | Aaron Gordon (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail10_poss` | possessions | 23,054 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail10_consensus` | consensus | +3.47 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail10_rapm` | rapm | +3.88 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail10_box` | box | +0.69 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail10_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail11_player` | tail player | Jamal Murray (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail11_poss` | possessions | 32,124 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail11_consensus` | consensus | +2.74 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail11_rapm` | rapm | +2.89 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail11_box` | box | +1.96 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail11_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail12_player` | tail player | Christian Braun (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail12_poss` | possessions | 25,880 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail12_consensus` | consensus | +2.44 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail12_rapm` | rapm | +3.24 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail12_box` | box | +0.21 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail12_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail13_player` | tail player | Cameron Johnson (DEN) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail13_poss` | possessions | 18,473 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail13_consensus` | consensus | +2.38 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail13_rapm` | rapm | +2.77 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail13_box` | box | +0.73 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail13_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail14_player` | tail player | Cade Cunningham (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail14_poss` | possessions | 29,653 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail14_consensus` | consensus | +3.48 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail14_rapm` | rapm | +2.91 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail14_box` | box | +1.31 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail14_darko` | darko | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail15_player` | tail player | Ausar Thompson (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail15_poss` | possessions | 21,191 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail15_consensus` | consensus | +3.95 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail15_rapm` | rapm | +4.35 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail15_box` | box | +1.16 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail15_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail16_player` | tail player | Paul Reed (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail16_poss` | possessions | 11,697 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail16_consensus` | consensus | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail16_rapm` | rapm | +3.79 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail16_box` | box | +2.41 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail16_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail17_player` | tail player | Isaiah Joe (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail17_poss` | possessions | 20,956 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail17_consensus` | consensus | +2.39 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail17_rapm` | rapm | +2.43 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail17_box` | box | +1.48 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail17_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail18_player` | tail player | Duncan Robinson (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail18_poss` | possessions | 22,814 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail18_consensus` | consensus | +1.88 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail18_rapm` | rapm | +2.51 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail18_box` | box | -0.02 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail18_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail19_player` | tail player | Javonte Green (DET) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail19_poss` | possessions | 11,773 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail19_consensus` | consensus | +2.58 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail19_rapm` | rapm | +2.78 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail19_box` | box | +1.11 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail19_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail20_player` | tail player | Amen Thompson (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail20_poss` | possessions | 28,337 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail20_consensus` | consensus | +4.24 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail20_rapm` | rapm | +4.13 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail20_box` | box | +1.31 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail20_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail21_player` | tail player | Kevin Durant (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail21_poss` | possessions | 31,434 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail21_consensus` | consensus | +3.51 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail21_rapm` | rapm | +3.36 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail21_box` | box | +1.72 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail21_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail22_player` | tail player | Tari Eason (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail22_poss` | possessions | 15,553 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail22_consensus` | consensus | +3.13 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail22_rapm` | rapm | +3.69 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail22_box` | box | +1.40 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail22_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail23_player` | tail player | Marcus Smart (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail23_poss` | possessions | 13,273 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail23_consensus` | consensus | +2.73 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail23_rapm` | rapm | +4.08 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail23_box` | box | -0.07 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail23_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail24_player` | tail player | Alperen Sengun (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail24_poss` | possessions | 29,429 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail24_consensus` | consensus | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail24_rapm` | rapm | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail24_box` | box | +1.47 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail24_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail25_player` | tail player | Steven Adams (HOU) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail25_poss` | possessions | 6,994 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail25_consensus` | consensus | +2.68 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail25_rapm` | rapm | +3.34 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail25_box` | box | -0.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail25_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail26_player` | tail player | OG Anunoby (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail26_poss` | possessions | 31,666 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail26_consensus` | consensus | +4.38 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail26_rapm` | rapm | +5.22 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail26_box` | box | +0.90 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail26_darko` | darko | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail27_player` | tail player | Karl-Anthony Towns (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail27_poss` | possessions | 32,893 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail27_consensus` | consensus | +3.77 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail27_rapm` | rapm | +3.59 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail27_box` | box | +1.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail27_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail28_player` | tail player | Jalen Brunson (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail28_poss` | possessions | 36,185 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail28_consensus` | consensus | +3.30 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail28_rapm` | rapm | +3.39 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail28_box` | box | +1.55 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail28_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail29_player` | tail player | Miles McBride (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail29_poss` | possessions | 18,187 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail29_consensus` | consensus | +3.22 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail29_rapm` | rapm | +4.07 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail29_box` | box | +0.17 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail29_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail30_player` | tail player | Josh Hart (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail30_poss` | possessions | 35,303 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail30_consensus` | consensus | +2.14 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail30_rapm` | rapm | +1.59 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail30_box` | box | -0.02 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail30_darko` | darko | +0.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail31_player` | tail player | Mikal Bridges (NYK) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail31_poss` | possessions | 37,099 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail31_consensus` | consensus | +1.70 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail31_rapm` | rapm | +1.44 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail31_box` | box | +0.37 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail31_darko` | darko | +0.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail32_player` | tail player | Shai Gilgeous-Alexander (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail32_poss` | possessions | 36,663 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail32_consensus` | consensus | +9.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail32_rapm` | rapm | +9.16 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail32_box` | box | +5.05 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail32_darko` | darko | +6.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail33_player` | tail player | Chet Holmgren (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail33_poss` | possessions | 30,400 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail33_consensus` | consensus | +6.05 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail33_rapm` | rapm | +6.39 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail33_box` | box | +2.95 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail33_darko` | darko | +5.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail34_player` | tail player | Isaiah Hartenstein (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail34_poss` | possessions | 24,050 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail34_consensus` | consensus | +4.53 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail34_rapm` | rapm | +4.17 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail34_box` | box | +1.28 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail34_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail35_player` | tail player | Alex Caruso (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail35_poss` | possessions | 20,771 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail35_consensus` | consensus | +5.17 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail35_rapm` | rapm | +5.41 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail35_box` | box | +2.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail35_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail36_player` | tail player | Ajay Mitchell (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail36_poss` | possessions | 9,612 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail36_consensus` | consensus | +3.26 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail36_rapm` | rapm | +3.55 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail36_box` | box | +1.11 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail36_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail37_player` | tail player | Jalen Williams (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail37_poss` | possessions | 24,304 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail37_consensus` | consensus | +2.65 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail37_rapm` | rapm | +1.59 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail37_box` | box | +2.13 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail37_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail38_player` | tail player | Cason Wallace (OKC) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail38_poss` | possessions | 26,671 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail38_consensus` | consensus | +2.21 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail38_rapm` | rapm | +1.76 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail38_box` | box | +1.02 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail38_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail39_player` | tail player | Joel Embiid (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail39_poss` | possessions | 14,241 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail39_consensus` | consensus | +5.43 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail39_rapm` | rapm | +4.25 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail39_box` | box | +2.96 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail39_darko` | darko | +4.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail40_player` | tail player | Tyrese Maxey (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail40_poss` | possessions | 30,824 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail40_consensus` | consensus | +3.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail40_rapm` | rapm | +3.26 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail40_box` | box | +2.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail40_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail41_player` | tail player | LeBron James (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail41_poss` | possessions | 27,829 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail41_consensus` | consensus | +3.38 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail41_rapm` | rapm | +1.88 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail41_box` | box | +2.10 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail41_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail42_player` | tail player | Dean Wade (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail42_poss` | possessions | 16,303 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail42_consensus` | consensus | +3.45 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail42_rapm` | rapm | +4.28 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail42_box` | box | +0.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail42_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail43_player` | tail player | VJ Edgecombe (PHI) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail43_poss` | possessions | 11,784 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail43_consensus` | consensus | +1.89 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail43_rapm` | rapm | +2.32 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail43_box` | box | +0.27 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail43_darko` | darko | +0.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail44_player` | tail player | Victor Wembanyama (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail44_poss` | possessions | 24,727 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail44_consensus` | consensus | +9.99 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail44_rapm` | rapm | +9.88 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail44_box` | box | +5.55 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail44_darko` | darko | +6.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail45_player` | tail player | De'Aaron Fox (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail45_poss` | possessions | 31,321 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail45_consensus` | consensus | +3.41 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail45_rapm` | rapm | +3.83 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail45_box` | box | +1.80 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail45_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail46_player` | tail player | Dylan Harper (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail46_poss` | possessions | 8,557 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail46_consensus` | consensus | +4.27 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail46_rapm` | rapm | +5.06 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail46_box` | box | +1.12 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail46_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail47_player` | tail player | Tobias Harris (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail47_poss` | possessions | 28,597 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail47_consensus` | consensus | +3.24 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail47_rapm` | rapm | +3.79 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail47_box` | box | +0.54 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail47_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail48_player` | tail player | Luke Kornet (SAS) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail48_poss` | possessions | 17,332 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail48_consensus` | consensus | +3.67 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail48_rapm` | rapm | +3.04 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail48_box` | box | +1.73 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail48_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail49_player` | tail player | Kawhi Leonard (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail49_poss` | possessions | 22,880 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail49_consensus` | consensus | +7.61 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail49_rapm` | rapm | +8.02 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail49_box` | box | +3.18 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail49_darko` | darko | +6.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail50_player` | tail player | Scottie Barnes (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail50_poss` | possessions | 28,446 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail50_consensus` | consensus | +3.65 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail50_rapm` | rapm | +2.83 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail50_box` | box | +2.09 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail50_darko` | darko | +2.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail51_player` | tail player | Jakob Poeltl (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail51_poss` | possessions | 16,432 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail51_consensus` | consensus | +2.76 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail51_rapm` | rapm | +2.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail51_box` | box | +1.32 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail51_darko` | darko | +3.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail52_player` | tail player | Immanuel Quickley (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail52_poss` | possessions | 20,156 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail52_consensus` | consensus | +2.15 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail52_rapm` | rapm | +1.79 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail52_box` | box | +1.66 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail52_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail53_player` | tail player | Collin Murray-Boyles (TOR) | OBSERVED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail53_poss` | possessions | 5,585 | OBSERVED | FACT | `f4_per_view_disagreement_20260929T061327Z` |
| `tail53_consensus` | consensus | +2.50 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail53_rapm` | rapm | +2.37 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail53_box` | box | +1.13 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `tail53_darko` | darko | +1.00 | MODELED | DESCRIPTIVE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_bos_mkt` | BOS market | 5.47% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_bos_consensus` | BOS consensus | 22.60% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_bos_rapm` | BOS rapm | 22.85% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_bos_box` | BOS box | 13.02% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_bos_darko` | BOS darko | 14.02% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_bos_label` | BOS label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_sas_mkt` | SAS market | 22.96% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_sas_consensus` | SAS consensus | 15.80% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_sas_rapm` | SAS rapm | 17.95% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_sas_box` | SAS box | 9.70% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_sas_darko` | SAS darko | 11.77% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_sas_label` | SAS label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_okc_mkt` | OKC market | 22.49% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_okc_consensus` | OKC consensus | 12.90% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_okc_rapm` | OKC rapm | 11.90% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_okc_box` | OKC box | 16.55% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_okc_darko` | OKC darko | 17.54% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_okc_label` | OKC label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_phi_mkt` | PHI market | 8.42% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_phi_consensus` | PHI consensus | 4.14% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_phi_rapm` | PHI rapm | 3.71% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_phi_box` | PHI box | 0.66% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_phi_darko` | PHI darko | 3.28% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_phi_label` | PHI label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_det_mkt` | DET market | 3.16% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_det_consensus` | DET consensus | 4.64% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_det_rapm` | DET rapm | 4.83% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_det_box` | DET box | 10.04% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_det_darko` | DET darko | 11.53% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_det_label` | DET label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_nyk_mkt` | NYK market | 8.21% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_nyk_consensus` | NYK consensus | 3.17% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_nyk_rapm` | NYK rapm | 3.31% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_nyk_box` | NYK box | 5.92% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_nyk_darko` | NYK darko | 3.69% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_nyk_label` | NYK label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_hou_mkt` | HOU market | 1.61% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_hou_consensus` | HOU consensus | 4.97% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_hou_rapm` | HOU rapm | 5.39% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_hou_box` | HOU box | 5.18% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_hou_darko` | HOU darko | 6.22% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_hou_label` | HOU label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_den_mkt` | DEN market | 3.16% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_den_consensus` | DEN consensus | 5.95% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_den_rapm` | DEN rapm | 4.56% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_den_box` | DEN box | 8.63% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_den_darko` | DEN darko | 5.30% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_den_label` | DEN label | ALL-VIEWS | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_min_mkt` | MIN market | 3.16% | OBSERVED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_min_consensus` | MIN consensus | 1.83% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_min_rapm` | MIN rapm | 2.50% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_min_box` | MIN box | 2.81% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_min_darko` | MIN darko | 3.89% | MODELED | QUOTABLE AS BAND | `f4_per_view_disagreement_20260929T061327Z` |
| `pv_min_label` | MIN label | MIXED | MODELED | QUOTABLE | `f4_per_view_disagreement_20260929T061327Z` |

## C. The bet: additions for Parts 1, 3 and 4

| key | figure | value | label | verdict | run |
|---|---|---|---|---|---|
| `c2_haz_2027_600` | Edwards departure hazard, 2026-27 season, team at .600 | 0.8% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2027_600_band` | 80%% interval | 0.4% to 1.2% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2028_600` | Edwards departure hazard, 2027-28 season, team at .600 | 7.3% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2028_600_band` | 80%% interval | 4.8% to 10% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2029_600` | Edwards departure hazard, 2028-29 season, team at .600 | 44% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2029_600_band` | 80%% interval | 35% to 53% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2033_600` | Edwards departure hazard, 2032-33 season, team at .600 | 14% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2033_600_band` | 80%% interval | 9.0% to 20% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_cum_2029_600` | P(Edwards departed by 2028-29), team at .600 | 48% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_cum_2029_600_band` | 80%% interval | 39% to 58% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_cum_2033_600` | P(Edwards departed by 2032-33), team at .600 | 56% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_cum_2033_600_band` | 80%% interval | 45% to 68% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2027_450` | Edwards departure hazard, 2026-27 season, team at .450 | 1.3% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2027_450_band` | 80%% interval | 0.7% to 2.0% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2028_450` | Edwards departure hazard, 2027-28 season, team at .450 | 12% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2028_450_band` | 80%% interval | 7.7% to 16% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2029_450` | Edwards departure hazard, 2028-29 season, team at .450 | 56% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2029_450_band` | 80%% interval | 47% to 66% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2033_450` | Edwards departure hazard, 2032-33 season, team at .450 | 22% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_haz_2033_450_band` | 80%% interval | 14% to 30% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_cum_2029_450` | P(Edwards departed by 2028-29), team at .450 | 62% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_cum_2029_450_band` | 80%% interval | 52% to 71% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_cum_2033_450` | P(Edwards departed by 2032-33), team at .450 | 71% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_cum_2033_450_band` | 80%% interval | 60% to 81% | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_scen_high` | central scenario, team two-year win percentage | .600 | MODELED | DESCRIPTIVE | `c2_edwards_clock_20260922T191531Z` |
| `c2_scen_low` | decline scenario, team two-year win percentage | .450 | MODELED | DESCRIPTIVE | `c2_edwards_clock_20260922T191531Z` |
| `c2_first_season` | first season in the star-spells data | 1990 | OBSERVED | DESCRIPTIVE | `c2_edwards_clock_20260922T191531Z` |
| `c2_calib_window` | calibration slope window set in advance | 0.8 to 1.2 | MODELED | DESCRIPTIVE | `c2_edwards_clock_20260922T191531Z` |
| `c2_cba_year` | the collective bargaining agreement quoted | 2023 | OBSERVED | DESCRIPTIVE | `c2_edwards_clock_20260922T191531Z` |
| `c2_raw_stage_n` | star-seasons with two seasons left, within-three window observed | 192 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_raw_within3` | of those, departed within three seasons | 44% | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_raw_walk_all` | walk-year departure rate, all star-seasons | 41% | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_raw_walk_all_n` | walk-year star-seasons | 536 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_raw_walk_600` | walk-year departure rate, team at .600 or better | 31% | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_raw_walk_600_n` | cases | 248 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_raw_walk_sub500` | walk-year departure rate, team under .500 | 56% | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_raw_walk_sub500_n` | cases | 118 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_n_spells` | star spells in the Part 1 model | 291 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_n_rows` | player-seasons | 1,264 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_n_departures` | departures | 228 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_walk_multiple` | walk-year odds multiple against two seasons left (from the M2 coefficient) | 66 | MODELED | QUOTABLE AS BAND | `c2_edwards_clock_20260922T191531Z` |
| `c2_c_index` | Model B C-index on the sealed holdout | 0.907 | MODELED | DESCRIPTIVE | `c2_edwards_clock_20260922T191531Z` |
| `c2_calibration` | Model B calibration slope (window 0.8 to 1.2, failed and printed) | 1.413 | MODELED | DESCRIPTIVE | `c2_edwards_clock_20260922T191531Z` |
| `c2_salary_2026_27` | Edwards salary 2026-27 | $48,924,624 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_salary_2026_27_m` | Edwards salary 2026-27, rounded | $48.9 million | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_salary_2027_28` | Edwards salary 2027-28 | $52,298,736 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_salary_2027_28_m` | Edwards salary 2027-28, rounded | $52.3 million | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_salary_2028_29` | Edwards salary 2028-29 | $55,672,848 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_salary_2028_29_m` | Edwards salary 2028-29, rounded | $55.7 million | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_ext_signed` | rookie scale extension signed | 2023-07-08 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_ext_window` | standard extension window opened (third anniversary) | 2026-07-08 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_games_2025_26` | Edwards regular-season games 2025-26 | 61 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_games_rule` | games required for All-NBA eligibility (Art. XXIX Sec. 6) | 65 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_walk_year` | walk year | 2028-29 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_free_agency` | unrestricted free agency | 2029-07-01 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_dvpe_window` | designated veteran extension window (if All-NBA 2026-27) | July 2027 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_dvpe_last` | last extension window before free agency (needs All-NBA 2027-28) | July 2028 | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_std_ext_reported` | standard extension available now, as reported | two years, about $122 million | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c2_supermax_reported` | designated veteran extension as reported | four years, about $300 million | OBSERVED | QUOTABLE | `c2_edwards_clock_20260922T191531Z` |
| `c3_games_2020_21` | Ball games played 2020-21 | 51 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_team_games_2020_21` | team games 2020-21 | 72 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_share_2020_21` | share of team games 2020-21 | 71% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_missed_2020_21` | games missed 2020-21 | 21 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_games_2021_22` | Ball games played 2021-22 | 75 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_team_games_2021_22` | team games 2021-22 | 82 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_share_2021_22` | share of team games 2021-22 | 91% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_missed_2021_22` | games missed 2021-22 | 7 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_games_2022_23` | Ball games played 2022-23 | 36 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_team_games_2022_23` | team games 2022-23 | 82 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_share_2022_23` | share of team games 2022-23 | 44% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_missed_2022_23` | games missed 2022-23 | 46 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_games_2023_24` | Ball games played 2023-24 | 22 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_team_games_2023_24` | team games 2023-24 | 82 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_share_2023_24` | share of team games 2023-24 | 27% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_missed_2023_24` | games missed 2023-24 | 60 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_games_2024_25` | Ball games played 2024-25 | 47 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_team_games_2024_25` | team games 2024-25 | 82 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_share_2024_25` | share of team games 2024-25 | 57% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_missed_2024_25` | games missed 2024-25 | 35 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_games_2025_26` | Ball games played 2025-26 | 72 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_team_games_2025_26` | team games 2025-26 | 82 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_share_2025_26` | share of team games 2025-26 | 88% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_missed_2025_26` | games missed 2025-26 | 10 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_mpa_2025_26` | Ball minutes per appearance 2025-26 | 27.5 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_games_total` | Ball games played, six seasons | 303 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_team_games_total` | team games, six seasons | 482 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_missed_total` | games missed, six seasons | 179 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_share_total` | share of team games, six seasons | 63% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_stretches` | missed stretches | 27 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_stretches_sourced` | stretches with a sourced cause | 27 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_surgeries` | stretches that ended in surgery | 3 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_a_n` | base rate A: injury history: player-seasons | 20 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_a_players` | players | 16 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_a_mean` | mean games | 56.7 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_a_median` | median games | 61.4 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_a_p50` | P(50 or more) | 75% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_a_p60` | P(60 or more) | 55% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_a_p70` | P(70 or more) | 25% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_a_pall` | P(all games) | 0% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_a_p40` | P(40 or fewer) | 20% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_b_n` | base rate B: injury history and a healthy prior season: player-seasons | 6 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_b_players` | players | 6 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_b_mean` | mean games | 54.5 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_b_median` | median games | 62.5 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_b_p50` | P(50 or more) | 67% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_b_p60` | P(60 or more) | 50% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_b_p70` | P(70 or more) | 33% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_b_pall` | P(all games) | 0% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_b_p40` | P(40 or fewer) | 33% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_c_n` | base rate C: looser history, two of five prior seasons at 60% or less: player-seasons | 85 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_c_players` | players | 62 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_c_mean` | mean games | 61.7 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_c_median` | median games | 67.0 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_c_p50` | P(50 or more) | 78% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_c_p60` | P(60 or more) | 69% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_c_p70` | P(70 or more) | 41% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_c_pall` | P(all games) | 5% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_c_p40` | P(40 or fewer) | 12% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_d_n` | base rate D: injury history, age 22 to 29: player-seasons | 41 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_d_players` | players | 32 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_d_mean` | mean games | 57.0 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_d_median` | median games | 63.0 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_d_p50` | P(50 or more) | 73% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_d_p60` | P(60 or more) | 61% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_d_p70` | P(70 or more) | 27% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_d_pall` | P(all games) | 0% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_d_p40` | P(40 or fewer) | 22% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_band_n` | base rate band: same age and role, no history condition: player-seasons | 617 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_band_players` | players | 329 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_band_mean` | mean games | 64.9 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_band_median` | median games | 70.0 | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_band_p50` | P(50 or more) | 83% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_band_p60` | P(60 or more) | 72% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_band_p70` | P(70 or more) | 52% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_band_pall` | P(all games) | 7% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_band_p40` | P(40 or fewer) | 10% | OBSERVED | QUOTABLE | `c3_ball_games_20260929T182638Z` |
| `c3_def_share` | base rate definition: a bad season is at most this share of team games | 60% | OBSERVED | DESCRIPTIVE | `c3_ball_games_20260929T182638Z` |
| `c3_def_seasons` | bad seasons required of the five prior | 3 | OBSERVED | DESCRIPTIVE | `c3_ball_games_20260929T182638Z` |
| `c3_def_age` | age band | 23 to 27 | OBSERVED | DESCRIPTIVE | `c3_ball_games_20260929T182638Z` |
| `c3_def_mpa` | minutes per appearance the season before, at least | 24 | OBSERVED | DESCRIPTIVE | `c3_ball_games_20260929T182638Z` |
| `c3_def_healthy` | healthy prior season, at least this share | 80% | OBSERVED | DESCRIPTIVE | `c3_ball_games_20260929T182638Z` |
| `c3_def_first` | first season in the base rate | 2001-02 | OBSERVED | DESCRIPTIVE | `c3_ball_games_20260929T182638Z` |
| `c3_title_50_u` | MIN title odds with Ball at 50 games, mean of views (unaged) | 2.65% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_title_50_u_band` | band across views | 1.67% to 3.81% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_title_drop_50_u` | drop from 82 games, points | 0.10 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_50_u` | P(top six) with Ball at 50 games (unaged) | 55.0% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_50_u_band` | band across views | 36.7% to 75.7% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_drop_50_u` | P(top six) drop from 82 games, points | 15.6 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_seed_50_u` | mean West seed | 6.24 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_net_drop_50_u` | regular-season net lost, mean of views | 0.74 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_ball_mpg_50_u` | Ball minutes per game in the allocation | 19.3 | MODELED | DESCRIPTIVE | `c3_ball_availability_20260929T181127Z` |
| `c3_title_60_u` | MIN title odds with Ball at 60 games, mean of views (unaged) | 2.68% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_title_60_u_band` | band across views | 1.70% to 3.86% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_title_drop_60_u` | drop from 82 games, points | 0.07 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_60_u` | P(top six) with Ball at 60 games (unaged) | 58.4% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_60_u_band` | band across views | 40.6% to 78.9% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_drop_60_u` | P(top six) drop from 82 games, points | 12.2 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_seed_60_u` | mean West seed | 6.13 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_net_drop_60_u` | regular-season net lost, mean of views | 0.58 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_ball_mpg_60_u` | Ball minutes per game in the allocation | 22.7 | MODELED | DESCRIPTIVE | `c3_ball_availability_20260929T181127Z` |
| `c3_title_70_u` | MIN title odds with Ball at 70 games, mean of views (unaged) | 2.71% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_title_70_u_band` | band across views | 1.69% to 3.91% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_title_drop_70_u` | drop from 82 games, points | 0.04 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_70_u` | P(top six) with Ball at 70 games (unaged) | 64.3% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_70_u_band` | band across views | 48.3% to 83.8% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_drop_70_u` | P(top six) drop from 82 games, points | 6.3 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_seed_70_u` | mean West seed | 5.93 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_net_drop_70_u` | regular-season net lost, mean of views | 0.31 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_ball_mpg_70_u` | Ball minutes per game in the allocation | 26.5 | MODELED | DESCRIPTIVE | `c3_ball_availability_20260929T181127Z` |
| `c3_title_82_u` | MIN title odds with Ball at 82 games, mean of views (unaged) | 2.75% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_title_82_u_band` | band across views | 1.74% to 3.97% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_title_drop_82_u` | drop from 82 games, points | 0.00 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_82_u` | P(top six) with Ball at 82 games (unaged) | 70.6% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_82_u_band` | band across views | 55.5% to 88.4% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_top6_drop_82_u` | P(top six) drop from 82 games, points | 0.0 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_seed_82_u` | mean West seed | 5.69 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_net_drop_82_u` | regular-season net lost, mean of views | 0.00 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181127Z` |
| `c3_ball_mpg_82_u` | Ball minutes per game in the allocation | 31.0 | MODELED | DESCRIPTIVE | `c3_ball_availability_20260929T181127Z` |
| `c3_title_50_a` | MIN title odds with Ball at 50 games, mean of views (aged) | 3.60% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_title_50_a_band` | band across views | 2.28% to 5.00% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_title_drop_50_a` | drop from 82 games, points | 0.15 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_50_a` | P(top six) with Ball at 50 games (aged) | 74.0% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_50_a_band` | band across views | 58.0% to 90.4% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_drop_50_a` | P(top six) drop from 82 games, points | 10.9 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_seed_50_a` | mean West seed | 5.47 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_net_drop_50_a` | regular-season net lost, mean of views | 0.70 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_ball_mpg_50_a` | Ball minutes per game in the allocation | 19.3 | MODELED | DESCRIPTIVE | `c3_ball_availability_20260929T181920Z` |
| `c3_title_60_a` | MIN title odds with Ball at 60 games, mean of views (aged) | 3.62% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_title_60_a_band` | band across views | 2.32% to 5.03% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_title_drop_60_a` | drop from 82 games, points | 0.12 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_60_a` | P(top six) with Ball at 60 games (aged) | 76.6% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_60_a_band` | band across views | 61.7% to 92.1% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_drop_60_a` | P(top six) drop from 82 games, points | 8.3 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_seed_60_a` | mean West seed | 5.35 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_net_drop_60_a` | regular-season net lost, mean of views | 0.55 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_ball_mpg_60_a` | Ball minutes per game in the allocation | 22.7 | MODELED | DESCRIPTIVE | `c3_ball_availability_20260929T181920Z` |
| `c3_title_70_a` | MIN title odds with Ball at 70 games, mean of views (aged) | 3.67% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_title_70_a_band` | band across views | 2.39% to 5.07% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_title_drop_70_a` | drop from 82 games, points | 0.07 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_70_a` | P(top six) with Ball at 70 games (aged) | 80.9% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_70_a_band` | band across views | 68.9% to 94.5% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_drop_70_a` | P(top six) drop from 82 games, points | 4.0 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_seed_70_a` | mean West seed | 5.13 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_net_drop_70_a` | regular-season net lost, mean of views | 0.29 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_ball_mpg_70_a` | Ball minutes per game in the allocation | 26.5 | MODELED | DESCRIPTIVE | `c3_ball_availability_20260929T181920Z` |
| `c3_title_82_a` | MIN title odds with Ball at 82 games, mean of views (aged) | 3.74% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_title_82_a_band` | band across views | 2.45% to 5.19% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_title_drop_82_a` | drop from 82 games, points | 0.00 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_82_a` | P(top six) with Ball at 82 games (aged) | 84.9% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_82_a_band` | band across views | 74.7% to 96.4% | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_top6_drop_82_a` | P(top six) drop from 82 games, points | 0.0 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_seed_82_a` | mean West seed | 4.89 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_net_drop_82_a` | regular-season net lost, mean of views | 0.00 | MODELED | QUOTABLE AS BAND | `c3_ball_availability_20260929T181920Z` |
| `c3_ball_mpg_82_a` | Ball minutes per game in the allocation | 31.0 | MODELED | DESCRIPTIVE | `c3_ball_availability_20260929T181920Z` |
| `c1_n` | champions in the table | 11 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_first` | first season | 2015-16 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_last` | last season | 2025-26 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_team` | 2015-16 champion | CLE | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_record` | record | 57-25 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_seed` | seed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_net_rs` | RS net rating | +6.3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_net_rs_rank` | RS net rating rank | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_net_post` | post-All-Star net rating | +6.3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_net_post_rank` | post-All-Star net rating rank | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_net_po` | playoff net rating | +9.5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_net_po_minus` | playoff minus RS net rating | +3.2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_age` | top-8 mean age | 28.0 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_oldest` | top-8 oldest | 35.6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_drafted` | top-8 drafted | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_traded` | top-8 traded for | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_signed` | top-8 signed | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_returning` | top-8 returning from the season before | 7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_returning_share` | share of playoff minutes to returning players | 86% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_returning_contract` | top-8 with the franchise the season before, by contract | 7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_returning_share_contract` | share of playoff minutes to players returning by contract | 86% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_missed_rs` | top-8 RS games missed | 88 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_missed_po` | top-8 playoff games missed | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_po_games` | playoff games | 21 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_top5_rs` | top-5 minutes share, RS | 59% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_top5_po` | top-5 minutes share, playoffs | 71% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_moves` | in-season moves touching the top 8 | none | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_pre_pct` | preseason title price, de-vigged | 22.95% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_pre_rank` | preseason title rank of 30 | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_pre_odds` | preseason title odds, American | 280 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_pre_fav` | preseason favourite | Cleveland Cavaliers | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2015_16_pre_fav_pct` | preseason favourite's price, de-vigged | 22.95% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_team` | 2016-17 champion | GSW | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_record` | record | 67-15 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_seed` | seed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_net_rs` | RS net rating | +11.4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_net_rs_rank` | RS net rating rank | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_net_post` | post-All-Star net rating | +9.2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_net_post_rank` | post-All-Star net rating rank | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_net_po` | playoff net rating | +12.8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_net_po_minus` | playoff minus RS net rating | +1.5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_age` | top-8 mean age | 29.7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_oldest` | top-8 oldest | 36.4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_drafted` | top-8 drafted | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_traded` | top-8 traded for | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_signed` | top-8 signed | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_returning` | top-8 returning from the season before | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_returning_share` | share of playoff minutes to returning players | 67% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_returning_contract` | top-8 with the franchise the season before, by contract | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_returning_share_contract` | share of playoff minutes to players returning by contract | 67% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_missed_rs` | top-8 RS games missed | 64 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_missed_po` | top-8 playoff games missed | 7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_po_games` | playoff games | 17 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_top5_rs` | top-5 minutes share, RS | 60% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_top5_po` | top-5 minutes share, playoffs | 68% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_moves` | in-season moves touching the top 8 | none | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_pre_pct` | preseason title price, de-vigged | 50.93% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_pre_rank` | preseason title rank of 30 | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_pre_odds` | preseason title odds, American | -128 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_pre_fav` | preseason favourite | Golden State Warriors | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2016_17_pre_fav_pct` | preseason favourite's price, de-vigged | 50.93% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_team` | 2017-18 champion | GSW | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_record` | record | 58-24 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_seed` | seed | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_net_rs` | RS net rating | +5.9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_net_rs_rank` | RS net rating rank | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_net_post` | post-All-Star net rating | +0.9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_net_post_rank` | post-All-Star net rating rank | 16 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_net_po` | playoff net rating | +10.8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_net_po_minus` | playoff minus RS net rating | +4.8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_age` | top-8 mean age | 29.5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_oldest` | top-8 oldest | 34.0 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_drafted` | top-8 drafted | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_traded` | top-8 traded for | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_signed` | top-8 signed | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_returning` | top-8 returning from the season before | 7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_returning_share` | share of playoff minutes to returning players | 89% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_returning_contract` | top-8 with the franchise the season before, by contract | 7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_returning_share_contract` | share of playoff minutes to players returning by contract | 89% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_missed_rs` | top-8 RS games missed | 113 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_missed_po` | top-8 playoff games missed | 15 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_po_games` | playoff games | 21 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_top5_rs` | top-5 minutes share, RS | 53% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_top5_po` | top-5 minutes share, playoffs | 67% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_moves` | in-season moves touching the top 8 | none | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_pre_pct` | preseason title price, de-vigged | 57.65% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_pre_rank` | preseason title rank of 30 | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_pre_odds` | preseason title odds, American | -187 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_pre_fav` | preseason favourite | Golden State Warriors | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2017_18_pre_fav_pct` | preseason favourite's price, de-vigged | 57.65% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_team` | 2018-19 champion | TOR | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_record` | record | 58-24 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_seed` | seed | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_net_rs` | RS net rating | +5.8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_net_rs_rank` | RS net rating rank | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_net_post` | post-All-Star net rating | +7.2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_net_post_rank` | post-All-Star net rating rank | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_net_po` | playoff net rating | +5.6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_net_po_minus` | playoff minus RS net rating | -0.2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_age` | top-8 mean age | 28.9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_oldest` | top-8 oldest | 34.0 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_drafted` | top-8 drafted | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_traded` | top-8 traded for | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_signed` | top-8 signed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_returning` | top-8 returning from the season before | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_returning_share` | share of playoff minutes to returning players | 56% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_returning_contract` | top-8 with the franchise the season before, by contract | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_returning_share_contract` | share of playoff minutes to players returning by contract | 56% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_missed_rs` | top-8 RS games missed | 93 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_missed_po` | top-8 playoff games missed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_po_games` | playoff games | 24 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_top5_rs` | top-5 minutes share, RS | 56% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_top5_po` | top-5 minutes share, playoffs | 72% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_moves` | in-season moves touching the top 8 | Marc Gasol (traded for, 2019-02-07) | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_pre_pct` | preseason title price, de-vigged | 4.54% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_pre_rank` | preseason title rank of 30 | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_pre_odds` | preseason title odds, American | 1850 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_pre_fav` | preseason favourite | Golden State Warriors | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2018_19_pre_fav_pct` | preseason favourite's price, de-vigged | 55.54% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_team` | 2019-20 champion | LAL | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_record` | record | 52-19 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_seed` | seed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_net_rs` | RS net rating | +5.6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_net_rs_rank` | RS net rating rank | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_net_post` | post-All-Star net rating | +1.0 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_net_post_rank` | post-All-Star net rating rank | 10 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_net_po` | playoff net rating | +6.9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_net_po_minus` | playoff minus RS net rating | +1.4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_age` | top-8 mean age | 29.5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_oldest` | top-8 oldest | 35.1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_drafted` | top-8 drafted | 0 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_traded` | top-8 traded for | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_signed` | top-8 signed | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_returning` | top-8 returning from the season before | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_returning_share` | share of playoff minutes to returning players | 58% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_returning_contract` | top-8 with the franchise the season before, by contract | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_returning_share_contract` | share of playoff minutes to players returning by contract | 58% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_missed_rs` | top-8 RS games missed | 61 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_missed_po` | top-8 playoff games missed | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_po_games` | playoff games | 21 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_top5_rs` | top-5 minutes share, RS | 55% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_top5_po` | top-5 minutes share, playoffs | 63% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_moves` | in-season moves touching the top 8 | Markieff Morris (signed, 2020-02-23) | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_pre_pct` | preseason title price, de-vigged | 15.41% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_pre_rank` | preseason title rank of 30 | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_pre_odds` | preseason title odds, American | 450 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_pre_fav` | preseason favourite | Los Angeles Clippers | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2019_20_pre_fav_pct` | preseason favourite's price, de-vigged | 16.14% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_team` | 2020-21 champion | MIL | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_record` | record | 46-26 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_seed` | seed | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_net_rs` | RS net rating | +5.8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_net_rs_rank` | RS net rating rank | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_net_post` | post-All-Star net rating | +5.1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_net_post_rank` | post-All-Star net rating rank | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_net_po` | playoff net rating | +5.3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_net_po_minus` | playoff minus RS net rating | -0.5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_age` | top-8 mean age | 29.6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_oldest` | top-8 oldest | 35.7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_drafted` | top-8 drafted | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_traded` | top-8 traded for | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_signed` | top-8 signed | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_returning` | top-8 returning from the season before | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_returning_share` | share of playoff minutes to returning players | 55% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_returning_contract` | top-8 with the franchise the season before, by contract | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_returning_share_contract` | share of playoff minutes to players returning by contract | 56% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_missed_rs` | top-8 RS games missed | 54 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_missed_po` | top-8 playoff games missed | 8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_po_games` | playoff games | 23 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_top5_rs` | top-5 minutes share, RS | 57% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_top5_po` | top-5 minutes share, playoffs | 72% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_moves` | in-season moves touching the top 8 | P.J. Tucker (traded for, 2021-03-19) | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_pre_pct` | preseason title price, de-vigged | 12.75% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_pre_rank` | preseason title rank of 30 | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_pre_odds` | preseason title odds, American | 550 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_pre_fav` | preseason favourite | Los Angeles Lakers | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2020_21_pre_fav_pct` | preseason favourite's price, de-vigged | 22.10% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_team` | 2021-22 champion | GSW | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_record` | record | 53-29 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_seed` | seed | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_net_rs` | RS net rating | +5.5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_net_rs_rank` | RS net rating rank | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_net_post` | post-All-Star net rating | +2.0 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_net_post_rank` | post-All-Star net rating rank | 18 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_net_po` | playoff net rating | +4.9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_net_po_minus` | playoff minus RS net rating | -0.6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_age` | top-8 mean age | 28.9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_oldest` | top-8 oldest | 33.9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_drafted` | top-8 drafted | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_traded` | top-8 traded for | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_signed` | top-8 signed | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_returning` | top-8 returning from the season before | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_returning_share` | share of playoff minutes to returning players | 70% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_returning_contract` | top-8 with the franchise the season before, by contract | 7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_returning_share_contract` | share of playoff minutes to players returning by contract | 87% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_missed_rs` | top-8 RS games missed | 152 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_missed_po` | top-8 playoff games missed | 13 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_po_games` | playoff games | 22 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_top5_rs` | top-5 minutes share, RS | 51% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_top5_po` | top-5 minutes share, playoffs | 69% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_moves` | in-season moves touching the top 8 | Gary Payton II (signed, 2021-10-19) | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_pre_pct` | preseason title price, de-vigged | 8.19% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_pre_rank` | preseason title rank of 30 | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_pre_odds` | preseason title odds, American | 900 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_pre_fav` | preseason favourite | Brooklyn Nets | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2021_22_pre_fav_pct` | preseason favourite's price, de-vigged | 24.10% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_team` | 2022-23 champion | DEN | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_record` | record | 53-29 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_seed` | seed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_net_rs` | RS net rating | +3.3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_net_rs_rank` | RS net rating rank | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_net_post` | post-All-Star net rating | +0.4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_net_post_rank` | post-All-Star net rating rank | 16 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_net_po` | playoff net rating | +8.0 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_net_po_minus` | playoff minus RS net rating | +4.7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_age` | top-8 mean age | 27.6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_oldest` | top-8 oldest | 36.4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_drafted` | top-8 drafted | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_traded` | top-8 traded for | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_signed` | top-8 signed | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_returning` | top-8 returning from the season before | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_returning_share` | share of playoff minutes to returning players | 52% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_returning_contract` | top-8 with the franchise the season before, by contract | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_returning_share_contract` | share of playoff minutes to players returning by contract | 69% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_missed_rs` | top-8 RS games missed | 105 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_missed_po` | top-8 playoff games missed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_po_games` | playoff games | 20 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_top5_rs` | top-5 minutes share, RS | 57% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_top5_po` | top-5 minutes share, playoffs | 76% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_moves` | in-season moves touching the top 8 | none | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_pre_pct` | preseason title price, de-vigged | 4.01% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_pre_rank` | preseason title rank of 30 | 9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_pre_odds` | preseason title odds, American | 1800 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_pre_fav` | preseason favourite | Boston Celtics | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2022_23_pre_fav_pct` | preseason favourite's price, de-vigged | 12.68% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_team` | 2023-24 champion | BOS | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_record` | record | 64-18 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_seed` | seed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_net_rs` | RS net rating | +11.7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_net_rs_rank` | RS net rating rank | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_net_post` | post-All-Star net rating | +14.6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_net_post_rank` | post-All-Star net rating rank | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_net_po` | playoff net rating | +8.6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_net_po_minus` | playoff minus RS net rating | -3.0 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_age` | top-8 mean age | 29.3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_oldest` | top-8 oldest | 37.7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_drafted` | top-8 drafted | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_traded` | top-8 traded for | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_signed` | top-8 signed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_returning` | top-8 returning from the season before | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_returning_share` | share of playoff minutes to returning players | 76% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_returning_contract` | top-8 with the franchise the season before, by contract | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_returning_share_contract` | share of playoff minutes to players returning by contract | 76% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_missed_rs` | top-8 RS games missed | 87 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_missed_po` | top-8 playoff games missed | 12 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_po_games` | playoff games | 19 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_top5_rs` | top-5 minutes share, RS | 58% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_top5_po` | top-5 minutes share, playoffs | 76% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_moves` | in-season moves touching the top 8 | none | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_pre_pct` | preseason title price, de-vigged | 14.69% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_pre_rank` | preseason title rank of 30 | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_pre_odds` | preseason title odds, American | 450 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_pre_fav` | preseason favourite | Boston Celtics / Denver Nuggets | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2023_24_pre_fav_pct` | preseason favourite's price, de-vigged | 14.69% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_team` | 2024-25 champion | OKC | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_record` | record | 68-14 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_seed` | seed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_net_rs` | RS net rating | +12.7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_net_rs_rank` | RS net rating rank | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_net_post` | post-All-Star net rating | +12.4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_net_post_rank` | post-All-Star net rating rank | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_net_po` | playoff net rating | +8.6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_net_po_minus` | playoff minus RS net rating | -4.1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_age` | top-8 mean age | 25.5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_oldest` | top-8 oldest | 30.9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_drafted` | top-8 drafted | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_traded` | top-8 traded for | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_signed` | top-8 signed | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_returning` | top-8 returning from the season before | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_returning_share` | share of playoff minutes to returning players | 78% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_returning_contract` | top-8 with the franchise the season before, by contract | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_returning_share_contract` | share of playoff minutes to players returning by contract | 79% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_missed_rs` | top-8 RS games missed | 154 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_missed_po` | top-8 playoff games missed | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_po_games` | playoff games | 23 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_top5_rs` | top-5 minutes share, RS | 54% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_top5_po` | top-5 minutes share, playoffs | 65% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_moves` | in-season moves touching the top 8 | none | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_pre_pct` | preseason title price, de-vigged | 10.80% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_pre_rank` | preseason title rank of 30 | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_pre_odds` | preseason title odds, American | 675 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_pre_fav` | preseason favourite | Boston Celtics | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2024_25_pre_fav_pct` | preseason favourite's price, de-vigged | 19.69% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_team` | 2025-26 champion | NYK | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_record` | record | 53-29 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_seed` | seed | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_net_rs` | RS net rating | +6.3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_net_rs_rank` | RS net rating rank | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_net_post` | post-All-Star net rating | +6.8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_net_post_rank` | post-All-Star net rating rank | 8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_net_po` | playoff net rating | +15.4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_net_po_minus` | playoff minus RS net rating | +9.1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_age` | top-8 mean age | 28.8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_oldest` | top-8 oldest | 30.9 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_drafted` | top-8 drafted | 1 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_traded` | top-8 traded for | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_signed` | top-8 signed | 2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_returning` | top-8 returning from the season before | 8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_returning_share` | share of playoff minutes to returning players | 91% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_returning_contract` | top-8 with the franchise the season before, by contract | 8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_returning_share_contract` | share of playoff minutes to players returning by contract | 91% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_missed_rs` | top-8 RS games missed | 141 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_missed_po` | top-8 playoff games missed | 3 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_po_games` | playoff games | 19 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_top5_rs` | top-5 minutes share, RS | 60% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_top5_po` | top-5 minutes share, playoffs | 68% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_moves` | in-season moves touching the top 8 | none | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_pre_pct` | preseason title price, de-vigged | 8.27% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_pre_rank` | preseason title rank of 30 | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_pre_odds` | preseason title odds, American | 900 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_pre_fav` | preseason favourite | Oklahoma City Thunder | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_2025_26_pre_fav_pct` | preseason favourite's price, de-vigged | 24.32% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_mean_age` | top-8 mean age across champions | 28.7 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_mean_returning` | top-8 returning, mean across champions | 5.8 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_mean_returning_contract` | top-8 returning by contract, mean across champions | 6.0 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_mean_returning_share` | share of playoff minutes to returning players, mean | 71% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_mean_returning_share_contract` | share of playoff minutes to players returning by contract, mean | 74% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_seed_1_n` | champions that were the 1 seed | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_top3_net_n` | champions in the top three of RS net rating | 5 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_top5_net_n` | champions in the top five of RS net rating | 10 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_worst_rs_rank` | worst RS net rating rank of a champion | 6 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_worst_post_rank` | worst post-All-Star net rating rank of a champion | 18 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_moves_n` | champions with an in-season move touching the top 8 | 4 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_mean_top5_rs` | top-5 minutes share RS, mean | 56% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_mean_top5_po` | top-5 minutes share playoffs, mean | 70% | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_mean_missed_rs` | top-8 RS games missed, mean | 101 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `c1_mean_missed_po` | top-8 playoff games missed, mean | 6.2 | OBSERVED | QUOTABLE | `c1_champions_20260924T195859Z` |
| `williams_prior_mpg` | Cody Williams, minutes per appearance for Utah 2025-26 | 24.3 | OBSERVED | FACT | `williams_ordering_check_20260929T061318Z` |
| `w_shannon_rank` | Shannon's rank on Minnesota's roster by the model's score | 13 | MODELED | FACT | `williams_ordering_check_20260929T061318Z` |
| `w_pool_n` | available players in Minnesota's pool | 13 | OBSERVED | FACT | `williams_ordering_check_20260929T061318Z` |
| `w_rank_primary` | Williams's rank under the primary ordering (movers 0.2 / 0.8) | 12 | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_mpg_primary` | Williams's minutes under the primary ordering (movers 0.2 / 0.8) | 0.0 | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_delta_primary` | offseason delta under the primary ordering (movers 0.2 / 0.8), mean of four views | +0.30 | MODELED | QUOTABLE AS BAND | `williams_ordering_check_20260929T061318Z` |
| `w_sign_primary` | offseason verdict under the primary ordering (movers 0.2 / 0.8) | MIXED | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_rank_flat` | Williams's rank under the flat 0.5 / 0.5 ordering (sensitivity) | 10 | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_mpg_flat` | Williams's minutes under the flat 0.5 / 0.5 ordering (sensitivity) | 16.1 | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_delta_flat` | offseason delta under the flat 0.5 / 0.5 ordering (sensitivity), mean of four views | -0.78 | MODELED | QUOTABLE AS BAND | `williams_ordering_check_20260929T061318Z` |
| `w_sign_flat` | offseason verdict under the flat 0.5 / 0.5 ordering (sensitivity) | ALL NEGATIVE | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_rank_impact_only` | Williams's rank under impact-only ordering | 13 | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_mpg_impact_only` | Williams's minutes under impact-only ordering | 0.0 | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_delta_impact_only` | offseason delta under impact-only ordering, mean of four views | +0.35 | MODELED | QUOTABLE AS BAND | `williams_ordering_check_20260929T061318Z` |
| `w_sign_impact_only` | offseason verdict under impact-only ordering | MIXED | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_ret_n` | mover cohort: players who changed teams | 34 | OBSERVED | FACT | `mover_minutes_base_rate_20260925T140950Z` |
| `w_ret_median` | mover cohort: median share of prior minutes kept | 74% | OBSERVED | QUOTABLE | `mover_minutes_base_rate_20260925T140950Z` |
| `w_ret_q25` | mover cohort: lower quartile | 43% | OBSERVED | QUOTABLE | `mover_minutes_base_rate_20260925T140950Z` |
| `w_ret_q75` | mover cohort: upper quartile | 90% | OBSERVED | QUOTABLE | `mover_minutes_base_rate_20260925T140950Z` |
| `w_ret_top10_n` | movers who landed on a top-ten team by wins | 8 | OBSERVED | FACT | `mover_minutes_base_rate_20260925T140950Z` |
| `w_ret_top10_median` | their median share of prior minutes kept | 48% | OBSERVED | QUOTABLE | `mover_minutes_base_rate_20260925T140950Z` |
| `w_ret_600_n` | movers who landed on a .600 team | 6 | OBSERVED | FACT | `mover_minutes_base_rate_20260925T140950Z` |
| `w_ret_600_median` | their median share kept | 48% | OBSERVED | QUOTABLE | `mover_minutes_base_rate_20260925T140950Z` |
| `w_cal_top10_mpg` | Williams at the top-ten-destination retention | 11.7 | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_cal_top10_delta` | offseason delta at that level, mean of four views | -0.71 | MODELED | QUOTABLE AS BAND | `williams_ordering_check_20260929T061318Z` |
| `w_cal_top10_sign` | offseason verdict at that level | ALL NEGATIVE | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `w_cal_all_raw_mpg` | Williams at the all-movers median retention, before the default cap | 18.0 | MODELED | QUOTABLE | `williams_ordering_check_20260929T061318Z` |
| `c4_in_n` | players in with a 2026-27 salary | 7 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_in_total` | 2026-27 salary in | $75,840,737 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_in_total_m` | 2026-27 salary in, rounded | $75.8 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_out_n` | players out with a 2026-27 salary | 7 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_out_total` | 2026-27 salary out | $80,779,576 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_out_total_m` | 2026-27 salary out, rounded | $80.8 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_rows` | ledger rows | 37 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_single_sourced` | ledger rows with one source | 0 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_hylanbo01_retained_salary` | Bones Hyland 2026-27 salary (retained) | $2,845,883 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_hylanbo01_retained_salary_m` | Bones Hyland 2026-27 salary, rounded | $2.8 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_hylanbo01_retained_total` | Bones Hyland remaining contract: years, total | 1 years, $2,845,883 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_anderky01_out_salary` | Kyle Anderson 2026-27 salary (out) | $2,449,421 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_anderky01_out_salary_m` | Kyle Anderson 2026-27 salary, rounded | $2.4 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_anderky01_out_total` | Kyle Anderson remaining contract: years, total | 1 years, $2,449,421 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_conlemi01_out_salary` | Mike Conley 2026-27 salary (out) | $2,449,421 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_conlemi01_out_salary_m` | Mike Conley 2026-27 salary, rounded | $2.4 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_conlemi01_out_total` | Mike Conley remaining contract: years, total | 1 years, $2,449,421 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_evansis01_in_salary` | Isaiah Evans 2026-27 salary (in) | $1,357,763 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_evansis01_in_salary_m` | Isaiah Evans 2026-27 salary, rounded | $1.4 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_evansis01_in_total` | Isaiah Evans remaining contract: years, total | 4 years, $9,264,648 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_greenjo02_in_salary` | Josh Green 2026-27 salary (in) | $14,679,012 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_greenjo02_in_salary_m` | Josh Green 2026-27 salary, rounded | $14.7 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_greenjo02_in_total` | Josh Green remaining contract: years, total | 1 years, $14,679,012 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_ballla01_in_salary` | LaMelo Ball 2026-27 salary (in) | $40,770,520 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_ballla01_in_salary_m` | LaMelo Ball 2026-27 salary, rounded | $40.8 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_ballla01_in_total` | LaMelo Ball remaining contract: years, total | 3 years, $130,746,840 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_lylestr01_in_salary` | Trey Lyles 2026-27 salary (in) | $2,449,421 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_lylestr01_in_salary_m` | Trey Lyles 2026-27 salary, rounded | $2.4 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_lylestr01_in_total` | Trey Lyles remaining contract: years, total | 1 years, $2,449,421 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_randlju01_out_salary` | Julius Randle 2026-27 salary (out) | $33,333,334 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_randlju01_out_salary_m` | Julius Randle 2026-27 salary, rounded | $33.3 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_randlju01_out_total` | Julius Randle remaining contract: years, total | 2 years, $69,135,802 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_reidna01_out_salary` | Naz Reid 2026-27 salary (out) | $23,275,862 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_reidna01_out_salary_m` | Naz Reid 2026-27 salary, rounded | $23.3 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_reidna01_out_total` | Naz Reid remaining contract: years, total | 4 years, $103,448,276 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_dosunay01_retained_salary` | Ayo Dosunmu 2026-27 salary (retained) | $19,310,345 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_dosunay01_retained_salary_m` | Ayo Dosunmu 2026-27 salary, rounded | $19.3 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_dosunay01_retained_total` | Ayo Dosunmu remaining contract: years, total | 5 years, $112,000,000 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_clarkja02_retained_salary` | Jaylen Clark 2026-27 salary (retained) | $3,086,420 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_clarkja02_retained_salary_m` | Jaylen Clark 2026-27 salary, rounded | $3.1 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_clarkja02_retained_total` | Jaylen Clark remaining contract: years, total | 3 years, $10,000,000 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_phillju01_out_salary` | Julian Phillips 2026-27 salary (out) | $2,537,526 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_phillju01_out_salary_m` | Julian Phillips 2026-27 salary, rounded | $2.5 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_phillju01_out_total` | Julian Phillips remaining contract: years, total | 1 years, $2,537,526 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_willico04_in_salary` | Cody Williams 2026-27 salary (in) | $6,015,600 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_willico04_in_salary_m` | Cody Williams 2026-27 salary, rounded | $6.0 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_willico04_in_total` | Cody Williams remaining contract: years, total | 2 years, $13,685,490 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_konchjo01_in_salary` | John Konchar 2026-27 salary (in) | $4,504,421 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_konchjo01_in_salary_m` | John Konchar 2026-27 salary, rounded | $4.5 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_konchjo01_in_total` | John Konchar remaining contract: years, total | 3 years, $8,614,421 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_konchjo01_out_salary` | John Konchar 2026-27 salary (out) | $2,055,000 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_konchjo01_out_salary_m` | John Konchar 2026-27 salary, rounded | $2.1 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_konchjo01_out_total` | John Konchar remaining contract: years, total | 3 years, $8,614,421 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_greenjo02_out_salary` | Josh Green 2026-27 salary (out) | $14,679,012 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_greenjo02_out_salary_m` | Josh Green 2026-27 salary, rounded | $14.7 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_greenjo02_out_total` | Josh Green remaining contract: years, total | 1 years, $14,679,012 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_kuminjo01_in_salary` | Jonathan Kuminga 2026-27 salary (in) | $6,064,000 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_kuminjo01_in_salary_m` | Jonathan Kuminga 2026-27 salary, rounded | $6.1 million | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_kuminjo01_in_total` | Jonathan Kuminga remaining contract: years, total | 2 years, $12,431,200 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_grades_read` | graded pieces fetched and read | 25 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_grades_whole_n` | national whole-offseason grades | 7 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_grades_whole` | national whole-offseason grades, outlet and grade | ESPN C+; Bleacher Report D+; Bleacher Report B+; CBS Sports B; CBS Sports B; Yahoo Sports C; The Big Lead (Minute Media) A- | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_grades_trade_n` | national grades of the Ball trade alone | 8 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |
| `c4_grades_not_read` | pieces found but not read | 3 | OBSERVED | QUOTABLE | `c4_ledger_20260924T170420Z` |

