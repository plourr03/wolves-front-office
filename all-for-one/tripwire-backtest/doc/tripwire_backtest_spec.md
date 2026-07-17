# Tripwire Backtest Spec

Pre-registering the February 2027 deadline alarms for the "If I Were Tim Connelly" master plan project.

Version 0.1, drafted July 17, 2026. Intended executor: warehouse agent (Claude Code) against the ScoutIQ PostgreSQL warehouse. All table and column names below are placeholders and must be mapped to the real schema in Phase 0.

## 0. Plain language summary

We want three or four early-season alarms, chosen and frozen before the season starts, that tell us by midseason which branch of the board we are on and which pre-committed deadline move to make. To choose them honestly, we backtest: for every past situation that looks like ours (a ball-dominant guard arriving next to an incumbent star, an injury-history player pacing below plan, a team that lost its frontcourt anchor), we measure which early metrics actually predicted how the season resolved, and we keep only the metrics that both stabilize fast enough to trust at 20 games and genuinely change which deadline move is correct. Everything else stays on the dashboard for diagnosis but is never wired to an action. The final deliverable is a short pre-registration file, TRIPWIRES.md, frozen in October, that the February 2027 decision will be executed against.

## 1. Vocabulary

Dashboard: everything the warehouse tracks. Unlimited. Used for diagnosis after an alarm, never for triggering one.

Wire (tripwire): a metric bound to a threshold, a read date, and a pre-committed action. Maximum four.

Read: a scheduled evaluation date. R1 is advisory (flags a wire as "at risk"). R2 is binding (a wire tripped at both R1 and R2 fires its action). A wire that is red at R1 and green at R2 does not fire. Exception: exact count metrics (see AVAIL-PACE) may hard-trip at R2 alone.

Arm: one of the enumerated actions available at the February 2027 deadline node.

Default arm: WAIT. Written down as an explicit action so that inaction in February is a decision made in October, not a failure of nerve.

## 2. Decision context: the February 2027 node

The node is the 2027 NBA trade deadline (early February 2027, exact date VERIFY at runtime). The action menu is small because of the cap position, and every constraint below should be re-verified against current data when Phase 0 runs, since the numbers drift with signings.

ARM-W (default): stand pat, develop internally, revisit at the summer 2028 gate.

ARM-G (guard depth): trade for backcourt insurance, matching salary built around the Josh Green expiring (about 14.7M) or the DiVincenzo expiring (about 12.9M, injured). Gated primarily by AVAIL-PACE and PAIR-DRTG.

ARM-B (frontcourt): trade for a backup big or rebounding forward using the same matching pieces. Gated primarily by FC-DRB.

ARM-S (staggering, free): coaching action, restructure the Ant and LaMelo minute overlap. Costs nothing, so its trigger threshold should be materially lower than the trade arms.

Constraints to encode as config, not prose: team is over the first apron (VERIFY), so incoming salary in any trade is capped at 100 percent of outgoing, and buyout-market signings are prohibited for players whose pre-waiver salary exceeded the non-taxpayer midlevel. Sweeteners available: Shannon Jr. on rookie scale, no tradeable first-round picks in any year, second-round inventory to be confirmed from the warehouse ledger. Every ARM-G and ARM-B target list must pass the trade model plausibility gate (P_yes at or above 0.25, TUNE) before it can appear in TRIPWIRES.md.

## 3. Scenario templates and reference classes

Era window: primary class 2010-11 through 2025-26, with a tracking-era flag for 2013-14 onward. Metrics that require tracking data restrict to the flagged subset.

### Scenario A: co-star integration

An arriving guard with prior-season usage at or above 28 percent and at least 1200 prior-season minutes joins a team employing an incumbent who made All-NBA in either of the two prior seasons or was an All-Star starter (filter sensitivity must be reported, since cases like CP3 to Phoenix hinge on it). Midseason arrivals count, with the evaluation clock starting at the arrival date.

Seed cases for validating the extraction query, core class:

| Case | Date | Arriving | Incumbent |
|---|---|---|---|
| Lillard to Bucks | Sep 2023 | Lillard | Antetokounmpo |
| Irving to Mavericks | Feb 2023 | Irving | Doncic |
| Harden to Nets | Jan 2021 | Harden | Durant |
| Harden to Sixers | Feb 2022 | Harden | Embiid |
| Harden to Clippers | Nov 2023 | Harden | Leonard, George |
| Westbrook to Lakers | Aug 2021 | Westbrook | James, Davis |
| Paul to Suns | Nov 2020 | Paul | Booker |
| Mitchell to Cavaliers | Sep 2022 | Mitchell | Garland |
| Beal to Suns | Jun 2023 | Beal | Booker, Durant |
| Fox to Spurs | Feb 2025 | Fox | Wembanyama |
| Doncic to Lakers | Feb 2025 | Doncic | James |
| Murray to Pelicans | Jul 2024 | Murray | Williamson |

Extended class (fails one filter, kept for robustness runs and as negative controls for the ball-dominant definition): Holiday to Bucks 2020, Holiday to Celtics 2023, Irving to Celtics 2017, Walker to Celtics 2019, Lowry to Heat 2021, Westbrook to Wizards 2020. Adjacent variant (high-usage non-guards, robustness only): Anthony to Thunder 2017, Butler to Timberwolves 2017, Towns to Knicks 2024.

### Scenario B: availability pacing

An arriving player, any position, who missed at least 30 percent of games in at least two of the four prior seasons. Question: how well does games-played pace at an early cut predict full-season and playoff availability? Seed cases: Simmons to Nets 2022, Wall to Rockets 2020, Irving to Mavericks 2023, LaVine to Kings 2025, Porzingis to Celtics 2023, Lonzo Ball to Bulls 2021, Leonard to Clippers 2019, George to Clippers 2019, Middleton to Wizards 2025.

### Scenario C: frontcourt succession

A team whose leading or second rim-minutes anchor departs in the offseason with no incoming replacement above a minutes threshold. Question: does early defensive rebounding and rim protection in anchor-off minutes predict the season-long hole, and did deadline big acquisitions patch it? Seed cases: Rockets 2020 post-Capela, Nets 2021 post-Allen, Jazz 2022 post-Gobert, Lakers 2025 post-Davis, Bucks 2025 post-Lopez. The 2026-27 Wolves instance is the Naz Reid departure behind Gobert.

## 4. Outcome labels

Each label is computed at two horizons: H1, end of the arrival season, and H2, end of the following season, because several pairings resolved in year two.

Scenario A. YA1_cont: pair shared-floor net rating over team games 41 through 82 (minimum 800 shared possessions, else null). YA1_bin: YA1_cont at or above zero. YA2: playoff rounds won minus preseason expectation, where expectation is derived from preseason title odds mapped to implied rounds (helper table required). YA3: breakup within 18 months of arrival, defined as either star traded or a publicly reported trade request, sourced from the transactions table plus a manually curated flag column.

Scenario B. YB1: arriving player regular-season games played. YB2: fraction of the team's playoff games in which the player was available. YB3: indicator that final availability landed below the pre-season plan (plan defined per case as prior three-season median games).

Scenario C. YC1: team defensive rebound percentage and opponent rim field goal percentage in anchor-off minutes, games 26 through 82. YC2: for teams that acquired a big at the deadline versus signal-tier-matched teams that did not, the before-and-after delta in YC1 components. YC2 is descriptive only: selection effects make it a comparison, not a causal estimate, and TRIPWIRES.md must not cite it as causal.

## 5. Candidate wire library

| ID | Definition | Gates | Stabilization prior |
|---|---|---|---|
| AVAIL-PACE | LaMelo games played through team game N, expressed as a percentile of the pick2033 pre-season availability posterior | ARM-G | Exact count, no sampling noise |
| PAIR-DRTG | Ant plus LaMelo shared-floor defensive rating, hierarchically shrunk using the fitengine prior, reported as posterior mean and P(worse than team baseline by 4 or more) | ARM-S first, then ARM-G or ARM-B | Raw version slow, shrunk version usable at R1 with the possession floor |
| FC-DRB | Team defensive rebound percentage in Gobert-off minutes, as a league percentile | ARM-B | Fast |
| TOV-BLEED | Opponent points off turnovers per 100 in LaMelo minutes, plus his shared-floor turnover percentage | ARM-S, ARM-G | Fast to moderate |
| SPACE-ANT | Ant catch-and-shoot three-point attempts per 100 and wide-open three frequency, as deltas versus his prior season | ARM-S, diagnostic | Moderate, tracking data required |

Dashboard-only, explicitly excluded from wiring, with reasons: any three-point percentage (does not stabilize by R1 or R2), clutch net rating (tiny samples, famously noisy year to year), raw win-loss versus expectation before R2 (schedule confounded, use an SRS-adjusted view at R2 only), any specific five-man lineup net rating (possession counts too small, the pair-level shrunk metric is the ceiling of what the sample supports), and individual scoring averages (not decision-relevant to any arm).

The pattern the seed cases suggest, to be confirmed or killed by Phase 3: early offense is the false signal in Scenario A. Most of the seed pairings looked fine offensively by game 20, including the ones that collapsed. The separators were availability pace, shared-floor defense, and the turnover and spacing interaction. This is a hypothesis with a class size around twelve. Treat it as a prior, not a verdict.

## 6. Method phases

### Phase 0: schema map

Map required sources: team_game, player_game, stint and stint_player (or the lineup equivalent), player_season, honors, transactions, tracking shot data, the pick2033 availability posterior tables, and the trade model P_yes interface. Deliverable: a coverage report (rows per season per table, null audits, era boundaries) and a rename map from placeholder names to real ones. Acceptance: every query in section 7 parses against the mapped schema.

### Phase 1: reliability curves

For every candidate metric, across all team-seasons or player-seasons 2014-15 through 2024-25 (not just the reference class, since stabilization is a property of the metric, not the scenario), compute the metric over the first N games and over the remaining games, for N in 10, 15, 20, 25, 30, and report the correlation r(N) between the early and rest values. Deliverable: an r(N) table and plot per metric. Gate: a metric is wire-eligible only if r(25) is at or above RELIABILITY_GATE, exact count metrics exempt.

### Phase 2: reference class and labels

Run the extraction queries, reconcile against the seed tables (every seed case must either appear or have a logged reason for exclusion), hand-curate the YA3 breakup flags, and compute all labels at both horizons. Deliverable: one case table per scenario with early features and labels. Acceptance: class sizes reported, and any case with null labels documented.

### Phase 3: predictive validity

For each surviving metric and each label: Spearman rank correlation across cases, sign consistency (the fraction of cases where the early metric's direction relative to the class median matches the outcome's direction), and a leave-one-out threshold stability check (refit the trip threshold leaving each case out, report how often the tripped-or-not classification of the held-out case flips). Eligibility to become a wire: at least N_GATE labeled cases, reliability gate passed, sign consistency at or above SIGN_GATE. Report exact case counts everywhere. No p-values; at this sample size they would be theater.

### Phase 4: selection and pre-registration

Select at most MAX_WIRES wires, breaking ties by decision coverage (prefer a set that gates different arms over two wires gating the same arm). Write TRIPWIRES.md containing, for each wire: frozen definition, threshold, R1 date and advisory rule, R2 date and binding rule, the wired arm with a pre-scoped target list that passes the trade model plausibility gate, and the explicit WAIT default. Include a change-control clause: any edit after the freeze date requires a logged justification in the file itself. Optional but recommended for the article: publish the SHA-256 hash of the frozen file publicly in October, so the February piece can prove the alarms were not chosen after the fact.

## 7. Query sketches

Placeholder schema. Rename in Phase 0. first_n_games(team, season, n) is a helper view returning the game_ids of a team's first n games of a season.

Reliability curve, team defensive rebound percentage example:

```sql
WITH ordered AS (
  SELECT team_id, season, game_id, drb, opp_orb,
         ROW_NUMBER() OVER (PARTITION BY team_id, season
                            ORDER BY game_date) AS rn
  FROM team_game
  WHERE season BETWEEN 2014 AND 2025
),
split AS (
  SELECT team_id, season,
         CASE WHEN rn <= 25 THEN 'early' ELSE 'rest' END AS phase,
         SUM(drb) AS drb, SUM(opp_orb) AS oorb
  FROM ordered
  GROUP BY 1, 2, 3
),
wide AS (
  SELECT team_id, season,
         MAX(CASE WHEN phase = 'early' THEN drb END)::float
           / NULLIF(MAX(CASE WHEN phase = 'early' THEN drb + oorb END), 0) AS early_val,
         MAX(CASE WHEN phase = 'rest' THEN drb END)::float
           / NULLIF(MAX(CASE WHEN phase = 'rest' THEN drb + oorb END), 0) AS rest_val
  FROM split
  GROUP BY 1, 2
)
SELECT COUNT(*) AS n_team_seasons, CORR(early_val, rest_val) AS r_at_25
FROM wide;
```

Parameterize the rn cut over 10, 15, 20, 25, 30 to build the full r(N) curve. For Gobert-off and anchor-off variants, replace team_game sums with stint sums filtered on the anchor being absent from stint_player.

Shared-floor pair aggregate (feeds the fitengine shrinkage, which produces the actual PAIR-DRTG posterior):

```sql
WITH pair_stints AS (
  SELECT st.stint_id, st.def_poss, st.pts_against
  FROM stint st
  WHERE st.game_id IN (SELECT game_id FROM first_n_games(:team_id, :season, :n))
    AND EXISTS (SELECT 1 FROM stint_player sp
                WHERE sp.stint_id = st.stint_id AND sp.player_id = :p1)
    AND EXISTS (SELECT 1 FROM stint_player sp
                WHERE sp.stint_id = st.stint_id AND sp.player_id = :p2)
)
SELECT SUM(def_poss) AS shared_def_poss,
       100.0 * SUM(pts_against) / NULLIF(SUM(def_poss), 0) AS raw_drtg
FROM pair_stints;
```

Scenario A class extraction:

```sql
SELECT s1.player_id AS arriving, s1.season, s1.team_id AS new_team,
       s0.team_id AS old_team, s0.usg_pct AS prior_usg
FROM player_season s1
JOIN player_season s0
  ON s0.player_id = s1.player_id AND s0.season = s1.season - 1
WHERE s1.team_id <> s0.team_id
  AND s0.usg_pct >= 28.0
  AND s0.minutes >= 1200
  AND s1.pos_group = 'G'
  AND s1.season >= 2011
  AND EXISTS (
    SELECT 1
    FROM player_season inc
    JOIN honors h
      ON h.player_id = inc.player_id
     AND h.season IN (s1.season - 1, s1.season - 2)
     AND h.award IN ('ALL_NBA', 'ALL_STAR_STARTER')
    WHERE inc.team_id = s1.team_id
      AND inc.season = s1.season
      AND inc.player_id <> s1.player_id
  );
```

Midseason arrivals will split player_season rows; also scan the transactions table for in-season team changes and start each case's clock at the arrival date. The seed tables in section 3 are the validation target: every seed must appear or be explained.

AVAIL-PACE against the pick2033 posterior:

```sql
WITH pace AS (
  SELECT COUNT(*) AS gp
  FROM player_game pg
  JOIN first_n_games(:team_id, :season, :n) fg USING (game_id)
  WHERE pg.player_id = :player_id AND pg.minutes > 0
)
SELECT p.gp, ap.q10, ap.q50, ap.q90,
       (SELECT AVG(CASE WHEN d.games_through_n <= p.gp THEN 1.0 ELSE 0 END)
        FROM availability_posterior_draws d
        WHERE d.player_id = :player_id AND d.through_game = :n) AS pctile_of_prior
FROM pace p
JOIN availability_posterior ap ON ap.player_id = :player_id;
```

## 8. Honesty clauses

The reference classes are small, roughly ten to fifteen cases each, so everything downstream is a prior update, not a proof, and TRIPWIRES.md should say so in its header. Intervention outcomes (YA2 uplift after a deadline move, YC2) carry selection bias that matching only partially addresses; they are reported as descriptive comparisons. The class spans three collective bargaining regimes, and apron-era constraints changed what deadline arms even existed, so era is carried as a covariate and flagged in every table. The model contains no private information: no medicals, no agent conversations, no locker room, and the article should name that as the blind spot a real front office fills. Finally, LaMelo's specific injury and usage profile is only partially exchangeable with the class, which is exactly why AVAIL-PACE runs against his individually fitted posterior rather than a class average.

## 9. Config

| Constant | Value | Status |
|---|---|---|
| R1 (advisory read) | 2026-11-27 | Approx team game 17 to 20 |
| R2 (binding read) | 2027-01-10 | Approx team game 36 to 39 |
| Deadline | Early Feb 2027 | VERIFY exact date |
| SHARED_POSS_FLOOR at R1 / R2 | 350 / 700 def poss | TUNE |
| RELIABILITY_GATE | r(25) >= 0.50 | TUNE |
| SIGN_GATE | 0.70 | TUNE |
| N_GATE | 8 cases | Fixed |
| MAX_WIRES | 4 | Fixed |
| P_yes floor for target lists | 0.25 | TUNE, from trade model |
| Freeze date for TRIPWIRES.md | 2026-10-20 | Day before opener, VERIFY |

## 10. How this feeds the board

The selected wires become the observable state variables at the February 2027 decision node on the master plan board. Every branch drawn out of that node in the article corresponds to a wire state, and the pre-committed arm attached to each state is the thing that makes the piece read like a policy instead of a prediction. The backtest exists so that when someone in a front office asks why those three numbers and not thirty others, the answer is a reliability table and a scorecard instead of a shrug.
