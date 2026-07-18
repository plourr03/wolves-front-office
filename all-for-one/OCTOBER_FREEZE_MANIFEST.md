# October 20, 2026 Freeze Manifest (ONE FOR ALL)

The single dry-run checklist of everything that freezes on **2026-10-20**. One row per artifact, with owner and status; blanks are left visible on purpose, because an open blank is the point of a countdown. Assembled 2026-07-17. Nothing here is itself frozen; this is the list of what will be.

Freeze mechanics: on 2026-10-20 each CLOSED item is locked, the frozen set is bundled, and (if the hash decision below lands YES) the SHA-256 of the bundle is published so the February 2027 piece can prove nothing was chosen after the fact. The commit history from July 2026 forward is the corroborating trail.

## Freeze checklist

| # | Item | Artifact | Owner | Status | What closes it |
|---|---|---|---|---|---|
| 1 | Tripwires | `tripwire-backtest/TRIPWIRES.md` | Claude, ratify Bobby | **DRAFT READY** | one binding wire (AVAIL-PACE -> ARM-G) + FC-DRB structured advisory + ARM-S dashboard; final read of the wording |
| 2 | Jaden markers | `board/jaden_calibration/jaden_markers_v02.md` | Claude, ratify Bobby | **PROPOSED, calibration banked** | thresholds are PROPOSED/TUNE; calibration class (n=19) banked and ratified; lock the numbers |
| 3 | Fork adjudication | `board/docs/fork_adjudication.md` | Bobby (prior), Claude (form) | **PRIOR FIELD OPEN** | functional form + evidence + fire dates fixed; recommendation 0.5/0.5 logged; Bobby confirms or overrides the prior |
| 4 | League-event rule | `board/docs/league_event_resolve_rule.md` | Bobby (thresholds) | **THRESHOLDS TUNE** | four trigger classes fixed; top-15/55-win/top-10 cutoffs are TUNE; lock the thresholds |
| 5 | P(east) | `board/build/board_step6.py` (realignment) | **Bobby (prior)** | **AWAITING PRIOR** | scenario axis held unweighted; needs Bobby's P(east); blend + /-0.15 sensitivity emit on arrival |
| 6 | SALVAGE_CAP | `board/docs/board_spec.md` s4 | Bobby | **CLOSED (logged)** | ruled 0.012, "win it with Ant", logged verbatim under the anti-tuning clause. Done |
| 7 | Roster snapshot | `board/build/roster_recon/roster_reconciliation.md` | Claude | **POST-LEBRON PENDING** | log-derived 15-man is clean; must be refreshed after the LeBron resolution and any Aug-Oct moves before it freezes as THE snapshot |
| 8 | R1/R2 schedule mapping | fork adjudication + tripwire read dates | Claude | **AWAITING NBA SCHEDULE** | R1 (~game 18) and R2 (~game 37) map to calendar dates only once the 2026-27 NBA schedule is released (usually mid-Aug); fill the dates then |
| 9 | Hash publication | this manifest | **Bobby (decision)** | **OPEN** | decide whether to publish the SHA-256 of the frozen bundle in October. Yes = strongest proof; the flex is only as credible as the commit history behind it |

## Status roll-up (as of 2026-07-17)

- **Closed**: 1 of 9 (SALVAGE_CAP).
- **Draft/proposed, awaiting a final lock**: 3 (tripwires, jaden markers, league-event thresholds).
- **Awaiting Bobby**: 3 decisions (fork prior confirm-or-override, P(east) prior, hash publication).
- **Awaiting external / downstream**: 2 (NBA schedule release for R1/R2 dates; the LeBron resolution + late-summer moves for the final roster snapshot).

## The critical path to 2026-10-20

1. **Mid-August**: NBA schedule releases -> fill item 8 (R1/R2 calendar dates).
2. **When LeBron signs**: fire the T1 field update (item 5 machinery), then refresh the roster snapshot (item 7).
3. **Before October**: Bobby's three decisions land (items 3 prior, 5 P(east), 9 hash) with any logged justifications.
4. **Final locks**: ratify tripwire wording (1), jaden thresholds (2), league-event thresholds (4).
5. **2026-10-20**: bundle the closed set, freeze, and (if item 9 is YES) publish the hash.

Tripwires are untouched by this manifest's assembly; it only inventories them.
