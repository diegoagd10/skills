# Tasks: Go to Python

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 550-750 |
| 400-line budget risk | High |
| 800-line budget risk | Low |
| Size exception needed | No |
| Suggested work units | Foundation; `sdd-status` parity; quality gates |
| Delivery strategy | single-pr |
| Size exception | No |

Decision needed before apply: No
Maintainer-approved size exception: No
400-line budget risk: High
800-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Delivery | Notes |
|------|------|----------|-------|
| 1 | Python uv/tooling foundation | single PR | Enables pytest, coverage, ruff, Typer/Rich |
| 2 | `sdd-status` compatibility | single PR | Golden/parity tests included |
| 3 | Verification and docs | single PR | Confirms hybrid scope and gates |

## Deferral: `sdd-continue`

- Defer Python `sdd-continue` tests and implementation to follow-up `sdd-continue` PR/change to keep this PR under the 800-line budget.
- Preserve the hybrid compatibility contract: Go remains the reference/fallback for `sdd-continue` and all out-of-scope commands in this PR.

## Phase 1: Foundation / Tooling

- [x] 1.1 RED: Add failing tooling checks proving `cli/pyproject.toml` supports `uv run pytest`, coverage, `ruff check`, and `ruff format --check`.
- [x] 1.2 GREEN: Create `cli/pyproject.toml` with uv metadata, Typer/Rich dependencies, pytest/coverage config, Ruff config, and `ai-harness` console script.
- [x] 1.3 GREEN: Update `cli/Makefile` with Python test, coverage, lint, and format targets without claiming installer or `sdd-continue` migration.

## Phase 2: RED `sdd-status` Compatibility Tests

- [x] 2.1 Add failing CLI tests under `cli/tests/` for Typer command name `sdd-status`, flags `--json`, `--instructions`, `--cwd`, and optional `change`.
- [x] 2.2 Add failing golden tests for `sdd-status` JSON schema, key order, empty arrays/nulls, file paths, blockers, and exit codes.
- [x] 2.3 Add failing resolver tests for `sdd-status` artifact discovery, active-change selection, task progress, state transitions, and verify-report heuristics.
- [x] 2.4 Add failing boundary tests proving Rich is absent from `sdd-status --json` and only used for human-readable rendering.

## Phase 3: GREEN `sdd-status` Implementation

- [x] 3.1 Create `cli/src/ai_harness/__init__.py` and `cli/src/ai_harness/cli.py` with Typer app and explicit `sdd-status` command registration.
- [x] 3.2 Create `cli/src/ai_harness/sdd/` with workspace resolution, artifact discovery, task parsing, status state, blockers, and next-phase recommendation logic.
- [x] 3.3 Create `cli/src/ai_harness/compat.py` with exit-code constants and deterministic ordered JSON payload builders for `sdd-status`.
- [x] 3.4 Create `cli/src/ai_harness/rendering.py` with Rich human rendering while keeping JSON serialization in plain `json.dumps`.

## Phase 4: REFACTOR / Verification

- [x] 4.1 REFACTOR: Keep CLI parsing, SDD resolution, JSON compatibility, and rendering as deep modules with one hidden decision each.
- [x] 4.2 TRIANGULATE: Cover at least one complete, one partial, and one invalid/missing-artifact OpenSpec fixture for `sdd-status`.
- [x] 4.3 Run targeted pytest during TDD, then full `uv run pytest`, coverage report, `uv run ruff check`, and `uv run ruff format --check`.
