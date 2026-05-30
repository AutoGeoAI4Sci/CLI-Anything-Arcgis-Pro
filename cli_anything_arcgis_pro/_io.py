"""Shared output / error handling for all commands.

Convention: with ``--json`` every command prints exactly one line of JSON:
  success -> {"ok": true,  "data": <result>}
  failure -> {"ok": false, "error": "...", "type": "...", "arcpy_messages": "..."}
Without ``--json`` it prints a human-readable rendering (falling back to pretty JSON).
"""

import functools
import json

import click


def _jsonify(obj):
    return json.dumps(obj, ensure_ascii=False, default=str)


def arcgis_command(human_renderer=None):
    """Decorate a click callback so its return value becomes structured output.

    The wrapped function should simply *return* a JSON-serialisable result (or
    raise). All printing, ``--json`` switching and error capture happens here.
    """

    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            ctx = click.get_current_context()
            as_json = bool(ctx.obj and ctx.obj.get("json"))
            try:
                data = fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - CLI boundary, report everything
                arcpy_msgs = ""
                try:
                    import arcpy

                    arcpy_msgs = arcpy.GetMessages(2)
                except Exception:  # arcpy may not even be imported yet
                    pass
                if as_json:
                    click.echo(
                        _jsonify(
                            {
                                "ok": False,
                                "error": str(exc),
                                "type": type(exc).__name__,
                                "arcpy_messages": arcpy_msgs,
                            }
                        )
                    )
                else:
                    click.secho(f"Error ({type(exc).__name__}): {exc}", fg="red", err=True)
                    if arcpy_msgs:
                        click.secho(arcpy_msgs, fg="yellow", err=True)
                ctx.exit(1)
                return None

            if as_json:
                click.echo(_jsonify({"ok": True, "data": data}))
            elif human_renderer is not None:
                human_renderer(data)
            else:
                click.echo(json.dumps(data, ensure_ascii=False, indent=2, default=str))
            return data

        return wrapper

    return deco
