"""Possession cache for RAPM (F2 foundation).

RAPM needs 10-player-fixed matchup rows (offense five vs defense five with
points and possession counts). The stint cache is the WRONG grain for that:
stints are per-team (one team's five fixed, bounded by that team's own
subs), so the two teams' stint boundaries do not align and cannot be
joined into matchup rows. The possession grain is correct -- derive_
possessions already emits offensive_floor and defensive_floor (5-player
frozensets) with points per possession -- but the panel build persisted
only the stint aggregation. This one extra process_game pass persists the
possessions.

Per possession we persist: game_id, season_yy, period, off5/def5 (sorted
comma-joined ids), points, and a garbage flag computed with the SAME rule
the stint builder uses (last 3 minutes of Q4/OT, margin >= 15 at the
possession's start clock). RAPM filters garbage; the flag is carried, not
baked, matching how stints carry in_garbage_time.

Resumable + multiprocess, same pattern as run_panel. Quarantined games
(the 1 unresolvable-sub game) simply produce no possessions.

Usage: python -m src.models.build_possessions [workers]
"""

from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))

POSS_DIR = FITENGINE_ROOT / "data" / "cache" / "possessions"
GARBAGE_MARGIN = 15
GARBAGE_LAST_SEC = 3 * 60
DONE_MARKER = FITENGINE_ROOT / "outputs" / "possessions_build_done.txt"


def possessions_for_game(res: dict, game_id: str,
                         season_yy: str) -> "pd.DataFrame":
    """Build the possession rows (paired 10-player floors + garbage flag)
    from a process_game result. Shared by this standalone builder and by
    reconcile.reconcile_game so ONE panel pass can persist stints, the
    scorecard, and the possession cache together (no second process_game
    pass over the warehouse)."""
    poss = res["possessions"]
    if poss.empty:
        return pd.DataFrame(columns=["game_id", "season_yy", "period",
                                     "off_lineup", "def_lineup", "points",
                                     "garbage"])
    a2clock = res["annotated"].set_index(
        "action_number")["clock_seconds_remaining"].to_dict()
    rows = []
    score = {int(poss.iloc[0].offensive_team_id): 0,
             int(poss.iloc[0].defensive_team_id): 0}
    for p in poss.itertuples():
        off_t, def_t = int(p.offensive_team_id), int(p.defensive_team_id)
        margin = abs(score.get(off_t, 0) - score.get(def_t, 0))
        clock = a2clock.get(p.start_action_number)
        per = int(p.period)
        garbage = bool(
            per >= 4 and clock is not None and pd.notna(clock)
            and float(clock) <= GARBAGE_LAST_SEC and margin >= GARBAGE_MARGIN)
        rows.append({
            "game_id": game_id, "season_yy": season_yy, "period": per,
            "off_lineup": ",".join(str(x) for x in sorted(p.offensive_floor)),
            "def_lineup": ",".join(str(x) for x in sorted(p.defensive_floor)),
            "points": int(p.points_scored), "garbage": garbage,
        })
        score[off_t] = score.get(off_t, 0) + int(p.points_scored)
    return pd.DataFrame(rows)


def _work(row: tuple[str, str]) -> tuple[str, int]:
    game_id, season_yy = row
    out_path = POSS_DIR / f"{game_id}.parquet"
    if out_path.exists():
        return (game_id, -1)  # already done
    from src.stints import floor_state
    try:
        res = floor_state.process_game(game_id)
    except Exception:
        return (game_id, 0)  # quarantined; no possessions
    df = possessions_for_game(res, game_id, season_yy)
    if df.empty:
        return (game_id, 0)
    df.to_parquet(out_path, index=False)
    return (game_id, len(df))


def main() -> None:
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    POSS_DIR.mkdir(parents=True, exist_ok=True)
    uni = pd.read_parquet(FITENGINE_ROOT / "data" / "staged" / "game_universe.parquet")
    todo = [(g, yy) for g, yy in
            uni[uni.include_train][["game_id", "season_yy"]].itertuples(index=False)]
    print(f"possession build: {len(todo)} train games, {workers} workers",
          flush=True)
    n_done = n_poss = n_skip = n_quar = 0
    with Pool(workers) as pool:
        for i, (gid, n) in enumerate(pool.imap_unordered(_work, todo, chunksize=8), 1):
            if n == -1:
                n_skip += 1
            elif n == 0:
                n_quar += 1
            else:
                n_done += 1
                n_poss += n
            if i % 1000 == 0:
                print(f"  {i}/{len(todo)}  (built {n_done}, skip {n_skip}, "
                      f"empty/quar {n_quar})", flush=True)
    msg = (f"possession build complete: {n_done} built, {n_skip} pre-existing, "
           f"{n_quar} empty/quarantined, {n_poss:,} possessions written")
    print(msg, flush=True)
    DONE_MARKER.write_text(msg)


if __name__ == "__main__":
    main()
