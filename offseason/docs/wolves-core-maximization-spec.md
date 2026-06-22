# Project Spec: Core Maximization (working title: "The Joan Bet")

**Status:** One-off analysis. NOT part of The Line for now.
**Horizon:** 1 to 2 years.
**Owner:** Bobby / ScoutIQ.
**Last updated:** June 19, 2026 (pre-draft, draft is June 23-24).

---

## 0. North Star (plain-language summary)

> **Spirit of this project:** we are hunting for the team nobody believed in, the one so well-fit it raises everyone's floor and shocks the league. That outcome is the right tail of the model, and the whole engine exists to find it and price it honestly. The guardrails are not here to suppress upside. They are here to make the upside credible, so that when the model believes, the belief means something. Optimize for the real version of the dream, never the manufactured one.

Maximize the existing Timberwolves core instead of star-hunting for the biggest name. Fix the offensive architecture the LAFI work exposed, without breaking the elite defense. Choose fit over splash every time. Bet on Joan Beringer as the long-term center. Build a championship-equity model that correctly prices young-player development, because a naive title-odds model will systematically discount the exact young upside this whole plan is built on.

The deliverable is two things at once: a captured strategic thesis (the decisions, locked) and a build spec for the model and tooling that evaluates it.

---

## 1. Thesis

1. **Maximize the core, do not tear it down.** Untouchables: Anthony Edwards, Jaden McDaniels, Naz Reid, Joan Beringer, Terrence Shannon Jr. (TSJ movable only as a reluctant must-include sweetener).
2. **The problem is offensive architecture, not talent.** Per The Ceiling / LAFI work: Sharp LAFI 90, movement death, isolation reliance, spacing clogged by a non-shooting Gobert plus a below-average-shooting Randle. Top-five defense, half-court offense that collapses against elite playoff defenses.
3. **Fit over splash.** The goal is the player who dissolves the LAFI problem, not the player who relocates it. Adding a second ball-dominant, defense-light alpha (Morant archetype) just gives the iso problem a backcourt partner. Run from it.
4. **Bet on Joan.** DECISION LOCKED: Fork B (see Section 6). Gobert's replacement is not a center. We hand the starting-5 keys to Joan and accept Year-1 defensive variance as the price of the development bet.
5. **The objective is P(championship), a tail event.** We are not maximizing expected wins. Title probability is convex in team strength at the top, so variance and young-player upside are assets the model must capture, not noise to average away.

**Non-goals:** generic trade machine, teardown/rebuild, biggest-name star-hunting, maximizing regular-season expected wins.

---

## 2. Motivation / context (the "why this exists")

Franchise-emotional throughline: this is about making the Karl-Anthony Towns return win in Minnesota. Joan Beringer literally is that return (KAT to New York for Randle, DiVincenzo, and the No. 17 pick that became Beringer). The plan to bet on Joan is, structurally, the plan to make the thing we got for KAT into a winner. That framing motivates the project but does not override the math.

---

## 3. The core (untouchables) and contracts

| Player | 2026-27 | Status / role | What they need around them |
|---|---|---|---|
| Anthony Edwards | $48.9M | Pillar, signed through 2029. Elite three-level scorer, high usage, improving but score-first | A secondary creator to share load and punish help; elite spacing |
| Jaden McDaniels | $26.2M | Locked through 2028-29. Elite wing/POA defender, low usage, growing offense | Defined, larger offensive role; does not need the ball |
| Naz Reid | $23.2M | Long-term, 2029-30 player option. Stretch big, plays 4 or 5, microwave scorer | Best as stretch-4 / play-finisher, not the lone rim protector |
| Joan Beringer | rookie scale (yr 2) | The KAT-trade pick. Athletic rim-runner / rim-protector, developmental | RUNWAY. Real starter minutes. (See Section 6.) |
| Terrence Shannon Jr. | rookie scale (yr 3) | Athletic downhill scoring wing. Cheap surplus, internal-leap candidate | Role and minutes to pop |

TSJ note: keeping him is the correct analytical call independent of any personal attachment. A third-year athletic scoring wing on a rookie deal is exactly the cheap surplus that funds an expensive top end.

Ranked needs of this core:
1. Secondary on-ball creator next to Ant (biggest hole).
2. Spacing (replace the frontcourt clog with shooting).
3. Modern, switchable rim protection that does not clog (the Joan bet, plus scheme).
4. Guard depth / wing shooting (DiVincenzo's Achilles injury makes this acute, see Section 4).

---

## 4. Movable assets and ammunition

| Asset | 2026-27 | Notes |
|---|---|---|
| Rudy Gobert | $36.5M | Player option 2027-28 ($38.0M). The Joan blocker. Primary trade chip. |
| Julius Randle | $33.3M | Player option 2027-28 ($35.8M). Primary trade chip. Skipped exit presser. |
| Donte DiVincenzo | ~$12M | Expiring. Out most or all of 2026-27 (Achilles). Useful matching salary + sweetener. |
| Mike Conley | ~$10.8M | Aging, expiring-ish. Matching salary. |
| Draft picks | No. 28, No. 59 (2026) | Only cleanly tradeable first is essentially No. 28. 2032 first frozen, 2034 at risk. |
| Trade exceptions | $10.8M, $7.6M, $6.6M | Using any of them hard-caps at the first apron. |

Asset constraint that shapes everything: thin draft capital means any creator we land carries a wart the market is down on. That is fine. That is the OKC model.

---

## 5. CBA-feasibility gate (HARD CONSTRAINT, evaluated before anything else)

2026-27 league lines (approx): cap ~$165M, luxury tax $200.5M, first apron $209.1M, second apron $222M.
Wolves current standing: ~$8M below tax, ~$14M under first apron, ~$27M under second apron. Ten players under contract at ~$193.4M.

**Operating-zone rule (the gate):**

- **Above first apron, below second apron = the sweet spot.** This is the only zone that lets us aggregate Gobert + Randle into one incoming player, with incoming capped at 100 percent of outgoing. Taxpayer MLE (~$6M) available.
- **Above second apron = forbidden.** No aggregation, no sign-and-trade, 2034 first frozen (2032 already frozen). This kills the entire mechanism.
- **Below first apron = unrealistic.** Would require gutting the roster; not a win-now path.

**Binding constraint: stay below the second apron.**

Ayo Dosunmu: Bird rights held from the deadline trade, so he can be re-signed over the tax/apron. Eligible for a 3-year, ~$52.4M extension before June 30. Re-signing is close to mandatory given DiVincenzo's injury. Reported math: to re-sign Ayo and stay under the second-apron hard cap, Minnesota needs to shed roughly $58.5M in salary, which is basically the Gobert-plus-Randle outflow.

Gate implementation: every candidate roster/plan must return PASS/FAIL on (a) below second apron, (b) Ayo retained, (c) roster filled to minimum, before its title equity is even computed. No FAIL plan gets evaluated.

---

## 6. Trade architecture (strategy, with one decision locked)

### 6.1 Two packages, not one (default)

Fit-over-splash structurally argues for two separate fit trades over one aggregated blockbuster:

- **Aggregated (one deal):** ~$70M out for one ~$70M player. Definitionally a splash. Lose a net rotation spot, concentrate all acquisition risk on one body's health and fit. High ceiling, thin depth.
- **Two separate deals:** Gobert's $36.5M into one ~$30-36M fit, Randle's $33.3M into another. Two good fits, keep the body count, solve two different needs precisely.

**Rule:** default to two trades. Collapse to one aggregated deal ONLY if a specific perfect-fit player is worth more than two fits plus our depth. We do not need to aggregate; aggregation is a tool reached for only for the right single player.

### 6.2 The Joan Fork (LOCKED: Fork B)

The Gobert decision is a referendum on Joan. We cannot call Joan an untouchable development priority and keep Gobert hogging the 5.

- ~~Fork A (hedge): Gobert for another good center (Claxton archetype). Safer, keeps rim-protection floor, but buries Joan. This is choosing not to bet on Joan.~~ REJECTED.
- **Fork B (the bet) — LOCKED:** Gobert for a wing/guard, or for relief plus picks. Hand starting-5 keys to Joan, Naz as stretch-4 and backup-5. Accept Year-1 defensive variance. This is the only Gobert outcome internally consistent with the Joan bet, and it is the OKC move (give the cheap young guy real run, eat the volatility).

Implication: the Claxton-type return is OFF the table for the Gobert trade, because it conflicts with Fork B. Note this when screening the Nets MPJ/Claxton framework.

### 6.3 The Randle trade (fit target)

Trade Randle for a secondary creator and/or shooting that fits next to Ant and is lower-usage compatible. Archetypes:
- Pick-and-roll creator with shooting (Garland-type): compatible with Ant's usage. Wart: injury history.
- Size + shooting + scaling creation wing (MPJ-type): great spacing fit, scales up or down. Wart: cost/role questions.

Avoid: another alpha (Morant/Trae). Do not relocate the LAFI problem.

Live context to screen against: the Randle + DiVincenzo + No. 28 package is already reportedly being shopped for a star-caliber player. The Nets are reportedly making MPJ and Claxton available. We can use MPJ as a Randle-side fit target; we do NOT take Claxton on the Gobert side (Fork B).

---

## 7. The modeling system (the build)

This is the core engineering deliverable: a championship-equity engine that does not throw away young-player upside.

### 7.1 Title-odds Monte Carlo (championship-equity engine)
- Inputs: per-player season-long impact estimates → team strength → simulate regular season and playoffs → P(title).
- Output: title-probability distribution and the multi-year (1 to 2 season) integrated title equity for a given roster/plan.
- Design principle: the engine evaluates plans, not single trades. A plan is a full offseason (trades + Ayo + MLE + draft + minutes allocation) that has already passed the CBA gate.

### 7.2 Young-player potential module (the key innovation)
- Represent young players (Joan, TSJ, and any acquired youth) as predictive DISTRIBUTIONS over the horizon, not point estimates.
- Mean drift from an age/development curve (peak ~26-27).
- Spread from prospect-level uncertainty. Right-skew for high pedigree / high flash, but an honest left (bust) tail.
- Estimation: Bayesian hierarchical model with partial pooling toward archetype-specific developmental trajectories. Predictors: age, draft slot, minutes, early-career production, role. Reuse the Settlers After Dark hierarchical infrastructure / approach (per-role hidden-skill modeling transfers directly).

### 7.3 The non-negotiable simulation rule
- SAMPLE each young player's season impact from their distribution on EVERY Monte Carlo iteration. Do not collapse to the mean before simulating.
- Title probability becomes an integral over the joint distribution of player outcomes. The scenarios where Joan or TSJ pop show up as real added title-probability mass.
- If you plug in expected values and then simulate, you have already destroyed the upside. Order of operations is the whole game.

### 7.4 Convexity / tail design principle (document so it is never "re-meaned")
- Objective is P(title), a tail event. Title probability is convex in team strength at the top, so variance can be an asset.
- A higher-variance fit-and-develop roster can carry more title equity than a higher-floor splash roster at equal or even slightly lower expected wins.
- Modeling young upside is not generosity to the kids. It is the only way the objective function is correctly specified.

### 7.5 Real-options valuation of the Gobert trade
- Trading Gobert buys the option on Joan's development plus future flexibility. Option value scales with variance and time horizon.
- Quantify directly: the gap in the UPPER-PERCENTILE title-prob distribution, and the multi-year integrated title equity, between the keep-Gobert branch and the trade-Gobert/develop-Joan branch.
- That delta is the number a naive point-estimate model hides.

### 7.6 Calibration and guardrails (adversarial, non-optional)
- Calibrate developmental distributions against historical comparables: how did similar age / pedigree / early-production bigs and wings actually develop? Let the data set the skew.
- Model the left tail honestly. Do not hand-set upside.
- Anti-goal, stated explicitly: do not build "confirmation bias with a Monte Carlo wrapper." Sensitivity analysis required on the young-player priors. If the conclusion only survives under optimistic Joan priors, that must be surfaced, not buried.

### 7.7 Scenario comparison harness
- Evaluate candidate plans head to head on title-equity DISTRIBUTION (and percentiles), not point estimates.
- Minimum scenario set:
  1. Keep everything (status quo baseline).
  2. Fork B plan (Gobert → wing/guard, Randle → fit creator, Joan starts, re-sign Ayo, MLE shooter).
  3. Splash counterfactual (Morant-type aggregated deal) for contrast.
- Outputs per scenario: CBA gate pass/fail, title-prob distribution, integrated multi-year equity, upper-percentile equity, and the option-value delta vs. baseline.

---

## 8. Data requirements
- Multi-season RAPM (existing models) for established-player impact posteriors.
- Current-season impact metrics.
- Canonical LAFI pipeline (offensive-architecture context and fit screening).
- Contract / cap data (Spotrac, Fanspo, salary sources) for the CBA gate.
- Historical young-player development dataset (for Section 7.6 calibration).
- Draft prospect data for No. 28 / No. 59.

---

## 9. System architecture / build notes
- Target environment: home Ubuntu / Linux server with PostgreSQL (existing infra). Python for modeling.
- Pipeline: data ingest → priors and distributions → Monte Carlo engine → scenario harness → reporting.
- Modular components:
  - CBA-gate module (deterministic, validates against known cap numbers).
  - Roster-impact module (established players as distributions from RAPM posteriors).
  - Young-player distribution module (Section 7.2).
  - Monte Carlo title engine (Section 7.1 and 7.3).
  - Scenario harness + real-options valuation (Section 7.5 and 7.7).
  - Reporting / decision outputs.
- Reproducibility: config-driven scenarios, fixed seeds for comparability, versioned priors.

---

## 10. Build phases / milestones
- **Phase 0:** Data inventory plus CBA gate. Deterministic. Validate against current cap lines.
- **Phase 1:** Roster-impact baseline. Established players as distributions from RAPM posteriors.
- **Phase 2:** Young-player distribution module plus historical calibration (the differentiator).
- **Phase 3:** Monte Carlo title engine with correct per-iteration sampling.
- **Phase 4:** Scenario harness plus real-options Gobert valuation.
- **Phase 5:** Reporting / decision outputs.

---

## 11. Decisions LOCKED (do not relitigate)
- Fit over splash. Run from Morant.
- Bet on Joan = Fork B. Gobert's replacement is not a center.
- Two-trade default; aggregate only for the perfect single fit.
- Stay below the second apron.
- Model young players as sampled distributions, never collapsed means.
- Objective is P(title), a tail event.

---

## 12. Open questions / pending decisions
- Which Randle return archetype to model first: Garland-type (PnP creator) vs MPJ-type (creation + spacing wing)?
- Integrated horizon: 1 year or 2?
- Historical comp-set definition for young-player calibration (age band, pedigree band, minutes threshold).
- Risk posture: pure P(title) max, or impose a floor constraint (e.g., do not drop below a defensive-rating threshold in Year 1)?
- Whether and when to fold this into The Line later (currently: no).
