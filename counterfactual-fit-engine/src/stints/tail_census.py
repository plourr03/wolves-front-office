"""F1 tail census: diagnose every non-quarantined panel game that misses
perfect reconciliation and bucket the residual causes deterministically
from the diagnostic's fields. The G1 gate already passes; this
characterizes the tail that feeds RAPM so F2 knows its input and any
SYSTEMATIC (fixable) residual is separated from diffuse data-floor noise.

Buckets (checked in order):
  reference_incomplete   official minutes_float undercount (warehouse
                         ingest gap; recon uniformly exceeds official with
                         team-seconds exact). NOT a reconstruction error.
  phantom_period_only    a stray period marker with no real playing time;
                         per-player reconciliation otherwise perfect.
  floor_count_error      a period whose reconstructed player-seconds are
                         not 5*length -> a genuine floor-COUNT bug in that
                         period (fixable, structural).
  attribution_residual   team-seconds exact, counts right, but floor
                         MEMBERSHIP wrong within periods (a player swapped
                         for another) -> the diffuse residual.

Usage: python -m src.stints.tail_census [recon_fraction_threshold]
       default threshold 0.999 (any game not essentially perfect).
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.stints.diagnose import diagnose  # noqa: E402

PANEL = FITENGINE_ROOT / "outputs" / "reconciliation_panel_full.parquet"
OUT = FITENGINE_ROOT / "outputs" / "tail_census.json"


def classify(d: dict) -> str:
    if d.get("quarantined"):
        return "quarantined"
    if d["n_failing"] == 0:
        return "clean_or_phantom"
    if d.get("reference_incomplete") and d["error_direction"] == "uniform_over":
        return "reference_incomplete"
    if d.get("bad_periods"):
        return "floor_count_error"
    return "attribution_residual"


def main() -> None:
    thr = float(sys.argv[1]) if len(sys.argv) > 1 else 0.999
    sc = pd.read_parquet(PANEL)
    d = sc[~sc.quarantined].copy()
    d["frac"] = d.n_within_half_true / d.n_player_games.clip(lower=1)
    tail = d[(d.frac < thr) | (~d.team_seconds_exact)]
    gids = sorted(tail.game_id)
    print(f"diagnosing {len(gids)} tail games (recon frac < {thr} or "
          f"team-seconds flagged)...", flush=True)

    records = []
    buckets: Counter = Counter()
    by_bucket_games: dict = defaultdict(list)
    fail_mass: Counter = Counter()
    for i, g in enumerate(gids, 1):
        dg = diagnose(g)
        b = classify(dg)
        buckets[b] += 1
        by_bucket_games[b].append(g)
        fail_mass[b] += dg.get("n_failing", 0)
        records.append({"game_id": g, "bucket": b, **{
            k: dg.get(k) for k in ("n_failing", "n_player_games", "worst_delta",
                                   "error_direction", "reference_incomplete",
                                   "bad_periods", "phantom_periods",
                                   "starter_mismatch")}})
        if i % 20 == 0:
            print(f"  {i}/{len(gids)}", flush=True)

    OUT.write_text(json.dumps({"threshold": thr, "n_tail": len(gids),
                               "buckets": dict(buckets),
                               "fail_mass": dict(fail_mass),
                               "records": records}, indent=1))
    print("\n=== TAIL CENSUS ===")
    total_fail = int(sc[~sc.quarantined].eval(
        "n_player_games - n_within_half_true").sum())
    for b, n in buckets.most_common():
        print(f"  {b:22} {n:4} games, {fail_mass[b]:5} failing player-games "
              f"({fail_mass[b] / total_fail:.1%} of all tail failures)")
    print(f"  total failing player-games across panel: {total_fail}")
    print(f"\nwrote {OUT}")
    # sample game ids per bucket for spot-checks
    for b, gs in by_bucket_games.items():
        print(f"  {b}: {gs[:6]}{'...' if len(gs) > 6 else ''}")


if __name__ == "__main__":
    main()
