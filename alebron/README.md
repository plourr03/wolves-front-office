# alebron, the LeBron-to-Wolves evaluation

A clean clone of the `lamelo/` championship-equity evaluation, applied to a new question:
**LeBron James is a confirmed 2026 unrestricted free agent, what if he signs with the Wolves,
now that the LaMelo trade is done?** Same calibrated engine, same identifiability discipline,
same "decline the number if a gate fails" rule.

## Start here

- **`DELIVERABLE.md`**, the locked evaluation (sections 1-10 + forward predictions). Read this.
- **`SUMMARY_FOR_BOBBY.md`**, the plain-language version.
- **`prereg/preregistration.md`**, the immutable prediction log reality grades in 2026-27.

## Headline

The LaMelo trade hard-capped MIN at the second apron, so LeBron fits **only at the veteran
minimum, and only as a minimum-for-minimum swap** (the taxpayer MLE is illegal). On the floor,
adding him is a **near-free, positive-leaning, asymmetric bet**, the title delta stays positive
across the entire fit fork (+0.3 to +3.8pp), the downside is truncated at ~zero (benchable, cost
nothing), and the only real risk is a 41-turning-42 body's availability. The mirror image of
LaMelo (wash-to-negative at a mountain-of-assets cost). A precise title % is declined (the
engine's star-acquisition retrodiction gate fails + the availability tail is unmodeled).

## What was REBUILT for LeBron (fresh this project)

| File | What it does |
|---|---|
| `data/field_2026_offseason.json` | Every verified 2026 offseason move + LeBron FA status + 2026-27 cap figures, with sources (9-agent research workflow). |
| `data/signing_definition.json` | The LeBron signing framed (free agent, zero assets, three-question structure). |
| `data_pull/min_cap_state.py` → `data/cap_state.json` | Q0 hard-cap feasibility: LeBron fits only as a minimum swap. |
| `impact/build_transport.py` → `data/impact/transport.json` | Age-and-role retention on NET (0.80, [0.55,1.00]); why survival-on-offense is rejected for LeBron. |
| `impact/build_team_strength.py` → `data/impact/team_strength.json` | Baseline = post-LaMelo roster; treatment = +LeBron. Marginal delta both forks. |
| `impact/sweep_lebron_availability.py` | The load-bearing age × availability fork (analogue of the LaMelo Gueye fork). |
| `sim/run_sim.py` → `data/sim/sim_results.json` | CRN-paired title/round odds, both forks, both field variants (calibrated + 2026-updated sensitivity). |
| `sim/run_scenarios.py` → `data/sim/scenario_table.json` | Three-initiator fit-clicks/neutral/fit-fails. |
| `sim/season_distribution.py` → `data/sim/season_hist.json` | +LeBron per-season outcome distribution. |
| `DELIVERABLE.md`, `SUMMARY_FOR_BOBBY.md`, `prereg/preregistration.md` | The writeups. |

## What is INHERITED from lamelo (methodology / engine, not re-skinned)

These are the pre-registered methodology and calibration, authored for the LaMelo project and
reused verbatim, the whole point of the clone is that the engine and gates do not change:

- `docs/lamelo-eval-project-spec.md`, the shared project spec (the analytical-rigor law).
- `sim/run_gates.py`, `sim/run_case3.py`, engine-level retrodiction gates (Case 3 FAILS → number
 gated, identical result to LaMelo).
- `impact/build_impact.py`, `data/impact/player_impact.csv`, the clean-room impact spine (contains
 LeBron, id 2544; unchanged frozen snapshot `snapshot_2026-06-25/`).
- `impact/00-02_*.md`, `sim/02-03_*.md`, `prereg/00_prior_pushback.md`, `prereg/freeze_manifest.md`, 
 inherited framework notes; the LeBron-specific findings live in `DELIVERABLE.md`, which supersedes
 any LaMelo-flavored narrative in these.
- `fit_decomp/`, `gobert_roll/`, `shot_share/`, `article/viz/`, `slide/`, LaMelo-era supporting
 analyses and presentation artifacts, NOT yet re-skinned for LeBron. Do not read these as LeBron
 findings.

## Reproduce

```
python alebron/data_pull/min_cap_state.py # cap feasibility
python alebron/impact/build_transport.py # LeBron transport
python alebron/impact/build_team_strength.py # marginal team-strength delta
python alebron/impact/sweep_lebron_availability.py
python alebron/sim/run_sim.py # CRN-paired title odds (both fields)
python alebron/sim/run_scenarios.py # three-alpha fit table
python alebron/sim/season_distribution.py
python alebron/sim/run_gates.py # engine gates (Case 3 fails -> gated)
```
