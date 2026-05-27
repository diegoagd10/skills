---
name: task-creator
description: Turn a GitHub-issue PRD into vertical, end-to-end-testable capability slices
  and create them as native GitHub sub-issues under the PRD. Derives the slices, a
  mechanical blocked-by graph, and per-slice acceptance criteria + deliverables from
  the PRD's Design and Module Dependencies sections. Use when the user wants to break
  a PRD into tasks, create slice issues, or mentions "task-creator".
---

Turn a PRD (**user stories + design + module dependencies**) into narrow, fully-complete
**capability slices** — one user-visible E2E flow each — and create them as native GitHub
**sub-issues** under the PRD.

Derive everything from the PRD — **hardcode nothing domain-specific**. This skill is
**creation-only**: it creates issues with every checkbox empty; the *implementing* agent
ticks them later. It is never a progress updater.

## Input
1. **PRD** — a GitHub issue **number** (assumes the current repo) or a **URL**. The
   source of user stories, deep module design, and module dependencies.
   Fetch: `gh issue view <number-or-url> --json number,title,body`.
2. Only the PRD is required — no separate Design file.

## STOP conditions — refuse early, never invent
- PRD has **no user stories** → STOP, tell the user to add them.
- PRD **Design section missing**, or lacks named modules / their methods → STOP, tell
  the user to run `to-prd` first.
- PRD **`## Module Dependencies` section missing** → STOP, tell the user to add it to
  the PRD (format: `ModuleA → ModuleB → ModuleC`).
- PRD URL resolves to a repo **other than the current working repo** → STOP. Native
  sub-issues are **same-repo only**.
- PRD **already has sub-issues** (`gh api repos/<owner>/<repo>/issues/<prd>/sub_issues`
  returns non-empty) → STOP and list them. **Never duplicate** — this is the re-run guard.

## Phase 1 — Derive the slices  (reason silently; show only the plan)
Each slice is a **narrow, fully-complete E2E flow**:

- **No stubs, no skeletons.** Every slice delivers real, working behavior the user can
  verify end-to-end.
- **One user-visible flow per slice.** Scope it to the minimum that lets a user observe
  a specific outcome (e.g. "Edit Config: option appears in menu, form prefills, save
  persists"). Do not bundle multiple independent flows into one slice.
- **Granularity target:** one slice ≈ one user story or a tight group of stories that
  share an obvious single verification step.

For each slice determine:
- **Capability** — one sentence + **how the user verifies it end-to-end**.
- **Acceptance criteria** — the PRD stories this slice **closes** (fully satisfies). A
  story belongs to the **first slice that fully satisfies it**. This keeps coverage honest.
- **Modules in scope** — from the PRD Design, each tagged `builds` (new) / `changes`
  (exists, must change).

**Coverage:** every story must land in **at least one** slice. Track `covered/total` and
list anything unmapped or explicitly out-of-scope.

## Phase 2 — Build order + blocked-by graph  (mechanical: module-ownership)
1. Order the slices so that a module is built before any slice that needs it.
2. The **first slice in order that touches a module owns/builds it**.
3. A later slice that needs a **not-yet-built** module is **`blocked-by` the owning slice**.
   Derive the edges from the PRD's `## Module Dependencies` section.
4. Slices that share **no** unbuilt module are **independent → can run in parallel**.

`blocked-by` only ever points **backward** (to a lower-ordered slice). The dependency
tree in the issue body and the `blocked-by` edges must agree.

## Phase 3 — Ratify gate  (STOP and wait)
Present the full plan and **create nothing** until the user signs off. Show:
- the **ordered** slice list: capability · stories it closes · modules (with status)
- the **`blocked-by`** edges and the **parallelizable sets**
- **story coverage** `N/total` + anything unmapped

The user may edit slices, names, grouping, or order. Proceed only on approval.

## Phase 4 — Create the sub-issues  (creation-only)
Target repo = **current working repo**. Create children **in build order**, so a
blocker's issue number exists before any slice references it.

For each slice:
1. Build the body from the template below — **all checkboxes empty**.
2. Create it: `gh issue create --repo <owner>/<repo> --title "<capability>" --body "<body>"`.
   Capture the new issue **number**.
3. Get its integer **database id**:
   `gh api repos/<owner>/<repo>/issues/<child#> --jq .id`.
   This is the integer `id`, **NOT** the `node_id` and **NOT** `gh issue view --json id`.
4. Link it as a native sub-issue of the PRD:
   `gh api --method POST repos/<owner>/<repo>/issues/<prd#>/sub_issues -F sub_issue_id=<dbid>`.

**Never edit the PRD body** — GitHub renders the sub-issue list on the parent natively.

### Issue body template
```markdown
## Capability
<one-line E2E capability + how the user verifies it>

## Acceptance Criteria
- [ ] Story <n>: <story text>
- [ ] Story <m>: <story text>

## Design (scope of this slice)
Canonical source: <link to the PRD issue>

- **<ClassOrModule>** (builds|changes) — `method(args) -> ret`, `method2(...) -> ...`
- **<ClassOrModule>** (changes) — `method(...) -> ...`

Dependency tree (this slice's scope):

    <Orchestrator/entry>
      ├─ <Module>        [built by: this slice]
      └─ <Module>        [owned by #<earlier-slice> → blocked-by]

## Blocked by
- #<issue> — needs <Module>, built there   (or: None — independent)

## Deliverables
- [ ] <Module/artifact 1>
- [ ] <Module/artifact 2>
- [ ] unit / integration tests
- [ ] E2E verification: <concrete steps the user runs>
```

## Scope boundary
Creation-only. Every **Acceptance Criteria** and **Deliverables** checkbox is created
**empty**; whoever implements the slice ticks them as work completes. This skill does not
mark, close, or refresh issues on later runs.
