# Q8: Player-Specific Roster Decisions (Gobert, Randle, and DiVincenzo)

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q8
**Status:** Specification, reviewed for replan consistency 2026-05-17.
**Position in stack:** Decision-prescriptive analysis, bridges Q2/Q6 to Q5. Sits at position 5 in master plan v3 Phase 3 build sequence (between Q6 and Q7).

**Revision note:** This spec was drafted independently of the post-LAFI replan and was reviewed for consistency. The spec's references to LAFI components (C2, C3, C5) and the three paths (Edwards development, Category B catch-and-shoot, system change) are aligned with the revised Q5. Section 13 below explicitly addresses how Q8's findings integrate into Q5's three-paths framework: Q8 informs which path or paths the prescription should weight more heavily, and may add a fourth path (frontcourt restructuring) if its findings warrant.

**Second revision (2026-05-17):** DiVincenzo added as a third player. The original Q8 scope was Gobert and Randle. DiVincenzo's torn Achilles in round 1 makes him a Category B personnel gap that the prescription must engage with explicitly, even though his case is "non-decision" (the choice is taken out of the team's hands by the injury). The DiVincenzo treatment is shorter than the Gobert and Randle deep dives: recovery projection, Category B gap analysis, and Q5 cap-implication framing. Spec renumbering: a new Section 5 covers DiVincenzo. The combined-question section moves to Section 6. Subsequent sections shift accordingly.

---

## 1. The thesis

### 1.1 The question

Given everything the project has surfaced about the Wolves' Q4 offensive pathology, what is the data-supported case for and against keeping Rudy Gobert, and the same for Julius Randle? What specific roster moves involving these two players, if any, would most plausibly improve the team's championship odds?

This is the most decision-prescriptive analysis in the project. Every other spec is diagnostic ("what is true about this team"). Q8 is prescriptive at the individual player level for the two specific contracts that constitute the biggest roster levers available to the front office this offseason.

### 1.2 Why this matters

Three reasons.

**First.** The Gobert and Randle contracts are the dominant items on the Wolves' cap sheet outside Edwards. Gobert is on a max-tier deal. Randle has a 2026-27 player option that he can exercise or decline. These two decisions will shape the team's cap flexibility and roster composition for the next two to four years. A diagnostic memo that doesn't engage with them is a memo that doesn't address the actual decisions the front office faces.

**Second.** Public discourse this summer will center on these two players. Every Wolves podcast, every Twin Cities columnist, every fan will be debating "keep or trade" for both. An analytical project that engages seriously with the team's struggles needs to engage with these specific players or risk being seen as theoretical. A front office reader will flip through and ask "okay but what about Gobert?" The analysis needs an answer.

**Third.** The Q4 pathology diagnosis from LAFI v1 has direct implications for both players that no public analysis is currently making. Gobert's positional role and Randle's possession allocation both potentially contribute to the LAFI architecture problems. The project has the analytical infrastructure to test these specific hypotheses with player-level evidence; very little public work does.

### 1.3 The principle

Q8 follows the project's "let the data lead" principle with extra rigor because both player questions are emotionally charged for Wolves fans. The analyst going into this spec is sympathetic to the "Gobert is part of the problem" framing. The user has stated theories about both players. Pre-validating either set of priors would compromise the work.

Q8's standard: every claim about either player must hold up to the inverse claim being presented with the same evidence weight. If the analysis says "Gobert is the problem because X, Y, Z," it must also present "Gobert is not the problem because A, B, C" and show why X-Y-Z outweighs A-B-C. Same for Randle. Same in both directions.

The output is not "trade Gobert" or "keep Gobert." The output is a probabilistic case for each direction with the underlying evidence visible to a reader who may want to draw their own conclusion.

### 1.4 The hypotheses to test

Pre-committed before any data is pulled.

**Gobert hypotheses:**

- H1a: Gobert's positional constraints (must stay near the rim, cannot shoot) suppress off-ball motion when he is on the floor.
- H1b: Gobert remains a top-tier defensive impact player despite his age (33 entering 2026-27).
- H1c: Gobert's fit with the current personnel is structurally worse than his fit with the 2023-24 KAT-anchored personnel was.
- H1d: The Wolves' offense improves measurably when Gobert sits and Naz Reid plays the 5.
- H1e: Gobert's offensive limitations specifically cause the Wolves' Q4 motion-death pathology.

**Randle hypotheses:**

- H2a: Randle's possession usage exceeds his marginal value at the team level (i.e., his iso possessions are negative-EV).
- H2b: Randle's regular season production has declined meaningfully from 2024-25 to 2025-26.
- H2c: Randle's playoff production is systematically below his regular season production.
- H2d: Randle's fit with Edwards is worse than alternative power forwards the Wolves could plausibly acquire would be.
- H2e: Randle's value is concentrated in a specific subset of game contexts (Edwards out, certain matchups, etc.).

**DiVincenzo hypotheses (added 2026-05-17):**

- H3a: DiVincenzo's 2024-25 contribution was a meaningful Category B asset in LAFI terms, and his absence is a primary driver of the 2025-26 Category B gap.
- H3b: Realistic Achilles recovery profiles for guards in their late 20s suggest DiVincenzo is unlikely to return to his 2024-25 form, and likely to miss most of 2026-27.
- H3c: The Category B gap his absence creates is not closeable by internal options (Naz, Conley, McDaniels at current volume) and requires external acquisition or significant role expansion.

Each hypothesis will be evaluated with explicit evidence. None of them is pre-validated.

---

## 2. The data structure

### 2.1 Individual production analysis

For each player, pull:

**Career trajectory:**
- Box score per 36, season by season (last 5 seasons minimum)
- TS%, eFG%, FT rate, three-point rate
- Usage rate by season
- Assist rate, turnover rate
- BPM, EPM, RAPM (multi-year pooled), LEBRON

**Current season detail:**
- Game-by-game splits
- Home vs away
- Vs strong defense vs weak defense
- Clutch performance (last 5 minutes within 5)
- Performance with vs without Edwards on the floor

**Playoff trajectory:**
- Playoff production vs regular season production (last 5 years)
- Series-by-series performance
- Performance vs different defensive archetypes (rim-protection vs switchable wings)

### 2.2 Lineup-level impact

For each player, compute:

**On/off splits:**
- Team net rating with player on vs off (regular season and playoffs)
- Team offensive rating splits
- Team defensive rating splits
- Halfcourt-only versions of all of the above

**Most-used lineups:**
- Top 10 lineups containing each player by minutes
- Each lineup's net rating with bootstrap CIs
- Comparison to lineups without each player

**Two-man combinations:**
- Gobert + each rotation player
- Randle + each rotation player
- Specifically: Gobert + Edwards, Gobert + Randle, Randle + Edwards, Gobert + Naz, Randle + Naz

**RAPM-style adjusted impact:**
- Multi-year pooled RAPM estimate for each player
- Adjusted impact controlling for teammate and opponent strength

### 2.3 The Q4 fit analysis

This is the LAFI-specific work. For each player, compute:

**Gobert-specific:**
- Wolves' Movement Death (C2) component value when Gobert is on the floor vs off
- Specifically: average off-ball distance traveled per offensive possession with Gobert on vs off
- Off-ball screen frequency with Gobert on vs off
- Cut frequency with Gobert on vs off
- Spacing measurement (average inter-player distance) with Gobert on vs off

This tests Hypothesis H1a directly. If motion measurably improves when Gobert sits, the positional-gravity theory has support.

**Randle-specific:**
- Wolves' Isolation Reliance (C3) component when Randle is on vs off
- Specifically: iso possession frequency with Randle on vs off
- Iso PPP for Randle compared to team iso PPP for other players
- Possession outcomes when Randle has the ball for 4+ seconds vs 2-4 seconds
- Shot quality (LAFI C5) of possessions Randle uses vs possessions Edwards uses vs possessions everyone else uses

This tests Hypotheses H2a and H2e directly.

### 2.4 Contract and trade market reality

**Contract details:**
- Each player's contract terms (years remaining, total dollars, guarantees, options)
- Trade restrictions if any
- Luxury tax and apron implications

**Realistic trade market:**
- For Gobert: what is the realistic return given age, contract size, and league-wide center demand
- For Randle: depends on whether he opts in; if he opts out, free agent market; if he opts in, trade market

This section is shorter and more pragmatic than the analytical sections. The goal is grounding the recommendations in what is actually achievable.

---

## 3. The Gobert deep dive

### 3.1 The case against Gobert (testing user's theory)

The analytical question: does Gobert's presence specifically cause or worsen the Wolves' Q4 pathology?

**Test 1: Off-ball motion with Gobert on vs off.** The cleanest test. Compute distance traveled by the four non-handlers in the offense, per possession, with Gobert on the floor vs off. If motion is measurably higher when he sits (controlling for which other players are on the floor), the positional-gravity hypothesis has support.

Caveats: lineup composition is confounded with Gobert's status. Need to control for who replaces him (typically Naz, sometimes Beringer). The control should compare Gobert lineups to Naz lineups, not Gobert lineups to all non-Gobert lineups.

**Test 2: Offensive rating with Gobert on vs off, in non-garbage time.** Standard on/off but filtered to competitive minutes. The hypothesis: Gobert's offensive cost in halfcourt is meaningfully larger than his defensive value.

Caveat: defensive value doesn't always show up in real-time team defensive rating. Gobert's rim protection forces opponents into worse shots, which is a downstream effect that may not capture in a single game.

**Test 3: Spacing measurement.** Compute average distance from teammates for each non-Gobert player when Gobert is on the floor vs off. The hypothesis: players cluster more when Gobert is on the floor because he occupies the paint, which forces other players to space outside.

Caveat: tracking data may have noise here. Validate the measurement on lineups where the hypothesis should clearly hold (any team with a non-shooting center) before applying.

**Test 4: Opponent defensive scheme response.** When the Wolves are on offense with Gobert on the floor, how do opposing defenses cover him? Specifically: how often do opposing centers leave him to help on the perimeter? If opposing defenses systematically ignore Gobert as a roll man or stationary big, that's structural evidence the Wolves are playing 4-on-5 on offense when he's in.

This is harder to measure but the agent should attempt it via PBP and tracking. If opposing centers' average distance from Gobert is consistently large, the help-load on Gobert is light, which means he's not bending the defense.

### 3.2 The case for Gobert (testing the counter)

The case for Gobert has to be presented with the same rigor.

**Defensive impact:** Despite his age, Gobert remains an elite rim protector. The data:
- Opponent FG% at the rim with Gobert as nearest defender
- Team defensive rating with Gobert on vs off
- Specifically: opponent rim FG% comparison Gobert on vs off

If Gobert's rim protection numbers remain top-5 in the league, the defensive case is real regardless of offensive concerns.

**Rebound and possession protection:** Gobert's defensive rebounding rate. Possessions he ends (rebounds + blocks) vs possessions he extends (offensive rebounds, fouls drawn).

**The 2023-24 context:** The Wolves reached the WCF with Gobert as the starting 5 and a top-3 defensive rating. If the data shows the offense had a workable shape with Gobert plus KAT, the question becomes whether Gobert is the problem or whether the loss of KAT is the problem.

**Replacement reality:** What does the Wolves' rim protection look like with Naz at the 5 full-time? Naz is a competent but not elite rim protector. If the team's defensive rating craters when Gobert sits (controlling for who else is on the floor), the defensive cost of moving him is severe.

**Counterfactual question:** Could the Wolves replace Gobert's defensive value through perimeter defense plus a different center? Plausibly yes for some replacement centers (Mobley-tier, hypothetically) but the realistic replacements available to the Wolves in trade are not Gobert-tier defensively. The trade math may not produce a defensive upgrade.

### 3.3 The honest synthesis

After all four tests in 3.1 and the case in 3.2 are run, the analysis should produce a probabilistic verdict:

- Probability Gobert is a net negative on this current roster (with current personnel around him)
- Probability Gobert would be a net positive on this current roster with different complementary personnel (a stretch four, a different perimeter rotation)
- Probability the realistic trade return for Gobert improves the team's championship odds

These three probabilities can disagree. It's possible for Gobert to be a net negative on the current roster, a net positive with the right complement, AND the realistic trade return to still not improve championship odds because the trade market for declining $40M+ centers is bad.

The honest landing is whichever of the three considerations dominates given the evidence. Pre-committed positions before running the data: I (the analytical advisor) am moderately sympathetic to the "Gobert is part of the problem" framing. The user is more sympathetic. Both biases need to be disclosed and disciplined in the writeup.

### 3.4 The Gobert age curve check

Defensive-anchor centers have known age curves. Mutombo, Camby, Ben Wallace, prime Dwight, Tyson Chandler. Pull the age curve for this archetype.

Where is Gobert at 33 on the comparable curve? If he's tracking ahead of the curve (declining more slowly than typical), the contention case is stronger. If he's behind the curve (declining faster), the trade case is stronger.

This is also the section where the year-over-year question gets answered: has Gobert specifically declined from 2023-24 to 2025-26 in measurable ways? Rim protection, defensive rebounding, foul rate, mobility indicators.

---

## 4. The Randle deep dive

### 4.1 The case against Randle (testing user's theory)

The analytical question: does Randle's possession usage produce negative team value?

**Test 1: Usage vs efficiency.** Standard analytical question. What is Randle's TS% at his usage rate? Compare to historical and contemporary high-usage power forwards. If his TS% is below 55% at usage above 24%, that's a structurally inefficient possession allocation.

Specifically for 2025-26 vs 2024-25: has his efficiency dropped while his usage held? If yes, Hypothesis H2b has support.

**Test 2: On/off in playoffs vs regular season.** Randle's career playoff trend has been negative. His 2024-25 playoff run was a positive outlier. Has his 2025-26 playoff performance reverted? Track game-by-game.

**Test 3: Possession value at the margin.** When Randle uses a possession (iso, post-up, drive), what is the expected value of that possession vs the alternative (Edwards iso, Edwards PnR, McDaniels off the catch)? This requires a possession-level value model but the agent can build a simplified version from Synergy PPP by play type and player.

If Randle's marginal possessions are worth meaningfully less than the alternative options, his usage is mis-allocated.

**Test 4: Lineup-level impact when Randle is on vs off, controlling for Edwards.** The cleanest test. Specifically:
- Edwards on, Randle on (the default)
- Edwards on, Randle off
- Edwards off, Randle on
- Edwards off, Randle off

The hypothesis: the team's net rating is highest in "Edwards on, Randle off" and lowest in "Edwards off, Randle on." If true, Randle's value to the team is conditional on Edwards being absent, which is a costly luxury role for his contract slot.

### 4.2 The case for Randle (testing the counter)

**The 2024-25 evidence:** Randle was a positive contributor to a conference finals run. His individual numbers were good. The team's offense functioned with him in it. Whatever has changed in 2025-26, it's worth understanding what specifically deteriorated.

**Possible explanations for a 24-25 to 25-26 decline if one exists:**
- Personal regression (age, injury, role)
- System fit deterioration (something the team did differently around him)
- Opponent adjustment (defenses learned how to guard him over a full season of film)
- Edwards' development reducing Randle's necessary role
- Randomness (one season's variance)

If the 2024-25 version of Randle is reachable again with different system or personnel choices, the trade case weakens. If the decline is structural and unreversable, the trade case strengthens.

**The player option implications:** Randle has a 2026-27 player option. If he opts in, the team controls his contract. If he opts out, he's a free agent. The decision space depends on which path he takes. If he opts in to a salary the market wouldn't pay, the team has a salary problem. If he opts out and the market pays him, the team can replace his cap slot. The analysis needs to engage with both scenarios.

**The replacement reality:** Power forwards at Randle's production level on tradeable contracts are not easy to find. The realistic alternative if he leaves: a less talented but cheaper free agent, plus a draft pick or two used to acquire a complementary piece. The math may not improve the team.

### 4.3 The 2024-25 vs 2025-26 reconciliation

This is the Randle-specific subsection that the broader case needs.

Pull Randle's 2024-25 and 2025-26 in detail. What changed? Specifically:

- Box score per 36 across both seasons
- TS% and shooting splits
- Usage rate
- Assist rate
- Turnover rate
- Defensive metrics
- Lineup-level impact

If 2025-26 is meaningfully worse, identify what specifically. If it's similar, the discourse about Randle's decline may be eye-test driven rather than data-supported. Either is a finding.

### 4.4 The honest synthesis

Same structure as Gobert. Probabilistic verdict:

- Probability Randle is a net negative on the current roster
- Probability Randle is recoverable to 2024-25 form with system or personnel changes
- Probability the realistic alternative (opt-out scenario or trade return) improves the team

---

## 5. The DiVincenzo treatment (added 2026-05-17)

DiVincenzo is a different kind of case than Gobert and Randle. There is no active "keep or trade" decision because his Achilles tear has effectively taken the choice out of the team's hands. The Q8 work on him is non-decision analysis: what was he, what is his realistic recovery profile, and what does his absence force on the Wolves in 2026-27 and beyond.

### 5.1 The 2024-25 contribution quantification

This is the retrospective. Before the injury, DiVincenzo was the Wolves' primary catch-and-shoot specialist. Pull:

- 2024-25 catch-and-shoot 3PA and 3P% (career-high volume at 38.3% on 496 attempts pre-injury equivalent)
- 2024-25 lineup-level impact: net rating, ORtg, DRtg with DiVincenzo on vs off
- 2024-25 LAFI sub-metric impact: how did the Wolves' C5 (shot quality decay) change when DiVincenzo was on the floor vs off? Specifically: did his catch-and-shoot share rise team-wide when he played?
- 2024-25 playoff contribution: per-game splits, lineup contributions in the playoff run
- Defensive value: where ranked among Wolves wing defenders, switchability indicators

The output is a clear picture of what specifically the team lost when he went down. This is the H3a test.

### 5.2 The recovery projection

Achilles recovery for guards in their late 20s. Build a comp set of historical Achilles tears for guards aged 25-30 and document the recovery profiles:

- How many returned within 12 months vs 18+ months?
- How many returned to their pre-injury production tier? What fraction at full athleticism?
- For those who returned at diminished athleticism, what specific drop-off (lift, lateral quickness, durability for back-to-back games)?
- Career trajectory post-injury (how long did the diminished version last, did athleticism recover further over time)?

Express the 2026-27 projection as bands rather than a point estimate:

- Best case (top quartile of comps): partial 2026-27 contribution at reduced athleticism, full return in 2027-28
- Median case: minimal 2026-27 contribution (35-50 games at reduced effectiveness), partial 2027-28
- Worst case (bottom quartile): no meaningful 2026-27 contribution, partial 2027-28 at substantially diminished form

This is the H3b test. Honest framing: Achilles tears are well-documented in the basketball literature and the comp set is large enough for defensible bands.

### 5.3 The Category B gap analysis

This is where the DiVincenzo work most directly feeds Q5.

With DiVincenzo out, the Wolves' Category B personnel for 2026-27 is:

- Naz Reid (38.1% on 344 catch-and-shoot 3PA in 2025-26, but plays the 5 not the wing)
- Conley (38.9% on 108 catch-and-shoot 3PA, lower volume and aging)
- McDaniels (45.1% on 162 attempts at high efficiency but low volume; could expand role)
- Edwards (49.6% on 139 attempts but he is the primary creator, not a Category B specialist)

The gap: no high-volume (5+ catch-and-shoot 3PA per game) elite-accuracy (38%+) wing specialist on the roster. DiVincenzo was that piece. With him gone or diminished, the team is structurally short on Category B protection per LAFI Section 6's framing.

Quantify the gap:
- What was the team-level catch-and-shoot 3PA volume with DiVincenzo on the floor in 2024-25?
- What is the realistic team-level catch-and-shoot 3PA volume in 2026-27 without him?
- What is the LAFI C5 implication of this volume gap (using the LAFI v1 model)?
- What is the Sharp LAFI implication if the C5 gap propagates?

This is the H3c test. If the gap is large and not closeable internally, Q5's Path 2 (Category B catch-and-shoot acquisition) becomes more urgent, not just one of three optional paths.

### 5.4 The honest framing: this is a non-decision

Unlike Gobert and Randle, the DiVincenzo treatment does not produce a "keep or trade" verdict. The contract is what it is. The injury is what it is. The team is adapting.

What the analysis produces:

- Probability DiVincenzo contributes meaningfully in 2026-27 (with bands)
- Probability he returns to 2024-25 form by 2027-28 (with bands)
- The Category B gap his absence creates and its implication for Q5's Path 2 priority
- Cap implications for Q5 (a salary slot producing zero or limited value in 2026-27)

The verdict for Q5 framing: assume DiVincenzo provides 30-50% of his 2024-25 value in 2026-27 (median projection), and plan as though Path 2 must be partially closed by external acquisition. If he returns to form, that is upside. If he doesn't, the prescription was robust to the downside.

### 5.5 Integration with Gobert and Randle (the combined question expansion)

The original combined question in Section 6 covered four scenarios over Gobert and Randle. With DiVincenzo added, the combined question expands but with a recognition that DiVincenzo is not a choice variable. The scenarios remain at four (Gobert and Randle combinations) but each scenario is evaluated under two DiVincenzo states: median-recovery and minimal-recovery. This produces eight conditional outcomes rather than four. Most of the analysis aggregates over the two DiVincenzo states; the prescription notes which combinations are robust to either state and which depend on DiVincenzo coming back.

---

## 6. The combined question

Q8 should not treat Gobert and Randle as independent decisions. They interact.

### 6.1 The combinations

Four possibilities exist:

- Keep both
- Trade Gobert, keep Randle
- Trade Randle (or let walk), keep Gobert
- Move both

Each has implications. Specifically:

**Keep both:** The current roster shape continues. Q4 pathology likely continues unless system change closes the gap. Edwards development is the path that determines outcomes.

**Trade Gobert, keep Randle:** Naz becomes the starting 5. Defensive rating likely drops but offensive rating likely rises (Naz's catch-and-shoot opens the floor). Salary cap relief from Gobert opens flexibility for other moves. Randle stays as the power forward.

**Keep Gobert, move Randle:** Power forward becomes the open question. A different stretch four (catch-and-shoot specialist, more LAFI-friendly) could be acquired. Gobert keeps the defensive identity. The Q4 pathology may improve through power forward replacement.

**Move both:** Most aggressive option. Significant cap space opens. The team rebuilds the frontcourt around Edwards. Highest variance, both upside and downside.

### 6.2 The expected value framing

For each combination, estimate:
- Likely 2026-27 net rating
- Probability of advancing each playoff round
- Probability of championship
- Asset cost
- Cap implications

These are model outputs, not predictions. Wide ranges expected. Methodology: use the LAFI v1 evidence on lineup composition impact, plus standard cap and trade analysis, plus historical replacement estimates for the archetypes lost.

The output is not a single recommendation. It is a comparison of four scenarios with their evidence and uncertainty.

---

## 7. The math

### 7.1 On/off with proper controls

Raw on/off is noisy. For Q8, use:

- Multi-year pooled on/off where applicable
- Lineup-controlled on/off (compare lineups with player vs lineups without, holding other personnel constant)
- RAPM-style adjusted impact as a robustness check

### 7.2 Counterfactual lineup performance

For the combination analysis in Section 6, project counterfactual lineup performance using the methodology in Q6 (the KAT counterfactual). Substitute the projected replacement player's role characteristics into the lineup composition, recompute LAFI components and net rating.

### 7.3 Bootstrap uncertainty

Every claim about either player gets a confidence interval. With small playoff samples especially, point estimates without CIs are misleading.

### 7.4 The probability assignments

The final probabilistic verdicts (Sections 3.3, 4.4, 5.4) should not be made up. They should be the analyst's calibrated estimate after looking at all the evidence, with explicit reasoning about why each probability lands where it does. Document the reasoning.

---

## 8. Charts and visualizations

### 8.1 The Gobert On/Off Motion Chart

A bar chart showing the Wolves' off-ball motion measurements (distance traveled, off-ball screen frequency, cut frequency) in Gobert-on vs Naz-at-5 lineups. Visualizes Hypothesis H1a.

### 8.2 The Gobert Age Curve

Gobert's defensive metrics across his career plotted against the historical age curve for defensive-anchor centers. Shows whether he's ahead, on, or behind the curve.

### 8.3 The Gobert Lineup Heatmap

A specific cut of the lineup heatmap focused on Gobert-containing lineups. Best and worst.

### 8.4 The Randle Usage vs Efficiency

Scatter of usage vs TS% with Randle's last 5 seasons plotted alongside comparable high-usage power forwards. Shows whether his efficiency is justified by his usage.

### 8.5 The Randle Edwards-Dependence

A 2x2 chart showing Randle's lineup-level impact in the four Edwards-on/off and Randle-on/off conditions.

### 8.6 The Combination Scenarios

### 8.7 The DiVincenzo Recovery and Category B Gap (added 2026-05-17)

A two-panel chart. Left panel: comp-set recovery profiles for Achilles tears in guards aged 25-30, with DiVincenzo's projection bands overlaid. Right panel: Wolves' team-level catch-and-shoot 3PA volume in 2024-25 (with DiVincenzo) vs projected 2026-27 (without him at full form), showing the Category B gap size and its LAFI C5 implication.

A scenario comparison chart showing the four roster combinations from Section 5 with their projected net ratings and championship probabilities.

---

## 9. Sequencing

Q8 sits after Q2 (lineup foundation) and Q6 (KAT counterfactual provides comparison methodology) and before Q5 (which consumes Q8 findings).

1. Pull individual and lineup data for all three players
2. Run the Gobert hypotheses (3.1, 3.2)
3. Compute the Gobert age curve and synthesis (3.3, 3.4)
4. Run the Randle hypotheses (4.1, 4.2)
5. Compute the Randle reconciliation and synthesis (4.3, 4.4)
6. Build the DiVincenzo contribution quantification (5.1)
7. Build the DiVincenzo recovery projection (5.2)
8. Build the Category B gap analysis (5.3)
9. Build the combination analysis (6), evaluated under two DiVincenzo states
10. Build charts
11. Write up

Estimated time: 2-3 weeks (Gobert and Randle were the bulk; DiVincenzo adds roughly a week of additional work primarily for the recovery comp set and gap analysis).

---

## 10. What I'm worried about

### 10.1 Confirmation bias on Gobert

The user has stated a theory. The analyst (Claude advising the project) has expressed sympathy for it. Both could bias the analysis toward confirming the theory. The discipline: present the counter case with equal rigor, run the tests as designed (not designed to produce the desired result), report the findings honestly even when they disconfirm.

### 10.2 The Randle 2024-25 outlier problem

Randle's 2024-25 was the best season of the Edwards-era Wolves and Randle was a meaningful contributor. Concluding "Randle should go" requires explaining why the 2024-25 version was a peak that won't recur. This is a hard analytical claim. The honest version may be "we don't know" rather than a confident verdict.

### 10.3 Counterfactual lineup performance is model-output

The projections in Section 5 (combination analysis) are model outputs, not measurements. Wide ranges essential. Don't oversell precision.

### 10.4 The discourse temptation

Q8 will surface findings that align or disagree with public Wolves discourse. The temptation is to write toward the discourse. Resist. The findings are what they are. If they contradict popular opinion, say so plainly. If they align with popular opinion, say that too without performing surprise.

### 10.5 Player dignity

### 10.6 DiVincenzo recovery uncertainty (added 2026-05-17)

Achilles recovery for guards is well-documented but the per-individual variance is wide. Some players return to full form (Kevin Durant, partially). Others never recover their athleticism (Wesley Matthews, somewhat). DiVincenzo's specific profile (age 28, guard, fairly recent injury) suggests he can come back in some form, but projecting *which* form is inherently uncertain. Express the recovery bands with appropriate width; do not pretend to precision.

Both Gobert and Randle are real people with real careers. The analysis is about decisions, not character. The writeup should be analytical, not dismissive. "Trade Gobert" if that's the recommendation does not mean "Gobert is bad." It means "the current configuration is suboptimal." Maintain that distinction.

---

## 11. Success criteria

**Minimum viable:** Clean individual production analyses, lineup-level on/off with appropriate uncertainty, the Q4 fit hypotheses tested explicitly, honest probabilistic synthesis for each player.

**Strong:** The four combination scenarios are quantified with realistic ranges. The analysis can defend its probability assignments. Both player cases hold up to scrutiny in both directions.

**Stretch:** The analysis identifies a specific player decision (or non-decision) supported by strong evidence that no public analyst has surfaced. The kind of finding that a front office would want to act on regardless of what the talk shows are saying.

---

## 12. Open questions to revisit

1. ~~Whether to include other players (DiVincenzo's Achilles recovery, Conley's age, McDaniels extension implications) or keep narrowly to Gobert and Randle~~ **Resolved 2026-05-17:** DiVincenzo added per Section 5. Conley and McDaniels remain out of Q8 scope but get touched in Q0B (Conley's age) and Q5 (McDaniels extension implications via cap reality).
2. How to handle Randle's player option scenario tree (assume opt-in, assume opt-out, model both)
3. How much weight to give the 2024-25 Randle data vs the 2025-26 data in the synthesis
4. Whether to compute counterfactual lineups with realistic replacement players or with archetype averages
5. How to integrate Q8 findings with Q5's three-paths framework (does Q5 add a fourth path called "frontcourt restructuring"?)

---

## 13. The integration with the larger project

Q8 feeds Q5 directly. The three paths in Q5 (Edwards development, Category B catch-and-shoot, system change) become four paths if Q8 surfaces a strong frontcourt-restructuring case, or remain three paths with Q8's findings informing the cap and asset analysis within each existing path.

Q8's DiVincenzo section (5) feeds Q5 specifically on Path 2 priority. If the DiVincenzo Category B gap is large and unlikely to close internally, Path 2 (Category B catch-and-shoot acquisition) becomes more urgent in the Q5 portfolio rather than one of three optional paths. The DiVincenzo cap analysis also feeds Q5's overall cap reality section.

Q8 also serves as the public-facing entry point to the deliverable. A front office reader who flips to "what about Gobert" will find Q8. A fan reader who wants to know "should we trade Randle" will find Q8. A reader who wonders "what happens with DiVincenzo" will find Q8. The other analyses are the foundation; Q8 is the door.

---

End of specification.
