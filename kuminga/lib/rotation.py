"""The minutes heuristic, in ONE place.

This used to exist twice, once in build_rotations.py and once in shapley.allocate(),
and the two drifted: one ranked percentiles league-wide, the other re-ranked inside
each roster. Anything that allocates minutes now imports from here.

THE RULE (C2 revision)

1. Rank players by a LEAGUE-WIDE score, computed once:
       0.5 * pct_rank(prior minutes per appearance) + 0.5 * pct_rank(consensus net)
   League-wide matters: a blend of two percentiles is not order-preserving under a
   change of reference set, so re-ranking inside a coalition would make a player's
   standing depend on which teammates happen to be in it.

2. Desired minutes are a 50/50 blend of an empirical team-rank curve (fitted on
   2025-26) and the player's own prior per-appearance load.

3. NEW: each player carries a CEILING of min(prior load + 3, 36) minutes.

   Why. Without a ceiling the rotation is simply rescaled to 240 on every add or
   remove, so taking a player out hands his minutes to the whole rotation in
   proportion, including to the stars. That is wrong in a specific direction: it lets
   a 31-minute centre absorb part of a departed forward's load and turns every roster
   question into a referendum on the best player's minutes. Real minutes move along
   the depth chart, not up it. The ceiling is anchored on what each player has
   actually carried, plus a little room for a genuine role increase, and hard-capped
   at 36 because almost nobody sustains more.

4. Overflow cascades DOWN the rank order. Anyone over his ceiling is capped and the
   excess is redistributed, in proportion to desired minutes, among players still
   below theirs. Repeated to convergence. If the rotation's total ceiling capacity is
   under 240, the rotation is EXTENDED one player at a time down the rank order until
   it can hold a full game, which is the honest answer to "who plays if everyone
   ahead is maxed out".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ROTATION_SIZE = 10
MPG_WEIGHT = 0.5          # weight on prior minutes in the rank score
CURVE_WEIGHT = 0.5        # weight on the team-rank curve vs the player's own load
TEAM_MINUTES = 240.0
CEILING_BONUS = 3.0       # minutes of room above a player's prior load
CEILING_HARD_MAX = 36.0
MAX_ROTATION = 14         # never extend past a plausible rotation


def rank_score(pct_mpg, pct_net):
    return MPG_WEIGHT * pct_mpg + (1 - MPG_WEIGHT) * pct_net


def ceiling_for(prior_mpg):
    return float(np.minimum(np.asarray(prior_mpg, dtype=float) + CEILING_BONUS,
                            CEILING_HARD_MAX))


def allocate(players: pd.DataFrame, curve: pd.Series, use_ceiling: bool = True) -> dict:
    """Return {player_id_str: minutes}. Requires a precomputed league-wide rank_score."""
    g = players[players.rs_avail > 0].copy()
    if g.empty:
        return {}
    if "rank_score" not in g.columns or g.rank_score.isna().any():
        raise ValueError("allocate() requires a precomputed league-wide rank_score")
    g = g.sort_values("rank_score", ascending=False).reset_index(drop=True)

    n = min(ROTATION_SIZE, len(g))
    if use_ceiling:
        # Extend the rotation until it can physically hold a full game.
        while n < min(MAX_ROTATION, len(g)):
            if ceiling_for(g.prior_mpg.iloc[:n].to_numpy()).sum() >= TEAM_MINUTES:
                break
            n += 1

    r = g.iloc[:n].copy()
    r["rot_rank"] = np.arange(1, len(r) + 1)
    cm = r.rot_rank.map(lambda i: curve.get(float(i), curve.iloc[-1])).to_numpy(dtype=float)
    desired = CURVE_WEIGHT * cm + (1 - CURVE_WEIGHT) * r.prior_mpg.to_numpy(dtype=float)
    desired = desired * r.rs_avail.to_numpy(dtype=float)
    if desired.sum() <= 0:
        return {}
    mins = desired / desired.sum() * TEAM_MINUTES

    if use_ceiling:
        cap = ceiling_for(r.prior_mpg.to_numpy()) * r.rs_avail.to_numpy(dtype=float)
        # Water-fill: cap whoever is over, push the excess to whoever has headroom,
        # in proportion to desired minutes. Repeat until nobody is over.
        for _ in range(64):
            over = mins > cap + 1e-9
            if not over.any():
                break
            excess = float((mins[over] - cap[over]).sum())
            mins = np.where(over, cap, mins)
            room = cap - mins
            openslots = room > 1e-9
            if not openslots.any():
                break                      # capacity exhausted; team plays short
            w = desired * openslots
            if w.sum() <= 0:
                w = openslots.astype(float)
            add = excess * w / w.sum()
            mins = mins + np.minimum(add, room)
        # Any minutes that still could not be placed are left unallocated rather than
        # forced onto someone past his ceiling; the shortfall is reported by callers.

    return {str(int(p)): float(m) for p, m in zip(r.player_id, mins)
            if pd.notna(p) and m > 0}


def allocation_frame(players: pd.DataFrame, curve: pd.Series,
                     use_ceiling: bool = True) -> pd.DataFrame:
    """Same as allocate() but returns the full frame, for reporting."""
    mp = allocate(players, curve, use_ceiling)
    g = players[players.rs_avail > 0].copy()
    g["mpg"] = g.player_id.map(lambda p: mp.get(str(int(p)), 0.0) if pd.notna(p) else 0.0)
    g = g[g.mpg > 0].sort_values("mpg", ascending=False).reset_index(drop=True)
    g["rot_rank"] = g.index + 1
    g["ceiling"] = ceiling_for(g.prior_mpg.to_numpy())
    g["at_ceiling"] = g.mpg >= g.ceiling - 1e-6
    return g
