"""Era-keyed NBA draft lottery mechanics, vectorized across simulation paths.

Three eras:

1. `pre_2019_weighted` (1990-2019 drafts; used only for historical replays,
   e.g. the 2013 Celtics-Nets pipeline replay): 14 lottery teams, weights
   250/199/156/119/88/63/43/28/17/11/8/7/6/5 (combinations out of 1000),
   TOP 3 picks drawn, remainder in inverse record order.

2. `post_2019` (2019-2026 drafts; historical replay only going forward):
   14 teams, weights 140/140/140/125/105/90/75/60/45/30/20/15/10/5,
   TOP 4 picks drawn, remainder in inverse record order.

3. `post_2026_reformed` -- the "3-2-1 lottery" (effective 2027 draft; the
   forward-sim era). NOT a fixed odds table: ball counts derive from each
   season's play-in outcome, ALL 16 picks are drawn, and three constraints
   break pure Plackett-Luce sampling (why eras 1-2 use the exact Gumbel
   top-k trick and this era uses custom sequential draw logic):
     - Ball counts: non-play-in lottery teams 3 balls, except the three
       worst records league-wide ("draft relegated") 2 balls; the 9/10
       play-in seeds 2 balls; the 7v8 play-in game losers 1 ball.
       (37 total balls; published pick-1 marginals 2/37=5.4%, 3/37=8.1%.)
     - FLOOR: the three worst teams are guaranteed picks within the top 12.
     - NO REPEAT #1: a team cannot win the first overall pick in
       consecutive drafts.
     - NO TOP-5 THREE STRAIGHT: a team cannot land a top-5 pick in three
       consecutive drafts.

DOCUMENTED ASSUMPTIONS for post_2026_reformed (public sources -- NBA.com BoG
release, CBS, ESPN, Wikipedia, pulled 2026-07-01 -- do not publish the
drawing micro-procedure; flagged in the validation report):
  A1. The 16 ball-holders are fixed by play-in ROLE (10 non-play-in lottery
      teams + four 9/10 seeds + two 7v8 losers) regardless of whether a
      second-chance winner ultimately makes the playoffs (per ESPN:
      "the loser of the 7-8 play-in game and both 9- and 10-seeds" are
      included; this is what makes the count 16).
  A2. Constraint enforcement is by exclusion-and-renormalization: a team
      barred from pick 1 (or picks 1-5) has its balls ignored for those
      draws and re-enters afterward.
  A3. Floor enforcement: before drawing pick p, if the number of undrawn
      floored teams equals 12 - p + 1, remaining draws through pick 12 are
      held among floored teams only (their ball weights, renormalized).
  A4. Picks 17-30 go to the 14 playoff teams holding no lottery balls, in
      inverse record order.
  A5. Cross-year constraints look back across the 2026 system boundary
      (a 2026 #1 bars a 2027 #1).
  A6. Relegation membership ties (equal records at the 3rd-worst cut) break
      by per-path uniform draw (real procedure: random drawing).
"""

from __future__ import annotations

import numpy as np

PRE_2019_WEIGHTS = np.array([250, 199, 156, 119, 88, 63, 43, 28, 17, 11, 8, 7, 6, 5], dtype=float)
POST_2019_WEIGHTS = np.array([140, 140, 140, 125, 105, 90, 75, 60, 45, 30, 20, 15, 10, 5], dtype=float)

BALLS_LOTTERY = 3       # non-play-in lottery team
BALLS_RELEGATED = 2     # three worst records league-wide
BALLS_NINE_TEN = 2      # 9/10 play-in seeds
BALLS_78_LOSER = 1      # loser of the 7v8 play-in game
FLOOR_WORST3_MAX_PICK = 12
N_REFORMED_LOTTERY = 16


def gumbel_topk_draw(weights: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    """Exact Plackett-Luce sequential draw via the Gumbel top-k trick.

    weights: (n_paths, n_teams) nonnegative; zero weight = ineligible.
    Returns (n_paths, k) team indices in draw order (pick 1..k).
    Valid ONLY for unconstrained weighted draws (pre-2019 / post-2019 eras).
    """
    with np.errstate(divide="ignore"):
        logw = np.log(weights)
    g = rng.gumbel(size=weights.shape)
    keys = np.where(weights > 0, logw + g, -np.inf)
    return np.argsort(-keys, axis=1)[:, :k]


def legacy_lottery(order_worst_first: np.ndarray, era: str, rng: np.random.Generator) -> np.ndarray:
    """Pre-reform lottery. order_worst_first: (n_paths, 14) team indices of
    lottery teams, worst record first. Returns (n_paths, 14) pick order:
    slot j (0-based) holds the team index picking at slot j+1."""
    if era == "pre_2019_weighted":
        table, k = PRE_2019_WEIGHTS, 3
    elif era == "post_2019":
        table, k = POST_2019_WEIGHTS, 4
    else:
        raise ValueError(f"legacy_lottery got era {era!r}")
    n_paths, n_lot = order_worst_first.shape
    assert n_lot == 14
    weights = np.broadcast_to(table, (n_paths, 14)).copy()
    drawn_pos = gumbel_topk_draw(weights, k, rng)          # positions within lottery order
    picks = np.empty((n_paths, 14), dtype=order_worst_first.dtype)
    # top-k drawn teams
    for j in range(k):
        picks[:, j] = np.take_along_axis(order_worst_first, drawn_pos[:, j:j + 1], axis=1)[:, 0]
    # remainder in inverse record order among undrawn
    mask = np.ones((n_paths, 14), dtype=bool)
    np.put_along_axis(mask, drawn_pos, False, axis=1)
    for p in range(n_paths):
        picks[p, k:] = order_worst_first[p, mask[p]]
    return picks


def reformed_lottery(
    lottery_teams: np.ndarray,
    balls: np.ndarray,
    relegated_mask: np.ndarray,
    barred_no1_mask: np.ndarray,
    barred_top5_mask: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """The 3-2-1 lottery, drawn sequentially per path (constraints break the
    Gumbel shortcut -- see module docstring).

    lottery_teams: (n_paths, 16) team indices ordered worst record first.
    balls:         (n_paths, 16) ball counts aligned with lottery_teams.
    relegated_mask:(n_paths, 16) True for the three floored worst teams.
    barred_no1_mask / barred_top5_mask: (n_paths, 16) cross-year constraint
        flags aligned with lottery_teams (True = barred).
    Returns (n_paths, 16): slot j holds the team picking at slot j+1.
    """
    n_paths, n_lot = lottery_teams.shape
    assert n_lot == N_REFORMED_LOTTERY
    picks = np.empty_like(lottery_teams)
    for p in range(n_paths):  # vectorize later if profiling demands (S5)
        w = balls[p].astype(float).copy()
        floored_left = int(relegated_mask[p].sum())
        for slot in range(n_lot):
            eligible = w > 0
            # cross-year constraints
            if slot == 0:
                eligible &= ~barred_no1_mask[p]
            if slot < 5:
                eligible &= ~barred_top5_mask[p]
            # floor: force floored teams if slots are running out (A3)
            slots_left_to_floor = FLOOR_WORST3_MAX_PICK - slot
            if floored_left > 0 and slots_left_to_floor <= floored_left:
                eligible &= relegated_mask[p] & (w > 0)
            we = np.where(eligible, w, 0.0)
            if we.sum() <= 0:  # constraint deadlock: relax cross-year bars (documented)
                we = np.where(w > 0, w, 0.0)
            idx = int(rng.choice(n_lot, p=we / we.sum()))
            picks[p, slot] = lottery_teams[p, idx]
            if relegated_mask[p, idx]:
                floored_left -= 1
            w[idx] = 0.0
    return picks
