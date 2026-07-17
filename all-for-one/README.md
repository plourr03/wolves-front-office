# ONE FOR ALL

Public name of this project and series. Internal codename and current repo path: `all-for-one` (working title "If I Were Tim Connelly").

**Name / path alias.** The directory is `all-for-one/`; the published name is **ONE FOR ALL**. Both refer to the same project. This alias is recorded here per the naming decision of 2026-07-17.

**On the physical rename.** Bobby recommended renaming `all-for-one` -> `one-for-all` "now while paths are cheap" (the same calcification logic as the day-one `tripwire-basktest` typo fix). It was deferred at the moment of the decision for one operational reason: background verification/analysis workflows were writing into `all-for-one/board/...` at the time, and renaming the directory mid-write would have broken them. Per Bobby's stated fallback ("if Bobby prefers keeping all-for-one as the internal codename, skip the rename and record the alias in the README"), the alias is recorded here and the codename retained. The physical `git mv all-for-one one-for-all` (plus a sweep of in-repo path references in the docs) is a clean one-command follow-up available on request, best run once no workflows are writing to the tree.

## What is here

- `tripwire-backtest/` — the February 2027 deadline-alarm backtest. `TRIPWIRES.md` is the (unfrozen) pre-registration draft; `doc/REVIEW.md` indexes the phases. Ships one binding wire (AVAIL-PACE) plus the FC-DRB structured advisory. Freeze target 2026-10-20.
- `board/` — the ONE FOR ALL master plan board.
  - `docs/board_spec.md` (v2.1, source of truth): state space, root node, decision calendar, the salvage term.
  - `docs/jaden_markers.md` + `jaden_calibration/` — the Jaden tier dial and its calibration class (v0.2: JO-GROWTH-primary LEAP, defense-screened).
  - `build/` — the board solver, built in steps: `board_step1.py` (scaffold + reachable count), `board_step2.py` (transition structure + the hazard-reads-value keystone), `board_step3.py` (real melo_avail prior + acceptance-model arm costs + interim gated leaf equity + the salvage/ARM-CONVERT rider + dual-curve harness). Each step has a `_report.md` and stops for review. All numbers are placeholder/interim/TUNE until the machinery lands step by step.

## Objective

Maximize P(championship while Anthony Edwards is a Timberwolf), with the salvage exception (v2.1): a departure is not worth zero, it salvages a leverage-adjusted return capped at SALVAGE_CAP, and no live contender is traded away for it (a checked property of every board solve).
