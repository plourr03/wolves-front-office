"""LAFI driver. Runs the analysis end-to-end against the production warehouse.

Phases:
    1. Foundations and data layer (this file's --diagnose flag exercises it)
    2-6. To be wired in as each phase lands.

Usage:
    python -m analyses.q0a_lafi --diagnose    # season universe sanity check
"""
from __future__ import annotations

import argparse

import pandas as pd

from analyses.q0a_lafi import config, data
from analyses.q0a_lafi.components import (
    ball_stickiness, movement_death, isolation_reliance, action_poverty,
    shot_quality_decay,
)
from analyses.q0a_lafi import composite as composite_mod
from analyses.q0a_lafi import validate as validate_mod
from analyses.q0a_lafi import charts as charts_mod


def run_diagnose() -> None:
    print(f"LAFI default season window: {config.DEFAULT_SEASON_START_YEARS[0]}-{config.DEFAULT_SEASON_START_YEARS[-1] + 1} season")
    print(f"  ({config.season_label(config.DEFAULT_SEASON_START_YEARS[0])} through "
          f"{config.season_label(config.DEFAULT_SEASON_START_YEARS[-1])})")
    print()

    print("Pulling season-universe diagnostic from warehouse...")
    df = data.season_universe()
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    print()
    print(df.to_string(index=False))

    out_path = config.TABLE_DIR / "season_universe.csv"
    df.to_csv(out_path, index=False)
    print(f"\nWritten: {out_path}")
    print()
    print("Component-by-season readiness:")
    required = {
        "ball_stickiness":     ["tracking_season_teams"],
        "movement_death":      ["tracking_season_teams"],
        "isolation_reliance":  ["synergy_teams", "tracking_season_teams"],
        "action_poverty":      ["synergy_teams"],
        "shot_quality_decay":  ["tracking_season_teams", "pt_shot_teams"],
    }
    for component, cols in required.items():
        ok_seasons = []
        for _, row in df.iterrows():
            if all(pd.notna(row[c]) and row[c] >= 28 for c in cols):
                ok_seasons.append(f"{row['season_label']} ({row['season_type'][:2]})")
        print(f"  {component:<22} ok for {len(ok_seasons):>2} season-types: {ok_seasons}")


COMPONENT_REGISTRY = {
    "ball_stickiness": ball_stickiness,
    "movement_death": movement_death,
    "isolation_reliance": isolation_reliance,
    "action_poverty": action_poverty,
    "shot_quality_decay": shot_quality_decay,
}


def run_component(name: str) -> None:
    if name not in COMPONENT_REGISTRY:
        raise SystemExit(f"Unknown component '{name}'. Known: {list(COMPONENT_REGISTRY)}")
    mod = COMPONENT_REGISTRY[name]
    print(f"Computing component: {name}")
    df = mod.compute(years=config.DEFAULT_SEASON_START_YEARS, season_types=("Regular Season",))
    print(f"  Returned {len(df):,} (team-season-type) rows.")
    mod.write(df)
    mod.validate(df)


def run_composite() -> None:
    """Phase 3: assemble composite, run correlation matrix and PCA diagnostics."""
    print("Assembling LAFI composite (5-component canonical and 4-component robustness)...")
    five, four = composite_mod.assemble_composite()
    print(f"  5-component sample: {len(five):,} team-seasons (RS)")
    print(f"  4-component sample: {len(four):,} team-seasons (RS)")

    # Persist composite CSVs.
    out5 = config.TABLE_DIR / "lafi_composite_5component.csv"
    out4 = config.TABLE_DIR / "lafi_composite_4component.csv"
    five.to_csv(out5, index=False)
    four.to_csv(out4, index=False)
    print(f"  Wrote {out5}")
    print(f"  Wrote {out4}")

    five_cols = list(composite_mod.COMPONENT_MODULES)
    four_cols = [c for c in five_cols if c != "C5_shot_quality_decay"]

    # --- Wolves 2025-26 composite placement ---
    print("\n" + "="*72)
    print("Wolves 2025-26 LAFI placement")
    print("="*72)
    w5 = five[(five["team_id"] == config.WOLVES_TEAM_ID)
              & (five["season_start_year"] == 2025)
              & (five["season_type"] == "Regular Season")]
    if not w5.empty:
        r = w5.iloc[0]
        print(f"  5-component LAFI: weighted_pct_sum={r['lafi_weighted_pct_sum']:.1f}  pct rank={r['lafi_pct']:.1f}")
        print(f"  Sharp LAFI (C2+C3+C5): weighted_pct_sum={r['sharp_lafi_weighted_pct_sum']:.1f}  pct rank={r['sharp_lafi_pct']:.1f}")
    w4 = four[(four["team_id"] == config.WOLVES_TEAM_ID)
              & (four["season_start_year"] == 2025)
              & (four["season_type"] == "Regular Season")]
    if not w4.empty:
        r = w4.iloc[0]
        print(f"  4-component LAFI: weighted_pct_sum={r['lafi_weighted_pct_sum']:.1f}  pct rank={r['lafi_pct']:.1f}")

    # --- League rank by 5-component LAFI for 2025-26 ---
    print("\n2025-26 RS league LAFI ranking (5-component, top 10):")
    latest5 = five[five["season_start_year"] == 2025].sort_values("lafi_pct", ascending=False)
    for _, r in latest5.head(10).iterrows():
        print(f"  #{int(round(r['lafi_pct'])):>3}  {r['team_abbreviation']:<4}  weighted_sum={r['lafi_weighted_pct_sum']:.1f}")
    print("\n2025-26 RS league LAFI ranking (bottom 10):")
    for _, r in latest5.tail(10).sort_values("lafi_pct").iterrows():
        print(f"  #{int(round(r['lafi_pct'])):>3}  {r['team_abbreviation']:<4}  weighted_sum={r['lafi_weighted_pct_sum']:.1f}")

    print("\n2025-26 RS sharp LAFI ranking (C2+C3+C5, top 10):")
    sharp_latest = five[five["season_start_year"] == 2025].sort_values("sharp_lafi_pct", ascending=False)
    for _, r in sharp_latest.head(10).iterrows():
        print(f"  #{int(round(r['sharp_lafi_pct'])):>3}  {r['team_abbreviation']:<4}  weighted_sum={r['sharp_lafi_weighted_pct_sum']:.1f}")

    # --- Correlation matrix ---
    print("\n" + "="*72)
    print("Correlation matrix (5-component, league-wide pooled)")
    print("="*72)
    corr5 = composite_mod.correlation_matrix(five, five_cols)
    print(corr5.to_string())
    print("\nPairwise correlations sorted (high to low):")
    pairs = composite_mod.correlation_pair_summary(five, five_cols)
    print(pairs.to_string(index=False))

    # --- PCA diagnostic ---
    print("\n" + "="*72)
    print("PCA diagnostic")
    print("="*72)
    pca = composite_mod.pca_diagnostic(five, five_cols)
    print(f"  Sample size: {pca['n_samples']:,}")
    for i, (ev, ve, cve) in enumerate(zip(pca["eigenvalues"], pca["variance_explained"], pca["cum_variance_explained"])):
        print(f"  PC{i+1}: eigenvalue={ev:.3f}  variance_explained={ve*100:.1f}%  cumulative={cve*100:.1f}%")
    print("\nLoadings (each PC's contribution from each component):")
    print(pca["loadings"].round(3).to_string())

    # --- Wolves vs league correlations ---
    print("\n" + "="*72)
    print("Wolves vs league pairwise correlations (the 'three surfaces' check)")
    print("="*72)
    wvl = composite_mod.wolves_vs_league_correlations(five, five_cols)
    print(f"  Wolves rows: {wvl['n_wolves_rows']}  /  League rows: {wvl['n_league_rows']}")
    print("\nLeague-wide:")
    print(wvl["league"].to_string())
    print("\nWolves-only (Edwards-era seasons in the 5-component sample):")
    print(wvl["wolves"].to_string())
    print("\nWolves minus league (positive = Wolves tighter coupling):")
    print(wvl["wolves_minus_league"].to_string())

    # Persist diagnostics summary CSV.
    diag_dir = config.TABLE_DIR / "composite_diagnostics"
    diag_dir.mkdir(parents=True, exist_ok=True)
    corr5.to_csv(diag_dir / "correlation_matrix_league.csv")
    wvl["wolves"].to_csv(diag_dir / "correlation_matrix_wolves.csv")
    wvl["wolves_minus_league"].to_csv(diag_dir / "correlation_matrix_diff.csv")
    pca["loadings"].to_csv(diag_dir / "pca_loadings.csv")
    pd.DataFrame({
        "PC": [f"PC{i+1}" for i in range(len(pca['eigenvalues']))],
        "eigenvalue": pca["eigenvalues"],
        "variance_explained": pca["variance_explained"],
        "cum_variance_explained": pca["cum_variance_explained"],
    }).to_csv(diag_dir / "pca_summary.csv", index=False)
    pairs.to_csv(diag_dir / "correlation_pairs.csv", index=False)
    print(f"\nWrote diagnostic CSVs to {diag_dir}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagnose", action="store_true",
                    help="Print season universe and exit.")
    ap.add_argument("--component", choices=list(COMPONENT_REGISTRY),
                    help="Compute a single component, persist its CSV, run eye-test.")
    ap.add_argument("--composite", action="store_true",
                    help="Phase 3: assemble composite, run correlation matrix and PCA.")
    ap.add_argument("--validate", action="store_true",
                    help="Phase 4: run predictive validation regressions.")
    ap.add_argument("--include-covid", action="store_true",
                    help="Include 2019-20 and 2020-21 in validation (robustness).")
    ap.add_argument("--charts", action="store_true",
                    help="Phase 6: build the six hero visualizations.")
    args = ap.parse_args()

    if args.diagnose:
        run_diagnose()
        return
    if args.component:
        run_component(args.component)
        return
    if args.composite:
        run_composite()
        return
    if args.validate:
        run_validate(include_covid=args.include_covid)
        return
    if args.charts:
        print("Phase 6: building hero visualizations...")
        paths = charts_mod.build_all_charts()
        print(f"\nBuilt {len(paths)} charts in {config.CHART_DIR}")
        return
    print("Pipeline not yet wired in. Use --diagnose, --component <name>, --composite, --validate, or --charts.")


def _print_reg(name: str, df: pd.DataFrame, focus_rows: list[str]) -> None:
    print(f"\n  [{name}]  n={df.attrs.get('n')}  R2={df.attrs.get('r2', df.attrs.get('pseudo_r2', float('nan'))):.3f}")
    rows = df.loc[[r for r in focus_rows if r in df.index]]
    print(rows.round(4).to_string())


def run_validate(include_covid: bool = False) -> None:
    """Phase 4: three predictive regressions, each three ways."""
    print(f"\nPhase 4: predictive validation.")
    print(f"  COVID exclusion: {'OFF (include 2019-20 and 2020-21)' if include_covid else 'ON (default; exclude 2019-20 and 2020-21)'}")
    print(f"  2025-26 always excluded (in-progress playoffs)")
    print(f"  Bootstrap n={validate_mod.BOOTSTRAP_N} seed={validate_mod.BOOTSTRAP_SEED}")

    # Assemble composite first.
    five, _ = composite_mod.assemble_composite()

    ds = validate_mod.build_validation_dataset(five, include_covid=include_covid)
    pt = ds["playoff_team_seasons"]
    series = ds["series"]

    print(f"\n  Sample sizes:")
    print(f"    team-season outcomes:   {len(ds['team_season_outcomes']):,}")
    print(f"    playoff team-seasons:   {len(pt):,}")
    print(f"    playoff series:         {len(series):,}")
    print(f"    seasons in sample:      {sorted(pt['season_start_year'].unique().tolist())}")

    component_cols = [f"{c}_pct" for c in composite_mod.COMPONENT_MODULES]

    # -------- Regression A: playoff overperformance --------
    print("\n" + "="*72)
    print("Regression A: playoff_wins ~ rs_net_rating + LAFI + season_FE")
    print("="*72)
    a_full = validate_mod.regression_a(pt, "lafi_pct")
    a_sharp = validate_mod.regression_a(pt, "sharp_lafi_pct")
    a_comp = validate_mod.regression_a_components(pt, component_cols)
    _print_reg("Reg A — Full LAFI",  a_full,  ["rs_net_rating", "lafi_pct"])
    _print_reg("Reg A — Sharp LAFI", a_sharp, ["rs_net_rating", "sharp_lafi_pct"])
    _print_reg("Reg A — Components", a_comp,  ["rs_net_rating"] + component_cols)

    # -------- Regression B: ORtg decay --------
    print("\n" + "="*72)
    print("Regression B: ortg_decay ~ LAFI + opp_avg_drtg + season_FE")
    print("="*72)
    b_full = validate_mod.regression_b(pt, "lafi_pct")
    b_sharp = validate_mod.regression_b(pt, "sharp_lafi_pct")
    b_comp = validate_mod.regression_b_components(pt, component_cols)
    _print_reg("Reg B — Full LAFI",  b_full,  ["lafi_pct", "opp_avg_drtg"])
    _print_reg("Reg B — Sharp LAFI", b_sharp, ["sharp_lafi_pct", "opp_avg_drtg"])
    _print_reg("Reg B — Components", b_comp,  component_cols + ["opp_avg_drtg"])

    # -------- Regression C: series upset --------
    print("\n" + "="*72)
    print("Regression C: favorite_won ~ LAFI_diff + nr_diff (logistic)")
    print("="*72)
    c_full = validate_mod.regression_c(series, "lafi_diff_fav_minus_other")
    c_sharp = validate_mod.regression_c(series, "sharp_diff_fav_minus_other")
    _print_reg("Reg C — Full LAFI diff",  c_full,  ["lafi_diff_fav_minus_other", "nr_diff_fav_minus_other"])
    _print_reg("Reg C — Sharp LAFI diff", c_sharp, ["sharp_diff_fav_minus_other", "nr_diff_fav_minus_other"])

    # -------- Robustness checks --------
    print("\n" + "="*72)
    print("Robustness #1: C1-only univariate (test the components-regression signal)")
    print("="*72)
    a_c1 = validate_mod.regression_a_c1_only(pt)
    _print_reg("Reg A — C1-only", a_c1, ["rs_net_rating", "C1_ball_stickiness_pct"])

    print("\n" + "="*72)
    print("Robustness #2: Binary DV (advanced past round 1, logistic)")
    print("="*72)
    a_full_bin = validate_mod.regression_a_binary(pt, "lafi_pct")
    a_sharp_bin = validate_mod.regression_a_binary(pt, "sharp_lafi_pct")
    _print_reg("Reg A binary — Full LAFI",  a_full_bin,  ["rs_net_rating", "lafi_pct"])
    _print_reg("Reg A binary — Sharp LAFI", a_sharp_bin, ["rs_net_rating", "sharp_lafi_pct"])

    # -------- Multiple testing correction --------
    print("\n" + "="*72)
    print("Multiple testing correction (Benjamini-Hochberg across primary LAFI coefficients)")
    print("="*72)
    primary_p = [
        ("A_full",  float(a_full.loc["lafi_pct", "p_value"])),
        ("B_full",  float(b_full.loc["lafi_pct", "p_value"])),
        ("C_full",  float(c_full.loc["lafi_diff_fav_minus_other", "p_value"])),
        ("A_sharp", float(a_sharp.loc["sharp_lafi_pct", "p_value"])),
        ("B_sharp", float(b_sharp.loc["sharp_lafi_pct", "p_value"])),
        ("C_sharp", float(c_sharp.loc["sharp_diff_fav_minus_other", "p_value"])),
    ]
    raw = [p for _, p in primary_p]
    bh = validate_mod.apply_bh_correction(raw)
    for (name, raw_p), adj_p, rej in zip(primary_p, bh["adj"], bh["reject"]):
        print(f"  {name:<10}  raw_p={raw_p:.4f}  bh_p={adj_p:.4f}  reject_at_05={rej}")

    # Persist key tables.
    out = config.TABLE_DIR / "validation"
    out.mkdir(parents=True, exist_ok=True)
    pt.to_csv(out / "validation_dataset_playoff_teams.csv", index=False)
    series.to_csv(out / "validation_dataset_series.csv", index=False)
    a_full.to_csv(out / "regression_a_full.csv")
    a_sharp.to_csv(out / "regression_a_sharp.csv")
    a_comp.to_csv(out / "regression_a_components.csv")
    b_full.to_csv(out / "regression_b_full.csv")
    b_sharp.to_csv(out / "regression_b_sharp.csv")
    b_comp.to_csv(out / "regression_b_components.csv")
    c_full.to_csv(out / "regression_c_full.csv")
    c_sharp.to_csv(out / "regression_c_sharp.csv")
    a_c1.to_csv(out / "regression_a_c1_only.csv")
    a_full_bin.to_csv(out / "regression_a_binary_full.csv")
    a_sharp_bin.to_csv(out / "regression_a_binary_sharp.csv")
    suffix = "_covid_included" if include_covid else ""
    if suffix:
        # write a second copy with suffix for easy comparison
        a_c1.to_csv(out / f"regression_a_c1_only{suffix}.csv")
        a_full.to_csv(out / f"regression_a_full{suffix}.csv")
        a_sharp.to_csv(out / f"regression_a_sharp{suffix}.csv")
    print(f"\nWrote validation outputs to {out}")


if __name__ == "__main__":
    main()
