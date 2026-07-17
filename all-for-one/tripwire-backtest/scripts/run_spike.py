"""Run the stint trust spike (tripwire backtest, Phase 0 Step 2).

Scores fitengine's stint reconstruction over the sampled game list from
build_spike_sample.py, and reports recon_rate_TRUE_0p5 / quarantine_rate
broken out by season and by spike stratum.

WHAT THIS IS: bench-class feasibility evidence. fitengine's house rule is
that gate claims come ONLY from the full 15,669-game panel, never from a
sample (PICKUP.md rider 3). This spike therefore CANNOT and DOES NOT issue
a G-gate verdict. It answers one question: how far back is stint grain
trustworthy enough to compute descriptive features on.

WHAT IS LOAD-BEARING: recon_rate_TRUE_0p5 and quarantine_rate, only.
team_seconds_exact and poss_parity are STRUCTURAL INVARIANTS, ruled
tautological by decisions.md (2026-07-02 directive item 1). They are
carried in the scorecard for comparability with the G1 panel and are NOT
quoted as evidence.

Reuses reconcile_game unmodified. Touches no pinned code. Writes no stint
cache. Parallel driver mirrors run_panel.py, whose own game list is
hardcoded to game_universe.parquet (which starts at yy13 and so cannot
reach this spike's frontier seasons).
"""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
SCRATCH = Path(
    r"C:\Users\bobby\AppData\Local\Temp\claude"
    r"\C--Users-bobby-playground-wolves-front-office"
    r"\ab0e38ad-9447-4c97-ab02-9edacecd90a8\scratchpad"
)
SAMPLE = SCRATCH / "spike_sample.json"
OUT = REPO / "all-for-one" / "tripwire-backtest" / "data" / "spike_scorecard.parquet"

WORKERS = 6


def _work(gid: str) -> dict:
    # imports inside the worker: Windows spawn safety, per run_panel.py
    sys.path.insert(0, str(REPO / "counterfactual-fit-engine"))
    from src.stints.reconcile import reconcile_game
    return reconcile_game(gid)


def main() -> None:
    meta = pd.DataFrame(json.loads(SAMPLE.read_text())["games"])
    gids = meta.game_id.tolist()
    print(f"spike: {len(gids)} games, {WORKERS} workers", flush=True)

    t0 = time.time()
    recs = []
    with Pool(WORKERS) as pool:
        for i, r in enumerate(pool.imap_unordered(_work, gids, chunksize=8)):
            recs.append(r)
            if (i + 1) % 50 == 0:
                el = time.time() - t0
                rate = (i + 1) / el
                print(f"  {i + 1}/{len(gids)}  {el:.0f}s elapsed, "
                      f"{(len(gids) - i - 1) / rate:.0f}s left", flush=True)

    sc = pd.DataFrame(recs)
    sc["stratum"] = sc.pbp_format  # per-game detection, never season prefix
    sc = sc.merge(meta, on="game_id", how="left", validate="one_to_one")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    sc.to_parquet(OUT, index=False)
    print(f"\nwrote {OUT}  ({time.time() - t0:.0f}s total)", flush=True)

    def score(g: pd.DataFrame) -> pd.Series:
        tot = g.n_player_games.sum()
        return pd.Series({
            "games": len(g),
            "player_games": int(tot),
            "quarantined": int(g.quarantined.sum()),
            "quarantine_rate": g.quarantined.mean(),
            "recon_rate_TRUE_0p5": g.n_within_half_true.sum() / tot if tot else float("nan"),
            "recon_rate_relaxed": g.n_within_tol.sum() / tot if tot else float("nan"),
            "median_worst_delta_true": g.worst_delta_true.median(),
        })

    pd.set_option("display.width", 200)
    for label, keys in [("BY SEASON", ["season"]),
                        ("BY SPIKE STRATUM", ["spike_stratum"]),
                        ("BY PBP FORMAT (AM-4)", ["stratum"]),
                        ("BY TARGETED CASE", ["case"])]:
        print("\n" + "=" * 78)
        print(label)
        print("=" * 78)
        if keys == ["case"]:
            sub = sc[sc.case.fillna("") != ""]
            if not len(sub):
                print("  (none)")
                continue
            print(sub.groupby(keys).apply(score, include_groups=False).to_string())
        else:
            print(sc.groupby(keys).apply(score, include_groups=False).to_string())

    print("\n" + "=" * 78)
    print("POOLED")
    print("=" * 78)
    print(score(sc).to_string())

    if sc.quarantined.any():
        print("\n" + "=" * 78)
        print("QUARANTINES (the whole mechanism: rows with quarantined=True)")
        print("=" * 78)
        print(sc[sc.quarantined][["game_id", "season", "spike_stratum", "error"]].to_string(index=False))


if __name__ == "__main__":
    main()
