# Testing Capabilities — ai-harness-setup (Go to Python Migration)

## Migration Context

**Last updated**: 2026-06-14
**Migration phase**: sdd-status ported to Python and archived; sdd-continue ported to Python.
**Strict TDD Mode**: ALWAYS ENABLED (not configurable — no `strict_tdd: false` toggle exists or will be written).

---

## Python Target Stack (live — sdd-status, sdd-continue)

| Capability | Available | Command |
|---|---|---|
| Test runner | ✅ | `uv run pytest` |
| Test layers | ✅ | unit, integration (pytest) |
| Coverage | ✅ | `uv run coverage run -m pytest && uv run coverage report` |
| Linter | ✅ | `uv run ruff check` |
| Formatter | ✅ | `uv run ruff format` |
| Type checker | ❌ | Not configured (no mypy in dev deps) |
| CLI framework | ✅ | `typer` for parsing/dispatch |
| Rendering | ✅ | `rich` for human output only; JSON is plain `json.dumps` |
| Package manager | ✅ | `uv` |

### Python Test Details

- **Config file**: `cli/pyproject.toml`
- **Test paths**: `cli/tests/`
- **Tests**: 121 passing (sdd-status and sdd-continue coverage: CLI, resolver, JSON compat, boundary, verify-report, tooling, dispatcher rendering)
- **Coverage target**: `ai_harness` package
- **Line length**: 100
- **Ruff rules**: E, F, I, UP, B
- **Build backend**: hatchling
- **Console script**: `ai-harness = "ai_harness.cli:main"` (preserves Go-compatible name)

---

## Go Reference Stack (fallback — all commands)

| Capability | Available | Command |
|---|---|---|
| Test runner | ✅ | `go test ./...` |
| Test layers | ✅ | unit, integration (stdlib `testing`) |
| Coverage | ❌ | No coverage tooling configured (no `-coverprofile` in standard invocation) |
| Linter | ❌ | None beyond `gofmt` |
| Formatter | ✅ | `gofmt` (implicit, no explicit config) |
| Type checker | ❌ | Not configured |

### Go Test Details

- **Module**: `github.com/diegoagd10/ai-harness-setup/cli`
- **Go version**: 1.25.6
- **Tests**: All passing (cmd/ai-harness, internal/sdd, internal/commands, internal/install, internal/opencode)
- **SDD core**: `internal/sdd/` — deep module, one responsibility per file

---

## E2E

| Layer | Available | Command |
|---|---|---|
| E2E | ✅ | `bash e2e/e2e_test.sh` (Docker-based) |
| Plugin (TypeScript) | ✅ | `bun test` at `agent-clis/opencode/plugins/` |

---

## Hybrid Migration Notes

- `sdd-status` is fully ported to Python, archived; current Python suite has 121 tests green including sdd-status and sdd-continue coverage.
- `sdd-continue` is ported to Python.
- Installer, uninstaller, plugin setup, command generation remain Go-only.
- Golden/parity tests in `test_json_compat.py` validate Python output against Go reference.
