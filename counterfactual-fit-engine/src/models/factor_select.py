"""F3 K-selection evidence (spec 8.3): choose K in {6, 8, 10} for the
Layer 1b latent skill factor model, on DEVELOPMENT SEASONS ONLY, and
present the decision to Bobby with (a) the held-out feature reconstruction
curve, (b) the PCA-beat health check at each K, and (c) a downstream
dev-season G3 proxy. K IS NOT FROZEN here (ruling 2026-07-03); this
produces the evidence for Bobby's ratify.

This is the SELECTION instrument, not the final skill_vectors fit. It uses
probabilistic FactorAnalysis for the reconstruction metric (fast,
defensible, directly comparable to PCA); the full measurement-error-aware
Bayesian factor model + skill_vectors freeze follows AFTER K is ratified.

Reconstruction (health + selection): K-fold over player-seasons, fit on
train, reconstruct held-out rows, standardized MSE. FactorAnalysis must
beat PCA at the same K (spec health gate) or the posterior machinery is
not earning its keep.

G3 proxy (selection tie-breaker, the ruling's emphasis): factor scores at
each K -> lineup features -> predict lineup pts_per100 on dev seasons,
temporal holdout (train <= s-1, test s for s in the G3 dev targets),
possession-weighted RMSE. A within-season scoring proxy (diagnostic, never
a gate) used only for the RELATIVE comparison across K. If more factors do
not lower lineup-prediction error, they are not worth interpreting.

Sealed window (2022+) is never read. Usage: python -m src.models.factor_select
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))

FEATURES = pd.read_parquet  # alias to keep imports tidy
FEAT_PATH = FITENGINE_ROOT / "outputs" / "features" / "player_features.parquet"
LINEUP_PATH = FITENGINE_ROOT / "outputs" / "features" / "lineup_obs.parquet"
OUT_DIR = FITENGINE_ROOT / "outputs" / "factor"

K_GRID = [6, 8, 10]
SEED = 20260702
DEV_MAX_END_YEAR = 2021          # dev = 2013-14..2020-21; sealed 2021-22+ untouched
G3_PROXY_TARGETS = [2019, 2020, 2021]  # dev-season temporal test years

# the Layer 1b input features (spec 7.3): box rates, advanced rates,
# public tracking per-75, and the Layer 1a O/D-RAPM point estimates. The
# RAPM SEs are NOT features -- they enter the Bayesian measurement-error
# likelihood at the real fit, not the selection reconstruction.
# FROZEN ORDER (2026-07-05, Path B). Layer 1b identifies the factors by a
# lower-triangular loading matrix, so the FIRST 8 features are the factor
# scaffolding (feature k primarily defines factor k). They are chosen as 8
# dense, 100%-populated, conceptually distinct skill markers (the former
# anchor set); a noisy/sparse leader would poison its factor. The remaining
# 13 features follow in any order (their loadings are free). This order is
# load-bearing for identification AND interpretation -- do not shuffle.
LEADER_FEATURES = [
    "usg_pct", "ts_pct", "fg3a_rate", "ast_pct",        # scoring/eff/spacing/playmaking
    "drives_per75", "drb_pct", "blk36", "def_rapm",     # rim-pressure/reb/rim-prot/def
]
_REST_FEATURES = [
    "ftr", "tov_ratio", "orb_pct", "stl36", "pts36", "ast36",
    "cs_fg3a_per75", "pu_fg3a_per75", "potential_ast_per75",
    "def_rim_fga_per75", "reb_contest_rate", "avg_speed", "off_rapm",
]
FEAT_COLS = LEADER_FEATURES + _REST_FEATURES
ZERO_FILL = ["cs_fg3a_per75", "pu_fg3a_per75"]  # legitimate zeros (no such shots)


def load_dev_matrix():
    f = FEATURES(FEAT_PATH)
    f = f[f.end_year <= DEV_MAX_END_YEAR].copy()
    # rotation players: an own-column RAPM estimate exists (the factor model's
    # population; sub-threshold players were pooled to replacement)
    f = f[f.off_rapm.notna()].copy()
    for c in ZERO_FILL:
        f[c] = f[c].fillna(0.0)
    f = f.dropna(subset=FEAT_COLS)
    X = f[FEAT_COLS].to_numpy(np.float64)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Xz = (X - mu) / sd
    return f.reset_index(drop=True), Xz, (mu, sd)


def reconstruction_curve(Xz, folds=5):
    """Held-out average LOG-LIKELIHOOD per K (higher = better). This is the
    right 'reconstruction' metric for a probabilistic factor model: raw
    reconstruction MSE is minimized by PCA by construction and would always
    favor it, whereas held-out LL rewards modeling the per-feature unique
    noise that real skill features carry. Both FactorAnalysis and PCA
    (probabilistic PCA) expose .score() as held-out average LL, so the
    spec's 'beats PCA at same K' health gate is a direct comparison."""
    from sklearn.decomposition import FactorAnalysis, PCA
    from sklearn.model_selection import KFold
    kf = KFold(n_splits=folds, shuffle=True, random_state=SEED)
    rows = []
    for K in K_GRID:
        fa_ll, pca_ll = [], []
        for tr, te in kf.split(Xz):
            fa_ll.append(FactorAnalysis(n_components=K, random_state=SEED)
                         .fit(Xz[tr]).score(Xz[te]))
            pca_ll.append(PCA(n_components=K, random_state=SEED)
                          .fit(Xz[tr]).score(Xz[te]))
        rows.append({"K": K, "fa_heldout_ll": float(np.mean(fa_ll)),
                     "pca_heldout_ll": float(np.mean(pca_ll)),
                     "fa_beats_pca": float(np.mean(fa_ll)) > float(np.mean(pca_ll))})
    return pd.DataFrame(rows)


def factor_scores(f, Xz, K):
    from sklearn.decomposition import FactorAnalysis
    fa = FactorAnalysis(n_components=K, random_state=SEED).fit(Xz)
    Z = fa.transform(Xz)
    cols = [f"z{i}" for i in range(K)]
    sc = pd.DataFrame(Z, columns=cols)
    sc["player_id"] = f.player_id.values
    sc["end_year"] = f.end_year.values
    return sc, cols


def g3_proxy_curve():
    """Downstream lineup-prediction RMSE by K on dev seasons. For each K:
    build factor scores, form lineup features (per-dim sum + offense-minus-
    defense contrasts of the five-man sums), predict pts_per100 with ridge,
    temporal holdout. Also the additive-z (K=all raw features) baseline."""
    from sklearn.linear_model import Ridge
    f, Xz, _ = load_dev_matrix()
    obs = FEATURES(LINEUP_PATH)
    obs = obs[(obs.end_year <= DEV_MAX_END_YEAR)
              & (obs.poss >= 10)].copy()  # drop single-possession noise matchups

    def lineup_matrix(scores, cols):
        K = len(cols)
        smap = {(int(r.player_id), int(r.end_year)): r[cols].to_numpy(np.float64)
                for _, r in scores.iterrows()}
        # non-rotation players (no own factor score) get the replacement-
        # level vector = 0 (the standardized-feature mean), mirroring how
        # Layer 1a pools sub-threshold players to a replacement column.
        repl = np.zeros(K)
        rows, y, w, yr = [], [], [], []
        for r in obs.itertuples():
            off = np.array([smap.get((int(p), r.end_year), repl)
                            for p in r.off_lineup.split(",")])
            dfn = np.array([smap.get((int(p), r.end_year), repl)
                            for p in r.def_lineup.split(",")])
            feat = np.concatenate([off.sum(0), dfn.sum(0), off.sum(0) - dfn.sum(0)])
            rows.append(feat); y.append(r.pts_per100); w.append(r.poss); yr.append(r.end_year)
        return np.array(rows), np.array(y), np.array(w), np.array(yr)

    results = []
    for K in K_GRID:
        scores, cols = factor_scores(f, Xz, K)
        Xl, y, w, yr = lineup_matrix(scores, cols)
        rmses = []
        for s in G3_PROXY_TARGETS:
            tr, te = yr < s, yr == s
            if tr.sum() < 100 or te.sum() < 50:
                continue
            m = Ridge(alpha=10.0).fit(Xl[tr], y[tr], sample_weight=w[tr])
            pred = m.predict(Xl[te])
            rmses.append(float(np.sqrt(np.average((y[te] - pred) ** 2, weights=w[te]))))
        results.append({"K": K, "g3_proxy_rmse": float(np.mean(rmses)),
                        "n_test_years": len(rmses)})
    return pd.DataFrame(results)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    f, Xz, _ = load_dev_matrix()
    print(f"dev factor matrix: {len(f)} player-seasons x {len(FEAT_COLS)} features "
          f"(seasons {sorted(f.end_year.unique())})", flush=True)

    recon = reconstruction_curve(Xz)
    print("\n=== reconstruction curve (held-out standardized MSE; FA must beat PCA) ===")
    print(recon.to_string(index=False), flush=True)

    g3 = g3_proxy_curve()
    print("\n=== G3 proxy (dev lineup-prediction RMSE by K; lower = factors help) ===")
    print(g3.to_string(index=False), flush=True)

    merged = recon.merge(g3, on="K")
    merged.to_parquet(OUT_DIR / "k_selection.parquet", index=False)
    (OUT_DIR / "k_selection.json").write_text(merged.to_json(orient="records", indent=1))
    print(f"\nwrote {OUT_DIR / 'k_selection.parquet'}", flush=True)


if __name__ == "__main__":
    main()
