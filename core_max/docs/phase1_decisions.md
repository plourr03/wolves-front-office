# Phase 1 Decisions (locked)

Phase 1 = established-player impact baseline + the box-to-RAPM correction that the
Phase 2 young-player bridge will reuse. Decisions resolved with the user; both
option 1, each with refinements that are binding, not optional.

## The meta-point that governs the spirit of Phase 1

These two knobs mostly affect how much credit and uncertainty the VETERAN-heavy
rosters (splash, status_quo) receive. Fork B's upside comes from the Phase 2
young-player module, not from here. So getting Phase 1 right is about keeping the
comparison FAIR to the alternatives, not about boosting Fork B. Doing it
rigorously protects the alternatives' tails, not ours. If anything, sloppiness
here would flatter Fork B by under-crediting the veteran rosters.

## Overarching guardrail (governs both decisions)

Every choice below is a knob that could be tuned to flatter the thesis. Two rules:
1. Calibrate each against HELD-OUT reality, never in-sample "looks reasonable."
2. Report what each choice does to the Fork-B-minus-splash title-equity gap. If
   widening established SDs or applying the rim correction noticeably moves that
   gap, surface it and understand why, rather than discover later that an
   uncertainty assumption was carrying the verdict. (The full title gap needs the
   Monte Carlo engine, so in Phase 1 we report each knob's effect on the
   team-strength DISTRIBUTIONS for the three rosters; the knobs then become config
   variants the Phase 3-4 harness sweeps for the actual title-gap sensitivity.)

## Q1. Established-player uncertainty: calibrate/inflate the analytic SDs

The analytic ridge posterior SDs capture sampling variation in the coefficients
and nothing else (blind to role, lineup, opponent, and the RS-to-PO regime
change). Using them as-is is disqualifying for a tail-event model: it compresses
every team-strength distribution and understates the exact variance we price.
Bootstrap is the right eventual answer but premature before we know uncertainty
calibration is the binding constraint.

Refinements (binding):
1. **Heteroscedastic, per-player inflation, NOT a global multiplier.** Drive the
   widening per-player off the already-player-specific columns (RAPM-vs-BBR
   divergence and the RS-to-PO translation delta). A flat multiplier re-flattens
   the relative uncertainty structure that matters (a stable star and a
   role-dependent specialist must not get the same widening). The RS-to-PO delta
   is the single most title-relevant uncertainty source, so it carries weight.
2. **"Validated" = a COVERAGE check against held-out realized outcomes.** Predict
   held-out impact with the inflated SD and check whether the 80% intervals
   actually contain 80% of outcomes. If they contain 60%, still overconfident,
   factor goes up. This coverage test is the only thing between "calibrated
   inflation" and "a knob tuned until the picture felt right."

## Q2. Box-to-RAPM correction: condition on a measured rim-protection signal

The data settles it: the bias tracks MEASURED rim-protection impact, not the
position label (Gobert/Wemby underrated by 4-5 pts; nominal center Claxton
over-rated). Crude position group fails. The learned-residual model is better at
catching box-BPM's other biases (over-credits high-usage scorers, under-credits
connective low-usage guys) but has more overfit capacity and is harder to audit,
so it is deferred to Phase 2 once the simple version is validated.

Refinements (binding):
1. **For young / prior-dominated players the conditioning signal must be
   box-computable and stable in small samples, NEVER def_rapm.** Joan is
   prior-dominated precisely because his RAPM is junk from limited minutes; if the
   rim correction depends on def_rapm we reintroduce the exact circularity we are
   escaping for the one player it most needs to work on. Stated rule: the
   correction for Joan runs on his measurable rim stats (block rate, rim
   deterrence, opponent FG% at the rim, contest rate), never on his nonexistent
   reliable def_rapm. (Established players with a reliable def_rapm may use it; the
   RULE binds for the prior-dominated.)
2. **Validate leave-one-out or on a temporal holdout, never in-sample.** In-sample
   it always looks like it fits. The real test: does it pull Gobert and Wemby up
   and Claxton down on HELD-OUT players without overcorrecting the mid-pack?

## Data dependencies: CONFIRMED (grounded 2026-06-20)

- **Rim signals (Q2.1): available.** `nba_player_tracking_season` (measure_type
  'Defense', warehouse, reachable over Tailscale at POSTGRES_HOST 100.69.186.94)
  has `def_rim_fg_pct`, `def_rim_fga` (rim contest volume), `blk` per
  player-season, 2013-14 to 2025-26, RS+PO. Joan (player_id 1642866) is present:
  2025-26 rookie line is def_rim_fg_pct 0.514 on 105 contests, 26 blocks, 40 GP,
  better rim FG% allowed than Gobert (0.542) on a smaller-but-usable sample. The
  signal that keeps Joan from being buried exists and is box-computable.
- **Held-out RAPM (Q1.2 / Q2.2): feasible, fully local.** 3,939 per-game
  possession parquet files in `offseason/data/cache/possessions_league/`,
  season-labeled (2023-24, 2024-25, 2025-26, RS+PO). A true temporal holdout (fit
  on 2023-24 + 2024-25, check coverage on held-out 2025-26) is buildable with no
  warehouse. `rs_to_po_delta` (Synergy PPP space) is a held-out REGIME covariate
  for the inflation, NOT the coverage target; the coverage target is held-out RAPM.

## Held-out RAPM production (the one open sub-decision)

The coverage check must validate the SAME estimator that produced
`player_value.csv` (recency weights, garbage-time filter, box-score prior), or it
validates the wrong thing. So reuse `build_rapm.py`'s exact logic via a core_max
adapter (same hybrid pattern as the CBA gate), reading the shared parquet cache.
RESOLVED: option 1 (offseason refactor exposing a windowed fit). Three binding
refinements from the user:

1. BEHAVIOR-PRESERVING REFACTOR AS A HARD GATE. Parameterizing the fit by season
   window risks silently changing the estimator (box-prior strength tuned for
   3-season volume, recency-weight renormalization, garbage-time interactions). The
   refactor must be a pure extraction, and PROVEN: run the windowed callable on the
   FULL window and diff against the committed player_value.csv RAPM columns.
   Reproduce to the decimal => behavior preserved, 1c trustworthy. Mismatch => a bug
   (or input drift) caught before it poisons the calibration. This diff is a REQUIRED
   gate on the refactor, not an afterthought.
2. NOISY-TARGET CORRECTION IN 1c COVERAGE. The held-out 2025-26 RAPM is itself a
   noisy estimate, not ground truth. Scoring coverage as "did my interval contain the
   held-out POINT estimate" without the target's own SD systematically OVER-inflates
   (some misses are target noise, not prediction error). Fold the held-out estimate's
   SD into the coverage scoring (overlapping-interval coverage, or net out target
   variance). Direction matters: sloppiness pushes inflation too high, fattening every
   tail and flattering "variance is an asset", so it is an honesty check that cuts
   AGAINST the thesis.
3. VETERAN ASSUMPTIONS STOP AT THE PHASE 2 BOUNDARY. The deterministic age-curve drift
   (1a) and the coverage factor calibrated on the durable survivor population (1c) are
   fine for established players but must NOT leak into Phase 2's young-player module,
   where drift uncertainty is first-order and the survivor population is the wrong
   reference class for a prior-dominated rookie. Keep a clean wall between Phase 1's
   veteran assumptions and Phase 2's Joan distribution.
