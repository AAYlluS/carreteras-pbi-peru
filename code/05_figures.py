"""Step 5: maps (Figures 1-4 of the paper).

Outputs (PNG at 200 dpi plus PDF, in output/figures/)
-------
fig1_roads_gdp         Figure 1: GDP per km2 and asphalted national roads, 2007 and 2017
fig2_study_districts   Figure 2: districts in the study (blue) vs excluded (white)
fig3_inca_road         Figure 3: Inca road (Qhapaq Nan)
fig4_kruskal_network   Figure 4: Kruskal minimum spanning tree between departmental capitals

Notes
-----
* Projection: EPSG:5387 (Peru96 / UTM 18S).
* GDP and roads: district GDP per km2 from Seminario & Palomino (2022), in 7
  quantile classes per year (districts without GDP in white). Roads: segments
  of the MTC national road network files Nacional_2007 / Nacional_2017 whose
  surface label RST_LBL is "Asfaltado". In the 2017 panel, a piece of road is
  "new" (red) if its midpoint is more than 250 m from every 2007 asphalted
  segment. The road layers are large and not in the repository; without them
  this map is skipped and the committed PNG/PDF are kept.
* Peripheral districts: districts whose centroid (Centroids.gpkg) lies within
  50 km of a departmental capital (Cap_Departa, 25 points incl. Callao) are
  white; the rest are blue. A few districts farther from the capitals are also
  excluded because they have no GDP data (mostly districts created after 2007);
  they are drawn blue with a grey hatch and listed separately in the legend.
* Kruskal network: MST.gpkg (24 straight-line edges, minimum spanning tree
  between the 25 points of Cap_Departa, Callao included, computed with
  terrain-based link costs). Label offsets are set by hand for a
  few capitals that would overlap.
* Inca road: Qapac/QN_pw.shp, the Peruvian extract of the Qhapaq Nan layer. It
  is the layer used to compute the instrument ln_dist_inca.

The script is deterministic (no randomness; PDF timestamps are removed).
"""
import time
import warnings

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import shapely  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from common import FIGURES, GIS, load_analysis  # noqa: E402

warnings.filterwarnings("ignore", message="Measured \\(M\\) geometry types")

T0 = time.time()
CRS = 5387
DPI = 200
DRAW_SIMPLIFY_M = 50  # vertex simplification for drawing only (1 px is about 1 km)
STUDY_BLUE = "#6070e0"
N_CLASSES = 7
RAMP = ["#ffff00", "#d6e200", "#adc500", "#84a800", "#5b8a00", "#326d00", "#095000"]
NEW_ROAD_TOLERANCE_M = 250
# Hand-set label offsets (points) for capitals whose labels would overlap.
LABEL_OFFSETS = {
    "PROV. CONSTITUCIONAL CALLAO": (-4, 0, "right"),
    "CHACHAPOYAS": (-4, 0, "right"),
    "MOYOBAMBA": (4, 2, "left"),
    "ABANCAY": (-4, -5, "right"),
    "CUSCO": (4, 4, "left"),
    "LIMA": (4, 0, "left"),
}
DISTRICT_GREY = "#c8c8c8"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                     "pdf.fonttype": 42})


def save(fig, name):
    fig.savefig(FIGURES / f"{name}.png", dpi=DPI, bbox_inches="tight",
                metadata={"Software": None})
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight",
                metadata={"CreationDate": None, "ModDate": None, "Producer": None,
                          "Creator": None})
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


def base_axes(bounds, figsize=(6.2, 7.4)):
    fig, ax = plt.subplots(figsize=figsize)
    pad = 0.03 * (bounds[2] - bounds[0])
    ax.set_xlim(bounds[0] - pad, bounds[2] + pad)
    ax.set_ylim(bounds[1] - pad, bounds[3] + pad)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    return fig, ax


def read(rel, **kw):
    path = GIS / rel
    if not path.exists():
        print(f"  SKIP: {rel} not found")
        return None
    return gpd.read_file(path, **kw).to_crs(CRS)


def load_districts():
    d = load_analysis("main").set_index("ubigeo")
    g = gpd.read_file(GIS / "Distritos.gpkg").to_crs(CRS)
    g = g[["ubigeo", "geometry"]].set_index("ubigeo").join(
        d[["Drop", "GDPkm2_2007", "GDPkm2_2017"]], how="left")
    assert g.Drop.notna().all(), "ubigeo merge failed"
    # Drawing uses a 50 m simplification (about 1/20 of a pixel at 200 dpi).
    g["geometry"] = g.geometry.simplify(DRAW_SIMPLIFY_M)
    return g


def asphalted(layer):
    """Asphalted segments, 2D, simplified for drawing (tolerance well below 1 px)."""
    r = layer[layer.RST_LBL == "Asfaltado"]
    return shapely.simplify(shapely.force_2d(r.geometry.values), DRAW_SIMPLIFY_M)


def draw_lines(ax, geoms, color, lw):
    """Draw many lines as one LineCollection (much faster than GeoSeries.plot)."""
    parts = shapely.get_parts(geoms)
    ax.add_collection(LineCollection([shapely.get_coordinates(x) for x in parts],
                                     colors=color, linewidths=lw, zorder=2))


def split_into_pieces(lines, max_len):
    """Explode (multi)lines into 2-vertex segments no longer than max_len metres."""
    parts = shapely.get_parts(shapely.segmentize(lines, max_len))
    coords, idx = shapely.get_coordinates(parts, return_index=True)
    same = idx[1:] == idx[:-1]  # consecutive vertices of the same line
    seg = np.stack([coords[:-1][same], coords[1:][same]], axis=1)
    return shapely.linestrings(seg)


# ------------------------------------------------------ GDP and roads
def fig_roads_gdp(g):
    print("GDP per km2 and asphalted national roads")
    nac07 = read("Nacional_2007.gpkg")
    nac17 = read("Nacional_2017.gpkg")
    if nac07 is None or nac17 is None:
        print("  SKIP: national road layers missing; existing fig1_roads_gdp files kept")
        return
    a07, a17 = asphalted(nac07), asphalted(nac17)
    # 2017 asphalted lines in pieces of at most 200 m; a piece is "new" when its
    # midpoint is more than NEW_ROAD_TOLERANCE_M from every 2007 asphalted segment.
    pieces = split_into_pieces(a17, max_len=200)
    mid = shapely.line_interpolate_point(pieces, 0.5, normalized=True)
    _, dist07 = shapely.STRtree(a07).query_nearest(mid, return_distance=True, all_matches=False)
    is_new = dist07 > NEW_ROAD_TOLERANCE_M
    km = lambda geoms: shapely.length(geoms).sum() / 1000  # noqa: E731
    print(f"  asphalted national km: 2007 {km(a07):,.0f}; 2017 {km(a17):,.0f} "
          f"(new vs 2007: {km(pieces[is_new]):,.0f})")
    panels = [("2007", [(a07, "black", "National network, asphalted", 0.35)]),
              ("2017", [(pieces[~is_new], "black", "National network, asphalted", 0.35),
                        (pieces[is_new], "#e0303a", "New asphalted roads since 2007", 0.6)])]
    fig, axes = plt.subplots(1, 2, figsize=(11, 7.4))
    b = g.total_bounds
    pad = 0.03 * (b[2] - b[0])
    for ax, (year, roads) in zip(axes, panels):
        v = g[f"GDPkm2_{year}"]
        br = np.quantile(v.dropna(), np.arange(1, N_CLASSES + 1) / N_CLASSES)
        cls = np.searchsorted(br, v.values, side="left")
        for i, c in enumerate(RAMP):
            sub = g[(cls == i) & v.notna().values]
            if len(sub):
                sub.plot(ax=ax, color=c, edgecolor="#4d4d4d", linewidth=0.08)
        g[v.isna().values].plot(ax=ax, color="white", edgecolor="#4d4d4d", linewidth=0.08)
        for geoms, color, _, lw in roads:
            draw_lines(ax, geoms, color, lw)
        handles = [Patch(facecolor=c, edgecolor="#4d4d4d", label=f"up to {x:,.0f}")
                   for c, x in zip(RAMP, br)]
        handles.append(Patch(facecolor="white", edgecolor="#4d4d4d", label="No data"))
        handles += [Line2D([], [], color=c, lw=1.2, label=lab) for _, c, lab, _ in roads]
        ax.legend(handles=handles, title="GDP per km² (soles)", loc="lower left",
                  frameon=False, fontsize=6.5, title_fontsize=7.5)
        ax.set_xlim(b[0] - pad, b[2] + pad)
        ax.set_ylim(b[1] - pad, b[3] + pad)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(year, fontsize=10)
    fig.tight_layout()
    save(fig, "fig1_roads_gdp")


# ------------------------------------------------- peripheral districts
def fig_study_districts(g):
    print("Study districts")
    cap = read("Cap_Departa/Cap_Departa.shp")
    cen = gpd.read_file(GIS / "Centroids.gpkg").set_index("ubigeo").reindex(g.index)
    d_cap = shapely.distance(cen.geometry.values, shapely.union_all(cap.geometry.values))
    near = d_cap < 50_000
    nodata = (g.Drop == "Si").values & ~near
    print(f"  centroid within 50 km: {near.sum()}; Drop == 'Si' but farther "
          f"(no GDP data): {nodata.sum()}")
    fig, ax = base_axes(g.total_bounds)
    g[~near].plot(ax=ax, color=STUDY_BLUE, edgecolor="white", linewidth=0.1)
    g[near].plot(ax=ax, color="white", edgecolor="#333333", linewidth=0.15)
    if nodata.any():
        g[nodata].plot(ax=ax, color="none", edgecolor="#9a9a9a", hatch="////",
                       linewidth=0.0)
    ax.legend(handles=[
        Patch(facecolor=STUDY_BLUE, label=f"In the study ({(~near & ~nodata).sum()})"),
        Patch(facecolor="white", edgecolor="#333333",
              label=f"Centroid within 50 km of a capital ({near.sum()})"),
        Patch(facecolor=STUDY_BLUE, edgecolor="#9a9a9a", hatch="////",
              label=f"No GDP data, also excluded ({nodata.sum()})")],
        loc="lower left", frameon=False, fontsize=7)
    save(fig, "fig2_study_districts")


# ------------------------------------------------------- Kruskal network
def fig_kruskal(g):
    print("Kruskal network")
    mst = read("MST.gpkg")
    cap = read("Cap_Departa/Cap_Departa.shp")
    if mst is None or cap is None:
        print("  SKIP Kruskal network")
        return
    fig, ax = base_axes(g.total_bounds)
    g.plot(ax=ax, color=DISTRICT_GREY, edgecolor="#6e6e6e", linewidth=0.1)
    mst.plot(ax=ax, color="#333333", linewidth=2.4)
    mst.plot(ax=ax, color="white", linewidth=1.4)
    cap.plot(ax=ax, color="white", edgecolor="black", markersize=14, zorder=3)
    for x, y, name in zip(cap.geometry.x, cap.geometry.y, cap.Nombre):
        dx, dy, ha = LABEL_OFFSETS.get(name, (4, 2, "left"))
        ax.annotate(name, (x, y), xytext=(dx, dy), textcoords="offset points",
                    ha=ha, va="center", fontsize=5.5,
                    bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.8))
    save(fig, "fig4_kruskal_network")


# -------------------------------------------------------------- Inca road
def fig_inca(g):
    print("Inca road (Qapac/QN_pw.shp)")
    inca = read("Qapac/QN_pw.shp")
    if inca is None:
        print("  SKIP Inca road")
        return
    fig, ax = base_axes(g.total_bounds)
    g.plot(ax=ax, color=DISTRICT_GREY, edgecolor="#6e6e6e", linewidth=0.1)
    inca.plot(ax=ax, color="#d7263d", linewidth=0.9)
    save(fig, "fig3_inca_road")


def main():
    g = load_districts()
    fig_roads_gdp(g)
    fig_study_districts(g)
    fig_inca(g)
    fig_kruskal(g)
    print(f"Runtime: {time.time() - T0:.1f} s")


if __name__ == "__main__":
    main()
