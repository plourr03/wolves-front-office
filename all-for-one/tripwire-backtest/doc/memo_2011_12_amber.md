# Decision Memo: 2011-12 amber (stint trust spike)

Filed 2026-07-17, retroactive per Ruling 1 (2026-07-17). Ruled threshold: stint trust requires `recon_rate_TRUE_0p5 >= 0.995` and `quarantine_rate <= 0.005`; a season in the amber band 0.95-0.995 requires a tail census and this memo before its stint features are trusted.

## Trigger

2011-12 is the only sampled season in the amber band. Scorecard (`data/spike_scorecard.parquet`):

| | value | vs bar |
|---|---|---|
| recon_rate_TRUE_0p5 | 0.982324 | below 0.995, above 0.95 -> AMBER |
| quarantine_rate | 0.014706 (3 of 204 games) | above 0.005 -> AMBER |

Every other sampled season is green (2010-11, 2013-14, 2017-18, 2020-21 at 1.000; 2012-13 at 0.997; 2019-20 at 0.997) or, being 2021-22-plus, out of the spike window.

## Tail census

Both amber signals trace to a single cause. All three quarantines are the identical error:

```
0021100905  LegacySubResolutionError: legacy sub IN player unresolved: 'Pendergraph' (team 1610612754)
0021100877  LegacySubResolutionError: legacy sub IN player unresolved: 'Pendergraph' (team 1610612754)
0021100717  LegacySubResolutionError: legacy sub IN player unresolved: 'Pendergraph' (team 1610612754)
```

Jeff Pendergraph played for the 2011-12 Indiana Pacers (team 1610612754) and legally changed his name to **Jeff Ayres in 2013**. The warehouse player dimension stores the post-change name (Ayres); the 2011-12 play-by-play substitution text says "Pendergraph." The resolver cannot match the two and quarantines rather than seat the wrong player, which is the designed behavior (guessing is banned; an unresolvable sub means the floor state is genuinely unknown).

Excluding those three games, **2011-12 reconciles at 0.9995** across the other 201 sampled games (one player-game miss). So the recon depression and the quarantines are one and the same finding: 2011-12 is a green-quality season with a single missing name alias, not a structurally degraded one.

This is a **name-shaped** quarantine, which `decisions.md` classifies as extend-the-resolver-one-verified-bucket work, not a structural gate failure. The existing `_NAME_ALIASES` in fitengine's `floor_state.py` are all 2016-plus retro-renames; Pendergraph/Ayres is the same species from an earlier era.

## Resolution

**One verified alias entry**, added to fitengine's staged legacy-sub resolver: map "Pendergraph" (team 1610612754, 2011-12) to Jeff Ayres's `nba_player_id`. This is a carry-forward to fitengine's queue (its fork owns the resolver; Phase 0 does not edit it). Once added, 2011-12 moves from amber to green (projected 0.9995 / 0.000).

## Reference-class impact

**None.** The caveat affects only 2011-12 Indiana Pacers games in which Pendergraph subbed. No reference-class case is a 2011-12 Pacers team-season, so no case's `stint_grain_ok` flag is downgraded. The impact is confined to Phase 1 reliability curves (which sweep all team-seasons), where three 2011-12 Pacers games contribute box-grain-only until the alias lands. Given ~13,500 games in the Phase 1 panel, three games is immaterial to any r(N) estimate.

## Status

Amber resolved to a named, bounded, fixable finding. 2011-12 stint features are trusted for descriptive use with the three Pacers/Pendergraph games flagged. Carry-forward logged (`carryforwards.md`).
