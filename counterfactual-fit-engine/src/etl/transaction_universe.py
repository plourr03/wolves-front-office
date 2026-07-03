"""F5 prep: the mechanical transaction-universe builder (G4 protocol,
FROZEN in config/backtest_protocol.yaml).

SEALED-WINDOW DISCIPLINE, enforced structurally: the builder detects team
changes across ALL seasons (it has to, to know a 2020-21 offseason move's
realized window), but every artifact this module writes or returns is
HARD-FILTERED to development-window transactions (2015-16 .. 2020-21).
Sealed-window cases (2021-22 onward) are never enumerated, listed,
counted, or written anywhere; even the summary prints suppress them. The
one-look evaluation at F5 will lift the filter under its own ceremony.

Mechanics (from nba_player_stats team changes, per protocol):
  A transaction case = a player-team-stint start: the player's first game
  with a new team (their previous appearance was for a different team, or
  the change happens across seasons). Midseason move: previous appearance
  in the SAME season -> realized window = remainder of that season.
  Offseason move: last appearance in an earlier season -> realized window
  = the player's first (following) season with the new team.

  Filters, all mechanical, all within the realized window (R2 am. 1a/1b):
    top-100 league-wide TOTAL MINUTES in the season PRECEDING the
    transaction; >= 1,000 possessions with the new team (sensitivity cut
    at 1,500 reported too); >= 3 distinct five-man lineups. Possessions
    and lineup counts come from the D6 stints table.

Output: outputs/backtest/dev_transaction_universe.parquet + a readable
case list. Nothing sealed exists on disk.

Usage: python -m src.etl.transaction_universe
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
OUT_DIR = FITENGINE_ROOT / "outputs" / "backtest"

# development window, end-year convention (2015-16 -> 2016, .. 2020-21 -> 2021)
DEV_END_YEARS = frozenset({2016, 2017, 2018, 2019, 2020, 2021})
FIRST_END_YEAR = 2016            # transactions_since: 2015-16
MIN_POSS = 1000
SENSITIVITY_POSS = 1500
MIN_LINEUPS = 3
TOP_MINUTES_RANK = 100


def _end_year(season_year: str) -> int:
    return int(season_year[:4]) + 1


def appearances() -> pd.DataFrame:
    """Player-game appearances with team and date, regular season only."""
    df = query("""
        SELECT s.player_id, s.player_name, s.team_id, s.game_id,
               s.season_year, g.game_date
        FROM nba_player_stats s
        JOIN (SELECT DISTINCT game_id, game_date FROM nba_games
              WHERE season_type = 'Regular Season') g USING (game_id)
        WHERE s.minutes_played IS NOT NULL
        ORDER BY s.player_id, g.game_date
    """, ())
    df["game_date"] = pd.to_datetime(df.game_date)
    df["end_year"] = df.season_year.map(_end_year)
    return df


def minutes_rank_by_season() -> pd.DataFrame:
    """League-wide total-minutes rank per player per season (R2 am. 1a)."""
    df = query("""
        SELECT player_id, season_year, SUM(minutes_played) AS total_min,
               RANK() OVER (PARTITION BY season_year
                            ORDER BY SUM(minutes_played) DESC) AS min_rank
        FROM nba_player_stats GROUP BY player_id, season_year
    """, ())
    df["end_year"] = df.season_year.map(_end_year)
    return df[["player_id", "end_year", "total_min", "min_rank"]]


def detect_team_changes(app: pd.DataFrame) -> pd.DataFrame:
    """One row per player-team-change: transaction date, type, windows."""
    app = app.sort_values(["player_id", "game_date"])
    prev = app.groupby("player_id")[["team_id", "end_year", "game_date"]].shift(1)
    changed = app[(prev.team_id.notna()) & (app.team_id != prev.team_id)].copy()
    changed["prev_end_year"] = prev.end_year[changed.index].astype(int)
    changed["midseason"] = changed.end_year == changed.prev_end_year
    changed["transaction_date"] = changed.game_date  # first game with new team
    # realized window: the transaction season (midseason, remainder) or the
    # first new-team season (offseason move) -- both equal end_year here
    # because end_year IS the season of the first new-team appearance.
    changed["window_end_year"] = changed.end_year
    changed["preceding_end_year"] = changed.end_year - 1
    return changed[["player_id", "player_name", "team_id", "end_year",
                    "midseason", "transaction_date", "window_end_year",
                    "preceding_end_year", "game_id"]].rename(
                        columns={"team_id": "new_team_id",
                                 "game_id": "first_game_id"})


def realized_window_stats(con: duckdb.DuckDBPyConnection,
                          cases: pd.DataFrame) -> pd.DataFrame:
    """Possessions and distinct-lineup counts with the new team inside each
    case's realized window, from the stints table. Midseason cases count
    only games on/after the transaction date."""
    ctx = query("""SELECT DISTINCT game_id, game_date FROM nba_games
                   WHERE season_type = 'Regular Season'""", ())
    ctx["game_date"] = pd.to_datetime(ctx.game_date)
    con.register("case_list", cases)
    con.register("game_dates", ctx)
    return con.execute("""
        WITH player_stints AS (
            SELECT s.game_id, s.team_id, s.lineup_id,
                   CAST(t.pid AS BIGINT) AS player_id,
                   s.possessions_off + s.possessions_def AS poss
            FROM stints s,
                 unnest(string_split(s.lineup_id, ',')) AS t(pid)
        )
        SELECT c.player_id, c.new_team_id, c.transaction_date,
               SUM(ps.poss) AS window_poss,
               COUNT(DISTINCT ps.lineup_id) AS distinct_lineups
        FROM case_list c
        JOIN games g
          ON g.season_yy = printf('%02d', c.window_end_year - 2001)
         AND g.include_train
        JOIN game_dates gd ON gd.game_id = g.game_id
        JOIN player_stints ps
          ON ps.game_id = g.game_id AND ps.player_id = c.player_id
         AND ps.team_id = c.new_team_id
        WHERE gd.game_date >= c.transaction_date
        GROUP BY 1, 2, 3
    """).fetchdf()


def build() -> pd.DataFrame:
    app = appearances()
    ranks = minutes_rank_by_season()
    cases = detect_team_changes(app)
    cases = cases[cases.end_year >= FIRST_END_YEAR]

    # ---- SEALED-WINDOW HARD FILTER: nothing past the dev window survives
    # this line; sealed cases are never enumerated downstream. -----------
    cases = cases[cases.end_year.isin(DEV_END_YEARS)].copy()

    cases = cases.merge(
        ranks.rename(columns={"end_year": "preceding_end_year"}),
        on=["player_id", "preceding_end_year"], how="left")
    cases = cases[cases.min_rank <= TOP_MINUTES_RANK]

    con = duckdb.connect(str(DB_PATH), read_only=True)
    stats = realized_window_stats(con, cases)
    con.close()
    cases = cases.merge(stats, on=["player_id", "new_team_id",
                                   "transaction_date"], how="left")
    cases["window_poss"] = cases.window_poss.fillna(0.0)
    cases["distinct_lineups"] = cases.distinct_lineups.fillna(0).astype(int)
    universe = cases[(cases.window_poss >= MIN_POSS)
                     & (cases.distinct_lineups >= MIN_LINEUPS)].copy()
    universe["meets_sensitivity_cut"] = universe.window_poss >= SENSITIVITY_POSS
    universe["case_id"] = (universe.player_id.astype(str) + "_"
                           + universe.new_team_id.astype(str) + "_"
                           + universe.end_year.astype(str))
    return universe.sort_values(["end_year", "transaction_date"]).reset_index(drop=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    uni = build()
    assert set(uni.end_year).issubset(DEV_END_YEARS), \
        "sealed-window leak in the dev universe"
    out = OUT_DIR / "dev_transaction_universe.parquet"
    uni.to_parquet(out, index=False)
    print(f"DEV transaction universe: {len(uni)} cases -> {out}")
    print(uni.groupby("end_year").agg(
        cases=("case_id", "size"),
        midseason=("midseason", "sum"),
        sens_1500=("meets_sensitivity_cut", "sum")).to_string())


if __name__ == "__main__":
    main()
