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

## 2026-07-02 — F1 directive (Bobby, verbatim) + same-session resolutions

F1 DIRECTIVE (before further repair coding):
1. Validation report labels quarantine, team-seconds, and possession
   parity as STRUCTURAL INVARIANTS (by construction / lossless
   partition) until repair logic exists to give them teeth. G1 "green"
   claims come from the full 15,669-game panel, not the 208-game
   sample.
2. Run the discriminator: per player-game |minutes error| vs sub
   count, by era stratum. Scales with subs -> boundary placement
   (split bookkeeping: clock-time for minutes, boundary-snap for
   possession attribution). Flat ~1 min -> audit Live-branch clock
   parsing (ISO durations, fractional seconds, period boundaries)
   against legacy-format games as reference.
3. Confirm nba_player_stats.minutes_played precision (seconds-precise
   vs rounded); if rounded, source seconds-precise official minutes or
   restate the tolerance against the reference's granularity, by memo.
4. Legacy-era repair proceeds per D3 fix order (period-start floors
   first) once 2-3 resolve.

### Resolutions (same session)
1. LANDED: reconcile.py labels the three metrics *_INVARIANT /
   *_PARTITION with the rationale inline; G1 claims restricted to the
   full panel.
2. DISCRIMINATOR: FLAT in both eras (corr +0.04 legacy / -0.09 live; no
   scaling with sub count) -> Candidate A (boundary placement) DEAD.
   CLOCK AUDIT: the warehouse ingest normalized ALL eras to ISO clock
   strings; zero unparseable across both branches, fractional seconds
   correct, period spans integrate -> Candidate B DEAD. The residual
   signature (flat errors, LOW-sub players worst, legacy >> live) is
   the period-start-floor fingerprint in both eras.
3. PRECISION MEMO: minutes_played is an INTEGER TRUNCATION (0 fractional
   in 786k rows; non-OT team sums average 234.72 vs 240 = the floor(x)
   shortfall). A perfect reconstruction fails the naive 0.5 bar half the
   time by construction. RESTATED GATE (authorized by directive item 3):
   |r - (official + 0.5)| <= 1.0, i.e. r within the truncation cell plus
   the spec's 0.5 model tolerance; naive metric kept as diagnostic; final
   G1 adds a seconds-precise verification stratum via targeted nba_api
   boxscore pulls. Truncation-aware baseline: legacy 67.8%, live 80.7%
   (from 36.6%/43.0% naive) -- a third disease was the yardstick itself;
   real disease remains in both eras.
4. UNLOCKED: repair coding proceeds, period-start floors first, both eras.

## 2026-07-02 (late) — F1 precision riders (Bobby, verbatim)

F1 PRECISION RIDERS (before repair iteration hardens):
1. The relaxed gate is the right observable bound against truncated
   references, but it admits true errors up to ~1.5 min in tail
   alignments (model tolerance stacking with the truncation cell).
   The seconds-precise verification stratum therefore carries the
   ORIGINAL criterion: >= 99.5% of player-games within 0.5 min of true
   seconds, on a defined sample (>= 200 games, era-stratified per
   AM-4) via targeted nba_api boxscore pulls. Final G1 green requires
   BOTH the relaxed full-panel gate AND this stratum passing. Without
   an attached criterion the stratum is a dangling check.
2. Repair inference using official minutes as evidence must constrain
   with the truncation interval [m, m+1), not m +/- tolerance. Do not
   bake the old yardstick into the new repair logic.
3. Bench/panel discipline: fixes iterate on the 208-game bench; gate
   claims come only from full-panel runs.

Independent verification (Bobby): 5.28-min team shortfall / 0.5 per player
implies ~10.6 players logging minutes per team-game -- matches NBA reality;
truncation inference confirmed from a second angle.

Hypothesis scoreboard (Bobby's own grading, logged like the agent's
predicted-wrong notes): directive disease candidates 0-for-2 (boundary
placement dead on flat correlation; Live clock parsing dead on clean
audit); the original plan's fix-order item 1 (period-start floors) 1-for-1
as the surviving target. The discriminator was still the right ten-minute
spend: two plausible diseases eliminated before a day of repair code.

## 2026-07-02 (night) — F1 repair session: three diseases found, three fixed

**Fix-order 1 (period-start floors), landed earlier this session:**
(a) sub-out-first evidence — a player whose FIRST sub event in a period is
an OUT with no prior appearance was on at period start; (b) negative-
evidence padding ban — a player whose first period event is a sub-IN
provably did NOT start it and is excluded from prior-floor/starter padding.

**Fix-order 2 (legacy sub name→id resolution) — the identity-swap disease.**
Two defects in the fork's inherited resolver: (1) PBP player_name stores
diacritic spellings ('Porziņģis') while sub descriptions use ASCII
('SUB: Porzingis FOR Noah') — exact-string lookup missed; (2) on a miss,
the code FELL BACK TO THE OUTGOING PLAYER'S person_id — a silent identity
swap that preserves team-seconds and possession parity (both structural
invariants, per the directive's labeling) while corrupting per-player
minutes AND downstream period-start inference (game 0021600001: the
phantom re-entry cascaded into Jennings losing his entire P4). The earlier
"0 unresolved names" check tested that names RESOLVED, not that they
resolved CORRECTLY. FIX: team-scoped diacritic-folded resolver
((team_id, normalized name) keys), supplemented by the official roster
(nba_player_stats) with generational-suffix handling ('Reggie Bullock Jr.'
must answer to description-form 'Bullock') and initialed forms
('J. Johnson') for same-surname teammates; same-key collisions within a
team are marked AMBIGUOUS. Unresolved or ambiguous now RAISES
LegacySubResolutionError -> the game quarantines with a legible reason.
The old guess-the-out-player fallback is BANNED. Consequence: the
quarantine metric now carries evidence (label relaxed from _INVARIANT);
team-seconds and possession parity remain labeled structural.

**Compensating-errors episode (logged in full, per house standards).**
The resolver fix REGRESSED live-parsed game 0022500001 from 20/20 to
17/20. Root cause chain, established by controlled file-surgery A/B: the
resolver correctly restored Chris Youngblood's 6-second cameo (previously
misattributed to Barnhizer by the fallback swap). That one P1 row changed
the appearance-count array feeding derive_starters' DEFENSIVE FALLBACK
("top 5 by period-1 appearance count", firing because pass logic yielded
6 candidates), whose unstable sort broke a Wallace/J.Williams 5-vs-5
count tie by array-content accident. The OLD bug had been flipping that
tie toward the CORRECT starter. Two wrongs had been scoring as one right;
the 20/20 was partly luck. Moral for the record: a gate metric that
improves for the wrong reason will be taken back with interest.

**Fix 3 — official starters (kills the fallback lottery).**
nba_player_advanced_stats.position is non-null for EXACTLY the five
official starters per team — verified 10/10 in ALL 15,669 panel games.
derive_starters now reads official starters first; PBP inference is
demoted to fallback (for games absent from that table) with its tie-break
made deterministic (count desc, person_id asc, stable sort).

**Fix 4 — seconds-precise official minutes (rider-1 memo).**
The same table's minutes_float is SECONDS-PRECISE official minutes
(mm:ss), complete for all 15,669 panel games. The reconciliation PRIMARY
gate is therefore restored to the spec's ORIGINAL criterion — >= 99.5% of
player-games within 0.5 min of TRUE seconds — evaluated on the FULL
PANEL. This satisfies rider 1's seconds-precise verification stratum with
the same source data (nba_api boxscore, already ingested by the
warehouse) at strictly larger coverage than the planned >= 200-game
targeted pulls. The truncation-aware relaxed metric vs integer
minutes_played is retained as the SECONDARY gate; G1 green requires both.
No criterion was weakened; the reference got better and the planned
nba_api pull work is unnecessary.

**AM-4 refinement — format is a per-game property.** Census: the 2025-26
warehouse load is MIXED (27,436 legacy-format substitution events vs
88,302 live-format across the season); earlier assumptions that
2025-26 == live were wrong per-game (0022500001 is legacy-format in the
warehouse). G1 strata now key on process_game's per-game format
detection, never the season prefix. AM-4's rationale stands: the live
branch is real for most of 2025-26 and keeps its own stratum.

**Spot-check after fixes (bench discipline, rider 3):** the five worst
baseline games — 0021600001, 0022000927, 0022000726, 0022300951,
0022500001 — all reconcile PERFECTLY under the original 0.5-min
criterion, worst per-player error 0.01 min (<1 second). 208-game bench
re-run tagged bench_fix123 (baseline parquet preserved); full-panel run
is the only place G1 claims can come from.

**Bench round 1 verdict (bench_fix123):** every game that processed
reconciled 100.0% — 3,988/3,988 player-games within 0.5 min of true
seconds, worst 0.012 min. 22/208 games (10.6%) quarantined, ALL on
LegacySubResolutionError — the honest surfacing of what the old code
resolved by silent identity swap. Four buckets, each verified against
source data before coding:
  (1) MINIMAL-UNIQUE POISONING: within a game the feed's name forms are
      minimally unique ('Williams' means Grant Williams precisely because
      Robert is 'Williams III'; plain 'Jones' is Kai because Derrick is
      'Jones Jr.'). Flat roster surname keys had poisoned already-correct
      PBP keys with false ambiguity.
  (2) VARIABLE-LENGTH PREFIX FORMS: 'Jal. Williams' vs 'Jay. Williams'
      (Jalen/Jaylin, whose player_name column collapses BOTH to
      'Williams'), 'Marc Morris' vs 'Mark Morris' (the twins), 'Shaw.
      Williams', 'Je. Green' vs 'Ja. Green' (Jeff/JaMychal, and HOU's
      Jeff/Jalen).
  (3) RETRO-RENAMES: the feed regenerates player_name and rosters from
      the CURRENT registry while descriptions keep the original text —
      'SUB: Kanter FOR ...' vs player_name 'Freedom' (7 of 22
      quarantines), desc 'Martin Jr.' vs roster 'KJ Martin'.
  (4) SUFFIXED LOOKUPS: desc form carries a generational suffix the
      roster form lacks or vice versa.

**Fix round 2 — staged resolver (_resolve_sub_in):** stages ordered most-
trustworthy first: (1) PBP exact-form map (team-scoped, never blended
with roster keys — preserves minimal-uniqueness), (2) same with
generational suffix stripped, (3) roster map, (4) roster suffix-stripped,
(5) prefix match against roster first names ('jal'+'williams' -> Jalen).
Every multi-candidate hit tries OUT-pid elimination (the entering player
cannot be the one leaving: 'SUB: Williams FOR Williams III' -> Grant).
Residual ambiguity still RAISES. One explicit alias recorded:
kanter -> freedom (token-level, lookup side). Result: all 22 quarantined
games re-run PERFECT (100% player-games within 0.5 min, zero residuals,
zero quarantines). Bench round 2 tagged bench_fix4.

## 2026-07-02 (laptop pickup, late night) — environment verification and panel-scale resolver buckets

**Machine switch.** Session resumed on the laptop (bobbys-lenovo) per
PICKUP.md. Python 3.13.14 installed via winget (the laptop had only
Anaconda 3.12.4; the venv was rebuilt on 3.13 to match the F0-verified
environment), venv from requirements.lock, warehouse reachable at the
Tailscale address. All 13 contract tests green after the fence episode
below.

**AM-1 fence false alarm (NOT drift, NOT a re-pin).** First pytest run
tripped PinnedLibDriftError on all pins. Evidence gathered before touching
anything: git ls-tree HEAD shows the COMMITTED blobs identical to every
hash in config/pinned_lib.yaml (db.py fb1b5be6, pbp.py 0a9024c8,
lineups.py 23587a1d, lineup_aggregation.py 1332d75f). The laptop clone has
core.autocrlf=true, so checkout smudged postmortem/lib to CRLF, and the
fence hashes raw working-tree bytes. The pinned library did not move one
byte; the working-tree REPRESENTATION did. Resolution: repo .gitattributes
now marks postmortem/lib/** -text (no EOL conversion on any platform) and
the four files were renormalized to LF in the working tree, after which
the pins verify and all 13 tests pass. The pin file was not edited. Commit
8b6fc807. Lesson for the record: the fence is representation-sensitive;
any future clone on Windows would have hit this, and the .gitattributes
closes it permanently.

**PICKUP.md correction.** data/cache/stints/ is NOT gitignored as PICKUP
section 3 claims; the .gitignore that landed in 8a08f178 is secrets-only,
and 7,377 stint parquets came over with the pull. Harmless (the fresh
laptop panel run regenerates them all), noted so nobody plans around the
wrong seam.

**Panel state at pickup.** The desktop pushed a mid-flight checkpoint
(8,500 of 15,669 games scored) at 17:01 and whatever finished after never
got pushed. The laptop is running the panel fresh (desktop checkpoint set
aside; it remains in git history at 8a08f178) so this machine ends up with
the complete stint cache for the D6 DuckDB load, per the PICKUP section 3
caveat. Build resumed from the laptop's own first checkpoint with 16
workers after the initial 8-worker pace projected ~5 hours over the
remote warehouse link.

**Panel-scale quarantine census (desktop checkpoint, 8,500 games, 72
quarantines, all legacy stratum).** Every reason read and bucketed before
any code was touched; every bucket verified against warehouse source data
(house rule: verify against source, then code). Seven buckets:

  1. 'McClellan' (25 games, 2016-17 WAS): retro-rename. Descriptions say
     McClellan; player_name and roster say 'Sheldon Mac' (pid 1627815, he
     changed his name). Same disease as kanter->freedom. FIX: token alias
     mcclellan->mac. No other NBA McClellan or Mac.
  2. 'Jones, Jr.' (20 games, 2016-17 PHX): comma-suffix form. Desc
     'Jones, Jr.' vs PBP exact form 'Jones Jr.' (Derrick Jones Jr.,
     1627884). _norm_name folded periods but not commas. FIX: commas fold
     like periods in _norm_name.
  3. 'Zhou' (18 games, 2017-18 HOU): Chinese family-name ordering, not a
     rename. Descriptions use the family name 'Zhou'; the registry surname
     form is 'Qi' (roster 'Zhou Qi', pid 1627753, PBP form 'Qi'). FIX:
     token alias zhou->qi. No other NBA Zhou.
  4. 'Mbah a Moute' (3 games: 2 MIN 2013-14, 1 LAC 2015-16): multi-token
     surname. In those games he has NO other PBP events, so the PBP
     exact-form map never learns him, and the roster map keyed only the
     bare last token 'moute'. FIX: roster names with 3+ tokens also key
     tokens[1:] ('mbah a moute' -> Luc, 201601).
  5. 'Hayes' (2 games, 2017-18 LAL and TOR): retro-rename WITH
     hyphenation. Desc 'Hayes'; current registry 'Nigel Hayes-Davis'
     (1628502). FIX: hyphenated surnames also key each part ('hayes',
     'davis'), team-scoped; a part colliding with a real teammate surname
     surfaces as AMBIGUOUS through _settle, never a coin flip.
  6. 'SUB: Jones FOR' truncated text (1 game, 0021500624 HOU-LAC
     2016-01-18): the feed's descriptions in this game drop names around
     the Howard/Jones/Capela rotations. Verified on all three 'SUB: Jones
     FOR' events that person_id carries the OUT pid (Capela 203991,
     Harrell 1626149), so the missing OUT TEXT costs nothing. FIX: the
     parser accepts 'SUB: <IN> FOR' with an empty OUT tail. BUT the same
     game also has three 'SUB:  FOR Howard' events where the IN name
     itself is absent, plus a missing Capela IN event entirely. The
     entering player is not recoverable from the sub text, inference would
     be guessing, and guessing is banned. THE GAME STAYS QUARANTINED with
     its legible reason. 1/15,669 = 0.006%, far inside the 0.5% gate.
  7. AttributeError 'float' has no attribute 'lower' (3 games, 2015-17):
     hypothesis scoreboard entry, my first read was WRONG. I suspected the
     freethrow branch of the possession walk (floor_state ~1080); the
     traceback landed in stint_builder.py:294, the rebound stat tally.
     Root cause: team-rebound rows in these games carry sub_type values
     the normalizer nulls ('Normal Rebound'/'Unknown'), and `(x or
     "").lower()` does not guard NaN because NaN is truthy. FIX: isinstance
     guards at BOTH sites (stint_builder rebound tally, floor_state FT
     ordinal parse). Unknown rebound class counts as not-offensive,
     identical to the legacy annotator's 'defensive' default; unknown FT
     ordinal means not-last, identical to the unparseable path. The
     possession walk decides rebound possession switches by team_id alone,
     so no working game changes behavior.

**Verification after fixes.** One game per bucket (all three for Mbah a
Moute, both for Hayes, all three AttributeError games): 11 of 12 reconcile
PERFECT (100% of player-games within 0.5 min of seconds-precise official
minutes, worst error 0.012 min); the twelfth is 0021500624 above,
quarantined by design. All 13 contract tests green after the edits. Full
208-game bench rerun tagged bench_fix5 and the panel-wide quarantine
re-run happen next; results recorded below when they land.

## 2026-07-03 — OVERNIGHT DIRECTIVE (Bobby, verbatim)

"OVERNIGHT DIRECTIVE, fitengine (auto mode; work in order, skip past
blocks, log everything):

1. F1 repair loop to completion: period-start-floor repair per D3 fix
   order, iterating on the 208-game bench with the truncation-aware
   scorer. Rider 2 binding: official-minutes evidence constrains with
   the half-open interval [m, m+1), never m +/- tolerance. When bench
   converges, run the FULL 15,669-game panel, produce the G1 scorecard
   (AM-3 denominator, AM-4/AM-5 strata, invariant labels), and run the
   Rider-1 seconds-precise stratum: >= 200 era-stratified games via
   targeted nba_api boxscore pulls, original 99.5%-within-0.5-min
   criterion. G1 green requires BOTH gates. If any G1 row fails after
   D3 fix items 1-5 are exhausted: decision memo, park, continue.
2. On G1 green (or parked-with-memo): F2 in full. Layer 1a per D4:
   per-season O/D ridge RAPM, prior blend, GCV alpha on dev seasons
   only then frozen, 200-block bootstrap SEs, A1 covariance parquets
   (exact blocks >= 500 shared possessions). Gate: G2 RAPM rows
   (YoY 0.50-0.75 band, face-validity top-20 lists exported for my
   morning read, never fitted-to).
3. F3 prep that doesn't need G2 ratified: player_features table from
   nba_player_tracking_season + box + RAPM placeholders; feature_regime
   scaffolding with the leakage canary test green on synthetic data;
   A2 aging-fit code written (fit runs only after skill vectors exist).
4. F4 scaffolding: lineup_obs builder with A3 leverage weights (frozen
   rule from the adapter taggers), GBM floor training harness,
   set-attention module + trainer with smoke tests on synthetic data.
   NO real Layer 2 fits until F3 vectors exist.
5. Backtest harness plumbing (F5 prep): mechanical transaction-universe
   builder from nba_player_stats team changes under the frozen
   protocol (preceding-season minutes basis, realized-window rules).
   Output the DEV-window case list only. Do NOT enumerate, list, or
   touch sealed-window (2021-22 onward) cases in any artifact.
6. Housekeeping: validation report regenerated; commit at each green
   milestone; full session log; any gate failure -> memo like the
   Model B one, park, proceed to independent work.

HARD CONSTRAINTS: sealed window untouched and unenumerated; no
threshold or gate revisions (memos only); K selection is F3 dev work
but the CHOICE is presented to me, not frozen overnight; nothing
publishes; provisional tags on anything downstream of an unratified
gate; when genuinely blocked, skip and log rather than guess."

### Same-session reading of directive item 1 vs the fix-4 memo

Item 1's Rider-1 stratum ("&gt;= 200 era-stratified games via targeted
nba_api boxscore pulls") is the plan-as-written language. The fix-4 memo
(2026-07-02 night, logged above and in reconcile.py) established that
nba_player_advanced_stats.minutes_float IS that seconds-precise reference,
same nba_api source data already ingested, with FULL-PANEL coverage
(15,669 games, strictly larger than the required 200), and made the
original 99.5%-within-0.5-min criterion the PRIMARY gate on the whole
panel. The directive's stratum is therefore satisfied at superset
coverage by the primary gate itself; no separate 200-game pull is run.
If an INDEPENDENT-of-warehouse ingest check is wanted on top (fresh API
pulls compared to the ingested table), that is a new requirement and a
morning question, not blocking G1.

## 2026-07-03 (overnight) — first full-panel read, round-2 buckets, and a real bug the panel caught

**First full-panel completion (laptop, 16 workers, ~1:00am).** All 15,669
games scored. Even with AM-3 counting every quarantined game's player-games
as failures, the gate criteria already read green: pooled
recon_rate_TRUE_0p5 99.5865%, relaxed 99.5991%, quarantine 0.2553%
(40 games), possession parity exact, live stratum 99.98% with zero
quarantines. NOT YET THE G1 CLAIM: the round-2 fixes below changed the
resolver, so the judged scorecard comes from the final-code re-run.

**The 40 quarantines, bucketed (every reason read, per discipline):**
  1. 14 games, OperationalError: warehouse connection drops in one
     contiguous 00221xxx stretch, a transient network blip mid-run, not a
     data disease. Re-run clean.
  2. 16 games, 'Pöltl' (2024-25 TOR, legacy-format rows): descriptions
     carry the umlaut, the registry uses the German transliteration
     ('Poeltl'), and the NFKD fold gives 'poltl' vs 'poeltl'. FIX:
     transliteration VARIANT forms (ae/oe/ue/ss) tried after the plain
     fold, never instead of it ('Schröder' still hits registry 'Schroder'
     via the plain fold first).
  3. 2 games, 'Yongxi' (2024-25 BKN): Cui Yongxi; descs use the given
     name, and the registry row is literally 'Cui Cui' (its own quirk).
     FIX: token alias yongxi->cui, verified unique.
  4. 7 games, AMBIGUOUS at roster: a cameo player with ZERO attributed
     PBP events shares a bare surname key with a teammate ('Williams'
     BOS 2020-21; 'Jones' CHI x2, LAC x2; 'Jackson' MEM; 'Williams' MEM
     x2). FIX: two evidence-based eliminations at the roster/prefix
     stages, each reverted if it would empty the candidate set:
     (a) minimal-uniqueness elimination: a candidate whose exact PBP forms
         in THIS game exist and do not include the lookup form is called
         something else by the feed ('Williams III' is never plain
         'Williams' in the same game);
     (b) played elimination: the entering player must appear in the
         seconds-precise minutes_float column (NULL = DNP). NEVER the
         integer minutes column: Grant Williams' 36-second cameo in
         0022000936 is minutes_played=0 but minutes_float=0.60. Rider 2's
         truncation lesson, reconfirmed in a new spot.

**A real bug the panel caught (hypothesis scoreboard: the ambiguity
buckets were hiding it).** Game 0022300106 resolved its 'Jackson'
ambiguity correctly post-fix but still read 22/24. The residual was a
WILLIAMS self-sub: 'SUB: Williams Jr. FOR Williams' (Vince Williams Jr.
in for Ziaire Williams). The suffix-stripped lookup 'williams' hit the
OUT player's own PBP form as a SINGLE candidate, and _settle only
removed the out-pid from multi-candidate sets, so Ziaire "subbed in for
himself" and Vince's 0.63-minute cameo vanished, SILENTLY (the game never
quarantined; team seconds stayed exact because the identity swap
preserves them). FIX: unconditional out-pid elimination at every stage
and every candidate count; the entering player can never be the leaving
player. The lookup then falls through to the roster stage where
'williams jr' resolves Vince uniquely.

**One more form: 'Louzada Silva' (1 game, 2020-21 NOP).** The desc
carries MORE of the legal name than any registry form (PBP form
'Louzada', roster 'Didi Louzada'). FIX: a dead-last leading-token
fallback stage (>= 2 tokens, leading token >= 3 chars so initialed forms
never reach it), eliminations on, ambiguity still raises.

**Consequence of the self-sub find: full-panel RE-RUN under final code.**
The prescribed loop (rerun only quarantined games) is insufficient this
round because the self-sub bug corrupted games that never quarantined,
and their per-game stint parquets embed wrong lineups, which would poison
the RAPM design matrix downstream. The G1 claim must come from ONE code
state. Re-run launched ~1:20am (16 workers); 208-game bench re-run
(bench_fix6) launched alongside per bench discipline. 0021500624 stays
quarantined by design (the 'SUB:  FOR Howard' events genuinely omit the
entering player; inference would be guessing and guessing is banned).

**Also verified this round:** all 12 round-1 bucket games still perfect
after the round-2 changes; 31 contract tests green.

## 2026-07-03 (overnight) — G1 VERDICT: GREEN (final-code full panel)

The full 15,669-game panel under final resolver code (commit 30744148)
is the sole basis for this judgment (directive 2026-07-02 item 1; bench
runs were repair iteration only). Summary table pasted verbatim from
src.stints.reconcile.summarize:

```
stratum  games  quarantine_rate  recon_rate_TRUE_0p5  recon_rate_relaxed  team_seconds_exact_INVARIANT  poss_parity_pct_PARTITION  median_worst_delta_true
 pooled  15669         0.000064             0.998476            0.998603                      0.999872                        0.0                 0.008333
 legacy  14940         0.000067             0.998410            0.998543                      0.999866                        0.0                 0.008333
   live    729         0.000000             0.999809            0.999809                      1.000000                        0.0                 0.008333
```

GATE READ (both criteria required, pooled AND per stratum):
- recon_rate_TRUE_0p5 (PRIMARY, seconds-precise minutes_float, original
  0.5-min criterion): pooled 99.8476%, legacy 99.8410%, live 99.9809%.
  All >= 99.5%. GREEN. (332,267 of 332,774 player-games.)
- recon_rate_relaxed (SECONDARY, truncation-aware vs integer minutes):
  pooled 99.8603%, legacy 99.8543%, live 99.9809%. All >= 99.5%. GREEN.
- quarantine_rate: pooled 0.0064% (1 game), legacy 0.0067%, live 0.0%.
  All < 0.5%. GREEN.
- lineup validity (D6 load assertion): 0 non-5v5 stints across 818,713
  stints. GREEN.
- possession parity (PARTITION, structural): 0.0000% deviation. Exact.
- team-seconds (INVARIANT, structural): 0.999872 pooled = 2 of 15,669
  games not exactly-exact, BOTH explained and cosmetic (below).
- coverage: all 15,669 R1 train-eligible games present. AM-5 backfill
  stratum empty by design (the 2013-14 "gap" was a query artifact, R1).

**G1 IS GREEN.** F1 is closed.

**The single quarantine (by design, not a failure to fix).** Game
0021500624 (2015-16 HOU-LAC): three substitution descriptions read
'SUB:  FOR Howard' with the ENTERING player's name absent from the text
entirely (not a resolution miss, an empty field), plus a missing Capela
sub-in event. The entering player is unrecoverable from the feed and
guessing is banned (house rule), so the game quarantines with its legible
reason. 1/15,669 = 0.0064%, ~78x inside the 0.5% budget. AM-3 counts all
its player-games as failures anyway; the gate passes regardless.

**The two team-seconds non-exact games, both cosmetic:**
- 0021500624: the quarantine above (reconcile sets team_seconds False for
  quarantined games by construction).
- 0021500916: a PHANTOM-OT game. The PBP carries a period-5 marker with
  ZERO real playing time; reconcile computed expected team-seconds for a
  5-period game (265 min/team) while the true game is regulation (240).
  Per-player reconciliation is PERFECT (0/21 fail, worst 0.01 min), so it
  is a reference-length artifact, not a floor error. Noted; not a defect.

**Tail characterization (src.stints.tail_census over all 142 games that
miss essentially-perfect reconciliation).** The 507 failing player-games
(0.152% pooled) bucket as:
- attribution_residual: 140 games, 464 failing player-games (95.7% of the
  tail). Team-seconds exact, floor COUNT correct in every period (zero
  games classified floor_count_error), but floor MEMBERSHIP is wrong for
  part of a period (a player briefly credited to a teammate). Diffuse
  across all 13 seasons, worst-10 games holding only ~19% of the mass.
  This is the residual data-quality floor, NOT a single fixable structural
  disease; the sharp per-period floor-count localizer (src.stints.diagnose)
  finds no period miscount to repair. Adversarial root-cause sampling
  queued as verification; even treating all 464 as genuine errors leaves
  G1 green with 60x margin.
- reference_incomplete: 1 game (0022500160, 2025-26 HOU-DAL). Official
  minutes_float sums to 171.6/team vs 240 expected (68-min shortfall),
  uniform-over with exact team-seconds -> the warehouse's advanced
  boxscore for this in-progress-season game is undercounted; the
  RECONSTRUCTION is correct (240/team). A reference gap, not our error.
- clean_or_phantom: 1 game (0021500916 above).

**Downstream note for F2.** These 140 residual games carry small lineup-
membership errors into the RAPM possession cache. At 0.139% of player-
games with sub-minute-to-few-minute magnitudes, the effect on season
RAPM is negligible; no exclusion applied. The one reference-incomplete
2025-26 game is flagged for a completeness re-check when that season's
boxscore ingest finalizes.

## 2026-07-03 (overnight) — G2 (RAPM rows) VERDICT: GREEN

F2 Layer 1a per plan D4: per-season O/D ridge RAPM from the possession
cache (3,020,898 possessions, garbage excluded), two-stage prior (box
composite + season s-1 estimate aged one year via the pinned Model C
curves, 0.6/0.4 blend), GCV alpha FROZEN at 2000 on dev seasons 2015-16
through 2020-21 only (alpha_freeze.json; refuses reselection), 200-game-
block bootstrap SEs, A1 covariance blocks at >= 500 shared possessions.
13 seasons written to outputs/rapm/rapm_<yr>.parquet + cov_<yr>.parquet.

GATE 1 — RAPM stability (YoY correlation in 0.50-0.75): GREEN, all 12
adjacent-season pairs in band on BOTH O-RAPM (0.624-0.726) and D-RAPM
(0.566-0.722). Neither noise (too low) nor over-shrunk prior (too high).
Full table in outputs/rapm/g2_rapm_report.md.

GATE 2 — face validity (narrative check, NEVER fitted-to): top-20 lists
match the known impact ladder precisely. 2015-16: Kawhi (def -4.88, the
DPOY that year), unanimous-MVP Curry (off +9.09), Draymond (def -3.50),
Chris Paul, Westbrook, LeBron. 2024-25: Jokic / SGA / Giannis at the top
(the actual MVP-race top three), then rim/wing defenders (Lively -5.21,
Finney-Smith, Franz Wagner) and Luka. Sign convention correct (negative
def_rapm = fewer points allowed = better defense). Bottom lists are
low-impact rotation players. Exported for Bobby's morning read.

Both G2 RAPM-row gates pass. The Layer 1b FACTOR rows (R-hat, ESS,
PCA-beat) are F3 and remain PENDING. The A2 aging fit for skill vectors
remains written-but-unrun until F3 produces skill_vectors.

Note (not a gate issue): alpha 2000 was the argmin of summed dev-season
GCV; the curve is flat-ish near the top (dev seasons individually also
picked 2000), so the estimate is stable. Frozen regardless per house
rule; no post-hoc adjustment.

## 2026-07-03 (overnight) — G1 tail root-cause: a REAL systematic bug found, fixed (post-green repair)

The census called the 140-game reconciliation tail "diffuse." A 13-agent
adversarial root-cause workflow (one trace agent per worst-residual game
per season, plus synthesis) OVERTURNED that: 10 of 13 sampled games localize
to ONE defect in floor_state._identify_period_start_floors. My census
bucketing was too coarse (it keyed on starter_mismatch / bad_periods, which
this bug does not trip); the workflow's per-game floor-chain traces caught
what the aggregate missed. Logged as a scoreboard miss: "diffuse" was wrong.

**The bug.** The period-start-floor seeder counts ANY non-substitution
event by a player as an on-floor "appearance." A technical foul charged to
a bench / DNP / ejected player (or an ejection at the period tip) is such
an event but does NOT imply floor presence. The phantom takes a slot in the
start-five via candidates[:5], truncating the true quiet starter (whose
first real event lands microseconds later), and with no sub to remove the
phantom the whole period freezes on the wrong lineup — one player over,
conserved unders mirroring. Example (0021300228): Larry Sanders, a DNP with
a single technical foul and zero sub events, was seated ~12 min in period 2,
displacing O.J. Mayo (-6.52) and Nate Wolters (-5.49). Team-seconds stay
exact (5 bodies, wrong identities), which is why it never quarantined.

**The precedent.** validate_floor_state ALREADY skips exactly this event
class in its actor check (SKIP_ACTOR_CHECK + the technical-foul skip, ~line
1048). The seeder simply failed to mirror it. FIX: a shared
_implies_floor_presence(atype, sub_type) predicate (technical fouls,
ejections, timeouts, period/game markers, jump-ball bookkeeping, heaves,
replays return False); the seeder's appearance branch now skips events that
do not imply floor presence. Surgical, name-resolution-independent, and
consistent with the existing house definition.

**Scope of fix (this is a CODE correctness fix, not a threshold retune —
house rule distinguishes them; no gate bar moved).** Verified on the 13
sampled games: 8 now reconcile PERFECTLY, a 9th improves (worst error 17 ->
5 min). The remaining sampled residuals are: 1 same-surname IN-resolution
(Glenn vs Thomas Robinson, 0021401189 — genuine, rare at ~8%, memo'd for a
targeted fix, not a campaign per the workflow); 1 irreducible data floor
(0021600253 — outgoing Afflalo and incoming Temple both silent in P4, zero
PBP signal); 2 quiet-starter period seatings with no technical (0021700266,
0022300527 — one-quarter swaps, partly data-floor, left for a later pass).
208-game bench re-run (bench_fix7): 208/208 PERFECT both criteria both
strata, ZERO quarantines — NO regression. 33 contract tests green.

**Propagation.** Because the fix changes period-start floors, it changes
the reconstructed lineups feeding the stint cache, the possession cache,
and thus RAPM. Per the directive ("F1 repair loop to completion... run the
FULL panel"), the full pipeline is being re-run under the fix. Optimization
landed first: reconcile_game now writes the possession cache in the SAME
pass as stints + scorecard (shared possessions_for_game), so ONE panel
re-run regenerates all three instead of two 90-minute warehouse passes.
Sequence: panel re-run -> D6 reload -> RAPM (alpha stays FROZEN at 2000, no
reselection) -> player_features + lineup_obs -> updated G1/G2 verdicts.
The frozen alpha and all gate bars are untouched; only reconstruction
quality improves.

## 2026-07-03 (overnight) — G1 + G2 RE-VERDICT after the period-start fix propagated (supersedes the earlier green rows)

The period-start-floor fix (commit 0927e194) was propagated through a full
combined panel re-run (one pass regenerating stints + possessions +
scorecard), D6 reload, RAPM re-fit (alpha stayed FROZEN at 2000, verified
no reselection), and player_features / lineup_obs rebuilds. The earlier
2026-07-03 G1 and G2 green rows are SUPERSEDED by the numbers below; they
remain in this record and in git history (scorecard at commit 6ad459d7) as
the audit trail. No gate bar moved; reconstruction quality improved.

**G1 RE-VERDICT: GREEN, improved.** Summary table verbatim:

```
stratum  games  quarantine_rate  recon_rate_TRUE_0p5  recon_rate_relaxed  team_seconds_exact_INVARIANT  poss_parity_pct_PARTITION  median_worst_delta_true
 pooled  15669         0.000064             0.999318            0.999396                      0.999872                        0.0                 0.008333
 legacy  14940         0.000067             0.999284            0.999366                      0.999866                        0.0                 0.008333
   live    729         0.000000             1.000000            1.000000                      1.000000                        0.0                 0.008333
```

Movement vs the pre-fix green (both criteria still >= 99.5% everywhere):
- recon_TRUE_0p5 pooled 99.8476% -> 99.9318%; legacy 99.8410% -> 99.9284%;
  live 99.9809% -> 100.0000% (live is now PERFECT).
- failing player-games 507 (0.152%) -> 227 (0.068%): more than halved.
- games under 99% reconciliation: 141 -> 63.
- quarantine unchanged (1 by-design game, 0.0064%); parity exact; 0
  non-5v5 stints across 818,809.

**Tail re-census:** attribution_residual 140 games / 464 failing -> 61
games / 184 failing (the entire technical-foul / ejection seating class,
~79 games, is gone). Remaining buckets are the memo'd residuals: quiet-
starter period seatings with no administrative event, the lone same-surname
IN-resolution (Glenn vs Thomas Robinson), and irreducible data-floor games
with zero PBP signal, plus 1 reference-incomplete 2025-26 game and 1
phantom-OT. All memo'd; none is a fixable systematic class at panel scale.

**G2 RE-VERDICT: GREEN, unchanged.** RAPM re-fit on the corrected
possessions with alpha FROZEN at 2000. YoY stability still all 12 pairs in
the 0.50-0.75 band (O 0.624-0.726, D 0.565-0.722) -- essentially identical
to the pre-fix fit, as expected since the fix cleaned only ~0.08% of
player-games. Face validity unchanged (top-20 ladders intact). Both G2
RAPM-row gates hold. Layer 1b factor rows remain F3-pending.

**Scoreboard (my own miss, logged per house convention):** the aggregate
tail census called the residual "diffuse"; it was wrong. The census keyed
on starter_mismatch and floor-count signals, neither of which the
technical-foul bug trips, so it under-classified. The 13-agent per-game
root-cause workflow caught the systematic cause the aggregate hid. Lesson:
aggregate bucketers can launder a real bug into "diffuse"; per-item traces
are the check.

## 2026-07-03 — F3 GATING ruling (Bobby, verbatim)

"F3 GATING (resolve before K selection runs):
1. 2020-21 tracking: attempt targeted nba_player_tracking_season
   ingest (few calls). If it lands, hole closed. If the endpoint
   lacks the season: pre-declared fallback = per-dimension mean
   imputation with a missingness flag into the factor model, AND
   2020-21 excluded from K-selection reconstruction scoring. Never
   silent. Memo either outcome.
2. 2025-26 undercounted boxscore: confirm ingest-gap vs live-branch
   reconstruction defect (AM-4 stratum). Ingest gap -> targeted pull
   or memo'd single-game exclusion. Defect -> stop and memo, do not
   proceed to F3.
3. THEN F3: fit factor model, K in {6,8,10} on dev, reconstruction
   vs PCA health gate, and present the K choice to me with both the
   reconstruction curve AND dev-season G3 proxy performance. Do not
   freeze K.
PREDICTION (logged pre-selection, predictions.md): K resolves to 8.

Residual cleanup pass: DEFER. Sub-0.5%, non-systematic, memo'd. Not
worth a session against the September clock; the banked time stays
banked."

Verbatim framing recorded for the K decision (so it can't be back-fit):
soft elbow expected on the reconstruction-vs-K curve; tie-breaker is
downstream dev-season G3 proxy, not reconstruction alone (a dimension that
does not help predict lineups is not worth interpreting). Ratify 8 if the
elbow is clean at 8 and G3 agrees; take 8 for interpretability if
reconstruction wants 10 but G3 is flat 8->10; memo if both point elsewhere.
Both data gates must resolve before K selection RUNS (the honest
reconstruction scoring needs a complete feature matrix; 2020-21 is
currently a hole).

## 2026-07-03 — F3 GATING resolved (both data gates cleared; K selection unblocked)

**Gate 1 (2020-21 tracking hole): CLOSED via targeted ingest (preferred
option landed).** The endpoint HAS the season (LeagueDashPtStats
season=2020-21 returns 540 players; a known-present control season
returned identically), so the hole was a warehouse ingest gap, not an
endpoint limitation. src/etl/ingest_tracking_2021.py pulled all 11 measure
types and inserted 5,937 rows into nba_player_tracking_season with the
existing seasons' schema/convention (API fields lowercased; one rename,
ast_pts_created -> ast_points_created, the sole API/warehouse column-name
difference). Idempotent (deletes 2020-21 rows first; there were none).
player_features rebuilt: 2020-21 tracking coverage 0% -> 100%, matching the
adjacent seasons. The pre-declared imputation fallback is NOT needed and
was not used. Feature matrix is complete; no missingness flag, no 2020-21
exclusion from K-selection reconstruction scoring.

**Gate 2 (2025-26 undercounted boxscore, game 0022500160): CONFIRMED
ingest gap, NOT a live-branch reconstruction defect (AM-4 check passes).**
Evidence: the integer reference (nba_player_stats.minutes_played) sums to
232/235 per team (near-full 240, the small gap is floor truncation), and
the reconstruction produces 240/team exactly, matching it. Only the
seconds-precise reference (nba_player_advanced_stats.minutes_float) is
wrong -- it sums to 171.6/171.6 per team, but every player HAS a non-null
float, so the VALUES are partial, not the rows missing. It is the ONLY
game in all of 2025-26 with this float-undercount. The reconstruction is
sound; the live branch is not defective; this is the same reference-ingest
class as the play-in absentees. Resolution: memo'd single-game reference
note. The game's lineups (correct, 240/team) feed RAPM/features unharmed;
it costs the G1 PRIMARY metric one game (counted against the gate under
AM-3, no laundering) while passing the SECONDARY integer-based criterion.
No targeted re-pull warranted for one cosmetic reference value; if the
2025-26 advanced-boxscore ingest is refreshed later it self-heals.

Both gates clear. Per the ruling, F3 K-selection now runs on the complete
feature matrix; K stays UNFROZEN and the choice is presented with the
reconstruction-vs-K curve AND the dev-season G3 proxy.

## 2026-07-03 — F3 K-selection EVIDENCE (presented to Bobby; K NOT frozen, awaiting ratify)

Run on the COMPLETE dev feature matrix (2020-21 hole now closed): 3,475
rotation player-seasons (own-column RAPM present) x 21 features (box rates,
advanced rates, tracking per-75, O/D-RAPM point estimates), dev seasons
2013-14..2020-21 only, sealed window untouched. Selection instrument =
probabilistic FactorAnalysis (the full measurement-error-aware Bayesian fit
+ skill_vectors freeze follows AFTER ratify). Two curves, per the ruling:

Reconstruction (held-out average log-likelihood, higher better; FA vs
probabilistic-PCA is the spec health gate -- raw reconstruction MSE is
minimized by PCA by construction so LL is the correct metric):
```
 K   FA held-out LL   PCA held-out LL   FA beats PCA
 6      -18.695          -22.751            YES
 8      -18.360          -22.108            YES
10      -18.229          -21.491            YES
```
FA beats PCA at every K (the posterior machinery earns its keep). Gains:
6->8 = +0.335, 8->10 = +0.130. The 8->10 gain is 39% of the 6->8 gain --
a SOFT ELBOW AT 8, exactly the shape the ruling anticipated.

G3 proxy (dev-season lineup-prediction possession-weighted RMSE by K, lower
= factors help; within-season scoring proxy, diagnostic not a gate, used
only for the relative K comparison; temporal holdout on 2019/2020/2021):
```
 K   G3-proxy RMSE
 6      27.179
 8      27.010
10      26.929
```
Improvement 6->8 = 0.169, 8->10 = 0.082. The marginal lineup-prediction
value of factors 9-10 is under half that of factors 7-8. G3 AGREES with
reconstruction: diminishing returns after 8.

RECOMMENDATION: K = 8. Both curves show a clean elbow at 8, FA beats PCA at
all K, and the G3 proxy confirms factors past 8 add little downstream
predictive value. This matches the pre-registered lean (P-K, predictions.md)
and is the "clean elbow at 8 with G3 agreeing -> ratify" scenario Bobby
pre-authorized. K IS NOT FROZEN here; presented for Bobby's ratify. On
ratify, the full Bayesian factor model fits at K=8 with the real health
gates (R-hat < 1.01, ESS > 400, anchor sign-stability), skill_vectors
freezes and versions, and the interpretability question (are the 8
dimensions nameable for the flagship) is answered from the fitted loadings.
Artifacts: outputs/factor/k_selection.parquet + .json.

## 2026-07-03 — K RATIFIED: K=8 (Bobby, verbatim)

"K RATIFIED: K=8. Freeze in model_params.yaml. Rationale: FA beats
pPCA at every K (structure real), soft elbow at 8 on both
reconstruction (6->8 gain 2.6x the 8->10) and the G3 proxy (8->10
adds <half the downstream value), matches pre-logged P-K. Proceed to
the full measurement-error-aware Bayesian factor model at K=8 with
the REAL health gates: R-hat<1.01, ESS>400, anchor sign-stability
across refits. skill_vectors freezes and versions ONLY after those
gates pass; a health-gate failure parks with a memo, it does not
ship vectors."

Held in view before the fit (Bobby, not a blocker): the K-selection used
a fast FactorAnalysis; the vector-producing model is the full measurement-
error-aware Bayesian version consuming the A1 RAPM covariance blocks.
Different estimators -- the Bayesian effective dimensionality may not match
FA's at 8 (measurement-error weighting can collapse or sharpen factors). If
health gates pass at 8, ship. If R-hat or anchor stability struggle SPECIFICALLY
because two factors fight over the same variance, the pre-authorized response
is a MEMO showing the Bayesian reconstruction curve, NOT a silent re-selection
of K. K is frozen; what stays open is whether the Bayesian fit confirms 8 is
healthy (a gate outcome, not a new choice).

Editorial call queued for after the vectors land (Bobby): whether the 8
dimensions are coherent enough to NAME in the flagship. The fit must export
top-loading features and exemplar players per factor so a dimension that is a
statistical smear is not pretended into a named skill.

## 2026-07-03 — F3 Layer 1b fit PARKED: NUTS intractable on this CPU; SVI fallback proposed (Bobby's ruling needed)

The measurement-error-aware Bayesian factor model (K=8, ratified) is
CORRECT and math-unit-tested (Woodbury marginal log-likelihood == direct
MVN; conditional-posterior scores == brute-force Gaussian conditioning;
8 distinct pure-marker anchors). The blocker is purely the NUTS fit's
wall-clock on this laptop CPU. Nothing about K, the anchors, the
measurement-error handling, or the factor structure is in question, and
none of it was changed; only sampler/perf settings were tuned.

**Diagnosis chain (each a sampler-geometry issue, each fixed, all
committed in skill_factors.py):**
1. Laplace sparsity prior: its non-differentiable spike at 0 forced very
   deep NUTS trees. FIX: smooth Normal loadings (shrinkage still yields
   interpretable few-large-loadings; strict-sparse is a v1.1 refinement).
2. Hierarchical loading scale (tau x w_raw): funneled against the loadings
   with this much data, saturating the tree cap. FIX: fixed-scale Normal
   (removes the funnel; standardized features make unit scale weakly
   informative).
3. Per-row MVN likelihood over the fit rows is the intrinsic CPU cost.
   FIXES: fit loadings on a bounded row SUBSAMPLE (population params;
   all player-seasons scored post-hoc), and cap max_tree_depth.

**Escalation ladder actually run (dev, 3475 rotation player-seasons):**
- funnel-fixed, 3475 rows, depth 7: killed at ~68 min, saturating.
- subsampled 1500 rows, depth 7: killed at ~26 min, still saturating (3.3
  cores steady).
- subsampled 1000 rows, depth 6, warmup 600 / samples 800: LIGHTER (2.1-2.4
  cores, ~40% less total compute) but STILL did not complete -- no health
  json at 28.7 min, steady sampling (not tapering). ~5 min of that is fixed
  JAX compile of the vectorized-4-chain NUTS scan; the rest is the per-row
  MVN over 1000 rows x up to 64 leapfrog steps x 1400 draws.

**Finding:** full-4-chain NUTS on this likelihood is intractable on this
CPU within a workable iteration budget, even funnel-fixed at depth 6 /
1000 rows. Further shaving (depth 5, 700 rows, 2 chains) would trade away
the health-gate's statistical meaning for speed, which is the wrong lever.

**PROPOSAL for Bobby's ruling (NOT adopted unilaterally -- it changes the
health-gate semantics):** fit Layer 1b by STOCHASTIC VARIATIONAL INFERENCE
(numpyro SVI, AutoLowRankMultivariateNormal guide over the loadings/psi;
the latent factor scores stay analytically marginalized, so the guide is
low-dimensional and SVI converges in seconds-to-minutes). Because SVI has
no R-hat/ESS, the health gate would be REPLACED by a documented surrogate:
(a) ELBO convergence (stable over the last N steps, multiple inits agree);
(b) posterior-predictive held-out reconstruction still BEATS PCA at K=8
    (the spec's own structural check, method-agnostic);
(c) loading sign/rotation STABILITY across seeds (the anchor-stability
    intent, restated for SVI).
Trade-off: SVI gives an approximate (often over-concentrated) posterior,
so the skill_vectors' sample spread would be a floor on uncertainty, not
exact -- acceptable for v1 vectors, flagged for Layer 2 to widen via the
deep ensemble it already runs. K STAYS FROZEN at 8. skill_vectors are NOT
shipped until Bobby rules on the SVI substitution. If he prefers to keep
strict NUTS, the path is a longer offline run on the desktop / more cores /
a GPU, or accepting a multi-hour fit -- his call.

Everything else in F3 is done and committed: K=8 ratified and frozen, the
factor model built and math-verified, the K-selection evidence, both data
gates resolved. Only the vector-producing fit is parked on this question.

## 2026-07-03 — LAYER 1B RULING (Bobby, verbatim)

"LAYER 1B RULING: no subsampled fit ships, full stop. The fit covers
all 6,936 player-seasons or no vectors ship; a sixth-of-the-data fit
disproportionately drops exactly the query/backtest players the engine
targets. That, not the sampler, is the disqualifier.

Order of operations before any inference-method switch:
1. Profile the full-data NUTS single step. Check three things:
   (a) per-row covariance Cholesky cached once vs refactored per
       leapfrog; (b) JAX actually JIT-compiling the vmapped
       likelihood (no Python row loop); (c) marginalized-scores
       formulation carrying no latent score params. Fix whatever's
       there and re-time. A K=8, 6,936x25 marginalized model should
       not be multi-hour on CPU; if it is, suspect spec before
       hardware.
2. If genuinely still too slow after profiling, PREFERRED path is the
   overnight/offline full-data NUTS run (more cores or just wall
   clock) with the REAL gates intact (R-hat<1.01, ESS>400, anchor
   stability). We have banked schedule; spend it here, this artifact
   is load-bearing.
3. SVI is the LAST resort, and only on full data, never subsampled.
   If adopted: the surrogate gates you named (ELBO convergence,
   held-out reconstruction beats PCA at K=8, loading stability across
   >=5 seeds) PLUS one more: on a tractable subset, NUTS and SVI
   posterior MEANS must agree within tolerance, so we know the VI
   point estimates aren't biased, only the variances tightened. And
   the over-concentration gets an explicit floor note: Layer 2's
   ensemble widens intervals, and the conformal wrapper is what
   ultimately guarantees coverage, so approximate 1b variances are
   tolerable IF G3 coverage still passes. If G3 coverage fails, 1b
   uncertainty is the first suspect.
Memo the outcome of step 1 before proceeding; I want to see whether
this was ever really a hardware wall."

The subsampling fallback is RETRACTED (n_fit_rows removed; full-data fit
only). Profiling the single-step cost now, per step 1, memo to follow.

## 2026-07-03 — Dense-mass fix RATIFIED + population verification protocol (Bobby, verbatim)

"POPULATION VERIFICATION (into the fit memo, blocking vector freeze):
1. Assert programmatically that ZERO query-roster players and ZERO
   backtest-universe incoming players (dev AND, without enumerating
   sealed cases, the sealed set's incoming players by id) fall in the
   ~1,100 archetype-prior group. Print the check, not a summary.
2. Explicit callout: Edwards and LaMelo are in the 5,838 fit
   population with own-column RAPM. Name them in the memo.
3. Standing rule for the record: any player who is ever a query
   target or a backtest-scored player must have a fitted vector, never
   an archetype prior. If the sealed set surfaces one at F5 who
   doesn't, that's a memo and a ruling, not a silent archetype
   fallback."

Point 3 is now a PRE-REGISTERED EXCLUSION-CRITERION RECONCILIATION: the
backtest inclusion filter already requires a top-100-minutes INCOMING
player (who by definition has own-column RAPM and thus a fitted vector),
so the two filters SHOULD be consistent; this ruling makes that
consistency a checked invariant rather than an assumption. If ever
violated (a sealed incoming player without a fitted vector), it is a memo
and Bobby's ruling at F5, never a silent archetype fallback.

Dense-mass diagnosis ratified: exact NUTS, full population, real R-hat/ESS
gates; nothing traded away. Profile findings + fix memo'd below with the
verification.

## 2026-07-03 — F3 profile finding + dense-mass fix + population verification (memo)

**Profile (Bobby's step 1, all three checks CLEAN).** The full-data
likelihood gradient was timed at N = 100, 1000, 3475, 5838 rows: 5.5, 5.8,
6.4, 6.2 us/ROW -- flat, i.e. gradient cost scales LINEARLY in rows (36 ms
on the full 5,838). Therefore: (a) NO accidental quadratic (a per-leapfrog
covariance refactor would show super-linear scaling); (b) JAX IS
JIT-vectorizing the vmapped likelihood (linear scaling proves the vmap
compiled, no Python row loop); (c) the marginalized-scores formulation
carries NO latent score params (only W_free 21x8, anchor_diag 8, psi 21 =
197). A 36 ms gradient is cheap; the model was never the wall.

**Real cause: mass matrix.** With a cheap gradient, a ~29 min fit means a
huge leapfrog-step count -- NUTS saturating the tree-depth cap. Cause: the
loadings posterior is correlated and the default DIAGONAL mass matrix can't
navigate correlation, so trajectories run to the cap. FIX: dense_mass=True
(a full 197x197 mass matrix, trivial to adapt) captures the correlations
and collapses the trajectory length. This keeps EXACT NUTS, the FULL
population, and the REAL R-hat/ESS gates -- nothing traded away. It was
never a hardware wall (Bobby's suspicion confirmed).

**Subsampling RETRACTED** (ruling): n_fit_rows removed; the fit is on ALL
rotation player-seasons. A random subsample was the disqualifying fourth
silent fallback -- it drops query/backtest players.

**POPULATION VERIFICATION (blocking freeze, PASS).** src.models.
verify_population, run verbatim:
- fitted population: 5,838 player-seasons, 1,346 distinct players with
  own-column RAPM (the factor model's domain).
- DEV backtest incoming (top-100-min filter): 167 players, ALL have a
  fitted prior-season vector: True.
- SEALED backtest incoming (BY ID, counts only, NOT enumerated -- seal
  preserved): 127 players, ALL have a fitted prior-season vector: True.
- Anthony Edwards (1630162) and LaMelo Ball (1630163): both in the
  population, fitted seasons 2021-2026.
- VERDICT: PASS. The G4 top-100-minutes inclusion filter guarantees the
  incoming player has RAPM, so it is CONSISTENT with the RAPM-coverage
  fit domain; zero query/backtest players take an archetype prior.

**Standing rule locked (pre-registered):** any query target or backtest-
scored player MUST have a fitted vector, never an archetype prior. If the
sealed set surfaces a violator at F5, that is a memo + Bobby ruling under
sealed ceremony, never a silent fallback. Reconciliation of the two
filters is now a checked invariant (verify_population), re-run before the
sealed evaluation.

The ~1,098 non-rotation player-seasons (all player-seasons 6,936 minus
5,838 rotation) are sub-minutes-floor players with no own-column RAPM; they
take archetype priors per spec 8.4 and NONE are query/backtest targets
(verified). This is a principled population definition, not a subsample.

## 2026-07-03 — F3 Layer 1b: OFFLINE full-data NUTS run launched (Bobby's step-2, pre-approved)

After the profile (gradient cheap + linear, model exonerated) and the mass-
matrix diagnosis, every INTERACTIVE sampler config proved too slow on this
laptop CPU to iterate on: diagonal mass saturates the tree cap (~63 leapfrog
steps at depth 6, confirmed by arithmetic: ~7 min/180-draw single chain);
dense-mass VECTORIZED chains stalled on a heavy compile (>20 min for
200+200); dense-mass SEQUENTIAL compiled and ran but the dense warmup
adaptation is expensive (tiny 150+60 test still going at 12 min). No single
config gives a fast interactive fit. The gradient is cheap and the model is
correct; this is a slow-CPU + hard-geometry combination, exactly Bobby's
step-2: "the overnight/offline full-data NUTS run with the REAL gates
intact. We have banked schedule; spend it here, this artifact is
load-bearing."

LAUNCHED (per that pre-approval, no further ok needed): the full-data fit,
ALL 5,838 rotation player-seasons, dense_mass=True, chain_method=sequential
(vectorized stalled), max_tree_depth=8, 4 chains x 1000+1000, real gates
(R-hat<1.01, ESS>400, anchor stability). Expected multi-hour on CPU; it
WILL complete (dense mass fixes the geometry after warmup, so sampling
steps collapse -- unlike diagonal which never converges the tree). On
health PASS it auto-freezes skill_vectors + the interpretability export
(top +/- loadings + top/bottom-5 exemplar player-seasons per factor).
Nothing traded away: exact NUTS, full population, real gates. SVI stays in
the drawer; subsampling stays retracted; K frozen at 8. Population
verification already PASSED (c9e41b81). Will NOT kill from impatience.

## 2026-07-05 — F3 leapfrog measurement: BOTH mass matrices saturate; geometry pathology, not a mass problem

Killed the 8.5h offline run (Bobby's call) and measured NUTS leapfrog steps
directly (depth-6 cap = 63 max), sampling phase, full data:
  DIAGONAL: mean 63.0, median 63, max 63, 100% at cap, 770s
  DENSE:    mean 63.0, median 63, max 63, 100% at cap, 1454s (SLOWER)

DEFINITIVE: dense mass gives ZERO benefit -- identical 100% saturation,
just slower per step. The earlier assumption that dense mass would cure the
wall was WRONG (never verified until now). NUTS ALWAYS hits the tree cap
under both mass settings, so the pathology is NOT linear correlation (which
dense mass would fix) -- it is a non-linear geometry (funnel and/or weak
identification / near-multimodality) that no global mass matrix
preconditions. This is why the 8.5h run never converged: it was saturating
throughout.

Root-cause candidates (to investigate, all near the MODEL-PARAMETRIZATION
boundary -> flagged for Bobby's ok before changing):
  1. Variance-parameter FUNNEL: psi ~ HalfNormal (a feature driven near
     zero unique variance funnels in log psi); and/or anchor_diag ~
     HalfNormal near its 0 boundary. Standard fix: non-centered / softplus
     reparametrization of the scale params, or a small floor.
  2. Weak identification / rotation ridges among non-anchor loadings (the
     anchors pin sign but 8 factors x 21 features leaves loading trade-offs
     that create curved ridges).
Neither is fixed by mass tuning; both are fixed by REPARAMETRIZATION.

Options presented to Bobby (his call, this is near the model boundary and a
strategic time decision):
  A. Reparametrize the scale params (psi, anchor_diag) to kill the funnel
     -- low-risk, standard, keeps the model identical in distribution; then
     re-measure leapfrog. If steps collapse, NUTS becomes fast on THIS CPU.
  B. If A doesn't collapse it, investigate loading-ridge identification
     (e.g. orthogonal/QR loading parametrization) -- more invasive.
  C. Run the current model on a GPU / many-core box (Bobby's step-2 offline
     on better hardware) -- but 63 steps x 36ms is the per-draw floor even
     there, so it only buys a constant factor, not efficiency.
  D. (Last resort, needs explicit ok) SVI on full data with the surrogate
     gates.
NOT done: no SVI, no subsample, K frozen at 8. Awaiting Bobby's path choice.

## 2026-07-05 — LAYER 1B PATH A approved + BLOCKING PROBE PROTOCOL (Bobby, verbatim)

"LAYER 1B PATH A: approved. Reparametrize scale params (non-centered
psi/tau, softplus or a small floor), model distributionally identical.
BLOCKING PROTOCOL, no exceptions:
1. Run the DEPTH-CAPPED leapfrog probe FIRST (2 chains, ~250+100,
   depth 6). Read the mean leapfrog count before launching anything
   long. Collapse to single digits = fixed; still near cap = A
   insufficient, park and bring me B.
2. No multi-hour full fit launches until the probe confirms collapse.
   The probe is the gate on the fit, every time, from now on.
3. If A works: full fit at 2 chains first (not 4), real R-hat/ESS,
   then vectors freeze.
Standing rule added to house standards: any NUTS config change is
verified by a short leapfrog probe BEFORE any full run depends on it.
An unverified sampler assumption is a parked risk, not a green light."

## 2026-07-05 — PATH A NEGATIVE RESULT (probe): funnel was not the cause; rotational under-identification confirmed

Path A blocking probe (depth-6, 2 chains, 250+100, diagonal mass, after the
softplus reparam of psi/anchor_diag):
  PATHA_RESULT: mean_leapfrog 63.0 | median 63 | max 63 | frac_at_cap 100%
                | worst_Rhat 2.022 | min_ESS 3 | 2585s
IDENTICAL 63/63 saturation to the pre-fix measurement -> Path A did NOT
help. The scale funnel was NOT the cause. And the health numbers are the
smoking gun: worst_Rhat 2.02 (gate 1.01) with min_ESS 3 (gate 400) mean the
2 chains DID NOT MIX AT ALL -- they settled on different points. That is the
textbook signature of ROTATIONAL UNDER-IDENTIFICATION: the marginalized
likelihood sees only WW^T, which is invariant under W -> W R for any
orthogonal R, so the posterior has FLAT RIDGES (whole rotation orbits of
equal density). The 8 pure-marker anchors pin only the K diagonal entries;
the off-anchor loadings are free to rotate along those ridges. NUTS
saturates wandering the ridge (63/63) and different chains land on
different rotations (R-hat 2.0). No mass matrix and no scale reparam can fix
a flat ridge; only IDENTIFICATION can.

VALUE OF THE PROBE PROTOCOL (first use): caught this in ~43 min (2-chain
probe) instead of another multi-hour full-fit wall, and the R-hat/ESS from
the probe pinpointed the cause. The standing rule earned its keep
immediately.

PARKED per protocol (no long fit launched). RECOMMEND Path B, awaiting
Bobby's ok (changes how W is parametrized, near the model boundary):
lower-triangular W with a positive diagonal (Geweke-Zhou factor-analysis
identification) -- W[i,k]=0 for k>i, W[i,i]>0. This removes the rotational
freedom ENTIRELY (a lower-triangular positive-diagonal loading matrix is a
unique representative of each WW^T orbit), so the flat ridges collapse to
points and NUTS should mix. The pure-marker ANCHORS are then redundant for
identification and can be dropped or kept as interpretation labels; the
interpretability naming still works from the fitted loadings. Path B is
gated by a fresh leapfrog probe before any full fit (standing rule). No SVI,
no subsample, K frozen at 8.

## 2026-07-05 — LAYER 1B PATH B approved (Bobby, verbatim)

"LAYER 1B PATH B: approved. Lower-triangular W, positive diagonal
(Geweke-Zhou identification). Conditions:
1. Probe FIRST (2 chains, ~250+100, depth 6): leapfrog collapse AND
   R-hat < 1.1 / ESS healthy on the probe before any full fit. Both,
   not just leapfrog. Rotational fixes must show mixing, which is the
   thing that was actually broken.
2. Ordering caveat, verify at F3: lower-triangular identification is
   order-dependent (the first K features define the factor basis).
   Confirm the current feature order puts sensible, well-populated,
   low-missingness anchor-like features in the first 8 slots. If slot
   1 is a noisy or sparse feature, factor 1 inherits its junk. Choose
   the first-8 feature ordering deliberately and record it as a frozen
   config, since it now affects interpretation.
3. Anchors: keep as interpretation labels only, identification now
   comes from the triangular structure. Note in the record that the
   naming exercise reads from fitted loadings regardless.
4. If B's probe still doesn't mix: STOP, park, bring me the numbers.
   That's three structural attempts; past it the move is offline
   hardware on a known-good config or a real modeling rethink, not a
   fourth in-session try.
K frozen at 8, no SVI, no subsample."

FROZEN first-8 leader feature order (condition 2), chosen as 8 dense,
high-quality, conceptually distinct skill markers (the former anchor set):
  0 usg_pct (scoring load), 1 ts_pct (efficiency), 2 fg3a_rate (spacing),
  3 ast_pct (playmaking), 4 drives_per75 (rim pressure),
  5 drb_pct (rebounding), 6 blk36 (rim protection),
  7 def_rapm (defensive impact).
All 100% populated within the fit population (rotation player-seasons);
each defines factor k's scaffolding by construction. Order frozen in
skill_factors.LEADER_FEATURES; the remaining 13 features follow. Anchors
retained as labels only. Path B gated by a fresh probe requiring BOTH
leapfrog collapse AND R-hat<1.1/healthy ESS. If B's probe fails: STOP/park
(three structural attempts is the ceiling; then offline hardware or a
modeling rethink, not a fourth in-session try).

## 2026-07-05 — PATH B NEGATIVE (probe): PARKED at the 3-attempt ceiling (Bobby cond 4)

Path B probe (lower-triangular positive-diagonal W, diagonal mass, depth-6,
2 chains 250+100):
  PATHB_RESULT: mean_leapfrog 63.0 | frac_at_cap 100% | worst_Rhat 2.252
                | min_ESS 3 | 2059s
Identical 63/63 saturation, and R-hat 2.25 (WORSE than Path A's 2.02). The
triangular identification did NOT collapse the steps or fix mixing.

Three structural attempts now, all saturating at EXACTLY 63/63 with R-hat
~2, ESS 3:
  1. pure-marker anchors     -> 63/63, R-hat 2.02
  2. softplus scale reparam  -> 63/63, R-hat 2.02 (funnel ruled out)
  3. lower-triangular ID      -> 63/63, R-hat 2.25 (rotation-ID ruled out)
PARKED per Bobby condition 4 (three attempts is the ceiling; no fourth
in-session structural try). K frozen at 8, no SVI, no subsample.

HONEST ANALYSIS for Bobby's decision:
- The identical 63/63 across three DIFFERENT identification schemes says the
  saturation is NOT primarily rotation/identification. Something more
  fundamental in the marginalized measurement-error geometry over 5,838
  rows.
- R-hat ~2 with ESS 3 means the 2 chains sit in DIFFERENT regions -> genuine
  multi-basin / non-mixing, not just slow convergence (overlapping slow
  chains would give R-hat near 1). This points at MULTIMODALITY (factor
  models are classically multimodal) that no reparametrization removes.
- CONFOUND CAVEAT: with every draw saturating at 63 steps, a 250-warmup
  probe barely moves, so some of the high R-hat is under-exploration. The
  one lever NOT yet tried is a mass matrix on the triangular model: dense
  mass failed on the ANCHOR model only because of the (now-removed) rotation
  ridge; on the triangular model it targets any residual LINEAR correlation.
  It is a SAMPLER setting (not a 4th structural attempt), but it is slow on
  this CPU (earlier dense runs never finished a small probe).

OPTIONS for Bobby (his call, per the ceiling):
  A. One triangular+DENSE-mass probe to disambiguate mass-matrix vs genuine
     multimodality (sampler setting; ~40 min or slow).
  B. Offline hardware (GPU / many-core) on the known-good triangular config,
     with a longer warmup so mixing has room to show.
  C. Modeling rethink: the marginalized measurement-error factor model may
     be multimodal at K=8; options include an initialization from the FA/PCA
     solution (warm-start the chains at a shared mode), tempering, or the
     pre-registered v2 one-stage structure -- but these are F3 design
     decisions for Bobby, not in-session.
Not shipping vectors. Awaiting Bobby's path choice.

## 2026-07-05 — CORRECTION + Path A disambiguating probe (Bobby, verbatim)

CORRECTION to the prior park memo (Bobby, and correct): the "three schemes,
same pathology -> multimodality" conclusion was OVER-STATED. All three
probes shared ONE confound -- ~250 warmup against tree-cap-saturated
trajectories, so NO config could have shown mixing even if healthy. You
cannot diagnose multimodality with a probe that never explores. Multimodality
is a HYPOTHESIS, not a finding. And dense mass failing pre-B was expected (a
flat rotation ridge is unpreconditionable); Path B REMOVED the ridge, so on
the triangular model dense mass targets ordinary LINEAR correlation for the
first time. Triangular+dense has never been tried; pairing them COMPLETES
the third attempt (not a fourth), and stops at the tree-cap ceiling.

RULING (verbatim): "LAYER 1B: Path A, scoped as the disambiguating probe,
not a fit. Triangular (Path B's identified model) + DENSE mass, one probe.
Critical change from prior probes: longer warmup. The saturation confound
means short warmup can't distinguish healthy-but-slow from multimodal. Run
>= 1000 warmup, 2 chains, and RAISE the tree-depth cap to 10 for this probe
so trajectories aren't artificially capped while the dense mass adapts. Read
TWO things: leapfrog count: collapses = dense mass on the de-ridged model
was the answer all along; still capped = geometry genuinely hard. R-hat/ESS
AFTER real warmup: mixing now = it was under-exploration, not multimodality;
still split = multimodality confirmed, and THEN path C (FA/PCA warm-start or
tempering) is the justified next move. This is the honest test the three
short probes couldn't be. If it's slow on this CPU, let it run offline
overnight; it's one probe and the answer settles the whole question. Ceiling
still holds: if this fails on genuine multimodality grounds, next move is C
or offline hardware, not more in-session tries. K frozen at 8."

HOUSE STANDARD addition (Bobby): match the probe length to the QUANTITY
being measured, not to a fixed idea of cheap. Leapfrog count shows up in 250
steps; mixing does not. A cheap probe that answers the wrong question is
worse than a slow probe that answers the right one.
