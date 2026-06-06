# Q0D: Coaching System Analysis Specification

**Project:** Timberwolves 2025-26 Postmortem
**Analysis ID:** Q0D
**Status:** Specification, revised post-LAFI v1 (2026-05-17)
**Position in stack:** Meta-layer analysis. Now anchored on the LAFI allocation problem finding. Moved up in the build sequence to immediately after Q3 (per master plan v3 Section 4) because the allocation finding is fresh and Q0D directly tests it.

**Revision note:** LAFI v1's "allocation problem" finding (off-ball motion held flat at 10-11% across all five Edwards-era seasons; iso rose from 7-8% to 9.6% while PR-Ball-Handler dropped from 14-16% to 13.1%) sharpens Q0D's central question. The system has not lost actions; it has reallocated them. Q0D now tests this empirically. A fifth verdict option ("allocation-shifted") is added. An allocation-restoration-impact sub-section quantifies what restoring 2023-24 ratios would do.

---

## 1. The thesis

### 1.1 The question

How has Chris Finch's offensive system changed from the 2023-24 (KAT-era) Wolves to the 2025-26 (Randle-era) Wolves, and is the current system fundamentally stale, structurally constrained by personnel, or both?

This is the system-level question that sits between roster construction (which can be changed) and coaching philosophy (which is harder to change). Understanding the answer matters because it determines whether the fix is "different players" or "different system" or "both."

### 1.2 Why this matters

If the system is fundamentally good but constrained by personnel, the fix is roster moves. The system will breathe again with the right players.

If the system is fundamentally stale and not adapting, the fix is system change. New plays, new philosophy, possibly new coaching staff influence.

If both, the fix is multi-layered. New players AND a fresh system rebuild.

Most fans assume "more talent fixes everything." Most front offices assume "the coach should adapt." Both are sometimes wrong. The right diagnostic engages with the system honestly.

### 1.3 The honesty requirement

This is the most politically sensitive analysis in the project. Chris Finch is a respected coach. The Wolves reached the conference finals under him in 2023-24. Saying "the system has gotten stale" is implicitly critical of his work.

The right framing: this is about the system, not the man. Even great coaches' systems can need refresh, especially after major personnel changes. The KAT-Randle swap was a fundamental change in offensive personnel. A system that was elegant with KAT may not be elegant with Randle, and that's not necessarily Finch's fault, but it is something the organization needs to address.

### 1.4 The working hypothesis (revised post-LAFI)

The 2023-24 Wolves offense was a real system: motion, off-ball screens, KAT as a gravitational hub, Ant as the engine. It was distinctive. **LAFI v1 confirmed this empirically: 2023-24 was the most-designed version of the Edwards-era offense, with Movement Death at 43rd percentile (lowest of the era), Isolation Reliance at 49th, and Shot Quality Decay at 39th.**

The 2024-25 and 2025-26 offense has progressively become less systematic. Randle is a different kind of player than KAT (more iso, more post-up, less catch-and-shoot, less ball-screen versatility). The system has gradually contracted around the players' individual strengths and lost the connecting tissue that made 2023-24 work.

**(Post-LAFI refinement) The allocation problem.** LAFI v1's most diagnostic finding for Q0D: off-ball motion (Cut + OffScreen) has been flat at 10-11% across all five Edwards-era seasons. What has changed is the iso/PR balance. Iso rose from 7-8% to 9.6%. PR-Ball-Handler dropped from 14-16% to 13.1%. **The system has not lost actions; it has reallocated them.** The pick-and-roll is in the playbook. It is being called less. Q0D's central question is now sharper: is this allocation shift coaching-driven or personnel-driven, and what is the realistic ceiling of restoring it?

The result: an offense that looks more like a collection of individual actions than a coherent system. Hence "pickup at LA Fitness" from Scott's text. The data shows the actions exist; the calling has shifted.

---

## 2. The data structure

### 2.1 Play type frequencies

For each season (2022-23 through 2025-26), pull play type frequencies:
- Pick-and-roll ball-handler
- Pick-and-roll roll-man
- Post-up
- Isolation
- Spot-up
- Handoff
- Off-screen
- Cut
- Transition

For each play type, also pull PPP (points per possession).

### 2.2 Action chaining

A "single action" possession involves one identifiable action (e.g. PnR, then shot). A "multi-action" possession chains actions (e.g. PnR, then flare screen, then catch-and-shoot).

Multi-action possessions are the signature of designed offenses. Build a per-season count of multi-action possession frequency from PBP (requires the action classifier).

### 2.3 Off-ball action density

From tracking and PBP:
- Off-ball screens per 100 possessions
- Cuts per 100 possessions
- Player movement (distance traveled off-ball per possession)

These metrics capture how much architecture exists off-ball.

### 2.4 Ball movement

- Passes per possession
- Touches per player
- Time of possession per touch

Designed offenses have more ball movement and more distributed touches. Iso-heavy offenses have less.

### 2.5 Personnel-controlled comparisons

The system metrics need to be evaluated controlling for personnel. To isolate the "system" effect from the "player" effect:

**Compare same lineups across seasons.** For lineups that played in both 2023-24 and 2024-25 (or any two seasons), did their play type frequencies and offensive characteristics change? If yes, that's likely a system change (since the players are the same).

**Compare similar players across roles.** KAT's role in 2023-24 and Randle's role in 2024-25/25-26 can be compared. Are they being used in similar actions? Is the offense flowing through them in similar ways? Or have the actions changed substantially?

This isolates system changes from personnel changes.

---

## 3. The math

### 3.1 Play type evolution

For each play type, compute frequency and PPP across the four seasons:

```
                 22-23    23-24    24-25    25-26
PnR ball-handler 24%      27%      29%      31%
Post-up          12%      9%       11%      14%
Isolation        9%       8%       11%      13%
Off-screen       8%       11%      8%       6%
Spot-up          21%      19%      18%      16%
Cut              7%       9%       7%       5%
...
```

(Illustrative numbers.)

The pattern of interest: are "designed" play types (off-screen, cut) declining while "individual" play types (iso, PnR, post-up) increasing? If yes, the system is contracting.

### 3.2 Action density score

Compute a composite "action density" score for each season:
- Off-ball screens per 100
- Cuts per 100
- Multi-action possession rate
- Off-ball touches per game

Normalize and average. Track over time.

A declining action density score over time is evidence of a stale or contracting system.

### 3.3 The Randle effect

Specifically: with Randle on the floor vs off the floor, what does the offense look like?

If Randle's presence systematically changes the offense toward iso/post-up and away from designed actions, that's evidence the system has constrained itself around him.

### 3.4 League comparison

Where does the Wolves' system metrics rank in the league? Top 5 teams typically have:
- High passes per possession
- High off-ball action density
- Multi-action possession rates
- Diverse play type distributions

Bottom teams have the opposite. Wolves' position over time tells the story.

---

## 4. The diagnostic questions

### 4.1 Has the offensive system contracted?

Specifically: does the data show a year-over-year reduction in action diversity, off-ball architecture, and ball movement?

If yes: the system has changed substantially since 2023-24.

### 4.2 Is the change personnel-driven or coach-driven? (Sharpened post-LAFI)

This is the central question of Q0D post-LAFI. The allocation problem finding tells us the playbook is preserved but the calling has shifted. The question is whether the shift is forced by personnel (Randle's skill set requires more iso) or chosen by coaching (the same actions could be called with the existing personnel but are not).

Comparing same-lineup performance across seasons isolates the system effect. If the same lineups are running different actions in 2025-26 vs 2024-25, that's a coaching decision. If different lineups (Randle vs KAT) are running different actions, that's personnel.

**Specific allocation-shift tests:**

- For lineups containing Randle in 2024-25 vs the same lineups in 2025-26: did iso usage rise within the same lineup configuration? If yes, the shift is coaching-driven within the same personnel. If iso stayed stable within lineups but the team's overall iso rose because of different lineup deployment, the shift is personnel-mix-driven.
- For lineups not containing Randle in 2024-25 vs 2025-26: did their iso usage rise? If yes, the shift is broader than Randle-specific.
- For the starting lineup specifically: how has the play-type distribution shifted?

The answer determines whether Path 3 (system change) is a credible primary prescription (if coaching-driven) or a constrained one (if personnel-driven and the personnel is what it is).

### 4.3 Does the system perform when run?

Even if the offense has shifted toward iso, when designed actions are run, do they still work? If yes, the system is still good but underused. If no, the system itself isn't working.

### 4.4 What would the system look like with the right personnel?

A counterfactual: if the Wolves had a secondary creator and a stretch big, what would the system likely look like? Compare to historical comps (Q0C) that successfully ran modern offenses.

### 4.5 The "stale" verdict (revised post-LAFI)

Synthesizing: is the Wolves' offensive system:
- Stale: not adapting to modern league trends regardless of personnel
- Personnel-constrained: would be fine with the right players
- Both: needs refresh AND new players
- Neither: actually fine and the diagnosis is elsewhere
- **(Post-LAFI fifth option) Allocation-shifted: the playbook is preserved but the calling has changed toward iso. Same actions, different choices.** This is the verdict LAFI's allocation finding implies. It is distinct from "stale" (which would mean the actions are missing) and from "personnel-constrained" (which would mean the actions are missing because the personnel can't run them). Allocation-shifted means the actions are there; the coach is choosing iso anyway.

### 4.6 The allocation restoration impact (post-replan addition)

If the allocation-shifted verdict holds (or partially holds), quantify the impact of restoring the 2023-24 allocation. Specifically:

Hold personnel constant. Project the Wolves' offensive performance if:
- Iso frequency dropped from 9.6% back to 7-8% (2023-24 baseline)
- PR-Ball-Handler frequency rose from 13.1% back to 14-16%
- Off-ball motion held at current 10.2% (no required change)

The projection uses Synergy per-play-type PPP for the Wolves' personnel applied to the counterfactual allocation. Output: an expected change in offensive rating from the allocation restoration alone.

If the projected improvement is meaningful (say, 2+ points of offensive rating), Path 3 has empirical support and Q5's Primary Portfolio A (system-first) is credible. If the projected improvement is small (under 1 point), Path 3's ceiling is lower than the LAFI deliverable suggested and Q5's prescription should weight Paths 2 and 1 more heavily.

This sub-analysis is the answer to the question Q5 needs: "what is the realistic ceiling of system-only improvements?"

---

## 5. Charts and visualizations

### 5.1 The Play Type Evolution

A stacked bar chart, one bar per season, showing the breakdown of possessions by play type. Visualizes the shift in offensive composition.

### 5.2 The Action Density Trend

A line chart of the composite action density score across seasons, with the league median overlaid for context.

### 5.3 The Ball Movement Trend

A line chart of passes per possession across seasons.

### 5.4 The Lineup-Controlled Comparison

A specific comparison: for lineups that played in multiple seasons, how have their offensive characteristics changed?

---

## 6. Sequencing

Q0D requires the action classifier (built for LAFI Component 4 and Q3). Build it after those analyses are underway.

1. Pull play type and tracking data across seasons
2. Compute frequencies and densities
3. Run lineup-controlled comparisons
4. Build trend charts
5. Write up

Estimated time: 1-2 weeks.

---

## 7. What I'm worried about

**Selection effects in play type frequencies.** Teams may run fewer designed actions because their players can't execute them, not because the coaching staff doesn't call them. Don't over-interpret a frequency change as a system change.

**The 2023-24 Wolves benefited from a lot of factors.** KAT was healthy. Ant took a leap. The team was relatively injury-free. Some of the system's success was contextual.

**Causal attribution is hard.** It's nearly impossible to definitively say "this change is the coach's fault" vs "this change is the players' fault" because they interact. Be honest about the ambiguity.

**Political sensitivity.** Implications about coaching are read by coaches. Keep the framing focused on system and structure, not personality.

---

## 8. Success criteria

**Minimum viable:** Clear trends in play type frequencies and action density across seasons, with appropriate context.

**Strong:** The analysis cleanly separates personnel effects from system effects, providing a defensible answer to whether the system or the personnel needs change.

**Stretch:** The analysis surfaces specific recommendations (e.g., "the system needs to reintroduce off-ball architecture around X player") that have evidence behind them.

---

End of specification.
