# Team-State Rollup: Schema Spec

**What this is.** The derived layer that sits on top of the three raw files (contracts, free agents, draft picks) and the CBA rules constants. It is the object the feasibility module actually queries. The raw files are inputs; this is the working table. Types shown are Postgres-flavored; adapt as needed.

**The grain.** One row per (team, season, scenario). Season covers 2026-27 through 2029-30 so the multi-year cascade is queryable. Scenario is the key idea below.

---

## 1. The scenario model (read this first)

Future-year salary is not a fixed number. It depends on assumptions: which player and team options get exercised, which non-guaranteed money survives its guarantee date, which of your own free agents you re-sign and at what cap hold. And the whole feasibility exercise is hypothetical anyway ("if we send out Gobert and Randle...").

So team_state is **parameterized by a scenario**, not a single static snapshot. Each scenario carries an explicit assumption set. This is also exactly how you implement the exit scenarios from the metric design: S1 (Randle out), S2 (Gobert out), S3 (both out) are just scenario rows for the Wolves with different rosters. The metric runs acquisition targets against those scenario rows.

Recommended approach: a base-case row per team-season, computed under documented default assumptions, plus additional scenario rows as needed. Build team_state as a function or materialized view that takes a scenario's assumptions and recomputes from the contracts file, rather than hand-maintaining totals.

Default ("base") assumptions, stored in the `assumptions` field so every row is auditable:
- Player options: counted on the books at option value until the player declines.
- Team options: counted if the team is expected to exercise (flag per player), else excluded.
- Non-guaranteed salary: counted if the guarantee date has passed, else excluded.
- Own pending free agents: carried at their cap hold until renounced or re-signed.
- Likely incentives included; unlikely incentives tracked separately.

---

## 2. `league_year_constants` (the rules as data)

The bridge from the prose rules reference to code. One row per season. Build this first; everything joins to it.

| field | type | notes |
|---|---|---|
| season | TEXT (PK) | '2026-27' |
| salary_cap | NUMERIC | ~165,000,000 (proj) |
| luxury_tax | NUMERIC | ~200,500,000 (proj) |
| first_apron | NUMERIC | ~209,100,000 (proj) |
| second_apron | NUMERIC | ~222,000,000 (proj) |
| full_mle | NUMERIC | ~15,000,000 (9.12% of cap) |
| taxpayer_mle | NUMERIC | ~6,100,000 |
| room_exception | NUMERIC | ~9,400,000 (5.678% of cap) |
| bae | NUMERIC | ~5,500,000 (3.32% of cap) |
| min_salary_by_yos | JSONB | minimum scale keyed by years of service |
| matching_pct_under_first_apron | NUMERIC | 1.25 (tiered, see derivation note) |
| matching_pct_first_apron | NUMERIC | 1.10 (CONFIRM) |
| matching_pct_second_apron | NUMERIC | 1.00 |
| repeater_lookback_years | INTEGER | 4 |
| repeater_threshold_years | INTEGER | 3 |
| frozen_pick_window | JSONB | params for the 3-of-5 vs 2-of-4 rule (CONFIRM) |
| is_projection | BOOLEAN | TRUE until the cap is set in early July |
| source | TEXT | |
| as_of_date | DATE | |

---

## 3. `team_state` (the core object)

Grouped for readability. One row per (team_abbr, season, scenario_id).

**Identity and scenario**

| field | type | notes |
|---|---|---|
| team_abbr | TEXT | PK part |
| season | TEXT | PK part, joins to constants |
| scenario_id | TEXT | PK part. 'base', 's1_randle_out', etc. |
| scenario_label | TEXT | human description |
| assumptions | JSONB | option/guarantee/FA assumptions baked into this row |

**Salary build-up** (all NUMERIC, so the total is transparent and auditable)

| field | notes |
|---|---|
| guaranteed_salary | sum of fully guaranteed contracts |
| nonguaranteed_salary_counted | included per the scenario's guarantee-date rule |
| player_option_salary_counted | included per scenario |
| team_option_salary_counted | included per scenario |
| cap_holds | own pending free agents, until renounced/signed |
| dead_money | waived-player charges |
| incomplete_roster_charges | rookie-min charges to fill to 12 if short |
| incentives_likely | counts toward cap and apron |
| incentives_unlikely | tracked separately (different apron treatment) |
| apron_team_salary | the tax/apron-relevant total. This is the number that gates the lines |
| cap_team_salary | for the under-cap room calc; different basis, mostly relevant to the few under-cap teams |

**Threshold distances and tier** (computed against constants)

| field | type | notes |
|---|---|---|
| distance_to_cap | NUMERIC | positive = under |
| distance_to_tax | NUMERIC | |
| distance_to_first_apron | NUMERIC | |
| distance_to_second_apron | NUMERIC | |
| tier | TEXT | enum: under_cap, over_cap_under_tax, taxpayer, first_apron, second_apron |
| is_taxpayer | BOOLEAN | apron_team_salary > luxury_tax |
| cap_room | NUMERIC | if under cap, else 0 |

**The toolbox** (derived from tier)

| field | type | notes |
|---|---|---|
| full_mle_available | BOOLEAN | only below first apron |
| taxpayer_mle_available | BOOLEAN | between first and second apron |
| room_exception_available | BOOLEAN | only if under cap and used room |
| bae_available | BOOLEAN | below first apron AND not used in prior year |
| tpe_total_available | NUMERIC | summary; detail in child table |
| min_exception_available | BOOLEAN | always TRUE |

**Hard-cap state**

| field | type | notes |
|---|---|---|
| hard_capped | BOOLEAN | |
| hard_cap_level | TEXT | none, first_apron, second_apron |
| hard_cap_line | NUMERIC | |
| hard_cap_room | NUMERIC | line minus apron_team_salary |
| hard_cap_trigger | TEXT | what move tripped it |

**Trade matching and permissions** (derived from tier)

| field | type | notes |
|---|---|---|
| matching_rule | TEXT | tiered_125, pct_110, pct_100 |
| can_aggregate | BOOLEAN | FALSE at second apron |
| can_take_back_more_than_send | BOOLEAN | FALSE at second apron |
| can_acquire_sign_and_trade | BOOLEAN | FALSE at or above first apron |
| can_use_prior_year_tpe | BOOLEAN | FALSE at second apron |
| can_send_cash | BOOLEAN | FALSE at second apron |
| can_sign_bought_out_above_mle | BOOLEAN | FALSE at or above first apron |

**Picks and assets** (derived from the draft-pick file via Stepien logic)

| field | type | notes |
|---|---|---|
| tradeable_firsts_count | INTEGER | outright firsts the team may legally trade now |
| tradeable_firsts | JSONB | list with year, origin, outright-vs-swap, timing notes |
| second_apron_pick_frozen | BOOLEAN | this season's frozen-pick status |

**Repeater status** (multi-year, needs tax_history)

| field | type | notes |
|---|---|---|
| taxpayer_this_season | BOOLEAN | = is_taxpayer |
| repeater_status | BOOLEAN | taxpayer in repeater_threshold of prior repeater_lookback seasons |
| repeater_window | JSONB | the prior-season tax flags used to derive it |

**Roster and provenance**

| field | type | notes |
|---|---|---|
| num_under_contract | INTEGER | for roster minimums and incomplete-roster charges |
| num_guaranteed | INTEGER | |
| as_of_date | DATE | |
| source | TEXT | |
| notes | TEXT | |

---

## 4. `team_trade_exceptions` (child table)

A team can hold several TPEs, so they do not fit in one team_state row. The Wolves hold three.

| field | type | notes |
|---|---|---|
| team_abbr | TEXT | |
| season | TEXT | |
| tpe_id | TEXT | |
| amount | NUMERIC | |
| created_date | DATE | |
| expiry_date | DATE | TPEs expire one year from creation |
| source_trade | TEXT | which deal generated it |
| is_active | BOOLEAN | |

---

## 5. `tax_history` (input for repeater status)

Small table, a few prior seasons per team. Without it, repeater_status cannot be computed.

| field | type | notes |
|---|---|---|
| team_abbr | TEXT | |
| season | TEXT | a prior season |
| paid_luxury_tax | BOOLEAN | |
| was_second_apron | BOOLEAN | feeds the frozen-pick window too |
| source | TEXT | |

---

## 6. Derivation notes for the tricky fields

- **tier**: compare apron_team_salary to the four lines in constants, in order. This drives most of the toolbox and permission booleans, so compute it once and derive the rest from it.
- **matching_rule**: under_first_apron to tiered_125, first_apron to pct_110, second_apron to pct_100. The under-apron tier is actually a bracketed formula (small outgoing salaries get 200% plus $250K, mid get 125% plus $250K, large get 100% plus a fixed amount). Encode the brackets; do not hardcode a flat 1.25.
- **hard_capped / hard_cap_trigger**: set when a move uses the full MLE, the BAE, a sign-and-trade acquisition, or (for the Wolves) any trade exception. Level is first apron for those; using the taxpayer MLE caps at the second apron. The evaluator sets these, then re-checks apron_team_salary against hard_cap_line on every subsequent move.
- **tradeable_firsts**: a function over the draft-pick file. A first is tradeable only if trading it does not leave the team without a first in two consecutive future years (Stepien) and is within seven drafts. Subtract frozen picks for second-apron seasons. This is why the pick file must be league-complete: you derive what a team owes from rows where pick_origin is not the controlling team.
- **repeater_status**: count paid_luxury_tax = TRUE across the prior repeater_lookback seasons in tax_history; TRUE if it meets repeater_threshold.

---

## 7. What this feeds: the transaction evaluator

team_state exists to answer one question fast: is a proposed move legal, and where does it leave the team. Every field above maps to a check. The evaluator is a separate build, but here is its contract so the schema's purpose is clear.

```
evaluate_move(
  team_state,            # the acquiring team's row for the season/scenario
  constants,             # league_year_constants for that season
  outgoing_player_ids,   # what the team sends (joins to contracts for salary)
  incoming_contracts,    # what the team receives
  pick_and_cash,         # picks/cash in the package
  exception_used         # none | full_mle | taxpayer_mle | tpe | sign_and_trade
) -> {
  legal: bool,
  failing_constraint: text,        # which check failed, in plain language
  matching_ok: bool,               # incoming vs outgoing under matching_rule
  aggregation_ok: bool,            # against can_aggregate
  takeback_ok: bool,               # against can_take_back_more_than_send
  st_ok: bool,                     # against can_acquire_sign_and_trade
  prior_tpe_ok: bool,              # against can_use_prior_year_tpe
  hard_cap_tripped: bool,
  hard_cap_level: text,
  new_apron_team_salary: numeric,
  new_tier: text,
  new_distances: {...}
}
```

Each boolean check reads a team_state field. That is the test of whether the schema is complete: if a check has no field to read, the schema is missing something.

---

## 8. Worked example: Wolves, 2026-27, base case

Filled from what we have, with the things to compute exactly flagged. Note one useful byproduct: the public figures do not perfectly reconcile (Marks's "under the tax" and "under the second apron" numbers imply slightly different totals because they predate the latest threshold projections). The rollup's job is to produce one internally consistent answer by summing the actual contract file against the final thresholds. Until then, the distances are Marks's and the exact total is "compute from contracts."

| field | value |
|---|---|
| team_abbr / season / scenario_id | MIN / 2026-27 / base |
| assumptions | options on books at value; own FAs at cap hold; Dosunmu not yet re-signed |
| apron_team_salary | compute from contracts; ~$192M to $195M range per current reporting |
| distance_to_tax | +$8M (under) |
| distance_to_first_apron | +$14M (under) |
| distance_to_second_apron | +$27M (under) |
| tier | over_cap_under_tax |
| is_taxpayer | FALSE (currently) |
| full_mle_available | TRUE (~$15M) |
| bae_available | TRUE (~$5.5M) |
| taxpayer_mle_available | TRUE (but you would use the full MLE here) |
| tpe_total_available | three TPEs: ~$10.8M, ~$7.6M, ~$6.6M (child table) |
| matching_rule | tiered_125 |
| can_aggregate | TRUE |
| can_acquire_sign_and_trade | TRUE |
| hard_capped | FALSE (but using any TPE, the full MLE, the BAE, or a S&T trips the first-apron cap) |
| tradeable_firsts | 2026 (pick ~28, tradeable on or after draft night), 2033 own first, plus a 2028 swap |
| second_apron_pick_frozen | FALSE |
| repeater_status | compute from tax_history; likely not yet a repeater but approaching |
| num_under_contract | ~10 |

The important reading: in the base case the Wolves still have the full toolbox, because they are under the first apron. The moment they re-sign Dosunmu (a separate scenario row), the build-up rises and the tier likely flips to taxpayer or first_apron, at which point the toolbox shrinks. That flip is the whole story, and it falls straight out of the schema.

---

## 9. Build order

1. `league_year_constants` (small, unblocks everything).
2. `tax_history` (small, needed for repeater and the frozen-pick window).
3. `team_state` base case, computed from the contracts file plus FA cap holds.
4. `team_trade_exceptions`.
5. The tradeable-firsts derivation over the pick file (needs the file to be league-complete).
6. The evaluator in section 7.
7. Wolves scenario rows: s1_randle_out, s2_gobert_out, s3_both_out. These are the exit scenarios the acquisition metric runs targets against.
