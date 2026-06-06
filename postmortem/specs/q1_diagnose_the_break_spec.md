# Q1: Diagnose the Break Specification

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q1
**Status:** Specification, revised post-LAFI v1 (2026-05-17, minor)
**Position in stack:** First tactical diagnostic, foundation for the lineup-level and mechanism work that follows.

**Revision note:** Q1's four-factors and halfcourt/transition decomposition is still original and necessary. Minor cross-references to LAFI C5 added because LAFI has already done team-season-level shot quality decay work. Q1's contribution is the playoff-specific dropoff and the LAFI-orthogonal pieces (four factors, turnover handling, defensive splits).

---

## 1. The thesis

### 1.1 The question

Does the 2025-26 Wolves' playoff version meaningfully underperform the regular season version, and if so, in what specific dimensions?

This is the baseline tactical diagnostic. Before localizing the damage (Q2) or explaining the mechanism (Q3), we have to first establish that something actually broke. This section is the empirical foundation for the rest of the project. If Q1 finds the team performed roughly to expectation, the rest of the project's framing changes substantially.

### 1.2 Why this matters

Every fan, analyst, and front office person has an opinion about what's wrong. Most of those opinions are based on selective memory and the most recent game. Q1's job is to anchor the discussion in facts about what actually happened, comprehensively, before anyone (including us) starts theorizing about causes.

The four factors framework is decades old and somewhat dated, but it remains the cleanest way to decompose offensive and defensive performance into independent components. It answers the question "where, mechanically, is the team underperforming?" before anyone has to invoke style, scheme, or chemistry.

Building this analysis first also gives us calibration: if the four factors look normal but the team feels broken, the answer is in places the four factors don't capture (clutch performance, lineup-level fit, opponent-specific issues), which guides where to look next. If the four factors are anomalous in specific places, those anomalies become the spine of the rest of the analysis.

### 1.3 The expected output

By the end of Q1, we should be able to make precise, evidence-based statements like:

- "The Wolves' playoff offensive rating is X points worse than regular season, vs the league-average playoff dropoff of Y."
- "The shooting (eFG%) declined by Z, while turnovers and rebounding held roughly constant."
- "The decline is concentrated in halfcourt offense; transition offense is roughly the same."
- "Defensive performance has held up by net rating but is leaking specifically in opponent three-point rate."

This is the calibration layer. Everything else in the project assumes Q1's conclusions are correct.

**Post-LAFI cross-reference.** Shot-quality-side findings should cross-reference LAFI C5 rather than re-derive. Q1 focuses on the four-factors decomposition and the halfcourt vs transition split, which are LAFI-orthogonal. Defensive analysis is also LAFI-orthogonal (LAFI is offense-only) and remains entirely original to Q1.

---

## 2. The data structure

### 2.1 Time periods to compare

For the Wolves specifically:

- 2025-26 regular season (full season, 82 games)
- 2025-26 playoffs (Round 1 vs Denver, Round 2 vs San Antonio through current point)
- 2024-25 full season and playoffs (for year-over-year reference)
- 2023-24 full season and playoffs (the WCF run, for "best recent version" reference)

For league context:

- 2025-26 regular season league averages
- 2025-26 playoffs to date league averages (for playoff teams only)
- Historical playoff dropoff norms (10 years of data) to calibrate what's normal

### 2.2 The metric set

**Top-level metrics:**
- Net rating, offensive rating, defensive rating
- Pace
- Strength of schedule (regular season) and opponent quality (playoffs)

**The four factors (offense):**
- Effective field goal percentage (eFG%)
- Turnover rate (TOV%)
- Offensive rebounding rate (OREB%)
- Free throw rate (FT/FGA)

**The four factors (defense):**
- Opponent eFG%
- Opponent turnover rate
- Defensive rebounding rate
- Opponent free throw rate

**Halfcourt vs transition splits:**
- Halfcourt offensive rating
- Transition offensive rating
- Halfcourt frequency
- Transition frequency
- Same splits on defense

**Clutch (last 5 minutes within 5 points):**
- Clutch net rating
- Clutch offensive and defensive ratings
- Frequency of clutch situations

**Shot distribution:**
- Rim attempt rate, rim FG%
- Midrange attempt rate, midrange FG%
- Three-point attempt rate, three-point FG%
- Corner three rate, corner three FG%

**Opponent shot distribution (defensive):**
- All of the above as defensive opponent rates

### 2.3 The cross-tab structure

The output of Q1 is structured as a cross-tab:

```
                                | 25-26 Reg | 25-26 Plyf | 24-25 Plyf | 23-24 Plyf | League Reg | League Plyf
Offensive rating                |
Defensive rating                |
Pace                            |
eFG%                            |
Opp eFG%                        |
TOV%                            |
Opp TOV%                        |
OREB%                           |
DREB%                           |
FT/FGA                          |
Opp FT/FGA                      |
Halfcourt ORtg                  |
Halfcourt DRtg                  |
Transition ORtg                 |
Transition DRtg                 |
Clutch Net                      |
Rim FG%                         |
3PT%                            |
Opp 3PT%                        |
Opp 3PT Rate                    |
```

This single table is the centerpiece deliverable of Q1.

---

## 3. The math

### 3.1 Computing the metrics

Most metrics are standard. Some methodological notes:

**Offensive and defensive rating:** Points per 100 possessions. Use the standard possession formula: FGA + 0.44 * FTA - OREB + TOV.

**Four factors:** All standard. eFG% = (FGM + 0.5 * 3PM) / FGA.

**Halfcourt and transition splits:** Requires possession-level classification. A standard convention: a possession is "transition" if it begins within 7 seconds of a defensive rebound, made basket, or live-ball turnover, and the offense pushes the ball up. All other possessions are halfcourt. This classification can be done from PBP.

**Clutch:** Last 5 minutes of regulation or overtime with the score margin within 5 points. NBA.com has this directly.

**Strength-adjusted comparisons:** For playoff samples specifically, the opponent quality is much higher than regular season. So a "decline" in offensive rating from regular season to playoffs is partly a strength-of-schedule effect, not pure team underperformance. Compute opponent-adjusted versions:

```
Adjusted_ORtg = ORtg + (League_avg_DRtg - Opponent_DRtg)
```

This adjusts for the fact that playoff opponents have better defenses than the regular-season average opponent.

### 3.2 Computing the dropoff

For each metric, compute the playoff dropoff:

```
Dropoff = Playoff_value - Regular_season_value
```

Then compare to league norms:

```
Expected_dropoff = Average of (playoff_value - regular_season_value) across all playoff teams in 2025-26
Excess_dropoff = Actual_dropoff - Expected_dropoff
```

A team with an "excess dropoff" of -3 in offensive rating is declining 3 points more than the typical playoff team. That's an anomaly worth flagging.

### 3.3 Historical calibration

For some metrics, compute the historical playoff dropoff norm:

```
Historical_avg_playoff_dropoff = Average of dropoffs across 10 years of playoff teams
```

This calibrates "normal" more reliably than a one-year league average.

### 3.4 Significance

Playoff samples are small (typically 10-15 games for a team that loses in round 2). With small samples, observed dropoffs have meaningful uncertainty. For each metric, compute bootstrap confidence intervals on the playoff value, and report whether the dropoff is statistically distinguishable from zero.

Specifically: bootstrap the playoff metric by resampling games with replacement, recomputing the metric, repeating 1000 times. Take 2.5th and 97.5th percentiles as 95% CI.

A dropoff whose CI doesn't include zero is statistically meaningful. A dropoff whose CI is wide and includes zero is suggestive at best.

---

## 4. The diagnostic questions to answer

After the cross-tab is built, ask these specific questions:

### 4.1 The headline question

Has the 2025-26 Wolves' offensive rating dropped more than the typical playoff dropoff, controlling for opponent strength?

If yes: offense is the primary problem.
If no: look at defense or specific situations.

### 4.2 Where in the four factors is the decline concentrated?

eFG% dropoff is typical in playoffs (better defenses contest shots). But if the eFG% dropoff is unusually large, that's a sign the offense is generating worse looks, not just facing better defenders.

**Cross-reference with LAFI C5.** LAFI Component 5 (Shot Quality Decay) documented that the Wolves' regular-season shot diet is already at the 83rd percentile of league pickup-like. Q1's contribution on the shot side is the playoff-specific dropoff (Wolves playoff eFG% vs Wolves regular-season eFG% vs league-average playoff dropoff). This is a different question than C5 answered. C5 is team-season-grain. Q1 is regular-season-to-playoff-grain.

TOV% rising in the playoffs is unusual and a sign of pressure not being handled (the offense can't function against playoff defensive intensity).

OREB% dropping in playoffs is somewhat normal (better defensive rebounding teams) but if it's dropping more than league average, that's a sign of effort or scheme leakage.

FT rate is the cleanest sign of getting to the rim. If it's dropping, the offense isn't generating high-quality drives.

### 4.3 Halfcourt vs transition

This is the most diagnostic split for the Wolves specifically. The hypothesis: their halfcourt offense is the problem, transition is roughly fine. If the data confirms this, the structural offensive issues (covered in LAFI and Q3) are validated. If transition is also broken, the problem is more about energy/talent than design.

### 4.4 Three-point defense

The Spurs shot 11-32 from three in Game 5 (34%) but they took 32 attempts, which is high. If the Wolves are systematically allowing high three-point volume, that's the defensive scheme problem (Gobert in drop, perimeter rotations) that the eye test suggests.

### 4.5 Clutch performance

If the Wolves are getting blown out (Game 5 was a 29-point loss, Game 2 was a 38-point loss), they have few clutch possessions. The clutch sample is therefore small. But it's worth checking: in games that have been close, has the Wolves' clutch performance been good or bad?

---

## 5. The Wolves-specific deep dive

After the main diagnostic, drill into Wolves-specific patterns:

### 5.1 Game-by-game variance

Compute the Wolves' offensive rating per playoff game. Is the team consistently bad, or are they alternating good and bad games? Variance matters because it tells us whether the issue is structural (consistent) or situational (high variance, blowouts mixed with competitive games).

### 5.2 First half vs second half

Some teams break down in second halves (conditioning, adjustments). Some teams come out flat. Split Wolves playoff performance by half to see if there's a pattern.

### 5.3 Score-dependent performance

The Wolves' offensive rating when leading by 10+ vs trailing by 10+ vs close. If they fall apart when trailing, that's a sign of mental/composure issues. If they coast when leading, that's a different problem.

### 5.4 Player availability

Which playoff games featured the full intended rotation? Which were missing key players? Injuries to Edwards, DiVincenzo (long-term out), and any others should be cataloged so the analysis can distinguish "playing poorly" from "missing personnel."

---

## 6. Charts and visualizations

### 6.1 The Four Factors Chart

A radar chart or bar chart showing the Wolves' four factors (offense and defense) in regular season vs playoffs vs league playoff average. Visually surfaces where the deviations are.

### 6.2 The Dropoff Comparison

A horizontal bar chart with one row per metric, showing:
- The Wolves' playoff dropoff
- The league-average playoff dropoff
- The "excess dropoff" (Wolves vs league)

Sorted by excess dropoff magnitude. The most anomalous metrics rise to the top.

### 6.3 The Game-by-Game Trajectory

A line chart showing offensive and defensive rating per game across the 2025-26 playoffs. Highlights variance and any trends.

### 6.4 The Halfcourt Decomposition

A stacked bar showing how the team's offense breaks down (transition vs halfcourt), comparing regular season to playoffs.

---

## 7. Sequencing

This is the first tactical analysis to build. It has no dependencies beyond having the data.

1. Pull regular season and playoff stats for the Wolves and all playoff teams
2. Pull historical playoff dropoff norms
3. Compute the cross-tab
4. Compute dropoffs and excess dropoffs
5. Build charts
6. Write up findings

Estimated time: 3-5 days.

---

## 8. What I'm worried about

**Sample size in playoffs.** Round 2 series of 5-6 games gives roughly 10-12 playoff games. That's small. CIs will be wide on many metrics. Don't oversell findings.

**Opponent quality confounds.** The Wolves' Round 1 opponent (Denver) and Round 2 opponent (San Antonio) are very different teams. Aggregating across them may obscure opponent-specific patterns. Report by-series splits where sample size allows.

**Garbage time inflation.** Blowouts can inflate or deflate certain metrics in ways that don't reflect competitive basketball. Consider filtering to non-garbage-time possessions (typically: score margin within 15 points and not in the last 3 minutes of a blowout). NBA.com supports this filter.

---

## 9. Success criteria

**Minimum viable:** A clean cross-tab with confidence intervals, identifying the top 3-5 metrics where the Wolves are deviating from norm.

**Strong:** The diagnostic localizes the problem to specific areas (halfcourt offense, three-point defense, etc.) and tees up Q2 and Q3 to investigate those specific areas with focus.

**Stretch:** The diagnostic surfaces a non-obvious anomaly that nobody is currently talking about (e.g., a specific defensive leak, a specific offensive component breakdown).

---

End of specification.
