# Decision record — fitengine

## 2026-07-02 — Plan approval: Section 14 rulings (Bobby, verbatim; frozen at F0)

1. Backtest inclusion: "Lower to 1,000 possessions, keep 3+ lineups and
   top-100 minutes. Rationale on record: reduces survivorship-of-
   successful-fits selection in the test population. Report the sealed
   results with a 1,500+ sensitivity cut alongside, so threshold dependence
   is visible."
2. K set: {6, 8, 10} as proposed.
3. Replacement archetype: positional archetype means at the 25th percentile
   of minutes-weighted impact.
4. Format/falsifiability: "Single piece, Luka replay mid-piece, board as
   closer, carousel after. Two pre-declared checkpoints with fixed roles: a
   25-game check-in in December, explicitly labeled descriptive and
   underpowered, no pass/fail language permitted; the formal graded
   checkpoint at the All-Star break with metrics stated in the flagship
   itself."

## 2026-07-02 — Plan approval amendments AM-1..AM-6 (Bobby, verbatim)

AM-1 (the fence): postmortem/lib is a LIVE library serving another project.
Frozen imports must pin a git commit hash of postmortem/lib recorded in
config, verified at import time, not just sys.path + fixture tests.
Fixtures catch drift after it bites; the hash refuses it. If postmortem
needs to move forward mid-build, fitengine vendors a snapshot at the pinned
hash (one memo, no silent divergence).
AM-2 (2013-14 ruling, pre-declared): attempt the backfill via the
nba-warehouse sibling pipeline, budget ONE session-day. If unrecovered,
panel starts 2014-15 by memo, and Layer 1a priors for 2014-15 use box
composites only. Do not let a 2h estimate become a week.
AM-3 (G1 denominator honesty): the 99.5% minutes-reconciliation rate is
computed over ALL player-games including quarantined periods' games, not
over post-quarantine survivors.
AM-4 (format-boundary stratification): every G1 metric reports split by PBP
format era alongside pooled. The 2025-26 format is one season deep in the
legacy shim, it is the season LaMelo's vectors come from, and a
format-specific parsing defect there poisons the headline query
specifically.
AM-5 (backfill provenance): backfilled rows carry a source tag and appear
as a G1 stratum too.
AM-6 (record hygiene): full F0-F6 session table confirmed intact in the
committed plan.

## 2026-07-02 — Riders R1/R2 (Bobby, verbatim; final approval)

R1: F0 coverage_audit expands from the 2013-14 gap check to full
game-universe classification by game-id type prefix. The ~30.6k count is
~2x the true NBA regular+playoff universe (~16.8k), so preseason / G-League
/ summer-league rows are likely present. Training filter = explicit
include-list (regular season IDs; playoffs flagged), asserted in a schema
test, not assumed absent. Reconcile the audited count against the
3,939-parquet 2023-26 cache as the known-good reference.
R2: F0's DoD "freezes ratified" is a named human checkpoint: session ends
by presenting backtest_protocol.yaml, redundancy_def.yaml, and the
decisions.md entries for Bobby's read-and-ratify before F1 touches anything
downstream. Everything after that ratification runs auto.

## 2026-07-02 — F0 execution outcomes

**Layer-0 restructure (recorded):** warehouse-first; the spec's 15-25h
nba_api pull is replaced by SQL against nba.nba_play_by_play. nba_client
demoted to gap-filler (per-period boxscore repairs at F1; future seasons).
DuckDB holds derived grains only; the 14.3M-row events table stays in
Postgres (amends the spec's warehouse line).

**R1 audit results:** the in-window universe is 16,836 games, NOT ~30.6k
(the earlier figure counted the full 1997-2026 table). Pollution is real
but small and now filtered by tested include-list: 66 preseason, 6
all-star, 5 play-in, 1 unknown '006' game. Train-eligible: 15,669
regular-season games. Cache reconciliation: 3,939 cache vs 3,941 warehouse
(warehouse is the superset; 0 cache-only).

**AM-2 resolution — the 2013-14 gap NEVER EXISTED.** Under the 002 filter,
2013-14 has exactly 1,230/1,230 regular-season games; the exploration
agent's "89 games" was a query artifact. Backfill cancelled; budget spent:
zero. Every season 2013-14 .. 2025-26 is complete (2019-20: 1,059 incl.
bubble seeding games; 2020-21: 1,080). The 3 missing 2025-26 playoff games
remain logged (playoffs excluded from training).

**AM-1 implemented:** config/pinned_lib.yaml pins git blob hashes of the
four postmortem/lib files (pinned at repo commit 1e56b4c4);
src/adapters/postmortem_lib.py verifies at import and refuses on drift
(tested, including the refusal path). Golden possession fixtures: 10 games
spanning 2013-14 .. 2025-26, both formats, byte-stable reproduction tested.

**GBM choice:** LightGBM 4.6.0 (Windows py3.13 wheel smoke-passed; sklearn
HistGradientBoosting remains the same-wrapper fallback). torch 2.12.1+cpu
smoke-passed (MultiheadAttention). Stack: jax 0.10.2 / numpyro per
pick2033 D4, no re-litigation.

**Meta-note (Bobby's wording, also entered in house standards):** audit
existing assets before accepting any spec's data-acquisition estimate —
exploration-before-planning deleted this project's long pole; the second
time this workflow caught the expensive assumption early.

**Schedule posture:** reclaimed weeks are BANKED, not spent.

## 2026-07-02 — R2 VERDICT (Bobby, verbatim): RATIFIED conditional on amendments 1-4

R2 VERDICT: RATIFIED, conditional on amendments 1-4 landing before F1
touches anything downstream. 5-6 are logged, non-blocking.
1. backtest_protocol.yaml precision (keeps "mechanical" mechanical):
   (a) top_minutes_rank_100 = league-wide total minutes in the season
       PRECEDING the transaction;
   (b) realized evaluation window = remainder of the transaction season
       for midseason moves, the following season for offseason moves;
       min_possessions and min_distinct_lineups counted within that
       window only;
   (c) significance clustering unit = transaction case.
2. redundancy_def.yaml precision:
   (a) formula with explicit subscripts:
       f(C+i+j) - f(C+i+r_j) - f(C+r_i+j) + f(C+r_i+r_j),
       r_i/r_j = archetypes at i's and j's positions;
   (b) replacement archetype = minutes-weighted MEAN VECTOR of players
       in the 20th-30th percentile impact band at the position, dev
       seasons only (not per-dimension percentiles).
3. model_params.yaml: conformal_holdout_season must be disjoint from
   coverage-gated seasons. Set conformal calibration = 2019; G3
   coverage gate evaluates 2020 and 2021 only. As configured the gate
   is circular.
4. pinned_artifacts: record content hashes (or cache keys) for the
   pick2033 posteriors and warehouse.duckdb alongside the paths, per
   D6's own promise. Verify at load like the AM-1 fence.
5. (Log) Play-in census: ~37 expected since 2020, 5 found. Reconcile;
   log absentees like the 3 playoff games. Excluded from training
   either way.
6. (Log) G3 reports per-season, not only pooled: two of three holdout
   targets are pandemic-shaped seasons and an anomaly there should be
   visible, not averaged away.

### Amendments landed same session (all four confirmed in committed configs)
1a/1b/1c -> backtest_protocol.yaml (preceding-season minutes basis,
realized-window rules, transaction-case clustering). 2a/2b ->
redundancy_def.yaml (subscripted formula; 20th-30th band mean vector).
3 -> model_params.yaml (conformal 2019; coverage gate 2020+2021 only;
per-season G3 reporting noted per log-item 6). 4 ->
src/adapters/pinned_artifacts.py verifying sha256 pins at load; the
CONVERGED v1.1 aging posterior pinned explicitly (its unconverged v1
sibling at r_hat 1.60 must never load).
Log-item 5 reconciled: only 2025-26's five play-in games exist under the
005 prefix; 2021-2025 play-ins (~30) were never ingested by the warehouse
backfill (RS+PO scope). Logged as absentees; excluded from training.
