# Piece skeleton: Kuminga and the Wolves' offseason

**Status:** drafted 2026-08-27, before the Green situation resolved. Every number carries its run ID in brackets. Nothing here may be quoted that is not on `outputs/final_numbers.md`.

**The standing caveat that opens everything:** Kuminga has agreed, not signed. NBA.com's tracker separates "multiple reports" from "officially announced" and puts him in the first bucket; the league transaction log has no row. If that changes before publication, promote the status and re-verify the dollars.

---

## 1. The deal that could not happen

**The lede.** Minnesota agreed to terms with Jonathan Kuminga on a Wednesday in late August and then could not sign him for the money they had agreed to pay him. They were **$1,999,829 short.** It took them three days and a trade to find it.

**Start with the basis, because the basis is the story.** The number that governs an apron is not a team's payroll. It is **Apron Team Salary**, which takes team salary, removes free-agent cap holds, and **adds back unlikely bonuses**, the incentives a player did not earn last season and so is not presumed to earn this one. Minnesota carries **$1,750,000** of them: **$1,000,000 for Jaden McDaniels and $750,000 for Donte DiVincenzo** `[cap_reconciliation_20260827T191905Z]`. They do not count against the cap or the tax. They count against the apron.

The arithmetic:

- Contracted 2026-27 salary, 13 players: **$215,871,829**
- Plus unlikely bonuses: **$217,621,829** ← *the apron basis*
- Add Kuminga at the taxpayer mid-level exception: **$223,685,829**
- The second apron: **$221,686,000**
- **They were $1,999,829 over.** `[same]`

*Independent agreement.* Spotrac publishes Minnesota's second-apron room as **$4,064,172**. We compute **$4,064,171**, one dollar apart, the dollar being McDaniels at $26,200,000 there against $26,200,001 in Basketball-Reference, SalarySwish and our own book.

Using the taxpayer MLE hard-caps a team at the second apron for the rest of the league year, and the test is where you sit **after** the signing, not before.

**The loophole, before a reader with a calculator finds it.** An exception may be used partially. Minnesota sits $4,064,171 below the second apron, so a first-year salary of exactly that fits and lands team salary on $221,686,000 to the dollar, which is legal because the hard cap prohibits *exceeding* the apron rather than reaching it `[lede_loophole_20260827T191752Z]`. But that is only **67% of the exception**, and it costs Kuminga **$4,099,649** across the two years. This is no longer a rounding-error loophole. It is a $4M pay cut on top of the one he already took, which is why nobody is going to take it.

**Hence Saturday.** Josh Green's $14,679,012 is what had to move.

**And Saturday was a real deadline, not a convenience.** A stretched salary only reaches the current season if the player clears waivers, waivers run 48 hours, and the cut-off is August 31. Hoops Rumors put it flatly on the morning of the 29th: "Today is the deadline to waive and stretch contracts ahead of the upcoming season." Minnesota had one working day.

**And then they did neither branch.** On Saturday, August 29, Minnesota traded Josh Green and cash to Utah for **Cody Williams** ($6,015,600) and **John Konchar** ($6,165,000), and waived Konchar the same afternoon, stretching him across three seasons at **$2,055,000 a year**. They did not trade Green to clear the money. They did not stretch Green. **They traded Green for a contract they could stretch, and stretched that instead.**

That is the move the model never considered, and it is worth stopping on, because it is the most front-office thing in the whole sequence. A salary dump normally costs a pick. This one did not. **No draft pick and no swap changed hands in either direction.** Minnesota's price was cash, plus $2,055,000 a year of dead money for three years, and in exchange for absorbing that they came away with the **tenth pick in the 2024 draft** on a rookie contract with a 2027-28 club option.

**What we modelled against what they did** `[green_resolution_20260903T225927Z]`:

| | Apron salary, Kuminga signed | vs first apron | vs second apron |
|---|---|---|---|
| Modelled: trade Green, minimum 14th man | $210,364,580 | $1,349,580 over | $11,321,420 under |
| Modelled: stretch Green | $215,257,584 | $6,242,584 over | $6,428,416 under |
| **Actual: trade Green, stretch Konchar, keep Williams** | **$217,077,416** | **$8,062,416 over** | **$4,608,584 under** |

**They spent $6,712,836 more hard-cap room than the cheapest route available to them, and they spent it on a player.** The modelled trade branch filled the fourteenth slot with a minimum body. Minnesota filled it with Cody Williams and ate Konchar's dead money to do it. That is a choice, not an accident, and section 5 is where it gets priced.

**The chain, end to end** `[cap_canonical.json, post_trade]`:

- Pre-trade apron basis: **$217,621,829**
- Out, Josh Green: **-$14,679,012**
- In, Cody Williams and John Konchar: **+$12,180,600**
- Waive Konchar, stretch over three seasons: **-$4,110,000**
- Post-trade: **$211,013,416**
- Add Kuminga at the full exception: **$217,077,416**
- Room under the second-apron hard cap: **$4,608,584**

*Independent agreement, and this is the strongest check in the piece.* Spotrac publishes two apron figures per team that are computed separately: first-apron space and second-apron space. Minnesota's are **-$1,998,416** and **$10,672,584**. Both imply an Apron Team Salary of **$211,013,416**. So does the itemised breakdown at the foot of their own page. **All three agree with ours to the dollar, at zero difference.**

**Minnesota is a first-apron team for 2026-27**, $8,062,416 over that line, so the four first-apron restrictions apply: no sign-and-trade acquisition, no bi-annual exception, no use of prior-year trade exceptions, and tighter salary matching. The last has a price worth naming: Minnesota holds **$17,350,158** of live prior-year trade exceptions, the Mike Conley $10,774,038 expiring 2/3/2027 and the Rob Dillingham $6,576,120 expiring 2/5/2027, and being over the first apron makes them unusable.

**And the hard cap did not go away when the signing cleared.** The taxpayer mid-level hard-caps Minnesota at the second apron for the whole league year. They have **$4,608,584** of room under it, which is roughly one veteran-minimum addition plus change, and every in-season move has to fit inside it.

*On the tax, and note the basis changes.* Tax is charged on **regular team salary, which excludes unlikely bonuses** unless they are actually earned. On that basis the trade branch owes roughly **$8.7M (est)** and the stretch branch roughly **$17.0M (est)**, and stretching leaves $4,893,004 of dead money in each of the next two seasons, the second landing in Edwards's walk year.

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
| Dosunmu retained (on-court) | -0.40pp | **negative under all four** |

**One note on the magnitudes.** Applying the slot rule cut every number in this table, by between a quarter and three quarters, and moved none of their signs. The looser rule flatters big effects by letting minutes flow to whoever the model likes best. Read the sizes here as the conservative version and the signs as the finding.

**What is missing from that table, and why.** The first draft of this section had "Randle out, +0.19pp, positive under all four". Applying the slot rule to him as well as to Kuminga takes it to **+0.07pp with no agreed sign** `[compare_slot_shapley_20260827T134414Z]`. It was the only player verdict that moved, and it does not come back. Letting Randle go is not a thing we can say helped. Two bundles moved too, the depth group and the other departures, so neither gets a sign either.

The rule being applied is worth stating once in the piece: **if a verdict changes when we change a modelling assumption, it is not a finding, and it does not get quoted.** Four of nine survived that test.

**The sentence this section is tempted by, and cannot have.** Hold the injury out and the remaining transactions are positive under all four views here, but under the looser minutes rule the same total is mixed. It flips, so it does not get a sign.

**The fallback sentence does not survive either, so do not write it.** "The Achilles is the largest negative on the board" is wrong three ways. It is the largest under **one of four views** (box). Under RAPM it is the **smallest** of the four negatives. And on the mean it ranks **third**, behind re-signing Dosunmu and behind the depth bundle `[compare_slot_shapley_20260827T134414Z]`.

**What is true, and it is enough.** The Achilles is negative under all four views, it survives the slot rule, and **it is the only item on the list nobody chose.** Every other line is a decision somebody made. That is the point, and it does not need a superlative to land.

**The uncomfortable one, which now stays in. It is two separate claims and the piece must not blur them.**

**(a) The cap arithmetic, which needs no model at all.** The honest way to see this is two finished rosters, both legal, both fourteen men, both with Kuminga on them `[dosunmu_final_states_20260827T154349Z]`:

| | Payroll | vs the tax line | Est. tax | Kuminga at | Josh Green |
|---|---|---|---|---|---|
| **What happened** | $208,614,817 | $8,186,817 over | ~$13.1M | $6,064,000 | traded away |
| **Dosunmu not re-signed** | $209,015,000 | $8,587,000 over | ~$13.8M | up to $10,004,516 | **kept** |

**Look at the first three columns before the last two.** They are nearly the same. Both rosters are taxpayers, both sit around $209M, both owe about $13M, and the counterfactual is very slightly the *more* expensive of the two. **Re-signing Ayo Dosunmu did not cost Minnesota money.** What it cost is two things, and neither of them is Josh Green the player: **the asset cost of having to move Green**, which is now known and was smaller than any branch assumed `[green_resolution_20260903T225927Z]`, plus **about four million dollars of Kuminga's first-year ceiling**.

**What the re-signing bought, then, is two things.**

**First, it is why Josh Green had to be moved.** Be precise about what is lost here, because it is not the player. Green was **the matching salary in the LaMelo Ball trade**, on an expiring one-year deal at $14,679,012, and priced on the floor his departure is a wash: keeping him grades **mixed across the four views, -0.48 to +0.01pp** `[green_kept_20260827T154636Z]`. Nothing in this project says Minnesota will miss him.

**What the re-signing removes is keeping him, and it makes every other exit cost something.** With both contracts on the book, adding Kuminga at the full taxpayer exception gives $217,621,829 + $6,064,000 = $223,685,829, which is $1,999,829 past the second apron and cannot be done, so **Green cannot be kept**.

He *could* be traded for salary, and that is the exit Minnesota took. There was **$13,071,183 of room under the second-apron hard cap** at a fourteen-man roster `[cap_branches_20260827T023847Z]`, so a real player could come back, and one did: Minnesota absorbed **$12,180,600** of incoming salary, just inside that ceiling. The cost was the tier. **Any meaningful incoming salary made Minnesota a first-apron team for the season**, with the four restrictions section 1 lists, and they now sit **$8,062,416** over that line.

**The part the piece predicted wrong, and it is worth saying so.** This section anticipated two exits, both charged for: a pure dump costing "whatever pick or swap has to be attached to move a $14.7M expiring contract for nothing", or a trade back costing the apron restrictions. Minnesota found a third. **They paid no pick and no swap at all**, took the apron hit they were taking anyway, and turned the dump into an acquisition. The only asset cost is **$2,055,000 a year of Konchar's dead money for three seasons**, $4,110,000 of which lands in 2027-28 and 2028-29, and against that they hold a 22-year-old former top-ten pick with a club option. **A $14.7M expiring contract was not the liability this piece assumed it was**, and the reason is that Utah wanted the player.

Dosunmu's $19,310,345 is larger than the $1,999,829 overage by $17,310,516, so **without him, Green stays and neither exit is needed.** The Saturday deadline in section 1 traces back to a contract agreed in June.

**And the two sit three days apart.** Minnesota agreed to re-sign Dosunmu on the night of Monday **June 22**. It agreed the trade that brought Ball and Green in, and sent Naz Reid out, on Thursday **June 25**. The league processed both on **July 10**, which is why the transaction log dates them identically and cannot be used to order them `[ESPN, Charania 06.23 and Youngmisuk 06.25]`.

*Handle the sequence carefully in the writing.* Reported three days earlier is not decided three days earlier. A four-team trade is negotiated over weeks and both were certainly live at once. The piece can say the Dosunmu agreement was reported first. It cannot say Minnesota chose Dosunmu and then took Green on anyway.

**Second, it cut Kuminga's first-year ceiling by about four million dollars.** Without Dosunmu, a replacement guard on a veteran minimum puts Minnesota at $199,010,484 across thirteen players, $10,004,516 under the first apron. **That distance is the ceiling on Kuminga's first-year salary**, because using the non-taxpayer mid-level hard-caps a team at the first apron. Note what that means: the exception is worth $15,044,000, but the whole of it was never spendable. The right phrasing is **up to $10,004,516 at a full roster**, against the $6,064,000 he actually got. A cheaper replacement lifts it to $11,095,516; paying him $8M instead would leave room for a fifteenth man, and $9M would not `[same]`.

**And this is why the weight lands on this contract and not another.** Four moves are tangled together here, and three of them were not really separable choices. **Ball was the trade. Green was its matching salary. Kuminga was the target. Dosunmu was the optional one.**

**(b) The on-court finding.** Against the guards actually on the roster, Dosunmu's minutes grade **negative under all four views, -0.13 to -0.76pp** `[shapley_20260827T134406Z, QUOTABLE AS BAND]`. This was the verdict most likely to be an artifact of handing his minutes to better players; constraining them to the guard rotation moves it a tenth of a point and does not touch the sign.

**One sentence on what kind of claim each is, because they are not the same kind.** The cap half is arithmetic on contracts and CBA thresholds, and it is true regardless of what anyone thinks of the player; **the on-court half is a model claim about impact metrics**, and it inherits every assumption those metrics carry, including the minutes rule in the methods note.

**And the two counterfactuals are different, which is why they do not add up.** The on-court number prices **losing him for nothing**: Minnesota was over the cap, an over-the-cap team has exceptions rather than room, and his salary was never convertible into a better guard. The cap number prices something else, **the exception and the roster spot his absence would have freed**, which is about a different player at a different position. Reported together they describe a cost; neither one, nor both, establishes what Minnesota should have done instead.

---

## 5. The structural risk

The risk is not the player. It is the contract shape.

Because a declined option year is never "covered by a player contract" under the CBA, opting out after one season leaves Minnesota with **Non-Bird rights only**, capping a re-signing start at 120% of his year-two salary: **$7,640,640** `[league_year_constants, verified from CBA text]`.

The first-pass option model puts **P(he opts out) at 0.50 to 0.80** and **P(Minnesota can keep him) at only 0.28 to 0.54** `[player_option_20260827T124131Z, band, labelled first pass]`.

**And there is no way to negotiate around it during the season, which we checked rather than assumed.** A two-year contract is **categorically ineligible to be extended**. The waiting period is the second anniversary of signing for three- and four-year deals and the third for five- and six-year deals, and beneath that "a contract that only covers one or two seasons is ineligible to be extended" `[Hoops Rumors glossary, veteran contract extension; CBA Guide extensions table]`. Kuminga's second anniversary would arrive in the summer of 2028, after the deal has already expired. **Minnesota cannot buy the leverage back in February.** There is no extension, and renegotiation needs cap room a team $8M into the tax does not have.

**But the retention door is not one door, and the piece had only described one of them.** Everything above is the branch where he **opts out**. If he instead **picks up the option and plays 2027-28**, Minnesota reaches the summer of 2028 with two consecutive seasons of his service and therefore **Early Bird rights**, which allow the greater of **175% of his prior salary, $11,142,600**, or 105% of the league-average salary, over up to four years `[Hoops Rumors glossary, Early Bird rights]`. That is a materially better position than the $7,640,640 Non-Bird cap.

So the structure is: **opt out and Minnesota is nearly powerless; opt in and Minnesota is fine.** Which is exactly why the option year, and his camp's stated reason for wanting it, is the whole risk.

*One thing to verify before this ships.* Sources are explicit that Early Bird needs two consecutive seasons without changing teams as a free agent, and are **not explicit that a year played on an exercised player option counts** toward it. It plainly should, since exercising an option continues the same contract rather than passing through free agency, but it is not confirmed in the sources consulted. Flagged CONFIRM in `gaps_remaining.md`.

**And his camp said the quiet part out loud.** The stated reason for taking roughly half the Lakers' annual money was to get back to free agency in 2027. The model prices that event at a coin flip or worse; the player is describing it as the plan.

**So the honest framing of the deal:** Minnesota is buying one year of a **23-year-old who turns 24 in October** at half his market price, the most likely single outcome is that they lose him for nothing, and there is no mechanism available to them in between.

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

**What we know.** The signing is a bargain against the only real market price we can observe, and all four views agree Atlanta was right to let him go at $24.3M. And they could not sign him to the full exception until Green moved: the gap was $1,999,829, and closing it any other way meant a 14-man roster frozen for the season.

**What we believe.** Against the player who would most likely take those minutes, Kuminga is worth something positive to Minnesota's title odds under every view we have. Two words in that sentence are load-bearing. **Most likely**, because promote a different forward into the slot and the four views stop agreeing. And **those minutes**, because the case rests on the alternative being poor, not on the player being good.

**What we cannot say.** Whether the offseason as a whole helped. The four views disagree on the sign, and the measurement error is as large as the effect. Anyone who tells you the Wolves' title odds went up or down by a specific amount this summer is reporting their choice of impact metric, not a fact about the team.

**The closing thought, if one is wanted:** they spent the summer converting a frontcourt that worked into a frontcourt that is cheaper and younger and less proven, and the thing that actually moved their season was a non-contact injury in Game 4 of a first-round series.

---

## Methods note

Four impact views (in-house consensus, RAPM, box score, DARKO) are carried separately end to end and never averaged; a claim ships only if all four agree on the sign. Title probabilities come from a bracket simulation calibrated against three prior seasons of betting markets. Minutes are allocated by a league-wide rank score with a per-player ceiling of prior load plus three, capped at 36.

**The four views are not four independent measurements, and the piece should not imply they are.** They are built from overlapping data: the consensus view is constructed partly *from* the RAPM and box views, and all four ultimately read the same possessions and the same box scores. Four-way agreement is therefore weaker evidence than four independent instruments agreeing would be. It is a check that a finding does not depend on one modelling choice, not a confidence interval, and it is used here only to decide whether a claim gets a sign at all.

**The noise floor, and how much it eats.** The machinery has its own error: Monte Carlo variation in the simulated seasons plus interpolation on the f-curve grid. At Minnesota's odds level that combines to a materiality floor of **0.24 to 0.45 percentage points** depending on the view `[noise_floor_20260827T194635Z]`. Re-testing every verdict against it, requiring an agreed sign *and* every individual view clearing the floor, **only two of eight survive**, and only one of those is a player move: LaMelo Ball's arrival. Reid out, Dosunmu retained and the DiVincenzo injury all have an agreed sign whose smallest view is inside the noise.

**That floor is our compute budget, not a law of nature.** Monte Carlo dominates it by roughly five to one over interpolation, and Monte Carlo error falls with the square root of the simulation count. The current figures come from 20,000 simulations per fork per seed. Ten times that would cut the floor by about a factor of three and several of these verdicts would clear it. Until that run happens, the honest statement is that the piece cannot resolve effects this small, not that the effects are zero.

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

## Appendix: keeping Josh Green, priced on the floor

Both cap branches assume Green leaves, which is a cap assumption that was never asked as a basketball question. Priced as one coalition under the slot rule, **keeping him is MIXED: -0.48 to +0.01pp, mean -0.18pp** `[green_kept_20260827T154636Z]`. Only RAPM is positive and it is positive by a hundredth of a point.

So the piece **does not** attach an on-court cost to the salary dump. If anything three of the four views think the minutes are better spent elsewhere, but they do not agree, so nothing is claimed. Two caveats travel with it: the pooled rule hands Green 13.3 minutes and takes them proportionally from the whole guard group, Edwards included, which is not how a rotation actually works; and his impacts run from -0.22 (box) to -2.00 (DARKO), a spread wide enough that the disagreement here is about him, not about the method.

---

## Appendix: the Dosunmu intermediate figures

The final-state table in section 4 is the version that should be read. These are the intermediate numbers behind it, kept so the arithmetic can be checked `[dosunmu_cap_20260827T152542Z]`:

| Roster | Payroll | vs the tax line |
|---|---|---|
| 13 players, Dosunmu on the book, no Kuminga | $215,871,829 | $15,443,829 over |
| 12 players, Dosunmu gone *(not a legal roster)* | $196,561,484 | $3,866,516 under |
| 14 players, vet-min replacement + rookie min | $200,368,484 | $59,516 under |
| 14 players, vet-min replacement + vet min | $201,459,484 | $1,031,484 over |

The 12-man line is why the intermediate figures are here rather than in the piece: read alone it suggests Minnesota could have ducked the tax entirely, and a legal roster with Kuminga on it lands them back at roughly $209M either way. **A replacement guard is charged the two-year minimum, $2,449,000**, when a veteran with three or more years signs a one-year minimum deal; the league pays the difference against the $3,877,000 he earns. Tax figures are estimates; the bracket rates are flagged for confirmation in the constants file.

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
