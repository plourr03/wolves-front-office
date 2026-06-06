"""Wolves 2024-25 vs 2025-26 lineup-grain comparison.

Answers four questions:

Q1. Edwards lineup-grain 3PA rates: did Edwards-on lineups in 2024-25 RS
    have higher 3PA rates than Edwards-on lineups in 2025-26 RS? If yes,
    the year-over-year shift is a real change in offensive identity.
Q2. Was the Gobert+Randle pairing also bad in 2024-25? Compare same
    pairing's net rating across both regular seasons.
Q3. DiVincenzo-on lineups in 2024-25 RS (he was healthy that year):
    cleaner Category B test than the playoff sample.
Q4. Team-level four factors at the lineup grain across both seasons.

Run via: python -m analyses.q2_localize.yoy_lineups
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from analyses.q2_localize import config, analysis, batch


def load_wolves_season_stints(season_year: int) -> pd.DataFrame:
    """Load cached stint records for Wolves in the given season."""
    if season_year == 2024:
        cache = config.CACHE_DIR / "wolves_2024_stints"
    elif season_year == 2025:
        cache = config.CACHE_DIR / "wolves_2025_stints"
    else:
        raise ValueError(f"No cache for season {season_year}")
    df = batch.load_cached_stints(cache)
    return df[df["team_id"] == config.WOLVES_TEAM_ID].copy()


def split_by_season_type(stints: pd.DataFrame, season_year: int) -> dict[str, pd.DataFrame]:
    return analysis.split_stints_by_season_type(stints, season_year=season_year)


# ---------------------------------------------------------------------------
# Cohort filters
# ---------------------------------------------------------------------------


def with_player(stints: pd.DataFrame, pid: int) -> pd.DataFrame:
    return stints[stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, pid))].copy()


def without_player(stints: pd.DataFrame, pid: int) -> pd.DataFrame:
    return stints[stints["lineup_id"].apply(lambda lid: not analysis.player_in_lineup(lid, pid))].copy()


def with_pair(stints: pd.DataFrame, pid1: int, pid2: int) -> pd.DataFrame:
    return stints[
        stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, pid1))
        & stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, pid2))
    ].copy()


def with_p1_no_p2(stints: pd.DataFrame, pid1: int, pid2: int) -> pd.DataFrame:
    return stints[
        stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, pid1))
        & stints["lineup_id"].apply(lambda lid: not analysis.player_in_lineup(lid, pid2))
    ].copy()


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------


def cohort_summary(stints: pd.DataFrame, label: str, garbage_filter: bool = True) -> dict:
    if garbage_filter and "in_garbage_time" in stints.columns:
        stints = stints[~stints["in_garbage_time"]]
    if stints.empty:
        return {"label": label, "stints": 0, "minutes": 0.0, "net_rating": np.nan,
                "off_rating": np.nan, "def_rating": np.nan, "off_3pa_rate": np.nan,
                "off_efg": np.nan, "fg3a_per_100": np.nan,
                "net_ci_lo": np.nan, "net_ci_hi": np.nan,
                "tpa_ci_lo": np.nan, "tpa_ci_hi": np.nan}
    minutes = stints["duration_sec"].sum() / 60
    poss_off = stints["possessions_off"].sum()
    poss_def = stints["possessions_def"].sum()
    pts_for = stints["points_for"].sum()
    pts_against = stints["points_against"].sum()
    fga = stints["fga_off"].sum()
    fg3a = stints["fg3a_off"].sum()
    fgm = stints["fgm_off"].sum()
    fg3m = stints["fg3m_off"].sum()
    fta = stints["fta_off"].sum()
    net = 100 * pts_for / poss_off - 100 * pts_against / poss_def if poss_off and poss_def else np.nan
    off_rtg = 100 * pts_for / poss_off if poss_off else np.nan
    def_rtg = 100 * pts_against / poss_def if poss_def else np.nan
    tpa_rate = fg3a / fga if fga else np.nan
    efg = (fgm + 0.5 * fg3m) / fga if fga else np.nan
    fg3a_p100 = 100 * fg3a / poss_off if poss_off else np.nan

    # Bootstrap CIs on net rating and 3PA rate
    net_b = analysis.bootstrap_lineup_metric(stints, analysis.m_net_rating)
    tpa_b = analysis.bootstrap_lineup_metric(stints, analysis.m_off_3pa_rate)
    fg3a_p100_b = analysis.bootstrap_lineup_metric(stints, analysis.m_fg3a_per_100)

    return {"label": label, "stints": len(stints), "minutes": float(minutes),
            "possessions_off": int(poss_off), "possessions_def": int(poss_def),
            "net_rating": float(net), "off_rating": float(off_rtg), "def_rating": float(def_rtg),
            "off_3pa_rate": float(tpa_rate), "off_efg": float(efg),
            "fg3a_per_100": float(fg3a_p100),
            "net_ci_lo": net_b["ci_lo"], "net_ci_hi": net_b["ci_hi"],
            "tpa_ci_lo": tpa_b["ci_lo"], "tpa_ci_hi": tpa_b["ci_hi"],
            "fg3a_p100_ci_lo": fg3a_p100_b["ci_lo"], "fg3a_p100_ci_hi": fg3a_p100_b["ci_hi"]}


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run():
    print("Loading 2024-25 and 2025-26 Wolves stints...")
    w24 = load_wolves_season_stints(2024)
    w25 = load_wolves_season_stints(2025)
    s24 = split_by_season_type(w24, 2024)
    s25 = split_by_season_type(w25, 2025)

    print(f"  2024-25: {len(w24)} stints across {w24['game_id'].nunique()} games")
    print(f"    by season type: { {k: len(v) for k, v in s24.items()} }")
    print(f"  2025-26: {len(w25)} stints across {w25['game_id'].nunique()} games")
    print(f"    by season type: { {k: len(v) for k, v in s25.items()} }")

    rs24 = s24.get("Regular Season", pd.DataFrame())
    rs25 = s25.get("Regular Season", pd.DataFrame())
    po24 = s24.get("Playoffs", pd.DataFrame())
    po25 = s25.get("Playoffs", pd.DataFrame())

    # =========================================================
    # Q4: Team-level (all Wolves stints) at the lineup grain
    # =========================================================
    print("\n=== Q4: Team-level four factors at lineup grain ===")
    rows = []
    rows.append(cohort_summary(rs24, "2024-25 RS"))
    rows.append(cohort_summary(rs25, "2025-26 RS"))
    rows.append(cohort_summary(po24, "2024-25 PO"))
    rows.append(cohort_summary(po25, "2025-26 PO"))
    df = pd.DataFrame(rows)
    print(df[["label", "stints", "minutes", "possessions_off", "net_rating",
              "off_rating", "def_rating", "off_3pa_rate", "off_efg",
              "fg3a_per_100"]].round(3).to_string(index=False))
    df.to_csv(config.TABLE_DIR / "yoy_team_lineup_grain.csv", index=False)

    # =========================================================
    # Q1: Edwards-on vs Edwards-off lineups in each season
    # =========================================================
    print("\n=== Q1: Edwards-on lineups (3PA rate comparison) ===")
    rows = []
    for label, st in [("2024-25 RS", rs24), ("2025-26 RS", rs25),
                       ("2024-25 PO", po24), ("2025-26 PO", po25)]:
        if st.empty:
            continue
        eon = with_player(st, config.ANT_ID)
        eoff = without_player(st, config.ANT_ID)
        rows.append(cohort_summary(eon, f"{label} Edwards-ON"))
        rows.append(cohort_summary(eoff, f"{label} Edwards-OFF"))
    df = pd.DataFrame(rows)
    print(df[["label", "stints", "minutes", "possessions_off",
              "net_rating", "net_ci_lo", "net_ci_hi",
              "off_3pa_rate", "tpa_ci_lo", "tpa_ci_hi",
              "fg3a_per_100"]].round(3).to_string(index=False))
    df.to_csv(config.TABLE_DIR / "yoy_edwards_lineups.csv", index=False)

    # =========================================================
    # Q2: Gobert+Randle pairing in each season
    # =========================================================
    print("\n=== Q2: Gobert+Randle pairing (with Naz off) ===")
    rows = []
    for label, st in [("2024-25 RS", rs24), ("2025-26 RS", rs25),
                       ("2024-25 PO", po24), ("2025-26 PO", po25)]:
        if st.empty:
            continue
        # Gobert+Randle on the floor, Naz off
        gr = with_pair(st, config.GOBERT_ID, config.RANDLE_ID)
        gr_no_naz = gr[gr["lineup_id"].apply(
            lambda lid: not analysis.player_in_lineup(lid, config.NAZ_ID))]
        # Gobert+Naz pairing, Randle off
        gn = with_pair(st, config.GOBERT_ID, config.NAZ_ID)
        gn_no_randle = gn[gn["lineup_id"].apply(
            lambda lid: not analysis.player_in_lineup(lid, config.RANDLE_ID))]
        # Naz+Randle pairing, Gobert off
        nr = with_pair(st, config.NAZ_ID, config.RANDLE_ID)
        nr_no_gob = nr[nr["lineup_id"].apply(
            lambda lid: not analysis.player_in_lineup(lid, config.GOBERT_ID))]
        rows.append(cohort_summary(gr_no_naz, f"{label} Gobert+Randle (Naz off)"))
        rows.append(cohort_summary(gn_no_randle, f"{label} Gobert+Naz (Randle off)"))
        rows.append(cohort_summary(nr_no_gob, f"{label} Naz+Randle (Gobert off)"))
    df = pd.DataFrame(rows)
    print(df[["label", "stints", "minutes", "possessions_off",
              "net_rating", "net_ci_lo", "net_ci_hi",
              "off_3pa_rate", "fg3a_per_100"]].round(3).to_string(index=False))
    df.to_csv(config.TABLE_DIR / "yoy_big_pairings.csv", index=False)

    # =========================================================
    # Q3: DiVincenzo-on lineups (the cleaner Category B test)
    # =========================================================
    print("\n=== Q3: DiVincenzo-on lineups (Category B test) ===")
    rows = []
    for label, st in [("2024-25 RS", rs24), ("2025-26 RS", rs25),
                       ("2024-25 PO", po24), ("2025-26 PO", po25)]:
        if st.empty:
            continue
        don = with_player(st, config.DIVINCENZO_ID)
        doff = without_player(st, config.DIVINCENZO_ID)
        rows.append(cohort_summary(don, f"{label} DiVincenzo-ON"))
        rows.append(cohort_summary(doff, f"{label} DiVincenzo-OFF"))
    df = pd.DataFrame(rows)
    print(df[["label", "stints", "minutes", "possessions_off",
              "net_rating", "net_ci_lo", "net_ci_hi",
              "off_3pa_rate", "fg3a_per_100"]].round(3).to_string(index=False))
    df.to_csv(config.TABLE_DIR / "yoy_divincenzo_lineups.csv", index=False)

    # =========================================================
    # Edwards configurations: Edwards with each frontcourt partner
    # =========================================================
    print("\n=== Edwards + frontcourt-partner configurations ===")
    rows = []
    for label, st in [("2024-25 RS", rs24), ("2025-26 RS", rs25)]:
        if st.empty:
            continue
        for partner_name, pid in [("Gobert", config.GOBERT_ID),
                                    ("Naz", config.NAZ_ID),
                                    ("Randle", config.RANDLE_ID)]:
            ee = with_pair(st, config.ANT_ID, pid)
            rows.append(cohort_summary(ee, f"{label} Edwards+{partner_name}"))
    df = pd.DataFrame(rows)
    print(df[["label", "stints", "minutes", "possessions_off",
              "net_rating", "off_3pa_rate", "fg3a_per_100"]].round(3).to_string(index=False))
    df.to_csv(config.TABLE_DIR / "yoy_edwards_partners.csv", index=False)

    print(f"\nOutputs in {config.TABLE_DIR}")


if __name__ == "__main__":
    run()
