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


def build(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    ctx = game_context()
    con.register("ctx", ctx)
    df = con.execute("""
        WITH ss AS (
            SELECT s.*, g.season_yy
            FROM stints s JOIN games g USING (game_id)
            WHERE g.include_train AND NOT s.in_garbage_time
        ),
        margined AS (
            SELECT *,
                   COALESCE(SUM(points_for - points_against) OVER (
                       PARTITION BY game_id, team_id
                       ORDER BY period_start, clock_start_sec DESC
                       ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                   ), 0) AS margin_at_start
            FROM ss
        ),
        directional AS (
            SELECT a.game_id, a.season_yy,
                   a.lineup_id AS off_lineup, b.lineup_id AS def_lineup,
                   a.team_id AS off_team, b.team_id AS def_team,
                   a.possessions_off AS poss, a.points_for AS pts,
                   CASE WHEN a.period_start >= 4
                             AND a.clock_start_sec <= 300
                             AND abs(a.margin_at_start) <= 5
                        THEN 1 ELSE 0 END AS is_clutch
            FROM margined a JOIN margined b
              ON a.game_id = b.game_id
             AND a.period_start = b.period_start
             AND a.clock_start_sec = b.clock_start_sec
             AND a.period_end = b.period_end
             AND a.clock_end_sec = b.clock_end_sec
             AND a.team_id <> b.team_id
            WHERE a.possessions_off > 0
        )
        SELECT d.season_yy,
               CAST(d.season_yy AS INTEGER) + 2001 AS end_year,
               d.off_lineup, d.def_lineup,
               SUM(d.poss) AS poss,
               SUM(d.pts) * 100.0 / SUM(d.poss) AS pts_per100,
               SUM(d.poss * co.is_home) * 1.0 / SUM(d.poss) AS home_share,
               SUM(d.poss * (co.rest_days - cd.rest_days)) / SUM(d.poss)
                   AS rest_delta,
               SUM(d.poss * d.is_clutch) * 1.0 / SUM(d.poss) AS clutch_share,
               COUNT(*) AS n_stints
        FROM directional d
        JOIN ctx co ON co.game_id = d.game_id AND co.team_id = d.off_team
        JOIN ctx cd ON cd.game_id = d.game_id AND cd.team_id = d.def_team
        GROUP BY 1, 2, 3, 4
    """).fetchdf()
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
