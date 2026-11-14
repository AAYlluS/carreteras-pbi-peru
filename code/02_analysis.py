"""Step 2: Tables 1, 2 and 3.

Estimators:
  OLS   statsmodels, heteroskedasticity-robust HC1 standard errors
  2SLS  linearmodels IV2SLS, robust HC0 standard errors (no small-sample correction)
  Department fixed effects: dummies for dpto (codes in alphabetical order of the
  department name; the first department is the base).
  First-stage F: square of the robust (HC1) t statistic of the excluded
  instrument in the first stage.

Outputs: output/tables/table{1,2,3}.{csv,md,tex}
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS

from common import CONTROLS, LABELS, PROC, TABLES, fmt, stars

CTRL = " + ".join(CONTROLS)


# --------------------------------------------------------------------------- #
# estimation helpers
# --------------------------------------------------------------------------- #
def ols(formula: str, data: pd.DataFrame, keep: list[str]) -> dict:
    r = smf.ols(formula, data=data, missing="drop").fit(cov_type="HC1")
    out = {"n": int(r.nobs), "r2": r.rsquared, "coef": {}, "se": {}, "p": {}}
    for v in keep:
        name = "Intercept" if v == "const" else v
        out["coef"][v], out["se"][v], out["p"][v] = r.params[name], r.bse[name], r.pvalues[name]
    return out


def first_stage_F(formula: str, data: pd.DataFrame, instr: str) -> tuple[float, float]:
    """Robust first-stage F for a single excluded instrument."""
    r = smf.ols(formula, data=data, missing="drop").fit(cov_type="HC1")
    return (r.params[instr] / r.bse[instr]) ** 2, r.pvalues[instr]


def iv(dep: str, exog: str, endog: str, instr: str, data: pd.DataFrame, keep: list[str]) -> dict:
    cols = [dep, endog, instr, "dpto"] + ([c.strip() for c in exog.split("+")] if exog else [])
    d = data.dropna(subset=cols)
    rhs = f"1 + C(dpto)" + (f" + {exog}" if exog else "")
    r = IV2SLS.from_formula(f"{dep} ~ {rhs} + [{endog} ~ {instr}]", d).fit(cov_type="robust", debiased=False)
    out = {"n": int(r.nobs), "r2": r.rsquared, "coef": {}, "se": {}, "p": {}}
    for v in keep:
        name = "Intercept" if v == "const" else v
        out["coef"][v], out["se"][v], out["p"][v] = r.params[name], r.std_errors[name], r.pvalues[name]
    fs = f"{endog} ~ {instr} + C(dpto)" + (f" + {exog}" if exog else "")
    out["F"], out["F_p"] = first_stage_F(fs, d, instr)
    return out


# --------------------------------------------------------------------------- #
# table writers
# --------------------------------------------------------------------------- #
def to_long(table: str, cols: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for c, res in cols.items():
        for v in res["coef"]:
            rows.append((table, c, v, "coef", res["coef"][v], res["p"][v]))
            rows.append((table, c, v, "se", res["se"][v], np.nan))
        rows.append((table, c, "model", "n", res["n"], np.nan))
        rows.append((table, c, "model", "r2", res["r2"], np.nan))
        if "F" in res:
            rows.append((table, c, "model", "F", res["F"], res["F_p"]))
    return pd.DataFrame(rows, columns=["table", "column", "variable", "stat", "value", "p"])


def render(cols: dict[str, dict], order: list[str], header: dict[str, str], title: str, note: str):
    names = list(cols)
    lines = []
    for v in order:
        c_row, s_row = [LABELS.get(v, v)], [""]
        for k in names:
            r = cols[k]
            if v in r["coef"]:
                c_row.append(fmt(r["coef"][v]) + stars(r["p"][v]))
                s_row.append("(" + fmt(r["se"][v]) + ")")
            else:
                c_row += [""]; s_row += [""]
        lines += [c_row, s_row]
    lines.append(["Observations"] + [f"{cols[k]['n']:,}" for k in names])
    lines.append(["R²"] + [f"{cols[k]['r2']:.3f}" for k in names])
    if any("F" in cols[k] for k in names):
        lines.append(["First-stage F"] + [
            (f"{cols[k]['F']:.2f}" + stars(cols[k]["F_p"])) if "F" in cols[k] else "" for k in names])
    head = [""] + [f"{k} {header[k]}" for k in names]
    md = [f"**{title}**", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    md += ["| " + " | ".join(l) + " |" for l in lines]
    md += ["", note]
    tex = ["\\begin{tabular}{l" + "c" * len(names) + "}", "\\hline",
           " & ".join(head) + " \\\\", "\\hline"]
    tex += [" & ".join(x.replace("%", "\\%") for x in l) + " \\\\" for l in lines]
    tex += ["\\hline", "\\end{tabular}"]
    return "\n".join(md) + "\n", "\n".join(tex) + "\n"


def save(name: str, cols, order, header, title, note, table_id):
    to_long(table_id, cols).to_csv(TABLES / f"{name}.csv", index=False)
    md, tex = render(cols, order, header, title, note)
    (TABLES / f"{name}.md").write_text(md, encoding="utf-8")
    (TABLES / f"{name}.tex").write_text(tex, encoding="utf-8")
    print(md)


NOTE = ("Robust standard errors in parentheses (OLS: HC1; 2SLS: HC0). "
        "All regressions include department fixed effects. "
        "*** p<0.01, ** p<0.05, * p<0.1")


# --------------------------------------------------------------------------- #
def table1(t1: pd.DataFrame, s: pd.DataFrame) -> None:
    """Study group = Table 2-3 regression sample (complete on all controls);
    near-capital group = districts with Drop == "Si" and complete data on the
    Table 1 variables."""
    vars_ = ["PIB2007", "Tasa", "Edu_2007", "Agro", "MYPE", "Urbano_level", "Minero"]
    lab = {"PIB2007": "GDP per capita 2007 (soles)", "Tasa": "Growth of GDP per capita 2007-18",
           "Edu_2007": "Education (share)", "Agro": "Agriculture (share)", "MYPE": "MYPEs (number)",
           "Urbano_level": "Urban population", "Minero": "Mining (0/1)"}
    g_out = t1[t1.group == "within50km"].dropna(subset=vars_)
    study_ids = s.dropna(subset=CONTROLS)["Id"]
    g_in = t1[t1.Id.isin(study_ids)]
    rows = []
    for v in vars_:
        rows.append({"variable": v, "label": lab[v],
                     "within50km_n": g_out[v].notna().sum(), "within50km_mean": g_out[v].mean(),
                     "within50km_sd": g_out[v].std(),
                     "study_n": g_in[v].notna().sum(), "study_mean": g_in[v].mean(), "study_sd": g_in[v].std()})
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "table1.csv", index=False)
    md = ["**Table 1: Descriptive statistics, 2007**", "",
          "| Variable | N (near capitals) | Mean | s.d. | N (study) | Mean | s.d. |", "|---|---|---|---|---|---|---|"]
    tex = ["\\begin{tabular}{lrrrrrr}", "\\hline",
           "Variable & N & Mean & SD & N & Mean & SD \\\\", "\\hline"]
    for r in rows:
        cells = [r["label"], f"{r['within50km_n']}", f"{r['within50km_mean']:,.3f}", f"{r['within50km_sd']:,.3f}",
                 f"{r['study_n']}", f"{r['study_mean']:,.3f}", f"{r['study_sd']:,.3f}"]
        md.append("| " + " | ".join(cells) + " |")
        tex.append(" & ".join(c.replace("%", "\\%") for c in cells) + " \\\\")
    tex += ["\\hline", "\\end{tabular}"]
    (TABLES / "table1.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (TABLES / "table1.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")
    print("\n".join(md))


def table2(s: pd.DataFrame) -> None:
    keep = ["ln_dist_inca", "Edu_2007", "Agro", "MYPE", "Minero", "Urbano", "const"]
    c1 = ols(f"Densidad_Total ~ ln_dist_inca + {CTRL} + C(dpto)", s, keep)
    c1["F"], c1["F_p"] = first_stage_F(f"Densidad_Total ~ ln_dist_inca + {CTRL} + C(dpto)", s, "ln_dist_inca")
    keep2 = ["ln_dist_kruskal"] + keep[1:]
    c2 = ols(f"Densidad_Total ~ ln_dist_kruskal + {CTRL} + C(dpto)", s, keep2)
    c2["F"], c2["F_p"] = first_stage_F(f"Densidad_Total ~ ln_dist_kruskal + {CTRL} + C(dpto)", s, "ln_dist_kruskal")
    save("table2", {"(1)": c1, "(2)": c2},
         ["ln_dist_inca", "ln_dist_kruskal", "Edu_2007", "Agro", "MYPE", "Minero", "Urbano", "const"],
         {"(1)": "Road density", "(2)": "Road density"},
         "Table 2: First stage, road density on the candidate instruments", NOTE, "T2")


def table3(s: pd.DataFrame, name: str = "table3", verbose_title: str = "") -> dict:
    keep0 = ["Densidad_Total", "const"]
    keep = ["Densidad_Total"] + CONTROLS + ["const"]
    cols = {
        "(1)": ols("Tasa ~ Densidad_Total + C(dpto)", s, keep0),
        "(2)": ols(f"Tasa ~ Densidad_Total + {CTRL} + C(dpto)", s, keep),
        "(3)": iv("Tasa", "", "Densidad_Total", "ln_dist_inca", s, keep0),
        "(4)": iv("Tasa", CTRL, "Densidad_Total", "ln_dist_inca", s, keep),
    }
    save(name, cols, keep, {"(1)": "OLS", "(2)": "OLS", "(3)": "2SLS", "(4)": "2SLS"},
         verbose_title or "Table 3: Road density and growth of GDP per capita, 2007-2018", NOTE, "T3")
    return cols


def main() -> None:
    s = pd.read_csv(PROC / "sample_2sls.csv")
    t1 = pd.read_csv(PROC / "sample_table1.csv")
    table1(t1, s)
    table2(s)
    table3(s)


if __name__ == "__main__":
    main()
