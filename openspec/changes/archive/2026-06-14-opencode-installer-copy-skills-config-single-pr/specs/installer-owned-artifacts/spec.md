# installer-owned-artifacts Specification

## Purpose

Define ai-harness installation ownership for copied skills, OpenCode assets, OpenCode configuration, manifest recording, reinstall, and uninstall.

## Requirements

### Requirement: Owned Artifact Installation

The system MUST install ai-harness-managed skills, OpenCode support assets, and OpenCode configuration as owned filesystem artifacts at their target locations. OpenCode global configuration MUST be installed at `~/.config/opencode/opencode.json`, and OpenCode global skills MUST be installed under `~/.config/opencode/skills/<name>/SKILL.md`.

#### Scenario: Install creates copied artifacts

- GIVEN a clean user home without existing ai-harness installed artifacts
- WHEN the user runs install
- THEN the required skills, OpenCode support assets, and OpenCode configuration exist at their target locations
- AND installed artifacts are regular copied files or directories, not repo-pointing symlinks

#### Scenario: Destination already exists

- GIVEN a destination file or directory already exists before install
- WHEN the user runs install
- THEN the destination is overwritten with the ai-harness-managed artifact

### Requirement: Central Install Manifest

The system MUST record every ai-harness-installed file in a central manifest or registry under `~/.config/ai-harness/`. The manifest MUST be the uninstall authority for owned installed files.

#### Scenario: Manifest records installed files

- GIVEN install completes successfully
- WHEN the manifest is inspected
- THEN it lists the installed file paths needed for uninstall

#### Scenario: Reinstall refreshes manifest

- GIVEN a previous manifest exists
- WHEN the user runs install again
- THEN the manifest reflects the current installed artifact set

### Requirement: Manifest-Based Uninstall

The system MUST remove files listed in the central manifest during uninstall, even when those files were edited after installation. The system MUST NOT depend on symlink targets to decide whether manifest-listed files are removable.

#### Scenario: Uninstall removes edited installed file

- GIVEN install recorded a file in the manifest
- AND the user edited that installed file after install
- WHEN the user runs uninstall
- THEN the edited file is removed

#### Scenario: Missing manifest entry is not removed

- GIVEN a user-created file is not listed in the manifest
- WHEN the user runs uninstall
- THEN that file remains in place
