---
title: The LA Fitness Game
dek: My brother-in-law watched the Wolves lose to the Spurs and said they were playing LA Fitness pickup. So I built a metric to find out how right he was.
tags: [Timberwolves, LAFI, Offensive Architecture, Basketball Analytics, Anthony Edwards, 2025-26 Postmortem]
---

# The LA Fitness Game

I've been a Timberwolves fan ever since my dad took me and my sister to a Timberwolves game back in 2004. I was 6 years old, and I remember watching KG get introduced with the loudest crowd I'd ever heard. Since then I've been a huge Wolves fan through it all. This year, however, something felt off.

I found I didn't enjoy watching this team nearly as much as I had in the past. I used to watch 50+ games a season; this year I watched maybe 5 full games. My brother-in-law and I were going over the Wolves' loss to the Spurs in mid-May. They had just gotten bounced from the second round in a disastrous Game 6 loss, and the offense was hard to watch. In the first quarter alone, three different Wolves missed unassisted mid-range jumpers in the span of five minutes. Jaden McDaniels: 15-foot pullup. Julius Randle: 10-foot fadeaway. Anthony Edwards: drove the lane, got walled off, hit the brakes and pulled up from 11 feet. All three missed. Three players, three iso attempts, no passes, no off-ball cuts. The fingerprint of the offense was a guy with the ball deciding what to do with it, and four other guys watching.

My brother-in-law said it casually, not like he was trying to make a big point: "They look like they're playing LA Fitness pickup."

He was right. I knew it the second he said it. Then I thought: how would I actually prove that?

That question turned into intense analytical work. This article is the first piece of what that work produced. The short version: my brother-in-law was right (sorry Scott, I'll never say it to your face), and the data lets us be specific about exactly what kind of pickup ball the Wolves are playing.

## What pickup ball actually looks like

If you have ever played at LA Fitness, you know the fingerprint. One person dribbles up the floor and decides whether to shoot, drive, or call out a vague action that nobody actually executes. The other four players stand and watch. The offense is whatever the ball-handler creates in the moment.

That fingerprint, generalized, has features you can measure. The ball is sticky (one player holds it for a long time before anything happens). The off-ball players stop moving. The possession ends in a one-on-one play because nothing else got organized. The shot is taken late, often contested, often from a spot the shooter would not choose if they had options.

The opposite end is what designed basketball looks like. Five players moving with purpose. Multiple actions in a single possession. The ball moves quickly. A shooter ends up open because the defense had to choose between covering the ball-handler and tracking off-ball cuts. The Spurs play this way. The peak Warriors did. OKC does now.

Most NBA teams sit somewhere between these poles. The interesting question is how to put a number on where exactly. I built a custom metric for this called the LA Fitness Index, or LAFI for short. The name is a joke on the origin story, but the math is real.

## The Wolves' fingerprint

LAFI measures offensive architecture across five dimensions: ball stickiness, motion death, isolation reliance, action poverty, and shot quality decay. Each comes from public NBA tracking data, and a team's score on each component is its percentile rank against every other team in the league since the tracking era began in 2014-15. A 50 is league-average. A 90 is genuinely extreme.

The 2025-26 Wolves are extreme on three of the five components. The bodies don't move (Motion Death: 72nd percentile, top third of the league). Possessions end in one-on-one plays (Isolation Reliance: 90th percentile, top tenth of the league). And the shots that result are bad (Shot Quality Decay: 83rd percentile, top tenth of the league).

The other two components surface a paradox. Ball Stickiness is at the 31st percentile, below league average. The Wolves actually pass the ball; no one player dominates the way Harden's Rockets or Doncic's Mavericks did at their iso peaks. Action Poverty is at the 45th percentile, dead average. The playbook is normal. The team has screens and cuts and designed plays in its system. They are running an iso offense by choice, not because the actions don't exist.

The composite scores compress the diagnosis. Sharp LAFI weights the three components most predictive of playoff failure (motion death, isolation reliance, shot quality decay). The Wolves' Sharp LAFI was 90: third in the league, behind only the 76ers (93) and the Clippers (92). Full LAFI weights all five components. The Wolves' Full LAFI was 65: 13th in the league, middle of the pack overall. The gap between the two ranks is the diagnosis. The Wolves are extreme on the components that matter for playoff offense and only moderate on the ones that don't.

{{viz:lafi-fingerprint-2025-26}}

*The chart is interactive. Pick another team to lay its fingerprint over the Wolves'.*

That fingerprint has a name. A team with low ball stickiness but dead off-ball movement, isolation-heavy possessions, and bad resulting shots is playing what this project calls distributed pickup: pickup-style basketball, the kind you would recognize from any gym, with one twist. The pattern is not concentrated in a single ball-dominant star. It is spread across the roster. Multiple Wolves take turns being the player who doesn't pass and doesn't create motion.

## How rare is this

Eight teams in the last eleven years of NBA tracking data have played offense the way the 2025-26 Wolves did. Out of roughly 330 team-seasons across the last decade, only eight. Fewer than one team per season.

Five of them are who you'd expect on a list of pickup-style offenses. The 2016-17 Phoenix Suns went 24-58. The 2018-19 Knicks went 17-65. The 2018-19 Kings went 39-43. The 2022-23 Bulls and the 2024-25 Kings both finished 40-42. Most of this list is bad teams that missed the playoffs entirely.

But two of them had real talent. The 2021-22 Philadelphia 76ers had Joel Embiid finishing second in MVP voting to Jokic. They lost in the second round. The 2023-24 Phoenix Suns had Kevin Durant, Devin Booker, and Bradley Beal. They got swept in the first round, by the Wolves themselves.

Including the 2025-26 Wolves, eight team-seasons match this offensive fingerprint. Of the seven that have already played their playoff series, zero reached a conference finals.

{{viz:lafi-cohort-ladder}}

*Every cohort team's bar runs as far as it reached in the playoffs. The red line is the Conference Finals. No bar reaches it.*

Sample size matters. With seven teams the right read isn't "this configuration cannot reach the conference finals." It's "this configuration has not, and the two cohort members with the most talent both came up short." Article 4 in this series spends its time on exactly that question. For now the simpler observation is enough: nobody who plays offense like this has gotten close.

## The obvious objection

If you are skeptical of all this, good. Here is the objection I would raise if someone handed me this analysis: the Wolves scored fine. Their offensive rating in 2025-26 was middle of the pack, not the bottom of the league. If the architecture were really this broken, wouldn't the points have dried up?

The objection is correct on the facts, and chasing down why it doesn't sink the argument is the fastest way to understand what LAFI actually measures.

LAFI measures how a team produces points, not how many. Individual shotmaking can paper over bad structure for months at a time. Edwards is good enough to hit contested pullups at a rate that keeps the offensive rating respectable, and a respectable offensive rating is exactly the thing that hides a broken structure from anyone reading only the scoreboard. Two teams can both score 115 per 100 possessions with completely different architectures, and one of those architectures holds up against a locked-in playoff defense while the other comes apart. Telling those two teams apart is the entire job LAFI was built to do. Offensive rating cannot do it.

What LAFI does not touch at all is defense. The Wolves had a top-ten defense in 2025-26, eighth in the league, anchored by Rudy Gobert. Nothing in the five components reaches that side of the floor. That is scope, not oversight. This article is about offense, and other work in this project handles the rest.

And LAFI is not, on its own, a prediction. It describes a structural pattern, and whether that pattern costs you a series depends on who you draw and what they are built to do to you. A 90 Sharp LAFI is not a death sentence by itself. It is a structural vulnerability that some opponents can pry open and others cannot. Which opponents, and how, is what the next several articles are about.

So the objection stands: the Wolves scored fine. The point of LAFI is that scoring fine in March tells you almost nothing about May, when the defense across from you has had six days to scheme and a roster built to switch every action you run. The metric makes the structure visible while the scoreboard is still busy hiding it.

## The question this raises

The Wolves had a 49-33 regular season. They beat the Nuggets in the first round. Anthony Edwards was an All-NBA caliber player, the kind of franchise star who is genuinely fun to watch and easy to root for. Rudy Gobert anchored one of the best defenses in the league. The supporting cast looked real, too. Ayo Dosunmu had turned into a sturdy role player. Mike Conley had chosen Minnesota. Terrence Shannon Jr. was an explosive young scorer off the bench. And let's not forget: they might have Wembanyama, but we have Jaden McDaniels. On paper this should have been exciting to watch. On paper this deserved more faith than I gave it, and it should have been a lot closer than it was.

In your gut, though, you knew better. Even in the best case, even if the Wolves had somehow found a way past the Spurs, nobody who actually watched this team believed they were beating OKC. The roster read like a contender. Watching it did not.

What you were watching was a pickup offense, distributed across the lineup, producing bad shots through isolation creation. The team that played the Spurs in the second round was structurally one of the most pickup-style offenses in modern NBA history.

That is the question the rest of this project tries to answer. How a team this talented ended up playing offense this way. Whether the architecture matters once the playoffs start. Whether any team with this profile can break through. What, specifically, the Wolves can do about it. The next article starts at the beginning of that chain, tracing how the Wolves drifted into this architecture from a 2023-24 team that looked nothing like it.

I do not know whether anyone with influence over the Wolves will ever read this work. I am writing it publicly anyway, to make the case where the case can be made. The franchise has never won a championship. I have been a fan since 2004, through the conference finals run and the long stretch of disappointing seasons that followed it. My brother-in-law's offhand comment became a project because the question underneath it, why this specific team plays this specific way, kept feeling like one worth answering.

For now the diagnosis is the foundation. The ball moves, the bodies don't, and the shots are bad. It started with a simple comment. It ended up here.
