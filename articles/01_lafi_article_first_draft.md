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

## What this measures, and what it does not

Before going further, I want to be honest about what LAFI is and is not.

LAFI measures offensive architecture, not offensive quality. A team can have high LAFI and still score plenty of points; the Wolves' offensive rating in 2025-26 was middle of the pack, not bottom of the league. The metric captures how a team produces points, not how many points they produce. Two teams can score 115 per 100 possessions with very different architectures.

LAFI also does not measure defense. The Wolves had a top-ten defense in 2025-26, eighth in the league, anchored by Rudy Gobert. None of what LAFI captures touches that. Other analytical work in this project addresses defense; this article is specifically about offense.

LAFI is also not predictive on its own. It describes a structural pattern. Whether that pattern matters depends on what happens when the structural pattern meets specific opponents in the playoffs. The next several articles in this series get into exactly that question.

What LAFI does measure, well, is the structural shape of a team's offense. Whether the team is running designed actions or watching one player figure it out. Whether the off-ball players are working or standing. Whether possessions end in advantage plays or one-on-one contests. The metric makes these structural distinctions visible and comparable across teams.

## The question this raises

The Wolves had a 49-33 regular season. They beat the Nuggets in the first round of the playoffs. Anthony Edwards was an All-NBA caliber player. Rudy Gobert anchored one of the best defenses in the league. The roster had no obvious holes.

And yet the architecture was the architecture of a pickup offense, distributed across the lineup, producing bad shots through isolation creation. The team that played the Spurs in the second round was structurally one of the most pickup-style offenses in modern NBA history.

This is the question the rest of this project tries to answer. How did a team this talented end up playing offense this way. Whether the architectural state matters in the playoffs. Whether teams with this profile can break through. What, specifically, the Wolves can do about it.

I do not know whether anyone with influence over the Wolves' front office will ever read this work. The goal of writing it publicly is to make the case where the case can be made. The team has never won a championship in its franchise history. I have been a fan since 2004, since the conference finals run that turned into a long stretch of disappointing seasons. My brother-in-law's casual observation became this analytical project because the question of why this specific team plays this specific way kept feeling like a question worth answering.

The next article in this series traces how the Wolves got to this architectural state from a very different one just two years ago. The trajectory matters. The team in 2023-24 looked nothing like the team in 2025-26. Understanding how the drift happened sets up everything that comes after.

For now, the diagnosis is the foundation. The Wolves are playing distributed pickup. The ball moves but the bodies don't. The shots are bad. The architecture is rare, and the rarity matters in ways we will spend the rest of this project working out.

It started with a comment on the couch. It ended up here.
