## Exploration: python-sdd-continue

### Current State

The `go-to-python` migration (archived under `openspec/changes/archive/2026-06-14-go-to-python/`) ported `sdd-status` to the Python `uv`/`typer`/`rich` stack and explicitly deferred `sdd-continue` to keep the first PR inside the review budget. The Go CLI remains the reference/fallback for `sdd-continue` and all out-of-scope commands.

In the Go implementation, `sdd-continue` is not a separate resolver. `cmd/ai-harness/run.go` dispatches both `sdd-status` and `sdd-continue` to the same `sdd.Resolve` call; the only differences are:

- `sdd-continue` always passes `includeInstructions=true` (equivalent to `sdd-status --instructions`).
- Human (non-JSON) output uses `sdd.RenderDispatcherMarkdown` instead of `sdd.RenderMarkdown`.
- The rendered header is `## Native SDD Dispatcher: <change>` and includes a `### Dependency States` section and `### Next Phase Instructions: <phase>` block when applicable.

The Python side already has the same deep `ai_harness.sdd` module with `resolve(cwd, workspace_root, change_name, include_instructions)`. `compat.status_to_json` already emits the correct ordered JSON with `phaseInstructions` when the `Status` carries them. The only missing pieces are the CLI command registration and the dispatcher-style human renderer.

### Affected Areas

- `cli/src/ai_harness/cli.py` — add `sdd-continue` Typer command, reuse the same flag set, force `include_instructions=True`, route human output to the dispatcher renderer, and update CLI help text.
- `cli/src/ai_harness/rendering.py` — add `render_dispatcher(status)` producing the Go-compatible dispatcher markdown (header, dependency states, next-phase instructions, blocked reasons, JSON block).
- `cli/tests/test_cli.py` — add `sdd-continue` command-name, flag, JSON-always-includes-instructions, and human-output tests.
- `cli/tests/test_json_compat.py` — extend parity matrix to run `sdd-continue --json` against the Go binary (no `--instructions` flag) and assert byte-for-byte equality; the fixtures already cover the state space.
- `cli/tests/conftest.py` — add `run_go_continue` helper mirroring `run_go_status`.
- `cli/tests/test_boundary.py` / `test_verifyreport.py` — no resolver changes expected; existing coverage should remain sufficient.
- `cli/Makefile` — update help text/comments to mention both migrated SDD commands.
- `cli/pyproject.toml` — update description from "sdd-status" to "sdd-status and sdd-continue".
- `openspec/specs/python-sdd-cli/spec.md` — already requires `sdd-continue` compatibility; no new requirements needed, but confirm existing scenarios are satisfied.

### Approaches

1. **Minimal delta: add command + renderer** — register a new Typer command that calls `resolve(..., include_instructions=True)` and selects the dispatcher renderer for human output. Keep the existing `sdd-status` path unchanged.
   - Pros: smallest change, fits easily under 400-line review budget, low regression risk, directly mirrors Go structure.
   - Cons: a second nearly-identical command function duplicates flag definitions; manageable because only two commands exist in the slice.
   - Effort: Low.

2. **Refactor shared command harness first** — extract a private `_run_sdd_command(..., always_instructions, renderer)` helper that both commands call.
   - Pros: removes duplication, makes the "always instructions / renderer choice" decision explicit in one place.
   - Cons: slightly larger diff, refactoring before adding behavior can obscure the parity change in review; current duplication is only two commands.
   - Effort: Low-Medium.

### Recommendation

Take Approach 1 (minimal delta) but avoid copy-pasting the entire command body. Keep the Typer-decorated functions thin: each parses its own flags (required by Typer), then delegates to a small internal `_dispatch_status_command(..., always_instructions: bool, renderer: Callable)` helper that owns the resolve/render/exit logic. This satisfies the coding-guidelines "no pass-through methods" rule while keeping the diff focused on the new command and renderer.

### Risks

- **Human renderer drift**: Go `RenderDispatcherMarkdown` has a specific layout and always ends with a fenced JSON block. The Python renderer must match it for parity tests; any Rich styling must not leak into the markdown string.
- **Flag / positional parity**: Typer must accept exactly the same shape (`sdd-continue [--json] [--instructions] [--cwd PATH] [change]`). `sdd-continue` should accept `--instructions` but ignore it (it is always on), matching Go behavior.
- **Help-text overclaim**: the CLI help currently says "Python migration slice: sdd-status". Update it carefully so it does not imply the installer/uninstaller are migrated.
- **Console-script entry point**: `ai-harness` script already points to `ai_harness.cli:main`; no change needed.
- **Golden / parity tests depend on Go toolchain**: conftest skips parity tests when `go` is missing; the new `sdd-continue` parity tests should do the same.
- **JSON `phaseInstructions` placement**: Go always emits `phaseInstructions` for `sdd-continue`; Python already does this when `status.phase_instructions` is set, so no `compat.py` change is needed.

### Open Product / Behavior Questions

1. Should the Python dispatcher markdown renderer aim for byte-for-byte parity with Go, or only semantic parity? The existing `sdd-status` parity tests assert byte-for-byte JSON equality; for consistency, dispatcher markdown should also match Go output, at least for the tested fixtures.
2. Is `--instructions` accepted (and ignored) on `sdd-continue`, or should Typer reject it? Go accepts the flag silently because the flag set is shared; matching Go means accepting and ignoring it.
3. Do we want a separate `render_dispatcher` test file, or add dispatcher cases to `test_cli.py`? A few cases in `test_cli.py` plus a renderer unit test in `test_boundary.py` or a new `test_rendering.py` is sufficient.

### Ready for Proposal

Yes. The scope is well understood, the Python foundation is already in place, and the migration slice is small. The proposal should name the change `python-sdd-continue`, keep it inside the single-PR delivery model, and include explicit parity tests against the Go binary for both JSON and human output.
