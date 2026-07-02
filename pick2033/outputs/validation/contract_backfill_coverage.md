# Contract backfill coverage (spec 6.2 / Ruling A)
- source: B-Ref all_salaries, 211 spell players, 0 with no salary table: []
- spell-season coverage: **99.5%** of 1290 rows
- by decade: 1990s 98.7%, 2000s 99.7%, 2010s 100.0%, 2020s 99.6%
- walk-year rate among covered rows: 38.9%
- method: salary-break + franchise-change inference; era envelopes keyed on the segment's SIGNING season (25% pre-1999, 15% to 2011, 9% after; 30% in a career's first four seasons for rookie scale); generous on purpose (false breaks truncate years-remaining, the worse error for the hazard). Known blind spot: smooth same-franchise re-signs read as continuations (Duncan-pattern; overstates remaining for stay-put stars, attenuating the coefficient). QC'd against Edwards/Garnett/LeBron/Duncan ground truth. Data enters the M2 refit blind to fit outcomes.