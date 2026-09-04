# Canonical figures

Where two numbers in this project describe nearly the same thing, this table says which one is canonical and why.

| label                                   | object                                                                               | source                             | canonical   |   consensus |   rapm |   box |   darko |   mean |   lo |   hi |
|:----------------------------------------|:-------------------------------------------------------------------------------------|:-----------------------------------|:------------|------------:|-------:|------:|--------:|-------:|-----:|-----:|
| Minnesota before the offseason          | R6 baseline: the 2025-26 end-of-season roster, 18 players, no injuries               | run_sim.py (direct simulation)     | True        |        2.95 |   2.95 |  2.92 |    2.95 |   2.94 | 2.92 | 2.95 |
| Minnesota if the free agents had walked | Shapley empty coalition: no moves AND no re-signings, 15 players + a 14th-man charge | shapley.py (f-curve interpolation) | False       |        3.16 |   3.49 |  2.59 |    3.79 |   3.26 | 2.59 | 3.79 |
| Minnesota after the offseason           | the current roster, Green removed per R3                                             | run_sim.py (direct simulation)     | True        |        0.66 |   1.05 |  1.96 |    2.37 |   1.51 | 0.66 | 2.37 |
| Minnesota after the offseason (f-curve) | the same roster, priced by interpolation                                             | shapley.py (f-curve interpolation) | False       |        1.78 |   2.38 |  2.96 |    3.88 |   2.75 | 1.78 | 3.88 |

## Notes

**Minnesota before the offseason** (canonical): CANONICAL for any before/after claim. This is what T1 and T2 use.

**Minnesota if the free agents had walked** (secondary): The natural origin for attribution. NOT the same roster as the R6 baseline and must not be called 'did nothing'.

**Minnesota after the offseason** (canonical): CANONICAL. Band 1.67 to 3.83.

**Minnesota after the offseason (f-curve)** (secondary): Used only so 256 coalitions are affordable. Differs from the direct sim by interpolation error alone.


f-curve interpolation error against the direct simulation is at most 1.512pp across the four forks. That is the price of pricing 256 coalitions by interpolation instead of simulating each one, and it is small relative to the fork spread.
