# Wolves to a T: The 2026 Offseason Series

_Working outline. Eight pieces plus one standing methodology page. The spine of the series is a bookend: defend Rudy early, name his price last. The arc underneath it is the honest journey the analysis actually took, from "which star do we trade for" to "the toolbox is the trade."_

---

## Series standards (these apply to every piece)

- **Nothing publishes on assumption.** Every number traces to a public source or a documented model output. If the model output rests on an assumption (availability, a synergy uplift, a projected roster), the assumption is named in the text.
- **Ranges, not points.** Where the four views disagree, the published number is the range with the conservative anchor named. The winner's-curse rule applies to our own consensus.
- **Sourcing discipline on every trade claim.** Reported / Analyst / Speculative tags, same as the internal boards. A name with no sourcing is labeled speculation, including our own ideas.
- **The private source firewall.** Nothing learned from the off-record team source appears in any piece, in any form, including as unattributed framing.
- **Voice.** No em dashes. No AI-tell phrasing. Rigorous, accessible, honest about uncertainty. Cleaning the Glass / FiveThirtyEight register.
- **Every piece links the methodology page** instead of re-explaining the machine.

## Timing against the calendar

Draft is June 23-24. Free agency opens June 30, signings July 6. Suggested cadence:

- **Pre-draft (June 11-22):** Pieces 1, 2, 3, and ideally 4. These are the foundation and they age well.
- **Draft week to FA (June 23-29):** Pieces 5 and 6.
- **FA window (June 30 onward):** Pieces 7 and 8, refreshed against the live market the day each publishes.

**Refresh triggers for any piece:** the Giannis resolution, any Gobert or Randle reporting, the Dosunmu market, the draft itself, and any injury news on the named targets. The boards re-run on command; build the re-run into the publishing checklist.

---

## Piece 1: The Situation

**Working title:** "The Wolves' Offseason Is an Apron Decision Before It Is a Trade Decision"

**Thesis.** Before any name gets argued, the geometry decides what is possible: the tax line, the two aprons, the Dosunmu rule, and a thin pick stash. Establish the board every later piece plays on.

**Argument beats.** The 49-win, 6-seed season and the Spurs exit. The cap table and the threshold distances. The Dosunmu $58.5M-out rule and why it quietly shapes every trade. The exception toolbox (three TPEs, the MLE) and the apron lines that freeze it. The asset inventory: two clean firsts plus No. 28. The six-dimension needs read: creation first, shooting second, rim protection conditional on the bigs. DiVincenzo's Achilles widening the creation and shooting holes. The verified reporting climate: Connelly's "everything is on the table," the Gobert and Randle availability reporting, Ant's dissatisfaction.

**Receipts to show.** The cap and threshold table. The needs vector by exit scenario (S0 through S3). The asset inventory table. The reporting ledger with sourcing tags.

**Public sources.** ESPN/Bobby Marks for the cap figures and the Dosunmu rule. HoopsHype/Spotrac for salaries. The Athletic (Krawczynski) for the Gobert reporting. ESPN (Windhorst) for the Ant item. Cleaning the Glass / NBA.com for the season profile.

**Integrity guardrails.** Ant's item is dissatisfaction, sourced, not a trade request. Every availability claim carries its tag. The needs analysis is the model's, presented as such.

**Hook idea.** Open with the number $209.1M and the sentence: most of this offseason was decided before a single trade call, by a line the Wolves are $14M under.

---

## Piece 2: It's Not (All) Gobert's Fault

**Working title:** "It's Not (All) Gobert's Fault" (the parenthetical is load-bearing and honest)

**Thesis.** The discourse misprices Gobert because his value is box-invisible and his offensive context never existed in Minnesota. Both things are true at once: his limitations are real, and the delivery system that made him a weapon was never built here.

**Argument beats.** The measurement story: the box sees +1.5, the play-by-play system sees +2.5 with elite defense, the on-court math sees +5.8, and that spread IS the Gobert discourse in miniature. The Utah evidence, with the audit's self-corrections baked in: roll-man efficiency was ELITE THEN and is ABOVE-AVERAGE NOW (80th to 95th percentile in his Utah peak, 73rd in Minnesota), not "best in basketball" flat; on screen assists he LED THE LEAGUE in three of his six Utah starter seasons (2018-19, 2019-20, 2020-21) and was TOP-FOUR in all six (not every year, as an earlier draft had it), then led the entire league AGAIN in 2025-26; a number-one offense built on his screen gravity with three to six live-dribble passers. The Minnesota evidence: a top-10 offense once in four years, his roll-man volume cut 37% and his live-dribble feeders halved to one by 2025-26, defenses blitzing Edwards because the Gobert catch is not feared, the on/off gap with its confound stated. The honest other side: DARKO grades his offense genuinely negative, he is a finish-only non-creator (assist-to-pass 3 to 5%) so a thin delivery system has no fallback, the hands limitation was always managed rather than absent, and the team defense slipped to 10th this season for reasons that include the perimeter around him. The contradiction the audit prints rather than smooths: his DUNK volume held up (-8%) while his roll-man possessions fell 37%, so Minnesota never stopped feeding his rim gravity, it stopped running him as the half-court roll hub. The conclusion is calibration, not absolution: the case to keep him is real, and so is the case that he can replenish the war chest. This piece does not promise he stays. It corrects the price.

**Receipts to show.** The four-view table on Gobert. The Utah-vs-Minnesota usage audit (pending, below). The roll-man efficiency history. The screen-assist history. The Minnesota offense ranks by season.

**Input DONE.** The Gobert usage audit is built: `outputs/gobert_usage_audit.md` (scripts
`pull_gobert_usage.py`, `analyze_gobert_usage.py`, `check_gobert_ranks.py`). Headline: roll-man
3.27 to 2.06 per game (-37%), touches 59.5 to 44.3 (-25%), screen assists 6.26 to 4.63 (-26%),
meaningful PnR ball-handlers 4 to 2 (one in 2025-26), roll-man PPP held (1.31 to 1.24). Two honest
corrections to this outline printed in the audit: he did NOT lead the league in screen assists
every Utah year (3 of 6, top-four all six), and roll-man efficiency is "elite then, above-average
now," not "best in basketball" flat. The misuse claim publishes only as measured, and the
dunk-volume contradiction prints.

**Public sources.** NBA.com tracking and synergy play types. ESPN's roll-man reporting from the Utah years. Cleaning the Glass for the on/off and offense ranks. Basketball-Reference for the season record.

**Integrity guardrails.** Do not claim the team defense is top-tier every year; it was 10th in 2025-26 and Finch said so. The on/off figure carries its confound note. The misuse claim is measured or it does not run.

**Hook idea.** The same human being was the most efficient roll man in basketball and "a massive detriment catching out of the pick-and-roll." Same hands. Different passes.

---

## Piece 3: The Young Core Is a Plan, Not a Hope

**Working title:** "What Is Joan Beringer's Actual Ceiling?" with the Shannon section as the second act, or split into two shorter pieces if length demands.

**Thesis.** Beringer's future is mostly an opportunity decision the franchise controls, not a talent mystery. Shannon is a player, not a prospect, and on the right ladder that is good news.

**Argument beats.** How development cones work: thirty years of comparable players, distributions instead of predictions. Beringer's three branches: runway, groomed behind the starter, buried. The groomed finding: a young first-round big given real backup minutes behind an established starter reaches rotation-caliber rim protection at rates close to the handed-the-job track, which means the development question is answerable without trading anyone. The roster fact that makes him singular: Naz is a stretch big, so Beringer is the only internal rim answer the franchise has. Shannon on the bench-creator ladder: at his age the comps say his per-minute level is roughly his prime level, his upside is role rather than growth, and on that ladder a dependable bench scorer is a success and the Sixth Man tier is the ceiling win, roughly a one-in-four shot with run. The selection-bias caveat stated in print: minutes are not randomly assigned, the branch gaps are directional, not causal gospel.

**Receipts to show.** Both cones with branch distributions and the tier ladders. The comp-set construction (first-rounders only for Beringer, age-25 bench creators for Shannon). The groomed-branch table. The de-bias note.

**Public sources.** NBA.com / Basketball-Reference historical player-season data (the comp pool is public data, the construction is ours and the methodology page documents it). DARKO for the current-level reads.

**Integrity guardrails.** Cones are distributions of comparable outcomes, never forecasts of these two specifically; say so verbatim. The endogeneity caveat prints. The Shannon age framing is honest and kind: the piece argues he is valuable, not that he is finished.

**Hook idea.** Beringer played 1.6 minutes a night last season. Thirty years of players like him say that number, not his talent, is the whole question.

---

## Piece 4: The Star Autopsy

**Working title:** "Every Big Name Fails the Physical, and Each One Fails Differently"

**Thesis.** The sexy trades do not fail for one reason. Giannis fails on gettability, AD on durability, Kyrie on a knee, Morant on fit and flags, Trae on defense, Kawhi on age and the fact that nobody credible has reported him available. The failure mode is the story.

**Argument beats.** The risk-adjusted board and what break-even availability means. Giannis as the deliberate exception: the only positive risk-adjusted star, robust on all four views, the largest Spurs and OKC swings of anything tested, and the one you cannot count on acquiring, so the case against him is acquisition probability, never value. The AD referendum: the trade's verdict flips sign by metric, because it is literally a bet on whether you believe in box-invisible rim deterrence, and his 83% break-even against 49% actual availability closes it regardless. Kyrie as a medical decision, not a take: 43% break-even, biased-low 32% base because the model counts a rehab year as fragility, flips positive at a credible Year-2 ACL read of 45% or better, and the model defers to doctors. Morant negative even at full health. Trae's defense as a title-math veto. Kawhi's tag: Speculative, fan-driven, aging expiring.

**Receipts to show.** The risk-adjusted board with break-even and actual availability columns. The AD four-view sign-flip table. The Kyrie sensitivity ladder. The availability-methodology note (and its honest bias on discrete rehab cases).

**Public sources.** Games-played histories (Basketball-Reference). The reporting ledger for each name's actual availability sourcing. DARKO public values.

**Integrity guardrails.** Giannis is framed as a gettability failure, not a value failure; the data refutes the lazier version. Kyrie is framed as contingent, not dead. Kawhi's non-reported status prints. No injury speculation beyond the public record and the model's stated availability method.

**Hook idea.** Our model spent two weeks trying to talk itself into a star trade. Here is the autopsy of every attempt.

---

## Piece 5: The Point Guard Problem

**Working title:** "The Wolves Need a Point Guard. The Math Says Build One Out of Parts."

**Thesis.** The orchestrator the gut demands either does not exist at an acceptable price or failed the physical. The honest answer is a committee, and the committee is better than it sounds.

**Argument beats.** The hook is now coach-confirmed: on June 11, 2026 (KFAN, via Yahoo/ClutchPoints) Finch said directly the Wolves "definitely need another ball handler and playmaker" to take load off Edwards (31.4% usage, a career-high 21 games missed), which is Reported-tier confirmation of the needs vector's number-one dimension. The thesis the model tested: an elite pick-and-roll orchestrator unlocks Gobert, the Stockton-Malone, prime-Conley-Gobert, CP3-DJ pattern, quantified as a bounded synergy view rather than a hidden assumption. The results: Morant flat without the synergy and only positive with it, meaning his whole case is the partnership bet; Kyrie the cleanest fit on the board, killed by the knee; Trae vetoed by defense; Giddey not corroborated by the independent metric. The Conley lesson printed honestly: the backward-looking model rated a 39-year-old as a positive and the age-aware system said he is done, which is why the math now says Dosunmu is the better guard. The committee: re-sign Dosunmu, add a corroborated cheap guard (Mitchell, 54th in the league by DARKO on a $3M contract, shaken loose by OKC's roster crunch, or McBride, the contract-year squeeze rental), manage Conley's minutes down, and use pick 28 in a draft with real guards. The labeled INTERNAL branch, run next to the committee: Finch also floated Terrence Shannon Jr. on the ball alongside Edwards (conceding the prior off-ball usage was a misuse), so price it honestly. Shannon's actual PnR ball-handler history is below the meaningful-feeder bar (about 70 possessions projected, 0.951 PPP on a 41-possession 2025-26 sample with a plus-or-minus 0.32 band), and the role sits one rung above his cone's bench-creator ladder, so it is internal upside the coach likes and the data has not yet earned, not a substitute for adding a real feeder. The delivery-system addendum (`gobert_usage_audit.md`) counts him as a fourth, developmental feeder to watch, not a counted one.

**Receipts to show.** The synergy-view table across the orchestrator scenarios. The PG verdicts with reasons. The Conley/Dosunmu four-view inversion. Mitchell's DARKO line and surplus. The seller-motive tiers (forced selling versus informed selling, and why it matters).

**Public sources.** DARKO public values. NBA.com play-type data for the pick-and-roll framing. The historical pairings cited (Utah's offense ranks, the CP3-era lob data) from NBA.com and Basketball-Reference.

**Integrity guardrails.** Never claim the model found the point guard. The synergy uplift is a labeled, bounded sensitivity, never folded into a headline. The breakout names carry their sample-size intervals in print.

**Hook idea.** I wanted Tyrese Haliburton. The model heard me out, priced every version of him on the market, and handed me back a committee. It was right.

---

## Piece 6: The Ant Clock (recommended, formally optional)

**Working title:** "What Anthony Edwards' Frustration Actually Demands"

**Thesis.** The retention question is a trajectory question. No realistic move makes the Wolves a 9% title team this summer, which means the bar that keeps Ant is something else: a credible, visible, two-summer plan.

**Argument beats.** The sourced reporting, exactly as strong as it is and no stronger. The math: baseline 1.7%, best realistic stack lands near 5%, the +1000-odds bar is unreachable with these assets, so anyone selling a one-summer fix is selling. The false binary: panic-win-now and rebuild are not the only options, and the third lane is raise the floor without spending the future. What actually retains stars: competitive present, credible ascent, organizational competence. The two-summer logic: by July 2027 every fragile star's health is a known fact, the books are clean, the picks are intact, and the kids have a year of priced development. The bridge is the retention plan, presented as such.

**Receipts to show.** The baseline and the stacked-ceiling math. The 2027 option-value framing with the break-even swings (what an observed-healthy Kyrie or AD becomes worth). The patience cost, priced honestly at roughly half a point with eroding Spurs and OKC matchups, the premium paid for information.

**Public sources.** The Windhorst item and whatever the fresh search finds the day of writing. Contract data for Ant's extension timeline.

**Integrity guardrails.** Fresh reporting search on publication day, mandatory. The piece analyzes sourced dissatisfaction; it does not speculate a trade request into existence. The patience cost prints; the piece does not pretend waiting is free.

**Hook idea.** The bar everyone thinks keeps Ant is a number no trade can reach. The bar that actually keeps him is one the front office fully controls.

---

## Piece 7: The Offseason Plan (the flagship)

**Working title:** "The Toolbox Is the Trade"

**Thesis.** Randle's contract does not just occupy a roster spot, it locks the exception toolbox. The recommended offseason is the Smith-first stack: convert Randle, rent a corroborated guard with an exception, sign the mid-level shooter the conversion unlocks, re-sign Dosunmu, develop the kids on purpose.

**Argument beats.** The apron-choke finding: keep Randle and re-sign Dosunmu and the Wolves sit over the line where the full MLE and the TPEs die, so the patience path is down to the mini-MLE and minimums. The conversion is worth roughly the whole swing because it is the key, not the player. The portfolio table, published as four-view ranges with the conservative anchor named: A and C anchor at +1.6 to +1.75 on the most skeptical view with a ceiling near +3.4, B's edge lives only in the metrics the independent system distrusts, D is the priced fallback. The named pieces: Jalen Smith as the corroborated stretch five, Mitchell or McBride as the exception flier, the Powell/McCollum/Huerter tier at the MLE. The asset bill, honestly: the Randle sweetener targets seconds with a lightly-protected first as the ceiling concession, the exception absorptions cost seconds, pick 28 is used or traded but not both. The development plan inside the recommendation: Beringer is the designated backup five and the plan signs no veteran big who blocks him; Shannon's bench-creator runway opens automatically. The floor and ceiling framing throughout: the four-view range IS the floor-to-ceiling statement.

**Receipts to show.** The apron-choke math. The portfolio table with view ranges and the gauntlet columns. The named-candidate tables with tags. The asset bill. The Portfolio D row with its tax footnote.

**Public sources.** Salary data, the apron figures, DARKO public values, FA market lists for the MLE tier.

**Integrity guardrails.** Ranges only. Counterparty realism tags on every leg (the Giddey construction stays labeled Speculative). The sweetener cost prints; the plan is not presented as free. The MLE names are illustrative of a tier, with their own availability unverified until FA opens; refresh on publication day.

**Hook idea.** The best trade of the Wolves' offseason is not for a star. It is for permission to use their own tools.

---

## Piece 8: The Price of Rudy (the closer)

**Working title:** "The Price of Rudy" with the depreciation analysis as the second act.

**Thesis.** We defended him in Piece 2. Now we name his price, by view, and answer the question the car lot teaches: does the trade-in value survive a year of waiting?

**Argument beats.** The both-out playbook honestly: every Gobert-out portfolio prices negative today, the trade-off is 2 to 5 points of present title equity for a materially richer 2027 war chest, and replacing a DPOY anchor with a committee is the rim trap the model has flagged since day one. The reservation price by view: under the box read a Charlotte-type harvest clears the bar; under DARKO it rarely clears; under consensus and RAPM it is effectively unpayable, which means the keep-or-trade question is, mathematically, a referendum on which measurement of Gobert you believe, the same referendum the AD trade was. The two-sided honesty: arming the Lakers barely moves the title math, the rival-arming fear is smaller than intuition. The Bridges flag on the Charlotte package, because the framework's rules apply to inbound players too. Then the depreciation act (DONE: `outputs/gobert_depreciation_curve.md`, script `gobert_depreciation.py`): the three windows, now versus the February deadline versus summer 2027, the $38M option cliff that flips him from the asset that replenishes the chest into the contract you pay to move. The result confirms and sharpens the ending: his contract surplus crosses NEGATIVE this coming season (+$4.7M today to about -$1.3M in 2026-27, about -$8M on the option year), the realistic return falls from a real package now to a contender's deadline premium to paying-to-move by summer 2027 (the Horford 2020 pay-to-move case, where PHI attached a first to dump the contract), so holding past the deadline destroys more value than any summer return adds. Under the box and DARKO views the depreciation SOFTENS the hold into a sell-at-the-deadline lean, and the piece says so plainly; under consensus and RAPM the hold-and-contend verdict survives. The ending: hold this summer, run the plan, re-price at the deadline with half a season of the groomed branch on tape, and never let it reach the summer-2027 cliff.

**Receipts to show.** The both-out portfolio table. The reservation-price-by-view table. The depreciation curve with the three windows and the surplus-crossing point (DONE). The time-dependent EV-sacrificed-by-view table and the three-branch decision (DONE).

**Public sources.** Contract structure including the option and the kicker (Spotrac/HoopsHype). Trade comps for aging elite centers (public transaction record). DARKO surplus values.

**Integrity guardrails.** The reservation price is view-dependent and prints that way, never as one number. The depreciation analysis publishes whatever it finds, including if it softens the hold. The Bridges flag prints. Availability tags on the Charlotte and Lakers constructions.

**Hook idea.** In Piece 2 we argued the world is too low on Rudy Gobert. Here is the exact price at which we would stop arguing.

---

## Infrastructure: The Methodology Page (standing, not a series entry)

A single page every article links. Contents:

- The four views (box, DARKO, our consensus, our RAPM), what each sees and misses, and why disagreements print as ranges.
- Risk-adjusted EV and break-even availability, with the healthy/absent branch logic and its stated conservatisms.
- The feasibility gate: what it checks (matching, aprons, hard-cap triggers, kickers, Bird rights) and the rule that nothing infeasible gets simulated.
- Availability tags (Reported / Analyst / Speculative / Keep) and the adverse-selection logic for why high-surplus players rarely move.
- The sim in one paragraph: calibrated to win totals and de-vigged title boards, matchup-adjusted series, opponents emerge from the bracket.
- What the model does not do: predict injuries beyond public history, read locker rooms beyond labeled flags, or produce single-number certainty.
- The trust ledger: the artifacts the process caught and corrected in public view (the Avdija availability catch, the Diabaté small-sample mirage, the Detroit anchoring bug, the winner's-curse correction applied to our own headline). Self-caught errors are the brand's proof of work.
- Source list: NBA.com tracking and play types, Basketball-Reference, DARKO, HoopsHype/Spotrac, ESPN/Bobby Marks, sourced reporting ledger.

---

## Open items before writing begins

1. **The Gobert usage audit** (feeds Piece 2). DONE: `outputs/gobert_usage_audit.md`.
2. **The Gobert depreciation curve and timed reservation price** (feeds Piece 8). DONE: `outputs/gobert_depreciation_curve.md`.
3. **Publication-day refresh protocol:** re-run the relevant board and a fresh reporting search the day each piece publishes; the draft and free agency will move names while the series runs.
4. **Optional split decision on Piece 3** (one piece or Beringer/Shannon as two) once draft length is visible.
