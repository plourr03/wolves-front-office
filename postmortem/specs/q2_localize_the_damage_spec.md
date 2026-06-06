# Q2: Localize the Damage Specification

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q2
**Status:** Specification, revised post-LAFI v1 (2026-05-17, minor)
**Position in stack:** Second tactical diagnostic, follows Q1. Feeds Q6, Q8, and Q5.

**Revision note:** Q2's lineup heatmap and on/off approach is preserved. Minor additions: iso-per-100-possessions per lineup (tracking the LAFI allocation problem at the lineup grain), and a reframing of the Gobert-vs-Naz comparison to engage with LAFI's Category B finding (Naz's catch-and-shoot shooting is a structural Category B asset).

---

## 1. The thesis

### 1.1 The question

Given the team-level decline identified in Q1, which specific lineups, player combinations, and individual players are responsible?

Q1 answered "what broke?" at the team level. Q2 answers "who broke it?" at the personnel level. The combination of Q1 and Q2 gives a precise picture: not just that the offense is underperforming, but that it's underperforming specifically in lineups containing X and Y, or specifically when player Z is on the floor.

### 1.2 Why this matters

Front offices have to make personnel decisions: who to play more, who to play less, who to trade, who to extend. Those decisions can be made on intuition or they can be made on evidence. Q2 produces the evidence.

The specific value of lineup-level analysis is that it captures fit and interaction effects that individual stats don't. A player can have good individual numbers while consistently being on the floor for bad team performance, because his style doesn't fit his teammates'. Lineup data exposes this. Without it, you'd never see it.

The specific value of on/off splits is that they capture marginal impact independent of any narrative about the player. A player can look bad on the box score but his team gets demonstrably worse when he sits. Or vice versa. The eye test misses both directions.

### 1.3 The Wolves-specific working hypotheses

Before running the data, document the hypotheses we'll test:

- **The Conley-Ant-McDaniels-Randle-Gobert starting five is the worst playoff lineup the Wolves have run.** Specifically because Gobert and Randle together create offensive spacing problems and Gobert in drop coverage isn't solving the modern offensive bigs.
- **Naz-at-the-5 lineups significantly outperform Gobert-at-the-5 lineups on offense.** Big enough margin that the defensive cost is debatable.
- **Edwards-without-a-secondary-creator lineups crater the offense.** Specifically, lineups with Ant + four non-creators get blitzed and trapped, and the offense has no answer.
- **Randle's individual playoff production is worse than his regular season.** Historically true; we're testing whether it's true again in 2025-26.
- **Gobert's individual on/off is worse than in past playoff years.** Hypothesis: the league has continued to evolve toward styles that exploit drop coverage, and Gobert's marginal impact has continued to shrink.

We test all of these honestly. Pre-committing to them is exactly the trap to avoid.

---

## 2. The data structure

### 2.1 Lineup-level data

**Five-man lineups:**
- Net rating, offensive rating, defensive rating, pace
- Minutes played
- Possessions played
- Four factors
- Halfcourt offensive rating specifically
- **Iso possessions per 100 possessions, per lineup (post-LAFI addition).** Tracks where the LAFI-identified iso allocation problem is concentrated by lineup. Critical for identifying which units are responsible for the year-over-year shift from PR-Ball-Handler to iso.
- Filter: minimum 20 possessions for inclusion in main analysis

**Two-man combinations:**
- Same metrics
- Focus on combinations involving Edwards, Gobert, Naz, Randle, McDaniels
- Filter: minimum 100 possessions

**Three-man combinations:**
- Same metrics
- Focus on the core trio (Edwards + frontcourt partners)
- Filter: minimum 100 possessions

### 2.2 Individual on/off data

For each rotation player:

- Team net rating with player on
- Team net rating with player off
- On/off differential
- Same splits for offense and defense
- Same splits for halfcourt offense specifically
- Regular season and playoffs separately

### 2.3 The "with or without you" matrix

For each pair of rotation players, compute net rating when both are on the floor vs when one is on and the other is off:

```
                        Both on      A on, B off    A off, B on    Both off
Ant + Gobert             X              Y                Z              W
Ant + Naz                X              Y                Z              W
Randle + Gobert          X              Y                Z              W
Randle + Naz             X              Y                Z              W
...
```

The pattern in these cells reveals which pairs work together vs separately.

### 2.4 Individual production stats

**Box score:**
- Standard counting stats (points, rebounds, assists, stocks, turnovers)
- Shooting splits (FG%, 3PT%, FT%, TS%, eFG%)
- Usage rate
- Assist rate, turnover rate

**Advanced:**
- BPM, EPM
- PIE
- Plus-minus
- Estimated wins
- Defensive impact metrics where available

**Playoff specific:**
- All of the above in playoff samples
- Year-over-year playoff trends for established veterans (Gobert, Conley, Randle especially)

### 2.5 Time periods

For all of the above:
- 2025-26 regular season
- 2025-26 playoffs to date
- 2024-25 playoffs (for year-over-year reference)
- 2023-24 playoffs (the WCF run, for "best recent version" reference)

---

## 3. The math

### 3.1 Sample size and noise

Lineup data is famously noisy. A five-man lineup with 50 possessions has wide confidence intervals on its net rating. Three principles for handling this:

**Use possession thresholds.** A lineup with under 20 possessions is essentially noise. Don't draw conclusions from it.

**Bootstrap confidence intervals.** For lineups with enough sample, bootstrap CIs are essential. A lineup with a net rating of +5 and a 95% CI of [-12, +22] is not meaningfully better than zero.

**Hierarchical priors.** Where possible, use a hierarchical Bayesian approach: shrink each lineup's net rating toward the team average, with shrinkage proportional to sample size. Small-sample lineups get pulled heavily toward the team mean. Large-sample lineups stand on their own. This is more statistically defensible than raw on/off but more work to implement. Optional for v1.

### 3.2 Computing on/off

On/off differentials are sensitive to lineup composition. If Player X is always on the floor with the best teammates and off the floor with the worst teammates, his on/off will look amazing for reasons that have nothing to do with him.

Two ways to handle this:

**Raw on/off:** Just compute team net rating with the player on vs off. Easy, interpretable, but confounded.

**Adjusted on/off (RAPM-style):** Use regularized regression to estimate each player's marginal impact, controlling for who else is on the floor. More defensible. Requires a multi-year sample for stability.

For Q2, my recommendation: compute raw on/off as the headline metric (because it's interpretable and what most readers understand), but also show RAPM estimates where available as a robustness check. If the two diverge significantly for a player, that's worth investigating.

### 3.3 Computing With-or-Without-You

For pairs of players, the WOWY matrix is:

```
NR(both_on) - NR(A_on, B_off) = marginal impact of B given A is on
NR(both_on) - NR(B_on, A_off) = marginal impact of A given B is on
```

These two numbers tell us how A and B complement each other. If A makes B better and vice versa, they're a good pair. If one makes the other worse, there's an interaction problem.

### 3.4 Statistical significance

For each meaningful comparison (lineup X vs lineup Y, player A on vs off), report:
- Point estimate
- 95% confidence interval (bootstrap)
- Whether the difference is statistically distinguishable from zero

Don't bury comparisons that aren't statistically meaningful. Report them honestly.

---

## 4. The lineup heatmap

The most important visualization in this analysis. A 2D heatmap:

- Rows: Wolves' five-man lineups, sorted by minutes
- Columns: each playoff game
- Cells: net rating per 100 possessions for that lineup in that game

Or alternatively, a different version:

- Rows: Edwards' frontcourt partners (Gobert, Naz, Randle, etc.)
- Columns: Edwards' backcourt/wing partners (Conley, McDaniels, DiVincenzo or recent equivalent, etc.)
- Cells: net rating for the lineup configuration

This visualization makes the lineup performance landscape immediately legible.

---

## 5. The diagnostic questions to answer

After the data is pulled, ask these specific questions:

### 5.1 Which Wolves lineups have been the best and worst in the playoffs?

The headline question. Identify the top 5 best lineups (by net rating, with minimum minutes) and the 5 worst. Note the personnel patterns.

### 5.2 Does the Gobert vs Naz at the 5 question have a clean answer? (Expanded post-LAFI)

Compute all minutes with:
- Gobert at the 5
- Naz at the 5

Compare team net rating, offensive rating, defensive rating in each configuration. The hypothesis to test: Naz-at-the-5 is much better offensively and only slightly worse defensively, making the net difference favor Naz. If true, this is a major finding. If false, Gobert is more valuable than the eye test suggests.

**LAFI framing (post-replan).** Naz at the 5 provides one form of Category B protection (a stretch big who can catch-and-shoot at 38.1%). Gobert at the 5 provides rim protection but no shot-quality manufacturing for the off-ball players. The trade-off is more LAFI-relevant than the original spec framed: it is not just an offense-vs-defense lineup question, it is a Category B vs rim-protection structural choice. The Q2 analysis should explicitly engage with this framing because Q8 (Gobert and Randle decisions) consumes it directly.

Specifically: compute the difference in catch-and-shoot 3PA per 100 possessions for the team between Gobert-at-5 and Naz-at-5 lineups. If Naz lineups generate substantially more catch-and-shoot opportunities (because his shooting pulls a defender out of the paint and opens kick-outs), that is direct evidence of Category B mechanism in lineup form.

### 5.3 Does Edwards' on/off differ significantly with different partners?

Specifically: Edwards-with-Gobert vs Edwards-with-Naz, in terms of team performance. Same for Edwards-with-Conley vs Edwards-without-Conley. This isolates which pairings are doing the work.

### 5.4 Has Randle declined?

Compare Randle's individual production from 2024-25 playoffs to 2025-26 playoffs. Has his TS% dropped? Is his usage being maintained but at lower efficiency? Are his assist numbers up or down? This is a calibration on whether the Randle acquisition has been a one-year peak or a sustained contribution.

### 5.5 What's happening to Gobert specifically?

Compare Gobert's individual metrics across the past three playoff runs. Is his defensive rebounding down? Is his rim protection (opponent FG% at the rim) down? Is he being targeted more in switches? This is the leading indicator of whether Gobert is declining or whether the system around him is failing him.

### 5.6 Where does Anthony Edwards stand?

Edwards is the only fully untouchable player on the roster. But that doesn't mean he's been perfect. Compare his playoff production to expectations:
- Has his usage been appropriate or too high/too low?
- His turnover rate has been concerning (4 TO in Game 5). Is this a pattern?
- His three-point shooting in playoffs vs regular season
- His on/off

Edwards is the engine. If the engine is fine, the failure is elsewhere. If the engine is struggling, the diagnosis changes.

---

## 6. The integration with other analyses

Q2 feeds Q3 (mechanism analysis), Q6 (KAT counterfactual), Q8 (Gobert and Randle decisions), and Q5 (prescription).

**To Q3:** The lineups that perform worst become the units to study in mechanism detail. If Lineup A is a -15 net rating, Q3 asks "specifically what's happening on the possessions in Lineup A?"

**To Q6:** The Randle lineup data is the foundation for the KAT counterfactual. Substitute KAT's projected impact into the Randle lineups.

**To Q8 (new):** Q8 consumes the Gobert vs Naz at the 5 comparison directly as the lineup-level evidence for the Gobert verdict. Q2's iso-per-lineup metric also feeds Q8's allocation analysis for Randle (which lineups concentrate Randle's iso usage).

**To Q5:** The pairings that work and don't work tell us what kinds of players need to be added or what kinds need to leave. Q2 also feeds Q5 with explicit lineup-level evidence of the LAFI allocation problem: the lineups where iso is heaviest become the units to focus on for the system-change Path 3.

---

## 7. Charts and visualizations

### 7.1 The Lineup Heatmap (centerpiece)

As described in Section 4. The visual centerpiece of Q2.

### 7.2 The Individual On/Off Ranking

A horizontal bar chart showing each rotation player's on/off differential, sorted. Quickly reveals who is helping and hurting at the margin.

### 7.3 The WOWY Matrix Chart

A grid visualization showing pairwise interaction effects. Players who lift each other are visually distinct from players who drag each other.

### 7.4 The Gobert vs Naz Comparison

A clean side-by-side bar chart of team performance with each at the 5. Includes offensive rating, defensive rating, and net rating.

### 7.5 The Edwards Configuration Chart

A small-multiples chart showing Edwards' team performance with various co-stars. Conley vs not Conley. Gobert vs Naz. Randle vs not Randle.

---

## 8. Sequencing

1. Pull all lineup data for 2025-26 (PBP-derived or NBA Stats)
2. Pull individual on/off data
3. Compute pairwise WOWY matrix
4. Compute all metrics with confidence intervals
5. Build the lineup heatmap
6. Run the diagnostic questions in Section 5
7. Write up findings

Estimated time: 5-7 days.

---

## 9. What I'm worried about

**Small samples in playoff lineups.** With 5-6 playoff games per round and limited rotations, some specific lineups won't have enough possessions to draw conclusions. Be honest about this.

**Lineup confounds.** Lineups that play together a lot are usually the starting unit, which means they face opposing starters. Garbage time lineups face opposing bench. Without opponent-quality adjustment, lineup net ratings are confounded. Mitigation: filter to non-garbage-time possessions and note when comparing lineups whose opponent contexts differ.

**The Gobert vs Naz comparison is politically loaded.** It's the single most contested question in Wolves fan discourse. Whatever the data says, present it with full context and uncertainty. Don't oversell.

---

## 10. Success criteria

**Minimum viable:** Clean lineup data with the top and bottom performing lineups identified, individual on/off rankings, and the Gobert vs Naz comparison with appropriate uncertainty.

**Strong:** Specific patterns identified (which player pairings work, which don't), with statistical confidence. Clear answer on the Gobert-Naz question. Edwards' performance contextualized.

**Stretch:** A non-obvious finding about lineup construction that the front office isn't currently considering. (E.g., "the Wolves' second-best lineup in playoff minutes is one they only play 4 minutes per game.")

---

End of specification.
