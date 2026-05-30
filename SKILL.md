---
name: cli-anything-arcgis-pro
description: Drive ArcGIS Pro (ArcPy) from the command line — professional cartographic export (layouts + Map Series / map books), geoprocessing, batch processing, and feature-class query/edit. Also ships a live-Pro MCP bridge that lets an agent operate the OPEN ArcGIS Pro session (the closed-source counterpart to CLI-Anything's QGIS harness). Use when operating ArcGIS Pro, running ArcPy/geoprocessing, exporting print-quality maps/map books, or reading/editing geodatabases. Triggers: "ArcGIS", "ArcGIS Pro", "ArcPy", "出图/制图/地图册", ".aprx", "geoprocessing", "buffer/clip/intersect".
---

# CLI-Anything · ArcGIS Pro

An agent-native interface to **ArcGIS Pro** via its official **ArcPy** API.
ArcGIS Pro is closed-source, so it can't be auto-generated like CLI-Anything's
QGIS harness — this harness wraps the real ArcPy/Pro SDK instead.

Two modes:
- **Headless CLI** (`cli-anything-arcgis-pro`) — batch/automation over `.aprx`
  projects and geodatabases. JSON output for every command.
- **Live bridge + MCP** (`live-bridge/`) — an in-process ArcGIS Pro add-in that
  exposes the OPEN project to an agent over MCP; the user watches operations
  happen in the Pro window.

## Headless CLI

Install into ArcGIS Pro's Python (`arcgispro-py3`), then:

```
cli-anything-arcgis-pro --json info
```

Rules:
- Put `--json` BEFORE the subcommand. Output is one line: `{"ok": true, "data": ...}` or `{"ok": false, "error": ..., "type": ..., "arcpy_messages": ...}`.
- Start with `info` to confirm the license (`ArcInfo`/`ArcEditor`) and extensions.
- Paths are full Windows paths; a feature class inside a gdb is `C:\path\data.gdb\featureclass`.

### Commands

| Command | What it does |
|---|---|
| `info` | ArcPy version, license, extensions. Call first. |
| `project inspect <aprx>` / `project layers <aprx> [--map]` | Maps, layouts, layers, data sources. |
| `layout list <aprx>` | Layouts, page sizes, map-series status. |
| `layout export <aprx> --layout --out [--format] [--dpi]` | ★ Export one layout (PDF/PNG/TIFF/JPEG/SVG/EPS). |
| `layout mapseries <aprx> --layout --out [--pages] [--dpi]` | ★ Export a Map Series / map book to one paged PDF. |
| `data describe/fields/count/query/calc <dataset>` | Inspect & edit feature classes / tables. |
| `gp <tool> -a ... --kw k=v [--checkout EXT]` | Run ANY geoprocessing tool (`analysis.Buffer`, …). |
| `batch export-layouts <aprx> --out-dir [--format] [--dpi]` | Export every layout in a project. |

Examples:
```
cli-anything-arcgis-pro --json gp analysis.Buffer -a C:\d.gdb\roads -a C:\d.gdb\roads_buf --kw buffer_distance_or_field="100 Meters"
cli-anything-arcgis-pro --json layout export C:\proj\city.aprx --layout "Main" --out C:\out\main.pdf --dpi 300
cli-anything-arcgis-pro --json data query C:\d.gdb\roads --where "POP > 1000" --fields "NAME,POP" --geometry
```

## Live bridge + MCP (operate the OPEN Pro)

The CLI above is headless (it touches files, not the running app). To drive the
**live** ArcGIS Pro session, build & install the add-in in `live-bridge/` and
register the MCP server. It exposes tools: `arcgis_ping`, `arcgis_export_layout`,
`arcgis_zoom_to`, `arcgis_query`, `arcgis_run_gp` (the last runs the entire
ArcToolbox on the open project, with results added to the live map). See
`live-bridge/README.md`.

## Notes
- ArcPy holds a single-use license; avoid concurrent heavy commands on one project.
- A locked `.aprx` (open in Pro) can block edits to its data from the headless CLI — use the live bridge for the open project instead.
- On Windows shells prefer `--kw key="value with spaces"` over JSON to avoid quoting issues.
