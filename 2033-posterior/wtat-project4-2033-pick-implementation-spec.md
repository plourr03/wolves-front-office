# Project 4 Implementation Spec
## The 2033 Pick Posterior and Swap Option Pricing

**Prepared:** July 1, 2026
**Parent document:** Wolves to a T Frontier Analytics Roadmap (Project 4)
**Intended consumer:** Claude Code implementation agent, with Bobby as reviewer
**Working name:** `pick2033`

---

## 0. Plain-Language Overview

The Wolves sent Charlotte an unprotected 2033 first-round pick and three pick swaps in the LaMelo Ball trade. Right now the cost of those assets is a feeling. This project turns it into a number with error bars.

The approach in one paragraph: build a statistical model of how NBA franchises rise and fall over long horizons (trained on 40+ years of history), a model of when stars leave their teams (trained on every star tenure since 1990), and a model of how players age. Use those three models to simulate the Wolves and Hornets thousands of times from 2027 through 2033, season by season, inside a full simulated league with real lottery mechanics. Every simulation produces a draft slot for the 2033 pick and an outcome for each swap. Convert slots to value, price the swaps the way a quant prices options (they only pay off in the specific futures where Charlotte's pick beats Minnesota's), and feed everything into the existing Joan Bet championship-equity framework so the final answer reads in the same units as all prior Wolves to a T work.

The output is three publishable stages: the Anthony Edwards retention hazard curve, the 2033 pick posterior, and the full priced trade cost.

---

## 1. Objective, Scope, and Non-Goals

### Objective

Produce a full posterior distribution over the value of the outgoing draft assets in the LaMelo trade (the unprotected 2033 first, three swaps, and second-round picks), expressed in (a) draft-slot terms, (b) surplus-value terms, and (c) Joan Bet championship-equity terms, with every number carrying credible intervals and a scenario decomposition.

### In Scope

- Franchise trajectory model for all 30 teams (Model A).
- Star retention hazard model, applied to Anthony Edwards and to Charlotte's core (Model B).
- Archetype-specific aging curves with survivor-bias handling (Model C).
- Two-tier league simulation engine, 2026-27 through 2032-33, with exact lottery mechanics (Engine D).
- Draft-slot value curves with uncertainty (Model E1) and Monte Carlo swap option pricing (E2).
- Joan Bet integration adapter (F).
- Validation suite including historical replays of famous distant-pick trades.
- Visualization-ready JSON exports for the Flutter/D3 site.

### Non-Goals (Explicitly Out of Scope for v1)

- No injury modeling beyond what is implicit in historical franchise trajectories.
- No modeling of future trades by either franchise (the simulation evolves rosters only through aging and star departure; franchise-level priors absorb the rest).
- No cause attribution for star departures (trade demand vs. free agency vs. team-initiated all count as one event type in v1).
- No re-litigation of the on-court trade evaluation; the clean-room team-strength assessment stands. This project prices the asset side only.
- No play-in tournament micro-mechanics (approximation documented in Section 7.5).

---

## 2. Deliverables

### Published Outputs (Three Stages)

| Stage | Deliverable | Ships After |
|---|---|---|
| 1 | The Edwards retention hazard curve: annual and cumulative departure probability 2027-2033 with intervals, plus the league-wide star-tenure findings behind it | Milestone M2 |
| 2 | The 2033 pick posterior: full distribution over draft slot, P(top-4), P(top-10), P(lottery), and the win-total fan charts for both franchises | Milestone M4 |
| 3 | The priced trade: option values for all three swaps with exercise probabilities and scenario decomposition, plus the total asset cost restated in championship equity | Milestone M6 |

### Code Artifacts

- `pick2033` repository (structure in Section 4) with reproducible, seeded runs.
- DuckDB warehouse with all staged datasets.
- Posterior sample files (parquet) for every fitted model.
- Simulation output store: per-path results for 50,000 league simulations.
- JSON export bundle conforming to the contracts in Section 11.
- Validation report (auto-generated markdown) with every gate in Section 8 and its pass/fail status.

---

## 3. System Architecture and Data Flow

```
                        RAW DATA
  Basketball-Reference    Contract data     Lottery odds tables
  (team seasons, drafts,  (historical +     (current + historical
   player seasons,         current)          eras)
   transactions)
        |                     |                   |
        v                     v                   v
  +---------------------------------------------------------+
  |                    ETL LAYER (src/etl)                    |
  |   franchise_seasons | star_spells | draft_outcomes |      |
  |   player_impact_seasons | rosters_current | contracts     |
  +---------------------------------------------------------+
                              |
                              v  (DuckDB warehouse)
  +----------------+  +----------------+  +----------------+
  |   MODEL A      |  |   MODEL B      |  |   MODEL C      |
  |   Franchise    |  |   Star         |  |   Aging        |
  |   trajectory   |  |   retention    |  |   curves       |
  |   (all 30)     |  |   hazard       |  |                |
  +----------------+  +----------------+  +----------------+
          \                  |                  /
           \                 v                 /
            +--> +---------------------------+ <--+
                 |     ENGINE D              |
                 |  Two-tier league sim      |
                 |  2027-2033, 50k paths     |
                 |  + exact lottery draws    |
                 +---------------------------+
                              |
              per-path (MIN slot, CHA slot) by year
                              |
                 +---------------------------+
                 |   E1 slot value curves    |
                 |   E2 swap option pricing  |
                 +---------------------------+
                              |
                 +---------------------------+
                 |   F  Joan Bet adapter     |
                 |   (championship equity)   |
                 +---------------------------+
                              |
                 +---------------------------+
                 |   Viz JSON exports (D3)   |
                 |   Validation report       |
                 +---------------------------+
```

The two-tier design in Engine D is the key architectural decision: Minnesota and Charlotte get roster-level fidelity (aging curves plus star hazard feeding a roster-informed strength estimate), while the other 28 franchises evolve under the pure franchise-level statistical prior from Model A. Detail where it matters, statistics where it does not.

---

## 4. Repository Layout and Conventions

```
pick2033/
  README.md
  config/
    trade_terms.yaml          # swap years, protections, seconds (Section 5)
    model_params.yaml         # priors, blend schedule, sim count, seeds
    star_definition.yaml      # criteria for star-spell inclusion
  data/
    raw/                      # untouched pulls, versioned by date
    staged/                   # cleaned parquet
    warehouse.duckdb
  src/
    etl/
      bref_team_seasons.py
      bref_draft_outcomes.py
      bref_player_seasons.py
      star_spells_builder.py  # includes manual-review export/import step
      contracts_loader.py
      rosters_current.py
    models/
      trajectory.py           # Model A (NumPyro)
      hazard.py               # Model B (discrete-time Bayesian logit + Cox check)
      aging.py                # Model C (delta method, hierarchical)
      slot_value.py           # Model E1
    sim/
      strength_blend.py       # roster-informed vs franchise-prior blending
      league_sim.py           # Engine D season loop
      lottery.py              # exact odds tables + draw mechanics, era-aware
      swap_pricing.py         # E2
    integrate/
      joan_bet_adapter.py     # F
    viz/
      export_json.py          # Section 11 contracts
      figures.py              # static matplotlib for internal review
    validation/
      backtests.py
      historical_replays.py
      report.py               # auto-generated validation report
  tests/
    test_lottery_odds.py
    test_win_conservation.py
    test_swap_payoff.py
    test_schema_contracts.py
  notebooks/                  # exploration only, nothing load-bearing
  outputs/
    posteriors/
    sims/
    json/
    figures/
    validation_report.md
```

### Conventions

- Python 3.11+. Core stack: NumPyro (JAX) for Bayesian models, lifelines for the Cox sanity check, pandas/pyarrow/DuckDB for data, ArviZ for diagnostics, matplotlib for internal figures.
- Every stochastic entry point takes an explicit seed from `model_params.yaml`. A full run from warehouse to JSON exports must be reproducible bit-for-bit.
- Posterior fits are cached to `outputs/posteriors/` and keyed by a hash of (data version, model code version, params). The simulation engine loads cached posteriors; it never refits.
- All published numbers come from the JSON export layer, never hand-copied from notebooks.

---

## 5. Configuration: `trade_terms.yaml`

The exact swap terms are a hard input that must be confirmed against the reported trade before any pricing runs. The config ships with placeholders and the build fails loudly if placeholders remain.

```yaml
# trade_terms.yaml
outgoing_first:
  year: 2033
  protection: none            # CONFIRM: reported as unprotected
  conveys_to: CHA

swaps:                        # CONFIRM years, direction, protections
  - year: TODO
    type: favorable_to_CHA    # CHA may elect the better of the two firsts
    protection: TODO          # none | top_k | other
  - year: TODO
    type: favorable_to_CHA
    protection: TODO
  - year: TODO
    type: favorable_to_CHA
    protection: TODO

seconds:                      # CONFIRM count and years
  - year: TODO
  - year: TODO

notes: >
  Swap semantics assumed: in each swap year, Charlotte receives
  max(MIN pick position, CHA pick position) in value terms, i.e. they
  keep their own pick unless Minnesota's is better. If any swap involves
  third-team picks Charlotte controls, extend the payoff function in
  swap_pricing.py accordingly and document.
```

`model_params.yaml` carries: sim path count (default 50,000), blend schedule (Section 7.4), prior hyperparameters, seed, and the era flag for lottery odds.

---

## 6. Data Acquisition and Schemas

All tables land in DuckDB. Schemas below are contracts; `test_schema_contracts.py` enforces them.

### 6.1 `franchise_seasons` (Model A training)

One row per franchise-season, 1980 to present (46 seasons, ~1,300 rows).

| column | type | notes |
|---|---|---|
| franchise_id | text | stable ID across relocations/renames (mapping table required) |
| season | int | ending year convention (2026 = 2025-26) |
| wins, losses | int | |
| win_pct | float | |
| srs | float | simple rating system, preferred strength observable |
| conference | text | for standings/lottery eligibility |
| core_age_min_weighted | float | minutes-weighted age of top-6 minutes players |
| had_star | bool | any star-spell player on roster (from 6.2) |
| continuity_pct | float | share of minutes returning from prior season |

Source: Basketball-Reference team pages. The franchise ID mapping (Sonics to Thunder, Bullets to Wizards, and so on) is a small hand-built table checked into `config/`.

### 6.2 `star_spells` (Model B training)

Counting-process format: one row per star-player-season within a spell. Target size roughly 200 to 300 distinct spells, 1,200+ player-season rows, 1990 to present.

| column | type | notes |
|---|---|---|
| player_id | text | |
| franchise_id | text | |
| season | int | |
| spell_id | text | player-franchise spell identifier |
| age | float | |
| years_with_franchise | int | |
| contract_years_remaining | int | best-effort; see data risk below |
| supermax_eligible | bool | era-aware rules |
| team_win_pct_2yr | float | trailing two-season average |
| deep_run_recent | bool | conference finals or better in last 3 seasons |
| all_nba_count_career | int | through this season |
| market_tier | int | 1-3, hand-assigned table in config |
| event_departure | bool | left franchise before next season (trade or FA, any cause) |
| event_retire | bool | competing risk: career ends with franchise |
| censored | bool | spell ongoing at data end |

**Star definition (in `star_definition.yaml`, confirm with Bobby):** a player enters a spell in the first season with the franchise where he earns All-NBA, OR posts a top-20 league finish in BPM with 1,500+ minutes. The spell persists until departure, retirement, or censoring, even if star-level play lapses (the asset question is about the player leaving, not about form).

**Build process:** `star_spells_builder.py` generates candidate spells automatically from Basketball-Reference player-season and transaction data, then exports a review CSV. This is the one deliberate human-in-the-loop step: Bobby reviews departure events and contract-years-remaining values (~200 spells, an evening of review), re-imports, and the builder freezes the dataset with a version hash.

**Data risk:** historical contract-years-remaining is the messiest field. Fallback: approximate from signing dates and contract lengths in RealGM-style records; where unresolvable, impute with a flag column so the model can learn a missingness effect. Document coverage rate in the validation report.

### 6.3 `draft_outcomes` (Model E1 training)

One row per drafted player, draft years 1990-2019 (so every pick has 4+ observable seasons).

| column | type | notes |
|---|---|---|
| draft_year | int | |
| slot | int | 1-60 |
| player_id | text | |
| value_4yr | float | VORP summed over first 4 seasons (v1 metric) |
| value_alt | float | Win Shares first 4 seasons (robustness metric) |

### 6.4 `player_impact_seasons` (Model C training + roster strength)

Player-season BPM, minutes, age, position, 1985 to present. BPM chosen for v1 because it exists across the full history; the known limitations are documented and a metric swap to Project 1 latent vectors is a planned v2 upgrade.

### 6.5 `rosters_current`

Current Wolves and Hornets rosters with age, contract years, and latest impact metrics, pulled at build time (do not hardcode; both rosters are actively changing this week). Charlotte's core enumerates from data: Naz Reid plus their incumbent young players as of the pull date.

### 6.6 `lottery_odds`

The exact NBA lottery probability tables, era-keyed:

- `post_2019`: flattened odds (bottom three records each 14.0% for the first pick; top four picks drawn; remaining lottery teams slotted 5-14 in inverse record order).
- `pre_2019_weighted`: the older table, required for historical replay validation only.

Both tables are entered from official sources during M0 and locked behind `test_lottery_odds.py`, which asserts every row sums correctly and matches the published values.

---

## 7. Component Specifications

### 7.1 Model A: Franchise Trajectory Model

**Purpose:** the statistical prior over how any NBA franchise's strength evolves over a 7-year horizon, including the fat-tailed collapses and rebuilds that dominate distant-pick value.

**Observable:** SRS (preferred over win% because it is margin-based and less bounded), modeled per franchise-season.

**Model (v1):** hierarchical AR(1) with fat-tailed innovations.

```
theta[i, t] = mu[i] + phi * (theta[i, t-1] - mu[i]) + eta[i, t]
eta[i, t]  ~ StudentT(nu, 0, sigma)
mu[i]      ~ Normal(0, tau)          # franchise long-run mean, partial pooling
srs[i, t]  ~ Normal(theta[i, t], sigma_obs)
```

- `phi` (persistence), `nu` (tail thickness), `sigma` shared across franchises with weakly informative priors. The Student-t innovation is the v1 mechanism for regime shifts: it lets a franchise fall off a cliff or leap without needing an explicit mixture.
- **v2 option (only if backtests demand it):** explicit two-component mixture innovation (routine noise vs. structural shock with estimated shock probability), and covariate effects on the innovation mean (core age, continuity, star loss). Build v1 first; complexity must be earned by a validation gate failure.
- **Fitting:** NumPyro NUTS on the full panel (about 1,300 rows; minutes on CPU). Diagnostics gate: R-hat < 1.01, bulk ESS > 400 on all parameters.
- **Output:** posterior samples for all parameters plus the filtered current state `theta[i, 2026]` for every franchise, which is the launch point for simulation.

### 7.2 Model B: Star Retention Hazard

**Purpose:** per-season probability that a star leaves his franchise, as a function of observable covariates, so the simulation can draw departure events for Edwards (and Charlotte's stars) year by year.

**Form: discrete-time hazard.** A hierarchical Bayesian logistic regression on player-seasons within spells:

```
P(departure in season t | spell active) =
  logistic( b0 + b_age * f(age)
          + b_yrs * years_with_franchise
          + b_contract * contract_years_remaining
          + b_win * team_win_pct_2yr
          + b_deep * deep_run_recent
          + b_market * market_tier
          + b_supermax * supermax_eligible
          + u[player_era] )
```

Discrete-time is chosen over continuous-time survival deliberately: the simulation steps in seasons, covariates are season-varying, and a per-season Bernoulli hazard drops into the sim loop with zero impedance. Retirement is handled as a competing per-season event with its own (simpler, age-driven) hazard; v1 may merge departure and retirement into a single "star exits" event if the retirement submodel starves for data, with the merge documented.

- **Sanity check:** fit a Cox proportional hazards model (lifelines) on the same spells and confirm covariate sign agreement. Disagreement on any sign is a stop-and-investigate gate.
- **The endogeneity note (document prominently):** team success is a covariate in the hazard, and in simulation that covariate comes from the simulated trajectory. This creates the intended feedback loop (a collapsing team raises departure risk, and a departure collapses the team further). The causal assumption is that the historical association between team success and star exits transfers to simulated futures. This is an assumption, not a theorem; it goes in the published methodology notes.
- **Edwards application:** his covariate path (age, contract years remaining from the confirmed current contract in config, simulated team success) is evaluated per simulated season. Deliverable: annual hazard and cumulative departure probability through 2033 with credible intervals. This is the Stage 1 publication.

### 7.3 Model C: Aging Curves

**Purpose:** realistic year-over-year impact deltas for the Wolves and Hornets cores inside the simulation.

**Form: the delta method, hierarchical by archetype.** Model year-over-year change in BPM as a function of age with archetype-level curves (guards / wings / bigs in v1):

```
delta_bpm[p, t] = g_archetype(age[p, t]) + gamma[p] + eps
```

with `g` a smooth function (natural cubic spline basis, hierarchical coefficients) and `gamma[p]` a small player random effect.

**Survivor bias is the known killer** of naive aging curves: players who decline hard exit the sample, flattening the estimated curve. v1 mitigation: for any player-season with 500+ minutes followed by a season under a minutes floor, impute a decline-to-replacement delta for the missing season, with the imputation flagged so its influence can be measured. The validation report must show curves with and without the imputation; if they diverge materially past age 30, the imputed version is authoritative and the divergence is documented.

### 7.4 Roster-to-Strength Mapping and the Blend Schedule

**Purpose:** convert roster-level detail into the same strength units as Model A, and control how much the simulation trusts roster detail versus the franchise-level prior as the horizon extends.

**Mapping:** minutes-weighted roster BPM aggregates map to team SRS via a calibration regression fit on history (`sum of minutes-weighted BPM -> SRS`, expect a near-linear fit; store residual variance as roster-model noise).

**Blend:** simulated MIN and CHA strength in season t is

```
theta_team[t] = w[t] * theta_roster[t] + (1 - w[t]) * theta_prior[t]
```

with the default schedule (config-driven, sensitivity-tested in Section 9):

| season | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 |
|---|---|---|---|---|---|---|---|
| w (roster weight) | 1.00 | 0.85 | 0.65 | 0.45 | 0.30 | 0.20 | 0.10 |

Rationale: rosters are largely knowable 1-2 years out and largely unknowable 6-7 years out; the franchise prior (which already embodies how teams historically churn) should dominate the far horizon. A star departure event overrides the blend by applying the departure shock directly to `theta_roster` (removal of the player's minutes-weighted contribution plus an estimated cascade term from historical post-star-exit seasons) and simultaneously shifting the franchise prior state downward by the historically observed average star-exit effect.

### 7.5 Engine D: Two-Tier League Simulation

**Purpose:** produce the joint distribution over (MIN pick slot, CHA pick slot) for every season 2027 through 2033.

**Pseudocode per simulation path:**

```
draw one joint posterior sample from Models A, B, C, E1 (parameter uncertainty
propagates by pairing each path with one posterior draw)

initialize theta[i, 2026] for all 30 franchises from Model A filtered states
initialize MIN, CHA rosters from rosters_current

for season in 2027..2033:
    # roster evolution (MIN, CHA only)
    for each core player on MIN, CHA:
        apply aging delta from Model C
    for each star on MIN, CHA:
        draw departure ~ Bernoulli(hazard from Model B, covariates from sim state)
        if departure: apply departure shock (7.4)

    # strengths
    theta_roster computed for MIN, CHA; blended per 7.4
    theta for other 28 franchises advanced one step under Model A dynamics

    # season outcome
    map all 30 thetas to expected win totals via calibrated SRS-to-wins curve
    add season-level noise; renormalize so total league wins == 1230
    rank standings; assign conferences from static mapping
    lottery_teams = the 14 non-playoff teams (top 8 per conference make
        playoffs in v1; the play-in is approximated away, documented)
    draw lottery per official post-2019 odds: four top picks drawn,
        remainder in inverse record order
    record slot[MIN, season], slot[CHA, season]

persist per-path results: slots by year, departure events, win paths
```

- **Path count:** 50,000 (config). Runtime target: under 10 minutes single-machine; the loop is vectorizable across paths in NumPy/JAX.
- **Conservation and sanity gates** (Section 8) run on every sim batch automatically.
- **Play-in approximation:** treating the top 8 per conference as playoff teams misclassifies lottery entry for teams in the 9-10 band occasionally. For MIN and CHA pick outcomes this is second-order (it perturbs which mid-tier team holds slots 11-14), but it is stated in the methodology notes, and a v2 play-in module is a listed upgrade.

### 7.6 Model E1: Draft Slot Value Curves

**Purpose:** convert a slot number into value, with uncertainty, in two currencies.

- **Currency 1, surplus value:** fit slot -> `value_4yr` (VORP, with the WS alternative as robustness) on `draft_outcomes` using a Bayesian monotone-decreasing curve (monotonic spline or isotonic-with-smoothing; enforce monotonicity as a hard constraint since a rational front office weakly prefers a better slot). Keep the full posterior; every simulation path pairs its slot draws with one curve draw so slot-value uncertainty propagates.
- **Currency 2, championship equity:** the Joan Bet adapter (7.8) maps value_4yr distributions into title-equity contributions using the framework's existing machinery. If Joan Bet already carries a pick-value module from the acquisition-pipeline work, adapt it rather than rebuilding; reconcile any disagreement between the two mappings in the validation report.

### 7.7 E2: Swap Option Pricing

**Purpose:** the number nobody else publishes.

For each swap year Y (from `trade_terms.yaml`), per simulation path:

```
exercised[path, Y] = slot_value(MIN_slot) > slot_value(CHA_slot)
payoff[path, Y]    = max(0, slot_value(MIN_slot) - slot_value(CHA_slot))
```

Reported per swap:

- **P(exercise):** the headline probability the swap matters at all.
- **Payoff distribution:** mean, median, 80% and 95% intervals, in both currencies.
- **Scenario decomposition:** conditional payoff and probability by named world-state: (a) baseline worlds (no Edwards departure, no collapse), (b) Edwards-departs worlds, (c) Charlotte-ascends worlds, (d) joint tail (Edwards departs AND Charlotte is good). The decomposition answers "where does the cost live," which is the editorial heart of Stage 3.
- **Correlation structure:** swaps in adjacent years are heavily correlated with each other and with the 2033 pick (they share the same simulated worlds). Report the total asset cost as the per-path sum, never the sum of marginal means, and show the total's full distribution.

Second-round picks: valued at a flat small surplus figure from the E1 curve's slot 31-45 average, config-listed, with a one-line sensitivity check. They are not worth simulation complexity.

### 7.8 F: Joan Bet Integration Adapter

**Purpose:** restate everything in the house currency.

- **Interface contract:** `joan_bet_adapter.equity_from_value_draws(value_draws: array, context: dict) -> equity_draws: array`. The adapter is the only file that imports from the Joan Bet codebase, keeping the coupling in one place.
- **Location and API of the Joan Bet entry point:** open question for Bobby (Section 13); the adapter is written against the contract above and a thin shim adapts to whatever the real entry point looks like.
- **Final deliverable of F:** total outgoing asset cost (2033 first + three swaps + seconds) as a championship-equity distribution, presented alongside the clean-room team-strength verdict so the complete trade statement reads: on-court effect X, asset cost Y with interval, decomposed by scenario.

---

## 8. Validation Gates and Acceptance Criteria

Every gate is implemented in `src/validation/` and lands in the auto-generated `validation_report.md`. Stages do not publish until their gates pass. Where a gate fails, the response is investigate-and-document, not silently retune.

### 8.1 Model A Gates (Trajectory)

| Gate | Criterion |
|---|---|
| MCMC health | R-hat < 1.01, bulk ESS > 400, no divergences after warmup |
| Rolling-origin backtest | Train through season T, predict T+1..T+7, for T in 1995..2019. Score every horizon. |
| Calibration | Empirical coverage of 80% predictive intervals within [72%, 88%] at every horizon 1-7 |
| Skill | CRPS beats two baselines at horizon 7: last-season persistence, and pooled-mean reversion |
| Dispersion sanity | Simulated cross-sectional SD of team wins per season within 15% of the historical SD |

### 8.2 Model B Gates (Hazard)

| Gate | Criterion |
|---|---|
| Discrimination | C-index >= 0.63 on held-out spells (20% spell-level holdout) |
| Calibration | Calibration slope in [0.8, 1.2] on held-out player-seasons; calibration plot in report |
| Sign agreement | Cox sanity model agrees with Bayesian model on the sign of every covariate |
| Face validity | Predicted hazard for canonical known cases behaves sensibly (winning supermax-eligible stars in year 1 of a max: low; aging stars on collapsing teams in walk years: high). Documented as narrative checks, not fitted-to. |

### 8.3 Model C Gates (Aging)

| Gate | Criterion |
|---|---|
| Held-out deltas | RMSE on held-out player-season deltas beats a "no aging" baseline and a league-mean-delta baseline |
| Survivor-bias audit | Curves with vs. without dropout imputation plotted; divergence documented; imputed version authoritative past age 30 |

### 8.4 Engine D Gates (Simulation)

| Gate | Criterion |
|---|---|
| Conservation | Total league wins == 1230 in every simulated season, exact |
| Lottery correctness | Unit tests reproduce the official post-2019 odds table exactly; simulated slot frequencies for a fixed standings input match the table within Monte Carlo error |
| Autocorrelation | Simulated franchise win-path autocorrelation (lags 1-3) within the historical envelope |
| Tail realism | Simulated frequency of 60+ win and sub-20 win seasons within 25% of historical rates |

### 8.5 End-to-End Gate: Historical Replays

The credibility centerpiece. Run the entire pipeline as-of a past date on famous distant-pick trades and check whether realized outcomes fell inside the model's predictive distribution.

- **Primary replay: the 2013 Celtics-Nets trade** (distant unprotected firsts plus a 2017 swap that famously converted at the extreme tail). Run the pipeline as-of summer 2013 with era-appropriate (pre-2019 weighted) lottery odds and only data available then. Exact terms verified during build.
- **Secondary replays (verify terms during build):** the 2019 Clippers-Thunder Paul George package (swaps and distant firsts, now partially resolved), plus one negative control: a distant pick that conveyed unremarkably.
- **Acceptance:** realized pick slots fall within the 90% predictive interval in at least 2 of 3 replays, and any miss is analyzed in the report (a tail case landing outside a 90% interval is not automatically a model failure, but it must be understood). The Nets replay doubles as publishable content: "we ran our model in 2013; here is what it said about the picks that became the Jaylen Brown and Jayson Tatum selections."

---

## 9. Sensitivity Analysis

A tornado analysis on the headline outputs (2033 pick expected value, total asset cost in equity), varying one assumption at a time across its plausible range:

1. Edwards hazard scale (multiply all his simulated hazards by 0.5x and 1.5x).
2. Blend schedule (roster-trust decays one season faster / slower than default).
3. Trajectory persistence `phi` (posterior 10th vs. 90th percentile).
4. Innovation tail thickness `nu` (same treatment).
5. Slot-value metric (VORP vs. Win Shares currency).
6. Play-in handling (v1 approximation vs. a crude 9-10 seed randomization).

Deliverable: `tornado.json` plus a ranked plain-language summary of which assumptions actually move the answer. If a single assumption dominates, that finding leads the Stage 3 methodology notes rather than hiding in an appendix.

---

## 10. Milestones, Effort, and Publication Mapping

Estimates are agent working days; the one human-heavy step is flagged.

| # | Milestone | Contents | Est. | Gate to pass | Publishes |
|---|---|---|---|---|---|
| M0 | Scaffold + ETL | Repo, configs, franchise/draft/player ETL, DuckDB warehouse, lottery tables + tests | 2-3d | Schema contracts, lottery unit tests | |
| M1 | Trajectory model | Model A fit + rolling-origin backtests | 3-4d | 8.1 | |
| M2 | Star spells + hazard | Spells builder, **Bobby review of ~200 spells (one evening)**, Model B + Cox check, Edwards curves | 3-4d | 8.2 | **Stage 1: Edwards hazard piece** |
| M3 | Aging curves | Model C + survivor-bias audit | 2d | 8.3 | |
| M4 | Simulation engine | Blend, Engine D, 50k paths, sim gates | 3-4d | 8.4 | **Stage 2: 2033 pick posterior** |
| M5 | Valuation | E1 curves, E2 swap pricing, scenario decomposition | 2-3d | Swap payoff tests | |
| M6 | Integration + replays + viz | Joan Bet adapter, historical replays, sensitivity, JSON exports, validation report | 3-4d | 8.5 + full report green | **Stage 3: the priced trade** |

Total: roughly 18 to 24 agent days. M1, M2, M3 are parallelizable after M0 if running multiple agent sessions; M4 depends on all three.

**Sequencing note:** M2 is deliberately early despite the sim not needing it until M4, because Stage 1 is the fastest path to publishing while the trade conversation is still hot.

---

## 11. Visualization Export Contracts (D3 / Flutter Site)

All published charts render from these JSON files; `test_schema_contracts.py` validates them. Numbers appear on the site only via this layer.

```
outputs/json/
  edwards_hazard.json
    { "annual": [{"season": 2027, "hazard_mean": ..., "lo80": ..., "hi80": ...}, ...],
      "cumulative": [{"season": 2027, "p_departed_by_mean": ..., "lo80": ..., "hi80": ...}, ...] }

  win_fancharts.json
    { "MIN": [{"season": 2027, "q05": ..., "q20": ..., "q50": ..., "q80": ..., "q95": ...}, ...],
      "CHA": [ ... ] }

  slot_distribution_2033.json
    { "slots": [{"slot": 1, "p": ...}, ... 1..30],
      "p_top4": ..., "p_top10": ..., "p_lottery": ...,
      "conditional": {"edwards_stays": {...}, "edwards_departs": {...}} }

  swap_pricing.json
    [ {"year": ..., "p_exercise": ...,
       "payoff_vorp": {"mean": ..., "q10": ..., "q50": ..., "q90": ...},
       "payoff_equity": { ... },
       "scenarios": [{"name": "baseline", "p": ..., "conditional_payoff": ...}, ...]} ]

  total_asset_cost.json
    { "equity_distribution_quantiles": {...}, "decomposition": {...},
      "per_path_sum_note": "totals are per-path sums, not sums of means" }

  tornado.json
    [ {"assumption": ..., "low_value": ..., "high_value": ..., "delta": ...} ]
```

Every JSON carries a `meta` block: run seed, data version hashes, model code version, generation timestamp.

---

## 12. Risks, Known Approximations, and Mitigations

- **Small-N hazard data.** 200-300 spells is thin for 8 covariates. Mitigations: hierarchical shrinkage priors, the Cox sign-agreement gate, and publishing hazard intervals prominently rather than point estimates. If intervals are wide, that is the honest finding, and the Stage 1 piece says so.
- **Nonstationarity.** The second-apron CBA era may change both franchise dynamics and star movement relative to history. Mitigations: era random effect in Model B (`u[player_era]`), the sensitivity analysis, and explicit methodology-notes language. Do not claim the model sees a regime it has never observed.
- **Contract-history data quality.** Flagged in 6.2; coverage rate reported; missingness modeled rather than silently imputed.
- **Endogeneity of the success-hazard loop.** Documented in 7.2; this is a modeling assumption stated in public methodology, not buried.
- **BPM as the v1 impact currency.** Known blind spots (defense especially). Mitigations: WS robustness track in E1, and the planned v2 swap to Project 1 latent skill vectors, which upgrades 7.3, 7.4, and E1 simultaneously.
- **Play-in approximation.** Second-order for this question; documented; v2 listed.
- **Swap-terms uncertainty.** The build hard-fails on placeholder terms. No pricing runs on unconfirmed terms, period.
- **Framing risk on Stage 1.** The Edwards piece must be framed as a league-wide model of star tenure applied to his covariates, with intervals, and never as a claim about his intentions. Editorial review before publication is a release gate, same as the technical ones.

---

## 13. Open Questions to Confirm Before Build (Blocking Items Marked)

1. **[BLOCKING for M5]** Exact swap years, direction, and protections; count and years of the seconds. Fills `trade_terms.yaml`.
2. **[BLOCKING for M2]** Edwards' current contract structure (years remaining, option years) as of today, entered into config from a current source.
3. Star definition thresholds in `star_definition.yaml`: All-NBA OR top-20 BPM with a 1,500-minute floor is the proposal; adjust if desired.
4. Joan Bet entry point: file/function the adapter should call, and whether a pick-value module already exists there from the acquisition-pipeline work.
5. Blend schedule defaults (7.4): accept the proposed w(t) or set your own before sensitivity runs.
6. Publication naming and whether Stage 1 runs as a standalone piece or as part one of a labeled series.
7. Whether the Hornets side should also get a published hazard/trajectory writeup (the model produces it for free; publishing it is an editorial choice).

---

## Appendix A: Definition of Done

The project is done when: all gates in Section 8 are green in `validation_report.md`; a single command reproduces the full pipeline from warehouse to JSON exports with the configured seed; the three publication stages have shipped with their charts rendered from the export contracts; and the total asset cost of the LaMelo trade exists as a distribution, in championship-equity units, with a scenario decomposition that a reader can interrogate.

## Appendix B: Suggested First Agent Session

Session 1 scope: M0 in full. Stand up the repo per Section 4, implement the franchise ID mapping and the three core ETL scripts (`bref_team_seasons`, `bref_draft_outcomes`, `bref_player_seasons`), load the warehouse, enter both lottery odds tables, and get `test_lottery_odds.py` plus `test_schema_contracts.py` green. End the session by generating the candidate star-spells review CSV so Bobby's review (the M2 human step) can happen offline before session 2.

*End of spec.*
