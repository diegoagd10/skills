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

The system MUST preserve `sdd-continue` routing behavior: blocker detection, next recommended phase, file paths, and exit codes. The system MUST force `include_instructions=True` regardless of `--instructions` flag (accepted, always on). Human output MUST route through `render_dispatcher` producing plain markdown with dispatcher header, dependency states, next-phase instructions, and a fenced JSON block. JSON output MUST reuse `compat.status_to_json()`.

(Previously: requirement existed without explicit CLI flag contract, rendering destination, or blocked-state instructions format.)

#### Scenario: Continue resolves the next phase

- GIVEN an OpenSpec change has partial or complete SDD artifacts
- WHEN `sdd-continue` runs
- THEN it MUST produce the same next recommended phase and blockers as Go `sdd-continue`

#### Scenario: Continue preserves missing-artifact handling

- GIVEN required specs, design, or tasks are missing for the current state
- WHEN `sdd-continue` runs
- THEN it MUST report blockers and exit with the Go-observed exit code

#### Scenario: JSON always includes phaseInstructions regardless of flag

- GIVEN `sdd-continue --json` is invoked with or without `--instructions`
- WHEN the command emits JSON
- THEN `include_instructions` MUST be `true` and the JSON output MUST include a `phaseInstructions` field

#### Scenario: Dispatcher human output is plain markdown

- GIVEN `sdd-continue` is invoked without `--json`
- WHEN the command emits human-readable output
- THEN the output MUST be plain markdown from `render_dispatcher(status)` containing dispatcher header, dependency state lines, next-phase instructions, and fenced JSON block — without Rich styling

#### Scenario: Blocked state output includes explicit next-step instructions

- GIVEN an SDD change is in a blocked state (missing required artifacts)
- WHEN `sdd-continue` runs
- THEN the output MUST identify which artifacts are missing and which phase the user SHALL run next

### Requirement: Deterministic JSON and Human Rendering Boundary

The system MUST keep `--json` output as deterministic plain JSON with stable schema, field names, ordering, null/empty values, and semantics. For `sdd-status`, the system MAY use Rich for human-readable terminal rendering. For `sdd-continue`, human output MUST be plain markdown via `render_dispatcher` — Rich styling SHALL NOT be used because the dispatcher output targets LLM consumption, not terminal display.

(Previously: requirement allowed Rich for human output universally; did not distinguish `sdd-continue` dispatcher rendering constraints.)

#### Scenario: JSON is stable

- GIVEN a user passes `--json` to `sdd-status` or `sdd-continue`
- WHEN the command emits output
- THEN the output MUST be parseable plain JSON without Rich styling or terminal control sequences

#### Scenario: Sdd-continue human output excludes Rich

- GIVEN a user runs `sdd-continue` without `--json`
- WHEN the command emits human-readable output
- THEN the output MUST NOT contain Rich markup, ANSI escape sequences, or terminal styling
