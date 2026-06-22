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

## 2. CRITICAL gap: the star branch (Giannis). Modeled across constructions (corrected).

The live Wolves conversation is a star-for-the-core trade (Giannis especially); omitting it is a
publication risk. FIRST PASS ERROR (caught in review): I modeled only the thesis-confirming
construction (keep Gobert, ship McDaniels -> a Giannis/Gobert spacing logjam + losing Edwards's
best defensive wing) and concluded "a star barely helps." That was a strawman. Corrected by
running the constructions analysts would actually propose (core_max/engine/run_star.py):

- A  Bucks' literal ask (keep Gobert, ship McDaniels+Naz+TSJ): 2.98% (worst fit; the strawman).
- B  MOVE Gobert, keep McDaniels + the core (analyst-preferred): 3.17%, a TIE with the retool
   (~3.0-3.7%), NOT a meaningful beat.
- C  keep everyone incl. Gobert, add Giannis: 7.73% (would dominate) but SALARY-INFEASIBLE.

The rigorous reason B only ties (this is the real argument, not "bad fit"): Giannis's ~$54M
salary can ONLY be matched by including Gobert (the team's #2). So a Giannis trade NECESSARILY
costs Gobert (+4.57), making the real upgrade only Giannis-minus-Gobert (~+2.4) minus the depth
shipped to match, which nets modest. The construction that would dominate (C, keep Gobert AND add
Giannis) cannot take back $54M while over the first apron, so it is financially impossible, not
merely unavailable.

ATTAINABILITY (resolves the McDaniels contradiction): separately, the Bucks' ask is the YOUNG
CORE (McDaniels + Naz + TSJ + picks). McDaniels AND Beringer are OFF-LIMITS, so the Bucks' ask
CANNOT be met at all -> Giannis is foreclosed outright. Do NOT also list McDaniels as the price
we pay; the price MIN could pay (aging Gobert+Randle salary) is exactly what a rebuilding
Milwaukee does not want, and Miami is the reported frontrunner.

BULLETPROOF CONCLUSION: no FEASIBLE, ATTAINABLE Giannis construction meaningfully beats the
retool, three independent locks: (i) his salary forces Gobert out, so the upgrade is modest
(B ~ retool); (ii) the keep-Gobert version is financially impossible (C); (iii) the Bucks want a
young core that is off-limits. The disciplined retool is the best AVAILABLE move. The honest
framing is NOT "a star wouldn't help" (kept-core it would); it is "no star MIN can actually
build and land beats the disciplined move." Engage Giannis explicitly with this logic.

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

## 4. Board vs market: the sim's 2026-27 board diverges from real futures. Disclose it.

Real 2026-27 title futures: SAS +250 and OKC +260 (co-favorites), BOS +550, NYK +650 (the
defending champ, ~13% implied). The sim board: OKC 20% (clear favorite), BOS 14%, DET 11%, SAS
11%, NYK 6%. So the sim OVERRATES high-regular-season-net teams (OKC the runaway favorite; DET
3rd) and UNDERRATES playoff-pedigree teams (SAS, who made the Finals, 4th; NYK, the champ, 6% vs
market 13%). Cause: the sim seats opponents by regular-season net + regression, which weights RS
dominance more than the market's weighting of playoff results and youth.

Why the FINDINGS still hold: every reported result is a MIN-vs-MIN DELTA on the SAME opponent
field (Fork B -1.1, retool +0.6, Giannis ~tie). A mis-seated field shifts MIN's ABSOLUTE title
odds slightly but cancels out of the deltas, which are the actual conclusions. PUBLICATION RULE:
do NOT publish the sim's opponent board as if it matches the market (a reader will probe OKC-as-
favorite and NYK-at-6%). Report MIN's own number as a band and frame conclusions as deltas/
relative, not as an absolute league ranking. MIN's ~2.5% absolute is plausibly market-consistent
(they are a second-tier contender, off the favorites shortlist), but verify MIN's actual futures
number before citing any absolute.

## Tone (not errors, but rip-risks)

- "mid-tier ~2.5%": a 49-33 team that made the second round (and back-to-back conference finals
  in the prior two years) reads as slighted by "mid-tier." Use "a real contender capped below the
  favorites without a co-star," same claim, less flammable.
- "be patient / disciplined": Connelly publicly said everything is on the table and he will be
  aggressive, and is not satisfied with the second-round exit. Our lean is deliberately
  contrarian-to-the-FO; acknowledge that posture explicitly so it reads as considered, not unaware.

## Verified clean (closed)

- Royce O'Neale: Phoenix, $10.875M (2026-27), two more years of control, and AVAILABLE (the
  33-year-old is the odd man out behind a rising Rasheer Fleming, a useful trade piece). Named-
  target set now fully verified: MPJ (BKN), Jrue (POR), Cam (DEN), O'Neale (PHX), DFS (HOU), Joan.

## Sources

- 2026 Finals (NYK over SAS, KAT): nba.com/news/how-the-knicks-won-the-2026-nba-championship;
  en.wikipedia.org/wiki/2026_NBA_Finals; npr.org Knicks championship photos (2026-06-18).
- Giannis / Wolves off-limits: ESPN, Yahoo Sports, CBS Sports, NBC Sports, Yardbarker (Giannis
  rumors, Bucks asking price, McDaniels/Beringer off-limits, Miami frontrunner).
- Cam Johnson salary dump: Mile High Sports, nugglove.com, Yahoo Sports (Denver shedding Cam to
  re-sign Watson, second-apron motive).
- Connelly posture / Randle market: Star Tribune, Dunking with Wolves, Zone Coverage, ESPN.
