# Trade Model Spec, Phase 2: Partner Reaction Realism

Author note for the agent: no em dashes or en dashes anywhere, including code comments. Use commas, periods, or parentheses.

## Goal

Make "would the partner say yes, and what would it cost" reflect each team's real situation: their needs, their cap and apron pressure, how desperate they are, how many other suitors a player has, and any news-driven motivation. Build on the existing layers, do not duplicate them. You already have posture, the absorbs_dumps / over_apron_cutter / floor_seeking flags, the 6-dimension need vector, surplus, the sweetener ladder, and a real CBA engine. Phase 2 adds four things on top.

Hard rule that defines the whole design: compute the urgency you can defend from data, source the motivation you cannot, and never let the model synthesize a news signal from box scores. Anything not computable and not sourced stays neutral.

Dependency: this assumes Phase 1 (the untouchables override and the returning-star health correction) has landed, because the urgency layer reads the health-adjusted projected wins.

---

## Component A: Computed urgency and leverage layer

New build script `build_urgency_layer.py`, writing two files that sit beside the existing data foundation:
- `team_urgency.csv`, one row per team.
- `player_market_heat.csv`, one row per available player.

Normalize every signal to a league z-score or min-max so the downstream multipliers are well behaved, and document the scaling. Keep the existing posture and the three flags, derive them from thresholds on these continuous signals for back-compat.

### A.1 Per-team signals (team_urgency.csv)

1. `shed_pressure` (eagerness to dump salary). Continuous function of distance over the tax and aprons, using the lines already in `evaluate_move.py` (tax 201, first apron 209.1, second apron 222, in millions for 2026-27). Weight each band more steeply than the last, because the second-apron penalties are the harshest:

   ```
   shed_pressure_raw = w1*max(0, sal - 201) + w2*max(0, sal - 209.1) + w3*max(0, sal - 222)
   # w1 < w2 < w3, then normalize across the league
   ```

   High shed_pressure means the team is eager to offload, will attach sweeteners, and is more willing to move a good player if the deal nets salary out. This is the continuous version of over_apron_cutter.

2. `win_now_pressure` (eagerness to acquire an upgrade). Function of projected wins (use the health-adjusted projection from Phase 1, not last year's record), a minutes-weighted roster age, and a window term that spikes for teams that just fell one step short (lost in the conference finals or Finals) and for teams with an aging star whose window is closing. High win_now_pressure means the team tolerates giving up more and accepts thinner incoming value.

3. `asset_hunger` (eagerness for youth and picks). Continuous from the existing rebuild_score, replacing the binary "rebuilder counts picks." High for rebuilders and retoolers. Feeds a continuous pick-value weight in acceptance (Component C).

4. `expiring_risk` (motivation to sell before losing a player for nothing). Per team, the max over its valuable players of `consensus_net * (1 - resign_prob) * is_expiring`. `resign_prob` is a proxy from contract years left, the team's cap room, Bird rights, age, and role. Flag it as a proxy in the output. A high value means the team is a motivated seller on that specific player.

shed_pressure and expiring_risk push a team to give (sell or dump). win_now_pressure and asset_hunger describe what it will receive and how much it will pay.

### A.2 Per-player market heat (player_market_heat.csv)

Leverage and competition, the honest stand-in for a bidding war without simulating other general managers bidding:

```
need_fit(player, team)  = dot(player_archetype_vector, team_need_vector)   # both 6-dim
market_heat(player)     = surplus(player) * sum over teams of
                          max(0, need_fit(player, team)) * acquire_weight(team)
acquire_weight(team)    = g(win_now_pressure(team), cap_room(team))
n_suitors(player)       = count of teams with need_fit above a small threshold
```

Reuse the per-player 6-dimension contribution that already feeds roster_profile in `build_need_layer.py` as the player_archetype_vector. If only the aggregate roster_profile is exposed, expose the per-player version.

High market_heat means scarce and coveted, so a price premium. Low or zero heat combined with high shed_pressure or expiring_risk means a forced sale, so a discount.

---

## Component B: Sourced motivation overrides (the news axis)

Config `MOTIVATION_OVERRIDES`, or `data/motivation_overrides.csv`, same discipline as the untouchables override. This is the only channel for news-driven motivation.

### B.1 Schema

Each entry, at team or player level:

```
{ scope: "team" | "player",
  key: team_abbr or player_id,
  type: "forced_seller" | "trade_demand" | "extend_or_trade" | "win_now_mandate" | "shopping" | "not_available_soft",
  magnitude: 0..1,
  source: required string (outlet + reporter),
  date: required ISO date,
  expiry: ISO date, default 6 weeks from date,
  confidence: "R" | "J" }
```

### B.2 Effects

- `forced_seller`, `trade_demand`, `extend_or_trade`: boost willingness to move the named player and soften the required return (a leverage discount). Example: Giannis at Milwaukee on an extend-or-trade footing flips him to available or speculative and drops his effective asking price.
- `shopping`: the team is openly moving a player, so he is available and his price softens. Example: Morant at Memphis.
- `win_now_mandate`: add to that team's win_now_pressure (owner pressure, title-or-bust).
- `not_available_soft`: a public "we are not trading him" that is not a hard untouchable. Raises the price and makes him speculative. Example: Kyrie at Dallas. Keep this consistent with the untouchables speculative tier, do not double-count.

### B.3 Non-negotiable rules

- Every entry requires a source and a date. No source means it cannot enter the table.
- Every entry has an expiry. Past expiry, the build ignores it and prints a warning. This stops a stale "available" signal from lingering after a player signs an extension.
- Low confidence applies a smaller magnitude.
- The model never generates a motivation signal from stats. Absent an entry, a team is neutral on the news axis and behaves only off the computed urgency layer.

---

## Component C: Urgency-driven acceptance and sweetener pricing

Refactor `partner_acceptance.py` so the fixed constants become functions of the team's urgency and motivation. Keep all three channels and the "any channel fires means yes" structure, and keep the existing blockers (for example, an incoming real player with consensus_net >= 1.2 still blocks the pure cap-relief channel).

### C.1 Thresholds become functions

- `SURPLUS_MARGIN` (now 0.6) becomes `surplus_margin(team, deal)`:

  ```
  required = BASE_SURPLUS_MARGIN
             - k1 * win_now_pressure(acquirer_side)
             - k2 * seller_motivation(outgoing_player)   # from forced_seller/trade_demand/shopping
  required = max(required, FLOOR)   # never accept pure value destruction unless a large explicit forced_seller applies
  ```

  A desperate acquirer accepts thinner value and tolerates giving up more. A motivated seller accepts less in return.

- `NEED_MARGIN` (now 0.12) scales with win_now_pressure: a win-now team weights filling a measured need more, so lower its need bar and raise the credit for a need fill. A rebuilder weights need less.

- Pick valuation in the Value channel: replace the binary "rebuilder counts picks" with a continuous `pick_value_weight(team) = f(asset_hunger)`. Rebuilders and retoolers weight picks heavily, contenders near zero. This is what keeps a correctly-labeled contender from ever rubber-stamping a picks-heavy lowball.

### C.2 Sweetener and required-return pricing

The sweetener ladder and the `drag * (1 + 0.4*(years-1))` pricing with PT_TO_SURPLUS 0.45 become heat-aware and pressure-aware:

- The price to pry a player loose scales up with his `market_heat` (more suitors cost more) and down with the seller's `shed_pressure` and `expiring_risk` (a forced or eager seller costs less).
- The cost to a team to absorb a dump scales down with its appetite for salary. A floor_seeking team (below the salary floor) may pay little or no sweetener to absorb salary, since it needs to reach the floor. Generalize the existing absorbs_dumps logic into this.
- When Minnesota targets a high-heat player, raise the rungs of the sweetener ladder and the required outbound by a market_heat multiplier. This is where "many teams want him, so he costs us more" enters Minnesota's cost.

### C.3 Related fix worth doing here

The risk haircut keys off only the single highest-value incoming piece, so a strong second player is invisible. While refactoring acceptance, consider extending the haircut to a blend of the top two incoming pieces. Mark as optional if it expands scope too far.

---

## Component D: Salary data hygiene (prerequisite, do first)

Acceptance and CBA matching are exact-number sensitive, and the current contract file is Pass-1 scrape quality with known errors (the Zubac-on-Indiana row).

- Replace the contract file with verified current salaries (Spotrac-grade).
- Add `validate_contracts.py`: check each team's total salary against a known cap-sheet total within tolerance, flag rows whose team assignment is stale (the Zubac-on-Indiana class), flag missing or duplicate players, and cross-check every player-to-team mapping against the current roster. Exit non-zero on hard errors.
- Gate the engine: refuse to score, or loudly flag, any deal touching a contract that failed validation, so a wrong number cannot quietly produce a "real" deal. This automates the Spotrac verify your findings doc already says every deal needs.

---

## Build order

1. Component D, salary hygiene. Everything downstream depends on it.
2. `build_urgency_layer.py`, producing team_urgency.csv and player_market_heat.csv. Reads the Phase 1 health-adjusted projected wins.
3. The motivation_overrides table, sourced.
4. Refactor `partner_acceptance.py` to read team_urgency, player_market_heat, and motivation_overrides, turning the constants into the functions in Component C.
5. Re-run with `--tier2`, then run the calibration and sanity checks below.

---

## Calibration and validation

> CLOSED OUT (2026-06-17). This section was attempted and is now out of scope. The realized-trade backtest was built and run (`backtest_harness.py`, `backtest_tune.py`); it proved the acceptance model is Minnesota-acquisition-specific and does not generalize to scoring arbitrary two-team trades (real-trade recall topped out at 16 percent because a general trade is zero-sum in surplus and these gates are tuned for Minnesota filling a need). So the Phase 2-C coefficients stay hand-set, validated only against the self-tests and the sanity checks below, and the realized-trade calibration is deliberately not completed. See `docs/acceptance_model_scope_and_limitation.md`. The section below is preserved as the record of what was commissioned.

This is how the thresholds stop being self-tuned. Your own findings doc flags that the acceptance constants were tuned against a handful of self-test deals, not realized trades. Fix that now.

- Realized-trade backtest. Feed the model the pre-trade league state for a sample of actual completed trades from the last one or two seasons. Check two things: the model would have accepted the deals that really happened (recall), and it does not accept obvious fleeces (precision). Tune k1, k2, the market_heat multiplier, and pick_value_weight on this set.
- Sanity checks. A forced-seller discount must not let Minnesota acquire a player for free. Market heat on a real star must produce a real premium. A floor-seeking team should accept salary it otherwise would not. A correctly-labeled contender should reject a picks-only package.
- Auditability. Every acceptance decision emits why: which channel fired, the urgency values used, and whether a motivation override applied along with its source and date. The board's no-deal and yes verdicts stay traceable, consistent with how the board already explains itself.

---

## Honesty guardrails (restate at the top of each new module)

- Computed urgency comes only from data: apron distance, projected wins, age, contract years.
- News-driven motivation comes only from the sourced override table, with mandatory source, date, and expiry. It is never synthesized from stats.
- Every new signal surfaces in the outputs with its inputs, so a reader can see why a team behaved the way it did.

---

## Acceptance tests

1. A team deep over the second apron shows high shed_pressure, attaches sweeteners, and will move a good player when the deal nets salary out.
2. A recent Finals or conference-finals loser shows high win_now_pressure and will pay a premium for a real upgrade.
3. A high market_heat player costs meaningfully more to acquire than a low-heat player of equal surplus.
4. A player with an expired motivation entry is treated as neutral, and the build warns about the stale row.
5. A contender labeled correctly (after Phase 1) rejects a picks-heavy package that a rebuilder would accept.
6. The realized-trade backtest hits target recall on actual deals without accepting flagged fleeces.
7. Removing the motivation_overrides table changes only the news-driven cases, leaving the computed-urgency behavior intact.
