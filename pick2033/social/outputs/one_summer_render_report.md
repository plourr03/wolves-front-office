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

## Slow cut (2026-07-14, Bobby: "super fast, slow some of it down")

Re-timed from ~40s to 52.4s. Same seven-beat spine; every beat gains air, the
chart's hold grows to ~16 seconds, the curve draws slower, the stamp lands a
touch later, dissolves lengthen to 0.45s, and every scene carries a
barely-there push-in (1.6% across its whole beat) so the long holds read as
alive rather than frozen. B6 swapped to Bobby's own line from the recording
sheet ("The Wolves and Charlotte both making opposite bets on that summer,"
spelling normalized), its caption split across two pages to stay inside the
two-line rule, and the card's sub now reads "Opposite bets on the same
summer." Recording-sheet windows updated (B1 0:00-0:05 ... B7 0:45-0:52).

## Bobby's sheet edits folded in (2026-07-14, fifth cut, ~62s)

- B1 rewritten to Bobby's hook line (words build to the number the screen
  already shows); B3 gains his "And"; grammar and spelling normalized so the
  burned captions match a clean read.
- B4 grew into a four-moment act per his margin note, and this time the
  losing-team number exists on the record: the Part 1 hazard viz publishes
  both scenarios (44 at .600, 56 declining), so "On a 37-win pace? It jumps to
  56." is spoken AND drawn (dotted slate decline_win45 line from the same
  export, arriving on the beat, 56% stacked over the 44 in the annotation
  column; .450 x 82 = 36.9 -> a 37-win pace). The earlier "no published
  walk-year-at-.450 number" ruling was wrong and is superseded. Method note
  now reads 291 STAR TENURES SINCE 1990 · 80% BAND AT THE 44: 35 TO 53, and
  the 44's tag reads THE WALK YEAR · AT .600.
- B5 is now "Still not extended." (his edit, and more accurate: LaMelo is
  under contract, not extended), so the stamp reads NO EXTENSION. Insurance
  take updated to match. Reel two's cumulative 56/71 pair is unchanged and
  distinct; watch the two 56s across posts when reel two ships.
- Total 62.1s, a true deep cut. Windows: B1 0:00-0:05 ... B7 0:54-1:02.

## B4 honesty clause + scope rulings (2026-07-14)

B4 now says out loud what the method note prints: "In the walk year? 44. And
that's with the team winning." (curve2 caption updated to match; the beat
gained 0.4s and everything downstream shifted; total now 53.2s). Two expansion
ideas were weighed and parked as their own posts rather than squeezed in:

- Jaden in B3 (his deal IS up the same summer, extension runs through
  2028-29): kept out because the model priced two clocks, not three (THE MODEL
  SAYS has to stay true), an early LaMelo mention kills the B5 stamp reveal,
  and B6's "two max guys" stops being accurate. Next post: "Three contracts.
  One summer." with the October extension-window peg. An optional caption seed
  line is in the kit.
- The winning stat (gone by 2033 in 56 percent of futures at .600, 71 at
  .450): cumulative numbers, not walk-year, and too good to bury; that is reel
  two, closing on the series' own most practical line (winning is worth 15
  points of keeping Ant; the cheapest way to keep the 2033 pick worthless is
  the best reason to have made the trade).

## Bobby's review fixes (2026-07-14, pre-recording)

1. B4 VO re-anchored to the contract clock ("With two years left on his deal")
   instead of "On a winning team": both the 1 and the 44 sit on the same .600
   path (central_win60); the clock is the only variable, which is the Part 1
   thesis. Caption updated to match.
2. Method note under the chart re-credited to the right machine: 291 STAR
   TENURES SINCE 1990 · .600 SCENARIO · 80% BAND: 35 TO 53 (the curve is the
   Part 1 tenure model, not Engine D; the ~70x dropped for fit per Bobby's
   call, the 50,000 stays in the CTA where it belongs).
3. THE MODEL SAYS kicker added above the 44% cold open (attribution turns the
   doom-stat into an owned claim; Part 1 warns about this number screenshotted
   naked).
4. Wordmark nudged down inside the safe zone (top 236) so app UI never covers it.
5. Recording sheet now asks for an insurance take of B5 without "Still
   unsigned," so a LaMelo signing between recording and posting is a one-line
   audio swap plus a stamp-card re-render, not a new session.

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
