# July 6 Runbook — the five buttons, in order

Everything below is staged, gated, and tested. Your part is three human
items (marked BOBBY); the rest is commands. If anything goes red, the house
rule applies: decision memo, park it, keep going on what doesn't depend on
it. No threshold moves, no silent choices.

All commands run from `pick2033/` using the project venv:
`.venv/Scripts/python`.

---

## July 5 (day before, optional but nice)

- [ ] `git status` clean; `.venv/Scripts/python -m pytest tests/ -q` green
      (53 tests, ~3 min).
- [ ] Skim the two staged drafts once WITHOUT numbers so the July 6 read is
      fresh: `docs/drafts/stage1_edwards_hazard_draft_v2.md`,
      `docs/drafts/stage2_pick_posterior_draft_v3.md`.
- [ ] Nothing else. The machine is supposed to be dormant today.

---

## Step 0 — BOBBY: the LaMelo news check (before anything runs)

He became extension-eligible today (2yr/$119.2M). Check the news, then
hand the agent ONE word:

- **unsigned** -> his current deal stands (walk year 2029, same as Edwards)
- **extended** -> new deal through 2031
- **unresolved** -> no reliable report either way; BOTH scenarios run
  (pre-declared sensitivity; never pick silently)

If unsigned or extended, also set it in `config/model_params.yaml`
(`simulation.lamelo_contract`). If unresolved, leave the config alone; the
both-ways flags in Step 4 handle it.

## Step 1 — Verify the trade terms (unlocks everything)

- [ ] Confirm the reported swap/pick terms against `config/trade_terms.yaml`
      (2033 first unprotected; swaps 2028/2029/2030 favorable to CHA;
      seconds 2029/2032/2033). Special attention to the 2029 language
      (CHA swap live only in MIN-top-5 worlds; the TBD branch: can CHA
      swap using the least-favorable UTA/CLE pick they control? v1 priced
      CHA-own; update the config note if reporting settles it).
- [ ] A fresh Spotrac pull helps cross-check:
      `.venv/Scripts/python src/etl/pull_spotrac_ledger.py`
      then eyeball the MIN/CHA first-round rows for the new swap text.
- [ ] Set `verified_post_july6: true` in `config/trade_terms.yaml`.
      Every priced path is hard-gated on this flag.

## Step 2 — Final spells freeze (one command)

```
.venv/Scripts/python src/etl/apply_review.py --final
```

Applies your 21 borderline calls + the three exit updates
(Giannis/Kawhi/LaMelo -> departure) and writes
`data/staged/star_spells_final.parquet`. It prints two disclosures;
expected values, precomputed:
- three-exits vs sealed holdout: **none** are members
- borderline prunes vs holdout: **3 of 13** are members; re-gate sample
  60 -> 57 spells, **46 -> 43 departure events**

## Step 3 — The one-shot M2 refit (one command, one look, final)

```
.venv/Scripts/python -m src.models.hazard --m2
```

Fits the pre-declared spec (contract covariates + Normal(0, 0.5) priors)
and re-gates ALL of 8.2 on the same sealed holdout. Per Ruling A this is
the second and FINAL look: pass, or the calibration cell stays red with
its bootstrap CI printed. Either outcome goes in the report; no third fit.
Output: `outputs/validation/model_b_hazard_M2_FINAL.md`.

**Grade P1 here** (docs/predictions.md): the final 2033 posterior should
come out lighter-tailed than provisional. The grade itself lands after
Step 4's slot distribution exists.

## Step 4 — Final Engine D run + automatic checks

Resolved LaMelo (one run):
```
.venv/Scripts/python src/sim/run_engine_d.py 50000 --tag=FINAL
```
Unresolved (both runs, both must clear):
```
.venv/Scripts/python src/sim/run_engine_d.py 50000 --tag=FINAL_UNSIGNED --lamelo=unsigned
.venv/Scripts/python src/sim/run_engine_d.py 50000 --tag=FINAL_EXTENDED --lamelo=extended
```
(~4 min each.) The runner prints the 8.4 gates under the ratified
operationalization. The transient cell is expected red for two_tier
(accepted FINAL per Ruling C; mechanism attached in the memo).

Then the AUTOMATIC p70 re-check (binds to whatever just shipped):
```
.venv/Scripts/python src/validation/young_core_cohort.py
```
If the final CHA crest exceeds 52.8 (matched cohort p70 peak), the
cohort-calibrated adjustment fires exactly as pre-committed, then Engine D
re-runs once. If not (expected), the crest stands and it says so.

Then refresh exports and the report:
```
.venv/Scripts/python src/viz/export_json.py
.venv/Scripts/python src/validation/report.py
```
Exports auto-prefer FINAL artifacts. **Grade P1 now**: compare the final
P(top4)/P(top10) against provisional (.170/.421); write the grade into
docs/predictions.md either way.

## Step 5 — Pricing unlocks + Stage 1 ships

- [ ] Priced E2 runs are now legal (`swap_pricing.price_all` passes the
      gate). The agent runs the priced pass + fills every slot in Part 1
      from the final exports (dataset stats from the freeze meta, hazard
      curve + cumulative + scenario split from `edwards_hazard` final,
      walk-year multiple from the M2 fit, calibration clause per the
      re-gate outcome, force-ranking verify-slots from the standardized
      coefficients).
- [ ] **BOBBY: the numbers-in-place read of Part 1** — the release gate.
      Read the whole filled draft once; slow down on the
      cumulative-probability sentence and the P1 grade (the screenshot
      lines). Second pair of eyes available if you bring the filled draft
      to your verification chat.
- [ ] Publish Part 1 on the news peg.
- [ ] **BOBBY (whenever): the carousel word.** Yes -> the Part 1 companion
      gets built from the final hazard chart. Still pending on the record.

## Afterward (not July 6)

- Part 2 fills and ships ~July 8-9 after your read.
- Part 3: replays (post-final-spells, runner built), 15-arm tornado
  (pre-declared, `src/validation/tornado.py`), equity adapter final pass,
  `total_asset_cost.json`, mid-July.
- Stage 2 notes step-6 additions are pre-staged in
  `docs/stage2_methodology_notes.md`.

## If something breaks

- A gate goes red that wasn't expected red -> memo like the 8.1/8.2 ones,
  park, continue independent steps. Templates: `outputs/validation/
  model_a_gate_decision.md`, `model_b_calibration_decision.md`.
- Terms don't match the config -> STOP at Step 1; `verified_post_july6`
  stays false; nothing priced runs until the yaml matches reporting.
- Spotrac still shows pre-trade state -> fine for the cross-check;
  reporting is the source for Step 1, the ledger just corroborates.
