# Post-Trade Roster Reconciliation (board step-four gate)

Produced 2026-07-17, before any Joan Bet sim, per the roster-gate directive. The encoded sim input `lamelo/data/impact/team_strength.json` (dated June 26) failed inspection against the July authoritative sources. This reconciles the post-trade MIN rotation and flags every discrepancy.

**Authoritative sources used:** `nba.nba_transactions` (July 2-11 moves, freshest event log) and `nba.nba_player_bio` (player-id disambiguation). Note: `nba.nba_team_rosters` at roster_date 2026-07-17 is itself STALE for this purpose (it still lists Randle and Naz Reid and lacks LaMelo/Green/Lyles/Evans), so the transaction log, not the roster snapshot, is the reconciliation spine.

## Discrepancies found (flagged for Bobby)

### 1. Gueye at 18 mpg is doubly spurious — the phantom-rotation error (silent-plausible bug #4)

The file's `post` rotation lists **"Mouhamed Gueye" at 18 minutes**. Two independent errors:
- **Wrong player.** "Mouhamed Gueye" (player_id 1631243) is an Atlanta forward, unconnected to any Minnesota move. The player the lamelo pipeline meant was **Mouhamadou Gueye** (1631338).
- **Wrong team, and never a Wolf.** Mouhamadou Gueye's only 2026 transaction is `2026-07-10 Trade: Charlotte received Mouhamadou Gueye from Chicago`. He went Chicago -> Charlotte. He is a Hornet. **Neither Gueye is on the post-trade Timberwolves.** The lamelo DELIVERABLE's "MIN receives LaMelo + Green + Gueye" did not match the executed trade, which sent MIN only LaMelo and Green (plus draft consideration to Charlotte, Randle to Brooklyn, Reid to Charlotte).

So the 18 rotation minutes assigned to a Gueye are phantom and must be removed and reallocated. This is exactly the pattern Bobby named: **the trade was ingested, the roster consequence (the player isn't actually here) was not.** Logged as silent-plausible bug #4 in the lamelo carry-forwards (below).

### 2. Missing July signings — the file predates them

The June-26 file carries generic `_fill` slots (`_fill_clark` 16, `_fill_min` 6) instead of the actual July depth, because it predates these moves:
- **Bones Hyland** re-signed 2026-07-03 (guard).
- **Trey Lyles** signed 2026-07-10 (forward/backup big).
- **Isaiah Evans** signed 2026-07-11 (forward).
- Jaylen Clark re-signed 2026-07-10 (the file's `_fill_clark` is correct in spirit; now named).
- Enrique Freeman re-signed 2026-07-02 (two-way).

### 3. Shannon Jr. absent at zero minutes — needs allocation (resolved with justification)

Terrence Shannon Jr. (2024 #27 pick, now a sophomore wing) is on the roster and absent from the file's rotation. On a thin post-trade bench he is a real rotation piece; **allocated minutes below** (a sophomore lottery-adjacent wing does not sit at zero on this roster), which is the explicit justification the gate required.

### 4. DiVincenzo correctly OUT (no discrepancy)

DiVincenzo (Achilles) is correctly absent from the rotation; he is on the roster but out most/all of 2026-27. Confirmed.

## Reconciled post-trade rotation (240 minutes, per-name provenance)

| Player | mpg | provenance |
|---|---|---|
| Anthony Edwards | 35 | core; #1 2020 |
| LaMelo Ball | 33 | trade in (CHA), 2026-07-10 |
| Jaden McDaniels | 33 | core |
| Rudy Gobert | 30 | core |
| Ayo Dosunmu | 28 | re-signed 2026-07-10 |
| Josh Green | 27 | trade in (CHA), 2026-07-10 |
| Terrence Shannon Jr. | 16 | #27 2024, sophomore wing; **allocated** (was absent at 0) |
| Jaylen Clark | 14 | re-signed 2026-07-10 (was `_fill_clark` 16) |
| Joan Beringer | 14 | #17 2025 rookie |
| Trey Lyles | 10 | signed 2026-07-10, backup big; **replaces the phantom Gueye frontcourt minutes** |
| **total** | **240** | |

Corrections vs the file: **Gueye 18 removed** (phantom), `_fill_min` 6 removed, and the freed 24 minutes reallocated to Shannon Jr. (16, was 0) and Trey Lyles (10), trimming Clark 16 -> 14. Core six (Edwards, LaMelo, McDaniels, Gobert, Dosunmu, Green) unchanged from the file.

**Judgment flagged for Bobby:** the exact bench split among Shannon Jr. / Lyles / Clark / Beringer / Hyland is a rotation projection, not a fact. The core six are solid; the last ~40 non-star minutes could distribute differently (e.g. Hyland taking some of Shannon's). This affects MIN's aggregate net only at the margin (all these are near-replacement pieces), but it is a modeling choice, not data, and is labelled as such in the sim.

## Full roster, log-derived (bench scrub, amended 2026-07-17)

Bobby's step-four review caught that the original bench list below carried Ingles / Kyle Anderson / Mike Conley / Julian Phillips, none of whom are Timberwolves. That list was residue from the same stale `nba_team_rosters` snapshot this document itself flagged in the sources note: the snapshot at roster_date 2026-07-17 lists 18 players and is wrong in BOTH directions, still carrying Randle, Reid, Anderson, Conley, Ingles, and Phillips while omitting LaMelo, Green, Lyles, and Evans. The rotation section above was built from the transaction log and is clean; the non-load-bearing bench paragraph reached for the snapshot and inherited its rot. Re-derived here strictly by applying the 2026 transaction-log deltas to that snapshot (snapshot + log-delta = current; the log is the authority for who moved).

**Departures the snapshot missed (transaction-log evidence):**

| Player | snapshot still lists | actual 2026 move (nba_transactions) |
|---|---|---|
| Julius Randle | yes | Trade -> Brooklyn Nets, 2026-07-10 (handled in rotation section) |
| Naz Reid | yes | Trade -> Charlotte Hornets, 2026-07-10 (handled in rotation section) |
| Kyle Anderson | yes | Signing -> Toronto Raptors, 2026-07-06 |
| Mike Conley | yes | Signing -> Boston Celtics, 2026-07-06 |
| Joe Ingles | yes | none in 2026; his 2024-07-06 one-year deal lapsed, unsigned FA |
| Julian Phillips | yes | none in 2026; his CHI-acquired expiring lapsed, not re-signed |

The four short-deal lapses are corroborated by the snapshot's own `how_acquired` stamps (Ingles signed 07/06/24, Phillips a 02/05/26 trade-in, Anderson a 03/01/26 signing, Conley a 02/17/26 signing) against the absence of any 2026 re-sign row.

**Clean 15-man plus two-ways (13 standard filled, 2 open, 3 two-way):**

- Standard, in rotation (10): Anthony Edwards, LaMelo Ball, Jaden McDaniels, Rudy Gobert, Ayo Dosunmu, Josh Green, Terrence Shannon Jr., Jaylen Clark, Joan Beringer, Trey Lyles.
- Standard, out of rotation (3): Donte DiVincenzo (out, Achilles), Bones Hyland, Isaiah Evans.
- Open standard spots: 2 (vet-minimum only, per the root-node cap state).
- Two-way (3): Enrique Freeman (re-signed two-way 2026-07-02, log-confirmed), Zyon Pullin, Rocco Zikarsky (both signed 2025, no 2026 move, held).

## Carry-forward logged

Silent-plausible bug #4 (**trade ingested, waiver/roster-consequence not**) added to the lamelo-pipeline carry-forwards: the post rotation encoded a player (a Gueye, wrong id and wrong team) who is not on the post-trade Timberwolves, at a real 18-mpg role. The fix is roster reconciliation against the transaction log before any sim consumes the rotation. This joins the earlier silent-plausible bugs (score_home/away; usg_pct scale; the board keystone fallback; the FC-DRB fallback-index).

Bench-scrub leak logged alongside it (amendment 2026-07-17): the stale `nba_team_rosters` snapshot contaminated this document's own non-load-bearing bench paragraph, the very section that flagged the snapshot as unreliable. The rotation (load-bearing) was log-derived and clean; the bench list was not, and copied the snapshot's four lapsed contracts (Anderson, Conley, Ingles, Phillips) into the roster. Lesson: a source flagged as unreliable must be quarantined from EVERY section, not only the load-bearing one, because this document is the freeze's roster snapshot and has to be clean end to end. Now re-derived from the transaction log throughout.

## Gate verdict

**Reconciled and PASSABLE.** Every discrepancy is resolvable from the authoritative transaction log (no unresolvable ambiguity that would force a stop), so the sim may proceed on the reconciled rotation above, with the bench-split judgment flagged. The raw absolute nets in the file are NOT used (see the sim step: only the delta is robust, and title equity comes from bracket_sim proper, both forks).
