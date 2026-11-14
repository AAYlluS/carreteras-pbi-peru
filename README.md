# Roads and Growth in Peru's Periphery

**Author:** Álvaro Alexander Yllu Socualaya
**Paper:** [`paper/working_paper/working_paper.pdf`](paper/working_paper/working_paper.pdf)

Code and data for *Roads and Growth in Peru's Periphery: District-Level Evidence from Nighttime-Light GDP* (working paper, November 2026).

The paper asks whether road infrastructure raised economic growth in Peru's peripheral districts between 2007 and 2018. District GDP per capita comes from estimates based on nighttime lights (Seminario & Palomino, 2022). Road density is instrumented with the distance to the pre-Columbian Inca road network (Qhapaq Ñan), and a spatial-error model allows for dependence between neighbouring districts.

**Main result.** OLS shows a positive association between road density and growth. The 2SLS and spatial-error estimates are not significantly different from zero. They are imprecise: the 95% interval of the 2SLS estimate, [−0.54, 0.45], rules out large effects (more than about 6 log points of 2007–2018 growth per standard deviation of road density) but contains the OLS estimate.

## How to run

Requirements: Python 3.10 and about 1 GB of free disk space. Tested on Windows 10 with Python 3.10.4.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt     # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # macOS/Linux
```

Then run everything (an internet connection is needed the first time, to download the GDP data):

```bash
python run_all.py              # about 1 min
python run_all.py --skip-gis   # without the maps
```

`run_all.py` deletes and rebuilds `data/processed/` and `output/tables/`, redraws the maps in `output/figures/` (Figure 1 only if the MTC road layers are present; otherwise the committed map is kept), then builds the paper (HTML, and PDF if Microsoft Edge or Google Chrome is installed). No step uses random numbers, and repeated runs give identical outputs.

## Results and the code that produces them

| Result | Script | Output |
|---|---|---|
| District GDP per capita | `code/00_get_gdp.py` | `data/processed/gdp_seminario_palomino.csv` |
| Analysis samples | `code/01_clean.py` | `data/processed/sample_*.csv` |
| Table 1 (descriptive statistics) | `code/02_analysis.py` | `output/tables/table1.{csv,md,tex}` |
| Table 2 (first stage) | `code/02_analysis.py` | `output/tables/table2.{csv,md,tex}` |
| Table 3 (OLS and 2SLS) | `code/02_analysis.py` | `output/tables/table3.{csv,md,tex}` |
| Table 4 (Moran and LM tests) | `code/03_spatial.py` | `output/tables/table4_spatial_tests.{csv,md}` |
| Table 5 (spatial-error IV model) | `code/03_spatial.py` | `output/tables/table5_spatial_iv.{csv,md}` |
| Table 6 (what the 2SLS estimate rules out) | `code/04_inference.py` | `output/tables/inference_checks.csv` |
| Figure 1 (roads and GDP per km²) | `code/05_figures.py` (needs the MTC road layers; see `data/README.md`) | `output/figures/fig1_roads_gdp.{png,pdf}` |
| Figure 2 (study districts) | `code/05_figures.py` | `output/figures/fig2_study_districts.{png,pdf}` |
| Figure 3 (Inca road) | `code/05_figures.py` | `output/figures/fig3_inca_road.{png,pdf}` |
| Figure 4 (Kruskal network) | `code/05_figures.py` | `output/figures/fig4_kruskal_network.{png,pdf}` |
| Paper | `code/06_working_paper.py` | `paper/working_paper/working_paper.{html,pdf}` |

`code/00_get_gdp.py` downloads the Seminario & Palomino (2022) workbook from the publisher into `data/external/` (once; checked by SHA-256) and computes district GDP per capita. `code/author_export_public.py` is run once by the author to export the public variables from the working files; users do not need it.

## Data availability

| Data | Source | In this repository |
|---|---|---|
| District GDP and population, 1993–2018 | Seminario, B. & Palomino, L. (2022), *Estimación del PIB a nivel subnacional utilizando datos satelitales de luminosidad: Perú, 1993-2018*, Universidad del Pacífico. doi:10.21678/978-9972-57-493-1. Public workbook linked in the book's Annex 4 | Not copied into the repository (the publication is © Universidad del Pacífico, CC BY-NC-ND 4.0). `code/00_get_gdp.py` downloads it from the publisher. |
| Census 2007 and 2017 variables (education, agriculture, urban population) | INEI, Censos Nacionales (Redatam) | Yes, district aggregates in `data/raw/analysis/analysis_public.csv` |
| Mining indicator, MYPE counts | author's compilation | Yes, in `analysis_public.csv` |
| District boundaries and centroids | INEI (CPV 2017) | Yes, `data/raw/gis/` |
| National and departmental road networks | Ministerio de Transportes y Comunicaciones (SINAC) | Road lengths and densities: yes. Raw layers (58–150 MB each): no, see `data/README.md` |
| Inca road network (Qhapaq Ñan) | Oré Menéndez, based on Chacaltana, Arkush & Marcone (2011); CC0 1.0 | Yes |
| Kruskal network between departmental capitals | built by the author (QGIS) | Yes |
| Contiguity weight matrix | built by the author | Yes, `data/raw/analysis/W.dta` |

Codebook and details: [`data/README.md`](data/README.md).

## Repository layout

```
├── README.md, LICENSE, CITATION.cff, requirements.txt, run_all.py
├── paper/working_paper/     paper (text.md source, HTML, PDF)
├── data/raw/                public inputs (never modified by the code)
├── data/external/           NOT in git: Seminario & Palomino workbook (downloaded by the code from Universidad del Pacífico)
├── data/processed/          rebuilt by run_all.py
├── code/                    00–06 pipeline scripts, common.py
└── output/tables, figures/  all results
```

## Citation

See [`CITATION.cff`](CITATION.cff).

> Yllu Socualaya, Á. A. (2026). *Roads and Growth in Peru's Periphery: District-Level Evidence from Nighttime-Light GDP*. Working paper.

## License

Code: MIT. Paper, documentation, tables and figures: CC BY 4.0. Data keep their providers' terms. See [`LICENSE`](LICENSE).
