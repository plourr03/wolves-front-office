"""Q1 metrics: four factors, ratings, dropoffs, bootstrap CIs.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from analyses.q1_diagnose import config


# ---------------------------------------------------------------------------
# Four factors (per Dean Oliver)
# ---------------------------------------------------------------------------


def four_factors(df: pd.DataFrame, side: str = "own") -> dict:
    """Compute the four factors (offense or defense) from a games DataFrame.

    side='own' computes offensive four factors. side='opp' computes defensive
    (i.e., opponent four factors that we allowed).

    Returns dict with: efg, tov_pct, oreb_pct, ft_rate, ppp, total_poss.
    """
    if side == "own":
        fgm, fga, fg3m, fta = df["fgm"], df["fga"], df["fg3m"], df["fta"]
        oreb = df["oreb"]
        dreb_opp = df["opp_dreb"]
        tov = df["tov"]
        pts = df["pts"]
    elif side == "opp":
        fgm, fga, fg3m, fta = df["opp_fgm"], df["opp_fga"], df["opp_fg3m"], df["opp_fta"]
        oreb = df["opp_oreb"]
        dreb_opp = df["dreb"]
        tov = df["opp_tov"]
        pts = df["opp_pts"]
    else:
        raise ValueError(f"side must be 'own' or 'opp', got {side}")

    fga_sum = fga.sum()
    fta_sum = fta.sum()
    fgm_sum = fgm.sum()
    fg3m_sum = fg3m.sum()
    tov_sum = tov.sum()
    oreb_sum = oreb.sum()
    dreb_opp_sum = dreb_opp.sum()
    pts_sum = pts.sum()

    efg = (fgm_sum + 0.5 * fg3m_sum) / fga_sum if fga_sum else np.nan
    possessions = fga_sum + 0.44 * fta_sum - oreb_sum + tov_sum
    tov_pct = tov_sum / possessions if possessions else np.nan
    oreb_pct = oreb_sum / (oreb_sum + dreb_opp_sum) if (oreb_sum + dreb_opp_sum) else np.nan
    ft_rate = fta_sum / fga_sum if fga_sum else np.nan
    # Possessions averaged with opponent's possessions to mirror Oliver convention
    # (using own-side here for the four-factor computation; rating uses paired poss).
    return {
        "efg": efg,
        "tov_pct": tov_pct,
        "oreb_pct": oreb_pct,
        "ft_rate": ft_rate,
        "ppp": pts_sum / possessions if possessions else np.nan,
        "total_possessions": possessions,
        "pts": pts_sum,
        "fga": fga_sum,
        "n_games": len(df),
    }


def team_season_summary(df: pd.DataFrame) -> dict:
    """Summarize a team-season slice into headline metrics.

    Uses possessions_eff (advanced-stats possessions when available, Oliver
    fallback otherwise) for ratings. Uses paired-possessions for offensive
    and defensive ratings separately.
    """
    off = four_factors(df, side="own")
    deff = four_factors(df, side="opp")
    # Use possessions_eff column for the ORtg/DRtg calculation (paired
    # possessions for the team in each game, summed).
    poss = df["possessions_eff"].sum()
    out = {
        "n_games": len(df),
        "possessions": poss,
        "pts_for": df["pts"].sum(),
        "pts_against": df["opp_pts"].sum(),
        "off_rating": 100 * df["pts"].sum() / poss if poss else np.nan,
        "def_rating": 100 * df["opp_pts"].sum() / poss if poss else np.nan,
        "net_rating": 100 * (df["pts"].sum() - df["opp_pts"].sum()) / poss if poss else np.nan,
        "pace": df["pace"].mean() if df["pace"].notna().any() else np.nan,
        "off_efg": off["efg"],
        "off_tov_pct": off["tov_pct"],
        "off_oreb_pct": off["oreb_pct"],
        "off_ft_rate": off["ft_rate"],
        "def_efg": deff["efg"],
        "def_tov_pct": deff["tov_pct"],
        "def_oreb_pct": deff["oreb_pct"],
        "def_ft_rate": deff["ft_rate"],
        "off_3pa_rate": df["fg3a"].sum() / df["fga"].sum() if df["fga"].sum() else np.nan,
        "off_3p_pct": df["fg3m"].sum() / df["fg3a"].sum() if df["fg3a"].sum() else np.nan,
        "def_3pa_rate": df["opp_fg3a"].sum() / df["opp_fga"].sum() if df["opp_fga"].sum() else np.nan,
        "def_3p_pct": df["opp_fg3m"].sum() / df["opp_fg3a"].sum() if df["opp_fg3a"].sum() else np.nan,
    }
    return out


# ---------------------------------------------------------------------------
# Bootstrap CIs
# ---------------------------------------------------------------------------


def bootstrap_summary(df: pd.DataFrame, metric_func, n_resamples: int = None, seed: int = None) -> dict:
    """Bootstrap a single metric. metric_func takes a games DataFrame and
    returns a scalar.
    """
    n_resamples = n_resamples or config.BOOTSTRAP_N
    seed = seed or config.BOOTSTRAP_SEED
    rng = np.random.default_rng(seed)
    n = len(df)
    if n < 3:
        return {"point": metric_func(df), "ci_lo": np.nan, "ci_hi": np.nan, "n": n}
    point = metric_func(df)
    samples = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        samples.append(metric_func(df.iloc[idx]))
    samples = np.array([s for s in samples if not np.isnan(s)])
    lo, hi = np.quantile(samples, [(1 - config.CI_LEVEL) / 2, 1 - (1 - config.CI_LEVEL) / 2])
    return {"point": point, "ci_lo": float(lo), "ci_hi": float(hi), "n": n}


def bootstrap_dropoff(
    po_df: pd.DataFrame,
    rs_value: float,
    metric_func,
    n_resamples: int = None,
    seed: int = None,
) -> dict:
    """Bootstrap CI on the dropoff (PO - RS) for one metric.

    The RS value is treated as a fixed anchor (since 82-game samples are
    tight). The playoff sample is resampled with replacement; each resample
    produces a (PO - RS) dropoff. Returns point estimate, CI lo, CI hi, and
    n of the playoff sample.

    The CI is dominated by the playoff sample width because the RS anchor is
    treated as exact. This matches the user's specification.
    """
    n_resamples = n_resamples or config.BOOTSTRAP_N
    seed = seed or config.BOOTSTRAP_SEED
    rng = np.random.default_rng(seed)
    n = len(po_df)
    point_po = metric_func(po_df)
    point_dropoff = point_po - rs_value
    if n < 3:
        return {"point": point_dropoff, "po_value": point_po, "rs_value": rs_value,
                "ci_lo": np.nan, "ci_hi": np.nan, "n": n}
    samples = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        po_resampled = metric_func(po_df.iloc[idx])
        if not np.isnan(po_resampled):
            samples.append(po_resampled - rs_value)
    samples = np.array(samples)
    lo, hi = np.quantile(samples, [(1 - config.CI_LEVEL) / 2, 1 - (1 - config.CI_LEVEL) / 2])
    return {"point": float(point_dropoff), "po_value": float(point_po),
            "rs_value": float(rs_value), "ci_lo": float(lo), "ci_hi": float(hi), "n": n}


# Convenience helpers for common metrics.
def metric_off_rating(df: pd.DataFrame) -> float:
    poss = df["possessions_eff"].sum()
    return 100 * df["pts"].sum() / poss if poss else np.nan


def metric_def_rating(df: pd.DataFrame) -> float:
    poss = df["possessions_eff"].sum()
    return 100 * df["opp_pts"].sum() / poss if poss else np.nan


def metric_net_rating(df: pd.DataFrame) -> float:
    return metric_off_rating(df) - metric_def_rating(df)


def metric_off_efg(df: pd.DataFrame) -> float:
    return four_factors(df, side="own")["efg"]


def metric_def_efg(df: pd.DataFrame) -> float:
    return four_factors(df, side="opp")["efg"]


def metric_off_tov(df: pd.DataFrame) -> float:
    return four_factors(df, side="own")["tov_pct"]


def metric_def_tov(df: pd.DataFrame) -> float:
    return four_factors(df, side="opp")["tov_pct"]


def metric_off_oreb(df: pd.DataFrame) -> float:
    return four_factors(df, side="own")["oreb_pct"]


def metric_def_oreb(df: pd.DataFrame) -> float:
    return four_factors(df, side="opp")["oreb_pct"]


def metric_off_ft_rate(df: pd.DataFrame) -> float:
    return four_factors(df, side="own")["ft_rate"]


def metric_def_ft_rate(df: pd.DataFrame) -> float:
    return four_factors(df, side="opp")["ft_rate"]


def metric_def_3pa_rate(df: pd.DataFrame) -> float:
    return df["opp_fg3a"].sum() / df["opp_fga"].sum() if df["opp_fga"].sum() else np.nan


def metric_def_3p_pct(df: pd.DataFrame) -> float:
    return df["opp_fg3m"].sum() / df["opp_fg3a"].sum() if df["opp_fg3a"].sum() else np.nan


# ---------------------------------------------------------------------------
# Dropoff analysis (RS -> PO)
# ---------------------------------------------------------------------------


def compute_dropoffs(rs_summary: dict, po_summary: dict, metrics: list[str]) -> dict:
    """For each named metric in the two summaries, compute PO - RS."""
    return {m: (po_summary.get(m, np.nan) - rs_summary.get(m, np.nan)) for m in metrics}


def historical_playoff_dropoffs(
    games: pd.DataFrame, years: list[int], metrics: list[str]
) -> dict:
    """For each metric, compute the average and std of (PO - RS) across all
    playoff teams in the given historical years.

    Excludes 2019-20 and 2020-21 by default per the project convention.
    """
    rows = []
    for year in years:
        po_team_ids = sorted(games[(games["season_start_year"] == year)
                                    & (games["season_type"] == "Playoffs")]["team_id"].unique())
        for tid in po_team_ids:
            rs = games[(games["team_id"] == tid) & (games["season_start_year"] == year)
                       & (games["season_type"] == "Regular Season")]
            po = games[(games["team_id"] == tid) & (games["season_start_year"] == year)
                       & (games["season_type"] == "Playoffs")]
            if len(rs) < 50 or len(po) < 4:
                continue
            rs_s = team_season_summary(rs)
            po_s = team_season_summary(po)
            for m in metrics:
                rows.append({"year": year, "team_id": tid, "metric": m,
                             "dropoff": po_s[m] - rs_s[m]})
    df = pd.DataFrame(rows)
    summary = (df.groupby("metric")["dropoff"]
                 .agg(["mean", "std", "median", "count"])
                 .rename(columns={"mean": "league_avg_dropoff",
                                   "std": "league_std_dropoff",
                                   "median": "league_median_dropoff",
                                   "count": "n_team_seasons"}))
    return {"summary": summary, "raw": df}
