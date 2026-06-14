# Tasks: OpenCode Installer Copies Skills and Config with Single-PR SDD Defaults

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 650-900 |
| 400-line budget risk | High |
| Chained PRs recommended | No |
| Suggested split | Single PR by product policy |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Installer manifest and copy ownership | Single PR | Include Go unit tests and CLI wiring. |
| 2 | E2E and legacy script migration | Single PR | Delete root scripts; verify install/uninstall behavior. |
| 3 | SDD preflight simplification | Single PR | Remove artifact-store and PR-chain choice language. |

## Phase 1: RED Tests

- [x] 1.1 Update `cli/internal/install/install_test.go` to fail for copied regular files/dirs, overwrite, manifest refresh, edited-file uninstall, and unlisted-file preservation.
- [x] 1.2 Update `cli/cmd/ai-harness/run_test.go` to fail until install writes `~/.config/opencode/opencode.json`, records it, and uninstall removes manifest-listed outputs.
- [x] 1.3 Update `e2e/e2e_test.sh` and `e2e/lib.sh` to fail on symlink installs and verify copied OpenCode skills/config plus edited-file uninstall.
- [x] 1.4 Add prompt/contract text assertions, if existing test helpers allow, for hybrid default and no artifact-store or PR-chain choice language.

## Phase 2: Installer Ownership Implementation

- [x] 2.1 Modify `cli/internal/install/install.go` to copy mapped files/directories instead of symlinking, replacing pre-existing destinations.
- [x] 2.2 Add manifest read/write support in `cli/internal/install/install.go` for `~/.config/ai-harness/install-manifest.json`, expanding copied directories to file entries.
- [x] 2.3 Modify uninstall in `cli/internal/install/install.go` to remove manifest-listed files, ignore symlink target inference, preserve unlisted user files, and clean empty owned directories safely.
- [x] 2.4 Keep filesystem decisions inside `cli/internal/install`; expose only install/uninstall outcomes to callers.

## Phase 3: CLI and OpenCode Wiring

- [x] 3.1 Modify `cli/cmd/ai-harness/run.go` to compose copied artifacts, generated commands, generated OpenCode config, and manifest finalization.
- [x] 3.2 Modify `cli/internal/opencode/opencode.go` only as needed so generated `~/.config/opencode/opencode.json` can be registered without leaking config-rendering details.
- [x] 3.3 Delete legacy root scripts `install.sh` and `uninstall.sh`; update migration notes to route users through the Go CLI.

## Phase 4: SDD Policy Updates

- [x] 4.1 Modify `prompts/sdd/sdd-orchestrator.md` to default artifact persistence to `hybrid` without asking the user.
- [x] 4.2 Modify `skills/_shared/persistence-contract.md` and `skills/_shared/sdd-phase-common.md` to remove artifact-store choice and chained/large-PR decision flow language.
- [x] 4.3 Modify `prompts/commands/sdd-*.md` to remove obsolete preflight requirements and keep review-size risk reporting informational.

## Phase 5: Verification and Cleanup

- [x] 5.1 Run `go test ./...` from `cli/` and fix failures without weakening behavior assertions.
- [x] 5.2 Run `bash e2e/e2e_test.sh` and verify clean install, reinstall overwrite, manifest refresh, and uninstall.
- [x] 5.3 Run `bun test` in `agent-clis/opencode/plugins/` if plugin config references changed.
- [x] 5.4 Review docs/output for stale symlink, artifact-store-choice, chained-PR, and legacy-script instructions.
