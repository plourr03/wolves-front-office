# TRIPWIRES.md

**DRAFT, 2026-07-17. NOT FROZEN.** This is the Phase 4 selection draft for review. It becomes binding only when frozen on the freeze date (see change control). Until then every number is amendable.

### Freeze-readiness checklist (must be cleared before the 2026-10-20 freeze)

- [ ] **Fresh contract + roster snapshot** for the ARM-G / ARM-B target lists, taken after the LeBron branch resolves and the two open roster spots are filled. The current draft target lists run on a stale 2026-27 snapshot (e.g. Reid still listed on MIN) and must be re-run against live rosters.
- [ ] **R1 / R2 game-count mapping verified against the actual 2026-27 NBA schedule** once it releases: confirm R1 (2026-11-27) lands at team game 17-20 and R2 (2027-01-10) at game 36-39. The wire thresholds are game-count based (12 of 20, 23 of 37, first-37), so the date-to-game-number mapping must be pinned.
- [ ] **Jaden markers calibrated and frozen the same date** (`../board/docs/jaden_markers.md`, feasibility confirmed in `jaden_markers_feasibility.md`; the calibration class is still queued). Same freeze, same change-control rule.
- [ ] **Hash-publication decision recorded** (Bobby's call): whether to publish the SHA-256 of the frozen file in October. If yes, compute and paste the hash at freeze.


Pre-registered deadline alarms for the February 2027 trade deadline node of the "If I Were Tim Connelly" master plan. The backtest behind every number is in `doc/` (`REVIEW.md` indexes it).

**What ships: one binding wire, plus advisories.**
- **AVAIL-PACE -> ARM-G**: the one binding wire. It fires an action.
- **FC-DRB -> ARM-B**: a structured advisory. It binds preparation and forces an adjudication, but does not itself fire the trade.
- **PAIR-DRTG, TOV-BLEED -> ARM-S**: dashboard advisories, non-binding, feeding the free staggering action only.

## Header: the arc (belongs in the frozen file)

Four candidate wires entered the backtest. The reliability and predictive-validity gates killed two (PAIR-DRTG and TOV-BLEED: reliability passed, but the co-star class of ~6 labeled cases could not power the predictive test). The subgroup split demoted a third (FC-DRB: its whole-team trip metric validates on the broad frontcourt-succession class, but not on the Wolves' own subgroup, disclosed below). One survived everything (AVAIL-PACE, on a 388-case class).

The single most important honesty note this backtest produced: **the situations most like ours are the least predictable.** FC-DRB's subgroup split makes this concrete. Teams that kept their primary anchor and lost the second without replacing it, which is exactly the Wolves losing Reid behind Gobert, are the noisiest subgroup, weaker than either teams that lost their primary or teams that replaced the loss:

| Subgroup | n | whole-team DRB persistence | verdict |
|---|---|---|---|
| Lost the primary anchor | 81 | 0.619 | validates |
| **Kept primary, lost second, no replacement (Wolves' case)** | 35 | **0.375** (CI to 0.05) | does not validate |
| Kept primary, lost second, replaced it | 65 | 0.665 | validates |

Everything here is a prior update, not a proof; the classes are small (roughly 8 to 400 cases). The model contains no private information: no medicals, no agent conversations, no locker room. That is the blind spot a real front office fills, and this file does not pretend to fill it.

**Design principle running through all of it: pre-commitment strictness scales with action cost.** Binding the costliest arm (a trade) requires subgroup-level validation; AVAIL-PACE has it, FC-DRB does not, so FC-DRB binds only the cheap and reversible parts (preparation, adjudication) and leaves the trade to human judgment. ARM-S costs nothing, so a dashboard whisper is enough to prompt it.

## Wire 1: AVAIL-PACE (binding) -> ARM-G

**Metric.** LaMelo Ball's games available (minutes > 0) through the Wolves' first N games, measured against his prior-three-season games-played median (47 games; the warehouse baseline, matching the YB3 label).

**Threshold (baseline-conditioned; see `doc/phase3_avail_pace_derivation.md`).**
- **R1, 2026-11-27 (advisory):** at risk if LaMelo is available in **12 or fewer** of the first 20 games.
- **R2, 2027-01-10 (binding):** fires if available in **23 or fewer** of the first 37 games. This wire is an exact count with no sampling noise, so it **may hard-trip at R2 alone** (it does not require an R1 flag first).

**What the wire means (cushion language, required).** Both trip lines sit just above LaMelo's on-plan pace (11.5 of 20, 21.2 of 37), so the wire stands down only if he **outperforms his own three-season history** by a small margin. This is deliberate and empirical: at his 47-game baseline he is under a 55-game contention bar about half the time and available for under half the playoffs, and early availability overstates final availability by a median ~6% (62 to 75% of comparable players pacing at plan early still finished below it). Hitting a low plan requires pacing ahead of it. A LaMelo who trips this wire projects to a median 23 to 26 game season, under 55 games ~90% of the time, available for ~30% of the playoffs; a LaMelo who clears it projects to a median 62 to 64 games and ~70% playoff availability.

**Sensitivity (logged, not baselined).** If his true availability plan is nearer the 63-game analyst prior than his 47-game history, the reads shift up to **15 of 20** (R1) and **31 of 37** (R2). State the wire at the 47-game baseline; keep the 63-game reads pre-computed for a mid-season revision.

**Arm.** ARM-G, backcourt insurance, matching salary built around the Josh Green (~14.7M) or DiVincenzo (~12.9M) expiring. Target list below.

**Evidence.** 388 comparable arrivals (players with a 2-of-4-season availability history). Early-pace-to-full-availability Spearman 0.77 at N=20, sign consistency 0.77, both above gate; reliability-exempt as an exact count. Strongest-supported wire in the library.

## FC-DRB: structured advisory (NOT a binding wire) -> ARM-B

FC-DRB is **demoted to a structured advisory** (ruling 2026-07-17). It does not fire the trade. The redesigned construct stands; only the commitment level drops, because binding the costliest arm requires subgroup-level validation and the Wolves' subgroup (retained_primary, 0.375-0.394, CI to 0.05, n=35) does not provide it.

**Trip metric (unchanged from the redesign).** Wolves **whole-team** defensive-rebound rate as a league percentile. Trip = bottom league third at a read. Derived from the whole-team scorecard: bottom-third at both reads is where P(the hole persists into the bottom third) first clears 0.5 (0.554). Binding-metric reliability r(25) = 0.619.

**Advisory teeth (these bind; the trade does not).**
1. **First trip at either read BINDS preparation.** On the first read (R1 or R2) that shows whole-team DRB in the bottom third, the ARM-B target list is refreshed through the acceptance model, price discovery is completed, and readiness is logged. This is cheap and reversible, so it binds: the front office must be a prepared buyer, not a browsing one, by the deadline.
2. **Trip at both reads triggers a MANDATORY adjudication memo before the deadline.** If the bottom-third trip holds at both R1 and R2, a memo is required that decides act-or-pass, argued against the pre-registered scorecard (all-team P(persist in bottom third) = 0.554) with the subgroup caveat stated (the Wolves' own retained-primary subgroup validates weakly, 0.375). The decision is logged in change control either way. **Silence is not an option**: the wire's teeth are that a both-read trip cannot be ignored, only adjudicated.
3. **Attribution (unchanged).** Gobert-off DRB frames the diagnosis: **Gobert-off red** frames the backup-big case (the hole is where Reid's absence bites); **Gobert-off green** flags an out-of-cycle review instead (team-level collapse with healthy anchor-off minutes implies a different cause than the Reid hole).

**Arm.** ARM-B, a backup big or rebounding forward, matching pieces (Green / DiVincenzo, or the aggregate ~27.6M). Target list below. The advisory prepares and adjudicates ARM-B; a human fires it.

**Provenance (full, retained; the marginal-wire label is moot for a non-binding advisory).**
- Trip metric reliability (whole-team DRB): r(25) = 0.619 across 330 team-seasons.
- Succession validity, broad class: lost-primary 0.619 (n=81, Fisher CI [0.464, 0.738]).
- Wolves-subgroup validity: retained-primary does **not** independently validate, whole-team 0.375 / anchor-off 0.394 (n=35, CI straddling ~0.05 to ~0.64). This non-validation is the reason for the demotion.
- Gate history: FC-DRB failed the original binarized sign gate (0.659 vs 0.70); the gate was amended to a continuous Spearman >= 0.59 for n >= 30 (arcsine translation; `doc/memo_signgate_amendment.md`). Moot for an advisory but recorded.
- Full basis: `doc/memo_fcdrb_redesign.md`.

## Default arm: WAIT

**WAIT is the explicit default.** If AVAIL-PACE does not fire and the FC-DRB advisory adjudicates to pass (or does not trip both reads), the pre-committed February action is to stand pat, develop internally, and revisit at the summer 2028 gate. This is written down as an action so that inaction in February is a decision made in October, not a failure of nerve. Note the asymmetry the advisory structure creates: AVAIL-PACE firing is a decision to act; the FC-DRB advisory tripping is a decision to *adjudicate*, whose outcome may still be WAIT, but only after the logged act-or-pass memo.

## ARM-S (free): advisory only, from the dashboard

ARM-S is the staggering action, restructuring the Ant and LaMelo minute overlap. It costs nothing, so its trigger bar is materially lower than the trade arms: it takes **non-binding advisory prompts** from the dashboard diagnostics, and a coach can act on a single suggestive read.

Dashboard diagnostics that prompt ARM-S (never binding, never a trade trigger):
- **PAIR-DRTG** (Ant+LaMelo shared-floor defensive rating). Passed reliability (raw r(25)=0.512 at the 350-possession floor) but its predictive validity could not be confirmed: the co-star class powers only 6 labeled cases, below N_GATE. Dashboard-only.
- **TOV-BLEED** (turnover bleed in LaMelo minutes). Passed reliability (0.665) but rests on the same 6-case class. Dashboard-only.

Rationale, one line: pre-commitment strictness scales with action cost, and ARM-S costs nothing, so a metric too thin to wire to a trade is still fine to whisper to a coach.

## Target lists (via the acceptance model, draft)

Generated by running each candidate through `partner_acceptance.decide()` (MIN acquiring, matching on the Green / DiVincenzo expirings), reporting the boolean verdict and the minimum sweetener (asset points) at which the partner accepts. Draft on 2026-27 contract data; finalize against live rosters near the deadline. Full run: `scripts/build_target_lists.py`, `data/target_lists.csv`.

**Marginal-deal caveat, carried verbatim from `offseason/docs/acceptance_model_scope_and_limitation.md`:**
> Read the board's MARGINAL deals (those near the accept/reject boundary, and the exact ranking among the middle of the pack) with that grain of salt. The strong deals clear regardless of the knobs (the identical top of the board across re-runs is the evidence).

Real-trade recall for this model topped out at 16 percent; it is a MIN-acquisition-specific plausibility screen, not a probability, and a target list lives exactly at the marginal boundary where it is least reliable.

**ARM-G (guard depth), illustrative draft candidates that cleared the screen:**
- Tre Jones (CHI, ~8.0M) — accepts at a 4-point sweetener, value channel.
- (Others screened NO-DEAL at <=12 points or need the Green+DDV aggregate; the list needs live-roster refresh, several 2026-27 salaries in the source set are stale.)

**ARM-B (backup big / rebounding forward), illustrative draft candidates:**
- Robert Williams III (NOP, via Green+DDV aggregate) — accepts at 0-point sweetener, value channel.
- Nic Claxton (BKN, via aggregate) — accepts at 0-point sweetener, value channel.

These are method demonstrations, not recommendations: the contract snapshot has known staleness (e.g. Reid still listed on MIN pre-departure) and the acceptance model is least reliable exactly here. The frozen file must re-run this against live rosters.

## Freeze and change control

- **Freeze date: 2026-10-20** (VERIFY: day before the opener). On the freeze date this file becomes binding and the February 2027 decision is executed against it.
- **Change control:** any edit after the freeze requires a logged justification appended to this file, with a date. No silent edits.
- **Change-control log (pre-freeze, disclosed):**
  - 2026-07-17: SIGN_GATE amended from binarized 0.70 to continuous Spearman >= 0.59 for n >= 30 (arcsine translation), after seeing the data, admitting FC-DRB. Both verdicts recorded. See `doc/memo_signgate_amendment.md`.
  - 2026-07-17: FC-DRB redesigned (post-draft). BEFORE: binding metric = Gobert-off (anchor-off) DRB percentile, admitted on the 0.617 whole-team number with a metric-definition caveat. AFTER: binding trip metric = **whole-team** DRB percentile (r25 0.619, validated on succession), threshold derived from the whole-team scorecard; Gobert-off demoted to the attribution read (route vs review). Subgroup split disclosed: the Wolves' retained-primary subgroup does not independently validate (0.375-0.394, n=35). See `doc/memo_fcdrb_redesign.md`.
  - 2026-07-17: FC-DRB **demoted from binding wire to structured advisory** (final ruling). Rationale: pre-commitment strictness scales with action cost; binding the costliest arm requires subgroup-level validation, which the retained-primary subgroup (0.375-0.394, CI to 0.05, n=35) does not provide. The redesigned construct stands; only the commitment level drops. File now ships ONE binding wire (AVAIL-PACE) + the FC-DRB structured advisory + the ARM-S dashboard advisories.
- **Optional, recommended for the article (Bobby's call):** on the freeze date, publish the SHA-256 hash of this frozen file publicly, so the February piece can prove the alarms were not chosen after the fact. Hash line to be filled at freeze:
  `SHA-256 (frozen 2026-10-20): <to be computed at freeze>`

## What is on the dashboard but never wired

Any three-point percentage (does not stabilize), clutch net rating (tiny noisy samples), raw win-loss vs expectation before R2 (schedule-confounded; use an SRS-adjusted view at R2 only), any specific five-man lineup net rating (possession counts too small), individual scoring averages (not decision-relevant), SPACE-ANT (no wide-open/defender-distance data exists in the warehouse), PAIR-DRTG and TOV-BLEED (reliability passed, predictive validity unconfirmable on the 6-case co-star class; they feed ARM-S advisories only).
