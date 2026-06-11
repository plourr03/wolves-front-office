#!/usr/bin/env python3
"""
pull_gobert_usage.py -- Gobert usage audit (feeds "It's Not All Gobert's Fault").

Pulls, BY SEASON, Utah years (UTA, 2013-14..2021-22) vs Minnesota years (MIN, 2022-23..),
entirely from the warehouse (synergy + tracking + PBP all cover his full career locally):

  A. Roll man (offensive PRRollMan): poss, poss/game, PPP, poss_pct (his offensive diet share)
  B. Touches (tracking Possessions measure): touches, touches/game, front-court touches, time of poss
  C. Dunk attempts (PBP): dunk FGA, dunk/game, dunk FG% (the "lob/vertical-threat" volume)
  D. Delivery system: # of teammates that roster-season with meaningful PnR BALL-HANDLER volume
     (offensive PRBallHandler poss >= threshold), the proxy for live-dribble passers around him.

Screen assists are a hustle stat (warehouse holds only 2025-26); pulled separately via nba_api
in pull_gobert_screen_assists.py and merged if available. Writes data/cache/gobert_usage.csv.

    python pull_gobert_usage.py
"""
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POST = os.path.abspath(os.path.join(HERE, "..", "..", "postmortem"))
sys.path.insert(0, POST)
from lib import db  # noqa: E402
OUT = os.path.join(HERE, "..", "data", "cache", "gobert_usage.csv")

GOBERT = 203497
# PnR ball-handler volume thresholds for the "delivery system" count (offensive poss / season)
MEANINGFUL = 150   # a real secondary live-dribble creator
PRIMARY = 300      # a high-volume primary initiator


def q(sql, params=None):
    with db.connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = 60000")
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


def main():
    # ---- confirm type_grouping values ----
    tg = q("""SELECT DISTINCT type_grouping FROM nba_synergy_player_play_types LIMIT 10""")
    print("type_grouping values:", tg["type_grouping"].tolist())

    # ---- Gobert games played + team per season (RS) from player_stats ----
    gp = q("""SELECT ps.season_year, ps.team_abbreviation team, COUNT(*) gp,
                     SUM(ps.minutes_played) tot_min
              FROM nba_player_stats ps JOIN nba_games g
                ON ps.game_id=g.game_id AND ps.team_id=g.team_id
              WHERE ps.player_id=%s AND g.season_type='Regular Season'
              GROUP BY 1,2 ORDER BY 1""", (GOBERT,))
    # one team per season for Gobert (no mid-season trades in his career)
    gp = gp.sort_values("gp", ascending=False).groupby("season_year").head(1).sort_values("season_year")
    gp["era"] = gp["team"].map(lambda t: "Utah" if t == "UTA" else ("Minnesota" if t == "MIN" else t))
    print("\nGobert season/team/gp:")
    print(gp.to_string(index=False))

    # ---- A. roll man (offensive) ----
    roll = q("""SELECT season_year, poss roll_poss, ppp roll_ppp, poss_pct roll_poss_pct,
                       pts roll_pts, fg_pct roll_fg
                FROM nba_synergy_player_play_types
                WHERE player_id=%s AND play_type='PRRollMan'
                  AND season_type='Regular Season' AND type_grouping='Offensive'
                ORDER BY season_year""", (GOBERT,))

    # ---- A2. his own PR ball-handler (should be ~zero; sanity) ----
    bh = q("""SELECT season_year, poss bh_poss
              FROM nba_synergy_player_play_types
              WHERE player_id=%s AND play_type='PRBallHandler'
                AND season_type='Regular Season' AND type_grouping='Offensive'
              ORDER BY season_year""", (GOBERT,))

    # ---- B. touches (Possessions measure) ----
    tch = q("""SELECT season_year, touches, front_ct_touches, time_of_poss, avg_sec_per_touch,
                      paint_touches, pts_per_touch
               FROM nba_player_tracking_season
               WHERE player_id=%s AND season_type='Regular Season' AND measure_type='Possessions'
               ORDER BY season_year""", (GOBERT,))

    # ---- C. dunk attempts from PBP (per season) ----
    # season map: game_id -> season_year for Regular Season games (season_year lives on
    # player_stats, season_type on games), then join to Gobert's PBP shot rows only.
    dunk = q("""WITH smap AS (
                  SELECT ps.game_id, MIN(ps.season_year) season_year
                  FROM nba_player_stats ps JOIN nba_games g
                    ON ps.game_id=g.game_id AND g.season_type='Regular Season'
                  GROUP BY ps.game_id
                )
                SELECT smap.season_year,
                       COUNT(*) dunk_fga,
                       SUM(CASE WHEN pbp.shot_result ILIKE 'made' THEN 1 ELSE 0 END) dunk_fgm
                FROM nba_play_by_play pbp JOIN smap ON pbp.game_id=smap.game_id
                WHERE pbp.person_id=%s AND pbp.is_field_goal=1
                  AND (pbp.sub_type ILIKE '%%dunk%%' OR pbp.description ILIKE '%%dunk%%')
                GROUP BY 1 ORDER BY 1""", (GOBERT,))

    # ---- D. delivery system: teammates with meaningful PnR ball-handler volume ----
    # For each Gobert season+team, count DISTINCT players on that team (synergy primary team)
    # with offensive PRBallHandler poss >= threshold, EXCLUDING Gobert himself.
    deliv_rows = []
    for _, r in gp.iterrows():
        sy, team = r["season_year"], r["team"]
        d = q("""SELECT player_id, player_name, poss
                 FROM nba_synergy_player_play_types
                 WHERE season_year=%s AND season_type='Regular Season'
                   AND play_type='PRBallHandler' AND type_grouping='Offensive'
                   AND team_abbreviation=%s AND player_id<>%s
                 ORDER BY poss DESC""", (sy, team, GOBERT))
        meaningful = d[d["poss"] >= MEANINGFUL]
        primary = d[d["poss"] >= PRIMARY]
        deliv_rows.append({
            "season_year": sy,
            "deliv_meaningful": len(meaningful),
            "deliv_primary": len(primary),
            "top_bh": (meaningful["player_name"].iloc[0] if len(meaningful) else None),
            "top_bh_poss": (int(meaningful["poss"].iloc[0]) if len(meaningful) else 0),
            "bh_names": "; ".join(f"{n}({int(p)})" for n, p in
                                  zip(meaningful["player_name"], meaningful["poss"])),
        })
    deliv = pd.DataFrame(deliv_rows)

    # ---- merge ----
    df = gp.merge(roll, on="season_year", how="left") \
           .merge(bh, on="season_year", how="left") \
           .merge(tch, on="season_year", how="left") \
           .merge(dunk, on="season_year", how="left") \
           .merge(deliv, on="season_year", how="left")

    # per-game rates
    df["roll_poss_pg"] = (df["roll_poss"] / df["gp"]).round(2)
    df["touches_pg"] = (df["touches"] / df["gp"]).round(1)
    df["frontct_touches_pg"] = (df["front_ct_touches"] / df["gp"]).round(1)
    df["dunk_fga_pg"] = (df["dunk_fga"] / df["gp"]).round(2)
    df["dunk_fg"] = (df["dunk_fgm"] / df["dunk_fga"]).round(3)
    df["mpg"] = (df["tot_min"] / df["gp"]).round(1)

    cols = ["season_year", "era", "team", "gp", "mpg",
            "roll_poss", "roll_poss_pg", "roll_ppp", "roll_poss_pct", "roll_fg",
            "bh_poss", "touches", "touches_pg", "frontct_touches_pg", "paint_touches",
            "time_of_poss", "dunk_fga", "dunk_fga_pg", "dunk_fg",
            "deliv_meaningful", "deliv_primary", "top_bh", "top_bh_poss"]
    df = df[cols]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_csv(OUT, index=False)
    pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40)
    print("\n=== GOBERT USAGE BY SEASON (warehouse) ===")
    print(df.to_string(index=False))
    # delivery-system detail
    print("\n=== Delivery system detail (teammates with >=150 PnR BH poss) ===")
    for _, r in deliv.iterrows():
        print(f"  {r['season_year']}: {r['deliv_meaningful']} meaningful / {r['deliv_primary']} primary | {r['bh_names']}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
