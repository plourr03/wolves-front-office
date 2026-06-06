"""Q0D play type evolution: how has the Wolves' offensive shape changed?

Focuses on three things:

1. Team play-type frequency evolution 2022-23 → 2025-26 (4 seasons)
2. Gobert's individual play-type role decomposition over those years
3. Allocation restoration impact: what would the team's expected ORtg be
   if 2025-26 personnel played the 2023-24 allocation?

Caveats:
- Synergy poss_pct sums to slightly less than 100% per side (some possessions
  are unclassified Misc). Treat percentages as approximate.
- "PPP" varies by play type; the restoration projection assumes the team
  can execute the alternative allocation at its current PPP per play type.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import db


OUT_DIR = Path("outputs/tables/q0d_coaching_system")
OUT_DIR.mkdir(parents=True, exist_ok=True)

WOLVES_TEAM_ID = 1610612750
GOBERT_ID = 203497
RANDLE_ID = 203944
EDWARDS_ID = 1630162

PLAY_TYPES = ["Cut", "Handoff", "Isolation", "Misc", "OffRebound", "OffScreen",
              "Postup", "PRBallHandler", "PRRollMan", "Spotup", "Transition"]

DESIGNED_TYPES = ["Cut", "OffScreen", "Handoff", "PRBallHandler", "PRRollMan", "Spotup"]
INDIVIDUAL_TYPES = ["Isolation", "Postup"]


def load_team_play_types(seasons=("2022-23", "2023-24", "2024-25", "2025-26"),
                          season_type="Regular Season",
                          team_id=WOLVES_TEAM_ID) -> pd.DataFrame:
    placeholders = ",".join(["%s"] * len(seasons))
    sql = f"""
        SELECT season_year, season_type, play_type, type_grouping,
               poss_pct, ppp, poss, fg_pct, efg_pct, percentile
        FROM nba_synergy_team_play_types
        WHERE team_id = %s
          AND season_year IN ({placeholders})
          AND season_type = %s
        ORDER BY season_year, play_type
    """
    df = db.query(sql, (team_id, *seasons, season_type))
    for c in ("poss_pct", "ppp", "fg_pct", "efg_pct"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["poss"] = pd.to_numeric(df["poss"], errors="coerce")
    return df


def load_player_play_types(player_id: int,
                             seasons=("2022-23", "2023-24", "2024-25", "2025-26"),
                             season_type="Regular Season") -> pd.DataFrame:
    placeholders = ",".join(["%s"] * len(seasons))
    sql = f"""
        SELECT season_year, season_type, play_type, type_grouping,
               poss_pct, ppp, poss, fg_pct, efg_pct, percentile
        FROM nba_synergy_player_play_types
        WHERE player_id = %s
          AND season_year IN ({placeholders})
          AND season_type = %s
        ORDER BY season_year, play_type
    """
    df = db.query(sql, (player_id, *seasons, season_type))
    for c in ("poss_pct", "ppp", "fg_pct", "efg_pct"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["poss"] = pd.to_numeric(df["poss"], errors="coerce")
    return df


def team_offensive_allocation(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot: rows = play_type, columns = season, values = offensive poss_pct."""
    off = df[df["type_grouping"] == "Offensive"].copy()
    return off.pivot_table(index="play_type", columns="season_year",
                            values="poss_pct", aggfunc="mean")


def team_offensive_ppp(df: pd.DataFrame) -> pd.DataFrame:
    off = df[df["type_grouping"] == "Offensive"].copy()
    return off.pivot_table(index="play_type", columns="season_year",
                            values="ppp", aggfunc="mean")


def designed_vs_individual(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate poss_pct by 'designed' vs 'individual' play types per season."""
    off = df[df["type_grouping"] == "Offensive"].copy()
    pivot = off.pivot_table(index="season_year", columns="play_type",
                              values="poss_pct", aggfunc="mean").fillna(0)
    rows = []
    for season in pivot.index:
        designed = sum(pivot.loc[season, p] for p in DESIGNED_TYPES if p in pivot.columns)
        individual = sum(pivot.loc[season, p] for p in INDIVIDUAL_TYPES if p in pivot.columns)
        off_ball_motion = sum(pivot.loc[season, p] for p in ["Cut", "OffScreen"] if p in pivot.columns)
        pnr_total = sum(pivot.loc[season, p] for p in ["PRBallHandler", "PRRollMan"] if p in pivot.columns)
        rows.append({
            "season": season,
            "designed_pct": designed,
            "individual_pct": individual,
            "off_ball_motion_pct": off_ball_motion,
            "pnr_total_pct": pnr_total,
            "iso_pct": pivot.loc[season, "Isolation"] if "Isolation" in pivot.columns else np.nan,
            "postup_pct": pivot.loc[season, "Postup"] if "Postup" in pivot.columns else np.nan,
            "cut_pct": pivot.loc[season, "Cut"] if "Cut" in pivot.columns else np.nan,
            "offscreen_pct": pivot.loc[season, "OffScreen"] if "OffScreen" in pivot.columns else np.nan,
            "prballhandler_pct": pivot.loc[season, "PRBallHandler"] if "PRBallHandler" in pivot.columns else np.nan,
            "prrollman_pct": pivot.loc[season, "PRRollMan"] if "PRRollMan" in pivot.columns else np.nan,
            "spotup_pct": pivot.loc[season, "Spotup"] if "Spotup" in pivot.columns else np.nan,
            "transition_pct": pivot.loc[season, "Transition"] if "Transition" in pivot.columns else np.nan,
        })
    return pd.DataFrame(rows)


def allocation_restoration_impact(team_df: pd.DataFrame,
                                     reference_season: str = "2023-24",
                                     current_season: str = "2025-26") -> dict:
    """Project the offensive rating impact of holding current personnel's PPP
    per play type but applying the reference season's allocation.

    Method:
      For each offensive play type p:
        delta_pct_p = ref_pct_p - cur_pct_p
        contribution_p = delta_pct_p * (cur_ppp_p - cur_baseline)
      where cur_baseline = current season's weighted PPP across all play types

    Expected ORtg change = sum over p of (delta_pct_p * cur_ppp_p) * 100
                          minus (current allocation's weighted PPP) * 100
    Simpler version: compute weighted PPP under current allocation, compute
    weighted PPP under reference allocation (with current PPPs), subtract.
    """
    off = team_df[team_df["type_grouping"] == "Offensive"].copy()
    ref = off[off["season_year"] == reference_season].set_index("play_type")
    cur = off[off["season_year"] == current_season].set_index("play_type")

    if ref.empty or cur.empty:
        return {"error": "Missing season data"}

    # Use current PPPs throughout; only the allocation differs
    rows = []
    cur_weighted_ppp = 0.0
    ref_weighted_ppp = 0.0
    total_ref_pct = 0.0
    total_cur_pct = 0.0
    for pt in PLAY_TYPES:
        if pt not in ref.index or pt not in cur.index:
            continue
        ref_pct = float(ref.loc[pt, "poss_pct"]) if pd.notna(ref.loc[pt, "poss_pct"]) else 0
        cur_pct = float(cur.loc[pt, "poss_pct"]) if pd.notna(cur.loc[pt, "poss_pct"]) else 0
        cur_ppp = float(cur.loc[pt, "ppp"]) if pd.notna(cur.loc[pt, "ppp"]) else 0
        ref_ppp = float(ref.loc[pt, "ppp"]) if pd.notna(ref.loc[pt, "ppp"]) else 0
        cur_weighted_ppp += cur_pct * cur_ppp
        ref_weighted_ppp += ref_pct * cur_ppp  # USE CURRENT PPP UNDER REF ALLOCATION
        total_ref_pct += ref_pct
        total_cur_pct += cur_pct
        rows.append({
            "play_type": pt,
            "ref_pct": ref_pct,
            "cur_pct": cur_pct,
            "delta_pct": ref_pct - cur_pct,
            "cur_ppp": cur_ppp,
            "ref_ppp": ref_ppp,
            "contribution_to_delta_ortg": (ref_pct - cur_pct) * cur_ppp,
        })

    detail = pd.DataFrame(rows)
    # ORtg = points per 100 possessions. PPP is points per possession.
    # So delta_PPP * 100 = delta_ORtg (points per 100 possessions).
    expected_ortg_change_points = (ref_weighted_ppp - cur_weighted_ppp) * 100

    return {
        "reference_season": reference_season,
        "current_season": current_season,
        "cur_weighted_ppp": cur_weighted_ppp,
        "ref_weighted_ppp_at_cur_efficiency": ref_weighted_ppp,
        "expected_ortg_change_points": expected_ortg_change_points,
        "total_ref_pct": total_ref_pct,
        "total_cur_pct": total_cur_pct,
        "detail": detail,
    }


def run():
    print("=== Q0D play type evolution analysis ===\n")

    # ---- Team-level evolution
    print("Loading Wolves team play types (4 seasons RS)...")
    team = load_team_play_types()
    print(f"  {len(team)} rows")

    print("\n=== Team offensive allocation by season (percent of possessions) ===")
    alloc = team_offensive_allocation(team)
    print(alloc.round(3).to_string())
    alloc.to_csv(OUT_DIR / "team_allocation_by_season.csv")

    print("\n=== Team offensive PPP by play type by season ===")
    ppp = team_offensive_ppp(team)
    print(ppp.round(3).to_string())
    ppp.to_csv(OUT_DIR / "team_ppp_by_season.csv")

    print("\n=== Designed vs individual play type aggregation ===")
    dvi = designed_vs_individual(team)
    print(dvi.round(3).to_string(index=False))
    dvi.to_csv(OUT_DIR / "designed_vs_individual.csv", index=False)

    # ---- Allocation restoration impact (2023-24 → 2025-26)
    print("\n=== Allocation restoration impact: 2025-26 personnel + 2023-24 allocation ===")
    impact = allocation_restoration_impact(team, "2023-24", "2025-26")
    print(f"Current (2025-26) weighted PPP: {impact['cur_weighted_ppp']:.4f}")
    print(f"Restored (2023-24 alloc, current PPP): {impact['ref_weighted_ppp_at_cur_efficiency']:.4f}")
    print(f"Expected ORtg change: {impact['expected_ortg_change_points']:+.2f} points per 100 possessions")
    print(f"\nDetail (play-type contribution):")
    print(impact["detail"].round(4).to_string(index=False))
    impact["detail"].to_csv(OUT_DIR / "allocation_restoration_impact.csv", index=False)

    # ---- Also do 2024-25 → 2025-26 to isolate the post-KAT vs post-DiVi-injury shift
    print("\n=== Allocation restoration: 2025-26 personnel + 2024-25 allocation ===")
    impact_24 = allocation_restoration_impact(team, "2024-25", "2025-26")
    print(f"Expected ORtg change: {impact_24['expected_ortg_change_points']:+.2f} points per 100 possessions")
    impact_24["detail"].to_csv(OUT_DIR / "allocation_restoration_2024to2025.csv", index=False)

    # ---- Gobert's individual role decomposition
    print("\n=== Gobert's individual play type role across seasons ===")
    gobert = load_player_play_types(GOBERT_ID)
    gobert_off = gobert[gobert["type_grouping"] == "Offensive"]
    gob_alloc = gobert_off.pivot_table(index="play_type", columns="season_year",
                                          values="poss_pct", aggfunc="mean")
    gob_poss = gobert_off.pivot_table(index="play_type", columns="season_year",
                                        values="poss", aggfunc="mean")
    gob_ppp = gobert_off.pivot_table(index="play_type", columns="season_year",
                                       values="ppp", aggfunc="mean")
    print("\nFrequency (poss_pct) - share of Gobert's own offensive possessions:")
    print(gob_alloc.round(3).to_string())
    print("\nVolume (raw possessions):")
    print(gob_poss.round(0).to_string())
    print("\nPPP per play type:")
    print(gob_ppp.round(3).to_string())
    gob_alloc.to_csv(OUT_DIR / "gobert_play_type_freq.csv")
    gob_poss.to_csv(OUT_DIR / "gobert_play_type_poss.csv")
    gob_ppp.to_csv(OUT_DIR / "gobert_play_type_ppp.csv")

    # ---- Also Randle, Edwards (so we can compare KAT-era to Randle-era)
    print("\n=== Randle's individual play type frequency by season ===")
    randle = load_player_play_types(RANDLE_ID)
    randle_off = randle[randle["type_grouping"] == "Offensive"]
    randle_alloc = randle_off.pivot_table(index="play_type", columns="season_year",
                                            values="poss_pct", aggfunc="mean")
    print(randle_alloc.round(3).to_string())
    randle_alloc.to_csv(OUT_DIR / "randle_play_type_freq.csv")

    print("\n=== Edwards' individual play type frequency by season ===")
    edwards = load_player_play_types(EDWARDS_ID)
    edwards_off = edwards[edwards["type_grouping"] == "Offensive"]
    edwards_alloc = edwards_off.pivot_table(index="play_type", columns="season_year",
                                              values="poss_pct", aggfunc="mean")
    print(edwards_alloc.round(3).to_string())
    edwards_alloc.to_csv(OUT_DIR / "edwards_play_type_freq.csv")


if __name__ == "__main__":
    run()
