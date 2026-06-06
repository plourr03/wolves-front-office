# Q0A LAFI: Starting Priors

**Date:** 2026-05-16
**Status:** Pre-build. Written before any component computation.

## The thesis we're testing

The 2025-26 Minnesota Timberwolves play offense that resembles pickup basketball at LA Fitness: ball-dominant, motionless, devoid of designed structure. The LA Fitness Index (LAFI) is a 0-100 composite that places every team-season on a pickup-vs-designed spectrum. The thesis predicts the 2025-26 Wolves rank in the top 3-5 league-wide, and that LAFI predicts playoff underperformance after controlling for regular-season strength.

The "LA Fitness" framing was coined by Scott (Bobby's brother-in-law) after watching the Wolves and texting that the offense "looks like pickup at LA Fitness." The project is built on the idea that this feeling is structurally real and measurable.

## What we expected for the Wolves on each component

Predictions stated before any computation, so we can score calibration later.

**Component 1: Ball Stickiness (25% weight).** Wolves rank top 5. They became more sticky after the KAT-to-Randle swap, because Randle's offensive game is more iso/post oriented and the system contracted around individual strengths. Expected trajectory: low in 2023-24 (WCF year, KAT gravity), rising in 2024-25 and 2025-26.

**Component 2: Movement Death (20% weight).** Wolves should rise meaningfully from 2023-24 to 2025-26. "No off-ball motion" is one of the strongest pieces of the LA-Fitness perception.

**Component 3: Isolation Reliance (20% weight).** Wolves should be elevated in 2024-25 and 2025-26, possibly higher in 25-26 if iso load spread across more players.

**Component 4: Action Poverty (20% weight).** This is the component the user expects to spike hardest. The "they only run two things" intuition is the strongest piece of the LA-Fitness perception.

**Component 5: Shot Quality Decay (15% weight).** Should be elevated but moderately. Late-clock shots are the symptom, not the cause.

## What we expected for the league

Expected high pickup-side: heavy iso teams. Hawks with Trae, Mavs with Luka, Knicks with Brunson, the Wolves per thesis.

Expected low pickup-side (designed): Warriors (Steph era), Celtics (motion), Pacers (Carlisle), Thunder (post-2023), Nuggets (Jokic system).

## What we expected from the predictive validation

Per spec section 4.1, the headline regression hypothesis: LAFI has a significant negative coefficient on playoff overperformance after controlling for regular season SRS. The interpretation thresholds:

- Coefficient of -0.05 wins per LAFI point: weakly suggestive
- Coefficient of -0.10 wins per LAFI point: meaningful, publishable
- Coefficient of -0.15+ wins per LAFI point: a genuine finding worth front-office attention

## What could go wrong

Documented in spec section 8:

1. LAFI correlates too tightly with usage rate of the star, in which case it's just inverted ball movement.
2. The action classifier proves too hard, making Component 4 v1 weaker than hoped.
3. The predictive relationship is real but small (3-5% of variance).

## Methodology constraints set before building

- Validation sample defaults to exclude 2019-20 and 2020-21 (COVID-disrupted), with robustness checks including them.
- Run both the 5-component canonical LAFI and a 4-component robustness variant (dropping Shot Quality Decay, which has a tighter usable window 2018-19 onward).
- Z-score sub-metrics within season, not pooled, to control for era drift.
- Equal weighting of sub-metrics within each component (no thumb on scale).
- Component weights fixed at the spec priors (25/20/20/20/15); empirical re-tuning is a robustness check after validation, not the default.

## Standing principle

Let the data lead. If an eye-test fails, the first move is to check whether the prior is outdated, not to re-spec the metric. Only after the data has been verified do we consider methodology changes.
