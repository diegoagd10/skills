"""Typer CLI boundary for the Python SDD migration slice.

Typer owns parsing, help, and dispatch. Commands are registered with explicit
hyphenated names so the Go-compatible ``sdd-status`` / ``sdd-continue`` invocations
are preserved. Both commands share the same resolve/render/exit path through
:func:`_dispatch_command`; the only differences are the renderer (Rich for
``sdd-status`` terminal output, plain markdown for ``sdd-continue`` LLM
consumption) and whether instructions are forced on (yes for ``sdd-continue``,
opt-in for ``sdd-status``).
"""

from __future__ import annotations

from collections.abc import Callable

import typer

from . import compat, rendering
from .sdd import SddError, Status, resolve

app = typer.Typer(
    add_completion=False,
    help="ai-harness SDD helper (Python migration slice: sdd-status, sdd-continue).",
)


@app.callback()
def _main() -> None:
    """Route to a subcommand; preserves group dispatch for hyphenated names."""


def _dispatch_command(
    cwd: str,
    change: str,
    json_output: bool,
    always_instructions: bool,
    instructions_flag: bool,
    renderer: Callable[[Status], str | None],
) -> None:
    """Resolve a Status and route it to JSON or the caller's renderer.

    ``always_instructions`` forces per-phase instructions to be attached to the
    Status regardless of the user-facing ``--instructions`` flag; the flag is
    still accepted (Go-compatible) but ignored when ``always_instructions`` is
    true. Error and usage exits share one path so both commands fail identically.
    """
    include_instructions = always_instructions or instructions_flag
    try:
        status = resolve(cwd, "", change, include_instructions)
    except SddError as err:
        typer.echo(f"ai-harness: {err}", err=True)
        raise typer.Exit(code=compat.EXIT_ERROR) from err
    except OSError as err:
        typer.echo(f"ai-harness: {err}", err=True)
        raise typer.Exit(code=compat.EXIT_ERROR) from err

    if json_output:
        typer.echo(compat.status_to_json(status))
        return

    output = renderer(status)
    if output is not None:
        typer.echo(output)


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
    _dispatch_command(
        cwd=cwd,
        change=change or "",
        json_output=json_output,
        always_instructions=False,
        instructions_flag=instructions,
        renderer=rendering.render_status,
    )


@app.command(name="sdd-continue")
def sdd_continue(
    change: str | None = typer.Argument(
        None, help="Active OpenSpec change name; inferred when omitted."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Emit deterministic JSON instead of dispatcher markdown."
    ),
    instructions: bool = typer.Option(
        False,
        "--instructions",
        help="Accepted for Go-compatibility; instructions are always attached on sdd-continue.",
    ),
    cwd: str = typer.Option("", "--cwd", help="Workspace directory to read openspec/ from."),
) -> None:
    """Report the SDD dispatcher routing for a change.

    Always attaches per-phase instructions (Go-compatible: ``--instructions`` is
    accepted and ignored). Human output is plain markdown targeting LLM
    consumption, not a Rich-rendered terminal.
    """
    _dispatch_command(
        cwd=cwd,
        change=change or "",
        json_output=json_output,
        always_instructions=True,
        instructions_flag=instructions,
        renderer=rendering.render_dispatcher,
    )


def main() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
