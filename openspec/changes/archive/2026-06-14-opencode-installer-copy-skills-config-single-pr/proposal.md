# Proposal: OpenCode Installer Copies Skills and Config with Single-PR SDD Defaults

## Intent

Replace repo-pointing symlinks with owned copy/install behavior for OpenCode skills and configuration, backed by a central manifest for deterministic uninstall. Simplify SDD preflight by defaulting persistence to hybrid and forcing single-PR delivery.

## Scope

### In Scope
- Copy skills and OpenCode support assets into correct destinations.
- Install OpenCode config under `~/.config/opencode/`.
- Track installed files in a manifest/registry under `~/.config/ai-harness/`.
- Uninstall deletes manifest-listed files, even if edited after install.
- Reinstall overwrites destination files, even if not already manifest-owned.
- Remove SDD artifact-store prompting and use hybrid by default.
- Remove chained/large-PR decision flow and force single-PR behavior.

### Out of Scope
- Creating specs, design, tasks, or implementation in this phase.
- Preserving user edits to installed files during uninstall/reinstall.
- Engram-only or file-only artifact-store choices.

## Capabilities

### New Capabilities
- `installer-owned-artifacts`: Defines copy, overwrite, manifest, reinstall, and uninstall behavior for ai-harness-managed files.
- `sdd-preflight-defaults`: Defines default SDD artifact persistence and single-PR delivery behavior.

### Modified Capabilities
- None

## Approach

Redraw `cli/internal/install` around artifact mapping to owned-copy/remove. Keep OpenCode config generation in `cli/internal/opencode`, but register outputs in the central manifest. Update SDD prompts/shared contracts to remove choices now fixed by policy.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `cli/internal/install` | Modified | Copy/remove owned artifacts; manifest integration |
| `cli/cmd/ai-harness` | Modified | Install/uninstall orchestration and output |
| `cli/internal/opencode` | Modified | Config install/removal ownership |
| `prompts/sdd` | Modified | Hybrid default; single-PR flow |
| `skills/_shared` | Modified | Persistence/delivery contracts |
| `e2e` | Modified | Assertions move from symlink behavior to copied ownership |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Uninstall deletes edited installed files | High | Make manifest ownership rule explicit and tested |
| Stale copied assets after repo updates | Medium | Document reinstall as refresh path |
| Single-PR policy increases review load | Medium | Preserve review-budget visibility without chained flow |

## Rollback Plan

Revert the change set to restore symlink install behavior, previous SDD prompts, and chained-PR guidance. Users can reinstall after rollback to recreate symlinks.

## Dependencies

- Correct OpenCode paths: global config `~/.config/opencode/opencode.json`; global skills under `~/.config/opencode/skills/<name>/SKILL.md`.

## Success Criteria

- [ ] Install creates copied files/directories, not symlinks, at OpenCode destinations.
- [ ] Manifest under `~/.config/ai-harness/` records installed files.
- [ ] Uninstall removes manifest-listed files after edits.
- [ ] Reinstall overwrites destination files.
- [ ] SDD preflight no longer asks artifact-store or PR-chain questions.
