# One Summer reel, render report (2026-07-14, third cut: hook-led)

## What this cut is

Cut 1 was the brief's montage (Bobby: too much, too trailer-ish). Cut 2 rebuilt
it as one point told slow in the verdict-carousel language. This cut keeps cut
2's spine and applies Bobby's three notes: a big-stat cold open (the giant
green 44% is frame one, fully legible inside the first second, and the loop
lands back on it), chrome pared to just the wordmark at the very top (no date,
no series label, no chapter chips), and upgraded transitions (every beat change
is a directional dissolve: the outgoing scene drifts up and fades as the next
rises from below, one continuous upward gesture; the loop return stays a hard
cut on purpose).

- 40.1 seconds, 1080x1920, 30fps, 4.1 MB (`one_summer_reel.mp4`), silent with
  burned captions (the record-VO-later path), plus the grid cover and this kit.
- Palette lifted verbatim from `lamelo/slide/render_lamelo_carousel.py`:
  midnight navy #051223 to #0B1E35, the dream-tail green rgb(132,214,104) as
  the only accent, slate and mute for quiet text, one faint green aurora, a
  whisper of grain. Faces are the carousel's real ones (Bahnschrift Bold,
  Consolas Bold numerals, Segoe UI, Ink Free scrawl; Google-font fallbacks
  wired for portability). Masthead on every frame like the slides: WOLVES TO A
  T left, PRICING THE LAMELO TRADE · 07.14.26 right in green.
- Seven beats, one hero visual each, weighty rises instead of slams, real
  holds. The montage cut (49 wins / 62% / 70x card / clocks / invoice / equity
  / part-cards / pass-fail) is in git history if ever wanted back.

Beat by beat: the 44% cold open (ANT'S ODDS OF LEAVING / IN THE 2029 WALK
YEAR.); a statement card (IT COMES DOWN / TO ONE SUMMER. in green); 2029 giant
with ANT'S WALK YEAR; the hazard curve drawing slowly and owning about twelve
unbroken seconds (1% callout at two-years-left, the 44% spike in green paying
off the hook, a hand-drawn circle, "the cliff" in marker with a hand arrow, the
80% band, and a method line that fades in on the hold: 50,000 paths, ~70x
mid-contract, band 35 to 53); the LaMelo contract card taking the UNSIGNED
stamp; TWO MAX GUYS. / ONE SUMMER. as the landing statement; COMMENT "BILL"
with wolvestoat.com; and a half-second hard cut back to the 44 card so the loop
reads as intentional. Editorial lower-third captions match the spoken words
verbatim throughout.

## Numbers on screen, verified against sources before render (gate 1)

| On screen | Value used | Source verified |
| --- | --- | --- |
| hazard curve shape | central_win60 annual means, exact floats | edwards_hazard_FINAL.json |
| 1% / 44%, band 35 to 53 | 2029 spike 0.4402 [0.349, 0.533]; two-years-left about 1% | edwards_hazard_FINAL.json |
| ~70x (method line) | walk-year odds multiple ~70x [43x, 104x] | s_final_run_0712.md (hazard_m2_full posterior), printed in Part 1 |
| forty years of stars (VO) | the article's own phrasing for the 1990-2026 spell history | Part 1 text |
| 2029 twice | Edwards walk year; LaMelo deal ends same summer, unsigned | Part 1 / Part 2 contract records |
| 50,000 | Engine D FINAL paths | freeze 50f9b7bc5b19835b |

All values are embedded in `src/data.ts` with per-value provenance comments.
(The first cut's 62%/8.3/4.5 values remain in data.ts, verified and unused.)

## QA gates

1. Numbers pass: PASS (table above).
2. House style pass: PASS. No em or en dashes on screen or in the caption; no
   "genuinely," "honestly," "actually."
3. Retention pass: PASS. The claim card and its caption are on screen inside
   the first second.
4. Mute pass: PASS. Captions carry every spoken line verbatim; the statement
   cards and chart carry the argument without audio.
5. Safe-zone pass: PASS. Critical copy inside the 4:5 center crop and above
   the bottom 420px; checked on stills at all nine key frames.
6. Post-grader: NOT RUN. No post-grader skill exists in this environment.
7. Morning-of check (2026-07-14): no LaMelo extension signing reported;
   coverage still lists him extension-eligible, deal out in 2029, matching the
   project record (unsigned, verified 07-12). RE-CHECK THE MORNING THIS POSTS.
   If he signs, hold the reel; the pivot post is the Part 3 tornado finding (a
   signed extension cuts the bill by about 0.4 wins) and the unsigned beat gets
   rewritten before this ever posts.

## Open flags for Bobby

1. VO script is new for this cut (~95 words, in the caption kit). It is not the
   brief's script; the brief's 165-word read could not fit its own 35-40s spec,
   and this cut's one-point structure needed its own lines. Veto or edit freely;
   the audio is the master clock and re-timing is one file (src/timeline.ts).
2. The 44%, the circle, "the cliff," and ONE SUMMER all sit in the carousel
   green. That is slide grammar (green = the thing that matters), applied to a
   warning number; say the word if you want the 44% in white instead.
3. Beats B2/B5 captions duplicate the on-card words (captions match VO by
   rule). Reads as reinforcement at speed; flag if it bugs you.

## Files

- pick2033/social/outputs/one_summer_reel.mp4 (deliverable, silent + captions)
- pick2033/social/outputs/one_summer_cover.png (grid cover: 2029 / ONE SUMMER.)
- pick2033/social/outputs/one_summer_caption.txt (caption, hashtags, alt text,
  story copy, VO script, render commands)
- pick2033/social/one-summer/ (the Remotion project; node_modules and out/
  gitignored; the montage first cut is the prior commit-able state in history)
