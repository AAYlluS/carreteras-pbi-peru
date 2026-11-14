"""Step 0: district GDP per capita from Seminario & Palomino (2022).

The estimates are published by Universidad del Pacífico as an Excel workbook
linked from Annex 4 of

  Seminario, B. & Palomino, L. (2022). Estimación del PIB a nivel subnacional
  utilizando datos satelitales de luminosidad: Perú, 1993-2018. Universidad del
  Pacífico. https://doi.org/10.21678/978-9972-57-493-1

The workbook is not redistributed here. This script downloads it once into
data/external/ (git-ignored), checks that it is the published file (SHA-256),
and computes, for each district, GDP per capita = GDP / population (sheets
PIB_Dist and Poblacion_Dist) and GDP per km2 = GDP / area (column Territorio,
km2), the latter only for the map in Figure 1.

Output: data/processed/gdp_seminario_palomino.csv
        (ubigeo, PIB2007, PIB2017, PIB2018, GDPkm2_2007, GDPkm2_2017)
"""
import hashlib
import sys
import urllib.request

import pandas as pd

from common import EXTERNAL, PROC

URL = ("https://fondoeditorial.up.edu.pe/wp-content/uploads/2022/05/"
       "Excel_Estimaci%C3%B3n-del-PBI-a-nivel-subnacional.xlsx")
FILE = EXTERNAL / "Excel_Estimacion-del-PBI-a-nivel-subnacional.xlsx"
SHA256 = "34387978592b60a5bc3039d46e5005e0dbc7207b9222966c3a4c5bba84480bd4"
YEARS = [2007, 2017, 2018]


def sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch() -> None:
    if FILE.exists() and sha256(FILE) == SHA256:
        return
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {URL}")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (research code)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        FILE.write_bytes(r.read())
    if sha256(FILE) != SHA256:
        sys.exit(f"{FILE.name}: checksum differs from the published file. If the publisher "
                 "updated it, check the values before changing SHA256 in this script.")


def read(sheet: str) -> pd.DataFrame:
    x = pd.read_excel(FILE, sheet_name=sheet).dropna(subset=["Ubigeo"])
    x["ubigeo"] = x["Ubigeo"].astype(int).astype(str).str.zfill(6)
    return x.set_index("ubigeo")[["Territorio"] + YEARS]


def main() -> None:
    fetch()
    gdp, pop = read("PIB_Dist"), read("Poblacion_Dist")
    pc = (gdp[YEARS] / pop.reindex(gdp.index)[YEARS]).rename(columns={y: f"PIB{y}" for y in YEARS})
    for y in (2007, 2017):
        pc[f"GDPkm2_{y}"] = gdp[y] / gdp["Territorio"]
    assert pc.index.is_unique and len(pc) == 1834, len(pc)
    pc.reset_index().to_csv(PROC / "gdp_seminario_palomino.csv", index=False)
    print(f"GDP per capita for {len(pc)} districts -> data/processed/gdp_seminario_palomino.csv")


if __name__ == "__main__":
    main()
