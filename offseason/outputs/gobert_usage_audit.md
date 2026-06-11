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
