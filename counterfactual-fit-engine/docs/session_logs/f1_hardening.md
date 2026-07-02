# Session F1 — stint hardening (started 2026-07-02)

## First artifact: reconciliation harness + quantified baseline (208 games, 13 seasons x 16)
| stratum | quarantine | minutes recon | team-secs exact | poss parity | median worst delta |
|---|---|---|---|---|---|
| pooled | 0.0% | 37.1% | 100% | 0.0% | 9.8 min |
| legacy (<=2024-25) | 0.0% | 36.6% | 100% | 0.0% | 10.0 min |
| live (2025-26) | 0.0% | 43.0% | 100% | 0.0% | **1.0 min** |

Three of four G1 rows green from the fork; the war is minutes
reconciliation only, and AM-4's strata split it into two distinct diseases:
- LEGACY: structural errors, players off by ~10 minutes -- the
  period-start-inference + legacy sub name->id failure modes (plan fix
  order 1 and 2).
- LIVE: small systematic errors (~1-minute scale, most players close but
  over the 0.5 bar) -- sub-timing/FT-window boundary placement (fix order
  3) and clock-integration details. The headline-vector season is already
  structurally close.

## Repair loop order (per plan D3, confirmed by the profile)
1. Legacy period-start evidence extension (sub-out-without-sub-in => on at
   period start; box-minutes consistency bounds; per-period boxscore API
   for residual hard cases)
2. Legacy incoming-sub name->id from nba_player_stats rosters (not PBP-only)
3. FT-window/sub boundary placement (drives the live stratum)
4. Technical-FT shooters, missing-sub back-fills, OT boundaries
Re-run harness after each fix; the same 208-game baseline set is the
iteration bench (dev seasons only; G1 final judgment on the full build).

## Diagnostic on 3 worst legacy games (2026-07-02, closes the session)
Decisive negatives that reorder the repair plan:
- ZERO unresolved sub-IN names (the name->id hypothesis, plan fix 2, is
  DEAD for these cases -- the map resolves everyone).
- ZERO invisible players (bad players all appear in sub events).
- Corruption is near-total per game (19/23, 16/20, 19/23 player-games bad)
  while team-seconds stay exact: the floor MEMBERSHIP is wrong while
  interval time is right. Candidates: period-start floors cascading
  through otherwise-correct sub chains, or synthetic sub-IN event ordering
  (the +0.5 action_number tie-break) misplacing entries.
NEXT SESSION OPENS WITH: per-period error localization on these three
games (which periods carry the delta; starters vs bench; walk one game's
floor chain by hand against the box). Fix, re-run the 208-game bench,
iterate.
