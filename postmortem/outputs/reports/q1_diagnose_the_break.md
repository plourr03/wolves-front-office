# Q1: Diagnose the Break

> **EXPOSED, NOT YET RECOMPUTED (D88).** The possession-grain splits below (halfcourt, transition, clutch) attribute points by the possession's offensive team, which misattributes about 3.4% of points, mirrored between the two teams. The team-level box-score ratings in this report are unaffected. Detail: `postmortem/outputs/findings/lineup_pipeline/03_d88_points_fix_and_recompute.md`.

**Status:** v2. Team-level diagnostic plus PBP-derived halfcourt-vs-transition, clutch, and shot-zone splits. Some pieces still pending: opponent-strength adjusted ORtg, league-wide comparators for the PBP splits (Wolves-only for now).

**Sample:** 2025-26 Wolves through 11 playoff games (5-game first round vs Denver, 6 games into round 2 vs San Antonio, currently down 3-2). Regular-season comparison uses all 82 games. League historical norms use all playoff team-seasons 2014-15 through 2024-25.

---

## The headline

The 25-26 Wolves' net-rating drop from regular season to playoffs is roughly in line with what playoff teams typically see (down 6.8 points, vs a 10-year historical norm of down 6.3). The overall story is normal. The composition is not.

**The break is entirely on offense.** Offensive rating fell 7.9 points (113.8 to 105.8). The 10-year historical norm for a playoff team is a 3.8-point drop. The Wolves are 4.2 points worse than typical playoff regression.

**The defense is not the problem.** Defensive rating actually improved slightly in the playoffs (110.5 to 109.4). Playoff defenses typically get 2.6 points worse against the elevated playoff competition, so the Wolves' defense is performing about 3.7 points better than the league historical norm holds. Opp eFG% held, opp 3PT% dropped, defensive rebounding spiked. Nothing in the four factors says the defense has broken.

**Within the offensive collapse, the largest anomaly is three-point volume.** The Wolves' 3PA rate fell from 42.0% of FGA in the regular season to 34.4% in the playoffs, a 7.6-point drop. The historical norm is roughly flat (+0.4 points). This is the most unusual deviation in the entire cross-tab. They are choosing not to shoot threes against playoff defenses, or are not getting the looks. Three-point shooting accuracy also fell (37.0% to 33.5%), but the volume change is the larger story.

**The other anomalies, in order of magnitude:**
- Opp FT/FGA spiked 5.8 percentage points (28.2% to 34.0%). The Wolves are fouling far more in the playoffs than they did in the regular season. The historical norm is +1.9.
- DREB% jumped 5.5 points (73.7% to 79.2%). Positive direction. The Wolves are cleaning the defensive glass at a much higher rate than the historical playoff norm.
- eFG% fell 5.8 points. The historical norm is 2.4. The shot-quality decline is real and not just a function of fewer threes.

**Uncertainty caveat.** All playoff numbers come from an 11-game sample. The bootstrap 95% CI on the playoff offensive rating is [100.9, 110.7]. The 95% CI on net rating is [-12.5, +5.9]. Several of the "anomaly" findings flip sign at the edge of those bands. The dropoff in 3PA rate is large enough that it likely survives any reasonable sample expansion. The opp-FT/FGA spike does not.

## The cross-tab

The full table lives at `outputs/tables/q1_crosstab.md`. The most relevant rows:

| Metric | 25-26 RS | 25-26 PO | 25-26 PO 95% CI | MIN dropoff | League PO avg dropoff | Historical norm | Excess |
|---|---|---|---|---|---|---|---|
| Off rating | 113.75 | 105.81 | [100.89, 110.70] | -7.94 | -6.32 | -3.75 | **-4.19** |
| eFG% | 55.9% | 50.1% | [47.8%, 52.6%] | -5.8 pp | -3.1 pp | -2.4 pp | -3.4 pp |
| 3PA rate | 42.0% | 34.4% | [31.8%, 37.1%] | -7.6 pp | -1.1 pp | +0.4 pp | **-7.9 pp** |
| 3PT% | 37.0% | 33.5% | [30.3%, 36.9%] | -3.5 pp | -1.8 pp | -1.8 pp | -1.7 pp |
| Def rating | 110.52 | 109.37 | [104.40, 114.09] | -1.15 | -0.65 | +2.57 | **-3.73** |
| DREB% | 73.7% | 79.2% | [75.5%, 83.2%] | +5.5 pp | -1.1 pp | -0.3 pp | **+5.8 pp** |
| Opp FT/FGA | 28.2% | 34.0% | [30.0%, 37.8%] | +5.8 pp | +2.9 pp | +1.9 pp | **+3.9 pp** |
| Net rating | 3.23 | -3.56 | [-12.49, +5.86] | -6.79 | -5.68 | -6.32 | -0.47 |

(Bold rows are the metrics with the largest excess dropoff vs the historical norm.)

## What this implies for Q2 and Q3

The four-factor diagnostic narrows the next layers of work:

1. The break is on offense. Q2's lineup analysis should foreground offensive lineups, not net rating overall. Defensive lineups can be evaluated on the side but are not the headline question.
2. The 3PA rate collapse is the single most distinctive anomaly. Q3 should investigate why. Is it shot selection (the offense is hunting twos rather than threes), is it opponent coverage (defenses are taking away the kick-out three), or is it personnel (the rotation has shifted toward worse shooters)? PBP-level work in Q3 will distinguish these.
3. eFG% dropped more than 3PT% would predict alone. So shot quality at the rim and in the midrange is also degraded. The expected-eFG model in Q3a should quantify the shot-quality drop separately from the shot-making drop.
4. Opp FT/FGA spiking is worth a small-scale check before assuming it's signal. With 11 games, a couple of foul-heavy games can move the number meaningfully. Worth pulling the per-game opp FT rate to see if it's concentrated in one or two games.
5. DREB% surge is real (the CI does not include the dropoff norm) but its impact on net rating is modest. Flagging it as a finding but not the headline.

## v2 findings: PBP-derived splits

Built from possession reconstruction of all 93 Wolves 25-26 games (82 RS + 11 PO), 19,764 reconstructed possessions. Garbage-time filter applied (CLAUDE.md default: 4th period or later, last 3 minutes, |margin| > 15). All numbers below are non-garbage-time.

Possession reconstruction has a documented ~2% imprecision from edge cases (period-boundary shots, team rebounds, flagrant/technical FT handling). The halfcourt-vs-transition **ratios** and shot-zone **shares** are not materially affected.

### Halfcourt vs transition: the surprising finding

| | Wolves 25-26 RS | Wolves 25-26 PO |
|---|---|---|
| **Halfcourt ORtg** | 95.0 | 96.9 |
| Halfcourt eFG% | 50.5% | 46.0% |
| Halfcourt share of possessions | 88.1% | 89.1% |
| **Transition ORtg** | 176.8 | 163.3 |
| Transition eFG% | 82.5% | 77.0% |
| Transition share of possessions | 11.9% | 10.9% |

The headline diagnostic moves the needle in an unexpected direction. **The halfcourt offense did not collapse in the playoffs.** Halfcourt ORtg actually rose 1.9 points (95.0 to 96.9). Halfcourt eFG% dropped 4.5 percentage points, but FT rate compensated.

**Where the offense actually regressed: transition.** Transition ORtg fell 13.5 points (176.8 to 163.3). Transition eFG% fell 5.5 points. Transition was the Wolves' weapon in the RS (177 ORtg is elite) and it became merely good in the playoffs (163 is still well above league average but not the runaway it had been).

This complicates the "halfcourt is broken in playoffs" hypothesis the spec started with. The eFG% in halfcourt did get worse, which lines up with the shot-zone shift documented below, but the net effect on halfcourt ORtg was muted by improved FT generation.

(Caveat: transition is defined as possession duration ≤ 7 seconds with ≥ 1 FGA. The classification is a v1 heuristic. Shifting the threshold to 6 or 8 seconds would change the magnitudes; the directional finding is robust.)

### Defense splits

| | Wolves 25-26 RS | Wolves 25-26 PO |
|---|---|---|
| **Halfcourt DRtg** | 91.4 | 98.2 |
| Halfcourt opp eFG% | 46.9% | 47.1% |
| **Transition DRtg** | 175.9 | 165.2 |
| Transition opp eFG% | 82.3% | 75.2% |

Halfcourt defense got 6.8 points worse in playoffs (91.4 to 98.2). Opp eFG% in halfcourt is identical (46.9% to 47.1%), so the extra points are not coming from worse shot quality allowed. They're coming from the FT spike documented in v1 (Opp FT/FGA jumped +5.8 pp). Wolves are fouling more in halfcourt defense in playoffs.

Transition defense improved 10.7 points (175.9 to 165.2). Lower opp eFG% in transition (82.3% to 75.2%) drives it.

Net defense across both splits is roughly flat, consistent with the v1 finding that overall DRtg held up.

### Shot zone shift on offense

| Zone | 25-26 RS share | 25-26 PO share | RS eFG | PO eFG |
|---|---|---|---|---|
| Rim | 30.8% | 32.8% | 68.1% | 62.3% |
| Midrange | 27.8% | 32.8% | 43.7% | 37.7% |
| Corner 3 | 10.2% | 9.3% | 39.6% (×1.5 = eFG 59.4%) | 45.7% (eFG 68.6%) |
| Above-break 3 | 31.2% | 25.1% | 36.3% (eFG 54.5%) | 29.0% (eFG 43.5%) |

(eFG% for two-point zones equals FG%; for three-point zones it's FG% × 1.5.)

The shot-distribution shift is the granular version of v1's "3PA rate dropped" finding:

- Above-break 3PA rate collapsed (31.2% → 25.1%). They're not generating these looks. When they do, they make them at 29.0%, far below their 36.3% RS pace.
- Midrange rate surged (27.8% → 32.8%). The offense is settling for worse shots.
- Rim attempt rate rose slightly but rim FG% dropped 5.8 pp (68.1% → 62.3%). Spurs' interior defense (Wembanyama as primary) is the obvious cause for the playoff drop; the broader RS-vs-playoff comparison would need league average rim FG% to contextualize.
- Corner 3 rate is roughly flat; corner 3 efficiency actually improved (39.6% → 45.7%). The corners are working. The above-break attempts are the problem.

### Clutch performance

| | Possessions | ORtg | DRtg | Net |
|---|---|---|---|---|
| 25-26 RS clutch | 216 off / 211 def | 98.6 | 100.5 | -1.9 |
| 25-26 PO clutch | 28 off / 26 def | 121.4 | 96.2 | +25.2 |

The Wolves were a below-break-even clutch team in the regular season (-1.9 net rating in 216 possessions). In the playoffs, they have been crushing clutch (+25.2), but the sample is 28 possessions. The pattern is consistent with the playoff series record so far: Wolves are 6-5 in playoffs but most losses have been blowouts (Game 2 lost by 38, Game 5 lost by 29). When games are close, they win.

This is important context for the v1 finding that the offense collapse in playoffs is real but the dropoff is similar to historical norms in net-rating terms. The Wolves are not losing close playoff games; they are losing blowouts. The diagnosis should focus on what's happening when the game gets out of hand, not the late-game decision-making.

## Open items still pending

- **League-wide comparators for the PBP splits.** Currently Wolves-only. Need to pull 30-team RS PBP for league averages on halfcourt ORtg, transition ORtg, and shot-zone shares. Several million PBP rows; doable in one query block.
- **Opponent-strength adjustment.** The Wolves' two playoff opponents (Denver, San Antonio) are top-tier teams. A 7.9-point ORtg drop against the best two defenses in the league is partly strength-of-schedule. The spec's adjusted-ORtg formula will reduce the apparent drop. Worth running once league PBP is pulled.
- **Possession reconstruction precision.** Known ~2% point drift from period boundaries, flagrant/technical FT handling, and team rebounds. Acceptable for the splits we report; would need tightening for player-level on/off (Q2).

## Methodology

- **Data source.** `nba.nba_games` (raw box scores) for 2014-15 through 2025-26, RS and playoffs. Self-joined on `game_id` to attach each team-game to its opponent's team-game.
- **Possessions.** Computed via the Oliver formula (`FGA + 0.44*FTA − OREB + TOV`), averaged across the two teams in each game. Independent of the `nba_team_advanced_stats` table, which is missing the 25-26 playoff backfill at the time of writing.
- **Ratings.** Season totals divided by season totals. `ORtg = 100 * SUM(pts) / SUM(poss)`. `DRtg = 100 * SUM(opp_pts) / SUM(poss)`.
- **Four factors.** Standard. `eFG% = (FGM + 0.5*3PM) / FGA`. `TOV% = TOV / (FGA + 0.44*FTA + TOV)`. `OREB% = OREB / (OREB + Opp_DREB)`. `FT/FGA = FTA / FGA`.
- **Bootstrap CIs.** Resample team-games with replacement (n_resamples=1000), recompute the aggregate metric from raw totals on each resample, take the 2.5th and 97.5th percentile of the resampled distribution.
- **League historical dropoff.** Mean across all team-seasons 2014-15 through 2024-25 of (playoff value minus regular-season value), for each metric. Teams included only if they have both an RS and a PO row.

## Build and data inputs

- Code: `analyses/q1/{data,metrics,build,charts}.py`. Re-runnable with `python -m analyses.q1.build` and `python -m analyses.q1.charts`.
- Tables: `outputs/tables/q1_crosstab.{md,parquet}`, `outputs/tables/q1_team_season_agg.parquet`.
- Charts: `outputs/charts/q1_{four_factors_radar,dropoff_comparison,game_trajectory,three_point_decline}.png`.
