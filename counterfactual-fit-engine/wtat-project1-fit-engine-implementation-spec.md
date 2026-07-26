# Project 1 Implementation Spec
## The Counterfactual Fit Engine (Ant x LaMelo)

**Prepared:** July 2, 2026
**Parent document:** Wolves to a T Frontier Analytics Roadmap (Project 1)
**Intended consumer:** Claude Code implementation agent, with Bobby as reviewer
**Working name:** `fitengine`
**Ship target:** flagship piece late September 2026; skill-vector handoff to Project 2 (LAFI forecast) by mid-September

---

## 0. Plain-Language Overview

Anthony Edwards and LaMelo Ball have never shared an NBA floor. Every on/off split, two-man net rating, and lineup number for the pairing is undefined, so every take about their fit is currently a vibe. This project builds the thing that can answer the question anyway: a model that has watched every five-man lineup the league has run since 2014, learned how player skills interact when combined (which pairings are redundant, which are complementary, what happens to turnovers and shot quality when two ball-dominant creators coexist), and can therefore evaluate lineups that do not exist yet.

Three layers. First, turn every player-season into a small vector of latent skills (rim pressure, pull-up gravity, connective passing, point-of-attack defense, and so on), estimated from adjusted plus-minus data with box-score and tracking priors. Second, train a synergy function that maps any five skill vectors against any opposing five to an expected net rating, learned from twelve seasons of real lineups. Third, feed it hypothetical Wolves fives containing LaMelo, with full uncertainty carried through, and read out the distribution.

The credibility centerpiece mirrors pick2033's Nets replay: run the engine as-of February 1, 2025 on the Luka Doncic trade and show what it predicted before those lineups ever played. And the whole build runs under the pick2033 discipline: sealed test sets, pre-registered gates, decision memos, and a public prediction log, because "a projected net rating for a lineup that has never existed" is the most dunk-able number this publication will ever print, and the armor is the process.

One honest posture, stated up front: it is possible that lineup-level interaction effects are small relative to raw talent at this data resolution. If the model cannot beat a simple additive baseline, that is not a failed project. It is a publishable finding ("fit is mostly a myth at the resolution public data can see"), exactly the way the franchise-DNA tau finding turned a red gate into the Stage 2 lead. The project is designed so either outcome is a story.

---

## 1. Objective, Scope, and Non-Goals

### Objective

Produce posterior net-rating distributions for hypothetical Minnesota lineups containing LaMelo Ball, a pre-registered redundancy score for the Edwards-Ball pairing, and a validated lineup board for the 2026-27 Wolves, with every number carrying calibrated intervals, validated against historical trades whose outcomes the model never saw.

### In Scope

- League-wide play-by-play acquisition and a stint/lineup warehouse, 2013-14 through 2025-26 (Layer 0).
- Multi-season regularized adjusted plus-minus with box/tracking priors (Layer 1a).
- Bayesian latent skill factor model producing player-season skill vectors with posteriors (Layer 1b).
- A lineup synergy function trained on all lineups since 2014, with a leakage-proof temporal feature regime (Layer 2).
- A query engine for counterfactual lineups: the Wolves board, the redundancy score, opponent-context evaluation (Layer 3).
- The historical trade backtest with a sealed 2022-2026 test window and the Luka-AD showcase replay.
- Skill-vector export contract for Project 2 (the generative possession model consumes these embeddings).
- Publication draft with slots, same discipline as the pricing series.

### Non-Goals (Explicitly Out of Scope for v1)

- No rotation prediction. The engine evaluates lineups it is given; it does not predict which lineups a coach will play. Backtests condition on the lineups that actually played.
- No injury modeling. Availability is a query-time input (config flags per player), not a modeled process.
- No spatial/tracking-coordinate features beyond the public aggregates (that is Project 6's unlock).
- No possession-sequence generation (that is Project 2, which consumes this project's vectors).
- No in-season retraining pipeline in v1; one pre-season build, one pre-registered mid-season grading checkpoint.

---

## 2. Deliverables

### Published Outputs

| # | Deliverable | Ships |
|---|---|---|
| 1 | The flagship: "The Fit Engine" piece with the Edwards-Ball redundancy score, the Wolves lineup board with intervals, and the honest size of fit effects league-wide | Late September |
| 2 | The trust centerpiece inside it: the Luka-AD replay (engine run as-of Feb 1, 2025, predictions vs what those lineups actually did) | Same piece |
| 3 | Pre-season lineup board published with a pre-registered grading date (All-Star break), so the model is publicly falsifiable | Opening week |
| 4 | Skill-vector handoff artifact to Project 2 | Mid-September (internal) |

### Code Artifacts

- `fitengine/` repository (Section 5) with reproducible, seeded runs.
- DuckDB warehouse: games, events, stints, lineup observations, player features, skill vectors.
- Posterior sample files for Layer 1; ensemble checkpoints for Layer 2.
- Trade-backtest harness with the sealed-window protocol encoded.
- JSON export bundle per Section 12 contracts.
- Auto-generated validation report; `decisions.md`, `predictions.md`, and session logs in the house format.

---

## 3. Inherited Standards (from pick2033, binding here)

1. **Sealed evaluation.** Development and sealed test windows are declared in this spec before any model exists. Sealed windows get exactly one look. No threshold revisions after results.
2. **Gate failures are parked, not patched.** A failing gate produces a decision memo with options; Bobby rules; the ruling and rationale enter `decisions.md` verbatim.
3. **Predictions log.** Directional predictions are timestamped in `predictions.md` before the runs that grade them, and graded in public either way.
4. **The three gate-design lessons, applied here:**
   - Long-horizon point-skill gates against near-unbeatable baselines are near-unwinnable by construction. Concretely: the additive baseline in G4 is this project's "pooled reversion," so the gate is written as "beats additive with clustered significance OR the null is promoted to the finding," not as an unconditional must-beat.
   - Convergence and consistency checks reference the model's own terminal or stationary state, symmetric in direction.
   - Conditional transients are not gated against unconditional references.
5. **Quarantine discipline.** Provisional numbers are tagged, never quoted in prose except when explicitly graded, and headline artifacts prefer FINAL tags by designation, never by file recency.
6. **Complexity must be earned.** Every v2 escalation (one-stage factor model, exotic architectures) requires a named gate failure of the v1.

---

## 4. System Architecture and Data Flow

```
                      NBA Stats API (nba_api)
              pbp + boxscores, 2013-14 .. 2025-26 (~15k games)
                              |
                              v
  +-----------------------------------------------------------+
  |  LAYER 0: cached pulls -> stint builder -> lineup warehouse |
  |  (reuses LAFI possession segmentation; G1 gates)            |
  +-----------------------------------------------------------+
        |                                        |
        v                                        v
  +--------------------+              +---------------------------+
  |  LAYER 1a           |              |  public box/tracking       |
  |  multi-season ridge |              |  aggregates (priors +      |
  |  RAPM (O and D)     |              |  factor-model features)    |
  +--------------------+              +---------------------------+
        \                                        /
         v                                      v
  +-----------------------------------------------------------+
  |  LAYER 1b: Bayesian latent skill factor model               |
  |  player-season vectors z in R^K with posteriors (G2 gates)  |
  +-----------------------------------------------------------+
                              |
             z from LAST AVAILABLE season only (leakage rule)
                              v
  +-----------------------------------------------------------+
  |  LAYER 2: synergy function f(offense five, defense five,    |
  |  context) -> points per 100; ensembles + conformal (G3)     |
  +-----------------------------------------------------------+
                              |
                              v
  +-----------------------------------------------------------+
  |  LAYER 3: query engine: Wolves board, redundancy score,     |
  |  reference-opponent evaluation (G5)                         |
  +-----------------------------------------------------------+
                              |
              +---------------+----------------+
              v                                v
   Trade backtest harness (G4,          JSON exports (D3 site),
   dev 2015-21 / SEALED 22-26,          skill-vector handoff to
   Luka-AD showcase)                    Project 2
```

The leakage rule in the middle is the architectural spine: the synergy function is trained and evaluated exclusively on skill vectors from seasons strictly before the target lineups, because that is the only mode the LaMelo query can ever run in (his vectors come from Charlotte 2025-26; the lineups are Minnesota 2026-27). Training in deployment mode is what makes the backtest honest.

---

## 5. Repository Layout and Environment

```
fitengine/
  README.md
  config/
    model_params.yaml        # K set, priors, ensemble size, seeds
    backtest_protocol.yaml   # inclusion rules, dev/sealed windows (frozen)
    query_roster.yaml        # Wolves candidates + availability flags (build-time)
    redundancy_def.yaml      # pre-registered redundancy definition
  data/
    raw/nba_api/             # permanent JSON cache, resumable
    staged/
    warehouse.duckdb
  src/
    etl/
      nba_client.py          # cache-first, throttled, resumable
      pull_games.py          # schedule -> game ids
      pull_pbp.py            # events per game
      pull_box.py            # boxscores incl. period starters
      aggregates.py          # box/tracking priors + factor features
    stints/
      period_starters.py
      sub_repair.py
      stint_builder.py
      possessions.py         # adapter around the canonical LAFI parser
    models/
      rapm.py                # Layer 1a
      skill_factors.py       # Layer 1b (PPL stack per pick2033 D4 decision)
      synergy.py             # Layer 2 (torch), gbm_floor.py baseline
      conformal.py
    query/
      reference_opponents.py
      lineup_board.py
      redundancy.py
    validation/
      gates.py
      trade_backtest.py
      luka_replay.py
      report.py
    viz/
      export_json.py
  tests/
  docs/
    decisions.md
    predictions.md
    session_logs/
  outputs/
    posteriors/  ensembles/  sims/  json/  validation_report.md
```

**Environment notes (inherited realities):** Windows, global Python 3.13, per-project venv. The Bayesian stack is whichever won pick2033's D4 smoke test; reuse that decision, do not re-litigate. Layer 2 uses PyTorch CPU wheels (small networks; ensemble training is hours, not days). The Postgres warehouse (<SERVER_LAN_IP>, never localhost) is available for cross-validation joins but the primary store is DuckDB, matching house convention.

**Data-use note:** NBA Stats API pulls are for analysis; raw play-by-play dumps are never redistributed. Published artifacts are derived metrics and charts only. Same posture as broadcast-derived work: analyze, do not redistribute the source.

---

## 6. Data Acquisition (Layer 0, the long pole)

### Volume and endpoints

- Seasons 2013-14 through 2025-26, regular season (playoffs pulled too, flagged, excluded from training; used only as diagnostic).
- Roughly 15,000 games, two primary endpoints per game (play-by-play; boxscore with period-level data for starter inference), plus season-level aggregate endpoints for priors. Order of 31,000 requests.
- **Wall-clock reality:** at a respectful 1.5-2.5s effective spacing with retries, the full pull is 15 to 25 hours. It runs as resumable background chunks across sessions, cache-first and permanent, exactly the bref_client pattern. The pull starts in session F0 and everything else in F0/F1 proceeds against partial cache.

### Client requirements (`nba_client.py`)

- Cache-first: a cached response is never re-fetched; parsers run against cache only.
- Randomized 1.5-2.5s sleep after network fetches; exponential backoff honoring Retry-After; loud fail after 5 consecutive errors (stats.nba.com throttles hard and silently; detect stall, checkpoint, resume).
- Checkpoint file per season; a single command resumes the global pull.
- Parser regression tests against cached fixtures only.

### Known nastiness to plan for (not discover)

Play-by-play substitution data is famously dirty. The stint builder (Section 8.1) is specced around the known failure modes: players who play entire periods without a substitution event, technical-foul free throws shot by players not on the floor, substitutions during free throws, missing sub-out events, and overtime period boundaries. These are engineering problems with known solutions; G1's minutes-reconciliation gate is the proof they were solved.

---

## 7. Data Schemas (contracts, enforced by tests)

### 7.1 `stints`

One row per unique on-court configuration segment.

| column | type | notes |
|---|---|---|
| stint_id | text | game_id + sequence |
| game_id, season, period | | playoffs flagged |
| home_lineup, away_lineup | text[5] each | sorted player ids |
| secs | float | wall-clock seconds on floor |
| poss_home, poss_away | float | canonical LAFI possession definitions |
| pts_home, pts_away | int | |
| start_margin, home_rest, away_rest | | context covariates |

### 7.2 `lineup_obs` (Layer 2 training rows)

Directional aggregation: each stint contributes two rows (home offense vs away defense, and the reverse), then rows are aggregated per (season, offense five, defense five) matchup with possession weights. Columns: season, off_lineup, def_lineup, poss, pts_per100, home flag share, mean rest delta.

### 7.3 `player_features` (Layer 1b inputs)

Player-season: minutes, usage, TS%, 3PAr, FTr, AST%, TOV%, ORB%/DRB%, STL%, BLK%, plus public tracking aggregates (drives per 75, catch-and-shoot vs pull-up 3PA split, average speed, contested rebound rate, rim FG% allowed where available), plus Layer 1a outputs (O-RAPM, D-RAPM with SEs). Tracking aggregates exist 2013-14 onward, which is why the panel starts there.

### 7.4 `skill_vectors` (the handoff artifact)

player_id, season, K posterior sample matrix (S x K), posterior mean, minutes. **This schema is the Project 2 interface; freeze it in F3 and version it.** Project 2's possession transformer conditions on these vectors; design decisions here propagate.

---

## 8. Component Specifications

### 8.1 Stint Builder (the grind, and where the project is won or lost)

**Period starters:** derived from the boxscore period data where available; otherwise inferred by first-action-before-first-sub heuristics with a repair pass. Every period of every game must resolve to exactly five per side before stint construction runs.

**Substitution repair rules (ordered):** (1) apply subs at the possession boundary consistent with FT micro-rules (players subbed during FTs enter after the final attempt); (2) technical/flagrant FT shooters do not alter lineups; (3) a player with events but no sub-in is back-filled to the earliest consistent boundary; (4) a player with a sub-in and no sub-out is closed at period end; (5) any period that cannot resolve to 5v5 after repair is quarantined and logged, never silently dropped.

**G1 gates (Section 9) are the definition of done here.** The reconciliation standard: reconstructed player-game minutes match official boxscore minutes within 0.5 minutes for at least 99.5% of player-games; team on-floor seconds are exact; possession counts match the canonical LAFI parser within 0.5% at the season level; quarantine rate below 0.5% of periods.

### 8.2 Layer 1a: Multi-Season Ridge RAPM

- Offense and defense estimated separately on the stint design matrix, points per 100 possessions as the target, possession-weighted.
- Per-season estimates with an informative prior mean per player: a shrunk blend of the previous season's estimate (aged one year via the Project-4 Model C curves, which already exist) and a box-score composite prior. This is the standard stabilization that makes single-season RAPM usable; it is a linear solve, seconds per season.
- Regularization strength chosen by generalized cross-validation on development seasons only (2015-2021); frozen before any sealed-window work.
- Uncertainty: game-level block bootstrap (200 resamples) for per-player SEs feeding Layer 1b.

### 8.3 Layer 1b: Bayesian Latent Skill Factor Model

**v1 is deliberately two-stage** (factor model on the player-feature matrix including RAPM, rather than a factor structure inside the stint regression). Rationale: the one-stage model is a ~500k-row hierarchical regression with ~50k latent parameters, a real computational and identification risk; the two-stage version is a ~6,500 player-season x ~25 feature matrix, fits in minutes, and loses little when the features already include the RAPM signal with its SEs. **One-stage is the pre-registered v2, buildable only if G2 or G3 shows the two-stage information loss matters.**

- Model: hierarchical Bayesian factor analysis with measurement-error-aware likelihood for the RAPM columns (their bootstrap SEs enter the noise term), K latent dimensions, sparsity-inducing priors on loadings plus anchor variables for identification (one designated anchor feature per factor with a positivity constraint, so factors do not rotate arbitrarily between fits).
- **K selection, pre-registered:** K in {6, 8, 10}, chosen by held-out feature reconstruction on development seasons plus downstream G3 performance on development seasons only. K is frozen before the sealed backtest. Interpretability labels ("rim pressure," "connective passing") are post-hoc descriptions for publication, explicitly not load-bearing.
- Health gates: R-hat < 1.01, bulk ESS > 400; reconstruction must beat a plain PCA at the same K on held-out players (if a linear PCA ties the Bayesian model, the posterior machinery is not earning its keep and the memo says so).

### 8.4 Layer 2: The Synergy Function

**Target:** points per 100 possessions of offense-five vs defense-five, on `lineup_obs` rows, possession-weighted, with season fixed effects (the 2014-2026 scoring-environment drift is large and must not leak into skill interactions), home share, and rest delta as nuisance covariates.

**The leakage rule (binding, tested):** all player features entering a season-s training or evaluation row are the skill vectors from that player's most recent season strictly before s, aged one year by the Model C curves. Rookies and players with no prior season get an archetype prior (draft-slot and position keyed). This exactly matches deployment (LaMelo's Charlotte 2025-26 vector, aged, queried in Minnesota 2026-27 lineups) and kills the circularity where a lineup's outcome trained the very vectors predicting it. A within-season mode may be computed as a diagnostic; it never touches a gate.

**Architectures, in build order:**
1. **GBM floor (mandatory first):** gradient-boosted trees on engineered features: sums, means, and extremes of the ten vectors per skill dim, offense-minus-defense contrasts, and explicit pairwise redundancy features (pairwise cosine overlaps in the creation subspace). This is the baseline the neural model must beat, and it may be embarrassingly strong; if it is, that is the finding.
2. **Primary: permutation-invariant set-attention network.** Embed each player's z; self-attention within the offense set (pairwise interactions are the entire point); cross-attention offense-to-defense; pooled readout plus context covariates. Small: two attention blocks, width 64-128. A GNN formulation (10 nodes, team-typed edges, message passing) is an accepted alternative primary given the MaxPreps experience; the choice between set-attention and GNN is made on development seasons and is an implementation detail, not a philosophy. What is non-negotiable is explicit pairwise interaction structure and permutation invariance.
3. **Uncertainty:** deep ensemble (8 seeds) over the primary, composed with Layer 1b posterior sampling (draw z samples, push through ensemble members), then a **split-conformal calibration wrapper** fit on a held-out development season so published intervals carry finite-sample coverage guarantees. Conformal is cheap and turns "the intervals look reasonable" into a gated property.

### 8.5 Layer 3: The Query Engine

- **Reference opponents:** a lineup's headline net rating is its expected margin against the league: offense evaluated against a minutes-weighted sample of the prior season's defensive lineups, defense evaluated against the same sample's offenses. The reference set definition is frozen in config before any Wolves numbers are computed.
- **The Wolves board:** every plausible five from `query_roster.yaml` (current roster at build time, availability flags per player, DiVincenzo's Achilles status a config flag, never hardcoded), ranked by posterior mean with 80% intervals, plus the sensitivity view the roadmap promised: how the projection swings by who plays the 4.
- **The redundancy score, pre-registered in `redundancy_def.yaml`:** the model-based double difference. For pair (i, j) in a context lineup C: f(C + i + j) - f(C + i + r) - f(C + j + r) + f(C + r + r'), where r, r' are replacement-archetype vectors at the relevant positional archetypes, averaged over a fixed set of context lineups and reference defenses. Positive means complementary, negative means redundant, units are net-rating points. The descriptive creation-subspace cosine overlap is computed as a secondary illustration only. The Edwards-Ball value of this quantity is the headline number of the flagship piece, so its definition freezes now, before anyone sees it.

---

## 9. Validation Gates and the Sealed Protocol

All gates land in the auto-generated validation report. Failures produce decision memos, never silent retunes.

### G1: Data Integrity (Layer 0)

| Gate | Criterion |
|---|---|
| Minutes reconciliation | >= 99.5% of player-games within 0.5 min of official; team seconds exact |
| Possession parity | Season-level possession counts within 0.5% of the canonical LAFI parser |
| Lineup validity | Zero non-5v5 stints in the warehouse; quarantine rate < 0.5% of periods, logged |
| Coverage | Every scheduled regular-season game present or explicitly logged missing |

### G2: Layer 1 (skills)

| Gate | Criterion |
|---|---|
| RAPM stability | Year-over-year correlation of O-RAPM and D-RAPM in the 0.50-0.75 band (too low = noise, too high = over-shrunk prior) |
| Face validity | Top-20 lists per season published as narrative checks, not fitted-to |
| Factor health | R-hat < 1.01, ESS > 400; held-out reconstruction beats PCA at same K |
| Anchor stability | Factor-anchor loadings sign-stable across refits and dev seasons |

### G3: Layer 2 (synergy, development seasons)

| Gate | Criterion |
|---|---|
| Skill vs additive | Possession-weighted RMSE on temporal holdout (train <= s-1, test s, for s in 2019-2021) beats the additive-z linear baseline, clustered by team-season |
| Skill vs floor | Primary beats or ties the GBM floor; if the floor wins, the floor ships and the memo says why |
| Coverage | Conformal 80% intervals achieve [76, 88] on the held-out season |
| Environment sanity | Season fixed effects recover the known league scoring drift direction |

### G4: The Trade Backtest (the crown jewel, sealed)

**Protocol, frozen in `backtest_protocol.yaml` before any model exists:**
- **Universe:** every trade or signing since 2015-16 where an incoming top-100-minutes player logged >= 1,500 possessions with the new team across >= 3 distinct five-man lineups. Mechanical inclusion, no cherry-picking.
- **Task:** with data frozen as-of the transaction date (prior-season vectors only), predict the net ratings of the post-move lineups that actually played; score against realized outcomes, possession-weighted.
- **Baselines:** (a) additive sum of prior-season impact estimates; (b) league-average prior; (c) previous-team lineup carryover.
- **Windows:** development = 2015-16 through 2020-21 transactions, iterate freely. **SEALED = 2021-22 through 2025-26 transactions, exactly one evaluation, after all modeling choices are frozen.**
- **Sealed gates:** beat baseline (a) on possession-weighted RMSE with origin-clustered significance, OR the pre-committed null posture activates (the finding becomes "fit effects at public-data resolution are worth X, which is small," published with the same prominence a win would get). Coverage of 80% intervals in [72, 88] on sealed cases regardless.
- **The showcase inside the sealed window:** the February 2025 Luka Doncic / Anthony Davis trade. The engine runs as-of February 1, 2025 and its predictions for the actual post-trade Lakers and Mavericks lineups print against reality, hit or miss. This is the piece's Nets-replay moment and it is graded in public.

### G5: Deployment Sanity

| Gate | Criterion |
|---|---|
| Known-lineup reproduction | Predict 2025-26 Wolves lineups from 2024-25 vectors; possession-weighted rank correlation with realized >= 0.5 |
| Famous-fit panel | Narrative checks (documented, not fitted-to): does the engine, from 2014-15 vectors, grade the 2015-16 Warriors small lineup as elite; does it flag known-toxic pairings |
| Query stability | Wolves board rankings stable under posterior resampling (top-3 fives unchanged in >= 80% of draws) |

---

## 10. Pre-Registered Predictions (into `predictions.md` at F0)

- **P-F1:** the interaction layer improves on the additive baseline by a small but real margin, 1-4% possession-weighted RMSE on the sealed window, not more. (Fit is real and modest; anyone promising huge fit effects from public data is overfitting.)
- **P-F2:** the Edwards-Ball redundancy score comes out negative but small relative to their combined talent: the pairing is a net strong lineup with a measurable redundancy tax, not a broken one. Direction and rough magnitude logged now, graded when the frozen definition is first computed.
- **P-F3:** the model's largest positive interaction terms league-wide involve elite spacing bigs next to rim-pressure creators. A sanity prediction about what the machine should discover if it works.

---

## 11. Milestones and Sessions

| # | Session | Contents | Est. | Gate |
|---|---|---|---|---|
| F0 | Scaffold + pull kickoff | Repo, venv, nba_client with resume, pull running in background, schema contracts, protocol + predictions frozen | 2d + background pull | contracts green |
| F1 | Stint builder | Period starters, sub repair, LAFI possession adapter, full warehouse build | 4-6d | G1 |
| F2 | Layer 1a | Ridge RAPM, priors, bootstrap SEs | 2-3d | G2 (RAPM rows) |
| F3 | Layer 1b | Factor model, K selection on dev, skill_vectors freeze + Project 2 handoff schema | 3-4d | G2 (factor rows) |
| F4 | Layer 2 | GBM floor, set-attention primary, ensembles, conformal | 4-6d | G3 |
| F5 | Backtest | Harness, dev iteration, freeze, SEALED one-shot incl. Luka showcase | 3-4d | G4 |
| F6 | Query + ship | Reference opponents, Wolves board, redundancy, exports, flagship draft with slots | 3d | G5 |

Elapsed calendar: 4 to 7 weeks, dominated by the F0 pull wall-clock and F1's edge cases. F2-F4 iterate on development seasons while later pull chunks land. The pick2033 calendar interleaves cleanly: July 6 is buttons, Parts 2-3 are drafted, and fitengine sessions fill the gaps. Hard personal deadline honored: flagship ships before October.

---

## 12. Export Contracts (D3 / site)

```
outputs/json/
  wolves_lineup_board.json    [{lineup: [ids], names, mean, lo80, hi80,
                                vs_baseline_additive, poss_note}]
  redundancy_matrix.json      {pairs: [{i, j, score_mean, lo80, hi80}],
                                definition_version}
  edwards_ball_headline.json  {redundancy, interval, context_set_version,
                                plain_sentence}
  four_slot_sensitivity.json  [{four_option, board_delta, interval}]
  luka_replay.json            {asof_date, lineups: [{pred, interval,
                                realized, poss}], verdict}
  backtest_scorecard.json     {dev, sealed: {rmse_model, rmse_additive,
                                coverage, n_cases}, null_posture_flag}
```

Every JSON carries the meta block (seed, data hashes, code version, timestamp). FINAL tags by designation.

---

## 13. Risks and Mitigations

- **Interaction signal may be small.** The central scientific risk, and it is pre-committed as a publishable outcome (Section 0, G4 null posture, P-F1). The project cannot lose this bet, only report it.
- **Leakage is the silent killer.** Mitigated architecturally (the temporal feature rule is the training mode, not a filter), and tested: a leakage canary test asserts no season-s stint contributes to any vector used in a season-s row.
- **Stint construction errors poison everything upstream.** G1 is the hardest gate in the project on purpose; nothing fits until it is green.
- **nba_api instability.** Cache-first, resumable, checkpointed; the pull starting on day one is the schedule protection.
- **Era drift 2014-2026.** Season fixed effects plus the temporal training regime; a dev-only diagnostic checks whether interaction terms drift across eras, and if they do, recency weighting is the pre-declared v2.
- **Redundancy-score gaming risk (ours).** The definition freezes before computation; the headline number cannot be definition-shopped after the fact.
- **DiVincenzo and roster churn.** Availability and roster are query-time config, refreshed at publication; the engine is roster-agnostic by design.

---

## 14. Open Questions for Bobby (none blocking F0-F2)

1. K set {6, 8, 10} acceptable, or widen?
2. Backtest inclusion thresholds (1,500 possessions, 3 lineups, top-100 minutes): ratify or adjust before the protocol freezes at F0.
3. Replacement-archetype construction for the redundancy definition: positional archetype means at the 25th percentile of minutes-weighted impact (proposed), or a different reference?
4. Flagship format: single long piece vs a two-parter (methods + board). Recommendation: single piece with the Luka replay mid-piece, board as the closer, carousel companion after.
5. Pre-season falsifiability checkpoint: All-Star break (proposed) or 25-game mark?

---

## Appendix A: Definition of Done

All gates green or red-with-ruling in the validation report; the sealed window evaluated exactly once; the leakage canary green; a single command reproduces warehouse-to-exports under the configured seed; the Edwards-Ball redundancy number exists with an interval under the frozen definition; the Luka replay is graded in public; the flagship has shipped; and the skill_vectors artifact is versioned and consumed by Project 2's kickoff.

## Appendix B: First Agent Session (F0)

Scaffold the repo per Section 5; stand up nba_client with cache/resume and start the season pulls oldest-first in the background; freeze `backtest_protocol.yaml` and `redundancy_def.yaml` drafts for Bobby's ratification; write `predictions.md` P-F1 through P-F3 with timestamps; land schema-contract tests green against fixture games; end the session with the pull checkpoint file showing progress and an ETA for full cache.

*End of spec.*

---

## 15. v1.1 Amendments (pre-F0, from the comprehensiveness audit)

Adopted before any code exists; these supersede the corresponding v1.0 text.

**A1. Full covariance handoff between stages (amends 8.2/8.3).** Layer 1a passes the analytic per-season RAPM posterior covariance (available in closed form from the ridge solve) into Layer 1b's likelihood, not just marginal SEs. This recovers the cross-player error structure (teammates confounded together) that motivates the one-stage model, at zero identification risk. The block covariance for players sharing >= 500 possessions is retained exactly; the remainder is diagonalized.

**A2. Dimension-specific vector aging (amends 8.4's leakage-regime aging).** Once the z panel exists (F3), estimate per-dimension aging deltas from the panel itself (hierarchical, same delta-method form as Model C) and use those for the one-year aging step in the temporal feature regime. Model C's BPM curves remain as priors only. Rationale: athleticism-loaded dimensions and skill-loaded dimensions age differently; borrowing a scalar BPM curve blurs that.

**A3. Leverage weighting (amends 7.2/8.4).** Lineup observations are weighted by possessions times a leverage factor from the canonical LAFI leverage definition, downweighting garbage time rather than dropping it. The weighting rule is frozen at F1 before any Layer 2 fit.

**A4. Scheme ablation, pre-registered (amends 8.4).** A team-season random intercept in Layer 2 is fit as a development-season ablation: included in the primary iff it improves the temporal holdout. If included, Wolves queries use Minnesota's intercept, with a league-mean-intercept sensitivity reported alongside.

**A5. End-to-end embedding tripwire (amends Section 3's earned-complexity path).** A dev-only diagnostic arm trains learned player embeddings directly on lineup outcomes (no factor bottleneck). If it beats the factor-vector primary on the G3 temporal holdout by more than the clustered noise band, that is the named trigger for the one-stage v2 discussion. It never touches the sealed window and never ships.

**A6. Noise-floor reporting (amends G4 and P-F1).** Split-half reliability of realized lineup net ratings establishes the explainable-variance ceiling per backtest case set. G4 results and the P-F1 grade report skill both as raw possession-weighted RMSE and as a fraction of the achievable ceiling, so "small improvement" is judged against what the data can actually support.

**Reaffirmed ceilings (unchanged, stated for the record):** no spatial features (Project 6's unlock), no rotation prediction, two-stage skill estimation as v1 with A1 narrowing the gap and A5 as the data-driven trigger for escalation.

*End of v1.1 amendments.*
