"""Q0B trajectory and contention window analysis.

Build a year-by-year projection of each Wolves rotation player's expected
production across 2025-26 through 2029-30, anchored on:
- Their current age and archetype
- Archetype age-curve norms (combo guards peak 26-29; defensive-anchor
  centers peak 27-31, decline visible after 32; modern wings peak 25-28+;
  combo bigs peak 26-30)
- Contract status (locked vs free agent vs option)

Output:
- Per-player year-by-year projected production tier
- Team-level contention window identification (when does the roster's
  expected aggregate production peak?)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lib import db


OUT_DIR = Path("outputs/tables/q0b_trajectory")
OUT_DIR.mkdir(parents=True, exist_ok=True)


# Wolves rotation: player_id, current age (2025-26), archetype, contract guarantee end year
WOLVES_ROTATION = {
    "Edwards":     {"player_id": 1630162, "age_2025_26": 24, "archetype": "star_guard", "guarantee_end": "2028-29"},
    "Gobert":      {"player_id": 203497, "age_2025_26": 33, "archetype": "defensive_anchor_center", "guarantee_end": "2026-27"},  # 2027-28 NG
    "Randle":      {"player_id": 203944, "age_2025_26": 31, "archetype": "combo_big", "guarantee_end": "2026-27"},  # 2027-28 NG, PO 2026-27
    "McDaniels":   {"player_id": 1630183, "age_2025_26": 25, "archetype": "wing", "guarantee_end": "2028-29"},
    "Naz Reid":    {"player_id": 1629675, "age_2025_26": 26, "archetype": "stretch_big", "guarantee_end": "2028-29"},
    "DiVincenzo":  {"player_id": 1628978, "age_2025_26": 29, "archetype": "two_way_guard", "guarantee_end": "2026-27"},  # FA 2027
    "Dosunmu":     {"player_id": 1630245, "age_2025_26": 26, "archetype": "wing_guard", "guarantee_end": "2025-26"},
    "Conley":      {"player_id": 201144, "age_2025_26": 38, "archetype": "veteran_pg", "guarantee_end": "2025-26"},
    "Clark":       {"player_id": 1641740, "age_2025_26": 24, "archetype": "wing", "guarantee_end": "2025-26"},
    "Beringer":    {"player_id": 1642866, "age_2025_26": 19, "archetype": "young_big", "guarantee_end": "2028-29"},
    "Shannon":     {"player_id": 1630545, "age_2025_26": 25, "archetype": "wing_guard", "guarantee_end": "2027-28"},
}


# Archetype age curves: expected production tier by age
# Tiers: "rising" (improving toward peak), "peak" (at career best), "stable_post_peak" (slightly past peak but still elite),
#        "declining" (visible decline), "late_decline" (significant decline)
ARCHETYPE_CURVES = {
    "star_guard": {
        22: "rising", 23: "rising", 24: "rising", 25: "rising_peak",
        26: "peak", 27: "peak", 28: "peak", 29: "peak",
        30: "stable_post_peak", 31: "stable_post_peak",
        32: "declining", 33: "declining", 34: "late_decline",
    },
    "defensive_anchor_center": {
        24: "rising", 25: "rising_peak", 26: "peak", 27: "peak", 28: "peak",
        29: "peak", 30: "stable_post_peak", 31: "stable_post_peak",
        32: "declining_visible", 33: "declining_visible", 34: "declining",
        35: "late_decline", 36: "late_decline",
    },
    "combo_big": {
        24: "rising", 25: "rising_peak", 26: "peak", 27: "peak", 28: "peak",
        29: "peak", 30: "stable_post_peak", 31: "stable_post_peak",
        32: "declining", 33: "declining", 34: "late_decline",
    },
    "wing": {
        22: "rising", 23: "rising", 24: "rising", 25: "rising_peak",
        26: "peak", 27: "peak", 28: "peak", 29: "peak",
        30: "stable_post_peak", 31: "stable_post_peak",
        32: "declining", 33: "declining",
    },
    "stretch_big": {
        24: "rising", 25: "rising", 26: "peak", 27: "peak", 28: "peak",
        29: "peak", 30: "stable_post_peak", 31: "stable_post_peak",
        32: "declining", 33: "declining",
    },
    "two_way_guard": {
        25: "rising", 26: "rising_peak", 27: "peak", 28: "peak", 29: "peak",
        30: "stable_post_peak", 31: "stable_post_peak",
        32: "declining", 33: "declining",
    },
    "wing_guard": {
        24: "rising", 25: "rising", 26: "rising_peak", 27: "peak", 28: "peak",
        29: "peak", 30: "stable_post_peak",
        31: "stable_post_peak", 32: "declining",
    },
    "veteran_pg": {
        32: "stable_post_peak", 33: "declining", 34: "declining",
        35: "late_decline", 36: "late_decline", 37: "late_decline",
        38: "late_decline", 39: "retire_zone",
    },
    "young_big": {
        18: "rookie", 19: "rookie", 20: "rookie", 21: "rising",
        22: "rising", 23: "rising", 24: "rising_peak", 25: "peak",
    },
}


# Tier -> production multiplier (relative to current production)
TIER_MULTIPLIER = {
    "rookie": 0.6, "rising": 1.0, "rising_peak": 1.1, "peak": 1.15,
    "stable_post_peak": 1.05, "declining_visible": 0.95, "declining": 0.85,
    "late_decline": 0.7, "retire_zone": 0.3,
}


def project_player_trajectory(player_info: dict, current_year: int = 2025,
                                 horizon: int = 5) -> list:
    """Project a player's production tier across the next horizon seasons."""
    arch = player_info["archetype"]
    curve = ARCHETYPE_CURVES.get(arch, {})
    age0 = player_info["age_2025_26"]
    rows = []
    for offset in range(horizon):
        season_year = current_year + offset
        season_label = f"{season_year}-{str(season_year + 1)[-2:]}"
        age = age0 + offset
        tier = curve.get(age, "out_of_curve")
        multiplier = TIER_MULTIPLIER.get(tier, 0.5)
        rows.append({
            "season_year": season_label,
            "season_start_year": season_year,
            "age": age,
            "tier": tier,
            "production_multiplier": multiplier,
        })
    return rows


def contract_status_at_year(player_info: dict, year_label: str) -> str:
    """For a given season label, return contract status: 'guaranteed', 'option', 'expiring', 'FA'."""
    guarantee_end = player_info["guarantee_end"]
    if year_label <= guarantee_end:
        return "guaranteed"
    # First year past guarantee
    if year_label == _next_season_after(guarantee_end):
        return "option/decision_point"
    return "FA_or_beyond"


def _next_season_after(season_label: str) -> str:
    y = int(season_label[:4])
    return f"{y+1}-{str(y+2)[-2:]}"


def build_team_trajectory(current_year: int = 2025, horizon: int = 5) -> pd.DataFrame:
    """Build the full team-level trajectory across all rotation players."""
    rows = []
    for name, info in WOLVES_ROTATION.items():
        traj = project_player_trajectory(info, current_year, horizon)
        for t in traj:
            rows.append({
                "player": name,
                "archetype": info["archetype"],
                "guarantee_end": info["guarantee_end"],
                **t,
                "contract_status": contract_status_at_year(info, t["season_year"]),
            })
    return pd.DataFrame(rows)


def team_aggregate(trajectory: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to team level by year.

    Compute a simple "expected contention strength" score: sum of multipliers
    weighted by player importance.
    """
    # Importance weights (rough): Edwards=4, Gobert=3, McDaniels=2.5,
    # Randle=2.5, Naz Reid=2, DiVincenzo=2, Conley=1, others=0.5
    importance = {
        "Edwards": 4.0, "Gobert": 3.0, "McDaniels": 2.5, "Randle": 2.5,
        "Naz Reid": 2.0, "DiVincenzo": 2.0, "Conley": 1.0, "Dosunmu": 0.7,
        "Clark": 0.5, "Beringer": 0.5, "Shannon": 0.5,
    }
    trajectory = trajectory.copy()
    trajectory["importance"] = trajectory["player"].map(importance)
    trajectory["weighted_contribution"] = (
        trajectory["production_multiplier"] * trajectory["importance"]
    )
    agg = trajectory.groupby(["season_year", "season_start_year"]).agg(
        team_score=("weighted_contribution", "sum"),
        n_guaranteed=("contract_status", lambda s: (s == "guaranteed").sum()),
        n_decision_points=("contract_status", lambda s: (s == "option/decision_point").sum()),
        n_FA=("contract_status", lambda s: (s == "FA_or_beyond").sum()),
    ).reset_index()
    return agg.sort_values("season_start_year")


def run():
    print("Q0B trajectory and contention window analysis\n")
    traj = build_team_trajectory(current_year=2025, horizon=5)
    print("=== Per-player trajectory ===")
    pivot = traj.pivot_table(index=["player", "archetype"], columns="season_year",
                                values="tier", aggfunc="first")
    print(pivot.to_string())
    traj.to_csv(OUT_DIR / "player_trajectories.csv", index=False)

    print("\n=== Per-player production multipliers ===")
    pivot_mult = traj.pivot_table(index=["player", "archetype"], columns="season_year",
                                     values="production_multiplier", aggfunc="first")
    print(pivot_mult.round(2).to_string())

    print("\n=== Per-player contract status ===")
    pivot_contract = traj.pivot_table(index="player", columns="season_year",
                                         values="contract_status", aggfunc="first")
    print(pivot_contract.to_string())

    print("\n=== Team aggregate contention score ===")
    agg = team_aggregate(traj)
    print(agg.round(2).to_string(index=False))
    agg.to_csv(OUT_DIR / "team_contention_scores.csv", index=False)

    # Identify peak window
    peak_year = agg.loc[agg["team_score"].idxmax(), "season_year"]
    print(f"\nPeak contention year (by aggregate score): {peak_year}")
    print(f"Peak score: {agg['team_score'].max():.2f}")
    print(f"\nYear-over-year deltas:")
    agg["delta"] = agg["team_score"].diff().round(2)
    print(agg[["season_year", "team_score", "delta"]].round(2).to_string(index=False))


if __name__ == "__main__":
    run()
