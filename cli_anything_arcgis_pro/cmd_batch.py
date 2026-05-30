"""``arcgis-cli batch`` — batch operations (export every layout from a project)."""

import os

import click

from ._io import arcgis_command
from .cmd_layout import _EXPORTERS


@click.group("batch")
def batch_group():
    """Batch operations over many layouts / datasets."""


@batch_group.command("export-layouts")
@click.argument("aprx", type=click.Path(exists=True, dir_okay=False))
@click.option("--out-dir", required=True, type=click.Path(), help="Directory to write exports into.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(sorted(_EXPORTERS), case_sensitive=False),
    default="PDF",
    show_default=True,
)
@click.option("--dpi", default=300, show_default=True, help="Output resolution.")
@click.option("--include-mapseries/--skip-mapseries", default=True,
              help="Export map-series layouts as full map books (else single page).")
@arcgis_command()
def export_layouts_cmd(aprx, out_dir, fmt, dpi, include_mapseries):
    """Export every layout in an .aprx to OUT-DIR (filenames = layout names)."""
    import arcpy

    fmt = fmt.upper()
    method_name, takes_res = _EXPORTERS[fmt]
    ext = {"JPEG": "jpg", "TIFF": "tif"}.get(fmt, fmt.lower())
    os.makedirs(out_dir, exist_ok=True)

    proj = arcpy.mp.ArcGISProject(aprx)
    results = []
    for lyt in proj.listLayouts():
        safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in lyt.name).strip()
        out_path = os.path.join(out_dir, f"{safe}.{ext}")
        try:
            if include_mapseries and lyt.mapSeries is not None and fmt == "PDF":
                lyt.mapSeries.exportToPDF(out_path, "ALL", resolution=dpi)
                kind = "mapseries"
            else:
                exporter = getattr(lyt, method_name)
                exporter(out_path, resolution=dpi) if takes_res else exporter(out_path)
                kind = "layout"
            results.append(
                {
                    "layout": lyt.name,
                    "kind": kind,
                    "output": os.path.abspath(out_path),
                    "bytes": os.path.getsize(out_path) if os.path.isfile(out_path) else 0,
                    "ok": True,
                }
            )
        except Exception as exc:  # noqa: BLE001 - keep going, report per-layout
            results.append({"layout": lyt.name, "ok": False, "error": str(exc)})

    return {
        "aprx": aprx,
        "outDir": os.path.abspath(out_dir),
        "format": fmt,
        "dpi": dpi,
        "exported": sum(1 for r in results if r.get("ok")),
        "failed": sum(1 for r in results if not r.get("ok")),
        "results": results,
    }
