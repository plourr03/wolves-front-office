"""LAFI composite assembly and Phase 3 diagnostics.

Combines the five component outputs into the LAFI composite, then runs the
spec's correlation matrix and PCA checks, plus the additional diagnostics the
user flagged: sharp LAFI (C2+C3+C5 subset), Wolves-specific correlations vs
league-wide.

Component weights from spec section 3.3:
    LAFI = 0.25*BS + 0.20*MD + 0.20*IR + 0.20*AP + 0.15*SQD

Sharp LAFI subset (motion death + iso reliance + shot quality decay only):
    weights renormalized to sum to 1.
"""
from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd

from analyses.q0a_lafi import config
from analyses.q0a_lafi.components import (
    ball_stickiness, movement_death, isolation_reliance,
    action_poverty, shot_quality_decay,
)


COMPONENT_MODULES = {
    "C1_ball_stickiness":     ball_stickiness,
    "C2_movement_death":      movement_death,
    "C3_isolation_reliance":  isolation_reliance,
    "C4_action_poverty":      action_poverty,
    "C5_shot_quality_decay":  shot_quality_decay,
}

COMPONENT_WEIGHTS = {
    "C1_ball_stickiness":     0.25,
    "C2_movement_death":      0.20,
    "C3_isolation_reliance":  0.20,
    "C4_action_poverty":      0.20,
    "C5_shot_quality_decay":  0.15,
}

# Sharp LAFI: only the three components that moved in lockstep across the
# Wolves' Edwards era (motion death + iso reliance + shot quality decay).
# Weights renormalized to sum to 1.
SHARP_COMPONENTS = ("C2_movement_death", "C3_isolation_reliance", "C5_shot_quality_decay")
_sharp_total = sum(COMPONENT_WEIGHTS[c] for c in SHARP_COMPONENTS)
SHARP_WEIGHTS = {c: COMPONENT_WEIGHTS[c] / _sharp_total for c in SHARP_COMPONENTS}


def _key(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """Reduce a component output to identity columns plus percentile_rank,
    renamed with the prefix so multiple components can be merged side by side.
    """
    out = df[["team_id", "team_abbreviation", "season_start_year",
              "season_type", "raw_score", "percentile_rank"]].copy()
    out = out.rename(columns={
        "raw_score": f"{prefix}_z",
        "percentile_rank": f"{prefix}_pct",
    })
    return out


def assemble_composite(
    years: Iterable[int] = config.DEFAULT_SEASON_START_YEARS,
    season_types: Optional[Iterable[str]] = ("Regular Season",),
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build both the 5-component canonical composite and the 4-component
    robustness composite (drops C5).

    Returns:
        (composite_5, composite_4)
        Each has one row per (team, season, season_type) on the inner-join
        of the relevant components, plus weighted-sum LAFI scores and
        percentile-rank LAFI scores.
    """
    parts = {}
    for name, mod in COMPONENT_MODULES.items():
        parts[name] = _key(mod.compute(years=years, season_types=season_types), name)

    # 5-component: inner join all 5 (sample bounded to seasons all components cover)
    five = parts["C1_ball_stickiness"]
    for name in ("C2_movement_death", "C3_isolation_reliance",
                 "C4_action_poverty", "C5_shot_quality_decay"):
        five = five.merge(parts[name],
                          on=["team_id", "team_abbreviation",
                              "season_start_year", "season_type"],
                          how="inner")

    # 4-component: inner join C1-C4 only (wider season window)
    four = parts["C1_ball_stickiness"]
    for name in ("C2_movement_death", "C3_isolation_reliance",
                 "C4_action_poverty"):
        four = four.merge(parts[name],
                          on=["team_id", "team_abbreviation",
                              "season_start_year", "season_type"],
                          how="inner")

    five = _attach_composite_scores(five, components=list(COMPONENT_MODULES))
    four = _attach_composite_scores(four,
                                    components=[c for c in COMPONENT_MODULES
                                                if c != "C5_shot_quality_decay"])

    # Sharp LAFI (uses 5-component sample because it needs C5).
    sharp = (five[[f"{c}_pct" for c in SHARP_COMPONENTS]]
             .mul([SHARP_WEIGHTS[c] for c in SHARP_COMPONENTS], axis=1)
             .sum(axis=1))
    five["sharp_lafi_weighted_pct_sum"] = sharp
    five["sharp_lafi_pct"] = sharp.rank(pct=True, method="average") * 100.0

    return five, four


def _attach_composite_scores(df: pd.DataFrame, components: list[str]) -> pd.DataFrame:
    """Compute weighted_pct_sum and lafi_pct from a list of component prefixes."""
    weights_sub = {c: COMPONENT_WEIGHTS[c] for c in components}
    total_w = sum(weights_sub.values())
    weights_sub = {c: w / total_w for c, w in weights_sub.items()}
    pcts = df[[f"{c}_pct" for c in components]]
    weighted = pcts.mul([weights_sub[c] for c in components], axis=1).sum(axis=1)
    df = df.copy()
    df["lafi_weighted_pct_sum"] = weighted
    df["lafi_pct"] = weighted.rank(pct=True, method="average") * 100.0
    return df


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def correlation_matrix(composite: pd.DataFrame, component_cols: list[str]) -> pd.DataFrame:
    """Pearson correlation matrix across the named component _z columns."""
    z_cols = [f"{c}_z" for c in component_cols]
    return composite[z_cols].corr().round(3)


def correlation_pair_summary(composite: pd.DataFrame, component_cols: list[str]) -> pd.DataFrame:
    """Long-format pairwise correlations sorted descending. Easier to scan than
    a matrix."""
    z_cols = [f"{c}_z" for c in component_cols]
    rows = []
    for i, a in enumerate(z_cols):
        for b in z_cols[i+1:]:
            rows.append({
                "pair": f"{a[:-2]} x {b[:-2]}",
                "pearson_r": round(float(composite[[a, b]].corr().iloc[0, 1]), 3),
            })
    return pd.DataFrame(rows).sort_values("pearson_r", ascending=False).reset_index(drop=True)


def pca_diagnostic(composite: pd.DataFrame, component_cols: list[str]) -> dict:
    """PCA on the z-scored components via correlation-matrix eigendecomposition.

    Returns:
      - eigenvalues, variance_explained, cum_variance_explained
      - loadings: (n_components x n_components) matrix, columns = PCs
    """
    z_cols = [f"{c}_z" for c in component_cols]
    X = composite[z_cols].dropna().values
    corr = np.corrcoef(X.T)
    eigvals, eigvecs = np.linalg.eigh(corr)
    # eigh returns ascending; reverse to descending
    order = eigvals.argsort()[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    total = eigvals.sum()
    return {
        "components": component_cols,
        "eigenvalues": eigvals,
        "variance_explained": eigvals / total,
        "cum_variance_explained": np.cumsum(eigvals / total),
        "loadings": pd.DataFrame(eigvecs,
                                 index=component_cols,
                                 columns=[f"PC{i+1}" for i in range(len(component_cols))]),
        "n_samples": X.shape[0],
    }


def wolves_vs_league_correlations(
    composite: pd.DataFrame,
    component_cols: list[str],
    wolves_team_id: int = config.WOLVES_TEAM_ID,
) -> dict:
    """Compare Wolves-only correlations across the Edwards-era seasons against
    league-wide correlations.

    Wolves-only is computed over Wolves seasons in the frame. League is the
    full sample.
    """
    z_cols = [f"{c}_z" for c in component_cols]
    league_corr = composite[z_cols].corr()
    wolves = composite[composite["team_id"] == wolves_team_id]
    if len(wolves) < 3:
        wolves_corr = pd.DataFrame(np.nan, index=z_cols, columns=z_cols)
    else:
        wolves_corr = wolves[z_cols].corr()
    diff = (wolves_corr - league_corr).round(3)
    return {
        "league": league_corr.round(3),
        "wolves": wolves_corr.round(3),
        "wolves_minus_league": diff,
        "n_wolves_rows": len(wolves),
        "n_league_rows": len(composite),
    }
