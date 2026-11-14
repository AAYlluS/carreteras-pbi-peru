# Data

Nothing in `data/raw/` is modified by the code. `data/processed/` is rebuilt by `run_all.py`, and neither it nor `data/external/` is committed.

The analysis data come in two parts:
- **District variables:** everything except GDP, in `data/raw/analysis/analysis_public.csv`.
- **GDP per capita:** from the public workbook of Seminario & Palomino (2022), which `code/00_get_gdp.py` downloads (see below).

`common.load_analysis()` merges the two parts by `ubigeo`.

## `data/raw/analysis/`

| File | What it is |
|---|---|
| `analysis_public.csv` | 1,874 districts. `Id`, `ubigeo`, department, the exclusion flags, road density and lengths, the two instruments, and all 2007 and 2017 controls. **No GDP columns.** |
| `W.dta` | 1,191 × 1,191 first-order contiguity matrix, spectral normalisation (largest eigenvalue 1). Rows and columns are the 1,191 districts with `Drop` ≠ "Si" and complete data on the variables in `common.L1`, in `Id` order. |

## `data/external/` (not in git): Seminario & Palomino (2022)

`code/00_get_gdp.py` downloads `Excel_Estimación-del-PBI-a-nivel-subnacional.xlsx` (4.7 MB), the workbook linked in Annex 4 of Seminario & Palomino (2022), from the publisher:

https://fondoeditorial.up.edu.pe/wp-content/uploads/2022/05/Excel_Estimaci%C3%B3n-del-PBI-a-nivel-subnacional.xlsx

The script checks the file's SHA-256 and stops if the publisher's file has changed. GDP per capita is district GDP (sheet `PIB_Dist`) divided by population (sheet `Poblacion_Dist`), for 2007, 2017 and 2018. GDP per km² (`GDPkm2_2007`, `GDPkm2_2017`), used only for the map in Figure 1, is district GDP divided by the district area in column `Territorio`. The result is `data/processed/gdp_seminario_palomino.csv`. The workbook covers 1,834 districts, of which 1,832 match the 1,874 districts of the INEI 2017 boundaries by `ubigeo`. The other 42 districts (mostly created after 2007) have no GDP and drop out of the analysis.

The workbook is not copied into this repository: the publication is © Bruno Seminario, Luis Palomino and Universidad del Pacífico, distributed open access under CC BY-NC-ND 4.0 (https://hdl.handle.net/11354/3422). Cite it as: Seminario, B. & Palomino, L. (2022). *Estimación del PIB a nivel subnacional utilizando datos satelitales de luminosidad: Perú, 1993-2018*. Universidad del Pacífico. https://doi.org/10.21678/978-9972-57-493-1

## `data/raw/sources/`

| File | Content |
|---|---|
| `Urbano.xlsx` | Census 2007 Redatam export: urban and rural population by district (source of `Urbano`) |
| `consolidado_public.csv` | the author's district compilation `Consolidado.xlsx`, without its GDP columns (source of `Minero`) |

## Codebook

| Variable | Definition | Source |
|---|---|---|
| `Id` | District row id 1–1874 | |
| `ubigeo` | INEI district code | INEI |
| `dpto_nombre` | Department name. Department fixed effects are dummies for it | INEI |
| `PIB2007`, `PIB2017`, `PIB2018` | District GDP per capita (soles), estimated from nighttime lights: GDP / population | Seminario & Palomino (2022), downloaded by `code/00_get_gdp.py` |
| `Tasa` | Growth of GDP per capita: `ln(PIB2018) − ln(PIB2007)` | derived |
| `Densidad_Total` | Length of national and departmental roads in the district (km) / district area (km²) | MTC road networks, author's GIS processing |
| `ln_dist_inca` | ln of the distance (metres) from the district centroid to the Inca road (`gis/Qapac/QN_pw.shp`). Main instrument | author's GIS processing |
| `ln_dist_kruskal` | ln of the distance (km) from the district centroid to the Kruskal minimum spanning tree between departmental capitals, computed with terrain-based link costs and drawn as straight lines (`gis/MST.gpkg`). Second candidate instrument | author's GIS processing |
| `Edu_2007` | Share of the population with completed secondary education or more, 2007 | INEI, Census 2007 (Redatam) |
| `Agro` | Share of workers in agriculture, 2007 | INEI, Census 2007 (Redatam) |
| `MYPE` | Number of micro and small enterprises in the district, 2007. Levels in Tables 1–3; `ln(MYPE)`, with `ln(1e-6)` for zero or missing, in Table 5 | author's compilation |
| `Minero` | 1 if the district has mining activity, 2007 | author's compilation (`sources/consolidado_public.csv`) |
| `Urbano` | Urban population, 2007. Regressions use `ln(Urbano)` | INEI, Census 2007 (`sources/Urbano.xlsx`) |
| `Drop` | `"Si"` = excluded from the estimation sample: the district centroid lies within 50 km of a departmental capital (25 capitals incl. Callao), or the district has no GDP data | author, GIS |
| `Drop_alt` | Stricter version of `Drop`: it excludes 208 more districts, all with part of their territory within 50 km of a capital (`within_50km` = 1). Used only for the robustness check in Table 6 | author, GIS |
| `within_50km` | 1 if any part of the district polygon lies within 50 km of a departmental capital | author, GIS |
| `*_2017` | the same controls measured in 2017; used to define the complete-data sample | INEI, author |

## `data/raw/gis/`: layers used for the maps

| File | Content | Source / license |
|---|---|---|
| `Distritos.gpkg` | 1,874 district polygons (`fuente`: "INEI - CPV2017 RESULTADOS") with the author's QGIS attributes | INEI, public |
| `Centroids.gpkg` | District centroids (EPSG:5387) with distances in metres to the Inca road (`dist_inca_m`) and to the Kruskal network (`dist_kruskal_m`) | derived |
| `MST.gpkg` | Kruskal minimum spanning tree between departmental capitals: 24 straight-line links chosen with terrain-based link costs (field `cost`) | built by the author in QGIS |
| `Cap_Departa/` | Departmental capitals (points) | IGN, public |
| `Qapac/` | Qhapaq Ñan road (`QN_pw`), sites and Tawantinsuyo extent | Oré Menéndez, based on Chacaltana, Arkush & Marcone (2011); license CC0 1.0 (from the shapefile metadata) |
| `Qapac.gpkg` | QGIS export of an Inca road layer | author |
| `Nacional_2007.gpkg`, `Nacional_2017.gpkg`, `Departamental_2007.gpkg`, `Departamental_2017.gpkg` | MTC national and departmental road networks (SINAC). **Not committed** (58–150 MB each). The two national layers are needed only to redraw Figure 1. | Ministerio de Transportes y Comunicaciones, public. Download from the MTC geoportal (Datos espaciales, Red Vial Nacional / Departamental) and save them here under these names. Note: the "2007" layers carry an update date of 2017 and the road classification of D.S. 011-2016-MTC. |

Road lengths, densities and distances were computed from these layers in QGIS; the resulting variables are in `analysis_public.csv`. Other raw inputs used upstream are not included because of their size: VIIRS and DMSP nighttime-light rasters (Earth Observation Group, Colorado School of Mines), the MTC Red Vial Vecinal layer, and INEI census tables.
