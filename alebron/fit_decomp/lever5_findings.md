# Lever 5: LaMelo availability. Built 2026-06-26.

Estimand: a DISTRIBUTION of LaMelo's 2026-27 games played, reconciled with the committed
forward prediction 63 [44, 73]. Data: his GP history, the recurrence pattern, comp guards.

## How it was built (auditable: recurrence base rate, NOT anchored to 72)

The distribution is bootstrapped from his SIX-SEASON empirical history (his own record is the
best personal base rate, and it directly samples his recurrence pattern), with small jitter,
clipped to [0, 82]. It is bimodal BY CONSTRUCTION because his history is bimodal. The 72-game
2025-26 rebound is included as ONE of six seasons (it drives the healthy mode and the upper
tail), not used as the anchor. Even the most recency-favorable DEFENSIBLE center is below 63.

His GP: 2020-21 to 2025-26 = 51, 75, 36, 22, 47, 72. Defensible center estimates, all below the
committed 63:
- full-6: mean 50.5, median 49
- last-4: mean 44.2, median 42
- recency-weighted (0.2/0.3/0.5 on the last three): 54.5

## The distribution (RS games played, 2026-27)

| p10 | p25 | median | p75 | p90 | mean |
|---|---|---|---|---|---|
| 23 | 36 | 49 | 71 | 75 | 51 |

Bimodal and wide: P(healthy, >= 70 games) = 28%; P(compromised, <= 50 games) = 53%. The shape
is "either the ankle holds (mode ~72-75) or it does not (mode ~22-47)," which is exactly his
record, not a smooth bell around the rosy number.

## Comp context (directional, not ankle-specific)

High-usage guards/wings with chronic-availability histories show the SAME bimodal pattern and
the same recent center. Last-4-season GP means: Ja Morant 35, John Wall 37, Markelle Fultz 32,
Zion Williamson 48, Kyrie Irving 49. LaMelo's last-4 mean (44) sits squarely in that band. Once
a high-usage guard enters a chronic-availability pattern, the center lands in the 35-50 range,
not the 60s. (Caveat: this comp set is availability-matched, not ankle-specific; directional.)

## Reconciliation with the committed forward prediction 63 [44, 73]

- The committed CENTER (63) is OPTIMISTIC by ~14 games vs the model median (49). Centering near
  63 requires over-weighting the single 72-game season, which this build deliberately did not do.
- The committed FLOOR (44) is too HIGH: P(GP < 44) = 36%. His 22-game and 36-game seasons are in
  living memory (the last four years), and the band's floor priced them out.
- P(GP >= 63) = 33%, P(GP >= 70) = 28%. The committed prediction is roughly the model's ~67th-70th
  percentile, i.e. an optimistic-side outcome, not the central case.
- The committed prediction STAYS LOCKED as a cold prior for grading (not retuned). This lever's
  job is to say, plainly, that it is ABOVE-MODEL: the recurrence-weighted center is ~50, not 63.

## The three pre-registered reads

- Positive read (center low-to-mid 60s): NOT SUPPORTED as the central case. The 72-game rebound is
  one mode (28%), not the center; treating it as the center is the rosy anchor this build avoided.
- Negative read (recurrence centers ~50, below committed): SUPPORTED. Median 49, mean 51.
- Can't-tell read: PARTIAL. The CENTER is callable (~49-51, clearly below 63), so this is not a
  full can't-tell. But the specific OUTCOME is genuinely uncertain: the distribution is bimodal,
  28% healthy vs 53% compromised, so which mode occurs cannot be called. The honest statement is a
  callable-but-low center with a wide, two-humped spread.

## Sample caveats

- N=6 personal seasons; the bootstrap is crude and ILLUSTRATIVE of the shape (bimodal, center ~50,
  wide), not a precise CDF.
- The 2025-26 "healthy" 72 came at his lowest non-rookie minutes (27.5 mpg), i.e. a MANAGED 72.
  Games played and minutes are different questions; a healthy GP mode may still be load-managed.

## Early signal

Games missed in the first 25 (any ankle absence is the red flag), and the pattern: a load-managed
healthy (GP up, minutes capped) vs a true-healthy (GP up, minutes restored) vs an early recurrence.

## Identifiability verdict

CALLABLE (unlike Lever 3): the data supports a center of ~50 games, clearly below the committed
63, with a wide bimodal spread (28% healthy, 53% compromised) and a real sub-40 tail the committed
floor missed. The honest headline: the availability lever leans NEGATIVE relative to the committed
prediction, and it was built from his actual recurrence record, not the comfortable rebound.
