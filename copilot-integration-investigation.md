# GitHub Copilot CLI — Exhaustive Research Documentation

## Table of Contents

1. [Installation](#installation)
2. [Authentication](#authentication)
3. [Core Usage](#core-usage)
4. [Tool Permissions](#tool-permissions)
5. [Customization](#customization)
   - [Custom Instructions](#custom-instructions)
   - [Skills](#skills)
   - [Custom Agents](#custom-agents)
   - [Hooks](#hooks)
   - [MCP Servers](#mcp-servers)
   - [Plugins](#plugins)
   - [Settings](#settings)
   - [BYOK](#byok)
6. [Key Slash Commands](#key-slash-commands)
7. [Autopilot Mode](#autopilot-mode)
8. [Remote Steering](#remote-steering)
9. [VS Code Integration](#vs-code-integration)
10. [Programmatic / CI Integration](#programmatic--ci-integration)
11. [Session Management](#session-management)
12. [Rollback](#rollback)
13. [Voice Input](#voice-input)
14. [Best Practices](#best-practices)

---

## Installation

| Method | Command |
|--------|---------|
| npm (cross-platform) | `npm install -g @github/copilot` |
| Homebrew (macOS/Linux) | `brew install copilot-cli` |
| Winget (Windows) | `winget install GitHub.Copilot` |
| Install script | `curl -fsSL https://gh.io/copilot-install \| bash` |

**Prerequisites:**
- Active GitHub Copilot subscription
- Node.js 22+ (for npm)
- PowerShell v6+ (Windows)

---

## Authentication

### Methods (in priority order)

1. **OAuth device flow** (default): `copilot login` or `/login` in session
2. **Environment variables**: `COPILOT_GITHUB_TOKEN` > `GH_TOKEN` > `GITHUB_TOKEN`
3. **GitHub CLI fallback**: `gh auth token` if no env var set

### Supported Token Types

| Token Type | Prefix | Supported |
|------------|--------|-----------|
| OAuth token (device flow) | `gho_` | Yes |
| Fine-grained PAT | `github_pat_` | Yes (must be user-owned with "Copilot Requests" permission) |
| GitHub App user-to-server | `ghu_` | Yes |
| Classic PAT | `ghp_` | **No** |

### Switching Accounts

- `/user list` — list available accounts
- `/user switch` — switch to different account
- `/logout` — sign out (revokes local token only)

---

## Core Usage

### Interactive Session
```bash
copilot
```

### Programmatic Mode
```bash
copilot -p "prompt" -s           # Silent output
copilot -sp "prompt"             # Silent + only response
```

### Resume Session
```bash
copilot --continue               # Most recent session
copilot --resume                # Session picker
copilot --resume SESSION-ID      # Specific session
```

### Key Shortcuts

| Shortcut | Action |
|---------|--------|
| `Esc` | Cancel current operation |
| `Ctrl+C` | Cancel / clear input / exit |
| `Ctrl+L` | Clear screen |
| `@FILENAME` | Include file in context |
| `#NUMBER` | Include GitHub issue/PR |
| `! COMMAND` | Run shell command directly |
| `/` | Show slash commands |
| `?` | Show help |
| `Shift+Tab` | Cycle modes: normal → plan → autopilot |
| `Ctrl+T` | Toggle reasoning visibility |
| `Ctrl+G` | Edit prompt in external editor |
| `Ctrl+R` | Reverse search history |
| `Ctrl+X` then `/` | Run slash command while prompt has text |

---

## Tool Permissions

### Two Layers of Control

**Layer 1: Restrict AI's choices (what tools it can consider)**
```bash
--available-tools='bash,edit,view,grep,glob'  # Only these tools available
--excluded-tools='web_fetch,web_search'       # Disable specific tools
```

**Layer 2: Grant/deny permission to use tools**
```bash
--allow-tool='shell(git:*)'                  # Allow all git commands
--deny-tool='shell(git push)'                 # Deny specific command
--allow-tool='write'                          # Allow file writes
--allow-tool='MyMCP(create_issue)'            # Allow MCP tool
```

### Permission Syntax

| Pattern | Meaning |
|---------|---------|
| `shell(COMMAND)` | Specific shell command |
| `shell(git:*)` | All git subcommands |
| `write` | All file write operations |
| `MCP_SERVER(tool)` | Specific MCP tool |
| `MCP_SERVER` | All tools from MCP server |

### Permissive Options

```bash
--allow-all-tools    # All available tools
--allow-all / --yolo # All tools + paths + URLs (combine all allow-* options)
```

**In-session equivalents:** `/allow-all` or `/yolo`

### Resetting Permissions
```bash
/reset-allowed-tools  # Revokes all session permissions
```

---

## Customization

### Custom Instructions

Automatically included in prompts based on file location.

| Type | File | Scope |
|------|------|-------|
| Global | `~/.copilot/copilot-instructions.md` | All projects |
| Repository-wide | `.github/copilot-instructions.md` | Repository |
| Path-specific | `.github/instructions/*.instructions.md` | File patterns via `applyTo` frontmatter |
| Agent instructions | `AGENTS.md` (root or cwd) | AI agents |
| Alternative | `GEMINI.md`, `CODEX.md` (root) | Alternative models |

#### Path-Specific Example

```markdown
---
applyTo: "**/*.ts,**/*.tsx"
---

Always use TypeScript strict mode.
Prefer functional components over class components.
```

#### Frontmatter Options

```markdown
---
applyTo: "**/*.rb"
excludeAgent: "code-review"  # or "cloud-agent"
---
```

---

### Skills

Folders of instructions, scripts, and resources for specialized tasks.

#### Structure
```
skills/SKILL-NAME/
├── SKILL.md              # Required
├── script.sh            # Optional
└── resources/           # Optional
```

#### SKILL.md Frontmatter

```markdown
---
name: github-actions-debugging
description: Debug failing GitHub Actions. Use when asked about CI failures.
allowed-tools: shell
---

1. Use `list_workflow_runs` to find the failing run
2. Use `summarize_job_log_failures` for AI summary
3. If needed, use `get_job_logs` for full logs
```

#### Locations

| Type | Path |
|------|------|
| Project | `.github/skills/`, `.claude/skills/`, `.agents/skills/` |
| User | `~/.copilot/skills/`, `~/.agents/skills/` |

#### Skill Commands

```bash
/skills list                    # List available skills
/skills info SKILL-NAME         # Show skill details
/skills reload                  # Reload skills in session
/skills remove SKILL-DIR        # Remove skill
```

---

### Custom Agents

Specialized Copilot variants defined in `.agent.md` files.

#### Locations (priority order)

1. User: `~/.copilot/agents/`
2. Repository: `.github/agents/`
3. Organization: `/agents` in org's `.github-private`
4. Enterprise: `/agents` in enterprise's `.github-private`

#### Example Agent

```markdown
---
name: security-auditor
description: Security expert. Use when security review/audit requested.
tools: ["bash", "edit", "view", "grep"]
---

You identify:
- Exposed secrets/credentials
- XSS, SQL injection vulnerabilities
- Vulnerable dependencies
- Auth bypass vectors

If issues found, create a GitHub issue with full details.
```

#### Usage

```bash
/agent                          # Select from list
Use the security-auditor agent on...  # Direct invocation
copilot --agent=security-auditor --prompt "..."
```

#### Built-in Agents

| Agent | Description |
|-------|-------------|
| Explore | Quick codebase analysis without cluttering main context |
| Task | Runs tests/builds, brief on success, full output on failure |
| General purpose | Complex multi-step tasks in separate context |
| Code review | Minimizes noise, surfaces only genuine issues |
| Research | Deep research with citations |
| Rubber duck | Constructive critic (auto-invoked) |

---

### Hooks

Execute custom shell commands at key points during agent execution.

#### Locations

| Type | Path |
|------|------|
| Repository | `.github/hooks/` |
| User | `~/.copilot/hooks/` |

#### Triggers

| Trigger | When |
|---------|------|
| `sessionStart` | CLI session begins |
| `sessionEnd` | Session ends |
| `userPromptSubmitted` | User submits prompt |
| `preToolUse` | Before a tool runs |
| `postToolUse` | After a tool completes |
| `errorOccurred` | Error occurs |

#### Example Hook Configuration

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [{
      "type": "command",
      "bash": "echo \"Session started: $(date)\" >> logs/session.log",
      "powershell": "Add-Content -Path logs/session.log -Value \"Session started: $(Get-Date)\"",
      "cwd": ".",
      "timeoutSec": 10
    }],
    "preToolUse": [{
      "type": "command",
      "bash": "./scripts/log-tool.sh",
      "env": { "LOG_LEVEL": "INFO" }
    }]
  }
}
```

---

### MCP Servers

Model Context Protocol servers for extended capabilities. GitHub MCP server is **built-in**.

#### Configuration File

`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "type": "local",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {},
      "tools": ["*"]
    },
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": { "CONTEXT7_API_KEY": "YOUR-KEY" },
      "tools": ["*"]
    }
  }
}
```

#### MCP Commands

```bash
/mcp show                        # List configured servers
/mcp add                         # Interactive add
/mcp edit SERVER-NAME            # Edit configuration
/mcp delete SERVER-NAME          # Remove server
/mcp disable SERVER-NAME         # Disable temporarily
/mcp enable SERVER-NAME          # Re-enable
/mcp reload                      # Reload configuration
```

---

### Plugins

Bundled customizations with `plugin.json` manifest.

#### Structure

```
my-plugin/
├── plugin.json           # Required manifest
├── agents/               # Custom agents
├── skills/               # Skills
├── hooks.json            # Hook configuration
└── .mcp.json             # MCP server config
```

#### plugin.json Example

```json
{
  "name": "my-dev-tools",
  "description": "React development utilities",
  "version": "1.2.0",
  "author": { "name": "Jane Doe", "email": "jane@example.com" },
  "license": "MIT",
  "keywords": ["react", "frontend"],
  "agents": "agents/",
  "skills": ["skills/", "extra-skills/"],
  "hooks": "hooks.json",
  "mcpServers": ".mcp.json"
}
```

#### Plugin Commands

```bash
copilot plugin marketplace list                  # List registered marketplaces
copilot plugin marketplace add OWNER/REPO       # Add marketplace
copilot plugin install NAME@MARKETPLACE         # Install plugin
copilot plugin list                             # View installed plugins
copilot plugin update NAME                      # Update plugin
copilot plugin uninstall NAME                   # Remove plugin
```

**Default marketplaces:** `copilot-plugins`, `awesome-copilot`

---

### Settings

`~/.copilot/settings.json` or via `/settings` command:

```json
{
  "remoteSessions": true,
  "mergeStrategy": "rebase"
}
```

| Setting | Values | Purpose |
|---------|--------|---------|
| `remoteSessions` | `true`/`false` | Always enable remote control |
| `mergeStrategy` | `"rebase"`/`"merge"` | Default for `/pr fix conflicts` |

#### Settings Commands

```bash
/settings                        # Interactive settings dialog
/settings KEY VALUE            # Set inline
/settings reset KEY            # Reset to default
```

---

### BYOK (Bring Your Own Model)

```bash
export COPILOT_PROVIDER_BASE_URL=https://my-provider.com/v1
export COPILOT_PROVIDER_API_KEY=sk-...
copilot
```

**Requirements:**
- Tool calling support
- Streaming support
- 128k+ context window recommended

**Note:** Without GitHub auth, `/delegate`, GitHub MCP server, and GitHub Code Search are unavailable.

---

## Key Slash Commands

| Command | Purpose |
|---------|---------|
| `/plan [PROMPT]` | Create implementation plan before coding |
| `/delegate [PROMPT]` | Push task to Copilot cloud agent → creates PR |
| `/fleet [PROMPT]` | Parallel subagent execution for multi-step tasks |
| `/review [PROMPT]` | Code review agent |
| `/pr view` | Show PR status for current branch |
| `/pr create` | Create/update PR |
| `/pr fix feedback` | Address review comments |
| `/pr fix conflicts` | Sync and resolve merge conflicts |
| `/pr fix ci` | Diagnose and fix failing CI |
| `/pr fix` / `/pr fix all` | Run all three fix phases |
| `/pr auto` | Full PR lifecycle: create → fix → green |
| `/chronicle standup` | Generate standup report |
| `/chronicle tips` | Personalized usage tips |
| `/chronicle cost tips` | Token spend optimization |
| `/chronicle search QUERY` | Search session history |
| `/chronicle improve` | Suggest improvements to custom instructions |
| `/mcp add/show/edit/delete/disable/enable` | MCP server management |
| `/skills list/info/add/remove/reload` | Skill management |
| `/agent` | Browse/create custom agents |
| `/voice` | Enable speech-to-text dictation |
| `/remote on/off` | Enable/disable remote steering |
| `/undo` / `/rewind` | Rollback workspace to previous snapshot |
| `/keep-alive [on/off/busy/DURATION]` | Prevent machine sleep |
| `/settings [KEY VALUE]` | View/change settings |
| `/every INTERVAL PROMPT` | Schedule recurring prompt (experimental) |
| `/after DELAY PROMPT` | Schedule one-shot prompt (experimental) |
| `/compact [FOCUS]` | Manually compress conversation history |
| `/context` | Visualize token usage |
| `/usage` | Show session statistics |
| `/allow-all` / `/yolo` | Enable all permissions in-session |
| `/reset-allowed-tools` | Revoke session permissions |
| `/clear` / `/new` | Start fresh conversation |
| `/exit` / `/quit` | Exit CLI |
| `/help` | Show help |
| `/feedback` | Submit feedback/bugs/features |
| `/changelog [summarize]` | Show changelog |
| `/env` | Show loaded environment details |
| `/session [info/checkpoints/files/plan/rename/cleanup/prune/delete]` | Session management |
| `/share file/gist [PATH]` | Export session |
| `/terminal-setup` | Configure terminal for multiline |
| `/instructions` | View/toggle custom instruction files |
| `/init` | Initialize Copilot features for repo |
| `/cwd` / `/cd [PATH]` | Change working directory |
| `/list-dirs` | Show allowed directories |
| `/add-dir PATH` | Add allowed directory |
| `/permissions [show/reset]` | View/clear tool permissions |
| `/experimental [on/off/show]` | Toggle experimental features |
| `/extensions [manage/mode]` | Manage CLI extensions |
| `/ide` | Connect/disconnect VS Code |
| `/lsp [show/test/reload/help]` | Manage LSP configuration |
| `/model [MODEL]` | Select AI model |
| `/tasks` | View/manage background tasks |
| `/rename NAME` | Rename current session |
| `/search QUERY` | Search conversation (experimental) |
| `/ask QUESTION` | Quick side question (experimental) |
| `/clikit [COMPONENT]` | Preview CLI components |
| `/downgrade VERSION` | Downgrade CLI version (team accounts) |
| `/restart` | Restart CLI, preserve session |
| `/rubber-duck [PROMPT]` | Consult rubber duck agent |
| `/research TOPIC` | Deep research investigation |
| `/plan` | Toggle plan mode |

---

## Autopilot Mode

Autonomous execution without stopping for input.

### Interactive
Press `Shift+Tab` until "autopilot" appears in status bar → enter prompt

### Programmatic
```bash
copilot --autopilot --yolo --max-autopilot-continues 10 -p "YOUR PROMPT"
```

---

## Remote Steering

Connect to a running CLI session from GitHub.com or GitHub Mobile.

### Enable

```bash
copilot --remote              # At startup
/remote on                    # During session
```

### Access

1. **GitHub.com**: Click Copilot icon → Recent agent sessions
2. **GitHub Mobile**: Tap Copilot button → Agent sessions
3. **QR code**: `Ctrl+E` in session to display QR code

### Keep Alive

```bash
/keep-alive on                # Prevent sleep while session active
/keep-alive busy              # Only while agent is working
/keep-alive 30m               # For specific duration
```

---

## VS Code Integration

- **Auto-connect**: When cwd matches open workspace in VS Code
- **Diff review**: Proposed edits shown as side-by-side diffs
- **Accept/reject**: ✓ or ✗ buttons in diff view
- **Session viewing**: Copilot Chat → Sessions icon
- **Resume in terminal**: Right-click session → Resume in Terminal

### /ide Commands

```bash
/ide                          # View connection status
/ide connect                  # Connect to workspace
/ide disconnect               # Disconnect
/ide auto-connect [on/off]    # Toggle auto-connect
/ide open-file-diffs [on/off] # Toggle diff view in IDE
```

---

## Programmatic / CI Integration

### Basic Usage

```bash
copilot -p "PROMPT" -s \
  --allow-tool='shell(git:*)' \
  --allow-tool=write \
  --no-ask-user
```

### Options for Scripts

| Option | Purpose |
|--------|---------|
| `-p`, `--prompt` | Prompt to execute |
| `-s`, `--silent` | Suppress session metadata |
| `--no-ask-user` | Prevent clarifying questions |
| `--model MODEL` | Specify model |
| `--allow-tool` | Grant tool permissions |
| `--share=FILE` | Export session to Markdown |
| `--share-gist` | Export session to GitHub gist |

### GitHub Actions Example

```yaml
name: Daily summary
on:
  workflow_dispatch:
  schedule:
    - cron: '30 17 * * *'
permissions:
  contents: read
jobs:
  daily-summary:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - name: Set up Node.js
        uses: actions/setup-node@v4
      - name: Install Copilot CLI
        run: npm install -g @github/copilot
      - name: Run Copilot CLI
        env:
          COPILOT_GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
        run: |
          copilot -p "Review git log and summarize today's changes" \
            --allow-tool='shell(git:*)' \
            --allow-tool=write \
            --no-ask-user
```

### Shell Script Patterns

```bash
# Capture output in variable
result=$(copilot -p 'What version of Node.js? Give number only.' -s)

# Conditional check
if copilot -p 'Any TypeScript errors? Reply YES or NO.' -s \
  | grep -qi "no"; then
  echo "No errors found."
fi

# Process multiple files
for file in src/api/*.ts; do
  copilot -p "Review $file for issues" -s --allow-all-tools | tee -a review.md
done
```

---

## Session Management

### Session Storage

```
~/.copilot/session-state/{session-id}/
├── events.jsonl      # Full session history
├── workspace.yaml    # Metadata
├── plan.md           # Implementation plan
├── checkpoints/      # Compaction history
└── files/            # Persistent artifacts
```

### Session Commands

```bash
/session info                 # Show current session details
/session checkpoints          # List session checkpoints
/session checkpoints N       # View checkpoint N
/session files                # List temp files created
/session plan                 # Show current plan
/session rename NAME          # Rename session
/session cleanup             # Remove temp files
/session prune                # Delete old sessions
/session delete ID            # Delete specific session
/session delete-all           # Delete all sessions
```

### /chronicle Subcommands

```bash
/chronicle standup            # Standup report (last 24h)
/chronicle standup for last 3 days
/chronicle tips                # Personalized tips
/chronicle cost tips           # Token optimization
/chronicle search QUERY       # Full-text search
/chronicle improve            # Suggest custom instructions improvements
/chronicle reindex             # Rebuild local session store
```

---

## Rollback

Rewind workspace to previous state using Git snapshots.

### Methods

- **Double-Esc**: Press `Esc` twice when input is empty
- **Slash command**: `/undo` or `/rewind`

### Notes

- Snapshots created at start of each user interaction
- Restores entire workspace (not just Copilot changes)
- Cannot be undone — later snapshots permanently removed
- Requires Git repo with at least one commit

### Verify Rollback

```bash
! git status                  # Check modified files
! git log --oneline -1        # Current commit
! git diff                    # Review changes
```

---

## Voice Input

### Enable

1. Enter `/voice` in session
2. Download voice runtime when prompted
3. Select English or Spanish model

### Usage

| Method | Action |
|--------|--------|
| Hold spacebar | Start recording → release to insert |
| `Ctrl+X V` | Toggle recording on/off |

### Switch Models

```bash
/voice models                 # Open voice models picker
```

---

## Best Practices

### 1. Customize Your Environment

- Add `.github/copilot-instructions.md` with build/test commands
- Use path-specific instructions for different file types
- Configure allowed tools patterns

### 2. Plan Before You Code

Use `/plan` for:
- Complex multi-file changes
- Refactoring with many touch points
- New feature implementation

Skip `/plan` for:
- Quick bug fixes
- Single file changes

### 3. Explore → Plan → Code → Commit Workflow

```
1. Explore: "Read the auth files but don't write code yet"
2. Plan: /plan Implement password reset flow
3. Review: Check and modify plan
4. Implement: "Proceed with the plan"
5. Verify: "Run tests and fix failures"
6. Commit: "Commit with descriptive message"
```

### 4. Leverage Infinite Sessions

- Use `/clear` or `/new` between unrelated tasks
- Use `/compact` to manually trigger context compression
- Use `/context` to visualize token usage

### 5. Delegate Effectively

| Use `/delegate` | Work locally |
|----------------|--------------|
| Tangential tasks | Core feature work |
| Documentation updates | Debugging |
| Refactoring separate modules | Interactive exploration |

### 6. Use /fleet for Parallel Execution

```bash
/fleet implement the plan
```

Copilot breaks task into parallel subtasks run by subagents.

### 7. Use Autopilot for Long-Running Tasks

```bash
copilot --autopilot --yolo --max-autopilot-continues 10 -p "TASK"
```

### 8. Multi-Repository Work

```bash
# Option 1: Run from parent directory
cd ~/projects && copilot

# Option 2: Add directories during session
/add-dir /Users/me/projects/backend-service
/add-dir /Users/me/projects/shared-libs
```

### 9. Model Selection

| Model | Best For |
|-------|----------|
| Auto | Reduced rate limiting, lower latency |
| Claude Opus 4.5 | Complex architecture, deep debugging |
| Claude Sonnet 4.5 | Day-to-day coding, routine tasks |
| GPT-5.2 Codex | Code generation, code review |

Switch mid-session with `/model`.

### 10. Security Considerations

- Never use `--allow-all` / `--yolo` as default alias
- Review all proposed changes before accepting
- Use permission allowlists judiciously
- Copilot avoids committing secrets, but always verify

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `COPILOT_HOME` | Config directory (default `~/.copilot`) |
| `COPILOT_GITHUB_TOKEN` | GitHub auth (highest priority) |
| `COPILOT_PROVIDER_BASE_URL` | BYOK provider endpoint |
| `COPILOT_PROVIDER_API_KEY` | BYOK API key |
| `COPILOT_OFFLINE` | `true` = air-gapped mode |
| `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` | Extra dirs for `AGENTS.md` lookup |
| `GH_TOKEN` | GitHub auth (fallback) |
| `GITHUB_TOKEN` | GitHub auth (fallback) |

---

## Troubleshooting

### Authentication Issues

1. Run `copilot login`
2. Check token: `COPILOT_GITHUB_TOKEN` env var
3. Verify with GitHub CLI: `gh auth status`
4. Fine-grained PAT must have "Copilot Requests" permission

### Hooks Not Executing

1. Verify JSON in `.github/hooks/` or `~/.copilot/hooks/`
2. Check JSON syntax: `jq . hooks.json`
3. Ensure `version: 1` is set
4. Verify script is executable: `chmod +x script.sh`
5. Check proper shebang: `#!/bin/bash`

### Tool Permission Denied

- Use `--allow-tool` to grant permission
- Use `/reset-allowed-tools` to reset session permissions
- Check `--available-tools` isn't blocking the tool

---

## Further Reading

- [Official Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli)
- [Copilot CLI Reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- [Programmatic Reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference)
- [Hooks Reference](https://docs.github.com/en/copilot/reference/hooks-reference)
- [Plugin Reference](https://docs.github.com/en/copilot/reference/cli-plugin-reference)
- [Skills Course](https://github.com/skills/create-applications-with-the-copilot-cli)
