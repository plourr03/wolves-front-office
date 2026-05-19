# Q5 v3: Prescription for the Minnesota Timberwolves [SUPERSEDED by v4]

**The 2025-26 postmortem and roster construction recommendation**

**Date:** 2026-05-18
**Status:** Q5 v3. **SUPERSEDED by Q5 v4 (`05_q5_v4_deliverable.md`).** Preserved for audit trail.

> **NOTE 2026-05-18:** Q5 v4 incorporates Phase 2 findings (Q0B contention window, Q6 v2 KAT counterfactual, Q0C historical cohort) and reads as a fresh consolidated document. The v3 below has revision markers from the contract structure correction same day; v4 reads cleanly without those markers. Refer to v4 for current state.

> **REVISED 2026-05-18 (contract structure correction):** Bobby flagged that Gobert's 2027-28 ($38M) and Randle's 2027-28 ($35.8M) are PLAYER OPTIONS (player decides, near-certain to opt in), not team-controlled non-guaranteed years. Randle's 2026-27 ($33.3M) is GUARANTEED, not a player option. The "2027 reset as automatic strategic asset" framing throughout Q5 v3 is incorrect; the reset is contingent on trade execution. Section 6 has been rebuilt around a four-scenario framework. Portfolio C has been reframed as patient-strategy-contingent-on-trades. Section 11 Gobert "free optionality" claim has been corrected. Section 6 contract table corrected. See `04_contract_structure_correction.md` for full discovery record. Q5 v4 will integrate these corrections plus Q0B/Q6/Q0C findings.

**Updates v3 vs v2:**
- Section 1 (diagnosis) adds Q7 and Q4 findings
- Section 2 (framework) elevates skilled secondary creator from opportunistic to co-priority with Category B
- Section 3 (primary path) explicit secondary creator archetype with named candidates
- Section 4 (Randle) re-framed: trade for secondary creator would address both vulnerabilities
- New Section 8: empirical matchup variance per Q4 (replaces v2's theoretical versatility framing)
- Section 9 (portfolios) re-scored on cluster coverage with explicit numbers
- Section 10 (Giannis/Durant) updated to engage with secondary-creator-not-primary-creator distinction
- Section 12 (names appendix) expanded with secondary creator candidates

---

## Executive summary

The Timberwolves' 2025-26 playoff loss to the Spurs was the latest manifestation of a structural matchup vulnerability that the team's roster construction has not addressed. The Wolves handle most NBA opponent types well in playoffs (the modal Western Conference matchup produces a +5.83 average margin across 23 playoff games over 3 years). They are catastrophically bad against two specific cluster archetypes: high-3PA offenses paired with elite rim protection defenses (Spurs-archetype, -16.17 margin in the 2025-26 R2 series), and small-ball spacing-heavy offenses (Mavericks-archetype, -5.80 margin in the 2024 WCF). The probability of avoiding both cluster types across a 4-round championship run is roughly **25-30%**.

The Wolves' supporting cast configuration matches the 2001 Sixers' template (defensive anchor + glue point guard + high-tier individual scorer) more than the 2009 Lakers' template (defensive anchor + skilled secondary creator + multi-positional wing defense). The 2001 Sixers reached the Finals but did not win. The 2009 Lakers won the championship. **The structural difference between the two templates is a skilled secondary creator.** The Wolves are one specific archetype acquisition away from the championship template.

**Concrete prescription:**

- **Acquire one multi-positional Category B wing at MLE tier** (4+ catch-and-shoot 3PA at 37%+ with movement off-ball, defensive switchability 2-4, occasional secondary playmaking)
- **Test McDaniels expansion** to 4+ catch-and-shoot 3PA per game in first 20-30 games of 2026-27
- **Restore Gobert's PR-Roll-Man volume and Edwards' PR-Ball-Handler share** through coaching emphasis
- **Pursue a skilled secondary creator** (Pau Gasol / Chris Paul / Khris Middleton / Jrue Holiday archetype) opportunistically in 2026, more aggressively in summer 2027 via trade-driven cap relief (contingent on Gobert/Randle trade execution; see Section 6 four-scenario framework)
- **Protect DiVincenzo's Achilles recovery; plan around summer 2027 re-sign priority**
- **Use the 2027 trade window** (the last chance to move Gobert and Randle before their 2027-28 player options lock in) as the strategic acquisition path. Cap relief is contingent on trade execution, not automatic.

**Explicit non-prescriptions:**
- NOT trading Gobert (positive RAPM, intact defense, top-5 league-wide defensive impact)
- NOT trading for Giannis or Durant (they are primary creators, not the skilled secondary creator the diagnostic identifies as the key gap)
- NOT architecting specifically against any one opponent
- NOT betting on Edwards' tier-leap to fix everything (25-35% probability; supporting cast is the bigger lever)
- NOT roster overhaul

**Edwards' tier-leap probability is 25-35%** (per Q7). His individual game adapted appropriately to the Spurs' scheme (46.9% FG vs SAS in his normal-load games). The team's failure was secondary creation, not his individual play. The tier-leap probability rises to 30-40% if the team adds the skilled secondary creator the historical MVP-tier supporting casts had.

**Randle disposition is conditional.** Approximately neutral by RAPM, significantly underpaid relative to production (-2.57 surplus vs tier threshold). Trade ONLY if a clear multi-positional Category B replacement OR a skilled secondary creator is available at his salary slot. Otherwise keep, deploy correctly.

---

## 1. The diagnosis

### 1.1 What broke (Q1)

Statistically distinguishable team-level offensive collapse:
- Off 3PA rate: -0.078 (42.0% RS → 34.2% PO), 95% CI [-0.104, -0.054]
- Off eFG: -0.065, 95% CI [-0.087, -0.040]

Both CIs exclude zero. The component-level offensive decline was robust.

### 1.2 Where it broke (Q2 + corrections + yoy)

The most-played 2025-26 playoff lineup configuration (Gobert+Randle, Naz off) was -13.26 over 204 minutes. But this configuration was **+5.71 in 2024-25 RS and +4.57 in 2025-26 RS** over thousands of minutes. The configuration wasn't structurally bad; it broke against the Spurs specifically.

**The DiVincenzo Category B finding is the cleanest empirical foundation:** in 2025-26 RS, DiVincenzo-on lineups were +7.57 net rating over 2463 minutes with 95% CI [+3.0, +12.2] (statistically positive). DiVincenzo-off was -4.57. A 12-point on/off swing.

### 1.3 The mechanism (Q3)

The Spurs' Wembanyama-anchored switch-everything defensive scheme produced a specific shot diet shift for Edwards:

| Metric | RS baseline | vs SAS (R2) | Change |
|---|---|---|---|
| 3PA per game | 8.43 | 5.33 | -37% |
| Average shot distance | 15.29 ft | 13.24 ft | -2.0 feet |
| Catch-and-shoot share | 13.8% | 6.2% | less than half |
| 11-16 ft floater zone share | 14.6% | 21.2% | +6.6 pp |
| 23-25 ft 3PA share | 25.8% | 16.8% | -9.0 pp |

**Edwards adapted individually.** His FG% on the shorter diet was 46.9% (RS: 48.9%). The team's secondary creation couldn't convert his kickouts.

### 1.4 The architectural context (LAFI v1, Q0D)

The Wolves run Q4 distributed pickup offense. The allocation shift from 2023-24 to 2025-26 is real but the team-ORtg impact is small: restoring 2023-24 allocation would gain only +0.35 ORtg per 100 possessions. **Targeted role restorations** (Gobert PR-Roll-Man volume down 41% YoY; Edwards PR-Ball-Handler share down 10 pp) are higher-leverage than broad allocation change.

### 1.5 The player-level picture (Q8 + RAPM)

| Player | 2025-26-only Net RAPM | League rank | Salary | Surplus vs tier |
|---|---|---|---|---|
| DiVincenzo | +4.84 | **#1 of 404** | $12.0M | **+4.34** |
| Naz Reid | +2.70 | #3 | $21.6M | +1.70 |
| Jaylen Clark | +1.45 | #23 | $2.2M | +1.45 |
| Gobert | +1.98 | #5 | $35.0M | -0.52 |
| Edwards | (artifact) | n/a | $45.6M | (true impact higher) |
| McDaniels | -0.48 | #393 | $24.4M | -1.62 |
| Randle | -0.07 | (mid-pack) | $30.9M | **-2.57** |

DiVincenzo was the team's highest-impact player in 2025-26. Gobert is intact (still top-5 league-wide in defensive impact). Edwards' offensive RAPM is +3.97 (high-tier). Randle is approximately neutral but expensive.

### 1.6 The Edwards tier-leap probability (Q7)

Weighted Euclidean similarity to 15 candidate guards at their age-24 seasons. Top 4 comps (all current era):

| Rank | Player | Outcome |
|---|---|---|
| 1 | Jaylen Brown | Finals MVP 2024, All-NBA |
| 2 | Devin Booker | Finals 2021, All-NBA plateau |
| 3 | Zach LaVine | All-Star plateau |
| 4 | Donovan Mitchell | All-NBA, contender |

**None of the top 4 closest comps reached MVP tier.** Their TS% at age 24 was 0.57-0.59. **Edwards' TS% at age 24 is 0.617**, 3-5 percentage points higher than any close comp. This efficiency edge is load-bearing for upside.

**Tier-leap probability bands:**
- Modal outcome (45-55%): Edwards plateaus at his current All-NBA tier
- Tier-leap (25-35%): Edwards reaches MVP-contender tier
- Decline (10-15%): Injury or shooting regression

### 1.7 The supporting cast template (Q7 expansion)

Across MVP-tier historical comps' championship rosters, the consistent missing piece for the Wolves is **a skilled secondary creator**.

**The 2009 Lakers championship template (Kobe + Pau Gasol + Lamar Odom):**
- Pau Gasol = skilled secondary creator (7-foot passing big, post scoring, high-IQ initiator)
- Lamar Odom = versatile forward / secondary creator from the wing
- Trevor Ariza = multi-positional wing defender
- Andrew Bynum = rim protector
- Derek Fisher = veteran PG

**The 2001 Sixers cautionary template (Iverson + Mutombo + Eric Snow + Aaron McKie):**
- Mutombo = defensive anchor (no secondary creator)
- Snow = glue PG
- McKie = secondary scorer but modest creation skill
- No skilled secondary creator. Reached Finals. Did not win.

**The Wolves' current configuration:**
- Edwards = high-tier individual scorer ✓
- Gobert = defensive anchor (Mutombo / Bynum analog) ✓
- McDaniels = multi-positional wing defender (Ariza analog) ✓
- Naz Reid = stretch big with floor-spacing (partial Bosh / Pau analog)
- Conley = veteran PG (Fisher / Snow analog, aging) ✓
- Randle = high-usage scorer, NOT a skilled secondary creator in the Pau-Gasol or Chris-Paul tier
- **Skilled secondary creator: GAP**

**The Wolves match the Iverson 2001 template more than the Kobe 2009 template.** This is the central uncomfortable truth of the analysis. But the framing is "one or two specific archetype additions away from the Kobe template" rather than "stuck at the Iverson template."

**Why "one or two" and not just "one":** the Kobe 2009 template wasn't just "Kobe + Pau Gasol." It was Kobe + Pau + Lamar Odom (versatile point-forward) + Trevor Ariza (multi-positional defender) + Andrew Bynum (rim protector) + Derek Fisher (veteran PG). Five supporting pieces, not one. The Wolves have analogues to Bynum (Gobert), Ariza (McDaniels), Fisher (Conley). **The Odom-tier point-forward versatility is the second question mark** alongside the missing skilled secondary creator. Randle is high-usage but not point-forward in skill profile.

The honest framing is therefore: the highest-leverage missing piece is the skilled secondary creator (Archetype B). The second-highest-leverage question is whether Randle's role gets filled appropriately (either by Randle himself in some lineups, or by a multi-positional 4 acquisition per Archetype A). Adding a secondary creator alone moves them partway. Adding both archetypes completes the Kobe template fit.

### 1.8 The empirical matchup variance (Q4)

K-means clustering of 30 NBA teams across 2023-24, 2024-25, 2025-26 produced 5 archetype clusters. The Wolves' performance against each:

| Cluster | Description | RS margin | PO margin | PO record |
|---|---|---|---|---|
| Cluster 0 | Traditional West (DEN, LAL, etc.) | +5.41 | **+5.83** | 16-7 |
| **Cluster 1** | **High-3PA + elite rim protection (SAS, ATL, etc.)** | +6.69 | **-16.17** | **2-4** |
| Cluster 2 | Elite defense + OKC (BOS, NYK, MIL, OKC) | +1.52 | +3.22 | 5-4 |
| **Cluster 3** | **Mixed East + DAL-style** | +4.74 | **-5.80** | **1-4** |

**Two specific playoff vulnerabilities:**
1. **Cluster 1 (Spurs-archetype):** -16.17 margin, 2-4 record. The 2025-26 R2 series.
2. **Cluster 3 (DAL-archetype):** -5.80 margin, 1-4 record. The 2024 WCF series.

**Matchup versatility variance:** standard deviation of ~10 points in playoff margin across clusters. The Wolves are matchup-specialized, not versatile.

**Expected playoff margin weighted by Western Conference cluster probability: ~-1.23 points.** Probability of avoiding BOTH vulnerable clusters across a 4-round championship run: **25-30%**.

The 2024 DAL loss and the 2025-26 SAS loss are within these vulnerable clusters. The two cluster vulnerabilities require different roster additions (Section 9).

---

## 2. The prescription framework

### 2.1 One primary path with elevated secondary creator priority

**"Build the personnel context Edwards needs."**

Consolidates v1's Paths 1 and 2 into one primary path. The diagnostic showed Edwards' development bottleneck isn't his individual skill (offensive RAPM +3.97, 0.617 TS%, 46.9% FG vs the Spurs); it's the supporting cast that converts his kickouts when defenses scheme against him.

The Q7 finding sharpens this: the supporting cast gap is specifically **a skilled secondary creator** in the Pau Gasol / Chris Paul / Jrue Holiday / Khris Middleton archetype. This is more specific than v2's "Category B" framing.

### 2.2 Two supporting elements

**Supporting element 1: System restoration (enabler).** Restore Gobert's PR-Roll-Man volume and Edwards' PR-Ball-Handler share through coaching emphasis. Worth 1-2 ORtg concentrated.

**Supporting element 2: Conditional Randle disposition.** Trade Randle ONLY if a clear multi-positional Category B replacement OR a skilled secondary creator is available at his salary slot.

### 2.3 What we are explicitly NOT prescribing

- **NOT trading Gobert in summer 2025 or summer 2026.** Positive RAPM, intact defense, defensive impact is plausibly top-5 league-wide. **REVISED:** the prior "non-guaranteed 2027-28 gives free optionality" framing is incorrect; 2027-28 is Gobert's player option (he holds it, he will exercise it). The team's options for removing him from the 2027-28 books are trade or buyout, not waiver. The cleanest trade window if value is to be extracted is summer 2026 or trade deadline 2027 (before his 2027-28 option locks in). Keep through 2026-27 still recommended; 2027-28 disposition is an active decision, not passive.
- **NOT a roster overhaul.** Edwards is the franchise. The supporting cast needs adjustment.
- **NOT trading for Giannis, Durant, or any third primary creator.** Q7 identified the missing piece as a SECONDARY creator (Pau Gasol / Chris Paul tier), not another primary star. Section 10 engages with this distinction.
- **NOT betting on Edwards' tier-leap to fix everything.** 25-35% probability; supporting cast is the bigger lever.
- **NOT architecting specifically against any one opponent.** Q4 identified two specific matchup vulnerabilities; addressing both requires versatility, not specialization.

---

## 3. The primary path: build the personnel context Edwards needs

### 3.1 The two archetype targets (now distinguished)

The Q5 v3 prescription distinguishes between two archetypes that the v2 framework conflated:

**Archetype A: Multi-positional Category B wing**
- 4+ catch-and-shoot 3PA per game at 37%+ accuracy
- Movement off-ball; ability to relocate after closeouts; closeout-attack ability
- Defensive switchability 2-4
- Occasional secondary playmaking but not primary creation skill
- Acquirable at MLE tier (~$14M) or via modest trade
- **Addresses Cluster 1 (Spurs-archetype) vulnerability**

**Archetype B: Skilled secondary creator**
- High basketball IQ; initiates offense from multiple positions
- Career assist rate above 25% (guards) or above 18% (forwards/bigs)
- Career TS% above 0.55
- Defensive minimum: defends one starting position without being a liability
- Acquirable only via major trade in 2026 or via trade-driven 2027 cap relief; costs $20M+ AAV
- **Addresses both Cluster 1 AND Cluster 3 vulnerabilities, plus unlocks tier-leap**

### 3.2 The Category B gap (Archetype A)

Internal options after DiVincenzo's Achilles tear:
- Naz Reid: 4.47/g at 38.1% (but he plays the 5, not wing)
- McDaniels: 2.22/g at 45.1% (expandable - the internal expansion test)
- Conley: 2.00/g at 38.9% (aging)
- Edwards: 2.28/g at 49.6% (primary creator)

**The gap:** ~3-4 catch-and-shoot 3PA per game of high-accuracy wing production. McDaniels expansion closes 1-2; external acquisition needs 2-3.

### 3.3 The secondary creator gap (Archetype B)

This is the gap Q7 identified as the consistent missing piece for MVP-tier supporting casts. **No current Wolves player fills this archetype.**

- Edwards: primary creator
- Randle: high-usage scorer (post-up + iso, not high-IQ playmaker)
- Conley: aging glue PG, limited creation
- Naz: stretch big with floor-spacing, modest playmaking

**The realistic acquisition paths for Archetype B:**
1. **Major trade in summer 2026.** Costs significant assets (3+ first-round picks, plus matching salary). Hard to execute because secondary creators are highly valued.
2. **Trade-driven 2027 cap relief.** Trade Gobert and/or Randle before their 2027-28 player options lock in (cleanest window: summer 2026 to trade deadline 2027). Cap relief from one trade is roughly $36M (Randle) or $38M (Gobert). Combined relief if both traded is roughly $74M. **REVISED:** this relief is not automatic; it requires trade execution. The prior "use ~$80M cap room" framing assumed team-controlled non-guaranteed years that do not exist.
3. **Internal development.** Low probability; no current young Wolves guard has this profile.

**The honest framing for 2026-27:** the realistic path for Archetype B is trade-driven (Portfolio C as patient strategy contingent on Gobert/Randle disposition). Summer 2026 likely only delivers Archetype A. The deliverable engages with this honestly rather than implying summer 2026 can deliver both archetypes, or that the 2027 cap relief opens passively.

### 3.4 The McDaniels Category B expansion test

McDaniels' 45.1% catch-and-shoot accuracy on 2.22 attempts per game is the strongest internal signal that the Category B gap can be partially closed without external acquisition.

**Recommended action:**
1. Design 2026-27 opening rotation to give McDaniels 4-5 catch-and-shoot 3PA per game opportunities
2. Track accuracy through first 20-30 games
3. If sustained at 38%+, the external Category B acquisition can be smaller (or skipped, with cap allocation shifted toward secondary creator)
4. If regresses to 33-35%, external Category B acquisition is needed

McDaniels at 25-26 is not at his ceiling. The expanded role tests whether his contract growth materializes.

**Does McDaniels expansion address Cluster 3 vulnerability?** McDaniels is a multi-positional defender (2-4). His expanded role would include more offensive responsibility. The Cluster 3 (DAL-archetype small-ball) vulnerability requires a stretch-shooting 4 who can defend in space. McDaniels at 4 could partially address this if his shooting expansion holds. But the Cluster 3 vulnerability is more about lineup composition (Gobert+Randle gets hunted) than McDaniels' specific role. Coaching the small-ball lineup (Naz at 5, McDaniels at 4) more aggressively against switch-everything spacing teams is the implementable response. **McDaniels expansion partially addresses Cluster 3 if combined with rotational discipline.**

### 3.5 The system restoration prescriptions

**Gobert PR-Roll-Man volume restoration.** From 2025-26's 111 possessions back toward 2023-24's 188. Adds 50-77 high-PPP possessions (1.27 PPP) concentrated in Gobert's minutes. Worth +0.6 to +1.0 ORtg concentrated.

**Edwards PR-Ball-Handler share restoration.** From 23.5% back toward 33.3%. Recovers 2-3 catch-and-shoot 3PA per game team-wide.

**Implementation:** Coaching emphasis prescription. Framed as "system, not the man."

---

## 4. The conditional Randle disposition (refined)

**REVISED 2026-05-18 (contract correction):** Randle's 2026-27 ($33.3M) is GUARANTEED, not a player option. His 2027-28 ($35.8M) is his player option (he holds it). The prior framing of "Branch A Randle opts in / Branch B Randle opts out" for 2026-27 is incorrect. Randle is locked in for 2026-27. The opt-in/opt-out decision is summer 2027.

The actual decision tree for the team in 2026-27:

- **A1: Keep, deploy correctly.** Maximize Edwards+Randle (+2.68 RS) and Gobert+Randle (+4.57 RS) minutes. Accept salary-vs-production gap.
- **A2: Trade Randle in 2026-27 (summer 2026, trade deadline 2027, or after season).** Targets: multi-positional Category B (Archetype A) or skilled secondary creator (Archetype B). Salary outgoing is $33.3M (guaranteed 2026-27) plus the team can include or exclude his 2027-28 player option as part of the package (most acquiring teams will want it included or want the option year converted).
- **A3: Hold and let Randle opt in to 2027-28 ($35.8M).** Most likely path. Team then faces the same trade decision in summer 2027 with Randle's $35.8M as the salary slot.
- **A4: Hold and hope Randle opts out (unlikely).** Randle at 33 with declining production is very unlikely to find $35.8M on the open market. Opt-out is the low-probability scenario.

**The realistic path:** Randle is on the roster through at least 2026-27. Trade decisions in summer 2026 or trade deadline 2027 are active. The 2027 opt-in is near-certain, which means summer 2027 trade decisions also exist (with Randle's $35.8M as the matching salary).

### 4.1 The honest framing

Randle is not the problem. His RAPM is essentially neutral. His pairings with Edwards and Gobert are positive. **He is expensive for what he provides** but he is not destroying value.

**The trade case rests on opportunity cost.** A $30M slot deployed on Archetype B (skilled secondary creator) addresses both cluster vulnerabilities AND enables Edwards' tier-leap. Randle's specific value is replaceable; the secondary creator gap is not.

If the realistic market doesn't produce an Archetype B target at his salary slot, the default is Sub-branch A1: keep, deploy correctly.

---

## 5. The McDaniels question

(Per Section 3.4 above plus the salary efficiency consideration.)

McDaniels at -1.62 surplus relative to tier threshold is the second-most-negative salary contract on the roster (after Randle's -2.57). He's locked in through 2028-29 at $108.4M guaranteed; not tradeable at meaningful value.

**The strategic question:** can McDaniels' role expand (Category B + multi-positional 4 deployment) such that his production justifies the salary?

The internal expansion test is the answer. Test in first 20-30 games of 2026-27. The test resolves to either:
- **Yes:** McDaniels' expanded role partially closes both Cluster 1 (Category B addition) and Cluster 3 (small-ball 4 deployment) vulnerabilities. The external acquisition urgency drops.
- **No:** McDaniels remains in his current role; the cluster vulnerabilities require larger external acquisitions.

---

## 6. The 2027 trade window (the active strategic decision space) [REVISED 2026-05-18]

**Previous v3 framing:** "The 2027 reset as a strategic asset" with implied automatic cap relief. **Corrected:** the 2027 cap relief is contingent on trade execution, not automatic. The Wolves do not control the 2027-28 option exercises for Gobert and Randle; both players hold those options and both will almost certainly opt in given their age and likely market value.

### 6.1 The contract picture (corrected)

| Player | 2025-26 | 2026-27 | 2027-28 | Guaranteed total |
|---|---|---|---|---|
| Edwards | $45.6M (G) | $48.9M (G) | $52.3M (G) | $202M (thru 2028-29) |
| Gobert | $35.0M (G) | $36.5M (G) | **$38.0M (Player Option)** | $71.5M (thru 2026-27) |
| Randle | $30.9M (G) | $33.3M (G) | **$35.8M (Player Option)** | $64.2M (thru 2026-27) |
| McDaniels | $24.4M (G) | $26.2M (G) | $28.0M (G) | $108.4M (thru 2028-29) |
| Naz Reid | $21.6M (G) | $23.3M (G) | $25.0M (G) | $96.6M (thru 2028-29). PO 2029-30 ($28.4M) |
| DiVincenzo | $12.0M (G) | $12.5M (G) | (FA) | $24.5M |
| Beringer | (rookie) | (rookie) | $4.6M (Team Option) | TO 2027-28, TO 2028-29 |
| Shannon | $2.7M (G) | $4.4M (G) | $5.1M (Team Option) | $7.1M |

**G = Guaranteed; PO = player option (player decides); Team Option = team decides; FA = free agent.**

Both Gobert's $38M 2027-28 and Randle's $35.8M 2027-28 are player options. Both players will almost certainly opt in (no other team will offer comparable money to a 35-year-old declining defensive anchor or a 33-year-old declining combo big). The team's options for removing either player from the 2027-28 books are trade (before the option exercises) or pay the salary.

### 6.2 The four-scenario framework

The 2027-28 cap picture depends on which trades the team executes. Four scenarios:

**Scenario 1: No trades. Both opt in. Default if no proactive moves.**
- Gobert at $38M, Randle at $35.8M. Combined $73.8M to two declining players in their age 35 (Gobert) and 33 (Randle) seasons.
- Plus Edwards $52.3M, McDaniels $28M, Naz $25M, Beringer $4.6M. Roughly $184M committed to seven players. Team is over the cap (2027-28 cap projected $170-180M).
- DiVincenzo re-sign requires MLE ($14M) or non-Bird mid-level mechanisms. Aggressive re-sign blocked by salary structure.
- Secondary creator acquisition via cap room is NOT available. Only achievable via trade.
- **Implication for prescription:** the secondary creator gap stays unaddressed unless trades happen.

**Scenario 2: Trade Gobert before 2027-28 option exercises.** Cleanest windows: summer 2026, 2027 trade deadline, or summer 2027 (with Gobert's $38M option included or excluded in the package).
- Opens roughly $38M in cap if Gobert's salary leaves cleanly (depends on outgoing contracts).
- Asset cost depends on return. Gobert at 35 with strong defense but declining offense is moderately tradeable to a contender willing to give up picks or a young player.
- Defensive value lost; needs replacement (internal or via the trade return).
- Randle stays at $35.8M.
- **Implication:** unlocks moderate cap flexibility for Archetype B or DiVincenzo aggressive re-sign.

**Scenario 3: Trade Randle before 2027-28 option exercises.** Per Q8 salary addendum, Randle is the lowest-surplus-RAPM contract on the roster; trading him is more defensible from a value perspective than trading Gobert.
- Opens roughly $35.8M in cap if Randle's salary leaves cleanly.
- Asset cost depends on return. Randle at 33 with declining production is harder to trade for premium return; more likely to require attaching picks.
- Gobert stays at $38M.
- **Implication:** smaller cap relief, less asset capital expended.

**Scenario 4: Trade both before 2027-28 options exercise.**
- Opens combined ~$73.8M in cap (assuming both salaries leave cleanly).
- Requires two separate transactions; highest execution risk.
- Asset cost depends on returns; both trades together likely require attaching significant capital.
- **Implication:** maximal cap flexibility; enables full Kobe-template-style multi-piece acquisition. Highest upside, highest execution bar.

**Scenario 5: Earlier or staggered trades.** Trade one in summer 2026 and the other later, or trade either at trade deadline 2027 if a good return is available. Each variant has different dynamics.

### 6.3 The active decision points

The team faces these active decision points:

**Summer 2026:**
- Trade Gobert? Highest-value window if a contender is willing to buy. Cost: defensive impact during Edwards' rising-peak year.
- Trade Randle? Per Q8, surplus-RAPM is negative; defensible from value angle. Cost: matched salary flexibility for 2026-27 acquisitions.
- Sign Archetype A (Category B wing) at MLE? Tactical; addresses Cluster 1 partially.

**Trade deadline 2027 (February 2027):**
- Final pre-option-exercise window for Gobert and Randle trades. After this, the team has less control because the players will opt in to 2027-28.

**Summer 2027:**
- Gobert and Randle opt in to 2027-28 (near-certain).
- DiVincenzo enters FA. Re-sign decision constrained by Scenario 1-4 outcome.
- Beringer and Shannon team options likely exercised.
- The "summer 2027 reset" is now a trade window if cap room is wanted, not a waiver window.

**Mid-season 2027-28:**
- Trade deadline February 2028 is another window to move Gobert or Randle if the team wants in-season pivot.

### 6.4 The 2026-27 decisions that interact with the 2027 window

The 2026-27 decisions still matter, but the framing is different. They are not "preserve the automatic asset." They are "preserve trade execution capacity."

- One-year MLE for Category B acquisition (don't burden long-term roster commitments).
- DiVincenzo recovery management (his summer 2027 re-sign depends partly on cap room from Scenario 2-4).
- Gobert pre-option trade evaluation (is the return better in summer 2026, deadline 2027, or summer 2027 with the option included?).
- Randle pre-option trade evaluation (same framing).
- Asset capital preservation (picks, young players) for trades that enable cap relief.

### 6.5 The honest verdict on the 2027 strategic landscape

The 2027 path to address the Archetype B (skilled secondary creator) gap requires trade execution. Summer 2026 likely cannot deliver Archetype B (cost too high, market constraints, asset capital needed). The 2027 cap room available depends on which scenario the team executes. **Scenario 4 (trade both Gobert and Randle) is the highest-upside path but the highest-execution-bar path; Scenario 3 (trade Randle only) is the most defensible from a value perspective but the smallest cap relief.**

Portfolio C in Section 9 has been reframed to reflect this. The patience is not waiting for the cap to open automatically. The patience is preserving asset capital and waiting for the right Scenario 2-4 trade opportunity.

---

## 7. The Spurs replicability question (Q3 + Q4 combined)

Q4's cluster analysis empirically validates the Q3 finding that the Spurs' scheme is partially replicable. Cluster 1 (high-3PA + elite rim protection) includes multiple teams beyond SAS: ATL, POR, CHI, MEM, IND, BKN. Cluster 2 (elite defense + OKC) has similar architectural elements.

**The Wolves should architect for the broader class, not Wembanyama specifically.** OKC (Cluster 2) is a likely 2026-27 playoff opponent; Spurs (Cluster 1) is a 2027-28 likely opponent. Multiple teams have the architecture to give the Wolves trouble.

**This sharpens the Category B target.** Movement off-ball + closeout-attack + multi-positional defense is the archetype. Pure spot-up shooters won't help against switch-everything schemes.

---

## 8. Matchup versatility (now empirical per Q4)

The v2 spec named matchup versatility as the meta-principle. Q4 puts numbers on it.

### 8.1 The Connelly-era reactive specialization pattern

**2022 offseason:** Connelly trades for Gobert (built for Nuggets matchup). Paid off in 2024 WCF.

**2024 WCF:** Mavericks small-ball exposes the design's vulnerability. Wolves' bigger lineups get hunted.

**Summer 2024:** KAT-to-Randle trade (response to Dallas). Gains some flexibility but disrupts offensive architecture (LAFI's core finding).

**2025-26 R2:** Spurs' Wembanyama-anchored switch-everything scheme exposes the new build. Edwards' 3PA suppressed; team's secondary creation can't convert.

**The pattern is reactive specialization.** Each iteration solves the immediate problem and creates the next vulnerability.

### 8.2 The empirical matchup variance (Q4)

Per Q4's cluster analysis:

- **3 of 5 cluster types handled well in playoffs** (Cluster 0: +5.83 over 23 games; Cluster 2: +3.22 over 9 games; Cluster 4: outlier)
- **2 of 5 cluster types catastrophic in playoffs** (Cluster 1: -16.17 over 6 games; Cluster 3: -5.80 over 5 games)
- **Standard deviation of playoff margin across clusters: ~10 points** (matchup-specialized, not versatile)
- **Probability of avoiding both vulnerable clusters across 4-round championship run: 25-30%**

### 8.3 The honest implication (dual framing)

**Even with optimal execution of the prescription, the Wolves face a structural 70-75% probability of drawing at least one bad-matchup cluster opponent in a championship run.** This is a real structural obstacle, not a remediable execution issue.

**Two framings of this number matter:**

**The league-wide structural matchup tax.** All NBA teams face this. The Cavaliers had to figure out how to beat the Warriors. The Bucks faced the Heat in 2020. Even championship teams usually have at least one tough draw in a 4-round run. **The 25-30% probability of avoiding bad matchups isn't unique to the Wolves; it's the structure of bracket-style playoffs.** Every championship requires winning matchups that include at least one architecturally challenging opponent.

**The Wolves-specific Western Conference layer.** Their two vulnerable clusters (Spurs-archetype Cluster 1 and DAL-archetype Cluster 3) include teams the Wolves face in any Western Conference playoff bracket. The 25-30% is specifically about the Western Conference, where avoiding both archetypes requires a favorable bracket. **The Wolves face the matchup tax MORE than most contenders** because their two cluster vulnerabilities overlap with likely WC playoff opponents.

Both framings are true. The deliverable engages with both rather than dismissing the structural reality or overstating the Wolves-specific challenge.

Adding Archetype A (Category B wing) addresses Cluster 1 partially. Adding Archetype B (skilled secondary creator) addresses both Cluster 1 and Cluster 3. The team's path to genuine championship contention requires reducing the matchup variance, which requires architectural additions to the roster.

**The matchup versatility argument is now empirical. The recommendation isn't "fix the Spurs problem." The recommendation is "reduce the matchup variance via specific archetype additions targeted at the two vulnerable cluster classes."**

### 8.4 What versatility requires

Per Q4's empirical findings + Q3 + Q7:

1. **Multi-positional defensive lineup configurations.**
   - Small-ball switchable: Naz at 5, McDaniels or new multi-positional 4 at 4. **Addresses Cluster 3.**
   - Traditional rim-protection: Gobert at 5, Randle or new stretch 4 at 4. **Default; handles Cluster 0.**

2. **Multiple offensive engine options.**
   - Edwards as primary creator (default; current).
   - Edwards as off-ball threat with skilled secondary creator (currently missing; this is the Archetype B gap). **Addresses Cluster 1.**
   - DiVincenzo as movement shooter (when healthy). **Addresses Cluster 1.**

3. **Multiple pace profiles.**
   - Half-court grinding (current strength).
   - Transition-heavy (the team's transition share rose in 2025-26; modest strength).

**The Wolves' current roster has versatility on dimension 3 and partial versatility on dimension 1.** The versatility gap is on dimension 2 (skilled secondary creator). This connects directly to the Q7 finding.

---

## 9. The three portfolios (re-scored on cluster coverage)

### Portfolio A: "Build the supporting cast" (DEFAULT)

**Personnel:**
- Acquire one multi-positional Category B wing at MLE tier (Archetype A)
- Test McDaniels Category B role expansion
- Defer Archetype B (secondary creator) acquisition to summer 2027 via trade-driven cap relief (contingent on Gobert/Randle trade execution per Section 6)

**System:**
- Coaching emphasis on PR-Ball-Handler and PR-Roll-Man restoration

**Player decisions:**
- Keep Gobert through 2026-27
- Keep Randle; deploy correctly
- Protect DiVincenzo recovery

**Cluster coverage scoring:**
- **Cluster 1 (Spurs-archetype):** Improves moderately. Category B addition adds movement shooting. McDaniels expansion adds more. Doesn't fully address (no secondary creator).
- **Cluster 3 (DAL-archetype):** Improves marginally. McDaniels at 4 in small-ball lineups partially. Multi-positional Category B partially. Not fully addressed.
- **Cluster 0 (traditional West):** Stable. Already strong.
- **Cluster 2 (elite defense):** Stable. Already decent.

**Expected impact:** +2 to +4 ORtg points in 2026-27. Championship probability change: +2 to +4 percentage points. **Cluster vulnerability variance reduction: modest** (down from 10 to maybe 7-8).

**Versatility added:** MODERATE. Partial improvement on both vulnerable clusters.

### Portfolio B: "Targeted upgrade"

**Differs from A:** Trade Randle for either Archetype A (multi-positional Category B) OR Archetype B (secondary creator).

**Sub-branches:**
- **B-Category-B:** Randle traded for multi-positional Category B. Addresses Cluster 1 strongly, Cluster 3 partially.
- **B-Secondary-Creator:** Randle traded for Archetype B (likely requires additional outflow plus picks). Addresses both Cluster 1 AND Cluster 3. Best execution case but hardest to actually land.

**Cluster coverage scoring (B-Secondary-Creator):**
- **Cluster 1:** Improves substantially. Skilled secondary creator can punish doubles (Q3 finding).
- **Cluster 3:** Improves substantially. Secondary creator with playmaking handles small-ball spacing.
- **Cluster 0, 2:** Stable or improving.

**Expected impact:** +3 to +6 ORtg points if execution lands. Championship probability change: +5 to +10 pp. **Cluster variance reduction: substantial** (down from 10 to maybe 5-6).

**Versatility added:** HIGHER. Both vulnerable clusters addressed.

**Risk:** Execution. Randle alone is unlikely to be enough trade salary for Archetype B; additional outflow required. The deal may not be available at acceptable cost.

### Portfolio C: "Trade-driven 2027 cap path" [REVISED 2026-05-18]

**Previous framing:** "Preserve 2027 flexibility" assumed automatic cap relief in summer 2027. **Corrected:** Portfolio C is now framed as a patient strategy contingent on trade execution. The cap relief in 2027 only opens via Scenario 2-4 trades described in Section 6.

**Personnel:**
- Sign Archetype A (multi-positional Category B) on a 1-year MLE deal (or 2-year with team option)
- Preserve asset capital (picks, young players) for trades that enable cap relief
- Actively shop Gobert and Randle for fair-value trades in 2026-27 (summer 2026, trade deadline 2027, or summer 2027)
- Do not commit to long-term contracts beyond what is necessary

**2026-27 actions:**
- Execute at least one of: trade Gobert OR trade Randle OR test the market for both
- The cleanest trade window is summer 2026 (full season for acquired player) or trade deadline 2027 (in-season)
- McDaniels expansion test still runs in parallel

**2027 plan (contingent on 2026-27 execution):**
- If Scenario 2 or 3 executed (one of Gobert/Randle traded): ~$36-38M cap relief in 2027-28. Use on Archetype B trade or aggressive DiVincenzo re-sign.
- If Scenario 4 executed (both traded): ~$74M cap relief. Use on Archetype B + DiVincenzo + additional Category B (the Kobe-template multi-piece reset).
- If Scenario 1 (no trades, both opt in): cap room not available. Archetype B requires another trade in 2027-28 itself.

**Cluster coverage scoring:**
- **2026-27:** Same as Portfolio A if trades execute (lose Gobert means Cluster 0/2 coverage drops; Archetype A addition partially addresses Cluster 1). Net likely +1 to +2 ORtg.
- **2027-28 with Scenario 2-4 executed:** Archetype B acquisition addresses both vulnerable clusters substantially. Step-change potential.
- **2027-28 if Scenario 1 (no trades):** marginal additional improvement.

**Expected impact:** 2026-27 +1 to +3 ORtg if trades execute cleanly; 2027-28 step-change potential if scenario delivers Archetype B.

**Versatility added:** HIGHEST in the long run IF trade execution succeeds.

**Execution risk (much higher than v3 implied):**
- Gobert trade in 2026-27 forfeits his RAPM #1 defensive value during Edwards' rising-peak year. Cost is real.
- Randle trade is more defensible from RAPM/salary efficiency, but salary is lower and matching for Archetype B is harder.
- Trading both requires two separate transactions, both with asset costs.
- If neither trade executes, Portfolio C collapses to a slightly modified Portfolio A.

**Risk:** the entire path requires the front office to execute one or more difficult trades. Without trade execution, the 2027 cap room does not materialize and the prescription's secondary creator acquisition path is constrained.

### Portfolio comparison (6 dimensions including cluster coverage)

| Dimension | A (default) | B (upside) | C (trade-driven 2027 path) |
|---|---|---|---|
| 2026-27 ORtg gain | +2 to +4 | +3 to +6 | +1 to +3 (if trades execute) |
| Championship prob change | +2-4 pp | +5-10 pp | +1-3 pp 2026-27, higher 2027-28 if scenario delivers |
| Asset cost | Low (MLE) | Medium-High (trade) | Medium (Gobert/Randle trade returns) |
| Execution risk | Low | Medium-High | **Medium-High (REVISED)** |
| **Cluster 1 (Spurs) coverage** | **Moderate** | **High (esp. B-Secondary-Creator)** | **Moderate now, High 2027 if Archetype B acquired** |
| **Cluster 3 (DAL) coverage** | **Marginal** | **High (esp. B-Secondary-Creator)** | **Marginal now, High 2027 if Archetype B acquired** |
| 2027 cap flexibility | Preserved | Reduced | **Trade-contingent** (REVISED) |
| Versatility variance reduction | 10 → 7-8 | 10 → 5-6 | 10 → 7-8 now, 5-6 in 2027 if scenario lands |

**REVISED 2026-05-18:** Portfolio C is no longer "very low execution risk." The trade-driven path requires trading Gobert and/or Randle before their 2027-28 player options exercise. Without those trades, the cap room does not materialize.

**Recommendation:** **Portfolio A as the default 2026-27 action** (Category B at MLE, McDaniels expansion, system restoration, DiVincenzo recovery management). **Pair with Portfolio C's trade-driven path as the medium-term strategy.** Portfolio A and C are complementary, not alternatives: A executes the tactical 2026-27 move while C preserves and actively pursues the trade execution that opens 2027 cap room.

The honest framing: **Summer 2026 likely delivers Portfolio A. Summer 2026 also opens the active trade window for Gobert and/or Randle. The team must engage that trade window (or the trade deadline 2027) if Portfolio C's 2027 cap room is to materialize.** Portfolio B-Secondary-Creator is the upside scenario if a clear Archetype B trade target emerges in 2026, but the execution bar is high.

The 2-year sequence: Portfolio A in 2026-27 plus active trade engagement for Gobert/Randle. If a trade lands, 2027 cap room enables Archetype B acquisition. If not, the team faces Scenario 1 (Section 6) and the secondary creator gap requires a 2027-28 trade with constrained mechanics.

---

## 10. Why we don't recommend trading for Giannis Antetokounmpo or Kevin Durant (updated with Q7 insight)

The Q7 finding specifically sharpens this section. The diagnostic identifies a SECONDARY creator as the key supporting cast gap. **Giannis and Durant are primary creators, not secondary creators.** Adding them doesn't address the gap the analysis identifies.

### 10.1 The diagnostic doesn't point at primary star acquisition

The Wolves have a primary star (Edwards, +3.97 offensive RAPM). The Wolves don't have a skilled secondary creator in the Pau Gasol / Chris Paul / Khris Middleton tier. Adding Giannis or Durant adds a SECOND primary creator, not the missing secondary creator.

**Two-primary-creator rosters have known coordination issues.** The Brooklyn Nets with Durant + Irving + Harden won zero championships. The Phoenix Suns with Durant + Booker + Beal didn't make it to the Finals. The exception (Wade + LeBron + Bosh 2012-13) required LeBron specifically to take a secondary creator role - a unique tier of player.

**The historical evidence:** the Pau Gasol-tier secondary creator with the Kobe-tier primary star produced championships more reliably than the two-primary-creator structure has in recent decades.

### 10.2 The trade math (reiterated from Q5 v2)

For Giannis:
- Two structures: (a) Edwards + filler + 4-5 firsts, or (b) Randle + McDaniels + Naz + 4-5 firsts (keeps Edwards but guts depth)
- Both defeat the diagnostic prescription

For Durant:
- Randle + McDaniels + 3 firsts roughly
- Adds 38-year-old primary creator with 1-2 year window
- Doesn't address the secondary creator gap

### 10.3 The Q7-informed verdict

**Even if the front office had unlimited assets, the right target wouldn't be Giannis or Durant.** It would be a skilled secondary creator at the Pau Gasol or Chris Paul tier.

Realistic 2027-reset Archetype B targets (illustrative, will be stale):
- Khris Middleton (career trajectory; trade possible)
- Jrue Holiday (aging but still in archetype; cost question)
- Tyrese Haliburton (durability question; possibly available)
- LaMelo Ball (durability; possibly available)
- Sabonis (skilled big; archetype fit)
- Trae Young (younger; primary creator who could be secondary)

**These are the right archetype.** Not Giannis. Not Durant.

### 10.4 The 2027 trade-driven framing for star pursuit [REVISED 2026-05-18]

If the front office wants to pursue Archetype B aggressively, the path is contingent on Gobert/Randle trade execution:
- Trading Gobert (Scenario 2) opens ~$38M cap room. Trading Randle (Scenario 3) opens ~$36M. Trading both (Scenario 4) opens ~$74M.
- The cap room does not open automatically; it requires trade execution before the 2027-28 player options exercise.
- Asset preservation through 2026-27 enables higher-quality trade packages.
- DiVincenzo retention as a complementary piece if proves out, contingent on cap room from Scenario 2-4.

**This is the realistic championship-pursuit path.** Summer 2026 Portfolio A plus active Gobert/Randle trade engagement. Trade deadline 2027 is the second active window. Summer 2027 cap deployment depends on whether at least one of those trades executed.

---

## 11. Cap reality

(Same as Q5 v2 Section 11; preserved.)

### 11.1 Salary efficiency picture

Using 2025-26-only RAPM:

| Player | 2025-26 | Net RAPM | Surplus vs tier |
|---|---|---|---|
| DiVincenzo | $12.0M | +4.84 | **+4.34** |
| Naz Reid | $21.6M | +2.70 | +1.70 |
| Gobert | $35.0M | +1.98 | -0.52 |
| McDaniels | $24.4M | -0.48 | -1.62 |
| Randle | $30.9M | -0.07 | **-2.57** |

**DiVincenzo is the most underpriced contract.** Aggressive recovery investment supported.

**Randle is the largest negative surplus.** Conditional disposition tree in Section 4.

### 11.2 Implementation cap math

- MLE-tier Category B acquisition: feasible at $14M
- Trade Randle for upgrade (Category B or secondary creator): feasible if right target
- Star trade: trade-driven 2027 cap relief is the realistic path (see Section 6 four-scenario framework)

---

## 12. Names appendix (illustrative; will be stale)

**Use the archetype thresholds in Sections 3.1-3.3 as the acquisition criteria.** Names are examples of player types, not specific recommendations. Markets in summer 2026 will differ.

### 12.1 Archetype A: Multi-positional Category B wing (MLE or modest trade)

**Tier 1 (Realistic at MLE):**
- Royce O'Neale (39%+ 3P, defensive switchability 2-4, occasional playmaking)
- Cam Johnson (39%+ 3P, defensive size; BKN possible trade)
- Naji Marshall (DAL: switchable wing, growing shooting)
- Gary Trent Jr. (38%+ 3P, defensive utility)

**Tier 2 (Stretch via modest trade):**
- Bogdan Bogdanovic (shooting + some creation)
- Norman Powell (40%+ 3P, scoring volume)

### 12.2 Archetype B: Skilled secondary creator (target for trade-driven 2027 cap relief, major trade in 2026 if available)

**Tier 1 (Pau Gasol / Chris Paul tier - the championship template):**
- Khris Middleton (career trajectory + shooting + creation, available?)
- Jrue Holiday (two-way guard, aging but in archetype)
- Tyrese Haliburton (durability question; possibly available)
- Domantas Sabonis (skilled big with creation from post/elbow; archetype fit but expensive)

**Tier 2 (Younger / higher-upside if available):**
- Trae Young (primary creator who could be secondary alongside Edwards)
- LaMelo Ball (durability question)
- Tyler Herro (shooting + creation)

**Tier 3 (Specific fit questions):**
- Coby White (developing secondary creation)
- D'Angelo Russell (volume + 3P, defensive concerns)

### 12.3 Multi-positional stretch-four (for Portfolio B Randle upgrade if Archetype B unavailable)

**Tier 1:**
- Naji Marshall (also Archetype A; small-ball 4 in switchable lineups)
- Aaron Gordon (DEN: defensive switchability + improving shooting; cost question)
- John Collins (UTA: stretch 4 with adequate switchability)

### 12.4 The honest caveat

**Names are illustrative.** Real 2026 and 2027 markets depend on trajectories, contract statuses, team willingness to move. **The archetype thresholds are what to pursue.**

---

## 13. What this deliverable doesn't do

- Full league-wide RAPM (would resolve Edwards artifact and tighten calibration)
- Spotrac-based cap and trade math
- Action classifier and refined PnR coverage decoder
- Defensive-anchor center age curve for Gobert
- Achilles recovery comp set for DiVincenzo
- Q0B (trajectory windows) and Q0C (historical cohort) - pending Phase 2
- Q6 KAT counterfactual - pending Phase 2

These sharpen specific findings but don't change the central prescription.

---

## 14. The honest framing (matchup variance lens)

### 14.1 The structural reality

Even with optimal execution, the Wolves face a 70-75% probability of drawing at least one bad-matchup cluster opponent in a 4-round championship run. The roster has matchup vulnerabilities that aren't fully remediated by any single 2026-27 move.

The realistic path to championship contention is **multi-year and multi-acquisition.** Summer 2026 (Portfolio A): one Category B wing + McDaniels expansion + system restoration plus active Gobert/Randle trade engagement. Summer 2027 (Portfolio C path, contingent on trade execution): skilled secondary creator acquisition via trade-driven cap relief + DiVincenzo re-sign + role players.

### 14.2 The hopeful framing

**The Wolves are not stuck. They are one or two specific archetype additions away from the Kobe 2009 template (championship-realistic) rather than the Iverson 2001 template (Finals possible, championship unlikely).**

The highest-leverage addition is the skilled secondary creator (Archetype B). The Kobe template was Kobe + Pau + Odom + Ariza + Bynum + Fisher. The Wolves have analogues to Bynum (Gobert), Ariza (McDaniels), Fisher (Conley). The Pau analog (skilled secondary creator) is the priority. The Odom analog (multi-positional point-forward) is the second consideration, and depends on whether Randle's role gets filled appropriately (by him or by an Archetype A acquisition).

The acquisitions are hard but specific. The path is real (trade-driven 2027 cap relief for the secondary creator, contingent on Gobert or Randle trade execution). The probability of championship contention is meaningfully higher with both additions than without.

### 14.3 The structural takeaway

The Wolves' 2025-26 problems weren't catastrophic and weren't player failures:
- Three positive-impact contributors (Gobert, DiVincenzo, Edwards) at the individual level
- The supporting cast around them needs adjustment, not overhaul
- The 2027 cap relief is a real strategic opportunity contingent on Gobert/Randle trade execution
- The matchup vulnerabilities are structural but addressable through specific archetype additions

**Edwards is fine** (offensive RAPM +3.97, 0.617 TS%, 25-35% tier-leap probability).
**Gobert is fine** (RAPM +1.98 in 2025-26-only, top-5 defensive impact, contracts give optionality).
**Randle is approximately neutral** (RAPM -0.07, salary-vs-production gap, conditional disposition).
**DiVincenzo is the question** (highest-impact player in 2025-26 sample; Achilles recovery is the key variable).
**The supporting cast gap is specific:** skilled secondary creator.

The team's job is to address that gap, manage rotations to maximize the positive pairings, and engage the trade-driven 2027 cap path (Scenario 2-4 in Section 6) if 2026-27 doesn't produce the secondary creator acquisition directly.

---

## 15. Status and next steps

Q5 v3 complete. Incorporates Q7 (star comp + supporting cast templates) and Q4 (archetype stress test). The matchup versatility framing is now empirical. The Iverson 2001 vs Kobe 2009 template distinction provides the central uncomfortable-but-honest framing.

### Project build status

| Analysis | Status |
|---|---|
| Q0A LAFI v1 | Complete |
| Q1 Diagnose | Complete |
| Q2 Localize | Complete (v1 + corrections + yoy) |
| Q3 Mechanism | Complete (v1) |
| Q0D Coaching System | Complete |
| Q8 Player Decisions | Complete (v1 + addendum + weighted-recent) |
| Q7 Star Comp | Complete (v1 + supporting cast detail) |
| Q4 Archetype Stress Test | Complete (v1) |
| **Q5 Prescription** | **Complete (v1, v2, v3 this doc)** |
| Q6 KAT Counterfactual | Pending (Phase 2) |
| Q0B Trajectory Windows | Pending (Phase 2) |
| Q0C Historical Cohort | Pending (Phase 2) |
| Q9 Superstar Acquisition | Built into Q5 v3 Section 10 |

### Phase 2 remaining

Per the data scientist's plan:
- Q6 (KAT counterfactual)
- Q0B (trajectory windows)
- Q0C (historical cohort)

Plus Phase 3 infrastructure (league-wide RAPM, Spotrac).

### Artifacts

```
specs/
  q5_prescription_spec_v2.md          v2 spec

outputs/findings/q5_prescription/
  01_q5_v1_deliverable.md             v1 (preserved)
  02_q5_v2_deliverable.md             v2 (preserved)
  03_q5_v3_deliverable.md             v3 (this document)
```

The Q5 v3 is the project's culminating prescriptive document with full integration of all completed analyses. The matchup versatility framing is now empirical. The Iverson template / Kobe template distinction provides the central honest framing. The acquisition-archetype map (Archetype A: multi-positional Category B; Archetype B: skilled secondary creator) connects diagnostic findings to actionable recommendations.

The Phase 2 analyses (Q6, Q0B, Q0C) will sharpen specific aspects but the central prescription is in place.

---

End of Q5 v3.
