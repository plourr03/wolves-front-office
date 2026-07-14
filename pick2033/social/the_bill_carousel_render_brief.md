# Render Brief: "The Bill" Carousel
## Capstone post for Pricing the LaMelo Trade, Parts 1 to 3

Prepared: July 13, 2026
Consumer: Claude Code implementation agent, Bobby as reviewer
Pipeline: Remotion stills at 1080 x 1350, per the trade-posts and social-visuals setup, feed tokens throughout
Ship target: posts the day Part 3 goes live (the carousel needs Part 3's numbers), then gets pinned

---

## 0. Plain-language overview

Seven still slides, swiped like a story. The organizing visual idea is a literal itemized invoice from Charlotte to Minnesota. Slide 1 shows the invoice with the TOTAL line redacted, which is the scroll-stopper and the swipe motivator. Slides 2 through 5 walk the reader through the series' four biggest findings (the coin flip on Ant, the walk-year cliff, where the 2033 pick lands, and the fine print on the three swaps). Slide 6 completes the invoice and reveals the total. Slide 7 closes on the 2029 collision, the CTA, and a debate question. Every number is a FINAL model export, verified against the manifest in section 5. This is real analysis of a real trade, not a hypothetical, so no "would they say yes" framing; the honesty framing is "our model, our gates, our published misses."

## 1. Format and visual system

- 7 PNG stills, 1080 x 1350, uploaded in order
- Feed tokens from the human-look reference: midnight background, ONE aurora accent, monospace numerals, editorial face for words, squared corners everywhere, light grain, restraint. No second accent, no rounded corners, no drop shadows
- The invoice motif: straight-cut edges (no perforation skeuomorphism), dotted leader lines between item and value, monospace throughout the receipt block, small "WOLVES TO A T" issuer mark. The receipt is a typographic object, not a photo prop
- Numbers with uncertainty carry their intervals visually (band or bracket), never as an afterthought footnote when the number is the slide's centerpiece
- Fit rule: if copy overflows, shorten the copy. Never shrink type below the system minimums

## 2. Slide-by-slide spec

### Slide 1, Cover: the invoice
- Top block: "INVOICE" small caps, then "FROM: CHARLOTTE HORNETS" and "TO: MINNESOTA TIMBERWOLVES," dateline "ISSUED JUNE 25, 2026. DUE: 2028 TO 2033."
- Receipt line items, monospace, values column right-aligned:
  - 2033 FIRST-ROUND PICK (UNPROTECTED)
  - SWAP RIGHTS, 2028
  - SWAP RIGHTS, 2029
  - SWAP RIGHTS, 2030
  - SECOND-ROUND PICKS x3
  - DRAFT NIGHT: NO. 28 OUT, NO. 33 BACK
- Values column on the cover shows no numbers, just dotted leaders running to the edge. Bottom row: "TOTAL" with the value covered by a solid accent redaction bar.
- Headline overlay (editorial face): "We priced the LaMelo trade. All of it."
- Dek: "3 articles. 50,000 futures. Every pick, every swap."
- Corner cue: "swipe for the total"

### Slide 2, The coin flip
- Kicker: "PART 1: THE TENURE BET"
- Question line: "Will Ant still be a Timberwolf in 2033?"
- Centerpiece: "56%" huge, labeled "chance he has departed by 2033." The 80 percent interval renders as part of the numeral lockup: a horizontal band behind or beneath the number marked 45 and 68 at its ends, physically attached so the number cannot be screenshotted without its uncertainty. This is deliberate; Part 1 warns about exactly this screenshot.
- Sublabel: "with the Wolves winning at a .600 clip"
- Support line: "History's answer, not a mind read. 291 star tenures since 1990, priced the way an insurer prices a policy."
- Catch line: "Read the width before the number. History does not know, and the width is the finding."

### Slide 3, The cliff
- Kicker: "THE WALK-YEAR CLIFF"
- Two facing tiles, squared: left tile "1%" labeled "two years left on the deal," right tile "44%" labeled "walk year" with a thin 35-to-53 interval bracket. Accent on the 44 tile.
- Between or beneath the tiles: "Same player. Same team. One difference: the contract."
- Support line: "A star's walk-year departure odds run about 70x mid-contract across 40 years of NBA history."
- Footer line: "Ant's walk year: summer 2029. LaMelo, still unsigned, hits the exact same July."

### Slide 4, The pick
- Kicker: "PART 2: WHERE THE 2033 PICK LANDS"
- Horizontal bar trio, monospace values:
  - LOTTERY PICK: 61.9%
  - TOP TEN: 39.1%
  - TOP FOUR: 15.7%
- Bars scaled to value, accent fill, labels left, values right.
- Footnote size: "lottery = 16 teams under the 2026 reform"
- Catch line: "This is the pick a 49-win team just traded. Unprotected."
- Source line, small: "50,000 simulated futures, drawn ball by ball"

### Slide 5, The fine print
- Kicker: "PART 3: THREE SWAPS, THREE DIFFERENT ANIMALS"
- Three stacked squared tiles, one per swap, each with a name, one number pair, and one line of character:
  - 2028, "THE CLEAN ONE": exercises in 41.6% of futures, mean 0.7 wins. "Two picks, Charlotte takes the better. No strings."
  - 2029, "THE INSURANCE POLICY": pays zero at the 90th percentile, ~5.3 wins when it wakes. "Only alive if the Wolves collapse hard enough to keep a top-five pick. Catastrophe coverage, nothing else."
  - 2030, "THE STRANGE ONE": exercises in 66.3% of futures, mean 1.3 wins, the most valuable of the three. "Not because of Minnesota. Because Charlotte expects to be good enough to throw its own pick away."
- Catch line: "Nobody read the fine print. We did."

### Slide 6, The bill, revealed
- Kicker: "THE TOTAL"
- The cover's invoice returns, now with the values column filled, mean 4-year win value per item, monospace:
  - 2033 FIRST (UNPROTECTED) ... 2.2
  - SWAP 2028 ... 0.7
  - SWAP 2029 ... 0.7
  - SWAP 2030 ... 1.3
  - SECONDS x3 ... 1.1
  - DRAFT NIGHT NET ... 0.25
  - TOTAL ... ~6.2 WINS (mean, 4-yr value)
- The TOTAL row sits where the redaction bar was on the cover, accent-ruled.
- Beneath the receipt, the sharpest fact in the series as two facing numbers: "CHARLOTTE COLLECTS 10.2" over "MINNESOTA GIVES UP 6.0," labeled "points of title equity, all-in." Support line: "Same picks. Same futures. Charlotte collects nearly double. That gap is the Ant bet, priced."
- Small honest line at the bottom: "The bill is only light in the futures where the house already burned."

### Slide 7, Closer
- Full-bleed midnight, minimal.
- Three stacked lines, editorial face, large: "Two max contracts." / "Two walk years." / "One summer: 2029."
- CTA block: "The full three-part breakdown is live. Comment BILL and I'll send you Part 1." Plus "wolvestoat.com" small.
- Trust line, small: "Every model gate is published. Including the ones we failed."
- End question, accent: "Would you have paid it?"

## 3. Caption and posting kit (agent produces as text files)

- Caption draft (Bobby edits to voice): "we spent three weeks pricing the lamelo trade. every pick, every swap, every line of fine print, across 50,000 simulated futures. the total is on slide 6 and the fine print nobody read is on slide 5. all three parts are live. comment BILL and i'll send you part one. would you have paid it?" Then 3 to 5 hashtags max.
- Comment keyword BILL wired to the Part 1 deep link (specific article URL, never the homepage). Bobby replies personally to early comments; the mechanic exists for conversation, not just link delivery.
- Same-day story: one slide, "the bill is in," link sticker to Part 3, sticker text "Read it."
- Bio links updated: all three article deep links occupying three of the five slots.
- Alt text: one sentence per slide for accessibility.
- Pin this post to the top of the grid once live.

## 4. Sequencing note

This carousel is the capstone and assumes all three parts are readable. Series order: the One Summer reel ships with Part 1, a single snapshot-style teaser ships with Part 2 (the Edwards split stat: top-ten odds 35.4% if he stays, 41.9% if he leaves; spec on request), and this carousel ships with Part 3 and gets pinned. If Bobby publishes all three articles at once instead, run reel day one and this carousel day two or three.

## 5. Numbers manifest (verify every value against source before render)

| Slide | Value | Source of truth |
| --- | --- | --- |
| 2 | 56%, interval 45 to 68, .600 scenario; 291 spells | edwards_hazard_FINAL.json; star_spells_final.meta.json |
| 3 | 1% / 44% (35 to 53); ~70x (43x to 104x); walk years summer 2029 | edwards_hazard_FINAL.json; contract records per Parts 1 and 2 |
| 4 | 61.9 / 39.1 / 15.7; 50,000 paths; 49 wins | slot_distribution_2033_FINAL.json; standings |
| 5 | 2028: 41.6%, 0.7. 2029: 12.3% exercise, 90th pct 0, ~5.3 conditional. 2030: 66.3%, 1.3 | swap_pricing_FINAL.json |
| 6 | Items 2.2 / 0.7 / 0.7 / 1.3 / 1.1 / 0.25, total ~6.2; equity 10.2 vs 6.0 all-in | total_asset_cost.json; swap_pricing_FINAL.json |
| 7 | 2029 collision; LaMelo unsigned | contract records; unsigned status re-verified at post time |

Rules: exports win over this table, and any mismatch gets flagged to Bobby before render. The receipt items on slide 6 must sum to the printed total within rounding (2.2 + 0.7 + 0.7 + 1.3 + 1.1 + 0.25 = 6.25, printed as ~6.2). Slide 6 uses the all-in equity pair (10.2 vs 6.0) because the invoice itemizes everything; the reel uses the headline-package pair (8.3 vs 4.5). Both are in total_asset_cost.json; do not mix the pairs on one asset.

## 6. QA gates before ship

1. Numbers pass: every figure matches its source export; receipt math sums.
2. House style pass: zero em or en dashes anywhere on any slide or in the caption; no "genuinely," "honestly," "actually."
3. Interval pass: the 56 and 44 render with their bands attached. A crop of either number must still show its interval.
4. Fit pass: review every rendered PNG for overflow or crowding; shorten copy, never shrink type.
5. One-accent pass: exactly one accent color across all seven slides.
6. Run the post-grader skill on the assembled carousel plus caption. Ship only on SHIP IT or after fixes.
7. Morning-of check: confirm LaMelo is still unsigned before slide 3 and slide 7 post as written. If he signs, those two slides get a one-line rewrite (his clock is resolved, and Part 3 already priced the signing at about 0.4 wins off the bill), and that news becomes its own snapshot post.

## 7. Deliverables

- /outputs/the_bill_carousel/slide_01.png through slide_07.png
- /outputs/the_bill_caption.txt (caption, hashtags, alt text per slide, story copy)
- A short plain-language render report: what each slide shows, confirmation that every figure traces to a FINAL export, and anything flagged.
