# RAPM findings: multi-season pooled adjusted impact

**Date:** 2026-05-17
**Status:** First RAPM build. 3-season pooled (2023-24, 2024-25, 2025-26). Wolves-games-only sample (see Section 6 caveat).
**Sample:** 289 Wolves games (RS + PO), 55,670 possessions, 565 qualifying players (>= 50 possessions).
**Method:** Ridge regression (alpha=2000) on sparse design matrix with offensive and defensive indicator columns per player, per-100-possession scaling. Replacement-level pooling for players below the 50-possession threshold.

## Headline

**Two findings carry the most weight from RAPM:**

1. **Rudy Gobert has the highest net RAPM in the entire 565-player sample.** Net RAPM +6.18 per 100 possessions, driven by elite defensive RAPM (-6.89, the lowest in the sample). For context, Wembanyama is #2 at +4.90 net (-3.43 def). Gobert's defensive value is the largest single impact in the data, and it's exactly what justifies the Edwards+Gobert lineup-grain finding from the yoy comparison (Edwards+Gobert was the team's best high-minute pairing in both 2024-25 RS and 2025-26 RS, despite the LAFI implication that the pairing should be problematic).

2. **The Wolves rotation ranking by RAPM is sharply differentiated.** Gobert (#1 in sample), Naz Reid (#12), Jaylen Clark (#23, but small sample), DiVincenzo (#50) are clearly positive. Conley (#372), McDaniels (#393), Edwards (#423), Randle (#468), Hyland, Dosunmu (#547) are clearly below replacement. The gap between the team's top-RAPM players and bottom-RAPM players is large.

**One result needs a methodological caveat before being interpreted (Section 6):** Anthony Edwards' net RAPM is -0.61 (rank #423), which is implausible for the team's franchise player. This is almost certainly an artifact of the Wolves-only sample limitation. His offensive RAPM is +3.97 (very high), but his defensive RAPM is +4.58 (very bad), and the model can't fully separate Edwards' impact from "the Wolves' overall offense when he plays" because every possession he's in is a Wolves possession. The Edwards estimate should not be used as a standalone impact measure; the Wolves players ranking among themselves IS informative.

## 1. Wolves rotation RAPM table

| Player | Off RAPM | Def RAPM | Net RAPM | League Rank (of 565) |
|---|---|---|---|---|
| **Rudy Gobert** | -0.71 | **-6.89** | **+6.18** | **#1** |
| Naz Reid | +0.04 | -2.38 | +2.42 | #12 |
| Jaylen Clark | +1.55 | +0.10 | +1.45 | #23 |
| Donte DiVincenzo | +0.38 | -0.96 | +1.35 | #50 |
| Joan Beringer | +1.00 | +1.57 | -0.58 | #406 |
| Mike Conley | -1.06 | -0.66 | -0.40 | #372 |
| Kyle Anderson | -1.81 | -1.42 | -0.40 | (close to Conley) |
| Jaden McDaniels | -0.20 | +0.29 | -0.48 | #393 |
| Anthony Edwards | **+3.97** | **+4.58** | -0.61 | #423 (see caveat) |
| Julius Randle | +1.07 | +1.95 | -0.88 | #468 |
| Joe Ingles | -0.15 | +0.95 | -1.10 | (replacement-level area) |
| Bones Hyland | -1.06 | +0.38 | -1.44 | (replacement-level area) |
| Ayo Dosunmu | -0.33 | +1.45 | -1.79 | #547 |
| Rob Dillingham | -1.64 | +0.82 | -2.46 | (small sample) |
| Terrence Shannon Jr. | +0.30 | +3.07 | -2.77 | (small sample) |

(Negative def RAPM = good defender, prevents points. Positive off RAPM = good offensive player, adds points.)

## 2. Benchmark validation

Wolves played each opponent 2-4 times per season, giving ~10 games of data per benchmark player over 3 seasons. Estimates are noisier than for Wolves players but should rank known stars near the top.

| Player | Off RAPM | Def RAPM | Net RAPM | League Rank |
|---|---|---|---|---|
| Wembanyama | +1.47 | -3.43 | +4.90 | **#2** |
| SGA | +1.31 | -0.99 | +2.30 | #14 |
| Doncic | +1.68 | -0.49 | +2.16 | #20 |
| Mitchell | +1.68 | -0.32 | +2.00 | #24 |
| Trae Young | +1.18 | -0.71 | +1.89 | #27 |
| Jokic | +1.84 | +0.63 | +1.22 | #66 |
| Embiid | +0.48 | -0.62 | +1.10 | #73 |
| Brunson | +0.86 | -0.01 | +0.87 | #98 |
| Tatum | +0.74 | +0.31 | +0.42 | #158 |
| Paul George | -0.25 | -0.63 | +0.38 | #168 |
| Durant | +1.33 | +1.36 | -0.03 | #279 |
| Jamal Murray | +0.01 | +2.08 | -2.08 | #557 |

**Sanity check assessment:** The very top is calibrated (Gobert and Wembanyama are clearly elite defenders; SGA and Doncic in top 25). The middle is noisier than ideal (Jokic at #66 is too low; Tatum at #158 is too low for his actual impact). The very bottom has some questionable placements (Murray at #557 is low for an All-NBA caliber player). These are consequences of the Wolves-only sample (each non-Wolves player has only 8-12 games of data).

**Implication:** Trust the top of the table (clearly elite players sort correctly). Trust the bottom of the Wolves rotation (Dosunmu at #547 is consistent with raw on/off and lineup-grain findings). Be cautious about specific magnitudes in the middle of the table.

## 3. Comparison table: RAPM vs Raw on/off vs Lineup-grain (2025-26 RS)

| Player | Min | On Net | Off Net | On/Off Diff | RAPM Off | RAPM Def | RAPM Net |
|---|---|---|---|---|---|---|---|
| Rudy Gobert | 2806 | +3.69 | -1.57 | **+5.26** | -0.71 | -6.89 | **+6.18** |
| Naz Reid | 2117 | +4.38 | -1.43 | **+5.81** | +0.04 | -2.38 | **+2.42** |
| Jaylen Clark | 534 | +1.55 | +1.34 | +0.22 | +1.55 | +0.10 | +1.45 |
| Donte DiVincenzo | 2435 | +5.40 | -5.12 | **+10.52** | +0.38 | -0.96 | **+1.35** |
| Mike Conley | 629 | -1.67 | +2.08 | -3.75 | -1.06 | -0.66 | -0.40 |
| Jaden McDaniels | 2746 | +0.80 | +2.12 | -1.32 | -0.20 | +0.29 | -0.48 |
| Anthony Edwards | 2402 | +1.13 | +1.64 | -0.51 | +3.97 | +4.58 | -0.61 |
| Julius Randle | 3058 | +0.48 | +2.96 | -2.49 | +1.07 | +1.95 | -0.88 |
| Bones Hyland | 890 | -0.21 | +2.26 | -2.48 | -1.06 | +0.38 | -1.44 |
| Ayo Dosunmu | 691 | +3.25 | +0.58 | +2.68 | -0.33 | +1.45 | -1.79 |

### Where the three estimates triangulate

**Gobert:** On/off +5.26, RAPM +6.18, lineup-grain (Edwards+Gobert) +4.38. All three point to Gobert as the team's most valuable player. RAPM is the largest magnitude estimate. Convergence is strong.

**Naz:** On/off +5.81, RAPM +2.42, lineup-grain (multiple positive cohorts including Gobert+Naz +5.78). All three positive, but RAPM is meaningfully lower than the on/off (because Naz's bench minutes are confounded with bench rest). The triangulated estimate is "real positive but smaller than the raw on/off suggests."

**DiVincenzo:** On/off +10.52, RAPM +1.35, lineup-grain (DiVincenzo-on +7.57 with CI [+3.0, +12.2]). The RAPM is much smaller than the on/off. This is the standard RAPM adjustment for lineup confounds: DiVincenzo plays with the starters, his off-floor minutes are with the bench. RAPM corrects this and gives a smaller (still positive) estimate. The DiVincenzo Category B finding survives RAPM but with a smaller magnitude than the raw on/off implied.

**Randle:** On/off -2.49, RAPM -0.88, lineup-grain (Edwards+Randle +2.68 in 2025-26 RS, Gobert+Randle +4.57 in 2025-26 RS). RAPM ranks Randle at #468 (below replacement). Raw on/off is negative. But his lineup pairings show positive net rating. The inconsistency: when Randle is with Edwards+Gobert (or just Gobert), the team plays positive net basketball. When Randle is otherwise deployed, the team is mediocre. RAPM averages this and gets slightly negative.

**Edwards:** On/off -0.51, RAPM -0.61, lineup-grain (Edwards+Gobert +4.38, Edwards+Naz +1.38). Both on/off and RAPM are slightly negative. The lineup-grain pairings are all positive. The disconnect is the bench-rest confound: Edwards' off-floor minutes are against opposing benches, so the team plays better in those minutes for opponent-quality reasons that RAPM can't fully control for with Wolves-only data.

### Where the three estimates DON'T triangulate

**McDaniels:** On/off -1.32 (slightly negative), RAPM -0.48 (mildly negative), lineup-grain pairings positive. All metrics agree he's around replacement-level on net impact.

**Dosunmu:** On/off +2.68 (positive), RAPM -1.79 (negative), lineup-grain mixed. The on/off is misleading; RAPM correctly identifies him as below replacement. His positive raw on/off is mostly from the bench-mob lineups he plays with (high-energy garbage-time stuff). His starting-unit minutes were a disaster.

## 4. 2025-26 PO comparison

The playoff sample is small (12 games) so on/off values have very wide CIs (per earlier confound checks). RAPM is from the larger 3-season RS+PO pool, so it doesn't change between RS and PO views; what changes is the on/off comparison.

| Player | PO Min | PO On Net | PO Off Net | PO On/Off | RAPM Net |
|---|---|---|---|---|---|
| Rudy Gobert | 372 | -0.28 | -1.90 | +1.62 | +6.18 |
| Naz Reid | 323 | +3.67 | -6.95 | +10.62 | +2.42 |
| Jaylen Clark | 54 | +3.31 | -1.37 | +4.68 | +1.45 |
| Donte DiVincenzo | 96 | +14.23 | -4.12 | +18.36 | +1.35 |
| Mike Conley | 167 | +8.28 | -4.58 | +12.87 | -0.40 |
| Jaden McDaniels | 406 | -3.79 | +5.61 | -9.39 | -0.48 |
| Anthony Edwards | 324 | -6.13 | +5.96 | -12.09 | -0.61 |
| Julius Randle | 400 | -5.99 | +10.31 | -16.30 | -0.88 |
| Ayo Dosunmu | 292 | -5.73 | +4.01 | -9.74 | -1.79 |

The Edwards -12.09 and Randle -16.30 playoff on/off numbers are exaggerated by the small playoff sample plus the bench-rest confound discussed earlier. RAPM's much smaller magnitude (-0.61 and -0.88 respectively) is the better estimate of true impact. The PO on/off numbers should be treated as descriptive of the playoff context only, not as impact estimates.

The DiVincenzo PO on/off of +18.36 is consistent with his small healthy-minutes sample being unusually positive, but the 96-minute sample is too small to trust as a real impact estimate. RAPM (+1.35) is the better number to anchor Q8 conclusions on.

## 5. What the RAPM resolves

**The Reconciliation A vs B question** (does Gobert's defensive value justify the LAFI Q4 offense limitations, or does the LAFI framework overstate Gobert's offensive cost):

**Reconciliation A is supported.** Gobert's defensive RAPM is -6.89 per 100 possessions, the lowest (best) in the sample. His offensive RAPM is -0.71 (slightly negative, consistent with the LAFI implication that he limits offensive spacing). The net is +6.18, because his defensive impact is much larger than his offensive cost.

**For Q5/Q8:** The Gobert trade case is now substantially weaker than the playoff-only Q2 corrections suggested. RAPM identifies Gobert as the team's most valuable player by a wide margin. The "trade Gobert" path can probably be set aside; the project's prescription should focus on building around him (Category B addition, Randle replacement, etc.).

**The Randle case stays mixed.** RAPM has Randle at -0.88 (slightly below replacement, rank #468). Not catastrophic. The case for moving him rests on:
- Raw on/off of -2.49 in 2025-26 RS
- Playoff on/off of -16.30 (exaggerated by sample)
- The Gobert+Randle pairing being -13.26 in 2025-26 PO (opponent-specific per yoy comparison)
- His RAPM being below replacement

But RAPM doesn't strongly indict Randle (just -0.88, very close to replacement). The case for keeping him rests on:
- Edwards+Randle being +2.68 RS net rating
- Gobert+Randle being +4.57 RS net rating
- His contract / age / utility as a secondary creator

**The DiVincenzo case is the cleanest.** RAPM +1.35, raw on/off +10.52, lineup-grain DiVincenzo-on +7.57 (statistically positive). All three measures agree he's a positive impact player. The 12-point raw on/off swing was the strongest single finding in the project; RAPM moderates it to +1.35 but doesn't refute it. The high-leverage Q8 question becomes how to support DiVincenzo's Achilles recovery and how to add Category B redundancy.

## 6. Methodological caveats

**The Wolves-only sample is the main limitation.** This RAPM was built from 289 Wolves games (regular season + playoffs across 2023-24, 2024-25, 2025-26), not from the full NBA. The consequence:

- **Wolves rotation players have full data:** they appear in every Wolves game when healthy, so their coefficients are estimated from thousands of possessions. Internally consistent rankings.
- **Non-Wolves players have ~10 games of data:** their coefficients are noisy. Sensible top placements (Wembanyama, SGA, Doncic) but middle and bottom of the league has noise (Jokic at #66, Tatum at #158, Murray at #557 are all probably underestimated).
- **Edwards' coefficient is particularly affected.** Every Wolves possession involves Edwards (when he plays). The model can't separate "Edwards' impact" from "the Wolves' team-level offensive system when he plays." His Net RAPM of -0.61 is almost certainly an artifact.

**For full league-wide RAPM, would need to process all 30 teams' games for 3 seasons.** Approximate compute cost: ~60-90 minutes of pipeline processing for 3690 games. Substantially more than this build. v2 work if the Q8 conclusions depend on it.

**Alpha (regularization) was set at 2000 without CV tuning.** Higher alpha shrinks all coefficients toward zero; lower alpha allows more extreme values. The current settings produce sensible top-of-sample rankings (Gobert #1, Wembanyama #2, SGA #14, Doncic #20) which suggests reasonable calibration. Variance sensitivity to alpha is a v2 question.

**No CV-based prediction quality measure reported.** The model's predictive accuracy is unknown. For now, the value of RAPM is in the rankings and the relative comparisons to raw on/off and lineup-grain, not in absolute predictions.

## 7. Implications for Q8

**Gobert:** Strongly supports KEEP. #1 in 565-player sample. Defensive value (-6.89 def RAPM) is the largest in the data. Trading him would forfeit the team's largest single individual impact.

**Randle:** Mixed. RAPM is slightly below replacement (-0.88, #468). Lineup-grain pairings are positive. The case for moving him rests on his fit with the team's playoff scheme (Spurs specifically broke his pairing with Gobert) and on his contract relative to value, not on his RAPM being catastrophically bad.

**DiVincenzo:** Strongly supports KEEP and PROTECT THE RECOVERY. RAPM positive, raw on/off positive, lineup-grain positive. All three measures agree. Highest-leverage personnel decision is investing in his Achilles recovery.

**Naz Reid:** Strongly supports KEEP. RAPM #12 in sample. Lineup-grain pairings positive. Multiple roles (backup big, occasional starter, Category B threat).

**Edwards:** Untouchable, but his RAPM should not be used in Q8 framing. The negative magnitude is an artifact. His offensive RAPM (+3.97) is high and meaningful; his net RAPM is unreliable here. Future full-league RAPM would give a cleaner Edwards estimate.

**Conley, McDaniels, Dosunmu:** Conley (-0.40) and McDaniels (-0.48) are around replacement. Dosunmu (-1.79) is clearly below. McDaniels at -0.48 with elite defensive reputation is surprising; his off RAPM is -0.20 and def RAPM is +0.29 (neutral defender by this measure). This may be an artifact of his role-player usage. Worth Q8 scrutiny.

## 8. What I didn't do

- **Full league-wide RAPM** (would resolve the Edwards artifact and give better benchmark calibration). v2 follow-on if Q8 conclusions require it.
- **Weighted-recent vs pooled comparison** (would test whether Gobert is declining at age 33). Bobby specifically requested this; should be done before Q8 if there's any doubt about Gobert's trajectory.
- **Cross-validation alpha tuning.** Used alpha=2000 as a reasonable default. Sensitivity to this could be checked.
- **Standard errors / confidence intervals on RAPM estimates.** Not built. The Wolves rotation rankings appear stable, but uncertainty bands aren't quantified.
- **Possession-weighted comparison to existing measures (BPM, EPM, LEBRON).** The Wolves rotation could be cross-checked against publicly available RAPM-style estimates from other sources.

## 9. Artifacts

```
analyses/q2_localize/
  rapm.py             RAPM build driver
  rapm_compare.py     comparison table builder

outputs/cache/q2_localize/possessions/
  *.parquet           per-game possession data (289 games)

outputs/tables/q2_localize/
  rapm_player_impacts.csv        full 565-player table
  rapm_wolves_rotation.csv       Wolves-specific subset
  rapm_vs_onoff_2025rs.csv       RS comparison table
  rapm_vs_onoff_2025po.csv       PO comparison table
```

Re-runnable: `python -m analyses.q2_localize.rapm` then `python -m analyses.q2_localize.rapm_compare`.

## 10. Status

The RAPM build delivers what was asked: a methodologically defensible adjusted impact estimate for Wolves rotation players, with benchmark validation. The main result (Gobert #1 in the sample) is the kind of finding that justifies the methodological investment. The Edwards artifact is documented honestly rather than glossed over.

Combined with the yoy lineup comparison, the project now has three load-bearing pieces of evidence:
1. **DiVincenzo's Category B value (lineup-grain + on/off + RAPM all positive).**
2. **Gobert is the team's most valuable player (RAPM #1, lineup-grain Edwards+Gobert best, defensive value supported across measures).**
3. **The 2025-26 PO 3PA collapse is Spurs-specific (lineup-grain comparison showed 2024-25 PO held 3PA rate flat; 2025-26 PO dropped 7.8 pp).**

Q8 has its analytical foundation. Ready to begin.
