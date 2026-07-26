# Wolves to a T

### A front office in a repository. Frontier analytics pointed at one thing: the Minnesota Timberwolves' first championship.

This repo is the analytical half of a personal project that treats one NBA team the way a real front office treats a title window. It measures what actually happened, prices what the team did, and searches for what it should do next, using methods that usually live behind team and league walls: Bayesian latent-skill models, survival analysis, option pricing, Monte Carlo championship simulation, and a finite-horizon decision solver. The work publishes as the **Wolves to a T** series on the **Chasing the First Banner** site.

Two things make it worth walking through slowly. First, almost every engine here is built to be able to say *no*, including *no* to the idea that commissioned it. Second, almost every number ships with error bars and a paper trail, so a reader can check the work rather than trust the tone.

> One fan, one question (the banner), attacked with the honest version of the hard tools. Where the honest answer is "we cannot tell yet," the machine is built to print that instead of a comfortable number.

---

## The one idea

Sports analytics usually rewards confidence. This project rewards being right, and treats "I do not know" as a valid and sometimes final answer. That principle is not a slogan bolted onto the writeups. It is wired into the code:

- **The Joan Bet engine rejected its own thesis.** It was commissioned to show that the Wolves should bet on young center Joan Beringer and trade Rudy Gobert. Run honestly, it found that move is a title-odds **downgrade of about 1.14 percentage points** and it beat standing pat in only **18% of simulated draws**. Three of the thesis's supporting pillars fell one by one to measurement. (`core_max/docs/phase3_verdict.md`)
- **The LaMelo and LeBron evaluations refuse to publish a title percentage.** Both compute one internally, then decline to print it because a pre-registered back-test of the engine's star-acquisition accuracy fails (5 of 8 signs correct), and because single-season noise is larger than the effect being measured. The published product is the honest decision structure, not a fake-precise number. (`lamelo/DELIVERABLE.md`, `alebron/DELIVERABLE.md`)
- **The LAFI predictive claim was pre-committed at 10% confidence, then reported as failing its own correction.** The headline "chaos predicts playoff failure" claim did not survive multiple-testing correction, and the writeup says so plainly, then reports the weaker signal that did survive. (`postmortem/outputs/findings/q0a_lafi/08_phase4_predictive_validation.md`)
- **The offseason board publishes its own worst gaps.** Its trade-acceptance model tops out at 16% recall on real trades, so the project prints that limitation and scopes the model to only the verdicts it can support. (`offseason/docs/acceptance_model_scope_and_limitation.md`)

That is the personality of the codebase. The rest of this document is a tour of what it contains.

---

## The data spine

Nothing here re-scrapes the internet at analysis time. The whole project reads from one warehouse through one small door.

- **Source of truth: a Postgres database** (`nba_warehouse`, schema `nba`) living on a home server, filled nightly by a **separate sibling repo (`nba-warehouse`)** that handles ingestion and the `stats.nba.com` bypass. It holds play-by-play back to **1997**, box scores, tracking, Synergy play types, shot charts, rosters, and transactions. The heavy play-by-play table alone is roughly **17 million rows**.
- **One connection helper.** Every subsystem reaches Postgres through a single ~115-line psycopg2 helper (`postmortem/lib/db.py`) that pins the schema and reads credentials from a gitignored `.env`. Clean-room subsystems import that helper and nothing else, so reproducibility is architectural rather than promised.
- **A derived parquet cache, about 35,000 files.** The expensive step (turning raw play-by-play into per-possession and per-stint tables) is done once and frozen: **15,668 per-game stint files, 15,668 per-game possession files**, plus a league-wide possession cache. These load into a local **DuckDB** file (`fitengine.duckdb`, over 800,000 stint rows) or are read directly with pandas. A hard validity gate aborts the load loudly if any lineup does not contain exactly five players.
- **Dated, content-hashed snapshots.** When a study needs to be pinned while the live warehouse keeps moving (for example, freezing the world as of a trade date), it exports a hashed parquet snapshot so the result stays reproducible forever.

Every subsystem follows the same path: **raw Postgres, to frozen snapshot, to derived features, to outputs, to article and social**. Any published figure can be rebuilt from the raw table.

---

## The projects at a glance

| Directory | What it answers | Status | A headline number (verified from output) |
|---|---|---|---|
| `postmortem/` | Why did the 2025-26 Wolves collapse on offense in the playoffs, and is their "pickup ball" style a measurable, playoff-predictive flaw? | Shipped | Playoff offensive rating fell **7.9 points** (113.8 to 105.8) vs a 3.8 historical norm; 3-point rate collapsed from **42.0% to 34.4%** of shots. |
| `counterfactual-fit-engine/` | How would a lineup that never existed perform (Edwards next to LaMelo), separating real fit from summed talent? | In progress | Bayesian skill vectors fitted for **5,838 player-seasons, 1,346 players**; worst R-hat **1.0027**. Synergy layer (the actual lineup score) not built yet. |
| `lamelo/` | Did the LaMelo Ball trade actually make the Wolves better, and by how much? | Shipped (number gated) | Two honest metric forks land at **+0.005pp vs +1.113pp** title change; the band crosses zero, so no single title % is published. |
| `alebron/` | Now that LaMelo is here, what would signing 41-year-old LeBron James do, and can they even afford him? | Shipped (number gated) | Fits **only at the veteran minimum**; title change stays positive across the whole fit fork (**+0.3 to +2.5pp**), but the number is declined on the same gate as LaMelo. |
| `pick2033/` | What did the LaMelo trade actually cost in draft assets, priced like financial options? | Shipped | The 2033 unprotected pick is a coin over the board: **P(lottery) 61.9%, P(top-4) 15.7%**. Charlotte collects roughly **twice** the title equity Minnesota loses. |
| `2033-posterior/` | The design authority (spec) for the pick-pricing project. | Spec only | The blueprint `pick2033/` executes and overrides. |
| `offseason/` | Under a hard cap and a thin pick chest, what should the Wolves do, across all 29 trade partners? | Shipped | Of 29 partners, **13 legal deals, 8 clear the bar, 16 return nothing**. No trade that ships Gobert wins anywhere. |
| `core_max/` | Should they bet on Joan and trade Gobert and Randle (the "Joan Bet")? | Shipped | **No: about -1.14pp.** The better shape is keep Gobert, retool only the Randle slot (up to **+0.77pp**). |
| `all-for-one/` | If you ran the front office, what is the pre-committed best move at every future decision point while Ant is a Wolf? | In progress | A finite-horizon decision solver: **9.95M naive states pruned to 17,743 reachable** (a 560x cut). Frozen Oct 2026. |

Figures throughout are the project's models and projections of a hypothetical and in-progress 2026 offseason. Several subsystems carry an explicit `is_projection` flag and treat only the model-vs-model deltas as robust, not the absolute levels.

---

## The projects in depth

The subsystems form a natural arc: **measure, value, price, decide, explore, publish.**

### 1. Measure what happened: `postmortem/` (the LA Fitness Index)

The flagship descriptive engine, and the origin of the whole project. It rebuilds every NBA possession from raw play-by-play with a state machine (`lib/pbp.py`) that unifies two different NBA data dialects, infers missing rebound flags from shot context, and correctly retro-credits and-1 free throws.

On top of that it defines **LAFI, the LA Fitness Index**: five components that score how much a team's offense looks like pickup ball at the gym (sticky ball, dead off-ball motion, isolation reliance, a thin playbook, bad shots), each z-scored within season for era control, converted to a percentile, and combined.

The findings are specific and honestly hedged:

- The 2025-26 Wolves rank **3rd in the NBA (90th percentile)** on the sharp version of LAFI (behind only Philadelphia and the Clippers), but only **13th on the full index**. The gap between those two ranks *is* the diagnosis.
- League-wide, motion death and shot-quality decay are **essentially uncorrelated** (r = 0.059 across 330 team-seasons). The Wolves moving in lockstep on both is the anomaly, the single most diagnostic number in the analysis.
- A four-quadrant offensive taxonomy built by eye was then **independently surfaced by the second principal component** of a PCA. The data found the framework rather than the framework being imposed. It shows the Wolves invented a rare "distributed pickup" failure mode, not the known single-star one.
- Of 7 historical teams matching the Wolves' architectural profile, **0 reached a conference finals.** The writeup flags the strict reading of that as an overclaim on 7 teams, and says so.

Run it: `python -m analyses.q0a_lafi --composite` then `--validate`.

### 2. Value the players: `counterfactual-fit-engine/` (Project 1)

The most ambitious build, and the most honest about being unfinished. The goal is to score five-man lineups that have never shared a floor (the marquee case is Anthony Edwards next to LaMelo Ball) by learning fit as an interaction, not a sum.

What is actually built and validated today:

- **Layer 0**, a rebuilt possession and stint panel over **15,669 games**, reconciled against official minutes to **99.93% within half a minute**.
- **Layer 1a**, per-season ridge RAPM with the regularization strength frozen once and locked against re-tuning, passing a pre-registered year-over-year stability band.
- **Layer 1b**, a measurement-error-aware Bayesian factor model in NumPyro. Its neat trick: it analytically marginalizes out the tens of thousands of latent player scores so the sampler only explores about **197 parameters**, and it feeds each player's RAPM uncertainty back in as measurement noise so shaky estimates are trusted less. Output is an 8-dimensional skill vector for **5,838 player-seasons**, both Edwards and LaMelo among them.
- **An identity audit that caught a real problem.** Rather than trust the factor labels, it verified each axis with high and low exemplar players and found **3 of 8 factors had drifted off their intended meaning** (one nominal "defense" axis was actually pull-up shooting, led by Harden and Luka). That failure is invisible in the loadings and only shows up in exemplars.

**Honest status:** the layer that actually scores hypothetical lineups (the synergy model) is scaffolding and smoke tests only. **The Edwards-times-LaMelo counterfactual number does not exist yet.** The pre-registered predictions are logged and ungraded, and the sealed back-test window is deliberately untouched.

### 3. Price the trade that happened: `lamelo/` and `pick2033/`

Two sides of the same coin. `lamelo/` prices the **on-court** effect of the LaMelo Ball trade; `pick2033/` prices the **asset cost**.

**`lamelo/` (clean-room championship evaluation).** Rebuilt from scratch with no numbers borrowed from earlier projects, every assumption and forward prediction locked in writing before running. LaMelo is valued two independent ways, one that can see defense (RAPM) and one that mostly cannot (box score), carried as two internally consistent forks all the way through a 20,000-season simulation. The two forks disagree by **almost exactly the amount of defense a box score cannot see**, and an out-of-sample test cannot say which is right. Because the honest band straddles zero and leans slightly negative once a contested throw-in player is valued reliably, the project **declines to print a title percentage** and publishes the decomposition instead. When the pre-registered back-test fired, the committed consequence was honored, and an independent red-team audit then walked back the project's own overclaims.

**`pick2033/` (the 2033 pick posterior and swap option pricing, Project 4).** This is the genuinely novel financial move. It treats the traded picks as a portfolio of path-dependent options and prices them by simulating both franchises' futures **50,000 times** from 2027 through 2033, inside a full simulated league with the post-2026 sixteen-team lottery.

- The **2033 unprotected first** is a coin over the board: **top-4 15.7%, top-10 39.1%, lottery 61.9%.**
- Each swap is priced as an option (it only pays in the worlds where Charlotte's pick beats Minnesota's), on top of an ordered ledger that resolves what Charlotte can actually capture through Minnesota's pre-existing pick obligations.
- The punchline is an **asymmetry**: in title-equity terms the package delivers Charlotte a mean **8.27 points** but costs Minnesota only **4.51**, because the bill comes due in exactly the collapsed-Minnesota futures where title equity is already gone.
- The load-bearing input is an actuarial **Edwards retention hazard**: cumulative probability he has departed by 2033 is **56.4%** at a winning pace, with the annual hazard spiking to **44.0%** in his 2029 walk year.

The rigor is unusual: sealed holdouts, pre-registered predictions graded after the fact, a 15-arm stress test declared before running, an as-of-2013 replay of the Celtics-Nets picks, and **red gates documented and defended rather than tuned away** (a calibration slope of 1.413 and a 3-of-4 replay both stand on the record).

### 4. Decide what to do next: `offseason/`, `core_max/`, `all-for-one/`

**`offseason/` (the offseason engine and trade board).** This is the shared championship machinery the rest of the monorepo reuses. An in-house ridge RAPM value spine (fit from the team's own possessions), a two-sided playoff Monte Carlo with a principled survivorship model, a deterministic CBA feasibility gate that runs **before** any move is scored (so an unaffordable star can never outrank an affordable fit), and a trade-acceptance model that asks whether the other team would say yes. It sweeps all 29 partners and reports, honestly, that most deals do nothing worth the picks. Every title number is a **four-view spread** (consensus, box, RAPM, and the conservative DARKO anchor) so the pipeline structurally refuses false precision. It also caught and corrected its own biases, including an adverse-selection artifact where its first pass surfaced exactly the high-surplus players nobody actually trades.

> Note on the roadmap. The planning document imagined this as an optimal-transport plus mixed-integer-program solver. The shipped code is ridge RAPM, a Monte Carlo bracket simulation, a rule-based cap gate, and a heuristic acceptance model. Treat the transport and MILP language in the roadmap as aspirational. The engine that exists is the one described here.

**`core_max/` (the Joan Bet).** A standalone study built on the offseason engine, and the clearest example of the project's spine. Young players are not plugged in as a guess; Joan is sampled from an empirical distribution of how similar prospects actually developed (a sobering **64% chance of replacement-level** in the faithful comp class). The rim-protector correction is deliberately switched **off** for Joan to avoid trusting his tiny rookie sample, and the uncertainty calibration used a held-out test that **refused to inflate the error bars** even though inflating them would have flattered the thesis. Commissioned to prove "bet on Joan, trade Gobert," it returned **-1.14pp** and pointed at the opposite shape: keep Gobert, retool only the Randle slot, worth up to **+0.77pp**.

**`all-for-one/` (ONE FOR ALL, the board).** The most structurally ambitious piece: a genuine **finite-horizon decision process** for a single franchise. It compresses every situation the team can be in through 2028 into a short state vector, prunes a naive **9.95 million** states down to **17,743 reachable** ones, and solves by backward induction, where a retention hazard reads the solver's own forward equity to decide how likely Ant is to stay (the value function feeds back into the transition model, which is the hard, elegant part). RAPM and box are carried as two first-class forks that genuinely disagree about the LaMelo trade, so every headline is a range. It ships with a companion **tripwire backtest** that pre-registers which in-season alarms are trustworthy enough to force a trade, and a **deterministic SHA-256 freeze** so a future article can prove nothing was chosen after the fact. **Nothing is frozen yet** (the target is October 2026), and several key values are the owner's logged rulings, not model outputs.

### 5. Explore the hypothetical: `alebron/` (the LeBron clone)

A clean clone of the LaMelo evaluation, pointed at a "what if LeBron signs?" scenario, to show the engine can deliver a rigorous mirror image rather than just repeat a result. The technical crux is **common random numbers**: running the current roster against roster-plus-LeBron on identical draws cancels field-modeling error, proven by the delta barely moving (**1.243 to 1.206pp**) when the entire league field is updated for real 2026 trades. The transport layer consciously **inverts** the LaMelo choice (aging applied to net impact, not to offense) because applying a shrink factor to LeBron's negative RAPM offense would perversely raise his value. The finding is the near-mirror of LaMelo: a near-free, downside-truncated, positive-leaning bet that fits **only at the veteran minimum**, with the point title percentage declined for the same honest reasons.

### 6. Publish it: the content and visualization layer

The analysis becomes public work through three distinct rendering stacks under one design language: **D3** for interactive article charts, **Remotion** (React and TypeScript) for voiced 9:16 vertical reels, and hand-written **PIL** renderers for carousel slides and the "board" stills. Two rare disciplines run through all of it:

- **Every on-screen number is re-validated by a script** (`validate.py`) that re-runs the model before a slide ships. Numbers are never hand-typed onto a graphic.
- **A written perceptual-science doctrine** (`phyc-of-users-scrolling.md`) separates the job of the visual (stop the scroll) from the job of the words (earn the click), grounded in real citations (Itti-Koch saliency, Potter's 13ms gist, the information-gap theory of curiosity).

The board visualization engine is a standout: it treats a chart as a physics problem, insisting brightness equal probability mass in linear light, and that histories reaching the same state must visibly **merge** (a lattice, not a tree: the real object has 12,565 states and 1,376 merge-nodes). It keeps a critique log that scores each iteration and an epitaph file for rejected geometries.

---

## How it is built

**Language and modeling.** Python throughout. Bayesian inference in **NumPyro / JAX** with NUTS and ArviZ diagnostics. Survival analysis with **lifelines**. Adjusted plus-minus via **scikit-learn** ridge. Gradient boosting (**LightGBM**) and set-attention networks (**PyTorch**) in the fit engine's synergy scaffolding. Data in **DuckDB**, **pandas**, and **pyarrow**. Video in **Remotion**, charts in **D3**, stills in **PIL** and **numpy**.

**The rigor apparatus** is the real signature. It recurs, deliberately, across subsystems:

- **Pre-registration.** Predictions and kill criteria are logged in writing before the fit runs, then graded honestly afterward.
- **Sealed holdouts.** Back-test windows are walled off from every fit and get exactly one look.
- **Gates that stop the line.** A feasibility or validity check runs before scoring; a red gate produces a decision memo, not a silent retune.
- **Metric forks.** Where two defensible measurements disagree (RAPM vs box), both are carried end to end and every headline is a range.
- **Common random numbers.** Two scenarios are compared on identical draws so the difference isolates cleanly from Monte Carlo noise.
- **Content-hashed freezes.** Results are pinned to a snapshot hash so any figure can be reproduced exactly.
- **Adversarial verification.** Independent passes hunt for silent-but-plausible bugs, and they find real ones (a phantom roster player inflating a net rating, a percent-vs-fraction scale bug that would have silently returned an empty sample).

The repo even ships its own house methodology as **Claude Code skills** under `.claude/skills/` (an `analytical-rigor` skill, `viz-builder`, `wolves-reels`, `trade-posts`, and the `storytelling-for-chasing-the-first-banner` narrative skill), so the working norms travel with the code.

---

## Repository map

```
wolves-front-office/
  postmortem/                  LAFI + the 2025-26 season postmortem (the descriptive flagship)
  counterfactual-fit-engine/   Project 1: Bayesian skill vectors + lineup synergy (in progress)
  lamelo/                      Clean-room championship eval of the LaMelo Ball trade
  alebron/                     The LeBron-signing clone of the LaMelo eval
  pick2033/                    Project 4: the 2033 pick posterior + swap option pricing
  2033-posterior/              The design-authority spec for pick2033
  offseason/                   The shared championship engine + the all-29-partner trade board
  core_max/                    The Joan Bet: should they bet on Joan and trade Gobert?
  all-for-one/                 ONE FOR ALL: the finite-horizon decision board + tripwire backtest
  wtat-frontier-analytics-roadmap.md   The 7-project frontier roadmap (planning source of truth)
  phyc-of-users-scrolling.md           The perceptual-science doctrine for the social layer
  .claude/skills/              The house methodology, shipped as reusable skills
  .env                         Postgres credentials (gitignored)
```

Data lives in each subsystem under `data/` (frozen snapshots and caches) and results under `outputs/` (JSON exports, parquet, and dated findings logs). The heaviest shared cache is `counterfactual-fit-engine/data/cache/`.

A few root folders (`analyses/`, `lib/`, `scripts/`, `outputs/`) hold an earlier root-level LAFI scaffold that has since moved into `postmortem/`, plus compiled artifacts. `social-posts/` is an empty placeholder. The live, current work is in the named subsystems above.

---

## Running it

**Prerequisites.**

1. **Warehouse access.** The data is in the sibling `nba-warehouse` Postgres instance, reachable over Tailscale. Join the tailnet, then `cp .env.example .env` and fill in the `POSTGRES_*` password. Analysis code fails loudly if the file is missing rather than falling back to a stale local database.
2. **Per-project environments.** The newer subsystems (`counterfactual-fit-engine/`, `pick2033/`) carry their own `.venv` and `requirements.txt`. Install with `python -m venv .venv` then `.venv/Scripts/pip install -r requirements.txt`.

**Some real entry points:**

```bash
# The LAFI index and its predictive validation
python -m analyses.q0a_lafi --composite
python -m analyses.q0a_lafi --validate --include-covid

# The Joan Bet verdict (keep-vs-trade, with confidence intervals)
python core_max/engine/run_scenarios.py

# The full 29-partner offseason trade board
python offseason/scripts/trade_search.py

# The 2033 pick posterior (about 4 minutes for 50k league paths)
python pick2033/src/sim/run_engine_d.py 50000 --tag=FINAL

# The LeBron evaluation, gates included
python alebron/sim/run_sim.py
python alebron/sim/run_gates.py

# A social reel (Remotion)
cd postmortem/social/lafi-fingerprint && npm install && npm run render
```

Most stochastic scripts take their seed from a config file and cache their fits, so a re-run reproduces the published numbers exactly rather than refitting.

---

## A note on status, and on honesty

Because the project prizes honest uncertainty, so does this README. The current state, plainly:

- **Shipped and reproducible:** `postmortem/` (LAFI and the postmortem), `lamelo/`, `alebron/`, `pick2033/`, `offseason/`, `core_max/`, and the published articles, carousels, and reels.
- **In progress:** `counterfactual-fit-engine/` (skill vectors done and validated; the synergy layer that scores hypothetical lineups is not built, so the Edwards-LaMelo number does not exist yet) and `all-for-one/` (solved through step 7, nothing frozen until October 2026, several values are logged rulings rather than model outputs).
- **Known soft spots, self-disclosed in the code:** absolute title levels are approximate (only model-vs-model deltas are treated as robust); the trade-acceptance model is scoped and un-calibrated; a couple of validation gates stand red on the record rather than being tuned away; and the fit engine carries a documented caveat on 3 of its 8 factor names.

None of that is hidden in the subsystems, and it is not hidden here. That is the point.

---

*Wolves to a T is a personal project by a lifelong Timberwolves fan and data scientist, written for an audience of one imaginary reader: the team's front office. Every number above was read out of a real output file. Where the honest answer was "we cannot tell yet," the machine printed that instead.*
