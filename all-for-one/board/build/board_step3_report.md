# Board Build, Step Three: Real-ish Machinery + the Salvage Rider

Against `board_spec v2.0` plus the ONE FOR ALL salvage/ARM-CONVERT rider. Produced 2026-07-17. Script: `board_step3.py`. Step three replaces the step-two placeholders with real and interim inputs one at a time, where the inputs exist; where they do not, it stops the sub-item and flags it rather than improvising.

**Provenance of every input is labelled**, because they are not all the same maturity:

| Input | Provenance |
|---|---|
| melo_avail prior over {A,B,C} | **REAL**, from LaMelo's injury-history reference class in the tripwire backtest (A .336 / B .267 / C .397, n=262) |
| arm costs (ARM-G/ARM-B/ARM-D) | **REAL-ish**, from the acceptance model's required sweeteners |
| leaf title-equity scale | **INTERIM, GATED**, anchored to the lamelo post-trade sim (~0.027/season), pending a fresh Joan Bet run |
| perf/run transition distributions | **STOPPED**, needs a fresh Joan Bet run on the post-trade roster (flagged below) |
| hazard params, arm effects, salvage weights | **PLACEHOLDER / TUNE** |

## 1. melo_avail goes real

The R1 read now resolves melo_avail on the **actual backtest prior**: LaMelo's injury-history class lands A .336 / B .267 / C .397. That distribution leans toward the low-availability tier (C is the single most likely, 40%), which is the honest reflection of his 22/47/72-game history and is exactly what makes ARM-G (guard insurance) a live arm. The hierarchical availability posterior stays a scheduled project per its build spec, off this critical path; the reference-class mapping is what the board consumes now, as the redefinition intended.

## 2. Dual-curve harness (a standard output from now on)

Every solve now runs under **both** curves: the cliff (midpoint 0.10, steep) and Bobby's robustness ramp (midpoint 0.08, moderate slope). The harness emits the holds-under-both-versus-flips sort as a standard output.

- Cliff root value 0.1252, ramp 0.1246 (both placeholder/interim scale).
- **Node-6 actions: 16 of 18 HOLD under both curves; 2 FLIP.** The flips are both `fit=yellow, melo=C` states, where the cliff prefers ARM-G and the ramp prefers ARM-B. Only the flips need a human ruling; the 16 holds are robust to the patience-curve shape. This is the sort that lets the board present holds as unconditional and flag flips for judgment.

## 3. perf/run: STOPPED and flagged (the guardrail worked)

Per the directive not to improvise roster inputs, this sub-item is **stopped**. The scout found that Joan Bet exists as runnable code (`offseason/scripts/bracket_sim.py`, Component E) but its default 2026-27 MIN roster is the **pre-trade** run-it-back roster (Randle + Reid, no LaMelo). No fresh post-trade run exists; the nearest (`lamelo/`, June 26) applies the trade as a scalar net-delta and its title number is gated. So perf/run stays placeholder here, with the requirement reported:

> **To un-stop perf/run:** run `bracket_sim.simulate_league()` on MIN's POST-trade lineup, which is already encoded at `lamelo/data/impact/team_strength.json`, reflecting the July final roster (two vet-min spots still open), and emit per-team title odds and seed bands. Until then the board carries placeholder perf/run dynamics, clearly labelled.

## 4. Acceptance model wiring (a real finding, and it inverts step two)

Arm costs now come from the acceptance model's required sweeteners: **ARM-G needs a ~4-point sweetener** (Tre Jones is the one guard that clears), while **ARM-B clears at ~0 points** (Robert Williams III, Nic Claxton). So **ARM-G costs more than ARM-B** in the board, the inverse of step two's guess that a backup big is the pricier move. The acceptance model's read is that backcourt insurance is the harder trade to construct for this team, and the board now prices it that way (ARM-G cost 0.012, ARM-B 0.003; ARM-D a net-relief dump at -0.008).

## 5. Leaf values from the interim (gated) title-equity table

The soft horizon is re-anchored so a neutral post-trade Wolves season sits near the lamelo sim's ~0.027 title equity, scaled by state health, with melo_avail folded in (A helps, C hurts). It is labelled interim and gated throughout, and it is not a published number; it anchors the scale so the hazard midpoint (0.10) and the leaf values live on the same title-equity scale, pending the fresh run.

## The salvage rider (ONE FOR ALL)

Departure is no longer worth zero. This is the objective amendment, and it lands cleanly.

- **Salvage value.** A departure salvages `SALVAGE_WEIGHT x return_quality`, **capped at SALVAGE_CAP = 0.03** (Bobby's dial: a stocked rebuild is worth at most 0.03 in title odds). ARM-CONVERT (proactive) at nodes 6, 9, 12, 14 is a terminal arm valued at proactive salvage; REQUESTED (involuntary) salvages at a discount.
- **Leverage decay + the price of hesitation.** return_quality decays toward the 2029 walk (proactive salvage node 6 = 0.0300, node 14 = 0.0165) and with the hazard level. At any node, **involuntary salvage < proactive salvage** (node 9: 0.0153 vs 0.0255): the gap is the price of hesitation, Utah 2022 (proactive Gobert trade) versus Minnesota 2007 (waited on KG), encoded.
- **The guardrail is a checked property, not prose.** Because ARM-CONVERT is capped at SALVAGE_CAP, no state whose stay-continuation exceeds 0.03 can prefer it. The convert audit lists every ARM-CONVERT state with its stay-continuation and asserts all are below the cap. **NEVER-TRADES-A-LIVE-BRANCH: PASS** (max converter stay-continuation 0.0254 < 0.03), and the run `assert`s it, so a regression would crash rather than slip through.

## Standard diagnostics (reported separately, every solve)

Cliff policy:

| Diagnostic | Value |
|---|---|
| P(ring while Ant a Wolf) | 0.0800 |
| P(Ant retained through season 1) | 1.0000 |
| P(Ant retained through season 2 / gate commit) | 0.2445 |
| P(mass reaching a proactive ARM-CONVERT) | 0.4415 |

P(ring) and P(Ant retained) are computed separately by a forward policy simulation, not conflated. **The high convert mass (0.44) is the salvage rider surfacing a real tension, not a bug**: the interim (gated) title-equity scale puts a typical post-trade Wolves state (~0.027) right up against the salvage cap (0.03), so for a marginal ~2.7% title team a stocked rebuild is genuinely competitive, and the solver takes it wherever the live branch has thinned to the cap. A fresh Joan Bet run that spreads strong states well above 0.03 would separate live branches from the cap and cut the convert mass; the current figure is a property of the interim scale and is labelled as such. The guardrail still holds throughout (no converted branch was live).

## Preliminary reads (components named)

- **UNLOCK spread: +0.0000** on the interim leaf scale with placeholder unlock cost. Consistent with step two's finding that UNLOCK dies quietly under these placeholders; preliminary, pending real leaf values.
- **LaMelo extension timing (node 0): ext-wait** under both curves. Flipped from step two once the salvage rider and interim leaves entered. Preliminary: the extension effect is placeholder, though the melo_avail prior feeding it is real.

## Sanity checks

RING terminal 1.00; REQUESTED now salvages 0.0099 (>0, capped at 0.03); proactive salvage decays node6 0.0300 > node14 0.0165; involuntary < proactive at node 9. Reachable count and backward induction run end to end; the dual-curve harness completes.

## Adversarial verification

Per the standing instruction to keep the three-lens workflow on everything board-side, step three was checked by a three-lens adversarial workflow (salvage guardrail, forward-sim mass conservation, harness/marker-parsing consistency). **Result: nothing severe survives.** The reviewers confirmed empirically that (a) the salvage guardrail holds under both curves (convert EV is `min`-clamped to SALVAGE_CAP, so `max` can never pick it over a stay branch worth more, and the violations list is empty), (b) total terminal probability mass sums to exactly 1.0 (stay-split weights sum to 1, the node-9 hazard distributes `p_stay + (1-p_stay)`), and (c) every `outs[0]` dispatch reads the marker/prob position consistently, with no residual position mixup after the one caught during self-testing.

Two minor items were raised and handled: the `t==7, eff==3` branch is unreachable dead code (by design, since season-1 run is drawn at a fixed T2, no perf read), left as-is; and a REQUESTED terminal that hardcoded node-14 leverage while `node9_resolve` credits node-9 leverage inline was a latent inconsistency (inert, because those states are never read for value) and is now fixed to be node-aware, so a future refactor that does read them stays correct. Neither changed any printed number.

## Stop for review

Step three runs end to end with provenance labelled. The load-bearing new pieces (the hazard-reads-value keystone from step two, the salvage guardrail, the dual-curve harness, the real melo_avail prior) are in place; perf/run is the one stopped sub-item, flagged with its exact input requirement. Everything remains placeholder/interim/TUNE except the two real inputs (melo_avail prior, acceptance-model arm costs). **Stop for review.**
