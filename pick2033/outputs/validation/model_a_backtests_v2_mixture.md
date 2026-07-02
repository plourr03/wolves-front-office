# Model A rolling-origin backtests (gates 8.1)
origins 1995-2019, horizons 1-7, 5153 scored cells, 4000 paths/forecast

|   horizon |   crps_model |   crps_persistence |   crps_pooled |   coverage_80 |   n |
|----------:|-------------:|-------------------:|--------------:|--------------:|----:|
|         1 |        1.897 |              2.911 |         1.888 |         0.775 | 737 |
|         2 |        2.31  |              3.802 |         2.299 |         0.774 | 736 |
|         3 |        2.522 |              4.5   |         2.5   |         0.764 | 736 |
|         4 |        2.542 |              4.783 |         2.519 |         0.776 | 736 |
|         5 |        2.584 |              5.041 |         2.562 |         0.77  | 736 |
|         6 |        2.594 |              5.041 |         2.58  |         0.776 | 736 |
|         7 |        2.623 |              5.128 |         2.614 |         0.772 | 736 |

- coverage gate (80% PI in [72,88] all horizons): **PASS**
- skill gate at h=7 (model 2.623 < persistence 5.128 and pooled 2.614): **FAIL**
- dispersion gate (sim wins SD 12.79 vs hist 12.86, within 15%): **PASS**