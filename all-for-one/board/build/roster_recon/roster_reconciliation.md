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

**Judgment flagged for Bobby:** the exact bench split among Shannon Jr. / Lyles / Clark / Beringer / Hyland / Ingles / Anderson / Conley is a rotation projection, not a fact. The core six are solid; the last ~40 non-star minutes could distribute differently (e.g. Hyland or Ingles taking some of Shannon's). This affects MIN's aggregate net only at the margin (all these are near-replacement pieces), but it is a modeling choice, not data, and is labelled as such in the sim.

Bench (on roster, out of rotation): Bones Hyland, Joe Ingles, Kyle Anderson, Mike Conley, Julian Phillips, Isaiah Evans, DiVincenzo (out, Achilles); two-way / fringe: Enrique Freeman, Zyon Pullin, Rocco Zikarsky.

## Carry-forward logged

Silent-plausible bug #4 (**trade ingested, waiver/roster-consequence not**) added to the lamelo-pipeline carry-forwards: the post rotation encoded a player (a Gueye, wrong id and wrong team) who is not on the post-trade Timberwolves, at a real 18-mpg role. The fix is roster reconciliation against the transaction log before any sim consumes the rotation. This joins the earlier silent-plausible bugs (score_home/away; usg_pct scale; the board keystone fallback; the FC-DRB fallback-index).

## Gate verdict

**Reconciled and PASSABLE.** Every discrepancy is resolvable from the authoritative transaction log (no unresolvable ambiguity that would force a stop), so the sim may proceed on the reconciled rotation above, with the bench-split judgment flagged. The raw absolute nets in the file are NOT used (see the sim step: only the delta is robust, and title equity comes from bracket_sim proper, both forks).
