# Board Build, Step One: Reachable Count + Toy Solve

Against `board_spec v2.0`. Produced 2026-07-17. Script: `board_step1.py`. **No real machinery. Every probability and value is a placeholder.** Step one proves the scaffold: the state space and calendar are encoded as the spec defines them, forward reachability lands a finite state set, and backward induction runs over it end to end.

## What was encoded

**State vector** (spec section 2), 12 fields = t plus the 11 spec dimensions: `perf` (4), `run` (6, monotone, RING absorbing), `melo_avail` (3), `fit` (4), `ant` (4, REQUESTED absorbing), `melo_deal` (3), `jaden` (4, now four tiers incl. CONVERTED), `cap` (4), and the decision-relevant reachable chest sub-fields `firsts_tradeable` (2), `pick2028_status` (3), `unlock_done` (2). The remaining chest sub-fields (seconds, sweeteners, expirings, core_on_roster) are deferred past step one, as the spec allows ("a modest set of reachable chest combinations").

**Decision calendar** (spec section 5): all 15 nodes (0-14) with their types (decision / commitment / read_R1 / read_R2 / threshold / chance / gate) and the node-dependent action menus (the deadline nodes 6 and 12 expose WAIT / ARM-G / ARM-B / ARM-S / UNLOCK; the chance nodes 7 and 13 resolve run and the 2028 swap).

**Root node** (spec section 3): t=0, perf=T2, run=none, melo_avail=B, fit=prior, ant=default, melo_deal=pre_ext, jaden=steady, cap=apron1, firsts=0, pick2028=swap_pending, unlock=False.

## Reachable count

| | count |
|---|---|
| Naive per-node product (non-t dims) | 663,552 |
| Naive x 15 nodes | 9,953,280 |
| **Reachable from root (with pruning)** | **17,743** |
| Transition edges traversed | ~31k |
| Absorbing states in the set (RING or REQUESTED) | present, not expanded |

Reachability pruning works: 17,743 is a 560x reduction from the naive 9.95M, because run is monotone (never regresses), RING and REQUESTED are absorbing and do not expand, chest evolves near-deterministically, and most dimensions are fixed until a specific node touches them.

Per-node reachable counts grow toward the gate (1 at nodes 0-3, ~10 after the reads, tens after the deadline, thousands after the July-2027 season boundary). The growth is dominated by **node 9 (July 2027)**, where the placeholder transition re-draws `ant` (4) x `jaden` (4) x `perf` (3) independently, a 48-way branch on every state. That single stub is most of the distance between this count and the spec's "low thousands" estimate.

**Honest note on the count vs the spec's prediction.** The spec guessed "low thousands." This scaffold prints 17,743, higher, for two placeholder reasons: (1) the node-9 branch treats ant, jaden, and perf as independent, which real transitions would correlate (a REQUESTED-out star and a Jaden leap are not independent draws), collapsing many combinations; and (2) monotone `run` is carried as a live dimension. It is also, in the other direction, an UNDERcount of the true space, because `melo_deal` is held fixed (no extension branch is modeled yet) and the full chest tuple is deferred. The number is reported as the scaffold produces it, not tuned to hit the prediction; step two's real transition stubs (correlated, roster-conditioned) are what move it toward the spec's estimate.

## Backward induction (toy solve on fake values)

Ran over all 17,743 states, processed in descending t so successors resolve first. Leaf value is a placeholder title-equity proxy (the objective is P(ring while Ant a Wolf)): zero if Ant requested out, else a monotone function of the deepest run and perf band.

- **Root value (placeholder): 0.28.** Meaningless as a number; it proves the induction completes and produces a value at the root.
- **Sanity checks pass:** a RING leaf values 1.00, a REQUESTED leaf values 0.00.
- **Decision logic demonstrated at a real menu node.** At node 6 (deadline 1) with fit=red and melo_avail=C, the solver's expected values are:

  | action | EV |
  |---|---|
  | ARM-G / ARM-B / ARM-S (improve fit) | 0.177 |
  | WAIT / UNLOCK | 0.119 |

  The arms that improve fit beat WAIT, because in the (placeholder) model a better fit shifts the playoff-run distribution deeper, which raises title equity. This proves the max-over-actions backward induction works, not just chance propagation: when the fit is red, the toy board correctly prefers to act.

## Status and what step one deliberately does NOT do

The scaffold runs end to end. It does **not** contain any real machinery: no Joan Bet perf/run distributions, no hazard curve, no availability posterior, no acceptance model, no real leaf values. Those are steps two (wire real transition stubs) and three (replace stubs one variable at a time, availability first since AVAIL-PACE is already built).

Known step-one simplifications, logged for step two:
- `melo_deal` is held fixed (no LaMelo-extension branch yet).
- The full chest tuple (seconds, sweeteners, expirings, core_on_roster) is collapsed to the three decision-relevant sub-fields.
- `cap`'s repeater_clock counter is folded into the cap band (not a separate dimension yet).
- Node-9 transitions treat ant/jaden/perf as independent; real transitions correlate them.
- Only one playoffs chance node (7) is modeled; the far-side seasons are a single monotone run.

**Stop for review** before step two.
