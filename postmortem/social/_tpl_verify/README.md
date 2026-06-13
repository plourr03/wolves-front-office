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

- `src/config.ts` sets the palette (paste the source site's real tokens), the
  fonts, the 9:16 size, and the safe margins. Edit this first.
- `src/timeline.ts` is the beat list: when each thing happens, the caption, and
  `focus` (which rows stay lit while the rest dim).
- `src/LafiBarChart.tsx` is the chart. Replace it with your real D3 chart.
- `src/Root.tsx` holds the sample data passed in as default props.

## The look-and-feel layer (already wired)

These default to a restrained, editorial look so the clip does not read as an AI
template. You usually do not need to touch them.

- `src/fonts.ts` loads real Inter + JetBrains Mono through Remotion (swap for the
  site's typefaces) so the render does not fall back to system Helvetica.
- `src/Background.tsx` is a quiet backdrop: a soft gradient, a vignette, fine
  grain. No glow.
- `src/Captions.tsx` is an editorial chyron: a left-aligned lower-third with a
  colored rule and an optional chapter number, plus a centered card for a CTA.
- `src/animation.ts` holds the frame-driven helpers: `ramp`, `barGrow`,
  `rowSpotlight` (dim + blur the rows you are not on), `drawOn` (telestrator),
  `shake`, `pulse`. Everything is a pure function of the frame.
- `src/ProgressBar.tsx` is the thin progress bar.

The sample chart demonstrates the three reusable moves: a frame-driven draw, the
spotlight, and a hand-drawn telestrator circle on the focused number.

See the parent skill's `references/` for the script formula and the full menu of
animation moves.
