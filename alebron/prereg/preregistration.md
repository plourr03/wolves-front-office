# Pre-registration and prediction log: LeBron James → Timberwolves evaluation (alebron)

STATUS: LOCKED 2026-07-03. This project (`alebron/`) is a clean CLONE of the LaMelo evaluation
(`lamelo/`), reusing its pre-registered methodology, calibration, and identifiability gates
verbatim, applied to a new question. Honesty note on sequencing: unlike the LaMelo prereg (inputs
committed cold before any modeling), this clone was built in a single session, so the engine and
gates are INHERITED-and-locked while the LeBron-specific inputs below are registered here with
their rationale and are NOT retuned after the fact. The forward predictions (bottom) are the
immutable log reality will grade in 2026-27.

## Registration header

- Analysis name: Clean-room evaluation of a hypothetical LeBron James free-agent signing onto the
 completed post-LaMelo Timberwolves.
- Date registered: 2026-07-03. Analyst: Bobby (project owner), build agent (engine + adaptation).
- Estimands:
 - Q0 (feasibility): can MIN legally sign LeBron under the second-apron hard cap, and at what
 price? Reported as a cap-sheet fact.
 - Q1 (decision grade, opportunity cost): is a minimum LeBron the best use of the last roster
 spot vs a healthier younger minimum body? Reported ordinally. Asset cost is ~zero (the sharp
 contrast with LaMelo).
 - Q2 (state estimate): the +LeBron roster's P(title), reach-CF, reach-Finals, and the CRN-paired
 delta vs the completed post-LaMelo baseline, against the live 2026 field.
- Decision served: not a go/no-go (a what-if). A reusable calibrated engine + a graded track record
 + a published evaluation that survives a sharp reader.

## Registered inputs (not retuned to taste)

| Input | Source context | Committed value | Uncertainty |
|---|---|---|---|
| LeBron age-and-role RETENTION | Measured net RAPM +1.27 / box +1.53 at age 40-41 (2025-26). Source context (competitive, high-leverage LA) transfers well; the haircut is AGE, not context. Value is diffuse (def + connective), so retention is applied to NET, not offense (operationalization documented in build_transport.py). | **0.80 on NET** | Band **[0.55, 1.00]**. The single widest per-minute term. |
| LeBron AVAILABILITY | 41 turning 42 (b. 1984-12-30); 24th season. Missed first 14 games of 2025-26 with sciatica (~60 GP). The catastrophic-regret tail (breaks down / retires mid-season) lives here. | rotation ~30 mpg, ~55 GP center | swept full(30)/reduced(20) mpg; GP band [38,68] |
| Three-initiator FIT | Edwards + Ball + James on-ball collision, NO spacing added (LeBron ~31% 3P; Reid/Randle gone), LeBron hunted on D, vs LeBron as connective orchestrator/closer unlocking Edwards off-ball + Gobert lobs. | scenario-parameterized ±0.75 net | fit-clicks / neutral / fit-fails; sweep ±0.5, ±1.0 |
| Cap feasibility | Second-apron hard cap $221.686M (verified); 10+-yr min cap hit $2,449,421; taxpayer MLE $6,064,000. | minimum-for-minimum SWAP only | binary legality; MLE infeasible |

## Registered named hypothesis: the three-initiator fit (reported with its hedge)

- Upside: LeBron as the half-court orchestrator and closer raises Edwards' efficiency off-ball and
 Gobert's ceiling via rim pressure/lobs; elite playoff IQ stabilizes non-Edwards minutes.
- Hedge (symmetric): three ball-dominant creators collide for on-ball reps with no floor spacing
 added, and LeBron is hunted defensively at 41-42; the bench is thinner because he cost a rotation
 body. Reported as a paired decomposition line, never one without the other.

## Registered objective (unchanged from lamelo)

Q2 uses only the on-court roster. Q1 adds the option-value and catastrophic-regret terms, but here
OV(assets surrendered) ≈ 0 (a minimum FA signing spends no picks), so the Q1 verdict is dominated by
the roster-spot opportunity cost and the availability tail, NOT by asset cost. This is the structural
reason the LeBron decision grade diverges from LaMelo's.

## Registered kill criteria (when no number publishes), inherited, and they FIRED

Publish the qualitative decomposition only, and decline a probability, if the impact/sim calibration
fails, the multiverse is unstable, OR the identifiability pre-check puts the delta inside the noise
floor / a retrodiction gate misses. RESULT: the star-acquisition retrodiction gate FAILED again
(engine-level, `run_gates.py` → Case 3), and the point estimate assumes unmodeled availability, so
the precise title percentage is DECLINED, consistent with the LaMelo project.

## Falsifiable forward predictions (reality will grade these)

Grade dates: signing question ~2026-10-01; regular-season quantities ~2027-04-15; playoff ~2027-06-30.

| # | Prediction | Point | Band | Grade date | Status |
|---|------------|-------|------|------------|--------|
| 1 | LeBron signs somewhere on a minimum/MLE-tier deal (not a max) | true | n/a | 2026-10-01 | LOCKED |
| 2 | IF MIN: LeBron games played | 55 | [38, 68] | 2027-04-15 | LOCKED |
| 3 | IF MIN: Wolves win total | 51 | [44, 56] | 2027-04-15 | LOCKED (above-model prior) |
| 4 | IF MIN: Edwards+Ball+James three-on-court net | +2.0 | [-4, +8] | 2027-04-15 | LOCKED |
| 5 | IF MIN: reach conference finals | ~22% (model) | one-shot | 2027-06-30 | LOCKED |

Prediction 4 settles the fit fork the calibration cannot: near +8 is fit-clicks, near -4 is the
three-alpha collision. Reality closes the loop.

## Note on the LaMelo contrast (the reason this clone exists)

The LaMelo evaluation found a wash-to-modest-negative on-court change bought with a mountain of
future and a hard cap. This evaluation finds a small-positive-to-good on-court change bought with a
roster spot and an availability gamble. Same engine, same gates, opposite risk profile. The hard cap
the LaMelo deal created is exactly what forces LeBron to a minimum, the two analyses are linked, and
that linkage is the story.
