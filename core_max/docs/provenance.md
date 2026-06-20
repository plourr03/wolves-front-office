# Phase 1 Data Provenance

Two data sources, pinned, with the rationale beside them so Phase 3 does not have to
rederive it from memory.

## Sources

- **1a (established-player distributions): `offseason/data/player_value.csv`, built
  2026-06-13.** Point estimate `consensus_net`, uncertainty `net_sd`. Not regenerated.
- **1b (rim correction) and 1c (held-out RAPM coverage): frozen warehouse snapshot
  `core_max/data_frozen/wh_0e1a90b850e6ea3b/` (label 2026-06-20).** Content-addressed.
  1b and 1c both load through `core_max/data_pull/frozen.py`, which re-hashes on read and
  asserts the same snapshot id, so they cannot drift apart. Holds the 3-season rim-defense
  signals and box features for the full / train(2023,2024) / holdout(2025) windows.

## Why two sources is fine (the static seam is closed)

The behavior-preserving refactor gate (`core_max/tests/diff_rapm_refactor.py`) showed the
warehouse box features drifted slightly between 2026-06-13 and now. The consequences are
bounded and the consistency that matters holds:
- Ridge posterior SDs depend on the design matrix and alpha, NOT the box-prior mean, so
  `net_sd` is byte-IDENTICAL across both snapshots. 1c calibrates an inflation factor on
  `net_sd`, so the factor transfers to 1a's file exactly.
- The point-estimate drift is mean 0.001 (max 0.07), negligible for team strength.
- Regenerating `player_value.csv` to erase a 0.001 drift would cost a full enrichment
  re-run and strip the BBR/consensus columns 1a needs. Bad trade.

## Static vs dynamic seam

- Static seam (06-13 file vs current warehouse): handled above.
- Dynamic seam (a second warehouse update landing mid-build, between 1b and 1c): closed by
  the frozen snapshot. Both steps read one content-addressed snapshot; a later warehouse
  change cannot move them apart, and a mutated snapshot fails the load-time hash check.
