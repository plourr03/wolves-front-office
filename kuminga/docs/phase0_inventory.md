# Phase 0 inventory: Kuminga and the 2026 offseason, league-wide

**Status:** Phase 0 only. Nothing scraped, loaded, or modeled. Read-only inventory.

**As-of:** 2026-08-26. Warehouse read live the same day (daily refresh run_id 137, 03:33).

**Scope:** what data and models exist to evaluate the Jonathan Kuminga signing against all 30 teams' offseasons.

---

## A. Data we have

### A.0 Where the data actually lives

| Store | Endpoint | Status |
|---|---|---|
| Production warehouse | `nba_warehouse`, schema `nba`, Postgres 18 on the home server, over Tailscale | **LIVE.** 33 tables, ~26.5 GB. Read today. |
| Legacy local instance | `localhost:4101 / postgres` | **DECOMMISSIONED.** See Contradictions. |

The brief describes "the local warehouse at 127.0.0.1:4101 (rosters, injury reports, betting props)". That instance is documented as decommissioned and out of date in two places (`nba-warehouse/docs/database_inventory.md`, `nba-warehouse/specs/data_pipeline_spec.md`), and the analysis code is written to refuse to connect to it. A connection attempt today was rejected on authentication. There is one warehouse, not two, and it does not hold injury reports or betting props.

### A.1 Player box and advanced stats through the 2025-26 playoffs

**Complete.** This closes the gaps the last inventory (2026-05-14) recorded as open.

| Table | Rows | 2025-26 RS | 2025-26 PO |
|---|---|---|---|
| `nba_games` | 77,480 | 1,230 / 1,230 | 85 / 85 |
| `nba_player_stats` | 786,765 | 1,230 | 85 |
| `nba_player_advanced_stats` | 978,839 | 1,230 | 85 |
| `nba_team_advanced_stats` | 77,204 | 1,230 | 85 |
| `nba_play_by_play` | 17,788,239 | 1,230 | 85 |
| `nba_shot_chart_detail` | 2,857,820 | 1,230 | 85 |
| `nba_boxscore_matchups` | 1,989,448 | 1,230 | 85 |

The 2025-26 season is finished: last game 2026-06-13. New York beat San Antonio 4-1 for the title. Minnesota went 49-33, beat Denver 4-2, lost to San Antonio 4-2, eliminated 2026-05-15.

Two prior known gaps are now closed: `nba_player_advanced_stats` playoff coverage (was 0 of 66) is complete at 85 of 85, and the three missing playoff PBP games are loaded. `nba_boxscore_matchups` (per-possession defender-on-offender) was Wolves-only at 17,494 rows; it is now league-wide at 1.99M.

**Trap:** `nba_player_advanced_stats` carries one row per rostered player per game including DNPs. Kuminga has 65 rows for 2025-26, of which 23 are DNPs. Averaging without `minutes_float > 0` deflated his usage from .223 to .136 and his true shooting from .534 to .326 in a test query. Always filter.

### A.2 Play-by-play and lineup data for the four-view RAPM

- Raw PBP is complete and league-wide: 17.8M rows, 1997 through 2026-06-13.
- `nba_player_stints` is **not** lineup data. Despite the name it holds player-team tenure spells (`stint_start_date`, `stint_end_date`, `games_played`), 21,892 rows. It cannot support RAPM.
- The real lineup/stint layer is a derived parquet cache under `counterfactual-fit-engine/data/cache/`. On this machine it is largely absent: `possessions/` does not exist, `stints/` holds 1,569 games covering only 2019-20 and 2020-21, and `fitengine.duckdb` is absent. The README describes 15,668 games each. All of it is gitignored and rebuildable from PBP, but it is a rebuild, not a read.

RAPM on 2025-26 season-plus-playoffs is therefore feasible but not free. The raw input is complete; the derived possession and stint layer must be regenerated first.

### A.3 Rosters: current-dated, stale in content

This is the most dangerous item in the inventory. `nba_team_rosters` is refreshed daily and the latest `roster_date` is 2026-08-26 (today), 530 rows, 30 teams. The content is the 2025-26 roster. Every row carries `season = 2025`. The daily refresh is still pinned to the 2025-26 season and re-fetches the same rosters each morning.

Checked directly against the latest snapshot:

| Player | Warehouse says | Actually |
|---|---|---|
| Julius Randle | MIN | Brooklyn |
| Naz Reid | MIN | Charlotte |
| LaMelo Ball | CHA | Minnesota |
| Josh Green | CHA | Minnesota |
| Jonathan Kuminga | ATL | Minnesota (per the brief) |

The divergence is exactly four players on Minnesota: Ball, Green, Lyles, Evans are in the contracts table but absent from the roster snapshot. A `roster_date` of today over 2025-26 content will silently produce a wrong depth chart, a wrong minutes projection, and a wrong lineup fit. Do not use this table for 2026-27 rosters.

### A.4 Contracts and cap: better than expected

`nba_player_contracts` is live and current: `scraped_at` 2026-08-26 08:42, sourced from Basketball-Reference's contracts page. 1,070 rows.

| Season | Rows | Teams | Players |
|---|---|---|---|
| 2026-27 | 462 | 30 | 458 |
| 2027-28 | 321 | 30 | 318 |
| 2028-29 | 185 | 30 | 183 |
| 2029-30 | 89 | 29 | 87 |
| 2030-31 | 12 | 9 | 12 |

It carries `salary`, `option_type` (guaranteed / player_option / team_option), `remaining_guaranteed_total`, and `source_url`. It does **not** carry cap holds, dead money, exception inventory, hard-cap flags, or two-way contracts.

Unlike the roster table, it reflects the offseason: Ball, Green, Lyles and Evans are on Minnesota; Randle is on Brooklyn; Reid is on Charlotte. It confirms Dosunmu at 5 years / $112,000,000 exactly (19,310,345 / 20,855,173 / 22,400,001 / 23,944,829 / 25,489,652 player option) and Gobert's 2027-28 as a player option, not team-controlled.

Kuminga is still listed on Atlanta at $24,300,000 (team option). The signing is not in this table yet.

### A.5 Injuries: nothing

There is no injury table and no injury column anywhere in the schema. The only availability signal is `nba_player_advanced_stats.comment`, a per-game DNP reason ("DND - Injury/Illness", 744 rows since January). That is retrospective, game-level, undiagnosed, and it exists only while games are being played. There is zero offseason injury data.

It does not even cover the case we care about. DiVincenzo's last appearance was 2026-04-25 (1.32 minutes, Game 4 vs Denver) and after that he has no rows at all, not even a DNP row. The warehouse cannot tell you he was hurt; he simply stops appearing. The Achilles diagnosis and the post-All-Star-break timeline must come from outside.

### A.6 Betting props and futures: three seasons of history, nothing forward

No odds data in Postgres. On disk there are exactly three hand-collected files: `offseason/data/{2023-24,2024-25,2025-26}-preseason-odd.csv`, 29 teams each, with title odds, a season win total over/under, and the realized result.

That is a genuinely useful backtest set for calibrating model against market. It is not 2026-27 futures. There are no 2026-27 title odds and no 2026-27 win totals anywhere in the project.

### A.7 2026 draft: absent

`nba_player_bio` has draft classes through 2025 (55 players) and no 2026 class. Isaiah Evans, whom Minnesota signed, is not in `nba_player_bio` at all; he appears only in the contracts table ($1,357,763, with $6,346,496 remaining guaranteed). No 2026 draft results, no rookie scale table.

### A.8 Schedule: 2025-26 only

`nba_schedule` holds 1,405 games, all 2025-26, through 2026-06-19. There is no 2026-27 schedule. A schedule-based season simulation cannot run for 2026-27 without pulling it.

### A.9 Transactions: the pleasant surprise

`nba_transactions` is live through 2026-08-23 and covers the 2026 offseason league-wide: 309 legs since 2026-06-01, all 30 teams, 16 distinct trade groups. Types are Trade, Signing, Waive, ContractConverted, AwardOnWaivers.

Trades are grouped by `group_sort`, so multi-team deals are representable. The Minnesota deal resolves as one four-team transaction (`Trade 2026008`, 7 legs), not the two separate deals the brief describes:

- Charlotte receives Naz Reid (MIN), Mouhamadou Gueye (CHI), and "draft consideration" (MIN)
- Brooklyn receives Julius Randle (MIN)
- Chicago receives Nic Claxton (BRK)
- Minnesota receives LaMelo Ball (CHA) and Josh Green (CHA)

Two legs the brief does not mention: Claxton to Chicago, and Gueye to Charlotte.

Limits: no dollars, and picks appear only as an undifferentiated "draft consideration" row. The 2033 unprotected first, the 2028/29/30 swaps, the three seconds, and the 2026 first to Brooklyn are not enumerated anywhere in the warehouse. No Kuminga signing appears; the feed ends 2026-08-23.

### A.10 The anchor facts, checked against in-house primary sources

The brief asked that each anchor fact be re-verified against a primary source. Below is what the warehouse can settle on its own. The warehouse's two primary feeds are the NBA's official box scores (`nba_player_stats`, `nba_player_advanced_stats`) and the NBA.com transaction log (`nba_transactions`). Web verification of the rest is a separate pass.

| Anchor claim | In-house verdict | Evidence |
|---|---|---|
| Kuminga 2025-26: 36 games, 12.2 pts, 5.6 reb, 46.3% FG, 33.3% 3P on 2.9 att, 23.1 mpg | **VERIFIED, exactly** | Official box scores, regular season only: 36 GP, 12.2 / 5.6, 46.3% FG, 33.3% 3P, 2.92 3PA, 23.07 mpg (`minutes_float`) |
| Kuminga split between GSW and ATL | **VERIFIED** | GSW 20 games (2025-10-21 to 2026-01-22), ATL 16 games (2026-02-24 to 2026-04-30). He moved at the February deadline. |
| Randle to Brooklyn, four-team deal (BKN, CHI, CHA, MIN) | **VERIFIED, and larger than described** | `nba_transactions` group `Trade 2026008`, 2026-07-10, 7 legs. Confirms all four teams. Adds two legs the brief omits: Nic Claxton BRK to CHI, Mouhamadou Gueye CHI to CHA. |
| Ball and Green acquired from Charlotte for Naz Reid | **VERIFIED (players)** | Same transaction group. Reid to CHA, Ball and Green to MIN. |
| The pick package (2033 first, 2028/29/30 swaps, three seconds, 2026 first) | **UNVERIFIABLE in-house** | The transaction feed records one undifferentiated leg: "Charlotte received draft consideration from Minnesota." No pick detail exists anywhere in the warehouse. |
| Dosunmu re-signed 5 years / $112M | **VERIFIED to the dollar** | `nba_player_contracts`: 19,310,345 + 20,855,173 + 22,400,001 + 23,944,829 + 25,489,652 (PO) = $112,000,000 |
| Hyland and Clark retained | **VERIFIED** | `nba_transactions` 2026-07-03 and 2026-07-10, both "re-signed ... to a Contract" (standard, not two-way). Contracts: Hyland $2,845,883, Clark $3,086,420. |
| Isaiah Evans added | **VERIFIED (signing), origin unclear** | `nba_transactions` 2026-07-11, "signed forward Isaiah Evans to a Contract." He is absent from `nba_player_bio` entirely, so the warehouse cannot say whether he was drafted. |
| DiVincenzo torn Achilles, out into 2027 | **CORROBORATED, not diagnosed** | Last appearance 2026-04-25, 1.32 minutes, Game 4 vs Denver, then no rows at all for MIN's remaining 8 playoff games. `all-for-one/board/docs/board_spec.md` (2026-07-17) independently records "DDV ... injured (Achilles, expected to miss most or all of the season)". |
| Projected five: Ball, Edwards, McDaniels, Kuminga, Gobert | **4 of 5 on the books** | All but Kuminga appear on MIN in `nba_player_contracts` for 2026-27. |
| Kuminga signed with Minnesota, 2yr/~$12.4M, taxpayer MLE, PO in yr 2 | **NOT PRESENT** | Absent from `nba_transactions` (feed ends 2026-08-23) and from `nba_player_contracts`, which still has him on Atlanta at $24,300,000 as a team option. Requires external verification. |
| ATL declined his $24.3M option in June | **CONTRADICTED by the current scrape** | `nba_player_contracts`, scraped today, still carries the $24,300,000 ATL team option as live. Either the source has not updated or the option decision is not reflected. |
| Taxpayer MLE hard-caps below the second apron | **VERIFIED in-house, twice** | `offseason/data/league_year_constants.json`: `hard_cap_triggers.second_apron = ["taxpayer_mle"]`. `offseason/docs/nba-roster-rules-reference.md`: "Hard-capped at the second apron if you use the taxpayer MLE." Still worth a primary-source check. |

One thing the warehouse settles that the brief does not mention: the 2025-26 season is over. **New York beat San Antonio 4-1 in the Finals**, closing it out 94-90 on the road on 2026-06-13. Minnesota went 49-33, beat Denver 4-2, then lost to San Antonio 4-2. San Antonio is the same archetype the postmortem's Q4 cluster work flagged as the matchup this roster handles worst.

### A.11 The apron arithmetic, and why the Green deadline exists

This is computable today from live data, and it is the sharpest thing in the inventory.

Minnesota's 2026-27 committed salary, from `nba_player_contracts` scraped 2026-08-26: **$215,871,829 across 13 players**, ninth-highest in the league. Josh Green is $14,679,012 of it, fully guaranteed.

The project carries **two different 2026-27 second-apron figures**:

| Source | Second apron | Taxpayer MLE | As-of |
|---|---|---|---|
| `offseason/data/league_year_constants.json` (`is_projection: true`) | $222,000,000 | $6,065,000 | 2026-06-09 |
| `alebron/data/cap_state.json` ("VERIFIED 2026-27 thresholds") | **$221,686,000** | $6,064,000 | 2026-07-03 |

A $314,000 difference. It decides the whole question:

| Branch | Total | vs projected apron | vs verified apron |
|---|---|---|---|
| Keep Green + full TPMLE (14 players) | $221,935,829 | under by $63,171 — **legal** | over by $249,829 — **illegal** |
| Green out + full TPMLE (13 players) | $207,256,817 | under by $14,742,183 | under by $14,429,183 |

Even on the permissive projection, keeping Green leaves $63,171 of room with only 14 players signed; a 14th-man minimum (~$1.36M) breaks it. On the verified number, the signing is simply illegal while Green is on the books.

**That is the mechanism behind the August 29 deadline**, and it reconciles a contradiction that would otherwise sink the analysis: the project's two most recent cap reconstructions both concluded Minnesota could not use the taxpayer MLE at all. `alebron/data/cap_state.json` records `taxpayer_mle_added ... legal: false`, over the hard cap by $4,002,232. `all-for-one/board/docs/board_spec.md` records "veteran minimum is the only signing tool ... no midlevel." Both assumed Green stayed. **Shedding Green is what creates the exception.**

A caveat on the stretch branch. Green has one year left, so the stretch is over three years (2 x 1 + 1): about $4,893,004 per season of dead money in 2026-27, 2027-28 and 2028-29. That clears 2026-27 comfortably but puts dead money on the books in the same years as Gobert's player option and the start of Edwards's supermax window.

**Note the propagation problem.** The verified thresholds appear in only two files, both under `alebron/`. The engine's own constants file, which the CBA gate and `build_team_state.py` read, still carries the June projection. Whatever the true figures are, they need to be re-verified against a primary source and pushed into `league_year_constants.json`, or the feasibility gate will keep answering on stale numbers.

---

## B. Models we have

Four engines matter. None has been run since the offseason actually happened. Last run dates: core_max **2026-06-22**, offseason **2026-06-17**, lamelo **2026-06-26**, alebron **2026-07-03**, pick2033 **2026-07-13**, fitengine **2026-07-06**, all-for-one **2026-07-18**.

### B.1 The championship engine (offseason/scripts/bracket_sim.py)

This is the shared spine. `core_max`, `lamelo`, `alebron` and `all-for-one` all import it.

**It is already an all-30 engine.** `build_2026_27_league(imp)` returns a strength dict keyed by all 30 tricodes, and `simulate_league()` returns title, conference, and reach-R2/CF/Finals probabilities plus a simulated win total for every team on every call. `lamelo/sim/run_sim.py` already computes the full 30-team result and then persists only `["teams"]["MIN"]`.

So the all-30 before/after table the brief asks for is, on the output side, a low-effort change: persist the other 29 keys.

**The real limit is on the input side.** Only five of 30 teams get any 2026-27 roster adjustment:

```
MOVED           = {"MIA", "MIN", "BOS"}     # a modeled move delta
HEALTH_REBOUND  = {"ORL"}                   # anchored to a healthy rollup
RETURNING_STARS = {"IND"}                   # Haliburton, pre-injury anchor
```

The other 25 sit at their measured 2025-26 net rating, regressed to expectation, with delta 0. They are assumed to have stood pat. The projected rotations that drive the five adjustments come from `opponent_rosters.json`, a hand-authored 12-team contender set with narrative `assumed_moves`.

Those assumptions were written in June 2026 as predictions of an offseason that has since happened. The transaction log now shows 309 legs and 16 trade groups across all 30 teams. Running the pipeline "identically on all 30 teams" means projecting 18 more rotations and replacing 25 stand-pat assumptions with real ones. **This is the single largest gap in the project.**

One useful de-escalation: the season sim is not schedule-based. Win totals come from a calibrated regression (`wins = a + b * net + noise`), so the missing 2026-27 schedule does not block it.

### B.2 The value spine: Kuminga is already valued

No new player valuation is required to produce a first number. He is already in both impact tables:

| Source | Metric | Value |
|---|---|---|
| `offseason/data/player_value.csv` | consensus net | **+1.33** (off -0.53, def -1.86) |
| same | RAPM | net +1.37 (off -1.16, def -2.53), 17,935 poss, `reliable=True` |
| same | box | `box_net_bpm` +0.07, B-Ref BPM -0.89 |
| same | playoff translation | **"slips"**: half-court PPP 0.888 RS to 0.800 PO, delta -0.088 |
| `offseason/data/darko-dpm-leaderboard.csv` | DARKO DPM (2026-06-10) | **-1.0** (O -1, D -0), value $8.6M |
| `offseason/data/player_surplus.csv` | surplus at his $24.3M ATL option | -0.12 net, par $25.3M, flag `neutral` |

**The four views disagree about Kuminga more than they agree.** In-house consensus has him a positive (+1.33); DARKO has him a negative (-1.0); the box views sit near zero. His `def_divergence` is 1.83. That spread is the story of the Phase 2 valuation, and it must be carried as a fork, not averaged away.

Note what changes with price. At $24.3M he graded as roughly fair value with a neutral keep flag. At a taxpayer MLE near $6.06M, the same impact estimate becomes a large positive surplus. The signing's value is mostly a price argument, not an impact argument.

### B.3 fitengine: cannot answer the fit question today

The Bayesian skill-vector layer is done and covers everyone we need: 5,838 player-seasons, 1,346 players, 2013-14 through 2025-26. All five projected starters are fitted, Kuminga included (5 seasons through 2025-26), plus Beringer, Dosunmu and Green.

But the layer that turns five skill vectors into a lineup score does not exist. `src/models/gbm_floor.py` and `src/models/set_attention.py` are headed "F4 scaffolding" and are smoke-tested on synthetic data only; `src/models/aging_fit.py` raises `NotImplementedError`. The agent's verdict was blunt: the engine cannot produce a fit or synergy number for any team today, Minnesota included.

Compounding it, the derived inputs are not on disk: `possessions/` is absent, `stints/` holds 1,569 games covering only 2019-20 and 2020-21, and `fitengine.duckdb` is absent. And three of the eight skill factors are documented as having drifted off their intended meaning.

**The counterfactual-five question in the brief is a build, not a run.**

### B.4 The two publication gates, and why they matter here

`lamelo/` and `alebron/` both computed a title percentage and then declined to publish it, on two pre-registered gates: a star-acquisition retrodiction backtest that failed (5 of 8 signs correct), and an identifiability test showing the delta's band across defensible forks straddles zero.

Both gates are engine-level, not player-level. They test the net-rating-to-outcome machinery and the additive star-acquisition estimand, so they are not specific to LaMelo or LeBron. The agent's read: they would fire again for Kuminga, and identifiability is worse for him than for either predecessor, because his fork spread (+1.33 in-house vs -1.0 DARKO) is wider and his minutes are fewer.

This is the most important scoping fact in Phase 0. **A headline "Kuminga is worth X percentage points of title equity" is, on the project's own standing rules, unlikely to survive to publication.** What survives is the decomposition, the ordinal ranking, the CRN-paired delta reported as a band, and the cap argument. Phase 2 should be planned around that from the start rather than discovering it at the end.

### B.5 Pre-Kuminga Wolves baselines on the record

| Metric | Value | Source | As-of |
|---|---|---|---|
| Title odds, pre-offseason (Randle + Reid roster) | 1.7% (band 1.4-2.0) | `offseason/outputs/e_baseline.md` | 2026-06-13 |
| Title odds, stand-pat (core_max harness) | 2.46% / 2.42% | `core_max/docs/phase3_verdict.md` | 2026-06-21 |
| Title odds, post-LaMelo-trade | **RAPM 2.658% / box 3.916%** | `lamelo/data/sim/sim_results.json` | 2026-06-26 |
| Title equity, board-reconciled roster | 1.937% (rapm) / 3.811% (box) | `all-for-one/.../joanbet_reconciled.json` | 2026-07-17 |
| Expected wins 2026-27 | 44.4 (rapm) / 47.6 (box) | same | 2026-07-17 |
| Projected RS net rating | +1.36 | `offseason/outputs/e_baseline.md` | 2026-06-13 |

**There is no single agreed baseline.** Four numbers between 1.7% and 3.9% describe roughly the same team on different roster assumptions and different forks. Phase 1 must pick one baseline definition and state it, or every attribution number downstream is uninterpretable.

A full 30-team pre-offseason title board does exist (`offseason/outputs/e_baseline.md`, 2026-06-13): OKC 20.1, BOS 14.1, SAS 11.6, DET 11.5, HOU 6.5, NYK 6.0, MIA 5.0, DEN 4.8, ORL 4.2, CHA 3.6, CLE 2.9, MIN 1.7, LAL 1.6, TOR 1.5. Worth noting against what happened: it had the eventual champion, New York, at 6.0% and the losing finalist, San Antonio, at 11.6%.

### B.6 pick2033: the option-pricing machinery does not price this option

The engine simulates all 30 franchises forward 2027-2033 and implements the reformed 16-team lottery. But only MIN and CHA get roster-informed strength; the other 28 run on a franchise-prior AR(1) with no knowledge of rosters or contracts.

More to the point: there is no player-option or contract-option machinery anywhere in pick2033. The draft-swap options it prices are path-dependent options on pick order, which is a different problem from a player's opt-out decision. The brief's plan to "price the player option with the pick2033 Part 3 machinery" does not work as written; that is a new model, not a parameterization. Its retention hazard also cannot be pointed at Kuminga: the star-spell definition requires an All-NBA selection or a top-20 BPM season, and he qualifies for neither.

Two of its gates stand red on the record (Model B calibration slope 1.413 against a [0.8, 1.2] gate; Model A skill gate fails at every horizon).

### B.7 What is reusable as-is

Genuinely reusable without change:

- `evaluate_move.py` (offseason) is team-agnostic: it takes any `team_state` row. A Kuminga taxpayer-MLE signing is expressible today as a single leg with `exception_used='taxpayer_mle'`.
- The CBA feasibility gate (`core_max/cba/gate.py`) is config-driven, with `team` and `season` fields, not MIN-hardcoded.
- `build_team_state.py` already emits 30 teams x 4 seasons.
- `tax_history.csv`: 30 teams x 4 seasons, complete.
- The RAPM value spine (`player_value.csv`, 612 players, all 30 teams) and `player_surplus.csv` (338 players).
- The CRN pairing pattern in `run_sim.py` (build the field once, swap only MIN's net, difference on identical draws).
- The frozen-snapshot discipline (content-addressed, per-table sha256, CURRENT pointer).
- The pre/post counterfactual harness (`pretrade_counterfactual.py`) is the exact template for "MIN with Kuminga vs MIN without".

### B.8 What needs new code

- A **free-agency / signing evaluator**. The engine models trades only. `evaluate_move` can gate an MLE signing against the hard cap, but nothing scores the value of a signing. The central move in this analysis has no evaluator. (Medium.)
- **Per-team roster-delta projection** inside `build_2026_27_league`, for the 25 teams currently assumed stand-pat. (High. The largest item.)
- A **Kuminga transport module** and the minutes-reallocation ruling that goes with it. (Low code, real judgment.)
- **Persisting the all-30 table** instead of only MIN. (Low.)
- A **player-option valuation module**. (Medium, and it does not exist in any subsystem.)
- The **fitengine synergy layer**, if the counterfactual-five question is in scope. (Large.)

---

## C. Gap list

Priority: **P0** blocks everything downstream. **P1** blocks a headline number. **P2** improves the work but does not gate it.

### P0 gaps

| # | Gap | Current state | Candidate sources | Effort | Terms of use |
|---|---|---|---|---|---|
| 1 | **The Kuminga signing itself** | Absent from every store. `nba_player_contracts` still has him on ATL at $24,300,000 (team option); `nba_transactions` ends 2026-08-23 with no signing. | NBA.com official transaction log; Spotrac player page; team release; reporter confirmation | Low to enter, but must be verified against two sources per the brief | None; hand-entry with a source URL |
| 2 | **Actual 2026-27 cap, tax and apron figures** | Two conflicting values in-repo. The engine reads the June **projection** ($222.0M apron 2, $6,065,000 TPMLE, `is_projection: true`). Only `alebron/` carries the "verified" set ($221,686,000, $6,064,000), and it never propagated back. | NBA PR release (primary); Larry Coon CBA FAQ; Hoops Rumors / Keith Smith | Low | None |
| 3 | **2026-27 rosters for all 30 teams** | `nba_team_rosters` is current-dated but frozen on 2025-26 content. No 2026-27 roster exists anywhere. | Rebuild from `nba_player_contracts` + `nba_transactions` (both current) and reconcile against B-Ref/RealGM team pages | Medium | Warehouse-internal; B-Ref only for reconciliation |
| 4 | **Post-offseason `team_state` for all 30 teams** | `team_state.csv` is as-of 2026-06-17, pre-free-agency. Hard-cap flags are all unset because hard caps are *triggered by* the very moves it predates. | Re-run `build_team_state.py` against today's contracts, after gap 2 | Low to run, medium to validate | None |
| 5 | **Per-team 2026-27 roster deltas for the 25 stand-pat teams** | `bracket_sim` adjusts only MIA, MIN, BOS (+ORL, IND health). 25 teams assumed unchanged, while the transaction log shows 309 legs across all 30. | The warehouse transaction log itself, plus rotation projections | **High. The largest item in the project.** | None |
| 6 | **A signing evaluator** | The engine models trades only. `evaluate_move` can gate an MLE signing against the hard cap, but nothing scores the *value* of a signing. The central move in this analysis has no evaluator. | New code, reusing `evaluate_move` for the cap side | Medium | n/a |

### P1 gaps

| # | Gap | Current state | Candidate sources | Effort |
|---|---|---|---|---|
| 7 | **A single agreed baseline** | Four numbers between 1.7% and 3.9% describe roughly this team, on different roster assumptions and forks. Attribution is uninterpretable until one is chosen and stated. | Internal decision, then one re-run | Low, but it is a ruling |
| 8 | **Long-term injury status, league-wide** | Zero offseason injury data. DiVincenzo's Achilles is corroborated only by his disappearance from box scores and one line in a board doc. Timeline conflict: the brief says "possible return after the All-Star break", `board_spec.md` says "most or all of the season". | Team releases; NBA injury report; reporter timelines; Spotrac injury tracker | Medium; hand-curated, needs a return-timeline convention |
| 9 | **Pick detail for the four-team trade** | The transaction feed carries one undifferentiated "draft consideration" leg. The 2033 first, the 2028/29/30 swaps and three seconds appear nowhere. | RealGM / Spotrac pick ledgers; B-Ref trade page; `nba_draft_picks_future.csv` refresh (currently as-of 2026-06-06) | Medium |
| 10 | **The derived possession / stint layer** | `possessions/` absent; `stints/` covers only 1,569 games from 2019-21; duckdb absent. Needed for any RAPM refit. | Rebuild from PBP, which is complete | Medium-high compute, low risk |
| 11 | **2026-27 futures and win totals** | Three seasons of history exist (good for backtest); nothing forward. | Sportsbooks / aggregators | Low to collect; **check terms of use before automated retrieval** |
| 12 | **2026 draft results and rookie scale** | `nba_player_bio` stops at the 2025 class. Isaiah Evans is not in the bio table at all. | B-Ref 2026 draft page; NBA.com | Low-medium |
| 13 | **Dead money and duplicate-row handling in contracts** | `nba_player_contracts` has no dead-money column, and a waived-and-stretched player appears under **both** teams at **full** salary. Four such players for 2026-27 (Beal, Lillard, Caldwell-Pope, Prosper), inflating six teams' totals. Minnesota is unaffected. | Spotrac dead-money tables | Medium |
| 14 | **Bird-rights logic** | Exists as prose only (`offseason/docs/nba-roster-rules-reference.md`), not code. Needed for the "what if Kuminga opts out after year one" question. | CBA text; encode as a rule | Low-medium |
| 15 | **A player-option valuation module** | Does not exist in any subsystem. The brief's plan to use pick2033's Part-3 machinery does not work: that prices path-dependent options on pick order, a different problem. | New model | Medium |

### P2 gaps

| # | Gap | Note |
|---|---|---|
| 16 | The fitengine synergy layer | Large build. Only needed if the counterfactual-five question stays in scope. |
| 17 | External metric validation (EPM, LEBRON) | DARKO exists as a hand-entered 582-row snapshot (2026-06-10). EPM and LEBRON are absent. Check terms before retrieval. |
| 18 | TPE coverage | `team_trade_exceptions.csv` covers 15 of 30 teams and predates the July trade wave. |
| 19 | 2026-27 schedule | **Not a blocker.** The season sim is regression-based, not schedule-based. Only needed for calendar mapping (e.g. deadline dates). |
| 20 | Trade kickers / no-trade clauses | Merged from a 2026-06-13 file, so every post-June signing defaults to kicker 0. `evaluate_move` inflates incoming salary by the kicker before matching, so a missing kicker can pass an illegal trade. |

### Proposed schemas for the three new tables

The brief asks for `transaction_ledger`, `cap_sheet_2026_27` and `roster_snapshot`. Two of the three substantially overlap what already exists, and my recommendation is to **extend rather than duplicate**:

- **`transaction_ledger`**: `nba_transactions` already provides the header/leg structure via `group_sort`, is live through 2026-08-23, and covers all 30 teams. What it lacks is dollars, enumerated picks, and exception-used. Recommend a **companion child table** keyed on `group_sort` that adds those, rather than a new parallel ledger that would immediately diverge from the live feed.
- **`cap_sheet_2026_27`**: `offseason/data/team_state.csv` already is this, with 55 columns covering apron distances, exception availability, matching rules, TPEs, hard-cap flags and repeater status, for 30 teams across four seasons. It is stale, not missing. Recommend **rebuilding it** off today's contracts rather than designing a new table.
- **`roster_snapshot`**: this one genuinely does not exist for 2026-27 and should be built new, as-of dated, 15 standard plus two-way, with the triggering event recorded.

Full DDL is in the companion synthesis output.

---

## D. Open questions for Bobby

Only the things that actually block Phase 1.

**1. The publication gate. This is the big one.**
`lamelo/` and `alebron/` both computed a title percentage and then declined to print it, on pre-registered gates that are **engine-level, not player-level**: a failed star-acquisition retrodiction backtest and an identifiability test whose band straddles zero. Those gates would fire again for Kuminga, and identifiability is *worse* for him (his four views span +1.33 in-house to -1.0 DARKO).

So: do you want Phase 2 planned around a **title-odds number that probably cannot be published**, or around what the project has twice found it *can* stand behind, namely the decomposition, the ordinal all-30 ranking, the CRN-paired delta as a band, and the cap argument? My recommendation is the latter, decided now rather than discovered at the end. It changes what Phase 2 builds.

**2. How far to take "identically on all 30 teams."**
The engine is all-30 on the output side already. The input side is not: 25 of 30 teams are assumed to have stood pat. Three options:
- (a) Full: project 2026-27 rotations for all 30 teams. Highest fidelity, by far the most work, and 29 of them are judgment calls.
- (b) Mechanical: rebuild every team's roster from `nba_player_contracts` + `nba_transactions` and roll up player values with a minutes heuristic. Uniform, reproducible, defensible, less accurate per team. **My recommendation** — it is the only option that literally satisfies "run identically on all 30."
- (c) Tiered: full treatment for contenders, mechanical for the rest. Best accuracy per hour, but the pipeline is no longer identical across teams, which is the thing the brief specifically asked for.

**3. The Green branch, and when to lock.**
Both branches are computable today. Do you want both carried through Phase 2 and collapsed on Saturday, or should I wait for the resolution before running anything? Carrying both doubles the Phase 2 sim work but leaves you publishable on Saturday either way. **Recommend carrying both.**

**4. Whether the Kuminga terms are hand-entered.**
The signing is in no data source we have. Verifying it against two sources and hand-entering it with a source URL is the only path to a Phase 1 number. Confirm you want that, and confirm the tolerance: the reported "$12.4M" is consistent to about $30k with two years of the projected taxpayer MLE at a 5% raise, which is reassuring but is not the same as a confirmed cap hit.

**5. Scope of the counterfactual fives.**
The brief asks for Beringer at the 4, McDaniels at the 4, and the best alternative PF. The fitengine cannot answer that for any team today; its synergy layer is scaffolding. Do you want that built (large), or should the counterfactuals be answered with the existing rollup-plus-net-rating machinery (much weaker, but runnable now)? **Recommend the latter for this piece**, flagged honestly as a talent rollup rather than a fit model.
