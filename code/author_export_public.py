"""Author only: export the public analysis variables from the author's working
files, kept in data/restricted/original/ (git-ignored). It writes:

  data/raw/analysis/analysis_public.csv   all analysis variables except GDP,
                                          which code/00_get_gdp.py downloads
  data/raw/sources/consolidado_public.csv the author's Consolidado.xlsx without
                                          its GDP columns
  data/raw/gis/Distritos.gpkg,            district polygons and centroids without
  data/raw/gis/Centroids.gpkg             GDP attribute fields

Other users do not need this step; run_all.py does not run it.
"""
import sys

import numpy as np
import pandas as pd
import pyogrio

from common import GIS, RAW, ROOT

ORIG = ROOT / "data" / "restricted" / "original"
SRC = ROOT / "data" / "raw" / "sources"

# Working-file column -> public name. The two instrument columns hold log
# distances from the district centroid to the Inca road (in metres) and to the
# Kruskal network between departmental capitals (in kilometres).
RENAME = {"dist_tree": "ln_dist_inca", "dist_inca": "ln_dist_kruskal"}
PUBLIC_COLS = ["Id", "ubigeo", "dpto_nombre", "Prov", "Drop", "within_50km", "dist_capital",
               "Densidad_Total", "Densidad_Asfaltado", "DensidadNacional", "AcervoTotal", "AcervoNacional",
               "dist_asfaltado", "Conectado_", "dist_tree", "dist_inca",
               "Edu_2007", "Agro", "MYPE", "Minero", "Urbano", "Pob",
               "Edu_2017", "Agro_2017", "MYPE_2017", "Minero_2017", "Urbano_2017", "NTL_TOTAL"]
# Centroids.gpkg distance attributes, in metres.
GPKG_RENAME = {"dist_tree": "dist_kruskal_m", "dist_inca": "dist_inca_m"}


def read_stricter_flag(path) -> pd.Series:
    """The stricter exclusion flag (column `Drop`) of the later analysis sheet."""
    x = pd.read_excel(path, sheet_name="Stata Automatico")
    return x["Drop"].astype(str)


def main() -> None:
    if not (ORIG / "durbin.dta").exists():
        sys.exit("data/restricted/original/ not found: this step is for the author only.")

    full = pd.read_stata(ORIG / "durbin.dta", convert_categoricals=False)
    tasa = np.log(full.PIB2018) - np.log(full.PIB2007)
    assert np.allclose(tasa, full.Tasa, equal_nan=True, atol=1e-12), "Tasa != ln(PIB2018) - ln(PIB2007)"

    pub = full[PUBLIC_COLS + ["LENGTH_Dep", "LENGTH_Nac"]].rename(columns=RENAME)
    pub["Drop"] = pub["Drop"].astype(str)
    alt = read_stricter_flag(ORIG / "Distritos Spatial.csv.xlsx")
    assert len(alt) == len(pub)
    pub["Drop_alt"] = alt.values
    pub.to_csv(RAW / "analysis_public.csv", index=False)

    c = pd.read_excel(ORIG / "Consolidado.xlsx", sheet_name="Consolidado")
    c.drop(columns=["2007 PIB", "2017 PIB"]).to_csv(SRC / "consolidado_public.csv", index=False)

    for name in ("Distritos", "Centroids"):
        g = pyogrio.read_dataframe(ORIG / f"{name}.gpkg")
        g = g.drop(columns=[c for c in g.columns if c.upper().startswith("PIB")])
        if name == "Centroids":
            g = g.rename(columns=GPKG_RENAME)
        out = GIS / f"{name}.gpkg"
        out.unlink(missing_ok=True)
        pyogrio.write_dataframe(g, out, layer=name, driver="GPKG")

    print(f"public: {pub.shape}")


if __name__ == "__main__":
    main()
