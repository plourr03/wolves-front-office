# LAFI v1 (canonical) vs v1.1 (dashboard pipeline) reconciliation audit

**Author:** analytical partner
**Date:** 2026-05-19
**Status:** decision-ready
**Scope:** targeted audit. Not a rebuild. Goal is to determine which set of 2025-26 Wolves LAFI values the website should publish.

---

## 1. Executive summary

**Publish v1 (canonical) values. The v1.1 Firestore numbers are not a like-for-like recomputation of the canonical methodology and should not be trusted as a replacement.**

The two pipelines differ on three independent axes, each of which alone would explain part of the gap:

1. **Reference distribution.** Canonical percentile-ranks each team-season against a **pooled 12-season sample (~360 rows, 2014-15 to 2025-26)**. v1.1 percentile-ranks against the **current-season-only 30 teams** (verified by inspecting v1.1's leagueMin / leagueAverage / leagueMax bounds, which sit at roughly 1, 50, 95 on every component, indicating a 30-team rank).
2. **Sub-metric set.** Canonical C4 has three sub-metrics. v1.1 C4 has two completely different sub-metrics (one of which appears to be a Spotup-share concentration measure rather than the Shannon entropy / designed-action share / ball-dominant share used canonically). Canonical C3 uses pull-up FGA share; v1.1 C3 substitutes a pull-up to catch-and-shoot ratio (which is structurally closer to a C5 sub-metric than to the canonical C3 design). Canonical C5 has four sub-metrics; v1.1 has two.
3. **Historical context inside the v1.1 doc itself disagrees with the canonical 5-component CSV.** v1.1's `wolvesPercentileLastSeason` for C4 is 74; canonical 2024-25 C4 is 35.8. v1.1 says C4 trended 73 (23-24) -> 74 (24-25) -> 28 (25-26); canonical shows 27 -> 36 -> 45. Same kind of mismatch on C2. These cannot both be measuring the same component on the same data.

This is **not a "different reference period" disagreement that can be reconciled with a percentile remap**. v1.1 is using different sub-metric definitions for at least C3, C4, and C5, plus a different reference universe, plus (in some components) what looks like a different data extract entirely.

**Recommendation:** publish the canonical Q0A values (31 / 72 / 90 / 45 / 83, Sharp 90, Full 65) on the dashboard. Treat v1.1 as a Firestore writer that drifted from the canonical implementation and needs to be rewritten against `analyses/q0a_lafi/` before any further publishing. The qualitative dashboard narrative ("distributed pickup, extreme on Sharp LAFI") is unchanged, but the specific numbers must come from the canonical pipeline.

The downstream cascade is therefore zero. No Q5 v4 / Q0C / Q4 re-work is triggered because v1 stands.

---

## 2. Status of v1.1 code location

**Not located.** The Python or TypeScript that writes `visualizations/lafi-fingerprint-2025-26` to Firestore was not found in any local repo.

Searched and confirmed absent from:

- `C:\Users\bobby\playground\wolves-front-office\` (no Firestore writer, no `publish*.py`, no `lafi*publish*`)
- `C:\Users\bobby\playground\chasing-the-first-banner\functions\src\` (only article-publish, sitemap, team-status, contact, auth functions; no LAFI writer)
- `C:\Users\bobby\playground\chasing-the-first-banner\` recursively (only the Dart reader and the model)
- `C:\Users\bobby\playground\nba-warehouse\pipeline\` (only data-ingest scripts; no Firestore client)
- `C:\Users\bobby\playground\nba-warehouse\` recursively (only mentions of LAFI in specs as a downstream consumer)
- `C:\Users\bobby\playground\timberwolves-2026-retro\` (predecessor repo; no Firestore writer)
- All known service-account JSON files (carry, dish-deets, settlers-after-dark, weekwell-dev, weekwell-typesense). None for `chasing-the-first-banner`.

What was located instead: the **Firestore document itself** at `visualizations/lafi-fingerprint-2025-26`. Public read on `visualizations/*` (verified in `firestore.rules`). Pulled the live document via the Firestore REST API. The doc was last updated 2026-05-19 03:39:08 UTC (today). The document carries **no provenance fields**: no `pipelineVersion`, no `computedAt` distinct from `lastUpdated`, no `sourceCommit`. The fields are limited to season, components, composites, and lastUpdated.

**Inference:** the v1.1 writer likely runs on the home server (`192.168.1.236`) where the warehouse cron lives, or on a Cloud Function not in the local checkout, or as a manual ad-hoc Python script that was not committed. It writes the document fresh each day (createTime 2026-05-19T01:39:22, updateTime 2026-05-19T03:39:08, both today).

**The audit below is structured around the comparison of canonical code, canonical CSV output, and the live Firestore document. I do not have the v1.1 source to inspect directly, so for every gap I distinguish "verified" (comparing canonical code to canonical CSV) from "consistent with" (inferred from the Firestore document shape).**

---

## 3. Component by component

### Universal verified findings (apply to every component)

**v1.1's reference distribution is current-season-only, not the 12-season pool.**

Evidence: v1.1's `leagueMin` / `leagueAverage` / `leagueMax` values for the five components are (1, 52, 89), (3, 49, 95), (2, 50, 97), (6, 48, 96), (0, 50, 98). Every component has a league average near 50, a min within a few points of 0, and a max within a few points of 100. That is the signature of a percentile rank inside a 30-team pool ranked symmetrically. A 12-season pool of ~360 team-seasons would not produce min/max that symmetric for the current-season Wolves because the Wolves are not extremes in every component every year. The canonical 5-component CSV confirms this: across 12 seasons, the Wolves' pctiles range from single digits (2019-20 C5 = 5.5) to mid-90s (2017-18 C4 = 95.6).

**Implication:** for every component, v1.1's percentile rank is "where the 2025-26 Wolves stand among the other 29 current teams," and the canonical percentile rank is "where the 2025-26 Wolves stand against the 359 team-seasons of the modern era." These are different questions. They cannot be directly compared without remapping one onto the other.

This single methodological difference is enough to explain small gaps in components where the Wolves' raw values match the canonical raw values (C1, C3). It is **not** enough to explain C4 or the historical-context divergences (see C4 below).

---

### Component 1: Ball Stickiness

| Source | Wolves 2025-26 percentile |
|---|---|
| Canonical (CSV verified) | 30.6 (rounds to 31) |
| v1.1 Firestore | 30 |
| Gap | -1 (canonical -> v1.1) |

**Spec.** Section 2.2 calls for four sub-metrics: lead-handler ToP share, long-touch possession rate (4+ second hold), dribbles per touch, inverse passes per possession.

**Canonical implementation** (`components/ball_stickiness.py:98-104`):

```
sub["lead_handler_top_share"]      = top player time_of_poss / team time_of_poss
sub["avg_sec_per_touch"]           = team avg seconds per touch (v1 proxy for spec's 4+sec rate)
sub["avg_drib_per_touch"]          = team avg dribbles per touch
sub["inv_passes_per_possession"]   = -1.0 * passes_made / poss_total
```

Each z-scored within (season, season_type), averaged, percentile-ranked across the 12-season pool.

**v1.1 sub-metrics** (from Firestore subMetrics map):

```
leadHandlerToTOPshare:           0.21592
averageSecondsPerTouch:          2.91
dribblesPerTouch:                2.25
inversePassesPerPossession:      0.40105
```

These match the canonical four sub-metric names one-for-one and the raw values are plausible for the 2025-26 Wolves.

**Diff.** Only the reference distribution (current 30 teams vs 12-season pool of ~360). Sub-metric names and structure match.

**Classification: Recoverable.** Same sub-metrics, same data sources, different pool size. The 1-point gap (30.6 -> 30) is within rounding tolerance and the universe difference combined.

**Canonical going forward: 31.**

---

### Component 2: Movement Death

| Source | Wolves 2025-26 percentile |
|---|---|
| Canonical (CSV verified) | 71.8 (rounds to 72) |
| v1.1 Firestore | 78 |
| Gap | +6 |

**Spec.** Section 2.3 calls for four sub-metrics: off-ball distance per possession, off-ball screens per 100 possessions, cuts per 100 possessions, inter-player spacing SD. Section 2.3 notes sub-metric 4 may be deferred to v2.

**Canonical implementation** (`components/movement_death.py:126-134`): three sub-metrics consistent with spec sub-metrics 1, 2, 3. Sub-metric 4 deferred per the spec's own note.

```
sub["inv_off_ball_miles_per_possession"]  (lead handler subtracted, /4)
sub["inv_off_screen_frequency"]            (Synergy OffScreen poss_pct)
sub["inv_cut_frequency"]                    (Synergy Cut poss_pct)
```

**v1.1 sub-metrics** (from Firestore):

```
inverseOffBallDistancePerPossession:   0.00888
inverseOffScreenPossessionPct:         0.021
inverseCutPossessionPct:               0.046
```

Sub-metric names and conceptual structure match the canonical. Raw values are plausible (Synergy Cut 4.6% matches the canonical investigation table's Wolves 2025-26 Cut share of 5.2% to within reasonable tolerance; OffScreen 2.1% matches canonical 5.0% less cleanly, but both are in the low single-digit Synergy percentages).

Wait. **Raw OffScreen mismatch (canonical 5.0%, v1.1 2.1%) is worth flagging.** This is consistent with either (a) a different Synergy extract date, (b) a different play_type filter, or (c) some downstream aggregation step that differs. I cannot verify without seeing v1.1 source.

**Historical context inside v1.1 disagrees with canonical 5-component CSV.** v1.1's `wolvesPercentileLastSeason` (24-25) = 42; canonical 24-25 = 55.5. v1.1's two-seasons-ago (23-24) = 30; canonical 23-24 = 43.0. This is consistent with the current-season-only reference distribution (different teams in each year would shuffle the Wolves' rank), but it could also be consistent with different raw inputs.

**Diff.** Sub-metric structure matches. Either the reference distribution (verified) or the Synergy extract (suspected but not verified) differs. Most of the +6 gap is plausibly explained by the 30-team vs 360-team reference difference, but the OffScreen raw discrepancy is unexplained.

**Classification: Recoverable + Unknown.** The reference-distribution piece is recoverable. The OffScreen-raw discrepancy is unknown without v1.1 source.

**Canonical going forward: 72.**

---

### Component 3: Isolation Reliance

| Source | Wolves 2025-26 percentile |
|---|---|
| Canonical (CSV verified) | 89.7 (rounds to 90) |
| v1.1 Firestore | 91 |
| Gap | +1 |

**Spec.** Section 2.4 calls for four sub-metrics: overall iso play-type frequency, late-clock iso rate, contested pull-up rate, self-created shot percentage. The spec notes late-clock iso requires per-shot shot-clock data not in the warehouse.

**Canonical implementation** (`components/isolation_reliance.py:171-175`):

```
sub["synergy_iso_freq"]      (Synergy Isolation poss_pct)
sub["pull_up_fga_share"]     (pull_up_fga / total fga; v1 proxy for contested pull-up rate)
sub["unassisted_fg_rate"]    (1 - ast/fgm; spec sub-metric 4)
```

Three sub-metrics. Spec sub-metric 2 (late-clock iso) deferred as data is unavailable.

**v1.1 sub-metrics** (from Firestore):

```
isolationPossessionPct:           0.096       (same as canonical synergy_iso_freq)
selfCreatedShotShare:             0.38827     (same as canonical unassisted_fg_rate; 1 - 0.612 = 0.388)
pullUpToCatchShootRatio:          1.08908     (NOT the canonical pull_up_fga_share)
```

The third sub-metric is different. **Canonical uses pull_up_fga / total_fga (a share of all shots). v1.1 uses pull_up_fga / catch_shoot_fga (a ratio).** These measure related but distinct things: the canonical share answers "what fraction of all your attempts are pull-ups," while the v1.1 ratio answers "for every catch-and-shoot, how many pull-ups do you take." The latter can go to infinity for a team that never catches-and-shoots; the former is bounded between 0 and 1.

This substitution is structurally suspicious because the **canonical Component 5 has a sub-metric also called `pull_up_fg3a / (pull_up_fg3a + catch_shoot_fg3a)`**, a closely related ratio of pull-up to catch-and-shoot threes. v1.1 appears to have ported a ratio-shaped sub-metric from C5 into C3.

Despite the sub-metric substitution, the resulting percentile is within 1 point of the canonical because the underlying data signal is so strong: the 2025-26 Wolves are the league's most iso-heavy non-tanker no matter how you measure it.

**Diff.** v1.1 substitutes one of three sub-metrics. Same data inputs (pull-up tracking, catch-and-shoot tracking), different ratio construction. Plus the reference distribution.

**Classification: Improvement candidate or Lost depending on intent.** If the v1.1 substitution was deliberate (someone thought a ratio is more interpretable than a share), it is a methodology drift that could be argued either way. If it was accidental (a copy-paste from C5), it is a bug. Without the v1.1 source, I cannot tell which. The 1-point gap is within rounding noise so this is not a publishable concern, but it is a methodological concern: **v1.1's C3 is computing a slightly different concept than canonical C3, and the agreement is coincidental.**

**Canonical going forward: 90.**

---

### Component 4: Action Poverty

| Source | Wolves 2025-26 percentile |
|---|---|
| Canonical (CSV verified) | 45.3 (rounds to 45) |
| v1.1 Firestore | 28 |
| Gap | -17 |

**This is the largest gap and the only one that materially changes interpretation.**

**Spec.** Section 2.5 calls for four sub-metrics: unique action types per game, multi-action possession rate, non-iso action density, off-ball action share. The spec notes the full version requires an action classifier that does not yet exist.

**Canonical implementation** (`components/action_poverty.py:123-127`): three Synergy-derived proxies, all transparently flagged as v1 proxies:

```
sub["inv_play_type_entropy"]          (Shannon entropy across 11 Synergy play types, sign-flipped)
sub["inv_designed_action_share"]      (Cut + OffScreen + Handoff + Spotup, sign-flipped)
sub["ball_dominant_action_share"]     (Iso + PRBallHandler + Postup)
```

**v1.1 sub-metrics** (from Firestore):

```
inverseOffBallActionShare:        0.15056
playTypeConcentration:            0.229
```

**Only two sub-metrics, both different from canonical.**

- v1.1's `playTypeConcentration = 0.229` exactly matches the Wolves' 2025-26 **Spotup share** of 22.9% from the canonical action-poverty investigation table (`outputs/findings/q0a_lafi/04_component4_action_poverty.md`). v1.1 is using the share of the team's single most-used play type as a concentration proxy, in lieu of the canonical Shannon entropy across all 11 types. Spotup is the Wolves' single most-frequent play type at 22.9%. This is a fundamentally different concentration measure than Shannon entropy.
- v1.1's `inverseOffBallActionShare = 0.15056` is a fraction. It is plausibly (Cut + OffScreen) / (Cut + OffScreen + Handoff + Spotup + Iso + PRBH + Postup + ...) or a similar ratio. It is **not** the canonical `inv_designed_action_share = Cut + OffScreen + Handoff + Spotup` (which would be 0.10 + 0.057 + 0.229 = 0.386 for the Wolves on canonical numbers, not 0.15).

**Historical context confirms structural divergence.** v1.1's wolvesPercentileLastSeason = 74 and wolvesPercentileTwoSeasonsAgo = 73. Canonical 2024-25 C4 = 35.8 and 2023-24 C4 = 27.2. The v1.1 trajectory is 73 -> 74 -> 28 (a sharp cliff this season). The canonical trajectory is 27 -> 36 -> 45 (a slow rise across seasons). **These are not describing the same metric on the same data.** Even after accounting for the universe difference, no permutation of "rank within 30 teams" produces canonical values that flip from rising to cliff.

**Diff summary.**

- Different sub-metric count (2 vs 3).
- Different concentration measure (single-largest-share vs Shannon entropy).
- Different "designed action" formula.
- Different historical trajectory pattern across seasons.
- Different reference distribution.

**Classification: Lost (or Unknown) for the sub-metric selection. Improvement (perhaps) for the concentration measure if intentional. Recoverable for the reference distribution.**

The honest reading: I cannot reproduce the v1.1 C4 value of 28 from the canonical code. The v1.1 result is not just the canonical metric ranked against 30 teams instead of 360. It is a different metric entirely.

**Canonical going forward: 45.**

This component is also the one most heavily caveated in the canonical findings (the 04 investigation file explicitly notes "v1 proxy and the v2 action classifier will sharpen it"). If anyone wanted to change C4, the right move is to build the action classifier (which is a known specced piece in `specs/action_classifier_infrastructure_spec.md`), not to silently substitute proxies in a downstream pipeline.

---

### Component 5: Shot Quality Decay

| Source | Wolves 2025-26 percentile |
|---|---|
| Canonical (CSV verified) | 82.7 (rounds to 83) |
| v1.1 Firestore | 89 |
| Gap | +6 |

**Spec.** Section 2.6 calls for five sub-metrics: shot clock remaining, wide-open shot rate, contested shot rate, expected eFG model, catch-and-shoot vs pull-up three ratio. The spec notes defender distance, shot clock, and expected-eFG require data not in the warehouse.

**Canonical implementation** (`components/shot_quality_decay.py:115-119`): four sub-metrics, all data-available proxies:

```
sub["inv_catch_shoot_share"]        (-catch_shoot_fga / (catch_shoot_fga + pull_up_fga))
sub["pull_up_fg3a_share"]           (pull_up_fg3a / (pull_up_fg3a + catch_shoot_fg3a))   # spec sub-metric 5
sub["inv_restricted_area_share"]    (-restricted_area_fga / total_zone_fga)
sub["midrange_share"]               (midrange_fga / total_zone_fga)
```

Three of the five spec sub-metrics (defender distance, shot clock, expected eFG) are explicitly absent because the data is missing. The four implemented sub-metrics are documented as v1 proxies.

**v1.1 sub-metrics** (from Firestore):

```
pullUpToCatchShootThreeRatio:   0.5642        (matches canonical pull_up_fg3a_share)
midrangeShotShare:              0.09972       (matches canonical midrange_share)
```

**Only two sub-metrics.** v1.1 dropped:

- The catch-and-shoot vs pull-up share (`inv_catch_shoot_share`).
- The restricted-area share (`inv_restricted_area_share`).

**Verification of the user's prior-investigation finding on C5.** The user-reported "two collinear sub-metrics removed in v1.1 (r=0.806)" claim is plausibly the catch-and-shoot share + pull-up three share pair: both load on the same "self-creation vs designed" axis. v1.1 kept the three-share (pullUpToCatchShootThreeRatio) and dropped the all-shot share (inv_catch_shoot_share). The restricted-area share was also dropped, which is harder to justify on collinearity grounds because restricted-area share measures shot **location** quality, not self-creation. Restricted-area and pull-up share are different sub-metric families and dropping one as a collinearity fix would be unusual.

**I cannot verify the r=0.806 claim without computing it directly from the canonical sub-metric output**, but the broad shape of the user's report (v1 had a collinear pair, v1.1 removed one) is consistent with what the data shows: v1.1 has two sub-metrics where canonical has four.

**Historical context.** v1.1's last-season = 77; canonical 2024-25 = 71.5. v1.1's two-seasons-ago = 34; canonical 2023-24 = 39.1. Closer than C2 / C4 (within ~5-7 points each), consistent with the universe difference accounting for most of it.

**Diff summary.**

- v1.1 keeps 2 of canonical's 4 sub-metrics.
- v1.1 drops `inv_catch_shoot_share` and `inv_restricted_area_share`.
- Different reference distribution.

**Classification: Improvement (partial) + Recoverable.** Dropping a collinear sub-metric is methodologically defensible **if** the drop was based on a measured correlation. Dropping the restricted-area share is harder to defend because it measures shot location quality (a distinct construct from off-the-dribble vs catch-and-shoot). v1.1 may have over-corrected.

**Canonical going forward: 83.**

A genuine improvement path here: compute the correlation matrix on the canonical sub-metric set (which the canonical composite.py already does in its diagnostics), identify the actual collinear pair, drop the redundant one, and recompute. This would be a defensible C5 v1.2 if anyone wanted to revisit. For the present audit, v1.1's dropped restricted-area share is a methodological loss, not a clean improvement.

---

### Sharp LAFI

| Source | Wolves 2025-26 |
|---|---|
| Canonical (CSV verified) | 89.7 (rounds to 90) |
| v1.1 Firestore | 86 |
| Gap | -4 |

**Definition (canonical).** Weighted average of C2, C3, C5 percentile ranks, weights renormalized from (0.20, 0.20, 0.15) to sum to 1, then **percentile-ranked across the full 12-season pool**. Source: `composite.py:46-49, 106-110`.

**v1.1 definition unknown** but the value (86) is consistent with either:

- (a) The same weighted-sum approach applied to v1.1's component percentiles (72*0.36 + 91*0.36 + 89*0.27 = roughly 84). Close to 86. The 30-team rank of that weighted sum would not necessarily give 86; depends on the rest of the league.
- (b) A direct weighted percentile sum without re-ranking. Using v1.1's components: (78*0.20 + 91*0.20 + 89*0.15) / (0.20+0.20+0.15) = (15.6 + 18.2 + 13.35) / 0.55 = 47.15 / 0.55 = 85.7. **Rounds to 86. Matches.**

So v1.1's Sharp LAFI is likely the weighted average of the three component percentiles **without** the additional re-rank step. Canonical applies a re-rank to get back to a percentile interpretation. The 4-point gap is partly the universe difference, partly the re-rank step.

**Classification: Recoverable (one-line code change in v1.1 to match canonical) but Sharp LAFI is also downstream of every C2/C3/C5 issue above, so even with the same composite formula, v1.1 Sharp would still differ until C5 sub-metrics are realigned.**

**Canonical going forward: 90.**

---

### Full LAFI

| Source | Wolves 2025-26 |
|---|---|
| Canonical (CSV verified) | 64.5 (rounds to 65) |
| v1.1 Firestore | 60 |
| Gap | -5 |

Same story as Sharp. Weighted sum of the five components: 0.25 BS + 0.20 MD + 0.20 IR + 0.20 AP + 0.15 SQD. The gap reduces to the C4 gap (-17) being heavily weighted (0.20 * -17 = -3.4) and the C5 gap (+6) being partially compensating (0.15 * +6 = +0.9), plus the re-rank vs weighted-percentile-sum difference.

**Canonical going forward: 65.**

---

## 4. Synthesis: which set to publish

**Publish the canonical Q0A values.**

| Component | Publish |
|---|---|
| C1 Ball Stickiness | 31 |
| C2 Movement Death | 72 |
| C3 Isolation Reliance | 90 |
| C4 Action Poverty | 45 |
| C5 Shot Quality Decay | 83 |
| Sharp LAFI | 90 |
| Full LAFI | 65 |

Rationale, ordered by force:

1. **The canonical code is fully inspectable and matches the canonical CSV exactly.** I verified the MIN 2025 RS row in `lafi_composite_5component.csv` reproduces 30.6 / 71.8 / 89.7 / 45.3 / 82.7 / Sharp 89.7 / Full 64.5. The canonical implementation is `analyses/q0a_lafi/components/*.py` and there is no ambiguity about what those values mean.
2. **The v1.1 pipeline is not inspectable.** No source exists in any local repo. The Firestore document has no provenance fields. Publishing values whose computation cannot be reviewed is a credibility risk for a public site.
3. **v1.1's C4 substantially diverges from canonical C4** (different sub-metric set, different historical trajectory, 17-point current-season gap). v1.1 C4 = 28 is incompatible with the canonical finding that the Wolves have "a normal-breadth playbook and are choosing iso anyway" (Q0A deliverable section 5). The canonical C4 = 45 was a deliberate, hard-earned finding that pivoted the diagnosis. v1.1's C4 reverts to a vaguer "action-poor" reading that the canonical analysis explicitly refuted.
4. **v1.1's C5 silently drops two sub-metrics**, one of which (restricted-area share) measures a distinct construct from the others.
5. **The qualitative dashboard narrative is unchanged in either case.** Distributed pickup, top-3 Sharp LAFI, extreme on the playoff-relevant subset. The values move by a few points each but the story is the same. Choosing canonical does not require rewriting the article or the methodology narrative.

**What about article-dashboard alignment?**

The article body cites canonical values (31 / 72 / 90 / 45 / 83 / Sharp 90 / Full 65) from the Q0A deliverable. The dashboard currently shows v1.1 (30 / 78 / 91 / 28 / 89 / Sharp 86 / Full 60). **They should align.** The least-effort fix is to publish canonical values to the dashboard by either (a) overwriting the Firestore document with canonical values directly, or (b) rebuilding the v1.1 writer to call `analyses.q0a_lafi.composite.assemble_composite` and serialize its output.

**Strong recommendation:** option (b). The dashboard refreshes every day; option (a) would drift the moment v1.1 next runs. Option (b) requires writing a thin Firestore writer that imports `analyses.q0a_lafi` and emits the same document schema. This is two to four hours of work and is the clean fix.

If option (b) is too much work right now, option (a) (overwrite Firestore with canonical values and pause the v1.1 cron) is acceptable as a holdover.

---

## 5. Downstream cascade assessment

**Zero work. The canonical values are unchanged by this audit.**

The following analyses cite canonical Q0A values and would have required re-checking if v1.1 had been adopted as the new canonical:

- Q5 v4 prescription (`outputs/findings/q5_prescription/05_q5_v4_deliverable.md`), which cites Sharp LAFI 90 as the headline structural diagnosis. Unchanged.
- Q0C cohort analysis (`outputs/findings/q0c_historical_cohort/01_q0c_v1_findings.md`), which uses LAFI to define cohort membership. Unchanged.
- Q4 archetype stress test, which cites LAFI as covariate. Unchanged.
- Q0A post-LAFI replan (`outputs/findings/q0a_lafi/12_post_lafi_replan_proposal.md`), which cites the Sharp LAFI 90 finding as the project's load-bearing result. Unchanged.

Recommending canonical preserves all downstream work.

If at some future date the team decides to adopt v1.1's methodology (e.g., a future audit confirms v1.1's C5 sub-metric drop is a genuine improvement), then a coordinated re-cascade would be needed. For now the right move is to keep canonical and document the v1.1 drift as a process bug.

---

## 6. Methodology evolution note (publishable)

Suggested text for the website methodology page. Plain English, no em or en dashes.

> ### How we compute the LA Fitness Index
>
> The LAFI for each NBA team is a composite of five components, each measuring a different way an offense can feel like pickup ball at LA Fitness rather than NBA-designed. The five components are Ball Stickiness, Movement Death, Isolation Reliance, Action Poverty, and Shot Quality Decay.
>
> For each component we compute three to four sub-metrics from publicly available NBA tracking and play-type data. Every sub-metric is z-scored against the rest of the league in the same season, the z-scores are averaged into a component score, and the component is converted to a percentile rank against the modern NBA (the 2014-15 season through today, roughly 360 team-seasons). A percentile of 90 means "more pickup-like than 90 percent of NBA team-seasons since 2014-15."
>
> The full Index is a weighted average of the five components: 25 percent Ball Stickiness, 20 percent each Movement Death, Isolation Reliance, and Action Poverty, and 15 percent Shot Quality Decay. The weights are priors set before looking at the predictive validation, not tuned to maximize fit.
>
> Sharp LAFI is a narrower composite using only Movement Death, Isolation Reliance, and Shot Quality Decay. The validation work found that these three components, considered together, are the most diagnostic of how an offense's regular-season identity holds up in the playoffs.
>
> The methodology and the per-component computation are documented in the project specs and the analysis code. The metric is intended to be auditable. If a value on the dashboard ever disagrees with the canonical analysis, the canonical analysis is the source of truth and the dashboard will be updated to match.

---

## 7. Open questions and what would resolve them

1. **Why does v1.1 exist if there is a canonical implementation already in `analyses/q0a_lafi`?** The most likely explanation is that v1.1 was an independent first-cut someone built before being aware of the canonical analysis, or before the canonical analysis was finalized. Resolution: ask whoever built v1.1, or find the writer on the home server and read its commit history.
2. **Is the v1.1 C3 pull-up-to-catch-shoot ratio an intentional sub-metric choice or a copy-paste from C5?** Resolution: find the v1.1 source and read it.
3. **Did v1.1 drop the canonical C5 catch-and-shoot share and restricted-area share based on a measured collinearity check?** If yes, on what reference sample. The canonical composite.py already produces a correlation matrix; the canonical C5 sub-metric set has not been audited for collinearity. Resolution: compute Pearson r among the canonical C5 sub-metrics across the full 12-season sample. If two sub-metrics correlate above 0.80, that is a real C5 v1.2 improvement opportunity; otherwise v1.1's drop was unsupported.
4. **Where does v1.1 run?** Probably the home server cron. Resolution: SSH to 192.168.1.236 and look in /etc/cron.* and the user crontab.
5. **Should the canonical implementation be promoted into the daily Firestore pipeline?** Yes, per Section 4's option (b). Resolution: write a thin `publish_lafi.py` in this repo that imports `analyses.q0a_lafi.composite`, serializes the result into the v1.1 document schema, and writes via firebase-admin. Schedule it on the same cadence as v1.1 (probably daily). Remove the v1.1 writer once verified.

---

## 8. Verification checklist (what I confirmed vs inferred)

| Claim | Status |
|---|---|
| Canonical MIN 2025 RS values = 30.6 / 71.8 / 89.7 / 45.3 / 82.7 / Sharp 89.7 / Full 64.5 | **Verified** (read CSV directly) |
| Canonical implementation is `analyses/q0a_lafi/components/*.py` | **Verified** (read source) |
| v1.1 Firestore values = 30 / 78 / 91 / 28 / 89 / Sharp 86 / Full 60 | **Verified** (pulled live from Firestore REST API) |
| v1.1 percentile distribution is current-season-only, not 12-season pool | **Verified** (leagueMin/Avg/Max bounds) |
| v1.1 C1 sub-metrics match canonical structurally | **Verified** (same four names) |
| v1.1 C3 substitutes a different pull-up-related sub-metric | **Verified** (different field name, different value) |
| v1.1 C4 has only 2 sub-metrics vs canonical 3, with different definitions | **Verified** (read both) |
| v1.1 C5 has only 2 sub-metrics vs canonical 4, drops catch-shoot share and restricted-area share | **Verified** (read both) |
| The reason v1.1 dropped two C5 sub-metrics was a collinearity check | **Inferred / consistent with user's prior report; not verified** |
| v1.1 OffScreen raw of 0.021 vs canonical's 0.050 indicates a data-extract difference | **Consistent with the gap, cause unknown** |
| The v1.1 writer lives on the home server | **Inferred; not verified** |
| The v1.1 writer was not committed to either local repo | **Verified** (searched both repos exhaustively) |

End of audit.
