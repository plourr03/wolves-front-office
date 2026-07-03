# Session log — F1 close-out + F2-F5 groundwork (2026-07-02 night into 2026-07-03)

Machine: laptop (bobbys-lenovo), picked up from the desktop mid-panel per
PICKUP.md. Full ruling record in docs/decisions.md; this is the narrative.

## Environment (task 1)

- Python 3.13.14 installed via winget (laptop had only Anaconda 3.12); venv
  rebuilt on 3.13 from requirements.lock. Warehouse reachable at the
  Tailscale address.
- AM-1 fence false alarm on first pytest: core.autocrlf=true smudged
  postmortem/lib to CRLF, and the fence hashes raw bytes. Committed blobs
  verified byte-identical to the pins (NOT drift). Fixed with a repo
  .gitattributes marking postmortem/lib -text; all 13 contract tests green.
  Commit 8b6fc807.

## F1 repair to close (tasks 2-5)

Two more resolver rounds beyond the desktop's bench_fix4, driven by
panel-scale quarantine buckets each verified against warehouse source
before coding:

- Round 1 (bench_fix5, commit 69de9000): mcclellan->mac, zhou->qi aliases;
  comma folding; multi-token surname roster keys; hyphenated-surname parts;
  truncated 'SUB: X FOR'; NaN sub_type guards at the rebound tally and FT
  parse. 208-game bench stayed 208/208.
- Round 2 (bench_fix6, commit 30744148): umlaut transliteration variants
  (Poeltl), yongxi->cui, evidence-based roster-stage eliminations (exact-
  PBP-form minimal-uniqueness + seconds-precise played column), leading-
  token fallback (Louzada Silva). Caught a SILENT self-sub bug ('SUB:
  Williams Jr. FOR Williams' returned the leaving player) -> unconditional
  out-pid elimination. Because the bug corrupted non-quarantined games, the
  full panel was re-run under final code from one clean state.

G1 VERDICT: GREEN (commit 6ad459d7). Final-code panel, both criteria, both
strata:
- primary seconds-precise recon 99.85% pooled (legacy 99.84%, live 99.98%)
- secondary truncation-aware 99.86%
- quarantine 0.0064% (1 by-design unrecoverable-sub game)
- zero non-5v5 stints across 818,713 (lineup-validity gate)
- possession parity exact; coverage complete.

Tail census (src.stints.tail_census, all 142 imperfect games): 140 diffuse
attribution_residual (0.139% of player-games, worst-10 games hold ~19% of
the mass), 1 reference-incomplete (2025-26 warehouse boxscore gap, not our
error), 1 phantom-OT (cosmetic). ZERO games classified floor_count_error;
ZERO starter mismatches; residuals span both formats and all 13 eras ->
the two nameable systematic causes (starter derivation, floor-count) are
ruled out. Conclusion: data-quality floor of possession-level floor
reconstruction (sub-level timing/attribution), not a fixable disease.
Negligible RAPM impact. Deep per-game root-cause verification queued.

D6 DuckDB load (src.etl.load_duckdb -> fitengine.duckdb, gitignored as a
rebuildable store): games/stints/quarantine/reconciliation, 818,713 stints,
0 non-5v5, complete cache coverage. Season counts match the R1 census
(2019-20 and 2020-21 correctly short).

## F2-F5 groundwork (tasks 6-10, code written + unit-tested)

Committed in 61dc2ed7 (before the panel re-run), then RAPM refined:

- Layer 1a RAPM (src/models/rapm.py): per-season O/D ridge from the
  possession cache, two-stage box+aged-prior blend, analytical GCV alpha
  frozen on dev seasons (rewritten to compute from the p x p Gram, no
  n x p densification -- avoids a ~1.2GB/season memory blowup), 200-game-
  block bootstrap SEs, A1 covariance blocks, G2 report generator.
- RAPM foundation fix: the stint cache is the WRONG grain for RAPM
  (per-team stints do not share clock boundaries, so a matchup self-join
  is not 1:1 -- caught at 45,071 vs 6,497 rows). Added
  src/models/build_possessions.py: a possession cache with paired
  10-player floors + garbage flag; rapm.load_matchups reads it.
- F3: player_features (7.3), feature_regime + leakage-safe FeatureService
  with the planted-canary test, A2 aging_fit (Model C basis, synthetic-
  tested, refuses real data until skill vectors exist).
- F4: lineup_obs (7.2) with A3 leverage-basis columns, gbm_floor,
  set_attention; smoke tests prove floor and primary both beat the
  additive baseline on planted synergy and invariance survives training.
- F5: transaction_universe mechanical builder; sealed window (2021-22+)
  hard-filtered before any artifact, tested.
- Instruments: src/stints/diagnose.py (per-game error localizer),
  src/stints/tail_census.py, src/validation/report.py.

37 tests green (13 contract + 24 new).

## In flight at this log

Possession cache build (src.models.build_possessions, 16 workers) running;
F2 RAPM fires on completion. Then: G2 face-validity (workflow), player_
features, lineup_obs, transaction universe (dev only), attribution-residual
deep verification, validation report regen.
