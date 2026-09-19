> **REFIT 2026-09-19 (D89).** The possession grain these RAPM figures are fitted on is fixed: points are credited to the team that scored them, and per-team possession points now reconcile to the box score exactly on every sampled team-game. RAPM has been refit on the corrected grain, so the numbers below have been superseded. **Both RAPM claims in this draft were re-tested on the refit and both hold:** Gobert's offence goes from +2.62 in 2023-24 to -4.12 in 2025-26 (the published direction, sharper), and DiVincenzo is still the highest net RAPM in the 2025-26-only sample at +4.86. Before and after, with the movers and the direction of the bias: `postmortem/outputs/findings/lineup_pipeline/04_d89_rapm_refit_and_article_claims.md`. The stint layer was fixed and recomputed earlier: `postmortem/outputs/findings/lineup_pipeline/03_d88_points_fix_and_recompute.md`.


---
title: How They Got Here
dek: Two seasons ago the Wolves ran a normal NBA offense. Now it is one of the most pickup-style in the league. The trade everyone blames is not the main reason it drifted.
tags: [Timberwolves, LAFI, Offensive Architecture, KAT Trade, Julius Randle, Donte DiVincenzo, 2025-26 Postmortem]
---
# How They Got Here

One of the most enjoyable days of my life was May 19th 2024. I was pacing in my living room when Mike Conley crossed Jamal Murray up, step back 3 and Bang! The Timberwolves had come back from 20 points down in Game 7. Every Timberwolf was getting involved. KAT and Jaden had 23, Ant 16/8/7, Gobert 13/9, Conley 10/8/4, Naz Reid 11. As a Wolves fan I had gotten so used to the ball not falling when we needed it, and comebacks getting smothered by the opponent's defense before they could even start. This felt like a real turning point. And it felt like no one could stop this team.

It was the best time to be a Wolves fan. We had swept KD, we had a comeback win against the Nuggets, ANT was talking alot and backing it up, and the season just felt so fun to watch. That season was unforgettable. And yes, the run ended with a bad loss to the Mavs in the conference finals, but even those games were worth watching. I'm not going to act like that season was perfect. We almost blew that Denver series before Game 7 ever happened, going up 2-0 and then losing three in a row, including a 27 point home blowout in Game 3. Maybe I'm looking back through rose-colored glasses (hint: I know I am). But that isn't the point. The point is it was so fun to watch.

Two seasons later, Edwards was still the centerpiece. Gobert was still the anchor. KAT was gone. Half the rotation was gone. And underneath them, the offense they were running was what my brother-in-law called LA Fitness pickup.

How that happened is what this article is about. Not whether the Wolves play pickup ball now. The first article in this series established that they do, and built a metric to prove it. This one asks how they got from there to here. How an offense that was unremarkable in 2023-24 drifted into one of the most pickup-style configurations in modern NBA history by 2025-26. Not just what went wrong, but how to keep it from happening again.

The short version, and the part that surprised me: the drift happened in two distinct steps, not one. The team did not slide straight from organized to broken. It passed through a different kind of broken first. And the trade most fans would point to as the cause, the one that brought Julius Randle to Minnesota, turns out to be close to architecturally neutral once you account for everything that came back. The real story is messier and quieter, which is exactly why it is worth telling carefully.

The metric driving this article is LAFI, a 0-to-100 score for how pickup-style an offense looks. Higher is more pickup. Full LAFI is the broad number; Sharp LAFI keeps the three traits that most predict a playoff offense falling apart, and article one builds the whole thing from scratch.

## The team that looked nothing like this

Start with the baseline. The 2023-24 Wolves were a great team, but not because of their offense. They went 56-26, had the best defense in the league, and the third-best net rating in the NBA. The offense ranked 17th of 30 in points per possession, a touch below the league median. The conference finals run was built on that defense, on Anthony Edwards, and on a roster that fit. Not on an offensive machine.

Structurally, the offense was ordinary. Full LAFI of 35, Sharp LAFI of 45, both modestly below average. That put them around 13th of 30 in how designed their offense was. Middle of the pack. Same on the three playoff-relevant traits: motion death 43, isolation reliance 49, shot quality decay 39. The team ran designed actions on 61.9 percent of its possessions. Towns at the four next to Gobert, Edwards rising into stardom, Conley organizing the floor, McDaniels and the supporting pieces in their roles. The ball moved, the bodies moved, the shots were fine. And man was it fun to watch.

{{viz:lafi-2023-24-league-ranking}}

*All 30 teams in 2023-24 plotted on Full LAFI, most designed on the left, most pickup on the right. The Wolves sit just below league average at 35, 13th of 30 in offensive design. Hover any dot for that team's component breakdown.*

Two years ago, this franchise ran a normal NBA offense. The roster has shifted since (KAT gone, NAW gone, supporting cast reshuffled), but the spine is largely intact: Edwards, Gobert, McDaniels, Reid. Not a great offense back then. A normal one. Whatever happened next did not have to happen.

## The first wrong turn 

Here is the part I did not expect when I started pulling the data. The Wolves did not drift directly toward the offense they play now. In 2024-25, the first year of the Julius Randle era, they became a different kind of "broken".

They became Anthony Edwards's offense in the most literal sense possible. Every possession started running through him, ended through him, and lived or died on what he decided to do with it. Ball stickiness almost doubled, from 35 to 69. Isolation reliance climbed from 49 to 71. Shot quality decay cratered, 39 to 72. Sharp LAFI rose from 45 to 71. The pattern has a name. Single-star pickup. One player holds the ball, dominates possessions, the offense becomes whatever that player creates.

My first thought was this must be one of two things: Edwards started shooting more, or Randle started hogging the ball. Neither happened. In fact the person "responsible" was a complete surprise to me.

Edwards used 31 percent of the Wolves' offensive possessions in 2023-24. He used 31 percent in 2024-25, and 31 percent again in 2025-26. Flat for three straight years. He was not taking on a heavier scoring load.

Randle did not match the "new guy hogs the ball" pattern either. He used possessions at a slightly lower rate than Towns had, 25 percent against 27. The change that mattered was not at power forward. It was at point guard. Edwards was being handed the steering wheel because the team's actual driver could no longer hold it.

That driver was Mike Conley. In 2023-24, even at 36, Conley ran long stretches of the offense the way old point guards do, with almost no mistakes. His assist-to-turnover ratio that season was 4.4. He kept things organized whenever Edwards rested or played off the ball. Then Conley got old, fast. His minutes fell from 29 a game to 25 to 18. His scoring from 11 points to 8 to 5.

I'm not trying to blame this on Conley. The Wolves had seen it coming. They spent a 2024 first-round pick on Rob Dillingham as the bet on life after Conley. Two seasons in, his role had shrunk instead of growing. The Wolves traded him at this year's deadline.

The distributor left the floor and nobody replaced him. Running the offense fell to Edwards by default. He held the ball longer. His dribbles per touch climbed from 3.9 to 4.5. The ball stickiness number is registering Edwards handling more, not Edwards shooting more. And the more the offense ran through him, the less the ball moved. His assist rate fell from 24 percent to 21 to 18 across the three seasons.

{{viz:edwards-conley-trajectory}}

*Three player-level metrics across three seasons. Edwards's usage rate stayed flat at 31 percent. Conley's minutes collapsed, and Edwards's assist rate collapsed alongside them.*

Here is where the comparison gets pointed. As a playmaker, Edwards is not Conley and never has been. His assist-to-turnover ratio has sat between 1.3 and 1.7. Conley's stayed above 4.2 every year of the same stretch. The gap is not subtle. Edwards is a brilliant scorer, a dangerous offensive threat and one of the highest-potential players in the entire NBA, maybe even a top 5 player now. He is not, however, a low-mistake playmaker. In 2024-25 the Wolves needed one and no longer had one, and they handed the role to the player they had.

And they reached the conference finals again.

That is the uncomfortable thing about 2024-25. The architecture had already gone wrong, and the record did not show it. A team can play structurally compromised offense and still win two playoff rounds, because individual talent and a top-tier defense can carry a lot of weight in a given spring. The drift was real. The results just had not caught up to it yet.

## Arrival 

Then came 2025-26, and a number that looks like good news until you understand it. Ball stickiness fell back down, from 69 to 31. On its own, that reads like the offense decluttered. It did not.

What happened is that the iso load decentralized. In 2024-25, Edwards held the ball too long. In 2025-26, five different Wolves did, in turns. One possession ended with Edwards backing his man down. The next ended with Randle bullying through a switch. The next was McDaniels rising for a midrange. The next was Naz Reid. The next was Conley. Possession by possession it looked diverse. In aggregate it was single-star pickup spread across five hands instead of one. The first article called this distributed pickup.

Every other component got worse. Motion death rose from 55 to 72. Isolation reliance went from 71 to 90, top tenth of the league. Shot quality decay reached 83. Sharp LAFI hit 90, third in the NBA.

Across the two years, three numbers moved in near-lockstep:

{{viz:lafi-trajectory}}

*Motion death, isolation reliance, and shot quality decay climbed together across both seasons. Ball stickiness is the outlier: it spiked, then fell, because the isolation load moved from one player to five.*

The path is two moves, not one. Organized offense, then single-star pickup, then distributed pickup. Action poverty, the fifth component, stayed moderate the whole way: 27, then 36, then 45. The playbook never emptied out. The team always had the designed actions available. It chose, season over season, to run them less.

{{viz:lafi-quadrant-migration}}

*The Wolves' position on the LAFI quadrant, season by season. The 2023-24 team sits in the designed corner. The 2024-25 team moves toward single-star pickup. The 2025-26 team lands in the distributed-pickup corner. The path is two moves, not one.*

## The trade everyone blames

If you ask a Wolves fan what broke the offense, most will give you one answer: the Wolves sent out Karl-Anthony Towns, brought in Julius Randle, and the architecture fell apart. It is the intuitive story. Towns was the stretch five who made the 2023-24 offense work. The drift began the season he left.

The data does not support that story cleanly. The reason is worth walking through.

Start with the deal itself. The Wolves did not trade Towns for Randle. They traded Towns (plus minor pieces and a second-round pick) for Randle, Donte DiVincenzo, and a 2025 first-round pick via Detroit that became Joan Beringer at #17. The first time I tried to model what the Wolves would look like if the trade never happened, I treated it as a straight Towns-for-Randle swap. That was wrong. DiVincenzo arrived in the same deal. Rebuilding the counterfactual with DiVincenzo properly included flipped the answer.

Here is the counterfactual. Take the actual 2025-26 season and rebuild it as if the trade never happened. Towns stays. Randle and DiVincenzo are never Wolves. A replacement-level wing fills the roster spot DiVincenzo would have occupied. I ran three versions, varying how good the replacement wing is, from a peak Joe Ingles in real rotation minutes (not the five-minute-a-night version the Wolves had last year) down to a minimum-salary roster filler. They all land in the same neighborhood. The counterfactual Wolves post a Sharp LAFI in the mid 70s to high 80s, against the actual 90. Full LAFI in the mid 50s to mid 60s, against the actual 65.

In plain terms: even with Towns and without the trade, this team is still playing distributed pickup. The trade was close to architecturally neutral.

The reason is that the trade gave and took on the same ledger. Towns back would help where Randle hurts. He sets a better screen, rolls a real threat, isolates less. But losing DiVincenzo would hurt those exact same components. DiVincenzo took 496 catch-and-shoot threes at 38.3 percent last year, the kind of volume that warps a defense, and he kept moving without the ball even when nobody else did. Strip him out and the counterfactual's motion death and shot quality decay actually come out worse than what the Wolves actually posted. The two effects cancel.

So if the trade was close to an architectural wash, what did it actually do? Its biggest single effect was bringing in Donte DiVincenzo, a name you will see a lot across these articles. A distributed-pickup offense lives or dies on shooting. When every possession can collapse into one-on-one, the structural thing that keeps the offense from cratering is a shooter the defense cannot help off of, someone who makes it pay every time it leaves him to wall off a drive. DiVincenzo was that shooter. For one season he was the connective tissue of an offense that otherwise had very little of it.

You can still argue the rest of the deal, the loss of a top-30 player weighed against the cap relief and the pick that came back, and reasonable people do. But the clearest line through all of it is this: the trade did not break the Wolves' offense. It handed them the one player most able to hold a breaking offense together.

## The quieter causes

When I started, I thought the drift had three accomplices. Working through the data, two of them turn out to be the same accomplice.

Start with what looks like a coaching choice. Rudy Gobert is still on the Wolves. They just stopped running him in pick-and-roll. The roll-man volume dropped 41 percent in two years, from 188 possessions to 111. The efficiency was still there (1.27 points per possession) when he did get the call. On its face it looks like the team decided to use him differently.

It is not actually that.

In 2023-24, Mike Conley was the team's second-most-used pick-and-roll ball-handler behind Edwards. The math lines up cleanly. Conley lost about 210 ball-handler possessions across the next two years. At league-average rates, those would have produced roughly 76 roll-man finishes. Gobert lost 77. The shapes match.

No one replaced Conley in that role. Edwards is iso-skewed by preference and his own pick-and-roll usage as the ball-handler dropped about ten percentage points in 2025-26 while his isolation rate climbed. Rob Dillingham, the 2024 first-rounder drafted as life-after-Conley, was traded at this year's deadline. DiVincenzo is a guard but a wing in usage, not a primary creator. The team functionally had no other distributor-type ball-handler. When Conley sat or shrank, the Gobert pick-and-roll just did not happen.

Honestly, taken alone, the play-calling math wasn't a huge killer. And if I'm being honest as a Wolves fan, seeing less Rudy offense was okay with me. Putting the 2023-24 play mix back on the current roster projects to gain only about 0.35 points of offensive rating per 100 possessions, and that estimate assumes the team can actually run those plays, which without a Conley replacement is not really true.

The play-calling cause and the aging cause are the same cause.

Conley isn't the only aging story, though. Three of the four most important non-Edwards pieces are declining at the same time. Gobert is 33, the age when defensive-anchor centers typically start to slip. Randle at 31 is past peak for his frontcourt archetype. Conley is at the tail end of a long career. They are all declining together.

Gobert's offensive impact, measured by a teammate-controlled metric called RAPM, has gone from positive in 2023-24 to clearly negative in 2025-26. Some of that is the pick-and-roll loss that traces back to Conley. Some of it is age. His defense stayed elite, which is part of why he is still on the team. But the offensive math is moving the wrong direction at the same time the cast around him is.

And then there is the one Wolves fans felt in real time. DiVincenzo tore his Achilles in the first round against the Nuggets. Every Wolves fan watching knew the second it happened that the playoff offense was going to look different. The numbers later said worse than they thought.

By the 2025-26-only version of that RAPM metric, DiVincenzo had been the highest-impact player in the entire league sample, not just on the Wolves. He was the team's best catch-and-shoot shooter. He was the single piece most capable of softening the offense's motion death and shot quality problems. The team that walked into the second round, against a Spurs roster built to switch every action, did not have him.

That isn't the only reason for what came next. But every Wolves fan who watched that series will tell you the same thing: without Donte, this team didn't stand a chance.

## What this means 

The drift was not a decision. It was an accumulation. A trade that washed out architecturally, an aging core whose decline took the team's pick-and-roll diet down with it, and a playoff injury that removed the one piece holding the worst tendencies in check. And underneath all of that, a front office that did not, or could not, replace what the team had lost. They needed a distributing point guard to take the ball off Edwards's hands when he rested. They needed more than one shooting wing. They got neither, and the offense drifted to fit what they actually had. No single move did this. No single move undoes it.

That is the discouraging read. Here is the other one. The 2023-24 Wolves posted a Full LAFI of 35, a normal NBA offense. They did it with the same spine that is still on this team: Edwards, Gobert, McDaniels, Reid. This is not an argument to rebuild the 2023-24 Wolves. That team had its own ceiling, and they showed it in the conference finals against the Mavs. The point is narrower than that. The spine has run normal NBA offense before, when the supporting pieces were right. The drift is structural drift, not talent collapse. The fix is filling the two holes the front office never filled, a distributor and a real shooting layer, not chasing a roster that already came and went.

But before any of that, there is the series itself. The Wolves did not just lose to the Spurs. They got specifically dismantled. San Antonio cut Anthony Edwards's catch-and-shoot looks more than in half and pushed him into the 11-to-16 foot floater zone, the worst spot on the floor for what he does. The next article walks through how they did it.

