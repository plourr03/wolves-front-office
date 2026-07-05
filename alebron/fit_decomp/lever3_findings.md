# Lever 3: Defensive exposure (LaMelo's core risk). Built 2026-06-26.

Estimand: (a) LaMelo's cost as a PnR/iso target (PPP allowed, percentile), (b) how much
Gobert's rim protection mitigates the blow-by vs an average backline. NET = perimeter cost
minus rim save. Data: synergy DEFENSIVE play-types (league-wide), tracking rim defense.
Uses the SHARED Gobert estimate (`gobert_defensive_estimate.json`), priced once for levers 3+4.

## Measured: the perimeter exposure is real (RS, GOOD identifiability)

LaMelo's PnR ball-handler defense (the hunt metric), by season: PPP allowed / percentile / share
of his defensive possessions spent as the PnR target:

| season | PnR-def PPP allowed | percentile | hunt share (poss_pct) |
|---|---|---|---|
| 2020-21 | 0.850 | 63rd | 19% |
| 2021-22 | 0.935 | 31st | 22% |
| 2022-23 | 1.153 | 6th | 25% |
| 2023-24 | 0.932 | 43rd | 35% |
| 2024-25 | 1.066 | 6th | 40% |
| 2025-26 | 0.908 | 38th | 36% |

Read: a BELOW-AVERAGE-to-BAD PnR defender (career roughly 30th-40th percentile, twice
bottom-decile), and increasingly HUNTED, the share of his defensive possessions spent as the
PnR target has roughly doubled (19% -> 36-40%). His ISOLATION defense is actually fine (86th,
89th percentile in 2024-25/25-26, but small 30-41 poss samples), so the exposure is specifically
NAVIGATING SCREENS, not static one-on-one. The perimeter risk is measured and real: bottom-third
PnR defender, primary target.

## Measured: the Gobert mitigation is strong (the shared estimate)

Gobert allows ~0.527 at the rim recently (2023-26 RS) vs a ~0.673 league baseline (high-volume
rim defenders) = a ~14-15 point FG% suppression, on elite volume (~450-560 rim FGA/season). So
when LaMelo is beaten off the dribble and the drive reaches the rim, Gobert's contest cuts the
conversion by ~14-15 points relative to an average backline. He is the strongest possible
backstop. (The rim-FG% tracking stat also independently corroborates that Gobert's defensive
value is large, closer to the RAPM end of the metric fork than the box prior; see the shared
estimate.)

## The NET: regular season mitigated; PLAYOFFS = CAN'T TELL (the pre-registered outcome)

- Regular season, vs most lineups (non-shooting bigs, Gobert in drop): the backstop largely
  offsets LaMelo's PnR exposure. The beaten drives meet an elite rim deterrent, so the net cost of
  hunting him is materially reduced relative to an average backline. Directionally MITIGATED.
- Playoffs (the decision-relevant context): the negative read is that offenses pull Gobert out of
  the paint with a shooting big (spread PnR), then attack LaMelo with the rim open, neutralizing
  the backstop. This is exactly the dynamic, and it is NOT CLEANLY QUANTIFIABLE from the data:
  - LaMelo's playoff defensive sample is essentially NIL (a handful of possessions across his
    career: e.g. 2020-21 PO PnR-def = 1 possession). There is no playoff PnR-defense rate to
    measure.
  - The "Gobert dragged out" rate depends on the specific opponent's personnel and the Wolves'
    coverage choices, which cannot be read off pre-trade data.
  Per the pre-registered CAN'T-TELL read for this lever, the playoff NET is reported as a FLAGGED
  UNKNOWN, not forced to a sign. The RS components above are measured; the playoff intensification
  that decides the actual risk is not callable today. (A faint, non-callable hint: Gobert's
  2025-26 playoff rim FG% allowed was 0.639, his worst, but small-sample.)

## Sample-size caveats

- LaMelo's iso-defense percentiles rest on 30-41 possessions/season (wide).
- His PLAYOFF defensive sample is ~nil (the binding limit on the net).
- Gobert's playoff rim numbers are 5-15 games each (noisy).

## Early signal (how reality grades this)

Opponent PPP when attacking LaMelo in PnR in the first 20 games (vs his ~0.9-1.1 RS baseline and
his rising hunt share), AND the Wolves' rim FG% allowed in LaMelo-on / Gobert-on lineups (does the
backstop hold, or do opponents pull Gobert out). The first time a playoff-caliber offense runs
spread PnR at him with a shooting 5 is the real test.

## Identifiability verdict

- RS perimeter exposure: GOOD (measured, real: bottom-third PnR defender, increasingly hunted).
- Gobert rim mitigation: GOOD (measured, strong: ~14-15pp rim suppression).
- The decision-relevant PLAYOFF NET: CAN'T TELL (LaMelo's playoff defensive sample is nil and the
  Gobert-pulled-out dynamic is opponent-specific). This is the honest, pre-registered outcome, and
  it is the most likely lever to land here, as anticipated.
