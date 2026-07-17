# Phase 3: AVAIL-PACE Predictive Validity and the LaMelo Threshold

Tripwire backtest, Phase 3 (Scenario B / AVAIL-PACE). Produced 2026-07-17. Data: `data/avail_pace_cases.parquet`. Script: `avail_pace_mapping.py`.

This is the empirical mapping the redefined AVAIL-PACE wire takes its threshold from. It is the wire the whole project leans on, and it is panel-independent (pure box-score availability), so it is the first Phase 3 result to land.

## The question

Does early-season games-played pace predict how a player's availability resolves over the full season? If it does, and stabilizes by the R1 read (~game 20), then AVAIL-PACE is a real wire. If early pace is noise, it is not.

## Result: yes, strongly

388 Scenario B cases with complete data. Early feature: games the arriving player was available (minutes > 0) among the team's first N games. Outcome: full-season games played (YB1), and whether it landed below the player's prior-three-season median plan (YB3).

**Spearman rank correlation, early availability vs full-season games played:**

| N | cases | Spearman | sign consistency |
|---|---|---|---|
| 10 | 385 | 0.690 | 0.764 |
| 15 | 383 | 0.733 | 0.775 |
| 20 | 377 | **0.769** | **0.772** |
| 25 | 369 | 0.807 | 0.780 |
| 30 | 339 | 0.829 | 0.791 |

At the R1 read (N=20), Spearman is 0.769 and sign consistency is 0.772, **above SIGN_GATE (0.70)**. AVAIL-PACE is exempt from the reliability gate (it is an exact count with no sampling noise), but note that its predictive signal strengthens monotonically with N and is already strong at N=20, which is the honest version of "stabilizes fast enough to trust at 20 games."

## Calibration is clean and monotone

Mean full-season availability by early-pace tertile at N=20:

| Early-pace tertile | cases | early avail frac | full-season avail frac | below-plan rate |
|---|---|---|---|---|
| low | 134 | 0.18 | 0.31 | 0.80 |
| mid | 136 | 0.75 | 0.64 | 0.39 |
| high | 107 | 0.99 | 0.81 | 0.25 |

A player available in a fifth of his team's first 20 games finishes at a third of the season and lands below his own plan 80% of the time. A player available in nearly all of the first 20 finishes at 80% of the season and beats his plan three times in four. The signal is not subtle.

## The threshold

Below-plan probability by early-availability bucket at N=20:

| Availability through first 20 games | cases | P(below own plan) | mean full-season avail |
|---|---|---|---|
| <= 50% (<= 10 games) | 79 | 0.76 | 0.38 |
| 50-70% (11-14 games) | 55 | 0.56 | 0.55 |
| 70-85% (15-17 games) | 51 | 0.31 | 0.66 |
| 85%+ (18-20 games) | 137 | 0.24 | 0.80 |

The below-plan probability crosses 0.5 at roughly **70% availability through 20 games, i.e. 14 of 20**. Below that pace, the reference class says a player is more likely than not to finish below his own prior-three-season median.

## Applied to LaMelo, out of sample

LaMelo's prior-three-season games are 22, 47, 72, so his plan (prior-three-season median) is **47 games**, 0.573 of an 82-game season. This is the warehouse-derived baseline, matching the YB3 definition, replacing the three inconsistent hand-set numbers (63, 49, 0.75) documented in the availability reconciliation note.

The wire, derived from the mapping and applied to him out of sample:

> **AVAIL-PACE trips toward ARM-G (guard depth) if LaMelo is available in fewer than 14 of the Wolves' first 20 games (R1, advisory), confirmed at R2.** Below that pace, the reference class of 388 comparable arrivals says he is more likely than not to finish below his own 47-game plan, which is the availability state that makes guard insurance the correct deadline move.

This is a pure reference-class threshold: no fitted model, no distributional assumption, just where 388 historical arrivals at that early pace ended up. It is applied to LaMelo out of sample (he is not in the class; his season is 2026-27).

## Honesty clauses that carry into TRIPWIRES.md

- **Partial exchangeability.** LaMelo's specific profile is only partially exchangeable with the class, which is why the pace is measured against his own prior-three-season median rather than a class average. The threshold is a class-derived prior on his season, not a proof about it.
- **The 2-of-4 selection.** The Scenario B class is players who already had an availability history (missed 2 of 4 prior seasons). LaMelo qualifies (22, 47, 72 is exactly that profile). But the class systematically excludes players whose breakdown was concentrated or post-arrival (Simmons, LaVine), so the mapping describes availability-history players specifically, which is the right class for LaMelo.
- **No private information.** This is games-played pace only. It cannot see a specific injury's timeline, a load-management plan, or medical risk, which is the blind spot a real front office fills.
- **The 63-game analyst prior** is logged as a sensitivity scenario, not the baseline. If LaMelo's true talent-level availability is nearer 63 than 47, the threshold shifts up proportionally; the mapping supports re-running at that plan.

## Status

AVAIL-PACE is **wire-eligible**: >= N_GATE cases (388), sign consistency 0.772 >= SIGN_GATE at N=20, exempt from the reliability gate as an exact count, and it gates a distinct arm (ARM-G). It is the strongest-supported wire in the library and the one with a fully derived threshold.
