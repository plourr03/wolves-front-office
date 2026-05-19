"""Phase 4: predictive validation of LAFI.

Three regressions per spec section 4, each run three ways (Full LAFI, Sharp
LAFI, individual components).

Regression A: playoff overperformance vs SRS + LAFI + season FE
Regression B: ORtg decay vs LAFI + opp DRtg + season FE
Regression C: series upset probability vs LAFI differential + net-rating diff

Default sample excludes 2019-20, 2020-21 (COVID disruptions) and 2025-26
(in-progress playoffs). Robustness checks include them via flags.

All coefficients reported with bootstrap CIs (1000 resamples, seed=42) and
Benjamini-Hochberg multiple-testing correction across the three primary
regressions.

SRS is approximated by season-aggregate net rating from
nba_team_advanced_stats. The spec accepts this substitution; a robustness
check using a true SRS computed from box scores can be added later.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from analyses.q0a_lafi import config, data, composite as composite_mod


# Default exclusions for the predictive validation per spec section 9 and
# user instruction. Bubble + COVID seasons treated as structurally distinct.
DEFAULT_EXCLUDED_VALIDATION_YEARS = (2019, 2020)
# 2025-26 has in-progress playoffs; exclude from the historical validation
# sample. It is the target prediction, not part of the training data.
TARGET_YEAR = 2025

BOOTSTRAP_N = 1000
BOOTSTRAP_SEED = 42


# ---------------------------------------------------------------------------
# Validation dataset construction
# ---------------------------------------------------------------------------


def _team_season_outcomes(years, include_covid: bool) -> pd.DataFrame:
    """For each (team, season) build the outcomes used as dependent variables:
    playoff_wins, rs_ortg, po_ortg, rs_net_rating, po_net_rating, made_playoffs.

    Excludes 2025-26 from the playoff side (playoffs in progress).
    Excludes 2019-20 and 2020-21 by default.
    """
    rs = data.load_team_season_summary(years=years, season_types=["Regular Season"])
    po = data.load_team_season_summary(years=years, season_types=["Playoffs"])

    rs = rs[["team_id", "team_abbreviation", "season_start_year", "gp",
             "off_rating", "def_rating", "net_rating", "pace", "poss_total"]].rename(
                 columns={"off_rating": "rs_ortg", "def_rating": "rs_drtg",
                          "net_rating": "rs_net_rating", "pace": "rs_pace",
                          "gp": "rs_gp", "poss_total": "rs_poss"})

    po = po[["team_id", "season_start_year", "gp",
             "off_rating", "def_rating", "net_rating", "poss_total"]].rename(
                 columns={"off_rating": "po_ortg", "def_rating": "po_drtg",
                          "net_rating": "po_net_rating",
                          "gp": "po_gp", "poss_total": "po_poss"})

    df = rs.merge(po, on=["team_id", "season_start_year"], how="left")
    df["made_playoffs"] = df["po_gp"].fillna(0) > 0

    # Playoff wins per team-season.
    yr_lo, yr_hi = min(years), max(years)
    sql = """
        SELECT team_id, (season_id %% 10000)::int AS season_start_year,
               SUM(CASE WHEN wl='W' THEN 1 ELSE 0 END) AS playoff_wins
        FROM nba_games
        WHERE season_type='Playoffs'
          AND (season_id %% 10000) BETWEEN %s AND %s
        GROUP BY team_id, season_start_year
    """
    from lib import db
    wins = db.query(sql, (yr_lo, yr_hi))
    wins["playoff_wins"] = pd.to_numeric(wins["playoff_wins"], errors="coerce")
    df = df.merge(wins, on=["team_id", "season_start_year"], how="left")
    df["playoff_wins"] = df["playoff_wins"].fillna(0)

    # ORtg decay (negative typically; less is more decay).
    df["ortg_decay"] = df["po_ortg"] - df["rs_ortg"]

    # Apply exclusions.
    excluded = set()
    if not include_covid:
        excluded.update(DEFAULT_EXCLUDED_VALIDATION_YEARS)
    excluded.add(TARGET_YEAR)
    df = df[~df["season_start_year"].isin(excluded)].copy()

    return df


def _playoff_opponent_drtg_avg(years, include_covid: bool) -> pd.DataFrame:
    """For each (team, season) in playoffs, compute the average of opponents'
    regular-season DRtg, weighted by games played in playoffs against them.
    """
    yr_lo, yr_hi = min(years), max(years)
    # All playoff games with opponent paired.
    sql = """
        SELECT a.team_id, (a.season_id %% 10000)::int AS season_start_year,
               b.team_id AS opp_team_id, COUNT(*) AS games_vs_opp
        FROM nba_games a
        JOIN nba_games b ON a.game_id = b.game_id AND a.team_id <> b.team_id
        WHERE a.season_type='Playoffs'
          AND (a.season_id %% 10000) BETWEEN %s AND %s
        GROUP BY a.team_id, season_start_year, b.team_id
    """
    from lib import db
    games = db.query(sql, (yr_lo, yr_hi))
    games["games_vs_opp"] = pd.to_numeric(games["games_vs_opp"], errors="coerce")

    # Opponent RS DRtg per (team_id, season).
    rs = data.load_team_season_summary(years=years, season_types=["Regular Season"])
    rs = rs[["team_id", "season_start_year", "def_rating"]].rename(
        columns={"def_rating": "rs_drtg", "team_id": "opp_team_id"})

    merged = games.merge(rs, on=["opp_team_id", "season_start_year"], how="left")
    merged["w_drtg"] = merged["games_vs_opp"] * merged["rs_drtg"]

    agg = (merged.groupby(["team_id", "season_start_year"], as_index=False)
                 .agg(opp_drtg_weighted_sum=("w_drtg", "sum"),
                      games_total=("games_vs_opp", "sum")))
    agg["opp_avg_drtg"] = agg["opp_drtg_weighted_sum"] / agg["games_total"]

    excluded = set()
    if not include_covid:
        excluded.update(DEFAULT_EXCLUDED_VALIDATION_YEARS)
    excluded.add(TARGET_YEAR)
    agg = agg[~agg["season_start_year"].isin(excluded)].copy()
    return agg[["team_id", "season_start_year", "opp_avg_drtg"]]


def _playoff_series(years, include_covid: bool) -> pd.DataFrame:
    """Derive playoff series from nba_games. One row per (season, team_A, team_B)
    pair (ordered so team_A_id < team_B_id), with wins for each side and winner.
    """
    yr_lo, yr_hi = min(years), max(years)
    sql = """
        SELECT (a.season_id %% 10000)::int AS season_start_year,
               LEAST(a.team_id, b.team_id) AS team_a_id,
               GREATEST(a.team_id, b.team_id) AS team_b_id,
               SUM(CASE WHEN a.wl='W' AND a.team_id < b.team_id THEN 1
                        WHEN b.wl='W' AND b.team_id < a.team_id THEN 1
                        ELSE 0 END) AS team_a_wins,
               SUM(CASE WHEN a.wl='W' AND a.team_id > b.team_id THEN 1
                        WHEN b.wl='W' AND b.team_id > a.team_id THEN 1
                        ELSE 0 END) AS team_b_wins,
               COUNT(*) / 2 AS games_played
        FROM nba_games a
        JOIN nba_games b ON a.game_id = b.game_id AND a.team_id <> b.team_id
        WHERE a.season_type='Playoffs'
          AND (a.season_id %% 10000) BETWEEN %s AND %s
        GROUP BY season_start_year, team_a_id, team_b_id
    """
    from lib import db
    s = db.query(sql, (yr_lo, yr_hi))
    for c in ("team_a_wins", "team_b_wins", "games_played"):
        s[c] = pd.to_numeric(s[c], errors="coerce")
    s["team_a_won"] = (s["team_a_wins"] > s["team_b_wins"]).astype(int)

    excluded = set()
    if not include_covid:
        excluded.update(DEFAULT_EXCLUDED_VALIDATION_YEARS)
    excluded.add(TARGET_YEAR)
    s = s[~s["season_start_year"].isin(excluded)].copy()
    return s


def build_validation_dataset(
    composite_df: pd.DataFrame,
    years=config.DEFAULT_SEASON_START_YEARS,
    include_covid: bool = False,
) -> dict:
    """Return a dict of dataframes ready for the three regressions.

    Keys:
      team_season_outcomes  : team-season with playoff outcomes and LAFI
      playoff_team_seasons  : restricted to teams that made the playoffs
      series                : series-level pairs with both teams' LAFI joined
    """
    outcomes = _team_season_outcomes(years, include_covid)
    opp_drtg = _playoff_opponent_drtg_avg(years, include_covid)

    # Merge composite LAFI scores.
    lafi = composite_df.copy()
    lafi = lafi[lafi["season_type"] == "Regular Season"]
    lafi_keep = ["team_id", "season_start_year", "lafi_weighted_pct_sum", "lafi_pct"]
    component_cols = list(composite_mod.COMPONENT_MODULES)
    for c in component_cols:
        if f"{c}_pct" in lafi.columns:
            lafi_keep.append(f"{c}_pct")
    if "sharp_lafi_pct" in lafi.columns:
        lafi_keep += ["sharp_lafi_weighted_pct_sum", "sharp_lafi_pct"]
    lafi = lafi[lafi_keep].drop_duplicates(["team_id", "season_start_year"])
    outcomes = outcomes.merge(lafi, on=["team_id", "season_start_year"], how="inner")
    outcomes = outcomes.merge(opp_drtg, on=["team_id", "season_start_year"], how="left")

    playoff_teams = outcomes[outcomes["made_playoffs"]].copy()

    # Series-level: join LAFI for both teams.
    series = _playoff_series(years, include_covid)
    series_lafi_a = lafi.rename(columns={
        "team_id": "team_a_id",
        "lafi_weighted_pct_sum": "lafi_a_w",
        "lafi_pct": "lafi_a_pct",
        "sharp_lafi_weighted_pct_sum": "sharp_a_w",
        "sharp_lafi_pct": "sharp_a_pct",
    })
    series_lafi_b = lafi.rename(columns={
        "team_id": "team_b_id",
        "lafi_weighted_pct_sum": "lafi_b_w",
        "lafi_pct": "lafi_b_pct",
        "sharp_lafi_weighted_pct_sum": "sharp_b_w",
        "sharp_lafi_pct": "sharp_b_pct",
    })
    # Trim component cols to non-conflicting names with suffix for each side.
    series = series.merge(
        series_lafi_a.rename(columns={f"{c}_pct": f"{c}_a_pct" for c in component_cols}),
        on=["team_a_id", "season_start_year"], how="inner")
    series = series.merge(
        series_lafi_b.rename(columns={f"{c}_pct": f"{c}_b_pct" for c in component_cols}),
        on=["team_b_id", "season_start_year"], how="inner")

    # Net rating differential for the series (uses outcomes table).
    nr = outcomes[["team_id", "season_start_year", "rs_net_rating"]].rename(
        columns={"team_id": "team_a_id", "rs_net_rating": "nr_a"})
    series = series.merge(nr, on=["team_a_id", "season_start_year"], how="left")
    nr = nr.rename(columns={"team_a_id": "team_b_id", "nr_a": "nr_b"})
    series = series.merge(nr, on=["team_b_id", "season_start_year"], how="left")

    # Define favorite (higher net rating) and whether favorite won.
    series["favorite_is_a"] = (series["nr_a"] >= series["nr_b"]).astype(int)
    series["favorite_won"] = np.where(
        series["favorite_is_a"] == 1, series["team_a_won"], 1 - series["team_a_won"]
    )
    series["nr_diff_fav_minus_other"] = np.where(
        series["favorite_is_a"] == 1,
        series["nr_a"] - series["nr_b"], series["nr_b"] - series["nr_a"])
    series["lafi_diff_fav_minus_other"] = np.where(
        series["favorite_is_a"] == 1,
        series["lafi_a_pct"] - series["lafi_b_pct"],
        series["lafi_b_pct"] - series["lafi_a_pct"])
    series["sharp_diff_fav_minus_other"] = np.where(
        series["favorite_is_a"] == 1,
        series["sharp_a_pct"] - series["sharp_b_pct"],
        series["sharp_b_pct"] - series["sharp_a_pct"])

    return {
        "team_season_outcomes": outcomes,
        "playoff_team_seasons": playoff_teams,
        "series": series,
    }


# ---------------------------------------------------------------------------
# Regression helpers
# ---------------------------------------------------------------------------


def _add_season_fe(df: pd.DataFrame) -> pd.DataFrame:
    """Add season fixed-effect dummies (drop one as reference)."""
    seasons = sorted(df["season_start_year"].unique())
    out = df.copy()
    for s in seasons[1:]:
        out[f"season_{s}"] = (out["season_start_year"] == s).astype(int)
    return out, [f"season_{s}" for s in seasons[1:]]


def _ols_with_bootstrap(
    df: pd.DataFrame, y_col: str, x_cols: list[str], n_resamples: int = BOOTSTRAP_N,
    seed: int = BOOTSTRAP_SEED,
) -> pd.DataFrame:
    """Fit OLS once for the point estimate, then bootstrap for CIs.

    Returns a DataFrame indexed by variable with columns:
      coef, p_value, ci_lo_2.5, ci_hi_97.5, ci_lo_bootstrap, ci_hi_bootstrap, n.
    """
    work = df.dropna(subset=[y_col] + x_cols).copy()
    X = sm.add_constant(work[x_cols].astype(float))
    y = work[y_col].astype(float)
    fit = sm.OLS(y, X).fit()

    rng = np.random.default_rng(seed)
    boot = []
    n = len(work)
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        sub = work.iloc[idx]
        Xs = sm.add_constant(sub[x_cols].astype(float))
        ys = sub[y_col].astype(float)
        try:
            f = sm.OLS(ys, Xs).fit()
            boot.append(f.params.values)
        except Exception:
            continue
    boot = np.array(boot)
    lo = np.quantile(boot, 0.025, axis=0)
    hi = np.quantile(boot, 0.975, axis=0)
    out = pd.DataFrame({
        "coef": fit.params.values,
        "p_value": fit.pvalues.values,
        "ci_lo_boot": lo,
        "ci_hi_boot": hi,
    }, index=fit.params.index)
    out.attrs["n"] = n
    out.attrs["r2"] = fit.rsquared
    out.attrs["r2_adj"] = fit.rsquared_adj
    return out


def _logit_with_bootstrap(
    df: pd.DataFrame, y_col: str, x_cols: list[str], n_resamples: int = BOOTSTRAP_N,
    seed: int = BOOTSTRAP_SEED,
) -> pd.DataFrame:
    work = df.dropna(subset=[y_col] + x_cols).copy()
    X = sm.add_constant(work[x_cols].astype(float))
    y = work[y_col].astype(int)
    try:
        fit = sm.Logit(y, X).fit(disp=0)
    except Exception as e:
        # Fall back to empty result with NaN
        idx = ["const"] + x_cols
        return pd.DataFrame({"coef": [np.nan]*len(idx),
                             "p_value": [np.nan]*len(idx),
                             "ci_lo_boot": [np.nan]*len(idx),
                             "ci_hi_boot": [np.nan]*len(idx)},
                            index=idx)

    rng = np.random.default_rng(seed)
    boot = []
    n = len(work)
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        sub = work.iloc[idx]
        Xs = sm.add_constant(sub[x_cols].astype(float))
        ys = sub[y_col].astype(int)
        try:
            f = sm.Logit(ys, Xs).fit(disp=0)
            boot.append(f.params.values)
        except Exception:
            continue
    boot = np.array(boot)
    lo = np.quantile(boot, 0.025, axis=0)
    hi = np.quantile(boot, 0.975, axis=0)
    out = pd.DataFrame({
        "coef": fit.params.values,
        "p_value": fit.pvalues.values,
        "ci_lo_boot": lo,
        "ci_hi_boot": hi,
    }, index=fit.params.index)
    out.attrs["n"] = n
    out.attrs["pseudo_r2"] = float(fit.prsquared)
    return out


# ---------------------------------------------------------------------------
# The three regressions, each run three ways
# ---------------------------------------------------------------------------


def regression_a(playoff_teams: pd.DataFrame, lafi_col: str) -> pd.DataFrame:
    """playoff_wins ~ rs_net_rating + LAFI + season_FE
    Run on playoff team-seasons only.
    """
    df, fe_cols = _add_season_fe(playoff_teams)
    return _ols_with_bootstrap(df, "playoff_wins",
                               ["rs_net_rating", lafi_col] + fe_cols)


def regression_a_components(playoff_teams: pd.DataFrame, component_cols: list[str]) -> pd.DataFrame:
    """Same DV, but all 5 components as separate predictors."""
    df, fe_cols = _add_season_fe(playoff_teams)
    return _ols_with_bootstrap(df, "playoff_wins",
                               ["rs_net_rating"] + component_cols + fe_cols)


def regression_b(playoff_teams: pd.DataFrame, lafi_col: str) -> pd.DataFrame:
    """ortg_decay ~ LAFI + opp_avg_drtg + season_FE
    DV is playoff ORtg minus regular season ORtg.
    """
    df, fe_cols = _add_season_fe(playoff_teams)
    return _ols_with_bootstrap(df, "ortg_decay",
                               [lafi_col, "opp_avg_drtg"] + fe_cols)


def regression_b_components(playoff_teams: pd.DataFrame, component_cols: list[str]) -> pd.DataFrame:
    df, fe_cols = _add_season_fe(playoff_teams)
    return _ols_with_bootstrap(df, "ortg_decay",
                               component_cols + ["opp_avg_drtg"] + fe_cols)


def regression_c(series: pd.DataFrame, lafi_diff_col: str) -> pd.DataFrame:
    """favorite_won ~ lafi_diff (favorite minus opponent) + net rating diff
    Logistic regression at the series level.
    """
    return _logit_with_bootstrap(series, "favorite_won",
                                 [lafi_diff_col, "nr_diff_fav_minus_other"])


# ---------------------------------------------------------------------------
# Robustness checks (post-primary)
# ---------------------------------------------------------------------------


def regression_a_c1_only(playoff_teams: pd.DataFrame) -> pd.DataFrame:
    """Univariate version of Regression A using only C1 (Ball Stickiness).

    Specific hypothesis from user analysis: if C1 is doing all the predictive
    work in the multivariate components regression, a univariate model with
    only C1 + rs_net_rating + season FE should produce a tighter and cleaner
    estimate of the C1 coefficient. Not methodology fishing: the hypothesis is
    grounded in the components regression where only C1 approached significance.
    """
    df, fe_cols = _add_season_fe(playoff_teams)
    return _ols_with_bootstrap(
        df, "playoff_wins",
        ["rs_net_rating", "C1_ball_stickiness_pct"] + fe_cols,
    )


def regression_a_binary(playoff_teams: pd.DataFrame, lafi_col: str,
                         threshold_wins: int = 4) -> pd.DataFrame:
    """Logistic version of Regression A using binary DV.

    DV: 1 if the team won >= threshold_wins playoff games (default 4: advanced
    past the first round), 0 otherwise.

    Specific hypothesis: continuous playoff wins is too noisy because of
    bracket draws. A binary outcome may be cleaner.
    """
    df = playoff_teams.copy()
    df["advanced_past_r1"] = (df["playoff_wins"] >= threshold_wins).astype(int)
    df, fe_cols = _add_season_fe(df)
    return _logit_with_bootstrap(
        df, "advanced_past_r1",
        ["rs_net_rating", lafi_col] + fe_cols,
    )


# ---------------------------------------------------------------------------
# Multiple testing correction
# ---------------------------------------------------------------------------


def apply_bh_correction(p_values: list[float], alpha: float = 0.05) -> dict:
    """Benjamini-Hochberg across the primary LAFI coefficients (one per
    regression). Returns dict of {test_name: (raw_p, adj_p, reject)}.
    """
    reject, adj_p, _, _ = multipletests(p_values, alpha=alpha, method="fdr_bh")
    return {"raw": p_values, "adj": adj_p.tolist(), "reject": reject.tolist()}
