"""Step 1: build the analysis samples.

Input
-----
data/raw/analysis/analysis_public.csv + data/processed/gdp_seminario_palomino.csv,
merged by common.load_analysis().

Outputs
-------
data/processed/sample_2sls.csv      estimation sample for Tables 2, 3 and 6
data/processed/sample_spatial.csv   estimation sample for Table 5 (MYPE in logs)
data/processed/sample_table1.csv    all districts, levels, for Table 1
data/processed/sample_2sls_alt.csv  as sample_2sls, with the stricter exclusion
                                    flag (robustness check in Table 6)
"""
import numpy as np
import pandas as pd

from common import L2, PROC, load_analysis, stata_encode


def sample_2sls(d: pd.DataFrame) -> pd.DataFrame:
    """Drop excluded districts, keep complete cases on L2, log urban population."""
    s = d[d["Drop"] != "Si"].dropna(subset=L2).copy()
    s["Urbano"] = np.log(s["Urbano"])
    s["dpto"] = stata_encode(s["dpto_nombre"])
    return s.sort_values("Id").reset_index(drop=True)


def sample_spatial(d: pd.DataFrame) -> pd.DataFrame:
    """Same sample as sample_2sls, but MYPE enters in logs: ln(MYPE), with
    ln(1e-6) for districts with zero or missing MYPE."""
    s = d[d["Drop"] != "Si"].dropna(subset=L2).copy()
    s["Urbano"] = np.log(s["Urbano"])
    m = s["MYPE"].where(s["MYPE"] > 0)
    s["MYPE"] = np.log(m).fillna(np.log(1e-6))
    s["dpto"] = stata_encode(s["dpto_nombre"])
    return s.sort_values("Id").reset_index(drop=True)


def sample_table1(d: pd.DataFrame) -> pd.DataFrame:
    """Table 1 compares districts near departmental capitals (Drop == "Si")
    with the study districts. Variables in levels."""
    s = d.copy()
    s["group"] = np.where(s["Drop"] == "Si", "within50km", "study")
    s["Urbano_level"] = s["Urbano"]
    return s[["Id", "ubigeo", "dpto_nombre", "group", "PIB2007", "Tasa", "Edu_2007",
              "Agro", "MYPE", "Urbano_level", "Minero"]]


def main() -> None:
    d = load_analysis("main")
    s1, s2, t1 = sample_2sls(d), sample_spatial(d), sample_table1(d)
    s1.to_csv(PROC / "sample_2sls.csv", index=False)
    s2.to_csv(PROC / "sample_spatial.csv", index=False)
    t1.to_csv(PROC / "sample_table1.csv", index=False)
    sample_2sls(load_analysis("alt")).to_csv(PROC / "sample_2sls_alt.csv", index=False)
    print(f"sample_2sls: {len(s1)} rows; sample_spatial: {len(s2)} rows; "
          f"table1 groups: {t1.group.value_counts().to_dict()}")


if __name__ == "__main__":
    main()
