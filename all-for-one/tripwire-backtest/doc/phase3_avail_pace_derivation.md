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

## The cushion effect: the wire stands down only if he outperforms his own history

Bobby's reading (2026-07-17), tested against the data and **confirmed**: both trip lines sit at or above LaMelo's on-plan pace, so the wire trips unless he beats his own history early.

**The trip lines are above plan pace.** LaMelo's 47-game plan is 0.573 of the season, which is 11.5 games through 20 and 21.2 through 37. The trip lines are 12 and 23. So the R1 line sits +0.5 above plan pace and the R2 line +1.8 above. To stand the wire down he must be available in **at least 13 of 20** (0.65, about 13% above his own plan pace) and **at least 24 of 37**. Merely pacing at his plan is not enough to stand it down.

**Two reasons, both empirical.**

(a) **The 47-game baseline itself sits inside arm territory.** Players pacing at plan early (early_rel 0.9-1.1) finish under the 55-game contention bar 46% of the time at R1 and 59% at R2, and are available for only 41% (R1) / 53% (R2) of their team's playoff games. So even if LaMelo merely hits his 47-game history, his stretch-run and playoff availability is a coin flip at best, which is exactly the state ARM-G (guard depth) insures against. The baseline is not a safe outcome; it is already a concerning one.

(b) **Early pace overstates final availability.** Across the class, early availability runs a median 6% higher than final (R1: mean +0.044, median +0.061 of season; R2: +0.029). Concretely, of players who paced at LaMelo's plan pace early, **62% (R1) and 75% (R2) still finished below their plan**. Availability erodes over a season for injury-prone players, so landing a plan requires running ahead of it by midseason. The cushion in the trip line (+0.5 at R1, +1.8 at R2) is the wire encoding that erosion.

**Scorecard above vs below each trip line:**

| | n | P(below plan) | median season games | share under 55 | playoff availability |
|---|---|---|---|---|---|
| **R1** below/at 12 (fires) | 166 | 0.77 | 26 | 0.91 | 0.30 |
| **R1** above 12 (stands down) | 211 | 0.28 | 62 | 0.33 | 0.72 |
| **R2** below/at 23 (fires) | 151 | 0.80 | 23 | 0.95 | 0.27 |
| **R2** above 23 (stands down) | 168 | 0.24 | 64 | 0.27 | 0.70 |

A LaMelo who trips the wire looks like the top rows: a median 23-26 game season, under the contention bar ~90-95% of the time, available for barely a quarter of the playoffs. A LaMelo who clears it looks like the bottom rows: a median 62-64 games, clears 55 two-thirds of the time, available for ~70% of the playoffs. The wire is not splitting hairs; it is separating a lost season from a healthy one.

**The memo does not differ from Bobby's reading; it confirms it.** The one nuance worth stating plainly: the absolute cushion is small (half a game at R1, under two at R2), because LaMelo's plan pace already sits just below the class's below-plan crossing. The wire is not demanding heroics, it is demanding that he clear his own low bar with a small margin, and the data says even that margin matters because early availability flatters the final number.

## For TRIPWIRES.md

> **AVAIL-PACE.** Trip toward ARM-G (guard depth) if LaMelo Ball is available in 12 or fewer of the Wolves' first 20 games at R1 (2026-11-27, advisory) and 23 or fewer of the first 37 at R2 (2027-01-10, binding). These lines sit just above his 47-game-baseline plan pace (11.5 of 20, 21.2 of 37), so the wire stands down only if he is available at **at least 13 of 20 and 24 of 37, i.e. only if he outperforms his own three-season history** by a small margin. This is deliberate: at his 47-game baseline he is under the 55-game contention bar about half the time and available for under half the playoffs, and early availability overstates the final number by ~6%, so hitting the plan requires pacing ahead of it. Baseline-conditioned on his prior-three-season median; at a 63-game plan the reads are 15 and 31. Derived from 388 (253 injury-history) comparable arrivals; no fitted model. Exact count, may hard-trip at R2.
