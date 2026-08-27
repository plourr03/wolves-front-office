# Piece skeleton: Kuminga and the Wolves' offseason

**Status:** drafted 2026-08-27, before the Green situation resolved. Every number carries its run ID in brackets. Nothing here may be quoted that is not on `outputs/final_numbers.md`.

**The standing caveat that opens everything:** Kuminga has agreed, not signed. NBA.com's tracker separates "multiple reports" from "officially announced" and puts him in the first bucket; the league transaction log has no row. If that changes before publication, promote the status and re-verify the dollars.

---

## 1. The deal that cannot happen yet

**The lede.** Minnesota agreed to terms with Jonathan Kuminga on Wednesday and, as of Thursday, could not sign him for the money they had agreed to pay him.

The arithmetic, and it is close enough to be the story:

- Contracted 2026-27 salary, 13 players: **$215,871,829** `[cap_reconciliation_20260827T123553Z]`
- Add Kuminga at the taxpayer mid-level exception: **$221,935,829** `[same]`
- The second apron: **$221,686,000** `[league_year_constants, verified against NBA.com]`
- **They are $249,829 over.** `[eval_signing_20260827T123804Z]`

That is less than a rookie-minimum contract. Using the taxpayer MLE hard-caps a team at the second apron for the rest of the league year, and the test is where you sit **after** the signing, not before. So the exception was available to them (they sit in the first-apron tier) and impossible to fit **in full**.

**Now the loophole, before a reader with a calculator finds it.** An exception can be used partially. Minnesota sits **$5,814,171** below the second apron, so a first-year salary of exactly that fits, lands team salary on **$221,686,000 to the dollar**, and is legal, because the hard cap prohibits *exceeding* the apron rather than reaching it `[lede_loophole_20260827T134245Z]`. That is 95.9% of the exception. So the precise claim is not that they could not sign him. It is that **they could not sign him to the full taxpayer mid-level exception**, and the gap is 4.1% of it.

Two things close the loophole, and both belong in the piece:

- **It costs Kuminga $512,149** over the two years, at the 5% maximum raise `[same]`. Someone has to volunteer that, and the player who just turned down the Lakers to protect his own optionality is not the obvious volunteer.
- **It freezes the roster at 14 for the season.** At exactly the apron, Minnesota cannot sign a fifteenth man, take back a dollar in any trade, or replace an injured player. Carry a fifteenth on the rookie minimum and Kuminga's ceiling drops to **$4,456,171**, 73.5% of the exception `[same]`.

So the Green move is not only about the last $249,829. It is about being able to field a normal roster afterwards.

**Hence Saturday.** August 29 is the last day to waive a player and stretch his 2026-27 salary. Josh Green's $14,679,012 is what has to move.

**The two branches, at a legal roster** `[cap_reconciliation_20260827T123553Z]`. "Legal" means the 14-man floor: CBA **Article XXIX, Section 2(a)** requires 14 or 15 players on the Active and Inactive Lists through the regular season, and **Section 2(b)(i)** allows 12 or 13 for no more than two consecutive weeks at a time and 28 days in total `[CBA text; cbaguide.com]`:

| | Team salary | vs first apron |
|---|---|---|
| Trade Green, 14 players | $208,614,817 | **$400,183 under** |
| Stretch Green, 14 players | $213,507,821 | $4,492,821 over |

Two things fall out of that $400,183. A **fifteenth** man on a rookie minimum puts the trade branch $957,817 over the first apron by itself. And **any player coming back in a Green trade crosses it**, because the smallest contract that can legally come back is $1,358,000 and the room is $400,183. The "pure salary dump" is not one option among several. It is the only version that keeps them under the first apron.

*Optional colour:* stretching costs roughly $10.9M more in tax in 2026-27 alone and leaves $4,893,004 of dead money in each of the next two seasons, the second of which lands in Edwards's walk year.

---

## 2. The price, and the market

**The claim that survives everything:** all four impact views agree Atlanta was right to decline his $24.3M option `[eval_signing_20260827T123804Z, QUOTABLE]`. That is the frame. He was not worth $24.3M and the team that had him said so.

**What he is worth.** Four views, four answers: $11.5M (in-house consensus), $11.7M (RAPM), $6.0M (box score), $2.7M (DARKO) `[eval_signing_20260827T123804Z, band]`. He is being paid $6,064,000.

**And here is the outside check, which is the best evidence in the piece.** Kuminga turned down a reported $12 million-plus a year over three years from the Lakers, via sign-and-trade `[ESPN, Anthony Slater]`. Chicago and Portland also bid; no terms reported.

The two possession-based views land **within four percent of that real bid**. The box and DARKO views are off by a factor of two and four. `[eval_signing_20260827T123804Z, QUOTABLE]`

*The caveat travels with the number.* The Lakers figure was a **sign-and-trade**, which is a different instrument from a taxpayer-exception signing: the price includes what Golden State had to be paid to cooperate and what Los Angeles was willing to hard-cap itself to do. It is a real number and it is the only real number we have, but it is not the same good being priced.

That is the first thing in this project that is **consistent with** the possession-based views over the box-based ones using something outside the model. One bid is not an adjudication. It is one observation, it is the only one we have, and it points the same way twice.

**Why he took less.** His camp's stated reason is control: a shorter prove-it deal that lets him reach free agency again in 2027 `[ESPN]`. Hold that thought for section 5.

---

## 3. The slot he inherits

**Start with what the tape says, not the model.** Over 2,253 possessions last season, Naz Reid next to Rudy Gobert was **+6.83** net. Julius Randle next to Gobert, over 3,443 possessions, was **+3.10** `[lineup_evidence_20260827T024925Z]`. Minnesota kept Gobert and moved both. Kuminga inherits that slot.

*(Descriptive on/off, not an effect. Say so.)*

**The Kuminga warning, stated honestly.** His on/off flips sign between his two 2025-26 teams: **-6.53 at Golden State** over 971 possessions, **+2.90 at Atlanta** over 1,077 `[lineup_evidence_20260827T024925Z]`. Neither sample is an effect. But the shot profile moves coherently with it: his three-point rate went from 27.3% at Golden State to 35.9% at Atlanta and his accuracy went **up**, 32.1% to 34.6%. In the playoffs the rate rose again to 40.0% and the accuracy collapsed to 20.8% `[same]`.

**Now the model, asked the right question.** This is the section's payoff and it needs the setup above to land.

If you ask "what happens if Kuminga is not here" and let his minutes go anywhere, they flow to Gobert and Edwards and Ball, and he looks replaceable. That counterfactual is not available to a coach: those minutes are already spoken for.

Constrain his minutes to players actually eligible at the 4, and the man who fills the slot is **Terrence Shannon Jr.**, whose consensus impact is -2.18. Against that alternative Kuminga is worth **+0.14 to +1.23 percentage points of title probability, positive under all four views** `[slot_analysis_20260827T131606Z, QUOTABLE AS BAND]`.

**That is the case for the signing.** Not that he is good in the abstract. That the alternative on this roster is bad.

**Two facts to set this up, because they are why the slot rule bites at all.**

First, Minnesota is the most big-heavy team in the league. Their centres played **53.7 minutes a game last season, first of thirty, against a league mean of 33.8** `[build_rotations_20260827T133313Z]`. That is not a rounding difference. It is a structurally different roster shape, and it is why "who can actually take these minutes" is a real constraint here rather than a technicality.

Second, and more starkly: read positional eligibility strictly, counting only players listed Forward or Forward-Centre, and **23.3 of Kuminga's 26 minutes have nobody to go to**. Behind Trey Lyles there is no eligible 4 on the roster `[slot_robustness_20260827T133141Z]`. Minnesota did not sign a power forward into a crowded room. They signed one into an empty one.

**Now, exactly how far the claim goes, which is not as far as it first looks.** The answer depends on naming the man who takes the minutes, so we re-priced it under five different answers `[slot_robustness_20260827T133141Z]`. It holds against Shannon and it holds if Jaden McDaniels slides down to the 4. It does **not** hold under three others: Trey Lyles promoted into the role (mixed, -0.91 to +0.68), Joan Beringer promoted into the role (negative under all four), or a strict reading of eligibility that counts only players listed Forward or Forward-Centre.

So the claim is **against the most likely internal alternative**, never "against any internal alternative". Two of those three failures are worth a sentence each rather than a hedge:

- The Beringer version says a Kuminga-to-Beringer swap is a downgrade under every view. That is a finding about a rookie centre, not evidence against Kuminga.
- The strict-eligibility version leaves **23.3 of his 26 minutes with nobody to give them to**, which is the most revealing result of the five. Read literally, Minnesota does not have a backup power forward. That is closer to an argument for the signing than against it.

The one that genuinely narrows the claim is Lyles, because a coach could actually do that, and the four views split on whether it would be worse.

---

## 4. What moved the offseason

**Only the signs that survived.** Exact Shapley over 256 coalitions, minutes ceiling applied, contributions summing to the whole with no residual. Every move is priced under the same slot rule section 3 uses: a departing player's minutes go to his own position group, not to whoever the model likes best `[shapley_20260827T134406Z]`.

| Move | Mean | Verdict |
|---|---|---|
| LaMelo Ball in | +0.67pp | **positive under all four views** |
| Reid out | -0.26pp | **negative under all four** |
| DiVincenzo's Achilles | -0.35pp | **negative under all four** |
| Dosunmu retained at $19.3M/yr | -0.40pp | **negative under all four** |

**What is missing from that table, and why.** The first draft of this section had "Randle out, +0.19pp, positive under all four". Applying the slot rule to him as well as to Kuminga takes it to **+0.07pp with no agreed sign** `[compare_slot_shapley_20260827T134414Z]`. It was the only player verdict that moved, and it does not come back. Letting Randle go is not a thing we can say helped. Two bundles moved too, the depth group and the other departures, so neither gets a sign either.

The rule being applied is worth stating once in the piece: **if a verdict changes when we change a modelling assumption, it is not a finding, and it does not get quoted.** Four of nine survived that test.

**The sentence this section is tempted by, and cannot have.** Hold the injury out and the remaining transactions are positive under all four views here, but under the looser minutes rule the same total is mixed. It flips, so it does not get a sign.

**The fallback sentence does not survive either, so do not write it.** "The Achilles is the largest negative on the board" is wrong three ways. It is the largest under **one of four views** (box). Under RAPM it is the **smallest** of the four negatives. And on the mean it ranks **third**, behind re-signing Dosunmu and behind the depth bundle `[compare_slot_shapley_20260827T134414Z]`.

**What is true, and it is enough.** The Achilles is negative under all four views, it survives the slot rule, and **it is the only item on the list nobody chose.** Every other line is a decision somebody made. That is the point, and it does not need a superlative to land.

**The uncomfortable one, which now stays in. It is two separate claims and the piece must not blur them.**

**(a) The cap arithmetic, which needs no model at all** `[dosunmu_cap_20260827T152542Z]`. Ayo Dosunmu is on $19,310,345 this season. With him on the book, Minnesota is **$15,443,829 over the tax line**, facing a bill of roughly **$30.9M (est)**.

Take his salary off and put a legal team back on the floor, which means a replacement guard at the veteran minimum plus one more contract to reach the 14-man roster the CBA requires. On a one-year deal a veteran with three or more years of service is charged the two-year minimum, **$2,449,000**, and the league pays the rest. That team lands **within about a million dollars of the tax line either side**: $59,516 under it if the last spot goes to a rookie minimum, $1,031,484 over it if it goes to another veteran `[same]`.

So the accurate version is not that his contract makes them a taxpayer outright. It is that **his contract is the difference between roughly level with the tax line and $15.4M past it.**

It also set the size of the tool they signed Kuminga with, and this is the part that connects to the lede. Without him, that legal roster sits **$7.56M to $8.65M under the first apron**, where the non-taxpayer mid-level lives. Using that exception hard-caps a team at the first apron, so the whole $15,044,000 was never spendable either. What was actually available was **up to $7.6M to $8.6M at a full roster, against the $6,064,000 taxpayer exception they had** `[same]`. Call it an extra $1.5M to $2.6M of buying power to chase a forward.

**(b) The on-court finding.** Against the guards actually on the roster, Dosunmu's minutes grade **negative under all four views, -0.13 to -0.76pp** `[shapley_20260827T134406Z, QUOTABLE AS BAND]`. This was the verdict most likely to be an artifact of handing his minutes to better players; constraining them to the guard rotation moves it a tenth of a point and does not touch the sign.

**One sentence on what kind of claim each is, because they are not the same kind.** The cap half is arithmetic on contracts and CBA thresholds, and it is true regardless of what anyone thinks of the player; **the on-court half is a model claim about impact metrics**, and it inherits every assumption those metrics carry, including the minutes rule described in the methods note.

**And the two counterfactuals are different, which is why they do not simply add up.** The on-court number prices **losing him for nothing**: Minnesota was over the cap, an over-the-cap team has exceptions rather than room, and his salary was never convertible into a better guard. The cap number prices something else entirely, **the exception his absence would have unlocked**, which is a tool for signing a different player at a different position. One says the guards behind him are better than he is. The other says the money bought tax exposure and a smaller exception. Reported together, they describe a cost; neither one, nor both, establishes what Minnesota should have done instead.

---

## 5. The structural risk

The risk is not the player. It is the contract shape.

Because a declined option year is never "covered by a player contract" under the CBA, opting out after one season leaves Minnesota with **Non-Bird rights only**, capping a re-signing start at 120% of his year-two salary: **$7,640,640** `[league_year_constants, verified from CBA text]`.

The first-pass option model puts **P(he opts out) at 0.50 to 0.80** and **P(Minnesota can keep him) at only 0.28 to 0.54** `[player_option_20260827T124131Z, band, labelled first pass]`.

**And his camp said the quiet part out loud.** The stated reason for taking roughly half the Lakers' annual money was to get back to free agency in 2027. The model prices that event at a coin flip or worse; the player is describing it as the plan.

**So the honest framing of the deal:** Minnesota is buying one year of a **23-year-old who turns 24 in October** at half his market price, and the most likely single outcome is that they lose him for nothing.

---

## 6. The West, after everybody's summer

Every team's roster was rebuilt the same way and run through the same pipeline. Seventeen of thirty changed apron tier since June `[diff_team_state]`.

**Minnesota moves from fifth to sixth in the West** `[build_outputs_20260827T131629Z, directional]`, passed by the Lakers.

**The number to lead with here is not a title probability.** Minnesota's chance of finishing top six and skipping the play-in falls from **73% on the baseline to a band of 39% to 84%** across the four views `[seed_distribution, band]`. That band spans "comfortably safe" to "more likely than not in the play-in", which is the finding: the four views do not agree on whether this is a top-six team.

Title odds for the piece, as a band and never as a midpoint: **1.63% to 3.74%** after the offseason `[run_sim_20260827T124337Z, QUOTABLE AS BAND]`.

**And the honesty rail that belongs in the piece, not a footnote.** A three-season backtest of this calibration against the betting market puts its title-odds error at **1.4 to 2.3 percentage points** `[backtest_calibration_20260827T124932Z]`. Minnesota's entire four-view spread is 2.1 points. The measurement error is the same size as the thing being measured, which is why this piece quotes bands and refuses point estimates.

**The same backtest on win totals, which is the less flattering half and runs anyway.** Against actual results over those three seasons, this model missed by **8.80 wins on average. The betting market missed by 7.47** `[same]`. The market was closer in two of the three seasons and tracked actual wins better in all three. Nothing here is a claim to beat the market. It is a claim to be explicit about a set of assumptions, which is a different and smaller thing, and it is why every seed and title figure above is a band.

---

## 7. Verdict

Structure it as three claims of decreasing confidence.

**What we know.** The signing is a bargain against the only real market price we can observe, and all four views agree Atlanta was right to let him go at $24.3M. And they could not sign him to the full exception until Green moved: the gap was $249,829, and closing it any other way meant a 14-man roster frozen for the season.

**What we believe.** Against the player who would most likely take those minutes, Kuminga is worth something positive to Minnesota's title odds under every view we have. Two words in that sentence are load-bearing. **Most likely**, because promote a different forward into the slot and the four views stop agreeing. And **those minutes**, because the case rests on the alternative being poor, not on the player being good.

**What we cannot say.** Whether the offseason as a whole helped. The four views disagree on the sign, and the measurement error is as large as the effect. Anyone who tells you the Wolves' title odds went up or down by a specific amount this summer is reporting their choice of impact metric, not a fact about the team.

**The closing thought, if one is wanted:** they spent the summer converting a frontcourt that worked into a frontcourt that is cheaper and younger and less proven, and the thing that actually moved their season was a non-contact injury in Game 4 of a first-round series.

---

## Methods note

Four impact views (in-house consensus, RAPM, box score, DARKO) are carried separately end to end and never averaged; a claim ships only if all four agree on the sign. Title probabilities come from a bracket simulation calibrated against three prior seasons of betting markets. Minutes are allocated by a league-wide rank score with a per-player ceiling of prior load plus three, capped at 36.

**Why this piece reports signs and never rankings.** The four views agree far more often on direction than on size, and a ranking is a claim about size. The worked example is the DiVincenzo injury in the slot-aware run `[compare_slot_shapley_20260827T134414Z]`:

| View | Largest single negative | The injury | Its rank |
|---|---|---|---|
| consensus | depth bundle, -0.332 | -0.218 | 4th of 8 |
| RAPM | Dosunmu retained, -0.443 | -0.189 | 4th of 8 |
| box | **the injury, -0.356** | -0.356 | **1st of 8** |
| DARKO | Dosunmu retained, -0.758 | -0.627 | 3rd of 8 |

All four views agree the injury hurt. They do not agree it hurt most: it leads under one view, and under RAPM it is the *smallest* negative on the board. "The Achilles was the biggest blow of Minnesota's offseason" is the kind of sentence this data cannot support, while "the Achilles hurt, under every way we know how to measure it" is one it supports easily. That is the whole editorial rule in one example.

**Positional minute budgets are each team's own 2025-26 shape, not a league average.** For Minnesota that assumes a **double-big allocation the current roster cannot repeat**: last season's 53.7 centre minutes a game were Gobert plus Reid, and Reid is gone. The budget is the right choice for measuring what the departures cost, because it holds the shape fixed while the personnel changes, and it is the wrong choice for predicting how Finch will actually play this team. Read every Shapley figure here as "what these moves did to last season's shape", not as a rotation forecast `[build_rotations_20260827T133313Z]`.

---

## Appendix: the alternatives, and why none of them is quotable

The overnight run found that several power forwards who signed elsewhere this summer graded at or above Kuminga for the same money. Under the constraints agreed for this piece, **none of them survives**:

| Player | Salary | Why excluded |
|---|---|---|
| Josh Minott | $4.5M | posterior sd 2.10, above the 1.5 bar |
| Dean Wade | $9.0M | posterior sd 1.61, and above the exception anyway |
| Kenrich Williams | $5.0M | posterior sd 1.87 |
| Jaxson Hayes | $6.0M | listed Centre-Forward, not a 4 |
| Al Horford | $6.8M | listed Centre-Forward, and above the exception |

`[slot_analysis_20260827T131606Z]`

The honest summary is that the taxpayer-MLE market this summer contained forwards who *may* have graded better, and our uncertainty on every one of them is too wide to say so in print. That is worth one sentence in the piece at most, and it belongs nowhere near the verdict.
