"""``arcgis-cli info`` — environment / license sanity check (great first call for agents)."""

import sys

import click

from ._io import arcgis_command


@click.command("info")
@arcgis_command()
def info_cmd():
    """Report ArcPy version, license level and available extensions."""
    import arcpy

    install = arcpy.GetInstallInfo()
    extensions = {}
    for ext in (
        "Spatial",
        "3D",
        "GeoStats",
        "Network",
        "DataReviewer",
        "ImageAnalyst",
        "Business",
    ):
        try:
            extensions[ext] = arcpy.CheckExtension(ext)  # "Available" / "Unavailable" / ...
        except Exception as exc:  # noqa: BLE001
            extensions[ext] = f"error: {exc}"

    return {
        "python": sys.version.split()[0],
        "python_exe": sys.executable,
        "arcpy_version": install.get("Version"),
        "build": install.get("BuildNumber"),
        "install_dir": install.get("InstallDir"),
        "product_license": arcpy.ProductInfo(),
        "extensions": extensions,
    }
