"""The 2023-24 to 2024-25 usage handoff: who gave up possessions to whom?

Tests three questions raised while drafting Article 2:

  1. Bobby's thesis: "the KAT-for-Randle swap was not Randle taking KAT's
     possessions, it was Randle forfeiting them to Edwards." Test by comparing
     KAT 2023-24 vs Randle 2024-25 vs Edwards both years on usage rate, time
     of possession, and on-ball creation volume.

  2. The Conley replacement question: did the Wolves bring in a guard to
     replace Conley's declining role? Rob Dillingham was the 2024 draft bet.
     Pull his role and the roster's how-acquired note.

  3. Conley vs Edwards as playmakers: assist rate, assist-to-turnover, and
     pick-and-roll ball-handler efficiency. Bobby's theory is that Edwards is
     a less efficient distributor than Conley was.

Re-runnable: python -m analyses.q0a_lafi.usage_handoff
"""
from __future__ import annotations

import pandas as pd

from lib import db

WOLVES = 1610612750
SEASONS = (2023, 2024, 2025)
FOCUS = ["Anthony Edwards", "Karl-Anthony Towns", "Julius Randle",
         "Mike Conley", "Rob Dillingham"]

pd.set_option("display.width", 180)
pd.set_option("display.max_rows", 60)


def box_season() -> pd.DataFrame:
    """Season box-score aggregates per Wolves player, RS."""
    sql = """
        SELECT (g.season_id %% 10000) AS sy, ps.player_name,
               COUNT(*) AS gp,
               SUM(ps.pts) AS pts, SUM(ps.ast) AS ast, SUM(ps.tov) AS tov,
               SUM(ps.fga) AS fga, SUM(ps.fta) AS fta
        FROM nba_player_stats ps
        JOIN nba_games g ON g.game_id = ps.game_id AND g.team_id = ps.team_id
        WHERE ps.team_id = %s
          AND g.season_type = 'Regular Season'
          AND (g.season_id %% 10000) IN (2023, 2024, 2025)
        GROUP BY 1, ps.player_name
    """
    df = db.query(sql, (WOLVES,))
    for c in ("sy", "gp", "pts", "ast", "tov", "fga", "fta"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["ppg"] = df["pts"] / df["gp"]
    df["apg"] = df["ast"] / df["gp"]
    df["topg"] = df["tov"] / df["gp"]
    df["ast_to"] = df["ast"] / df["tov"].replace(0, pd.NA)
    return df


def adv_season() -> pd.DataFrame:
    """Minutes-weighted usage and assist rate per Wolves player, RS."""
    sql = """
        SELECT (g.season_id %% 10000) AS sy,
               a.first_name || ' ' || a.family_name AS player_name,
               SUM(a.minutes_float) AS min,
               SUM(a.usage_percentage * a.minutes_float)
                   / NULLIF(SUM(a.minutes_float), 0) AS usage,
               SUM(a.assist_percentage * a.minutes_float)
                   / NULLIF(SUM(a.minutes_float), 0) AS ast_pct,
               SUM(a.true_shooting_percentage * a.minutes_float)
                   / NULLIF(SUM(a.minutes_float), 0) AS ts
        FROM nba_player_advanced_stats a
        JOIN nba_games g ON g.game_id = a.game_id AND g.team_id = a.team_id
        WHERE a.team_id = %s
          AND g.season_type = 'Regular Season'
          AND (g.season_id %% 10000) IN (2023, 2024, 2025)
        GROUP BY 1, 2
    """
    df = db.query(sql, (WOLVES,))
    for c in ("sy", "min", "usage", "ast_pct", "ts"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["mpg_min"] = df["min"]
    return df


def synergy_prbh() -> pd.DataFrame:
    """Pick-and-roll ball-handler volume and efficiency per player, RS."""
    sql = """
        SELECT season_year, player_name, poss, ppp, percentile
        FROM nba_synergy_player_play_types
        WHERE team_id = %s
          AND season_type = 'Regular Season'
          AND type_grouping = 'Offensive'
          AND play_type = 'PRBallHandler'
          AND season_year IN ('2023-24', '2024-25', '2025-26')
    """
    df = db.query(sql, (WOLVES,))
    for c in ("poss", "ppp", "percentile"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def roster_acquisition() -> pd.DataFrame:
    sql = """
        SELECT season, player, age, experience, how_acquired, position
        FROM nba_team_rosters
        WHERE team_id = %s
          AND player ILIKE '%%Dillingham%%'
    """
    return db.query(sql, (WOLVES,))


def run() -> None:
    box = box_season()
    adv = adv_season()

    merged = box.merge(adv[["sy", "player_name", "min", "usage", "ast_pct", "ts"]],
                       on=["sy", "player_name"], how="left")
    merged["mpg"] = merged["min"] / merged["gp"]

    print("=" * 90)
    print("  1. THE USAGE HANDOFF: KAT / Randle / Edwards / Conley")
    print("=" * 90)
    f = merged[merged["player_name"].isin(FOCUS)].copy()
    f = f.sort_values(["player_name", "sy"])
    cols = ["sy", "player_name", "gp", "mpg", "ppg", "usage", "ast_pct",
            "apg", "topg", "ast_to", "ts"]
    print(f[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    print("\n  Forfeit-thesis check (KAT 2023-24 vs Randle 2024-25):")
    for nm, sy in [("Karl-Anthony Towns", 2023), ("Julius Randle", 2024)]:
        r = merged[(merged["player_name"] == nm) & (merged["sy"] == sy)]
        if not r.empty:
            r = r.iloc[0]
            print(f"    {nm} {sy}-{str(sy+1)[-2:]}: "
                  f"usage {r['usage']:.1f}%, {r['ppg']:.1f} ppg")
    for sy in (2023, 2024):
        r = merged[(merged["player_name"] == "Anthony Edwards") & (merged["sy"] == sy)]
        if not r.empty:
            r = r.iloc[0]
            print(f"    Edwards {sy}-{str(sy+1)[-2:]}: "
                  f"usage {r['usage']:.1f}%, {r['ppg']:.1f} ppg")

    print("\n" + "=" * 90)
    print("  2. THE CONLEY REPLACEMENT: Rob Dillingham")
    print("=" * 90)
    d = merged[merged["player_name"] == "Rob Dillingham"][cols]
    print(d.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print("\n  Roster acquisition note:")
    print(roster_acquisition().to_string(index=False))

    print("\n" + "=" * 90)
    print("  3. CONLEY vs EDWARDS AS PLAYMAKERS")
    print("=" * 90)
    print("\n  Assist rate, assist-to-turnover, turnovers (box + advanced):")
    ce = merged[merged["player_name"].isin(["Mike Conley", "Anthony Edwards"])]
    print(ce[["sy", "player_name", "usage", "ast_pct", "apg", "topg",
              "ast_to"]].sort_values(["player_name", "sy"])
          .to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    print("\n  Pick-and-roll ball-handler (Synergy: volume, PPP, league percentile):")
    syn = synergy_prbh()
    syn = syn[syn["player_name"].isin(["Mike Conley", "Anthony Edwards"])]
    print(syn.sort_values(["player_name", "season_year"])
          .to_string(index=False, float_format=lambda x: f"{x:.3f}"))


if __name__ == "__main__":
    run()
