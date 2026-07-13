# Session 2026-07-13 — Ruling A paperwork, equity final pass, Part 3 v3, pre-publish

Bobby ruled the P1 baseline question ("A") and directed the full remaining
pass ahead of publishing all three parts.

## Ruling A paperwork (executed with the ruling)
- outputs/validation/p1_baseline_decision.md: ruling recorded verbatim,
  with the sequencing disclosure (the 07-12 grade preceded the ruling; the
  ruling ratifies it; direction holds under either baseline).
- docs/decisions.md: mirrored entry.
- docs/predictions.md: dated PIN-NOTE addendum under P1 (04:02 artifact,
  commit 8931e70c); the logged prediction untouched.
- JULY6_RUNBOOK.md: banner marked RESOLVED, Step 4 corrected to .167/.422.

## Equity final pass (adapter F) -> total_asset_cost.json
New src/integrate/joan_bet_adapter.py (spec 7.8 interface,
equity_from_value_draws + runner). Chain: per-path 4yr-VORP payoffs
regenerated with the pricing pass's exact rng (seed+7) and ASSERTED to
reproduce swap_pricing_FINAL.json (mean + median, both top1 branches)
before any equity number is written; per-season net delta = V/4 (season
VORP is already a net-rating-equivalent unit); tier read per delivery
season (draft year +1..+4, clamped to the 2033 horizon) on the receiving
team's simulated win path, net = (win_pct - 0.5)/c; ON-5 curve
interpolated on (tier base_net x delta grid), anchored at 0, odd symmetry
for negative draws, end-slope extrapolation past 4.0. Two co-equal
perspectives per plan D3 amendment 1. Deltas only, per the gate.

Headline (top1_true, cumulative 4-yr title-equity pp, picks+swaps):
- delivered to CHA: mean +8.27 [q10 -0.66, q90 +23.57], median 3.34
- forgone by MIN:  mean +4.51 [q10 -0.67, q90 +13.05], median 1.97
- the 1.8x asymmetry is real and diagnosable: payments concentrate in
  MIN-collapse / CHA-crest futures where MIN's marginal title curve is
  flat and CHA's is steep. MIN's forgone equity is nearly flat across the
  four world-states (4.1/4.7/4.3/4.8); CHA's runs 4.1 -> 14.1.
- line items (VORP): resolved 2026 net 0.245 (EV28 .819 - EV33 .574);
  seconds flat .372 each (band .084-.67), trio 1.116; all-in package 6.22.
- package totals in equity: CHA +10.15, MIN +5.98. top1_false moves the
  CHA number -0.37.
- spec 7.6's "reconcile with an existing Joan Bet pick-value module"
  clause: no such module exists (confirmed at curve build), nothing to
  reconcile; validation report untouched (no gate consumes the equity
  layer).

## Part 3 v3 (docs/drafts/stage3_priced_trade_draft_v3.md)
All slots filled from exports: Beat 3 (2026 line item + seconds + all-in
6.2), Beat 5 (both-perspectives equity + asymmetry + world-state shape +
house-gate language), Beat 6 (clean-room verdict quoted verbatim from
lamelo/DELIVERABLE.md one-line finding; its no-title-number gate honored
explicitly). Two flagged prose touches: "full package" -> "headline
package" (collision with the new all-in number), tornado arm count made
honest (fourteen same-currency arms + the win-shares currency check;
redundant ws sentence removed). Headline unit choice (agent, Bobby may
veto at the read): cumulative 4-yr pp leads, per-season in one clause.

## Viz
- NEW equity_bill_fragment.html (vizId equity-bill), swap-ledger interval
  grammar, two rows + 1.8x gap bracket (wide layouts only; caption carries
  it in compact). Data from total_asset_cost.json. Script parse-checked.
- tornado retitled "Fourteen ways to shake the bill" (README manifest; the
  fragment caption already said fourteen), altText extended with the
  fifteenth-arm currency-check clause.
- article/viz/build_previews.py NEW: the previously ephemeral preview
  generator, persisted; previews regenerated in ARTICLE order (they were
  in build order), Part 3 now carries 5 fragments.
- README manifest: thirteen fragments, stage3 v3, equity-bill row +
  provenance, "may earn one more visual" note resolved.

## Tests
tests/test_equity_adapter.py NEW (7 tests: zero->zero, tier monotonicity,
odd symmetry, tier clamp, delta extrapolation, horizon clamp, export gate
language). Suite 60 green (was 53).

## Open items (the publish checklist)
- BOBBY: numbers-in-place reads, the release gates: Part 1 v3, Part 2 v4,
  Part 3 v3. Part 2 carries the public P1 grade paragraph.
- Publish 13 viz at /admin/visualizations/new (vizId/title/altText in
  article/viz/README.md), then the three articles, Part 1 first.
- Hero images: none exist; silhouette rule applies if the template wants
  them.
- BOBBY: the carousel word (still pending on the record).
- BOBBY: gate 8.5 completion (2019 PG replay + negative control) before
  Part 3 ships, or ship with the in-text partial disclosure as drafted.
- Part 2's "the full scorecard is public" line: link the validation
  report from the article at publish time.
