# Shot-share model: findings (built 2026-06-29)

Comp-based estimate of how much Anthony Edwards's SHARE of open (catch-and-shoot) three-point
looks could shift next to a lead creator like LaMelo. Frequency only; efficiency held fixed.
Criteria locked before the screen ran (`PREREGISTRATION.md`). Take every qualifier, no cherry-pick.

## Headline

The comps do NOT support a meaningful jump in his open-look share. Comparable high-usage scorers
who gained a lead creator kept a sticky shot diet: the clean, on-archetype cases cluster within a
couple of points of zero. Per the pre-registered kill criterion, **a numeric projection is DECLINED**
(the spread straddles zero, is outlier-driven, and the effective clean N is small). The directional
finding is that the open-look share is sticky, and the "more open looks" path is a behavioral choice
(does Ant cede on-ball reps), not a mechanical result of adding a creator. This is exactly the
behavioral floor Lever 1 flagged, now comp-checked.

## Method

Metric: `cs_share = catch_shoot_fg3a / (catch_shoot_fg3a + pull_up_fg3a)`, regular season, from
`nba_player_tracking_season` (2013-14..2025-26; 2020-21 absent). Edwards baseline 2025-26 = 27%
(139 / 502). Screen returns every player-season where a high-usage scorer (PPG >= 20, APG < 6,
cs_share < 0.50, on real volume) gained a NEW lead-creator teammate (APG >= 6) the next season, and
measures his cs_share before vs after, netting out league drift. Full rule in `PREREGISTRATION.md`.

## The comp set (N = 5, as the locked criteria returned)

| subject | pre -> post | creator gained (APG) | team change | pre cs% | post cs% | raw delta | drift-adj |
|---|---|---|---|---|---|---|---|
| De'Aaron Fox | 23-24 -> 24-25 | Chris Paul (6.6) | YES (to SAS) | 40.6 | 50.7 | +10.1 | +15.3 |
| Donovan Mitchell | 21-22 -> 22-23 | Darius Garland (8.6) | yes (to CLE) | 36.5 | 38.4 | +2.0 | -2.6 |
| Donovan Mitchell | 24-25 -> 25-26 | James Harden (8.7) | no | 38.6 | 38.7 | +0.1 | -3.5 |
| Jalen Green | 22-23 -> 23-24 | Fred VanVleet (7.2) | no | 44.4 | 43.0 | -1.5 | -2.9 |
| Giannis Antetokounmpo | 22-23 -> 23-24 | Damian Lillard (7.3) | no | 41.8 | 33.6 | -8.2 | -9.7 |

All five: raw delta median +0.1pp (mean +0.5pp); drift-adjusted median -2.9pp. The distribution
straddles zero from -8pp to +10pp (raw), driven by the two flagged cases pulling opposite ways.

## Quality flags (transparent, not dropped)

- **Fox + Chris Paul (the big positive, +10pp):** a MID-SEASON trade (Fox to SAS, Feb 2025), and the
  tracking season aggregates a traded player under a single team label, so his "post" cs_share mixes
  his SAC and SAS portions. The least reliable point, and it is the largest positive. Flagged
  confounded by the pre-reg's team-change rule.
- **Giannis + Lillard (the big negative, -8pp):** an ARCHETYPE MISMATCH. Giannis is a reluctant,
  low-volume three-point shooter (~120-165 3PA/yr), not an Edwards-type perimeter scorer; his
  cs_share is noisy and not a relevant analog. He passed the numeric filters but is not the
  comparison we want.
- The three CLEAN, on-archetype comps (Mitchell x2, Green) cluster tightly: -1.5pp, +0.1pp, +2.0pp
  raw. Median ~0. The signal there is "barely moves," and it is the more relevant read. Dropping the
  two flagged outliers does not change the conclusion, it sharpens it toward zero.

## The big limitation (stated up front)

The two textbook "high-usage scorer cedes to a pass-first lead PG and gets more open looks" cases,
Booker + Chris Paul (2020-21) and LaVine + Lonzo Ball (2021-22), are exactly the ones removed by the
missing 2020-21 tracking season. Those carry the strongest prior for a large shift, and they are
unmeasurable here. So the measurable set may UNDERSTATE the upside: the comps that survived involve
creators who co-existed as co-creators (Garland, Harden alongside Mitchell) or connectors (VanVleet),
not a pure lead guard taking the wheel. This is a real gap, not a modeling choice, and it is why the
honest read is "modest at most, possibly flat" rather than "zero."

## Lens B (ceiling, qualitative only)

The intended ceiling reference (perimeter movement shooters next to a creator) did not isolate
cleanly; the highest cs_share players are spot-up BIGS (Vucevic, Horford, Draymond at ~99%, players
who simply never shoot off the dribble), which is not an Edwards analog. The usable takeaway is only
directional: Edwards remains a high-usage on-ball scorer, so his open-look share would stay well
below a pure spot-up player's. It bounds the top; it does not set the projection.

## Reconciliation with the main project

Consistent with, and underneath, the existing fit-clicks scenario (+3.5 to +7.7pp reach-CF,
`sim/01_scenario_findings.md`). It introduces no new title or reach-CF claim. It quantifies the
FREQUENCY floor: the share does not rise on its own, so the fit-clicks unlock requires the behavioral
change (Ant ceding on-ball reps) that Lever 1 named and `DELIVERABLE.md` holds open as a future fact.
The forward signal that will grade it is already logged: Edwards's off-ball possession share in the
first 20 games.

## One-line summary

Across comparable high-usage scorers who gained a lead creator, the open-look share barely moved, so
we cannot project a confident jump for Edwards: more open looks would be a choice he makes, not an
automatic gift from LaMelo (and the two best-prior comps are unmeasurable behind the 2020-21 data gap).

## Implication for slide 2

The data does NOT support a "27% jumps to X%" movement visual. An honest visual would show the share
as sticky with a wide, zero-straddling band, or keep slide 2 qualitative ("more green, less gray")
without inventing a number. Recommend NOT building a big-shift movement graphic; hold for a call.
