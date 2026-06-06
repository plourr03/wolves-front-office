# User analysis: Wembanyama hypothesis and the Q4 vulnerability

**Date:** 2026-05-16
**Author:** Bobby
**Context:** Reading the Component 3 result and the three-component pattern matrix.

## What Component 3 confirms

The Wolves' 2025-26 profile is: low ball stickiness (30), high motion death (71), very high iso reliance (89), and decentralized iso load (Herfindahl dropped to 0.361, Edwards' share of iso fell from 62% to 48%). That combination means the offense is running eight different players through isolation possessions while the four off-ball players stand still on every possession.

Now think about what that does to a defense with Wembanyama at the back. Wembanyama is the rim protector who lets the rest of the defense take risks they otherwise couldn't. With him sitting in the paint:

- The Spurs can send aggressive doubles at Ant because the rotation back to the rim is covered.
- They can switch a guard onto Randle in the post because Wemby's help shrinks Randle's space.
- They can let McDaniels or Naz catch the swing because nothing happens off-ball after the catch and Wemby is waiting for the drive.

This is exactly the matchup that Q4 offenses lose to. Q4 offenses need favorable iso matchups to function because they have no other advantage-creation mechanism. A team with elite rim protection AND switchable perimeter defenders removes both pieces of the favorable-matchup equation. The Spurs have Wembanyama at the rim and Vassell, Sochan, and Castle on the perimeter. That's the worst possible matchup architecture for a Q4 offense.

So the intuition isn't just right, it's structurally inevitable. The Wolves were going to struggle against the Spurs specifically because the Spurs' personnel directly counters every advantage the Wolves' Q4 offense was trying to create.

## The Component 3 magnitude matters

Prior was 55-75 percentile. Landed at 89. Meaningfully wrong on magnitude.

That magnitude is important. When 89% of teams in the league use less iso than the Wolves, you're not iso-leaning, you're iso-defined. Combined with the decentralized Herfindahl, the precise diagnosis is even sharper than what we said yesterday: the Wolves run more iso than almost any team in the league AND they spread it across more players than they used to. That's a worse problem than just "high iso." High iso concentrated in one star at least has the logic of "we trust our best player." High iso distributed across eight players has no logic at all. It's the offense saying "we have no idea who should attack so everyone takes turns."

## Why the findings folder matters

Most analytical work loses its reasoning trail. By the time you write the final memo, you've forgotten which predictions you made, which were right, which were wrong, and what you learned along the way. The findings folder solves this. Three months from now when someone asks "why did you conclude X?" you can show them the actual chronological sequence of priors, data, surprises, and updates. That's intellectual honesty made durable.

The calibration scorecard (8 right, 6 wrong across 14 priors) is a kind of artifact that almost no public basketball analyst maintains. Most analysts present conclusions without ever telling you what their priors were and how often they were wrong. The project's final deliverable will walk in with a documented track record of being right 57% of the time on specific testable predictions, with the wrong ones disclosed honestly. That track record is what makes the conclusions credible.

If this work ever gets to the Wolves front office, the findings folder is the thing that will make them take it seriously. Not the conclusions themselves. The transparent reasoning behind the conclusions.

## Four tests to run in Q3 (mechanism analysis), saved here so they aren't lost

These are not LAFI questions. They are mechanism questions that fall out of the Q4 diagnosis. Write them down for the Q3 build, not for now.

**Test 1: Wolves shot quality by primary opponent rim protector.** Compute Wolves expected eFG% in games against teams with elite rim protection (Wembanyama, Mobley, Holmgren, Adebayo) vs teams without. If the Wolves' expected eFG% is meaningfully lower against elite rim protection, the rim-protector-vulnerability hypothesis is supported.

**Test 2: Ant's possession outcomes by coverage type.** Compute Edwards' PPP when blitzed by elite vs non-elite teams. The hypothesis: Ant gets blitzed by everyone, but only elite-rim-protector teams successfully convert the blitz into a stop because the rotation back to the rim is sound.

**Test 3: Wolves offensive rebounding by opponent.** Q4 offenses sometimes survive by getting second chances on bad shots. Against elite rim protection, second-chance opportunities collapse because the rim protector cleans up the boards. Worth checking.

**Test 4: Spurs-specific possession outcomes.** Filter to just the second-round series. Are the Wolves' possessions ending in late-clock isos at a higher rate than usual? Are those isos against Vassell/Sochan/Castle individually, or are they being forced into Wembanyama help?

## Updated prediction for Component 4

Component 4 (Action Poverty) is going to be the big one. Updated prediction after seeing C3 land at 89: Wolves 2025-26 Action Poverty will land between 80th and 95th percentile.

If C4 lands below 70, that warrants investigation. Either the metric isn't catching what feels obvious from the eye test, or the diagnosis needs refining. Don't quietly accept a moderate ranking.

Specifically, the agent should track: diversity of identifiable actions per possession for the Wolves vs the league. If the Wolves run only 3 or 4 distinct action types repeatedly while championship offenses run 15-20, that's the structural pickup-ball tell. Pure count matters as much as frequency.

Note: v1 of Component 4 has to use proxies because the full action classifier doesn't exist yet. The eye-test report should be explicit about the v1 vs v2 distinction. If proxies are doing the work, the finding is suggestive. If we later build the classifier and it confirms, the finding becomes solid.

## Personal note

22 years of watching this team. Gut said "pickup at LA Fitness." Data said yes, but specifically the quadrant 4 version, which is more diagnostic than what the gut originally said. The whole point of doing analytics on a team you love isn't to replace intuition, it's to sharpen it. That happened here.
