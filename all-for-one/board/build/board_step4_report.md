# Board Build, Step Four: Real Joan Bet, Both Forks First-Class

Against `board_spec v2.2` plus the ONE FOR ALL salvage rider. Produced 2026-07-17. Script: `board_step4.py`. Step four un-stops the one sub-item step three stopped and flagged: perf/run and the leaf title-equity anchor are now REAL, from a fresh Joan Bet (`bracket_sim`) run on the RECONCILED post-trade roster, carried across BOTH metric forks (rapm, box) end to end as first-class scenarios. Every headline is reported as a RANGE across the two forks with the driving fork named.

This step ran under the mandated three-lens adversarial workflow, which found one clean lens and two real defects. Both were fixed before this report; they are documented in full below because the process catching them is part of the deliverable.

## What un-stopped, and the gate that preceded it

The un-stop was CONDITIONAL on a roster reconciliation, because the encoded sim input failed inspection. That gate ran first and is its own artifact: `roster_recon/roster_reconciliation.md`.

**The phantom Gueye (silent-plausible bug #4).** The encoded rotation (`lamelo/data/impact/team_strength.json`, June 26) carried "Mouhamed Gueye" at 18 mpg. Doubly spurious: that player-id (1631243) is an Atlanta forward, and the intended Mouhamadou Gueye (1631338) went Chicago -> Charlotte in July, so NEITHER Gueye is a Timberwolf. The executed trade sent MIN only LaMelo and Green. The 18 phantom minutes were adding roughly +1.0 to the post-trade net on the rapm fork, masking the trade's rapm-negativity. Logged as bug #4 (trade ingested, roster consequence not) in the lamelo carry-forwards. The reconciled 15-man (July signings Hyland/Lyles/Evans added, Clark named, Shannon Jr. allocated 16 mpg, DDV correctly out on the Achilles) is in the gate doc with per-name provenance.

**Respecting the file's note.** The file's own note says the raw aggregated nets are pre-deflation and only the POST-minus-PRE delta is robust. The reconciled run honors that: it recomputes the trade delta from the reconciled rotation (`build_team_strength.team_raw_net`), deflates it (BETA 1.067), and feeds only the delta. It never reads the file's absolute nets. Title equity comes from `bracket_sim` proper, both forks. Lens 1 of the verification confirmed no absolute leaked.

## The reconciled Joan Bet, both forks

`roster_recon/joanbet_reconciled.py`, 20,000 sims x 5 seeds per fork, on the reconciled roster:

| Fork | recon trade delta (raw / deflated) | MIN net pre -> post | ~wins | title equity | reach R2 | CF |
|---|---|---|---|---|---|---|
| **rapm** | -0.637 / -0.680 | +2.18 -> **+1.50** | ~44 | **1.94%** | 30.3% | 12.0% |
| **box** | +0.715 / +0.763 | +2.18 -> **+2.94** | ~48 | **3.81%** | 46.8% | 18.9% |

The two forks genuinely disagree about the trade. On the rapm read the deal is mildly NET-NEGATIVE (LaMelo's multi-season RAPM does not clear what left) and MIN is a ~44-win play-in team; on the box read the deal is net-positive and MIN is a ~48-win solid playoff team. That disagreement is not noise to average away; it is carried as two first-class scenarios so every board output below is a range.

Real distributions the board consumes (per fork):

- **run bands** (season-1 deepest result): rapm {none .62, R1 .08, R2 .18, WCF .07, F .03, RING .019}; box {none .39, R1 .15, R2 .28, WCF .11, F .05, RING .038}.
- **perf bands** (node-9 season-boundary re-draw): rapm {T1 .06, T2 .33, T3 .40, T4 .21}; box {T1 .16, T2 .45, T3 .30, T4 .08}.

## The leaf-scale swap (real title equity replaces the interim anchor)

Step three anchored the soft-horizon leaf scale to the lamelo interim (~0.027). Step four replaces that single gated number with each fork's real `bracket_sim` title equity: `LEAF_SCALE = fork_title / 0.027`, so rapm leaves scale to x0.717 and box leaves to x1.411 of the old scale. RING (=1.0) and the salvage terms stay ABSOLUTE (a title is a title; salvage is Bobby's dial), so the fork scale moves the live-branch leaves relative to the FIXED hazard midpoint (0.10) and salvage cap (0.03). Lens 1 confirmed the swap is correct and the invariants hold.

## Results as fork ranges (driving fork named)

| Headline (cliff policy) | rapm | box | range | driven high by |
|---|---|---|---|---|
| leaf title equity | 0.0194 | 0.0381 | [0.019, 0.038] | box |
| root value | 0.0463 | 0.0875 | [0.046, 0.088] | box |
| P(ring while Ant a Wolf) | 0.0237 | 0.0450 | [0.024, 0.045] | box |
| P(Ant retained through S2 / gate commit) | 0.0063 | 0.1930 | [0.006, 0.193] | box |
| convert mass (proactive ARM-CONVERT) | 0.9408 | 0.5635 | [0.564, 0.941] | **rapm** |
| root action (node 0) | ext-wait | ext-wait | ext-wait | (both) |
| node-6 modal action | ARM-B (12/18) | ARM-B (10/18) | ARM-B | (both) |
| node-6 holds under both curves | 18/18 | 13/18 | | |

P(ring) and P(Ant retained) are computed SEPARATELY by forward policy simulation, never conflated, as the directive requires. Ant is retained through season 1 in both forks (the hazard first bites at the July 2027 boundary). The forks split hardest on season-2 retention: 0.6% (rapm) vs 19.3% (box).

## The convert-mass finding (reported, not tuned)

The single loudest fork split is convert mass: **rapm 0.94 vs box 0.56**, and it is driven by the leaf scale, exactly as the salvage rider is designed to surface. On the rapm read the reconciled roster is a ~1.9% title team; scaled down (x0.717), most live branches' continuation equity sits below the salvage cap, so at the July 2027 season boundary (node 9) the solver proactively converts in 94% of mass rather than run back a team it judges below the rebuild line. On the box read leaves scale UP (x1.411), clear the cap, and holding dominates in 44% of mass.

Per the **SALVAGE_CAP anti-tuning clause** now written into `board_spec v2.2` (section 4), the cap is NOT moved in response to this. A high convert mass is a REPORTED FINDING about where the reconciled roster's forward equity sits relative to a rebuild, not a parameter problem. The honest read: **if you believe the rapm valuation of this trade, the machine judges run-it-back barely better than a proactive reset; if you believe the box valuation, holding wins comfortably.** The fork you trust is the decision, and that is surfaced rather than buried under an averaged number.

The convert is always at node 9 (the season boundary), never in season 1 (retained_s1 = 1.00 both forks). The board never trades Ant at the first deadline; it runs it back a year, then decides.

## The salvage guardrail, now shown doing real work

Step three's never-trades-a-live-branch check compared each converter's stay-continuation to the cap. The verification (lens 3) correctly flagged that this passes by construction (a converter's convert value is `min(cap, ...)` and convert is the argmax, so its stay alternative is <= cap trivially): a true statement, but it could not demonstrate the guardrail protecting anything. Step four adds the meaningful measurement: the max continuation among convert-ELIGIBLE states that DECLINED to convert.

- **rapm: 0.1502. box: 0.3062.** Both far above the 0.03 cap.

So there really are live branches worth 15 to 31 points of title equity that the solver holds rather than converts. The guardrail is actively protecting them, not passing vacuously. The converter-side check is retained as a clamp-regression guard, and a direct `assert proactive_salvage(node) <= cap` was added so a broken clamp crashes.

## Three-lens adversarial verification (one clean, two fixed)

Per the standing instruction to keep the three-lens workflow on everything board-side, step four was checked by three independent adversarial lenses, each running real code against the solver.

**Lens 1, leaf-anchor / fork-scale: CLEAN.** Confirmed no absolute net leaks from the file into leaf equity; RING and salvage stay absolute (unscaled); LEAF_SCALE swaps correctly per fork; the convert-mass finding is a genuine consequence of the scale, not a bug.

**Lens 3, MAJOR, fixed, silent-plausible bug #5.** The rapm node-6 policy in the first run was a unanimous ARM-D dump (18/18). The verifier proved this was a pure artifact of a benefit-only placeholder cost (`ARM-D = -0.008`): the arm's only modeled state effect (cap relief) has NO valued channel here, because `_hazard9_next_states` was hardcoding `cap = tax_band` unconditionally, silently erasing ARM-D's relief before any leaf was valued, and the only cap-sensitive leaf is past that node-9 reset. So a free negative cost was buying an unsubstantiated dump; a single sign flip inverted the entire node-6 policy. This is the score_home/away pattern (a plausible output masking an inert code path) and is logged as silent-plausible bug #5 (benefit-only arm chosen unanimously; keystone fallback, FC-DRB fallback-index, phantom Gueye #4 precede it). Two fixes: (a) `_hazard9_next_states` now does `cap = min(current, tax_band)`, which models the July 2027 expirings easing the payroll toward the tax while PRESERVING a team that dumped below it; (b) `ARM-D` cost set to net-zero (its real cost side, the dump sweetener and lost Green+DDV matching and DDV's healthy-branch return, is unmodeled, and its repeater-reset benefit has no valued channel yet). After the fix the node-6 modal move is ARM-B (targeted frontcourt help that clears at ~0 sweetener) or WAIT, which is a defensible marginal-team deadline posture. The provenance line was corrected: ARM-G/ARM-B are acceptance-model REAL-ish, ARM-D is a PLACEHOLDER. Terminal mass still sums to 1.000000 both forks after the fix.

**Lens 2, MINOR, fixed.** A code comment claimed the perf-averaged leap "stays ~0.105" (the class base rate). Under the real perf re-draw the fork-averaged leap is 0.079 (rapm) and 0.096 (box), because the reconciled team's perf mass sits in T3/T4. The deviation is DOWNWARD, so the "not hope" intent is honored (conditioning on a middling team lowers the leap expectation further), but the literal claim was wrong. The comment now states the real numbers.

## Jaden priors seeded from the ratified class (item 6)

The board's `jaden` transition priors are seeded from the ratified defense-screened calibration class (`../jaden_calibration/jaden_markers_v02.md`, n=19), so the machine's leap expectation is the historical base rate, not hope: LEAP 2/19 = 0.105 (Barnes, Crowder), CONVERTED ~1/19 (Huerter, gate-fail plus offensive leap), STALLED ~6/19 (floor-trippers), STEADY the remainder. The T2 band is pinned to the base rate; perf tilts it modestly. The ratifications (ladder inversion, LEAP at one growth signal with two-signal as a historically-empty sensitivity, Gordon appendix) are recorded in `jaden_markers_v02.md` section 7.

## Preliminary reads (per fork, labelled)

- **UNLOCK price sweep**: spread +0.0000 (rapm), +0.0002 (box) on the real leaf scales with the placeholder unlock cost. UNLOCK still dies quietly; the box fork shows a hair of life once leaves are real. Preliminary, pending a real unlock cost. Provenance: leaf scale REAL per fork, unlock cost PLACEHOLDER.
- **LaMelo extension timing (node 0)**: ext-wait under both curves and both forks. The board prefers to preserve the option value of a season of fit data before extending. Preliminary: the melo_avail prior feeding it is REAL (backtest), but the extension EFFECT is placeholder. Provenance labelled.

## Sanity checks

Reachable state count 59,749 (grew from step three because the node-9 re-draw now spans four perf bands including T4). Terminal probability mass sums to 1.000000 under both forks. Dual-curve harness completes; node-6 holds-under-both 18/18 (rapm), 13/18 (box). RING terminal 1.00; REQUESTED salvages within the cap; proactive salvage decays with node; involuntary < proactive at every node.

## Stop for review

Step four runs end to end on the reconciled roster with both forks first-class and every output a labelled range. perf/run/title are un-stopped and real; the leaf anchor is the real `bracket_sim` title equity per fork; the salvage cap is untouched and its tension is reported; the guardrail is shown doing real work; the Jaden priors are class-seeded; the two verification findings are fixed and documented. **Stop for review.**
