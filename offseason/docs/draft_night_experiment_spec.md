# Draft-Night Experiment: Architecture and Spec ("Three Doors")

Author note for anyone building this: no em dashes or en dashes anywhere. Commas, periods, parentheses.

## 1. Concept and goal

One carousel for Wolves to a T, posted as a pre-draft preview. It lays out three hypothetical draft-night trade philosophies the Wolves could run, each a chained multi-step deal, and scores each one on the real choice Connelly faces: how much it helps us win now versus how much future it builds. The three are deliberately different points on that tradeoff:

- The Swing: go for it now, cash flexibility for a lead guard next to Edwards's prime.
- The Flip: be the smart middleman, turn dead money into a guard and keep your own picks.
- The Stockpile: bet on patience, stack assets for a bigger swing when a real star shakes loose.

Framing is hypothetical throughout ("one way this could go," "my model says"), never a prediction. The point of doing three is that a single prediction almost certainly misses, but three plausible paths is a portfolio, so the odds that what Connelly does rhymes with one of them is much higher. That sets up the real win: if draft night produces something that looks like one of the doors, we post a follow-up that says we mapped it days earlier.

## 2. The analytical backbone: two-axis scoring

Every scenario is scored on two axes, both pulled from the model. This is the rigor, and it is honest about the fact that there is no single best answer.

Axis 1, win-now (title): the championship-probability change of the final post-chain roster versus the current baseline, read with the conservative anchor (the lowest of the four metric views), not the flashy headline. Show it as a title-odds change.

Axis 2, future (capital and flexibility): a composite of three things:
- net first-round picks gained or spent, valued on the model's asset-point and pick scale
- young or cost-controlled talent acquired, valued on surplus but treated as a floor, because the model is known to undervalue young players, so we do not let it understate the future-heavy scenarios
- flexibility gained, mainly apron room (for example, ducking the second apron unlocks salary aggregation and escapes a hard cap) and any cap space freed

On each scenario slide we show the breakdown (title change, net picks, apron move, young talent), because a breakdown is more legible and more honest than one opaque number. For the final comparison slide we synthesize the future components into a single position so the three scenarios can sit on one plane.

### Two methodology rules that are easy to get wrong

1. These are chains, and the model scores one trade at a time. So each scenario is run as a sequence: apply leg one, re-rate the roster and cap, then run leg two on the new state, and so on. Judge the scenario by where the roster lands, not leg by leg.
2. The apron-duck leg (sending Gobert out) will look flat or negative on its own. That is the same keep-Gobert finding the board already produced. In a chain its job is to unlock the next move, so do not read its standalone number as the scenario's value. The scenario's value is the end state plus the flexibility it bought.

## 3. The format: scenario carousel

The body shows the trades, because that is what trade fans come to see. The two-axis rigor rides along as a scoreboard and pays off at the end. Reuse the editorial and human design system from the social work (one accent, real type pairing, squared bars, minimal chrome, footer credit and issue number) and the framing and data conventions from the trade-posts skill, adapted from a single-trade layout to a three-scenario comparison.

Slide plan:
- Slide 1, hook: "Connelly walks into draft night with three doors." One line that sets up the future-versus-win-now tension.
- Slide 2, the setup: the constraint in one breath, Minnesota is jammed at the second apron, only Edwards, McDaniels, and Beringer are off the table, and the apron is why every plan starts with a money move.
- Slides 3 to 5, one per door: the trade chain laid out visually (who and what moves, in order), the two-number scoreboard (title change and future breakdown), a one-line thesis, and the model's read on whether the partners say yes.
- Slide 6, the payoff: the three doors positioned on a future-versus-title plane, so the whole choice lands in one picture.
- Slide 7, outro and CTA: "Which door would you open?" plus the Wolves to a T tag. The question is engagement bait and it is honest, since the point is that there is no single right answer.

## 4. The three scenarios (proposed v1, pending model validation)

These are designed starting points. Every counterparty and every term is a candidate that must be validated through the model for legality and acceptance before it is published. Swap in whatever the model confirms. Grounded parts are noted, parts that need locking are flagged.

### Door 1, the Swing
Thesis: trade flexibility for a star-level guard while Edwards is in his prime.
- Leg 1, the apron duck: Gobert to a center-needy contender for a future first and a smaller expiring. Grounded mechanic (verified cap engine handles the duck). Flag: the specific contender is a model-surfacing task, find a team whose acceptance fires on taking Gobert (a positive-surplus player a rim-needy contender wants), prioritizing real center needs.
- Leg 2, the strike: Randle plus the No. 28 pick (plus filler to match) to Memphis for Ja Morant. Grounded: the news layer has Morant being shopped by a rebuilding Memphis. Flag: validate the salary match against Morant's number.
- Backfill: Beringer slides to starting center, add a cheap rim protector from the Capela, Clingan, Kessler tier with the exception, since moving Gobert opens the rim (the rim-protection trap the model keeps surfacing).
- Expected position: high title-now, low-to-middle future (banks a future first from leg 1 but spends the No. 28 and takes on Morant's salary and risk). Ducks the apron, which is a real flexibility gain.

### Door 2, the Flip
Thesis: be the middleman, turn dead money into a real guard, keep your own picks.
- Leg 1: Randle plus the No. 28 pick to a rebuilder that wants an expiring and a pick, for a young shooter on a cheap deal plus a future first. Flag: lock the rebuilder (a Washington or Utah type) and the shooter via the model.
- Leg 2: the acquired future first plus Gobert (plus filler) to a tanking team for a cost-controlled starting guard, steadier and cheaper than the Morant swing. Flag: lock the tanker and the guard via the model and current reporting.
- Expected position: middle on both axes, a real point guard next to Edwards and a young shooter, with your own future firsts untouched.

### Door 3, the Stockpile
Thesis: bet on patience, stack assets for a bigger swing later.
- Move Gobert to a contender for picks and youth, and Randle to a rebuilder for youth and a pick, as two separate deals (no aggregation needed).
- Re-sign or sign-and-trade Dosunmu.
- Optional: flip Reid if a contender overpays for his scoring and shooting, for more youth and picks.
- Flag: lock each return via the model.
- Expected position: low title-now (flat to slightly down next season), high future (under the apron, a stack of future firsts, still anchored by Edwards, McDaniels, Beringer, and Reid).

## 5. Data integrity and framing rules

- Every number on the slides comes from the model or the warehouse. No invented picks, salaries, or odds.
- Every counterparty's willingness is the model's acceptance read, framed as such ("my model has them saying yes here"), never as fact.
- "Available" claims are sourced from the news layer (Morant shopped, and so on), and stay current as of the post date.
- Title odds are quoted as the anchor and, where useful, a range, not a single decimal presented as truth.
- The whole piece is labeled hypothetical. We are mapping choices, not reporting deals.

## 6. Build pipeline and ownership

1. Lock the scenarios (this doc, then refine): confirm the legs and the candidate counterparties.
2. Bobby, in the model: validate each leg (legal and accepted), lock the real counterparties the model confirms, then run each scenario as a chain (apply leg one, re-rate, leg two) to produce, per scenario, the end-state title odds with the anchor and the future breakdown (net picks, apron move, young talent). Hand the outputs over.
3. Claude: build the carousel from the validated outputs, write the copy, produce the slides on the design system, and assemble the future-versus-title payoff plane.
4. Review and iterate, then ship.

## 7. Timeline (working back from draft day)

The draft is around June 23. Ship the preview a day or two before so it rides in.
- By June 18 to 19: scenarios and candidate counterparties locked from this doc.
- By June 20: Bobby has validated the legs through the model and handed over the scored chains.
- June 20 to 21: Claude builds the carousel and copy.
- June 21 to 22: review, finalize, ship the preview.
- Keep a short reaction post drafted and ready for the night of and the morning after.

Honest note: six days for three validated chains plus a built carousel is tight. Keep each scenario lean rather than gold-plating it, and if the clock slips, lead with the Swing as a standalone and follow with the other two, accepting that this costs the single-image comparison payoff.

## 8. Post-draft reaction plan

If Connelly does something draft night that rhymes with one of the doors, post the follow-up: "Three days ago I mapped three ways this could go, here is the one that happened." Have the comparison plane and the matching door's slide ready to repost with the result overlaid. That is the credibility moment, so it is worth pre-staging.

## 9. Open items and risks

- Counterparties to lock via the model: the Gobert suitor in the Swing, the rebuilder and shooter in the Flip's leg one, and the tanker and guard in the Flip's leg two, plus all of the Stockpile returns.
- Scope versus clock: all three in one carousel is the goal, leading with the Swing is the fallback.
- Model scope: these are Minnesota-acquisition chains, which is the model's validated lane, so the legs are in scope. The future axis leans on pick and asset-point values rather than raw young-player ratings, because of the known youth-undervaluation.
- Moving target: rosters and the cap shift through the draft and free agency, so validate against the freshest data right before shipping.
