# CLAUDE.md

This file gives Claude context about the project so any session in Claude Code, Claude Desktop, or Claude.ai has the working context locked in.

## Project overview

**Name:** Timberwolves 2025-26 Postmortem and Roster Construction Analysis

**Owner:** Bobby (data scientist at MaxPreps, lifelong Wolves fan)

**Purpose:** Produce a rigorous, data-driven analysis of why the 2025-26 Minnesota Timberwolves underperformed expectations in the playoffs, and identify the specific archetypes of player acquisition, roster construction, and tactical adjustments most likely to meaningfully improve their championship odds. Intended audience is the Timberwolves front office. Personal motivation is a lifelong fan wanting his team to win a championship.

**Status:** Specification phase complete. Data engineering and execution phase next.

## Required reading at session start

Always start by reading these in order:

1. **`specs/00_master_project_plan_v3.md`** - the **active** master plan as of 2026-05-17. Reflects the post-LAFI replan: revised build sequence, Q7 promoted, Q3 narrowed, Q8 added, Action Classifier extracted as standalone spec, LAFI v2 deferred with re-trigger condition. Prior versions (`00_master_project_plan.md` v1 and `00_master_project_plan_v2.md`) are preserved as historical artifacts; do not use them for current state.
2. The spec(s) most relevant to whatever the current session is about
3. `outputs/findings/q0a_lafi/11_wolves_lafi_deliverable.md` and `12_post_lafi_replan_proposal.md` if working on anything downstream of LAFI
4. The `nba-data-scientist` skill (if available in the environment) for the analytical role

The master plan v3 is the single source of truth for project state. If it disagrees with anything elsewhere, v3 wins.

## Project principles (non-negotiable)

These are documented in detail in the master plan but bear repeating because they govern every decision.

**Let the data lead.** No pre-baked conclusions. If the analysis says trade Gobert, say so. If it says he is fine, say that. The same applies to every player including Anthony Edwards (though we are not seriously considering trading him absent a request).

**Archetypes before names.** When prescribing roster moves, define the archetype with concrete production thresholds first. Names go in appendices. This is how real front offices think.

**Rigor over hot takes.** Every claim needs to hold up across appropriate samples with appropriate uncertainty. Confidence intervals are not optional. Single-game eye-test conclusions get explicitly flagged as such.

**Honest uncertainty.** Where samples are small, say so. Where confidence intervals are wide, say so. Do not oversell findings. Do not undersell them either.

**Be willing to land anywhere.** Each analysis must be willing to produce a "the conventional wisdom is correct" finding as readily as a "the conventional wisdom is wrong" finding. Pre-committing to a conclusion is the fastest way to lose credibility.

## Analysis inventory

The project consists of eleven specifications, all in `specs/`. They build on each other in a specific dependency order documented in the master plan.

**Meta-layer analyses (frame the project):**
- Q0A: LA Fitness Index (LAFI) - the marquee piece, quantifies pickup-style offense and validates it as a playoff predictor
- Q0B: Trajectory and Windows - player age curves and contention window analysis
- Q0C: Historical Cohort Analysis - what happens to teams that look like the 2025-26 Wolves
- Q0D: Coaching System Analysis - has Finch's system gone stale or is it personnel-constrained

**Tactical analyses (the core diagnostic and prescriptive work):**
- Q1: Diagnose the Break - four factors baseline, what specifically broke
- Q2: Localize the Damage - lineup matrices, on/off, who is responsible
- Q3: Mechanism Analysis - PnR coverage decoder, the highest-leverage original work
- Q4: Archetype Stress Test - opponent clustering, structural vs circumstantial
- Q5: Prescription - the payoff, archetype gaps and acquisition paths

**Special analysis:**
- Q6: KAT Retroactive and Counterfactual - evaluate the KAT-Randle trade and project what the Wolves would look like today with KAT

## Build sequence

Documented in detail in the master plan. The short version:

1. Spec phase: complete
2. Data engineering phase: in planning. The action classifier from Q3 is the rate-limiting infrastructure piece
3. Execution phase, in order: Q1 → LAFI v1 → Q2 → Q3 → Q6 → Q0C → Q4 → Q0B/Q0D → LAFI v2 → Q5
4. Integration and deliverable

## Database connection

**Production warehouse, the only Postgres instance with project data:**

- Host: `100.69.186.94` (the server's Tailscale IP, `bobbys-server`). Works from any network. On the home LAN, `192.168.1.236` also works and gives a lower-latency direct path.
- Port: `5432`
- Database: `nba_warehouse`
- User: `bobby`
- Schema: `nba`
- Password: in `wolves-front-office/.env` (gitignored). Copy `.env.example` to `.env` and fill in.

**The warehouse is reachable over Tailscale.** Any machine running analysis code must have Tailscale installed and be logged into the tailnet (`plourr03@`); without it the host is unreachable. New-machine setup: install and join Tailscale, clone this repo, `cp .env.example .env`, fill in the password. Do not rely on a User-scope `POSTGRES_HOST` env var; it is machine-local and does not travel. `.env` is the portable source of connection config.

**Never connect to `localhost:4101` (database `postgres`).** That was the original local dev instance; it is decommissioned, stale, and no longer in use. Any code or doc that points there is a bug. Analysis scripts must load `POSTGRES_*` env vars from `.env` via `python-dotenv` and fail loudly if the file is missing or the password is the placeholder. No silent fallbacks to localhost, ever.

Refer to `../nba-warehouse/docs/database_inventory.md` for the live table inventory and current 2025-26 coverage. Update that doc after material refreshes.

## Data available

Bobby has, in the production warehouse today:

- Play-by-play data archive 1997 to 2026 (2025-26 caught up post run 31, three specific playoff games still missing PBP and listed in the inventory)
- Player stats and team stats per game (`nba_player_stats`, `nba_games`); regular season complete for 2025-26 and playoffs in progress
- Advanced stats per player and per team per game (`nba_player_advanced_stats`, `nba_team_advanced_stats`); regular season complete for 2025-26, **playoffs not yet backfilled (highest-priority data gap)**
- Tracking data, per game and per season (`nba_player_tracking_game`, `nba_team_tracking_game`, `nba_player_tracking_season`, `nba_team_tracking_season`). Per-game tracking covers the recent ~2-3 seasons. Per-season tracking covers more.
- Synergy play type frequencies and efficiency (`nba_synergy_player_play_types`, `nba_synergy_team_play_types`) for RS+PO 2024-25 and 2025-26, plus RS 2023-24. This is a real asset for Q3; the old plan said Synergy was unavailable and that was wrong.
- Shot chart detail (`nba_shot_chart_detail`) for 2025-26: per-shot coordinates, zone, made/missed. Older seasons not yet pulled.
- Hustle, defensive-impact, point-shot, shot-location season aggregates for the recent seasons.
- Matchup-level box scores (`nba_boxscore_matchups`): Wolves-only for 2025-26. League-wide backfill is a candidate ingest if cross-team comparisons are required.
- 2025-26 roster snapshots (`nba_team_rosters`). Historical rosters not yet present.

Bobby can pull on demand:

- Cap and contract data from Spotrac
- Historical data from Basketball Reference (rosters, results, comp populations)

Bobby does not have:

- Second Spectrum proprietary tracking
- Cleaning the Glass subscription (could acquire if needed)

The master plan section 6.1 used to say tracking was not wired in and Synergy was unavailable. Both are present today. Build sequence decisions should be re-evaluated against this.

## Coding standards for this project

Beyond the general standards in the `nba-data-scientist` skill, this project specifically should follow these patterns:

**Reproducibility.** Every analysis re-runnable from raw data with one command. Random seeds set. Data sources documented. Pipeline steps explicit.

**Caching.** PBP data and tracking data pulls are expensive. Cache aggressively. Use parquet for tabular data. Version snapshots with date pulled.

**Possession-level data.** Many analyses operate at the possession level. Build the possession-level dataset once and reuse.

**Lineup integrity validation.** When building lineup data from PBP, validate that 5 players per team are on the floor at all times. Substitution errors in raw PBP do happen.

**Garbage time filtering.** Default to filtering: score margin within 15 points, not in the last 3 minutes of a blowout. Document the filter. Show both filtered and unfiltered results when it might matter.

**Bootstrapping for uncertainty.** Every team or player metric reported with a CI. Bootstrap is the default. 1000+ resamples.

**Era adjustment.** Z-score within season when comparing across eras. The 2015 NBA plays a different game than the 2025 NBA.

## Workflow conventions

**When starting a new analysis:** Read the relevant spec end-to-end first. Then check the master plan for dependencies. Then plan the work as a sequence of sub-tasks before writing any code.

**When pulling new data:** Document the source, date pulled, and any filtering applied. Save raw and processed versions separately.

**When implementing a model:** Build v1 first using the simplest defensible methodology. Validate on a known sample. Then iterate.

**When writing up findings:** Use the structure documented in the relevant spec. Lead with the answer. Show work in the next layer. Methodology in appendix.

**When uncertain:** Flag it. Ask Bobby. Better to clarify than to assume.

**Findings folder convention.** Every analysis maintains a chronological findings log at `outputs/findings/<analysis_id>/`. This is not the deliverable; it is the reasoning trail. After every meaningful step (component build, validation run, hypothesis test, major user analysis), write a dated markdown into that folder. Use numbered prefixes for chronological order (00_starting_priors.md, 01_*.md, 02_*.md, ...) so the analytical story reads top-to-bottom. The folder also holds living synthesis documents (e.g., `cross_component_pattern_matrix.md`) that get updated as new components land.

The findings folder serves three purposes:

1. **Pre-commitment of priors.** Every prediction stated before the data is logged. We grade ourselves later. The calibration scorecard accumulates across components and across analyses.
2. **Honest "let the data lead" trail.** When an eye-test fails and the prior turns out to be wrong (e.g., stale roster, outdated mental model), document it. The corrections build credibility.
3. **Durable reasoning across sessions.** Three months later, anyone (including future Claude) can reconstruct why a conclusion was reached, what was tried, what failed, and what the final synthesis was. Without this, the final memo is just assertions.

The eye-test markdowns under `outputs/tables/<analysis_id>/components/` are the technical record (data, priors, leaderboards, investigation notes). The findings folder is the analytical narrative (what changed in our understanding and why). The two complement each other. Both belong to the project.

When the user sends an analytical message that updates the working synthesis (e.g., new hypotheses, updated predictions, structural insights), capture it in the findings folder verbatim or near-verbatim under a `NNb_user_analysis_*.md` filename. Don't paraphrase user analysis away; preserve it. Their reasoning is part of the project's evidence base.

## Things to avoid

- Drawing conclusions from a single playoff game
- Comparing playoff and regular season metrics without opponent adjustment
- Using raw on/off without acknowledging lineup confounds
- Reporting point estimates without CIs
- Recommending specific players in the body of analyses (names go in appendices)
- Overconfident causal claims; most basketball findings are associational
- Hiding limitations in confident prose

## Personal notes

Bobby dislikes em dashes and en dashes in any writing. Use periods, commas, parentheses, or restructure the sentence instead.

Bobby has watched the Wolves since 2004 (Garnett era). He has more historical context on the franchise than most analysts. This sometimes informs hypotheses that the data needs to validate.

Bobby's brother-in-law Scott is also a serious Wolves observer whose intuitions have been useful checkpoint data. The "LA Fitness Index" coining came from his characterization of the offensive design.

The KAT-for-Randle trade is the most politically sensitive piece of the project. Treat the analysis honestly but write the findings carefully. The trade was made for real reasons and reasonable people can read the evidence differently.

## Where things live

This project is split into two repositories:

- **wolves-front-office** (this repo): analytical work. Specs, analysis code, notebooks, outputs.
- **nba-warehouse** (sibling repo at `../nba-warehouse`): data ingestion pipeline. The daily refresh that fills the Postgres warehouse, the Akamai bypass, schema definitions, and `database_inventory.md`. Runs on the home server via cron. Analysis code in this repo reads the data via psycopg2 connection; it does not import any code from `nba-warehouse`.

```
wolves-front-office/  (this repo)
├── CLAUDE.md (this file)
├── README.md
├── specs/
│   ├── 00_master_project_plan.md
│   ├── q0a_la_fitness_index_spec.md
│   ├── q0b_trajectory_windows_spec.md
│   ├── q0c_historical_cohort_spec.md
│   ├── q0d_coaching_system_spec.md
│   ├── q1_diagnose_the_break_spec.md
│   ├── q2_localize_the_damage_spec.md
│   ├── q3_mechanism_analysis_spec.md
│   ├── q4_archetype_stress_test_spec.md
│   ├── q5_prescription_spec.md
│   └── q6_kat_retroactive_counterfactual_spec.md
├── analyses/ (one module per Q0A, Q1, etc.)
├── notebooks/ (exploratory work, not final analyses)
└── outputs/
    ├── charts/
    ├── tables/
    └── reports/

../nba-warehouse/  (sibling repo)
├── pipeline/
│   ├── daily_refresh_complete.py
│   ├── nba_session.py            (Akamai bypass)
│   ├── cdn_collector.py          (cdn.nba.com fallback)
│   └── br_fallback.py            (Basketball Reference sanity check)
├── specs/
│   └── data_pipeline_spec.md     (architecture, schemas, troubleshooting)
└── docs/
    └── database_inventory.md     (current table contents)
```

The Postgres warehouse itself lives on the home server (`192.168.1.236:5432`, database `nba_warehouse`, schema `nba`). Analysis code reads from there via the same `POSTGRES_*` env vars the pipeline uses.

## Open questions to revisit

These were left unresolved across the specs and need decisions when execution starts:

1. Specific SRS threshold for the Q0C base cohort
2. Final weights on the five LAFI components (priors set, empirical tuning during validation)
3. The translation weight for the Q6 KAT counterfactual
4. Whether to use SRS or net rating as the playoff prediction baseline
5. How to handle the 2019-20 and 2020-21 bubble seasons in cohort work
6. Whether the action classifier needs to be its own spec (probably yes)
7. Whether DiVincenzo's Achilles is treated as "trade downside" or "bad luck" in Q6
