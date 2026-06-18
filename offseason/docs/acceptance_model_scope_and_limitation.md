# Acceptance Model: Scope and Calibration Limitation

Snapshot date: 2026-06-17. Author note: no em dashes or en dashes anywhere.

## The decision, up front

The partner-acceptance model (`partner_acceptance.decide`) is scoped to ONE use case: deciding whether
a partner says yes to a deal Minnesota proposes. It is NOT a general trade-acceptance engine, and it
should not be used or trusted to score whether two arbitrary teams would accept a trade between them.

The Phase 2-C coefficients stay HAND-SET. They are validated against the module self-tests and the
Phase 2 sanity checks, not against realized league trades. We tried to calibrate them on real trades
and the backtest proved the model does not generalize, so the realized-trade calibration is closed as
out of scope rather than completed. This document is the record of why.

## What the model is for (in scope, validated)

The trade board asks, for each of the 29 partners, "would this team accept the deal Minnesota is
offering." That is the model's job and it does it well enough for the board:

- The three channels (value / need / cap-relief) and the "any channel fires means yes" structure are
  calibrated for a partner reacting to a Minnesota proposal.
- The self-tests pass (UTA cashes out a vet, CHA refuses a dump it cannot absorb, BKN eats a dump for
  a priced sweetener, MIA takes Gobert on value, Kuzma prices above Randle).
- The Phase 2 sanity checks pass: a forced seller is not acquired for free, a high-market-heat star
  carries a real premium, a floor-seeking team absorbs salary it otherwise would not, and a
  correctly-labeled contender rejects a picks-heavy lowball.

So the board's verdicts (DEAL / NO DEAL, the accept channel, the required sweetener) are sound for
Minnesota's acquisition use case. Nothing in this document weakens that.

One live exception to "only ever a partner reacting to Minnesota": the Pass-2 three-team resolver
(`trade_search.pass2_resolve`) calls `decide()` on a non-Minnesota third team to absorb a Minnesota
salary dump, forced through the cap-relief channel only. That is a narrow, channel-restricted use (a
dump absorber, the same path the BKN self-test and the floor-seeker sanity check cover), not a general
two-team-trade evaluation, and Pass-2 surfaced no deal in the live runs. Treat those few rows as
inheriting the same un-calibrated-coefficient caveat as the rest of the board.

## What we tested, and what it found

We built a state-reconstruction backtest over real 2025-26 league trades to try to calibrate the
coefficients against deals that actually happened (`backtest_harness.py`, `backtest_tune.py`):

- Reconstructed each trade's pre-trade state (rosters as of the trade date, verified 2025-26 salaries
  with dead-money handling, posture and need vectors recomputed from the as-of-date roster).
- Labeled positives: 19 genuine two-team deadline trades (fit set) plus 11 offseason trades held out
  as a generalization check. Negatives: 60 synthetic fleeces (quality-for-scraps and
  redundant-archetype, one pair per team).
- Ran `decide()` from both sides; a trade counts as accepted only if both sides say yes.
- Fixed every harness issue first (verified salaries, the double-encoding repair, waive-and-stretch
  dead money, true two-team grouping, and restoring the dropped draft-pick compensation), then made
  the pick-to-surplus value a tunable knob and let the fit search it.

Result: real-trade recall topped out at 16 percent (fleece rejection 90 percent). The pick value fit
to its ceiling and recall still did not move, so picks are not the missing piece.

The failure-mode tally, per rejecting side, is the diagnosis:

- 12, value-negative side (zero-sum surplus). The dominant mode. A real trade is value-positive for
  one team and value-negative for the other. The losing side gives up a known veteran's surplus for
  youth and picks, and even max-valued picks cannot offset a three-to-six-point surplus swing.
- 8, value-positive side blocked by a gate. Even the team gaining value rejects, because the value
  channel's fit gate (`best_recv_fit >= 0.30`, unless the team is a true asset collector with
  `pvw >= 0.5`) is tuned for Minnesota's "acquire a player who fills a measured need" pattern and
  blocks a general acquisition that fills no measured need.
- 1, unbalanced salary.

## Why it does not generalize

Two structural reasons, both consequences of the model being built for Minnesota acquiring, not for
arbitrary bilateral trades:

1. Zero-sum surplus. Player surplus in a trade is roughly zero-sum: one side gains it, the other
   loses it. Minnesota's use case is one-directional (Minnesota gives value plus picks to acquire a
   player), so the value channel only ever has to clear the acquiring side. A general trade needs the
   value-LOSING side to clear too, and the surplus-based channels cannot do that. Picks do not close
   it, because a single vague "draft consideration" cannot offset a star-sized talent swing, and
   because the model under-values the young and rookie players coming back (thin RAPM samples read
   near zero) and does not price the rebuild, timeline, or cap motives a real seller acts on.
2. Gate calibration. The value channel's fit gate and the need-margin floor are set for Minnesota
   filling measured needs. A general team often acquires a value-positive player who does not fill a
   measured need, and the gate blocks it.

Closing either gap is a real model change (a selling-side acceptance that prices youth, timeline, and
cap beyond raw surplus, and a relaxed fit gate for value-positive acquisitions), not a calibration.
It would change the board's behavior, so it is deliberately not done here.

## What this means for the coefficients and the board

- The Phase 2-C knobs (`K_WINNOW_VALUE`, `K_WINNOW_NEED`, `K_ABSORB_DISCOUNT`, `SURPLUS_MARGIN_FLOOR`,
  `NEED_MARGIN_FLOOR`), the heat star-gate (`K_HEAT_PREMIUM`, `HEAT_STAR_FLOOR`), and the news
  coefficients (`K_SELLER_DISCOUNT`, `K_SOFT_PREMIUM`) are hand-set and directionally reasonable, but
  un-calibrated at the margin.
- Read the board's MARGINAL deals (those near the accept/reject boundary, and the exact ranking among
  the middle of the pack) with that grain of salt. The strong deals clear regardless of the knobs
  (the identical top of the board across re-runs is the evidence).
- The board's structure (which partners say no and why, the accept channel, the required sweetener)
  is sound for the Minnesota-acquisition question it answers.

## The backtest artifacts (retained)

`backtest_harness.py` (reconstruction, packages, fleeces) and `backtest_tune.py` (decide-wiring,
tuning, leave-one-out, held-out check, failure-mode tally) are kept as the diagnostic that established
this scope. They are runnable for re-validation if the model is ever generalized. Their dependencies,
the verified-contracts salary source (`verified_contracts.py`, `nba_contracts_2026_27_verified.csv`)
and the rebuilt `team_state` apron, are NOT backtest-only: they are now part of the live pipeline and
benefit the board directly. The labeled trade set grows as `nba_transactions` stays fresh, so the
backtest is worth re-running if the model is generalized later.

## If you ever want to generalize the model

1. Add a selling-side acceptance path that prices youth, timeline, and cap relief above raw surplus
   for the value-losing side (the 12 zero-sum failures).
2. Relax the value-channel fit gate for value-positive acquisitions (the 8 gated failures), guarding
   precision against the synthetic fleeces.
3. Re-run `backtest_tune.py`. The harness is ready; it just needs the model changes, then fit the five
   knobs on the deadline trades and check the held-out offseason trades.
4. Re-validate `team_state` after June 30 first (pre-free-agency rosters move), per the team_state
   rebuild note, since the harness and the live board both read those totals.

## Related

- `partner_acceptance.py` carries a pointer to this document at the Phase 2-C coefficient block.
- `trade_model_spec_phase2_partner_reaction.md` is the Phase 2 spec; its calibration section is what
  this limitation closes out.
- `trade_board_findings.md` and `optimal_trade_board.md` are the board outputs whose marginal deals
  carry the un-calibrated-coefficient caveat above.
