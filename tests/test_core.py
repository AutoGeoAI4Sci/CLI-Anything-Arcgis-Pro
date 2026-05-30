"""Core tests — pass WITHOUT an ArcGIS Pro / ArcPy backend.

These exercise the CLI wiring (command tree, help, option parsing). ArcPy is
imported lazily inside command bodies, so loading the modules needs no backend.
"""

from click.testing import CliRunner

from cli_anything_arcgis_pro.__main__ import cli

EXPECTED_COMMANDS = ["info", "project", "layout", "data", "gp", "batch"]


def test_root_help():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Agent-friendly CLI over ArcGIS Pro" in result.output


def test_all_subcommands_present():
    result = CliRunner().invoke(cli, ["--help"])
    for cmd in EXPECTED_COMMANDS:
        assert cmd in result.output, f"missing command: {cmd}"


def test_json_is_group_level_flag():
    # --json belongs to the group, before the subcommand
    result = CliRunner().invoke(cli, ["--help"])
    assert "--json" in result.output


def test_layout_group_help():
    result = CliRunner().invoke(cli, ["layout", "--help"])
    assert result.exit_code == 0
    for sub in ["list", "export", "mapseries"]:
        assert sub in result.output


def test_gp_help_mentions_kw():
    result = CliRunner().invoke(cli, ["gp", "--help"])
    assert result.exit_code == 0
    assert "--kw" in result.output


def test_version():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
