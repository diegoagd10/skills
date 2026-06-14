"""Typer CLI boundary for the Python SDD migration slice.

Typer owns parsing, help, and dispatch. Commands are registered with explicit
hyphenated names so the Go-compatible ``sdd-status`` invocation is preserved. This
slice ports only ``sdd-status``; every other Go command remains the reference and
fallback during the hybrid migration.
"""

from __future__ import annotations

import typer

from . import compat, rendering
from .sdd import SddError, resolve

app = typer.Typer(
    add_completion=False,
    help="ai-harness SDD helper (Python migration slice: sdd-status).",
)


@app.callback()
def _main() -> None:
    """Route to a subcommand; preserves group dispatch for hyphenated names."""


@app.command(name="sdd-status")
def sdd_status(
    change: str | None = typer.Argument(
        None, help="Active OpenSpec change name; inferred when omitted."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Emit deterministic JSON instead of a rendered summary."
    ),
    instructions: bool = typer.Option(
        False, "--instructions", help="Attach per-phase instructions to the status."
    ),
    cwd: str = typer.Option("", "--cwd", help="Workspace directory to read openspec/ from."),
) -> None:
    """Report the SDD phase state for a change."""
    try:
        status = resolve(cwd, "", change or "", instructions)
    except SddError as err:
        typer.echo(f"ai-harness: {err}", err=True)
        raise typer.Exit(code=compat.EXIT_ERROR) from err
    except OSError as err:
        typer.echo(f"ai-harness: {err}", err=True)
        raise typer.Exit(code=compat.EXIT_ERROR) from err

    if json_output:
        typer.echo(compat.status_to_json(status))
        return

    rendering.render_status(status)


def main() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
