"""Gobert career-arc visualization.

Two-panel chart:
- Top: Net impact across career. Public proxy (PIE from warehouse) for
  2013-14 through 2022-23. Project net RAPM for 2023-24, 2024-25, 2025-26.
- Bottom: Offensive vs defensive impact trajectory.

Methodology note: PIE and RAPM are NOT on the same scale. They are plotted
on the same axis with clearly distinct markers/colors so a reader can see
the career shape but understand the source change. PIE roughly tracks
"share of meaningful actions" (league avg ~10). RAPM is per-100-possession
impact (league avg ~0). The chart annotates the distinction.

Sources:
- Historical PIE: nba_player_advanced_stats (NBA Stats API)
- Project RAPM: outputs/tables/q2_localize/rapm_2023_only.csv,
  rapm_2024_only.csv, rapm_2025_only.csv (Wolves-games-only sample)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from lib import db


GOBERT_ID = 203497
CHART_DIR = Path("outputs/charts/q8_player_decisions")
CHART_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR = Path("outputs/tables/q8_player_decisions")
TABLE_DIR.mkdir(parents=True, exist_ok=True)
RAPM_DIR = Path("outputs/tables/q2_localize")


def pull_gobert_career_stats() -> pd.DataFrame:
    """Per-season aggregates from nba_player_advanced_stats joined with
    nba_games for season info.
    """
    sql = """
        SELECT (g.season_id %% 10000)::int AS season_start_year,
               COUNT(*) AS games,
               AVG(pas.pie) AS avg_pie,
               AVG(pas.net_rating) AS avg_net_rtg,
               AVG(pas.offensive_rating) AS avg_off_rtg,
               AVG(pas.defensive_rating) AS avg_def_rtg,
               AVG(pas.minutes_float) AS avg_min
        FROM nba_player_advanced_stats pas
        JOIN nba_games g ON g.game_id = pas.game_id AND g.team_id = pas.team_id
        WHERE pas.person_id = %s
          AND g.season_type = 'Regular Season'
        GROUP BY g.season_id
        ORDER BY season_start_year
    """
    df = db.query(sql, (GOBERT_ID,))
    # Postgres NUMERIC comes back as Decimal; coerce to float for arithmetic
    for c in ("avg_pie", "avg_net_rtg", "avg_off_rtg", "avg_def_rtg", "avg_min"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # PIE in the warehouse is stored as a fraction (0-1); scale to standard PIE (0-100)
    df["avg_pie"] = df["avg_pie"] * 100.0
    df["season_label"] = df["season_start_year"].apply(lambda y: f"{y}-{str(y+1)[-2:]}")
    return df


def load_project_rapm() -> pd.DataFrame:
    """Load Gobert's project RAPM for the 3 most recent seasons."""
    rows = []
    for year in [2023, 2024, 2025]:
        path = RAPM_DIR / f"rapm_{year}_only.csv"
        df = pd.read_csv(path)
        gob = df[df["player_id"] == GOBERT_ID]
        if not gob.empty:
            r = gob.iloc[0]
            rows.append({
                "season_start_year": year,
                "season_label": f"{year}-{str(year+1)[-2:]}",
                "net_rapm": r["net_rapm"],
                "off_rapm": r["off_rapm"],
                "def_rapm": r["def_rapm"],
            })
    return pd.DataFrame(rows)


def build_chart(career: pd.DataFrame, project_rapm: pd.DataFrame, save_path: Path):
    # Filter out the 2013-14 rookie year (9.6 min/game; outlier garbage minutes)
    career = career[career["season_start_year"] >= 2014].copy()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10))

    proj = project_rapm.copy()
    hist = career[career["season_start_year"] < 2023].copy()

    # ---- Top panel: net impact with twin y-axes ----
    # Left axis: PIE (historical)
    color_pie = "#888888"
    ax1.plot(hist["season_start_year"], hist["avg_pie"],
              color=color_pie, linestyle="--", marker="o", markersize=7,
              alpha=0.85, label="Per-game PIE (NBA Stats, left axis)")
    ax1.set_ylabel("Per-game PIE\n(historical proxy)", fontsize=10, color=color_pie)
    ax1.tick_params(axis="y", labelcolor=color_pie)
    # Set PIE range: typical 8-18 for impact players
    ax1.set_ylim(8, 20)

    # Right axis: RAPM (project years)
    ax1r = ax1.twinx()
    color_rapm = "#1a5490"
    ax1r.scatter(proj["season_start_year"], proj["net_rapm"],
                  color=color_rapm, s=220, marker="D", zorder=5,
                  edgecolors="black", linewidths=1.5,
                  label="Project Net RAPM (right axis)")
    # Connect the dots for visual trend
    ax1r.plot(proj["season_start_year"], proj["net_rapm"],
               color=color_rapm, linestyle="-", linewidth=2, alpha=0.7)
    ax1r.set_ylabel("Project Net RAPM\n(per 100 possessions)", fontsize=10, color=color_rapm)
    ax1r.tick_params(axis="y", labelcolor=color_rapm)
    ax1r.axhline(0, color=color_rapm, alpha=0.3, linewidth=0.8, linestyle=":")
    ax1r.set_ylim(-2, 9)

    # Annotate RAPM values
    for _, r in proj.iterrows():
        ax1r.annotate(f"{r['net_rapm']:+.2f}",
                       xy=(r["season_start_year"], r["net_rapm"]),
                       xytext=(0, 12), textcoords="offset points",
                       ha="center", fontsize=10, fontweight="bold",
                       color=color_rapm)

    # Reference lines (team transitions)
    ax1.axvline(2022, color="#cc6600", linestyle=":", alpha=0.7, linewidth=1.5)
    ax1.annotate("Utah → MIN", xy=(2022, 19.5), fontsize=9, color="#cc6600",
                  ha="right", va="top", xytext=(-3, 0), textcoords="offset points")
    ax1.axvline(2024, color="#cc6600", linestyle=":", alpha=0.7, linewidth=1.5)
    ax1.annotate("KAT trade", xy=(2024, 19.5), fontsize=9, color="#cc6600",
                  ha="right", va="top", xytext=(-3, 0), textcoords="offset points")

    ax1.set_xlabel("Season (start year)", fontsize=11)
    ax1.set_title("Rudy Gobert career impact arc\nGray (PIE) is approximate career shape; Blue (RAPM) is load-bearing recent estimate",
                   fontsize=12, loc="left", fontweight="bold")
    ax1.grid(True, alpha=0.3, which="major")

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines1r, labels1r = ax1r.get_legend_handles_labels()
    ax1.legend(lines1 + lines1r, labels1 + labels1r, loc="lower left",
                fontsize=9, framealpha=0.95)

    # ---- Bottom panel: offensive vs defensive split for project years ----
    # Project years only: clean off/def RAPM comparison
    ax2.bar(proj["season_start_year"] - 0.18, proj["off_rapm"],
             width=0.35, color="#cc4444", alpha=0.85, edgecolor="black",
             label="Offensive RAPM (positive = adds points)")
    ax2.bar(proj["season_start_year"] + 0.18, -proj["def_rapm"],
             width=0.35, color="#449944", alpha=0.85, edgecolor="black",
             label="Defensive RAPM saved (sign-flipped; positive = prevents points)")

    # Value labels on bars
    for _, r in proj.iterrows():
        # Offense
        off_val = r["off_rapm"]
        ax2.annotate(f"{off_val:+.2f}",
                       xy=(r["season_start_year"] - 0.18, off_val),
                       xytext=(0, 4 if off_val >= 0 else -12),
                       textcoords="offset points", ha="center", fontsize=9,
                       fontweight="bold", color="#aa2222")
        # Defense (sign-flipped)
        def_val = -r["def_rapm"]
        ax2.annotate(f"{def_val:+.2f}",
                       xy=(r["season_start_year"] + 0.18, def_val),
                       xytext=(0, 4 if def_val >= 0 else -12),
                       textcoords="offset points", ha="center", fontsize=9,
                       fontweight="bold", color="#226622")

    ax2.axhline(0, color="black", alpha=0.4, linewidth=1)
    ax2.set_xticks([2023, 2024, 2025])
    ax2.set_xticklabels(["2023-24", "2024-25", "2025-26"], fontsize=11)
    ax2.set_xlabel("Season", fontsize=11)
    ax2.set_ylabel("RAPM per 100 possessions", fontsize=10)
    ax2.set_title(
        "Project years: Defensive impact INCREASING year-over-year. Offensive impact DECLINING. "
        "Net drop is offense-driven.",
        fontsize=11, loc="left", fontweight="bold")
    ax2.legend(loc="upper left", fontsize=9, framealpha=0.95)
    ax2.grid(True, alpha=0.3, axis="y")

    # Source footer
    fig.text(0.01, 0.005,
              "Sources: NBA Stats API (per-game PIE) via warehouse for 2014-15 through 2022-23. "
              "Project Wolves-games-only RAPM for 2023-24, 2024-25, 2025-26 (separate single-season fits).\n"
              "Top panel uses twin y-axes because PIE and RAPM are not directly comparable. "
              "The shape of each line is informative; the absolute levels are not.",
              fontsize=8, color="#555555", style="italic")

    plt.tight_layout(rect=[0, 0.025, 1, 1])
    plt.savefig(save_path, dpi=160, bbox_inches="tight")
    print(f"Saved {save_path}")


def build_combined_table(career: pd.DataFrame, project_rapm: pd.DataFrame) -> pd.DataFrame:
    """Combined table with both historical and project data per season."""
    hist = career[["season_start_year", "season_label", "games", "avg_min",
                    "avg_pie", "avg_off_rtg", "avg_def_rtg", "avg_net_rtg"]].copy()
    hist["source"] = "warehouse_pie"

    proj = project_rapm[["season_start_year", "season_label",
                          "off_rapm", "def_rapm", "net_rapm"]].copy()
    proj["source"] = "project_rapm"

    return pd.concat([hist, proj], ignore_index=True, sort=False).sort_values("season_start_year")


def run():
    print("Pulling Gobert career stats from warehouse...")
    career = pull_gobert_career_stats()
    print(career.to_string(index=False))

    print("\nLoading project RAPM (3 seasons)...")
    project_rapm = load_project_rapm()
    print(project_rapm.to_string(index=False))

    combined = build_combined_table(career, project_rapm)
    combined.to_csv(TABLE_DIR / "gobert_career_arc.csv", index=False)
    print(f"\nCombined table saved.")

    print("\nBuilding chart...")
    chart_path = CHART_DIR / "gobert_career_arc.png"
    build_chart(career, project_rapm, chart_path)


if __name__ == "__main__":
    run()
