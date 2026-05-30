"""``arcgis-cli project`` — inspect ArcGIS Pro projects (.aprx): maps, layouts, layers."""

import click

from ._io import arcgis_command


def _describe_layer(lyr):
    info = {"name": lyr.name, "isFeatureLayer": getattr(lyr, "isFeatureLayer", False)}
    try:
        info["visible"] = lyr.visible
    except Exception:
        pass
    try:
        if lyr.supports("DATASOURCE"):
            info["dataSource"] = lyr.dataSource
    except Exception:
        pass
    try:
        if lyr.supports("DEFINITIONQUERY"):
            info["definitionQuery"] = lyr.definitionQuery
    except Exception:
        pass
    return info


@click.group("project")
def project_group():
    """Inspect .aprx project structure."""


@project_group.command("inspect")
@click.argument("aprx", type=click.Path(exists=True, dir_okay=False))
@arcgis_command()
def inspect_cmd(aprx):
    """Summarise an .aprx: its maps, layouts and layer counts."""
    import arcpy

    proj = arcpy.mp.ArcGISProject(aprx)
    maps = []
    for m in proj.listMaps():
        maps.append(
            {
                "name": m.name,
                "mapType": m.mapType,
                "spatialReference": getattr(m.spatialReference, "name", None),
                "layerCount": len(m.listLayers()),
                "tableCount": len(m.listTables()),
            }
        )
    layouts = []
    for lyt in proj.listLayouts():
        layouts.append(
            {
                "name": lyt.name,
                "pageWidth": lyt.pageWidth,
                "pageHeight": lyt.pageHeight,
                "pageUnits": str(lyt.pageUnits),
                "hasMapSeries": lyt.mapSeries is not None,
            }
        )
    return {
        "aprx": aprx,
        "defaultGeodatabase": proj.defaultGeodatabase,
        "homeFolder": proj.homeFolder,
        "maps": maps,
        "layouts": layouts,
    }


@project_group.command("layers")
@click.argument("aprx", type=click.Path(exists=True, dir_okay=False))
@click.option("--map", "map_name", default=None, help="Map name (default: first map).")
@arcgis_command()
def layers_cmd(aprx, map_name):
    """List layers (with data sources and definition queries) in a map."""
    import arcpy

    proj = arcpy.mp.ArcGISProject(aprx)
    maps = proj.listMaps(map_name) if map_name else proj.listMaps()
    if not maps:
        raise ValueError(f"No map matching {map_name!r}")
    m = maps[0]
    return {
        "map": m.name,
        "layers": [_describe_layer(l) for l in m.listLayers()],
    }
