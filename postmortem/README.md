# wolves-front-office

Data-driven analysis of why the 2025-26 Minnesota Timberwolves underperformed in the playoffs, and what roster construction and tactical adjustments would meaningfully improve their championship odds.

Intended audience: the Timberwolves front office. Project owner: Bobby.

## Project status

Specification phase complete. Data engineering phase complete (handled by the `nba-warehouse` repo). Execution phase next.

The 11 analyses are scoped in `specs/`. Start with `specs/00_master_project_plan.md` for the dependency graph and build sequence, then read whichever spec is relevant to the current session.

## Repository structure

```
specs/                 The analyses, scoped and ready to build
  00_master_project_plan.md     dependency graph, build sequence, principles
  q0a_la_fitness_index_spec.md  LAFI: pickup-style offense and playoff predictor
  q0b_trajectory_windows_spec.md
  q0c_historical_cohort_spec.md
  q0d_coaching_system_spec.md
  q1_diagnose_the_break_spec.md
  q2_localize_the_damage_spec.md
  q3_mechanism_analysis_spec.md
  q4_archetype_stress_test_spec.md
  q5_prescription_spec.md
  q6_kat_retroactive_counterfactual_spec.md
analyses/              Per-question analysis code (one module per spec)
notebooks/             Exploratory work, not final analyses
outputs/               Charts, tables, reports
CLAUDE.md              Project context for Claude sessions
```

## Data access

The data this project depends on lives in a Postgres warehouse maintained by the separate [`nba-warehouse`](../nba-warehouse) repo. That repo handles ingestion, the daily refresh, and the Akamai bypass that keeps `stats.nba.com` reachable.

To read the data from analysis code here, set the same `POSTGRES_*` environment variables and connect with psycopg2. The schemas are documented in `../nba-warehouse/specs/data_pipeline_spec.md` and the current contents in `../nba-warehouse/docs/database_inventory.md`.

## Principles

These govern every analysis. Documented in detail in `specs/00_master_project_plan.md`.

- Let the data lead. No pre-baked conclusions.
- Archetypes before names. Production thresholds first, names in appendices.
- Rigor over hot takes. Confidence intervals are not optional.
- Honest uncertainty. Where samples are small, say so.
- Be willing to land anywhere. The conventional wisdom may or may not be right.

## Workflow conventions

When starting work on an analysis:

1. Read its spec end-to-end first.
2. Check the master plan for dependencies.
3. Plan the work as a sequence of sub-tasks before writing any code.

See `CLAUDE.md` for the full set of conventions.
