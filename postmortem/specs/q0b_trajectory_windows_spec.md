# Q0B: Trajectory and Windows Specification

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q0B
**Status:** Specification, revised post-LAFI v1 (2026-05-17)
**Position in stack:** Meta-layer analysis, synthesis piece. Edwards trajectory now elevated to primary sub-analysis. Runs after Q7 (which provides comp evidence for Edwards' tier-leap probability).

**Revision note:** Per LAFI v1's identification of Edwards' developmental ceiling as the central variable for the prescription (Path 1: Edwards develops into Category A solo creator), Q0B Section 4.1 is expanded from a single sub-question to the primary sub-analysis of the spec. Other rotation players' trajectories become supporting context. Q0B's sequencing position is moved to after Q7 (which provides the historical comp evidence for the tier-leap probability).

---

## 1. The thesis

### 1.1 The question

Where is each Wolves rotation player on their individual development or decline curve, and what does that imply about the team's competitive window?

Q1-Q4 analyzed the team's current state. Q0B steps back and asks about trajectories. A team can look the same on paper from year to year but be drifting up or down because of player-level changes underneath. Understanding the trajectory is essential to roster construction decisions.

### 1.2 Why this matters

Three reasons.

First, every team has a competitive window. The window opens when the core is good enough to contend and closes when the core declines or breaks up. Knowing where you are in the window determines what kind of moves make sense. A team at the start of its window should preserve assets and develop. A team at the end of its window should spend assets to maximize the current season. A team in the middle should look for value-creating moves that extend the window.

Second, player development isn't linear. Young players don't always improve. Veterans don't always decline. The specific trajectory of each player on the roster is what determines team performance in coming years. A roster that looks good on paper but has multiple players nearing decline is a worse roster than it appears.

Third, this analysis directly informs Q5. The prescription is shaped by the window: aggressive moves vs patient moves vs rebuild moves.

### 1.3 The working hypothesis

The Wolves have a structural timeline mismatch. Edwards (24), McDaniels (25), Naz (26), and Beringer (very young) are in their development and prime years. Gobert (33) is in clear decline. Conley (mid-30s) is past prime. Randle (30) is at or just past prime. DiVincenzo (recovering from Achilles) is high risk.

The result: the team's young core is just starting its prime, but the veterans surrounding them are aging out. By the time Edwards is fully in his MVP-caliber peak (probably 2027-2029), Gobert will be 35 and likely well into decline, Conley may be retired, and Randle will be 32+.

This timeline mismatch is one of the most consequential structural issues facing the team.

**(Post-LAFI revision) Edwards trajectory is the central question.** Per LAFI v1's Path 1 framing, whether Edwards reaches the Luka/SGA tier of solo creation in the next two seasons determines whether the Wolves automatically receive Category A protection (his solo creation manufactures shot quality despite motion death). If he reaches that tier, the prescription becomes "support the Category A creator." If he plateaus at his current tier, the prescription depends on Path 2 (acquire Category B catch-and-shoot) and Path 3 (system change). Edwards' trajectory analysis is no longer one of six diagnostic questions; it is **the** central question of Q0B, with the other rotation players as supporting context.

---

## 2. The data structure

### 2.1 Individual player trajectories

For each rotation player, pull the last 3-5 seasons of:
- Box score production per 36 minutes
- Advanced impact metrics (BPM, EPM, LEBRON, etc.)
- Athletic indicators where available (speed, vertical from combine/tracking)
- Injury history

Annotate with age at each season.

### 2.2 Age curves

For each archetype, pull historical age curves:
- Defensive-anchor centers (Gobert's comp set)
- Combo bigs (Randle's comp set)
- Wings (McDaniels)
- Stretch fives (Naz)
- Star scoring guards (Edwards)
- Veteran point guards (Conley)

The historical curves show the expected trajectory at each age based on archetype. Then we can ask: where is each Wolves player relative to their archetype's expected curve? Ahead? On pace? Behind?

### 2.3 Contract status

For each player:
- Current contract year (year X of Y)
- Cap hit per season
- Player and team options
- Free agency timing

This determines who is locked in vs who is approaching a decision point.

---

## 3. The math

### 3.1 Building age curves

For each archetype, identify the historical comp population (e.g. "all defensive-anchor centers who played at least 5 seasons since 2000"). Compute their average production at each age, smoothed.

Output: an expected production trajectory by age for each archetype.

### 3.2 Comparing players to curves

For each Wolves player, plot their actual trajectory against their archetype's expected curve.

Categories of trajectory:
- Ahead of curve (player is producing more than archetype average at their age)
- On curve (producing roughly as expected)
- Behind curve (declining or stagnating earlier than expected)

This is the player-by-player evaluation.

### 3.3 Projecting forward

For each player, project forward 3 years. The projection uses:
- Their current trajectory (ahead, on, behind)
- Archetype age curves for the next 3 years
- Injury history adjustments

Output: expected production in 2026-27, 2027-28, 2028-29.

### 3.4 The window analysis

Aggregate the individual projections into team-level performance projections:

- Sum of expected impact metrics across the roster
- Bracket by year
- Identify the year of peak collective performance

Conclusion: is the Wolves' window 2026? 2027? 2028? Already closed?

### 3.5 Uncertainty

Individual projections have wide uncertainty. Express each projection as a range, not a point estimate. The team-level aggregate will also have a range.

---

## 4. The diagnostic questions

### 4.1 Is Edwards still ascending? (Primary sub-analysis, expanded post-LAFI)

Edwards is the franchise. His trajectory is the most important variable in the entire project, not just in Q0B. Per LAFI's Path 1 framing, his developmental ceiling determines whether the Wolves get Category A protection automatically. This sub-analysis is structured to answer that question specifically.

**Step 1: Year-over-year production trajectory.**

Pull Edwards' year-over-year metrics and document the curve:
- BPM, EPM, LEBRON, RAPM (whatever modern impact metrics are available)
- Usage rate, time-of-possession share, scoring rate
- True shooting percentage, three-point volume and accuracy
- Assist rate, turnover rate (playmaking development)
- Defensive metrics where available
- All splits regular season and playoffs separately

Output: a trajectory curve from rookie year through 2025-26. Is the curve still climbing, plateauing, or stabilizing?

**Step 2: Comparison to historical age-24 stars (depends on Q7 output).**

For each Q7 comp star, compare their age-24 production to Edwards' age-24 production:
- Were they ahead, on pace, or behind at the same age?
- For those who reached the Luka/SGA tier (top-10 in the league), what was their age-24 profile?
- For those who plateaued at the tier just below (Edwards' current tier), what was their age-24 profile?

This is the bridge to Q7. Q7's comp set provides the population of historical guards who were Edwards-like at this age. Q0B's Edwards analysis asks where Edwards sits in that distribution.

**Step 3: Probabilistic forecast of tier-leap.**

Based on the comp distribution and Edwards' trajectory, estimate:
- P(Edwards reaches Luka/SGA tier by end of 2026-27)
- P(Edwards reaches that tier by end of 2027-28)
- P(Edwards plateaus at current tier)

These are probabilistic estimates with wide intervals. Express each as a range (e.g., "P(tier-leap by 2027-28) is in the range of 25-45%, with point estimate 35%"). Document the basis for each probability.

**Step 4: Implications for the LAFI Path 1 prescription.**

If P(tier-leap by 2026-27) is high (above 60%), Path 1 is a credible primary plan and the prescription can rely on it.

If P(tier-leap by 2026-27) is moderate (30-60%), Path 1 is upside but the prescription should be built around Paths 2 and 3 with Path 1 as additional benefit.

If P(tier-leap by 2026-27) is low (below 30%), the prescription must explicitly assume Edwards stays at his current tier and Paths 2 and 3 carry the load.

This step directly feeds Q5's portfolio framing.

**Step 5: Specific trajectory signals to monitor.**

What specific in-game indicators would update the probability if observed in 2026-27? Examples:
- Usage rate climbing above 32% without efficiency drop
- True shooting percentage above 62%
- Playmaking growth (assist rate above 25% at his usage level)
- Iso PPP versus elite defenses
- Solo-creation possessions against blitzes (the Q3 finding)

These are the leading indicators. Document them so the front office can track Edwards' development in 2026-27 against the Q0B forecast.

### 4.1a Other rotation players (supporting context)

The original Q0B questions about Gobert, McDaniels, Randle, Conley, and the young development pieces are preserved as supporting context for the Edwards analysis. They are no longer the primary frame.

### 4.2 Is Gobert in clear decline?

Gobert at 33 is the biggest decline question. Specifically:
- Rim protection (opponent FG% at the rim with Gobert as nearest defender)
- Rebounding rates
- Mobility indicators
- Foul rates (older bigs typically foul more)

The expected answer: he's in decline but not yet collapsed. The question is the rate of decline.

### 4.3 Has McDaniels broken out yet, or is he still on the come?

McDaniels at 25 should be approaching his peak. Has he made the leap to All-Star-caliber two-way play, or is he still a complementary piece?

### 4.4 Where is Randle in his arc?

Randle at 30. His historical trajectory has been inconsistent (good years, bad years). At 30, the question is whether his 2024-25 contribution was a peak or a sustainable level.

### 4.5 Is there enough young development behind the core?

What's the trajectory for Shannon Jr., Beringer, and any other young players? Are they trending toward rotation pieces, starters, or non-contributors?

### 4.6 The window verdict (revised post-LAFI)

Synthesizing: when is the Wolves' window?
- Closed: the team peaked in 2023-24 and is in decline
- Open now: 2025-26 was the peak, with 2026-27 being roughly comparable
- Opening: the peak is still ahead (2027-29)
- Indeterminate: too much variance to forecast

**The Edwards-dependent verdict.** With LAFI's Path 1 framing, the window verdict depends heavily on Edwards' trajectory:

- **If Edwards reaches Luka/SGA tier by 2027-28:** the window is opening, peak is 2027-29. Even with Gobert and Conley aging out, Edwards as a Category A creator extends the window.
- **If Edwards plateaus at current tier:** the window is more constrained. The team is in a Path 2 + Path 3 contention window, which is narrower and depends on Category B catch-and-shoot acquisition.
- **If Edwards regresses (unlikely but possible):** the window is closing.

The window verdict is no longer "what is the team's peak year" alone; it is "what is the team's peak year conditional on Edwards' trajectory."

---

## 5. Charts and visualizations

### 5.1 The Player Trajectory Charts

For each rotation player, a line chart showing their year-over-year impact metric vs the archetype age curve.

### 5.2 The Window Forecast

A bar chart showing projected team strength (in terms of net rating or similar) for the next 3 seasons. Bars colored by confidence (wide ranges in lower-confidence years).

### 5.3 The Age Distribution

A bar chart of the current roster sorted by age. Visually shows the timeline mismatch.

### 5.4 The Contract Timeline

A Gantt-style chart showing each player's contract over the next 3-4 years. Visually shows when flexibility opens up and when decisions force themselves.

---

## 6. Sequencing (revised post-LAFI)

Q0B can be built relatively independently for the other rotation players. The Edwards primary sub-analysis depends on Q7's comp output.

**Sequencing position post-replan:** Q0B runs after Q7. Q7's comp set provides the population of historical guards who were Edwards-like at age 24. Q0B's Edwards analysis asks where Edwards sits in that distribution and forecasts his probability of reaching the Luka/SGA tier.

Within Q0B:
- Pull historical age curve data (one-time work). Can start in parallel with Q7.
- Pull Edwards' year-over-year trajectory. Can start in parallel with Q7.
- The probabilistic forecast of tier-leap (Step 3 of Section 4.1) requires Q7's comp distribution. Wait for Q7 here.
- The other rotation players' trajectories are Q7-independent. Build in parallel.

Estimated time: 1-2 weeks. The Edwards probabilistic forecast adds work relative to the original Q0B scope.

---

## 7. What I'm worried about

**Age curves are population averages.** Individual players deviate widely. Gobert might decline gracefully like Mutombo did or sharply like Dwight Howard did. The age curves give expected values, not predictions.

**Edwards' ceiling is highly variable.** A star player's ceiling has more variance than role players. Edwards could plateau at his current level or jump to MVP candidate. Both are plausible. The projection should reflect that wide range.

**Edwards trajectory is now the project's single most consequential prediction.** Per the post-LAFI replan, Path 1 in the prescription depends on this prediction. Be extra careful about projecting a leap that the data does not support, and equally careful about projecting a plateau that the data does not support. The honest framing throughout: probabilistic ranges, comp evidence, named uncertainty.

**Injury risk dominates everything for older players.** Conley's age makes him a much bigger injury risk than the production stats suggest. Gobert's mileage similarly. Account for this.

**DiVincenzo's Achilles is highly uncertain.** Achilles recoveries vary widely. Some players return to full form. Some never recover. The projection for DiVincenzo specifically should be very wide.

---

## 8. Success criteria

**Minimum viable:** Clear trajectories for each rotation player, expected vs actual comparisons, and a tentative window verdict.

**Strong:** Quantified projections with appropriate uncertainty, identification of the most likely peak year, and clear implications for roster construction.

**Stretch:** The analysis identifies a specific window strategy (consolidate now vs preserve for 2027) that informs Q5 directly.

---

End of specification.
