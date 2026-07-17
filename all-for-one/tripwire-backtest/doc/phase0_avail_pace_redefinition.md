# Phase 0: AVAIL-PACE Redefinition and Availability-Posterior Build Spec

Tripwire backtest, Phase 0 Step 4b and 4c. Produced 2026-07-17.

## The problem this fixes

The spec (section 5, section 7, section 8) defines AVAIL-PACE as LaMelo's games-played through team game N "expressed as a percentile of the pick2033 pre-season availability posterior," and its section 7 query reads from tables `availability_posterior` and `availability_posterior_draws`.

**Those tables do not exist, and the model behind them was never built.** pick2033 prices draft-pick lottery slots, not player availability; the name collision is total. A repo-wide search for `availability_posterior` returns exactly one hit, line 210 of the spec itself. The AVAIL-PACE query, as written, has no source. See the gap register and the availability reconciliation note for the full trace.

The spec's section 8 leans on this hardest: it justifies AVAIL-PACE specifically on the grounds that it runs "against his individually fitted posterior rather than a class average." That sentence describes an artifact that does not exist.

## The redefinition (4b)

AVAIL-PACE is redefined to run on the warehouse and the reference class, with no fitted posterior on the critical path. This is Bobby's direction (2026-07-17), sharpened from the original spec, and it is stronger than the original, not a fallback.

**Baseline (the "plan" the pace is measured against):** the arriving player's **prior-three-season regular-season games-played median**, computed from `nba_player_stats` joined to `nba_games`. This is deliberately identical to the spec's existing YB3 definition ("plan defined per case as prior three-season median games"). So the wire and the Scenario B label it feeds share one definition instead of carrying two subtly different notions of "the plan." For LaMelo the three prior seasons (2023-24, 2024-25, 2025-26 = 22, 47, 72) give a median of **47**.

**The pace metric itself:** games played through team game N (exact count, no sampling noise; this is why the spec calls it exempt from the reliability gate), expressed relative to the baseline.

**Where the threshold comes from:** the Scenario B reference class, in Phase 3, produces the empirical mapping from `pace-at-game-N versus prior-median` to `end-of-season availability` and `playoff availability`. The wire's trip threshold falls out of that mapping, applied to LaMelo **out of sample**. There is no fitted model to defend and no distributional assumption to justify. It is a pure reference-class argument: history says players arriving at this pace relative to their own prior median ended their seasons like so, and here is where LaMelo sits against that history.

**Why this is stronger than the spec's version.** Three reasons, all worth putting in TRIPWIRES.md:
1. It removes a circularity. Gating a February decision on a posterior fitted by the same shop making the decision invites the fit to drift toward the answer the shop wants. A reference-class mapping computed before the season, from other teams' histories, cannot.
2. It has no modeling assumptions to attack. A front office asking "why this number" gets a scorecard of comparable arrivals, not a prior specification.
3. It shares a definition with its own outcome label, so the wire and the thing it predicts cannot silently diverge.

**The 63-game analyst prior becomes a sensitivity scenario, not the baseline.** It is a logged bet (see the reconciliation note), useful for showing how the wire reads if you believe the optimistic case, but it is not the plan the pace is measured against. The 49 model median and the 0.75 survival scalar do not enter the wire at all.

**Spec amendments this forces:**

| Spec location | Change |
|---|---|
| Section 5, AVAIL-PACE row | "percentile of the pick2033 pre-season availability posterior" becomes "games-played pace vs prior-three-season median, thresholded on the Scenario B empirical mapping." |
| Section 7, AVAIL-PACE query | Delete the `availability_posterior` / `availability_posterior_draws` query. Replace with the games-played-through-N count and the prior-median baseline, both warehouse-derived. |
| Section 8, honesty clause | Rewrite the sentence justifying AVAIL-PACE on "his individually fitted posterior." The honest justification is the opposite: it runs on a reference-class mapping precisely because his individual posterior does not exist and, for a pre-committed decision, should not be the thing on the critical path. |

Phase 0 records this redefinition. It does not run the Phase 3 mapping; that is Phase 3.

## Build spec for a real per-player availability posterior (4c)

A real per-player games-played posterior is still worth building. Its customer is the **master plan board**, not this backtest. The board's availability state transitions (the `melo_avail` node in the board design) need a distribution over LaMelo's season, not a single pace reading against a reference class. Scheduling it against the board takes it off the tripwire critical path entirely, which is the point: the February wire ships on the reference-class mapping, and the board consumes the posterior when the board is built.

This is a one-page scope, not an implementation.

**Object:** a posterior distribution over a player's regular-season games played, and over playoff availability, conditioned on pre-season information, with draws at each `through_game = N` so it can be read at R1 and R2.

**Inputs, all warehouse-resident:**
- Per-season games-played history (`nba_player_stats` + `nba_games`), full career.
- Age and position (`nba_player_bio`, `nba_player_season_bio`).
- Prior-injury structure to the extent it is inferable from games-missed patterns. The warehouse has no medical data, which is the honest ceiling on this model and must be stated as such (the spec's section 8 blind-spot clause applies directly).

**Structure:** a hierarchical model, players nested in an availability-archetype prior, shrinking each player toward players with similar age and games-missed history. This is the same shrinkage philosophy fitengine already uses for RAPM (two-stage, shrink toward a learned prior), so the house has a pattern to reuse, though the target quantity (a games-played count, likely a Beta-Binomial or a hurdle model for the zero-inflation of chronic-injury seasons) is different enough that the fitengine RAPM code is a reference, not a drop-in.

**Outputs:** `q10/q50/q90` and full draws per `through_game`, keyed by `player_id`. This is the interface the original spec's section 7 query assumed; if it is ever built, the original AVAIL-PACE query would run against it unchanged, so the redefinition above is forward-compatible.

**Effort estimate:** a genuine hierarchical availability model with archetype pooling, honest zero-inflation handling, and a backtest against held-out player-seasons is **roughly one to two weeks** of modeling work, dominated by the archetype definition and the validation, not the fit. It is a real project, comparable in size to fitengine's F2, and it should get a spec and a gate structure of its own on the board's roadmap.

**Why not now:** the February 2027 wire does not need it, the reference-class mapping is more defensible in print for a pre-committed decision, and putting a one-to-two-week model on the tripwire critical path would delay the October freeze for no gain to the wire. Build it when the board needs it.

## One-line summary

The wire ships on a reference-class mapping (buildable now, more defensible for a pre-commitment). The posterior is a real project (one to two weeks) scheduled against the board, which is its actual customer. Neither depends on the pick2033 name collision, which is retired from the AVAIL-PACE definition entirely.
