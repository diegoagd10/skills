## Exploration: opencode-installer-copy-skills-config-single-pr

### Current State
The active installer path is the Go CLI (`ai-harness install` / `uninstall`), with legacy shell scripts still present. `cli/internal/install` owns repo-to-home artifact mappings and currently creates symlinks for skills, `AGENTS.md`, OpenCode `prompts/sdd`, and OpenCode `plugins`. `cli/cmd/ai-harness/run.go` composes install/uninstall, generates OpenCode slash commands, and generates/removes `~/.config/opencode/opencode.json` from `agent-clis/opencode/opencode.json` with `{{HOME}}` substitution.

OpenCode configuration already installs to the correct user-level location (`$HOME/.config/opencode`). However, most OpenCode support assets are symlinked, and uninstall only removes symlinks pointing into the repo plus generated command/config files. E2E and unit tests currently assert symlink behavior.

SDD session preflight is prompt-driven in `prompts/sdd/sdd-orchestrator.md`: it asks for artifact store (`openspec`, `engram`, `both`) and PR delivery strategy (`ask-always`, `single-pr-default`, `force-chained`, `auto-forecast`). Shared persistence and phase common docs still describe user-selected/default stores and chained PR/large-PR guard behavior.

### Affected Areas
- `cli/internal/install/install.go` — central mapping and symlink/uninstall logic; should become the ownership boundary for copy/remove behavior.
- `cli/internal/install/install_test.go` — heavily asserts symlinks, relinks, repo-pointing uninstall, and backup semantics.
- `cli/cmd/ai-harness/run.go` — install composition root, user-facing help/output, OpenCode extras install/uninstall ordering.
- `cli/cmd/ai-harness/run_test.go` — CLI-level assertions for symlinks, OpenCode extras, harness selection, and uninstall.
- `cli/internal/opencode/opencode.go` — already generates/removes `opencode.json`; may need ownership markers/backups if config copy semantics expand beyond this file.
- `cli/internal/commands/commands.go` — already copies/generates command files and removes owned command names; useful pattern for copy-style install/uninstall.
- `e2e/e2e_test.sh` and `e2e/lib.sh` — currently assert installed OpenCode assets are symlinks into the repo.
- `install.sh` and `uninstall.sh` — legacy shell scripts still symlink and may need parity or clear deprecation.
- `prompts/sdd/sdd-orchestrator.md` — owns preflight prompt, default artifact-store behavior, PR strategy choices, delivery/chain guard text.
- `skills/_shared/persistence-contract.md` — shared artifact-store default and mode-resolution contract.
- `skills/_shared/sdd-phase-common.md` — shared delivery strategy/review workload guard still recommends chained PRs and size exceptions.
- `prompts/commands/sdd-*.md` — command gates mention preflight requiring artifact store/chained PR strategy and may need aligned wording.
- `agent-clis/opencode/opencode.json` — canonical OpenCode config; install copies/generates it into `$HOME/.config/opencode/opencode.json`.

### Approaches
1. **Replace symlink module with owned copy/remove module** — Keep `install.Config` as the deep module, but change each mapping from link realization to copy realization. For directories, recursively copy into the destination. For files, copy bytes/permissions. On install, backup existing real files/dirs that are not known owned outputs; on reinstall, replace/update owned installed paths idempotently. On uninstall, remove installed paths owned by ai-harness rather than only repo-pointing symlinks.
   - Pros: Single owner for install semantics; callers still use a small interface (`Install`/`Uninstall`); reduces leaked knowledge about symlinks across CLI/E2E/tests.
   - Cons: Must define ownership carefully to avoid deleting user-created config; recursive copy/removal needs tests for nested directories and stale files.
   - Effort: Medium

2. **Add a separate copy layer beside existing symlink logic** — Keep current link behavior for some mappings and add new copy functions for skills/OpenCode config.
   - Pros: Smaller initial diff for selected assets.
   - Cons: Creates a shallow/pass-through split where callers and tests must know which artifacts are links vs copies; likely increases change amplification and unknown unknowns during uninstall.
   - Effort: Medium

### Recommendation
Use approach 1: redraw `cli/internal/install` around an `artifact mapping -> install/remove owned artifact` abstraction instead of symlink-specific operations. The dominant complexity symptom is change amplification: link terminology and behavior are spread across comments, output vocabulary, tests, E2E assertions, shell scripts, and docs. A copy-oriented deep module should hide filesystem mechanics and expose only stable install outcomes.

For OpenCode config, keep `opencode.Generate` as the source of truth for `opencode.json` because it already hides host-specific `{{HOME}}` substitution and writes the correct location. Treat `commands.Generate` as the proven copy/generate pattern for slash commands. For SDD preflight, update the orchestrator and shared contracts to default artifact store to `hybrid` without asking, remove artifact-store options from the prompt, and normalize delivery to a single-PR flow without chained-PR choice text.

### Risks
- Removing copied directories safely requires an ownership model. Without a manifest, uninstall could either leave stale files or delete user-added files under copied directories.
- Copying directories means installed assets can become stale until reinstall; this is intentional but should be documented and tested.
- Existing tests and E2E currently assert symlinks, so implementation must update behavior-first assertions rather than only changing code.
- `both` vs `hybrid` naming is inconsistent in orchestrator text; defaulting to hybrid should normalize the canonical value passed to sub-agents.
- Forcing single PR conflicts with existing review workload guard language that protects reviewer burden through chained PR recommendations; the new single-PR policy should still preserve review-budget visibility or explicitly replace it.

### Ready for Proposal
Yes — the proposal should define copy ownership semantics for uninstall, whether legacy shell scripts remain supported or are updated, and how much of the review workload guard survives after forcing single-PR delivery.
