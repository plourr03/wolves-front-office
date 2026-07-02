# PICKUP: fitengine, written 2026-07-02 ~17:00 (desktop, end of the F1 repair session)

This is the resume-here document for switching machines. Everything below is current as of commit f51a6fed plus one in-flight background job. The authoritative record of every ruling and fix is docs/decisions.md; this doc is the operational map.

## 1. Where the project stands

- F0 is DONE (commit bbcbcc06): scaffold, venv, AM-1 hash-pinned adapter over postmortem/lib, R1 game-universe audit (15,669 train-eligible regular-season games 2013-26; the 2013-14 "gap" never existed), protocol freezes.
- R2 is RATIFIED with amendments 1-4 landed (commit 08e5e301): backtest protocol precision, subscripted redundancy formula, conformal decircularized (calibration 2019, coverage gate 2020+2021), cross-repo artifact sha256 pins.
- F1 repair loop is COMPLETE and committed (f51a6fed). The 208-game bench reads 208/208 games with 100% minutes reconciliation on BOTH criteria, zero quarantines, both format strata. Median worst per-player error is about half a second.
- The FULL-PANEL build (all 15,669 games) was launched 15:56 on the desktop and was at ~7,500/15,669 at 16:53. ETA ~17:50. It writes data/cache/stints/{game_id}.parquet per game plus outputs/reconciliation_panel_full.parquet (checkpointed every 500 games, resumable).
- G1 has NOT been judged yet. That judgment comes only from the full-panel scorecard, per the F1 directive. Nothing downstream of F1 has been touched.

## 2. What happened in the F1 repair session (the short version)

Full detail with verbatim rationale lives in docs/decisions.md, sections dated 2026-07-02 (night). Three diseases, three fixes:

1. Period-start floors: sub-out-first evidence (a player whose first sub event in a period is an OUT was on at period start) plus a negative-evidence padding ban (a player whose first period event is a sub-IN provably did not start it).
2. Legacy sub name resolution: the inherited resolver missed diacritic spellings ('Porzingis' in descriptions vs 'Porziņģis' in player_name) and on any miss silently seated the OUTGOING player as the incoming one (an identity swap invisible to team-seconds and possession parity). Replaced with a staged team-scoped resolver, _resolve_sub_in in src/stints/floor_state.py: PBP exact-form map first (within a game, name forms are minimal-unique: plain 'Williams' means Grant precisely because Robert is 'Williams III'), then roster map, then suffix-stripped retries ('Martin Jr.' vs retro-renamed 'KJ Martin'), then first-name prefix matching ('Jal.'/'Jay.' Williams, 'Marc'/'Mark' Morris), with OUT-pid elimination at every stage. One recorded alias: kanter to freedom (the feed retro-renames player_name and rosters from the current registry while description text stays original). Unresolvable subs now RAISE and quarantine the game legibly. Guessing is banned.
3. Starter derivation: nba_player_advanced_stats.position marks exactly the five official starters per team in ALL 15,669 panel games, so derive_starters now reads official starters first. The old defensive fallback (top 5 by period-1 appearance count) lost quiet starters to active bench players on unstable-sort tie flips. That produced the compensating-errors episode worth remembering: fixing the identity swap REGRESSED one game because the old bug had been luckily flipping a starter tie the right way. Logged in full in decisions.md.

Two gate-relevant data discoveries, both memo'd in decisions.md:

- nba_player_advanced_stats.minutes_float is SECONDS-PRECISE official minutes with full panel coverage. The PRIMARY G1 gate is therefore the spec's ORIGINAL criterion (99.5% of player-games within 0.5 min of true seconds) evaluated on the full panel. This satisfies rider 1's seconds-precise stratum at strictly larger coverage than the planned 200-game targeted nba_api pulls (same source data, already ingested). The truncation-aware relaxed metric vs integer minutes_played stays as the SECONDARY gate. G1 green requires both.
- PBP format is a PER-GAME property, not a season property. The 2025-26 warehouse load is mixed (27,436 legacy-format sub events vs 88,302 live-format). AM-4 strata now key on per-game detection (process_game returns pbp_format), never the season prefix.

## 3. The in-flight job and how to handle the machine switch

The panel build is running on the DESKTOP in a background shell: `.venv/Scripts/python -m src.stints.run_panel panel_full 6` from the fitengine folder.

Preferred: let the desktop finish (ETA ~17:50, roughly an hour after you asked). It survives you locking the screen; it does not survive shutdown or sleep. When it finishes, the summary table prints at the end of the run log and outputs/reconciliation_panel_full.parquet holds the full scorecard. Commit that parquet.

If the desktop gets shut down mid-run, nothing is lost: the run checkpoints every 500 games. Two resume paths on any machine:

- Same machine later: rerun the exact command above. It reads the existing outputs/reconciliation_panel_full.parquet, skips finished games, continues.
- On the laptop: after git pull, the checkpoint parquet comes with the repo (outputs/ is tracked). CAVEAT: resuming from the checkpoint SKIPS games already scored, so their per-game stint parquets will NOT be written locally (data/cache/stints/ is gitignored as the D6 rebuild seam, it stays on the desktop). That is fine for the G1 JUDGMENT, which needs only the scorecard. It is NOT fine for the DuckDB stint load. If you want a complete local cache on the laptop, delete outputs/reconciliation_panel_full.parquet first and run fresh overnight (2-3h); otherwise do the DuckDB load back on the desktop.

## 4. Laptop environment setup

1. git pull. The repo carries everything except the venv, the .env, and the stint cache.
2. Python 3.13 venv in counterfactual-fit-engine/: `python -m venv .venv` then `.venv/Scripts/pip install -r requirements.lock` (the lock file pins the exact F0-verified versions; requirements.txt is the loose list).
3. Warehouse access: repo-root .env with the POSTGRES_* variables (copy from the desktop or recreate; it is not in git). AWAY FROM THE HOME LAN THE HOST IS THE TAILSCALE ADDRESS 100.69.186.94, not 192.168.1.236. Never localhost.
4. Smoke: `.venv/Scripts/python -m pytest tests/ -q` (13 tests: AM-1 pin verification, golden possession fixtures both formats, R1 census). If the AM-1 pin test fails, postmortem/lib drifted relative to config/pinned_lib.yaml; that is a stop-and-memo situation, not a re-pin.
5. Cross-repo artifact pins (config/model_params.yaml pinned_artifacts) reference the pick2033 aging posterior and warehouse.duckdb. They are verified at load, first needed at F2/F3, not for G1.

## 5. Next work, in order

1. G1 JUDGMENT from outputs/reconciliation_panel_full.parquet once complete. Load it, run src/stints/reconcile.summarize, and judge:
   - recon_rate_TRUE_0p5 >= 0.995 (primary, seconds-precise reference), pooled AND per stratum (legacy, live).
   - recon_rate_relaxed >= 0.995 (secondary, truncation-aware vs integer reference).
   - quarantine_rate < 0.005 with every quarantine reason read and bucketed (they are legible LegacySubResolutionError messages by design).
   - team_seconds_exact and poss_parity remain labeled structural invariants in the report.
   - AM-3 denominator discipline is built into summarize (quarantined games count all their player-games as failed).
2. If new quarantine name-forms appear at panel scale (the bench saw 22 in 4 buckets, all fixed): extend the staged resolver the same way, one verified bucket at a time, rerun only the quarantined games, update the scorecard. If something fails the gate NON-name-shaped: STOP, decision memo for Bobby, no retunes (house rule).
3. G1 verdict goes in docs/decisions.md either way, with the summary table pasted verbatim. If green: F1 is closed.
4. DuckDB load of the stint cache (games dim, stints, quarantine, reconciliation tables per plan D6). Needs the full cache, see section 3 caveat about which machine has it.
5. F2 begins: Layer 1a ridge RAPM per plan D4 (seed from offseason/scripts/build_rapm.py, per-season O/D fits, two-stage priors, A1 posterior covariance parquets). Gate G2 RAPM rows (YoY 0.50-0.75, face checks).

## 6. Key files map

- docs/decisions.md: every ruling verbatim, the whole F1 story. READ THE 2026-07-02 (night) SECTIONS FIRST if anything is unclear.
- docs/predictions.md: P-F1..P-F3, timestamped, untouched since F0. Graded at the sealed backtest, not before.
- src/stints/floor_state.py: the hardened fork (starters, floor walk, legacy shim, staged resolver). The pinned original in postmortem/lib is the comparison baseline and is NEVER edited.
- src/stints/stint_builder.py: fork of lineup_aggregation, derive_stints.
- src/stints/reconcile.py: the G1 instrument. reconcile_game scores one game (and writes its stint parquet when given stints_dir); summarize produces the gate table; main runs the 208-game bench (argv tag, do not overwrite reconciliation_baseline).
- src/stints/run_panel.py: resumable multiprocess full-panel build. Usage: `python -m src.stints.run_panel [tag] [workers]`.
- src/adapters/postmortem_lib.py: AM-1 fence (git blob hashes, refuses drift). src/adapters/pinned_artifacts.py: R2-4 fence (sha256).
- config/: pinned_lib.yaml, model_params.yaml, backtest_protocol.yaml (FROZEN), redundancy_def.yaml (FROZEN).
- outputs/reconciliation_*.parquet: baseline (pre-repair, preserve), bench_fix123 (round 1), bench_fix4 (round 2, all green), panel_full (in flight).
- tests/: 13 contract tests. data/staged/game_universe.parquet: the R1 include-list census.

## 7. Discipline reminders that bind the next session

- Bench (208 games) is for repair iteration; G1 claims come ONLY from the full panel. Both criteria must pass.
- Gate failures produce decision memos for Bobby's ruling. No silent retunes, no threshold revisions.
- The sealed 2022-26 backtest window has not been touched and gets exactly one look, at F5.
- Provisional numbers stay quarantined and tagged. FINAL artifacts by designation, never file recency.
- Repair inference against integer official minutes must use the truncation interval [m, m+1), never m plus-minus tolerance (rider 2). With minutes_float available this mostly does not come up, but the rule stands.
- The 2025-26 format detection matters because LaMelo's vectors come from that season (AM-4 rationale); it keeps its own stratum in every gate report.

## 8. Cross-project note

pick2033 is dormant with everything staged: JULY 6 IS MONDAY. The five-button runbook is pick2033/JULY6_RUNBOOK.md (button 0 is your LaMelo news word: unsigned, extended, or unresolved). Nothing in fitengine blocks or is blocked by it; just do not let the weekend absorb the Monday.

## 9. State of the session task list

F0 tasks 1-6 complete. F1 repair complete (bench 208/208, commit f51a6fed). Open: full-panel build + G1 judgment (in flight), then DuckDB load and F1 close-out, then F2. No decisions are currently pending on Bobby beyond the eventual G1 verdict read.

## 10. Agent bootstrap prompt

Paste everything inside the fence below as the first message to a fresh Claude Code session opened in the wolves-front-office repo on the new machine.

```
You are picking up the fitengine project (counterfactual-fit-engine/) mid-build, continuing the work of a previous agent session that ended cleanly. Get up to speed, then continue in auto mode. Read in this order before doing anything else:

1. counterfactual-fit-engine/PICKUP.md, the whole thing. It is the operational map: current state, the in-flight full-panel build and its resume semantics, laptop environment setup, and the ordered work queue.
2. counterfactual-fit-engine/docs/decisions.md, at minimum every section dated 2026-07-02. This is the authoritative record. Every ruling from me in there is binding and recorded verbatim; the F1 night sections tell you exactly what was fixed and why.
3. counterfactual-fit-engine/wtat-project1-fit-engine-implementation-spec.md for the full build plan (layers, gates G1-G5, sessions F0-F6), plus the frozen configs in counterfactual-fit-engine/config/ (backtest_protocol.yaml and redundancy_def.yaml are FROZEN, do not touch) and docs/predictions.md (P-F1..P-F3 are timestamped, graded later, never edited).

House rules, binding on everything you do:
- Sealed test windows get exactly one look. The 2022-26 backtest window is sealed until F5. Never peek, never rehearse on it.
- Gate failures produce a decision memo for MY ruling. Never silently retune, never revise a threshold to make a gate pass. If G1 fails on the full panel for any non-name-resolution reason, stop and write the memo.
- Provisional numbers are quarantined and tagged. FINAL artifacts are FINAL by designation, never by file recency.
- The bench (208 games) is for repair iteration only; gate claims come only from the full 15,669-game panel.
- The AM-1 fence: postmortem/lib is imported frozen through hash-pinned adapters. If a pin test fails, that is a stop-and-memo, not a re-pin. The fork in src/stints/ is yours to edit; the pinned originals are never edited.
- Record every ruling I give you verbatim in docs/decisions.md, and log your own wrong hypotheses there the same way you log mine (hypothesis scoreboard convention).
- Complexity must be earned by a named gate failure. Do not add machinery speculatively.

Working style with me:
- I approved the plan through F6 and ratified the R2 freezes, so within that scope you run auto without asking. New phases follow the plan as written. Only stop for genuine scope changes, gate-failure memos, or things only I can decide.
- When you find something surprising, verify it against source data before coding on it. This session's biggest catch (the compensating-errors episode in decisions.md) came from refusing to accept an impossible result.
- Writing rules for anything you draft: never use em dashes or en dashes, use periods, commas, or parentheses instead. In article draft files, one line per paragraph, no hard wrapping. Treat unusual spellings in my messages as voice, not errors.

Environment notes (Windows, PowerShell and Git Bash both available):
- Warehouse is Postgres. Away from the home LAN the host is the Tailscale address 100.69.186.94 (home LAN is 192.168.1.236). NEVER localhost. Credentials come from the repo-root .env via POSTGRES_* variables; if .env is missing I need to copy it over, ask me.
- Use the project venv: counterfactual-fit-engine/.venv/Scripts/python. If it does not exist yet, build it per PICKUP.md section 4 (python 3.13, requirements.lock).
- Set PYTHONIOENCODING=utf-8 when printing player names (diacritics break cp1252).
- NBA Stats API data is for analysis only, raw play-by-play is never redistributed.

Your immediate work queue (details in PICKUP.md section 5):
1. Verify environment: pytest green (13 tests), warehouse reachable.
2. Determine the full-panel build state (outputs/reconciliation_panel_full.parquet). Resume or rerun per PICKUP.md section 3 if incomplete. The desktop may have already finished it; check the row count against 15,669 before redoing anything.
3. Judge G1 from the completed panel scorecard: recon_rate_TRUE_0p5 >= 0.995 AND recon_rate_relaxed >= 0.995, pooled and per format stratum, quarantine_rate < 0.005 with every quarantine reason read. New name-resolution buckets get verified fixes in the staged resolver (src/stints/floor_state.py, _resolve_sub_in) followed by rerunning only the quarantined games. Anything else that fails: decision memo.
4. Write the G1 verdict into docs/decisions.md with the summary table pasted verbatim, green or not.
5. If green: DuckDB load of the stint cache (mind the which-machine-has-the-cache caveat in PICKUP.md section 3), close F1, then start F2 (Layer 1a RAPM per plan D4, seeded from offseason/scripts/build_rapm.py, with the A1 covariance parquets).

Announce what you find at each step in plain language, keep decisions.md current as you go, and commit in the existing style (subjects prefixed "fitengine ...", body explaining what and why).
```
