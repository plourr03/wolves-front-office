# Kuminga: a league-wide read on the 2026 offseason

What signing Jonathan Kuminga changes for Minnesota, measured against what all 29 other teams did with their summer, on one pipeline run identically for everybody.

**Status:** Phases 0 through 3 complete. One item blocked on terms of use (2026-27 betting futures), two partially limited (league-wide pick ledger, counterfactual fives). See `docs/gaps_remaining.md`.

---

## The one thing to know before reading any number

Kuminga has **agreed**, not signed. NBA.com's tracker separates "multiple reports" from "officially announced" and puts him in the first bucket; the league transaction log has no row. Every Kuminga row in every output carries `reported_pending_official`, and the deal cannot legally be executed until Josh Green leaves the books.

## How it is built

```
freeze_inputs.py          one content-addressed warehouse snapshot for the whole build
  |
  +-- build_transaction_supplement.py   Kuminga's terms + the Hawks option, with sources
  +-- build_roster_snapshot.py          all 30 rosters for 2026-27, from contracts + transactions
  +-- patch_contracts.py                applies the supplement, restores the 2026 rookie class
  +-- build_injuries.py                 league-wide long-term injuries (R7)
  +-- build_pick_ledger.py              the ten draft assets in the four-team trade
  |
  +-- build_rotations.py                ONE minutes heuristic, all 30 teams, no hand-authored rotations
  +-- build_strengths.py                rollup -> 2026-27 net rating, four impact views
  |
  +-- run_sim.py                        all-30 CRN-paired before/after, 20k sims x 5 seeds
  +-- build_fcurve.py                   P(title | MIN net), so coalitions can be priced by interpolation
  +-- shapley.py                        exact 256-coalition decomposition + named scenarios
  +-- counterfactuals.py                Kuminga scenario fan + the counterfactual fives
  +-- eval_signing.py                   surplus under each view, and the cap gate
  +-- player_option.py                  the year-2 opt-out, and what Non-Bird rights cost
  +-- cap_branches.py                   both Green branches, 2026-27 through 2028-29
  +-- lineup_evidence.py                descriptive on/off from rebuilt 2025-26 stints
  |
  +-- build_outputs.py                  publication tables + the provenance appendix
  +-- build_figures.py                  waterfall, West ranking, scenario fan
```

Every script opens a run, logs its inputs and outputs to `logs/runs.jsonl`, and every published number traces back through `outputs/PROVENANCE.md` to a run id and a snapshot hash.

## The rules this was built under

Bobby's rulings R1 through R9 are recorded at the top of `docs/decisions.md` and are not re-litigated anywhere in the code. The two that shape everything:

- **R1:** no single title-odds point estimate. Ship the surplus argument, sign agreement across forks, the all-30 ordinal ranking, the CRN-paired band, and the cap mechanics. Point estimates are computed because the decomposition needs them, but every number ships as a band with the forks visible.
- **R2:** the all-30 scope is mechanical. Rosters rebuilt from contracts plus transactions, one documented minutes heuristic applied identically, no hand-authored rotations. The previous engine modelled a roster change for three teams and assumed the other 25 stood pat.

## What is honest about it and what is not

**Honest.** The warehouse is read-only and pinned to a content hash. The four impact views are carried separately end to end and never averaged into a single number. Both Green branches are carried. Every externally sourced fact has a URL. Where two sources disagree, both values are recorded.

**Not.** The matchup overlay is off, because the profiles it needs exist for only 12 teams and running it would break the identical-pipeline rule. The counterfactual fives are talent rollups that cannot see position. DARKO, the only external view available, is integer-rounded to 13 distinct values across 582 players. The 2027-28 and 2028-29 cap thresholds are a forward scale, not league-set figures. And there is no market comparison, because every odds source forbids automated retrieval.

## Reading order

1. `docs/phase0_inventory.md` -- what existed before any of this was built
2. `docs/morning_report.md` -- what the run found
3. `docs/decisions.md` -- every judgment call, with the alternative and the reason
4. `docs/gaps_remaining.md` -- what did not get done
5. `outputs/PROVENANCE.md` -- how to trace any number back to a run
