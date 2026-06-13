# Wolves to a T social clip template

A Remotion project that turns a D3 chart into a vertical (1080x1920) clip for
TikTok, Reels, and Shorts. Animation is timed to a script through a list of
"beats."

## One-time setup

Requires Node 18 or newer. From this folder:

```
npm install
```

## Preview while you build

```
npm run dev
```

This opens Remotion Studio in a browser. Scrub the timeline, edit any file in
`src/`, and the preview updates live. This is where you tune timing and look.

## The two ways to get a video

Path 1, clips for CapCut (do this now):

```
npm run render
```

Produces `out/clip.mp4`: the animated chart with captions, no audio. Drop it in
CapCut, record your voiceover over it, post. To caption inside CapCut instead,
render with captions off:

```
npx remotion render Clip out/clip.mp4 --props='{"showCaptions": false}'
```

Path 2, finished video in one command (do this later):

1. Record your voiceover and save it as `public/voiceover.mp3`.
2. Render with the audio baked in:

```
npx remotion render Clip out/clip.mp4 --props='{"voiceoverSrc": "voiceover.mp3"}'
```

You can pass any prop this way, or feed a whole file with
`--props=./myprops.json`, which is how your agent will batch out many clips.

## What to edit

- `src/config.ts` sets colors (the site design tokens), per-bucket gradients,
  fonts, the 9:16 size, and the safe margins. Tune the whole look here first.
- `src/timeline.ts` is the beat list: when each thing happens, the caption, and
  `focus` (which rows stay lit while the rest dim).
- `src/Root.tsx` holds the five-component fingerprint data passed as props.
- `src/LafiBarChart.tsx` is the chart itself.

The full script (voiceover plus captions) lives in `SCRIPT.md`.

## The look-and-feel layer

This clip is built to feel produced, not like a default slide. The pieces:

- `src/fonts.ts` loads real Inter + JetBrains Mono through Remotion so the render
  matches the website type instead of falling back to Helvetica.
- `src/Background.tsx` is the backdrop: a radial wash, a vignette, a faint
  brand-green glow up top, and fine film grain.
- `src/LafiBarChart.tsx` gives the bars depth: per-bucket gradient fills, a gloss
  highlight, a colored glow that brightens on the focused row, a gradient pickup
  zone with a glowing edge, pill labels, and hero percentile numbers. The chart
  also has a choreographed entrance (rows rise and stagger in, numbers count up).
- `src/Captions.tsx` renders a centered title-card for the hook, then a kinetic
  per-word lower-third with an accent bar and a legibility scrim.
- `src/ProgressBar.tsx` is the thin broadcast-style progress bar at the bottom.
- `src/animation.ts` holds every motion helper. Everything is a pure function of
  the current frame (no CSS transitions or d3 `.transition()`), which is what
  keeps the render clean.

See the parent skill's `references/` for the script formula and animation moves.
