# Snapshot slide: design system and rules

The look is deliberately consistent with the rest of the Wolves to a T feed
(the same family as the trade-posts carousels): one accent plus a neutral, real
type, monospace numerals, squared corners, a whisper of grain, restraint. The
render engine (`scripts/render_slide.py`) bakes all of this in. You supply
content via a JSON config; you rarely touch the visual tokens.

## Canvas
- 1080 x 1350 (portrait, the feed's still-image format).
- Output is a single PNG. One slide, not a carousel. For multi-slide hypothetical
  trade breakdowns, use the `trade-posts` skill instead.

## Visual tokens (defaults, already in the engine)
- Field: midnight navy vertical gradient (#081324 to #0D213A) with a faint
  aurora glow upper-right and low-amplitude grain.
- Accent: aurora green (#84D668). Exactly ONE accent. Used for the headline
  accent line, the dateline, every stat number, the tile ticks, and the catch
  label. Do not introduce a second accent color.
- Neutral text: off-white (#EEF4FA) primary, slate (#8C9FB4) secondary, muted
  (#5F748A) for caveats.
- Tiles: faint navy fill with a thin hairline border, squared corners (no
  rounding), a short accent tick at top-left.
- Type: condensed bold for the headline, bold sans for labels, regular sans for
  body, and monospace bold for every number. Numbers are always monospace; that
  is a signature of the feed.

## Layout map (fixed positions the engine draws to)
1. Masthead: thin aurora bar across the top, then brand kicker (left) and
   dateline (right).
2. Headline: one or two condensed-bold lines. The accent line (default: the
   last) is the payoff word(s).
3. Subhead: one or two slate lines, the plain-language "what happened."
4. Stat grid: a 2x2 of tiles. Each tile = big mono number, a bold label, and up
   to two short detail lines. This is the heart of the slide.
5. The catch (optional): a bordered strip with an accent label and one line.
   This is the editorial insight, the thing a casual account would miss.
6. Context line (optional): a small label plus one monospace line (assets,
   tools, what's next).
7. Footer: brand + tag (left), source credit and caveats (right).

## Content rules (this is where judgment lives)

### Pick four numbers, no more
The 2x2 grid forces discipline. Choose the four figures that actually define the
story. A number earns a tile only if it changes how a fan understands the
situation. Resist cramming; four sharp numbers beat eight soft ones.

### Headline: hook, not label
Two short lines, the second carrying the accent payoff. "THE BOOKS, / RESET."
beats "TIMBERWOLVES CAP UPDATE." Say the thing, don't announce the topic.

### Subhead: plain-language what-happened
One or two lines a non-capologist understands. The tiles carry the precision;
the subhead carries the meaning.

### The catch: earn your credibility
Use this strip for the non-obvious truth, the wrinkle most accounts get wrong
(a hard cap, a pick that's actually next night, a TPE that can't be combined).
This line is what makes the account worth following. Skip it only if there
genuinely isn't one.

### Context line: assets and what's next
Good for the tools still in hand, the picks, or the open question. Keep it to a
single monospace line with "  ·  " separators.

## Data integrity (non-negotiable)
This is real-news content under a real byline, so accuracy is the whole game.
- Every number traces to a verified source. If you can't source it, it doesn't
  go on the slide.
- Label soft numbers honestly: "est" for projections, "~" for approximations.
  A modeled or reported-but-unofficial figure must read as one.
- Credit sources in `footer_right` (e.g., "Cap figures: ESPN & Dane Moore").
- Note the official-status caveat when relevant (e.g., "Trade official July 6"),
  so a slide built during a moratorium or on a verbal agreement says so.
- This is news framing, not a hypothetical. (Hypothetical trades = trade-posts,
  which carry the "my model says / would you do it" framing instead.)
- Double-check the dateline and any "tonight/tomorrow" wording against the actual
  calendar before rendering.

## Fit constraints (keep the proven layout intact)
- Headline: at most 2 lines, roughly 11 characters per line at the condensed
  140px size before it crowds the right edge.
- Subhead: at most 2 lines.
- Tiles: exactly 4. Label up to ~22 characters; each of the up-to-2 detail lines
  up to ~26 characters.
- Catch text and context line: one line each, up to ~70 characters at their
  sizes. If something overflows, shorten the copy rather than resizing.

## Config schema (passed to render_slide.py)
```json
{
  "brand": "WOLVES TO A T",
  "brand_tag": "TIMBERWOLVES ANALYTICS",
  "dateline": "DRAFT NIGHT · 06.23.26",
  "headline": ["THE BOOKS,", "RESET."],
  "accent_line": 1,
  "subhead": ["line one", "line two"],
  "tiles": [
    {"num": "$33.3M", "label": "TRADE EXCEPTION", "detail": ["line", "line"]}
  ],
  "catch":   {"label": "THE CATCH", "text": "..."},
  "context": {"label": "STILL IN THE BAG", "text": "... · ... · ..."},
  "footer_right": ["Cap figures: ...", "Caveat ..."]
}
```
- `tiles` must contain exactly 4 entries.
- `accent_line` is the 0-indexed headline line that gets the accent (or -1 for
  the last line).
- `catch` and `context` may be null to omit them.
- Override palette keys (`accent`, `bg_top`, etc.) only for a deliberate reason;
  the default aurora-on-midnight is the brand.
