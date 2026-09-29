# M3: opponent cards, the West field

**Basis.** Series probabilities on net rating with the style overlay **off** (M2). Style shown as **descriptive only**. Matchups are observed 2025-26 possessions and are **evidence, not verdicts**: the median pairing is 4.8 partial possessions, pairings under 30 are flagged thin, and a pairing's standard error is measured at 0.14 points per matchup possession at 30 possessions and 0.08 at 100. Run `m3_opponent_cards_20260929T100601Z`.

**The yardstick is what a primary defender normally allows, not zero.** Across the league in 2025-26, a team's heaviest rotation defender on one of the top 150 offenders held him 0.05 to 0.10 below his own baseline (by possession band: 5-30 poss -0.05, 30-60 poss -0.07, 60-120 poss -0.07, 120+ poss -0.10). A heavy matchup is a designated stopper on possessions the offence did not choose, so running below baseline is the normal result and says nothing on its own. Each row is judged **beyond that norm**, and a matchup is called an **edge** only at 2 or more standard errors past it. After the adjustment the spread of league pairings is 0.95 standard errors (1.00 would be pure noise), so most of what separates one matchup from another is sampling. On the 79 observed rows below, the league's own rate of two-SE deviations among primary pairings would produce about 2.3 above and 0.8 below, with nothing special about these teams.

**Minnesota's top five against primary defenders, every opponent pooled.** Each player's 2025-26 pairings of 30+ possessions against a team's heaviest rotation defender on him, judged beyond the norm and set against the other 149 top offenders with five or more such pairings. A percentile near 0 means primary defenders held him more than they hold most scorers.

| player | pairings | possessions | beyond norm | in SEs | percentile |
|---|---:|---:|---:|---:|---:|
| Anthony Edwards | 21 | 1451 | -0.115 | -5.6 | 1 |
| Rudy Gobert | 29 | 2490 | +0.037 | +2.4 | 95 |
| Jaden McDaniels | 20 | 1416 | +0.009 | +0.4 | 57 |
| LaMelo Ball | 16 | 806 | -0.042 | -1.5 | 14 |
| Ayo Dosunmu | 12 | 614 | +0.017 | +0.5 | 63 |

**Confound check** (`m3_primary_defender_check.py`). Edwards's rank survives a baseline built from rotation defenders only (percentile 1, -5.3 SEs) and survives dropping the playoffs (percentile 5, -3.4 SEs; both changes together, 5). The playoffs sharpen it (Christian Braun drew 110 of his 145 possessions on Edwards in the first-round series, Devin Vassell 119 of 147 in the second), but the regular season alone already puts him at the 5th percentile of 149 top scorers. Read it as description: last season, the defender a team assigned to Edwards held him further under his own level than that assignment holds almost any other scorer. It does not say why, and it does not say 2026-27 will repeat it.

**Read the matchup numbers on their own scale.** They are points per *matchup* possession: the points the offender scored while that defender was on him, divided by the partial possessions they shared. He does not shoot on most of those possessions, so typical values run 0.2 to 0.5, not the 1.1 of team offence. That is why every row is set against the offender's own baseline across all defenders, and only the difference is meaningful.

**Minnesota.** Market **3.16%**, rank 6. Model **2.76%**. In 2025-26 Minnesota sat at league average on pace and size (z within 0.05 of zero), so a style contrast on either describes the opponent, not a Minnesota tendency.

---

## OKC

| | |
|---|---|
| model title odds | **14.72%** [11.90, 17.54] |
| market title odds | 22.49%, rank 2 |
| **Minnesota wins the series** | **0.162** [0.134, 0.181] |
| P(first-round opponent) | 0.164 |
| modelled offseason change | -0.45 net [-0.66, -0.27] |

**Offseason ledger.** Arrivals: Jared McCain (15.4 mpg, -0.36); Aday Mara (16.2 mpg, -0.01). Departures: Isaiah Joe (18.8 mpg, +2.40); Luguentz Dort (19.6 mpg, +0.23).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): OKC **forces more turnovers** than Minnesota (+1.57 against +0.27); OKC **crashes the offensive glass less** than Minnesota (-1.20 against -0.10); OKC **is smaller** than Minnesota (-0.59 against league average).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Shai Gilgeous-Alexander | Jaden McDaniels | 99 | 0.32 | 0.46 | -0.13 | -0.07 | **-0.06** | -0.74 | 12-21 | 2-3 | 3 |
| Chet Holmgren | Rudy Gobert | 39 | 0.36 | 0.29 | +0.07 | -0.07 | **+0.14** | +1.09 | 6-10 | 2-5 | 0 |
| Jalen Williams | Anthony Edwards | 29 *thin* | 0.14 | 0.31 | -0.17 | -0.05 | **-0.12** | -0.82 | 1-2 | 1-2 | 1 |
| Isaiah Hartenstein | Rudy Gobert | 99 | 0.10 | 0.19 | -0.09 | -0.07 | **-0.02** | -0.24 | 5-12 | 0-0 | 1 |
| Ajay Mitchell | Anthony Edwards | 14 *thin* | 0.43 | 0.27 | +0.16 | -0.05 | **+0.21** | +1.00 | 3-6 | 0-1 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Chet Holmgren against Rudy Gobert, +0.14 beyond the norm over 39 possessions (+1.09 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Cason Wallace | 89 | 0.21 | 0.41 | -0.20 | -0.07 | **-0.12** | -1.50 | 7-19 | 1-6 | 3 |
| Rudy Gobert | Isaiah Hartenstein | 99 | 0.08 | 0.17 | -0.09 | -0.07 | **-0.01** | -0.18 | 3-8 | 0-0 | 2 |
| Jaden McDaniels | Shai Gilgeous-Alexander | 88 | 0.21 | 0.24 | -0.03 | -0.07 | **+0.05** | +0.57 | 8-16 | 3-7 | 3 |
| LaMelo Ball | Jalen Williams | 8 *thin* | 0.27 | 0.36 | -0.10 | -0.05 | **-0.04** | -0.16 | 0-0 | 0-0 | 3 |
| Ayo Dosunmu | Shai Gilgeous-Alexander | 12 *thin* | 0.00 | 0.27 | -0.27 | -0.05 | **-0.22** | -0.98 | 0-0 | 0-0 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Jaden McDaniels against Shai Gilgeous-Alexander, +0.05 beyond the norm over 88 possessions (+0.57 SEs).

---

## SAS

| | |
|---|---|
| model title odds | **13.80%** [9.70, 17.95] |
| market title odds | 22.96%, rank 1 |
| **Minnesota wins the series** | **0.180** [0.110, 0.249] |
| P(first-round opponent) | 0.176 |
| modelled offseason change | +1.20 net [-0.14, +2.67] |

**Offseason ledger.** Arrivals: Tobias Harris (29.0 mpg, +3.24). Departures: Keldon Johnson (18.2 mpg, -1.38).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): SAS **forces fewer turnovers** than Minnesota (-1.24 against +0.27); SAS **is bigger** than Minnesota (+0.77 against league average); SAS **plays faster** than Minnesota (+0.71 against league average).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Victor Wembanyama | Rudy Gobert | 164 | 0.42 | 0.41 | +0.01 | -0.10 | **+0.11** | +1.82 | 28-53 | 7-21 | 3 |
| De'Aaron Fox | Jaden McDaniels | 217 | 0.24 | 0.30 | -0.05 | -0.10 | **+0.05** | +0.85 | 23-49 | 2-11 | 8 |
| Tobias Harris | LaMelo Ball | 7 *thin* | 0.41 | 0.25 | +0.16 | -0.05 | **+0.21** | +0.73 | 1-1 | 0-0 | 0 |
| Devin Vassell | Anthony Edwards | 121 | 0.16 | 0.21 | -0.05 | -0.10 | **+0.05** | +0.64 | 8-16 | 3-8 | 2 |
| Julian Champagnie | Anthony Edwards | 100 | 0.08 | 0.19 | -0.11 | -0.07 | **-0.04** | -0.49 | 3-9 | 2-7 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Victor Wembanyama against Rudy Gobert, +0.11 beyond the norm over 164 possessions (+1.82 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Devin Vassell | 147 | 0.14 | 0.41 | -0.27 | -0.10 | **-0.17** | -2.64 | 10-23 | 0-3 | 5 |
| Rudy Gobert | Victor Wembanyama | 171 | 0.09 | 0.17 | -0.07 | -0.10 | **+0.02** | +0.38 | 7-19 | 0-0 | 4 |
| Jaden McDaniels | Julian Champagnie | 111 | 0.31 | 0.24 | +0.07 | -0.07 | **+0.15** | +1.99 | 14-23 | 1-2 | 1 |
| LaMelo Ball | Stephon Castle | 30 *thin* | 0.34 | 0.36 | -0.03 | -0.05 | **+0.03** | +0.18 | 3-7 | 3-3 | 0 |
| Ayo Dosunmu | De'Aaron Fox | 121 | 0.18 | 0.27 | -0.09 | -0.10 | **+0.01** | +0.13 | 8-20 | 4-7 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Jaden McDaniels against Julian Champagnie, +0.15 beyond the norm over 111 possessions (+1.99 SEs). Held two or more SEs beyond the norm: Anthony Edwards against Devin Vassell, -0.17 beyond the norm over 147 possessions (-2.64 SEs).

---

## DEN

| | |
|---|---|
| model title odds | **6.11%** [4.56, 8.63] |
| market title odds | 3.16%, rank 6 |
| **Minnesota wins the series** | **0.311** [0.247, 0.398] |
| P(first-round opponent) | 0.240 |
| modelled offseason change | +0.91 net [+0.11, +1.82] |

**Offseason ledger.** Arrivals: Marvin Bagley III (19.2 mpg, +1.07); Tyus Jones (14.7 mpg, -1.17); DeMar DeRozan (23.4 mpg, +0.70). Departures: Bruce Brown (18.7 mpg, -1.75); Tim Hardaway Jr. (21.6 mpg, -1.21); Jonas Valančiūnas (14.3 mpg, +1.71).

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
| Jaden McDaniels | Jamal Murray | 194 | 0.24 | 0.24 | -0.00 | -0.10 | **+0.09** | +1.68 | 20-36 | 3-8 | 2 |
| LaMelo Ball | DeMar DeRozan | 9 *thin* | 0.00 | 0.36 | -0.36 | -0.05 | **-0.31** | -1.21 | 0-3 | 0-1 | 0 |
| Ayo Dosunmu | Jamal Murray | 108 | 0.33 | 0.27 | +0.05 | -0.07 | **+0.13** | +1.69 | 13-18 | 5-6 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Ayo Dosunmu against Jamal Murray, +0.13 beyond the norm over 108 possessions (+1.69 SEs). Held two or more SEs beyond the norm: Anthony Edwards against Christian Braun, -0.20 beyond the norm over 145 possessions (-3.01 SEs).

---

## HOU

| | |
|---|---|
| model title odds | **5.44%** [4.97, 6.22] |
| market title odds | 1.61%, rank 14 |
| **Minnesota wins the series** | **0.330** [0.282, 0.372] |
| P(first-round opponent) | 0.234 |
| modelled offseason change | +0.40 net [+0.10, +0.81] |

**Offseason ledger.** Arrivals: Marcus Smart (26.0 mpg, +2.73); Bogdan Bogdanovic (13.8 mpg, +0.57). Departures: Dorian Finney-Smith (14.5 mpg, +1.47); Josh Okogie (15.8 mpg, +1.32).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): HOU **crashes the offensive glass harder** than Minnesota (+2.86 against -0.10); HOU **takes fewer threes** than Minnesota (-1.56 against +0.12); HOU **forces fewer turnovers** than Minnesota (-0.62 against +0.27).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Amen Thompson | Jaylen Clark | 25 *thin* | 0.41 | 0.25 | +0.16 | -0.05 | **+0.21** | +1.34 | 3-5 | 1-1 | 0 |
| Kevin Durant | Jaden McDaniels | 138 | 0.27 | 0.37 | -0.10 | -0.10 | **-0.01** | -0.10 | 14-27 | 1-2 | 7 |
| Alperen Sengun | Rudy Gobert | 71 | 0.32 | 0.31 | +0.01 | -0.07 | **+0.08** | +0.92 | 11-22 | 0-2 | 4 |
| Jabari Smith Jr. | Jaden McDaniels | 20 *thin* | 0.20 | 0.23 | -0.03 | -0.05 | **+0.02** | +0.13 | 2-4 | 0-1 | 1 |
| Marcus Smart | Anthony Edwards | 26 *thin* | 0.00 | 0.16 | -0.16 | -0.05 | **-0.11** | -0.71 | 0-1 | 0-1 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Amen Thompson against Jaylen Clark, +0.21 beyond the norm over 25 possessions (+1.34 SEs, thin).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Marcus Smart | 41 | 0.00 | 0.41 | -0.41 | -0.07 | **-0.34** | -2.81 | 0-4 | 0-3 | 2 |
| Rudy Gobert | Alperen Sengun | 64 | 0.12 | 0.17 | -0.04 | -0.07 | **+0.03** | +0.30 | 4-7 | 0-0 | 1 |
| Jaden McDaniels | Kevin Durant | 105 | 0.18 | 0.24 | -0.06 | -0.07 | **+0.01** | +0.19 | 8-16 | 1-2 | 2 |
| LaMelo Ball | Amen Thompson | 43 | 0.12 | 0.36 | -0.25 | -0.07 | **-0.18** | -1.51 | 2-6 | 1-4 | 2 |
| Ayo Dosunmu | Amen Thompson | 29 *thin* | 0.14 | 0.27 | -0.13 | -0.05 | **-0.08** | -0.55 | 2-2 | 0-0 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Rudy Gobert against Alperen Sengun, +0.03 beyond the norm over 64 possessions (+0.30 SEs). Held two or more SEs beyond the norm: Anthony Edwards against Marcus Smart, -0.34 beyond the norm over 41 possessions (-2.81 SEs).

---

## LAL

| | |
|---|---|
| model title odds | **2.61%** [1.27, 4.95] |
| market title odds | 2.13%, rank 12 |
| **Minnesota wins the series** | **0.524** [0.364, 0.650] |
| P(first-round opponent) | 0.088 |
| modelled offseason change | +0.92 net [-0.16, +2.70] |

**Offseason ledger.** Arrivals: Sandro Mamukelashvili (24.9 mpg, +3.26); Walker Kessler (31.4 mpg, +2.48); Matisse Thybulle (19.0 mpg, +2.76). Departures: LeBron James (31.0 mpg, +3.38); Marcus Smart (26.4 mpg, +2.73); Jaxson Hayes (17.9 mpg, +1.85).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): LAL **plays slower** than Minnesota (-1.63 against league average); LAL **is bigger** than Minnesota (+1.05 against league average); LAL **gets to the rim less** than Minnesota (-0.44 against +0.32).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Luka Doncic | Jaden McDaniels | 52 | 0.60 | 0.47 | +0.13 | -0.07 | **+0.20** | +1.80 | 11-17 | 3-6 | 3 |
| Austin Reaves | Jaden McDaniels | 47 | 0.36 | 0.33 | +0.03 | -0.07 | **+0.10** | +0.87 | 6-14 | 2-6 | 2 |
| Walker Kessler | none observed | 0 | | | | | | | | | |
| Sandro Mamukelashvili | Rudy Gobert | 26 *thin* | 0.00 | 0.25 | -0.25 | -0.05 | **-0.19** | -1.26 | 0-4 | 0-3 | 0 |
| Jake LaRavia | Ayo Dosunmu | 17 *thin* | 0.12 | 0.16 | -0.04 | -0.05 | **+0.01** | +0.06 | 0-0 | 0-0 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Luka Doncic against Jaden McDaniels, +0.20 beyond the norm over 52 possessions (+1.80 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Luka Doncic | 16 *thin* | 0.83 | 0.41 | +0.42 | -0.05 | **+0.47** | +2.38 | 6-12 | 1-3 | 0 |
| Rudy Gobert | Sandro Mamukelashvili | 38 | 0.10 | 0.17 | -0.06 | -0.07 | **+0.00** | +0.04 | 2-2 | 0-0 | 0 |
| Jaden McDaniels | Luka Doncic | 46 | 0.22 | 0.24 | -0.02 | -0.07 | **+0.05** | +0.40 | 5-10 | 0-3 | 1 |
| LaMelo Ball | Jake LaRavia | 10 *thin* | 0.61 | 0.36 | +0.25 | -0.05 | **+0.30** | +1.20 | 2-6 | 2-6 | 1 |
| Ayo Dosunmu | Collin Sexton | 26 *thin* | 0.12 | 0.27 | -0.15 | -0.05 | **-0.10** | -0.65 | 1-4 | 1-3 | 1 |

*In one line:* **Edge for Minnesota:** Anthony Edwards against Luka Doncic, +0.47 beyond the norm over 16 possessions (+2.38 SEs, thin).

---

## POR

| | |
|---|---|
| model title odds | **1.86%** [0.45, 2.82] |
| market title odds | 1.01%, rank 18 |
| **Minnesota wins the series** | **0.563** [0.442, 0.802] |
| P(first-round opponent) | 0.067 |
| modelled offseason change | +1.51 net [-1.13, +2.59] |

**Offseason ledger.** Arrivals: Ja Morant (29.8 mpg, +2.52); Branden Carlson (14.6 mpg, +2.79); Vit Krejci (20.1 mpg, -0.20). Departures: Matisse Thybulle (16.7 mpg, +2.76); Jerami Grant (24.7 mpg, -0.81); Kris Murray (19.5 mpg, +0.46).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): POR **crashes the offensive glass harder** than Minnesota (+1.72 against -0.10); POR **takes more threes** than Minnesota (+1.29 against +0.12); POR **is bigger** than Minnesota (+1.15 against league average).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Deni Avdija | Jaden McDaniels | 92 | 0.29 | 0.36 | -0.07 | -0.07 | **+0.01** | +0.07 | 9-24 | 1-7 | 3 |
| Toumani Camara | Anthony Edwards | 52 | 0.04 | 0.19 | -0.15 | -0.07 | **-0.08** | -0.77 | 1-3 | 0-1 | 2 |
| Jrue Holiday | Anthony Edwards | 50 | 0.34 | 0.26 | +0.07 | -0.07 | **+0.14** | +1.28 | 7-14 | 3-5 | 3 |
| Ja Morant | Jonathan Kuminga | 18 *thin* | 0.34 | 0.34 | -0.00 | -0.05 | **+0.05** | +0.26 | 2-3 | 0-1 | 0 |
| Donovan Clingan | Rudy Gobert | 172 | 0.10 | 0.22 | -0.12 | -0.10 | **-0.03** | -0.43 | 7-16 | 2-10 | 2 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Jrue Holiday against Anthony Edwards, +0.14 beyond the norm over 50 possessions (+1.28 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Toumani Camara | 103 | 0.29 | 0.41 | -0.12 | -0.07 | **-0.05** | -0.61 | 11-24 | 5-10 | 5 |
| Rudy Gobert | Donovan Clingan | 169 | 0.16 | 0.17 | -0.01 | -0.10 | **+0.09** | +1.48 | 9-18 | 0-0 | 4 |
| Jaden McDaniels | Deni Avdija | 77 | 0.10 | 0.24 | -0.14 | -0.07 | **-0.06** | -0.71 | 3-10 | 1-1 | 1 |
| LaMelo Ball | Toumani Camara | 28 *thin* | 0.00 | 0.36 | -0.36 | -0.05 | **-0.31** | -2.10 | 0-5 | 0-3 | 2 |
| Ayo Dosunmu | Jrue Holiday | 31 | 0.13 | 0.27 | -0.14 | -0.07 | **-0.07** | -0.53 | 2-4 | 0-2 | 0 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Rudy Gobert against Donovan Clingan, +0.09 beyond the norm over 169 possessions (+1.48 SEs). Held two or more SEs beyond the norm: LaMelo Ball against Toumani Camara, -0.31 beyond the norm over 28 possessions (-2.10 SEs, thin).

---

## PHX

| | |
|---|---|
| model title odds | **1.43%** [0.91, 2.55] |
| market title odds | 0.60%, rank 20 |
| **Minnesota wins the series** | **0.654** [0.624, 0.696] |
| P(first-round opponent) | 0.030 |
| modelled offseason change | -0.29 net [-0.76, +0.73] |

**Offseason ledger.** Arrivals: Luke Kennard (16.8 mpg, +0.28); Miles Bridges (19.9 mpg, -0.03). Departures: Grayson Allen (28.2 mpg, +1.59); Royce O'Neale (25.4 mpg, +0.37).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): PHX **gets to the rim less** than Minnesota (-1.40 against +0.32); PHX **forces more turnovers** than Minnesota (+1.61 against +0.27); PHX **crashes the offensive glass harder** than Minnesota (+0.95 against -0.10).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Devin Booker | Jaden McDaniels | 74 | 0.19 | 0.37 | -0.18 | -0.07 | **-0.11** | -1.20 | 3-15 | 0-4 | 5 |
| Collin Gillespie | LaMelo Ball | 38 | 0.08 | 0.21 | -0.13 | -0.07 | **-0.07** | -0.52 | 1-3 | 1-3 | 1 |
| Jordan Goodwin | Anthony Edwards | 33 | 0.06 | 0.20 | -0.14 | -0.07 | **-0.07** | -0.50 | 1-2 | 0-0 | 0 |
| Dillon Brooks | Anthony Edwards | 40 | 0.38 | 0.35 | +0.03 | -0.07 | **+0.10** | +0.77 | 6-8 | 3-3 | 1 |
| Oso Ighodaro | Rudy Gobert | 51 | 0.19 | 0.15 | +0.04 | -0.07 | **+0.11** | +0.99 | 4-7 | 0-0 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Oso Ighodaro against Rudy Gobert, +0.11 beyond the norm over 51 possessions (+0.99 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | Jordan Goodwin | 48 | 0.19 | 0.41 | -0.22 | -0.07 | **-0.16** | -1.38 | 4-7 | 1-3 | 2 |
| Rudy Gobert | Mark Williams | 57 | 0.23 | 0.17 | +0.06 | -0.07 | **+0.13** | +1.22 | 6-10 | 0-0 | 0 |
| Jaden McDaniels | Devin Booker | 54 | 0.13 | 0.24 | -0.11 | -0.07 | **-0.04** | -0.40 | 2-3 | 0-1 | 0 |
| LaMelo Ball | Collin Gillespie | 38 | 0.29 | 0.36 | -0.07 | -0.07 | **-0.01** | -0.04 | 4-7 | 3-6 | 1 |
| Ayo Dosunmu | Jalen Green | 16 *thin* | 0.12 | 0.27 | -0.15 | -0.05 | **-0.09** | -0.49 | 1-2 | 0-0 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Rudy Gobert against Mark Williams, +0.13 beyond the norm over 57 possessions (+1.22 SEs).

---

## GSW

| | |
|---|---|
| model title odds | **0.06%** [0.00, 0.15] |
| market title odds | 1.35%, rank 15 |
| **Minnesota wins the series** | **0.848** [0.784, 0.903] |
| P(first-round opponent) | 0.000 |
| modelled offseason change | -2.73 net [-4.03, -1.18] |

**Offseason ledger.** Arrivals: Brandon Williams (17.8 mpg, +0.25); Yaxel Lendeborg (15.8 mpg, +0.02). Departures: Jimmy Butler III (32.8 mpg, +5.90); Moses Moody (21.2 mpg, +1.30).

**Style, descriptive only** (2025-26, z-scored, not adjusted for this summer's moves): GSW **is smaller** than Minnesota (-2.18 against league average); GSW **takes more threes** than Minnesota (+1.96 against +0.12); GSW **gets to the rim less** than Minnesota (-0.75 against +0.32).

**Their offence against Minnesota's defenders (above the norm = they hurt Minnesota)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Stephen Curry | Jaden McDaniels | 76 | 0.41 | 0.41 | -0.00 | -0.07 | **+0.07** | +0.76 | 12-27 | 5-14 | 0 |
| Brandin Podziemski | Jaden McDaniels | 54 | 0.19 | 0.24 | -0.05 | -0.07 | **+0.02** | +0.14 | 3-6 | 2-2 | 0 |
| Draymond Green | Rudy Gobert | 19 *thin* | 0.00 | 0.14 | -0.14 | -0.05 | **-0.09** | -0.51 | 0-2 | 0-2 | 0 |
| Kristaps Porzingis | Rudy Gobert | 30 *thin* | 0.20 | 0.34 | -0.14 | -0.05 | **-0.08** | -0.59 | 2-6 | 0-1 | 1 |
| Al Horford | Rudy Gobert | 11 *thin* | 0.00 | 0.19 | -0.19 | -0.05 | **-0.13** | -0.57 | 0-1 | 0-1 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: Stephen Curry against Jaden McDaniels, +0.07 beyond the norm over 76 possessions (+0.76 SEs).

**Minnesota's offence against their defenders (above the norm = Minnesota hurts them)**

| offence | guarded most by | poss | pts per matchup poss | his baseline | vs baseline | primary-defender norm | beyond norm | in SEs | FG | 3P | TOV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| Anthony Edwards | De'Anthony Melton | 26 *thin* | 0.08 | 0.41 | -0.33 | -0.05 | **-0.28** | -1.81 | 1-2 | 0-1 | 2 |
| Rudy Gobert | Kristaps Porzingis | 40 | 0.10 | 0.17 | -0.07 | -0.07 | **+0.00** | +0.01 | 2-2 | 0-0 | 0 |
| Jaden McDaniels | Stephen Curry | 50 | 0.10 | 0.24 | -0.14 | -0.07 | **-0.07** | -0.66 | 2-5 | 1-2 | 2 |
| LaMelo Ball | De'Anthony Melton | 18 *thin* | 0.51 | 0.36 | +0.15 | -0.05 | **+0.20** | +1.07 | 3-6 | 1-4 | 1 |
| Ayo Dosunmu | Brandin Podziemski | 24 *thin* | 0.08 | 0.27 | -0.19 | -0.05 | **-0.14** | -0.86 | 1-5 | 0-1 | 1 |

*In one line:* **no edge.** No matchup ran two standard errors above what a primary defender normally allows. Closest: LaMelo Ball against De'Anthony Melton, +0.20 beyond the norm over 18 possessions (+1.07 SEs, thin).

---
