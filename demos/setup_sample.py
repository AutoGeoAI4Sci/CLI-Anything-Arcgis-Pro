"""Build self-contained sample data for the demos.

Creates demos/_sample/sample.gdb with a `cities` point layer, and (if a blank
ArcGIS Pro template can be found) demos/_sample/Sample.aprx with that layer in a
map — so the live-bridge demo has something to open and zoom/buffer.

Run with ArcGIS Pro's Python:
    "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" demos\\setup_sample.py
"""

import os
import shutil

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_sample")

# name, country, population, (lon, lat)
CITIES = [
    ("Kathmandu", "Nepal", 1442271, (85.3240, 27.7172)),
    ("Tokyo", "Japan", 13929286, (139.6917, 35.6895)),
    ("Los Angeles", "USA", 3898747, (-118.2437, 34.0522)),
    ("London", "UK", 8982000, (-0.1276, 51.5072)),
    ("Nairobi", "Kenya", 4397073, (36.8219, -1.2921)),
    ("Sao Paulo", "Brazil", 12325232, (-46.6333, -23.5505)),
    ("Sydney", "Australia", 5312163, (151.2093, -33.8688)),
]

BLANK_APRX_CANDIDATES = [
    r"C:\Program Files\ArcGIS\Pro\Resources\ArcToolBox\Services\routingservices\data\Blank.aprx",
]


def build_gdb():
    os.makedirs(OUT, exist_ok=True)
    gdb = os.path.join(OUT, "sample.gdb")
    if arcpy.Exists(gdb):
        arcpy.management.Delete(gdb)
    arcpy.management.CreateFileGDB(OUT, "sample.gdb")

    fc = os.path.join(gdb, "cities")
    arcpy.management.CreateFeatureclass(
        gdb, "cities", "POINT", spatial_reference=arcpy.SpatialReference(4326)
    )
    arcpy.management.AddField(fc, "NAME", "TEXT", field_length=40)
    arcpy.management.AddField(fc, "COUNTRY", "TEXT", field_length=40)
    arcpy.management.AddField(fc, "POP", "LONG")

    with arcpy.da.InsertCursor(fc, ["NAME", "COUNTRY", "POP", "SHAPE@XY"]) as cur:
        for name, country, pop, xy in CITIES:
            cur.insertRow([name, country, pop, xy])

    print(f"[ok] {fc}  ({len(CITIES)} cities)")
    return fc


def build_aprx(fc):
    template = next((p for p in BLANK_APRX_CANDIDATES if os.path.isfile(p)), None)
    if not template:
        print("[skip] no blank .aprx template found — Sample.aprx not created.")
        print("       (The headless demo still works; for the live demo open any")
        print("        project and add demos/_sample/sample.gdb/cities to a map.)")
        return None

    dst = os.path.join(OUT, "Sample.aprx")
    shutil.copyfile(template, dst)
    aprx = arcpy.mp.ArcGISProject(dst)
    m = aprx.listMaps()[0]

    # A basemap so the cities sit on a recognizable world map (not a blank canvas).
    for name in ("Topographic", "Light Gray Canvas", "Streets"):
        try:
            m.addBasemap(name)
            print(f"[ok] basemap added: {name}")
            break
        except Exception:
            continue

    m.addDataFromPath(fc)
    aprx.save()
    print(f"[ok] {dst}  (map '{m.name}' with basemap + cities layer)")
    return dst


if __name__ == "__main__":
    fc = build_gdb()
    build_aprx(fc)
    print("\nSample data ready under demos/_sample/.")
