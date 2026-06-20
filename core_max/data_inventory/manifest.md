# Core Maximization — Data Inventory Manifest (Phase 0)

**Version:** 0.1.0
**As of:** 2026-06-19 (pre-draft; draft is June 23-24)
**Purpose:** the single, versioned record of every input the championship-equity
pipeline depends on (spec Section 8), with provenance, freshness, role, and known
quirks, plus the gaps that need filling and the cap reconciliations resolved in
Phase 0.

Reproducibility: all paths are repo-relative. The CBA gate and this inventory
re-run from `python core_max/run_gate.py` and `python core_max/tests/test_cba_gate.py`.
Constants are versioned (`league_year_constants.json`, built 2026-06-09). Seed
20260619 is pinned in `core_max/config/gate_config.json` (no sampling in Phase 0;
the seed is a convention carried forward).

---

## 1. Inputs by pipeline role

| Role (spec) | File | Format | Freshness / verified | Notes / quirks |
|---|---|---|---|---|
| Contracts (CBA gate) | `offseason/data/nba_contracts_2026_27_verified.csv` | CSV | 2026-06-18, VERIFIED (warehouse) | Canonical. Dead-money, kicker, NTC merged. Use this, not the legacy scrape. |
| Contracts (legacy) | `offseason/data/nba_contracts_2026_27.csv` | CSV | 2026-06-13, STALE | HoopsHype scrape. Fallback only; `build_team_state` prefers the verified file. |
| Cap-line constants | `offseason/data/league_year_constants.json` | JSON | built 2026-06-09, `is_projection: true` | 2026-27 is a researched projection; several `confirm` flags. Re-validate before publication. |
| Team-state rollup | `offseason/data/team_state.csv` / `.json` | CSV/JSON | 2026-06-18, derived | All 30 teams x 4 seasons + MIN subtraction scenarios. Apron + cap bases kept distinct. |
| Established-player impact | `offseason/data/player_value.csv` | CSV | 2026-06-13, VERIFIED | 3-season box-informed RAPM. Carries `off_sd`/`def_sd`/`net_sd` (analytic ridge posterior, NOT bootstrapped) and `box_net_bpm` (corr ~0.77 w/ RAPM). Phase 1 impact posteriors. |
| External impact check | `offseason/data/darko_dpm.json`, `darko-dpm-leaderboard.csv` | JSON/CSV | 2026-06-13, hand-entered | Corroboration / tiebreaker only. Not a pipeline input. |
| Offensive architecture (LAFI) | `postmortem/analyses/q0a_lafi/` + `postmortem/outputs/tables/q0a_lafi/lafi_composite_5component.csv` | code + CSV | 2026-06-13 | 5-component "Sharp LAFI". Fit-screening input, NOT a title-engine input. Re-validate any cited LAFI number against the pipeline. |
| Historical development | `offseason/data/cache/season_min_blk_2001_2026.csv` | CSV | 2026-06-13 | 12,369 player-seasons, AGE/MIN/BLK/box. BOX SCORE ONLY (see calibration note 4). Phase 2 comp-set raw material. |
| Age curve | `offseason/scripts/age_curve.py` | code | base | Point-estimate decline prior (peak 24-27). A reference, NOT the Phase 2 distribution. |
| Opponent strength substrate | `offseason/data/opponent_profiles.json`, `opponent_rosters.json` | JSON | 2026-06-13 | League identities + rotations. Phase 3 playoff-sim substrate. |
| Playoff / series sim | `offseason/scripts/{bracket_sim,build_series_calibration,series_resolver,build_rotation_model,build_team_ratings}.py` | code | base | A series/bracket layer already exists. Candidate Phase 3 reuse (audit before adopting). |
| Future picks ledger | `offseason/data/nba_draft_picks_future.csv` / `.json` | CSV/JSON | 2026-06-06 verified | Control ledger 2027-2033. MIN: 2 tradeable firsts (2028, 2033), 2032 frozen. |
| CBA compute engine | `offseason/scripts/{evaluate_move,chain_engine,build_team_state}.py` | code | maintained | Reused unchanged as the gate's compute core (see Section 4). |

---

## 2. MIN 2026-27 ground truth (from the verified rollup)

- **Apron team salary: $194,461,866** (over_cap_under_tax). Cap basis: $206,872,414.
- Distances: **$6.54M under the tax, $14.64M under the first apron, $27.54M under the second apron.**
- `num_under_contract`: 9 counted contracts (apron basis charges empty slots to 12 at the rookie min).
- TPE: largest single $10,774,038 (Conley), total $17,412,540. `can_aggregate`: true. Full MLE flagged available; taxpayer MLE not.
- Subtraction scenarios present: `s1_randle_out` $162.49M, `s2_gobert_out` $159.32M, `s3_both_out` $127.34M (under_cap).

---

## 3. Cap reconciliations resolved in Phase 0

1. **The stray $132.9M readback** was a partial subtotal that excluded the Gobert
   and Randle **player options** (~$69.8M combined; both count at value until
   declined). Add them back and you land at the canonical **$194.46M** apron. Not
   a contradiction, just a non-apron sub-total. RESOLVED.
2. **Luxury-tax line:** constants $201.0M vs spec $200.5M, a $0.5M gap that does
   NOT bind. MIN clears the tax by ~$6.54M under either line, and the second apron
   ($222M, identical in both) is the gate. First apron ($209.1M) is also identical.
   Documented; immaterial to the gate.
3. **Tax distance ($6.54M vs the spec's "~$8M"), pinned.** The engine compares the
   tax line to the APRON basis (there is no separate "tax salary" basis in this
   engine): $6,538,134 under = $201,000,000 (constants tax line) minus the
   $194,461,866 apron-basis team salary (guaranteed + player options + team options
   counted + empty-roster charges to 12 at the rookie min + dead money). The spec's
   "~$8M under" came from its earlier ~$193.4M team-salary snapshot against the tax
   line ($201.0M - $193.4M = ~$7.6M, rounded up). So the gap is the verified rollup
   being ~$1.06M higher than the spec snapshot plus rounding, NOT two different
   bases. The binding gate line (second apron $222M) reconciles cleanly at $27.54M
   under either way, which is why the gate is unaffected.

---

## 4. Phase 2 calibration design notes (locked guardrails, recorded now)

- **Box-to-impact bridge.** The title engine consumes impact (RAPM scale), but the
  only historical development data is box-score. Calibrate developmental
  trajectories in box-BPM space (computable historically; `box_net_bpm` exists in
  `player_value.csv`), then translate to the RAPM scale via the current
  cross-section relationship, carrying the translation uncertainty forward.
  Pre-register the map. This is the single place "confirmation bias with a Monte
  Carlo wrapper" can enter.
- **Archetype-condition the map (rim-protector residual).** Box-BPM adds
  one-directional BIAS against rim protectors (a shot-alterer who does not block
  gets little box credit; this is why Gobert reads as a role player in box and an
  anchor in RAPM). Joan is that archetype, so a single uniform box-to-RAPM map
  SYSTEMATICALLY buries him on the exact dimension the bet is about. The
  translation must be archetype-conditioned (or carry an explicit rim-protector
  residual term). Default error direction is too-pessimistic-on-Joan; correct it
  visibly and show the sensitivity.
- **Comp set (resolved 1/1/1/1):** broad, pre-registered structural pool (position
  group, draft-slot band around #17, entry-age band, minutes floor) with archetype
  as a covariate under hierarchical partial pooling. No hand-picked comps.

---

## 5. Gaps (net-new work; not in the repo)

- **Bayesian hierarchical infrastructure** (the Settlers approach) is NOT in the
  repo. New dependency required (PyMC or numpyro; current stack is
  numpy/pandas/scipy/sklearn/statsmodels, no sampler). Phase 2.
- **2026 draft-prospect data** (No. 28 / No. 59) is NOT in the repo. Source
  externally if/when the picks enter a scenario. Low priority for the core thesis.
- **Historical per-season IMPACT (RAPM) data** does not exist; only box-score
  history. This is why the box-to-impact bridge (note 4) is necessary.
- **Period-accurate historical CBA replay** (e.g., a fully period-accurate KAT
  trade) needs 2024-25 cap lines and 2024-25 team-state, neither in the repo.
  Constants start at 2025-26. The Phase 0 KAT test is therefore a STRUCTURAL
  (salary-shape) regression, not a period-accurate replay.

---

## 6. Phase 0 deliverable status

- **CBA gate:** built (`core_max/cba/gate.py`), config-driven
  (`core_max/config/`), reuses the verified engine via a single adapter
  (`core_max/cba/engine_bridge.py`). Returns PASS/FAIL with per-reason failures
  for (below 2nd apron), (Ayo retained), (roster filled).
- **Validation:** `core_max/tests/test_cba_gate.py` is **15/15**.
  - The three spec scenarios are all FEASIBLE (they differ on title equity, not
    legality): status_quo lands $209.60M (first-apron tier, only $12.40M under the
    2nd apron), fork_b lands $193.77M ($28.23M under), splash lands $206.13M
    ($15.87M under). Fork B opening room BELOW the tax while adding two fits and
    re-signing Ayo is the thesis, mechanically confirmed.
  - One FAIL per predicate is correctly rejected (illegal leg, above 2nd apron,
    Ayo dropped, roster too thin).
- **KAT structural regression:** legal, takes back less ($40.39M in vs $49.21M
  out), no take-back-more hard cap. PASS.
- **Engine known-answer suites (run, recorded):** `chain_engine.py` exits 0 (latch,
  TPE single-use, monotonicity all green). `evaluate_move.py` is **14/15**. The one
  failure is a STALE TEST, not a logic error (see finding below).

### Finding F1: full MLE no longer fits without shedding (and a stale engine test)

`evaluate_move.py` self-test #3 hardcodes the expectation that a full-MLE signing
"lands just under the first-apron hard cap" (legal=True). With the regenerated
verified-contract data, MIN's base apron is $194,461,866; adding the full MLE
($15,048,000) lands at **$209,509,866, which is $409,866 OVER the first apron**.
The engine correctly returns illegal; the test's hardcoded answer did not move
when the data did. Two takeaways: (1) the test is stale and would show a spurious
FAIL until its expectation is updated (offseason project's code; flagged, not
edited here); (2) the real finding stands: **at the current verified apron, MIN
cannot use the full mid-level exception without first shedding ~$0.41M+.** After
the Fork B shed (apron ~$193.77M), the full MLE fits again, barely ($0.28M under).
This reinforces the spec's "essentially no room without moving the bigs" premise.
