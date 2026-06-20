# core_max — Core Maximization ("The Joan Bet")

A standalone championship-equity project. Source of truth: the spec at
`offseason/docs/wolves-core-maximization-spec.md`. Project brief:
`core_max/docs/kickoff_brief.md`.

> Spirit: we are hunting for the team nobody believed in, the one so well-fit it
> raises everyone's floor and shocks the league. That is the right tail of the
> model, and the whole engine exists to find it and price it honestly. The
> guardrails make the upside credible, never suppress it.

## Status

Phase 0 complete: data inventory + deterministic CBA-feasibility gate, validated.
Later phases (impact baseline, young-player distributions, Monte Carlo title
engine, scenario harness, reporting) are not built yet.

## Layout

```
core_max/
  cba/
    engine_bridge.py   single coupling point to the verified offseason CBA engine
    gate.py            typed, config-driven gate(plan, config) -> GateResult
  config/
    gate_config.json   season, binding lines, required-retained (Ayo), roster floor, seed
    scenarios/         status_quo.json, fork_b.json, splash.json (config, not hardcoded)
  data_inventory/
    manifest.md        versioned input inventory + cap reconciliations + Phase 0 findings
  docs/
    kickoff_brief.md   locked + resolved decisions, working norms
  tests/
    test_cba_gate.py   15/15: scenarios, one FAIL per predicate, KAT regression, engine cases
  run_gate.py          CLI
```

## Run

```
python core_max/run_gate.py                 # all scenarios
python core_max/run_gate.py --scenario fork_b
python core_max/tests/test_cba_gate.py      # Phase 0 validation
```

## Design decisions

- **Hybrid CBA gate.** The deterministic CBA math (matching brackets, apron hard
  caps, aggregation rules, the multi-leg hard-cap latch, TPE consumption) is
  reused unchanged from the verified offseason engine
  (`offseason/scripts/{evaluate_move,chain_engine}.py`). All coupling lives in
  `cba/engine_bridge.py`; the rest of core_max depends on a clean typed surface.
- **Config-driven and reproducible.** Scenarios are JSON in `config/scenarios/`.
  Binding cap lines are read live from the versioned engine constants and
  asserted against the config so they cannot silently drift. Seed pinned.
- **The gate is a classifier, not a build step.** It returns PASS/FAIL and never
  errors on a FAIL. No plan that FAILS is handed to the title-equity engine.
