"""
Q1 build: assemble the diagnostic cross-tab.

Columns:
    25-26 RS  | 25-26 PO  | 24-25 PO  | 23-24 PO  | League 25-26 RS  | League 25-26 PO

Rows: net rating, offensive rating, defensive rating, pace, then the offensive
four factors and defensive four factors.

Also produces:
    - Wolves playoff dropoff for each metric (PO - RS)
    - 25-26 league average playoff dropoff (mean across 16 playoff teams)
    - 10-year historical league playoff dropoff (mean across all playoff teams
      2014-15 through 2024-25)
    - Wolves "excess dropoff": actual minus historical norm
    - Bootstrap 95% CI on the 25-26 Wolves playoff metric (resampling games)

Outputs land in outputs/tables/q1_*.{parquet,md}.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from analyses.q1.data import pull_team_games
from analyses.q1.metrics import (
    aggregate_team_season,
    bootstrap_team_metrics,
    METRIC_COLS_ALL,
)


REPO = Path(__file__).resolve().parents[2]
TABLES_DIR = REPO / "outputs" / "tables"


METRIC_LABELS = {
    "net_rtg":           "Net rating",
    "ortg":              "Offensive rating",
    "drtg":              "Defensive rating",
    "pace":              "Pace (poss / game)",
    "efg_pct":           "eFG%",
    "tov_pct":           "TOV%",
    "oreb_pct":          "OREB%",
    "ft_per_fga":        "FT / FGA",
    "three_pt_rate":     "3PA rate",
    "three_pt_pct":      "3PT%",
    "opp_efg_pct":       "Opp eFG%",
    "opp_tov_pct":       "Opp TOV%",
    "dreb_pct":          "DREB%",
    "opp_ft_per_fga":    "Opp FT / FGA",
    "opp_three_pt_rate": "Opp 3PA rate",
    "opp_three_pt_pct":  "Opp 3PT%",
}


def league_dropoff(agg: pd.DataFrame, season_label: str) -> pd.Series:
    """
    Mean per-metric playoff dropoff (PO - RS) across all playoff teams in the
    given season. Only teams with both an RS row and a PO row are included.
    """
    s = agg[agg.season_label == season_label]
    rs = s[s.season_type == "Regular Season"].set_index("team_abbreviation")
    po = s[s.season_type == "Playoffs"].set_index("team_abbreviation")
    common = rs.index.intersection(po.index)
    diff = po.loc[common, METRIC_COLS_ALL] - rs.loc[common, METRIC_COLS_ALL]
    return diff.mean()


def historical_dropoff(agg: pd.DataFrame, exclude_season: str) -> pd.DataFrame:
    """
    Mean and std of per-metric playoff dropoff across all playoff teams in all
    seasons except the one given. Returns DataFrame indexed by metric with
    columns: hist_mean, hist_std, n.
    """
    s = agg[agg.season_label != exclude_season]
    rs = s[s.season_type == "Regular Season"].set_index(["season_label", "team_abbreviation"])
    po = s[s.season_type == "Playoffs"].set_index(["season_label", "team_abbreviation"])
    common = rs.index.intersection(po.index)
    diff = po.loc[common, METRIC_COLS_ALL] - rs.loc[common, METRIC_COLS_ALL]
    out = pd.DataFrame({
        "hist_mean": diff.mean(),
        "hist_std":  diff.std(),
        "n":         diff.count(),
    })
    return out


def build_crosstab(agg: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame:
    """
    Build the Q1 diagnostic cross-tab indexed by metric.
    """
    def col(team: str | None, season: str, stype: str) -> pd.Series:
        s = agg
        if team:
            s = s[s.team_abbreviation == team]
        s = s[(s.season_label == season) & (s.season_type == stype)]
        if team is None:
            # League average: simple mean across teams in that slice
            return s[METRIC_COLS_ALL].mean()
        if len(s) == 0:
            return pd.Series(index=METRIC_COLS_ALL, dtype=float)
        return s.iloc[0][METRIC_COLS_ALL]

    cols = {
        "MIN 25-26 RS":        col("MIN", "2025-26", "Regular Season"),
        "MIN 25-26 PO":        col("MIN", "2025-26", "Playoffs"),
        "MIN 24-25 PO":        col("MIN", "2024-25", "Playoffs"),
        "MIN 23-24 PO":        col("MIN", "2023-24", "Playoffs"),
        "League 25-26 RS":     col(None,  "2025-26", "Regular Season"),
        "League 25-26 PO":     col(None,  "2025-26", "Playoffs"),
    }
    ct = pd.DataFrame(cols)

    # Dropoffs
    ct["MIN 25-26 dropoff (PO - RS)"] = ct["MIN 25-26 PO"] - ct["MIN 25-26 RS"]
    ct["League 25-26 dropoff"]        = league_dropoff(agg, "2025-26")
    hist = historical_dropoff(agg, exclude_season="2025-26")
    ct["League historical dropoff"]   = hist["hist_mean"]
    ct["League historical dropoff std"] = hist["hist_std"]
    ct["MIN 25-26 excess dropoff vs historical"] = (
        ct["MIN 25-26 dropoff (PO - RS)"] - ct["League historical dropoff"]
    )

    # Bootstrap CI for the 25-26 Wolves playoff sample on each metric
    wolves_po_games = games[
        (games.team_abbreviation == "MIN")
        & (games.season_label == "2025-26")
        & (games.season_type == "Playoffs")
    ]
    boot = bootstrap_team_metrics(wolves_po_games, METRIC_COLS_ALL, n_resamples=1000)
    boot = boot.set_index("metric")
    ct["MIN 25-26 PO 95% CI low"]  = boot["lower"]
    ct["MIN 25-26 PO 95% CI high"] = boot["upper"]

    ct.index.name = "metric"
    ct = ct.reindex(list(METRIC_LABELS.keys()))
    ct.insert(0, "label", [METRIC_LABELS[m] for m in ct.index])
    return ct


def render_markdown(ct: pd.DataFrame) -> str:
    """Pretty markdown table of the cross-tab, suitable for outputs/reports."""
    pct_rows = {"efg_pct","tov_pct","oreb_pct","ft_per_fga","three_pt_rate","three_pt_pct",
                "opp_efg_pct","opp_tov_pct","dreb_pct","opp_ft_per_fga","opp_three_pt_rate","opp_three_pt_pct"}
    def fmtval(metric: str, v) -> str:
        if pd.isna(v): return ""
        if metric in pct_rows:
            return f"{v*100:.1f}%"
        return f"{v:.2f}"
    cols_to_format = [c for c in ct.columns if c != "label"]
    fmt = ct[["label"]].copy()
    for c in cols_to_format:
        fmt[c] = [fmtval(m, ct.at[m, c]) for m in ct.index]
    fmt = fmt.reset_index(drop=True)
    return fmt.to_markdown(index=False)


def main() -> None:
    print("[Q1] Pulling team-game data, 2014-15 through 2025-26...")
    games = pull_team_games()
    print(f"[Q1]   rows: {len(games):,}")
    print(f"[Q1]   seasons: {sorted(games.season_label.dropna().unique())}")

    print("[Q1] Aggregating to team-season-type...")
    agg = aggregate_team_season(games, ["team_abbreviation", "season_label", "season_type"])
    print(f"[Q1]   rows: {len(agg):,}")

    print("[Q1] Building cross-tab...")
    ct = build_crosstab(agg, games)

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    parquet_path = TABLES_DIR / "q1_crosstab.parquet"
    md_path = TABLES_DIR / "q1_crosstab.md"
    agg_path = TABLES_DIR / "q1_team_season_agg.parquet"

    ct.to_parquet(parquet_path)
    agg.to_parquet(agg_path)
    md_path.write_text(
        "# Q1 cross-tab\n\n"
        "Generated by `analyses/q1/build.py`. Values are season totals divided by season totals; CIs are bootstrap percentile on the 25-26 Wolves playoff sample (resampled at the game level).\n\n"
        + render_markdown(ct)
        + "\n",
        encoding="utf-8",
    )
    print(f"[Q1] Wrote {parquet_path.relative_to(REPO)}")
    print(f"[Q1] Wrote {md_path.relative_to(REPO)}")
    print(f"[Q1] Wrote {agg_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
