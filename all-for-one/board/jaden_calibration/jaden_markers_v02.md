# Jaden Markers v0.2: Residualized JO-EFF, the LEAP tier, and the Gordon reclass

A focused revision of `jaden_calibration_report.md` (v0.1), scoped to the defense-screened class (n=19) and the section-2b finding that a bare true-shooting climb next to a star is a usage-compression artifact, not a skill leap. This does five things Bobby's v0.2 directive asked for, all with real code run against the warehouse: (1) residualize JO-EFF against usage change, (2) test whether the fix still selects usage-cutters, (3) build a LEAP tier and its growth-signal sensitivity, (4) reclassify Aaron Gordon out of the calibration class into an appendix row, (5) note the JD-COVER 34/38 coverage.

Every threshold below is PROPOSED / TUNE. Freeze is 2026-10-20; this freezes NOTHING. No p-values. Exact counts throughout. Descriptive, not causal. n=19 is small and confounded (age, development, scheme, health, shortened 2019-20 / 2020-21 seasons, selection toward pairings that kept the wing a starter). Read every number as a prior to tune.

Scripts: `scripts/residualize_jo_eff.py` (new, v0.2), on top of v0.1's `scripts/defense_screen.py`, `scripts/compute_markers.py`, `scripts/compute_jd_cover.py`. Data written: `data/jo_eff_residuals.parquet`, `data/leap_tier_v02.json`. Joins are on `nba_player_id` only. `usg_pct` from `nba_player_season_bio` is a FRACTION.

## 0. The class this calibrates (unchanged from v0.1 section 2b)

The v0.2 CLASS is the DEFENSE-SCREENED subset: the 19 marker-usable wing-arrivals whose `jd_load_before >= class median 0.191`. The screen is non-circular (it uses BEFORE deployment, not the AFTER markers being calibrated) and it matches Jaden, a high-defensive-load perimeter stopper. Bridges (0.297) and Anunoby (0.312) survive and anchor the comp set. Gordon (0.182) sits just below the median and is OUT (see section 4). Full class 38 -> defense-screened 19.

## 1. Residualize JO-EFF against usage change

The section-2b claim is that a TS rise next to a ball-dominant creator is largely mechanical: fewer, easier shots (usage compression) lift efficiency without any skill jump. To separate gravity from growth, I pulled each of the 19 wings' `usg_pct` for `before_ss` and `after_ss` (max-gp stint per player-season, the same row `compute_markers.py` uses for `ts_after`, so usage and efficiency are measured on the same season-stint), formed `usg_delta = usg_after - usg_before`, and fit an OLS of the own-baseline efficiency climb on it:

```
ts_after_vs_trail3  =  +0.00167  +  (-0.15408) * usg_delta        (OLS, n=19)
```

| Quantity | Value |
|---|---|
| slope | **-0.15408** (per +1.00 usage fraction); **-0.00154** per +0.01 usage |
| intercept | **+0.00167** |
| R^2 | **0.0292** |
| residual SD (ddof=1) | **0.02826** (residual mean ~0 by construction) |

Read this carefully, because the fit itself is a finding. The slope is NEGATIVE, which is the usage-compression direction (cut usage, efficiency ticks up), so the mechanism is real and points the way section 2b said. But the slope is small and **R^2 is only 0.029**: across these 19 defenders, usage change explains about 3% of the cross-sectional variance in the own-baseline TS climb. The usage-compression story is directionally true but is NOT what drives most of the efficiency movement in the screened class. That nuance matters for step 2.

The residual is the efficiency climb IN EXCESS of what the usage change predicts:

```
jo_eff_residual  =  ts_after_vs_trail3  -  (+0.00167  -  0.15408 * usg_delta)
```

**PROPOSED residual leap band (TUNE):** `jo_eff_residual >= +1 SD (+0.0283)`. Because the OLS forces mean residual to ~0, "+1 SD" reads cleanly as "more than one standard deviation of unexplained efficiency gain." An alternative continuity threshold, `residual >= 75th pct (+0.0157)`, is reported alongside; it widens the band from 3 to 5 but yields the IDENTICAL LEAP set (section 3), so the tier is robust to this choice.

Residuals, sorted (growth-signal count from section 3 in the last column):

| Wing | before->after | creator | usg_delta | ts climb | pred from usg | **residual** | growth |
|---|---|---|---:|---:|---:|---:|---:|
| Kevin Huerter | 21->22 | De'Aaron Fox | +0.028 | +0.068 | -0.003 | **+0.0706** | 3 |
| Jae Crowder | 19->20 | Devin Booker | +0.000 | +0.035 | +0.002 | **+0.0337** | 1 |
| Harrison Barnes | 23->24 | Wembanyama | +0.003 | +0.034 | +0.001 | **+0.0328** | 1 |
| Taurean Prince | 23->24 | Giannis | -0.011 | +0.025 | +0.003 | +0.0213 | 0 |
| Kyle Kuzma | 23->25 | Giannis | -0.083 | +0.035 | +0.015 | +0.0205 | 2 |
| Robert Covington | 17->19 | Towns | +0.001 | +0.012 | +0.002 | +0.0108 | 2 |
| OG Anunoby | 22->24 | Brunson | +0.003 | +0.011 | +0.001 | +0.0098 | 2 |
| Bruce Brown | 21->22 | Jokic | +0.028 | +0.005 | -0.003 | +0.0080 | 1 |
| P.J. Tucker | 21->22 | Embiid | -0.050 | +0.012 | +0.009 | +0.0026 | 0 |
| Reggie Bullock Jr. | 20->21 | Doncic | -0.012 | +0.001 | +0.004 | -0.0025 | 0 |
| Garrett Temple | 19->20 | LaVine | -0.036 | -0.006 | +0.007 | -0.0129 | 1 |
| Kelly Oubre Jr. | 22->23 | Embiid | -0.037 | -0.006 | +0.007 | -0.0134 | 1 |
| Mikal Bridges | 23->24 | Brunson | -0.046 | -0.006 | +0.009 | -0.0151 | 1 |
| Tobias Harris | 23->24 | Cunningham | -0.030 | -0.010 | +0.006 | -0.0166 | 0 |
| Kelly Oubre Jr. | 19->20 | Curry | -0.004 | -0.019 | +0.002 | -0.0216 | 0 |
| De'Andre Hunter | 23->25 | Mitchell | +0.014 | -0.023 | -0.001 | -0.0228 | 0 |
| Garrett Temple | 18->19 | Irving | +0.031 | -0.028 | -0.003 | -0.0252 | 1 |
| Evan Fournier | 20->21 | Randle | -0.021 | -0.022 | +0.005 | -0.0272 | 0 |
| Royce O'Neale | 21->22 | Durant | +0.038 | -0.057 | -0.004 | -0.0528 | 1 |

## 2. Test the fix: does the residual still select usage-cutters?

**No, and the reason exposes an over-reach in the v0.1 headline that is worth stating plainly.** When you actually pull the usage numbers for the four v0.1 leap-band members, only ONE of them cut usage:

| v0.1 leap-band member | usg_delta | ts climb | what actually happened |
|---|---:|---:|---|
| Kevin Huerter | **+0.028** | +0.068 | usage UP and efficiency up (not compression) |
| Harrison Barnes | **+0.003** | +0.034 | usage ~flat, efficiency up |
| Taurean Prince | -0.011 | +0.025 | usage down slightly |
| Kyle Kuzma | **-0.083** | +0.035 | textbook usage cut |

Two of the four (Huerter, Barnes) RAISED or held usage while raising efficiency, which is the opposite of the usage-compression mechanism. Only Kuzma is a clean usage-cutter. So the section-2b sentence "they lifted true shooting by cutting usage" was true for Kuzma and overstated for the rest. Residualizing does exactly what it should: it **demotes the one true cutter (Kuzma)** out of the +1 SD band (his raw +0.035 climb shrinks to a +0.0205 residual once the -0.083 usage cut is credited) and it **rewards the flat/rising-usage gainers** (Huerter's residual +0.0706 exceeds his raw climb; Crowder, at 0.000 usage change and +0.035 climb, rises into the band). The residualized +1 SD band is Kevin Huerter, Jae Crowder, Harrison Barnes.

So the fix is worth keeping. But the honest conclusion is the deeper v0.1 recommendation, now REINFORCED rather than overturned: **JO-EFF, even residualized, is still only an efficiency axis, and it cannot certify a two-way skill leap.** Two independent reasons:

1. The R^2 is 0.029. Usage barely predicts the climb, so the residual band is nearly the same names as the raw-climb band; residualizing refines the ordering (Kuzma down, Huerter/Crowder up) but does not change what the axis is measuring.
2. The residual band's single clearest "real leap" candidate, Kevin Huerter, is the one member with all THREE JO-GROWTH rungs firing, and he is excluded from the LEAP tier below by the DEFENSIVE gate (he did not defend at SAC). That is JO-GROWTH plus the defensive gate doing the load-bearing work, not JO-EFF.

**Recommendation (unchanged in direction, sharper in evidence): adopt the JO-GROWTH-primary ladder.** The LEAP is defined by real growth rungs (self-created efficiency, FT rate, 3P volume-and-accuracy) gated by defense, with the residualized JO-EFF as a NECESSARY FLOOR, not the definition. A bare TS rise, and even a usage-residualized TS rise, is necessary-not-sufficient. This is the calibration's real yield.

Note on the canonical JO-GROWTH rungs: v0.2 uses the report's section-4 real-margin definitions, which reproduce the stated full-38 class counts exactly (a=20, b=14, c=6, any=27):
- (a) self-created efficiency: pull-up eFG% OR drive FG% up by >= +0.010
- (b) FT rate: FTA/FGA up by >= +0.010
- (c) 3P volume AND accuracy both rising: fg3a/g up AND fg3_pct up

(`defense_screen.py` had used a looser stand-in for rung (a); v0.2 corrects to the canonical definitions. On the screened 19: 12 clear >=1 rung, 4 clear >=2.)

## 3. The LEAP tier

**LEAP = defensive gate PASS AND residual JO-EFF leap band AND JO-FLOOR intact AND at least one JO-GROWTH signal.** Component definitions on the screened 19:

- **Defensive gate PASS** (section-5 composite, JD-COVER de-weighted to supporting): the gate FAILS only if JD-LOAD fails AND JD-HOLD fails; otherwise PASS. Note this is a deliberate departure from the spec's literal composite (which fails if JD-LOAD fails AND [JD-COVER OR JD-HOLD] fails): dropping JD-COVER from the conjunction makes the gate strictly **more lenient** (it fails less often), which is the intended effect of the v0.1 de-weight recommendation, not an accident. JD-LOAD pass at `jd_load_after >= 0.200` (the screened class's own median of the AFTER metric, so mildly self-referential; it does not affect the LEAP set because both LEAP members clear the gate via JD-HOLD suppression, not JD-LOAD). JD-HOLD pass at `jd_hold_after < 0` (holds primary options below their own baselines). Composite gate passes for 16/19.
- **Residual JO-EFF leap band**: `jo_eff_residual >= +1 SD` (section 1). 3/19.
- **JO-FLOOR intact**: `sa75_pctchg > -15%` (not down more than 15%). 13/19.
- **>=1 JO-GROWTH signal** (canonical rungs). 12/19.

**LEAP set on the screened 19 (2/19): Harrison Barnes, Jae Crowder.**

Both pass the composite gate (via JD-HOLD suppression), keep their scoring floor, sit in the residual leap band, and carry one growth rung each. Notably OUT and why, which is the tier working as intended:
- **Kevin Huerter** has the top residual and all 3 growth rungs but FAILS the defensive gate (JD-LOAD 0.165 and JD-HOLD +0.034 both fail at SAC). The biggest offensive leap in the class is not a Jaden-archetype LEAP because he did not defend.
- **Taurean Prince** passes the gate and the floor and sits in the wider p75 band but has ZERO growth signals, so the growth requirement excludes him: an efficiency bump with nothing real underneath.
- **Kyle Kuzma** is the only residual-band member with >=2 growth rungs but TRIPS the floor (sa75 -29%), a real volume collapse.

**Anchors as a reality check.** The two closest Jaden comps both PASS the gate cleanly but are NOT in the leap band: **OG Anunoby** is flat-band on efficiency (residual +0.010) with 2 growth rungs and floor intact, a solid two-way hold rather than a leap; **Mikal Bridges** passes the gate (strict, both components) but sits below the band AND trips the floor (the textbook -18.7% usage cut). The honest read for Jaden: a LEAP is rare in this class, and the realistic prior for a 3-and-D wing arriving next to a high-usage creator is gate-pass-and-hold (Anunoby / Bridges), not an efficiency jump.

### Sensitivity: one vs two growth signals

**Requiring TWO growth signals instead of one empties the LEAP set: 2 -> 0.** Barnes and Crowder each carry only one rung, so both drop. The only residual-leap member with >=2 growth rungs is Kuzma, and he is already excluded by the floor. This is robust: no wing on the screened class simultaneously (a) passes the defensive gate, (b) sits in the residual leap band, (c) keeps the floor, AND (d) shows two independent growth signals. The tier is genuinely demanding on this population, which is the correct read for a small, survivorship-tilted class, not a defect to tune away before more data.

Two further sensitivities in the same direction:
- **Gate strictness.** Under a stricter gate (require BOTH JD-LOAD and JD-HOLD to pass, not the composite), the LEAP set is empty even at >=1 growth: Barnes and Crowder both fail the JD-LOAD 0.200 deployment bar and clear the composite only through JD-HOLD suppression. The two seeds that pass the strict gate (Anunoby, Bridges) are not in the leap band. So under the strict gate the class produces no LEAP, reinforcing that the tier is rare here.
- **Residual threshold.** Swapping +1 SD for the 75th-percentile band (3 -> 5 members) does NOT change the LEAP set: the two added members (Prince, Kuzma) fail on growth and floor respectively.

## 4. Gordon: reclassified to adjacent-informative (appendix, OUT of class)

**Aaron Gordon is OUT of the v0.2 calibration class.** His `jd_load_before = 0.1816` is below the class median 0.1906 that defines the defense screen, so the non-circular BEFORE-deployment filter drops him (0.182 vs 0.191). The basis is archetype, not arithmetic: at Orlando, Gordon was a versatile forward who guarded up a position, not a point-of-attack perimeter stopper, so his defensive-load archetype is a step away from Jaden's. He is kept as an APPENDIX row, **adjacent-informative**: he remains the canonical OFFENSIVE success next to a star (he owns the full-38 true-shooting max at +0.086, +0.074 over his own trailing-3), but that success is exactly of the archetype the screen is designed to exclude when calibrating a 3-and-D wing. Reporting him inside the class would re-import the offense-first contamination v0.2 exists to remove.

**Bridges (0.297) and Anunoby (0.312) anchor the comp set.** They are the closer 3-and-D comps, they survive the screen, and they carry the LEAP-tier reality check in section 3. Gordon's row is retained for context and honesty about the seed set, flagged clearly as out-of-class.

## 5. JD-COVER coverage

JD-COVER is computed for **34 of 38** full-class members. The 4 panel-pending are 2025-26 AFTERs that fall outside the built stint panel (RS through 2024-25): De'Andre Hunter -> CLE, Kyle Kuzma -> MIL, Cameron Johnson -> DEN, Tim Hardaway Jr. -> DEN. Within the screened 19, two are JD-COVER panel-pending: De'Andre Hunter and Kyle Kuzma. This does NOT affect any LEAP determination, because the LEAP gate runs on JD-LOAD + JD-HOLD (both computed for all 19) with JD-COVER de-weighted to supporting evidence per v0.1 section 5. Extend the panel by one season to close the four before the season-end 2026-27 read.

## 6. Discipline and what stays unfrozen

Descriptive, not causal: every BEFORE->AFTER movement is confounded by age and development curve, by the mechanical efficiency lift of a usage cut, by scheme and shot diet, by health, and by the shortened 2019-20 / 2020-21 seasons inside several windows. The class conditions on wings who kept a starter role in both seasons, so it is an optimistic, survivorship-tilted reference, not a random sample. n=19 spanning 17 distinct players, with 2 (Kelly Oubre, Garrett Temple) contributing two pairings each in the screened set (the "7 repeats" figure is the full-38 count, not the screened one), so observations are not fully independent and bands at the 25th/75th percentile move by a member or two under reasonable filter changes. The residualization R^2 is low (0.029) precisely because the sample is small and heterogeneous; the slope's sign is the trustworthy part, not its magnitude.

Freeze NOTHING now. For the 2026-10-20 freeze: adopt the JO-GROWTH-primary ladder with residualized JO-EFF as a floor; carry the composite gate (JD-LOAD + JD-HOLD) with JD-COVER as supporting; extend the stint panel to 2025-26; and keep Gordon as an out-of-class appendix comp with Bridges and Anunoby as the in-class anchors. All thresholds remain PROPOSED / TUNE.

## 7. Ratifications (Bobby, 2026-07-17)

The v0.2 directive rulings, accepted for the record. None of these freezes anything before 2026-10-20; they fix the DIRECTION the freeze will take and are what the board build now consumes.

1. **Ladder inverted, ratified.** JO-GROWTH is the PRIMARY leap distinguisher (self-created efficiency, FT rate, 3P volume-and-accuracy, gated by defense); residualized JO-EFF is a NECESSARY FLOOR, not the definition. A bare TS climb, even usage-residualized, is necessary-not-sufficient (sections 1-2).

2. **LEAP defined at ONE growth signal, ratified.** The class-instance LEAP set is {Harrison Barnes, Jae Crowder} (section 3). The two-growth-signal variant is retained as a reported SENSITIVITY only, and is labelled HISTORICALLY EMPTY on this population (2 -> 0): no wing on the screened 19 simultaneously passes the defensive gate, sits in the residual leap band, keeps the floor, AND shows two independent growth signals. That emptiness is the correct read for a small survivorship-tilted class, not a threshold to loosen.

3. **Gordon appendix stands, ratified.** Aaron Gordon remains OUT of the calibration class (adjacent-informative appendix, section 4): his BEFORE-deployment defensive load (0.182) sits below the class median (0.191), so the non-circular screen drops him. Bridges (0.297) and Anunoby (0.312) are the in-class anchors and carry the realistic Jaden prior: gate-pass-and-hold, not an efficiency jump.

4. **Board `jaden` priors seeded from the screened-class tier frequencies (TUNE), done.** So the board's expectation of the leap is the historical base rate, not hope. The screened class (n=19) partitions to: LEAP 2/19 = 0.105 (Barnes, Crowder), CONVERTED ~1/19 (Kevin Huerter: defensive gate FAILED but offensive leap achieved, the archetype-change branch), STALLED ~6/19 (the JO-FLOOR trippers), STEADY the remainder ~10/19 (the Anunoby/Bridges gate-pass-and-hold). These seed `jaden_dist` in `../build/board_step4.py`: the T2 band is pinned to the class base rate and perf tilts it modestly, so the perf-averaged leap probability stays near 0.105. The board consumes this as a PRIOR to tune, carrying the section-6 discipline (n=19, confounded, descriptive). See `../build/board_step4_report.md`.
