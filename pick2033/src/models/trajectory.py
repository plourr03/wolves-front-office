"""Model A: franchise trajectory -- hierarchical AR(1) with Student-t
innovations on observed SRS (spec 7.1, amended by the M0 identification
finding: SRS is fitted directly as the AR(1) state; the latent-state +
observation-noise form is unidentified in practice and is earned-complexity
only if backtest gates demand it).

    srs[i, t] ~ StudentT(nu, mu[i] + phi * (srs[i, t-1] - mu[i]), sigma)
    mu[i]     ~ Normal(0, tau)        # franchise long-run mean, partial pooling
    phi ~ Beta, sigma/tau ~ HalfNormal, nu ~ Gamma  (config priors)

Panel handling: transitions are built only within contiguous franchise runs
(expansion entries and the CHA 2003-04 gap contribute no transition across
the break; run-initial seasons are conditioned on, not modeled).

Fit results cache to outputs/posteriors/trajectory_<hash>.parquet keyed by
(data version, model code version, params). The simulation engine loads the
cache; it never refits. Forward simulation starts from the observed SRS of
the final training season (the "filtered state" under the observed-panel
form is the observation itself).

CLI:
  python -m src.models.trajectory fit             # full panel through 2026
  python -m src.models.trajectory fit --through T # rolling-origin training fit
"""

from __future__ import annotations

import argparse
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
MODEL_CODE_VERSION = "trajectory_v2_config_innovation"


def load_params() -> dict:
    return yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())


def load_panel(through: int | None = None) -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute(
        "SELECT franchise_id, season, srs FROM franchise_seasons ORDER BY franchise_id, season"
    ).fetchdf()
    con.close()
    if through is not None:
        df = df[df.season <= through]
    return df


def build_transitions(panel: pd.DataFrame):
    """(prev_srs, curr_srs, franchise_index) for contiguous season pairs."""
    fr_ids = sorted(panel.franchise_id.unique())
    fr_index = {f: i for i, f in enumerate(fr_ids)}
    prev, curr, idx = [], [], []
    for f, g in panel.groupby("franchise_id"):
        g = g.sort_values("season")
        s = g.season.values
        v = g.srs.values
        contiguous = s[1:] == s[:-1] + 1
        prev.extend(v[:-1][contiguous])
        curr.extend(v[1:][contiguous])
        idx.extend([fr_index[f]] * int(contiguous.sum()))
    return (np.array(prev), np.array(curr), np.array(idx, dtype=int), fr_ids)


def model(prev, curr, fr_idx, n_franchises, priors, innovation,
          franchise_means="hierarchical"):
    import jax.numpy as jnp
    import numpyro
    import numpyro.distributions as dist

    phi = numpyro.sample("phi", dist.Beta(*priors["phi_beta"]))
    sigma = numpyro.sample("sigma", dist.HalfNormal(priors["sigma_halfnormal"]))
    if franchise_means == "hierarchical":
        tau = numpyro.sample("tau", dist.HalfNormal(priors["tau_halfnormal"]))
        with numpyro.plate("franchises", n_franchises):
            z_mu = numpyro.sample("z_mu", dist.Normal(0, 1))
        mu = numpyro.deterministic("mu", tau * z_mu)
    elif franchise_means == "pooled":
        # gate-ruling condition 1 (2026-07-01): tau -> 0 variant, fit ONCE,
        # never tuned; the S7 tornado arm runs this posterior through Engine D
        mu0 = numpyro.sample("mu0", dist.Normal(0, 2))
        mu = numpyro.deterministic("mu", jnp.repeat(mu0, n_franchises))
    else:
        raise ValueError(f"unknown franchise_means {franchise_means!r}")
    mean = mu[fr_idx] + phi * (prev - mu[fr_idx])
    if innovation == "student_t":
        nu = numpyro.sample("nu", dist.Gamma(*priors["nu_gamma"]))
        numpyro.sample("obs", dist.StudentT(nu, mean, sigma), obs=curr)
    elif innovation == "mixture":
        # routine noise (sigma) vs structural shock (sigma_shock > sigma),
        # marginalized two-component zero-mean mixture
        w = numpyro.sample("w_routine", dist.Beta(*priors["mix_w_beta"]))
        shock_extra = numpyro.sample(
            "shock_extra", dist.HalfNormal(priors["mix_shock_scale_hn"]))
        sigma_shock = numpyro.deterministic("sigma_shock", sigma + shock_extra)
        mixing = dist.Categorical(probs=jnp.stack([w, 1 - w]))
        scales = jnp.stack([
            jnp.broadcast_to(sigma, mean.shape),
            jnp.broadcast_to(sigma_shock, mean.shape)], axis=-1)
        comp = dist.Normal(mean[..., None], scales)
        numpyro.sample("obs", dist.MixtureSameFamily(mixing, comp), obs=curr)
    else:
        raise ValueError(f"unknown innovation {innovation!r}")


def data_version_hash(panel: pd.DataFrame) -> str:
    h = hashlib.sha256(pd.util.hash_pandas_object(panel, index=False).values.tobytes())
    return h.hexdigest()[:12]


def cache_key(panel: pd.DataFrame, model_a_cfg: dict, seed: int,
              through: int | None) -> str:
    blob = json.dumps({
        "data": data_version_hash(panel),
        "code": MODEL_CODE_VERSION,
        "params": model_a_cfg,
        "seed": seed,
        "through": through,
    }, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def fit(through: int | None = None, quiet: bool = False,
        variant_overrides: dict | None = None,
        panel_override: pd.DataFrame | None = None):
    """Fit Model A; returns (posterior DataFrame, franchise ids, cache path).
    Cache-first: an existing parquet for the same key is returned untouched.
    panel_override: alternate panel (the tornado CHA-lineage arm); the cache
    key hashes panel data, so an override keys its own cache entry."""
    import jax
    import numpyro
    from numpyro.infer import MCMC, NUTS

    params = load_params()
    model_a_cfg = dict(params["model_a"])
    if variant_overrides:
        model_a_cfg.update(variant_overrides)
    panel = panel_override if panel_override is not None else load_panel(through)
    key = cache_key(panel, model_a_cfg, params["seed"], through)
    POSTERIORS.mkdir(parents=True, exist_ok=True)
    cache_path = POSTERIORS / f"trajectory_{key}.parquet"
    meta_path = POSTERIORS / f"trajectory_{key}.meta.json"
    prev, curr, fr_idx, fr_ids = build_transitions(panel)

    if cache_path.exists():
        return pd.read_parquet(cache_path), fr_ids, cache_path

    numpyro.set_host_device_count(model_a_cfg["num_chains"])
    mcmc = MCMC(
        NUTS(model, target_accept_prob=model_a_cfg["target_accept"]),
        num_warmup=model_a_cfg["num_warmup"],
        num_samples=model_a_cfg["num_samples"],
        num_chains=model_a_cfg["num_chains"],
        progress_bar=False,
    )
    innovation = model_a_cfg.get("innovation", "student_t")
    franchise_means = model_a_cfg.get("franchise_means", "hierarchical")
    mcmc.run(jax.random.PRNGKey(params["seed"]), prev=prev, curr=curr,
             fr_idx=fr_idx, n_franchises=len(fr_ids),
             priors=model_a_cfg["priors"], innovation=innovation,
             franchise_means=franchise_means)

    import arviz as az
    idata = az.from_numpyro(mcmc)
    var_names = ["phi", "sigma"]
    var_names += ["tau", "z_mu"] if franchise_means == "hierarchical" else ["mu0"]
    var_names += ["nu"] if innovation == "student_t" else ["w_routine", "shock_extra"]
    summ = az.summary(idata, var_names=var_names, round_to="none")
    n_div = int(np.asarray(mcmc.get_extra_fields()["diverging"]).sum())
    health = {
        "worst_r_hat": float(summ.r_hat.max()),
        "min_ess_bulk": float(summ.ess_bulk.min()),
        "divergences": n_div,
        "n_transitions": len(curr),
        "through": through,
        "franchises": fr_ids,
    }
    if not quiet:
        print(f"[through={through}] r_hat={health['worst_r_hat']:.4f} "
              f"ess={health['min_ess_bulk']:.0f} div={n_div} n={len(curr)}")

    samples = mcmc.get_samples()
    post = pd.DataFrame({
        "phi": np.asarray(samples["phi"]),
        "sigma": np.asarray(samples["sigma"]),
    })
    if innovation == "student_t":
        post["nu"] = np.asarray(samples["nu"])
    else:
        post["w_routine"] = np.asarray(samples["w_routine"])
        post["sigma_shock"] = np.asarray(samples["sigma"]) + np.asarray(samples["shock_extra"])
    if franchise_means == "hierarchical":
        post["tau"] = np.asarray(samples["tau"])
        mu = np.asarray(samples["tau"])[:, None] * np.asarray(samples["z_mu"])
    else:
        mu = np.tile(np.asarray(samples["mu0"])[:, None], (1, len(fr_ids)))
    for i, f in enumerate(fr_ids):
        post[f"mu_{f}"] = mu[:, i]
    post.to_parquet(cache_path, index=False)
    meta_path.write_text(json.dumps(health, indent=1))
    return post, fr_ids, cache_path


def forecast_paths(post: pd.DataFrame, fr_ids: list[str], start_srs: dict[str, float],
                   horizons: int, n_paths: int, seed: int) -> np.ndarray:
    """Simulate SRS paths under Model A dynamics.
    Returns array (n_paths, horizons, n_franchises); each path pairs with one
    posterior draw (resampled with replacement)."""
    rng = np.random.default_rng(seed)
    draw_idx = rng.integers(0, len(post), n_paths)
    phi = post.phi.values[draw_idx]
    sigma = post.sigma.values[draw_idx]
    present = [f for f in fr_ids if f in start_srs]
    mu = np.stack([post[f"mu_{f}"].values[draw_idx] for f in present], axis=1)
    theta = np.tile(np.array([start_srs[f] for f in present]), (n_paths, 1))
    out = np.empty((n_paths, horizons, len(present)))
    is_mixture = "w_routine" in post.columns
    if is_mixture:
        w = post.w_routine.values[draw_idx]
        sigma_shock = post.sigma_shock.values[draw_idx]
    else:
        nu = post.nu.values[draw_idx]
    for h in range(horizons):
        if is_mixture:
            shock = rng.random(theta.shape) > w[:, None]
            scale = np.where(shock, sigma_shock[:, None], sigma[:, None])
            innov = rng.normal(0, 1, size=theta.shape) * scale
        else:
            innov = rng.standard_t(nu[:, None], size=theta.shape) * sigma[:, None]
        theta = mu + phi[:, None] * (theta - mu) + innov
        out[:, h, :] = theta
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fit"])
    ap.add_argument("--through", type=int, default=None)
    args = ap.parse_args()
    post, fr_ids, path = fit(args.through)
    print(f"posterior cached -> {path} ({len(post)} draws, {len(fr_ids)} franchises)")


if __name__ == "__main__":
    main()
