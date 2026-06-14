# Proposal: Python sdd-continue Migration

## Intent

Deliver the deferred `sdd-continue` Python port so the Go binary can be removed for SDD commands. The Python foundation (`resolve`, `compat`, `rendering`) is already in place; this change registers the Typer command and adds dispatcher human rendering.

## Scope

### In Scope
- Register `sdd-continue` Typer command with Go-compatible flags and exit codes
- Implement `render_dispatcher(status)` producing Go-compatible markdown (dispatcher header, dependency states, next-phase instructions, fenced JSON block)
- Add CLI tests for `sdd-continue` (command name, flags, JSON always includes instructions, human output)
- Extend JSON parity matrix for `sdd-continue --json` against Go binary (byte-for-byte)
- Add `run_go_continue` helper in conftest (mirrors `run_go_status`)

### Out of Scope
- Other Go commands (installer, uninstaller, plugin setup)
- Documentation changes (already handled elsewhere)
- Refactoring `sdd-status` command — keep its path unchanged

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `python-sdd-cli`: delivering the deferred `sdd-continue` command registration and dispatcher rendering. The spec already requires this under `Requirement: SDD Continue Compatibility`; no new spec-level requirements.

## Approach

**Minimal delta** (Approach 1 from exploration): register a thin Typer-decorated `sdd_continue()` that parses its own flags then delegates to a small internal `_dispatch_command(...)` helper owning the resolve/render/exit path. This avoids copy-pasting the command body while keeping the diff focused.

Key design decisions:
- `sdd-continue` forces `include_instructions=True` and ignores `--instructions` flag (Go-compatible: flag accepted, always on)
- Human output routes to `render_dispatcher()` (new); JSON output reuses `compat.status_to_json()` (existing)
- `render_dispatcher()` emits plain markdown — no Rich styling, consistent with `sdd-status` JSON/human boundary

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `cli/src/ai_harness/cli.py` | Modified | Add `sdd-continue` command + `_dispatch_command` helper |
| `cli/src/ai_harness/rendering.py` | Modified | Add `render_dispatcher(status)` |
| `cli/tests/test_cli.py` | Modified | Add `sdd-continue` command and output tests |
| `cli/tests/test_json_compat.py` | Modified | Extend parity matrix for `sdd-continue --json` |
| `cli/tests/conftest.py` | Modified | Add `run_go_continue` helper |
| `cli/pyproject.toml` | Modified | Update description: "sdd-status and sdd-continue" |
| `cli/Makefile` | Modified | Update help text/comments |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Dispatcher markdown drift from Go reference | Medium | Byte-for-byte parity tests against Go binary for known fixtures |
| Typer flag shape mismatch | Low | Explicit flag mapping; `--instructions` accepted and ignored (Go behavior) |
| Rich styling leaks into markdown | Low | `render_dispatcher` returns plain str; no Console involved |
| Parity tests fail when Go toolchain missing | Low | Conftest skips parity when `go` is absent (existing pattern) |

## Rollback Plan

Revert to Go binary for `sdd-continue`. No data migration; the Python command is additive and shares zero state with Go.

## Dependencies

- Go binary available for parity tests (optional — tests skip gracefully)
- Existing `ai_harness.sdd.resolve(include_instructions=True)` foundation (already shipped)

## Success Criteria

- [ ] `sdd-continue --json` produces byte-for-byte identical output to Go `sdd-continue --json` for all fixture states
- [ ] `sdd-continue` (human) produces dispatcher markdown matching Go layout
- [ ] `sdd-continue` exit codes match Go for all states (success, error, blocked)
- [ ] `sdd-status` path unchanged — all existing tests pass
- [ ] Review diff under 400 lines
