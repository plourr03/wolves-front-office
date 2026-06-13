---
name: social-clips
description: >-
  Turn an existing D3 (or any SVG/JS) data visualization into a vertical 9:16
  short video for TikTok, Instagram Reels, and YouTube Shorts, with frame-precise
  animation (chart draws in, a data point is spotlighted, big captions) timed to a
  spoken script. Produces both editable animated clips to finish in CapCut and a
  one-command auto-rendered MP4 with baked-in voiceover. Use this whenever the
  user wants to make a social clip, Reel, TikTok, Short, or "video version" of a
  chart or analytics visual, wants to promote a Wolves to a T article or a LAFI
  insight on social, asks to "optimize a visual for Instagram or TikTok," or
  mentions turning charts into video. Trigger even if they just say "make a clip
  of this chart," "how do I post this to TikTok," or "animate this for Reels."
---

# Social clips from D3 visuals

Turn a chart that already exists in a D3 project into a vertical short for
TikTok, Reels, and Shorts. The chart code is reused as-is for its look. Movie
style animation (a reveal, a spotlight, a hand-drawn mark) gets layered on top
and timed to a spoken script, so the picture moves exactly when the words land.

The tool underneath is Remotion, which renders React and SVG to video frame by
frame. D3 charts are SVG, so they drop straight in.

## What you produce

Two outputs from the same project, both supported:

1. Clips for CapCut (the default). A silent animated MP4 with captions. The user
   records voiceover over it in CapCut and posts. This is the path to use first.
2. A finished video in one command (later). The user records a voiceover, drops
   it in `public/`, and renders once to get a complete video with audio.

## Make it feel human, not a template (this is the whole game)

The fastest way to lose a viewer is for the clip to look AI-generated. The
"default premium" motion-graphics look reads as cheap and kills credibility,
especially for a real publication. These specifically read as AI slop, so avoid
them unless asked:

- Radial-gradient backgrounds, green/colored glow blooms, heavy drop-shadow on
  every bar, neon colors, thick film grain.
- Centered captions where every word bounces/springs in one at a time (kinetic
  text). This is the single biggest tell.
- Everything centered and symmetric; constant motion with no rest.

What reads as a person made this, on purpose:

- **Match the source publication's real design tokens.** Pull the site's CSS
  custom properties (its exact `--accent`, `--status-error`, background, text
  colors) and use them, so the clip looks like the published chart, not a
  template. For Wolves to a T, see the `viz-builder` skill's token table.
- **Use the real fonts.** Load the site's typefaces through `@remotion/google-fonts`
  (`fonts.ts` in the template). System Helvetica fallback looks cheap instantly.
- **Flat, article-style marks on a quiet backdrop.** A near-flat dark background
  and solid bars beat gradients and glow.
- **Real holds and stillness.** Something changes every beat, but let an idea
  breathe (8 to 10 seconds for a deep clip) instead of flashing. A move at the
  top of a beat, then rest, reads as confident.
- **Film-room annotation.** A hand-drawn telestrator circle around the number
  you are discussing (an ellipse drawn on with `pathLength` + `strokeDashoffset`,
  rotated a few degrees) is the strongest "a person broke down this film" signal.
- **An editorial chyron, not kinetic text.** Left-aligned lower-third, a small
  chapter number (`01 / 05`), a rule in the data's color, whole lines that fade
  in. Reserve centered title cards for only the hook and the closing CTA.
- **The user's voice, verbatim.** Their phrasing in the copy is most of the
  humanity. Do not sanitize it.

The template already defaults to this editorial look. Hold the line on it.

## The workflow

### Step 1: Get the project ready

A ready-to-run Remotion project is bundled at `assets/template/`. If the user
has no clip project yet, copy that folder to a working location and install:

```
cp -r assets/template <user-project>/social-clips
cd <user-project>/social-clips
npm install
```

Put clip projects somewhere sensible (e.g. `<repo>/social/<clip-name>/`) and let
`node_modules/` and `out/` be gitignored (the template ships a `.gitignore`). If
the user already has a clip project from a previous run, reuse it and skip the
copy. Requires Node 18+. Remotion downloads its own Chromium on first install,
so do the install and render in the user's real environment, not a locked-down
sandbox.

### Step 2: Write the script

One clip makes one point and pays it off completely on its own (it is not a
trailer for an article). Read `references/script-formula.md` and write the
script: a hook with stakes, the reveal, the insight and what it cost, the call to
action. Two lengths both work: a punchy ~20 to 30s cut, or a deep ~60 to 90s cut
that gives each idea 8 to 10 seconds with real holds.

Size every beat to how long the line actually takes to say (about 3.3 words per
second). Do not pack a 20-word sentence into a 3-second window. Confirm the
script with the user before building, because everything else is timed to it.

### Step 3: Build the clip

Edit these, in order:

`src/config.ts`. Set the brand once: paste the source site's exact color tokens
and the safe margins. 9:16 size, 30fps, and real fonts (`fonts.ts`) are wired.

`src/Chart.tsx` (the example is `LafiBarChart.tsx`). This is the chart and the
part to swap. Bring in the user's real D3 chart. Keep the D3 that defines the
look (`scaleLinear`, `scaleBand`, axes, line/area generators, color encodings,
data shaping). Delete the D3 that animates (`.transition()`, `.duration()`,
`.ease()`) and recompute every moving value from the frame. See
`references/shot-grammar.md` for how a line, scatter, or fingerprint reveal
differs from a bar reveal, and for the spotlight and telestrator moves.

`src/Root.tsx`. Put the real chart data here as the composition's default props.

`src/timeline.ts`. Place one beat per script line: a start time in seconds, a
kind, the on-screen caption, and `focus` (which rows stay lit while the rest dim).
The clip length is derived from the beats. Use the moves and timing rules in
`references/shot-grammar.md`.

Multi-scene clips (e.g. a fingerprint that cuts to a league ranking) are fine:
render scene A or B by frame with a short crossfade, and key each scene's
internal timing off the cut second.

Preview with `npm run dev` (Remotion Studio) to scrub and approve timing.

### Step 4: Render

Clips for CapCut (do this first):

```
npm run render
```

Outputs `out/clip.mp4`, animated with captions, no audio. To caption inside
CapCut instead of burning them in:

```
npx remotion render Clip out/clip.mp4 --props='{"showCaptions": false}'
```

Finished video with voiceover (later): save the recording as
`public/voiceover.mp3`, then

```
npx remotion render Clip out/clip.mp4 --props='{"voiceoverSrc": "voiceover.mp3"}'
```

Any field can be overridden with `--props`, or a whole JSON file with
`--props=./props.json`, which is how to batch many clips from one project.

## Verify before the long render

A full render of a 90s clip is minutes; a still is seconds. Always:

1. `npx tsc --noEmit` first. It catches wiring mistakes (bad imports, a renamed
   prop) in a second, before you wait on a render. A removed import that is still
   referenced will pass esbuild but crash the render, so trust tsc.
2. Render a handful of stills at the key beats and actually look at them:
   `npx remotion still Clip out/stills/f<N>.png --frame=<N>`. Check the hook, the
   full chart, each spotlight, and the close. Fix layout there, then render the
   whole thing once.

## Rules that keep renders clean

Drive every animation from the frame. Never use D3 `.transition()`, CSS
transitions, CSS keyframes, or Tailwind animation classes. They run on wall-clock
time, not the render clock, so frames land wrong and the video flickers. Use
`useCurrentFrame()` with `interpolate` and `spring` (see `src/animation.ts`).

Reuse the chart's scales and encodings, not its animation. Match the look,
recreate the motion frame-driven.

Keep it readable on a phone. Big fonts, few gridlines, no dense legends, one idea
on screen. Do not crowd a row with a label, a sub-description, a bar, and a
number all at once; it reads as squished. Drop what the voiceover already says.

Put any asset (a voiceover, a logo) in `public/` and reference it with
`staticFile()`.

## Gotchas that cost real time

- **Bar width when the scale does not start at zero.** For a domain like
  `[40, 100]`, `x(0)` is extrapolated far off-canvas (negative), so a bar drawn
  with width `x(value) - x(0)` runs hundreds of pixels off the right edge.
  Measure from the axis start: width is `x(value) - barStartX`.
- **Do not zoom a single full-width row.** A camera zoom on a row whose content
  spans the whole width pushes the left label and the right-aligned number (and
  any circle around it) off the edges. For vertical charts, focus with a
  spotlight (dim + blur the other rows) instead. If you genuinely need a zoom,
  keep content well inboard or anchor the transform origin on the side you cannot
  afford to lose.
- **Spotlight without flicker.** Cross-fade each row's opacity and "lit" amount
  from the previous beat's target to the current beat's over ~0.3s. If you just
  snap to the active beat, a row that stays dim across two beats flashes.
- **Match the Remotion versions.** Install companions like
  `@remotion/google-fonts` at the exact core version (`@4.0.x`), or fonts/render
  break. `npx remotion versions` checks.
- **Use real data.** If the closing chart needs values you do not have, pull them
  (warehouse, a CSV in `outputs/`) rather than inventing them. These ship on a
  real publication.

## After building

Tell the user, in plain language, what the clip says start to finish and what
changed since last time, so they can follow without reading the code. Then give
the exact command to run and the file it produces.

## Optional extras

`npx remotion versions` validates package versions if an install looks off.
Remotion also ships its own deeper skill via `npx remotion skills` for advanced
effects beyond this workflow.
