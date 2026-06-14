# Proposal: Go to Python

## Intent

Migrate `ai-harness` from Go toward Python to align with this project’s AI/Python workflow and unlock `uv`, `pytest`, coverage, `ruff`, `typer`, and `rich`. The first PR is a migration foundation, not a polished replacement.

## Scope

### Goals / In Scope
- Add a `uv`-managed Python CLI foundation under `cli/`.
- Port only `sdd-status` and `sdd-continue`.
- Preserve command names, flags, JSON schema, file paths, and exit codes.
- Use `typer` for Python CLI command parsing, command tree, options/flags, help, and dispatch while preserving Go-compatible hyphenated command names.
- Use `rich` only for human output; `--json` remains plain deterministic JSON.
- Wire `uv`, `ruff`, `pytest`, coverage.

### Non-Goals / Out of Scope
- Installer, uninstaller, plugin setup, command generation, and config generation unless later approved.
- Removing Go in the first PR.
- Changing SDD semantics, paths, JSON, or routing beyond parity.

## Capabilities

### New Capabilities
- `python-sdd-cli`: Python foundation for migrated SDD commands, deterministic status resolution, human rendering, stable JSON, and quality tooling.

### Modified Capabilities
- None.

## Compatibility Contract

- Commands: `sdd-status` and `sdd-continue` keep names and invocation shape.
- Flags: supported flags remain compatible, including `--json`.
- JSON: fields, null/empty values, ordering expectations, and semantics remain stable.
- Files: OpenSpec paths and artifact discovery remain unchanged.
- Exit codes: success, invalid/missing state, and failure cases preserve Go-observed behavior.

## Approach

Use temporary hybrid migration: Go and Python may coexist while slices move over. Create a deep Python boundary around SDD state resolution and rendering. Use Typer at the CLI boundary for parsing, help, and dispatch, preferring explicit command names where needed to preserve `sdd-status` and `sdd-continue`. Defer filesystem-heavy installer behavior. Keep `rich` outside deterministic logic.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `cli/pyproject.toml` | New | uv, pytest, coverage, ruff config |
| `cli/` Python package | New | Entrypoint and SDD commands |
| `cli/internal/sdd/*.go` | Reference | Parity source |
| `cli/Makefile` | Modified | uv/ruff/pytest/coverage wrapper |
| `openspec/changes/go-to-python/` | New | SDD artifacts |

## Risks and Open Questions

| Risk / Question | Likelihood | Mitigation |
|---|---:|---|
| JSON or exit-code drift | Med | Golden/parity tests against Go behavior |
| Hybrid CLI ownership confusion | Med | Document first-slice ownership |
| `rich` leaks into JSON | Low | Renderer-separated deterministic tests |
| Entrypoint shape | Med | Resolve in design |

## Rollback Plan

Revert the Python package, Makefile updates, and change artifacts. Keep Go CLI as the fallback until Python is validated.

## Dependencies

- `uv`, `pytest`, coverage integration, `ruff`, `typer`, `rich`.
- Existing Go implementation.

## Success Criteria

- [ ] `sdd-status` and `sdd-continue` preserve flags, files, JSON, and exit codes.
- [ ] `uv run pytest`, coverage, `uv run ruff check`, and `uv run ruff format` are wired.
- [ ] First PR stays limited to Python foundation plus the two SDD commands.
