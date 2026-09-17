# Canonical figures

Where two numbers in this project describe nearly the same thing, this table says which one is canonical and why.

| label                                   | object                                                                               | source                             | canonical   |   consensus |   rapm |   box |   darko |   mean |   lo |   hi |
|:----------------------------------------|:-------------------------------------------------------------------------------------|:-----------------------------------|:------------|------------:|-------:|------:|--------:|-------:|-----:|-----:|
| Minnesota before the offseason          | R6 baseline: the 2025-26 end-of-season roster, 18 players, no injuries               | run_sim.py (direct simulation)     | True        |        2.95 |   2.95 |  2.92 |    2.95 |   2.94 | 2.92 | 2.95 |
| Minnesota if the free agents had walked | Shapley empty coalition: no moves AND no re-signings, 15 players + a 14th-man charge | shapley.py (f-curve interpolation) | False       |        1.80 |   1.89 |  1.89 |    2.56 |   2.03 | 1.80 | 2.56 |
| Minnesota after the offseason           | the current roster, Green removed per R3                                             | run_sim.py (direct simulation)     | True        |        0.82 |   1.20 |  2.11 |    2.62 |   1.69 | 0.82 | 2.62 |
| Minnesota after the offseason (f-curve) | the same roster, priced by interpolation                                             | shapley.py (f-curve interpolation) | False       |        0.79 |   1.17 |  2.19 |    2.56 |   1.68 | 0.79 | 2.56 |

## Notes

**Minnesota before the offseason** (canonical): CANONICAL for any before/after claim. This is what T1 and T2 use.

**Minnesota if the free agents had walked** (secondary): The natural origin for attribution. NOT the same roster as the R6 baseline and must not be called 'did nothing'.

**Minnesota after the offseason** (canonical): CANONICAL. Band 0.82 to 2.62.

**Minnesota after the offseason (f-curve)** (secondary): Used only so 256 coalitions are affordable. Differs from the direct sim by interpolation error alone.


f-curve interpolation error against the direct simulation is at most 0.078pp across the four forks. That is the price of pricing 256 coalitions by interpolation instead of simulating each one, and it is small relative to the fork spread.
