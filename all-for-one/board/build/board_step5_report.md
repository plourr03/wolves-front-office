# Board Build, Step Five: Convert Frontier, Cliff Positioning, Loyalty Premium

At the **ruled SALVAGE_CAP = 0.012** ("I want to try to win this with Ant", Bobby, 2026-07-17, logged verbatim in `board_spec v2.3`), carried across both metric forks. Produced 2026-07-17. Scripts: `board_step5.py` (analysis, imports `board_step4.py` as the solver library) and `roster_recon/pretrade_counterfactual.py` (the trade-verdict sim). This step delivers the four post-step-four items plus the ruling's convert re-emission, and it ran under the mandated three-lens adversarial workflow.

The cap ruling is a legitimate values move under the anti-tuning clause: values-anchored (Utah 2022 near 1, rebuild median 2-3, OKC best 5-6, in title-equity points), with solver outputs used once as a disclosed consistency check and no cap adjusted to alter any output. On receipt SALVAGE_WEIGHT was scaled to 0.012 so max rebuild value (node 6, best leverage) equals the cap; `return_quality` (leverage decay in [0,1]) is unchanged.

## The ruled cap sharpens the fork split

At 0.012 the rebuild is worth at most 1.2 title-equity points, so the solver only resets branches whose forward equity has fallen below that. The convert masses:

| Fork | convert mass (cliff) | reading |
|---|---|---|
| **box** | **0.18** | holds Ant in 82% of mass: the optimistic read strongly supports "win with Ant" |
| **rapm** | **0.94** | still high, but every converter is a near-dead branch (below) |

The rapm mass barely moved from the 0.03 placeholder (0.94) because lowering the cap scales the proactive-convert value AND the proceed value (which contains the involuntary salvage) together: a genuinely dead branch prefers orderly conversion (proactive 0.0102) to watching Ant walk for the involuntary 0.0061 at ANY cap. So the cap change moved the marginal-alive branches (big on box, tiny on rapm) and left the dead ones converting. This is the no-scorched-earth behavior working, not a failure.

## 1. Convert frontier (conditional breakdown)

All convert mass is at **node 9**, the July 2027 season boundary. No mass converts at the first deadline (node 6): the board never trades Ant in season 1, it runs it back a year and then decides. Per fork, node-9 convert-vs-reach:

| Fork | node-9 reach | node-9 convert | convert % |
|---|---|---|---|
| rapm | 1.00 | 0.94 | 94% |
| box | 0.96 | 0.18 | 19% |

**By resolved state (run x melo_avail x jaden).** The convert conditions on the season-1 run result and LaMelo's availability; the `jaden` tier is `steady` for essentially all of it, because Jaden re-draws AFTER the node-9 decision (the tier conditioning lives in the loyalty premium at the gate, section 3, which is exactly where CONVERTED matters). Top rapm convert buckets:

| run (season 1) | melo_avail | mass |
|---|---|---|
| none (missed playoffs) | C (LaMelo under 40 games) | 0.278 |
| none | B | 0.158 |
| R2 exit | C | 0.089 |
| none | **A (LaMelo healthy)** | 0.088 |
| R1 exit | C | 0.085 |

The tell is the fourth row: on the rapm read, even a season where LaMelo stays healthy but the team misses the playoffs still resets (0.088 mass). The rapm roster is judged not good enough to contend even at full LaMelo availability. Box, by contrast, converts almost only the doubly-dead branch (missed playoffs AND LaMelo out): `none/C` 0.116, `R1/C` 0.064, and little else.

**Root hold-vs-reset reconciliation (the sentence and the number are the same fact).** The high convert mass is NOT a root-level preference to reset:

| Fork | run-it-back (optimal root) | reset-now (node 6) | hold beats reset by | value the reset OPTION adds over pure hold |
|---|---|---|---|---|
| rapm | 0.0316 | 0.0120 | 2.6x | +0.0034 |
| box | 0.0785 | 0.0120 | 6.5x | +0.0003 |

At the root the board prefers to run it back by a wide margin (2.6x on rapm, 6.5x on box), and giving it the reset option adds almost nothing over a forced pure-hold solve (+0.003 rapm, +0.0003 box). The 94% rapm convert mass is entirely a downstream node-9 conditional on the season turning out dead a year later, not a preference to reset today. Both numbers describe the same policy: hold now, and only orderly-convert the branches that arrive at the boundary already dead.

## 2. Cliff positioning (the trade verdict against the 0.10 line)

The pre-trade counterfactual (`pretrade_counterfactual.py`, encoded run-it-back rotation, both forks) gives the single-season read:

| Fork | pre-trade (run-it-back) | post-trade (reconciled) | trade delta |
|---|---|---|---|
| rapm | 2.65% title, ~46 wins | 1.94% title, ~44 wins | **-0.72 title pts** |
| box | 2.80% title, ~46 wins | 3.81% title, ~48 wins | **+1.01 title pts** |

The run-it-back team was itself a low-equity contender (~2.7% title, ~46 wins). The LaMelo trade is title-positive on the box read and title-negative on the rapm read; on rapm the post-trade team is actually a hair BELOW the run-it-back.

Positioned against the board's 0.10 hazard commitment line (forward equity, board root value, cliff curve):

| Fork | pre-trade root (commit p) | post-trade root (commit p) | move |
|---|---|---|---|
| rapm | 0.0437 (p=0.12) | 0.0316 (p=0.08) | DOWN the slope, -0.012 |
| box | 0.0464 (p=0.13) | 0.0785 (p=0.32) | UP the slope, +0.032 |

Neither roster clears the cliff on either fork (both forward equities sit below 0.10, so the hazard reads Ant as more likely than not to depart on the pre-trade team and on the rapm post-trade team). The trade's effect on Ant's implied commitment probability is fork-defining: it drops from 0.12 to 0.08 on the rapm read (the trade makes Ant likelier to leave) and climbs from 0.13 to 0.32 on the box read (the trade nearly triples his implied commitment odds, though still short of the cliff). PRELIMINARY; the pre-trade board reuses the post-trade scaffold with pre-trade sim inputs and LaMelo availability neutralized (no LaMelo pre-trade), labelled as such. Provenance: sim inputs REAL per fork, board structure a labelled approximation.

## 3. Loyalty premium (publishable three): keeping Jaden is cheap

Dual solve per fork, cold (free to expose Jaden at the gate) versus keep-Jaden (that arm disabled; the LaMelo/Ant extension arms unaffected). The expose-Jaden arm at node 14 uses only existing channels: the leaf loses Jaden's tier bonus and gains one band of cap relief. A real Jaden-trade asset return is NOT modeled, so the premium here is a conservative LOWER bound.

| Fork | curve | keep root | cold root | loyalty premium | expose tiers at the gate |
|---|---|---|---|---|---|
| rapm | cliff | 0.0316 | 0.0317 | **+0.0000** | stalled, converted only |
| rapm | ramp | 0.0345 | 0.0347 | +0.0002 | stalled, converted only |
| box | cliff | 0.0785 | 0.0800 | **+0.0015** | stalled, converted only |
| box | ramp | 0.0815 | 0.0826 | +0.0011 | stalled, converted only |

Two robust findings:

- **Keeping Jaden costs almost nothing.** The premium is 0 to 0.15 title-equity points (conservative). You do not have to choose between loyalty to Jaden and contending. The premium is larger on the box read (0.0015) than the rapm read (~0) for a simple reason: the loyalty premium can only be paid in branches where Ant stays, and Ant stays far more often on box (retained-through-gate 0.19 vs 0.006). If Ant walks, Jaden's fate barely touches the Ant-era objective.
- **The divergence is confined to the low-value tiers.** Cold exposes Jaden ONLY when he is `stalled` or `converted`; a `leap` or `steady` Jaden is never exposed (his leaf bonus exceeds the cap relief). `stalled` dominates the divergence by frequency and by having the lowest on-court value, with `converted` the secondary tier. The CONVERTED tier is the conceptually load-bearing one Bobby flagged (defensive gate failed, offensive leap achieved: the archetype-change case where loyalty actually costs a real fit decision), but it is UNDERSTATED here: a converted Jaden who made an offensive leap would return real trade assets, unmodeled in the cap-relief-only channel, so the true premium in the converted tier is higher than shown. The qualitative result (loyalty is cheap, and only ever questioned for a stalled or converted Jaden) is robust; the exact magnitude waits on the asset-return channel.

The convert audit under the keep-Jaden constraint is identical to the base board (keep == EXPOSE off): convert mass 0.94 (rapm) / 0.18 (box), zero live-branch violations.

## 4. No-scorched-earth, confirmed at the ruled cap

| Fork | node-9 convert / hold | converter stay (max) | held value (range) | hesitation gap |
|---|---|---|---|---|
| rapm | 201 / 69 | 0.0096 (< line: dead) | 0.0107 .. 0.0585 (> line: live) | 0.0102 vs 0.0061 |
| box | 18 / 252 | 0.0097 (< line: dead) | 0.0116 .. 0.2564 (> line: live) | priced |

The convert/hold boundary at node 9 is `proactive_salvage(9) = 0.0102` (the ruled cap 0.012 times the node-9 leverage 0.85), NOT the node-6 cap itself. Converters sit below that line (dead branches, preferring the proactive 0.0102 to watching Ant walk for the involuntary 0.0061); held branches sit above it (live, up to 0.26 on box). Note the lowest held values (0.0107, 0.0116) are below the 0.012 cap but above the 0.0102 node-9 line, which is why they correctly hold: the relevant comparison is the node's own salvage, not the max-leverage cap. The hesitation gap (proactive minus involuntary, 0.0041) is priced, so proactive conversion always beats waiting for a forced request. No live branch is traded on either fork.

## Three-lens adversarial verification

Per the standing instruction, step five (and the board_step4 additions that power it: the `EXPOSE_JADEN_ARM` and `DISABLE_CONVERT` flags, `exposed_leaf`, the gate expose arm) was checked by three independent adversarial lenses running real code: (1) convert-frontier accounting and the hold-vs-reset reconciliation, (2) the loyalty premium and the expose-arm wiring, (3) cliff positioning, ruled-cap scaling, and global-state hygiene.

**Lens 1: clean.** The instrumented forward conserves mass and reproduces the base convert mass exactly; the by-node and by-resolved-state buckets do not double-count; `DISABLE_CONVERT` genuinely strips ARM-CONVERT from every menu so `forced_hold <= root_hold`; the reconciliation is sound. One nit: the "beats reset-now by 2.6x/6.5x" ratio uses the optimal root (which itself converts dead mass downstream) rather than the pure-hold value; both readings exceed 2x and the pure-hold value is shown adjacent, so it is transparent (pure-hold ratios are 2.36x / 6.52x).

**Lens 2: clean.** All five checks confirmed correctness: `exposed_leaf` adds no term beyond `jaden->stalled` and one band of cap relief (0 mismatches across all 20,160 gate states); the premium is non-negative on every fork and curve; the keep-Jaden solve reproduces the base board's root value and convert mass to zero difference; expose-Jaden is chosen for zero leap and zero steady states (only stalled and converted, confirmed non-vacuous against 5,040 gate states per tier); the wiring is consistent across `reachable`/`action_value`/`forward` with terminal mass summing to exactly 1.0 with the arm on.

**Lens 3: one minor, fixed.** The no-scorched-earth print labelled held node-9 values as "> cap 0.012," but the lowest held values (0.0107, 0.0116) are below 0.012; they hold correctly because the node-9 convert line is `proactive_salvage(9) = 0.0102`, not the node-6 cap. The board's decisions were right; only the printed threshold was wrong. Fixed to compare against the node-9 line and to say so explicitly (code and the section-4 table above). A second nit (the pre-trade `board_root` left some fork globals unrestored on exit, harmless because every consumer re-sets them before solving) was closed by having `board_root` save and restore all fork globals.

## Stop for review

Step five runs end to end at the ruled cap, both forks, every headline a range. The convert frontier is broken down by node and resolved state with the root reconciliation; the trade verdict is positioned against the cliff; the loyalty premium is priced (cheap, conservative, tier-confined). ARM-D stays net-zero (its value channel is queued next, not improvised here); SALVAGE_CAP stays at the ruled 0.012 with no cap-adjacent edits. **Stop for review.**
