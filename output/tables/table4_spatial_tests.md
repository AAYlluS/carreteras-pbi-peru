# Table 4: tests for spatial dependence in the OLS residuals

OLS of growth on road density, controls and department fixed effects; N = 1191. W = first-order contiguity matrix, spectral normalisation. Moran z, LM and robust LM follow Anselin (1988) and Anselin et al. (1996); KP chi2 is the Kelejian-Prucha version of the Moran test. The check_* columns of the CSV repeat the statistics with spreg/esda.

| Test | Statistic | p-value |
|---|---|---|
| Moran's I (z) | 0.364 (22.13) | 0.000 |
| LM error | 417.09 | 0.000 |
| Robust LM error | 292.92 | 0.000 |
| LM lag | 124.19 | 0.000 |
| Robust LM lag | 0.012 | 0.914 |
| Moran, Kelejian-Prucha chi2(1) | 417.09 | 0.000 |
