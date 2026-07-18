# October 20, 2026 Freeze Manifest (ONE FOR ALL)

The single dry-run checklist of everything that freezes on **2026-10-20**. One row per artifact, with owner and status; blanks are left visible on purpose, because an open blank is the point of a countdown. Assembled 2026-07-17. Nothing here is itself frozen; this is the list of what will be.

Freeze mechanics: on 2026-10-20 each CLOSED item is locked, the frozen set is bundled, and (if the hash decision below lands YES) the SHA-256 of the bundle is published so the February 2027 piece can prove nothing was chosen after the fact. The commit history from July 2026 forward is the corroborating trail.

## Freeze checklist

| # | Item | Artifact | Owner | Status | What closes it |
|---|---|---|---|---|---|
| 1 | Tripwires | `tripwire-backtest/TRIPWIRES.md` | Claude, ratify Bobby | **DRAFT READY** | one binding wire (AVAIL-PACE -> ARM-G) + FC-DRB structured advisory + ARM-S dashboard; final read of the wording |
| 2 | Jaden markers | `board/jaden_calibration/jaden_markers_v02.md` | Claude, ratify Bobby | **PROPOSED, calibration banked** | thresholds are PROPOSED/TUNE; calibration class (n=19) banked and ratified; lock the numbers |
| 3 | Fork adjudication | `board/docs/fork_adjudication.md` | Bobby (prior), Claude (form) | **CLOSED (2026-07-17)** | functional form + evidence + fire dates fixed; prior **0.5/0.5 confirmed** by Bobby (see ruling below) |
| 4 | League-event rule | `board/docs/league_event_resolve_rule.md` | Bobby (thresholds) | **THRESHOLDS TUNE** | four trigger classes fixed; top-15/55-win/top-10 cutoffs are TUNE; lock the thresholds |
| 5 | P(east) | `board/build/board_step6.py` (realignment) | Bobby (prior) | **CLOSED (2026-07-17)** | **P(east) = 0.60 ruled** (see ruling below); blend + /-0.15 band (0.45-0.75) emitted |
| 6 | SALVAGE_CAP | `board/docs/board_spec.md` s4 | Bobby | **CLOSED (logged)** | ruled 0.012, "win it with Ant", logged verbatim under the anti-tuning clause. Done |
| 7 | Roster snapshot | `board/build/roster_recon/roster_reconciliation.md` | Claude | **POST-LEBRON PENDING** | log-derived 15-man is clean; must be refreshed after the LeBron resolution and any Aug-Oct moves before it freezes as THE snapshot |
| 8 | R1/R2 schedule mapping | fork adjudication + tripwire read dates | Claude | **AWAITING NBA SCHEDULE** | R1 (~game 18) and R2 (~game 37) map to calendar dates only once the 2026-27 NBA schedule is released (usually mid-Aug); fill the dates then |
| 9 | Hash publication | this manifest | Bobby (decision) | **CLOSED (2026-07-17)** | **YES** -- publish the SHA-256 of the frozen bundle in October (see ruling below); change control governs post-freeze amendments |

## Status roll-up (as of 2026-07-17)

- **Closed**: 4 of 9 (SALVAGE_CAP, fork adjudication prior, P(east), hash publication).
- **Draft/proposed, awaiting a final lock**: 3 (tripwires, jaden markers, league-event thresholds).
- **Awaiting Bobby**: **0** (all three rulings landed 2026-07-17).
- **Awaiting external / downstream**: 2 (NBA schedule release for R1/R2 dates; the LeBron resolution + late-summer moves for the final roster snapshot).

## Rulings logged (Bobby, 2026-07-17), with elicitation disclosures

**P(east) = 0.60.** Justification, verbatim: *"there is a chance it could be Memphis but I feel like it's almost for sure the Wolves based on everything I've seen."* Disclosure for change control: the decomposition offered was P(expansion by 2028-29) x P(MIN over MEM given expansion); Bobby's 0.60 sits slightly above the suggested 0.35-0.55 range and is logged as given, not adjusted. Internal-consistency note: 0.60 with expansion near 0.75 implies roughly 0.80 conditional on the Wolves, which matches "almost for sure." The weighted blend is emitted beside the per-scenario values with the +/-0.15 sensitivity band (0.45-0.75) in `board_step6_report.md`: at P(east)=0.60 the value of the East is +0.0005 root (rapm) and **+0.0151 root (box)**, band [+0.0109, +0.0195] on box.

**Fork prior = 0.5/0.5, confirmed for the freeze.** Bobby's confirmation of the agnostic recommendation (an agnostic prior is the strongest public position; it lets the season's realized reads do the adjudicating). Logged in `fork_adjudication.md`.

**Hash publication = YES.** The SHA-256 of the frozen bundle publishes in October. Change control governs any post-freeze amendment: an amendment is logged with its own hash and justification, so a correction never weakens the original proof (the original hash stands as what was frozen on 2026-10-20).

## Freeze dry-run (rehearsed 2026-07-17)

The freeze mechanics were rehearsed now so October 20 is the second run, not the first. `all-for-one/freeze_bundle.py` bundles the freeze set exactly as the real freeze will and computes the bundle SHA-256.

Procedure (deterministic by construction; the hash is the article's proof, so it must reproduce byte for byte):
1. Read each freeze-set artifact as raw BYTES (no line-ending normalization).
2. Compute each file's SHA-256; sort the lines by repo-relative path.
3. The bundle hash is SHA-256 over exactly those sorted `sha256  path` lines, and nothing else (no timestamps, machine names, or run order enter the output).
4. Members named but not yet materialized (item 8, the R1/R2 schedule mapping) are recorded as pending and are NOT hashed (absent = not in the bundle), so October adds them.

Rehearsal result: run twice, the manifest bytes and the bundle hash are **byte-identical** (`freeze_bundle.py --verify` -> PASS). Rehearsal bundle SHA-256 (over the current draft freeze set, after this session's ruling edits):

```
f1c3192d39b62ddfcaa9c4967ef2248e3d8cdbea47bc4a6b8fde0c4a84803d15
```

Nothing is published; this hash is local rehearsal only, over draft artifacts that will still change before October. The full manifest is `all-for-one/freeze_bundle_manifest.txt`.

## The critical path to 2026-10-20 (countdown mode)

Build mode is closed; no new mechanisms ship before the freeze absent a Bobby directive. The remaining active standing items:

1. **Mid-August**: NBA schedule releases -> fill item 8 (R1/R2 calendar dates).
2. **When LeBron signs**: fire the T1 field update with the real destination, re-solve, emit the marker-moved artifact unprompted, then refresh the roster snapshot (item 7).
3. **Final locks (before October)**: ratify tripwire wording (1), jaden thresholds (2), league-event thresholds (4).
4. **2026-10-20**: re-run `freeze_bundle.py` on the final artifacts, freeze, and publish the bundle hash (item 9 = YES).

Tripwires are untouched by this manifest's assembly; it only inventories them.
