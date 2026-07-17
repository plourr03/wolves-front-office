# Stint Trust Spike: Sealed-Season Addendum

Tripwire backtest, per Ruling 2c (2026-07-17). Run 2026-07-17. Scorecard: `data/sealed_addendum_scorecard.parquet`. Script: `run_sealed_addendum.py`. Sample RNG seed 20260717.

## Why this exists

Ruling 2 split the fitengine seal by artifact type. Raw warehouse data and mechanical stint reconstruction on sealed seasons (2021-22 onward) are in scope for the backtest (2a), because half the Scenario A reference class lives there and the class does not exist otherwise. But Ruling 2c requires that before Phase 2 trusts stint features on those seasons, the spike is extended mechanically onto them: 20 games per sealed season-case, same scorecard, load-bearing metrics only, same thresholds and amber process.

This is that extension. It is **mechanical reconstruction only** (it fits nothing) and **bench/spike-class evidence** (not a G-gate claim; those come from fitengine's full panel). It reuses `reconcile_game` unmodified, touches no pinned code, and writes no cache.

## Sample

160 games, 20 per sealed reference-class case:

| Case | Season | yy |
|---|---|---|
| Harden to PHI [A] | 2021-22 | 21 |
| Mitchell to CLE [A] | 2022-23 | 22 |
| Lillard to MIL [A] | 2023-24 | 23 |
| Beal to PHX [A] | 2023-24 | 23 |
| Fox to SAS [A] | 2024-25 | 24 |
| Doncic to LAL / Lakers post-Davis [A/C] | 2024-25 | 24 |
| Murray to NOP [A] | 2024-25 | 24 |
| Bucks post-Lopez [C] | 2025-26 | 25 |

Coverage spans every sealed season yy21 through yy25. **2025-26 (yy25) is included deliberately: it is the mixed cdn/stats_api format season and it is LaMelo's season, so it is the single most important season to verify.**

## Result: uniformly green

| Season | Games | Player-games | Quarantined | recon_TRUE_0.5 | Verdict |
|---|---|---|---|---|---|
| 2021-22 | 20 | 407 | 0 | 1.0000 | GREEN |
| 2022-23 | 20 | 396 | 0 | 1.0000 | GREEN |
| 2023-24 | 40 | 862 | 0 | 1.0000 | GREEN |
| 2024-25 | 60 | 1,266 | 0 | 1.0000 | GREEN |
| 2025-26 | 20 | 469 | 0 | 1.0000 | GREEN |
| **Pooled** | **160** | **3,400** | **0** | **1.0000** | **GREEN** |

By format: 147 legacy-format games and 13 live-format games (the live games are in 2025-26, the mixed season), both at recon 1.0000. Every one of the eight cases scores 1.0000 individually.

## Verdict

**Sealed-season stint reconstruction is trustworthy.** Every sealed season passes the ruled 0.995 / 0.005 bar with room to spare, at the perfect end of the scale, with zero quarantines across 3,400 player-games. No season enters the amber band. In particular, 2025-26 (LaMelo's mixed-format season) reconstructs cleanly on both format strata, which is the result the whole tripwire project most needed to be true.

Phase 2 may compute descriptive box and stint aggregates on sealed seasons (Ruling 2a). Per Ruling 2b, only fitted artifacts trained on pre-seal data (the frozen 2026-07-06 vectors) may be applied out of sample to these seasons, and no metric is fit, tuned, or threshold-selected on them. This addendum verifies the mechanical reconstruction those descriptive aggregates rest on; it does not authorize any fitting.

## Scope note

This is a sample, so by the house rule it cannot issue a gate verdict, only feasibility evidence. It is logged as a spike addendum, not a gate claim, exactly as the earlier 2010-21 spike was.
