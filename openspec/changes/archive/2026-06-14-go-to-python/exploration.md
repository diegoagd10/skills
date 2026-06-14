## Exploration: Go to Python migration

### Current State
`ai-harness` is a Go CLI under `cli/` with a thin `main.go` that delegates to `Run()` in `cli/cmd/ai-harness/run.go`. The command surface is `sdd-status`, `sdd-continue`, `install`, and `uninstall`. SDD commands read OpenSpec artifacts and render markdown or JSON; install commands copy/generate harness assets into user home directories and track ownership through a manifest.

The Go layout is module-oriented: `cmd/ai-harness` owns argument parsing, process I/O, environment-derived home paths, CLI rendering, and command dispatch; `internal/install` owns copied artifact mappings, install/uninstall, manifest validation, safe removal, and rollback for partial directory copies; `internal/commands` owns OpenCode slash-command generation from canonical prompt sources; `internal/opencode` owns `opencode.json` generation with `{{HOME}}` substitution; `internal/sdd` owns SDD state resolution, artifact discovery, task progress, verify-report heuristics, and markdown/JSON rendering. Current complexity is mostly cognitive load in `run.go`, which acts as a composition root but also carries parsing, prompting, rendering, and installer orchestration.

Install behavior to preserve: `ai-harness install` defaults to all harnesses in non-interactive mode, prompts on a TTY, accepts `--harness`, validates `--repo`, copies `skills/`, `AGENTS.md`, `prompts/sdd`, and OpenCode plugins, generates OpenCode commands under `~/.config/opencode/commands`, generates `~/.config/opencode/opencode.json`, and writes `~/.config/ai-harness/install-manifest.json`. `ai-harness uninstall` uses the manifest as authority, removes only managed regular files under managed roots, prunes empty parents, ignores the harness selection, and does not require a source repo.

Testing today includes Go unit tests across command, install, commands, opencode, and sdd packages; shell E2E tiers in `e2e/e2e_test.sh`; optional OpenCode config-load checks; optional Bun plugin tests; and optional live smoke. The Python target should replace Go unit tests with pytest + coverage, keep the shell E2E tier, and keep Bun plugin tests unchanged.

### Affected Areas
- `cli/cmd/ai-harness/main.go` — current process entrypoint; replace with a Python console script entrypoint.
- `cli/cmd/ai-harness/run.go` — current command surface, argument parsing, dispatch, rendering, and installer orchestration; primary port boundary.
- `cli/internal/install/install.go` — filesystem ownership, copy, manifest, rollback, and uninstall behavior; highest-risk behavioral port.
- `cli/internal/commands/commands.go` — OpenCode command generation; preserve placeholder substitution and frontmatter translation.
- `cli/internal/opencode/opencode.go` — OpenCode config generation; preserve host-injected paths and `{{HOME}}` substitution.
- `cli/internal/sdd/*.go` — SDD dispatcher/state machine; preserve JSON schema, markdown output, artifact classification, and routing decisions.
- `cli/*_test.go` and `cli/internal/**/*_test.go` — migrate to pytest tests with coverage.
- `cli/Makefile` — replace Go build/test/vet/fmt commands with uv, pytest, coverage, and ruff commands or keep as a compatibility wrapper.
- `e2e/e2e_test.sh` — update Tier 1 build/install commands to invoke the Python CLI while preserving the rest of the E2E contract.
- `openspec/testing-capabilities.md` — current Python target notes contain inaccuracies around coverage/ruff and should be corrected in proposal/design, not during exploration.

### Approaches
1. **First-slice Python CLI shell with SDD dispatcher port** — create a uv-managed Python CLI that preserves `sdd-status` and `sdd-continue`, plus pytest/coverage/ruff wiring, while leaving Go installer behavior as the reference for later porting.
   - Pros: small enough for an 800-line review budget; exercises packaging, CLI entrypoint, rich rendering decisions, pytest, coverage, and SDD JSON compatibility early; lowest filesystem risk.
   - Cons: does not complete the user-facing migration; install/uninstall still needs a later port or temporary bridge; requires clear README/Makefile expectations to avoid two competing CLIs.
   - Effort: Medium

2. **Full CLI port in one PR** — port SDD dispatcher, install/uninstall, command generation, OpenCode config generation, tests, Makefile, and E2E in a single change.
   - Pros: one-step migration and no temporary split-brain CLI.
   - Cons: likely exceeds the 800-line review budget; filesystem safety and manifest behavior create high regression risk; review surface mixes packaging decisions with behavioral porting.
   - Effort: High

3. **Compatibility wrapper around the Go binary** — introduce Python packaging and a console script that shells out to the existing Go implementation while gradually porting internals.
   - Pros: fastest path to uv packaging with near-zero behavioral risk.
   - Cons: not a real migration boundary; keeps Go build/runtime dependency; hides complexity behind a shallow wrapper and delays the hard design work.
   - Effort: Low

### Recommendation
Use the first-slice Python CLI shell with the SDD dispatcher port. It draws a deep boundary around deterministic OpenSpec status resolution, avoids the highest-risk filesystem installer behavior in the first PR, and gives the team a working uv/ruff/pytest/coverage/rich foundation without blowing the 800-line review budget.

Recommended first-slice scope for one PR:
- Add `cli/pyproject.toml` configured for uv, ruff, pytest, and coverage.
- Add a Python console entrypoint for `ai-harness`.
- Port only `sdd-status` and `sdd-continue` behavior, preserving the existing JSON schema and markdown semantics.
- Use `rich` only as the terminal rendering boundary for human-readable output; keep JSON output plain and schema-stable.
- Add pytest coverage for active-change selection, artifact classification, state machine routing, JSON output, and markdown smoke tests.
- Update Makefile commands to run `uv run pytest`, `uv run coverage run -m pytest && uv run coverage report`, `uv run ruff check`, and `uv run ruff format`.
- Defer install/uninstall, OpenCode command generation, OpenCode config generation, and E2E install migration to follow-up tasks/specs.

### Risks
- Behavior compatibility: SDD JSON field names, null/empty-list behavior, markdown text, and exit codes are observable and should be preserved.
- Filesystem safety: install/uninstall has rollback, manifest validation, managed-root checks, and unlisted-file preservation; porting it too early risks destructive regressions.
- Review budget: a full port will exceed 800 changed lines; the first PR needs a strict boundary.
- Packaging ambiguity: during migration, docs and Makefile must avoid unclear Go-vs-Python command ownership.
- Rich overuse: rich should not leak into deterministic JSON/status computation; otherwise tests couple to terminal formatting.
- Existing testing-capabilities notes conflate ruff linting with coverage; proposal/design should correct coverage to use `coverage.py`/pytest coverage reporting.

### Ready for Proposal
Yes — propose a bounded first PR that establishes the Python project and ports the SDD dispatcher only, preserving command compatibility while explicitly deferring installer/filesystem behavior.
