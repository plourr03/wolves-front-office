# Lever 4: Frontcourt fragility without Reid. Built 2026-06-26.

Estimand: the non-Gobert defensive minutes (Reid AND Gueye gone) and the team's projected defense
across a realistic range of Gobert games-played, tied to his age-34 durability. Uses the SHARED
Gobert estimate (`gobert_defensive_estimate.json`), priced once for Levers 3+4 (no double-count).

## Gobert durability: good base rate, but it is NOT a given at 34

RS games played, last four: 70, 76, 72, 76 (mean 74), at ~30-34 mpg. He has been DURABLE recently,
so the risk is not "he will get hurt." It is that (a) he turns 34 this season, which raises the
downside, and (b) even when healthy he plays ~32 minutes, so the depth behind him is on the floor a
large share of the time. The fragility below is computed as a FUNCTION of his games played, not on
the assumption that he plays a full season.

## The fragility scales with Gobert GP, and is real even at full health

Cliff (team defense lost per 100 when Gobert sits, best available backup-5) under the RAPM fork:
+5.89 with Beringer (raw, unreliable) as the backup, up to +8.02 with a replacement minimum.
Wider than the prior +4.00 because Gueye (who flattered it) is waived. Season-level defensive drag
from the non-Gobert center minutes:

| Gobert GP | mpg | backup-C share | drag (Beringer backup) | drag (min backup) |
|---|---|---|---|---|
| 78 (full health) | 32 | 37% | +2.15 | +2.93 |
| 70 | 32 | 43% | +2.54 | +3.46 |
| 70 | 28 (load-managed) | 50% | +2.96 | +4.03 |
| 60 (age-34 downside) | 30 | 54% | +3.20 | +4.35 |
| 50 | 30 | 62% | +3.65 | +4.96 |

The decisive point (your check): EVEN AT 78 GAMES the drag is ~+2.2 to +2.9 per 100, because Gobert
plays only ~32 minutes and the backup-5 is gutted (no Reid). "The depth is fine as long as Gobert
plays 78" is FALSE: the fragility is structural at full health and merely WIDENS with his GP and
minutes. At a plausible age-34 downside (60 games, or 78 at reduced minutes) it reaches ~+3.2 to
+4.4 per 100, a serious defensive drag.

## Metric fork (priced once, via the shared estimate)

This cliff is RAPM-fork: the box fork would say the backups defend fine (~no cliff). BUT Lever 3
produced BOX-INDEPENDENT corroboration (opponent rim FG% allowed: Gobert ~0.527 vs ~0.673 league)
that Gobert's defensive value is large, the RAPM end. So the cliff is REAL, not a RAPM artifact, and
the box "no fragility" view is undercut by evidence the box itself cannot see. The same shared
Gobert estimate drives Levers 3 and 4; the uncertainty is priced once, not twice.

## The three pre-registered reads

- Positive read (durable Gobert, tolerable non-Gobert minutes): PARTIAL. His recent durability is
  genuinely good and credited, but it does NOT eliminate the fragility, which is ~+2.2 even at full
  health because the depth behind him is gutted.
- Negative read (age-34 risk + cratered non-Gobert minutes): SUPPORTED. The drag is ~+2.2 to +4.4
  per 100, structural and scaling with his GP, and wider than before without Reid and Gueye.
- Can't-tell read: NOT fully triggered. The drag is a callable range; its width comes from two
  uncertain inputs (the backup-5 level, Beringer being unreliable; and Gobert's age-34 GP/minutes),
  not from the data being silent.

## Sample caveats

The backup-5 anchor (Beringer +0.63) is low-sample and unreliable, the same caution as the Gueye
throw-in; the true backup level could be worse (a replacement minimum), widening the drag. Gobert's
2026-27 GP/minutes at age 34 are the other uncertain input; the table spans a realistic range.

## Early signal

The Wolves' defensive rating in non-Gobert minutes in the first 20-25 games (does the gutted
backup-5 crater as projected), and Gobert's games played and minutes (any age-34 load reduction
widens the drag).

## Identifiability verdict

CALLABLE and leaning NEGATIVE: a real, structural defensive fragility (~+2.2 to +4.4 per 100 drag),
present even at full Gobert health and scaling with his age-34 durability, wider than before because
Reid and Gueye are gone, and confirmed real (not box-explained-away) by Lever 3's independent rim
corroboration. Tied to Gobert's GP, not assuming it.
