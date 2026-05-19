"""Q0C v1 historical cohort analysis.

Scope-capped question: Are there historical teams with similar architectural
profiles to the 2025-26 Wolves, and if so, what happened to them?

Simple cohort definition (v1):
  Sharp LAFI >= 80 percentile AND
  C1 ball stickiness < 50 (Q4 placement: distributed, not single-star pickup) AND
  C2 movement death > 50 (Q4 placement: dead off-ball motion)
  Regular Season only.

For each cohort team: pull RS record, playoff appearance, playoff round reached.
Identify pattern.

Output:
  outputs/tables/q0c_historical_cohort/cohort_with_outcomes.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from lib import db


OUT_DIR = Path("outputs/tables/q0c_historical_cohort")
OUT_DIR.mkdir(parents=True, exist_ok=True)


COHORT_FILTERS = {
    "sharp_lafi_pct_min": 80.0,
    "c1_ball_stickiness_pct_max": 50.0,
    "c2_movement_death_pct_min": 50.0,
}


def load_lafi() -> pd.DataFrame:
    df = pd.read_csv("outputs/tables/q0a_lafi/lafi_composite_5component.csv")
    df = df[df["season_type"] == "Regular Season"].copy()
    return df


def define_cohort(lafi: pd.DataFrame) -> pd.DataFrame:
    cohort = lafi[
        (lafi["sharp_lafi_pct"] >= COHORT_FILTERS["sharp_lafi_pct_min"]) &
        (lafi["C1_ball_stickiness_pct"] < COHORT_FILTERS["c1_ball_stickiness_pct_max"]) &
        (lafi["C2_movement_death_pct"] > COHORT_FILTERS["c2_movement_death_pct_min"])
    ].copy()
    cohort = cohort.sort_values("sharp_lafi_pct", ascending=False)
    return cohort


def pull_outcomes(cohort: pd.DataFrame) -> pd.DataFrame:
    """For each (team_id, season_start_year) in the cohort, pull RS record and
    playoff results from nba_games."""
    rows = []
    for _, r in cohort.iterrows():
        team_id = r["team_id"]
        season_start = int(r["season_start_year"])
        season_id_rs = 20000 + season_start
        season_id_po = 40000 + season_start

        rs = db.query("""
            SELECT COUNT(*) AS gp, SUM(CASE WHEN wl='W' THEN 1 ELSE 0 END) AS wins
            FROM nba.nba_games
            WHERE team_id = %(team_id)s AND season_id = %(season_id)s
        """, {"team_id": int(team_id), "season_id": season_id_rs})
        po = db.query("""
            SELECT COUNT(*) AS gp, SUM(CASE WHEN wl='W' THEN 1 ELSE 0 END) AS wins
            FROM nba.nba_games
            WHERE team_id = %(team_id)s AND season_id = %(season_id)s
        """, {"team_id": int(team_id), "season_id": season_id_po})

        rs_gp = int(rs.iloc[0]["gp"]) if not rs.empty else 0
        rs_w = int(rs.iloc[0]["wins"]) if not rs.empty and rs.iloc[0]["wins"] is not None else 0
        po_gp = int(po.iloc[0]["gp"]) if not po.empty else 0
        po_w = int(po.iloc[0]["wins"]) if not po.empty and po.iloc[0]["wins"] is not None else 0

        # Round reached: 0 games = missed, 4-6 wins = R1 (best of 7), etc.
        # NBA playoff structure: R1 = first 4-7 games, R2 = next 4-7, etc.
        # Use cumulative wins to infer round.
        if po_gp == 0:
            outcome = "missed"
        elif po_w < 4:
            outcome = f"R1 lost ({po_w}-{po_gp - po_w})"
        elif po_w < 8:
            outcome = f"R2 lost ({po_w}-{po_gp - po_w})"
        elif po_w < 12:
            outcome = f"CF lost ({po_w}-{po_gp - po_w})"
        elif po_w < 16:
            outcome = f"Finals lost ({po_w}-{po_gp - po_w})"
        else:
            outcome = f"CHAMPION ({po_w}-{po_gp - po_w})"

        rows.append({
            "season_start_year": season_start,
            "season_year": f"{season_start}-{str(season_start+1)[-2:]}",
            "team_abbreviation": r["team_abbreviation"],
            "C1_pct": round(r["C1_ball_stickiness_pct"], 1),
            "C2_pct": round(r["C2_movement_death_pct"], 1),
            "C3_pct": round(r["C3_isolation_reliance_pct"], 1),
            "C4_pct": round(r["C4_action_poverty_pct"], 1),
            "C5_pct": round(r["C5_shot_quality_decay_pct"], 1),
            "lafi_pct": round(r["lafi_pct"], 1),
            "sharp_lafi_pct": round(r["sharp_lafi_pct"], 1),
            "rs_record": f"{rs_w}-{rs_gp - rs_w}",
            "rs_wins": rs_w,
            "made_playoffs": po_gp > 0,
            "playoff_outcome": outcome,
            "playoff_wins": po_w,
            "playoff_losses": po_gp - po_w,
        })
    return pd.DataFrame(rows)


def run():
    print("=" * 80)
    print("Q0C v1 historical cohort analysis")
    print("=" * 80)
    lafi = load_lafi()
    cohort = define_cohort(lafi)
    print(f"\nCohort definition: Sharp LAFI >= {COHORT_FILTERS['sharp_lafi_pct_min']}, "
          f"C1 < {COHORT_FILTERS['c1_ball_stickiness_pct_max']}, "
          f"C2 > {COHORT_FILTERS['c2_movement_death_pct_min']}")
    print(f"N teams: {len(cohort)} (universe: {len(lafi)} team-seasons 2014-15 through 2025-26 RS)")

    outcomes = pull_outcomes(cohort)
    print("\n=== Cohort teams with outcomes ===\n")
    print(outcomes[["season_year", "team_abbreviation", "rs_record",
                    "sharp_lafi_pct", "lafi_pct", "playoff_outcome"]].to_string(index=False))

    # Outcome distribution
    print("\n=== Outcome distribution (excluding 2025-26 MIN target) ===\n")
    excl_target = outcomes[~((outcomes["team_abbreviation"] == "MIN") &
                                (outcomes["season_start_year"] == 2025))]
    n = len(excl_target)
    missed = (~excl_target["made_playoffs"]).sum()
    r1 = excl_target["playoff_outcome"].str.startswith("R1").sum()
    r2 = excl_target["playoff_outcome"].str.startswith("R2").sum()
    cf = excl_target["playoff_outcome"].str.startswith("CF").sum()
    finals = excl_target["playoff_outcome"].str.startswith("Finals").sum()
    champ = excl_target["playoff_outcome"].str.startswith("CHAMPION").sum()

    print(f"  Missed playoffs:   {missed}/{n} ({missed/n:.0%})")
    print(f"  R1 lost:           {r1}/{n} ({r1/n:.0%})")
    print(f"  R2 lost:           {r2}/{n} ({r2/n:.0%})")
    print(f"  Conf Finals lost:  {cf}/{n} ({cf/n:.0%})")
    print(f"  Finals lost:       {finals}/{n} ({finals/n:.0%})")
    print(f"  Champion:          {champ}/{n} ({champ/n:.0%})")

    outcomes.to_csv(OUT_DIR / "cohort_with_outcomes.csv", index=False)
    print(f"\nWrote outcomes to {OUT_DIR / 'cohort_with_outcomes.csv'}")


if __name__ == "__main__":
    run()
