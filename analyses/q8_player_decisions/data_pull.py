"""Q8 data pulls. New data beyond what Q2/RAPM already provide.

What this builds:
- Career trajectory per player (last 5 seasons): per-36 stats, TS%, eFG%, usage
- Playoff vs regular season splits per player per season
- Catch-and-shoot 3PA from tracking data (when available)
- The 2x2 Edwards-on/off x Randle-on/off lineup-grain matrix

What it does NOT build (intentional v1 scope):
- Tracking-data motion measurements (LAFI C2 with Gobert on vs off)
- Achilles recovery comp set (would need external research/scraping)
- Defensive-anchor center age curve
- Cap/contract details
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import db
from analyses.q2_localize import config as q2_config, analysis, batch


OUT_DIR = Path("outputs/tables/q8_player_decisions")
OUT_DIR.mkdir(parents=True, exist_ok=True)


PLAYERS = {
    "Gobert": q2_config.GOBERT_ID,
    "Randle": q2_config.RANDLE_ID,
    "DiVincenzo": q2_config.DIVINCENZO_ID,
    "Edwards": q2_config.ANT_ID,
    "Naz Reid": q2_config.NAZ_ID,
    "McDaniels": q2_config.MCDANIELS_ID,
    "Conley": q2_config.CONLEY_ID,
}


# ---------------------------------------------------------------------------
# Career trajectory (per-36 stats, last 5 seasons)
# ---------------------------------------------------------------------------


def career_trajectory(player_id: int, seasons: list[str] = None) -> pd.DataFrame:
    """Per-season per-game and per-36 stats for one player."""
    if seasons is None:
        seasons = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
    placeholders = ",".join(["%s"] * len(seasons))
    sql = f"""
        SELECT ps.season_year, COUNT(*) AS games,
               SUM(ps.minutes_played) AS mins,
               SUM(ps.pts) AS pts, SUM(ps.fgm) AS fgm, SUM(ps.fga) AS fga,
               SUM(ps.fg3m) AS fg3m, SUM(ps.fg3a) AS fg3a,
               SUM(ps.ftm) AS ftm, SUM(ps.fta) AS fta,
               SUM(ps.oreb) AS oreb, SUM(ps.dreb) AS dreb,
               SUM(ps.ast) AS ast, SUM(ps.tov) AS tov,
               SUM(ps.stl) AS stl, SUM(ps.blk) AS blk,
               SUM(ps.plus_minus) AS pm
        FROM nba_player_stats ps
        JOIN nba_games g ON ps.game_id = g.game_id AND ps.team_id = g.team_id
        WHERE ps.player_id = %s
          AND ps.season_year IN ({placeholders})
          AND g.season_type = 'Regular Season'
        GROUP BY ps.season_year
        ORDER BY ps.season_year
    """
    df = db.query(sql, (player_id, *seasons))
    if df.empty:
        return df
    # Per-36
    df["mp"] = df["mins"]
    df["pts_per_36"] = 36 * df["pts"] / df["mp"].replace(0, np.nan)
    df["fga_per_36"] = 36 * df["fga"] / df["mp"].replace(0, np.nan)
    df["fg3a_per_36"] = 36 * df["fg3a"] / df["mp"].replace(0, np.nan)
    df["fta_per_36"] = 36 * df["fta"] / df["mp"].replace(0, np.nan)
    df["oreb_per_36"] = 36 * df["oreb"] / df["mp"].replace(0, np.nan)
    df["dreb_per_36"] = 36 * df["dreb"] / df["mp"].replace(0, np.nan)
    df["ast_per_36"] = 36 * df["ast"] / df["mp"].replace(0, np.nan)
    df["tov_per_36"] = 36 * df["tov"] / df["mp"].replace(0, np.nan)
    df["pm_per_36"] = 36 * df["pm"] / df["mp"].replace(0, np.nan)
    df["fg_pct"] = df["fgm"] / df["fga"].replace(0, np.nan)
    df["fg3_pct"] = df["fg3m"] / df["fg3a"].replace(0, np.nan)
    df["ft_pct"] = df["ftm"] / df["fta"].replace(0, np.nan)
    df["ts_pct"] = df["pts"] / (2 * (df["fga"] + 0.44 * df["fta"])).replace(0, np.nan)
    df["efg_pct"] = (df["fgm"] + 0.5 * df["fg3m"]) / df["fga"].replace(0, np.nan)
    df["3pa_rate"] = df["fg3a"] / df["fga"].replace(0, np.nan)
    df["usg_proxy"] = (df["fga"] + 0.44 * df["fta"] + df["tov"]) / df["mp"].replace(0, np.nan)
    return df


def playoff_vs_rs(player_id: int, seasons: list[str] = None) -> pd.DataFrame:
    """For each season, regular season vs playoffs split per player."""
    if seasons is None:
        seasons = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
    placeholders = ",".join(["%s"] * len(seasons))
    sql = f"""
        SELECT ps.season_year, g.season_type, COUNT(*) AS games,
               SUM(ps.minutes_played) AS mins,
               SUM(ps.pts) AS pts, SUM(ps.fga) AS fga, SUM(ps.fg3a) AS fg3a,
               SUM(ps.fta) AS fta, SUM(ps.fgm) AS fgm, SUM(ps.fg3m) AS fg3m,
               SUM(ps.ftm) AS ftm, SUM(ps.tov) AS tov, SUM(ps.plus_minus) AS pm
        FROM nba_player_stats ps
        JOIN nba_games g ON ps.game_id = g.game_id AND ps.team_id = g.team_id
        WHERE ps.player_id = %s
          AND ps.season_year IN ({placeholders})
          AND g.season_type IN ('Regular Season', 'Playoffs')
        GROUP BY ps.season_year, g.season_type
        ORDER BY ps.season_year, g.season_type
    """
    df = db.query(sql, (player_id, *seasons))
    if df.empty:
        return df
    df["mp"] = df["mins"]
    df["pts_per_36"] = 36 * df["pts"] / df["mp"].replace(0, np.nan)
    df["fg3a_per_36"] = 36 * df["fg3a"] / df["mp"].replace(0, np.nan)
    df["ts_pct"] = df["pts"] / (2 * (df["fga"] + 0.44 * df["fta"])).replace(0, np.nan)
    df["3pa_rate"] = df["fg3a"] / df["fga"].replace(0, np.nan)
    df["fg3_pct"] = df["fg3m"] / df["fg3a"].replace(0, np.nan)
    df["pm_per_36"] = 36 * df["pm"] / df["mp"].replace(0, np.nan)
    return df


def catch_and_shoot_per_season(player_id: int) -> pd.DataFrame:
    """Pull catch-and-shoot tracking data per season for a player."""
    sql = """
        SELECT season_year, season_type,
               team_abbreviation,
               catch_shoot_fg3a AS cs_3pa,
               catch_shoot_fg3m AS cs_3pm,
               catch_shoot_fg3_pct AS cs_3pct,
               gp
        FROM nba_player_tracking_season
        WHERE player_id = %s
        ORDER BY season_year, season_type
    """
    try:
        df = db.query(sql, (player_id,))
        if not df.empty:
            df["cs_3pa_per_game"] = df["cs_3pa"] / df["gp"].replace(0, np.nan)
        return df
    except Exception as e:
        print(f"  catch_and_shoot pull failed for {player_id}: {e}")
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# Edwards x Randle 2x2 lineup matrix (the key Q8 Randle test)
# ---------------------------------------------------------------------------


def edwards_randle_2x2(season_year: int = 2025) -> pd.DataFrame:
    """Compute the team's net rating in each of 4 cohorts:
        Edwards on, Randle on (the default)
        Edwards on, Randle off
        Edwards off, Randle on
        Edwards off, Randle off

    Returns one row per (season_type, cohort) with stints, minutes, net rating,
    bootstrap CI on net rating.
    """
    cache = q2_config.CACHE_DIR / f"wolves_{season_year}_stints"
    stints = batch.load_cached_stints(cache)
    wolves = stints[stints["team_id"] == q2_config.WOLVES_TEAM_ID].copy()
    splits = analysis.split_stints_by_season_type(wolves, season_year=season_year)

    rows = []
    for st_name, sub in splits.items():
        if sub.empty:
            continue
        sub = sub[~sub["in_garbage_time"]]

        e_on = sub["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, q2_config.ANT_ID))
        r_on = sub["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, q2_config.RANDLE_ID))

        cohorts = {
            "EdwardsON_RandleON":  sub[e_on & r_on],
            "EdwardsON_RandleOFF": sub[e_on & ~r_on],
            "EdwardsOFF_RandleON": sub[~e_on & r_on],
            "EdwardsOFF_RandleOFF": sub[~e_on & ~r_on],
        }
        for label, df in cohorts.items():
            if df.empty:
                continue
            minutes = df["duration_sec"].sum() / 60
            poss_off = df["possessions_off"].sum()
            poss_def = df["possessions_def"].sum()
            net = 100 * df["points_for"].sum() / poss_off - 100 * df["points_against"].sum() / poss_def \
                  if poss_off and poss_def else np.nan
            off = 100 * df["points_for"].sum() / poss_off if poss_off else np.nan
            d = 100 * df["points_against"].sum() / poss_def if poss_def else np.nan
            tpa_rate = df["fg3a_off"].sum() / df["fga_off"].sum() if df["fga_off"].sum() else np.nan
            bs = analysis.bootstrap_lineup_metric(df, analysis.m_net_rating)
            rows.append({
                "season_type": st_name, "cohort": label,
                "stints": len(df), "minutes": float(minutes),
                "poss_off": int(poss_off), "poss_def": int(poss_def),
                "net_rating": float(net), "net_ci_lo": bs["ci_lo"], "net_ci_hi": bs["ci_hi"],
                "off_rating": float(off), "def_rating": float(d),
                "off_3pa_rate": float(tpa_rate),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run():
    print("=== Q8 data pulls ===\n")

    # Career trajectories
    print("\nCareer trajectories (RS only, last 5 seasons):")
    all_traj = []
    for name, pid in PLAYERS.items():
        df = career_trajectory(pid)
        if df.empty:
            continue
        df["player"] = name
        print(f"\n{name}:")
        cols = ["season_year", "games", "mp", "pts_per_36", "fg3a_per_36",
                "ast_per_36", "ts_pct", "3pa_rate", "usg_proxy", "pm_per_36"]
        print(df[cols].round(3).to_string(index=False))
        all_traj.append(df.assign(player=name))
    if all_traj:
        pd.concat(all_traj).to_csv(OUT_DIR / "career_trajectories.csv", index=False)

    # Playoff vs RS
    print("\n\nPlayoff vs RS splits:")
    all_porfs = []
    for name, pid in PLAYERS.items():
        df = playoff_vs_rs(pid)
        if df.empty:
            continue
        df["player"] = name
        print(f"\n{name}:")
        cols = ["season_year", "season_type", "games", "mp", "pts_per_36",
                "fg3a_per_36", "ts_pct", "3pa_rate", "pm_per_36"]
        print(df[cols].round(3).to_string(index=False))
        all_porfs.append(df)
    if all_porfs:
        pd.concat(all_porfs).to_csv(OUT_DIR / "playoff_vs_rs.csv", index=False)

    # Catch-and-shoot
    print("\n\nCatch-and-shoot tracking:")
    all_cs = []
    for name, pid in PLAYERS.items():
        df = catch_and_shoot_per_season(pid)
        if df.empty:
            continue
        df["player"] = name
        print(f"\n{name}:")
        if "cs_3pa_per_game" in df.columns:
            cols = ["season_year", "season_type", "gp", "cs_3pa_per_game",
                    "cs_3pct"]
            print(df[cols].round(3).to_string(index=False))
        all_cs.append(df)
    if all_cs:
        pd.concat(all_cs).to_csv(OUT_DIR / "catch_and_shoot.csv", index=False)

    # Edwards x Randle 2x2
    print("\n\n=== Edwards x Randle 2x2 (2025-26) ===")
    er = edwards_randle_2x2(2025)
    print(er[["season_type", "cohort", "stints", "minutes", "poss_off",
              "net_rating", "net_ci_lo", "net_ci_hi", "off_3pa_rate"]].round(3).to_string(index=False))
    er.to_csv(OUT_DIR / "edwards_randle_2x2.csv", index=False)

    print("\n\n=== Edwards x Randle 2x2 (2024-25) ===")
    er24 = edwards_randle_2x2(2024)
    print(er24[["season_type", "cohort", "stints", "minutes", "poss_off",
                "net_rating", "net_ci_lo", "net_ci_hi", "off_3pa_rate"]].round(3).to_string(index=False))
    er24.to_csv(OUT_DIR / "edwards_randle_2x2_2024.csv", index=False)


if __name__ == "__main__":
    run()
