---
name: task-creator
description: Turn a GitHub-issue PRD into small, independently-verifiable tasks and create
  them as native GitHub sub-issues under the PRD. Emits module tasks (build one deep
  module, verified by unit tests) then integration tasks (glue modules into user-visible
  behavior, verified by integration/E2E tests), with a mechanical blocked-by graph derived
  from the PRD's Design and Module Dependencies. Use when the user wants to break a PRD
  into tasks, create task issues, or mentions "task-creator".
---

Turn a PRD (**user stories + design + module dependencies**) into small, self-contained
**tasks** — each one completable and verifiable in a single bounded iteration by an
**agent or a human** — and create them as native GitHub **sub-issues** under the PRD.

There are **two kinds of task**:
- **Module task** — builds ONE deep module from the PRD Design. Not user-visible on its
  own; verified by its **unit tests**.
- **Integration task** — glues already-built modules into one **user-visible** behavior.
  Verified by **integration tests** *and* by running the real thing (a browser for a web
  UI; the **TUI executed in a sandbox** for a TUI).

Build order is **global two-phase**: every **module task** first (in dependency order),
then every **integration task**.

Derive everything from the PRD — **hardcode nothing domain-specific**. This skill is
**creation-only**: it creates issues with every checkbox empty; the *implementing* agent
ticks them later. It is never a progress updater.

**Why small.** A task that bundles many modules or many outcomes exhausts an implementing
agent's context window (and a human's attention) before the work is done. One module per
module task, and one observable outcome per integration task, keeps every iteration
bounded.

**No skeletons.** Every task delivers **complete, tested** behavior *at its own layer* — a
module task completes a module (unit-tested), an integration task completes a user-visible
flow (integration/E2E-tested). Never emit a half-wired stub that only "works" once a future
task lands.

**How a task is closed.** Every task — *regardless of type* — is closeable by whoever
implements it (agent or human) once **all of its `## Verification` checkboxes pass**. The
Verification section is the self-contained close gate; a downstream agent needs only the
issue body to decide it is done. A module task is done when its **unit tests** pass; an
integration task is done when its **integration test + real run** pass. (Closing the task
issue is distinct from closing a PRD *story*: only **integration tasks** close stories;
module tasks are enablers.)

## Input
1. **PRD** — a GitHub issue **number** (assumes the current repo) or a **URL**. The
   source of user stories, deep module design, and module dependencies.
   Fetch: `gh issue view <number-or-url> --json number,title,body`.
2. Only the PRD is required — no separate Design file.

## STOP conditions — refuse early, never invent
- PRD has **no user stories** → STOP, tell the user to add them.
- PRD **Design section missing**, or lacks named modules / their methods → STOP, tell
  the user to run `to-prd` then `deep-design` first.
- PRD **`## Module Dependencies` section missing** → STOP, tell the user to add it to
  the PRD (format: `ModuleA → ModuleB → ModuleC`).
- PRD URL resolves to a repo **other than the current working repo** → STOP. Native
  sub-issues are **same-repo only**.
- PRD **already has sub-issues** (`gh api repos/<owner>/<repo>/issues/<prd>/sub_issues`
  returns non-empty) → STOP and list them. **Never duplicate** — this is the re-run guard.

## Phase 1 — Derive the module tasks  (mechanical: from Design + Module Dependencies)
These fall almost straight out of the PRD — `deep-design` already chose each module's
interface and wrote the dependency graph. Emit **one module task per deep module** in the
Design. For each, capture:
- **Module + responsibility** — the module name and its one-line job.
- **Contract** — the **exposed** methods (signatures) and the **hidden** implementation
  details, copied from the Design. Do NOT redesign — if the Design is ambiguous, STOP.
- **Depends on** — the modules this one **calls**, read from `## Module Dependencies`.
  These become its `blocked-by` edges.
- **Verification** — its **unit tests** cover the exposed contract (happy path + edges).

A module task **does not close a story** — it is an enabler. Stories are closed in Phase 2.

## Phase 2 — Derive the integration tasks  (from the user stories)
Emit **one integration task per observable outcome**:
- **One user action → one observable result** — i.e. a single `Then`. Scope it to the
  minimum that lets a user observe a specific outcome.
- **`And`-clause rule:** an `And` stays in the same task if the *same single action*
  reveals it; it **splits** into its own task if observing it needs a *different action or
  precondition* (e.g. "...And it survives a restart" → separate task).
- **Never bundle two stories** into one task.

For each integration task determine:
- **Capability** — one sentence + **how the user verifies it end-to-end** (concrete steps;
  for a TUI, run it in a **sandbox**; for a web UI, drive a **browser**).
- **Acceptance criterion** — the specific story **outcome** this task closes.
- **Glues** — which already-built modules it **wires together** (it wires, it does not
  build them).
- **Backward edge allowed** — if gluing reveals a module's interface was **wrong**, this
  task may change that module. Record the change in the issue rather than pretending the
  module task was final. (This is the escape hatch for the global two-phase order — wrong
  interfaces surface late, so integration tasks must be allowed to fix them.)

## Phase 3 — Build order + blocked-by graph  (mechanical)
1. **All module tasks first**, ordered **topologically** from `## Module Dependencies`: a
   module is built before any module that depends on it.
2. **Then all integration tasks.**
3. A **module task** is `blocked-by` the module tasks for the modules it **calls**.
4. An **integration task** is `blocked-by` every module task whose module it **glues**.
5. `blocked-by` points **backward only** (to a lower-ordered task). The dependency tree in
   each issue body and the `blocked-by` edges must agree.
6. Tasks that share **no** unbuilt dependency are **independent → can run in parallel**.

**Coverage — TWO checks, both must be honest:**
- **Module coverage:** every module named in the Design has **exactly one** module task.
  Track `modules covered/total`.
- **Story coverage:** every story **outcome** is closed by **exactly one** integration
  task; a story is fully closed only when **all** its outcome-tasks are done. Track
  `outcomes covered/total`.

List anything unmapped or explicitly out-of-scope.

## Phase 4 — Ratify gate  (STOP and wait)
Present the full plan and **create nothing** until the user signs off. Show:
- the **ordered module tasks**: module · contract summary · dependency edges · parallel sets
- the **ordered integration tasks**: capability · story outcome it closes · modules glued ·
  `blocked-by`
- **both coverage numbers** + anything unmapped

The user may edit tasks, names, grouping, or order. Proceed only on approval.

## Phase 5 — Create the sub-issues  (creation-only)
Target repo = **current working repo**. Create children **in build order** (all module
tasks, then all integration tasks), so a blocker's issue number exists before any task
references it.

For each task:
1. Build the body from the matching template below — **all checkboxes empty**.
2. Create it: `gh issue create --repo <owner>/<repo> --title "<title>" --body "<body>"`.
   Capture the new issue **number**.
3. Get its integer **database id**:
   `gh api repos/<owner>/<repo>/issues/<child#> --jq .id`.
   This is the integer `id`, **NOT** the `node_id` and **NOT** `gh issue view --json id`.
4. Link it as a native sub-issue of the PRD:
   `gh api --method POST repos/<owner>/<repo>/issues/<prd#>/sub_issues -F sub_issue_id=<dbid>`.

**Never edit the PRD body** — GitHub renders the sub-issue list on the parent natively.

### Module task body template
```markdown
## Module
Build `<ModuleName>` — <one-line responsibility from the Design>.

## Contract (from PRD Design)
Canonical source: <link to the PRD issue>

- **Exposed:** `method(args) -> ret`, `method2(...) -> ...`
- **Hidden:** <implementation details kept inside the module>

## Depends on (modules it calls)
- #<module-task> — `<ModuleX>`, built there   (or: None — leaf module)

## Verification
- [ ] Unit tests cover the exposed contract (happy path + edge cases)
- [ ] All unit tests pass

## Deliverables
- [ ] `<ModuleName>` implementing the contract above
- [ ] unit tests
```

### Integration task body template
```markdown
## Capability
<one user action → one observable result>.
Verify: <concrete steps the user runs — TUI executed in a sandbox / browser for web UI>.

## Acceptance Criteria
- [ ] Story <n> — When <action>, Then <the single observable outcome>

## Glues (modules wired here — built earlier, not built here)
Canonical source: <link to the PRD issue>

- `<ModuleA>` (#<module-task>), `<ModuleB>` (#<module-task>)

Dependency tree (this task's scope):

    <Orchestrator/entry>
      ├─ <ModuleA>   [built by #<module-task> → blocked-by]
      └─ <ModuleB>   [built by #<module-task> → blocked-by]

## Blocked by
- #<module-task>, #<module-task> — modules built there

## Verification
- [ ] Integration test exercises the glued flow end-to-end
- [ ] Real run shows the outcome: <TUI in sandbox / browser / CLI execution>

## Deliverables
- [ ] wiring of the modules above into the user-visible flow
- [ ] integration tests
- [ ] E2E verification: <concrete steps the user runs>

## Interface fixes (backward edges) — if any
- If gluing revealed a module's interface was wrong, list the module + the change made.
```

## Scope boundary
Creation-only. Every **Acceptance Criteria**, **Verification**, and **Deliverables**
checkbox is created **empty**. Any agent or human may close the sub-issue once all of its
**Verification** checkboxes pass — the body is self-contained, so no conversation context
is needed. This skill does not mark, close, or refresh issues on later runs.
