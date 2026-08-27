# Saturday lock runbook

**Status as of 2026-08-27 13:16 UTC: NOT TRIGGERED.** The league transaction feed refreshed this morning (run 03:33, max transaction_date 2026-08-26) and contains no Josh Green move and no official Kuminga row. Both branches remain live and every Kuminga row still reads `reported_pending_official`.

Execute on resolution, or by Sunday morning regardless.

---

## L1. Green resolves

**Check first:**

```bash
python -c "import sys;sys.path.insert(0,'postmortem');from lib import db;print(db.query(\"select * from nba.nba_transactions where transaction_date>='2026-08-27' and (team_slug='timberwolves' or player_slug='josh-green')\").to_string())"
```

**Then, in `kuminga/scripts/build_transaction_supplement.py`,** add a record with `group_sort="SUPP_GREEN_RESOLVED"`, the resolution type, and **two source URLs** per R8.

**If TRADED and a player comes back:**
1. Add the incoming player to `kuminga/data/transaction_supplement.csv` with his salary.
2. Re-run: `patch_contracts.py`, `build_roster_snapshot.py`, `build_team_state.py`, `build_rotations.py`, `build_strengths.py`, `run_sim.py`, `build_fcurve.py`, `shapley.py`.
3. **Green becomes a lever, not a precondition.** Add `green_out` to `MOVES` in `shapley.py` and to `REMOVE_WHEN_APPLIED`; the coalition count goes from 256 to 512, which is still instant on the f-curve. Re-run `compare_ceiling.py` to see whether any verdict moves.
4. Remember the first-apron finding: any incoming salary above **$400,183** crosses the first apron at a 14-man roster. If a player comes back, Minnesota is a first-apron team and loses the bi-annual exception, sign-and-trade acquisition, and prior-year trade exceptions. Say so.

**If STRETCHED:**
1. Promote the stretch branch to primary in `cap_branches.py` (set a `PRIMARY_BRANCH` constant).
2. Add the $4,893,004 per season dead money to 2026-27, 2027-28 and 2028-29 in the contract book so `team_state` picks it up.
3. No strength re-run is needed: R3 already has Green off the floor in both branches.

**Either way:** retire the other branch in `cap_branches.md` with a one-line note saying which resolved and when, rather than deleting it.

## L2. The signing becomes official

1. Verify the announced dollars against R4 ($6,064,000 / $6,367,200 player option / $12,431,200 total).
2. **Log any difference in `decisions.md` with before and after.** A different year-one figure changes the apron arithmetic, and the whole lede sits inside a $249,829 margin.
3. Promote every `reported_pending_official` row in the supplement to `official`, and drop the standing caveat from the top of the piece skeleton.
4. If the reported total is $13.0M rather than $12.4M (two outlets carry each), that is $568,800 of difference and it does not change legality under either branch, but it does change the surplus. Re-run `eval_signing.py`.

## L3. Regenerate everything

```bash
python kuminga/scripts/build_outputs.py
python kuminga/scripts/build_figures.py
python kuminga/scripts/reconcile_figures.py
python kuminga/scripts/build_final_numbers.py
```

`final_numbers.md` is the gate: if a figure is not on it, it does not go in the piece.

## L4. Refresh the skeleton

`kuminga/docs/piece_skeleton.md` is written against the unresolved state. On resolution:
- Section 1's lede changes from "could not legally sign him" to whichever branch happened.
- Section 1's branch table collapses to the branch that occurred.
- Every run ID in brackets must be re-pulled from the new `final_numbers.csv`.

---

## What must NOT change without re-verification

- The canonical apron basis: contracted salary only, no placeholder, no cap holds.
- The four-view structure. Never average the forks into one number.
- The quotability bar: posterior sd above 1.5 is not quotable.
- The standing rule that a title-odds point estimate does not ship, which the three-season backtest now supports quantitatively (error 1.4 to 2.3pp against a spread of 2.1pp).
