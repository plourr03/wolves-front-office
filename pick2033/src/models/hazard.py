"""Model B: star retention hazard -- discrete-time hierarchical Bayesian
logit on spell-season rows (spec 7.2). PROVISIONAL overnight fit
(2026-07-01): trained on the PROVISIONAL spells freeze; borderline spells
kept (sensitivity variant excludes them); July-6 exit updates not applied.

    P(departure in season t | spell active) = logistic(
        b0 + b_age*age_z + b_age2*age_z^2 + b_yrs*yrs_z + b_win*win2_z
        + b_deep*deep + b_mkt*(market_tier-2) + b_super*supermax
        + b_an*all_nba_z + u[era] )

KNOWN OMISSION (loud): contract_years_remaining has 0% historical coverage
at M0 and is OMITTED from the provisional fit. For Edwards specifically the
2029 walk year is likely the highest-leverage covariate; provisional curves
therefore lack contract leverage entirely. The final M2 fit requires the
best-effort contract backfill + Bobby review before Stage 1 publishes.

Competing risk: retirement censors (cause-specific departure hazard);
spec-sanctioned given 25 retire events.

Gates 8.2 (holdout: 20% of SPELLS, seed from config):
  C-index >= 0.63 on held-out player-seasons (binary AUC of predicted hazard)
  calibration slope in [0.8, 1.2] on held-out rows
  Cox (lifelines CoxTimeVaryingFitter) sign agreement on every covariate
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
STAGED = PROJECT_ROOT / "data" / "staged"
POSTERIORS = PROJECT_ROOT / "outputs" / "posteriors"
OUT_VAL = PROJECT_ROOT / "outputs" / "validation"
OUT_JSON = PROJECT_ROOT / "outputs" / "json"
MODEL_CODE_VERSION = "hazard_v1_provisional_nocontract"

COVARS = ["age_z", "age_z2", "yrs_z", "win2_z", "deep", "mkt_c", "supermax", "an_z"]

# =====================================================================
# M2 FINAL SPEC — pre-declared 2026-07-02 (Ruling A), blind to backfilled
# data. The M2 refit uses EXACTLY this and re-gates all of 8.2 on the same
# sealed holdout, once. Pass, or the red cell stands with its bootstrap CI.
# No third fit.
M2_FINAL_SPEC = {
    "covariates": COVARS + ["contract_z", "contract_known"],
    #  contract_z: standardized contract_years_remaining, 0 where unknown
    #  contract_known: missingness indicator (spec 6.2 -- the model learns
    #  a missingness effect rather than silently imputing)
    "coef_prior_sd": 0.5,     # Normal(0, 0.5) on standardized covariates
    "code_version": "hazard_m2_final_contract_shrunk",
}
# =====================================================================


def load_params() -> dict:
    return yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())


def era_of(season: int) -> int:
    return min(3, max(0, (season - 1990) // 10))


def prep(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    d = df.copy()
    d = d.dropna(subset=["age", "years_with_franchise", "team_win_pct_2yr", "market_tier"])
    stats = {
        "age_mean": float(d.age.mean()), "age_sd": float(d.age.std()),
        "yrs_mean": float(d.years_with_franchise.mean()), "yrs_sd": float(d.years_with_franchise.std()),
        "win_mean": float(d.team_win_pct_2yr.mean()), "win_sd": float(d.team_win_pct_2yr.std()),
        "an_mean": float(d.all_nba_count_career.mean()), "an_sd": float(d.all_nba_count_career.std()),
    }
    d["age_z"] = (d.age - stats["age_mean"]) / stats["age_sd"]
    d["age_z2"] = d.age_z ** 2
    d["yrs_z"] = (d.years_with_franchise - stats["yrs_mean"]) / stats["yrs_sd"]
    d["win2_z"] = (d.team_win_pct_2yr - stats["win_mean"]) / stats["win_sd"]
    d["deep"] = d.deep_run_recent.astype(float)
    d["mkt_c"] = d.market_tier.astype(float) - 2.0
    d["supermax"] = d.supermax_eligible.astype(float)
    d["an_z"] = (d.all_nba_count_career - stats["an_mean"]) / stats["an_sd"]
    d["era"] = d.season.map(era_of)
    d["event"] = d.event_departure.astype(int)
    return d, stats


def model(X, era_idx, y):
    import numpyro
    import numpyro.distributions as dist

    n_cov = X.shape[1]
    b0 = numpyro.sample("b0", dist.Normal(-1.5, 1.5))
    b = numpyro.sample("b", dist.Normal(0, 1).expand([n_cov]).to_event(1))
    s_era = numpyro.sample("s_era", dist.HalfNormal(0.5))
    with numpyro.plate("eras", 4):
        z_era = numpyro.sample("z_era", dist.Normal(0, 1))
    logits = b0 + X @ b + s_era * z_era[era_idx]
    numpyro.sample("obs", dist.Bernoulli(logits=logits), obs=y)


def fit(d: pd.DataFrame, tag: str, seed: int):
    import jax
    import numpyro
    from numpyro.infer import MCMC, NUTS

    key_blob = json.dumps({
        "data": hashlib.sha256(pd.util.hash_pandas_object(
            d[COVARS + ["era", "event"]], index=False).values.tobytes()).hexdigest()[:12],
        "code": MODEL_CODE_VERSION, "tag": tag, "seed": seed}, sort_keys=True)
    key = hashlib.sha256(key_blob.encode()).hexdigest()[:16]
    POSTERIORS.mkdir(parents=True, exist_ok=True)
    cache = POSTERIORS / f"hazard_{tag}_{key}.parquet"
    if cache.exists():
        return pd.read_parquet(cache), {"cached": True}

    numpyro.set_host_device_count(4)
    mcmc = MCMC(NUTS(model, target_accept_prob=0.9), num_warmup=1000,
                num_samples=1000, num_chains=4, progress_bar=False)
    mcmc.run(jax.random.PRNGKey(seed), X=d[COVARS].values,
             era_idx=d.era.values, y=d.event.values)
    import arviz as az
    summ = az.summary(az.from_numpyro(mcmc), var_names=["b0", "b", "s_era", "z_era"],
                      round_to="none")
    health = {"worst_r_hat": float(summ.r_hat.max()),
              "min_ess_bulk": float(summ.ess_bulk.min())}
    s = mcmc.get_samples()
    post = pd.DataFrame({"b0": np.asarray(s["b0"]), "s_era": np.asarray(s["s_era"])})
    b = np.asarray(s["b"])
    for i, c in enumerate(COVARS):
        post[f"b_{c}"] = b[:, i]
    z = np.asarray(s["z_era"])
    for e in range(4):
        post[f"u_era_{e}"] = post.s_era * z[:, e]
    post.to_parquet(cache, index=False)
    return post, health


def predict_hazard(post: pd.DataFrame, X: np.ndarray, era: int, draws=False):
    b = post[[f"b_{c}" for c in COVARS]].values
    logits = post.b0.values[:, None] + b @ X.T + post[f"u_era_{era}"].values[:, None]
    p = 1 / (1 + np.exp(-logits))
    return p if draws else p.mean(0)


def auc(p: np.ndarray, y: np.ndarray) -> float:
    order = np.argsort(p)
    ranks = np.empty(len(p)); ranks[order] = np.arange(1, len(p) + 1)
    n1, n0 = y.sum(), (1 - y).sum()
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def calibration_slope(p: np.ndarray, y: np.ndarray) -> float:
    from scipy.optimize import minimize
    x = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))

    def nll(theta):
        z = np.clip(theta[0] + theta[1] * x, -30, 30)
        return float(np.sum(np.logaddexp(0, z) - y * z))

    res = minimize(nll, x0=np.array([0.0, 1.0]), method="Nelder-Mead")
    return float(res.x[1])


def cox_sign_check(d: pd.DataFrame) -> dict:
    from lifelines import CoxTimeVaryingFitter
    ctv = CoxTimeVaryingFitter(penalizer=0.1)
    cd = d.copy()
    cd["start"] = cd.years_with_franchise - 1
    cd["stop"] = cd.years_with_franchise
    # lifelines requires strictly increasing start<stop and unique intervals
    cd = cd[cd.start < cd.stop]
    cox_covs = ["age_z", "yrs_z", "win2_z", "deep", "mkt_c", "supermax", "an_z"]
    ctv.fit(cd[["spell_id", "start", "stop", "event"] + cox_covs],
            id_col="spell_id", start_col="start", stop_col="stop", event_col="event")
    return ctv.params_.to_dict()


def edwards_path(stats: dict, scenario_win: float = 0.60) -> pd.DataFrame:
    rows = []
    for i, season in enumerate(range(2027, 2034)):
        age = 25 + i
        yrs = 7 + i
        supermax = 1.0 if yrs >= 7 and season >= 2018 else 0.0
        rows.append({
            "season": season,
            "age_z": (age - stats["age_mean"]) / stats["age_sd"],
            "yrs_z": (yrs - stats["yrs_mean"]) / stats["yrs_sd"],
            "win2_z": (scenario_win - stats["win_mean"]) / stats["win_sd"],
            "deep": 0.0, "mkt_c": 0.0, "supermax": supermax,
            "an_z": (2 - stats["an_mean"]) / stats["an_sd"],
        })
    df = pd.DataFrame(rows)
    df["age_z2"] = df.age_z ** 2
    return df[["season"] + COVARS]


def edwards_curves(post: pd.DataFrame, stats: dict, scenario_win: float) -> dict:
    path = edwards_path(stats, scenario_win)
    h_draws = predict_hazard(post, path[COVARS].values, era=3, draws=True)  # (draws, 7)
    surv = np.cumprod(1 - h_draws, axis=1)
    cum = 1 - surv
    q = lambda a, lo, hi: (np.percentile(a, lo, axis=0), np.percentile(a, hi, axis=0))
    ann_lo, ann_hi = q(h_draws, 10, 90)
    cum_lo, cum_hi = q(cum, 10, 90)
    return {
        "scenario_team_win_pct_2yr": scenario_win,
        "annual": [{"season": int(s), "hazard_mean": float(h_draws[:, i].mean()),
                    "lo80": float(ann_lo[i]), "hi80": float(ann_hi[i])}
                   for i, s in enumerate(path.season)],
        "cumulative": [{"season": int(s), "p_departed_by_mean": float(cum[:, i].mean()),
                        "lo80": float(cum_lo[i]), "hi80": float(cum_hi[i])}
                       for i, s in enumerate(path.season)],
    }


def main():
    params = load_params()
    seed = params["seed"] + 2
    d_all, stats = prep(pd.read_parquet(STAGED / "star_spells_provisional.parquet"))
    meta = json.loads((STAGED / "star_spells_provisional.meta.json").read_text())
    print(f"rows {len(d_all)}, events {d_all.event.sum()}, spells {d_all.spell_id.nunique()} "
          f"(freeze {meta['freeze_hash']})")

    # spell-level holdout for gates
    rng = np.random.default_rng(params["model_b"]["holdout_seed"])
    spells = np.array(sorted(d_all.spell_id.unique()))
    test_spells = set(rng.choice(spells, int(0.2 * len(spells)), replace=False))
    train = d_all[~d_all.spell_id.isin(test_spells)]
    test = d_all[d_all.spell_id.isin(test_spells)]

    post_tr, health_tr = fit(train, "train", seed)
    p_test = np.concatenate([
        predict_hazard(post_tr, g[COVARS].values, era=e)
        for e, g in test.groupby("era")])
    y_test = np.concatenate([g.event.values for _, g in test.groupby("era")])
    c_index = auc(p_test, y_test)
    cal_slope = calibration_slope(p_test, y_test)

    cox = cox_sign_check(d_all)
    post_full, health_full = fit(d_all, "full", seed)
    bayes_means = {c: float(post_full[f"b_{c}"].mean()) for c in COVARS}
    sign_pairs = {c: (np.sign(cox[c]), np.sign(bayes_means[c]))
                  for c in cox}
    sign_ok = all(s1 == s2 for s1, s2 in sign_pairs.values())

    # borderline sensitivity: exclude the 21 kept-borderline spells
    d_nob = d_all[~d_all.borderline_kept]
    post_nob, _ = fit(d_nob, "no_borderline", seed)

    OUT_JSON.mkdir(parents=True, exist_ok=True)
    curves = {
        "tag": "PROVISIONAL",
        "freeze_hash": meta["freeze_hash"],
        "contract_covariate": "OMITTED (0% historical coverage at M0; final fit requires backfill)",
        "scenarios": {
            "central_win60": edwards_curves(post_full, stats, 0.60),
            "decline_win45": edwards_curves(post_full, stats, 0.45),
        },
        "borderline_sensitivity": {
            "central_win60_excl_borderlines": edwards_curves(post_nob, stats, 0.60),
        },
    }
    (OUT_JSON / "edwards_hazard_PROVISIONAL.json").write_text(json.dumps(curves, indent=1))

    cum_full = curves["scenarios"]["central_win60"]["cumulative"][-1]["p_departed_by_mean"]
    cum_nob = curves["borderline_sensitivity"]["central_win60_excl_borderlines"]["cumulative"][-1]["p_departed_by_mean"]

    gate_c = c_index >= 0.63
    gate_cal = 0.8 <= cal_slope <= 1.2
    lines = [
        "# Model B hazard (gates 8.2) -- PROVISIONAL",
        f"- freeze {meta['freeze_hash']}; {len(d_all)} rows, {int(d_all.event.sum())} departures; "
        "contract covariate OMITTED (0% coverage); July-6 updates not applied",
        f"- train MCMC r_hat {health_tr.get('worst_r_hat', float('nan')):.4f} "
        f"ess {health_tr.get('min_ess_bulk', float('nan')):.0f}; "
        f"full r_hat {health_full.get('worst_r_hat', float('nan')):.4f}",
        f"- C-index (held-out rows): {c_index:.3f} (gate >= 0.63) -> "
        f"**{'PASS' if gate_c else 'FAIL'}**",
        f"- calibration slope: {cal_slope:.3f} (gate [0.8, 1.2]) -> "
        f"**{'PASS' if gate_cal else 'FAIL'}**",
        f"- Cox sign agreement: {'PASS' if sign_ok else 'FAIL'} "
        f"{ {c: (float(cox[c]), bayes_means[c]) for c in cox} }",
        f"- Edwards cumulative P(departed by 2033), central scenario: "
        f"{cum_full:.3f}; excluding 21 borderlines: {cum_nob:.3f} "
        f"(delta {cum_nob - cum_full:+.3f})",
    ]
    OUT_VAL.mkdir(parents=True, exist_ok=True)
    (OUT_VAL / "model_b_hazard_PROVISIONAL.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    sys.exit(0 if (gate_c and gate_cal and sign_ok) else 1)


if __name__ == "__main__":
    main()
