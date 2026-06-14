# Design: OpenCode Installer Copies Skills and Config with Single-PR SDD Defaults

## Technical Approach

Redraw installer ownership around copied artifacts and a central manifest while preserving the existing deep CLI boundary: `cmd/ai-harness` composes host paths and `internal/install` owns artifact realization/removal. `internal/opencode` remains the source-specific renderer for host-substituted `opencode.json`; its output is registered in the same ownership manifest. SDD prompt/shared contracts are simplified so preflight defaults to `hybrid` and delivery policy is single PR while still reporting review-size risk.

## Architecture Decisions

| Decision | Choice | Alternatives considered | Rationale |
|---|---|---|---|
| Installer boundary | Keep `cli/internal/install` as the owner of artifact mappings, copy semantics, and manifest persistence. | Add a parallel copy package beside symlink logic. | One owner hides filesystem rules and avoids callers knowing which artifacts are links, generated files, or copied trees. |
| Manifest authority | Store a JSON manifest under `~/.config/ai-harness/`, listing installed file paths and source metadata. | Infer removals from repo paths or destination inspection. | Specs require uninstall to remove edited installed files; inference reintroduces symlink-era hidden coupling. |
| Overwrite behavior | Install/reinstall removes/replaces destination paths and refreshes the manifest. | Backup or preserve untracked destination files. | User-approved policy says install overwrites even if not manifest-owned; backup semantics would contradict expected ownership. |
| OpenCode config | Generate `~/.config/opencode/opencode.json` via `internal/opencode`, then include it in the central manifest. | Move config generation into `internal/install`. | `opencode` already hides `{{HOME}}` substitution; install should own ownership, not config rendering. |
| SDD delivery policy | Remove artifact-store and PR-chain choice flows; pass/use canonical `hybrid` and single-PR policy. | Keep old choices with different defaults. | Product policy eliminates choice to reduce orchestration complexity; review budget remains informational risk reporting. |

## Data Flow

```text
ai-harness install
  -> run.go resolves HOME/repo/harnesses
  -> install.Install copies mapped files/dirs
  -> commands.Generate + opencode.Generate create OpenCode outputs
  -> manifest writer records every owned installed file

ai-harness uninstall
  -> manifest reader loads ~/.config/ai-harness/install-manifest.json
  -> remover deletes manifest-listed files, even if edited
  -> manifest is refreshed/removed after cleanup
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `cli/internal/install/install.go` | Modify | Replace symlink vocabulary and behavior with artifact copy/remove plus manifest registration. |
| `cli/internal/install/install_test.go` | Modify | Assert regular copied files/dirs, overwrites, manifest refresh, and manifest-based uninstall. |
| `cli/cmd/ai-harness/run.go` | Modify | Compose install, generated commands, generated config, and manifest finalization; update output wording. |
| `cli/cmd/ai-harness/run_test.go` | Modify | Update CLI assertions from symlink/remove behavior to owned-copy behavior. |
| `cli/internal/opencode/opencode.go` | Modify | Keep generation API; expose/report enough outcome data for manifest registration if needed. |
| `e2e/e2e_test.sh`, `e2e/lib.sh` | Modify | Replace symlink assertions with regular-file/tree and uninstall ownership checks. |
| `install.sh`, `uninstall.sh` | Modify | Either align legacy scripts with copy/manifest behavior or clearly route users to the Go CLI. |
| `prompts/sdd/sdd-orchestrator.md` | Modify | Remove artifact-store and PR-chain preflight choices; default to hybrid and single PR. |
| `skills/_shared/persistence-contract.md` | Modify | Make `hybrid` the normal SDD persistence mode; remove user-choice language. |
| `skills/_shared/sdd-phase-common.md` | Modify | Replace chained-PR guard requirements with single-PR review-risk reporting. |
| `prompts/commands/sdd-*.md` | Modify | Remove references to artifact-store/chained-PR preflight requirements. |

## Interfaces / Contracts

```go
type Manifest struct {
    Version   int             `json:"version"`
    Installed []ManifestEntry `json:"installed"`
}

type ManifestEntry struct {
    Dest    string `json:"dest"`
    Source  string `json:"source,omitempty"`
    Kind    string `json:"kind"` // file | directory-generated-file
    Harness string `json:"harness,omitempty"`
}
```

Manifest path: `~/.config/ai-harness/install-manifest.json`. The manifest records files, not implicit directory ownership; copied directories should be expanded to file entries so uninstall removes only installed files and leaves user-created unlisted files intact.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Copy files/dirs, overwrite existing paths, manifest write/read, edited-file uninstall. | `go test ./...` with temp homes and fixed paths. |
| Integration | CLI install/uninstall output and OpenCode config placement. | Existing `run_test.go` style with injected HOME/repo fixtures. |
| E2E | Clean-home install, regular copied OpenCode assets, OpenCode config load, uninstall removes edited manifest-listed files. | `bash e2e/e2e_test.sh`; `bun test` remains plugin-specific. |

## Migration / Rollout

No data migration required. First reinstall replaces existing symlinks or real files with copied artifacts and writes the manifest. Users with old symlink installs can run the new uninstall after reinstall; without a manifest, uninstall should only remove the manifest itself if absent and report no owned files.

## Open Questions

- [ ] Should legacy `install.sh`/`uninstall.sh` keep full parity or become thin wrappers around the Go CLI?
