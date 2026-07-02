# pick2033 — The 2033 Pick Posterior and Swap Option Pricing

Prices the draft assets Minnesota sent Charlotte in the LaMelo Ball trade
(2033 unprotected first, 2028/2029/2030 first swaps, 2029/2032/2033 seconds)
as full posterior distributions in draft-slot, surplus-value (4-yr VORP), and
championship-equity terms.

- **Spec (design authority):** `../2033-posterior/wtat-project4-2033-pick-implementation-spec.md`
- **Execution plan (overrides spec where they conflict):** approved 2026-07-01;
  encodes the MIN pick-encumbrance stack, the 2026 lottery reform, and the
  Joan Bet adapter design.
- **Publishes as:** "Pricing the LaMelo Trade", Parts 1-3 on Wolves to a T
  (Stage 1 Edwards retention hazard, Stage 2 2033 pick posterior, Stage 3 the priced trade).

## Layout
Per spec Section 4, plus: `src/etl/bref_client.py` (shared B-Ref fetch/cache/throttle),
`src/sim/pick_ledger.py` (MIN obligation stack + ordered swap resolution),
`config/franchise_map.csv`, `src/integrate/build_equity_curve.py`, `src/models/smoke_test.py`.

## Environment
Per-project venv (`.venv`), Python 3.11+. Install: `python -m venv .venv &&
.venv/Scripts/pip install -r requirements.txt`. The PPL stack (NumPyro/JAX CPU,
PyMC+nutpie fallback) is locked by `src/models/smoke_test.py` at M0.

## Reproducibility contract
Every stochastic entry point takes its seed from `config/model_params.yaml`.
Posterior fits cache to `outputs/posteriors/` keyed by (data version, code version,
params) hash; the sim engine loads cached posteriors and never refits. All published
numbers come from `outputs/json/` exports, never hand-copied. Raw B-Ref HTML is
cached permanently under `data/raw/bref/` — re-parses never re-fetch.

## Hard gates
`swap_pricing.py` refuses to run while `trade_terms.yaml: verified_post_july6` is
false. Validation gates (spec Section 8) land in `outputs/validation_report.md`;
stages do not publish until their gates are green.
