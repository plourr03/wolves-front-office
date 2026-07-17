# Phase 0 Gap Register

Tripwire backtest, Phase 0 Step 3. Produced 2026-07-17.

Six gaps between the spec's placeholder schema and the real warehouse. Each entry: what the spec assumed, what actually exists, what it blocks, options with effort, recommendation. Ordered by how much they block, most-blocking first.

Summary table:

| ID | Gap | Blocks | Phase 0 blocker? | Recommended fix | Effort |
|---|---|---|---|---|---|
| G1 | No honors/awards table | Scenario A extraction (the whole class) | **Yes** | Scrape B-Ref All-NBA + All-Star | ~half day |
| G2 | Transactions start 2015-07-01 | Dating pre-2015 midseason arrivals | No | Derive from player_season + curate a handful | ~1 hour |
| G3 | No preseason title-odds table | YA2 label only | No | SRS proxy, not an odds archive | ~2 hours (proxy) |
| G4 | No wide-open/defender-distance data | SPACE-ANT wire | No | Drop SPACE-ANT to dashboard-only | 0 (a deletion) |
| G5 | Trade model has no P_yes | Phase 4 target-list gate | No (Phase 4) | Use boolean decide() + sweetener price | design note only |
| G6 | No pair-level shrinkage | PAIR-DRTG posterior | No (Phase 1/2) | New pair-level machinery | ~3-5 days, Phase 1/2 |

## G1: no honors table (BLOCKING)

**Spec assumed:** an `honors` table with `(player_id, season, award)` where award is in `ALL_NBA`, `ALL_STAR_STARTER`. The Scenario A extraction query (section 7) joins to it to find the incumbent star.

**Reality:** no award, honor, All-NBA, All-Star, MVP, or DPOY data exists anywhere in the warehouse. A search of every table and column name returned zero matches.

**Blocks:** the entire Scenario A class. Without the incumbent filter there is no "arriving guard joins a team with an All-NBA incumbent," which is the definition of Scenario A. This is the one gap that stops Phase 2 cold, so it is the first thing to fix in Phase 0.5.

**Options:**
1. Scrape Basketball-Reference for All-NBA teams and All-Star rosters (starters distinguished), **2008-09 through 2025-26**. The window starts two seasons before the era window because the filter looks back two years from each arrival. Roughly 450 rows (15 All-NBA + ~10 All-Star starters per year x 18 years). Precedent: `nba_player_contracts` is already B-Ref sourced, so the scraping and the `nba_player_id` crosswalk pattern exist in-repo. The crosswalk is the only safe join key (house convention).
2. Hand-curate only the incumbents that appear in the seed cases (~15 players). Faster, but it hard-codes the class to the seed list and defeats the extraction query's purpose, which is to find cases the seed list missed.

**Recommendation:** option 1. It is the cheapest high-value gap and it is what makes the class extraction real rather than a lookup of the seed table. Validate by asserting every seed-case incumbent (Antetokounmpo, Doncic, Durant, Embiid, Leonard, George, James, Davis, Booker, Garland, Wembanyama, Williamson) resolves to an All-NBA or All-Star-starter row in the right seasons. Effort: half a day including validation.

**Note on the filter sensitivity the spec already flagged:** the spec says "cases like CP3 to Phoenix hinge on" whether the incumbent filter is All-NBA-only or includes All-Star starters (Booker was an All-Star but not All-NBA in the relevant window). The honors ingest must carry the starter distinction so this sensitivity can actually be run, not just mentioned.

## G2: transactions start 2015-07-01 (minor)

**Spec assumed:** a `transactions` table covering the full era window (2010-11 forward) to date midseason arrivals and to source the YA3 breakup flag.

**Reality:** `nba_transactions` exists, 9,781 rows, but starts hard at **2015-07-01**. Verified: 499 rows in 2015 (first date 2015-07-01), then 690-1,038/year through 2026.

**Blocks:** less than it looks. Offseason arrivals need no transactions table at all; they are visible as a team change between consecutive `player_season` rows. Transactions are needed only to (a) date midseason arrivals and (b) seed the YA3 breakup flag (which is hand-curated anyway). Every midseason arrival in the **core** seed class is 2015 or later (Harden to Nets, Jan 2021 is the earliest). The only exposure is pre-2015 midseason **bonus** cases: Anthony to NYK (Feb 2011), and Howard to LAL (offseason, so unaffected).

**Recommendation:** derive offseason arrivals from `player_season` team changes. Hand-curate the arrival date for the one or two pre-2015 midseason bonus cases (Anthony to NYK is the only real one), logging each as curated. **Do not ingest transaction history.** Effort: about an hour, most of it the curation log.

## G3: no preseason title-odds table (minor, label-only)

**Spec assumed:** a helper table mapping preseason title odds to implied playoff rounds, for the YA2 label ("playoff rounds won minus preseason expectation").

**Reality:** does not exist. Odds archives are patchy, vendor-dependent, and not in the warehouse.

**Blocks:** the YA2 label only, which is one of three Scenario A labels (YA1 net rating and YA3 breakup are unaffected). YA2 is also the softest label; the spec already treats expectation-relative outcomes as descriptive.

**Options:**
1. Ingest a historical title-odds archive. Roughly a day, and the quality is uncertain (which book, which date, survivorship in the archive).
2. Replace the expectation baseline with a warehouse-derivable proxy: preseason SRS projection, or simply prior-season SRS as the expectation. `nba_games` supports SRS computation directly.

**Recommendation:** option 2, the SRS proxy. It is warehouse-native, reproducible, and free of vendor and survivorship problems, and for a class of ~12 cases the precision of a betting-market expectation buys nothing over a prior-season-strength expectation. State in TRIPWIRES.md that YA2's expectation baseline is SRS-derived, not market-derived. Effort: about two hours. Not a Phase 0 blocker.

## G4: no wide-open/defender-distance data (kills SPACE-ANT as a wire)

**Spec assumed:** SPACE-ANT = "catch-and-shoot three-point attempts per 100 and wide-open three frequency," gated on a Phase 1 reliability curve.

**Reality (verified in the coverage report):** no closest-defender, wide-open, touch-time, or dribble-range data exists anywhere in the warehouse. The only column with defender semantics is `nba_boxscore_matchups.percentage_defender_total_time`, a matchup time-share, not a distance. Catch-and-shoot exists only at **season grain** (`nba_player_tracking_season`, `measure_type='CatchShoot'`), which cannot produce a first-N-games reliability curve. Game grain (`nba_player_tracking_game`) has `uncontested_fga` but no three-point split and no wide-open definition.

**Blocks:** SPACE-ANT's ability to be a wire. A wire must pass the Phase 1 reliability gate `r(25) >= 0.50`. That gate is computed from an r(N) curve, and the r(N) curve cannot be built at all: season grain has no first-N split, and the game-grain proxy is neither three-point-restricted nor wide-open. There is no metric to gate.

**Recommendation:** move SPACE-ANT to **dashboard-only**, and say plainly in the register and TRIPWIRES.md that the reason is data availability, not judgement. The spec already labels SPACE-ANT "ARM-S, diagnostic," so the cost is one diagnostic and zero wires; the pair-level defensive and turnover metrics already gate ARM-S. If a coarser season-grain catch-and-shoot delta (this season vs prior) is wanted as a dashboard diagnostic, it is computable and harmless, but it is a diagnostic, not a triggerable wire. Effort: zero, it is a reclassification.

## G5: trade model has no P_yes (Phase 4, record only)

**Spec assumed:** every ARM-G and ARM-B target list passes a "trade model plausibility gate (P_yes at or above 0.25)" before appearing in TRIPWIRES.md.

**Reality:** `offseason/scripts/partner_acceptance.py::decide(partner, sends, receives, sweetener_pts=0.0)` returns `{"accepted": bool, "channels": [...], "delta_value": ..., ...}`. It is deterministic and boolean. A repo-wide grep for `p_yes` returns zero hits. There is no probability to threshold at 0.25.

Worse, `offseason/docs/acceptance_model_scope_and_limitation.md` documents that calibration was attempted, failed to generalize (16% recall on real trades, 90% on fleece-rejection), and was closed as out of scope, with an explicit instruction to read **marginal** deals with a grain of salt. A `P_yes >= 0.25` floor is, by construction, a marginal-deals filter: it selects exactly the deals near the accept/reject boundary, which is precisely where the model is documented as least trustworthy.

The one piece of good news: the tripwire use case (Minnesota acquiring, matching salary around the Green ~14.7M or DiVincenzo ~12.9M expirings) is **in scope** for the model. That is the one thing it does well.

**Blocks:** nothing in Phase 0. This is a Phase 4 concern (building the ARM-G/ARM-B target lists). Recorded here so it is not rediscovered in October.

**Recommendation:** replace the `P_yes >= 0.25` gate with the boolean `decide()` verdict plus its required-sweetener price. A target makes the list if `decide()` accepts it at a sweetener the Wolves can actually pay (Shannon Jr. rookie-scale, second-round inventory to be confirmed from the ledger, no tradeable firsts). Carry the scope caveat into TRIPWIRES.md verbatim: the acceptance read is MIN-acquisition-specific and marginal deals are least reliable. Do not manufacture a probability the model does not produce.

## G6: no pair-level shrinkage (Phase 1/2 design task)

**Spec assumed:** PAIR-DRTG is "hierarchically shrunk using the fitengine prior," producing a posterior mean and `P(worse than baseline by 4+)`.

**Reality:** fitengine's shrinkage (`src/models/rapm.py`, two-stage ridge toward a learned prior via the offset trick) is GREEN (F2/G2 ratified, skill vectors frozen 2026-07-06), but it operates on **individual player** offensive and defensive RAPM. There is no pair-level, shared-floor DRTG shrinkage function anywhere. Going from individual player posteriors to a shrunk shared-floor pair defensive rating is new machinery.

**Blocks:** PAIR-DRTG's shrunk posterior, which is what makes it usable at R1 with the possession floor (the raw version is too slow to stabilize). The raw shared-floor DRTG aggregate is computable now from the stint grain the spike just validated; the shrinkage layer is not.

**Recommendation:** record as a Phase 1/2 design task, not a Phase 0 fix. The design question is whether to (a) build a genuine pair-level hierarchical model, or (b) approximate the pair posterior from the two players' individual defensive RAPM posteriors plus a shared-floor interaction term estimated from the stint data. Option (b) reuses the frozen fitengine artifacts and is likely enough for a wire whose job is to answer "is this pair's defense meaningfully below baseline," a coarse yes/no, not a precise point estimate. Effort: roughly three to five days depending on which path, and it lands in Phase 1/2, gated on the stint panel the spike proved feasible.

## What is NOT a gap

For completeness, the spec placeholders that mapped cleanly and need no ingestion: `team_game` (`nba_games`), `player_game` (`nba_player_stats`), `player_season` (`nba_player_season_bio`, derived for minutes), tracking for the catch-and-shoot half (`nba_player_tracking_season`), and the stint grain itself (reconstructed, feasibility proven by the Step 2 spike back to 2010-11). See the coverage report for the four spec-query corrections these forced (the usg_pct scale bug chief among them).
