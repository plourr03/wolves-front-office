---
name: social-visuals
description: >-
  Turn a chart or visual into a short vertical social post for TikTok, Instagram
  Reels, and YouTube Shorts that tells a story with on-screen text and music and
  NO voiceover. Two hard rules: every number is validated against the data
  warehouse and never invented, and the post looks like a person made it rather
  than a generator. Use this whenever the user wants a quick visual post, a
  no-voiceover or music-only post, to turn a chart, shot chart, or comparison
  into a Reel or TikTok without recording audio, a data graphic for social, or
  mentions posting Wolves visuals. Trigger even if they just say "make a post out
  of this chart" or "turn this viz into something for Instagram."
---

# Silent data-driven social posts

Turn a chart or visual into a short vertical post for TikTok, Reels, and Shorts that tells a story with on-screen text and music, no voiceover. Two things are non-negotiable: every number is validated against the data warehouse (never invented), and the post looks like a person made it, not AI.

This shares the Remotion rendering engine from the social-clips skill, so reuse that template for the actual video build. This skill adds the three layers on top: the data-integrity contract, the silent text-driven narrative, and the human look.

## Order of operations (do not skip step 2)

1. Pick the story as a hypothesis. Decide the angle, but treat it as something to test, not assert. See examples/ant-playoff-scoring.md for a full run.
2. Validate the data first. Before building anything, list every on-screen claim, back each with a warehouse query, run them, and confirm the values. Read references/data-integrity.md. This is the rule that matters most: no number reaches the screen without a query behind it, and the story bends to the data, never the reverse. Use scripts/validate_claims.py to run the claims manifest and write a provenance log.
3. Write the silent narrative. Turn the validated numbers into a hook, build, turn, payoff, and sign-off, carried by short on-screen text for muted viewers and motion that changes every couple of seconds. Read references/silent-narrative.md.
4. Build it in the human look. Apply the editorial tokens (one accent plus a neutral, real type, grain, squared bars, restraint) so it matches the voiceover clips and does not read as AI. Read references/human-look.md.
5. Render for music. Use the social-clips Remotion setup to render the animated visual with the on-screen text and no audio track. Drop it into the editor, add music, post.

## If you are reusing an existing visual
Re-validate it. Re-run the queries behind every number in the visual and confirm they still match the warehouse. If anything disagrees, stop and surface it. Never publish a number you cannot trace.

## After building
Give the user a plain-language summary: what the post says start to finish, which numbers it shows and that they were validated (point to the provenance log), and the exact command to render it.

## Files
- references/data-integrity.md, the never-fabricate contract and validation workflow (read first)
- references/silent-narrative.md, the on-screen text beat structure and music notes
- references/human-look.md, the editorial design tokens
- scripts/validate_claims.py, runs a claims manifest against the warehouse and writes a provenance log
- examples/ant-playoff-scoring.md, a full worked example end to end
