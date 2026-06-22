# Keep-the-core PACKAGES: combined-roster effect on the season (deliverable)

Each package's full post-move roster modeled end to end and compared to stand-pat (NOT summed
from individual move deltas; the moves are coupled under the apron, compete for minutes, have
diminishing returns, and the fit term is recomputed on the combined roster). CBA-gated first.
Champion = Knicks; OKC = projected favorite, not champion. Opponent board is RS-net-seated and
mis-seats playoff-pedigree teams, so the ABSOLUTE level is approximate and the DELTAS are robust.

## Results (Year-1, title odds banded; vs stand-pat 2.42% and vs best single retool 3.05%)

| package | CBA | title band | dStandpat | dRetool | R2 | CF | Finals | ~wins |
|---|---|---|---|---|---|---|---|---|
| stand-pat (keep Randle + taxpayer-MLE shooter + Ayo + Joan) | PASS (first apron) | 2.42% [0.0,7.6] | - | -0.63 | 29% | 11% | 5% | 44 |
| **A  Randle+DDV->Jrue + full-MLE shooter + Ayo + rookie** | PASS (taxpayer) | 3.01% [0.1,9.0] | +0.60 | -0.04 | 35% | 14% | 6% | 45 |
| B  Randle+DDV->MPJ + min shooter + Ayo + rookie | PASS (taxpayer) | 2.45% [0.0,7.5] | +0.03 | -0.60 | 29% | 11% | 5% | 44 |
| **C  Randle->Cam + full-MLE shooter + Ayo + rookie** | PASS* (taxpayer) | 3.19% [0.1,9.3] | +0.77 | +0.14 | 37% | 15% | 6% | 46 |

*C requires a THIRD-TEAM Randle taker: Denver is shedding salary (re-signing Watson) and will not
absorb Randle's bigger, longer deal, so a Randle-for-Cam swap needs a third team to take Randle.

## What it says (plain language)

Every keep-core package lands in the low 3s% of title odds, a modest lift over stand-pat (~2.4%)
and essentially TIED with the best single retool (~3.0%). The combined moves do NOT compound into
contention: the best package (C) is only +0.14pp over the single best retool, because the Randle
slot is the one real upgrade lever and stacking a shooter + a rookie on top adds little
(diminishing returns, exactly why deltas must not be summed). Round-advancement moves modestly
(R2 29%->35-37%, CF 11%->14-15%, Finals 5%->6%, ~44->45-46 wins): a slightly better team, not a
transformed one. The bands overlap stand-pat heavily, so on title odds alone these are small,
disciplined improvements, the decision rests as much on flexibility and development as on the
title number.

Package-level confirmations of earlier findings:
- B (MPJ) barely helps (+0.03): MPJ is a near-lateral move from Randle (low impact + high usage),
  confirmed now in a combined roster, not just in isolation.
- A (Jrue) is the clean, attainable package (+0.60, ~tied with the retool); the realistic pick.
- C (Cam) is the highest (+0.77) but needs the third-team structure and Cam is a shaky seller.

## CBA texture (a real flexibility finding)

Keeping Randle pins MIN at the FIRST APRON (~$214M), where only the TAXPAYER MLE (~$6M) is
available. Shedding Randle drops MIN under the first apron (~$206M, taxpayer tier), which unlocks
the FULL MLE, though using it hard-caps at the first apron, so the bigger the return's salary, the
less MLE room remains: A/C (Jrue/Cam) leave ~$8-9M (a real rotation shooter); B (MPJ's $40.8M)
leaves only a minimum. So moving Randle buys both a roster upgrade and a bigger exception, a
flexibility gain beyond the on-court that stand-pat does not have.

## Decomposition of package A (cumulative; NON-ADDITIVE, illustrative only)

bare (keep Randle, no Ayo/MLE, Joan->replacement) 1.19% -> +re-sign Ayo +0.45 -> +develop Joan
+0.39 -> +Randle->Jrue swap +0.36 -> +MLE shooter +0.43. Each piece adds ~0.4pp; they are
cumulative and order-dependent and do NOT sum to the package total (interactions + diminishing
returns). The point: no single component carries it; it is a stack of small, real improvements.

## Ja Morant scenario (SEPARATE, flagged, NOT a recommendation)

| Morant | title band | dStandpat |
|---|---|---|
| with availability (~79/246 games, ~0.32) | 1.84% [0.0,6.1] | -0.58 (WORSE than stand-pat) |
| IF healthy (full availability) | 2.84% [0.0,9.3] | +0.42 |

Boom-bust, and mostly bust: even healthy, Morant is only +1.08 (sd 1.85) in the spine and stacks
on-ball usage next to Edwards (the iso-duplication the thesis runs from), so healthy he is a
modest +0.42; his ~1/3 availability then guts the median to BELOW stand-pat. The high-variance
splash is worse than the disciplined packages on the central estimate, exactly the fit-over-splash
case, now shown with his real availability.

## Guardrail check

The low-3s% result is the prior expectation (a sanity check, not a target), and the combined
model matched it without forcing, consistent with the frontier and retool findings: the Wolves
are asset-constrained into the mid-tier this window, and the disciplined keep-core retool (A, or
C if a Randle taker exists) is the best available move, a small lift, not a leap.

## Provenance

Warehouse snapshot wh_0e1a90b850e6ea3b | engine reuse: bracket_sim + series_resolver (calibrated)
| seed 20260621 | ndraw 4000 | outcome curves n=8000 | script core_max/engine/run_package.py |
inputs: player_value.csv (impacts), Phase-2 dev_distribution (Joan), frozen warehouse snapshot.
Fact-check corrections applied (Knicks champion; opponent-board mis-seating disclosed; deltas are
the robust quantity).
