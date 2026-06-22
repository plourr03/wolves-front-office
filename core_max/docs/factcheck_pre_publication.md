# Pre-publication fact-check and corrections (2026-06-21)

Every load-bearing fact verified against TWO sources: the project warehouse (its own source of
truth) and live reporting (the real league). Worst-first. The conclusion survives; three things
must be fixed before anything is published, and one reframe makes the piece much harder to rip.

## 1. CRITICAL (mine): "OKC the recent champion" was false. Fixed.

- Claim made in narration: OKC was "the actual recent champion." FALSE.
- Warehouse: the 2025-26 Finals was NEW YORK over SAN ANTONIO; last game 2026-06-13, NYK 94 SAS
  90. OKC lost to SAS in the West finals (warehouse: OKC's series ended 2026-05-30, an L). So the
  claim contradicted the project's OWN data.
- Web confirms: Knicks beat Spurs 4-1, Brunson 45 in the Game 5 clincher, first NYK title since
  1973. And the gut-punch: KARL-ANTHONY TOWNS won it with the Knicks (KAT is +3.86 in our data,
  a quality starter on the champion). The team the Wolves traded him to won the title the year
  after the trade.
- Why the ENGINE is unaffected: the sim never used "who won" as an input. It seats teams by
  regular-season net + move deltas (OKC's +11.1 net makes them the legitimate projected FAVORITE,
  which is correct and standard, best net is not the champion), and calibrates to de-vigged
  preseason boards + historical series. The sim gave the eventual champion NYK ~6.3%, a sane
  non-favorite title that its variance structure is designed to allow. So only the WORDING was
  wrong. Fixed in phase3_plan.md ("favorite," not "champion").
- PUBLICATION RULE: never say or imply OKC won. If the KAT-on-the-champion irony is mentioned (it
  should be, it is the emotional spine), state it correctly: KAT won 2026 with the Knicks.

## 2. CRITICAL gap: the star branch (Giannis) was never modeled. Now modeled.

The live Wolves conversation is a star-for-the-core trade (Giannis especially). The frontier
capped moves at ~+3 and concluded "no move helps," which is exposed if published next to "Wolves
pursue Giannis." Now modeled (core_max/engine/run_star.py):

- Giannis at the REALISTIC price (Milwaukee's reported ask: McDaniels + Naz + TSJ + 2 firsts) ->
  ~2.98% title, essentially the SAME as the disciplined retool (~3.0%). Surrendering McDaniels'
  defense + Naz's +3.15 + depth for one body (with minimum-filler holes and a Giannis/Gobert
  spacing logjam) offsets even an MVP. Fit-over-splash holds at the MVP level.
- Giannis at a CHEAP price (keep the core) -> ~7.73%, a huge jump. But that price is NOT
  available: the Bucks want the young core; the Wolves have McDaniels AND Beringer OFF-LIMITS
  (reporting) and only ~No. 28 + a 2033 first to trade; Miami is the reported frontrunner.

REFRAMED CONCLUSION (rip-proof): the only thing that materially raises title odds is a co-star
acquired cheaply enough to keep the core, which is not on the table. A star at the price the
Bucks actually want barely beats the retool. So among ATTAINABLE moves none materially helps, and
the star route is foreclosed by the asset cupboard and the Wolves' own off-limits stance, not
because stars would not help. Engage Giannis explicitly; do not omit him.

## 3. REAL error: the Cam Johnson trade structure is backwards. Fixed framing.

- Reporting: Denver is shopping Cam as a SALARY DUMP (expiring ~$23M) to duck the second apron and
  re-sign Peyton Watson. Denver wants to SHED money.
- So "Randle ($33.3M) for Cam" is backwards: it hands Denver $10M MORE salary and a longer deal,
  the opposite of their motive. Denver has no reason to accept.
- And MIN cannot absorb Cam while keeping Randle (taking back ~$10M more hard-caps MIN at the
  first apron, which they are already at). So Cam is, in practice, NOT cleanly attainable for a
  Randle-shedding retool.
- Consequence: the realistic best retool is the JRUE version (Portland is motivated to move a
  35-turning-36 vet, and Randle + DiVincenzo for Jrue takes back less and opens room, gate-clean),
  landing ~3.0%, not the Cam/Cam+MLE cells (3.2-3.7%). This LOWERS the realistic near-term ceiling
  to ~3.0-3.1% and STRENGTHENS the asset-constrained conclusion. Treat the Cam cells as an
  illustrative upper bound, not an attainable plan.

## What checks out cleanly (keep with confidence)

- Core recommendation is CONSENSUS-backed: multiple outlets expect the Wolves to trade Randle;
  the Star Tribune retool blueprint (build around Edwards, add ball-handling, Reid at the 4, split
  center between Beringer and a return) is nearly identical to ours. We arrived there with a model.
- Cap lines: cap ~$165M, tax ~$201M, first apron ~$209.1M, second apron ~$222M; picks No. 28 and
  No. 59; draft June 23-24. MIN out of the second apron, operating just above the first apron as
  the realistic zone, matching the CBA gate.
- Joan: No. 17 pick (2025), redshirt rookie, viewed as Gobert's successor, OFF-LIMITS in trade
  talks, consistent with our untouchable treatment and the retool keeping him as a backup.
- Jrue Holiday: Portland, available, ~2yr/$72M, turning 36 (write "35 turning 36," not "35").
- Dorian Finney-Smith: Houston. Confirmed.

## Tone (not errors, but rip-risks)

- "mid-tier ~2.5%": a 49-33 team that made the second round (and back-to-back conference finals
  in the prior two years) reads as slighted by "mid-tier." Use "a real contender capped below the
  favorites without a co-star," same claim, less flammable.
- "be patient / disciplined": Connelly publicly said everything is on the table and he will be
  aggressive, and is not satisfied with the second-round exit. Our lean is deliberately
  contrarian-to-the-FO; acknowledge that posture explicitly so it reads as considered, not unaware.

## Still open (low priority)

- Royce O'Neale on Phoenix not independently re-verified (tertiary relief option, not load-bearing).

## Sources

- 2026 Finals (NYK over SAS, KAT): nba.com/news/how-the-knicks-won-the-2026-nba-championship;
  en.wikipedia.org/wiki/2026_NBA_Finals; npr.org Knicks championship photos (2026-06-18).
- Giannis / Wolves off-limits: ESPN, Yahoo Sports, CBS Sports, NBC Sports, Yardbarker (Giannis
  rumors, Bucks asking price, McDaniels/Beringer off-limits, Miami frontrunner).
- Cam Johnson salary dump: Mile High Sports, nugglove.com, Yahoo Sports (Denver shedding Cam to
  re-sign Watson, second-apron motive).
- Connelly posture / Randle market: Star Tribune, Dunking with Wolves, Zone Coverage, ESPN.
