"""
Exploratory: hit the NBA tracking endpoints with one Wolves playoff game and
one current season to see what each returns. NOT production code. Used to
decide which endpoints are worth ingesting into the warehouse.

Run:  python -m notebooks.tracking_endpoint_exploration
"""

from __future__ import annotations

import json
import sys
import time

import pandas as pd

# Wide pandas display so we can read the columns
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 30)

GAME_ID = "0042500235"   # MIN @ SAS, 2026-05-12, playoff R2 G5
SEASON  = "2025-26"


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def safe_endpoint(label: str, fn):
    """Run an endpoint call, catch any failure, print a short status line."""
    print(f"\n--- {label} ---")
    t0 = time.time()
    try:
        result = fn()
        elapsed = time.time() - t0
        print(f"  [ok in {elapsed:.1f}s]")
        return result
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  [FAILED in {elapsed:.1f}s: {type(e).__name__}: {e}]")
        return None


def show_frames(label: str, frames: dict[str, pd.DataFrame]) -> None:
    for name, df in frames.items():
        print(f"\n  Dataset '{name}': shape {df.shape}")
        print(f"  Columns ({len(df.columns)}): {list(df.columns)}")
        if len(df) > 0:
            print("  Head:")
            print(df.head(3).to_string(index=False))


# ------------------------------------------------------------------
# 1) BoxScorePlayerTrackV3 — per game, player and team level
# ------------------------------------------------------------------
section("1) BoxScorePlayerTrackV3 (per-game tracking)")

def call_boxscore_player_track_v3():
    from nba_api.stats.endpoints import boxscoreplayertrackv3
    return boxscoreplayertrackv3.BoxScorePlayerTrackV3(game_id=GAME_ID)

ep = safe_endpoint("BoxScorePlayerTrackV3 game_id=" + GAME_ID, call_boxscore_player_track_v3)
if ep is not None:
    show_frames("BoxScorePlayerTrackV3", {
        "player_stats": ep.player_stats.get_data_frame(),
        "team_stats":   ep.team_stats.get_data_frame(),
    })


# ------------------------------------------------------------------
# 2) LeagueDashPtStats — season aggregates by PtMeasureType
# ------------------------------------------------------------------
section("2) LeagueDashPtStats — season-aggregate tracking by measure type")

PT_MEASURES = [
    "Possessions",   # time of possession per player — critical for LAFI Component 1
    "CatchShoot",    # catch-and-shoot only — critical for LAFI Component 5
    "PullUpShot",    # pull-up shots only — critical for LAFI Component 5
    "Drives",        # drives per game — for Q3a
    "Defense",       # defensive metrics — for Q3c
    "Passing",       # pass details — supplements Ball Stickiness
    "ElbowTouch",    # touch location splits
    "PostTouch",
    "PaintTouch",
]


def call_league_dash_pt_stats(pt_measure_type: str):
    from nba_api.stats.endpoints import leaguedashptstats
    return leaguedashptstats.LeagueDashPtStats(
        pt_measure_type=pt_measure_type,
        player_or_team="Player",
        season=SEASON,
        season_type_all_star="Regular Season",
    )


for measure in PT_MEASURES[:3]:  # only the top 3 to keep the test short
    ep = safe_endpoint(f"LeagueDashPtStats pt_measure_type={measure}", lambda m=measure: call_league_dash_pt_stats(m))
    if ep is not None:
        try:
            df = ep.league_dash_pt_stats.get_data_frame()
        except AttributeError:
            df = ep.get_data_frames()[0]
        print(f"  shape: {df.shape}")
        print(f"  columns ({len(df.columns)}): {list(df.columns)}")
        if len(df) > 0:
            print("  Wolves player rows:")
            mn = df[df["TEAM_ABBREVIATION"] == "MIN"]
            print(mn.head(5).to_string(index=False))


# ------------------------------------------------------------------
# 3) LeagueDashPtShots — defender-distance buckets
# ------------------------------------------------------------------
section("3) LeagueDashPtShots (defender-distance buckets)")

def call_league_dash_pt_shots():
    from nba_api.stats.endpoints import leaguedashptshots
    return leaguedashptshots.LeagueDashPtShots(
        player_or_team="Player",
        season=SEASON,
        season_type_all_star="Regular Season",
    )

ep = safe_endpoint("LeagueDashPtShots", call_league_dash_pt_shots)
if ep is not None:
    try:
        df = ep.get_data_frames()[0]
    except Exception as e:
        print(f"  could not extract frame: {e}")
        df = None
    if df is not None:
        print(f"  shape: {df.shape}")
        print(f"  columns ({len(df.columns)}): {list(df.columns)}")
        if len(df) > 0:
            mn = df[df["TEAM_ABBREVIATION"] == "MIN"] if "TEAM_ABBREVIATION" in df.columns else df.head(5)
            print("  Wolves rows (head 5):")
            print(mn.head(5).to_string(index=False))


# ------------------------------------------------------------------
# 4) SynergyPlayTypes — play-type frequencies and PPP
# ------------------------------------------------------------------
section("4) SynergyPlayTypes (play-type frequencies)")

SYNERGY_TYPES = [
    "Isolation", "PRBallHandler", "PRRollman", "PostUp",
    "Spotup", "Handoff", "OffScreen", "Cut", "Transition",
]


def call_synergy(play_type: str):
    from nba_api.stats.endpoints import synergyplaytypes
    return synergyplaytypes.SynergyPlayTypes(
        season=SEASON,
        season_type_all_star="Regular Season",
        play_type_nullable=play_type,
        player_or_team_abbreviation="T",  # team-level
        type_grouping_nullable="offensive",
    )


for pt in SYNERGY_TYPES[:3]:
    ep = safe_endpoint(f"SynergyPlayTypes play_type={pt} (team, offensive)", lambda p=pt: call_synergy(p))
    if ep is not None:
        try:
            df = ep.get_data_frames()[0]
        except Exception as e:
            print(f"  could not extract frame: {e}")
            continue
        print(f"  shape: {df.shape}")
        print(f"  columns ({len(df.columns)}): {list(df.columns)}")
        if len(df) > 0:
            print("  Wolves row + top-3 league rows:")
            mn = df[df["TEAM_ABBREVIATION"] == "MIN"] if "TEAM_ABBREVIATION" in df.columns else pd.DataFrame()
            top = df.sort_values("POSS", ascending=False).head(3) if "POSS" in df.columns else df.head(3)
            print(pd.concat([mn, top]).drop_duplicates().to_string(index=False))


print("\n\nDONE.")
