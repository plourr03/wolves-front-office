# Session log — the July-6 runbook, executed 2026-07-12 (trade finalized 7/10)

## Step 0 — LaMelo extension status: UNSIGNED (news check delegated to agent)
No extension reported anywhere as of 2026-07-11 (HoopsRumors timeline;
Hornets exec Peterson 7/11 describing the 3-years-remaining deal;
SalarySwish contract page). Basis documented in model_params.yaml.
Single FINAL run; the both-ways sensitivity was not needed.

## Step 1 — Terms verified, gate flipped
Finalized 2026-07-10 (four-team close). Reported terms match
trade_terms.yaml exactly. The 2029 TBD branch SETTLED: CHA swaps ITS OWN
2029 first, "(6-30 protected)" per the finalization coverage — CHA-own
semantics (what v1 priced) and top-5-only operative worlds both confirmed.
verified_post_july6: true. Fresh Spotrac pull corroborates the full
pre-existing encumbrance stack; Spotrac had not yet processed the new CHA
components (anticipated by the runbook; reporting is the source).

## Environment incident (machine-local, no model impact)
Project venv absent on this machine; rebuilt. Python 3.12.4 produced a
jaxlib 0.10.2 DLL-load failure (cp312 wheel); rebuilt on Python 3.13.14
(the fit-engine interpreter) and JAX loads. Smoke test PASS (r_hat 1.00).
Suite 53/53 green after the two hard-gate tests were repointed at the gate
MECHANISM under both flag states (monkeypatched terms) instead of the live
config, which legitimately changed today.

## Step 2 — FINAL freeze 50f9b7bc5b19835b
291 spells / 1,264 rows / 228 departure events. Both disclosures match the
precomputed expectations: July-6 exits (Giannis/LaMelo/Kawhi -> departure)
touch NO holdout members; borderline prunes 3 of 13 in holdout
(anderry01_1, batumni01_1, lowryky01_1), re-gate sample 60 -> 57 spells,
46 -> 43 events.

## Step 3 — M2 refit (second and FINAL look, Ruling A)
C-index 0.907 PASS; Cox signs PASS; health clean (r_hat 1.0025).
Calibration slope 1.413 [boot 90% 1.127, 1.872] vs [0.8, 1.2]: RED, stands
documented, no third fit. b_contract_z -2.940 (dominant covariate).

## Step 4 — Engine D FINAL (50k, seed 20330706) + automatic checks
Gates as pre-declared: two_tier transient red (accepted per Ruling C), all
else green both variants. p70 re-check: crest 50.9 < 52.8 trigger -> crest
stands, no adjustment, no re-run. Departures over horizon: Edwards .573,
LaMelo .604.

FINAL exports: P(top4) .157, P(top10) .391, P(lottery) .619.
**P1 GRADED: CONFIRMED** — lighter-tailed than provisional (.167/.422) in
both pre-declared cells (see docs/predictions.md).

Wiring gap closed: run_m2() never exported edwards_hazard_FINAL.json; new
src/viz/export_hazard_final.py builds it from the CACHED m2_full posterior
(never re-calls run_m2, which would NaN the recorded r_hats on cache hit).
Edwards central P(departed by 2033) = .564 [.453, .677]; decline .707.
Walk-year odds multiple ~70x [43x, 104x] (0 vs 2 years remaining).

## Step 5 — priced pass + Part 1 fill
New src/sim/run_priced_pass.py (both top1 branches x both currencies,
payoff seed = config seed + 7) -> outputs/json/swap_pricing_FINAL.json.
Headline (top1_true, VORP): 2033 outright mean 2.24; swaps 2028/2029/2030
mean 0.66/0.65/1.32 at p_exercise .416/.123/.663; total per-path 4.86.

Part 1 filled: docs/drafts/stage1_edwards_hazard_draft_v3.md (v2 prose
untouched, slots only). Force-ranking check: contract_z dominates ->
"does the most work" clause RESTORED; win-pct stays non-superlative as
drafted. Calibration clause uses the red-cell branch.

## Open items
- BOBBY: numbers-in-place read of Part 1 v3 (RELEASE GATE), then publish.
- BOBBY: the carousel word (still pending on the record).
- Part 2 fill ~2 days post-read; Part 3 (replays, 15-arm tornado, equity
  final pass, total_asset_cost.json) mid-July.
- OUT OF SCOPE, FLAGGED: finalization coverage shows Mouhamadou Gueye
  landing in CHARLOTTE (with Spagnolo draft rights), while
  lamelo/data/trade_definition.json routes Gueye to MIN from BKN. Does not
  touch pick2033 (draft assets unchanged), but the lamelo-project roster /
  impact layer should re-verify before its numbers are reused.
