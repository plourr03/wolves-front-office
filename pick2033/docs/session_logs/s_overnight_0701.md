# Overnight session (2026-07-01 → 07-02) — directive execution
Auto mode per Bobby's overnight directive. Constraints held: nothing
publishes, no gate rulings by the agent (two failures parked with memos),
no threshold revisions, sealed sets sealed, provisional tags throughout,
priced runs hard-gated.

## ON-1: 8.4 preview re-judged — PASS (both variants)
Amendment 3 caught an inclusive-boundary bug, not a pace bug: B-Ref stores
win_pct at 3 decimals, so exactly-20-win teams (.244) were excluded by
`win_pct*82 <= 20`. Bottom base rate corrected .0525 -> .0632. Re-judged
under the ratified operationalization: terminal + transient PASS, v1/v2
identical. outputs/validation/early_84_rejudged.md.

## ON-2: PROVISIONAL spells + Model B — 3/4 gates, calibration parked
- Freeze 49f2135d: 304 spells (15 pruned, 13 SETs, 21 borderline KEPT+tagged,
  3 pending July 6). En route, found+fixed a tuple-order bug that silently
  zeroed deep_run_recent (regression test added: Duncan 2004, KG 2005/2003).
- Model B (contract covariate OMITTED, 0% coverage — loud caveat): health
  clean, C-index .675 PASS, Cox signs 7/7 PASS (all face-valid), calibration
  slope .664 FAIL -> PARKED (46-event holdout, bootstrap CI [.38, 1.04],
  P(pass) .30; memo recommends re-gate at the M2 contract backfill).
  model_b_calibration_decision.md.
- Edwards provisional curves exported (NOT publishable): cumulative
  P(departed by 2033) .846 central — inflated by the missing contract
  covariate by construction. Borderline sensitivity: +.005 (negligible).

## ON-3: Engine D — 4/5 gates, transient parked
Built: play-in module (probit single-game, +2.6 home, sd 13.4), 3-2-1
lottery with cross-year constraints tracked per path, roster tier (Model C
aging + provisional-B departures + blend), 50k paths in ~200s (5x under
budget). THREE real bugs found through gate/sanity discipline, all fixed:
1. Recursive prior-chain leak (AR step evolved from the blended state;
   roster optimism compounded -> CHA median 51 wins in 2033). Spec 7.4
   implies a separate prior chain; implemented.
2. Roster-calibration construction mismatch (sim aggregated a top-10
   rotation, history aggregated full team minutes -> MIN/CHA 2027 sixty-win
   rates of 57-77%). Single shared rotation_aggregate() both sides now.
3. Selection-on-noise + overlay duplication (Diabate +6.3 low-minutes
   artifact ranked CHA's best; Dosunmu doubled because the 7-01 snapshot
   already had him). Reliability shrinkage w = mp/(mp+1500) toward -1.0;
   idempotent dedupe.
Final medians: MIN 51 -> 37 wins (departure worlds accumulate), CHA 45 ->
51 -> 43 (young-core crest, then reversion). Gates: conservation, slot
permutation, tail TERMINAL, autocorr all PASS both variants; transient
FAILS for two_tier on approach-from-below convergence (excess decays
.023 -> .007 by 2029 then converges up to the stationary .068 — amendment 2
assumed decay-from-above). PARKED: engine_d_transient_decision.md, three
options for Bobby, none applied.
PROVISIONAL 2033 pick posterior: P(top4) .167, P(top10) .422, P(lottery
16-team) .664.

## ON-4: E1 + E2 — green, pricing gated
- E1 first fit collapsed (s_d funnel + symmetric-t targeting the median of
  skewed VORP: flat curve). Fixed: non-centered increments + Normal
  likelihood (mean estimand) + empirical band residuals for realized draws.
  VORP slot1 5.66 / slot14 1.74 / slot30 .72; WS track corr .99; seconds
  flat value .372 VORP. Cache-key lesson re-learned: model changes must bump
  MODEL_CODE_VERSION (a stale cache masked the first fix attempt).
- E2 payoff machinery + pick_ledger resolution stack: 8 hand-built standings
  tests green incl. 2029 conveyance worlds, 2030 SAS-stack, both
  top1_carries_to_CHA branches, and the verified_post_july6 hard gate
  (tested to raise). NO priced runs.

## ON-5: equity curve — running at log time
4 tiers (refs BKN/LAL/DEN/BOS) x 7 deltas x 5 CRN-paired seeds, 20k sims
each, under the GLOBAL python (offseason bracket_sim needs statsmodels).
Rebuild-tier deltas ~0pp (correct: +2 net buys a bad team no title equity);
mid tier ~+1.1pp per net point. Deltas only stored, per the gate ruling.

## ON-6: verified already-done items
Boundary rule + branch tests, Bosh 2016 qualification (1,778 mp, rank 17),
Robertson All-NBA (covariate bug fixed, not a name-join miss) — all landed
pre-directive with tests; in suite.

## ON-7: 2013/2019 replay cuts
config/replay_nets_2013.yaml (terms to verify at build) +
historical_replays.py as-of cuts (panel/draft/spells with edge
re-censoring): as-of-2013 = 924 panel rows, drafts <= 2009, 192 spells.
Replay FIT deferred to post-final-spells per directive.

## ON-8: suite 53 green; commits f263279a, 8931e70c, a5bb0a5d (+ final)

## Parked for Bobby (decision memos, no action taken)
1. Model B calibration slope (model_b_calibration_decision.md)
2. Engine D transient approach-from-below (engine_d_transient_decision.md)

## Skipped/deferred per constraints
- Priced swap runs (verified_post_july6 gate up, untouched)
- Stage 1 finalization (borderline pass + July 6 + M2 contract backfill)
- Replay fits (post-final-spells)
