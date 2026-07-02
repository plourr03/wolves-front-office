"""Model C: aging curves -- the delta method, hierarchical by archetype
(spec 7.3). Year-over-year BPM change as a smooth function of age:

    delta_bpm[p, t] = g_archetype(age[p, t]) + gamma[p] + eps
    g = natural-cubic-spline basis, coefficients = global + archetype offset
    gamma[p] ~ Normal(0, s_gamma)  (non-centered player random effect)
    eps ~ StudentT(nu_c, 0, sigma_c)  (fat tails absorb injury-year swings)

Survivor bias mitigation (the known killer): any player-season with 500+
minutes followed by NO qualifying season gets an imputed decline-to-
replacement delta (replacement = -2.0 BPM, the B-Ref convention), flagged
`imputed`. The model fits WITH imputation (authoritative past age 30 per
spec) and the validation report shows curves with vs without.

Gates 8.3: held-out delta RMSE beats the no-aging baseline (delta = 0) and
the league-mean-delta baseline; survivor-bias audit plotted.

Data: combined-row BPM from player_impact_seasons, both seasons >= 500 mp
(or the imputed rows). Archetype from listed position: PG/SG -> guard,
SF (and G-F/F-G combos) -> wing, PF/C -> big.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "data" / "warehouse.duckdb"
POSTERIORS = PROJECT_ROOT / "outputs" / "posteriors"
OUT_VAL = PROJECT_ROOT / "outputs" / "validation"
MODEL_CODE_VERSION = "aging_v1.1_imputed_scale"
REPLACEMENT_BPM = -2.0
MP_FLOOR = 500
KNOTS = np.array([21.0, 24.0, 27.0, 30.0, 33.0, 36.0])


def load_params() -> dict:
    return yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())


def archetype_of(pos: str) -> str:
    p = (pos or "").split("-")[0].strip().upper()
    if p in ("PG", "SG", "G"):
        return "guard"
    if p in ("SF", "GF", "F"):
        return "wing"
    return "big"  # PF, C, FC


def natural_cubic_basis(age: np.ndarray, knots: np.ndarray = KNOTS) -> np.ndarray:
    """Natural cubic spline basis (truncated power, natural constraints);
    returns (n, K-1) columns incl. linear term."""
    K = len(knots)

    def d(k, x):
        num = np.maximum(x - knots[k], 0) ** 3 - np.maximum(x - knots[K - 1], 0) ** 3
        return num / (knots[K - 1] - knots[k])

    cols = [age - knots.mean()]
    for k in range(K - 2):
        cols.append(d(k, age) - d(K - 2, age))
    return np.column_stack(cols)


def build_deltas() -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    ps = con.execute("""
        SELECT player_id, season, pos, age, mp, bpm FROM (
            SELECT *, row_number() OVER (PARTITION BY player_id, season
                     ORDER BY is_combined DESC) AS rn
            FROM player_impact_seasons WHERE is_combined OR stint_order IS NULL)
        WHERE rn = 1 AND bpm IS NOT NULL AND age IS NOT NULL
        ORDER BY player_id, season
    """).fetchdf()
    con.close()
    data_end = int(ps.season.max())
    rows = []
    for pid, g in ps.groupby("player_id"):
        g = g.sort_values("season").reset_index(drop=True)
        qual = g[g.mp >= MP_FLOOR]
        qual_seasons = set(qual.season)
        for _, r in qual.iterrows():
            nxt = g[g.season == r.season + 1]
            if len(nxt) and nxt.iloc[0].mp >= MP_FLOOR:
                n = nxt.iloc[0]
                rows.append({
                    "player_id": pid, "season": int(n.season),
                    "age": float(n.age), "pos": r.pos,
                    "delta_bpm": float(n.bpm - r.bpm), "imputed": False,
                })
            elif r.season + 1 <= data_end and (r.season + 1) not in qual_seasons:
                # dropout: no qualifying next season -> decline to replacement
                rows.append({
                    "player_id": pid, "season": int(r.season + 1),
                    "age": float(r.age + 1), "pos": r.pos,
                    "delta_bpm": float(REPLACEMENT_BPM - r.bpm), "imputed": True,
                })
    df = pd.DataFrame(rows)
    df["archetype"] = df.pos.map(archetype_of)
    return df


def model(X, arch_idx, player_idx, n_arch, n_players, imputed, y):
    import jax.numpy as jnp
    import numpyro
    import numpyro.distributions as dist

    n_basis = X.shape[1]
    beta_g = numpyro.sample("beta_global", dist.Normal(0, 2).expand([n_basis]).to_event(1))
    with numpyro.plate("arch", n_arch):
        z_beta = numpyro.sample("z_beta_arch", dist.Normal(0, 1).expand([n_basis]).to_event(1))
    s_arch = numpyro.sample("s_arch", dist.HalfNormal(0.5))
    beta = beta_g + s_arch * z_beta                      # (n_arch, n_basis)
    intercept = numpyro.sample("intercept", dist.Normal(0, 2).expand([n_arch]).to_event(1))
    s_gamma = numpyro.sample("s_gamma", dist.HalfNormal(1.0))
    with numpyro.plate("players", n_players):
        z_gamma = numpyro.sample("z_gamma", dist.Normal(0, 1))
    sigma = numpyro.sample("sigma", dist.HalfNormal(3.0))
    nu = numpyro.sample("nu", dist.Gamma(2, 0.1))
    mean = intercept[arch_idx] + (X * beta[arch_idx]).sum(-1) + s_gamma * z_gamma[player_idx]
    if imputed is not None and imputed.any():
        # imputed decline-to-replacement rows come from a different
        # measurement process (systematically large negative deltas); a
        # dedicated residual scale keeps them from destabilizing nu/sigma
        # (with-imputation fit hit R-hat 1.60 under a single scale)
        sigma_imp = numpyro.sample("sigma_imp", dist.HalfNormal(5.0))
        scale = jnp.where(jnp.asarray(imputed), sigma_imp, sigma)
    else:
        scale = sigma
    numpyro.sample("obs", dist.StudentT(nu, mean, scale), obs=y)


def fit(df: pd.DataFrame, tag: str, seed: int, mcmc_cfg: dict):
    import jax
    import numpyro
    from numpyro.infer import MCMC, NUTS

    key_blob = json.dumps({
        "data": hashlib.sha256(pd.util.hash_pandas_object(df, index=False).values.tobytes()).hexdigest()[:12],
        "code": MODEL_CODE_VERSION, "tag": tag, "seed": seed, "cfg": mcmc_cfg}, sort_keys=True)
    key = hashlib.sha256(key_blob.encode()).hexdigest()[:16]
    POSTERIORS.mkdir(parents=True, exist_ok=True)
    cache = POSTERIORS / f"aging_{tag}_{key}.parquet"
    meta = POSTERIORS / f"aging_{tag}_{key}.meta.json"

    arches = sorted(df.archetype.unique())
    players = sorted(df.player_id.unique())
    a_idx = {a: i for i, a in enumerate(arches)}
    p_idx = {p: i for i, p in enumerate(players)}
    X = natural_cubic_basis(df.age.values)
    arch_idx = df.archetype.map(a_idx).values
    player_idx = df.player_id.map(p_idx).values

    if cache.exists():
        return pd.read_parquet(cache), arches, json.loads(meta.read_text())

    numpyro.set_host_device_count(4)
    mcmc = MCMC(NUTS(model, target_accept_prob=0.95),
                num_warmup=mcmc_cfg["num_warmup"], num_samples=mcmc_cfg["num_samples"],
                num_chains=4, progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), X=X, arch_idx=arch_idx, player_idx=player_idx,
             n_arch=len(arches), n_players=len(players),
             imputed=df.imputed.values, y=df.delta_bpm.values)

    import arviz as az
    idata = az.from_numpyro(mcmc)
    summ = az.summary(idata, var_names=["beta_global", "s_arch", "intercept",
                                        "s_gamma", "sigma", "nu"], round_to="none")
    health = {"worst_r_hat": float(summ.r_hat.max()),
              "min_ess_bulk": float(summ.ess_bulk.min()),
              "n_rows": len(df), "n_players": len(players), "tag": tag}
    s = mcmc.get_samples()
    beta = np.asarray(s["beta_global"])[:, None, :] + \
        np.asarray(s["s_arch"])[:, None, None] * np.asarray(s["z_beta_arch"])
    post = {"sigma": np.asarray(s["sigma"]), "nu": np.asarray(s["nu"]),
            "s_gamma": np.asarray(s["s_gamma"])}
    flat = pd.DataFrame(post)
    for i, a in enumerate(arches):
        flat[f"intercept_{a}"] = np.asarray(s["intercept"])[:, i]
        for b in range(beta.shape[2]):
            flat[f"beta_{a}_{b}"] = beta[:, i, b]
    flat.to_parquet(cache, index=False)
    meta.write_text(json.dumps(health, indent=1))
    return flat, arches, health


def curve_from_posterior(flat: pd.DataFrame, arch: str, ages: np.ndarray) -> np.ndarray:
    """Posterior draws of g_arch(age): (n_draws, len(ages))."""
    X = natural_cubic_basis(ages)
    betas = np.column_stack([flat[f"beta_{arch}_{b}"].values for b in range(X.shape[1])])
    return flat[f"intercept_{arch}"].values[:, None] + betas @ X.T


def expected_delta(flat: pd.DataFrame, arch: str, age: float) -> float:
    return float(curve_from_posterior(flat, arch, np.array([age])).mean())


def main():
    params = load_params()
    seed = params["seed"] + 3
    mcmc_cfg = {"num_warmup": 1500, "num_samples": 1000}
    df = build_deltas()
    print(f"delta rows: {len(df)} ({df.imputed.sum()} imputed), "
          f"players {df.player_id.nunique()}, archetypes {df.archetype.value_counts().to_dict()}")

    # held-out gate on OBSERVED deltas only (imputed rows are a modeling
    # device, not ground truth)
    rng = np.random.default_rng(seed)
    obs = df[~df.imputed].reset_index(drop=True)
    test_mask = rng.random(len(obs)) < 0.20
    train = pd.concat([obs[~test_mask], df[df.imputed]], ignore_index=True)
    test = obs[test_mask]

    flat, arches, health = fit(train, "train", seed, mcmc_cfg)
    print(f"train fit: r_hat={health['worst_r_hat']:.4f} ess={health['min_ess_bulk']:.0f}")

    Xt = natural_cubic_basis(test.age.values)
    pred = np.zeros(len(test))
    for a in arches:
        m = (test.archetype == a).values
        if m.any():
            betas = np.column_stack([flat[f"beta_{a}_{b}"].values for b in range(Xt.shape[1])])
            pred[m] = (flat[f"intercept_{a}"].values[:, None] + betas @ Xt[m].T).mean(0)
    rmse_model = float(np.sqrt(((test.delta_bpm.values - pred) ** 2).mean()))
    rmse_zero = float(np.sqrt((test.delta_bpm.values ** 2).mean()))
    mean_delta = float(train[~train.imputed].delta_bpm.mean())
    rmse_mean = float(np.sqrt(((test.delta_bpm.values - mean_delta) ** 2).mean()))
    gate_rmse = rmse_model < rmse_zero and rmse_model < rmse_mean

    # survivor-bias audit: full fits with and without imputation
    flat_with, _, h_with = fit(df, "with_imputation", seed, mcmc_cfg)
    flat_wo, _, h_wo = fit(df[~df.imputed].reset_index(drop=True), "no_imputation", seed, mcmc_cfg)
    ages = np.arange(19, 40.5, 0.5)
    audit = {}
    for a in arches:
        cw = curve_from_posterior(flat_with, a, ages).mean(0)
        co = curve_from_posterior(flat_wo, a, ages).mean(0)
        audit[a] = {"ages": ages.tolist(), "with_imp": cw.tolist(), "no_imp": co.tolist(),
                    "max_div_past_30": float(np.abs(cw - co)[ages >= 30].max())}

    OUT_VAL.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Model C aging curves (gates 8.3)",
        f"- delta rows {len(df)} ({int(df.imputed.sum())} imputed dropout rows), "
        f"players {df.player_id.nunique()}",
        f"- train MCMC: r_hat {health['worst_r_hat']:.4f}, ess {health['min_ess_bulk']:.0f}; "
        f"with-imp r_hat {h_with['worst_r_hat']:.4f}; no-imp r_hat {h_wo['worst_r_hat']:.4f}",
        f"- held-out RMSE: model {rmse_model:.3f} vs no-aging {rmse_zero:.3f} "
        f"vs league-mean {rmse_mean:.3f} -> **{'PASS' if gate_rmse else 'FAIL'}**",
        "- survivor-bias audit (max |with - without| past age 30, BPM):",
    ]
    for a in arches:
        lines.append(f"    - {a}: {audit[a]['max_div_past_30']:.2f} "
                     f"(imputed version authoritative past 30 per spec)")
    (OUT_VAL / "model_c_aging.md").write_text("\n".join(lines), encoding="utf-8")
    (OUT_VAL / "model_c_curves.json").write_text(json.dumps(audit), encoding="utf-8")
    print("\n".join(lines))
    sys.exit(0 if gate_rmse else 1)


if __name__ == "__main__":
    main()
