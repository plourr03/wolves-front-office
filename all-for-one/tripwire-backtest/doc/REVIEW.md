# Tripwire Backtest: Review Package

Produced 2026-07-17, updated after Phase 4. Phases 0 through 4 ran; the deliverable is a **TRIPWIRES.md draft that stops before the freeze** for review. Everything is committed and pushed.

## Phase 4 draft (the deliverable)

`../TRIPWIRES.md` (draft, not frozen): two wires. **AVAIL-PACE -> ARM-G** (R1 12/20 advisory, R2 23/37 binding, hard-trip allowed, cushion language, 63-game sensitivity). **FC-DRB -> ARM-B** (bottom-third at both reads, marginal-wire disclosure). WAIT explicit default. ARM-S free takes non-binding advisories from the PAIR-DRTG/TOV-BLEED dashboard. Target lists via the acceptance model. Freeze 2026-10-20 + change-control + optional hash line.

**Top review item (I flagged, did not decide):** FC-DRB was admitted on the Scenario C succession-class persistence (0.617, whole-team DRB), but the wire's own Gobert-off metric persists at only ~0.50. The Wolves keep Gobert and lose the second anchor (Reid), so the wire reads Gobert-off. Keep-with-disclosure vs demote-to-dashboard (ship one wire) is your call. See `memo_signgate_amendment.md`.

**SIGN_GATE amendment** (`memo_signgate_amendment.md`): the 0.70 gate translated via arcsine to Spearman >= 0.59 (n >= 30); FC-DRB admitted, symmetry re-checked, CIs reported, disclosed in change control.

---

## The earlier phases (Phases 0-3, all committed)

## What ran

| Phase / task | Deliverable | Outcome |
|---|---|---|
| Phase 0 schema map | `phase0_README.md` + 5 docs | Mapped; found the usg_pct scale bug, retired the pick2033 availability collision, struck SPACE-ANT (G4) |
| Spec amendment | `tripwire_backtest_spec.md` v0.2 | All Phase 0 rulings folded in |
| Stint trust spike | `phase0_stint_trust_spike.md` + addendum | Green to 2010-11; sealed seasons (2021-26) uniformly green incl. LaMelo's 2025-26 |
| Phase 0.5 honors | `phase05_honors_ingest.md` | All-NBA exact + All-Star; 16 voted-starter-DNP rows curated; Murray-NOP now resolves |
| Phase 1 reliability | `phase1_reliability.md` | FC-DRB 0.502, PAIR-DRTG 0.512, TOV-BLEED 0.665 (all pass r25>=0.50) |
| Phase 2 class + labels | `phase2_reference_class.md` | A: 17 strict / 58 loosened / 26 widened; B: 388; C: 116. All seeds accounted for |
| Phase 3 predictive validity | `phase3_synthesis.md` | See wire tally below |
| AVAIL-PACE derivation | `phase3_avail_pace_derivation.md` | Baseline-conditioned thresholds; cushion effect confirmed |
| Jaden feasibility | `../board/docs/jaden_markers_feasibility.md` | Every marker computable; nothing struck |
| Board spec | `../board/docs/board_spec.md` v2.0 | Consolidated to source of truth |

## The wire tally (Phase 3 outcome)

| Metric | Reliability | Predictive validity | Verdict |
|---|---|---|---|
| **AVAIL-PACE** | exempt | Spearman 0.77, sign 0.77, n=388 | **Clears every gate.** Wire, ARM-G. Threshold derived. |
| **FC-DRB** | 0.502 pass | Spearman 0.617, n=82, but **sign 0.659 < 0.70** | Reliability + strong Spearman; misses the sign gate |
| PAIR-DRTG | 0.512 pass | YA1 underpowered (n=6), hypothesis not confirmed | Demote to dashboard (per the rule); G6 not built |
| TOV-BLEED | 0.665 pass | same n~6 co-star class | Dashboard |
| SPACE-ANT | no curve | — | Dashboard (G4) |

The honest reading: only the two large reference classes (Scenario B availability, n=388; Scenario C succession, n=82) can currently support wires. The co-star class (Scenario A, ~6-17) is too small to promote its metrics from prior to verdict, exactly as the spec warned ("class ~twelve, prior not verdict"). This points toward **one to two binding wires** covering two different arms (ARM-G, ARM-B), not four.

## Decisions waiting for you at the Phase 4 stop

1. **SIGN_GATE for FC-DRB.** FC-DRB has a well-powered Spearman (0.617, n=82) but sign consistency 0.659, just under the 0.70 gate. SIGN_GATE is marked TUNE. I did **not** retune it to pass (rigor discipline). Your call whether a 0.70 binary-sign bar is the right screen for a strong-Spearman metric, which decides whether FC-DRB becomes the second wire.
2. **Final wire selection** (Phase 4 proper): how many wires, which arms, and the TRIPWIRES.md draft. My read is AVAIL-PACE certainly; FC-DRB if the sign gate is relaxed or judged non-binding here; PAIR-DRTG/TOV-BLEED to the dashboard pending a larger co-star class.
3. **Carry-forwards** (`carryforwards.md`): the lamelo/ availability reconciliation change set (out of tripwire scope, logged for you); the Pendergraph/Ayres alias to fitengine; G2/G3 into Phase 2 prep; the availability posterior scheduled on the board.
4. **Jaden**: markers all feasible; the calibration class (markers section 5) is queued, not started, and gets scoped after this review.

## The AVAIL-PACE wire, ready for TRIPWIRES.md

> Trip toward ARM-G if LaMelo is available in 12 or fewer of the Wolves' first 20 games at R1 (advisory) and 23 or fewer of the first 37 at R2 (binding). These sit just above his 47-game-baseline plan pace, so the wire stands down only if he outperforms his own history. At a 63-game plan the reads are 15 and 31. Derived from 388 comparable arrivals, no fitted model, exact count.

## Reproduce

All scripts in `scripts/`; run order documented per deliverable. Panel cache (`data/stints_panel/`) is gitignored; rebuild with `build_stint_panel.py`. Everything else (case tables, scorecards, honors, mapping outputs) is committed under `data/`.
