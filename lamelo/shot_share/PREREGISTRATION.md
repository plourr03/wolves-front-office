# Shot-share model: pre-registration (LOCKED 2026-06-29)

A small comp-based sub-analysis under the LaMelo project's rigor and kill-criteria discipline.
Estimates how much Anthony Edwards's SHARE of open (catch-and-shoot) three-point looks could
shift next to LaMelo. Frequency only. Efficiency is held fixed. Locked before the screen ran.

## Estimand

The change in Edwards's catch-and-shoot share of his 3PA when a lead creator joins, expressed
as a comp-based RANGE conditional on the fit-clicks (bull-case) scenario. NOT a forecast that the
shift will happen; it sizes the IF, which is the frequency mechanism behind the project's existing
fit-clicks reach-CF number (+3.5 to +7.7pp). It must not contradict or exceed that claim.

## Hard constraints (from the brief)

1. Efficiency held FIXED. Edwards is already elite on the catch-and-shoot three (49.6%, eFG 0.633,
   top-4 of 31 high-usage stars, `fit_decomp/lever1_findings.md`). We do NOT project the percentage
   moving. The mechanism is "LaMelo gets him more of the shot he is already great at," not "LaMelo
   makes him shoot better." We estimate only the SHARE/frequency.
2. Conditional / bull-case label. Whether Edwards actually cedes on-ball reps is a behavioral future
   fact the main project holds open (`DELIVERABLE.md` section 6; forward prediction #4, Ant-LaMelo
   net +3.0 [-2,+8]). This model never claims the unlock happens; it only sizes it if it does.
3. Comp-based, criteria pre-specified, take every qualifier. No cherry-picking by outcome.
4. Output a RANGE with a band, small N flagged. Decline a number if the gate fails.

## Metric

`cs_share = catch_shoot_fg3a / (catch_shoot_fg3a + pull_up_fg3a)` per player-season, regular season,
from `nba_player_tracking_season`. Edwards 2025-26 baseline = 139 / (139 + 363) = 27.7% (the 27% on
slide 2). Catch-and-shoot is the open-look proxy; pull-up is the off-the-dribble/contested mode.

## Universe

Player-seasons in `nba_player_tracking_season`, Regular Season, tracking era 2013-14 .. 2025-26.
NOTE: 2020-21 is absent from the warehouse tracking, so any before/after pair straddling it is
unavailable (this removes Booker+Chris Paul and LaVine+Lonzo Ball; flagged, not worked around).
PPG = Possessions.points / gp; APG = Passing.ast / gp; team = team_abbreviation (one per season).

## Criteria (the locked rule)

Let Y be the season the creator is gained; Y-1 the season before.

SUBJECT S qualifies in the pre-event season Y-1 if, in Y-1:
- PPG >= 20 (high-usage scoring wing/guard, the Edwards archetype; era-robust proxy for usage rate
  given per-game usage% does not cover the full tracking era uniformly),
- APG < 6.0 (a scorer, not already the lead distributor, so there is a creation role to cede),
- cs_share < 0.50 (on-ball / pull-up-heavy, like Edwards's 27%, so there is room to shift),
- gp >= 40 and total 3PA >= 80 (a real season on real 3PA volume).
And S also plays Y with gp >= 40 and tracking present in both Y-1 and Y.
Edwards himself is EXCLUDED from the comp set (he is the projection target).

TREATMENT (S gains a lead creator in Y): there exists a player C with
- APG >= 6.0 in Y-1 (an established lead distributor), gp >= 40 in Y,
- team(C, Y) == team(S, Y) AND team(C, Y-1) != team(S, Y-1) (a NEW teammate: covers both "C joins
  S's team" and "S joins C's team").
If several qualify, take the highest-APG new creator as the labeled C.

MEASURE: delta = cs_share(S, Y) - cs_share(S, Y-1). Take EVERY qualifying (S, Y) pair, regardless of
whether delta is large, small, or negative. The low/negative cases are the behavioral-risk floor
(the alpha kept the ball) and stay in the band.

## Confound control (descriptive, not causal)

cs_share has drifted up league-wide (offenses take more catch-and-shoot threes over time). Report:
- raw delta, and
- drift-adjusted delta = delta - league_drift(Y), where league_drift(Y) = mean cs_share(Y) minus
  mean cs_share(Y-1) over the reference pool (players with PPG >= 20, gp >= 40, total 3PA >= 80 in
  both seasons).
Flag team-change cases (S switched teams in Y), where system change confounds the creator effect.
This is associational, not causal, and is labeled as such.

## Output

Distribution of (raw and drift-adjusted) deltas across the comp set, applied to Edwards's 27%:
"his open-look share could move from ~27% to roughly X to Y%," band = the comp spread (report
median and the inter-quartile or min-max range), with N stated. Labeled a comp-based projection of
the fit-clicks/bull-case scenario, conditional on Edwards ceding reps, NOT a forecast.

Lens B (ceiling sanity bound only): the cs_share LEVEL of established movement shooters (high
cs_share on volume) in the same universe, as an upper anchor. Edwards stays a high-usage scorer, so
his projected share must land BELOW the pure movement-shooter level. This bounds the top, it does
not set the projection.

## Kill criteria (decline the number)

- If fewer than 5 qualifying comps, report DIRECTIONALLY only (no numeric range), consistent with the
  main project's decline-the-number discipline.
- If the drift-adjusted delta distribution straddles zero with a spread wider than its center (no
  resolvable signal), report directionally only.
- The projected share lift may not imply anything larger than, or inconsistent with, the existing
  fit-clicks reach-CF claim. It sits underneath that claim as its frequency texture.

## Reconciliation

The comp-based share lift is the FREQUENCY mechanism of the fit-clicks scenario already in the
project (`sim/01_scenario_findings.md`, `DELIVERABLE.md` section 4). It introduces no new title or
reach-CF claim. Its floor (minimal shift) is the same behavioral risk Lever 1 flagged. The forward
signal that will grade it is the one already logged: Edwards's off-ball possession share in the
first 20 games.
