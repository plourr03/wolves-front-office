# Phase 0 Stint Trust Spike

Tripwire backtest, Phase 0 Step 2. Run 2026-07-17. Scorecard: `all-for-one/tripwire-backtest/data/spike_scorecard.parquet` (930 rows). Sample manifest RNG seed 20260717.

## What this is, and what it is not

Three of five candidate wires (PAIR-DRTG, FC-DRB anchor-off, and Scenario C's YC1) need to know which five players were on the floor at each moment. No lineup table exists in the warehouse; lineups are reconstructed from play-by-play by fitengine's hardened builder. That builder's universe starts at 2013-14, so seasons 2010-11 through 2012-13 had never been attempted. This spike prices whether they can be.

**This is bench-class feasibility evidence, not a gate verdict.** fitengine's house rule (PICKUP.md rider 3, decisions.md) is that G-gate claims come only from the full 15,669-game panel, never from a sample. This spike samples. It therefore answers one question only: how far back is stint reconstruction trustworthy enough to compute descriptive features on. It reuses `reconcile.reconcile_game` unmodified, touches no pinned code, and writes no stint cache.

**Load-bearing numbers: `recon_rate_TRUE_0p5` and `quarantine_rate`, only.** `team_seconds_exact` and `poss_parity` are structural invariants (decisions.md 2026-07-02 directive item 1 rules them tautological), carried in the scorecard for comparability with the G1 panel but never quoted as evidence.

## Sample

930 unique regular-season games, three strata:

| Stratum | Games | What |
|---|---|---|
| frontier | 575 | Random draw, 150/season target, from 2010-11, 2011-12, 2012-13, 2013-14. Locates the trust frontier. |
| targeted | 176 | Every game of the three pre-2014 bonus cases: Anthony to NYK (from 2011-02-23), Paul to LAC (2011-12), Howard to LAL (2012-13). |
| spot | 179 | 20 games each from nine seed-case team-seasons, 2017-18 to 2020-21. Format weirdness is per-game, so season-level proof does not cover it. |

Seal guardrail honored: max season sampled is 2020-21 (yy20). fitengine seals yy21 (2021-22) and later until F5. The sample builder hard-asserts no game exceeds yy20; it passed.

### Sizing arithmetic

`recon_rate_TRUE_0p5` is scored over player-games (~21 played per game). The 95% CI half-width at p=0.998 is `1.96*sqrt(p(1-p)/N)`:

| Games | Player-games | +/- |
|---|---|---|
| 150 | 3,150 | 0.00156 |
| 600 | 12,600 | 0.00078 |
| 930 | 19,530 | 0.00063 |

So 150 games/season resolves 0.995 vs 0.998 comfortably.

`quarantine_rate` is scored over games and is the binding constraint on sample size. With zero observed quarantines the 95% upper bound is the rule of three, 3/n:

| Games | 0-quarantine 95% upper bound |
|---|---|
| 150 | 0.0200 |
| 600 | 0.0050 |
| 930 | 0.0032 |

**This asymmetry is load-bearing for the open threshold question.** A single 150-game season cannot, by itself, resolve a 0.005 quarantine bar; its tightest bound is 0.02. Only pooled across the four frontier seasons (600 games) can the sample bound quarantine at 0.005. Reported, not smoothed over.

## Result

Runtime 580s, 6 workers, single desktop.

### By season

| Season | Games | Player-games | Quarantined | Quar. rate | recon_TRUE_0.5 | median worst delta |
|---|---|---|---|---|---|---|
| 2010-11 | 172 | 3,509 | 0 | 0.0000 | **1.000000** | 0.008 min |
| 2011-12 | 204 | 4,243 | **3** | **0.0147** | **0.982324** | 0.008 min |
| 2012-13 | 225 | 4,642 | 0 | 0.0000 | 0.997199 | 0.008 min |
| 2013-14 | 150 | 3,121 | 0 | 0.0000 | 1.000000 | 0.008 min |
| 2017-18 | 60 | 1,258 | 0 | 0.0000 | 1.000000 | 0.008 min |
| 2019-20 | 59 | 1,247 | 0 | 0.0000 | 0.996792 | 0.008 min |
| 2020-21 | 60 | 1,255 | 0 | 0.0000 | 1.000000 | 0.008 min |

Pooled: 930 games, 19,275 player-games, 3 quarantines (0.003226), recon 0.995227. The 100%-legacy stratum (the whole window) matches the format the G1 panel clears at 0.998410, so these numbers sit on the same scale as the panel.

### The only wrinkle: one name in 2011-12

All three quarantines, and the entire reason 2011-12 sits below every other season, are the identical cause:

```
0021100905  LegacySubResolutionError: legacy sub IN player unresolved: 'Pendergraph'
0021100877  LegacySubResolutionError: legacy sub IN player unresolved: 'Pendergraph'
0021100717  LegacySubResolutionError: legacy sub IN player unresolved: 'Pendergraph'
```

Jeff Pendergraph played for the 2011-12 Indiana Pacers (team 1610612754) and **legally changed his name to Jeff Ayres in 2013.** The warehouse's player dimension carries the post-change name; the 2011-12 play-by-play substitution text says "Pendergraph." The resolver, correctly, refuses to guess and quarantines rather than seat the wrong player. This is the exact failure mode the house design intends: an unresolvable name means the floor state is genuinely unknown, so the game quarantines with a legible reason instead of silently corrupting.

**Excluding those three games, 2011-12 reconciles at 0.9995** (one player-game miss across the other 201 games). So 2011-12 is not a bad season. It is a clean season with one missing name alias.

This is a **name-shaped** quarantine, which decisions.md explicitly classifies as extend-the-resolver-one-bucket work, not a structural gate failure. The existing `_NAME_ALIASES` in floor_state.py are all 2016-plus retro-renames; Pendergraph/Ayres is the same species from an earlier era. The fix is one verified alias entry. It belongs to fitengine (its fork owns the resolver), not to this spike, and not to Phase 0.

### The residual tail is the panel's own tail

Six non-quarantined games (of 927) have a small number of player-game misses, worst deltas clustered near 5 minutes, one at 7.1: three in 2012-13, two in 2019-20, one in 2011-12. This is the same low-rate reconciliation tail the full G1 panel carries (the panel is 0.9984, not 1.000). It is not concentrated in the unproven seasons and does not distinguish them.

### Every pre-2014 bonus case is clean

The targeted stratum, which is the whole reason the spike exists, comes back spotless:

| Case | Games | recon_TRUE_0.5 |
|---|---|---|
| Anthony to NYK (Feb 2011) | 28 | 1.000 |
| Paul to LAC (2011-12) | 66 | 1.000 |
| Howard to LAL (2012-13) | 82 | 1.000 |

## Trust boundary

**Stint reconstruction is trustworthy back to 2010-11, the earliest season with warehouse data, with one named and bounded caveat.** There is no pre-2014 cliff. The 2013 floor in fitengine's universe was a scoping choice, not a data or quality limit, and this spike confirms it: 2010-11 and 2013-14 are perfect, 2012-13 is 0.997, and 2011-12 would join them at 0.9995 the moment the Pendergraph/Ayres alias is added.

### How this reads against the two candidate thresholds

The open threshold question (Bobby pinned 0.95/0.02; I proposed 0.995/0.005 with a 0.95-to-0.995 amber "investigate" band) resolves against real data like this:

| Season | Under 0.95 / 0.02 | Under 0.995 / 0.005 + amber |
|---|---|---|
| 2010-11 | pass | pass (green) |
| 2011-12 | **pass** (0.982 > 0.95, 0.0147 < 0.02) | **amber** -> tail census -> 100% one name -> one-alias fix |
| 2012-13 | pass | pass (green, 0.997) |
| 2013-14 | pass | pass (green) |

**2011-12 is the case that decides between the two bars, and it argues for the amber band.** At 0.95/0.02, 2011-12 passes clean and nobody ever learns that three Pacers games silently drop from any 2011-12 lineup metric, because Pendergraph never gets seated. At 0.995/0.005, 2011-12 goes amber, the investigation runs, and the output is a specific, fixable finding: add one alias, recover three games. The looser bar does not just admit a worse season; it admits it without surfacing the reason, which is exactly the failure the tripwire project exists to avoid. My recommendation stands: **0.995 / 0.005, amber band 0.95-0.995, amber produces a decision memo.**

If Bobby holds at 0.95/0.02 after this, the practical consequence is small (all four frontier seasons pass either way); the difference is entirely whether 2011-12's missing alias gets named or buried.

## stint_grain_ok, per reference-class case

Per the plan, the class is not truncated at any boundary. A case that fails stint reconstruction stays in as a box-grain-only member and loses only its lineup-dependent features. The flag:

| Case era | stint_grain_ok | Basis |
|---|---|---|
| Pre-2014 cases (Anthony NYK 2011, Paul LAC 2011, Howard LAL 2012-13) | **TRUE** | Verified clean by this spike, targeted stratum, 100% recon. |
| 2014-15 to 2020-21 cases | **TRUE** | Inside fitengine's G1-proven panel; this spike's 2017-20 spot checks confirm at sample level. |
| 2021-22 onward (Mitchell 2022, Harden-76ers 2022, Lillard 2023, Beal 2023, Murray 2024, Fox 2025, Doncic 2025) | **PRESUMED, sealed** | Same legacy/live machinery, G1-proven formats, but these seasons are inside fitengine's F5 seal. Mechanical reconstruction is presumed fine; see governance question 1 in the plan about consuming fitted artifacts here. Not spike-verified, by design. |

The 2011-12 caveat propagates to exactly one place: any case whose lineup metrics are computed on 2011-12 Indiana Pacers games in which Pendergraph subbed. None of the reference-class cases are 2011-12 Pacers, so no case's `stint_grain_ok` is downgraded by it. It matters for Phase 1 reliability curves (which sweep all team-seasons), not for the reference class.

## What this changes in the spec

Section 3's era window ("primary class 2010-11 through 2025-26") is **confirmed feasible on its early end.** No amendment needed to push the window back; the window is not the constraint. The one carried caveat is the Pendergraph/Ayres alias, logged here and owned by fitengine.

## Reproduce

```
python all-for-one/tripwire-backtest/scripts/build_spike_sample.py   # writes scratchpad/spike_sample.json
python all-for-one/tripwire-backtest/scripts/run_spike.py            # writes data/spike_scorecard.parquet
```
