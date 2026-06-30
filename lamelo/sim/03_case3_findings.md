# Case 3 (star-acquisition retrodiction): FAILED, and the failure is informative

Ran on the 8 clean offseason sealed-era star acquisitions (box-BPM era-transport,
star-marginal prediction vs realized team change). Result, delta vs prior season:

| star | team | box-net | pred dNet | real dNet | pred dW | real dW | err W |
|---|---|---|---|---|---|---|---|
| Paul George | OKC | +0.38 | +0.25 | +2.75 | +0.6 | +1.0 | 0.4 |
| Jimmy Butler | MIN | +2.30 | +1.54 | +3.20 | +3.7 | +16.0 | 12.3 |
| Kyrie Irving | BOS | +1.11 | +0.74 | +1.01 | +1.8 | +2.0 | 0.2 |
| Chris Paul | HOU | +3.00 | +2.00 | +2.74 | +4.8 | +10.0 | 5.2 |
| Kawhi Leonard | TOR | +2.94 | +1.96 | -2.10 | +4.7 | -1.0 | 5.7 |
| Rudy Gobert | MIN | +2.31 | +1.54 | -2.49 | +3.7 | -4.0 | 7.7 |
| Donovan Mitchell | CLE | +1.12 | +0.75 | +3.62 | +1.8 | +7.0 | 5.2 |
| Dejounte Murray | ATL | +3.54 | +2.36 | -1.43 | +5.7 | -2.0 | 7.7 |

Pre-registered pass: (a) sign correct for ALL cases -> 5/8, FAIL. (b) within 4 wins for
>= 60% -> 2/8, FAIL. (c) inside 80% band for 70-90% -> 5/8, FAIL. **Case 3 FAILS.**

## The pattern (this is not random noise)

Two distinct failure modes, both real and both directly relevant to the LaMelo question:

1. **Sign-wrong on the fit-failure and load-management cases** (Kawhi-TOR, Gobert-MIN,
   Murray-ATL): the additive engine predicted a positive star bump, but the team got WORSE.
   Kawhi was load-managed (60 games), and Gobert-MIN and Murray-ATL were the canonical fit
   failures. The additive impact -> wins mapping CANNOT see fit or availability, which
   dominated these outcomes.
2. **Magnitude under-prediction on the successes** (Butler +16 realized vs +3.7 predicted;
   Chris Paul +10 vs +4.8; Mitchell +7 vs +1.8): the realized improvement was far larger
   than the star's marginal box-BPM, because the realized change folds in team health,
   other moves, and regression that the marginal prediction does not.

## What this means (downgraded per audit): mostly ESTIMAND MISMATCH, not fit-blindness

The crudeness of the test DRIVES THE MAJORITY of the failure, and that is the story, not a
footnote. The test compares a star's SOLO marginal impact against the team's FULL
year-over-year change, omitting (a) outgoing-player subtraction, (b) availability, and (c)
using an era-transported box-to-net map. Those omissions, not fit-blindness, account for
most of the misses. Concretely, the Gobert-to-MIN sign error: MIN sent out a LARGE package
(Kessler, Vanderbilt, Beasley, Beverley) to get him, and subtracting those outgoing players
plausibly flips the predicted delta negative with NO fit modeling at all. So the earlier
claim that "a full-trade reconstruction would NOT fix that" was an overclaim and is
retracted: a full reconstruction plausibly DOES fix Gobert-MIN.

What survives, stated correctly: the result is CONSISTENT WITH fit and availability
mattering, but the retrodiction CANNOT attribute the misses to additive fit-blindness,
because it omits outgoing-player subtraction, availability, and an era-stable box mapping.
At most one to two of the three sign errors (the Murray-ATL two-guard fit, and partly
Kawhi's load management) are plausibly genuine additive-blind failures. The strong claim
("empirical proof that star outcomes are fit-dominated and additively unpredictable") is
NOT supported by this test and is withdrawn.

## The implication for the LaMelo title number (re-anchored on identifiability)

The no-number decision rests primarily on the OVER-DETERMINED identifiability ground (spec
section 20), NOT on Case 3. The title-delta band already includes zero across the metric
fork, and once the role-player valuation fork (Fix 1) and the parametric input uncertainty
are included, the band crosses well below zero. The title delta is therefore not
identifiable at this resolution, which is a pre-registered kill criterion on its own. Case
3 is a SECONDARY, properly-caveated supporting consideration: it is consistent with star
outcomes being fit-and-availability sensitive, but (per the section above) it cannot prove
additive fit-blindness. So the number does not publish because it is not identifiable, with
Case 3 as corroboration rather than the load-bearing reason.

Cautionary note, in its defensible form only: Gobert -> MIN (2022), Minnesota's last big
star acquisition, was a fit-and-personnel disappointment in year one. That is a real,
relevant precedent for a team making another star bet whose payoff depends on fit. It is
NOT offered as proof that the engine validated, and the engine's mis-sign on it is
substantially the outgoing-package omission above, not a demonstrated fit-blindness.

## Verdict

- Structural / qualitative finding: PUBLISHABLE (fork-and-Gueye-dependent, ranging from a
  modest negative to a small positive, bought with a mountain of future). Unaffected by
  Case 3.
- Precise title percentages: NOT PUBLISHED, primarily because the title delta is NOT
  IDENTIFIABLE (the fork plus role-player plus parametric band crosses zero; spec section
  20), with Case 3 as secondary corroboration. Publish the qualitative finding and the
  scenario shape, and decline the precise number on identifiability grounds.
- Do NOT build a fuller Case 3 reconstruction (per the locked decision). Note honestly that
  such a reconstruction would plausibly fix the Gobert-MIN sign error (outgoing-package
  subtraction), which is exactly why Case 3 cannot be the load-bearing reason for the
  no-number decision; identifiability is.
