# Stage 2 methodology notes — running stub
(Accumulates as milestones land; the Part 2 piece drafts from here.)

## Required disclosure (gate ruling condition 2 — one plain sentence, not buried)
"Our trajectory model failed one of its four pre-registered validation gates:
at the seven-year horizon its point forecasts were 0.3% worse than simply
assuming every team drifts back to league average (a statistical tie,
t = 0.7), and we report that red gate rather than revising the threshold."

## Finding promoted from the gate investigation (leads, not appendix)
Forty-six years of data say long-run franchise identity is worth less than
one point per 100 possessions: the fitted spread of franchise long-run means
is tau = 0.78 SRS with the extremes (SAS +0.85, WAS -0.69) under a single
point. "Franchise DNA" is mostly a myth, and that is exactly why no model
beats pooled mean-reversion on seven-year point skill. The red gate and the
finding are the same fact seen from two sides.

## Young-core emergent validation (staged for July-6 step 6; Ruling D)
We asked whether the model was being too generous to Charlotte's future in
exactly the seasons the swaps live (2028-2030) and checked it against forty
years of actual young cores: 77 sub-.500 team-seasons with three or more
under-23 rotation players, 18 in Charlotte's starting band. The model's
simulated crest (a 51-win median peak) sits at roughly the 60th percentile
of what those historical teams actually did, below the pre-committed
correction threshold (the band's 70th percentile peaked at 53). The
stronger finding is emergent: without ever being fit to it, the engine
reproduced the cohort's characteristic arc — crest around year four, then
fade. Caveat carried: the matched band is n=18. The blend schedule was
already doing the discounting the skeptical prior expected (at the crest,
35% of Charlotte's simulated strength is franchise-prior reversion).

## Corrected Duncan-bias record (staged for July-6 step 6)
An early memo claimed smooth same-franchise re-sign mislabeling would
ATTENUATE the contract coefficient; a synthetic test reversed this on the
record (true slope -0.45, clean fit -0.62, corrupted fit -1.62 — a ~2.6x
EXAGGERATION, walk-year hazard inflating .341 -> .667). The labels were
fixed before the one-shot refit; without the fix, Edwards' 2029 walk year
would have overproduced departure worlds through a labeling artifact
wearing the costume of a finding.

## Shock regime (from the accepted v2 mixture)
Roughly 19% of franchise-seasons are structural-shock years with innovation
scale 5.3 SRS (vs 2.9 in routine years) -- the fat tail that drives distant
pick value.

## Other notes queue
- Endogeneity of the success-hazard loop (spec 7.2 language) -- add at M4.
- Play-in + 3-2-1 lottery assumptions A1-A6 (lottery.py) -- add at M4.
- 2029/2030 swap encumbrance semantics + July-6 verification -- add at M5/M6.
- Lag-3 over-persistence direction (add at M4, Bobby's wording): the model
  holds Minnesota's current strength slightly too long, producing fewer
  bad-Wolves worlds in the swap years and a thinner 2033 tail -- biasing the
  asset cost DOWNWARD, against the editorial thesis. If the priced trade
  still comes out expensive under a model slightly too kind to Minnesota's
  future, the finding is robust.
- 8.4 operationalization disclosure (one sentence): chosen after a
  correlated preview, justified a priori (phi^7 ~ 0.07 makes 2033
  effectively stationary); weaker than true pre-registration.
