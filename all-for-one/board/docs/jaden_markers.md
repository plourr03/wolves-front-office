# Jaden Tier Markers

Pre-registered definitions for the jaden state variable on the master plan board. Draft v0.1, July 17, 2026. Status: DRAFT, thresholds TUNE, frozen only after the agent feasibility pass confirms every marker's data source (the SPACE-ANT rule: no marker freezes on data the warehouse cannot produce).

## 0. Plain language summary

The board tracks Jaden McDaniels on a four-setting dial: LEAP, STEADY, CONVERTED, STALLED. This file defines the on-court evidence for each setting, in advance, so that nobody eyeballs "did Jaden level up" in the heat of an extension negotiation. The design principle, set by Bobby: elite defense is the must (a gate), offensive efficiency is the climb (a ladder). A fourth tier, CONVERTED, covers the world where the scoring arrives but the stopper role fades, because that world is a different decision, not a failure.

## 1. Customers and read dates

The dial's customers are the July 2027 extension node and the summer 2028 gate on the board. In-season reads at R1 (late November) and R2 (early January) are informational only; the binding tier assignment is computed at season end. This variable does not gate the February trade deadline; that belongs to the tripwires.

## 2. The tier grid

Two axes. Axis one, the defensive gate: pass or fail. Axis two, the offensive ladder: leap band or not.

| | Offense: leap band | Offense: not leap band |
|---|---|---|
| Defense gate: PASS | LEAP | STEADY |
| Defense gate: FAIL | CONVERTED | STALLED |

Gate posture by tier, for the board's arms: LEAP, extend, near-untouchable, the duo thesis is real. STEADY, extend at two-way role price, keep; this is where the loyalty premium applies most naturally. CONVERTED, the archetype changed; peak market value coinciding with a role mismatch next to LaMelo; the cold solver will read it as the sell-high branch, and the loyalty premium output is expected to diverge widest here. STALLED, the hard conversation; convert or extend cheap depending on market.

## 3. Defensive gate markers

All per-opportunity, so a shrinking offensive role cannot slander the defense.

JD-LOAD (deployment). Jaden leads the roster in matchup time share against opponents' primary perimeter creators, from the matchup data. Measures a coaching decision, near noise-free, readable at R1.

JD-COVER (the anchor claim, literal). Team defensive rating in LaMelo's minutes is materially better with Jaden on the floor than off. Draft threshold: 3.0 points per 100 (TUNE), minimum possession floor (TUNE), readable at R2, binding at season end.

JD-HOLD (suppression, season end only). Primary options he defends score below their own season baselines, aggregated diff-in-diff across matchups. Too noisy for midseason; honest by April.

Gate failure definition (two-part, protects against mislabeling): the gate fails only if JD-LOAD fails AND at least one of JD-COVER or JD-HOLD fails. If deployment drops but effectiveness holds, that is coaching reallocation with skills intact; it reads STEADY with a REALLOCATED flag, and the flag is itself information for the gate conversation, since the anchor seat being empty by choice is a roster question, not a Jaden question.

## 4. Offensive ladder markers

JO-EFF (the climb). True shooting percentage measured against two baselines at once: the league, and his own trailing three-season baseline. Leap band: clears both by a real margin (TUNE, calibrated on the reference class in section 5). Flat band: within noise of baseline. Decline: materially below.

JO-FLOOR (anti-vanishing clause). Scoring attempts per 75 possessions may not fall more than roughly 15 percent below his trailing baseline (TUNE). Efficiency achieved by disappearing is not a leap. A broken floor caps the offensive axis at not-leap regardless of JO-EFF.

JO-GROWTH (season end only, distinguishes a true leap from eating well off LaMelo's gravity). At least one of: self-created scoring efficiency rising, free throw rate rising, or three-point volume and accuracy both rising. Exact rungs pend the feasibility pass; any rung the warehouse cannot compute is struck, not approximated.

LEAP requires: gate passed at every read, JO-EFF in the leap band, JO-FLOOR intact, at least one JO-GROWTH signal. Connector-level playmaking is explicitly a dashboard nice-to-have and not a marker; the creation seats on this roster are taken, and the thesis Bobby set is stops plus no wasted possessions.

## 5. Calibration class (TODO, Phase-2-style extraction)

Thresholds get calibrated on a small reference class: two-way wings whose team added a high-usage star creator, evaluated on how their per-opportunity numbers moved. Canonical success: Aaron Gordon after arriving next to Jokic. Seed candidates: Gordon (DEN 2021), Bridges (NYK 2024), Anunoby (NYK 2024), Finney-Smith archetypes. Class construction follows the tripwire backtest's discipline: extraction query, seed validation, curated log for anything hand-added.

## 6. Change control

This file freezes with the October 20 freeze, alongside TRIPWIRES.md, under the same rule: edits after the freeze require a logged justification in the file. The tier read at season end 2026-27 feeds the July 2027 node as computed, not as re-argued.
