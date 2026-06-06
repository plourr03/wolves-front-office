"""2024-25 vs 2025-26 comparison using warehouse aggregates.

Because the lineup pipeline does not yet handle 2024-25 legacy PBP format,
this module uses team-level and player-level warehouse aggregates to
investigate the discontinuous drop identified in Q1.

Sources:
- nba_team_advanced_stats (team-level four factors and ratings per game)
- nba_player_stats (player box score per game)
- nba_player_advanced_stats (player TS%, USG%, etc., per game)
- nba_player_tracking_game (catch-and-shoot 3PA, etc., when present)
- nba_synergy_player_play_types (iso frequency / efficiency)

The intent is to answer: where in personnel space did the 2025-26
discontinuous drop concentrate?

Output: per-player and per-team Wolves-only RS and PO splits for both
seasons, with year-over-year deltas and bootstrap CIs on per-game means.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lib import db
from analyses.q2_localize import config


# ---------------------------------------------------------------------------
# Wolves player stats per season-slice
# ---------------------------------------------------------------------------


def load_wolves_player_stats(season_year: int, season_type: str) -> pd.DataFrame:
    """Pull per-game player stats for Wolves players in a season slice."""
    sql = """
        SELECT ps.player_id, ps.player_name, ps.game_id, ps.game_date,
               ps.minutes_played, ps.pts, ps.fgm, ps.fga, ps.fg3m, ps.fg3a,
               ps.ftm, ps.fta, ps.oreb, ps.dreb, ps.ast, ps.tov, ps.stl, ps.blk,
               ps.plus_minus, ps.matchup
        FROM nba_player_stats ps
        WHERE ps.team_id = %s
          AND ps.season_year = %s
          AND ps.minutes_played > 0
    """
    season_label = f"{season_year}-{str(season_year + 1)[-2:]}"
    df = db.query(sql, (config.WOLVES_TEAM_ID, season_label))
    df["game_date"] = pd.to_datetime(df["game_date"])
    # Identify season_type via the games table.
    if not df.empty:
        gids = sorted(df["game_id"].unique())
        placeholders = ",".join(["%s"] * len(gids))
        meta = db.query(
            f"SELECT DISTINCT game_id, season_type FROM nba_games WHERE game_id IN ({placeholders})",
            tuple(gids),
        )
        season_map = dict(zip(meta["game_id"], meta["season_type"]))
        df["season_type"] = df["game_id"].map(season_map)
        df = df[df["season_type"] == season_type].copy()
    return df


def aggregate_player_season(df: pd.DataFrame) -> pd.DataFrame:
    """Per-(player_id) season totals + rate stats."""
    if df.empty:
        return pd.DataFrame()
    g = df.groupby(["player_id", "player_name"], as_index=False).agg(
        games=("game_id", "nunique"),
        mins=("minutes_played", "sum"),
        pts=("pts", "sum"),
        fgm=("fgm", "sum"),
        fga=("fga", "sum"),
        fg3m=("fg3m", "sum"),
        fg3a=("fg3a", "sum"),
        ftm=("ftm", "sum"),
        fta=("fta", "sum"),
        oreb=("oreb", "sum"),
        dreb=("dreb", "sum"),
        ast=("ast", "sum"),
        tov=("tov", "sum"),
        plus_minus=("plus_minus", "sum"),
    )
    g["fg_pct"] = g["fgm"] / g["fga"].replace(0, np.nan)
    g["fg3_pct"] = g["fg3m"] / g["fg3a"].replace(0, np.nan)
    g["ft_pct"] = g["ftm"] / g["fta"].replace(0, np.nan)
    g["ts_pct"] = g["pts"] / (2 * (g["fga"] + 0.44 * g["fta"])).replace(0, np.nan)
    g["efg_pct"] = (g["fgm"] + 0.5 * g["fg3m"]) / g["fga"].replace(0, np.nan)
    g["fg3a_per_36"] = 36 * g["fg3a"] / g["mins"].replace(0, np.nan)
    g["3pa_rate"] = g["fg3a"] / g["fga"].replace(0, np.nan)
    g["usg_proxy"] = (g["fga"] + 0.44 * g["fta"] + g["tov"]) / g["mins"].replace(0, np.nan)
    g["plus_minus_per_36"] = 36 * g["plus_minus"] / g["mins"].replace(0, np.nan)
    return g


def yoy_player_comparison(season_a: int, season_b: int,
                            season_type: str) -> pd.DataFrame:
    """Compare per-player aggregates between two seasons for one season_type."""
    df_a = load_wolves_player_stats(season_a, season_type)
    df_b = load_wolves_player_stats(season_b, season_type)
    if df_a.empty and df_b.empty:
        return pd.DataFrame()
    agg_a = aggregate_player_season(df_a)
    agg_b = aggregate_player_season(df_b)
    if not agg_a.empty:
        agg_a = agg_a.add_suffix(f"_{season_a}")
        agg_a = agg_a.rename(columns={f"player_id_{season_a}": "player_id",
                                        f"player_name_{season_a}": "player_name"})
    if not agg_b.empty:
        agg_b = agg_b.add_suffix(f"_{season_b}")
        agg_b = agg_b.rename(columns={f"player_id_{season_b}": "player_id",
                                        f"player_name_{season_b}": "player_name"})
    if agg_a.empty:
        return agg_b
    if agg_b.empty:
        return agg_a
    merged = agg_a.merge(agg_b, on=["player_id", "player_name"], how="outer")
    # Year-over-year deltas for rate stats.
    for stat in ("ts_pct", "efg_pct", "fg3_pct", "3pa_rate",
                  "fg3a_per_36", "usg_proxy", "plus_minus_per_36"):
        col_a = f"{stat}_{season_a}"
        col_b = f"{stat}_{season_b}"
        if col_a in merged.columns and col_b in merged.columns:
            merged[f"{stat}_delta"] = merged[col_b] - merged[col_a]
    return merged.sort_values(f"mins_{season_b}", ascending=False, na_position="last")


# ---------------------------------------------------------------------------
# Team-level Wolves trajectory (which we already have in Q1; reused here
# for the year-over-year synthesis)
# ---------------------------------------------------------------------------


def load_team_advanced_per_game(season_year: int, season_type: str) -> pd.DataFrame:
    """Per-game team advanced stats for Wolves in a season slice."""
    sql = """
        SELECT tas.game_id, tas.team_id, ng.game_date,
               tas.offensive_rating, tas.defensive_rating, tas.net_rating,
               tas.pace, tas.possessions,
               tas.true_shooting_percentage AS ts_pct,
               tas.effective_field_goal_percentage AS efg_pct,
               tas.assist_percentage AS assist_pct
        FROM nba_team_advanced_stats tas
        JOIN nba_games ng ON tas.game_id = ng.game_id AND tas.team_id = ng.team_id
        WHERE tas.team_id = %s
          AND (ng.season_id %% 10000) = %s
          AND ng.season_type = %s
    """
    df = db.query(sql, (config.WOLVES_TEAM_ID, season_year, season_type))
    df["game_date"] = pd.to_datetime(df["game_date"])
    return df


def team_season_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    df = df.copy()
    for c in ("possessions", "offensive_rating", "defensive_rating",
              "net_rating", "pace", "efg_pct", "ts_pct"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    poss = df["possessions"].sum()
    return {
        "n_games": len(df),
        "possessions": float(poss),
        "off_rating_pg_avg": float(df["offensive_rating"].mean()),
        "def_rating_pg_avg": float(df["defensive_rating"].mean()),
        "net_rating_pg_avg": float(df["net_rating"].mean()),
        "pace_avg": float(df["pace"].mean()),
        "efg_pct_avg": float(df["efg_pct"].mean()) if "efg_pct" in df.columns else None,
        "ts_pct_avg": float(df["ts_pct"].mean()) if "ts_pct" in df.columns else None,
    }


# ---------------------------------------------------------------------------
# Synergy isolation comparison
# ---------------------------------------------------------------------------


def load_wolves_synergy_isolation(season_year: int, season_type: str) -> pd.DataFrame:
    """Pull synergy isolation play-type frequencies and efficiency for Wolves
    players in a season slice.
    """
    season_label = f"{season_year}-{str(season_year + 1)[-2:]}"
    sql = """
        SELECT player_id, player_name, play_type, season_type,
               poss AS possessions, poss_pct AS freq_pct, ppp,
               fg_pct, efg_pct, percentile
        FROM nba_synergy_player_play_types
        WHERE team_id = %s
          AND season_year = %s
          AND season_type = %s
    """
    return db.query(sql, (config.WOLVES_TEAM_ID, season_label, season_type))


def yoy_synergy_iso(season_a: int, season_b: int, season_type: str) -> pd.DataFrame:
    a = load_wolves_synergy_isolation(season_a, season_type)
    b = load_wolves_synergy_isolation(season_b, season_type)
    if a.empty and b.empty:
        return pd.DataFrame()
    a_iso = a[a["play_type"].str.lower().str.startswith("iso")].copy()
    b_iso = b[b["play_type"].str.lower().str.startswith("iso")].copy()
    a_iso = a_iso.rename(columns={"possessions": f"poss_{season_a}",
                                   "freq_pct": f"freq_{season_a}",
                                   "ppp": f"ppp_{season_a}"})
    b_iso = b_iso.rename(columns={"possessions": f"poss_{season_b}",
                                   "freq_pct": f"freq_{season_b}",
                                   "ppp": f"ppp_{season_b}"})
    keep_a = ["player_id", "player_name", f"poss_{season_a}",
              f"freq_{season_a}", f"ppp_{season_a}"]
    keep_b = ["player_id", "player_name", f"poss_{season_b}",
              f"freq_{season_b}", f"ppp_{season_b}"]
    merged = a_iso[[c for c in keep_a if c in a_iso.columns]].merge(
        b_iso[[c for c in keep_b if c in b_iso.columns]],
        on=["player_id", "player_name"], how="outer")
    return merged


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run():
    print("=== Wolves player YoY: 2024-25 vs 2025-26 (Regular Season) ===")
    rs_yoy = yoy_player_comparison(2024, 2025, "Regular Season")
    if not rs_yoy.empty:
        cols_show = ["player_id", "player_name", "mins_2024", "mins_2025",
                     "ts_pct_2024", "ts_pct_2025", "ts_pct_delta",
                     "3pa_rate_2024", "3pa_rate_2025", "3pa_rate_delta",
                     "fg3_pct_2024", "fg3_pct_2025",
                     "fg3a_per_36_2024", "fg3a_per_36_2025", "fg3a_per_36_delta",
                     "plus_minus_per_36_2024", "plus_minus_per_36_2025", "plus_minus_per_36_delta"]
        cols_show = [c for c in cols_show if c in rs_yoy.columns]
        sub = rs_yoy[cols_show]
        print(sub.head(15).round(3).to_string(index=False))
        rs_yoy.to_csv(config.TABLE_DIR / "yoy_player_rs.csv", index=False)

    print("\n=== Wolves player YoY: 2024-25 vs 2025-26 (Playoffs) ===")
    po_yoy = yoy_player_comparison(2024, 2025, "Playoffs")
    if not po_yoy.empty:
        cols_show = ["player_id", "player_name", "games_2024", "games_2025",
                     "mins_2024", "mins_2025",
                     "ts_pct_2024", "ts_pct_2025", "ts_pct_delta",
                     "3pa_rate_2024", "3pa_rate_2025", "3pa_rate_delta",
                     "fg3a_per_36_2024", "fg3a_per_36_2025",
                     "plus_minus_per_36_2024", "plus_minus_per_36_2025"]
        cols_show = [c for c in cols_show if c in po_yoy.columns]
        sub = po_yoy[cols_show]
        print(sub.head(15).round(3).to_string(index=False))
        po_yoy.to_csv(config.TABLE_DIR / "yoy_player_po.csv", index=False)

    print("\n=== Wolves team-level (PO 2024-25 vs PO 2025-26) ===")
    t24 = load_team_advanced_per_game(2024, "Playoffs")
    t25 = load_team_advanced_per_game(2025, "Playoffs")
    s24 = team_season_summary(t24)
    s25 = team_season_summary(t25)
    print("2024-25 PO:", s24)
    print("2025-26 PO:", s25)

    print("\n=== Wolves Synergy iso (RS 2024-25 vs RS 2025-26) ===")
    iso_rs = yoy_synergy_iso(2024, 2025, "Regular Season")
    if not iso_rs.empty:
        print(iso_rs.round(3).to_string(index=False))
        iso_rs.to_csv(config.TABLE_DIR / "yoy_synergy_iso_rs.csv", index=False)

    print("\n=== Wolves Synergy iso (PO 2024-25 vs PO 2025-26) ===")
    iso_po = yoy_synergy_iso(2024, 2025, "Playoffs")
    if not iso_po.empty:
        print(iso_po.round(3).to_string(index=False))
        iso_po.to_csv(config.TABLE_DIR / "yoy_synergy_iso_po.csv", index=False)

    print(f"\nOutputs written to {config.TABLE_DIR}")


if __name__ == "__main__":
    run()
