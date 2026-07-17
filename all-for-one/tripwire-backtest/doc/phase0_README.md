# Phase 0: results index

Tripwire backtest, Phase 0. Complete 2026-07-17. Executor: Claude Code against `nba_warehouse`.

Phase 0 answers one question: can the spec's section 7 queries actually run, and if not, what does it cost to make them run. Phases 1 through 4 have not run.

## Headline

The schema maps, the reference class resolves, and stint grain reaches back to 2010-11. But three of the spec's named dependencies do not exist as assumed, and one of its core queries has a silent scale bug. None of this is fatal; all of it is now costed.

**Deliverables:**

| Doc | What it answers |
|---|---|
| [phase0_coverage_report.md](phase0_coverage_report.md) | Schema map, coverage 2009-10 to 2025-26, null audits, the four spec-query corrections. |
| [phase0_stint_trust_spike.md](phase0_stint_trust_spike.md) | Stint reconstruction feasibility, 930 games, trust boundary back to 2010-11. |
| [phase0_gap_register.md](phase0_gap_register.md) | G1-G6: what is missing, what it blocks, effort to fix. |
| [phase0_availability_reconciliation.md](phase0_availability_reconciliation.md) | The three inconsistent LaMelo availability numbers and their consumers. |
| [phase0_avail_pace_redefinition.md](phase0_avail_pace_redefinition.md) | AVAIL-PACE onto the warehouse; build spec for a real posterior (board, not backtest). |
| [phase0_rename_map.md](phase0_rename_map.md) | Placeholder to real, per-query parse status, seed resolution, revised acceptance bar. |

## The four things that change the spec now

1. **usg_pct scale bug (coverage report).** `usg_pct >= 28.0` matches zero rows; the column is a fraction. Correct to `>= 0.28`. Silent, not loud: it returns an empty class rather than erroring.
2. **AVAIL-PACE retired from pick2033 (4b).** The availability posterior it read never existed (name collision with draft-slot posteriors). Redefined onto a warehouse baseline plus the Scenario B reference-class mapping, which is stronger for a pre-commitment anyway.
3. **SPACE-ANT drops to dashboard-only (G4).** No wide-open/defender-distance data exists anywhere; the reliability curve it would be gated on cannot be computed.
4. **Honors must be ingested before Phase 2 (G1).** No award data in the warehouse; the Scenario A incumbent filter has no source. Half a day, B-Ref, ~450 rows.

## Two decisions waiting on your ruling

1. **Stint spike acceptance threshold.** You pinned 0.95/0.02; I argued 0.995/0.005 with a 0.95-0.995 amber band. The spike produced the deciding case: 2011-12 passes clean at 0.95 but goes amber at 0.995, and the amber investigation surfaces a specific fixable finding (one missing name alias, Pendergraph/Ayres) that the looser bar buries. Detail in the spike doc.

2. **The fitengine seal (plan governance Q1).** Half the Scenario A class lives inside fitengine's F5-sealed window (2021-22+). Mechanical stint reconstruction there is fine; consuming fitengine's fitted artifacts there is your call. Cheaper to rule now than after Phase 2.

Plus one flag, not a decision: the master plan board that section 10 says these wires feed does not exist yet as a spec. See plan governance Q2.

## Next

Phase 0 stops here for review. The recommended Phase 0.5, if greenlit, is the honors ingest (G1), since it is the only hard blocker for Phase 2 and the cheapest high-value gap. The section 3 era window is confirmed feasible on its early end and should be amended (or not) once you have ruled on the threshold and the seal.
