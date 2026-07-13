# Model B M2 FINAL refit (gates 8.2, second and final look)
- spec: M2_FINAL_SPEC (contract covariates, Normal(0,0.5) priors)
- health: train r_hat 1.0025, full r_hat 1.0025
- C-index: 0.907 (>= 0.63) -> **PASS**
- calibration slope: 1.413 [boot 90% CI 1.127, 1.872] ([0.8, 1.2]) -> **FAIL (stands documented, no third fit)**
- Cox sign agreement: PASS
- contract coefficients: b_contract_z -2.940, b_contract_known -0.015