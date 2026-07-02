# Model B hazard (gates 8.2) -- PROVISIONAL
- freeze 49f2135d534f3ce7; 1290 rows, 238 departures; contract covariate OMITTED (0% coverage); July-6 updates not applied
- train MCMC r_hat 1.0034 ess 1269; full r_hat 1.0024
- C-index (held-out rows): 0.675 (gate >= 0.63) -> **PASS**
- calibration slope: 0.664 (gate [0.8, 1.2]) -> **FAIL**
- Cox sign agreement: PASS {'age_z': (0.3662638866457283, 0.940141499042511), 'yrs_z': (-1.962254648101481e-16, -0.11008197069168091), 'win2_z': (-0.1769523744216352, -0.32242700457572937), 'deep': (-0.3427215956875313, -0.4964357614517212), 'mkt_c': (0.013642719056742001, 0.07910475134849548), 'supermax': (0.2423147651642942, 0.41805529594421387), 'an_z': (-0.09122637450069201, -0.35096755623817444)}
- Edwards cumulative P(departed by 2033), central scenario: 0.846; excluding 21 borderlines: 0.851 (delta +0.005)