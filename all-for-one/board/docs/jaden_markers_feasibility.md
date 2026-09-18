# Jaden Markers: Feasibility Pass

> **EXPOSED, NOT YET RECOMPUTED (D88).** JD-COVER and any PAIR-DRTG marker here is built on `points_against` from the fit engine's forked stint builder, which credits about 3.4% of points to the wrong team. The upstream library is fixed as of 2026-09-18; the fork is hash-pinned and was deliberately left alone, so this panel still carries the defect. Small on/off windows are where it bites hardest. Detail: `postmortem/outputs/findings/lineup_pipeline/03_d88_points_fix_and_recompute.md`.

For `jaden_markers.md` (draft v0.1). Produced 2026-07-17 by the warehouse agent, in the slot after tripwire Phase 3 and before the Phase 4 stop. Coverage and grain only, no builds. The SPACE-ANT rule applies: no marker freezes on data the warehouse cannot produce; anything uncomputable is struck, not approximated.

**Headline: every marker is computable. Nothing is struck.** The one marker whose source was genuinely in question, JD-HOLD, is supported by `nba_boxscore_matchups`, which carries per-matchup points allowed with zero nulls.

## Defensive gate

### JD-LOAD (deployment) — FEASIBLE

Matchup time share against opponents' primary perimeter creators. Source: `nba_boxscore_matchups`, grain (game, offensive player, defender), covering **2017-18 through 2025-26**. Per matchup it carries `partial_possessions`, `matchup_minutes`, and `percentage_defender_total_time`. Jaden has real defender data every season since 2020-21 (587 to 907 matchups/season, 347 to 377 distinct opponents guarded, 3,100 to 6,200 partial possessions/season). "Primary perimeter creators" is identified by joining the offensive player's usage/position (high-usage guards and wings). Readable at R1, near noise-free, as the marker claims.

### JD-COVER (the anchor claim) — FEASIBLE

Team defensive rating in LaMelo's minutes, Jaden on vs off. Source: the stint panel (`build_stint_panel.py`, proven feasible back to 2010-11 and green on 2025-26). Filter to LaMelo-on stints, split by Jaden in/out of `lineup_id`, aggregate `points_against` over `possessions_def`. Grain: stint. Note the pairing itself is 2026-27 (future), so the season-end read is computed in-season once games exist; any pre-season calibration of the 3.0-per-100 threshold uses other star-plus-wing pairs. The possession-floor question (the draft threshold's minimum) is a TUNE, computable from the panel.

### JD-HOLD (suppression) — FEASIBLE (the source check answered)

The question posed: can `nba_boxscore_matchups` support per-matchup points allowed vs the opponent's own season baseline, at what grain, with what nulls?

- **Yes.** The table carries `player_points` (points the offensive player scored in that matchup, i.e. points Jaden allowed), plus `matchup_field_goals_made/attempted/percentage`, `matchup_three_pointers_*`, `matchup_free_throws_*`, and `partial_possessions`.
- **Grain:** (game, offensive player, defender). Aggregate across games to a season-level defender-vs-offensive-player cell.
- **Nulls:** `player_points` is **0 null** across all 2.04M rows. `partial_possessions` is null-or-zero on **0.07%** (1,489 rows). Mean partial possessions per matchup is 5.25, so single-matchup samples are tiny and the diff-in-diff must aggregate to season level with a possession floor (TUNE), exactly as the marker says ("too noisy for midseason; honest by April").
- **The baseline:** the offensive player's own scoring rate, computable either from the same table aggregated across all their defenders, or from player-season stats. The diff-in-diff (how much less a primary option scores per possession against Jaden than against the league) is fully supported.
- **Coverage caveat:** matchup data starts 2017-18, so JD-HOLD and JD-LOAD (and the calibration class, when it runs) are bounded to 2017-18 onward. Jaden's own career (2020-21+) is fully covered.

## Offensive ladder

### JO-EFF (the climb) — FEASIBLE

True shooting percentage vs the league and his own trailing-three-season baseline. Source: `nba_player_season_bio.ts_pct` (all seasons), league mean computable from the same, trailing-3 from his prior rows. Straightforward.

### JO-FLOOR (anti-vanishing) — FEASIBLE

Scoring attempts per 75 possessions vs trailing baseline. Source: `nba_player_stats` (fga, fta) with possessions from `nba_player_advanced_stats.possessions`. Scoring attempts = FGA + 0.44*FTA, per 75 possessions. All seasons.

### JO-GROWTH (true-leap distinguisher) — FEASIBLE per rung

Section 4 enumerates three rungs; computability reported per rung:

| Rung | Source | Verdict |
|---|---|---|
| Self-created scoring efficiency rising | `nba_player_tracking_season`, `PullUpShot` measure (`pull_up_efg_pct`, `pull_up_pts`, `pull_up_fga`) and `Drives` measure (`drive_pts`, `drive_fg_pct`, `drive_ftm/fta`), 2013-14+ | **FEASIBLE.** Self-created = pull-up jumpers + drives; efficiency from the pull-up eFG% and drive scoring cuts. Tracking-era only (2013-14+), which covers all of Jaden's career. |
| Free throw rate rising | `nba_player_stats` (fta, fga); FTr = FTA/FGA | **FEASIBLE**, all seasons. |
| Three-point volume AND accuracy both rising | `nba_player_stats` (fg3a per game, fg3_pct) | **FEASIBLE**, all seasons. Both components present; the "both rising" conjunction is a simple joint test. |

None of the three rungs is struck. All are computable on Jaden's career span.

## Summary

| Marker | Source | Coverage | Verdict |
|---|---|---|---|
| JD-LOAD | nba_boxscore_matchups | 2017-18+ | FEASIBLE |
| JD-COVER | stint panel | 2013-14+ (pair is future, computed in-season) | FEASIBLE |
| JD-HOLD | nba_boxscore_matchups (`player_points`) | 2017-18+ | FEASIBLE |
| JO-EFF | nba_player_season_bio (ts_pct) | all seasons | FEASIBLE |
| JO-FLOOR | nba_player_stats + advanced (possessions) | all seasons | FEASIBLE |
| JO-GROWTH: self-created | tracking PullUpShot + Drives | 2013-14+ | FEASIBLE |
| JO-GROWTH: FT rate | nba_player_stats | all seasons | FEASIBLE |
| JO-GROWTH: 3P vol + acc | nba_player_stats | all seasons | FEASIBLE |

**Nothing struck.** Two coverage caveats to carry into the freeze: the matchup-based defensive markers (JD-LOAD, JD-HOLD) and any matchup-based calibration are bounded to 2017-18+; and JD-COVER's specific LaMelo-plus-Jaden read is a 2026-27 in-season computation, with any pre-season threshold calibration drawn from analogous pairs.

## Out of scope (per Bobby, 2026-07-17)

The calibration class in `jaden_markers.md` section 5 (two-way wings whose team added a high-usage creator; Gordon DEN 2021, Bridges NYK 2024, Anunoby NYK 2024) is **queued, not started**. It gets scoped after the Phase 1-3 review using the same extraction discipline as tripwire Scenario A. This feasibility pass confirms only that its inputs (per-opportunity defensive and self-creation metrics) exist in the warehouse for 2017-18 onward.
