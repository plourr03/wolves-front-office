# C2: the Edwards clock

*As of 2026-09-22. Pulled forward from pick2033 Part 1 (Model B, M2 FINAL, freeze `50f9b7bc5b19835b`), restated against the contract and the 2023 CBA. Run `c2_edwards_clock_20260922T191531Z`.*

## The table

P(Anthony Edwards departs) by season, from the league-wide star-tenure hazard model, under two team paths. The hazard is the chance he leaves in that season given he is still here; the cumulative column is the chance he has left by then. 80% intervals in brackets. Sample: 291 star spells, 1264 player-seasons, 228 departures, 1990 to 2026.

| season | age | seasons left after this one | hazard, team at .600 | hazard, team at .450 | departed by then, .600 | departed by then, .450 | the clock |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-27 | 25 | 2 | 0.8% [0.4%, 1.2%] | 1.3% [0.7%, 2.0%] | 0.8% [0.4%, 1.2%] | 1.3% [0.7%, 2.0%] | Standard veteran extension window open since July 8, 2026, the third anniversary of the July 8, 2023 rookie scale extension (5- or 6-season contracts extend after the third anniversary, Art. VII Sec. 7(a)(1)); reported at two years, about $122 million. The supermax (Designated Veteran) window is closed this summer: the 61-game 2025-26 fell short of the 65 games All-NBA requires (Art. XXIX Sec. 6). |
| 2027-28 | 26 | 1 | 7.3% [4.8%, 10%] | 12% [7.7%, 16%] | 8.0% [5.2%, 11%] | 13% [8.4%, 18%] | July 2027: Designated Veteran Player Extension window opens (seven Years of Service, one or two seasons left, drafted by the team, Art. II Sec. 7(c)(ii)) IF he is All-NBA in 2026-27, which needs 65 games; six seasons from signing (Art. I Sec. 1(r)), so two remaining plus four new, the reported four-year deal. |
| 2028-29 | 27 | 0 | 44% [35%, 53%] | 56% [47%, 66%] | 48% [39%, 58%] | 62% [52%, 71%] | Walk year. July 2028: the last extension window before free agency; the Designated Veteran version needs All-NBA in 2027-28 (the two-of-three route is closed by the 2025-26 miss). Contract ends June 30, 2029; unrestricted free agent July 2029. |
| 2029-30 | 28 | 4 | 0.0% [0.0%, 0.1%] | 0.0% [0.0%, 0.1%] | 48% [39%, 58%] | 62% [52%, 71%] | Model assumption from Part 1: a star who survives his walk year re-signs on a fresh four-year deal, so the clock restarts. |
| 2030-31 | 29 | 3 | 0.2% [0.1%, 0.4%] | 0.4% [0.2%, 0.7%] | 49% [39%, 58%] | 62% [52%, 72%] |  |
| 2031-32 | 30 | 2 | 2.0% [1.0%, 3.2%] | 3.3% [1.7%, 5.3%] | 49% [39%, 60%] | 63% [53%, 73%] |  |
| 2032-33 | 31 | 1 | 14% [9.0%, 20%] | 22% [14%, 30%] | 56% [45%, 68%] | 71% [60%, 81%] | Fresh deal's own cliff approaches; the hazard climbs back. |

## The paragraph

Edwards is two seasons from his walk year. His deal runs 2026-27 through 2028-29, with no options in it, so the summer of 2029 is the first time he can leave on his own terms, and the history of stars in exactly that position says the leaving, when it happens, happens then: across 291 star spells since 1990, the departure odds in a walk year run about seventy times the mid-contract odds. Run his profile through the model with the Wolves winning at a .600 clip and his chance of departing is 0.8% this season, 7.3% next, and 44% at the 2029 cliff, 48% cumulative by that summer and 56% by 2033 [45%, 68%]. Let the team sag to .450 and the cliff is 56%, the cumulative 62% by 2029 and 71% by 2033 [60%, 81%]. The raw history says the same thing without a model: of 192 star-seasons with two years left, 44% had departed within three seasons, and in the walk year itself stars on .600 teams left 31% of the time (248 cases) against 56% on sub-.500 teams (118). What the clock adds is the CBA's dates. He has been eligible for a standard extension since July 8, 2026, two years and about $122 million by the reporting; the supermax window opens in July 2027 only if he makes All-NBA in 2026-27, which after a 61-game 2025-26 means playing 65 games first; and if that window closes too, the last one before free agency is July 2028, which needs an All-NBA 2027-28. Every one of those dates is a place where a season that goes wrong turns into a departure probability, which is why the title odds in this series and the retention odds in Part 1 are the same bet.

## Backing: the raw rates at his stage, by the team's two-year win percentage

| stage | horizon | team | star-seasons | spells | departed | rate |
|---|---|---|---:|---:|---:|---:|
| two seasons left after this one | within 1 season | all | 207 | 157 | 2 | 1.0% |
| two seasons left after this one | within 1 season | .500 to .600 | 71 | 69 | 0 | 0.0% |
| two seasons left after this one | within 1 season | .600 or better | 87 | 72 | 0 | 0.0% |
| two seasons left after this one | within 1 season | under .500 | 49 | 44 | 2 | 4.1% |
| two seasons left after this one | within 2 seasons | all | 194 | 148 | 5 | 2.6% |
| two seasons left after this one | within 2 seasons | .500 to .600 | 68 | 66 | 0 | 0.0% |
| two seasons left after this one | within 2 seasons | .600 or better | 82 | 67 | 3 | 3.7% |
| two seasons left after this one | within 2 seasons | under .500 | 44 | 41 | 2 | 4.5% |
| two seasons left after this one | within 3 seasons | all | 192 | 148 | 84 | 44% |
| two seasons left after this one | within 3 seasons | .500 to .600 | 68 | 66 | 35 | 51% |
| two seasons left after this one | within 3 seasons | .600 or better | 80 | 65 | 30 | 38% |
| two seasons left after this one | within 3 seasons | under .500 | 44 | 41 | 19 | 43% |
| walk year | that season | all | 536 | 272 | 221 | 41% |
| walk year | that season | .500 to .600 | 170 | 128 | 77 | 45% |
| walk year | that season | .600 or better | 248 | 147 | 78 | 31% |
| walk year | that season | under .500 | 118 | 89 | 66 | 56% |

The stage rows are read forward from every star-season with exactly two seasons left on the contract after that one; a window is counted only when it is fully observed or the departure falls inside it. The .500-to-.600 tier is not monotone in the middle row, which is what 44-to-87-case cells do; the model smooths across all of it. The walk-year rows are the cleaner conditional.

## Backing: the model's scorecard, unchanged from Part 1

- spec: M2_FINAL_SPEC (contract covariates, Normal(0,0.5) priors)
- health: train r_hat 1.0025, full r_hat 1.0025
- C-index: 0.907 (>= 0.63) -> **PASS**
- calibration slope: 1.413 [boot 90% CI 1.127, 1.872] ([0.8, 1.2]) -> **FAIL (stands documented, no third fit)**
- Cox sign agreement: PASS
- contract coefficients: b_contract_z -2.940, b_contract_known -0.015
- the walk-year multiple, recomputed here from the M2 coefficient and the standardization constant: exp(2.940 x 2 / 1.4023) = 66 times the odds with two seasons left, against Part 1's "roughly seventy" (80% interval 43 to 104 in the draft, from the full posterior)

## Sources

**Contract.** Basketball-Reference contracts via the warehouse `nba.nba_player_contracts` (scraped 2026-09-22): 2026-27 $48,924,624; 2027-28 $52,298,736; 2028-29 $55,672,848; HoopsHype contract file (`offseason/data/nba_contracts_2026_27.csv`, 2026-06-06) agrees on every figure and shows no option. Rookie scale extension signed 2023-07-08: NBA.com transactions (warehouse `nba.nba_transactions`) and the Basketball-Reference player page (cached, sha256 `512ced22895c54d4`, fetched 2026-09-22) agree. 2025-26 regular-season games: 61, warehouse box scores.

**CBA.** 2023 NBA-NBPA Collective Bargaining Agreement, NBPA copy (`https://imgix.cosmicjs.com/25da5eb0-15eb-11ee-b5b3-fbd321202bdf-Final-2023-NBA-Collective-Bargaining-Agreement-6-28-23.pdf`, sha256 in `data/c2_pick2033_inputs.sha256`). Quoted, by PDF page:

- *Article I, Section 1(r) (PDF p. 27):* "(r) “Designated Veteran Player Extension” means an Extension of a Contract entered into between a Team and its Designated Veteran Player that covers six (6) Seasons from the date the Extension is signed and provides for Salary for the first Salary Cap Year covered by the extended term equal to thirty percent (30%) or thirty-five percent (35%) (or such other percentage between 30% and 35% as agreed upon by the Team and the player) of the Salary Cap in effect during the first Season of the extended term. Annual increases and decreases in Salary in a Designated Veteran Player Extension shall be governed by Article VII, Section 5(a)(3). (s) “Draft” or “NBA Draft” means the NBA’s annual draft of Rookie basketball players. (t) “Early Qualifying Veteran Free Agent” means a Veteran Free Agent who, prior to becoming a Veteran Free Agent, played under one (1) or more Player Contracts covering som"
- *Article II, Section 7(a)(i) (PDF p. 60):* "(a) Notwithstanding any other provision of this Agreement, no Player Contract entered into on or after the effective date of this Agreement may provide for a Salary plus Unlikely Bonuses in the first Season covered by the Contract that exceeds the following amounts: (i) for any player who has completed fewer than seven (7) Years of Service, the greater of (x) twenty -five percent (25%) of the Salary Cap in effect at the time the Contract is executed, or (y) one hundred five percent (105%) of the Salary for the final Season of the player’s prior Contract; provided, however, that a player who has four (4) Years of Service as of the June 30 following the end of the last Season covered by his Player Contract (“5th Year Eligible Players”) sh all be eligible to receive from his Prior Team up to thirty percent (30%) of the Salary Cap in effect at the time the Contract is executed if the player"
- *Article II, Section 7(c)(ii) (PDF p. 62):* "Accordingly, and notwithstanding any other provision of this Agreement, the following rule shall apply to any Extension in which the extended term begins on or after the effective date of this Agreement: if, on July 1 of the Salary Cap Year encompassing the first Season of the extended term of such Extension, the Salary plus Unlikely Bonuses provided for in such Season exceeds the following amounts: (i) for any player who has completed fewer than seven (7) Years of Service, the greater o f (x) twenty -five percent (25%) of the Salary Cap in effect on July 1 of the Salary Cap Year encompassing the first Season of the extended term of such Extension, or (y) one hundred five percent (105%) of the Salary provided for in the final Season of the original term of the Contract; provided, however, that a 5th Year Eligible Player who signed a Rookie Scale Extension in accordance with Section 7(d) below shall be eligible to receive the percentage that is agreed upon by the Team and player, which shall be no less than twenty -five percent (25%) or greater than thirty percent (30%) of the Salary"
- *Article VII, Section 7(a)(1) (PDF p. 274):* "250 Article VII than the second anniversary of the signing (or, as applicable, the Extension) of the Contract; and (ii) a Player Contract covering a term of five (5) or six (6) Seasons (including, for clarity, any Option Year) may be extended no sooner than the third anniversary of the signing (or, as applicable, the Extension) of the Contract. A Player Contract covering a term of one (1) or two (2) Seasons (including, for clarity, any Option Year) may not be extended. If a player and Team seek to enter into an Extension pursuant to this Section 7(a) (other than a Designated Veteran Player Extension in accordance with Section 7(a)(3)(ii) below) more than one (1) year prior to the July 1 preceding the first Season covered by the extended term, then the Extension may only be negotiated and entered into during the off-season (i.e., during the period from July 1 through the day prior to the first day of a Regular Season). Notwithstanding the foregoing, a Player Contract may be extended pursuant to the Designated Veteran Player Extension rules set forth in Article II, Section 7 and Section 7(a)(3)(ii) below no sooner than the third anniversary of the signing of the Contract, and Designated Veteran Player Extensions may only be negotiated and entered into during the off-season. For purposes of this Section 7: (A) to determine the second or third anniversary of the signing of an Extension or Renegotiation, an Extension or Renegotiation entered into during the period from October 2 t"
- *Article XXIX, Section 6(a) (PDF p. 456):* "Games Played Requirement for Certain League Honors. (a) Award Eligibil ity. No player shall be eligible for NBA Most Valuable Player, NBA Defensive Player of the Year, NBA Most Improved Player, All- NBA Team (First, Second, or Third), or NBA All -Defensive Team (First or Second) honors (the “Applicable Generally Recognized League Honors”) for a Season unless the player has satisfied at least one of the following criteria (the “Award Eligibility Criteria”) in respect of such Season: (1) the player played in at least sixty-five (65) Regular Season games; or (2) the player (A) played in at least sixty -two (62) Regular Season games,"

**Reporting on the 65-game consequence.**

- Fadeaway World, syndicated by Yahoo Sports, 2026-05-30 (Vishwesha Kumar): "Edwards played in just 61 regular-season games, falling short of the NBA's mandatory 65-game threshold required to qualify for All-NBA teams and major end-of-season awards. [...] Edwards is no longer eligible for a four-year supermax extension worth roughly $300 million this summer [and] is currently eligible for a much smaller two-year extension worth approximately $122 million. [...] If Edwards reaches the 65-game threshold next season and earns another All-NBA selection, he would immediately become eligible for the same four-year, $300 million supermax extension in 2027." (https://sports.yahoo.com/articles/anthony-edwards-loses-eligibility-300m-113622348.html)
- Heavy, 2026-08-05 (Michael Kaskey-Blomain): "the Timberwolves' superstar was ineligible for All-NBA because he fell short of the 65-games-played threshold. [...] If Edwards had played four more games, he would have been eligible to sign a four-year, $301 million supermax extension next summer. [...] Edwards will need All-NBA, MVP or Defensive Player of the Year honors in 2026-27 to become eligible for that deal." (https://heavy.com/sports/nba/minnesota-timberwolves/how-anthony-edwards-can-become-eligible-supermax-extension-timberwolves/)

**Model.** pick2033 `outputs/json/edwards_hazard_FINAL.json`, `outputs/validation/model_b_hazard_M2_FINAL.md`, `data/staged/star_spells_final.parquet` with `contract_years_backfill.parquet` (copies and hashes under `kuminga/data/c2_*`). The Part 1 draft's own wording of the sample and the walk-year multiple is in `pick2033/docs/drafts/stage1_edwards_hazard_draft_v4.md`.
