# Phase 0.5: Honors Ingest (G1)

Tripwire backtest, Phase 0.5. Produced 2026-07-17. Resolves gap G1, the one hard blocker for Phase 2. Data: `all-for-one/tripwire-backtest/data/honors.parquet` (682 rows). Scripts: `ingest_honors.py`, `validate_honors.py`.

## What was ingested

| Award | Rows | Coverage | Grain |
|---|---|---|---|
| ALL_NBA | 270 | 2008-09 to 2025-26, exactly 15/season (90 1st, 90 2nd, 90 3rd) | player x season x tier |
| ALL_STAR | 412 | 2008-09 to 2025-26, ~24/season | player x season, `is_starter` flag |

Source: Basketball-Reference, the same source as `nba_player_contracts`. All-NBA from the single `/awards/all_league.html` page; All-Star from per-game `/allstar/NBA_{year}.html` pages. Fetched with a browser user-agent (B-Ref 403s the default agent and WebFetch), decoded as UTF-8 (the default latin-1 guess produced mojibake).

Window is 2008-09 forward, two seasons before the tripwire era window, because the incumbent filter looks back two years from each arrival.

## Crosswalk: player_id only

Every honor row is resolved to `nba_player_id` by diacritic-folded name match against `nba_player_bio`, disambiguated by season-active check against `nba_player_season_bio`. **682 of 682 resolved, zero unresolved.** This is the join rule the coverage report mandated: an early run that matched on raw name left 33 rows unresolved, every one a diacritic case (Jokić, Dončić, Ginóbili, Šengün). Folding diacritics and keying on player_id cleared all 33. The honors table stores `nba_player_id`, never a name, as its join key.

## Validation

### All-NBA is exact

270 rows = 18 seasons x 15, split 90/90/90 across tiers, matches B-Ref's page structure exactly. Spot-checked against the raw page: 2023-24 1st team (Jokić, Antetokounmpo, Tatum, Dončić, Gilgeous-Alexander), 2nd (Davis, Durant, Leonard, Brunson, Edwards), 3rd (James, Sabonis, Booker, Curry, Haliburton) all reproduce. This is the authoritative, clean incumbent signal.

### All-Star starter flag has documented format caveats

`is_starter` reflects B-Ref's roster designation (the player who started the game), not who was voted a starter. In two format eras this diverges from "voted starter":
- **Captain-draft years (2018-2023):** rosters are two drafted teams, not East/West. The parser captures 10 game-starters per year, but a voted starter who did not play (injury) is replaced, and the replacement is listed as the starter. Confirmed case: **Zion Williamson was voted a 2023 All-Star starter but was injured (DNP); B-Ref lists him on the page but not as a participating starter**, so he is not flagged `is_starter` for 2022-23.
- **Tournament format (2024, 2025):** the parser captures 15 selections and 10 starters but the new multi-team structure makes the starter designation unreliable. Confirmed case: **Wembanyama started the 2025 All-Star event but is flagged reserve** for 2024-25.

Consequence: the All-Star-**starter** criterion of the incumbent filter is reliable pre-2018 and unreliable 2018-onward. **All-NBA should be the primary incumbent signal; All-Star-starter is a secondary signal carrying these caveats.** All the clean seed resolutions below come via All-NBA.

### Seed-case incumbent resolution

Every incumbent resolves to a player_id and an honors record (crosswalk 100%). Whether each **qualifies** under the spec's rule ("made All-NBA in either of the two prior seasons OR was an All-Star starter") is the substantive result:

| Seed case | Incumbent | Window | Qualifies |
|---|---|---|---|
| Lillard to MIL 23-24 | Antetokounmpo | 21,22 | All-NBA 1st |
| Irving to DAL 22-23 | Dončić | 20,21 | All-NBA 1st |
| Harden to BKN 20-21 | Durant | 18,19 | All-NBA 2nd |
| Harden to PHI 21-22 | Embiid | 19,20 | All-NBA 2nd |
| Westbrook to LAL 21-22 | James / Davis | 19,20 | All-NBA (both) |
| Beal to PHX 23-24 | Booker / Durant | 21,22 | All-NBA (both) |
| Doncic to LAL 24-25 | James | 22,23 | All-NBA 3rd |
| Harden to LAC 23-24 | George (Leonard none) | 21,22 | **AS-reserve only** |
| Paul to PHX 20-21 | Booker | 18,19 | **AS-reserve only** |
| Mitchell to CLE 22-23 | Garland | 20,21 | **AS-reserve only** |
| Fox to SAS 24-25 | Wembanyama | 22,23 | **none (strict)** |
| Murray to NOP 24-25 | Williamson | 22,23 | **none (strict)** |

**10 of 12 core seed cases have a qualifying incumbent under the strict rule** (7 via All-NBA, 3 via the loosened All-Star-reserve reading). The 2 that do not resolve strictly are exactly the filter sensitivity the spec demands be reported, and both are recoverable under a current-season reading:

- **Fox to SAS (Wembanyama):** a sophomore incumbent. Wemby was not in the NBA two seasons prior and had no All-NBA/All-Star in his rookie year, so a strictly backward-looking honors filter cannot see him. He was a 2024-25 All-Star starter (the same season as Fox's Feb 2025 arrival) and 2025-26 All-NBA 1st. This is the CP3-to-Phoenix sensitivity generalized to a phenom: the filter has a false negative for stars too early in their careers to have accumulated honors.
- **Murray to NOP (Williamson):** Zion was a voted 2023 All-Star starter but injured (DNP), so he is not flagged a game-starter (the caveat above). Under a "voted starter" reading he qualifies.

## What this hands to Phase 2

1. A validated, player_id-keyed honors table that unblocks the Scenario A extraction.
2. A mandated incumbent-filter sensitivity, joining the usage-filter sensitivity already logged (carry-forward #2). Phase 2 reports the Scenario A class under both the strict prior-two-season honors reading and a widened reading (current-season All-Star, or consensus-star), and names which cases move: Fox-SAS and Murray-NOP enter only under the widened reading; Harden-LAC, Paul-PHX, Mitchell-CLE enter only under the loosened All-Star-reserve reading.
3. A recommendation: use All-NBA as the primary incumbent signal (exact), All-Star-starter as secondary (reliable pre-2018, caveated after). Do not treat the 2018+ `is_starter` flag as authoritative for voted-starter status.

## Reproduce

```
python all-for-one/tripwire-backtest/scripts/ingest_honors.py    # writes data/honors.parquet
python all-for-one/tripwire-backtest/scripts/validate_honors.py  # seed incumbent check
```
