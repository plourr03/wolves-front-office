# Board Build, Step Two: Transition Structure + the Hazard Recursion

Against `board_spec v2.0`. Produced 2026-07-17. Script: `board_step2.py`. **All probabilities and values are placeholders (TUNE).** Step two adds real transition *structure* to the step-one scaffold; step three replaces the placeholder numbers with real machinery one variable at a time (availability first, since AVAIL-PACE is built).

Bobby's review note is taken to heart: the node-9 independence simplification is the project's central subject (correlated failure), so the causal-ordering and hazard-reads-value wiring below is load-bearing analysis, not cleanup. The 17,743 -> 33,901 count growth is accepted as reported, not tuned toward any target.

## 1. Causal ordering at season boundaries

At node 9 (July 2027) the resolution is now ordered, not simultaneous: **perf re-draws, run stays monotone, jaden conditions on the resolved perf, and ant resolves last.** Jaden's tier distribution is a function of the resolved season (a T1 season makes a leap likelier: leap 0.35 vs 0.10 in a T3 season). This replaces step one's independent draw and is the structural home for the correlated-failure story the project is about.

## 2. The keystone: hazard-reads-value recursion

Ant's transition at nodes 9 and 14 is the cliff curve applied to the solver's **own continuation value** at the state: `P(commit) = sigmoid(SLOPE * (equity - 0.10))`, midpoint 0.10, steep slope, all TUNE. There is no fixed-point circularity within a backward pass: because states are processed in descending t, the continuation values the hazard reads (the stay-branch successors at t > 9) are already solved when node 9 is evaluated. `node9_resolve()` is the single code path that computes this, used by both `solve()` and the demo, indexing `val` by membership (`k in val`) with no soft-horizon fallback, so a missing continuation surfaces as an error rather than a silent substitution. (An earlier draft's demo built synthetic states that were never reachable and silently fell through to the horizon leaf; the step-two adversarial verification caught it, and this is the corrected version reading real solver values.)

**Demonstration, computed over all 180 actually-reachable node-9 states.** The forward-equity range across them is min 0.043, median 0.119, max 0.230, which straddles the 0.10 cliff, and P(Ant requests out) ranges min 0.012, median 0.362, max 0.864. Representative real states, low equity to high:

| run | perf | jaden | melo_deal | fit | forward equity | P(REQUESTED) |
|---|---|---|---|---|---|---|
| R1 | T2 | steady | pre_ext | yellow | 0.043 | 0.864 |
| R2 | T2 | steady | pre_ext | green | 0.069 | 0.728 |
| WCF | T2 | steady | pre_ext | yellow | 0.128 | 0.294 |
| WCF | T2 | steady | extended | yellow | 0.164 | 0.109 |
| F | T2 | steady | extended | yellow | 0.230 | 0.012 |

The cliff engages exactly as the spec's patience curve intends: a shallow season with LaMelo unextended (equity 0.043) puts Ant's departure probability at 0.86, while a Finals run with LaMelo extended (equity 0.230) drives it to 0.01. This is the mechanism that makes a declined supermax the loudest observable on the board, and it is now demonstrated on the solver's real continuation values, not a constructed illustration.

**smax_signed multiplier flows through (node 14 final hazard):** a state that reached the gate having signed the supermax carries a departure hazard multiplied by 0.3.

| node-14 state | soft-horizon cont | P(final REQUESTED) |
|---|---|---|
| ant = smax_signed | 0.085 | 0.188 |
| ant = default | 0.070 | 0.741 |

Isolated at a fixed continuation of 0.12 (so only the multiplier differs): base P(depart) 0.332 -> smax_signed 0.100 (x0.3). Signing the supermax is worth a large reduction in late-window departure risk, and that value flows back through the backward induction to raise smax_signed states everywhere.

## 3. melo_deal live (extension timing expressible)

An extension arm exists at nodes 0 and 12 (`ext-LaMelo-now` / `ext-wait`), with a placeholder cost (0.012) and effect (melo_deal -> extended, which the soft horizon rewards as pairing/asset health). The extension-timing question is now a real choice the solver evaluates. Under the current placeholders the toy optimal action at node 0 is **ext-LaMelo-now** (the horizon value of locking LaMelo in outweighs the early cost); that flips with the placeholder cost, which is the point: the question is expressible and TUNE-able, not that this answer is real.

## 4. Arm differentiation

The deadline menu now carries distinct cost AND effect per arm: ARM-S (free stagger, a one-level fit nudge capped at yellow), ARM-G (guard depth, one-level improvement that can reach green, cost 0.015), ARM-B (backup big, one-SHOT to green in a single move, cost 0.020), UNLOCK (option purchase), ARM-D (dump, net cap relief via the repeater reset, cost -0.008).

Across the 18 reachable node-6 states the optimal action splits **ARM-G 6, ARM-B 6, ARM-D 6** (the three fit levels the reads produce, times the cap states): ARM-G wins where fit is yellow (cheapest route to green), ARM-B wins where fit is red (the one-shot to green beats a free half-step), ARM-D wins where fit is already green (nothing to fix on the pairing, so shed salary for the repeater reset). This corrects the earlier draft where ARM-B was strictly dominated by ARM-G (identical effect, higher cost); it now has a distinct effect and wins its own states.

Honest note (the verification flagged the earlier overclaim): **ARM-S is optimal in 0 of the 18 states** under the current placeholders, because the value of reaching green always exceeds ARM-S's free half-step to yellow. That is a real toy outcome, not a demonstrated preference; the report states it rather than claiming ARM-S is chosen. Whether a free stagger is ever sufficient is a step-three calibration question.

## 5. UNLOCK pricing (with-vs-without spread)

Node 12's advance-trade-2028 action is gated on `firsts_tradeable`, which only UNLOCK enables; the advance-trade is a stronger move (full fit->green) than the ordinary expiring-matched ARM-B2 (one fit level). Rather than report one number, the demo **sweeps the placeholder unlock price** and reports the with-vs-without option value at each, which is precisely the spec's pricing mechanism ("compute board value with and without UNLOCK... report the spread; if the spread never exceeds the market price, UNLOCK dies quietly"):

| unlock price | value w/ option | value w/o | spread | verdict |
|---|---|---|---|---|
| 0.004 | 0.1581 | 0.1555 | +0.0026 | UNLOCK lives |
| 0.008 | 0.1574 | 0.1555 | +0.0019 | UNLOCK lives |
| 0.012 | 0.1568 | 0.1555 | +0.0013 | UNLOCK lives |
| 0.020 | 0.1555 | 0.1555 | +0.0000 | dies quietly |

The option value is the gross benefit of having the 2028 first deadline-usable at node 12 (it pays off in the branch where node 11 leaves fit red at deadline 2 and the premium pick fixes what the expiring-matched move cannot). It falls as the price rises and hits zero around 0.012-0.020: above that break-even, UNLOCK dies quietly. That crossover, computed by the solver, is the mechanism step three prices with real market numbers.

## 6. Soft horizon (no scorched earth)

Terminal states carry a continuation value as a function of state health (run, perf, jaden, melo_deal, ant, cap, fit, firsts), so the late tree does not go to zero. The weights are now scaled as a P(eventual ring) proxy on the same scale as the hazard midpoint (0.10), which is the calibration the verification's issue #1 exposed: a health proxy on a larger scale had left the cliff inert. A healthy horizon state values ~0.185; a bleak one ~0.05; neither is zero, so the solver never torches the final year (spec section 1). REQUESTED is the only hard zero.

## Reachable count and drivers

**33,901 reachable states** (step one was 17,743). The growth is driven by the mechanisms this step added, exactly where the spec says the action is: node 9 now resolves perf(3) x jaden(4) x ant(4) causally, `melo_deal` branches (the extension arm), and node 11 redraws season-2 fit. This is reported as produced, not tuned. It remains a 300x prune from the naive product, and tractable with large headroom (the full solve runs in a couple of seconds).

## Sanity checks (unchanged, still pass)

RING terminal 1.00; REQUESTED terminal 0.00; soft-horizon healthy 0.185 and bleak 0.05 (both > 0). Backward induction runs end to end over all 33,901 states and returns a root value (0.1555, placeholder, now on a realistic title-equity scale).

## Adversarial verification (and what it changed)

Step two was checked by a three-lens adversarial workflow before this writeup was finalized. It confirmed the solver core (backward induction, `node9_resolve` / node-14 hazard, descending-t ordering, reachability) is sound, and it caught four real defects that this revision fixes: (1) MAJOR, the keystone demo built synthetic node-9 states that are never reachable and silently fell through to a soft-horizon fallback, so its cliff was an artifact rather than the solver's real recursion, the exact silent-fallback pattern the project's own review discipline warns about; the demo now runs `node9_resolve` over real reachable states with membership indexing. (2) the `x or fallback` idiom that would mask a legitimate 0.0 continuation, replaced with `k in val`. (3) ARM-B was strictly dominated by ARM-G, now given a distinct one-shot-to-green effect. (4) the report overclaimed that ARM-S is chosen; it is chosen in 0 states and the report now says so. The verification is why the keystone demonstration in this file is trustworthy rather than merely plausible.

## What step two deliberately does NOT do

No real machinery: the hazard slope/midpoint/multiplier, the perf/run/jaden distributions, the arm costs/effects, and the soft-horizon weights are all placeholders. Step three replaces them one variable at a time. Remaining simplifications: one playoffs chance node (season-2 run is a single monotone value); the full chest tuple is still the three decision-relevant sub-fields; cap's repeater_clock is folded into the band. **Stop for review.**
