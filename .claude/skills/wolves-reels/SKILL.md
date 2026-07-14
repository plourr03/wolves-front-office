---
name: wolves-reels
description: >-
  Build a Wolves to a T data-story reel end to end, exactly the way Bobby
  settled on with the One Summer reel (July 2026): a 9:16 Remotion video in the
  verdict-carousel look, voiced by his ElevenLabs clone, one point told slow
  over a hero chart, every number receipted against FINAL exports. Use this
  whenever Bobby wants a reel, a video for an article or series, a "one summer
  style" video, a voiced chart story, or to market a piece on TikTok/IG/Shorts.
  This SUPERSEDES the generic social-clips skill for Wolves reels; reach for
  social-clips only for quick CapCut-path chart clips.
---

# Wolves to a T reels, the settled pipeline

The canonical reference implementation is `pick2033/social/one-summer/`
(Remotion project + `scripts/make_ai_vo.py`). Copy that project for a new reel
and swap the content; eleven cuts of iteration are baked into it. This file is
the taste and the process; the project is the code.

## The look (locked, do not relitigate)

- Palette from `lamelo/slide/render_lamelo_carousel.py`, verbatim: midnight
  navy #051223 to #0B1E35, tile #102136, hair #263C56, ONE accent (dream-tail
  green #84D668, pop #96E670), slate #96A8BE, mute #657991. One faint green
  aurora top-right, whisper of grain (0.05), squared corners, flat fills.
- Faces: Bahnschrift Bold (display), Consolas Bold (all numerals), Segoe UI
  (captions/body), Ink Free (the one marker scrawl) — Windows system fonts
  first with Google fallbacks (Oswald/JetBrainsMono/Inter/PermanentMarker).
- Chrome: the green gradient bar at y0 and WOLVES TO A T at top 236 (inside
  the safe zone), left-aligned. NOTHING else: no date, no series label, no
  chapter chips on captions (the small green caption rule stays).
- Safe zones: critical copy inside the 4:5 center crop (y 285-1635) and above
  the bottom 420px. Captions: Segoe 600 ~48px, max two lines, lower third.

## Structure (what hooks Bobby's audience)

- COLD OPEN ON THE HERO CHART with a claim in the first breath. Number-first
  rug-pull beats setup ("odds this year? about 1 percent" ... then the cliff).
  The chart title, first callout, and caption must be legible inside 0.5s,
  with the line already drawing. Never open on a statement card.
- One point per reel, told slow. 60-70s is fine when every beat pays. Deep
  cuts breathe: a move at the top of each beat, then stillness.
- Statement cards (Bahnschrift, one line green) are breathers between acts;
  the thesis card sits right before the twist. The twist (e.g. the NO
  EXTENSION stamp) lands mid-video. CTA = COMMENT "KEYWORD" card + a spoken
  open-loop question; keyword wired in ManyChat to the article DEEP LINK.
- Loop: the tail hard-cuts back to an early frozen state of the opening scene
  (mid-setup, pre-reveal) so a rewatch reads as intentional. No dissolve into
  the loop.

## Motion (weighty, editorial, never slammy)

- Entrances are riseIn (0.55s confident ease); transitions are 0.45s
  directional dissolves (outgoing drifts up 44px and fades, incoming rises);
  each scene carries a 1.6% push-in across its whole window so holds stay
  alive. Everything is a pure function of frame.
- The hero chart draws length-parametrized (cumulative segment fractions) so
  the reveal lands ON the spoken word: idle along the flat stretch during
  setup, race up the spike on cue, crash the tail after. Key every callout,
  band, telestrator circle, scrawl, and stamp to the exact spoken moment.
- One telestrator moment per reel (Ink Free scrawl + hand-drawn ellipse +
  little arrow). Stamps get stampIn + a 0.4s shake, landing in an empty band
  of the document so the stamped text stays readable (mute pass).

## Voice pipeline (scripts/make_ai_vo.py)

- ElevenLabs clone, resolved BY NAME (`--elevenlabs-name "upbeat bob"`), key
  from repo `.env` ELEVENLABS_API_KEY. Quota errors = the per-key credit cap;
  have Bobby raise it in the key settings, don't make a new key.
- One clip per caption beat, each generated with previous_text/next_text so
  lines flow. Base settings stability 0.42 / style 0.25 (calmer WON; the
  expressive 0.30/0.45 read as weird exaggeration). Per-line
  SETTING_OVERRIDES for problem lines; `--only id1,id2` regenerates just
  those. This voice reads SLOW: global atempo 1.09, hero-chart act 1.13,
  applied per clip BEFORE probing so beat starts stay true.
- 150ms tail fade baked into every clip in numpy (the bundled Remotion ffmpeg
  has no afade/volumedetect/atempo-in-complex; call
  node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe directly, never
  through npx.cmd, which mangles | and ; in filter args).
- Gaps: audio is the master clock. GAP_AFTER per beat (0.3-0.6 inside a
  thought, 0.6-0.9 between ideas, ~2.2s CTA dwell); the script prints the
  timeline.ts starts to paste. Long sentences page across caption-only beats
  (~50-60% into the clip).
- Bed: original synthesized heartbeat ONLY (54Hz thump, 72bpm, BED_GAIN 0.10,
  fade in/out). NO tick/hi-hat, it pokes through speech and reads as noise.
  Mix loudnorm to -14 LUFS. `--assemble-only` remixes without regenerating.
- Bobby's real closet recording remains the ideal; the clone ships fine WITH
  the platform AI-content label ticked (Meta may auto-label anyway).

## Words and rigor (the house rules that bit us)

- Captions match spoken words verbatim (grammar-normalized), two lines max.
  Say "percent" out loud after numbers. No em/en dashes anywhere; no
  "honestly/genuinely/actually." Bobby's rewrites are authoritative; fix
  typos and units silently but FLAG meaning changes (his "37 percent" meant
  37 GAMES; check every unit).
- Every on-screen number from a FINAL export with a receipt printed in-session
  (src/data.ts carries exact floats + provenance comments). Nothing eyeballed.
- Band language: "as high as X" for an 80% band top, NEVER "upwards of X"
  (overclaims). If the voice says a band top, DRAW the band and put the big
  number at the band top with the point-estimate dot honest below it and the
  band printed ("80% BAND: A TO B").
- When two true numbers share digits across assets (the two 56s), label
  loudly or cut one; a freak collision confuses even sharp readers. Keep
  each reel in ONE metric where possible.
- Contract years: never say "N years left" (fan-inclusive vs
  at-decision-moment counting fight); name the end date ("under contract
  until the summer of 2029").
- "About" stays in front of rounded model numbers.

## Process

1. Verify every number against exports FIRST; print receipts.
2. Copy `pick2033/social/one-summer/`, swap data.ts + scenes + SEGMENTS.
3. `npx tsc --noEmit`, then stills at the key beats (hook frame ~15, each
   reveal, the twist, CTA, loop) and actually look at them before any render.
4. Full render with `--props voiceoverSrc`, copy deliverables to
   `<project>/social/outputs/`: the mp4, cover still, caption kit
   (post caption in Bobby's lowercase voice + hashtags 3-5 + alt text +
   keyword + story copy + VO script with per-beat screen descriptions), and a
   render report with QA gates and fact records.
5. Commit every cut. Iterate by named line: Bobby gives notes per line, use
   `--only` + overrides + gap tweaks; the script reprints starts; paste into
   timeline.ts (use the Write/Edit tools for captions, bash heredocs mangle
   \n into real newlines).
6. Ship checklist: the ARTICLE must be live first; ManyChat keyword tested to
   the deep link; AI label ticked; morning-of re-check of any live factual
   claim in the reel (extension/signing status kills beats); same-day story
   slide with link sticker.
