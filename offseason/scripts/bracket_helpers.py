#!/usr/bin/env python3
"""
bracket_helpers.py  -- shared helpers for Component E.

Builds role-tagged rotations from a season's ACTUAL minutes (top 10 by minutes, roles
assigned by minutes rank), used both to fill the ~18 non-contender teams in the
2026-27 baseline and to calibrate the hot-rollup -> RS-net deflation against past
seasons. Roles match the projected-roster vocabulary so the same rollup path applies
to projected and actual rosters identically.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POSTMORTEM)
sys.path.insert(0, HERE)
from lib import db                       # noqa: E402
import build_rotation_model as B         # noqa: E402

ROLE_MPG = {"starter": 34, "sixth": 26, "rotation": 18, "deep": 9}


def _role_for_rank(rank):
    if rank < 5:
        return "starter"
    if rank == 5:
        return "sixth"
    if rank < 9:
        return "rotation"
    return "deep"


def actual_top_rotations(season_year, top_n=10):
    """{abbr: [{nba_player_id, role, mp}]} from a season's actual minutes. Cached."""
    if (season_year, top_n) in _ROT_CACHE:
        return _ROT_CACHE[(season_year, top_n)]
    rows = db.query("""SELECT team_abbreviation t, player_id, SUM(minutes_played) m
                       FROM nba_player_stats WHERE season_year=%s
                       GROUP BY t, player_id""", (season_year,))
    by = {}
    for _, r in rows.iterrows():
        by.setdefault(r["t"], []).append((str(r["player_id"]), float(r["m"])))
    out = {}
    for ab, players in by.items():
        players.sort(key=lambda x: -x[1])
        rot = [{"nba_player_id": pid, "role": _role_for_rank(i), "mp": mp}
               for i, (pid, mp) in enumerate(players[:top_n])]
        out[ab] = rot
    _ROT_CACHE[(season_year, top_n)] = out
    return out


_NET_CACHE, _ROT_CACHE = {}, {}


def actual_team_net(yr_int):
    """{abbr: actual RS per-100 net rating} for the season ending in yr_int. Cached, since
    the championship layer rolls this up many times per run."""
    if yr_int in _NET_CACHE:
        return _NET_CACHE[yr_int]
    rows = db.query("""SELECT g.team_abbreviation t, AVG(a.net_rating) net
                       FROM nba_games g JOIN nba_team_advanced_stats a
                         ON a.game_id=g.game_id AND a.team_tricode=g.team_abbreviation
                       WHERE g.season_type='Regular Season' AND (g.season_id %% 10000)=%s
                       GROUP BY t""", (yr_int,))
    _NET_CACHE[yr_int] = {r["t"]: float(r["net"]) for _, r in rows.iterrows()}
    return _NET_CACHE[yr_int]


def roster_to_mpg(rotation):
    raw = {p["nba_player_id"]: ROLE_MPG.get(p["role"], 12) for p in rotation}
    tot = sum(raw.values()) or 1
    return {pid: m / tot * 240.0 for pid, m in raw.items()}


def team_dim_profile(rotation, dims):
    return B.team_profile(roster_to_mpg(rotation), dims)
