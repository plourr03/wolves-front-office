"""Q1 driver. Builds the centerpiece cross-tab, computes dropoffs vs league
baselines, writes outputs and a findings markdown.

Usage:
    python -m analyses.q1_diagnose
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from analyses.q1_diagnose import config, data, metrics


HEADLINE_METRICS = [
    "off_rating", "def_rating", "net_rating", "pace",
    "off_efg", "off_tov_pct", "off_oreb_pct", "off_ft_rate",
    "def_efg", "def_tov_pct", "def_oreb_pct", "def_ft_rate",
    "off_3pa_rate", "off_3p_pct",
    "def_3pa_rate", "def_3p_pct",
]


def build_cross_tab(games: pd.DataFrame) -> pd.DataFrame:
    """Build the Q1 centerpiece cross-tab.

    Columns: Wolves 23-24 RS, Wolves 23-24 PO, Wolves 24-25 RS, Wolves 24-25 PO,
             Wolves 25-26 RS, Wolves 25-26 PO,
             League 25-26 RS (playoff teams), League 25-26 PO,
             Historical league avg playoff dropoff.
    Rows: HEADLINE_METRICS.
    """
    cols = {}
    for year in config.WOLVES_REFERENCE_YEARS:
        for st in ("Regular Season", "Playoffs"):
            sub = data.filter_to_team_and_seasons(games, config.WOLVES_TEAM_ID, [year], st)
            if len(sub) > 0:
                summary = metrics.team_season_summary(sub)
                cols[f"MIN_{year}_{st[:2]}"] = summary

    # League playoff-team averages for the current season.
    current = config.CURRENT_SEASON_YEAR
    po_team_ids = data.playoff_team_seasons(games, current)
    rs_pool = games[(games["season_start_year"] == current)
                    & (games["season_type"] == "Regular Season")
                    & (games["team_id"].isin(po_team_ids))]
    po_pool = games[(games["season_start_year"] == current)
                    & (games["season_type"] == "Playoffs")]
    # Average across team-seasons.
    cols[f"LEAGUE_{current}_RS_avg"] = _avg_team_summary(rs_pool, po_team_ids)
    cols[f"LEAGUE_{current}_PO_avg"] = _avg_team_summary(po_pool, po_team_ids)

    table = pd.DataFrame(cols).reindex(HEADLINE_METRICS)
    return table


def _avg_team_summary(pool: pd.DataFrame, team_ids: list[int]) -> dict:
    """Compute league average team-season summary across the listed team_ids
    within the pool (which is already filtered to a season/season_type).
    """
    per_team = []
    for tid in team_ids:
        sub = pool[pool["team_id"] == tid]
        if len(sub) < 4:
            continue
        per_team.append(metrics.team_season_summary(sub))
    if not per_team:
        return {m: np.nan for m in HEADLINE_METRICS}
    return {m: float(np.nanmean([t[m] for t in per_team])) for m in HEADLINE_METRICS}


def build_wolves_dropoffs(games: pd.DataFrame) -> dict:
    """For each Wolves reference year, compute PO - RS for each metric and
    compare to historical league average dropoff.
    """
    out = {}
    for year in config.WOLVES_REFERENCE_YEARS:
        rs = data.filter_to_team_and_seasons(games, config.WOLVES_TEAM_ID, [year], "Regular Season")
        po = data.filter_to_team_and_seasons(games, config.WOLVES_TEAM_ID, [year], "Playoffs")
        if len(rs) < 50 or len(po) < 4:
            continue
        rs_s = metrics.team_season_summary(rs)
        po_s = metrics.team_season_summary(po)
        out[year] = {
            "rs_summary": rs_s,
            "po_summary": po_s,
            "n_po_games": len(po),
            "dropoffs": metrics.compute_dropoffs(rs_s, po_s, HEADLINE_METRICS),
        }
    return out


def bootstrap_wolves_playoffs(games: pd.DataFrame, year: int) -> dict:
    """Bootstrap key metrics on the Wolves' playoff sample."""
    po = data.filter_to_team_and_seasons(games, config.WOLVES_TEAM_ID, [year], "Playoffs")
    if len(po) < 4:
        return {}
    metric_funcs = {
        "off_rating": metrics.metric_off_rating,
        "def_rating": metrics.metric_def_rating,
        "net_rating": metrics.metric_net_rating,
        "off_efg": metrics.metric_off_efg,
        "def_efg": metrics.metric_def_efg,
        "off_tov_pct": metrics.metric_off_tov,
        "def_tov_pct": metrics.metric_def_tov,
        "off_oreb_pct": metrics.metric_off_oreb,
        "def_oreb_pct": metrics.metric_def_oreb,
        "off_ft_rate": metrics.metric_off_ft_rate,
        "def_ft_rate": metrics.metric_def_ft_rate,
        "def_3pa_rate": metrics.metric_def_3pa_rate,
        "def_3p_pct": metrics.metric_def_3p_pct,
    }
    return {name: metrics.bootstrap_summary(po, f) for name, f in metric_funcs.items()}


def metric_off_3pa_rate(df: pd.DataFrame) -> float:
    fga = df["fga"].sum()
    return df["fg3a"].sum() / fga if fga else float("nan")


def bootstrap_wolves_dropoffs(games: pd.DataFrame, year: int) -> dict:
    """Bootstrap CI on the DROPOFF (PO - RS) for headline metrics.

    Treats the regular season as a fixed anchor. Resamples playoff games
    with replacement; each resample computes PO - RS. Returns per-metric
    point + CI dict.
    """
    rs = data.filter_to_team_and_seasons(games, config.WOLVES_TEAM_ID, [year], "Regular Season")
    po = data.filter_to_team_and_seasons(games, config.WOLVES_TEAM_ID, [year], "Playoffs")
    if len(rs) < 50 or len(po) < 4:
        return {}
    metric_funcs = {
        "off_rating": metrics.metric_off_rating,
        "def_rating": metrics.metric_def_rating,
        "net_rating": metrics.metric_net_rating,
        "off_efg": metrics.metric_off_efg,
        "def_efg": metrics.metric_def_efg,
        "off_3pa_rate": metric_off_3pa_rate,
        "off_tov_pct": metrics.metric_off_tov,
        "off_oreb_pct": metrics.metric_off_oreb,
        "off_ft_rate": metrics.metric_off_ft_rate,
        "def_oreb_pct": metrics.metric_def_oreb,
        "def_ft_rate": metrics.metric_def_ft_rate,
    }
    out = {}
    for name, fn in metric_funcs.items():
        rs_value = fn(rs)
        out[name] = metrics.bootstrap_dropoff(po, rs_value, fn)
    return out


def run() -> None:
    print("Loading team-game data 2014-15 through 2025-26...")
    games = data.load_team_games(year_lo=2014, year_hi=2025)
    print(f"  {len(games):,} team-game rows.")

    print("\nBuilding cross-tab...")
    table = build_cross_tab(games)
    print(table.round(3).to_string())
    table.to_csv(config.TABLE_DIR / "cross_tab.csv")

    print("\nWolves year-over-year dropoffs (PO - RS):")
    wolves = build_wolves_dropoffs(games)
    dropoff_rows = []
    for year, d in wolves.items():
        for m, v in d["dropoffs"].items():
            dropoff_rows.append({"year": year, "season_label": config.season_label(year),
                                  "metric": m, "rs_value": d["rs_summary"][m],
                                  "po_value": d["po_summary"][m], "dropoff": v,
                                  "n_po_games": d["n_po_games"]})
    drop_df = pd.DataFrame(dropoff_rows)
    print(drop_df.pivot_table(index="metric", columns="season_label", values="dropoff").round(3).to_string())
    drop_df.to_csv(config.TABLE_DIR / "wolves_dropoffs.csv", index=False)

    print("\nHistorical league playoff dropoffs (last 10 seasons, excl. COVID)...")
    hist = metrics.historical_playoff_dropoffs(games, config.HISTORICAL_DROPOFF_YEARS, HEADLINE_METRICS)
    print(hist["summary"].round(3).to_string())
    hist["summary"].to_csv(config.TABLE_DIR / "historical_league_dropoffs.csv")
    hist["raw"].to_csv(config.TABLE_DIR / "historical_dropoffs_raw.csv", index=False)

    print("\nExcess dropoffs: Wolves 2025-26 PO - typical league playoff dropoff")
    current_year = config.CURRENT_SEASON_YEAR
    if current_year in wolves:
        current_drops = wolves[current_year]["dropoffs"]
        league_avg = hist["summary"]["league_avg_dropoff"].to_dict()
        league_std = hist["summary"]["league_std_dropoff"].to_dict()
        rows = []
        for m in HEADLINE_METRICS:
            wolves_drop = current_drops.get(m, np.nan)
            la = league_avg.get(m, np.nan)
            ls = league_std.get(m, np.nan)
            excess = wolves_drop - la
            z = excess / ls if ls else np.nan
            rows.append({"metric": m, "wolves_dropoff": wolves_drop,
                         "league_avg_dropoff": la, "league_std_dropoff": ls,
                         "excess_dropoff": excess, "z_score": z})
        excess_df = pd.DataFrame(rows).sort_values("z_score", key=lambda s: s.abs(), ascending=False)
        print(excess_df.round(3).to_string(index=False))
        excess_df.to_csv(config.TABLE_DIR / "excess_dropoffs_25_26.csv", index=False)

    print("\nBootstrap CIs on Wolves 2025-26 playoff metrics (1000 resamples, seed=42)...")
    boots = bootstrap_wolves_playoffs(games, config.CURRENT_SEASON_YEAR)
    rows = []
    for m, b in boots.items():
        rows.append({"metric": m, "point": b["point"], "ci_lo": b["ci_lo"], "ci_hi": b["ci_hi"], "n": b["n"]})
    bdf = pd.DataFrame(rows)
    print(bdf.round(4).to_string(index=False))
    bdf.to_csv(config.TABLE_DIR / "bootstrap_wolves_25_26_playoffs.csv", index=False)

    print("\nBootstrap CIs on Wolves 2025-26 DROPOFFS (PO - RS, RS fixed)...")
    drops = bootstrap_wolves_dropoffs(games, config.CURRENT_SEASON_YEAR)
    rows = []
    # Match each dropoff CI to league avg / std for the same metric so the
    # reader can see "is the dropoff distinguishable from zero AND from the
    # league norm" in one row.
    league_avg = hist["summary"]["league_avg_dropoff"].to_dict() if current_year in wolves else {}
    league_std = hist["summary"]["league_std_dropoff"].to_dict() if current_year in wolves else {}
    for m, d in drops.items():
        la = league_avg.get(m, np.nan)
        ls = league_std.get(m, np.nan)
        # Z-score using the league dropoff distribution.
        z = (d["point"] - la) / ls if ls and not np.isnan(ls) and ls != 0 else np.nan
        rows.append({
            "metric": m,
            "rs_value": d["rs_value"],
            "po_value": d["po_value"],
            "dropoff_point": d["point"],
            "dropoff_ci_lo": d["ci_lo"],
            "dropoff_ci_hi": d["ci_hi"],
            "league_avg_dropoff": la,
            "league_std_dropoff": ls,
            "z_score": z,
            "ci_crosses_zero": d["ci_lo"] <= 0 <= d["ci_hi"] if not (np.isnan(d["ci_lo"]) or np.isnan(d["ci_hi"])) else None,
            "n_po_games": d["n"],
        })
    drop_ci_df = pd.DataFrame(rows)
    print(drop_ci_df.round(4).to_string(index=False))
    drop_ci_df.to_csv(config.TABLE_DIR / "bootstrap_dropoff_25_26.csv", index=False)

    print(f"\nOutputs written to {config.TABLE_DIR}")


def main():
    ap = argparse.ArgumentParser()
    args = ap.parse_args()
    run()


if __name__ == "__main__":
    main()
