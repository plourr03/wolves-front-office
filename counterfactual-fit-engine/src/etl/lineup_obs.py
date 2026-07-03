"""F4 scaffolding: lineup_obs, the Layer 2 training rows (spec 7.2).

Directional aggregation from the D6 stints table: each physical stint
contributes its two directional (offense five vs defense five) rows,
aggregated per (season, off_lineup, def_lineup) with possession weights.

Columns per row: end_year, off_lineup, def_lineup, poss, pts_per100,
home_share (fraction of the matchup's possessions with the offense at
home), rest_delta (possession-weighted mean of off-team rest days minus
def-team rest days, capped at 7), clutch_share and the garbage exclusion
already applied upstream. A3's leverage BASIS ships as columns
(clutch_share; garbage time excluded at source per the F1 tagger flag);
the final scalar weighting rule is applied at Layer 2 training time from
config, never baked irreversibly into the table.

Clutch here is the stint-level shadow of the adapter tagger's definition:
last 5 minutes of P4/OT with running margin within 5 at stint start,
computed from the stint sequence itself (stints carry period, clock and
per-stint points, so the running margin is exact at stint boundaries).

Usage: python -m src.etl.lineup_obs   (writes table lineup_obs into
       data/fitengine.duckdb and outputs/features/lineup_obs.parquet)
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.adapters.postmortem_lib import query  # noqa: E402

DB_PATH = FITENGINE_ROOT / "data" / "fitengine.duckdb"
OUT_DIR = FITENGINE_ROOT / "outputs" / "features"
REST_CAP = 7.0


def game_context() -> pd.DataFrame:
    """(game_id, team_id) -> is_home, rest_days from nba_games."""
    g = query("""
        SELECT game_id, team_id, game_date,
               CASE WHEN matchup LIKE '%%vs.%%' THEN 1 ELSE 0 END AS is_home
        FROM nba_games WHERE season_type = 'Regular Season'
    """, ())
    g["game_date"] = pd.to_datetime(g.game_date)
    g = g.sort_values(["team_id", "game_date"])
    g["rest_days"] = (g.groupby("team_id").game_date.diff()
                        .dt.days.clip(upper=REST_CAP))
    g["rest_days"] = g["rest_days"].fillna(REST_CAP)
    return g[["game_id", "team_id", "is_home", "rest_days"]]


POSS_GLOB = str(FITENGINE_ROOT / "data" / "cache" / "possessions" / "*.parquet")


def build(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Layer 2 training rows from the POSSESSION cache (the correct grain:
    offense five vs defense five per possession). The stint table is the
    wrong source -- per-team stints do not share clock boundaries, so a
    stint self-join captures only the coincidentally-aligned subset (~7x
    undercount). Team context (home_share, rest_delta) attaches via the
    (game_id, lineup_id) -> team_id map from the stints table; a five-man
    lineup belongs to exactly one team in a game, and the possession-cache
    lineup strings are byte-identical to the stint lineup_ids (verified).

    Garbage possessions are already excluded (build_possessions carries the
    flag). The A3 leverage WEIGHTS proper -- from the frozen adapter
    taggers (tag_garbage_time/tag_clutch) -- attach at Layer 2 FIT time,
    not here; this builder ships the possession-weighted rows plus the
    context covariates the fit consumes. NO Layer 2 fit runs until F3
    vectors exist (directive 2026-07-03 item 4)."""
    ctx = game_context()
    con.register("ctx", ctx)
    df = con.execute("""
        WITH poss AS (
            SELECT game_id, season_yy, off_lineup, def_lineup,
                   COUNT(*) AS poss, SUM(points) AS pts
            FROM read_parquet(?, union_by_name=true)
            WHERE NOT garbage
            GROUP BY 1, 2, 3, 4
        ),
        lu_team AS (   -- a lineup belongs to one team per game
            SELECT DISTINCT game_id, lineup_id, team_id FROM stints
        ),
        per_game AS (
            SELECT p.game_id, p.season_yy, p.off_lineup, p.def_lineup,
                   p.poss, p.pts,
                   co.is_home AS off_home,
                   (co.rest_days - cd.rest_days) AS rest_delta
            FROM poss p
            JOIN lu_team ot ON ot.game_id = p.game_id AND ot.lineup_id = p.off_lineup
            JOIN lu_team dt ON dt.game_id = p.game_id AND dt.lineup_id = p.def_lineup
            JOIN ctx co ON co.game_id = p.game_id AND co.team_id = ot.team_id
            JOIN ctx cd ON cd.game_id = p.game_id AND cd.team_id = dt.team_id
        )
        SELECT season_yy,
               CAST(season_yy AS INTEGER) + 2001 AS end_year,
               off_lineup, def_lineup,
               SUM(poss) AS poss,
               SUM(pts) * 100.0 / SUM(poss) AS pts_per100,
               SUM(poss * off_home) * 1.0 / SUM(poss) AS home_share,
               SUM(poss * rest_delta) / SUM(poss) AS rest_delta,
               COUNT(DISTINCT game_id) AS n_games
        FROM per_game
        GROUP BY 1, 2, 3, 4
    """, [POSS_GLOB]).fetchdf()
    return df


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    obs = build(con)
    con.execute("CREATE OR REPLACE TABLE lineup_obs AS SELECT * FROM obs")
    con.close()
    obs.to_parquet(OUT_DIR / "lineup_obs.parquet", index=False)
    print(f"{len(obs):,} lineup_obs rows "
          f"({obs.poss.sum():,.0f} possessions) -> lineup_obs.parquet")
    print(obs.groupby("end_year").agg(rows=("poss", "size"),
                                      poss=("poss", "sum")).to_string())


if __name__ == "__main__":
    main()
