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
