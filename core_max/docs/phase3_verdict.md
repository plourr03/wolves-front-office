# Phase 3 verdict: status quo vs Fork B on near-term title odds

Engine: the calibrated `bracket_sim` season+playoff pipeline (spot-checked: OKC the title
favorite, league sums to 100). MIN's strength per scenario is built by per-iteration sampling
(Joan from his Phase-2 comp distribution, NOT his naive +2.29; established from Phase-1a; returns
with real availability/collapse tails), with common random numbers across scenarios so the DELTA
is low-noise. MIN's epistemic strength uncertainty is supplied by the draws (removed from the sim
to avoid double-counting). Returns are the vetted capital-realistic band (plausible sellers only).

## The result (Year 1, 2026-27 title probability)

| cell | status quo | Fork B | delta | 90% CI | P(FB>SQ) |
|---|---|---|---|---|---|
| **central** (Jrue + O'Neale) | 2.46% | 1.31% | **-1.14pp** | [-4.85, +1.15] | 18% |
| conservative (MPJ + relief) | 2.42% | 0.64% | -1.78pp | [-5.66, 0.00] | 4% |
| optimistic* (Cam + DFS, low-prob deals) | 2.46% | 1.47% | -0.99pp | [-4.56, +1.40] | 21% |
| creator only (Jrue + relief wing) | 2.42% | 0.81% | -1.61pp | [-5.30, +0.05] | 6% |
| wing only (MPJ + O'Neale) | 2.46% | 1.07% | -1.39pp | [-5.25, +0.67] | 13% |

Sensitivities around the central case (all move the delta < 0.5pp):
Joan sub-class -1.34 | replacement -0.97/-2.83: -1.10/-1.20 | fit 0/1.5: -1.36/-0.89 | collapse x2 -1.09.

## What it says, plainly

**At realistic returns, Fork B is a near-term title-odds DOWNGRADE in every cell of the sweep,
roughly halving title probability (from ~2.5% to ~1.0-1.3% central).** The delta is negative
across the entire grid (-0.89 to -1.78pp), and Fork B beats status quo in only 4-24% of draws.
The upper CI touches zero only in the best corner (good returns + a favorable Joan develop draw),
so "Fork B roughly matches status quo" is a ~1-in-5 tail, not the expectation.

**It is driven by the Gobert loss, not by any assumption.** Fork B's mean team net is -0.2 to
-1.8 vs status quo's +1.36, because Gobert is genuinely elite (+4.57 even aged) and the Wolves'
thin capital cannot replace him: Joan (year-1 mean ~-0.6) absorbs the 5 spot. Every swept knob
(fit, replacement, Joan full-vs-sub, veteran collapse) moves the verdict < 0.5pp. The verdict is
structural, not a knob set to taste. The decoupled cells confirm the Randle->creator upgrade is
the load-bearing positive piece, but it cannot cover the Gobert hole.

## The honest framing (what this does and does not settle)

This is the NEAR-TERM (Year 1) TITLE-ODDS number only. It deliberately excludes the three things
Fork B actually rests on, and the verdict is the same shape with them folded in:
- 2-year integration: Joan's mean barely rises within the window (cy3 full median -0.5 vs cy2
  -0.6; Gobert barely declines, +4.48), so Year 2 does not flip it.
- Out-year real-option (the surviving pillar): Joan's development mean climbs later (mature p50
  ~0, p90 ~+4), convexity-rewarded, but it is still a bust-dominated distribution and lands
  beyond the 2-year window.
- Cap flexibility: status quo is jammed at the first apron (no full MLE, hard-capped); Fork B
  opens room below the tax. This is real value, but it is an OPTION, not a Year-1 title-odds gain.

So the title-odds case for Fork B does not survive measurement: on the number the project set as
its objective (P(title), near-to-medium term), keeping Gobert is better. Fork B is justifiable
ONLY if the GM weights cap flexibility and multi-year development belief heavily enough to accept
a measured, ~1pp near-term title-odds cost, and the development distribution that belief rests on
is itself sobering (majority bust in the faithful view).

This is the third and biggest thesis pillar to fall to measurement (after the LAFI fit term and
the single-year variance bonus): the core "fit over splash, bet on Joan" move is, on near-term
title odds, a downgrade, because the player it moves (Gobert) is too good and the capital to
replace him is not there. The model refused to confirm the thesis on its own stated terms.
