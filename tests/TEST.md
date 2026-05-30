# Tests

- **`test_core.py`** — no backend required. Exercises the command tree, help
  text, and option wiring via Click's `CliRunner`. Runs in any environment with
  `click` + `pytest`.
- **`test_full_e2e.py`** — requires a licensed ArcGIS Pro (ArcPy). Auto-skips
  when ArcPy is absent. Run with ArcGIS Pro's bundled Python.

## Run

```bat
:: core only (no ArcGIS Pro needed)
python -m pytest tests/test_core.py

:: full suite with ArcGIS Pro's Python (runs e2e too)
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" -m pytest tests/
```
