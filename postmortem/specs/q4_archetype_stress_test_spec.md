# Q4: Archetype Stress Test Specification

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q4
**Status:** Specification, revised post-LAFI v1 (2026-05-17)
**Position in stack:** Fourth tactical analysis, structural league-wide diagnostic

**Revision note:** LAFI components are added as clustering features (Section 2.1). A quadrant-based clustering approach is added as a second method (Section 2.3). The "archetype prevalence over time" analysis explicitly tracks Q4 (distributed pickup) prevalence (Section 4.1). The "championship correlation" analysis cross-references the LAFI C1 univariate finding (Section 4.4). Plus a new feature per Issue 2 of the post-LAFI replan: anomalous-correlation pattern (Wolves-like C2 x C5 lockstep) as a candidate clustering or differentiator feature.

---

## 1. The thesis

### 1.1 The question

Is the Wolves' playoff problem opponent-specific or league-wide? Specifically: is there a particular archetype of team that the Wolves consistently lose to, and is that archetype the future of the league?

This is the structural diagnostic. Q1-Q3 examined the Wolves in isolation. Q4 asks how they perform against the league as a whole, decomposed by team type. If they lose to specific archetypes consistently, and those archetypes are becoming more common, that's an existential roster construction problem. If they perform evenly against all archetypes and just have variance, the answer is much more optimistic.

### 1.2 Why this matters

This distinguishes "the Wolves are a tweak away from a title" from "the Wolves are structurally outdated and need to rebuild the supporting cast around Edwards."

In the modern NBA, certain types of offenses have grown sharply: skilled-five offenses (Jokic, Wembanyama, Sabonis, Sengun), star perimeter creators (SGA, Luka, Halliburton, Brunson), five-out spacing systems. If the Wolves consistently lose to these archetypes, and these archetypes will define the next five years of championship-caliber basketball, the team is structurally behind the league.

Conversely, if the Wolves perform fine against the modern archetypes and only lose to a specific subset (say, "elite offenses with five plus shooters"), the prescription is much more targeted: address that specific weakness.

### 1.3 The working hypothesis

The Wolves are below league average against teams with skilled offensive bigs who can pull Gobert out of the paint (Jokic, Wembanyama, Sabonis). They are average or above average against teams with traditional or limited offensive bigs.

They are also vulnerable to teams with two creators who can switch attack the Wolves' guards (testing this against teams like the Knicks with Brunson plus another creator, or any team with a true secondary star).

This hypothesis tracks with the eye test. The data will either confirm or complicate it.

---

## 2. The archetype clustering

### 2.1 The features

To cluster teams into archetypes, use features that capture offensive and defensive style:

**Offensive features:**
- Pace
- Three-point attempt rate
- Rim attempt rate
- Midrange attempt rate (residual from 3PT and rim)
- Assist rate
- Isolation rate
- PnR ball-handler frequency
- Post-up frequency
- Off-ball action frequency

**LAFI features (post-replan, primary):**
- LAFI Full and Sharp percentile ranks
- LAFI quadrant placement (Q1/Q2/Q3/Q4) as a categorical feature
- C1 through C5 percentile ranks individually (allows clustering on specific architectural dimensions)
- **Anomalous-correlation flag** (per Issue 2): does the team show Wolves-like C2 x C5 lockstep across the prior 3 seasons, or is the team's C2 x C5 correlation closer to the league-wide near-zero? This is a derived feature computed across a multi-season window.

**Roster features:**
- Center type: classified as rim-runner, stretch, playmaking-skilled (Jokic-type), or hybrid
- Primary creator type: classified as PG, wing, big, or multiple
- Number of "creators" (players with usage rate > 22% and assist rate > 18%)
- Three-point shooters in rotation (counted by 3PT% threshold)

**Defensive features:**
- Defensive scheme: switch-heavy, drop-heavy, hybrid
- Defensive rating
- Rim protection tier (specifically for the Spurs-style elite-rim-protection cluster identified in LAFI's Wolves diagnosis)

### 2.2 The sample

All 30 NBA teams across the 2023-24, 2024-25, and 2025-26 regular seasons. That's 90 team-seasons. Enough to support clustering.

Optionally extend back to 2021-22 for more historical depth, but recent seasons are most relevant because the league has continued to evolve.

### 2.3 The clustering method

Run two complementary clustering approaches and cross-validate them.

**Approach A: K-means or hierarchical clustering on z-scored features.**

K-means is simple and interpretable. Try k=4, k=5, k=6, evaluate cluster quality with silhouette scores and visual inspection. Likely best at k=5.

Expected clusters (hypothesis):
- **Skilled-Five Offenses:** Built around a high-IQ big (Denver, OKC if Holmgren counts as skilled five, hypothesis includes Spurs with Wemby, Indiana with Turner, Sacramento with Sabonis, Houston with Sengun)
- **Star Perimeter Offenses:** Built around a guard-wing creator with high usage (Dallas with Luka, Boston with Tatum-Brown, Cleveland with Mitchell, Atlanta with Trae)
- **Five-Out Spacing Offenses:** Built around shooting at every position (Knicks during certain stretches, Hawks)
- **Defensive Identity Teams:** Defense first, offense second (Magic, Wolves arguably)
- **Hybrid / In-Transition:** Teams that don't cleanly fit (Lakers, Bucks, etc.)

These are hypothesized clusters; the actual clusters will emerge from the data.

**Approach B (post-replan): Quadrant-based clustering using LAFI.**

Classify teams directly by LAFI quadrant placement (Q1/Q2/Q3/Q4). Treat each quadrant as a cluster. This is the simplest possible clustering and has the advantage that the partitioning is empirically grounded in LAFI's Phase 3 PCA (which independently surfaced the quadrant framework as the second-most-important axis in the league's offensive space).

The four LAFI quadrants:
- **Q1: Designed (low sticky, low motion death).** Warriors, Pacers, post-Trae Hawks. Gold standard.
- **Q2: Star-fed motion (high sticky, low motion death).** Brunson Knicks. Effective if creator is elite.
- **Q3: Single-star pickup (high sticky, high motion death).** Harden Rockets, Trae Hawks, Westbrook OKC. Known playoff-failure mode per LAFI's C1 finding.
- **Q4: Distributed pickup (low sticky, high motion death).** Wolves 2025-26. Rare and not well-precedented.

**Cross-validation between approaches.** If Approach A k-means produces clusters that align with Approach B quadrant placement, the framework is robust. If they diverge, that informs which dimensions of team style matter most for the archetype framing. Report both clusterings.

**Anomaly-based sub-clustering (per Issue 2).** Within each quadrant, split teams by whether they exhibit the Wolves-like anomalous C2 x C5 correlation pattern. The hypothesis to test: teams in Q4 with anomalous correlation have worse playoff outcomes than teams in Q4 without it (small sample, but informative if it holds).

### 2.4 Cluster interpretation

For each cluster, characterize it:
- Centroid feature values
- Representative team-seasons
- Defining offensive style
- Defining defensive scheme

This characterization makes the clusters legible to readers.

---

## 3. The Wolves performance by archetype

### 3.1 The setup

For each opponent the Wolves have played in 2023-24, 2024-25, and 2025-26 (regular season and playoffs), label the opponent's cluster.

Compute Wolves performance by opponent cluster:
- Net rating
- Offensive rating
- Defensive rating
- Win rate

Compare to overall Wolves averages and to league averages for those clusters.

### 3.2 The output

```
Opponent Archetype          | Games | Wolves NR | Wolves Win% | League Avg NR
Skilled-Five Offenses       |   24  |   -3.2    |    33%      |    -0.5
Star Perimeter Offenses     |   31  |   +1.1    |    52%      |    +0.2
Five-Out Spacing            |   18  |   +2.8    |    61%      |    +1.0
Defensive Identity          |   22  |   +5.4    |    73%      |    +2.5
Hybrid                      |   16  |   +1.9    |    56%      |    +0.5
```

(Illustrative numbers.)

The story is in the contrast. If Wolves NR vs Skilled-Five Offenses is sharply negative and significantly below league average, that confirms the structural weakness hypothesis.

### 3.3 Playoff-specific results

Same table, restricted to playoff games. Smaller sample but more important. Playoff games are where structural weaknesses get exposed.

---

## 4. The archetype prevalence analysis

### 4.1 The question

Are the archetypes that the Wolves struggle against becoming more common in the league?

**Specific Q4-prevalence question (post-replan).** Has Q4 (distributed pickup) prevalence risen, fallen, or stayed stable across the last decade? If Q4 prevalence has been rising, the Wolves are an early example of an emerging archetype and other teams will soon need to solve the same problem. If Q4 prevalence has been stable or falling, the Wolves are a structural outlier and the league's defensive solutions will continue to be calibrated against Q3 (single-star pickup), not Q4.

This question is directly material to the Q5 prescription. If Q4 is rising and the league is starting to develop counter-schemes, the Wolves' window for the current Q4 architecture is closing fast. If Q4 is rare and stable, the Wolves have more time to fix it on their own terms.

### 4.2 The methodology

For each season (2015-16 through 2025-26), classify each team into the cluster framework defined in Section 2.3. Then compute, by season:
- What fraction of the league is each archetype?
- What fraction of playoff teams (or conference finalists, or champions) is each archetype?
- **What fraction of the league is in each LAFI quadrant (Q1/Q2/Q3/Q4)?** Specifically tracks Q4 prevalence over time per the question above.

### 4.3 The output

A line chart showing the prevalence of each archetype over time. If "Skilled-Five Offenses" has been rising sharply and now constitutes 30% of playoff teams (and the Wolves struggle against them), that's a major structural problem.

This is the meta-analysis. It tells us whether the Wolves are losing to the future of the league.

### 4.4 Championship correlation

Look at championship outcomes by archetype and by LAFI quadrant:
- What archetype has won the most titles in the last 10 years?
- What's the trend?
- **What LAFI quadrant has won the most titles in the last 10 years?** Cross-reference with LAFI's Phase 4 C1 univariate finding (C1-extreme teams underperform in playoffs at p=0.030). If Q1 (designed) has dominated championships, that confirms the C1 finding from the championship side. If Q3 or Q4 have won championships despite the C1 finding, that complicates the story.

If skilled-five offenses have won 5 of the last 7 titles, that's strong evidence of where the league is heading.

**The Q4 championship question (post-replan).** Have any Q4-leaning teams won championships in the LAFI sample (2014-15 onward)? Reached finals? If not, the Wolves' Q4 placement is a structural disadvantage that has historically not produced championships. If a Q4 team has won, identify what they did differently. This becomes the most direct cohort evidence for the Wolves prescription.

---

## 5. The math

### 5.1 Clustering quality

For the k-means clustering, evaluate:
- Silhouette score for different k values
- Inertia (within-cluster sum of squared distances)
- Visual inspection of cluster assignments

Choose k based on the elbow of inertia + interpretability.

### 5.2 Performance estimates by cluster

For each cluster, compute Wolves' net rating with bootstrap CI:
```
For each bootstrap iteration:
  Resample games against cluster opponents with replacement
  Recompute net rating
Take 2.5th and 97.5th percentiles
```

A net rating of -3.2 with CI [-5.8, -0.6] is meaningfully negative. A net rating of -3.2 with CI [-8.1, +1.7] is too noisy to draw conclusions from.

### 5.3 Sample sizes

The Wolves play 82 regular season games per year, plus playoffs. Across three seasons, that's 250+ regular season games. Divided across 5 archetypes, that's 40-60 games per archetype. Good sample for regular season analysis.

Playoffs samples are smaller. Across 3 seasons of playoff games, the Wolves have played maybe 25-30 games. Divided across archetypes, some clusters may have only 3-5 games. Be honest about uncertainty.

### 5.4 League-adjusted comparisons

Wolves' performance against a cluster isn't meaningful in isolation. We need to know "how does the league perform against this cluster?" Then compare. A Wolves NR of -3 against skilled-fives is bad only if the league average NR against skilled-fives is meaningfully better.

Compute league average NR against each cluster as a baseline.

---

## 6. Charts and visualizations

### 6.1 The Cluster Map

A 2D projection (PCA or UMAP) of all team-seasons, colored by cluster. Wolves' team-seasons highlighted. Visually shows which clusters the league occupies and where the Wolves sit.

### 6.2 The Performance by Archetype Chart

A bar chart with one bar per archetype. Each bar shows Wolves' net rating. Reference line for league average performance against that archetype. Color-coding for confidence.

### 6.3 The Archetype Prevalence Over Time

Line chart with one line per archetype, showing percentage of league teams in each cluster from 2015-16 to 2025-26.

### 6.4 The Playoff Conversion Chart

A different visualization for the championship correlation. Sankey diagram or stacked bar showing what fraction of each archetype reached each playoff round.

---

## 7. Sequencing

1. Pull team-season feature data for 2015-16 through 2025-26
2. Run clustering, validate cluster quality
3. Label opponents in Wolves games
4. Compute Wolves performance by cluster
5. Compute league average performance by cluster
6. Build prevalence over time analysis
7. Build charts
8. Write up

Estimated time: 1-2 weeks.

---

## 8. What I'm worried about

**Clustering is partly arbitrary.** Different feature weightings and different k values produce different clusters. The clusters that emerge are real but they're not the only valid partitioning of the league. Mitigation: run multiple clustering approaches and check robustness. If results are consistent across methods, the findings are robust.

**Cluster boundaries are fuzzy.** Some teams are clearly in one cluster (Denver is unambiguously a skilled-five team). Others are between clusters (the Wolves themselves might be hard to classify). Soft cluster membership (probabilities of belonging to each cluster) is more honest than hard assignment for borderline teams.

**Small playoff samples by archetype.** The headline playoff numbers may be statistically noisy. Be careful about overclaiming.

**League evolution.** The 2025-26 league is different from the 2015-16 league. A "skilled-five offense" in 2015 is different from one in 2025. Adjust feature norms within season (z-score within season) to control for league drift.

---

## 9. Success criteria

**Minimum viable:** Clean clustering with interpretable archetypes, Wolves performance computed by archetype with appropriate uncertainty.

**Strong:** The analysis confirms or refutes the hypothesis about Wolves vs skilled-five offenses with statistical confidence. The prevalence analysis shows a clear trend that has implications for roster construction.

**Stretch:** The analysis identifies a specific archetype gap (e.g., "the Wolves consistently struggle against teams with two perimeter creators") that informs Q5 prescriptions directly.

---

## 10. Open questions

1. Exact feature set for clustering (which to include, which to exclude)
2. Whether to include playoff games as separate "seasons" or pool with regular season
3. How to handle teams that change identity mid-season (trades, injuries)
4. Whether to use soft clustering (probabilities) or hard assignment

---

End of specification.
