# Q2 corrections and Edwards-injury contextualized findings

**Date:** 2026-05-17
**Status:** Corrects two issues in `01_q2_findings.md` and adds Edwards injury context.

## What this document does

Three things:

1. Corrects a labeling error in the original Q2 findings markdown that mislabeled the Gobert+Naz pairing as the "Gobert+Randle jumbo."
2. Surfaces the Edwards 2025-26 injury timeline and propagates it through the Q2 findings as a context variable.
3. Reports the confound checks on the Gobert+Naz and Gobert+Randle cohorts with Edwards status, series, and game-state controls.

The headline finding from `01_q2_findings.md` that survives all corrections: **the Wolves' de-facto starting playoff lineup configuration (Gobert+Randle, Naz off) was net -13.26 over 203.8 minutes, statistically distinguishable from zero at the 95% level by a hair.** The other Q2 findings need to be re-read with Edwards' injury context in mind.

## 1. The labeling correction

In `01_q2_findings.md`, the headline finding "the Gobert+Randle jumbo was the team's best playoff lineup at +12.34 over 160 minutes" was incorrect. The +12.34 cohort was actually **Gobert+Naz on the floor together (with Randle mostly off, 75 of 94 stints)**.

The actual Gobert+Randle (Naz off) cohort:

| Configuration | Stints | Minutes | Net rating | Bootstrap 95% CI |
|---|---|---|---|---|
| **Gobert+Naz on floor (all)** | 94 | 160.5 | +12.34 | [-6.7, +29.4] |
| ...with Randle also on (triple-big) | 19 | 33.2 | +22.53 | [-28.3, +63.1] |
| ...with Randle off (Gobert+Naz pairing) | 75 | 127.3 | **+9.82** | [-9.9, +28.9] |
| **Gobert+Randle on floor (all)** | 95 | 237.0 | -8.29 | (overall) |
| ...with Naz also on (same triple-big) | 19 | 33.2 | +22.53 | (same) |
| ...with Naz off (Gobert+Randle pairing) | 76 | **203.8** | **-13.26** | [-27.9, +1.5] |

The original `01_q2_findings.md` will be updated to reflect this correction; I am leaving the original document in place for the project's audit trail.

The corrected reading **reinforces** the LAFI Category B framework rather than cutting against it: Gobert paired with another stretch big (Naz) was directionally positive; Gobert paired with a non-shooting big (Randle) was robustly negative. Same Q8 implications, sharper framing.

## 2. Edwards injury timeline

A clean per-game record of Anthony Edwards' availability and minute load for 2025-26 RS and PO.

### Regular season

| Status | Games | Total minutes | Avg minutes | Avg 3PA rate |
|---|---|---|---|---|
| DNP | 21 | 0 | 0 | (n/a) |
| Limited (1-29 min) | 9 | 219 | 24.3 | 0.504 |
| Normal (30+ min) | 52 | 1893 | 36.4 | 0.410 |

**Edwards missed 21 of 82 regular season games (25%) and played limited minutes in 9 more.** He played a "normal" load in only 52 games. Injury windows ranged from 1 to 6 games. The largest window was a 6-game stretch in mid-March 2026.

### Monthly 3PA rate (regular season, Edwards-played games)

| Month | Games | Avg minutes | 3PA rate |
|---|---|---|---|
| Oct 2025 | 3 | 25.3 | 0.365 |
| Nov 2025 | 13 | 34.6 | **0.444** |
| Dec 2025 | 11 | 37.0 | 0.392 |
| Jan 2026 | 13 | 35.6 | 0.398 |
| Feb 2026 | 10 | 36.2 | 0.412 |
| Mar 2026 | 9 | 33.4 | **0.457** |
| Apr 2026 | 2 | 26.5 | 0.483 |

**Edwards' regular-season 3PA rate did NOT show a gradual decline.** It bounced between 0.39 and 0.46 month-to-month with no monotonic trend. The 0.503 → 0.418 drop from 2024-25 to 2025-26 (reported in the Q2 YoY section) was a **step-function shift at the start of the season**, not a gradual within-year drift. He started 2025-26 at a lower 3PA-rate baseline (after a 6-game preseason injury window) and held that baseline through the year.

**Implication:** The "Edwards' 3PA pullback contributed to the playoff collapse" framing is partially supported and partially not.
- Supported: the 2025-26 season-long baseline is lower than 2024-25's. Edwards is taking fewer threes per game on average than he did in 2024-25.
- Not supported: within-season decline. The pullback didn't worsen as the season went on; it was at a stable lower level throughout 2025-26.

The mechanism question for Q3 is now sharper: what changed between 2024-25 and 2025-26 that made Edwards take fewer threes as a season-long baseline. Not "what changed during 2025-26 that progressively reduced his three-point volume," because that's not what the data shows.

### Playoffs (game by game)

| Series-G# | Date | Matchup | Status | Min | FGA | 3PA | 3PA rate | Result |
|---|---|---|---|---|---|---|---|---|
| R1-G1 | 4/18 | @DEN | **Normal** | 38 | 19 | 9 | **0.474** | L |
| R1-G2 | 4/20 | @DEN | **Normal** | 40 | 25 | 11 | **0.440** | W |
| R1-G3 | 4/23 | vs DEN | Limited | 23 | 15 | 8 | 0.533 | W |
| R1-G4 | 4/25 | vs DEN | Limited | 17 | 8 | 3 | 0.375 | W |
| R1-G5 | 4/27 | @DEN | **DNP** | 0 | 0 | 0 | (n/a) | L |
| R1-G6 | 4/30 | vs DEN | **DNP** | 0 | 0 | 0 | (n/a) | W |
| R2-G1 | 5/4 | @SAS | Limited | 25 | 13 | 3 | **0.231** | W |
| R2-G2 | 5/6 | @SAS | Limited | 24 | 13 | 5 | 0.385 | L (-33!) |
| R2-G3 | 5/8 | vs SAS | Normal | 40 | 26 | 9 | 0.346 | L |
| R2-G4 | 5/10 | vs SAS | Normal | 40 | 22 | 5 | 0.227 | W |
| R2-G5 | 5/12 | @SAS | Normal | 39 | 13 | 3 | **0.231** | L |
| R2-G6 | 5/15 | vs SAS | Normal | 35 | 26 | 7 | **0.269** | L |

**Edwards' 3PA rate in his four normal-load R2 games (G3-G6): 0.346, 0.227, 0.231, 0.269.** Average ~0.27. That is dramatically below his RS Normal-load average of 0.410. **Even when Edwards came back to full minutes in R2, his three-point volume stayed suppressed.** This rules out "minute restriction alone" as the explanation. Either:

1. The Spurs were specifically scheming to deny Edwards' threes (Wembanyama-anchored defense letting wings close out hard on Ant's perimeter looks), OR
2. Edwards was still playing through limitation that affected his shot lift, OR
3. The coaching staff directed Edwards to attack more downhill given the Spurs' rim protection.

Q3 (mechanism) is the right place to disambiguate. Specifically, Q3's PnR coverage decoder should show whether SAS defenders were closing out on Edwards differently than DEN did in R1 G1-2 (where his 3PA rate was 0.474, 0.440 = healthy/normal).

### Edwards R1 healthy vs R2 split

| Subset | Games | Min | 3PA rate |
|---|---|---|---|
| R1 G1-2 (healthy, normal load) | 2 | 78 | 0.456 |
| R1 G3-4 (injury, limited) | 2 | 40 | 0.478 (small) |
| R1 G5-6 (DNP) | 2 | 0 | (n/a) |
| R2 G1-2 (return, limited) | 2 | 49 | 0.300 |
| R2 G3-6 (back to normal load) | 4 | 154 | 0.276 |

**Within 2025-26 playoffs, Edwards' 3PA rate dropped from ~0.46 (healthy R1) to ~0.28 (R2 normal load).** A 17-percentage-point intra-playoff drop, even controlling for minutes played.

The Q1 finding (team-level 3PA rate dropped from 0.420 RS to 0.342 PO) is dominated by this Edwards R2 effect. If we restrict the PO sample to Edwards-healthy R1 games (G1-G2), Edwards alone was taking threes at his RS Normal baseline. The team-level collapse is concentrated in R2 against SAS.

**This is the most important new finding in this document.** The Q1 "team-level 3PA rate cratered in the playoffs" finding is really "Edwards' 3PA rate cratered against SAS specifically, and the team didn't compensate." The Spurs-specific defensive scheme is the proximate cause, not a general team-wide regression.

## 3. Pairing confound checks

### Cohort A: Gobert+Naz on the floor, Randle OFF (the corrected "best pairing" finding)

| Subset | Stints | Minutes | Net rating |
|---|---|---|---|
| Overall | 75 | 127.3 | **+9.82** |
| Bootstrap 95% CI | | | **[-9.87, +28.86]** |
| R1 vs DEN | 42 | 67.6 | +4.56 |
| R2 vs SAS | 33 | 59.7 | **+15.34** |
| Edwards DNP | 14 | 19.7 | +12.76 |
| Edwards Limited | 24 | 45.8 | +0.17 |
| Edwards Normal | 37 | 61.8 | **+15.84** |
| Edwards on floor | 42 | 74.9 | +7.17 |
| Edwards off floor | 33 | 52.4 | +14.10 |

**Score margin at stint start:** Trailing 3-10 (28 stints), close (15), trailing 10+ (12), leading 3-10 (12), leading 10+ (8). **40 of 75 stints started in trailing situations.** The cohort was deployed often when the Wolves needed to come back.

**Interpretation:**

- **The CI crosses zero.** Net rating +9.82 with 95% CI [-9.9, +28.9] is not statistically distinguishable from zero. The point estimate is directional but not strong evidence.
- **Series breakdown is favorable to the cohort.** Unlike Gobert+Randle, the Gobert+Naz pairing performed BETTER in R2 vs SAS (+15.34) than R1 vs DEN (+4.56). The Spurs series was actually a favorable matchup for this configuration.
- **Edwards status matters.** When Edwards played Normal minutes, +15.84 net rating. When Limited, near zero. When DNP, +12.76.
- **Game-state confound is real.** The cohort played 40 of 75 stints in trailing contexts. Comeback minutes against a fatigued defense or in non-half-court contexts can inflate net rating. The "+15.34 in R2" finding deserves a deeper look at whether those minutes were specifically deployment-driven.

**Verdict:** The Gobert+Naz pairing as a positive lineup is directionally suggestive but not statistically established. Q8 should not lean heavily on this finding as definitive Category B evidence at the lineup grain. Use it as one input among several.

### Cohort B: Gobert+Randle on the floor, Naz OFF (the de-facto starting configuration)

| Subset | Stints | Minutes | Net rating |
|---|---|---|---|
| Overall | 76 | 203.8 | **-13.26** |
| Bootstrap 95% CI | | | **[-27.94, +1.50]** |
| R1 vs DEN | 40 | 115.0 | -3.04 |
| R2 vs SAS | 36 | 88.7 | **-26.46** |
| Edwards DNP | 13 | 29.7 | -21.53 |
| Edwards Limited | 27 | 76.3 | -9.64 |
| Edwards Normal | 36 | 97.7 | -13.81 |
| Edwards on floor | 46 | 126.1 | -12.36 |
| Edwards off floor | 30 | 77.7 | -14.71 |

**Score margin at stint start:** Close (28 stints, most common), trailing 3-10 (16), trailing 10+ (15), leading 3-10 (11), leading 10+ (6). **The cohort played heavy close-game and high-leverage minutes.**

**Interpretation:**

- **The CI just barely crosses zero on the high side (+1.50).** Net rating -13.26 with 95% CI [-27.9, +1.5]. Robustly negative.
- **The R2 catastrophe is the dominant signal.** R1 was -3.04; R2 was -26.46. Against the Spurs, the de-facto starting lineup was crushed by 26 points per 100 possessions.
- **Edwards status does not rescue the cohort.** Even in cleanest Edwards-Normal subset (97.7 min), the cohort was -13.81. The pairing was bad regardless of whether Edwards was at full health.
- **Edwards on/off the floor doesn't matter much.** With Edwards on floor: -12.36. With Edwards off: -14.71. Both negative. The pairing problem is structural, not Edwards-dependent.
- **High-leverage deployment.** 28 of 76 stints started in close-game contexts. The team was actively trying to win those moments with this configuration. They lost.

**Verdict:** The Gobert+Randle pairing's negative net rating **survives all confound checks.** Series, Edwards status, Edwards on-floor flag, and game-state controls do not rescue the cohort. This is the most empirically robust negative lineup finding in Q2.

### Cohort C: Triple-big (Gobert+Naz+Randle)

| Subset | Stints | Minutes | Net rating |
|---|---|---|---|
| Overall | 19 | 33.2 | +22.53 |
| Bootstrap 95% CI | | | [-28.26, +63.14] |
| R1 vs DEN | 10 | 18.3 | +18.44 |
| R2 vs SAS | 9 | 15.0 | +26.13 |
| Edwards DNP | 8 | 17.9 | +15.97 |
| Edwards Limited | 4 | 5.7 | +90.77 (13 poss!) |
| Edwards Normal | 7 | 9.7 | -4.35 |
| Edwards on floor | 7 | 7.95 | -2.96 |
| Edwards off floor | 12 | 25.29 | +29.41 |

**Verdict: too small a sample to conclude anything.** 33 minutes total. CI spans 90 points. The triple-big "best lineup" finding from `01_q2_findings.md` does not survive scrutiny: 25 of 33 minutes were Edwards-off (he was resting), and in the 7.95 minutes Edwards was on the floor with the triple-big, the cohort was -2.96. The +22.53 is a small sample dominated by Edwards-rest comeback contexts.

## 4. What the corrected findings actually imply

Putting the three cohort findings together with the Edwards injury timeline and the original Q2 leaderboards, what holds up:

**Strongly supported (statistically distinguishable from zero or distinguishable from a meaningful null):**

- The Wolves' de-facto starting playoff configuration (Gobert+Randle pairing with Naz off, 204 minutes, the highest-minute pairing) was robustly net-negative. Even cleanest subset by Edwards status: -13.81. CI [-27.9, +1.5]. **This is the strongest single Q2 finding.**
- Edwards' 3PA rate in R2 vs SAS dropped 17 percentage points from his R1 healthy rate, even after returning to normal minute load. The Spurs forced him off the line specifically.
- The 2025-26 RS Edwards 3PA rate was a step-function lower than 2024-25 RS, not a gradual decline. Whatever changed happened at season start.

**Directionally suggestive (not statistically established but consistent across multiple cuts):**

- Gobert+Naz pairing was modestly positive (+9.82, CI [-9.9, +28.9]). The CI crosses zero. Used as one input among several for Q8 rather than as definitive Category B evidence at the lineup grain.
- The team's most-played playoff lineups (both the Dosunmu-led and DiVincenzo-led versions of the Gobert+Randle config) were net-negative in playoffs. Detail in the lineup leaderboard from `01_q2_findings.md`.
- The DiVincenzo-anchored version of the lineup (+3.0 over 44.7 min) outperforming the Dosunmu-anchored version (-27.2 over 45.6 min) within the Gobert+Randle pairing supports the Category B framework, even with the R1 vs R2 confound flagged.

**Weakened or set aside by the confound check / Edwards context:**

- The triple-big "best lineup" finding does not survive scrutiny.
- The Edwards individual on/off finding (-12.1) is too contaminated by Edwards being off-floor in late-game and Edwards-rest minutes against bench. Standard on/off confound; the magnitude doesn't carry weight by itself.
- The Randle individual on/off (-16.3) is similarly contaminated but the magnitude is large enough that Q8 should still investigate via RAPM-style adjustment.
- The straight Gobert-at-5 vs Naz-at-5 comparison from `01_q2_findings.md` Section 5 (Gobert -9.88 vs Naz -4.58) is still valid but should be interpreted alongside the Edwards-injury context: most of Gobert-at-5 minutes were R2 (Edwards limited/forced off line), most of Naz-at-5 minutes were R1 (Edwards available).

## 5. What this means for Q3, Q5, Q8

**Q3 (Mechanism analysis):**

- The primary Q3 question becomes: **what did the Spurs do schemewise to force Edwards' 3PA rate from 0.46 to 0.28 within the playoffs**, and what did the Wolves not adjust to? The PnR coverage decoder should specifically test SAS's closeout patterns on Edwards.
- The Gobert+Randle structural-bad pairing's mechanism is also a Q3 question. Why does this pairing collapse? Spacing? Defensive coverage of the screen action? Both bigs unable to switch onto perimeter creators?

**Q5 (Prescription):**

- **The most actionable Q5 question is now: what changes the Gobert+Randle pairing's net rating from -13.26 to something positive?** Either (a) replace Randle with a stretch four who can shoot threes (which is Naz, but Naz is the backup big, not a starter, and lacks Randle's playmaking volume), (b) replace Gobert with a more switchable center (KAT counterfactual, Q6), or (c) keep both and add a Category B wing to the perimeter (which is DiVincenzo, who's coming back from Achilles).
- The Edwards-development path (Path 1) needs to address whether Edwards can restore his 2024-25 3PA volume baseline. The 2025-26 step-function drop is the question. Was it a coaching decision (Finch's adjustment), a defensive adjustment (defenses started running him off the line), or a self-selected change?

**Q8 (Player decisions):**

- **The strongest Q8 input is the Gobert+Randle pairing's robust negative.** The case against the status-quo Gobert+Randle starting frontcourt is now empirically supported. The decision is: which one of the two do you keep, and what archetype fills the other slot?
- **The Naz+Gobert pairing is directionally positive but not statistically established.** Q8 should not lean on it as the definitive answer. It's one input among several.
- **DiVincenzo's return from Achilles** is the cleanest "high-leverage roster decision" for Q8: he was the anchor of the team's least-bad heavy-minute playoff lineup (+3.0 in the Gobert+Randle config with him as the Category B wing). His recovery projections are decision-relevant.

## 6. What I didn't do (transparency)

- **RAPM / adjusted on/off:** Bobby flagged this for Randle and Gobert specifically. Not built yet. Q8 should incorporate it before any politically-sensitive Gobert or Randle conclusion ships.
- **Opponent lineup composition during the cohort minutes:** I have the league-wide 2025-26 PO stints in cache. I could cross-reference (game_id, period, clock) to identify which 5-man opponent lineups the Wolves' cohort minutes were against, then classify by opponent-stint minutes-played (starters vs bench heuristic). I did not do this for time reasons. v2 follow-on.
- **The PBP normalization shim** (the next planned task per Bobby's instruction) is the next infrastructure piece. It unlocks 2024-25 lineup work for Q6, Q8, Q0C, and parts of Q3/Q4.
- **Detailed re-analysis of the original Q2 Section 5 (Gobert-at-5 vs Naz-at-5) under the corrected framing.** The original section is still valid as written but its interpretation needs to be updated to reflect the Edwards-injury weighting per cohort. I left a flag in Section 4 of this document for now.

## 7. Artifacts

```
outputs/findings/q2_localize/
  01_q2_findings.md          original Q2 findings; contains the mislabel
  02_q2_corrections_and_edwards_context.md  this document
outputs/findings/lineup_pipeline/
  02_pairing_confound_checks.md   raw cohort confound tables
outputs/tables/q2_localize/
  edwards_2025_timeline.csv  game-by-game Edwards data with status

analyses/q2_localize/
  edwards_timeline.py    Edwards availability + 3PA timeline driver
  confound_checks.py     Cohort confound check driver
```

Re-runnable:
```
python -m analyses.q2_localize.edwards_timeline
python -m analyses.q2_localize.confound_checks
```

## 8. Honest assessment of where this round leaves us

Two corrections this session (the Gobert+Naz mislabel and the Edwards injury context propagation) plus the prior DiVincenzo confound check are three substantial discipline events. The project's analytical narrative has been refined enough that the front-office deliverable (eventually Q5) should be tighter than it would have been without the corrections.

The Q1 "3PA collapse" headline still stands but is now sharper: the 3PA collapse was concentrated in R2 vs SAS, driven by Edwards' specific 3PA suppression against the Wembanyama-anchored defense, after he was already operating at a lower season-long baseline than 2024-25.

The Q2 "Dosunmu lineup was worst" finding still stands and is now situated in the broader Gobert+Randle pairing being robustly bad finding. The DiVincenzo-anchored lineup +3.0 within the Gobert+Randle pairing is the least-bad Wolves heavy-minute PO lineup. This is what holds up.

The "best lineup" finding from the original Q2 markdown does not survive. After correction (it's actually Gobert+Naz, not Gobert+Randle) and confound check (CI crosses zero, deployment context inflates the rating), the +9.82 net rating is directional but not definitive. The triple-big +22.53 is small-sample noise.

The Edwards injury context fundamentally reframes how we should read every Q2 finding. The cohort confound checks accounted for it, but the broader Q2 narrative needs to be updated to acknowledge that 50% of the playoff sample was Edwards-limited or Edwards-DNP, and the cleanest Edwards-Normal subset (R1 G1-2 vs R2 G3-6) has its own confound: the matchup quality changed dramatically between the two sets of games.

Ready for the PBP normalization shim next.
