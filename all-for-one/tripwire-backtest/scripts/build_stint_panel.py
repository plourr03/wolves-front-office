"""Build the stint panel for tripwire Phase 1 reliability + Phase 2 features.

Per RS game 2014-15 through 2024-25, reconstruct stints (fitengine's forked
builder, unmodified) and write one parquet per game to data/stints_panel/.
Resumable: skips games already written. Parallel.

This is DESCRIPTIVE stint aggregation (RULING 2a: in scope for sealed seasons
too). It fits nothing. It reuses floor_state.process_game + derive_stints
exactly as reconcile.py does internally; no pinned-code edits.

Failures are logged to data/stints_panel/_failures.csv, never silently
dropped (the bare-except path in process_games_to_stints is avoided by
calling the two functions directly and catching per game).
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
FITENGINE = REPO / "counterfactual-fit-engine"
OUTDIR = REPO / "all-for-one" / "tripwire-backtest" / "data" / "stints_panel"
WORKERS = 6

# 2014-15 .. 2024-25 regular season. season_id = '2' || (2000+yy).
SEASONS = list(range(14, 25))  # yy14..yy24 inclusive


def _game_ids() -> list[str]:
    sys.path.insert(0, str(REPO / "postmortem"))
    from lib.db import query
    sids = [f"2{2000 + yy}" for yy in SEASONS]
    rows = query(
        """
        SELECT DISTINCT game_id
        FROM nba.nba_games
        WHERE season_id::text = ANY(%s)
        ORDER BY game_id
        """,
        (sids,),
    )
    return rows.game_id.tolist()


def _work(gid: str) -> tuple[str, str]:
    sys.path.insert(0, str(FITENGINE))
    out = OUTDIR / f"{gid}.parquet"
    if out.exists():
        return (gid, "skip")
    try:
        from src.stints import floor_state, stint_builder
        r = floor_state.process_game(gid)
        st = stint_builder.derive_stints(r["annotated"], r["possessions"])
        if "game_id" not in st.columns:
            st["game_id"] = gid
        st["pbp_format"] = r["pbp_format"]
        st.to_parquet(out, index=False)
        return (gid, "ok")
    except Exception as e:  # quarantine-honest: log, never guess
        return (gid, f"FAIL {type(e).__name__}: {str(e).splitlines()[0][:200]}")


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    gids = _game_ids()
    print(f"panel: {len(gids)} games over seasons yy{SEASONS[0]}..yy{SEASONS[-1]}, "
          f"{WORKERS} workers", flush=True)

    t0 = time.time()
    results = []
    with Pool(WORKERS) as pool:
        for i, res in enumerate(pool.imap_unordered(_work, gids, chunksize=16)):
            results.append(res)
            if (i + 1) % 250 == 0:
                el = time.time() - t0
                rate = (i + 1) / el
                print(f"  {i + 1}/{len(gids)}  {el:.0f}s, "
                      f"{(len(gids) - i - 1) / rate:.0f}s left", flush=True)

    res = pd.DataFrame(results, columns=["game_id", "status"])
    ok = (res.status == "ok").sum()
    skip = (res.status == "skip").sum()
    fails = res[~res.status.isin(["ok", "skip"])]
    print(f"\ndone in {time.time() - t0:.0f}s: {ok} built, {skip} skipped, "
          f"{len(fails)} failed", flush=True)
    if len(fails):
        fails.to_csv(OUTDIR / "_failures.csv", index=False)
        print(fails.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
