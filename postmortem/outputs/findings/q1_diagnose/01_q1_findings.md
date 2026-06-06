# Q1 Diagnose the Break: findings

**Date:** 2026-05-17
**Status:** Q1 v1 build complete. Centerpiece cross-tab plus dropoff analysis with bootstrap CIs.
**Sample:** Wolves 2014-15 through 2025-26; historical baselines from 144 playoff team-seasons across 9 non-COVID years.

## Headline

**The Wolves' 2025-26 playoff dropoff is meaningfully worse than league norms in two specific places: three-point attempt rate and effective field goal percentage.** Both signal that the offense is generating worse shots in playoffs than it does in the regular season, beyond the normal playoff degradation other teams experience. The net rating dropoff (-9.1) is bigger than league average (-6.4) but within one standard deviation; the offensive components driving it are the diagnostic.

The 3PA-rate dropoff (point -0.078, 95% CI [-0.104, -0.054]), the eFG dropoff (point -0.065, 95% CI [-0.087, -0.040]), and the off-rating dropoff (point -8.22, 95% CI [-14.04, -2.97]) all have bootstrap CIs that exclude zero. The findings are statistically distinguishable from zero, not just directional. The net rating dropoff CI [-19.22, +0.45] crosses zero, so the headline number's magnitude is uncertain even though the component-level offensive collapse is statistically real.

This cross-references LAFI C5 (Shot Quality Decay) cleanly. Q1's team-level dropoff analysis and LAFI's structural team-season shot-quality analysis point to the same finding from different directions.

## Wolves year-over-year Edwards-era cross-tab

| Metric | 2023-24 RS | 2023-24 PO | 2024-25 RS | 2024-25 PO | **2025-26 RS** | **2025-26 PO** |
|---|---|---|---|---|---|---|
| Off rating | 114.6 | 114.8 | 115.7 | 113.6 | **115.6** | **107.4** |
| Def rating | 108.1 | 110.3 | 110.7 | 110.8 | **112.3** | **113.1** |
| Net rating | +6.5 | +4.5 | +5.1 | +2.8 | **+3.3** | **-5.8** |
| Pace | 97.8 | 93.4 | 97.9 | 96.1 | 101.5 | 100.8 |
| Off eFG | 0.559 | 0.538 | 0.554 | 0.539 | **0.559** | **0.495** |
| Off TOV% | 0.142 | 0.129 | 0.144 | 0.158 | 0.143 | 0.134 |
| Off OREB% | 0.232 | 0.263 | 0.258 | 0.289 | 0.257 | 0.257 |
| Off FT rate | 0.270 | 0.285 | 0.249 | 0.256 | 0.285 | 0.264 |
| Def eFG | 0.515 | 0.538 | 0.532 | 0.527 | 0.529 | 0.531 |
| Def TOV% | 0.142 | 0.140 | 0.146 | 0.155 | 0.144 | 0.128 |
| Def OREB% | 0.231 | 0.216 | 0.249 | 0.270 | 0.263 | 0.218 |
| Def FT rate | 0.252 | 0.273 | 0.232 | 0.272 | 0.282 | **0.338** |
| Off 3PA rate | 0.384 | 0.393 | 0.455 | 0.434 | **0.420** | **0.342** |
| Off 3P% | 0.387 | 0.359 | 0.377 | 0.358 | 0.370 | 0.337 |
| Def 3PA rate | 0.372 | 0.368 | 0.409 | 0.420 | 0.379 | 0.387 |
| Def 3P% | 0.354 | 0.367 | 0.353 | 0.357 | 0.355 | 0.335 |

Bold values are the current season. The 2024-25 and 2023-24 entries are reference points.

## Excess dropoffs vs historical league baseline (144 playoff team-seasons, 2014-15 to 2024-25 excl. COVID)

Top anomalies sorted by z-score magnitude. Negative dropoff = decline; positive z = unusually negative dropoff.

| Metric | Wolves dropoff | League avg dropoff | Excess | z-score |
|---|---|---|---|---|
| **Off 3PA rate** | **-0.078** | +0.001 | -0.079 | **-2.16** |
| Off eFG | -0.065 | -0.025 | -0.039 | -1.50 |
| Def OREB% | -0.044 | +0.003 | -0.047 | -1.32 |
| Def FT rate | +0.055 | +0.019 | +0.037 | +0.92 |
| Off rating | -8.22 | -3.96 | -4.27 | -0.83 |
| Off FT rate | -0.021 | +0.009 | -0.030 | -0.71 |
| Def 3P% | -0.020 | +0.005 | -0.025 | -0.71 |
| Net rating | -9.07 | -6.38 | -2.69 | -0.42 |

## The two findings worth naming

### Finding 1: the three-point attempt rate cratered

The Wolves' 3PA rate dropped from 42.0% (regular season) to 34.2% (playoffs). The dropoff is -0.078 with 95% bootstrap CI [-0.104, -0.054], which does not cross zero. The dropoff is also 2.16 standard deviations below the league norm dropoff (mean +0.001, std 0.037). The finding is statistically distinguishable from both zero and from the league norm.

**The Wolves stopped shooting threes in the playoffs.**

This is the single most diagnostic number in the Q1 cross-tab. The team that took the 9th-most threes in the league during the regular season is taking threes at a bottom-of-league rate in the playoffs.

Two plausible mechanisms:

1. **Opponent (specifically the Spurs) closing out and defending three-point shooters aggressively.** Wembanyama's rim protection lets the Spurs send perimeter defenders out hard on shooters, which the Wolves have not adjusted to.
2. **The iso-heavy halfcourt offense (per LAFI Q4 diagnosis) is generating fewer kick-out threes** because the iso doesn't bend the defense the same way pick-and-roll or motion does.

Q3 (PnR coverage decoder) is where these mechanisms get separated. Q1 establishes the empirical fact.

### Finding 2: eFG dropoff is unusual

Off eFG dropped from 55.9% to 49.5%, a -6.5 point drop. Dropoff CI [-0.087, -0.040] does not cross zero. League average dropoff is -2.5 points. Wolves are 1.5 standard deviations worse than normal eFG decay.

This is consistent with LAFI C5 (Shot Quality Decay, 83rd percentile for Wolves) but with the playoff-specific dropoff added. The shots the team takes in playoffs are not just worse than league average; they're worse than even the Wolves' regular season equivalent shots, by a wider margin than the typical playoff team.

## The non-anomalies (where the Wolves are normal)

- **Net rating dropoff** (-9.07 vs league avg -6.38) is bigger than typical but within one standard deviation. The Wolves are not having an unusually bad net-rating playoff dropoff; the underlying components are unusual in specific ways.
- **Defensive rating** held essentially flat (112.3 RS to 113.1 PO; +0.85 increase vs league avg +2.4). The defense is doing its job.
- **Defensive OREB%** improved sharply (0.263 to 0.218; a positive sign for Wolves rebounding).
- **Defensive TOV%** (turnover generation) actually dropped (forced fewer turnovers), but only modestly.

The dominant story is offensive. The defense is roughly holding serve.

## Bootstrap CIs on Wolves 2025-26 playoff metrics (12 games)

12-game playoff sample is small. CIs on the playoff-only values are wide.

| Metric | Point | 95% CI |
|---|---|---|
| Off rating | 107.4 | [101.5, 112.6] |
| Def rating | 113.1 | [107.5, 118.5] |
| Net rating | -5.8 | [-15.9, +3.7] |
| Off eFG | 0.495 | [0.472, 0.519] |
| Def eFG | 0.531 | [0.488, 0.572] |

These are CIs on the playoff value itself, not on the dropoff. For the analytical claim, the dropoff CI (below) is the more precise version.

## Bootstrap CIs on the DROPOFF (PO - RS, RS treated as fixed anchor)

The regular season is 82 games, so the RS anchor is tight enough to treat as fixed. The dropoff CI resamples playoff games with replacement and computes (PO - RS) each time. 1000 resamples, seed 42.

| Metric | RS | PO | Dropoff | 95% CI on dropoff | CI crosses zero? | League avg dropoff | z-score |
|---|---|---|---|---|---|---|---|
| **Off 3PA rate** | **0.420** | **0.342** | **-0.078** | **[-0.104, -0.054]** | **No** | +0.001 | -2.16 |
| Off eFG | 0.559 | 0.495 | -0.065 | [-0.087, -0.040] | No | -0.025 | -1.50 |
| Off rating | 115.6 | 107.4 | -8.22 | [-14.04, -2.97] | No | -3.96 | -0.82 |
| Def FT rate | 0.282 | 0.338 | +0.055 | [+0.018, +0.094] | No | +0.019 | +0.92 |
| Def OREB% | 0.263 | 0.218 | -0.044 | [-0.085, -0.002] | No | +0.003 | -1.32 |
| Off FT rate | 0.285 | 0.264 | -0.021 | [-0.047, +0.009] | Yes | +0.009 | -0.71 |
| Off TOV% | 0.143 | 0.134 | -0.010 | [-0.036, +0.019] | Yes | -0.001 | -0.50 |
| Off OREB% | 0.257 | 0.257 | +0.000 | [-0.043, +0.049] | Yes | -0.006 | +0.18 |
| Def eFG | 0.529 | 0.531 | +0.002 | [-0.041, +0.043] | Yes | +0.005 | -0.12 |
| Def rating | 112.3 | 113.1 | +0.85 | [-4.80, +6.19] | Yes | +2.43 | -0.32 |
| **Net rating** | **+3.3** | **-5.8** | **-9.07** | **[-19.22, +0.45]** | **Yes** | -6.38 | -0.42 |

**The Off 3PA rate dropoff, Off eFG dropoff, and Off rating dropoff are all statistically distinguishable from zero at p<0.05.** This is a stronger version of the headline claim. The team's offensive collapse in the playoffs is not just a directional finding driven by point estimates; the underlying shot-quality components have CIs that exclude zero entirely.

**The Net rating dropoff CI crosses zero (just barely; upper bound +0.45).** Direction is clear but magnitude is uncertain. This is consistent with the project's discipline of stating only what the sample can support.

Per the project's "honest uncertainty" principle: the offensive collapse is statistically real at the four-factors layer. The net rating uncertainty reflects normal small-sample variance, not a directional ambiguity.

## Cross-reference with LAFI

| Metric/finding | LAFI v1 (team-season) | Q1 (RS → PO dropoff) | Consistent? |
|---|---|---|---|
| Shot quality (C5) | Wolves 83rd percentile | eFG dropoff at -1.50 z; 3PA dropoff at -2.16 z | Yes, mutually reinforcing |
| Iso reliance (C3) | Wolves 90th percentile | Off rating dropoff at -0.83 z (driven by shot quality) | Yes |
| Motion death (C2) | Wolves 72nd percentile | Off OREB% unchanged (motion doesn't directly drive OREB) | Q1 doesn't directly test this; needs PBP halfcourt vs transition splits in v2 |
| Action poverty (C4) | Wolves 45th percentile (moderate) | TOV% and OREB% within norms | Consistent (the playbook isn't sparse) |

Q1's diagnostic and LAFI's structural diagnostic point at the same place from different directions: the offense's shot generation has degraded sharply in playoffs.

## What this implies for Q2 and Q3

**Q2 (Localize the Damage):** the lineup-level analysis should investigate which lineups are responsible for the 3PA rate collapse. Per the confound check on the DiVincenzo lineup (`outputs/findings/lineup_pipeline/01_divincenzo_lineup_confound_check.md`), the Dosunmu-anchored R2 starting unit had the worst net rating. Worth computing 3PA per 100 possessions per lineup specifically.

**Q3 (Mechanism):** the PnR coverage decoder should specifically test whether opposing teams (especially the Spurs) are sending hard closeouts on three-point shooters, which would directly explain the 3PA rate drop. Q3's pass-out tracking from blitzes should also surface whether the pass-outs are producing three-point looks vs other shot types.

## What Q1 does not address

Per the revised Q1 spec, halfcourt vs transition splits are deferred to v2 because they require PBP-derived possession classification. The lineup pipeline foundations (in `lib/lineups.py` and `lib/lineup_aggregation.py`) provide most of what halfcourt classification would need; integrating that into Q1 is a follow-on.

Clutch performance and first-half vs second-half splits are also deferred to a follow-on. Both require per-game time-aware aggregation. Q1 v1 captures the team-season-level story; v2 adds the temporal slices.

## Artifacts

```
outputs/tables/q1_diagnose/
  cross_tab.csv                          headline cross-tab
  wolves_dropoffs.csv                    per-Wolves-year dropoffs
  historical_league_dropoffs.csv         league baseline 2014-2024 excl COVID
  historical_dropoffs_raw.csv            raw per-team-season dropoffs
  excess_dropoffs_25_26.csv              z-scored excess dropoffs (the diagnostic table)
  bootstrap_wolves_25_26_playoffs.csv    bootstrap CIs on Wolves PO metrics
  bootstrap_dropoff_25_26.csv            bootstrap CIs on the dropoff itself (added per session feedback)
```

Re-runnable with `python -m analyses.q1_diagnose`.

## Status

Q1 v1 complete. Sets the table for Q2 (which builds on the lineup pipeline now in place) and Q3 (which builds on the action classifier infrastructure spec, with manual-coding fallback for the Wolves playoff sample).

The 3PA rate finding is the strongest single Q1 result. Worth carrying forward as a named finding in any downstream synthesis.
