<#
  Demo 1 - Headless CLI tour (great for a terminal screencast).

  Runs a narrated sequence of cli-anything-arcgis-pro commands against the
  self-contained sample geodatabase. No ArcGIS Pro window needed.

  Prereqs:
    1. pip install this package (into any Python - it self-dispatches to ArcGIS Pro)
    2. python demos\setup_sample.py   (creates demos\_sample\sample.gdb)

  Then:  powershell -ExecutionPolicy Bypass -File demos\demo_headless.ps1
#>

$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$gdb = Join-Path $here "_sample\sample.gdb"
$cities = "$gdb\cities"
$buf = "$gdb\cities_buffer"

# Resolve the CLI: prefer the installed command, else ArcGIS Pro's Python -m.
$ProPy = "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
function RunCli {
  if (Get-Command cli-anything-arcgis-pro -ErrorAction SilentlyContinue) {
    & cli-anything-arcgis-pro $args
  } else {
    & $ProPy -m cli_anything_arcgis_pro $args
  }
}

function Step {
  param([string]$desc, [string[]]$cmd)
  Write-Host ""
  Write-Host "  >>> $desc" -ForegroundColor Cyan
  Write-Host "  PS> cli-anything-arcgis-pro $($cmd -join ' ')" -ForegroundColor DarkGray
  Start-Sleep -Milliseconds 900
  $out = RunCli @cmd
  try { ($out | ConvertFrom-Json | ConvertTo-Json -Depth 6) } catch { $out }
  Start-Sleep -Seconds 2
}

Clear-Host
Write-Host "=== CLI-Anything : ArcGIS Pro -- headless CLI demo ===" -ForegroundColor Green

Step "1) Environment and license" @("--json", "info")
Step "2) Describe the cities feature class" @("--json", "data", "describe", $cities)
Step "3) List its fields" @("--json", "data", "fields", $cities)
Step "4) Query: cities with population over 5 million" @("--json", "data", "query", $cities, "--where", "POP > 5000000", "--fields", "NAME,COUNTRY,POP")
Step "5) Geoprocessing: 50 km buffer around every city" @("--json", "gp", "analysis.Buffer", "-a", $cities, "-a", $buf, "--kw", "buffer_distance_or_field=50 Kilometers")
Step "6) Count the buffer polygons that were created" @("--json", "data", "count", $buf)

Write-Host ""
Write-Host "=== Done. Everything ran on the live ArcPy backend, JSON in / JSON out. ===" -ForegroundColor Green
