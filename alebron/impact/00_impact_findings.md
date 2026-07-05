# Impact layer findings (clean-room), 2026-06-25

Method reused from `build_rapm.py` (not its fitted output), box features recomputed
from the frozen snapshot `wh_65cf5da7f50c7f62`, possession cache 2023-24..2025-26.
HALT-for-review point: the raw anchor below is what the 0.75 survival prior multiplies.

## Validation (the fit is sound)

- 765,618 possessions, 612 qualifying players (>= 1000 poss).
- Top of board: Wembanyama +8.87, SGA +6.82, Jokic +6.63, Giannis +6.54, Gobert +5.76.
  Sensible star ordering. corr(net_rapm, box_net_bpm) = 0.740.
- A few small-sample bigs (Edey, Diabate, Queta) sit high, the known low-possession-big
  RAPM artifact; they are flagged reliable only above 3000 poss and do not affect MIN.

## LaMelo raw RAPM (PRE-TRANSPORT anchor)

- **net = +1.95 (off +4.18, def -2.23 contribution), SD +/-1.67, 17,304 poss, reliable.**
- box_net_bpm = +1.89. The RAPM and the box prior AGREE on LaMelo (~+1.9 either way),
  so his raw anchor is ROBUST to the spine-metric choice (the metric tie below does not
  destabilize his number).
- Read: strongly positive offense, clearly negative defense, modest-positive net. A
  good-not-elite starter-plus on bad Charlotte teams. Consistent with public consensus.
- The 0.75 survival prior applied to +1.95 gives a transported CENTER near +1.46 net
  BEFORE the role/usage/leverage/playoff-defense transport adjustments (those are the
  next layer). Eyes on the raw before that haircut, as requested.

## YoY metric-selection calibration (the honest result)

Train 2023-24 + 2024-25, test held-out 2025-26 single-season RAPM, n=329 players
reliable in train and present in test. ONE transition only (cache is 3 seasons), so
this is LOW POWER and reported as such.

| candidate | OOS corr vs next-season RAPM | OOS RMSE | std-resid SD |
|---|---|---|---|
| net_rapm (box-prior RAPM) | +0.495 | 1.930 | 0.69 |
| box_net_bpm (box-only BPM) | +0.495 | 1.649 | 0.59 |

Honest reading, not the flattering one:
- The two metrics are **TIED** on out-of-sample correlation (+0.495 each), and box-only
  BPM is actually BETTER on RMSE (1.649 vs 1.930). The calibration does NOT decisively
  pick a spine. The RAPM possession signal adds little OOS predictive power for
  next-season RAPM beyond the box prior at this sample.
- Implication for the tower: the impact-metric choice is a GENUINE multiverse fork, not
  a calibration-settled winner. Carry box-prior RAPM and box-only BPM as parallel forks
  and report headline outputs across both. If a single spine is needed for the central
  path, box-prior RAPM is defensible (richer model, ties on corr, and for LaMelo
  specifically the two agree at ~+1.9), but the choice is flagged as not
  calibration-decisive and swept.
- std-resid SD below 1.0 on both means the posterior SD bands are CONSERVATIVE
  (over-wide), the safe direction, consistent with the prior coverage test that adopted
  no inflation. We are not over-stating precision.

Caveat carried upward: the YoY test's single transition and noisy single-season-RAPM
target are real power limits. The metric-fork decision rests on a weak discriminator, so
it is treated as a fork rather than a settled choice.
