"""
Q1 charts. Builds the team-level visualizations from the cross-tab data
produced by analyses.q1.build.

Charts produced (PNG):
    q1_four_factors_radar.png
        Wolves 25-26 RS, Wolves 25-26 PO, League 25-26 PO on the eight
        four-factor metrics. Values plotted as percentile rank within the
        25-26 league so the axes are comparable.

    q1_dropoff_comparison.png
        Horizontal bar chart. One row per metric. Bars for Wolves 25-26
        dropoff, league 25-26 dropoff, league historical dropoff. Sorted
        by Wolves excess dropoff magnitude.

    q1_game_trajectory.png
        Wolves 25-26 ORtg and DRtg per playoff game, with regular-season
        baseline reference lines.

    q1_three_point_decline.png
        Specific zoom on the three-point story: 3PA rate and 3PT% across
        25-26 RS, 25-26 PO, and the 24-25/23-24 PO comparisons.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from analyses.q1.data import pull_team_games
from analyses.q1.metrics import aggregate_team_season


REPO = Path(__file__).resolve().parents[2]
CHARTS_DIR = REPO / "outputs" / "charts"
TABLES_DIR = REPO / "outputs" / "tables"


plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

WOLVES_BLUE  = "#0C2340"
WOLVES_GREEN = "#236192"
LEAGUE_GREY  = "#7A8B99"
ACCENT_RED   = "#C8102E"


def _percentile_within(values: pd.Series, ref: pd.Series) -> pd.Series:
    """Convert each value to its percentile rank within the reference series."""
    ref = ref.dropna()
    return values.apply(lambda v: (ref < v).mean() if pd.notna(v) else np.nan)


def four_factors_radar(agg: pd.DataFrame, out: Path) -> None:
    """Radar of the offensive and defensive four factors, plotted as
    percentile-within-league for the 25-26 season so all axes share a scale.
    Higher = better for the team (we flip defensive metrics where appropriate)."""

    metrics_oriented = [
        ("efg_pct",        +1, "eFG%"),
        ("tov_pct",        -1, "TOV% (lower)"),
        ("oreb_pct",       +1, "OREB%"),
        ("ft_per_fga",     +1, "FT / FGA"),
        ("opp_efg_pct",    -1, "Opp eFG% (lower)"),
        ("opp_tov_pct",    +1, "Opp TOV%"),
        ("dreb_pct",       +1, "DREB%"),
        ("opp_ft_per_fga", -1, "Opp FT/FGA (lower)"),
    ]

    rs_league = agg[(agg.season_label == "2025-26") & (agg.season_type == "Regular Season")]
    po_league = agg[(agg.season_label == "2025-26") & (agg.season_type == "Playoffs")]

    def pctile_for(row: pd.Series, ref: pd.DataFrame) -> list[float]:
        out = []
        for m, sign, _ in metrics_oriented:
            v = row[m]
            r = ref[m] * sign
            out.append(float((r < v * sign).mean()))
        return out

    wolves_rs = agg[(agg.team_abbreviation == "MIN") & (agg.season_label == "2025-26") & (agg.season_type == "Regular Season")].iloc[0]
    wolves_po = agg[(agg.team_abbreviation == "MIN") & (agg.season_label == "2025-26") & (agg.season_type == "Playoffs")].iloc[0]
    league_po_mean = po_league[[m for m, _, _ in metrics_oriented]].mean()
    league_po_mean_row = pd.Series({m: league_po_mean[m] for m, _, _ in metrics_oriented})

    rs_pct = pctile_for(wolves_rs, rs_league)
    po_pct = pctile_for(wolves_po, po_league)
    lp_pct = pctile_for(league_po_mean_row, po_league)

    labels = [lab for _, _, lab in metrics_oriented]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    def closeloop(xs):
        return xs + xs[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, closeloop(rs_pct), color=WOLVES_BLUE, linewidth=2, label="MIN 25-26 RS")
    ax.fill(angles, closeloop(rs_pct), color=WOLVES_BLUE, alpha=0.12)
    ax.plot(angles, closeloop(po_pct), color=ACCENT_RED, linewidth=2, label="MIN 25-26 PO")
    ax.fill(angles, closeloop(po_pct), color=ACCENT_RED, alpha=0.18)
    ax.plot(angles, closeloop(lp_pct), color=LEAGUE_GREY, linewidth=1.5, linestyle="--", label="League 25-26 PO avg")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.set_yticklabels(["25th", "50th", "75th"], fontsize=8, color="#666")
    ax.set_title("Wolves four factors, percentile within 25-26 league\nhigher = better in all axes",
                 fontsize=13, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.10))
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def dropoff_comparison(crosstab: pd.DataFrame, out: Path) -> None:
    """Horizontal bar: one row per metric. Three bars per metric:
    Wolves 25-26 dropoff, league 25-26 dropoff, league historical dropoff."""
    rows = [
        ("ortg",              "Off. rating"),
        ("efg_pct",           "eFG%"),
        ("three_pt_rate",     "3PA rate"),
        ("three_pt_pct",      "3PT%"),
        ("ft_per_fga",        "FT / FGA"),
        ("tov_pct",           "TOV%"),
        ("oreb_pct",          "OREB%"),
        ("drtg",              "Def. rating"),
        ("opp_efg_pct",       "Opp eFG%"),
        ("opp_three_pt_rate", "Opp 3PA rate"),
        ("opp_three_pt_pct",  "Opp 3PT%"),
        ("opp_ft_per_fga",    "Opp FT/FGA"),
        ("dreb_pct",          "DREB%"),
        ("net_rtg",           "Net rating"),
    ]
    pct_rows = {"efg_pct","tov_pct","oreb_pct","ft_per_fga","three_pt_rate","three_pt_pct",
                "opp_efg_pct","opp_tov_pct","dreb_pct","opp_ft_per_fga","opp_three_pt_rate","opp_three_pt_pct"}

    fig, ax = plt.subplots(figsize=(10, 8))
    y = np.arange(len(rows))
    height = 0.27

    def scaled(m, v):
        if pd.isna(v): return 0.0
        return v * 100 if m in pct_rows else v

    wolves = [scaled(m, crosstab.at[m, "MIN 25-26 dropoff (PO - RS)"]) for m, _ in rows]
    league = [scaled(m, crosstab.at[m, "League 25-26 dropoff"]) for m, _ in rows]
    hist   = [scaled(m, crosstab.at[m, "League historical dropoff"]) for m, _ in rows]

    ax.barh(y - height, wolves, height=height, color=WOLVES_BLUE, label="MIN 25-26")
    ax.barh(y,          league, height=height, color=WOLVES_GREEN, label="League 25-26 PO avg")
    ax.barh(y + height, hist,   height=height, color=LEAGUE_GREY, label="League 10-yr historical")

    ax.set_yticks(y)
    ax.set_yticklabels([lab for _, lab in rows])
    ax.invert_yaxis()
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Playoff dropoff (PO − RS). Units: rating points, or percentage points")
    ax.set_title("Where the 25-26 Wolves diverged from norm in the playoffs",
                 fontsize=13, pad=12)
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def game_trajectory(games: pd.DataFrame, out: Path) -> None:
    """Wolves 25-26 playoff per-game ORtg and DRtg with RS baselines."""
    wp = games[(games.team_abbreviation == "MIN")
               & (games.season_label == "2025-26")
               & (games.season_type == "Playoffs")].sort_values("game_date").copy()
    wp["ortg_game"] = 100.0 * wp["pts"]     / wp["possessions"]
    wp["drtg_game"] = 100.0 * wp["opp_pts"] / wp["possessions"]
    wp["game_no"] = np.arange(1, len(wp) + 1)

    rs = games[(games.team_abbreviation == "MIN")
               & (games.season_label == "2025-26")
               & (games.season_type == "Regular Season")]
    rs_ortg = 100.0 * rs["pts"].sum() / rs["possessions"].sum()
    rs_drtg = 100.0 * rs["opp_pts"].sum() / rs["possessions"].sum()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(wp["game_no"], wp["ortg_game"], marker="o", color=ACCENT_RED, label="Off. rating", linewidth=2)
    ax.plot(wp["game_no"], wp["drtg_game"], marker="s", color=WOLVES_BLUE, label="Def. rating", linewidth=2)
    ax.axhline(rs_ortg, color=ACCENT_RED, linestyle="--", alpha=0.5, label=f"RS Off. ({rs_ortg:.1f})")
    ax.axhline(rs_drtg, color=WOLVES_BLUE, linestyle="--", alpha=0.5, label=f"RS Def. ({rs_drtg:.1f})")
    for i, row in wp.iterrows():
        opp = row["opp_abbr"]
        result = row["wl"]
        ax.annotate(f"{opp} {result}", xy=(row["game_no"], row["ortg_game"]),
                    xytext=(0, 8), textcoords="offset points", ha="center", fontsize=7)
    ax.set_xlabel("Playoff game number")
    ax.set_ylabel("Points per 100 possessions")
    ax.set_title("Wolves 25-26 playoffs: per-game offensive and defensive rating",
                 fontsize=13, pad=12)
    ax.legend(loc="lower right", ncol=2, fontsize=8)
    ax.set_xticks(wp["game_no"])
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def three_point_decline(agg: pd.DataFrame, out: Path) -> None:
    """The three-point story: Wolves and league across seasons."""
    rows = []
    for season in ["2023-24", "2024-25", "2025-26"]:
        for stype in ["Regular Season", "Playoffs"]:
            mn = agg[(agg.team_abbreviation == "MIN") & (agg.season_label == season) & (agg.season_type == stype)]
            lg = agg[(agg.season_label == season) & (agg.season_type == stype)]
            if len(mn) == 0: continue
            rows.append({
                "season": season, "stype": stype,
                "min_3pa_rate": mn["three_pt_rate"].iloc[0],
                "min_3pt_pct":  mn["three_pt_pct"].iloc[0],
                "lg_3pa_rate":  lg["three_pt_rate"].mean(),
                "lg_3pt_pct":   lg["three_pt_pct"].mean(),
            })
    df = pd.DataFrame(rows)
    df["label"] = df["season"] + " " + df["stype"].map({"Regular Season": "RS", "Playoffs": "PO"})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    x = np.arange(len(df))
    w = 0.35

    ax1.bar(x - w/2, df["min_3pa_rate"] * 100, width=w, color=WOLVES_BLUE, label="Wolves")
    ax1.bar(x + w/2, df["lg_3pa_rate"] * 100, width=w, color=LEAGUE_GREY, label="League avg")
    ax1.set_xticks(x); ax1.set_xticklabels(df["label"], rotation=20, ha="right")
    ax1.set_ylabel("3PA rate (% of FGA)")
    ax1.set_title("Three-point attempt rate")
    ax1.legend(); ax1.set_ylim(0, 55)

    ax2.bar(x - w/2, df["min_3pt_pct"] * 100, width=w, color=WOLVES_BLUE, label="Wolves")
    ax2.bar(x + w/2, df["lg_3pt_pct"] * 100, width=w, color=LEAGUE_GREY, label="League avg")
    ax2.set_xticks(x); ax2.set_xticklabels(df["label"], rotation=20, ha="right")
    ax2.set_ylabel("3PT%")
    ax2.set_title("Three-point shooting accuracy")
    ax2.legend(); ax2.set_ylim(0, 45)

    fig.suptitle("The three-point story", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    print("[Q1 charts] Pulling team-game data...")
    games = pull_team_games()
    print("[Q1 charts] Aggregating...")
    agg = aggregate_team_season(games, ["team_abbreviation", "season_label", "season_type"])
    ct = pd.read_parquet(TABLES_DIR / "q1_crosstab.parquet")

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    print("[Q1 charts] four_factors_radar...")
    four_factors_radar(agg, CHARTS_DIR / "q1_four_factors_radar.png")
    print("[Q1 charts] dropoff_comparison...")
    dropoff_comparison(ct, CHARTS_DIR / "q1_dropoff_comparison.png")
    print("[Q1 charts] game_trajectory...")
    game_trajectory(games, CHARTS_DIR / "q1_game_trajectory.png")
    print("[Q1 charts] three_point_decline...")
    three_point_decline(agg, CHARTS_DIR / "q1_three_point_decline.png")
    print("[Q1 charts] done. Saved to outputs/charts/")


if __name__ == "__main__":
    main()
