"""Q3 v1: Edwards shot diet decomposition (Spurs series vs Denver series vs RS).

Focused on the central Q3 question: what did the Spurs specifically do to
Edwards' shot diet vs other opponents.

Method (action-classifier-free v1):
1. Pull Edwards' per-shot data from nba_shot_chart_detail
2. Classify each shot by zone, distance, action_type, made/missed
3. Aggregate by opponent series for the 2025-26 PO
4. Compare to 2025-26 RS baseline and to 2024-25 PO

Key questions:
- Was Edwards' shot distance distribution shifted vs the Spurs?
- Was his 3PA volume specifically suppressed?
- Were his pull-up vs catch-and-shoot shares different?
- Did certain action_types disappear (e.g., spot-up threes vs pull-up threes)?
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import db


EDWARDS_ID = 1630162
WOLVES_TEAM_ID = 1610612750
OUT_DIR = Path("outputs/tables/q3_mechanism")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def pull_edwards_shots(season_years=("2024-25", "2025-26")) -> pd.DataFrame:
    placeholders = ",".join(["%s"] * len(season_years))
    sql = f"""
        SELECT scd.game_id, scd.game_date, scd.period,
               scd.minutes_remaining, scd.seconds_remaining,
               scd.event_type, scd.action_type, scd.shot_type,
               scd.shot_zone_basic, scd.shot_zone_area, scd.shot_zone_range,
               scd.shot_distance, scd.shot_attempted_flag, scd.shot_made_flag,
               scd.season_year, scd.season_type, scd.htm, scd.vtm,
               g.matchup
        FROM nba_shot_chart_detail scd
        LEFT JOIN nba_games g ON g.game_id = scd.game_id AND g.team_id = scd.team_id
        WHERE scd.player_id = %s
          AND scd.season_year IN ({placeholders})
        ORDER BY scd.season_year, scd.game_date, scd.game_id, scd.period DESC
    """
    df = db.query(sql, (EDWARDS_ID, *season_years))
    df["game_date"] = pd.to_datetime(df["game_date"])
    return df


def classify_opponent(matchup: str) -> str:
    """Return opponent abbr from matchup string."""
    if not isinstance(matchup, str):
        return "UNK"
    # 'MIN vs. DEN' or 'MIN @ DEN'
    parts = matchup.replace("vs.", "").replace("@", "").split()
    parts = [p for p in parts if p != "MIN" and p.isupper() and len(p) == 3]
    return parts[0] if parts else "UNK"


def classify_action(action_type: str) -> str:
    """Coarse classification of Edwards' action types into shot diet buckets."""
    if not isinstance(action_type, str):
        return "Other"
    a = action_type.lower()
    if "pullup" in a or "pull-up" in a or "step back" in a:
        return "Pull-up"
    if "catch" in a:
        return "Catch-and-shoot"
    if "driving" in a or "drive" in a or "running layup" in a or "cutting" in a:
        return "Driving/Cutting"
    if "fadeaway" in a or "turnaround" in a:
        return "Fadeaway/Post"
    if "jump shot" in a:
        # Generic jump shot - common for catch-and-shoot off-ball
        return "Generic jump shot"
    if "dunk" in a:
        return "Dunk"
    if "layup" in a:
        return "Layup"
    if "tip" in a or "putback" in a:
        return "Putback/Tip"
    return "Other"


def summarize_by_opponent_phase(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate Edwards' shooting by opponent phase (RS, R1 DEN, R2 SAS for 2025-26 PO)."""
    df = df.copy()
    df["opp"] = df["matchup"].apply(classify_opponent)
    df["shot_attempted_flag"] = pd.to_numeric(df["shot_attempted_flag"], errors="coerce")
    df["shot_made_flag"] = pd.to_numeric(df["shot_made_flag"], errors="coerce")
    df["is_three"] = (df["shot_type"].astype(str).str.contains("3PT", na=False)).astype(int)
    df["shot_distance"] = pd.to_numeric(df["shot_distance"], errors="coerce")

    # Phase classifier
    def phase(row):
        if row["season_year"] == "2025-26" and row["season_type"] == "Playoffs":
            if row["opp"] == "DEN":
                return "25-26 PO R1 DEN"
            elif row["opp"] == "SAS":
                return "25-26 PO R2 SAS"
            else:
                return "25-26 PO Other"
        if row["season_year"] == "2025-26" and row["season_type"] == "Regular Season":
            return "25-26 RS"
        if row["season_year"] == "2024-25" and row["season_type"] == "Playoffs":
            return "24-25 PO"
        if row["season_year"] == "2024-25" and row["season_type"] == "Regular Season":
            return "24-25 RS"
        return "Other"

    df["phase"] = df.apply(phase, axis=1)
    return df


def shot_zone_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Per phase, fraction of shots in each zone + 3PA rate + eFG."""
    rows = []
    for phase in df["phase"].unique():
        sub = df[df["phase"] == phase]
        if sub.empty:
            continue
        total = len(sub)
        zones = sub.groupby("shot_zone_basic").size().to_dict()
        threes = int(sub["is_three"].sum())
        makes = int(sub["shot_made_flag"].sum())
        three_makes = int(((sub["is_three"] == 1) & (sub["shot_made_flag"] == 1)).sum())
        twos_makes = makes - three_makes
        efg = (twos_makes + 1.5 * three_makes) / total if total else np.nan
        avg_dist = sub["shot_distance"].mean()
        row = {
            "phase": phase,
            "games": sub["game_id"].nunique(),
            "fga": total,
            "fg3a": threes,
            "fgm": makes,
            "fg3m": three_makes,
            "fga_per_game": total / sub["game_id"].nunique() if sub["game_id"].nunique() else 0,
            "fg3a_per_game": threes / sub["game_id"].nunique() if sub["game_id"].nunique() else 0,
            "3pa_rate": threes / total if total else 0,
            "fg_pct": makes / total if total else 0,
            "fg3_pct": three_makes / threes if threes else 0,
            "efg": efg,
            "avg_distance": avg_dist,
        }
        for zone, count in zones.items():
            row[f"zone_{zone}"] = count / total
        rows.append(row)
    return pd.DataFrame(rows)


def action_type_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Per phase, distribution of action types (pull-up / driving / catch-and-shoot)."""
    df = df.copy()
    df["action_bucket"] = df["action_type"].apply(classify_action)
    rows = []
    for phase in df["phase"].unique():
        sub = df[df["phase"] == phase]
        if sub.empty:
            continue
        n = len(sub)
        buckets = sub.groupby("action_bucket").size().to_dict()
        row = {"phase": phase, "total_fga": n,
                "games": sub["game_id"].nunique()}
        for b, c in buckets.items():
            row[f"{b}_pct"] = c / n
            row[f"{b}_count"] = c
        rows.append(row)
    return pd.DataFrame(rows)


def shot_distance_buckets(df: pd.DataFrame) -> pd.DataFrame:
    """Per phase, distribution by shot distance bucket."""
    df = df.copy()
    def dist_bucket(d):
        if pd.isna(d):
            return "Unknown"
        if d <= 3:
            return "0-3 ft (rim)"
        if d <= 10:
            return "4-10 ft (paint)"
        if d <= 16:
            return "11-16 ft (short mid)"
        if d <= 22:
            return "17-22 ft (long mid)"
        if d <= 25:
            return "23-25 ft (3pt)"
        return "26+ ft (deep 3)"

    df["dist_bucket"] = df["shot_distance"].apply(dist_bucket)
    rows = []
    for phase in df["phase"].unique():
        sub = df[df["phase"] == phase]
        if sub.empty:
            continue
        n = len(sub)
        bucket_counts = sub.groupby("dist_bucket").size().to_dict()
        row = {"phase": phase, "total": n, "games": sub["game_id"].nunique()}
        for b in ["0-3 ft (rim)", "4-10 ft (paint)", "11-16 ft (short mid)",
                   "17-22 ft (long mid)", "23-25 ft (3pt)", "26+ ft (deep 3)"]:
            row[f"{b}_pct"] = bucket_counts.get(b, 0) / n
            row[f"{b}_count"] = bucket_counts.get(b, 0)
        rows.append(row)
    return pd.DataFrame(rows)


def run():
    print("Pulling Edwards' shot chart data for 2024-25 and 2025-26...")
    df = pull_edwards_shots()
    df = summarize_by_opponent_phase(df)
    print(f"  {len(df)} shots across {df['game_id'].nunique()} games")
    print(f"  Phase distribution:")
    print(df.groupby("phase").size().to_string())

    # Zone breakdown
    print("\n=== Shot zone breakdown by phase ===")
    zone = shot_zone_breakdown(df)
    # Reorder phases manually for narrative
    order = ["24-25 RS", "24-25 PO", "25-26 RS", "25-26 PO R1 DEN", "25-26 PO R2 SAS"]
    zone["sort"] = zone["phase"].apply(lambda p: order.index(p) if p in order else 99)
    zone = zone.sort_values("sort").drop(columns=["sort"])
    print(zone[["phase", "games", "fga", "fga_per_game", "fg3a_per_game",
                  "3pa_rate", "fg_pct", "fg3_pct", "efg", "avg_distance"]].round(3).to_string(index=False))
    zone.to_csv(OUT_DIR / "edwards_shot_zone_by_phase.csv", index=False)

    # Action type breakdown
    print("\n=== Action type breakdown by phase (% of shots) ===")
    act = action_type_breakdown(df)
    act["sort"] = act["phase"].apply(lambda p: order.index(p) if p in order else 99)
    act = act.sort_values("sort").drop(columns=["sort"])
    pct_cols = [c for c in act.columns if c.endswith("_pct")]
    print(act[["phase", "games", "total_fga"] + pct_cols].round(3).to_string(index=False))
    act.to_csv(OUT_DIR / "edwards_action_type_by_phase.csv", index=False)

    # Distance buckets
    print("\n=== Shot distance bucket distribution ===")
    dist = shot_distance_buckets(df)
    dist["sort"] = dist["phase"].apply(lambda p: order.index(p) if p in order else 99)
    dist = dist.sort_values("sort").drop(columns=["sort"])
    print(dist[["phase", "games", "total"] +
                [c for c in dist.columns if c.endswith("_pct")]].round(3).to_string(index=False))
    dist.to_csv(OUT_DIR / "edwards_distance_buckets_by_phase.csv", index=False)


if __name__ == "__main__":
    run()
