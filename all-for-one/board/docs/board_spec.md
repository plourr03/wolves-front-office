# Board Spec: State Space, Root Node, and Decision Calendar

For the **ONE FOR ALL** master plan project (public name; internal codename and repo path: `all-for-one`, working title "If I Were Tim Connelly"). Covers the state vector definition, the root node encoded as of July 17, 2026, the decision calendar through the summer 2028 gate, and the mapping from each moving part to the machinery that powers it.

**Version 2.1, July 17, 2026. Source of truth.** Consolidates and supersedes the 0.1-0.4 drafts (this file replaces both the prior `board_spec.md` at 0.3 and the `board_spec (1).md` at 0.4). Companion to `tripwire_backtest_spec.md` (v0.2) and `jaden_markers.md`. Facts pulled from the July 2026 asset audit carry VERIFY tags where they can drift.

Version history:
- 0.1: initial state vector, root node, decision calendar; Jaden a state variable with the loyalty premium as a first-class output; repeater clock in the cap state; ARM-D dump arm with reset-aware valuation; ownership curves beside the Ant machine; standing orders (section 7).
- 0.2: availability transition source corrected after the tripwire Phase 0 finding that pick2033 models draft slots, not player availability (see `phase0_avail_pace_redefinition.md`); the P_yes probability gate replaced with the acceptance model's boolean verdict plus sweetener price (gap G5).
- 0.3: (draft) minor consistency edits.
- 0.4: `jaden` gains a fourth tier, CONVERTED (defensive gate failed, offensive leap achieved), per Bobby's ruling; tier semantics and markers in `jaden_markers.md`.
- 2.0: consolidated to a single source-of-truth file; duplicate removed; settled tripwire findings folded into the transition mapping (AVAIL-PACE threshold derived and live; SPACE-ANT reclassified dashboard-only per gap G4; PAIR-DRTG/FC-DRB pending final Phase 1 panel results); Jaden markers cross-referenced now that `jaden_markers.md` exists.
- 2.1: adopts the public name **ONE FOR ALL** (internal codename `all-for-one` retained as the repo path). Adds the SALVAGE term to the objective (section 0/1): departure is no longer worth zero; it carries a leverage-adjusted salvage value capped at SALVAGE_CAP (0.03, Bobby's dial), and a new proactive-conversion arm ARM-CONVERT sits beside the involuntary REQUESTED absorbing state. See section 4 and `build/board_step3_report.md`.

## 0. Plain language summary

The board is a map of every situation the franchise can be in between now and the summer of 2028, plus a pre-committed move for each situation where a move exists. To make that computable, each situation is compressed into a short list of variables (how the team is performing, how healthy LaMelo is, what Ant has signed or declined, what assets remain, where the payroll sits). This file defines those variables, records today's values as the starting point, lists every calendar date where a decision or a dice roll happens, and states which of Bobby's existing models supplies the probabilities for each dice roll. The objective being maximized, from the earlier design conversations: the probability of winning a championship while Anthony Edwards is a Timberwolf. **The exception, the salvage term (ONE FOR ALL, v2.1): if Ant leaves, the era does not end at zero. A departure salvages a leverage-adjusted return (the picks and youth a trade returns, worth more the earlier and more proactively it happens), capped so that a stocked rebuild is worth at most a small slice of title odds (SALVAGE_CAP) and no genuinely live contender is ever traded away for it. Proactively converting (ARM-CONVERT) returns more than waiting for a forced request (REQUESTED): that gap is the price of hesitation, Utah trading Gobert in 2022 versus Minnesota waiting on Garnett in 2007.** Two humans the model cannot see inside, the star and the owner, are carried as explicit curves with robustness sorts, and the things nobody can schedule are covered by standing orders rather than nodes.

## 1. Design principles

State membership test: a variable belongs in the state vector only if some pre-committed action differs based on its value. Everything else lives in the simulation layer.

Observability: the policy conditions only on what the front office can observe. Latent quantities (Ant's true patience, LaMelo's true fit ceiling) are carried by models (hazard curve, fit priors), not by the state.

Forward equity is the value function. It is computed by backward induction, read by the retention hazard, and never stored as a state variable.

Absorbing states: RING (a championship is won; the objective is achieved) and REQUESTED (Ant requests a trade; per the design decision, this ends the board rather than branching into a rebuild, which is a different story). A supermax signing is NOT absorbing; it modifies the hazard (see section 4).

Soft horizon: the board is built in detail through July 2028. Seasons beyond carry probability mass only along branches that kept Ant, so the far side of the board dims rather than ends. Terminal states at the modeling edge carry a continuation value estimated from state health, so the solver never torches the final year.

## 2. State vector

S = (t, perf, run, melo_avail, fit, ant, melo_deal, jaden, cap, chest)

| Variable | Levels | Rationale |
|---|---|---|
| t | Node index from the calendar in section 5 | Time and action menus are node dependent |
| perf | T1 top-4 seed pace, T2 playoff band, T3 play-in band, T4 lottery band | Gates deadline posture and feeds the hazard through equity |
| run | none, R1, R2, WCF, F, RING within the window | Deepest playoff result since June 2026; monotone; RING absorbing; primary hazard covariate |
| melo_avail | A on or above 60-game pace, B 40 to 59 pace, C under 40 pace | Tiered from the availability baseline (prior-three-season median, 47 games) and, once built, the real availability posterior; gates ARM-G. The in-season read is AVAIL-PACE (threshold derived, see section 8) |
| fit | prior, green, yellow, red | Compressed tripwire state (the wired metrics: PAIR-DRTG and TOV-BLEED; SPACE-ANT is dashboard-only per tripwire gap G4, not a wire); gates ARM-S and trade arms |
| ant | default, smax_signed, smax_declined, REQUESTED | Observable commitment machine; see section 4 |
| melo_deal | pre_ext (3 years left), extended, walk (2028-29 unextended) | Own decision plus his agreement; affects hazard and salvage |
| jaden | leap, steady, converted, stalled | Named bet in the thesis; the gate move differs by tier, with CONVERTED (defensive gate failed, offensive leap achieved) as the archetype-change branch where the loyalty premium is expected to diverge widest; tier markers defined in `jaden_markers.md`, frozen after the feasibility pass |
| cap | below_tax, tax_band, apron1_band, apron2_plus, each carrying a repeater_clock count of consecutive tax finishes | Determines legal action menus under the apron rules and the marginal price of a payroll dollar |
| chest | Tuple, see below | Determines which trade arms are constructible |

chest = (firsts_tradeable: 0 or 1, pick2028_status: swap_pending or resolved_kept or resolved_swapped, unlock_done: bool, seconds: int VERIFY from warehouse, sweeteners: subset of {Shannon, Beringer, Evans, Clark, Zikarsky}, expirings: subset of {Green, DDV, Gobert_27_28}, core_on_roster: subset of {Gobert, Jaden})

Lives in the simulation layer, not the state: full roster and minutes, individual stat lines, opponent strength and schedule. Ownership tax appetite is handled by the curves in section 4 rather than by a state variable.

Rough size: 4 x 6 x 3 x 4 x 4 x 3 x 4 x 4 levels across roughly 14 time nodes with a modest set of reachable chest combinations. Naive product is large; reachability pruning (run is monotone, chest evolves nearly deterministically given actions, absorbing states exit) should land the reachable set in the low thousands. Phase one of the build should print the exact count.

## 3. Root node, July 17, 2026

t: node 0. perf: projection band pending a fresh Joan Bet run on the post-trade roster; placeholder T2. run: none (window opens June 2026; context for the hazard baseline: WCF trips in 2024 and 2025, then a second-round exit in 2026, a step back that mildly elevates the starting hazard). melo_avail: prior from the prior-three-season games-played median (47), pending the availability posterior build. fit: prior (no shared-floor data exists yet for the Ant-LaMelo pair; the pair has never shared a floor). ant: default. melo_deal: pre_ext, and note the two-year extension window is ALREADY OPEN per reporting from the trade (VERIFY exact eligibility window). jaden: steady (baseline; tier markers now defined in `jaden_markers.md`, frozen after the feasibility pass, before the October freeze). cap: apron1_band with repeater_clock 2, tax finishes in 2024-25 and 2025-26 and a third projected in 2026-27, meaning repeater rates arrive with this season's bill or 2027-28 at the latest (VERIFY exact trigger against CBA text), over the first apron, under a second-apron hard cap that expires June 30, 2027, roughly 4.4M of headroom (VERIFY, drifts with signings). chest: firsts_tradeable 0, pick2028_status swap_pending (Charlotte), unlock_done false, seconds VERIFY from warehouse ledger, sweeteners {Shannon, Beringer, Evans, Clark, Zikarsky}, expirings {Green about 14.7M, DDV about 12.9M injured (Achilles, expected to miss most or all of the season)}, core_on_roster {Gobert (expiring after 2027-28, salary roughly high 30s VERIFY), Jaden (through 2028-29)}. Additional root facts: two open roster spots, veteran minimum is the only signing tool, leftover trade exceptions functionally dead while over the first apron, no midlevel.

Pruned branch: LeBron. Per the design decision, the exercise assumes he signs elsewhere. On the published board he appears as a grey stub that resolved in July 2026.

## 4. The Ant commitment machine

States: default, smax_signed, smax_declined, REQUESTED (absorbing).

Hazard windows: July 2027 (first supermax offer window, minor hazard), July 2028 (major hazard, the gate), February 2029 (near terminal). Between windows the hazard is small but nonzero.

Patience curve, per the design conversation: the cliff. Commitment probability as a function of forward three-year title equity (computed by the solver at the decision window), sigmoid with midpoint near 10 percent and steep slope, so equity below roughly 8 percent reads as probable departure and above roughly 13 percent as probable commitment. Robustness requirement: every recommended move is re-derived under the ramp (midpoint 8, moderate slope) and the results sorted into moves that hold under both curves versus moves that flip. Only the first pile is presented as unconditional.

Supermax mechanics: eligibility opens summer 2027 if the All-NBA criteria hold (VERIFY criteria against his actual honors at that time). Signing multiplies subsequent hazard by a factor around 0.3 (TUNE) and improves departure salvage, but does not zero the hazard. Precedents for post-extension departure: Lillard extended in Portland in 2022 and requested out in 2023; Davis requested out of New Orleans mid-contract. A declined offer in July 2027 is the single loudest observable on the whole board, and the pre-committed response to it must be written before the season, because that node is where panic trades are born.

Ownership curves. The owner is the second human the model cannot see inside, and gets the same treatment as the star: two budget postures, tax_tolerant (base case, per July 2025 reporting that the new owners were prepared to keep paying the tax) and tax_averse (hard aversion to repeater rates), with every recommended move re-derived under both and sorted into holds-under-both versus flips. An observed dump executed at real asset cost is the loudest update toward tax_averse and triggers an immediate re-solve.

## 5. Decision calendar, July 2026 through July 2028

| Node | Date | Type | What happens |
|---|---|---|---|
| 0 | Now to Oct 2026 | Decision | Fill two roster spots at the vet min (frontcourt depth per need); two-way slots; LaMelo early-extension arm (default WAIT, preserves option value of one season of fit data; counterargument, his price rises if he plays well); LeBron stub resolves |
| 1 | Oct 31, 2026 | Decision | Rookie scale options: Shannon fourth year, Beringer third year (VERIFY dates); expected exercise |
| 2 | Oct 20, 2026 approx | Commitment | TRIPWIRES.md and jaden_markers.md freeze; season opens |
| 3 | Nov 27, 2026 | Read R1 | Advisory tripwire read, approx game 17 to 20 (AVAIL-PACE R1); Jaden markers read informationally |
| 4 | Dec 15, 2026 | Threshold | Offseason signees league-wide become trade eligible; practical open of trade season |
| 5 | Jan 10, 2027 | Read R2 | Binding tripwire read, approx game 36 to 39 (AVAIL-PACE R2); also league guarantee date window (VERIFY exact date) |
| 6 | Early Feb 2027 | Decision | Trade deadline. Arms per tripwire spec: WAIT default, ARM-G guard depth, ARM-B frontcourt, ARM-S staggering (free). Matching salary Green and DDV. Over-apron rules: 100 percent matching, no buyout signings above the midlevel line. UNLOCK and ARM-D available here (see section 6) |
| 7 | Apr to Jun 2027 | Chance | Playoffs. Outcome updates run, feeds the hazard. This is the milestone lever: a deep run is worth equity through retention, not just glory |
| 8 | Jun 2027 | Decision | Draft. No picks owned; second-round purchases if inventory and rules allow (VERIFY) |
| 9 | Jul 2027 | Decision layer | Hard cap expires. Green and DDV roughly 27.6M come off the books. Gobert enters his expiring year, the largest matching salary of the whole window. Ant supermax window opens, offer decision plus his response, the first clean read of the clock. Jaden tier assignment (2026-27 season-end) feeds the extension node. LaMelo extension arm again. Own free agents (Hyland, Lyles). Midlevel status recomputed. Tax and repeater posture set for 2027-28 |
| 10 | Oct 31, 2027 | Decision | Next rookie option cycle (Beringer fourth year, Evans, others VERIFY) |
| 11 | Nov 2027 to Jan 2028 | Reads | Season two tripwire cycle; re-run the backtest freeze for the new roster context before the season (new TRIPWIRES revision) |
| 12 | Early Feb 2028 | Decision | Trade deadline two. Gobert expiring is the hammer. NOTE: still zero tradeable firsts unless UNLOCK was executed, because the Utah 2029 obligation keeps Stepien binding. If unlock_done, the 2028 first (post-swap value) is advance-tradeable here |
| 13 | May 2028 | Chance | Lottery. Charlotte swap on the 2028 pick resolves after positions are set; pick2028_status flips to resolved_kept or resolved_swapped |
| 14 | Jun to Jul 2028 | THE GATE | Draft night: first fully tradeable first materializes (whatever survived the swap). Then the July layer: Ant answer due if not resolved in 2027, LaMelo entering walk year (extend or expose), Jaden entering walk year (same), Gobert contract resolved (re-sign, sign-and-trade, or walk), war chest partially re-armed. Five doors, one hallway. Every branch of the board funnels through this node |

Dead-end amplifier to draw on the board: if the 2028-29 season craters and the 2029 pick lands top five, it does not stay as lottery consolation; the Charlotte swap captures it (and if it lands six through thirty it conveys to Utah). The tank branch has no salvage in 2029. Rollover terms of the Utah protection if unconveyed: VERIFY.

## 6. Special actions: UNLOCK and ARM-D

Acquiring any 2029 first-round pick, from any team, at any node, plugs the potential 2029 hole and restores the legality of advance-trading the own 2028 first (still subject to the Charlotte swap haircut in valuation). Cost: whatever the market charges for a late 2029 first. Benefit: converts the 2028 pick from a June 2028 asset into a deadline-usable asset five months earlier, at node 12. This is a pure option purchase and the solver should price it explicitly: compute board value with and without UNLOCK executed at each affordable node, and report the spread. If the spread never exceeds the market price of a late first, UNLOCK dies quietly and the piece says so.

ARM-D, the dump. A generic salary-shed template, instantiated per contract, with the DiVincenzo expiring as the first case. Value side: tax savings at the applicable rate, plus, decisively, the repeater reset if the dump is what carries the team under the line for the season, which reprices every tax dollar spent in the gate years at standard rates instead of repeater rates. Cost side: the sweetener the market charges to absorb an injured expiring, the amputation of aggregate matching (Green plus DDV at roughly 27.6M is the only doorway to a midsize deadline acquisition; Green alone is 14.7M), and the loss of his return in healthy branches, since Achilles timelines put him back on the floor around the stretch run at zero acquisition cost. Expected behavior: fires rarely, mostly in branches where the tripwires are green and no acquisition is coming. If the real front office executes a dump at asset cost, treat it as revealed preference on the ownership curve and re-solve.

## 7. Standing orders

The state vector is egocentric, so events that expand the menu rather than move the dials cannot be pre-solved as calendar nodes. They get standing orders instead: pre-committed protocols for unschedulable event classes, frozen with the October freeze and edited only with logged justification. Each order names its trigger and its first-week actions, and every one ends the same way: re-solve the board from the new position.

STAR-AVAILABLE. Trigger: a consensus top-15 player becomes gettable. Protocol: run the package through the trade model and the board for the equity delta, against a price ceiling table written in advance and keyed to the current state (what the chest can spend, by perf band and clock position). The ceiling exists to protect against the December version of us. No bid above ceiling, and the ceiling is revisable only at a scheduled re-solve, never during the courtship.

OWN-INJURY. Trigger: a rotation player is lost long-term. Protocol: disabled player exception checklist, the depth ladder for that position from the pre-scoped target lists, and an out-of-cycle tripwire read, since the injury may have moved the state across an action threshold.

MELO-REQUEST. Trigger: LaMelo asks out. Survivable by design, which is why it is an order and not an absorbing state: three years of team control means no forced timeline. Protocol: no reactive sale, market only at peak leverage windows (draft week, early free agency), salvage floor set by the trade model before any call is taken.

CONTENDER-COLLAPSE. Trigger: a rival starts selling veterans midseason. Protocol: the windfall shopping list, refreshed at each read date by archetype of need, so the front office is a prepared buyer inside 48 hours instead of a browsing one.

OWNERSHIP-SHIFT. Trigger: any observed action or directive implying a budget posture change, in either direction. Protocol: update the ownership curve, log the evidence, re-solve, and re-sort the holds-under-both pile, since moves that were unconditional may no longer be.

## 8. Transition model mapping

| Moving part | Powered by |
|---|---|
| melo_avail transitions | Interim: the prior-three-season median baseline (47 games) plus the Scenario B reference-class mapping; the in-season read is AVAIL-PACE, threshold derived (trip toward ARM-G if LaMelo is available in 12 or fewer of the first 20 games at R1, 23 or fewer of 37 at R2; baseline-conditioned, see `phase3_avail_pace_derivation.md`). Later: the real per-player availability posterior (build spec in `phase0_avail_pace_redefinition.md`, scheduled on this board's roadmap, its actual customer) |
| perf given roster | Joan Bet Monte Carlo (roster to win distribution to seed band) |
| run given perf | Joan Bet playoff and championship simulation |
| fit transitions | Priors from tripwire backtest Phase 3, updated in season by fitengine shrunk posteriors. Settled: AVAIL-PACE wire-eligible with a derived threshold. Pending final Phase 1 panel results: PAIR-DRTG and FC-DRB reliability, per the pre-staged decision rule (a metric that clears r(25) >= 0.50 proceeds as a wire candidate; otherwise it demotes to dashboard). SPACE-ANT is dashboard-only (gap G4: no wide-open/defender-distance data exists in the warehouse) |
| jaden transitions | The tier markers in `jaden_markers.md` (defensive gate JD-LOAD/JD-COVER/JD-HOLD, offensive ladder JO-EFF/JO-FLOOR/JO-GROWTH), computed at season end, read informationally at R1/R2. Thresholds calibrated on the section-5 calibration class (queued). This dial feeds the July 2027 extension node and the 2028 gate, NOT the February deadline |
| ant transitions | Patience curve (section 4) reading solver forward equity |
| Action legality | Joan Bet CBA feasibility gating (aprons, matching, Stepien, hard caps) |
| Counterparty realism | partner_acceptance.decide() boolean verdict plus required sweetener price for every trade arm target list, carrying the acceptance model's documented caveat that marginal deals are least reliable |
| Equity values | Backward induction over this state space, leaves valued by the championship sim |

## 9. Build order

Step one, encode the calendar and state space and print the reachable state count. Step two, wire the transition stubs with placeholder probabilities and verify the backward induction runs end to end on fake numbers. Step three, replace stubs with real machinery one variable at a time (availability first, it is already built; then perf via Joan Bet; then the hazard). Step four, price UNLOCK, the LaMelo early extension, and the loyalty premium (the board solved cold versus solved with a keep-Jaden constraint, with the same machinery run backward over the Towns and Reid trades as the audit mirror) as the first policy outputs, all answerable before opening night and each publishable on its own.

## 10. Open questions

Jaden tier markers: defined in `jaden_markers.md` with four tiers; thresholds TUNE pending the calibration class (section 5 there, queued) and the agent feasibility pass; freeze before October 20.

Granularity of perf (four bands versus six) and whether run should distinguish losing the Finals from winning the conference.

The exact repeater trigger year, 2026-27 or 2027-28, pinned against the CBA text in config.

Second-round inventory: fill in from the warehouse ledger before step one.

Whether melo_deal needs a REQUESTED level of its own (LaMelo asking out is survivable in a way Ant asking out is not; currently it would be handled as a chest and roster event in the sim layer rather than an absorbing state).
