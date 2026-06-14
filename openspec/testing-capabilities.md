# Testing Capabilities — ai-harness-setup (Go to Python Migration)

## Current State (Go)

**Strict TDD Mode**: Enabled
**Detected**: 2026-06-14
**Note**: Migration target is Python; this documents the source (Go) state.

### Test Runner

- Command: `go test ./...`
- Framework: Go stdlib `testing`

### Test Layers

| Layer | Available | Tool |
|-------|-----------|------|
| Unit | ✅ | Go stdlib `testing` |
| Integration | ✅ | Go stdlib httptest |
| E2E | ✅ | bash (`e2e/e2e_test.sh`) |

### Coverage

- Available: ❌
- Command: —

### Quality Tools

| Tool | Available | Command |
|------|-----------|---------|
| Linter | ❌ | — |
| Type checker | ❌ | — |
| Formatter | ✅ | `gofmt` |

---

## Target State (Python)

**Strict TDD Mode**: Enabled (required — not configurable)
**Note**: Strict TDD is the method for every project. No `strict_tdd: false` toggle exists or will be written.

### Test Runner

- Command: `uv run pytest` (requires `pytest` in dependencies)
- Framework: pytest
- Layers: unit (pytest), integration (pytest + pytest-asyncio/pytest-httpx), E2E (shell scripts)

### Coverage

- Available: ✅
- Command: `uv run ruff check --select=C4 --diff` (ruff internal) OR `uv run coverage run -m pytest && uv run coverage report`
- Note: ruff v0.9+ supports `--diff` for CI gate without coverage persist

### Quality Tools

| Tool | Available | Command |
|------|-----------|---------|
| Linter | ✅ | `uv run ruff check` |
| Type checker | ✅ | `uv run ruff check --select=UP,SIM` (ruff lints type-related rules) or `uv run mypy` |
| Formatter | ✅ | `uv run ruff format` |

### CLI Output

- Framework: `rich` (for styled CLI output, tables, progress bars)

### Python Project File

- Path: `cli/pyproject.toml`
- Package manager: `uv`
- Build tool: `hatch` or `rye` style (standard Python project)