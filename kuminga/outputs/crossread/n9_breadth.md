<!-- cross-read export of kuminga\docs\n9_breadth.md | run export_crossread_20260929T183814Z | commit 749ed93a | 2026-09-29T18:38:14Z | visuals replaced by [visual: id]; N9 documents marked PENDING -->

> **PENDING. N9 is not in the series.** The breadth analysis and its proxies are here for the cross-read only; nothing from them enters the parts until Bobby decides (D112, D113).

# N9: the breadth of the odds (version 2)

Run `n9_breadth_20260929T183215Z`. PENDING: N9 does not enter the series while the headline gate (G5) fails or until Bobby decides. Design: D112 as revised by D113 in decisions.md.

## Gates

- G1 zero noise reproduces the published net: worst gap 8.9e-15.
- G2 the proxy returns each team's simulated odds at its anchor: worst gap 1.0e-03 pp.
- G3 the seeding share reproduces C3's direct simulations: worst title gap 0.076 pp, worst drop gap 0.026 pp. Seeding share by view, un-aged / aged: consensus 0.13 / 0.25, rapm 0.17 / 0.10, box 0.12 / 0.27, darko 0.16 / 0.19.
- G4 the seed rule reproduces the published mean seed: worst gap 0.020.
- G5 (unaged): headline 2.76%, mean over the joint draws 2.49%, gap -0.27 pp against a tolerance of 0.15: **fails**.
- G5 (aged): headline 3.72%, mean over the joint draws 3.34%, gap -0.38 pp against a tolerance of 0.15: **fails**.

## Minnesota's headline cells, by source

| sources | basis | mean | gap to headline | p10 | p50 | p90 |
|---|---|---|---|---|---|---|
| all three sources | unaged | 2.49% | -0.27 | 1.61 | 2.65 | 3.32 |
| all three sources | aged | 3.34% | -0.38 | 2.30 | 3.52 | 4.34 |
| availability only | unaged | 2.74% | -0.02 | 2.50 | 2.75 | 2.95 |
| availability only | aged | 3.65% | -0.07 | 3.30 | 3.68 | 3.96 |
| mover order only | unaged | 2.21% | -0.55 | 1.68 | 1.68 | 2.76 |
| mover order only | aged | 3.08% | -0.64 | 2.44 | 2.44 | 3.75 |
| rookie impact only | unaged | 2.91% | +0.15 | 2.76 | 2.76 | 3.33 |
| rookie impact only | aged | 3.91% | +0.19 | 3.73 | 3.75 | 4.40 |
| availability and rookies (mover order at the primary) | unaged | 2.86% | +0.10 | 2.52 | 2.80 | 3.28 |
| availability and rookies (mover order at the primary) | aged | 3.79% | +0.07 | 3.33 | 3.73 | 4.31 |
| sensitivity: availability reaching the playoffs too | unaged | 2.62% | -0.14 | 0.99 | 2.68 | 4.04 |
| sensitivity: availability reaching the playoffs too | aged | 3.31% | -0.41 | 1.44 | 3.41 | 4.90 |

## Minnesota against the teams priced beside it

| team | market | mean | p10 | p50 | p90 | upside share | draws above market | wins p10 to p90 | seed p10 to p90 | P(top six) p10 to p90 |
|---|---|---|---|---|---|---|---|---|---|---|
| MIN | 3.16% | 2.21% | 0.57 | 2.05 | 3.98 | 74% | 22% | 35.1 to 46.8 | 4.1 to 7.7 | 17% to 96% |
| DEN | 3.16% | 4.33% | 1.46 | 4.19 | 7.45 | 71% | 65% | 38.7 to 53.9 | 2.5 to 5.9 | 65% to 100% |
| DET | 3.16% | 6.61% | 1.79 | 5.81 | 11.99 | 74% | 77% | 43.2 to 54.3 | 1.6 to 5.1 | 74% to 100% |
| CLE | 3.16% | 1.15% | 0.12 | 0.42 | 3.96 | 91% | 15% | 35.1 to 47.3 | 5.0 to 9.7 | 1% to 76% |
| TOR | 3.16% | 4.94% | 2.65 | 4.27 | 7.66 | 67% | 79% | 41.6 to 53.0 | 2.2 to 6.6 | 46% to 99% |
| BOS | 5.47% | 12.94% | 7.61 | 11.18 | 22.16 | 66% | 100% | 47.0 to 61.8 | 1.0 to 2.6 | 96% to 100% |
| MIA | 2.65% | 3.22% | 1.29 | 2.99 | 5.54 | 71% | 57% | 35.3 to 51.5 | 3.0 to 9.4 | 3% to 97% |

**Variant: the mover order held at the primary for every team** (availability and rookie impact only). Headline gate: unaged 2.86% against 2.76%, gap +0.10, passes; aged 3.79% against 3.72%, gap +0.07, passes.

| team | market | mean | p10 | p50 | p90 | upside share | draws above market | wins p10 to p90 | seed p10 to p90 | P(top six) p10 to p90 |
|---|---|---|---|---|---|---|---|---|---|---|
| MIN | 3.16% | 2.45% | 0.63 | 2.37 | 4.22 | 73% | 29% | 35.5 to 47.3 | 4.0 to 7.5 | 22% to 96% |
| DEN | 3.16% | 4.34% | 1.48 | 4.20 | 7.43 | 71% | 66% | 38.7 to 54.0 | 2.5 to 5.9 | 65% to 100% |
| DET | 3.16% | 6.69% | 1.87 | 5.97 | 11.92 | 73% | 77% | 43.5 to 54.3 | 1.6 to 5.0 | 76% to 100% |
| CLE | 3.16% | 1.16% | 0.12 | 0.42 | 3.97 | 91% | 15% | 35.1 to 47.3 | 5.0 to 9.7 | 2% to 76% |
| TOR | 3.16% | 4.93% | 2.63 | 4.24 | 7.66 | 67% | 79% | 41.6 to 52.9 | 2.3 to 6.6 | 46% to 99% |
| BOS | 5.47% | 12.92% | 7.68 | 11.10 | 22.05 | 65% | 100% | 47.0 to 61.8 | 1.0 to 2.6 | 96% to 100% |
| MIA | 2.65% | 3.36% | 1.42 | 3.11 | 5.69 | 70% | 61% | 35.6 to 51.9 | 2.9 to 9.2 | 5% to 98% |

Upside share: the share of the mean title odds contributed by the upper half of the draws (50% would be no skew).

## Where the breadth comes from

| team | within cells (the draws) | between cells | view | basis | allocator | sd of title odds |
|---|---|---|---|---|---|---|
| MIN | 22% | 78% | 41% | 8% | 27% | 1.35 |
| DEN | 13% | 87% | 32% | 9% | 41% | 2.26 |
| DET | 12% | 88% | 60% | 0% | 26% | 3.85 |
| CLE | 2% | 98% | 91% | 0% | 4% | 1.41 |
| TOR | 26% | 74% | 18% | 1% | 47% | 2.07 |
| BOS | 9% | 91% | 30% | 4% | 44% | 5.26 |
| MIA | 18% | 82% | 23% | 16% | 35% | 1.68 |

## Availability, Minnesota's rotation

Typical availability for rotation minutes, league-wide: 0.70 of games. A player's draw enters relative to it.

| player | age | last season's share | seasons at 60% or less (of 3) | cohort n | predicted mean share | p10 | relative to typical |
|---|---|---|---|---|---|---|---|
| Trey Lyles | 31 | 0.00 | 0 | 54 | 0.43 | 0.00 | 0.62 |
| Jonathan Kuminga | 24 | 0.44 | 2 | 41 | 0.45 | 0.00 | 0.64 |
| Terrence Shannon Jr. | 26 | 0.52 | 2 | 90 | 0.47 | 0.03 | 0.68 |
| Joan Beringer | 20 | 0.48 | 1 | 62 | 0.58 | 0.15 | 0.83 |
| Nah'Shon Hyland | 26 | 0.85 | 2 | 53 | 0.65 | 0.18 | 0.94 |
| LaMelo Ball | 25 | 0.88 | 2 | 125 | 0.66 | 0.16 | 0.95 |
| Jaylen Clark | 25 | 0.83 | 1 | 77 | 0.68 | 0.28 | 0.98 |
| Anthony Edwards | 25 | 0.74 | 0 | 200 | 0.76 | 0.50 | 1.10 |
| Cody Williams | 22 | 0.82 | 0 | 174 | 0.77 | 0.47 | 1.10 |
| Ayo Dosunmu | 27 | 0.84 | 1 | 110 | 0.77 | 0.39 | 1.10 |
| Jaden McDaniels | 26 | 0.89 | 0 | 556 | 0.80 | 0.52 | 1.15 |
| Donte DiVincenzo | 30 | 1.00 | 0 | 367 | 0.81 | 0.54 | 1.17 |
| Rudy Gobert | 35 | 0.93 | 0 | 173 | 0.83 | 0.58 | 1.18 |

## Limits

Games share mixes injury with a coach's decision, and a season out of the NBA (overseas) reads as a season missed; Kuminga's 2025-26 and Lyles's 2025-26 are both examples. Availability is drawn independently player by player, for the regular season only; April is the fragility question (N5), and the sensitivity above shows the cost if games were missed at random through the playoffs too. The mover fork is an equal-probability choice between two orderings, not an estimate of which is right. The other teams are priced on an anchored proxy of Minnesota's f-curve. The rookie prior sd comes from one class.
