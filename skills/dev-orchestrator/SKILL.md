---
name: dev-orchestrator
description: The autonomous recipe that implements ONE sub-issue of a PRD end-to-end — explore → plan →
  per-class TDD fan-out → integrate → bounded verify loop → PR → accept — by delegating each stage to a
  sub-agent. Load it ALONGSIDE the orchestrator engine; this recipe owns the fan-out. Use to "implement
  the next sub-issue", run the dev pipeline, or "dev-orchestrator".
---

> **RECIPE for the top-level coordinator.** You run this YOURSELF while holding the `orchestrator`
> engine. You never hand this whole recipe to one sub-agent — it owns the fan-out, and sub-agents can't
> nest. Each *stage* below is a separate delegated sub-agent.

Implement **one sub-issue** of a PRD autonomously. The human's judgment is already baked into the Design
and the sub-issues upstream, so there are **NO ratification gates**. You open a PR but **NEVER merge** —
the PR is the human's verification point.

## Inputs
- **PRD** = the parent GitHub issue number `{prd}` (required). The repo is the current working repo
  (native sub-issues are same-repo only).

## Step 0 — Pick the sub-issue (you do this inline; too thin to delegate)
1. `gh api repos/<owner>/<repo>/issues/{prd}/sub_issues` → the children.
2. Keep the ones still **open**. For each, read its **## Blocked by**; a sub-issue is **workable** only if
   every blocker is **closed/merged**.
3. Pick the **lowest build-order** workable one → `{n}`. If none is workable, STOP and report why.
4. `gh issue view {n} --json title,body` → read its **Acceptance Criteria** and **## Design (scope)**.
   Thread this body as context into Step 1.

## Pipeline — delegate each stage through the engine
| # | Stage | Sub-agent type | Skill to inject | Reads | Writes |
|---|---|---|---|---|---|
| 1 | Explore | **Explore** | `dev-code-explorer` | sub-issue body | `slice/{prd}/issue-{n}/exploration` |
| 2 | Plan | general-purpose | `dev-plan` | …/exploration + sub-issue scope | `…/class-{C}/spec` (per class), `…/plan`, `slice/{prd}/testing-capabilities` |
| 3 | Implement (FAN-OUT) | general-purpose | `tdd-implement` (class mode) | `…/class-{C}/spec` | `…/class-{C}/impl` |
| 4 | Integrate | general-purpose | `tdd-implement` (integration mode) | all `…/class-*/impl` | `…/integration` |
| 5 | Verify | general-purpose | `dev-verifier` | …/plan + scope + integration | `…/verify` `{pass\|fail+what}` |
| 6 | PR | general-purpose | `dev-pr` | …/integration | `…/pr` |
| 7 | Accept | general-purpose | `dev-acceptance` | sub-issue criteria + …/verify | `…/acceptance` |

(Stage 1 is the only read-only stage → `subagent_type: Explore`. The rest edit code, run the suite, or
touch git → `general-purpose`.)

## Fan-out rule (Step 3)
Read `…/plan`'s class graph. For each **parallel set**, spawn **one `tdd-implement` (class mode) sub-agent
per class, in a single message** (concurrent). Honor `blocked-by`: a class depending on a not-yet-built
class waits for that class's sub-agent to return. Once every class is green, run **one** `tdd-implement`
(integration mode) sub-agent (Step 4).

## The verify loop (Step 5 — bounded to 2 retries)
If `…/verify` is **fail**: spawn a `tdd-implement` **retry mode** sub-agent and pass it the `…/verify`
key — it fixes exactly what failed, keeps the suite green, and re-persists its `impl`/`integration`
artifact. Then re-run `dev-verifier`. **Max 2 retries.** Still failing → STOP, escalate to the human with
the verdict; do **not** proceed to PR.

## End order
Verify green → **dev-pr** (branch / commit / push / open PR, never merge) → **dev-acceptance** (tick the
sub-issue's Acceptance Criteria + Deliverables boxes). The human merging the PR = the real "done".

## Resume
Update `slice/{prd}/issue-{n}/state` after each step so you can resume mid-pipeline after a compaction.
