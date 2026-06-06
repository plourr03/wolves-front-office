"""Phase 6: hero visualizations for the Wolves diagnosis deliverable.

Six charts:
  1. Index Map (RS net rating vs LAFI, colored by playoff outcome)
  2. Wolves Trajectory (5 component lines across Edwards era)
  3. Predictive Validation Bar (LAFI decile vs P(advance past R1))
  4. League Fingerprint (30 teams 2025-26 LAFI horizontal bars)
  5. Historical Case Studies (2x2 component-profile small multiples)
  6. Wolves Quadrant Migration (C1, C2 plane with Edwards-era arrows)

All charts saved to outputs/charts/q0a_lafi/ as PNG, 300dpi.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from analyses.q0a_lafi import config


# Style: clean, presentation-ready.
plt.rcParams.update({
    "figure.dpi": 100,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.grid": True,
    "axes.grid.axis": "both",
    "grid.alpha": 0.25,
    "grid.linestyle": "-",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

WOLVES_BLUE = "#0C2340"
WOLVES_GREEN = "#236192"
HIGHLIGHT = "#78BE20"
LEAGUE_GREY = "#A0A0A0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _outcome_category(wins):
    if pd.isna(wins) or wins == 0:
        return "Missed playoffs / R1 sweep"
    if wins <= 3:
        return "Round 1 exit"
    if wins <= 7:
        return "Round 2 exit"
    if wins <= 11:
        return "Conference Finals"
    if wins <= 15:
        return "Finals appearance"
    return "Champion"


OUTCOME_ORDER = [
    "Missed playoffs / R1 sweep",
    "Round 1 exit",
    "Round 2 exit",
    "Conference Finals",
    "Finals appearance",
    "Champion",
]
OUTCOME_COLORS = {
    "Missed playoffs / R1 sweep": "#D9D9D9",
    "Round 1 exit":               "#A6A6A6",
    "Round 2 exit":               "#FFB347",
    "Conference Finals":          "#1F77B4",
    "Finals appearance":          "#9467BD",
    "Champion":                   "#FFD700",
}


def _load_composite_and_validation():
    comp = pd.read_csv(config.TABLE_DIR / "lafi_composite_5component.csv")
    comp = comp[comp["season_type"] == "Regular Season"]
    val = pd.read_csv(config.TABLE_DIR / "validation" / "validation_dataset_playoff_teams.csv")
    return comp, val


# ---------------------------------------------------------------------------
# Chart 1: Index Map
# ---------------------------------------------------------------------------


def chart_index_map(out_dir: Path) -> Path:
    comp, val = _load_composite_and_validation()

    # Build merged frame with net rating + LAFI + playoff outcome.
    # Need RS net rating per team-season; use val for playoff teams,
    # and pull all team-seasons net rating from composite computation chain.
    # The validation_dataset has playoff teams only. For the scatter we
    # include all team-seasons we have, and color by playoff_wins category.
    from analyses.q0a_lafi import data as data_mod
    sum_df = data_mod.load_team_season_summary(season_types=["Regular Season"])
    sum_df = sum_df[["team_id", "team_abbreviation", "season_start_year", "net_rating"]]

    # Playoff wins per team-season.
    from lib import db
    sql = ("SELECT MOD(season_id, 10000) AS season_start_year, team_id, "
           "SUM(CASE WHEN wl='W' THEN 1 ELSE 0 END) AS playoff_wins "
           "FROM nba.nba_games WHERE season_type='Playoffs' GROUP BY 1, 2")
    po = db.query(sql)
    po["season_start_year"] = po["season_start_year"].astype(int)
    po["playoff_wins"] = pd.to_numeric(po["playoff_wins"])

    df = comp.merge(sum_df, on=["team_id", "team_abbreviation", "season_start_year"], how="inner")
    df = df.merge(po, on=["team_id", "season_start_year"], how="left")
    df["outcome"] = df["playoff_wins"].apply(_outcome_category)

    fig, ax = plt.subplots(figsize=(11, 7))
    for outcome in OUTCOME_ORDER:
        sub = df[df["outcome"] == outcome]
        ax.scatter(sub["net_rating"], sub["lafi_pct"],
                   c=OUTCOME_COLORS[outcome], s=44, alpha=0.75,
                   edgecolors="white", linewidths=0.6, label=outcome,
                   zorder=2)

    # Highlight notable team-seasons.
    annotations = [
        ("GSW", 2016, "2016 GSW (champion)"),
        ("HOU", 2017, "2018 HOU"),
        ("MIN", 2023, "2023 MIN WCF"),
        ("MIN", 2025, "2025 MIN"),
        ("BOS", 2023, "2024 BOS champion"),
        ("OKC", 2024, "2024 OKC champion"),
        ("ATL", 2021, "2022 ATL"),
        ("DAL", 2022, "2022 DAL"),
    ]
    for abbr, yr, label in annotations:
        sub = df[(df["team_abbreviation"] == abbr) & (df["season_start_year"] == yr)]
        if not sub.empty:
            r = sub.iloc[0]
            ax.annotate(label, (r["net_rating"], r["lafi_pct"]),
                        xytext=(6, 6), textcoords="offset points",
                        fontsize=9, color="#222")

    # Highlight 2025-26 MIN with red ring.
    min2025 = df[(df["team_abbreviation"] == "MIN") & (df["season_start_year"] == 2025)]
    if not min2025.empty:
        r = min2025.iloc[0]
        ax.scatter(r["net_rating"], r["lafi_pct"], s=240, facecolors="none",
                   edgecolors="#C8102E", linewidths=2.5, zorder=3)

    ax.set_xlabel("Regular season net rating")
    ax.set_ylabel("Full LAFI percentile")
    ax.set_title("The Index Map: where pickup-ball teams sit at any given talent level")
    ax.legend(loc="lower left", framealpha=0.95, fontsize=9, title="Playoff outcome")
    ax.axhline(50, color="#666", linewidth=0.7, linestyle="--", alpha=0.5)
    ax.axvline(0, color="#666", linewidth=0.7, linestyle="--", alpha=0.5)
    ax.set_xlim(df["net_rating"].min() - 1, df["net_rating"].max() + 1)
    ax.set_ylim(-2, 102)
    path = out_dir / "01_index_map.png"
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Chart 2: Wolves Trajectory
# ---------------------------------------------------------------------------


def chart_wolves_trajectory(out_dir: Path) -> Path:
    comp, _ = _load_composite_and_validation()
    w = comp[(comp["team_abbreviation"] == "MIN")
             & (comp["season_start_year"].between(2021, 2025))].sort_values("season_start_year")
    years = [int(y) for y in w["season_start_year"]]
    labels = [f"{y}-{(y+1)%100:02d}" for y in years]

    components = [
        ("C1_ball_stickiness_pct", "C1 Ball Stickiness", "#888"),
        ("C2_movement_death_pct", "C2 Motion Death", "#C8102E"),
        ("C3_isolation_reliance_pct", "C3 Iso Reliance", "#236192"),
        ("C4_action_poverty_pct", "C4 Action Poverty", "#888"),
        ("C5_shot_quality_decay_pct", "C5 Shot Quality Decay", HIGHLIGHT),
    ]

    fig, ax = plt.subplots(figsize=(10, 6.5))
    for col, label, color in components:
        is_lockstep = col in ("C2_movement_death_pct", "C3_isolation_reliance_pct", "C5_shot_quality_decay_pct")
        lw = 2.6 if is_lockstep else 1.4
        alpha = 1.0 if is_lockstep else 0.55
        ax.plot(labels, w[col].values, label=label, color=color,
                linewidth=lw, marker="o", markersize=7, alpha=alpha)

    # Mark Acts.
    ax.axvspan(-0.3, 0.5, alpha=0.06, color="#888", zorder=0)  # 2021-22
    ax.axvspan(0.5, 1.5, alpha=0.10, color="#666", zorder=0)   # Gobert
    ax.axvspan(1.5, 2.5, alpha=0.10, color=HIGHLIGHT, zorder=0)  # WCF
    ax.axvspan(2.5, 3.5, alpha=0.10, color="#FFB347", zorder=0)  # Randle Y1
    ax.axvspan(3.5, 4.3, alpha=0.18, color="#C8102E", zorder=0)  # Q4

    annotations = {
        1: ("Gobert\nintegration", 95),
        2: ("WCF year\n(most designed)", 95),
        3: ("Randle\nintegration", 95),
        4: ("Q4 collapse", 95),
    }
    for i, (label, y) in annotations.items():
        ax.text(i, y, label, ha="center", va="top", fontsize=9,
                color="#333", fontweight="bold")

    ax.set_xlabel("Season")
    ax.set_ylabel("Percentile rank (higher = more pickup-like)")
    ax.set_title("The four-act Wolves Edwards-era trajectory")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    ax.set_ylim(0, 100)
    ax.set_xlim(-0.4, 4.4)
    path = out_dir / "02_wolves_trajectory.png"
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Chart 3: Predictive Validation Bar
# ---------------------------------------------------------------------------


def chart_predictive_validation(out_dir: Path) -> Path:
    val = pd.read_csv(config.TABLE_DIR / "validation" / "validation_dataset_playoff_teams.csv")
    val["advanced"] = (val["playoff_wins"] >= 4).astype(int)
    # Bin LAFI percentile into deciles.
    val["decile"] = pd.cut(val["lafi_pct"], bins=np.arange(0, 101, 10),
                            labels=range(1, 11), include_lowest=True).astype(int)
    rng = np.random.default_rng(42)
    rows = []
    for d, sub in val.groupby("decile"):
        n = len(sub)
        if n == 0:
            continue
        rate = sub["advanced"].mean()
        # bootstrap CI
        boot = []
        for _ in range(1000):
            idx = rng.integers(0, n, size=n)
            boot.append(sub["advanced"].values[idx].mean())
        lo = float(np.quantile(boot, 0.025))
        hi = float(np.quantile(boot, 0.975))
        rows.append({"decile": int(d), "rate": rate, "ci_lo": lo, "ci_hi": hi, "n": n})
    g = pd.DataFrame(rows).sort_values("decile")

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#236192" if d <= 5 else "#C8102E" for d in g["decile"]]
    bars = ax.bar(g["decile"], g["rate"], color=colors, alpha=0.85,
                  edgecolor="white", linewidth=1.2)
    # Error bars
    yerr_low = g["rate"] - g["ci_lo"]
    yerr_high = g["ci_hi"] - g["rate"]
    ax.errorbar(g["decile"], g["rate"], yerr=[yerr_low, yerr_high],
                fmt="none", color="#222", capsize=5, capthick=1.4, lw=1.2)
    # n labels at the top
    for d, n in zip(g["decile"], g["n"]):
        ax.text(d, 1.02, f"n={n}", ha="center", va="bottom", fontsize=8, color="#555")

    ax.set_xticks(range(1, 11))
    ax.set_xticklabels([f"{d}\n({10*(d-1)+1}-{10*d})" for d in range(1, 11)])
    ax.set_xlabel("LAFI decile (1 = most designed, 10 = most pickup-like)")
    ax.set_ylabel("P(advance past round 1)")
    ax.set_title("LAFI predicts advancement past round 1\n(playoff team-seasons 2014-15 through 2024-25, excl. COVID)")
    ax.set_ylim(0, 1.1)
    ax.axhline(0.5, color="#666", linestyle="--", linewidth=0.7, alpha=0.4)
    path = out_dir / "03_predictive_validation.png"
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Chart 4: League Fingerprint
# ---------------------------------------------------------------------------


def chart_league_fingerprint(out_dir: Path) -> Path:
    comp, _ = _load_composite_and_validation()
    latest = comp[comp["season_start_year"] == 2025].sort_values("lafi_pct", ascending=True)
    teams = latest["team_abbreviation"].values
    vals = latest["lafi_pct"].values
    sharp = latest["sharp_lafi_pct"].values

    fig, ax = plt.subplots(figsize=(8.5, 10))
    colors = ["#C8102E" if t == "MIN" else "#BBB" for t in teams]
    ax.barh(teams, vals, color=colors, alpha=0.85, edgecolor="white", linewidth=0.8, label="Full LAFI")
    # Sharp LAFI as a thin marker.
    ax.plot(sharp, teams, "o", color="#1B5E20", markersize=6, zorder=3, label="Sharp LAFI (C2+C3+C5)")

    median = float(np.median(vals))
    ax.axvline(median, color="#444", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(median + 1, 0.5, f"League median ({median:.0f})", fontsize=8, color="#444")

    # Highlight Wolves.
    min_idx = list(teams).index("MIN")
    ax.text(vals[min_idx] + 2, min_idx, f"Wolves: Full {vals[min_idx]:.0f}, Sharp {sharp[min_idx]:.0f}",
            fontsize=9, color="#C8102E", fontweight="bold", va="center")

    ax.set_xlabel("LAFI percentile (higher = more pickup-like)")
    ax.set_title("League fingerprint, 2025-26 Regular Season")
    ax.legend(loc="lower right", framealpha=0.95, fontsize=9)
    ax.set_xlim(0, 105)
    path = out_dir / "04_league_fingerprint.png"
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Chart 5: Historical Case Studies (2x2)
# ---------------------------------------------------------------------------


def chart_historical_case_studies(out_dir: Path) -> Path:
    comp, _ = _load_composite_and_validation()
    cases = [
        ("HOU", 2017, "2017-18 Houston (Harden) - lost WCF Game 7"),
        ("OKC", 2017, "2017-18 OKC (Westbrook-PG) - lost Round 1"),
        ("DAL", 2022, "2022-23 Dallas (pre-Kyrie Luka) - missed playoffs"),
        ("MIN", 2025, "2025-26 Minnesota (Edwards) - ongoing"),
    ]
    cols = ["C1_ball_stickiness_pct", "C2_movement_death_pct", "C3_isolation_reliance_pct",
            "C4_action_poverty_pct", "C5_shot_quality_decay_pct"]
    short_names = ["C1\nStickiness", "C2\nMotion Death", "C3\nIso", "C4\nAction Poverty", "C5\nShot Quality"]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    for ax, (abbr, yr, title) in zip(axes.flat, cases):
        row = comp[(comp["team_abbreviation"] == abbr) & (comp["season_start_year"] == yr)]
        if row.empty:
            ax.text(0.5, 0.5, f"No data for {abbr} {yr}", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(title)
            continue
        vals = [float(row.iloc[0][c]) for c in cols]
        colors = ["#C8102E" if (abbr == "MIN") else "#236192" for _ in cols]
        bars = ax.bar(short_names, vals, color=colors, alpha=0.82, edgecolor="white", linewidth=1.2)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width()/2, v + 1.5, f"{v:.0f}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.axhline(50, color="#888", linestyle="--", linewidth=0.7, alpha=0.5)
        ax.set_ylim(0, 105)
        ax.set_ylabel("Percentile")
        ax.set_title(title, fontsize=11)
        if abbr != "MIN":
            # Note historical = C1-extreme (Q3 single-star pickup pattern)
            ax.text(0.02, 0.96, "Q3 pattern: C1 high", transform=ax.transAxes,
                    fontsize=8, color="#444", va="top")
        else:
            ax.text(0.02, 0.96, "Q4 pattern: C2+C3+C5 high, C1 moderate", transform=ax.transAxes,
                    fontsize=8, color="#C8102E", va="top", fontweight="bold")

    fig.suptitle("Historical case studies: Q3 single-star pickup vs the Wolves' Q4 distributed pickup", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    path = out_dir / "05_historical_case_studies.png"
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Chart 6: Wolves Quadrant Migration (NEW, per user request)
# ---------------------------------------------------------------------------


def chart_quadrant_migration(out_dir: Path) -> Path:
    comp, _ = _load_composite_and_validation()
    latest = comp[comp["season_start_year"] == 2025]
    fig, ax = plt.subplots(figsize=(10, 9))

    # Background: 2025-26 league teams as grey dots.
    ax.scatter(latest["C1_ball_stickiness_pct"], latest["C2_movement_death_pct"],
               s=80, color=LEAGUE_GREY, alpha=0.55, edgecolors="white", linewidths=0.6, zorder=1)
    for _, r in latest.iterrows():
        if r["team_abbreviation"] != "MIN":
            ax.annotate(r["team_abbreviation"], (r["C1_ball_stickiness_pct"], r["C2_movement_death_pct"]),
                        xytext=(4, 4), textcoords="offset points", fontsize=8, color="#666")

    # Wolves Edwards-era seasons connected by arrows.
    w = comp[(comp["team_abbreviation"] == "MIN")
             & (comp["season_start_year"].between(2022, 2025))].sort_values("season_start_year")
    xs = w["C1_ball_stickiness_pct"].values
    ys = w["C2_movement_death_pct"].values
    yrs = w["season_start_year"].astype(int).values
    # Draw arrows season-to-season
    for i in range(len(xs) - 1):
        ax.annotate("", xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                    arrowprops=dict(arrowstyle="->", color=WOLVES_BLUE, lw=2.4, alpha=0.85),
                    zorder=3)
    ax.scatter(xs, ys, s=240, color="#C8102E", edgecolors="white", linewidths=2,
               zorder=4)
    for x, y, yr in zip(xs, ys, yrs):
        ax.annotate(f"MIN {yr}-{(yr+1)%100:02d}", (x, y), xytext=(8, 8),
                    textcoords="offset points", fontsize=10, fontweight="bold",
                    color=WOLVES_BLUE, zorder=5)

    # Quadrant dividers and labels.
    ax.axvline(50, color="#444", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.axhline(50, color="#444", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.text(8, 92, "Q4: distributed pickup\n(low sticky, high motion death)\n← Wolves now",
            fontsize=10, color="#C8102E", fontweight="bold", va="top")
    ax.text(92, 92, "Q3: single-star pickup\n(high sticky, high motion death)",
            fontsize=10, color="#444", fontweight="bold", va="top", ha="right")
    ax.text(8, 8, "Q1: designed offense\n(low sticky, low motion death)",
            fontsize=10, color="#1B5E20", fontweight="bold", va="bottom")
    ax.text(92, 8, "Q2: star-fed motion\n(high sticky, low motion death)",
            fontsize=10, color="#444", fontweight="bold", va="bottom", ha="right")

    ax.set_xlabel("C1 Ball Stickiness (percentile)")
    ax.set_ylabel("C2 Motion Death (percentile)")
    ax.set_title("Wolves quadrant migration across the Edwards era\n(grey dots = 2025-26 league)")
    ax.set_xlim(-2, 102)
    ax.set_ylim(-2, 102)
    path = out_dir / "06_wolves_quadrant_migration.png"
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def build_all_charts() -> list[Path]:
    out_dir = config.CHART_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for fn in (chart_index_map, chart_wolves_trajectory, chart_predictive_validation,
               chart_league_fingerprint, chart_historical_case_studies,
               chart_quadrant_migration):
        print(f"  Building {fn.__name__}...")
        try:
            paths.append(fn(out_dir))
            print(f"    Wrote {paths[-1].name}")
        except Exception as e:
            print(f"    FAILED: {e}")
    return paths
