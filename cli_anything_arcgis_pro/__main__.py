"""Entry point: ``python -m arcgis_cli`` (run inside ArcGIS Pro's arcgispro-py3)."""

import sys

# ArcPy emits localised messages; force UTF-8 stdout so JSON is consistent for agents
# regardless of the Windows console code page (e.g. GBK).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import click

from . import __version__
from .cmd_batch import batch_group
from .cmd_data import data_group
from .cmd_gp import gp_cmd
from .cmd_info import info_cmd
from .cmd_layout import layout_group
from .cmd_project import project_group


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="arcgis-cli")
@click.option("--json", "as_json", is_flag=True, help="Emit structured JSON (recommended for agents).")
@click.pass_context
def cli(ctx, as_json):
    """Agent-friendly CLI over ArcGIS Pro / ArcPy.

    Put --json BEFORE the subcommand: `arcgis-cli --json layout list project.aprx`.
    The `layout` group (professional export + map series) is the ArcGIS Pro edge over QGIS.
    """
    ctx.ensure_object(dict)
    ctx.obj["json"] = as_json


cli.add_command(info_cmd)
cli.add_command(project_group)
cli.add_command(layout_group)
cli.add_command(data_group)
cli.add_command(gp_cmd)
cli.add_command(batch_group)


if __name__ == "__main__":
    cli()
