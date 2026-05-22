# The 2023-24 to 2024-25 usage handoff: testing the Randle-forfeit thesis

**Date:** 2026-05-22
**Trigger:** Drafting Article 2. Bobby proposed a thesis for the "first wrong turn" section: the KAT-for-Randle swap was "not Randle taking KAT's possessions, it was Randle forfeiting them to Edwards," moving the team "from Ant and KAT having to share to Randle being okay without the ball." He flagged it explicitly for data verification. He also asked whether the Wolves replaced Conley, and whether Edwards is a less efficient playmaker than Conley.

## Method

`analyses/q0a_lafi/usage_handoff.py`. Minnesota, Regular Season, 2023-24 through 2025-26. Box-score season aggregates (`nba_player_stats`), minutes-weighted usage and assist rate (`nba_player_advanced_stats`), pick-and-roll efficiency (`nba_synergy_player_play_types`), roster acquisition (`nba_team_rosters`). Time-of-possession and on-ball volume from the earlier `hub_check.py`.

## Finding 1: the forfeit thesis does not hold

| Player / season | Usage rate | Time of poss share | On-ball creation poss |
|---|---|---|---|
| KAT 2023-24 | 27% | 7.0% | 369 |
| Randle 2024-25 | 25% | 12.0% | 423 |
| Edwards 2023-24 | 31% | 23.6% | 996 |
| Edwards 2024-25 | 31% | 26.3% | 1,128 |
| Edwards 2025-26 | 31% | 20.3% | 797 |

The thesis fails on its central claim. **Edwards' usage rate was flat at 31% across all three seasons.** He did not absorb a larger share of scoring possessions in 2024-25. There was no usage handoff to Edwards.

There is one small kernel of truth: Randle's usage (25%) was modestly below KAT's (27%), so Randle ended slightly fewer possessions as the scorer. But Randle was not a low-ball-dominance player. He held the ball *more* than KAT (12.0% time-of-possession vs 7.0%) and ran *more* on-ball creation (423 vs 369). KAT was a high-usage, low-time-of-possession player (quick-touch post-ups, catch-and-shoot, putbacks). Randle pounds the ball more and finishes fewer possessions. "Randle forfeited possessions to Edwards" is not what happened.

## Finding 2: the real driver is Conley's decline, unreplaced

What concentrated the offense onto Edwards was not the KAT/Randle swap. It was the collapse of the team's second initiator.

| Conley | 2023-24 | 2024-25 | 2025-26 |
|---|---|---|---|
| Minutes per game | 28.9 | 24.7 | 18.4 |
| Points per game | 11.4 | 8.2 | 4.5 |
| Usage | 16% | 14% | 11% |
| Assist-to-turnover | 4.40 | 4.25 | 4.62 |

Conley aged out of a meaningful role fast. The Wolves saw it coming and used a 2024 first-round pick on Rob Dillingham (acquired draft-night via San Antonio) as the bet on a replacement. Through two seasons that bet has not paid off: Dillingham played 49 games then 35, under 11 minutes a night, true shooting .48 then .39, role contracting. Caveat: he is 20; the bet is not dead, but it has not worked yet.

With Conley fading and unreplaced, Edwards ran the offense by default. His ball-handling rose (dribbles per touch 3.9 to 4.5, seconds per touch 4.3 to 4.8). That, not increased scoring, is what drove the ball-stickiness component from 35 to 69.

## Finding 3: Edwards is a far less efficient distributor than Conley

| | Conley AST/TO | Edwards AST/TO | Conley AST% | Edwards AST% |
|---|---|---|---|---|
| 2023-24 | 4.40 | 1.68 | 29% | 24% |
| 2024-25 | 4.25 | 1.44 | 24% | 21% |
| 2025-26 | 4.62 | 1.30 | 21% | 18% |

Bobby's theory holds, with a precise shape. As a pure distributor Edwards is not close to Conley: assist-to-turnover 1.3-1.7 against Conley's 4.2-4.6. And Edwards' own passing has declined every year as his ball-handling load rose (assist rate 24 to 21 to 18; AST/TO 1.7 to 1.4 to 1.3).

The nuance: Edwards is not a bad creator. His pick-and-roll ball-handler PPP graded at the 75th-86th league percentile across these seasons, better than Conley's recent marks. Edwards is an efficient pick-and-roll *scorer*. He is an inefficient pure *distributor*. The Wolves shifted offensive initiation from a low-mistake table-setter to a high-usage scorer, and the table-setting did not get replaced.

## Implications for Article 2

- The "first wrong turn" section is rewritten. The false Randle-misdirection is dropped. The true story: Edwards' scoring share never changed; the offense concentrated onto him because Conley declined and was not replaced, and Edwards is a weaker distributor than the man he replaced.
- Bobby's forfeit thesis is reported back as not supported, with the better data-true story offered in its place.

## Artifacts

`analyses/q0a_lafi/usage_handoff.py`. Re-runnable: `python -m analyses.q0a_lafi.usage_handoff`.
