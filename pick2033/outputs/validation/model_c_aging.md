# Model C aging curves (gates 8.3)
- delta rows 14496 (2861 imputed dropout rows), players 2432
- train MCMC: r_hat 1.0050, ess 687; with-imp r_hat 1.0054; no-imp r_hat 1.0055
- held-out RMSE: model 1.799 vs no-aging 1.849 vs league-mean 1.849 -> **PASS**
- survivor-bias audit (max |with - without| past age 30, BPM):
    - big: 0.14 (imputed version authoritative past 30 per spec)
    - guard: 0.08 (imputed version authoritative past 30 per spec)
    - wing: 0.11 (imputed version authoritative past 30 per spec)