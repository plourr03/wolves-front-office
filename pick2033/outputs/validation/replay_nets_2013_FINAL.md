# 2013 Celtics-Nets replay (spec 8.5 primary) -- FINAL
- as-of 2013 fit, 20000 paths, pre-2019 weighted lottery, pure Model A (declared default)
- runtime 11.6s
- 2014: realized 17, 90% interval 4-28, median 18 -> **INSIDE** (P(slot <= realized) 0.47)
- 2016: realized 3, 90% interval 2-29, median 16 -> **INSIDE** (P(slot <= realized) 0.09)
- 2017: realized 1, 90% interval 2-29, median 16 -> **OUTSIDE** (P(slot <= realized) 0.03)
- 2018: realized 8, 90% interval 2-29, median 15 -> **INSIDE** (P(slot <= realized) 0.28)
- replay verdict: 3/4 inside -> **FAIL**
- gate 8.5: **PARTIAL** (1 of 3 replays built; 2019 PG package and the negative control remain open)