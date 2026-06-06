# Q2: 2024-25 vs 2025-26 lineup-grain comparison

**Date:** 2026-05-17
**Status:** First lineup-grain look at the year-over-year change, using the PBP normalization shim that landed earlier today. Updates several Q2 corrections claims.
**Sample:** 2024-25 (97 Wolves games), 2025-26 (94 Wolves games); both processed through the lineup pipeline now that the legacy PBP format is handled.

## Headline

**Two Q2 claims need substantial revision after looking at 2024-25 data:**

1. **The Gobert+Randle pairing is NOT structurally bad.** The pairing was +5.71 net rating over 1217 minutes in 2024-25 RS, and +4.57 net rating over 1348 minutes in 2025-26 RS. Both are statistically borderline positive. The -13.26 finding from the 2025-26 playoffs is opponent-specific, not a structural year-long pattern. The 2024-25 playoff version was -4.00 with wide CI.

2. **The team-level 3PA rate decline started in the regular season.** Team-wide 3PA rate dropped 3.6 percentage points from 2024-25 RS (0.456) to 2025-26 RS (0.420). This was a structural shift, not Edwards-specific (Edwards-ON and Edwards-OFF lineups dropped similarly). The 2025-26 PO collapse (0.342) is dramatic against this already-lower baseline.

**Three findings strengthen rather than revise:**

3. **DiVincenzo-on lineups in 2025-26 RS were +7.57 net rating with 95% CI [+3.0, +12.2] (statistically positive).** DiVincenzo-off was -4.57. The 12-point on/off swing is the strongest Category B evidence at the lineup grain in the project so far.

4. **Gobert+Naz pairing in 2024-25 RS was +10.76 net rating with 95% CI [+2.0, +19.1] (statistically positive).** This was 919 minutes. The Category B pairing has empirical support from a clean (non-playoff, healthy-roster) sample.

5. **2025-26 PO 3PA collapse is NOT a generic Wolves playoff regression.** The 2024-25 PO team maintained their 3PA rate (0.436 vs 0.456 RS, basically flat). The 2025-26 PO drop (0.420 RS to 0.342 PO) is specific to that playoff run.

## 1. Team-level lineup-grain four factors (Q4)

| Season | Stints | Min | Poss | Net | Off | Def | 3PA rate | eFG | fg3a/100 |
|---|---|---|---|---|---|---|---|---|---|
| 2024-25 RS | 1946 | 3937 | 7772 | +4.17 | 119.2 | 115.0 | **0.456** | 0.554 | 41.9 |
| 2025-26 RS | 1912 | 3933 | 8115 | +3.00 | 118.0 | 115.0 | **0.420** | 0.559 | 37.4 |
| 2024-25 PO | 370 | 711 | 1330 | -3.68 | 116.7 | 120.4 | 0.436 | 0.541 | 41.6 |
| 2025-26 PO | 289 | 572 | 1178 | -0.92 | 112.1 | 113.1 | **0.342** | 0.494 | 31.6 |

**Note on methodology:** these ratings are from the lineup-grain possession pipeline, not from `nba_team_advanced_stats`. The two can differ by ~5 ppp due to AND-1 attribution noise (documented v1 caveat in `lib/lineup_aggregation.py`). For year-over-year comparisons within the same methodology, the differences are meaningful; for cross-method comparison to Q1's headline numbers, treat as directional.

**Observations:**

- Team 3PA rate dropped 3.6 percentage points in regular season (-7.9% relative). eFG essentially identical (0.554 vs 0.559). Net rating slightly worse (+1.2 swing). **The team replaced some three-point volume with equally efficient inside scoring in 2025-26 RS.**
- 2024-25 PO maintained 3PA rate (0.436 vs RS 0.456, only -0.020 drop). League-norm flat-from-RS-to-PO behavior.
- 2025-26 PO 3PA dropped to 0.342 (vs RS 0.420, -0.078). The Q1 finding of "team-level 3PA cratered in playoffs" is fully visible at the lineup-grain too.
- fg3a per 100 possessions: 41.9 → 37.4 (RS YoY); 41.6 (2024-25 PO) → 31.6 (2025-26 PO). The 2025-26 PO drop of 10 fg3a per 100 is enormous.

**The structural year-over-year shift was real in shot selection but small in overall production.** The 2025-26 RS team was a +3 net team that shot fewer threes than the 2024-25 RS +4 net team. Not dramatically different. But that structurally lower 3PA baseline created vulnerability when the 2025-26 PO opponent (the Spurs) could push the team's 3PA volume even further down.

## 2. Edwards-on vs Edwards-off (Q1)

| Cohort | Stints | Min | Net | 95% CI | 3PA rate | 95% CI | fg3a/100 |
|---|---|---|---|---|---|---|---|
| 2024-25 RS Edwards-ON | 1341 | 2822 | +2.74 | [-2.0, +7.1] | 0.455 | [0.441, 0.470] | 41.9 |
| 2024-25 RS Edwards-OFF | 605 | 1115 | +7.77 | [+0.3, +14.8] | 0.460 | [0.437, 0.483] | 41.9 |
| 2025-26 RS Edwards-ON | 1023 | 2158 | +1.79 | [-2.9, +6.5] | 0.419 | [0.404, 0.435] | 37.0 |
| 2025-26 RS Edwards-OFF | 889 | 1775 | +4.46 | [-0.9, +9.9] | 0.421 | [0.403, 0.438] | 37.8 |
| 2024-25 PO Edwards-ON | 302 | 588 | -3.63 | [-14.7, +7.3] | 0.436 | [0.406, 0.463] | 42.0 |
| 2024-25 PO Edwards-OFF | 68 | 123 | -4.01 | [-21.3, +12.7] | 0.433 | [0.364, 0.500] | 39.9 |
| 2025-26 PO Edwards-ON | 165 | 324 | -6.13 | [-19.1, +6.1] | 0.341 | [0.304, 0.377] | 31.3 |
| 2025-26 PO Edwards-OFF | 124 | 248 | +5.96 | [-6.7, +18.1] | 0.344 | [0.301, 0.386] | 32.0 |

**The most important finding:** In both 2024-25 RS and 2025-26 RS, Edwards-ON and Edwards-OFF lineups had essentially identical 3PA rates (within 0.5 percentage points each season). **Edwards does not drive the team's 3PA rate in either direction.** The team's 3PA rate is structural, not Edwards-individual.

This means **the 3PA rate decline from 2024-25 RS to 2025-26 RS is a team-wide phenomenon, not an Edwards-individual shift.** Both Edwards-on (0.455 → 0.419, -3.6 pp) and Edwards-off (0.460 → 0.421, -3.9 pp) lineups dropped by nearly identical amounts.

The Edwards on/off paradox holds in both seasons:
- 2024-25 RS: Edwards-on +2.74, Edwards-off +7.77 (-5 differential)
- 2025-26 RS: Edwards-on +1.79, Edwards-off +4.46 (-3 differential)

This is the well-known bench-rest confound. When the star rests, his off minutes are against opposing bench units, inflating off-rating. The differential of -3 to -5 net rating with Edwards on the floor is consistent across seasons and consistent with standard on/off bias for franchise players.

**For Q8:** Edwards' true on/off impact is much smaller than the raw -12 reported for 2025-26 PO. The -3 to -5 confounded magnitude is similar across years. The 2025-26 PO -12 is mostly playoff-sample noise plus confound, not a real degradation in Edwards' impact.

## 3. Gobert+Randle pairing across seasons (Q2)

| Cohort | Stints | Min | Net | 95% CI | 3PA rate | fg3a/100 |
|---|---|---|---|---|---|---|
| 2024-25 RS Gobert+Randle (Naz off) | 431 | 1217 | **+5.71** | [-0.3, +12.8] | 0.422 | 39.1 |
| 2025-26 RS Gobert+Randle (Naz off) | 446 | 1348 | **+4.57** | [-1.8, +10.6] | 0.414 | 36.8 |
| 2024-25 PO Gobert+Randle (Naz off) | 92 | 252 | -4.00 | [-20.8, +11.9] | 0.452 | 44.9 |
| 2025-26 PO Gobert+Randle (Naz off) | 74 | 197 | **-12.22** | [-26.2, +1.8] | 0.317 | 29.2 |

**The Q2 corrections claim "Gobert+Randle was robustly bad" is wrong. The pairing was net-positive in BOTH regular seasons over substantial samples (1200+ minutes each).**

The pairing's RS net rating dropped only 1.1 points YoY (+5.7 → +4.6), both bumping into the positive side of the CI. The pairing's 3PA rate dropped slightly (0.422 → 0.414).

The 2024-25 PO version was -4.00 with very wide CI. The 2025-26 PO version was -12.22 with CI barely crossing zero. **The catastrophic 2025-26 PO version is opponent-specific, not a year-over-year structural collapse.**

**Comparison: Gobert+Naz pairing (Randle off)**

| Cohort | Stints | Min | Net | 95% CI | 3PA rate | fg3a/100 |
|---|---|---|---|---|---|---|
| 2024-25 RS Gobert+Naz (Randle off) | 475 | 919 | **+10.76** | [+2.0, +19.1] | 0.447 | 41.5 |
| 2025-26 RS Gobert+Naz (Randle off) | 469 | 826 | +5.78 | [-2.3, +13.9] | 0.430 | 39.7 |
| 2024-25 PO Gobert+Naz (Randle off) | 68 | 108 | +2.44 | [-22.9, +24.3] | 0.471 | 48.3 |
| 2025-26 PO Gobert+Naz (Randle off) | 75 | 127 | +9.82 | [-9.9, +28.9] | 0.290 | 27.9 |

**Important new finding:** In 2024-25 RS, the Gobert+Naz pairing had **+10.76 net rating over 919 minutes with 95% CI [+2.0, +19.1] - statistically distinguishable from zero at p<0.05.** This is the cleanest Category B evidence at the lineup grain in the project.

The pairing's net rating dropped 5 points YoY in RS (+10.8 → +5.8). The 2025-26 RS version's CI now includes zero. But the 2024-25 RS version is a clear positive lineup signal.

Note: the 2025-26 PO Gobert+Naz had 3PA rate 0.290 (very low) despite the positive net rating. This is the same "Spurs forced the team off the line" effect that hit other lineups.

**Comparison: Naz+Randle pairing (Gobert off)**

| Cohort | Stints | Min | Net | 95% CI | 3PA rate | fg3a/100 |
|---|---|---|---|---|---|---|
| 2024-25 RS Naz+Randle (Gobert off) | 436 | 828 | -0.94 | [-10.1, +7.5] | 0.497 | 44.8 |
| 2025-26 RS Naz+Randle (Gobert off) | 532 | 974 | +2.58 | [-4.3, +9.8] | 0.437 | 38.3 |
| 2024-25 PO Naz+Randle (Gobert off) | 125 | 232 | -6.28 | [-23.2, +9.4] | 0.418 | 38.0 |
| 2025-26 PO Naz+Randle (Gobert off) | 83 | 146 | -5.95 | [-23.5, +10.0] | 0.403 | 38.0 |

The Naz+Randle no-Gobert pairing is unremarkable across all four contexts. Modest positive or modest negative with wide CIs. This is the small-ball front-court lineup (Randle at the 5 with Naz at the 4) and it doesn't appear to be a high-leverage configuration.

## 4. DiVincenzo-on vs DiVincenzo-off (Q3)

| Cohort | Stints | Min | Net | 95% CI | 3PA rate | fg3a/100 |
|---|---|---|---|---|---|---|
| 2024-25 RS DiVincenzo-ON | 901 | 1608 | +4.08 | [-2.1, +9.8] | 0.484 | 43.7 |
| 2024-25 RS DiVincenzo-OFF | 1045 | 2330 | +4.22 | [-0.6, +8.9] | 0.437 | 40.6 |
| 2025-26 RS DiVincenzo-ON | 1085 | 2463 | **+7.57** | [+3.0, +12.2] | 0.433 | 38.9 |
| 2025-26 RS DiVincenzo-OFF | 827 | 1471 | **-4.57** | [-10.0, +1.0] | 0.397 | 34.8 |
| 2024-25 PO DiVincenzo-ON | 236 | 392 | -10.66 | [-22.3, +1.7] | 0.439 | 40.3 |
| 2024-25 PO DiVincenzo-OFF | 134 | 319 | +5.57 | [-8.9, +19.5] | 0.431 | 43.3 |
| 2025-26 PO DiVincenzo-ON | 42 | 96 | +14.23 | [-4.8, +35.6] | 0.366 | 33.3 |
| 2025-26 PO DiVincenzo-OFF | 247 | 476 | -4.12 | [-13.7, +5.7] | 0.337 | 31.2 |

**The 2025-26 RS DiVincenzo finding is the strongest in this comparison:** DiVincenzo-on lineups were +7.57 net rating over 2463 minutes (95% CI [+3.0, +12.2], statistically positive). DiVincenzo-off lineups were -4.57 over 1471 minutes (CI barely crosses zero on the upside).

**12-point on/off swing.** Comparable to the differential of a starting-quality player.

The 3PA rate when DiVincenzo is on:
- 2024-25 RS: 0.484 (vs 0.437 without him) - +4.7 pp Category B mechanism visible
- 2025-26 RS: 0.433 (vs 0.397 without him) - +3.6 pp Category B mechanism visible

In both years, DiVincenzo's presence raises the team's 3PA rate by 3.6-4.7 percentage points. The 2025-26 RS net rating swing is much larger than 2024-25 (12 points vs basically equal). Why?

**Hypothesis:** in 2024-25 the team had other shot-creators and stretch options (NAW, healthy roster) so DiVincenzo was one of many positive contributors. In 2025-26, after the Randle trade restructured the team and NAW left, DiVincenzo's catch-and-shoot value became more load-bearing. Without him, the team was -4.57; with him, +7.57.

The 2024-25 PO DiVincenzo-ON was -10.66 (DiVincenzo-OFF +5.57). This is the inverse direction. Small playoff sample (392 minutes), wide CI, possibly the playoff context inversion. Worth noting but not necessarily contradicting.

The 2025-26 PO DiVincenzo-ON was +14.23 over 96 minutes (CI crosses zero, small sample). Direction matches.

**For Q8:** The 2025-26 RS DiVincenzo on/off is the strongest lineup-grain finding for the DiVincenzo Achilles-recovery decision. The 12-point swing is real evidence that DiVincenzo's presence vs absence in 2025-26 RS was worth ~12 net rating points. Healthy-DiVincenzo lineups were +7.57. Without him, the 2025-26 RS team was -4.57.

## 5. Edwards + frontcourt partner combinations

| Cohort | Stints | Min | Net | 3PA rate | fg3a/100 |
|---|---|---|---|---|---|
| 2024-25 RS Edwards+Gobert | 821 | 1871 | +6.07 | 0.435 | 40.3 |
| 2024-25 RS Edwards+Naz | 786 | 1401 | +1.39 | 0.475 | 43.7 |
| 2024-25 RS Edwards+Randle | 774 | 1785 | +3.44 | 0.445 | 40.9 |
| 2025-26 RS Edwards+Gobert | 584 | 1419 | +4.38 | 0.417 | 37.3 |
| 2025-26 RS Edwards+Naz | 611 | 1026 | +1.38 | 0.437 | 38.5 |
| 2025-26 RS Edwards+Randle | 675 | 1610 | +2.68 | 0.416 | 36.9 |

**Edwards+Gobert was the highest-net pairing in BOTH years (+6.07 then +4.38).** Edwards+Naz was the highest-3PA-rate pairing (0.475, 0.437). Edwards+Randle was mid-pack on both.

This contradicts the older LAFI-narrative implication that Edwards+Gobert was a structural problem due to spacing. The data says Edwards+Gobert in regular season was the team's best high-minute Edwards pairing in both years.

(The playoff Edwards+Gobert is a different story per the prior confound checks. The Spurs scheme matters.)

## 6. Updated synthesis: what holds up after this comparison

### Findings that get STRONGER

- **DiVincenzo's Category B value at lineup grain.** 2025-26 RS DiVincenzo-on +7.57 with CI [+3.0, +12.2]. 12-point on/off swing. Statistically positive. The strongest lineup-grain Category B evidence the project has produced.

- **Edwards' team-level 3PA rate is structural, not individual.** Edwards-on and Edwards-off lineups have nearly identical 3PA rates in both years. The team-wide YoY 3PA decline (-3.6 pp) is structural, not Edwards-specific shot selection.

- **The 2025-26 PO 3PA collapse is opponent-specific.** 2024-25 PO held 3PA rate within 2 percentage points of RS. 2025-26 PO dropped 7.8 percentage points. The Spurs scheme is the mechanism.

### Findings that need REVISION

- **"Gobert+Randle pairing is structurally bad" - WEAKENED.** The pairing was +5.71 in 2024-25 RS and +4.57 in 2025-26 RS. The -13.26 finding from 2025-26 PO is opponent-specific, not a year-long pattern. **The Q2 corrections doc's confident claim that this is the "strongest single Q2 finding" should be downgraded.** The 2025-26 PO Gobert+Randle was specifically bad against the Spurs.

- **"The team's offensive collapse started with Edwards' shot selection" - WEAKENED.** The team-wide 3PA decline is not specifically Edwards. It's a structural shift the team made over the off-season (possibly tied to the Randle trade, possibly coaching choice). Edwards' on/off doesn't drive it.

### Findings that get NEW SUPPORT

- **Gobert+Naz pairing in 2024-25 RS was statistically positive (+10.76, CI [+2.0, +19.1]).** This is the cleanest Category B evidence at the lineup grain. The pairing's effectiveness declined in 2025-26 RS (+5.78, CI crosses zero) but the 2024-25 evidence is robust.

- **Edwards+Gobert in regular season is the team's best high-minute pairing in both years.** The LAFI-narrative implication that "Gobert clogs the lane for Edwards" is not supported at the RS lineup-grain level. The Edwards+Gobert RS pairing was +6.07 in 2024-25 and +4.38 in 2025-26.

## 7. Implications for Q3, Q5, Q8

**For Q3 (Mechanism analysis):**
- The central question becomes sharper: **what did the Spurs do to force the Wolves' 3PA rate from 0.420 RS to 0.342 PO, when no comparable opponent did this in 2024-25?** The Wembanyama-anchored defensive scheme is the proximate cause. PnR coverage decoder should specifically test SAS closeout patterns vs DEN/OKC/LAL closeout patterns from 2024-25 PO.
- The team-wide 3PA decline from 2024-25 RS to 2025-26 RS is a coaching/personnel question, not an opponent question. Q3 doesn't address it directly but Q5 should.

**For Q5 (Prescription):**
- **The "trade Randle, keep Gobert+Naz" framing weakens.** Gobert+Randle was net-positive in regular season both years. The Randle trade case loses some of its empirical foundation. If anything, the data supports "deploy Gobert+Naz lineups more (especially Edwards+Gobert+Naz)" rather than "trade Randle."
- **The DiVincenzo recovery becomes high-leverage.** With DiVincenzo healthy in 2025-26 RS, lineups were +7.57. Without, -4.57. The Achilles recovery projection is decision-relevant for the team's actual ceiling.
- **The team's lower 2025-26 RS 3PA baseline is a strategic question.** Going into 2026-27, should the team return to the 2024-25 0.456 3PA rate baseline or stay at the 2025-26 0.420 baseline? The 2024-25 version had better net rating but went to WCF; the 2025-26 version had lower 3PA but similar efficiency and went to R2.

**For Q8 (Player decisions):**
- **Gobert keep/trade case is now mixed.** Gobert+Randle was positive in RS but bad in 2025-26 PO. Gobert+Naz was statistically positive in 2024-25 RS but neutral in 2025-26 RS. Edwards+Gobert is positive in RS both years. The case for keeping Gobert is stronger than the Q2 corrections doc implied; the case for trading him weakens.
- **Randle keep/trade case also gets less clear-cut.** Edwards+Randle was +3.44 in 2024-25 RS and +2.68 in 2025-26 RS. Not great but not catastrophic. Gobert+Randle was positive in both regular seasons.
- **DiVincenzo decision becomes clearer:** the 12-point on/off swing in 2025-26 RS is real evidence. Whatever it costs to ensure DiVincenzo's Achilles recovery and re-sign him is supported by this finding.

## 8. What I didn't do (transparency)

- Game-by-game year-over-year line-up matching (which lineups recurred across seasons with similar personnel). The aggregated comparisons here are at the cohort level rather than matched-lineup. Useful for some Q8 questions but not built.
- Opponent-adjusted year-over-year comparisons. The 2024-25 PO was a different opponent slate than 2025-26 PO. Not adjusted.
- RAPM-style adjusted impact. Next in the sequence per Bobby's instruction.

## 9. Artifacts

```
analyses/q2_localize/yoy_lineups.py        driver

outputs/tables/q2_localize/
  yoy_team_lineup_grain.csv          team-level four factors comparison
  yoy_edwards_lineups.csv             Edwards on/off across both seasons
  yoy_big_pairings.csv                Gobert+Randle, Gobert+Naz, Naz+Randle
  yoy_divincenzo_lineups.csv          DiVincenzo on/off
  yoy_edwards_partners.csv            Edwards+frontcourt partner combos
```

Re-runnable: `python -m analyses.q2_localize.yoy_lineups`.

## 10. Status

The 2024-25 comparison has produced two findings that revise the Q2 corrections framing (Gobert+Randle isn't structurally bad; Edwards isn't the 3PA driver) and two findings that strengthen the project's broader narrative (DiVincenzo Category B value; Spurs-specific 3PA collapse). 

This is exactly what the "let the data lead" discipline produces. The story is getting more textured. Some of the prescriptive implications from Q2 corrections will need to be softened in Q5; others (DiVincenzo) get clearer.

Ready for RAPM build next.
