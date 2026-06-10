=== Component F: Anthony Davis (both-out): Gobert + Randle out, AD in, counterparty WAS ===

FEASIBILITY (evaluate_move, gate runs first):
  legal=True | tier=over_cap_under_tax | hard_cap_tripped=False | no failing constraint
  outgoing Gobert $36.5M + Randle $33.3M = $69.8M out for AD $58.5M in (MIN sheds ~$11.4M).

MIN roster move: net +1.36 -> +0.69  (delta -0.67)
  (regressed core +2.16 + realigned roster delta -1.46)
  counterparty WAS: net -8.28 -> -3.98 (receives the outgoing package; stays a non-contender -> negligible on MIN's path)

DELTA P(TITLE) for MIN (band over sigma 4.5-6.5):
  pre  : 1.36-1.73-2.04%   (conf 4.6%, reach-CF 11.3%)
  post : 0.84-1.11-1.46%   (conf 3.2%, reach-CF 8.4%)
  ΔP(title) ~ -0.62pp (band -0.52 to -0.58pp)

GAUNTLET: P(MIN wins a series) vs each contender, pre -> post  [deep-round = slight upper bound]
  opp      pre%    post%    delta
  OKC      9.2%     8.0%    -1.2
  BOS     14.1%    12.4%    -1.7
  DET     16.0%    13.6%    -2.4
  SAS     17.1%    14.8%    -2.3
  NYK     25.2%    22.2%    -2.9
  MIA     28.8%    25.3%    -3.5
  HOU     25.9%    22.8%    -3.1
  DEN     31.4%    27.8%    -3.6
  CHA     32.8%    29.3%    -3.4
  ORL     30.4%    26.9%    -3.6
  CLE     34.6%    31.0%    -3.6

READ vs the key gates:
  vs OKC: 9.2% -> 8.0% (-1.2pp)
  vs SAS: 17.1% -> 14.8% (-2.3pp)
