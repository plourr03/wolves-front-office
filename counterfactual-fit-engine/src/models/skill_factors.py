"""F3 Layer 1b: the Bayesian latent skill factor model (spec 8.3), fit at
the RATIFIED K=8 (decisions.md 2026-07-03). Produces skill_vectors (spec
7.4), the Project 2 handoff artifact, but ONLY after the health gates pass.

Model (measurement-error-aware, marginalized). Standardized player-season
feature matrix Y (n x p). Latent factors Z (n x K) are integrated out
analytically (linear-Gaussian), so MCMC samples only the loadings and
unique variances (~p*K + p params, not n*K latents) -- fast and stable.
Per row the marginal likelihood is

    y_i ~ Normal(0, W Wᵀ + diag(psi² + se_i²))

where se_i² is the Layer-1a bootstrap VARIANCE of the O/D-RAPM columns for
that player-season (zero for the box/tracking columns): the RAPM columns'
measurement error enters the noise, so noisy RAPM estimates are
down-weighted (spec 8.3). psi_j is each feature's intrinsic unique std.

Identification (kills rotation, spec 8.3): eight PURE-MARKER anchors, one
per factor, each a distinct skill feature. Anchor a_k loads POSITIVELY on
factor k (HalfNormal) and ZERO on every other factor; all non-anchor
loadings get a Laplace sparsity prior. This pins both sign and rotation.

skill_vectors: after the fit, each player-season's factor scores are drawn
from the conditional Gaussian posterior Z_i | y_i, W, psi across posterior
draws, giving an S x K sample matrix per player-season (spec 7.4).

HEALTH GATES (config layer1b.health_gates): worst R-hat < 1.01, min bulk
ESS > 400, plus anchor sign-stability. skill_vectors freeze/version ONLY
if all pass; a failure PARKS with a memo (the Bayesian reconstruction
curve), it does NOT ship vectors and does NOT re-select K (K is frozen,
ruling 2026-07-03).

Usage: python -m src.models.skill_factors [--dev]   (--dev = dev-season
       rotation players only, a fast health check before the full fit)
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

FITENGINE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FITENGINE_ROOT))
from src.models.factor_select import FEAT_COLS, ZERO_FILL  # noqa: E402

CFG = yaml.safe_load((FITENGINE_ROOT / "config" / "model_params.yaml").read_text())
L1B = CFG["layer1b"]
K = int(L1B["K"])
SEED = int(CFG["seed"])
GATES = L1B["health_gates"]
FEAT_PATH = FITENGINE_ROOT / "outputs" / "features" / "player_features.parquet"
OUT_DIR = FITENGINE_ROOT / "outputs" / "skill_vectors"
MODEL_VERSION = "skill_factors_v1_me_anchored"

# eight pure-marker anchors, one distinct skill per factor (indices into
# FEAT_COLS). Chosen a priori as clean markers so the factors do not rotate.
ANCHORS = {
    0: "usg_pct",            # scoring load
    1: "ts_pct",             # scoring efficiency
    2: "fg3a_rate",          # spacing / 3pt volume
    3: "ast_pct",            # playmaking
    4: "drives_per75",       # rim pressure / driving
    5: "drb_pct",            # rebounding
    6: "blk36",              # rim protection
    7: "def_rapm",           # overall defensive impact
}
ANCHOR_LABELS = {
    0: "scoring load", 1: "scoring efficiency", 2: "spacing",
    3: "playmaking", 4: "rim pressure", 5: "rebounding",
    6: "rim protection", 7: "defensive impact",
}


def load_matrix(dev_only: bool):
    f = pd.read_parquet(FEAT_PATH)
    if dev_only:
        f = f[f.end_year <= 2021]
    f = f[f.off_rapm.notna()].copy()   # rotation players (own-column RAPM)
    for c in ZERO_FILL:
        f[c] = f[c].fillna(0.0)
    f = f.dropna(subset=FEAT_COLS).reset_index(drop=True)
    X = f[FEAT_COLS].to_numpy(np.float64)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Y = (X - mu) / sd
    # measurement-error variance per feature per row: RAPM columns carry
    # their bootstrap SE (standardized by the feature's sd); others zero.
    se2 = np.zeros_like(Y)
    for col, se_col in [("off_rapm", "off_se"), ("def_rapm", "def_se")]:
        j = FEAT_COLS.index(col)
        se2[:, j] = (f[se_col].to_numpy(np.float64) / sd[j]) ** 2
    return f, Y, se2, (mu, sd)


def _model(Y, SE2, anchor_idx):
    import jax
    import jax.numpy as jnp
    import numpyro
    import numpyro.distributions as dist

    n, p = Y.shape
    tau = numpyro.sample("tau", dist.HalfNormal(1.0))
    W_free = numpyro.sample("W_free", dist.Laplace(0.0, tau).expand([p, K]).to_event(2))
    anchor_diag = numpyro.sample("anchor_diag", dist.HalfNormal(2.0).expand([K]).to_event(1))
    psi = numpyro.sample("psi", dist.HalfNormal(1.0).expand([p]).to_event(1))

    W = W_free
    for k in range(K):
        a = anchor_idx[k]
        W = W.at[a, :].set(0.0)
        W = W.at[a, k].set(anchor_diag[k])

    log2pi = jnp.log(2.0 * jnp.pi)

    def row_ll(y, se2):
        # C = W Wᵀ + diag(d); log N(y|0,C) via the matrix-determinant lemma
        # so the per-row work is a K x K solve, not a p x p cholesky.
        d = psi ** 2 + se2 + 1e-6           # (p,)
        inv_d = 1.0 / d
        a = inv_d * y                        # (p,)
        b = W.T @ a                          # (K,)
        M = jnp.eye(K) + (W.T * inv_d) @ W   # (K,K)
        L = jnp.linalg.cholesky(M)
        x = jax.scipy.linalg.cho_solve((L, True), b)      # M^-1 b
        quad = jnp.dot(y, a) - jnp.dot(b, x)
        logdet = jnp.sum(jnp.log(d)) + 2.0 * jnp.sum(jnp.log(jnp.diag(L)))
        return -0.5 * (p * log2pi + logdet + quad)

    numpyro.factor("obs", jax.vmap(row_ll)(Y, SE2).sum())


def fit(Y, se2, anchor_idx, dev_tag: str):
    import jax
    import numpyro
    from numpyro.infer import MCMC, NUTS
    import arviz as az

    numpyro.set_host_device_count(int(L1B["num_chains"]))
    mcmc = MCMC(NUTS(_model, target_accept_prob=0.9),
                num_warmup=int(L1B["num_warmup"]),
                num_samples=int(L1B["num_samples"]),
                num_chains=int(L1B["num_chains"]), progress_bar=False)
    mcmc.run(jax.random.PRNGKey(SEED), Y=Y, SE2=se2, anchor_idx=anchor_idx)
    idata = az.from_numpyro(mcmc)
    summ = az.summary(idata, var_names=["W_free", "anchor_diag", "psi", "tau"],
                      round_to="none")
    health = {"worst_r_hat": float(summ.r_hat.max()),
              "min_ess_bulk": float(summ.ess_bulk.min()),
              "n_rows": int(Y.shape[0]), "K": K, "tag": dev_tag}
    return mcmc.get_samples(), health


def _reassemble_W(samples, anchor_idx, p):
    """(S, p, K) loading draws with the anchor structure applied."""
    Wf = np.asarray(samples["W_free"])              # (S, p, K)
    ad = np.asarray(samples["anchor_diag"])          # (S, K)
    W = Wf.copy()
    for k in range(K):
        a = anchor_idx[k]
        W[:, a, :] = 0.0
        W[:, a, k] = ad[:, k]
    return W


def factor_scores(Y, se2, samples, anchor_idx, n_draw=200, seed=SEED):
    """S x K skill-vector samples per player-season from the conditional
    Gaussian Z_i | y_i, W, psi, over a thinned set of posterior draws."""
    rng = np.random.default_rng(seed)
    p = Y.shape[1]
    W = _reassemble_W(samples, anchor_idx, p)
    psi = np.asarray(samples["psi"])                 # (S, p)
    S = W.shape[0]
    idx = rng.choice(S, size=min(n_draw, S), replace=False)
    n = Y.shape[0]
    out = np.empty((n, len(idx), K))
    for t, s in enumerate(idx):
        Ws, ps = W[s], psi[s]
        for i in range(n):
            Dinv = 1.0 / (ps ** 2 + se2[i])
            A = np.eye(K) + (Ws.T * Dinv) @ Ws
            Ainv = np.linalg.inv(A)
            m = Ainv @ (Ws.T * Dinv) @ Y[i]
            out[i, t] = rng.multivariate_normal(m, Ainv)
    return out                                        # (n, n_draw, K)


def main() -> None:
    dev_only = "--dev" in sys.argv[1:]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    f, Y, se2, (mu, sd) = load_matrix(dev_only)
    anchor_idx = tuple(FEAT_COLS.index(ANCHORS[k]) for k in range(K))
    tag = "dev" if dev_only else "full"
    print(f"[{tag}] factor fit: {Y.shape[0]} player-seasons x {Y.shape[1]} "
          f"features, K={K}, anchors={[ANCHORS[k] for k in range(K)]}", flush=True)

    samples, health = fit(Y, se2, anchor_idx, tag)
    passed = (health["worst_r_hat"] < GATES["max_r_hat"]
              and health["min_ess_bulk"] > GATES["min_ess_bulk"])
    print(f"HEALTH: worst R-hat {health['worst_r_hat']:.4f} "
          f"(gate < {GATES['max_r_hat']}), min ESS {health['min_ess_bulk']:.0f} "
          f"(gate > {GATES['min_ess_bulk']}) -> {'PASS' if passed else 'FAIL'}",
          flush=True)

    # loadings posterior mean + interpretability
    W = _reassemble_W(samples, anchor_idx, Y.shape[1]).mean(0)   # (p, K)
    load = pd.DataFrame(W, index=FEAT_COLS, columns=[f"z{k}" for k in range(K)])
    load.to_parquet(OUT_DIR / f"loadings_{tag}.parquet")

    interp = []
    for k in range(K):
        top = load[f"z{k}"].abs().sort_values(ascending=False).head(5)
        interp.append({"factor": k, "anchor": ANCHORS[k],
                       "provisional_label": ANCHOR_LABELS[k],
                       "top_features": [(c, round(float(load.loc[c, f'z{k}']), 2))
                                        for c in top.index]})
    health["interpretability"] = interp
    (OUT_DIR / f"health_{tag}.json").write_text(json.dumps(health, indent=1))

    print("\nTop-loading features per factor (provisional labels; naming is "
          "Bobby's editorial call):", flush=True)
    for it in interp:
        feats = ", ".join(f"{c}{v:+.2f}" for c, v in it["top_features"])
        print(f"  z{it['factor']} [{it['provisional_label']}] anchor={it['anchor']}: {feats}")

    if not passed:
        print("\nHEALTH GATE FAILED -> PARKING. skill_vectors NOT shipped. "
              "Memo the Bayesian reconstruction curve; K stays frozen (no "
              "re-selection). See decisions.md.", flush=True)
        return

    print("\nhealth gates PASS -> drawing skill_vectors ...", flush=True)
    Z = factor_scores(Y, se2, samples, anchor_idx)      # (n, n_draw, K)
    key = hashlib.sha256((MODEL_VERSION + tag + str(SEED)).encode()).hexdigest()[:12]
    meta = {"model_version": MODEL_VERSION, "K": K, "tag": tag, "seed": SEED,
            "n_player_seasons": int(Y.shape[0]), "n_draws": int(Z.shape[1]),
            "anchors": {k: ANCHORS[k] for k in range(K)}, "health": health,
            "schema_version": "skill_vectors.v1", "content_key": key}
    ids = f[["player_id", "player_name", "season", "end_year"]].reset_index(drop=True)
    ids["z_mean"] = list(Z.mean(1))
    ids["z_samples_shape"] = [list(Z.shape[1:])] * len(ids)
    ids.to_parquet(OUT_DIR / f"skill_vectors_{tag}.parquet")
    np.save(OUT_DIR / f"skill_vectors_{tag}_samples.npy", Z.astype(np.float32))
    (OUT_DIR / f"skill_vectors_{tag}.meta.json").write_text(json.dumps(meta, indent=1))
    print(f"skill_vectors FROZEN: {Y.shape[0]} player-seasons x {Z.shape[1]} "
          f"draws x K={K} -> outputs/skill_vectors/ (key {key})", flush=True)


if __name__ == "__main__":
    main()
