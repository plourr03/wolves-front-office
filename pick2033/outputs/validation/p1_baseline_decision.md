# P1 provisional baseline: two committed runs disagree — ruling needed before the public grade

2026-07-05 (release eve). Found during the July-5 pre-flight. P1 is graded
publicly tomorrow at Step 4; the baseline it grades against is currently
ambiguous. No prediction has been edited. This memo is for Bobby's ruling;
the fix is one line either way.

## What P1 predicts (unchanged, not in question)
Direction only: the final 2033 posterior comes out LIGHTER-TAILED than the
provisional, because the missing contract covariate inflates departure worlds.
The DIRECTION call is unaffected by anything below. Only the numeric baseline
the shift is measured against is in question.

## The conflict
Two committed "provisional" 2033 posteriors exist from 2026-07-02, both
pre-M2, both variant two_tier, both n=50000:

| Run (UTC)        | code_commit | p_top4  | p_top10 | rounded    |
|------------------|-------------|---------|---------|------------|
| 2026-07-02 04:02 | 8931e70c    | 0.16696 | 0.4217  | .167 / .422 |
| 2026-07-02 18:16 | dbb3657b    | 0.17002 | 0.42092 | .170 / .421 |

- `docs/predictions.md` P1 pins the baseline at **.167/.422** (the 04:02 run;
  P1 was logged the morning of 07-02, commit 9f3cb710).
- The artifact on disk `outputs/json/slot_distribution_2033_PROVISIONAL.json`
  and `JULY6_RUNBOOK.md` Step 4 both use **.170/.421** (the 18:16 run).

## Why they differ (not reseed noise)
Both runs use the declared seed, so identical code + data would give identical
output. They differ because the provisional pipeline changed between them: the
`pick_ledger` E2 slot-resolution machinery landed in `a5bb0a5d`, between 04:02
and 18:16. So the 18:16 number reflects the ledger-resolved conveyance and the
04:02 number does not. Magnitude of the shift: +0.003 p_top4 (~1.8 SE at
n=50000), -0.001 p_top10 (within noise). Small, but real and directional.

## Options
- **A. Grade as-logged (.167/.422).** Honor the timestamp: P1 wrote .167/.422,
  grade against .167/.422. Append a dated pin-note to predictions.md naming the
  04:02 artifact + commit 8931e70c (an ADDENDUM, never an edit of the logged
  prediction). Fix runbook Step 4 to .167/.422. Cleanest defense of the
  pre-committed discipline: you grade against exactly what you wrote, and the
  "newer provisional is better" argument is precisely the post-hoc baseline
  adjustment the discipline exists to forbid.
- **B. Re-pin to .170/.421.** Treat the 18:16 run (post-ledger, last pre-M2
  provisional) as canonical because it is the more correct provisional. Append
  a dated addendum to P1 explaining the re-pin and its reason. Runbook already
  matches. Cost: re-pins a committed prediction, weakens the "we could not move
  the goalposts" line the timestamp is supposed to buy.
- **C. Grade against both.** Quote .167/.422 and .170/.421 as the provisional
  range (both legitimate pre-M2 runs, within noise), grade final vs the range.
  Most transparent; adds one hedging sentence to the public piece.

## Recommendation
**A.** The direction is what P1 actually bet, and it is untouched. Grading
against the literally-logged number is the most defensible version of the
discipline, and the addendum keeps the provenance honest without rewriting
history. B's "more correct provisional" reasoning is real but is the exact
move the pre-commit is designed to prevent; if the shift mattered
scientifically it would be larger than 1.8 SE.

## RULING (Bobby)
> **A** (2026-07-13, verbatim: "A"). Grade as-logged (.167/.422).

Mirrored into docs/decisions.md. Option A paperwork executed same day:
dated pin-note appended to predictions.md naming the 04:02 artifact and
commit 8931e70c; runbook Step 4 corrected to .167/.422.

Sequencing disclosure, on the record: the P1 grade was written into
predictions.md on 2026-07-12 against the as-logged baseline while this
ruling was still pending. The ruling now ratifies that choice; it did not
precede it. The grade's direction call (CONFIRMED, lighter-tailed) holds
against either candidate baseline, so no graded output changes under A.
