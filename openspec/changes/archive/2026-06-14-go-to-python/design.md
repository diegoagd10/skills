# Design: Go to Python

## Technical Approach

Add a `uv`-managed Python package under `cli/` that ports only `sdd-status` and `sdd-continue`. The existing Go CLI remains the compatibility reference and owner for `install`, `uninstall`, plugin setup, command generation, and config generation. Python owns the migrated SDD command surface for this slice: Typer-based command parsing/help/dispatch, deterministic SDD resolution, Go-compatible JSON, exit-code mapping, and Rich human rendering.

The main boundary is a deep `ai_harness.sdd` module: callers ask for resolved status or dispatcher status; artifact discovery, task parsing, state-machine rules, JSON shape, and verify-report heuristics stay hidden inside.

## Architecture Decisions

| Decision | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| Hybrid ownership | Python dispatch accepts only `sdd-status` and `sdd-continue`; out-of-scope commands are not implemented as migrated behavior. Go remains fallback/reference. | Full port; Python wrapper shelling to Go. | Keeps first PR inside review budget and avoids a shallow Go wrapper while making command ownership explicit. |
| CLI framework | `ai_harness.cli` uses `typer.Typer()` and `@app.command(name="sdd-status")` / `@app.command(name="sdd-continue")` style explicit names where needed. | Hand-rolled `argparse`; implicit Typer name conversion. | Typer owns parsing/help/dispatch while explicit names prevent accidental drift from Go-compatible hyphenated commands. |
| Package boundaries | `ai_harness.cli` owns Typer app, options, dispatch, and exit codes; `ai_harness.sdd` resolves state; `ai_harness.rendering` formats human output; `ai_harness.compat` owns JSON schema/goldens. | Many per-step modules; one large CLI file. | Boundaries hide real knowledge: CLI protocol, SDD state rules, terminal rendering, and compatibility fixtures. |
| JSON contract | Use dataclasses/typed dict builders that emit explicit keys in Go order with non-null empty lists. | Serialize arbitrary objects; hand-build JSON in commands. | Prevents schema drift and keeps JSON knowledge in one owner. |
| Rich boundary | `rich` only in human renderers; JSON uses `json.dumps(..., indent=2)` to stdout. | Rich console for all output. | Satisfies deterministic `--json` and avoids terminal-control leakage. |
| Tooling | `cli/pyproject.toml` with uv, pytest, coverage, ruff, typer, rich, console script `ai-harness`. | Keep Go Makefile only. | Establishes Python foundation without changing non-SDD behavior. |

## Data Flow

```text
argv -> Typer app (ai_harness.cli) -> ai_harness.sdd.resolve()
                         -> Status model -> JSON renderer -> stdout
                                      `--> Rich/markdown renderer -> stdout
errors/parse failures -> stderr + Go-compatible exit code
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `cli/pyproject.toml` | Create | uv project metadata, Typer/Rich dependencies, console script, pytest/coverage/ruff config. |
| `cli/src/ai_harness/__init__.py` | Create | Package marker. |
| `cli/src/ai_harness/cli.py` | Create | Typer app, explicit compatible command names, flags/options/help, dispatch, stdout/stderr, exit codes. |
| `cli/src/ai_harness/sdd/` | Create | Workspace resolution, artifact discovery, task parsing, state machine, verify report heuristics. |
| `cli/src/ai_harness/rendering.py` | Create | Human output using rich without affecting JSON. |
| `cli/src/ai_harness/compat.py` | Create | Schema constants, ordered payload construction, exit-code constants. |
| `cli/tests/` | Create | pytest unit/parity tests and fixtures. |
| `cli/Makefile` | Modify | Add/wire `uv run pytest`, `uv run coverage run -m pytest && uv run coverage report`, `uv run ruff check`, `uv run ruff format`. |
| `cli/internal/sdd/*.go` | Reference | Source of Go-observed behavior; not removed. |

## Interfaces / Contracts

```python
app = typer.Typer(...)
def main(argv: Sequence[str] | None = None) -> int: ...
def resolve(cwd: Path | None, change: str | None, include_instructions: bool) -> Status: ...
def status_to_json(status: Status) -> str: ...  # plain deterministic JSON
```

Supported commands: `ai-harness sdd-status [--json] [--instructions] [--cwd PATH] [change]` and `ai-harness sdd-continue [--json] [--instructions] [--cwd PATH] [change]`. Typer owns parsing and help, with explicit command names preserving hyphenated Go compatibility. Parse errors return `2`; resolution/serialization failures return `1`; valid blocked SDD states return `0`, matching current Go behavior.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Artifact classification, active-change selection, task progress, state machine, verify heuristic. | Port Go test cases to pytest temp-dir fixtures. |
| Parity | Typer command names/flags/help, JSON key order/values, empty arrays vs null, blocked reasons, markdown/rich smoke, parse errors and exit codes. | Generate observed Go golden outputs for representative fixtures; compare Python output exactly for JSON and exit code. |
| Integration | Console script invocation for both commands and `--cwd`. | `uv run pytest` subprocess tests. |
| Quality | Formatting/lint/coverage. | `uv run ruff check`, `uv run ruff format --check`, `uv run coverage run -m pytest && uv run coverage report`. |

## Migration / Rollout

No data migration required. Roll out as a temporary hybrid: Python owns only the two migrated SDD commands in this PR; Go remains available as reference/fallback for all other behavior. Installer, uninstaller, plugin setup, command generation, and config generation are explicitly out of scope.

## Implementation Risks and Mitigations

- JSON drift: centralize schema construction and assert golden outputs.
- Exit-code drift: test CLI subprocess results for parse, filesystem error, and blocked-but-valid states.
- Hybrid ambiguity: document command ownership in CLI help/Makefile comments without claiming installer migration.
- Typer command-name drift: register explicit hyphenated command names and test both migrated invocations.
- Rich leakage: keep renderers separate and test `--json` bytes contain parseable JSON only.

## Open Questions

None.
