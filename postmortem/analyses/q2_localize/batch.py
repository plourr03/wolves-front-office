"""Batch processing for Q2: run the lineup pipeline + aggregation on game
lists and cache the per-game stint records as parquet.

The batches are:

1. League batch: all 2025-26 playoff games (68 games, all 16 playoff teams).
   Used for league-relative lineup baselines.

2. Wolves 2024-25 batch: 82 RS + 15 PO Wolves games (97 total). Used for the
   2024-25 vs 2025-26 lineup comparison.

3. Wolves 2025-26 batch: already processed earlier; this module also caches
   the 12 PO games + 82 RS games for the year-over-year work.

Each game's stint records are written to parquet, keyed by game_id, so the
batch is restartable and incremental.

Caveats inherited from `lib/lineup_aggregation.py`:
- AND-1 attribution noise (~5 ppp at the lineup-rating level, mirrored).
- ~98% possession coverage vs advanced stats (heaves and edge cases).

Per-game processing is currently sequential (psycopg2 single connection per
game). The bottleneck is PBP fetching + Python row iteration, not Postgres.
For 68 league games we expect ~30 minutes; for 97 Wolves games ~45 minutes.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Iterable

import pandas as pd

from lib import db, lineups, lineup_aggregation as agg
from analyses.q2_localize import config


def fetch_game_ids(season_year: int, season_type: str,
                    team_id: int | None = None) -> list[str]:
    """Pull game_ids for a (season_year, season_type), optionally filtered
    to one team. Returns sorted distinct list as strings.
    """
    where = ["season_type = %s", "(season_id %% 10000) = %s"]
    params = [season_type, season_year]
    if team_id is not None:
        where.append("team_id = %s")
        params.append(team_id)
    sql = f"""
        SELECT DISTINCT game_id
        FROM nba_games
        WHERE {' AND '.join(where)}
        ORDER BY game_id
    """
    df = db.query(sql, tuple(params))
    return df["game_id"].astype(str).tolist()


def process_one_game_to_parquet(game_id: str, cache_subdir: Path) -> Path | None:
    """Run the pipeline on one game, write stint records to a parquet file.
    Returns the parquet path if successful, None on error.
    """
    cache_subdir.mkdir(parents=True, exist_ok=True)
    out = cache_subdir / f"{game_id}.parquet"
    if out.exists():
        return out
    try:
        result = lineups.process_game(game_id)
        stints = agg.derive_stints(result["annotated"], result["possessions"])
        if stints.empty:
            return None
        # Ensure consistent dtypes so parquet roundtrip is stable.
        for c in ("team_id", "period_start", "period_end"):
            if c in stints.columns:
                stints[c] = pd.to_numeric(stints[c], errors="coerce").astype("Int64")
        stints.to_parquet(out, index=False)
        return out
    except Exception as e:
        print(f"  {game_id}: EXCEPTION {type(e).__name__}: {e}")
        return None


def batch_process(game_ids: Iterable[str], cache_subdir: Path, label: str) -> dict:
    """Process a list of games, write each to parquet under cache_subdir.
    Returns summary stats.
    """
    cache_subdir.mkdir(parents=True, exist_ok=True)
    game_ids = list(game_ids)
    n = len(game_ids)
    successes, skips, fails = 0, 0, 0
    t0 = time.time()
    print(f"[{label}] processing {n} games, cache_dir={cache_subdir}")
    for i, gid in enumerate(game_ids, 1):
        out = cache_subdir / f"{gid}.parquet"
        if out.exists():
            skips += 1
            if i % 25 == 0 or i == n:
                print(f"  [{i}/{n}] {gid} (cached); elapsed={time.time()-t0:.1f}s")
            continue
        try:
            result = lineups.process_game(gid)
            stints = agg.derive_stints(result["annotated"], result["possessions"])
            if stints.empty:
                fails += 1
                print(f"  {gid}: empty stints")
                continue
            for c in ("team_id", "period_start", "period_end"):
                if c in stints.columns:
                    stints[c] = pd.to_numeric(stints[c], errors="coerce").astype("Int64")
            stints.to_parquet(out, index=False)
            successes += 1
            if i % 5 == 0 or i == n:
                print(f"  [{i}/{n}] {gid} ok; elapsed={time.time()-t0:.1f}s")
        except Exception as e:
            fails += 1
            print(f"  {gid}: EXCEPTION {type(e).__name__}: {e}")
    elapsed = time.time() - t0
    print(f"[{label}] done: {successes} new, {skips} cached, {fails} failed. {elapsed:.1f}s")
    return {"label": label, "n": n, "successes": successes, "skips": skips,
            "fails": fails, "elapsed_sec": elapsed}


def load_cached_stints(cache_subdir: Path) -> pd.DataFrame:
    """Load all parquet stint files from cache_subdir."""
    files = sorted(cache_subdir.glob("*.parquet"))
    if not files:
        return pd.DataFrame()
    parts = []
    for f in files:
        try:
            parts.append(pd.read_parquet(f))
        except Exception as e:
            print(f"  failed to read {f}: {e}")
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", choices=["league_2025_po", "wolves_2023", "wolves_2024", "wolves_2025"],
                    help="Which batch to run.")
    ap.add_argument("--limit", type=int, default=None,
                    help="Process at most N games (for testing).")
    args = ap.parse_args()

    if args.batch == "league_2025_po":
        ids = fetch_game_ids(2025, "Playoffs")
        cache = config.CACHE_DIR / "league_2025_po_stints"
    elif args.batch == "wolves_2023":
        ids_rs = fetch_game_ids(2023, "Regular Season", team_id=config.WOLVES_TEAM_ID)
        ids_po = fetch_game_ids(2023, "Playoffs", team_id=config.WOLVES_TEAM_ID)
        ids = ids_rs + ids_po
        cache = config.CACHE_DIR / "wolves_2023_stints"
    elif args.batch == "wolves_2024":
        ids_rs = fetch_game_ids(2024, "Regular Season", team_id=config.WOLVES_TEAM_ID)
        ids_po = fetch_game_ids(2024, "Playoffs", team_id=config.WOLVES_TEAM_ID)
        ids = ids_rs + ids_po
        cache = config.CACHE_DIR / "wolves_2024_stints"
    elif args.batch == "wolves_2025":
        ids_rs = fetch_game_ids(2025, "Regular Season", team_id=config.WOLVES_TEAM_ID)
        ids_po = fetch_game_ids(2025, "Playoffs", team_id=config.WOLVES_TEAM_ID)
        ids = ids_rs + ids_po
        cache = config.CACHE_DIR / "wolves_2025_stints"
    else:
        raise SystemExit(1)

    if args.limit:
        ids = ids[: args.limit]
    summary = batch_process(ids, cache, args.batch)
    print("\nSummary:", summary)


if __name__ == "__main__":
    main()
