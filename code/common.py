"""Shared paths and helpers.

All paths are relative to the repository root. Run every script from the root,
e.g. `python code/01_clean.py`.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Windows consoles default to cp1252; table text contains accents and symbols.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "analysis"
GIS = ROOT / "data" / "raw" / "gis"
PROC = ROOT / "data" / "processed"
EXTERNAL = ROOT / "data" / "external"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"

for p in (PROC, TABLES, FIGURES):
    p.mkdir(parents=True, exist_ok=True)

# Complete-data filters. L1 defines the 1,191 districts of the contiguity
# matrix W; L2 adds the 2017 variables and defines the 1,141-district
# estimation sample.
L1 = ["Tasa", "Minero", "Urbano", "ln_dist_inca", "Agro", "Edu_2007",
      "dist_asfaltado", "Conectado_", "Densidad_Asfaltado"]
L2 = L1 + ["Edu_2017", "Agro_2017", "MYPE_2017", "Urbano_2017", "NTL_TOTAL", "Minero_2017"]

CONTROLS = ["Edu_2007", "Agro", "MYPE", "Minero", "Urbano"]

# Display labels for the Markdown/LaTeX tables.
LABELS = {
    "Densidad_Total": "Road density",
    "ln_dist_inca": "ln distance to Inca road",
    "ln_dist_kruskal": "ln distance to Kruskal network",
    "Edu_2007": "Education 2007 (share)",
    "Agro": "Agriculture 2007 (share)",
    "MYPE": "MYPEs 2007",
    "Minero": "Mining 2007 (0/1)",
    "Urbano": "ln urban population 2007",
    "const": "Constant",
}


def load_analysis(flag: str = "main") -> pd.DataFrame:
    """Analysis dataset: the public district file plus GDP per capita from
    Seminario & Palomino (2022), built by code/00_get_gdp.py.

    flag="main" -> exclusion flag `Drop` used in the paper
    flag="alt"  -> stricter exclusion flag `Drop_alt` (robustness check)
    Growth: Tasa = ln(PIB2018) - ln(PIB2007).
    """
    pub = pd.read_csv(RAW / "analysis_public.csv", dtype={"ubigeo": str, "Drop": str, "Drop_alt": str})
    pub["ubigeo"] = pub["ubigeo"].str.zfill(6)
    f = PROC / "gdp_seminario_palomino.csv"
    if not f.exists():
        sys.exit("Missing data/processed/gdp_seminario_palomino.csv: run code/00_get_gdp.py first.")
    gdp = pd.read_csv(f, dtype={"ubigeo": str})
    d = pub.merge(gdp, on="ubigeo", how="left", validate="1:1")
    d["Tasa"] = np.log(d["PIB2018"]) - np.log(d["PIB2007"])
    if flag == "alt":
        d["Drop"] = d["Drop_alt"]
    d["Drop"] = d["Drop"].astype(str)
    return d.sort_values("Id").reset_index(drop=True)


def stata_encode(s: pd.Series) -> pd.Series:
    """Mimic Stata `encode`: integer codes 1..K in sorted (alphabetical) order."""
    cats = sorted(s.dropna().astype(str).unique())
    return s.astype(str).map({c: i + 1 for i, c in enumerate(cats)}).astype(int)


def stars(p: float) -> str:
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


def fmt(x: float, sig: int = 3) -> str:
    """Format with 3 significant digits."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    if x == 0:
        return "0"
    return f"{x:.{sig}g}" if abs(x) < 1e-3 else f"{x:.{max(sig - 1 - int(np.floor(np.log10(abs(x)))), 0)}f}"
