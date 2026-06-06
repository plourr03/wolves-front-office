# Timberwolves 2026 Offseason: Series Planning Document

**Status:** Planning and analytical design. No articles written yet.
**As of:** June 5, 2026 (18 days before the draft, 25 before free agency opens).
**Scope:** This series is independent. It does not build on, cite, or assume the reader has seen any prior retrospective work. Every finding below is to be derived freshly from the warehouse and from public data verified in June 2026.

A note on confidence before anything else. The asset and cap facts in this document were verified against current public reporting (ESPN's Bobby Marks, Spotrac, The Third Apron, team beat writers) and a few items in the original brief had drifted. Those corrections are flagged inline. The need analysis and the metric are designed to produce conclusions, not to import them, so where this document states a directional read about what the Wolves need, it is labeled as a hypothesis to be confirmed by the data work, not a finding.

---

## 1. Foundational facts (the asset reality)

### 1.1 The picks

The Wolves are thin on draft capital, and the exact shape matters for every trade we model.

- **2026 first-round pick: No. 28**, not 29. Reporting is uniform on 28. Final slotting depends on the league's standings order and the Conley-trade pick swap with Detroit, so confirm the exact number once the order is locked, but plan on 28. The pick can only be traded **on or after draft night** (Stepien-rule mechanics), which is a timing constraint, not a yes/no.
- **2033 first-round pick** (their own, the earliest future first they can move outright under the seven-year rule).
- **A 2028 first-round swap.** This is a real third chip the original brief omitted, though a swap is a weaker asset than an outright pick and its value depends on where both teams finish.

So the honest framing is not "two tradable firsts." It is one outright near pick (28, draft-night only), one outright distant pick (2033), and one swap (2028). Second-round capital is depleted: four seconds went to Chicago in the February Dosunmu deal, and only the 2029 second is trade-ineligible among what remains. ESPN's asset rankings peg the Wolves near the bottom of the league for tradable future firsts, which is the binding reality for any star pursuit.

### 1.2 Cap and apron position

Working from the 2026-27 projections (cap roughly $165M, luxury tax roughly $201M, first apron roughly $209.1M, second apron roughly $222M):

- Per Bobby Marks, the Wolves enter the offseason roughly **$8M under the tax, $14M under the first apron, and $27M under the second apron.**
- They hold **three trade exceptions** (about $10.8M, $7.6M, and $6.6M). Using any of them **hard-caps the team at the first apron** ($209.1M).
- The single most important mechanical fact for the whole series: **to re-sign Dosunmu and stay under the second-apron hard cap, the Wolves must send out at least $58.5M in salary** (Marks). That number is what forces a major subtraction. You cannot keep your top free-agent priority and add salary without moving Gobert, Randle, or both.

The CBA matching detail that governs trade construction: a team operating below the first apron gets the generous matching band (up to roughly 125% of outgoing salary plus $250K on larger deals). Once a team operates above the first apron, matching tightens to roughly dollar-for-dollar (the 125% expansion is gone), and above the second apron a team cannot aggregate salaries in a trade at all, cannot send cash, and cannot take back more than it sends. Encode the exact brackets from Larry Coon's Salary Cap FAQ; for planning, treat any star acquisition as effectively an apron-bound transaction, because adding a $50M-plus salary while keeping Dosunmu pushes the team up regardless.

### 1.3 The outgoing-salary menu

What the Wolves can send to make money match:

- **Rudy Gobert: about $36.5M** in 2026-27, player option for 2027-28 (three-year, $109.5M extension signed October 2024). He is the most plausible single salary-matching piece for a star. Note the complication for honest analysis: he was the Wolves' best defender against Jokic in the first round, so his on-court value is real even as the front office reportedly questions his long-term fit.
- **Julius Randle: about $33M** in 2026-27 (confirm the exact figure, roughly $33.3M is the number in circulation), player option for 2027-28. Widely reported as the likeliest piece to move after a poor playoff run.
- **Jaden McDaniels and Naz Reid** as larger pieces if a deal demands a young-core sacrifice (the painful path).
- The **three trade exceptions** for smaller absorptions, with the hard-cap tradeoff noted above.

Gobert plus Randle is roughly **$69.5M**, which clears the $58.5M outbound threshold and over-matches almost any single max salary. That combination is the spine of any "go get a star and keep Dosunmu" scenario.

### 1.4 Roster and the fact the brief missed

The brief omitted a roster fact that reshapes the need analysis: **Donte DiVincenzo tore his Achilles and is expected to miss most or all of 2026-27.** He was a starter-level shooter and a connective secondary ball-handler. Treat his absence as a near-certainty baked into the returning-roster baseline (carry the "most or all" uncertainty rather than asserting a lost season). This is a large part of why re-signing Dosunmu is treated internally as non-negotiable rather than optional: Dosunmu is, in part, the DiVincenzo replacement.

Other returning context: Edwards is the fixed point, under contract through 2028-29, and is the one player not realistically in any trade. Connelly's public posture is genuinely mixed and should be represented as such. He used the phrase "sub-26 core" and said the team is "not good enough right now," but he also said he likes that core and is not convinced a major swing is required, pointing to internal development. The specific five-name membership of the "sub-26 core" is media interpretation, not a clean Connelly enumeration, and the lists vary by outlet (one stale version still includes the traded Rob Dillingham). The series should not treat either a fixed five-man core or an unambiguous teardown mandate as established.

### 1.5 Gaps requiring data work

What we can establish now: the cap position, the apron math, the rough pick chest, and the outgoing menu. What needs building before the trade analysis is credible: the full-league salary and contract table, the draft-pick ledger with protections for all 30 teams, and a comparable-trade database to ground value estimates. Section 5 specifies all of it.

---

## 2. The need analysis (method first, then hypotheses)

The brief is explicit: reason from the data, do not assume. So this section specifies **how** to derive the need, then offers directional hypotheses clearly labeled as such.

### 2.1 The exit scenarios, defined

Player value to the Wolves is conditional on who is still on the roster, which depends on who gets traded out. We evaluate every target against a small, explicit set of post-trade rosters:

- **S0, status quo.** No major subtraction. Relevant only for low-cost additions (a minimum or exception-level role player), because the cap math forbids adding real salary without subtracting.
- **S1, Randle out.** Roughly $33M off the books, the power-forward and secondary-scorer slot opened. The most-reported single move.
- **S2, Gobert out.** Roughly $36.5M off, the center slot opened, Beringer minutes unlocked. The canonical salary-match for a star.
- **S3, Randle and Gobert both out.** Roughly $69.5M off, which is what clears the $58.5M outbound requirement while keeping Dosunmu. This is the "acquire a max star" scenario.
- **S4, a young-core piece out** (for example McDaniels). Only invoked when a specific target's market demands it. Flag it as the painful scenario because it cuts into the timeline the front office says it values.

Each scenario produces a different returning roster, and therefore a different need.

### 2.2 Deriving the need vector from the warehouse

Define team need as a vector across dimensions, each quantified from data you already hold (play-by-play, Synergy play types, box, advanced, tracking):

- **Half-court shot creation and rim pressure:** drives, isolation frequency and efficiency, time of possession, rim-attempt rate and finishing, unassisted-shot share.
- **Secondary playmaking:** assist and potential-assist creation, passes that generate advantages, turnover economy at high usage.
- **Off-ball shooting and spacing:** Synergy spot-up volume and efficiency, catch-and-shoot accuracy of returning players, team 3PA rate and location quality.
- **Defensive versatility:** matchup data and switchability, point-of-attack containment, screen-navigation, versatility across positions.
- **Rim protection and rebounding:** opponent rim FG% with the player on, block and contest rates, rebounding rates.
- **Transition and pace fit.**

For each exit scenario, recompute the **returning-roster profile** across these dimensions (subtract the departing players, add Dosunmu re-signed and any pieces that return in a setup trade). The **need vector** is the gap between a contender-level benchmark profile and the returning-roster profile. Because DiVincenzo's absence is baked into the baseline, the shooting and secondary-creation gaps will be wider than the surface roster suggests, in every scenario.

Critically, weight the benchmark toward **playoff** conditions, not regular season. The Wolves' actual failure mode this spring was a half-court problem against set, switching defenses: they were outscored by roughly 97 points across six games by San Antonio and, in Finch's words, ran out of bullets. A need vector calibrated to regular-season offense would understate the problem. Build the benchmark from how the league's best half-court playoff offenses are constructed, and from how switch-heavy defenses (the Spurs, the Thunder) actually attacked Minnesota.

### 2.3 Directional hypotheses (to confirm, not to assume)

Stated as hypotheses the data work should test and is free to overturn:

- **H1:** The largest gap is **secondary half-court creation next to Edwards**, a player who can generate a good shot when Edwards is loaded up or off the floor. Randle's iso-heavy version of this cratered under playoff pressure, which is part of why his fit is in question.
- **H2:** **Shot quality and shooting** are a secondary but real gap, widened by the DiVincenzo injury, especially movement and off-ball shooting that survives playoff close-outs.
- **H3:** A target who provides creation **and** holds up defensively against switching is worth a premium, because the Wolves' losses came on both ends in the same stretches.
- **H4:** Fit with the younger core's timeline (age, contract length, complementary rather than redundant skills with Edwards, McDaniels, Reid, Beringer) is itself a need dimension, not a tiebreaker.

If the data contradicts any of these, the articles follow the data.

---

## 3. The acquisition metric (the centerpiece)

### 3.1 Design philosophy

A single opaque score would be worse than useless here, because it would blur the one distinction that matters most: a player you cannot acquire should never outrank a player you can, no matter how well he fits. So the metric is a **structured profile that gates before it scores.** Feasibility is a gate, not a smooth dimension. Among the targets that clear the gate, the profile shows salary fit, contract health, need fit, and impact separately, then rolls up into a tiered verdict whose logic is written out rather than hidden in weights.

The output for any target is a one-page profile plus a conditional verdict matrix. Four modules feed it.

### 3.2 Module 1: Acquisition feasibility (the gate)

Returns a category, not a number: **Feasible**, **Stretch (direct)**, **Stretch (via setup trade)**, or **Infeasible.** Two sub-gates.

**1a. Salary-matching feasibility (CBA legality).**
Inputs: the target's incoming salary; the Wolves' outgoing menu (Gobert $36.5M, Randle $33M, McDaniels, Reid, smaller pieces, the three exceptions); the apron thresholds; the team's roughly $14M of room under the first apron; the $58.5M outbound requirement to keep Dosunmu under the second-apron hard cap.
Logic: find the minimum legal outgoing set for the incoming salary under the applicable matching band, identify which apron line the resulting team salary lands under, and flag any hard cap triggered. Treat star acquisitions as apron-bound (roughly dollar-for-dollar matching) unless the math demonstrably keeps the team under the first apron. Output the minimum viable package(s) and the apron landing.

**1b. Asset feasibility (does the chest cover the market price).**
Inputs: the Wolves' tradable assets (pick 28, the 2033 first, the 2028 swap, young players such as Shannon and Beringer, plus anything that returns in a setup trade); the target's likely market price benchmarked against the comparable-trade database.
Logic: compare the likely price to what the Wolves can assemble. Output one of:
- **Feasible:** market price is clearly within the chest.
- **Stretch (direct):** requires most of the chest and a favorable market, but no setup trade.
- **Stretch (via setup trade):** infeasible directly, but reachable through a documented two-stage path.
- **Infeasible:** market price exceeds what the Wolves can assemble even after a setup trade. This is the category the brief specifically wanted, distinct from "feasible but expensive."

**The two-step chain.** Per the decision to model it: feasibility is a chain, not a snapshot. Stage 0 is the current chest. Stage 1 is the chest after a plausible Gobert or Randle move that itself **returns** picks or young players (a value trade, not just a salary dump). Stage 2 repackages the combined chest for the target. A target can be "infeasible directly, Stretch via a two-stage path," which is an honest and distinct verdict. The setup trade's plausible returns come from the comp database, expressed as ranges, never point prices.

### 3.3 Module 2: Contract and timeline fit

Legality is not the same as a good contract. A deal can match and still be cap-toxic. Inputs: the target's salary across the full contract, length, player and team options, trade kicker (which inflates the matching math), no-trade clause (which gives the player veto power and feeds back into feasibility), and age relative to the contract's end versus the sub-26 timeline. Output: a contract-health read (good fit, tolerable, toxic) with the specific reasons, including whether the deal worsens the apron problem in out-years.

### 3.4 Module 3: Need fit (conditional on the post-trade roster)

This is the subtle centerpiece. Two steps.

First, take the need vector for the relevant exit scenario from Section 2. Second, project the target's contribution across the same dimensions from his own tracking, Synergy, and box profile, applying **role and translation adjustments**: a high-usage iso scorer is discounted when the need is off-ball spacing; a low-usage 3-and-D wing is discounted when the need is on-ball creation. The need-fit score is the weighted dot product of the target's dimensional profile and the need vector. A great player who does not fill the actual hole scores lower than a good player who fills it precisely. That is the entire point.

Run each target only against the scenarios in which he is plausibly acquirable. You do not evaluate a $58M star against S0.

### 3.5 Module 4: Player impact and playoff translation

The cross-team valuation spine should be a **multi-year regularized adjusted plus-minus (RAPM) model built from your own play-by-play.** Building it in-house makes it reproducible and defensible, which is the standard the brief sets. Triangulate against public all-in-one metrics (EPM, LEBRON, DARKO) as sanity checks rather than sources of truth, because methodologies differ and you want to own the number you publish.

Add a **playoff-translation read**, because the Wolves' problem is specifically a playoff problem. Regular-season RAPM can flatter players who feast on weak half-court defenses. For each target, assess how the game holds up against switching and physicality (Synergy half-court splits, iso and pick-and-roll efficiency versus set defenses, playoff splits where the sample allows, with heavy sample-size caveats stated every time).

Output an impact estimate **with an explicit uncertainty band.** RAPM standard errors are large; carry them. Do not publish a point estimate that implies precision the model does not have.

### 3.6 The roll-up: profile, matrix, tiers

For each target, produce:

1. **Feasibility verdict** (the gate), with minimum viable package(s) and apron landing.
2. **Contract health** with reasons.
3. **Need fit**, which specific needs filled, under which scenario, with the per-scenario score.
4. **Impact**, the value estimate with its band, plus the playoff-translation note.
5. **The conditional verdict matrix:** target by exit scenario, each cell holding {feasible?, need-fit, net roster value}. This three-to-four-row matrix is the heart of the output, because it shows how the answer changes by scenario rather than collapsing to one number.
6. **An overall tier**, explicitly derived: Priority Target, Worth Pursuing, Situational, Pass, or Infeasible. The logic is a written rule, not a hidden scalar. A target must clear the feasibility gate to rank above Infeasible. Among feasible targets, ranking is driven by need-fit times impact, with contract health and timeline as modifiers. Show the rule so a reader can disagree with the weights and recompute.

### 3.7 Uncertainty handling (no false precision)

- **Feasibility:** discrete categories with the binding constraint named, never a probability to two decimals.
- **Trade cost:** a range grounded in named comps ("comparable deals for this archetype have cost a future first plus a young rotation player plus salary filler"), never a point price. This mirrors the hard constraint exactly.
- **Impact:** carry RAPM standard errors, show a band, flag small playoff samples.
- **Need fit:** publish the weights, then run a sensitivity check. If a reasonable reweighting flips the verdict, say so.
- Every profile closes with **"what would change this verdict,"** naming the key assumptions and how fragile they are.

### 3.8 Reproducibility and defensibility

Every input traces to a source (a warehouse table or a public source plus a date). Weights are explicit and version-controlled. The comp set anchoring each trade-cost range is listed by name. The roll-up logic is written as rules. No black-box scalar. A front-office reader should be able to rebuild the verdict from the inputs.

---

## 4. Worked example (a design demonstration)

This runs the framework end to end on one target to pressure-test the design before the build. **The CBA and salary math below are real** (figures from Spotrac, June 2026). **The impact and need-fit values are illustrative placeholders**, marked as such, because the warehouse models are not built yet. The point is to show the shape of the output and prove the modules cohere, not to publish a verdict.

### 4.1 Primary case: Kawhi Leonard

**Feasibility, 1a (salary).** Kawhi's 2026-27 cap figure is **$50.3M** (three-year, $149.5M extension with the Clippers). As an apron-bound transaction, the Wolves must send roughly $50.3M-plus. Gobert ($36.5M) plus Randle ($33M) over-matches at $69.5M and also clears the $58.5M Dosunmu threshold, so it works on both counts and actually sheds salary. A leaner alternative, Gobert plus a roughly $14M piece, also matches and keeps more young talent. Aggregation is permitted as long as the team is not above the second apron at the time, which the move itself helps satisfy. **Salary verdict: Feasible (multiple legal paths).**

**Feasibility, 1b (assets).** This is where Kawhi separates from Giannis. The Clippers appear headed for a reset, and Kawhi's age and injury history depress his trade value relative to a healthy prime star. If the comp database supports a market price in the range of one future first plus a young player plus filler, the Wolves' chest (pick 28 or the 2033 first, plus Shannon, plus Gobert-or-Randle salary) plausibly clears it without a setup trade. **Asset verdict: Feasible or mild Stretch (direct), pending the comp database.**

**Contract and timeline.** Real reasons to hedge: Kawhi is on the wrong side of the sub-26 timeline, his availability is the central question of his career, and the contract runs through 2026-27 with the structure to confirm in Pass 1. A win-now move that does not extend the window as far as a younger star would. **Contract verdict: tolerable, with durability as the swing factor.**

**Need fit (illustrative).** Against S2 (Gobert out) or S3 (both out), Kawhi addresses H1 and H3 directly: half-court shot creation next to Edwards and a switchable two-way wing. He is a strong fit for the actual hole, not just a strong player. *Per-dimension scores: to be computed from the warehouse. Expected shape: high on secondary creation and defensive versatility, moderate on spacing, low marginal value on rim protection (which a Gobert subtraction worsens, a real tension to surface).*

**Impact (illustrative).** *RAPM estimate with band: to be computed. Playoff-translation note: historically elite, but recent availability caps the minutes you can bank on, so the impact band should be wide and the durability risk stated in plain language.*

**Conditional verdict matrix (illustrative shape):**

| Scenario | Feasible? | Need fit | Net roster value |
|---|---|---|---|
| S1 (Randle out) | Salary tight, likely needs Gobert too | high creation, but rim protection intact | [to compute] |
| S2 (Gobert out) | Feasible | high, but rim protection now a hole | [to compute] |
| S3 (both out) | Feasible | high creation and versatility, two holes opened (rim, depth) | [to compute] |

**Overall (illustrative):** likely Worth Pursuing rather than Priority Target, with the verdict gated on durability and on whether the comp database confirms an affordable price. The framework's value here is that it refuses to call this either a slam-dunk or a non-starter; it isolates exactly which uncertain inputs decide it.

### 4.2 Contrast case: Giannis Antetokounmpo (why the gate matters)

**Feasibility, 1a (salary).** Giannis's 2026-27 cap figure is **$58.46M**. Gobert plus Randle ($69.5M) matches and clears the Dosunmu threshold. **Salary verdict: Feasible.**

**Feasibility, 1b (assets).** Milwaukee would command a haul of unprotected firsts and young star-level talent. The Wolves hold one near pick (28, draft-night only), one distant first (2033), one swap (2028), and a modest young core. That does not approach a market price for a top-five player, even after a Gobert setup trade that returns picks. **Asset verdict: Infeasible directly; Stretch (via setup trade) at the most optimistic, and even then the total chest likely falls short.**

The lesson for the design: Giannis is **salary-matchable but asset-infeasible.** A single blended score would muddle that. The gate keeps it clear. Giannis lands at Infeasible-to-Stretch on assets despite passing the salary test, while Kawhi clears both. That distinction is the entire reason the metric gates before it scores, and it is exactly the distinction the brief asked for.

---

## 5. Data infrastructure plan

For each requirement: source, realistic method, and whether it gates the analysis.

### 5.1 Player performance (on-court). Status: in hand.
You hold play-by-play, Synergy play types, box, and advanced from the stats.nba.com API, with pipelines to add endpoints. Add, if not already present, **player-tracking and defensive-matchup endpoints** (for spacing, switchability, and rim-protection dimensions). **Not a blocker.** One build item: the in-house **multi-year RAPM** model from play-by-play is the valuation spine and needs to be stood up. Treat that as the main on-court engineering task.

### 5.2 Salary and contract data (financial). Status: must acquire. Soft gate.
No clean free API; stats.nba.com carries none of this. Options, in order of preference:
- **Spotrac developer API** (paid, RESTful JSON, NBA contracts, salaries, cap, filterable). Cleanest single source for a periodic bulk pull. Rate-limited on lower tiers (roughly weekly), which is fine for an offseason cadence.
- **Sportradar NBA API** carries base salary only (no options, kickers, NTCs, out-years), also paid. Insufficient alone.
- **Scrape** Spotrac pages, HoopsHype salaries, or Capology. Basketball Reference has a contracts page but Sports Reference prohibits scraping and rate-limits hard, so use it for occasional manual lookups, not bulk.
- A small indie aggregator (The Linda Report API) combines Spotrac and RealGM; treat as a convenience, not a source of truth.

**Recommended given the ASAP timeline and the "let the analysis decide" mandate** (which requires broad coverage so the metric can rank the whole acquirable pool): a **two-pass** approach.
- **Pass 1, breadth, fast:** the full-league salary table for every player (base salary, contract years, option type, basic flags) in one Spotrac pull or scrape. This is what lets the metric rank everyone.
- **Pass 2, depth, targeted:** the granular mechanics (trade kickers, no-trade clauses, partial guarantees, cap holds, exact option amounts) only for the roughly 30 to 50 players and 8 to 12 teams that actually surface as relevant. Depth where it matters, not everywhere.

Why a soft gate, not hard: the named-target (Track A) feasibility can lean on already-reported figures (the star salaries above are confirmed), but the Track B "let the metric surface targets" work cannot run without the breadth pass.

### 5.3 Draft-pick ledger with protections (assets). Status: must acquire. Hard gate for trade construction.
No API anywhere. Compile from **RealGM's detailed future-pick database** and **Spotrac's future-picks page**, encode protections and swap conditions as structured data, cross-check the "maximum tradable future firsts" interpretation (which already bakes in the Stepien and seven-year rules) against **ESPN's leaguewide asset rankings**, and use **Tankathon** for the locked current-year order. Validate every constructed package in a free trade machine (**Fanspo**) to confirm it is CBA-legal and respects pick obligations. A few hours of work, and it is the thing that gates credible trade construction. **Hard blocker for Track B packages.**

### 5.4 Comparable-trade database (grounding). Status: must build. Gates honest cost ranges.
Compile recent veteran-and-star trades (last three to four seasons) with the assets exchanged, salary moved, and context. This is what turns "would likely cost a first and a young player" from a guess into a comp-anchored range. Sources: trade trackers (ESPN, RealGM transactions, Spotrac transactions) plus contemporaneous reporting. **Gates the no-false-precision requirement;** without it, every cost estimate is a hot take.

### 5.5 CBA mechanics (rules). Status: reference, encode once.
Larry Coon's Salary Cap FAQ for the matching brackets, hard-cap triggers, aggregation rules, and apron restrictions; The Third Apron (Yossi Gozlan) and Bobby Marks explainers for the apron-specific edges. Encode the relevant rules into the feasibility module. Not data, but the logic the module runs on.

---

## 6. Article structure (recommended, flexible count)

Sequenced to the offseason calendar, because the brief wants this fast and the calendar is binding: draft June 23 to 24, free-agent negotiations open June 30, signings official July 6, Dosunmu's extension window closes June 30.

1. **The Asset Reality.** The picks (28 draft-night-only, 2033, the 2028 swap, depleted seconds), the cap and apron position, the $58.5M-to-keep-Dosunmu math, the outgoing menu, and a clear statement of what the Wolves can and cannot do mechanically. **Publish pre-draft.** This is the foundation everything else stands on.
2. **The Need.** The exit scenarios, DiVincenzo's absence, the returning-roster profile, the need vector derived from the warehouse and calibrated to playoff conditions. Reason from data; present H1 through H4 as tested, confirmed, or overturned. **Publish before free agency opens.**
3. **The Metric.** The scorecard, the conditional matrix, how feasibility gates, how uncertainty is handled and why. The methods piece, written so a skeptical reader trusts the machinery. **Publish alongside or just before the first application.**
4. **Applications, Track A (the reported targets).** Giannis, Kyrie, Ja Morant, and Kawhi run through the metric with honest verdicts. The public names also floated include Kawhi via the Clippers' apparent reset, so the target universe is wider than Giannis and Kyrie. This may be one piece or split in two depending on how many clear the gate.
5. **Applications, Track B (what the analysis surfaces).** Let the metric rank the acquirable pool and surface the best-fit targets the model likes, including non-obvious names the media is not discussing, then compare to the Track A list. This is where the framework earns its keep.
6. **The Decision.** Synthesis: given feasibility, need, and cost, what the decision space actually looks like and what the model would do, uncertainty preserved. Could fold into the end of Track B if it runs short.

Plan on roughly six pieces, with 4 and 5 each expandable if many targets clear the gate. Do not lock the count until the metric has run, because the number of feasible targets determines how many application pieces are warranted.

---

## 7. Open questions and decisions for the author

Resolved from your last round: analysis decides the targets (Track A plus Track B), worked example included (Kawhi primary, Giannis contrast), two-step chain modeled, timeline is ASAP. The following still need your call.

1. **Setup-trade depth.** The two-step chain can model Stage 1 returns at two levels: a light version that only asks "could a Gobert or Randle move plausibly return assets X," or a heavier version that constructs named Stage 1 deals with specific third teams. The heavier version is more concrete but more speculative. Which do you want, given the no-false-precision rule?

2. **How far to go on cost ranges.** Section 3.7 commits to comp-anchored ranges, never point prices. Within that, are you comfortable attaching ranges to named targets ("a Kawhi deal in the range of one first plus a young player plus filler"), or do you want to stop at "the decision space and feasibility" without putting a number on any specific player? Both respect the constraint; they are different products.

3. **Player-availability assumptions.** Some Track A targets may not actually be available (the Clippers have shown no official sign Kawhi is on the market; Giannis is reported but unconfirmed). Do we evaluate them anyway with availability flagged as an assumption, or gate the analysis on reported availability? My lean is to evaluate with the assumption stated, since the decision space is the point, but it is your brand voice on the line.

4. **Cadence versus dominoes.** ASAP means the foundational and need pieces go out pre-draft, before any move happens, so the applications will be partly speculative by necessity. Are you comfortable publishing applied verdicts on trades that have not occurred (clearly framed as decision-space analysis), or do you want the applied pieces to wait for real dominoes (a Gobert or Randle move, the Giannis resolution) at the cost of speed? You cannot fully have both.

5. **Edges on the young core.** If the metric surfaces a target whose market realistically requires McDaniels (S4), do you want that modeled and published, given Connelly named him part of the core? It is the most uncomfortable scenario and the one most likely to draw reader heat.

6. **Verification depth on figures.** I have confirmed the load-bearing numbers (cap position, the $58.5M threshold, the star salaries, Gobert and Randle). Before publishing the asset piece, do you want me to lock the exact 2026 pick slot and the precise Randle figure, or is the current confidence level (28, roughly $33M) good enough for a pre-draft piece with a confirm-on-publish note?

Answer these and the data engineering and the writing can both start from the same page.
