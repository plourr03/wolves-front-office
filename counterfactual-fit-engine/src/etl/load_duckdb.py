"""D6: load the F1 stint cache into DuckDB (the project's primary store).

Four tables, rebuilt wholesale from the cache each run (data/cache/stints/
is the rebuild seam; this loader is idempotent and cheap next to the panel
build that fills the cache):

  games            dim: one row per game universe entry, joined with the
                   panel scorecard's per-game format stratum + quarantine
                   flag for train-eligible games.
  stints           every per-team directional stint row from the cache,
                   with a per-game stint_seq. G1's lineup-validity gate is
                   asserted DURING load: every lineup_id must carry exactly
                   five person ids, else the load aborts (never silently).
  quarantine       scorecard rows of quarantined games with their legible
                   error reasons.
  reconciliation   the full G1 scorecard (one row per train-eligible game).

Usage: python -m src.etl.load_duckdb [scorecard_tag]
       default tag: panel_full; DB lands at data/fitengine.duckdb
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = FITENGINE_ROOT / "data" / "fitengine.duckdb"
STINTS_GLOB = str(FITENGINE_ROOT / "data" / "cache" / "stints" / "*.parquet")
UNIVERSE = str(FITENGINE_ROOT / "data" / "staged" / "game_universe.parquet")


def load(tag: str = "panel_full") -> dict:
    scorecard = str(FITENGINE_ROOT / "outputs" / f"reconciliation_{tag}.parquet")
    con = duckdb.connect(str(DB_PATH))
    try:
        con.execute(f"""
            CREATE OR REPLACE TABLE reconciliation AS
            SELECT * FROM read_parquet('{scorecard}')
        """)
        con.execute("""
            CREATE OR REPLACE TABLE quarantine AS
            SELECT game_id, pbp_format, n_player_games, error
            FROM reconciliation WHERE quarantined
        """)
        con.execute(f"""
            CREATE OR REPLACE TABLE games AS
            SELECT u.game_id, u.type_prefix, u.season_yy, u.label,
                   u.pbp_rows, u.include_train, u.include_flagged,
                   r.pbp_format, r.quarantined
            FROM read_parquet('{UNIVERSE}') u
            LEFT JOIN reconciliation r USING (game_id)
        """)
        con.execute(f"""
            CREATE OR REPLACE TABLE stints AS
            SELECT row_number() OVER (
                       PARTITION BY game_id
                       ORDER BY period_start, clock_start_sec DESC, team_id
                   ) AS stint_seq, *
            FROM read_parquet('{STINTS_GLOB}')
        """)

        # G1 lineup-validity gate, asserted at load: exactly five ids per
        # lineup, zero exceptions. Abort loudly, never load a bad row.
        bad = con.execute("""
            SELECT count(*) FROM stints
            WHERE len(string_split(lineup_id, ',')) != 5
        """).fetchone()[0]
        if bad:
            raise RuntimeError(
                f"lineup-validity violation: {bad} stint rows without "
                "exactly 5 player ids. Load aborted; nothing to quarantine "
                "here because the cache itself is wrong -- fix upstream.")

        stats = {
            "games": con.execute("SELECT count(*) FROM games").fetchone()[0],
            "train_games": con.execute(
                "SELECT count(*) FROM games WHERE include_train").fetchone()[0],
            "stint_games": con.execute(
                "SELECT count(DISTINCT game_id) FROM stints").fetchone()[0],
            "stints": con.execute("SELECT count(*) FROM stints").fetchone()[0],
            "quarantine": con.execute(
                "SELECT count(*) FROM quarantine").fetchone()[0],
            "reconciliation": con.execute(
                "SELECT count(*) FROM reconciliation").fetchone()[0],
            "non5v5_stints": bad,
        }
        # The cache must cover every scored (non-quarantined) train game.
        missing = con.execute("""
            SELECT count(*) FROM reconciliation r
            WHERE NOT r.quarantined
              AND r.game_id NOT IN (SELECT DISTINCT game_id FROM stints)
        """).fetchone()[0]
        stats["scored_games_missing_from_cache"] = missing
        return stats
    finally:
        con.close()


def main() -> None:
    tag = sys.argv[1] if len(sys.argv) > 1 else "panel_full"
    stats = load(tag)
    for k, v in stats.items():
        print(f"{k:35s} {v:,}")
    if stats["scored_games_missing_from_cache"]:
        print("WARNING: cache does not cover every scored game "
              "(incomplete panel or wrong machine; see PICKUP section 3).")


if __name__ == "__main__":
    main()
