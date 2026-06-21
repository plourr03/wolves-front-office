# Phase 3 carry-forwards (the title engine)

Logged before Phase 3 codes. Item 1 is the single most important Phase 3 design decision and
is NOT a deferred sweep; it determines whether the engine can even see the thesis.

## 1. TEAM-LEVEL FIT: the engine must NOT be a sum of individual impacts

A title engine that sums per-player RAPMs would treat Gobert's ~+4.5 as pure gain, miss that
his non-shooting fit was CAPPING the team's offense, miss that the two fit returns and Joan's
spacing-friendlier profile lift the WHOLE offense, and so quietly favor keeping Gobert. That
makes "fit over splash" invisible and undervalues Fork B BY CONSTRUCTION, because the entire
Fork B argument is that the team is worth more than its parts once the offense is un-clogged.

Team strength must therefore carry an offensive-architecture / fit term, not just summed
impacts. The LAFI work is the natural input: un-clogging the offense (removing the
non-shooting big, adding shooting/creation, handing Joan a spacing-friendlier role) must show
up as a real TEAM-LEVEL gain, not an individual-impact wash. Design the team-strength function
so fit is first-class (a baseline from impacts PLUS a LAFI-driven offensive adjustment that
rewards un-clogging and penalizes redundancy/clog), validated against the LAFI cohort's
realized offense. Do not defer this.

## 2. Honest tails on BOTH sides (symmetric, not selectively pessimistic)

Phase 2 gave Joan an honest bust tail (64% washout in the faithful view). Fairness requires
the same honesty on the veteran side: a 34-year-old Gobert and a 39-year-old Conley do NOT
have certain floors. Joan's downside cuts against Fork B; the veterans' real downside cuts
toward it; honest tails on both sides keep the comparison fair (any "certain floor" phrasing
is corrected: high but uncertain).

Veteran availability + collapse left-tail (the queued item): the 1c survivor-only test cannot
see dropouts (veterans who crater, get hurt, age off a cliff, lose a role); 1a's
Normal(point + age drift, sd) captures expected decline but not a sharp collapse or lost
season. Add an explicit availability + collapse left-tail (a sharp-decline-or-missed-season
hazard, modeled as a mixture, not a wider symmetric SD), calibrated from REAL age and injury
base rates (never hand-set), carried as a Phase 3-4 sensitivity. This correction HELPS Fork B
(under-modeling veteran collapse flatters the veteran-heavy rosters, status quo most), so it
gets the MOST scrutiny: base-rate-calibrated and swept, never hand-set.

## 3. The replacement sweep is VERDICT-DETERMINING, not routine

Joan's sub-class Yr1 median swings -0.72 (generous -0.97) to -2.50 (harsh -2.83) across the
replacement bracket, so it can flip the verdict. The report must show explicitly whether Fork
B holds across the WHOLE bracket or only at the generous end. Same for the full-vs-sub-class
split and the established-SD variants: sweep, do not pick, and show the verdict's range.

## 4. Local convexity is MEASURED, not assumed (the original pushback)

P(title) being convex in team strength (so variance is an asset) holds at the very top of the
strength curve. Whether it holds at the Wolves' operating point is empirical. Measure the
local convexity at their strength level; if it is locally linear or concave there, the
"variance is an asset" argument (and thus part of the Fork B case) weakens, and that must be
surfaced.

## 5. Per-iteration sampling (the locked rule)

Sample every player's impact from its distribution each Monte Carlo iteration (established
players from Phase 1a; Joan from the Phase 2 comp distribution), never collapsing to the mean.
The real-options Gobert term carries Joan's out-year upside that the 2-year window truncates.
