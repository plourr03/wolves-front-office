# League-Event Re-Solve Rule: Pre-Registered Field Triggers

Pre-registered 2026-07-17 for the ONE FOR ALL board. **The trigger classes below freeze with the October 20, 2026 freeze; thresholds are TUNE until then and fixed after.** This rule governs OUT-OF-CYCLE updates to the ENVIRONMENT (the field of rival teams), separate from the calendar nodes and separate from the MIN-actionable standing orders.

## Scope: the environment side only

The board already carries two MIN-actionable standing orders (board_spec section 7): **STAR-AVAILABLE** (a top-15 player becomes gettable by MIN) and **CONTENDER-COLLAPSE** (a rival sells, and MIN is a prepared buyer). Those stay exactly as written; they are about what MIN can DO.

This rule is the mirror on the other side of the table: a change in the FIELD that alters MIN's title odds without MIN doing anything. When a trigger fires, the field is updated (a rival's strength moves), the board is re-solved, and the equity delta is reported. Per the organizing principle logged in the spec, the field is modeled as changing, never as scheming: a trigger updates a rival's strength from the fact of the event, it does not simulate the rival's strategy against MIN.

## Trigger classes (freeze the text, TUNE the thresholds)

**T1. A consensus top-15 player changes teams.** Trigger: a player inside the consensus top-15 (by the board's value layer or a named public aggregate) is traded or signs with a new team. Field update: move that player's impact from the old team's net to the new team's net (the LeBron resolution, `board_step6.lebron_field_update`, is the worked first instance). Threshold TUNE: the top-15 cutoff and the impact magnitude.

**T2. A 55-plus-win core breaks up.** Trigger: a team that won 55 or more games in the prior season trades away a top-3 contributor (a core dissolution, not a depth move). Field update: that team's net drops toward its post-breakup roster; the picks/players it received redistribute to the acquiring teams. Threshold TUNE: the 55-win line, the "top-3 contributor" test.

**T3. A season-ending injury to a top-10 player on a West contender.** Trigger: a top-10 player on a Western Conference team projected as a top-6 seed suffers a season-ending injury. Field update: that team's net drops for the affected season; MIN's Western path eases. Threshold TUNE: the top-10 cutoff, the "West contender" seed line. (This is the field-side complement to OWN-INJURY, which handles MIN's own losses.)

**T4. League-structure events.** Trigger: expansion confirmed, realignment announced, or a playoff-format change adopted. Field update: re-scope the playoff field itself (a new team dilutes the pool; realignment moves MIN's conference, which the realignment axis in `board_step6` already prices as the value of the East; a format change alters the run-stage bracket). Threshold: none (these are discrete announced facts, not magnitudes).

## What a fire does

Each fire runs the same three steps, then stops for a human read:

1. **Update the field.** Apply the event's fact to the affected team(s)' net(s) via the evolution machinery (`board_step6`), never by inventing a downstream trade chain.
2. **Re-solve** the board under both forks and both patience curves.
3. **Emit the delta**: MIN's title-equity and root-value change, and any policy flips (a move that was HOLD under both curves that now flips). Report as a marker-moved artifact with the event named and dated.

## Discipline

- Thresholds are TUNE now and frozen in October; they are not revised in response to a fired update's output (the same anti-tuning rule as SIGN_GATE, SALVAGE_CAP, and the fork adjudication).
- A fire updates strength from the event's FACT. It does not model the rival responding to MIN, and it does not predict the rival's next move. Mean field with exact interaction only at MIN's own trade table (board_spec limitations).
- Environment side only. If an event both changes the field AND opens a MIN action (a rival selling a star MIN could get), the field update runs here and the action runs under STAR-AVAILABLE / CONTENDER-COLLAPSE; the two are logged separately so the environment change and the MIN decision never blur.

## First instance on record

The LeBron resolution is staged as the first T1 fire (`board_step6.lebron_field_update`, `board_step6_report.md`): on his decision, the field updates for his assumed destination, the board re-solves, and the MIN title-equity delta is emitted as the first marker-moved artifact. The worked example fixes the machinery before any real trigger fires in-season.
