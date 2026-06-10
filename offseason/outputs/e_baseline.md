=== Component E: 2026-27 BASELINE (calibrated, no trade) ===
params: deflation -5.4365+1.067*hot, wins=41.0+2.239*net; title odds as a BAND over sigma_unobs in [4.5, 5.5, 6.5] (central 5.5)  [build_e_calibration]

team   act25    exp  delta   net26  munc  title band (lo-mid-hi)   conf             src
OKC    10.96   7.89  +0.00    7.89  0.72         18.2-20.1-22.8%  34.9%    exp standpat
BOS     8.31   6.01  +1.21    7.21  0.91         13.2-14.1-15.1%  25.4%        exp+move
SAS     8.28   5.99  +0.00    5.99  0.97         10.8-11.6-12.1%  22.4%    exp standpat
DET     8.47   6.12  +0.00    6.12  0.38         11.1-11.5-12.3%  21.4%    exp standpat
HOU     5.38   3.93  +0.00    3.93  0.76            6.1-6.5-6.6%  13.8%    exp standpat
NYK     6.28   4.57  +0.00    4.57  0.72            5.8-6.0-6.2%  12.0%    exp standpat
MIA     1.98   1.52  +2.77    4.29  0.70            4.6-5.0-5.1%  10.6%        exp+move
DEN     5.11   3.74  +0.00    3.74  0.78            4.3-4.8-5.0%  10.7%    exp standpat
ORL     0.49   3.25  +2.79    3.25  0.82            3.7-4.2-4.5%   8.8%  health-rebound
CHA     4.96   3.63  +0.00    3.63  0.54            3.3-3.6-4.0%   8.3%    exp standpat
CLE     4.10   3.02  +0.00    3.02  0.70            2.5-2.9-3.3%   6.7%    exp standpat
MIN     2.88   2.16  -0.80    1.36  1.84            1.4-1.7-2.0%   4.4%        exp+move
LAL     1.45   1.15  +0.00    1.15  0.79            1.1-1.6-1.9%   4.1%    exp standpat
TOR     2.61   1.97  +0.00    1.97  0.26            1.3-1.5-1.8%   3.6%    exp standpat
MIN: net 1.36 title 1.4-1.7-2.0% (band over sigma) conf 4.4% reach-CF 11.2% reach-R2 29.0%

=== Variant A: Tatum three-way (BOS) ===
  Boston healthy-Tatum delta = +2.41 over its regressed (Tatum-less) core +6.01; baseline uses diminished (0.5x).
  branch            BOS net  BOS title  OKC title  champ is East
  healthy              8.42      18.3%      19.4%          52.3%
  diminished*          7.21      14.0%      20.3%          50.6%
  out                  6.01      10.4%      20.9%          49.4%
  * diminished is the DEFAULT (baseline) expectation for a Year-1 Achilles return.

=== Variant B: Giannis landing ===
  scenario                MIA net  MIA title  MIA conf
  Giannis -> MIA (base)      4.29       5.0%     10.3%
  Giannis stays MIL          1.52       1.1%      2.7%
  (MIN is West; these East moves change MIN's Finals opponent, not its path there.)

=== Matchup-overlay eyeball: MIN vs each contender (cannot be backtested) ===
  opp       net    base%  overlay%  overlay tilt
  OKC     +7.89    10.6%      9.2%         -1.4
  BOS     +7.21    12.9%     14.1%         +1.3
  DET     +6.12    17.3%     16.0%         -1.3
  SAS     +5.99    17.9%     17.1%         -0.8
  NYK     +4.57    25.1%     25.2%         +0.1
  MIA     +4.29    26.7%     28.8%         +2.1
  HOU     +3.93    28.8%     25.9%         -2.9
  DEN     +3.74    30.0%     31.4%         +1.4
  CHA     +3.63    30.7%     32.8%         +2.1
  ORL     +3.25    33.1%     30.4%         -2.6
  CLE     +3.02    34.6%     34.6%         +0.0
  (tilt > 0 = the overlay helps MIN vs that style; capped at a few series points)
