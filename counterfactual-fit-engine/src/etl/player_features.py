"""F3 prep: the player_features table (spec 7.3), one row per
player-season, the Layer 1b input matrix.

Sources:
  box + advanced      warehouse (nba_player_stats, nba_player_advanced_stats)
  tracking            nba_player_tracking_season (SEASON TOTALS; verified
                      2026-07-03 against SGA 2024-25 drives=1,567). Wide
                      table, one row per measure_type with off-measure
                      columns NULL, so each group is selected from its own
                      measure rows.
  on-floor possessions  the D6 stints table (lineup membership exploded),
                      the denominator for per-75 tracking rates.
  RAPM                outputs/rapm/rapm_<yr>.parquet when F2 has run;
                      otherwise the columns land NULL and the table carries
                      rapm_provisional=True (provisional tags on anything
                      downstream of an unratified gate).

Feature regimes are data-driven, not assumed: availability masks come from
src.models.feature_regime over the built table. Known hole logged
2026-07-03: the warehouse has NO 2020-21 tracking rows (2019-20 jumps to
2021-22); those player-seasons get NULL tracking features and the regime
mask marks them, pending an ingest backfill ruling.

Output: player_features table in data/fitengine.duckdb plus
outputs/features/player_features.parquet.

Usage: python -m src.etl.player_features
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.adapters.postmortem_lib import query  # noqa: E402

DB_PATH = FITENGINE_ROOT / "data" / "fitengine.duckdb"
RAPM_DIR = FITENGINE_ROOT / "outputs" / "rapm"
OUT_DIR = FITENGINE_ROOT / "outputs" / "features"

SEASONS = list(range(2014, 2027))  # end-year convention


def season_str(end_year: int) -> str:
    return f"{end_year - 1}-{str(end_year)[-2:]}"


def box_block(end_year: int) -> pd.DataFrame:
    ss = season_str(end_year)
    box = query("""
        SELECT player_id,
               COUNT(*) gp, SUM(minutes_played) minutes,
               SUM(pts) pts, SUM(ast) ast, SUM(tov) tov,
               SUM(oreb) oreb, SUM(dreb) dreb, SUM(stl) stl, SUM(blk) blk,
               SUM(pf) pf, SUM(fga) fga, SUM(fg3a) fg3a, SUM(fta) fta
        FROM nba_player_stats WHERE season_year = %s
        GROUP BY player_id HAVING SUM(minutes_played) > 0""", (ss,))
    adv = query("""
        SELECT person_id AS player_id,
          SUM(true_shooting_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) ts_pct,
          SUM(usage_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) usg_pct,
          SUM(assist_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) ast_pct,
          SUM(turnover_ratio*minutes_float)/NULLIF(SUM(minutes_float),0) tov_ratio,
          SUM(offensive_rebound_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) orb_pct,
          SUM(defensive_rebound_percentage*minutes_float)/NULLIF(SUM(minutes_float),0) drb_pct
        FROM nba_player_advanced_stats
        WHERE game_id IN (SELECT DISTINCT game_id FROM nba_player_stats
                          WHERE season_year = %s)
        GROUP BY person_id""", (ss,))
    df = box.merge(adv, on="player_id", how="left")
    m = df.minutes.clip(lower=1)
    df["fg3a_rate"] = df.fg3a / df.fga.clip(lower=1)
    df["ftr"] = df.fta / df.fga.clip(lower=1)
    for c in ("pts", "ast", "tov", "oreb", "dreb", "stl", "blk", "pf"):
        df[f"{c}36"] = df[c] / m * 36.0
    return df


TRACKING_GROUPS = {
    "Drives": ["drives", "drive_pts", "drive_passes"],
    "CatchShoot": ["catch_shoot_fg3a", "catch_shoot_fga", "catch_shoot_efg_pct"],
    "PullUpShot": ["pull_up_fg3a", "pull_up_fga", "pull_up_efg_pct"],
    "SpeedDistance": ["avg_speed", "avg_speed_off", "avg_speed_def"],
    "Rebounding": ["reb_contest", "reb_chances", "reb_contest_pct"],
    "Defense": ["def_rim_fgm", "def_rim_fga", "def_rim_fg_pct"],
    "Passing": ["potential_ast", "ast_points_created", "passes_made"],
}


def tracking_block(end_year: int) -> pd.DataFrame:
    ss = season_str(end_year)
    out: pd.DataFrame | None = None
    for measure, cols in TRACKING_GROUPS.items():
        sel = ", ".join(cols)
        df = query(f"""
            SELECT player_id, {sel}
            FROM nba_player_tracking_season
            WHERE season_year = %s AND season_type = 'Regular Season'
              AND measure_type = %s""", (ss, measure))
        out = df if out is None else out.merge(df, on="player_id", how="outer")
    return out if out is not None else pd.DataFrame({"player_id": []})


def possessions_block(con: duckdb.DuckDBPyConnection,
                      end_year: int) -> pd.DataFrame:
    yy = f"{end_year - 2001:02d}"
    return con.execute("""
        SELECT CAST(pid AS BIGINT) AS player_id,
               SUM(s.possessions_off) AS poss_off,
               SUM(s.possessions_def) AS poss_def
        FROM stints s
        JOIN games g USING (game_id),
             unnest(string_split(s.lineup_id, ',')) AS t(pid)
        WHERE g.include_train AND g.season_yy = ?
        GROUP BY 1
    """, [yy]).fetchdf()


def rapm_block(end_year: int) -> tuple[pd.DataFrame, bool]:
    p = RAPM_DIR / f"rapm_{end_year}.parquet"
    if not p.exists():
        return pd.DataFrame({"player_id": pd.Series(dtype="int64")}), True
    r = pd.read_parquet(p)[
        ["player_id", "off_rapm", "off_se", "def_rapm", "def_se"]]
    return r, False


def build(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    frames = []
    for yr in SEASONS:
        box = box_block(yr)
        if box.empty:
            continue
        trk = tracking_block(yr)
        poss = possessions_block(con, yr)
        rapm, provisional = rapm_block(yr)
        df = (box.merge(trk, on="player_id", how="left")
                 .merge(poss, on="player_id", how="left")
                 .merge(rapm, on="player_id", how="left"))
        # Postgres NUMERIC comes back as decimal.Decimal via psycopg2; cast
        # every non-key column to float so downstream arithmetic (per-75
        # rates, parquet) does not choke on Decimal/float mixing.
        keep = {"player_id"}
        for c in df.columns:
            if c not in keep:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        p75 = df.poss_off.clip(lower=1) / 75.0
        d75 = df.poss_def.clip(lower=1) / 75.0
        df["drives_per75"] = df.drives / p75
        df["cs_fg3a_per75"] = df.catch_shoot_fg3a / p75
        df["pu_fg3a_per75"] = df.pull_up_fg3a / p75
        df["potential_ast_per75"] = df.potential_ast / p75
        df["def_rim_fga_per75"] = df.def_rim_fga / d75
        df["reb_contest_rate"] = df.reb_contest / df.reb_chances.clip(lower=1)
        df["season"] = season_str(yr)
        df["end_year"] = yr
        df["rapm_provisional"] = provisional
        df["has_tracking"] = df.drives.notna()
        frames.append(df)
        print(f"  {season_str(yr)}: {len(df)} players, "
              f"tracking {df.has_tracking.mean():.0%}, "
              f"rapm {'PROVISIONAL (absent)' if provisional else 'joined'}")
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    feats = build(con)
    con.execute("CREATE OR REPLACE TABLE player_features AS SELECT * FROM feats")
    con.close()
    out = OUT_DIR / "player_features.parquet"
    feats.to_parquet(out, index=False)
    print(f"\n{len(feats):,} player-season rows -> {out}")
    print("regime summary (has_tracking share by season):")
    print(feats.groupby("season").has_tracking.mean().to_string())


if __name__ == "__main__":
    main()
