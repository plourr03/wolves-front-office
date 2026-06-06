# Q0A LAFI: Wolves Diagnosis

**Phase 5 of the LAFI analysis.**
**Date:** 2026-05-16
**Status:** Draft. The spine of the eventual front-office deliverable.

---

## Executive summary

The 2025-26 Minnesota Timberwolves play offense in a structurally novel way that the rest of the NBA has not had to defeat at scale. The LA Fitness Index framework places them at the 90th percentile on the subset of components that predict playoff offensive collapse (Sharp LAFI), but only the 65th percentile on the full composite. That gap is the diagnosis: the team is extreme on the dimensions that matter for playoff offense, and only moderate on the dimensions the league has historically learned how to beat.

The historical playoff-failure archetype is single-star pickup, captured by Component 1 (Ball Stickiness). One creator dominates the ball; defenses scheme that one player; the offense breaks. The data shows this archetype consistently underperforms in the playoffs across the last decade (univariate p=0.030).

The Wolves do not fit that archetype. They are 30th percentile on stickiness. Their failure pattern is different: distributed pickup, where multiple players take turns isolating while no one moves off-ball, and the resulting shot diet decays sharply. This pattern is rare historically and has not had a counter-scheme developed against it because nobody has tried it at this scale.

This makes the Wolves' diagnosis sharper, not softer. They are not the latest example of a known failure mode that someone else has solved. They are running a novel failure mode that has to be thought through from first principles. The fixes that worked for other pickup-leaning teams (acquire a secondary creator, lean into the star) do not directly apply.

---

## Section 1: Where the Wolves rank

**The Wolves' 2025-26 LAFI profile, regular season, percentile rank against the 2014-15 through 2025-26 league sample:**

| Metric | Wolves percentile | League position |
|---|---|---|
| **Sharp LAFI (C2+C3+C5)** | **90** | **3rd** behind PHI (93), LAC (92) |
| Full LAFI (all 5 components) | 65 | ~13th |
| C1 Ball Stickiness | 31 | bottom third |
| C2 Movement Death | 72 | top third |
| C3 Isolation Reliance | 90 | top 10% |
| C4 Action Poverty (v1) | 45 | middle |
| C5 Shot Quality Decay | 83 | top 17% |

The gap between Sharp LAFI (90) and Full LAFI (65) is the structure of the diagnosis. The Wolves are not extreme on every component. They are extreme on the three components that capture how playoff offenses actually break: bodies not moving off the ball (C2), too much isolation (C3), bad shots as the consequence (C5).

The Sharp LAFI metric isolates this signal. It puts the Wolves third in the league behind two teams with established sticky-and-iso offenses (Philadelphia with Embiid/Maxey, the Clippers with Harden/Kawhi/George). The Wolves are in elite company on the playoff-relevant subset.

The Full LAFI dilution to 65th percentile is the other half of the story. The Wolves are not classically pickup. They are not sticky like Brunson Knicks (C1 high) or playbook-poor like the LAC iso-narrow offense (C4 high). They sit at moderate values on those components. The pathology lives in three specific dimensions, not all five.

---

## Section 2: The Edwards-era trajectory, a four-act story

The five-component evolution from 2022-23 through 2025-26 reads as four distinct acts.

| Season | C1 sticky | C2 motion-death | C3 iso | C4 action-pov | C5 shot-qual | Full LAFI | Sharp LAFI |
|---|---|---|---|---|---|---|---|
| 2022-23 (Gobert year 1) | 14 | 64 | 44 | 31 | 47 | 34 | 53 |
| 2023-24 (WCF year) | 35 | 43 | 49 | 27 | 39 | 35 | 45 |
| 2024-25 (Randle year 1) | 69 | 56 | 71 | 36 | 72 | 63 | 71 |
| **2025-26 (Randle year 2)** | **31** | **72** | **90** | **45** | **83** | **65** | **90** |

**Act 1, 2022-23: the Gobert integration year.** Moderate stickiness (14), high motion death (64), moderate iso (44). The defining feature: motion died early in the Gobert era because the offense had not figured out how to play with him. The Wolves were already a "bodies do not move" team but not yet an iso team.

**Act 2, 2023-24: the WCF breakthrough.** The most designed version of the offense. Stickiness rose slightly (35) as Edwards became more central, but motion came back (43), iso stayed contained (49), shot quality was the cleanest of the era (39). This was the most designed version of the offense and it produced the deepest playoff run of the Edwards era. The data validates that 2023-24 was the high-water mark not just in record but in offensive structure.

**Act 3, 2024-25: the Randle integration.** The most diagnostic year. Stickiness jumped to 69 (Randle dominated possessions as the team figured out how to use him). Motion died slightly more (56). Iso jumped (71). Shot quality cratered (72). The team reached the conference finals but the offense was already structurally different. Q3-leaning (single-star pickup with Randle as the engine).

**Act 4, 2025-26: the Q4 collapse.** Stickiness fell back to 31 (Randle no longer dominating, iso load decentralized). Motion died worse (72). Iso reached extreme (90). Shot quality continued its decline (83). They became the distributed-iso, dead-off-ball team this analysis has been diagnosing.

The Edwards-era progression on three components moved in clear lockstep:

- C2 motion-death: 64 → 43 → 56 → 72
- C3 iso-reliance: 44 → 49 → 71 → 90
- C5 shot-quality-decay: 47 → 39 → 72 → 83

The 2023-24 dip on all three was the WCF year working. The 2024-25 to 2025-26 rise on all three is the current collapse. Three components, three identical-shaped curves.

This is what the Phase 3 PCA validated. PC2 of the league's offensive space independently surfaces the Q3 vs Q4 distinction, which means the four-quadrant framework is a real structural axis in NBA offensive style, not just an analyst mental model.

---

## Section 3: The C1 contrast (the new and most important section)

This is where the validation findings reshape the diagnosis.

**The historical playoff-failure pattern is single-star pickup (high C1).** Univariate regression on the 144 playoff team-seasons since 2014-15: C1 coefficient -0.023, p=0.030, 95% bootstrap CI entirely negative ([-0.046, -0.002]). Teams in the top quartile of C1 have systematically underperformed their regular-season strength in the playoffs.

**The historical examples:**

| Team-season | C1 percentile | Playoff wins | Note |
|---|---|---|---|
| DAL 2022-23 (Luka pre-Kyrie) | 95 | 0 | Missed playoffs |
| POR 2017-18 (Lillard McCollum) | 98 | 0 | Round 1 sweep |
| HOU 2017-18 (Harden, peak iso) | 99 | 10 | WCF in 7 |
| OKC 2017-18 (Westbrook PG) | 99 | 2 | Round 1 |
| HOU 2018-19 (Harden) | 100 | 5 | Lost WCF |
| ATL 2021-22 (Trae) | 98 | 1 | Round 1 |
| OKC 2018-19 (Westbrook) | 97 | 1 | Round 1 |
| LAC 2023-24 (Harden Kawhi PG) | 97 | 2 | Round 1 |
| POR 2019-20 (Lillard CJ) | 100 | 1 | Round 1 (bubble) |

The shape is consistent. A team becomes C1-extreme. The defense schemes the dominant ball-handler. The offense breaks. The league has had a decade to learn how to beat this archetype, and the playoff data shows it does.

**The Wolves are 30th percentile on C1.** They are not playing this kind of offense. Edwards is not a Harden-style ball-dominant handler. His time-of-possession share is 21.6% of team total, well below the 25-35% range that defines Q3 ball-dominant offenses.

If the Wolves were a Q3 team, the historical record would suggest specific fixes. Houston post-Harden traded him and rebuilt around younger players. Atlanta post-Trae moved off the iso-star architecture. The league's playoff-failure mode has known counter-moves.

The Wolves' Q4 pathology does not appear in this historical sample. There is no clean comp for "high motion death + decentralized iso + bad shot quality + moderate stickiness + normal-breadth playbook." It is not in the data because it has not been tried at scale.

**Implication.** The Wolves' diagnosis cannot lean on "do what the post-Harden Rockets did" because they are not in the same architectural state. The prescription has to be derived from the components of their specific pathology, not from a historical playbook.

---

## Section 4: The Q3 vs Q4 framework with quantitative validation

The four-quadrant framework on the (C1 stickiness, C2 motion-death) plane:

| Quadrant | (C1, C2) | Archetype | Failure mode |
|---|---|---|---|
| Q1: Designed | low, low | Warriors, Pacers, post-Trae Hawks | Rare. Gold standard. |
| Q2: Star-fed motion | high, low | Brunson Knicks | Survivable if the creator is elite. |
| Q3: Single-star pickup | high, high | Harden Rockets, Trae Hawks, Westbrook OKC | The known playoff-failure mode. |
| Q4: Distributed pickup | low, high | **Wolves 2025-26** | Historically rare. Not a known failure mode. |

The Phase 3 PCA independently surfaced this axis. PC2 (22% of variance) loads with one end at "high motion death + narrow playbook + good shot quality" (Q3 single-star) and the other end at "high iso reliance + bad shot quality + more motion" (Q4 distributed). The PCA was run blind on the five-component data and arrived at the same axis we developed qualitatively from cross-component reasoning. That is methodological convergence.

**League placement 2025-26 RS, by quadrant:**

| Team | C1 | C2 | Quadrant |
|---|---|---|---|
| GSW | 0 | 2 | Q1 extreme (designed) |
| IND | 5 | 24 | Q1 (Pacers motion) |
| ATL | 26 | 15 | Q1 post-Trae |
| BOS | 77 | 23 | Q2 (sticky+iso but bodies move) |
| LAC | 84 | 51 | Q3-leaning (Harden + Kawhi + PG) |
| PHI | 86 | 86 | Q3 extreme (Embiid heavy) |
| LAL | 89 | (n/a) | Q3-likely (LeBron + Luka) |
| OKC | 92 | (n/a) | Q3-leaning (SGA-concentrated) |
| **MIN** | **31** | **72** | **Q4. Distributed pickup, dead off-ball.** |

The Wolves sit nearly alone in Q4. PHI is the closest by raw component values but PHI is sticky (Q3) and the Wolves are not. The four-quadrant placement is what makes the Wolves architecturally distinct.

---

## Section 5: The Wolves-specific correlation anomaly

Across the league, motion death (C2) and shot quality decay (C5) are essentially uncorrelated (Pearson r = 0.059, n = 330). Most teams that have dead off-ball motion still produce normal-quality shots, because their on-ball creator manufactures shot quality despite the lack of motion, or because their off-ball shooters convert from stationary positions.

For the Wolves' last three seasons, motion death and shot quality decay have moved in lockstep. C2 went 43 → 56 → 72; C5 went 39 → 72 → 83. The two components rose together.

This is not the league-wide pattern. The Wolves have an internal correlation between motion death and bad shots that other teams do not have.

**Why this matters.** The mechanism connecting motion death to bad shots needs to be explained, not assumed. League-wide, motion death does not cause bad shots. So what causes the Wolves' motion death to cause bad shots when it does not cause bad shots for the rest of the league?

The working answer (developed in Section 6 below): the Wolves do not have the personnel that protects most motion-dead offenses. Their motion death produces bad shots because they have neither the star-tier solo creation nor the elite catch-and-shoot specialists that other motion-dead teams use to manufacture shot quality from stationary positions.

The component-relationship anomaly is the deeper version of the diagnosis. The Wolves are not just elevated on the levels of certain components. They have built an offense where the components do not connect to each other the way they connect for typical NBA teams. That is an architectural problem at a level deeper than any single elevated metric.

---

## Section 6: The mechanism, why this pathology is hard to fix

Most teams with dead off-ball motion fall into one of two categories.

**Category A: Star-anchored isolation.** The team has a transcendent on-ball creator (Luka Doncic, Shai Gilgeous-Alexander, prime James Harden) who can manufacture good shots from isolation despite the lack of motion. The star bends the defense one-on-one. The off-ball players do not need to move because the star creates enough advantage by himself.

**Category B: Specialist shooting.** The team has elite catch-and-shoot personnel (Klay-era Warriors, Buddy Hield-style specialists, certain Hawks configurations) who produce good shots from stationary positions because they are so good at the shot itself.

The Wolves are in neither category.

**On the star tier.** Anthony Edwards is a great scorer but not yet at the Luka or SGA level of solo defense-breaking. His 2025-26 time-of-possession share of team total is 21.6%, which is moderate, not elite-dominant. Defenses scheme him with help and force the ball into other hands, where the iso load gets distributed to Randle, McDaniels, Naz Reid, and others. The decentralization the Phase 3 Herfindahl analysis surfaced is the structural symptom: the team is allocating iso possessions across many players because no single player is bending the defense enough to make iso a one-stop solution.

**On the shooting tier.** The Wolves' catch-and-shoot personnel in 2025-26 is good not great. DiVincenzo (38.3% on 496 catch-and-shoot 3PA) was the elite specialist but he is out for the year. Naz Reid (38.1% on 344), Jaden McDaniels (45.1% on 162), and Mike Conley (38.9% on 108) are reliable but not at the volume or accuracy of a Klay Thompson tier shooter. Ayo Dosunmu (42.9% on 231) is the best efficiency but at a lower volume tier. The team has good shooting; it does not have elite catch-and-shoot specialists who can manufacture shot quality from stationary positions in the way Category B teams can.

**The architectural problem.** The Wolves have neither escape hatch. Their motion death produces bad shots specifically because they do not have the personnel that protects motion-dead offenses elsewhere. The mechanism is not "the offense is dysfunctional." The mechanism is "the offense has built itself in a configuration that requires either of two specific personnel profiles to function, and the team has neither."

This points to three potentially independent fixable paths, not one:

1. **Edwards develops into Luka/SGA tier solo creation.** Realistic over multiple seasons but not in the current playoff window.
2. **Acquire elite catch-and-shoot specialists.** Buyer's market for shooters at the trade deadline; specific Q5 question.
3. **Restore designed off-ball motion.** System change; the actions exist in the playbook (the Wolves run all 11 Synergy play types at >=3%) but are not being called or run when called.

Any one of the three closes the gap. The current state has none of them.

---

## Section 7: The Spurs matchup, structural counterargument

The Spurs are the team most structurally opposite to the Wolves in the entire league on the LAFI dimensions.

| Component | Wolves 2025-26 | Spurs 2025-26 | Gap |
|---|---|---|---|
| C1 Ball Stickiness | 31 | 38 | similar |
| C2 Movement Death | 72 | 56 | +16 (Wolves worse) |
| C3 Isolation Reliance | 90 | 28 | +62 (Wolves much higher) |
| C4 Action Poverty | 45 | 15 | +31 (Wolves narrower playbook... but both broad) |
| **C5 Shot Quality Decay** | **83** | **11** | **+72 (massive)** |
| Full LAFI | 65 | 23 | +42 |
| Sharp LAFI | 90 | 27 | +63 |

The Spurs are designed across every component. They are low on iso reliance, low on action poverty (broad playbook), and have one of the cleanest shot diets in the league. They are also anchored defensively by Wembanyama (elite rim protection) and switchable perimeter defenders (Vassell, Sochan, Castle).

This is the worst possible matchup architecture for a Q4 offense. The Q4 pathology depends on iso advantage creation (the offense's only mechanism). The Spurs counter both ways:

- **Wembanyama at the rim** lets the rest of the defense take risks they otherwise could not. Aggressive doubles on Edwards because the rotation is covered. Switches onto Randle in the post because help shrinks his space. Catches by McDaniels or Reid because the drive into help is waiting.
- **Switchable perimeter** lets every iso get a competent defender without compromising rotations.

The 71-percentile-point gap on shot quality is the result. The Spurs' offense generates clean shots (11th percentile on shot quality decay, very low; the system manufactures the right looks). The Wolves' offense generates bad shots (83rd percentile; the iso-and-no-motion architecture produces late-clock pull-ups). One team gets the right shots; the other gets the wrong shots; the gap compounds across a seven-game series.

**This is not bad luck or a hot opponent.** The Wolves drew the team architecturally most equipped to beat them. If they had drawn a different second-round opponent with a more conventional offensive profile and weaker rim protection (the Lakers, the Mavericks, the Heat), the series might have produced a very different result. Q4 archetype stress-testing (Q4 analysis spec, separate) will formalize this. We already have a strong signal.

---

## What this implies for Q5 (prescription)

This diagnosis pushes Q5 toward first-principles analysis rather than historical-comp pattern matching.

1. **The standard pickup-team fix template (acquire a secondary creator, lean into the star) does not apply** because the Wolves' pathology is not single-star pickup. They already have distributed touches; adding more creators does not close the architectural gap, it might widen it.

2. **The three independent paths from Section 6 are the candidate fixes:** Edwards development, catch-and-shoot personnel acquisition, designed-action restoration. Q5 should evaluate each on cost (cap, asset, time) and likely impact (close how much of the Sharp LAFI gap).

3. **The Wolves cannot afford to treat this as "we are the latest Rockets-style team."** They are not. Their failure mode is novel. Q5's prescription should explicitly grapple with the fact that the precedent literature does not have a clean comp for their pathology.

4. **The Spurs matchup analysis suggests opponent-specific roster construction matters.** If the path to the Finals requires beating an elite-rim-protection team, the Wolves need either a Category A or Category B personnel upgrade. Q5 should test how much each upgrade changes the projected matchup outcome.

---

## What this diagnosis is honest about

The LAFI framework does not predict the Wolves' playoff outcome deterministically. The strongest predictive finding was Component 1 (Ball Stickiness) and the Wolves are not C1-extreme. The Sharp LAFI prediction (binary "advanced past round 1") gives the Wolves roughly a one-third probability of advancing, controlling for net rating; that is a real estimate but not certainty.

The Wolves' second-round struggles against the Spurs are consistent with the architecture but not predicted by it with high confidence. The diagnosis explains the mechanism more than it predicts the outcome.

The v1 components in Action Poverty and Shot Quality Decay rely on Synergy and tracking proxies. The full action classifier (v2 work, separate from LAFI v1) would refine the action-poverty reading. The current diagnosis is robust enough for v1 conclusions; v2 may sharpen or qualify them.

The Wolves' Q4 placement is supported by Phase 3 PCA but the sample of Q4 historical comps is small. The "novel failure mode" framing is supported by the data but it is also a forward-looking claim. Future seasons of Q4-leaning teams (if they emerge) would test it.

---

## What the front office should read off this diagnosis

Three things.

**First.** The 2023-24 WCF version of the offense is the most designed version this team has had. The structural shape of that team (KAT gravity, off-ball motion, Edwards as second creator rather than primary handler) is reachable again. The 2025-26 collapse is two seasons of post-trade drift away from that shape, not an unrecoverable structural change.

**Second.** Edwards is on a development trajectory. If he reaches Luka or SGA tier solo creation in the next two seasons, the Wolves get Category A protection automatically. The team can support a developing star with personnel choices in the meantime: more catch-and-shoot, more off-ball motion, fewer halfcourt isos by design.

**Third.** The current configuration is not a known failure mode. There is no historical playbook for fixing distributed pickup ball with moderate stickiness, dead off-ball, and bad shot quality, because that combination has not been tried at scale. The front office is not behind in solving a known problem; it is ahead in encountering a new one. The standard moves (trade for a secondary creator, lean into the star) do not directly apply. The right moves are derived from the components of their specific pathology.

The diagnosis is severe. It is not hopeless. The structural problems are nameable, measurable, and at least partially fixable. Q5's job is to translate this diagnosis into specific acquisition paths and system changes.
