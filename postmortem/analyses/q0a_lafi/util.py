"""Shared utilities for LAFI components.

The component contract:

    compute(years, season_types) -> pd.DataFrame

with output columns:

    team_id, team_abbreviation,
    season_start_year, season_label, season_type,
    sub_metric columns (one or more, raw values; "_z" suffix for z-scored),
    raw_score        # equally-weighted mean of sub-metric z-scores (component z)
    z_score          # alias for raw_score, kept for clarity downstream
    percentile_rank  # 0-100, computed across the full pool returned

Each component should also expose:

    validate(df) -> None

which prints a qualitative eye-test report (top-5 / bottom-5 of the latest
season, plus the Wolves' trajectory). Eye tests are guardrails against
silently broken metrics.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def z_within_season(
    df: pd.DataFrame,
    value_col: str,
    season_col: str = "season_start_year",
    season_type_col: str = "season_type",
) -> pd.Series:
    """Z-score `value_col` within each (season, season_type) group.

    This is the spec's prescribed normalization (LAFI spec section 3.1). It
    controls for league-wide era drift by comparing each team to its
    contemporaries instead of to historical averages.
    """
    grouped = df.groupby([season_col, season_type_col])[value_col]
    means = grouped.transform("mean")
    stds = grouped.transform("std", ddof=0)
    z = (df[value_col] - means) / stds.replace(0, np.nan)
    return z


def percentile_rank_pooled(series: pd.Series) -> pd.Series:
    """Convert values to 0-100 percentile rank pooled across the input.

    Used for the final LAFI score interpretability. Per spec section 3.3,
    percentile rank is across the full historical sample, not within season.
    """
    return series.rank(pct=True, method="average") * 100.0


def assemble_component_output(
    base: pd.DataFrame,
    sub_metrics: dict[str, pd.Series],
    season_col: str = "season_start_year",
    season_type_col: str = "season_type",
) -> pd.DataFrame:
    """Take a base frame (team-season identity) plus a dict of named sub-metric
    Series (sign-oriented so higher = stickier / more pickup-like) and return
    the standardized component output.

    Each sub-metric:
      - kept as <name>_raw in the output
      - z-scored within (season, season_type) as <name>_z
    Component z = mean of the sub-metric z-scores.
    Percentile rank = 0-100 across the full pool returned.
    """
    out = base.copy()
    z_cols: list[str] = []
    for name, values in sub_metrics.items():
        out[f"{name}_raw"] = values.values
        out[f"{name}_z"] = z_within_season(
            out.assign(_v=values.values),
            "_v",
            season_col=season_col,
            season_type_col=season_type_col,
        ).values
        z_cols.append(f"{name}_z")
        out.drop(columns=["_v"], errors="ignore", inplace=True)
    out["raw_score"] = out[z_cols].mean(axis=1)
    out["z_score"] = out["raw_score"]
    out["percentile_rank"] = percentile_rank_pooled(out["raw_score"])
    return out


def eye_test_report(
    df: pd.DataFrame,
    component_name: str,
    score_col: str = "percentile_rank",
    season_year: int = 2025,
    wolves_team_id: int = 1610612750,
    show_n: int = 8,
) -> None:
    """Print the standard eye-test: top-N / bottom-N teams for the latest
    season, plus the Wolves' trajectory across all seasons in the frame.
    """
    print(f"\n{'='*72}\n[{component_name}] eye-test  (higher = more pickup)\n{'='*72}")
    latest = df[(df["season_start_year"] == season_year) & (df["season_type"] == "Regular Season")]
    if latest.empty:
        print(f"  No rows for season_start_year={season_year} RS. Skipping eye-test.")
        return

    print(f"\nLeague leaders (top {show_n}, season {season_year}-{(season_year+1)%100:02d} RS):")
    top = latest.nlargest(show_n, score_col)
    for _, r in top.iterrows():
        print(f"  #{int(r[score_col]):>3} pct  {r['team_abbreviation']:<5}  raw_z={r['raw_score']:+.2f}")

    print(f"\nLeague tail (bottom {show_n}, same season):")
    bot = latest.nsmallest(show_n, score_col)
    for _, r in bot.iterrows():
        print(f"  #{int(r[score_col]):>3} pct  {r['team_abbreviation']:<5}  raw_z={r['raw_score']:+.2f}")

    wolves = df[(df["team_id"] == wolves_team_id) & (df["season_type"] == "Regular Season")] \
              .sort_values("season_start_year")
    if not wolves.empty:
        has_handler = "top_handler_name" in wolves.columns
        print(f"\nWolves trajectory across loaded seasons (RS only):")
        for _, r in wolves.iterrows():
            yr = int(r["season_start_year"])
            handler = f"  top={r['top_handler_name']}" if has_handler and pd.notna(r.get("top_handler_name")) else ""
            print(f"  {yr}-{(yr+1)%100:02d}  pct={int(r['percentile_rank']):>3}  z={r['raw_score']:+.2f}{handler}")


def write_component_csv(df: pd.DataFrame, component_name: str, out_dir) -> None:
    """Persist the component frame under outputs/tables/q0a_lafi/components/."""
    sub = out_dir / "components"
    sub.mkdir(parents=True, exist_ok=True)
    path = sub / f"{component_name}.csv"
    df.to_csv(path, index=False)
    print(f"  Wrote {path}")


def total_team_possessions_from_advanced(team_summary: pd.DataFrame) -> pd.Series:
    """Helper: pull `poss_total` from team_season_summary frame, indexed for
    consistent merging in components that need a possession denominator."""
    return team_summary.set_index(
        ["team_id", "season_start_year", "season_type"]
    )["poss_total"]


def top_handler_per_team_season(
    player_poss_df: pd.DataFrame,
    value_col: str = "time_of_poss",
    name_col: str = "player_name",
) -> pd.DataFrame:
    """Return one row per (team_id, season_year, season_type) identifying the
    player with the largest value of `value_col` (default: time_of_poss).

    Used to annotate component outputs with "who carried the offense" so the
    Wolves trajectory is legible (e.g., 2024-25 Randle vs 2025-26 Edwards).
    """
    df = player_poss_df.dropna(subset=[value_col]).copy()
    df = df.sort_values(
        ["team_id", "season_year", "season_type", value_col], ascending=[True, True, True, False]
    )
    top = df.groupby(["team_id", "season_year", "season_type"], as_index=False).head(1)
    return top[["team_id", "season_year", "season_type", name_col, value_col]].rename(
        columns={name_col: "top_handler_name", value_col: "top_handler_top"}
    )


def wolves_trajectory_table(
    df: pd.DataFrame,
    wolves_team_id: int = 1610612750,
) -> pd.DataFrame:
    """Return one row per Wolves season-type in `df`, with raw_score, percentile,
    and the top-handler annotation if present.
    """
    cols = ["season_start_year", "season_label", "season_type", "raw_score", "percentile_rank"]
    if "top_handler_name" in df.columns:
        cols.append("top_handler_name")
    out = (df[df["team_id"] == wolves_team_id][cols]
           .sort_values(["season_start_year", "season_type"])
           .reset_index(drop=True))
    return out


def _format_trajectory_markdown(traj: pd.DataFrame) -> str:
    """Render the trajectory table as markdown."""
    if traj.empty:
        return "_(no Wolves rows in this frame)_\n"
    has_handler = "top_handler_name" in traj.columns
    header = "| Season | Type | Raw z | Pct rank"
    align  = "|---|---|---|---"
    if has_handler:
        header += " | Top handler"
        align  += "|---"
    header += " |\n"
    align  += " |\n"
    rows = []
    for _, r in traj.iterrows():
        line = (f"| {r['season_label']} | {r['season_type'][:2]} "
                f"| {r['raw_score']:+.2f} | {int(round(r['percentile_rank']))} ")
        if has_handler:
            line += f"| {r.get('top_handler_name','') or ''} "
        line += "|"
        rows.append(line)
    return header + align + "\n".join(rows) + "\n"


def _format_top_bottom_markdown(df: pd.DataFrame, season_year: int, show_n: int = 8) -> str:
    """Render the latest-season top/bottom-N table as markdown."""
    latest = df[(df["season_start_year"] == season_year) & (df["season_type"] == "Regular Season")]
    if latest.empty:
        return "_(no latest-season rows)_\n"
    top = latest.nlargest(show_n, "percentile_rank")
    bot = latest.nsmallest(show_n, "percentile_rank")
    out = ["**League leaders (top {0}, {1}-{2:02d} RS):**\n".format(
                show_n, season_year, (season_year + 1) % 100)]
    out.append("| Team | Pct | Raw z |\n|---|---|---|\n")
    for _, r in top.iterrows():
        out.append(f"| {r['team_abbreviation']} | {int(round(r['percentile_rank']))} | {r['raw_score']:+.2f} |\n")
    out.append(f"\n**League tail (bottom {show_n}, same season):**\n\n")
    out.append("| Team | Pct | Raw z |\n|---|---|---|\n")
    for _, r in bot.iterrows():
        out.append(f"| {r['team_abbreviation']} | {int(round(r['percentile_rank']))} | {r['raw_score']:+.2f} |\n")
    return "".join(out)


def write_eye_test_markdown(
    component_name: str,
    df: pd.DataFrame,
    out_dir,
    priors_md: str = "",
    investigation_md: str = "",
    season_year: int = 2025,
    wolves_team_id: int = 1610612750,
    show_n: int = 8,
) -> None:
    """Persist a markdown eye-test report for this component.

    Combines latest-season top/bottom rankings, Wolves year-over-year trajectory,
    plus optional sections for stated priors and manual investigation notes.
    """
    sub = out_dir / "components"
    sub.mkdir(parents=True, exist_ok=True)
    path = sub / f"{component_name}_eye_test.md"

    traj = wolves_trajectory_table(df, wolves_team_id=wolves_team_id)
    traj_rs = traj[traj["season_type"] == "Regular Season"] if not traj.empty else traj

    body = []
    body.append(f"# Eye-test: {component_name}\n\n")
    body.append("_Higher percentile = more pickup-like. "
                "Each percentile is pooled across the full team-season sample._\n\n")
    if priors_md:
        body.append("## Priors before running\n\n")
        body.append(priors_md.rstrip() + "\n\n")
    body.append("## League leaderboard\n\n")
    body.append(_format_top_bottom_markdown(df, season_year, show_n))
    body.append("\n## Wolves trajectory\n\n")
    body.append(_format_trajectory_markdown(traj_rs))
    if investigation_md:
        body.append("\n## Investigation notes\n\n")
        body.append(investigation_md.rstrip() + "\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(body))
    print(f"  Wrote {path}")
