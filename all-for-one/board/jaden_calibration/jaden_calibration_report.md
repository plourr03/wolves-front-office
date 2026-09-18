# Jaden Markers: Calibration Class

> **EXPOSED, NOT YET RECOMPUTED (D88).** JD-COVER and any PAIR-DRTG marker here is built on `points_against` from the fit engine's forked stint builder, which credits about 3.4% of points to the wrong team. The upstream library is fixed as of 2026-09-18; the fork is hash-pinned and was deliberately left alone, so this panel still carries the defect. Small on/off windows are where it bites hardest. Detail: `postmortem/outputs/findings/lineup_pipeline/03_d88_points_fix_and_recompute.md`.

Board_spec v2.0 / `jaden_markers.md` section 5. Produced 2026-07-17, in the slot after the tripwire Phase 4 stop. Scoped with the same extraction discipline as tripwire Scenario A (`build_reference_class.py`): arrivals foundation from game-level data, diacritic-safe, join on `nba_player_id` only, seed validation, curated log. Freezes NOTHING. Every threshold below is labelled PROPOSED / TUNE. No p-values; exact counts throughout. Descriptive, not causal.

**Read section 2b first.** This analysis was adversarially verified, and the verification found a real population-validity problem: the class was built with a position-only filter, dropping the "wing *known for defense*" criterion, so roughly half the 38 members are offense-first scorers rather than stoppers. Section 2b re-does the calibration on a defense-screened subset that matches Jaden's 3-and-D archetype, and it is the headline; the full-38 sections 4-5 are retained as the robustness comparison. The screened recompute also surfaced a deeper point the full-class analysis missed (2b): the JO-EFF "leap" band is a usage-compression artifact even after screening, so JO-GROWTH, not JO-EFF, is the load-bearing distinguisher of a real leap.

Scripts: `scripts/build_calibration_class.py`, `scripts/compute_markers.py`, `scripts/compute_jd_cover.py`, `scripts/propose_thresholds.py`. Data: `data/calibration_class.parquet`, `data/marker_movements.parquet`, `data/jd_cover.parquet`, `data/threshold_proposals.json`, `data/calibration_class_curation_log.md`.

## 1. What this calibrates and why

Jaden McDaniels is a two-way wing already on the Wolves, and the team added a high-usage creator (LaMelo). The calibration class is the historical analog: a two-way wing who arrived at a team that already fielded an established high-usage star creator, measured by how the wing's OWN per-opportunity markers moved from a BEFORE baseline (his last full starter season without that creator) to an AFTER state (his first full starter season with the creator). We use that movement distribution to propose where the leap / flat / decline bands sit on the offensive ladder and where pass/fail sits on the defensive gate. The class is small and confounded, so these are calibration priors, not verdicts.

## 2. The class

Definition (all query-derived, no hand-adds):
- Arriving wing: `nba_player_bio.position` in {Forward, Guard-Forward, Forward-Guard}. "Known for defense" is NOT separately enforced (the warehouse has no clean defense-archetype filter that is non-circular with the JD markers); this is a stated limitation, so a few members are offense-first forwards rather than pure stoppers.
- Star high-usage creator on the new team: a teammate with `usg_pct >= 0.28` (fraction, prior OR current season) AND a real season (`gp >= 40`) AND an All-Star or All-NBA selection in {arr_ss-1, arr_ss} (`honors.parquet`). The honors requirement is what keeps the class from ballooning; it removes small-sample high-usage non-stars (James Wiseman at 0.455 in 4 games, Tristen Newton, and the like) and encodes "established STAR creator" from the framing.
- Starter role, era-robust: BEFORE and AFTER both at least 24.0 mpg over at least 40 games (keeps the shortened 2019-20 and 2020-21 seasons in play instead of penalizing them on raw-minute floors).
- Secondary-in-the-pairing screen: the wing's AFTER usage is below the creator's AND below 0.27, so the wing is not the primary creator alongside the star. No cap on the wing's PRIOR usage, because Mikal Bridges was a #1 option at Brooklyn and must stay in-class.
- Window: arrivals `arr_ss` in 2018 through 2025 (2018-19 through 2025-26). Bounded below by matchup coverage, which begins **2016-17** in the warehouse (verified; the feasibility doc's "2017-18+" was conservative), since BEFORE = arr_ss-1 must have matchup data for JD-LOAD / JD-HOLD. The 2018 floor is therefore comfortably inside coverage, not at its edge.
- BEFORE / AFTER rule: offseason arrival, BEFORE = arr_ss-1, AFTER = arr_ss. Midseason arrival, BEFORE = arr_ss-1 (last full season, prior team), AFTER = arr_ss+1 (first FULL season with the creator; the partial arrival season is skipped).

Class size:
- 90 wing-arrivals-next-to-a-star pass the structural screen (starter BEFORE + star creator + secondary role where checkable).
- 38 are MARKER-USABLE (both BEFORE and AFTER are real starter seasons with data). These 38 pairings span 31 distinct players; 7 wings appear for two different star-pairings (for example Robert Covington, once to KAT's Minnesota and once to Lillard's Portland). The 38 are the calibration set.
- The remaining 52 structural members lack a computable AFTER: a 2025-26 (future/absent) AFTER season, or fewer than 40 games / a non-secondary role at the new team. They are enumerated in `data/calibration_class_curation_log.md`.

This is larger than the loose "~10-20 like Scenario A" the ruling anticipated. The reason is honest and structural: a wing changing teams into a starter role next to a star is simply more common than Scenario A's high-usage lead-guard-plus-incumbent-star event. I did not force it smaller with an arbitrary defense proxy; a larger, objective class gives more stable distributions and I flag the archetype heterogeneity instead.

### Seed validation (all three IN, with margin)

| Seed | Path | Creator | BEFORE | AFTER | In class |
|---|---|---|---|---|---|
| Aaron Gordon | ORL -> DEN, Mar 2021 (midseason) | Nikola Jokic (usg 0.293) | 2019-20, 32.0 mpg | 2021-22, 31.2 mpg | YES, marker-usable |
| Mikal Bridges | BKN -> NYK, 2024-25 (offseason) | Jalen Brunson (usg 0.311) | 2023-24, 34.3 mpg | 2024-25, 37.0 mpg | YES, marker-usable |
| OG Anunoby | TOR -> NYK, Dec 2023 (midseason) | Jalen Brunson (usg 0.311) | 2022-23, 35.2 mpg | 2024-25, 36.1 mpg | YES, marker-usable |

No seed required a hand-add or a logged exclusion. Anunoby's AFTER is 2024-25 (his first FULL season with Brunson), since 2023-24 was the partial midseason-arrival year, which is exactly the BEFORE/AFTER rule working as intended.

## 2b. Defense-screened calibration (the headline; post-verification fix)

Script: `scripts/defense_screen.py`, output `data/threshold_proposals_screened.json`.

**The screen.** A non-circular defensive filter: the wing was already a primary perimeter defender BEFORE the pairing, `jd_load_before >= class median (0.191)`. This uses BEFORE deployment (not the AFTER markers being calibrated), and it matches Jaden, who is a high-defensive-load perimeter stopper. **Full class 38 -> defense-screened 19.**

**A finding the verification's own suggestion got wrong, and it matters.** The screen does NOT keep all three seeds. It keeps **Bridges (0.297) and Anunoby (0.312)** but **drops Aaron Gordon (0.182, just below the 0.191 median)**. That is not a defect; it is informative. Gordon at Orlando was a versatile forward who guarded up a position, not a point-of-attack perimeter stopper, so his defensive-load archetype is a step away from Jaden's. **Bridges and Anunoby are the closer 3-and-D comps for Jaden, and they survive the screen; Gordon, the canonical *offensive* success, does not.** For calibrating Jaden specifically, that is the right sorting, and it is worth stating plainly rather than papering over.

**The screened thresholds move materially** (headline; full-38 in parentheses for contrast):

| Band | Screened (n=19) | Full-38 |
|---|---|---|
| JO-EFF LEAP: ts_after_vs_trail3 >= | **+0.019** | +0.027 |
| JO-EFF LEAP: d(ts_vs_league) >= | **+0.021** | +0.027 |
| JO-EFF DECLINE: <= | **-0.015** | -0.010 |
| JD-HOLD strong-pass: <= | **-0.124** | -0.100 |
| JD-LOAD pass: after-share >= | **0.200** | 0.188 |

The screened class holds primaries below baseline 16 of 19 (vs 27 of 38), and its JD-HOLD is deeper (median -0.080 vs -0.044): genuine defenders suppress harder, as expected, which tightens the strong-pass bar.

**The deeper finding, and the actual recommendation.** Even after the defensive screen, the JO-EFF leap band (4 of 19) is Harrison Barnes, Kevin Huerter, Kyle Kuzma, Taurean Prince, still offense-first scorers who lifted true shooting by *cutting usage* next to the star, not by a two-way skill jump. This is because a TS rise next to a high-usage creator is mechanically the usage-compression effect (fewer, easier shots), and it happens to scorers regardless of whether they defend. **So JO-EFF alone cannot define a leap; screening the population does not fix that, only the JO-GROWTH rungs can.** The recommendation to the board: LEAP should require a JO-GROWTH rung (real self-created-efficiency, free-throw-rate, or three-point volume-and-accuracy expansion), and JO-EFF should be read as necessary-not-sufficient, because on this evidence a bare TS rise is gravity, not growth. The defensive gate calibrates cleanly on the screened class (JD-LOAD conserved, JD-HOLD deeper); JD-COVER stays de-weighted (section 5). This point is the calibration's real yield, and it only appeared once the class was screened.

## 3. Markers: computable now vs panel-dependent

| Marker | Source | Status |
|---|---|---|
| JO-EFF | `nba_player_season_bio.ts_pct` + league mean + own trailing-3 | COMPUTED, 38/38 |
| JO-FLOOR | `nba_player_stats` (fga, fta) + `nba_player_advanced_stats.possessions` | COMPUTED, 38/38 |
| JO-GROWTH (a) self-created | `nba_player_tracking_season` PullUpShot + Drives | COMPUTED, 38/38 |
| JO-GROWTH (b) FT rate | `nba_player_stats` FTA/FGA | COMPUTED, 38/38 |
| JO-GROWTH (c) 3P vol + acc | `nba_player_stats` fg3a/g, fg3_pct | COMPUTED, 38/38 |
| JD-LOAD | `nba_boxscore_matchups` partial_possessions | COMPUTED, 38/38 |
| JD-HOLD | `nba_boxscore_matchups` player_points / partial_possessions vs opponent baseline | COMPUTED, 38/38 |
| JD-COVER | fitengine stint panel (points_against / possessions_def in creator minutes, wing on/off) | COMPUTED for 34/38; 4 PANEL-PENDING |

Nothing was struck as uncomputable. JD-COVER is stint/lineup-dependent; the panel (`tripwire-backtest/data/stints_panel/`, RS 2014-15 through 2024-25) was readily usable, so rather than defer the whole marker I computed it for every member whose AFTER season is 2024-25 or earlier. The 4 members with a 2025-26 AFTER (De'Andre Hunter -> CLE, Kyle Kuzma -> MIL, Cameron Johnson -> DEN, Tim Hardaway Jr. -> DEN) fall outside the built panel and are reported as panel-pending, not faked. The board's literal JD-COVER read for LaMelo-plus-Jaden is itself a 2026-27 in-season computation once the pair shares a floor.

## 4. Movement distributions (n = 38 unless noted)

All deltas are AFTER minus BEFORE. Efficiency figures are fractions (TS, FG%, eFG%). "trail3" is the wing's true-shooting mean over his three seasons ending in BEFORE.

### Offensive ladder

JO-EFF (true shooting, the climb):

| Measure | mean | median | sd | q25 | q75 | range |
|---|---|---|---|---|---|---|
| TS delta (after-before) | +0.004 | +0.001 | 0.035 | -0.010 | +0.028 | -0.078 to +0.086 |
| d(TS vs league) | -0.000 | +0.005 | 0.036 | -0.016 | +0.027 | -0.085 to +0.084 |
| TS(after) vs own trail3 | +0.008 | +0.004 | 0.032 | -0.010 | +0.027 | -0.057 to +0.075 |

The center of the class is flat: the median wing gains almost no true shooting from joining a star creator. The gains are in the right tail, and Aaron Gordon owns the max (+0.086 TS, +0.074 vs his trailing-3), which is why he is the canonical success. Among the seeds only Gordon is a true efficiency leap; Bridges (+0.025 TS, -0.006 vs trail3) and Anunoby (+0.005, +0.011) are flat-band, both because they were already efficient.

JO-FLOOR (scoring attempts per 75 possessions, anti-vanishing):

| Measure | mean | median | q25 | q75 | range |
|---|---|---|---|---|---|
| sa75 percent change | -5.3% | -5.0% | -16.5% | +5.2% | -46.7% to +32.7% |

Volume drops modestly on average when a wing joins a creator, but the spread is large. 12 of 38 dropped more than 15 percent; 7 of 38 more than 20 percent. Bridges is the textbook case of a real usage cut (-18.7 percent, breaking a 15-percent floor). Gordon (-7.9 percent) and Anunoby (+4.1 percent) keep their floor.

JO-GROWTH (three rungs; a true leap needs at least one):

| Rung | Definition (real-margin, TUNE) | Class count |
|---|---|---|
| (a) self-created efficiency rising | pull-up eFG% OR drive FG% up by >= +0.010 | 20 / 38 |
| (b) free-throw rate rising | FTA/FGA up by >= +0.010 | 14 / 38 |
| (c) 3P volume AND accuracy both rising | fg3a/g up AND fg3_pct up | 6 / 38 |
| at least one rung | | 27 / 38 |

Component deltas for reference: pull-up eFG% median -0.021, drive FG% median -0.014, FT-rate median -0.011, fg3a/g median -0.30, fg3_pct median -0.010. Self-creation and shooting generally DRIFT DOWN in the class median (role compression next to a ball-dominant star), which is exactly why a rising signal is meaningful. All three seeds clear rung (a); Anunoby also clears rung (b). Rung (c), both 3P volume and accuracy up together, is rare (6 of 38) and is the strongest single tell of a real offensive expansion rather than gravity-fed catch-and-shoot.

### Defensive gate

JD-LOAD (share of the wing's defensive partial-possessions spent on primary perimeter creators, opponent usg >= 0.25 and a perimeter position):

| Measure | mean | median | q25 | q75 | range |
|---|---|---|---|---|---|
| share BEFORE | 0.198 | 0.191 | 0.156 | 0.250 | 0.066 to 0.328 |
| share AFTER | 0.191 | 0.188 | 0.136 | 0.243 | 0.064 to 0.320 |
| delta | -0.007 | -0.008 | -0.058 | +0.041 | -0.127 to +0.137 |

Deployment is roughly conserved across the move (median delta near zero). The seeds sit at the top of the class in the AFTER state: Gordon 0.319, Bridges 0.320, Anunoby 0.254, all at or above the class 75th percentile, consistent with becoming the primary perimeter stopper next to a star who does not defend the point of attack.

JD-HOLD (possession-weighted mean of points allowed per possession by the wing minus the opponent's own season baseline computed excluding the wing, over primary-option opponents guarded >= 20 partial-possessions; negative = suppression):

| Measure | mean | median | q25 | q75 | range |
|---|---|---|---|---|---|
| BEFORE | -0.054 | -0.077 | -0.112 | -0.042 | -0.171 to +0.344 |
| AFTER | -0.031 | -0.044 | -0.100 | +0.004 | -0.159 to +0.329 |
| delta | +0.024 | +0.014 | -0.015 | +0.070 | -0.124 to +0.208 |

27 of 38 hold primary options below their baselines in the AFTER state. Suppression weakens slightly on average after the move (delta +0.024, opponents score a touch more relative to baseline), plausibly because the wing inherits tougher assignments on the better team, but the class stays net-suppressive. All three seeds pass and pass strongly (Gordon -0.141, Bridges -0.131, Anunoby -0.080).

JD-COVER (team defensive rating in the creator's minutes, wing on-off = DRTG_on minus DRTG_off; negative = the wing improves team defense in the star's minutes; n = 34):

| Measure | mean | median | sd | q25 | q75 | range |
|---|---|---|---|---|---|---|
| on-off (per 100) | +0.55 | +0.90 | 3.14 | -1.49 | +2.50 | -7.54 to +6.86 |

This is the important calibration result. The distribution centers near zero and is slightly positive (team defense is, on average, not better in the star's minutes with the wing on than off). Only 4 of 34 historical wings cleared the draft threshold of 3.0-per-100-better (on-off <= -3.0); 13 of 34 were merely any-better. The reason is a genuine confound the spec already flags: on-off in a fixed star's minutes is dominated by WHO replaces the wing, and star lineups skew to specific defenders and game states. Among the seeds, Anunoby is best at -2.12 (improves NYK defense in Brunson minutes) but still does not clear -3.0; Gordon (+1.96) and Bridges (+1.11) are on the wrong side of zero. Possession support is healthy (median wing-OFF sample in star minutes is 1,489 possessions; minimum 306), so the noise is structural, not sample-size.

## 5. Proposed thresholds (all TUNE, frozen NOTHING) -- FULL-38 (robustness)

These are the full-38 thresholds. The **headline, archetype-matched thresholds are the defense-screened ones in section 2b**; these full-38 numbers are retained for the robustness comparison and are calibrated on the archetype-heterogeneous class, so read them as the looser, contaminated reference. The offensive bands in particular sit wider here because the leap band is populated by offense-first usage-cutters (see 2b).

### Offensive ladder bands

JO-EFF, leap / flat / decline, derived from the class quartiles of the two climb measures the spec names (clears BOTH the league and the own trailing-3 baseline):
- LEAP band: TS(after) vs trail3 >= +0.027 AND d(TS vs league) >= +0.027 (about the class 75th percentile on both). 8 of 38 pairings clear it, including Aaron Gordon; the others are Carmelo Anthony, Harrison Barnes, Jerami Grant, Kevin Huerter, Kyle Kuzma, Marcus Morris Sr., Tim Hardaway Jr.
- FLAT band: TS(after) vs trail3 between -0.010 and +0.027.
- DECLINE band: TS(after) vs trail3 <= -0.010 (about the class 25th percentile).

JO-FLOOR: cap the offensive axis at NOT-LEAP if sa75 falls more than 15 percent below the trailing baseline. The spec's -15 percent draft holds up against the class (median move only -5 percent, so -15 percent is a real break, not normal variation); it trips 12 of 38. A -20 percent alternative trips 7 of 38 if a looser floor is preferred.

JO-GROWTH: keep "at least one of the three rungs," with the real-margin definitions above (self-created efficiency or FT rate up by at least +0.010, or 3P volume and accuracy both up). This fires for 27 of 38 in the class, which is appropriately permissive as one necessary-but-not-sufficient condition inside the LEAP definition (LEAP still also needs the gate passed, JO-EFF in the leap band, and JO-FLOOR intact).

### Defensive gate (pass/fail)

JD-LOAD (deployment): PROPOSED pass at after-share >= 0.188 (class median). This is a stand-in for the board's real test, which is "leads the roster" in matchup share against primary creators, a team-relative rank. That rank is computable from the same matchup table plus a roster join and should be added when the panel context is wired; the per-player share here calibrates the level.

JD-HOLD (suppression): PROPOSED pass at jd_hold_after < 0 (holds primary options below their own baselines), with a STRONG-pass marker at <= -0.100 (class 25th percentile). 27 of 38 pass; all three seeds pass, two of them strongly.

JD-COVER (the anchor claim): the draft 3.0-per-100 threshold is DEMANDING and should be softened or de-weighted. Only 4 of 34 calibration wings cleared it and the metric is confounded by lineup replacement, so I propose treating JD-COVER as SUPPORTING evidence (sign and a possession floor, TUNE, suggest at least ~300 wing-off possessions in star minutes before reading it) rather than a hard gate, and leaning the gate on JD-LOAD plus JD-HOLD, which are per-opportunity and far less confounded. This is a recommendation to the board, not a rewrite of the marker.

Gate composite (unchanged from spec, restated): the gate fails only if JD-LOAD fails AND at least one of JD-COVER or JD-HOLD fails. If deployment drops but effectiveness holds, that reads STEADY with a REALLOCATED flag, not a fail.

## 6. What I computed vs flagged

- Computed now, warehouse-only, all 38 pairings: JO-EFF, JO-FLOOR, JO-GROWTH (all three rungs), JD-LOAD, JD-HOLD.
- Computed from the stint panel (readily usable), 34 of 38 pairings: JD-COVER. 4 members panel-pending because their AFTER is 2025-26, which the panel build (through 2024-25) does not yet cover; extend the panel by one season to close them.
- Struck / uncomputable: none.

## 7. Discipline and caveats

Descriptive, not causal. Every BEFORE-to-AFTER movement is confounded by age and development curve, by the mechanical efficiency lift that comes from a usage cut next to a ball-dominant star (lower usage tends to raise TS regardless of skill growth), by team scheme and shot diet, by health, and by the shortened / bubble 2019-20 and 2020-21 seasons that sit inside several BEFORE and AFTER windows. Do not read any single delta as "the creator caused this."

Selection and survivorship. The class conditions on wings who held a starter role in BOTH the before and after seasons, which tilts it toward pairings that worked. Wings who joined a star and lost their role are largely in the 52 non-marker-usable structural members, not in the 38. The distributions therefore describe successful-enough pairings and should be read as an optimistic reference, not a random sample.

Small-n and multiplicity. 38 pairings across 31 players; 7 players contribute two pairings each, so the observations are not fully independent. Bands drawn at the 25th and 75th percentiles move by a member or two under reasonable filter changes; treat the numbers as priors to tune, which is the whole point of leaving them unfrozen.

Archetype heterogeneity (the verification's headline; RESOLVED in section 2b). The positional wing filter admits both 3-and-D stoppers and offense-first forwards (Tobias Harris, Bogdanovic, Christian Wood, Carmelo, Kuzma, Hardaway, Fournier, Huerter), and "known for defense" is not separately enforced. This is not merely cosmetic: 7 of the 8 full-38 JO-EFF leap-band members are offense-first scorers, so the full-38 offensive thresholds are calibrated largely on the wrong archetype. Section 2b re-does the calibration on the defense-screened subset (n=19) and is the headline; the full-38 numbers here are the robustness comparison. The screened recompute lands the class at 19 (the "low-20s" this caveat predicted) and moves the thresholds materially.

Additional caveats the verification surfaced. (1) JD-LOAD's "primary perimeter creator" opponent flag admits plain position "Forward", so it is effectively "any high-usage non-center", slightly looser than the perimeter-creator intent; a guard-only flag would tighten it. (2) Midseason arrivals carry a two-season BEFORE->AFTER gap (Gordon 2019-20 -> 2021-22 skips the partial arrival year), which widens the age/development/health confound beyond the generic caveat for those specific members. (3) Checked and CLEARED: the known 2021-22 tracking corruption is Gobert-specific (Possessions/Passing rows), and does NOT affect the PullUpShot/Drives measures JO-GROWTH uses, so Gordon's 2021-22 AFTER self-creation is sound.

## 8. Appendix: per-member table

Columns: TS delta, TS(after) vs trail3, sa75 percent change, JO-GROWTH rungs satisfied (0-3), JD-LOAD share after, JD-HOLD after, JD-COVER on-off (blank = panel-pending). Sorted by TS delta.

See `data/marker_movements.parquet` and `data/jd_cover.parquet` for the full record. Seed rows: Aaron Gordon (TS +0.086, sa75 -7.9%, growth 1, load 0.319, hold -0.141, cover +1.96); Mikal Bridges (TS +0.025, sa75 -18.7%, growth 1, load 0.320, hold -0.131, cover +1.11); OG Anunoby (TS +0.005, sa75 +4.1%, growth 2, load 0.254, hold -0.080, cover -2.12).

## 9. Recommendation to the board

Adopt the offensive-ladder bands and the JD-LOAD / JD-HOLD gate thresholds above as PROPOSED priors for the October freeze, all tagged TUNE. Down-weight JD-COVER from a hard 3.0-per-100 gate to supporting evidence with a possession floor, on the calibration evidence that almost no historical two-way wing clears that bar and that the metric is lineup-confounded. Add the team-relative "leads the roster" JD-LOAD rank and extend the stint panel to 2025-26 to close the four panel-pending JD-COVER members before the season-end 2026-27 read that feeds the July 2027 extension node. Freeze nothing until the review.
