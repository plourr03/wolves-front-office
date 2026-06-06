"""Who was the Wolves' offensive center of gravity in 2024-25?

Article 2 ("How They Got Here") claims that in 2024-25 the offense became
"single-star pickup" and that "Randle was the new center of gravity, and the
architecture reorganized around him." That claim was inherited from the LAFI
deliverable's narrative. The Component 1 ball-stickiness eye-test, however,
lists Anthony Edwards as the top time-of-possession handler in 2024-25, not
Randle. This script settles which is right with data.

Three independent measures, Minnesota, Regular Season, 2023-24 -> 2025-26:

  1. Time of possession (tracking, measure 'Possessions'). Who literally holds
     the ball. This is the substrate of the LAFI ball-stickiness component.
  2. Touches, average seconds per touch, average dribbles per touch.
  3. On-ball creation volume (Synergy: Isolation + PRBallHandler + Postup raw
     possessions). Who carries the half-court creation load.

Re-runnable: python -m analyses.q0a_lafi.hub_check
"""
from __future__ import annotations

import pandas as pd

from lib import db

WOLVES = 1610612750
SEASONS = ["2023-24", "2024-25", "2025-26"]
ONBALL = ["Isolation", "PRBallHandler", "Postup"]

pd.set_option("display.width", 170)
pd.set_option("display.max_rows", 300)
pd.set_option("display.max_columns", 40)


def tracking_possessions() -> pd.DataFrame:
    ph = ",".join(["%s"] * len(SEASONS))
    sql = f"""
        SELECT season_year, player_name, gp, time_of_poss, touches,
               avg_sec_per_touch, avg_drib_per_touch
        FROM nba_player_tracking_season
        WHERE team_id = %s
          AND season_type = 'Regular Season'
          AND measure_type = 'Possessions'
          AND season_year IN ({ph})
    """
    df = db.query(sql, (WOLVES, *SEASONS))
    for c in ["gp", "time_of_poss", "touches", "avg_sec_per_touch", "avg_drib_per_touch"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def synergy_onball() -> pd.DataFrame:
    ph = ",".join(["%s"] * len(SEASONS))
    sql = f"""
        SELECT season_year, player_name, play_type, poss, ppp
        FROM nba_synergy_player_play_types
        WHERE team_id = %s
          AND season_type = 'Regular Season'
          AND type_grouping = 'Offensive'
          AND season_year IN ({ph})
    """
    df = db.query(sql, (WOLVES, *SEASONS))
    df["poss"] = pd.to_numeric(df["poss"], errors="coerce")
    df["ppp"] = pd.to_numeric(df["ppp"], errors="coerce")
    return df


def run() -> None:
    print("=== Hub check: who was the Wolves' center of gravity? ===\n")

    track = tracking_possessions()
    syn = synergy_onball()

    for season in SEASONS:
        print("\n" + "=" * 78)
        print(f"  {season} Regular Season")
        print("=" * 78)

        # ---- Time of possession leaderboard
        t = track[track["season_year"] == season].copy()
        team_top = t["time_of_poss"].sum()
        t["top_share_pct"] = 100.0 * t["time_of_poss"] / team_top
        t["top_per_g"] = t["time_of_poss"] / t["gp"]
        t["touch_per_g"] = t["touches"] / t["gp"]
        t = t.sort_values("time_of_poss", ascending=False)
        print("\n  Time of possession (tracking). Ranked. "
              "top_share_pct = share of team ball-handling time.")
        print(t[["player_name", "gp", "time_of_poss", "top_share_pct",
                 "top_per_g", "touch_per_g", "avg_sec_per_touch",
                 "avg_drib_per_touch"]]
              .head(8)
              .to_string(index=False,
                         float_format=lambda x: f"{x:.2f}"))

        # ---- On-ball creation volume (Synergy)
        s = syn[syn["season_year"] == season].copy()
        on = s[s["play_type"].isin(ONBALL)]
        piv = on.pivot_table(index="player_name", columns="play_type",
                             values="poss", aggfunc="sum").fillna(0)
        for pt in ONBALL:
            if pt not in piv.columns:
                piv[pt] = 0.0
        piv["onball_total"] = piv[ONBALL].sum(axis=1)
        piv = piv.sort_values("onball_total", ascending=False)
        print("\n  On-ball creation volume (Synergy raw possessions: "
              "Isolation + PRBallHandler + Postup).")
        print(piv[ONBALL + ["onball_total"]]
              .head(8)
              .to_string(float_format=lambda x: f"{x:.0f}"))


if __name__ == "__main__":
    run()
