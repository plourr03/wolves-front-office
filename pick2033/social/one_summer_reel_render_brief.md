# Render Brief: "One Summer" Reel
## Series trailer for Pricing the LaMelo Trade, Parts 1 to 3

Prepared: July 13, 2026
Consumer: Claude Code implementation agent, Bobby as reviewer and voice
Pipeline: same PIL + ffmpeg build as lamelo_reel.mp4, upgraded to 9:16 and voice-led
Ship target: posts the day Part 1 goes live

---

## 0. Plain-language overview

This is a 35 to 40 second vertical video. Bobby records the voiceover first. The agent then builds animated type and chart graphics timed to his voice, in the feed's midnight-and-aurora look, and exports a single MP4. The video opens on the most shocking number in the series (a 49-win team traded a pick with a 62 percent chance of being a lottery pick), escalates through the walk-year cliff and the two-clocks finding, lands on the bill, and ends with a comment-keyword CTA that drives readers to Part 1 on the site. No face on camera at any point. Everything on screen is a number from the FINAL model exports, verified against the manifest in section 6 before render.

Why the format changed from the last reel: the first LaMelo reel died on cold-viewer retention (60.7 percent skip rate, 4 second average watch). The fixes baked into this brief: the claim is spoken and on screen inside the first second, no logo intro, a cut every 2 to 3 seconds, burned-in captions for muted viewers, and a loop-friendly ending.

---

## 1. Format and technical spec

- Resolution: 1080 x 1920 (9:16), 30 fps, H.264 MP4, target under 60 MB
- Duration: 35 to 40 seconds, exact length set by the recorded VO
- Safe zones: keep all critical text inside the central 1080 x 1350 region (feed preview crops to 4:5). Additionally keep the top 220 px and bottom 420 px free of essential copy (IG UI overlays live there)
- Audio: Bobby's VO, normalized to -14 LUFS. Optional low percussion bed at -26 LUFS or quieter, ducked under VO. If no clean bed is available, VO alone is fine (original audio is an asset, not a gap)
- Captions: burned in, high contrast, max 2 lines at a time, positioned lower third inside safe zone, word-level or phrase-level reveal synced to VO
- No TikTok or CapCut watermarks anywhere. Native export only, uploaded natively to both IG and TikTok

## 2. Visual system

Use the feed tokens from the human-look reference in the social-visuals skill (same system as the snapshot-slide design system): midnight background, one aurora accent, monospace numerals for every number, real editorial type for words, squared corners, a whisper of grain, restraint. One accent color for the entire video. Numbers always render in the monospace numeral face. Do not introduce gradients, glows, or a second accent.

Charts in this reel are rebuilt versions of the article figures (hazard curve, invoice ledger). Rebuild them in the video's type and tokens rather than screenshotting site renders, so they animate cleanly and read at phone size. Axis labels minimal, one annotation per chart maximum.

## 3. Voiceover script (Bobby records this verbatim, natural pace)

Read at a conversational clip, roughly 130 words per minute. Leave a full one-second pause between beats so the agent has clean cut points. Record 3 takes on the phone in a quiet room, mic 8 to 12 inches away, send all takes.

> BEAT 1: "The Wolves just won 49 games. The pick they traded for LaMelo has a 62 percent chance of being a lottery pick."
>
> BEAT 2: "It comes down to one summer. 2029. That is Ant's walk year. Across 40 years of NBA history, a star's odds of leaving in a walk year run about 70 times higher than mid-contract. For Ant's profile, that is 1 percent with two years left on the deal. 44 in the walk year."
>
> BEAT 3: "And here is the part almost nobody is talking about. LaMelo is still unsigned. His deal runs out the exact same July. Two max guys. Two walk years. One summer."
>
> BEAT 4: "So we simulated fifty thousand futures and priced the whole package the way an insurance company would. Every pick. Every swap. Charlotte collects almost double what Minnesota gives up."
>
> BEAT 5: "All three parts are on the site, including the model misses we published on purpose. Comment BILL and I will send you part one."

House style check on this copy is already done: no em or en dashes, no "genuinely," "honestly," or "actually." Do not paraphrase the script in captions; captions match the spoken words.

## 4. Scene-by-scene build

Timing below assumes a ~38 second read. Re-time everything to the actual VO; the audio is the master clock.

### Scene 1, Hook (0.0 to ~3.5s, Beat 1)
- Frame 1 (before any sound finishes): giant "49 WINS" fills the safe zone, monospace, white on midnight. No logo, no intro card.
- On "62 percent": hard cut to "62%" in the accent color at the same scale, with a small lockup beneath: "chance the pick is a lottery pick" and a footnote-size "61.9, under the 16-team lottery."
- Animation: numbers slam in with a 2-frame scale settle, no easing longer than 150 ms. Subtle grain constant.
- This scene doubles as the cover frame (see deliverables).

### Scene 2, The cliff (~3.5 to ~14s, Beat 2)
- On "one summer. 2029": full-frame "2029" with "ANT'S WALK YEAR" beneath.
- On "70 times higher": cut to "70x" large, sublabel "walk year vs. mid-contract," footnote-size "80% interval: 43x to 104x."
- On "1 percent... 44": the Edwards hazard curve draws left to right across the years, flat and low through 2027 and 2028, then spikes at 2029. Two callouts land on the curve as they are spoken: "1%" at the two-years-left point, "44%" at the spike. The 35 to 53 interval band renders as a translucent accent band around the spike. Spoken point estimates, drawn intervals: that is the rule for the whole video.
- Cuts within this scene every 2 to 3 seconds (2029 card, 70x card, curve draw).

### Scene 3, Two clocks (~14 to ~22s, Beat 3)
- On "LaMelo is still unsigned": "UNSIGNED" stamps over a LaMelo contract line ("deal ends: summer 2029").
- On "Two max guys. Two walk years. One summer.": two countdown-style clock graphics converge, both faces reading JULY 2029, then merge into a single "2029."
- Keep the clocks flat and typographic (rings or dials in line-art, no skeuomorphism). One accent only.

### Scene 4, The bill (~22 to ~31s, Beat 4)
- On "fifty thousand futures": "50,000 FUTURES" counter spins up fast and locks.
- On "Every pick. Every swap.": an invoice graphic stamps line by line in monospace: "2033 1ST (UNPROTECTED)," "SWAP 2028," "SWAP 2029," "SWAP 2030."
- On "Charlotte collects almost double": cut to two facing numbers, "CHA COLLECTS 8.3" over "MIN GIVES UP 4.5," sublabel "points of title equity, headline package." Accent on the 8.3.
- The invoice motif here is a deliberate visual handshake with the carousel cover. Same layout language.

### Scene 5, CTA and loop (~31 to end, Beat 5)
- On "All three parts": three article cover cards fan out (Part 1, Part 2, Part 3 titles set in the editorial face).
- On "the model misses we published on purpose": a small red cell graphic pulses once next to a green one. This is the trust flex; keep it to one second, no dwelling.
- On "Comment BILL": "COMMENT 'BILL'" large in accent, with "full series at wolvestoat.com" small beneath, inside safe zone.
- Final 0.5s: cut back to the exact "49 WINS" card from frame 1 so the loop is seamless and rewatches read as intentional.

## 5. Caption, cover, and posting kit (agent produces as text files)

- Post caption (Bobby edits voice as he likes): "the wolves just won 49 games. the pick they sent charlotte has a 62% chance of landing in the lottery. we priced the whole trade, every pick and every swap, across 50,000 simulated futures. all three parts are live. comment BILL and i'll send you part one." Then 3 to 5 hashtags maximum (suggest: #Timberwolves #NBA #WolvesBack #LaMelo, final pick Bobby's).
- Cover frame: export Scene 1 frame 1 as a 1080 x 1920 PNG with a small "ONE SUMMER" title lockup added for the grid.
- Alt text: one sentence describing the video for accessibility.
- Comment keyword: BILL, wired in ManyChat to DM the deep link to the Part 1 article URL (the specific article, never the homepage).
- Same-day story: single slide, "the series is live," link sticker to Part 1, sticker text "Read it."

## 6. Numbers manifest (verify every value against source before render)

| On screen | Value | Source of truth |
| --- | --- | --- |
| 49 WINS | 49 (2025-26 actual) | league standings, cross-check article text |
| 62% lottery | 61.9% (16-team definition) | slot_distribution_2033_FINAL.json |
| 70x | ~70x, 80% interval 43x to 104x | edwards_hazard_FINAL.json / model_b_hazard_M2_FINAL.md |
| 1% / 44% | 1% two-years-left, 44% walk year, interval 35 to 53 | edwards_hazard_FINAL.json |
| 2029 | Edwards walk year summer 2029; LaMelo deal ends same summer, unsigned | contract records cited in Part 1 and Part 2 |
| 50,000 | 50,000 simulation paths | Part 2 methodology / engine_d_gates_FINAL.md |
| 8.3 vs 4.5 | title equity, headline package, CHA delivered vs MIN forgone | total_asset_cost.json |

Rule: if any exported value disagrees with this table, the export wins and the agent flags the discrepancy to Bobby before rendering. Nothing is eyeballed.

## 7. QA gates before ship

1. Numbers pass: every on-screen figure matches the manifest source file.
2. House style pass: zero em or en dashes in any on-screen text or caption; no "genuinely," "honestly," "actually."
3. Retention pass: watch the first 2 seconds cold. If the claim is not fully legible and spoken by second two, fix it.
4. Mute pass: watch the whole video muted. It must make complete sense from captions and graphics alone.
5. Safe-zone pass: check the 4:5 center crop; nothing essential clipped.
6. Run the post-grader skill on the finished MP4 plus caption. Ship only on SHIP IT or after fixes.
7. Morning-of check: confirm LaMelo is still unsigned. If he signs, hold this reel and tell Bobby: the pivot post is the Part 3 tornado finding that a signed extension cuts the bill by about 0.4 wins, which becomes its own snapshot post, and Beat 3 of this reel gets rewritten before it ever posts.

## 8. Deliverables

- /outputs/one_summer_reel.mp4 (1080 x 1920)
- /outputs/one_summer_cover.png (grid cover)
- /outputs/one_summer_caption.txt (caption, hashtags, alt text, story copy)
- A short plain-language render report: what was built, the final duration, which numbers appear and their sources, anything flagged.
