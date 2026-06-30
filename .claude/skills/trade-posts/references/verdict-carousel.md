# Verdict carousel (analytical mode)

A second mode of trade carousel, distinct from the six-slide debate-starter in
`playbook.md`. Use it when the carousel delivers a *verdict* on a trade that
already happened (or a full model evaluation), not a "would you do it?" debate.
The honest verdict gets the last word; the post never ends on "would you pull the
trigger?" The LaMelo trade carousel is the worked reference, and its renderer is
the template.

- **Renderer / template:** `lamelo/slide/render_lamelo_carousel.py` (PIL + numpy,
  rendered at 2x supersample then LANCZOS-downscaled so every edge is
  anti-aliased). `python render_lamelo_carousel.py` writes `carousel/slide_1..5.png`.
  Canvas 1080x1350, margin 80, usable text width 920.
- **When to use this vs the debate playbook:** decided trade / model verdict ->
  this. Hypothetical fan trade, "what if," "would you do it" -> the six-slide
  `playbook.md`. Both share the data rule and the human look.

## The look (Bobby's settled preferences)

- **Editorial film-room, not glossy "AI."** Flat fills, a faint aurora glow on a
  midnight gradient, a whisper of grain. No bloom/halo that reads as AI-generated.
- **One accent: brand green, reserved EXCLUSIVELY for the upside / the dream.**
  Risks, danger lines, and neutral data stay slate/blue/gray. Never color a
  negative or a neutral green. Green should be the smallest, brightest thing in
  the set (the long-shot tail, the one hopeful word).
- **Type:** condensed bold for display headlines and bar labels (Bahnschrift
  Bold), Franklin Gothic Heavy for the biggest impact lines, Segoe UI for body,
  Segoe UI Semibold for labels/tags, **Consolas Bold for all numerals** (mono
  numbers), Ink Free for the analyst's hand "marker" scrawl. Real display fonts,
  never plain Arial.
- **Charts read as model output, not infographic.** Use the *actual* simulation
  output as true (lumpy) bars, not a smooth illustrated curve. Add a method note,
  and annotate the one key feature (a loose hand-drawn circle + marker note +
  hand-arrow on the feature that matters, used sparingly). Squared bars/tiles,
  subtle vertical gradient, a lit top edge.

## Layout conventions (every slide)

- **Masthead on every slide, cover included:** green gradient top bar (y 0-7) +
  `WOLVES TO A T` left + `TOPIC  ·  MM.DD.YY` right in accent. The date is the
  CURRENT date and is updated on every render (it lives in one `masthead()`
  function, so changing it once updates all slides). The cover gets the full
  masthead row too, not just the bar.
- **Footer on every slide:** wordmark + method line (e.g. `CHAMPIONSHIP MODEL +
  FIT DECOMPOSITION`) + a swipe arrow naming the next beat (`THE NIGHTMARE  ->`).
  The final slide swaps the swipe for source credits.
- **Headers pinned at the top; spacing fixed internally.** Do NOT vertically
  center a slide by block-shifting the whole body down (it leaves an awkward gap
  under the masthead). Keep the header at the top and distribute the body spacing
  to fill the frame evenly. The bottom gap should roughly match the gaps between
  sections.
- **Bullet every list.** Small neutral (slate) square bullets so each watch-item
  or point reads as a distinct line, not a blur.
- **Caption every chart.** A small muted footnote naming WHAT the distribution
  measures (the unit), so a reader knows the shape is *outcomes*, not decoration.
  Frame it as the range of outcomes and their frequency ("how the season could
  play out"), never as "how much the trade helps."

## Rigor (fact-check before it ships)

- **Every number traces to the warehouse or a locked project finding**, and is
  verified fresh before finalizing. Pull the exact stat for the exact season; do
  not eyeball. Final pass on the LaMelo set verified, from the warehouse:
  Edwards catch-and-shoot 3P 49.6% / pull-up 35.3% / cs-share 27% (all 2025-26),
  LaMelo GP sawtooth 51/75/36/22/47/72, Gobert roll volume 1.52 now vs ~3.5 peak,
  LaMelo PnR defense bottom-third, plus model outputs (20,000 sims, dream tail
  ~17% = reach-CF, committed 63 games vs model-leans-~50).
- **No fabrication, no invented precision.** Reconcile with the project's locked
  findings (`sim/`, `fit_decomp/`, `prereg/`, `DELIVERABLE.md`) and never state a
  claim stronger than the gated result. Rounding follows the project's own
  convention (e.g. the project says "27%", so the slide says 27%).
- **Headline hyperbole is allowed only if the support line under it is precise.**
  "He can't guard anybody." is fine as a headline when the line beneath it states
  the exact, true claim ("Bottom third against the pick-and-roll"). Keep the hard
  number honest even when the headline punches.
- Measure each text line's width (PIL `getlength`) against the 920px usable width
  before committing it; wrap or size down rather than overflow. Review every
  rendered PNG for collisions, crowding, and uneven bottom gaps before presenting.

## Tone and honesty (the heart of this mode)

- **The honest verdict gets the LAST word. Hope never overturns the finding.**
- **Credit the model:** "The simulations say it's most likely a wash," "the model
  leans nearer 50 games than our 63" -- not flat assertions.
- **A fan's-heart note is allowed as an italic slate aside in the MIDDLE of a
  beat** ("As a fan, you're praying this is the swing that gets them over the
  top."), visibly set apart, never replacing the verdict.
- **Earned-but-honest hope can close**, but it must name the PRECISE long shot and
  tie it to the gradeable watch-items, and stay honest about the cost: "The model
  says probably not. But if the looks open up and the ankle holds and the kid
  leaps, that's the season that proves it wrong." Never land on pure optimism that
  flips the verdict the piece earned.
- **Respect the players.** Frame uncertainty as a bet, not a knock: "A big bet on
  Beringer" (they are counting on him to leap), not "the backup is unproven and
  bad."
- **Keep claims true if read later.** "The only help left is the mid-level or a
  minimum" (true for a hard-capped, pick-less team), not "they have no power
  forward," which a single minimum signing would falsify.
- **No em dashes or en dashes** (standing rule). Use periods, commas, parentheses,
  or restructure.
- **Two-beat punchy headlines** ("THE CEILING'S REAL. THE ODDS AREN'T."). Use
  all-caps + bold for a final punch line, keeping the size.

## The five-beat arc (adapt as the analysis needs)

1. **The bet / the distribution.** The full outcome distribution as a hero
   (real sim output, true lumpy bars), green tail = the dream and the least
   likely; one hand-drawn analyst note on the long-shot; a caption naming the unit.
2. **The bull case.** The upside levers side by side (green here, and only here),
   each with its honest turn ("the looks will be there, but comps say the share
   barely moves; it's on the player to take them").
3. **The risks.** A risk ledger shown at a glance (health sawtooth, a defense
   percentile bar, the depth bet), neutral colors, direction obvious.
4. **The steelman + honest landing.** "Okay, to be fair" concessions, then an
   "AND YET" box where the verdict lands heavier than the concessions. The fan's
   heart can speak inside this box; the honest line still closes it.
5. **The verdict.** Two-beat headline, the crisp call ("Not a disaster. Not an
   upgrade. A bet."), honest beats, a bulleted "WHAT TO WATCH EARLY" of sharp
   one-line mechanism-based gradeable tells, then the earned-hope close as the
   last word (caps + bold, the hopeful clause the one spot of green).
