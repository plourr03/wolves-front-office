#!/usr/bin/env python3
"""
series_resolver.py  -- Championship layer, Component D.

The probability one team beats another in a best-of-7, given each team's strength
(per-100 net rating, the scale Component A produces) and home-court. Two parts:

  1. BASE: a per-game logistic on the net-rating gap with a home-court term,
     calibrated on every playoff game 1997-2025 (build_series_calibration.py fits
     b0/b1 and writes them to series_resolver_params.json). The per-game
     probabilities are composed into a best-of-7 by enumerating the 128 win/loss
     paths over the 2-2-1-1-1 venue pattern. "First to four" equals "majority of a
     hypothetical seven" because seven is odd, so the enumeration is exact.

  2. MATCHUP overlay (optional, bounded, OFF unless both six-dimension profiles are
     passed): three repeatable structural interactions, never small-sample lore:
       - half-court offense weakness  x  opponent half-court defense strength  (mean shift)
       - rim protection               x  opponent rim pressure                 (mean shift)
       - three-point reliance         ->  series VARIANCE, regresses P toward 0.5 (widens)
     The mean shift is capped at a few series points and the variance widening is
     capped separately. The base carries the strength signal; the overlay only tilts
     it. The overlay is deliberately small because, unlike the base, it cannot be
     validated against history (no historical dimensional profiles exist), so it is
     constrained to directionally-correct, documented nudges.

SCALE CONTRACT: net ratings in must be on the actual RS per-100 scale the base was
calibrated on. Component A's centered full-roster RS rollup is on that scale
(validation slope ~1.0). The opponent-profile "full-strength" nets (top-10 rotation,
no garbage dilution) run ~5-6 points hot and MUST be calibrated to the RS scale at
Component E before being fed here. Feeding hot nets in directly overstates every gap.

VALIDATION (build_series_calibration.py, 435 series 1997-2025):
  - By RATING GAP, the metric this resolver actually computes: predicted favorite
    series-win rate matches empirical within 3 points across every gap bucket. Clean.
  - By SEED, two opposing real effects show up, neither a resolver bug, both a property
    of feeding a single RS-net predictor: (a) R1 top seeds OVER-deliver vs their net gap
    (8-seeds almost never win), so the resolver is mildly conservative early; (b) in the
    CONFERENCE FINALS the higher-net team (by a mean +2.4 net) wins only ~50%, not the
    ~68% the gap implies. That is LATE-ROUND SURVIVORSHIP: deep-round survivors are
    positively selected on playoff quality RS net cannot see, so the gap overstates the
    true gap. CONSEQUENCE FOR E: a raw RS-net bracket sim will inflate the top seed's
    title path. This is exactly why E's baseline title odds must be calibrated to the
    de-vigged boards before any trade is simulated; the variance overlay only partly
    absorbs it. Do not "fix" it here with a round dummy (overfits 50 series).

    python series_resolver.py        # prints a small grid of example series odds
"""

import os
import json
import itertools
import math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PARAMS_PATH = os.path.join(DATA, "series_resolver_params.json")

DIMS = ["hc_creation", "secondary_playmaking", "off_ball_shooting",
        "def_versatility_poa", "rim_protect_reb", "transition"]

# Matchup-overlay caps. Conservative by design (the overlay is not history-validated).
MATCHUP_MEAN_CAP = 0.05      # max shift to the SERIES win prob from the two mean terms
VAR_SHRINK_CAP = 0.06        # max regression of the series prob toward 0.5 (variance widening)
_MEAN_K = 0.25               # style-edge difference -> per-game logit scale (pre-cap)
_VAR_K = 0.30                # 3pt-reliance -> variance shrink scale (pre-cap)

# 2-2-1-1-1: the home-court holder hosts games 1,2,5,7 (indices 0,1,4,6).
_HC_HOME_GAMES = frozenset({0, 1, 4, 6})
# the 64 seven-game outcomes the favorite wins (>=4 wins); precomputed once.
_WIN_PATTERNS = np.array([p for p in itertools.product((1, 0), repeat=7)
                          if sum(p) >= 4], dtype=float)        # 64 x 7
_HOME_MASK_HC = np.array([1.0 if i in _HC_HOME_GAMES else 0.0 for i in range(7)])

_PARAMS = None


def load_params():
    """b0 = home-court advantage in logit units; b1 = logit per net-rating point.
    Falls back to documented defaults if the calibration file is absent (so the
    resolver is importable before the one-time fit has run)."""
    global _PARAMS
    if _PARAMS is None:
        if os.path.exists(PARAMS_PATH):
            _PARAMS = json.load(open(PARAMS_PATH, encoding="utf-8"))
        else:
            # league-typical fallbacks; replaced the moment calibration runs
            _PARAMS = {"b0": 0.40, "b1": 0.115, "source": "fallback_defaults"}
    return _PARAMS


def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def game_prob(net_F, net_O, F_home):
    """P(team F wins a single game vs O at the stated venue), on the RS net scale."""
    p = load_params()
    hca = p["b0"] if F_home else -p["b0"]
    return _sigmoid(hca + p["b1"] * (net_F - net_O))


def _series_prob_from_pgames(p_home, p_road, F_has_hc):
    """Exact best-of-7 win prob, summing F's win probability over the 64 seven-game
    outcomes it wins, under the 2-2-1-1-1 venue pattern. (First-to-four equals
    majority-of-seven since seven is odd, so this is exact.) Vectorized over patterns."""
    home_mask = _HOME_MASK_HC if F_has_hc else (1.0 - _HOME_MASK_HC)
    pg = home_mask * p_home + (1.0 - home_mask) * p_road            # per-game F win prob
    P = _WIN_PATTERNS * pg + (1.0 - _WIN_PATTERNS) * (1.0 - pg)     # 64 x 7
    return float(np.prod(P, axis=1).sum())


def base_series_prob(net_F, net_O, F_has_hc):
    p_home = game_prob(net_F, net_O, True)     # F hosting
    p_road = game_prob(net_F, net_O, False)    # F on the road
    return _series_prob_from_pgames(p_home, p_road, F_has_hc)


def _hc_offense(profile):
    return 0.5 * (profile["hc_creation"] + profile["off_ball_shooting"])


def _hc_defense(profile):
    return 0.5 * (profile["def_versatility_poa"] + profile["rim_protect_reb"])


def _rim_pressure(profile):
    # offense that attacks the rim: transition + half-court rim creation
    return 0.5 * (profile["transition"] + profile["hc_creation"])


def matchup_adjustment(profile_F, profile_O):
    """Returns (game_logit_shift_for_F, variance_shrink). Bounded structural overlay.

    Mean terms use the antisymmetric DIFFERENCE of the two teams' style edges, so the
    overlay is zero-sum (shift_F == -shift_O) and a mirror matchup adjusts nothing. The
    difference form also gets the sign right in all four quadrants, which the earlier
    product-of-centered-terms form did not (it helped both teams when both were strong).

    The terms ride on top of the net-rating base; they are a modest playoff-style tilt,
    not the strength signal. They deliberately do NOT re-credit a team's rim anchor:
    Wemby's / Gobert's rim deterrence already lives in the team's net rating via the
    defensive reweighting, and the team-level rim_protect_reb percentile is a diluted
    rotation average, so the rim term only adds the marginal style interaction. Capped."""
    # 1. F's half-court offense vs O's half-court defense, minus the reverse.
    off_F = _hc_offense(profile_F) - _hc_defense(profile_O)
    off_O = _hc_offense(profile_O) - _hc_defense(profile_F)
    off_term = off_F - off_O
    # 2. F's rim protection vs O's rim pressure, minus the reverse (F's wall blunts O's
    #    rim attack; O's wall blunts F's).
    rim_F = profile_F["rim_protect_reb"] - _rim_pressure(profile_O)
    rim_O = profile_O["rim_protect_reb"] - _rim_pressure(profile_F)
    rim_term = rim_F - rim_O
    logit_shift = _MEAN_K * (off_term + rim_term)
    # 3. three-point reliance -> series variance. A jumpshooting series is more random,
    #    which helps whoever is behind. Symmetric reliance of both teams.
    reliance = 0.5 * ((profile_F["off_ball_shooting"] - 0.5) + (profile_O["off_ball_shooting"] - 0.5))
    var_shrink = max(0.0, min(VAR_SHRINK_CAP, _VAR_K * max(0.0, reliance)))
    return logit_shift, var_shrink


def series_win_prob(net_F, net_O, F_has_hc, profile_F=None, profile_O=None,
                    return_parts=False):
    """P(F wins the series). With both profiles, applies the bounded matchup overlay;
    without them, returns the base. The mean overlay is clamped to MATCHUP_MEAN_CAP on
    the series scale; the variance overlay regresses the result toward 0.5."""
    p_base = base_series_prob(net_F, net_O, F_has_hc)
    if profile_F is None or profile_O is None:
        return (p_base, {"base": p_base}) if return_parts else p_base

    logit_shift, var_shrink = matchup_adjustment(profile_F, profile_O)
    # apply the mean shift at the per-game level, then recompose the series
    p_home = _sigmoid(math.log(game_prob(net_F, net_O, True) / (1 - game_prob(net_F, net_O, True))) + logit_shift)
    p_road = _sigmoid(math.log(game_prob(net_F, net_O, False) / (1 - game_prob(net_F, net_O, False))) + logit_shift)
    p_mean = _series_prob_from_pgames(p_home, p_road, F_has_hc)
    # clamp the mean overlay's effect on the series number
    p_mean = p_base + max(-MATCHUP_MEAN_CAP, min(MATCHUP_MEAN_CAP, p_mean - p_base))
    # variance widening: regress toward a coin flip
    p_final = 0.5 + (p_mean - 0.5) * (1.0 - var_shrink)
    if return_parts:
        return p_final, {"base": p_base, "after_mean": p_mean, "var_shrink": var_shrink,
                         "logit_shift": logit_shift, "final": p_final}
    return p_final


if __name__ == "__main__":
    p = load_params()
    print(f"params: HCA(logit) b0={p['b0']:.3f}  net-slope b1={p['b1']:.4f}  "
          f"[{p.get('source','?')}]")
    print(f"  -> a single home game, even teams: P = {game_prob(0,0,True):.3f}")
    print(f"  -> +5 net rating gap, neutral: per-game home P = {game_prob(5,0,True):.3f}\n")
    print(f"{'net gap':>8}{'P(series), favorite has HC':>30}{'P(series), favorite no HC':>28}")
    for gap in (0, 1, 2, 3, 5, 7, 10):
        print(f"{gap:>8}{base_series_prob(gap,0,True):>30.3f}{base_series_prob(gap,0,False):>28.3f}")
