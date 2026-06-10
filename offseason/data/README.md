# Offseason data: contract, free-agent, and draft-pick files

Pass-1 breadth data for the 2026 offseason series. Pulled by the scrapers in
`../scripts/` and enriched with a canonical join key. Read this before joining
any two files or summing any team's books. The traps below are the ones that
fail silently.

## Files

| File | Rows | Source | What it is |
|---|---|---|---|
| `nba_contracts_2026_27.csv` | 670 | HoopsHype | Every team's salary book, 2026-27 through 2029-30, with option flags |
| `nba_free_agents_2026.csv` | 238 | Spotrac | Everyone who could reach the 2026 market, by FA type |
| `nba_draft_picks_future.csv` (+ `.json`) | 609 | Spotrac | League-wide future pick ledger, 2027 to 2033 |
| `player_id_crosswalk.csv` | 908 | warehouse | The id bridge (see below). The load-bearing artifact. |
| `league_year_constants.json` | 5 seasons | NBA PR / reporting | CBA thresholds, exceptions, matching brackets, rule params as data |
| `team_state.csv` (+ `.json`) | 132 | derived | The rollup the feasibility module queries (see "The derived layer") |
| `tax_history.csv` | 120 | Spotrac/SalarySwish | repeater + frozen-pick input (30 teams x 4 prior seasons) |
| `team_trade_exceptions.csv` | 20 | Spotrac/SalarySwish | open TPEs (the team_state child table) |
| `nba_trade_comps.json` | 44 | reporting | comparable-trade database for grounding value ranges |

## The id problem (read this first)

There are THREE player-id namespaces and none of the scraped two reconcile to
each other or to the warehouse:

- contracts `player_id` is a **HoopsHype** id (6 to 7 digits)
- free agents `player_id` is a **Spotrac** id (4 to 6 digits)
- the warehouse, and every performance table (stats, RAPM, tracking, synergy),
  keys on the **nba_stats** id

A join on the raw `player_id` fails 100 percent (the two scraped sets share zero
ids). So both files now carry a **`nba_player_id`** column, resolved by name
against the warehouse player dimension. **`nba_player_id` is the only safe join
key** across these files and to the warehouse. Joining money to performance goes
through it.

`player_id_crosswalk.csv` is the auditable mapping: `source_system`, `source_name`,
`nba_player_id`, `nba_name`, `position`, `match_method`, `match_score`, `note`.

Match coverage: contracts 655/670 (97.8 percent), free agents 237/238 (99.6 percent).
Every rotation-level player resolves. The ~16 unmatched are deep-bench, two-way,
or out-of-league names (Rubio, McGee, undrafted rookies) with no NBA minutes in
2024-25 or 2025-26. They are left blank on purpose: a wrong id is worse than a
missing one, and there is no performance row to join to them anyway.

## Pipeline order

The enrichment is a post-scrape step, not part of the scrape:

```
python pull_nba_contracts.py      # or pull_nba_free_agents.py
python enrich_player_ids.py        # fills nba_player_id, position, and the flags
```

Always run `enrich_player_ids.py` after any re-scrape. The scrapers declare the
enriched columns (blank) so the schema stays stable, but only the enrich step
populates them. It needs the warehouse (reads `../../postmortem/.env`).

## Salary caveats

`salary_is_estimate = TRUE` flags **12** contracts that are flat and round across
multiple years (Jalen Johnson 30M x4, Dyson Daniels 25M x4, Jalen Green 36M x2,
Giddey, Patrick Williams, and others). These are HoopsHype simplifications. Real
deals escalate 5 to 8 percent a year. Salary matching is exact-number sensitive:
a package legal at the true cap hit can be illegal at a rounded one. **Before any
player enters a real trade scenario, verify the exact 2026-27 cap hit against
Spotrac.** That is the Pass-2 depth step.

Position on contracts is backfilled from the warehouse roster (627/670 filled;
the rest are stats-only matches with no roster position on record).

## The option-decision boundary (avoid double-counting salary)

A player with a 2026-27 option is under contract until the option resolves. Rule,
applied consistently across both files:

1. **`nba_contracts_2026_27.csv` is the single source of truth for money on a
   team's 2026-27 books.** An option is carried at its amount until resolved.
2. **`nba_free_agents_2026.csv` lists who COULD reach the market.** `fa_type`
   distinguishes them:
   - `UFA` / `RFA`: unconditional 2026 free agents. Not on any 2026-27 book.
   - `PLYR` (player option) / `CLUB` (team option): **conditional.** Free agents
     only if the option is declined. Until then they remain on the contracts book.
3. The free-agent file carries **`counts_on_books_until_declined`**: TRUE for the
   73 PLYR/CLUB players, FALSE for UFA/RFA.

So: sum 2026-27 team salary from the **contracts file only**; do not add FA-file
PLYR/CLUB players as extra cap holds. Build the available-FA pool from UFA/RFA by
default and pull in PLYR/CLUB only under an explicit "assume declines" scenario.

233 players appear in both files on `nba_player_id`. That overlap is expected
(HoopsHype lists a player on his team's page through his final year while Spotrac
lists him as a pending FA). Genuine source conflicts are negligible: exactly **1**
UFA carries a non-blank guaranteed 2026-27 salary (Bryce McGowens, a minimum,
likely non-guaranteed). Verify that one in Pass-2.

## Draft picks: control vs tradeable

`nba_draft_picks_future.csv` lists, per team, the picks that team currently
**controls** (its own plus picks acquired from others). A team's own pick that it
traded away appears in the **acquiring** team's section, not its own. So this is a
control ledger, not a tradeable ledger.

- **Round 2 is present.** 299 round-1 entries, 310 round-2 entries, every team has
  both. Seconds matter (they are the standard sweetener, and the Wolves' second
  cupboard is nearly empty).
- **`slot_span`** is the colspan hint: 30 means the whole round (unprotected or
  slot unknown, 525 of 609), a smaller value means a positional protection range
  (84 picks carry real protections, captured verbatim in `condition`).
- **`condition`** holds the protection / swap / conveyance text (332 entries). A
  human must read it before constructing a deal.
- 198 entries have `pick_origin` different from `controlling_team` (acquired or
  owed traces).

**What the feasibility module needs is tradeable, not controlled.** Deriving that
requires a Stepien-rule pass (no trading firsts in consecutive future years) plus
the seven-years-out limit, run against what each team already owes (derivable from
the origin-not-equal-controller rows, IF the ledger is league-complete). That is
the next module, not done here.

Open discrepancy to reconcile (flagged, not resolved): the plan doc calls the
Wolves' third chip a "2028 first-round swap," but the ledger shows MIN's 2028
first as their own outright pick with no swap, plus incoming/frozen picks the
"thin chest" framing omitted. Control vs tradeable (Stepien plus the 2027/2029
firsts owed to Utah from the Gobert trade) likely explains it. Reconcile against
ESPN asset rankings before the module trusts either count.

## The derived layer (team_state + constants)

This is the working object the feasibility module queries. It sits on top of the
raw files and recomputes from them, so every total is auditable and a scenario is
just a different roster fed through the same code.

**`league_year_constants.json`** (build it first; everything joins to it). 2025-26
is final; 2026-27 is the researched projection (cap ~$165M, tax ~$201M, apron1
~$209.1M, apron2 ~$222M, full MLE $15.048M); 2027-28 through 2029-30 are scaled
forward at 7%/yr (the CBA caps annual cap growth at 10%, so a strong-revenue season
could outrun this projection; revise when each year's cap is set). It carries the below-apron trade-matching brackets (200%+$250K up
to $7.5M, outgoing+$7.5M through $29M, 125%+$250K above) as data, the hard-cap
triggers, repeater params (3 of prior 4), and the frozen-pick rule. `confirm` flags
mark the three figures the rules reference says need a primary-source check before
publication (first-apron matching %, exact tax rates, frozen-pick window).

**`team_state.csv` / `.json`** (built by `build_team_state.py`). One row per
(team, season, scenario). It keeps **two salary bases** because the CBA compares
different lines to different totals, and conflating them mislabels a team:
- `apron_team_salary` = actual salaries (+ roster charges to 12). The TAX and
  APRON lines, and the taxpayer/first-apron/second-apron tier, are read off this.
- `cap_team_salary` = actual salaries + cap holds + charges. The CAP line
  (under-vs-over-cap, the room exception, `cap_room`, `distance_to_cap`) is read
  off this. A team can be low on the apron basis but over the cap once its own
  free agents' holds are added, so the under/over-cap call uses the cap basis.
  `potential_cap_room_if_renounced` shows the salary-only room a rebuild could
  open by renouncing those holds.

Base assumptions, all in the `assumptions` field: player options counted at value;
**team options counted only if at or below that season's full MLE (likely
exercised), larger ones treated as likely declined and excluded** (a ~$24M vet
option is shed, not kept), with the excluded amount in `team_option_declined_excluded`.

It reconciles: MIN base 2026-27 is $194.0M, within ~$1M of Marks's distances (under
tax ~$7M, first apron ~$15M, second ~$28M). Base case is all 30 teams x 4 seasons.
After the cap-basis fix, only BKN, CHA, MEM are genuinely under the cap; the rest
operate over the cap (full MLE, not the room exception). Borderline calls depend on
the cap-hold approximation (prior AAV), a Pass-2 precision item.

**Scenarios are subtraction-only baselines.** s1_randle_out, s2_gobert_out,
s3_both_out remove that salary and re-derive the tier. They show the roster floor
BEFORE the incoming piece: removing Randle drops MIN under the cap on paper, but a
real trade brings back matching salary, which the evaluator (not yet built) adds.
Read the scenario tier as "where the subtraction leaves them," not the post-trade
position. This is the schema's intent: the acquisition metric runs targets against
these rows.

**`tradeable_firsts` (v1 Stepien pass).** `tradeable_firsts_count` is the number of
own, OUTRIGHT (unconditional, unfrozen) firsts a team may legally trade now, where
removing one leaves no two consecutive future years (within 7 drafts) without a
first. The list returns everything controlled, tagged: own_outright, frozen_
untradeable, own_conditional_review (protected / swap / least-favorable), incoming,
incoming_swap. A human reads the conditions before constructing a deal. For the
Wolves this resolves the plan-doc discrepancy: their 2028 first is an OWN OUTRIGHT
tradeable pick (not a "swap"), and 2033 own is tradeable, so 2 clean tradeable
firsts, with 2027/2029/2031 incoming and 2029/2030 conditional flagged, and 2032
frozen. v1 limits: tests each pick independently (not combinations) and trusts the
ledger's control rows; full rigor needs the owed-pick reconciliation against a
league-complete ledger plus ESPN asset rankings.

**`tax_history.csv` + `team_trade_exceptions.csv`** feed `repeater_status` and the
TPE fields. Two things to know:
- TPE availability is **season-aware**: a TPE counts toward a season only if it has
  not expired before that league year starts (July 1). So a team's TPEs zero out in
  the seasons after they lapse, instead of persisting forever. Both
  `tpe_total_available` (sum of usable) and `tpe_max_single_available` are carried,
  because TPEs cannot be combined in one trade, so the per-trade absorb limit is the
  largest single exception (MIN: $10.77M Conley), not the $17.4M sum.
- `repeater_status` uses historical tax flags AND **projects the taxpayer flag
  forward** in the modeled seasons (taxpayer when projected apron salary clears the
  tax line), so the out-year cascade is not understated by a shrinking history-only
  lookback.

**Pipeline order:** `build_league_constants.py`, `build_tax_and_tpe.py`, the three
scrapers + `enrich_player_ids.py`, then `build_team_state.py`.

**`evaluate_move.py`** (schema section 7, built and self-tested 12/12). `evaluate_move(
team_state, constants, outgoing, incoming, pick_and_cash, exception_used)` returns
legal / illegal with the failing constraint in plain language, plus the post-move
apron, tier, and distances. It uses the tiered matching brackets from the constants
(not a flat percentage), routes exception signings/absorbs (TPE / MLE / BAE / room)
through an exception-bounded path with no salary matching, enforces no-aggregation
and no-take-back-more at the second apron, inflates incoming by any trade kicker
before matching, gates sign-and-trade and prior-year-TPE on their booleans, treats a
declined team-option player as un-sendable, and re-checks the hard cap against the
apron line AFTER the move lands. `evaluate_chain([...])` runs a two-stage star path.
Instructive result: a full-MLE signing lands MIN $40K under the first-apron hard cap
at base, but $5.95M over once Dosunmu is re-signed. This is Component 1 (the
feasibility gate) of the acquisition metric.

**Team-option intent** is an analyst input, not a magnitude rule: teams exercise big
team-friendly options on good players (OKC's Hartenstein $28.5M, Dort $17.2M) and
decline ones a player has fallen below. Team options default to counted (exercised);
only nba_player_ids in `TEAM_OPTION_LIKELY_DECLINED` (seeded with Kuminga) are
excluded. Refine in Pass-2.

## The value layer (Component 4: player impact)

**`player_value.csv`** (612 players), built by `build_rapm.py` from ~766K possessions
(`build_possessions_league.py`, all 30 teams, 2023-24..2025-26, RS+PO). A league-wide,
recency-weighted, box-score-informed 2-stage RAPM:
- First-pass ridge RAPM (CV-tuned alpha), then a box-score model learned by regressing
  those estimates on per-player box features sets each player's PRIOR mean (the
  in-house "box BPM"), then a second ridge shrinks toward that prior. Low-minute
  players are pulled toward a sensible box estimate, not to zero.
- Offense and defense are separate coefficients (`off_rapm`, `def_rapm`; def negative
  = good). `net_rapm` = off minus def.
- Intervals: analytical ridge posterior SD (`off_sd`, `def_sd`, `net_sd`). Bootstrap
  is a Pass-2 refinement.
- `box_net_bpm` is the in-house triangulation metric. corr(net_rapm, box_net_bpm) =
  0.77. `reliable` = TRUE when possessions >= 3000 (~a season of rotation minutes).
- The Synergy playoff read (`translation_read`, `rs_to_po_delta`) is merged in.

Validation: the top is Wembanyama, SGA, Jokic, Giannis, Kawhi, Gobert, with sensible
O/D splits, and the Wolves core matches the postmortem RAPM (Gobert elite defense,
Edwards offense-driven with weak defensive RAPM, Randle near replacement).

Honest caveats (carry these into any read):
- **Defensive RAPM collinearity:** backup bigs on good defensive teams (Edey, Diabate,
  Queta, Lively) ride inflated defensive net RAPM. This is the known RAPM
  identifiability limit, not a data error. Triangulate against `box_net_bpm` and treat
  defensive point estimates for low-usage bigs with skepticism.
- Intervals are analytical (ridge posterior), not bootstrapped. Wide bands (`net_sd`
  ~1.5 for stars, larger for low-sample players) are real uncertainty.
- Garbage time is filtered approximately (no clock in the possession data; 4th-period
  >25-point blowouts dropped).
- External triangulation DONE via `build_external_triangulation.py` (`player_value.csv`
  gains bbr_bpm/obpm/dbpm, consensus_net/off/def, impact_divergence,
  externally_corroborated). Independent Basketball-Reference BPM (box-based, league-wide,
  computed outside our pipeline) corroborates the spine: corr(net_rapm, bbr_bpm) = 0.74,
  offense 0.77, defense 0.66. The acquisition metric now scores on the CONSENSUS impact
  (0.6 RAPM / 0.4 BBR, z-blended) and marks a verdict provisional when the two methods
  diverge (externally_corroborated = FALSE). DARKO/EPM/LEBRON (plus-minus-based) remain a
  fuller Pass-2. Pulling BBR lifted Anthony Davis from RAPM +2.70 to consensus +3.60,
  which moved his board verdict off "pass" to "situational."
- The evaluator now models outbound trade kickers (inflate outgoing for matching, base
  for apron relief; Gobert 7.5% is wired into the Gobert-out scenarios) and no-trade
  clauses (a contingency flag, `ntc_waivers_needed`, not an auto-fail).

## The need layer (Component 3) and the assembled metric

**`player_dimensions.csv`** (462 rotation players) and **`need_vectors.csv`**, built by
`build_need_layer.py`. Each player gets a league percentile on six need dimensions
(half-court creation, secondary playmaking, off-ball shooting, defensive versatility
/ POA, rim protection / rebounding, transition) from Synergy, advanced, box, and
RAPM. The Wolves returning-roster profile is computed per exit scenario (DiVincenzo's
torn-Achilles absence baked in; a departed player's minutes filled at replacement
level), and the need vector is a playoff-calibrated contender benchmark minus that
profile. It validates: status_quo's top need is off-ball shooting (DiVincenzo gone),
gobert_out flips to rim protection / defensive versatility, both_out is broad and
anchored by rim protection. The same per-player dimension row is the target's profile
in the metric, so need-fit is a dot product in one shared space.

**`acquisition_metric.py`** assembles all four components for a target across the
exit scenarios: feasibility (the gate, via `evaluate_move` plus the apron/Dosunmu
reality and a comp-anchored asset read), contract/timeline, need-fit (with a role
adjustment so a wing does not fill a center-sized rim-protection hole), and impact
(RAPM with its band, the playoff read, an age multiplier). It writes a one-page
profile, a conditional verdict matrix, and a tier by a written rule to
`offseason/outputs/acquisition_profiles/<slug>.md`. Run:
`python acquisition_metric.py "Kawhi Leonard" --age 35`.

End-to-end test (Kawhi): infeasible at status_quo, stretch in the single-big
scenarios (salary-legal but breaks the Dosunmu apron math), feasible in both_out.
Overall "worth pursuing" via both_out, but flagged: he is an aging expiring rental,
his playoff half-court read slips, and the scenario that makes him affordable (both
bigs out) leaves the rim-protection hole he cannot fill. The gate, not talent,
separates the scenarios, which is the design working.

The full acquisition pipeline now runs end to end, with consensus impact and a
kicker/NTC-aware gate. Remaining Pass-2: bootstrap intervals, stronger defensive
shrinkage, plus-minus-based external metrics (DARKO/EPM/LEBRON), and the remaining
contract fields (guarantee dates, partial guarantees).

## Pair evaluation and the championship layer

There is deliberately NO standalone target-pair evaluator in the acquisition metric.
The "wing plus rim protector" companion-move problem (the asterisk on every both-out
wing verdict) is handled by the championship-impact layer
(`offseason/docs/championship-impact-layer-spec.md`), which simulates the actual
resulting roster and scores the pair as one team. The acquisition metric flags the
contingency; the championship layer resolves it.

The championship layer is built foundation-first per its spec: A (team-rating rollup,
`build_team_ratings.py`) and B (rotation/redundancy) first, validated against current
team ratings, standings, and win totals, then C (opponent profiles), D (series
resolver), E (bracket Monte Carlo). Hard rule from the spec: no trade is simulated
until the baseline title odds calibrate against win totals and the de-vigged preseason
boards. The three `*-preseason-odd.csv` files are queued for that Component E backtest.

## Not captured (Pass-2 manual fill)

Trade kickers, no-trade clauses, partial-guarantee dates, and Bird rights are left
blank in the contracts file. They are a targeted manual fill from Spotrac/Coon for
the ~30 to 50 players who actually surface in a scenario, not a full-league pull.
Dead money, likely-vs-unlikely incentives, and precise cap holds (currently proxied
by prior AAV, room-basis only) are the same kind of targeted Pass-2 fill.
