"""Sealed-season spike addendum (Ruling 2c, 2026-07-17).

Before Phase 2 trusts stint features on fitengine's F5-sealed seasons
(2021-22 onward, yy21..yy25), extend the spike mechanically: 20 games per
sealed season-case, same scorecard, load-bearing metrics only
(recon_rate_TRUE_0p5, quarantine_rate), same 0.995/0.005 thresholds and
amber process.

This is MECHANICAL reconstruction only (Ruling 2a/2c). It fits nothing.
It is bench/spike-class evidence, NOT a G-gate claim. Reuses reconcile_game
unmodified; no pinned-code edits, no cache writes.

Sealed season-cases (the reference-class cases living inside the seal):
  Scenario A: Harden-PHI 21-22, Mitchell-CLE 22-23, Lillard-MIL 23-24,
              Beal-PHX 23-24, Fox-SAS 24-25, Doncic-LAL 24-25,
              Murray-NOP 24-25
  Scenario C: Lakers post-Davis 24-25 (LAL yy24), Bucks post-Lopez 25-26
              (MIL yy25)
yy25 (2025-26) is the mixed cdn/stats_api season and LaMelo's season, so
verifying it is doubly valuable.
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(r"C:\Users\bobby\playground\wolves-front-office")
FITENGINE = REPO / "counterfactual-fit-engine"
OUT = REPO / "all-for-one" / "tripwire-backtest" / "data" / "sealed_addendum_scorecard.parquet"
RNG_SEED = 20260717
N_PER_CASE = 20
WORKERS = 3

# (yy, team_abbr, case label)
CASES = [
    (21, "PHI", "Harden to PHI 2021-22 [A]"),
    (22, "CLE", "Mitchell to CLE 2022-23 [A]"),
    (23, "MIL", "Lillard to MIL 2023-24 [A]"),
    (23, "PHX", "Beal to PHX 2023-24 [A]"),
    (24, "SAS", "Fox to SAS 2024-25 [A]"),
    (24, "LAL", "Doncic to LAL / Lakers post-Davis 2024-25 [A/C]"),
    (24, "NOP", "Murray to NOP 2024-25 [A]"),
    (25, "MIL", "Bucks post-Lopez 2025-26 [C]"),
]


def _team_season_games(yy: int, abbr: str):
    sys.path.insert(0, str(REPO / "postmortem"))
    from lib.db import query
    sid = f"2{2000 + yy}"
    return query(
        """
        SELECT DISTINCT game_id, game_date
        FROM nba.nba_games
        WHERE season_id::text = %s AND team_abbreviation = %s
        ORDER BY game_date, game_id
        """,
        (sid, abbr),
    )


def _work(gid: str) -> dict:
    sys.path.insert(0, str(FITENGINE))
    from src.stints.reconcile import reconcile_game
    return reconcile_game(gid)


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for yy, abbr, case in CASES:
        pool = _team_season_games(yy, abbr)
        n = min(N_PER_CASE, len(pool))
        pick = pool.iloc[rng.choice(len(pool), size=n, replace=False)]
        for gid in pick.game_id:
            rows.append({"game_id": gid, "yy": yy, "season": f"20{yy}-{yy+1}",
                         "case": case})
    meta = pd.DataFrame(rows).drop_duplicates("game_id")

    # SEAL FLOOR assertion: every game must be yy>=21 (sealed). This addendum
    # exists precisely to touch the seal mechanically; assert we ARE in it.
    assert (meta.yy >= 21).all(), "addendum should only sample sealed seasons"
    print(f"sealed addendum: {len(meta)} games, yy{meta.yy.min()}..yy{meta.yy.max()}, "
          f"{WORKERS} workers", flush=True)

    t0 = time.time()
    recs = []
    with Pool(WORKERS) as pool:
        for i, r in enumerate(pool.imap_unordered(_work, meta.game_id.tolist(), chunksize=8)):
            recs.append(r)
    sc = pd.DataFrame(recs).merge(meta, on="game_id", how="left", validate="one_to_one")
    sc["stratum"] = sc.pbp_format
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sc.to_parquet(OUT, index=False)
    print(f"wrote {OUT} ({time.time()-t0:.0f}s)\n", flush=True)

    def score(g):
        tot = g.n_player_games.sum()
        return pd.Series({
            "games": len(g), "player_games": int(tot),
            "quarantined": int(g.quarantined.sum()),
            "quarantine_rate": g.quarantined.mean(),
            "recon_rate_TRUE_0p5": g.n_within_half_true.sum() / tot if tot else np.nan,
        })

    pd.set_option("display.width", 200)
    for label, keys in [("BY SEASON", ["season"]),
                        ("BY PBP FORMAT", ["stratum"]),
                        ("BY CASE", ["case"])]:
        print("=" * 78); print(label); print("=" * 78)
        print(sc.groupby(keys).apply(score, include_groups=False).to_string()); print()
    print("=" * 78); print("POOLED"); print("=" * 78)
    print(score(sc).to_string())

    # amber classification per season
    print("\n" + "=" * 78); print("VERDICT (0.995/0.005, amber 0.95-0.995)"); print("=" * 78)
    for seas, g in sc.groupby("season"):
        tot = g.n_player_games.sum()
        rec = g.n_within_half_true.sum() / tot
        qr = g.quarantined.mean()
        v = ("GREEN" if rec >= 0.995 and qr <= 0.005
             else "AMBER" if rec >= 0.95 else "RED")
        print(f"  {seas}: recon={rec:.4f} quar={qr:.4f} -> {v}")
    if sc.quarantined.any():
        print("\nQUARANTINES:")
        print(sc[sc.quarantined][["game_id", "season", "case", "error"]].to_string(index=False))


if __name__ == "__main__":
    main()
