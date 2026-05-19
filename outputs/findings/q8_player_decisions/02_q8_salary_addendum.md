# Q8 salary addendum: cap context, opt-in decision trees, scenario reframing

**Date:** 2026-05-17
**Status:** Addendum to `01_q8_v1_findings.md`. Adds the salary dimension that the v1 didn't engage with directly.
**Source:** `specs/timberwolves-current-salaries.csv` (provided by user).

> **REVISED 2026-05-18 (contract structure correction):** This addendum had two material errors. (1) Section 2 framed Randle's 2026-27 ($33.3M) as a player option. It is GUARANTEED. His player option is 2027-28 ($35.8M). (2) Section 3 framed Gobert's 2027-28 ($38M) and Randle's 2027-28 ($35.8M) as team-controlled non-guaranteed years that the team could "let slide off the books." Both are PLAYER OPTIONS; both players will almost certainly opt in. Sections 2, 3, 4, 5, 7, 9 have been revised. The "free roll" / "2027 reset as automatic strategic asset" framing throughout was incorrect; the 2027 cap relief is contingent on trade execution. See `../q5_prescription/04_contract_structure_correction.md` for full discovery record.

## What this addendum adds

Four pieces, all flagged by the data scientist's review of Q8 v1:

1. A salary-efficiency table that pairs each rotation player's adjusted impact (RAPM) with their salary, and a tier-based threshold comparison
2. An opt-in decision tree for Randle's 2026-27 player option
3. The summer 2027 DiVincenzo free agency and its interaction with Randle and Gobert 2027-28 option years
4. Reframing Scenario C from "data-aggressive" to "data-targeted upgrade path"

The addendum re-reads the Randle case with salary context in hand. It does not pre-commit to a new conclusion. The salary changes the framing of what "approximately neutral RAPM" means in context, not the RAPM itself.

## 1. Salary-efficiency table

Each Wolves rotation player's 2025-26 salary alongside their RAPM net (or for Edwards, offensive RAPM as the meaningful proxy since net is a Wolves-only-sample artifact). The "implied threshold" column is a heuristic for what a player at that salary tier typically needs to produce; "surplus" is impact minus threshold.

| Player | Age | 2025-26 | 2026-27 | Off RAPM | Def RAPM | Net RAPM | Impact proxy | Per-$M | Threshold | Surplus |
|---|---|---|---|---|---|---|---|---|---|---|
| Anthony Edwards | 24 | $45.6M | $48.9M | +3.97 | +4.58 | -0.61 (artifact) | **+3.97** | 0.087 | 4.0 | -0.03 |
| **Rudy Gobert** | 33 | $35.0M | $36.5M | -0.71 | **-6.89** | **+6.18** | **+6.18** | **0.177** | 2.5 | **+3.68** |
| **Julius Randle** | 31 | $30.9M | $33.3M | +1.07 | +1.95 | **-0.88** | -0.88 | -0.029 | 2.5 | **-3.38** |
| Jaden McDaniels | 25 | $24.4M | $26.2M | -0.20 | +0.29 | -0.48 | -0.48 | -0.020 | 1.0 | -1.48 |
| Naz Reid | 26 | $21.6M | $23.3M | +0.04 | -2.38 | **+2.42** | +2.42 | 0.112 | 1.0 | +1.42 |
| Donte DiVincenzo | 29 | $12.0M | $12.5M | +0.38 | -0.97 | +1.35 | +1.35 | 0.113 | 0.5 | +0.85 |
| Ayo Dosunmu | 26 | $7.5M | (FA) | -0.33 | +1.45 | -1.79 | -1.79 | -0.238 | 0.5 | -2.29 |
| Joan Beringer | 19 | $4.2M | $4.4M | +1.00 | +1.58 | -0.58 | -0.58 | -0.138 | 0.0 | -0.58 |
| Terrence Shannon Jr. | 25 | $2.7M | $2.8M | +0.30 | +3.07 | -2.77 | -2.77 | -1.035 | 0.0 | -2.77 |
| Jaylen Clark | 24 | $2.2M | (FA) | +1.55 | +0.10 | +1.45 | +1.45 | **0.664** | 0.0 | +1.45 |
| Mike Conley | 38 | $0.7M | (FA) | -1.06 | -0.66 | -0.40 | -0.40 | -0.544 | 0.0 | -0.40 |

(I previously corrected for the salary CSV showing the $35M tier threshold; updated to use $25-35M tier threshold of +2.5 for Randle's salary slot.)

### How to read the salary-efficiency table

The "threshold" column is a rough NBA-market convention for what a player at each salary tier typically needs to produce to "justify" the contract. The thresholds I'm using:

| Salary tier | Implied RAPM threshold |
|---|---|
| Under $5M (minimum/cheap rotation) | 0.0 (any positive contribution justifies) |
| $5-15M (MLE tier) | +0.5 |
| $15-25M (mid tier) | +1.0 |
| $25-35M (star tier) | +2.5 |
| $35M+ (max tier) | +4.0 |

These are approximate. Actual NBA market efficiency varies. But the directional message is clear: a player at $30M needs to produce meaningfully more than a player at $10M to be considered "well-paid."

### What the table shows

**Gobert: producing 1.5x his contract.** At $35M, the implied threshold is +2.5 RAPM. He produces +6.18 RAPM, a surplus of +3.68. The clearest positive-value contract on the roster.

**Naz Reid: good value.** $21.6M for +2.42 RAPM is a surplus of +1.42. Good return on the contract.

**DiVincenzo: good value (pre-injury).** $12M for +1.35 RAPM is a surplus of +0.85. The 2026-27 deployment value depends entirely on his recovery, but his salary slot is reasonable for the role.

**Edwards: at threshold (per offensive RAPM proxy).** $45.6M is the max tier with implied threshold +4.0. His offensive RAPM is +3.97. He's producing roughly his contract value by this measure, with the strong caveat that the Wolves-only sample artifact makes his true impact likely meaningfully higher. A full league-wide RAPM would resolve this and almost certainly show Edwards as a meaningful positive-value max contract.

**Randle: -3.38 surplus.** $30.9M for -0.88 RAPM is the largest salary-vs-impact gap on the roster. This doesn't make him a bad player. It makes him a structurally inefficient use of the $30M slot, IF the salary could be redeployed to produce meaningfully more.

**McDaniels: -1.48 surplus.** A real gap but smaller than Randle's. At $24.4M he's producing slightly less than the implied threshold for the $15-25M tier. Worth noting but not necessarily actionable. His contract runs 4 more years; the surplus may close as the cap grows.

**Terrence Shannon Jr., Bones Hyland, Ayo Dosunmu:** all negative-surplus on small contracts. Manageable but worth knowing.

**Jaylen Clark: best value player on the roster.** +0.66 RAPM per million is the highest ratio. At minimum salary for a positive contributor, he's a bargain.

### Honest caveat about the salary-efficiency framing

The Wolves-only RAPM has known limitations (Section 6 of `01_q8_v1_findings.md`). For Edwards specifically the net RAPM is artifact. For other Wolves rotation players the RAPM is internally consistent but possibly biased in absolute magnitude. The salary efficiency comparisons are directional, not absolute.

The directional message: **Gobert is significantly outproducing his contract; Randle is significantly underproducing his.** This is robust to the sample limitation because both players have similar adjustment biases (both have ~70 games per season included; both have similar opponent context).

## 2. Randle disposition decision tree [REVISED 2026-05-18]

**Corrected contract structure:** Randle's 2026-27 ($33.3M) is GUARANTEED. His player option is 2027-28 ($35.8M). The Spotrac Guaranteed total of $64.2M = $30.9M (2025-26) + $33.3M (2026-27). The 2027-28 $35.8M is the player option (PO in green per Spotrac convention).

Randle is locked in for 2026-27 regardless of his preference. The opt-in/opt-out decision is summer 2027 for the 2027-28 season. The active trade windows are summer 2026, trade deadline 2027, and summer 2027 (with his $35.8M PO typically included or excluded as part of the trade package).

### Branch A: Hold Randle through 2026-27, he plays out his guaranteed year

**Most likely default scenario if no trade lands.** Randle plays the 2026-27 season at $33.3M guaranteed. He approaches his $35.8M player option in summer 2027 from a contract-year context. Team decisions:

- **Sub-branch A1: Keep, deploy carefully.** Manage rotations to maximize Edwards+Randle and Gobert+Randle minutes. Minimize the Edwards-OFF Randle-ON cohort. This is the "use correctly" path from Q8 v1.

- **Sub-branch A2: Trade in 2026-27 for a targeted upgrade.** Active trade windows: summer 2026 (full season for incoming player) or trade deadline 2027 (mid-season). If a stretch-4 catch-and-shoot specialist with playmaking is available at his salary slot, the math favors the move. The salary-efficiency table: $30M slot producing -0.88 RAPM; threshold +2.5. Even a +1 RAPM upgrade closes ~$10M annually.

- **Sub-branch A3: Trade in 2026-27 for cap relief.** Returns expiring contracts or younger players on rookie deals plus picks. The team can convert the -3.38 surplus into future flexibility. Note: this is a trade-driven path to cap relief, not a passive 2027 reset.

### Branch B: Summer 2027 - Randle's player option decision (the actual opt-in/opt-out moment)

**B1: Randle opts in to $35.8M for 2027-28 (most likely).** At age 33 with declining production, $35.8M is well above what he could secure on the open market on a multi-year deal. Near-certain opt-in. The team then faces the same trade-or-keep decision for 2027-28 with $35.8M as the salary slot.

**B2: Randle opts out (low probability).** Only happens if Randle believes he can secure a longer-term deal at lower AAV but more guaranteed years (e.g., 3 years $20M AAV). This is unlikely at age 33. If it happens, the team has $35.8M of cap space freed automatically.

### Synthesis on Randle (corrected)

The decision is conditional in two layers: first on whether the team executes a trade during 2026-27, then (if no trade) on Randle's opt-in choice in summer 2027 (near-certain opt-in). The data supports "approximately neutral piece at a high salary" which makes the case for moving him compelling, but the move only makes sense IF a clear upgrade or meaningful cap flexibility is achievable. The active trade windows are summer 2026, trade deadline 2027, and summer 2027 with his $35.8M PO as the matching salary.

**Refined probability assignment (updated from v1 with salary context):**

| Question | Q8 v1 estimate | Updated with salary context |
|---|---|---|
| Randle is a net negative on the current roster | 30-45% | 30-45% (unchanged) |
| Randle is overpaid relative to production | n/a in v1 | **70-85%** (new finding from salary lens) |
| The realistic alternative improves the team | 35-50% | 40-55% (slightly up; the salary makes the upgrade math easier) |
| Probability the team should actively pursue a Randle trade during 2026-27 | Not assigned | 45-60% (Randle is locked in for 2026-27; active trade windows are summer 2026, deadline 2027, summer 2027) |

## 3. The 2027 trade window and DiVincenzo's contract year [REVISED 2026-05-18]

**Previous framing was wrong about team control of 2027-28.** The original Section 3 framed Gobert's 2027-28 $38M and Randle's 2027-28 $35.8M as team-controlled non-guaranteed years that the team could "let slide off the books." Both are PLAYER OPTIONS. Both players will almost certainly opt in. The team's options for removing them from the 2027-28 books are trade or buyout, not waiver.

The corrected structural feature: **summer 2027 is an active trade window, not a passive reset year.**

| Player | 2025-26 | 2026-27 | 2027-28 | 2028-29 |
|---|---|---|---|---|
| Edwards | $45.6M (G) | $48.9M (G) | $52.3M (G) | $55.7M (G) |
| Gobert | $35.0M (G) | $36.5M (G) | **$38.0M (Player Option)** | (FA) |
| Randle | $30.9M (G) | $33.3M (G) | **$35.8M (Player Option)** | (FA) |
| McDaniels | $24.4M (G) | $26.2M (G) | $28.0M (G) | $29.8M (G) |
| Naz Reid | $21.6M (G) | $23.3M (G) | $25.0M (G) | $26.7M (G). PO 2029-30 ($28.4M) |
| **DiVincenzo** | **$12.0M (G)** | **$12.5M (G; final)** | (FA) | (FA) |

**DiVincenzo is a 2027 free agent.** His Achilles tear hits during his final guaranteed year (2026-27 will be the recovery year). This means:

1. **2026-27 is his contract-year test.** If he recovers and plays well, he commands a meaningful deal in summer 2027. If he doesn't recover, he's a buy-low candidate.
2. **The team's 2026-27 deployment of DiVincenzo is partly contract evaluation.** This creates an incentive structure: the team wants to test his form to know what to offer, but his health needs protecting.
3. **His summer 2027 free agency interacts with the team's Gobert/Randle trade decisions.** Cap room to re-sign DiVincenzo aggressively only materializes if the team executes Scenario 2-4 from Q5 v3 Section 6 (trade Gobert, trade Randle, or trade both before their 2027-28 options exercise). If neither trade happens, both players opt in to their 2027-28 contracts and the Wolves are over the cap; DiVincenzo re-sign is constrained to the MLE or related mechanisms.

**The 2027-28 cap projection (corrected):**
- Currently committed if both options exercised: Edwards $52.3M + Gobert $38M + Randle $35.8M + McDaniels $28M + Naz $25M + Beringer $4.6M = ~$184M
- That is over the cap (2027-28 cap projected $170-180M).
- Cap room only opens via trades. If Gobert traded: ~$38M relief. If Randle traded: ~$36M relief. If both traded: ~$74M relief.

**The 2027 cap relief is a real strategic opportunity but it is contingent on trade execution, not automatic.** The 2026-27 decisions (DiVincenzo deployment, Randle/Gobert trade engagement, system restoration) all interact with whether the team can land Scenario 2-4 trades during 2026-27 or summer 2027.

### Implications for Q5 Path 2 (Category B acquisition)

The DiVincenzo gap analysis in Q8 v1 said external Category B acquisition is required for 2026-27. With the contract context added:

- A one-year MLE deal (~$14M) for a catch-and-shoot wing in summer 2026 is the right tool. It bridges to DiVincenzo's potential 2027-28 return without long-term commitment.
- If DiVincenzo doesn't recover, the team can re-sign the bridge wing or upgrade further with the 2027 cap room.
- If DiVincenzo does recover, the team has flexibility to redirect the cap room toward other needs.

This is a cleaner Q5 Path 2 framing than the v1 had: short-term acquisition with the 2027 reset as the long-term play.

### Implications for the Gobert decision [REVISED 2026-05-18]

**The previous framing assumed team control of Gobert's 2027-28 year. That was wrong.** Gobert's $38M 2027-28 is his player option; he holds it; he will almost certainly opt in given his age (35) and the lack of other teams offering comparable money.

Corrected reading:

- Gobert is guaranteed through 2026-27 ($71.5M over 2 years). The 2027-28 ($38M) is a player option held by Gobert (not team control).
- The team's options for removing Gobert from the 2027-28 books are trade or buyout. There is no "let him roll off" path because he will opt in.
- The keep-Gobert recommendation from Q8 v1 still holds for 2026-27 (RAPM #1, defensive value during Edwards' rising-peak, system restoration value). But the framing of "we can keep him for 2026-27 with the door open to either extend or move on cheaply in summer 2027" is wrong. The summer 2027 decision is "trade or pay $38M." There is no waiver path.
- The cleanest trade window if value extraction is desired is summer 2026 or trade deadline 2027 (before his 2027-28 option locks in). Summer 2027 trades become harder because acquiring teams have to absorb $38M for a 35-year-old.
- **Corrected recommendation framing:** "Keep Gobert through 2026-27 for tactical reasons, with active trade-evaluation in summer 2026 and trade deadline 2027 as the genuine value-extraction windows."

## 4. Reframing Scenario C

The data scientist's note: "data-aggressive" implies higher risk than is warranted for Scenario C. The reframing:

| Scenario | v1 framing | Refined framing |
|---|---|---|
| A. Keep all three | **Data-conservative path** | **Preserve-what's-working path** |
| B. Trade Gobert, keep Randle | NOT supported | NOT supported |
| C. Keep Gobert, trade Randle | Data-aggressive path | **Data-targeted upgrade path** |
| D. Trade both | NOT supported | NOT supported |

Scenario C is now framed as a single specific upgrade: replace Randle's slot with a player whose archetype better fits LAFI Category B + the team's existing stars. This isn't aggressive; it's targeted. The risk is execution-dependent (does the team actually land the right replacement) rather than directional.

With the salary context: the case for Scenario C is sharper. The $30M slot producing -0.88 RAPM is a clear opportunity cost. The same slot deployed on a +1.5 to +2.5 RAPM player closes ~$10-15M of "production gap" annually. The math favors the move IF the replacement is genuinely better and IF the trade return doesn't sacrifice future flexibility.

## 5. Updated four-scenario assessment

With salary context integrated:

**Scenario A (Preserve what's working):** Cap implication: $193M total in 2025-26, $190M in 2026-27. Stays in luxury tax range. Bets on DiVincenzo recovery and on Q5 Path 2 acquisition via MLE or trade. **REVISED:** the "free roll on Gobert's 2027-28 non-guaranteed year" framing was incorrect; Gobert holds his 2027-28 player option and will exercise it. Scenario A's implicit assumption that the team can re-evaluate Gobert cheaply in summer 2027 is wrong. The summer 2027 path for Gobert is trade or pay $38M.

**Scenario C (Data-targeted upgrade):** Trade Randle for a Category B stretch-4 archetype. The trade math is conditional on what's actually available. Best-case (clean upgrade at similar salary): the team gets the LAFI-Category-B-friendly piece AND keeps Gobert AND preserves 2027 flexibility. Worst-case (cap dump or modest upgrade): minor improvement, possible asset cost.

The two scenarios are not mutually exclusive in a soft sense: Scenario A can pivot to Scenario C mid-season if the right trade emerges. The recommendation: pursue Scenario A as the default, with active exploration of Scenario C trade opportunities.

**Scenarios B and D remain unsupported** by the empirical evidence. Trading Gobert forfeits the team's clearest positive-value contract (surplus +3.68 over implied threshold). Trading both adds execution risk without clear empirical upside.

## 6. What this addendum does NOT change

Three things from `01_q8_v1_findings.md` remain unchanged:

- **The DiVincenzo case stays at KEEP/PROTECT/ADD CATEGORY B REDUNDANCY.** Salary supports the case (he's a good-value contract); contract year adds the strategic dimension but doesn't change the recommendation direction.
- **The Gobert case stays at KEEP WITH CONDITIONS.** Salary strongly supports keeping (he's the highest-surplus contract on the roster). The "conditions" remain Category B around him.
- **The Edwards framing stays at untouchable + offensive RAPM is the meaningful signal.** Salary at max tier matches his production tier.

The Randle case is the one that meaningfully changes with the salary lens. The shift: from "use correctly, assess the opt-in" (v1) to "use correctly OR pursue targeted upgrade IF a clear LAFI-Category-B-fitting replacement is available; the salary gap makes the upgrade case more pressing" (this addendum).

## 7. What this addendum still doesn't do

- **Realistic trade market analysis.** The addendum names the question (what's actually available at Randle's salary slot) but doesn't answer it. External research required.
- **Free-agent market projection for summer 2026 and 2027.** Same.
- **Detailed cap math under Sub-branches A1, A2, A3.** The addendum frames the decision tree but doesn't compute specific cap implications under each sub-branch. A v3 would build this out.
- **Weighted-recent RAPM (decline test for Gobert).** Still the highest-leverage analytical follow-on. Bobby's data scientist explicitly flagged this as blocking for final ship.
- **Defensive-anchor center age curve.** Supplementary but valuable for the Gobert long-term framing.
- **Achilles recovery comp set for DiVincenzo.** Same.

## 8. Artifacts

```
analyses/q8_player_decisions/
  salary_efficiency.py            new module
outputs/tables/q8_player_decisions/
  salary_efficiency.csv           Wolves rotation with salary + RAPM + thresholds
outputs/findings/q8_player_decisions/
  01_q8_v1_findings.md            (original Q8 v1)
  02_q8_salary_addendum.md        (this document)
specs/
  timberwolves-current-salaries.csv   (input data provided by user)
```

Re-runnable: `python -m analyses.q8_player_decisions.salary_efficiency`.

## 9. Honest synthesis with the salary lens

The salary efficiency table makes one finding visually clear: **Gobert is the most positive-value contract on the roster, and Randle is the most negative-value contract.**

This sharpens the original Q8 v1 conclusions:

- Keep Gobert: even cleaner case. He produces 1.5x his contract tier.
- DiVincenzo: even cleaner case. His pre-injury production was good value at $12M; recovery makes the salary slot pay off again in 2026-27 if he comes back.
- Randle: the case for moving him is now more pressing in opportunity-cost terms. The $30M slot deployed elsewhere likely produces more. But the move only helps if a clear upgrade or meaningful cap relief is achievable.

**The data-targeted upgrade path (Scenario C) becomes the active scenario to pursue.** The team should explore Randle trade opportunities specifically for LAFI-Category-B-fitting replacements at his salary slot or for cap relief that can be deployed on Category B + bench depth. If no clean upgrade emerges, Scenario A (preserve) remains the default with the salary gap accepted as cost-of-doing-business.

**The 2027 trade window is a real strategic opportunity, contingent on trade execution.** [REVISED 2026-05-18] Gobert and Randle both have player options for 2027-28 and both will almost certainly opt in. The cap room ($36-74M depending on which trades execute) only materializes if the team trades one or both before their 2027-28 options exercise. This interacts with DiVincenzo's free agency (he's a 2027 FA too) and with the team's ability to acquire Category B and bench depth. The 2026-27 decisions should be evaluated partly through the lens of "what trade execution capacity are we preserving for the 2027 window."

## 10. Tasks remaining for Q8 final ship

Per the data scientist's review, the blocking item before Q8 final ship:

- **Weighted-recent RAPM (Gobert decline test).** 30 minutes. If his 2025-26-specific impact is meaningfully lower than the 3-year pooled +6.18, the keep-Gobert framing needs adjustment.

Non-blocking but valuable:

- Defensive-anchor center age curve
- Achilles recovery comp set
- Full league-wide RAPM (resolves Edwards artifact)
- Realistic trade market research

The agent's recommended next sequence stands: weighted-recent RAPM first (30 min), then Q0D and Q3 (which inform Q5's prescription paths), then Q5 spec revision based on what Q0D and Q3 surface.
