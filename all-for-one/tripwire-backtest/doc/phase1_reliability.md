# Phase 1: Reliability Curves

Tripwire backtest, Phase 1. Produced 2026-07-17 on the complete stint panel (13,208 of 13,209 games; the one failure is game 0021500624, fitengine's single known-unrecoverable quarantine, the `'SUB: FOR Howard'` case where the entering player's name is absent from the feed). Scripts: `compute_phase1_reliability.py`, `compute_pair_drtg_reliability.py`. Panel built by `build_stint_panel.py`.

## Method

For each candidate metric, across all team-seasons 2014-15 through 2024-25 (330 team-seasons, not just the reference class, since stabilization is a property of the metric), split each season at game N, compute the metric on the first N games and the rest, and correlate early vs rest across seasons. Gate: r(25) >= 0.50 (RELIABILITY_GATE). Garbage-time stints excluded.

## Results

| Metric | r(10) | r(15) | r(20) | r(25) | r(30) | Gate (r25 >= 0.50) |
|---|---|---|---|---|---|---|
| FC-DRB (anchor-off DRB proxy) | 0.356 | 0.412 | 0.474 | **0.502** | 0.527 | **PASS** (marginal) |
| PAIR-DRTG (raw, 350-poss floor) | — | — | — | **0.512** | — | **PASS** (marginal) |
| TOV-BLEED (team on-floor TOV%) | 0.578 | 0.634 | 0.665 | **0.665** | 0.670 | **PASS** |
| AVAIL-PACE | exact count | | | | | EXEMPT |
| SPACE-ANT | not computable | | | | | N/A (G4) |

All three stint metrics clear the 0.50 gate at r(25), two of them marginally.

### PAIR-DRTG: raw pair-level, at the possession floor

The spec warns that raw pair defensive rating is slow to stabilize and only the fitengine-shrunk version is usable at R1. So PAIR-DRTG was measured two ways:

- **Team-DRTG ceiling** (the upper bound, defensive rating stabilizes well at the team level): r(25) = 0.743.
- **Raw pair-level DRTG** for qualifying pairs (top-10-minute players, shared-floor DRTG early vs rest), by shared-possession floor:

| shared def poss floor | pairs | r(25) |
|---|---|---|
| 200 | 9,332 | 0.448 |
| **350 (the R1 spec floor)** | 6,314 | **0.512** |
| 500 | 4,099 | 0.558 |

At the spec's 350-possession R1 floor, raw PAIR-DRTG r(25) = 0.512, clearing the gate. So **PAIR-DRTG passes reliability on the raw metric without needing the G6 shrinkage.** Per the pre-staged decision rule, it proceeds as a wire candidate into Phase 3. (Whether it survives Phase 3 is a separate question, answered in `phase3_synthesis.md`: it does not, on predictive-validity grounds.)

### FC-DRB proxy note

FC-DRB uses a defensive-rebound proxy from the stint parquet: `1 - oreb_def / (fga_def - fgm_def)`, opponent offensive rebounds per opponent missed field goal, aggregated over anchor-off stints (anchor = the team's max-minute center that season). The parquet has no direct DRB column, so this is the best available proxy; it is a rate, adequate for a reliability curve (which cares about stability) and for a percentile wire. r(25) = 0.502 is a marginal pass and should be read as such.

### TOV-BLEED scope note

Only the turnover half of TOV-BLEED is measured here (team offensive turnovers per 100 possessions, which stabilizes at r(25) = 0.665). The other half, opponent points off turnovers, requires PBP transition-sequence tagging that the stint parquet does not carry; it is flagged, not computed. The wire's reliability rests on the TOV% half, which passes.

## Handoff to Phase 3

All three stint metrics are reliability-eligible. Reliability is necessary but not sufficient: a metric must also predict a decision-relevant outcome (Phase 3) and clear the sign-consistency gate before it can be wired. See `phase3_synthesis.md` for the predictive-validity results, where the small co-star class (Scenario A) proves the binding constraint for PAIR-DRTG and TOV-BLEED, and FC-DRB's sign consistency lands just under the gate.
