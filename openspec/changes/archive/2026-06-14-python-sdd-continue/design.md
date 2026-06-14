# Design: Python sdd-continue

## Technical Approach

Register a thin Typer `sdd-continue` command that forces `include_instructions=True`, then delegates resolve/render/exit through a shared `_dispatch_command` helper (extracted from `sdd_status`). Human output routes to a new `render_dispatcher(status)` producing Go-compatible plain markdown; JSON output reuses existing `compat.status_to_json()`. Zero changes to SDD resolution, JSON serialization, or the existing `sdd-status` path.

## Architecture Decisions

| Decision | Choice | Alternatives rejected | Rationale |
|----------|--------|-----------------------|-----------|
| Command+dispatch structure | Thin Typer command → `_dispatch_command(always_instructions=True, renderer=render_dispatcher)` | Copy-paste entire `sdd_status` body; separate module for dispatch | Extracted helper hides the "resolve/render/exit" ritual behind one call site per command, avoids duplication without adding a shallow pass-through module. Two commands only — no classitis. |
| Dispatcher markdown | Plain `str` from `render_dispatcher(status)`, no Rich | Rich Table like `sdd-status`; separate MarkdownRenderer class | Go's `RenderDispatcherMarkdown` emits plain text targeting LLM consumption. Rich styling would break parity tests and leak terminal concepts into LLM context. |
| `--instructions` flag on sdd-continue | Accepted and ignored (Go-compatible) | Reject it as unknown | Go binary accepts `--instructions` silently because flag set is shared. Rejecting would break existing scripts/commands that pass it. |
| Renderer location | `rendering.py` alongside `render_status` | New `dispatcher.py` module | One rendering boundary with two renderers is a deep module (same knowledge domain — Status → markdown). Splitting would create two shallow modules sharing the Status type. |
| Parity tests | Add `run_go_continue` helper; extend `PARITY_FIXTURES` loop to `sdd-continue --json` | New test file; manual-only parity | Same fixture set exercises the same Status shape; the Go binary's `sdd-continue --json` output is byte-identical to `sdd-status --json --instructions`. Parity test invokes both commands and asserts equality. |

## Data Flow

```
CLI args → Typer (parse flags, force instructions=True)
              │
              ▼
     _dispatch_command(always_instructions=True, renderer=render_dispatcher)
              │
              ├─ resolve(cwd, workspace_root, change, include_instructions=True) → Status
              │
              ├─ --json? → compat.status_to_json(status) → stdout (exit 0)
              │
              └─ human?  → render_dispatcher(status) → stdout (exit 0)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `cli/src/ai_harness/cli.py` | Modify | Extract `_dispatch_command` from `sdd_status`; add `sdd-continue` command; update app help text |
| `cli/src/ai_harness/rendering.py` | Modify | Add `render_dispatcher(status)` producing Go-compatible dispatcher markdown |
| `cli/tests/test_cli.py` | Modify | Add `sdd-continue` name/flag/JSON-always-instructions/human tests |
| `cli/tests/test_json_compat.py` | Modify | Extend parity loop to `sdd-continue --json` |
| `cli/tests/conftest.py` | Modify | Add `run_go_continue` helper |
| `cli/pyproject.toml` | Modify | Description: "sdd-status and sdd-continue" |
| `cli/Makefile` | Modify | Update help text |

## Interfaces / Contracts

`render_dispatcher(status: Status) -> str` contract — must produce output matching Go's `RenderDispatcherMarkdown`:

```
## Native SDD Dispatcher: {change_name}

Native status is authoritative. Route by next_recommended and dependency state, not by prompt inference.

next_recommended: {status.next_recommended}

### Dependency States
- proposal: {deps.proposal}
- specs: {deps.specs}
- design: {deps.design}
- tasks: {deps.tasks}
- apply: {deps.apply}
- verify: {deps.verify}
- archive: {deps.archive}
- task_progress: {completed}/{total} complete

### Blocked Reasons        ← only when blocked_reasons non-empty
- {reason}

### Next Phase Instructions: {phase}  ← only when next_recommended ∈ {apply,verify,archive}
- {instruction per line}

### JSON
```json
{status JSON via compat.status_to_json}
```
```

The CLI internal helper signature:

```python
def _dispatch_command(
    cwd: str, change: str | None, json_output: bool,
    always_instructions: bool, instructions_flag: bool,
    renderer: Callable[[Status], None],
) -> None:
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit (CLI) | Command name `sdd-continue` registered; `--instructions` accepted; JSON always includes `phaseInstructions`; human output contains dispatcher header | `CliRunner` invoke, assert on stdout/exit code |
| Unit (rendering) | Dispatcher markdown contains all required sections; blocked reasons conditional; next-phase instructions conditional; fenced JSON block present | Direct call to `render_dispatcher(status)` on seeded Status |
| Integration (parity) | `sdd-continue --json` byte-for-byte matches Go binary across all 7 fixtures | Extend `test_json_matches_go_binary` parametrize with `command=["sdd-status","sdd-continue"]`; Python JSON from resolve → Go JSON from `run_go_continue` |

## Migration / Rollout

No migration required. Python `sdd-continue` is additive; Go binary remains available as fallback.

## Open Questions

None — all behavior decisions resolved in exploration and confirmed by Go reference code.
