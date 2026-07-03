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

## F2 through F5 landed (continued)

- Possession cache built: 15,668 games, 3,020,898 possessions (garbage
  flagged per the stint-builder rule). Gitignored as a rebuildable
  intermediate.
- F2 RAPM ran full: GCV alpha frozen at 2000 (dev seasons only), 13
  seasons fit, 200-block bootstrap, A1 covariance blocks. G2 GREEN both
  gates -- YoY O/D correlations all 12 pairs in the 0.50-0.75 band, face
  validity exact (2015-16 Kawhi/Curry/Draymond, 2024-25 Jokic/SGA/Giannis).
  Commit 9ed1df28. Layer 1b factor rows remain F3-pending.
- player_features (6,936 rows) built with RAPM joined; a warehouse
  Decimal->float coercion fixed. DATA NOTE FOR BOBBY: the warehouse has NO
  2020-21 tracking rows (2019-20 jumps to 2021-22); regime mask flags it,
  pending an ingest ruling.
- lineup_obs: the SAME wrong-grain bug RAPM had (stint self-join, 7x
  undercount) fixed -- now sourced from the possession cache, 770,369 rows,
  2,969,298 possessions, team context via the lineup->team join. A3
  leverage weighting deferred to Layer 2 fit time (frozen adapter taggers).
- dev_transaction_universe: 174 mechanical cases, 2015-16..2020-21 ONLY
  (sealed asserted absent), face-valid (KD->GSW, Kawhi->LAC, etc.).
- validation report regenerated (G1 + G2 green).
- Two grain bugs (RAPM, lineup_obs) both traced to the same root: per-team
  stints do not share clock boundaries, so a matchup self-join is not 1:1.
  The possession cache is now the canonical matchup grain for both layers.

Commits this stretch: 6ad459d7 (F1 closed), d489a7cf (GCV), 9ed1df28 (G2),
c1687276 (F3/F4/F5 builds), plus the diagnose trace instrument.

## In flight at this log

Tail-residual root-cause workflow (13 stratified games, one trace agent
each + synthesis) running to adversarially verify the census claim that
the 140-game attribution tail is diffuse data-floor noise, not a fixable
systematic bug. Verdict lands in decisions.md on completion.

## Tail root-cause workflow + fix propagation (session close)

The adversarial tail workflow (13 trace agents + synthesis) OVERTURNED the
census "diffuse" call: 10/13 sampled games traced to one bug in
_identify_period_start_floors (technical fouls / ejections by non-floor
players counted as on-floor appearances, seating a phantom into the
period-start five). validate_floor_state already skipped that event class;
the seeder didn't. Fix: shared _implies_floor_presence predicate
(commit 0927e194).

Propagated through the whole pipeline (one combined panel re-run writing
stints+possessions+scorecard, D6 reload, RAPM re-fit with alpha frozen,
feature rebuilds). Results (commit b47d5d82):
- G1 pooled recon 99.8476% -> 99.9318%, live 99.98% -> 100.00%, failing
  player-games 507 -> 227 (halved), games<99% 141 -> 63.
- Tail: 140 attribution-residual games -> 61; the technical-foul class
  (~79 games) eliminated.
- G2 unchanged green (YoY all in band, alpha still 2000, face validity
  intact).

Memo'd residuals (not fixed, not systematic at scale): quiet-starter period
seatings, 1 same-surname IN-resolution, irreducible data-floor games, 1
reference-incomplete 2025-26 game, 1 phantom-OT.

## Final overnight state

- G1 GREEN (improved), F1 closed. G2 GREEN (RAPM rows). Layer 1b factor
  rows F3-pending.
- Full F2-F5 code written, unit/smoke-tested (35 tests green), and the
  real data builds run: RAPM (13 seasons), player_features (6,936),
  lineup_obs (770k), dev transaction universe (174 cases, sealed absent).
- Sealed 2022-26 backtest window untouched and unenumerated throughout.
- Caches (stints, possessions), the DuckDB store, and large feature
  parquets are gitignored as rebuildable; scorecards, RAPM parquets, G2
  report, validation report, dev universe, and all decisions committed.
- Open for the next session: F3 proper (Layer 1b factor model, K selection
  on dev seasons -- the K CHOICE is presented to Bobby, not frozen
  overnight), the A2 aging fit once skill vectors exist, and the memo'd
  reconstruction residuals if a further pass is wanted (all sub-0.5% of
  player-games).
