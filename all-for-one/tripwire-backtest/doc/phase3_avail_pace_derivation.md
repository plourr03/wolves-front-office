# AVAIL-PACE Derivation Memo

Tripwire backtest. Required before any TRIPWIRES.md entry, per Bobby's directive 2026-07-17. Produced 2026-07-17. Data: `data/avail_pace_derivation.parquet`. Script: `avail_pace_derivation.py`. **Supersedes the single 14-of-20 number in `phase3_avail_pace.md`** (see "Correction" below).

## The epistemic question, answered

**Is the trip an absolute-count breakpoint, or LaMelo's baseline-conditioned instantiation of a relative mapping?** It is the latter. The redefined wire measures games-played pace against the player's own prior-three-season median, so the mapping is relative: the predictor is `early_rel = (avail_N / N) / (plan / sched)`, early availability expressed as a multiple of the player's own plan pace. `early_rel = 1.0` means pacing exactly at plan.

The class's below-plan probability crosses 0.5 at `early_rel ≈ 1.0` on the full class and `≈ 1.10` on the injury-history subset (a player pacing at or just below his own plan is more likely than not to finish below it). That crossing is **baseline-agnostic** as a ratio. LaMelo's baseline (plan = 47) enters only when the ratio is translated into a count, and because his plan is low, his count breakpoint is lower than the class-typical player's.

This is why the absolute-count framing misleads: **14 of 20 is the class-average absolute breakpoint, but LaMelo's 47-game plan makes his correct R1 trip ~12 of 20, not 14.** Applying the class-average absolute count to a low-availability player would over-trigger the wire.

## The wire (baseline-conditioned, injury-history subset)

Using the injury-history subset threshold (`early_rel = 1.10`, the more LaMelo-applicable and slightly more conservative of the two):

| Read | N | Trip condition (plan = 47) |
|---|---|---|
| **R1 (advisory)** | 20 | LaMelo available in **12 or fewer** of the Wolves' first 20 games |
| **R2 (binding)** | 37 | LaMelo available in **23 or fewer** of the first 37 games |

Derivation: R1 trip fraction = 1.10 x (47/82) = 0.630, so avail < 0.630 x 20 = 12.6 → 12 or fewer. R2 trip fraction = 0.630, avail < 0.630 x 37 = 23.3 → 23 or fewer. This wire is one the spec allows to hard-trip at R2 alone (an exact count, no sampling noise), so R2 carries its own number rather than merely confirming R1.

## Scorecard: outcomes above vs below the line

Relative mapping at R1 (N=20), full Scenario B:

| early_rel bucket | n | P(below plan) | median season games | share under 55 | playoff availability |
|---|---|---|---|---|---|
| 0.0-0.6 (well below plan pace) | 46 | 0.89 | 21.5 | 0.96 | 0.26 |
| 0.6-0.85 | 35 | 0.86 | 41.0 | 0.86 | 0.43 |
| 0.85-1.05 (at plan) | 35 | 0.51 | 47.0 | 0.54 | 0.33 |
| 1.05-1.3 | 73 | 0.38 | 62.0 | 0.32 | 0.79 |
| 1.3+ (well above plan pace) | 132 | 0.17 | 62.0 | 0.38 | 0.66 |

A player pacing below his plan early (early_rel < 0.85) finishes with a median of 21-41 games, lands under the 55-game contention bar 86-96% of the time, and is available for a quarter to two-fifths of his team's playoff games. A player pacing above plan finishes at a median of 62 games, clears 55 two-thirds of the time, and is available for two-thirds to four-fifths of the playoffs. The line separates cleanly on every outcome dimension Bobby named.

At R2 (N=37) the separation sharpens (below-0.6 bucket: median 15 games, 100% under 55, 0.23 playoff availability), which is why R2 is the binding read.

## Absolute-count view, for the record

The absolute breakpoint on raw early fraction (not baseline-conditioned), R1:

| avail through 20 | n | P(below plan) | median games | under 55 |
|---|---|---|---|---|
| <= 10 | 79 | 0.76 | 30 | 0.92 |
| 11-14 | 55 | 0.56 | 45 | 0.67 |
| 15-17 | 51 | 0.31 | 52 | 0.53 |
| 18-20 | 137 | 0.24 | 67 | 0.21 |

The absolute crossing is ~14 of 20. This is the class breakpoint for a typical-plan player. It is reported for transparency but is **not** the wire; the wire is baseline-conditioned to LaMelo's 47-game plan, which lowers his count to 12.

## 63-game analyst-prior sensitivity

If LaMelo's true availability plan is nearer the 63-game analyst prior than his 47-game history median (the sensitivity scenario from the redefinition doc, logged not baselined):

| Read | Trip condition (plan = 63) |
|---|---|
| R1 | available in **15 or fewer** of first 20 |
| R2 | available in **31 or fewer** of first 37 |

A higher plan demands more early availability to stay "on plan," so the trip count rises. The wire should be stated at the 47-game baseline with this 63-game read logged, so a mid-season revision to his expected availability has a pre-computed threshold.

## Injury-history subset vs full class

LaMelo's applicability argument runs through the injury-history subset (players who, like him, had a prior season missing >= 50% of games; his 22-game 2023-24 qualifies). Both are reported:

| Class | n | Spearman(early_rel, full_gp) | threshold_rel | LaMelo R1 trip (plan 47) |
|---|---|---|---|---|
| Full Scenario B | 377 | 0.636 | 1.00 | avail < 11.5 of 20 |
| Injury-history subset | 253 | 0.631 | 1.10 | avail < 12.6 of 20 |

The subset and the full class agree closely (Spearman 0.63 both; threshold 1.00 vs 1.10). The wire uses the subset's slightly more conservative 1.10, giving 12 of 20, because it is the class LaMelo actually belongs to. That the two agree is the evidence that the mapping is not an artifact of the broader class's healthier players.

Note the relative-mapping Spearman (0.636) is lower than the raw-count Spearman (0.769 in `phase3_avail_pace.md`) because dividing by plan injects the plan estimate's noise. The raw count is the metric's raw predictive strength; the relative mapping is how the baseline-conditioned threshold is set. Both are real and both belong in the record.

## Correction to phase3_avail_pace.md

That deliverable stated the wire as "fewer than 14 of the first 20 games." That was the absolute class breakpoint, not the baseline-conditioned LaMelo number. **The corrected wire is 12 or fewer of 20 at R1, 23 or fewer of 37 at R2**, both at the 47-game plan, with the 63-game reads logged as sensitivity. The predictive-validity result in that doc (Spearman 0.77 raw, sign consistency 0.77, wire-eligible) is unchanged; only the threshold count is corrected here.

## For TRIPWIRES.md

> **AVAIL-PACE.** Trip toward ARM-G (guard depth) if LaMelo Ball is available in 12 or fewer of the Wolves' first 20 games at R1 (2026-11-27, advisory) and 23 or fewer of the first 37 at R2 (2027-01-10, binding). Baseline-conditioned on his 47-game prior-three-season median; at a 63-game plan the reads are 15 and 31. Derived from 388 (253 injury-history) comparable arrivals; no fitted model. Exact count, may hard-trip at R2.
