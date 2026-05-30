# Demos

Self-contained demos — good for screen recordings. They build their own data, so
anyone with ArcGIS Pro can reproduce them.

- **Demo 3 (`region_workflow.py`)** is the headline one: a complete, real
  workflow — **data → clip → analysis → finished map** — on public Natural Earth
  data. Start here.
- Demos 1 & 2 below are short, focused tours of the headless CLI and the live bridge.

## 0. Build the sample data (once)

```bat
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" demos\setup_sample.py
```

Creates under `demos\_sample\`:
- `sample.gdb\cities` — 7 world cities (NAME, COUNTRY, POP).
- `Sample.aprx` — a project with a **Topographic basemap** + the cities layer,
  so the data shows on a recognizable world map (not a blank canvas).

`demos\_sample\` is git-ignored (regenerate it anytime).

## 3. Region workflow — DATA -> CLIP -> ANALYSIS -> MAP (headline demo)

A complete, real GIS workflow end to end, on public-domain Natural Earth data:

```bat
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" demos\region_workflow.py
:: or pick a country:  ... demos\region_workflow.py Kenya
```

Steps (each prints a banner, good for a screencast):
1. **DATA** - download Natural Earth countries + populated places (cached).
2. **CLIP** - extract the country boundary, clip world cities to it.
3. **ANALYSIS** - 50 km geodesic service areas (buffer + dissolve) + coverage stats.
4. **MAP** - compose a finished layout: Light Gray basemap, country boundary,
   cities, semi-transparent service areas, legend, north arrow, scale bar.
5. **EXPORT** - render to PDF and open it.

Default country is **Nepal** (17 cities, ~99,000 sq km of 50 km coverage). The
finished PDF/aprx land in `demos\_sample\`. **Recording tip:** run it in a
terminal; the PDF pops up at the end as the payoff. (A title text isn't added
programmatically — add one in ArcGIS Pro if you want, or just narrate it.)

## 1. Headless CLI tour — terminal screencast

```bat
powershell -ExecutionPolicy Bypass -File demos\demo_headless.ps1
```

Narrated run of: `info` → `data describe` → `data fields` → `data query`
(cities over 5M) → `gp analysis.Buffer` (50 km) → `data count`. Pure terminal,
JSON in / JSON out. No ArcGIS Pro window required.

**Recording tip:** full-screen the terminal; each step pauses ~2 s so it reads well.

## 2. Live bridge — drive the OPEN ArcGIS Pro (the headline demo)

Prereqs: build + install the add-in (`live-bridge\README.md`), then **open
`demos\_sample\Sample.aprx` in ArcGIS Pro** with a map view active.

```bat
powershell -ExecutionPolicy Bypass -File demos\demo_live_bridge.ps1
```

Posts to the live session: `ping` → `zoom_to` cities → `query` (cities over 5M)
→ `run_gp` 200 km buffer (the buffer **appears in the map**) → `zoom_to` the
buffer. The terminal shows structured JSON; the ArcGIS Pro window shows it happen.

**Recording tip:** put the ArcGIS Pro window and the terminal side by side, so the
viewer sees the JSON command on one side and the map react on the other. The
Topographic basemap makes the world context obvious.

> Once the MCP server is registered (`live-bridge\README.md`), the same five
> operations are available to an agent as `arcgis_ping` / `arcgis_zoom_to` /
> `arcgis_query` / `arcgis_run_gp` — i.e. you can drive this by chatting instead
> of running the script.
