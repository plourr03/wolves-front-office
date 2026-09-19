# D89. Postmortem RAPM refit, and the two article claims re-tested

*Possession points are now credited to the team that scored them (`lib/lineups.py`), so RAPM is refit on the corrected grain. Before values are the frozen pre-D89 tables.*

## The two claims

- **Claim 1: Gobert offence positive 2023-24 to clearly negative 2025-26** -> **VERIFIED**
- **Claim 2: DiVincenzo highest net RAPM in the 2025-26-only fit** -> **VERIFIED**

## Gobert's offensive RAPM by season-only fit

| season | before | after |
|---|---:|---:|
| 2023-24 | +2.70 | +2.62 |
| 2024-25 | -0.36 | -1.38 |
| 2025-26 | -3.20 | -4.12 |

## Wolves rotation, 2025-26-only fit

| player           |   net_before |   net_after |   d_net |   off_before |   off_after |   d_off |
|:-----------------|-------------:|------------:|--------:|-------------:|------------:|--------:|
| Anthony Edwards  |        -1.97 |       -1.17 |    0.8  |         1.37 |        1.99 |    0.62 |
| Rudy Gobert      |         1.98 |        1.22 |   -0.76 |        -3.2  |       -4.12 |   -0.91 |
| Naz Reid         |         2.7  |        1.83 |   -0.87 |         0.19 |        0.02 |   -0.17 |
| Julius Randle    |        -0.07 |        0.56 |    0.63 |         1.38 |        2.05 |    0.67 |
| Jaden McDaniels  |        -0.62 |       -0.44 |    0.18 |        -0.34 |       -0.2  |    0.14 |
| Mike Conley      |        -0.38 |       -1.01 |   -0.63 |        -0.1  |       -0.35 |   -0.25 |
| Donte DiVincenzo |         4.84 |        4.86 |    0.01 |         1.98 |        1.72 |   -0.26 |
| Ayo Dosunmu      |        -1.14 |       -2.94 |   -1.8  |        -0.45 |       -1.29 |   -0.85 |

## The fix, proved the same way as the stint fix
`lib/lineups.derive_possessions` credited a possession's points to whichever team the tracker had on offence. A made field goal ends the possession, so an and-one free throw arrived when the other team was already on offence and the point was credited to the wrong team. Points now go to the team that scored them.
Against `nba_games.pts`, on a league-wide sample of 48 games across three seasons and both season types, 96 team-games:
| basis | mean error | mean absolute | largest | exact |
|---|---:|---:|---:|---:|
| corrected (now) | +0.000 | 0.000 | 0 | 96 of 96 |
| legacy (before) | -0.042 | 3.167 | 10 | 14 of 96 |
The legacy error is **2.84% of all points** and sums to about zero across the two teams of a game, the same mirrored signature the stint layer had. `points_scored_legacy` keeps the old value per possession for diagnosis.

**A second correction rode along.** An and-one free throw used to END a possession, so the old grid carried a phantom possession for every one of them. The rebuilt league cache has **2.22% fewer possessions**, and every one of the removed possessions ended in `made_ft`. Possession counts, and therefore every per-100 denominator built on this cache, move by that much.

## Postmortem's pooled three-season fit
Mean absolute shift 0.234 in offensive RAPM and 0.432 in net, over 561 players. **Gobert was the top net RAPM in the sample at +6.18 and is now third at +4.77**, behind Wembanyama (+6.28). That retires the "highest net RAPM in the entire sample" line wherever it appears.

Largest offensive movers:

| player_name       |   off_rapm_b |   off_rapm_a |   d_off |
|:------------------|-------------:|-------------:|--------:|
| Julian Champagnie |         1.73 |         0.61 |   -1.12 |
| Rudy Gobert       |        -0.71 |        -1.79 |   -1.08 |
| Rob Dillingham    |        -1.64 |        -2.62 |   -0.98 |
| Kevin Durant      |         1.33 |         2.26 |    0.92 |
| Royce O'Neale     |         0.1  |         1.01 |    0.91 |
| Jordan McLaughlin |        -0.22 |         0.64 |    0.86 |
| Eric Gordon       |        -0.27 |         0.57 |    0.85 |
| Andrew Wiggins    |        -1.33 |        -0.5  |    0.82 |
| Mike Conley       |        -1.06 |        -0.24 |    0.82 |
| Dalano Banton     |        -0.22 |         0.6  |    0.82 |
