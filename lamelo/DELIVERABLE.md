# LaMelo Ball trade: the locked evaluation (2026-06-25)

Status: LOCKED (revised after an independent red-team audit, 2026-06-26). The qualitative
finding is published. A precise title percentage is DELIBERATELY NOT published, primarily
because the title delta is NOT IDENTIFIABLE: the band across the metric fork, the role-player
valuation fork, and the parametric inputs crosses zero (spec section 20 kill criterion). The
star-trade retrodiction (Case 3) is secondary corroboration, not the load-bearing reason.
Decomposition first, the gated number declined, per the discipline.

## The one-line finding

On the most complete way of measuring (defense-aware RAPM), adding LaMelo Ball changed how
good the Timberwolves are by an amount that ranges from indistinguishable-from-zero to
slightly NEGATIVE once the near-minimum throw-in is valued reliably. On the simpler
(defense-blind) read, a small improvement. The data cannot say this trade made them better,
and the most complete read leans slightly negative; Minnesota spent a mountain of future and
a second-apron hard cap to get there.

## 1. Value decomposition (where the impact moved)

- LaMelo, raw clean-room net RAPM +1.95 (offense +4.18, defense -2.23), reliable. RAPM and
  the in-house box model AGREE on his net at ~+1.9, so the anchor is robust. Transported to
  MIN's role (0.75 offensive survival, measured defense carried, no double-count): +0.90 net
  under RAPM, +1.41 under box. The whole gap is his defense, which RAPM prices and box hides.
- Reid OUT costs +3.27 net under RAPM but only +0.87 under box (again, his defense). Randle
  OUT is near replacement either way (+0.44 / -0.02): the on-court loss was minimal; the cost
  was the picks and the cap, not his production.
- The trade is a four-team deal: MIN moves Randle AND Reid plus a 2033 unprotected first,
  three first swaps (2028/29/30), three seconds, and the No. 28, for LaMelo + Green + Gueye,
  and re-signs Ayo (5/$112M). It hard-caps MIN at the SECOND apron (~$211M), forfeiting the
  $33.3M exception and the full mid-level. The frontcourt hole behind Gobert cannot be
  cap-fixed this offseason. See `data/cap_state.json`, `impact/00_*`, `impact/02_*`.

## 2. Team strength: a modest negative to a small positive

The trade delta depends on two researcher degrees of freedom (swept as forks): the defensive
metric, and the valuation of Mouhamed Gueye, a near-minimum throw-in whose value is almost
entirely low-sample defensive RAPM the box cannot see (the profile flagged unreliable for
Edey/Diabate). The published +0.003 is the single most Gueye-favorable point.

| Gueye valued at | RAPM trade delta | box trade delta |
|---|---|---|
| modeled (shrunk +1.498) | +0.003 | +0.776 |
| neutral (0.0) | -0.559 | +0.570 |
| replacement (-1.5) | -1.121 | +0.007 |

So the defense-aware result is a WASH TO A MODEST NEGATIVE (roughly -0.4 to -0.6 in net at a
neutral Gueye, about -1.1 at replacement); the defense-blind result is a small positive that
shrinks to ~0 at replacement. K-stable across the regression sweep. The same contested Gueye
value also props up the Gobert-fragility backup-5 term (defensive cliff +4.00 with him, +5.89
without), so one unreliable number flatters two results.
(`impact/03_team_strength_findings.md`, `impact/sweep_gueye.py`, `impact/sweep_regression_K.py`.)

## 3. Sim: the title and deep-round picture (Q2 state estimate)

| quantity | RAPM | box |
|---|---|---|
| post-trade P(title) | 2.66% | 3.92% |
| post-trade P(reach CF) | 15.1% | 19.3% |
| post-trade P(reach Finals) | 6.4% | 8.6% |
| CRN-paired title delta | +0.005pp | +1.113pp |

The deep-round odds tell the same story as the title odds: small-positive under box,
flat-to-slightly-negative under RAPM once the Gueye fork is included.

BAND LABELING (audit Fix 4): the interval [+0.005, +1.113]pp is ONLY the inter-fork POINT
SPREAD between the two metric forks at the modeled-Gueye point. It does NOT include
parametric input uncertainty (player-impact posterior SDs, the transport band, the
role-player valuation fork). With those included, and because the Gueye fork alone drives
the RAPM net delta to -0.56 (neutral) and -1.12 (replacement), the true title-delta band
extends well BELOW zero. Do not read [+0.005, +1.113] as the full uncertainty band.

WIN/SEED RECONCILIATION (audit Fix 3): the engine's own net-to-wins mapping projects roughly
46-49 wins post-trade (RAPM end ~46, box end ~48) and a correspondingly lower seed (play-in
to low-playoff range), consistent with the wash. The pre-registered forward predictions of 54
wins and a 4-seed (section 8) EXCEED the model's output; they are above-model analyst priors,
logged cold for grading, NOT the analysis's projection. They are left exactly as committed but
must not be presented next to the wash as if the analysis projects them. (`sim/00_sim_findings.md`.)

## 4. The scenario shape (fit-clicks / neutral / fit-fails): the bet, quantified

Reach-CF delta vs run-it-back:

| scenario | RAPM | box |
|---|---|---|
| fit_fails | -3.35pp | +0.28pp |
| neutral | +0.02pp | +3.81pp |
| fit_clicks | +3.54pp | +7.72pp |

The "LaMelo unlocks Edwards and Gobert" thesis is real as the upside tail: if it clicks, a
+3.5 to +7.7pp deep-round bump. Its symmetric hedge is also real: under the defense-aware
read, if the fit fails (collision, LaMelo hunted), the team gets WORSE. Connelly is buying
the right tail of a distribution whose middle is a wash and whose other tail is a real
negative. (`sim/01_scenario_findings.md`.)

## 5. Why there is no title percentage in this evaluation

PRIMARY reason (over-determined): the title delta is NOT IDENTIFIABLE. Its band across the
metric fork, the role-player valuation fork (section 2), and the parametric inputs (section
3) crosses zero, and leans negative on the most complete read. A point estimate inside a band
that straddles zero is exactly the pre-registered identifiability kill criterion (spec section
20). That alone is sufficient to decline the number.

SECONDARY corroboration (properly caveated): the gate results.
- Calibration re-validation (re-fit excluding the sealed seasons): PASS, reproduces the old
  params within 0.2 SE. Series-mechanics retrodiction on 60 unseen sealed series: PASS, 0/5
  buckets outside interval. The net-rating-to-outcome machinery works on unseen data.
- Star-acquisition retrodiction (Case 3): the engine mis-signed 3 of 8 cases, but the audit
  established that the MAJORITY of the failure is estimand mismatch (the test omits
  outgoing-player subtraction, availability, and uses an era-transported box map), not a proof
  of additive fit-blindness. For example, the Gobert-MIN miss is plausibly fixed just by
  subtracting the outgoing package (Kessler, Vanderbilt, Beasley, Beverley), with no fit
  modeling. So Case 3 is CONSISTENT WITH fit and availability mattering, but does not by itself
  carry the no-number decision; identifiability does. (`sim/03_case3_findings.md`.)

Cautionary precedent, in its defensible form only: Gobert to Minnesota, 2022, MIN's own last
big star acquisition, was a fit-and-personnel disappointment in year one. That is a real,
relevant warning for a team making another fit-dependent star bet. It is NOT offered as proof
the engine validated.

## 6. What we cannot resolve

- WHICH of the two defensive metrics is right. The out-of-sample calibration tied, so the
  difference between "nothing" and "a modest bump" cannot be settled with current data.
- WHETHER the fit clicks. That is a future fact, not a measurable one today.
- A PRECISE title percentage. The title delta is not identifiable: its band (the metric fork,
  the role-player valuation fork, and the parametric inputs) crosses zero. This is not fixable
  by more compute; the binding limits are a metric the calibration could not choose and a fit
  the model cannot observe in advance.

## 7. Public-translation rule (the caption inherits the error bars)

The public claim may not be stronger than the gated result. The honest public frame: "We
built a championship model and it could not tell us this trade helped. The effect depends on
which defensive metric you trust (the data can't pick one) and on a near-minimum throw-in's
contested value, and once you account for both, the most complete read leans slightly
NEGATIVE. The honest band crosses zero, so we will not hand you a false-precision title
number. The bet is a swing for a fit-dependent ceiling bought with years of future, and
Minnesota's own Gobert deal is the cautionary precedent." Do not lean on the star-trade
backtest as proof of anything structural: that test was crude (it omits what teams gave up
and players' availability), and the crudeness, not a clean fit-blindness finding, drives most
of its misses. The number is declined on identifiability, not on the backtest.

## 8. Forward predictions (the immutable log; reality grades these)

| # | prediction | point | band | grade date |
|---|---|---|---|---|
| 1 | Wolves 2026-27 win total | 54 | [46, 58] | 2027-04-15 |
| 2 | final seed (West) | 4 | [3, 5] | 2027-04-15 |
| 3 | LaMelo games played | 63 | [44, 73] | 2027-04-15 |
| 4 | Ant-LaMelo on-court net | +3.0 | [-2, +8] | 2027-04-15 |

Prediction 4 is the one that settles the fork the calibration could not: near +8 is the
fit-clicks world, near -2 is fit-fails. Reality closes the loop the model left open.

NOTE (audit Fix 3): predictions 1 and 2 (54 wins, 4-seed) EXCEED the model's own output (the
net-to-wins mapping projects ~46-49 wins and a lower seed; see section 3). They are
deliberately left exactly as committed, as cold analyst priors logged for grading, but they
are ABOVE-MODEL and are not what this analysis projects.

## Decisions locked

- Publish the qualitative finding and the scenario shape. Do NOT print a title percentage,
  declined on IDENTIFIABILITY grounds (the band crosses zero), not on the backtest.
- Do NOT build a fuller Case 3 reconstruction. Not because it would not help (it plausibly
  would, e.g. fixing the Gobert-MIN sign by subtracting the outgoing package), but because the
  number is already declined on identifiability, so chasing a backtest that might "rescue" a
  number would be motivated reasoning, not added rigor.
- The qualitative finding (a modest negative to a small positive, not identifiable to a point,
  bought with a mountain of future) is the deliverable.
