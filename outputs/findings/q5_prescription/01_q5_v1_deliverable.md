# Q5: Prescription for the Minnesota Timberwolves

**The 2025-26 postmortem and roster construction recommendation**

**Date:** 2026-05-18
**Status:** Q5 v1 draft. The culminating document of the Timberwolves 2025-26 Postmortem project. **SUPERSEDED.** Q5 v2 supersedes this; Q5 v3 supersedes v2. Preserved for audit trail.

> **NOTE 2026-05-18:** This v1 contains the contract structure error corrected in `04_contract_structure_correction.md`. Specifically: "non-guaranteed 2027-28" framings for Gobert and Randle are wrong (both are player options that the players will exercise). Do not use this v1 for any current-state interpretation. See Q5 v3 (revised) for active prescription.
**Author note:** Built from the diagnostic work of Q1, Q2 (+ corrections + yoy comparison), Q3, Q0D, Q8 (+ salary addendum + weighted-recent RAPM), LAFI v1, plus supporting analyses (Gobert career arc, Edwards injury timeline). Every prescription in this document is referenced to the underlying finding.

---

## Executive summary

The Minnesota Timberwolves' 2025-26 playoff loss to the San Antonio Spurs was the result of three things acting together: the team's offensive architecture (Q4 distributed pickup, LAFI v1), Donte DiVincenzo's Achilles tear in Round 1 (the largest negative impact shock on the roster), and the Spurs' Wembanyama-anchored switch-everything defensive scheme that specifically suppressed Anthony Edwards' three-point creation. None of these are individual player failures. Rudy Gobert, Julius Randle, and Anthony Edwards were all positive contributors at the individual level.

**The prescription is "build the personnel context Edwards needs."** Specifically: add a Category B catch-and-shoot wing through the mid-level exception or trade; expand Jaden McDaniels' Category B role from current 2.2 to 4+ catch-and-shoot 3PA per game; restore Gobert's PR-Roll-Man volume and Edwards' PR-Ball-Handler share to 2023-24 levels through coaching emphasis; protect Donte DiVincenzo's Achilles recovery and plan around his summer 2027 free agency as a re-signing priority if he proves out; preserve the 2027 cap reset (Gobert and Randle 2027-28 non-guaranteed years) as a strategic asset for major roster moves in summer 2027.

**We are NOT recommending trading Gobert.** Gobert's RAPM is positive in both pooled and 2025-26-only samples. His defensive impact is intact and likely top-5 league-wide. His decline is offensive and plausibly system-recoverable (his PR-Roll-Man volume dropped 41% year-over-year per Q0D). The case for trading him is weak.

**We are NOT recommending trading for Giannis Antetokounmpo or Kevin Durant.** The diagnostic findings do not point at superstar acquisition as the bottleneck. The trade math required to acquire either would deplete the existing core (likely costing Edwards or most of the rotation) in ways that may not improve net rating. See Section 11 for the honest engagement with this question.

**The Randle disposition is conditional.** His 2025-26-only RAPM is essentially neutral (-0.07) but his $30.9M salary produces the largest negative surplus on the roster (-2.57 vs implied tier threshold). Trade ONLY if a clear LAFI-Category-B-friendly upgrade is available at his salary slot or if cap relief enables multiple Category B additions that beat his marginal value in aggregate. Otherwise keep, deploy correctly (maximize Edwards+Randle and Gobert+Randle minutes), and reassess at trade deadline.

**Three portfolios are presented (A, B, C).** Portfolio A "Build the supporting cast" is the default recommendation. Portfolio B "Targeted upgrade" is the upside scenario contingent on Randle trade execution. Portfolio C "Preserve 2027 flexibility" is the patient option that minimizes 2026-27 moves to maximize 2027-28 cap room.

---

## 1. The diagnosis

### 1.1 What broke (Q1)

The Wolves' 2025-26 playoff offensive collapse was statistically distinguishable from league norms in two specific places:

- **Off 3PA rate:** -0.078 (42.0% RS → 34.2% PO), 95% CI [-0.104, -0.054], z = -2.16 vs league norms
- **Off eFG:** -0.065 (0.559 RS → 0.495 PO), 95% CI [-0.087, -0.040], z = -1.50

Both CIs exclude zero. The team's offensive collapse was a real, statistically supported finding, not a small-sample artifact.

The net rating dropoff (-9.07 points) had a wider CI that crossed zero, but the component-level offensive decline was robust. The defensive rating held essentially flat.

### 1.2 Where it broke (Q2 + corrections + yoy)

The Wolves' most-played 2025-26 playoff lineup configuration was Gobert+Randle on the floor with Naz off (203.8 minutes, net rating **-13.26**, 95% CI [-27.94, +1.50]). Within-series breakdown: Round 1 vs DEN -3.04, Round 2 vs SAS -26.46. The collapse was almost entirely Spurs-specific.

**The yoy lineup comparison revealed the same configuration was POSITIVE in regular seasons of both years** (2024-25 RS: +5.71 over 1217 min; 2025-26 RS: +4.57 over 1348 min). The 2025-26 PO -13.26 is opponent-specific, not structural year-long.

**The DiVincenzo Category B finding is the cleanest empirical foundation:** in 2025-26 RS, DiVincenzo-on lineups were +7.57 net rating over 2463 minutes with 95% CI [+3.0, +12.2] (statistically positive). DiVincenzo-off lineups were -4.57. A 12-point on/off swing. He was the team's most important contributor by adjusted impact.

### 1.3 The mechanism (Q3)

The Spurs' Wembanyama-anchored switch-everything defensive scheme suppressed Edwards' specific shot creation:

| Metric | RS baseline | vs SAS (R2) | Change |
|---|---|---|---|
| 3PA per game | 8.43 | **5.33** | -37% |
| Average shot distance | 15.29 ft | **13.24 ft** | -2.0 ft |
| Catch-and-shoot share | 13.8% | **6.2%** | less than half |
| Shots in 11-16 ft (floater) | 14.6% | **21.2%** | +6.6 pp |
| Shots in 23-25 ft (3pt) | 25.8% | **16.8%** | -9.0 pp |

**Edwards adapted individually.** His FG% on the shorter shot diet was 46.9% (RS: 48.9%). His eFG only dropped modestly (.522 vs .572). The Spurs didn't break him as a scorer; they broke him as a three-point creator and as a screen-and-roll engine for teammates. The team's secondary creation (Randle, Gobert) couldn't convert his kickouts.

**Replicability is partial.** OKC has the league's best defensive rating (106.6) and rim protection (60.1% opp rim FG%, league best). Their architecture could plausibly recreate elements of the Spurs' scheme. Multiple Western Conference teams have similar architectural elements. Wembanyama's specific versatility is harder to fully replicate, but the broader class of switch-everything-with-rim-protection schemes is a recurring threat.

### 1.4 The system context (Q0D)

The Wolves' 2025-26 offense shifted allocation versus 2023-24:
- Spot-up: 27.2% → 22.9% (-4.3 pp)
- Transition: 14.9% → 19.0% (+4.1 pp)
- Isolation: 7.4% → 9.6% (+2.2 pp)
- PR-Ball-Handler: 14.4% → 13.1% (-1.3 pp)
- PR-Roll-Man: 5.6% → 4.2% (-1.4 pp)
- Cut: 6.1% → 5.2% (-0.9 pp)

**The "designed actions" share dropped 5.8 percentage points** (61.9% → 56.1%).

But **the allocation restoration impact is small.** Restoring 2023-24 allocation with current personnel and per-play-type efficiency would gain only **+0.35 ORtg points per 100 possessions**. Well below the +2-point threshold for "system change as standalone lever has empirical support." The Spot-up reduction (-4.3 pp at 1.118 PPP) is almost exactly canceled by the Transition increase (+4.1 pp at 1.167 PPP). Both are high-PPP play types.

**The targeted role restorations are higher-leverage than broad allocation change:**
- Gobert's PR-Roll-Man volume dropped 41% (188 → 111 possessions). His PPP on the action remained elite at 1.27. Restoring 50-77 possessions would add +0.6 to +1.0 ORtg points concentrated in his minutes.
- Edwards' PR-Ball-Handler share dropped 10 percentage points from 2024-25 to 2025-26 (33.3% → 23.5%). Restoring would recover 2-3 catch-and-shoot 3PA per game team-wide.

### 1.5 The player-level picture (Q8 + salary addendum + weighted-recent RAPM)

**DiVincenzo:** Highest impact player in the 2025-26 sample (RAPM +4.84, rank #1 of 404). Catch-and-shoot 3PA volume in 2025-26 RS: 6.05/game at 38.3% on 496 attempts across 82 games (elite Category B production). Achilles tear in Round 1 is the largest negative impact shock on the roster. Salary $12.0M producing +4.34 surplus (massive underpay).

**Gobert:** Three-year pooled RAPM +6.18 (rank #1 in 565-player sample, defensive RAPM -6.89 the lowest in sample). 2025-26-only RAPM +1.98 (still top-5 in league sample). Net decline of 4.2 RAPM points YoY is entirely offensive (offensive RAPM -0.71 pooled → -3.20 in 2025-26). **Defensive RAPM has been increasing year-over-year** (-3.19 → -4.56 → -5.19), suggesting his individual ability is intact and likely top-5 league-wide. The decline is system-and-personnel-driven, not physical. Salary $35.0M producing -0.52 surplus at recent year (slightly below tier).

**Randle:** RAPM -0.07 in 2025-26-only (essentially neutral; up from pooled -0.88). Lineup pairings with Edwards (+2.68 RS) and Gobert (+4.57 RS) are positive. Salary $30.9M producing -2.57 surplus (largest negative on roster). The case for trading him rests primarily on salary-efficiency arbitrage, not on his being a clearly negative-impact player.

**Edwards:** Offensive RAPM +3.97 (high-tier; comparable to or higher than SGA, Doncic in the Wolves-only sample). Net RAPM -0.61 is artifact (Wolves-only sample can't separate his impact from team-level offense). His individual game adapted appropriately to the Spurs scheme. Path 1 (Edwards development) is not his bottleneck; the supporting cast around him is.

**McDaniels:** RAPM -0.48 in 2025-26-only (slightly below replacement). Catch-and-shoot accuracy 45.1% on 2.22 attempts per game (high accuracy, low volume). Salary $24.4M producing -1.62 surplus. Locked in through 2028-29 at $108.4M guaranteed. **The internal Category B expansion candidate** (Section 5).

---

## 2. The prescription framework

### 2.1 One primary path

**"Build the personnel context Edwards needs."**

This consolidates what the original Q5 spec framed as Path 1 (Edwards development) and Path 2 (Category B acquisition). The diagnostic work showed these aren't independent. Edwards' development bottleneck isn't his individual skill; it's the supporting cast that converts his kickouts when defenses sell out on him. Path 1 effectively merges into Path 2.

### 2.2 Two supporting elements

**Supporting element 1: System restoration (enabler).** Restore Gobert's PR-Roll-Man volume and Edwards' PR-Ball-Handler share to 2023-24 / 2024-25 levels respectively. Worth 1-2 ORtg points concentrated in the relevant lineups, OR 1-3 RAPM points of Gobert offensive recovery, depending on execution. This is a coaching emphasis prescription, not a roster move.

**Supporting element 2: Conditional Randle disposition.** Trade Randle ONLY if a clear LAFI-Category-B-fitting replacement is available at his salary slot, OR if cap relief enables multiple Category B additions that beat his marginal value in aggregate. Otherwise keep and deploy carefully.

### 2.3 What we are explicitly NOT prescribing

- **NOT trading Gobert.** His positive RAPM, intact defense, and non-guaranteed 2027-28 year (free optionality) make the trade case weak.
- **NOT a roster overhaul.** Edwards is the franchise. The diagnostic shows the supporting cast needs adjustment, not wholesale change.
- **NOT trading for a third superstar (Giannis, Durant, etc.).** See Section 11.
- **NOT betting on Edwards' tier-leap to fix everything.** His offensive RAPM is already high; his development is genuine but not the primary lever.

---

## 3. The primary path: build the personnel context Edwards needs

### 3.1 The Category B gap quantification

DiVincenzo in 2025-26 RS produced 6.05 catch-and-shoot 3PA per game at 38.3% accuracy across 82 games (496 total attempts). This is elite Category B production. The Achilles tear creates a structural gap for 2026-27.

**Internal options (2025-26 RS catch-and-shoot 3PA/game, accuracy):**
- Naz Reid: 4.47/g at 38.1% (but he plays the 5, not the wing)
- McDaniels: 2.22/g at 45.1% (high accuracy, low volume, expandable)
- Conley: 2.00/g at 38.9% (aging, declining)
- Edwards: 2.28/g at 49.6% (primary creator; not a Category B specialist by role)

**The gap:** approximately 3-4 catch-and-shoot 3PA per game of high-accuracy wing production. Internal expansion (mostly McDaniels) closes ~1-2 attempts. External acquisition needs the remaining 2-3.

### 3.2 The Category B archetype target

For external acquisition:

- **Production minimum:** 4+ catch-and-shoot 3PA per game at 37%+ accuracy
- **Movement profile:** Capable of running through screens and relocating, not stationary spot-up only (the Q3 finding showed standstill shooters didn't help when the Spurs collapsed onto Edwards)
- **Closeout-attack ability:** Can drive to floater or kick when run off the line
- **Defensive minimum:** Capable of guarding wings at NBA pace; not a complete sieve
- **Age and contract:** Under 32, on a movable contract or signable at MLE-tier (~$14M)

### 3.3 The secondary creator question

Q3 showed Edwards' individual adaptation to the Spurs scheme was fine; the team's lack of secondary creation was the problem. A secondary creator would help but is harder to acquire than Category B specialists:

- **Production minimum:** PR-Ball-Handler PPP > 0.95 vs blitz/aggressive coverage, 35%+ 3P on 4+ attempts per game, 18-24% usage rate
- **Cost reality:** Secondary creators at this profile typically cost $20M+ AAV
- **Recommended approach:** Opportunistic. Pursue if a clear target emerges at the right cost. Otherwise double down on Category B.

### 3.4 The McDaniels Category B expansion

McDaniels' 45.1% catch-and-shoot accuracy on 2.22 attempts per game is the strongest signal that the Category B gap can be partially closed internally. **Coaching emphasis on getting him 4+ catch-and-shoot 3PA per game would:**

- Partially close the Category B gap internally (saving the external acquisition for a more specific archetype)
- Improve his salary-efficiency picture (currently -1.62 surplus at $24.4M)
- Set up the 2027-28 evaluation cleanly (is he producing his contract value?)
- Reduce the team's external acquisition urgency

**The risk:** Small samples on high-volume catch-and-shoot can regress when volume scales. McDaniels' 45.1% on 162 attempts is not a guaranteed predictor of 45% on 300+ attempts. If his volume scaling produces accuracy regression (say to 37-39% which would still be useful), the gap is partially closed. If it regresses to 33-35%, the internal expansion is less valuable.

**Recommended approach:** test the role expansion in the first 20-30 games of 2026-27. If McDaniels sustains 38%+ on expanded volume, the external Category B acquisition can be smaller. If he doesn't sustain, the external acquisition needs to be larger.

### 3.5 The system restoration prescriptions

**Gobert PR-Roll-Man volume restoration.** From 2025-26's 111 possessions back toward 2023-24's 188. The action is in the playbook; the calling has shifted. Restoring it adds 50-77 high-PPP possessions (1.27 PPP) concentrated in Gobert's minutes. Worth +0.6 to +1.0 ORtg points concentrated.

**Edwards PR-Ball-Handler share restoration.** From 2025-26's 23.5% back toward 2024-25's 33.3%. The shift reduced kickout three opportunities team-wide. Restoring would recover 2-3 catch-and-shoot 3PA per game.

**Implementation note:** This is a coaching emphasis prescription, framed as "system, not the man." The current coaching staff can execute these changes. The political sensitivity of coaching prescriptions argues for the system framing rather than personnel framing.

---

## 4. The conditional Randle disposition

### 4.1 The decision tree

Randle has a player option for 2026-27 at $33.3M. His 2027-28 ($35.8M) is non-guaranteed.

**Branch A: Randle opts in (most likely).** The team controls his contract.

- **A1: Keep, deploy correctly.** Maximize Edwards+Randle (+2.68 RS) and Gobert+Randle (+4.57 RS) minutes. Minimize the Edwards-OFF Randle-ON cohort (which produced approximately neutral marginal value per Q2 2x2 analysis). Accept the salary-vs-production gap as the cost of keeping a complementary piece who fits with the stars.
- **A2: Targeted upgrade trade.** Trade ONLY if a clear LAFI-Category-B-fitting replacement (stretch 4 with movement off-ball + shooting) is available at his salary slot. The bar is high: replacement must be a clear +1.5 to +2.5 RAPM upgrade to justify execution risk.
- **A3: Cap relief trade.** Trade Randle for expiring contracts plus picks. Bets on the 2027 reset being a major asset.

**Branch B: Randle opts out (less likely).** Team has $30.9M cap space.
- Use on Category B + secondary creator combination
- This is the cleanest scenario for executing the primary path

### 4.2 The honest framing

Randle is not the problem. His 2025-26-only RAPM is approximately neutral. His pairings with Edwards and Gobert are positive. **He is expensive for what he provides** but he is not destroying value. The trade case rests on opportunity cost (the $30M slot deployed elsewhere likely produces more), not on him being a bad player.

If the realistic market doesn't produce a clear upgrade or meaningful cap flexibility, the default is Sub-branch A1: keep, deploy correctly, accept the salary-vs-production gap.

---

## 5. The McDaniels question

Per Section 3.4. The internal Category B expansion candidate. His role expansion is the cleanest analytical move available because it doesn't require external acquisition, doesn't require cap flexibility, and tests a specific hypothesis (can his high-accuracy low-volume profile sustain on increased volume).

**Recommended action:**
1. Design 2026-27 opening rotation to give McDaniels 4-5 catch-and-shoot 3PA per game opportunities
2. Track his accuracy through first 20-30 games
3. If he sustains 38%+, the Category B gap is partially closed internally
4. If he regresses, the external acquisition becomes a higher priority
5. The 2027-28 evaluation: is McDaniels producing his $26.2M / $28.0M salary in his expanded role? This becomes the contract justification or trade-consideration question.

McDaniels at age 25-26 is not at his ceiling. The extension priced in expected growth. The expanded role is the test of whether that growth is materializing.

---

## 6. The 2027 reset (the strategic asset)

### 6.1 The contract picture

Three players with major contracts have decision points in summer 2027:
- **Gobert's 2027-28 ($38.0M)** is non-guaranteed
- **Randle's 2027-28 ($35.8M)** is non-guaranteed (if he opts into 2026-27)
- **DiVincenzo** becomes a free agent

If both Gobert and Randle come off the books in summer 2027 (the team waives the non-guaranteed years), the team has approximately $80M of cap room available (current 2027-28 committed is ~$110M including Beringer; expected cap ~$190-200M).

### 6.2 The strategic implications

The 2027 reset is a major strategic asset that the 2026-27 decisions should preserve.

- **Don't sign Category B to long-term deals.** A one-year MLE deal in 2026 preserves 2027 flexibility. If the right player demands a longer deal, weigh that against the reset value.
- **Don't trade picks for short-term help.** The picks are needed for a 2027 trade if the team pursues that path.
- **Plan for the DiVincenzo retention question.** If he proves out in 2026-27, the team has cap room to re-sign him aggressively in summer 2027. If he doesn't recover, the cap room redirects.
- **Plan for the Gobert evaluation.** The 2027-28 non-guaranteed year is the decision point. Based on his 2026-27 performance (does the system restoration recover his offensive RAPM?), the team can extend, waive, or trade.
- **Plan for the Randle decision.** Same framing as Gobert. The 2027-28 non-guaranteed year is the decision point.

### 6.3 The 2027 free-agent or trade pursuit

If the team executes the reset (Gobert and Randle off the books, DiVincenzo a free agent), the ~$80M cap room can be deployed on:

- **Star trade:** Use cap room to absorb a star's salary in trade with a willing seller team (asset cost reduced because no salary matching needed).
- **Multiple free agents:** Re-sign DiVincenzo + add 2-3 Category B / role players + retain partial Gobert salary if his 2026-27 performance warrants.
- **Strategic patience:** Save cap room for 2028 free agency if 2027 market doesn't produce the right opportunity.

The Q9 analysis (deferred) addresses superstar acquisition specifically. The 2027 reset is the realistic path for it if the team pursues that direction.

---

## 7. The Spurs replicability question

OKC has the league's best defensive rating (106.6) and rim protection (60.1% opp rim FG%, league best). Multiple Western Conference teams have similar architectural elements that could partially replicate the Spurs' scheme.

### 7.1 What this means for the prescription

**The Wolves cannot architect their offense assuming favorable matchups.** Personnel additions must be robust to switch-everything-with-rim-protection schemes, not just adequate against generic playoff defenses.

**This sharpens the Category B target.** A standstill spot-up shooter doesn't help against switch-everything (defenses close out hard and run shooters off the line). The Category B target needs:
- Movement off-ball
- Ability to relocate after closeouts
- Closeout-attack ability (drive to floater or kick)
- Not just spot-up shooting from one spot

### 7.2 The time horizon

Building offense robust to this defensive class is a 2-3 year roster construction project, not a one-acquisition fix. The portfolios in Section 9 reflect this.

### 7.3 What we architect for

**Architect for the modal case.** A switch-everything-with-rim-protection scheme is the threat class. Wembanyama is the worst case but isn't the only example. OKC is the most likely 2026-27 Western Conference opponent that can deploy elements of it.

The Wolves face the modal case multiple times per season and once or twice in a playoff run. Architecting for the modal case provides broad protection. Architecting specifically for Wembanyama would overbuild for a matchup that may not recur in critical playoff series.

---

## 8. Cap reality

### 8.1 The cap sheet

From `specs/timberwolves-current-salaries.csv`:

| Player | Age | 2025-26 | 2026-27 | 2027-28 | Guaranteed |
|---|---|---|---|---|---|
| Edwards | 24 | $45.6M | $48.9M | $52.3M | $202M (thru 2028-29) |
| Gobert | 33 | $35.0M | $36.5M | $38.0M (NG) | $71.5M (thru 2026-27) |
| Randle | 31 | $30.9M | $33.3M (PO) | $35.8M (NG) | $64.2M (thru 2026-27) |
| McDaniels | 25 | $24.4M | $26.2M | $28.0M | $108.4M (thru 2028-29) |
| Naz Reid | 26 | $21.6M | $23.3M | $25.0M | $96.6M (thru 2028-29) |
| DiVincenzo | 29 | $12.0M | $12.5M | (FA) | $24.5M |
| Dosunmu | 26 | $7.5M | (FA) | (FA) | $7.5M |

### 8.2 The salary efficiency picture

Per Q8 salary addendum, using 2025-26-only RAPM:

| Player | 2025-26 | Net RAPM 2025-26 | Surplus vs tier |
|---|---|---|---|
| DiVincenzo | $12.0M | +4.84 | **+4.34** |
| Naz Reid | $21.6M | +2.70 | +1.70 |
| Jaylen Clark | $2.2M | +1.45 | +1.45 |
| Gobert | $35.0M | +1.98 | -0.52 |
| Edwards | $45.6M | (artifact) | (true impact higher) |
| McDaniels | $24.4M | -0.48 | -1.62 |
| Randle | $30.9M | -0.07 | **-2.57** |

**Gobert is essentially producing his contract tier in current year terms** (down from pooled +3.68 surplus). The recent decline matters; the keep-Gobert recommendation now rests on his floor being elite defense rather than on him outproducing his contract.

**DiVincenzo is the most underpriced contract on the roster.** Aggressive recovery investment and 2027 re-sign priority are well-supported by the salary-efficiency lens.

**Randle is the largest negative surplus.** The conditional disposition tree in Section 4 reflects the opportunity cost framing.

### 8.3 Cap reality for the recommendations

- **MLE-tier Category B acquisition:** Feasible at $14M. Recommended.
- **Trade Randle for upgrade:** Feasible if right target available. Conditional.
- **Multiple Category B additions:** Requires Randle disposition or 2027 reset to free cap room.
- **Star trade:** 2027 reset is the realistic path (Section 6).

---

## 9. The three portfolios

### Portfolio A: "Build the supporting cast" (DEFAULT RECOMMENDATION)

**Personnel:**
- Acquire one Category B wing at MLE tier (4+ catch-and-shoot 3PA/g at 37%+ with movement off-ball; defensive minimum)
- Expand McDaniels' Category B role (test 4-5 cs_3PA/g in first 20-30 games)

**System:**
- Coaching emphasis on restoring Edwards' PR-Ball-Handler usage from 2024-25 levels
- Coaching emphasis on restoring Gobert's PR-Roll-Man volume
- Estimated impact: +1 to +2 ORtg concentrated in relevant lineups

**Player decisions:**
- Keep Gobert through 2026-27; reassess 2027-28 based on 2026-27 performance
- Keep Randle; deploy correctly; reassess at trade deadline
- Protect DiVincenzo recovery; plan for 2027 re-sign if proves out

**2027 plan:**
- Preserve flexibility
- 2027 reset is the medium-term major-move asset

**Expected impact:** +2 to +4 ORtg points cumulative. Championship probability change: +2 to +4 percentage points from current ~4-8%.

**Cost:** MLE-tier signing (~$14M annual), preserves picks, preserves cap flexibility.

**Risk:** Execution risk on Category B acquisition (right archetype may not be available at MLE).

### Portfolio B: "Targeted upgrade"

**Differs from A:** Trade Randle for either a Category B-fitting stretch four at his salary slot, OR for two players that beat his marginal value in aggregate.

**Same as A:** System restoration, Gobert keep, DiVincenzo recovery, McDaniels role expansion.

**Expected impact:** +3 to +6 ORtg points cumulative if execution lands. Championship probability change: +5 to +10 percentage points.

**Cost:** Trade execution; possible asset outlay; risk of acquiring worse player.

**Risk:** Execution. Randle market may not produce clear upgrade. Trade can move team backward if return doesn't fit.

### Portfolio C: "Preserve 2027 flexibility"

**Personnel:**
- Sign Category B at MLE on a 1-year deal (preserves 2027 cap room)
- Do not pursue trades unless clearly value-additive

**Player decisions:**
- Same as A (keep Gobert, keep Randle, protect DiVincenzo)
- Plan to potentially waive Gobert 2027-28 if his performance declines further

**2027 plan:**
- Major free-agent or trade pursuit using ~$80M cap room
- Re-sign DiVincenzo aggressively if proves out
- Possibly pursue superstar trade if right opportunity (Q9 analysis)

**Expected impact:** 2026-27 +1 to +3 ORtg (similar to A but more conservative). 2027-28 step-change potential if reset executes well.

**Cost:** Minimal 2026-27. Opportunity cost of not improving more aggressively in immediate window.

**Risk:** Edwards-development window may be closing if team isn't competitive in 2026-27. The 2027 reset is real only if executed; bad 2027 decisions undo the strategic asset.

### Portfolio comparison

| Dimension | A (default) | B (upside) | C (patient) |
|---|---|---|---|
| 2026-27 ORtg gain | +2 to +4 | +3 to +6 | +1 to +3 |
| Championship prob change | +2-4 pp | +5-10 pp | +1-3 pp 2026-27, higher 2027-28 |
| Asset cost | Low (MLE) | Medium (trade) | Very low |
| Execution risk | Low | Medium-High | Low |
| 2027 flexibility | Preserved | Mostly preserved | Maximized |
| Coverage of diagnostic | Good | Good | Modest |

**Recommendation:** Portfolio A as default. Portfolio B if a clear Randle trade target emerges in summer 2026 or at the trade deadline. Portfolio C if the front office prioritizes 2027 reset over 2026-27 competitiveness.

### Alternative portfolios (preserved as v1)

Portfolios D (internal-plus-targeted), E (reset around Edwards / trade Gobert), and F (all-in star trade) from the v1 Q5 spec are preserved as alternatives. Current diagnostic evidence weakens each:

- **D:** approximately Portfolio A with less Category B emphasis. The diagnostic supports A's emphasis.
- **E:** Trading Gobert forfeits the team's clearest positive RAPM contributor. Weakly supported.
- **F:** Star trade asset cost likely exceeds expected value. The Q3 finding (Edwards' shooting was fine vs the Spurs) doesn't suggest a "we need another star" diagnosis.

---

## 10. The supporting cast quantification

What specifically does the team need to acquire?

### 10.1 The catch-and-shoot 3PA target

The team's 2025-26 team-level catch-and-shoot 3PA total (estimated from per-player tracking) was approximately 15-17 attempts per game from non-Edwards perimeter players (DiVincenzo 6.05, Naz 4.47, McDaniels 2.22, Conley 2.00, plus bench).

Without DiVincenzo in 2026-27, the internal team-level base is ~8-11 catch-and-shoot 3PA per game from non-Edwards perimeter players. **The team needs to restore to roughly 15-17 attempts per game total**, requiring:
- McDaniels expansion: +2 attempts (from 2.2 to 4+)
- External Category B addition: +4 attempts
- Cumulative non-Edwards catch-and-shoot 3PA: ~14-17 attempts per game, restoring approximately the 2024-25 / 2025-26 RS baseline

### 10.2 The accuracy target

The team needs the non-Edwards catch-and-shoot threes to convert at 37%+ team-wide. DiVincenzo was at 38.3%, McDaniels at 45.1%. If the external Category B is at 37-38%, the team-wide accuracy holds at the 2024-25 / 2025-26 RS level.

### 10.3 The defensive minimum

Wing additions need to defend at NBA pace without being a complete liability. They will share defensive minutes with McDaniels (the team's best perimeter defender), so the new piece doesn't need to be elite defensively, just adequate.

---

## 11. Why we don't recommend trading for Giannis Antetokounmpo or Kevin Durant

This section exists because Wolves fans, media, and likely the front office will ask the question. The diagnostic findings produce a specific answer.

### 11.1 The diagnostic doesn't point at superstar acquisition

The Wolves' 2025-26 playoff issues weren't about Edwards' ceiling or about needing a third superstar to share the load. The issues were:
- DiVincenzo's Achilles tear (the team's actual highest-impact player by 2025-26 RAPM)
- The Spurs' specific scheme that channeled Edwards into a low-EV shot diet
- The team's lack of secondary off-ball creation when Edwards was contained

Adding a third superstar to the roster doesn't address these specific gaps. A Giannis or Durant addition would change the team's identity, raise its ceiling under some scenarios, but wouldn't directly solve the Q3 problem (the team needed catch-and-shoot threats around Edwards, not another iso creator).

### 11.2 The trade math

A realistic Giannis trade likely costs Edwards plus most of the rotation plus significant draft capital. The team gets Giannis but loses Edwards (the better player by age curve, contract value, and offensive RAPM) and most of the supporting cast. The post-trade roster's net rating may not improve.

A realistic Durant trade is less drastic (Durant is older, his trade value is lower) but still requires significant outflow.

**The path Wolves fans want is "add Giannis or Durant without losing Edwards." That path doesn't exist.** Other teams have no incentive to make those trades.

### 11.3 The 2027 reset path

If the team wanted to pursue a superstar acquisition realistically, the 2027 reset (Section 6) is the realistic path. By 2027:
- The Wolves have ~$80M cap room potentially available
- Multiple stars may become available (contract expirations, retirement-adjacent restructuring)
- Edwards is more developed and can fit alongside another star

But by 2027, Giannis and Durant are both older. Giannis would be 32; Durant would be 38. Their production years remaining are reduced. The pursuit may be aimed at a different star by then.

### 11.4 The honest framing

The Wolves don't need a third superstar. They need the supporting cast that converts Edwards' creation. The Q5 recommendation is built on that diagnosis. The Giannis/Durant question is the inevitable counter, addressed here for completeness rather than as the recommended path.

**The deferred Q9 analysis (master plan v3, post-Q5) will engage with the superstar acquisition question more deeply** if the front office wants to revisit it after considering Q5's recommendations.

---

## 12. Open questions and what we didn't do

### 12.1 What this deliverable doesn't quantify

- **Defender distance / shot quality expected eFG model.** Q3 deferred this; the v1 finding (Spurs scheme on Edwards) was robust enough without it.
- **Action classifier outputs.** Q3 used proxy metrics rather than per-possession coverage classification. Manual coding the 2025-26 playoff sample (~600 PnRs over 11 games) would sharpen the coverage decoder; estimated 20-30 hours.
- **Full league-wide RAPM.** The Wolves-only RAPM has known limitations (Edwards' net RAPM is artifact; opponent benchmarks noisy). Full league-wide build would resolve.
- **Defensive-anchor center age curve for Gobert.** The keep-Gobert recommendation rests partly on his 2026-27 and 2027-28 trajectory. A comp-set age curve would tighten the projection.
- **Achilles recovery comp set for DiVincenzo.** General medical literature bands used in Section 5. A specific NBA-guards comp set would tighten the recovery probability bands.
- **Spotrac-based realistic trade market.** Concrete trade scenarios for Randle and hypothetical Category B targets. The recommendation framing references availability but doesn't specify deal mechanics.

### 12.2 The deferred Q9 (superstar acquisition)

Added to the master plan as a post-Q5 deferred analysis. Will engage with the Giannis/Durant question with quantified trade math.

### 12.3 The 2024-25 PO data

The yoy lineup comparison showed the 2024-25 PO Gobert+Randle pairing was -4.00 over 252 minutes. Wider CI but directionally negative. The 2025-26 PO -13.26 is consistent with a "playoffs are harder for this pairing" pattern, with the Spurs-specific being the extreme version. Worth deeper investigation in a future analysis.

---

## 13. Names appendix (illustrative; will be stale)

These names are illustrative as of the project's knowledge cutoff (January 2026). Actual 2026 free-agent and trade markets will differ. **Use the archetype thresholds in Sections 3.2 and 3.3 as the acquisition criteria. The names below are examples of player types to look for, not specific recommendations.**

### 13.1 Category B wing targets (MLE tier or trade)

**Tier 1 (Realistic at MLE or via modest trade):**
- Luke Kennard (veteran specialist, 40%+ career 3P, movement off-ball)
- Sam Hauser (CEL: high-volume cs threat, defensive minimum is the question)
- Gary Trent Jr. (career 38%+ 3P on volume, defensive utility)
- Cam Johnson (BKN: 39%+ 3P on volume, defensive size, may require trade)
- Buddy Hield (high-volume veteran shooter, age concerns)
- Royce O'Neale (39%+ 3P, defensive switchability)

**Tier 2 (Stretch via larger trade investment):**
- Bogdan Bogdanovic (LAC: shooting + secondary creation)
- Norman Powell (LAC: 40%+ 3P, scoring volume)
- Klay Thompson (DAL: aging but elite C&S DNA; complicated fit)
- Malik Beasley (high-volume 3P specialist; defensive concerns)

**Tier 3 (Longer-shot or aspirational):**
- Desmond Bane (MEM: 41%+ 3P, secondary creation, high cost)
- Tyler Herro (MIA: 40%+ 3P, on-ball creation, high cost)
- Klay-tier shooter on a market correction

### 13.2 Stretch-four targets (for Portfolio B Randle upgrade)

**Tier 1:**
- John Collins (UTA: stretch 4, 37%+ 3P, defensive limitations)
- Tobias Harris (DET veteran, mid-tier production)
- Naji Marshall (DAL: stretch wing with switchability)

**Tier 2:**
- Lauri Markkanen (UTA: elite stretch 4 but higher salary; may not fit)
- Cam Johnson (also category B; some fit as 4 in small-ball)

**Tier 3:**
- Brandon Ingram (TOR: scoring stretch wing but cost is high)
- Pascal Siakam (IND: too expensive but the archetype fit)

### 13.3 Secondary creator targets (opportunistic only)

**Tier 1:**
- Tyus Jones (career PR-Ball-Handler PPP, low-mistake)
- Malik Monk (SAC: 35%+ 3P, secondary scoring)
- Coby White (CHI: scoring guard, age curve favorable)

**Tier 2:**
- D'Angelo Russell (volume + 3P, defensive concerns)
- Spencer Dinwiddie (veteran secondary creator, free agent)
- Russell Westbrook (no longer fits but illustrative of veteran secondary)

**Tier 3:**
- Trade target: a sub-star creator at $15-20M who fits

### 13.4 The honest caveat on names

These names are educated guesses based on production through January 2026 plus knowledge of contract structures. Real acquisitions in summer 2026 will depend on:
- Each player's then-current production trajectory
- Each player's contract status and expectations
- Each team's willingness to move them
- The Wolves' actual cap room and assets at the time

**The point of the names list is illustration, not recommendation.** The archetype thresholds are what the team should pursue.

---

## 14. The honest framing

None of this is guaranteed to produce a championship. The Wolves are competing in a deep Western Conference with multiple teams that have defensive architectures capable of giving Edwards-led offenses trouble. The prescription is "give Edwards the supporting cast that makes him hardest to scheme against" rather than "do X and you'll win it all."

The recommendation portfolios A, B, and C all assume:
- DiVincenzo's Achilles recovery falls within the median to best-case bands (Section 1 of Q8 v1)
- The targeted system restorations are executed (coaching emphasis on PR-Ball-Handler and PR-Roll-Man)
- The Category B acquisition lands within the archetype's quality range

If any of these assumptions fail, the expected impacts narrow. The honest probability ranges in Section 9 reflect this.

**The structural takeaway:** the Wolves' 2025-26 problems weren't catastrophic. Three positive-impact individual contributors (Gobert, DiVincenzo, Edwards) ran into a specific structural mismatch against a specific opponent at the same time as the team's #1 impact player was lost to injury. The fixes are personnel-and-coaching adjustments, not roster overhaul. The 2027 reset is a real strategic asset if the team executes intermediate decisions well.

**Edwards is fine.** Gobert is fine. Randle is approximately neutral. DiVincenzo is the question. The team's job is to build the supporting cast that lets Edwards' creation produce points when defenses scheme against him.

---

## 15. Status and next steps

Q5 v1 draft complete. The prescription framework is consolidated, the supporting-cast quantification is grounded in specific catch-and-shoot targets, the player decisions are framed at appropriate uncertainty, and the 2027 reset is incorporated as a strategic asset.

### Build status of project analyses

| Analysis | Status |
|---|---|
| Q0A LAFI v1 | Complete |
| Q1 Diagnose the Break | Complete (v1 + dropoff CI) |
| Q2 Localize the Damage | Complete (v1 + corrections + yoy lineup comparison) |
| Q3 Mechanism analysis | Complete (v1, action-classifier-free) |
| Q0D Coaching System | Complete (v1) |
| Q8 Player Decisions | Complete (v1 + salary addendum + weighted-recent RAPM) |
| Q5 Prescription | **Complete (v1, this document)** |
| Q4 Archetype Stress Test | Pending (could sharpen Q5; not blocking) |
| Q6 KAT Counterfactual | Pending (would address "what if KAT stayed" framing) |
| Q7 Star Comp Analysis | Pending (would feed Q5 with star-comp evidence) |
| Q0B Trajectory and Windows | Pending |
| Q0C Historical Cohort | Pending |
| Q9 Superstar Acquisition | Pending (deferred to post-Q5; Giannis / Durant trade-math analysis) |

### Recommended next steps

1. **Engage with this Q5 v1.** The framework is consolidated. Specific findings or recommendations may need refinement based on your read.
2. **Build Q9** (Giannis/Durant superstar acquisition analysis) per master plan v3 addition.
3. **Optional follow-ons:** Q4 archetype clustering (sharpens the Spurs-replicability question), Q6 KAT counterfactual (provides "what if we hadn't traded KAT" framing), Q7 star comparable (provides Edwards' tier-leap probability via historical comps).
4. **Optional infrastructure follow-ons:** full league-wide RAPM (resolves Edwards artifact), Spotrac cap integration (sharpens trade math), action classifier (sharpens Q3 coverage decoder).

The Q5 v1 is the project's culminating prescriptive document. The diagnostic work the project has produced is referenced in every recommendation. The remaining work refines and rounds out but does not change the central prescription.

### Artifacts

```
specs/
  q5_prescription_spec_v2.md          revised spec (this document built from)

outputs/findings/q5_prescription/
  01_q5_v1_deliverable.md             this document

References:
  outputs/findings/q0a_lafi/11_wolves_lafi_deliverable.md
  outputs/findings/q1_diagnose/01_q1_findings.md
  outputs/findings/q2_localize/01_q2_findings.md (+ corrections + yoy + 04_gobert_career_arc)
  outputs/findings/q3_mechanism/01_q3_v1_findings.md
  outputs/findings/q0d_coaching_system/01_q0d_v1_findings.md
  outputs/findings/q8_player_decisions/01_q8_v1_findings.md (+ addendum + weighted-recent)
  outputs/tables/q2_localize/*.csv
  outputs/tables/q3_mechanism/*.csv
  outputs/tables/q8_player_decisions/*.csv
  outputs/charts/q8_player_decisions/gobert_career_arc.png
```

---

End of Q5 v1.
