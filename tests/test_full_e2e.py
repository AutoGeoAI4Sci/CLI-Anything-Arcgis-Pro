"""End-to-end tests — require a licensed ArcGIS Pro (ArcPy) install.

Skipped automatically when ArcPy is unavailable, so the suite still passes in CI
without a backend. Run these with ArcGIS Pro's `arcgispro-py3` Python.
"""

import importlib.util
import json

import pytest
from click.testing import CliRunner

from cli_anything_arcgis_pro.__main__ import cli

arcpy_available = importlib.util.find_spec("arcpy") is not None
requires_arcpy = pytest.mark.skipif(
    not arcpy_available, reason="ArcGIS Pro / ArcPy not available"
)


@requires_arcpy
def test_info_reports_license_and_version():
    result = CliRunner().invoke(cli, ["--json", "info"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["ok"] is True
    data = payload["data"]
    assert "arcpy_version" in data
    assert "product_license" in data
    assert "extensions" in data


@requires_arcpy
def test_bad_dataset_returns_structured_error():
    result = CliRunner().invoke(
        cli, ["--json", "data", "describe", r"C:\does\not\exist.gdb\nope"]
    )
    payload = json.loads(result.output)
    assert payload["ok"] is False
    assert "error" in payload
