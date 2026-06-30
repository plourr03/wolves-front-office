# Team-strength findings, 2026-06-25 (regressed, K-swept)

Both metric forks aggregated end to end and consistently. Deep-bench RAPM regressed
toward replacement, possession-weighted at K = RELIABLE_POSS = 3000 (the principled
reliability scale from `build_rapm.py`, NOT tuned to a clean number). DiVincenzo OUT.

## The headline result (raw aggregated net, pre-SCALE-deflation; delta = post - pre)

| fork | trade delta at MODELED Gueye | best read |
|---|---|---|
| RAPM (defense-aware) | +0.003 | wash to modest NEGATIVE (see Gueye fork) |
| box (defense-blind) | +0.776 | a small positive (shrinks to ~0 at replacement Gueye) |

NO false precision: the RAPM delta is NOT "exactly zero" or a "perfect lateral." It is a
point inside the model's resolution, and the sim attaches the error band.

## Role-player valuation fork (Fix 1, `sweep_gueye.py`): the +0.003 is the most Gueye-favorable point

The RAPM "wash" depends entirely on crediting Mouhamed Gueye, a near-minimum throw-in, at
his full shrunk RAPM (+1.498). Gueye has the exact low-sample-big defensive-RAPM profile
the analysis flags as unreliable for Edey and Diabate: 7,608 possessions, value almost
entirely from defense the box cannot see, and he is plausibly waived. He is a real
researcher degree of freedom and gets his own fork alongside K:

| Gueye valued at | RAPM trade delta | box trade delta |
|---|---|---|
| modeled (shrunk +1.498) | +0.003 | +0.776 |
| neutral (0.0) | **-0.559** | +0.570 |
| replacement (-1.5) | **-1.121** | +0.007 |

So +0.003 is the single most Gueye-favorable point on the curve. Valuing the throw-in
reliably, the defense-aware result is a **wash to a modest negative**: roughly -0.4 to -0.6
in net at a neutral Gueye, reaching about -1.1 at replacement. The defense-blind result
stays positive but shrinks to ~0 at replacement. The same contested Gueye value also props
up the Gobert-fragility backup-5 term (cliff +4.00 with him, +5.89 without), so one
unreliable number flatters two results.

## K-stability (researcher-degree-of-freedom check; `sweep_regression_K.py`)

The regression strength K was swept. The RAPM trade delta stays in roughly [-0.03, +0.10]
across every defensible K (0, 1000, 2000, 3000, 4000, 6000, 10000); the box delta stays a
small positive (~+0.74 to +0.84). The finding is K-STABLE: the near-zero RAPM result is
not an artifact of K=3000. This is the multiverse check the discipline requires, and it
passes.

## This is robustness, not "fork instability"

Earlier framing called this a fork that might "flip." Both metrics AGREE the change is
SMALL in magnitude: at most a small positive (defense-blind), and a wash to a modest
negative (defense-aware, once the Gueye throw-in is valued reliably). The metric and
role-player choices decide "modestly worse" versus "barely positive," NOT "great" versus
"terrible." So the conclusion is robust in MAGNITUDE (small either way) but the SIGN
depends on the metric and on the Gueye valuation: the defense-aware read leans slightly
negative. Report both forks and the Gueye fork (no cherry-pick).

## The actual story is Q1 (the editorial payload)

Team strength being a wash (or slightly negative) is the SETUP, not the conclusion. The
decision-grade question is where it gets sharp: Minnesota paid a 2033 unprotected first,
three first-round swaps (2028/2029/2030), three seconds, and a second-apron hard cap (with
the $33.3M exception and the full MLE forfeited), for a move that, on the most complete
defensive read, changed their team strength by an amount from indistinguishable-from-zero
to slightly negative (once the throw-in is valued reliably). The Q1 decomposition frames
the asset-and-flexibility cost against that on-court result: "they did not get better, and
on the most complete read they got slightly worse, and here is the mountain of future they
spent to do it."

## Caveats carried to the sim

- Rotation documented and confirmed; starters drive the result.
- Raw nets need SCALE deflation (the delta is the robust quantity); done in the sim.
- Field rating (30 teams) and the SCALE / SHAPE / series-resolver re-validation are next;
  the CRN-paired delta is field-robust. When the title-odds band comes back, split it into
  the reducible (more data sharpens) and the irreducible one-season-variance parts.
