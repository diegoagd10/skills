"""Human-readable rendering for the SDD commands.

Rich lives only here: it formats the terminal display and never participates in
the deterministic ``--json`` path (see :mod:`ai_harness.compat`). Rendering reads
an already-resolved Status and computes no SDD state.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .sdd import Status

UNRESOLVED_CHANGE = "unresolved"


def render_status(status: Status, console: Console | None = None) -> None:
    """Render a status summary for sdd-status to the terminal using Rich."""
    console = console or Console()
    change = status.change_name if status.change_name is not None else UNRESOLVED_CHANGE

    console.print(f"[bold]SDD Status:[/bold] {change}")
    console.print(f"schema: {status.schema_name}@{status.schema_version}")
    console.print(f"store: {status.artifact_store}")
    console.print(f"planning_home: {status.planning_home.path}")
    console.print(f"next: {status.next_recommended}")

    table = Table(title="Summary", show_header=True, header_style="bold")
    table.add_column("phase")
    table.add_column("state")
    table.add_row("apply", status.dependencies.apply)
    table.add_row("verify", status.dependencies.verify)
    table.add_row("archive", status.dependencies.archive)
    table.add_row(
        "tasks",
        f"{status.task_progress.completed}/{status.task_progress.total} complete",
    )
    console.print(table)

    if status.blocked_reasons:
        console.print("[bold]Blocked Reasons[/bold]")
        for reason in status.blocked_reasons:
            console.print(f"- {reason}")
