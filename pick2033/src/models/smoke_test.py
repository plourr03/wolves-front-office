"""M0 gate: verify the NumPyro/JAX CPU stack on this machine by fitting a
miniature Model A -- hierarchical AR(1) with Student-t innovations on an
OBSERVED panel -- and demanding clean diagnostics (R-hat < 1.01) plus
parameter recovery.

DESIGN NOTE (M0 finding, feeds M1): the spec's latent-state variant
(theta latent, srs = theta + Normal(0, sigma_obs)) is unidentified in
practice: free (nu, sigma, sigma_obs) trade off along a ridge and 4-chain
NUTS lands in different modes (R-hat ~2.8 observed on synthetic data, with
nu escaping to enormous values in the near-normal mode). SRS is a full-season
aggregate with negligible measurement noise, so Model A v1 fits SRS directly
as the AR(1) state; innovations absorb any residual observation noise. The
latent-state form is the earned-complexity variant, only if backtest gates
demand it and only with sigma_obs fixed or tightly prior-constrained.
"""

import sys

import jax
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS

numpyro.set_host_device_count(4)

N_UNITS, N_T = 30, 46          # the real panel's shape
TRUE = {"phi": 0.75, "sigma": 1.5, "tau": 2.0, "nu": 5.0}


def simulate(seed=0):
    rng = np.random.default_rng(seed)
    mu = rng.normal(0, TRUE["tau"], N_UNITS)
    y = np.zeros((N_UNITS, N_T))
    y[:, 0] = mu + rng.standard_t(TRUE["nu"], N_UNITS) * TRUE["sigma"]
    for t in range(1, N_T):
        innov = rng.standard_t(TRUE["nu"], N_UNITS) * TRUE["sigma"]
        y[:, t] = mu + TRUE["phi"] * (y[:, t - 1] - mu) + innov
    return y


def model(y):
    n_units, n_t = y.shape
    phi = numpyro.sample("phi", dist.Beta(20, 5))
    sigma = numpyro.sample("sigma", dist.HalfNormal(3.0))
    tau = numpyro.sample("tau", dist.HalfNormal(3.0))
    nu = numpyro.sample("nu", dist.Gamma(2, 0.1))
    with numpyro.plate("units", n_units):
        mu = numpyro.sample("mu", dist.Normal(0, tau))
    resid_mean = mu[:, None] + phi * (y[:, :-1] - mu[:, None])
    numpyro.sample("obs", dist.StudentT(nu, resid_mean, sigma), obs=y[:, 1:])


def main():
    y = simulate()
    mcmc = MCMC(
        NUTS(model, target_accept_prob=0.9),
        num_warmup=1000,
        num_samples=1000,
        num_chains=4,
        progress_bar=False,
    )
    mcmc.run(jax.random.PRNGKey(20330701), y=y)
    import arviz as az

    idata = az.from_numpyro(mcmc)
    summ = az.summary(idata, var_names=["phi", "sigma", "tau", "nu"])
    print(summ[["mean", "r_hat", "ess_bulk"]])
    worst_rhat = float(summ["r_hat"].max())
    worst_ess = float(summ["ess_bulk"].min())
    phi_mean = float(summ.loc["phi", "mean"])
    ok = worst_rhat < 1.01 and worst_ess > 400 and abs(phi_mean - TRUE["phi"]) < 0.1
    print(f"\nworst r_hat={worst_rhat:.4f} worst ess_bulk={worst_ess:.0f} "
          f"phi={phi_mean:.3f} (true {TRUE['phi']})")
    print("SMOKE-TEST", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
