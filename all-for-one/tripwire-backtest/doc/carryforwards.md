# Carry-forwards

Items surfaced by the tripwire backtest that are owned elsewhere or deferred to a later phase. Logged per Bobby's rulings 2026-07-17 so nothing is lost.

| # | Item | Owner | Status | Detail |
|---|---|---|---|---|
| 1 | Pendergraph/Ayres legacy-sub alias | fitengine (its fork owns the resolver) | queued | Add one verified alias: "Pendergraph" (team 1610612754, 2011-12) -> Jeff Ayres `nba_player_id`. Moves 2011-12 amber to green. See `memo_2011_12_amber.md`. |
| 2 | Usage-filter sensitivity, mandated for Phase 2 | tripwire Phase 2 | mandated | Report the Scenario A class under BOTH the strict 0.28 usage bar and a loosened bar. Cases sitting below 0.28 on prior-season usage: Harden-to-Clippers (0.202), Paul-to-Suns (0.221), Beal-to-Suns (0.224). Strict and loosened class definitions both reported; no silent choice. |
| 3 | lamelo/ availability reconciliation change set | Bobby (out of tripwire scope) | logged for Bobby | Three edits named in `phase0_availability_reconciliation.md`: (a) add above-model marker to DELIVERABLE prediction 3, or add the 49 model center beside the 63 bet; (b) fix the availability viz provenance comment (points at DELIVERABLE section 8, real source is fit_decomp/lever5_findings.md); (c) wire or drop the unused survival band [0.50, 0.90]. |
| 4 | Real per-player availability posterior | master plan board roadmap | scheduled off critical path | 1-2 week hierarchical model, customer is the board's `melo_avail` transitions, not the backtest. Build spec in `phase0_avail_pace_redefinition.md`. |
| 5 | G2 transactions curation, G3 SRS-proxy title odds | tripwire Phase 2 prep | scheduled | Per Bobby's ruling, both land inside Phase 2 prep. G2: derive offseason arrivals from player_season, hand-curate the pre-2015 midseason cases. G3: SRS proxy for the YA2 expectation baseline, not an odds archive. |
| 6 | `first_n_games` helper view | tripwire Phase 1 | to build | Trivial, from `nba_games` ordered by `game_date`. Not yet created. |
