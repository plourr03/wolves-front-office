# Q7: Star Comparable Analysis Specification

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q7
**Status:** Specification, revised post-LAFI v1 (2026-05-17, minor)
**Position in stack:** Bridge analysis between Q0C (historical cohort) and Q5 (prescription). **Promoted in build sequence to immediately before Q5** per the post-LAFI replan, because LAFI showed the Wolves' team-level pathology is rare and not well-precedented, making star-level historical evidence the primary external benchmark for Q5.

**Revision note:** Spec content is largely unchanged from the original. Minor edits add the LAFI framing for why Q7's star-level evidence carries more prescription weight than originally assumed. One new hypothesis added per Issue 2 of the post-LAFI replan: did any historical comp stars play on teams with Wolves-like anomalous correlation patterns?

---

## 1. The thesis

### 1.1 The question

Which historical stars resemble Anthony Edwards in playstyle, usage, and trajectory, and what roster constructions around those stars produced championship outcomes vs failed outcomes? More importantly, what are the underlying principles those constructions encoded, and how do those principles translate to the modern NBA?

This analysis takes the question of "what should we build around Ant" out of the realm of pundit speculation and grounds it in 30 years of evidence about what has actually worked around similar players.

### 1.2 Why this matters

The standard fan and media framing of roster construction is shallow. It picks a specific player from the past (Kobe, MJ, Wade) and tries to find modern analogs of the players around them. That fails for two reasons.

First, **the league has changed.** The 2001 Lakers won with a slow-paced offense built around a back-to-the-basket center. That construction is unviable today because the modern game punishes that frontcourt with three-point volume, spacing, and pace. Trying to acquire "a modern Shaq" misses the point of why Shaq worked.

Second, **the star changes too.** Ant is not Kobe. He's not Wade. He's not Jordan. He has overlap with each but he's structurally his own player. Pretending he's a clone of a historical star and copying the historical roster around that star is a category error.

The right framing is to go up a level of abstraction. Identify the historical stars Ant resembles. Identify what *kinds* of pieces around them worked. Extract the *principles* (not the specific players). Then translate those principles through what the modern league looks like.

The output isn't "we should get a 2001-Shaq equivalent." The output is "stars like Ant historically need a co-star who can punish doubles, plus rim protection that allows aggressive perimeter pressure, plus at least one off-ball gravity threat. Here's how each of those principles looks in 2026."

### 1.3 The relationship to other analyses

This is a bridge spec.

**Q0C (Historical Cohort)** answers: what happened to teams that looked like ours overall.

**Q7 (this spec)** answers: what worked around stars who looked like ours specifically.

**Q5 (Prescription)** consumes both Q0C and Q7 to produce archetype-specific roster recommendations.

The order is: Q0C runs first, then Q7, then Q5 synthesizes them into a prescription. Q7 cannot run in place of Q5 because Q7's output is principles, not actionable archetype targets. Q5 takes those principles and combines them with the diagnostic findings (Q1-Q4) and the cap reality to produce specific archetype targets.

**Post-LAFI re-prioritization.** Following the LAFI v1 finding that the Wolves' team-level pathology (Q4 distributed pickup) is rare and not well-precedented, Q7's star-level evidence becomes the primary external benchmark for Q5. Where Q0C provides weak team-level analogies (because few historical teams share the Wolves' Q4 architecture), Q7 must provide stronger star-level ones. This re-prioritization is reflected in the build sequence: Q7 runs immediately before Q5, not in parallel with Q4. Q0B's Edwards trajectory analysis depends on Q7's comp output.

### 1.4 The era-translation principle

This is the methodological heart of the spec and what differentiates it from naive comp work. It's so important I want to state it directly.

**Historical roster constructions encode underlying principles that may or may not translate directly to modern equivalents. The analysis must identify the principle, not the player.**

Example. In 2003, Dwyane Wade had Lamar Odom and Eddie Jones around him. Modern eye-test analysis would say: get Ant a "Lamar Odom" (a tall, skilled forward with passing) and an "Eddie Jones" (a savvy wing defender). That's wrong. The principle behind Odom-Jones-Wade was: secondary creator who could initiate when Wade was off, plus length and defense on the wing to compensate for Wade's defensive ambivalence. The modern translation isn't "find a tall passing forward and a savvy old wing." It's "find a secondary creator and a wing stopper, calibrated to the modern league's spacing and pace demands."

The deliverable's value is in the translation, not the identification.

---

## 2. Identifying Edwards comparables

### 2.1 The features that matter

Star comp analysis is meaningless without a defensible similarity metric. The features that should drive Edwards comparability:

**Playstyle features:**
- Usage rate at age 24
- Three-point rate (3PA / FGA)
- Free throw rate
- Pick-and-roll ball-handler frequency
- Isolation frequency
- Rim-attack frequency
- Mid-range frequency
- Assist rate
- Turnover rate

**Physical and athletic features:**
- Height (6'4")
- Weight class (210-225 range, athletic build)
- Position (combo guard, primarily 2)
- Athletic archetype (explosive, downhill, vertical leaper)

**Career trajectory features:**
- Age of NBA entry
- Production curve from rookie year to age 24
- All-Star selections by age 24
- Playoff experience by age 24

**Star tier:**
- Filter to players who reached "top-15 in the league" status by their mid-20s
- Not just statistical similarity but ascended to franchise-cornerstone level

### 2.2 The candidate pool

The starting universe to evaluate for similarity:

**The obvious candidates (high overlap on playstyle and physicality):**
- Dwyane Wade (combo guard, explosive, downhill scorer, slashed and finished)
- Kobe Bryant (2 guard, scorer, athletic, midrange-heavy in his era)
- Vince Carter (early-career explosive shooting guard, dunk attacker)
- Allen Iverson (smaller but stylistically: high-usage scoring guard, isolation-heavy)
- Tracy McGrady (taller but: scorer, isolation, high-usage)
- Jamal Crawford (less successful but stylistically: combo guard, isolation, high-volume)

**The modern candidates (overlap on current league fit):**
- Bradley Beal (combo guard, scorer, mid-volume threes)
- Donovan Mitchell (combo guard, scoring leader, high usage)
- Jaylen Brown (similar physical build, athletic scoring wing)
- Devin Booker (high-usage scoring guard, more midrange-leaning)
- Zach LaVine (athletic 2-guard, scoring)
- DeMar DeRozan (high-usage scoring guard, midrange-heavy)

**The borderline candidates (worth checking for similarity):**
- Russell Westbrook (combo guard, attacker, but very different style)
- John Wall (combo guard, attacker, but different shooting profile)
- Andrew Wiggins (similar build, but never reached star tier)
- Brandon Roy (similar build, scoring guard, short prime)
- Penny Hardaway (taller but similar style early career)
- Steve Francis (combo guard, scorer)
- Larry Hughes (athletic 2-guard era comp)

**Outside the box candidates (different position but stylistic overlap):**
- LeBron James early career (different position but the "young athletic alpha scorer" archetype)
- Grant Hill (different position but high-usage, dynamic scorer pre-injury)

The actual comp set will be narrowed by the similarity metric. The starting universe just needs to be wide enough that the algorithm can pick.

### 2.3 The similarity computation

For each candidate, compute similarity to Ant across the feature set. Two approaches:

**Approach A: Weighted Euclidean.**
Z-score each feature across the candidate pool. Compute distance to Ant's feature vector with weights:
- Playstyle features: 50%
- Physical and athletic features: 20%
- Career trajectory features: 20%
- Star tier achieved: 10% (binary filter; the player has to have actually been a star)

**Approach B: Categorical filtering plus rank.**
Filter to players who match on key categorical features (combo guard, athletic build, scoring-first, made All-Star by age 24), then rank within that filter by playstyle similarity.

Run both. The top 8-12 comps that emerge from both approaches become the comp set.

### 2.4 Era-control consideration

A player's stats from 2003 are not directly comparable to 2026. Z-score features within era (or use league-relative metrics like usage rate, which is inherently relative). Document the era of each comp.

The era-control is also important for the downstream principle extraction. A 2003 stat profile that looks high-usage might be normal for that era. A 2025 stat profile that looks similar might actually be very high relative to its era. These are different things even when the raw numbers match.

---

## 3. Mapping the supporting casts

### 3.1 The cast for each comp

For each historical comp, identify the rotational pieces around them during their best and worst team-level outcomes. Specifically:

**For each comp, identify two team-seasons:**
- Their best playoff team (deepest run, ideally a championship or finals)
- Their best regular season team that fell short in the playoffs (the "should have won more" team)

**For each of those team-seasons, catalog the supporting cast:**
- The co-star (the second-best player)
- The third option
- The starting center / rim protector
- The starting point guard (if different from the star)
- The fifth starter
- The key bench contributors
- The coach

**For each cast member, classify their archetype, not their name.**

Archetypal taxonomy to use:

- **Secondary creator** (can initiate when the star is off or doubled)
- **Off-ball gravity threat** (catch-and-shoot or movement shooter at a level that bends the defense)
- **Defensive anchor** (rim protector who allows the star to gamble or rest defensively)
- **Switch-defender wing** (perimeter stopper who can hide the star defensively)
- **Stretch big** (frontcourt shooter that opens driving lanes)
- **Pure rim runner** (vertical spacer who threatens lobs)
- **Veteran point guard** (game-managing facilitator with low usage)
- **Microwave scorer** (bench instant offense)
- **Connective passer** (high-IQ, low-usage glue)
- **Versatile forward** (multi-positional defender, secondary playmaker)

The taxonomy should map every cast member to one or two archetypes. The point of the taxonomy is to abstract from player names to roles.

### 3.2 Why two team-seasons per comp

Comparing the championship version to the failed version of the same star tells us what made the difference. The star is the same player. The system might be different. The cast is different. The outcomes are different. What changed?

This is the heart of the principle extraction. It's not enough to know "Kobe won with Shaq and Pau." We need to know what was different between the 2004 Lakers that lost in the Finals and the 2009 Lakers that won. The differences tell us the principles.

### 3.3 The principle extraction

For each comp, write a short analytical brief that addresses:

1. What worked in the championship version?
2. What was missing or wrong in the failed version?
3. What was the offensive design that maximized the star?
4. What was the defensive design that compensated for the star's weaknesses?
5. How did the cast handle the star being doubled or schemed off?
6. How did the cast handle the star resting?
7. What was the playoff vulnerability that almost beat them, and how did they overcome it?

These briefs are the analytical work product, not the comp identification itself. The work is in the extraction, not the matching.

---

## 4. The Ant-specific feature analysis

Before extracting principles broadly, anchor on Ant specifically.

### 4.1 Ant's structural needs

From the diagnostic work (Q1-Q4), what specific needs has the analysis surfaced for Ant?

- A secondary creator who can punish blitzes and traps (Q3 finding: Ant gets blitzed because no one else can punish)
- Off-ball architecture that creates advantages before Ant has the ball (LAFI finding: Q4 offense, no pre-advantage)
- Rim protection that holds up against switching (Q3c finding: Gobert in drop concedes; Gobert in switch concedes more)
- Wing defense to hide Ant in matchups against elite primary creators (general principle)
- Shooting at the four or five to open driving lanes (LAFI Movement Death finding)

These specific needs should be cross-referenced against the principles extracted from the comp analysis. Where the principles align with the needs, that's high-confidence prescription. Where they diverge, that's where the era-translation work has to do the heavy lifting.

### 4.2 What Ant has that comps may or may not have had

Ant's profile has some features that are unusual even among similar combo-guard scorers:

- Playmaking growth trajectory (his assist rate has climbed every year)
- Three-point volume at high efficiency for his position
- Defensive engagement is variable but capable of high-end stretches
- Age 24 with relatively modest mileage (he played in college and entered the league young, but no significant injuries)

These features may shift which comps are most predictive. A star who couldn't pass may need a different cast than Ant. A star who couldn't shoot may also need a different cast. Document where Ant diverges from each comp and what that implies for principle translation.

---

## 5. The principle library

The deliverable's central artifact is a principle library: a set of testable, era-translatable principles extracted from the comp analyses. Each principle should have:

**The principle statement.** A single sentence describing what was true.

**The evidence.** Which comps support it, with what outcomes.

**The mechanism.** Why this principle works (the basketball logic, not just the correlation).

**The modern translation.** What this principle looks like in 2026, given league trends in pace, spacing, switching, three-point volume.

**The Wolves-specific application.** How this principle informs Wolves roster construction, given the current roster.

### 5.1 Candidate principles (hypothesized in advance, to be tested by the data)

These are my priors. Some may be confirmed by the comp analysis. Some may be refuted. Document either way.

**Principle 1: The secondary creator.** Star scorers historically have not won championships without a credible secondary creator who can run offense when the star is doubled or off the floor. The form of this secondary creator has varied (point guards, forwards, wings) but the function has been constant. Modern translation: a secondary creator who can also shoot off-ball when the star is on (a higher bar than historical comps, because spacing matters more now).

**Wolves-specific sub-principle (post-LAFI):** for Q4 architectures specifically, the secondary creator may need different traits than for Q3 architectures. Q3 single-star teams need a release valve (someone who can run offense when the star sits). Q4 distributed-iso teams need someone who can convert distributed touches into actual designed actions rather than more iso. This is potentially a different player profile (organizer + connector vs scorer). Whether this is a refinement of Principle 1 or a distinct principle depends on what the comp analysis finds.

**Principle 2: The rim protector.** Star scorers who can attack the rim have benefited from a rim protector who allows them to play more aggressively on defense (gambling, jumping passing lanes) without compromising the team defense. The form has shifted (Shaq to Bynum to Tyson Chandler to Gobert to Embiid to Mobley), but the function is consistent. Modern translation: rim protection that also has perimeter switchability is now the higher bar.

**Principle 3: The release valve.** Stars get tired. Stars get hurt. Stars sit. Championship teams have had an offense that functions for short stretches without the star on the floor. The "release valve" was sometimes a microwave scorer, sometimes a stable veteran, sometimes a backup point guard who could organize the offense. The principle: the non-star unit must be capable of treading water, not just losing minutes badly.

**Principle 4: The off-ball gravity threat.** Stars draw doubles. Doubles create open shots elsewhere. Those open shots need to be taken by players whose mere presence on the floor warps the defense. Catch-and-shoot threats above 38-40% from three at meaningful volume. Modern translation: the threshold for "warps the defense" has risen as the league has gotten more shooting-heavy. A 36% catch-and-shoot shooter that mattered in 2005 doesn't bend a defense in 2026.

**Wolves-specific application (post-LAFI):** LAFI's Path 2 finding maps directly to this principle. The Wolves lack Category B catch-and-shoot personnel at the volume and accuracy threshold that defines this principle. The Path 2 prescription depends on this principle being correct in modern terms. Q7's evidence on this principle (which historical comp stars had elite catch-and-shoot specialists, and what difference did it make for their championship outcomes?) becomes the primary external evidence for Path 2 in Q5.

**Principle 5: The defensive cover.** High-usage scoring guards historically have been the weaker defender on their team because their offensive load reduces their defensive energy. Championship teams have built defensive structures that hide this. A switch-everything front five. A rim protector behind. A stopper wing who takes the toughest perimeter matchup. The principle: the star's defensive limitations must be schemed around, not exposed.

**Principle 6: The two-way wing.** Almost every championship team with a primary-scorer guard has had at least one wing who could defend multiple positions AND contribute offensively. Pippen for Jordan. Wade had Eddie Jones then Bosh. Kobe had Artest then later Trevor Ariza. The principle: a two-way wing is the most-required cast member, more than a secondary creator in some comps.

**Principle 7: The non-shooting big problem.** Stars who shared the floor with non-shooting bigs have struggled in the playoffs against modern defenses unless the big provided exceptional rim protection AND the team had elite shooting elsewhere. This is the Gobert principle. Test it against the historical comps.

**(Post-LAFI addition) Principle 8 candidate: the anomalous-correlation question.** LAFI v1 surfaced that the Wolves have unusual cross-component correlations (C2 motion-death and C5 shot-quality move in lockstep for the Wolves, while uncorrelated league-wide). Did any historical comp stars play on teams with this kind of anomalous correlation pattern? If yes, what protected them from the structural disadvantage the Wolves face? If no, the Wolves' pattern is genuinely novel and the star-level historical evidence is weaker for predicting their specific outcome.

This is methodologically delicate because computing the anomalous correlation for historical comps requires multi-season tracking data, which is available only for 2014-15 onward (per the LAFI sample). For comps before that era, this principle cannot be tested at the cross-component grain. For comps within the LAFI sample, it can.

These seven (now eight) are starting hypotheses. The actual library will be refined by what the data says.

### 5.2 The translation framework

For each principle, the era-translation needs a framework. The framework dimensions:

**Pace difference.** Has the principle's mechanism become more or less important as the league has sped up?

**Spacing difference.** Has the modern three-point revolution made the principle's mechanism more or less important?

**Switching difference.** Modern playoff defenses switch more. Has the principle changed in a league where switching is the default?

**Foul rules difference.** The freedom-of-movement rules and the post-play rules have changed. Some historical principles may rely on rules that no longer exist.

**Scoring environment difference.** The league average offensive rating has risen sharply. Some principles that mattered when 105 ORtg was elite may matter differently when 118 is mid-tier.

Each principle's translation should explicitly walk through these dimensions.

---

## 6. The math

### 6.1 Similarity computation

Standard z-scored Euclidean distance with documented weights. Sensitivity analysis: run the analysis with the comp set varied by similarity threshold. If the principles are stable across different comp sets, they're robust. If they change with which comps are included, they're more fragile and should be presented with that caveat.

### 6.2 Outcome attribution

The hardest methodological piece. When a championship team had Cast Element X, did Cast Element X *cause* the championship, or was it correlated with other factors? The honest answer is: we can't fully resolve this. Star comp analysis is observational, not causal.

The mitigation: triangulate across multiple comps. If five comps all won championships and all had Cast Element X, the case is stronger than if one comp won. If three comps had Cast Element X and only one won, the case is weaker. The principle library should weight evidence by the consistency of the pattern across comps.

### 6.3 Era-translation quantification (where possible)

Some translations can be made quantitative. For example, the "off-ball gravity threat" principle can be operationalized as a specific three-point volume and accuracy threshold, era-adjusted. The principle "the wing shooter needs to be a true gravity threat" becomes "the wing shooter should be above the 85th percentile of catch-and-shoot threes in the current league," which translates cleanly across eras.

Other principles are harder to quantify. "The team must function without the star on the floor" is qualitative. For these, the deliverable should acknowledge the qualitative nature rather than fake precision.

---

## 7. Charts and visualizations

### 7.1 The Comp Set

A 2D scatter of the candidate pool projected onto two principal components of the feature set. Ant highlighted. The top 8-12 comps highlighted. Visualizes who is similar and how similar.

### 7.2 The Cast Archetype Matrix

A grid: rows are the comp stars, columns are archetypes. Cells indicate which archetypes each comp had on their championship team (in one color) and on their failed team (in another). Patterns emerge visually.

### 7.3 The Principle Strength Chart

A horizontal bar chart of each principle, with bar length showing the evidence strength (number of comps supporting it) and color showing the era-translation difficulty.

### 7.4 The Wolves Gap Map

For each principle, where the current Wolves roster sits relative to it. A radar chart or scorecard. Highlights which principles the Wolves are currently meeting and which they are not.

### 7.5 The Translated Archetype Targets

The final visualization: for each principle the Wolves are not meeting, a list of archetype targets translated into modern terms. This feeds directly into Q5.

---

## 8. Sequencing

Q7 can run in parallel with Q4 (archetype stress test). It depends on Q0C (historical context) and Q1-Q3 (Wolves diagnostic findings). It feeds Q5 (prescription).

Within Q7:
1. Build the candidate pool feature dataset (Ant's features plus the historical candidates)
2. Compute similarity, select comp set
3. For each comp, identify the championship team-season and the failed team-season
4. Catalog the supporting casts using the archetype taxonomy
5. Write the principle extraction briefs (one per comp)
6. Synthesize the principle library across comps
7. Apply the translation framework to each principle
8. Map principles to Wolves' current gaps
9. Build charts
10. Write up

Estimated time: 2-3 weeks of evenings.

---

## 9. What I'm worried about

### 9.1 The "let me find the comp I want" trap

The biggest risk in star comp analysis is that the analyst pre-selects comps that support a desired conclusion. To mitigate this: the comp set should be determined by the similarity metric, documented before the principle extraction, and not changed once chosen.

If a particular comp produces inconvenient results, it stays in the set. If a comp who would support a desired narrative doesn't make the set, they stay out.

### 9.2 Era translation is judgment

Some translations are clean (gravity-shooter threshold can be quantified). Others are not. Where translation is judgment, the deliverable must say so. Don't fake precision.

### 9.3 Cast attribution is observational

We don't have randomized roster construction trials. Every claim about "Cast Element X mattered" is observational. Multiple comps support a stronger inference, but the analysis should be honest about not establishing causation.

### 9.4 Ant might not be a "Kobe type"

The whole frame assumes Ant is similar enough to some set of historical stars to make comp analysis informative. If the similarity metrics produce no comps with strong overlap, the analysis is in trouble. The mitigation: don't artificially force a comp set. If Ant is genuinely a unique archetype, the deliverable should say so and pivot to first-principles analysis.

### 9.5 The temptation to pre-commit on Wembanyama-era trends

The Wolves' current playoff opponent (Spurs with Wembanyama) is shaping how we think about the future of the league. There's a real risk of over-indexing on what beats Wembanyama specifically and missing what wins championships generally. The principle library should be league-wide, not Wembanyama-specific.

---

## 10. Success criteria

**Minimum viable:** A defensible comp set, a documented principle library with at least 5 principles, and an honest translation of each into modern terms.

**Strong:** The comp set holds up across sensitivity analyses, the principle library is supported by evidence across multiple comps, and the translation provides clear archetype targets for Q5.

**Stretch:** The analysis identifies at least one principle that contradicts conventional wisdom and is supported by the data. (Example hypothetical: "Star scoring guards have historically won more without a co-star creator than with one if the supporting cast had enough shooting." This would be contrarian but if true, it changes the prescription.)

---

## 11. Open questions to revisit

1. The exact weights in the similarity computation
2. Whether to include LeBron's early career (different position) as a comp or exclude
3. Whether to compare championship version vs failed version within the same career, or championship version of one star vs failed version of a different star
4. How much weight to put on Edwards' specific developmental trajectory (playmaking growth) vs his current state in choosing comps
5. Whether to extend the comp pool internationally or to ABA era
6. How to handle stars whose careers were derailed by injury (Brandon Roy, Penny Hardaway) - same archetype but different sample size for outcomes

---

End of specification.
