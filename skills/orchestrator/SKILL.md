---
name: orchestrator
description: The generic delegation ENGINE for autonomous, high-effort tasks. Holds the mechanics every
  recipe reuses — how to spawn sub-agents, inject skills by path, thread context, persist to engram, and
  respect the no-nesting constraint. Load it ALONGSIDE a recipe skill (e.g. dev-orchestrator); the recipe
  supplies the steps, this supplies the how. Use when coordinating sub-agents, orchestrating, or
  "delegate this".
---

You are the **top-level COORDINATOR**. You hold this engine **plus a recipe** skill. The recipe says
*what* stages run and in *what order*; this engine says *how* to delegate each one. You delegate every
piece of real work to sub-agents — you do not implement yourself.

## The one hard constraint — read first
**Sub-agents CANNOT spawn sub-agents** in Claude Code (a delegated agent has no `Agent` tool, even when
its listing shows `*` — verified empirically). Therefore **ALL fan-out happens HERE, at the top level.**
Never hand a *recipe* to a single sub-agent expecting it to fan out — it can't. You run the recipe
yourself and delegate each *stage*, and each parallel unit within a stage, as its own sub-agent.

## How to delegate a stage
1. **Pick the skill(s).** Match the stage against the **Summary** column of `.atl/registry.md` (build or
   refresh it with `create-skills-registry` if missing). Take the matching **Path** value(s) — never the
   summary.
2. **Choose the sub-agent type.** Read-only reconnaissance → `Explore`. Anything that edits code, runs
   the suite, or touches git → `general-purpose` (it has Edit/Write/Bash).
3. **Spawn the sub-agent** (`Agent` tool) with a prompt containing, in this order:
   - `## Skills to load before work` — the exact absolute `SKILL.md` path(s). The sub-agent reads those
     first and applies them. `SKILL.md` is the source of truth; never inline a summary in its place.
   - **Task** — the single stage to perform, plus the engram key it must **read** (its input) and the key
     it must **write** (its output).
   - **Context** — the prior stage's summary you are threading forward (see handoff).
   - **Report back** — "save your findings to engram under `<key>`, then return a short summary."
4. **Parallel units** in one stage (no shared unbuilt dependency) → spawn them in **one message** so they
   run concurrently. **Blocked units** → wait for the blocker's sub-agent to return first.

## Handoff — engram + summary (do BOTH)
Every sub-agent **persists** durable findings to engram **and returns a summary** to you.
- You hold the summaries to drive sequencing and to thread context into the next stage's prompt.
- Engram holds the full artifact, so any later stage (a retry, or recovery after a compaction) reads the
  detail via the deterministic key — you only pass the **key**, never re-paste the content.

### Engram convention (memory only — never use engram for delegation)
- Tools: `mem_search` → id, then `mem_get_observation(id)` (two-step recovery). Save with `mem_save`.
- Deterministic keys: `slice/{prd}/...` (PRD-scoped) and `slice/{prd}/issue-{n}/...` (sub-issue-scoped).
- Every save: `type: "architecture"` (or `"config"` for capability detection), `capture_prompt: false`.
- Keep a `slice/{prd}/issue-{n}/state` artifact current (last completed step) so a recipe can resume after
  a context compaction.

## When NOT to delegate
Do the work yourself only when it is **not** a real challenge: ≤2 skills, ≤2 files, a single web page.
Anything heavier → delegate.
