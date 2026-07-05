---
name: social-replies
description: Draft a sharp, data-backed reply to a Reddit or X (Twitter) post about the Minnesota Timberwolves, grounded in the trade model, cap runs, and warehouse so every claim traces to real numbers, written in Bobby's own fan voice as a starting draft for him to rewrite and post himself. This is a co-pilot: it finds the data and drafts the analysis, and it NEVER scrapes threads or posts on its own. Use this whenever Bobby pastes a Reddit thread, comment, tweet, or a link to one and wants to weigh in, asks "how should I reply to this" or "what would I say here," wants to answer a fan question with real analysis, or wants to turn a Wolves discussion into a credible comment that grows the account. Trigger even if he just pastes a thread and says "respond to this," "help me answer this," or names a topic he wants to jump into on r/timberwolves or Wolves Twitter.
---

# Wolves to a T: Social Replies

Turn a Reddit or X post about the Timberwolves into a reply that is the smartest, most grounded take in the thread, backed by the trade model and the warehouse, and written so it sounds like Bobby. The goal is not clicks. The goal is to be the most useful voice in the room so that people click the profile on their own and follow the trail home.

## The one rule that governs everything: co-pilot, never auto-poster

This skill drafts. Bobby posts. Always, no exceptions.

- It NEVER scrapes threads, monitors subreddits, or posts comments on its own.
- It produces a starting draft. Bobby rewrites it in his own words, adds his own judgment, and posts it as himself. The final comment has to be genuinely his take, tool-assisted, not a copy-paste of model output.
- Why this is non-negotiable: the entire strategy works because a real person who knows ball did the homework. Reddit and X can smell a generic AI comment instantly, and getting tagged as "the guy running bot replies" would vaporize the exact credibility being built. It also cuts against platform rules on automation and self-promotion, and a ban kills the channel outright.

If a request ever implies auto-posting or bulk-generating comments to spray around, stop and reframe it back to the co-pilot workflow.

## Workflow

Input can be pasted text (a thread, a comment, a tweet) or a link. If it is a link, read it first; if it is text, use it directly. Then:

1. **Read the prompt for what is actually being asked, and answer THAT.** Parse the literal ask and the human intent behind it before doing anything else. Many posts are a plain question that just wants a plain take: "would you trade X for Y if it meant getting Z" is usually just asking "yes or no, and why," and the honest answer is often a simple "yeah, obviously." State the ask in one line. Reframe ONLY when there is a genuinely better question hiding that the asker would find illuminating (e.g. "can we afford to re-sign Ayo" really is "are we OK operating as a first-apron team"). Do NOT substitute a more technical or clever question for the simple one they meant. Over-reframing a straightforward hypothetical into a cap-mechanics lecture answers a question nobody asked. When the answer is "yes, obviously," lead with that in plain language, take the side, and add at most one grounded layer on top.
2. **Inventory what's already been said, then pull the data.** Before drafting, list what the post asserts AND the obvious common takes floating around the topic. Treat all of it as known ground the reply must get past (see the add-don't-reiterate guardrail). Then query the warehouse and model for the numbers that answer it (see Data sources). Every factual claim in the draft must trace to something real. If the data does not support a claim, do not make the claim.
3. **Verify any stat the post cites, including its season.** If the post drops a number (On-Off, EPM, a per-game line), check it before amplifying it, and check WHICH SEASON it is from. Raw stats swing wildly year to year (a hurt year vs a healthy year), and posters routinely splice a stat from one season onto a claim about another. Reframe raw team splits (On-Off, team-offense-with-him-on) toward isolated impact (RAPM), which strips out how bad the supporting cast was without him. Do not correct a poster's season pedantically in public; fold the correct read in so the reply is simply right.
4. **Draft in Bobby's voice.** A few tight paragraphs, casual register (see Voice and format). Grant the point, sharpen or flip the frame, add the one angle they don't have, land it.
5. **Hand it back for editing.** Output the draft, plus a short note on which data or model output it used, plus any flags. Good flag set from experience: which cited stats are verified-safe, which are shaky or wrong (so he doesn't lean on them), any sub self-promo rule, and any place Bobby's own read should override. Bobby sharpens it and posts.

## Data sources

Use the existing stack. Pull only what the question needs and map to the live schema.

- **Cap and apron picture:** the current cap run (committed salary, distance to tax, first apron, second apron, available exceptions). This answers most "can we afford / can we sign / are we hard-capped" questions.
- **Trade grades:** `chain_engine.py` for multi-step sequences, `trade_search.py` / `evaluate_move.py` for single trades and CBA legality. This answers "should we trade X for Y," "is this deal legal," "does this help."
- **Player value and fit:** `player_value.csv` (RAPM blended with BPM), `player_surplus.csv` (value minus contract), `team_needs` / posture. This answers "is this player good," "does he fit," "is this contract worth it." Note the split: `consensus_off` / `consensus_def` / `consensus_net` are the blended value; RAPM (teammate-and-opponent-controlled) is the number to reach for whenever a post leans on a raw On-Off or team-split stat, because it is the deconfounded version of exactly that.
- **Championship evals:** the full player-specific evaluations in `lamelo/` (and clones like `alebron/`) hold deep, already-verified numbers on fit, availability, the defensive/offensive tax, sim-based title deltas, and built-in comparisons (e.g. the Gobert defensive-lift estimate). When a post is about a star the Wolves added or might add, fan out across that eval before drafting rather than re-deriving. These are also Bobby's published positions, so the reply must stay consistent with them.
- **Contracts:** the verified contract table for exact salaries, options, and Bird status.

Same integrity bar as the posts: every number traces to the model or a cap run, projections are labeled as projections, and anything selling-side or out-of-lane is flagged as lower-confidence rather than stated as fact.

## Voice and format

Fan tone, not journal tone. Confident, plainspoken, a little personality, no lecturing. Someone should be able to tell a real person who watches the games wrote it.

**Register: casual, the way Bobby actually types in a thread, not the way an article reads.** This is the single biggest correction from real use. Draft it lowercase and loose, not polished:

- mostly lowercase, including "i"
- soft hedges: "i feel like", "imo", "to me", "honestly"
- clipped, conversational rhythm and slang ("hits diff", "way bigger swing", "for sure")
- CAPS on one key word for emphasis instead of italics (e.g. "make ANT better")
- contractions welcome, comma-splices welcome; it should read like a text, not a paragraph
- still no em dashes or en dashes anywhere; commas, periods, parentheses only

The analysis underneath stays rigorous and every number still traces to the model. The casual surface is a delivery choice, not a license to get loose with facts. Do not fake typos; write clean but casual and let Bobby add his own.

Shape of a strong reply (this is the pattern that landed in practice):
1. **Grant the point in one clause.** Do not re-explain what the poster already said. "totally with you on the comp" and move on.
2. **Sharpen or flip the frame.** The marginal insight: the thing that is true but one level deeper than the post (e.g. the comp is real but it is not 1 to 1, it is floor vs ceiling).
3. **Add the one angle they don't have.** Usually a second-order or fit effect. If it is a common take, name the common take and go past it (see the false-novelty guardrail).
4. **One honest caveat, close human.** Name the real risk in a line, then end on the upside or a real-fan note. Do not end as a wet blanket.

Length: shorter than you think. Reddit is a few SHORT paragraphs and Bobby will trim from there, so cut anything the poster already said and anything that does not add. X is tighter, one or two sentences, compressed to the single sharpest point and the number that carries it.

## Guardrails that make it land

- **Add, never reiterate.** This is the most common failure mode in practice. Every sentence must add something the poster does not already have. Cut any line that re-explains or re-cites what is already in the post (if they made the comp, cited the number, or used the word "gravity," repeating it back is filler that reads as agreement padding). The value is the marginal layer, nothing else.
- **Don't claim false novelty.** "The part nobody is bringing up is X" is fragile and often wrong, because X is frequently a common take. Instead, name the prevailing take explicitly, then go one level past it: flip the direction or raise the magnitude. Example from real use: the common take was "Ant CAN play off-ball so Melo fits" (permission, coexistence); the sharper add was "Ant is BETTER off-ball than on-ball, so Melo could make ANT better" (an upgrade, not just tolerance). "yeah people say X, but it is actually bigger/backwards: Y" beats "nobody is saying X."
- **Answer the question asked, sized to it.** Match the depth of the reply to the depth of the ask. A simple hypothetical ("would you trade X for Y") gets a plain human take first (pick a side, say it like you'd type it), then at most one light grounded nugget on top. Do not turn it into a mechanics breakdown. The data is seasoning, not the meal, unless the post is genuinely a data or mechanics question. Tell: if you have talked yourself three reframes deep or are leading with the salary cap on a question about a player, you have probably answered a question nobody asked. The account is built by being the smartest voice, and the smartest voice also knows when the answer is just "yeah, obviously, because."
- **Additive, never contrarian for sport.** Add a layer nobody else has. "Here is a wrinkle the raw stats miss" beats "actually you're wrong." When correcting a shaky number, do it as a gentle nuance ("one nuance on that number"), not a gotcha, and fold in the honest version rather than just deflating theirs.
- **Lead with the surprising thing.** The edge is a model that produces takes people do not expect. The counterintuitive, defensible call is what makes someone click the name.
- **No links in the early going.** For a new account, earn the right to be heard first. The profile and flair or bio do the linking silently. Only share actual work once recognized, and even then as substance, not an ad.
- **Respect each community's rules.** Read the subreddit sidebar. Many have a self-promo ratio (e.g. a lot of helpful comments per link). Never post a bare "check out my article." If sharing an article, the analysis lives in the comment and the link is the source.
- **Match the room.** These are fans. Keep it human. You can be the smartest person in the thread without sounding like the driest.

## Worked examples

### Example 1: reframing a question (analysis shape)

**Reddit thread:** "Can we even afford to keep Ayo?"

Draft:

> The re-sign isn't really the question, the apron is. Ayo lands you right around the first-apron line. So it's not "can we afford the contract," it's "are we OK operating as a first-apron team," which costs you real tools. You drop from the full mid-level down to just the taxpayer version, and you lose the ability to bring anyone in through a sign-and-trade. If the front office believes in this core, you pay it and live with the smaller toolkit. If they think this group has a ceiling, that is the reason to hesitate. I'd pay it, his playoff shot-making earned the check, but it's a real fork, not a formality.

Why it works: reframes the question, drops one real constraint (the apron and what it costs), lands a clear take, and never mentions the site. Note this one is written toward the FORMAL end of the register; a live fan thread usually wants it looser and lowercase (see Example 2). The reframing discipline is the part to copy, not the polish.

**Same take, compressed for X:**

> Keeping Ayo isn't a money question, it's an apron question. His number puts MIN on the first-apron line, which means taxpayer MLE only and no sign-and-trades. I'd still pay him, but that's the real cost, not the salary.

### Example 2: replying to a good take (voice + add-don't-reiterate)

**Reddit post:** a strong, bullish take arguing the LaMelo trade mirrors the Gobert trade, "LaMelo raises the offense the way Gobert raised the defense," citing his huge On-Off and his EPM rank.

The post already made the comp, cited the On-Off, and used the word "gravity." So none of that goes in the reply. What the post did NOT have: that the comp is not symmetric, and what LaMelo does for Ant specifically. That is the whole reply.

Draft (his actual posted register):

> totally with you on the comp. i feel like gobert for sure raised the floor, did it every single night no matter what. melo's though i feel like is more of a ceiling instead of the floor, it only shows up when hes actually out there and when the fit clicks, so its a way bigger swing.
>
> yeah people are already talking about ant being able to play off ball so melo can run the show. but i think its actually bigger than that. ant isnt just able to play off ball, hes better off the ball than on it, like top 4 among stars in off ball efficiency. so its not really "can they coexist," its that melo taking the on ball load could make ant a MORE efficient scorer than he already is. only real question to me is if ant actually gives up those reps.
>
> only catch is health, but if hes out there this offense hits diff.

Why it works: grants the comp in one clause instead of re-explaining it, flips the frame (floor vs ceiling, not a mirror), names the common "Ant can play off-ball" take and goes one level past it (better off-ball, so it is an upgrade to Ant, not just coexistence), and closes on one honest caveat (health) without souring the room. Every claim traces to the eval (RAPM offense, the off-ball efficiency rank, the availability record), and it stays consistent with Bobby's published article on the trade.

## When to use, and when not to

Use it whenever Bobby wants to respond to a Wolves post or question on Reddit or X, or wants a fan question turned into a grounded reply.

Do not use it to post anything automatically, to generate piles of comments to scatter, or to make claims the data does not back. If the numbers aren't there, say so in the draft instead of inventing them.
