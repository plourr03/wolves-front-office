# Phase 0 Availability Reconciliation

Tripwire backtest, Phase 0 Step 4a. Produced 2026-07-17.

This is a hygiene note, not a backtest artifact. It exists because building AVAIL-PACE forced a look at where LaMelo Ball's availability number actually comes from, and the answer is that there are three different numbers living in the `lamelo/` project, published side by side, without a single canonical source. That is worth fixing independent of the tripwire work, because two shipped pieces can disagree depending on which number they read.

## The three numbers

| Number | Meaning | Defined at | Published? |
|---|---|---|---|
| **63 games** (band [44, 73], grade 2027-04-15) | Hand-logged cold analyst prior. A bet, deliberately not retuned. | `lamelo/DELIVERABLE.md:150`, `lamelo/prereg/preregistration.md:113` | Yes |
| **49 games** (model median, "~50") | The reference-class model center: median of his six-season games-played history. | Computed `lamelo/fit_decomp/lever5_findings.md:17`; hard-coded `lamelo/article/viz/lamelo_availability_fragment.html:62` | Yes |
| **0.75** survival fraction (band [0.50, 0.90]) | Hand-set scalar haircut, multiplied into his transported net rating. | `lamelo/impact/build_transport.py:19` | Yes, as the derived +0.90/+1.41, and literally at `DELIVERABLE.md:23` |

These are not three estimates of the same quantity, which is the first thing to say clearly. **63 and 49 are both games-played** (a prior bet vs a model median, which is a legitimate and intentional gap). **0.75 is a value-survival multiplier on net rating, not a games count.** It happens to imply roughly 61 games if you read it as a played-fraction of 82, but that is not what it is; it is the fraction of on-court impact assumed to survive transport to Minnesota's role. Conflating the three is the risk this note exists to prevent.

## Consumer trace

### 63 games (analyst prior)

Defined in the immutable prediction log and preregistration. Consumed by: `fit_decomp/lever5_findings.md` and `SYNTHESIS.md` (which reconcile it against the model and judge it above-model), the `prediction_log` and `lamelo_availability` viz fragments, both slide renderers (`render_lamelo_slide.py:154`, `render_lamelo_carousel.py:313,395`), and both article drafts. It reaches publication in the DELIVERABLE, two viz fragments, two social slides, and the article.

### 49 games (model median)

Truly derived in `lever5_findings.md:17` (bootstrap of the six-season history 51, 75, 36, 22, 47, 72; full-six median 49, mean 50.5). Hard-coded as `MEDIAN = 49` in the availability viz. Consumed by: the availability viz, the five-levers viz, both slide renderers, and both article drafts, always framed as "the model centers near 49, I bet 63."

### 0.75 survival fraction

Defined in `build_transport.py`, written into `data/impact/transport.json` as `survival_fraction.center = 0.75`. Consumed by: `build_team_strength.py` and `sweep_regression_K.py` (which read the 0.75-derived `B_surv_on_off.net_center`), and through `team_strength.json` into `sim/run_sim.py`, so it propagates into the title-odds simulation. Published as the derived net (+0.90 RAPM / +1.41 box) in the DELIVERABLE and draft v1, and as the literal "0.75 offensive survival" at `DELIVERABLE.md:23`.

## Findings worth acting on

Three, in descending order of importance.

**1. The DELIVERABLE prints 63 without the above-model caveat that governs it everywhere else.** The DELIVERABLE's own audit note ("Fix 3", `DELIVERABLE.md:156-159`) flags predictions 1 and 2 (54 wins, 4-seed) as above-model priors. It does **not** name prediction 3 (games played). So the DELIVERABLE's section 8 table prints 63 as "the prediction" with no in-table signal that the model actually centers at 49, while the article, both viz fragments, and both slides all frame 63 as the optimistic bet over a model median of 49. A reader of the DELIVERABLE table alone and a reader of the article come away with different headline numbers. They are reconciled in the article, but not inside the DELIVERABLE. This is the concrete "two published artifacts disagree" case.

**2. The availability viz mis-cites its own source.** `lamelo_availability_fragment.html:57` comments that the 49 center comes from "DELIVERABLE section 8." It does not. DELIVERABLE section 8 states only 63; its only "49" is a win total (46-49 wins), a different quantity entirely. The real source of 49 is `fit_decomp/lever5_findings.md`. The chart is correct; its provenance comment points at the wrong file, and at a file that contains a same-valued number for a different quantity, which is how these things become genuinely confused later.

**3. The survival band [0.50, 0.90] is defined and serialized but never consumed.** `SURV_LO`/`SURV_HI` are written into `transport.json` and restated in findings prose, but no downstream reader reads `net_band` or the `A_surv_on_net` fork. The title sim's uncertainty band comes from the metric-fork range (RAPM vs box), not from the survival band. So the band reads as if it drives uncertainty when it does not. Not wrong, but misleading to anyone who assumes the published [0.50, 0.90] flows anywhere.

## Recommendation

Make **games-played** have one canonical source, and keep it distinct from the value haircut.

- Canonical games-played baseline for all downstream use: **the warehouse-derived prior-season games history**, computed once, not hard-coded in a viz. The tripwire project's own baseline (prior-three-season median, matching the YB3 label definition) is derivable from `nba_player_stats` joined to `nba_games`. From the six stated seasons (2020-21 through 2025-26: 51, 75, 36, 22, 47, 72), the repo already reports full-six median 49 and last-four median 42; the prior-three-season median (22, 47, 72) is **47**, which the repo does not currently state anywhere and would need to be computed rather than cited.
- The **63** stays exactly as it is: a logged analyst prior, a bet. It should not be retired. It should be labeled as above-model in the DELIVERABLE table the same way it is labeled everywhere else, so the DELIVERABLE stops being the one artifact that hides the gap.
- The **0.75** should be renamed in prose wherever it sits next to a games count, so it is never read as "61 games." It is a value-survival fraction. If it is to be derived rather than hand-set, that is a modeling change owned by the LaMelo project, out of scope here.

## Scope

This note names the change set. It does not perform any of it, because every fix touches `lamelo/`, which is out of Phase 0 scope. The change set, for whoever picks it up:

1. `DELIVERABLE.md:150` area: add an above-model marker to prediction 3, matching predictions 1 and 2, or add 49 to the table as the model center beside the 63 bet.
2. `lamelo/article/viz/lamelo_availability_fragment.html:57`: fix the provenance comment to point at `fit_decomp/lever5_findings.md`, not DELIVERABLE section 8.
3. `lamelo/impact/build_transport.py` and `transport.json`: either wire the survival band into the sim or drop it from the serialized output and prose, so defined equals consumed.

## Relationship to AVAIL-PACE

None of the three numbers is the AVAIL-PACE baseline. That is the point of section 4b: the wire's baseline is the warehouse-derived prior-season median (the same source recommended as canonical above), and its uncertainty comes from the Scenario B reference class, not from any of these three hand-set figures. The 63 becomes a sensitivity scenario. The 49 and the 0.75 do not enter the wire at all. This note and 4b share one recommendation: games-played availability should have a single, warehouse-derived, canonical source, and everything else is either a labeled bet or a different quantity.
