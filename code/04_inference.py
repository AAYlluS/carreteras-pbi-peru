"""Step 4: what the 2SLS estimate can and cannot rule out (Table 6).

For the preferred specification (Table 3, column 4: growth on road density,
2007 controls and department fixed effects; road density instrumented with the
log distance to the Inca road) this script reports:

  1. the reduced form (growth on the instrument);
  2. the 2SLS estimate and its 95% Wald confidence interval;
  3. the Anderson-Rubin 95% confidence set, which stays valid if the instrument
     is weak (heteroskedasticity-robust, by test inversion on a fine grid);
  4. the OLS estimate and its 95% confidence interval;
  5. the Wu-Hausman and Wooldridge tests of exogeneity of road density;
  6. the implied effect of a one-standard-deviation increase in road density at
     the bounds of the intervals;
  7. the same 2SLS estimate with the stricter exclusion flag (Drop_alt).

Output: output/tables/inference_checks.csv (one row per statistic).
"""
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS

from common import CONTROLS, PROC, TABLES

warnings.filterwarnings("ignore")
CTRL = " + ".join(CONTROLS)
Z = "ln_dist_inca"  # ln distance to the Inca road
GRID = np.round(np.arange(-3.0, 3.0 + 1e-9, 0.001), 3)


def iv_fit(d):
    return IV2SLS.from_formula(f"Tasa ~ 1 + C(dpto) + {CTRL} + [Densidad_Total ~ {Z}]", d).fit(
        cov_type="robust", debiased=False)


def anderson_rubin(d) -> tuple[float, float, bool]:
    """Robust AR test of H0: beta = b0 is the HC1 t-test of the instrument in a
    regression of (y - b0 * x) on the instrument and all exogenous regressors."""
    keep = []
    for b0 in GRID:
        y0 = d["Tasa"] - b0 * d["Densidad_Total"]
        m = smf.ols(f"y0 ~ {Z} + {CTRL} + C(dpto)", d.assign(y0=y0)).fit(cov_type="HC1")
        if m.pvalues[Z] > 0.05:
            keep.append(b0)
    keep = np.array(keep)
    contiguous = len(keep) > 0 and np.allclose(np.diff(keep), 0.001)
    return keep.min(), keep.max(), bool(contiguous)


def main() -> None:
    d = pd.read_csv(PROC / "sample_2sls.csv").dropna(subset=CONTROLS)
    sd_x = d["Densidad_Total"].std()
    rows = []
    add = lambda k, v, note="": rows.append({"statistic": k, "value": v, "note": note})

    rf = smf.ols(f"Tasa ~ {Z} + {CTRL} + C(dpto)", d).fit(cov_type="HC1")
    add("reduced_form_coef", rf.params[Z], "growth on ln distance to Inca road, HC1")
    add("reduced_form_se", rf.bse[Z])
    add("reduced_form_p", rf.pvalues[Z])

    r = iv_fit(d)
    b, se = r.params["Densidad_Total"], r.std_errors["Densidad_Total"]
    add("iv_coef", b, "Table 3 column 4")
    add("iv_se", se)
    add("iv_ci95_low", b - 1.96 * se)
    add("iv_ci95_high", b + 1.96 * se)

    lo, hi, cont = anderson_rubin(d)
    add("ar_set95_low", lo, f"grid -3..3 step 0.001; contiguous={cont}")
    add("ar_set95_high", hi)

    o = smf.ols(f"Tasa ~ Densidad_Total + {CTRL} + C(dpto)", d).fit(cov_type="HC1")
    ci = o.conf_int().loc["Densidad_Total"]
    add("ols_coef", o.params["Densidad_Total"], "Table 3 column 2")
    add("ols_ci95_low", ci[0])
    add("ols_ci95_high", ci[1])

    wh = r.wu_hausman()
    wr = r.wooldridge_regression
    add("wu_hausman_F", wh.stat, f"F({wh.df}, {wh.df_denom})")
    add("wu_hausman_p", wh.pval)
    add("wooldridge_chi2", wr.stat)
    add("wooldridge_p", wr.pval)

    add("sd_density", sd_x, "km per km2, estimation sample")
    add("sd_growth", d["Tasa"].std(), "log points, 2007-2018")
    for k in ("iv_ci95_low", "iv_ci95_high", "ar_set95_low", "ar_set95_high", "ols_coef"):
        v = next(x["value"] for x in rows if x["statistic"] == k)
        add(f"effect_1sd__{k}", v * sd_x, "log points of 2007-2018 growth per 1 s.d. of road density")

    c = pd.read_csv(PROC / "sample_2sls_alt.csv").dropna(subset=CONTROLS)
    rc = iv_fit(c)
    add("iv_coef_drop_alt", rc.params["Densidad_Total"], f"stricter exclusion flag, N={int(rc.nobs)}")
    add("iv_se_drop_alt", rc.std_errors["Densidad_Total"])

    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "inference_checks.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
