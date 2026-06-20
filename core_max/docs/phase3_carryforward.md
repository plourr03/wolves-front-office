# Phase 3 carry-forward (veteran availability and collapse left-tail)

This is a Phase 3 input-modeling item, logged now while fresh. It does NOT reopen the
1c as-is call (that is an SD-level a/b question); this is a separate left-tail-SHAPE
question.

## The blind spot

The 1c held-out coverage test is survivor-only: it scores players present in BOTH the
training window and the held-out season. A veteran who craters, gets hurt, ages off a
cliff, or loses his role is INVISIBLE to it (no held-out estimate). That is exactly the
left tail that matters on a two-year horizon for an aging roster. So "established SDs are
near-nominal" means calibrated for the survivors, not veteran downside fully captured.

1a models impact as Normal(point + age drift, sd). The age drift captures the EXPECTED
decline (39-year-old Conley correctly sliding toward zero), but a Normal SD does not
capture a sharp collapse or a lost season, and the survivor test structurally cannot tell
us whether it should. For this roster specifically (a 34-year-old Gobert and a
39-year-old Conley carried across two years), that under-modeled downside is real.

## The fix (Phase 3)

The established-player distributions likely need an explicit AVAILABILITY + COLLAPSE
left-tail component: a sharp-decline-or-missed-season HAZARD, distinct from the analytic
SD, because the survivor coverage test cannot provide it. Model it as a mixture (a small
probability of a collapse / lost-season state) layered on the Normal, not as a wider
symmetric SD.

## The honesty rule (this correction helps the thesis, so it gets the MOST scrutiny)

Under-modeling veteran collapse FLATTERS the veteran-heavy rosters (status quo most, since
it is the most aging-dependent). Adding the tail PENALIZES the alternatives and HELPS Fork
B. So: calibrate the collapse hazard from REAL age and injury base rates (historical
sharp-decline and games-missed rates by age and role), NEVER hand-set it, and carry it as
a Phase 3-4 sensitivity variant so we can SEE whether it moves the verdict rather than
assuming it does. Same rule as every other knob: the correction that happens to help the
thesis gets the most scrutiny, not the least.
