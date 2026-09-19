# Q5: Prescription Specification (v2, post-diagnostic-completion)

> **EXPOSED, NOT YET RECOMPUTED (D88).** This spec leans on Gobert's RAPM (+6.18 pooled, +1.98 in 2025-26) and on Q2 lineup figures. The stint layer those lineup figures come from was fixed on 2026-09-18 and recomputed (playoff figures move by up to 17 points per 100, five change sign); the RAPM fit has since been refit on the corrected possession grain (D89), so the Gobert RAPM figures quoted in this spec are superseded by `postmortem/outputs/findings/lineup_pipeline/04_d89_rapm_refit_and_article_claims.md`. See `postmortem/outputs/findings/lineup_pipeline/03_d88_points_fix_and_recompute.md` before treating any of those numbers as settled.

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q5
**Status:** Specification v2, revised 2026-05-18 after the diagnostic work completed.
**Position in stack:** Culminating prescriptive analysis. The deliverable the project has been building toward.

**Revision note (v2):** The original Q5 spec (v1, dated 2026-05-17) was written immediately after LAFI v1 with the three-paths framework as the spine. Six analytical rounds since then (Q1 four factors, Q2 lineup work + corrections, Q3 Spurs decoder, Q0D coaching system, Q8 player decisions + salary addendum + weighted-recent RAPM, Gobert career arc) have refined the diagnosis and revealed that the three paths are not independent. This v2 spec restructures the prescription framework to match what the diagnostic work has actually surfaced.

**v1 is preserved as historical artifact at `specs/q5_prescription_spec.md`.** This v2 spec supersedes it.

---

## 1. The thesis (refined)

### 1.1 The question

Given the now-complete diagnostic work, what specific archetypes of roster moves, system changes, and player-development investments would most plausibly improve the Wolves' championship odds, and what is the calibrated expected magnitude of each?

### 1.2 What the diagnostic work established

The project's findings converge on a coherent story:

**The mechanism (Q1, Q2, Q3):** The 2025-26 playoff offensive collapse was Spurs-specific, not generic. The Spurs' Wembanyama-anchored switch-everything-with-rim-protection scheme channeled Edwards into the 11-16 ft floater zone, suppressed his catch-and-shoot opportunities (6.2% of his shots vs SAS, vs 13.8% in RS), and dropped his 3PA volume by 37%. Edwards adapted individually (his FG% on the shorter diet was 46.9%). The team's secondary creation couldn't convert his kickouts. The 3PA collapse the Q1 team-level analysis identified was substantially Edwards' suppressed 3PA volume specifically.

**The architectural context (LAFI v1, Q0D):** The Wolves' 2025-26 offense is Q4 distributed pickup by LAFI classification (off-ball motion held flat at 10-11% across all five Edwards-era seasons; iso rose to 9.6%; PR-Ball-Handler dropped to 13.1%). But the allocation shift's impact on team ORtg is small: restoring 2023-24 allocation with current personnel would gain only +0.35 ORtg points per 100 possessions (Q0D finding). The "stale system" framing is partially supported but the impact ceiling from system-only changes is well below the spec's +2-point threshold.

**The player-level picture (Q8 + RAPM):**
- **DiVincenzo** was the team's highest-impact player by 2025-26-only RAPM (+4.84, rank #1 in the 404-player sample). His Achilles tear is the largest negative shock the roster has absorbed.
- **Gobert** was the team's #1 RAPM in the 3-year pooled sample (+6.18) and dropped to +1.98 in 2025-26-only RAPM. The decline is entirely offensive; defensive RAPM is intact and likely top-5 league-wide. The decline is plausibly system-and-personnel-driven (KAT departure removed offensive gravity; his PR-Roll-Man volume dropped 41% YoY per Q0D), not physical.
- **Randle** is approximately neutral by RAPM (-0.07 in 2025-26-only) but significantly underpriced relative to his $30.9M tier (-3.38 surplus vs implied threshold). The case for moving him rests on salary-efficiency arbitrage, not on him being a clearly negative-impact player.
- **Edwards** is the franchise. His offensive RAPM is +3.97 (high-tier); his net RAPM is artifact of the Wolves-only sample. His individual game adapted appropriately to the Spurs' scheme.

**The replicability question (Q3):** The Spurs' scheme is partially replicable. OKC has the architecture (Holmgren-anchored rim protection + closeout discipline; #1 defensive rating in 2025-26 at 106.6). Multiple Western Conference teams have similar elements. The Wolves should expect to face Spurs-like defensive looks in future playoff series, not just from SAS.

### 1.3 What this changes about the prescription framework

The v1 spec's three independent paths (Edwards development, Category B acquisition, system change) are not independent in the way the original framing suggested:

- **Path 1 (Edwards development)** has its bottleneck NOT in Edwards' individual skill development but in the personnel around him. Edwards adapted to the Spurs scheme by driving more and converting at decent rates; the team's problem was no secondary creation to convert his kickouts. Path 1's main lever is Path 2's personnel work.

- **Path 3 (system restoration)** has a small ceiling (+0.35 ORtg from allocation restoration per Q0D). It's not a load-bearing path on its own. Its role is to enable the personnel work to operate effectively (e.g., restoring Gobert's PR-Roll-Man volume is plausibly +1-2 ORtg points concentrated in his minutes, but this is a targeted role restoration rather than broad system overhaul).

- **Path 4 (frontcourt restructuring)** is mostly off the table per Q8. Gobert's RAPM (even after the 2025-26 decline) is positive and his defensive value is intact. Randle's case is closer to "use correctly or pursue conditional upgrade" than to "trade him."

**The revised framework collapses to one primary path with two supporting elements:**

- **Primary path: "Build the personnel context Edwards needs."** This merges old Paths 1 and 2. The recommendation is to invest in shooters and secondary creators around Edwards such that his kickouts convert, the offense has answers against schemes that channel him to specific zones, and the team's Q4 architecture is supplemented by Category B threats.

- **Supporting element 1: System restoration as enabler.** Restoring designed actions (Gobert PR-Roll-Man volume, Edwards PR-Ball-Handler share from 2024-25 levels) enables the personnel additions to operate at their potential. Worth 1-2 ORtg points if executed concurrently with personnel additions. Worth +0.35 ORtg points alone.

- **Supporting element 2: Conditional Randle disposition.** Trade Randle ONLY if a clear LAFI-Category-B-friendly replacement is available at his salary slot OR if the cap relief can be redeployed on multiple Category B / supporting cast additions that beat his marginal value in aggregate.

### 1.4 The principles (preserved from v1)

- **Honest about cost.** Every recommendation has a price (cap dollars, picks, players). Engage with cost.
- **Honest about availability.** Distinguish "easy archetype to acquire" from "extremely scarce archetype."
- **Probabilistic, not deterministic.** No move is guaranteed.
- **First principles, not pattern matching.** The Wolves' situation is rare. Forced historical analogies are worse than acknowledging thin evidence.
- **Archetypes before names.** Production thresholds first. Names go in appendices.

---

## 2. The revised prescription framework

### 2.1 The primary path: "Build the personnel context Edwards needs"

The primary path consolidates v1's Paths 1 and 2 into one prescription: acquire and retain the supporting cast that makes Edwards' creation productive against modern defensive schemes.

#### The Category B gap quantification

The 2025-26 RS DiVincenzo gap (with him healthy and producing 6.05 catch-and-shoot 3PA/game at 38.3% across 82 games) is the specific Category B benchmark. Without him in 2026-27:

- **Internal options (cap-and-shoot 3PA/game in 2025-26 RS, % accuracy):**
  - Naz Reid: 4.47/g at 38.1% (but he plays the 5, not the wing)
  - McDaniels: 2.22/g at 45.1% (high accuracy, low volume; could expand role)
  - Conley: 2.00/g at 38.9% (aging, declining)
  - Edwards: 2.28/g at 49.6% (primary creator, can't be a Category B specialist)

- **The gap:** approximately 3-4 catch-and-shoot 3PA per game of high-accuracy wing production. Internal expansion (mostly McDaniels) could close ~1-2 of those attempts. The remainder requires external acquisition.

- **The archetype target:**
  - Catch-and-shoot 3PA: 4+ per game at 37%+ accuracy
  - Defensive minimum: capable of guarding wings at NBA pace; not a sieve
  - Movement off-ball: capable of running through screens and relocating; not stationary spot-up only (because the Q3 finding showed standstill shooters didn't help when the Spurs collapsed onto Edwards)
  - Age and contract: under 32, on a movable contract or signable at MLE-tier (~$14M)
  - **Q5 should produce a names appendix of plausible Category B targets for the 2026 offseason at the MLE tier and via trade.**

#### The secondary creator question

Q3 showed Edwards' individual adaptation to the Spurs scheme was fine; the problem was the team's lack of secondary creation. A secondary creator who can punish defensive sell-out on Edwards is one approach. But this archetype is harder to acquire than Category B specialists:

- **Archetype target:**
  - PR-Ball-Handler PPP > 0.95 vs blitz/aggressive coverage
  - On-ball usage rate 18-24%
  - Three-point shooting 35%+ on 4+ attempts per game
  - Defensive minimum: not a complete sieve
  - Age and contract: under 32, on a movable contract

- **Cost reality:** Secondary creators at this profile typically cost $20-25M+ AAV or significant draft capital. The Wolves' cap and asset realities (Section 4) make this archetype hard to acquire outright.

- **Recommended approach:** Treat secondary creator acquisition as opportunistic. If a clear target emerges at the right cost, pursue. If not, double down on Category B which is easier to acquire and addresses the same diagnostic gap (giving Edwards options to pass to).

### 2.2 Supporting element 1: System restoration

Q0D's finding: broad allocation restoration is small impact (+0.35 ORtg). But targeted role restorations are higher-leverage:

- **Restore Gobert's PR-Roll-Man volume.** His 2025-26 volume was 111 possessions; 2023-24 was 188. Adding 50-77 possessions at his 1.27 PPP = +0.6 to +1.0 ORtg points concentrated in his minutes. Higher-leverage than broad allocation change.

- **Restore Edwards' PR-Ball-Handler usage.** His 2024-25 RS rate was 33.3%; 2025-26 RS was 23.5%. The 10-percentage-point shift toward iso reduced his three-point generation specifically. Restoring the 2024-25 mix could recover 2-3 catch-and-shoot 3PA per game team-wide.

- **Cumulative system restoration estimate:** 1-2 ORtg points concentrated in the relevant lineups, OR 1-3 RAPM points of Gobert offensive recovery, depending on execution.

- **Implementation:** This is a coaching prescription. Q5 should explicitly address this with appropriate political care (the Q0D spec's "this is about the system, not the man" principle applies).

### 2.3 Supporting element 2: Conditional Randle disposition

Per Q8 + salary addendum:
- Randle's RAPM is -0.07 in 2025-26-only (approximately neutral)
- His $30.9M salary produces -2.57 surplus vs the implied tier threshold
- He has a player option for 2026-27 at $33.3M
- His lineup pairings with Edwards (+2.68) and Gobert (+4.57) are positive

Decision tree:
- **If Randle opts in (most likely):**
  - **Sub-branch A1: Keep, deploy correctly.** Maximize Edwards+Randle and Gobert+Randle minutes; minimize Edwards-OFF Randle-ON cohort. Accept salary-vs-production gap.
  - **Sub-branch A2: Targeted upgrade trade.** Trade Randle ONLY if a clear LAFI-Category-B-fitting replacement is available at his salary slot. The bar is high: replacement must be a clear +1.5 to +2.5 RAPM upgrade to justify execution risk.
  - **Sub-branch A3: Cap relief trade.** Trade Randle for expiring contracts plus picks to preserve 2027 flexibility. Bets on the 2027 reset (Section 4) being a major asset.

- **If Randle opts out (less likely):**
  - Team has $30.9M cap space freed
  - Use on Category B + secondary creator combination
  - This is the cleanest scenario for executing the primary path

### 2.4 What we are NOT prescribing (v2 explicit non-prescriptions)

- **NOT prescribing: trade Gobert.** His RAPM is positive, his defense is intact, his 2027-28 year is non-guaranteed (free optionality). The case for moving him is weak.

- **NOT prescribing: blow up the roster.** Edwards is the franchise. The diagnostic shows the supporting cast around him needs adjustment, not roster overhaul.

- **NOT prescribing: bet on Edwards' tier-leap to fix everything.** Edwards' offensive RAPM is already high (+3.97). His development is genuine but not the primary lever. The personnel around him is.

---

## 3. The cap reality (now grounded in actual numbers)

### 3.1 The contract picture

From `specs/timberwolves-current-salaries.csv`:

| Player | 2025-26 | 2026-27 | 2027-28 | Guaranteed |
|---|---|---|---|---|
| Edwards | $45.6M | $48.9M | $52.3M | $202.4M (through 2028-29) |
| Gobert | $35.0M | $36.5M | $38.0M (NG) | $71.5M (through 2026-27) |
| Randle | $30.9M | $33.3M (PO) | $35.8M (NG) | $64.2M (through 2026-27) |
| McDaniels | $24.4M | $26.2M | $28.0M | $108.4M (through 2028-29) |
| Naz Reid | $21.6M | $23.3M | $25.0M | $96.6M (through 2028-29) |
| DiVincenzo | $12.0M | $12.5M | (FA) | $24.5M |
| Dosunmu | $7.5M | (FA) | (FA) | $7.5M |

(NG = non-guaranteed; PO = player option; FA = free agent)

### 3.2 The 2027 reset (the strategic asset)

Three players with significant contracts have decision points in summer 2027:
- **Gobert's 2027-28 ($38M)** is non-guaranteed. Team can waive or extend.
- **Randle's 2027-28 ($35.8M)** is non-guaranteed (if he opts into 2026-27). Same optionality.
- **DiVincenzo** becomes a free agent.

If both Gobert and Randle come off the books in summer 2027, the team has approximately $80M of cap room (current 2027-28 committed is ~$110M including rookie-scale Beringer; cap is expected around $190-200M). This is a major strategic asset.

**Q5 must frame the 2026-27 decisions in terms of preserving 2027 flexibility.** The DiVincenzo retention question, the Gobert extension question, the Category B acquisition contract length all interact with the 2027 reset.

### 3.3 The salary efficiency picture

Per Q8 addendum, the salary-efficiency surplus values (using 2025-26-only RAPM where applicable):

| Player | Surplus vs tier threshold |
|---|---|
| DiVincenzo | +4.34 (massive underpay, even before injury context) |
| Naz Reid | +1.70 (underpriced) |
| Jaylen Clark | +1.45 (best value-per-$ on roster) |
| Gobert | -0.52 (slightly below tier in recent year) |
| Edwards | (artifact, real impact higher) |
| McDaniels | -1.62 (clear underproduction) |
| Randle | -2.57 (largest negative; concentrated trade target) |

**The McDaniels question:** McDaniels is locked in through 2028-29 at $108M guaranteed. His RAPM at -0.62 produces a clear surplus gap. Q5 must engage with this question rather than ignore it. Possibilities:

1. **McDaniels' defensive value is real but under-measured by RAPM.** His individual defensive metrics (DBPM, opponent FG% as primary defender, switchability) might justify the salary even if RAPM doesn't reflect it.
2. **McDaniels has development upside.** At age 25 (turning 26 in 2026-27), he's not at his ceiling. The extension priced in his expected growth.
3. **McDaniels is overpaid and the team has to live with it.** No realistic trade market exists for his contract at the production level. The team's flexibility is constrained.

Q5 should investigate which of these is most supported and frame the McDaniels role accordingly (expanded Category B role? Role-player who anchors defense? Trade candidate if his trade value is preserved?).

---

## 4. The Spurs-replicability strategic question

Per Q3: OKC has architecture similar enough to the Spurs' to replicate elements of the scheme. The Wolves face this defensive style not just from SAS but potentially from multiple Western Conference opponents.

Implications for Q5:

- **The Wolves cannot architect their offense assuming favorable matchups.** The personnel additions must be robust to switch-everything-with-rim-protection schemes, not just adequate against generic playoff defenses.

- **This sharpens the Category B target.** A standstill spot-up shooter doesn't help against the Spurs' scheme (the Spurs close out hard and run shooters off the line). The Category B target needs movement off-ball, ability to relocate, and ideally some closeout-attack ability (drive to floater or kick).

- **This frames the time horizon.** Building offense robust to this defensive class is a 2-3 year roster construction project, not a one-acquisition fix. Q5's portfolio framing should reflect this.

---

## 5. The revised portfolio framework

Three portfolios, derived from the revised prescription framework:

### Portfolio A: "Build the supporting cast" (primary)

The data-conservative path that operationalizes the primary prescription.

- **Personnel:** Acquire one Category B wing at MLE tier (4+ catch-and-shoot 3PA/g at 37%+ with movement off-ball; defensive minimum). If the right Category B is unavailable at MLE, use trade exception or part of mid-tier exception.
- **System:** Coaching emphasis on restoring Edwards' PR-Ball-Handler usage and Gobert's PR-Roll-Man volume. Worth 1-2 ORtg points incremental.
- **Randle disposition:** Keep, manage rotations to maximize Edwards+Randle and Gobert+Randle minutes. Reassess at trade deadline.
- **Gobert disposition:** Keep through 2026-27. Reassess 2027-28 non-guaranteed year based on his 2026-27 performance.
- **DiVincenzo plan:** Protect the recovery. Re-sign aggressively in summer 2027 if he proves out at any meaningful level.
- **2027 plan:** Preserve flexibility. The 2027 reset is the medium-term asset.

**Estimated impact:** +2 to +4 ORtg points cumulative (1-2 from system, 1-2 from Category B addition). Championship probability change: +2 to +4 percentage points from current ~4-8%.

**Cost:** MLE-tier signing ($14M-ish), modest trade asset for Category B if needed (perhaps a future second-round pick + minimum salary).

**Risk:** Execution risk on Category B acquisition (the right archetype may not be available at MLE).

### Portfolio B: "Targeted upgrade" (data-targeted)

The scenario where Randle is moved for a clear upgrade. Higher upside, higher execution risk.

- **Personnel:** Trade Randle for either (a) a Category B-fitting stretch four who shoots 37%+ on 5+ catch-and-shoot 3PA at his salary slot, or (b) two players that beat his marginal value in aggregate (Category B wing + secondary creator).
- **System:** Same as Portfolio A.
- **Gobert disposition:** Keep through 2026-27.
- **DiVincenzo plan:** Same as Portfolio A.
- **2027 plan:** Same as Portfolio A.

**Estimated impact:** +3 to +6 ORtg points cumulative if execution lands. Championship probability change: +5 to +10 percentage points.

**Cost:** Trade execution; risk of acquiring a worse player than expected.

**Risk:** Execution risk on Randle trade (his market value may not produce a clear upgrade). Risk of moving a complementary piece for a less-fitting alternative.

### Portfolio C: "Preserve 2027 flexibility" (data-conservative-plus-patience)

The patient path that minimizes 2026-27 moves to maximize 2027-28 cap room.

- **Personnel:** Sign Category B at MLE tier (1-year deal if possible). Do not pursue trades unless clearly value-additive.
- **System:** Same as Portfolios A and B.
- **Gobert disposition:** Keep. Plan to potentially exercise the 2027-28 non-guaranteed waiver if his performance declines further.
- **Randle disposition:** Keep through 2026-27 unless opt-out happens; if opt-out, use cap on multiple Category B additions.
- **DiVincenzo plan:** Protect recovery; re-sign in summer 2027 if available.
- **2027 plan:** Major free-agent or trade pursuit. Use ~$80M of potential 2027 cap room on top-tier addition.

**Estimated impact 2026-27:** +1 to +3 ORtg points (similar to A but more conservative). 2027-28 impact: substantial if the 2027 reset is well-executed.

**Cost:** Minimal in 2026-27. The cost is opportunity cost of not improving more aggressively in the immediate window.

**Risk:** Edwards-development window may be closing if the team isn't competitive in 2026-27. The 2027 reset is real only if the team executes on it; bad 2027 free-agent decisions undo the strategic asset.

### Portfolios D, E, F (preserved as alternatives, weakened by current evidence)

The v1 alternative portfolios (D: internal-plus-targeted; E: reset-and-rebuild-around-Edwards; F: all-in) are preserved as alternatives but are now weakly supported:

- **D (internal-plus-targeted):** Approximately Portfolio A with less Category B emphasis. The diagnostic work suggests A is preferable.
- **E (reset around Edwards / trade Gobert):** Q8 + RAPM show Gobert is a positive contributor. The case for E is weak.
- **F (all-in star trade):** Asset cost likely exceeds expected value. The Wolves don't have a clear "we need one more star" diagnostic.

Q5 should present A, B, C as the primary options and D, E, F as alternatives the front office may want to consider given different risk tolerances or diagnostic interpretations.

---

## 6. The McDaniels question (new in v2)

The McDaniels case wasn't engaged in v1. The diagnostic work has surfaced it.

### 6.1 The data

- 2025-26 RS RAPM: -0.48 (net), -0.20 (off), +0.29 (def). Slightly below replacement by adjusted impact.
- 2025-26 RS raw on/off: -1.32 net rating differential (on +0.80, off +2.12)
- Catch-and-shoot 3PA: 2.22/game at **45.1%** (high accuracy, low volume)
- Salary: $24.4M in 2025-26, scaling to $29.8M by 2028-29; $108.4M guaranteed total

### 6.2 The questions

1. **Is McDaniels' defensive value real and under-measured?** His DPOY-tier individual defensive metrics (he's been a top-15 individual perimeter defender in lineup-grain measurements) may justify the salary even if RAPM doesn't capture it fully. The Wolves-only sample RAPM has known limitations.

2. **Can his Category B role expand?** At 45.1% catch-and-shoot accuracy, he's an elite shooter on low volume. If his role expanded to 4-5 catch-and-shoot 3PA per game, he could partially close the DiVincenzo gap internally. This depends on his ability to handle increased volume (small samples on high-volume catch-and-shoot are unreliable predictors of large-sample performance).

3. **What's his 2026-27 trajectory?** At age 25-26, he's not at his ceiling. The contract priced in his expected growth.

### 6.3 The Q5 framing

Q5 should treat McDaniels as the **"internal Category B expansion candidate."** His high accuracy on low volume is the strongest signal that he can be the partial replacement for DiVincenzo's role. Coaching emphasis on getting him 4+ catch-and-shoot 3PA per game (vs current 2.2) would:
- Partially close the Category B gap internally (saving the external acquisition for a different archetype)
- Improve his salary-efficiency picture (more production at his salary tier)
- Set up the 2027-28 evaluation cleanly (is he producing his contract value?)

If his role expansion succeeds, the Category B external acquisition can be modest (MLE-tier specialist). If it fails (his volume scaling produces accuracy regression), the external acquisition needs to be larger.

This is the cleanest framing of the McDaniels question that the data supports. Q5 should present it explicitly.

---

## 7. The math (revised)

### 7.1 Quantifying gap impact

The v1 spec's three approaches (counterfactual swap, historical comparison, RAPM estimate) remain valid. Add a fourth:

**Approach 4: Direct mechanism-based estimate.** Use the Q3 finding (Edwards' 3PA suppression specifically) to estimate the impact of adding Category B. If Category B addition adds 3-4 catch-and-shoot 3PA per game at 38%+ accuracy, the team gains roughly 4-5 points per game from the additional three-point production. Spread over 100 possessions, that's +3 to +5 ORtg points. **This is a larger estimate than the Q0D system-only impact and reinforces Path 2's primacy.**

### 7.2 The expected value calculation (revised)

The v1 framework (championship 100, finals 25, conference finals 10, round 2 3, round 1 1, miss playoffs 0) is preserved. The portfolio probabilities now incorporate:

- **Portfolio A:** baseline + 2-4 ORtg points improvement. Estimated championship probability: 4-8%.
- **Portfolio B:** baseline + 3-6 ORtg points improvement (if execution lands). Estimated championship probability: 6-12%.
- **Portfolio C:** baseline in 2026-27 + 2027-28 step-change. Estimated championship probability: 2-5% in 2026-27, with higher 2027-28 ceiling.

These are model outputs. Wide ranges expected.

### 7.3 Sensitivity to assumptions

Same as v1. Run sensitivity on the probability assignments.

---

## 8. Integration with prior analyses (updated)

Q5 v2 explicitly references:

- **Q1 v1 (`outputs/findings/q1_diagnose/01_q1_findings.md`):** Team-level 3PA collapse magnitude and CI
- **Q2 (`01_q2_findings.md` + `02_q2_corrections.md` + `03_yoy_lineup_comparison.md`):** Lineup-grain findings, the DiVincenzo Category B finding, the Gobert+Randle (not bad in RS) finding
- **Q3 v1 (`01_q3_v1_findings.md`):** The Spurs mechanism, the replicability question, the catch-and-shoot suppression
- **Q0D v1 (`01_q0d_v1_findings.md`):** The allocation restoration small-impact finding, the Gobert PR-Roll-Man volume drop
- **Q8 v1 + addendum + weighted-recent RAPM (`01_q8_v1_findings.md`, `02_q8_salary_addendum.md`, `03_q8_weighted_recent_rapm.md`):** Player-specific verdicts and salary efficiency
- **Gobert career arc (`04_gobert_career_arc_chart.md`):** The decline character (offense-only, defense intact)
- **LAFI v1 (`outputs/findings/q0a_lafi/11_wolves_lafi_deliverable.md`):** The Q4 architecture framework

### Findings the prescription should reference verbatim

- "Gobert's 2025-26-only RAPM is +1.98, defensive RAPM -5.19 (lowest in sample)" - foundation of keep-Gobert recommendation
- "DiVincenzo was the team's highest-impact player in 2025-26 sample (+4.84 RAPM)" - foundation of Category B priority and recovery investment
- "Edwards' catch-and-shoot share vs SAS was 6.2% (vs RS 13.8%)" - the cleanest mechanism finding
- "Allocation restoration impact: +0.35 ORtg per 100 possessions" - the bound on Path 3 alone
- "Randle salary surplus: -2.57 vs tier threshold" - the conditional Randle case
- "McDaniels accuracy: 45.1% on 2.22 cs_3PA/g" - the internal Category B expansion candidate

---

## 9. Charts and visualizations (updated)

The v1 chart set is preserved. Add:

- **The Gobert career arc chart** (already built; reference for system-restoration potential framing)
- **The Edwards shot diet shift visualization** (Spurs series vs RS, the catch-and-shoot collapse). Build this as part of Q5.
- **The 2027 cap roadmap chart** showing the reset asset visually
- **The salary-efficiency scatter** (RAPM vs salary, one point per rotation player) showing where the gaps are

---

## 10. Sequencing (post-diagnostic)

1. Consolidate diagnostic findings (this v2 spec is most of this work)
2. Quantify the Category B gap with named candidates
3. Quantify the secondary creator targets
4. Quantify the McDaniels expansion scenario
5. Build the portfolio comparisons with realistic ranges
6. Build the cap roadmap visualizations
7. Build the charts (including the Edwards shot diet shift)
8. Write the deliverable
9. Pause for review, then iterate

Estimated time for Q5 build: 1 week if focused. The diagnostic work is done; this is synthesis and communication.

---

## 11. What I'm worried about (updated)

The v1 worries are preserved. Add:

**Names creeping into the prescription document.** The temptation will be stronger now because the analytical foundation supports specific recommendations. Names go in appendices, not body.

**Over-confidence about the Spurs replicability.** The Q3 finding (Spurs scheme is partially replicable) is real but the magnitude of "partial" is uncertain. Don't oversell.

**Underweighting the 2027 reset because it's farther away.** The 2027 strategic asset is real and decision-relevant for 2026-27 moves. Don't ignore.

**Pulling punches on the McDaniels question.** The data has surfaced it. The front office will want analytical engagement, not silence. Address it directly.

**Pulling punches on the system restoration recommendation.** Coaching prescriptions are politically sensitive. The data supports targeted role restorations (Gobert PR-Roll-Man, Edwards PR-Ball-Handler). The deliverable should make these recommendations honestly while framing them as "the system, not the man."

---

## 12. Success criteria (revised)

**Minimum viable:** A clean primary recommendation (Portfolio A or B) with quantified expected impact, transparent assumptions, and direct reference to the diagnostic findings.

**Strong:** Three portfolios (A, B, C) with quantified expected values, sensitivity analyses, named cap implications, the McDaniels question addressed, and the Spurs replicability incorporated.

**Stretch:** A specific prescriptive recommendation that the Wolves front office isn't currently considering, defensible quantitatively, surfaced from the diagnostic work. Candidates: the Gobert PR-Roll-Man role restoration (specific, decision-relevant, non-obvious); the McDaniels Category B role expansion; the 2027 reset as a strategic asset that should influence 2026-27 decisions.

---

## 13. Open questions to revisit

1. Should the Q5 deliverable engage with the question of whether the head coach should be retained, replaced, or kept with a different offensive coordinator? The Q0D + Q3 findings suggest the offensive system needs reform but don't directly indict Finch. The political sensitivity is high.

2. How aggressively to recommend pursuing the OKC matchup specifically (architect for the worst-case opponent vs architect for the modal opponent)?

3. How much detail to provide on specific Category B candidates in the names appendix vs leaving it at archetype level?

4. Whether to commit to a single recommended portfolio or present A/B/C with the front office choosing.

---

## 14. The clean v2 framing

**The diagnosis:** Edwards is fine. The system is partially shifted but the impact is small. The Spurs found a specific scheme that exploits the team's lack of secondary off-ball threats. DiVincenzo's Achilles loss removed the team's #1 impact player.

**The prescription:** Build the supporting cast Edwards needs. Specifically:
1. Acquire one Category B wing (MLE tier, movement off-ball, 37%+ accuracy on 4+ catch-and-shoot 3PA)
2. Expand McDaniels' Category B role from 2.2 to 4+ catch-and-shoot 3PA per game
3. Restore Gobert's PR-Roll-Man volume and Edwards' PR-Ball-Handler share
4. Keep Gobert (defensively intact, his decline is offensive and partially recoverable); reassess in summer 2027
5. Keep Randle through 2026-27 unless a clear LAFI-Category-B-friendly upgrade is available
6. Protect DiVincenzo's recovery and re-sign in summer 2027 if he proves out
7. Plan around the 2027 reset (Gobert + Randle 2027-28 non-guaranteed; DiVincenzo FA) as a strategic asset

**The honest framing:** none of this is guaranteed to produce a championship. The Wolves are competing in a deep Western Conference with multiple teams (OKC, SAS, possibly others) that have or will have defensive architectures that can give them trouble. The prescription is "give Edwards the supporting cast that makes him hardest to scheme against" rather than "do X and you'll win it all."

---

End of v2 specification.
