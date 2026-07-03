"""F1 full-panel build: per-game stint parquet cache + the G1
reconciliation scorecard, over every include_train game (15,669 under the
R1 include-list). This is the ONLY run G1 claims may come from (directive
2026-07-02 item 1; bench runs are for repair iteration per rider 3).

Multiprocess (Windows spawn-safe): each worker owns its Postgres
connection through the AM-1 fence. Checkpoints every CHECKPOINT games so a
killed run resumes without recompute; per-game stint parquets land in
data/cache/stints/ as the rebuild seam (plan D6).

Usage: python -m src.stints.run_panel [tag] [workers]
       defaults: tag=panel_full workers=6
"""

from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))

STINTS_DIR = FITENGINE_ROOT / "data" / "cache" / "stints"
POSS_DIR = FITENGINE_ROOT / "data" / "cache" / "possessions"
CHECKPOINT = 500


def _work(game_id: str) -> dict:
    # import inside the worker so spawn gets a clean module + connection
    from src.stints.reconcile import reconcile_game
    try:
        return reconcile_game(game_id, stints_dir=str(STINTS_DIR),
                              poss_dir=str(POSS_DIR))
    except Exception as e:  # reconcile_game quarantines internally; this is
        # the belt-and-braces for worker-level failures (db drop etc.)
        return {"game_id": game_id, "quarantined": True, "pbp_format": "unknown",
                "n_player_games": 0, "n_within_half_true": 0, "n_within_tol": 0,
                "worst_delta_true": float("nan"), "team_seconds_exact": False,
                "poss_stints": 0.0, "poss_parser": 0.0,
                "n_validation_errors": -1, "error": f"WORKER {type(e).__name__}: {e}"}


def main() -> None:
    from src.stints.reconcile import summarize

    tag = sys.argv[1] if len(sys.argv) > 1 else "panel_full"
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    out_path = FITENGINE_ROOT / "outputs" / f"reconciliation_{tag}.parquet"
    STINTS_DIR.mkdir(parents=True, exist_ok=True)
    POSS_DIR.mkdir(parents=True, exist_ok=True)

    uni = pd.read_parquet(FITENGINE_ROOT / "data" / "staged" / "game_universe.parquet")
    gids = sorted(uni[uni.include_train].game_id)

    done: list[pd.DataFrame] = []
    if out_path.exists():  # resume
        prior = pd.read_parquet(out_path)
        prior = prior[prior.game_id.isin(set(gids))]
        done.append(prior)
        already = set(prior.game_id)
        gids = [g for g in gids if g not in already]
        print(f"resuming: {len(already)} done, {len(gids)} remaining", flush=True)

    print(f"panel build [{tag}]: {len(gids)} games, {workers} workers", flush=True)
    recs: list[dict] = []

    def _flush() -> None:
        nonlocal recs, done
        if recs:
            done.append(pd.DataFrame(recs))
            recs = []
        sc = pd.concat(done, ignore_index=True)
        sc["stratum"] = sc.pbp_format
        sc.to_parquet(out_path, index=False)
        done = [sc]

    with Pool(workers) as pool:
        for i, rec in enumerate(pool.imap_unordered(_work, gids, chunksize=8), 1):
            recs.append(rec)
            if i % CHECKPOINT == 0:
                _flush()
                print(f"  {i}/{len(gids)}", flush=True)
    _flush()

    sc = done[0]
    print(f"\npanel complete: {len(sc)} games", flush=True)
    print(summarize(sc).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
