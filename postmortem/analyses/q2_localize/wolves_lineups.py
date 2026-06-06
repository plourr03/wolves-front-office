"""Wolves-specific lineup analysis: leaderboards, 3PA per lineup, RS vs PO
discontinuous drop, Gobert-at-5 vs Naz-at-5, individual on/off.

Run via: python -m analyses.q2_localize.wolves_lineups
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from analyses.q2_localize import analysis, batch, config


def load_wolves_stints(season_year: int) -> pd.DataFrame:
    """Load cached stint records for a Wolves season batch."""
    if season_year == 2024:
        cache = config.CACHE_DIR / "wolves_2024_stints"
    elif season_year == 2025:
        cache = config.CACHE_DIR / "wolves_2025_stints"
    else:
        raise ValueError(f"No batch for season {season_year}")
    df = batch.load_cached_stints(cache)
    # Restrict to Wolves stints only (the batch also has opponent stints since
    # each game involves both teams). For Wolves-specific analyses we want
    # team_id == 1610612750.
    return df[df["team_id"] == config.WOLVES_TEAM_ID].copy()


def load_league_po_stints() -> pd.DataFrame:
    """Load cached stint records for the league-wide 2025-26 playoff batch.
    Includes all teams that played in the playoffs.
    """
    cache = config.CACHE_DIR / "league_2025_po_stints"
    return batch.load_cached_stints(cache)


def split_wolves_by_season_type(wolves_stints: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Annotate Wolves stints with season_type and split into RS / PO."""
    return analysis.split_stints_by_season_type(wolves_stints, season_year=2025)


def lineup_leaderboard(stints: pd.DataFrame,
                         season_year: int, season_type: str,
                         min_possessions: int = 30,
                         gt_filter: bool = True) -> pd.DataFrame:
    """Aggregate to lineup totals and sort by minutes, filter to min possessions."""
    agg = analysis.aggregate_for_team(stints, config.WOLVES_TEAM_ID,
                                        season_year, season_type, gt_filter)
    if agg.empty:
        return agg
    agg = agg.sort_values("total_minutes", ascending=False).reset_index(drop=True)
    if min_possessions:
        agg = agg[agg["possessions_off"] >= min_possessions].reset_index(drop=True)
    return agg


# ---------------------------------------------------------------------------
# 3PA rate distribution per lineup
# ---------------------------------------------------------------------------


def lineup_3pa_distribution(
    wolves_stints_rs: pd.DataFrame,
    wolves_stints_po: pd.DataFrame,
    min_possessions: int = 30,
) -> pd.DataFrame:
    """For each Wolves lineup with enough possessions in BOTH RS and PO,
    compute the 3PA rate in each and the dropoff.
    """
    rs = analysis.aggregate_for_team(wolves_stints_rs, config.WOLVES_TEAM_ID,
                                       2025, "Regular Season", gt_filter=True)
    po = analysis.aggregate_for_team(wolves_stints_po, config.WOLVES_TEAM_ID,
                                       2025, "Playoffs", gt_filter=True)
    if rs.empty or po.empty:
        return pd.DataFrame()
    rs = rs[["lineup_id", "possessions_off", "off_3pa_rate", "off_efg",
             "off_rating", "def_rating", "net_rating",
             "fga_off", "fg3a_off", "total_minutes"]].copy()
    rs.columns = ["lineup_id", "poss_rs", "rate_rs", "efg_rs",
                  "off_rtg_rs", "def_rtg_rs", "net_rtg_rs",
                  "fga_rs", "fg3a_rs", "min_rs"]
    po = po[["lineup_id", "possessions_off", "off_3pa_rate", "off_efg",
             "off_rating", "def_rating", "net_rating",
             "fga_off", "fg3a_off", "total_minutes"]].copy()
    po.columns = ["lineup_id", "poss_po", "rate_po", "efg_po",
                  "off_rtg_po", "def_rtg_po", "net_rtg_po",
                  "fga_po", "fg3a_po", "min_po"]
    merged = rs.merge(po, on="lineup_id", how="inner")
    merged["3pa_dropoff"] = merged["rate_po"] - merged["rate_rs"]
    merged["efg_dropoff"] = merged["efg_po"] - merged["efg_rs"]
    merged["net_rtg_dropoff"] = merged["net_rtg_po"] - merged["net_rtg_rs"]
    return merged


def lineup_3pa_all_observations(wolves_stints: pd.DataFrame,
                                 season_year: int = 2025) -> pd.DataFrame:
    """For each Wolves lineup, compute 3PA rate in RS and PO independently
    (does NOT require lineup to play in both). Returns one row per
    (lineup_id, season_type) with possessions and rate.
    """
    splits = split_wolves_by_season_type(wolves_stints)
    rows = []
    for st_name, sub in splits.items():
        if sub.empty:
            continue
        agg = analysis.aggregate_for_team(sub, config.WOLVES_TEAM_ID,
                                           season_year, st_name, gt_filter=True)
        if agg.empty:
            continue
        agg["season_type"] = st_name
        rows.append(agg)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


# ---------------------------------------------------------------------------
# Gobert-at-5 vs Naz-at-5
# ---------------------------------------------------------------------------


def stints_with_player(stints: pd.DataFrame, player_id: int) -> pd.DataFrame:
    """Filter stints to those where player_id is on the floor for the Wolves."""
    mask = stints["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, player_id))
    return stints[mask].copy()


def stints_without_player(stints: pd.DataFrame, player_id: int) -> pd.DataFrame:
    mask = stints["lineup_id"].apply(lambda lid: not analysis.player_in_lineup(lid, player_id))
    return stints[mask].copy()


def gobert_naz_at_5_analysis(wolves_stints: pd.DataFrame) -> dict:
    """For each season_type (RS, PO), compare:
      - Gobert on, Naz off: Gobert at the 5
      - Naz on, Gobert off: Naz at the 5
      - Both on: jumbo / double-big
      - Both off: small ball

    Headline metrics: net rating, off rating, def rating, off 3PA rate.
    Bootstrap CIs and minutes/possessions.

    Also: opponent-quality confound check (which opponents each configuration
    faced) and game-state context (margin distribution).
    """
    splits = split_wolves_by_season_type(wolves_stints)
    out = {}
    for st_name, sub in splits.items():
        sub_wolves = sub[sub["team_id"] == config.WOLVES_TEAM_ID].copy()
        if sub_wolves.empty:
            continue
        # Apply garbage time filter for the headline numbers.
        sub_wolves = sub_wolves[~sub_wolves["in_garbage_time"]]
        cohorts = {
            "gobert_at_5": sub_wolves[
                sub_wolves["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.GOBERT_ID))
                & sub_wolves["lineup_id"].apply(lambda lid: not analysis.player_in_lineup(lid, config.NAZ_ID))
            ],
            "naz_at_5": sub_wolves[
                sub_wolves["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.NAZ_ID))
                & sub_wolves["lineup_id"].apply(lambda lid: not analysis.player_in_lineup(lid, config.GOBERT_ID))
            ],
            "both_on": sub_wolves[
                sub_wolves["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.GOBERT_ID))
                & sub_wolves["lineup_id"].apply(lambda lid: analysis.player_in_lineup(lid, config.NAZ_ID))
            ],
            "both_off": sub_wolves[
                sub_wolves["lineup_id"].apply(lambda lid: not analysis.player_in_lineup(lid, config.GOBERT_ID))
                & sub_wolves["lineup_id"].apply(lambda lid: not analysis.player_in_lineup(lid, config.NAZ_ID))
            ],
        }
        cohort_summary = {}
        for cohort_name, cohort_stints in cohorts.items():
            if cohort_stints.empty:
                cohort_summary[cohort_name] = {"n_stints": 0, "minutes": 0.0}
                continue
            minutes = cohort_stints["duration_sec"].sum() / 60.0
            poss_off = cohort_stints["possessions_off"].sum()
            poss_def = cohort_stints["possessions_def"].sum()
            net_b = analysis.bootstrap_lineup_metric(cohort_stints, analysis.m_net_rating)
            off_b = analysis.bootstrap_lineup_metric(cohort_stints, analysis.m_off_rating)
            def_b = analysis.bootstrap_lineup_metric(cohort_stints, analysis.m_def_rating)
            tpa_b = analysis.bootstrap_lineup_metric(cohort_stints, analysis.m_off_3pa_rate)
            fg3a_b = analysis.bootstrap_lineup_metric(cohort_stints, analysis.m_fg3a_per_100)
            cohort_summary[cohort_name] = {
                "n_stints": len(cohort_stints),
                "minutes": float(minutes),
                "possessions_off": int(poss_off),
                "possessions_def": int(poss_def),
                "net_rating": net_b,
                "off_rating": off_b,
                "def_rating": def_b,
                "off_3pa_rate": tpa_b,
                "fg3a_per_100": fg3a_b,
            }
        out[st_name] = cohort_summary
    return out


# ---------------------------------------------------------------------------
# Individual on/off (raw)
# ---------------------------------------------------------------------------


def individual_on_off(wolves_stints: pd.DataFrame, player_ids: list[int]) -> pd.DataFrame:
    """For each player_id, compute team net rating with player on vs off,
    in 2025-26 RS and PO, with bootstrap CIs.
    """
    splits = split_wolves_by_season_type(wolves_stints)
    rows = []
    for st_name, sub in splits.items():
        sub_wolves = sub[sub["team_id"] == config.WOLVES_TEAM_ID].copy()
        if sub_wolves.empty:
            continue
        sub_wolves = sub_wolves[~sub_wolves["in_garbage_time"]]
        for pid in player_ids:
            on_stints = sub_wolves[sub_wolves["lineup_id"].apply(
                lambda lid: analysis.player_in_lineup(lid, pid))]
            off_stints = sub_wolves[sub_wolves["lineup_id"].apply(
                lambda lid: not analysis.player_in_lineup(lid, pid))]
            on_b = analysis.bootstrap_lineup_metric(on_stints, analysis.m_net_rating) if not on_stints.empty else {"point": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "n": 0}
            off_b = analysis.bootstrap_lineup_metric(off_stints, analysis.m_net_rating) if not off_stints.empty else {"point": np.nan, "ci_lo": np.nan, "ci_hi": np.nan, "n": 0}
            on_min = on_stints["duration_sec"].sum() / 60.0 if not on_stints.empty else 0.0
            off_min = off_stints["duration_sec"].sum() / 60.0 if not off_stints.empty else 0.0
            rows.append({
                "season_type": st_name,
                "player_id": pid,
                "on_minutes": float(on_min),
                "on_net_rating": on_b["point"],
                "on_ci_lo": on_b["ci_lo"],
                "on_ci_hi": on_b["ci_hi"],
                "off_minutes": float(off_min),
                "off_net_rating": off_b["point"],
                "off_ci_lo": off_b["ci_lo"],
                "off_ci_hi": off_b["ci_hi"],
                "on_off_diff": on_b["point"] - off_b["point"] if not (np.isnan(on_b["point"]) or np.isnan(off_b["point"])) else np.nan,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# League percentile placement for Wolves PO lineups
# ---------------------------------------------------------------------------


def league_po_baseline(league_stints: pd.DataFrame,
                        min_possessions: int = 30) -> pd.DataFrame:
    """Aggregate the league-wide 2025-26 PO stints to per-(team, lineup) totals
    and return only those with enough possessions for comparison.
    """
    agg = analysis.aggregate_all_teams(league_stints, 2025, "Playoffs", gt_filter=True)
    if agg.empty:
        return agg
    return agg[agg["possessions_off"] >= min_possessions].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run():
    print("Loading Wolves 2025-26 cached stints...")
    w2025 = load_wolves_stints(2025)
    print(f"  {len(w2025)} Wolves stints from {w2025['game_id'].nunique()} games")
    w2025_by_st = split_wolves_by_season_type(w2025)
    print(f"  by season type: { {k: len(v) for k, v in w2025_by_st.items()} }")

    # NOTE: 2024-25 PBP uses the legacy NBA Stats API format ('Made Shot',
    # 'Missed Shot', 'Rebound', etc.) which the foundational pipeline does
    # not parse. The lineup pipeline only works for 2025-26 PBP (Live PBP
    # format). The 2024-25 vs 2025-26 lineup-grain comparison is therefore
    # blocked pending a PBP normalization layer. For 2024-25 vs 2025-26
    # comparisons we use warehouse aggregates (nba_player_stats,
    # nba_player_advanced_stats, nba_synergy_*, nba_player_tracking_*) in
    # analyses/q2_localize/year_over_year.py instead.
    w2024 = pd.DataFrame()

    print("\nLoading league-wide 2025-26 PO cached stints...")
    league = load_league_po_stints()
    print(f"  {len(league)} stints from {league['game_id'].nunique()} games, {league['team_id'].nunique()} teams")

    # ---- Headline tables ----
    print("\n=== Wolves 2025-26 PO lineup leaderboard (>=30 possessions, GT-filtered) ===")
    po_2025_lb = lineup_leaderboard(w2025_by_st.get("Playoffs", pd.DataFrame()),
                                      2025, "Playoffs", min_possessions=30)
    print(po_2025_lb.head(15).to_string(index=False))
    po_2025_lb.to_csv(config.TABLE_DIR / "wolves_po_2025_lineup_leaderboard.csv", index=False)

    print("\n=== Wolves 2025-26 RS lineup leaderboard (>=30 possessions, GT-filtered) ===")
    rs_2025_lb = lineup_leaderboard(w2025_by_st.get("Regular Season", pd.DataFrame()),
                                      2025, "Regular Season", min_possessions=30)
    print(rs_2025_lb.head(15).to_string(index=False))
    rs_2025_lb.to_csv(config.TABLE_DIR / "wolves_rs_2025_lineup_leaderboard.csv", index=False)

    # 2024-25 leaderboards intentionally skipped: PBP format mismatch
    # prevents the pipeline from extracting stints. See module-level NOTE.
    print("\n=== Wolves 2024-25 lineup leaderboards: SKIPPED (PBP format mismatch) ===")

    # ---- 3PA per lineup ----
    print("\n=== Per-lineup 3PA rate (RS vs PO 2025-26) ===")
    pa3 = lineup_3pa_distribution(w2025_by_st.get("Regular Season", pd.DataFrame()),
                                    w2025_by_st.get("Playoffs", pd.DataFrame()),
                                    min_possessions=30)
    if not pa3.empty:
        pa3 = pa3.sort_values("min_po", ascending=False)
        print(pa3[["lineup_id", "poss_rs", "poss_po", "rate_rs", "rate_po", "3pa_dropoff",
                   "net_rtg_rs", "net_rtg_po", "net_rtg_dropoff"]].head(15).round(3).to_string(index=False))
        pa3.to_csv(config.TABLE_DIR / "wolves_lineup_3pa_rs_vs_po_2025.csv", index=False)
    else:
        print("(no lineups with sufficient possessions in BOTH RS and PO)")

    # ---- Gobert vs Naz ----
    print("\n=== Gobert-at-5 vs Naz-at-5 (2025-26) ===")
    gn = gobert_naz_at_5_analysis(w2025)
    gn_rows = []
    for st_name, cohorts in gn.items():
        for cohort_name, summary in cohorts.items():
            if summary.get("n_stints", 0) == 0:
                continue
            gn_rows.append({
                "season_type": st_name, "cohort": cohort_name,
                "n_stints": summary["n_stints"], "minutes": summary["minutes"],
                "possessions_off": summary["possessions_off"],
                "possessions_def": summary["possessions_def"],
                "net_rating": summary["net_rating"]["point"],
                "net_ci_lo": summary["net_rating"]["ci_lo"],
                "net_ci_hi": summary["net_rating"]["ci_hi"],
                "off_rating": summary["off_rating"]["point"],
                "off_ci_lo": summary["off_rating"]["ci_lo"],
                "off_ci_hi": summary["off_rating"]["ci_hi"],
                "def_rating": summary["def_rating"]["point"],
                "def_ci_lo": summary["def_rating"]["ci_lo"],
                "def_ci_hi": summary["def_rating"]["ci_hi"],
                "off_3pa_rate": summary["off_3pa_rate"]["point"],
                "tpa_ci_lo": summary["off_3pa_rate"]["ci_lo"],
                "tpa_ci_hi": summary["off_3pa_rate"]["ci_hi"],
                "fg3a_per_100": summary["fg3a_per_100"]["point"],
                "fg3a_per_100_ci_lo": summary["fg3a_per_100"]["ci_lo"],
                "fg3a_per_100_ci_hi": summary["fg3a_per_100"]["ci_hi"],
            })
    gn_df = pd.DataFrame(gn_rows)
    print(gn_df.round(3).to_string(index=False))
    gn_df.to_csv(config.TABLE_DIR / "gobert_naz_at_5_2025.csv", index=False)

    # 2024-25 Gobert-Naz lineup analysis intentionally skipped (PBP format
    # mismatch). The team-level Gobert vs Naz on/off for 2024-25 is computed
    # in analyses/q2_localize/year_over_year.py from warehouse aggregates.

    # ---- Individual on/off ----
    print("\n=== Individual on/off (2025-26) ===")
    onoff = individual_on_off(w2025, config.CORE_ROTATION + [config.HYLAND_ID, config.CLARK_ID])
    # Attach names.
    names = analysis.load_player_names(onoff["player_id"].unique().tolist())
    onoff["player_name"] = onoff["player_id"].map(names)
    onoff = onoff[["season_type", "player_name", "player_id",
                    "on_minutes", "on_net_rating", "on_ci_lo", "on_ci_hi",
                    "off_minutes", "off_net_rating", "off_ci_lo", "off_ci_hi",
                    "on_off_diff"]]
    print(onoff.round(2).to_string(index=False))
    onoff.to_csv(config.TABLE_DIR / "individual_on_off_2025.csv", index=False)

    # ---- League PO baseline ----
    print("\n=== League-wide 2025-26 PO lineup baseline (top 20 by minutes) ===")
    lg = league_po_baseline(league, min_possessions=30)
    if not lg.empty:
        print(lg.sort_values("total_minutes", ascending=False).head(20)
                [["team_id", "lineup_id", "total_minutes", "possessions_off",
                  "off_rating", "def_rating", "net_rating",
                  "off_3pa_rate", "off_efg"]].round(3).to_string(index=False))
        lg.to_csv(config.TABLE_DIR / "league_po_2025_lineups.csv", index=False)

    print(f"\nOutputs written to {config.TABLE_DIR}")


if __name__ == "__main__":
    run()
