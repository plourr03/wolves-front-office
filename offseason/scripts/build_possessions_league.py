#!/usr/bin/env python3
"""
build_possessions_league.py

Phase 1 of the value layer: reconstruct possession-level data for EVERY team's
games across three seasons (2023-24, 2024-25, 2025-26), regular season and
playoffs, so a league-wide multi-year RAPM can be fit. The postmortem RAPM was
Wolves-games-only; valuing arbitrary acquisition targets needs full coverage.

Reuses the possession engine in postmortem/lib/lineups.process_game (team-
agnostic). Each game's possessions are cached to parquet, so the job is
restartable and incremental: re-running skips games already done.

Output per game (offseason/data/cache/possessions_league/<game_id>.parquet):
  game_id, season_year, season_type, possession_number, period,
  offensive_team_id, defensive_team_id, points_scored, end_reason,
  off_players_str, def_players_str   (5 ids each, comma-joined)

Run a smoke test first, then the full job (long; run in background):
    python build_possessions_league.py --limit 5
    python build_possessions_league.py
"""

import os
import sys
import time
import argparse

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMORTEM = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
CACHE = os.path.join(HERE, "..", "data", "cache", "possessions_league")

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(POSTMORTEM, ".env"))
except ImportError:
    pass
sys.path.insert(0, POSTMORTEM)
from lib import db, lineups  # noqa: E402

SEASONS = [2023, 2024, 2025]          # 2023-24, 2024-25, 2025-26
SEASON_TYPES = ["Regular Season", "Playoffs"]
KEEP = ["game_id", "season_year", "season_type", "possession_number", "period",
        "offensive_team_id", "defensive_team_id", "points_scored", "end_reason",
        "off_players_str", "def_players_str"]


def all_game_ids():
    """Every (game_id, season_year, season_type) across the window, all teams."""
    out = []
    for yr in SEASONS:
        for st in SEASON_TYPES:
            df = db.query(
                """SELECT DISTINCT game_id FROM nba_games
                   WHERE season_type = %s AND (season_id %% 10000) = %s
                   ORDER BY game_id""", (st, yr))
            for gid in df["game_id"].astype(str):
                out.append((gid, yr, st))
    # de-dupe game_ids (a game belongs to one season/type)
    seen, uniq = set(), []
    for gid, yr, st in out:
        if gid not in seen:
            seen.add(gid)
            uniq.append((gid, yr, st))
    return uniq


def process_one(game_id, season_year, season_type):
    out_path = os.path.join(CACHE, f"{game_id}.parquet")
    if os.path.exists(out_path):
        return "cached"
    try:
        poss = lineups.process_game(game_id)["possessions"]
        if poss is None or poss.empty:
            return "empty"
        poss = poss.copy()
        poss["game_id"] = game_id
        poss["season_year"] = season_year
        poss["season_type"] = season_type
        poss["off_players_str"] = poss["offensive_floor"].apply(
            lambda fs: ",".join(str(p) for p in sorted(fs)) if fs else "")
        poss["def_players_str"] = poss["defensive_floor"].apply(
            lambda fs: ",".join(str(p) for p in sorted(fs)) if fs else "")
        poss[KEEP].to_parquet(out_path, index=False)
        return "ok"
    except Exception as e:
        print(f"  {game_id}: EXCEPTION {type(e).__name__}: {e}", flush=True)
        return "fail"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="process at most N games (smoke test)")
    args = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)

    games = all_game_ids()
    if args.limit:
        # for the smoke test, prefer non-Wolves games to confirm league coverage
        games = games[:args.limit]
    n = len(games)
    print(f"League possession build: {n} games across {SEASONS} (RS+PO). cache={CACHE}", flush=True)

    counts = {"ok": 0, "cached": 0, "empty": 0, "fail": 0}
    t0 = time.time()
    for i, (gid, yr, st) in enumerate(games, 1):
        counts[process_one(gid, yr, st)] += 1
        if i % 50 == 0 or i == n:
            el = time.time() - t0
            rate = el / max(1, (counts["ok"]))
            print(f"  [{i}/{n}] ok={counts['ok']} cached={counts['cached']} "
                  f"empty={counts['empty']} fail={counts['fail']} "
                  f"elapsed={el:.0f}s (~{rate:.2f}s/new game)", flush=True)
    print(f"DONE: {counts} in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
