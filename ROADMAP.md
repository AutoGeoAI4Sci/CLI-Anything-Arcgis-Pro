# Roadmap

Where **CLI-Anything · ArcGIS Pro** is headed, and where you can help.

> **North star:** an AI agent should be able to take a task from *raw data → analysis → a finished, publication-ready map* end to end — with no human clicking in the GUI. We're most of the way on **analysis**; the open frontier is **cartographic authoring** (making the map look right) and **feature editing** (writing data back).

---

## How to read this

Each item lists the **command / MCP tool** to add, its rough signature, and the underlying API on **both** execution paths (see *Two API worlds* below). Items are tagged:

- 🟢 **good first issue** — small, self-contained, mentorship available
- 🐍 **no ArcGIS license needed** — touches the stdlib MCP server / CLI wiring / tests / docs only
- 🪟 **needs licensed ArcGIS Pro** — exercises real ArcPy or the live .NET bridge

If you want to contribute, open an issue (or comment on an existing one) before a large PR so we can align on the command shape.

---

## Two API worlds (read this first)

The same GIS concept is reached through **two different APIs**, one per execution mode:

| | Headless CLI (`.aprx` on disk) | Live bridge (the open session) |
|---|---|---|
| API | **ArcPy** — `arcpy.mp`, `arcpy.da` | **ArcGIS Pro SDK for .NET** (C# add-in) |
| Threading | runs in-process | everything wrapped in `QueuedTask.Run` (CIM thread) |
| Editing | `arcpy.da` cursors inside an `Editor` session | **`EditOperation`** (gives undo/redo) |

**Key constraint:** an external process *cannot* obtain `ArcGISProject("CURRENT")` — that only works inside Pro's built-in Python window. So every **write** to the live session must go through the **.NET add-in** (`live-bridge/ProSimpleMapExport`). New capabilities are generally implemented twice, or deliberately scoped to one path.

**The CIM escape hatch.** Anything the high-level API doesn't expose (deep symbol/label/layout control) is reachable by dropping to the **CIM** (the low-level JSON definition):

- ArcPy: `lyr.getDefinition('V3')` → mutate → `lyr.setDefinition(cim)` (Pro 3.x = `'V3'`)
- .NET: `layer.GetDefinition()` → mutate `ArcGIS.Core.CIM` objects → `layer.SetDefinition()` (inside `QueuedTask`)

A generic `cim get` / `cim set` power-tool (see Phase 3) lets an agent reach anything we haven't wrapped yet.

---

## Shipped — v0.1.0

The analysis + export half is in place.

| Area | Surface |
|---|---|
| Environment | `info` |
| Project (read) | `project inspect`, `project layers` |
| Cartography (export) | `layout list`, `layout export`, `layout mapseries`, `batch export-layouts` |
| Data (read + field calc) | `data describe`, `data fields`, `data count`, `data query`, `data calc` |
| Geoprocessing | `gp` — runs **any** ArcToolbox tool |
| Live MCP tools | `arcgis_ping`, `arcgis_query`, `arcgis_run_gp`, `arcgis_zoom_to`, `arcgis_export_layout` |

What's missing: the agent can run a buffer, but it can't yet **add the result to a map, symbolize it, compose a layout, or edit features** — that's the rest of this roadmap.

---

## Phase 1 — Cartographic authoring (the differentiator) → v0.2.0

This is where ArcGIS Pro beats QGIS, and it's our biggest gap. Completing Phase 1 closes the core narrative loop:

> `gp` (analyze) → `map add-data` (add result) → `map symbology graduated` (auto-classify colors) → `layout export` (finished map) — **zero human clicks.**

### 1.1 Layer management 🪟
Add/remove/configure layers in a map.

- **Commands:** `map add-data <path> [--map] [--name]`, `map remove-layer <name>`, `map set-visible <name> <bool>`, `map def-query <name> <sql>`
- Headless: `Map.addDataFromPath()`, `Map.addLayer()`, `Map.removeLayer()`, `lyr.visible`, `lyr.definitionQuery`, `Map.moveLayer()`
- Live (.NET): `LayerFactory.Instance.CreateLayer(uri, map)`, `map.RemoveLayer()`, `layer.SetVisibility()`, `layer.SetDefinitionQuery(sql)`
- **MCP:** `arcgis_add_data`, `arcgis_set_layer`
- **Acceptance:** after `gp` produces an output, one command makes it a visible layer in the active map; verified in both headless and live paths.

### 1.2 Symbology 🪟 — *highest-value single item*
Apply renderers so the map actually communicates.

- **Commands:** `map symbology graduated <layer> --field --classes --ramp`, `map symbology unique <layer> --field`, `map symbology simple <layer> --color`, `map apply-lyrx <layer> <lyrx>`
- Headless (standard 4-step): `sym = lyr.symbology` → `sym.updateRenderer('GraduatedColorsRenderer')` → set `sym.renderer.classificationField`, `breakCount`, `colorRamp` → `lyr.symbology = sym`. For `unique`: `sym.updateRenderer('UniqueValueRenderer')` then `sym.renderer.fields = [...]`. Template path: `arcpy.management.ApplySymbologyFromLayer`.
- Supported renderers: `SimpleRenderer`, `GraduatedColorsRenderer`, `GraduatedSymbolsRenderer`, `UnclassedColorsRenderer`, `UniqueValueRenderer`.
- Live (.NET): CIM route — `layer.GetDefinition()` → swap `CIMFeatureLayer.Renderer` (`CIMClassBreaksRenderer` / `CIMUniqueValueRenderer`) → `SetDefinition()`.
- **MCP:** `arcgis_symbology`
- **Acceptance:** a quantitative field renders as graduated colors; a categorical field renders as unique values; both visible in the live session and in an exported PDF.

### 1.3 Labeling 🪟
- **Commands:** `map labels on <layer> --field` / `map labels off <layer>` / `map labels expression <layer> <expr>`
- Headless: `lyr.showLabels`, `lyr.listLabelClasses()`, label class `.expression`; deeper styling via CIM `CIMLabelClass`.
- Live (.NET): CIM `CIMFeatureLayer.LabelClasses` + `LabelVisibility`.
- **Acceptance:** labels toggle on with a chosen field and survive export.

### 1.4 Layout authoring (build a map, don't just export one) 🪟
- **Commands:** `layout create --name --width --height --units`, `layout add-element legend|scalebar|northarrow|text <layout> [--map-frame] [--text]`
- Headless: `aprx.createLayout(w, h, units)`, `layout.createMapFrame(geom, map)`, `layout.createMapSurroundElement(geom, 'LEGEND'|'SCALE_BAR'|'NORTH_ARROW', mapframe)`, `layout.createTextElement(...)`
- Live (.NET): `ElementFactory.Instance.CreateMapFrameElement / CreateLegendElement / CreateScaleBarElement / CreateNorthArrowElement`, text via `CreateTextGraphicElement`
- **Acceptance:** an agent builds a layout from scratch (map frame + legend + scale bar + title) and exports it to PDF.

---

## Phase 2 — Feature editing & selection (the write half) → v0.3.0

"Operate ArcGIS" means CRUD, not just read. Today we have `data query` (read) + `data calc` (field calc) only.

### 2.1 Feature CRUD 🪟
- **Commands:** `data insert <fc> --json`, `data update <fc> --where --set`, `data delete <fc> --where`
- Headless: `arcpy.da.InsertCursor` (add), `arcpy.da.UpdateCursor` (update + delete), **wrapped in an `arcpy.da.Editor(workspace)` edit session** to respect locks/versioned data; geometry via `SHAPE@` / `SHAPE@XY` tokens.
- Live (.NET) — **must** use this path on open data: `EditOperation` → `op.Create(layer, attrs)` / `op.Modify()` / `op.Delete()` / `op.Execute()` inside `QueuedTask`. ⚠️ Never open a raw ArcPy cursor on data Pro has open — it locks/conflicts.
- **MCP:** `arcgis_edit`
- **Acceptance:** insert/update/delete a feature in the live session with working undo; the same operations work headless against a file GDB.

### 2.2 Schema management 🪟 🟢
- **Commands:** `data create-fc`, `data add-field`, `data delete-field`
- Headless: `arcpy.management.CreateFeatureclass`, `AddField`, `DeleteField`
- **Acceptance:** create an empty feature class with defined fields, then insert into it via 2.1.

### 2.3 Selection 🪟
- **Commands / MCP:** `arcgis_select <layer> --where | --intersects`, `arcgis_clear_selection`
- Headless: `arcpy.management.SelectLayerByAttribute`, `SelectLayerByLocation`
- Live (.NET): `layer.Select(QueryFilter)`, `MapView.Active.SelectFeatures(geom)`, `map.ClearSelection()`
- **Note:** `arcgis_zoom_to` currently does a where-select as a side effect — split that into a first-class selection capability.

---

## Phase 3 — Power tools & polish → v0.4.0

### 3.1 Generic CIM access 🪟
- **Commands / MCP:** `cim get <layer|layout>`, `cim set <layer|layout> --json` — the universal escape hatch for anything unwrapped.

### 3.2 Navigation (live) 🪟
- `arcgis_pan`, `arcgis_set_scale`, `arcgis_zoom_bookmark`, switch active map/view.
- Live (.NET): `MapView.Active` — `PanTo`, `camera.Scale`, `ZoomToBookmark`.

### 3.3 Project/document management 🪟
- `project save`, `project save-copy`, `project new-map`, import `.mapx` / `.lyrx`.
- Headless: `aprx.save()`, `aprx.saveACopy()`, `aprx.createMap()`. Live: `Project.Current.SaveAsync()`, `MapFactory.Instance.CreateMap`.

---

## Project health (parallel track, mostly license-free)

These don't need ArcGIS Pro and are great entry points:

- 🐍 🟢 **CI** — GitHub Actions running `test_core.py` (already backend-free) on each push, plus a tests badge.
- 🐍 🟢 **MCP server test** — feed the stdlib server a `tools/list` JSON-RPC request and assert the 5 tools come back. (`mcp_server.py` currently has no test.)
- 🐍 🟢 **Docs** — quickstart recipes, a worked "data → map" example, expand `SKILL.md`.
- 🐍 🟢 **Mock-based CLI tests** — verify command wiring without a Pro license.

---

## Later / long-tail (not scheduled)

Raster & mosaic datasets · 3D scenes · publishing to ArcGIS Online / web maps · Report authoring · ModelBuilder/Task integration. Open an issue if you need one of these and we'll prioritize by demand.

---

## Contributing

Heads-up: ArcGIS Pro is Esri's commercial, **Windows-only** desktop app, so the 🪟 items need a licensed install. But the 🐍 items (MCP protocol layer, tests, docs) need **none** — and "just try it and file an issue where it breaks" is genuinely valuable. See the **Contributing** section of the [README](README.md). First-timers welcome on anything tagged 🟢.
