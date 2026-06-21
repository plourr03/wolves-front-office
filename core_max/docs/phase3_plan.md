# Phase 3 plan and PRE-REGISTRATION (the championship-equity engine)

Status: FROZEN (v1.1, 2026-06-21) after sign-off; see "Resolved on sign-off" at the bottom.
This is the last gate before the engine; build order follows. Phase 3 turns the
Phase 1 (established) and Phase 2 (Joan) impact DISTRIBUTIONS into team strength, simulates
the season and playoffs to P(title) for three roster scenarios, and prices the Fork B
decision honestly. The governing rule from every prior phase holds: each number set on its
merits; speculative beliefs are swept open stakes, never gifts the model grants itself.

## Reused, calibrated engine (do not rebuild)

A validated season+playoff->P(title) pipeline already exists and is reused as the compute
core (same hybrid pattern as the CBA engine and build_rapm):
- `offseason/scripts/series_resolver.py` (best-of-7 win prob, logistic calibrated on 435
  playoff series 1997-2025, optional matchup overlay).
- `offseason/scripts/bracket_sim.py` (season sim -> seeding -> bracket -> title odds, with a
  survivorship variance model; anchors to de-vigged preseason boards).
- `offseason/scripts/build_team_ratings.py` (minute-weighted impact rollup), `build_series_calibration.py`.
SPOT-CHECK (like the build_rapm gate): confirm the reused sim reproduces sensible title odds
for the actual recent champion and the known contenders before trusting any scenario delta.

## Decision 1 (RESOLVED): the fit term is a SYMMETRIC, data-bounded, SWEPT assumption

The empirical wall: a league-wide redundancy penalty is not supported, and Sharp LAFI does
not predict playoff outcomes (p=0.758; only C1 ball-stickiness is individually significant,
and the Wolves are not C1-extreme). So LAFI is NOT baked into team strength (that would be
fitting an absent correlation on the one term favoring the thesis). But a pure sum of CURRENT
impacts genuinely misses the un-clogging gain (impacts are estimated on past lineups). So the
fit gain is real-but-unproven and uncertain in size AND direction.

Resolution (the honest test of "fit over splash"):
- The fit effect enters via the existing bounded `marginal_fit` mechanism (build_rotation_model.py,
  bounded [-1.5, +1.5] net), applied SYMMETRICALLY to ALL THREE rosters by composition, NOT as
  a Fork-B-only bonus. Fork B that fills gaps earns a positive nudge; a splash roster that
  stacks ball-dominance earns a negative one (the relocated-LAFI problem, shown honestly);
  status quo gets whatever its shape says. "Fit over splash" then EMERGES from a neutral
  mechanism or admits it was not real.
- BOUND the magnitude FROM THE DATA, not by taste: the largest defensible fit effect is sized
  from where fit is actually detectable (the C1 ball-stickiness effect), translated to
  net-rating units and capped within the marginal_fit bound. CROSS-CHECK against the additive
  model's own residual room (how much the sum-of-impacts actually mis-predicts real team net
  ratings) and use the SMALLER of the two: a fit channel cannot honestly exceed what the
  additive model ever leaves unexplained, and a too-high ceiling quietly hands Fork B more
  fit-channel room than the data supports.
- SWEEP it from zero to that data-bound, and show whether each scenario's verdict depends on
  the unproven fit gain.

## Per-iteration sampling (LOAD-BEARING, locked)

Sample every player's impact from its distribution each Monte Carlo iteration. The load-bearing
extension to the reused sim: Joan is sampled from his REAL non-normal Phase 2 comp distribution
(the bust-mass + development-tail shape), NOT a net plus/minus an sd. That shape is the whole
reason the engine can answer the variance question. Established players sample from Phase 1a;
never collapse to means.

## The convexity check (near-pivotal, measured EARLY, BOTH forms, ACROSS the range)

With the fit term no longer baked in, whether Joan's variance is an asset depends on whether
P(title) is convex where the scenarios actually sit. Two forms, because they answer different
questions and the second keeps the first honest:
- DECISION metric (headline): Joan as a point mass at his distribution's mean vs his full
  distribution, mean held fixed; if full-distribution P(title) > point-mass, his variance is
  an asset. But his distribution is asymmetric (heavy bust mass + thin upside tail), so this
  conflates the curve's curvature with the distribution's shape.
- STRUCTURAL check: a direct curvature probe, P(title) at strength-delta / strength /
  strength+delta. If the decision metric says "variance helps" while the probe says the curve
  is locally CONCAVE, the result is riding on the distribution's shape reaching a high-payoff
  region, not on real convexity, a far more fragile reason to bet, and that must be surfaced.
- ACROSS THE RANGE, not a single point: P(title) vs strength is S-shaped (convex lower-middle,
  concave near the top), and the scenarios plus sweeps move the Wolves across a real chunk of
  it. A strong-enough Fork B could be pushed into the concave region where variance stops
  helping. Report the curve across the strength range the scenarios span; "is variance an
  asset" has an answer per location, not one answer. Measure this EARLY; it could be the hinge.

### Convexity RESULT (measured 2026-06-21, return-agnostic)

P(title) is globally convex/accelerating across the Wolves' range (increments rise from ~0.1pp
near net 0 to ~1pp near net +5). BUT Joan's variance contribution to title odds is NEGLIGIBLE
EVERYWHERE (~0.00pp at net +1.36 and +3.0; the small negative at +4.5 is sim noise, since the
curve is globally convex). Reason: one ~30-mpg young player moves team net by only ~+/-0.3,
against a MIN distribution already ~1.8 wide, so the marginal Jensen gain is trivial. So spec
Section 7.4's "variance is a tail asset" pillar is TESTED AND DOES NOT SURVIVE at the Wolves'
operating point. This is the second thesis pillar to fall to measurement (after the LAFI fit
term); the final readout names both, so what held and what fell is on the page.

CRITICAL distinction (do not over-extend the null): what died is the single-year VARIANCE
bonus. Joan's DEVELOPMENT real-option is a separate MEAN effect (his expected impact rises over
the out-years; Phase 2 had mature washout ~55% vs 64% year-1, with a higher tail), and a rising
mean is a straight strength gain that the confirmed convexity rewards SUPER-LINEARLY. So the
real-options Gobert term SURVIVES AT FULL WEIGHT; convexity is good news for it. Variance bonus
dead; mean development alive.

## The honest recentering of Fork B (make fragility visible)

The LAFI null demotes the offense-architecture argument from established premise to
plausible-but-unproven assumption. Phase 3 must let this show. The recentering:
- Fork B rests PRIMARILY on the ADDITIVE merits of the returns plus cap flexibility: replacing
  Gobert and Randle with two better-fitting returns and keeping Ayo may be a better roster on
  pure additive impact BEFORE any speculative gain. Joan's downside is a genuine cost; the
  returns are a genuine upgrade.
- The SWUNG UPSIDE (separating "marginally better" from "clearly better") is, AFTER the
  convexity result: Joan's DEVELOPMENT real-option (his MEAN rising over the out-years,
  convexity-rewarded; alive at full weight) plus the SWEPT fit gain (unproven, 0-to-bound). The
  single-year variance bonus is NOT in this list anymore (it tested negligible). Joan's
  near-term (year-1) mean is a real, sobering COST that improves over the window. If Fork B's
  verdict leans heavily on the unproven pieces (the swept fit gain, the development option),
  that fragility must be reported, not hidden.

## Full sweep set (sweep, do not pick; show the verdict's range)

- RETURN QUALITY (the single biggest driver, added): Fork B is recentered on the returns'
  additive merit, so the assumed quality of the two returns is the most important number in the
  comparison, more than the fit bound or the replacement floor. Sweep a conservative-to-
  optimistic, CAPITAL-REALISTIC band (see below). If Fork B only wins with optimistic returns,
  that is the HEADLINE finding, not a footnote.
- replacement bracket [-0.97, -2.83]; full-vs-faithful-sub-class; established-SD variants
  (as-is / shrink / hetero-widen); the SYMMETRIC fit-bonus sweep (0 to data-bound).
- VETERAN-COLLAPSE hazard MAGNITUDE as a swept sensitivity (not a single base-rate point;
  symmetric with sweeping Joan's bust floor): centered on the real age+injury base rate,
  modeled as a mixture not a wider SD, with the verdict's sensitivity shown (too-low flatters
  status quo, too-high flatters Fork B).
- Plus the real-options Gobert term (out-year development upside) and the convexity check.

PRIMARY VERDICT = the Fork-B-minus-status-quo DELTA in title equity (absolute P(title)
secondary): the delta cancels the shared league-context and engine-calibration assumptions and
is far more robust than either absolute number. Report the delta as a distribution across the
full sweep grid.

## Returns as a capital-realistic BAND (not a wish-list slate)

The scenarios currently carry salary-matched placeholders. The returns are NOT specified as a
single slate of preferred players (that is the wish-list thumb). Instead, propose a realistic
return BAND grounded in what Gobert + Randle + No. 28 actually command, vetted together, then
swept (this IS the return-quality dimension). HARD realism constraint: any return that would
require draft capital we do not have (2032 frozen, 2034 at risk, only ~No. 28 cleanly
tradeable) is OUT OF BOUNDS, because premium talent cannot be landed without premium
sweeteners. The returns enter as an honest range, not an optimistic guess.

## Pre-registration items (frozen on sign-off)

- The symmetric fit mechanism + the C1-derived data bound + the 0-to-bound sweep.
- The convexity test (point-mass-at-mean vs full-distribution, mean held fixed), measured early.
- The sweep grid above; verdict reported across it (Fork B on additive merits alone, then with
  each swept upside).
- The veteran-collapse hazard, base-rate calibrated, swept.
- Joan sampled from the non-normal comp distribution; established from 1a; per-iteration.
- The sim reused + spot-checked (recent champion + contenders reproduce sensible odds).

## Resolved on sign-off (2026-06-21)

- Fit bound: C1 ball-stickiness anchor, cross-checked against the additive residual room, use
  the smaller. Swept 0-to-bound, symmetric across all three rosters.
- Convexity: both forms (distribution test = headline decision metric; curvature probe =
  structural check), measured ACROSS the strength range the scenarios span, early.
- Sweep grid: added the return-quality sweep (capital-realistic band) and the veteran-collapse
  hazard-magnitude sweep; primary verdict is the Fork-B-minus-status-quo DELTA.
- Build order: build + spot-check the engine on status quo; propose a capital-realistic return
  band to vet together; then run the comparison across the full grid.
