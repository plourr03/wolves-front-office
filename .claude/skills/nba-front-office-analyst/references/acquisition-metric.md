# The Acquisition Metric (reference)

A structured way to evaluate any potential acquisition target. It is not a single score. It is a profile that gates before it scores, because a target you cannot acquire should never rank above one you can. The output is a profile plus a conditional verdict matrix plus a tier, with the roll-up logic written out rather than hidden in weights.

## Design philosophy

- **Gate, then score.** Feasibility is a hard gate that returns a category, not a smooth dimension.
- **Show the parts.** A reader should see salary fit, contract health, need fit, and impact separately, then how they combine.
- **No black box.** Every input traces to a source. Weights are explicit. The comp set behind any trade-value range is named.
- **Honest uncertainty.** Trade value and roster effect are both uncertain. The metric expresses ranges and bands, never false precision.

## Component 1: Acquisition feasibility (the gate)

Returns one of: feasible, stretch (direct), stretch (via setup trade), infeasible. Two sub-gates.

**1a. Salary-matching feasibility.** Given the acquiring team's apron position, can a legal salary match be constructed for the target's incoming salary using realistic outgoing-salary combinations? Respect the matching band for the team's tier (generous below the first apron, tighter at the first apron, dollar-for-dollar with no aggregation at the second apron), the apron thresholds, and any hard cap triggered. Output the minimum viable outgoing set and the apron line the deal lands under.

**1b. Asset feasibility.** Benchmark the target's likely market price against a comparable-trade database, then compare to the assets the team can actually assemble (tradeable picks under the Stepien and seven-year rules, plus young players). Distinguish clearly:
- feasible: market price is within the chest.
- stretch (direct): requires most of the chest and a favorable market.
- stretch (via setup trade): infeasible directly, reachable only through a documented two-stage path where an intermediate trade returns assets that are then repackaged.
- infeasible: the price exceeds what the team can assemble even after a setup trade.

The "via setup trade" category matters when a team's biggest target cannot be acquired in one step. Model feasibility as a chain in those cases, with intermediate returns expressed as comp-anchored ranges, never point prices.

## Component 2: Contract and timeline fit

Legality is not the same as a good contract. Evaluate the target's salary across the full contract, the length, player and team options, trade kicker (which inflates matching math), no-trade clause (which gives the player veto power and feeds back into feasibility), and age relative to the contract's end versus the team's competitive window. Output a contract-health read (good fit, tolerable, toxic) with the specific reasons, including whether the deal worsens the apron problem in future years.

## Component 3: Need fit, conditional on the post-trade roster

The subtle centerpiece. Two steps.

**Define need from data, per exit scenario.** Build a team-need vector across dimensions: half-court shot creation and rim pressure, secondary playmaking, off-ball shooting and spacing, defensive versatility and point-of-attack defense, rim protection and rebounding, transition. Quantify each from tracking, Synergy, and box data. The need vector is the gap between a contender-level benchmark and the projected returning-roster profile after the subtraction, so it is recomputed for each exit scenario. Calibrate the benchmark toward playoff conditions, since contention is decided in the half court against set, switching defenses.

**Score the target against the need vector.** Project the target's contribution on each dimension from his own profile, with role and translation adjustments (discount a high-usage iso scorer when the need is off-ball spacing; discount a low-usage 3-and-D wing when the need is on-ball creation). Need-fit is the weighted dot product of the target's profile and the need vector, so a great player who does not fill the actual hole scores lower than a good player who fills it precisely. Fit with the younger core's timeline is itself a dimension, not a tiebreaker.

## Component 4: Player impact and playoff translation

The cross-team valuation spine is a reproducible multi-year RAPM built from play-by-play, triangulated against public all-in-one metrics as sanity checks rather than sources of truth. Add a playoff-translation read: how the game holds up against switching and physicality (half-court and pick-and-roll efficiency versus set defenses, playoff splits where the sample allows, with sample-size caveats stated every time). Output an impact estimate with an explicit uncertainty band. RAPM standard errors are large; carry them rather than publishing a misleadingly precise point.

## The roll-up

For each target produce:

1. Feasibility verdict (the gate), with minimum viable package and apron landing.
2. Contract health with reasons.
3. Need fit: which specific needs filled, under which scenario, with the per-scenario score.
4. Impact: the value estimate with its band, plus the playoff-translation note.
5. **Conditional verdict matrix:** target by exit scenario, each cell holding feasibility, need-fit, and net roster value. This matrix is the heart of the output, because it shows how the answer changes by scenario instead of collapsing to one number.
6. **Overall tier:** priority target, worth pursuing, situational, pass, or infeasible, derived by a written rule. A target must clear the feasibility gate to rank above infeasible. Among feasible targets, rank by need-fit times impact, with contract health and timeline as modifiers. Show the rule so a reader can disagree with the weights and recompute.

## Exit scenarios (the conditional machinery)

Define a small, explicit set grounded in the team's actual situation, for example:
- status quo (relevant only for low-cost additions, since cap math usually forbids adding salary without subtracting),
- a high-salary forward out,
- the starting center out,
- both out (the scenario that frees enough salary for a max addition),
- a young-core piece out (the painful scenario, invoked only when a target's market demands it).

Each scenario yields a different returning-roster profile and therefore a different need vector. Run each target only against the scenarios in which it is plausibly acquirable. These scenarios map directly onto scenario rows in the team-state data layer.

## Uncertainty handling

- Feasibility: discrete categories with the binding constraint named, never a probability to two decimals.
- Trade cost: a range grounded in named comps, never a point price.
- Impact: carry standard errors, show a band, flag small playoff samples.
- Need fit: publish the weights, then run a sensitivity check. If a reasonable reweighting flips the verdict, say so.
- Close every profile with "what would change this verdict," naming the key assumptions and how fragile they are.

## Reproducibility

Every input traces to a source (a data table or a public source plus a date). Weights are explicit and version-controlled. The comp set anchoring each trade-cost range is listed by name. The roll-up logic is written as rules. A front-office reader should be able to rebuild the verdict from the inputs.
