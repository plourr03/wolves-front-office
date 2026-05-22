# Chasing the First Banner: Article Plan

**Project:** Public-facing publication of the Wolves analytical project
**Brand:** Chasing the First Banner / Data science in pursuit of Minnesota's first NBA title
**Author:** Bobby Plourde
**Entity:** ScoutIQ LLC
**Goal:** Establish credible analytical voice, eventually reach Timberwolves front office through professional networking

## The story arc

A regular fan watched his team and noticed something off. He built rigorous analytical work to understand what was actually happening. He found the team's offensive architecture had drifted into a specific pickup-style pattern that historically caps teams at the second round. He identified the specific scheme the Spurs used to break Edwards in the playoffs. He showed that historical teams with this profile haven't broken the ceiling even with elite talent. He proposed a specific prescription centered on a particular kind of player addition that addresses the architectural gap. He showed that the team's contention window is real but contingent on execution.

Six articles tell that story. Each one stands alone but rewards the series.

## Sequencing principles

1. **Diagnostic before prescription.** Don't lead with what the front office should do. Lead with what happened and why. Readers earn the recommendation by following the diagnosis.

2. **Stand-alone but reward the series.** A reader arriving at Article 4 understands it without having read 1-3. A reader who reads in order finds each article more meaningful because of what came before.

3. **Group by story, not by analysis.** Some articles combine findings from multiple Q-analyses. Some Q-analyses get split or woven into multiple articles. The grouping serves narrative coherence.

## The six articles

### Article 1: The LA Fitness Game

**Job:** The origin story plus the architectural diagnosis. Establishes voice, methodology, and the core analytical framework readers need to understand everything that follows.

**Opening:** Brother-in-law on the couch watching the Wolves. "They look like they're playing LA Fitness pickup." That casual observation becomes the seed of the project.

**Core content:**
- The origin story
- Building LAFI (LA Fitness Index) as a way to measure what "pickup ball" actually means architecturally
- The five components: Ball Stickiness, Movement Death, Isolation Reliance, Action Poverty, Shot Quality Decay
- The Wolves' specific fingerprint in 2025-26
- The four-quadrant framework (Q1 designed, Q2 star-anchored, Q3 single-star pickup, Q4 distributed pickup)
- The Wolves' Q4 classification: distributed pickup

**Visualizations:**
- The LAFI fingerprint chart (the homepage hero, embedded inline)
- The five-component breakdown with descriptions
- A 30-team league scatter plot showing where the Wolves sit relative to every other team
- An interactive comparison: select another team to see how their fingerprint differs from the Wolves

**Length:** 2500-3500 words

**Status:** First draft below. Written manually to establish voice before invoking the storytelling skill on subsequent articles.

### Article 2: How They Got Here

**Job:** The historical drift. Shows how the team moved from architecturally normal (2023-24) to architecturally extreme (2025-26). Sets up that the current state isn't accidental but didn't have to happen this way.

**Core content:**
- The 2023-24 baseline (last KAT year, Western Conference Finals run, Q1/Q2 architecture)
- The 2024-25 transition year (Randle year 1, Q3 territory)
- The 2025-26 destination (extreme Q4)
- The KAT-Randle swap as one factor among several (Q6 v2 honest framing: complicated transaction with offsetting effects)
- The DiVincenzo benefit (he became the team's most impactful player after the trade)
- The system trajectory shift (Q0D coaching system finding: PR-Roll-Man allocation dropped 41%)
- The aging context (Conley decline, Gobert decline, Randle decline)

**Visualizations:**
- Three-year trajectory chart showing each component evolving (data already in Firestore)
- A transaction timeline showing key moves with their architectural consequences
- Interactive: filter by season to see the Wolves' LAFI position move across the four-quadrant framework

**Length:** 2000-2500 words

**Source analyses:** Q0A trajectory data, Q6 v2, Q0D, parts of Q8

### Article 3: What Wembanyama Did to Edwards

**Job:** The mechanism analysis. The specific way the Spurs broke the Wolves' offense in the playoff series everyone watched. Most dramatic article.

**Core content:**
- Edwards' regular season vs Spurs series shot profile
- Catch-and-shoot 3PA dropped from 13.8% (regular season) to 6.2% (Spurs normal-load games)
- The Wembanyama-anchored switch-everything scheme
- How the scheme channeled Edwards into the 11-16 foot floater zone where he is least efficient
- The architectural inversion: the Wolves' Q4 architecture depends on isolation advantage creation, the Spurs' scheme is its architectural inverse
- Replicability: which other teams could deploy similar schemes (the OKC question)

**Visualizations:**
- Edwards' shot distribution: regular season vs Spurs series side-by-side
- Defensive scheme diagram showing the switch-everything coverage
- The "channel into the floater zone" visualization
- Replicability map: which 2025-26 teams have the personnel to deploy this scheme

**Length:** 2500-3000 words

**Source analyses:** Q3 mechanism, parts of Q4

### Article 4: Why R2 Is the Ceiling

**Job:** The historical cohort. Establishes that the architectural state has a known historical ceiling that talent alone hasn't broken. Makes the prescription urgent.

**Core content:**
- The seven historical cohort teams (top quintile Sharp LAFI plus Q4 placement, 2014-15 through 2024-25)
- Zero of seven reached the conference finals
- The 2021-22 Sixers as the load-bearing cautionary comp (Embiid MVP candidate, R2 lost)
- The 2023-24 Suns as the closest talent comp (Durant + Booker + Beal, R1 swept by the Wolves themselves)
- The sample size caveat (7 teams is small; true probability is uncertain)
- The escape hatch (the cohort is teams that ENDED UP in this profile; teams that successfully change their architecture move out of the cohort)

**Visualizations:**
- The cohort table with all seven teams, records, and outcomes
- A "talent vs architectural state" 2D plot showing where each cohort team sat
- Interactive: pick any team in the historical sample and see where they ended up
- The Wolves' position highlighted against the cohort distribution

**Length:** 2000-2500 words

**Source analyses:** Q0C historical cohort

### Article 5: The Iverson Template vs The Kobe Template

**Job:** The prescription framework. Establishes what kind of player the Wolves actually need. The template framing is illustrative and powerful: a specific picture readers can hold in their head.

**Core content:**
- Edwards' similarity comp set from Q7 (Brown, Booker, LaVine, Mitchell all plateaued at All-NBA)
- Edwards' efficiency edge over his comps (0.617 TS% vs their 0.57-0.59 range)
- The tier-leap probability bands (25-35% per Q7)
- The supporting cast pattern across MVP-tier championship rosters: the consistent missing piece is a skilled secondary creator
- The Iverson 2001 template (defensive anchor, glue PG, high-tier individual scorer, no skilled secondary creator; Finals possible, championship unlikely)
- The Kobe 2009 template (defensive anchor, skilled secondary creator, multi-positional wing, glue PG, star guard; championship realistic)
- The Wolves' configuration matches Iverson 2001
- The structural difference is a skilled secondary creator (Pau Gasol / Chris Paul / Khris Middleton archetype)
- The illustrative-not-prescriptive note on player names

**Visualizations:**
- Side-by-side template comparison: Iverson 2001 vs Kobe 2009 roster components with the Wolves overlaid
- Secondary creator gap visualization
- Edwards tier-leap probability bands
- Interactive: drag a hypothetical secondary creator into the Wolves' lineup and see how the template shifts

**Length:** 2500-3000 words

**Source analyses:** Q7 star comp analysis

### Article 6: The Prescription

**Job:** The flagship article. The full Q5 v4 deliverable in publishable form. The article eventually distributed to Timberwolves front office contacts.

**Core content:**
- The two archetype acquisitions (Archetype A: multi-positional Category B wing; Archetype B: skilled secondary creator)
- Portfolio A: summer 2026 Category B at MLE plus McDaniels expansion test plus system restoration
- Portfolio C: trade-driven 2027 cap path for secondary creator acquisition
- The contention window (2026-27 through 2028-29 peak years, extending to 2029-30 if 2027 reset executes)
- The trade-driven 2027 cap path specifics (Gobert and Randle player options before exercise)
- Three scenarios for DiVincenzo Achilles recovery
- The explicit non-prescriptions (not Giannis or Durant, not trading Gobert immediately, not a roster overhaul, not betting on Edwards' tier-leap to fix everything)
- Edwards tier-leap window aligned with team peak window (2027-28 and 2028-29)
- The honest framing on uncertainty

**Visualizations:**
- Portfolio comparison: A, B, C with cluster coverage and timeline
- Contention window chart with player trajectories
- The trade-driven 2027 cap path with Gobert/Randle player option timing
- Edwards tier-leap window aligned with team peak window
- Interactive: explore the prescription's sensitivity to DiVincenzo recovery scenarios

**Length:** 3500-4500 words

**Source analyses:** Q5 v4 prescription document, Q0B trajectory, Q4 cluster vulnerabilities

## What gets left out (and where it goes instead)

**Q0D coaching system finding.** Woven into Article 2 as one factor in the historical drift. Doesn't need a standalone article because the finding (allocation shift) is a contributing cause, not a primary story.

**Q8 player decisions.** Specifics on Gobert, Randle, and DiVincenzo are woven into Articles 5 and 6. The "should we trade Gobert" question gets answered as part of the prescription article rather than as standalone content.

**Q4 matchup cluster analysis.** Cluster 1 (Spurs-archetype) vulnerability gets covered in Article 3 (the mechanism). Cluster 3 (DAL-archetype) vulnerability gets covered in Article 6 (the prescription) as part of why archetype acquisitions matter. Could be split into a standalone article eventually if more visualization work justifies it.

**The methodology corrections and audit findings.** Live on the methodology page rather than in articles. The page documents the project's discipline patterns including the five corrections caught during development (DiVincenzo lineup confound, Gobert+Naz mislabel, Gobert+Randle Spurs-specific framing, contract structure, the LAFI v1 vs canonical audit).

## Offseason content (slow periods)

These pieces fill gaps between major articles when the analytical work is between cycles. Lower-pressure publication that maintains site activity during offseason.

### Revisiting the KAT Trade Two Years Later

**Trigger:** Offseason 2026 or 2027, when there's space for retrospective analysis without immediate playoff context.

**Job:** The Q6 v2 counterfactual analysis. The KAT trade evaluated honestly two years after the fact, with the benefit of seeing what both teams became.

**Core content:**
- The trade structure (KAT and three filler players plus a 2nd round pick for Randle, DiVincenzo, Bates-Diop, and a first-round pick that became Beringer)
- KAT's performance at the Knicks (age 30 production, role shift)
- The architectural counterfactual (would the Wolves have stayed Q1 with KAT)
- The honest finding: approximately architecturally neutral
- The complications: DiVincenzo became the team's most impactful player; Randle's salary efficiency is the worst on the roster; Beringer is a future asset
- The "reasonable people can disagree" framing

**Why this fits offseason:** The trade evaluation doesn't have immediate playoff stakes. It's retrospective analysis that benefits from being written without pressure. The "two years later" framing earns its place in slower content cycles.

### Potential future offseason content

- Player development deep dives (Beringer trajectory, Dosunmu role expansion)
- Coaching system retrospectives
- Salary cap deep dives (the 2027 cap math, the player option strategy)
- League-wide architectural surveys (where do all 30 teams sit on LAFI, who's drifting toward Q4)
- Methodological essays (why custom metrics matter, the discipline of confound checks)

## Publication sequence

Three options to consider:

**Option A: Drop all six at launch.** Maximum impact, complete story available from day one. Requires having all six drafted before launch.

**Option B: Drop weekly over six weeks.** Builds anticipation, allows refinement based on early reaction. Most journalistic pattern.

**Option C: Drop in three pairs.** Diagnostic pair (1 and 2) at launch. Mechanism pair (3 and 4) two weeks later. Prescription pair (5 and 6) two weeks after that. Each pair tells a complete arc.

**Option D: Launch with Article 1 only.** Lowest-risk path. Establish voice and analytical level. Build the rest based on reaction.

Recommendation: Option C if targeting a 6-8 week launch window. Option D if not in a rush and wanting to validate voice before committing to the full series.

## On interactive visualizations

Build interactivity that reveals new information. Skip interactivity for its own sake.

**Worth building:**
- LAFI 30-team scatter plot where readers hover to see any team's fingerprint
- Trajectory chart where readers scrub through years to see drift
- Cohort plot where readers highlight any comp team
- Portfolio comparison where readers toggle scenarios

**Skip:**
- Tooltips on bar charts showing the same value the bar already displays
- Hover effects that don't reveal new information
- Animation that delays the point
- "Click to expand" hiding information that should just be visible

## Voice and discipline

Across all articles:

- Sports-savvy: write like someone who watches the games and knows the league
- Rigorous: preserve confidence intervals, sample size caveats, and methodological hedges
- Personal: the author is a lifelong fan, that stake comes through honestly without overwhelming
- Accessible: technical concepts get translated, not jargon-dumped
- No em dashes or en dashes (hard rule)
- No AI tells (delve, dive deep, navigate the landscape, in conclusion, etc)
- The corrections and refinements appear in the narrative when relevant; the discipline is part of the story

## Production sequence

1. Article 1 first draft (written manually to establish voice, included in this plan)
2. Visualizations for Article 1 (LAFI fingerprint exists; 30-team scatter plot needs building)
3. Article 1 publication
4. Voice references locked in from Article 1
5. Articles 2-6 drafted via storytelling skill using Article 1 as voice anchor
6. Visualizations for each article built using the patterns established
7. Publication sequence per chosen option

## Status

Plan: complete
Article 1 first draft: included below
Storytelling skill: built (storytelling-for-chasing-the-first-banner-SKILL.md)
LAFI fingerprint visualization: live on homepage
30-team scatter plot for Article 1: not yet built
Other article visualizations: not yet built
