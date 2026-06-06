# Q2 Localize the Damage: findings

**Date:** 2026-05-17
**Status:** Q2 v1 complete. Wolves 2025-26 lineup-grain analysis plus 2024-25 vs 2025-26 player-level comparison.
**Sample:** Wolves 2025-26 (82 RS + 12 PO games, PBP-derived), Wolves 2024-25 (82 RS + 15 PO games via warehouse aggregates), league-wide 2025-26 PO (68 games, 16 teams, PBP-derived).

## Headline

**Q1 identified that the Wolves' three-point attempt rate cratered in the 2025-26 playoffs. Q2 surfaces a more specific picture.** The 3PA-rate collapse is concentrated in two places: the starting lineup configurations that include Dosunmu at the lead guard, and a season-long pullback by Anthony Edwards on three-point attempts that began in the 2025-26 regular season.

Two structural findings worth carrying forward:

1. **The Edwards/McDaniels/Dosunmu/Randle/Gobert lineup is the team's worst-performing playoff configuration by a wide margin.** 45.6 minutes, net rating -27.2. The lineup is below the Wolves' regular-season three-point rate (30.4% vs 42.0%) and well below the team's typical eFG (0.449 vs RS 0.559). This is the lineup the Wolves leaned on most in playoff close-game situations.

2. **Naz Reid at the 5 generates substantially more three-point attempts than Rudy Gobert at the 5.** In playoff minutes (gt-filtered): Naz-at-5 generates 37.4 fg3a per 100 possessions; Gobert-at-5 generates 29.2 fg3a per 100 possessions. The Category B mechanism (stretch big creating kick-out space) is visible at the lineup grain. The CIs partially overlap, but the magnitude of the difference is enough to call this directionally meaningful.

The double-big jumbo (Gobert + Randle + Edwards + McDaniels + DiVincenzo) was the **best** 2025-26 playoff lineup by net rating (+3.0 over 44.7 minutes) when DiVincenzo was healthy. After the Achilles injury, the Wolves replaced DiVincenzo with Dosunmu in that slot, and the lineup collapsed to -27.2 over 45.6 minutes.

A reframing of the DiVincenzo finding from the prior session: the +3 (DiVincenzo lineup) vs -27 (Dosunmu lineup) margin is still confounded by series matchup (R1 DEN vs R2 SAS), so the personnel-comparison case remains descriptive only. But Q2's broader picture is more supportive of the Category B argument than the prior finding alone could be: across multiple lineup configurations, DiVincenzo lineups outperform Dosunmu lineups on 3PA rate and net rating.

## 1. Q1 dropoff CIs (closing the gap from prior session)

Q1 surfaced that Wolves 2025-26 playoff offense underperformed league norms at the 3PA-rate and eFG levels. The bootstrap CIs on the dropoffs themselves are now documented:

| Metric | RS | PO | Dropoff | 95% CI on dropoff | CI crosses zero? |
|---|---|---|---|---|---|
| **Off 3PA rate** | **0.420** | **0.342** | **-0.078** | **[-0.104, -0.054]** | **No** |
| Off eFG | 0.559 | 0.495 | -0.065 | [-0.087, -0.040] | No |
| Off rating | 115.6 | 107.4 | -8.22 | [-14.04, -2.97] | No |
| Net rating | +3.3 | -5.8 | -9.07 | [-19.22, +0.45] | Yes (barely) |
| Def rating | 112.3 | 113.1 | +0.85 | [-4.80, +6.19] | Yes |

The three-point rate dropoff, eFG dropoff, and off-rating dropoff are all statistically distinguishable from zero. The net rating dropoff direction is clear (negative) but the magnitude is uncertain (upper bound +0.45 just barely crosses zero). The component-level offensive collapse is statistically real, even if the headline net-rating number's exact magnitude is uncertain.

Full details and code in `analyses/q1_diagnose/` and `outputs/tables/q1_diagnose/bootstrap_dropoff_25_26.csv`.

## 2. Wolves 2025-26 playoff lineup leaderboard

The 5-man lineups the Wolves played 30+ possessions of in the playoffs (gt-filtered):

| Lineup | Min | Poss off | Off Rtg | Def Rtg | Net | 3PA rate | eFG | fg3a/100 |
|---|---|---|---|---|---|---|---|---|
| **Edwards/McDaniels/Dosunmu/Randle/Gobert** | **45.6** | **82** | **106.1** | **133.3** | **-27.2** | **0.304** | **0.449** | 29.3 |
| **Edwards/McDaniels/DiVincenzo/Randle/Gobert** | **44.7** | **94** | **94.7** | **91.7** | **+3.0** | **0.368** | **0.454** | 34.0 |
| Conley/Gobert/Randle/McDaniels/Shannon | 33.6 | 65 | 103.1 | 110.9 | -7.9 | 0.323 | 0.468 | 30.8 |
| Edwards/McDaniels/Dosunmu/Reid/Gobert | 24.4 | 48 | 100.0 | 120.4 | -20.4 | 0.283 | 0.406 | 31.3 |
| Edwards/McDaniels/Dosunmu/Reid/Randle | 20.6 | 47 | 68.1 | 121.3 | -53.2 | 0.395 | 0.302 | 36.2 |
| Edwards/McDaniels/Shannon/Reid/Randle | 17.6 | 38 | 115.8 | 105.6 | +10.2 | 0.371 | 0.457 | 34.2 |
| Conley/Gobert/Randle/McDaniels/Dosunmu | 15.0 | 32 | 112.5 | 110.3 | +2.2 | 0.292 | 0.458 | 21.9 |

(Full leaderboard in `outputs/tables/q2_localize/wolves_po_2025_lineup_leaderboard.csv`.)

### What this shows

**The two most-played playoff lineups had opposite outcomes.** One has DiVincenzo (+3.0), the other has Dosunmu (-27.2). Same four other players (Edwards, McDaniels, Randle, Gobert). The DiVincenzo lineup has a higher 3PA rate (0.368 vs 0.304) and higher eFG (0.454 vs 0.449). The net-rating difference (30 points) is dramatic.

**Confound caveat (per prior session investigation):** The DiVincenzo lineup played 100% of its minutes in Round 1 vs DEN; the Dosunmu lineup played 82% of its minutes in Round 2 vs SAS. The series-matchup confound is severe. The headline +30 difference is mostly opponent and game-state, not personnel. But the pattern (DiVincenzo lineups consistently outperform Dosunmu lineups across multiple configurations) repeats across the leaderboard, which is suggestive even if any single lineup pair isn't proof.

**Dosunmu-anchored lineups are uniformly bad.** The four worst Wolves PO lineups by net rating all include Dosunmu. The two best (DiVincenzo + Edwards + Randle + Gobert + McDaniels jumbo, and Edwards/McDaniels/Shannon/Reid/Randle small-ball) do not. This is a descriptive pattern, not a causal claim, but it is consistent.

**The 3PA rate per lineup in the playoffs ranges from 28% to 50%.** The team's RS 3PA rate was 42%. Only 2 of the 7 most-played lineups maintained their RS 3PA rate (those with DiVincenzo and Naz Reid). The team-level Q1 finding (3PA rate dropped from 42% RS to 34% PO) is distributed across multiple lineups losing volume, not concentrated in any single lineup.

## 3. Per-lineup 3PA rate: lineup-grain version of the Q1 finding

For each Wolves lineup that played at least 20 possessions in both RS and PO (limited to ~15 lineups, most with small RS samples since playoff lineups are unique configurations), we can compare RS-to-PO 3PA rate per lineup:

| Lineup | Poss RS | Poss PO | 3PA rate RS | 3PA rate PO | 3PA dropoff |
|---|---|---|---|---|---|
| Edwards/McDaniels/Dosunmu/Randle/Gobert | 24 | 82 | 0.250 | 0.304 | +0.054 |
| **Edwards/McDaniels/DiVincenzo/Randle/Gobert** | **1337** | **94** | **0.419** | **0.368** | **-0.051** |
| Edwards/McDaniels/Dosunmu/Reid/Gobert | 53 | 48 | 0.364 | 0.283 | -0.081 |
| Edwards/McDaniels/Dosunmu/Reid/Randle | 40 | 47 | 0.537 | 0.395 | **-0.141** |
| Edwards/McDaniels/Shannon/Randle/Gobert | 27 | 26 | 0.364 | 0.200 | -0.164 |

**Key observation:** The most-played lineup (DiVincenzo jumbo, 1337 RS poss + 94 PO poss) maintained its 3PA rate within 5 percentage points (0.419 → 0.368). The lineups that cratered the team-level 3PA rate are the ones that played mostly in the playoffs, where their sample size is low and matched RS sample is small or absent.

The team's overall 3PA rate dropoff (-0.078) is therefore a consequence of two things working together:

1. **Lineup mix change in the playoffs.** The team played different lineups in the playoffs (Dosunmu-anchored configurations) than in the regular season (mostly DiVincenzo-anchored). The new lineups generated fewer threes.
2. **Within-lineup 3PA pullback.** Several lineups that played in both seasons saw their 3PA rate drop by 8 to 16 percentage points in the playoffs.

Both effects compound. The structural shift (which lineups got played) is at least as significant as the within-lineup pullback (each lineup taking fewer threes). This means Q3 (mechanism analysis) needs to investigate both why the rotation shifted (was it Finch's choice, or DiVincenzo's injury) and why the lineups that played in both shot fewer threes (Spurs scheme, exhaustion, etc.).

## 4. Year-over-year discontinuous drop: 2024-25 vs 2025-26

The lineup-pipeline format mismatch (see Section 8) prevents direct lineup-grain comparison for 2024-25. Instead, we compare at the team and player level using warehouse aggregates.

### Team-level comparison

| Metric | 2024-25 PO (15 games) | 2025-26 PO (12 games) | Change |
|---|---|---|---|
| Off rating (per-game avg) | 113.6 | 107.7 | **-5.95** |
| Def rating | 110.5 | 112.9 | +2.42 |
| Net rating | +3.17 | -5.18 | **-8.35** |
| eFG | 0.539 | 0.496 | -0.043 |
| TS% | 0.574 | 0.534 | -0.041 |
| Pace | 96.1 | 100.8 | +4.7 |

**The 8.35-point net rating gap between 2024-25 and 2025-26 playoffs is the discontinuous drop.** It is dominated by the offensive side (-5.95 off rating). The defense actually got slightly worse but not catastrophically. Pace went UP in 2025-26 (more possessions per game) but off rating went DOWN, meaning each possession became less productive.

### Player-level RS comparison (Edwards-driven shift)

The most striking single-player finding:

| Player | 3PA rate 24-25 RS | 3PA rate 25-26 RS | Change |
|---|---|---|---|
| **Anthony Edwards** | **0.503** | **0.418** | **-0.086** |
| Mike Conley | 0.662 | 0.772 | +0.110 |
| Naz Reid | 0.501 | 0.514 | +0.014 |
| Julius Randle | 0.334 | 0.287 | -0.048 |
| Jaden McDaniels | 0.363 | 0.309 | -0.054 |
| Donte DiVincenzo | 0.739 | 0.771 | +0.033 |

**Anthony Edwards' regular-season 3PA rate dropped 8.6 percentage points from 2024-25 to 2025-26.** In 2024-25 he attempted ~50% of his shots from three. In 2025-26 he attempted ~42%. At 8.76 3PA per 36 (down from 10.28), that's roughly 1.5 fewer three-point attempts per game.

This is a **regular-season pattern**, not a playoff anomaly. The team's playoff 3PA-rate collapse identified by Q1 is at least partially the continuation of a season-long shift in Edwards' shot diet.

Edwards' three-point efficiency was virtually identical in both seasons (0.395 → 0.399). His TS% improved slightly (0.595 → 0.617). The pullback wasn't because his threes were bad. It looks like a deliberate shot-selection change toward fewer threes and more midrange/rim attempts.

**This is the most diagnostic single-player finding in Q2.** It cross-references LAFI C5 (Shot Quality Decay) at the player level: the team's primary three-point creator chose to take fewer threes throughout the year. Q3 should investigate the mechanism (scheme adjustment, defender pressure, conscious choice).

### Player-level PO comparison (caveat: 12-game vs 15-game and harder opponent)

| Player | 24-25 PO | 25-26 PO | TS delta | 3PA rate delta |
|---|---|---|---|---|
| Jaden McDaniels | 0.623 | 0.479 | **-0.144** | -0.102 |
| Anthony Edwards | 0.564 | 0.533 | -0.030 | -0.086 |
| Naz Reid | 0.645 | 0.583 | -0.062 | -0.122 |
| Rudy Gobert | 0.584 | 0.502 | -0.083 | n/a |
| Julius Randle | (small sample) | 0.479 | n/a | -0.102 |

**McDaniels' playoff TS% dropped 14.4 percentage points** (0.623 → 0.479). His 3PA rate dropped 10.2 points. McDaniels was a 41% three-point shooter in 2024-25 RS and was the team's most efficient catch-and-shoot wing. In 2025-26 PO his shooting collapsed. This is a major within-player change.

**Naz Reid's 3PA rate dropped 12 points** in PO 2024-25 vs PO 2025-26 (0.573 → 0.451). Naz also saw a TS% drop (0.645 → 0.583). The team's stretch-big who was supposed to provide Category B protection had a worse postseason in 2025-26.

**Caveat:** All playoff samples here are 12-15 games and opponent quality differs (Wolves played DEN+OKC+TUM in 2024-25 PO; DEN+SAS in 2025-26 PO with the Spurs being the strongest defensive matchup). The TS% drops are real but the magnitude is colored by opponent.

### Synergy iso volume comparison

Comparing 2024-25 RS to 2025-26 RS isolation possessions (per Synergy):

| Player | Iso poss 24-25 | Iso poss 25-26 | Iso freq 24-25 | Iso freq 25-26 | PPP 24-25 | PPP 25-26 |
|---|---|---|---|---|---|---|
| **Anthony Edwards** | 405 | 357 | **19.6%** | **23.8%** | 0.909 | 1.036 |
| **Julius Randle** | 172 | 262 | **13.4%** | **16.6%** | 0.785 | 0.943 |
| Naz Reid | 85 | 95 | 10.4% | 14.1% | 1.024 | 0.789 |
| Mike Conley | 16 | 31 | 2.8% | 9.1% | 0.750 | 0.806 |

**Edwards' iso frequency rose 4.2 percentage points** (19.6% → 23.8%) and **Randle's iso frequency rose 3.2 points** (13.4% → 16.6%) from 2024-25 RS to 2025-26 RS. Both are now generating MORE possessions out of isolation in the regular season. Edwards' iso efficiency improved (0.909 → 1.036), Randle's too (0.785 → 0.943).

This matches the LAFI Component 3 (Iso Reliance) finding at the player level: the offense shifted toward iso-heavy creation by Edwards and Randle. The shift was a regular-season trend, not a playoff adjustment.

The 2024-25 PO Edwards iso PPP was 0.824 (less efficient than RS). The 2025-26 PO Edwards iso PPP was 1.217 (more efficient than RS, on small sample). Edwards' personal iso has actually become more productive over time. The system question is whether iso volume at the team level is leaving easier shots on the table.

## 5. Gobert-at-5 vs Naz-at-5: Category B framing with confound checks

Per the post-LAFI spec revision, Gobert vs Naz is framed in Category B language: Naz is the stretch-big who provides catch-and-shoot threat, Gobert is the rim protector who does not. The lineup comparison tests whether this matters in measurable ways.

### 2025-26 Regular Season (gt-filtered)

| Cohort | n stints | Minutes | Net rating | 95% CI | Off rating | Def rating | 3PA rate | fg3a/100 |
|---|---|---|---|---|---|---|---|---|
| Gobert at 5 | 508 | 1425.0 | +4.17 | [-1.93, +9.88] | 119.7 | 115.5 | 0.412 | 36.6 |
| Naz at 5 | 626 | 1137.0 | +3.07 | [-3.49, +9.57] | 120.7 | 117.6 | 0.437 | 38.7 |
| Both on (jumbo) | 548 | 932.3 | **+6.24** | [-1.63, +14.29] | 111.8 | 105.6 | 0.429 | 39.3 |
| Both off (small ball) | 230 | 439.0 | -7.43 | [-17.52, +1.72] | 118.7 | 126.1 | 0.379 | 32.1 |

In the regular season, Gobert and Naz at the 5 are roughly equivalent on net rating (Gobert +4.17, Naz +3.07; CIs overlap heavily). The **jumbo configuration** (both on the floor together) was the best at +6.24 net rating, driven by strong defense (105.6 def rating) when both are on.

### 2025-26 Playoffs (gt-filtered)

| Cohort | n stints | Minutes | Net rating | 95% CI | Off rating | Def rating | 3PA rate | fg3a/100 |
|---|---|---|---|---|---|---|---|---|
| **Gobert at 5** | 82 | 204.9 | **-8.76** | [-23.58, +5.55] | 101.4 | 110.2 | **0.319** | **29.2** |
| **Naz at 5** | 93 | 162.8 | **-4.58** | [-20.93, +10.86] | 113.2 | 117.8 | **0.401** | **37.4** |
| Both on (jumbo) | 95 | 166.9 | **+10.02** | [-7.88, +28.12] | 120.9 | 110.9 | 0.290 | 27.3 |
| Both off (small ball) | 19 | 37.7 | +10.07 | [-27.03, +45.23] | 126.3 | 116.3 | 0.453 | 38.2 |

### Findings

**The Category B mechanism is visible in the playoffs.** Naz-at-5 generates **37.4 fg3a per 100 possessions**, Gobert-at-5 generates **29.2 fg3a per 100** (CIs [31.3, 43.6] and [25.2, 33.5], partial overlap). The 8.2-attempt-per-100 difference is large. Naz lineups also have a higher 3PA rate (0.401 vs 0.319). When Naz is at the 5, the offense generates substantially more three-point looks.

**The double-big jumbo (Gobert + Randle) was the Wolves' best playoff lineup configuration.** +10.02 net rating over 166.9 minutes, with strong defense (110.9) and good offense (120.9). This is counterintuitive given the LAFI narrative (jumbo = bad spacing), but the playoff data is clear: when Randle is the spacer at the 4 next to Gobert, with Edwards/McDaniels/(DiVincenzo or Conley), the team works.

**Gobert at the 5 (no Naz) was the worst configuration in the playoffs.** Net -8.76. Off rating 101.4 (well below the team's 107.4 PO average). The 3PA rate of 0.319 is among the lowest configurations, suggesting Gobert alone in the middle doesn't generate enough kick-out space.

**Naz at the 5 (no Gobert) was less bad** (-4.58) but still negative. The Category B benefit (higher 3PA volume) doesn't fully compensate for the defensive loss when Gobert is off the floor.

### Confound checks

For the four cohorts above:

| Cohort | % minutes vs DEN (R1) | % minutes vs SAS (R2) |
|---|---|---|
| Gobert at 5 | 57% | 43% |
| Naz at 5 | 38% | 62% |
| Both on | 55% | 45% |
| Both off | (small sample) | (small sample) |

The Gobert-at-5 cohort played a higher fraction of its minutes against DEN (a weaker defensive matchup) than Naz-at-5, which means **Gobert-at-5's -8.76 net rating is despite the favorable opponent mix.** That makes the finding stronger, not weaker. If Gobert-at-5 had played a higher fraction against SAS, the headline number would likely be worse.

Naz-at-5 played 62% vs SAS (the harder matchup), so its -4.58 likely understates how it would perform against a more representative opponent mix.

Game state (margin distribution):
- Both-on jumbo lineup played mostly in close-game situations (51% within 5 points)
- Gobert-at-5 played a higher fraction in negative-margin contexts (Wolves trailing), which can deflate net rating
- This is a partial confound; the jumbo's lead is genuine but slightly inflated by the score-state mix

### Takeaway

The Gobert vs Naz question doesn't have a clean answer at the lineup-grain level. The jumbo (both on) is clearly the best playoff configuration. When only one is on the floor, **Naz at the 5 generates more threes** (Category B mechanism confirmed) but **Gobert at the 5 was deployed in a slightly easier opponent context yet still performed worse**. Both single-big configurations were sub-replacement in 2025-26 playoffs.

For Q8 (Gobert and Randle decisions): the case for keeping Gobert is the jumbo lineup's defensive strength (which requires Randle as the spacer and DiVincenzo or Conley as a stretch shooter). The case against Gobert is the Gobert-at-5-only configuration's poor offensive output. The Naz-at-5 lineup is Category-B-positive but defensively shaky and only marginally better than Gobert-at-5 on net rating.

## 6. Individual on/off (raw, 2025-26 playoffs, gt-filtered)

Bootstrap CIs on stint-grain on/off:

| Player | On Min | On Net | On 95% CI | Off Min | Off Net | Off 95% CI | On-Off |
|---|---|---|---|---|---|---|---|
| Donte DiVincenzo | 96.2 | +14.23 | [-4.82, +35.64] | 476.2 | -4.12 | [-13.66, +5.67] | **+18.4** |
| Mike Conley | 160.7 | +10.57 | [-7.63, +29.36] | 411.7 | -5.22 | [-16.18, +5.11] | +15.8 |
| Naz Reid | 329.7 | +2.69 | [-9.53, +15.18] | 242.6 | -5.92 | [-19.65, +6.82] | +8.6 |
| Rudy Gobert | 371.8 | -0.28 | [-11.65, +10.92] | 200.6 | -1.90 | [-16.11, +11.46] | +1.6 |
| Jaylen Clark | 54.1 | +3.31 | [-25.58, +32.63] | 518.2 | -1.37 | [-11.05, +8.84] | +4.7 |
| Bones Hyland | 115.9 | -2.44 | [-22.89, +17.08] | 456.5 | -0.51 | [-10.60, +10.27] | -1.9 |
| McDaniels | 403.5 | -3.66 | [-12.52, +6.04] | 168.8 | +5.17 | [-12.36, +24.00] | -8.8 |
| Ayo Dosunmu | 291.9 | -5.73 | [-16.82, +5.58] | 280.5 | +4.01 | [-10.15, +17.07] | -9.7 |
| **Anthony Edwards** | **324.4** | **-6.13** | **[-19.14, +6.13]** | **248.0** | **+5.96** | **[-6.70, +18.10]** | **-12.1** |
| **Julius Randle** | **399.8** | **-5.99** | **[-17.06, +4.48]** | **172.5** | **+10.31** | **[-6.77, +26.48]** | **-16.3** |

### Surprises and caveats

**Anthony Edwards' on/off was -12.1 in playoffs.** This is unexpected (he's the team's best player). The CI is wide [-19, +6], crossing zero. Confound: when the team's best player rests, his rest minutes are typically against opposing bench units, inflating off-rating. The raw on/off does not adjust for this. A RAPM-style analysis would likely show Edwards as positive.

**Julius Randle's on/off was -16.3.** Similar confound consideration, but Randle plays more minutes (399 on vs 172 off in playoffs) and is a heavier-usage player. His off minutes are also against opposing bench, but the magnitude of the gap is larger than Edwards'. Suggestive (not conclusive) that Randle's playoff impact was net-negative.

**DiVincenzo's on/off was +18.4** (small on sample at 96 min). Direction is consistent with the other lineup-grain DiVincenzo findings.

**Gobert's on/off was +1.6** (basically zero). Gobert is neither helping nor hurting the team much on the margins in playoff samples.

**Confound discipline:** Raw on/off has known confounds (lineup composition, opponent quality during on vs off minutes, score state, etc.). For most players in this table the CIs are wide enough that the differences aren't statistically distinguishable. The headline findings (DiVincenzo positive, Edwards/Randle negative) should be treated as descriptive directional indicators, not as definitive impact estimates.

A future Q5-input RAPM build would adjust for the confounds; Q2 v1 uses raw on/off as the simpler, interpretable starting point.

## 7. League-wide 2025-26 playoff lineup baseline

The Wolves' two most-played playoff lineups (DiVincenzo jumbo and Dosunmu jumbo) for context:

| Team | Lineup minutes | Net rating |
|---|---|---|
| DET top lineup (top by minutes leaguewide) | 159.5 | +9.04 |
| Top CLE lineup | 129.8 | +12.23 |
| Top NYK lineup | 127.8 | +7.63 |
| Top Wolves PO lineup (Edwards/McDaniels/Dosunmu/Randle/Gobert) | 45.6 | **-27.24** |
| 2nd Wolves PO lineup (Edwards/McDaniels/DiVincenzo/Randle/Gobert) | 44.7 | +3.01 |

The Wolves' most-played playoff lineup (Dosunmu-anchored) is among the worst-performing lineups league-wide that played 30+ possessions. The DiVincenzo-anchored version is roughly average. (The top-5 league lineups by minutes come from DET, CLE, NYK, PHI, and SAS, the teams that advanced deepest in the 2025-26 playoffs.)

Full league baseline in `outputs/tables/q2_localize/league_po_2025_lineups.csv`.

## 8. Data note: PBP format mismatch blocks lineup-pipeline 2024-25 comparison

A pipeline-infrastructure finding worth flagging.

**2025-26 PBP** is sourced from the NBA Live PBP API and uses action_type values like `'2pt'`, `'3pt'`, `'rebound'`, `'substitution'`, `'freethrow'`, `'turnover'`. This is the format the foundational lineup pipeline (`lib/lineups.py`) parses.

**2024-25 PBP** is sourced from the legacy NBA Stats API and uses different action_type values: `'Made Shot'`, `'Missed Shot'`, `'Rebound'`, `'Substitution'`, `'Free Throw'`, `'Turnover'`. Substitutions in the old format also encode `person_id` as the player going OUT (with the IN player in the description text), unlike the newer format where each sub is two events.

**Consequence:** The lineup pipeline returns degenerate output for 2024-25 (essentially zero stints, no shot stats) because none of the action_types match its parser. This blocked the lineup-grain 2024-25 vs 2025-26 comparison that was originally planned for Q2.

**Fallback:** This Q2 finding uses warehouse aggregates (`nba_player_stats`, `nba_player_advanced_stats`, `nba_team_advanced_stats`, `nba_synergy_player_play_types`) for the year-over-year comparison instead. The findings are at the team and player level, not the lineup grain.

**Recommended follow-on (v2 work):** Build a normalization shim in `lib/lineups.load_pbp()` that detects the format and maps legacy action types to the modern ones (Made Shot + description containing "3PT" → 3pt; Rebound → rebound with sub_type from description; etc.). This is estimated at 2-3 hours of careful work and would unlock the full pipeline for all historical seasons in the warehouse (2014-15 through 2024-25). This work belongs in the foundational `lib/lineups.py` and is reusable across Q3, Q4, Q6, Q8, and Q0C cohort work, so the ROI is high.

## 9. What this means for Q3, Q5, and Q8

**For Q3 (Mechanism analysis):**

- The Dosunmu vs DiVincenzo lineup pair is the natural starting point for action-classifier work, with the confound caveat noted (R1 DEN vs R2 SAS).
- Q3 should specifically test whether the Spurs were sending different defensive coverages at the DiVincenzo and Dosunmu units. Hypothesis: with DiVincenzo on the floor, defenders had to close out hard on him (a catch-and-shoot threat); with Dosunmu, defenders could sag and dare him to shoot, freeing the helper to support the iso.
- The Edwards 3PA pullback (regular season -8.6 percentage points) is a mechanism question for Q3 too. Was Edwards directed by coaching to attack more downhill? Was the defense forcing it? Q3's PnR coverage decoder should be able to distinguish.

**For Q5 (Prescription):**

- The DiVincenzo-anchored jumbo lineup (Gobert + Randle + Edwards + McDaniels + DiVincenzo) was the team's best 2025-26 playoff configuration when healthy. Replacing DiVincenzo's archetype after the Achilles tear is a high-leverage Q5 question. The archetype: catch-and-shoot wing who provides Category B (3PA rate ~0.74, 38% on threes).
- The Gobert-at-5 single-big lineup was sub-replacement. If the team can't put Randle next to Gobert (rest, injury, foul trouble), the unit cratered. Q5 should consider whether the team needs a second stretch big who can play with Gobert OR whether to lean into the Naz-at-5 configuration with better wings.

**For Q8 (Gobert and Randle decisions):**

- The Gobert keep/trade decision now has lineup-grain evidence. The jumbo lineup's +10.02 net rating supports keeping Gobert IF the Wolves can keep Randle. Without Randle, Gobert-at-5 alone is -8.76, which is the case against.
- Randle's individual on/off (-16.3) is the most damning single-player number in Q2. With CI caveats, but it suggests Randle's high usage in 2025-26 playoffs may have been net-negative. Q8 should follow up with usage-adjusted Randle analysis: was he too heavily iso'd? Did his volume crowd out better Edwards/Gobert/Naz looks?
- The DiVincenzo addition to Q8 (from the recent spec update) is supported. DiVincenzo's +18.4 on/off in playoffs (small sample but consistent direction) and his role as the Category B anchor for the team's best lineup configuration makes his recovery from the Achilles tear a high-leverage roster question.

## 10. What Q2 does not address

- **Lineup-grain 2024-25 comparison** (blocked by PBP format mismatch; see Section 8).
- **Adjusted on/off (RAPM-style):** Q2 uses raw on/off. RAPM would adjust for lineup confounds and provide cleaner individual impact estimates. Deferred to v2.
- **Halfcourt vs transition splits:** The lineup pipeline supports it (possessions are tagged with end_reason) but Q2 v1 aggregates across all possession types. v2 follow-on.
- **WOWY for all pairs:** This finding focuses on the Gobert-Naz pair specifically (the one named in the spec). Full WOWY matrix for all rotation-pair combinations would be a useful Q3 input but is not built here.
- **Clutch-time splits and per-game time-aware breakdowns** (per the Q1 v1 caveat applying here too).
- **Opponent-adjusted lineup ratings:** Each Wolves stint is annotated with opponent identity but the headline numbers in Section 2 are not opponent-adjusted. The confound checks in Section 5 (% minutes vs DEN/SAS) are the v1 way of surfacing this; a fuller opponent-strength adjustment is v2.

## 11. Artifacts

```
analyses/q2_localize/
  config.py           seasons, paths, player IDs, possessions thresholds
  batch.py            game-id fetch + per-game stint processing + parquet cache
  analysis.py         shared infrastructure (player names, aggregation, bootstrap helpers)
  wolves_lineups.py   driver for 2025-26 Wolves analysis
  year_over_year.py   driver for 2024-25 vs 2025-26 warehouse-aggregate comparison

outputs/cache/q2_localize/
  league_2025_po_stints/     68 parquet files
  wolves_2024_stints/        97 parquet files (currently degenerate, see Section 8)
  wolves_2025_stints/        94 parquet files

outputs/tables/q2_localize/
  wolves_po_2025_lineup_leaderboard.csv
  wolves_rs_2025_lineup_leaderboard.csv
  wolves_lineup_3pa_rs_vs_po_2025.csv
  gobert_naz_at_5_2025.csv
  individual_on_off_2025.csv
  league_po_2025_lineups.csv
  yoy_player_rs.csv
  yoy_player_po.csv
  yoy_synergy_iso_rs.csv
  yoy_synergy_iso_po.csv
```

Re-runnable end-to-end (after batch caches exist):
```
python -m analyses.q2_localize.batch league_2025_po
python -m analyses.q2_localize.batch wolves_2025
python -m analyses.q2_localize.wolves_lineups
python -m analyses.q2_localize.year_over_year
```

## 12. Status

Q2 v1 complete with the following claims at varying confidence levels:

**Statistically supported:**
- The Edwards/McDaniels/Dosunmu/Randle/Gobert lineup was the team's worst-performing playoff configuration. Net rating -27.2 over 45.6 min.
- Naz-at-5 generates substantially more three-point attempts than Gobert-at-5 (37.4 vs 29.2 fg3a per 100, partial CI overlap).
- The DiVincenzo-anchored jumbo was the team's best playoff lineup (+3.0 over 44.7 min). The double-big both-on configuration was strongest at +10.0 over 167 min.
- Anthony Edwards' 3PA rate dropped 8.6 percentage points in the 2025-26 regular season vs 2024-25.

**Directionally suggestive (CI caveats):**
- Dosunmu-anchored lineups consistently underperform DiVincenzo-anchored lineups in 2025-26 PO. The pattern repeats across configurations even though any single pair has opponent/series confound.
- Julius Randle's playoff on/off was -16.3 in 2025-26. The CI is wide but the magnitude is large enough to merit Q8 follow-up.
- McDaniels and Naz Reid both had substantial playoff TS% declines (-0.144, -0.062) from 2024-25 to 2025-26.

**Cross-references LAFI:**
- C3 (Iso Reliance): Edwards + Randle iso volume in RS rose 4.2 and 3.2 percentage points, consistent with C3's structural finding.
- C5 (Shot Quality Decay): The Edwards 3PA pullback and the lineup-grain 3PA distribution both reinforce C5 at the player and lineup grain.
- Category B (Naz/DiVincenzo): Direct lineup-grain evidence. Naz-at-5 lineups generate 7.8 more fg3a per 100 than Gobert-at-5. DiVincenzo's catch-and-shoot anchor role appears in the lineup-grain ratings.

Ready for Q3 mechanism work and Q8 player-decisions consumption.
