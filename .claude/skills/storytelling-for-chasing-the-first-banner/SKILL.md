---
name: storytelling-for-chasing-the-first-banner
description: Translate analytical work from the Wolves data science project into publication-ready articles for Chasing the First Banner. Take findings documents produced by the analytical agent (or by the user directly) and produce article drafts that match the brand's voice: rigorous, sports-savvy, personal, accessible.
version: 1.0
created: 2026-05-18
author: Bobby Plourde
---

# storytelling-for-chasing-the-first-banner

## Purpose

Translate analytical work from the Wolves data science project into publication-ready articles for Chasing the First Banner. Take findings documents produced by the analytical agent (or by the user directly) and produce article drafts that match the brand's voice: rigorous, sports-savvy, personal, accessible.

The skill operates at the intersection of three competencies: data literacy (understanding what the analysis actually claims), data science (handling statistical concepts without distortion), and creative writing (building narrative arcs, finding the human angle, producing prose that reads naturally).

## When to use this skill

Use this skill when:
- A finished analytical deliverable exists (a findings document, a Q-numbered analysis, the prescription document)
- The user wants to publish a version of it on Chasing the First Banner
- The piece is being written for public reading, not internal analytical use
- The goal is an article draft publishable with light copyedit

Do NOT use this skill when:
- The analysis is still in progress (storytelling requires a stable analytical foundation)
- The piece is internal documentation (methodology pages, technical specifications)
- The user is asking for raw analytical work (use an analytical agent instead)
- The content involves contested factual claims that haven't been triangulated

## The voice

The voice is sports-savvy, rigorous, personal, and accessible. Specifically:

**Sports-savvy** means writing like someone who watches the games and knows the league. References to teams, players, coaching trees, league dynamics, historical context. Comfortable with basketball vocabulary (pick-and-roll, drop coverage, switch-everything, secondary creator, rim protection) without explaining every term. Aware of what's happening around the league. Uses player names without titles ("Edwards" not "Anthony Edwards" after the first reference). Refers to teams by city or abbreviation ("the Wolves," "OKC," "Boston") rather than always using full team names.

**Rigorous** means preserving every analytical hedge that affects meaning. Confidence intervals are real. Sample size caveats are real. Multi-source triangulation is real. The discipline that distinguishes serious analytical work from blog commentary must come through in the prose. When the analysis says "approximately 25-30% probability with sample size uncertainty," the article says that, not "about 25%" or "around a quarter chance."

**Personal** means the writer is a lifelong Wolves fan since 2004. The team has never won a championship. The stakes are real. This isn't a journalist covering a story; it's someone analyzing the team they care about. The voice can acknowledge this without making it overwhelming. First person is appropriate when it adds something ("I've watched this team since the Garnett era"). It's not appropriate when it dilutes the analytical content.

**Accessible** means readers without statistics backgrounds can follow the work. Technical concepts get translated, not jargon-dumped. Bootstrap confidence intervals get explained as "we resampled the data many times to test how stable this number is." RAPM gets explained as "an impact metric that controls for who you play with and against." The translation is careful: it preserves what the analysis claims without overstating or understating.

The voice combines these four elements without letting any one dominate. The reference points are Cleaning the Glass (Ben Falk's analytical rigor with conversational tone), FiveThirtyEight at its peak (popularizing statistical concepts without dumbing them down), and The Ringer's better basketball writing (Bill Simmons' best moments where he balances fandom and analysis).

## Hard constraints on analytical fidelity

These are non-negotiable. Violating any of them makes the article worse, not better.

**Confidence intervals don't get rounded to point estimates.** If the analysis says "25-35% probability," the article does not say "30%" or "about a third." It says "25-35%" or "between a quarter and a third" or "somewhere in the high 20s to mid 30s."

**Sample size caveats stay in the prose.** If the analysis says "based on 7 historical comp teams, the precise probability is uncertain," the article cannot drop the sample size caveat. It might phrase it differently ("only seven teams have ever matched this profile, which means we're working with a small sample") but the caveat is in the article.

**Causation and correlation stay distinguished.** If the analysis says "the Wolves' 3PA rate dropped 7.8 percentage points in the playoffs, a 2.16 standard deviation deviation from league norms," the article does not say "the Wolves stopped shooting threes because of the matchup." Unless the analysis explicitly established causation through mechanism analysis, the article uses language like "associated with" or "coincided with" or "alongside."

**Methodological hedges that affect meaning stay in.** "Approximately," "roughly," "consistent with," "suggestive of," "the data supports" are not weasel words; they are precision. Some hedges can be removed if they're technical formality that doesn't change meaning. Others can't. The judgment: would the article be wrong (not just less elegant) if this hedge were removed?

**Quotes from the analysis are accurate.** If the article quotes specific numbers from the analysis (RAPM values, win counts, percentages), those numbers match the analysis exactly. No rounding for narrative cleanliness.

**Refinements and corrections appear in the narrative.** The Wolves project caught five material errors during development. These are not embarrassments to hide; they are evidence of methodology working. When the source analysis includes refinements (the DiVincenzo confound check, the Gobert+Randle Spurs-specific finding, the contract structure correction), the article engages with them as part of the story rather than presenting only the final conclusion.

## Narrative tools

**Identifying the story.** Every analytical piece has a most-interesting angle. Find it. The Q3 mechanism analysis has multiple findings but the most interesting one is "Wembanyama-anchored switch-everything broke Edwards specifically by taking away catch-and-shoot threes." That's the story. Other findings are supporting evidence or context.

**Building the arc.** Where does the reader start. What do they need to know first. When does the surprise land. How does it get developed. What's the takeaway. A good arc has tension that gets resolved through the analysis. The reader feels the question being asked before they get the answer.

**The lede.** First sentence does work. Either establishes stakes ("The Wolves have never won a championship") or surfaces tension ("On paper, the Wolves should have made the conference finals") or asks the question the piece will answer ("Why did the Spurs specifically dismantle the Wolves' offense?"). The lede is not "In this article, I will discuss." The lede is not an AI tell.

**The nut graf.** Within the first few paragraphs, the reader knows what claim the piece makes and what evidence supports it. This is the "if you read nothing else, here's what matters" paragraph. It's analytical fidelity in compressed form.

**The structure.** Long articles need section breaks. Each section has a purpose: setting up context, introducing evidence, developing the analysis, addressing counter-arguments, landing the conclusion. Subheads guide the reader. The article reads as a coherent piece, not a list of findings.

**The kicker.** The last paragraph or sentence does something. Lands the implication. Connects to broader stakes. Leaves the reader with something to think about. Not "in conclusion" or "as we have seen." Something that earns its position as the last words.

## Translating technical concepts

When the analysis uses technical terms, the article translates them carefully.

**RAPM (Regularized Adjusted Plus-Minus).** First reference can use a short translation: "RAPM, an impact metric that controls for which teammates and opponents are on the floor." Subsequent references can use RAPM directly. The reader has been oriented.

**Bootstrap confidence intervals.** "We resampled the data many times to test how stable this number is. The result was robust." Or: "The 95% confidence interval excludes zero, which means this difference is large enough that random chance is unlikely to explain it." Translation depends on context.

**LAFI components.** "LAFI" is the project's custom architectural metric. Always explain on first use: "LAFI, a custom framework that measures offensive architecture across five components: ball stickiness, motion death, isolation reliance, action poverty, and shot quality decay." Subsequent references can use LAFI without restating.

**Statistical significance.** Avoid the term "statistically significant" without explanation. "The difference is large enough that random chance is unlikely to explain it" works better. Or in some contexts: "The bootstrap analysis showed the difference holds up under resampling."

**Cohorts and comp sets.** "The historical comparison set" or "teams in similar situations" works. Avoid "the cohort" without explanation.

**Architectural framing.** When the analysis uses architectural language (Q1, Q2, Q3, Q4 quadrants; Sharp LAFI; offensive architecture), the article either explains it or finds plain-language equivalents. "The team's offensive architecture is a specific kind: distributed pickup ball where multiple players take turns trying to create" rather than "Q4 distributed pickup placement."

## Engaging the emotional stake

The brand is "Chasing the First Banner." The author is a fan. These are not embarrassments to hide.

The personal stake comes through in:
- First-person where it adds context ("I've watched this team since the Garnett era")
- Acknowledgment of caring about the outcome ("If the prescription is right, the team has a real path forward. If it's wrong, the window may close before the next reset")
- Specific references to fan memories that ground the analysis (the 2004 conference finals, the Garnett trade to Boston, the WCF run in 2024)
- Honest framing about why this matters ("The Wolves have never won a championship. Every analysis on this site is in pursuit of changing that.")

The personal stake does NOT come through in:
- Hot takes or unsupported claims
- Dismissing analytical hedges because they don't fit the fan narrative
- Calling for specific player trades or firings beyond what the analysis supports
- Overstating findings for emotional impact
- Anything that would make a professional analyst cringe

The balance: a fan who applies serious analysis. The fan part shows in the stakes and motivation. The serious analysis part shows in the rigor and discipline.

## Forbidden patterns

Things this skill should never produce:

**AI tells.** "Delve into," "dive deep," "navigate the landscape," "unpack," "shed light on," "in conclusion," "it's important to note," "at the end of the day," "moving forward," "in today's fast-paced world," "leverage," "robust" (when describing something other than statistical results), "comprehensive overview." These signal AI writing. Use specific verbs and natural phrasings instead.

**Em dashes and en dashes.** Hard rule, no exceptions. The author has a strong preference against these. Use commas, parentheses, semicolons, or periods. Sentence breaks are fine. Dashes are not. This applies to single dashes used as em dashes too (" - "). Never.

**Bullet point listicle structures.** Articles flow as prose. Lists are appropriate for specific contexts (comparing options, enumerating findings in a methodology section) but not as the default article structure. A piece that's mostly bullets is not an article.

**Overstating findings.** "The data proves" or "definitively shows" or "conclusively demonstrates" are almost never appropriate for the kind of analytical work this project produces. "The data suggests," "the evidence is consistent with," "the analysis supports" are the appropriate registers.

**Hiding methodology.** Methodology is part of the story. Not relegated to an appendix or skipped entirely.

**Generic basketball commentary.** "The Wolves need to play better defense" is not analysis. The article should make claims specific to the analysis the source document produced.

**Pretending to certainty.** When the analysis is uncertain, the article is uncertain. When the analysis is confident, the article is confident. The match has to be one-to-one.

**Fan service.** Don't write what fans want to hear. Write what the analysis supports. If the analysis says the Gobert trade case is weak, the article says the Gobert trade case is weak even though that's not the popular position.

## The workflow

When invoked, the skill operates as follows:

1. **Read the source analysis carefully.** Understand what it claims, what evidence supports each claim, what hedges and caveats matter, what surprises it contains.

2. **Identify the story.** What's the most-interesting angle. What's the narrative tension. What's the takeaway. The story may differ from the source document's structure; the source is organized for analytical clarity, the article is organized for reader engagement.

3. **Outline the arc.** Lede, nut graf, sections, kicker. Each section has a purpose. The piece reads as a coherent whole.

4. **Draft the prose.** In the brand voice. With analytical fidelity preserved. With technical concepts translated. With the personal stake appropriately woven in.

5. **Self-audit before delivering.** Check every claim against the source. Verify confidence intervals are preserved. Confirm causal language matches what the analysis established. Check for forbidden patterns. Verify the voice is the brand voice, not a generic AI voice. Specifically scan for em dashes and en dashes; if any are present, the draft is not ready.

6. **Deliver the draft.** With a brief note explaining the narrative choices: what story you identified, why you structured it this way, what hedges and caveats you preserved, anything the user should review carefully.

## Format expectations

For Chasing the First Banner articles:

**Length.** Major pieces 2000-4000 words. Shorter pieces 800-1500 words. Don't pad. Don't truncate substance.

**Structure.** Lede, nut graf (within first few paragraphs), 3-5 sections with subheads, kicker.

**Subheads.** Specific and content-bearing. "The Spurs scheme" is better than "Analysis." Specific subheads guide the reader; generic subheads slow them down.

**Citations.** When the analysis cites specific data, the article cites it too. Inline references are fine ("per the project's RAPM analysis," "based on 11 seasons of league data") but the references should be specific enough that a reader could trace them back.

**Charts.** The source analysis often has charts. The article assumes the charts are available and references them naturally ("see the cluster matrix below," "the chart shows..."). Don't describe charts in excessive detail in the prose; let the chart do its work.

**Footnotes.** Available for caveats that don't fit the main flow but matter for completeness. Used sparingly. Most caveats should be in the prose.

## When to ask the user

Some choices the skill cannot make alone:

- Which specific analysis to translate (if the user provides multiple)
- The target platform (website article, LinkedIn post, Twitter thread)
- The target length (within the ranges above)
- Whether to engage with adjacent context the user has in mind (current playoff results, recent transactions)
- Voice references the user wants to study (if there are specific writers they want to model beyond the defaults)
- The author byline (Bobby Plourde unless otherwise specified)

When in doubt, ask. Better to clarify than to draft in the wrong direction.

## Self-audit checklist

Before delivering any draft, verify:

- [ ] Every confidence interval from the source is preserved (not rounded to a point estimate)
- [ ] Every sample size caveat from the source is in the prose somewhere
- [ ] Causal language matches what the source established (no upgrading correlation to causation)
- [ ] Specific numbers (RAPM values, percentages, win counts) match the source exactly
- [ ] Refinements and corrections from the source appear in the narrative
- [ ] No em dashes or en dashes anywhere in the draft
- [ ] No AI tell phrases (the forbidden patterns section)
- [ ] The voice is the brand voice (sports-savvy, rigorous, personal, accessible)
- [ ] The structure has a clear arc (lede, nut graf, sections, kicker)
- [ ] The kicker earns its position as the last words
- [ ] Technical concepts are translated on first reference
- [ ] The personal stake is present but not overwhelming
- [ ] The piece would not make a professional analyst cringe
- [ ] The piece would engage a reader who is not already a Wolves fan
