---
title: The LA Fitness Game
dek: My brother-in-law watched the Wolves lose to the Spurs and said they were playing LA Fitness pickup. So I built a metric to find out how right he was.
tags: [Timberwolves, LAFI, Offensive Architecture, Basketball Analytics, Anthony Edwards, 2025-26 Postmortem]
---

# The LA Fitness Game (Bobby notes: do not change this section, love it)

I've been a Timberwolves fan ever since my dad took me and my sister to a Timberwolves game back in 2004. I was 6 years old, and I remember watching KG get introduced with the loudest crowd I'd ever heard. Since then I've been a huge Wolves fan through it all. This year, however, something felt off.

I found I didn't enjoy watching this team nearly as much as I had in the past. I used to watch 50+ games a season; this year I watched maybe 5 full games. My brother-in-law and I were going over the Wolves' loss to the Spurs in mid-May. They had just gotten bounced from the second round in a disastrous Game 6 loss, and the offense was hard to watch. In the first quarter alone, three different Wolves missed unassisted mid-range jumpers in the span of five minutes. Jaden McDaniels: 15-foot pullup. Julius Randle: 10-foot fadeaway. Anthony Edwards: drove the lane, got walled off, hit the brakes and pulled up from 11 feet. All three missed. Three players, three iso attempts, no passes, no off-ball cuts. The fingerprint of the offense was a guy with the ball deciding what to do with it, and four other guys watching.

My brother-in-law said it casually, not like he was trying to make a big point: "They look like they're playing LA Fitness pickup."

He was right. I knew it the second he said it. Then I thought: how would I actually prove that?

That question turned into intense analytical work. This article is the first piece of what that work produced. The short version: my brother-in-law was right (sorry Scott, I'll never say it to your face), and the data lets us be specific about exactly what kind of pickup ball the Wolves are playing.

## What pickup ball actually looks like (Bobby notes: Good)

If you have ever played at LA Fitness, you know the fingerprint. One person dribbles up the floor and decides whether to shoot, drive, or call out a vague action that nobody actually executes. The other four players stand and watch. The offense is whatever the ball-handler creates in the moment.

That fingerprint, generalized, has features you can measure. The ball is sticky (one player holds it for a long time before anything happens). The off-ball players stop moving. The possession ends in a one-on-one play because nothing else got organized. The shot is taken late, often contested, often from a spot the shooter would not choose if they had options.

The opposite end is what designed basketball looks like. Five players moving with purpose. Multiple actions in a single possession. The ball moves quickly. A shooter ends up open because the defense had to choose between covering the ball-handler and tracking off-ball cuts. The Spurs play this way. The peak Warriors did. OKC does now.

Most NBA teams sit somewhere between these poles. The interesting question is how to put a number on where exactly. I built a custom metric for this called the LA Fitness Index, or LAFI for short. The name is a joke on the origin story, but the math is real.

## The Wolves' fingerprint

Take a Wolves possession from this season. You can almost predict it. Mike Conley walks the ball up and swings to Edwards on the wing. That counts. The ball moved. Two players, one to the other, the way designed basketball is supposed to start.

Now Edwards has it. He surveys. The other three Wolves on the floor stand still. Maybe one drifts a few feet, but nobody cuts, nobody screens, nobody runs to a relocation. Edwards jabs. Hesitates. Jabs again. At the seven-second mark he drives, gets walled off, and pulls up from 11 feet, contested. Miss.

That sequence is the architecture. The Wolves pass the ball. They stop moving once the pass arrives. The possession resolves the only way it can after that, which is whoever has the ball trying to make something happen alone.

LAFI puts five numbers on the possession we just watched. Each is a percentile against every team-season since 2014-15. A 50 is league average. A 90 is the kind of extreme you would name a team for.

Conley to Edwards counts. Ball movement is fine. 31st percentile in stickiness, which is just to say no one player has the ball glued to him. The Wolves move it.

The four other Wolves going still the second Edwards catches: 72nd percentile in motion deadness, top third of the league for standing around. The seven seconds of jabs ending in a contested pullup from 11 feet that nobody on this roster shoots well: 90th percentile in isolation reliance, 83rd in shot quality decay. Top tenth in both.

Then the twist. The fifth number, action poverty, asks whether the team has designed plays in the book at all. The Wolves rank 45th. Dead average. They have plays. They run plays. The plays end where the possession we just watched ended, with someone standing still and watching, and one guy trying to make something happen alone. The architecture is not absence. It is a habit.

Roll the five numbers into two composites. Full LAFI weights them equally. The Wolves come out at 65, 13th in the league. Dead middle. Sharp LAFI weights only the three components that predict playoff failure. The Wolves come out at 90, third in the league, behind only the 76ers and the Clippers.

The gap is the diagnosis. The Wolves are extreme on the things that matter in May. Average on the ones that hide the problem in March.

{{viz:lafi-fingerprint-2025-26}}

*The chart is interactive. Pick another team to lay its fingerprint over the Wolves'.*

That fingerprint has a name. Distributed pickup. The pattern from the Spurs game shows up game after game, but it is not concentrated in any one ball-dominant star. It is shared. Edwards, Randle, McDaniels, Conley, Reid. Watch a few Wolves possessions in a row and you can guess who isolates, but not always right. The pickup style is not Edwards's. It is the team's.

## How rare is this

Eight teams in eleven years of NBA tracking data have played offense like the 2025-26 Wolves. Out of roughly 330 team-seasons. Fewer than one per year.

Most of them are forgettable. The 2016-17 Suns won 24 games. The 2018-19 Knicks won 17. The 2018-19 Kings, the 2022-23 Bulls, the 2024-25 Kings: bottom-of-the-conference teams that did not make the playoffs at all. The kind of rosters where pickup offense is what happens when nobody on the floor can break a defense down.

Two of them are not forgettable.

The 2021-22 Sixers had Joel Embiid finishing second in MVP voting. In February they traded Ben Simmons for James Harden, the most ball-dominant guard of the previous decade. On paper, that team had a creator at every level. In practice it scored its way into the second round and got bounced by the Heat. Embiid played hurt. Harden disappeared. The architecture that made them so weird in the regular season, a team with two MVP-tier creators that still played isolation-heavy distributed pickup, gave them nothing to fall back on when the offense seized up.

The 2023-24 Suns had Kevin Durant, Devin Booker, and Bradley Beal. Three All-Stars, all healthy when the playoffs started. They drew the Wolves in the first round and got swept. The Suns' answer for everything was for one of their three stars to take a tough shot. The Wolves had a different roster that year, and they made every one of those shots harder than it needed to be. Three stars, four games, no structure to fall back on when individual brilliance was not enough.

Those are the two cohort members the 2025-26 Wolves should be looking at hardest. Both had real talent. Both had star creators. Both ran an architecture that depended on shotmaking to cover for the absence of structure. Both lost early.

Including this year's Wolves, the cohort is eight teams. Of the seven that have already played their playoff series, none have made a conference finals.

{{viz:lafi-cohort-ladder}}

*Every cohort team's bar runs as far as it reached in the playoffs. The red line is the Conference Finals. No bar reaches it.*

Seven is not enough to call this a law of basketball. The honest read is that nobody built like the 2025-26 Wolves has gotten close, and the two cohort members with the most talent both lost when the playoffs forced their offense to be more than the sum of its stars. Whether the architecture is actually fatal or just suggestive is what the next article spends time on. For now the simpler observation is enough.

Nobody who plays offense like this has gotten close.

## The obvious objection

If you're skeptical of all this, good. Here's the objection: the Wolves scored fine. They put up a middle-of-the-pack offensive rating in 2025-26. If their architecture were really broken, wouldn't the points have dried up?

The objection is right on the facts. It just isn't the gotcha it sounds like.

LAFI measures how a team scores, not how much. Edwards is good enough to hit contested pullups at a rate that keeps the scoreboard respectable. So is Randle. So is Reid. Three players in a rotation can carry a bad-architecture offense to a normal offensive rating for 82 games. A normal offensive rating is exactly the thing that hides a broken structure until May.

The thing that changes in May is the defense across the floor. The Spurs had six days to game-plan the Wolves, and a roster built to switch every action they ran. Switching kills designed plays. It also exposes pickup offense for exactly what it is: five against five, the ball-handler against his man, four other guys watching. When the Wolves' answer to the switch was Edwards isolating against Wembanyama, the architecture got the playoff defense it had been hiding from.

That is the gap LAFI was built to measure. Two teams can both score 115 points per 100 possessions, and one of them survives a switching playoff defense while the other does not. The scoreboard cannot tell you which is which. The structure can.

## The question this raises

The Wolves had a 49-33 regular season. They beat the Nuggets in the first round. Anthony Edwards was an All-NBA caliber player, the kind of franchise star who is genuinely fun to watch and easy to root for. Rudy Gobert anchored one of the best defenses in the league. The supporting cast looked real, too. Ayo Dosunmu had turned into a sturdy role player. Mike Conley had chosen Minnesota. Terrence Shannon Jr. was an explosive young scorer off the bench. And let's not forget: they might have Wembanyama, but we have Jaden McDaniels. On paper this should have been exciting to watch. On paper this deserved more faith than I gave it, and it should have been a lot closer than it was.

In your gut, though, you knew better. Even in the best case, even if the Wolves had somehow found a way past the Spurs, nobody who actually watched this team believed they were beating OKC. The roster read like a contender. Watching it did not.

What you were watching was a pickup offense, distributed across the lineup, producing bad shots through isolation creation. By the playoffs you were watching it without Donte DiVincenzo, the player who most reliably broke that pattern, lost to a torn Achilles. Every Wolves fan knew this was bad. What none of us realized was how much of the architecture itself was being held up by the specific kind of player Donte is. The team that played the Spurs in the second round was one of the most pickup-style offenses the modern NBA has produced.

That is what the rest of this project tries to figure out. Where this team came from, what they can do about it, and whether anyone built this way ever has a real chance. The next article picks up the trail. Two years ago the Wolves were one win away from the Finals. Same coach, same franchise star. A different team in almost every other way. How they drifted from there to here is the next piece.

I do not know whether anyone with influence over the Wolves will ever read this work. I am writing it publicly anyway, to make the case where the case can be made. The franchise has never won a championship. I have been a fan since 2004, through the conference finals run and the long stretch of disappointing seasons that followed it. My brother-in-law's offhand comment became a project because the question underneath it, why this specific team plays this specific way, kept feeling like one worth answering.

For now the diagnosis is the foundation. The ball moves, the bodies don't, and the shots are bad. It started with a simple comment. It ended up here.
