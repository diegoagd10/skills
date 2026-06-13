# agent-clis/opencode

Faithful copy of the **OpenCode** SDD (Spec-Driven Development) configuration that
[`gentle-ai`](https://github.com/Gentleman-Programming/gentle-ai) generates. Staged
here so we can study/adapt it **without touching the repo's main `skills/`**.

This mirrors what `gentle-ai sync` writes into `~/.config/opencode/`.

## How the pipeline works

A single **primary** agent orchestrates; everything else is a **hidden subagent**
delegated to via OpenCode's native `task` tool. There is no custom runtime — the
whole pipeline is prompts + `opencode.json` config.

```
gentle-orchestrator (primary)
  └─ task tool ─▶ sdd-init → sdd-explore → sdd-propose ─┬─▶ sdd-spec ─┐
                                                        └─▶ sdd-design ┴─▶ sdd-tasks
                  ─▶ sdd-apply → sdd-verify → sdd-archive
  judgment ─▶ jd-judge-a ∥ jd-judge-b (blind, parallel) → jd-fix-agent → re-judge
  review   ─▶ review-risk / -readability / -reliability / -resilience (R1–R4)
```

The orchestrator never works inline; it asks a session **preflight** (interactive vs
auto, artifact backend, PR strategy, review budget), enforces **hard gates** between
phases, and a **review-workload guard** before implementing.

## Layout

| Path | Purpose |
|---|---|
| `opencode.json` | The whole agent graph: `gentle-orchestrator` (primary) + 17 hidden subagents (10 SDD phases, 3 judgment-day, 4 reviewers). Prompts are `{file:...}` references; only the short judgment/reviewer prompts stay inline. |
| `AGENTS.md` | Global persona / system prompt applied to all agents. |
| `sdd-orchestrator.md` | The primary orchestrator prompt, referenced by `gentle-orchestrator` via `{file:{{HOME}}/.config/opencode/sdd-orchestrator.md}`. |
| `commands/sdd-*.md` | Slash-command entrypoints (`/sdd-new`, `/sdd-ff`, `/sdd-continue`, `/sdd-apply`, `/sdd-verify`, `/sdd-archive`, `/sdd-status`, `/sdd-init`, `/sdd-explore`, `/sdd-onboard`). |
| `prompts/sdd/*.md` | The prompt each phase subagent loads. Derived from the matching `skills/<phase>/SKILL.md`. |
| `plugins/*.ts` | OpenCode plugins: `skill-registry.ts` (resolves project skills) and `model-variants.ts` (model profiles). |
| `skills/` | Full bundled skill set, incl. the `judgment-day` skill (the "juicio final" choreography), `_shared` conventions, and the `sdd-*` phase skills. |

## `{{HOME}}` placeholder

`opencode.json` references subagent prompts with absolute paths using a literal
`{{HOME}}` placeholder, e.g.:

```json
"prompt": "{file:{{HOME}}/.config/opencode/prompts/sdd/sdd-init.md}"
```

`gentle-ai` substitutes `{{HOME}}` with the real home dir at install time. To run this
copy directly you'd either replace `{{HOME}}` with your home and drop the folder into
`~/.config/opencode/`, or rewrite the refs to relative `{file:./prompts/sdd/...}`.

## Source

Assembled from `internal/assets/opencode/` and `internal/assets/skills/` of the
`gentle-ai` repo, with `opencode.json` / `AGENTS.md` taken from its golden fixtures
(the exact generated output).
