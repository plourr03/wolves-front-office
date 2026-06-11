---
title: It's Not (All) Gobert's Fault
dek: Depending on which number you trust, Rudy Gobert is a problem, a solid starter, or the second-most important Wolf. Everyone in the argument is holding a real number. I went and found out what each one actually measures.
tags: [Timberwolves, Rudy Gobert, Pick-and-Roll, Four Views, 2026 Offseason, Offseason Series]
---

# It's Not (All) Gobert's Fault

For a stretch of years in Utah, Rudy Gobert was one of the most efficient roll men in basketball. Not "good for a center." The most efficient kind of basketball play, run through him, over and over, at the top of the league. Today the discourse's word for that same player is some version of: a massive detriment catching the ball out of the pick-and-roll.

Same hands. Different passes.

I've had the Rudy argument so many times since 2022 that I can run both sides of it by myself in the car. And here's what I finally figured out after building the models for this series: everyone in that argument is holding a real number. The argument never resolves because the numbers are measuring different things, and almost nobody says which one they're holding.

So this piece does two jobs. First it lays the four numbers on the table and tells you what each one can and cannot see. Then it does the thing the argument actually needs, which is to measure what changed between Utah and here. Not vibes. Possessions, touches, screens, feeds. The misuse claim, the one Wolves fans mutter and Gobert defenders shout, turns out to be checkable. I checked it.

Fair warning before we start: the parenthetical in the title is load-bearing. If you came here for absolution, you're going to be mad at me by the end. If you came here to dunk on him, same.

## The four numbers

Here's Rudy Gobert, four ways, all from this past season.

{{viz:gobert-four-view}}

*Four real numbers, one player. Hover each for what that number can see and what it's blind to. The spread is the whole argument.*

The box-score read has him around plus 1.5, a good starter. The box counts what a player does: points, rebounds, blocks. It cannot see what never happens, and Gobert's entire defensive value is things that never happen. Drives not attempted. Floaters not taken. It also can't see screens, and screening is most of his offensive job.

DARKO, the public machine-learning metric, has him at plus 2 overall, and the split is the honest part: plus 4 on defense, elite, top of the league for a center his age, and minus 2 on offense. Genuinely negative. Hold that minus 2, because the back half of this piece is about where it comes from.

And the on-court math, both my regularized plus-minus model and the consensus blend this series uses, has him between plus 5 and plus 6, which is second-most-important-player-on-the-team territory. Those metrics watch the scoreboard move with him out there against him off, across every lineup, and they keep concluding the same thing: the whole defense organizes around him, and the team is massively better with him.

That spread is not measurement error. That spread IS the Gobert discourse in miniature. The guy yelling that Rudy is a liability is holding the box score. The guy yelling that Rudy is a top-20 player is holding the on-court math. Neither of them is lying. You don't settle this argument by picking your favorite number. You settle it by asking why a player can be elite and negative at the same time, and the answer lives in what Utah built and Minnesota didn't.

## The machine Utah built

Utah in Gobert's prime was an offense designed around a specific physical fact: if you deliver him the ball on time, on target, rolling downhill, almost nobody on Earth can stop the result.

The numbers from those years are honestly kind of absurd. From 2016-17 through 2021-22 he ran the pick-and-roll as the finisher about three and a half times a game, peaking at 3.9, and the roll was as much as 31.7 percent of his entire offensive diet. His efficiency on those possessions sat between the 80th and 95th percentile in the league at its peak. He was top four in the NBA in screen assists six seasons straight, and led the league outright in three of them. And the team results followed: Utah built the number-one offense in basketball in 2021-22, a top-five offense the year before, on his screen and his roll.

None of that happened by accident, and this is the part the trade-era discourse forgets. Utah surrounded him with live-dribble passers, plural. The audit counts every teammate with at least 150 pick-and-roll ball-handler possessions in a season, which is my proxy for a guard who can actually deliver the ball out of a live dribble. Utah gave him three to six of those every single year. Donovan Mitchell ran more than 800 such possessions a season at the peak. Behind Mitchell: Conley, Joe Ingles, Jordan Clarkson, Rodney Hood, Ricky Rubio. The deliveries came from everywhere.

{{viz:feeder-count}}

*The delivery system, year by year: every teammate with meaningful pick-and-roll ball-handler volume. Hover a bar for the names. Watch what happens after 2022.*

And the scheme itself was built to feed him. Utah ran pick-and-roll ball-handler offense 3 to 7 percentage points above the league average every year of his prime. Here's the detail that settles whose scheme it was: the year Utah traded him, their pick-and-roll frequency fell straight back to league average. The machine wasn't Quin Snyder's whiteboard in the abstract. It was him.

## What Minnesota ran instead

Now the audit, Utah prime against the four Minnesota years. Every number below is from the same sources, same methods, side by side.

{{viz:roll-man-collapse}}

*Roll-man possessions per game by season, Utah blue-collar years in gray, Minnesota in green, with his efficiency line riding on top. The volume collapses. The efficiency never does.*

His roll-man volume fell 37 percent, from 3.27 possessions a game in the Utah prime to 2.06 here, and this past season it hit a career low as a starter: 1.46 a game, 15.7 percent of his offensive diet. His touches fell 25 percent. His screen assists fell 26 percent. And the delivery system got cut in half and then half again: three feeders in 2022-23, two the next two years, and in 2025-26 exactly one. Anthony Edwards, and nobody else. Conley at 39 fell below the bar. Donte, for all his shooting gravity, is not a live-dribble pick-and-roll guy. The proxy that returned three to six names a year in Utah returned one name here.

It gets one layer worse. The one feeder also changed his own game: Edwards' pick-and-roll ball-handler volume nearly halved this season, from 688 possessions to 353, as his diet shifted toward isolation and transition. And the team-level scheme finding is the quiet headline of the whole audit: Minnesota has run pick-and-roll ball-handler offense at or below the league average in every one of Gobert's four years here, bottoming out this past season at the lowest rate of the era. Utah fed the machine 3 to 7 points above league average. Minnesota runs it below average by design.

Meanwhile, the part of the job he controls never declined. His points per roll possession in Minnesota: 1.21 to 1.27, still comfortably above league average, 73rd percentile this past season. His dunk conversion held near 90 percent in both uniforms. He didn't get worse at the thing. He got a third less of it, from half the feeders, in a scheme that runs it less than the league does.

So the offense around the most efficient roll finisher of his generation ranked 23rd, 16th, 8th, and 13th in his four Minnesota years. Top ten once. That's the misuse claim, measured. It's real.

## The honest other side

Now the part where I don't give him absolution, because the data doesn't either.

Gobert is a finish-only player. Across his whole career, his assist-to-pass rate sits between 3 and 5 percent. He moves the ball fine, 2,500-plus passes a season, but he creates almost nothing off it: one to two assists a game, career, every year. That's not a slander, it's an archetype. And it's exactly why a thin delivery system is so expensive for him specifically. A big who can attack a closeout or make a short-roll read has somewhere for his offense to go when the clean feeds dry up. Rudy doesn't. Cut his deliveries and his offensive value has no fallback at all, which is precisely why DARKO's minus 2 is correct in this environment. A center whose offense must be manufactured by the system, playing in a system that stopped manufacturing it, is a negative offensive player here. Both halves of that sentence matter.

The hands thing is also real, just not the way it gets said. His turnover rate on roll possessions has been normal for the role his whole career, 8 to 11 percent, because Utah's deliveries arrived on time and on target. The limitation was always managed rather than absent: he converts clean catches at an elite rate and does not bail out bad ones. Utah built around that. Minnesota, mostly, did not, and the bobbles you remember are what an unmanaged limitation looks like.

And the defense, the thing his whole price rests on: still elite by every impact metric, but the team defense slipped to 10th this season, and Finch said so out loud. Some of that is the perimeter in front of him. Some of it is that he turns 34 this month. Print both.

## The data that argues back

I promised the misuse claim publishes only as measured, and measurement cuts both ways. Three things in the audit push against the clean "they buried him" story, and they print too.

First, his dunk attempts barely moved. Down 8 percent, against a 37 percent collapse in roll possessions. If Minnesota had truly stopped using him, the dunks die with the rolls. They didn't, which means Edwards' lobs and the transition rim runs still found him. What disappeared is narrower and more specific: the structured half-court possession that ends with him rolling out of a screen. They never stopped feeding his rim gravity. They stopped building the offense through it.

Second, the collapse wasn't a straight line. His roll volume actually ticked up in 2023-24 and 2024-25 before cratering this season, the same season the feeder count hit one. The structural problem spans all four years. The acute version is this past season specifically.

Third, my own outline for this piece overclaimed twice, and I'm printing the corrections because that's the deal. I had written that he led the league in screen assists every tracked Utah year. He didn't: three of six, top four in all of them. I had also written "most efficient roll man in basketball" as if it held continuously. The honest version is elite then, above average now. And here's the correction that sharpens the story instead of softening it: he led the entire league in screen assists again this past season. The screens still generate points for everyone else. He just finishes fewer of them himself.

## The price

So what is this piece actually claiming? Not that Rudy is secretly a top-10 player. Not that he's cooked. Something more specific: the two loudest positions in the Gobert argument are both priced off real numbers, and the gap between those numbers is mostly a description of the roster and scheme around him, not of him. Build the machine and the on-court math is what you get. Don't build it, and the box score and that minus 2 are what you get. Minnesota, for four years, did not build it.

That cuts both directions, and I want to be honest about the direction Wolves fans like less. He turns 34 this month. He makes $36.5 million next season with a $38 million player option behind it, and if you read the first piece in this series, you know his contract is one of exactly two doors out of the apron squeeze. A team that was never going to build the machine around him has a fair case that someone else should pay for the parts of his game it wasn't using. The case to keep him is real. So is the case that he can restock the war chest. This piece does not promise he stays. It corrects the price.

Because here's the thing the audit leaves you with. The fix for the delivery system, it turns out, looks a lot like the fix for the point guard problem this team already has, and the coach already named. Same hole. Same summer. That's a later piece.

The wrong first question is "should the Wolves trade Rudy." The right first question is which Rudy you think you have, and the answer depends almost entirely on what you put around him. We never really found out.

It's not all his fault. It's not none of it either. The parenthetical is doing real work.

---

*Next in the series: the young core. Joan Beringer played 1.6 minutes a night last season, and thirty years of players like him say that number, not his talent, is the whole question. And Terrence Shannon Jr. is a player, not a prospect, which is better news than it sounds.*

*[Methodology: the four views, the feeder proxy, the audit sources, and the sourcing tags](#methodology)*

<!-- Production notes, do not publish:
- Vizzes TK (ids reserved, to build): gobert-four-view (the spread with per-number blind spots),
  feeder-count (delivery system by season with names on hover), roll-man-collapse (volume bars +
  PPP line, UTA vs MIN), scheme-was-his (team PnR-BH frequency vs league avg, UTA/MIN, with the
  post-trade Utah dropoff highlighted). Data: outputs/gobert_usage_audit.md + cache CSVs.
- The "massive detriment catching out of the pick-and-roll" line is presented as the discourse's
  composite voice, no quote marks. If we want it as a quote, source it first.
- Four-view figures: box +1.48, DARKO +2.0 (ODPM -2 / DDPM +4, rank 32), consensus +5.28, RAPM
  +5.76. DARKO surplus +$4.7M not used here (Piece 8 material).
- Offense ranks verified vs warehouse June 11 (per-game ORtg averages): UTA 2021-22 #1, 2020-21
  #4; MIN 23rd/16th/8th/13th. Cross-check official NBA.com possession-weighted ranks at publish.
- Screen-assist ranks verified vs warehouse hustle table (g>=40): #2 Gortat 16-17, #4 Adams
  17-18, #1 x3 (18-19, 19-20, 20-21), #2 Adams 21-22; MIN years #2 behind Sabonis x3, #1 in
  2025-26 (307 total).
- Audit numbers all from outputs/gobert_usage_audit.md (warehouse-verified June 11): roll 3.27
  -> 2.06 (-37%), 1.46/g and 15.7% diet in 2025-26; touches 59.5 -> 44.3 (-25%); screen ast
  6.26 -> 4.63 (-26%); feeders 4 -> 2 -> 1 (Edwards 353, halved from 688); PPP 1.314 -> 1.244,
  73rd pct; dunks 3.50 -> 3.22 (-8%), conversion ~90% both eras; team PnR freq UTA +3.2 to
  +6.8pp above league, MIN at/below all four years, 13.1% (-2.2pp) in 2025-26; post-trade UTA
  fell to league average. 2021-22 tracking touches/passes excluded as corrupt ingest.
- Ast-to-pass 3-5%, 2,500+ passes, 1-2 apg: warehouse Passing tracking.
- Gobert turns 34 on June 26; "age-35 season" applies to the 2027-28 option year.
- Team defense 10th in 2025-26 + Finch acknowledgment: cite at publish (presser/quote).
- Gobert contract: $36.5M 2026-27, $38.0M PO 2027-28, no kicker, no NTC (HoopsHype 6/6).
- Krawczynski long-term-fit reporting and the "best Jokic defender in April" counter live in
  Piece 1's ledger; not re-cited here.
- Feeder-bridge teaser ("same hole, same summer") deliberately vague; the 1-to-3 number stays in
  Piece 7.
-->
