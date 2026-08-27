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
MAX_ROTATION = 15         # a legal roster maximum; extend no further

# S1: position pools. A player's PRIMARY listing decides his pool, so Guard-Forward is
# a guard and Forward-Centre is a forward. The budgets are the league-average share of
# team minutes by pool, measured on 2025-26 (guard 49.81%, forward 36.11%, big 14.08%),
# so they are observed rather than assumed and are identical for all 30 teams as R2
# requires. A team whose pool cannot absorb its budget spills the excess to the others.
POOL_BUDGET = {"guard": 0.4981, "forward": 0.3611, "big": 0.1408}


def pool_of(position) -> str:
    p = str(position or "")
    if p.startswith("Center"):
        return "big"
    if p.startswith("Guard"):
        return "guard"
    if p.startswith("Forward"):
        return "forward"
    return "forward"          # unknown listings default to the middle pool


def rank_score(pct_mpg, pct_net):
    return MPG_WEIGHT * pct_mpg + (1 - MPG_WEIGHT) * pct_net


def ceiling_for(prior_mpg):
    """Per-player minutes ceiling. Vectorised: returns an array for array input."""
    return np.minimum(np.asarray(prior_mpg, dtype=float) + CEILING_BONUS,
                      CEILING_HARD_MAX)


def allocate_pooled(players: pd.DataFrame, curve: pd.Series,
                    budget_share: dict | None = None) -> dict:
    """S1: allocate within position pools, so a move can only take minutes from players
    who could actually play that position.

    This generalises the C3 slot constraint from Kuminga to EVERY player. Without it,
    removing a guard hands his minutes to centres and the counterfactual for any
    player-specific move is "his minutes go to the best players on the roster", which
    no coach can do. With it, removing Dosunmu means another guard plays.

    Each pool gets a budget (league-average share of 240) and is filled by the same
    rank / curve / ceiling machinery. Where a pool has too little capacity to absorb
    its budget, the remainder spills to the pools that do, which keeps the team at a
    full 240 minutes.
    """
    g = players[players.rs_avail > 0].copy()
    if g.empty or "pool" not in g.columns:
        return allocate(players, curve, use_ceiling=True)

    # Budgets are TEAM-SPECIFIC where a team's own prior-season shape is known, and
    # fall back to the league average otherwise. This matters and is not a refinement:
    # Minnesota played the MOST big minutes in the league in 2025-26 (53.7 a game
    # against a 33.8 average, rank 1 of 30) because Gobert and Reid played together.
    # Forcing the league-average 33.8 onto them erases exactly the structure that
    # losing Reid destroys, and it turned "Reid out" from clearly negative into a wash.
    # That was an artefact of the budget, not a finding about Naz Reid.
    share = budget_share or POOL_BUDGET
    budgets = {k: share.get(k, POOL_BUDGET[k]) * TEAM_MINUTES for k in POOL_BUDGET}
    out, unfilled = {}, 0.0
    caps_left = {}
    for pool, budget in budgets.items():
        sub = g[g.pool == pool].sort_values("rank_score", ascending=False)
        if sub.empty:
            unfilled += budget
            caps_left[pool] = 0.0
            continue
        cm = np.arange(1, len(sub) + 1)
        curve_min = np.array([curve.get(float(i), curve.iloc[-1]) for i in cm])
        desired = (CURVE_WEIGHT * curve_min
                   + (1 - CURVE_WEIGHT) * sub.prior_mpg.to_numpy(dtype=float))
        desired = desired * sub.rs_avail.to_numpy(dtype=float)
        cap = ceiling_for(sub.prior_mpg.to_numpy()) * sub.rs_avail.to_numpy(dtype=float)
        take = _waterfill(desired, cap, budget)
        short = budget - float(take.sum())
        if short > 1e-9:
            unfilled += short
        caps_left[pool] = float((cap - take).sum())
        for pid, m in zip(sub.player_id, take):
            if pd.notna(pid) and m > 0:
                out[str(int(pid))] = out.get(str(int(pid)), 0.0) + float(m)

    # Spill whatever no pool could absorb, in proportion to remaining headroom.
    if unfilled > 1e-9 and sum(caps_left.values()) > 1e-9:
        for pool, room in caps_left.items():
            if room <= 1e-9:
                continue
            extra = unfilled * room / sum(caps_left.values())
            sub = g[g.pool == pool].sort_values("rank_score", ascending=False)
            cap = ceiling_for(sub.prior_mpg.to_numpy()) * sub.rs_avail.to_numpy(dtype=float)
            cur = np.array([out.get(str(int(p)), 0.0) if pd.notna(p) else 0.0
                            for p in sub.player_id])
            add = _waterfill(np.maximum(cap - cur, 1e-9), cap - cur, extra)
            for pid, m in zip(sub.player_id, add):
                if pd.notna(pid) and m > 0:
                    out[str(int(pid))] = out.get(str(int(pid)), 0.0) + float(m)
    return out


def _waterfill(desired, cap, budget):
    """Hand out `budget` minutes in proportion to `desired`, capped by `cap`."""
    mins = np.zeros_like(np.asarray(desired, dtype=float))
    cap = np.asarray(cap, dtype=float)
    desired = np.asarray(desired, dtype=float)
    remaining = float(budget)
    for _ in range(64):
        room = cap - mins
        active = room > 1e-9
        if remaining <= 1e-9 or not active.any():
            break
        w = desired * active
        if w.sum() <= 0:
            w = active.astype(float)
        take = np.minimum(remaining * w / w.sum(), room)
        if take.sum() <= 1e-12:
            break
        mins = mins + take
        remaining -= float(take.sum())
    return mins


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
        # A game IS 240 minutes. That is an accounting identity, not a modelling
        # choice, so where the ceiling rule cannot accommodate it the RULE yields.
        # Ten teams hit this: rosters made up of rookies and low-minute bench players
        # have low prior loads, so "prior + 3" cannot cover a full game even across a
        # 15-man rotation. Rather than let those teams play 221 minutes, which would
        # silently understate every one of their players' contributions, the ceilings
        # are scaled up by exactly the factor needed. The scaling is reported.
        capacity = float(cap.sum())
        if capacity < TEAM_MINUTES and capacity > 0:
            cap = cap * (TEAM_MINUTES / capacity)
        # Water-fill. Hand out the 240 minutes in proportion to desired load, capping
        # anyone who hits his ceiling and re-dealing the REMAINDER to whoever still has
        # headroom, until the minutes are placed or the rotation is physically full.
        #
        # The remainder must be carried across iterations. A first version added
        # min(share, room) and then re-tested only for players still OVER their cap;
        # once everyone was at or under, the loop exited with the undealt remainder
        # simply dropped, and Minnesota's rotation summed to 239.3 instead of 240.
        mins = np.zeros_like(desired)
        remaining = TEAM_MINUTES
        for _ in range(64):
            room = cap - mins
            active = room > 1e-9
            if remaining <= 1e-9 or not active.any():
                break
            w = desired * active
            if w.sum() <= 0:
                w = active.astype(float)
            take = np.minimum(remaining * w / w.sum(), room)
            if take.sum() <= 1e-12:
                break
            mins = mins + take
            remaining -= float(take.sum())
        # If capacity genuinely cannot hold a full game the team plays short rather
        # than pushing anyone past his ceiling; callers can see it in the row sum.

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
