# Gobert Usage Audit: Utah vs Minnesota (feeds Piece 2, "It's Not (All) Gobert's Fault")

_Measured, not asserted. Every number here is a warehouse pull across Gobert's full career
(synergy play types, NBA tracking, hustle stats, and play-by-play all cover 2013-14 to 2025-26
locally). The misuse claim is reported exactly as the data supports it, and where the data
contradicts the simple story, or contradicts our own outline, it prints._

Scripts: `pull_gobert_usage.py`, `analyze_gobert_usage.py`, `check_gobert_ranks.py`.
Data: `data/cache/gobert_usage_final.csv`.

## The headline: the delivery system, not the player

Comparing Gobert's Utah prime as a full-time starter (2016-17 through 2021-22) to his four
Minnesota seasons (2022-23 through 2025-26):

| measure | Utah prime (16-22) | Minnesota (22-26) | change |
|---|---|---|---|
| roll-man possessions / game | 3.27 | 2.06 | **-37%** |
| roll-man points per possession | 1.314 | 1.244 | -0.07 (still elite) |
| roll-man share of his offense | 26.0% | 19.1% | -6.9 pp |
| touches / game | 59.5 | 44.3 | **-25%** |
| frontcourt touches / game | 32.9 | 23.9 | -27% |
| screen assists / game | 6.26 | 4.63 | -26% |
| dunk attempts / game | 3.50 | 3.22 | **only -8%** |
| meaningful PnR ball-handlers around him | 4.0 | 2.0 | **-50%** |

The pattern is consistent: he is **involved much less** (touches, roll-man volume, screen
assists all down a quarter or more), his **finishing remains elite** (roll-man PPP 1.31 to 1.24,
dunk conversion 92.7% to 91.2%), and the **live-dribble passing around him was halved**. The
decline in his offensive box and impact numbers is, in large part, a decline in opportunity, not
in execution.

## Season by season

| season | team | gp | mpg | roll/g | roll PPP | roll% | screen ast/g | touch/g | dunk/g | dunk FG% | meaningful PnR BHs | top ball-handler |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2016-17 | UTA | 81 | 33.4 | 2.54 | 1.379 | 20.9% | 6.16 | 58.6 | 3.02 | 95.9% | 4 | Hayward (419) |
| 2017-18 | UTA | 56 | 31.9 | 2.88 | 1.280 | 23.8% | 6.18 | 59.5 | 2.93 | 92.1% | 4 | Mitchell (660) |
| 2018-19 | UTA | 81 | 31.3 | 3.36 | 1.349 | 25.3% | 5.90 | 58.9 | 4.21 | 89.7% | 3 | Mitchell (857) |
| 2019-20 | UTA | 68 | 33.9 | 3.54 | 1.216 | 27.4% | 6.93 | 61.0 | 3.49 | 93.2% | 6 | Mitchell (798) |
| 2020-21 | UTA | 71 | 30.3 | 3.86 | 1.339 | 31.7% | 6.11 | n/a | 3.52 | 92.4% | 4 | Mitchell (594) |
| 2021-22 | UTA | 66 | 31.6 | 3.41 | 1.320 | 27.1% | 6.26 | (corrupt) | 3.80 | 92.8% | 3 | Mitchell (806) |
| 2022-23 | MIN | 70 | 30.3 | 2.07 | 1.255 | 17.7% | 4.93 | 43.5 | 3.03 | 94.3% | 3 | Edwards (541) |
| 2023-24 | MIN | 76 | 33.7 | 2.47 | 1.239 | 20.8% | 4.76 | 45.9 | 3.57 | 91.5% | 2 | Edwards (576) |
| 2024-25 | MIN | 72 | 32.6 | 2.25 | 1.210 | 22.3% | 4.78 | 43.3 | 3.50 | 89.3% | 2 | Edwards (688) |
| 2025-26 | MIN | 76 | 30.8 | **1.46** | 1.270 | 15.7% | 4.04 | 44.6 | 2.78 | 89.6% | **1** | Edwards (353) |

("meaningful PnR BHs" = teammates that roster-season with at least 150 offensive pick-and-roll
ball-handler possessions, the proxy for live-dribble creators who can feed a roll man. "roll%"
is the share of Gobert's own offensive possessions that came as the roll man.)

## The misuse claim, measured

**1. The roll-man hub was dismantled.** In Utah's last four full seasons Gobert ran the
roll a peak 3.4 to 3.9 times a game, and the roll was a quarter to nearly a third of his entire
offensive diet (31.7% in 2020-21). In Minnesota that fell to roughly 2 a game and under 20% of
his offense, bottoming at **1.46 a game and 15.7% in 2025-26**, his lowest as a starter. This is
the single cleanest number in the audit: the action he is elite at, cut by more than a third.

**2. The live-dribble delivery system was halved.** Utah surrounded him with three to six
genuine pick-and-roll ball-handlers every year (Mitchell, Conley, Hayward, Ingles, Clarkson,
Hood, Rubio). Minnesota fielded three in 2022-23, then two, then **one in 2025-26**: Anthony
Edwards and no one else cleared the 150-possession bar. Conley aged below it (493 PnR ball-handler
possessions in Utah's 2021-22, down to 169 by 2024-25 and under the line in 2025-26), and
DiVincenzo is not a high-volume pick-and-roll initiator. A roll man with one feeder gets fewer
quality feeds, regardless of how well he finishes.

**3. His finishing never left.** Roll-man PPP stayed at 1.21 to 1.27 in Minnesota (73rd
percentile league-wide, still above average), and dunk conversion held near 90%. He did not get
worse at the job. He got far less of it.

## The honest other side (the parenthetical is load-bearing)

The audit does not absolve him, and three measured facts keep the piece honest:

- **He is a finish-only non-creator.** Across his career his assist-to-pass rate sits at 3 to 5%
  (roughly 1 to 2 assists a game on 2,500-plus passes). He moves the ball but creates almost
  nothing off it. That is why a thinned delivery system is so costly to *him* specifically: a big
  who can attack a closeout or make a pick-and-roll read has somewhere for his offense to go when
  the feeds dry up. Gobert does not. Cut his clean feeds and his offensive value has no fallback,
  which is the structural reason his DARKO offensive grade is genuinely negative (ODPM about -2)
  even as his net DARKO is positive on defense.
- **The hands limitation is real, not invented.** It does not show up as a turnover spike (his
  roll-man turnover rate held in the 8 to 11% range, normal for the role), but it is the reason
  his game was always *managed*: he converts clean, on-time deliveries at an elite rate and does
  not bail out bad ones. Utah built around that. Minnesota largely did not.
- **The negative offensive grade is correct on its own terms.** A center who needs the system to
  manufacture his offense, and whose system stopped doing so, is a negative offensive player in
  that environment. "It's not all his fault" is not "it's none his fault." The delivery system
  collapsed *and* he is the kind of player who cannot rescue himself when it does.

## Where the data contradicts the simple story (printed, not smoothed)

- **Dunk volume barely moved (-8%) while roll-man possessions fell 37%.** If Minnesota had truly
  buried his finishing, his dunks would have cratered with his roll-man reps. They did not. The
  honest reading: Minnesota never stopped feeding his **rim gravity**, it stopped running him as
  the **half-court roll hub**. Edwards lobs, transition, and cuts still find him; the structured
  pick-and-roll diet is what shrank. The accurate claim is narrow and survives contact: not "they
  stopped throwing him lobs," but "they stopped building the half-court offense through his
  screen."
- **The decline is not monotonic; 2025-26 is the acute year.** Roll-man volume actually ticked
  up in 2023-24 and 2024-25 (2.47 and 2.25 a game) before collapsing to 1.46 in 2025-26, the same
  season the delivery count fell to one. The structural problem is real across the Minnesota
  tenure, but it reached its floor specifically this past season, alongside the thinnest
  live-dribble environment of his career.
- **Our own outline overstated the screen-assist claim. Correcting it.** The draft asserts
  "league-leading screen assists every tracked year" in Utah. He did not. He **led the league
  outright in 2018-19, 2019-20, and 2020-21**, but was 2nd behind Gortat (2016-17), 4th behind
  Steven Adams (2017-18), and 2nd behind Adams (2021-22). The defensible claim is "perennial
  top-four, league-leading in three of his last four Utah seasons." Importantly, he stayed elite
  at it in Minnesota too: top-two every year behind Sabonis, and **first in the entire league in
  2025-26 (307)**. So his screens still generate points for others, he just finishes far fewer of
  them himself, which sharpens rather than softens the misuse reading.
- **Roll-man efficiency is "elite then, above-average now," not "best in basketball" flat.** His
  roll-man percentile ran 80th to 95th in his Utah peak (95th in 2016-17, 93rd in 2018-19) and
  sits at the 73rd in Minnesota. Elite is the right word for the Utah peak seasons; "still a
  clearly positive roll finisher" is the right word for now.

## Addendum A: scheme choice vs feeder scarcity (separating the two causes)

The roll-man collapse has two distinct causes, and the team-level data separates them. Pulling each
team's offensive share run as a pick-and-roll BALL-HANDLER action (the scheme-frequency measure, from
`nba_synergy_team_play_types`) against the league average:

| era | team PnR ball-handler frequency | total team PnR poss |
|---|---|---|
| Utah prime (2016-17 to 2021-22) | **+3.2 to +6.8 pp ABOVE league** every year | 1,719 to 2,046 |
| Minnesota (2022-23 to 2025-26) | **at or BELOW league** (-0.6 to -2.2 pp) | 1,180 to 1,482 |
| Minnesota 2025-26 specifically | 13.1%, **-2.2 pp below league, the lowest of the era** | 1,180 (lowest) |

This is the load-bearing nuance. **Minnesota does not just lack the feeders; it runs a fundamentally
less pick-and-roll-heavy scheme than Utah did.** Quin Snyder's Utah built an offense around Gobert's
screen and ran 4 to 7 percentage points more PnR ball-handler than the league; Finch's Minnesota
runs an Edwards-on-ball, transition, and isolation offense that sits below league average in PnR
frequency. (Telling corroboration: once Utah traded Gobert, its own PnR frequency fell to
league-average, the scheme was his.) So the diminished roll diet is scheme AND personnel, and the two
compound. The misuse reading is partly an indictment of an offensive design that structurally
underuses the action that makes him a weapon, not just of a thin roster.

And the 2025-26 acute year has a named mechanism on the feeder side too: **Edwards' own PnR
ball-handler volume nearly halved, from 688 possessions in 2024-25 to 353 in 2025-26** (33.3% of his
offense down to 23.5%), as he shifted toward isolation, transition, and off-ball work. His PnR
efficiency held (about 1.00 points per possession), so this is a role/scheme shift, not a decline,
but it starved Gobert's roll in the one season the delivery count also fell to one.

## Addendum B: the Piece 2 to Piece 7 bridge (does the plan restore the delivery system?)

Projecting each Portfolio A/C addition's historical PnR ball-handler volume onto a full Wolves season
(poss per game times 72, against the same 150-possession "meaningful feeder" bar the audit uses):

| player | role in plan | projected full-season PnR ball-handler poss | clears 150 bar? |
|---|---|---|---|
| Anthony Edwards | incumbent | 353 (2025-26 actual) | yes |
| Ayo Dosunmu | re-sign, full season | ~208 | yes |
| Ajay Mitchell | Portfolio C flier | ~357 | yes |
| CJ McCollum | MLE tier | ~472 | yes |
| Norman Powell | MLE tier | ~264 | yes |
| Miles McBride | Portfolio A flier | ~133 | no (connector / spot-up) |
| Kevin Huerter | MLE tier | ~105 | no (spot-up wing) |
| Jalen Smith | stretch five | none (not an initiator) | no, and correctly so |

**The plan moves the delivery-system count from 1 (2025-26) toward 3.** Portfolio C (the Mitchell
flier) lands at Edwards plus Dosunmu plus Mitchell, **three feeders**, and reaches four if the MLE is
a pick-and-roll guard like McCollum. Portfolio A (the McBride flier) lands at two on its own, because
McBride does not clear the bar, and reaches **three** only if the MLE slot is a ball-handler
(McCollum or Powell) rather than a spot-up shooter (Huerter). So the choice WITHIN the MLE tier is a
delivery-system decision, not just a shooting one: a McCollum-type restores a feeder, a Huerter-type
does not.

This is the bridge from Piece 2 to Piece 7. The usage audit diagnoses the disease (one live-dribble
feeder around Gobert in 2025-26, down from four to six in Utah); the capstone plan's prescription
restores the delivery environment to roughly Utah levels (three feeders) WITHOUT trading him. **Two
honest caveats:** (1) restoring the feeders raises the CEILING for his roll-man volume but does not
guarantee it, because the team-frequency data shows Minnesota runs below-average PnR by design, so
the personnel is necessary and a scheme shift toward more pick-and-roll is also required; and (2) the
projections lean on health (Dosunmu and McCollum have missed time, Conley at 39 and a
post-Achilles DiVincenzo no longer backfill the bar), so three is the plan's target, not a guarantee.

**The Finch-floated internal branch (Shannon on the ball), priced as the labeled scenario it is.**
On June 11, 2026 (KFAN, via Yahoo/ClutchPoints) Finch confirmed the playmaking need directly ("we
definitely need another ball handler and playmaker" to take load off Edwards, 31.4% usage, 21 games
missed) and floated an internal piece of the answer: Terrence Shannon Jr. taking on-ball reps in the
starting unit, conceding the earlier off-ball deployment was a misuse. The data says this is a
small-sample bet, not a solution. Shannon's actual pick-and-roll ball-handler history: ZERO meaningful
reps as a 2024-25 rookie (his diet was spot-up 39% and transition 30%), then 41 possessions in
2025-26 (18.5% of his offense, 0.951 points per possession), which projects to about **70 over a full
season, well below the 150 feeder bar**. And the efficiency is unstable on the sample: 41 possessions
puts a roughly plus-or-minus 0.32 band on that 0.951 PPP, so it cannot be distinguished from
below-average. So in the delivery-system count he is a **fourth, developmental feeder to watch, not a
counted one**: he does not yet clear the bar, and the Finch-floated co-primary-handler role sits one
full rung ABOVE the cone's bench-creator ladder (which projects him as a dependable bench scorer with
a Sixth-Man ceiling, not a starting-unit on-ball creator). The honest framing for Piece 5: the
committee (Dosunmu plus a Mitchell-type plus a PnR-capable MLE) is the real answer to the feeder
problem, and Shannon-on-the-ball is a labeled internal-upside branch that the coach likes and the
data has not yet earned.

## Data provenance and caveats

- All figures are warehouse pulls (schema `nba`): synergy `PRRollMan`/`PRBallHandler`
  (offensive grouping), tracking `Possessions` and `Passing` measures, `nba_player_hustle_stats_season`
  for screen assists, and play-by-play shot rows (`sub_type`/`description` matched on "dunk")
  for dunk attempts. Synergy, hustle, and PBP all cover his full career; tracking covers it
  except a missing 2020-21 row (touches shown n/a that season).
- **2021-22 touches are excluded as a corrupt ingest.** The tracking Possessions and Passing
  rows for 2021-22 show full games and minutes but roughly half the touches and passes of every
  surrounding full season (2,224 touches vs about 4,100; 1,367 passes vs about 3,000), so they
  are dropped from the touch and passing era means. The 2021-22 synergy, dunk, and delivery
  figures come from independent sources and are intact.
- The delivery-system count uses a 150-possession threshold for "meaningful" and 300 for
  "primary." The qualitative finding (4 to 2, bottoming at 1) is robust to either cut.

## One-line summary for the piece

The same player was the most efficient roll man in basketball in Utah and grades as a negative
offensive player in Minnesota. The audit says both are true: his roll-man volume was cut 37%, his
feeders were halved to one, and his finishing never declined, but he is also a finish-only big who
cannot manufacture offense when the system stops manufacturing it for him. Same hands. Different
passes.
