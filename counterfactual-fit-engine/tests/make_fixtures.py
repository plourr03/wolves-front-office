"""One-time fixture builder: cache raw PBP + golden possession outputs for
10 games spanning both formats and the season range. Fixtures pin the
adapter surface (AM-1's second layer): if the pinned lib's BEHAVIOR ever
changes (hash re-pin after a memo), goldens quantify the drift.

Games chosen mechanically: first 002 game of each of 5 legacy seasons
(2013, 2016, 2019, 2022, 2024 start-years) + 5 games spread across 2025-26
(the Live-format season -- AM-4's headline-vector era gets extra weight).
"""

from __future__ import annotations

import sys
from pathlib import Path

FITENGINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.adapters.postmortem_lib import normalize_pbp, query, reconstruct_possessions

FIXDIR = FITENGINE_ROOT / "tests" / "fixtures"


def pick_games() -> list[str]:
    games = query("""
        SELECT DISTINCT game_id FROM nba_play_by_play
        WHERE substr(game_id, 1, 3) = '002' ORDER BY game_id
    """).game_id
    out = []
    for yy in ("13", "16", "19", "22", "24"):
        season = games[games.str[3:5] == yy]
        out.append(season.iloc[0])
    live = games[games.str[3:5] == "25"]
    step = max(len(live) // 5, 1)
    out.extend(live.iloc[::step].head(5).tolist())
    return out


def main():
    FIXDIR.mkdir(parents=True, exist_ok=True)
    for gid in pick_games():
        raw = query("SELECT * FROM nba_play_by_play WHERE game_id = %s "
                    "ORDER BY action_number", (gid,))
        raw.to_parquet(FIXDIR / f"pbp_{gid}.parquet", index=False)
        norm = normalize_pbp(raw)
        _, poss = reconstruct_possessions(norm)
        poss.to_parquet(FIXDIR / f"golden_poss_{gid}.parquet", index=False)
        print(f"{gid}: {len(raw)} events -> {len(poss)} possessions")


if __name__ == "__main__":
    main()
