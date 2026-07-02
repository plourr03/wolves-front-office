"""Model E1: draft slot -> value curves with uncertainty (spec 7.6).

Monotonicity is a HARD constraint via construction: the mean curve is a
reversed cumulative sum of non-negative increments,
    m(slot) = base + sum_{k >= slot} delta_k,   delta_k = s_d * z_k,
    z_k ~ HalfNormal(1)  (non-centered: the centered form funnels at
    s_d -> 0 and collapsed the VORP curve flat, r_hat 1.04),
so m is non-increasing in slot by parameterization, not by hope.

Observation model: Normal(m[slot], sigma). The estimand is the conditional
MEAN (expected surplus value) -- a symmetric heavy-tailed likelihood targets
the median, and the median 4yr VORP is ~0 for most slots, which mispriced
the whole curve on the first fit. The value distribution's right skew is
preserved for REALIZED draws via empirical residual bootstrap within slot
bands (1-5 / 6-14 / 15-30 / 31-60), not via the likelihood (v2 option:
skewed observation model).

Currencies: value_4yr (VORP over draft_year+1..+4, primary) and value_alt
(Win Shares, robustness). Training: 1990-2019 drafts, slots 1-60.

Seconds flat value (spec 7.7): mean posterior value over slots 31-45,
exported alongside.
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
POSTERIORS = PROJECT_ROOT / "outputs" / "posteriors"
OUT_VAL = PROJECT_ROOT / "outputs" / "validation"
MODEL_CODE_VERSION = "slot_value_v1.1_noncentered_normal"
N_SLOTS = 60


def load_data() -> pd.DataFrame:
    con = duckdb.connect(str(PROJECT_ROOT / "data" / "warehouse.duckdb"), read_only=True)
    df = con.execute("SELECT slot, value_4yr, value_alt FROM draft_outcomes "
                     "WHERE slot BETWEEN 1 AND 60").fetchdf()
    con.close()
    return df


def model(slot_idx, y):
    import jax.numpy as jnp
    import numpyro
    import numpyro.distributions as dist

    base = numpyro.sample("base", dist.Normal(0, 2))
    s_d = numpyro.sample("s_d", dist.HalfNormal(1.0))
    with numpyro.plate("slots", N_SLOTS):
        z = numpyro.sample("z_delta", dist.HalfNormal(1.0))
    delta = s_d * z
    # m[k] = base + sum_{j >= k} delta_j  -> non-increasing by construction
    m = base + jnp.cumsum(delta[::-1])[::-1]
    numpyro.deterministic("m", m)
    sigma = numpyro.sample("sigma", dist.HalfNormal(5.0))
    numpyro.sample("obs", dist.Normal(m[slot_idx], sigma), obs=y)


def fit(values: np.ndarray, slots: np.ndarray, tag: str, seed: int):
    import jax
    import numpyro
    from numpyro.infer import MCMC, NUTS

    blob = json.dumps({"code": MODEL_CODE_VERSION, "tag": tag, "seed": seed,
                       "data": hashlib.sha256(values.tobytes() + slots.tobytes()).hexdigest()[:12]},
                      sort_keys=True)
    key = hashlib.sha256(blob.encode()).hexdigest()[:16]
    cache = POSTERIORS / f"slot_value_{tag}_{key}.parquet"
    if cache.exists():
        return pd.read_parquet(cache), {"cached": True}

    numpyro.set_host_device_count(4)
    mcmc = MCMC(NUTS(model, target_accept_prob=0.9), num_warmup=1000,
                num_samples=1000, num_chains=4, progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), slot_idx=slots - 1, y=values)
    import arviz as az
    summ = az.summary(az.from_numpyro(mcmc), var_names=["base", "s_d", "sigma", "z_delta"],
                      round_to="none")
    health = {"worst_r_hat": float(summ.r_hat.max()),
              "min_ess_bulk": float(summ.ess_bulk.min())}
    s = mcmc.get_samples()
    delta = np.asarray(s["s_d"])[:, None] * np.asarray(s["z_delta"])
    m = np.asarray(s["base"])[:, None] + np.cumsum(delta[:, ::-1], axis=1)[:, ::-1]
    post = pd.DataFrame({"sigma": np.asarray(s["sigma"])})
    for k in range(N_SLOTS):
        post[f"m_{k + 1}"] = m[:, k]
    post.to_parquet(cache, index=False)
    return post, health


BANDS = [(1, 5), (6, 14), (15, 30), (31, 60)]


def band_residuals(df: pd.DataFrame, post: pd.DataFrame, col: str) -> dict:
    """Empirical residuals (value - posterior-mean curve) pooled by slot band,
    preserving the right skew for realized-value draws."""
    means = np.array([post[f"m_{k}"].mean() for k in range(1, N_SLOTS + 1)])
    resid = df[col].values - means[df.slot.values - 1]
    return {b: resid[(df.slot.values >= b[0]) & (df.slot.values <= b[1])]
            for b in BANDS}


def curve_draws(post: pd.DataFrame, slots: np.ndarray, rng: np.random.Generator,
                residuals: dict | None = None) -> np.ndarray:
    """Value draws for an array of slots. Curve-only (parameter uncertainty)
    when residuals is None; REALIZED-value draws (curve draw + empirical
    band-bootstrapped residual, skew preserved) when residuals is provided."""
    di = rng.integers(0, len(post), len(slots))
    vals = np.array([post[f"m_{int(s)}"].values[d] for s, d in zip(slots, di)])
    if residuals is not None:
        for b, r in residuals.items():
            mask = (slots >= b[0]) & (slots <= b[1])
            if mask.any():
                vals[mask] += rng.choice(r, size=int(mask.sum()), replace=True)
    return vals


def main():
    params = yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())
    seed = params["seed"] + 6
    df = load_data()
    results = {}
    for tag, col in [("vorp", "value_4yr"), ("ws", "value_alt")]:
        post, health = fit(df[col].values.astype(float), df.slot.values.astype(int),
                           tag, seed)
        means = np.array([post[f"m_{k}"].mean() for k in range(1, N_SLOTS + 1)])
        assert (np.diff(means) <= 1e-9).all(), "monotonicity violated (impossible by construction)"
        results[tag] = {"health": health,
                        "curve_mean": means.round(3).tolist(),
                        "seconds_flat_31_45": float(means[30:45].mean())}
        print(f"{tag}: r_hat {health.get('worst_r_hat', float('nan')):.4f} | "
              f"slot1 {means[0]:.2f} slot5 {means[4]:.2f} slot14 {means[13]:.2f} "
              f"slot30 {means[29]:.2f} slot45 {means[44]:.2f} | "
              f"seconds flat {results[tag]['seconds_flat_31_45']:.3f}")
    v, w = np.array(results["vorp"]["curve_mean"]), np.array(results["ws"]["curve_mean"])
    results["vorp_ws_rank_corr"] = float(np.corrcoef(v, w)[0, 1])
    OUT_VAL.mkdir(parents=True, exist_ok=True)
    (OUT_VAL / "model_e1_slot_value.json").write_text(json.dumps(results, indent=1))
    print(f"vorp/ws curve correlation: {results['vorp_ws_rank_corr']:.4f}")


if __name__ == "__main__":
    main()
