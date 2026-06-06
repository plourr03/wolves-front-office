# Q0D v1: Coaching system analysis

**Date:** 2026-05-17
**Status:** Q0D v1. Tests whether the Wolves' offensive system shifted between 2023-24 and 2025-26 in ways that explain the team's offensive decline.
**Source:** Synergy team and player play-type data (`nba_synergy_team_play_types`, `nba_synergy_player_play_types`), 2022-23 through 2025-26 regular season.

## Headline

**Three findings, one of which is a meaningful Q5 update:**

1. **The allocation shift is real.** From 2023-24 to 2025-26 RS, the Wolves moved possessions away from designed actions (Spot-up -4.3pp, PR-Ball-Handler -1.3pp, PR-Roll-Man -1.4pp, Cut -0.9pp) toward Isolation (+2.2pp) and Transition (+4.1pp). The "designed" share of possessions dropped from 61.9% to 56.1%.

2. **The allocation shift's impact on team-level ORtg is small.** Restoring 2023-24 allocation with current personnel/efficiency would gain only **+0.35 points of ORtg per 100 possessions**. Restoring 2024-25 allocation: **+0.18 points**. Both far below the spec's "+2 points" threshold for Path 3 having strong empirical support. **The allocation matters less for team ORtg than the LAFI v1 framing implied.**

3. **Gobert's PR-Roll-Man volume dropped 41% from 2023-24 to 2025-26 (188 → 111 possessions).** This is the largest single role change for any Wolves rotation player. His PR-Roll-Man PPP stayed elite (1.27 in 2025-26). The team is calling roll plays less, which mechanically reduces Gobert's offensive RAPM contribution even though his per-action efficiency is intact. **This finding directly explains the Gobert career-arc chart's offensive RAPM decline.**

**Verdict per the spec's five-option framework: "Allocation-shifted" (option 5) is the right label, BUT with the critical addition that the allocation impact ceiling is small.** Path 3's prescription is genuine but not load-bearing. The Wolves can't system-restore their way back to elite offense; the personnel reality matters more.

## 1. Team allocation evolution (RS, 4 seasons)

| Play type | 2022-23 | 2023-24 | 2024-25 | 2025-26 | Δ 23→25 |
|---|---|---|---|---|---|
| Spot-up | 25.2% | **27.2%** | 25.6% | **22.9%** | **-4.3pp** |
| Transition | 17.9% | 14.9% | 15.3% | **19.0%** | **+4.1pp** |
| PR-Ball-Handler | 15.3% | 14.4% | 16.3% | **13.1%** | **-1.3pp** |
| Isolation | 7.0% | 7.4% | 7.8% | **9.6%** | **+2.2pp** |
| Cut | 6.5% | 6.1% | 5.9% | 5.2% | -0.9pp |
| PR-Roll-Man | 5.0% | 5.6% | 5.7% | **4.2%** | **-1.4pp** |
| Off-Rebound | 5.1% | 5.2% | 5.8% | 5.6% | +0.4pp |
| Misc | 5.9% | 5.2% | 4.8% | 5.5% | +0.3pp |
| Off-Screen | 4.5% | 4.8% | 4.9% | 5.0% | +0.2pp |
| Hand-off | 4.4% | 3.8% | 4.5% | 5.7% | +1.9pp |
| Post-up | 3.1% | 5.4% | 3.3% | 4.1% | -1.3pp |

**Designed vs individual aggregation:**

| Season | Designed (Cut+OffScreen+HO+PRBH+PRRM+Spotup) | Individual (Iso+Postup) | Off-ball motion (Cut+OffScreen) |
|---|---|---|---|
| 2022-23 | 60.9% | 10.1% | 11.0% |
| 2023-24 | **61.9%** | 12.8% | 10.9% |
| 2024-25 | 62.9% | 11.1% | 10.8% |
| 2025-26 | **56.1%** | 13.7% | 10.2% |

The "designed" share dropped 5.8 percentage points from 2023-24 to 2025-26. Off-ball motion (Cut + OffScreen) was flat across all four years at ~10-11% (confirming LAFI v1's allocation-not-actions finding).

## 2. The allocation restoration impact (the central Q0D finding)

The spec's central question: if the team held 2025-26 personnel and efficiency but restored 2023-24 allocation, what would the projected ORtg gain be?

**Method:** for each play type, take 2025-26's PPP. Apply 2023-24's possession allocation. Compute the difference between the two weighted PPP totals. Multiply by 100 to express in ORtg points.

| Reference allocation | Current personnel | Expected ORtg change |
|---|---|---|
| 2023-24 | 2025-26 | **+0.35 points per 100 possessions** |
| 2024-25 | 2025-26 | **+0.18 points per 100 possessions** |

**Both numbers are far below the spec's +2-point threshold for "Path 3 has empirical support."**

### Detail: where the +0.35 comes from

| Play type | 2023-24 % | 2025-26 % | Δ% | Current PPP | Contribution |
|---|---|---|---|---|---|
| Spot-up | 27.2% | 22.9% | +4.3pp | 1.118 | **+0.048** (positive) |
| Transition | 14.9% | 19.0% | -4.1pp | 1.167 | **-0.048** (negative) |
| Isolation | 7.4% | 9.6% | -2.2pp | 0.965 | -0.021 |
| Cut | 6.1% | 5.2% | +0.9pp | 1.176 | +0.011 |
| Postup | 5.4% | 4.1% | +1.3pp | 0.989 | +0.013 |
| PR-Roll-Man | 5.6% | 4.2% | +1.4pp | 1.164 | +0.016 |
| PR-Ball-Handler | 14.4% | 13.1% | +1.3pp | 0.882 | +0.012 |
| Hand-off | 3.8% | 5.7% | -1.9pp | 0.985 | -0.019 |

**Why the impact is small:** the Spot-up reduction (-4.3pp) is almost exactly offset by the Transition increase (+4.1pp). Both are high-PPP play types (~1.12-1.17). Trading one for the other is approximately net-neutral in team ORtg.

The Isolation increase costs about -2 ORtg points if reverted (Iso is the lowest-PPP common play type at 0.965). The PR reductions and Cut reduction collectively cost about +4 ORtg points if reverted.

Net: small positive but well under the +2-point threshold.

**This is the v1 finding that updates the Q5 framing.** Path 3 (system change to restore allocation) has limited ceiling. The Wolves can't system-restore their way back to elite offense.

### Caveat on this finding

The analysis assumes:
- Current 2025-26 PPPs per play type would hold under a restored allocation
- The allocation can be restored without personnel changes

Both are simplifications. Restoring allocation MIGHT improve per-play-type PPP (because the actions would be better-supported in a designed system) or MIGHT decrease per-play-type PPP (because current personnel can't execute the actions as well). The +0.35 is the directional estimate at constant PPP; the realistic range is probably -1 to +2 points depending on how the second-order effects play out.

The directional finding (allocation impact is small) is robust. The exact magnitude is uncertain.

## 3. Gobert's role decomposition (the player-level explanation)

Gobert's individual play-type involvement by season:

| Play type | 2022-23 | 2023-24 | 2024-25 | 2025-26 |
|---|---|---|---|---|
| **PR-Roll-Man** | 145 | **188** | 162 | **111** |
| Cut | 234 | (data gap) | 226 | 196 |
| Off-Rebound | 173 | 198 | 192 | 200 |
| Postup | 81 | 92 | 22 | 18 |
| Transition | 69 | 64 | 61 | 91 |
| Misc | 78 | 94 | 55 | 75 |
| Spot-up | 27 | (data gap) | (data gap) | 12 |

**The PR-Roll-Man finding is the key:** Gobert's roll-man volume dropped 41% from 2023-24 (188) to 2025-26 (111). His PPP on the action stayed elite (1.27 in 2025-26, his second-highest of the four years).

Other role changes:
- **Post-ups collapsed** (92 → 18). The team has stopped using Gobert as a post option.
- **Cuts roughly stable** (~200-230). Off-ball motion is preserved.
- **Off-rebounds increasing** (173 → 200). He's getting more put-back opportunities.
- **Transition possessions rising** (64 → 91). Faster pace deployment.

### Why this matters for the Gobert career arc chart

The chart from `04_gobert_career_arc_chart.md` showed Gobert's offensive RAPM dropping from +2.70 (2023-24) to -3.20 (2025-26). This Q0D finding explains the mechanism: **the team is using Gobert less as a roll-and-finish piece.** His per-action efficiency is intact; his volume in his most productive offensive role has been cut nearly in half.

Critical implication for Q5: **if the team restored Gobert's PR-Roll-Man volume to 2023-24 levels (188 possessions, +77 over 2025-26), at his 2025-26 PPP of 1.27, that's +98 points across the season.** Spread over the team's ~8000 RS offensive possessions, that's +1.2 ORtg points. Concentrated in Gobert-on lineups specifically, the impact would be larger.

This is a more specific finding than the overall allocation restoration (+0.35). The Gobert-specific allocation restoration has more leverage than the team-wide allocation restoration.

## 4. Edwards' role shift (secondary finding)

| Play type | 2022-23 | 2023-24 | 2024-25 | 2025-26 |
|---|---|---|---|---|
| Isolation | 17.6% | 17.5% | 19.6% | **23.8%** |
| PR-Ball-Handler | 27.6% | 28.6% | **33.3%** | **23.5%** |
| Transition | 21.2% | 18.2% | 15.1% | 14.7% |
| Post-up | 1.7% | 3.4% | 1.7% | 5.8% |
| Spot-up | 15.1% | (data gap) | 11.0% | 12.8% |

**Edwards' PR-Ball-Handler usage dropped 10 percentage points from 2024-25 to 2025-26 (33.3% → 23.5%).** His Isolation rose 4.2pp. This is a major role shift for the team's primary creator in a single year.

The team is asking Edwards to iso more and run PR less. Possible explanations:
- Randle's role expanded, taking some primary-creator possessions
- Edwards' injury required simpler primary actions
- Coaching choice to maximize Edwards' iso ability

Edwards' iso PPP in 2025-26 was 1.036 (very good for high-volume iso). His PR-Ball-Handler PPP was lower. So the shift may be efficient at the per-action level. But it changes the team's overall complexion: more standstill watching Edwards iso, less screen-and-roll action that creates Spot-up opportunities for others.

This connects to the team-wide 3PA decline. Edwards-iso possessions generate fewer kick-out 3PA than Edwards-PR possessions. The team-level 3PA rate dropping is partially attributable to Edwards running less PR.

## 5. Randle's role (the personnel question)

| Play type | 2022-23 | 2023-24 | 2024-25 | 2025-26 |
|---|---|---|---|---|
| Isolation | 20.5% | 12.9% | 13.4% | **16.6%** |
| Postup | 8.9% | 15.9% | 12.1% | 9.9% |
| Spotup | 24.5% | 20.3% | 24.0% | 21.2% |
| Transition | 14.6% | 16.4% | 14.1% | 16.6% |
| PR-Ball-Handler | 6.7% | 10.3% | 7.5% | 9.4% |

Randle's 2024-25 to 2025-26 isolation rate rose +3.2 percentage points (13.4% → 16.6%). His post-up rate fell -2.2pp. He's iso'ing more, posting less.

His isolation PPP in 2025-26 was 0.943 (decent for a high-volume isolator but below average for a high-usage 4). His post-up PPP was 1.013 (better per-action but less variety of looks).

**The personnel-driven case:** Randle isn't a screener that opens space the way KAT was. His preferred actions are iso and post-up. The team's iso rise is partly Randle running his preferred actions more.

**The system-driven case:** Same personnel running different actions = coaching choice. Randle COULD be used more as a PR-Ball-Handler (he was 10.3% in 2023-24 when he was on the Knicks; he's been 7.5-9.4% in MIN). The coaching staff chose to deploy him differently.

The data supports both interpretations. The 2024-25 Randle's iso freq was 13.4% (during the WCF run year on MIN). The 2025-26 jump to 16.6% is the meaningful shift. Whether that shift was forced or chosen is the system-vs-personnel question Q0D was supposed to answer; the data doesn't cleanly resolve it.

## 6. The Q0D verdict (per the spec's five-option framework)

The spec offered five verdicts. My assessment:

1. **Stale (not adapting to modern league trends):** PARTIALLY SUPPORTED. The 2025-26 system runs more iso and less PR than the 2023-24 system. League trends are toward more PR and Spot-up. The Wolves are drifting against the league.

2. **Personnel-constrained (would be fine with right players):** PARTIALLY SUPPORTED. The Randle iso rise is plausibly personnel-driven. KAT was a different kind of player and the system worked better with him.

3. **Both (needs refresh AND new players):** SUPPORTED. The verdict the data most clearly supports.

4. **Neither (the diagnosis is elsewhere):** NOT SUPPORTED. The allocation shift is real.

5. **Allocation-shifted (same actions, different choices, no actions missing):** SUPPORTED with a critical caveat. The actions are still in the playbook (off-ball motion held flat at 10.2-10.9%; OffScreen flat at 4.5-5.0%). The calling has shifted toward iso and transition. **But the allocation shift's impact on team ORtg is small (+0.35 if reverted), so this verdict alone doesn't carry a strong prescription.**

**Composite verdict:** The 2025-26 system is allocation-shifted (option 5) on top of personnel-constrained (option 2). The system change is real but the marginal-ORtg ceiling is small. The bigger lever is personnel: getting Category B back (DiVincenzo recovery, Q5 Path 2 acquisition), restoring Edwards' health, and possibly restoring Gobert's roll-man volume specifically.

## 7. Implications for Q5

**Path 1 (Edwards development):** Modestly supported by Q0D. Edwards' role shift to iso-heavy in 2025-26 is something the system can address. If the team can call more Edwards PR plays in 2026-27, both his individual production and the team's Spot-up generation likely improve.

**Path 2 (Category B catch-and-shoot acquisition):** No change from prior recommendation. Still the highest-priority path.

**Path 3 (system change to restore allocation):** **DOWNGRADED.** The allocation restoration impact is +0.35 ORtg points, well below the +2-point threshold the spec set for "Path 3 has empirical support." Path 3 is a real prescription but its ceiling is low. **Q5's prescription should weight Paths 2 and 1 more heavily.**

**Path 4 (frontcourt restructuring):** Q0D doesn't directly address this. The Randle iso rise is partly personnel-driven, which weakly supports the trade case. But the v2 Randle finding (neutral RAPM in 2025-26 only) and the Gobert finding (still positive contributor) keep Path 4 weakly supported overall.

### A new Q5 sub-path the data suggests

The Gobert-specific finding (PR-Roll-Man volume down 41%) suggests a Q5 sub-prescription that wasn't in the original three-path framework:

**Sub-path 3a: "Restore Gobert's roll game specifically."** Independent of overall allocation, the team could design more PR-Roll-Man for Gobert specifically. His PPP on the action is intact (1.27). Adding 50-77 PR-Roll-Man possessions for him at 1.27 PPP across the season = +0.6 to +1.0 ORtg points concentrated in his minutes. This isn't system-wide change; it's a targeted role restoration.

**Calibrated Gobert offensive RAPM recovery estimate (combining 3a + Path 2):** the realistic range is **1-3 RAPM points** depending on execution:
- **+3 RAPM ceiling:** DiVincenzo recovers to 2024-25 form + Category B acquisition lands + Gobert PR-Roll-Man volume restored to 2023-24 levels (188 possessions). This recovers offensive RAPM from -3.20 toward 0 or modestly positive, returning net RAPM toward +4.
- **+1 to +2 RAPM realistic case:** DiVincenzo partial recovery + modest Category B addition + Gobert PR-Roll-Man volume partially restored (say 140 possessions). Recovers offensive RAPM toward -1, net RAPM toward +3.
- **+0 to +1 RAPM floor case:** DiVincenzo minimal recovery + no Category B added + system stays where it is. Offensive RAPM stays around -2 to -3, net RAPM around +2.

The +3 ceiling is plausible but not expected. The realistic Q5 framing should plan for +1 to +2 as the expected recovery and treat +3 as the optimistic case.

## 7b. Note for later: the McDaniels question

The Gobert career-arc chart triggered the Q0D analysis. McDaniels has a similar but smaller-magnitude finding that the project hasn't engaged with yet: his RAPM at -0.62 on a $24.4M salary is a -1.62 surplus vs his salary tier threshold. He's locked in through 2028-29 at $108M guaranteed, so he's not tradeable, but his production trajectory matters for the team's expected 2026-27 value.

A McDaniels career-arc chart (analogous to the Gobert chart) is a useful future visualization. His defensive reputation is strong but his RAPM doesn't fully capture it. Either his defensive value is real and the metric is missing it, or the team has a player-development question.

Not urgent for Q5 v1, but flagged for the project record. The eventual final deliverable should at minimum acknowledge the McDaniels surplus question rather than ignore it.

## 8. What this addendum does NOT do

- **Same-lineup play-type comparison.** The spec called for lineups that played in both 2023-24 and 2024-25 to see if their play-type frequency changed. Would isolate system from personnel more cleanly. Not built (requires possession-level play-type tagging that Synergy doesn't provide directly at the lineup grain).
- **Multi-action possession analysis.** Spec called for tracking chained actions (PnR → flare → catch-and-shoot). Requires the action classifier from Q3 spec which hasn't been built.
- **League comparison.** Where does the Wolves' play-type composition rank vs other 2025-26 teams? Not built.
- **Tracking-data measures.** Passes per possession, off-ball screens per 100, distance traveled. Not pulled in v1.
- **2024-25 vs 2025-26 same-personnel comparison for non-Randle changes.** Would help isolate "what's not personnel" vs "what is personnel."

These would sharpen Q0D's verdict and quantify the system-vs-personnel split more precisely. For Q5 prescription purposes, the v1 findings are sufficient.

## 9. The clean Q0D story

**Was Finch's system "stale" or "personnel-constrained"?**

Both, but the data suggests the personnel side dominates. The Wolves shifted allocation (Iso up, Spot-up down, PR-Roll-Man for Gobert down) but the **team-level ORtg impact of that shift is small (~0.35 points).** Reverting to 2023-24 allocation wouldn't recover much.

The bigger lever is personnel and role-specific deployment. The Q5 prescription should focus on:
1. Getting Category B back (DiVincenzo recovery + Q5 Path 2 acquisition)
2. Restoring Gobert's PR-Roll-Man role specifically (the targeted Sub-path 3a)
3. Restoring Edwards' PR-Ball-Handler role from 2024-25 levels (his role shift may be reversible)

The "stale" framing was partly right but the impact is small. The "personnel-constrained" framing dominates. The system can be improved at the margins but the big gains come from roster moves.

## 10. Artifacts

```
analyses/q0d_coaching_system/
  play_type_evolution.py            driver

outputs/tables/q0d_coaching_system/
  team_allocation_by_season.csv     team play-type frequency 2022-23 to 2025-26
  team_ppp_by_season.csv            team PPP per play type per season
  designed_vs_individual.csv        aggregated designed/individual splits
  allocation_restoration_impact.csv  detail for the +0.35 ORtg calculation
  allocation_restoration_2024to2025.csv  2024-25 → 2025-26 version
  gobert_play_type_freq.csv         Gobert role frequency per season
  gobert_play_type_poss.csv         Gobert role raw possessions per season
  gobert_play_type_ppp.csv          Gobert PPP per play type per season
  randle_play_type_freq.csv         Randle role frequency per season
  edwards_play_type_freq.csv        Edwards role frequency per season
```

Re-runnable: `python -m analyses.q0d_coaching_system.play_type_evolution`.

## 11. Status

Q0D v1 complete with one finding that updates the Q5 path framework: the allocation shift's impact on team ORtg is small, so Path 3 (system change to restore allocation) has a lower ceiling than the LAFI deliverable's framing implied. The Gobert-specific PR-Roll-Man volume drop (41%) is a real and explainable mechanism for his offensive RAPM decline; targeting that role restoration is a higher-leverage sub-prescription than overall allocation restoration.

Combined with the prior session's findings, the project's Q5 framework now leans toward Paths 1 and 2 as the primary prescriptions, with Path 3 narrowed to specific role-restoration (Gobert PR-Roll-Man; possibly Edwards PR-Ball-Handler) rather than broad system overhaul.

Ready for Q3 (mechanism analysis) per the data scientist's sequence. The Spurs-specific 3PA collapse remains the open mechanism question for the playoff postmortem.
