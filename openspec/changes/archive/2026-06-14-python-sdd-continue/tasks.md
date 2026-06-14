# Tasks: Python sdd-continue Migration

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~200 (5 files modified, no new files) |
| 400-line budget risk | Low |
| Size exception needed | No |
| Suggested work units | Not needed |
| Delivery strategy | exception-ok |
| Size exception | No |

Decision needed before apply: No
Maintainer-approved size exception: Yes
400-line budget risk: Low

## Phase 1: Infrastructure (RED prep)

- [x] 1.1 Add `run_go_continue(go_cli, root, *args)` helper in `cli/tests/conftest.py` (mirrors `run_go_status` but invokes `sdd-continue` subcommand)
- [x] 1.2 Extend `cli/tests/test_json_compat.py` parametrize to `command=["sdd-status","sdd-continue"]`; call `run_go_continue` when `command=="sdd-continue"`

## Phase 2: RED — Write failing tests (no sdd-continue implementation yet)

- [x] 2.1 `test_cli.py`: test `sdd-continue` command name is registered and hyphenated (invoke app, assert exit_code 0, assert JSON `schemaName` present)
- [x] 2.2 `test_cli.py`: test `sdd-continue --json` always emits `phaseInstructions` regardless of `--instructions` flag presence
- [x] 2.3 `test_cli.py`: test `sdd-continue --instructions` flag is accepted (exit 0) and ignored (same JSON as without)
- [x] 2.4 `test_cli.py`: test `sdd-continue` (human) stdout contains "## Native SDD Dispatcher" header and fenced JSON block
- [x] 2.5 `test_cli.py`: test `sdd-continue` blocked state exits 0 and reports missing artifacts in output
- [x] 2.6 `test_cli.py` or `test_rendering.py`: test `render_dispatcher(status)` returns plain str with all sections; blocked reasons conditional; next-phase instructions conditional

## Phase 3: GREEN — Implement

- [x] 3.1 Add `render_dispatcher(status: Status) -> str` in `cli/src/ai_harness/rendering.py`: plain markdown with dispatcher header, dependency states, blocked reasons (conditional), next-phase instructions (conditional), fenced JSON block via `compat.status_to_json`
- [x] 3.2 Extract `_dispatch_command(cwd, change, json_output, always_instructions, instructions_flag, renderer)` from `sdd_status` body in `cli/src/ai_harness/cli.py`; route errors to `typer.echo`/`typer.Exit`; rewire `sdd_status` to call it
- [x] 3.3 Register `sdd-continue` Typer command in `cli.py`: calls `_dispatch_command(always_instructions=True, renderer=render_dispatcher)`, accepts `--instructions` flag (ignored)
- [x] 3.4 Verify all Phase 2 tests pass (RED→GREEN gate)

## Phase 4: REFACTOR / Verify

- [x] 4.1 Run full `pytest` suite; confirm all existing `sdd-status` tests still pass (no regression)
- [x] 4.2 Run `pytest -k "parity" --run-go` to verify `sdd-continue --json` byte-for-byte matches Go binary across all 7 fixtures
- [x] 4.3 Run `ruff check` and `ruff format --check`; fix any violations
