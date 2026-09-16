# M3: opponent cards, the West field

**Basis.** Series probabilities on net rating with the style overlay **off** (M2). Style shown as **descriptive only**. Matchups are observed 2025-26 possessions and are **evidence, not verdicts**: the median pairing is 4.8 partial possessions, pairings under 30 are flagged thin, and a pairing's standard error is measured at 0.14 points per matchup possession at 30 possessions and 0.08 at 100. Run `m3_opponent_cards_20260916T201505Z`.

**The yardstick is what a primary defender normally allows, not zero.** Across the league in 2025-26, a team's heaviest rotation defender on one of the top 150 offenders held him 0.05 to 0.10 below his own baseline (by possession band: 5-30 poss -0.05, 30-60 poss -0.07, 60-120 poss -0.07, 120+ poss -0.10). A heavy matchup is a designated stopper on possessions the offence did not choose, so running below baseline is the normal result and says nothing on its own. Each row is judged **beyond that norm**, and a matchup is called an **edge** only at 2 or more standard errors past it. After the adjustment the spread of league pairings is 0.95 standard errors (1.00 would be pure noise), so most of what separates one matchup from another is sampling. On the 79 observed rows below, the league's own rate of two-SE deviations among primary pairings would produce about 2.3 above and 0.8 below, with nothing special about these teams.

**Minnesota's top five against primary defenders, every opponent pooled.** Each player's 2025-26 pairings of 30+ possessions against a team's heaviest rotation defender on him, judged beyond the norm and set against the other 149 top offenders with five or more such pairings. A percentile near 0 means primary defenders held him more than they hold most scorers.

| player | pairings | possessions | beyond norm | in SEs | percentile |
|---|---:|---:|---:|---:|---:|
| Anthony Edwards | 21 | 1451 | -0.115 | -5.6 | 1 |
| Rudy Gobert | 29 | 2490 | +0.037 | +2.4 | 95 |
| LaMelo Ball | 16 | 806 | -0.042 | -1.5 | 14 |
| Jaden McDaniels | 20 | 1416 | +0.009 | +0.4 | 57 |
| Ayo Dosunmu | 12 | 614 | +0.017 | +0.5 | 63 |

**Confound check** (`m3_primary_defender_check.py`). Edwards's rank survives a baseline built from rotation defenders only (percentile 1, -5.3 SEs) and survives dropping the playoffs (percentile 5, -3.4 SEs; both changes together, 5). The playoffs sharpen it (Christian Braun drew 110 of his 145 possessions on Edwards in the first-round series, Devin Vassell 119 of 147 in the second), but the regular season alone already puts him at the 5th percentile of 149 top scorers. Read it as description: last season, the defender a team assigned to Edwards held him further under his own level than that assignment holds almost any other scorer. It does not say why, and it does not say 2026-27 will repeat it.

**Read the matchup numbers on their own scale.** They are points per *matchup* possession: the points the offender scored while that defender was on him, divided by the partial possessions they shared. He does not shoot on most of those possessions, so typical values run 0.2 to 0.5, not the 1.1 of team offence. That is why every row is set against the offender's own baseline across all defenders, and only the difference is meaningful.

**Minnesota.** Market **3.16%**, rank 6. Model **1.69%**. In 2025-26 Minnesota sat at league average on pace and size (z within 0.05 of zero), so a style contrast on either describes the opponent, not a Minnesota tendency.

---

## OKC

| | |
|---|---|
| model title odds | **16.72%** [15.05, 17.92] |
| market title odds | 22.49%, rank 2 |
| **Minnesota wins the series** | **0.101** [0.064, 0.129] |
| P(first-round opponent) | 0.249 |
| modelled offseason change | -0.24 net [-0.36, -0.14] |

**Offseason ledger.** Arrivals: Kenrich Williams (15.6 mpg, +0.70); Jared McCain (15.5 mpg, -0.17). Departures: Isaiah Joe (18.8 mpg, +1.97); Luguentz Dort (19.6 mpg, +0.39).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): OKC **forces more turnovers** than Minnesota (+1.57 against +0.27); OKC **crashes the offensive glass less** than Minnesota (-1.20 against -0.10); OKC **is smaller** than Minnesota (-0.59 against league average).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Shai Gilgeous-Alexander | Jaden McDaniels | 99 | 0.32 | 0.46 | -0.13 | -0.07 | **-0.06** | -0.74 | 12-21 | 2-3 | 3 |
| Chet Holmgren | Rudy Gobert | 39 | 0.36 | 0.29 | +0.07 | -0.07 | **+0.14** | +1.09 | 6-10 | 2-5 | 0 |
| Jalen Williams | Anthony Edwards | 29 *thin* | 0.14 | 0.31 | -0.17 | -0.05 | **-0.12** | -0.82 | 1-2 | 1-2 | 1 |
| Isaiah Hartenstein | Rudy Gobert | 99 | 0.10 | 0.19 | -0.09 | -0.07 | **-0.02** | -0.24 | 5-12 | 0-0 | 1 |
| Ajay Mitchell | Cody Williams | 15 *thin* | 0.60 | 0.27 | +0.32 | -0.05 | **+0.38** | +1.87 | 3-6 | 3-4 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Ajay Mitchell against Cody Williams, +0.38 beyond the norm over 15 possessions (+1.87 SEs, thin).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Cason Wallace | 89 | 0.21 | 0.41 | -0.20 | -0.07 | **-0.12** | -1.50 | 7-19 | 1-6 | 3 |
| Rudy Gobert | Isaiah Hartenstein | 99 | 0.08 | 0.17 | -0.09 | -0.07 | **-0.01** | -0.18 | 3-8 | 0-0 | 2 |
| LaMelo Ball | Jalen Williams | 8 *thin* | 0.27 | 0.36 | -0.10 | -0.05 | **-0.04** | -0.16 | 0-0 | 0-0 | 3 |
| Jaden McDaniels | Shai Gilgeous-Alexander | 88 | 0.21 | 0.24 | -0.03 | -0.07 | **+0.05** | +0.57 | 8-16 | 3-7 | 3 |
| Ayo Dosunmu | Shai Gilgeous-Alexander | 12 *thin* | 0.00 | 0.27 | -0.27 | -0.05 | **-0.22** | -0.98 | 0-0 | 0-0 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Jaden McDaniels against Shai Gilgeous-Alexander, +0.05 beyond the norm over 88 possessions (+0.57 SEs).

---

## SAS

| | |
|---|---|
| model title odds | **13.89%** [9.77, 17.52] |
| market title odds | 22.96%, rank 1 |
| **Minnesota wins the series** | **0.133** [0.066, 0.209] |
| P(first-round opponent) | 0.261 |
| modelled offseason change | +0.95 net [-0.23, +2.08] |

**Offseason ledger.** Arrivals: Tobias Harris (29.0 mpg, +2.68). Departures: Keldon Johnson (19.3 mpg, -0.99).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): SAS **forces fewer turnovers** than Minnesota (-1.24 against +0.27); SAS **is bigger** than Minnesota (+0.77 against league average); SAS **plays faster** than Minnesota (+0.71 against league average).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Victor Wembanyama | Rudy Gobert | 164 | 0.42 | 0.41 | +0.01 | -0.10 | **+0.11** | +1.82 | 28-53 | 7-21 | 3 |
| De'Aaron Fox | Jaden McDaniels | 217 | 0.24 | 0.30 | -0.05 | -0.10 | **+0.05** | +0.85 | 23-49 | 2-11 | 8 |
| Tobias Harris | LaMelo Ball | 7 *thin* | 0.41 | 0.25 | +0.16 | -0.05 | **+0.21** | +0.73 | 1-1 | 0-0 | 0 |
| Julian Champagnie | Anthony Edwards | 100 | 0.08 | 0.19 | -0.11 | -0.07 | **-0.04** | -0.49 | 3-9 | 2-7 | 1 |
| Stephon Castle | Anthony Edwards | 89 | 0.29 | 0.27 | +0.02 | -0.07 | **+0.09** | +1.13 | 10-18 | 1-3 | 7 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Victor Wembanyama against Rudy Gobert, +0.11 beyond the norm over 164 possessions (+1.82 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Devin Vassell | 147 | 0.14 | 0.41 | -0.27 | -0.10 | **-0.17** | -2.64 | 10-23 | 0-3 | 5 |
| Rudy Gobert | Victor Wembanyama | 171 | 0.09 | 0.17 | -0.07 | -0.10 | **+0.02** | +0.38 | 7-19 | 0-0 | 4 |
| LaMelo Ball | Stephon Castle | 30 *thin* | 0.34 | 0.36 | -0.03 | -0.05 | **+0.03** | +0.18 | 3-7 | 3-3 | 0 |
| Jaden McDaniels | Julian Champagnie | 111 | 0.31 | 0.24 | +0.07 | -0.07 | **+0.15** | +1.99 | 14-23 | 1-2 | 1 |
| Ayo Dosunmu | De'Aaron Fox | 121 | 0.18 | 0.27 | -0.09 | -0.10 | **+0.01** | +0.13 | 8-20 | 4-7 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Jaden McDaniels against Julian Champagnie, +0.15 beyond the norm over 111 possessions (+1.99 SEs). Held two or more SEs beyond the norm: Anthony Edwards against Devin Vassell, -0.17 beyond the norm over 147 possessions (-2.64 SEs).

---

## HOU

| | |
|---|---|
| model title odds | **5.45%** [5.03, 6.41] |
| market title odds | 1.61%, rank 14 |
| **Minnesota wins the series** | **0.255** [0.191, 0.312] |
| P(first-round opponent) | 0.195 |
| modelled offseason change | +0.13 net [+0.02, +0.37] |

**Offseason ledger.** Arrivals: Marcus Smart (26.0 mpg, +2.27); Bogdan Bogdanovic (13.8 mpg, +1.01). Departures: Dorian Finney-Smith (16.3 mpg, +1.98); Josh Okogie (14.7 mpg, +1.52).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): HOU **crashes the offensive glass harder** than Minnesota (+2.86 against -0.10); HOU **takes fewer threes** than Minnesota (-1.56 against +0.12); HOU **forces fewer turnovers** than Minnesota (-0.62 against +0.27).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Amen Thompson | Jaden McDaniels | 22 *thin* | 0.09 | 0.25 | -0.16 | -0.05 | **-0.10** | -0.62 | 1-1 | 0-0 | 1 |
| Kevin Durant | Jaden McDaniels | 138 | 0.27 | 0.37 | -0.10 | -0.10 | **-0.01** | -0.10 | 14-27 | 1-2 | 7 |
| Alperen Sengun | Rudy Gobert | 71 | 0.32 | 0.31 | +0.01 | -0.07 | **+0.08** | +0.92 | 11-22 | 0-2 | 4 |
| Jabari Smith Jr. | Jaden McDaniels | 20 *thin* | 0.20 | 0.23 | -0.03 | -0.05 | **+0.02** | +0.13 | 2-4 | 0-1 | 1 |
| Marcus Smart | Anthony Edwards | 26 *thin* | 0.00 | 0.16 | -0.16 | -0.05 | **-0.11** | -0.71 | 0-1 | 0-1 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Alperen Sengun against Rudy Gobert, +0.08 beyond the norm over 71 possessions (+0.92 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Marcus Smart | 41 | 0.00 | 0.41 | -0.41 | -0.07 | **-0.34** | -2.81 | 0-4 | 0-3 | 2 |
| Rudy Gobert | Alperen Sengun | 64 | 0.12 | 0.17 | -0.04 | -0.07 | **+0.03** | +0.30 | 4-7 | 0-0 | 1 |
| LaMelo Ball | Amen Thompson | 43 | 0.12 | 0.36 | -0.25 | -0.07 | **-0.18** | -1.51 | 2-6 | 1-4 | 2 |
| Jaden McDaniels | Kevin Durant | 105 | 0.18 | 0.24 | -0.06 | -0.07 | **+0.01** | +0.19 | 8-16 | 1-2 | 2 |
| Ayo Dosunmu | Amen Thompson | 29 *thin* | 0.14 | 0.27 | -0.13 | -0.05 | **-0.08** | -0.55 | 2-2 | 0-0 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Rudy Gobert against Alperen Sengun, +0.03 beyond the norm over 64 possessions (+0.30 SEs). Held two or more SEs beyond the norm: Anthony Edwards against Marcus Smart, -0.34 beyond the norm over 41 possessions (-2.81 SEs).

---

## DEN

| | |
|---|---|
| model title odds | **4.69%** [2.96, 7.53] |
| market title odds | 3.16%, rank 6 |
| **Minnesota wins the series** | **0.288** [0.225, 0.363] |
| P(first-round opponent) | 0.150 |
| modelled offseason change | -0.24 net [-1.19, +1.27] |

**Offseason ledger.** Arrivals: Tyus Jones (14.7 mpg, -1.24); Marvin Bagley III (19.2 mpg, +0.87); Zeke Nnaji (12.4 mpg, -0.86). Departures: Jonas Valančiūnas (15.7 mpg, +2.76); Tim Hardaway Jr. (20.8 mpg, -1.07); Peyton Watson (24.5 mpg, -0.14).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): DEN **forces fewer turnovers** than Minnesota (-2.03 against +0.27); DEN **gets to the rim less** than Minnesota (-0.42 against +0.32); DEN **crashes the offensive glass less** than Minnesota (-0.77 against -0.10).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Nikola Jokic | Rudy Gobert | 386 | 0.30 | 0.39 | -0.09 | -0.10 | **+0.00** | +0.11 | 45-96 | 9-31 | 18 |
| Jamal Murray | Jaden McDaniels | 338 | 0.25 | 0.36 | -0.12 | -0.10 | **-0.02** | -0.50 | 29-72 | 9-26 | 7 |
| Christian Braun | Anthony Edwards | 86 | 0.09 | 0.18 | -0.08 | -0.07 | **-0.01** | -0.10 | 2-8 | 0-1 | 0 |
| Cameron Johnson | Ayo Dosunmu | 66 | 0.06 | 0.20 | -0.14 | -0.07 | **-0.06** | -0.64 | 2-8 | 0-3 | 0 |
| Aaron Gordon | Jonathan Kuminga | 34 | 0.50 | 0.30 | +0.21 | -0.07 | **+0.28** | +2.05 | 5-9 | 4-6 | 1 |

*In one line:* **Edge for them:** Aaron Gordon against Jonathan Kuminga, +0.28 beyond the norm over 34 possessions (+2.05 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Christian Braun | 145 | 0.12 | 0.41 | -0.29 | -0.10 | **-0.20** | -3.01 | 7-18 | 1-5 | 2 |
| Rudy Gobert | Nikola Jokic | 404 | 0.10 | 0.17 | -0.07 | -0.10 | **+0.03** | +0.79 | 17-38 | 0-0 | 6 |
| LaMelo Ball | DeMar DeRozan | 9 *thin* | 0.00 | 0.36 | -0.36 | -0.05 | **-0.31** | -1.21 | 0-3 | 0-1 | 0 |
| Jaden McDaniels | Jamal Murray | 194 | 0.24 | 0.24 | -0.00 | -0.10 | **+0.09** | +1.68 | 20-36 | 3-8 | 2 |
| Ayo Dosunmu | Jamal Murray | 108 | 0.33 | 0.27 | +0.05 | -0.07 | **+0.13** | +1.69 | 13-18 | 5-6 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Ayo Dosunmu against Jamal Murray, +0.13 beyond the norm over 108 possessions (+1.69 SEs). Held two or more SEs beyond the norm: Anthony Edwards against Christian Braun, -0.20 beyond the norm over 145 possessions (-3.01 SEs).

---

## LAL

| | |
|---|---|
| model title odds | **3.77%** [2.34, 5.87] |
| market title odds | 2.13%, rank 12 |
| **Minnesota wins the series** | **0.347** [0.244, 0.554] |
| P(first-round opponent) | 0.110 |
| modelled offseason change | +1.75 net [+0.40, +3.06] |

**Offseason ledger.** Arrivals: Walker Kessler (32.5 mpg, +3.02); Sandro Mamukelashvili (24.9 mpg, +3.30); Matisse Thybulle (19.0 mpg, +2.60). Departures: LeBron James (31.0 mpg, +2.77); Marcus Smart (26.4 mpg, +2.27); Jaxson Hayes (17.9 mpg, +1.72).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): LAL **plays slower** than Minnesota (-1.63 against league average); LAL **is bigger** than Minnesota (+1.05 against league average); LAL **gets to the rim less** than Minnesota (-0.44 against +0.32).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Luka Doncic | Jaden McDaniels | 52 | 0.60 | 0.47 | +0.13 | -0.07 | **+0.20** | +1.80 | 11-17 | 3-6 | 3 |
| Austin Reaves | Jaden McDaniels | 47 | 0.36 | 0.33 | +0.03 | -0.07 | **+0.10** | +0.87 | 6-14 | 2-6 | 2 |
| Walker Kessler | none observed | 0 | | | | | | | | | |
| Jake LaRavia | Ayo Dosunmu | 17 *thin* | 0.12 | 0.16 | -0.04 | -0.05 | **+0.01** | +0.06 | 0-0 | 0-0 | 0 |
| Sandro Mamukelashvili | Rudy Gobert | 26 *thin* | 0.00 | 0.25 | -0.25 | -0.05 | **-0.19** | -1.26 | 0-4 | 0-3 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Luka Doncic against Jaden McDaniels, +0.20 beyond the norm over 52 possessions (+1.80 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Luka Doncic | 16 *thin* | 0.83 | 0.41 | +0.42 | -0.05 | **+0.47** | +2.38 | 6-12 | 1-3 | 0 |
| Rudy Gobert | Sandro Mamukelashvili | 38 | 0.10 | 0.17 | -0.06 | -0.07 | **+0.00** | +0.04 | 2-2 | 0-0 | 0 |
| LaMelo Ball | Quentin Grimes | 32 | 0.25 | 0.36 | -0.11 | -0.07 | **-0.04** | -0.32 | 2-6 | 1-5 | 0 |
| Jaden McDaniels | Luka Doncic | 46 | 0.22 | 0.24 | -0.02 | -0.07 | **+0.05** | +0.40 | 5-10 | 0-3 | 1 |
| Ayo Dosunmu | Quentin Grimes | 32 | 0.16 | 0.27 | -0.11 | -0.07 | **-0.04** | -0.32 | 1-4 | 1-1 | 0 |

*In one line:* **Edge for Minnesota:** Anthony Edwards against Luka Doncic, +0.47 beyond the norm over 16 possessions (+2.38 SEs, thin).

---

## PHX

| | |
|---|---|
| model title odds | **1.44%** [0.94, 2.66] |
| market title odds | 0.60%, rank 20 |
| **Minnesota wins the series** | **0.516** [0.417, 0.626] |
| P(first-round opponent) | 0.021 |
| modelled offseason change | -0.39 net [-1.06, +0.84] |

**Offseason ledger.** Arrivals: Miles Bridges (23.7 mpg, -0.57); Luke Kennard (14.9 mpg, +0.36). Departures: Grayson Allen (28.2 mpg, +0.94); Royce O'Neale (25.4 mpg, +0.76).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): PHX **gets to the rim less** than Minnesota (-1.40 against +0.32); PHX **forces more turnovers** than Minnesota (+1.61 against +0.27); PHX **crashes the offensive glass harder** than Minnesota (+0.95 against -0.10).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Devin Booker | Jaden McDaniels | 74 | 0.19 | 0.37 | -0.18 | -0.07 | **-0.11** | -1.20 | 3-15 | 0-4 | 5 |
| Collin Gillespie | LaMelo Ball | 38 | 0.08 | 0.21 | -0.13 | -0.07 | **-0.07** | -0.52 | 1-3 | 1-3 | 1 |
| Jordan Goodwin | Anthony Edwards | 33 | 0.06 | 0.20 | -0.14 | -0.07 | **-0.07** | -0.50 | 1-2 | 0-0 | 0 |
| Mark Williams | Rudy Gobert | 57 | 0.23 | 0.24 | -0.01 | -0.07 | **+0.05** | +0.52 | 4-6 | 1-1 | 0 |
| Dillon Brooks | Anthony Edwards | 40 | 0.38 | 0.35 | +0.03 | -0.07 | **+0.10** | +0.77 | 6-8 | 3-3 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Dillon Brooks against Anthony Edwards, +0.10 beyond the norm over 40 possessions (+0.77 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Jordan Goodwin | 48 | 0.19 | 0.41 | -0.22 | -0.07 | **-0.16** | -1.38 | 4-7 | 1-3 | 2 |
| Rudy Gobert | Mark Williams | 57 | 0.23 | 0.17 | +0.06 | -0.07 | **+0.13** | +1.22 | 6-10 | 0-0 | 0 |
| LaMelo Ball | Collin Gillespie | 38 | 0.29 | 0.36 | -0.07 | -0.07 | **-0.01** | -0.04 | 4-7 | 3-6 | 1 |
| Jaden McDaniels | Devin Booker | 54 | 0.13 | 0.24 | -0.11 | -0.07 | **-0.04** | -0.40 | 2-3 | 0-1 | 0 |
| Ayo Dosunmu | Jalen Green | 16 *thin* | 0.12 | 0.27 | -0.15 | -0.05 | **-0.09** | -0.49 | 1-2 | 0-0 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Rudy Gobert against Mark Williams, +0.13 beyond the norm over 57 possessions (+1.22 SEs).

---

## POR

| | |
|---|---|
| model title odds | **1.18%** [0.36, 1.95] |
| market title odds | 1.01%, rank 18 |
| **Minnesota wins the series** | **0.540** [0.418, 0.750] |
| P(first-round opponent) | 0.014 |
| modelled offseason change | +0.37 net [-1.35, +1.73] |

**Offseason ledger.** Arrivals: Branden Carlson (14.6 mpg, +2.87); Scoot Henderson (20.0 mpg, -2.07); Ja Morant (26.8 mpg, +1.08). Departures: Matisse Thybulle (16.7 mpg, +2.60); Jerami Grant (22.7 mpg, -1.32); Kris Murray (22.8 mpg, +1.08).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): POR **crashes the offensive glass harder** than Minnesota (+1.72 against -0.10); POR **takes more threes** than Minnesota (+1.29 against +0.12); POR **is bigger** than Minnesota (+1.15 against league average).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Toumani Camara | Anthony Edwards | 52 | 0.04 | 0.19 | -0.15 | -0.07 | **-0.08** | -0.77 | 1-3 | 0-1 | 2 |
| Deni Avdija | Jaden McDaniels | 92 | 0.29 | 0.36 | -0.07 | -0.07 | **+0.01** | +0.07 | 9-24 | 1-7 | 3 |
| Donovan Clingan | Rudy Gobert | 172 | 0.10 | 0.22 | -0.12 | -0.10 | **-0.03** | -0.43 | 7-16 | 2-10 | 2 |
| Jrue Holiday | Anthony Edwards | 50 | 0.34 | 0.26 | +0.07 | -0.07 | **+0.14** | +1.28 | 7-14 | 3-5 | 3 |
| Ja Morant | Jonathan Kuminga | 18 *thin* | 0.34 | 0.34 | -0.00 | -0.05 | **+0.05** | +0.26 | 2-3 | 0-1 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Jrue Holiday against Anthony Edwards, +0.14 beyond the norm over 50 possessions (+1.28 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Toumani Camara | 103 | 0.29 | 0.41 | -0.12 | -0.07 | **-0.05** | -0.61 | 11-24 | 5-10 | 5 |
| Rudy Gobert | Donovan Clingan | 169 | 0.16 | 0.17 | -0.01 | -0.10 | **+0.09** | +1.48 | 9-18 | 0-0 | 4 |
| LaMelo Ball | Toumani Camara | 28 *thin* | 0.00 | 0.36 | -0.36 | -0.05 | **-0.31** | -2.10 | 0-5 | 0-3 | 2 |
| Jaden McDaniels | Deni Avdija | 77 | 0.10 | 0.24 | -0.14 | -0.07 | **-0.06** | -0.71 | 3-10 | 1-1 | 1 |
| Ayo Dosunmu | Scoot Henderson | 44 | 0.20 | 0.27 | -0.07 | -0.07 | **-0.00** | -0.01 | 4-6 | 1-1 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Rudy Gobert against Donovan Clingan, +0.09 beyond the norm over 169 possessions (+1.48 SEs). Held two or more SEs beyond the norm: LaMelo Ball against Toumani Camara, -0.31 beyond the norm over 28 possessions (-2.10 SEs, thin).

---

## GSW

| | |
|---|---|
| model title odds | **0.14%** [0.01, 0.39] |
| market title odds | 1.35%, rank 15 |
| **Minnesota wins the series** | **0.739** [0.688, 0.785] |
| P(first-round opponent) | 0.000 |
| modelled offseason change | -1.97 net [-3.01, -0.20] |

**Offseason ledger.** Arrivals: Charles Bassey (13.5 mpg, +1.74); Brandon Williams (18.2 mpg, -0.24). Departures: Jimmy Butler III (32.8 mpg, +4.88); Moses Moody (22.4 mpg, +1.33).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): GSW **is smaller** than Minnesota (-2.18 against league average); GSW **takes more threes** than Minnesota (+1.96 against +0.12); GSW **gets to the rim less** than Minnesota (-0.75 against +0.32).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Stephen Curry | Jaden McDaniels | 76 | 0.41 | 0.41 | -0.00 | -0.07 | **+0.07** | +0.76 | 12-27 | 5-14 | 0 |
| Brandin Podziemski | Jaden McDaniels | 54 | 0.19 | 0.24 | -0.05 | -0.07 | **+0.02** | +0.14 | 3-6 | 2-2 | 0 |
| Kristaps Porzingis | Rudy Gobert | 30 *thin* | 0.20 | 0.34 | -0.14 | -0.05 | **-0.08** | -0.59 | 2-6 | 0-1 | 1 |
| Draymond Green | Rudy Gobert | 19 *thin* | 0.00 | 0.14 | -0.14 | -0.05 | **-0.09** | -0.51 | 0-2 | 0-2 | 0 |
| De'Anthony Melton | Anthony Edwards | 20 *thin* | 0.10 | 0.25 | -0.16 | -0.05 | **-0.10** | -0.59 | 0-2 | 0-1 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Stephen Curry against Jaden McDaniels, +0.07 beyond the norm over 76 possessions (+0.76 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | De'Anthony Melton | 26 *thin* | 0.08 | 0.41 | -0.33 | -0.05 | **-0.28** | -1.81 | 1-2 | 0-1 | 2 |
| Rudy Gobert | Kristaps Porzingis | 40 | 0.10 | 0.17 | -0.07 | -0.07 | **+0.00** | +0.01 | 2-2 | 0-0 | 0 |
| LaMelo Ball | Brandon Williams | 28 *thin* | 0.35 | 0.36 | -0.01 | -0.05 | **+0.04** | +0.28 | 4-8 | 2-4 | 1 |
| Jaden McDaniels | Stephen Curry | 50 | 0.10 | 0.24 | -0.14 | -0.07 | **-0.07** | -0.66 | 2-5 | 1-2 | 2 |
| Ayo Dosunmu | Brandon Williams | 27 *thin* | 0.37 | 0.27 | +0.10 | -0.05 | **+0.15** | +1.00 | 5-9 | 0-3 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Ayo Dosunmu against Brandon Williams, +0.15 beyond the norm over 27 possessions (+1.00 SEs, thin).

---
