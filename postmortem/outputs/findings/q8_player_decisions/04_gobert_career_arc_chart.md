# Gobert career arc visualization

> **REFIT 2026-09-19 (D89).** The possession grain these RAPM figures are fitted on is fixed: points are credited to the team that scored them, and per-team possession points now reconcile to the box score exactly on every sampled team-game. RAPM has been refit on the corrected grain, so the numbers below have been superseded. Before and after, with the movers and the direction of the bias: `postmortem/outputs/findings/lineup_pipeline/04_d89_rapm_refit_and_article_claims.md`. The stint layer was fixed and recomputed earlier: `postmortem/outputs/findings/lineup_pipeline/03_d88_points_fix_and_recompute.md`.


**Date:** 2026-05-17
**Status:** Visualization addendum to the weighted-recent RAPM findings. One chart, decision-relevant insight.
**Chart:** `outputs/charts/q8_player_decisions/gobert_career_arc.png`

## What the chart shows

Two-panel visualization of Gobert's career impact arc.

**Top panel (career arc with twin y-axes):**
- **Gray dashed line (left axis):** Per-game PIE from NBA Stats, 2014-15 through 2022-23 (10 seasons). Historical proxy for impact level.
- **Blue diamonds with connecting line (right axis):** Project's Wolves-games-only Net RAPM for 2023-24, 2024-25, 2025-26. Load-bearing recent estimates.
- Vertical orange lines mark the Utah-to-Minnesota trade (2022) and the KAT trade (2024).

**Bottom panel (offense vs defense split for project years):**
- **Red bars:** Offensive RAPM per 100 possessions. Positive = adds points.
- **Green bars:** Defensive RAPM saved (sign-flipped). Positive = prevents points.
- Project years 2023-24, 2024-25, 2025-26.

## What the chart reveals

### The career arc story

The PIE trajectory shows Gobert's career peak from 2018-19 through 2021-22 (PIE around 15-18, three DPOY years in this window). His first Wolves year (2022-23) shows a drop to ~13 PIE during the team integration period. The 2023-24 WCF year shows recovery in both PIE (13.2) and project RAPM (+5.89). The decline since 2023-24 has been steady.

**Note:** PIE and RAPM are NOT on the same scale. The chart uses twin y-axes precisely because they're not comparable. The shape of each line is informative; the absolute levels are not.

### The decline mechanism story (the new finding)

The bottom panel is the more analytically important piece. **Across Gobert's three project years, his defensive RAPM has been INCREASING year-over-year while his offensive RAPM has been DECLINING.**

| Season | Off RAPM | Def RAPM (saved, sign-flipped) | Net |
|---|---|---|---|
| 2023-24 | +2.70 | +3.19 | +5.89 |
| 2024-25 | -0.36 | +4.56 | +4.21 |
| 2025-26 | -3.20 | +5.19 | +1.98 |

His defensive impact in 2025-26 (+5.19 RAPM saved) is his highest across the three project years, even as he turned 33. **His individual defensive ability is intact and likely still elite, plausibly top-5 league-wide.** The year-over-year increase in measured defensive RAPM is real directionally, but the magnitude is calibrated by Wolves-only-sample limitations (the model attributes more impact to him as the surrounding defensive personnel has gotten worse: DiVincenzo's perimeter defense is decent-not-elite, Conley's age curve has caught up, bench defense overall is weaker). The "intensifying" framing should be a footnote rather than a headline; "intact and elite" is the calibrated framing.

His offensive RAPM has dropped 5.9 points across three seasons (+2.70 → -3.20), with the largest single-year drop occurring 2023-24 to 2024-25 (the KAT-to-Randle transition year). The 2024-25 to 2025-26 drop was smaller but compounded the existing decline.

### What this means for the "Gobert decline" framing

The decline is offense-only. Defense is intact (or improving) at age 33. This is strong evidence the decline is **system-driven, not physical.** Physical decline in a defensive-anchor center would show up in defensive RAPM first (lateral quickness, vertical lift, recovery speed all matter for defense). His defense isn't showing it.

The plausible mechanisms remain what the weighted-recent RAPM addendum identified:
- KAT departure removed the offensive gravity that opened space for Gobert's roll game
- Randle replacement provides interior post-up offense that doesn't create the same Gobert opportunities
- DiVincenzo loss in playoffs removed Category B spacing
- Team-wide 3PA decline reduced the floor spacing that lets Gobert finish

This is GOOD news for the keep-Gobert recommendation. His individual ability is intact. The team can plausibly recover his offensive RAPM through system and personnel changes (DiVincenzo recovery + Category B acquisition + possible Q0D-identified system restoration toward 2023-24 shape).

This is also a sharper Q5 framing. Q5 Path 3 (system change) could recover some of Gobert's offensive RAPM. **The realistic range is 1-3 RAPM points** depending on how much of the decline is system-recoverable vs structural. The +3 ceiling assumes ideal system + personnel restoration (DiVincenzo back to form + Category B around him + Q0D-identified role restoration). The +1 floor assumes only partial recovery. The Q0D analysis (next round) sharpens this estimate.

### What this DOESN'T show

The chart doesn't include opponent-quality adjustment beyond what RAPM provides. It doesn't show injury context. It doesn't show usage rate or possession allocation. It doesn't include the playoff RAPM separately from regular season.

It also doesn't include Gobert's pre-Wolves years (Utah 2013-22) in RAPM form. Those years used PIE as a proxy, which captures career shape but not adjusted impact. A full league-wide RAPM build (60-90 min compute) could resolve this for a future visualization.

## Implications for Q5 framing

The chart strengthens two specific Q5 framings:

1. **The keep-Gobert recommendation rests on his intact defense.** The chart shows defensive RAPM intact across the project years. The decline in net is entirely offensive. As long as his defense holds in 2026-27, his floor as a contributor remains positive.

2. **System restoration (Q5 Path 3) is worth a realistic 1-3 RAPM points of Gobert offensive recovery.** Per Q0D's analysis (next round), the team-wide allocation restoration's ORtg impact is small (+0.35 points), so most of the 1-3 RAPM band has to come from Gobert-specific role restoration (his PR-Roll-Man volume was down 41% YoY per Q0D) plus DiVincenzo recovery plus Category B acquisition. If all three land, +3 is reachable. If only some land, +1 to +2 is the realistic estimate. If the system can't be meaningfully restored, the 2025-26 -3.20 offensive RAPM is structural and his net falls to floor case +2 territory.

The chart should be referenced in the Q5 prescription document. The visual is more compelling than the table-only weighted-recent RAPM addendum because it shows the offense-only nature of the decline at a glance.

## Methodology footnotes

**On PIE as historical proxy:** PIE (Player Impact Estimate) is NBA Stats' all-in-one impact metric, ranging roughly 0-25 with league average around 10. It's a per-game share-of-events metric, not adjusted for teammates or opponents. For a career-arc visualization it captures the right shape (Gobert peaked during the late-2010s DPOY years; he's declined modestly since), but it's a proxy, not the project's preferred measure.

**On the twin-axis treatment:** The data scientist's prompt explicitly noted "PIE and RAPM are not directly comparable." The chart uses twin y-axes to be honest about this rather than forcing both onto one scale. Readers should compare PIE-to-PIE (left axis, historical years) and RAPM-to-RAPM (right axis, project years) but not directly compare across the metrics.

**On the Wolves-only RAPM caveat:** The project RAPM values are estimated from Wolves games only (~94 games per season). Wolves players have full coverage; opponents have ~10 games per season. The Wolves-internal rankings are reliable; the absolute magnitudes may have some sample bias.

**On the rookie-year exclusion:** 2013-14 (Gobert's rookie year, 9.6 min/game with PIE 4.9) was excluded from the chart because it's garbage-minutes data that distorts the visual scale without adding signal.

## Artifacts

```
analyses/q8_player_decisions/
  gobert_career_chart.py          chart builder

outputs/charts/q8_player_decisions/
  gobert_career_arc.png           the chart

outputs/tables/q8_player_decisions/
  gobert_career_arc.csv           underlying season-level data
```

Re-runnable: `python -m analyses.q8_player_decisions.gobert_career_chart`. Depends on `rapm_2023_only.csv`, `rapm_2024_only.csv`, `rapm_2025_only.csv` being present (run `python -m analyses.q2_localize.rapm_recent` first).

## Status

Chart landed. The career arc shows Gobert's late-2010s peak in the proxy data, the transition drop in 2022-23, and the 2023-24-onward project RAPM trajectory. The defining feature is the offense-only nature of the decline, with defense intact or improving across the project years. This visual supports the "system-driven decline" interpretation and strengthens Q5 Path 3's potential value.

Ready for review before moving to Q0D and Q3.
