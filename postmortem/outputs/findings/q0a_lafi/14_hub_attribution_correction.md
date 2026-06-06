# Hub attribution correction: the 2024-25 "single-star" was Edwards, not Randle

**Date:** 2026-05-22
**Trigger:** Drafting Article 2 ("How They Got Here"). Bobby questioned the claim that Julius Randle "became the new center of gravity" in 2024-25. The claim was inherited from the LAFI deliverable's narrative and had never been verified at the player grain.

## The question

In 2024-25, the Wolves' LAFI ball-stickiness component spiked from 35 to 69, the signature of a single-player-dominated ("single-star pickup") offense. Which player did the offense concentrate around?

## The prior (what the deliverable assumed)

The Q0A LAFI deliverable (`11_wolves_lafi_deliverable.md`, Section 2, Act 3) states: "Randle integration. Q3-leaning. **Randle dominated possessions as the new hub.** Stickiness rose sharply (69)." The Component 1 eye-test (`01_component1_ball_stickiness.md`) had floated "Randle dominated the ball as the new offensive hub" as an unverified Phase 5 hypothesis (lines 49, 69), and its own leaderboard table simultaneously listed the top time-of-possession handler in 2024-25 as **Anthony Edwards**. The hypothesis was never tested; the deliverable narrative promoted it to fact.

## Method

`analyses/q0a_lafi/hub_check.py`. Minnesota, Regular Season, 2023-24 through 2025-26. Three independent measures:

1. Time of possession (`nba_player_tracking_season`, measure `Possessions`).
2. Touches and seconds / dribbles per touch (same table).
3. On-ball creation volume: raw Synergy possessions for Isolation + PRBallHandler + Postup (`nba_synergy_player_play_types`).

## The data

**Time of possession (share of team total ball-handling time):**

| Season | 1st | 2nd | 3rd |
|---|---|---|---|
| 2023-24 | Edwards 23.6% | Conley 22.2% | Alexander-Walker 11.2% |
| 2024-25 | **Edwards 26.3%** | Conley 13.9% | **Randle 12.0%** |
| 2025-26 | Edwards 20.3% | Randle 14.8% | Dosunmu 11.2% |

**On-ball creation volume (Synergy raw possessions, Iso + PRBallHandler + Postup):**

| Season | Edwards | Randle | Edwards / Randle ratio |
|---|---|---|---|
| 2023-24 | 996 | (KAT 369) | n/a |
| 2024-25 | **1,128** | **423** | 2.67x |
| 2025-26 | 797 | 566 | 1.41x |

## The finding

**The 2024-25 single-star was Anthony Edwards, not Julius Randle.** The deliverable's "Randle dominated possessions as the new hub" is false.

- Edwards held the ball more than twice as long as Randle and accounted for about a quarter of the team's total ball-handling time. Randle ranked **third** in time of possession, behind an aging Conley.
- Edwards ran 1,128 on-ball creation possessions to Randle's 423, a 2.67-to-1 margin.
- The ball-stickiness spike from 35 to 69 was driven by a guard-rotation change, not by Randle. In 2023-24, ball-handling was split almost evenly between Edwards (23.6%) and Conley (22.2%). In 2024-25, Conley's share fell by more than a third as he declined, and Edwards absorbed it. A two-guard offense became a one-man engine.
- 2025-26 is the genuine decentralization: Edwards' on-ball volume fell from 1,128 to 797, his time-of-possession share dropped to 20.3%, and the Edwards-to-#2 creation ratio compressed from 2.67x to 1.41x. This is the "distributed pickup" step, and it is data-confirmed.

The two-step drift narrative (organized to single-star pickup to distributed pickup) holds. Only the attribution of the single star was wrong. Randle added isolation and post-up volume as the clear number two, but he was never the hub.

This is consistent with Q0D: Edwards' PRBallHandler usage peaked in 2024-25 (688 raw possessions) and was cut to 353 in 2025-26.

## Implications

- **Article 2:** the "first wrong turn" section is corrected to name Edwards as the single star, with the misdirection (the obvious guess is Randle) used deliberately. Fixed in the draft.
- **Q0A LAFI deliverable (`11_wolves_lafi_deliverable.md`), Section 2, Act 3:** the "Randle dominated possessions as the new hub" sentence is wrong and should be marked. Recommend an in-place correction marker.
- This is the sixth material correction the project has caught. Pattern holds: a single-source narrative claim, never verified at the right grain, refined under scrutiny. Bobby flagged it.

## Artifacts

`analyses/q0a_lafi/hub_check.py`. Re-runnable: `python -m analyses.q0a_lafi.hub_check`.
