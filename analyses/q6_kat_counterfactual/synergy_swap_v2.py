"""Q6 v2 KAT counterfactual: corrected Synergy-level swap.

V2 fixes the methodological gap in v1: the KAT trade brought in BOTH Randle
AND DiVincenzo (plus picks). The v1 swap was one-for-one (KAT for Randle,
holding DiVincenzo constant). V2 is one-for-two:

  - Remove Randle's actual 2025-26 MIN Synergy possessions
  - Remove DiVincenzo's actual 2025-26 MIN Synergy possessions
  - Add KAT's actual 2025-26 NYK Synergy possessions (scaled to Randle's
    volume, same as v1)
  - Add a "replacement-level wing" filling DiVincenzo's slot, modeled at
    50% of DiVincenzo's volume with -0.05 PPP per play type. Two sensitivity
    bands also reported (optimistic 70%/-0.02 PPP, pessimistic 30%/-0.08 PPP).

The "replacement-level wing" assumption represents what the Wolves likely
would have signed in 2024 free agency if they had not received DiVincenzo
in the KAT trade (an Ingles-tier veteran or minimum-salary catch-and-shoot
specialist). Without the cap savings from the KAT trade, the team would
not have had the room to pursue a DiVincenzo-equivalent.
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
DIVINCENZO_PLAYER_ID = 1628978


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


def construct_corrected_counterfactual(
    team_2526: pd.DataFrame, randle_2526: pd.DataFrame,
    kat_2526: pd.DataFrame, dvz_2526: pd.DataFrame,
    replacement_volume_scale: float = 0.5,
    replacement_ppp_delta: float = -0.05,
) -> pd.DataFrame:
    """Build the v2 counterfactual.

    Args:
        team_2526: actual 2025-26 Wolves team Synergy (filtered to season)
        randle_2526: Randle's actual 2025-26 MIN player Synergy
        kat_2526: KAT's actual 2025-26 NYK player Synergy
        dvz_2526: DiVincenzo's actual 2025-26 MIN player Synergy
        replacement_volume_scale: fraction of DiVincenzo's volume the
            replacement wing would carry (default 0.5)
        replacement_ppp_delta: PPP delta vs DiVincenzo (default -0.05; the
            replacement wing is less efficient)
    """
    # Scale KAT to Randle's volume (same as v1)
    randle_total = randle_2526["poss"].sum()
    kat_total = kat_2526["poss"].sum()
    kat_scale = randle_total / kat_total if kat_total else 1.0
    kat_scaled = kat_2526.copy()
    kat_scaled["poss_scaled"] = kat_scaled["poss"] * kat_scale

    # Replacement wing: replacement_volume_scale of DiVincenzo's per-play volume
    rep_wing = dvz_2526.copy()
    rep_wing["poss_scaled"] = rep_wing["poss"] * replacement_volume_scale
    rep_wing["ppp_scaled"] = rep_wing["ppp"] + replacement_ppp_delta

    merged = team_2526.merge(
        randle_2526[["play_type", "poss"]].rename(columns={"poss": "randle_poss"}),
        on="play_type", how="left",
    ).merge(
        kat_scaled[["play_type", "poss_scaled", "ppp"]].rename(
            columns={"ppp": "kat_ppp", "poss_scaled": "kat_poss_scaled"}),
        on="play_type", how="left",
    ).merge(
        dvz_2526[["play_type", "poss", "ppp"]].rename(
            columns={"poss": "dvz_poss", "ppp": "dvz_ppp"}),
        on="play_type", how="left",
    ).merge(
        rep_wing[["play_type", "poss_scaled", "ppp_scaled"]].rename(
            columns={"poss_scaled": "rep_poss", "ppp_scaled": "rep_ppp"}),
        on="play_type", how="left",
    )

    for col in ("randle_poss", "kat_poss_scaled", "dvz_poss", "rep_poss"):
        merged[col] = merged[col].fillna(0)

    merged["cf_poss"] = (
        merged["poss"] - merged["randle_poss"] - merged["dvz_poss"]
        + merged["kat_poss_scaled"] + merged["rep_poss"]
    )

    cf_total = merged["cf_poss"].sum()
    actual_total = merged["poss"].sum()
    merged["cf_pct"] = merged["cf_poss"] / cf_total
    merged["actual_pct"] = merged["poss"] / actual_total
    merged["delta_pct"] = merged["cf_pct"] - merged["actual_pct"]

    return merged, kat_scale, randle_total, kat_total


def compute_team_ppp(merged: pd.DataFrame, dvz_2526: pd.DataFrame,
                       replacement_ppp_delta: float) -> tuple[float, float]:
    """Approximate team blended PPP for actual and counterfactual."""
    actual_total = merged["poss"].sum()
    actual_ppp = (merged["poss"] * merged["ppp"]).sum() / actual_total

    cf_total = merged["cf_poss"].sum()
    # CF PPP: weighted by each component's contribution
    # remaining_poss = poss - randle_poss - dvz_poss (kept at actual ppp)
    # plus kat_poss_scaled at kat_ppp
    # plus rep_poss at (dvz_ppp + delta)
    remaining = merged["poss"] - merged["randle_poss"] - merged["dvz_poss"]
    cf_pts = (
        remaining * merged["ppp"]
        + merged["kat_poss_scaled"] * merged["kat_ppp"].fillna(0)
        + merged["rep_poss"] * (merged["dvz_ppp"].fillna(0) + replacement_ppp_delta)
    ).sum()
    cf_ppp = cf_pts / cf_total
    return actual_ppp, cf_ppp


def run():
    seasons = ["2023-24", "2024-25", "2025-26"]
    team = pull_team_synergy(seasons)
    randle = pull_player_synergy(RANDLE_PLAYER_ID, seasons)
    kat = pull_player_synergy(KAT_PLAYER_ID, seasons)
    dvz = pull_player_synergy(DIVINCENZO_PLAYER_ID, seasons)

    team_2526 = team[team["season_year"] == "2025-26"].copy()
    randle_2526 = randle[randle["season_year"] == "2025-26"].copy()
    kat_2526 = kat[kat["season_year"] == "2025-26"].copy()
    dvz_2526 = dvz[dvz["season_year"] == "2025-26"].copy()

    print("=" * 80)
    print("Q6 v2 KAT counterfactual: CORRECTED Synergy swap")
    print("Removes Randle AND DiVincenzo; adds KAT + replacement-level wing")
    print("=" * 80)

    print(f"\nRandle 2025-26 total offensive poss: {randle_2526['poss'].sum():.0f}")
    print(f"DiVincenzo 2025-26 total offensive poss: {dvz_2526['poss'].sum():.0f}")
    print(f"KAT 2025-26 (NYK) total offensive poss: {kat_2526['poss'].sum():.0f}")
    print(f"Wolves team 2025-26 total offensive poss: {team_2526['poss'].sum():.0f}")

    # Three scenarios for replacement wing
    scenarios = [
        ("optimistic_70pct", 0.70, -0.02),
        ("default_50pct",     0.50, -0.05),
        ("pessimistic_30pct", 0.30, -0.08),
    ]

    results = []
    for name, vol_scale, ppp_delta in scenarios:
        merged, kat_scale, _, _ = construct_corrected_counterfactual(
            team_2526, randle_2526, kat_2526, dvz_2526, vol_scale, ppp_delta)
        actual_ppp, cf_ppp = compute_team_ppp(merged, dvz_2526, ppp_delta)
        results.append((name, merged, kat_scale, actual_ppp, cf_ppp, vol_scale, ppp_delta))

    # Print headline architectural metrics for the default scenario plus bands
    print("\n=== Headline architectural shifts (corrected v2) ===")
    print("\n2025-26 play-type frequencies across scenarios:\n")
    base_merged = results[1][1]  # default 50%
    headline_plays = ["Isolation", "Cut", "OffScreen", "PRRollMan", "Spotup", "Transition"]

    # Compute v1 (one-for-one, no DVZ removal) for comparison
    v1_merged = team_2526.merge(
        randle_2526[["play_type", "poss"]].rename(columns={"poss": "randle_poss"}),
        on="play_type", how="left",
    ).merge(
        kat_2526[["play_type", "poss", "ppp"]].rename(
            columns={"poss": "kat_poss", "ppp": "kat_ppp"}),
        on="play_type", how="left",
    )
    randle_total = randle_2526["poss"].sum()
    kat_total = kat_2526["poss"].sum()
    kat_scale = randle_total / kat_total
    v1_merged["kat_poss_scaled"] = v1_merged["kat_poss"] * kat_scale
    for c in ("randle_poss", "kat_poss_scaled"):
        v1_merged[c] = v1_merged[c].fillna(0)
    v1_merged["cf_poss_v1"] = v1_merged["poss"] - v1_merged["randle_poss"] + v1_merged["kat_poss_scaled"]
    v1_total = v1_merged["cf_poss_v1"].sum()
    v1_merged["cf_pct_v1"] = v1_merged["cf_poss_v1"] / v1_total

    # Historical
    hist = {}
    for season, grp in team.groupby("season_year"):
        total = grp["poss"].sum()
        hist[season] = {r["play_type"]: r["poss"] / total for _, r in grp.iterrows()}

    rows = []
    for play in headline_plays:
        v1_pct = v1_merged[v1_merged["play_type"] == play]["cf_pct_v1"].iloc[0]
        row = {
            "play_type": play,
            "2023-24 actual": hist["2023-24"].get(play, 0),
            "2025-26 actual": hist["2025-26"].get(play, 0),
            "v1 CF (one-for-one)": v1_pct,
        }
        for scen_name, m, _, _, _, _, _ in results:
            row[f"v2 CF {scen_name}"] = m[m["play_type"] == play]["cf_pct"].iloc[0]
        rows.append(row)
    df_summary = pd.DataFrame(rows)
    print(df_summary.round(4).to_string(index=False))

    print("\n=== Motion (Cut + OffScreen) total ===")
    def _sum(d, plays):
        return sum(d.get(p, 0) for p in plays)
    motion = {
        "2023-24 actual": _sum(hist["2023-24"], ["Cut", "OffScreen"]),
        "2025-26 actual": _sum(hist["2025-26"], ["Cut", "OffScreen"]),
        "v1 CF (one-for-one)": (
            v1_merged[v1_merged["play_type"].isin(["Cut", "OffScreen"])]["cf_pct_v1"].sum()
        ),
    }
    for scen_name, m, _, _, _, _, _ in results:
        motion[f"v2 CF {scen_name}"] = m[m["play_type"].isin(["Cut", "OffScreen"])]["cf_pct"].sum()
    for k, v in motion.items():
        print(f"  {k:35s} {v:.4f}")

    print("\n=== Team blended PPP impact ===")
    for scen_name, m, kat_scale, actual_ppp, cf_ppp, vol_scale, ppp_delta in results:
        print(f"\n  Scenario {scen_name} (rep wing: {vol_scale:.0%} volume, {ppp_delta:+.2f} PPP):")
        print(f"    Actual team Synergy PPP:        {actual_ppp:.3f}")
        print(f"    CF team Synergy PPP:            {cf_ppp:.3f}")
        print(f"    Delta PPP per Synergy poss:     {cf_ppp - actual_ppp:+.3f}")
        ssn_poss = team_2526["poss"].sum()
        print(f"    Delta team points per season:   {(cf_ppp - actual_ppp) * ssn_poss:+.1f}")

    base_merged.to_csv(OUT_DIR / "v2_counterfactual_default_50pct.csv", index=False)
    df_summary.to_csv(OUT_DIR / "v2_headline_architectural_shifts.csv", index=False)

    print("\n=== Q6 v2 verdict shape ===")
    print("Q6 v1 said: CF lands at Q3 (Sharp LAFI ~70-80, Full LAFI ~50-58)")
    print("Q6 v2 corrects: CF DiVincenzo loss removes ~316 Spotup possessions,")
    print("which hurts C5 shot quality decay and partly C2 motion. The corrected")
    print("counterfactual lands further from Q1 than v1 said.")


if __name__ == "__main__":
    run()
