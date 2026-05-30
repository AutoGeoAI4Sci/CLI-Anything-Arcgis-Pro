"""``arcgis-cli layout`` — professional cartographic export.

This is the module that distinguishes ArcGIS Pro from QGIS for an agent:
high-fidelity layout export with precise DPI control, and **Map Series**
(a.k.a. map books / Data Driven Pages) — exporting one styled layout across
many features into a single paged PDF. QGIS's atlas support is far weaker here.
"""

import os

import click

from ._io import arcgis_command

# format -> (exporter method name, accepts resolution kwarg)
_EXPORTERS = {
    "PDF": ("exportToPDF", True),
    "PNG": ("exportToPNG", True),
    "TIFF": ("exportToTIFF", True),
    "JPEG": ("exportToJPEG", True),
    "SVG": ("exportToSVG", True),
    "EPS": ("exportToEPS", False),
    "AIX": ("exportToAIX", False),
}


def _resolve_layout(proj, layout_name):
    layouts = proj.listLayouts(layout_name) if layout_name else proj.listLayouts()
    if not layouts:
        raise ValueError(f"No layout matching {layout_name!r}")
    if layout_name and len(layouts) > 1:
        raise ValueError(f"{layout_name!r} matches {len(layouts)} layouts; be specific")
    return layouts[0]


@click.group("layout")
def layout_group():
    """Export print layouts and map series (the ArcGIS Pro cartography advantage)."""


@layout_group.command("list")
@click.argument("aprx", type=click.Path(exists=True, dir_okay=False))
@arcgis_command()
def list_cmd(aprx):
    """List layouts, page sizes, and whether each drives a Map Series."""
    import arcpy

    proj = arcpy.mp.ArcGISProject(aprx)
    out = []
    for lyt in proj.listLayouts():
        entry = {
            "name": lyt.name,
            "pageWidth": lyt.pageWidth,
            "pageHeight": lyt.pageHeight,
            "pageUnits": str(lyt.pageUnits),
            "mapSeries": None,
        }
        if lyt.mapSeries is not None:
            ms = lyt.mapSeries
            entry["mapSeries"] = {
                "enabled": ms.enabled,
                "pageCount": ms.pageCount,
                "indexLayer": getattr(ms.indexLayer, "name", None),
                "pageNumberField": getattr(getattr(ms, "pageNumberField", None), "name", None),
            }
        out.append(entry)
    return {"aprx": aprx, "layouts": out}


@layout_group.command("export")
@click.argument("aprx", type=click.Path(exists=True, dir_okay=False))
@click.option("--layout", "layout_name", required=True, help="Layout name to export.")
@click.option("--out", "out_path", required=True, type=click.Path(), help="Output file path.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(sorted(_EXPORTERS), case_sensitive=False),
    default=None,
    help="Export format (default: inferred from --out extension, else PDF).",
)
@click.option("--dpi", default=300, show_default=True, help="Output resolution.")
@arcgis_command()
def export_cmd(aprx, layout_name, out_path, fmt, dpi):
    """Export a single layout to PDF/PNG/TIFF/JPEG/SVG/EPS at a given DPI."""
    import arcpy

    if fmt is None:
        ext = os.path.splitext(out_path)[1].lstrip(".").upper()
        fmt = {"TIF": "TIFF", "JPG": "JPEG"}.get(ext, ext) if ext else "PDF"
        if fmt not in _EXPORTERS:
            fmt = "PDF"
    fmt = fmt.upper()
    method_name, takes_res = _EXPORTERS[fmt]

    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    proj = arcpy.mp.ArcGISProject(aprx)
    lyt = _resolve_layout(proj, layout_name)
    exporter = getattr(lyt, method_name)
    if takes_res:
        exporter(out_path, resolution=dpi)
    else:
        exporter(out_path)
    return {
        "layout": lyt.name,
        "format": fmt,
        "dpi": dpi if takes_res else None,
        "output": os.path.abspath(out_path),
        "exists": os.path.isfile(out_path),
        "bytes": os.path.getsize(out_path) if os.path.isfile(out_path) else 0,
    }


@layout_group.command("mapseries")
@click.argument("aprx", type=click.Path(exists=True, dir_okay=False))
@click.option("--layout", "layout_name", required=True, help="Layout that drives the map series.")
@click.option("--out", "out_path", required=True, type=click.Path(), help="Output PDF (map book).")
@click.option("--dpi", default=300, show_default=True, help="Output resolution.")
@click.option(
    "--pages",
    default=None,
    help='Page range, e.g. "1-5,8". Omit to export ALL pages.',
)
@arcgis_command()
def mapseries_cmd(aprx, layout_name, out_path, dpi, pages):
    """Export a Map Series / map book to a single multi-page PDF.

    This is the headline ArcGIS Pro capability: one styled layout iterated over
    every feature of an index layer, paginated into one PDF.
    """
    import arcpy

    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    proj = arcpy.mp.ArcGISProject(aprx)
    lyt = _resolve_layout(proj, layout_name)
    if lyt.mapSeries is None:
        raise ValueError(f"Layout {lyt.name!r} has no map series enabled")
    ms = lyt.mapSeries

    if pages:
        ms.exportToPDF(out_path, "RANGE", page_range_string=pages, resolution=dpi)
        range_type = f"RANGE:{pages}"
    else:
        ms.exportToPDF(out_path, "ALL", resolution=dpi)
        range_type = "ALL"
    return {
        "layout": lyt.name,
        "pageCount": ms.pageCount,
        "exported": range_type,
        "dpi": dpi,
        "output": os.path.abspath(out_path),
        "exists": os.path.isfile(out_path),
        "bytes": os.path.getsize(out_path) if os.path.isfile(out_path) else 0,
    }
