# Wolves to a T: Frontier Analytics Roadmap
## Advanced Data Science Projects for the 2026 Offseason and Beyond

**Prepared:** July 1, 2026
**Status:** Planning document. Intended as the source-of-truth spec for prioritizing and handing projects to the implementation agent.

---

## Executive Summary (Plain Language)

The Wolves just made the two biggest structural changes of any contender this offseason: LaMelo Ball and Josh Green arrived, Naz Reid and Julius Randle left, and the team is now operating under a second-apron hard cap with almost no flexibility. That creates three questions that ordinary basketball analysis cannot answer:

1. **Does Ant plus LaMelo actually work?** They have never shared an NBA floor, so there is literally no data on the pairing. Every on/off split and two-man number is undefined.
2. **What did losing the Randle and Naz frontcourt do structurally, and what is the best possible fix under a hard cap with only minimum contracts to offer?**
3. **What did the trade actually cost?** The 2033 unprotected first and three swaps are the real price, and right now that price is a vibe, not a number.

This roadmap describes seven projects that answer those questions with genuinely frontier methods: counterfactual inference, generative sequence models, causal machine learning, option pricing, constrained optimization, and computer vision. Each section explains the idea in plain language first, then goes into implementation depth. A recommended build order is at the end.

---

## Current State of the Roster (Context)

As of July 1, 2026, per reporting from the Star Tribune, The Athletic, and Canis Hoopus:

- **In:** LaMelo Ball and Josh Green (from Charlotte). **Out:** Naz Reid, an unprotected 2033 first-round pick, three pick swaps, and second-round picks (to Charlotte). Julius Randle was moved to Brooklyn in a separate deal.
- The team sits at roughly **10 guaranteed contracts**, can add second-rounder Isaiah Evans on a minimum, and has **minimum-level signing power only** for outside free agents.
- Ownership has committed to the luxury tax but will **not cross the second apron**, which functions as a hard cap on every move.
- The **frontcourt (especially power forward) is the glaring hole** after losing both Randle and Naz, with floor spacing at the 4 the specific need.
- **Josh Green's expiring deal (roughly $14.7M) is the only meaningful trade lever**, and the team has **no tradable first-round capital** left to attach.
- Recent moves: Bones Hyland re-signed (one year, minimum), Jaylen Clark re-signed (three years, ~$10M). Mike Conley and Kyle Anderson are unsigned free agents; Conley has reported interest from Miami.

The three live analytical problems, restated precisely:

- **The Fit Problem:** predict the Edwards-Ball interaction with zero observed shared possessions.
- **The Reconstruction Problem:** replace the departed frontcourt production under second-apron and minimum-only constraints.
- **The Cost Problem:** put a rigorous, uncertainty-quantified value on the 2033 pick and the three swaps.

---

# Project 1: The Counterfactual Fit Engine (Ant × LaMelo)

**One-line summary:** A model that predicts how any hypothetical five-man lineup performs, trained on the entire league's history, so we can evaluate Edwards-Ball lineups that have never existed.

### The Question

What happens when Anthony Edwards and LaMelo Ball share the floor: net rating, spacing behavior, turnover profile, and role overlap, before a single possession of evidence exists?

### Why Standard Methods Fail

There are zero shared NBA possessions between Edwards and Ball. On/off splits, two-man net ratings, and lineup data are all undefined for this pairing. The naive approach (add their individual impact metrics together) assumes impact is additive, which is precisely the assumption in question when combining two high-usage, loose-handle primary creators. Fit is an interaction effect, and interaction effects cannot be read off individual numbers.

### Method

The core idea: fit is a **learned interaction function**, not a lookup. Train that function on every lineup the league has ever run, then query it with lineups that do not exist yet. Three layers.

**Layer 1: Bayesian latent skill decomposition.**
Fit a hierarchical factor model to 10+ seasons of stint-level adjusted plus-minus data (an RAPM-style design matrix where each row is a stint, columns are player indicators, outcome is point differential per possession). Instead of estimating one scalar impact per player, estimate a K-dimensional latent skill vector per player per season, with dimensions that emerge as interpretable factors: rim pressure, pull-up gravity, connective passing, point-of-attack defense, rim protection, defensive rebounding, and so on.

- Use informative priors built from box-score aggregates and public tracking aggregates (drives, touches, catch-and-shoot vs. pull-up splits, contested rebound rates) so low-minute players are stabilized and factors are identified.
- Impose sparsity or semi-informative loadings so factors stay interpretable rather than rotating arbitrarily.
- Implementation: NumPyro or PyMC with stochastic variational inference for scale; full MCMC on a subsample to validate the variational posterior.
- Output: a posterior distribution over each player's skill vector, including Edwards, Ball, and every plausible Wolves rotation player.

**Layer 2: The lineup synergy function.**
Train a function f(five latent skill vectors, opponent context) → expected net rating per 100 possessions, on every five-man lineup the league has run since roughly 2014 (weighting by possessions, with shrinkage for low-minute lineups).

- Architecture options, in order of preference: (a) a graph neural network with players as nodes and learned pairwise interaction edges, pooled to a lineup readout (directly reuses the GNN experience from the MaxPreps ranking system); (b) a permutation-invariant set network (DeepSets or set attention) over the five skill vectors; (c) a gradient-boosted model over engineered pairwise features as a fast baseline.
- The critical property: the model learns interaction structure (redundancy penalties, complementarity bonuses) from the whole league. It has seen every "two ball-dominant guards" pairing in modern history, every "non-spacing big plus paint-bound forward" frontcourt, and it has learned what happens to turnover rates and shot quality in each configuration.

**Layer 3: Counterfactual inference.**
Query the trained model with hypothetical Wolves fives containing Ball. Propagate uncertainty properly: sample skill vectors from the Layer 1 posterior, push each sample through the synergy function, and report full predictive distributions rather than point estimates.

### Validation

- Leave-one-team-out cross-validation on lineup-level predictions.
- The killer validation: historical midseason trades. For every significant acquisition since 2014, predict post-trade lineup performance using only pre-trade data, then score against what actually happened. If the model beats additive baselines on real trades, the LaMelo predictions carry weight.

### Data

- Full league play-by-play from the NBA Stats API (via nba_api) to construct stints and lineups, 2014 to present.
- Public tracking and hustle aggregates from stats.nba.com for priors.
- Existing possession-parsing logic can be shared with Project 2.

### Outputs and Deliverables

- Posterior net-rating distributions for every candidate Wolves starting five and key bench units.
- A quantified **redundancy score** between Edwards' and Ball's creation profiles (overlap of their latent skill vectors in the creation subspace), which becomes a headline number.
- Sensitivity analysis: how much does the projection swing based on who plays the 4? This connects directly to the frontcourt reconstruction problem in Project 5.

### Content Angles

- "The model has watched every two-star backcourt since 2014. Here is what it predicts for Ant and LaMelo," with full uncertainty shown, not hidden.
- The redundancy score as a single shareable number with a carousel explaining what it means.
- Lineup leaderboard: best and worst projected Wolves fives, with the why.

### Effort and Dependencies

Heavy. The flagship summer build: roughly 4 to 8 weeks of agent implementation time. No dependencies on other projects, but its skill vectors feed Projects 2 and 5. Ship target: before opening night.

---

# Project 2: The Generative Possession Model (and the LAFI Forecast)

**One-line summary:** A transformer trained on tokenized play-by-play, a language model of basketball possessions, that can simulate Wolves-with-LaMelo possessions and let us compute LAFI on a season that has not happened yet.

### The Question

What will Wolves possessions actually look like next season: pace, turnover profile, shot diet, transition frequency, and above all, chaos? Can we forecast LAFI before the team plays a game together?

### Why Standard Methods Fail

Aggregate projection systems predict season-level averages. They cannot tell you how possessions unfold: whether early-clock threes replace halfcourt post-ups, whether transition frequency spikes, whether turnovers cluster. LAFI is a possession-sequence property, so forecasting it requires generating sequences, not averages.

### Method

**Tokenization.** Convert play-by-play into token sequences per possession: event type (drive, pass, screen action proxy, shot, turnover type, foul), actor role (slotting players into archetype-role tokens plus identity embeddings), shot zone, shot-clock bucket, transition flag, score-state bucket. Possession segmentation follows pbpstats-style definitions, which the existing LAFI pipeline already implements canonically. That pipeline is the starting point.

**Model.** A decoder-only transformer trained autoregressively on possession token sequences across the whole league (2015 to present), conditioned on:

- Lineup embeddings: ideally the latent skill vectors from Project 1 (clean dependency), or learned player embeddings as a standalone fallback.
- Opponent embedding and defensive-scheme proxies.
- Game context (score margin, period, rest).

**Calibration.** Before trusting generations, verify the model reproduces held-out team profiles: pace, turnover percentage, rim rate, three-point rate, transition share, per team-season. Generated marginals must match observed marginals within tolerance. This is the make-or-break gate.

**Simulation.** Generate a full synthetic 2026-27 Wolves season against the real schedule with LaMelo-inclusive lineups (rotation priors set editorially or from Project 5's solver). Then compute LAFI on the synthetic possessions exactly as the canonical pipeline computes it on real ones.

### Known Limitation and Mitigation

Event-level play-by-play lacks true spatial detail. Mitigate with shot-zone tokens, transition flags, and tracking-aggregate conditioning. If Project 6 (computer vision tracking) eventually ships, its spatial features upgrade this model substantially. Be explicit in publication about what the tokens can and cannot see.

### Data

- League-wide play-by-play 2015 to present (shared ETL with Project 1).
- pbpstats-style possession segmentation from the existing LAFI codebase.

### Outputs and Deliverables

- A **LAFI forecast distribution** for the 2026-27 Wolves: the single best brand crossover available, because LaMelo is plausibly the highest-entropy player in the league joining a team already measured at the chaotic extreme.
- Simulated season profile: pace, shot diet, turnover clustering, transition share, with comparisons to last season.
- Possession-type shift analysis: which possession archetypes LaMelo adds and which he deletes.

### Content Angles

- "We measured how chaotic the Wolves will be before opening night."
- A "possessions that don't exist yet" explainer showing sample generated sequences (clearly labeled synthetic).
- Preseason vs. forecast scorecard in October, then forecast vs. reality checkpoints through the season. Being publicly falsifiable is the credibility play.

### Effort and Dependencies

Heavy. Shares its data pipeline with Project 1 and ideally consumes Project 1's embeddings. Roughly 4 to 6 weeks after the shared ETL exists. Ship target: LAFI forecast published before opening night.

---

# Project 3: LAFI 2.0, The Causal Layer

**One-line summary:** Upgrade LAFI from describing chaos to answering whether chaos actually causes bad offense, and identifying which players inject it.

### The Question

Three questions, in ascending order of ambition:

1. Do games have identifiable chaos regimes, and what triggers transitions between them?
2. Who injects chaos into whom? Is it a property of specific players, specific pairings, or the scheme?
3. Does chaos causally reduce offensive efficiency, or is it a style correlate that costs nothing once talent is controlled for?

### Why Standard Methods Fail

LAFI currently correlates chaos with outcomes. Correlation here is badly confounded: chaotic possessions happen more against good defenses, in clutch situations, and with bench units. A raw chaos-vs-efficiency regression cannot separate "chaos hurts" from "hard situations produce both chaos and bad offense."

### Method

**Component A: Regime identification.**
Fit a hidden Markov model (or switching state-space model) over within-game possession sequences, where the latent state is an order/chaos regime and emissions are possession-level LAFI components. Deliverables: regime maps per game, dwell times, and transition triggers (lineup changes, opponent runs, timeouts, foul trouble). This turns "the Wolves are chaotic" into "the Wolves enter chaos states under these specific conditions and stay there this long."

**Component B: Source attribution via directed information.**
Compute transfer entropy (directed information flow) between player-level event streams: does player X's action entropy predict teammates' subsequent entropy beyond what the teammates' own history predicts? This is directional, unlike correlation. Output is a directed chaos-influence graph: who is a chaos source, who is a chaos amplifier, who is a stabilizer. Mike Conley's stabilizer value, if he departs, becomes quantifiable here.

**Component C: Causal effect estimation via double machine learning.**
Treatment: stint-level or possession-cluster chaos score. Outcome: points per possession. Controls: lineup talent (the latent skill vectors from Project 1 are the ideal control set), opponent defensive quality, rest, score state, clock. Use DML with cross-fitting so flexible ML nuisance models do not bias the causal estimate. Report the average treatment effect of chaos on efficiency with confidence intervals, plus heterogeneity: does chaos cost more in halfcourt vs. transition, playoffs vs. regular season, high-leverage vs. garbage time?

### The LaMelo Projection

Compute LaMelo's historical chaos-source profile from his Charlotte event streams, then combine with Component C's causal estimate to project the net chaos cost (or non-cost) of adding him. If the causal effect of chaos is near zero, the entire editorial framing flips: chaos is a tax the Wolves can afford, and the "most chaotic player joins most chaotic team" storyline becomes a feature, not a bug. If the effect is large and negative, the concern is now quantified rather than vibes-based. Either answer is a story.

### Data

Existing canonical LAFI pipeline plus league-wide play-by-play (shared ETL). Component C benefits from Project 1's skill vectors but can run with simpler talent controls in v1.

### Outputs and Deliverables

- Causal estimate: points per 100 possessions attributable to chaos, with intervals.
- Directed chaos-influence graph for the current roster plus LaMelo's imported profile.
- Regime maps and trigger analysis.

### Content Angles

- "Is chaos actually bad? We ran the causal analysis." This is the definitive LAFI thesis piece.
- The chaos-influence graph as a visual (natural D3 candidate, consistent with the existing LAFI visualization work).
- Conley-as-stabilizer valuation if his free agency resolves elsewhere.

### Effort and Dependencies

Medium. Components A and B can start immediately on existing LAFI infrastructure. Component C is stronger after Project 1 ships but has a workable v1 without it. New-season data sharpens everything after October.

---

# Project 4: The 2033 Pick Posterior and Swap Option Pricing

**One-line summary:** Replace "the 2033 unprotected first is scary" with a full probability distribution over what it will actually be worth, and price the three swaps the way a quant prices options.

### The Question

What did the LaMelo trade actually cost? Not in vibes, but as a posterior distribution over draft outcomes, converted into championship equity through the existing Joan Bet framework.

### Why Standard Methods Fail

Public pick valuations use flat expected-value tables that ignore the single most important thing about a 2033 unprotected pick: its value is dominated by tail scenarios (the core ages out, Ant leaves, the franchise bottoms out) whose probabilities are estimable but never estimated. Swaps are even worse: they are conditional assets that only pay off in specific world-states, and almost nobody values them as such.

### Method

**Component A: Franchise trajectory model.**
A hierarchical Bayesian state-space model of franchise quality: latent team strength evolves as an autoregressive process with regime-shift dynamics, trained on 40+ years of franchise win histories. Covariates: core age profile, star presence, cap state, roster continuity. This captures the empirical reality that franchises mean-revert, but with fat tails and persistence.

**Component B: Star retention hazard.**
Survival analysis (Cox proportional hazards or a Bayesian parametric survival model) on superstar tenure with their drafting/current franchise. Covariates: age, contract structure and year, team success trajectory, market size, franchise stability. Apply to Anthony Edwards for the Wolves side and to LaMelo Ball and the Hornets' young core for the Charlotte side. The Edwards hazard curve is the dominant driver of the 2033 tail and deserves its own writeup.

**Component C: Aging curves.**
Hierarchical, archetype-specific aging curves feeding Component A, so the simulated Wolves of 2031-2033 reflect a realistic decay (or persistence) of the current core rather than a frozen snapshot.

**Component D: Joint simulation.**
Co-simulate Wolves and Hornets trajectories 2027 through 2033 within a shared league environment (correlated shocks, so both teams face the same competitive landscape). Map each simulated season's win total to lottery odds to a pick-slot distribution using actual lottery mechanics.

**Component E: Valuation.**
Convert pick slots to value using surplus-value curves estimated with uncertainty from historical draft outcomes (distributions over slot value, not point estimates). Then the key move: **each swap is an option.** From Charlotte's perspective, a swap in year Y pays max(0, value of the better pick minus value of their own pick) in the world-states where Minnesota's pick lands ahead of theirs. Price each of the three swaps by Monte Carlo over the joint simulation from Component D, exactly as one prices a path-dependent financial option. Report expected values and, more importantly, the scenario decomposition: which world-states carry the cost.

**Component F: Integration.**
Feed the resulting asset-value distributions into the Joan Bet championship-equity machinery and restate the total trade cost in title-equity terms with credible intervals. This closes the loop with the existing clean-room trade evaluation, upgrading "wash to slightly negative on team strength, asset cost is the payload" into a fully quantified statement.

### Data

Historical franchise win records and draft outcomes (Basketball-Reference), public contract data, lottery mechanics, and the existing Joan Bet codebase, which already contains the championship Monte Carlo this plugs into.

### Outputs and Deliverables

- Full posterior over the 2033 pick's draft slot and surplus value.
- Priced valuations of each of the three swaps with scenario decomposition.
- The "doomsday distribution": probability mass on the worlds where the 2033 pick becomes a top-5 selection for Charlotte, and what has to happen for those worlds to occur.
- A restated total trade cost in championship-equity points.

### Content Angles

- The definitive longform: "What the LaMelo trade actually cost, with error bars."
- The Edwards retention hazard curve as its own piece (sensitive framing, handled carefully).
- A tail-risk visualization of the 2033 distribution, which is exactly the kind of chart this asset was made for.

### Effort and Dependencies

Medium-heavy, but it extends existing Joan Bet code rather than starting fresh. No dependencies on other projects. Can begin immediately and publish in stages (hazard model first, joint simulation second, option pricing third).

---

# Project 5: The Offseason Solver (Optimal Transport + Hard-Cap MILP)

**One-line summary:** Treat the rest of the offseason as a formal constrained-optimization problem: reconstruct the departed frontcourt production as cheaply as possible, subject to the second-apron hard cap, and publish the solution while free agency is live.

### The Question

Given minimum-only signing power, the Green expiring as the lone trade lever, no attachable first-round capital, and a hard ceiling at the second apron: what is the best executable remainder of this offseason, and what is a marginal dollar of apron room actually worth?

### Why Standard Methods Fail

Free agency coverage evaluates moves one at a time. But the Wolves' problem is combinatorial: every minimum signing, every Green trade construction, and every roster-spot decision interacts under a shared hard constraint. One-at-a-time analysis cannot find the best bundle, and it cannot produce shadow prices.

### Method

**Stage 1: Replacement scoring via optimal transport.**
Represent the departed Randle-plus-Reid production as a joint distribution over shot locations, play types (public Synergy-style aggregates), usage contexts, and lineup roles. For each candidate bundle (combinations of minimum-market free agents plus plausible Josh Green trade returns), build the same distribution and compute the **Wasserstein distance** between the bundle and the departed production. Low distance means structural reconstruction, not just point replacement. This formalizes "spacing at the 4" as a measurable property of a distribution rather than a scouting adjective.

**Stage 2: The optimizer.**
A mixed-integer linear program:

- **Decision variables:** binary sign/no-sign for each realistic minimum-market free agent; binary execute/no-execute for each enumerated Green trade construction; roster-spot assignments.
- **Constraints:** total salary below the second-apron line, roster count between 14 and 15 (plus two-ways), signing-power rules (minimum-only), exception availability, positional minutes coverage (a feasibility constraint ensuring 48 playable minutes at each position slot).
- **Objective:** projected championship equity from the existing Monte Carlo. Version 1 can drive the objective with public impact metrics; version 2 swaps in Project 1's fit engine so the objective rewards complementarity with Edwards and Ball rather than raw talent accumulation.
- **Solver:** OR-Tools CP-SAT or PuLP with CBC; the problem size is trivially small for modern solvers, so iteration speed will be instant.

**Stage 3: Shadow prices (the best content in the project).**
From the LP relaxation duals: the marginal championship equity of one additional dollar of room under the apron, the implied title-equity value of Green's roughly $14.7M expiring, and the value of the 15th roster spot. These are numbers no one else publishes.

### Data

Public contract and cap data, the current free-agent pool, Synergy-style public aggregates, and the cap-rule logic already partially encoded in the existing trade model. Cap-rule fidelity is the main correctness risk: apron mechanics (no aggregation, frozen picks, minimum-only) must be encoded exactly.

### Outputs and Deliverables

- A ranked list of executable offseason plans with projected equity and Wasserstein reconstruction scores.
- The **minimum-contract big board**, ranked by how cheaply each player reconstructs the departed distribution.
- Shadow prices: dollar-of-apron-room value, Green-expiring value, roster-spot value.

### Content Angles

- "We solved the Wolves offseason as an optimization problem," published this week while decisions are actually live.
- The shadow-price carousel: what one dollar under the apron is worth.
- Real-time updates: re-run the solver after every signing league-wide as the free-agent pool shrinks, which makes this a living piece rather than a one-off.

### Effort and Dependencies

Light-to-medium and the fastest to ship: a credible v1 in days, since it reuses the trade model's cap logic and the Joan Bet Monte Carlo. Highest urgency of all seven projects because its content value decays as free agency resolves.

---

# Project 6: Do-It-Yourself Tracking Data (Computer Vision on Broadcast Film)

**One-line summary:** Port the existing high school basketball computer vision pipeline to NBA broadcast footage and generate proprietary spatial tracking data, unlocking gravity and spacing metrics that no independent analyst publishes.

### The Question

Can Wolves to a T stop being capped at box-score and play-by-play derivatives, and instead generate its own player-coordinate data, becoming a data source rather than only an analysis publication?

### Why This Is the Moat

League tracking data (Second Spectrum lineage) is private. Every public analyst, no matter how sophisticated, works from the same event-level derivatives. Player coordinates unlock an entire class of metrics (gravity, spacing geometry, off-ball defense, transition value) that currently only exist behind team and league walls. An independent publication computing these from broadcast film would be close to unique.

### Method

The MaxPreps play-by-play extraction stack is the starting point, adapted for NBA broadcast conditions:

- **Detection:** RF-DETR for player and ball detection, fine-tuned on NBA broadcast frames.
- **Tracking:** BoT-SORT for multi-object tracking through occlusion.
- **Court registration:** court keypoint detection per frame, then homography from broadcast pixel space to court coordinates. NBA broadcasts use a moving main camera, so homography must be estimated continuously, not once.
- **Identity:** jersey number OCR plus SigLIP appearance embeddings for re-identification across camera cuts, with team classification from uniform color.
- **Broadcast hygiene:** shot-boundary detection to segment the feed, filtering replays, cutaways, and commercial segments so only live game action enters the pipeline. This is the unglamorous work that determines whether the whole thing functions.
- **Alignment:** synchronize extracted coordinates against official play-by-play timestamps so every possession has both event and spatial views.

### Derived Metrics (The Payoff)

- **Gravity:** defender displacement conditional on an off-ball player's location. Directly quantifies the **Naz Reid void**: how much defensive attention a big above the break commanded, versus what his replacements command.
- **Spacing geometry:** offensive convex-hull area, nearest-defender distances, corner occupancy rates by lineup.
- **LaMelo's transition creation:** hit-ahead pass frequency and the expected-value lift of his outlet passing, which event data systematically undercounts.
- **Off-ball defense:** denial and top-lock frequency for McDaniels, which no public metric currently sees.

### Validation

Sanity-check pipeline outputs against the public tracking aggregates the league does release (speed and distance, touches, drives). If extracted coordinates reproduce those aggregates within tolerance, the novel metrics inherit credibility.

### Rights Note

Compute metrics from broadcast footage for analysis; never republish the footage itself. Publishing derived statistics from watched broadcasts is standard practice across independent analytics outlets, but the line (analysis of broadcasts yes, redistribution of broadcast content no) should be respected deliberately, and it is worth a proper review before this becomes a commercial pillar.

### Effort and Dependencies

The heaviest project on this list: multi-month, with real engineering risk in camera registration and re-identification. No dependencies, but its outputs would upgrade Projects 2 and 3 substantially. This is the long game, and the deepest moat.

---

# Project 7 (In-Season Bonus): Synthetic Control Evaluation of the Trade

**One-line summary:** Once real games start, estimate the causal effect of the LaMelo trade in real time by constructing a "synthetic Wolves" that never made the trade, using the econometrics method built for exactly this kind of policy question.

### Method

- Build a donor pool of historical team-seasons matched on pre-trade covariates: net-rating trajectory, age profile, continuity, star usage structure.
- Fit synthetic-control weights so the weighted donor combination reproduces the Wolves' pre-trade trajectory as closely as possible.
- Track the divergence between the real 2026-27 Wolves and the synthetic no-trade Wolves as the season unfolds.
- Inference via placebo tests and permutation: run the same procedure on donor teams that made no trade and check whether the Wolves' divergence is unusual against that distribution.

### Why It Matters

Every trade evaluation published before games start (including the clean-room work already done) is a projection. This is the instrument that measures the actual effect as evidence accumulates, with a principled counterfactual instead of "compared to last year." Monthly checkpoint pieces write themselves.

### Effort and Dependencies

Light-to-medium. Cannot start producing results until games exist, but the donor pool and matching infrastructure can be built in September so the first checkpoint publishes in November.

---

# Recommended Build Sequence

**Now (July, while free agency is live):**

1. **Project 5, Offseason Solver v1.** Days to a credible version; content value decays fastest. Reuses trade-model cap logic and Joan Bet Monte Carlo. Publish and re-run as signings happen.
2. **Project 4 kickoff.** Extends existing Joan Bet code. Publish in stages: Edwards retention hazard first, joint Wolves-Hornets simulation second, swap option pricing third.

**July through September (the flagship builds):**

3. **Shared ETL first:** one league-wide play-by-play, stint, and lineup warehouse feeding Projects 1, 2, 3, and 7. Build the pipeline once.
4. **Project 1, Fit Engine.** The headline summer build. Validate on historical midseason trades before publishing anything about Ant and LaMelo.
5. **Project 2, Generative Possession Model.** Consumes Project 1 embeddings. Ship the **LAFI forecast before opening night** and commit publicly to scoring it against reality.

**Rolling:**

6. **Project 3, LAFI Causal Layer.** Regime models and transfer entropy can start now on existing LAFI infrastructure; the DML causal estimate is best after Project 1 ships and sharpens further with new-season data.

**September and beyond:**

7. **Project 7 infrastructure in September**, first synthetic-control checkpoint in November.
8. **Project 6, CV tracking**, as the persistent background long game, with the explicit goal of upgrading Projects 2 and 3 once spatial data exists.

### Shared Infrastructure Notes

- A single local warehouse (DuckDB or Postgres) for league-wide play-by-play, stints, lineups, and tracking aggregates serves Projects 1, 2, 3, and 7. Do not build four pipelines.
- Project 1's latent skill vectors are the connective tissue: they condition Project 2's generator, control Project 3's causal model, and drive Project 5's v2 objective. Design their storage format (player-season posterior samples) for reuse from day one.
- Everything publishes with uncertainty shown. Distributions and credible intervals are the house style that separates this work from the field; every project above is designed to produce them natively.

---

# Appendix: Data Sources

| Source | Used By | Notes |
|---|---|---|
| NBA Stats API (nba_api) | P1, P2, P3, P7 | Play-by-play, lineups, stints, tracking and hustle aggregates |
| pbpstats-style possession parsing | P2, P3 | Already implemented canonically in the LAFI pipeline |
| Basketball-Reference | P4 | Franchise win histories, draft outcomes, historical rosters |
| Public contract/cap data | P4, P5 | Contracts, apron lines, exception rules; encode apron mechanics exactly |
| Synergy-style public aggregates | P5 | Play-type distributions for the optimal-transport reconstruction |
| Existing internal codebases | P3, P4, P5 | Canonical LAFI pipeline, Joan Bet championship Monte Carlo, trade-model cap logic |
| Broadcast video (local processing only) | P6 | Analysis of broadcasts, never redistribution of footage |

---

*End of roadmap. Each project section is written to be self-contained enough to hand directly to the implementation agent as a starting spec; the natural next step for any given project is a full implementation plan (architecture, milestones, validation gates) built from its section here.*
