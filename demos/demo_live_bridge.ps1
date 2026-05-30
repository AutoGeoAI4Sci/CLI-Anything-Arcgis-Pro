<#
  Demo 2 - Drive the LIVE ArcGIS Pro session (the headline demo for video).

  With ArcGIS Pro open on demos\_sample\Sample.aprx and the ProSimpleMapExport
  add-in installed (bridge listening on 127.0.0.1:5005), this posts commands to
  the live project: read state, zoom to the cities, query attributes, and run a
  geoprocessing buffer whose output appears in the map - all while you watch.

  Prereqs:
    1. python demos\setup_sample.py            (creates demos\_sample\Sample.aprx)
    2. Build + install live-bridge\ProSimpleMapExport (see live-bridge\README.md)
    3. Open demos\_sample\Sample.aprx in ArcGIS Pro, with a MAP view active.

  Then:  powershell -ExecutionPolicy Bypass -File demos\demo_live_bridge.ps1
#>

$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$Bridge = "http://127.0.0.1:5005/"
$Layer = "cities"
$citiesPath = Join-Path $here "_sample\sample.gdb\cities"
$bufPath = Join-Path $here "_sample\sample.gdb\cities_buffer_live"

function Send {
  param([string]$desc, [hashtable]$cmd)
  Write-Host ""
  Write-Host "  >>> $desc" -ForegroundColor Cyan
  $body = $cmd | ConvertTo-Json -Compress -Depth 6
  Write-Host "  POST $body" -ForegroundColor DarkGray
  Start-Sleep -Milliseconds 900
  $r = Invoke-RestMethod -Uri $Bridge -Method Post -Body $body -ContentType "application/json"
  Write-Host ($r | ConvertTo-Json -Depth 6)
  Start-Sleep -Seconds 2
}

# fail fast if the bridge isn't up
if (-not (Test-NetConnection 127.0.0.1 -Port 5005 -WarningAction SilentlyContinue).TcpTestSucceeded) {
  Write-Host "Bridge not reachable on 127.0.0.1:5005." -ForegroundColor Red
  Write-Host "Open Sample.aprx in ArcGIS Pro with the add-in installed, then retry." -ForegroundColor Red
  exit 1
}

Clear-Host
Write-Host "=== CLI-Anything : ArcGIS Pro -- LIVE bridge demo ===" -ForegroundColor Green
Write-Host "Watch the ArcGIS Pro window as each command runs." -ForegroundColor Yellow

Send "1) Ping the live session - what project is open?" @{ command = "ping" }
Send "2) Zoom the map to the cities layer" @{ command = "zoom_to"; layer = $Layer }
Send "3) Query cities with population over 5 million" @{ command = "query"; layer = $Layer; where = "POP > 5000000"; limit = 10 }
Send "4) Geoprocessing: 200 km buffer - watch it appear in the map" @{ command = "run_gp"; tool = "analysis.Buffer"; params = @($citiesPath, $bufPath, "200 Kilometers") }
Send "5) Zoom out to the new buffer layer" @{ command = "zoom_to"; layer = "cities_buffer_live" }

Write-Host ""
Write-Host "=== Done. An agent just drove the open ArcGIS Pro project end to end. ===" -ForegroundColor Green
