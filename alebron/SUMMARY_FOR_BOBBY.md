# LeBron to the Wolves, the plain-language version (for Bobby)

You left me to run the whole thing with no input. Here's what I did and what I found. Everything
below is reproducible from `alebron/` (a full clone of `lamelo/`, same engine, same discipline).

## What I actually did

1. **Cloned `lamelo/` → `alebron/`** and rebuilt every layer for LeBron instead of LaMelo.
2. **Researched the real 2026 offseason** with a 9-agent web workflow (6 finders + 3 fact-checkers).
 Confirmed: LaMelo trade done; Ayo (5/$112M), Jalen Clark (3/$10M) and Bones (1/$2.9M) re-signed;
 the Jaylen Brown trade (Celtics → 76ers for Paul George + picks); Giannis → Miami; Kawhi → Toronto;
 Ja Morant → Portland; Knicks won the 2025-26 title. And the big one: **LeBron is a confirmed
 unrestricted free agent**, told the Lakers he's leaving, chasing "meaningful, competitive
 basketball." He's 41 (turns 42 this December, the premise was off by one year, noted).
3. Ran the real numbers through the same calibrated championship model.

## The three things you need to know

**1. The Wolves literally can't afford him except at the minimum, and even then only by cutting
the 15th man.** The LaMelo trade hard-capped you at the second apron ($221.7M). Once Clark and Bones
are in, a legal 14-man roster is already at $219.6M, $2M under the ceiling. So:
- LeBron at the minimum, added as an extra body → **illegal** (over by $0.4M).
- LeBron at the minimum, swapping out a minimum body → **legal, barely.**
- LeBron at the taxpayer mid-level ($6.1M) → **illegal** by $2-4M.
The GOAT fits only as a minimum-for-minimum swap. He's a substitution, not an addition.

**2. Unlike the LaMelo swing, this one basically can't backfire.** That's the whole finding. Because
he costs nothing and you can bench him, the model has adding LeBron as a **small, one-sided plus**:
- Title odds: RAPM 2.7% → 3.9%, box 3.9% → 6.1%. A **+1.2 to +2.2 point** bump.
- Reach the conference finals: about **+4 to +7 points** (up to ~20-26% with him).
- And critically, the title delta stays **positive even in the "fit fails" world** (three ball
 handlers, no spacing): fit-fails is still +0.3 to +0.7 points, fit-clicks is +2.5 to +3.8. It never
 goes negative, because a badly-fitting free minimum guy is still better than the replacement body he
 replaced, and if it's ugly you just play him 12 minutes.
- Compare LaMelo, whose "fit fails" case was an actual **negative** (-3.4 points to reach the CF),
 bought with a 2033 first, three swaps, three seconds and the hard cap. **LaMelo was wash-to-negative
 at a huge cost. LeBron is small-positive-to-good at almost none.** Mirror images.

**3. The only real risk is that a 42-year-old breaks down, and even that is nearly free.** The
availability tail is the whole game. He missed 14 games with sciatica last year and played ~60. If he
gives you 50 great games instead of a healthy body's 70, the bump shrinks; if he breaks down, the
roster spot is wasted (but you spent nothing). So it's a depth-vs-ceiling trade on an already thin,
Gobert-fragile roster, not an asset disaster.

## Why I still won't print a title percentage

Same rule as the LaMelo piece, and I held to it even though the answer here is more flattering:
- The model's own back-test on **star acquisitions still fails** (it can't see fit or availability, 
 the two things LeBron's value hinges on most). Under our pre-registered kill criteria, a failed
 back-test means no published number.
- The point estimate quietly assumes he's available. Nobody can promise a 42-year-old plays 70 games,
 so a precise "+2%" would be false precision.
So the honest answer is a **shape**: roughly [0, +4] points, positive-leaning, downside capped, 
"almost certainly doesn't hurt, plausibly helps a little, for free."

## The bottom line for the front office

As a **basketball process decision, a minimum LeBron is defensible-to-smart**: cheap, asymmetric,
optional, with a real (if modest and availability-dependent) title-relevant upside and a downside you
can bench. The catch is entirely mechanical, the hard cap means he bumps your 15th man, and you're
betting a 42-year-old's health over a healthier body's 70 games. It's the opposite kind of bet from
LaMelo: that one spent the future for a wash; this one risks almost nothing for a taste of a ceiling.

## Where everything lives

- `alebron/DELIVERABLE.md`, the full locked writeup (sections 1-10 + forward predictions).
- `alebron/data/cap_state.json`, the hard-cap feasibility math.
- `alebron/data/impact/`, transport + team-strength (LeBron's marginal value).
- `alebron/impact/sweep_lebron_availability.py`, the age × availability fork.
- `alebron/data/sim/`, the CRN-paired title/round odds + the three-alpha scenario table.
- `alebron/data/field_2026_offseason.json`, every verified 2026 move with sources.
- `alebron/prereg/preregistration.md`, the immutable prediction log reality grades in 2026-27.

Two honesty flags I want you to see: (a) the inherited baseline assumes DiVincenzo is OUT for
2026-27, but 2026 reporting lists him back, I left it as-is for consistency and flagged it; it moves
the absolute odds, not the LeBron delta. (b) The field for the sim is the calibrated 2025-26-anchored
one; I also ran a version updated for the Jaylen Brown trade and the other big moves, the LeBron
delta barely moved (that's the point of the CRN pairing), so I kept the clean field as primary.
