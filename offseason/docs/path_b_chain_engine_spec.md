# Chain Engine Build Spec (Path B)

No em dashes or en dashes anywhere. Commas, periods, parentheses.

## Goal

Let the model evaluate a sequence of trades (a chain), where each leg changes Minnesota's cap and roster, the next leg is judged against that new state, and the whole chain is scored on where it ends, not leg by leg. This is the capability the model does not have today. The current chain handling stops at the first illegal leg, is subtraction-only (it removes outgoing salary but models no incoming return), does not propagate the first-apron hard cap, and scores a single hand-assembled final roster rather than a real sequence.

## What this is not

The draft-night content scenarios stay in lane: keep Gobert, acquisitions built around Randle and Naz and the picks and the trade exceptions as the chips. The relaxed-untouchable path below is a separate exploration capability, not a license to put untouchables in the content scenarios.

## 1. Core: carry state leg to leg

For a chain of legs L1 through Ln:
- Hold a mutable team-state for Minnesota, and for any other team that appears in more than one leg, that updates after each leg.
- After applying leg i, recompute Minnesota's apron salary, cap basis, room under the tax and both aprons, hard-cap status, the roster (who is in and out), and any trade exceptions the leg creates.
- Evaluate leg i+1's legality and acceptance against the post-leg-i state, never the original.
- Model the full transaction on every leg, outgoing and incoming salary both. Room opened by a leg equals outgoing minus incoming, so the engine never assumes a clean salary deletion.

## 2. The first-apron hard cap must propagate

- The 2026-27 lines are tax $201M, first apron $209.7M, second apron $222.4M. Minnesota starts over the cap and under the tax, roughly $17.5M under the first apron.
- If any leg takes back more salary than it sends, Minnesota is hard-capped at the first apron for the rest of the chain and the season.
- Once hard-capped, no later leg may push Minnesota's apron salary above the first apron. Enforce that on every downstream leg. This is the keep-Gobert squeeze generalized: a chain can trip the hard cap on leg one and that ceiling then constrains everything after it.

## 3. Swap, not dump (this is from the Morant test)

- Moving a big veteran is a swap, not a free dump. There is no team that can cleanly absorb a $33M contract for nothing. A partner sends a real contract back, or in a three-team leg routes salary to a third party.
- So a shed-Randle leg does not open his full $33.3M of room, it opens his salary minus whatever comes back. The engine computes room from the net.
- The engine should reflect this everywhere, so it stops promising room that does not physically exist.

## 4. Three-way salary routing (the gap we found)

- The current three-team logic assumes a third team's matching salary routes back to Minnesota, which is why it declared "no Randle home" on a deal that actually has one.
- Generalize it. A third team's outgoing salary can route to whichever team in the chain best absorbs it, most often expiring contracts to a teardown team, not just back to Minnesota.
- When the engine needs to place a contract, it should search structures where the absorbing team sends its matching salary to the team that wants it (expirings to a rebuilder is the common case), so Minnesota comes out clean. This removes the false "no home" verdicts.

## 5. Score the end state, not the legs

- Score the chain on the final roster's championship-probability change, reported with the conservative anchor and the risk-adjusted number and the four-view spread, plus the final cap position.
- Never judge a chain by summing or gating on individual legs. A setup leg that sheds salary to open room looks flat or negative on its own. Its value shows up only in the end state.
- For the two-axis read, also report the final future-capital breakdown: net picks, young talent (as a floor, see flag below), and apron room gained.

## 6. Relaxed-untouchable path for hand-specified chains

- Keep the untouchable filter on the automatic board search. It keeps that search realistic.
- But the engine must be able to evaluate any hand-specified chain, including legs involving untouchables (Edwards, McDaniels, Beringer). The untouchable list is a search filter, not a valuation limit.
- Add a path or flag where a user-specified chain bypasses the untouchable prune and is evaluated on its merits. The engine will correctly say Minnesota loves a deal like Edwards plus Gobert for two MVP-level guards, and the acceptance layer will correctly say the partner refuses. Both outputs are useful, so do not pre-block them. This is what lets us explore bold trades, including a Gobert-out multi-piece deal, and see what the model actually says.

## 7. Carry the known limits into the output (honesty flags)

- Young players: when a leg brings back young or rookie players, flag that the model undervalues them and treat their value as a floor in the future-capital axis, leaning on pick and asset-point values rather than raw young-player ratings. Surface a warning so these numbers are read with the bias in mind.
- Selling legs: when a leg has Minnesota shedding a veteran (Minnesota as seller), flag it as outside the validated Minnesota-acquisition lane. The legality is solid, but the acceptance and value on those legs carry the un-calibrated caveat from the scope doc.
- Always report which legs are in lane and which are not, so the read stays honest.

## 8. Suggested build order

1. Core first: two-leg state-carry (cap and roster), incoming-return modeling, hard-cap propagation, and end-state scoring. Validate before going further.
2. Then three-way salary routing.
3. Then the hand-specified-chain path with relaxed untouchables, plus the honesty flags.
Extend to N legs once two-leg is solid.

## 9. Validation and deliverables

- Self-tests with hand-checkable outcomes: a two-leg shed-then-spend that is legal and opens the room you expect; a chain that trips the hard cap on leg one and correctly blocks an over-apron leg two; a three-way routing case like routing Randle to a team that wants him while its expirings go to a rebuilder.
- One worked example end to end: a real in-lane two-leg draft-night reshape, shed Randle for a real player to open room, then spend that room on a second acquisition while keeping Gobert, reported with the end-state two-axis read.
- Report what is new code versus what reuses existing pieces (evaluate_move, partner_acceptance, tier2_full, dump_absorbers), and flag the effort and blast radius before building, so we know the cost.

## 10. What it unlocks

Once it works, the engine powers the draft-night reshape content: in-lane multi-trade chains scored on the end-state two axes, title now versus future, the three philosophies rebuilt on real, chained, model-validated moves instead of single deals.
