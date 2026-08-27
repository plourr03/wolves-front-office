# Cap reconciliation and the Green branches

## Reconciling $215,871,829 against $223,293,829

| component                                                |      amount | counts_toward_apron   | note                                                                                                                                |
|:---------------------------------------------------------|------------:|:----------------------|:------------------------------------------------------------------------------------------------------------------------------------|
| 13 contracted players (nba_player_contracts, 2026-08-26) | 215,871,829 | True                  | Green in, Kuminga out. This is the Phase 0 A.11 figure.                                                                             |
| Jonathan Kuminga, taxpayer MLE                           |   6,064,000 | True                  | Counts once signed. Status: reported, not officially announced.                                                                     |
| R4 14th-man placeholder                                  |   1,358,000 | False                 | NOT a CBA charge. A team is charged for empty slots only below TWELVE players; Minnesota is at 13. Shown separately as roster fill. |
| incomplete roster charge                                 |           0 | True                  | Zero, correctly: the charge applies only below 12 players.                                                                          |
| dead money                                               |           0 | True                  | Zero on the current book. Non-zero only in the stretch branch.                                                                      |
| free-agent cap holds                                     |  16,484,548 | False                 | CAP basis only. Never quote the cap-basis total as an apron figure.                                                                 |
| two-way contracts (Enrique Freeman)                      |           0 | False                 | Excluded from team salary.                                                                                                          |

**Canonical pre-Kuminga apron salary: $215,871,829** (13 contracted players).

**Canonical with Kuminga signed: $221,935,829** (14 contracted players), which is $249,829 over the second apron of $221,686,000.

## The Green branches, roster fill made explicit

| branch   |   n_players |   contracted |   dead_money |   roster_fill |   apron_team_salary |   vs_first_apron |   vs_second_apron | legal_roster_size   |
|:---------|------------:|-------------:|-------------:|--------------:|--------------------:|-----------------:|------------------:|:--------------------|
| trade    |          13 |  207,256,817 |            0 |             0 |         207,256,817 |        1,758,183 |        14,429,183 | False               |
| trade    |          14 |  207,256,817 |            0 |       1358000 |         208,614,817 |          400,183 |        13,071,183 | True                |
| trade    |          15 |  207,256,817 |            0 |       2716000 |         209,972,817 |         -957,817 |        11,713,183 | True                |
| stretch  |          13 |  207,256,817 |    4,893,004 |             0 |         212,149,821 |       -3,134,821 |         9,536,179 | False               |
| stretch  |          14 |  207,256,817 |    4,893,004 |       1358000 |         213,507,821 |       -4,492,821 |         8,178,179 | True                |
| stretch  |          15 |  207,256,817 |    4,893,004 |       2716000 |         214,865,821 |       -5,850,821 |         6,820,179 | True                |

Thresholds: first apron $209,015,000, second apron $221,686,000, tax $200,428,000, rookie minimum $1,358,000.
