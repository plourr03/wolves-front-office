# Session F0 — scaffold, audit, freezes (2026-07-02)

## DoD status: everything green except the R2 human checkpoint (open by design)
- venv: torch 2.12.1+cpu, lightgbm 4.6.0, jax 0.10.2/numpyro, duckdb 1.5.4
  all smoke-passed; requirements.lock frozen.
- AM-1 adapter live: pin verification at import, refusal path tested; 10
  golden-fixture games reproduce exactly across both PBP formats.
- R1 coverage audit run: see decisions.md — the 30.6k figure was the full
  1997-2026 table; the true window universe is 16,836 (15,669 train-eligible
  002 games), pollution filtered by tested include-list, 2013-14 gap was a
  query artifact, BACKFILL CANCELLED (AM-2 budget: zero spent).
- Freeze drafts written: backtest_protocol.yaml (Bobby's 1,000-poss
  amendment verbatim), redundancy_def.yaml (25th-pctile replacement),
  model_params.yaml. predictions.md P-F1..P-F3 timestamped.
- Tests: 13/13 (pin verify + refuse, 10 goldens, include-list census
  assertions incl. per-season completeness).

## Open at session end (by design)
R2 checkpoint: backtest_protocol.yaml + redundancy_def.yaml + decisions.md
presented for Bobby's read-and-ratify. F1 (stint hardening) touches nothing
downstream until ratified; auto mode resumes after.

## F1 preview (post-ratification)
Fork lineups/lineup_aggregation into src/stints/ at the pinned hash;
reconciliation harness (AM-3 denominator, AM-4 format strata) as the first
artifact; repair loop on dev seasons per the plan's fix order; full
13-season per-game parquet build in background.
