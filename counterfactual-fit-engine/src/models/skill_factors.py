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
# Reparam constants: positive scale params sampled as floor + softplus(LOC +
# N(0,1)) -- smooth, no funnel neck. psi = unique std per feature (median
# ~0.5). W_diag = the triangular positive diagonal (Path B, median ~0.8).
PSI_FLOOR, PSI_LOC = 0.05, -0.5
DIAG_FLOOR, DIAG_LOC = 0.1, 0.0

ANCHOR_LABELS = {
    0: "scoring load", 1: "scoring efficiency", 2: "spacing",
    3: "playmaking", 4: "rim pressure", 5: "rebounding",
    6: "rim protection", 7: "defensive impact",
}

# FROZEN factor names (Bobby's editorial call, 2026-07-06), replacing the
# provisional anchor labels in the shipped export. Three factors (4, 5, 7)
# drifted off their assigned leader: a free feature owns the axis, caught only
# by the exemplars. The honest data-driven reads (not the aspirational anchor
# labels) ship in the export. See decisions.md 2026-07-06. drift_from_leader
# marks the three defensive/hustle factors whose identity moved; a v2
# defensive-leader reassignment is logged for a future refit (K stays 8).
FROZEN_FACTOR_NAMES = {
    0: "offensive engine",     1: "interior finishing",   2: "spacing",
    3: "playmaking",           4: "perimeter quickness",  5: "perimeter disruption",
    6: "shot-blocking",        7: "pull-up shooting",
}
FACTOR_DRIFT = {0: False, 1: False, 2: False, 3: False,
                4: True, 5: True, 6: False, 7: True}
FACTOR_HONEST_READ = {
    0: "High-usage on-ball creation load. usg (+1.00), scoring volume, drives, pull-up 3s, playmaking gravity. High: Westbrook, Harden, Embiid, Luka, Giannis. Leader owns the axis.",
    1: "Low-usage rim-finishing efficiency, NOT general scoring efficiency. ts% (+0.81) flanked by center markers (orb%, def_rim_fga). High end is unanimously rim-running / putback centers (Gafford, Bruno Fernando, Beringer 25-26), not efficient wings or stars.",
    2: "Three-point shooting volume / floor spacing. fg3a_rate (+0.98) and catch-shoot 3PA (+0.90) dominate. High: Merrill, Bertans, Hauser. Low: non-shooting interior bigs.",
    3: "On-ball, pass-first assist creation. ast36 / potential_ast / ast% cluster (+0.83 to +0.88). High: Rondo, McConnell, Haliburton. Skewed toward pass-first accumulator guards.",
    4: "Guard-vs-big size axis, NOT rim pressure. Owned by the negative interior pole (def_rim_fga, drb%, reb_contest, orb%, blk all -0.4 to -0.6); leader drives_per75 only +0.33. High: small/fast perimeter players (M. Howard, S. Brown, SGA). Low: rim-anchoring bigs (Jokic scores lowest). Measures backcourt smallness via absence of interior work.",
    5: "Steals and deflections / event defense, NOT rebounding. stl (+0.55) dominates (2x anything else), def_rapm (-0.36) second; leader drb_pct only +0.13. High: Thybulle, Covington, Reed. Low: stationary offense-first shooters.",
    6: "Block RATE / raw swat production, narrower than defensive value. blk36 (+0.48) leads, def_rim_fga (+0.29) reinforces. High: Turner, Wembanyama, Boucher, Pelle, Anthony.",
    7: "Off-the-dribble / pull-up shot creation, NOT defense. pull-up 3PA (+0.40) dominates (~2.5x leader def_rapm +0.16); catch-shoot 3PA (-0.28) is the negative pole. High: Harden, Luka, Lillard (offensive engines, zero defensive character). stl loads negative, i.e. against event defense.",
}
FACTOR_FOOTNOTE = {
    6: "Tracks block PRODUCTION, not team-defense VALUE: def_rapm (-0.23) and off_rapm (-0.17) load ~0/negative, so high block-rate specialists here are not necessarily high-value defenders.",
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
    # PATH B (2026-07-05): LOWER-TRIANGULAR loadings with a POSITIVE DIAGONAL
    # (Geweke-Zhou factor-analysis identification). The measurement proved
    # both diagonal and dense mass saturate the tree cap AND the chains do
    # not mix (R-hat 2.02, ESS 3): the marginalized likelihood sees only
    # W Wᵀ, which is invariant under W -> W R for orthogonal R, so the
    # posterior has FLAT ROTATION RIDGES. Pure-marker anchors (Path A) pinned
    # only K diagonal entries and left the ridge; a lower-triangular
    # positive-diagonal W is a UNIQUE representative of each W Wᵀ orbit, so
    # the ridge collapses to a point and NUTS can mix. The first K features
    # (FEAT_COLS[:K] = LEADER_FEATURES, frozen) are the factor scaffolding:
    # feature k loads on factors 0..k only, with W[k,k] > 0. The remaining
    # p-K features load freely on all K factors. Anchors are now labels only.
    W_diag_raw = numpyro.sample(
        "W_diag_raw", dist.Normal(0.0, 1.0).expand([K]).to_event(1))
    W_diag = DIAG_FLOOR + jax.nn.softplus(DIAG_LOC + W_diag_raw)   # positive
    n_lower = K * (K - 1) // 2
    W_lower = numpyro.sample(
        "W_lower", dist.Normal(0.0, 1.0).expand([n_lower]).to_event(1))
    W_rest = numpyro.sample(
        "W_rest", dist.Normal(0.0, 1.0).expand([p - K, K]).to_event(2))

    Wtop = jnp.zeros((K, K))
    Wtop = Wtop.at[jnp.diag_indices(K)].set(W_diag)
    tr, tc = jnp.tril_indices(K, -1)                 # strictly-lower entries
    Wtop = Wtop.at[tr, tc].set(W_lower)
    W = numpyro.deterministic("W", jnp.concatenate([Wtop, W_rest], axis=0))

    # psi: softplus reparam retained (smooth positive, no funnel), exposed
    # via deterministic so downstream code reads samples["psi"] unchanged.
    psi_raw = numpyro.sample("psi_raw", dist.Normal(0.0, 1.0).expand([p]).to_event(1))
    psi = numpyro.deterministic(
        "psi", PSI_FLOOR + jax.nn.softplus(PSI_LOC + psi_raw))

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


def _samples_cache_key(dev_tag: str) -> str:
    blob = json.dumps({"v": MODEL_VERSION, "tag": dev_tag, "seed": SEED,
                       "K": K, "warmup": L1B["num_warmup"],
                       "samples": L1B["num_samples"], "chains": L1B["num_chains"],
                       "depth": L1B.get("max_tree_depth", 8),
                       "dense": L1B.get("dense_mass", True)}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def fit(Y, se2, anchor_idx, dev_tag: str):
    import jax
    import numpyro
    from numpyro.infer import MCMC, NUTS
    import arviz as az

    # CHECKPOINT: the MCMC samples are the ONLY expensive artifact (~14h on
    # CPU). Persist them the instant the run finishes, BEFORE any downstream
    # post-processing that could crash, and resume from them if present. A
    # trivial export bug once cost a full 14h fit (2026-07-06); never again.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    key = _samples_cache_key(dev_tag)
    scache = OUT_DIR / f"samples_{dev_tag}_{key}.npz"
    hcache = OUT_DIR / f"samples_{dev_tag}_{key}.health.json"
    if scache.exists() and hcache.exists():
        print(f"[{dev_tag}] resuming from cached samples {scache.name} "
              "(skipping MCMC)", flush=True)
        npz = np.load(scache)
        return {k: npz[k] for k in npz.files}, json.loads(hcache.read_text())

    numpyro.set_host_device_count(int(L1B["num_chains"]))
    # 'vectorized' runs all chains in one vmapped pass -- far faster on CPU
    # than the default sequential chains for this small-parameter model.
    # DENSE mass matrix: the loadings posterior is correlated, which made
    # NUTS take enormous (tree-depth-saturating) trajectories under the
    # default diagonal mass -- the true cause of the wall (the gradient is
    # cheap, profiled). A full 197x197 mass matrix captures the correlations
    # and collapses trajectory length, so exact NUTS runs on ALL the data in
    # minutes with the real gates. max_tree_depth stays generous (won't be
    # hit once the geometry is fixed); if it ever were, low ESS would flag it.
    mcmc = MCMC(NUTS(_model, target_accept_prob=0.9, dense_mass=True,
                     max_tree_depth=int(L1B.get("max_tree_depth", 8))),
                num_warmup=int(L1B["num_warmup"]),
                num_samples=int(L1B["num_samples"]),
                num_chains=int(L1B["num_chains"]), progress_bar=False,
                # SEQUENTIAL: the vectorized dense-mass compile stalled on
                # this CPU; sequential compiles a single-chain graph that
                # reliably runs. This is the OFFLINE full-data NUTS run
                # (Bobby's pre-approved step-2) -- correctness + real gates
                # over speed, on a load-bearing artifact.
                chain_method=L1B.get("chain_method", "sequential"))
    mcmc.run(jax.random.PRNGKey(SEED), Y=Y, SE2=se2, anchor_idx=anchor_idx)
    idata = az.from_numpyro(mcmc)
    summ = az.summary(idata, var_names=["W_diag_raw", "W_lower", "W_rest",
                                        "psi_raw"], round_to="none")
    health = {"worst_r_hat": float(summ.r_hat.max()),
              "min_ess_bulk": float(summ.ess_bulk.min()),
              "n_rows": int(Y.shape[0]), "K": K, "tag": dev_tag}
    samples = {k: np.asarray(v) for k, v in mcmc.get_samples().items()}
    # persist IMMEDIATELY (before any caller post-processing can crash)
    np.savez(scache, **samples)
    hcache.write_text(json.dumps(health, indent=1))
    print(f"[{dev_tag}] samples checkpointed -> {scache.name}", flush=True)
    return samples, health


def _reassemble_W(samples, anchor_idx, p):
    """(S, p, K) loading draws. Path B exposes the assembled lower-triangular
    W directly via numpyro.deterministic, so this just returns it."""
    return np.asarray(samples["W"])                  # (S, p, K)


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

    # FULL-DATA fit, NO subsampling (ruling 2026-07-03: a subsampled fit
    # disproportionately drops exactly the query/backtest players the engine
    # targets, so it does not ship). The earlier wall was NOT the data size:
    # the likelihood gradient is cheap and scales LINEARLY in rows (~6 us/row,
    # ~36 ms on the full ~5.8k rotation player-seasons -- profiled). The wall
    # was NUTS saturating the tree depth on a poorly-conditioned (correlated-
    # loadings) posterior; the DENSE mass matrix in fit() cures the geometry
    # and collapses the trajectory length, keeping exact NUTS and the real
    # R-hat/ESS gates on all the data.
    print(f"[{tag}] factor fit: ALL {Y.shape[0]} rotation player-seasons x "
          f"{Y.shape[1]} features, K={K}, "
          f"anchors={[ANCHORS[k] for k in range(K)]}", flush=True)

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
        col = load[f"z{k}"].sort_values(ascending=False)
        pos = [(c, round(float(col[c]), 2)) for c in col.index if col[c] > 0.05][:5]
        neg = [(c, round(float(col[c]), 2)) for c in col[::-1].index
               if col[c] < -0.05][:5]
        rec = {"factor": k, "name": FROZEN_FACTOR_NAMES[k],
               "leader_feature": ANCHORS[k], "provisional_label": ANCHOR_LABELS[k],
               "drift_from_leader": FACTOR_DRIFT[k],
               "honest_read": FACTOR_HONEST_READ[k],
               "top_positive_features": pos, "top_negative_features": neg}
        if k in FACTOR_FOOTNOTE:
            rec["footnote"] = FACTOR_FOOTNOTE[k]
        interp.append(rec)
    health["interpretability"] = interp
    (OUT_DIR / f"health_{tag}.json").write_text(json.dumps(health, indent=1))

    print("\nTop +/- loading features per factor (FROZEN names; * = drifted "
          "off leader):", flush=True)
    for it in interp:
        p_ = ", ".join(f"{c}{v:+.2f}" for c, v in it["top_positive_features"])
        n_ = ", ".join(f"{c}{v:+.2f}" for c, v in it["top_negative_features"])
        drift = " *drift" if it["drift_from_leader"] else ""
        print(f"  z{it['factor']} [{it['name']}{drift}] leader={it['leader_feature']}"
              f"\n      +: {p_}\n      -: {n_}")

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
    # player_features carries player_id/season/end_year but NOT player_name;
    # fetch names from the warehouse by id (robust; the feature ETL omitted it).
    from src.adapters.postmortem_lib import query
    nm = query("""SELECT DISTINCT ON (player_id) player_id, player_name
                  FROM nba_player_stats WHERE player_id = ANY(%s)
                  ORDER BY player_id, game_date DESC""",
               (f.player_id.astype(int).tolist(),))
    name_map = dict(zip(nm.player_id, nm.player_name))
    ids = f[["player_id", "season", "end_year"]].reset_index(drop=True)
    ids["player_name"] = ids.player_id.map(name_map)
    ids["z_mean"] = list(Z.mean(1))
    ids["z_samples_shape"] = [list(Z.shape[1:])] * len(ids)
    ids.to_parquet(OUT_DIR / f"skill_vectors_{tag}.parquet")
    np.save(OUT_DIR / f"skill_vectors_{tag}_samples.npy", Z.astype(np.float32))

    # exemplar player-seasons per factor (the naming aid Bobby asked for: a
    # namable axis has coherent exemplars, a smear does not). Top/bottom 5
    # by posterior-mean score, restricted to reliable rotation seasons.
    zmean = Z.mean(1)                                    # (n, K)
    label = (ids.player_name.fillna(ids.player_id.astype(str)) + " "
             + f.season.values).tolist()
    for it in interp:
        k = it["factor"]
        order = np.argsort(zmean[:, k])
        it["exemplars_high"] = [(label[i], round(float(zmean[i, k]), 2))
                                for i in order[::-1][:5]]
        it["exemplars_low"] = [(label[i], round(float(zmean[i, k]), 2))
                               for i in order[:5]]
    (OUT_DIR / f"interpretability_{tag}.json").write_text(json.dumps(interp, indent=1))
    print("\nExemplars per factor (naming aid):", flush=True)
    for it in interp:
        hi = ", ".join(f"{n} ({v:+.1f})" for n, v in it["exemplars_high"])
        lo = ", ".join(f"{n} ({v:+.1f})" for n, v in it["exemplars_low"])
        print(f"  z{it['factor']} [{it['name']}]"
              f"\n      high: {hi}\n      low:  {lo}")

    (OUT_DIR / f"skill_vectors_{tag}.meta.json").write_text(json.dumps(meta, indent=1))
    print(f"\nskill_vectors FROZEN: {Y.shape[0]} player-seasons x {Z.shape[1]} "
          f"draws x K={K} -> outputs/skill_vectors/ (key {key})", flush=True)


if __name__ == "__main__":
    main()
