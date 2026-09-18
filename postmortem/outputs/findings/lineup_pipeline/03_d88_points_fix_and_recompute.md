# D88. The stint points defect is fixed in the shared library, and every figure that rode on it is recomputed

*2026-09-18. Fix in `lib/lineup_aggregation.py`. Validation `scripts/validate_stint_points.py`. Recompute `scripts/recompute_stint_figures.py`, table `outputs/tables/validation/d88_recomputed_figures.csv`.*

## What was wrong

`derive_stints` credited each possession's `points_scored` to whichever stint contained that possession's lookup timestamp. Points from a possession that spanned a substitution, and and-1 free throws shot after the clock stopped, landed on the wrong side. The library's own v1 caveat had measured the symptom (about 5 points per team-game, mirrored between the two teams) and called it AND-1 attribution noise, which undersold it: the points were not noisy, they were credited to the wrong team.

Measured against the box score on 24 Wolves games spread across 2023-24, 2024-25 and 2025-26, regular season and playoffs, 48 team-games:

| basis | mean error | mean absolute error | largest | exact |
|---|---:|---:|---:|---:|
| made shots (now) | +0.000 | 0.000 | 0.0 | 48 of 48 |
| possession (before) | +0.000 | 4.250 | 11.0 | 2 of 48 |

The possession-basis error is **3.89% of all points** and sums to exactly zero across the two teams of every game. That mirroring is the proof of the mechanism: a basket taken off one team was handed to the other, so team totals were wrong, not just stint totals.

The fix is to rebuild points from made-shot events, which are already attributed to the stint containing each shot: `points = 2*fgm + fg3m + ftm`. Stint points now equal the box score exactly. The old figures are kept per stint as `points_for_possession_basis` and `points_against_possession_basis` for diagnosis only.

## How much it moved a whole sample, not just a stint

Over Minnesota's 15 games in the 2024-25 playoffs, the old basis gave Minnesota **68 points too few** and its opponents **exactly 68 too many**. On 1,330 possessions that is about 5 points per 100 on each side of the ledger, in the same direction, which is why the team's playoff net rating on this pipeline flips sign.

## Recomputed figures, before and after

41 figures from the findings documents. Every "before" reproduces the published number exactly, which is the check that the recompute harness is the same pipeline. "After" carries a bootstrap interval on the corrected basis (1000 resamples, seed 42, 95%), Q2's own settings.

**Regular season figures barely move.** The four-season team table moves by 0.9 to 1.6 points per 100, every pairing moves by less than 2, and every one stays inside its interval. Sample size is doing the work: over 800 to 1,350 minutes the mirrored errors mostly cancel.

**Playoff figures move a lot.** Five change sign.

| figure | published | corrected | shift | 95% interval on the corrected basis |
|---|---:|---:|---:|---|
| Team net rating, 2024-25 PO | -3.68 | **+6.59** | +10.26 | -4.03 to +16.36 |
| Gobert + Reid, no Randle, 2025-26 PO | +9.82 | **-5.51** | -15.33 | -26.46 to +15.14 |
| Rudy Gobert on/off, 2025-26 PO | +1.6 | **-11.27** | -12.89 | -31.81 to +10.13 |
| Jaylen Clark on/off, 2025-26 PO | +4.7 | **-4.23** | -8.92 | -39.38 to +26.96 |
| Edwards on, Randle off, 2025-26 PO | +6.68 | **-6.45** | -13.13 | -32.86 to +20.24 |
| Julius Randle on/off, 2025-26 PO | -16.30 | **-4.71** | +11.58 | -24.49 to +15.75 |
| Donte DiVincenzo on/off, 2025-26 PO | +18.4 | **+35.56** | +17.20 | +10.70 to +60.72 |
| Dosunmu five, 2025-26 PO | -27.24 | **-37.24** | -10.01 | -81.17 to +8.29 |
| DiVincenzo five, 2025-26 PO | +3.01 | **+9.33** | +6.32 | -25.00 to +42.32 |
| Gobert + Randle, no Reid, 2025-26 PO | -12.22 | **-18.81** | -6.59 | -34.23 to -3.50 |
| Team net rating, 2025-26 PO | -0.92 | **-6.35** | -5.43 | -16.78 to +3.41 |

**Only one figure moved by more than its own interval:** the 2024-25 playoff team net rating, which shifted 10.26 against a half-width of 10.19. Every other shift, including the five sign changes, sits inside the uncertainty the figure already carried. That is the honest reading: these playoff samples were never precise enough to carry the sentences built on them, and the correction makes that visible rather than creating it.

**A control that must not move, and does not:** three-point attempts per 100 possessions, Reid at the 5 and Gobert at the 5, are identical on both bases (37.35 and 28.35, shift 0.00). The defect is in points only. Separately, the published 29.2 for Gobert at the 5 does not match 28.35 on either basis, which is a filter difference in my recompute rather than a points issue, and is not a D88 effect.

## Which sentences no longer hold

- **"The Gobert plus Reid pairing was positive in the playoffs" does not hold.** It was +9.82 and is -5.51. What survives is the *ordering*: the Reid pairing is still about 13 points per 100 better than the Randle pairing (-5.51 against -18.81) over 127 and 197 playoff minutes. Q2's comparative claim stands, its absolute claim does not.
- **"Randle was the worst on/off on the team" does not hold.** He was -16.30 and is -4.71. On the corrected basis Gobert (-11.27) and Dosunmu (-11.60) are lower, and Edwards (-13.33) is lowest of the rotation. The Q8 verdict "use Randle correctly" cited -16.30 explicitly.
- **"Gobert was a positive on/off in the playoffs" does not hold.** +1.6 becomes -11.27. The Q8 "keep Gobert, with conditions" verdict cited pairing and RAPM evidence rather than this figure, but the figure was part of the picture.
- **"Minnesota's 2024-25 playoff run was negative on the lineup-grain pipeline" does not hold.** -3.68 becomes +6.59, and this is the one figure whose shift exceeds its own interval.
- **DiVincenzo's case gets stronger, not weaker.** +18.4 becomes +35.56, with an interval that excludes zero (+10.70 to +60.72). The "protect the recovery" verdict is better supported than it was.
- **Every regular-season claim survives**, including "Gobert plus Randle is not structurally bad" (+5.71 and +4.57 become +4.99 and +6.18) and DiVincenzo's +7.57 in 2025-26 RS (+7.32).

## Still exposed, and not recomputed here

**The possession grain, which is where RAPM lives.** The mirrored error proves the possession table credits points to the wrong team, not merely to the wrong stint. `analyses/q2_localize/rapm.py`, `rapm_recent.py`, `analyses/q1/pbp_splits.py` and the fit engine's `src/models/build_possessions.py` read possession `points_scored` against `offensive_team_id` directly and do not rebuild from made shots. This is the same root cause and it is NOT fixed by D88. It reaches:

- The RAPM tables (`rapm_player_impacts.csv`, the 2023/2024/2025-only splits, `gobert_career_arc.csv`).
- **The published article draft** `articles/02_how_they_got_here_first_draft.md`, lines 116 and 120: "Gobert's offensive impact ... has gone from positive in 2023-24 to clearly negative in 2025-26" and "DiVincenzo had been the highest-impact player in the entire league sample". Both are RAPM claims. They are not refuted here, they are unverified, and RAPM's ridge fit is not a job this pass can do honestly in passing.
- Q1's halfcourt and transition splits (ORtg 95.0 and 176.8) and the clutch table, all possession-grain.

**The fit engine's fork.** `counterfactual-fit-engine/src/stints/stint_builder.py` is a deliberate hash-pinned copy of this library ("pinned original, NEVER edited") with the same defect. Fixing it breaks the pin by design, so it needs Bobby's call, not a quiet edit. Everything downstream of its stint panel carries the defect: `tripwire-backtest` PAIR-DRTG (`compute_pair_drtg_reliability.py`, `compute_scenarioA_labels.py`, `compute_phase1_reliability.py`) and the `jaden_calibration` JD-COVER metric and its report. The tripwire panel is about 15,669 games, so recomputing it is a scheduled job rather than part of this pass. The affected metrics are all `points_against` based defensive ratings, so expect shifts of the same order: small on season-length samples, large on the small on/off windows these markers use.

**Q2 and Q8 output CSVs on disk are still the old basis.** The recompute above reads the frozen stint caches and reports figures; it does not overwrite `outputs/tables/q2_localize/*` or `outputs/tables/q8_player_decisions/*`. Re-running those scripts now regenerates them correctly, because they call the fixed library.

## Kuminga project, for the trail

The defect was found there (D82), which retracted two of its own sentences (D84) and warned that postmortem was exposed. That warning had not reached postmortem until now. The kuminga figures already use rebuilt points and do not change.
