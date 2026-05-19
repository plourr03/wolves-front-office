"""Salary-efficiency analysis for Q8.

Combines Wolves rotation player RAPM with the salary data from
specs/timberwolves-current-salaries.csv. Computes RAPM per million of
salary as a salary-efficiency metric.

Caveats applied:
- Edwards net RAPM is an artifact of the Wolves-only sample. Use his
  offensive RAPM +3.97 as the meaningful signal for the salary lens.
- Wolves-only RAPM has limitations for all Wolves players (every Wolves
  possession includes Wolves players, confounded with team-level effects).
  The salary efficiency is a directional comparison, not a precise ranking.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SALARY_CSV = Path("specs/timberwolves-current-salaries.csv")
RAPM_CSV = Path("outputs/tables/q2_localize/rapm_player_impacts.csv")
OUT_DIR = Path("outputs/tables/q8_player_decisions")
OUT_DIR.mkdir(parents=True, exist_ok=True)


# Map between salary CSV "Player" string and warehouse player_id
NAME_TO_PID = {
    "Anthony Edwards": 1630162,
    "Rudy Gobert": 203497,
    "Julius Randle": 203944,
    "Jaden McDaniels": 1630183,
    "Naz Reid": 1629675,
    "Donte DiVincenzo": 1628978,
    "Ayo Dosunmu": 1630245,
    "Joan Beringer": 1642866,
    "Terrence Shannon Jr.": 1630545,
    "Bones Hyland": 1630538,
    "Joe Ingles": 204060,
    "Julian Phillips": 1641763,
    "Jaylen Clark": 1641740,
    "Mike Conley": 201144,
    "Kyle Anderson": 203937,
}


def _parse_dollar(s: str) -> float:
    if not isinstance(s, str) or not s.strip():
        return np.nan
    return float(s.replace("$", "").replace(",", ""))


def load_salaries() -> pd.DataFrame:
    df = pd.read_csv(SALARY_CSV)
    df = df[df["Player"] != "Team Totals"].copy()
    for col in ["2025-26", "2026-27", "2027-28", "2028-29", "2029-30", "2030-31", "Guaranteed"]:
        df[col] = df[col].apply(_parse_dollar)
    df["player_id"] = df["Player"].map(NAME_TO_PID)
    return df


def load_rapm() -> pd.DataFrame:
    return pd.read_csv(RAPM_CSV)


def build_salary_efficiency() -> pd.DataFrame:
    sal = load_salaries()
    rapm = load_rapm()

    merged = sal.merge(rapm[["player_id", "off_rapm", "def_rapm", "net_rapm"]],
                        on="player_id", how="left")
    merged = merged.sort_values("2025-26", ascending=False, na_position="last")

    # Edwards net RAPM is artifact; use off RAPM as proxy for impact lens.
    # Document this explicitly via a column.
    merged["impact_proxy"] = merged["net_rapm"]
    merged.loc[merged["player_id"] == 1630162, "impact_proxy"] = (
        merged.loc[merged["player_id"] == 1630162, "off_rapm"]
    )

    # RAPM per million salary (for 2025-26 currently observed season).
    sal_millions = merged["2025-26"] / 1_000_000
    merged["rapm_per_$m"] = merged["net_rapm"] / sal_millions
    merged["impact_per_$m"] = merged["impact_proxy"] / sal_millions

    # Implied threshold by salary tier (rough heuristic from NBA economics):
    #   $0-5M minimum/cheap rotation: any positive impact = fine
    #   $5-15M MLE tier: positive impact required
    #   $15-25M mid tier: modest positive RAPM required (~+0.5 to +1)
    #   $25-35M star tier: substantial RAPM required (~+2 to +3)
    #   $35M+ max tier: top-tier impact required (~+3 to +5)
    def _threshold(sal_25_26):
        if pd.isna(sal_25_26):
            return np.nan
        s = sal_25_26 / 1_000_000
        if s < 5:
            return 0.0
        if s < 15:
            return 0.5
        if s < 25:
            return 1.0
        if s < 35:
            return 2.5
        return 4.0

    merged["implied_threshold_rapm"] = merged["2025-26"].apply(_threshold)
    merged["surplus_vs_threshold"] = merged["impact_proxy"] - merged["implied_threshold_rapm"]

    cols = ["Player", "Age", "2025-26", "2026-27", "2027-28", "Guaranteed",
            "off_rapm", "def_rapm", "net_rapm", "impact_proxy",
            "rapm_per_$m", "impact_per_$m",
            "implied_threshold_rapm", "surplus_vs_threshold"]
    return merged[cols]


def run():
    df = build_salary_efficiency()
    print("\n=== Wolves rotation: Salary vs RAPM efficiency ===\n")
    # Format for display
    disp = df.copy()
    for col in ["2025-26", "2026-27", "2027-28", "Guaranteed"]:
        disp[col] = disp[col].apply(lambda v: f"${v/1e6:.1f}M" if pd.notna(v) else "")
    cols_show = ["Player", "Age", "2025-26", "2026-27", "off_rapm", "def_rapm",
                  "net_rapm", "impact_proxy", "impact_per_$m",
                  "implied_threshold_rapm", "surplus_vs_threshold"]
    print(disp[cols_show].round(3).to_string(index=False))
    df.to_csv(OUT_DIR / "salary_efficiency.csv", index=False)


if __name__ == "__main__":
    run()
