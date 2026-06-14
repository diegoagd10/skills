# Python SDD CLI Specification

## Purpose

Define the first Python migration slice for `ai-harness`: a temporary hybrid Go/Python CLI foundation that ports only `sdd-status` and `sdd-continue` while preserving observable behavior.

## Requirements

### Requirement: Temporary Hybrid Migration Boundary

The system MUST allow the Python CLI foundation to coexist with the existing Go implementation during the migration. The first slice MUST NOT port installer, uninstaller, plugin setup, command generation, or config generation behavior.

#### Scenario: First slice excludes installer behavior

- GIVEN the Python migration slice is being delivered
- WHEN a user invokes installer, uninstaller, plugin setup, command generation, or config generation behavior through the Python scope
- THEN the system MUST NOT claim those behaviors are migrated in this slice

#### Scenario: Go remains available as fallback

- GIVEN a behavior is outside `sdd-status` or `sdd-continue`
- WHEN the first Python slice is installed or tested
- THEN the existing Go implementation SHALL remain the compatibility reference

### Requirement: Python Tooling Foundation

The system MUST provide a `uv`-managed Python foundation under `cli/` with `pytest`, coverage reporting, `ruff`, `typer`, and `rich` available for the migrated SDD commands.

#### Scenario: Quality commands are available

- GIVEN the Python CLI foundation exists
- WHEN maintainers run Python checks
- THEN `uv run pytest`, coverage reporting, `uv run ruff check`, and `uv run ruff format` MUST be supported

#### Scenario: Coverage uses test coverage tooling

- GIVEN maintainers request coverage for the Python migration
- WHEN coverage is executed
- THEN coverage MUST be produced by pytest/coverage tooling, not by `ruff` lint rules

### Requirement: Command Surface Compatibility

The system MUST use Typer for Python CLI command parsing, command tree, options/flags, help, and dispatch. The system MUST preserve the command names and supported invocation shape for `sdd-status` and `sdd-continue`, including compatible flags such as `--json`.

#### Scenario: Status command remains compatible

- GIVEN a user previously invoked `ai-harness sdd-status` with supported flags
- WHEN the same invocation targets the Python CLI slice
- THEN the command name, accepted flags, and meaning of each flag MUST remain compatible

#### Scenario: Typer preserves hyphenated command names

- GIVEN the Python CLI uses Typer command registration
- WHEN `sdd-status` or `sdd-continue` is registered
- THEN the implementation MUST prefer explicit Typer command names where needed so the Go-compatible hyphenated command names remain accepted

#### Scenario: Unsupported scope is not silently changed

- GIVEN a user invokes a command outside `sdd-status` and `sdd-continue`
- WHEN the first Python slice handles command dispatch
- THEN it MUST NOT change the observable contract for that command in this PR

### Requirement: SDD Status Compatibility

The system MUST preserve `sdd-status` behavior for OpenSpec artifact discovery, active-change state resolution, output semantics, file paths, and exit codes.

#### Scenario: Status reports compatible state

- GIVEN an OpenSpec change with proposal, specs, design, tasks, or verification artifacts
- WHEN `sdd-status` runs
- THEN it MUST classify artifacts and recommend the next state using the Go-observed semantics

#### Scenario: Status preserves invalid-state exits

- GIVEN required OpenSpec state is missing, invalid, or inconsistent
- WHEN `sdd-status` runs
- THEN it MUST return the Go-observed exit code for that state

### Requirement: SDD Continue Compatibility

The system MUST preserve `sdd-continue` routing behavior, including blocker detection, next recommended phase, file paths, and exit codes.

#### Scenario: Continue resolves the next phase

- GIVEN an OpenSpec change has partial or complete SDD artifacts
- WHEN `sdd-continue` runs
- THEN it MUST produce the same next recommended phase and blockers as the existing behavior

#### Scenario: Continue preserves missing-artifact handling

- GIVEN required specs, design, or tasks are missing for the current state
- WHEN `sdd-continue` runs
- THEN it MUST report blockers and exit with the Go-observed code

### Requirement: Deterministic JSON and Human Rendering Boundary

The system MUST keep `--json` output as deterministic plain JSON with stable schema, field names, ordering expectations, null/empty values, and semantics. The system MAY use Rich only for human-readable terminal rendering.

#### Scenario: JSON is stable

- GIVEN a user passes `--json` to `sdd-status` or `sdd-continue`
- WHEN the command emits output
- THEN the output MUST be parseable plain JSON without `rich` styling or terminal control sequences
- AND JSON emission MUST NOT depend on Rich formatting APIs

#### Scenario: Human output may be rich-rendered

- GIVEN a user runs `sdd-status` or `sdd-continue` without `--json`
- WHEN the command emits human-readable output
- THEN `rich` MAY format the display without changing computed SDD state
