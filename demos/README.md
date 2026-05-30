# Demos

Two short, self-contained demos — good for screen recordings. Both build their
own sample data (world cities), so anyone with ArcGIS Pro can reproduce them.

## 0. Build the sample data (once)

```bat
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" demos\setup_sample.py
```

Creates under `demos\_sample\`:
- `sample.gdb\cities` — 7 world cities (NAME, COUNTRY, POP).
- `Sample.aprx` — a project with a **Topographic basemap** + the cities layer,
  so the data shows on a recognizable world map (not a blank canvas).

`demos\_sample\` is git-ignored (regenerate it anytime).

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
