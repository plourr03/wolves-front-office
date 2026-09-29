# N9: the breadth of the odds

Run `n9_breadth_20260929T125248Z`. No written N9 specification exists in the project; the design is D112 in decisions.md, built from the listed components. Every figure here is in `n9_breadth_summary.csv`, `n9_breadth_cells.csv`, `n9_breadth_sources.csv`, `n9_proxy_validation.csv`, `n9_proxy_tendency.csv` and `n9_proxies_history.csv`.

## The four sources and the cells

Each team has 32 cells: four impact views, two aging bases, two rotation orderings (the primary mover-discounted order and the flat half-and-half sensitivity), two minutes allocators (team-rank and pooled). A cell's expected net is the pipeline's own formula; the primary cell reproduces the published strengths on both bases (G1). Minnesota's cells are priced on its own f-curve. Every other team is priced on an anchored proxy: Minnesota's f-curve shifted in log-odds to pass through that team's own simulated title odds at its primary cell (G2). The simulator's season noise is not drawn again, because the f-curve already integrates it.

## Minnesota against the teams priced beside it

| team | market | mean | p10 | p25 | p50 | p75 | p90 | upside share | cells above market | wins p10 to p90 | mean seed range | P(top six) range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MIN | 3.16% | 2.05% | 0.62 | 1.13 | 1.86 | 2.75 | 3.71 | 74% | 16% | 37.3 to 45.0 | 4.1 to 6.2 | 55% to 96% |
| DEN | 3.16% | 3.87% | 1.43 | 2.26 | 3.81 | 5.06 | 6.03 | 71% | 62% | 39.5 to 51.8 | 2.9 to 5.0 | 86% to 99% |
| DET | 3.16% | 6.21% | 1.81 | 3.96 | 5.78 | 8.30 | 11.45 | 73% | 75% | 42.0 to 54.0 | 1.7 to 4.7 | 81% to 100% |
| CLE | 3.16% | 1.10% | 0.11 | 0.17 | 0.41 | 1.37 | 3.82 | 91% | 12% | 34.3 to 45.6 | 5.3 to 9.8 | 2% to 72% |
| TOR | 3.16% | 4.62% | 3.04 | 3.40 | 3.92 | 6.20 | 6.91 | 64% | 75% | 42.8 to 52.9 | 3.3 to 5.6 | 66% to 96% |
| BOS | 5.47% | 12.75% | 8.05 | 9.38 | 10.73 | 15.01 | 22.18 | 64% | 100% | 47.4 to 62.5 | 1.0 to 2.3 | 99% to 100% |
| MIA | 2.65% | 3.05% | 1.42 | 1.89 | 2.89 | 4.06 | 4.92 | 69% | 56% | 39.2 to 50.8 | 4.1 to 7.0 | 39% to 91% |

Upside share is the share of a team's mean title odds contributed by the upper half of its 32 cells; 50% would mean no upside skew at all.

## Where the breadth comes from

| team | view | basis | ordering | allocator | interaction | sd of expected net |
|---|---|---|---|---|---|---|
| MIN | 32% | 20% | 8% | 32% | 8% | 1.42 |
| DEN | 15% | 61% | 0% | 21% | 3% | 2.02 |
| DET | 29% | 41% | 0% | 28% | 2% | 1.76 |
| CLE | 41% | 39% | 0% | 19% | 1% | 1.86 |
| TOR | 23% | 52% | 0% | 23% | 2% | 1.51 |
| BOS | 39% | 49% | 0% | 11% | 1% | 2.20 |
| MIA | 3% | 77% | 0% | 15% | 3% | 1.91 |

## The proxies

The model cannot be run on past seasons, so breadth is bridged by correlates that exist for the eleven champions and the 48 top-five non-champions: top-eight mean age, returning share of playoff minutes by contract, and in-season acquisitions among the eight.

**Validation on 2026-27** (Spearman across the 30 teams; the odds ratio only for teams the model has at 0.5% or more):

| measure | proxy | n | rho | p |
|---|---|---|---|---|
| breadth of net (p90 - p10) | top-eight mean age | 30 | +0.24 | 0.195 |
| breadth of net (p90 - p10) | returning minutes share | 30 | -0.27 | 0.154 |
| breadth of net (p90 - p10) | movers in the rotation | 30 | +0.30 | 0.109 |
| upside share | top-eight mean age | 30 | -0.24 | 0.210 |
| upside share | returning minutes share | 30 | -0.15 | 0.425 |
| upside share | movers in the rotation | 30 | +0.08 | 0.674 |
| breadth of title odds (p90 / p10, teams at 0.5% or more) | top-eight mean age | 17 | -0.38 | 0.130 |
| breadth of title odds (p90 / p10, teams at 0.5% or more) | returning minutes share | 17 | -0.20 | 0.439 |
| breadth of title odds (p90 / p10, teams at 0.5% or more) | movers in the rotation | 17 | +0.19 | 0.457 |

**Tendency on the eleven seasons** (Mann-Whitney, two-sided; lean at p below 0.05, Bonferroni for three tests 0.017):

| proxy | champions' median | contenders' median | p | leans |
|---|---|---|---|---|
| top-eight mean age | 28.90 | 29.30 | 0.419 | no |
| returning playoff-minutes share, by contract | 0.77 | 0.75 | 0.974 | no |
| in-season acquisitions among the eight | 0.00 | 1.00 | 0.158 | no |

Minnesota on the proxies: top-eight mean age 26.5, returning minutes share 76%, 2 movers in the ten.

## Limits

The other teams' pricing is a proxy anchored on one simulated point per view and basis; Minnesota's own f-curve slope is assumed to carry. The four sources are the model's forks, equally weighted; nothing here says one view or basis is more likely than another. The historical proxies are correlates of breadth, not breadth: a team can be young and narrow, or old and wide.
