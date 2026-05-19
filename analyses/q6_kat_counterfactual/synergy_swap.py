"""Q6 v1 KAT counterfactual: Synergy-level swap analysis.

The scope-capped question (per data scientist direction): would the 2025-26 Wolves
have stayed Q1 architecturally per LAFI if KAT had stayed?

Step 1 of Q6 (2023-24 LAFI baseline) is already established by Q0A:
- 2023-24 Wolves (KAT year, WCF): Full LAFI 35 / Sharp 45 = Q1/Q2 territory
- 2024-25 (Randle year 1): Full LAFI 63 / Sharp 71 = Q3-leaning
- 2025-26 (Randle year 2): Full LAFI 65 / Sharp 90 = Q4

This module builds the player-level Synergy swap counterfactual:
- Take Randle's 2025-26 actual Wolves Synergy possessions
- Replace with KAT's 2025-26 actual NYK Synergy possessions, scaled to Randle's
  total volume to control for usage differences
- Construct counterfactual team Synergy and compute the architectural
  signal differences that drive LAFI components C2 (motion) and C3 (iso)

Output:
- Per-play-type counterfactual frequencies
- Comparison: 2023-24 actual / 2024-25 actual / 2025-26 actual / 2025-26 counterfactual
- Verdict on architectural reversion (full / partial / none)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from lib import db


OUT_DIR = Path("outputs/tables/q6_kat_counterfactual")
OUT_DIR.mkdir(parents=True, exist_ok=True)


WOLVES_TEAM_ID = 1610612750
KAT_PLAYER_ID = 1626157
RANDLE_PLAYER_ID = 203944


def pull_team_synergy(seasons: list[str]) -> pd.DataFrame:
    q = """
    SELECT season_year, play_type, poss, ppp, efg_pct
    FROM nba.nba_synergy_team_play_types
    WHERE team_id = %(team_id)s
      AND season_year IN %(seasons)s
      AND season_type = 'Regular Season'
      AND type_grouping = 'Offensive'
    ORDER BY season_year, play_type
    """
    df = db.query(q, {"team_id": WOLVES_TEAM_ID, "seasons": tuple(seasons)})
    for c in ("poss", "ppp", "efg_pct"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def pull_player_synergy(player_id: int, seasons: list[str]) -> pd.DataFrame:
    q = """
    SELECT season_year, team_abbreviation, play_type, poss, ppp, efg_pct
    FROM nba.nba_synergy_player_play_types
    WHERE player_id = %(player_id)s
      AND season_year IN %(seasons)s
      AND season_type = 'Regular Season'
      AND type_grouping = 'Offensive'
    ORDER BY season_year, play_type
    """
    df = db.query(q, {"player_id": player_id, "seasons": tuple(seasons)})
    for c in ("poss", "ppp", "efg_pct"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def construct_counterfactual(team: pd.DataFrame, randle: pd.DataFrame,
                              kat: pd.DataFrame) -> pd.DataFrame:
    """Construct 2025-26 counterfactual team Synergy distribution.

    Strategy: subtract Randle's actual 2025-26 possessions, add KAT's 2025-26 NYK
    possessions scaled to Randle's total volume so the swap controls for usage
    rather than overall team minutes.
    """
    team_2526 = team[team["season_year"] == "2025-26"].copy()
    randle_2526 = randle[randle["season_year"] == "2025-26"].copy()
    kat_2526 = kat[kat["season_year"] == "2025-26"].copy()

    randle_total = randle_2526["poss"].sum()
    kat_total = kat_2526["poss"].sum()
    scale = randle_total / kat_total if kat_total else 1.0
    kat_2526["poss_scaled"] = kat_2526["poss"] * scale

    merged = team_2526.merge(
        randle_2526[["play_type", "poss"]].rename(columns={"poss": "randle_poss"}),
        on="play_type", how="left",
    ).merge(
        kat_2526[["play_type", "poss_scaled", "ppp", "efg_pct"]].rename(
            columns={"ppp": "kat_ppp", "efg_pct": "kat_efg", "poss_scaled": "kat_poss_scaled"}),
        on="play_type", how="left",
    )
    merged["randle_poss"] = merged["randle_poss"].fillna(0)
    merged["kat_poss_scaled"] = merged["kat_poss_scaled"].fillna(0)
    merged["cf_poss"] = merged["poss"] - merged["randle_poss"] + merged["kat_poss_scaled"]

    cf_total = merged["cf_poss"].sum()
    actual_total = merged["poss"].sum()
    merged["cf_pct"] = merged["cf_poss"] / cf_total
    merged["actual_pct"] = merged["poss"] / actual_total
    merged["delta_pct"] = merged["cf_pct"] - merged["actual_pct"]

    cf_ppp = (merged["cf_poss"] * (
        (merged["poss"] - merged["randle_poss"]) / (merged["cf_poss"] + 1e-9) * merged["ppp"]
        + merged["kat_poss_scaled"] / (merged["cf_poss"] + 1e-9) * merged["kat_ppp"]
    )).sum() / cf_total
    actual_ppp = (merged["poss"] * merged["ppp"]).sum() / actual_total

    print(f"\nKAT 2025-26 NYK total offensive poss: {kat_total:.0f}")
    print(f"Randle 2025-26 MIN total offensive poss: {randle_total:.0f}")
    print(f"Scale factor (KAT to Randle volume): {scale:.3f}")
    print(f"Team actual 2025-26 total poss: {actual_total:.0f}")
    print(f"Team counterfactual 2025-26 total poss: {cf_total:.0f}")
    print(f"Team actual blended PPP (per Synergy poss): {actual_ppp:.3f}")
    print(f"Team counterfactual blended PPP (per Synergy poss): {cf_ppp:.3f}")
    print(f"PPP swing: {cf_ppp - actual_ppp:+.3f}")

    return merged


def historical_team_pct(team: pd.DataFrame) -> pd.DataFrame:
    """Compute per-season play type frequency for the Wolves."""
    rows = []
    for season, grp in team.groupby("season_year"):
        total = grp["poss"].sum()
        for _, r in grp.iterrows():
            rows.append({
                "season_year": season,
                "play_type": r["play_type"],
                "poss": r["poss"],
                "pct": r["poss"] / total,
                "ppp": r["ppp"],
            })
    return pd.DataFrame(rows)


def run():
    seasons = ["2023-24", "2024-25", "2025-26"]
    team = pull_team_synergy(seasons)
    randle = pull_player_synergy(RANDLE_PLAYER_ID, seasons)
    kat = pull_player_synergy(KAT_PLAYER_ID, seasons)

    print("=" * 80)
    print("Q6 v1 KAT counterfactual: Synergy-level swap analysis")
    print("=" * 80)

    print("\n--- Wolves team Synergy across three seasons ---")
    hist = historical_team_pct(team)
    pivot = hist.pivot_table(index="play_type", columns="season_year",
                              values="pct", aggfunc="first")
    print(pivot.round(4).to_string())

    print("\n--- KAT player Synergy across three seasons ---")
    kat_pivot = kat.pivot_table(index="play_type", columns="season_year",
                                  values="poss", aggfunc="first")
    print(kat_pivot.to_string())

    print("\n--- Randle player Synergy across two seasons (in MIN) ---")
    randle_pivot = randle.pivot_table(index="play_type", columns="season_year",
                                       values="poss", aggfunc="first")
    print(randle_pivot.to_string())

    print("\n--- Counterfactual 2025-26 swap: Randle out, KAT (NYK 2025-26 scaled) in ---")
    cf = construct_counterfactual(team, randle, kat)

    cf_display = cf[["play_type", "poss", "randle_poss", "kat_poss_scaled",
                       "cf_poss", "actual_pct", "cf_pct", "delta_pct"]].copy()
    cf_display["actual_pct"] = cf_display["actual_pct"].round(4)
    cf_display["cf_pct"] = cf_display["cf_pct"].round(4)
    cf_display["delta_pct"] = cf_display["delta_pct"].round(4)
    print(cf_display.to_string(index=False))

    cf.to_csv(OUT_DIR / "counterfactual_synergy.csv", index=False)
    hist.to_csv(OUT_DIR / "wolves_team_synergy_history.csv", index=False)

    print("\n--- Headline architectural metrics ---")
    cf_iso = cf[cf["play_type"] == "Isolation"].iloc[0]
    cf_cut = cf[cf["play_type"] == "Cut"].iloc[0]
    cf_offscreen = cf[cf["play_type"] == "OffScreen"].iloc[0]
    cf_prroll = cf[cf["play_type"] == "PRRollMan"].iloc[0]
    cf_spotup = cf[cf["play_type"] == "Spotup"].iloc[0]

    def _row(label, play_type):
        row23 = pivot.loc[play_type, "2023-24"]
        row24 = pivot.loc[play_type, "2024-25"]
        row25 = pivot.loc[play_type, "2025-26"]
        cf_val = cf[cf["play_type"] == play_type]["cf_pct"].iloc[0]
        return [label, row23, row24, row25, cf_val, cf_val - row25, cf_val - row23]

    summary = pd.DataFrame(
        [_row("Isolation", "Isolation"),
         _row("Cut", "Cut"),
         _row("OffScreen", "OffScreen"),
         _row("Motion (Cut+OffScreen)", None) if False else
            ["Motion (Cut+OffScreen)",
             pivot.loc["Cut", "2023-24"] + pivot.loc["OffScreen", "2023-24"],
             pivot.loc["Cut", "2024-25"] + pivot.loc["OffScreen", "2024-25"],
             pivot.loc["Cut", "2025-26"] + pivot.loc["OffScreen", "2025-26"],
             cf_cut["cf_pct"] + cf_offscreen["cf_pct"],
             (cf_cut["cf_pct"] + cf_offscreen["cf_pct"]) - (pivot.loc["Cut", "2025-26"] + pivot.loc["OffScreen", "2025-26"]),
             (cf_cut["cf_pct"] + cf_offscreen["cf_pct"]) - (pivot.loc["Cut", "2023-24"] + pivot.loc["OffScreen", "2023-24"])],
         _row("PRRollMan", "PRRollMan"),
         _row("Spotup", "Spotup"),
        ],
        columns=["metric", "2023-24 KAT", "2024-25 Randle Y1", "2025-26 Randle Y2",
                  "2025-26 CF (KAT)", "delta CF vs actual 2025-26", "delta CF vs 2023-24 baseline"],
    )
    print(summary.round(4).to_string(index=False))
    summary.to_csv(OUT_DIR / "headline_architectural_swing.csv", index=False)


if __name__ == "__main__":
    run()
