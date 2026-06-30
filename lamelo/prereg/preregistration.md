# Pre-registration and prediction log: LaMelo Ball trade evaluation

STATUS: LOCKED 2026-06-25. All four open items resolved by Bobby and the
secondary-creator-unlock hypothesis registered (see the resolution note at the end).
Registered sections are not edited after lock; any change becomes a dated amendment.
The value of this file is that it is honest about what was committed before any model
output existed. No modeling has run and no title number exists as of this writing.

## Registration header

- Analysis name: Clean-room evaluation of the LaMelo Ball + Josh Green for Naz Reid
  and a pick package trade.
- Date and time registered: 2026-06-25.
- Analyst: Bobby (priors committed cold), build agent (engine, pushback, on/off
  proposal). Reviewer: Scott.
- Model version / commit hash: to be stamped at first run (clean-room project under
  `lamelo/`; no inheritance of fitted outputs from `core_max` or `offseason`).
- One-line estimands:
  - Q1 (decision grade, opportunity cost): the signed difference in the
    discounted-title-equity objective between the actual LaMelo arm and the best
    realistic alternative arm AT THE DECISION POINT, with assets then unspent.
    Reported ordinally only.
  - Q2 (state estimate): the current roster's P(title), P(reach Finals),
    P(reach CF), and seed distribution against the live field, plus the
    common-random-number paired delta from the pre-trade roster.
- Decision served: not a go or no-go (the trade is settled). The credibility of the
  published evaluation, and a reusable calibrated, falsifiable engine plus a graded
  track record.

## Registered inputs (the estimates that will not be retuned to taste)

| Input | Source context | Transport adjustments | Committed value | Uncertainty |
|---|---|---|---|---|
| LaMelo impact (import) | High-usage primary on non-competitive Charlotte, low-leverage minutes, not game-planned as a playoff threat. Raw impact computed in the impact layer from the frozen warehouse. | Usage compression next to Edwards; leverage jump; better teammates and spacing; playoff defense hunting a lead guard; availability. | Survival fraction 0.75 of measured impact | Band [0.50, 0.90]. Floor extended to 0.50 to admit the playoff-hunting and usage-compression scenario. The single widest term in the model. |
| LaMelo fit interaction | Same | Gobert-ceiling raise (rim pressure, lob gravity) registered as an UPSIDE fit scenario only, NOT in the center. Symmetric DOWNSIDE (point-of-attack defense hunted, Gobert dragged into space) registered as the fit-fails scenario. | Scenario-parameterized (fit-clicks / neutral / fit-fails) | Set in the interaction layer, plan section 5 |
| Reid impact (export) | Best non-Gobert big, real floor spacing at the five, depth that insulated against Gobert missing time. | Two registered parts: (1) impact and spacing lost; (2) fragility cost, modeled as a VARIANCE widening on the Gobert-availability shared factor (section 8), not a mean haircut. | Meaningful loss, two parts | Computed in impact + dependence layers |
| Green impact (import) | 3-and-D wing, role close to prior context, smallest transport adjustment. | Modest role/leverage/opponent adjustments. | Near face value | Computed in impact layer |

## Registered named hypothesis: the secondary-creator unlock (reported with its hedge)

Registered as a NAMED hypothesis so it surfaces as its own paired decomposition line
in the output, not buried inside the interaction math. The unlock and its hedge are
reported together; neither is shown without the other.

- The unlock (upside): LaMelo as a secondary scorer and passer raises Edwards'
  efficiency by letting him play off-ball, and raises Gobert's ceiling through rim
  pressure and lob gravity.
- The hedge (symmetric downside, attached): the Edwards-LaMelo on-ball usage
  collision when both initiate, and LaMelo's defense being targeted with Gobert in
  drop coverage.
- Reporting rule: the decomposition shows the unlock line and the hedge line as a
  pair, with bands, so a reader sees the bet and its cost side by side. This is the
  same symmetric, data-bounded discipline the fit term uses (plan section 5), now
  pinned as a headline-eligible structural finding rather than an internal term.
- Data to set the ranges: Edwards off-ball efficiency splits (the Q3
  catch-and-shoot work), two-initiator lineup nets league-wide, Gobert lob and
  rim-pressure synergy, and LaMelo point-of-attack defensive matchup data.

## Registered comp-selection criteria

- Q1 alternative arm: an ARCHETYPE, a veteran lead ball-handler acquirable for a
  similar or smaller package at the decision point, solving the same diagnosed
  lead-creator need (a Jrue-type fit deal stands in, reproduced as an external
  claim). Hand-picked by scouting judgment, past-tense decision-point framing, no
  model search. Plus hold-and-run-it-back.
- Reference class (Q0C, to be built): teams that added a second star onto a young,
  non-contender-tier core within a comparable window since 1997, matching loosened
  to target n of about 20 to 30, base rate reported as a Wilson or Beta interval,
  not a point. Outcome base rate and delta base rate kept distinct.
- Retrodiction Case 3 star-acquisition definition: a player acquired by trade in a
  sealed season who was an All-Star in either of the two prior seasons OR whose
  prior-season impact ranked top 40 league-wide, where the acquiring team played at
  least 20 games with him. Realized change measured primarily as on-court
  net-rating change. Power thresholds pre-registered (n at least 8 full power; 4 to
  7 reduced; below 4 inconclusive and no green light).

## Registered objective function

Two objectives, kept separate. Q2 uses only the on-court roster (no option value, no
regret). Q1 (decision grade), with `t` over the contention window `W` (swept short /
central / long as a Q1-only sensitivity, never a headline):

```
V(R) = sum_{t in W} d^t * E[ TE_t(R) ]   discounted title equity over the window
       - OV(picks_out, flex_lost)         option value surrendered
       - lambda * CR(R)                    catastrophic-regret penalty on the bad tail
R evolves non-stationarily: aging-curve drift (Edwards, Gobert, Ball, Reid/Green)
and year-to-year correlation via shared factors, not independent seasons.
```

Risk attitude: risk-averse on the catastrophic tail (LaMelo breaks down or busts AND
the team is capped out and pick-poor with no pivot), approximately risk-neutral on
title equity in the body, positive discount on time. `d`, `lambda`, and `W` are
swept forks.

## Registered reference class and base rate

- Reference class definition: as above (loosened, n target 20 to 30).
- Base rate: TO BE PULLED before modeling, reported as an interval. Not yet known;
  not invented here.
- Source: warehouse rosters and outcomes plus Basketball-Reference cohort
  reconstruction, sealed from any modeling fit.

## Falsifiable forward predictions (reality will grade these)

Grade dates: regular-season quantities at the end of the 2026-27 regular season
(about 2027-04-15); playoff quantities about 2027-06-30.

| # | Prediction | Quantity | Point | Band | Grade date | Status |
|---|------------|----------|-------|------|------------|--------|
| 1 | Wolves regular-season win total | wins | 54 | [46, 58] | 2027-04-15 | LOCKED |
| 2 | Final seed in the West | seed | 4 | [3, 5] | 2027-04-15 | LOCKED |
| 3 | LaMelo games played | GP | 63 | [44, 73] | 2027-04-15 | LOCKED |
| 4 | Ant-LaMelo on-court net (both on floor) | net rtg | +3.0 | [-2.0, +8.0] | 2027-04-15 | LOCKED (agent-proposed, accepted by Bobby) |
| 5 | LaMelo deep-playoff availability (if Wolves reach R2+) | plays the series | bold prior, to set | to set | 2027-06-30 | optional, to add |

Predictions 1, 2, 3 are Bobby's, committed cold. Prediction 4 is the agent's proposal
on the one term Bobby delegated, accepted by Bobby. The win floor (1) and the
games-played floor (3) were widened together because they are the same availability
risk. The "set numbers you would be willing to be publicly wrong about" rule governs
all of them.

## Post-hoc scoring (filled in after outcomes)

- Date scored:
- Brier or log score across graded predictions:
- Calibration note (were the bands honest):
- What this updates for the next analysis:

## Resolution note (2026-06-25): all open items closed, file LOCKED

Bobby resolved the four open items and added a registered hypothesis:

1. LaMelo games played: band widened to [44, 73], center 63 held. The floor admits
   the ankle-recurrence tail (his 2022-23 and 2023-24 were 36 and 22 games), which
   the regret term exists to capture.
2. Win total: band widened to [46, 58], center 54 held. The win floor moves with the
   availability floor; they are the same risk.
3. Ant-LaMelo on/off: agent proposal +3.0 [-2, +8] accepted.
4. Survival-fraction downside: floor extended to 0.50, center 0.75 held, to admit the
   playoff-hunting and usage-compression scenario.
5. Secondary-creator unlock registered as a named hypothesis with its symmetric hedge
   (see that section), reported as paired decomposition lines.

The file is LOCKED. The freeze, fingerprint, three-era partition, and sealed holdout
are set in `freeze_manifest.md`. Phase 2 (parquet snapshot export and the data layer)
proceeds from here.

## Amendment 1 (2026-06-25): actual trade structure is a four-team sequence

Discovered in Phase 2 that the headline ("Reid and a pick package for LaMelo and
Green") is not salary-legal: MIN cannot absorb $55.45M for Reid's $23.28M under apron
rules. Bobby confirmed the real deal is a four-team sequence (MIN, Brooklyn, Chicago,
Charlotte), encoded canonically in `lamelo/data/trade_definition.json`. MIN's net:

- OUT: Julius Randle AND Naz Reid (both), plus the pick package (2033 1st unprotected,
  2028/2029/2030 first-round swaps, 2029/2032/2033 seconds, and the No. 28 first).
- IN: LaMelo Ball, Josh Green, Mouhamed Gueye (near-minimum), plus the No. 33 second.
- Re-signed with cleared space: Ayo Dosunmu, 5 years / $112M.

Implications for the registered priors (the LOCKED values do not change; this records
how the actual structure is handled):

1. The deal removes BOTH Randle and Reid from the frontcourt behind Gobert. The
   registered Reid-out fragility prior (#3) STANDS as committed and is AMPLIFIED, not
   contradicted: losing both bigs is a larger structural hole than Reid alone, which
   widens the Gobert-availability tail further. Randle's departing impact is computed
   as its own transport (export) term in the impact layer; the committed Reid-out
   prior is not edited.
2. The option-value term (`OV` in the objective) is now anchored to the large pick
   package above (one outright unprotected 2033 first, three first swaps, three
   seconds, the No. 28), partially offset by the No. 33 in. This is the "spent the
   future" the catastrophic-regret tail prices.
3. Q1's opportunity cost is benchmarked against THIS asset outlay (Randle plus the
   pick package), not against Reid plus picks. The Jrue-type alternative archetype is
   judged as the realistic different use of the SAME assets at the decision point.

Open verification carried into the data layer: confirm CBA legality and the apron tier.
RESOLVED in Amendment 2 below. (An earlier guess in this paragraph that the deal stayed
under an apron with flexibility was WRONG and is corrected there.)

## Amendment 2 (2026-06-25): cap state verified, second-apron HARD CAP (binding constraint)

Computed MIN's completed-trade 2026-27 cap sheet from the frozen snapshot
(`lamelo/data_pull/min_cap_state.py` -> `lamelo/data/cap_state.json`), reproducing the
cap-analyst claim rather than accepting it:

- Post-trade salary about $211.4M for 11 committed players. Over the luxury tax ($201M)
  by about $10.4M (third straight tax year, repeater rates), over the first apron
  ($209.1M) by about $2.3M, and about $10.6M under the second apron ($222M).
- HARD-CAPPED at the second apron. Aggregating Reid + Randle to acquire LaMelo is the
  trigger. The $33.3M trade exception is forfeited and the full non-taxpayer MLE is
  unavailable. Only the taxpayer MLE (about $6.1M) and minimums remain, with about
  $10.6M and four spots to fill (realistically RFA Jaylen Clark plus minimums; thin at
  PF with McDaniels at the four).
- CORRECTION: an earlier reconciliation note read the Randle shed as keeping MIN under an
  apron with flexibility. That was the standalone-Randle framing. Folding LaMelo in is
  exactly what consumes the flexibility; the aggregation hard-caps them. This was a known
  failure mode (a wrong cap tier flatters the team), caught and reversed.
- DATA-SOURCE RULE: model the COMPLETED (post-2026-07-06) trade. The live tracker
  (Spotrac about $192M) is pre-official and would read under the first apron, which is
  wrong.

Why it matters (it cuts against the team, the honest direction): the second-apron hard
cap is the binding constraint on Q2 depth and on the Reid-out fragility term. The
frontcourt hole from losing BOTH bigs behind Gobert cannot be cap-fixed this offseason
(no exception, no full MLE). So the registered fragility prior sits at its AMPLIFIED end,
and the cap layer must not assume tools the team does not have.

## Amendment 3 (2026-06-25): transport operationalization and the metric-fork headline

After the impact and transport layers (`lamelo/impact/02_transport_findings.md`):

1. **LaMelo transport: operationalization B locked.** The 0.75 survival fraction is
   applied to his OFFENSE; his measured defense is carried in full under each metric (no
   second playoff-defense multiplier, double-count guard held). B is chosen because it
   makes his defensive risk legible on his OWN number rather than smearing it into the
   team aggregate. Transported net: RAPM +0.90 [-0.14, 1.53], box +1.41 [0.92, 1.70].
2. **The metric fork is run as TWO complete, internally consistent worlds, end to end.**
   Within each fork the SAME metric drives LaMelo's value, Reid's and Randle's losses,
   and the team-defense and Gobert-fragility aggregates. RAPM's LaMelo is never mixed
   with box's Reid. The two worlds are compared only at the output. This keeps the
   reported instability the real metric disagreement, not inconsistent wiring.
3. **The forks AGREE the change is small (robustness, not instability), and that
   agreement is the headline.** After the team-strength layer, the two forks do not flip
   between good and bad: both land small (RAPM trade delta indistinguishable from zero,
   box a small positive, and K-stable under the regression sweep). The metric choice
   decides "nothing" versus "barely positive," not "great" versus "terrible." So the
   robust conclusion is that the trade did not meaningfully change MIN's team strength,
   regardless of how it is measured. The no-cherry-pick rule still holds (both forks
   reported side by side, the YoY test could not separate them), but the framing is robust
   agreement on "small," not an unstable flip. The decision-grade story (Q1) carries the
   piece: a near-zero on-court change bought with a large pick package and a second-apron
   hard cap.
4. **Prior-learning note, in Bobby's words (the prior is NOT retuned, it stays locked):**
   "My committed 0.75 turns out to encode a box-score, defense-neutral view of LaMelo.
   Under RAPM his real survival is 0.46, not 0.75. I do not retune the prior, it is
   locked, that is the point. I register that I learned my 0.75 was a box-flavored bet,
   so when the forks split I understand why, and I am not tempted to call RAPM too harsh
   just because it disagrees with the number I committed. RAPM disagreeing with my prior
   is information, not an attack on it. The pre-registration did its job: it caught my
   assumption in daylight."

## Amendment 4 (2026-06-25): kill criteria FIRED, title number declined

The pre-registered retrodiction gate (Case 3, star-acquisition win-total) FAILED: on 8
clean offseason star acquisitions the engine got the sign wrong on the 3 fit-and-availability
cases (Kawhi-TOR, Gobert-MIN, Murray-ATL) and under-predicted the successes (5/8 sign, 2/8
within-4-wins). An additive impact engine structurally cannot model fit or availability,
which dominate star-acquisition outcomes.

Per the pre-registered kill criteria ("publish no probability if the retrodiction backtest
records a miss"), the precise title percentages (2.66% / 3.92%) are NOT published. The
qualitative, fork-and-fit-dependent finding is published. A fuller Case 3 reconstruction is
DECLINED: it would not rescue the fit-failure sign errors, and searching for a test that lets
the number through would be motivated reasoning. The gate did its job. Final deliverable:
`lamelo/DELIVERABLE.md`.

This is the project working exactly as designed: a falsification test, pre-committed before
the answer was known, fired, and the pre-committed consequence (no number) was honored. The
finding empirically validates the analysis's own structure (star outcomes are fit-dominated),
with Minnesota's own 2022 Gobert acquisition sitting inside the failure set as the warning.

## Amendment 5 (2026-06-26): independent red-team audit fired; five fixes applied

An independent audit verified the cap layer, the transport double-count guard, the CRN
implementation, the defensive sign convention, the SCALE/BETA application, the K-stability,
and the temporal seal as CLEAN (left untouched). It found two conclusion-level defects and
three smaller ones; all five fixes applied (and the per-file change list reported to Bobby).

- FIX 1 (headline): the RAPM "wash" depended on crediting Mouhamed Gueye (a near-minimum,
  low-sample-defensive-RAPM throw-in) at full shrunk value. Added a role-player valuation fork
  (`impact/sweep_gueye.py`): RAPM trade delta +0.003 (modeled), -0.56 (neutral), -1.12
  (replacement). Re-reported the defense-aware result as WASH TO MODEST NEGATIVE, not
  indistinguishable from zero. The same Gueye value props up the Gobert-fragility cliff (+4.00
  with, +5.89 without): one unreliable number flattered two results.
- FIX 2 (overclaim downgrade): the Case 3 failure does NOT prove additive models are
  structurally fit-blind; most misses are estimand mismatch (no outgoing-player subtraction, no
  availability, era-transported box map). Gobert-MIN is plausibly fixed by subtracting the
  outgoing package alone. The Amendment 4 claim ("empirically validates ... star outcomes are
  fit-dominated") is WITHDRAWN as overstated. The no-number decision RE-ANCHORS on the
  over-determined identifiability ground (the title-delta band crosses zero; spec section 20);
  Case 3 is secondary corroboration only.
- FIX 3: the pre-registered forward predictions (54 wins, 4-seed) exceed the model's own
  output (~46-49 wins, lower seed). The predictions are LEFT EXACTLY AS COMMITTED (cold priors
  for grading); a reconciliation line was added flagging them as above-model analyst priors,
  not the analysis's projection.
- FIX 4: the title-delta interval [+0.005, +1.113]pp is the inter-fork point spread ONLY;
  relabeled, with the true band (parametric inputs + role-player fork included) extending well
  below zero.
- FIX 5: `run_gates.py` clearance logic checked Case 3 POWER, not PASS/FAIL; corrected to
  reflect the actual FAILED result. Did not affect the published outcome (the number was
  already declined).

Net conclusion after the audit: a modest negative to a small positive, NOT identifiable to a
point, declined on identifiability grounds. The verified-clean layers were not re-litigated.
