"""Demo 3 - a complete regional GIS workflow: DATA -> CLIP -> ANALYSIS -> MAP.

Real, reproducible, end to end. Downloads Natural Earth data (public domain),
clips world cities to a chosen country, builds 50 km service areas, computes
coverage stats, then composes a finished layout (basemap, boundary, cities,
service areas, legend, north arrow, scale bar) and exports it to PDF.

Run with ArcGIS Pro's Python:
    "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" demos\\region_workflow.py
Optional: pass a country name, e.g.  ... region_workflow.py Kenya
"""

import os
import shutil
import ssl
import sys
import tempfile
import urllib.request
import zipfile

import arcpy

COUNTRY = sys.argv[1] if len(sys.argv) > 1 else "Nepal"
BUF_KM = 50

HERE = os.path.dirname(os.path.abspath(__file__))
SAMP = os.path.join(HERE, "_sample")
CACHE = os.path.join(SAMP, "naturalearth")
GDB = os.path.join(SAMP, "workflow.gdb")
APRX = os.path.join(SAMP, "Workflow.aprx")
PDF = os.path.join(SAMP, f"{COUNTRY}_service_areas.pdf")

NE = {
    "ne_10m_admin_0_countries": "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip",
    "ne_10m_populated_places": "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_populated_places.zip",
}
BLANK_APRX = r"C:\Program Files\ArcGIS\Pro\Resources\ArcToolBox\Services\routingservices\data\Blank.aprx"

arcpy.env.overwriteOutput = True


def step(n, title):
    print(f"\n{'=' * 64}\n  STEP {n}: {title}\n{'=' * 64}")


def fetch(name, url):
    shp = os.path.join(CACHE, name + ".shp")
    if os.path.isfile(shp):
        print(f"  [cache] {name}")
        return shp
    print(f"  [download] {name} ...")
    os.makedirs(CACHE, exist_ok=True)
    tmp = os.path.join(tempfile.gettempdir(), name + ".zip")
    with urllib.request.urlopen(url, timeout=180, context=ssl.create_default_context()) as r, open(tmp, "wb") as f:
        f.write(r.read())
    with zipfile.ZipFile(tmp) as z:
        z.extractall(CACHE)
    return shp


def main():
    os.makedirs(SAMP, exist_ok=True)

    step(1, "DATA - fetch Natural Earth (countries + populated places)")
    countries = fetch("ne_10m_admin_0_countries", NE["ne_10m_admin_0_countries"])
    places = fetch("ne_10m_populated_places", NE["ne_10m_populated_places"])

    if arcpy.Exists(GDB):
        arcpy.management.Delete(GDB)
    arcpy.management.CreateFileGDB(os.path.dirname(GDB), os.path.basename(GDB))
    region = os.path.join(GDB, "region")
    cities = os.path.join(GDB, "cities")
    region_line = os.path.join(GDB, "region_line")
    buf = os.path.join(GDB, "cities_buffer")
    svc = os.path.join(GDB, "service_area")

    step(2, f"CLIP - extract {COUNTRY} and clip world cities to it")
    arcpy.management.MakeFeatureLayer(countries, "c_lyr", f"NAME = '{COUNTRY}'")
    arcpy.management.CopyFeatures("c_lyr", region)
    if int(arcpy.management.GetCount(region)[0]) == 0:
        raise SystemExit(f"No country named '{COUNTRY}' in Natural Earth (try the exact NAME).")
    arcpy.analysis.Clip(places, region, cities)
    n_cities = int(arcpy.management.GetCount(cities)[0])
    print(f"  -> {n_cities} cities inside {COUNTRY}")

    step(3, f"ANALYSIS - {BUF_KM} km geodesic service areas + coverage stats")
    arcpy.analysis.Buffer(cities, buf, f"{BUF_KM} Kilometers", method="GEODESIC")
    arcpy.analysis.PairwiseDissolve(buf, svc)
    arcpy.management.AddField(svc, "AREA_KM2", "DOUBLE")
    arcpy.management.CalculateGeometryAttributes(svc, [["AREA_KM2", "AREA_GEODESIC"]], area_unit="SQUARE_KILOMETERS")
    coverage = sum(r[0] for r in arcpy.da.SearchCursor(svc, ["AREA_KM2"]))
    pops = sorted((r[0] for r in arcpy.da.SearchCursor(cities, ["POP_MAX"]) if r[0]), reverse=True)
    print(f"  -> {BUF_KM} km coverage: {coverage:,.0f} sq km")
    print(f"  -> largest city pop: {pops[0]:,.0f}" if pops else "  -> no population data")

    step(4, "MAP - compose a finished layout")
    arcpy.management.PolygonToLine(region, region_line)
    shutil.copyfile(BLANK_APRX, APRX)
    aprx = arcpy.mp.ArcGISProject(APRX)
    m = aprx.listMaps()[0]
    m.addBasemap("Light Gray Canvas")
    for path in (svc, region_line, cities):  # bottom -> top
        m.addDataFromPath(path)

    friendly = {"service_area": f"{BUF_KM} km service area", "region_line": f"{COUNTRY} boundary", "cities": "Cities"}
    for lyr in m.listLayers():
        if lyr.name in friendly:
            lyr.name = friendly[lyr.name]
    m.listLayers(f"{BUF_KM} km service area")[0].transparency = 55

    lyt = aprx.createLayout(297, 210, "MILLIMETER", f"{COUNTRY} Service Areas")
    frame_geom = arcpy.Polygon(arcpy.Array([
        arcpy.Point(8, 8), arcpy.Point(208, 8), arcpy.Point(208, 196), arcpy.Point(8, 196)]))
    mf = lyt.createMapFrame(frame_geom, m, "MainFrame")
    boundary_lyr = m.listLayers(f"{COUNTRY} boundary")[0]
    mf.camera.setExtent(mf.getLayerExtent(boundary_lyr, False, True))
    lyt.createMapSurroundElement(arcpy.Point(198, 185), "NORTH_ARROW", mf, None, "NorthArrow")
    lyt.createMapSurroundElement(arcpy.Point(40, 14), "SCALE_BAR", mf, None, "ScaleBar")
    lyt.createMapSurroundElement(arcpy.Point(212, 188), "LEGEND", mf, None, "Legend")
    aprx.save()

    step(5, "EXPORT - render the map to PDF")
    lyt.exportToPDF(PDF, resolution=200)
    print(f"  -> {PDF}  ({os.path.getsize(PDF):,} bytes)")
    print(f"\nDone. {n_cities} cities, {coverage:,.0f} sq km of {BUF_KM} km coverage in {COUNTRY}.")
    try:
        os.startfile(PDF)  # pop the finished map (Windows)
    except Exception:
        pass


if __name__ == "__main__":
    main()
