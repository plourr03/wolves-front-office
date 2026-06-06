"""RAPM (Regularized Adjusted Plus/Minus) build for Wolves rotation players.

Approach:
1. Re-process each Wolves game across 2023-24, 2024-25, 2025-26 to get
   per-possession data with offensive_floor and defensive_floor.
2. Build a sparse design matrix:
   - One row per possession
   - 2 columns per player: an offensive indicator and a defensive indicator
   - Outcome: points scored by the offensive team * 100 (per-100-possession scale)
3. Fit ridge regression. The coefficient for player P's offensive column
   represents their estimated per-100 boost to team offensive rating when on
   the floor. Similarly for defensive column.
4. Net RAPM = off coef - def coef. Positive = good.

Scope caveat: this build uses only Wolves games (the team and their
opponents). Wolves rotation players have full 3-season coverage. Opponent
players have 2-4 games per season, which gives noisy but directionally
useful estimates for benchmark validation (Jokic, SGA, Brunson, etc.).

A full league-wide RAPM would require processing all 30 teams' games and
takes substantially more compute. The Wolves-focused version is sufficient
for Q8's purpose (estimating each Wolves rotation player's RAPM with
benchmark sanity checks).

Outputs:
- outputs/tables/q2_localize/rapm_player_impacts.csv  full coefficient table
- outputs/tables/q2_localize/rapm_wolves_rotation.csv Wolves-specific
- outputs/findings/q2_localize/04_rapm_findings.md   findings markdown
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from analyses.q2_localize import config, batch
from lib import db, lineups


CACHE_POSS_DIR = config.CACHE_DIR / "possessions"
CACHE_POSS_DIR.mkdir(parents=True, exist_ok=True)


def get_all_wolves_game_ids(seasons=(2023, 2024, 2025)) -> list[str]:
    """All Wolves game_ids across the specified seasons (RS + PO)."""
    gids = []
    for y in seasons:
        for st in ("Regular Season", "Playoffs"):
            ids = batch.fetch_game_ids(y, st, team_id=config.WOLVES_TEAM_ID)
            gids.extend(ids)
    return sorted(set(gids))


def process_game_to_possessions(game_id: str) -> pd.DataFrame | None:
    """Re-process one game and extract possession-level data.

    Returns a DataFrame with columns:
      game_id, possession_number, period, offensive_team_id, defensive_team_id,
      points_scored, end_reason, off_players (list of 5 player_ids),
      def_players (list of 5 player_ids).
    """
    out_path = CACHE_POSS_DIR / f"{game_id}.parquet"
    if out_path.exists():
        try:
            return pd.read_parquet(out_path)
        except Exception:
            pass

    try:
        result = lineups.process_game(game_id)
        poss = result["possessions"]
        if poss.empty:
            return None
        poss = poss.copy()
        poss["game_id"] = game_id
        # Convert frozensets to sorted comma-separated strings (parquet-friendly).
        poss["off_players_str"] = poss["offensive_floor"].apply(
            lambda fs: ",".join(str(p) for p in sorted(fs)) if fs else "")
        poss["def_players_str"] = poss["defensive_floor"].apply(
            lambda fs: ",".join(str(p) for p in sorted(fs)) if fs else "")
        keep_cols = ["game_id", "possession_number", "period",
                     "offensive_team_id", "defensive_team_id",
                     "points_scored", "end_reason",
                     "off_players_str", "def_players_str"]
        poss = poss[keep_cols]
        poss.to_parquet(out_path, index=False)
        return poss
    except Exception as e:
        print(f"  {game_id}: EXCEPTION {type(e).__name__}: {e}")
        return None


def build_possession_dataset(seasons=(2023, 2024, 2025)) -> pd.DataFrame:
    """Re-process all Wolves games and return concatenated possession data."""
    gids = get_all_wolves_game_ids(seasons=seasons)
    print(f"Processing {len(gids)} Wolves games for possessions (seasons {seasons})...")
    t0 = time.time()
    parts = []
    for i, gid in enumerate(gids, 1):
        df = process_game_to_possessions(gid)
        if df is not None:
            parts.append(df)
        if i % 25 == 0 or i == len(gids):
            print(f"  [{i}/{len(gids)}] elapsed={time.time()-t0:.1f}s")
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# RAPM model
# ---------------------------------------------------------------------------


def build_rapm_matrices(possessions: pd.DataFrame, min_possessions_per_player: int = 50):
    """Build (X_off, X_def, y, player_ids) for the RAPM fit.

    X_off: sparse matrix (n_poss x n_players) with +1 if player on offense
    X_def: sparse matrix (n_poss x n_players) with +1 if player on defense
    y: vector of points scored on the possession (will be scaled by 100)
    player_ids: list of player_ids matching column order

    Players with fewer than min_possessions_per_player total possessions
    (off + def) are pooled into a "replacement" feature instead of having
    their own column. This keeps the matrix tractable.
    """
    from scipy.sparse import lil_matrix, csr_matrix

    print(f"Building RAPM matrices from {len(possessions)} possessions...")

    # Count appearances per player across all possessions.
    player_counts: dict[int, int] = {}
    for _, row in possessions.iterrows():
        for p in row["off_players_str"].split(","):
            if p:
                pid = int(p)
                player_counts[pid] = player_counts.get(pid, 0) + 1
        for p in row["def_players_str"].split(","):
            if p:
                pid = int(p)
                player_counts[pid] = player_counts.get(pid, 0) + 1

    # Players with enough data to get their own coefficient.
    qualifying_players = sorted(p for p, c in player_counts.items() if c >= min_possessions_per_player)
    player_to_idx = {p: i for i, p in enumerate(qualifying_players)}
    n_players = len(qualifying_players)
    print(f"  Qualifying players (>= {min_possessions_per_player} possessions): {n_players}")
    print(f"  Pooled below-threshold players: {len(player_counts) - n_players}")

    n_poss = len(possessions)
    # Sparse construction.
    X_off = lil_matrix((n_poss, n_players + 1), dtype=np.float32)  # +1 for "replacement" column
    X_def = lil_matrix((n_poss, n_players + 1), dtype=np.float32)
    y = np.zeros(n_poss, dtype=np.float32)

    for i, row in enumerate(possessions.itertuples()):
        for p in row.off_players_str.split(","):
            if not p:
                continue
            pid = int(p)
            idx = player_to_idx.get(pid, n_players)  # n_players = replacement bucket
            X_off[i, idx] = 1.0
        for p in row.def_players_str.split(","):
            if not p:
                continue
            pid = int(p)
            idx = player_to_idx.get(pid, n_players)
            X_def[i, idx] = 1.0
        y[i] = float(row.points_scored)

    return X_off.tocsr(), X_def.tocsr(), y, qualifying_players


def fit_rapm(X_off, X_def, y, alpha: float = 2000.0):
    """Fit ridge regression. Returns (off_coefs, def_coefs, intercept)."""
    from sklearn.linear_model import Ridge
    from scipy.sparse import hstack

    # Concatenate off and def features.
    X = hstack([X_off, X_def]).tocsr()
    # Scale y to per-100-possession.
    y_scaled = y * 100.0
    print(f"Fitting ridge regression: X shape {X.shape}, alpha={alpha}")
    model = Ridge(alpha=alpha, fit_intercept=True, solver="auto")
    model.fit(X, y_scaled)
    n_off = X_off.shape[1]
    off_coefs = model.coef_[:n_off]
    def_coefs = model.coef_[n_off:]
    return off_coefs, def_coefs, model.intercept_


def extract_player_impacts(off_coefs, def_coefs, intercept, qualifying_players):
    """Convert raw coefficients to interpretable RAPM impacts.

    Off coef = per-100 expected boost to offensive points when player on floor.
    Def coef = per-100 expected boost to opp offensive points when player on
    floor (so HIGHER def coef = WORSE defender).

    Net RAPM = off_coef - def_coef. Positive = good (more impact when on floor).
    """
    rows = []
    for pid, off_c, def_c in zip(qualifying_players, off_coefs, def_coefs):
        rows.append({
            "player_id": pid,
            "off_rapm": float(off_c),
            "def_rapm": float(def_c),
            "net_rapm": float(off_c - def_c),
        })
    df = pd.DataFrame(rows)
    df["intercept"] = float(intercept)
    return df


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run(alpha: float = 2000.0, min_poss: int = 50):
    print("=== RAPM build for Wolves rotation players ===\n")

    # Step 1: Build possession dataset across 3 seasons.
    possessions = build_possession_dataset(seasons=(2023, 2024, 2025))
    print(f"\nTotal possessions: {len(possessions)}")
    print(f"Unique games: {possessions['game_id'].nunique()}")

    # Step 2: Build sparse matrices.
    X_off, X_def, y, qualifying = build_rapm_matrices(possessions, min_possessions_per_player=min_poss)

    # Step 3: Fit ridge.
    off_coefs, def_coefs, intercept = fit_rapm(X_off, X_def, y, alpha=alpha)

    # Step 4: Extract impacts.
    impacts = extract_player_impacts(off_coefs, def_coefs, intercept, qualifying)

    # Attach names.
    pids = impacts["player_id"].astype(int).tolist()
    placeholders = ",".join(["%s"] * len(pids))
    names = db.query(
        f"""SELECT DISTINCT ON (player_id) player_id, player_name
            FROM nba_player_stats
            WHERE player_id IN ({placeholders})
            ORDER BY player_id, game_date DESC""",
        tuple(pids),
    )
    name_map = dict(zip(names["player_id"], names["player_name"]))
    impacts["player_name"] = impacts["player_id"].map(name_map)

    # Sort by net RAPM desc.
    impacts = impacts.sort_values("net_rapm", ascending=False).reset_index(drop=True)

    # Write full table.
    impacts.to_csv(config.TABLE_DIR / "rapm_player_impacts.csv", index=False)
    print(f"\nFull RAPM table written ({len(impacts)} players).")

    # Wolves rotation subset.
    wolves_pids = (config.CORE_ROTATION + config.WING_OR_GUARD_DEPTH + config.BIGS)
    wolves_pids = list(set(wolves_pids))
    wolves_subset = impacts[impacts["player_id"].isin(wolves_pids)].copy()
    wolves_subset = wolves_subset.sort_values("net_rapm", ascending=False)
    print("\n=== Wolves rotation RAPM ===")
    print(wolves_subset[["player_name", "off_rapm", "def_rapm", "net_rapm"]].round(2).to_string(index=False))
    wolves_subset.to_csv(config.TABLE_DIR / "rapm_wolves_rotation.csv", index=False)

    # Benchmark check: top and bottom 15 net RAPM.
    print("\n=== Top 15 net RAPM (sanity check) ===")
    top15 = impacts.head(15)
    print(top15[["player_name", "off_rapm", "def_rapm", "net_rapm"]].round(2).to_string(index=False))

    print("\n=== Bottom 15 net RAPM ===")
    bot15 = impacts.tail(15)
    print(bot15[["player_name", "off_rapm", "def_rapm", "net_rapm"]].round(2).to_string(index=False))

    return impacts


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--alpha", type=float, default=2000.0)
    ap.add_argument("--min-poss", type=int, default=50)
    args = ap.parse_args()
    run(alpha=args.alpha, min_poss=args.min_poss)
