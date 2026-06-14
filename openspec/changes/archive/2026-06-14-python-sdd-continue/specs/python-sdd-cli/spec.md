# Delta for Python SDD CLI

## MODIFIED Requirements

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
