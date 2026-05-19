"""
Probe the deferred tracking endpoints to see which work and what they return.

Targets:
  LeagueDashPlayerPtShot     - the endpoint I called PtShots; player-level
  LeagueDashTeamPtShot       - team-level version
  LeagueDashOppPtShot        - opponent shots allowed
  LeagueDashPtDefend         - defender vs shots (no matchup data, just shot
                                defense metrics per player)
  LeagueDashPtTeamDefend     - team-level analog
  LeagueDashPlayerShotLocations  - zone breakdowns (RA, paint non-RA, etc.)
  BoxScoreMatchupsV3         - per-game matchup pairs
  PlayerDashPtShotDefend     - per-player shot defense detail
"""

from __future__ import annotations

import time

import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

SEASON = "2025-26"
GAME_ID = "0042500235"


def try_endpoint(label: str, fn):
    print(f"\n=== {label} ===")
    t0 = time.time()
    try:
        obj = fn()
        elapsed = time.time() - t0
        # Different endpoints expose data via different attribute names.
        try:
            dfs = obj.get_data_frames()
        except Exception:
            dfs = []
        print(f"  ok in {elapsed:.1f}s, {len(dfs)} dataset(s)")
        for i, df in enumerate(dfs):
            print(f"  dataset[{i}]: shape {df.shape}")
            print(f"    cols ({len(df.columns)}): {list(df.columns)}")
            if len(df) and "TEAM_ABBREVIATION" in df.columns:
                mn = df[df["TEAM_ABBREVIATION"] == "MIN"]
                if len(mn):
                    print("    MIN head:")
                    print(mn.head(3).to_string(index=False))
            elif len(df):
                print("    head:")
                print(df.head(3).to_string(index=False))
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  FAILED in {elapsed:.1f}s: {type(e).__name__}: {e}")


# 1) LeagueDashPlayerPtShot — the misnamed one
def t1():
    from nba_api.stats.endpoints import leaguedashplayerptshot
    return leaguedashplayerptshot.LeagueDashPlayerPtShot(
        season=SEASON, season_type_all_star="Regular Season",
    )
try_endpoint("LeagueDashPlayerPtShot", t1)


# 2) LeagueDashTeamPtShot — team-level
def t2():
    from nba_api.stats.endpoints import leaguedashteamptshot
    return leaguedashteamptshot.LeagueDashTeamPtShot(
        season=SEASON, season_type_all_star="Regular Season",
    )
try_endpoint("LeagueDashTeamPtShot", t2)


# 3) LeagueDashOppPtShot — opponent shots allowed
def t3():
    from nba_api.stats.endpoints import leaguedashoppptshot
    return leaguedashoppptshot.LeagueDashOppPtShot(
        season=SEASON, season_type_all_star="Regular Season",
    )
try_endpoint("LeagueDashOppPtShot", t3)


# 4) LeagueDashPtDefend — player defensive matchup stats
def t4():
    from nba_api.stats.endpoints import leaguedashptdefend
    return leaguedashptdefend.LeagueDashPtDefend(
        season=SEASON, season_type_all_star="Regular Season",
    )
try_endpoint("LeagueDashPtDefend", t4)


# 5) LeagueDashPtTeamDefend — team defensive
def t5():
    from nba_api.stats.endpoints import leaguedashptteamdefend
    return leaguedashptteamdefend.LeagueDashPtTeamDefend(
        season=SEASON, season_type_all_star="Regular Season",
    )
try_endpoint("LeagueDashPtTeamDefend", t5)


# 6) LeagueDashPlayerShotLocations — zone breakdowns
def t6():
    from nba_api.stats.endpoints import leaguedashplayershotlocations
    return leaguedashplayershotlocations.LeagueDashPlayerShotLocations(
        season=SEASON, season_type_all_star="Regular Season",
    )
try_endpoint("LeagueDashPlayerShotLocations", t6)


# 7) BoxScoreMatchupsV3 — per-game matchup pairs
def t7():
    from nba_api.stats.endpoints import boxscorematchupsv3
    return boxscorematchupsv3.BoxScoreMatchupsV3(game_id=GAME_ID)
try_endpoint("BoxScoreMatchupsV3", t7)


# 8) PlayerDashPtShotDefend — per-player shot defense detail
def t8():
    from nba_api.stats.endpoints import playerdashptshotdefend
    # Anthony Edwards player_id from our DB or just try
    return playerdashptshotdefend.PlayerDashPtShotDefend(
        player_id=1630162,
        team_id=1610612750,
        season=SEASON,
        season_type_all_star="Regular Season",
    )
try_endpoint("PlayerDashPtShotDefend (Anthony Edwards)", t8)


print("\nDONE")
