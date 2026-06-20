# Phase 2 carry-forwards (locked, from the 1b rim-correction finding)

1b surfaced that box does NOT bury Joan. His box prior is +3.61, ABOVE his own
unreliable RAPM (+2.82 on 1,156 possessions, net_sd 2.43). His profile (small,
favorable-minutes sample with inflated per-36) matches the young-big class box
OVER-rates (GG Jackson: RAPM -2.03, box -0.04; Trayce Jackson-Davis: RAPM +0.54,
box +1.90), not the established-deterrent class box under-rates (Gobert, Wembanyama,
Holmgren, who carry 25-30K possessions of elite play). The bias direction inverts
for Joan. Three things ride into Phase 2 because of this.

## 1. Gate the rim correction on reliability (a GATE, not a guideline)

The rim correction was validated leave-one-out on the RELIABLE population, where it
correctly prices Gobert (for a trade) and veteran defenders (for the lineup).
Applying it to an unreliable small sample is out-of-domain extrapolation into the
regime where the box-vs-RAPM relationship reverses, and it would quietly compound an
already-optimistic prior (it would have added +0.47 to Joan, pushing +3.61 to +4.08).
So: the correction applies to reliable-sample players only; for unreliable players it
is switched OFF, full stop. ALREADY ENFORCED in `core_max/impact/rim_correction.py`
(the `correction_suppressed` gate). Phase 2 must keep this gate; Joan's value comes
from the development module, not the correction.

## 2. Asymmetric posture on Joan's prior (skepticism in both directions)

The finding licenses removing the assumption that box buries Joan. It does NOT license
flipping to a confident "box over-rates Joan by X" — his RAPM is 1,156 possessions at
net_sd 2.43, too noisy for a precise over-rating claim. The honest stance is
asymmetric: no evidence of under-rating, a comp class that warns of over-rating, so let
small-sample shrinkage toward the pool and an honest bust tail carry the uncertainty
rather than substituting one confident point claim for another.

## 3. Build the comp pool (and its bust tail) from the right reference class

Joan's reference class is "young bigs with small-sample high box readings." The realized
outcomes of that class include heavy regression and real busts. So the left (bust) tail
is not a hyperparameter to tune; it is populated by actual players who looked like Joan,
flashed in limited minutes, and did not pan out. Build the pre-registered comp pool from
that class and let shrinkage do its job. This is the constructive half of the finding:
it hands us the honest left tail.

## What it means for the bet

It does not shrink the bet, it cleans it. The Joan bet was never "box is hiding a stud
the model will reveal." It was always "we believe he develops." The finding strips out a
false comfort we did not need and leaves the real development wager standing on its real
foundation, priced honestly with a visible bust tail. The model refused to manufacture
the cornerstone's upside, which is exactly what the spirit clause asked it to do.
