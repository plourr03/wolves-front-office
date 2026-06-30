# Plan: the LaMelo fit decomposition (five levers). FOR REVIEW, not built yet.

Sequel to `lamelo/DELIVERABLE.md`, under the same analytical-rigor skill and kill-criteria
discipline. The trade evaluation concluded the on-court effect hinges almost entirely on
fit, and that the title delta is NOT identifiable. This project does NOT forecast whether
the fit works.

## The hard constraint (carried from the main project)

- FORBIDDEN: a single "P(fit works)" number, or any combined probability across levers. That
  walks straight back into the false precision we refused.
- The output is a MAP OF THE LEVERS: decompose fit into observable mechanisms, measure what
  the data can say about each as a RANGE, and name the early real-world signal that will tell
  us which way each is breaking. A clearly-marked unknown is a correct answer.
- Pre-register each lever's data source and its positive-vs-negative reading BELOW, before any
  numbers are pulled, so no read is retrofitted. This file IS that pre-registration.
- Small-sample comps are reported WIDE with N stated. No over-interpreting a handful of duos.

## Correlated-skepticism guard (levers 3 and 4)

Levers 3 (defensive exposure) and 4 (frontcourt fragility) BOTH lean on RAPM pricing Gobert's
rim deterrence that the box misses. That is ONE shared uncertainty, not two. Build a SINGLE
shared Gobert-defensive-value estimate (one central value, one band, reported once) and feed
it into both levers. Do not independently re-estimate it in each, or the same skepticism gets
double-counted. The two forks (RAPM-credits-Gobert vs box-does-not) are reported as a shared
fork across the pair, exactly as the main project's metric fork was.

## Data availability (probed 2026-06-26, so the plan promises only what exists)

- Synergy play-types: league-wide, 2013-14..2025-26, RS + PO, Offensive AND Defensive
  groupings (PnR ball-handler, isolation, spot-up, off-screen, cut, etc.). Feeds levers 1, 3.
- Tracking season: catch_shoot_* and pull_up_* splits, drives, touches, time_of_poss,
  def_rim_fga/fg_pct. Feeds levers 1, 3.
- Possession cache (2023-26) for clean two-man lineups; older duos need a team-level proxy
  (off-rating in both-played games). Constrains lever 2.
- nba_boxscore_matchups is Wolves-only, so league-wide hunting uses synergy defense, not it.
- nba_player_stats GP history + player_impact.csv (RAPM/box). Feeds levers 4, 5.

---

## Lever 1: Can Edwards play efficiently off-ball?

- Estimand: Edwards's scoring efficiency (eFG and synergy PPP) on OFF-BALL possessions
  (catch-and-shoot, spot-up, off-screen, cut) vs ON-BALL (pull-up, isolation, PnR ball-handler),
  as a delta; plus his current off-ball possession SHARE (which rises next to LaMelo).
- Data: synergy player play-types (Edwards by type, 2023-26 RS+PO); tracking
  catch_shoot_efg vs pull_up_efg. Anchor: a small comp set of high-usage wings who added a lead
  ball-handler (e.g. Mitchell when Garland arrived, Booker with CP3, Brown alongside Tatum),
  measuring whether their off-ball efficiency held.
- Method: Edwards's off-ball vs on-ball eFG/PPP, range across seasons; the comp wings' off-ball
  efficiency change. Report the range, not a point.
- Sample caveat: the "high-usage wing adds a lead guard" comp set is small (likely 5-8);
  report wide, state N. Edwards's per-season off-ball FGA is moderate.
- Positive read (pre-registered): Edwards's off-ball eFG is AT OR ABOVE his on-ball eFG, and the
  comp wings mostly held efficiency off-ball -> he scales off-ball.
- Negative read: off-ball eFG materially BELOW on-ball (he needs the ball), comps declined.
- Can't-tell read (pre-registered): if the off-ball/on-ball eFG gap is inside the noise
  (overlapping CIs across seasons) AND the comp set is too small to anchor a direction, the data
  cannot call whether he scales off-ball. Report the gap with its band and say so.
- EARLY SIGNAL: Edwards's catch-and-shoot eFG and off-ball PPP in the first 20 games, vs his
  career off-ball baseline.
- Identifiability: GOOD for Edwards (synergy + tracking are rich); the comp anchor is the weak
  part (small N).

## Lever 2: The Ant-LaMelo usage collision

- Estimand: for each high-usage two-initiator duo, the COMBINED two-man on-court offensive rating
  vs the additive expectation from their individual on-court rates (the synergy/collision term);
  then place LaMelo-Edwards in that distribution by profile, not by a predicted number.
- Data: duos' individual on-court off-rating (nba_player_advanced_stats, league-wide). Two-man
  (both on floor): possession cache for 2023-26 duos; team off-rating in both-played games as the
  proxy for older duos. Comp set: Mitchell-Garland, Doncic-Irving, Young-Murray, Booker-Beal,
  Fox-DeRozan, Morant-Bane, plus others in the tracking era.
- Method: each duo's two-man off-rating minus additive expectation; split the duos that worked
  from those that did not; name what separates them (off-ball shooting of at least one, a
  defensive/rim backstop, complementary vs duplicative usage). Place LaMelo-Edwards by those
  features. Report the SPREAD across the duos.
- Sample caveat: the duo set is small (~6-10) and two-man rates are noisy; report wide, state N,
  do not over-interpret. The older-duo proxy (team off-rating) is coarser than the cache.
- Positive read (pre-registered): LaMelo-Edwards's profile resembles the SUCCESSFUL duos
  (spacing, a backstop, complementary usage).
- Negative read: it resembles the FAILURES (Young-Murray, Booker-Beal: two ball-dominant, thin
  defense, limited spacing).
- Can't-tell read (pre-registered): if the two-man synergy term's spread across duos is wide
  enough that LaMelo-Edwards's profile lands in the OVERLAP zone (where both successes and
  failures occur), the distribution cannot separate which way it breaks. Report the placement and
  the overlap, not a verdict.
- EARLY SIGNAL: the Edwards+LaMelo two-man net / offensive rating in the first 20-25 games.
- Identifiability: individual rates clean; two-man noisy and small-N; the "what separates" read
  is partly structural/qualitative. Flag it.

## Lever 3: Defensive exposure (LaMelo's core risk)

- Estimand: (a) LaMelo's defensive cost as a PnR/isolation target (PPP allowed, percentile vs
  the league), (b) how much Gobert's rim protection mitigates the blow-by relative to an average
  backline. NET = perimeter cost minus rim save.
- Data: synergy DEFENSIVE play-types (LaMelo's PPP allowed as PnR ball-handler and iso defender,
  and possession share, 2020-26, league-wide); tracking def_rim_fga/fg_pct for Gobert's rim
  deterrence. Uses the SHARED Gobert-defensive estimate (correlated-skepticism guard).
- Method: LaMelo's defended PPP and percentile; the gap to an average defender = the per-target
  cost. Gobert's rim-FG%-allowed reduction = the backstop. Report the NET range under the shared
  Gobert fork.
- Sample caveat: LaMelo's playoff defensive sample is tiny (he has barely played playoff
  minutes); the "playoff intensification of hunting" is therefore weakly estimable and is flagged
  as a partial unknown, anchored on RS rates plus the general playoff-hunting literature.
- Positive read (pre-registered): Gobert's rim protection materially offsets the hunt cost (small
  net) AND LaMelo's iso/PnR defense is not bottom-decile.
- Negative read: LaMelo is bottom-decile PnR defender AND playoff offenses can drag Gobert into
  space (via LaMelo's man), neutralizing the backstop.
- Can't-tell read (pre-registered, MOST LIKELY to land here): LaMelo's playoff defensive sample is
  too tiny to estimate the playoff hunt cost, and the "Gobert pulled out of the paint" dynamic is
  not cleanly quantifiable, so the NET (perimeter cost minus rim save) cannot be called FOR THE
  PLAYOFFS. Then report the RS components as measured (his RS PnR-defense PPP, Gobert's RS rim
  save) and mark the playoff intensification and the net as a flagged unknown, not a forced sign.
- EARLY SIGNAL: opponent PPP when attacking LaMelo in PnR in the first 20 games, and the Wolves'
  rim FG% allowed in LaMelo-on / Gobert-on lineups.
- Identifiability: LaMelo's RS defensive PPP is estimable; the playoff intensification and the
  "Gobert pulled out of the paint" dynamic are the weak parts (partial unknowns, marked).

## Lever 4: Frontcourt fragility without Reid

- Estimand: (a) the non-Gobert defensive minutes' projected level with the ACTUAL available
  backup-5 (Reid AND Gueye gone; Beringer plus minimum signings), (b) the team's projected
  defense across a realistic range of Gobert games-played, tied to Gobert's durability base rate.
- Data: backup-5 defensive impact (player_impact.csv, with the Beringer small-sample caveat;
  replacement level for minimum signings); Gobert's GP history (durability base rate); the prior
  eval's cliff finding. Uses the SAME shared Gobert-defensive estimate as lever 3.
- Method: the non-Gobert lineup defensive level (shared Gobert value removed, best-available
  backup added); sweep Gobert GP across a realistic range (e.g. ~55 to ~78); report team defense
  as a function of Gobert GP. Note explicitly that Gueye (the prior cliff's backup) is being
  waived, so the realistic backup is worse than the +4.00 cliff implied.
- Sample caveat: Beringer's defensive RAPM is low-sample (the same unreliability flagged for the
  Gueye throw-in); report his contribution wide. Gobert's base rate is N=several seasons, clear.
- Positive read (pre-registered): Gobert's durability base rate is high (70+ games), so non-Gobert
  minutes are a small share, and a developing Beringer or a minimum vet keeps them tolerable.
- Negative read: Gobert at age 34 carries rising durability risk, and the non-Gobert minutes
  crater (the cliff, now wider without Gueye), so even a 10-15 game absence is costly.
- Can't-tell read (pre-registered): if the non-Gobert defensive level is dominated by Beringer's
  unreliable small-sample RAPM (so it cannot be pinned) and Gobert's durability range is wide, the
  defense-vs-Gobert-GP curve is too uncertain to call a magnitude. Report the curve with its band
  and flag it as range-only.
- EARLY SIGNAL: the Wolves' defensive rating in non-Gobert minutes in the first 20-25 games, and
  Gobert's games played / any absence.
- Identifiability: backup-5 level estimable (small-sample caveat); Gobert durability clear; the
  cliff magnitude inherits the shared Gobert fork (do not re-count vs lever 3).

## Lever 5: LaMelo availability (the most data-rich lever)

- Estimand: a DISTRIBUTION of LaMelo's 2026-27 games played (percentiles), reconciled with the
  committed forward prediction 63 [44, 73].
- Data: his GP history (51, 75, 36, 22, 47, 72); the recurrence base rate for his specific
  chronic-ankle profile; durability curves of comparable high-usage guards with ankle histories.
- Method: build the GP distribution from his recency-weighted history, an ankle-recurrence hazard,
  and the comp guards' curves. Output percentiles, not a point. Reconcile with 63 [44, 73].
- Sample caveat: his own history is N=6 seasons; the chronic-ankle-guard comp set is small. Wide.
- Positive read (pre-registered): the 72-game 2025-26 rebound and the comp curves center the
  distribution in the low-to-mid 60s (the committed 63 is reasonable).
- Negative read: the chronic-recurrence base rate (two sub-40 seasons in four years) pulls the
  median into the low-to-mid 50s, below the committed center.
- Can't-tell read (pre-registered): if his GP history plus the comp curves give a distribution
  wide enough that the median is indistinguishable across the positive (60s) and negative (50s)
  reads (the inter-quartile range spans both), report the full distribution and state the data
  cannot pin the central tendency tighter than that span.
- EARLY SIGNAL: games missed in the first 25 games (any ankle absence is the red flag); and a
  load-managed pattern (GP up, minutes down) vs a true-healthy pattern.
- Identifiability: GOOD (most data-rich). The comp ankle-recurrence base rate is the small-sample
  part (flag).

---

## Synthesis (no combined probability)

Rank the levers by SWING MAGNITUDE (how much each lever's measured range moves the on-court
outcome), determined FROM the measured ranges, not asserted. State which one or two are
load-bearing (most likely to decide it) and which are conditioning factors. Report them as a
ranked list of levers with their ranges and signals, NEVER multiplied into a single number.
Pre-plan expectation to test, not assume: availability (5) and defensive exposure (3) are the
likely load-bearers; the usage collision (2) decides the offensive ceiling; Edwards off-ball (1)
and the fragility (4) are conditioning. The build confirms or revises this.

## Deliverable layout

Five self-contained lever write-ups (each: estimand, data source, measured range, sample-size
caveat, pre-registered read, early signal, identifiability verdict), then the short ranked
synthesis. Each lever is potentially its own post. No combined probability anywhere.

## Decisions (RESOLVED with reviewer, 2026-06-26)

1. Build order: **Lever 3 (defensive exposure) FIRST**, then 5, 2, 1, 4. Build the hardest,
   most load-bearing, most data-constrained lever first so its limits are known before the rest.
   Hold for review after each lever.
2. Every lever gets a THIRD pre-registered read: "indistinguishable / can't-tell," the condition
   under which the data genuinely cannot call it either way. "Can't tell at this resolution" is an
   allowed and honest outcome, not forced into positive-or-negative. Committed per lever below.
3. Lever 2 duo sources: include BOTH the clean 2023-26 two-man data and the pre-2023
   team-off-rating proxy, clearly labeled, BUT weight the clean possession-level data more heavily
   in the synthesis. The proxy duos are DIRECTIONAL CONTEXT ONLY; a 2018 team-level proxy does not
   carry equal evidential weight to a clean 2024 possession-level number.
4. Lever 1 comp set: criteria-based and pre-registered (prior-season usage above a threshold, then
   a lead guard added). Commit the rule before pulling and take whoever it returns, even if awkward.
5. Shared Gobert-defensive estimate across levers 3 and 4: CONFIRMED. One shared uncertainty,
   estimated once, fed into both, reported once.

Hard constraint stands: no combined probability, no "P(fit works)" number, ranges and early
signals only, unknowns marked as unknowns.
