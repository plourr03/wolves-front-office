---
name: trade-posts
description: >-
  Turn an NBA trade run through the trade model into a swipeable carousel post
  for Instagram and TikTok, showing the cap and apron mechanics, the
  championship-probability change, and the probability each team says yes. Every
  number comes from the model and nothing is invented, the post is framed as a
  hypothetical, and it uses the same human editorial look as the rest of the
  feed. Use this whenever the user wants to make a post out of a trade, a trade
  idea, a "what if" deal, a trade-machine style breakdown, or wants to run a
  fan-suggested trade through the model and post it. Trigger even if they just
  say "make a post out of this trade" or "what would X for Y do."
---

# Trade scenario carousel posts

Turn a trade run through the trade model into a swipeable carousel for Instagram and TikTok. The model is the source of truth for every number (salary matching, each team's books against the tax line and the two aprons, the championship-probability delta, and the probability each team says yes), and nothing on a slide is invented. The post is a debate starter, framed as a hypothetical, in the same human editorial look as everything else you make.

This reuses the human look and the Remotion setup from the social-clips and social-visuals skills. Each slide is rendered as a still image, not a video.

## Order of operations (step 2 is the rule that matters)
1. Run the trade through the model. Take the trade, yours or one from the comments, and run it to get the full output: salary matching and legality, each team's resulting books versus the tax line and both aprons, the title-odds delta, and the say-yes probabilities.
2. Use only model numbers, never eyeball them. Every figure on every slide traces to that model run. Cap and apron numbers especially must be exact. Read references/playbook.md, and see the data-integrity reference in the social-visuals skill for the full contract and provenance workflow.
3. Build the six slides. Hook first, receipts after. The full template is in references/playbook.md.
4. Apply the human look. Same tokens as the rest of the feed: one accent plus a neutral, real type, monospace numerals, a whisper of grain, squared corners, restraint. See the human-look reference in the social-visuals skill.
5. Render each slide as a still and assemble. Build each slide as a composition and render it with `remotion still` at 1080 x 1350 (portrait carousel). Upload the PNGs in order.

## Framing and guardrails
- Hypothetical, not news. Tag every trade post as a hypothetical or trade idea so you are never mistaken for a rumor account.
- The say-yes number is only model-backed when MINNESOTA is acquiring. The acceptance model is validated only for whether a partner accepts a deal the Wolves are acquiring in (offseason/docs/acceptance_model_scope_and_limitation.md); a realized-trade backtest showed it does not generalize to arbitrary trades. So for a fan trade where the Wolves are not a participant acquiring a player, present "would they say yes" qualitatively, not as a model percentage. The cap/apron and title-odds numbers are fine for any trade; only the say-yes probability carries this scope.
- Modeled numbers are estimates, and you say so. "My model says" the title-odds delta and the say-yes probabilities. That honesty is also your most ownable line.
- End on a question. The verdict plus "would you do it?" drives comments, and the recurring "drop a trade and I'll run it" turns the audience into the content pipeline.

## After building
Give the user a plain-language summary: the trade, the headline number, what each slide shows and that every figure came from the model run, and the command to render the slides.

## Files
- references/playbook.md, the six-slide anatomy, framing guardrails, and the data rule
- examples/fox-for-randle-divincenzo.md, a worked example mapping model output to slides
