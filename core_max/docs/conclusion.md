# Core Maximization: conclusion (front-office deliverable)

The project set out to test a thesis: maximize the core by betting on Joan (Fork B), trading
Gobert and Randle for fit. The honest engine, built to be able to say no, said no, and then
mapped what to do instead. This is the captured result.

## The frontier (near-term, Year-1 title odds, vs ~2.46% stand-pat)

| move | title | vs stand-pat | asset cost | CBA |
|---|---|---|---|---|
| stand pat + develop (Ayo only) | 2.46% | - | none | PASS |
| stand pat + taxpayer-MLE shooter | 2.69% | +0.24 | MLE $ only | PASS |
| retool Randle+DDV -> Jrue (attainable) | 3.05% | +0.60 | Randle + DDV + pick | PASS |
| retool Randle -> Cam (best fit, shaky seller) | 3.24% | +0.79 | Randle + pick | PASS |
| **retool Randle -> Cam + full-MLE shooter (ceiling, combined-modeled)** | **~3.2%** | **+0.77** | Randle + pick + MLE $ | PASS |
| retool Randle+DDV -> MPJ (available, flat) | 2.68% | +0.23 | Randle + DDV + pick | PASS |
| Fork B (Gobert + Randle out) [contrast] | 1.30% | -1.15 | Gobert + Randle + pick | PASS |

CORRECTION (2026-06-22): an earlier version of this table listed the ceiling cell at 3.69%
(+1.24), which ADDED the MLE shooter's value as a flat bonus ON TOP OF the Cam retool. The
combined-roster model (run_package.py, package C: the shooter modeled IN the rotation) shows the
shooter adds ~0 once a creator has already un-clogged the offense, so the honest ceiling is ~3.2%
(+0.77), not 3.69%. The combined-roster PACKAGE table (phase3_packages.md) is canonical; this
frontier is a first-pass and its stacked-MLE cell was additivity-inflated. The correction tightens
the conclusion (the ceiling is lower than first published).

## What it concludes

1. **The Wolves are asset-constrained into the mid-tier for this window.** Every
   capital-realistic move lands in a ~2.5-3.2% title band. Nothing buys contention (5%+). The
   pattern across the whole project (Fork B negative, best retool under +1.3pp) is the finding,
   not a series of wrong picks: no single move materially moves the needle, because the team is
   a real-but-mid contender and the capital is thin.

2. **The best feasible near-term move is the opposite shape from the thesis.** Keep Gobert (the
   elite defense is the team's real edge and is irreplaceable with this capital), retool the
   Randle slot with a creator/shooter (opens cap room AND un-clogs the offense, the actual LAFI
   fix), and develop Joan behind Gobert. That is the ceiling, ~+0.8pp to ~3.2%. The spec
   correctly diagnosed the offense and bet on moving the wrong big.

3. **RECOMMENDED BUILD: package A, Randle (+ DiVincenzo) -> Jrue Holiday + a shooter + re-sign Ayo
   + the No. 28 developmental pick (3.01%, +0.60).** This is the executable, NO-ASTERISK pick: it
   needs no third team, depends on no shaky seller, fills the actual hole (lead-guard playmaking,
   made acute by DiVincenzo's torn Achilles), reinforces the Gobert/McDaniels defensive identity,
   and shedding Randle is what unlocks the full MLE. Cam Johnson's package C is marginally higher
   ON PAPER (3.19%, +0.77) but the gap is ~0.18pp (a rounding error) and it needs a third team to
   take Randle plus a shaky seller in Denver, so it does not survive contact with how you would
   actually build it. Honest cost of A: Jrue is 35 turning 36 on a 2-year deal (a $37M option into
   age 37), a win-now stabilizer while Joan develops, NOT a long-horizon piece; do NOT attach the
   No. 28 first to get him (you do not pay a first for a 36-year-old, a second either way is fine).
   Keep C in frame as the marginally-higher paper option with the third-team catch; the choice of
   the executable build over a paper-thin edge is itself the front-office judgment worth showing.

4. **Fork B is the worst realistic move (-1.15pp).** It sells the edge for what the capital
   cannot replace. Rejected on the project's own stated objective.

5. **Patience pays only CONDITIONALLY.** The future window (Gobert/Randle money off, cap and
   picks regained) opens to ~6-8% ONLY in the minority branch where Joan actually develops
   (~36-45% in the faithful base rate) AND the freed cap lands real talent. If Joan busts (the
   base rate), the future window is ~3.2%, no better than the near-term ceiling. (Illustrative:
   mapped through the current league; rivals age too, so this bounds rather than predicts.)
   "Be patient" is a real strategy only if you believe that conjunction; it is not free.

## The recommendation

Do not chase a title-winning move; with this capital, none exists. Make the disciplined marginal
upgrade: keep the defense, fix the Randle slot with a lead-guard creator (package A, Randle +
DiVincenzo -> JRUE HOLIDAY, the executable no-asterisk build), add a shooter with the MLE room
that shedding Randle unlocks, develop Joan and TSJ behind the veterans, and preserve flexibility.
Cam Johnson (package C) is a paper-thin edge that needs a third team, not worth chasing over the
clean build. Treat the real upside as a conditional future bet, made
eyes-open that it rests on a development outcome the data says is more likely than not to
disappoint. This is the OKC blueprint as it actually is (keep your edge, marginal discipline,
develop, wait for a window that pays only if the young bet hits), not the romantic version (one
bold blow-it-up move that shocks the league).

## The pillars that fell to measurement (why this is trustworthy)

The thesis rested on arguments that did not survive honest testing:
- LAFI as a baked-in fit gain (not significant, p=0.758; carried instead as a swept, symmetric,
  data-bounded term that even at max could not rescue Fork B).
- "Variance is a tail asset" (Joan's variance contribution to title odds measured ~0 at the
  Wolves' operating point; the convex-tail bonus does not exist at their strength).
- "Box buries Joan" (his box prior over-rates him; the rim correction was gated off; his value
  is a development bet, not a measurement rescue).
- The Joan bet itself on near-term title odds (a downgrade, robust across every sweep cell,
  driven structurally by Gobert being too good to replace).

At every step the engine refused to flatter the answer the project wanted, including overturning
the analyst's own assumptions. The conclusion is unwelcome and trustworthy for the same reason:
it was reached by a process built to be unable to manufacture it.
