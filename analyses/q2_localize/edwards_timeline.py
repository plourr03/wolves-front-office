"""Edwards 2025-26 availability and 3PA timeline.

Foundational context for all Q2 confound checks. Pulls per-game minutes
played and 3PA rate; classifies each game by availability status; flags
the Round 1 injury and Round 2 minute-restricted return windows.

Output: outputs/tables/q2_localize/edwards_2025_timeline.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lib import db
from analyses.q2_localize import config


# Edwards player_id
ANT_ID = config.ANT_ID

# Heuristic thresholds for availability classification. Edwards' typical
# RS minute load is 35.6 (per 71-game 2112-min total). We classify:
#   DNP        : 0 minutes played (no row in nba_player_stats)
#   Limited    : 1-29 minutes
#   Normal     : 30+ minutes
THRESH_LIMITED_MAX_MIN = 29


def pull_team_games(season_year: int) -> pd.DataFrame:
    """All Wolves games (RS + PO) for the season with date and matchup."""
    sql = """
        SELECT game_id, game_date, season_type, matchup, wl
        FROM nba_games
        WHERE team_id = %s
          AND (season_id %% 10000) = %s
        ORDER BY game_date, game_id
    """
    df = db.query(sql, (config.WOLVES_TEAM_ID, season_year))
    df["game_date"] = pd.to_datetime(df["game_date"])
    return df


def pull_edwards_per_game(season_year: int) -> pd.DataFrame:
    """Per-game stats for Edwards in the given season."""
    season_label = config.season_label(season_year)
    sql = """
        SELECT game_id, game_date, matchup, minutes_played,
               pts, fgm, fga, fg3m, fg3a, ftm, fta, plus_minus
        FROM nba_player_stats
        WHERE player_id = %s
          AND season_year = %s
    """
    df = db.query(sql, (ANT_ID, season_label))
    df["game_date"] = pd.to_datetime(df["game_date"])
    return df


def build_timeline(season_year: int) -> pd.DataFrame:
    """Outer join all Wolves games with Edwards per-game stats so DNP games
    show explicit zeros. Classify each game by availability status.
    """
    games = pull_team_games(season_year)
    edwards = pull_edwards_per_game(season_year)
    merged = games.merge(edwards, on=["game_id", "game_date"], how="left",
                          suffixes=("", "_e"))
    # Fill DNP rows with explicit zeros for the per-game stats.
    for c in ("minutes_played", "pts", "fgm", "fga", "fg3m", "fg3a",
              "ftm", "fta", "plus_minus"):
        merged[c] = pd.to_numeric(merged[c], errors="coerce").fillna(0)
    merged["3pa_rate"] = np.where(merged["fga"] > 0,
                                    merged["fg3a"] / merged["fga"], np.nan)
    merged["3p_pct"] = np.where(merged["fg3a"] > 0,
                                  merged["fg3m"] / merged["fg3a"], np.nan)
    merged["status"] = merged["minutes_played"].apply(_classify_status)
    # Sequential game number within season_type for rolling windows.
    merged = merged.sort_values(["game_date", "game_id"]).reset_index(drop=True)
    merged["game_seq"] = merged.groupby("season_type").cumcount() + 1
    return merged


def _classify_status(mins: float) -> str:
    if mins == 0:
        return "DNP"
    if mins <= THRESH_LIMITED_MAX_MIN:
        return "Limited"
    return "Normal"


def annotate_injury_windows(timeline: pd.DataFrame) -> pd.DataFrame:
    """Identify clusters of consecutive DNP games as injury windows."""
    out = timeline.copy()
    # Within each season_type, walk through and label injury windows.
    for st in out["season_type"].unique():
        sub = out[out["season_type"] == st].sort_values("game_date")
        window_id = 0
        window_active = False
        windows = []
        for _, row in sub.iterrows():
            if row["status"] == "DNP":
                if not window_active:
                    window_id += 1
                    window_active = True
                windows.append(window_id)
            else:
                window_active = False
                windows.append(0)
        out.loc[sub.index, "injury_window"] = windows
    out["injury_window"] = out["injury_window"].fillna(0).astype(int)
    return out


def rolling_3pa_rate(timeline: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Add a rolling 3PA rate column for trend visualization. Computed
    over the games Edwards actually played (DNPs excluded from the window).
    """
    out = timeline.copy()
    out["rolling_3pa_rate"] = np.nan
    for st in out["season_type"].unique():
        mask = (out["season_type"] == st) & (out["status"] != "DNP")
        sub = out[mask].sort_values("game_date")
        # Rolling mean of (fg3a, fga) totals.
        sub["roll_fg3a"] = sub["fg3a"].rolling(window=window, min_periods=1).sum()
        sub["roll_fga"] = sub["fga"].rolling(window=window, min_periods=1).sum()
        sub["roll_3pa_rate"] = sub["roll_fg3a"] / sub["roll_fga"].replace(0, np.nan)
        out.loc[sub.index, "rolling_3pa_rate"] = sub["roll_3pa_rate"].values
    return out


def summarize(timeline: pd.DataFrame) -> dict:
    """Summary by season_type and status."""
    summaries = {}
    for st in timeline["season_type"].unique():
        sub = timeline[timeline["season_type"] == st]
        by_status = (sub.groupby("status")
                       .agg(games=("game_id", "count"),
                            total_min=("minutes_played", "sum"),
                            avg_min=("minutes_played", "mean"),
                            avg_3pa_rate=("3pa_rate", "mean"),
                            avg_3p_pct=("3p_pct", "mean")))
        summaries[st] = by_status
    return summaries


def run():
    print("Edwards 2025-26 timeline (RS + PO)")
    timeline = build_timeline(2025)
    timeline = annotate_injury_windows(timeline)
    timeline = rolling_3pa_rate(timeline, window=5)

    summaries = summarize(timeline)

    print("\n--- Summary by season_type and status ---")
    for st, df in summaries.items():
        print(f"\n{st}:")
        print(df.round(3).to_string())

    print("\n--- Injury windows (consecutive DNP clusters) ---")
    inj = timeline[timeline["status"] == "DNP"].copy()
    if not inj.empty:
        wcounts = inj.groupby(["season_type", "injury_window"]).agg(
            n_games=("game_id", "count"),
            start_date=("game_date", "min"),
            end_date=("game_date", "max"),
        ).reset_index()
        print(wcounts.to_string(index=False))

    print("\n--- Limited-minutes games (Edwards played 1-29 minutes) ---")
    lim = timeline[timeline["status"] == "Limited"][
        ["game_date", "season_type", "matchup", "minutes_played", "fga", "fg3a",
         "3pa_rate", "wl"]
    ]
    if not lim.empty:
        print(lim.round(3).to_string(index=False))
    else:
        print("(none)")

    print("\n--- Edwards 2025-26 playoff games (game-by-game) ---")
    po = timeline[timeline["season_type"] == "Playoffs"][
        ["game_seq", "game_date", "matchup", "status", "minutes_played",
         "fga", "fg3a", "3pa_rate", "rolling_3pa_rate", "plus_minus", "wl"]
    ]
    print(po.round(3).to_string(index=False))

    print("\n--- Regular season 3PA rate by month (Edwards-played games only) ---")
    rs = timeline[(timeline["season_type"] == "Regular Season") &
                   (timeline["status"] != "DNP")].copy()
    rs["month"] = rs["game_date"].dt.to_period("M")
    monthly = rs.groupby("month").agg(
        games=("game_id", "count"),
        avg_minutes=("minutes_played", "mean"),
        fg3a_total=("fg3a", "sum"),
        fga_total=("fga", "sum"),
    ).reset_index()
    monthly["3pa_rate"] = monthly["fg3a_total"] / monthly["fga_total"].replace(0, np.nan)
    print(monthly.round(3).to_string(index=False))

    timeline.to_csv(config.TABLE_DIR / "edwards_2025_timeline.csv", index=False)
    print(f"\nWrote {config.TABLE_DIR / 'edwards_2025_timeline.csv'}")


if __name__ == "__main__":
    run()
