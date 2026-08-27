# Decision log: Kuminga project

Every judgment call made during the autonomous run. Format: the call, the alternative, why.
Rulings R1-R9 came from Bobby and are recorded at the top for reference, not re-litigated.

## Standing rulings (from Bobby, 2026-08-26)

| Ref | Ruling |
|---|---|
| R1 | No single title-odds point estimate. Ship surplus argument, Shapley sign agreement, all-30 ordinal ranking, CRN-paired band, cap mechanics. Compute points internally. |
| R2 | All-30 scope is mechanical: rebuild rosters from contracts + transactions, one documented minutes heuristic applied identically. Retire opponent_rosters.json assumed_moves. |
| R3 | Carry both Green branches. Both have Green off the 2026-27 roster, so strength/attribution runs once; only cap outputs fork. |
| R4 | Kuminga hand-entered: Y1 $6,064,000 TPMLE, Y2 $6,367,200 (5% raise) player option, total $12,431,200. Tag "reported, pending official". Add placeholder 14th-man minimum. |
| R5 | Counterfactual fives on rollup-plus-net-rating, labeled talent rollups. No fitengine synergy build. |
| R6 | Baseline = 2025-26 end-of-season roster for all 30 (as of 2026-06-13, no injuries), through the new pipeline. |
| R7 | DiVincenzo out for 2026-27 RS in primary; sensitivity playoff return at 80%. League-wide long-term-out = sourced report of 20+ games. |
| R8 | Source precedence: official NBA/team release > Spotrac/B-Ref/RealGM > reporters. Log every conflict with both values and URLs. |
| R9 | Fold in the external fact-verification pass; conflicts logged here, resolved by R8. |

---

## Decisions

### D1. Cap thresholds upgraded from projection to final (item 1)

**Call.** Replaced the 2026-27 row in `offseason/data/league_year_constants.json` with the league's actual figures and set `is_projection: false`. Cap $164,961,000, tax $200,428,000, first apron $209,015,000, second apron $221,686,000, minimum team salary $148,465,000, non-taxpayer MLE $15,044,000, taxpayer MLE $6,064,000, room $9,366,000, BAE $5,477,000.

**Alternative.** Adopt the `alebron/data/cap_state.json` "verified" set without an external check, as the fallback in item 1 permitted.

**Why.** A primary source was reachable, so the fallback was not needed. NBA.com confirms the cap/tax/apron/min-team figures; Hoops Rumors confirms the exception values and their term limits. The `alebron` set turned out to be correct on all five figures it carried, so this also retro-validates that file. Regenerated via `build_league_constants.py` rather than hand-edited, so the out-years rescale consistently off the new anchor.

**Why it matters.** The second apron moved $314,000 from the projection ($222,000,000 to $221,686,000). That is the difference between a full-TPMLE signing being legal and illegal for Minnesota while Josh Green is on the books. The engine had been reading the projection.

**Also added** (same file, same run): `exception_terms` (max years and max raise per exception) and `bird_rights` (service-time grades and starting-salary rules). Both previously existed only as prose in `offseason/docs/nba-roster-rules-reference.md`. The `exception_terms` block settles a consistency check on its own: the taxpayer MLE is capped at **two years**, which is exactly the reported length of the Kuminga deal. A three-year deal would have been impossible on this exception.

**Side effect, accepted.** This file is shared with `core_max`, `offseason` and `all-for-one`. Their feasibility gates will now answer on final rather than projected numbers. That is a strict improvement, but it means any previously published figure that depended on the June projection is no longer exactly reproducible from the current constants file. The pre-edit file is preserved at `kuminga/data/league_year_constants.PRE_ITEM1.json`.

