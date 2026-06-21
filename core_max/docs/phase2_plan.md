# Phase 2 plan and PRE-REGISTRATION (young-player module, v1: Joan only)

Status: FROZEN (v1.1, 2026-06-20) after sign-off; see the re-registration log at the
bottom. The comp-class membership bands and the washout rule are frozen BEFORE a single
outcome is computed, so the bust tail cannot be tuned post-hoc. Any change requires a dated
re-registration, never a quiet adjustment after seeing results. Next: compute the class
membership and the within-class input profile; outcomes only after that check.

Carry-forwards binding here: [[phase2_carryforward]] (rim correction gated off for Joan;
asymmetric posture; comp pool + bust tail from the right reference class).

## Scope

v1 is **Joan Beringer only** (young big). TSJ (young wing) is a separate reference class
and far less prior-dominated; he gets his own comp class next, reusing this METHOD, not
this scaffolding. Hierarchical pooling is deferred until there are >= 2 players inside ONE
archetype (the precise trigger); one big + one wing share no trajectory, so analytic
per-archetype is correct now.

## The design (membership vs estimation, the split that beats the box bias)

The biased rookie box is used ONLY for membership (who is in the class). Impact is taken
ONLY from career years where the player cleared a minutes floor, so the box-to-impact map
is applied only on reliable samples. Selection bias is the thing we WANT here (we are
deliberately gathering players whose rookie box looked inflated like Joan's); estimation
bias is what we avoid.

## PRE-REGISTERED comp-class membership (structural, broad, frozen)

Membership is STRUCTURAL only. It does NOT condition on blocks, rebounds, or any
small-sample-inflated production stat (that lever is the gameable one and is kept out of
membership; Joan's flashiness, if used at all, enters only as a soft estimation covariate,
default OFF, never as a hard filter). A historical player-season qualifies as a Joan comp if:

- Position is a big: listed C, C-F, or F-C.
- Draft slot: first round, pick in [9, 25] (a band around #17).
- Entry age: rookie-season age in [18, 21].
- Limited rookie runway: rookie-season minutes in [100, 1200] (played, but limited; Joan: 314).
- Observability: rookie season between 2001-02 and 2020-21 (so >= 5 forward seasons exist
  through 2025-26).

Report the resulting N with the result. A development prior on a handful of players is
fragile no matter how clean the method, and that fragility must be visible, not smoothed
inside a tidy distribution.

PRE-COMMITTED TRANSPARENCY CHECK (not an outcome tweak): report the within-class INPUT
distributions alongside N, specifically where Joan's 314 rookie minutes sit inside the
class's minutes spread, plus the draft-slot and entry-age spreads. The 1200-minute ceiling
is generous relative to Joan's 314, so the class could quietly fill with young bigs who had
real rotation roles as rookies, a different developmental animal than a 7.9-minute-a-night
player. That cannot be tuned away after the fact, but it can be SEEN: if the class clusters
at 800-1200 minutes while Joan sat at 314, the ceiling diluted his reference class and the
fix is a dated re-registration, never a silent edit.

## PRE-REGISTERED washout rule and per-year measurement

For each comp, and for Joan, impact at a given career year is set as:
- **Measured** if that season's minutes clear the Phase-1 reliability bar: the SAME bar
  used everywhere in the project (3000 possessions; Joan was flagged unreliable at 1,156).
  Historical comps have minutes, not possessions, so the bar is the minutes-equivalent of
  3000 possessions, derived from the data's possessions-per-minute ratio and frozen with
  this spec. "Reliable" then means the same thing for a comp's measured year and an
  established player's estimate. Map that season's per-36 BASIC box (PTS/REB/AST/BLK/STL,
  era-handled below) to net impact via the reliable-player basic-box-to-impact map (fit on
  current reliable players, who have both basic box and consensus_net). Basic box, not
  box_net_bpm, because advanced-stat history is incomplete pre-2024.
- **Replacement** if minutes are below the bar or the player is out of the league that
  year: impact = a TRUE replacement level (a freely-available-player value), pegged from
  the sub-rotation / minimum population in the data, NOT the 5th percentile of reliable
  players. Reliable players are a selected, better population (everyone who cleared the
  bar), so their 5th percentile sits ABOVE true replacement and would OVER-credit busts,
  softening the left tail in the flattering direction. The replacement floor is carried as
  a Phase 3-4 sensitivity variant so the verdict's robustness to it is shown, not assumed.
  Low-minute and out-of-league years are honestly freely-available-level for the team, and
  this also avoids estimating off inflated low-minute box.

This single rule does double duty: it builds the bust tail (washouts -> true replacement)
and keeps early-career impact off the biased small-sample box.

## Era handling

z-score the mature box features within era (season) before mapping, to control league
drift. Do NOT restrict to a recent window: the class is already small and cannot afford to
shed N. Report N so the fragility is visible.

## Analytic comp-prior (empirical, so it traces to counts)

- Joan's trajectory prior at each career year = the EMPIRICAL distribution of the comps'
  realized impacts at that career year (measured or replacement). NOT a parametric form
  fitted to them (a fitted skew-Normal is a place to massage the tail).
- The bust mass = the EMPIRICAL washout rate in the class, NOT a hand-set mixture weight.
- Every number in Joan's distribution traces to a count in the data.

## Joan's data update (precision sets it, not fiat)

- Use his RAPM as the data (net_rapm with net_sd, 1,156 poss), NOT his box. His RAPM already
  sits BELOW his box, so using it sidesteps the inflation.
- The update is precision-weighted: comp-prior precision vs his noisy-estimate precision. His
  net_sd of 2.43 is so imprecise that a proper update moves the prior only marginally on its
  own. Let the precisions do that; then VERIFY and REPORT that the movement is small, rather
  than imposing "marginal" by hand (which would be one more tuned knob).
- The bust tail stays UNTOUCHED by his data.

## Horizon and outputs (2 years + real-option out-year)

Joan enters career year 2 in 2026-27. Outputs:
- Year 1 (2026-27 = career year 2) and Year 2 (2027-28 = career year 3): per-year impact
  distributions for the title-engine sampling window.
- Out-year real-option term: the comp class's mature (career years 4-6) impact distribution,
  the development payoff the 2-year window truncates.
Phase 3 samples Joan's per-year impact from these distributions each Monte Carlo iteration,
never collapsing to the mean; the real-option term feeds the Gobert-trade option value.

## Modeling approach (analytic, spec revised with reason)

Analytic per-archetype, not full Bayesian hierarchical. Modeling approach was never a LOCKED
decision; two things changed since the spec (Joan is severely prior-dominated, and 1b
confirmed his data must not pull him up), so for a single prior-dominated player a
hierarchical model collapses to "the comp distribution, barely updated" while adding
hyperprior and pooling-strength knobs that buy nothing and add attack surface. The data
layer transfers wholesale to a hierarchical v2 if there are ever >= 2 players in one
archetype, so analytic-first is low-regret, not throwaway.

## Build note (anti-overconfidence)

When mapping each comp's mature basic box to impact, carry the map's RESIDUAL UNCERTAINTY
into the comp impacts rather than using point predictions. Basic box explains less of impact
than the advanced version, so each mapped impact is itself noisy; on a small-N class that
within-comp uncertainty matters alongside the across-comp spread. Folding it in keeps the
comp distribution from looking artificially tight (same theme as the noisy-target correction).

## Flashiness covariate (resolved: OFF baseline, two-sided sensitivity)

OFF for the baseline (the asymmetric posture: his high box must not lift him). Reported ON
only as a TWO-SIDED sensitivity, with the comp data setting the SIGN, never pre-labeled an
upside knob. The 1b finding (the flashiest small-sample rookies are exactly the ones box
over-rates) means flashier rookies in this class may have regressed MORE, so an honestly-fit
flashiness covariate could pull Joan DOWN, not up. The sensitivity asks what flashiness
actually predicts in the class.

## PRE-COMMITTED reporting rules (before outcomes, binding)

1. FULL CLASS vs JOAN-LIKE SUB-CLASS, a binding check. Report Joan's distribution against
   BOTH the full N=28 class AND the Joan-like sub-class (rookie minutes <= 600, his minutes
   regime). The development prior counts as robust ONLY if the bet survives the faithful
   sub-class, not just the fuller class. The reason is FAITHFULNESS (the sub-class matches
   Joan's 21st-percentile minutes regime), not pessimism: it would be weighted the same way
   if it cut optimistic. The full class is the bigger-N primary; the sub-class is a binding
   check; the honest verdict lives in whether the bet holds across both. The sub-class is
   NOT demoted to a footnote if it comes back more bust-heavy (which the bust-clustered
   low-minute end suggests it will).
2. PER-YEAR MEASURED COUNT + out-year humility. Every comp contributes to every career year
   (washouts drop to replacement), so the year count stays 28, but the MEASURED count (comps
   who cleared the minutes bar that season) shrinks the further out you go. By career years
   4-6 (the out-year real-option), most of the class is at replacement and the upside rests
   on a handful of survivors, the thinnest estimate in the module and exactly where the
   development payoff lives. Report the per-year measured count alongside every distribution,
   and treat the out-year upside with wide humility (no confident upside claim off a
   six-survivor year-5 distribution).

## Re-registration log

- 2026-06-20 v1: initial pre-registration.
- 2026-06-20 v1.2: pre-committed the full-vs-sub-class binding check (sub-class = rookie
  minutes <= 600) and the per-year-measured-count + out-year-humility rules, before
  computing any outcome.
- 2026-06-20 v1.3: two corrections, each set on its MERITS (calibration means getting each
  number right; sobering is not a policy, and it is a coincidence, not a goal, when the
  merits point sobering).
  (a) Joan's data update is a QUANTITY MISMATCH, not a hand-tuned down-weight: his rookie
      RAPM measures career-year-1 impact, the comp prior is over year-2+ impact, and they
      are separated by exactly the development we model. Pooling them by raw precision is the
      banned "rookie predicts maturity" move (which we forbid for the comps) through a side
      door. The forward link is unvalidatable (no historical RAPM; comps' rookie years are
      mostly floored), so we adopt the fallback: year-2+ prior is essentially the comp prior,
      his rookie RAPM near-uninformative (carried through a wide, unvalidatable development
      gap, leaving a few-tenths nudge at most), and NOTHING from his rookie data touches the
      out-year mature term. This vindicates, not contradicts, the asymmetric posture.
  (b) Replacement floor is set from the WASHOUT COMPOSITION, not from which direction it
      leans: of the washout-years, the out-of-league fraction (truly freely-available,
      anchor ~-2.83) vs the under-floor-but-present fraction (marginal-but-rostered, anchor
      ~-0.97) sets a composition-weighted center, and the WHOLE bucket is floored to it (we
      never estimate under-floor survivors off their box, which is inflated for young bigs
      per 1b and would over-credit the washouts). Bracket [-0.97, -2.83] carried as the
      Phase 3-4 sensitivity on both full and sub-class. My earlier "5th-pct-reliable is
      generous" mechanism was backwards; the data corrected it.
- 2026-06-20 v1.1 (FROZEN): replacement floor changed from "5th pct of reliable" to a TRUE
  replacement level (sub-rotation / minimum population), carried as a Phase 3-4 sensitivity
  variant; measured-year floor aligned to the Phase-1 reliability bar (3000-possession
  minutes-equivalent) instead of an arbitrary 1000 minutes; within-class input-profile
  transparency check added; flashiness resolved to OFF-baseline / two-sided sensitivity;
  map residual-uncertainty propagation added. Frozen before any outcome is computed.
